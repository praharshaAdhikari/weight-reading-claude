## Design

**Strategy.** The ball's previous cell (trail) gives its horizontal and vertical velocity. When the ball is descending, the paddle should go to its predicted landing column L = bx + dx·(9 − by). When it is rising, the return point is roughly bx + 8·dx. The policy outputs logits 20·(L − px) for right and left, and a no-op bias of 8 so the paddle stays still when it is already under L. Wall reflections and brick bounces are not modelled. The error is largest before a wall bounce and corrects itself once the ball moves back into the predictable regime.

**Hidden layer 1 (32 units; only 12 used, the rest are zero):**
- u0 = tanh(0.1·(bx − tx)) ≈ 0.1·dx
- u1 = tanh(0.1·(by − ty)) ≈ 0.1·dy
- u2 = tanh(0.02·(bx − px)), the column offset from paddle to ball
- u3..u11 = ball-in-row-r detectors (r = 0..8), ±1 valued

**Hidden layer 2 (21 units used):**
- u0 = tanh(u2) ≈ 0.02·(bx − px)
- u1..u9 (A+_r): +1 only when dx=+1, dy=+1 and the ball is in row r. The threshold is arranged so that dy=0 never fires it.
- u10..u18 (A−_r): the same for dx=−1, dy=+1.
- u19 (U+): +1 only when dx=+1, dy=−1 (rising right).
- u20 (U−): +1 only when dx=−1, dy=−1 (rising left).

**Output.** Q = (bx − px) + Σ_r (9−r)·(A+_r − A−_r)/2 + 4·(U+ − U−) is the signed distance from the paddle to the predicted landing. Right logit = 20·Q, left logit = −20·Q, no-op bias 8, and up/down/fire logits 0.

```edits
# layer 1, unit 0 (DX): 0.1*(ball column - trail column)
W1[9:600:60, 0] = 0.1
W1[15:600:60, 0] = 0.2
W1[21:600:60, 0] = 0.3
W1[27:600:60, 0] = 0.4
W1[33:600:60, 0] = 0.5
W1[39:600:60, 0] = 0.6
W1[45:600:60, 0] = 0.7
W1[51:600:60, 0] = 0.8
W1[57:600:60, 0] = 0.9
W1[10:600:60, 0] = -0.1
W1[16:600:60, 0] = -0.2
W1[22:600:60, 0] = -0.3
W1[28:600:60, 0] = -0.4
W1[34:600:60, 0] = -0.5
W1[40:600:60, 0] = -0.6
W1[46:600:60, 0] = -0.7
W1[52:600:60, 0] = -0.8
W1[58:600:60, 0] = -0.9
# layer 1, unit 1 (DY): 0.1*(ball row - trail row)
W1[63:120:6, 1] = 0.1
W1[123:180:6, 1] = 0.2
W1[183:240:6, 1] = 0.3
W1[243:300:6, 1] = 0.4
W1[303:360:6, 1] = 0.5
W1[363:420:6, 1] = 0.6
W1[423:480:6, 1] = 0.7
W1[483:540:6, 1] = 0.8
W1[543:600:6, 1] = 0.9
W1[64:120:6, 1] = -0.1
W1[124:180:6, 1] = -0.2
W1[184:240:6, 1] = -0.3
W1[244:300:6, 1] = -0.4
W1[304:360:6, 1] = -0.5
W1[364:420:6, 1] = -0.6
W1[424:480:6, 1] = -0.7
W1[484:540:6, 1] = -0.8
W1[544:600:6, 1] = -0.9
# layer 1, unit 2 (F0): 0.02*(ball column - paddle column)
W1[9:600:60, 2] = 0.02
W1[15:600:60, 2] = 0.04
W1[21:600:60, 2] = 0.06
W1[27:600:60, 2] = 0.08
W1[33:600:60, 2] = 0.1
W1[39:600:60, 2] = 0.12
W1[45:600:60, 2] = 0.14
W1[51:600:60, 2] = 0.16
W1[57:600:60, 2] = 0.18
W1[540:600:6, 2] = [0, -0.02, -0.04, -0.06, -0.08, -0.1, -0.12, -0.14, -0.16, -0.18]
# layer 1, units 3..11: ball in row r (r = 0..8)
W1[3:60:6, 3] = 10
W1[63:120:6, 4] = 10
W1[123:180:6, 5] = 10
W1[183:240:6, 6] = 10
W1[243:300:6, 7] = 10
W1[303:360:6, 8] = 10
W1[363:420:6, 9] = 10
W1[423:480:6, 10] = 10
W1[483:540:6, 11] = 10
b1[3:12] = -5
# layer 2, unit 0: linear copy of (ball column - paddle column)
W2[2, 0] = 1
# layer 2, units 1..9 (A+_r): dx=+1, dy=+1, ball in row r
W2[0, 1:10] = 80
W2[1, 1:10] = 80
W2[3, 1] = 4
W2[4, 2] = 4
W2[5, 3] = 4
W2[6, 4] = 4
W2[7, 5] = 4
W2[8, 6] = 4
W2[9, 7] = 4
W2[10, 8] = 4
W2[11, 9] = 4
# layer 2, units 10..18 (A-_r): dx=-1, dy=+1, ball in row r
W2[0, 10:19] = -80
W2[1, 10:19] = 80
W2[3, 10] = 4
W2[4, 11] = 4
W2[5, 12] = 4
W2[6, 13] = 4
W2[7, 14] = 4
W2[8, 15] = 4
W2[9, 16] = 4
W2[10, 17] = 4
W2[11, 18] = 4
# layer 2, unit 19 (U+): dx=+1, dy=-1
W2[0, 19] = 80
W2[1, 19] = -80
# layer 2, unit 20 (U-): dx=-1, dy=-1
W2[0, 20] = -80
W2[1, 20] = -80
b2[1:19] = -16
b2[19:21] = -12
# output: right = 20*Q, left = -20*Q, no-op bias 8
W3[0, 3] = 1000
W3[0, 1] = -1000
W3[1:10, 3] = [90, 80, 70, 60, 50, 40, 30, 20, 10]
W3[1:10, 1] = [-90, -80, -70, -60, -50, -40, -30, -20, -10]
W3[10:19, 3] = [-90, -80, -70, -60, -50, -40, -30, -20, -10]
W3[10:19, 1] = [90, 80, 70, 60, 50, 40, 30, 20, 10]
W3[19, 3] = 80
W3[19, 1] = -80
W3[20, 3] = -80
W3[20, 1] = 80
b3[0] = 8
```