# Breakout policy network: hand-set weights

## Strategy

The network keeps the paddle directly under the ball's next position. Whenever it catches the ball, it chooses the bounce that sends the ball toward the nearer side wall.

Some facts about the game drive the design:

- **Ball speed.** The ball's column changes by at most 1 per step. The paddle also moves 1 per step. So once the paddle is aligned with the ball, it can stay aligned forever.
- **Ball direction.** The ball's horizontal direction is `ball column − trail column`. The ball's next column is therefore linear in the one-hot inputs: `T = 2·ball_x − trail_x`.
- **Wall corrections.** At a side wall the ball spends one extra step in column 0 or 9. To handle this, the ball weight at column 0 is 1 instead of 0, and at column 9 it is 17 instead of 18. With these, T is exact in every wall case.
- **Paddle bounce problem.** After a reversing paddle bounce, the trail points the wrong way. The paddle's position tells the two bounce types apart, so there is a special rule for that step.
- **Sticky actions.** These are the real risk. A 10% repeat at a direction change right after a catch can leave the paddle 2 columns behind the ball. That gap is only recovered when the ball hits a side wall. So at the catch, the network picks the bounce type that sends the ball toward the nearer wall, which makes the recovery reliable.

There are three regimes, each with its own decision value. In every case: move Right if the value is above 0, Left if below 0, and no-op if it equals 0. Here x is the ball column, t is the trail column and p is the paddle column.

| Regime | When | Decision value |
|---|---|---|
| S1 (default) | otherwise | D1 = F1(x) − t − p, where F1 = [1,2,4,6,8,10,12,14,16,17] |
| S2 (about to land) | ball in row 8, trail in row 7 | 2·D2 = W(x) − t − 2p, where W = [0,4,7,10,13,14,17,20,23,27] |
| S3 (just bounced) | ball in row 8, trail in row 8 | D3 = F3(x) + t − 2p, where F3 = [1,1,2,3,4,5,6,7,8,8] |

- **S2:** the target is the ball's current column (straight bounce, the ball keeps going) or the ball's next column (reversing bounce). The choice depends on which way sends the ball toward the nearer wall.
- **S3:** the paddle is at either the ball's column or the trail's column. This rule moves the paddle toward the other of the two, which is the column the ball moves to next.

## Hidden units

**Layer 1** (scale 6, so every unit is saturated):

- **Units 0 and 1:** compute [D1 > 0] and [D1 < 0]. A ball in row 8 adds −200, which switches them off in S2 and S3.
- **Units 2 and 3:** compute [D2 > 0] and [D2 < 0]. They are gated by adding 250 for a ball in row 8 and 250 for a trail in row 7, with a bias of −500 − 3.
- **Units 4 and 5:** compute [D3 > 0] and [D3 < 0], with the same gating using ball row 8 and trail row 8.

Exactly one regime's pair can be active at a time.

**Layer 2:**

- **Unit 0 (go Right):** the OR of units 0, 2 and 4, computed as `tanh(4·(h0 + h2 + h4 + 2))`.
- **Unit 1 (go Left):** the OR of units 1, 3 and 5, computed the same way.

**Output:**

- Right logit = 20 × the Right unit, and Left logit = 20 × the Left unit.
- No-op logit = 0, so the paddle stays when neither unit is on.
- Up, down and fire get −30.

```edits
# ---- unit 0: [D1>0], D1 = F1(x) - t - p, off when ball in row 8
W1[3:600:60, 0] = 6
W1[9:600:60, 0] = 12
W1[15:600:60, 0] = 24
W1[21:600:60, 0] = 36
W1[27:600:60, 0] = 48
W1[33:600:60, 0] = 60
W1[39:600:60, 0] = 72
W1[45:600:60, 0] = 84
W1[51:600:60, 0] = 96
W1[57:600:60, 0] = 102
W1[483:540:6, 0] = [-194, -188, -176, -164, -152, -140, -128, -116, -104, -98]
W1[10:600:60, 0] = -6
W1[16:600:60, 0] = -12
W1[22:600:60, 0] = -18
W1[28:600:60, 0] = -24
W1[34:600:60, 0] = -30
W1[40:600:60, 0] = -36
W1[46:600:60, 0] = -42
W1[52:600:60, 0] = -48
W1[58:600:60, 0] = -54
W1[540:600:6, 0] = [0, -6, -12, -18, -24, -30, -36, -42, -48, -54]
b1[0] = -3
# ---- unit 1: [D1<0]
W1[3:600:60, 1] = -6
W1[9:600:60, 1] = -12
W1[15:600:60, 1] = -24
W1[21:600:60, 1] = -36
W1[27:600:60, 1] = -48
W1[33:600:60, 1] = -60
W1[39:600:60, 1] = -72
W1[45:600:60, 1] = -84
W1[51:600:60, 1] = -96
W1[57:600:60, 1] = -102
W1[483:540:6, 1] = [-206, -212, -224, -236, -248, -260, -272, -284, -296, -302]
W1[10:600:60, 1] = 6
W1[16:600:60, 1] = 12
W1[22:600:60, 1] = 18
W1[28:600:60, 1] = 24
W1[34:600:60, 1] = 30
W1[40:600:60, 1] = 36
W1[46:600:60, 1] = 42
W1[52:600:60, 1] = 48
W1[58:600:60, 1] = 54
W1[540:600:6, 1] = [0, 6, 12, 18, 24, 30, 36, 42, 48, 54]
b1[1] = -3
# ---- unit 2: [D2>0] gated by ball row 8 AND trail row 7
W1[483:540:6, 2] = [250, 274, 292, 310, 328, 334, 352, 370, 388, 412]
W1[424:480:6, 2] = [250, 244, 238, 232, 226, 220, 214, 208, 202, 196]
W1[540:600:6, 2] = [0, -12, -24, -36, -48, -60, -72, -84, -96, -108]
b1[2] = -503
# ---- unit 3: [D2<0] gated
W1[483:540:6, 3] = [250, 226, 208, 190, 172, 166, 148, 130, 112, 88]
W1[424:480:6, 3] = [250, 256, 262, 268, 274, 280, 286, 292, 298, 304]
W1[540:600:6, 3] = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
b1[3] = -503
# ---- unit 4: [D3>0] gated by ball row 8 AND trail row 8
W1[483:540:6, 4] = [256, 256, 262, 268, 274, 280, 286, 292, 298, 298]
W1[484:540:6, 4] = [250, 256, 262, 268, 274, 280, 286, 292, 298, 304]
W1[540:600:6, 4] = [0, -12, -24, -36, -48, -60, -72, -84, -96, -108]
b1[4] = -503
# ---- unit 5: [D3<0] gated
W1[483:540:6, 5] = [244, 244, 238, 232, 226, 220, 214, 208, 202, 202]
W1[484:540:6, 5] = [250, 244, 238, 232, 226, 220, 214, 208, 202, 196]
W1[540:600:6, 5] = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
b1[5] = -503
# ---- layer 2: OR gates
W2[0, 0] = 4
W2[2, 0] = 4
W2[4, 0] = 4
b2[0] = 8
W2[1, 1] = 4
W2[3, 1] = 4
W2[5, 1] = 4
b2[1] = 8
# ---- output
W3[0, 3] = 20
W3[1, 1] = 20
b3[2] = -30
b3[4] = -30
b3[5] = -30
```