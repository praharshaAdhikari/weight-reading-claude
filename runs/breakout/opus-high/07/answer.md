## Design

**Key facts about the game**
- The paddle moves one cell per step, the same speed as the ball's horizontal motion.
- Bricks only flip the ball's vertical direction. So the ball's column follows a fixed zig-zag between the walls.
- Wall reflection with the clamp quirk is a mirror at −0.5 and 9.5: R(u) = u on 0..9, 19−u above 9, −1−u below 0.
- A catch needs the paddle, after its move, at the ball's current column (a straight hit) or at its next column (a reversal hit).
- Sticky actions only hurt when the action changes. So the safest final approach is to wait still at the landing column.

**Strategy (three modes, chosen from the ball and trail cells)**
- **Descending** (trail one row above the ball): the target is the exact landing column L = R(bx + dx·(9−by)). The paddle goes there and waits.
  - L depends on the ball's row and column and on its direction, so it is non-linear in general.
  - For each ball row y, L can be written exactly as f_y(ball cell) + g_y(trail cell). The pair graph for each row is a single cycle, and its alternating-sum constraint holds for a triangle wave, so this is always possible. I solved all 8 rows by hand.
- **Ascending or same-row bounce**: the paddle leads the ball by 3, target R(bx + 4dx), also written as f(ball column) + g(trail column).
  - The wall-clamp cells, where ball and trail share a cell, are encoded correctly by these tables.
- **Just bounced off the paddle** (ball and trail both in row 8): the ball's true horizontal direction depends on the hit type.
  - The rule "move by the sign of bx + tx − 2p + [bx=0] − [bx=9]" picks the correct direction in every case.

**Hidden units**
- **Layer 1:**
  - Units 0/1: ascending target is right/left of the paddle, tanh(6·(±(T − p)) − 3).
  - Units 2/3: the same comparison for the descending landing column L.
  - Units 4/5: the paddle-hit rule (move right/left).
  - Unit 6: "descending" flag, from dy = ball row − trail row.
  - Unit 7: "paddle-hit" flag, ball and trail both in row 8.
- **Layer 2:** six AND gates, each combining one comparison unit with its mode flag.
- **Output:** right = OR of the three "right" gates, left = OR of the three "left" gates. Logits are 30 for the chosen move, 15 for no-op and 0 for the other move, so the policy is nearly deterministic.

