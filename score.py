#!/usr/bin/env python3
"""Experiment 5: read a reply into the 600-32-32-6 network and score it on MinAtar.

Follows the prompt in lm_understand-logs/exp5_write_from_scratch: only the last ```edits block is read,
statements apply in order, a statement that cannot be read is skipped. Score: mean over 1,000 episodes of
MinAtar 1.0.15, sticky actions 0.1, actions sampled from softmax(logits), episodes cut at 10,000 steps.

  score.py SOURCE [--game breakout] [--episodes 1000] [--save net.npz] [--out score.json]
      SOURCE: a reply (.md/.txt), a network (.npz), 'zero' (every weight 0 = uniform random play)
              or 'rule' (Breakout only: move the paddle toward the ball's column)
  score.py --selftest     reading Astra's three replies must give its released networks exactly
"""
import argparse, ast, json, os, re, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

EXP5 = Path(__file__).resolve().parent / "lm_understand-logs" / "exp5_write_from_scratch"
SHAPES = {"W1": (600, 32), "b1": (32,), "W2": (32, 32), "b2": (32,), "W3": (32, 6), "b3": (6,)}
NPZ = {"W1": "actor/dense1/kernel", "b1": "actor/dense1/bias", "W2": "actor/dense2/kernel",
       "b2": "actor/dense2/bias", "W3": "actor/logits/kernel", "b3": "actor/logits/bias"}
OPS = {ast.Add: np.add, ast.Sub: np.subtract, ast.Mult: np.multiply}
MAX_STEPS = 10_000
DECIMAL = r"(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?"


# ---------- reading a reply ----------

def last_edits_block(text):
    """The last ```edits block. A reply that ends inside it gives what was written (cut_off=True)."""
    starts = [m.end() for m in re.finditer(r"^[ \t]*```edits\b[^\n]*\n", text, re.M)]
    if not starts:
        return None, False
    body = text[starts[-1]:]
    end = re.search(r"^[ \t]*```", body, re.M)
    if end is None:  # cut off: drop the last line, which may stop mid-number
        return body[:body.rfind("\n") + 1], True
    return body[:end.start()], False


def split_statements(block):
    """One statement per line; a list may continue over the next lines. A line that starts with a
    tensor name always starts a new statement, so one unbalanced bracket can't swallow the rest."""
    out, buf, depth = [], [], 0
    for line in block.splitlines():
        code = line.split("#", 1)[0].strip()
        if not code:
            continue
        if buf and re.match(r"(W[123]|b[123])\s*\[", code):
            out.append(" ".join(buf))
            buf, depth = [], 0
        buf.append(code)
        depth += code.count("[") - code.count("]")
        if depth <= 0 and not code.endswith("="):  # a list may also start on the line after '='
            out.append(" ".join(buf))
            buf, depth = [], 0
    if buf:
        out.append(" ".join(buf))
    return out


def numbers(v):
    """True for a real number or a (nested) list of them: the only values the prompt allows."""
    return all(numbers(x) for x in v) if isinstance(v, list) else type(v) in (int, float)


def as_index(node):
    v = ast.literal_eval(node)
    if type(v) is not int:
        raise ValueError("index is not an integer")
    return v


def apply_statement(net, stmt):
    body = ast.parse(stmt).body
    if len(body) != 1:
        raise ValueError("not one statement")
    s = body[0]
    if isinstance(s, ast.Assign) and len(s.targets) == 1:
        target, op = s.targets[0], None
    elif isinstance(s, ast.AugAssign) and type(s.op) in OPS:
        target, op = s.target, OPS[type(s.op)]
    else:
        raise ValueError("not =, +=, -= or *=")
    if not (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)
            and target.value.id in SHAPES):
        raise ValueError("target is not W1/b1/W2/b2/W3/b3[...]")
    name = target.value.id
    parts = target.slice.elts if isinstance(target.slice, ast.Tuple) else [target.slice]
    if len(parts) != len(SHAPES[name]):
        raise ValueError(f"{name} takes {len(SHAPES[name])} indices")
    idx = tuple(slice(*(None if x is None else as_index(x) for x in (p.lower, p.upper, p.step)))
                if isinstance(p, ast.Slice) else as_index(p) for p in parts)
    src = ast.get_source_segment(stmt, s.value) or ""
    if not all(re.fullmatch(DECIMAL, t) for t in re.findall(r"(?:\d|\.\d)[0-9A-Za-z_.]*(?:(?<=[eE])[-+]\d+)?", src)):
        raise ValueError("not a plain decimal number")  # e.g. 0x10, 1_000
    v = ast.literal_eval(s.value)
    if not numbers(v):
        raise ValueError("value is not a number or a list of numbers")
    v = np.asarray(v, dtype=np.float64)  # a ragged list raises here
    if not np.all(np.abs(v) <= 1e6):
        raise ValueError("|value| > 1e6")
    block = net[name][idx]
    shape = np.shape(block)
    if v.ndim and v.shape != shape:
        if v.ndim == 1 and v.size == np.size(block):
            v = v.reshape(shape)  # a flat list with as many values as entries
        else:
            raise ValueError(f"{v.shape} values for a block of shape {shape}")
    new = v if op is None else op(block, v)
    if not np.all(np.abs(new) <= 1e6):
        raise ValueError("result |value| > 1e6")  # repeated *= could reach inf and NaN logits
    net[name][idx] = new


