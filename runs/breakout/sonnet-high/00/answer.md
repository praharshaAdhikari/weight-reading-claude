**Design**

The policy tracks the ball's column with the paddle. The paddle moves 1 cell per step, the same as the ball's horizontal speed, and the game catches the ball if the paddle is at the ball's column or its next column. Matching columns is therefore enough to catch it nearly every time. Let d = ball_column − paddle_column.

- **Hidden unit 0 ("ball is to the right")** has pre-activation 4·d − 2. Each ball-channel cell in column c has weight 4c, and each paddle cell in column c has weight −4c. The bias is −2. The unit is about +1 when d ≥ 1 and about −1 when d ≤ 0.
- **Hidden unit 1 ("ball is to the left")** is the mirror image, with pre-activation −4·d − 2. It is about +1 when d ≤ −1 and about −1 otherwise.
- **Layer 2** has two pass-through units that multiply by 3 before the tanh, which re-saturates the signals to about ±1.
- **Output:**
  - Right logit = 6 × (unit 0), and left logit = 6 × (unit 1).
  - The no-op logit stays at 0 because its bias is 0 and it has no incoming weights.
  - When d = 0, both move logits are about −6, so the policy holds still with probability above 0.99.
  - When d ≠ 0, the matching move logit is about +6, so the policy moves toward the ball with probability above 0.99.
  - Up, down and fire stay at 0 and are effectively never chosen against a +6 logit.

The input indices used are ball = channel 3 (index 6c+3 plus 60 per row) and paddle = channel 0 on row 9 (index 540+6c).

```edits
# Unit 0: 4*(ball_col - paddle_col) - 2   (ball is right of paddle)
W1[9:600:60, 0] = 4
W1[15:600:60, 0] = 8
W1[21:600:60, 0] = 12
W1[27:600:60, 0] = 16
W1[33:600:60, 0] = 20
W1[39:600:60, 0] = 24
W1[45:600:60, 0] = 28
W1[51:600:60, 0] = 32
W1[57:600:60, 0] = 36
W1[540:600:6, 0] = [0, -4, -8, -12, -16, -20, -24, -28, -32, -36]
b1[0] = -2
# Unit 1: -4*(ball_col - paddle_col) - 2  (ball is left of paddle)
W1[9:600:60, 1] = -4
W1[15:600:60, 1] = -8
W1[21:600:60, 1] = -12
W1[27:600:60, 1] = -16
W1[33:600:60, 1] = -20
W1[39:600:60, 1] = -24
W1[45:600:60, 1] = -28
W1[51:600:60, 1] = -32
W1[57:600:60, 1] = -36
W1[540:600:6, 1] = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36]
b1[1] = -2
# Layer 2: re-saturating pass-through
W2[0, 0] = 3
W2[1, 1] = 3
# Outputs: action 3 (right) from unit 0, action 1 (left) from unit 1, no-op stays at 0
W3[0, 3] = 6
W3[1, 1] = 6
```