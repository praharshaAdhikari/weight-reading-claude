**Design.** The policy tracks the ball's column with the paddle and ignores the bricks. Let d = ball_x − paddle_x. Two hidden units in the first layer compute tanh(1.5·d) and tanh(−1.5·d). Each is a dot product over the one-hot ball and paddle cells, so the pre-activation is exactly 1.5·(ball column − paddle column). A second layer sharpens these to about ±0.99 when d ≠ 0, and it stays near 0 when d = 0. The output logits are: right = +10·h2₀, left = +10·h2₁, and no-op = 6 (bias). When d > 0 the policy picks "right" with probability near 0.98, when d < 0 it picks "left", and when the paddle is aligned it picks no-op. The remaining 30 hidden units are unused.

```edits
# Layer 1, unit 0: tanh(1.5 * (ball column - paddle column))
# ball channel 3 in grid column c has input index c*6+3 (+60 per row)
W1[3:600:60, 0] = 0
W1[9:600:60, 0] = 1.5
W1[15:600:60, 0] = 3
W1[21:600:60, 0] = 4.5
W1[27:600:60, 0] = 6
W1[33:600:60, 0] = 7.5
W1[39:600:60, 0] = 9
W1[45:600:60, 0] = 10.5
W1[51:600:60, 0] = 12
W1[57:600:60, 0] = 13.5
# paddle channel 0 at row 9, column c has input index 540+6c
W1[546, 0] = -1.5
W1[552, 0] = -3
W1[558, 0] = -4.5
W1[564, 0] = -6
W1[570, 0] = -7.5
W1[576, 0] = -9
W1[582, 0] = -10.5
W1[588, 0] = -12
W1[594, 0] = -13.5
# Layer 1, unit 1: tanh(-1.5 * (ball column - paddle column))
W1[3:600:60, 1] = 0
W1[9:600:60, 1] = -1.5
W1[15:600:60, 1] = -3
W1[21:600:60, 1] = -4.5
W1[27:600:60, 1] = -6
W1[33:600:60, 1] = -7.5
W1[39:600:60, 1] = -9
W1[45:600:60, 1] = -10.5
W1[51:600:60, 1] = -12
W1[57:600:60, 1] = -13.5
W1[546, 1] = 1.5
W1[552, 1] = 3
W1[558, 1] = 4.5
W1[564, 1] = 6
W1[570, 1] = 7.5
W1[576, 1] = 9
W1[582, 1] = 10.5
W1[588, 1] = 12
W1[594, 1] = 13.5
# Layer 2: sharpen both signals
W2[0, 0] = 3
W2[1, 1] = 3
# Output: right (action 3) follows unit 0, left (action 1) follows unit 1, no-op (action 0) has a bias
W3[0, 3] = 10
W3[1, 1] = 10
b3[0] = 6
```