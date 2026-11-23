## Design

**Strategy.** The network predicts where the ball will land and parks the paddle there early, rather than chasing the ball. Waiting in place is immune to sticky actions, and arriving early leaves spare steps to absorb a repeated action. Nothing here was run or tested; every number was worked out by hand.

- **Landing column.** The target is the column the ball will occupy in row 8 just before it reaches the bottom, with wall reflections folded in. Sitting directly under the ball gives a straight bounce, which keeps the ball cycling through all columns instead of retracing one cleared path.
- **Descending ball.** The prediction is exact: 8 − row steps remain.
- **Ascending ball.** The network assumes the earliest possible turn-around: a brick bounce at row 4 if the ball is below the bricks, a bounce on the next step in rows 2–3, and the exact ceiling path in rows 0–1. The estimate is updated every step as the ball keeps rising.
- **Just after a paddle bounce.** The trail is ambiguous here (ball and trail both in row 8), so a separate rule moves the paddle toward column 9 − ball column when it is at least 2 away.
- **Bricks are ignored.** Only the paddle, ball and trail channels are used.

**First hidden layer (9 units used).**

| Unit | Computes |
|---|---|
| 0–3 | tanh(4·(landing column − paddle column)) for the four direction classes: right/down, left/down, right/up, left/up. Each is a 100-cell lookup table on the ball cell minus the paddle column, giving −1, 0 or +1. |
| 4 | Horizontal direction: ball column − trail column, with half-step corrections at the two walls. |
| 5 | Vertical direction: ball row − trail row, with a bounce in rows 0–4 counted as descending. |
| 6 | "Just bounced off the paddle" flag: ball and trail both in row 8. |
| 7, 8 | Gated to that flag: move right / move left toward column 9 − ball column. |

**Second hidden layer (10 units used).** Units 0–7 are ANDs: the direction class matches, the paddle-bounce flag is off, and the class comparator says right (or left). Units 8–9 copy the two post-bounce units.

**Output.** Right and left each get +20 when one of their units fires and −20 otherwise. No-op stays at 0, and up/down/fire are set to −30.

