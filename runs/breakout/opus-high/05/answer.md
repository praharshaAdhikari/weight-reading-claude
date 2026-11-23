## Design

**Strategy.** Move the paddle to the column where the ball will reach row 8 on its way down (the landing column L), then wait there. At the final step, choose at random between the two moves that both catch the ball. This randomness changes the ball's path from one catch to the next, so it cannot settle into a loop that never hits a brick.

**Landing prediction.** Reflections off the side walls are a fold of a straight line. The ball's unfolded column is u = bx + d·n, where:
- d = ±1 is the horizontal direction.
- n is the number of steps left before the ball reaches row 8 going down.
- Going down: n = 8 − by.
- Going up: n = by + 1. This assumes the ball bounces off the bottom brick row at row 4.

The real column is L = f(u), with f(u) = −1−u for u < 0 and f(u) = 19−u for u > 9. Comparing L with the paddle column p reduces to thresholds on u−p and u+p:
- For d = +1:
  - Move right = [u−p ≥ 1] AND NOT [u+p ≥ 19].
  - Move left = NOT [u−p ≥ 0] OR [u+p ≥ 20].
- For d = −1:
  - Move right = [u−p ≥ 1] OR NOT [u+p ≥ −1].
  - Move left = [u+p ≥ 0] AND NOT [u−p ≥ 0].

**Layer 1 (24 units).** Weights are column terms plus row terms, so every unit is additive in the inputs.
- **Units 0–15:** threshold units for the 4 cases (d = ±1, going down or up) × 4 thresholds. Unit index = case + 4·type.
  - Ball weights: 8·bx + 8·d·n(by).
  - Paddle weights: ∓8·p.
- **Unit 16 (direction):** d = +1 if bx − tx + [bx = 0] ≥ 1, where tx is the trail column. This covers the step where the ball sits against a wall.
- **Unit 17 (vertical):** going down vs. going up, from additive row weights on the ball and the trail. A ball and trail in the same row count as going down after a brick or ceiling bounce, and as going up at row 8 just after a catch.
- **Units 18–21 (final step):** active only on the final step (ball in row 8, trail in row 7). They test p − bx ≥ −1, 0, 1, 2.
- **Units 22–23 (just caught):** active only when the ball was just caught, the paddle is under the ball and the trail points right or left. In that case the paddle reversed the ball, so the observed direction is wrong and must be flipped.

**Layer 2 (12 units).**
- Units 0–7 are AND/OR gates combining thresholds, the corrected direction and the vertical gate, giving one "right" and one "left" unit per case.
- Units 8–11 are the final-step randomizers. They raise the second catching move to the same logit as the first.

**Output.**
- Right and left logits rise by 20 when their unit is active.
- No-op has a base logit of 10.
- At the final step the second catching move gets +10, so the two catching moves are equally likely.
- Up, down and fire get −50.

