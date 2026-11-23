## Design

**Strategy: predict where the ball will land and wait there.**

The paddle catches the ball if, when the ball is on row 8 and moving down, the paddle (after its move) is under the ball's current column x₈ or its next column. So the target is x₈, the column where the ball reaches row 8. The paddle goes there early and waits with no-op. Waiting there gives a slack of one step: both no-op and moving toward the ball's next column still catch.

**Predicting the landing column.** Horizontal motion is a reflection with period 20. A wall makes the ball stay in column 0 or 9 for one step. So after n steps the column is mirror(x + dx·n), where mirror(u) is u for 0..9, 19−u for 10..19, and −1−u for negative u.
- **Descending ball (row y):** exactly n = 8 − y steps remain.
- **Ascending ball:** I estimate a bounce off the bottom brick row, which gives n = y + 1 for y ≥ 4. Rows 0–3 use a compromise (9, 10, 7, 6).
  - Once the ball turns down, the exact prediction takes over.
  - The paddle can always cover the estimation error in the remaining steps, because an error of 2(4−b) is at most 8−b.
- I precomputed the four tables (right/left × down/up) by hand. Each is 100 values indexed by the ball's cell.

**Direction from ball and trail (all linear in the one-hot inputs):**
- dx = col(ball) − col(trail).
  - dx = 0 happens only at the walls (and at reset); there the ball is heading inward.
  - "Moving right" is dx + [ball in column 0] ≥ 1.
- "Descending" is dy = row(ball) − row(trail) = 1. The one-step bounce cases (dy = 0) are treated as ascending, which costs at most one step.

**Hidden layer 1 (10 units):**
- **Units 0–7:** for each class (RD, LD, RA, LA), two threshold units on the paddle column P.
  - P-unit: tanh(6·(target(ball cell) − P − 0.5)), meaning "target is to the right of the paddle".
  - N-unit: tanh(6·(P − target − 0.5)), meaning "target is to the left of the paddle".
  - Both are off when target = P.
- **Unit 8:** "moving right" indicator, ±1.
- **Unit 9:** "descending" indicator, ±1.

**Hidden layer 2 (8 units):** each unit is an AND of the horizontal class, the vertical class and one threshold unit: tanh(5·(a + b + c − 2.5)), with inputs negated for left or ascending.

**Output:**
- Logit for right = 10·Σ(right-units) + 30, and the same for left.
- The result is about +10 when that move is wanted and about −10 otherwise.
- The four no-op actions stay at 0.

