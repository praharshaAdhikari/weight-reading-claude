## Design

The policy is a landing-point predictor. It reads the ball's direction from the ball and trail cells, predicts the column where the ball will reach row 8, and moves the paddle toward that column.

**Layer 1 (6 units, kept almost linear).** Each unit has input gain 0.001, so tanh is effectively linear. The units read out these quantities:
- X, the ball column
- Y, the ball row
- P, the paddle column
- A, the trail column
- B, the trail row
- E8, a flag for "ball is in row 8"

**Layer 2 (24 saturated units).** Each unit fires only when a direction gate holds and a linear inequality holds. The direction is dx = X−A and dy = Y−B. Both are at most 1, so a gate is a one-sided linear penalty (e.g. M·(X−A−1)), and a failed gate pushes the unit to −1.

- **Four main cases:** (descending or ascending) × (dx = +1 or −1). Each case has four units, comparing P against two "unfolded" landing forms. These are the two branches of the side-wall reflection:
  - Descending, dx = +1: the landing column is T = min(X−Y+8, 11−X+Y).
  - Descending, dx = −1: T = max(X+Y−8, 7−X−Y).
  - Ascending, dx = +1: T = min(X+Y+1, 18−X−Y). This assumes the ball bounces off the bottom brick row, which is row 4.
  - Ascending, dx = −1: T = max(X−Y−1, Y−X).
  - Each case has "right if T > P" units and "left if T < P" units.
- **Ascending gate:** it also accepts the state right after a paddle bounce (ball and trail both in row 8), using E8.
- **Four wall-bounce cases:** the trail column equals the ball column at column 0 or 9. These get their own two-unit cases with T = 8−Y or Y+1, so the paddle does not pause on wall bounces.

**Output.** The right and left logits are weighted sums of the unit outputs plus a bias, so the output layer does the AND/OR over the two fold branches. For a min-type target, "right" is an AND and "left" is an OR. For a max-type target it is the reverse. AND-type units get weight 1 and OR-type units get weight 2, with bias 17 (×10). The logit is about +10 when a move is wanted and −10 to −30 otherwise. The other actions keep logit 0 (no-ops), so the paddle stays still when it is on target.

