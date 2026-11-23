## Design

**Strategy: always move the paddle to the column the ball will occupy next.** The paddle and the ball both move one column per step. So once the paddle is under the ball ("locked"), it can stay locked indefinitely.

**Predicting the next column, linearly.** Normally the next ball column is `2·bx − tx` (ball column bx, trail column tx). After a side-wall bounce the ball has just moved straight down or up, so `bx = tx`, and it will next move away from the wall. Both cases fit one linear function of the one-hot inputs:

- `f(bx) = 2x − [x odd]`
- `g(tx) = −x + [x even]`

This gives `f(bx)+g(tx) = 2bx−tx` for normal motion, 8 for (9,9) and 1 for (0,0).

The decision quantity is `Dn = f(bx) + g(tx) − paddle`, which is also linear in the inputs.

**Special case: just after a paddle hit.** Here the ball and the trail are both in row 8, and the trail cannot tell which way the ball goes next:

- If the paddle is at the ball's column, the hit was a reversal, so the paddle should move toward tx.
- If the paddle is at tx, the hit was a straight reflection, so the paddle should move toward bx.

Both rules are captured by `D8 = f8(bx) + g8(tx) − 2·paddle`, with `f8(x) = g8(x) = x ± 0.5` (+0.5 for even x, −0.5 for odd x). The ±0.5 terms handle the corner bounce at a wall.

**Hidden layer 1** (all units saturated, scale 6):

- u0 = [Dn ≥ 1] (go right)
- u1 = [Dn ≤ −1] (go left)
- u2 = [D8 ≥ 1]
- u3 = [D8 ≤ −1]
- u4 = gate: ball in row 8 AND trail in row 8

**Hidden layer 2** (AND logic):

- R_n = u0 ∧ ¬gate
- L_n = u1 ∧ ¬gate
- R_8 = u2 ∧ gate
- L_8 = u3 ∧ gate

**Output logits:**

- Right is about 30 if R_n or R_8 is on, otherwise about 0.
- Left is about 30 if L_n or L_8 is on, otherwise about 0.
- No-op, up, down and fire are all no-ops in this game, and each gets 15.

The policy is therefore nearly deterministic and keeps the paddle locked on the ball. Sticky actions occasionally break the lock, and wall bounces restore it.

```edits
# ---------- Layer 1 unit 0: Dn - 0.5 > 0  (scale 6) ----------
# ball channel (3), per column: 6*f(c), f = 0,1,4,5,8,9,12,13,16,17
W1[3:600:60, 0] = 0
W1[9:600:60, 0] = 6
W1[15:600:60, 0] = 24
W1[21:600:60, 0] = 30
W1[27:600:60, 0] = 48
W1[33:600:60, 0] = 54
W1[39:600:60, 0] = 72
W1[45:600:60, 0] = 78
W1[51:600:60, 0] = 96
W1[57:600:60, 0] = 102
# trail channel (4): 6*g(c), g = 1,-1,-1,-3,-3,-5,-5,-7,-7,-9
W1[4:600:60, 0] = 6
W1[10:600:60, 0] = -6
W1[16:600:60, 0] = -6
W1[22:600:60, 0] = -18
W1[28:600:60, 0] = -18
W1[34:600:60, 0] = -30
W1[40:600:60, 0] = -30
W1[46:600:60, 0] = -42
W1[52:600:60, 0] = -42
W1[58:600:60, 0] = -54
# paddle (row 9, channel 0): -6*c
W1[540:600:6, 0] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
b1[0] = -3

# ---------- unit 1: -Dn - 0.5 > 0 ----------
W1[3:600:60, 1] = 0
W1[9:600:60, 1] = -6
W1[15:600:60, 1] = -24
W1[21:600:60, 1] = -30
W1[27:600:60, 1] = -48
W1[33:600:60, 1] = -54
W1[39:600:60, 1] = -72
W1[45:600:60, 1] = -78
W1[51:600:60, 1] = -96
W1[57:600:60, 1] = -102
W1[4:600:60, 1] = -6
W1[10:600:60, 1] = 6
W1[16:600:60, 1] = 6
W1[22:600:60, 1] = 18
W1[28:600:60, 1] = 18
W1[34:600:60, 1] = 30
W1[40:600:60, 1] = 30
W1[46:600:60, 1] = 42
W1[52:600:60, 1] = 42
W1[58:600:60, 1] = 54
W1[540:600:6, 1] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
b1[1] = -3

# ---------- unit 2: D8 - 0.5 > 0 ; f8 = g8 = 0.5,0.5,2.5,2.5,4.5,4.5,6.5,6.5,8.5,8.5 (x6) ----------
W1[3:600:60, 2] = 3
W1[9:600:60, 2] = 3
W1[15:600:60, 2] = 15
W1[21:600:60, 2] = 15
W1[27:600:60, 2] = 27
W1[33:600:60, 2] = 27
W1[39:600:60, 2] = 39
W1[45:600:60, 2] = 39
W1[51:600:60, 2] = 51
W1[57:600:60, 2] = 51
W1[4:600:60, 2] = 3
W1[10:600:60, 2] = 3
W1[16:600:60, 2] = 15
W1[22:600:60, 2] = 15
W1[28:600:60, 2] = 27
W1[34:600:60, 2] = 27
W1[40:600:60, 2] = 39
W1[46:600:60, 2] = 39
W1[52:600:60, 2] = 51
W1[58:600:60, 2] = 51
W1[540:600:6, 2] = [0, -12, -24, -36, -48, -60, -72, -84, -96, -108]
b1[2] = -3

# ---------- unit 3: -D8 - 0.5 > 0 ----------
W1[3:600:60, 3] = -3
W1[9:600:60, 3] = -3
W1[15:600:60, 3] = -15
W1[21:600:60, 3] = -15
W1[27:600:60, 3] = -27
W1[33:600:60, 3] = -27
W1[39:600:60, 3] = -39
W1[45:600:60, 3] = -39
W1[51:600:60, 3] = -51
W1[57:600:60, 3] = -51
W1[4:600:60, 3] = -3
W1[10:600:60, 3] = -3
W1[16:600:60, 3] = -15
W1[22:600:60, 3] = -15
W1[28:600:60, 3] = -27
W1[34:600:60, 3] = -27
W1[40:600:60, 3] = -39
W1[46:600:60, 3] = -39
W1[52:600:60, 3] = -51
W1[58:600:60, 3] = -51
W1[540:600:6, 3] = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
b1[3] = -3

# ---------- unit 4: gate = ball in row 8 AND trail in row 8 ----------
W1[483:540:6, 4] = 10
W1[484:540:6, 4] = 10
b1[4] = -15

# ---------- Layer 2: gated AND logic ----------
W2[0, 0] = 6
W2[4, 0] = -6
b2[0] = -9
W2[1, 1] = 6
W2[4, 1] = -6
b2[1] = -9
W2[2, 2] = 6
W2[4, 2] = 6
b2[2] = -9
W2[3, 3] = 6
W2[4, 3] = 6
b2[3] = -9

# ---------- Output ----------
W3[0, 3] = 15
W3[2, 3] = 15
b3[3] = 30
W3[1, 1] = 15
W3[3, 1] = 15
b3[1] = 30
b3[0] = 15
b3[2] = 15
b3[4] = 15
b3[5] = 15
```