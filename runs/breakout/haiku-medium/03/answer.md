**Design**

The policy is a reactive tracker that aims the paddle at the ball's next column.

- **Target:** Since the ball moves one column per step, its next column is `bx + dx`, where `dx = bx - tx` and `tx` is the trail column. The target is therefore `2*bx - tx`. A paddle at that column catches the ball on its next descent to row 9 (the catch check accepts `pos` equal to `ball_x` or `ball_x + dx`).
- **Error signal:** `D = 2*bx - tx - px` is the offset between target and paddle. Ball and trail columns are encoded with weights `6c` and `-3c`, and paddle columns with `-3p`, all on the one-hot cells, so the pre-activation is linear in `D`.
- **Hidden layer 1:** Unit A = tanh(3(D − 0.5)) and unit B = tanh(3(D + 0.5)). These are two soft thresholds that separate D < 0, D = 0, and D > 0.
- **Hidden layer 2:** Unit 0 = tanh(2(A + B)), a sign-like signal that is about +1 for D ≥ 1, 0 for D = 0, and −1 for D ≤ −1. Unit 1 = tanh(2(B − A)), which is near 1 only when D = 0.
- **Output:** Right logit = 6·h2₀, left logit = −6·h2₀, no-op logit = 5·h2₁. Up, down and fire stay at 0. This gives about 97% no-op when the paddle is centred, and about 98% move toward the target otherwise.

I have not run this, so the score is unverified. I expect a modest score, since it ignores bounce angles and brick geometry.

```edits
# Layer 1, units 0 (A) and 1 (B): pre-activation = 6*bx - 3*tx - 3*px -/+ 1.5
# ball channel 3, column c: weight 6c (all rows)
W1[9:600:60, 0:2] = 6
W1[15:600:60, 0:2] = 12
W1[21:600:60, 0:2] = 18
W1[27:600:60, 0:2] = 24
W1[33:600:60, 0:2] = 30
W1[39:600:60, 0:2] = 36
W1[45:600:60, 0:2] = 42
W1[51:600:60, 0:2] = 48
W1[57:600:60, 0:2] = 54
# trail channel 4, column c: weight -3c (all rows)
W1[10:600:60, 0:2] = -3
W1[16:600:60, 0:2] = -6
W1[22:600:60, 0:2] = -9
W1[28:600:60, 0:2] = -12
W1[34:600:60, 0:2] = -15
W1[40:600:60, 0:2] = -18
W1[46:600:60, 0:2] = -21
W1[52:600:60, 0:2] = -24
W1[58:600:60, 0:2] = -27
# paddle channel 0, row 9, column p: weight -3p
W1[540:600:6, 0] = [0, -3, -6, -9, -12, -15, -18, -21, -24, -27]
W1[540:600:6, 1] = [0, -3, -6, -9, -12, -15, -18, -21, -24, -27]
b1[0] = -1.5
b1[1] = 1.5
# Layer 2: h2_0 = tanh(2(A+B)), h2_1 = tanh(2(B-A))
W2[0:2, 0:2] = [[2, -2], [2, 2]]
# Layer 3: col 0 no-op from h2_1; col 1 left and col 3 right from h2_0
W3[0:2, 0:4] = [[0, -6, 0, 6], [5, 0, 0, 0]]
```