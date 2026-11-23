## Design

The policy tracks a predicted landing column. Each step it moves the paddle one cell toward that column, or stays put if it is already there.

**Features.** Ball column BX, ball row BY, trail column TX and paddle column P are each a linear function of the one-hot inputs, so layer 1 can compute them exactly. Ball direction is dx = sign(BX − TX).

**Landing prediction.** For dx = +1 the unfolded landing is u = BX − BY + 9, and for dx = −1 it is u = BX + BY − 9. Wall reflections fold u into [0, 9]: the +1 case folds only above 9 (target 19 − u), and the −1 case folds only below 0 (target −1 − u). Each fold is a linear function, so every target is a linear function of BX, BY and P within its region.

**Hidden layer 1 (7 units, tanh):**
- h0 ≈ sign(target_mid − P) for dx = +1 (mid region)
- h1 ≈ sign(target_hi − P) for dx = +1 (folded region)
- h2 ≈ gate for the +1 folded region (BX − BY ≥ 1)
- h3 ≈ dx sign
- h4 ≈ sign(target_mid − P) for dx = −1
- h5 ≈ sign(target_lo − P) for dx = −1 (folded region)
- h6 ≈ gate for the −1 mid region (BX + BY ≥ 9)

**Hidden layer 2 (8 AND-gates, each with threshold 6·(sum − 2.5)).** Exactly one gate fires in a given state. Each gate encodes one (direction, region, move-right or move-left) case. Units 0–3 move right and 4–7 are their left counterparts.

**Output.** Right logit = 8·(sum of the active right-gate values) + 24, and left logit is built the same way. No-op, up, down and fire stay at 0. When no gate fires (for example dx = 0 on the first step), both move logits are −8 and the agent does nothing.

**Known limitations.** Bricks are ignored, the ascending-ball case reuses the descending formula, and the one-step stall at walls is only handled roughly.

