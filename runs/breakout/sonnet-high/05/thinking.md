I'm working out the input indexing for the network by hand: each position is (row×10+col)×6 plus the channel. The channels I need are paddle at 0, ball at 3 (the projectile), and trail at 4, and the mapping also names brick at channel 2 as the reward input.

I'm weighing a simple tracking strategy: move the paddle toward the ball's column, since the ball and paddle both move one cell per step and the paddle can keep up. I'm also checking how the catch condition works at the bottom row, where the paddle counts as a catch if it matches either the ball's previous or new x. Next I'm thinking about how to encode the ball and paddle columns in the network so a linear layer can produce their difference.

I'm setting the logits for the three actions: right gets 4 times the right unit, left gets 4 times the left unit, and noop stays at zero bias. At d=0 both units sit near -0.9, so the logits are about -3.6 each, which still gives noop roughly a 95% share.

I'm checking the output scaling for the network: with a second hidden layer that sharpens the sign, and a final weight of 6, the logits come out around ±5.7, which should make the right and left choices clearly dominant.

I'm going over the bounce rule: the paddle position doesn't change the angle, so catching the ball is all that matters, and tracking its x column should keep the paddle in place at the right moment.

I'm checking whether tracking the ball's column is enough, since the catch condition allows the paddle to be at either the old or new ball x. The paddle can keep pace with the ball horizontally, but if it falls behind, simple tracking won't close the gap, so predicting the landing point could help, though bounce math with the walls looks messy. I'll start from the ball at row 3 with the paddle at column 4 and see how much tolerance the catch rule gives me.

I'm checking how the ball's horizontal speed compares with the paddle's: both move one cell per step, so a paddle that starts level with the ball can stay level, and only a missed move lets the gap grow. If the ball drifts one column away while the paddle holds, the gap is one, and following it at the same speed keeps that gap steady.

I'm checking whether a lag of 2 can be recovered: if the ball moves away, the paddle can't catch up until a wall bounce. So I'm considering using the trail to get the ball's velocity and aiming at the predicted next x, bx plus the horizontal step, to remove that lag.

I'm testing whether a predicted target of bx plus the ball's velocity would close a lag of one, but the wall bounce makes that prediction clamp awkwardly at the edges, so I'm still working out the exact lead.

I'm checking the catch rule again: the paddle needs to end its move at either the ball's old x or its new x. Tracking the midpoint between those two, bx + vx/2, gives the paddle a margin on either side at the row-8 step. Sticky actions can repeat the previous move, so I'll keep that tolerance in mind.

I'm weighing whether a velocity estimate from the trail is worth the extra complexity, since a bounce off the paddle only flips the vertical direction and leaves the horizontal motion intact. The trail gives the previous cell, so the horizontal velocity can still be read from it, even right after a paddle hit.

I'm combining the ball's position, its previous position from the trail, and the paddle into one linear target: the ball's current column plus half its horizontal velocity, minus the paddle's column. Written out, that's 1.5 times the ball column, minus half the trail column, minus the paddle column, so each input gets a simple weight. I'm noting that at the start the trail matches the ball, so the velocity reads as zero.

I'm checking the acceptable offsets for the paddle given the ball's predicted midpoint, working through which values of e would let the paddle stay put without missing the catch.

I'm settling the dead zone for the paddle: no move while the target offset stays within half a cell, and a move toward the ball once it grows past about three-quarters of a cell, which still lands the paddle on a valid catch position. I'm checking whether that holds when the paddle starts far from the ball, since a fixed zone could leave it lagging.

I'm checking the sticky-action case: if a noop lands while the ball is moving, the lag grows to 2 and the paddle can't recover before the row-8 catch, since the leading target doesn't pull it back. So I'm looking at whether a different target fixes that.

I'm weighing a tighter dead zone, so the paddle moves whenever the target offset grows past a small threshold rather than waiting for a wide margin. The ideal paddle spot is centered on the ball's midpoint, with a window of about one cell on either side.

I'm checking the dead-zone threshold for the paddle: with the ball moving right, a steady offset of 0.5 means no move, but one sticky no-op pushes the offset to 1.5, and then the paddle can't catch up.

I'm checking whether a lead target can keep the paddle ahead of the ball: if the ball moves right and the paddle takes a no-op, the lag grows, so I'm working out how each action shifts the offset to see where a steady point holds.

