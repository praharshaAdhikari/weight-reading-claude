# Fact sheet for article/draft.md

Every number in the draft, with where it comes from. Paths are relative to the repo root.
`runs.json` means `results/explorer/runs.json` (built by `analysis/explorer_data.py` from `runs/breakout/<arm>/<nn>/run.json`
and `score.json`). "Research" means the sourced findings gathered on 2026-11-22 (outside sources, read from raw files).

## The original experiment
| Claim in draft | Value | Source |
|---|---|---|
| Weights in the network | 20,486 | 600·32+32 + 32·32+32 + 32·6+6, the prompt's 600-32-32-6 network (`lm_understand-logs/exp5_write_from_scratch/runs/breakout/reply/prompt.txt`) |
| Astra's score, as published | 517.4 | Sparks of Weight-Space Programming, Exp 5; `PROTOCOL.md` |
| RL (PPO) after 500M steps | 25 (25.3) | same paper; `results/explorer/references.json` |
| Astra's network under our scorer | 502.9 (502.88 ± 7.75) | `results/baselines/astra.json` |
| Two independent scorers | 502.8 and 502.9 | logs repo PR #1 (502.8 ± 7.7); wsplore README (502.9). Research |
| Astra's reply length | 20,567 output tokens | `lm_understand-logs/exp5_write_from_scratch/runs/breakout/apply.json` |
| … of which reasoning | about 17,000 (16,828) | same file; README.md line 46 |

## Claude results reported online (intro)
Single Opus 5.5 runs of Experiment 5 Breakout:
| Draft | Exact | Effort | Source (research) |
|---|---|---|---|
| 55 | 55.2 ± 1.7 | high | MaceTenth/weight-space-programming-replication `RESULTS.md` |
| 57 | 57.4 ± 1.7 | xhigh | Sir-Olexander/lm_understand-logs-claude (auto-continued by Claude Code) |
| 307 | 306.6 ± 7.9 | xhigh | nihilistau/weight-space-claude `runs/exp5/…opus-xhigh/scores.json` |
| 484 | 483.6 ± 5.2 | xhigh | MatinKhajavi/Weight-Space-Programming (reply auto-continued past the cap) |
| 504 | 503.7 ± 5.6 | xhigh | EphraiemSarabamoun/weight-space-programming-opus `results/exp5/scores.json` |

Left out: 336 (wsplore, could not be traced to its primary file); 51.2 (Cenrax, a different task).
"At least two … went through automatic continuations": Matin (483.6) and Sir-Olexander (57.4), per their own READMEs.

Earlier Fable result credited in the effort section: shawnghu, LessWrong post
https://www.lesswrong.com/posts/wg3K6xFFTdM6RmRgn/claude-fable-5-2-can-do-weight-space-programming-about-as and data
https://huggingface.co/datasets/shawnghu/fable-weight-space-programming. Fable 5.2 high, Breakout: 456.3, 502.7, 494.6
(mean 484.5), 3 of 3 finished. At xhigh: 8 of 9 attempts across three games used the full 128K thinking.

## Our runs (all from runs.json unless noted)
| Claim | Value | Detail |
|---|---|---|
| Total runs | 85 | 40 at xhigh, 40 at high, 5 at max |
| Haiku xhigh | 0 of 10, median 0.54, best 0.54 | |
| Sonnet xhigh | 6 of 10, median 29 (29.04), best 351 (351.4, sonnet-xhigh/04) | |
| Opus xhigh | 4 of 10, median 0.54, best 510 (510.4, opus-xhigh/03) | finished: 57.2 (00), 134.2 (10), 502.7 (11), 510.4 (03) |
| Fable xhigh | 0 of 10 | |
| Opus's two best "about 17 minutes" | 17.4 and 17.9 min | opus-xhigh/11, opus-xhigh/03 |
| "beats RL by a factor of 20" | 510.4 / 25.3 = 20.2 | |
| Sonnet: six of ten beat RL | 6 (all six finished networks are above 25.3) | lowest 26.7 |
| xhigh runs that hit the 128K cap | 30 of 40 | `outcome == cut_off` |
| … still thinking when cut off | 28 | the other 2 (Sonnet) were writing |
| Median output tokens, finished xhigh runs | Opus 114,575; Sonnet 109,206 | draft says 115,000 and 109,000 |
| "more than five times" Astra | 109,206 / 20,567 = 5.3 | |
| Fable xhigh "hit the 128,000 limit while still thinking every single time" | 10 of 10 | run.json injection, empty answer.md, last block thinking |
| Haiku high | 9 of 10, median 6.4 (6.37), best 20 (20.17) | |
| Sonnet high | 10 of 10, median 7.6, best 16 (15.79); median 1.0 min, 7,384 tokens | |
| Opus high | 10 of 10, median 56 (55.6), best 352 (352.3) | |
| Opus max | 0 of 5 | |
| Fable high | 9 of 10, median 450 (449.77), best 503 (503.47) | |
| Fable high, three networks level with Astra | 503.5 (03), 502.2 (05), 500.6 (08) | all within 2 SE of 502.9 |
| Five Claude networks above 500 | opus-xhigh/03 510.4, fable-high/03 503.5, opus-xhigh/11 502.7, fable-high/05 502.2, fable-high/08 500.6 | |
| Ball-follow rule | 8 (8.37) | `results/baselines/rule.json` |
| Random play / empty network | 0.54 | `results/baselines/zero.json` |
| p-values (Fisher exact, two-sided) | Fable 0→9 of 10: 0.0001; Opus 4→10: 0.011; Sonnet 6→10: 0.087 | computed 2026-11-23 |

