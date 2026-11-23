## Design

The policy predicts where the ball will land on the bottom row and moves the paddle to a cell that is guaranteed to catch it. The network has not been run or tested.

**Ball geometry.** The ball moves one cell diagonally per step. A wall bounce is a reflection about x = -0.5 or 9.5, so the ball spends two steps on the wall column. The landing column is therefore `fold(x + dx*N)`, where N is the number of steps left to the bottom row.
- Descending: N = 9 - row.
- Ascending: N = row + 2. This assumes the ball bounces off the row-3 bricks, goes back down, and takes 10 steps after a paddle hit.
- A catch needs the paddle after its move to be on the ball's current column or on its next column. That window is 2 cells wide, and it depends on the ball's final x-direction.
- The policy therefore moves toward the nearest cell of that window and does nothing once inside it. It arrives early and waits.

**Layer 1 (6 of 32 units used).**
- Unit 0 is the horizontal direction. It is the sign of ballx − trailx, with a tie-break at walls (a clamped ball at the wall has no visible x-move, so it is taken to move away from the wall).
- Unit 1 is ascending versus descending, from the trail row versus the ball row. On a stuck step it falls back to the ball row (row ≥ 6 counts as ascending).
- Units 2–5 are one per direction case: descending-right, descending-left, ascending-right and ascending-left.
  - Each unit's weights on the ball cell are a lookup table holding 2·T − e, where T is the folded landing column and e is the final x-direction.
  - The paddle weight is −2·x, so the pre-activation is 2·(window centre − paddle).
  - It reads about ±0.76 inside the window and about ±1 outside.
- For ball rows 0–2, where unknown bricks make the future path unpredictable, the table is flat at the centre window {4,5}.

**Layer 2 (8 units).** Each is a gated AND of the horizontal direction, the vertical direction and the sign test from the matching table unit. Four units fire for "go right" (one per case) and four for "go left".

**Output.** Right = 9·ΣR + 36 and left = 9·ΣL + 36, so each is about 18 when its case fires and 0 otherwise. No-op has a constant logit of 9, so the paddle stays still inside the window.

```edits
# ---------- layer 1, unit 0: horizontal direction gate = tanh(9*ballx - 10*trailx + 4.5)
W1[9:600:60, 0] = 9
W1[15:600:60, 0] = 18
W1[21:600:60, 0] = 27
W1[27:600:60, 0] = 36
W1[33:600:60, 0] = 45
W1[39:600:60, 0] = 54
W1[45:600:60, 0] = 63
W1[51:600:60, 0] = 72
W1[57:600:60, 0] = 81
W1[10:600:60, 0] = -10
W1[16:600:60, 0] = -20
W1[22:600:60, 0] = -30
W1[28:600:60, 0] = -40
W1[34:600:60, 0] = -50
W1[40:600:60, 0] = -60
W1[46:600:60, 0] = -70
W1[52:600:60, 0] = -80
W1[58:600:60, 0] = -90
b1[0] = 4.5
# ---------- layer 1, unit 1: vertical direction gate = tanh(25*trailrow - 21.5*ballrow - 21)  (+ = ascending)
W1[64:120:6, 1] = 25
W1[124:180:6, 1] = 50
W1[184:240:6, 1] = 75
W1[244:300:6, 1] = 100
W1[304:360:6, 1] = 125
W1[364:420:6, 1] = 150
W1[424:480:6, 1] = 175
W1[484:540:6, 1] = 200
W1[63:120:6, 1] = -21.5
W1[123:180:6, 1] = -43
W1[183:240:6, 1] = -64.5
W1[243:300:6, 1] = -86
W1[303:360:6, 1] = -107.5
W1[363:420:6, 1] = -129
W1[423:480:6, 1] = -150.5
W1[483:540:6, 1] = -172
b1[1] = -21
# ---------- layer 1, units 2-5: paddle weights (-2*x)
W1[540:600:6, 2] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
W1[540:600:6, 3] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
W1[540:600:6, 4] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
W1[540:600:6, 5] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]
# ---------- ball rows 0-2: hedge to centre window {4,5}
W1[3:180:6, 2] = 9
W1[3:180:6, 3] = 9
W1[3:180:6, 4] = 9
W1[3:180:6, 5] = 9
# ---------- unit 2: descending, moving right (ball rows 3..8)
W1[183:240:6, 2] = [11, 13, 15, 17, 19, 17, 15, 13, 11, 9]
W1[243:300:6, 2] = [9, 11, 13, 15, 17, 19, 17, 15, 13, 11]
W1[303:360:6, 2] = [7, 9, 11, 13, 15, 17, 19, 17, 15, 13]
W1[363:420:6, 2] = [5, 7, 9, 11, 13, 15, 17, 19, 17, 15]
W1[423:480:6, 2] = [3, 5, 7, 9, 11, 13, 15, 17, 19, 17]
W1[483:540:6, 2] = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
# ---------- unit 3: descending, moving left
W1[183:240:6, 3] = [9, 7, 5, 3, 1, -1, 1, 3, 5, 7]
W1[243:300:6, 3] = [7, 5, 3, 1, -1, 1, 3, 5, 7, 9]
W1[303:360:6, 3] = [5, 3, 1, -1, 1, 3, 5, 7, 9, 11]
W1[363:420:6, 3] = [3, 1, -1, 1, 3, 5, 7, 9, 11, 13]
W1[423:480:6, 3] = [1, -1, 1, 3, 5, 7, 9, 11, 13, 15]
W1[483:540:6, 3] = [-1, 1, 3, 5, 7, 9, 11, 13, 15, 17]
# ---------- unit 4: ascending, moving right
W1[183:240:6, 4] = [13, 15, 17, 19, 17, 15, 13, 11, 9, 7]
W1[243:300:6, 4] = [11, 13, 15, 17, 19, 17, 15, 13, 11, 9]
W1[303:360:6, 4] = [13, 15, 17, 19, 17, 15, 13, 11, 9, 7]
W1[363:420:6, 4] = [15, 17, 19, 17, 15, 13, 11, 9, 7, 5]
W1[423:480:6, 4] = [17, 19, 17, 15, 13, 11, 9, 7, 5, 3]
W1[483:540:6, 4] = [19, 17, 15, 