I'm seeing that the paddle can't recover once it falls behind, because moving at the ball's speed keeps the gap fixed. A sticky no-op pushes the lead the wrong way, so the real danger is drift toward the paddle lagging, and I need the target to hold the paddle close to the ball's position.

I'm now settling on a rule where the paddle moves right when the offset is above about a quarter cell, and I'm testing whether a threshold like that keeps the paddle ahead of the ball instead of lagging behind it.

I'm checking whether a lower threshold changes the steady state: if the paddle only moves right when the offset is at least about a quarter cell, the ball settles at an offset of 0.5, which leaves room for one sticky no-op before the catch fails.

I'm trying to find a lead target that keeps the paddle ahead of the ball, so a sticky no-op doesn't leave it behind. I'm testing a dead zone centered on a point slightly behind the ball's predicted position, with the paddle moving right once the offset reaches about -0.5.

I'm now testing a lead target of bx plus vx, so the paddle sits one cell ahead of the ball, with a dead zone of zero and moves whenever the offset reaches one cell in either direction.

I'm checking whether a steady lead is even possible: with the ball moving at one cell per step, a no-op lets it close the gap, so the paddle can only hold its position relative to the ball. I'll accept that the paddle should stay level with the ball and rely on the sticky tolerance rather than chase a perfect lead.

I'm noting that sticky repeats only matter when the paddle is changing direction, since steady tracking keeps the same move each step. Paddle bounces flip only the vertical motion, and brick hits do the same, so the horizontal velocity I'm tracking only changes at the side walls.

Walls are the only thing that changes the horizontal direction, so I'm checking what happens at the edge: when the ball reflects at x=9, it stays in that column for one extra step before heading back, which means the trail reads zero velocity for that step.

I'm settling on the offset e = d + vx, so with the ball moving right at vx=1, a lag of one cell reads as e=1 and the paddle moves right to hold it there.

I'm checking where the paddle sits relative to the ball: if the ball is one cell ahead, the paddle needs to move right to catch it. A single missed step still leaves the paddle in a catchable spot, since it can recover on the following move. I'm now asking whether a steady state exists where the paddle holds that position.

I'm testing a version where the offset includes a 1.5 multiple of the ball's velocity, so the dead zone sits at half-integer values when the ball is moving. Under that rule a noop at e=0.5 is followed by a move at e=1.5, and I'm checking whether that keeps the paddle on a catchable spot.

I'm checking whether a threshold of 0.25 gives a steady lead: with the ball moving right, the paddle would hold one cell ahead, and one missed step still lets it catch the ball on the row-8 step.

I'm looking at a half-step version of the offset, with the paddle holding one cell ahead of the ball when the threshold is 0.25. On the ahead side, I'd rather stay put at e=-0.5 than jump, so I'm sketching a dead zone that spans roughly -0.75 to 0.25.

I'm working out the paddle's dead zone for the case where the ball is moving left: the offset has to be measured against where the ball will be, not where it is, and the thresholds that work for rightward motion don't carry over directly.

I'm checking the symmetry of the left-moving case: with the ball going left, the lag version holds the paddle one cell behind, and the margins for the two directions come out unequal. I want thresholds that treat both sides the same way.

I'm trying to settle the dead zone so the paddle only moves when the offset is clearly off: right when e is at least 0.25, left when it's at most -0.25, and a noop only when e is exactly zero. That would keep the steady state at half a cell ahead when the ball moves right, but with the left-moving case the margins still come out lopsided, so I'll need to check whether the two directions really match.

I'm checking whether leading the ball by 1.5 cells holds up near the walls: at x=8 moving right, the target is 9.5, so the paddle heads toward the edge, and once the ball stalls at x=9 the target drops back to 9.

I'm checking whether leading the ball by 1.5 cells is too aggressive right before a bounce: if the ball is at x=8 moving right toward row 8, the target lands at 9.5, so the paddle has to move right to stay in a catchable spot.

I'm checking the edge cases: when the ball stalls at x=9 after a wall bounce, the trail reads zero horizontal velocity, so the target settles at 9. The next step should still catch it, since the ball ends at (8,9) and the paddle at 9 covers that.

I'm weighing whether a lead of 1.5 cells is too aggressive, since pushing the paddle that far ahead might cause trouble in the middle of the board, for example when the ball is moving fast across the field.

