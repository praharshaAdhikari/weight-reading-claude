I'm designing a hand-written policy for Breakout MinAtar as a two-hidden-layer tanh network with hand-set weights. I've worked out the input layout: the paddle is in channel 0 on row 9, the bricks are in channel 2 on rows 1 to 3, the ball is in channel 3, and the trail is in channel 4, with each cell's index computed as (row*10+col)*6+ch. Now I'm turning to where the paddle should sit.

I'm working out the paddle's index formula and how the ball's position and direction can be read off the ball and trail channels. My plan is to move the paddle toward where the ball is heading in x, and I'm checking whether the ball would reach the paddle row at the paddle's current column.

I'm checking how the paddle's position relates to the ball's bounce direction. If the ball's current column matches the paddle, it bounces left, and I'm working through the direction mappings for the case where it lands on the paddle diagonally from a neighboring column.

I'm settling on tracking the ball's x-position with the paddle, since the paddle only needs to sit under the ball when it reaches row 8 to bounce it back up. Whether that works depends on the paddle moving at most one cell per step to keep up with the ball's column.

I'm weighing whether a paddle that simply follows the ball's current column is enough, since the ball moves one cell in x per step and the paddle can match that pace. The alternative is predicting where the ball will land, including wall bounces, which is more involved and harder to encode with hand-set tanh weights.

I'm checking that the paddle has to be at the ball's column at the moment it reaches row 8, since the paddle moves before the ball within each step. So the paddle needs to keep pace with the ball's x-position from one step to the next.

I'm checking that the paddle has to land on the ball's column at row 8, or on the column the ball moves into, so it can bounce the ball back up.

I'm settling on a simple rule: the paddle moves toward the ball's x-position plus its horizontal direction, so it's slightly ahead of the ball when the ball is falling. Since both the paddle and the ball move one cell per step, the paddle should be able to keep up. Bricks still matter, because the ball has to travel upward to hit them.

I'm now thinking about whether the rewards grow over time, so a perfect tracker should score well, and I'm planning to move the paddle toward the ball's x-position. Next I'm working out how to encode the ball's x, the paddle's x, and the ball's direction as hidden-layer detectors.

I'm now defining per-column detectors for the ball and the paddle, so I can compare their columns with a signed difference rather than just checking whether they match.

I'm sketching a linear score for the ball's column minus the paddle's column, using one-hot weights so the difference comes out exactly. The idea is to feed that difference through a scaled tanh, with one side driving "left" and the other driving "right."

I'm settling on a difference-based unit: a tanh of the ball's column minus the paddle's column, scaled so that any nonzero gap saturates to a clear sign. From there, the right-move logit gets that signal and the left-move logit gets its negative, and I still need a way to make the no-op win when the gap is zero.

I'm checking the two tanh units that split the column difference: one is near +1 when the gap is zero or positive, and the other flips over once the gap reaches one. Their difference should light up only when the ball and paddle share a column, and their sum should carry the sign of the gap, with zero at the center.

I'm setting up the ball-minus-paddle column difference as a signed input, so I can pass it through tanh units that fire on the sign and on exact alignment.

I'm weighing whether the paddle should track the ball's current column or aim for a predicted landing spot. Tracking the current x is easy to encode and mostly works, since the ball's column shifts by one each step and the paddle can keep pace, but chasing a landing point would need reflections that are heavy to hand-build.

I'm working out how the paddle should lead the ball: since the ball shifts by its horizontal step on the way down, the paddle needs to be at the column the ball will occupy at row 8, not where it is now. I'm checking whether the trail channel is enough to read that step's sign.

I'm settling the paddle's target as the ball's column plus its horizontal step, which I can read from the difference between the ball and trail cells. That keeps the paddle one step ahead of the ball, so it can catch it at row 8. I'm also noting that the rule still holds after a wall bounce, since the trail gives the direction of the most recent move.

I'm settling on the paddle's target as the ball's column plus its horizontal step, since that step is already readable as the ball's current direction. I'm noting that the vertical direction doesn't change this rule, so the paddle leads the ball whether it's going up or down.

I'm wondering whether the paddle could end up in the wrong spot when the ball bounces back off row 8, but when the ball is moving up there's no paddle interaction, so that's fine. Since the ball moves diagonally, its horizontal step should be ±1 except right at the start, which means I could fold the trail-derived direction into the target as ball_x + dx - pos.