def read_reply(text):
    net = {k: np.zeros(s) for k, s in SHAPES.items()}
    block, cut_off = last_edits_block(text)
    rep = {"block": block is not None, "cut_off": cut_off, "statements": 0, "applied": 0, "errors": []}
    for stmt in split_statements(block or ""):
        rep["statements"] += 1
        try:
            apply_statement(net, stmt)
            rep["applied"] += 1
        except Exception as e:  # the prompt's rule: a statement that cannot be read is skipped
            rep["errors"].append({"statement": stmt[:300], "error": f"{type(e).__name__}: {e}"})
    net = {k: v.astype(np.float32) for k, v in net.items()}
    rep["nonzero"] = {k: int(np.count_nonzero(v)) for k, v in net.items()}
    rep["nonzero_total"] = sum(rep["nonzero"].values())
    rep["max_abs"] = {k: float(np.abs(v).max()) for k, v in net.items()}
    return net, rep


def load_net(path):
    d = np.load(path)
    return {k: d[NPZ[k]] for k in SHAPES}


def save_net(net, path):
    np.savez(path, **{NPZ[k]: v for k, v in net.items()})


# ---------- playing ----------

def channel_map(game, names):
    """(game channels) x 6 matrix of 0/1, from the prompt's 'How the 6 channels are built' line."""
    text = (EXP5 / "runs" / game / "reply" / "prompt.txt").read_text()
    line = re.search(r"How the 6 channels are built[^:]*:(.*?)A cell is 1", text, re.S).group(1)
    M = np.zeros((len(names), 6))
    for ch, srcs in re.findall(r"channel (\d) \(\w+\) <- ([\w, ]+)", line):
        for s in (x.strip() for x in srcs.split(",")):
            if s != "nothing":
                M[names[s], int(ch)] = 1
    return M


def network_policy(net):
    W1, b1, W2, b2, W3, b3 = (net[k].astype(np.float64) for k in SHAPES)

    def policy(x, rng):
        z = np.tanh(np.tanh(x @ W1 + b1) @ W2 + b2) @ W3 + b3
        return int(np.argmax(z - np.log(-np.log(rng.random(6)))))  # Gumbel-max: a sample from softmax(z)
    return policy


def rule_policy(x, rng):
    g = x.reshape(10, 10, 6)
    paddle, ball = np.flatnonzero(g[9, :, 0]), np.argwhere(g[:, :, 3])
    if len(paddle) == 0 or len(ball) == 0:
        return 0
    bx, px = ball[0][1], paddle[0]
    return 1 if bx < px else 3 if bx > px else 0  # 1 left, 3 right, 0 no-op


def play(game, source, seeds):
    from minatar import Environment
    policy = rule_policy if isinstance(source, str) else network_policy(source)
    M = None
    out = []
    for seed in seeds:  # one fresh game per episode, seeded by its number
        env = Environment(game, sticky_action_prob=0.1, difficulty_ramping=True)
        env.seed(seed)  # MinAtar 1.0.15: one RandomState for the game and the sticky actions
        M = channel_map(game, env.env.channels) if M is None else M
        rng = np.random.default_rng(seed)
        env.reset()
        total, steps, done = 0.0, 0, False
        while not done and steps < MAX_STEPS:
            x = ((env.state().reshape(100, -1) @ M) > 0).reshape(600).astype(np.float64)
            r, done = env.act(policy(x, rng))
            total += r
            steps += 1
        out.append((total, steps))
    return out


