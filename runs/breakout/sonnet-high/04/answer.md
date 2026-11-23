**Design**

The strategy is to keep the paddle under the ball. The ball moves one column per step and the paddle also moves one column per step, so the paddle can keep up and catch the ball almost every time. The policy only needs the signed column difference d = ball_col − paddle_col.

**Hidden layer 1**
- Unit 0 is tanh(6·(d − 0.5)). Each ball cell (channel 3) in column c contributes +6c, and the paddle cell (channel 0, row 9) in column c contributes −6c. The bias is −3. The unit is about +1 when d ≥ 1 and about −1 when d ≤ 0.
- Unit 1 is tanh(6·(d + 0.5)), with the same weights and bias +3. It is about +1 when d ≥ 0 and about −1 when d ≤ −1.

**Hidden layer 2**
- Units 0 and 1 pass these signals through with weight 3, which sharpens the tanh output to about ±0.995.

**Output**
- The right logit is +6·h2₀. It is high when the ball is to the right (d ≥ 1) and low otherwise.
- The left logit is −6·h2₁. It is high when the ball is to the left (d ≤ −1) and low otherwise.
- The no-op, up, down and fire logits stay at 0, and all four do nothing in this game. When d = 0 both move logits are −6, so the paddle stays put. When the ball is off to one side, the correct move gets about 99% probability.

Sticky actions are mostly harmless, because while the ball travels diagonally the paddle is repeating the same move anyway.

```edits
W1[6*1+3:600:60, 0] = 6
W1[6*2+3:600:60, 0] = 12
W1[6*3+3:600:60, 0] = 18
W1[6*4+3:600:60, 0] = 24
W1[6*5+3:600:60, 0] = 30
W1[6*6+3:600:60, 0] = 36
W1[6*7+3:600:60, 0] = 42
W1[6*8+3:600:60, 0] = 48
W1[6*9+3:600:60, 0] = 54
W1[6*1+3:600:60, 1] = 6
W1[6*2+3:600:60, 1] = 12
W1[6*3+3:600:60, 1] = 18
W1[6*4+3:600:60, 1] = 24
W1[6*5+3:600:60, 1] = 30
W1[6*6+3:600:60, 1] = 36
W1[6*7+3:600:60, 1] = 42
W1[6*8+3:600:60, 1] = 48
W1[6*9+3:600:60, 1] = 54
W1[546, 0] = -6
W1[552, 0] = -12
W1[558, 0] = -18
W1[564, 0] = -24
W1[570, 0] = -30
W1[576, 0] = -36
W1[582, 0] = -42
W1[588, 0] = -48
W1[594, 0] = -54
W1[546, 1] = -6
W1[552, 1] = -12
W1[558, 1] = -18
W1[564, 1] = -24
W1[570, 1] = -30
W1[576, 1] = -36
W1[582, 1] = -42
W1[588, 1] = -48
W1[594, 1] = -54
b1[0] = -3
b1[1] = 3
W2[0, 0] = 3
W2[1, 1] = 3
W3[0, 3] = 6
W3[1, 1] = -6
```