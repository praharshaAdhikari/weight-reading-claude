#!/usr/bin/env python3
"""Figures for the article.

  viz.py gif SOURCE OUT.gif [--label TEXT] [--seed 0] [--steps 400]
      SOURCE: a network (.npz), 'zero' or 'rule'. One Breakout episode, played as score.py plays it.
  viz.py pair SOURCE SOURCE OUT.gif --labels TEXT TEXT [--seed 0] [--steps 400]
      Two sources side by side on the same game seed.
  viz.py tables FILE.md PREFIX
      Each Markdown table in FILE as PREFIX1.png, PREFIX2.png, ... (Medium has no tables).
  viz.py dots OUT.png
      Every counted run: score against output tokens, one panel per model; runs cut off at the cap stacked past it.
  viz.py w1 NET.npz OUT.png [--title TEXT] [--subtitle TEXT]
      First-layer weights of every hidden unit the network uses, one 10 x 10 map per input channel.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import score

# reference palette (dataviz skill), light mode: Medium pages are light
GRID, INK, MUTED = "#e1e0d9", "#0b0b0b", "#898781"
BG, CARD = "#f3f2ee", "#ffffff"  # page tint, so each panel reads as its own white card (all figures)
PADDLE, BRICK, BALL, TRAIL = "#2a78d6", "#eb6834", "#0b0b0b", "#c3c2b7"
OPEN_SANS = "/usr/share/fonts/open-sans/OpenSans-{}.ttf"  # static Open Sans (Google Fonts)
CELL, PAD, HEAD = 44, 20, 56  # GIF: board cell, page margin, header height (px)


def font(size, weight="Regular"):
    return ImageFont.truetype(OPEN_SANS.format(weight), size)


def mpl_style():
    """matplotlib with the figures' shared look; returns (plt, matplotlib)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    for w in ("Regular", "Semibold"):
        font_manager.fontManager.addfont(OPEN_SANS.format(w))
    plt.rcParams.update({"font.family": "Open Sans", "font.size": 10.5, "axes.edgecolor": GRID,
                         "text.hinting": "no_hinting", "text.hinting_factor": 1,  # unhinted draws smoother in Agg
                         "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": MUTED})
    return plt, matplotlib


def card(fig, x0, y0, x1, y1, matplotlib):
    """A rounded white card behind figure coordinates (x0, y0)-(x1, y1)."""
    fig.patches.append(matplotlib.patches.FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0, transform=fig.transFigure, zorder=-1, boxstyle="round,pad=0,rounding_size=0.012",
        facecolor=CARD, edgecolor=GRID, lw=1))


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


