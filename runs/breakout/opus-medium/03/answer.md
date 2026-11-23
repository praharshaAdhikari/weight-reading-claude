## Design

**Strategy: anticipatory tracking.** The paddle moves 1 cell per step, the same as the ball's horizontal speed. The policy keeps the paddle, after its move, in the column the ball is about to enter. When the ball comes down to row 8, the paddle is then either under the ball's column or under its next column. Both of those catch it. This also leaves one step of slack if a sticky or sampled action goes wrong.

**Predicting the ball's next column.** I read the next column linearly from the ball and its trail: `next = 2·bx − tx`.
- **Wall correction:** a trail in column 9 gets weight −10 instead of −9, and a trail in column 0 gets +1 instead of 0. So when ball and trail are both at a wall (the bounce step, and also the reset state), the prediction is 8 or 1, which is correct.
- **Only the sign matters,** so the small prediction errors this correction causes elsewhere do not change the action.

**Paddle-bounce case** (ball and trail both in row 8, just after a catch). In this case the ball's next column is "the other one" of {bx, tx}, seen from the paddle. So the paddle moves by the sign of `bx + tx − 2·pos`. This avoids losing the ball after a catch that reverses its direction.

**Layer 1 (5 units):**
- **u0 / u1:** fire when `s_reg = (2bx − tx)_corrected − pos` is ≥ 1 (u0, go right) or ≤ −1 (u1, go left). Pre-activation is `±6·s − 3`.
- **u2 / u3:** fire when `s_b = bx + tx − 2·pos` is ≥ 1 (u2, right) or ≤ −1 (u3, left). Each gets +150 for "ball in row 8" and +150 for "trail in row 8", with bias −303. They can therefore only fire when both are in row 8.
- **u4 (D):** bounce detector, about +1 when ball and trail are both in row 8, otherwise about −1.

**Layer 2 (2 units):**
- **R** = (u0 AND NOT D) OR u2, computed as `tanh(3·u0 − 3·D + 6·u2 + 3)`.
- **L** = (u1 AND NOT D) OR u3, computed the same way.
- The margins are about ±3 in every case of the truth table.

**Output:**
- `right = 6R` and `left = 6L`.
- No-op has logit 0.
- Up, down and fire (which also do nothing) get −6.
- The chosen action has probability of about 99.5%.

## Weights

```edits
# ---- unit 0: right if s_reg>=1 ; unit 1: left if s_reg<=-1 (ball cols weight 12c / -12c)
W1[3:600:60, 0] = 0
W1[9:600:60, 0] = 12
W1[15:600:60, 0] = 24
W1[21:600:60, 0] = 36
W1[27:600:60, 0] = 48
W1[33:600:60, 0] = 60
W1[39:600:60, 0] = 72
W1[45:600:60, 0] = 84
W1[51:600:60, 0] = 96
W1[57:600:60, 0] = 108
W1[9:600:60, 1] = -12
W1[15:600:60, 1] = -24
W1[21:600:60, 1] = -36
W1[27:600:60, 1] = -48
W1[33:600:60, 1] = -60
W1[39:600:60, 1] = -72
W1[45:600:60, 1] = -84
W1[51:600:60, 1] = -96
W1[57:600:60, 1] = -108
# trail: -6c, col0 -> +6, col9 -> -60
W1[4:600:60, 0] = 6
W1[10:600:60, 0] = -6
W1[16:600:60, 0] = -12
W1[22:600:60, 0] = -18
W1[28:600:60, 0] = -24
W1[34:600:60, 0] = -30
W1[40:600:60, 0] = -36
W1[46:600:60, 0] = -42
W1[52:600:60, 0] = -48
W1[58:600:60, 0] = -60
W1[4:600:60, 1] = -6
W1[10:600:60, 1] = 6
W1[16:600:60, 1] = 12
W1[22:600:60, 1] = 18
W1[28:600:60, 1] = 24
W1[34:600:60, 1] = 30
W1[40:600:60, 1] = 36
W1[46:600:60, 1] = 42
W1[52:600:60, 1] = 48
W1[58:600:60, 1] = 60
# paddle (row 9): -6c / +6c
W1[540:600:6, 0] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[540:600:6, 1] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
b1[0] = -3
b1[1] = -3
# ---- unit 2/3: bounce case, s_b = bx + tx - 2pos, scaled by 6
W1[9:600:60, 2] = 6
W1[15:600:60, 2] = 12
W1[21:600:60, 2] = 18
W1[27:600:60, 2] = 24
W1[33:600:60, 2] = 30
W1[39:600:60, 2] = 36
W1[45:600:60, 2] = 42
W1[51:600:60, 2] = 48
W1[57:600:60, 2] = 54
W1[10:600:60, 2] = 6
W1[16:600:60, 2] = 12
W1[22:600:60, 2] = 18
W1[28:600:60, 2] = 24
W1[34:600:60, 2] = 30
W1[40:600:60, 2] = 36
W1[46:600:60, 2] = 42
W1[52:600:60, 2] = 48
W1[58:600:60, 2] = 54
W1[9:600:60, 3] = -6
W1[15:600:60, 3] = -12
W1[21:600:60, 3] = -18
W1[27:600:60, 3] = -24
W1[33:600:60, 3] = -30
W1[39:600:60, 3] = -36
W1[45:600:60, 3] = -42
W1[51:600:60, 3] = -48
W1[57:600:60, 3] = -54
W1[10:600:60, 3] = -6
W1[16:600:60, 3] = -12
W1[22:600:60, 3] = -18
W1[28:600:60, 3] = -24
W1[34:600:60, 3] = -30
W1[40:600:60, 3] = -36
W1[46:600:60, 3] = -42
W1[52:600:60, 3] = -48
W1[58:600:60, 3] = -54
W1[540:600:6, 2] = [0, -12, -24, -36, -48, -60, -72, -84, -96, -108]
W1[540:600:6, 3] = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
# gating: ball in row 8 and trail in row 8
W1[483:540:6, 2] += 150
W1[484:540:6, 2] += 150
W1[483:540:6, 3] += 150
W1[484:540:6, 3] += 150
b1[2] = -303
b1[3] = -303
# ---- unit 4: bounce detector D
W1[483:540:6, 4] = 5
W1[484:540:6, 4] = 5
b1[4] = -7.5
# ---- layer 2: R = (u0 & !D) | u2 ; L = (u1 & !D) | u3
W2[0, 0] = 3
W2[4, 0] = -3
W2[2, 0] = 6
b2[0] = 3
W2[1, 1] = 3
W2[4, 1] = -3
W2[3, 1] = 6
b2[1] = 3
# ---- output
W3[0, 3] = 6
W3[1, 1] = 6
b3[2] = -6
b3[4] = -6
b3[5] = -6
```