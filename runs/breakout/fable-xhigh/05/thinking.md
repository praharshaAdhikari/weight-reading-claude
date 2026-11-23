I'm working out how the Breakout dynamics translate into a hand-built policy, starting with the state: the ball's position and its direction, with the paddle fixed on the bottom row. Each step the player moves and then the ball moves, and I'm checking what happens when the ball reaches that bottom row, specifically whether the paddle is under it.

I'm checking the bounce rules at the bottom row: if the ball's old x matches the paddle, it reflects straight back, and if the new x matches, it reverses fully, otherwise it's terminal. So when the ball is on row 8 heading down, the paddle has to land on either its current x or the clamped new x, which is a two-cell target except at the walls, where it narrows to a single cell.

I'm weighing the simple tracking policy: move the paddle toward the ball's x-position, since both move one cell per step, so it stays aligned once close. I'm checking the start state too, where the ball at x=0 heading down-right should reach row 8 at x=5, and the paddle at 4 can reach the target in time.

I'm weighing whether simply following the ball's x-position is enough, since the ball and paddle both move one cell per step, so alignment can hold once it's established. The one exception is at the walls, where the ball stays in the same column for a step, and I'm checking that the paddle can still keep up.

I'm working through whether the paddle can stay aligned with the ball. Since I know the ball's direction from its trail, I can aim the paddle at the ball's next x, and if it keeps moving in that direction, the two stay matched, so a bounce at row 8 just reverses the direction. That's still fine for survival, but sticky actions, which repeat the last move 10% of the time, could knock the paddle out of sync by a step or more.

I'm checking what a wall bounce does to the paddle timing: once the ball hits x=9 and reverses, the paddle is still at 9, and if a sticky action keeps it pressing right, it might not move back left in time to match the ball's next column.

I'm checking whether a single sticky error can be recovered: if the paddle lags one cell behind the ball, it still reaches the ball's column at the bounce, so that's tolerable, but two cells behind isn't. The ball hitting the far wall should give the paddle room to catch up.

I'm checking the remaining bounce case: when the paddle is under the ball's old x, the ball reflects straight back up while its x moves on to the new column, and I still need to work out where the paddle should sit for that branch.

I'm weighing a different approach: instead of chasing the ball's x tightly, I could head for the landing spot early so that a sticky error has time to be corrected. Predicting that spot when the ball is heading down below the bricks is straightforward, since its column at row 8 depends only on its current x, row, and direction, with wall reflections applied.

I'm considering how the paddle's target could depend on the ball's direction, which I'd infer from the gap between the ball's current and previous x-positions. A simple linear combination of those positions might be enough to encode whether it's moving left or right. Wall bounces and paddle hits complicate that, since the ball can briefly keep the same x.

I'm noticing that at row 8 the trail can't tell me the direction reliably: if the ball and trail sit on the same row with one cell between them, the paddle bounce could have reversed the horizontal motion or kept it, so the observation alone is ambiguous.

I'm checking whether the trail can tell the horizontal direction at row 8: if the paddle was under the ball's old x the motion reverses, and if it was under the new x it continues, so the paddle's position at bounce time settles it. Top-wall and brick bounces keep the horizontal motion going, so the ball and its trail sit on the same row with no ambiguity there.

I'm now checking the brick-hit case, where a subtlety arises: if the previous step was already a strike, the ball passes into the brick cell without removing it or reversing direction.

I'm noting that a brick can be passed through on consecutive strikes without breaking, so the ball keeps going until it reaches open space, and that only matters for how the ball behaves near the bricks. I'm also thinking about the score: it's the count of bricks broken, and a policy that keeps catching the ball should rack up many more than typical RL baselines.

I'm thinking about whether a fixed tracking policy could get stuck in a loop that never breaks another brick, since a deterministic trajectory might repeat. Sticky actions add some randomness that could break such a cycle, but the main priority right now is just keeping the paddle alive.

I'm now turning to how a single linear expression could give the signed distance from the paddle to the target, since position, ball, and trail coordinates are all linear inputs.

I'm settling on the tanh trick for the tracking rule: two hidden units, one centered just above the midpoint and one just below, so the left and right logits switch on cleanly for D ≥ 1, D = 0, and D ≤ −1. That gives a linear policy that only needs two units in the first layer.

I'm now thinking about the ideal policy: predicting the landing spot early and moving there, then waiting with no-ops so sticky repeats don't throw the paddle off.

Now I'm looking at how the ball behaves once it's heading upward into the bricks. That's harder to predict, since the return path depends on which bricks are still standing, so I'm considering tracking its x for now. Going down below the bricks, the landing spot is fixed, so that part's simpler. Counting rows, the ball would be near row 4 and then move down a few rows before reaching the paddle.

I'm counting the steps left before the catch: four more rows down, then the catch step itself, so about five actions to position the paddle. The ball only drifts about four columns in that time, so the paddle has room to get ahead of it and wait there.

I'm working out the worst-case timing: after a paddle bounce at row 8, the ball goes up four rows, hits a row-3 brick, and comes back down, so the paddle gets about ten moves and has to cover up to nine or ten cells with wall reflections in play.

I'm checking where the ball lands relative to the paddle: it moves steadily across the grid except when it bounces off a wall. If it starts at x=5 heading right, it comes back down close to where it began, so the landing spot is usually near, though it can be up to 10 cells away. The open question is whether the paddle can cover a long horizontal gap in the roughly five moves available once the ball is heading down.

I'm sketching the hybrid: while the ball is still going up, the paddle should track its x, since starting to move only after the bounce would leave too little time to reach a far landing spot.

I'm now defining the landing position for when the ball is heading down: the steps to reach the paddle row are eight minus its current row, and its x at that row comes from reflecting its position with the wall bounces.

I'm working out the catch rule in terms of a reflected landing position: the ball reaches row 8 after 8 minus its current row steps, and its x there is found by folding its position across the walls. The paddle then has two valid cells for the catch, the ball's x at row 8 and the next x after that, which differ only in whether the horizontal direction flips.

I'm weighing a dead-zone rule: if the paddle already sits on either valid catch cell, it should do nothing. The risk is that a sticky repeat of an earlier move could push it into the other cell, so the stopping point needs some thought.

I'm settling on a dead-zone rule: the valid catch cells are the two around the reflected landing point, so the paddle only needs to land inside that pair. Its target is their midpoint, and it moves only when it is at least a full cell away, with the half-cell offsets handled so it doesn't oscillate.

I'm now working out how to compute the fold for the network: the center of the two valid catch cells is a continuous reflection of the unfolded landing point shifted by half a step, with the walls at -0.5 and 9.5.

I'm checking the wall-fold for the center point: when the ball lands at x=9 the fold gives 9.5, which looks like a mismatch with the true center of 9. That's fine, though, because the paddle can't be past 9, so the offset stays at least 0.5 and the no-op case still holds at the right edge.

I'm working out how to write the folding as a piecewise function. The landing values come in half-integer steps, so the reflection can be built from a sum of step-like activations instead of relu.

I'm now checking whether the ball's trail can tell me its horizontal direction, since the landing calculation needs that sign. The trail usually sits one step back along the diagonal, but it stops matching right after a side-wall bounce or a ceiling or brick bounce, so that needs handling. If the trail works, I could build the folded landing value from step-like units instead of relu.

I'm trying to express the landing computation as a linear combination of the ball's and trail's positions, so I'm testing whether a per-row weight on the ball's x plus a weight on the trail's x can produce x + d(8.5 − y) for both directions.

I'm writing the trail-weight term so that the ball's and trail's contributions combine into the folded landing value, with the trail's weight depending on its row.

I'm checking the special case where the ball has just bounced off a side wall. Its trail then sits in the same column, so the direction estimate from the trail breaks down, and I need to handle that case separately.

I'm checking the special case where the ball has just bounced off a side wall: its trail sits in the same column, so the linear trail estimate gives the wrong direction. The unfolded position, with x=10 and heading right, folds back to the same landing value, so I can fix this by treating the ball at x=9 as coming from an unfolded x of 10 and adjusting the trail weight to match.

I'm handling the trail-column ambiguity: a ball in column 9 moving down can't have come from the right, so its trail is either from the column to the left (normal bounce path) or directly above it (just bounced off the side wall), and I need the weights to account for both.

I'm working out how the trail weights behave for a ball in column 8 and column 9, since the two possible trail cells give different expected values. The difference between the column-9 and column-8 trail contributions has to come out to exactly one, and I'm checking whether the weights can be set to make that hold.

I'm testing whether a single linear weight on the trail can cover the ball-in-column-9 case, where the trail could sit either in column 8 or directly above. Fitting both the column-8 and column-9 trail cases at once gives a contradiction, so I'm looking at whether the periodic symmetry of the fold can absorb the difference.

I'm trying a different route for the side-wall case: split the left- and right-moving directions into separate units, or look up the landing column directly from the ball's diagonal. For a down-right ball the landing value is its diagonal offset plus 8.5, and for a down-left ball it is simply its x.

I'm considering whether the trail can settle the direction: for down-right motion the ball and its trail share the same x − y, and the side-wall bounces break that pattern, so I'm checking how those wall cases map onto the diagonals.

I'm checking whether the wall-bounce error matters: for a ball at column 9 with its trail in the same column, the formula gives a center of 9 where the true target is 9 minus the diagonal offset. I want to see how much that single-step mistake would cost before deciding whether the special case needs its own handling.

I'm checking how much a wrong move in the side-wall case would cost: when the ball is at the right wall near row 8, the formula's target is off, but the paddle can still catch it, and I'm weighing how many steps of margin a misstep would use up.

I'm weighing whether a paddle that is one step off the correct target would lose much margin, and I'm leaning toward fixing the wall-bounce case exactly rather than accepting a small error. The next step is a dedicated correction for a ball in column 9 whose trail sits in the same column in the row above.

I'm testing whether the trail weights can be set so the wall-bounce case comes out right, but the trail cell at column 9 gets used for two different ball positions with different targets. Writing out the constraints for those shared cells, I'm looking at whether any single set of weights satisfies all of them.

I'm writing out the constraints for the shared trail cells, checking which target values each ball-and-trail pair must produce after the fold, including the edge case near y = 0 where the boundary value needs care.

I'm checking the fold symmetry at the edge, where a ball at (8, 0) heading down-left lands with x9 = 0 and a center of −0.5. I'm working through the two trail constraints for the ball at column 8 and the weights A(x,y) = (9.5−y)x and B(tx) = −(8.5−y)tx that I'm testing against them.

I'm considering pairing the trail cells so the differences line up: setting the ball-at-9 case with trail-at-9 and trail-at-8 one unit apart, which would force a linear change in the left-moving weights. That would mean flipping the left-moving form to 19 minus the value, and I'm checking whether the chain of constraints still closes.

I'm checking whether a quadratic term like (x − tx)(x − 9.5) can be folded into the one-hot linear form A(x,y) + B(tx,y−1), since the direction-dependent target doesn't seem to fit that structure cleanly.

I'm trying to see whether the difference between the two trail cases can be absorbed by splitting the weights, since a single linear trail term seems to break down here. Writing the right-moving and left-moving targets out separately, I'm testing whether a term that depends on both the ball and trail columns can be represented without a product.

I'm solving for the coefficients of a quadratic B(t) so that its differences match the required linear change, and I get a coefficient of 9.5 on the linear term. From there I can write the left-moving weight A(x) as a quadratic in x, and I'm checking it against the left-moving target.

I'm checking whether a quadratic split works for both directions: with the trail term the same, the right-moving and left-moving cases each reduce to a single x-dependent piece, and the algebra closes, so the combined form holds for any position.

I'm checking whether the folded version still holds for the wall-bounce case with the trail in column 9, where the true landing is 9 + y − 8.5 and I need to see how it fits the two fold points.

I'm checking the wall-bounce case with the new weights: plugging in the values at column 9 gives 18.5 − y, which matches the reflected target. I think this works because, at that wall, the left-moving ball behaves like a right-moving one in a mirrored frame, so the trail term lines up with the bounce.

I'm checking whether the unfolded picture gives a consistent target: each physical column maps to an unfolded column, and after a bounce the ball sits at unfolded 10 while its trail is at 9, which still lands on physical column 9. I'm now working out which functions A and B have to cover both the unfolded and the physical cases.

I'm checking the left-wall case next: a ball at column 0 with its trail in the same column, moving right after the bounce. The formula gives 18.5 − y there, but the true landing should be 8.5 − y, so the error is a full 10 units and I need to see whether that changes anything.

I'm checking the left-wall case against the unfolded picture: a ball at physical column 0 moving right corresponds to position 20 in unfolded coordinates, and the trail lines up at 19. The combined formula gives 0.5 there instead of the 10.5 that the unfolded picture requires, so the two don't agree at that edge.

