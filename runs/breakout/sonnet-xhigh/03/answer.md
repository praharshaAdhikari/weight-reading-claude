## Design

The paddle should go straight to where the ball will land, not just follow the ball's x. Chasing the ball keeps the paddle one cell behind it, and a single sticky-action slip leaves it two cells behind until the next wall bounce.

**Prediction.** The ball's horizontal motion is independent of bricks, because it only reflects off the side walls, with a one-step pause at each wall. Unfolding that motion gives a landing column `L = fold(u)`. Here `u = x ± n`, where `n` is the number of steps until the ball is on row 8. `fold(u)` is `min(u, 19-u)` for a right-moving ball and `max(u, -1-u)` for a left-moving one.
- **Down-moving ball:** `n = 8 - y`.
- **Up-moving ball:** `n = y + 1`, assuming it reflects off the brick wall at row 4.

The ball's direction comes from the ball and trail cells. The paddle then moves right if `p < L`, left if `p > L`, and stays put if `p = L`. Catching at `L` always lands inside the paddle's catch zone.

**Hidden layer 1 (20 of 32 units used).**
- **Units 0–15** are threshold detectors, each tanh-saturated to ±1. They test whether one of four linear forms is at least a threshold. The forms are `A−p`, `A+p`, `B−p` and `B+p`, with `A = bx−by` and `B = bx+by`. Each form has 4 thresholds, and they are the half-planes that encode `p < L` and `p > L` for each direction class.
- **Units 16–19** are direction-class gates: right-down, left-down, right-up and left-up. Each computes `dx + [bx=0]` and `dy + [by=0]` (or the up/left equivalents) from the ball and trail cells. It is on only when both equal 1, which also handles wall-pause steps.

**Hidden layer 2 (8 units).** One unit per class and action. Each is an AND or OR of its class gate and two threshold units. In the right-moving classes, "right" is an AND and "left" is an OR. In the left-moving classes it is the reverse.

**Output.**
- Right logit = 20 if any right unit is on, else 0.
- Left logit follows the same rule.
- No-op logit = 10.
- Up, down and fire are pushed down to −20.

On steps where no class is active (initial step, brick-bounce steps), the network just no-ops.

