**Design**

The strategy is to keep the paddle under the ball's column. The ball and paddle both move one cell per step, so a paddle that always steps toward the ball's column stays within catching range. Wall bounces shrink any gap. When the paddle is directly under the ball it stays still, so the ball lands on it. Tracking only needs the ball's column and the paddle's column. The trail channel is not used.

**Hidden units**

- **Layer 1, unit 0:** `tanh(3·(ball_col − paddle_col) − 1.5)`. The column index is read out as a weighted sum over the ball channel and the paddle channel. This unit is about +1 when the ball is right of the paddle (d ≥ 1) and about −1 otherwise.
- **Layer 1, unit 1:** `tanh(3·(ball_col − paddle_col) + 1.5)`. This unit is about +1 when d ≥ 0 and about −1 when d ≤ −1.
- **Layer 2:** two units that sharpen these, `tanh(2·u0)` and `tanh(2·u1)`.
- **Outputs:**
  - Right ≈ +6·h2₀.
  - Left ≈ −6·h2₁.
  - No-op ≈ 3·(h2₁ − h2₀), which peaks only when d = 0.
  - Up, down and fire get a bias of −5, so they are almost never chosen.

I could not run anything, so the logit values above come from hand arithmetic.

```edits
# Unit 0: tanh(3*(ball_col - paddle_col) - 1.5)
W1[9:600:60, 0] = 3
W1[15:600:60, 0] = 6
W1[21:600:60, 0] = 9
W1[27:600:60, 0] = 12
W1[33:600:60, 0] = 15
W1[39:600:60, 0] = 18
W1[45:600:60, 0] = 21
W1[51:600:60, 0] = 24
W1[57:600:60, 0] = 27
W1[540:600:6, 0] = [0, -3, -6, -9, -12, -15, -18, -21, -24, -27]
b1[0] = -1.5
# Unit 1: tanh(3*(ball_col - paddle_col) + 1.5)
W1[9:600:60, 1] = 3
W1[15:600:60, 1] = 6
W1[21:600:60, 1] = 9
W1[27:600:60, 1] = 12
W1[33:600:60, 1] = 15
W1[39:600:60, 1] = 18
W1[45:600:60, 1] = 21
W1[51:600:60, 1] = 24
W1[57:600:60, 1] = 27
W1[540:600:6, 1] = [0, -3, -6, -9, -12, -15, -18, -21, -24, -27]
b1[1] = 1.5
# Layer 2: sharpen
W2[0, 0] = 2
W2[1, 1] = 2
# Outputs
W3[0, 3] = 6
W3[1, 1] = -6
W3[1, 0] = 3
W3[0, 0] = -3
b3[2] = -5
b3[4] = -5
b3[5] = -5
```