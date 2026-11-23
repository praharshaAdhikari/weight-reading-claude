**Design**

The strategy is to keep the paddle on the column the ball is about to occupy. That way a single sticky-action slip still leaves the paddle within one cell of the ball when it lands, and any larger lag is recovered when the ball stalls for a step at a side wall.

- **Normal mode (ball not in row 8):** the target is the ball's next column, `2·ball_x − trail_x`. Ball columns 0 and 9 are weighted 1 and 17 instead of 0 and 18, so the wall stall and reflection are predicted exactly. The signal is `s1 = target − paddle_x`.
- **Ball in row 8 (about to land, or just bounced):** the target is the ball's current column, `s0 = ball_x − paddle_x`. This gives the straight bounce, where the ball keeps its horizontal direction. I avoid the corner bounce because it sends the ball back along its own path, and for one step afterwards the trail points the wrong way.

Both signals are linear in the inputs, so the network only needs thresholds and a gate.

First-layer units:
- Unit 0: `s1 ≥ 1`.
- Unit 1: `s1 ≥ 0`.
- Unit 2: `s0 ≥ 1`.
- Unit 3: `s0 ≥ 0`.
- Unit 4: ball is in row 8.

Second-layer units (each an AND of a threshold with the gate):
- Unit 0: go right in normal mode (`s1 ≥ 1` and ball not in row 8).
- Unit 1: go right in row-8 mode (`s0 ≥ 1` and ball in row 8).
- Unit 2: go left in normal mode (`s1 ≤ −1` and ball not in row 8).
- Unit 3: go left in row-8 mode (`s0 ≤ −1` and ball in row 8).

Output: the right logit is 20·(unit 0 + unit 1), the left logit is 20·(unit 2 + unit 3), and no-op has a bias of −20. The active move wins by about 20 logits and no-op wins by about 20 when neither fires, so sampling is effectively deterministic. Up, down and fire are held at −60.

```edits
# ---- Layer 1, units 0 and 1: s1 = 2*ball_x' - trail_x - paddle_x (scaled by 6) ----
# ball (channel 3), per column, all rows
W1[3:600:60, 0] = 6
W1[9:600:60, 0] = 12
W1[15:600:60, 0] = 24
W1[21:600:60, 0] = 36
W1[27:600:60, 0] = 48
W1[33:600:60, 0] = 60
W1[39:600:60, 0] = 72
W1[45:600:60, 0] = 84
W1[51:600:60, 0] = 96
W1[57:600:60, 0] = 102
W1[3:600:60, 1] = 6
W1[9:600:60, 1] = 12
W1[15:600:60, 1] = 24
W1[21:600:60, 1] = 36
W1[27:600:60, 1] = 48
W1[33:600:60, 1] = 60
W1[39:600:60, 1] = 72
W1[45:600:60, 1] = 84
W1[51:600:60, 1] = 96
W1[57:600:60, 1] = 102
# trail (channel 4), per column
W1[10:600:60, 0] = -6
W1[16:600:60, 0] = -12
W1[22:600:60, 0] = -18
W1[28:600:60, 0] = -24
W1[34:600:60, 0] = -30
W1[40:600:60, 0] = -36
W1[46:600:60, 0] = -42
W1[52:600:60, 0] = -48
W1[58:600:60, 0] = -54
W1[10:600:60, 1] = -6
W1[16:600:60, 1] = -12
W1[22:600:60, 1] = -18
W1[28:600:60, 1] = -24
W1[34:600:60, 1] = -30
W1[40:600:60, 1] = -36
W1[46:600:60, 1] = -42
W1[52:600:60, 1] = -48
W1[58:600:60, 1] = -54
# paddle (channel 0), per column
W1[6:600:60, 0] = -6
W1[12:600:60, 0] = -12
W1[18:600:60, 0] = -18
W1[24:600:60, 0] = -24
W1[30:600:60, 0] = -30
W1[36:600:60, 0] = -36
W1[42:600:60, 0] = -42
W1[48:600:60, 0] = -48
W1[54:600:60, 0] = -54
W1[6:600:60, 1] = -6
W1[12:600:60, 1] = -12
W1[18:600:60, 1] = -18
W1[24:600:60, 1] = -24
W1[30:600:60, 1] = -30
W1[36:600:60, 1] = -36
W1[42:600:60, 1] = -42
W1[48:600:60, 1] = -48
W1[54:600:60, 1] = -54
b1[0] = -3
b1[1] = 3

# ---- Layer 1, units 2 and 3: s0 = ball_x - paddle_x (scaled by 6) ----
W1[9:600:60, 2] = 6
W1[15:600:60, 2] = 12
W1[21:600:60, 2] = 18
W1[27:600:60, 2] = 24
W1[33:600:60, 2] = 30
W1[39:600:60, 2] = 36
W1[45:600:60, 2] = 42
W1[51:600:60, 2] = 48
W1[57:600:60, 2] = 54
W1[9:600:60, 3] = 6
W1[15:600:60, 3] = 12
W1[21:600:60, 3] = 18
W1[27:600:60, 3] = 24
W1[33:600:60, 3] = 30
W1[39:600:60, 3] = 36
W1[45:600:60, 3] = 42
W1[51:600:60, 3] = 48
W1[57:600:60, 3] = 54
W1[6:600:60, 2] = -6
W1[12:600:60, 2] = -12
W1[18:600:60, 2] = -18
W1[24:600:60, 2] = -24
W1[30:600:60, 2] = -30
W1[36:600:60, 2] = -36
W1[42:600:60, 2] = -42
W1[48:600:60, 2] = -48
W1[54:600:60, 2] = -54
W1[6:600:60, 3] = -6
W1[12:600:60, 3] = -12
W1[18:600:60, 3] = -18
W1[24:600:60, 3] = -24
W1[30:600:60, 3] = -30
W1[36:600:60, 3] = -36
W1[42:600:60, 3] = -42
W1[48:600:60, 3] = -48
W1[54:600:60, 3] = -54
b1[2] = -3
b1[3] = 3

# ---- Layer 1, unit 4: ball in row 8 ----
W1[483:540:6, 4] = 6
b1[4] = -3

# ---- Layer 2: gated decisions ----
# unit 0: right, normal mode  (s1>=1 AND not row 8)
W2[0, 0] = 3
W2[4, 0] = -3
b2[0] = -3
# unit 1: right, row-8 mode   (s0>=1 AND row 8)
W2[2, 1] = 3
W2[4, 1] = 3
b2[1] = -3
# unit 2: left, normal mode   (s1<=-1 AND not row 8)
W2[1, 2] = -3
W2[4, 2] = -3
b2[2] = -3
# unit 3: left, row-8 mode    (s0<=-1 AND row 8)
W2[3, 3] = -3
W2[4, 3] = 3
b2[3] = -3

# ---- Output ----
W3[0, 3] = 20
W3[1, 3] = 20
W3[2, 1] = 20
W3[3, 1] = 20
b3[0:6] = [-20, 0, -60, 0, -60, -60]
```