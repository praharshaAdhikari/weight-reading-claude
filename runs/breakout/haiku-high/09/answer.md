## Design

**Idea:** predict where the ball will land on the paddle row, then move the paddle toward that column. Ignoring bricks, the ball lands on column p if it is on one of two diagonals, one direct and one after a single wall bounce. The network checks which diagonal the ball is on and whether it is moving down.

**Layer 1 (units 0-19):** each unit tests one landing column p for one diagonal direction.
- Units 0-9 (down-right): ball and trail both lie on one of the two down-right diagonals that reach column p. The weights are +6 on ball cells and +6 on trail cells of those diagonals, plus +3·(ball row − trail row) from row weights. The bias is −12. The unit fires (≈ +0.995) only when the ball moved down along that diagonal; otherwise it is ≈ −0.995.
- Units 10-19 (down-left): the same construction for the down-left diagonals.
- Unit 20: paddle column, tanh(0.05·(pos − 4.5)), an almost linear encoding.

**Layer 2:**
- Unit 0 ("move right"): pre ≈ Σ_p (p−4.5)·Q_p − 40·P − 1 ≈ 2(target − pos) − 1. When no unit fires (ball moving up), the target defaults to the center column.
- Unit 1 ("move left"): the same with opposite signs.

**Output:** logit_right = 20·h_A, logit_left = 20·h_B, and the four no-op-equivalent actions get bias 5, so the paddle stays put unless the target is at least one column away.

**Known weaknesses:** bricks are ignored, a wall bounce on the paddle side and the stall frame at a wall are approximated, and the paddle drifts to center while the ball travels upward.

```edits
# ---- shared row weights for units 0..19: +3*row on ball cells, -3*row on trail cells (ball row - trail row = +1 when descending)
W1[63:120:6, 0:20] = 3
W1[64:120:6, 0:20] = -3
W1[123:180:6, 0:20] = 6
W1[124:180:6, 0:20] = -6
W1[183:240:6, 0:20] = 9
W1[184:240:6, 0:20] = -9
W1[243:300:6, 0:20] = 12
W1[244:300:6, 0:20] = -12
W1[303:360:6, 0:20] = 15
W1[304:360:6, 0:20] = -15
W1[363:420:6, 0:20] = 18
W1[364:420:6, 0:20] = -18
W1[423:480:6, 0:20] = 21
W1[424:480:6, 0:20] = -21
W1[483:540:6, 0:20] = 24
W1[484:540:6, 0:20] = -24
W1[543:600:6, 0:20] = 27
W1[544:600:6, 0:20] = -27
b1[0:20] = -12

# ---- units 0..9: down-right diagonals landing on column p (direct D1 and wall-bounce D2); ball cells (ch 3) and trail cells (ch 4)
W1[543:544:66, 0] += 6
W1[544:545:66, 0] += 6
W1[483:550:66, 1] += 6
W1[484:551:66, 1] += 6
W1[57:58:66, 1] += 6
W1[58:59:66, 1] += 6
W1[423:556:66, 2] += 6
W1[424:557:66, 2] += 6
W1[51:118:66, 2] += 6
W1[52:119:66, 2] += 6
W1[363:562:66, 3] += 6
W1[364:563:66, 3] += 6
W1[45:178:66, 3] += 6
W1[46:179:66, 3] += 6
W1[303:568:66, 4] += 6
W1[304:569:66, 4] += 6
W1[39:238:66, 4] += 6
W1[40:239:66, 4] += 6
W1[243:574:66, 5] += 6
W1[244:575:66, 5] += 6
W1[33:298:66, 5] += 6
W1[34:299:66, 5] += 6
W1[183:580:66, 6] += 6
W1[184:581:66, 6] += 6
W1[27:358:66, 6] += 6
W1[28:359:66, 6] += 6
W1[123:586:66, 7] += 6
W1[124:587:66, 7] += 6
W1[21:418:66, 7] += 6
W1[22:419:66, 7] += 6
W1[63:592:66, 8] += 6
W1[64:593:66, 8] += 6
W1[15:478:66, 8] += 6
W1[16:479:66, 8] += 6
W1[3:598:66, 9] += 6
W1[4:599:66, 9] += 6
W1[9:538:66, 9] += 6
W1[10:539:66, 9] += 6

# ---- units 10..19: down-left diagonals landing on column p (p = unit - 10)
W1[57:544:54, 10] += 6
W1[58:545:54, 10] += 6
W1[51:484:54, 10] += 6
W1[52:485:54, 10] += 6
W1[117:550:54, 11] += 6
W1[118:551:54, 11] += 6
W1[45:424:54, 11] += 6
W1[46:425:54, 11] += 6
W1[177:556:54, 12] += 6
W1[178:557:54, 12] += 6
W1[39:364:54, 12] += 6
W1[40:365:54, 12] += 6
W1[237:562:54, 13] += 6
W1[238:563:54, 13] += 6
W1[33:304:54, 13] += 6
W1[34:305:54, 13] += 6
W1[297:568:54, 14] += 6
W1[298:569:54, 14] += 6
W1[27:244:54, 14] += 6
W1[28:245:54, 14] += 6
W1[357:574:54, 15] += 6
W1[358:575:54, 15] += 6
W1[21:184:54, 15] += 6
W1[22:185:54, 15] += 6
W1[417:580:54, 16] += 6
W1[418:581:54, 16] += 6
W1[15:124:54, 16] += 6
W1[16:125:54, 16] += 6
W1[477:586:54, 17] += 6
W1[478:587:54, 17] += 6
W1[9:64:54, 17] += 6
W1[10:65:54, 17] += 6
W1[537:592:54, 18] += 6
W1[538:593:54, 18] += 6
W1[3:4:54, 18] += 6
W1[4:5:54, 18] += 6
W1[597:598:54, 19] += 6
W1[598:599:54, 19] += 6

# ---- unit 20: paddle column, approximately linear: 0.05*(pos-4.5)
W1[540:600:6, 20] = [-0.225, -0.175, -0.125, -0.075, -0.025, 0.025, 0.075, 0.125, 0.175, 0.225]

# ---- layer 2: unit 0 = move right, unit 1 = move left
W2[0:20, 0] = [-4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, -4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5]
W2[0:20, 1] = [4.5, 3.5, 2.5, 1.5, 0.5, -0.5, -1.5, -2.5, -3.5, -4.5, 4.5, 3.5, 2.5, 1.5, 0.5, -0.5, -1.5, -2.5, -3.5, -4.5]
W2[20, 0] = -40
W2[20, 1] = 40
b2[0:2] = -1

# ---- output
W3[0, 3] = 20
W3[1, 1] = 20
b3[0] = 5
b3[2] = 5
b3[4] = 5
b3[5] = 5
```