I'm realizing the steady state I just assumed doesn't hold: with the paddle one cell ahead and moving right each step, its post-move position lands two cells past the ball's column, which misses the catch window. I need the paddle's post-move position to fall within the ball's current or next column, so I'm rechecking the lead values against that requirement.

I'm finding that a steady move to the right can't hold the paddle at the right spot: with the paddle one cell ahead and moving right each step, it lands two cells past the ball. So at e=0.5 I should stay put, since that already catches the ball, and at e=1.5 or 2.5 moving right still works. On the left side, e=-0.5 needs a move left rather than a hold.

I'm now checking the paddle's post-move position against the ball's possible landing columns, since a target one and a half cells ahead might still leave it just outside the catch window.

I'm settling on a target of g = bx + 0.5·vx − px, since that puts the post-move position in the catch window, and I'm checking whether a dead zone of |g| < 1 keeps the paddle from overshooting. Moving right when g ≥ 1 and left when g ≤ −1 should hold it in place.

I'm settling on a dead zone of ±0.75 around the target, so half-integer offsets of ±0.5 leave the paddle still while ±1.5 trigger a move, and integer offsets of ±1 still get corrected.

I'm checking the steady state for the right-moving case: with the paddle holding half a cell behind the ball, it keeps catching the ball as long as it moves right, but any single missed step leaves it one cell short of the catch window.

I'm checking the paddle's post-move position against the ball's landing columns, since a half-cell lead only catches the ball if the paddle keeps moving at the right moment. Moving right at that lead gives a clean catch on one miss, but a second miss pushes it out of the window, and on the other side a move right would overshoot, so I'd hold still there.

I'm finding that the dead-zone rule can't be symmetric in the offset alone, because the same offset needs a different action depending on whether the ball is moving left or right. I'm considering whether to split the decision into separate conditions on the paddle-to-ball distance and the ball's velocity, perhaps with two hidden units that each use a different lead.

I'm working out the paddle rule in terms of the offset d between ball and paddle, since the right action depends on the ball's horizontal velocity. For a rightward ball I'd move right when d is zero or more and hold when d is -1, and for a leftward ball the cutoffs shift the other way.

I'm checking the paddle rule in terms of the offset d between paddle and ball, since the same offset needs different actions depending on the ball's direction. For a rightward ball the paddle should move right at d of zero or more, and for a leftward ball the cutoffs shift the other way, so I'm working out how to express both cases in one formula.

I'm settling the rule in terms of d: for a rightward ball the paddle should move right once d is zero or more, which means g > 0.25. A leftward ball needs a larger cutoff, near g > 1. So the threshold shifts with the ball's velocity, and I'm looking for one expression that captures that shift.

I'm checking the thresholds on the combined offset e = d + vx: moving right when e is above 0.5 covers the right-moving, stationary, and left-moving cases, and the left side needs e at or below -1.

I'm settling on a single integer error term, e = 2·bx − tx − px, and checking it against the cases: right when e ≥ 1, left when e ≤ −1, and hold at 0. The steady-state check works out, with the paddle catching the ball after one miss but losing the window after a second.

I'm checking whether the trail position is still right when a brick is hit, since the move then goes straight across rather than diagonally.

I'm checking how the trail position works when the ball hits a brick, since the trail then sits at the previous column rather than moving diagonally. At the wall the ball's column stays the same for one step, so the trail reads as no horizontal motion before the direction flips. I'm now defining the input indices for the ball, trail, and paddle channels in the grid.

Now I'm writing the hidden-layer units for the paddle network, with a right-move unit and a left-move unit that each use the combined error term and a bias of -1.5.

Still writing the weight initialization for the paddle network...

Still writing the weights for the paddle network...

Still working out the weight layout for the left and right units across the columns.

Still writing the weight lines for the paddle network...

Still writing the weight lines for the paddle network...

Still working out the weights for the second and third layers...

Still working out the output biases for the policy head, setting the no-op logit to zero and deciding whether the other actions need negative biases to keep them quiet.

Still working out the output biases for the network, checking whether the noop logit stays dominant when neither move is needed.

Still working out the weights for the paddle network's hidden units...

Still working out the output weights, setting the second layer to a simple pass-through and leaving the bias terms at zero.