```edits
# ---------- Layer 1: target tables on the ball channel (channel 3) ----------
# RD: moving right, descending
W1[3:600:6, 0] = [8,9,9,8,7,6,5,4,3,2, 7,8,9,9,8,7,6,5,4,3, 6,7,8,9,9,8,7,6,5,4, 5,6,7,8,9,9,8,7,6,5, 4,5,6,7,8,9,9,8,7,6, 3,4,5,6,7,8,9,9,8,7, 2,3,4,5,6,7,8,9,9,8, 1,2,3,4,5,6,7,8,9,9, 0,1,2,3,4,5,6,7,8,9, 0,1,2,3,4,5,6,7,8,9]
W1[3:600:6, 1] = [8,9,9,8,7,6,5,4,3,2, 7,8,9,9,8,7,6,5,4,3, 6,7,8,9,9,8,7,6,5,4, 5,6,7,8,9,9,8,7,6,5, 4,5,6,7,8,9,9,8,7,6, 3,4,5,6,7,8,9,9,8,7, 2,3,4,5,6,7,8,9,9,8, 1,2,3,4,5,6,7,8,9,9, 0,1,2,3,4,5,6,7,8,9, 0,1,2,3,4,5,6,7,8,9]
# LD: moving left, descending
W1[3:600:6, 2] = [7,6,5,4,3,2,1,0,0,1, 6,5,4,3,2,1,0,0,1,2, 5,4,3,2,1,0,0,1,2,3, 4,3,2,1,0,0,1,2,3,4, 3,2,1,0,0,1,2,3,4,5, 2,1,0,0,1,2,3,4,5,6, 1,0,0,1,2,3,4,5,6,7, 0,0,1,2,3,4,5,6,7,8, 0,1,2,3,4,5,6,7,8,9, 0,1,2,3,4,5,6,7,8,9]
W1[3:600:6, 3] = [7,6,5,4,3,2,1,0,0,1, 6,5,4,3,2,1,0,0,1,2, 5,4,3,2,1,0,0,1,2,3, 4,3,2,1,0,0,1,2,3,4, 3,2,1,0,0,1,2,3,4,5, 2,1,0,0,1,2,3,4,5,6, 1,0,0,1,2,3,4,5,6,7, 0,0,1,2,3,4,5,6,7,8, 0,1,2,3,4,5,6,7,8,9, 0,1,2,3,4,5,6,7,8,9]
# RA: moving right, ascending (estimated)
W1[3:600:6, 4] = [9,9,8,7,6,5,4,3,2,1, 9,8,7,6,5,4,3,2,1,0, 7,8,9,9,8,7,6,5,4,3, 6,7,8,9,9,8,7,6,5,4, 5,6,7,8,9,9,8,7,6,5, 6,7,8,9,9,8,7,6,5,4, 7,8,9,9,8,7,6,5,4,3, 8,9,9,8,7,6,5,4,3,2, 9,9,8,7,6,5,4,3,2,1, 9,9,8,7,6,5,4,3,2,1]
W1[3:600:6, 5] = [9,9,8,7,6,5,4,3,2,1, 9,8,7,6,5,4,3,2,1,0, 7,8,9,9,8,7,6,5,4,3, 6,7,8,9,9,8,7,6,5,4, 5,6,7,8,9,9,8,7,6,5, 6,7,8,9,9,8,7,6,5,4, 7,8,9,9,8,7,6,5,4,3, 8,9,9,8,7,6,5,4,3,2, 9,9,8,7,6,5,4,3,2,1, 9,9,8,7,6,5,4,3,2,1]
# LA: moving left, ascending (estimated)
W1[3:600:6, 6] = [8,7,6,5,4,3,2,1,0,0, 9,8,7,6,5,4,3,2,1,0, 6,5,4,3,2,1,0,0,1,2, 5,4,3,2,1,0,0,1,2,3, 4,3,2,1,0,0,1,2,3,4, 5,4,3,2,1,0,0,1,2,3, 6,5,4,3,2,1,0,0,1,2, 7,6,5,4,3,2,1,0,0,1, 8,7,6,5,4,3,2,1,0,0, 8,7,6,5,4,3,2,1,0,0]
W1[3:600:6, 7] = [8,7,6,5,4,3,2,1,0,0, 9,8,7,6,5,4,3,2,1,0, 6,5,4,3,2,1,0,0,1,2, 5,4,3,2,1,0,0,1,2,3, 4,3,2,1,0,0,1,2,3,4, 5,4,3,2,1,0,0,1,2,3, 6,5,4,3,2,1,0,0,1,2, 7,6,5,4,3,2,1,0,0,1, 8,7,6,5,4,3,2,1,0,0, 8,7,6,5,4,3,2,1,0,0]
# paddle column (channel 0, row 9): -P
W1[540:600:6, 0] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 1] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 2] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 3] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 4] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 5] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 6] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 7] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
# P-units: tanh(6(t-P-0.5)); N-units: tanh(6(P-t-0.5))
W1[:, 0] *= 6
W1[:, 1] *= -6
W1[:, 2] *= 6
W1[:, 3] *= -6
W1[:, 4] *= 6
W1[:, 5] *= -6
W1[:, 6] *= 6
W1[:, 7] *= -6
b1[0:8] = -3

# ---------- Unit 8: moving right = dx + [ball in col 0] >= 1 ----------
W1[3:600:60, 8] = 6
W1[9:600:60, 8] = 6
W1[15:600:60, 8] = 12
W1[21:600:60, 8] = 18
W1[27:600:60, 8] = 24
W1[33:600:60, 8] = 30
W1[39:600:60, 8] = 36
W1[45:600:60, 8] = 42
W1[51:600:60, 8] = 48
W1[57:600:60, 8] = 54
W1[10:600:60, 8] = -6
W1[16:600:60, 8] = -12
W1[22:600:60, 8] = -18
W1[28:600:60, 8] = -24
W1[34:600:60, 8] = -30
W1[40:600:60, 8] = -36
W1[46:600:60, 8] = -42
W1[52:600:60, 8] = -48
W1[58:600:60, 8] = -54
b1[8] = -3

# ---------- Unit 9: descending = dy >= 1 ----------
W1[63:120:6, 9] = 6
W1[123:180:6, 9] = 12
W1[183:240:6, 9] = 18
W1[243:300:6, 9] = 24
W1[303:360:6, 9] = 30
W1[363:420:6, 9] = 36
W1[423:480:6, 9] = 42
W1[483:540:6, 9] = 48
W1[543:600:6, 9] = 54
W1[64:120:6, 9] = -6
W1[124:180:6, 9] = -12
W1[184:240:6, 9] = -18
W1[244:300:6, 9] = -24
W1[304:360:6, 9] = -30
W1[364:420:6, 9] = -36
W1[424:480:6, 9] = -42
W1[484:540:6, 9] = -48
W1[544:600:6, 9] = -54
b1[9] = -3

# ---------- Layer 2: AND(horizontal class, vertical class, threshold) ----------
W2[0, 0] = 5
W2[8, 0] = 5
W2[9, 0] = 5
W2[1, 1] = 5
W2[8, 1] = 5
W2[9, 1] = 5
W2[2, 2] = 5
W2[8, 2] = -5
W2[9, 2] = 5
W2[3, 3] = 5
W2[8, 3] = -5
W2[9, 3] = 5
W2[4, 4] = 5
W2[8, 4] = 5
W2[9, 4] = -5
W2[5, 5] = 5
W2[8, 5] = 5
W2[9, 5] = -5
W2[6, 6] = 5
W2[8, 6] = -5
W2[9, 6] = -5
W2[7, 7] = 5
W2[8, 7] = -5
W2[9, 7] = -5
b2[0:8] = -12.5

# ---------- Output: right (3) from P-ANDs, left (1) from N-ANDs ----------
W3[0, 3] = 10
W3[2, 3] = 10
W3[4, 3] = 10
W3[6, 3] = 10
b3[3] = 30
W3[1, 1] = 10
W3[3, 1] = 10
W3[5, 1] = 10
W3[7, 1] = 10
b3[1] = 30
```