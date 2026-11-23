I'm working out a hand-designed policy for Breakout, so I'll lean on the ball's position and its previous position to get its direction, and on the paddle's row to figure out where to move.

I'm going with a reactive rule: nudge the paddle toward the ball's column, since predicting the landing point with a single hidden layer is hard. I'm also checking how the ball reflects off the paddle, where the new direction depends on whether the ball hits the paddle head-on or from the side.

I'm settling on a reactive approach: move the paddle toward the ball's column, nudged by its horizontal direction. Predicting the exact landing point by hand is hard without running the environment, so I'll aim for a sensible rule that should score modestly, with stronger policies being the goal.

I'm working out the hidden units now: one unit should respond to whether the ball's column is left or right of the paddle, so I'm weighting the ball's column positively and the paddle's column negatively in the first layer.

Working out the hidden units for the paddle now: the ball's column and the paddle's column can be combined so one unit responds to their difference, with the ball's column weighted up and the paddle's column weighted down. Next I'm checking how the ball's trail gives its vertical and horizontal direction.

I'm defining the ball's horizontal and vertical direction as differences between its current and previous positions, so I can tell which way it's moving. I'm leaning toward a simple policy that steers the paddle toward the ball's column, especially when the ball is moving down.

I'm thinking about the paddle's position relative to the ball when the ball is moving up, since tracking its column should still roughly line up the next descent. I'll also try steering with the ball's direction, aiming a bit ahead of it, though exact aim by hand is hard, so I'll keep the adjustment small.

I'm checking the paddle bounce rules at the wall and the paddle edge, working through which new direction the ball takes when it meets the paddle from each side.

I'm working out how the paddle's bounce depends on the ball's column: if the ball lands on the paddle's column while moving down, it keeps its horizontal direction and goes back up, but if it arrives from one column over, the horizontal direction flips. So being one column to the side of the ball's path changes how it returns.

I'm checking how the paddle's position relative to the ball changes the bounce: if the ball is at the paddle's column, it reflects vertically and keeps its sideways direction, so tracking the ball's column keeps the paddle under it.

I'm now checking that the paddle catches the ball whether it sits on the ball's current column or the one it moves into next, so aiming at the ball's column plus its horizontal direction works.

I'm still checking whether tracking the ball's column keeps the paddle in position for the catch, since the ball moves one column per step just like the paddle can.

I'm checking whether the paddle can keep up with the ball's column as it moves sideways, since both move one column per step, so tracking should mostly work. The part I'm less sure of is what happens after the ball bounces off a wall, because the clamping there could make its horizontal motion stall for a step.

I'm figuring out the movement rule now: if the ball's column is left of the paddle, I move left, and if it's to the right, I move right. The rest of the note is about the ball's column and the paddle's current position, and it's time to settle how the paddle chooses when to fire.

I'm settling the paddle's network: a unit for the signed gap between the ball's column and the paddle's, squashed with tanh so it behaves like a sign, feeding the left and right logits in opposite directions.

I'm setting the noop bias to about 2.5, since with D=0 the no-op logit should win while D=±1 gives a strong push left or right with the tanh scaled up.

I'm working out the bias for the no-op action: with it set to about 1.5 and the output weights at 6, a paddle one column off gives a clear push toward the ball, while a perfectly aligned paddle still leans toward staying put.

I'm setting the no-op bias so the network still prefers staying put when the paddle is centered under the ball, and I'm weighing whether a centering unit is worth adding to sharpen that.

I'm weighing the noop bias against the output weights: with zero bias, D=0 leaves all six logits equal, so the paddle would wander left or right at random a third of the time, and making the output weights large only sharpens the choice when D is nonzero.

I'm trying a unit shaped around D minus a half, so that it fires for D of one or more and stays negative for zero, but the sign pattern at zero and at -1 needs checking before I trust it.

I'm trying to get the sign of the gap from two offset tanh units: one centered just below zero and one just above, so their average is zero at D=0 and roughly ±0.95 when the ball is one column off.

Now I'm weighing a pair of offset tanh units, one centered at D=0.5 and one at D=-0.5, so their combined output gives a sign-like signal and a separate difference can drive the no-op logit.

I'm checking the output weights for the left and right moves: with the tanh pair, a gap of one column gives a logit near 5.7, which makes the chosen move almost certain, and I'm now testing the case where the ball sits one column to the left of the paddle.

I'm checking the right-hand logit: with the two offset units summed, it comes out to about -5.7 at D=-1 and about 6 at D=2, so the sign works out in each case. At D=0 the centering term gives the no-op logit a value around 3.6, so the paddle stays put when it's aligned under the ball.

I'm checking how the second layer can carry the sign signal forward: the first-layer units already sit near ±0.9 to ±1, so passing them through a tanh with a weight of about 1 should keep most of that signal intact.

I'm simplifying the second layer: I'll use two first-layer units, A and B, and have the second layer pass their sum through with weight 2 so the sign signal gets amplified.

I'm now setting up the second layer as a sign detector: one unit squashes twice the sum of the two first-layer units, which saturates to a clean sign for the ball being a column away, and the other takes twice their difference, which is large only when the ball is centered under the paddle.

Now I'm setting the right logit to 6 for D=1, and checking that the right move wins with probability near 0.99 while the no-op logit sits around 0.57. Next is the D=0 case.

I'm setting the no-op weight to 5, so at D=0 the no-op logit dominates and the paddle stays put about 97% of the time. I'm also considering a slight negative bias on up, down, and fire, though that's a minor tweak.

Now I'm working out how the ball's column relates to the paddle's, so the paddle's position feeds into the decision for which way to move.

