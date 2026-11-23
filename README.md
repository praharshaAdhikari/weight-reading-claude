# Hand-writing a Breakout network with Claude

A replication of Experiment 5 of [*Sparks of Weight-Space Programming*](https://rikiyat.github.io/blog/weight-space-programming/)
(Rikiya Takehi, Jayden Teoh, Alex Zhang, Omar Khattab; MIT CSAIL, 2 November 2026) with Claude instead of GPT-6 Astra.
Each model gets the original prompt, byte for byte, and must write all 20,486 weights of a 600-32-32-6 MinAtar Breakout
network in one reply, with no tools. 105 runs: Haiku 5.5, Sonnet 5.5, Opus 5.5 and Fable 5.2 at effort `xhigh` and
`high` (10 each), Opus 5.5 and Sonnet 5.5 at `max` (5 each), and Haiku 5.5, Opus 5.5 and Fable 5.2 at `medium` (5 each).

## What's here
| Path | What |
|---|---|
| `PROTOCOL.md` | The protocol, committed before any run was scored, with dated amendments |
| `runs/breakout/<model>-<effort>/<nn>/` | Every run: raw event stream, reply, thinking summaries, run record, the network read from the reply (`net.npz`) and its score |
| `results/` | Baselines (Astra, random, follow-the-ball rule), per-ball catch rates, figures, GIFs, and `explorer/runs.json` (one row per counted run) |
| `article/fact-sheet.md` | Every number in the write-up with the file it comes from |
| `score.py` | Reads a reply into the network and scores it: 1,000 games, seeds 0–999, sticky actions 0.1, softmax sampling, 10,000-step cap |
| `run.py` | Runs one fresh `claude -p` session per run (Claude Code 2.1.330, tools off, 128K output cap) and scores it |
| `viz.py`, `analysis/` | Figures, GIFs, catch rates and the explorer data |

Runs numbered past 09 exist because infrastructure failures (usage limits, dropped connections) are rerun under a new
number and not counted; their folders are kept with `outcome: infra`. `runs/_stopped_by_restart/` holds runs stopped
before any output when the batch was restarted (see PROTOCOL.md); they are not counted either. In the run files, local
paths have been replaced with `/home/user` and `./`.

## Reproduce
```sh
git clone https://github.com/RikiyaT/lm_understand-logs   # the original prompts and Astra's networks
python3 -m venv .venv && .venv/bin/pip install --require-hashes -r requirements.txt
.venv/bin/python score.py --selftest                          # reading Astra's replies must give its networks
.venv/bin/python score.py runs/breakout/opus-xhigh/03/answer.md --out /tmp/score.json
.venv/bin/python run.py --models opus --effort high --target 1   # needs Claude Code, signed in
```

## License
Code (`*.py`, `analysis/`): MIT, see `LICENSE`. Data, runs, results and figures: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The original experiment's prompts and Astra's networks come from [lm_understand-logs](https://github.com/RikiyaT/lm_understand-logs) (CC BY 4.0)
and are not copied here.