I'm checking the left-wall case for the cell at column 0: it has to work both when the ball is heading left toward that wall and when it has just bounced off it, so the same weight on column 0 is doing double duty. Working through the constraints, the left-moving case comes out right, and I'm now testing whether the post-bounce target can also hold with that shared weight.

Checking whether the remaining constraints on A and B can be satisfied alongside the shared-cell requirement at column 0, where A(0) + B(0) has to hold for both the left-moving and the post-bounce cases.

I'm noting that the unknowns outnumber the equations by one, so there's a free direction to exploit. Shifting A up by a constant and B down by the same constant leaves every sum unchanged, and I'm weighing that against the right-wall constraint to see what's actually pinned.

I'm seeing that the left wall breaks the pattern: the bounce value there comes out as 18.5 − y, but the unfolded picture wants a shift of ten. That means no single linear assignment can fix both walls, so I'll need to handle that edge separately, probably with a correction applied after the linear step.

I'm considering a different fix for the left-wall bounce: a separate correction step, since a single linear formula can't give the right value there for the same input as the normal case.

I'm looking at the layer-1 approach for the left-wall case, using a dedicated AND unit to detect the ball and trail both in column 0. The problem is that such a unit can only feed layer 2, not the fold units in layer 1, so I'm checking whether the final decision can still be linear in the layer-1 outputs, which would mean getting v'' through a unit that stays in its linear range.

I'm now checking the scaling for the tanh units: a small scale like 0.001 keeps them in their linear range for values up to about 30, and the error stays under a hundredth, so the later layer can amplify it back up.

I'm settling on a cleaner design: use a linear pass-through unit in layer 1, with tanh kept near zero so it stays in its linear range, and let layer 2 apply the sign thresholds on the difference between the folded value and the paddle position.

I'm now checking the left-bounce state, where the ball sits at column 0 and its trail at the cell just above it, and working out the correction that state needs. The computed value there is y + 0.5 while the true target is 8.5 − y, so the gap is 8 − 2y, which depends on y and so can't be fixed by one constant shift.

I'm now weighing a periodic version of the unfolding: if the target were taken modulo 20, the left-wall mismatch would be a multiple of 20, but I'm finding the gap there is 10 instead, so I'm checking the unfolded coordinate for the right-moving and left-moving cases to see where the extra 10 comes from.

I'm checking the periodic picture here: a right-moving ball at column 0 maps to position 20, and its trail after the left-wall bounce maps to 19, so both land on the same physical column. The target should then be 10.5 rather than what I got, which means the mismatch is 10 and not a multiple of the full period, and the constraints going around the cycle don't close up consistently.

Now I'm summing the alternating identity over all twenty positions, checking that the A and B terms cancel pairwise, which leaves only the linear and wrap-around constants to account for.

I'm seeing that the alternating sum over all twenty positions can't vanish, because the leftover constant is 10 plus a multiple of 20, so no assignment that respects the period-20 wrap can be fully consistent. I'm now considering whether letting the weights depend on the row as well as the column, so each cell has its own target, gets around that obstruction.

I'm testing whether the left-wall bounce can be fixed by giving it a different input value that G still decodes to 8.5 − y, since the usual v'' = X − y + 8.5 mapping leaves it off by 10.

I'm testing whether the left-wall mismatch can be absorbed by letting each row have its own weights, since the per-cell freedom might allow a consistent assignment. The catch is a parity condition: the alternating sum of the targets over all twenty states for a given row has to vanish, and I'm checking whether the desired representatives can be chosen to satisfy that.

I'm writing each candidate target as either the "plus" form or the "minus" form, shifted by a multiple of 20, and summing them with alternating signs. If every state uses the plus form, that alternating sum comes out to 10 plus a multiple of 20, so I'd need to flip one state's representative to change it.

I'm checking whether flipping a single state's representative can fix the parity sum, which works if I pick the state X0 so that the weighted term comes out to the needed −5 modulo 10, say X0 = y + 6 when that parity lines up.

I'm checking that the parity obstruction can be cleared by flipping the representative of one state per row, since that shifts the target by exactly 10 and the linear system becomes consistent. For the state X0 = y + 6, the two candidate values are 14.5 and 4.5, which differ by 10 and both decode to the same landing position.

I'm now seeing that the fix can be done row by row: for each row, I pick one state to carry a representative offset of 10, which breaks the parity obstruction. That turns the constraints for that row into a single cycle of twenty linked terms, each tying one column's value to a neighbouring column's.

I'm checking the consistency condition for each row pair, since the ball's row and the trail's row give an independent system of twenty unknowns. The catch is that the trail may sit in the same row when the ball has just bounced off a brick or the ceiling, so the horizontal direction carries over to the trail's cell instead.

I'm now checking the upward-moving case: the trail sits one row higher, so the linear formula pulls in a weight meant for a different situation, which means those states need their own gating to keep the policy from mixing up up-moving and down-moving balls.

I'm now defining the vertical direction as the sign of the difference between the ball's row and the trail's row, which gives up, down, or a zero case for bounces. A zero case means a brick or ceiling bounce sending the ball down, or a paddle bounce sending it up at row 8, and since bricks sit in rows 1 through 3, the bounce rows are fixed enough to check.

I'm now checking whether the ball's vertical direction can be told apart from the trail when it bounces off a brick or the ceiling. In those cases the trail sits in the same row, so the row alone doesn't reveal whether the ball is heading up or down, and the rows where this ambiguity shows up are the ones I need to pin down.

I'm now thinking about the up-moving case, where I could either follow the ball's current column or predict the landing spot by assuming it bounces off a brick at row 4 and comes back down.

I'm working through the up-moving case by estimating where the ball will land. If it bounces off a brick at row 4, the unfolded horizontal travel to the landing center comes to y + 1.5, and a bounce off a row-2 brick adds two more columns of travel. A ceiling bounce pushes the estimate out to y + 9.

Next I'm working out how far the ball travels horizontally before it comes back down, which depends on the row where it bounces. Bouncing lower on the board means less travel, so the estimate ranges from about y+1.5 at a row-4 bounce up to y+9.5 for a ceiling bounce. The exact bounce row depends on the brick map along the path, which is hard to predict, so I'm leaning toward following the ball's column while it rises and only switching to an exact prediction once it starts coming down.

I'm now checking how far the paddle has to travel after the ball bounces off a brick at height h and falls back down. The ball covers 8 − h rows before the catch, so the paddle needs about 8 − h moves, which leaves a margin of one step for a missed move.

I'm settling on a target for the up-moving ball: the predicted landing spot depends on which row it bounces at, which I can't know in advance. I'll lean on the lowest possible bounce, row 4, since that gives the soonest return and the most urgent case, and aim the paddle at the fold of the ball's position plus its unfolded travel in the direction it's moving.

I'm settling the up-moving target: for a ball above row 4 I'd take the bounce to be at row 4 and aim at its unfolded travel of y + 1.5, while for a ball at row 4 or higher I'd assume the bounce is imminent and use the shorter distance 9.5 − y. That gives a target of the ball's position plus the chosen travel in its direction of motion, folded back into the board.

I'm checking the up-moving target: the unfolded travel is y + 1.5 once the ball is at row 4 or higher, and 9.5 − y below that. If the ball climbs one more row without bouncing, the target moves by 2 units, yet the paddle only gains 1 per step, so I need to check whether the extra time covers that gap.

Tracking the ball is weighed against simply waiting: if I move the paddle ahead as the ball climbs, the sticky-action errors stay rare, and the down-prediction usually already has the paddle in place.

Now I'm setting up the linear form for the up-moving ball: its trail sits one row lower, and each row's constraints tie the ball's column to the trail's column. That couples the systems across rows, since the same variables show up for both up-moving and down-moving balls.

I'm writing out the linear equations that pair each ball position with its trail cell, one set for balls moving down, one for balls moving up, and one for same-row cases. Since the up-moving equations use the trail one row below and the down-moving ones use the row above, the same variables end up shared across rows, so the systems stay coupled.

I'm checking whether a single linear layer can handle both the up-moving and down-moving cases, since the equations overlap across rows and look overdetermined. A single functional won't cover it, so I'm considering separate first-layer functionals for downward and upward motion, gated by vertical direction, though that costs more units than I'd like.

I'm trying to get a gating trick into a single linear functional: add a large offset whenever the ball is moving the wrong way. The vertical difference between the ball and its trail, which is +1 for downward motion, −1 for upward, and 0 for the same row, is linear, so it could serve as that indicator.

I'm weighing whether to drop the linear pass-through and instead encode the decision entirely with step units, so that the gating offset doesn't leak into the comparison. The open question is how to express the sign of the difference between the target and the paddle position without an explicit intermediate value.

I'm now splitting the unfolded branches into paddle-relative comparisons, so each one checks v minus the paddle position directly, with the branch-1 case mirrored.

I'm settling the branch selectors now: the fold points sit at 9.5 and 19.5, so I'll put the thresholds at 10 rather than exactly on 9.5 to avoid a zero tanh input. Then the second layer can combine the branch outputs into the right-or-left decision.

I'm settling the gating: the vertical-direction check can go straight into the layer-2 AND, so each branch only needs its comparison and its branch selector to fire.

I'm gating each mode with a large offset that pushes its pre-activation out of range whenever the ball moves the wrong way, and I'm bounding the branch selectors on both sides so that nothing fires in that case. That keeps the design down to a handful of units, since a single upper-bound selector can stand in for the gate.

I'm now considering whether one shared linear functional could serve both the down and up modes, since the trail weights would have to match two different row offsets for each cell. Viewed as a graph, the down and up constraints link the same ball cells to trail cells in neighboring rows, which makes the system hard to satisfy with one set of weights.

I'm checking whether the parity of the cell coordinates could split the system into two independent pieces. A down-edge and a wall bounce flip parity differently, so it doesn't separate cleanly, and the system still looks overdetermined with roughly 200 unknowns against more than 320 equations. The saving grace is that the target values have some freedom in which representative I pick.

I'm considering a different setup: one functional per direction, built from the ball's position alone, gated by the trail's offset so that it only stays active when the ball is moving that way.

I'm now weighing a simpler structure: handle the down-moving case exactly, treat the up-moving case as a rough heuristic, and treat the same-row case separately. That keeps the unit count small while still covering the situations that matter most for play.

I'm weighing whether to simply hold the paddle still during the same-row states after a bounce. That would cost a step of margin on each bounce, but if the paddle was already positioned from the upward-motion prediction, it might be the right call. I still want to handle those states properly rather than rely on that.

I'm now setting up a separate functional for the same-row case, where the trail sits in the same row as the ball. For row 8, after a paddle bounce, the direction is unclear without paddle information, so I'd leave that state as a no-op. Even so, the ball then has plenty of steps to come back down.

I'm sizing up the same-row case after a paddle bounce: the ball ends at row 8 heading up, and I'm counting the steps it needs to come back down and whether the paddle has enough margin to reach the landing spot in time.

I'm now tracing the same-row case after the paddle bounce: the ball climbs from row 8 to row 4, bounces, and returns to the paddle row, so the count of actions from that state comes to ten. Moving right from the left side, the unfolded travel of nine cells wraps past the right wall, so I need to track the fold rather than assume a straight run.

I'm checking the worst case for the wrap-around: if the ball lands at the left edge moving right, the paddle has to cover nearly the full width, so I need to confirm the wall-bounce math still leaves enough actions.

I'm tracing the ball's path from the corner at (0, 8) heading up-right, and it reaches the right wall and comes back to the paddle. That takes 10 actions, and the paddle at 0 has to cover 9 cells, so there's still a margin of one step.

I'm checking whether sticky actions actually hurt here: if the paddle is already moving right, a repeated "right" is unaffected, so only the first step of the movement carries the 10% risk of being replaced by the previous action.

I'm checking whether the failure rate holds up over a full episode: at roughly 600 to 1,000 catches, I'd need each catch to fail less than 0.1% of the time to reach the step cap. That makes handling the worst-case geometry at S8 worth the effort.

I'm weighing what baseline scores to expect: good RL agents on MinAtar Breakout land around 20 to 60, and a strong hand-coded policy could plausibly reach hundreds. Next I'm working out the same-row case after a wall bounce, where the paddle position decides whether the ball is heading left or right.

I'm checking the direction of the ball in the same-row case after a paddle bounce, where it depends on the paddle's position relative to the trail and the ball. If the paddle sits on the trail, the ball keeps moving away from it; if the paddle sits on the ball, the ball heads back toward the trail. Both cases collapse into one formula, with a separate exception when the ball is against a wall.