Now I'm mapping the weight indices for the ball's column into the first-layer weight matrix, so each column's ball weight lands on the right cells across all rows.

I'm filling in the first-layer weights for the paddle's channel: the cells on the bottom row get values of -3 times their column index, so the paddle's position pushes the gap in the right direction. Then I'm doing the same for the ball's channel, where each column's weight is 3 times its index and is repeated down all ten rows.

Checking the ball's contribution to the first-layer units: the ball's column weight is 3 times its index, and that's repeated down all ten rows, so the ball's position alone sets the unit's input. Ball and paddle are each always present once, so the pre-activation is just 3(bx − px) shifted by ±1.5.

I'm considering whether to add a term based on the ball's direction of travel, so the paddle aims ahead of the ball instead of just under it. The catch point at row 8 is what matters, and tracking the current column alone will lag behind a moving ball.

I'm checking the lag: the paddle only moves one step after the ball has already shifted to D=1, so it ends up trailing the ball by a column and stays at D=1 from then on.

I'm checking the lag more carefully: if the paddle trails the ball by one column while the ball moves right, the catch check at row 8 fails, since the ball lands one column past the paddle. Only a ball moving left would be caught from that offset, so the trailing gap matters for the catch.

I'm checking the case where the ball moves right and the paddle trails it on the left, since then the ball lands one column past the paddle at row 8 and the catch fails. The paddle has to sit at the ball's column or one to its right when the ball is heading right, so a left-side lag is the problem to fix.

I'm noticing the paddle has to land on the right side of the ball depending on its direction: when the ball moves right, the paddle should sit at the ball's column or one to its left, and when it moves left, at the ball's column or one to its right. So I'll shift the target by half a column in the direction of travel, so the paddle lines up with where the ball will be.

I'm now testing whether a shift of the ball's column by the direction of travel gives a target that the paddle can hit, so I'm checking which paddle positions still catch the ball when it moves right or left.

I'm weighing whether a half-column offset in the target would let the paddle catch the ball moving either way. Since the paddle has to sit at the ball's column or one step toward its direction of travel, the threshold would need to fall at half-integers, so I'm considering tanh-based thresholds at ±0.5 to handle that.

I'm working out the paddle's target when the ball moves diagonally. Shifting the offset by one column in the direction of travel gives a window of acceptable paddle positions, and that window is asymmetric, so a plain sign threshold at 0.5 won't capture both sides of it.

I'm settling on the target as the ball's next column, bx + dx, since that is a valid catch point at row 8 with no dead zone needed.

I'm settling on the paddle target as one column ahead of the ball in its direction of travel, which gives a stable lead with no dead zone. Since the ball moves at the same speed as the paddle, the lead holds once it's set, though sticky actions might introduce some noise.

I'm settling on the target as the ball's next column, bx + dx, and I'm checking the edge case where the ball bounces off the wall at x=9. There the target would be 10, which is off the board, but the paddle would just press against the wall and stay at 9, which is fine. I'm also noting that dx comes from the ball's previous position, so the target can be written as 2bx − tx.

Now the target is 2·bx − tx, which is the ball's next column, so the paddle has a linear expression to chase with no dead zone. Starting out, the trail equals the current position, so the target just reduces to the ball's column. I'm also checking how the trail cell lines up with the separate ball channel, since the two sit in different input channels.

I'm checking the brick-hit case, where the ball keeps its column change but stays on the same row, so the trail still gives a usable direction. Then I'm settling the paddle target as 2·bx − tx, the ball's next column, and building the two threshold units around D2 = 2bx − tx − px with their offsets at ±0.5.

I'm settling the weights: the ball's column gets 6c, the trail column gets -3c, and the paddle column gets -3p, so the pre-activation comes out to D2 with the ±1.5 offsets for the two threshold units.

Working through the two-layer wiring now: the second layer just sums and differences the two threshold units, so I'm checking how those combine at a sample distance.

Setting up the output layer now: I'm writing the weights that map the two second-layer units to the six action logits, starting with the noop column.

I'm setting the output weights now: the noop logit gets 5 from the second unit, left gets -6 and right gets 6, with zero bias and the rest at zero. Checking a sample distance, moving right gives right about 98% probability, and when the target is already matched, noop dominates.

Now I'm setting the first-layer weights for the two threshold units, which share the same weights and differ only in their bias.

Writing the weight assignments for the first layer now...

Writing out the first-layer weights for the ball channel, one strided assignment over all cells with the value scaled by column.

Still writing out the first-layer weights for each column...

Still working out how to write the weights for the first layer, one column at a time.

Still writing out the first-layer weights, one column at a time, with each column's ball-channel values as a scalar fill.

Still writing out the ball-channel weights, one column at a time.

Still writing out the paddle's first-layer weights, one row at a time.

Still writing out the paddle's first-layer weights, one row at a time.

Still writing out the bias and second-layer weights...

Writing the final layer's weights now, with the noop logit driven by the second hidden unit and left and right driven by the first.

Checking the start-of-policy sanity points now: the second-layer units beyond the first two stay at zero since tanh(0) gives nothing, and the ball's trail matches its current cell on the first step, so the paddle target is just the ball's column.

Setting up the weights for the Breakout policy now: the two first-layer units both read a single target-offset signal, and I'm filling in the ball and trail columns as strided blocks.

Still writing out the trail channel's weights, one column at a time.

Still writing out the paddle's first-layer weights, one column at a time.

Checking the remaining setup: the paddle weights are in place, the two threshold biases are at ±1.5, and the second-layer and output weights are set. Everything else stays zero.