I'm checking how the ball's horizontal step gets read when it bounces off the walls or bricks: at a wall the direction flips but the trail still shows the actual move, so dx stays a true ±1 each step. A brick hit keeps the ball in the same row while its column changes, so I'll need to handle that case separately.

Working through the paddle-bounce case: after the paddle hits the ball, the ball's row stays at 8 and it shifts sideways to the next column, so its horizontal step is still ±1 but its vertical step is zero. That's an awkward state, so I need to check how the trail reads it.

I'm checking the wall-bounce case: if the ball was already at x=0 and is moving left, the reflection keeps it at the edge, so the trail and the ball could end up in the same column.

I'm checking the wall-bounce case again: a ball at x=0 should always be moving right by the time it gets there, since the bounce flips its direction on arrival. So the trail-derived step stays a true ±1 through wall hits, and the remaining question is the paddle-bounce case.

I'm working out a linear encoding for the paddle's target offset, e = ball_x + dx - pos, since dx comes from the trail and I need it as a weighted sum. The trick is that bx + dx equals 2·bx − tx, so the ball's channel should carry weight 2c, the trail's channel weight −c, and the row-9 paddle channel weight −c.

Now I'm checking the target offset as a weighted sum: the ball's column is counted twice, the trail's column is subtracted, and the paddle's column is subtracted, which gives e = 2·bx − tx − pos. The trail and ball channels each contain a single cell, so their weighted sums recover those columns exactly.

I'm checking whether leading the paddle by dx actually helps, since the target then sits one column ahead of the ball, which should matter when the ball is approaching row 8.

I'm working out where the paddle should sit one step ahead of the ball: if the ball is on row 7 moving down, the paddle needs to be at the column the ball reaches on row 8, or the column after that, so the bounce still happens. I'm weighing which of those two columns the target should aim for.

I'm working out that the paddle has to be at x8 or x8+dx when the ball reaches row 9, so the target T = x8+dx = bx+dx is the one to aim for.

I'm checking that the paddle only has to land on T within one step, and that tracking T is enough since it moves one cell per step. The policy will be to move right if the paddle is left of T, left if it's right of T, and hold otherwise, which means I need the paddle close to T when the ball reaches row 8.

I'm checking that the paddle's error, the gap between its position and the target, shrinks each step it moves toward the target. Since both the ball and the paddle move one cell per step, the paddle can keep up once it's close, as long as it keeps moving toward the target.

I'm settling the input layout: the ball's weight in channel 3 is 2c, the trail's in channel 4 is -c, and the paddle's on row 9 is -c, so the first layer can compute the offset between the target and the paddle directly. Now I'm working out the first-layer weights for each cell's index.

I'm still weighing whether to condition the policy on the ball's row, but tracking the target every step looks like enough. I'm also settling the action set to noop, left, and right, so the logits for the unused actions should stay low.

I'm setting the logits for actions 2, 4, and 5 very low, since they're equivalent to noop and should never be sampled. That leaves the policy as a choice between noop, left, and right. Now I'm starting to lay out the first-layer units, beginning with one that tracks whether the offset e is non-negative.

Now I'm defining the first-layer units as tanh functions of the offset e, with one unit shifted up by half a step and the other shifted down, so their combined sign pattern tells me whether e is positive, zero, or negative. Since e has to come from the inputs, I'll build it as a weighted sum: the ball's column gets weight 2c, while the trail and paddle columns each get -c.

I'm comparing two steepness settings for the tanh units: at k=2 the e=0 case only reaches about 0.76 and the sign separation is weak, so I'm trying k=4 instead, where the e=0 unit gives about 0.96.

I'm settling on a steeper tanh slope of k=4, since the sign units separate cleanly at that setting. The ball's weight becomes 8c, and the trail and paddle each get -4c, so the pre-activations grow large at the edges, but the units still saturate to the signs I need.

I'm writing the first-layer pre-activations so each unit is a linear function of the offset: the ball's column gets weight 8c, the trail and paddle columns get -4c, and the two sign units have biases of +2 and -2.

I'm checking how the trail-derived target handles the start of the episode, where the trail and ball sit in the same column, so the offset is slightly off for a few steps until the ball moves away. Next I'm setting up the two first-layer units, one for each side of the sign boundary.

I'm setting up the second layer so the output logits read the sign pattern of the two first-layer units. Right should fire when the offset is positive, since then a and b are both 1, and left should fire when it's negative. Noop needs to win at zero, which will take a separate constant term.

