**Design.** The policy is a hand-set tracker with a small lead. The paddle moves toward a target column `bx + 2*(bx - tx)`, where `bx` is the ball's column and `tx` is the trail's column. The trail gives the ball's horizontal direction, so the paddle leads the ball slightly in the direction it travels. Brick channels are ignored.

**Hidden units.** Each unit has at most one active ball cell, one trail cell and one paddle cell, so its pre-activation is a per-cell weight sum:

- **Unit 0 ("needs right")** has pre-activation `4*(3bx - px - 2tx) - 2`. It is near +1 when the paddle is at least one column left of the target and near -1 otherwise.
- **Unit 1 ("needs left")** has pre-activation `4*(px - 3bx + 2tx) - 2`. It is near +1 when the paddle is at least one column right of the target and near -1 otherwise.
- The other 30 hidden units are zero.

**Second layer.** `h2 = tanh(3*h1)` on units 0 and 1 sharpens these into near-sign signals.

**Output.** `logit_left = 2*(B - A)` and `logit_right = 2*(A - B)`, where A and B are the sharpened unit 0 and unit 1 outputs. The no-op logit is 1, and up/down/fire get the same bias, so they behave like no-op. When the paddle is on target, both A and B are near -1, so no-op wins.

```edits
# Hidden layer 1, unit 0 ("needs right"): pre = 12*bx - 4*px - 8*tx - 2
# Ball cell (channel 3) in column c: weight 12c
W1[9:600:60, 0] = [12,12,12,12,12,12,12,12,12,12]
W1[15:600:60, 0] = [24,24,24,24,24,24,24,24,24,24]
W1[21:600:60, 0] = [36,36,36,36,36,36,36,36,36,36]
W1[27:600:60, 0] = [48,48,48,48,48,48,48,48,48,48]
W1[33:600:60, 0] = [60,60,60,60,60,60,60,60,60,60]
W1[39:600:60, 0] = [72,72,72,72,72,72,72,72,72,72]
W1[45:600:60, 0] = [84,84,84,84,84,84,84,84,84,84]
W1[51:600:60, 0] = [96,96,96,96,96,96,96,96,96,96]
W1[57:600:60, 0] = [108,108,108,108,108,108,108,108,108,108]
# Trail cell (channel 4) in column c: weight -8c
W1[10:600:60, 0] = [-8,-8,-8,-8,-8,-8,-8,-8,-8,-8]
W1[16:600:60, 0] = [-16,-16,-16,-16,-16,-16,-16,-16,-16,-16]
W1[22:600:60, 0] = [-24,-24,-24,-24,-24,-24,-24,-24,-24,-24]
W1[28:600:60, 0] = [-32,-32,-32,-32,-32,-32,-32,-32,-32,-32]
W1[34:600:60, 0] = [-40,-40,-40,-40,-40,-40,-40,-40,-40,-40]
W1[40:600:60, 0] = [-48,-48,-48,-48,-48,-48,-48,-48,-48,-48]
W1[46:600:60, 0] = [-56,-56,-56,-56,-56,-56,-56,-56,-56,-56]
W1[52:600:60, 0] = [-64,-64,-64,-64,-64,-64,-64,-64,-64,-64]
W1[58:600:60, 0] = [-72,-72,-72,-72,-72,-72,-72,-72,-72,-72]
# Paddle cell (row 9, channel 0) in column c: weight -4c
W1[540:600:6, 0] = [0,-4,-8,-12,-16,-20,-24,-28,-32,-36]

# Hidden layer 1, unit 1 ("needs left"): pre = 4*px - 12*bx + 8*tx - 2
# Ball cell (channel 3) in column c: weight -12c
W1[9:600:60, 1] = [-12,-12,-12,-12,-12,-12,-12,-12,-12,-12]
W1[15:600:60, 1] = [-24,-24,-24,-24,-24,-24,-24,-24,-24,-24]
W1[21:600:60, 1] = [-36,-36,-36,-36,-36,-36,-36,-36,-36,-36]
W1[27:600:60, 1] = [-48,-48,-48,-48,-48,-48,-48,-48,-48,-48]
W1[33:600:60, 1] = [-60,-60,-60,-60,-60,-60,-60,-60,-60,-60]
W1[39:600:60, 1] = [-72,-72,-72,-72,-72,-72,-72,-72,-72,-72]
W1[45:600:60, 1] = [-84,-84,-84,-84,-84,-84,-84,-84,-84,-84]
W1[51:600:60, 1] = [-96,-96,-96,-96,-96,-96,-96,-96,-96,-96]
W1[57:600:60, 1] = [-108,-108,-108,-108,-108,-108,-108,-108,-108,-108]
# Trail cell (channel 4) in column c: weight +8c
W1[10:600:60, 1] = [8,8,8,8,8,8,8,8,8,8]
W1[16:600:60, 1] = [16,16,16,16,16,16,16,16,16,16]
W1[22:600:60, 1] = [24,24,24,24,24,24,24,24,24,24]
W1[28:600:60, 1] = [32,32,32,32,32,32,32,32,32,32]
W1[34:600:60, 1] = [40,40,40,40,40,40,40,40,40,40]
W1[40:600:60, 1] = [48,48,48,48,48,48,48,48,48,48]
W1[46:600:60, 1] = [56,56,56,56,56,56,56,56,56,56]
W1[52:600:60, 1] = [64,64,64,64,64,64,64,64,64,64]
W1[58:600:60, 1] = [72,72,72,72,72,72,72,72,72,72]
# Paddle cell (row 9, channel 0) in column c: weight +4c
W1[540:600:6, 1] = [0,4,8,12,16,20,24,28,32,36]

# Hidden layer 1 bias for units 0 and 1
b1[0:2] = -2

# Hidden layer 2: pass-through with gain 3 for units 0 and 1
W2[0, 0] = 3
W2[1, 1] = 3

# Output: left/right from the difference of the two sharpened units; no-op-like actions get bias 1
W3[0, 1] = -2
W3[1, 1] = 2
W3[0, 3] = 2
W3[1, 3] = -2
b3[0] = 1
b3[2] = 1
b3[4] = 1
b3[5] = 1
```