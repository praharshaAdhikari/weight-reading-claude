#!/usr/bin/env python3
"""Figures for the article.

  viz.py gif SOURCE OUT.gif [--label TEXT] [--seed 0] [--steps 400]
      SOURCE: a network (.npz), 'zero' or 'rule'. One Breakout episode, played as score.py plays it.
"""
import argparse

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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gif")
    g.add_argument("source")
    g.add_argument("out")
    g.add_argument("--label", default="")
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--steps", type=int, default=400)
    a = ap.parse_args()
    if a.cmd == "gif":
        src = a.source if a.source == "rule" else (
            {k: np.zeros(s, np.float32) for k, s in score.SHAPES.items()} if a.source == "zero" else score.load_net(a.source))
        n, total, done = make_gif(src, a.out, a.label, a.seed, a.steps)
        print(f"{a.out}: {n} frames, score {int(total)}{', game over' if done else ''}")


if __name__ == "__main__":
    main()
