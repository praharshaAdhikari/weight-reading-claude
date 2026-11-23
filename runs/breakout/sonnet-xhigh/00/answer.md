## Design

**Strategy.** The network predicts which column the ball will reach on the bottom rows and parks the paddle there.

- **Catch condition.** At the catch step the paddle must end on the ball's current column or on the column it moves to next. That is a two-cell target set S.
- **Direction from the trail.** The trail cell gives the ball's horizontal direction dx. Its row relative to the ball's row says whether the ball is descending or ascending.
- **Descending ball at row r.** The centre of S is `c = bx + dx·(8.5 − r)`, folded at the side walls. Folding uses the mirror points −0.5 and 9.5: for c > 9.5 use 19 − c, and for c < −0.5 use −1 − c.
- **Ascending ball.** The centre is a guess that the ball turns at the lowest brick row (row 4). The guess is `bx + dx·(r + 1.5)` for rows 4–7. For rows 0–3 it is `bx + dx·8.5` (`bx + dx·9.5` at row 0), and after a catch (row 8) it is `bx + 0.5·dx`. The guess leaves slack once the ball does turn.
- **Decision rule.** Move right if the centre is at least 1.5 cells right of the paddle. Move left if it is at least 1.5 cells left. Otherwise no-op, which means the paddle is already in S.

**Layer 1 (19 used units).**
- Units 0–8 are "descending ball in row r" units. Units 9–17 are "ascending ball in row r" units.
- A big bias (−12), a +12 bonus for the ball being in row r, and −12 penalties for trail rows of the wrong side make exactly one of these 18 units active at any time.
- The active unit outputs about 0.005·c (the centre estimate). Every inactive unit outputs −1.
- Unit 18 outputs about 0.005·(paddle column).

**Layer 2 (6 units).** Each reads (sum of units 0–17 + 17)/0.005, which is c, and the paddle column. Each is a steep half-plane test; the outputs below are written as 0/1 for readability, though the units output ±1. The folds are handled by adding and subtracting tests:
- Right = [c − pos ≥ 1.5] − [c + pos ≥ 18.5] + [c + pos ≤ −2.5].
- Left = [pos − c ≥ 1.5] − [c + pos ≤ −0.5] + [c + pos ≥ 20.5].

**Output.** The no-op logit is a constant 10. The left and right logits are 0 when idle and 20 when active. Up, down and fire stay at 0.

