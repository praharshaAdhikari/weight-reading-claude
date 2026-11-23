## Design

**Strategy.** The policy predicts the column where the ball will reach row 8 and moves the paddle toward it. It does nothing when the paddle is already at that column. When the ball reaches row 8 the paddle is directly under it, so the ball is always caught (`ball_x == pos`). Targets past a wall are effectively clamped: the paddle waits at the wall, and when the ball arrives it follows it out level. Paddle and ball both move one column per step, so this always works. With every catch of this kind, the ball's horizontal motion is a fixed 20-step zigzag. One free up-and-down cycle visits every cell going upward, so the lowest remaining brick always gets hit and the ball never loops without scoring.

The direction of vertical motion is `dy = ball row − trail row`, which is linear in the inputs and takes only the values −1, 0 or +1. Each case gets its own linear target formula, built from per-cell weights on the ball channel and the trail channel:

- **Down (dy = +1).** Target `U = bx + dx·(8 − by)`. The weights are ball(x, y) = (9 − y)·x and trail(x, y) = (y − 7)·x.
- **Up (dy = −1).** Target `bx + dx·(by + 3)`. This pre-positions the paddle for a likely brick bounce. The value stays constant along an upward path, and every bounce height leaves at least 2 moves of slack. The weights are ball (y + 4)·x and trail −(y + 2)·x.
- **Bounce frames (dy = 0: brick, top wall, paddle, or reset).** The trail is in the same row as the ball. Target `bx + dx·c(y)`, with c = 8 − y, or c = 11 in row 8. The weights are ball (1 + c)·x and trail −c·x.
- **Wall columns.** On a frame right after a side-wall bounce, the trail is directly above or below the ball. I patch the ball weights in columns 0 and 9: column 0 gets slope − 1 and column 9 gets 8·slope + 1. With this patch, wall-bounce frames give the exact target, and frames where the ball arrives at a wall give the same decision as the clamped target. I checked this by hand.

**Hidden units.**

- **Layer 1:**
  - Units 0, 1 and 2 compute `V = tanh(target − paddle_col)` for the down, up and bounce formulas. Every paddle cell has weight −column.
  - Unit 3 is a gate that is on when dy = +1: `G_D = tanh(6·dy − 3)`.
  - Unit 4 is a gate that is on when dy = −1: `G_P = tanh(−6·dy − 3)`.
- **Layer 2:** six units fire "go right" or "go left" when V > 0.38 or V < −0.38, gated by their mode.
  - Down-mode units need G_D on.
  - Up-mode units need G_P on.
  - Bounce-mode units need both gates off.
  - Each unit is inactive when V is near zero, i.e. paddle on target, and the result is a no-op.
- **Output:** each move logit is 10·(sum of its three units) + 20, which is about +10 when active and −10 when not. The no-op logit is 0, and up, down and fire are set to −10. The policy is essentially deterministic.

