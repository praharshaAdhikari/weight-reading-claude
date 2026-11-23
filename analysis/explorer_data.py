"""Rows for the personal run explorer: one per counted run, with what it cost, how it ended and what it said."""
import json, re
from pathlib import Path

R = Path(__file__).resolve().parent.parent
OUT = R / "results" / "explorer"
ARMS = {"haiku-xhigh": ("Haiku 5.5", "xhigh"), "sonnet-xhigh": ("Sonnet 5.5", "xhigh"), "opus-xhigh": ("Opus 5.5", "xhigh"),
        "fable-xhigh": ("Fable 5.2", "xhigh"), "haiku-high": ("Haiku 5.5", "high"), "sonnet-high": ("Sonnet 5.5", "high"),
        "opus-high": ("Opus 5.5", "high"), "fable-high": ("Fable 5.2", "high"),
        "opus-max": ("Opus 5.5", "max"), "sonnet-max": ("Sonnet 5.5", "max")}


def excerpt(text, n, tail=False):
    text = re.sub(r"/home/\S+", "[path]", text)  # keep local paths out of the page
    text = re.sub(r"[#*`]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= n:
        return text
    return "…" + text[-n:] if tail else text[:n] + "…"


rows = []
for arm, (model, effort) in ARMS.items():
    for d in sorted((R / "runs" / "breakout" / arm).glob("[0-9][0-9]")):
        if not (d / "score.json").exists():
            continue
        run, sc = json.loads((d / "run.json").read_text()), json.loads((d / "score.json").read_text())
        if run["outcome"] == "infra":
            continue
        rd = sc["reading"]
        usage = (run.get("result") or {}).get("usage") or {}
        out = usage.get("output_tokens")
        think = (usage.get("output_tokens_details") or {}).get("thinking_tokens")
        ended = "finished" if rd["nonzero"]["W3"] else "cut off while writing" if rd["block"] else "cut off while thinking"
        windows = (run.get("rate_limit") or {}).get("unifiedWindows") or {}
        ans = (d / "answer.md").read_text() if (d / "answer.md").exists() else ""
        thk = (d / "thinking.md").read_text() if (d / "thinking.md").exists() else ""
        prose = ans.split("<edits>")[0] if "<edits>" in ans else ans
        rows.append({
            "id": f"{arm}/{d.name}", "arm": arm, "model": model, "effort": effort, "run": int(d.name),
            "outcome": run["outcome"], "ended": ended,
            "score": sc["mean"], "se": sc["se"], "best_game": sc["max"], "game_steps": sc["mean_length"],
            "games_at_step_cap": sc["hit_step_cap"],
            "output_tokens": out, "thinking_tokens": think,
            "answer_tokens": (out - think) if out is not None and think is not None else None,
            "minutes": round(run["wall_s"] / 60, 1), "cost_usd": round(run["result"]["total_cost_usd"], 2) if run.get("result") else None,
            "statements_read": rd["applied"], "statements_found": rd["statements"], "nonzero_weights": rd["nonzero_total"],
            "started": run["started"][:16].replace("T", " "),
            "five_hour_pct": round(100 * windows.get("five_hour", {}).get("utilization", 0)),
            "weekly_pct": round(100 * windows.get("seven_day", {}).get("utilization", 0)),
            "said": excerpt(prose, 420) if rd["block"] else "",
            "last_thought": excerpt(thk, 360, tail=True) if not rd["nonzero"]["W3"] else "",
        })

catch = []
txt = R / "results" / "catch_rate.txt"
for line in (txt.read_text().splitlines() if txt.exists() else []):
    m = re.match(r"(\S+)\s+score (\S*)\s+catches\s+(\d+) misses\s+(\d+)", line)
    if m:
        name, s, c, mi = m.groups()
        s = s or {"rule": "8.37", "astra": "502.88"}.get(name)  # baselines: scores from references.json
        catch.append({"network": name, "score": float(s) if s else None, "catches": int(c), "misses": int(mi),
                      "balls_per_miss": round((int(c) + int(mi)) / int(mi)) if int(mi) else None})

assert rows and all(r["score"] >= 0 for r in rows)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "runs.json").write_text(json.dumps(rows, indent=0))
(OUT / "catch_rate.json").write_text(json.dumps(catch, indent=0))
print(len(rows), "runs,", len(catch), "catch-rate rows ->", OUT)
