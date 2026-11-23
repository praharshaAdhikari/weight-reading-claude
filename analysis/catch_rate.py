"""Per network: how often the paddle catches the ball when it reaches the bottom row (200 episodes, seeds 5000+)."""
import sys, json, glob, numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
import score
from minatar import Environment

def catches(path):
    net = score.load_net(path) if path != "rule" else "rule"
    pol = score.rule_policy if net == "rule" else score.network_policy(net)
    c = m = 0
    for seed in range(5000, 5200):
        env = Environment("breakout", sticky_action_prob=0.1, difficulty_ramping=True); env.seed(seed); env.reset()
        M = score.channel_map("breakout", env.env.channels); rng = np.random.default_rng(seed)
        done, steps = False, 0
        while not done and steps < score.MAX_STEPS:
            e = env.env; coming = e.ball_y == 8 and e.ball_dir in (2, 3)
            x = ((env.state().reshape(100, -1) @ M) > 0).reshape(600).astype(np.float64)
            _, done = env.act(pol(x, rng)); steps += 1
            if coming: (m := m + 1) if done else (c := c + 1)
    return path, c, m

if __name__ == "__main__":
    R = str(__import__("pathlib").Path(__file__).resolve().parent.parent) + "/"
    paths = ["rule", R + "lm_understand-logs/exp5_write_from_scratch/networks/breakout/hand.npz"]
    for f in sorted(glob.glob(R + "runs/breakout/*/*/score.json")):
        s = json.load(open(f))
        if s["reading"]["nonzero"]["W3"] and s["mean"] > 8: paths.append(f.replace("score.json", "net.npz"))
    with ProcessPoolExecutor(3) as ex:
        for p, c, m in ex.map(catches, paths):
            name = "rule" if p == "rule" else "astra" if "hand" in p else "/".join(p.split("/")[-3:-1])
            sc = "" if p == "rule" or "hand" in p else json.load(open(p.replace("net.npz", "score.json")))["mean"]
            print(f"{name:16} score {sc!s:7} catches {c:6} misses {m:4}  miss rate per ball {m/max(c+m,1):.4f}")
