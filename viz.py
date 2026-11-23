#!/usr/bin/env python3
"""Figures for the article.

  viz.py gif SOURCE OUT.gif [--label TEXT] [--seed 0] [--steps 400]
      SOURCE: a network (.npz), 'zero' or 'rule'. One Breakout episode, played as score.py plays it.
  viz.py dots OUT.png
      Every counted run: score against output tokens, one panel per model; runs cut off at the cap stacked past it.
  viz.py w1 NET.npz OUT.png [--title TEXT]
      First-layer weights of every hidden unit the network uses, one 10 x 10 map per input channel.
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


ARMS = [("haiku-high", "Haiku 5.5 · high"), ("haiku-xhigh", "Haiku 5.5 · xhigh"), ("sonnet-high", "Sonnet 5.5 · high"),
        ("sonnet-xhigh", "Sonnet 5.5 · xhigh"), ("opus-high", "Opus 5.5 · high"), ("opus-xhigh", "Opus 5.5 · xhigh"),
        ("opus-max", "Opus 5.5 · max"), ("sonnet-max", "Sonnet 5.5 · max"), ("fable-high", "Fable 5.2 · high"), ("fable-xhigh", "Fable 5.2 · xhigh")]
MODELS = [("haiku", "Haiku 5.5", "#2a78d6"), ("sonnet", "Sonnet 5.5", "#eb6834"), ("opus", "Opus 5.5", "#1baf7a"),
          ("fable", "Fable 5.2", "#eda100")]  # categorical slots 1-4, in order (dataviz palette, validated)
EFFORTS = [("high", "^", True), ("xhigh", "o", False), ("max", "D", False)]  # marker, filled
REFS = [(0.54, "random"), (8.37, "rule"), (25.3, "PPO 500M"), (502.9, "Astra")]


def counted_runs(label, game="breakout"):
    """One dict per counted run of an arm: score, output tokens (None if cut off at the cap), and how it ended."""
    out = []
    for d in sorted((Path(__file__).parent / "runs" / game / label).glob("[0-9][0-9]")):
        if not (d / "score.json").exists():
            continue
        run, sc = json.loads((d / "run.json").read_text()), json.loads((d / "score.json").read_text())
        if run["outcome"] == "infra":
            continue
        tokens = ((run.get("result") or {}).get("usage") or {}).get("output_tokens")
        kind = ("wrote" if sc["reading"]["nonzero"]["W3"] else "writing" if sc["reading"]["block"] else "thinking")
        out.append({"score": sc["mean"], "tokens": tokens, "kind": kind, "run": d.name})
    return out


def dots(out):
    """One panel per model, score against output tokens; runs cut off at the 128K cap stack as arrows past it."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for w in ("Regular", "Semibold"):  # static Open Sans (Google Fonts); unhinted text draws smoother in Agg
        font_manager.fontManager.addfont(f"/usr/share/fonts/open-sans/OpenSans-{w}.ttf")
    plt.rcParams.update({"font.family": "Open Sans", "font.size": 10.5, "axes.edgecolor": GRID,
                         "text.hinting": "no_hinting", "text.hinting_factor": 1,
                         "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": MUTED})
    BG, CARD = "#f3f2ee", "#ffffff"  # page tint, so each panel reads as its own white card
    fig, axs = plt.subplots(2, 2, figsize=(12, 9.6), dpi=200, facecolor=BG, sharex=True, sharey=True,
                            gridspec_kw={"hspace": 0.55, "wspace": 0.3})
    CAP0, CAP1 = 134, 166  # the column past the cap, in thousands of tokens
    for ax, (key, model, color) in zip(axs.flat, MODELS):
        arms = [(e, mk, filled, runs) for e, mk, filled in EFFORTS if (runs := counted_runs(f"{key}-{e}"))]
        ax.set_facecolor(CARD)
        ax.tick_params(length=0, which="both")
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.set_yscale("log")
        ax.set_ylim(0.3, 2600)  # headroom so the best-score label clears the subtitle
        ax.set_xlim(0, CAP1)
        for v in (1, 10, 100):
            ax.axhline(v, color=GRID, lw=0.6, zorder=0)
        ax.axvspan(CAP0, CAP1, color="#f0efea", zorder=0, lw=0)
        ax.text((CAP0 + CAP1) / 2, 2300, "hit the\n128K cap", ha="center", va="top", fontsize=8.5, color=MUTED,
                linespacing=1.2)  # top of the grey column: empty, and clear of the 128K tick below
        for v, name in REFS:
            ax.axhline(v, color=TRAIL, lw=1, ls=(0, (5, 4)), zorder=1)
            ax.text(CAP1 + 2, v, name, va="center", fontsize=8.5, color=MUTED, clip_on=False)
        counts = " · ".join(f"{e} {sum(r['kind'] == 'wrote' for r in runs)}/{len(runs)}" for e, _, _, runs in arms)
        ax.set_title(model, loc="center", fontsize=12.5, fontweight="semibold", color=INK, pad=20)
        ax.text(0.5, 1.02, f"finished: {counts}", transform=ax.transAxes, ha="center", fontsize=9, color=MUTED)
        m = dict(s=46, zorder=3, linewidths=1.4)
        fin = [(e, mk, f, r) for e, mk, f, runs in arms for r in runs if r["tokens"] is not None]
        for e, mk, f, r in fin:
            ax.scatter(r["tokens"] / 1000, max(r["score"], 0.3), marker=mk, edgecolors=color,
                       facecolors=color if f else CARD, clip_on=False, **m)  # 0.00 (sonnet-high/04) on the floor
        if fin:  # the panel's best network, named
            e, _, _, b = max(fin, key=lambda t: t[3]["score"])
            ax.annotate(f"{b['score']:.0f}", (b["tokens"] / 1000, b["score"]), xytext=(0, 9),
                        textcoords="offset points", ha="center", fontsize=9, color=INK)
        # cut off: one stack per setting, five arrows to a row, counted above (log y, so rows step by a factor)
        row = 0
        for e, _, f, runs in arms:
            cut = [r for r in runs if r["tokens"] is None]
            for i, r in enumerate(cut):
                ax.scatter(CAP0 + 5 + (i % 5) * 5.5, 0.54 * 1.42 ** (row + i // 5), marker=">", edgecolors=color,
                           facecolors=color if f else CARD, **dict(m, s=34))
            if cut:
                row += -(-len(cut) // 5)
                ax.text((CAP0 + CAP1) / 2, 0.54 * 1.42 ** (row - 0.45), f"{len(cut)} {e}", ha="center", va="bottom",
                        fontsize=8.5, color=INK)
                row += 1.8
        ax.set_yticks([0.5, 1, 5, 10, 50, 100, 500], ["0.5", "1", "5", "10", "50", "100", "500"])
        ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_xticks([0, 32, 64, 96, 128], ["0", "32K", "64K", "96K", "128K"])
        ax.tick_params(labelbottom=True, labelleft=True)
    # axis names once for the figure, outside the cards, so all four cards hold the same things
    fig.text(0.012, 0.53, "score, mean of 1,000 games (log)", rotation=90, va="center", color=MUTED)
    for e, mk, f in EFFORTS:
        axs[0, 0].scatter([], [], marker=mk, edgecolors=INK, facecolors=INK if f else CARD, s=46, linewidths=1.4,
                          label=e)
    axs[0, 0].scatter([], [], marker=">", edgecolors=INK, facecolors=INK, s=34, label="cut off at the cap (no network)")
    fig.subplots_adjust(left=0.07, right=0.915, top=0.885, bottom=0.246)
    # cards: one rounded white box per panel, the same overhang on every panel (the largest one needed)
    fig.canvas.draw()
    inv, rend = fig.transFigure.inverted(), fig.canvas.get_renderer()
    boxes = [(ax.get_position(), ax.get_tightbbox(rend).transformed(inv)) for ax in axs.flat]
    padx, pady = 0.014, 0.016
    L = max(p.x0 - t.x0 for p, t in boxes) + padx
    R = max(t.x1 - p.x1 for p, t in boxes) + padx
    B = max(p.y0 - t.y0 for p, t in boxes) + pady
    T = max(t.y1 - p.y1 for p, t in boxes) + pady
    card = dict(transform=fig.transFigure, zorder=-1, boxstyle="round,pad=0,rounding_size=0.012", facecolor=CARD,
                edgecolor=GRID, lw=1)
    for p, _ in boxes:
        fig.patches.append(matplotlib.patches.FancyBboxPatch((p.x0 - L, p.y0 - B), p.width + L + R,
                                                             p.height + B + T, **card))
    x0, x1 = boxes[0][0].x0 - L, boxes[1][0].x1 + R
    top, bottom = boxes[0][0].y1 + T, boxes[2][0].y0 - B
    # legend just above the cards; axis name just below them; notes in a full-width card of their own
    fig.legend(loc="lower center", bbox_to_anchor=(0.5, top + 0.008), ncol=4, frameon=False, fontsize=9.5)
    fig.text(0.5, bottom - 0.022, "output tokens, almost all thinking", ha="center", va="top", color=MUTED)
    # notes: one heading + text per column of cards; the card is sized from the drawn text, equal padding all round
    import textwrap
    notes = [("Marks", "Each mark is one run of Claude through claude -p: one reply, MinAtar Breakout. Arrows hit the"
                       " cap, wrote no network and play at random (0.54); they are only stacked, so their height"
                       " isn't a score. A mark on the bottom edge scored 0."),
             ("Dashed lines", "Random play (0.54), the follow-the-ball rule (8.4), PPO after 500M steps (25.3)"
                              " and GPT-6\u00a0Astra's network under the same scorer (502.9). PPO is reinforcement"
                              " learning on the same network shape, as reported in the original post.")]
    ny1, pad = bottom - 0.062, 0.018
    texts = []
    for cx, (head, body) in zip((x0, boxes[1][0].x0 - L), notes):
        fig.text(cx + padx, ny1 - pad, head, fontsize=8.5, fontweight="semibold", color=INK, va="top")
        texts.append(fig.text(cx + padx, ny1 - pad - 0.024, textwrap.fill(body, 80, break_on_hyphens=False),
                              fontsize=8.5, color=MUTED, va="top", linespacing=1.5))
    fig.canvas.draw()
    ny0 = min(t.get_window_extent(rend).transformed(inv).y0 for t in texts) - pad + 0.006  # text box includes descent
    fig.patches.append(matplotlib.patches.FancyBboxPatch((x0, ny0), x1 - x0, ny1 - ny0, **card))
    fig.savefig(out, facecolor=BG)


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