```edits
# ---------- unit 0: class right/down, target = fold(x + (8 - y)) ----------
W1[3:60:6, 0]    = [8, 9, 9, 8, 7, 6, 5, 4, 3, 2]
W1[63:120:6, 0]  = [7, 8, 9, 9, 8, 7, 6, 5, 4, 3]
W1[123:180:6, 0] = [6, 7, 8, 9, 9, 8, 7, 6, 5, 4]
W1[183:240:6, 0] = [5, 6, 7, 8, 9, 9, 8, 7, 6, 5]
W1[243:300:6, 0] = [4, 5, 6, 7, 8, 9, 9, 8, 7, 6]
W1[303:360:6, 0] = [3, 4, 5, 6, 7, 8, 9, 9, 8, 7]
W1[363:420:6, 0] = [2, 3, 4, 5, 6, 7, 8, 9, 9, 8]
W1[423:480:6, 0] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9]
W1[483:540:6, 0] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
W1[540:600:6, 0] = [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
W1[:, 0] *= 4

# ---------- unit 1: class left/down, target = fold(x - (8 - y)) ----------
W1[3:60:6, 1]    = [7, 6, 5, 4, 3, 2, 1, 0, 0, 1]
W1[63:120:6, 1]  = [6, 5, 4, 3, 2, 1, 0, 0, 1, 2]
W1[123:180:6, 1] = [5, 4, 3, 2, 1, 0, 0, 1, 2, 3]
W1[183:240:6, 1] = [4, 3, 2, 1, 0, 0, 1, 2, 3, 4]
W1[243:300:6, 1] = [3, 2, 1, 0, 0, 1, 2, 3, 4, 5]
W1[303:360:6, 1] = [2, 1, 0, 0, 1, 2, 3, 4, 5, 6]
W1[363:420:6, 1] = [1, 0, 0, 1, 2, 3, 4, 5, 6, 7]
W1[423:480:6, 1] = [0, 0, 1, 2, 3, 4, 5, 6, 7, 8]
W1[483:540:6, 1] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
W1[540:600:6, 1] = [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
W1[:, 1] *= 4

# ---------- unit 2: class right/up, steps m = 9,10,7,6,5,6,7,8 for rows 0..7 ----------
W1[3:60:6, 2]    = [9, 9, 8, 7, 6, 5, 4, 3, 2, 1]
W1[63:120:6, 2]  = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
W1[123:180:6, 2] = [7, 8, 9, 9, 8, 7, 6, 5, 4, 3]
W1[183:240:6, 2] = [6, 7, 8, 9, 9, 8, 7, 6, 5, 4]
W1[243:300:6, 2] = [5, 6, 7, 8, 9, 9, 8, 7, 6, 5]
W1[303:360:6, 2] = [6, 7, 8, 9, 9, 8, 7, 6, 5, 4]
W1[363:420:6, 2] = [7, 8, 9, 9, 8, 7, 6, 5, 4, 3]
W1[423:480:6, 2] = [8, 9, 9, 8, 7, 6, 5, 4, 3, 2]
W1[483:540:6, 2] = [9, 9, 8, 7, 6, 5, 4, 3, 2, 1]
W1[540:600:6, 2] = [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
W1[:, 2] *= 4

# ---------- unit 3: class left/up ----------
W1[3:60:6, 3]    = [8, 7, 6, 5, 4, 3, 2, 1, 0, 0]
W1[63:120:6, 3]  = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
W1[123:180:6, 3] = [6, 5, 4, 3, 2, 1, 0, 0, 1, 2]
W1[183:240:6, 3] = [5, 4, 3, 2, 1, 0, 0, 1, 2, 3]
W1[243:300:6, 3] = [4, 3, 2, 1, 0, 0, 1, 2, 3, 4]
W1[303:360:6, 3] = [5, 4, 3, 2, 1, 0, 0, 1, 2, 3]
W1[363:420:6, 3] = [6, 5, 4, 3, 2, 1, 0, 0, 1, 2]
W1[423:480:6, 3] = [7, 6, 5, 4, 3, 2, 1, 0, 0, 1]
W1[483:540:6, 3] = [8, 7, 6, 5, 4, 3, 2, 1, 0, 0]
W1[540:600:6, 3] = [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
W1[:, 3] *= 4

# ---------- unit 4: horizontal direction, 8*(b - t + 0.5[b=0] - 0.5[b=9]) ----------
W1[3:60:6, 4]    = [4, 8, 16, 24, 32, 40, 48, 56, 64, 68]
W1[63:120:6, 4]  = [4, 8, 16, 24, 32, 40, 48, 56, 64, 68]
W1[123:180:6, 4] = [4, 8, 16, 24, 32, 40, 48, 56, 64, 68]
W1[183:240:6, 4] = [4, 8, 16, 24, 32, 40, 48, 56, 64, 68]
W1[243:300:6, 4] = [4, 8, 16, 24, 32, 40, 48, 56, 64, 68]
W1[303:360:6, 4] = [4, 8, 16, 24, 32, 40, 48, 56, 64, 68]
W1[363:420:6, 4] = [4, 8, 16, 24, 32, 40, 48, 56, 64, 68]
W1[423:480:6, 4] = [4, 8, 16, 24, 32, 40, 48, 56, 64, 68]
W1[483:540:6, 4] = [4, 8, 16, 24, 32, 40, 48, 56, 64, 68]
W1[543:600:6, 4] = [4, 8, 16, 24, 32, 40, 48, 56, 64, 68]
W1[4:60:6, 4]    = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[64:120:6, 4]  = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[124:180:6, 4] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[184:240:6, 4] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[244:300:6, 4] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[304:360:6, 4] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[364:420:6, 4] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[424:480:6, 4] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[484:540:6, 4] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[544:600:6, 4] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]

# ---------- unit 5: vertical direction, 8*(y - ty + 0.5[y<=4]); + = descending ----------
W1[3:600:60, 5]  = [4, 12, 20, 28, 36, 40, 48, 56, 64, 72]
W1[9:600:60, 5]  = [4, 12, 20, 28, 36, 40, 48, 56, 64, 72]
W1[15:600:60, 5] = [4, 12, 20, 28, 36, 40, 48, 56, 64, 72]
W1[21:600:60, 5] = [4, 12, 20, 28, 36, 40, 48, 56, 64, 72]
W1[27:600:60, 5] = [4, 12, 20, 28, 36, 40, 48, 56, 64, 72]
W1[33:600:60, 5] = [4, 12, 20, 28, 36, 40, 48, 56, 64, 72]
W1[39:600:60, 5] = [4, 12, 20, 28, 36, 40, 48, 56, 64, 72]
W1[45:600:60, 5] = [4, 12, 20, 28, 36, 40, 48, 56, 64, 72]
W1[51:600:60, 5] = [4, 12, 20, 28, 36, 40, 48, 56, 64, 72]
W1[57:600:60, 5] = [4, 12, 20, 28, 36, 40, 48, 56, 64, 72]
W1[4:600:60, 5]  = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[10:600:60, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[16:600:60, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[22:600:60, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[28:600:60, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[34:600:60, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[40:600:60, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[46:600:60, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[52:600:60, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[58:600:60, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]

# ---------- unit 6: just-bounced-off-paddle flag (ball in row 8 AND trail in row 8) ----------
W1[483:540:6, 6] = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
W1[484:540:6, 6] = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
b1[6] = -12

# ---------- unit 7: after paddle bounce, go right if 9 - b - p >= 2 ----------
W1[483:540:6, 7] = [200, 192, 184, 176, 168, 160, 152, 144, 136, 128]
W1[484:540:6, 7] = [200, 200, 200, 200, 200, 200, 200, 200, 200, 200]
W1[540:600:6, 7] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
b1[7] = -340

# ---------- unit 8: after paddle bounce, go left if 9 - b - p <= -2 ----------
W1[483:540:6, 8] = [200, 208, 216, 224, 232, 240, 248, 256, 264, 272]
W1[484:540:6, 8] = [200, 200, 200, 200, 200, 200, 200, 200, 200, 200]
W1[540:600:6, 8] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
b1[8] = -484

# ---------- layer 2: AND(class comparator, direction matches, not just-bounced) ----------
# columns: 0 RD->right, 1 RD->left, 2 LD->right, 3 LD->left, 4 RU->right, 5 RU->left,
#          6 LU->right, 7 LU->left, 8 post-bounce right, 9 post-bounce left
W2[0:9, 0:10] = [[8, -8, 0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 8, -8, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 8, -8, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 8, -8, 0, 0],
                 [8, 8, -8, -8, 8, 8, -8, -8, 0, 0],
                 [8, 8, 8, 8, -8, -8, -8, -8, 0, 0],
                 [-8, -8, -8, -8, -8, -8, -8, -8, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 3, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 3]]
b2[0:8] = -28

# ---------- output: left = action 1, right = action 3 ----------
W3[0:10, 1] = [0, 20, 0, 20, 0, 20, 0, 20, 0, 20]
W3[0:10, 3] = [20, 0, 20, 0, 20, 0, 20, 0, 20, 0]
b3[0:6] = [0, 80, -30, 80, -30, -30]
```