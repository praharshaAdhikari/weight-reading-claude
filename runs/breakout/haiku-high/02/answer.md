**Design.** The policy tracks the ball's column with the paddle. Since the ball moves one column per step and the paddle can move one column per step, a paddle that always steps toward the ball's column stays within one cell of it. When the ball reaches row 8, the paddle is then under it or one cell away, which is enough to bounce it. Brick positions and the trail channel are not needed.

**Hidden units.**
- `h1[0] = tanh(2·(ballx − paddlex))`. The ball-channel weights in column c are 2c and the paddle-channel weights at row 9, column c, are −2c. This gives a sharp sign of the horizontal offset. Other hidden units are left at zero.
- `h2[0] = tanh(3·h1[0])`, which is essentially the sign of the offset.
- Logits: `left = −10·h2[0]`, `right = +10·h2[0]`, `no-op = 6` (constant), and up, down and fire stay at 0. When the offset is 0 the no-op logit wins by a wide margin. When the ball is one cell to the right, "right" wins by about 4 logits over no-op.

```edits
# Hidden unit 0 = tanh(2*(ball_x - paddle_x)); ball channel 3 weight 2c in column c,
# paddle channel 0 at row 9 weight -2c in column c.
W1[9:600:60, 0] = 2          # ball, column 1
W1[15:600:60, 0] = 4         # ball, column 2
W1[21:600:60, 0] = 6         # ball, column 3
W1[27:600:60, 0] = 8         # ball, column 4
W1[33:600:60, 0] = 10        # ball, column 5
W1[39:600:60, 0] = 12        # ball, column 6
W1[45:600:60, 0] = 14        # ball, column 7
W1[51:600:60, 0] = 16        # ball, column 8
W1[57:600:60, 0] = 18        # ball, column 9
W1[540:600:6, 0] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]   # paddle, row 9, columns 0..9

# Hidden unit 0 of layer 2 = tanh(3 * h1[0]), essentially sign(ball_x - paddle_x)
W2[0, 0] = 3

# Output: 0 no-op (bias 6), 1 left (-10 * sign), 3 right (+10 * sign)
b3[0] = 6
W3[0, 1] = -10
W3[0, 3] = 10
```