Working it through with the ball's travel of about 9.5 cells, the landing center comes out near 9 − b, mirroring the ball's column whichever way it's moving. Both landing cells for either direction then include 9 − b, so that cell is the target.

I'm settling on a single rule for the same-row case after a paddle bounce: the target is the mirror of the ball's column, 9 − b, which lies inside the landing zone whichever way the ball is moving. So I'd move the paddle right when it's at least one cell short of that target and left when it's at least one past, with no need to know the direction. I'm also wondering whether the upward-row cases can be folded into the same kind of rule, where the travel distance alone sets the target.

I'm settling on a fixed target for the row-8 case: the mirror position 9 − b, which sits in the landing zone whichever way the ball is moving. That would let me set the upward functional's value at row 8 directly from the ball's column, with no paddle or direction lookup, though the same entries also feed the row-7 cycle, so I'd need to check that reuse doesn't break it.

I'm working out the constraints for the row-8 states: the upward functional has to give 9 − b for every valid ball and trail pair, and since the row-7 cycle already fixes the trail-side values, I only have freedom in the row-8 ball-side values.

I'm deriving the row-7 cycle solution to get the row-8 trail values, and I'm considering whether a separate small rule for the row-8 same-row case would be simpler, since the target comes out as a linear function of the ball's column and the paddle's position.

I'm sketching the budget for a separate functional for each case: downward travel, upward travel, low-row same-row, and the row-8 same-row case. For the downward case, I'm writing the unfolded coordinate as X + 8.5 − y, with y running from 1 to 8.

I'm now budgeting units for each functional: the downward and upward cases each need about ten units for their three branches, the low-row case another ten, and the row-8 case a couple more. That totals around thirty-two, which is tight, and the final layer of ANDs adds roughly twenty more, so I'll need to check that it still fits.

I'm looking at whether the branch count can be cut by letting each state pick its own representative value, as long as the overall consistency holds.

I'm checking whether the representative can simply be the true center for every state, which would remove the folding branches entirely. That hinges on whether the alternating sum over each row's cycle vanishes for a triangle-wave center, so I'm testing that consistency condition now.

I'm checking whether the alternating sum over one row's cycle vanishes when the target is the true center, since that would let every state use a single branch with no folding. I'm stepping through the 20 half-integer values of the triangle wave, pairing each with its mirror image to see if they cancel.

I'm checking the alternating sum over one row's cycle: the pairs mirror each other with matching signs, and the total works out to zero, so the direct solution should hold.

I'm checking whether the cycle system is actually solvable, since the alternating-sum condition only rules out one obstacle. With 20 equations and 20 unknowns forming a single cycle, I need to confirm the system has full rank and not just that the sum vanishes. If it does, the direct targets work and the layer-1 units collapse to two per mode.

I'm checking whether the cycle really is one 20-node loop, with a ball-column node and a trail-column node for each state, since that determines whether the alternating-sum condition is enough for the direct targets to be solvable.

I'm confirming the cycle structure: every node has degree two, so the 20 edges form a single loop through the ball-column and trail-column nodes. For each mode and ball row, that loop is what the solvability check has to cover.

I'm now splitting the functional into one per mode, since the weights for downward, upward and same-row cases conflict if they share a single sum. Each mode's functional will carry a gate term that switches it off outside its own case, with the vertical direction (down is +1, up is −1) deciding which gate is active.

I'm splitting each mode's comparison into two units, with a gate offset that pushes both outputs into the no-op pattern whenever that mode isn't the active one.

I'm looking at whether a separate gate can handle the S-mode case, since the other two modes can use simple linear gates based on the vertical direction, but the same-row case needs |δ|, which isn't linear.

I'm checking whether the downward and upward cycles can share weights with the same-row states, so the row-8 and ceiling bounces fall into the right mode's functional.

I'm counting the constraints again: the downward and upward cycles each tie a ball row to a trail row, and if the same-row states are also folded into the downward functional, the system has about 260 equations for 180 unknowns. That looks overdetermined, so I'm considering whether a gate offset can let the downward units absorb the same-row case.

I'm setting up the S-mode gate now: a separate pair of comparison units for the same-row case, with two extra step units checking whether the vertical offset is exactly zero, and then an AND in the next layer to combine them.

I'm now weighing a different gating for the same-row case: because the |δ| term isn't linear, I'd use a pair of extra step units to test whether the vertical offset is exactly zero and combine that with the S-mode comparisons in a second layer. I'm also considering whether the same-row states could instead be folded into the downward functional with a row-specific trail weight, but that would overdetermine the system, so it's ruled out.

I'm considering whether to skip the S-low states entirely: since the previous U-state already points the paddle at the same target, I could output no-op there and accept losing one step, or keep the U-mode prediction, which lands on the same spot.

I'm weighing whether the S-low states can get the same gated treatment as the other modes, since a no-op there would cost a step in the tightest worst case. I'm considering how much of the layer-1 budget that would use, and whether some spare capacity could go toward brick-aware prediction for the upward mode.

I'm weighing whether the paddle's targets should account for bricks, since a brick at row 3 would change the bounce row from the assumed 4. I'm also checking the worst case, where the ball climbs to the ceiling and back, because the target then shifts faster than the paddle can follow, though the cost of adjusting is only exposure to sticky failures.

I'm checking how far the paddle can get in the time left: from a bounce at row h there are 9 − h + 1 actions including the S-state, so at h=4 only six, and the paddle must sit within five cells of the zone when the ball arrives there. I'm now testing whether, on the upward pass, the paddle will have reached that zone by the time the ball hits row 4.

I'm checking whether the paddle can keep up if the ball skips row 4 and lands at row 3: from that point there are only seven actions, and the paddle may need to cover about seven cells, which looks like it could leave no margin.

I'm working out where the paddle has to sit relative to the ball's unfolded travel position at the moment of the bounce. Going from row 8 up to a bounce at row h and back down, the ball covers a fixed displacement, so the target offset depends on h and on whether the paddle starts behind or at the ball.

I'm checking the paddle's timing in terms of the unfolded travel distance: for a bounce at row h there are 18 − 2h actions in total, and the paddle's required move is 17 − 2h cells, plus one if it starts behind the ball. The physical grid is only ten cells wide, though, so the real distance is capped by the walls.

I'm checking the paddle's catch window against the folded targets: the h=4 zone at about 9.5 unfolded, then the h=3 zone at about 11.5 if the ball climbs one row higher. I'm starting from b = 0 with the ball moving right to see how far the paddle would have to travel.

I'm tracing the paddle's path for a ball that starts at column 0 and moves right, checking where it has to stand for each possible bounce row. For a bounce at row 4 the target is column 9, and for row 3 it's columns 7–8, with the targets shifting left as the bounce row gets higher. If the ball bounces at row 3, the paddle reaches column 7 in time; if it keeps climbing, the paddle steps back left to stay ahead of the next target.

I'm checking whether the slack holds through the switch: when the assumed bounce row drops by one, the remaining actions grow by two while the zone shifts by at most two, so the margin doesn't shrink.

I'm checking whether slack survives a reversal: if the paddle was moving left and the policy now needs it to go right, a sticky left move costs two units of slack, which could push the margin below zero. I'm thinking about when that reversal happens, such as when an assumption change moves the target past the paddle or right after a catch, and noting that the margin is usually larger than the worst case.

I'm now checking the worst-case slack at the first ceiling-reversal state: the paddle sits at b or b minus the up direction, and I'm measuring how far it is from the nearest cell of the h=4 zone against the ten actions available.

I'm checking the remaining cases where the paddle starts just behind the ball: with the zone at 9−b and 10−b, the gap is at most 8 cells, so there's still at least two units of slack. I'm now looking at the reversed case, where the paddle sits right at the ball's position and the zone is at 9−b and 10−b, starting with b=0 where the distance works out to 9 and the slack drops to 1.

I'm checking the edge cases where the slack falls to one, which happen only at the walls: the paddle at column 0 with the ball in the corner, since the zone there is nine cells away. Everywhere else the margin stays at least two. I'm leaving the corner situations alone for now and moving on to the upward-mode assumption.

I'm checking the ball's behavior in the upper rows, where it can bounce between the ceiling and the bricks, and the different movement assumptions that apply in each state. Where the ball is moving up just after a brick bounce, the downward assumption is wrong for a single step, which I'm treating as harmless. I'm also noting that a ball coming down from above the bricks can be deflected upward by a brick, so that assumption can be briefly off as well.

I'm now checking the edge cases around the starting state: a ball that bounces off a brick from below and then meets another brick directly above the first would be rare, and I'm treating its effect as harmless.

I'm checking the starting states now: a ball at column 0 moving down-right and one at column 9 moving down-left both read as wall-bounce cases, so the starting moves come out right. That means the bottom-row handling at rows 0 to 4 and row 8 can be combined into a single pair of functions.

I'm writing out the neural network weights for the paddle's state-dependent gating, using linear offsets and two units combined with AND in the next layer.

I'm working out the gating for the paddle's state, and I'm checking whether one unit can fire only when the offset is zero. It can't, so the band-pass needs two units. I'm weighing a three-input AND in the next layer against keeping separate comparison and gate units, and the count comes out the same either way.

I'm defining the two gate units g1 and g2 so that their sum is zero whenever δ isn't zero, and then combining them with the comparison unit in the next layer so that only the exact S-state gets a positive output.

I'm confirming that the ball and trail can share a cell at the start or in a corner, which is fine since they're read from separate input channels. So δ = 0 in those cases and the design holds. I'm also noting that the paddle and brick information each come from their own channels.

Now I'm defining the two gate-combined units for the right and left votes on the downward and upward cases, with the offsets shifted by the δ term so each fires only in its matching mode.

I'm checking how large the cycle-solution weights get, since the gating constant M has to be bigger than the leftover values from the other modes. The quadratic terms run from about −45 to 45, and I can shift a constant between the ball and trail functions, so I'm looking at whether that keeps the range small enough.

I'm settling on a large constant M around 1000 so the gating terms dominate any garbage values from the wrong modes, and K around 20 so the tanh units saturate cleanly at the ±0.75 thresholds. I'm also starting to question whether gating inside the layer-1 units is the right approach, and I'm about to check how reliably the vertical offset δ works as a linear function.

Now I'm weighing whether the gating constant and the cycle-solution weights will hold up, and I'm considering whether brick information could improve the upward-mode prediction. The main goals are survival, avoiding loops that never hit bricks, and breaking bricks quickly.

I'm considering whether loops could trap the ball forever, since a deterministic policy might cycle among cleared diagonals without ever reaching a brick. The sticky-action noise in the paddle position could break those cycles eventually, but slowly, so I'm thinking about adding some deliberate randomness inside the zone.

I'm thinking about whether the policy should be stochastic: softmax sampling could add randomness, and occasionally shifting the paddle to the other zone cell might break deterministic loops. The risk is that a wrong move could carry the paddle out of the zone, though the dead-zone would pull it back. Before settling that, I want to check whether loops are really a problem by looking at how the ball's x+y parity flips with each wall or brick bounce.

I'm estimating how many round trips the ball would need to clear the last bricks under a deterministic policy, and whether the sticky-action noise would be enough to break any cycles before the step limit runs out.

I'm now estimating how many points a trip is likely to yield, and I'm weighing whether to add some randomness so the policy doesn't settle into a loop, since each change in the paddle's action carries a 10% chance of being misapplied.

I'm checking how the sticky-action noise affects the paddle near the zone edges: if the paddle overshoots once, it stays inside the zone, but two overshoots in a row would take it out, and correcting back afterward is itself subject to the same 10% repeat.

I'm considering the corner case at ball position (0,8) heading up-right with the paddle at column 0, where the landing lands at column 9 after the bounce. The first move "right" might get replaced by the previous action with 10% chance, and if the paddle was already sitting still or moving left at the wall, that amounts to a no-op and the slack is tight.

I'm checking the stop-overshoot risk at the zone edge: if the paddle arrives early, the sticky repeat could carry it past the cell, but there's enough time to correct. The last-moment arrival is safe, since the catch happens on the step the paddle enters the zone.

I'm checking the overshoot risk once more: at the final catch step the paddle sits in the zone with the action set to no-op, but a sticky repeat could still push it. Inside the two-cell zone that just moves it to the other zone cell, which is safe, and at a wall the extra move does nothing. The trouble only starts if an earlier overshoot has already left it at the far cell.

I'm comparing the two options for the catch: straight, where the paddle sits under the ball's current column, versus reverse, where it sits one cell over, to see which leaves more slack for the next landing four rows up.

I'm checking the reverse case now: if the paddle sits at the ball's column instead, the zone shifts and the distance to the next landing changes, and I'm testing whether the position works out when the ball has just bounced back from the right wall.

