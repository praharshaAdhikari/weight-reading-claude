**Design.** The policy tracks the ball's column and keeps the paddle under it. It does not predict bounces or aim for the paddle edges.

**Hidden units.** Ball cells in channel 3 contribute `4·c` to a unit when the ball is in column `c`, and the paddle cell in row 9 contributes `-4·c` when the paddle is in column `c`. Each unit therefore receives a pre-activation proportional to `4·(ball_col − paddle_col)`, which is linear in the column difference. Each first-layer unit has bias -2:
- **h1[0] ("ball right")** = tanh(4·(ball − paddle) − 2). It is near +1 when the ball is strictly right of the paddle and near -1 otherwise.
- **h1[1] ("ball left")** = tanh(4·(paddle − ball) − 2). It is near +1 when the ball is strictly left of the paddle and near -1 otherwise.

**Second layer.** Units 0 and 1 are scaled copies of h1[0] and h1[1]. All other units are zero and unused.

**Output.** With s = h2[0] + h2[1] and u = h2[0] − h2[1]:
- **right (3)** = 3u, **left (1)** = -3u.
- **no-op (0)** = -2.5·s. This is large only when the ball is exactly under the paddle, so the paddle stays still then.
- **up, down, fire (2, 4, 5)** = 0, so they are effectively no-ops, and they stay at 0 in every case.

**Expected behaviour.** If the ball is off-centre, the paddle moves toward it with probability near 1. If the ball is exactly above the paddle, no-op has probability near 0.97. Sticky actions add some noise but do not change the policy.

```edits
# Hidden layer 1, unit 0 ("ball right of paddle"): pre = 4*(ball_col - paddle_col) - 2
W1[3:600:60, 0] = 0          # ball channel 3, column 0
W1[9:600:60, 0] = 4          # column 1
W1[15:600:60, 0] = 8         # column 2
W1[21:600:60, 0] = 12        # column 3
W1[27:600:60, 0] = 16        # column 4
W1[33:600:60, 0] = 20        # column 5
W1[39:600:60, 0] = 24        # column 6
W1[45:600:60, 0] = 28        # column 7
W1[51:600:60, 0] = 32        # column 8
W1[57:600:60, 0] = 36        # column 9
W1[540:600:6, 0] = [0, -4, -8, -12, -16, -20, -24, -28, -32, -36]   # paddle, row 9, channel 0

# Hidden layer 1, unit 1 ("ball left of paddle"): pre = 4*(paddle_col - ball_col) - 2
W1[3:600:60, 1] = 0          # ball, column 0
W1[9:600:60, 1] = -4         # column 1
W1[15:600:60, 1] = -8        # column 2
W1[21:600:60, 1] = -12       # column 3
W1[27:600:60, 1] = -16       # column 4
W1[33:600:60, 1] = -20       # column 5
W1[39:600:60, 1] = -24       # column 6
W1[45:600:60, 1] = -28       # column 7
W1[51:600:60, 1] = -32       # column 8
W1[57:600:60, 1] = -36       # column 9
W1[540:600:6, 1] = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36]            # paddle, row 9, channel 0

b1[0:2] = -2

# Hidden layer 2: scaled pass-through of units 0 and 1
W2[0, 0] = 2
W2[1, 1] = 2

# Output logits
W3[0, 0] = -2.5    # no-op uses -2.5*(h2[0]+h2[1]); high only when ball is centred
W3[1, 0] = -2.5
W3[0, 1] = -3      # left
W3[1, 1] = 3
W3[0, 3] = 3       # right
W3[1, 3] = -3
b3[0] = 0
```