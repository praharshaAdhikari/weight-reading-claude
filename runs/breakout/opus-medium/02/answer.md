**Strategy.** The paddle chases the column the ball will occupy on the next step. I'll call that column T. Under the game rules, the ball is caught if, after the paddle moves, the paddle sits in the ball's current column or its next column. The paddle moves one cell per step and the ball moves one column per step, so chasing T means the gap between them never grows. It shrinks whenever the ball comes toward the paddle or bounces off a wall. This also works from the start position: the paddle has 6 moves to close a gap of 3.

**Computing T exactly.** The paddle moves first in each step, so the next column is the one that matters. Ignoring walls, T = 2·ball_x − trail_x.

The walls need a fix:
- If the ball is in column 9 and the trail is in column 8, the ball will be clipped and stay at 9. The formula gives 10.
- If the ball and trail are both in column 9, the ball has just bounced and is heading to 8. The formula gives 9.

Both cases are correct if the ball's weight in column 9 is 17 instead of 18. By symmetry, the ball's weight in column 0 is 1 instead of 0.

So the ball-channel weight per column is [1, 2, 4, 6, 8, 10, 12, 14, 16, 17], and the trail-channel weight is −column. The trail is never in the same column as the ball except at a wall, so this table covers every case.

**Hidden units.**
- **Layer 1:** Let s = T − paddle_x. Unit 0 computes tanh(4(s − 0.5)), meaning "the target is to the right." Unit 1 computes tanh(4(−s − 0.5)), meaning "the target is to the left." Because s is an integer, both units are always saturated near ±0.96.
- **Layer 2:** Units 0 and 1 copy these signals through tanh(3·h), which pushes them to about ±0.99.
- **Output:** The right logit is 10·h2[0] and the left logit is 10·h2[1]. The no-op logit is 0. Up, down and fire get a bias of −20.
- **Result:** The network moves right when s > 0, moves left when s < 0, and does nothing when s = 0. The softmax picks that action with probability close to 1.

```edits
# unit 0: right detector, s = T - paddle ; unit 1: left detector
# ball channel (3), per column c, all rows
W1[3:600:60, 0] = 4
W1[9:600:60, 0] = 8
W1[15:600:60, 0] = 16
W1[21:600:60, 0] = 24
W1[27:600:60, 0] = 32
W1[33:600:60, 0] = 40
W1[39:600:60, 0] = 48
W1[45:600:60, 0] = 56
W1[51:600:60, 0] = 64
W1[57:600:60, 0] = 68
W1[3:600:60, 1] = -4
W1[9:600:60, 1] = -8
W1[15:600:60, 1] = -16
W1[21:600:60, 1] = -24
W1[27:600:60, 1] = -32
W1[33:600:60, 1] = -40
W1[39:600:60, 1] = -48
W1[45:600:60, 1] = -56
W1[51:600:60, 1] = -64
W1[57:600:60, 1] = -68
# trail channel (4), weight -c
W1[4:600:60, 0] = 0
W1[10:600:60, 0] = -4
W1[16:600:60, 0] = -8
W1[22:600:60, 0] = -12
W1[28:600:60, 0] = -16
W1[34:600:60, 0] = -20
W1[40:600:60, 0] = -24
W1[46:600:60, 0] = -28
W1[52:600:60, 0] = -32
W1[58:600:60, 0] = -36
W1[4:600:60, 1] = 0
W1[10:600:60, 1] = 4
W1[16:600:60, 1] = 8
W1[22:600:60, 1] = 12
W1[28:600:60, 1] = 16
W1[34:600:60, 1] = 20
W1[40:600:60, 1] = 24
W1[46:600:60, 1] = 28
W1[52:600:60, 1] = 32
W1[58:600:60, 1] = 36
# paddle channel (0), row 9, weight -c
W1[540:600:6, 0] = [0, -4, -8, -12, -16, -20, -24, -28, -32, -36]
W1[540:600:6, 1] = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36]
b1[0:2] = -2
# layer 2 pass-through
W2[0, 0] = 3
W2[1, 1] = 3
# outputs
W3[0, 3] = 10
W3[1, 1] = 10
b3[2] = -20
b3[4] = -20
b3[5] = -20
```