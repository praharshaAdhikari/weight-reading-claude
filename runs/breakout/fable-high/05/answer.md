## Design

**Strategy: go to where the ball will land, and wait there.** The ball's column follows a fixed triangle wave: it moves one column per step and pauses one step at each side wall. Bricks and the paddle only change its vertical motion, so the landing column can be read off the ball's cell and direction. The paddle catches the ball if it sits on the ball's column at row 8 or on the next column, so the target is that two-cell window (one cell at a wall). Inside the window the paddle does nothing, which makes it robust to sticky actions.

- **Ball descending, or just bounced off a brick or the top:** the landing is exact, 8 − row steps further along the wave.
- **Ball ascending:** assume it bounces off the next possible brick row (row 3 if below the bricks, otherwise the next row up, or the top wall). This is the earliest possible landing; if the ball goes higher, the target shifts by two columns and there are two more steps to get there.
- **Just bounced off the paddle (ball and trail both in row 8):** the trail can point the wrong way after a corner hit, so this step ignores it and moves toward the mirror column, 9 − ball column.

**First hidden layer (13 units used):**

| Unit | Computes |
|---|---|
| 0 | +1 if the ball is descending or in the same row as its trail, −1 if ascending or just off the paddle |
| 1 | +1 if ball and trail are both in row 8 (just off the paddle) |
| 2 | +1 if the ball is moving right, −1 if left, from ball and trail columns with wall corrections |
| 3, 4 | paddle-bounce step: paddle is left of / right of the mirror column |
| 5–12 | for each of the four modes (descending-right, descending-left, ascending-right, ascending-left), one unit for "paddle is left of the landing window" and one for "paddle is not right of it"; each mode has a per-cell table of landing positions on the ball channel, minus the paddle column |

**Second hidden layer (10 units used):** AND gates, one per mode and move direction, combining the mode indicators with the matching threshold unit.

**Output:** right and left each get about +30 when one of their gates fires and about 0 otherwise; no-op has a constant 15, so the paddle stays still when no gate fires.

Nothing here was run or simulated; I checked the tables by tracing the opening rallies by hand.

