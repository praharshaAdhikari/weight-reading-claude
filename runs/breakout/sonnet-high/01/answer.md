**Design**

The policy chases the ball horizontally: the paddle moves toward the ball's column and stays still when they line up. The catch test is `pos == ball_x` or `pos == new_x`. Chasing keeps the paddle within one column of the ball, so it usually catches it.

**Hidden units**

- **Layer 1** has two units that both read the signed offset d = ball_col − paddle_col, computed linearly from the one-hot ball channel (3) and paddle channel (0). Each ball cell in column c adds 10c, and the paddle cell in column c subtracts 10c.
  - Unit 0 is tanh(10d − 5), which is about +1 when d ≥ 1 and about −1 otherwise.
  - Unit 1 is tanh(10d + 5), which is about +1 when d ≥ 0 and about −1 otherwise.
- **Layer 2** has two units, each the matching layer-1 unit passed through tanh(2·x) to give about ±0.96. Together they encode three cases: d ≥ 1, d = 0 and d ≤ −1.
- **Outputs** (v1 and v2 are the layer-2 units fed by layer-1 units 0 and 1):
  - Right = 8·v1.
  - Left = −8·v2.
  - No-op = 8·(v2 − v1), which is large only when d = 0.
  - Up, down and fire get a bias of −6 so they are almost never chosen.

Each correct action therefore gets a probability above 0.999.

```edits
# layer 1: units 0 and 1 compute d = ball_col - paddle_col (scaled by 10)
W1[9:600:60, 0:2] = 10
W1[15:600:60, 0:2] = 20
W1[21:600:60, 0:2] = 30
W1[27:600:60, 0:2] = 40
W1[33:600:60, 0:2] = 50
W1[39:600:60, 0:2] = 60
W1[45:600:60, 0:2] = 70
W1[51:600:60, 0:2] = 80
W1[57:600:60, 0:2] = 90
W1[540:600:6, 0:2] = [[0, 0], [-10, -10], [-20, -20], [-30, -30], [-40, -40], [-50, -50], [-60, -60], [-70, -70], [-80, -80], [-90, -90]]
b1[0] = -5
b1[1] = 5
# layer 2: pass-through with gain 2
W2[0, 0] = 2
W2[1, 1] = 2
# outputs: 0 noop, 1 left, 3 right
W3[0, 3] = 8
W3[1, 1] = -8
W3[0, 0] = -8
W3[1, 0] = 8
b3[2] = -6
b3[4] = -6
b3[5] = -6
```