I'm now checking the U-mode travel distances for the ball at different heights. For the upper rows the paddle has to cover about 5.5 to 8.5 cells, and for the lower rows the distance grows as the ball gets closer to the bottom, up to 9.5. I'm also questioning whether the bounce is really one step away when the ball is below row 4.

I'm weighing whether to check for bricks directly at the next row, since that depends on a nonlinear AND of ball position and brick presence, which a linear function can't capture. I'm leaving that out and relying on the soonest-return assumption, which should hold up because shifting the assumption by one row only adds slack.

I'm checking that the paddle keeps enough slack after a bounce, and that the D-mode prediction still holds when the ball is moving down past cleared cells. If the prediction misses a brick from above, the error is harmless, so I'm thinking about whether the randomization I'm planning would help break loops.

I'm checking whether the policy can fall into a deterministic loop that never reaches a brick. The paddle always heads for the nearer zone cell, so the state repeats unless something changes. The only thing that breaks that repetition is a sticky overshoot from the near cell to the far cell, which happens about 10% of the time per arrival.

I'm concluding that the loops only last about ten trips, roughly 150 steps, so they waste time without ending the run. Bricks should still get hit eventually, since a loop with no brick contact under any paddle sequence is unlikely. I'm weighing whether a smarter brick-aiming policy is worth the complexity, and I'm leaning toward randomizing the zone choice instead, which turns the trajectories into a random walk. Next I want to estimate the typical reward rate for a level that starts with 30 bricks.

I'm estimating roughly ten steps per brick early on, with trips stretching toward eighteen steps as the board empties and some of them producing nothing. Averaged out, that's maybe 25 steps per brick, so about 400 bricks over 10,000 steps if the run survives. Since deterministic play can fall into long unproductive loops, I'm considering whether randomizing the zone choice could help, and I'm checking that it stays safe at the final catch step.

I'm considering adding randomness to the zone choice: when the paddle is at the lower of the two zone cells, it would sometimes step right, and vice versa, so the trajectories don't keep repeating. Before committing, I'm checking that a sticky repeat of a random move can't leave the paddle outside the zone at the final catch, since two steps of correction still bring it back in.

I'm weighing whether the randomization could itself cause trouble: a randomized move at D6 followed by a sticky repeat would need two unlucky events in a row to push the paddle out of the zone, so the risk stays tiny. I'm also asking whether randomness is needed at all, since the loops might be broken naturally, and I'm most concerned about the endgame where only a few bricks remain and the ball has to reach one specific cell.

I'm now thinking about whether to randomize the paddle's zone choice or keep it deterministic. I'm starting with pure periodic orbits when only a few bricks remain: from the catch at column b, moving in direction d, I'm computing where the ball lands after the ceiling bounce by folding its unfolded travel distance back into the board.

I'm checking where the ball comes back after the ceiling bounces: for a ball leaving column b moving right, the unfolded travel puts it at about b−3 moving right, and the paddle's zone becomes b−3 and b−2. A straight catch would shift the ball's starting column left by two each trip, while a reversed catch sends it back the other way.

I'm weighing whether the loops are stable at all: each trip shifts the ball's starting column by two, so the orbit sweeps through different diagonals and should eventually reach a brick. I'm leaning toward skipping randomization unless it turns out to be simple to add safely.

I'm settling the output logits so the policy picks right, left, or no-op deterministically, with the other actions pushed far negative. Layer two passes each vote through a saturating tanh, so the signal stays clean before it reaches the output.

I'm checking the output layer's voting math: each mode gives a ±1 vote, so with one right vote the right logit sits at +20 and the others at −20 or 0, which makes the choice effectively deterministic.

Next I'm writing out the layer-2 OR unit, which combines the right-mode and up-mode gates with a bias and a tanh squash.

Writing layer-2 gate formulas...

I'm folding the two paddle-mode votes and the sticky AND-gate into one combined sum per side, but the D and U terms are gated off whenever the sticky state is active, so the mixing doesn't quite work.

I'm checking whether one combined unit can do the job of the separate gates: the sum 2(R_D + R_U) + S-sum stays above −2 exactly in the cases where the right vote should fire. The margins are thin at gain 1, so I'd scale it up with gain 3, which keeps tanh saturated and is plenty for the output.

Now I'm defining the input indexing, with the paddle on row 9 and the ball and trail channels, and writing the linear terms for paddle position and the ball's vertical motion.

Writing the layer-1 gate formulas for the D-mode and L-mode units...

I'm settling on a scaling constant K so the layer-1 margins saturate cleanly, since a value around 12 keeps tanh near 0.995 without making the weights unwieldy.

Setting the layer-1 scale: with K=16 each quarter-unit margin becomes 4, so tanh saturates near 0.9993 and the weights stay as scaled multiples of 16.

Writing out the per-row weight updates with += offsets for the gating terms.

I'm weighing whether to hard-code the layer-1 weights directly or apply the scale factor in place, and leaning toward explicit numbers so nothing depends on in-place operations being supported.

I'm weighing whether to trust the in-place scaling operations or just write the final numbers out directly. Folding the gating offsets into each row as plain values would avoid depending on how the in-place updates get applied.

I'm weighing whether to keep the gating inside each unit or move it into a separate layer-2 AND with direction gates, which would avoid relying on in-place weight updates.

I'm dropping the M-offset approach and instead splitting the direction logic out: layer one gets plain comparison units for each mode, plus two gate units that check whether the paddle-delta is +1 or −1. Layer two then ANDs each comparison with its matching gate, which keeps the weights small and avoids any in-place adjustments.

Writing layer-2 gate formulas...

Writing the output layer's vote weights...

I'm deciding to skip the in-place scaling and write the weights at their final values instead, so nothing depends on *= working. I'm also weighing whether the gate margins can stay readable at that scale.

Now I'm weighing a scale of 10 instead: half-integers become multiples of 5, which keeps the arithmetic simple. That gives tanh(2.5) ≈ 0.987 for the comparison units, and the gated AND units still saturate close to ±1 in each case.

I'm scaling the weights by 20 so each half-integer becomes a clean multiple of 10, which keeps the margins at about 5 and makes tanh saturate almost completely. The threshold placement is the thing I still need to check, because the offsets of ±0.75 depend on whether the folded center is always a half-integer.

I'm weighing the threshold placement for the saturated comparison units: when the target is a whole number the margin is ±0.5, and a half-integer target would need a different offset. One option is to shift the target to a half-integer so both cases share the same ±0.75 threshold, or to give each unit its own bias.

I'm settling the threshold question for the S-mode units: I can either set a separate target for each of the two units, or use a single offset of ±0.75 for the whole family. Both work because the integer margins stay clear at this scale, so I'll keep ±0.75 everywhere. Next I need to solve the cycles for the D, U, and S modes across their rows.

I'm now setting up the constraints for each mode's two weight vectors: a right-moving ball at x pairs with the trail at x−1, a left-moving ball at x pairs with the trail at x+1, and the wall bounces at 0 and 9 each need their own equation. Each of these fixes a sum of A and B at the relevant position.

I'm now checking the wall-bounce cases in each mode: in D-mode the ball at the right wall has come down-right and reverses to down-left, in U-mode it reverses to up-left, and in S-mode it bounces off the side wall and a brick at the same moment.

I'm checking the wall-bounce and corner cases: at the right wall in S-mode, the ball bounces off the side and a brick at once, and the trail stays on the same row, so the structure matches the other modes. Next I'm setting the row-dependent travel distance τ for each mode: 8.5 − y for D-mode, a piecewise formula for U-mode, and a fixed 8.5 for S-mode.

I'm solving the cycle equations for each mode by treating the travel distance τ as the key parameter, since D-mode, U-mode, and S-mode all reduce to the same structure with a row-dependent τ. I need the solutions for every τ from 0.5 to 9.5, which covers all the rows across the three modes.

I'm writing down the closed forms for the right and left folded targets: each is a simple shift of x by τ, reflected back off the wall when it overshoots. Then I'm setting up the cycle order that links the A and B weights around the loop.

Now I'm writing out the edge equations that tie each A weight to its neighboring B weights, one per pairing around the cycle, with the targets for right- and left-moving balls.

Now I'm writing out the edge equations that close the loop back to A(0), with the last pairing checking B(1) against the left-moving target at x=0. I'm fixing the gauge at B(0) = 0, which lets me read off A(0) and A(1) directly from their right-moving targets, and I'm starting to solve for B(2).

Working through the back half of the cycle now, I'm solving for B(4), A(5), B(6), and so on around the loop, each time subtracting the known partner weight from the target.

I'm checking the cycle constraints by working in unfolded coordinates, where each physical position maps to a point on a period-20 triangle wave. The idea is to find smooth periodic functions for the A and B weights that satisfy every pairing at once, instead of solving the 20 edge equations one by one.

Now I'm trying to decompose the target into two even functions, one for each weight family, so the cycle equations collapse into a pattern instead of twenty separate solves.

I'm checking whether a closed-form quadratic can serve as the solution: with the substitution X, the pair a(X) and b(X−1) sums exactly to X − 9.5, with the reflection symmetry holding. For the triangle-wave targets I expect the solution to be piecewise quadratic instead.

Checking that the alternating sum over the full cycle vanishes for any offset, so the system is consistent for every τ.

I'm checking the alternating sign pattern around the cycle: the edges in the X-ordered pairs carry one sign and the others the opposite, so I'm tracking which edges take each sign as I go around.

Now I'm checking the sign pattern: the alternating signs come out to plus for even X and minus for odd X. Next I'm tabulating the right-moving and left-moving folded targets for τ = 0.5.

Working through the alternating solve for the cycle, I'm getting the A and B weights step by step: starting from B(0)=0, A(0) is 0.5, A(1) is 1.5, and the chain continues through A(7) at 10.5.

Now I'm solving the back part of the cycle numerically: B(7) comes out to −4, A(6) to 9.5, B(5) to −3, and A(4) to 6.

I'm checking the τ = 0.5 case and finding the weights for each position, landing on A values of 0.5 through 13.5 and B values from 0 down to −5, with a consistency check at the end that matches.

I'm checking the closed-form pattern for the A and B weights at τ = 0.5: A(x) is x + 0.5 plus floor(x/2), and B(t) is minus ceil(t/2). Plugging in a right-moving ball at x with its trail at x−1 confirms the pairing sums exactly to x + 0.5.

I'm noting that the direction of the ball can be encoded in a floor-and-ceiling difference: it comes out to 0 for a right-moving ball and −1 for a left-moving one. At the walls the same expression gives the correct left-moving value at x = 9.

I'm now trying to split the fold-adjusted target into a part that depends only on position and a part that switches on when the ball is moving left, since the direction flag is a simple floor-and-ceiling difference of the positions.

I'm splitting the two cases apart: the right-moving target cR(x) and the left-moving target cL(x), each tied to the trail weights on either side. Subtracting the two gives a difference equation in B that has to hold across the interior, with the walls handled by their own boundary conditions. I'm now working out A(0) and B(1) from the start of the loop.

I'm setting up a recursion for the B weights: B(0) is zero, and each B(x+1) is B(x−1) plus the difference Δ(x) = cL(x) − cR(x). Then each A(x) follows from its right-moving target minus the previous B weight. I'm also checking that the last step closes the loop consistently, and I'll tabulate Δ for each τ.

Now I'm checking the τ = 0.5 result against the recursion: Δ is −1 everywhere, so B comes out as the staircase I already had, and the closing difference at x=9 matches. Moving on to τ = 1.5, I'm setting the right-moving target at 1.5 through 9.5 for x up to 8, with x=9 folding back to 8.5, and the left-moving target as x − 1.

Now I'm working through the recursion at τ = 1.5: the difference is −1 at the two ends and −3 across the interior, so B steps down in pairs, giving B(1) = −1, B(2) = −3, B(3) = −4, and continuing on.

Checking the B values at τ = 1.5 against the recursion, then working out the A values from their right-moving targets: A(0) is 1.5, and each following A(x) is its target minus the previous B weight, running through A(8) at 19.5.

Now I'm working out the τ = 2.5 case, setting up the right-moving target for the first several positions.

Now I'm setting up the τ = 2.5 differences, where the boundary terms come out to −1 at the ends and −5 through the middle, and I'm starting the B recursion from zero.

I'm filling in the rest of the τ = 2.5 solve: the B weights step down through B(9) = −19, which closes the loop with the expected −1 difference at the last position. Now I'm starting the A weights, with A(0) at 2.5 and each next value set by its right-moving target minus the previous B weight, running up to A(5).

Now I'm working out the τ = 3.5 case, taking the right-moving and left-moving targets position by position and starting to see where the left-moving values begin.