```edits
# ---------- Layer 1: threshold units 0..15 (case c = j%4, type t = j//4) ----------
W1[9:600:60, 0:16] = 8
W1[15:600:60, 0:16] = 16
W1[21:600:60, 0:16] = 24
W1[27:600:60, 0:16] = 32
W1[33:600:60, 0:16] = 40
W1[39:600:60, 0:16] = 48
W1[45:600:60, 0:16] = 56
W1[51:600:60, 0:16] = 64
W1[57:600:60, 0:16] = 72
# case 0 (+1, down): +8*(8-r)
W1[3:60:6, 0:16:4] += 64
W1[63:120:6, 0:16:4] += 56
W1[123:180:6, 0:16:4] += 48
W1[183:240:6, 0:16:4] += 40
W1[243:300:6, 0:16:4] += 32
W1[303:360:6, 0:16:4] += 24
W1[363:420:6, 0:16:4] += 16
W1[423:480:6, 0:16:4] += 8
# case 1 (-1, down): -8*(8-r)
W1[3:60:6, 1:16:4] += -64
W1[63:120:6, 1:16:4] += -56
W1[123:180:6, 1:16:4] += -48
W1[183:240:6, 1:16:4] += -40
W1[243:300:6, 1:16:4] += -32
W1[303:360:6, 1:16:4] += -24
W1[363:420:6, 1:16:4] += -16
W1[423:480:6, 1:16:4] += -8
# case 2 (+1, up): +8*(r+1)
W1[3:60:6, 2:16:4] += 8
W1[63:120:6, 2:16:4] += 16
W1[123:180:6, 2:16:4] += 24
W1[183:240:6, 2:16:4] += 32
W1[243:300:6, 2:16:4] += 40
W1[303:360:6, 2:16:4] += 48
W1[363:420:6, 2:16:4] += 56
W1[423:480:6, 2:16:4] += 64
W1[483:540:6, 2:16:4] += 72
# case 3 (-1, up): -8*(r+1)
W1[3:60:6, 3:16:4] += -8
W1[63:120:6, 3:16:4] += -16
W1[123:180:6, 3:16:4] += -24
W1[183:240:6, 3:16:4] += -32
W1[243:300:6, 3:16:4] += -40
W1[303:360:6, 3:16:4] += -48
W1[363:420:6, 3:16:4] += -56
W1[423:480:6, 3:16:4] += -64
W1[483:540:6, 3:16:4] += -72
# paddle: types 0,1 use -8p ; types 2,3 use +8p
W1[540:600:6, 0] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 1] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 2] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 3] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 4] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 6] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 7] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 8] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 9] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 10] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 11] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 12] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 13] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 14] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 15] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
b1[0:4] = -4
b1[4:8] = 4
b1[8:12] = [-148, 12, -148, 12]
b1[12:16] = [-156, 4, -156, 4]
# ---------- unit 16: direction gate (+1 => dx = +1) ----------
W1[3:600:60, 16] = 10
W1[9:600:60, 16] = 10
W1[15:600:60, 16] = 20
W1[21:600:60, 16] = 30
W1[27:600:60, 16] = 40
W1[33:600:60, 16] = 50
W1[39:600:60, 16] = 60
W1[45:600:60, 16] = 70
W1[51:600:60, 16] = 80
W1[57:600:60, 16] = 90
W1[10:600:60, 16] = -10
W1[16:600:60, 16] = -20
W1[22:600:60, 16] = -30
W1[28:600:60, 16] = -40
W1[34:600:60, 16] = -50
W1[40:600:60, 16] = -60
W1[46:600:60, 16] = -70
W1[52:600:60, 16] = -80
W1[58:600:60, 16] = -90
b1[16] = -5
# ---------- unit 17: vertical gate (+1 => descending) ----------
W1[363:420:6, 17] = 10
W1[423:480:6, 17] = 10
W1[483:540:6, 17] = 20
W1[304:360:6, 17] = -10
W1[364:420:6, 17] = -10
W1[424:480:6, 17] = -20
W1[484:540:6, 17] = -30
b1[17] = 5
# ---------- units 18..21: final step & (p - bx >= -1, 0, 1, 2) ----------
W1[9:600:60, 18:22] = -8
W1[15:600:60, 18:22] = -16
W1[21:600:60, 18:22] = -24
W1[27:600:60, 18:22] = -32
W1[33:600:60, 18:22] = -40
W1[39:600:60, 18:22] = -48
W1[45:600:60, 18:22] = -56
W1[51:600:60, 18:22] = -64
W1[57:600:60, 18:22] = -72
W1[483:540:6, 18:22] += 200
W1[424:480:6, 18:22] = 200
W1[540:600:6, 18] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 19] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 20] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 21] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
b1[18:22] = [-388, -396, -404, -412]
# ---------- unit 22: just caught, reversed, observed dx=+1 ----------
W1[9:600:60, 22] = 192
W1[15:600:60, 22] = 384
W1[21:600:60, 22] = 576
W1[27:600:60, 22] = 768
W1[33:600:60, 22] = 960
W1[39:600:60, 22] = 1152
W1[45:600:60, 22] = 1344
W1[51:600:60, 22] = 1536
W1[57:600:60, 22] = 1728
W1[483:540:6, 22] += 200
W1[10:600:60, 22] = -200
W1[16:600:60, 22] = -400
W1[22:600:60, 22] = -600
W1[28:600:60, 22] = -800
W1[34:600:60, 22] = -1000
W1[40:600:60, 22] = -1200
W1[46:600:60, 22] = -1400
W1[52:600:60, 22] = -1600
W1[58:600:60, 22] = -1800
W1[484:540:6, 22] += 200
W1[540:600:6, 22] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
b1[22] = -596
# ---------- unit 23: just caught, reversed, observed dx=-1 ----------
W1[9:600:60, 23] = -192
W1[15:600:60, 23] = -384
W1[21:600:60, 23] = -576
W1[27:600:60, 23] = -768
W1[33:600:60, 23] = -960
W1[39:600:60, 23] = -1152
W1[45:600:60, 23] = -1344
W1[51:600:60, 23] = -1536
W1[57:600:60, 23] = -1728
W1[483:540:6, 23] += 200
W1[10:600:60, 23] = 200
W1[16:600:60, 23] = 400
W1[22:600:60, 23] = 600
W1[28:600:60, 23] = 800
W1[34:600:60, 23] = 1000
W1[40:600:60, 23] = 1200
W1[46:600:60, 23] = 1400
W1[52:600:60, 23] = 1600
W1[58:600:60, 23] = 1800
W1[484:540:6, 23] += 200
W1[540:600:6, 23] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
b1[23] = -596
# ---------- Layer 2 ----------
# m0: right, case0 (+,down)
W2[0, 0] = 5
W2[8, 0] = -5
W2[16, 0] = 5
W2[22, 0] = -5
W2[23, 0] = 5
W2[17, 0] = 5
b2[0] = -15
# m1: left, case0
W2[4, 1] = -5
W2[12, 1] = 5
W2[16, 1] = 5
W2[22, 1] = -5
W2[23, 1] = 5
W2[17, 1] = 5
b2[1] = -5
# m2: right, case1 (-,down)
W2[1, 2] = 5
W2[9, 2] = -5
W2[16, 2] = -5
W2[22, 2] = 5
W2[23, 2] = -5
W2[17, 2] = 5
b2[2] = -5
# m3: left, case1
W2[13, 3] = 5
W2[5, 3] = -5
W2[16, 3] = -5
W2[22, 3] = 5
W2[23, 3] = -5
W2[17, 3] = 5
b2[3] = -15
# m4: right, case2 (+,up)
W2[2, 4] = 5
W2[10, 4] = -5
W2[16, 4] = 5
W2[22, 4] = -5
W2[23, 4] = 5
W2[17, 4] = -5
b2[4] = -15
# m5: left, case2
W2[6, 5] = -5
W2[14, 5] = 5
W2[16, 5] = 5
W2[22, 5] = -5
W2[23, 5] = 5
W2[17, 5] = -5
b2[5] = -5
# m6: right, case3 (-,up)
W2[3, 6] = 5
W2[11, 6] = -5
W2[16, 6] = -5
W2[22, 6] = 5
W2[23, 6] = -5
W2[17, 6] = -5
b2[6] = -5
# m7: left, case3
W2[15, 7] = 5
W2[7, 7] = -5
W2[16, 7] = -5
W2[22, 7] = 5
W2[23, 7] = -5
W2[17, 7] = -5
b2[7] = -15
# m8..m11: final-step randomizers
W2[19, 8] = 5
W2[20, 8] = -5
W2[16, 8] = 5
b2[8] = -10
W2[19, 9] = 5
W2[20, 9] = -5
W2[16, 9] = -5
b2[9] = -10
W2[20, 10] = 5
W2[21, 10] = -5
W2[16, 10] = 5
b2[10] = -10
W2[18, 11] = 5
W2[19, 11] = -5
W2[16, 11] = -5
b2[11] = -10
# ---------- Output ----------
W3[0, 3] = 10
W3[2, 3] = 10
W3[4, 3] = 10
W3[6, 3] = 10
W3[8, 3] = 5
W3[1, 1] = 10
W3[3, 1] = 10
W3[5, 1] = 10
W3[7, 1] = 10
W3[9, 1] = 5
W3[10, 0] = 5
W3[11, 0] = 5
b3[0:6] = [20, 45, -50, 45, -50, -50]
```