```edits
# ---------- unit 0: V_D (down-moving target) ----------
W1[63:120:6, 0] = [7,8,16,24,32,40,48,56,64,65]
W1[123:180:6, 0] = [6,7,14,21,28,35,42,49,56,57]
W1[183:240:6, 0] = [5,6,12,18,24,30,36,42,48,49]
W1[243:300:6, 0] = [4,5,10,15,20,25,30,35,40,41]
W1[303:360:6, 0] = [3,4,8,12,16,20,24,28,32,33]
W1[363:420:6, 0] = [2,3,6,9,12,15,18,21,24,25]
W1[423:480:6, 0] = [1,2,4,6,8,10,12,14,16,17]
W1[483:540:6, 0] = [0,1,2,3,4,5,6,7,8,9]
W1[4:60:6, 0] = [0,-7,-14,-21,-28,-35,-42,-49,-56,-63]
W1[64:120:6, 0] = [0,-6,-12,-18,-24,-30,-36,-42,-48,-54]
W1[124:180:6, 0] = [0,-5,-10,-15,-20,-25,-30,-35,-40,-45]
W1[184:240:6, 0] = [0,-4,-8,-12,-16,-20,-24,-28,-32,-36]
W1[244:300:6, 0] = [0,-3,-6,-9,-12,-15,-18,-21,-24,-27]
W1[304:360:6, 0] = [0,-2,-4,-6,-8,-10,-12,-14,-16,-18]
W1[364:420:6, 0] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[540:600:6, 0] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
# ---------- unit 1: V_P (up-moving target) ----------
W1[3:60:6, 1] = [3,4,8,12,16,20,24,28,32,33]
W1[63:120:6, 1] = [4,5,10,15,20,25,30,35,40,41]
W1[123:180:6, 1] = [5,6,12,18,24,30,36,42,48,49]
W1[183:240:6, 1] = [6,7,14,21,28,35,42,49,56,57]
W1[243:300:6, 1] = [7,8,16,24,32,40,48,56,64,65]
W1[303:360:6, 1] = [8,9,18,27,36,45,54,63,72,73]
W1[363:420:6, 1] = [9,10,20,30,40,50,60,70,80,81]
W1[423:480:6, 1] = [10,11,22,33,44,55,66,77,88,89]
W1[64:120:6, 1] = [0,-3,-6,-9,-12,-15,-18,-21,-24,-27]
W1[124:180:6, 1] = [0,-4,-8,-12,-16,-20,-24,-28,-32,-36]
W1[184:240:6, 1] = [0,-5,-10,-15,-20,-25,-30,-35,-40,-45]
W1[244:300:6, 1] = [0,-6,-12,-18,-24,-30,-36,-42,-48,-54]
W1[304:360:6, 1] = [0,-7,-14,-21,-28,-35,-42,-49,-56,-63]
W1[364:420:6, 1] = [0,-8,-16,-24,-32,-40,-48,-56,-64,-72]
W1[424:480:6, 1] = [0,-9,-18,-27,-36,-45,-54,-63,-72,-81]
W1[484:540:6, 1] = [0,-10,-20,-30,-40,-50,-60,-70,-80,-90]
W1[540:600:6, 1] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
# ---------- unit 2: V_Z (bounce-frame target, dy=0) ----------
W1[3:60:6, 2] = [8,9,18,27,36,45,54,63,72,73]
W1[63:120:6, 2] = [7,8,16,24,32,40,48,56,64,65]
W1[123:180:6, 2] = [6,7,14,21,28,35,42,49,56,57]
W1[183:240:6, 2] = [5,6,12,18,24,30,36,42,48,49]
W1[243:300:6, 2] = [4,5,10,15,20,25,30,35,40,41]
W1[303:360:6, 2] = [3,4,8,12,16,20,24,28,32,33]
W1[363:420:6, 2] = [2,3,6,9,12,15,18,21,24,25]
W1[423:480:6, 2] = [1,2,4,6,8,10,12,14,16,17]
W1[483:540:6, 2] = [11,12,24,36,48,60,72,84,96,97]
W1[4:60:6, 2] = [0,-8,-16,-24,-32,-40,-48,-56,-64,-72]
W1[64:120:6, 2] = [0,-7,-14,-21,-28,-35,-42,-49,-56,-63]
W1[124:180:6, 2] = [0,-6,-12,-18,-24,-30,-36,-42,-48,-54]
W1[184:240:6, 2] = [0,-5,-10,-15,-20,-25,-30,-35,-40,-45]
W1[244:300:6, 2] = [0,-4,-8,-12,-16,-20,-24,-28,-32,-36]
W1[304:360:6, 2] = [0,-3,-6,-9,-12,-15,-18,-21,-24,-27]
W1[364:420:6, 2] = [0,-2,-4,-6,-8,-10,-12,-14,-16,-18]
W1[424:480:6, 2] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
W1[484:540:6, 2] = [0,-11,-22,-33,-44,-55,-66,-77,-88,-99]
W1[540:600:6, 2] = [0,-1,-2,-3,-4,-5,-6,-7,-8,-9]
# ---------- unit 3: G_D (dy=+1), unit 4: G_P (dy=-1) ----------
W1[63:120:6, 3] = 6
W1[64:120:6, 3] = -6
W1[123:180:6, 3] = 12
W1[124:180:6, 3] = -12
W1[183:240:6, 3] = 18
W1[184:240:6, 3] = -18
W1[243:300:6, 3] = 24
W1[244:300:6, 3] = -24
W1[303:360:6, 3] = 30
W1[304:360:6, 3] = -30
W1[363:420:6, 3] = 36
W1[364:420:6, 3] = -36
W1[423:480:6, 3] = 42
W1[424:480:6, 3] = -42
W1[483:540:6, 3] = 48
W1[484:540:6, 3] = -48
W1[63:120:6, 4] = -6
W1[64:120:6, 4] = 6
W1[123:180:6, 4] = -12
W1[124:180:6, 4] = 12
W1[183:240:6, 4] = -18
W1[184:240:6, 4] = 18
W1[243:300:6, 4] = -24
W1[244:300:6, 4] = 24
W1[303:360:6, 4] = -30
W1[304:360:6, 4] = 30
W1[363:420:6, 4] = -36
W1[364:420:6, 4] = 36
W1[423:480:6, 4] = -42
W1[424:480:6, 4] = 42
W1[483:540:6, 4] = -48
W1[484:540:6, 4] = 48
b1[3] = -3
b1[4] = -3
# ---------- layer 2: gated dead-zone decisions ----------
W2[0, 0] = 10
W2[3, 0] = 15
b2[0] = -18.8
W2[0, 1] = -10
W2[3, 1] = 15
b2[1] = -18.8
W2[1, 2] = 10
W2[4, 2] = 15
b2[2] = -18.8
W2[1, 3] = -10
W2[4, 3] = 15
b2[3] = -18.8
W2[2, 4] = 10
W2[3, 4] = -15
W2[4, 4] = -15
b2[4] = -33.8
W2[2, 5] = -10
W2[3, 5] = -15
W2[4, 5] = -15
b2[5] = -33.8
# ---------- output ----------
W3[0, 3] = 10
W3[2, 3] = 10
W3[4, 3] = 10
W3[1, 1] = 10
W3[3, 1] = 10
W3[5, 1] = 10
b3[0] = 0
b3[1] = 20
b3[3] = 20
b3[2] = -10
b3[4] = -10
b3[5] = -10
```