Now I'm checking the τ = 3.5 targets at the edges and interior, getting the Δ differences, which run from −1 at the ends up to −7 through the middle. Then I'm building the B weights from zero, with B(1) at −1, B(2) at −3, and B(3) and B(4) following from the recursion.

Now I'm filling in the τ = 3.5 solve: the B weights step down to B(9) = −23, which closes the loop with the expected −1 difference, and I'm starting the A values, with A(0) at 3.5 and A(5) at 18.5.

Now I'm setting up the τ = 4.5 targets, with the right-moving values for the first positions and the left-moving ones starting from the ball at x = 4.

Now I'm tabulating the differences Δ for τ = 4.5, with the left-moving targets near the walls producing the largest negative values in the middle.

Now I'm filling in the B weights for the τ = 4.5 case, stepping down to B(9) = −25, which closes the loop with the expected −1 difference. Then I'm starting the A values, with A(0) at 4.5 and A(3) at 10.5.

Now I'm setting up the τ = 5.5 targets, with the right-moving values for the first positions and the left-moving ones starting once the ball is near the walls.

Now I'm tabulating the left-moving targets for τ = 5.5, where the ball has moved past the midpoint, and the differences Δ start at −1 and grow to −9 through the middle.

Now I'm checking the τ = 5.5 case, and its difference values match the τ = 4.5 case, so the B weights come out the same. Then I'm working out the A values from their right-moving targets, starting at A(0) = 5.5 and running through A(5) = 18.

Now I'm working through the τ = 6.5 case, setting the right-moving targets from x + 6.5 near the start and switching to 12.5 − x once the ball passes the middle, and I'm starting on the left-moving targets from x = 6 onward.

Now I'm checking the τ = 6.5 differences, which hold at −7 through the middle positions.

Now I'm checking the τ = 6.5 values against the same pattern, since the differences match τ = 3.5, and I'm starting the A weights from their right-moving targets.

Still working through the τ = 7.5 differences, where the right-moving and left-moving targets are being set position by position.

Still checking the τ = 7.5 differences, which come out the same as the τ = 2.5 case, so the B weights are being filled in from there.

Still working through the τ = 7.5 and 8.5 solves, filling in the A weights from their right-moving targets.

Still working out the cost-difference values for τ = 8.5, where the left-moving and right-moving targets are being tabulated position by position.

Now I'm setting up the τ = 9.5 targets, starting the right-moving values from the ball's position.

Now I'm setting up the τ = 9.5 case, where the right-moving targets fall off by one as x grows and the left-moving ones mirror that pattern, so each difference comes out to −1.

Now I'm filling in the A values for the τ = 9.5 case, running the right-moving targets down from 9.5 and checking the last position against the left-moving target.

Checking the τ = 4.5 row again: the ball at (3, 4) moving down-right gives a trail value of 7.5, which matches x + τ and confirms the A and B entries.

I'm checking the ball starting at (7, 4) moving down-right, where the trail value comes out to 7.5 against the true value of 11.5.

Now I'm working out the D-mode weight tables, where each ball row uses the τ value tied to its position, and I'm checking the trail values against the true positions.

Now I'm filling in the D-mode weight tables, starting with the ball rows near the bottom and the τ values that go with each row.

Still filling in the D-mode weight tables, listing the A values for the ball rows near the top as each τ gets set.

Still filling in the weight tables, now the trail rows for the lower part of the D-mode grid.

Still filling in the weight tables, now the trail rows for the lower part of the D-mode grid.

Now I'm setting up the upward-moving weight tables for the ball rows, with the τ values running from 8.5 at the top down to 9.5 at the bottom, and filling in the first two rows' A values.

Still filling in the U-mode weight tables, now the A values for the ball rows running up the middle of the grid.

Still filling in the U-mode weight tables, now the trail values for the upper rows.

Still filling in the U-mode weight tables, now the trail rows for the lower part of the grid.

I'm checking the upward-moving case for the rows near the top, where I'm wondering whether the bounce should be counted at the brick row itself. I'm also questioning the bottom row, since a ball there arriving from below doesn't bounce yet, so the same assumption may not hold.

Still filling in the S-mode weight tables, starting with the ball rows near the bottom and their τ values.

Still filling in the S-mode weight tables, now the A and B values for the ball rows in the lower part of the grid.

Still filling in the S-mode weight tables, now the A and B values for the ball rows near the top.

Still filling in the S-mode weight tables, now checking whether the mirror target for the top row holds up against the next row's U-mode target.

Now I'm working through the gate conditions for the D- and U-mode cases, using the distance from each row to its target and the scaled sigmoid-style thresholds. I'm also reconsidering the final layer's AND logic, since the timing has to line up exactly for the policy to stay correct.

Now I'm checking the dead zone at the top row: when the ball sits at (x, 8) with its trail one row up, the paddle is already in the catch zone when the offset from the fold stays within half a cell, so no move is needed. If the paddle is outside that zone, the policy should steer it toward the target.

Now I'm checking the first-step case, where the ball starts at (0, 3) moving down-right and I need to see which paddle column it should aim for.

I'm checking the start state: the ball at (0, 3) heading down-right should reach the paddle zone around columns 5 and 6, and the paddle at 4 needs to move right. Tracing its path through (1, 4) to (5, 8) confirms it meets the brick-row check cleanly at the first step.

Checking the start state on its own: the first paddle move toward the ball's path is right, and the ball reaches row 8 with the paddle still clear of the catch zone.

Now I'm checking the first few steps of the simulation: the ball's path up to the catch, then how the paddle moves after it and what the upward-moving state looks like one row down.

Now I'm tracing the ball's bounces through the lower-middle rows: at (8,6) the target comes out to 3.5, and the ball then reaches the right wall at (9,5), where the check still holds.

Checking the paddle's catch at the bottom row: the ball should land at column 4 with the paddle already there, so no move is needed.

Now I'm checking the S8 mirror target and how the paddle handles the bounce, and I'm working through the nominal case to confirm the U7 zone still catches the ball.

Now I'm settling the paddle's response at the top row: the mirror target leaves it inside the two-cell catch zone, so it only makes one harmless extra move before the later upward-moving rule takes over.

Now I'm thinking through what happens at the brick rows: when the level clears, the bricks come back as the ball reaches the bottom, so the ball keeps going with no hitch. I'm also considering how sticky actions might throw off the common trip, but the paddle just follows the mirror target and the zone-catch logic, and the typical run should stay well inside the available distance.

I'm checking the corner case at the walls: when the ball lands at a corner, the next trip's target sits at the far wall, about nine cells away, which leaves little slack against sticky actions. I estimate that failure requires two sticky actions in a row at the start, roughly 1%, plus a few other paths. Whether that matters depends on how often the ball actually lands in a corner, which I'm still weighing.

Now I'm comparing where the paddle should sit for the ball's next trip: parking on the edge cell, at 1 rather than 0, gives the straight-up path and leaves the paddle only seven cells from the next catch zone, so the choice of cell 1 looks better than the near cell I'd been using.

Checking the corner case again: with only one cell of slack, a paddle parked at 0 has to cover nine cells on the next trip, so I'm working through how many moves that takes before the ball returns.

Now I'm checking the slack in the corner case: after the catch at the far wall, the paddle has ten actions to cover nine cells, but the first action could be a no-op or a wrong move, so it really comes down to whether the opening move is stuck.

I'm noting that the corner case costs about 1% in failures, and that I'll accept it rather than reshape the catch logic. Next I want to look at the U-phase when the ball passes row 4 without bouncing: the target shifts as the row changes, and I need to check how the zone moves when the unfolded coordinate changes.

I'm checking the U3 step: the paddle has to cover about two cells, then six more actions for the bounce and the return. Without a bounce, the lag grows by one cell per row, so the paddle still has roughly ten actions to catch up. The trouble comes when the unfolded target crosses a wall fold, since the zone can jump back the other way and the paddle then has to reverse direction.

I'm thinking about whether the U-mode target-chasing can fall too far behind when the bounce assumption turns out wrong. The plan is to bound the remaining actions needed to catch the ball under the current assumption and check that the paddle still has enough slack to recover.

I'm checking the slack condition as the assumed bounce row shifts. Feasibility just needs the remaining actions to cover the distance to the zone, and the paddle staying inside the zone is always fine. The worry is what happens when the ball passes a row without bouncing and the target moves under the paddle.

I'm working out the remaining action count under the assumed bounce row: from an upward state at row y, it takes y − 2h + 10 actions to catch the ball, which for rows 4 and below comes to y + 2.

I'm checking the slack on the upward pass: from the U4 state the paddle has six actions to cover its distance, and if the ball doesn't bounce, the U3 target moves two cells in unfolded coordinates, so I need to see how much of the slack that uses up.

I'm checking that the slack never shrinks when the bounce assumption changes: the paddle's remaining actions and its distance to the zone both move together, so the margin stays the same through the upward pass. That means the worst case is whatever slack I have at the corner start, minus any sticky losses.

I'm going to test whether the deterministic policy falls into a loop, starting with the easy case of a full brick wall: each trip removes one brick from row 3. I'll simulate the ball's path from the start, assuming no sticky actions, to see how the first trip unfolds off the right wall and back down toward the removed brick.

I'm tracing the second trip of the ball: it bounces off the left wall, takes out a brick at row 3, and comes back down toward the right side. I'm setting the paddle to cover the zone around columns 5 and 6 as the ball returns.

Tracing the third trip, the ball follows the same route as the first and reaches row 3 without finding a brick at (3,8), since that one is already gone. It then strikes the brick at (2,7), which removes it, and I'm keeping the paddle parked around columns 5 and 6 to meet it.

I'm tracing the third trip further: the ball comes down toward the left zone, and I'm keeping the paddle at 4 for the upward leg, then shifting it left to 3 and finally to 2 so it lands inside the catch zone at columns 1 and 2.

I'm tracing the fourth trip now: the ball bounces off the left wall and takes out the brick at (3,3), then heads down-right toward the right side. I'm moving the paddle right from 2 toward the zone around columns 7 and 8 so it's in place when the ball arrives.

I'm tracing the fifth trip: the ball comes back down through the right side and the paddle drifts left from column 7 toward the catch zone at columns 1 and 2, arriving there just as the ball does.

I'm tracing the sixth trip, which follows the same route as the fourth: the ball bounces off the left wall, clears the brick at (2,4), and heads down-right toward a zone near the right edge.

I'm working out how to make the paddle sometimes choose the other cell when the ball is in the upper rows, so the policy isn't stuck in a loop. I'm planning to add a small probabilistic nudge, set up as a separate unit that only fires when the ball is at row 5 or above.

I'm weighing a randomized tweak for the paddle: when it's in the zone at the left cell with the ball in rows 5 and above, a weak vote for moving right would fire, so the policy sometimes breaks out of a loop. The open question is whether that extra movement adds enough sticky-action exposure to hurt more than it helps.

I'm checking whether the randomized nudge can be limited to the freeze window: a random move at row 5 would have until row 8 to get back, so the sticky-action risk has to be weighed against the loop-breaking benefit.

I'm working out the failure odds of a random move at row 5: I'd need three sticky events in a row, so randomizing only at rows 4 and below keeps the risk around 0.025% per trip. The catch is that those rows only come up for bounces at height 3 or below.

I'm considering whether randomizing only at rows 4 and below is worth it when the ball goes to the ceiling without hitting any brick, since those trips would get four chances to pick a random final cell.

I'm working out the bounce pattern for the next trip, where the ball's entry column b lets me predict the two catch cells and the paddle's one-step move toward the near one, which sets up a reverse bounce and a new b' of b − 2.

I'm noticing that the paddle would reverse the ball along the same diagonal it arrived on, so the trip from the ceiling just retraces itself. That makes the two-cycle between b and b−2 an exact loop, with the ball's direction flipping back and forth between up-right and up-left.

I'm seeing that the ball's bounce pattern creates a two-cycle between two parallel paths, since the reversed bounce just shifts the path by one column rather than retracing it exactly. If no bricks lie on either path, the policy loops forever, and only sticky-action noise would break it. I'm considering how those sticky events could change the outcome.

I'm weighing whether the sticky-action noise will actually break the two-cycle: if the paddle overshoots when it stops, it lands on the other cell and the straight bounce shifts the loop, though that only happens about one time in ten per trip. At that rate the policy could stay stuck for around ten trips, so I'm considering randomizing the choice at the early descent rows as a way to shorten the wait.

I'm now estimating how much the randomized exploration would save near the end of a level, where only a few bricks remain. Each unproductive trip probes about three cells on the way up and three on the way down, so with one brick left a trip has a real chance of hitting it.

