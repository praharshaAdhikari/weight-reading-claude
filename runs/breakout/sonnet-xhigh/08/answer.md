## Design

The network predicts where the ball will come back down and moves the paddle into the two-cell catch window there. It does this in four steps.

1. **Landing prediction.** The ball moves one cell per step along a diagonal. Its x-motion is a reflection between the walls. Brick, ceiling and paddle bounces only flip the vertical direction. So the unfolded landing x is `u = bx + dx·(steps to row 8)`, and the real landing cell is `fold(u)`. That gives four direction cases:
   - Descending right: `u = bx − by + 8`.
   - Descending left: `u = bx + by − 8`.
   - Ascending right: `u = bx + by + 1`. This assumes the ball turns back at the lowest brick row.
   - Ascending left: `u = bx − by − 1`. This makes the same assumption.

2. **Catch window.** At the last step the paddle must end on the ball's x or on its post-bounce x. For each case this window is `[lo, hi]`, written with min/max of `u` and `19−u` for right-moving balls, or of `|u|−1` and `|u|` for left-moving balls. The paddle moves right if `p < lo`, left if `p > hi`, and stays still inside the window. Staying still inside the window also makes the policy robust to sticky actions.

3. **Layer 1 (7 units used).**
   - Units 0–2 run in the near-linear region of tanh and give soft readouts of ball x, ball y and paddle x.
   - Units 3–6 are saturated direction gates: right-down, left-down, right-up and left-up. They read (ball − trail) along the S = x+y or D = x−y diagonal, with small bonuses so that wall, brick, top and paddle bounce frames are classified correctly.

4. **Layer 2 (16 units used).** There are four per case. Each unit is `tanh(300·(gate−1) + 10·Z)`, where `Z` is one integer inequality between `u` and the paddle position, offset by 0.5. It is active only when its gate is on.
   - Right needs two conditions to hold together (`p<u` and `p<18−u`, or the left-moving equivalent).
   - Left needs either of two conditions.

   **Output.** The logits are weighted sums of these units, with a constant noop logit of 36 that wins whenever no move is needed. Up, down and fire are suppressed.

```edits
# ---------- layer 1: soft readouts (linear regime of tanh, eps=0.02) ----------
# unit 0: ball x  -> tanh(0.02*(bx-4.5))
W1[9:600:60, 0] = 0.02
W1[15:600:60, 0] = 0.04
W1[21:600:60, 0] = 0.06
W1[27:600:60, 0] = 0.08
W1[33:600:60, 0] = 0.10
W1[39:600:60, 0] = 0.12
W1[45:600:60, 0] = 0.14
W1[51:600:60, 0] = 0.16
W1[57:600:60, 0] = 0.18
b1[0] = -0.09
# unit 1: ball y -> tanh(0.02*(by-4))
W1[63:120:6, 1] = 0.02
W1[123:180:6, 1] = 0.04
W1[183:240:6, 1] = 0.06
W1[243:300:6, 1] = 0.08
W1[303:360:6, 1] = 0.10
W1[363:420:6, 1] = 0.12
W1[423:480:6, 1