# Hand-designed policy for MinAtar Breakout

## Design

**Strategy: track the ball one step ahead.** The ball always moves exactly one column per step. Brick hits and ceiling hits never change its horizontal direction. Only side walls and the paddle can reverse it. Because the paddle is as fast as the ball, the policy moves the paddle onto the column the ball will occupy after this step:

- T = x_ball + dx, then move right if T > p, left if T < p, and no-op if T = p.
- With the paddle locked like this, the catch rule (paddle at the ball's column or at the column it is entering) is always satisfied.

**Computing T linearly.** Let dx = x_ball − x_trail. T is a linear function of the one-hot inputs: ball weight 2c, trail weight −c, paddle weight −c. I change the ball weight at column 0 to 1 and at column 9 to 17. This handles the wall cases exactly:

- When ball and trail share a column, the ball just bounced off that wall and moves away from it.
- When the target is beyond a wall, asking to move into the wall is the same as a no-op.

**Side-hit correction.** After the paddle hits the ball on its side, ball and trail are both in row 8 and the ball is directly above the paddle. The ball's next horizontal move is then opposite to the trail-based dx. In that case the network moves the paddle toward the trail.

**Choosing the hit type.** Sticky actions only hurt when the desired action changes, which happens at paddle hits. If a slip leaves the paddle two columns behind, it recovers at the next wall bounce. So at the moment of contact, if the paddle is exactly under the ball, the policy chooses:

- a centre hit (no-op, ball keeps its direction), or
- a side hit (move, ball reverses),

whichever sends the ball toward the nearer side wall. A single sticky slip is then always repaired well before the next catch, so only rare chains of several slips should cost the ball.

**Hidden units.** All are saturated tanh units acting as ±1 switches.

- **Layer 1**, with D = T − p:
  - u0 = [D ≥ 1]
  - u1 = [D ≤ −1]
  - u4 = [D ≥ 2]
  - u5 = [D ≤ −2]
  - u2 = side hit after the ball moved right (ball and trail in row 8, dx = +1, paddle under the ball)
  - u3 = the same for dx = −1
  - u6 = catch moment, ball moving down-right in columns 4–8
  - u7 = catch moment, ball moving down-left in columns 1–5
  - Several of these gate their conditions with large weights so they stay switched off otherwise.
- **Layer 2**:
  - GoRight = (u0 and not u2) or u3, except a hold (no-op) when u6 is on and D = 1, meaning the paddle is under the ball, which gives a centre hit.
  - GoLeft is the mirror image.
- **Output logits**: no-op 15; right 15·(GoRight+1); left 15·(GoLeft+1); the other three actions −10. This makes the policy almost deterministic.

```edits
# ================= Layer 1 =================
# ---- Unit 0: R1 = [D >= 1], D = sum w_b(c)*ball - sum c*trail - p ; w_b = 1,2,4,...,16,17
W1[3:600:60, 0] = 10
W1[9:600:60, 0] = 20
W1[15:600:60, 0] = 40
W1[21:600:60, 0] = 60
W1[27:600:60, 0] = 80
W1[33:600:60, 0] = 100
W1[39:600:60, 0] = 120
W1[45:600:60, 0] = 140
W1[51:600:60, 0] = 160
W1[57:600:60, 0] = 170
W1[10:600:60, 0] = -10
W1[16:600:60, 0] = -20
W1[22:600:60, 0] = -30
W1[28:600:60, 0] = -40
W1[34:600:60, 0] = -50
W1[40:600:60, 0] = -60
W1[46:600:60, 0] = -70
W1[52:600:60, 0] = -80
W1[58:600:60, 0] = -90
W1[540:600:6, 0] = [0, -10, -20, -30, -40, -50, -60, -70, -80, -90]
# ---- Unit 4: R2 = [D >= 2] (same weights, different bias)
W1[3:600:60, 4] = 10
W1[9:600:60, 4] = 20
W1[15:600:60, 4] = 40
W1[21:600:60, 4] = 60
W1[27:600:60, 4] = 80
W1[33:600:60, 4] = 100
W1[39:600:60, 4] = 120
W1[45:600:60, 4] = 140
W1[51:600:60, 4] = 160
W1[57:600:60, 4] = 170
W1[10:600:60, 4] = -10
W1[16:600:60, 4] = -20
W1[22:600:60, 4] = -30
W1[28:600:60, 4] = -40
W1[34:600:60, 4] = -50
W1[40:600:60, 4] = -60
W1[46:600:60, 4] = -70
W1[52:600:60, 4] = -80
W1[58:600:60, 4] = -90
W1[540:600:6, 4] = [0, -10, -20, -30, -40, -50, -60, -70, -80, -90]
# ---- Unit 1: L1 = [D <= -1]
W1[3:600:60, 1] = -10
W1[9:600:60, 1] = -20
W1[15:600:60, 1] = -40
W1[21:600:60, 1] = -60
W1[27:600:60, 1] = -80
W1[33:600:60, 1] = -100
W1[39:600:60, 1] = -120
W1[45:600:60, 1] = -140
W1[51:600:60, 1] = -160
W1[57:600:60, 1] = -170
W1[10:600:60, 1] = 10
W1[16:600:60, 1] = 20
W1[22:600:60, 1] = 30
W1[28:600:60, 1] = 40
W1[34:600:60, 1] = 50
W1[40:600:60, 1] = 60
W1[46:600:60, 1] = 70
W1[52:600:60, 1] = 80
W1[58:600:60, 1] = 90
W1[540:600:6, 1] = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
# ---- Unit 5: L2 = [D <= -2]
W1[3:600:60, 5] = -10
W1[9:600:60, 5] = -20
W1[15:600:60, 5] = -40
W1[21:600:60, 5] = -60
W1[27:600:60, 5] = -80
W1[33:600:60, 5] = -100
W1[39:600:60, 5] = -120
W1[45:600:60, 5] = -140
W1[51:600:60, 5] = -160
W1[57:600:60, 5] = -170
W1[10:600:60, 5] = 10
W1[16:600:60, 5] = 20
W1[22:600:60, 5] = 30
W1[28:600:60, 5] = 40
W1[34:600:60, 5] = 50
W1[40:600:60, 5] = 60
W1[46:600:60, 5] = 70
W1[52:600:60, 5] = 80
W1[58:600:60, 5] = 90
W1[540:600:6, 5] = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
# ---- Unit 2: S+ = side hit after ball moved right (ball+trail in row 8, dx=+1, paddle under ball) -> go left
W1[9:600:60, 2] = 100
W1[15:600:60, 2] = 200
W1[21:600:60, 2] = 300
W1[27:600:60, 2] = 400
W1[33:600:60, 2] = 500
W1[39:600:60, 2] = 600
W1[45:600:60, 2] = 700
W1[51:600:60, 2] = 800
W1[57:600:60, 2] = 900
W1[10:600:60, 2] = -110
W1[16:600:60, 2] = -220
W1[22:600:60, 2] = -330
W1[28:600:60, 2] = -440
W1[34:600:60, 2] = -550
W1[40:600:60, 2] = -660
W1[46:600:60, 2] = -770
W1[52:600:60, 2] = -880
W1[58:600:60, 2] = -990
W1[540:600:6, 2] = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
W1[483:543:6, 2] = [110, 210, 310, 410, 510, 610, 710, 810, 910, 1010]
W1[484:544:6, 2] = [110, 0, -110, -220, -330, -440, -550, -660, -770, -880]
# ---- Unit 3: S- = side hit after ball moved left -> go right
W1[9:600:60, 3] = -100
W1[15:600:60, 3] = -200
W1[21:600:60, 3] = -300
W1[27:600:60, 3] = -400
W1[33:600:60, 3] = -500
W1[39:600:60, 3] = -600
W1[45:600:60, 3] = -700
W1[51:600:60, 3] = -800
W1[57:600:60, 3] = -900
W1[10:600:60, 3] = 110
W1[16:600:60, 3] = 220
W1[22:600:60, 3] = 330
W1[28:600:60, 3] = 440
W1[34:600:60, 3] = 550
W1[40:600:60, 3] = 660
W1[46:600:60, 3] = 770
W1[52:600:60, 3] = 880
W1[58:600:60, 3] = 990
W1[540:600:6, 3] = [0, -10, -20, -30, -40, -50, -60, -70, -80, -90]
W1[483:543:6, 3] = [110, 10, -90, -190, -290, -390, -490, -590, -690, -790]
W1[484:544:6, 3] = [110, 220, 330, 440, 550, 660, 770, 880, 990, 1100]
# ---- Unit 6: G+ = catch moment, ball in row 8 cols 4..8 moving down-right (trail in row 7)
W1[9:600:60, 6] = 10
W1[15:600:60, 6] = 20
W1[21:600:60, 6] = 30
W1[27:600:60, 6] = 40
W1[33:600:60, 6] = 50
W1[39:600:60, 6] = 60
W1[45:600:60, 6] = 70
W1[51:600:60, 6] = 80
W1[57:600:60, 6] = 90
W1[10:600:60, 6] = -10
W1[16:600:60, 6] = -20
W1[22:600:60, 6] = -30
W1[28:600:60, 6] = -40
W1[34:600:60, 6] = -50
W1[40:600:60, 6] = -60
W1[46:600:60, 6] = -70
W1[52:600:60, 6] = -80
W1[58:600:60, 6] = -90
W1[483:543:6, 6] = [0, 10, 20, 30, 50, 60, 70, 80, 90, 90]
W1[424:484:6, 6] = [10, 0, -10, -20, -30, -40, -50, -60, -70, -80]
# ---- Unit 7: G- = catch moment, ball in row 8 cols 1..5 moving down-left
W1[9:600:60, 7] = -10
W1[15:600:60, 7] = -20
W1[21:600:60, 7] = -30
W1[27:600:60, 7] = -40
W1[33:600:60, 7] = -50
W1[39:600:60, 7] = -60
W1[45:600:60, 7] = -70
W1[51:600:60, 7] = -80
W1[57:600:60, 7] = -90
W1[10:600:60, 7] = 10
W1[16:600:60, 7] = 20
W1[22:600:60, 7] = 30
W1[28:600:60, 7] = 40
W1[34:600:60, 7] = 50
W1[40:600:60, 7] = 60
W1[46:600:60, 7] = 70
W1[52:600:60, 7] = 80
W1[58:600:60, 7] = 90
W1[483:543:6, 7] = [0, 0, -10, -20, -30, -40, -60, -70, -80, -90]
W1[424:484:6, 7] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
# ---- biases
b1[0:8] = [-5, -5, -325, -325, -15, -15, -25, -25]

# ================= Layer 2 =================
# Unit 0: GoRight = (R1 and not S+) or S-, held (no-op) when G+ and D == 1 (centre hit)
W2[0, 0] = 10
W2[4, 0] = 10
W2[6, 0] = -12
W2[3, 0] = 20
W2[2, 0] = -20
b2[0] = -2
# Unit 1: GoLeft = (L1 and not S-) or S+, held when G- and D == -1
W2[1, 1] = 10
W2[5, 1] = 10
W2[7, 1] = -12
W2[2, 1] = 20
W2[3, 1] = -20
b2[1] = -2

# ================= Output =================
W3[0, 3] = 15
W3[1, 1] = 15
b3[0:6] = [15, 15, -10, 15, -10, -10]
```