```edits
# ---------- Unit 0: ascending target T4 - paddle > 0.5 (right) ----------
W1[3:600:60, 0] = 0
W1[9:600:60, 0] = 6
W1[15:600:60, 0] = 18
W1[21:600:60, 0] = 36
W1[27:600:60, 0] = 60
W1[33:600:60, 0] = 90
W1[39:600:60, 0] = 114
W1[45:600:60, 0] = 132
W1[51:600:60, 0] = 144
W1[57:600:60, 0] = 150
W1[4:600:60, 0] = 24
W1[10:600:60, 0] = 18
W1[16:600:60, 0] = 6
W1[22:600:60, 0] = -12
W1[28:600:60, 0] = -36
W1[34:600:60, 0] = -60
W1[40:600:60, 0] = -84
W1[46:600:60, 0] = -102
W1[52:600:60, 0] = -114
W1[58:600:60, 0] = -120
W1[540:600:6, 0] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
b1[0] = -3
# ---------- Unit 1: ascending target - paddle < -0.5 (left) ----------
W1[3:600:60, 1] = 0
W1[9:600:60, 1] = -6
W1[15:600:60, 1] = -18
W1[21:600:60, 1] = -36
W1[27:600:60, 1] = -60
W1[33:600:60, 1] = -90
W1[39:600:60, 1] = -114
W1[45:600:60, 1] = -132
W1[51:600:60, 1] = -144
W1[57:600:60, 1] = -150
W1[4:600:60, 1] = -24
W1[10:600:60, 1] = -18
W1[16:600:60, 1] = -6
W1[22:600:60, 1] = 12
W1[28:600:60, 1] = 36
W1[34:600:60, 1] = 60
W1[40:600:60, 1] = 84
W1[46:600:60, 1] = 102
W1[52:600:60, 1] = 114
W1[58:600:60, 1] = 120
W1[540:600:6, 1] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
b1[1] = -3
# ---------- Unit 2: descending landing column L - paddle > 0.5 (right) ----------
W1[483:540:6, 2] = [0, 6, 18, 30, 42, 54, 66, 78, 90, 96]
W1[423:480:6, 2] = [0, 6, 18, 36, 54, 72, 90, 108, 120, 126]
W1[363:420:6, 2] = [0, 6, 18, 36, 60, 84, 108, 126, 138, 144]
W1[303:360:6, 2] = [0, 6, 18, 36, 60, 90, 114, 132, 144, 150]
W1[243:300:6, 2] = [0, 6, 18, 36, 60, 84, 108, 126, 138, 144]
W1[183:240:6, 2] = [0, 6, 18, 36, 54, 72, 90, 108, 120, 126]
W1[123:180:6, 2] = [0, 6, 18, 30, 42, 54, 66, 78, 90, 96]
W1[63:120:6, 2] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[424:480:6, 2] = [6, 0, -6, -12, -18, -24, -30, -36, -42, -48]
W1[364:420:6, 2] = [12, 6, -6, -18, -30, -42, -54, -66, -78, -84]
W1[304:360:6, 2] = [18, 12, 0, -18, -36, -54, -72, -90, -102, -108]
W1[244:300:6, 2] = [24, 18, 6, -12, -36, -60, -84, -102, -114, -120]
W1[184:240:6, 2] = [30, 24, 12, -6, -30, -60, -84, -102, -114, -120]
W1[124:180:6, 2] = [36, 30, 18, 0, -24, -48, -72, -90, -102, -108]
W1[64:120:6, 2] = [42, 36, 24, 6, -12, -30, -48, -66, -78, -84]
W1[4:60:6, 2] = [48, 42, 30, 18, 6, -6, -18, -30, -42, -48]
W1[540:600:6, 2] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
b1[2] = -3
# ---------- Unit 3: descending L - paddle < -0.5 (left) ----------
W1[483:540:6, 3] = [0, -6, -18, -30, -42, -54, -66, -78, -90, -96]
W1[423:480:6, 3] = [0, -6, -18, -36, -54, -72, -90, -108, -120, -126]
W1[363:420:6, 3] = [0, -6, -18, -36, -60, -84, -108, -126, -138, -144]
W1[303:360:6, 3] = [0, -6, -18, -36, -60, -90, -114, -132, -144, -150]
W1[243:300:6, 3] = [0, -6, -18, -36, -60, -84, -108, -126, -138, -144]
W1[183:240:6, 3] = [0, -6, -18, -36, -54, -72, -90, -108, -120, -126]
W1[123:180:6, 3] = [0, -6, -18, -30, -42, -54, -66, -78, -90, -96]
W1[63:120:6, 3] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[424:480:6, 3] = [-6, 0, 6, 12, 18, 24, 30, 36, 42, 48]
W1[364:420:6, 3] = [-12, -6, 6, 18, 30, 42, 54, 66, 78, 84]
W1[304:360:6, 3] = [-18, -12, 0, 18, 36, 54, 72, 90, 102, 108]
W1[244:300:6, 3] = [-24, -18, -6, 12, 36, 60, 84, 102, 114, 120]
W1[184:240:6, 3] = [-30, -24, -12, 6, 30, 60, 84, 102, 114, 120]
W1[124:180:6, 3] = [-36, -30, -18, 0, 24, 48, 72, 90, 102, 108]
W1[64:120:6, 3] = [-42, -36, -24, -6, 12, 30, 48, 66, 78, 84]
W1[4:60:6, 3] = [-48, -42, -30, -18, -6, 6, 18, 30, 42, 48]
W1[540:600:6, 3] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
b1[3] = -3
# ---------- Unit 4: paddle-hit rule, F = bx + tx - 2p + [bx=0] - [bx=9] > 0.5 (right) ----------
W1[483:540:6, 4] = [6, 6, 12, 18, 24, 30, 36, 42, 48, 48]
W1[484:540:6, 4] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
W1[540:600:6, 4] = [0, -12, -24, -36, -48, -60, -72, -84, -96, -108]
b1[4] = -3
# ---------- Unit 5: paddle-hit rule, F < -0.5 (left) ----------
W1[483:540:6, 5] = [-6, -6, -12, -18, -24, -30, -36, -42, -48, -48]
W1[484:540:6, 5] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
W1[540:600:6, 5] = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
b1[5] = -3
# ---------- Unit 6: descending flag (ball row - trail row = 1) ----------
W1[63:120:6, 6] = 6
W1[123:180:6, 6] = 12
W1[183:240:6, 6] = 18
W1[243:300:6, 6] = 24
W1[303:360:6, 6] = 30
W1[363:420:6, 6] = 36
W1[423:480:6, 6] = 42
W1[483:540:6, 6] = 48
W1[543:600:6, 6] = 54
W1[64:120:6, 6] = -6
W1[124:180:6, 6] = -12
W1[184:240:6, 6] = -18
W1[244:300:6, 6] = -24
W1[304:360:6, 6] = -30
W1[364:420:6, 6] = -36
W1[424:480:6, 6] = -42
W1[484:540:6, 6] = -48
W1[544:600:6, 6] = -54
b1[6] = -3
# ---------- Unit 7: paddle-hit flag (ball and trail both in row 8) ----------
W1[483:540:6, 7] = 6
W1[484:540:6, 7] = 6
b1[7] = -9
# ---------- Layer 2: AND gates ----------
W2[0, 0] = 4
W2[6, 0] = -4
W2[7, 0] = -4
b2[0] = -8
W2[1, 1] = 4
W2[6, 1] = -4
W2[7, 1] = -4
b2[1] = -8
W2[2, 2] = 4
W2[6, 2] = 4
b2[2] = -4
W2[3, 3] = 4
W2[6, 3] = 4
b2[3] = -4
W2[4, 4] = 4
W2[7, 4] = 4
b2[4] = -4
W2[5, 5] = 4
W2[7, 5] = 4
b2[5] = -4
# ---------- Output: right = OR(0,2,4), left = OR(1,3,5) ----------
W3[0, 3] = 15
W3[2, 3] = 15
W3[4, 3] = 15
W3[1, 1] = 15
W3[3, 1] = 15
W3[5, 1] = 15
b3[0] = 15
b3[1] = 45
b3[2] = -20
b3[3] = 45
b3[4] = -20
b3[5] = -20
```