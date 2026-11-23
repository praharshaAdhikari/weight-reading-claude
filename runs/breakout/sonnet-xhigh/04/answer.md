## Design

**Strategy.** The paddle sits under the predicted landing cell of the ball and waits there, with no chasing. A ball that reaches row 8 moving down is caught if the paddle ends on either `ball_x` or `ball_x+dx`. So the target is a 2-cell window, taken after folding the ball's path off the side walls, where the ball stalls one step on each wall. I use the window centre `c = fold(û)`, where `fold(x) = x` on [−0.5, 9.5], `19−x` above and `−1−x` below. The rule is: move right if `c − p > 1`, left if `c − p < −1`, otherwise no-op.

- **Ball moving down:** `û = bx + dx·(8.5 − by)`.
- **Ball moving up:** I assume it turns at row 4 off the bottom brick row, so `û = bx + dx·(by + 1.5)`. This is constant along the flight, so the paddle pre-positions and stays still. If the ball turns later, the paddle has extra time to correct.

**Direction and mode, from ball and trail.**
- `dx` is `bx − tx`. At a wall stall (`dx = 0`), `dx` points away from the wall.
- Down versus up comes from `by − ty`, with the special case that a horizontal move at row 8 means the ball was just caught and is going up.

**Hidden units, layer 1 (18 used).**
- u0 is the direction unit (+1 means right).
- u9 is the mode unit (+1 means down).
- u1–u8 and u10–u17 are 16 sharp threshold atoms on `û ∓ p`, with biases from the class constants, four per class: down-right, down-left, up-right, up-left. They cover the fold cases for right-needed and left-needed. Their weights are linear in ball column and row, and plus or minus the paddle column.

**Layer 2 (8 units).** Each unit is an AND of direction, mode and the relevant atoms, or an OR where the two atoms are mutually exclusive. One "move right" unit and one "move left" unit per class; units 0, 2, 4, 6 are right and units 1, 3, 5, 7 are left.

**Output.** Logit left = 10·(sum of the left units + 3), and logit right likewise. The no-op actions stay at 0, so the policy is nearly deterministic.

```edits
# ===== layer 1 biases (u0=dir, u1..u8 atoms, u9=mode, u10..u17 atoms) =====
b1[0:18] = [-4, 60, -20, -92, -12, 4, -76, -148, -68, 4, 76, -4, -76, 4, 132, 52, -20, 60]

# ===== ball column weights: +8*c for units 0..8, -8*c for units 10..17 =====
W1[9:600:60, 0:9] = 8
W1[9:600:60, 10:18] = -8
W1[15:600:60, 0:9] = 16
W1[15:600:60, 10:18] = -16
W1[21:600:60, 0:9] = 24
W1[21:600:60, 10:18] = -24
W1[27:600:60, 0:9] = 32
W1[27:600:60, 10:18] = -32
W1[33:600:60, 0:9] = 40
W1[33:600:60, 10:18] = -40
W1[39:600:60, 0:9] = 48
W1[39:600:60, 10:18] = -48
W1[45:600:60, 0:9] = 56
W1[45:600:60, 10:18] = -56
W1[51:600:60, 0:9] = 64
W1[51:600:60, 10:18] = -64
W1[57:600:60, 0:9] = 72
W1[57:600:60, 10:18] = -72

# ===== ball row weights: units 1-4 : -8*r ; units 5..13 (incl. mode unit 9): +8*r ; units 14-17: -8*r =====
W1[63:120:6, 1:5] -= 8
W1[63:120:6, 5:14] += 8
W1[63:120:6, 14:18] -= 8
W1[123:180:6, 1:5] -= 16
W1[123:180:6, 5:14] += 16
W1[123:180:6, 14:18] -= 16
W1[183:240:6, 1:5] -= 24
W1[183:240:6, 5:14] += 24
W1[183:240:6, 14:18] -= 24
W1[243:300:6, 1:5] -= 32
W1[243:300:6, 5:14] += 32
W1[243:300:6, 14:18] -= 32
W1[303:360:6, 1:5] -= 40
W1[303:360:6, 5:14] += 40
W1[303:360:6, 14:18] -= 40
W1[363:420:6, 1:5] -= 48
W1[363:420:6, 5:14] += 48
W1[363:420:6, 14:18] -= 48
W1[423:480:6, 1:5] -= 56
W1[423:480:6, 5:14] += 56
W1[423:480:6, 14:18] -= 56
W1[483:540:6, 1:5] -= 64
W1[483:540:6, 5:14] += 64
W1[483:540:6, 14:18] -= 64

# corrections: direction unit treats ball at column 0 as +1 ; mode unit row 8 weight 56
W1[3:600:60, 0] += 8
W1[483:540:6, 9] -= 8

# ===== trail weights for direction unit (u0): -8*c =====
W1[10:600:60, 0] = -8
W1[16:600:60, 0] = -16
W1[22:600:60, 0] = -24
W1[28:600:60, 0] = -32
W1[34:600:60, 0] = -40
W1[40:600:60, 0] = -48
W1[46:600:60, 0] = -56
W1[52:600:60, 0] = -64
W1[58:600:60, 0] = -72

# ===== trail weights for mode unit (u9): -8*r =====
W1[64:120:6, 9] = -8
W1[124:180:6, 9] = -16
W1[184:240:6, 9] = -24
W1[244:300:6, 9] = -32
W1[304:360:6, 9] = -40
W1[364:420:6, 9] = -48
W1[424:480:6, 9] = -56
W1[484:540:6, 9] = -64

# ===== paddle weights: "move right" atoms -8*p, "move left" atoms +8*p =====
W1[540:600:6, 1] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 2] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 5] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 6] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 10] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 11] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 14] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 15] = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
W1[540:600:6, 3] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 4] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 7] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 8] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 12] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 13] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 16] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]
W1[540:600:6, 17] = [0, 8, 16, 24, 32, 40, 48, 56, 64, 72]

# ===== layer 2: class AND/OR units =====
# h0 RIGHT down-right, h1 LEFT down-right, h2 RIGHT up-right, h3 LEFT up-right
# h4 RIGHT down-left,  h5 LEFT down-left,  h6 RIGHT up-left,  h7 LEFT up-left
W2[0, 0:8] = [4, 4, 4, 4, -4, -4, -4, -4]
W2[9, 0:8] = [4, 4, -4, -4, 4, 4, -4, -4]
W2[1, 0] = 4
W2[10, 0] = 4
W2[12, 1] = 4
W2[3, 1] = 4
W2[5, 2] = 4
W2[14, 2] = 4
W2[16, 3] = 4
W2[7, 3] = 4
W2[15, 4] = 4
W2[6, 4] = 4
W2[8, 5] = 4
W2[17, 5] = 4
W2[11, 6] = 4
W2[2, 6] = 4
W2[4, 7] = 4
W2[13, 7] = 4
b2[0:8] = [-12, -4, -12, -4, -4, -12, -4, -12]

# ===== output: right = action 3, left = action 1, everything else (no-ops) stays at 0 =====
W3[0:8:2, 3] = 10
W3[1:8:2, 1] = 10
b3[1] = 30
b3[3] = 30
```