I'm estimating the total cost of clearing a level: the last few bricks each take many trips to hit, so summing those waits gives roughly 1,100 to 1,200 steps for 30 bricks, which would come to about 250 points over eight levels if the policy never dies and the randomization works well.

I'm checking the reversal more carefully: with the paddle at b−2 after the reverse, the next trip's unfolded path lands the ball at column 16 − b′ under the wall fold, so the cycle depends on where b sits relative to that fold.

I'm checking the wrap-around step for the next bounce: after folding the ball's path off the left wall, I get a new position that depends on which side of column 7 the paddle sits. For a paddle in the left region, the ball lands at the cell two columns to the right of the paddle, which is the one the paddle reaches first, so it reverses back up-right. That means the cycle closes with the ball returning to its original column.

I'm weighing a randomized exploration step for the late stage of each level, because the deterministic policy tends to fall into two-cycles on empty paths where only sticky-action noise can break out.

I'm thinking about randomizing the paddle's final cell during the descent rows: if it sits in the zone between two cells, each row gives a chance to step toward the other one, so with four rows the final choice comes out close to a coin flip. For wall cells, though, the tie-breaking vote only pushes one way, so that case needs separate handling.

I'm checking the risk of a randomized move at row 4: after it, the paddle sits on the other cell, and sticky actions over the next few rows could push it out of the zone, so I'm tracing how far it would drift by the final step.

I'm working through the failure odds for a randomized move at row 4, tracing how a sticky overshoot at the next row could push the paddle out of the zone before the final step lands.

I'm checking the failure odds for a random move at row 4 once more: if the paddle is pushed out by a sticky action at D5, it can still recover by D8 unless another sticky event hits at D6 or D7. Working through the branches, most paths get it back into the zone before the final step, and only a small fraction end outside it.

I'm checking the baseline risk too: even without randomizing, arriving at a zone cell lets a sticky action push the paddle to the far cell and then out, so the failure odds for the random move are about the same size as the existing ones.

I'm considering whether to restrict the randomization to rows 1 through 3, since that keeps the chance of a sticky overshoot leaving the paddle outside the zone low. With a move probability around 0.35, the odds of an odd number of flips come out near even for trips that reach row 1, and they drop for trips that arrive later.

I'm settling on randomizing only in rows 1 through 3, since those are the only unproductive trips where the choice matters, and it keeps the chance of a sticky overshoot leaving the paddle outside the zone low. Trips that already hit a brick on the way up are productive anyway, so the random step only needs to cover the empty ceiling trips.

I'm weighing a single randomized choice at row 4 instead of a random walk: if the paddle sits on one cell of the zone, it would move to the other with probability about one half. That keeps the failure risk to roughly 0.1% per trip that passes through the zone, but it only helps the trips that reach row 4 while the paddle is already there.

I'm weighing whether the extra risk from randomizing at rows 1 through 3 is worth it, since it could speed up brick-finding on the empty ceiling trips, though it also raises the chance the paddle gets pushed out of the zone.

I'm weighing a different option: randomizing the choice once at the start of the ceiling descent, in the S0 state, rather than at row 4. That would let the dead zone shift without a random walk through the zone, though I still need to check whether that shift helps or just moves the same risk elsewhere.

I'm estimating how often the paddle lands in the dead zone during the ceiling trips, since it has only about two moves to close the gap before row 1. The gap depends on whether the paddle was still chasing the one-brick target, which sits two columns away from the ceiling target. That makes the random walk during rows 1 through 3 worth checking against how far the paddle usually is at the start of the descent.

I'm tracing the ceiling chase step by step: after the bounce at S8 the paddle moves to 5, and at U7 it steps left to 4, which is inside the zone. The next few rows are no-ops because the paddle already sits in the zone, and the ball keeps moving up and to the left.

I'm tracing the ceiling bounce through the last few rows: the ball drops to column 3 and then 2, and the paddle shifts left to 3 and then 2 as it tracks the zone. On the final row the paddle ends on 3, which lands it inside the zone.

I'm tracing the ball's path from S0 down-left through the walls, and checking where it lands on row 8. The paddle ends at column 3, which is the straight bounce, not the near cell I'd expected. That's because the paddle overshot left while chasing the hypothetical targets and came back from that side. So the dynamics don't settle into a simple two-cycle, but they're still deterministic and will eventually repeat.

I'm now weighing a randomized move restricted to the ball's descent rows, where the choice between paddle cells matters. I'm planning two small layer-one units that fire when the randomization condition is met, one for each direction.

I'm setting the ball-row weights for rows 4 through 8 to large values so the randomized votes drop out there, limiting the randomization to rows 1 through 3. Row 0 is never in the descent mode, so its weight doesn't matter, since the gate in layer 2 already blocks it.

I'm setting the ball-row weights for rows 4 through 8 to large values so the randomized votes drop out there, limiting the randomization to rows 1 through 3. Then I'm wiring the two randomized votes into a layer-two gate so they only fire in descent mode on those rows.

Working out the weak-vote output now: I want the right logit to land near -0.6, so I'll add a term scaled by (v6 + 1) and solve for its weight from the existing -16 baseline, which gives about 7.7. When both the full vote and the weak vote fire, the right logit goes far positive.

Now I'm setting the weak-vote weight so the right logit lands at the target value, which makes the single randomized vote come out to roughly the intended probability. I'm also checking that the gain is high enough that the layer-two outputs saturate cleanly at plus or minus one.

I'm settling on q = 0.5 for the random step, since a fair coin makes the final cell uniform after any single randomized move in the zone. I'm weighing whether one randomized row is enough or whether several rows give better coverage, and I'm noting that extra random moves also add exposure to the sticky 10% repeat.

I'm checking how often the paddle would be stuck in the zone under a random move at row 3: the chance of a sticky repeat three times in a row comes out to about 0.1³, and with the coin at 0.5 that is roughly 0.05% overall. I'm now recomputing that failure rate to see whether it stays small enough.

I'm recounting the failure chains for the last random row: if the paddle sticks on the way back, it can fall out of the zone and need several more moves to recover. Multiplying the stick probabilities gives roughly 5e-4 for one path, and I'm adding in the other chain where the paddle re-enters the zone after an earlier sticky repeat.

I'm checking whether randomizing at rows 1 and 2 only would keep the failure chance negligible, since that needs four sticky repeats in a row instead of three. I'm also asking whether the paddle is already in the dead zone by row 1 or 2 during the h=0 trips, starting from the U0 state.

I'm deciding the paddle should have about two or three moves to reach the zone before the row-1 observation. I'm going with randomization on rows 1 and 2 with q=0.5, and I'm skipping the S-mode case because it follows a different functional. I'm also noting that only ceiling trips with no brick contact can form a loop, so those are the only ones that matter here.

I'm checking the randomized-vote idea against the ceiling-trip case: bricks struck from below or above would make those trips productive, so only the trips with no brick contact can loop. I'm also considering the single-cell zone at the wall, where the weak vote just pushes into the wall and does nothing.

I'm settling on a random step at rows 1 and 2 only, since randomizing at row 3 would add too much risk of getting stuck out of the zone. The question now is whether going "straight" or "reverse" should be a fair coin, or whether the default near cell is better.

I'm checking whether the ball could get stuck bouncing between the ceiling and a brick, and noting that each such bounce still scores, so it isn't an unproductive loop. I'm also looking at whether a ball that strikes a brick and reverses direction could land on another brick in the next step.

I'm checking the case where the ball bounces off a row-1 brick and its next cell lands on a row-3 brick. Since the strike flag is still set from the earlier bounce, the ball just moves into that brick cell without reflecting or scoring.

I'm checking the ball's path in the corner case: if it hits the ceiling at the edge, it reverses horizontal direction and the vertical one flips, and I'm confirming that the trail of bricks it leaves stays consistent with the descent and ascent modes I've already planned.

Checking the corner case at the ceiling: a ball on the top-left corner cell bounces down-left and I trace it through the zone at the left wall, which matches the wall-state value I already assigned. I'm also tracing a ball moving up-right from the eighth column, where the next step lands in the top-right corner and reverses to down-right.

I'm checking the corner case at the top-right: a ball at (8,0) moving up-right reaches (9,0) and bounces down-right, and the wall-state value there works out to 1.5, which matches the zone center I expected.

Now I'm setting up the first layer of the network, where one unit computes the right-moving signal from the ball's position and the trail, with a fixed bias to shift the threshold.

Still setting up the network units, this time the left-moving and vertical signals, the stuck-in-row helpers, and the gates that keep randomization limited to rows 1 and 2.

I'm setting the gating units for the bottom-row weights so the right and left votes only fire in rows 1 and 2, then moving on to the second layer's three vote signals built from the first-layer units.

Still writing the output layer equations...

Checking the weak-vote arithmetic: with c = 20 and w = 10, the no-vote, weak-only, and full-vote logits come out to the values I need, so the tie between doing nothing and the weak move sits at 50/50. Now I'm working out the threshold for the weak right vote, where it should fire once the fraction F reaches one half.

Checking the precision of the weak vote now: the ceiling-side margins come out near tanh(5), so the fractional threshold behaves as intended.

I'm checking the logit for the right move: the wall-side terms cancel out to roughly zero, and the weak vote's contribution is just enough to balance it.

I'm settling on randomization only at rows 1 and 2, with the paddle's choice at those rows landing close to even odds. I'm also looking at whether the randomized move is needed at all once the paddle is already in the zone for a ceiling trip.

I'm checking how far the paddle can drift during the U3 to U0 steps, since each hypothetical target shifts by two cells and the paddle only moves one cell per step. From the zone at U4, the worst-case distance after the shift is about 2.5 cells, so I need to see whether it can still reach the zone before the row-1 observation.

I'm checking the lag in the worst case, where the paddle starts in the zone and the hypothetical target keeps shifting one way with no reflection. Each step moves the paddle one cell, but the target shifts two, so by the row-1 observation the paddle is still about 1.5 cells out. That means randomization at rows 1 and 2 wouldn't trigger in that case, and the paddle would only reach the zone by the nearest deterministic cell.

I'm checking whether randomizing only at rows 1 and 2 leaves enough time for the paddle to reach the zone in a ceiling trip. The lag builds up when the target shifts without reflecting, so I'm weighing whether aiming one hypothesis further ahead in U-mode could shrink it.

I'm weighing whether randomizing only at rows 1 and 2 is enough, since a paddle drifting from the zone in a ceiling trip may not get there in time. Assuming the ball returns soonest is safe, but the time left before the bottom row is long for rows 0 to 3, so the real question is which single assumption best positions the paddle there. I'm considering whether to randomize in later rows instead.

I'm weighing whether to randomize at rows 3 or 4 instead, since row 2 leaves the paddle too little margin. The risk at row 3 is roughly 0.05%, a bit higher at row 4. If the paddle arrives late at the zone, I'd need the randomized move further down, and I'm checking what follows from that.

I'm weighing whether to assume the ball returns straight to the ceiling for the upper rows, since that would let the paddle reach the zone sooner than the soonest-return assumption does.

I'm working out the cycle solutions for the upper rows, where the hypothetical target is offset by a larger amount, and I'm treating the offset as a longer shift that still follows the same period-20 pattern.

I'm checking the shifted targets for the upper rows: the cycle solution at τ = 10.5 is just the mirror of the τ = 0.5 solution, so the same alternating-sum consistency holds. Then I'm looking at the h = 0 assumption at U3, where a wrong guess leaves the paddle up to about six cells away from the true zone.

I'm checking where the paddle ends up if I assume the ball goes straight to the ceiling for U3. The paddle starts near the row-4 zone, moves one cell per step, and I'm measuring how far it lands from the row-3 zone and how many actions remain before the bottom row.

I'm checking the worst case for the U2 step: if the ball bounces at row 2, the paddle has had two moves toward the ceiling target, so its distance from the true zone is at most about six cells, with seven actions left.

I'm checking the worst case for the U2 step: if the ball bounces at row 2, the paddle has made two moves toward the ceiling target, so it could be about six cells from the true zone with seven actions left.

I'm checking the worst case for the upper rows by testing whether the paddle can end up on the far side of the target. That would require a reflection in the offset, and I'm working through the conditions under which the two targets fall on opposite sides of the paddle's position.

I'm checking the worst case for the upper rows, and a paddle that moves toward the ceiling target for two steps ends up about four cells from the row-2 zone. With seven actions still left, that leaves a margin of about three, so assuming the ball goes straight to the ceiling for U3 or U2 looks safe.

I'm weighing whether to assume the ball returns to the ceiling for the upper rows, or to keep the soonest-return guess. Near the top, the soonest-return guess is usually right, so a ceiling assumption would mostly add wasted moves that I'd have to correct later, though the paddle still has enough time to recover.

