## Design

**Strategy: go to where the ball will land, then wait.** The ball's horizontal motion is a 20-step cycle (10 cells, with a one-step pause at each wall), so its landing column can be computed from its position and direction. I have not run anything; a few states were traced by hand through the weights.

- **Landing estimate.** The unfolded landing coordinate is `z = x ± m`, where `m` is the earliest possible number of steps until the ball is back on row 8. Descending (or just bounced off a brick or the ceiling), `m = 8 − y`. Ascending, `m` assumes the next possible brick strike: 9, 8, 7, 6, 5 for rows 8 to 4, then 6, 7, 10, 9 for rows 3 to 0.
- **Why earliest is safe.** The estimate only ever moves later, and the paddle should have enough actions left to follow it when it does.
- **Parity trick.** The landing phase is rounded up to even, which makes the first paddle hit a "reverse" bounce. After that, the ball never lands exactly in a corner, which is the one case that needs a full 9-cell paddle run in 10 actions. A miss should then need about three consecutive sticky repeats at the worst moment rather than two.
- **Bricks are ignored.** No weights read the brick channel; with the paddle bounces the policy aims for, the ball's path should eventually sweep every brick.

**Hidden layer 1 (17 units used, sharp tanh as ±1 logic):**
- Units 0–7 assume the ball moves right; units 8–15 assume it moves left. Each is switched off (−1) by an exact additive gate on ball column plus trail column when its assumption is wrong, including the wall-pause case where ball and trail share a column.
- Within each group there are four threshold comparisons of `z` against a paddle-dependent table (the reflection and parity rounding live in the paddle weights). Each comparison exists twice: once with the ascending `m`, once with the descending `m`.
- Unit 16 reports the vertical direction (+1 ascending or just hit by the paddle, −1 otherwise).

**Hidden layer 2 (4 units):** `Right` and `Left`, each for the ascending and descending case. Each is a weighted sum of the comparison units that implements the AND/OR, combined with unit 16.

**Output:** right and left get +20 when their unit fires and −20 otherwise; no-op sits at 0; up, down and fire sit at −100.

The block relies on scalar fills of 2-D ranges and on `+=` / `-=` with a scalar; if the parser rejects either, the policy breaks.

