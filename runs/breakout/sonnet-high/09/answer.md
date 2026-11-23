**Design**

The policy keeps the paddle under the ball's column. The ball moves one column per step and the paddle moves one column per step, so a paddle that follows the ball's column stays within one cell of it. When the ball reaches row 8, the paddle ends up on the ball's column and catches it. Wall bounces close any gap left by sticky actions.

**What the units compute.** Let d = ball column − paddle column.
- **Layer 1:** The ball's input weight is 4·column, the same for all 10 rows. The paddle's weight is −4·column, in row 9. This gives a pre-activation of 4d plus a bias.
  - Unit 0 has bias −2, so it is about +1 if d ≥ 1 and about −1 otherwise ("ball right of paddle").
  - Unit 1 has bias +2, so it is about +1 if d ≥ 0 and about −1 otherwise ("ball not left of paddle").
- **Layer 2:** Two units, h2_0 = tanh(2·u0) and h2_1 = tanh(2·u1). They pass the two indicators on, slightly sharpened.
- **Output logits:**
  - right = 5·h2_0
  - left = −5·h2_1
  - no-op = 5·(h2_1 − h2_0), which is large only when d = 0
  - up, down and fire get a bias of −8, so they are essentially never chosen.

The result is that the paddle moves right when the ball is to its right, left when the ball is to its left, and stays still when they are aligned. Each action gets about 0.99 probability or more in its case.

```edits
# ---- layer 1: unit 0 = ball right of paddle (d>=1), unit 1 = ball not left of paddle (d>=0)
# ball channel (3) column c, all 10 rows: weight 4*c
W1[9:600:60, 0] = 4
W1[15:600:60, 0] = 8
W1[21:600:60, 0] = 12
W1[27:600:60, 0] = 16
W1[33:600:60, 0] = 20
W1[39:600:60, 0] = 24
W1[45:600:60, 0] = 28
W1[51:600:60, 0] = 32
W1[57:600:60, 0] = 36
W1[9:600:60, 1] = 4
W1[15:600:60, 1] = 8
W1[21:600:60, 1] = 12
W1[27:600:60, 1] = 16
W1[33:600:60, 1] = 20
W1[39:600:60, 1] = 24
W1[45:600:60, 1] = 28
W1[51:600:60, 1] = 32
W1[57:600:60, 1] = 36
# paddle channel (0) in row 9: weight -4*c
W1[540:600:6, 0] = [0, -4, -8, -12, -16, -20, -24, -28, -32, -36]
W1[540:600:6, 1] = [0, -4, -8, -12, -16, -20, -24, -28, -32, -36]
b1[0] = -2
b1[1] = 2
# ---- layer 2: pass the two indicators through, sharpened
W2[0, 0] = 2
W2[1, 1] = 2
# ---- outputs: 0 noop, 1 left, 3 right
W3[0, 3] = 5
W3[1, 1] = -5
W3[0, 0] = -5
W3[1, 0] = 5
b3[2] = -8
b3[4] = -8
b3[5] = -8
```