Now I'm checking the sign logic at each case: when the offset is positive, right should win; at zero, noop should win; when it's negative, left should win.

I'm settling on how the second layer should combine the two sign units, using tanh of a and b so the output logits can separate right, left, and noop.

I'm setting up the second layer with a unit that sums the two sign signals, tanh(3·(a+b)), which saturates to 1 when the offset is at least one step to the right and sits at 0 when the offset is exactly zero.

I'm checking how the sign units combine in the second layer, and noticing that a bit of leakage at e=1 means the simple tanh(3·(a−b)) isn't perfectly sharp, so I'll consider a steeper scale or accept the small error and build the logits from the second layer's outputs.

Now I'm tuning the second-layer weights so the noop logit stays below right at e=1, where the leakage from the sign units is still about 0.1.

Now I'm settling on the second-layer scale and checking the logits at each offset: with right at 6, noop at about 2.1 and left at -6 for e=1, right still wins, and noop takes e=0 cleanly.

Now I'm checking whether layer 2 even needs to exist, since the right logit could read the sum a+b straight from layer 1. I'll keep layer 2 as a tanh pass-through of that sum for now, and the output weights can still pick up the sign pattern from it.

Now I'm setting up the third layer, starting with the noop logit, which should read the difference between the two layer-2 units.

Now I'm assigning the output weights: the noop unit gets 20 from the sign-difference unit, left gets -6 and right gets 6 from the sum unit, and the biases for the unused actions are pushed down to -10.

Now I'm setting the remaining output biases to -10 for actions 2, 4 and 5, and checking the noop case at e=0: noop comes out to 20 there, while left and right both sit at zero.

I'm checking the sign at e=-1 next, where a should come out near -1 and b near -1 as well, so left should win there.

Checking the e=-1 case, the first unit comes out near -0.96 and the second near -1, so left should win there. Now I'm running the same check at e=0, where the sum sits near zero and the difference near 1.93, so noop should take over. Next I'm looking at e=2.

Now I'm writing out the weight entries for the first-layer units: the ball's channel gets 8c per column, and the trail channel gets -4c.

I'm now writing out the first-layer weights in bulk, using strided slices: for each column c and channel ch, the ten cells in that column are picked out with a start index of c*6+ch and a stride of 60.

Writing the first-layer weights in bulk now, since setting each column's cells one at a time is tedious.

Now I'm working out the strided index list for the channel-3 ball weights, since each column's value depends on c and the cell order has to match.

Still writing the first-layer weights column by column, using strided slices so each channel's cells line up with their column index.

Still writing the first-layer weights column by column, one statement per column for the ball and trail channels across both units.

Still writing the first-layer ball and trail weights, now deciding whether a two-column slice with a scalar fill will work or if I should split it into separate unit statements.

Still filling in the paddle's first-layer weights, now setting the row 9 channel 0 entries with a strided slice, one value per column.

Still writing the first-layer trail weights, deciding whether to split them by column or fill the whole channel in one go.

Still writing the first-layer weights, now weighing whether the paddle's row-9 entries can go in as two strided slices instead of ten separate statements.

Still writing the first-layer weights, now filling the paddle's row-9 channel-0 entries as strided lists for both units.

Still writing the first-layer weights, now checking that the zero-weighted units stay out of the way.

Checking the layer-3 weights now: the noop logit gets its own sign-difference input, and I'm confirming that left and right stay well below and above it respectively near the edges.

Checking the noop-versus-left margin at e=±1 now: the noop logit sits near 2.1 against left at 6, so left still wins but only by a modest margin. I'm considering raising the layer-2 scale so the sign units saturate harder and that gap widens.

Now I'm checking whether a steeper first-layer scale, with the offset moved, would sharpen the sign units so the leakage at e=1 drops.

I'm checking the sharper version of the first layer, with a steeper scale of 8 and biases of +4 and -4, so the sign units saturate much harder at e=1. At e=-1, the first unit comes out near -0.9993 and the second near -1, which still puts left on top.

Still tuning the first-layer weights, now with a sharper scale of 8 and offsets of +4 and -4 so the sign units saturate harder.

Now I'm checking the margins at e=±1 and e=2 with the sharper scale, and confirming the brick channel stays out of the calculation.

I'm checking the paddle's target as the ball's column plus its horizontal direction, ignoring vertical position. At the walls the target stays within the board, since a ball at the right edge can only be moving left.