```edits
# ================= LAYER 1 =================
# --- ball (channel 3) weights: column part, same for all 20 units
W1[9:600:60, 0:20] = 6
W1[15:600:60, 0:20] = 12
W1[21:600:60, 0:20] = 18
W1[27:600:60, 0:20] = 24
W1[33:600:60, 0:20] = 30
W1[39:600:60, 0:20] = 36
W1[45:600:60, 0:20] = 42
W1[51:600:60, 0:20] = 48
W1[57:600:60, 0:20] = 54
# --- ball row part: units 0-7,18,19 get -6r ; units 8-17 get +6r
W1[63:120:6, 0:20] -= 6
W1[63:120:6, 8:18] += 12
W1[123:180:6, 0:20] -= 12
W1[123:180:6, 8:18] += 24
W1[183:240:6, 0:20] -= 18
W1[183:240:6, 8:18] += 36
W1[243:300:6, 0:20] -= 24
W1[243:300:6, 8:18] += 48
W1[303:360:6, 0:20] -= 30
W1[303:360:6, 8:18] += 60
W1[363:420:6, 0:20] -= 36
W1[363:420:6, 8:18] += 72
W1[423:480:6, 0:20] -= 42
W1[423:480:6, 8:18] += 84
W1[483:540:6, 0:20] -= 48
W1[483:540:6, 8:18] += 96
W1[543:600:6, 0:20] -= 54
W1[543:600:6, 8:18] += 108
# --- gate adjustments (units 17,19 need -6c ; wall / edge indicators)
W1[9:600:60, 17:20:2] -= 12
W1[15:600:60, 17:20:2] -= 24
W1[21:600:60, 17:20:2] -= 36
W1[27:600:60, 17:20:2] -= 48
W1[33:600:60, 17:20:2] -= 60
W1[39:600:60, 17:20:2] -= 72
W1[45:600:60, 17:20:2] -= 84
W1[51:600:60, 17:20:2] -= 96
W1[57:600:60, 17:20:2] -= 108
W1[57:600:60, 17:20:2] += 6
W1[3:60:6, 16:18] += 6
W1[3:600:60, 16:20:2] += 6
W1[483:540:6, 18:20] += 6
# --- paddle (channel 0, row 9) weights: -6x for A-p / B-p forms, +6x for A+p / B+p forms
W1[540:600:6, 0] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[540:600:6, 1] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[540:600:6, 2] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[540:600:6, 3] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[540:600:6, 8] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[540:600:6, 9] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[540:600:6, 10] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[540:600:6, 11] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[540:600:6, 4] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 5] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 6] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 7] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 12] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 13] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 14] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 15] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
# --- trail (channel 4) weights for gate units 16..19: column part
W1[10:600:60, 16:20:2] = -6
W1[10:600:60, 17:20:2] = 6
W1[16:600:60, 16:20:2] = -12
W1[16:600:60, 17:20:2] = 12
W1[22:600:60, 16:20:2] = -18
W1[22:600:60, 17:20:2] = 18
W1[28:600:60, 16:20:2] = -24
W1[28:600:60, 17:20:2] = 24
W1[34:600:60, 16:20:2] = -30
W1[34:600:60, 17:20:2] = 30
W1[40:600:60, 16:20:2] = -36
W1[40:600:60, 17:20:2] = 36
W1[46:600:60, 16:20:2] = -42
W1[46:600:60, 17:20:2] = 42
W1[52:600:60, 16:20:2] = -48
W1[52:600:60, 17:20:2] = 48
W1[58:600:60, 16:20:2] = -54
W1[58:600:60, 17:20:2] = 54
# --- trail row part: units 16,17 get -6r ; units 18,19 get +6r
W1[64:120:6, 16:18] -= 6
W1[64:120:6, 18:20] += 6
W1[124:180:6, 16:18] -= 12
W1[124:180:6, 18:20] += 12
W1[184:240:6, 16:18] -= 18
W1[184:240:6, 18:20] += 18
W1[244:300:6, 16:18] -= 24
W1[244:300:6, 18:20] += 24
W1[304:360:6, 16:18] -= 30
W1[304:360:6, 18:20] += 30
W1[364:420:6, 16:18] -= 36
W1[364:420:6, 18:20] += 36
W1[424:480:6, 16:18] -= 42
W1[424:480:6, 18:20] += 42
W1[484:540:6, 16:18] -= 48
W1[484:540:6, 18:20] += 48
W1[544:600:6, 16:18] -= 54
W1[544:600:6, 18:20] += 54
# --- layer-1 biases: threshold units then gates
b1[0:20] = [45, 51, -9, -3, -63, -69, 3, -3, -51, -45, 3, 9, -39, -45, -105, -111, -9, -9, -9, -9]

# ================= LAYER 2 =================
# h0: class RD -> right (AND)
W2[16, 0] = 4
W2[0, 0] = 4
W2[4, 0] = -4
b2[0] = -8
# h1: class RD -> left (OR)
W2[16, 1] = 4
W2[1, 1] = -4
W2[5, 1] = 4
# h2: class LD -> right (OR)
W2[17, 2] = 4
W2[8, 2] = 4
W2[12, 2] = -4
# h3: class LD -> left (AND)
W2[17, 3] = 4
W2[9, 3] = -4
W2[13, 3] = 4
b2[3] = -8
# h4: class RU -> right (AND)
W2[18, 4] = 4
W2[10, 4] = 4
W2[14, 4] = -4
b2[4] = -8
# h5: class RU -> left (OR)
W2[18, 5] = 4
W2[11, 5] = -4
W2[15, 5] = 4
# h6: class LU -> right (OR)
W2[19, 6] = 4
W2[2, 6] = 4
W2[6, 6] = -4
# h7: class LU -> left (AND)
W2[19, 7] = 4
W2[3, 7] = -4
W2[7, 7] = 4
b2[7] = -8

# ================= OUTPUT =================
# right action (3) from h0,h2,h4,h6 ; left action (1) from h1,h3,h5,h7
W3[0, 3] = 10
W3[2, 3] = 10
W3[4, 3] = 10
W3[6, 3] = 10
W3[1, 1] = 10
W3[3, 1] = 10
W3[5, 1] = 10
W3[7, 1] = 10
b3[0] = 10
b3[1] = 40
b3[3] = 40
b3[2] = -20
b3[4] = -20
b3[5] = -20
```