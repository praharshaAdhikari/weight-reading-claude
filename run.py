#!/usr/bin/env python3
"""Ask Claude the Experiment 5 question: one fresh `claude -p` session per run, tools off, one reply.

  run.py --models haiku,sonnet,opus,fable --target 10 [--game breakout] [--effort xhigh] [--parallel 4]

Fills each model up to --target counted runs (ok, refused or cut off; infrastructure failures don't count
and are retried), so it can be stopped and started again at any time. Each run goes to
runs/<game>/<model>[-<effort>]/<nn>/:
  events.jsonl   raw stream from claude          answer.md       the reply (requested model's text only)
  thinking.md    thinking summaries              run.json        outcome, tokens, time, cost, usage %
  net.npz        network read from the reply     score.json      its MinAtar score (score.py)
Progress, one line per event: logs/runs.log (tail -f it).

Usage guard (subscription): pauses when the 5-hour window passes --five-hour-cap until it resets; when the
weekly window passes the cap, waits for the weekly reset if it comes before --resume-before, else stops.
"""
import argparse, hashlib, json, os, queue, re, subprocess, threading, time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROMPTS = HERE / "lm_understand-logs" / "exp5_write_from_scratch" / "runs"
MODELS = {"haiku": "claude-haiku-5-5", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5",
          "fable": "claude-fable-5-2"}
SYSTEM = "Answer the user's request."  # the paper's instructions.md
EMPTY_CWD = Path(os.environ.get("RUN_CWD", "/tmp/claude-empty-cwd/"
                                "empty"))
LOG = HERE / "logs" / "runs.log"
COUNTED = ("ok", "refused", "cut_off", "interrupted")
# One reply, as in the paper: no refusal retries or fallback model. (Claude Code also continues a capped reply
# in a new turn by itself, with no switch to turn that off, so run_one stops the process when that turn starts.)
ENV = {"CLAUDE_CODE_MAX_OUTPUT_TOKENS": "128000", "CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK": "1",
       "CLAUDE_CODE_DISABLE_REFUSAL_RETRY": "1"}

lock, score_lock = threading.Lock(), threading.Lock()
usage = {}  # latest rate-limit windows seen: {"five_hour": {...}, "seven_day": {...}}


def log(msg):
    line = f"{datetime.now():%H:%M:%S} {msg}"
    with lock:
        print(line, flush=True)
        with open(LOG, "a") as f:
            f.write(line + "\n")


def event_type(line):
    try:
        return json.loads(line).get("type")
    except ValueError:
        return None


def read_events(path, model_id):
    rec = {"answered_by": [], "flags": [], "tools": None, "rate_limit": None, "result": None, "injected": None}
    texts, other, thinks = [], [], []
    for line in open(path, errors="replace"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        t, st = e.get("type"), e.get("subtype")
        if t == "user":  # Claude Code's own follow-up turn (output cap, safety stop): the one reply ended here
            c = (e.get("message") or {}).get("content")
            rec["injected"] = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c or [])
            break
        if t == "system" and st == "init":
            rec["tools"], rec["init_model"] = e.get("tools"), e.get("model")
        elif t == "system" and st != "thinking_tokens":
            rec["flags"].append(st)  # e.g. model_refusal_fallback, api_retry
        elif t == "assistant":
            m = e.get("message") or {}
            who = m.get("model")
            if e.get("error"):
                rec["flags"].append(f"error:{e['error']}")
            if who == "<synthetic>":  # Claude Code's own error text (usage limit, lost connection), not a model
                continue
            if who and who not in rec["answered_by"]:
                rec["answered_by"].append(who)
            for c in m.get("content") or []:
                if c.get("type") == "text":
                    (texts if who == model_id else other).append(c.get("text", ""))
                elif c.get("type") == "thinking" and c.get("thinking"):
                    thinks.append(c["thinking"])
                elif c.get("type") == "tool_use":
                    rec["flags"].append("tool_use")
        elif t == "rate_limit_event":
            rec["rate_limit"] = e.get("rate_limit_info")
        elif t == "result":
            rec["result"] = {k: e.get(k) for k in (
                "subtype", "is_error", "stop_reason", "terminal_reason", "duration_ms", "num_turns",
                "total_cost_usd", "usage", "modelUsage", "safety_stops", "api_error_status")}
    return rec, "\n\n".join(texts), "\n\n".join(other), "\n\n---\n\n".join(thinks)