```edits
# ---- layer 1 ----
# h0 = tanh(2*(BX-BY-P+9)): ball cells (ch3) weight 2c-2r, paddle (row 9, ch0) weight -2c, bias 18
W1[3:600:6, 0] = [
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 -2, 0, 2, 4, 6, 8, 10, 12, 14, 16,
 -4, -2, 0, 2, 4, 6, 8, 10, 12, 14,
 -6, -4, -2, 0, 2, 4, 6, 8, 10, 12,
 -8, -6, -4, -2, 0, 2, 4, 6, 8, 10,
 -10, -8, -6, -4, -2, 0, 2, 4, 6, 8,
 -12, -10, -8, -6, -4, -2, 0, 2, 4, 6,
 -14, -12, -10, -8, -6, -4, -2, 0, 2, 4,
 -16, -14, -12, -10, -8, -6, -4, -2, 0, 2,
 -18, -16, -14, -12, -10, -8, -6, -4, -2, 0]
W1[540:600:6, 0] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]

# h1 = tanh(2*(BY-BX-P+10)): ball weight 2r-2c, paddle -2c, bias 20
W1[3:600:6, 1] = [
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 2, 0, -2, -4, -6, -8, -10, -12, -14, -16,
 4, 2, 0, -2, -4, -6, -8, -10, -12, -14,
 6, 4, 2, 0, -2, -4, -6, -8, -10, -12,
 8, 6, 4, 2, 0, -2, -4, -6, -8, -10,
 10, 8, 6, 4, 2, 0, -2, -4, -6, -8,
 12, 10, 8, 6, 4, 2, 0, -2, -4, -6,
 14, 12, 10, 8, 6, 4, 2, 0, -2, -4,
 16, 14, 12, 10, 8, 6, 4, 2, 0, -2,
 18, 16, 14, 12, 10, 8, 6, 4, 2, 0]
W1[540:600:6, 1] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]

# h2 = tanh(4*(BX-BY-0.5)): ball weight 4c-4r, bias -2
W1[3:600:6, 2] = [
 0, 4, 8, 12, 16, 20, 24, 28, 32, 36,
 -4, 0, 4, 8, 12, 16, 20, 24, 28, 32,
 -8, -4, 0, 4, 8, 12, 16, 20, 24, 28,
 -12, -8, -4, 0, 4, 8, 12, 16, 20, 24,
 -16, -12, -8, -4, 0, 4, 8, 12, 16, 20,
 -20, -16, -12, -8, -4, 0, 4, 8, 12, 16,
 -24, -20, -16, -12, -8, -4, 0, 4, 8, 12,
 -28, -24, -20, -16, -12, -8, -4, 0, 4, 8,
 -32, -28, -24, -20, -16, -12, -8, -4, 0, 4,
 -36, -32, -28, -24, -20, -16, -12, -8, -4, 0]

# h3 = tanh(2*(BX-TX)): ball weight 2c, trail (ch4) weight -2c, bias 0
W1[3:600:6, 3] = [
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
W1[4:600:6, 3] = [
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18]

# h4 = tanh(2*(BX+BY-P-9)): ball weight 2c+2r, paddle -2c, bias -18
W1[3:600:6, 4] = [
 0, 2, 4, 6, 8, 10, 12, 14, 16, 18,
 2, 4, 6, 8, 10, 12, 14, 16, 18, 20,
 4, 6, 8, 10, 12, 14, 16, 18, 20, 22,
 6, 8, 10, 12, 14, 16, 18, 20, 22, 24,
 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
 10, 12, 14, 16, 18, 20, 22, 24, 26, 28,
 12, 14, 16, 18, 20, 22, 24, 26, 28, 30,
 14, 16, 18, 20, 22, 24, 26, 28, 30, 32,
 16, 18, 20, 22, 24, 26, 28, 30, 32, 34,
 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
W1[540:600:6, 4] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]

# h5 = tanh(2*(8-BX-BY-P)): ball weight -2c-2r, paddle -2c, bias 16
W1[3:600:6, 5] = [
 0, -2, -4, -6, -8, -10, -12, -14, -16, -18,
 -2, -4, -6, -8, -10, -12, -14, -16, -18, -20,
 -4, -6, -8, -10, -12, -14, -16, -18, -20, -22,
 -6, -8, -10, -12, -14, -16, -18, -20, -22, -24,
 -8, -10, -12, -14, -16, -18, -20, -22, -24, -26,
 -10, -12, -14, -16, -18, -20, -22, -24, -26, -28,
 -12, -14, -16, -18, -20, -22, -24, -26, -28, -30,
 -14, -16, -18, -20, -22, -24, -26, -28, -30, -32,
 -16, -18, -20, -22, -24, -26, -28, -30, -32, -34,
 -18, -20, -22, -24, -26, -28, -30, -32, -34, -36]
W1[540:600:6, 5] = [0, -2, -4, -6, -8, -10, -12, -14, -16, -18]

# h6 = tanh(4*(BX+BY-8.5)): ball weight 4c+4r, bias -34
W1[3:600:6, 6] = [
 0, 4, 8, 12, 16, 20, 24, 28, 32, 36,
 4, 8, 12, 16, 20, 24, 28, 32, 36, 40,
 8, 12, 16, 20, 24, 28, 32, 36, 40, 44,
 12, 16, 20, 24, 28, 32, 36, 40, 44, 48,
 16, 20, 24, 28, 32, 36, 40, 44, 48, 52,
 20, 24, 28, 32, 36, 40, 44, 48, 52, 56,
 24, 28, 32, 36, 40, 44, 48, 52, 56, 60,
 28, 32, 36, 40, 44, 48, 52, 56, 60, 64,
 32, 36, 40, 44, 48, 52, 56, 60, 64, 68,
 36, 40, 44, 48, 52, 56, 60, 64, 68, 72]

b1[0:7] = [18, 20, -2, 0, -18, 16, -34]

# ---- layer 2: AND gates, threshold 6*(sum-2.5) ----
b2[0:8] = -15
# j=0 (dx+, mid, right): 6*(h3 - h2 + h0)
W2[0, 0] = 6
W2[2, 0] = -6
W2[3, 0] = 6
# j=1 (dx+, hi, right): 6*(h3 + h2 + h1)
W2[1, 1] = 6
W2[2, 1] = 6
W2[3, 1] = 6
# j=2 (dx+, mid, left): 6*(h3 - h2 - h0)
W2[0, 2] = -6
W2[2, 2] = -6
W2[3, 2] = 6
# j=3 (dx+, hi, left): 6*(h3 + h2 - h1)
W2[1, 3] = -6
W2[2, 3] = 6
W2[3, 3] = 6
# j=4 (dx-, mid, right): 6*(-h3 + h6 + h4)
W2[3, 4] = -6
W2[4, 4] = 6
W2[6, 4] = 6
# j=5 (dx-, lo, right): 6*(-h3 - h6 + h5)
W2[3, 5] = -6
W2[5, 5] = 6
W2[6, 5] = -6
# j=6 (dx-, mid, left): 6*(-h3 + h6 - h4)
W2[3, 6] = -6
W2[4, 6] = -6
W2[6, 6] = 6
# j=7 (dx-, lo, left): 6*(-h3 - h6 - h5)
W2[3, 7] = -6
W2[5, 7] = -6
W2[6, 7] = -6

# ---- output: right = 8*(sum of right gates) + 24, left = 8*(sum of left gates) + 24 ----
W3[0, 3] = 8
W3[1, 3] = 8
W3[4, 3] = 8
W3[5, 3] = 8
b3[3] = 24
W3[2, 1] = 8
W3[3, 1] = 8
W3[6, 1] = 8
W3[7, 1] = 8
b3[1] = 24
```