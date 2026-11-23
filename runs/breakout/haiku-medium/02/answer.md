**Design**

The strategy is a ball tracker. The paddle moves toward the ball's column, and when it is directly under the ball it stays put. The ball reaches row 9 only from row 8, and a ball at column x in row 8 is caught when the paddle is at x after its move, so tracking the ball's current column is enough near the bottom.

Hidden units:
- **Layer 1, unit 0:** `tanh(2*(ball_x - paddle_x))`. Ball-channel weights are `2c` for column `c`, and paddle weights are `-2c` on row 9. It is about +1 when the ball is right of the paddle, about -1 when left, and 0 when aligned.
- **Layer 2, unit 0:** `tanh(3*h1_0)`, a sharpened sign of the offset.
- **Layer 2, units 1 and 2:** `tanh(3*h1_0 + 1)` and `tanh(3*h1_0 - 1)`. Their difference is a zero-offset detector, about 1.5 when aligned and about 0.04 when off by one.
- **Output:** right and left logits are ±8 times the sign unit, so the paddle moves decisively toward the ball. The no-op logit is 3 times the zero detector, so the paddle stays still when aligned. Up, down and fire get zero logits and act as no-ops in this game.

```edits
# Layer 1: unit 0 = 2*(ball_x - paddle_x).
# Ball channel 3 (rows 3::6 for every cell): value 2*column.
W1[3:600:6, 0] = [
0,2,4,6,8,10,12,14,16,18,
0,2,4,6,8,10,12,14,16,18,
0,2,4,6,8,10,12,14,16,18,
0,2,4,6,8,10,12,14,16,18,
0,2,4,6,8,10,12,14,16,18,
0,2,4,6,8,10,12,14,16,18,
0,2,4,6,8,10,12,14,16,18,
0,2,4,6,8,10,12,14,16,18,
0,2,4,6,8,10,12,14,16,18,
0,2,4,6,8,10,12,14,16,18
]
# Paddle channel 0 on row 9 (indices 540 + 6c): value -2*column.
W1[540:600:6, 0] = [0,-2,-4,-6,-8,-10,-12,-14,-16,-18]

# Layer 1 biases stay zero.
b1[0:32] = 0

# Layer 2: units 0..2 read layer-1 unit 0.
W2[0, 0:3] = [3, 3, 3]
b2[0:3] = [0, 1, -1]

# Output: right/left follow the sign unit; no-op follows the zero detector.
W3[0, 1] = -8     # left  <- sign unit (negative offset means ball is left)
W3[0, 3] = 8      # right <- sign unit (positive offset means ball is right)
W3[1, 0] = 3      # no-op <- zero detector (+)
W3[2, 0] = -3     # no-op <- zero detector (-)
b3[0:6] = 0
```