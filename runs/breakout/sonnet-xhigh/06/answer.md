## Design

The network moves the paddle so that it stays under the ball. It reads the ball's direction from the trail and anticipates wall bounces.

**Geometry.** The ball is caught if, after the paddle's move, the paddle is at the ball's column x or at its landing column x+dx. I use this two-cell window, and I read dx from the trail as x − x_trail. Every quantity below is linear in the one-hot inputs: ball column x, trail column x_t and paddle column p.

**Layer 1 (5 units)**
- u0 ≈ tanh(0.05·S_A), where S_A = 2x − x_t − p = (x+dx) − p. This is the signed distance from the paddle to the ball's next column. Because the gain is small, the unit stays near-linear and passes S_A on to layer 2.
- u1 ≈ tanh(0.05·S_B), where S_B = 3x − x_t − 2p = 2·(x + dx/2 − p). This is the distance to the middle of the catch window, used when the ball is in row 8.
- u2 is an AND of "ball in column 9" and "trail in column 9". That combination means the ball is bouncing off the right wall, so it will next move left.
- u3 is the same test for column 0 and the left wall.
- u4 is +1 if the ball is in row 8 (the landing step), otherwise −1.

**Layer 2 (4 decision units, the rest unused)**
- Wall correction: during a wall bounce the trail gives dx = 0, so S_A is shifted by −1 at the right wall and +1 at the left wall (S_B by ±2). The paddle then starts moving away from the wall one step early.
- Rows 0–7:
  - RA fires if S_A ≥ 1 (move right).
  - LA fires if S_A ≤ −1 (move left).
  - The paddle tracks the ball's next column and stays level with it while it moves.
- Row 8, the landing step:
  - RB fires if S_B ≥ 2.
  - LB fires if S_B ≤ −2.
  - Otherwise the paddle idles when it is already inside the catch window. This keeps the ball's horizontal direction, so the trail stays a valid direction cue.
- The row-8 flag u4 gates the two unit pairs with large weights so only the right pair can fire.

**Output**
- right logit = 10·(RA + RB + 1)
- left logit = 10·(LA + LB + 1)
- no-op logit = 0
- up, down and fire get bias −20.

Right and left are never on together, and both are low when the paddle is already in position. The softmax is therefore nearly deterministic.

```edits
# ---------- layer 1, unit 0: u0 = tanh(0.05*(2*ballx - trailx - padx)) ----------
W1[9:600:60, 0] = 0.1
W1[15:600:60, 0] = 0.2
W1[21:600:60, 0] = 0.3
W1[27:600:60, 0] = 0.4
W1[33:600:60, 0] = 0.5
W1[39:600:60, 0] = 0.6
W1[45:600:60, 0] = 0.7
W1[51:600:60, 0] = 0.8
W1[57:600:60, 0] = 0.9
W1[10:600:60, 0] = -0.05
W1[16:600:60, 0] = -0.1
W1[22:600:60, 0] = -0.15
W1[28:600:60, 0] = -0.2
W1[34:600:60, 0] = -0.25
W1[40:600:60, 0] = -0.3
W1[46:600:60, 0] = -0.35
W1[52:600:60, 0] = -0.4
W1[58:600:60, 0] = -0.45
W1[540:600:6, 0] = [0, -0.05, -0.1, -0.15, -0.2, -0.25, -0.3, -0.35, -0.4, -0.45]
# ---------- layer 1, unit 1: u1 = tanh(0.05*(3*ballx - trailx - 2*padx)) ----------
W1[9:600:60, 1] = 0.15
W1[15:600:60, 1] = 0.3
W1[21:600:60, 1] = 0.45
W1[27:600:60, 1] = 0.6
W1[33:600:60, 1] = 0.75
W1[39:600:60, 1] = 0.9
W1[45:600:60, 1] = 1.05
W1[51:600:60, 1] = 1.2
W1[57:600:60, 1] = 1.35
W1[10:600:60, 1] = -0.05
W1[16:600:60, 1] = -0.1
W1[22:600:60, 1] = -0.15
W1[28:600:60, 1] = -0.2
W1[34:600:60, 1] = -0.25
W1[40:600:60, 1] = -0.3
W1[46:600:60, 1] = -0.35
W1[52:600:60, 1] = -0.4
W1[58:600:60, 1] = -0.45
W1[540:600:6, 1] = [0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6, -0.7, -0.8, -0.9]
# ---------- layer 1, unit 2: right-wall bounce (ball col 9 AND trail col 9) ----------
W1[57:600:60, 2] = 10
W1[58:600:60, 2] = 10
b1[2] = -15
# ---------- layer 1, unit 3: left-wall bounce (ball col 0 AND trail col 0) ----------
W1[3:600:60, 3] = 10
W1[4:600:60, 3] = 10
b1[3] = -15
# ---------- layer 1, unit 4: ball is in row 8 (landing step) ----------
W1[483:540:6, 4] = 10
b1[4] = -5
# ---------- layer 2 ----------
# unit 0: RIGHT when rows 0-7 (S_A >= 1 after wall correction)
W2[0, 0] = 160
W2[2, 0] = -4
W2[3, 0] = 4
W2[4, 0] = -100
b2[0] = -104
# unit 1: LEFT when rows 0-7 (S_A <= -1)
W2[0, 1] = -160
W2[2, 1] = 4
W2[3, 1] = -4
W2[4, 1] = -100
b2[1] = -104
# unit 2: RIGHT in row 8 (S_B >= 2)
W2[1, 2] = 160
W2[2, 2] = -8
W2[3, 2] = 8
W2[4, 2] = 100
b2[2] = -112
# unit 3: LEFT in row 8 (S_B <= -2)
W2[1, 3] = -160
W2[2, 3] = 8
W2[3, 3] = -8
W2[4, 3] = 100
b2[3] = -112
# ---------- output ----------
W3[0, 3] = 10
W3[2, 3] = 10
b3[3] = 10
W3[1, 1] = 10
W3[3, 1] = 10
b3[1] = 10
b3[2] = -20
b3[4] = -20
b3[5] = -20
```