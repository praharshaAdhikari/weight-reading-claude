## Design

**Strategy.** Keep the paddle directly under the ball, one step ahead of it. Each step the policy works out the ball's next column N and moves the paddle toward N. If the paddle is already at N, it does nothing. The ball and the paddle move at the same horizontal speed, so the paddle stays locked under the ball. A catch is then guaranteed with a tolerance of one cell behind and two cells ahead, and any gap that sticky actions or sampling noise opens up closes again at wall bounces.

**Predicting the next column.** Let bx be the ball's column, tx the trail's column and p the paddle's column.
- **Normal case:** N = 2·bx − tx. Wall clamping is built into the linear weights: the ball weight is f(c) = 2c, except f(0) = 1 and f(9) = 17. This gives the exact next column at the walls and on the very first step.
- **Just bounced off the paddle** (ball and trail both in row 8): the observed direction can be wrong, because the bounce may have reversed it. The paddle is at either bx or tx. In this case the right move is the sign of s' = F(bx) + 2·tx − 4p, where F = f. This sends the paddle back toward the other of the two columns, and it also handles the corner cases.

**Hidden units.**
- **Layer 1:**
  - h0 = tanh(5(s − 0.5)), which means s ≥ 1, where s = f(bx) − tx − p.
  - h1 = tanh(5(s + 0.5)), which means s ≥ 0.
  - h2 and h3 are the same two thresholds for s'.
  - h4 = tanh(5(ball in row 8 + trail in row 8 − 1.5)), the "just bounced" gate G.
- **Layer 2** (AND gates):
  - q0 = right and not G.
  - q1 = right′ and G.
  - q2 = left and not G.
  - q3 = left′ and G.
- **Output:**
  - Right logit = 6(q0 + q1 + 1), which is ±6.
  - Left logit = 6(q2 + q3 + 1), which is ±6.
  - No-op logit = 0.
  - Up, down and fire are suppressed with a logit of −10.

The chosen action has probability of about 0.997 per step. The remaining randomness plus sticky actions breaks deterministic loops that never reach a brick.

```edits
# ---------- Layer 1: units 0,1 compute s = f(bx) - tx - p ; units 2,3 compute s' = F(bx) + 2tx - 4p (all x5)
# ball channel 3, column c (all rows): 5*f(c), same for units 0..3
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
W1[3:600:60, 1] = 5
W1[9:600:60, 1] = 10
W1[15:600:60, 1] = 20
W1[21:600:60, 1] = 30
W1[27:600:60, 1] = 40
W1[33:600:60, 1] = 50
W1[39:600:60, 1] = 60
W1[45:600:60, 1] = 70
W1[51:600:60, 1] = 80
W1[57:600:60, 1] = 85
W1[3:600:60, 2] = 5
W1[9:600:60, 2] = 10
W1[15:600:60, 2] = 20
W1[21:600:60, 2] = 30
W1[27:600:60, 2] = 40
W1[33:600:60, 2] = 50
W1[39:600:60, 2] = 60
W1[45:600:60, 2] = 70
W1[51:600:60, 2] = 80
W1[57:600:60, 2] = 85
W1[3:600:60, 3] = 5
W1[9:600:60, 3] = 10
W1[15:600:60, 3] = 20
W1[21:600:60, 3] = 30
W1[27:600:60, 3] = 40
W1[33:600:60, 3] = 50
W1[39:600:60, 3] = 60
W1[45:600:60, 3] = 70
W1[51:600:60, 3] = 80
W1[57:600:60, 3] = 85
# trail channel 4, column c: units 0,1 get -5c ; units 2,3 get +10c
W1[10:600:60, 0] = -5
W1[16:600:60, 0] = -10
W1[22:600:60, 0] = -15
W1[28:600:60, 0] = -20
W1[34:600:60, 0] = -25
W1[40:600:60, 0] = -30
W1[46:600:60, 0] = -35
W1[52:600:60, 0] = -40
W1[58:600:60, 0] = -45
W1[10:600:60, 1] = -5
W1[16:600:60, 1] = -10
W1[22:600:60, 1] = -15
W1[28:600:60, 1] = -20
W1[34:600:60, 1] = -25
W1[40:600:60, 1] = -30
W1[46:600:60, 1] = -35
W1[52:600:60, 1] = -40
W1[58:600:60, 1] = -45
W1[10:600:60, 2] = 10
W1[16:600:60, 2] = 20
W1[22:600:60, 2] = 30
W1[28:600:60, 2] = 40
W1[34:600:60, 2] = 50
W1[40:600:60, 2] = 60
W1[46:600:60, 2] = 70
W1[52:600:60, 2] = 80
W1[58:600:60, 2] = 90
W1[10:600:60, 3] = 10
W1[16:600:60, 3] = 20
W1[22:600:60, 3] = 30
W1[28:600:60, 3] = 40
W1[34:600:60, 3] = 50
W1[40:600:60, 3] = 60
W1[46:600:60, 3] = 70
W1[52:600:60, 3] = 80
W1[58:600:60, 3] = 90
# paddle (channel 0, row 9): units 0,1 get -5c ; units 2,3 get -20c
W1[540:600:6, 0] = [0, -5, -10, -15, -20, -25, -30, -35, -40, -45]
W1[540:600:6, 1] = [0, -5, -10, -15, -20, -25, -30, -35, -40, -45]
W1[540:600:6, 2] = [0, -20, -40, -60, -80, -100, -120, -140, -160, -180]
W1[540:600:6, 3] = [0, -20, -40, -60, -80, -100, -120, -140, -160, -180]
# unit 4: gate G = ball in row 8 AND trail in row 8 (just bounced off paddle)
W1[483:543:6, 4] = 5
W1[484:544:6, 4] = 5
b1[0:5] = [-2.5, 2.5, -2.5, 2.5, -7.5]

# ---------- Layer 2: gated AND units
# q0 = (s>=1) and not G
W2[0, 0] = 4
W2[4, 0] = -4
# q1 = (s'>=1) and G
W2[2, 1] = 4
W2[4, 1] = 4
# q2 = (s<=-1) and not G
W2[1, 2] = -4
W2[4, 2] = -4
# q3 = (s'<=-1) and G
W2[3, 3] = -4
W2[4, 3] = 4
b2[0:4] = -4

# ---------- Output
W3[0, 3] = 6
W3[1, 3] = 6
b3[3] = 6
W3[2, 1] = 6
W3[3, 1] = 6
b3[1] = 6
b3[0] = 0
b3[2] = -10
b3[4] = -10
b3[5] = -10
```