I'm considering a different split: keep the soonest-return guess for the upper rows, but assume the ball goes straight to the ceiling at rows 1 and 0. Checking the lag that builds up at that switch, starting from where the paddle is after the row-2 step.

I'm noting that the total shift from the row-4 zone to the ceiling zone is 8 cells no matter which assumption I use for each row, so the paddle needs eight moves in the worst no-reflection case. Assuming the ceiling earlier doesn't shorten that; only anticipating the move before row 3 would.

I'm checking how far the paddle's target zone moves for different starting positions, since the unfolded shift is 8 cells and the gap depends on whether the triangle wave reflects between them.

I'm checking the worst-case arrival times for a direct assumption that the ball returns to the ceiling from U3 onward. Paddle distances of 8 arrive too late for the bottom rows, while 6 or less lands in the zone in time for the random move at D2 or D3.

I'm checking the safety of assuming the ball goes straight to the ceiling at rows 3, 2, and 1, in case it bounces earlier. If it does, the paddle still has enough remaining actions to recover, so the slack seems fine, though I want to confirm how far it has drifted by each step.

I'm checking how far the paddle can drift when the ball bounces at row 3: it moved one step toward the ceiling target, so it's within about 3 cells of the zone, with 6 actions left. Bouncing at row 2 is the tighter case, where the paddle has moved two steps and I'm estimating the gap to the zone from the cell positions.

I'm checking the bounce at row 1: after three steps toward the ceiling target, the paddle is within about two cells of the zone, with the distance depending on whether the target lies on the far side of the paddle's starting position.

I'm checking the edge case where the paddle and the target fall on opposite sides, and the window where that can happen for the row-1 zone is empty, so it never occurs. That leaves the distance to the row-1 zone at most about six cells with eight actions left, which is enough slack. The main worry with assuming the ball returns to the ceiling is that the paddle slowly falls behind the true zone, losing roughly one cell of slack per step when it drifts the wrong way.

I'm checking the slack at the row-4 step: if the paddle is five cells from the row-4 zone with only six actions counting the U4 move, the margin is just one, so I'm tracing how that margin changes after the move toward Z4 and the observation at row 3.

I'm checking the corner case where the paddle starts far from the row-4 zone and has to walk right for several steps. If the ball reaches row 3 while the paddle is still five cells behind, leaning toward the ceiling target could push the paddle further from the row-3 zone and cut into the remaining slack.

I'm checking the case where the ball bounces at row 3 and the paddle is at column 4 with six actions left, since it only needs three moves right to reach the zone at columns 7 and 8. That leaves a slack of about three, so the leftward move under the ceiling assumption is still safe.

I'm checking whether the corner case is really tight: the reflection brings the row-3 zone closer, so the crude bound overstates the risk. The dangerous setup would need the paddle far from the row-4 zone, the row-3 zone two cells further off, and the ceiling zone on the paddle's side, but that last condition contradicts the row-4 position, so it can't happen.

I'm checking whether the corner case is even reachable: the paddle would have to sit near column 3 or 4 when the ball reaches row 3, with the row-4 zone at 7.5. If that holds, the paddle has about six actions left and would land right at the edge of its slack, so the ceiling assumption could be too tight there.

I'm checking whether the paddle could really be nine cells from the row-4 zone at the catch, which would only happen in the corner case where the ball starts at the far left or right.

I'm checking the case where the paddle starts just one or two cells from the row-4 zone: after the catch and four moves toward it, the paddle is within one or two cells of the row-3 zone, so the worst-case ceiling assumption still has enough slack.

I'm weighing the direct Z0 assumption for rows 3, 2, and 1 against the soonest-return hybrid, and I think the direct version is fine. Bouncing at row 3 costs only one wrong step before things line up again, and when the ball goes on to the ceiling the paddle arrives early enough to randomize at D1 and D2.

I'm wondering whether to pick between the soonest-return and ceiling assumptions based on brick density, since a simple count of bricks in rows 1 and 2 could act as a proxy. It's a linear feature I could gate with a threshold. Still, I'm asking whether the extra complexity is worth it over just committing to one assumption.

I'm checking the ceiling case for row 1: there are no bricks on row 0, so a ball at row 1 heading up always reaches the ceiling next, and I can treat that as certain rather than as a possible bounce.

I'm noting that a ball at row 1 heading up can only reach the ceiling next, since there are no bricks on row 0, so that case is exact. At row 2 the ball either bounces off a brick on row 1 or reaches the ceiling, giving two possible arrival times. At row 3 there are three possibilities, and the bounce row decides which one applies.

I'm seeing that the two assumptions give the same worst-case lag over the remaining actions, so the difference only shows up when reflections make the paddle zigzag. Since the row-1 and row-0 cases are exact anyway, I'll keep the soonest-return target for rows 3 and 2 and use the exact ceiling target for rows 1 and 0.

I'm now estimating how often the paddle arrives late at the row-4 zone, using the distance distribution from the zone to the ceiling target. Counting the actions before each observation, a distance of 8 puts it in the zone only by the row-4 observation, while shorter distances get there by the row-2 or row-3 observations.

I'm checking whether the dist-8 trips could keep recurring, since those arrivals come too late for any randomization at rows 1–3. A two-cycle made entirely of such trips looks possible if the paddle's zone stays near one wall, so I'm testing whether sticky noise would eventually break it.

I'm checking the dist-8 cases: with the next target at the far wall, the gap between the row-4 zone and the ceiling target comes to 8 only when the ball starts at b = 0, 1, or 2 heading right.

I'm checking where the paddle would be when the ball reaches row 3, since for launches near a wall it has to travel a long way toward the row-4 zone, and I'm working out the zone positions it lands on at that point.

I'm working through the randomization window for the launch case b=0: the paddle lands at 5 after five moves, then steps to 6, 6, 5, 4, and 3, so it reaches the zone at the D2 observation and can randomize from there.

I'm running the b=2 launch case now: the paddle's next zone sits near column 7.5 and the ceiling target near 0, so I'm tracing where it lands at each step to see whether it can randomize before the ball returns.

Checking the paddle's travel toward the row-4 zone when the ball starts near a wall: it lands at 7 after five moves, and from there it reaches the row-0 zone on the D2 action, so it can randomize by D3. The row-0 zone is a single cell, so nothing to choose there. Because the paddle hasn't reached the row-4 zone yet, its travel isn't just the direct distance, and randomization at D2 or D3 should be available in most cases, so I'll use rows 1 to 3 for that.

I'm weighing the risk of randomizing at row 3: roughly 0.03% per ceiling trip, which adds up to around 8% over a full episode, against about 2% if I limit randomization to rows 1 and 2.

I'm settling on rows 1 and 2 for randomization and skipping the extra S0 or U0 votes, since one coin flip is enough once the paddle is in the zone by the D2 observation in the cases I traced.

I'm settling on randomizing only at rows 1 and 2, since the paddle is usually in the zone by the D2 observation. A random move at D2 would only fail after four sticky noise steps in a row, about 1e-4 times 0.5, so the risk is small.

I'm now checking the target times for the upper rows: for row 3 the soonest-return target is 6.5, for row 2 it's 7.5, and for row 1 the exact ceiling target is 10.5. Row 0 uses 9.5. For the row-1 case I'm working through the solution by reflecting the 0.5 values, which gives a list of arrival times starting at 8.

I'm checking the solution by tracing a concrete case, the ball at (4,1) moving up-right, and the result matches the target at 4.5.

I'm checking the unfolded positions for the ball at (4,1) heading up-left, which gives 5.5, and confirming it matches the direct trace. I'm also testing the wall case at (9,1) and (0,1), where the formula gives 0.5 and 8.5 and the reflected positions agree.

I'm checking the unfolded formula against a few more points, and it holds: the ceiling target for row 1 matches the reflected positions. I'm now writing out the row-0 table of arrival times, starting with the first few entries.

I'm now writing out the table of arrival times for the ball's rows, starting with row 7 and the first few entries.

Now I'm filling in the arrival-time table for the row-1 ball positions, working through each column.

Now I'm writing out the trail-position arrays for rows 5 through 0, checking each row's values against the ceiling targets.

I'm now going back over the U2 case, where the soonest-return target for row 2 is 7.5, to see whether the paddle can still land in the zone before the ball comes back.

I'm checking the bounce at the upper rows: at U2 the ball bounces off the row-1 bricks, and I'm assuming the soonest-return timing as the default, since row 1 is usually still mostly intact early in a level. At U3 the same check depends on whether row 2 has a brick at the ball's next column.

Now I'm checking the trail position for the ball coming down from the ceiling, confirming that a ball in row 8 can't occur and that the trail-above pattern only appears on downward moves. I'm also considering how a top-wall hit leaves the ball and its trail both on row 0, and I'm double-checking the timing assumption that each action is applied before the ball moves.

I'm checking the wall-catch case where the ball lands at column 9 moving right, which flips it to up-left, and confirming the mirror target of 0 matches the zone. I'm also verifying the generic bounce at b=6, where both directions give a zone containing the mirror target of 3, and then I'm turning to the brick-bounce cases for the middle rows.

Now I'm checking how the sticky-action noise affects randomization, and whether the zone rules for the mode rows still hold. I want to confirm that the randomization weights only switch on for the ball rows where the paddle can actually reach the zone in time, and that they stay off everywhere else.

I'm settling the weak votes: randomization only fires in the D-mode rows where the paddle can reach the zone, and the trail-row weights are zero everywhere else. With the paddle one cell from the zone, the weak vote pushes it toward the other cell, and then it pushes back.

Now I'm setting the output layer and bias, giving the no-op action its index and pushing the unused actions down hard. I'm also checking that left and right can't both vote in the same mode, since the two bands don't overlap.

Writing the arrival-time tables for the remaining τ values...

Still writing the arrival-time tables for the remaining τ values...

Still writing the arrival-time tables for the remaining τ values...

Still checking the arrival-time table against the cR and cL values for each τ.

Still checking the arrival-time table: for each of these states I'm confirming the right-move and left-move values against the neighbouring B entries, and the checks so far all match.

Still checking the left-move values against the neighbouring B entries, and the ones so far agree.

Still checking the right-move values against the neighbouring B entries for τ = 2.5.

Still checking the left-move values against the neighbouring B entries for τ = 2.5, and the right-move values match so far.

Still checking the arrival-time values for τ = 3.5, comparing the right-move and left-move entries against their neighbouring B values.

Still checking the right-move values for τ = 3.5 against the neighbouring B entries, and those agree so far.

Still checking the left-move values against the neighbouring B entries for τ = 3.5, and the ones so far agree.

Still checking the right-move values for τ = 4.5 against the neighbouring B entries, and the first few agree.

Still checking the left-move values for τ = 4.5 against the neighbouring B entries, and the right-move ones agree so far.

Still checking the arrival-time values for τ = 5.5, with the right-move entries going through the neighbouring B values.

Still checking the right-move values for τ = 5.5 against the neighbouring B entries, and the first several agree.

Still checking the left-move values for τ = 5.5 against the neighbouring B entries, and the ones so far agree.

Still checking the right-move values for τ = 6.5 against the neighbouring B entries, and the first few agree.

Still checking the left-move values for τ = 6.5 against the neighbouring B entries, and the right-move ones agree so far.

Still checking the right-move and left-move values for τ = 7.5 against the neighbouring B entries.

Still checking the right-move values for τ = 7.5 against the neighbouring B entries, and the ones so far agree.

Still checking the left-move values for τ = 7.5 against the neighbouring B entries, and those agree so far.

Still checking the arrival-time table for τ = 8.5, confirming the right-move entries against the neighbouring B values.

Still checking the left-move values for τ = 8.5 against the neighbouring B entries, and those agree so far.

Still checking the arrival-time values for τ = 9.5 against the neighbouring B entries, and the first several agree.

Still checking the right-move and left-move values for τ = 9.5 against the neighbouring B entries, and the ones so far agree.

Still checking the left-move values for τ = 9.5 against the neighbouring B entries, and the ones so far agree.

Still checking the arrival-time table for τ = 10.5, working through the right-move values against the neighbouring B entries.

Still checking the remaining right-move and left-move values for τ = 10.5 against the neighbouring B entries, and the ones so far agree.

Still checking the left-move values against the neighbouring B entries for τ = 10.5, and those agree so far.

Still checking the bounce values at the edges of the board for τ = 10.5, confirming the last few right-move and left-move entries against the neighbouring B values.

Still checking the Breakout arrival-time values, confirming the τ=10.5 boundary cases against the bottom-row zone.

Still checking the τ=10.5 boundary values against the formulas for the downward-moving modes.

Still writing the weight tables, now filling in the ball-channel rows for the downward-moving unit.

