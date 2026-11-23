## Design

**Strategy: track the ball's next column.** The ball's x-coordinate changes by at most 1 per step, and so can the paddle's. Once the paddle is within one cell of the ball, a "move toward the ball's next column" rule keeps it there for the rest of the episode. Walls, bricks and the top don't reverse horizontal motion except at the side walls, so the gap never has to grow.

At the landing step the paddle catches the ball if it ends up at the ball's current column or its next one. Aiming at the ball's next column, `x + dx`, gives a catch window of 4 paddle positions, from `x - dx` to `x + 2dx`. That means one missed step from a sticky action is tolerated. While chasing, the desired action stays the same, so a sticky repeat usually does no harm.

**Target computation (linear in the one-hot inputs):**
- **Lead target** is `2·ballcol − trailcol`, which equals `x + dx`.
- **Side-wall correction:** a ball in column 9 gets weight 17 instead of 18, and a ball in column 0 gets weight 1 instead of 0. This gives the correct next column on the wall-bounce frame, where ball and trail share a column, and also at the start state.
- **Paddle-bounce frame** (ball and trail both in row 8): the trail no longer predicts the next column, because the bounce may have reversed dx. Here I use the midpoint `(ball+trail)/2` instead. It moves the paddle the right way in both bounce cases.

**Layer 1:**
- **Unit 0, A+:** `5·(D_lead − 0.5)`, where `D_lead = lead target − paddle`. It is on when the paddle should go right.
- **Unit 1, A−:** the mirror of A+, on when the paddle should go left.
- **Unit 2, M+:** `10·(D_mid − 0.25)`, where `D_mid = midpoint − paddle`.
- **Unit 3, M−:** the mirror of M+.
- **Unit 4, Z:** an AND unit, "ball in row 8 AND trail in row 8", which detects the paddle-bounce frame.

**Layer 2 (gating):**
- **R1 = A+ AND NOT Z**
- **L1 = A− AND NOT Z**
- **R2 = M+ AND Z**
- **L2 = M− AND Z**

**Output:**
- **Right** = 8·(R1 + R2).
- **Left** = 8·(L1 + L2).
- **No-op** has bias −8, so it wins only when neither direction is on. The margin is always at least 8 logits.
- **Up, down and fire** get bias −40.

```edits
# ---- Layer 1, unit 0: A+ = 5*(2B - T + wallcorr - P - 0.5) ----
W1[3:600:60, 0] = 5
W1[9:600:60, 0] = 10
W1[15:600:60, 0] = 20
W1[21:600:60, 0] = 30
W1[27:600:60, 0] = 40
W1[33:600:60, 0] = 50
W1[39:600:60, 0] = 60
W1[45:600:60, 0] = 70
W1[51:600:60, 0] = 80
W1[57:600:60, 0] = 85
W1[4:600:60, 0] = 0
W1[10:600:60, 0] = -5
W1[16:600:60, 0] = -10
W1[22:600:60, 0] = -15
W1[28:600:60, 0] = -20
W1[34:600:60, 0] = -25
W1[40:600:60, 0] = -30
W1[46:600:60, 0] = -35
W1[52:600:60, 0] = -40
W1[58:600:60, 0] = -45
W1[540:600:6, 0] = [0, -5, -10, -15, -20, -25, -30, -35, -40, -45]
b1[0] = -2.5
# ---- unit 1: A- (negated) ----
W1[3:600:60, 1] = -5
W1[9:600:60, 1] = -10
W1[15:600:60, 1] = -20
W1[21:600:60, 1] = -30
W1[27:600:60, 1] = -40
W1[33:600:60, 1] = -50
W1[39:600:60, 1] = -60
W1[45:600:60, 1] = -70
W1[51:600:60, 1] = -80
W1[57:600:60, 1] = -85
W1[4:600:60, 1] = 0
W1[10:600:60, 1] = 5
W1[16:600:60, 1] = 10
W1[22:600:60, 1] = 15
W1[28:600:60, 1] = 20
W1[34:600:60, 1] = 25
W1[40:600:60, 1] = 30
W1[46:600:60, 1] = 35
W1[52:600:60, 1] = 40
W1[58:600:60, 1] = 45
W1[540:600:6, 1] = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
b1[1] = -2.5
# ---- unit 2: M+ = 10*((B+T)/2 - P - 0.25) ----
W1[3:600:60, 2] = 0
W1[9:600:60, 2] = 5
W1[15:600:60, 2] = 10
W1[21:600:60, 2] = 15
W1[27:600:60, 2] = 20
W1[33:600:60, 2] = 25
W1[39:600:60, 2] = 30
W1[45:600:60, 2] = 35
W1[51:600:60, 2] = 40
W1[57:600:60, 2] = 45
W1[4:600:60, 2] = 0
W1[10:600:60, 2] = 5
W1[16:600:60, 2] = 10
W1[22:600:60, 2] = 15
W1[28:600:60, 2] = 20
W1[34:600:60, 2] = 25
W1[40:600:60, 2] = 30
W1[46:600:60, 2] = 35
W1[52:600:60, 2] = 40
W1[58:600:60, 2] = 45
W1[540:600:6, 2] = [0, -10, -20, -30, -40, -50, -60, -70, -80, -90]
b1[2] = -2.5
# ---- unit 3: M- ----
W1[3:600:60, 3] = 0
W1[9:600:60, 3] = -5
W1[15:600:60, 3] = -10
W1[21:600:60, 3] = -15
W1[27:600:60, 3] = -20
W1[33:600:60, 3] = -25
W1[39:600:60, 3] = -30
W1[45:600:60, 3] = -35
W1[51:600:60, 3] = -40
W1[57:600:60, 3] = -45
W1[4:600:60, 3] = 0
W1[10:600:60, 3] = -5
W1[16:600:60, 3] = -10
W1[22:600:60, 3] = -15
W1[28:600:60, 3] = -20
W1[34:600:60, 3] = -25
W1[40:600:60, 3] = -30
W1[46:600:60, 3] = -35
W1[52:600:60, 3] = -40
W1[58:600:60, 3] = -45
W1[540:600:6, 3] = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
b1[3] = -2.5
# ---- unit 4: Z = ball in row 8 AND trail in row 8 ----
W1[483:540:6, 4] = 5
W1[484:540:6, 4] = 5
b1[4] = -7.5
# ---- Layer 2: gating ----
W2[0, 0] = 3
W2[4, 0] = -3
b2[0] = -3
W2[1, 1] = 3
W2[4, 1] = -3
b2[1] = -3
W2[2, 2] = 3
W2[4, 2] = 3
b2[2] = -3
W2[3, 3] = 3
W2[4, 3] = 3
b2[3] = -3
# ---- Output ----
W3[0, 3] = 8
W3[2, 3] = 8
W3[1, 1] = 8
W3[3, 1] = 8
b3[0] = -8
b3[2] = -40
b3[4] = -40
b3[5] = -40
```