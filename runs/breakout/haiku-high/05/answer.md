## Design

**Strategy:** a paddle tracker. The ball's next column is `ball_x + dx`, where `dx = ball_x - trail_x` is the ball's current horizontal direction. The paddle moves toward that column and stays there. This keeps it under the ball when it reaches row 8, which is the only row where a paddle hit is possible.

**Hidden units:**
- Layer 1, unit 0 computes `tanh(8(e + 0.5))` and unit 1 computes `tanh(8(e - 0.5))`, where `e = (2·ball_x - trail_x) - paddle_x` is the signed offset from the target column. Both are linear in the one-hot inputs: ball column c gets weight 16c, trail column c gets -8c, and paddle column c gets -8c. Together they give a sharp three-way signal: `e ≥ 1` gives (+1, +1), `e = 0` gives (+1, -1), and `e ≤ -1` gives (-1, -1).
- Layer 2, unit 0 is `tanh(3(a+b))`, which is about +1 when the paddle should move right, 0 when it is aligned, and -1 when it should move left. Unit 1 is `tanh(3(a-b))`, which is about 1 only when aligned.
- Output: right is `+6·H0`, left is `-6·H0`, and no-op is `20·H1`. Up, down and fire get bias -10 so they are effectively never sampled. Up, down and fire do nothing anyway.

```edits
# Layer 1 unit 0: pre = 8*(e+0.5); unit 1: pre = 8*(e-0.5)
# e = (2*ball_x - trail_x) - paddle_x  (target = ball_x + dx, dx = ball_x - trail_x)
# ball (channel 3) column c: weight 16c ; trail (channel 4) column c: weight -8c ; paddle (row 9, channel 0) column c: weight -8c
W1[9:600:60, 0] = 16
W1[15:600:60, 0] = 32
W1[21:600:60, 0] = 48
W1[27:600:60, 0] = 64
W1[33:600:60, 0] = 80
W1[39:600:60, 0] = 96
W1[45:600:60, 0] = 112
W1[51:600:60, 0] = 128
W1[57:600:60, 0] = 144
W1[10:600:60, 0] = -8
W1[16:600:60, 0] = -16
W1[22:600:60, 0] = -24
W1[28:600:60, 0] = -32
W1[34:600:60, 0] = -40
W1[40:600:60, 0] = -48
W1[46:600:60, 0] = -56
W1[52:600:60, 0] = -64
W1[58:600:60, 0] = -72
W1[9:600:60, 1] = 16
W1[15:600:60, 1] = 32
W1[21:600:60, 1] = 48
W1[27:600:60, 1] = 64
W1[33:600:60, 1] = 80
W1[39:600:60, 1] = 96
W1[45:600:60, 1] = 112
W1[51:600:60, 1] = 128
W1[57:600:60, 1] = 144
W1[10:600:60, 1] = -8
W1[16:600:60, 1] = -16
W1[22:600:60, 1] = -24
W1[28:600:60, 1] = -32
W1[34:600:60, 1] = -40
W1[40:600:60, 1] = -48
W1[46:600:60, 1] = -56
W1[52:600:60, 1] = -64
W1[58:600:60, 1] = -72
W1[540:600:6, 0] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 1] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
b1[0] = 4
b1[1] = -4

# Layer 2: unit 0 = tanh(3(a+b)) (sign of e), unit 1 = tanh(3(a-b)) (is e == 0)
W2[0, 0] = 3
W2[1, 0] = 3
W2[0, 1] = 3
W2[1, 1] = -3

# Output: left = -6*unit0, right = +6*unit0, no-op = 20*unit1; up/down/fire suppressed
W3[0, 1] = -6
W3[0, 3] = 6
W3[1, 0] = 20
b3[2] = -10
b3[4] = -10
b3[5] = -10
```