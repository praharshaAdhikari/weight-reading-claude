I'm designing a hand-crafted policy and sorting out the input channels: paddle on channel 0, bricks on 2, ball on 3, and trail on 4. The ball's direction comes from subtracting its previous cell, the trail, from its current position. My plan is to track the ball's column relative to the paddle and steer the paddle toward it, so I need the ball's column, the paddle's column, and the ball's horizontal direction as features.

I'm working out a simple policy that steers the paddle toward the ball's column. The ball's x position can be read from channel 3 and the paddle's from row 9 of channel 0, using column-valued weights so the difference between them drives the decision.

Next I'm setting the hidden units to act like sign detectors on the ball-minus-paddle difference, with a 0.5 scale on the column values. I'll use two units, one for ball-left-of-paddle and one for ball-right-of-paddle, each with a steep tanh so they saturate near -1 or 1 and only sit near zero when the two columns match.

I'm working out how to get the ball's horizontal direction from the trail, since the difference between the ball's cell and its previous cell gives the movement. The next step is to compute the ball's column and row from the weighted sums over its active cells.

I'm considering how to turn the ball's horizontal direction into a usable signal, since a product of ball and trail columns isn't linear and the hidden units can't form it directly. I'm weighing whether a sign term, the ball's column minus the trail's, can stand in for the landing estimate.

I'm settling on a sign feature for the ball's horizontal direction, S = tanh(3*(bx - tx)), so the paddle can lead the ball by a fixed offset instead of tracking its raw position.

I'm checking whether the ball's horizontal direction can be folded into the paddle target with a linear unit, since a term like px minus bx minus a multiple of (bx minus tx) stays linear in the features.

I'm folding the lead into one linear error term, e = px - 3bx + 2tx, since the target sits at bx plus twice the sideways step. That keeps everything linear in the features. The catch is that the lead only makes sense while the ball is heading down; when it's rising, the paddle should mostly hold still.

I'm settling on a lead of two, since the simplest linear form folds it in as e = px - bx - 2(bx - tx). I'm accepting the crude fixed offset, knowing it may drift when the ball is rising, and I'll leave fire and no-op as equivalent, so the action is just 0.

I'm working out how to read the ball's column and row from channel 3, using weights that depend on the cell's coordinates, since with exactly one ball cell active the hidden unit's pre-activation is just the weight of that cell.

I'm noting that each hidden unit can take additive contributions from the ball, trail, and paddle positions, since only one ball cell is active at a time. The target error is px - 3bx + 2tx, which keeps the lead term linear, and I'll leave the brick channel out.

Now I'm checking how the paddle should sit relative to the ball in each direction, with the lead of two cells. Moving right, the paddle should end up two columns past the ball's column, and moving left, two columns before it.

I'm sketching the left-steering hidden unit so it switches on when the paddle is too far to the left of the target.

I'm weighing a unit that fires for "go right": its pre-activation is twice the negative of the error, minus 3, so it only turns on once the paddle is clearly left of the target.

Now I'm writing out the weights for the first hover-left unit, which should fire when the paddle sits too far right of the target. The ball's column gets weight 6c, the trail's gets -4c, the paddle's gets -2c, and the bias is -3.

I'm checking how large the pre-activation gets when the ball sits in the far column. It saturates tanh, so the extreme values are fine, but I need the values near zero to still line up with a one-cell error.

I'm checking that the pre-activation for the first unit comes out as odd integers, with -e = 2 giving 1, -e = 1 giving -1, and -e = 3 giving 3. I'm also making sure the per-cell weights add up correctly, since only one ball, one trail, and one paddle cell are active at a time.

I'm checking that the trail and ball can sit on the same cell at reset, where the lead term collapses to tracking the paddle against the ball's column. The ball is far away then, so this edge case is fine. Wall bounces also make the trail differ from the ball, and the brick channel stays out of the policy.

Now I'm setting up the second hidden unit to fire when the paddle needs to go left, with its pre-activation roughly the mirror of the first unit's. At zero error both units sit near -1, so the policy stays idle.

I'm settling the output layer now: the two steering units feed the logits directly, with the right-action logit driven by the "go right" unit and the left-action logit by the "go left" unit. I'm weighing whether an extra tanh layer adds anything, and it doesn't seem needed, since the units already saturate near plus or minus one.

