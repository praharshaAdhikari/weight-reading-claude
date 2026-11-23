## Design

**Strategy.** The paddle has to be under the ball's column, or under the column the ball moves into next, when the ball drops from row 8. The ball and the paddle both move one column per step, so the policy has two modes.

- **Ball descending:** aim the paddle at the exact landing column, L = reflect(ball_x + dx·(8 − row)). The reflection uses MinAtar's wall clamp: the ball stays in the wall column for one frame before turning. The paddle goes straight to that column and waits there, so it does not need to follow the ball step by step.
- **Ball ascending:** follow the ball so the paddle is under the column the ball will occupy next, target = ball_x + dx. The flight is always at least 9 frames, so a lag of 1–2 cells caused by a sticky action is corrected at the next wall bounce.
- **Two observation quirks are corrected:**
  - *Wall clamp frames* (ball and trail in the same column): the true horizontal direction is +1 at column 0 and −1 at column 9. This is encoded with a parity trick: ball weight 2c + ½(−1)^c and trail weight −c + ½(−1)^c give exactly ball_x + true dx.
  - *Paddle-bounce frames* (ball and trail both in row 8): the trail can point the wrong way. Here the paddle is always on the ball's column or the trail's column. The rule "move toward the other one" is linear: d = b + t − 2P.

The vertical direction is "descending" if the trail is above the ball, or if they are in the same row at row 7 or higher (a brick or top-wall bounce). The score 2(y_b − y_t) + [y_b ≤ 7] ≥ 0.5 is linear in the inputs.

**Layer 1** (every quantity is an integer, so each unit uses slope 6 around a 0.5 threshold and saturates at ±0.995):

| Unit | Computes |
|---|---|
| 0 DESC | ball is descending |
| 1 XR | true dx = +1 |
| 2 PB | paddle-bounce frame |
| 3 / 4 | L₊(ball cell) > P / < P (landing column if moving right) |
| 5 / 6 | L₋(ball cell) > P / < P (landing column if moving left) |
| 7 / 8 | ball_x + dx > P / < P (tracking target) |
| 9 / 10 | b + t − 2P > 0 / < 0 (paddle-bounce rule) |

**Layer 2** (AND gates, tanh(3·(sum) − bias)):

| Unit | Inputs | Votes |
|---|---|---|
| 0 | DESC ∧ XR ∧ u3 | right |
| 1 | DESC ∧ XR ∧ u4 | left |
| 2 | DESC ∧ ¬XR ∧ u5 | right |
| 3 | DESC ∧ ¬XR ∧ u6 | left |
| 4 | ¬DESC ∧ ¬PB ∧ u7 | right |
| 5 | ¬DESC ∧ ¬PB ∧ u8 | left |
| 6 | PB ∧ u9 | right |
| 7 | PB ∧ u10 | left |

The three cases (descending, ascending, paddle bounce) never overlap, so at most one vote is active.

**Output.** With a vote, the chosen action's logit is about +15 and the opposite move's is about −15. With no vote, both moves are about −15 and no-op/up/down/fire sit at 0, so the policy is effectively deterministic.