```edits
# ---------- Layer 1: ball channel (3), column part = +-10*x + 300*gate ----------
# units 0-3: moving-right group, +x
W1[9:600:60, 0:4] = 10
W1[15:600:60, 0:4] = 320
W1[21:600:60, 0:4] = 330
W1[27:600:60, 0:4] = 640
W1[33:600:60, 0:4] = 650
W1[39:600:60, 0:4] = 960
W1[45:600:60, 0:4] = 970
W1[51:600:60, 0:4] = 1280
W1[57:600:60, 0:4] = 1290
# units 4-7: moving-right group, -x
W1[9:600:60, 4:8] = -10
W1[15:600:60, 4:8] = 280
W1[21:600:60, 4:8] = 270
W1[27:600:60, 4:8] = 560
W1[33:600:60, 4:8] = 550
W1[39:600:60, 4:8] = 840
W1[45:600:60, 4:8] = 830
W1[51:600:60, 4:8] = 1120
W1[57:600:60, 4:8] = 1110
# units 8-11: moving-left group, +x
W1[3:600:60, 8:12] = 1200
W1[9:600:60, 8:12] = 1210
W1[15:600:60, 8:12] = 920
W1[21:600:60, 8:12] = 930
W1[27:600:60, 8:12] = 640
W1[33:600:60, 8:12] = 650
W1[39:600:60, 8:12] = 360
W1[45:600:60, 8:12] = 370
W1[51:600:60, 8:12] = 80
W1[57:600:60, 8:12] = 90
# units 12-15: moving-left group, -x
W1[3:600:60, 12:16] = 1200
W1[9:600:60, 12:16] = 1190
W1[15:600:60, 12:16] = 880
W1[21:600:60, 12:16] = 870
W1[27:600:60, 12:16] = 560
W1[33:600:60, 12:16] = 550
W1[39:600:60, 12:16] = 240
W1[45:600:60, 12:16] = 230
W1[51:600:60, 12:16] = -80
W1[57:600:60, 12:16] = -90

# ---------- trail channel (4), column part = 300*gate ----------
# units 0-7 (moving-right gate)
W1[10:600:60, 0:8] = -300
W1[16:600:60, 0:8] = -300
W1[22:600:60, 0:8] = -600
W1[28:600:60, 0:8] = -600
W1[34:600:60, 0:8] = -900
W1[40:600:60, 0:8] = -900
W1[46:600:60, 0:8] = -1200
W1[52:600:60, 0:8] = -1200
W1[58:600:60, 0:8] = -1500
# units 8-15 (moving-left gate)
W1[4:600:60, 8:16] = -1500
W1[10:600:60, 8:16] = -1200
W1[16:600:60, 8:16] = -1200
W1[22:600:60, 8:16] = -900
W1[28:600:60, 8:16] = -900
W1[34:600:60, 8:16] = -600
W1[40:600:60, 8:16] = -600
W1[46:600:60, 8:16] = -300
W1[52:600:60, 8:16] = -300

# ---------- ball channel, row part = +-10*m(row) ----------
# units 0-1: +10*m_asc
W1[3:60:6, 0:2] += 90
W1[63:120:6, 0:2] += 100
W1[123:180:6, 0:2] += 70
W1[183:240:6, 0:2] += 60
W1[243:300:6, 0:2] += 50
W1[303:360:6, 0:2] += 60
W1[363:420:6, 0:2] += 70
W1[423:480:6, 0:2] += 80
W1[483:540:6, 0:2] += 90
# units 2-3: +10*m_desc
W1[3:60:6, 2:4] += 80
W1[63:120:6, 2:4] += 70
W1[123:180:6, 2:4] += 60
W1[183:240:6, 2:4] += 50
W1[243:300:6, 2:4] += 40
W1[303:360:6, 2:4] += 30
W1[363:420:6, 2:4] += 20
W1[423:480:6, 2:4] += 10
# units 4-5: -10*m_asc
W1[3:60:6, 4:6] -= 90
W1[63:120:6, 4:6] -= 100
W1[123:180:6, 4:6] -= 70
W1[183:240:6, 4:6] -= 60
W1[243:300:6, 4:6] -= 50
W1[303:360:6, 4:6] -= 60
W1[363:420:6, 4:6] -= 70
W1[423:480:6, 4:6] -= 80
W1[483:540:6, 4:6] -= 90
# units 6-7: -10*m_desc
W1[3:60:6, 6:8] -= 80
W1[63:120:6, 6:8] -= 70
W1[123:180:6, 6:8] -= 60
W1[183:240:6, 6:8] -= 50
W1[243:300:6, 6:8] -= 40
W1[303:360:6, 6:8] -= 30
W1[363:420:6, 6:8] -= 20
W1[423:480:6, 6:8] -= 10
# units 8-9: -10*m_asc
W1[3:60:6, 8:10] -= 90
W1[63:120:6, 8:10] -= 100
W1[123:180:6, 8:10] -= 70
W1[183:240:6, 8:10] -= 60
W1[243:300:6, 8:10] -= 50
W1[303:360:6, 8:10] -= 60
W1[363:420:6, 8:10] -= 70
W1[423:480:6, 8:10] -= 80
W1[483:540:6, 8:10] -= 90
# units 10-11: -10*m_desc
W1[3:60:6, 10:12] -= 80
W1[63:120:6, 10:12] -= 70
W1[123:180:6, 10:12] -= 60
W1[183:240:6, 10:12] -= 50
W1[243:300:6, 10:12] -= 40
W1[303:360:6, 10:12] -= 30
W1[363:420:6, 10:12] -= 20
W1[423:480:6, 10:12] -= 10
# units 12-13: +10*m_asc
W1[3:60:6, 12:14] += 90
W1[63:120:6, 12:14] += 100
W1[123:180:6, 12:14] += 70
W1[183:240:6, 12:14] += 60
W1[243:300:6, 12:14] += 50
W1[303:360:6, 12:14] += 60
W1[363:420:6, 12:14] += 70
W1[423:480:6, 12:14] += 80
W1[483:540:6, 12:14] += 90
# units 14-15: +10*m_desc
W1[3:60:6, 14:16] += 80
W1[63:120:6, 14:16] += 70
W1[123:180:6, 14:16] += 60
W1[183:240:6, 14:16] += 50
W1[243:300:6, 14:16] += 40
W1[303:360:6, 14:16] += 30
W1[363:420:6, 14:16] += 20
W1[423:480:6, 14:16] += 10

# ---------- paddle (channel 0, row 9): threshold tables ----------
W1[540:600:6, 0] = [-10, -10, -30, -30, -50, -50, -70, -70, -90, -90]
W1[540:600:6, 1] = [-190, -190, -170, -170, -150, -150, -130, -130, -110, -110]
W1[540:600:6, 2] = [-10, -10, -30, -30, -50, -50, -70, -70, -90, -90]
W1[540:600:6, 3] = [-190, -190, -170, -170, -150, -150, -130, -130, -110, -110]
W1[540:600:6, 4] = [180, 160, 160, 140, 140, 120, 120, 100, 100, 80]
W1[540:600:6, 5] = [-20, 0, 0, 20, 20, 40, 40, 60, 60, 80]
W1[540:600:6, 6] = [180, 160, 160, 140, 140, 120, 120, 100, 100, 80]
W1[540:600:6, 7] = [-20, 0, 0, 20, 20, 40, 40, 60, 60, 80]
W1[540:600:6, 8] = [-10, -30, -30, -50, -50, -70, -70, -90, -90, -110]
W1[540:600:6, 9] = [-10, 10, 10, 30, 30, 50, 50, 70, 70, 90]
W1[540:600:6, 10] = [-10, -30, -30, -50, -50, -70, -70, -90, -90, -110]
W1[540:600:6, 11] = [-10, 10, 10, 30, 30, 50, 50, 70, 70, 90]
W1[540:600:6, 12] = [-20, -20, -40, -40, -60, -60, -80, -80, -100, -100]
W1[540:600:6, 13] = [0, 0, 20, 20, 40, 40, 60, 60, 80, 80]
W1[540:600:6, 14] = [-20, -20, -40, -40, -60, -60, -80, -80, -100, -100]
W1[540:600:6, 15] = [0, 0, 20, 20, 40, 40, 60, 60, 80, 80]
b1[0:16] = 5

# ---------- unit 16: vertical direction (+1 ascending / just hit by paddle) ----------
W1[63:120:6, 16] = -10
W1[123:180:6, 16] = -20
W1[183:240:6, 16] = -30
W1[243:300:6, 16] = -40
W1[303:360:6, 16] = -50
W1[363:420:6, 16] = -60
W1[423:480:6, 16] = -70
W1[483:540:6, 16] = -70
W1[64:120:6, 16] = 10
W1[124:180:6, 16] = 20
W1[184:240:6, 16] = 30
W1[244:300:6, 16] = 40
W1[304:360:6, 16] = 50
W1[364:420:6, 16] = 60
W1[424:480:6, 16] = 70
W1[484:540:6, 16] = 80
b1[16] = -5

# ---------- Layer 2 ----------
# unit 0: Right (ascending case)
W2[0, 0] = 5
W2[4, 0] = 5
W2[8, 0] = 10
W2[12, 0] = 10
W2[16, 0] = 10
b2[0] = 5
# unit 1: Right (descending case)
W2[2, 1] = 5
W2[6, 1] = 5
W2[10, 1] = 10
W2[14, 1] = 10
W2[16, 1] = -10
b2[1] = 5
# unit 2: Left (ascending case)
W2[5, 2] = 10
W2[1, 2] = 10
W2[13, 2] = 5
W2[9, 2] = 5
W2[16, 2] = 10
b2[2] = 5
# unit 3: Left (descending case)
W2[7, 3] = 10
W2[3, 3] = 10
W2[15, 3] = 5
W2[11, 3] = 5
W2[16, 3] = -10
b2[3] = 5

# ---------- Output ----------
W3[0, 3] = 20
W3[1, 3] = 20
W3[2, 1] = 20
W3[3, 1] = 20
b3[0:6] = [0, 20, -100, 20, -100, -100]
```