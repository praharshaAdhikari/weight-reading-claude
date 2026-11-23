# Protocol

Written and committed before any counted run. Anything changed after the first run is added under
"Amendments" with its date, never edited in place.

## Question

Experiment 5 of "Sparks of Weight-Space Programming" had GPT-6 Astra write every weight of a 600-32-32-6 network
in one reply, with no tools. The network averaged 517.4 points at MinAtar Breakout. Can Claude models do the
same? How often do they manage it, and how well?

## Task

- Prompt: `lm_understand-logs/exp5_write_from_scratch/runs/breakout/reply/prompt.txt`, unchanged. sha256
  `766ee251d59a7893ed86d5eaea99ddb847529ab2092afc69f90f55fb0a22e876`.
- System prompt: "Answer the user's request." (the paper's).
- One reply, no tools, output capped at 128,000 tokens.

## Models and runs

- `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5` and `claude-fable-5-2`, all at effort xhigh
  (Astra's setting). 10 runs each, started round robin across models, 4 at a time.
- Optional, only if usage allows after the main batch: 5 runs of Fable 5.2 at effort high and 5 of Opus 5.5 at
  effort max. These are reported as a separate arm.

## How a run is made (`run.py`)

- The command is `claude -p` (Claude Code 2.1.330) with these flags:
  - `--tools ""`
  - `--system-prompt "Answer the user's request."`
  - `--setting-sources ""`
  - `--strict-mcp-config`
  - `--disable-slash-commands`
  - `--no-session-persistence`
  - `--thinking-display summarized`
  - `--effort <effort>`
- The prompt goes on stdin. The working directory is an empty folder outside any git repository.
- Environment: `CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000`. Refusal retries and the fallback model are turned off
  (`CLAUDE_CODE_DISABLE_REFUSAL_RETRY=1`, `CLAUDE_CODE_DISABLE_REFUSAL_FALLBACK=1`).
- **One reply.** When a reply hits the output cap, Claude Code continues it in a new turn on its own. It sends
  "Output token limit hit. Resume directly…", or, if the cap was hit while the model was still thinking, a
  message telling it to reason much more briefly. Claude Code has no setting to turn this off, so `run.py` stops
  the process as soon as that turn starts. The reply up to that point is what gets scored.
- **Known difference from the paper.** Claude Code adds about 650 tokens of its own context to every request:
  - the date, the working folder, the platform and the model's name;
  - a note on handling untrusted files;
  - a note about the account.

  It can't be removed when using a subscription login. It is the same for every model and every run.

## Reading a reply (`score.py`)

- The prompt's rules apply: only the last edits block is read, statements are applied in order, and a
  statement that can't be read is skipped.
- Three cases the rules leave open are settled here, in advance:
  1. A flat list with as many values as the block has entries is reshaped to fit the block.
  2. Exponent notation (`1e-3`) counts as a number.
  3. A reply that ends inside an edits block keeps the statements written before the cut.
- Check: reading the paper's three replies gives its released networks exactly (`score.py --selftest`).

## Score

- MinAtar 1.0.15 Breakout, difficulty ramping on, sticky actions 0.1.
- 1,000 episodes. Episode k is seeded with k (k = 0…999), the same for every network.
- Actions are sampled from softmax(logits). Episodes are cut at 10,000 steps.
- Reported for each network: mean ± standard error.
- Check: Astra's released network scores 502.9 ± 7.8 under this scorer. The paper reports 517.4 ± 7.4.

## Outcomes

| Outcome | Meaning |
|---|---|
| `ok` | The reply ended normally. |
| `cut_off` | The reply hit the 128K output cap. |
| `refused` | A refusal, a safety stop, or an answer from another model. |
| `interrupted` | Claude Code stopped the reply for some other reason. |
| `infra` | No reply at all (usage limit, network or server error). |

- Only `infra` runs are retried, up to 3 times, and they are not counted.
- Every counted run is scored as written. A reply without an edits block is scored as the all-zero network,
  which plays uniformly at random.

## Baselines (measured before any Claude run)

| Baseline | Score |
|---|---|
| All-zero network (uniform random play) | 0.54 ± 0.02 |
| Rule: move the paddle toward the ball's column | 8.37 ± 0.28 |
| PPO, same network, 100M steps (from the paper) | 15.8 |
| PPO, same network, 500M steps (from the paper) | 25.3 |
| Astra's hand-written network (paper / this scorer) | 517.4 / 502.9 |

## Reported

- **Every run:** outcome, score ± SE, output tokens (thinking and text), wall time, and Claude Code's
  API-equivalent cost.
- **Per model:**
  - median and range of scores;
  - how many runs beat PPO at 500M steps (25.3);
  - how many beat the rule (8.37);
  - how many are within 3 SE of Astra's network;
  - outcome counts.
- No run is dropped, or run again, because of its result.

## Amendments

### 1. 2026-11-22, before any Claude reply was scored, after an independent code review

Reading:
- A reply cut off inside an edits block also drops its last, unfinished line, which may stop mid-number.
- A list may start on the line after `=`.
- Numbers must be plain decimals: `0x10` and `1_000` are not read.
- A statement whose result has an absolute value over 1e6 is skipped. This covers repeated `*=`, which could
  otherwise reach inf.

Harness:
- An error message from Claude Code itself (a usage limit or a lost connection) counts as `infra`, not
  `refused`.
- A counted run left without a score is scored when the batch resumes.

No result was known when these were changed.

### 2. 2026-11-23 00:10, after the pilot (Haiku and Fable cut off with no network, Opus 57.2)

- New arm, added after seeing pilot results and reported as such: **Haiku 5.5 at effort high, 10 runs.** The
  128K output cap is already the maximum for every model, so a lower effort is the only way to leave Haiku room
  to write. The xhigh arms are unchanged.
- Tonight's weekly-usage cap is raised from 97% to 100%, since that usage expires at the 05:45 reset.
- The batch was restarted to apply this. The four runs in flight were stopped about 3 minutes in, before any
  output, and moved to `runs/_stopped_by_restart/`. They are not counted; their slots are run again.

### 3. 2026-11-23 08:00, after the main batch

- The optional arm is run as planned: 5 runs of Fable 5.2 at effort high and 5 of Opus 5.5 at effort max.
- The user set both usage caps for this week to 60% (5-hour window and weekly).
- After the weekly reset, Claude Code's weekly reading stayed at 0%. Measured last night, one weekly point is
  about $4.70 of API-equivalent usage, so this arm (at most about $35) is around 7 points and cannot reach the cap
  even if the reading stays wrong.

## Amendment 4 (2026-11-23 09:05), started 11:27 on the user's go
**Status:** started at 09:01 and stopped by the user after about 20 seconds; the two runs in progress were moved to
`runs/_stopped_by_restart/` and are not counted. No run of this amendment exists yet.

Added after seeing the results of every arm above, so these arms are exploratory, not pre-registered.
- **Why:** at effort high, Haiku finished 9 of 10 and Fable 4 of 5, against 0 of 10 each at xhigh. Opus finished
  4 of 10 at xhigh and 0 of 5 at max, and had no runs at high. Sonnet ran only at xhigh.
- **What:** effort high for Fable 5.2 (5 more runs, making 10), Opus 5.5 (10 runs) and Sonnet 5.5 (10 runs).
  Everything else as in the protocol and Amendment 1. Same 60% caps for both usage windows.
- **Expected usage:** about 10 weekly points (about $45 of API-equivalent cost).
- 12:12: the user raised the 5-hour cap to 95% for this batch (the window resets at 12:55). Weekly cap unchanged at 60%.
  The batch was paused with no run in progress, so the restart lost nothing.

## Note (2026-11-23 12:35): arithmetic inside an index
sonnet-high/04 wrote 18 statements like `W1[6*1+3:600:60, 0] = 6`, copying the form of the prompt's own hint
("rows c*6+ch : 600 : 60"). The prompt asks for numbers only, and the reader, unchanged since Amendment 1, skips
these statements as unreadable. The official score stays 0.00 (24 of 42 statements read). As a sensitivity check,
not a rule change: with the arithmetic worked out, all 42 statements read and the network scores 5.76 ± 0.20.
No earlier run wrote arithmetic in an index.

**Amendment 4 finished (2026-11-23 13:53):** all 25 runs scored (2 before the 12:12 restart, 23 after).

**Note (2026-11-23 15:30): arm folders renamed.** At the user's request the xhigh arms are now named like the others:
`runs/breakout/haiku` → `haiku-xhigh`, and the same for sonnet, opus and fable. `run.py` now always labels a run
`<model>-<effort>`. Paths inside score.json, the figure file names, the catch-rate file and the docs were updated to
match. `logs/runs.log` is left as written, so its xhigh lines use the old names (`opus/03` is now `opus-xhigh/03`).
No run, score or reading rule changed; `scores.png` re-renders byte-identical.

## Amendment 5 (2026-11-24), on the user's go
Added after seeing the results of every arm above, so this arm is exploratory, not pre-registered.
- **Why:** max was tried only with Opus (0 of 5 finished). Sonnet is the only other model that ever finished at
  xhigh (6 of 10, two of them within 1.5K tokens of the cap), so it is the only other model where max could show
  anything. Haiku and Fable finished 0 of 10 at xhigh, so they are not run at max.
- **What:** effort max for Sonnet 5.5, 5 runs. Everything else as in the protocol and Amendment 1. Caps: 60% for
  both usage windows, as in Amendment 4.
- **Rule, set before the first run:** if at least one of the 5 runs finishes (writes a network), the arm is extended
  to 10 runs, on the user's go. If none finishes, it stops at 5.
- **Expected:** most or all runs cut off at the cap; about $1.30 API-equivalent each if they run to the cap.

**Amendment 5 finished (2026-11-24 00:53):** 5 of 5 cut off at the cap, no network, each scored 0.54 (random play),
18.8 to 19.1 min each. By the rule above the arm stops at 5. Weekly usage went from 13% to 16%.
Each run logged one `api_retry` about 5K estimated thinking tokens in (error "unknown", retried after 0.6 s); no earlier
run had one. The thinking-token estimate kept counting through it and ended at 73.5K to 75.6K, as Opus at max did
with no retry (72.4K), and each run ended at Claude Code's "Output token limit hit" follow-up. The cut-offs are the
model's, not the retry's, so all five count.

## Amendment 6 (2026-11-24), on the user's go
Added after seeing the results of every arm above, so these arms are exploratory, not pre-registered.
- **Why:** Haiku and Fable did best at high, the lowest effort tried for them (Haiku 9 of 10, median 6.4; Fable 9 of 10,
  median 450). Medium is the next step down, so it tells whether high is their best setting or only the lowest tried.
  Sonnet and Opus already got worse going from xhigh down to high, so they are not run at medium. Low is not run.
- **What:** effort medium for Haiku 5.5 and Fable 5.2, 5 runs each. Everything else as in the protocol and
  Amendment 1. Caps: 60% for both usage windows.
- **Rule, set before the first run:** a model's arm is extended to 10 runs, on the user's go, if its median at medium
  is above its median at high (Haiku 6.37, Fable 449.77). Otherwise it stops at 5.
- **Expected:** Fable about $3.30 and about 1 weekly point per run; Haiku about $0.04 per run.

## Amendment 7 (2026-11-24), on the user's go, while Amendment 6 was running
Added after seeing the results of every arm above, so it is exploratory. One Amendment 6 run had finished
(haiku-medium/03, 7.76); no Fable or Opus medium result was known.
- **Why:** Amendment 6 says Opus got worse from xhigh to high. That holds for its best network (510 → 352) but not for
  its median (0.54 → 55.6). By median, Opus did best at high, the lowest effort tried, as Haiku and Fable did.
  At high it used a median of 52K tokens, so medium still leaves room. Sonnet stays out: it is worse at high on both
  median and best, and used a median of 7.4K tokens there.
- **What:** effort medium for Opus 5.5, 5 runs, run alongside Amendment 6. Everything else as in the protocol and
  Amendment 1. Caps: 60% for both usage windows.
- **Rule, set before the first run:** extended to 10 runs, on the user's go, if its median at medium is above its
  median at high (55.6). Otherwise it stops at 5.
- **Expected:** about $1 API-equivalent per run.
