**Design**

The strategy is to keep the paddle under where the ball is about to be. The input channels are: paddle = ch 0, bricks = ch 2, ball = ch 3, trail = ch 4. The predicted ball column is `t = ball_x + (ball_x − trail_x) = 2·ball_x − trail_x`. This is the ball's next column, since it moves diagonally one cell per step. The signed error is `diff = t − paddle_x`.

**Hidden layer 1** uses two units that are both linear in the one-hot inputs, so they compute `diff` directly.
- Weights: ball cell in column c gets +8c, trail cell in column c gets −4c, and the paddle cell in column c gets −4c. So the pre-activation is 4·diff plus a bias.
- Unit A has bias −2, so it computes tanh(4(diff − 0.5)). It is about +1 when diff ≥ 1 and about −1 when diff ≤ 0.
- Unit B has bias +2, so it computes tanh(4(diff + 0.5)). It is about +1 when diff ≥ 0 and about −1 when diff ≤ −1.

**Hidden layer 2** has two units, h2[0] = tanh(2A) and h2[1] = tanh(2B). This sharpens the signals.

**Output**
- The right logit is 8·h2[0]. It is high only when diff ≥ 1.
- The left logit is −8·h2[1]. It is high only when diff ≤ −1.
- When diff = 0, both move logits are strongly negative, so the no-op (logit 0) wins and the paddle stays put.
- The up, down and fire logits get a bias of −4. They are no-ops anyway, so this just keeps them from diluting the move probabilities.

Aiming at the ball's next column means the paddle ends up either on the ball's old column or on its new column, and both count as a catch. This gives one cell of tolerance against sticky actions.

```edits
# ball channel (3): weight 8*col for every row, to units A (0) and B (1)
W1[9:600:60, 0] = 8
W1[9:600:60, 1] = 8
W1[15:600:60, 0] = 16
W1[15:600:60, 1] = 16
W1[21:600:60, 0] = 24
W1[21:600:60, 1] = 24
W1[27:600:60, 0] = 32
W1[27:600:60, 1] = 32
W1[33:600:60, 0] = 40
W1[33:600:60, 1] = 40
W1[39:600:60, 0] = 48
W1[39:600:60, 1] = 48
W1[45:600:60, 0] = 56
W1[45:600:60, 1] = 56
W1[51:600:60, 0] = 64
W1[51:600:60, 1] = 64
W1[57:600:60, 0] = 72
W1[57:600:60, 1] = 72
# trail channel (4): weight -4*col
W1[10:600:60, 0] = -4
W1[10:600:60, 1] = -4
W1[16:600:60, 0] = -8
W1[16:600:60, 1] = -8
W1[22:600:60, 0] = -12
W1[22:600:60, 1] = -12
W1[28:600:60, 0] = -16
W1[28:600:60, 1] = -16
W1[34:600:60, 0] = -20
W1[34:600:60, 1] = -20
W1[40:600:60, 0] = -24
W1[40:600:60, 1] = -24
W1[46:600:60, 0] = -28
W1[46:600:60, 1] = -28
W1[52:600:60, 0] = -32
W1[52:600:60, 1] = -32
W1[58:600:60, 0] = -36
W1[58:600:60, 1] = -36
# paddle channel (0), row 9: weight -4*col
W1[546, 0] = -4
W1[546, 1] = -4
W1[552, 0] = -8
W1[552, 1] = -8
W1[558, 0] = -12
W1[558, 1] = -12
W1[564, 0] = -16
W1[564, 1] = -16
W1[570, 0] = -20
W1[570, 1] = -20
W1[576, 0] = -24
W1[576, 1] = -24
W1[582, 0] = -28
W1[582, 1] = -28
W1[588, 0] = -32
W1[588, 1] = -32
W1[594, 0] = -36
W1[594, 1] = -36
b1[0] = -2
b1[1] = 2
# layer 2
W2[0, 0] = 2
W2[1, 1] = 2
# outputs: right (3) from A, left (1) from -B, others suppressed
W3[0, 3] = 8
W3[1, 1] = -8
b3[2] = -4
b3[4] = -4
b3[5] = -4
```