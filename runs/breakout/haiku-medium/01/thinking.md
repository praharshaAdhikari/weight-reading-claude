I'm planning a hand-crafted policy for Breakout MinAtar, a small two-layer tanh MLP that outputs logits for six actions, and I want it simple enough to write by hand. The idea is to track the ball's x position against the paddle, reading its location from the ball channel and its direction from the trail channel, then move the paddle toward where the ball will land along the bottom.

I'm weighing whether tracking the ball's current x would be enough, since the paddle can simply follow it. I'm also considering ways to encode the ball column with tanh units, though the direction from the trail channel complicates a purely linear scheme.

I'm working out a paddle-tracking rule for the ball's x position. A linear weighting on the ball and paddle columns gives a pre-activation proportional to the difference between them, so the sign alone decides whether to move right or left.

I'm settling on a unit that compares ball and paddle columns directly, using the difference b - p with weight 1 so the sign decides the direction. Then I'll sharpen it with a tanh of 4*(z - 0.5), which should saturate near ±1 on either side of the threshold, and set up a second unit for the opposite side.

I'm checking the cell indexing for the weights: each column's channel-3 and channel-0 entries sit at a fixed stride across the ten rows, so the weight for column c is set by stepping through those rows.

Writing the channel-3 weights as a repeated column pattern across all hundred ball cells...

Writing the channel-3 weights column by column, filling each column's ball entries with its index value across the ten rows...

I'm settling on a simple tracking rule that ignores bounce physics. The ball's column and the paddle's column are each read from fixed cell indices, so I'm working out the paddle-row offsets and the trail-based lead that I'll leave out for now.

I'm settling on tracking only the ball's column and ignoring the trail lookahead, with a dead zone around the paddle. The plan is to move left when the ball sits left of the paddle, right when it's to the right, and keep the no-op logit high when they line up, while leaving the other actions effectively unused.

I'm setting up the first hidden unit to detect when the ball is right of the paddle, using a weight of 4 times the column on the ball cells and negative 4 times the column on the paddle cells, with a bias of -2.

I'm now checking the sign on the second unit: with weights -4 on the ball column and +4 on the paddle column and a bias of -2, it should fire when the ball sits at least one column left of the paddle.

I'm checking the sign convention on the output side: the R unit fires for ball-right-of-paddle and the L unit for the opposite, so the second layer needs to route those two signals into the logits.

I'm setting the second hidden layer to pass each first-layer unit through a scaled tanh, so the ±0.96 saturation carries straight into the output routing.

I'm setting the output weights so the right-move logit gets +3 times the first routed unit and -3 times the second, which gives about +5.8 when the ball is to the right, about -5.8 when it's to the left, and zero when they line up.

I'm settling the no-op side now: the noop logit gets a bias of 1, so it wins at d=0 while the move logits sit at 0. Next I'm checking how the up, down and fire logits fare in that same zero-baseline region.

I'm settling the noop logit so it dominates when the ball is centered, which means a large bias on noop. The catch is that a large noop bias would also swamp the left and right moves when the ball is off the paddle, so I need to subtract its contribution in those cases with a negative weight routed from the tracking units.

I'm setting the noop logit as a function of the summed second-layer units, since that sum drops to about -1.92 only when the ball is centered on the paddle.

I'm settling the noop logit as a function of the summed second-layer units, using a negative weight so it jumps to about 4.8 when the ball is dead center and drops to zero otherwise, leaving the move logits to win when the ball is off the paddle.

I'm checking the noop weights on the summed second-layer units: at d=0 the sum is -1.92, so a weight of -2.5 on each gives a noop logit near 4.8, and off-center it falls to zero. The up, down and fire logits stay at zero, and the biases on the second layer aren't needed.

Next I'm weighing whether plain ball tracking will hold up, since the ball drops one column per step and the paddle can match that pace while it descends. I'm also noting that the first-layer and second-layer routing is set and the unused units stay at zero.

I'm checking how the ball's landing column depends on its horizontal speed as it falls. Tracking the current column only catches the ball when it moves straight down, so the paddle would also need to lead it by one column when the ball is moving diagonally. That lead would take extra weights, so I'm leaving it out for now.

I'm checking whether tracking the ball's current column is enough to catch it. If the paddle sits under the ball on the row above the paddle, the bounce check uses the old ball position, so it still returns the ball, and since the paddle and ball both move one column per step, staying under it should work.

I'm checking whether the paddle can keep pace with the ball's horizontal drift. If the ball moves away from the paddle at the same speed the paddle chases it, the gap never closes, so the simple tracking rule only works when the ball is heading toward the paddle.

I'm checking whether a simple tracking rule holds up, since the paddle has to chase the ball's column and a moving ball can pull away from it. I'm also setting aside a trail-based lookahead for now, because predicting the landing column would need a nonlinear term that a hand-written linear policy can't express.

Now I'm setting the first-layer weights for the right-move unit, scaling the ball column contributions by the column index and making the paddle column contributions negative.

Still setting the weights for the left-move unit, using a negative weight on the ball column and a positive one on the paddle column.

Working out the weights for the rightward-move unit, I'm settling on the ball-channel cells: each column gets a weight of 4 times its index, and the matching paddle cells on the bottom row get the negative of that.

Still filling in the ball-channel weights for the right-move unit, one column stride at a time.

Still filling in the unit-one weights on the ball channel, but I'm sorting out how to set both hidden units at once across the two columns without writing out every cell separately.

Still filling in the unit-one weights on the ball channel, one column stride at a time. The paddle cells on the bottom row get the matching positive values, starting from zero and stepping down by four.

Still filling in the unit-one weights, and now I'm setting the second layer so each of the two units passes its signal through with a weight of 2. I'm also setting the hidden biases to -2, which keeps the tanh outputs near the saturated ±0.96 range I want.

Writing the output-layer weights now: the noop logit gets -2.5 on both second-layer units, and the left and right logits get opposite-signed weights so they cancel when the ball is centered.

I'm checking the noop and left/right logits numerically now: at distance 1 or more, the right move comes out around 5.75 and the noop drops to zero, so the policy picks the correct direction.

Next I'm checking the output mapping: the right-move logit is 3 times the first second-layer unit minus 3 times the second, and I'm writing the edits block as the final section, with brief comments on the design.

