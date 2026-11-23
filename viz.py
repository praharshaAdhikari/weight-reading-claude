#!/usr/bin/env python3
"""Figures for the article.

  viz.py gif SOURCE OUT.gif [--label TEXT] [--seed 0] [--steps 400]
      SOURCE: a network (.npz), 'zero' or 'rule'. One Breakout episode, played as score.py plays it.
  viz.py dots OUT.png
  viz.py w1 NET.npz OUT.png [--title TEXT]
      First-layer weights of every hidden unit the network uses, one 10 x 10 map per input channel.
      Every counted run's score, one row per model and effort, log scale, with the baselines marked.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import score

# reference palette (dataviz skill), light mode: Medium pages are light
SURFACE, GRID, INK, MUTED = "#fcfcfb", "#e1e0d9", "#0b0b0b", "#898781"
PADDLE, BRICK, BALL, TRAIL = "#2a78d6", "#eb6834", "#0b0b0b", "#c3c2b7"
CELL, HEAD = 28, 34


def font(size):
    for f in ("/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def episode_frames(source, seed=0, steps=400, game="breakout"):
    """(state, total score) for each step of one episode, seeded as in score.play."""
    from minatar import Environment
    policy = score.rule_policy if isinstance(source, str) else score.network_policy(source)
    env = Environment(game, sticky_action_prob=0.1, difficulty_ramping=True)
    env.seed(seed)
    M = score.channel_map(game, env.env.channels)
    rng = np.random.default_rng(seed)
    env.reset()
    total, done, out = 0.0, False, []
    while not done and len(out) < steps:
        s = env.state()
        out.append((s, total))
        x = ((s.reshape(100, -1) @ M) > 0).reshape(600).astype(np.float64)
        r, done = env.act(policy(x, rng))
        total += r
    out.append((env.state(), total))
    return out, env.env.channels, done


def draw(state, ch, total, label, f_big, f_small, over=False):
    W = 10 * CELL
    im = Image.new("RGB", (W, HEAD + W), SURFACE)
    d = ImageDraw.Draw(im)
    d.text((8, 8), label, fill=INK, font=f_big)
    d.text((W - 8, 8), f"score {int(total)}", fill=INK, font=f_big, anchor="ra")
    for i in range(11):
        d.line([(0, HEAD + i * CELL), (W, HEAD + i * CELL)], fill=GRID)
        d.line([(i * CELL, HEAD), (i * CELL, HEAD + W)], fill=GRID)
    for name, color, pad in (("trail", TRAIL, 9), ("brick", BRICK, 2), ("paddle", PADDLE, 2), ("ball", BALL, 6)):
        for y, x in np.argwhere(state[:, :, ch[name]]):
            box = [x * CELL + pad, HEAD + y * CELL + pad, (x + 1) * CELL - pad, HEAD + (y + 1) * CELL - pad]
            (d.ellipse if name in ("ball", "trail") else d.rounded_rectangle)(box, fill=color, **(
                {"radius": 4} if name not in ("ball", "trail") else {}))
    if over:
        d.text((W // 2, HEAD + W // 2), "game over", fill=MUTED, font=f_small, anchor="mm")
    return im


def make_gif(source, out, label, seed=0, steps=400):
    frames, ch, done = episode_frames(source, seed, steps)
    f_big, f_small = font(16), font(14)
    ims = [draw(s, ch, t, label, f_big, f_small) for s, t in frames[:-1]]
    s, t = frames[-1]
    ims.append(draw(s, ch, t, label, f_big, f_small, over=done))
    durations = [50] * (len(ims) - 1) + [1500]
    ims[0].save(out, save_all=True, append_images=ims[1:], duration=durations, loop=0, optimize=True)
    return len(ims), frames[-1][1], done


ARMS = [("haiku", "Haiku 5.5 · xhigh"), ("haiku-high", "Haiku 5.5 · high"), ("sonnet", "Sonnet 5.5 · xhigh"),
        ("opus", "Opus 5.5 · xhigh"), ("opus-max", "Opus 5.5 · max"), ("fable", "Fable 5.2 · xhigh"),
        ("fable-high", "Fable 5.2 · high")]
REFS = [(0.54, "random", "center"), (8.37, "ball-follow rule ", "right"), (25.3, " PPO 500M steps", "left"),
        (502.9, "GPT-6 Astra", "center")]


def counted_runs(label, game="breakout"):
    """One dict per counted run of an arm: score, output tokens, and how it ended."""
    out = []
    for d in sorted((Path(__file__).parent / "runs" / game / label).glob("[0-9][0-9]")):
        if not (d / "score.json").exists():
            continue
        run, sc = json.loads((d / "run.json").read_text()), json.loads((d / "score.json").read_text())
        if run["outcome"] == "infra":
            continue
        tokens = ((run.get("result") or {}).get("usage") or {}).get("output_tokens") or 128_000  # cut off = cap
        kind = ("wrote" if sc["reading"]["nonzero"]["W3"] else "writing" if sc["reading"]["block"] else "thinking")
        out.append({"score": sc["mean"], "tokens": tokens, "kind": kind, "run": d.name})
    return out


STYLE = {"wrote": dict(facecolors=PADDLE, edgecolors=PADDLE),
         "writing": dict(facecolors=SURFACE, edgecolors=PADDLE),
         "thinking": dict(facecolors=SURFACE, edgecolors=MUTED)}
LEGEND = {"wrote": "finished a network", "writing": "cut off while writing the network",
          "thinking": "cut off while still thinking"}


def dots(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    font_manager.fontManager.addfont("/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf")
    plt.rcParams.update({"font.family": "Noto Sans", "font.size": 10.5, "axes.edgecolor": GRID,
                         "xtick.color": MUTED, "ytick.color": INK, "axes.labelcolor": MUTED})
    arms = [(name, runs) for k, name in ARMS if (runs := counted_runs(k))][::-1]  # first arm at the top
    n = len(arms)
    fig, (ax, at, ax3) = plt.subplots(1, 3, figsize=(13, 0.7 * n + 1.5), dpi=200, facecolor=SURFACE, sharey=True,
                                      gridspec_kw={"width_ratios": [5.2, 2.6, 2.2], "wspace": 0.06})
    for a_ in (ax, at, ax3):
        a_.set_facecolor(SURFACE)
        a_.tick_params(length=0, which="both")
        for side in ("top", "right", "left"):
            a_.spines[side].set_visible(False)
        for row in range(n):
            a_.axhline(row, color=GRID, lw=0.6, zorder=0)
    m = dict(s=44, zorder=3, linewidths=1.4)

    # 1. score, log scale
    for x, name, ha in REFS:
        ax.axvline(x, ymax=(n + 0.02) / (n + 0.5), color=TRAIL, lw=1, zorder=1)
        ax.text(x, n - 0.45, name, ha=ha, va="bottom", fontsize=8.5, color=MUTED)
    for row, (_, runs) in enumerate(arms):
        blank = [r for r in runs if r["kind"] != "wrote"]
        for kind in ("thinking", "writing"):  # blank networks all score 0.54: one marker per kind, with a count
            k = sum(r["kind"] == kind for r in blank)
            if k:
                y = row + (0.17 if kind == "writing" and len({r["kind"] for r in blank}) > 1 else 0)
                ax.scatter(0.54, y, **m, **STYLE[kind])
                ax.text(0.63, y, f"×{k}", va="center", fontsize=9, color=MUTED)
        placed = []
        for r in sorted((r for r in runs if r["kind"] == "wrote"), key=lambda r: r["score"]):
            lx, k = np.log10(r["score"]), 0
            while any(abs(lx - px) < 0.045 and pk == k for px, pk in placed):
                k += 1
            placed.append((lx, k))
            ax.scatter(r["score"], row + 0.15 * ((k + 1) // 2) * (1 if k % 2 else -1), **m, **STYLE["wrote"])
            if r["score"] >= 300:
                ax.text(r["score"] * 1.18, row + 0.15 * ((k + 1) // 2) * (1 if k % 2 else -1), f"{r['score']:.0f}",
                        va="center", fontsize=8.5, color=INK)
    ax.set_xscale("log")
    ax.set_xlim(0.35, 1000)
    ax.set_ylim(-0.6, n - 0.05)
    ax.set_yticks(range(n), [a[0] for a in arms])
    ax.set_xticks([1, 10, 100, 500], ["1", "10", "100", "500"])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("Breakout score, mean of 1,000 games (log scale)")

    # 2. output tokens: the 128K cap is why most runs wrote nothing
    at.axvline(128, ymax=(n + 0.02) / (n + 0.5), color=TRAIL, lw=1, zorder=1)
    at.text(128, n - 0.45, "output cap", ha="right", va="bottom", fontsize=8.5, color=MUTED)
    rng = np.random.default_rng(0)
    for row, (_, runs) in enumerate(arms):
        for r in runs:
            at.scatter(r["tokens"] / 1000, row + rng.uniform(-0.2, 0.2), **m, **STYLE[r["kind"]])
    at.set_xlim(0, 140)
    at.set_xticks([0, 32, 64, 96, 128], ["0", "32K", "64K", "96K", "128K"])
    at.set_xlabel("output tokens, almost all thinking")

    # 3. summary per arm
    ax3.set_xlim(0, 1)
    ax3.set_xticks([])
    ax3.spines["bottom"].set_visible(False)
    for x, head in ((0.02, "finished"), (0.38, "median"), (0.70, "best")):
        ax3.text(x, n - 0.45, head, va="bottom", fontsize=8.5, color=MUTED)
    for row, (_, runs) in enumerate(arms):
        sc = [r["score"] for r in runs]
        wrote = sum(r["kind"] == "wrote" for r in runs)
        for x, txt in ((0.02, f"{wrote} of {len(runs)}"), (0.38, f"{np.median(sc):.3g}"), (0.70, f"{max(sc):.3g}")):
            ax3.text(x, row, txt, va="center", fontsize=10, color=INK)

    for kind, label in LEGEND.items():
        ax.scatter([], [], **dict(m, zorder=0), **STYLE[kind], label=label)
    fig.legend(loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False, fontsize=9.5)
    fig.text(0.01, 0.005, "Each dot is one run. Runs that finish no network play as the all-zero network (random play,"
             " 0.54). Claude via claude -p, one reply, 128K output cap; MinAtar Breakout.", fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.035, 1, 0.95))
    fig.savefig(out, facecolor=SURFACE)


CHANNELS = [(0, "paddle"), (3, "ball"), (4, "ball's last cell")]  # the only inputs Breakout fills, besides bricks


def w1(net_path, out, title=""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.colors import LinearSegmentedColormap
    font_manager.fontManager.addfont("/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf")
    plt.rcParams.update({"font.family": "Noto Sans", "font.size": 10})
    W = score.load_net(net_path)["W1"].reshape(10, 10, 6, 32)  # input i = (row*10 + col)*6 + channel
    chans = CHANNELS + [(2, "bricks")] * bool(np.abs(W[:, :, 2]).sum())
    units = [u for u in range(32) if np.abs(W[..., u]).sum()]
    lim = float(np.percentile(np.abs(W[W != 0]), 98))  # a few huge weights would wash out the rest
    cmap = LinearSegmentedColormap.from_list("div", ["#1c5cab", "#86b6ef", "#f0efec", "#f19a96", "#e34948"])
    fig, axes = plt.subplots(len(chans), len(units), figsize=(0.95 * len(units) + 1.4, 1.05 * len(chans) + 1.2),
                             dpi=200, facecolor=SURFACE, squeeze=False)
    for r, (c, name) in enumerate(chans):
        for k, u in enumerate(units):
            ax = axes[r][k]
            im = ax.imshow(W[:, :, c, u], cmap=cmap, vmin=-lim, vmax=lim)
            ax.set_xticks([]), ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_color(GRID)
            if r == 0:
                ax.set_title(f"unit {u}", fontsize=9, color=MUTED)
            if k == 0:
                ax.set_ylabel(name, fontsize=10, color=INK, rotation=0, ha="right", va="center")
    cb = fig.colorbar(im, ax=axes, orientation="horizontal", fraction=0.04, pad=0.04, aspect=50)
    cb.set_label(f"weight (clipped at ±{lim:g}; red excites the unit, blue inhibits)", color=MUTED, fontsize=9)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=MUTED, length=0, labelsize=8)
    if title:
        fig.suptitle(title, color=INK, fontsize=12, x=0.02, ha="left")
    fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gif")
    g.add_argument("source")
    g.add_argument("out")
    g.add_argument("--label", default="")
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--steps", type=int, default=400)
    sub.add_parser("dots").add_argument("out")
    h = sub.add_parser("w1")
    h.add_argument("net")
    h.add_argument("out")
    h.add_argument("--title", default="")
    a = ap.parse_args()
    if a.cmd == "w1":
        w1(a.net, a.out, a.title)
        print(a.out)
    if a.cmd == "dots":
        dots(a.out)
        print(a.out)
    if a.cmd == "gif":
        src = a.source if a.source == "rule" else (
            {k: np.zeros(s, np.float32) for k, s in score.SHAPES.items()} if a.source == "zero" else score.load_net(a.source))
        n, total, done = make_gif(src, a.out, a.label, a.seed, a.steps)
        print(f"{a.out}: {n} frames, score {int(total)}{', game over' if done else ''}")


if __name__ == "__main__":
    main()