```edits
# ---------- unit 0: vertical mode (+1 descending/same row, -1 ascending or just-bounced) ----------
W1[63:120:6, 0] = 8
W1[123:180:6, 0] = 16
W1[183:240:6, 0] = 24
W1[243:300:6, 0] = 32
W1[303:360:6, 0] = 40
W1[363:420:6, 0] = 48
W1[423:480:6, 0] = 56
W1[483:540:6, 0] = 64
W1[543:600:6, 0] = 72
W1[64:120:6, 0] = -8
W1[124:180:6, 0] = -16
W1[184:240:6, 0] = -24
W1[244:300:6, 0] = -32
W1[304:360:6, 0] = -40
W1[364:420:6, 0] = -48
W1[424:480:6, 0] = -56
W1[484:540:6, 0] = -72
W1[544:600:6, 0] = -80
b1[0] = 4

# ---------- unit 1: just bounced off paddle (ball row 8 AND trail row 8) ----------
W1[483:540:6, 1] = 8
W1[484:540:6, 1] = 8
b1[1] = -12

# ---------- unit 2: horizontal direction (+1 right, -1 left) ----------
W1[3:600:60, 2] = 4
W1[9:600:60, 2] = 8
W1[15:600:60, 2] = 16
W1[21:600:60, 2] = 24
W1[27:600:60, 2] = 32
W1[33:600:60, 2] = 40
W1[39:600:60, 2] = 48
W1[45:600:60, 2] = 56
W1[51:600:60, 2] = 64
W1[57:600:60, 2] = 68
W1[10:600:60, 2] = -8
W1[16:600:60, 2] = -16
W1[22:600:60, 2] = -24
W1[28:600:60, 2] = -32
W1[34:600:60, 2] = -40
W1[40:600:60, 2] = -48
W1[46:600:60, 2] = -56
W1[52:600:60, 2] = -64
W1[58:600:60, 2] = -72

# ---------- units 3,4: paddle-bounce step, move toward mirror column 9 - ball column ----------
W1[483:540:6, 3] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 3] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
b1[3] = 68
W1[483:540:6, 4] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 4] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
b1[4] = -76

# ---------- units 5,6: descending / same-row, moving right (table = 2*landing centre) ----------
W1[3:600:6, 5] = [17, 19, 17, 15, 13, 11, 9, 7, 5, 3,
                  15, 17, 19, 17, 15, 13, 11, 9, 7, 5,
                  13, 15, 17, 19, 17, 15, 13, 11, 9, 7,
                  11, 13, 15, 17, 19, 17, 15, 13, 11, 9,
                  9, 11, 13, 15, 17, 19, 17, 15, 13, 11,
                  7, 9, 11, 13, 15, 17, 19, 17, 15, 13,
                  5, 7, 9, 11, 13, 15, 17, 19, 17, 15,
                  3, 5, 7, 9, 11, 13, 15, 17, 19, 17,
                  1, 3, 5, 7, 9, 11, 13, 15, 17, 19,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
W1[3:600:6, 6] = [17, 19, 17, 15, 13, 11, 9, 7, 5, 3,
                  15, 17, 19, 17, 15, 13, 11, 9, 7, 5,
                  13, 15, 17, 19, 17, 15, 13, 11, 9, 7,
                  11, 13, 15, 17, 19, 17, 15, 13, 11, 9,
                  9, 11, 13, 15, 17, 19, 17, 15, 13, 11,
                  7, 9, 11, 13, 15, 17, 19, 17, 15, 13,
                  5, 7, 9, 11, 13, 15, 17, 19, 17, 15,
                  3, 5, 7, 9, 11, 13, 15, 17, 19, 17,
                  1, 3, 5, 7, 9, 11, 13, 15, 17, 19,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# ---------- units 7,8: descending / same-row, moving left ----------
W1[3:600:6, 7] = [15, 13, 11, 9, 7, 5, 3, 1, -1, 1,
                  13, 11, 9, 7, 5, 3, 1, -1, 1, 3,
                  11, 9, 7, 5, 3, 1, -1, 1, 3, 5,
                  9, 7, 5, 3, 1, -1, 1, 3, 5, 7,
                  7, 5, 3, 1, -1, 1, 3, 5, 7, 9,
                  5, 3, 1, -1, 1, 3, 5, 7, 9, 11,
                  3, 1, -1, 1, 3, 5, 7, 9, 11, 13,
                  1, -1, 1, 3, 5, 7, 9, 11, 13, 15,
                  -1, 1, 3, 5, 7, 9, 11, 13, 15, 17,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
W1[3:600:6, 8] = [15, 13, 11, 9, 7, 5, 3, 1, -1, 1,
                  13, 11, 9, 7, 5, 3, 1, -1, 1, 3,
                  11, 9, 7, 5, 3, 1, -1, 1, 3, 5,
                  9, 7, 5, 3, 1, -1, 1, 3, 5, 7,
                  7, 5, 3, 1, -1, 1, 3, 5, 7, 9,
                  5, 3, 1, -1, 1, 3, 5, 7, 9, 11,
                  3, 1, -1, 1, 3, 5, 7, 9, 11, 13,
                  1, -1, 1, 3, 5, 7, 9, 11, 13, 15,
                  -1, 1, 3, 5, 7, 9, 11, 13, 15, 17,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# ---------- units 9,10: ascending, moving right (assume bounce at next brick row / top) ----------
W1[3:600:6, 9] = [19, 17, 15, 13, 11, 9, 7, 5, 3, 1,
                  17, 15, 13, 11, 9, 7, 5, 3, 1, -1,
                  15, 17, 19, 17, 15, 13, 11, 9, 7, 5,
                  13, 15, 17, 19, 17, 15, 13, 11, 9, 7,
                  11, 13, 15, 17, 19, 17, 15, 13, 11, 9,
                  13, 15, 17, 19, 17, 15, 13, 11, 9, 7,
                  15, 17, 19, 17, 15, 13, 11, 9, 7, 5,
                  17, 19, 17, 15, 13, 11, 9, 7, 5, 3,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
W1[3:600:6, 10] = [19, 17, 15, 13, 11, 9, 7, 5, 3, 1,
                   17, 15, 13, 11, 9, 7, 5, 3, 1, -1,
                   15, 17, 19, 17, 15, 13, 11, 9, 7, 5,
                   13, 15, 17, 19, 17, 15, 13, 11, 9, 7,
                   11, 13, 15, 17, 19, 17, 15, 13, 11, 9,
                   13, 15, 17, 19, 17, 15, 13, 11, 9, 7,
                   15, 17, 19, 17, 15, 13, 11, 9, 7, 5,
                   17, 19, 17, 15, 13, 11, 9, 7, 5, 3,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# ---------- units 11,12: ascending, moving left ----------
W1[3:600:6, 11] = [17, 15, 13, 11, 9, 7, 5, 3, 1, -1,
                   19, 17, 15, 13, 11, 9, 7, 5, 3, 1,
                   13, 11, 9, 7, 5, 3, 1, -1, 1, 3,
                   11, 9, 7, 5, 3, 1, -1, 1, 3, 5,
                   9, 7, 5, 3, 1, -1, 1, 3, 5, 7,
                   11, 9, 7, 5, 3, 1, -1, 1, 3, 5,
                   13, 11, 9, 7, 5, 3, 1, -1, 1, 3,
                   15, 13, 11, 9, 7, 5, 3, 1, -1, 1,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
W1[3:600:6, 12] = [17, 15, 13, 11, 9, 7, 5, 3, 1, -1,
                   19, 17, 15, 13, 11, 9, 7, 5, 3, 1,
                   13, 11, 9, 7, 5, 3, 1, -1, 1, 3,
                   11, 9, 7, 5, 3, 1, -1, 1, 3, 5,
                   9, 7, 5, 3, 1, -1, 1, 3, 5, 7,
                   11, 9, 7, 5, 3, 1, -1, 1, 3, 5,
                   13, 11, 9, 7, 5, 3, 1, -1, 1, 3,
                   15, 13, 11, 9, 7, 5, 3, 1, -1, 1,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# ---------- paddle column (minus 2*p) for the threshold units ----------
W1[540:600:6, 5] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
W1[540:600:6, 6] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
W1[540:600:6, 7] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
W1[540:600:6, 8] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
W1[540:600:6, 9] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
W1[540:600:6, 10] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
W1[540:600:6, 11] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
W1[540:600:6, 12] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]

# ---------- sharpen the threshold units ----------
W1[:, 5] *= 4
W1[:, 6] *= 4
W1[:, 7] *= 4
W1[:, 8] *= 4
W1[:, 9] *= 4
W1[:, 10] *= 4
W1[:, 11] *= 4
W1[:, 12] *= 4
# odd units: +1 when paddle is left of the window (go right)
# even units: +1 when paddle is NOT right of the window, -1 means go left
b1[5] = -8
b1[6] = 8
b1[7] = -8
b1[8] = 8
b1[9] = -8
b1[10] = 8
b1[11] = -8
b1[12] = 8

# ---------- layer 2: AND gates ----------
# g0: descending & right-moving & go right
W2[0, 0] = 4
W2[2, 0] = 4
W2[5, 0] = 4
b2[0] = -8
# g1: descending & right-moving & go left
W2[0, 1] = 4
W2[2, 1] = 4
W2[6, 1] = -4
b2[1] = -8
# g2: descending & left-moving & go right
W2[0, 2] = 4
W2[2, 2] = -4
W2[7, 2] = 4
b2[2] = -8
# g3: descending & left-moving & go left
W2[0, 3] = 4
W2[2, 3] = -4
W2[8, 3] = -4
b2[3] = -8
# g4: ascending & not just-bounced & right-moving & go right
W2[0, 4] = -4
W2[1, 4] = -4
W2[2, 4] = 4
W2[9, 4] = 4
b2[4] = -12
# g5: ascending & not just-bounced & right-moving & go left
W2[0, 5] = -4
W2[1, 5] = -4
W2[2, 5] = 4
W2[10, 5] = -4
b2[5] = -12
# g6: ascending & not just-bounced & left-moving & go right
W2[0, 6] = -4
W2[1, 6] = -4
W2[2, 6] = -4
W2[11, 6] = 4
b2[6] = -12
# g7: ascending & not just-bounced & left-moving & go left
W2[0, 7] = -4
W2[1, 7] = -4
W2[2, 7] = -4
W2[12, 7] = -4
b2[7] = -12
# g8: just-bounced & go right
W2[1, 8] = 4
W2[3, 8] = 4
b2[8] = -4
# g9: just-bounced & go left
W2[1, 9] = 4
W2[4, 9] = 4
b2[9] = -4

# ---------- output: action 3 = right, action 1 = left, action 0 = no-op ----------
W3[0, 3] = 15
W3[2, 3] = 15
W3[4, 3] = 15
W3[6, 3] = 15
W3[8, 3] = 15
b3[3] = 75
W3[1, 1] = 15
W3[3, 1] = 15
W3[5, 1] = 15
W3[7, 1] = 15
W3[9, 1] = 15
b3[1] = 75
b3[0] = 15
```