## Misses per ball (`results/catch_rate.txt`, 200 games per network, seeds 5000–5199; recomputed 2026-11-23)
"1 in" = (catches + misses) / misses, rounded.
| Network | Score | Catches / misses | "1 in" |
|---|---|---|---|
| Fable best (fable-high/03) | 503.5 | 117,195 / 55 | 2,132 → 2,100 |
| Opus best (opus-xhigh/03) | 510.4 | 113,941 / 64 | 1,781 → 1,800 |
| Astra | 502.9 | 103,307 / 112 | 923 → 900 |
| Opus worst finished (opus-xhigh/00) | 57.2 | 18,773 / 200 | 95 |
| Rule | 8.4 | 1,882 / 200 | 10 |

Astra misses fewer balls per game partly because 517 of its 1,000 scoring games hit the 10,000-step cap.

Identical play: fable-high/05 and opus-xhigh/11, fable-high/04 and 07, and opus-high/06 and 08 have identical catch and miss counts
although their weights differ (checked with np.array_equal). Their weights are large, so actions are near-deterministic, and
the same choices on the same seeds give the same games.

## Not checkable by script (from reading the networks and Claude Code)
- What units in opus-xhigh-11's first layer do (2 direction units, 8 landing units): from the heatmap `results/figures/w1-opus-xhigh-11.png`
  and the reply's own description in `runs/breakout/opus-xhigh/11/answer.md`.
- Claude Code's continuation behavior, checked in the installed 2.1.330 build (`~/.local/share/claude/versions/2.1.330`):
  - the retry limit is a constant `bs=3`, next to the cut-reply code (`maxOutputTokensRecoveryCount+1; return g<=bs`): "up to three more times";
  - the message "Output token limit hit while you were still reasoning … reason much more briefly …" is in the same build.
  - Our runs received only the "Output token limit hit. Resume directly …" version (37 times in `runs/breakout/*/*/run.json`), and `run.py`
    stops at the first one.
- "Hit the 128K limit": cut-off runs have no usage record. The evidence is Claude Code's output-limit message in each
  run.json plus a final block that is thinking (28 runs) or text (sonnet-xhigh/01, sonnet-xhigh/08). Checked by the fact-check agent, 2026-11-23.
- About 650 tokens of Claude Code context: measured earlier in the session; the checker could not separate it from the prompt
  in the saved files (about 4,333 cache-creation tokens in all). Reproduce before the paper.

## Fixes from the fact-check (2026-11-23)
Wording changed in the draft: "tenfold" → "ninefold" (57.2 vs 502.7/510.4); "Sonnet came close once" → "Sonnet's best was 351";
"Haiku's are no better" → "similar; its best scored 20"; Fable high "best result" → "most reliable result" (Opus xhigh has the
single highest score); Fable xhigh wording now says it hit the limit while thinking. The catch-rate table now uses
opus-xhigh/03 (510.4) for "Opus, best" and adds Fable's best.

## Added with the review fixes (2026-11-23)
| Claim | Value | Source |
|---|---|---|
| Original authors and date | Rikiya Takehi, Jayden Teoh, Alex Zhang, Omar Khattab; MIT CSAIL; 2 Nov 2026 | the post, https://rikiyat.github.io/blog/weight-space-programming/ (research) |
| Haiku high, tokens of finished runs | median 70,343; range 16,903 to 115,737 (9 runs) | runs.json |
| Haiku 0 → 9 of 10, Fisher exact two-sided | p = 0.0001 (same table as Fable) | computed |
| Sonnet high scored 0 | sonnet-high/04, 0.00 | runs.json |
| Sonnet xhigh weakest finished | 26.74 | runs.json |
| Games that hit the 10,000-step cap | Astra 517 of 1,000; Claude's five 500+ networks 703 to 780 | `results/baselines/astra.json`; runs.json `games_at_step_cap` |
| sonnet-xhigh/04 misses less often than Astra | 77 misses / 102,727 balls vs 112 / 103,419 | `results/catch_rate.txt` |
| opus-xhigh/11 uses 10 of 32 hidden units | 22 all-zero columns in `actor/dense1/kernel` | `runs/breakout/opus-xhigh/11/net.npz` |
| What units 2–9 do | 4 directions × (paddle left / right of the landing zone), wall-folded paths | `runs/breakout/opus-xhigh/11/answer.md` |
| opus-xhigh run numbers go to 11 | slots 05 and 09 were `infra` and rerun | `runs/breakout/opus-xhigh/*/run.json` |
| Replication links | 55 MaceTenth, 57 Sir-Olexander, 307 nihilistau, 484 MatinKhajavi, 504 EphraiemSarabamoun | GitHub repos (research) |
| MinAtar | Young & Tian 2019, arXiv:1903.03176 | |
