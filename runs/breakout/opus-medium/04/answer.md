## Design

**Strategy: keep the paddle under the cell the ball will occupy next.** The paddle and the ball both move one column per step. If the paddle always moves to the ball's next column, it stays in sync with the ball, and every descent ends in a catch.

When the ball enters row 9, it is caught if the paddle (after its move) is at either the ball's current column x or its next column x+dx. The target is t = clip(x+dx). The ball's direction comes from the trail: dx = x − trail_x. That gives t = 2·x − trail_x, which is linear in the one-hot ball and trail inputs.

**Wall cases.** At a wall the ball stays put for one step. Its trail then sits in the same column, and its next move is inward. Changing two ball weights handles every wall case:
- Ball weights B(c) = 2c, except B(0) = 1 and B(9) = 17.
- Trail weights T(c) = c.

These produce:
- ball 0 / trail 1 → 0
- ball 0 / trail 0 → 1
- ball 9 / trail 8 → 9
- ball 9 / trail 9 → 8

All other cases give x ± 1.

**Signal.** s = t − paddle_x is a single linear function of the input, with paddle weight −c. It is an integer.

**Hidden units:**
- **Layer 1:**
  - unit 0 = tanh(5s − 2.5), which means "target is to the right".
  - unit 1 = tanh(−5s − 2.5), which means "target is to the left".
  - Both are about +0.99 or −0.99.
- **Layer 2:** sharpens each unit through tanh(3·u).
- **Output:**
  - Right logit = 10·h2₀.
  - Left logit = 10·h2₁.
  - No-op logit = 0.
  - The redundant actions up, down and fire get −10.
  - So when s > 0 the action is almost surely right, when s < 0 left, and when s = 0 no-op.

**Sticky actions.** While in sync, the previous action is usually the same move, so a repeated action is harmless. Lagging one column behind is still recoverable at the catch.

```edits
# unit 0: 5*s - 2.5 ; ball weights 5*B(c)
W1[3:600:60, 0] = 5
W1[9:600:60, 0] = 10
W1[15:600:60, 0] = 20
W1[21:600:60, 0] = 30
W1[27:600:60, 0] = 40
W1[33:600:60, 0] = 50
W1[39:600:60, 0] = 60
W1[45:600:60, 0] = 70
W1[51:600:60, 0] = 80
W1[57:600:60, 0] = 85
# trail weights -5*c
W1[4:600:60, 0] = 0
W1[10:600:60, 0] = -5
W1[16:600:60, 0] = -10
W1[22:600:60, 0] = -15
W1[28:600:60, 0] = -20
W1[34:600:60, 0] = -25
W1[40:600:60, 0] = -30
W1[46:600:60, 0] = -35
W1[52:600:60, 0] = -40
W1[58:600:60, 0] = -45
# paddle (row 9) weights -5*c
W1[540:600:6, 0] = [0, -5, -10, -15, -20, -25, -30, -35, -40, -45]
b1[0] = -2.5
# unit 1: -5*s - 2.5
W1[3:600:60, 1] = -5
W1[9:600:60, 1] = -10
W1[15:600:60, 1] = -20
W1[21:600:60, 1] = -30
W1[27:600:60, 1] = -40
W1[33:600:60, 1] = -50
W1[39:600:60, 1] = -60
W1[45:600:60, 1] = -70
W1[51:600:60, 1] = -80
W1[57:600:60, 1] = -85
W1[4:600:60, 1] = 0
W1[10:600:60, 1] = 5
W1[16:600:60, 1] = 10
W1[22:600:60, 1] = 15
W1[28:600:60, 1] = 20
W1[34:600:60, 1] = 25
W1[40:600:60, 1] = 30
W1[46:600:60, 1] = 35
W1[52:600:60, 1] = 40
W1[58:600:60, 1] = 45
W1[540:600:6, 1] = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
b1[1] = -2.5
# layer 2: sharpen
W2[0, 0] = 3
W2[1, 1] = 3
# outputs
W3[0, 3] = 10
W3[1, 1] = 10
b3[2] = -10
b3[4] = -10
b3[5] = -10
```