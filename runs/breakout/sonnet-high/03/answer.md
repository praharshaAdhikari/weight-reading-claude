**Design**

The policy is a tracking controller. It moves the paddle toward the ball's column, so the paddle stays within one cell of the ball while it is falling and is in place for the catch at row 8. The ball moves one column per step and the paddle moves one cell per step, so a one-cell lag is stable. The ball also dwells for two steps at a side wall, which lets the paddle regain a cell if sticky actions cause a slip.

I have not run this network, so its performance is untested.

**Hidden units**

- **Layer 1, units 0 and 1.** Both compute d = (ball column) − (paddle column), scaled by 4. Each ball cell (channel 3) gets weight 4·column and each paddle cell (channel 0, row 9) gets weight −4·column. Only one ball and one paddle are ever active, so the pre-activation is 4d plus the bias.
  - Unit 0 has bias −2, so it is about +1 when d ≥ 1 and about −1 otherwise.
  - Unit 1 has bias +2, so it is about +1 when d ≥ 0 and about −1 otherwise.
- **Layer 2.** Units 0 and 1 copy layer-1 units 0 and 1 through a gain of 2, which sharpens the saturation.
- **Outputs.**
  - Right = 8·h0, so it is high when d ≥ 1.
  - Left = −8·h1, so it is high when d ≤ −1.
  - No-op = 4·(h1 − h0), so it is high only when d = 0.
  - Up, down and fire get bias −5 so they are never chosen.

```edits
W1[9:600:60, 0:2] = 4
W1[15:600:60, 0:2] = 8
W1[21:600:60, 0:2] = 12
W1[27:600:60, 0:2] = 16
W1[33:600:60, 0:2] = 20
W1[39:600:60, 0:2] = 24
W1[45:600:60, 0:2] = 28
W1[51:600:60, 0:2] = 32
W1[57:600:60, 0:2] = 36
W1[546, 0:2] = -4
W1[552, 0:2] = -8
W1[558, 0:2] = -12
W1[564, 0:2] = -16
W1[570, 0:2] = -20
W1[576, 0:2] = -24
W1[582, 0:2] = -28
W1[588, 0:2] = -32
W1[594, 0:2] = -36
b1[0] = -2
b1[1] = 2
W2[0, 0] = 2
W2[1, 1] = 2
W3[0, 3] = 8
W3[1, 1] = -8
W3[0, 0] = -4
W3[1, 0] = 4
b3[2] = -5
b3[4] = -5
b3[5] = -5
```