Still working out the weight values for the downward-moving unit: I'm recomputing the remaining ball-channel rows, starting with row 3 and continuing through row 8, to make sure each scaled value is right.

Still scaling the arrival-time rows by 20 for the τ=7.5, 6.5 and 5.5 cases.

Still scaling the τ=1.5 and τ=2.5 rows by 20 into the weight table.

Still filling in the weight rows, now the τ=8.5 and τ=9.5 arrival values scaled by 20.

Still writing the weight table, filling in the remaining τ=3.5 scaled values.

Still writing the trail-channel weights for the downward-moving unit, filling in the rows from τ=7.5 through τ=5.5.

Still writing the upward-moving ball rows, filling in the weights for row 0.

Writing the upward-moving trail weights now, starting with the row for the bounce at the ceiling.

Still writing the trail-channel weight rows for the upward-moving unit, filling in the values for rows 1 through 6.

Still writing the weight tables, now the trail-channel rows and the ball-channel rows for the serve-mode unit, checking each scaled value against its τ.

Still writing the weight tables, now the serve-mode rows and the trail-channel rows, checking each scaled value against its τ.

Still writing the weight tables, now the paddle input and the bias values for each unit, plus the gate units that track whether the ball is moving down or up.

Still writing the weight tables for the two weak units: their ball rows are set to match the downward unit in rows 1 and 2, and pushed far negative or positive elsewhere, with the trail rows and paddle kept the same.

Still writing the weight tables: the layer-2 weights are next, starting with the first two units.

Still writing the layer-2 weights, filling in the connections for the last few units.

Still checking the layer-2 weights, confirming each output unit's positive and negative contributions for the two states.

Writing the output weights now: the right-move unit gets positive weights from the downward-ball and gate-style units, and the left-move unit mirrors that, with biases set so that no votes gives a negative right score and a full vote gives a positive one. Checking the three cases, the totals come out to -20, +20 and 0 as intended.

Checking the full-vote and weak-vote totals, they come out to 40. I'm also weighing whether the weak votes should apply in the zone, and whether random moves could push the paddle out of position.

I'm double-checking how the state is recorded after each action: the trail holds the previous position and the ball holds the new one. I'm also re-reading the bottom-row branch, where the ball either reflects off the paddle or passes beside it.

Still tracing the paddle-bounce branch: I'm checking how the ball's direction flips when it hits the paddle, including the case where a wall flip already happened on the same step.

I'm tracing the paddle-bounce reversal: when the ball hits the paddle's edge, the direction flips to up-left or up-right. Then I'm checking a concrete case, the ball at column 4 moving down-right into the paddle at column 5, to see where it lands next. I'm also starting a mirror analysis for the ball at the bottom-row column after the bounce.

Still writing the weight tables, now the input indexing for the first layer: each row's ball, trail, paddle and brick channels sit at fixed offsets in the flattened observation.

Still writing the weight tables, now the input indexing for the first layer, checking that the ball, trail, paddle and brick channels land at the right offsets.

Still checking the paddle-movement rule at the last step: the left move works out when the paddle is one cell to the right of the mirrored target, but I'm now testing whether a threshold based on the distance between the paddle and the mirrored position would handle both ball directions in a two-cell zone.

Checking the mirrored-target case at the last step: with the paddle exactly at the trail position, the linear form gives the ball's x plus a constant in the first term and the trail in the second, but the paddle term doubles, and that doubled coefficient can't be set for row 8 alone since the paddle weight is shared.

Checking the paddle-position term at the last step: the mirrored target can't get its own coefficient without breaking the shared paddle weight, so I'm weighing whether that mismatch actually matters in practice.

I'm working through the paddle's decision rule at the last step, comparing the true target against the simpler mirrored-target rule. The two differ by half a cell depending on the ball's direction, so I'm checking what threshold on the mirrored distance would give the same right-or-left choice.

Checking the mirror rule against the exact target: the two only disagree by half a cell, and only when the ball moves up-left with the paddle sitting on the mirrored cell, which just shifts the paddle within the catch zone. I'm treating that as harmless and keeping the rule. Next I'm looking at the upward phase's soonest-reach logic for the U3 and U2 units, and the transitions between them.

Still working through the trail weights for the upper rows, checking that each ball row pulls from the trail row just above it. Then I'm testing how the tanh gates behave when a unit lands in an intermediate state.

I'm checking the tanh gates' robustness: with the mode units off, the AND terms stay pinned near -1, and in the correct mode the decision margins for the half-integer and integer cases still clear the thresholds.

I'm checking the corner case where the ball launches right from (0,8) with a height of 4, to see whether it returns into the catch zone at column 9, and I'm estimating how likely that slack-one case is to fail.

I'm checking how often the ball lands on the far-left corner, since that case leaves only one cell of slack on the return, and I'm estimating how likely the paddle is to be in position for it.

I'm estimating how often the slack-two corner cases would actually fail: they need three sticky actions in a row at the start, so that's roughly a 0.1% chance, and I'm checking whether the distance-eight landings push those trips any closer to trouble.

I'm checking the sticky-action risk at the corner: if the paddle has to reverse direction to reach the catch cell, a sticky action costs two steps instead of one, which could push a slack-one case into failure.

I'm checking the sticky-action cost at the wall: if the paddle is already at cell 0, a sticky left move just stays put, so a reversal there costs only one step and the corner is safe. Overall I estimate the failure rate per trip at around 0.03 to 0.05 percent, so most episodes should reach the step cap. Next I'm looking at whether the ceiling trips can be made more efficient and how the level-clearing ending plays out.

I'm working through how often a remaining brick actually gets hit on a ceiling trip: each trip is about 18 actions, and the up and down passes each cross a couple of cells per row, so I'm estimating the chance of a given brick being struck from either direction.

I'm estimating how many trips a level takes and what that means for the score: roughly 650 steps per level, so about 450 points over the episode. I'm also weighing whether the randomized catch is worth it, since deterministic loops would make the endgame several times slower.

Now I'm checking whether the coin-flip on each ceiling trip actually reaches all the launch states. From a rightward launch at column b, the ball lands at b−2 with the direction chosen at random, and from a leftward one it lands at b+2, so the column drifts in steps of two and keeps its parity in the middle of the board. I still need to see what happens near the walls.

I'm checking how the wall cases work out: from a ball position at column b moving right, the fold maps it to 2 − b on the left side, and for b = 2 the ball lands in the single cell 0. The parity of the launch column flips at the walls, so the randomized catch can still reach every launch state.

I'm looking at whether the randomized catch could also be used in the U1, U0, and S0 states, where the ceiling is certain and the targets are exact, so that a coin flip happens more often before the paddle has to be in zone at D1 or D2.

I'm double-checking the paddle's fallback for the case where it isn't in the catch zone by the second-to-last step: it would just reach the near cell later, which is fine for that trip. I'm also confirming that the weak-vote gate only fires with the ball descending in rows 1 to 2 and the mirror offset at or above 0.5.

Now I'm writing out the weight matrix for the first layer, with units for the right and left decisions in each mode, the gate units, and the wall units. I'm filling in the columns one at a time, since the two ball-direction units share weights and differ only in their bias.

Still writing the weight matrix, so I'm counting how many statements it will take, around 150 at this rate. I'm also considering whether a 2-D slice assignment could shorten the code.

I'm now checking whether a strided row range can be combined with a two-column block in a single assignment, but I'll keep it safe and use plain forms. For the gate channels I'm considering filling each row's strided range with one value, which would cut down the number of statements.

Still writing the weight matrix, so I'm filling in explicit value lists for each row range of the gate channels.

Still writing the weight entries for the gate channels, row by row.

Still writing the weight entries for the dynamic units, filling in the ball and trail rows one block at a time.

Still writing the weight entries for the dynamic units, filling in the trail rows for the right and left decision units.

Still writing the weight entries for the dynamic units, filling in the trail rows and the paddle row for the right and left decision units.

Still writing the weight entries for the upward units, filling in the ball rows for the upward decision units.

Still writing the weight entries, now the trail rows for the upward units.

Still writing the weight entries for the symmetric units, filling in the ball and trail rows for the stay-in-place decision units.

Still writing the trail values for the upward units, checking the ball-to-trail combination at row 6.

Still writing the weight entries for the symmetric units, checking the sign pattern of the trail values against the ball values at each row.

Still writing the weight entries, now checking the up-mode values for the next few rows.

Still writing the weight entries for the symmetric units, checking the ball-to-trail values for the upward trip from row 3 to row 2.

I'm checking the first ceiling-trip example by hand: the ball at (6,1) moving up-left, with the trail from (7,2), gives a weight sum of 3.5, so the decision is no-op, and then I'm tracing the bounces off the top and the walls to confirm the paddle ends up near column 3.

Still checking the last few states, the D1 case comes out at 3.5 as well, so the fallback is right there.

Still checking the trail values for the downward states, confirming the D3 through D5 cases each land on a 3.5 center.

I'm checking the downward cases one by one, confirming that each trail value lands the center at 3.5 for D5 through D8. Next I want to see how the gating behaves when the ball is on row 0 with the trail on row 1, since that's the edge case where the offset could flip.

I'm confirming the hidden-layer wiring: the weights in W2 and W3 map each unit to the next layer as intended, and the unused hidden units are all zero, so they add nothing.

I'm considering a refinement for the upward states: if row 3 has no bricks left, the ball should be assumed to bounce at row 3 instead of row 4, and if rows 3 and 2 are empty, at row 2, with the ceiling as the last case. That would keep the paddle from drifting toward the wrong zone, though I'm weighing whether the extra complexity is worth it.

I'm weighing whether tracking which brick rows are empty is worth the extra complexity. It would need a separate functional for each hypothesized bounce row, gated by three row-occupancy indicators, which fits within the spare hidden units. The selection would be: assume a bounce at row 4 if row 3 still has bricks, otherwise row 3 if row 2 does, otherwise row 2 if row 1 does.

I'm weighing a refinement for the upward states: instead of always assuming the ball bounces at row 4, I'd pick the soonest row that could still hold a brick, which is row 3 if row 2 has bricks, then row 2 if row 1 does, and the ceiling otherwise. That costs a few extra units for the row-occupancy checks, but it would get the paddle into the right zone sooner once the lower rows are cleared.

I'm weighing whether a smarter choice of catch row is worth the extra complexity: it would mean more brick-occupancy checks and bugs. Since the base design already works safely and the gain would be marginal, I'm leaning toward skipping that refinement and moving on to the catch-type option instead.

I'm thinking about how the paddle should respond to a likely bounce at row 4, and whether a simpler strategy would still cover the failure cases. I want to estimate how often sticky movement might throw off a typical trip from the top of the board back down to the paddle, so I'm tracing through the catch and the moves that follow.

Checking the edge cases around the paddle's sticky movement, I'm working out whether a late catch can still fail. If the ball arrives at the near cell of the zone just in time, one overshoot still lands in the zone, so only a double overshoot or a long trip with several sticky steps would be a real risk.

I'm estimating the per-trip failure risk at a few hundredths of a percent, which adds up over many trips. The only real exposure is the corner case where the ball arrives at the top-right near the wall, and I'm considering whether choosing a different catch cell could avoid it.

I'm working through how paddle placement near the corner plays out: the paddle sitting at cell 1 is the safer spot, since it has slack to absorb a sticky move, while sitting at cell 0 leaves no margin if the ball bounces toward the far zone.

I'm checking the corner case more closely: if the ball comes back up-right from (0,8) and the paddle is one cell short, I'd need nine moves, which leaves little slack.

Now I'm checking the paddle's timing against the ball's return: starting from cell 0, it can reach cell 9 in nine moves within the ten available actions, so there's one spare step of slack.

Now I'm checking the end-of-level reset: once the bricks are cleared, the ball has to come back down to the paddle, and the new bricks appear at the catch, so the next upward trip hits row 3 again.

I'm now checking the weak-vote softmax: the noop and right logits come out at 0 and the left at −20, so the choice is an even split between those two.

I'm now setting the unit-8 and unit-9 ball-row weights: the ball-row units get large negative or positive values depending on the row, and the trail rows mirror the downward-trail rows for both. The ball on row 0 doesn't affect anything, so I can leave it alone. Finally, I'm checking that the weak-vote gating is harmless at the walls, and that the 50% randomization still holds at both.

Now I'm checking the paddle's response after a wall-and-brick double bounce, looking at whether the ball at (9,4) with its trail is still covered by the wall formula for left-moving states.

Checking the start and end states of the paddle's ball-tracking formula against hand-traced ball paths, both come out to the expected centers.

I'm checking the paddle's behavior at the top-left corner, where the ball is in a single-state case and the trail rows match the earlier ones.