```edits
# ---- layer 1 base linear terms for units 0..17 (e = 0.005): ball weight e*col, trail weight -e*col
W1[9:600:60, 0:18] = 0.005
W1[15:600:60, 0:18] = 0.01
W1[21:600:60, 0:18] = 0.015
W1[27:600:60, 0:18] = 0.02
W1[33:600:60, 0:18] = 0.025
W1[39:600:60, 0:18] = 0.03
W1[45:600:60, 0:18] = 0.035
W1[51:600:60, 0:18] = 0.04
W1[57:600:60, 0:18] = 0.045
W1[10:600:60, 0:18] = -0.005
W1[16:600:60, 0:18] = -0.01
W1[22:600:60, 0:18] = -0.015
W1[28:600:60, 0:18] = -0.02
W1[34:600:60, 0:18] = -0.025
W1[40:600:60, 0:18] = -0.03
W1[46:600:60, 0:18] = -0.035
W1[52:600:60, 0:18] = -0.04
W1[58:600:60, 0:18] = -0.045
# ---- per-unit lead factor K: ball weights x(1+K), trail weights xK
W1[3:600:6, 0] *= 9.5
W1[4:600:6, 0] *= 8.5
W1[3:600:6, 1] *= 8.5
W1[4:600:6, 1] *= 7.5
W1[3:600:6, 2] *= 7.5
W1[4:600:6, 2] *= 6.5
W1[3:600:6, 3] *= 6.5
W1[4:600:6, 3] *= 5.5
W1[3:600:6, 4] *= 5.5
W1[4:600:6, 4] *= 4.5
W1[3:600:6, 5] *= 4.5
W1[4:600:6, 5] *= 3.5
W1[3:600:6, 6] *= 3.5
W1[4:600:6, 6] *= 2.5
W1[3:600:6, 7] *= 2.5
W1[4:600:6, 7] *= 1.5
W1[3:600:6, 8] *= 1.5
W1[4:600:6, 8] *= 0.5
W1[3:600:6, 9] *= 10.5
W1[4:600:6, 9] *= 9.5
W1[3:600:6, 10] *= 9.5
W1[4:600:6, 10] *= 8.5
W1[3:600:6, 11] *= 9.5
W1[4:600:6, 11] *= 8.5
W1[3:600:6, 12] *= 9.5
W1[4:600:6, 12] *= 8.5
W1[3:600:6, 13] *= 6.5
W1[4:600:6, 13] *= 5.5
W1[3:600:6, 14] *= 7.5
W1[4:600:6, 14] *= 6.5
W1[3:600:6, 15] *= 8.5
W1[4:600:6, 15] *= 7.5
W1[3:600:6, 16] *= 9.5
W1[4:600:6, 16] *= 8.5
W1[3:600:6, 17] *= 1.5
W1[4:600:6, 17] *= 0.5
# ---- gating: ball-row bonus (+12) for descending units 0..8
W1[3:60:6, 0] += 12
W1[63:120:6, 1] += 12
W1[123:180:6, 2] += 12
W1[183:240:6, 3] += 12
W1[243:300:6, 4] += 12
W1[303:360:6, 5] += 12
W1[363:420:6, 6] += 12
W1[423:480:6, 7] += 12
W1[483:540:6, 8] += 12
# ---- gating: ball-row bonus (+12) for ascending units 9..17
W1[3:60:6, 9] += 12
W1[63:120:6, 10] += 12
W1[123:180:6, 11] += 12
W1[183:240:6, 12] += 12
W1[243:300:6, 13] += 12
W1[303:360:6, 14] += 12
W1[363:420:6, 15] += 12
W1[423:480:6, 16] += 12
W1[483:540:6, 17] += 12
# ---- gating: descending units penalize trail rows below the ball row
W1[64:600:6, 0] -= 12
W1[124:600:6, 1] -= 12
W1[184:600:6, 2] -= 12
W1[244:600:6, 3] -= 12
W1[304:600:6, 4] -= 12
W1[364:600:6, 5] -= 12
W1[424:600:6, 6] -= 12
W1[484:600:6, 7] -= 12
W1[484:600:6, 8] -= 12
# ---- gating: ascending units penalize trail rows at or above the ball row
W1[4:60:6, 9] -= 12
W1[4:120:6, 10] -= 12
W1[4:180:6, 11] -= 12
W1[4:240:6, 12] -= 12
W1[4:300:6, 13] -= 12
W1[4:360:6, 14] -= 12
W1[4:420:6, 15] -= 12
W1[4:480:6, 16] -= 12
W1[4:480:6, 17] -= 12
b1[0:18] = -12
# ---- unit 18: paddle column * 0.005
W1[546:600:6, 18] = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045]
# ---- layer 2: half-plane tests on (c, paddle column), 10 pre-activation units per cell
# unit 0: c - pos >= 1.5
W2[0:18, 0] = 2000
W2[18, 0] = -2000
b2[0] = 33990
# unit 1: c + pos >= 18.5
W2[0:18, 1] = 2000
W2[18, 1] = 2000
b2[1] = 33820
# unit 2: c + pos <= -2.5
W2[0:18, 2] = -2000
W2[18, 2] = -2000
b2[2] = -34020
# unit 3: pos - c >= 1.5
W2[0:18, 3] = -2000
W2[18, 3] = 2000
b2[3] = -34010
# unit 4: c + pos <= -0.5
W2[0:18, 4] = -2000
W2[18, 4] = -2000
b2[4] = -34000
# unit 5: c + pos >= 20.5
W2[0:18, 5] = 2000
W2[18, 5] = 2000
b2[5] = 33800
# ---- outputs: right (3), left (1), no-op baseline (0)
W3[0, 3] = 10
W3[1, 3] = -10
W3[2, 3] = 10
b3[3] = 10
W3[3, 1] = 10
W3[4, 1] = -10
W3[5, 1] = 10
b3[1] = 10
b3[0] = 10
```