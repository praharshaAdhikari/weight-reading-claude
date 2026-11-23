# Hand-built Breakout policy: track the ball's next column

## Strategy

The paddle and the ball both move one column per step. Bricks only flip the ball's vertical direction; its column keeps changing at the same rate. If the paddle stands exactly where the ball will be on the next step, it stays under the ball indefinitely. It catches every descent with one cell of slack, which absorbs most sticky-action and sampling errors.

**Target column.** The target is the ball's next column, T = f(bx) − tx:
- bx is the ball's column and tx is the trail's column.
- f(x) = 2x, except f(0) = 1 and f(9) = 17.
- The corrections at 0 and 9 make T exact at the walls. There the ball lingers one step in the wall column, with trail column equal to ball column.
- T is linear in the one-hot inputs, so one tanh unit can compare it with the paddle column P.

**The catch step.** This target makes the paddle meet the ball at its next column, so most catches reverse the ball horizontally. The trail does not show that reversal. This "just caught" state is recognisable because the ball and trail are both in row 8. In that state the correct move is the sign of (bx + tx − 2P), with ±0.5 wall corrections. This covers both kinds of catch and the wall corners.

## Hidden units

**Layer 1**
- **Unit 0 (go right):** tanh(6·(f(bx) − tx − P − 0.5)).
- **Unit 1 (go left):** the same comparison with the sign flipped, so it fires when T < P.
- **Unit 2 (go right, catch state only):** tanh(6·(Db2 − 0.5) + gate).
  - Db2 = f(bx) + 2tx − 4P, using the same f.
  - Only ball and trail cells in row 8 feed this unit.
  - The gate is a weight of +400 on each of those row-8 cells and a bias of −800. It saturates the unit at −1 unless both the ball and the trail are in row 8.
- **Unit 3 (go left, catch state only):** the same as unit 2 with Db2 negated.

**Layer 2**
- **h2_0 (move right):** tanh(4·(U0 + 3·U2 − 2·U3 + 1)).
  - In normal play units 2 and 3 are both exactly −1, so this reduces to unit 0.
  - In the catch state, units 2 and 3 override unit 0.
- **h2_1 (move left):** the mirror of h2_0, using units 1, 3 and 2.

**Output**
- The right logit is 15·h2_0 and the left logit is 15·h2_1.
- No-op has a logit of 0.
- Up, down and fire have a logit of −15.
- So the policy is nearly deterministic: right if the target is to the right, left if it is to the left, otherwise no-op.

```edits
# ---------- Unit 0: right if f(bx) - tx - P > 0  (K=6) ----------
W1[3:600:60, 0] = 6
W1[9:600:60, 0] = 12
W1[15:600:60, 0] = 24
W1[21:600:60, 0] = 36
W1[27:600:60, 0] = 48
W1[33:600:60, 0] = 60
W1[39:600:60, 0] = 72
W1[45:600:60, 0] = 84
W1[51:600:60, 0] = 96
W1[57:600:60, 0] = 102
W1[4:600:60, 0] = 0
W1[10:600:60, 0] = -6
W1[16:600:60, 0] = -12
W1[22:600:60, 0] = -18
W1[28:600:60, 0] = -24
W1[34:600:60, 0] = -30
W1[40:600:60, 0] = -36
W1[46:600:60, 0] = -42
W1[52:600:60, 0] = -48
W1[58:600:60, 0] = -54
W1[540:600:6, 0] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
b1[0] = -3
# ---------- Unit 1: left if f(bx) - tx - P < 0 ----------
W1[3:600:60, 1] = -6
W1[9:600:60, 1] = -12
W1[15:600:60, 1] = -24
W1[21:600:60, 1] = -36
W1[27:600:60, 1] = -48
W1[33:600:60, 1] = -60
W1[39:600:60, 1] = -72
W1[45:600:60, 1] = -84
W1[51:600:60, 1] = -96
W1[57:600:60, 1] = -102
W1[4:600:60, 1] = 0
W1[10:600:60, 1] = 6
W1[16:600:60, 1] = 12
W1[22:600:60, 1] = 18
W1[28:600:60, 1] = 24
W1[34:600:60, 1] = 30
W1[40:600:60, 1] = 36
W1[46:600:60, 1] = 42
W1[52:600:60, 1] = 48
W1[58:600:60, 1] = 54
W1[540:600:6, 1] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
b1[1] = -3
# ---------- Unit 2: just-caught (ball & trail in row 8), right if f(bx)+2tx-4P > 0 ----------
W1[483:540:6, 2] = [406, 412, 424, 436, 448, 460, 472, 484, 496, 502]
W1[484:540:6, 2] = [400, 412, 424, 436, 448, 460, 472, 484, 496, 508]
W1[540:600:6, 2] = [0, -24, -48, -72, -96, -120, -144, -168, -192, -216]
b1[2] = -803
# ---------- Unit 3: just-caught, left if f(bx)+2tx-4P < 0 ----------
W1[483:540:6, 3] = [394, 388, 376, 364, 352, 340, 328, 316, 304, 298]
W1[484:540:6, 3] = [400, 388, 376, 364, 352, 340, 328, 316, 304, 292]
W1[540:600:6, 3] = [0, 24, 48, 72, 96, 120, 144, 168, 192, 216]
b1[3] = -803
# ---------- Layer 2: combine normal and just-caught cases ----------
W2[0, 0] = 4
W2[2, 0] = 12
W2[3, 0] = -8
b2[0] = 4
W2[1, 1] = 4
W2[3, 1] = 12
W2[2, 1] = -8
b2[1] = 4
# ---------- Output ----------
W3[0, 3] = 15
W3[1, 1] = 15
b3[0] = 0
b3[2] = -15
b3[4] = -15
b3[5] = -15
```