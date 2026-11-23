I'm designing a hand-crafted policy and want it simple but effective. The core idea is to track the ball's x position and the paddle's position, and steer the paddle toward where the ball will land.

I'm weighing a simple tracking policy: steer the paddle toward the ball's current x, since the ball moves one cell per step and the paddle can keep pace. The catch is whether tracking the current position is enough, or whether I need the ball's direction from the trail channel to predict where it will land.

I'm weighing whether the ball's direction is worth modeling. The simple version is to steer toward the current column, which works roughly because the paddle and ball both move one cell per step, but it can lag when the ball is angled. I'm considering a lead term based on the ball's motion, and I'm starting to sketch hidden-unit features that compare the ball's column against the paddle's.

I'm working out a pre-activation for a hidden unit that compares the ball's column against the paddle's, so the sign of the difference picks the direction. The one-hot presence of the ball and paddle makes the sum collapse to just ball_x minus pos. I'm now deciding how sharp to make it, since a scale of 0.5 saturates too little while 1.0 gives a usable gradient near zero.

Writing the two sign-flipped tanh units for the ball-minus-paddle difference, with the ball column weighted across all rows and the paddle column weighted on the bottom row.

I'm adding a unit that tracks the ball's horizontal direction by comparing its column with the trail's, giving a value of about ±0.96 for a one-column move. I'm also noting that on the first step there's no previous position, so the direction reads as zero, and I'm starting to think about the ball's vertical direction as well.

I'm now weighing a lead term that projects the ball's landing column from its direction and remaining rows. Making that multiplicative product work with tanh units is awkward, so I'm considering approximating it with the sign of the direction instead, though I'm short on time and may just track the ball's current column.

I'm weighing a lead term from the ball's direction, something like target = ball_x + 0.5*dx, but that isn't quite right. Making the landing estimate work would need a product of direction and remaining rows, which is awkward with tanh units. I'll settle for tracking the ball's current x, which is a common and reasonably strong heuristic here.

I'm checking whether the paddle can keep up with the ball's column as it drops, since both move one cell per step, so tracking its x just after it moves may leave the paddle a step behind.

I'm checking whether tracking the ball's current x actually works diagonally: the paddle moves first, then the ball, so if the paddle starts a step behind the ball's column, it can end up one cell short when the ball reaches the bottom row.

I'm checking the lag more carefully: the paddle trails the ball by one column, so when the ball lands on the bottom row it sits one cell past the paddle and the catch fails.

I'm checking the hit condition at the bottom row: the paddle counts as catching the ball if it sits on the ball's current column or on the column the ball moves into, so a one-cell lag might still be covered.

I'm settling on tracking the ball's current column rather than adding a lead term. The one-cell lag works out: when the ball reaches the bottom row, the paddle still counts as a hit if it sits on the ball's column or the one it moves into, so the chase holds up in either direction.

Writing the weight matrix for the first unit now, with the ball channel weighted by column so the tanh tracks ball_x minus the paddle's position.

Writing the weights for the second unit now, the negated copy of the ball-minus-paddle comparison.

Writing the weights for the trail-based direction unit next, scaling the ball and trail columns so their difference gives the horizontal motion.

Writing the second layer now, with a pass-through weight of 3 so the tanh output stays close to the ball-minus-paddle sign. Then I'm setting the output weights to 5 so the right and left logits separate clearly when the difference is ±1.

Now I'm settling the bias for the no-op action: with both hidden units at zero when the ball is directly over the paddle, the logits would be flat and the paddle would wander, so I'll give the no-op a bias of 3. That way the paddle holds still when aligned and only moves when the ball is one column off, where the right or left logit (about 5) overtakes it.

I'm setting the right-logit weight to 10 so that when the ball is one column off, the right action clearly wins over the no-op bias of 3. The remaining worry is that with the no-op at 3 and the other actions at 0, the paddle could still drift left or right about 15% of the time when the ball is aligned, so I'm checking whether the no-op bias needs to be higher.

Now I'm checking the bias on the no-op action: at d=0 the logits are flat, so the paddle would wander, and I'll set the no-op bias to 6 so it dominates. When the ball is one column off, the right logit near 10 still beats that bias, so the paddle moves.

I'm deciding whether to drop the direction unit entirely, since the lag analysis suggests plain ball-tracking is good enough, and I'm wondering if its contribution is worth the complexity.

Anticipating the ball one step ahead, aiming at ball_x + dx while it falls, could help, but tracking its current column already works for the chase. If the paddle trails by one and the ball moves toward it, the paddle reaches the ball's column in time for the hit check.

Now I'm setting the input weights for the ball and paddle channels, one column at a time, so the first hidden unit computes the ball-minus-paddle difference.

Still writing the weight indices for each column of the ball channel, one column at a time.

Still writing the per-column weights for the ball channel, with the scale rising from 0 to 10.5 across the columns.

Still writing the per-column weights for the ball channel, with the scale rising from 0 to 13.5 across the columns and the paddle entries mirroring it.

Still writing the paddle weights, with the ball-column scales running up to 13.5 and the matching negative values for the second unit.

Still writing the weight entries for the ball channel, mapping each grid column's index and scaling it so the first hidden unit tracks the ball-minus-paddle difference.

Still writing the weights for the second layer, with the right and left outputs keyed to the two hidden units.

Still working out the bias values, I'm settling on a no-op bias of 6 so the paddle holds still when the ball is directly above it, and I'm checking that the sign of each hidden unit carries through to the right and left logits.

Still writing the weight entries for the ball channel, one column at a time, with each column's scale stepping up by 1.5.

Still writing the per-column weights for the ball channel, with the paddle entries stepping down by 1.5 per column.

Still filling in the paddle weights, with the first unit's values stepping down toward -13.5 and the second unit's mirroring them.

