**Design.** The policy tracks the ball. The paddle moves toward the ball's column and stops when they match. The paddle is always within one cell of the ball's column when the ball reaches row 8, so every descending ball is caught, and the episode runs until the 10,000-step cap. Score then comes from bricks broken during those rounds.

**What the hidden units compute.** Each frame contains exactly one ball cell (channel 3) and one paddle cell (row 9, channel 0). With the ball at column `bx` and the paddle at column `px`, the first layer has two units:
- `h1[0] = tanh(4(bx − px) − 2)`, which is about +1 when the ball is right of the paddle and about −1 otherwise.
- `h1[1] = tanh(−4(bx − px) − 2)`, which is about +1 when the ball is left of the paddle and about −1 otherwise.

The second layer passes these through with weight 1. The output logits are `right = 8·h2[0]` and `left = 8·h2[1]`, with the other logits at 0. This gives about 99% right when the ball is right of the paddle, about 99% left when it is left, and no-op (or up/down/fire, which are no-ops) when aligned. The brick, trail, and other channels are unused.

```edits
# h1[0] = tanh(4*(ball_col - paddle_col) - 2): ~+1 when ball is right of paddle
# h1[1] = tanh(-4*(ball_col - paddle_col) - 2): ~+1 when ball is left of paddle
# ball cells: channel 3, column c -> rows c*6+3 + 60k
W1[9:600:60, 0] = 4
W1[15:600:60, 0] = 8
W1[21:600:60, 0] = 12
W1[27:600:60, 0] = 16
W1[33:600:60, 0] = 20
W1[39:600:60, 0] = 24
W1[45:600:60, 0] = 28
W1[51:600:60, 0] = 32
W1[57:600:60, 0] = 36
# paddle cells: row 9, channel 0 -> indices 540 + 6c
W1[540:600:6, 0] = [0, -4, -8, -12, -16, -20, -24, -28, -32, -36]
b1[0] = -2

W1[9:600:60, 1] = -4
W1[15:600:60, 1] = -8
W1[21:600:60, 1] = -12
W1[27:600:60, 1] = -16
W1[33:600:60, 1] = -20
W1[39:600:60, 1] = -24
W1[45:600:60, 1] = -28
W1[51:600:60, 1] = -32
W1[57:600:60, 1] = -36
W1[540:600:6, 1] = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36]
b1[1] = -2

# second layer: pass-through of the two sign units
W2[0, 0] = 1
W2[1, 1] = 1

# output: 1 = left, 3 = right; no-op / up / down / fire stay at 0
W3[1, 1] = 8
W3[0, 3] = 8
```