def outcome(rec, model_id):
    r, flags, inj = rec["result"] or {}, " ".join(rec["flags"]), rec["injected"] or ""
    if not inj and any(f.startswith("error:") and "max_output_tokens" not in f for f in rec["flags"]):
        return "infra"  # usage limit, server or connection error: no complete reply, retried
    if ("refusal" in flags or (r.get("safety_stops") or 0) > 0 or r.get("stop_reason") == "refusal"
            or "safety" in inj or any(m != model_id for m in rec["answered_by"])):
        return "refused"
    if "max_output_tokens" in flags or r.get("stop_reason") == "max_tokens" or "token limit" in inj:
        return "cut_off"
    if inj:
        return "interrupted"  # another follow-up from Claude Code; the reply before it is scored
    if not r or r.get("is_error") or r.get("stop_reason") != "end_turn":
        return "infra"  # no complete reply: usage limit, network, overload... retried, not counted
    return "ok"


def existing(run_dir):
    """Outcomes of the runs already saved for one model."""
    out = {}
    for d in sorted(run_dir.glob("[0-9][0-9]")):
        f = d / "run.json"
        out[d.name] = json.loads(f.read_text())["outcome"] if f.exists() else "incomplete"
    return out


def guard(a):
    """Block while a usage window is nearly used up; return False if the batch must stop."""
    while True:
        five, week, now = usage.get("five_hour"), usage.get("seven_day"), time.time()
        if five and five["utilization"] >= a.five_hour_cap and five["resetsAt"] > now:
            log(f"pause: 5-hour window at {five['utilization']:.0%}, waiting until "
                f"{datetime.fromtimestamp(five['resetsAt']):%H:%M}")
            time.sleep(five["resetsAt"] - now + 120)
            usage.pop("five_hour", None)
            continue
        if week and week["resetsAt"] <= now:  # reading from before the reset
            usage.pop("seven_day", None)
            continue
        if week:
            ends_soon = week["resetsAt"] <= a.resume_before  # tonight's week: its leftover expires anyway
            cap = a.weekly_cap_now if ends_soon else a.weekly_cap
            if week["utilization"] >= cap:
                if ends_soon and week["resetsAt"] > now:
                    log(f"pause: weekly use at {week['utilization']:.0%}, waiting for the reset at "
                        f"{datetime.fromtimestamp(week['resetsAt']):%a %H:%M}")
                    time.sleep(week["resetsAt"] - now + 120)
                    usage.pop("seven_day", None)
                    continue
                log(f"stop: weekly use at {week['utilization']:.0%} (cap {cap:.0%})")
                return False
        return True


def run_one(a, label, model):
    model_id = MODELS[model]
    run_dir = HERE / "runs" / a.game / label
    with lock:
        run_dir.mkdir(parents=True, exist_ok=True)
        nn = f"{max((int(p.name) for p in run_dir.glob('[0-9][0-9]')), default=-1) + 1:02d}"
        d = run_dir / nn
        d.mkdir()
    log(f"start  {label}/{nn}")
    cmd = ["claude", "-p", "--model", model_id, "--effort", a.effort, "--thinking-display", "summarized",
           "--no-session-persistence", "--tools", "", "--system-prompt", SYSTEM, "--setting-sources", "",
           "--strict-mcp-config", "--disable-slash-commands", "--output-format", "stream-json", "--verbose"]
    t0, timed_out = time.time(), threading.Event()
    with open(a.prompt) as fin, open(d / "events.jsonl", "w") as fout, open(d / "stderr.log", "w") as ferr:
        p = subprocess.Popen(cmd, stdin=fin, stdout=subprocess.PIPE, stderr=ferr, cwd=EMPTY_CWD, text=True,
                             env={**os.environ, **ENV})
        timer = threading.Timer(a.timeout, lambda: (timed_out.set(), p.kill()))
        timer.start()
        for line in p.stdout:
            fout.write(line)
            if '"user"' in line and event_type(line) == "user":
                p.kill()  # Claude Code is starting a second turn of its own; the run is one reply
        p.wait()
        timer.cancel()
    code = "timeout" if timed_out.is_set() else p.returncode
    rec, answer, other, thinking = read_events(d / "events.jsonl", model_id)
    rec.update(model=model_id, effort=a.effort, game=a.game, prompt_sha256=a.prompt_sha, cmd=cmd,
               exit_code=code, wall_s=round(time.time() - t0), started=datetime.fromtimestamp(t0).isoformat(),
               claude_version=a.claude_version)
    rec["outcome"] = "infra" if code == "timeout" else outcome(rec, model_id)
    (d / "answer.md").write_text(answer)
    (d / "thinking.md").write_text(thinking)
    if other:
        (d / "other_model_answer.md").write_text(other)
    (d / "run.json").write_text(json.dumps(rec, indent=1) + "\n")
    rl = rec["rate_limit"] or {}
    with lock:
        usage.update(rl.get("unifiedWindows") or {})
    r = rec["result"] or {}
    u = r.get("usage") or {}
    pct = " ".join(f"{k.replace('_hour', 'h').replace('seven_day', 'week')} {v['utilization']:.0%}"
                   for k, v in (rl.get("unifiedWindows") or {}).items())
    spent = (f"out {u.get('output_tokens', 0):,} (thinking {(u.get('output_tokens_details') or {}).get('thinking_tokens', 0):,})"
             f"  ${r.get('total_cost_usd') or 0:.2f}" if r else
             f"stopped at Claude Code's follow-up: {rec['injected'][:60]!r}" if rec["injected"] else "no result")
    log(f"done   {label}/{nn}  {rec['outcome']}  {rec['wall_s'] / 60:.1f} min  {spent}  {pct}  {' '.join(rec['flags'])}")
    if rec["outcome"] == "infra":
        return False
    score_run(a, label, d)
    return True


