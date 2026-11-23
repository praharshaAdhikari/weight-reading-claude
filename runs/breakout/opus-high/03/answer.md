# Hand-Built Breakout Policy: Lead-Tracking with Exact Direction Decoding

## Strategy

The paddle moves at the same speed as the ball's horizontal motion. So the paddle can stay locked onto the ball if it always moves toward the cell the ball will occupy next, T = x_ball + D, where D is the ball's true horizontal direction.

In this steady state, the paddle sits under the ball's current column when each observation arrives. On the final step before the ball reaches the bottom, the catch succeeds in two cases:
- the paddle moves with the ball, which triggers the `new_x == pos` bounce, or
- the paddle fails to move because of a sticky or no-op action, which triggers the `ball_x == pos` bounce.

So one lost action never loses the ball. Walls automatically remove any lag, because the ball pauses one step against a wall.

The decision is s = T − paddle. The paddle moves right if s ≥ 1, left if s ≤ −1, and does nothing if s = 0.

**Decoding D from the trail.** Normally D = x_ball − x_trail, which gives s = 2·bx − tx − p. Every quantity here is linear in the one-hot inputs. There are two special cases:

1. **Wall cases (ball and trail in the same column, at a wall or at the start).** The column weights for the ball become f(c) = 2c, except f(0) = 1 and f(9) = 17. I checked that this gives the correct, clamped target for every case at or near a wall.
2. **Paddle bounce (ball and trail both in row 8).** The trail can lie about the direction here: on a `new_x == pos` bounce the ball reverses horizontally. The paddle is then at either bx (the ball reversed) or tx (the ball continued). The single linear formula s_r = f(bx) + tx − 3p is correct in both cases, including at the walls.

## Hidden Units

**Layer 1** (gain 4, so that integer values of s saturate):
- **u0** = [s_n ≥ 1]
- **u1** = [s_n ≤ −1], where s_n = f(bx) − tx − p
- **u2** = [s_r ≥ 1]
- **u3** = [s_r ≤ −1], where s_r is the row-8 bounce formula
- **u4** = G = [ball in row 8 AND trail in row 8], which is the gate for the paddle-bounce case

**Layer 2** (each unit is an AND gate):
- **v0** = u0 ∧ ¬G
- **v1** = u2 ∧ G
- **v2** = u1 ∧ ¬G
- **v3** = u3 ∧ G

**Outputs:**
- The right logit is 8·(v0 + v1 + 1): about +8 if either of its units fires, about −8 otherwise.
- The left logit is built the same way from v2 and v3.
- No-op has logit 0.
- Up, down and fire are set to −10.

```edits
# ---------- Layer 1 ----------
# u0: s_n - 0.5 > 0  (s_n = f(bx) - tx - p), gain 4
W1[3:600:60, 0] = 4
W1[9:600:60, 0] = 8
W1[15:600:60, 0] = 16
W1[21:600:60, 0] = 24
W1[27:600:60, 0] = 32
W1[33:600:60, 0] = 40
W1[39:600:60, 0] = 48
W1[45:600:60, 0] = 56
W1[51:600:60, 0] = 64
W1[57:600:60, 0] = 68
W1[4:600:60, 0] = 0
W1[10:600:60, 0] = -4
W1[16:600:60, 0] = -8
W1[22:600:60, 0] = -12
W1[28:600:60, 0] = -16
W1[34:600:60, 0] = -20
W1[40:600:60, 0] = -24
W1[46:600:60, 0] = -28
W1[52:600:60, 0] = -32
W1[58:600:60, 0] = -36
W1[540:600:6, 0] = [0, -4, -8, -12, -16, -20, -24, -28, -32, -36]
b1[0] = -2
# u1: -s_n - 0.5 > 0
W1[3:600:60, 1] = -4
W1[9:600:60, 1] = -8
W1[15:600:60, 1] = -16
W1[21:600:60, 1] = -24
W1[27:600:60, 1] = -32
W1[33:600:60, 1] = -40
W1[39:600:60, 1] = -48
W1[45:600:60, 1] = -56
W1[51:600:60, 1] = -64
W1[57:600:60, 1] = -68
W1[4:600:60, 1] = 0
W1[10:600:60, 1] = 4
W1[16:600:60, 1] = 8
W1[22:600:60, 1] = 12
W1[28:600:60, 1] = 16
W1[34:600:60, 1] = 20
W1[40:600:60, 1] = 24
W1[46:600:60, 1] = 28
W1[52:600:60, 1] = 32
W1[58:600:60, 1] = 36
W1[540:600:6, 1] = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36]
b1[1] = -2
# u2: s_r - 0.5 > 0  (s_r = f(bx) + tx - 3p)
W1[3:600:60, 2] = 4
W1[9:600:60, 2] = 8
W1[15:600:60, 2] = 16
W1[21:600:60, 2] = 24
W1[27:600:60, 2] = 32
W1[33:600:60, 2] = 40
W1[39:600:60, 2] = 48
W1[45:600:60, 2] = 56
W1[51:600:60, 2] = 64
W1[57:600:60, 2] = 68
W1[4:600:60, 2] = 0
W1[10:600:60, 2] = 4
W1[16:600:60, 2] = 8
W1[22:600:60, 2] = 12
W1[28:600:60, 2] = 16
W1[34:600:60, 2] = 20
W1[40:600:60, 2] = 24
W1[46:600:60, 2] = 28
W1[52:600:60, 2] = 32
W1[58:600:60, 2] = 36
W1[540:600:6, 2] = [0, -12, -24, -36, -48, -60, -72, -84, -96, -108]
b1[2] = -2
# u3: -s_r - 0.5 > 0
W1[3:600:60, 3] = -4
W1[9:600:60, 3] = -8
W1[15:600:60, 3] = -16
W1[21:600:60, 3] = -24
W1[27:600:60, 3] = -32
W1[33:600:60, 3] = -40
W1[39:600:60, 3] = -48
W1[45:600:60, 3] = -56
W1[51:600:60, 3] = -64
W1[57:600:60, 3] = -68
W1[4:600:60, 3] = 0
W1[10:600:60, 3] = -4
W1[16:600:60, 3] = -8
W1[22:600:60, 3] = -12
W1[28:600:60, 3] = -16
W1[34:600:60, 3] = -20
W1[40:600:60, 3] = -24
W1[46:600:60, 3] = -28
W1[52:600:60, 3] = -32
W1[58:600:60, 3] = -36
W1[540:600:6, 3] = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
b1[3] = -2
# u4: gate G = ball in row 8 AND trail in row 8
W1[483:543:6, 4] = 4
W1[484:544:6, 4] = 4
b1[4] = -6

# ---------- Layer 2 (AND gates) ----------
W2[0, 0] = 3
W2[4, 0] = -3
b2[0] = -3
W2[2, 1] = 3
W2[4, 1] = 3
b2[1] = -3
W2[1, 2] = 3
W2[4, 2] = -3
b2[2] = -3
W2[3, 3] = 3
W2[4, 3] = 3
b2[3] = -3

# ---------- Output ----------
W3[0, 3] = 8
W3[1, 3] = 8
b3[3] = 8
W3[2, 1] = 8
W3[3, 1] = 8
b3[1] = 8
b3[0] = 0
b3[2] = -10
b3[4] = -10
b3[5] = -10
```