def score(game, source, episodes=1000, workers=None):
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    chunks = [c.tolist() for c in np.array_split(np.arange(episodes), workers * 4) if len(c)]
    res = []
    with ProcessPoolExecutor(workers) as ex:
        for i, f in enumerate(as_completed([ex.submit(play, game, source, c) for c in chunks]), 1):
            res += f.result()
            print(f"\r  {game}: {len(res)}/{episodes} episodes", end="", file=sys.stderr, flush=True)
    print(file=sys.stderr)
    s, n = np.array([r[0] for r in res]), np.array([r[1] for r in res])
    return {"mean": round(float(s.mean()), 2), "se": round(float(s.std(ddof=1) / np.sqrt(len(s))), 2),
            "episodes": len(s), "mean_length": round(float(n.mean()), 1),
            "hit_step_cap": int((n >= MAX_STEPS).sum()), "min": float(s.min()), "max": float(s.max())}


# ---------- checks and CLI ----------

def selftest():
    example = ("Some text.\n```edits\nW1[0, 0] = 9\n```\nThe final block:\n```edits\n"
               "W1[12, 0] = 2.5    # a comment\nW1[0:6, 3] = [1, 0, -1, 0, 2, 0]\nb1[0:4] = -1\n"
               "W1[3:600:60, 0] = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1]\nW2[0:2, 0:3] = [[1, -1, 0.5],\n  [0, 2, 0]]\n"
               "W3[:, 2] = 1\nW3[:, 2] *= 2\nW3[0, 0 = 1\nb3[0] = 7\nb2[0] = 2e7\n```\n")
    net, rep = read_reply(example)
    assert (rep["statements"], rep["applied"]) == (10, 8), rep
    assert net["W1"][0, 0] == 0 and net["W1"][12, 0] == 2.5 and net["W1"][4, 3] == 2 and net["b1"][3] == -1
    assert net["W1"][483, 0] == net["W1"][543, 0] == 1 and net["W1"][423, 0] == 0
    assert net["W2"][1, 1] == 2 and net["W3"][5, 2] == 2 and net["b3"][0] == 7 and net["b2"][0] == 0
    net, rep = read_reply("```edits\nb1[0:3] =\n  [1, 2, 3]\nb1[3] = 0x10\nb1[4] = 1_000\nb1[5] = 1e-3\n"
                          "b2[0] = 1e6\nb2[0] *= 10\nb2[1] = -415\nb2[2] = -4")
    assert (rep["statements"], rep["applied"], rep["cut_off"]) == (7, 4, True), rep
    assert list(net["b1"][:6]) == [1, 2, 3, 0, 0, np.float32(1e-3)] and net["b2"][0] == 1e6 and net["b2"][1] == -415
    assert net["b2"][2] == 0  # the cut last line is dropped
    print("example block: ok")
    for game in ("breakout", "seaquest", "asterix"):
        net, rep = read_reply((EXP5 / "runs" / game / "reply" / "answer.md").read_text())
        want = json.loads((EXP5 / "runs" / game / "apply.json").read_text())["edit_report"]
        assert not rep["errors"] and rep["statements"] == want["statements"], (game, rep)
        ref = load_net(EXP5 / "networks" / game / "hand.npz")
        for k in SHAPES:
            assert ref[k].dtype == np.float32 and np.array_equal(net[k], ref[k]), (game, k)
        print(f"{game}: {rep['statements']} statements, network identical to hand.npz")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", nargs="?")
    ap.add_argument("--game", default="breakout")
    ap.add_argument("--episodes", type=int, default=1000)
    ap.add_argument("--workers", type=int)
    ap.add_argument("--save")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    result = {"source": a.source, "game": a.game}
    if a.source == "rule":
        assert a.game == "breakout", "the rule baseline is for Breakout"
        src = "rule"
    elif a.source == "zero":
        src = {k: np.zeros(s, np.float32) for k, s in SHAPES.items()}
    elif a.source.endswith(".npz"):
        src = load_net(a.source)
    else:
        src, result["reading"] = read_reply(Path(a.source).read_text())
        if a.save:
            save_net(src, a.save)
    result.update(score(a.game, src, a.episodes, a.workers))
    print(json.dumps(result, indent=1))
    if a.out:
        Path(a.out).write_text(json.dumps(result, indent=1) + "\n")


if __name__ == "__main__":
    main()