def draw(state, ch, total, label, f_big, f_small, over=False, k=2):
    """One frame, drawn at k times the size and scaled down: PIL shapes have no anti-aliasing of their own."""
    C, P, W = CELL * k, PAD * k, 10 * CELL * k
    X, Y = P + 16 * k, P + HEAD * k  # board origin inside the card
    im = Image.new("RGB", (W + 2 * X, Y + W + 16 * k + P), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([P, P, im.width - P - 1, im.height - P - 1], radius=14 * k, fill=CARD, outline=GRID, width=k)
    d.text((X, P + HEAD * k / 2), label, fill=INK, font=f_big, anchor="lm")
    d.text((X + W, P + HEAD * k / 2), f"score {int(total)}", fill=MUTED, font=f_small, anchor="rm")
    for i in range(11):
        d.line([(X, Y + i * C), (X + W, Y + i * C)], fill="#efeee9", width=k)
        d.line([(X + i * C, Y), (X + i * C, Y + W)], fill="#efeee9", width=k)
    for name, color, pad in (("trail", TRAIL, 14), ("brick", BRICK, 3), ("paddle", PADDLE, 3), ("ball", BALL, 9)):
        for y, x in np.argwhere(state[:, :, ch[name]]):
            box = [X + x * C + pad * k, Y + y * C + pad * k, X + (x + 1) * C - pad * k, Y + (y + 1) * C - pad * k]
            (d.ellipse if name in ("ball", "trail") else d.rounded_rectangle)(box, fill=color, **(
                {"radius": 6 * k} if name not in ("ball", "trail") else {}))
    if over:
        d.text((X + W // 2, Y + W // 2), "game over", fill=MUTED, font=f_big, anchor="mm")
    return im.resize((im.width // k, im.height // k), Image.LANCZOS)


def make_gif(source, out, label, seed=0, steps=400):
    frames, ch, done = episode_frames(source, seed, steps)
    f_big, f_small = font(44, "Semibold"), font(40)  # drawn at 2x, see draw()
    ims = [draw(s, ch, t, label, f_big, f_small) for s, t in frames[:-1]]
    s, t = frames[-1]
    ims.append(draw(s, ch, t, label, f_big, f_small, over=done))
    durations = [50] * (len(ims) - 1) + [1500]
    ims[0].save(out, save_all=True, append_images=ims[1:], duration=durations, loop=0, optimize=True)
    return len(ims), frames[-1][1], done


def make_pair(sources, out, labels, seed=0, steps=400):
    """Two networks side by side on the same game seed; one that ends first holds its last frame."""
    f_big, f_small = font(44, "Semibold"), font(40)
    eps = [episode_frames(src, seed, steps) for src in sources]
    n = max(len(frames) for frames, _, _ in eps)
    ims = []
    for i in range(n):
        cards = []
        for (frames, ch, done), label in zip(eps, labels):
            state, total = frames[min(i, len(frames) - 1)]
            cards.append(draw(state, ch, total, label, f_big, f_small, over=done and i >= len(frames) - 1))
        w = cards[0].width - PAD  # overlap the margins, so the gap between cards equals the outer margin
        im = Image.new("RGB", (w * len(cards) + PAD, cards[0].height), BG)
        for k, c in enumerate(cards):
            im.paste(c, (k * w, 0))
        ims.append(im)
    ims[0].save(out, save_all=True, append_images=ims[1:], duration=[50] * (n - 1) + [1500], loop=0, optimize=True)
    return n, [frames[-1][1] for frames, _, _ in eps]


def md_tables(path):
    """Every Markdown table in a file, as lists of rows of cell strings (the --- row dropped)."""
    tables, cur = [], []
    for line in Path(path).read_text().splitlines() + [""]:
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(set(c) <= set("-: ") for c in cells):
                cur.append(cells)
        elif cur:
            tables.append(cur)
            cur = []
    return tables


def table_png(rows, out, k=2):
    """A Markdown table as a card image for Medium, which has no tables. **bold** cells are drawn semibold."""
    import re
    rows = [[re.sub(r'"([^"]*)"', "\u201c\\1\u201d", c) for c in r] for r in rows]  # curly quotes, as Medium's text
    group = [i > 1 and r[0] == rows[i - 1][0] for i, r in enumerate(rows)]  # repeated first cell: same group
    f_head, f_reg, f_bold = font(15 * k, "Semibold"), font(16 * k), font(16 * k, "Semibold")
    cell = lambda c: (c.replace("**", ""), f_bold if c.startswith("**") else f_reg)
    padx, rowh, gap = 22 * k, 46 * k, 40 * k
    meas = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    widths = [max(meas.textlength(*cell(r[j])) if i else meas.textlength(r[j], f_head) for i, r in enumerate(rows))
              for j in range(len(rows[0]))]
    W = int(sum(widths) + gap * (len(widths) - 1) + 2 * padx)
    H = rowh * len(rows) + 16 * k
    m = PAD * k
    im = Image.new("RGB", (W + 2 * m, H + 2 * m), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([m, m, m + W, m + H], radius=14 * k, fill=CARD, outline=GRID, width=k)
    for i, r in enumerate(rows):
        y = m + 8 * k + rowh * i + rowh / 2
        if i:
            d.line([m + padx, y - rowh / 2, m + W - padx, y - rowh / 2],
                   fill=MUTED if i == 1 else "#f0efea" if group[i] else GRID, width=k)
        x = m + padx
        for j, c in enumerate(r):
            text, f = (c.replace("**", ""), f_head) if i == 0 else cell(c)
            if not (j == 0 and group[i]):  # model named once per group
                d.text((x, y), text, fill=MUTED if i == 0 else INK, font=f, anchor="lm")
            x += widths[j] + gap
    im.save(out)
    return im.size


def load_source(source):
    """'rule', 'zero' or a network .npz."""
    if source == "rule":
        return source
    return {k: np.zeros(s, np.float32) for k, s in score.SHAPES.items()} if source == "zero" else score.load_net(source)


ARMS = [("haiku-medium", "Haiku 5.5 · medium"), ("opus-medium", "Opus 5.5 · medium"), ("fable-medium", "Fable 5.2 · medium"),
        ("haiku-high", "Haiku 5.5 · high"), ("haiku-xhigh", "Haiku 5.5 · xhigh"), ("sonnet-high", "Sonnet 5.5 · high"),
        ("sonnet-xhigh", "Sonnet 5.5 · xhigh"), ("opus-high", "Opus 5.5 · high"), ("opus-xhigh", "Opus 5.5 · xhigh"),
        ("opus-max", "Opus 5.5 · max"), ("sonnet-max", "Sonnet 5.5 · max"), ("fable-high", "Fable 5.2 · high"), ("fable-xhigh", "Fable 5.2 · xhigh")]
MODELS = [("haiku", "Haiku 5.5", "#2a78d6"), ("sonnet", "Sonnet 5.5", "#eb6834"), ("opus", "Opus 5.5", "#1baf7a"),
          ("fable", "Fable 5.2", "#eda100")]  # categorical slots 1-4, in order (dataviz palette, validated)
EFFORTS = [("medium", "s", True), ("high", "^", True), ("xhigh", "o", False), ("max", "D", False)]  # marker, filled
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
    plt, matplotlib = mpl_style()
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
    drawn = {e for key, _, _ in MODELS for e, _, _ in EFFORTS if any(r["tokens"] for r in counted_runs(f"{key}-{e}"))}
    for e, mk, f in [t for t in EFFORTS if t[0] in drawn]:  # no legend marker for a setting that never finished (max)
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
    for p, _ in boxes:
        card(fig, p.x0 - L, p.y0 - B, p.x1 + R, p.y1 + T, matplotlib)
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
    card(fig, x0, ny0, x1, ny1, matplotlib)
    fig.savefig(out, facecolor=BG)


CHANNELS = [(0, "paddle"), (3, "ball"), (4, "ball's last cell")]  # the only inputs Breakout fills, besides bricks


def w1(net_path, out, title="", subtitle=""):
    """First-layer weights, one 10 x 10 map per (input channel, hidden unit used), in Figure 1's card style."""
    import textwrap
    from matplotlib.colors import LinearSegmentedColormap
    plt, matplotlib = mpl_style()
    W = score.load_net(net_path)["W1"].reshape(10, 10, 6, 32)  # input i = (row*10 + col)*6 + channel
    bricks = bool(np.abs(W[:, :, 2]).sum())
    chans = CHANNELS + [(2, "bricks")] * bricks
    units = [u for u in range(32) if np.abs(W[..., u]).sum()]
    lim = float(np.percentile(np.abs(W[W != 0]), 98))  # a few huge weights would wash out the rest
    if not title:  # from the run folder: runs/breakout/<model>-<effort>/<nn>/net.npz
        run = Path(net_path).parent
        model, effort = run.parent.name.split("-")
        name = dict((k, n) for k, n, _ in MODELS)[model]
        sc = json.loads((run / "score.json").read_text())["mean"]
        title = f"{name} · {effort}"  # readers know a network by its score; run numbers stay in the repo
        subtitle = f"the {sc:.1f}-point network · uses {len(units)} of 32 hidden units"
    cmap = LinearSegmentedColormap.from_list("div", ["#1c5cab", "#86b6ef", "#f0efec", "#f19a96", "#e34948"])
    n, m = len(units), len(chans)
    fig, axes = plt.subplots(m, n, figsize=(0.95 * n + 1.9, 1.05 * m + 3.4), dpi=200, facecolor=BG, squeeze=False,
                             gridspec_kw={"wspace": 0.14, "hspace": 0.14})
    fig.subplots_adjust(left=0.135, right=0.975, top=0.80, bottom=0.40)
    for r, (c, label) in enumerate(chans):
        for k, u in enumerate(units):
            ax = axes[r][k]
            im = ax.imshow(W[:, :, c, u], cmap=cmap, vmin=-lim, vmax=lim)
            ax.set_xticks([]), ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_color(GRID)
            if r == 0:
                ax.set_title(f"unit {u}", fontsize=9, color=MUTED, pad=5)
            if k == 0:
                ax.set_ylabel(label, fontsize=10, color=INK, rotation=0, ha="right", va="center", labelpad=8)
    # card around the grid with its labels, title and subtitle inside its top (as in Figure 1)
    fig.canvas.draw()
    inv, rend = fig.transFigure.inverted(), fig.canvas.get_renderer()
    bb = [ax.get_tightbbox(rend).transformed(inv) for ax in axes.flat]
    padx, pady = 0.022, 0.035
    x0, x1 = min(b.x0 for b in bb) - padx, max(b.x1 for b in bb) + padx
    y0, gy1 = min(b.y0 for b in bb) - pady, max(b.y1 for b in bb)
    fig.text((x0 + x1) / 2, gy1 + 0.045, subtitle, ha="center", fontsize=9, color=MUTED)
    fig.text((x0 + x1) / 2, gy1 + 0.095, title, ha="center", fontsize=12.5, fontweight="semibold", color=INK)
    card(fig, x0, y0, x1, gy1 + 0.145, matplotlib)
    # colour scale under the card, like Figure 1's axis name; notes in a card of their own
    cw = 0.5 * (x1 - x0)
    cax = fig.add_axes([(x0 + x1 - cw) / 2, y0 - 0.075, cw, 0.022])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=MUTED, length=0, labelsize=8.5)
    cb.set_label(f"weight (colours clipped at ±{lim:g})", color=MUTED, fontsize=9.5)
    fig.canvas.draw()
    ny1, pad = cax.get_tightbbox(rend).transformed(inv).y0 - 0.05, 0.04
    notes = [("Reading it", "Each column is one hidden unit. Each row is one input, drawn as the 10 × 10 screen: where"
                            " the paddle is, where the ball is, and where the ball was a step ago. Red excites the"
                            " unit, blue inhibits it."),
             ("Not shown", f"The network has room for 32 hidden units; the other {32 - n} have all-zero weights"
                           + ("." if bricks else ", and so do the bricks inputs.")
                           + " The largest few weights are clipped so they don't wash out the rest.")]
    texts, colw = [], (x1 - x0) / 2
    for i, (head, body) in enumerate(notes):
        cx = x0 + i * colw + padx
        fig.text(cx, ny1 - pad, head, fontsize=8.5, fontweight="semibold", color=INK, va="top")
        texts.append(fig.text(cx, ny1 - pad - 0.036, textwrap.fill(body, int(colw * fig.get_figwidth() * 14), break_on_hyphens=False),
                              fontsize=8.5, color=MUTED, va="top", linespacing=1.5))
    fig.canvas.draw()
    ny0 = min(t.get_window_extent(rend).transformed(inv).y0 for t in texts) - pad + 0.012
    card(fig, x0, ny0, x1, ny1, matplotlib)
    fig.savefig(out, facecolor=BG, bbox_inches="tight", pad_inches=0.3)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gif")
    g.add_argument("source")
    g.add_argument("out")
    g.add_argument("--label", default="")
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--steps", type=int, default=400)
    pr = sub.add_parser("pair")
    pr.add_argument("a")
    pr.add_argument("b")
    pr.add_argument("out")
    pr.add_argument("--labels", nargs=2, required=True)
    pr.add_argument("--seed", type=int, default=0)
    pr.add_argument("--steps", type=int, default=400)
    tb = sub.add_parser("tables")
    tb.add_argument("markdown")
    tb.add_argument("prefix")
    sub.add_parser("dots").add_argument("out")
    h = sub.add_parser("w1")
    h.add_argument("net")
    h.add_argument("out")
    h.add_argument("--title", default="", help="default: model, effort and run from the net's folder")
    h.add_argument("--subtitle", default="")
    a = ap.parse_args()
    if a.cmd == "w1":
        w1(a.net, a.out, a.title, a.subtitle)
        print(a.out)
    if a.cmd == "tables":
        for n, rows in enumerate(md_tables(a.markdown), 1):
            print(f"{a.prefix}{n}.png", table_png(rows, f"{a.prefix}{n}.png"))
    if a.cmd == "dots":
        dots(a.out)
        print(a.out)
    if a.cmd == "pair":
        n, totals = make_pair([load_source(a.a), load_source(a.b)], a.out, a.labels, a.seed, a.steps)
        print(f"{a.out}: {n} frames, scores {totals}")
    if a.cmd == "gif":
        n, total, done = make_gif(load_source(a.source), a.out, a.label, a.seed, a.steps)
        print(f"{a.out}: {n} frames, score {int(total)}{', game over' if done else ''}")


if __name__ == "__main__":
    main()