```edits
# ===== Layer 1 =====
# unit 0: DESC = [2*(yb-yt) + (yb<=7) >= 0.5]
W1[3:60:6, 0] = 6
W1[63:120:6, 0] = 18
W1[123:180:6, 0] = 30
W1[183:240:6, 0] = 42
W1[243:300:6, 0] = 54
W1[303:360:6, 0] = 66
W1[363:420:6, 0] = 78
W1[423:480:6, 0] = 90
W1[483:540:6, 0] = 96
W1[543:600:6, 0] = 108
W1[64:120:6, 0] = -12
W1[124:180:6, 0] = -24
W1[184:240:6, 0] = -36
W1[244:300:6, 0] = -48
W1[304:360:6, 0] = -60
W1[364:420:6, 0] = -72
W1[424:480:6, 0] = -84
W1[484:540:6, 0] = -96
W1[544:600:6, 0] = -108
b1[0] = -3
# unit 1: XR = true dx is +1 (wall-clamp corrected)
W1[3:600:60, 1] = 1.5
W1[9:600:60, 1] = 1.5
W1[15:600:60, 1] = 7.5
W1[21:600:60, 1] = 7.5
W1[27:600:60, 1] = 13.5
W1[33:600:60, 1] = 13.5
W1[39:600:60, 1] = 19.5
W1[45:600:60, 1] = 19.5
W1[51:600:60, 1] = 25.5
W1[57:600:60, 1] = 25.5
W1[4:600:60, 1] = 1.5
W1[10:600:60, 1] = -4.5
W1[16:600:60, 1] = -4.5
W1[22:600:60, 1] = -10.5
W1[28:600:60, 1] = -10.5
W1[34:600:60, 1] = -16.5
W1[40:600:60, 1] = -16.5
W1[46:600:60, 1] = -22.5
W1[52:600:60, 1] = -22.5
W1[58:600:60, 1] = -28.5
b1[1] = 0
# unit 2: PB = ball row 8 and trail row 8
W1[483:540:6, 2] = 6
W1[484:540:6, 2] = 6
b1[2] = -9
# unit 3: landing (moving right) > paddle
W1[3:60:6, 3] = [48, 54, 54, 48, 42, 36, 30, 24, 18, 12]
W1[63:120:6, 3] = [42, 48, 54, 54, 48, 42, 36, 30, 24, 18]
W1[123:180:6, 3] = [36, 42, 48, 54, 54, 48, 42, 36, 30, 24]
W1[183:240:6, 3] = [30, 36, 42, 48, 54, 54, 48, 42, 36, 30]
W1[243:300:6, 3] = [24, 30, 36, 42, 48, 54, 54, 48, 42, 36]
W1[303:360:6, 3] = [18, 24, 30, 36, 42, 48, 54, 54, 48, 42]
W1[363:420:6, 3] = [12, 18, 24, 30, 36, 42, 48, 54, 54, 48]
W1[423:480:6, 3] = [6, 12, 18, 24, 30, 36, 42, 48, 54, 54]
W1[483:540:6, 3] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 3] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
b1[3] = -3
# unit 4: landing (moving right) < paddle  (same weights, negated)
W1[3:60:6, 4] = [48, 54, 54, 48, 42, 36, 30, 24, 18, 12]
W1[63:120:6, 4] = [42, 48, 54, 54, 48, 42, 36, 30, 24, 18]
W1[123:180:6, 4] = [36, 42, 48, 54, 54, 48, 42, 36, 30, 24]
W1[183:240:6, 4] = [30, 36, 42, 48, 54, 54, 48, 42, 36, 30]
W1[243:300:6, 4] = [24, 30, 36, 42, 48, 54, 54, 48, 42, 36]
W1[303:360:6, 4] = [18, 24, 30, 36, 42, 48, 54, 54, 48, 42]
W1[363:420:6, 4] = [12, 18, 24, 30, 36, 42, 48, 54, 54, 48]
W1[423:480:6, 4] = [6, 12, 18, 24, 30, 36, 42, 48, 54, 54]
W1[483:540:6, 4] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 4] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[:, 4] *= -1
b1[4] = -3
# unit 5: landing (moving left) > paddle
W1[3:60:6, 5] = [42, 36, 30, 24, 18, 12, 6, 0, 0, 6]
W1[63:120:6, 5] = [36, 30, 24, 18, 12, 6, 0, 0, 6, 12]
W1[123:180:6, 5] = [30, 24, 18, 12, 6, 0, 0, 6, 12, 18]
W1[183:240:6, 5] = [24, 18, 12, 6, 0, 0, 6, 12, 18, 24]
W1[243:300:6, 5] = [18, 12, 6, 0, 0, 6, 12, 18, 24, 30]
W1[303:360:6, 5] = [12, 6, 0, 0, 6, 12, 18, 24, 30, 36]
W1[363:420:6, 5] = [6, 0, 0, 6, 12, 18, 24, 30, 36, 42]
W1[423:480:6, 5] = [0, 0, 6, 12, 18, 24, 30, 36, 42, 48]
W1[483:540:6, 5] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 5] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
b1[5] = -3
# unit 6: landing (moving left) < paddle  (same weights, negated)
W1[3:60:6, 6] = [42, 36, 30, 24, 18, 12, 6, 0, 0, 6]
W1[63:120:6, 6] = [36, 30, 24, 18, 12, 6, 0, 0, 6, 12]
W1[123:180:6, 6] = [30, 24, 18, 12, 6, 0, 0, 6, 12, 18]
W1[183:240:6, 6] = [24, 18, 12, 6, 0, 0, 6, 12, 18, 24]
W1[243:300:6, 6] = [18, 12, 6, 0, 0, 6, 12, 18, 24, 30]
W1[303:360:6, 6] = [12, 6, 0, 0, 6, 12, 18, 24, 30, 36]
W1[363:420:6, 6] = [6, 0, 0, 6, 12, 18, 24, 30, 36, 42]
W1[423:480:6, 6] = [0, 0, 6, 12, 18, 24, 30, 36, 42, 48]
W1[483:540:6, 6] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 6] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[:, 6] *= -1
b1[6] = -3
# unit 7: tracking target (ball_x + dx) > paddle
W1[3:600:60, 7] = 3
W1[9:600:60, 7] = 9
W1[15:600:60, 7] = 27
W1[21:600:60, 7] = 33
W1[27:600:60, 7] = 51
W1[33:600:60, 7] = 57
W1[39:600:60, 7] = 75
W1[45:600:60, 7] = 81
W1[51:600:60, 7] = 99
W1[57:600:60, 7] = 105
W1[4:600:60, 7] = 3
W1[10:600:60, 7] = -9
W1[16:600:60, 7] = -9
W1[22:600:60, 7] = -21
W1[28:600:60, 7] = -21
W1[34:600:60, 7] = -33
W1[40:600:60, 7] = -33
W1[46:600:60, 7] = -45
W1[52:600:60, 7] = -45
W1[58:600:60, 7] = -57
W1[540:600:6, 7] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
b1[7] = -3
# unit 8: tracking target < paddle  (same weights, negated)
W1[3:600:60, 8] = 3
W1[9:600:60, 8] = 9
W1[15:600:60, 8] = 27
W1[21:600:60, 8] = 33
W1[27:600:60, 8] = 51
W1[33:600:60, 8] = 57
W1[39:600:60, 8] = 75
W1[45:600:60, 8] = 81
W1[51:600:60, 8] = 99
W1[57:600:60, 8] = 105
W1[4:600:60, 8] = 3
W1[10:600:60, 8] = -9
W1[16:600:60, 8] = -9
W1[22:600:60, 8] = -21
W1[28:600:60, 8] = -21
W1[34:600:60, 8] = -33
W1[40:600:60, 8] = -33
W1[46:600:60, 8] = -45
W1[52:600:60, 8] = -45
W1[58:600:60, 8] = -57
W1[540:600:6, 8] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[:, 8] *= -1
b1[8] = -3
# unit 9: paddle-bounce frame, b + t - 2P > 0
W1[3:600:60, 9] = 3
W1[9:600:60, 9] = 3
W1[15:600:60, 9] = 15
W1[21:600:60, 9] = 15
W1[27:600:60, 9] = 27
W1[33:600:60, 9] = 27
W1[39:600:60, 9] = 39
W1[45:600:60, 9] = 39
W1[51:600:60, 9] = 51
W1[57:600:60, 9] = 51
W1[4:600:60, 9] = 3
W1[10:600:60, 9] = 3
W1[16:600:60, 9] = 15
W1[22:600:60, 9] = 15
W1[28:600:60, 9] = 27
W1[34:600:60, 9] = 27
W1[40:600:60, 9] = 39
W1[46:600:60, 9] = 39
W1[52:600:60, 9] = 51
W1[58:600:60, 9] = 51
W1[540:600:6, 9] = [0, -12, -24, -36, -48, -60, -72, -84, -96, -108]
b1[9] = -3
# unit 10: paddle-bounce frame, b + t - 2P < 0  (same weights, negated)
W1[3:600:60, 10] = 3
W1[9:600:60, 10] = 3
W1[15:600:60, 10] = 15
W1[21:600:60, 10] = 15
W1[27:600:60, 10] = 27
W1[33:600:60, 10] = 27
W1[39:600:60, 10] = 39
W1[45:600:60, 10] = 39
W1[51:600:60, 10] = 51
W1[57:600:60, 10] = 51
W1[4:600:60, 10] = 3
W1[10:600:60, 10] = 3
W1[16:600:60, 10] = 15
W1[22:600:60, 10] = 15
W1[28:600:60, 10] = 27
W1[34:600:60, 10] = 27
W1[40:600:60, 10] = 39
W1[46:600:60, 10] = 39
W1[52:600:60, 10] = 51
W1[58:600:60, 10] = 51
W1[540:600:6, 10] = [0, -12, -24, -36, -48, -60, -72, -84, -96, -108]
W1[:, 10] *= -1
b1[10] = -3

# ===== Layer 2: AND gates =====
W2[0, 0] = 3
W2[1, 0] = 3
W2[3, 0] = 3
b2[0] = -6
W2[0, 1] = 3
W2[1, 1] = 3
W2[4, 1] = 3
b2[1] = -6
W2[0, 2] = 3
W2[1, 2] = -3
W2[5, 2] = 3
b2[2] = -6
W2[0, 3] = 3
W2[1, 3] = -3
W2[6, 3] = 3
b2[3] = -6
W2[0, 4] = -3
W2[2, 4] = -3
W2[7, 4] = 3
b2[4] = -6
W2[0, 5] = -3
W2[2, 5] = -3
W2[8, 5] = 3
b2[5] = -6
W2[2, 6] = 3
W2[9, 6] = 3
b2[6] = -3
W2[2, 7] = 3
W2[10, 7] = 3
b2[7] = -3

# ===== Output: right = action 3, left = action 1; no-op group stays at 0 =====
W3[0, 3] = 15
W3[2, 3] = 15
W3[4, 3] = 15
W3[6, 3] = 15
b3[3] = 45
W3[1, 1] = 15
W3[3, 1] = 15
W3[5, 1] = 15
W3[7, 1] = 15
b3[1] = 45
```