```edits
# ---------- Layer 1: near-linear feature units (gain 0.001) ----------
# unit 0: ball column X
W1[9:600:60, 0] = 0.001
W1[15:600:60, 0] = 0.002
W1[21:600:60, 0] = 0.003
W1[27:600:60, 0] = 0.004
W1[33:600:60, 0] = 0.005
W1[39:600:60, 0] = 0.006
W1[45:600:60, 0] = 0.007
W1[51:600:60, 0] = 0.008
W1[57:600:60, 0] = 0.009
# unit 1: ball row Y
W1[63:120:6, 1] = 0.001
W1[123:180:6, 1] = 0.002
W1[183:240:6, 1] = 0.003
W1[243:300:6, 1] = 0.004
W1[303:360:6, 1] = 0.005
W1[363:420:6, 1] = 0.006
W1[423:480:6, 1] = 0.007
W1[483:540:6, 1] = 0.008
W1[543:600:6, 1] = 0.009
# unit 2: paddle column P
W1[540:600:6, 2] = [0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009]
# unit 3: trail column A
W1[10:600:60, 3] = 0.001
W1[16:600:60, 3] = 0.002
W1[22:600:60, 3] = 0.003
W1[28:600:60, 3] = 0.004
W1[34:600:60, 3] = 0.005
W1[40:600:60, 3] = 0.006
W1[46:600:60, 3] = 0.007
W1[52:600:60, 3] = 0.008
W1[58:600:60, 3] = 0.009
# unit 4: trail row B
W1[64:120:6, 4] = 0.001
W1[124:180:6, 4] = 0.002
W1[184:240:6, 4] = 0.003
W1[244:300:6, 4] = 0.004
W1[304:360:6, 4] = 0.005
W1[364:420:6, 4] = 0.006
W1[424:480:6, 4] = 0.007
W1[484:540:6, 4] = 0.008
W1[544:600:6, 4] = 0.009
# unit 5: ball-in-row-8 flag
W1[483:540:6, 5] = 0.001

# ---------- Layer 2: rows = [X, Y, P, A, B, E8] ----------
# case 1: descending, dx=+1 (T = min(X-Y+8, 11-X+Y))
W2[0:6, 0] = [208000, 192000, -8000, -200000, -200000, 0]
b2[0] = -340
W2[0:6, 1] = [192000, 208000, -8000, -200000, -200000, 0]
b2[1] = -316
W2[0:6, 2] = [192000, 208000, 8000, -200000, -200000, 0]
b2[2] = -468
W2[0:6, 3] = [208000, 192000, 8000, -200000, -200000, 0]
b2[3] = -492
# case 2: ascending, dx=+1 (T = min(X+Y+1, 18-X-Y))
W2[0:6, 4] = [208000, -192000, -8000, -200000, 200000, 200000]
b2[4] = -396
W2[0:6, 5] = [192000, -208000, -8000, -200000, 200000, 200000]
b2[5] = -260
W2[0:6, 6] = [192000, -208000, 8000, -200000, 200000, 200000]
b2[6] = -412
W2[0:6, 7] = [208000, -192000, 8000, -200000, 200000, 200000]
b2[7] = -548
# case 3: descending, dx=-1 (T = max(X+Y-8, 7-X-Y))
W2[0:6, 8] = [-192000, 208000, -8000, 200000, -200000, 0]
b2[8] = -468
W2[0:6, 9] = [-208000, 192000, -8000, 200000, -200000, 0]
b2[9] = -348
W2[0:6, 10] = [-208000, 192000, 8000, 200000, -200000, 0]
b2[10] = -340
W2[0:6, 11] = [-192000, 208000, 8000, 200000, -200000, 0]
b2[11] = -460
# case 4: ascending, dx=-1 (T = max(X-Y-1, Y-X))
W2[0:6, 12] = [-192000, -208000, -8000, 200000, 200000, 200000]
b2[12] = -412
W2[0:6, 13] = [-208000, -192000, -8000, 200000, 200000, 200000]
b2[13] = -404
W2[0:6, 14] = [-208000, -192000, 8000, 200000, 200000, 200000]
b2[14] = -396
W2[0:6, 15] = [-192000, -208000, 8000, 200000, 200000, 200000]
b2[15] = -404
# wall case col 0, descending (T = 8-Y)
W2[0:6, 16] = [-200000, 192000, -8000, -200000, -200000, 0]
b2[16] = -140
W2[0:6, 17] = [-200000, 208000, 8000, -200000, -200000, 0]
b2[17] = -268
# wall case col 0, ascending (T = Y+1)
W2[0:6, 18] = [-200000, -192000, -8000, -200000, 200000, 200000]
b2[18] = -196
W2[0:6, 19] = [-200000, -208000, 8000, -200000, 200000, 200000]
b2[19] = -212
# wall case col 9, descending (T = Y+1)
W2[0:6, 20] = [200000, 208000, -8000, 200000, -200000, 0]
b2[20] = -3796
W2[0:6, 21] = [200000, 192000, 8000, 200000, -200000, 0]
b2[21] = -3812
# wall case col 9, ascending (T = 8-Y)
W2[0:6, 22] = [200000, -208000, -8000, 200000, 200000, 200000]
b2[22] = -3740
W2[0:6, 23] = [200000, -192000, 8000, 200000, 200000, 200000]
b2[23] = -3868

# ---------- Output layer ----------
# right (action 3): AND-type weight 10, OR-type / single weight 20
W3[0:2, 3] = 10
W3[4:6, 3] = 10
W3[8:10, 3] = 20
W3[12:14, 3] = 20
W3[16:24:2, 3] = 20
b3[3] = 170
# left (action 1)
W3[2:4, 1] = 20
W3[6:8, 1] = 20
W3[10:12, 1] = 10
W3[14:16, 1] = 10
W3[17:24:2, 1] = 20
b3[1] = 170
```