I'm checking how the output logits should read the two hidden units, A and B, and whether a pass-through layer with plain weights keeps the right-versus-left split clean.

I'm setting the no-op logit to a constant bias of 1.5, since at zero error both steering units sit near -0.76 and the right and left logits cancel to zero.

I'm checking the output logit for the left action when the error is one cell off, using the two steering units' activations. The numbers so far suggest the left logit is still tied to the right one, so I'm working through how the difference between them comes out.

I'm testing whether the no-op bias should be zero, since at e=1 the paddle still needs to move left, and a bias of 1.5 lets the stay-still option win. I'm considering amplifying the steering signal with a second hidden layer so that any nonzero error clears the threshold.

I'm checking the pass-through scaling so the steering units saturate, and then I'm recomputing the left logit at an error of one cell, where the difference between the two hidden units comes out smaller than I'd like.

I'm checking whether the logit gap is strong enough at e=1, since the B unit's pre-activation there is only -1 and the scaled difference barely clears zero. The fix seems to be a larger scale on the steering signal so the move-left choice wins by a clear margin.

I'm switching the "need left" unit to a scale of 4 with an offset of -2, so that e=1 gives a clearly positive pre-activation and e=0 stays clearly negative.

Now I'm settling the output sign: the paddle-right unit takes the sign of the error, and the logits will be built from the saturated hidden values.

I'm working out the logit for the "no move" action: a constant bias of 0.5 should win when the error is zero, since both steering units then sit near -1 and the right and left logits cancel.

Now I'm settling on the weights for the first unit, using the ball, trail, and paddle positions to get the pre-activation right.

I'm working out the weights for the first hidden unit, giving the ball, trail, and paddle cells their per-column coefficients, and a bias of -2.

I'm checking the first unit's numbers: with ball column 5, paddle 5, and trail 4, the pre-activation comes out to 6, which saturates to about 1. That matches the error of -2, meaning the paddle needs to move right toward the target at column 7.

Still writing out the hidden-unit weights, now the second unit's, with the paddle, ball, and trail coefficients and a bias of -2.

Still writing out the output weights, filling in the logit columns for the left and right actions from the two steering units.

Now I'm working out the bias for the no-op and the other non-moving actions, so that staying still and only left or right can compete.

I'm pinning down the weights for the ball, paddle, and trail cells, with the ball's column carrying a 12x coefficient and the paddle and trail columns the other two. Then I'll write out the input index for each cell as (row×10 + column)×6.

Still writing the weights for the first hidden unit, now spreading the ball's column coefficient across its ten rows with a stride of 60 in the flattened input.

Still writing the first hidden unit's weights, now filling the ball channel for each column with a scalar value across its ten rows.

Still writing the paddle's weights, spreading the row-9 paddle cells across the ten columns with a weight that grows with each column.

Still writing the ball-channel weights, now laying them out column by column for both steering units.

Still writing the first hidden unit's weights, now deciding how to express the ball and trail coefficients column by column, with a scalar or list fill for each column's rows.

Still writing the weights, now the ball and trail columns for both steering units, and the paddle's row-9 values.

Still working out the weights for the first hidden unit, now the trail-channel coefficients column by column, and I'm checking that the ball and trail slices start at the right offsets so each column lines up with its own cells.

Still writing the first hidden unit's weights, now the ball and trail columns with their per-column coefficients and the paddle's row-9 values.

Still writing the output weights and biases for the policy network.

Checking the sign and magnitude at e=0 and e=2: both steering units sit near ±1 after the tanh chain, so the left and right logits cancel at zero error and the left logit reaches about 4 when the error is two cells.

Still writing the weight edits for the policy network, now the ball-channel and trail-channel slices column by column.

Still writing the weight edits, now the ball-channel slices for the individual columns.

Still writing the first hidden unit's weights, now the ball-channel columns with their coefficients spread down the rows.

Still writing the first hidden unit's weights, now filling the ball channel column by column across the ten rows.

Still writing the ball and trail weights for the first unit, column by column, and the paddle's row-9 values.

Still writing out the weights for the second hidden unit, with the ball column coefficients negated and the trail and paddle values flipped in sign.

