## Design

The network predicts where the ball will land on row 8 and steps the paddle toward that column.

**Prediction.** With ball (X, Y), trail (TX, TY) and paddle column P:
- The ball's horizontal direction dx comes from X−TX. When X = TX (right after a wall bounce) the ball is heading away from the wall.
- The ball's vertical direction comes from Y−TY. When Y = TY the ball is going down, except on row 8, where it has just been caught and is going up.
- Going down, the unfolded landing column is u = X + dx·(8−Y). That is u = X−Y+8 for down-right and u = X+Y−8 for down-left.
- The ball reflects off the side walls about −0.5 and 9.5. The folded target T is u itself for 0 ≤ u ≤ 9, 19−u for u ≥ 10, and −1−u for u ≤ −1.
- Going up, the target is T = X, so the paddle tracks the ball.

**Decision.** With thresholds t1 = −1−P, t2 = P, t3 = 19−P, the pattern along u is: right if u < t1, left if t1 < u < t2, right if t2 < u < t3, left if u > t3. Equality at a threshold means no move. This holds in all three cases, with u = X for the going-up case.

**Layer 1 (16 tanh units, saturated, each a ±1 detector):**
- Units 0–5 (down-right): A1, B1, A2, B2, A3, B3, where A_k = [u − t_k ≥ 1] and B_k = [u − t_k ≥ 0].
- Units 6–11: the same six detectors for down-left.
- Units 12–13: [X > P] and [X ≥ P] for the going-up case.
- Unit 14: "ball going down", computed as (Y−TY) − 0.6·[Y = 8] + 0.3.
- Unit 15: sign of dx, computed as (X−TX) + 0.6·[X = 0] − 0.6·[X = 9].

**Layer 2 (6 AND units):** right and left for each of down-right, down-left and going-up.
- Each is the gate (down, and direction where relevant) combined with the interval formula.
- For example, right = 1 − B1 + A2 − B3.

**Output:**
- Logit right = 7·(sum of the three right units) + 21, and logit left is built the same way. Each reaches about 14 when active and about 0 otherwise.
- Actions 0, 2, 4 and 5 all act as no-ops and get a bias of 5, so the paddle stays still when it is already on target.

