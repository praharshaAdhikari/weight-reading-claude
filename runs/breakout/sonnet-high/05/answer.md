**Design**

The ball always moves diagonally, and the paddle catches it whenever it ends its move on the ball's current column or the one the ball is about to enter. So the policy is to chase a point just ahead of the ball.

- **Inputs used:** paddle (channel 0), ball (channel 3) and trail (channel 4). Each is one-hot, so a weight of "column number" on every cell reads out that object's x position. The ball's x velocity is vx = ball_x − trail_x.
- **Chase signal:** e = (ball_x − paddle_x) + vx = 2·ball_x − trail_x − paddle_x. This is linear in the inputs, so layer 1 computes it directly.
- **Rule from e:** e ≥ 1 means move right, e ≤ −1 means move left, and e = 0 means no-op. A paddle exactly on the ball's column but a step behind a moving ball still gets e ≥ 1 and keeps moving. If the paddle is already one column ahead of a moving ball, e = 0 and it waits.
- **Layer 1:**
  - Unit 0 is tanh(3(e − 0.5)), which is about +0.9 when e ≥ 1 and −0.9 otherwise.
  - Unit 1 is tanh(3(−e − 0.5)), which is about +0.9 when e ≤ −1 and −0.9 otherwise.
  - The other 30 units are unused.
- **Layer 2:** units 0 and 1 pass the signals through with gain 2 for a sharper saturation.
- **Outputs:**
  - The right logit (action 3) is 6 × unit 0.
  - The left logit (action 1) is 6 × unit 1.
  - The no-op logit is 0.
  - Up, down and fire get a bias of −6 so they don't dilute the choice.
  - When aligned, the no-op wins with probability about 0.98. When the paddle is off, the correct move wins with probability about 0.99.

```edits
b1[0] = -1.5
b1[1] = -1.5
# column 1
W1[9:600:60, 0] = 6
W1[10:600:60, 0] = -3
W1[6:600:60, 0] = -3
W1[9:600:60, 1] = -6
W1[10:600:60, 1] = 3
W1[6:600:60, 1] = 3
# column 2
W1[15:600:60, 0] = 12
W1[16:600:60, 0] = -6
W1[12:600:60, 0] = -6
W1[15:600:60, 1] = -12
W1[16:600:60, 1] = 6
W1[12:600:60, 1] = 6
# column 3
W1[21:600:60, 0] = 18
W1[22:600:60, 0] = -9
W1[18:600:60, 0] = -9
W1[21:600:60, 1] = -18
W1[22:600:60, 1] = 9
W1[18:600:60, 1] = 9
# column 4
W1[27:600:60, 0] = 24
W1[28:600:60, 0] = -12
W1[24:600:60, 0] = -12
W1[27:600:60, 1] = -24
W1[28:600:60, 1] = 12
W1[24:600:60, 1] = 12
# column 5
W1[33:600:60, 0] = 30
W1[34:600:60, 0] = -15
W1[30:600:60, 0] = -15
W1[33:600:60, 1] = -30
W1[34:600:60, 1] = 15
W1[30:600:60, 1] = 15
# column 6
W1[39:600:60, 0] = 36
W1[40:600:60, 0] = -18
W1[36:600:60, 0] = -18
W1[39:600:60, 1] = -36
W1[40:600:60, 1] = 18
W1[36:600:60, 1] = 18
# column 7
W1[45:600:60, 0] = 42
W1[46:600:60, 0] = -21
W1[42:600:60, 0] = -21
W1[45:600:60, 1] = -42
W1[46:600:60, 1] = 21
W1[42:600:60, 1] = 21
# column 8
W1[51:600:60, 0] = 48
W1[52:600:60, 0] = -24
W1[48:600:60, 0] = -24
W1[51:600:60, 1] = -48
W1[52:600:60, 1] = 24
W1[48:600:60, 1] = 24
# column 9
W1[57:600:60, 0] = 54
W1[58:600:60, 0] = -27
W1[54:600:60, 0] = -27
W1[57:600:60, 1] = -54
W1[58:600:60, 1] = 27
W1[54:600:60, 1] = 27
# layer 2 pass-through
W2[0, 0] = 2
W2[1, 1] = 2
# outputs
W3[0, 3] = 6
W3[1, 1] = 6
b3[2] = -6
b3[4] = -6
b3[5] = -6
```