def score_run(a, label, d):
    nn = d.name
    with score_lock:  # one scoring job at a time; it uses --workers processes
        s = subprocess.run([str(HERE / ".venv" / "bin" / "python"), str(HERE / "score.py"), str(d / "answer.md"),
                            "--game", a.game, "--save", str(d / "net.npz"), "--out", str(d / "score.json"),
                            "--workers", str(a.workers)], capture_output=True, text=True)
    if s.returncode:
        log(f"score  {label}/{nn}  FAILED: {s.stderr.strip()[-300:]}")
    else:
        sc = json.loads((d / "score.json").read_text())
        rd = sc["reading"]
        log(f"score  {label}/{nn}  {sc['mean']} ± {sc['se']}  (edits block: {rd['block']}, "
            f"statements read {rd['applied']}/{rd['statements']}{', cut off' if rd['cut_off'] else ''})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", required=True, help="comma list of: " + ", ".join(MODELS))
    ap.add_argument("--target", type=int, required=True, help="counted runs wanted per model")
    ap.add_argument("--game", default="breakout")
    ap.add_argument("--effort", default="xhigh")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--workers", type=int, default=4, help="processes for scoring")
    ap.add_argument("--timeout", type=int, default=3 * 3600, help="seconds per run")
    ap.add_argument("--five-hour-cap", type=float, default=0.95)
    ap.add_argument("--weekly-cap-now", type=float, default=0.97, help="cap before the current week resets")
    ap.add_argument("--weekly-cap", type=float, default=0.50, help="cap after the weekly reset")
    ap.add_argument("--resume-before", default="2026-11-23T06:00",
                    help="wait for a weekly reset only if it comes before this time")
    a = ap.parse_args()
    a.prompt = PROMPTS / a.game / "reply" / "prompt.txt"
    a.prompt_sha = hashlib.sha256(a.prompt.read_bytes()).hexdigest()
    a.resume_before = datetime.fromisoformat(a.resume_before).timestamp()
    a.claude_version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    EMPTY_CWD.mkdir(parents=True, exist_ok=True)
    assert not any(EMPTY_CWD.iterdir()), f"{EMPTY_CWD} must be empty"
    LOG.parent.mkdir(exist_ok=True)

    jobs = queue.Queue()
    for k in range(a.target):  # round robin, so a stopped batch is balanced across models
        for model in a.models.split(","):
            label = model if a.effort == "xhigh" else f"{model}-{a.effort}"
            done = sum(o in COUNTED for o in existing(HERE / "runs" / a.game / label).values())
            if k >= done:
                jobs.put((label, model, 0))
    for model in a.models.split(","):  # counted runs a stopped batch left without a score
        label = model if a.effort == "xhigh" else f"{model}-{a.effort}"
        for nn, o in existing(HERE / "runs" / a.game / label).items():
            d = HERE / "runs" / a.game / label / nn
            if o in COUNTED and not (d / "score.json").exists():
                score_run(a, label, d)
    total = jobs.qsize()
    log(f"batch: {total} runs to do ({a.models}, target {a.target}, effort {a.effort}, {a.claude_version}, "
        f"prompt sha256 {a.prompt_sha[:12]})")
    stopped = threading.Event()
    finished = []

    def worker():
        while not stopped.is_set():
            try:
                label, model, tries = jobs.get_nowait()
            except queue.Empty:
                return
            if not guard(a):
                stopped.set()
                return
            try:
                ok = run_one(a, label, model)
            except Exception as e:  # never lose a job silently
                log(f"error  {label}: {type(e).__name__}: {e}")
                ok = False
            if ok:
                finished.append(label)
            elif tries < 2:
                time.sleep(300)
                jobs.put((label, model, tries + 1))
            else:
                log(f"giving up on one {label} run after 3 infrastructure failures")

    threads = [threading.Thread(target=worker) for _ in range(min(a.parallel, max(total, 1)))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    log(f"batch {'stopped' if stopped.is_set() else 'finished'}: {len(finished)}/{total} scored")


if __name__ == "__main__":
    main()
