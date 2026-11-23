**Design**

The policy moves the paddle toward the spot where the ball will land next. It never plans further ahead than that.

- **Inputs used.** Three input channels carry the signal: the paddle (channel 0, row 9), the ball (channel 3) and the ball's trail (channel 4).
- **Target position.** Let b be the ball's column, l the trail's column (where the ball was one step ago) and p the paddle's column. The target is t = b + (b−l)/2 = 1.5b − 0.5l. This is the ball column plus half its horizontal velocity. It sits midway between the two cells that catch the ball: the paddle catches at either the ball's current column or its next column.
- **Error signal.** The error is d = t − p. Because the weights are linear in column index, the first layer computes d as a weighted sum over cells. Ball cells get weight 12·column, trail cells −4·column, and paddle cells −8·column. These are 8× the formula above, so the tanh units are steep.
- **Hidden layer 1, two units.** Both units see the same 8d. Unit 0 is tanh(8d + 6), which is about +1 when d ≥ −0.5 and −1 when d ≤ −1. Unit 1 is tanh(8d − 6), which is about +1 when d ≥ 1 and −1 when d ≤ 0.5. The thresholds sit at ±0.75, which gives a dead band where the paddle does nothing.
- **Hidden layer 2.** Units 0 and 1 copy the two first-layer units with gain 1.5. The other units stay at zero.
- **Outputs.** Left = −6·A, right = +6·B, and no-op = 3·(A−B), where A and B are the two copied units. The three cases are:
  - **Ball well left of target (d ≤ −1):** left is favoured.
  - **Within the dead band:** no-op is favoured.
  - **Ball well right (d ≥ 1):** right is favoured.

  The winning logit leads by about 5 over the others. Up, down and fire get a bias of −5 so they are rarely sampled.

I could not run anything, so the weights are untested. The `W1[..., 0:2]` statements use scalar fills over a two-column block and assume broadcasting works.

```edits
# ball channel (3): weight 12*column to units 0 and 1
W1[9:600:60, 0:2] = 12
W1[15:600:60, 0:2] = 24
W1[21:600:60, 0:2] = 36
W1[27:600:60, 0:2] = 48
W1[33:600:60, 0:2] = 60
W1[39:600:60, 0:2] = 72
W1[45:600:60, 0:2] = 84
W1[51:600:60, 0:2] = 96
W1[57:600:60, 0:2] = 108
# trail channel (4): weight -4*column
W1[10:600:60, 0:2] = -4
W1[16:600:60, 0:2] = -8
W1[22:600:60, 0:2] = -12
W1[28:600:60, 0:2] = -16
W1[34:600:60, 0:2] = -20
W1[40:600:60, 0:2] = -24
W1[46:600:60, 0:2] = -28
W1[52:600:60, 0:2] = -32
W1[58:600:60, 0:2] = -36
# paddle channel (0), row 9: weight -8*column
W1[540:600:6, 0:2] = [[0, 0], [-8, -8], [-16, -16], [-24, -24], [-32, -32], [-40, -40], [-48, -48], [-56, -56], [-64, -64], [-72, -72]]
b1[0] = 6
b1[1] = -6
# layer 2: copy the two threshold units
W2[0, 0] = 1.5
W2[1, 1] = 1.5
# outputs
W3[0, 1] = -6
W3[1, 3] = 6
W3[0, 0] = 3
W3[1, 0] = -3
b3[2] = -5
b3[4] = -5
b3[5] = -5
```