```edits
# ---- layer 1: compare units (cols 0-5 down-right, 6-11 down-left, 12-13 going up), scale 8 ----
W1[9:600:60, 0:14] = 8
W1[15:600:60, 0:14] = 16
W1[21:600:60, 0:14] = 24
W1[27:600:60, 0:14] = 32
W1[33:600:60, 0:14] = 40
W1[39:600:60, 0:14] = 48
W1[45:600:60, 0:14] = 56
W1[51:600:60, 0:14] = 64
W1[57:600:60, 0:14] = 72
# Y part (ball row): down-right gets -8r, down-left gets +8r
W1[63:120:6, 0:6] += -8
W1[63:120:6, 6:12] += 8
W1[123:180:6, 0:6] += -16
W1[123:180:6, 6:12] += 16
W1[183:240:6, 0:6] += -24
W1[183:240:6, 6:12] += 24
W1[243:300:6, 0:6] += -32
W1[243:300:6, 6:12] += 32
W1[303:360:6, 0:6] += -40
W1[303:360:6, 6:12] += 40
W1[363:420:6, 0:6] += -48
W1[363:420:6, 6:12] += 48
W1[423:480:6, 0:6] += -56
W1[423:480:6, 6:12] += 56
W1[483:540:6, 0:6] += -64
W1[483:540:6, 6:12] += 64
# paddle column weights (input 540+6c), signs per unit
W1[546, 0:14] = [8, 8, -8, -8, 8, 8, 8, 8, -8, -8, 8, 8, -8, -8]
W1[552, 0:14] = [16, 16, -16, -16, 16, 16, 16, 16, -16, -16, 16, 16, -16, -16]
W1[558, 0:14] = [24, 24, -24, -24, 24, 24, 24, 24, -24, -24, 24, 24, -24, -24]
W1[564, 0:14] = [32, 32, -32, -32, 32, 32, 32, 32, -32, -32, 32, 32, -32, -32]
W1[570, 0:14] = [40, 40, -40, -40, 40, 40, 40, 40, -40, -40, 40, 40, -40, -40]
W1[576, 0:14] = [48, 48, -48, -48, 48, 48, 48, 48, -48, -48, 48, 48, -48, -48]
W1[582, 0:14] = [56, 56, -56, -56, 56, 56, 56, 56, -56, -56, 56, 56, -56, -56]
W1[588, 0:14] = [64, 64, -64, -64, 64, 64, 64, 64, -64, -64, 64, 64, -64, -64]
W1[594, 0:14] = [72, 72, -72, -72, 72, 72, 72, 72, -72, -72, 72, 72, -72, -72]
b1[0:6] = [68, 76, 60, 68, -92, -84]
b1[6:12] = [-60, -52, -68, -60, -220, -212]
b1[12:14] = [-4, 4]
# ---- unit 14: ball going down (scale 15) ----
W1[63:120:6, 14] = 15
W1[123:180:6, 14] = 30
W1[183:240:6, 14] = 45
W1[243:300:6, 14] = 60
W1[303:360:6, 14] = 75
W1[363:420:6, 14] = 90
W1[423:480:6, 14] = 105
W1[483:540:6, 14] = 111
W1[64:120:6, 14] = -15
W1[124:180:6, 14] = -30
W1[184:240:6, 14] = -45
W1[244:300:6, 14] = -60
W1[304:360:6, 14] = -75
W1[364:420:6, 14] = -90
W1[424:480:6, 14] = -105
W1[484:540:6, 14] = -120
b1[14] = 4.5
# ---- unit 15: horizontal direction sign (scale 10) ----
W1[3:600:60, 15] = 6
W1[9:600:60, 15] = 10
W1[15:600:60, 15] = 20
W1[21:600:60, 15] = 30
W1[27:600:60, 15] = 40
W1[33:600:60, 15] = 50
W1[39:600:60, 15] = 60
W1[45:600:60, 15] = 70
W1[51:600:60, 15] = 80
W1[57:600:60, 15] = 84
W1[10:600:60, 15] = -10
W1[16:600:60, 15] = -20
W1[22:600:60, 15] = -30
W1[28:600:60, 15] = -40
W1[34:600:60, 15] = -50
W1[40:600:60, 15] = -60
W1[46:600:60, 15] = -70
W1[52:600:60, 15] = -80
W1[58:600:60, 15] = -90
# ---- layer 2: AND units ----
# unit 0: right, down-right
W2[14, 0] = 4
W2[15, 0] = 4
W2[1, 0] = -4
W2[2, 0] = 4
W2[5, 0] = -4
b2[0] = -8
# unit 1: left, down-right
W2[14, 1] = 4
W2[15, 1] = 4
W2[0, 1] = 4
W2[3, 1] = -4
W2[4, 1] = 4
b2[1] = -8
# unit 2: right, down-left
W2[14, 2] = 4
W2[15, 2] = -4
W2[7, 2] = -4
W2[8, 2] = 4
W2[11, 2] = -4
b2[2] = -8
# unit 3: left, down-left
W2[14, 3] = 4
W2[15, 3] = -4
W2[6, 3] = 4
W2[9, 3] = -4
W2[10, 3] = 4
b2[3] = -8
# unit 4: right, going up (track ball)
W2[14, 4] = -4
W2[12, 4] = 4
b2[4] = -4
# unit 5: left, going up
W2[14, 5] = -4
W2[13, 5] = -4
b2[5] = -4
# ---- outputs ----
W3[0, 3] = 7
W3[2, 3] = 7
W3[4, 3] = 7
W3[1, 1] = 7
W3[3, 1] = 7
W3[5, 1] = 7
b3[3] = 21
b3[1] = 21
b3[0] = 5
b3[2] = 5
b3[4] = 5
b3[5] = 5
```