Checking the wall case: a ball at x=9 still moving right gives a target of 10, but the paddle can't go past 9, so it just stays pinned at the edge until the ball reflects.

Now I'm weighing whether tracking the target T = x8 + dx is enough, given that the ball near the walls can get clamped and throw off the new_x == pos check.

I'm checking whether tracking the target holds up over a longer run, since the paddle may lag behind a fast-moving ball. Each step the target shifts by the ball's horizontal direction while the paddle closes by one cell, so the tracking error either stays roughly constant or shrinks.

I'm checking the paddle's tracking over time: when the ball reflects off a brick its horizontal direction flips and the target jumps, but the paddle still closes the gap. I expect a reasonable score, maybe 10 to 30, since the ball mostly bounces back down toward the paddle.

I'm checking how the paddle keeps up after the ball bounces off bricks. Since the ball stays in the top rows for several steps, the paddle has time to close the gap, though it may end up a few cells off by the time the ball drops back down toward row 8.

I'm checking the brick bounce: the ball only flips its vertical direction there and keeps its horizontal one, so after a hit it heads back down along the same diagonal it came up on. That means the paddle's current tracking should still line up when the ball returns.

I'm checking how the paddle keeps pace once the ball descends after a brick bounce. Since the vertical flip leaves the horizontal direction alone, the ball keeps drifting the same way on its way back down, so the paddle has to keep moving in that direction to be under it at the bottom.

I'm checking the paddle-bounce case now: when the ball reaches row 8 on the paddle, its vertical direction flips upward while the horizontal direction stays the same.

Checking the paddle-bounce mapping next: when the ball's x matches the paddle, it keeps its horizontal direction and only flips vertically, but when it reaches the paddle's column from the side, the horizontal direction flips too. So whether the tracker holds depends on which of those two cases occurs.

I'm checking whether the paddle can keep up after the ball bounces off the bricks and comes back down with a different horizontal direction. The paddle closes one cell per step, so it should have about eight steps to correct before the ball reaches row 8. I expect a reasonable score, around 20 or more, which is good enough for a hand-designed policy.

I'm checking how the paddle's tracking would work if the ball goes up, bounces off the bricks, and comes back down: the tracker should still be able to keep up with the descent. I'm also noting that the paddle has to start from its current position and move toward the ball's starting column.

I'm working through the first few steps of the rollout: the ball starts at (0,3) with no horizontal motion, so the target is column 0 and the paddle at column 4 has to move left. Once the ball moves to (1,4) heading down-right, the target shifts to column 2, and the paddle should keep closing that gap as it moves.

I'm checking the paddle's tracking over the first few steps: the paddle moves left from 4 toward the target, and by the time the ball is at row 3+k its column should be close to k+1, so the paddle lags by about one cell and then closes the gap.

Checking the paddle's tracking to the end: with lag 1 behind the target, it should reach the bounce at row 8 in position to hit, around 5 or 6. The design seems to hold, so I'm moving on to double-check the tanh saturation on the layer-1 values for large inputs.

I'm checking the layer-2 weights next, confirming that the a and b units feed the two hidden units with the signs I intended. Then I'm verifying the layer-3 weights, where the noop logit of 20 should beat left and right at zero error.

Now I'm laying out the first-layer weights for the ball channel, one column at a time, and I'm weighing whether a single 2D slice fill would be cleaner or whether separate column assignments are safer.

Still writing out the first-layer weights for the ball channel, one column at a time...

Still writing out the ball channel's first-layer weights, one column at a time...

Still writing out the ball channel's first-layer weights, one column at a time...

Still writing out the trail channel's first-layer weights, one column at a time...

Still writing out the paddle's first-layer weights...

Still writing out the paddle's bias and weight checks for the first layer...

Still writing out the output-layer weights and the biases that keep the non-noop actions suppressed...

I'm double-checking the action mapping: left is action 1 and right is action 3. The left logit is -6 times H2_0, which is -1 when the target is left of the paddle, and the right logit is +6 when it's to the right, so the signs line up with the intended moves.

Still writing out the paddle's and trail's first-layer weights, one cell column at a time...

Still writing out the trail channel's first-layer weights, one column at a time...

Still writing out the trail channel's first-layer weights, one column at a time...

Still writing out the paddle and trail weight assignments for the second hidden unit...

Still writing out the paddle and trail weights for the second hidden unit...

