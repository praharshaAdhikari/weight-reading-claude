**Design: reactive intercept.** The paddle estimates where the ball will land and moves toward it at one cell per step.

- **Landing estimate:** With `dx` = ball column − trail column and `dy` = ball row − trail row, a descending ball (`dy = +1`) in row `w` lands at about `u + dx·(8.5 − w)`. The 8.5 (instead of 9) centres the paddle on the two cells that catch the ball.
- **Layer 1, units 0–9 (P_r) and 10–19 (M_r):** Each is `tanh` of the linear form `6·[ball in row r] ± 3·dx + 3·dy − 10`. P_r is about +0.96 only for a ball in row r moving down-right, and M_r only for one moving down-left. Otherwise it is about −1.
- **Layer 1, unit 20:** `tanh(0.05·(ball column − paddle column))`.
- **Layer 2, unit 0:** `tanh(2D − 1)`, which is positive when D > 0.5 (move right). Here `D = 20·X + Σ_r (8.5−r)/1.964·(P_r − M_r)`, which is approximately `(ball column − paddle) + dx·(8.5 − row)`.
- **Layer 2, unit 1:** `tanh(−2D − 1)`, which is positive when D < −0.5 (move left).
- **Output:** the right logit is `6·h2_0` and the left logit is `6·h2_1`. The no-op logit is 0, and up/down/fire are −3, so the policy stays put inside the ±0.5 dead zone.

Known approximations: the landing estimate ignores wall and brick reflections, and the paddle corrects one step after each reflection.

```edits
# ---- layer 1 biases: P/M units 0..19 at -10, unit 20 at 0
b1[0:20] = -10

# ---- ball cells (channel 3): row term +3*row, units 0..19
W1[63:120:6, 0:20] += 3
W1[123:180:6, 0:20] += 6
W1[183:240:6, 0:20] += 9
W1[243:300:6, 0:20] += 12
W1[303:360:6, 0:20] += 15
W1[363:420:6, 0:20] += 18
W1[423:480:6, 0:20] += 21
W1[483:540:6, 0:20] += 24
W1[543:600:6, 0:20] += 27

# ---- ball cells (channel 3): column term, +3*col for P (0..9), -3*col for M (10..19)
W1[9:600:60, 0:10] += 3
W1[9:600:60, 10:20] += -3
W1[15:600:60, 0:10] += 6
W1[15:600:60, 10:20] += -6
W1[21:600:60, 0:10] += 9
W1[21:600:60, 10:20] += -9
W1[27:600:60, 0:10] += 12
W1[27:600:60, 10:20] += -12
W1[33:600:60, 0:10] += 15
W1[33:600:60, 10:20] += -15
W1[39:600:60, 0:10] += 18
W1[39:600:60, 10:20] += -18
W1[45:600:60, 0:10] += 21
W1[45:600:60, 10:20] += -21
W1[51:600:60, 0:10] += 24
W1[51:600:60, 10:20] += -24
W1[57:600:60, 0:10] += 27
W1[57:600:60, 10:20] += -27

# ---- ball row one-hot: +6 for the unit P_r (r) and M_r (10+r)
W1[3:60:6, 0] += 6
W1[3:60:6, 10] += 6
W1[63:120:6, 1] += 6
W1[63:120:6, 11] += 6
W1[123:180:6, 2] += 6
W1[123:180:6, 12] += 6
W1[183:240:6, 3] += 6
W1[183:240:6, 13] += 6
W1[243:300:6, 4] += 6
W1[243:300:6, 14] += 6
W1[303:360:6, 5] += 6
W1[303:360:6, 15] += 6
W1[363:420:6, 6] += 6
W1[363:420:6, 16] += 6
W1[423:480:6, 7] += 6
W1[423:480:6, 17] += 6
W1[483:540:6, 8] += 6
W1[483:540:6, 18] += 6
W1[543:600:6, 9] += 6
W1[543:600:6, 19] += 6

# ---- trail cells (channel 4): row term -3*row, units 0..19
W1[64:120:6, 0:20] += -3
W1[124:180:6, 0:20] += -6
W1[184:240:6, 0:20] += -9
W1[244:300:6, 0:20] += -12
W1[304:360:6, 0:20] += -15
W1[364:420:6, 0:20] += -18
W1[424:480:6, 0:20] += -21
W1[484:540:6, 0:20] += -24
W1[544:600:6, 0:20] += -27

# ---- trail cells (channel 4): column term, -3*col for P (0..9), +3*col for M (10..19)
W1[10:600:60, 0:10] += -3
W1[10:600:60, 10:20] += 3
W1[16:600:60, 0:10] += -6
W1[16:600:60, 10:20] += 6
W1[22:600:60, 0:10] += -9
W1[22:600:60, 10:20] += 9
W1[28:600:60, 0:10] += -12
W1[28:600:60, 10:20] += 12
W1[34:600:60, 0:10] += -15
W1[34:600:60, 10:20] += 15
W1[40:600:60, 0:10] += -18
W1[40:600:60, 10:20] += 18
W1[46:600:60, 0:10] += -21
W1[46:600:60, 10:20] += 21
W1[52:600:60, 0:10] += -24
W1[52:600:60, 10:20] += 24
W1[58:600:60, 0:10] += -27
W1[58:600:60, 10:20] += 27

# ---- unit 20: 0.05*(ball column - paddle column)
W1[9:600:60, 20] = 0.05
W1[15:600:60, 20] = 0.1
W1[21:600:60, 20] = 0.15
W1[27:600:60, 20] = 0.2
W1[33:600:60, 20] = 0.25
W1[39:600:60, 20] = 0.3
W1[45:600:60, 20] = 0.35
W1[51:600:60, 20] = 0.4
W1[57:600:60, 20] = 0.45
W1[540:600:6, 20] = [0, -0.05, -0.1, -0.15, -0.2, -0.25, -0.3, -0.35, -0.4, -0.45]

# ---- layer 2: unit 0 = tanh(2D-1) (move right), unit 1 = tanh(-2D-1) (move left)
W2[20, 0] = 40
W2[20, 1] = -40
W2[0:10, 0] = [8.66, 7.64, 6.62, 5.60, 4.58, 3.56, 2.55, 1.53, 0.51, -0.51]
W2[10:20, 0] = [-8.66, -7.64, -6.62, -5.60, -4.58, -3.56, -2.55, -1.53, -0.51, 0.51]
W2[0:10, 1] = [-8.66, -7.64, -6.62, -5.60, -4.58, -3.56, -2.55, -1.53, -0.51, 0.51]
W2[10:20, 1] = [8.66, 7.64, 6.62, 5.60, 4.58, 3.56, 2.55, 1.53, 0.51, -0.51]
b2[0:2] = -1

# ---- output: right (3) = 6*h2_0, left (1) = 6*h2_1, up/down/fire suppressed
W3[0, 3] = 6
W3[1, 1] = 6
b3[2:6] = [-3, 0, -3, -3]
```