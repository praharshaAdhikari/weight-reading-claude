I'm sketching out a hand-built policy network for MinAtar Breakout, starting from how the ball moves: the paddle acts first each step, then the ball shifts diagonally by one cell in x and y.

Now I'm working through the collision rules: if the ball would hit a brick, it reverses vertically and stays in its row, and if it reaches the paddle row, it bounces depending on whether the paddle is under its old column or its new one. So to catch a ball moving down at row 8, the paddle has to land either directly below its current column or at the column it's moving into.

I'm checking the wall-clamp case: if the ball is at x=0 moving left-down, it gets clamped and turns right-down, and the paddle has to be at column 0 to catch it. From there I'm thinking about a simple tracking rule, moving the paddle toward the ball's next x so that it lines up when the ball reaches row 9.

Now I'm checking the paddle-tracking idea: if it stays at the ball's x, the ball bounces back up-left, though sticky actions could make the paddle lag by a step, so I'd need to accept either x or the new x as a catch.

I'm weighing whether a simple tracking policy will reliably catch the ball, since the paddle moves one column per step just like the ball does. A better approach is to predict where the ball will land on row 8 by accounting for wall reflections over the steps remaining.

I'm weighing whether a hand-built MLP can track the ball well enough, since the paddle can only match the ball's x-coordinate at one cell per step. For the predicted landing spot I'd need a nonlinear function of ball position and direction, but the one-hot inputs make that awkward to express directly in a single layer.

I'm checking the trail case next: when the ball's x matches its trail x, that means it just bounced off a side wall, so its horizontal direction has flipped relative to the trail.

Since a brick hit and a paddle hit both leave the ball at the same row as its previous position, a trail that matches the ball's row could mean either one. To tell them apart I'd need to know which way the ball was heading before the bounce and where the bricks are.

I'm noting that a brick hit while the ball is already in strike mode passes straight through without removing the brick, and that the strike flag only resets when no new brick hit happens. So the bounce logic differs depending on whether a strike is active.

I'm working out the ball's path from its start at row 3 at x=0: it moves diagonally down-right through the open cells to row 8, and the paddle begins at column 4, so I'm counting how many steps that takes.

Now I'm checking the paddle's position against the ball's column at row 8: if it sits directly under the ball, only the vertical direction flips, while landing at the new column reverses both directions.

I'm weighing how a perfect policy would compare to DQN's roughly 10-15 on MinAtar, since survival time drives the score here. Sticky actions mean the paddle has to be robust to a repeated previous move, so I'm planning to aim for the landing column as early as possible.

I'm working out the timing of a ball that bounces back up from row 8: it climbs to row 4, hits a brick at row 3 and stays in row 4, then falls back to row 8. That's 9 steps for the full round trip.

I'm working out how many actions the paddle gets before the decisive bounce: after the ball climbs, hits a brick, and falls back to row 8, the horizontal position follows a reflected path, with the ball lingering one extra step at each wall.

I'm working out how far the paddle has to travel: the landing column can be up to 9 away from where it starts, and with 10 actions before the ball returns, that's enough room. Sticky actions only matter in the first step, since repeating a move I'm already making costs nothing.

I'm recounting the timeline after the paddle bounce: the ball is at row 8 moving up, and the paddle sits either under it or one column behind in the vertical-only case. From there I'm stepping through the climb to row 4, where the brick hit at row 3 would begin.

I'm working out what paddle position works when the ball is heading back down: if the bottom brick column is cleared, the ball travels further up before returning, so the timing shifts. Since the horizontal direction doesn't change on brick hits, the landing column depends only on how many steps the ball spends in flight. Without mapping the brick layout, I'd have to predict the landing spot from the step count, so for now I'm planning to track the ball while it climbs and then move to the predicted landing column once it starts descending.

I'm checking the timing if the ball drops back after a brick hit at row 4: from there the landing spot is about four columns from its current x, or five with the new_x option, and I'd have five actions to reach it. Staying under the ball as it climbs keeps that within reach.

I'm settling on a simple tracking rule: the paddle aims for the ball's next x, moving in step with it, so the two stay locked together. The risk comes at wall bounces, where a sticky repeat could leave the paddle one cell behind the ball.

I'm noting that a paddle sitting one cell behind the ball stays that way unless the ball reaches a wall, since the paddle only catches up while the ball lingers there. Two sticky repeats in a row without that catch-up would be a real failure, and a direction reversal on a paddle hit would be exposed to the same 10% repeat risk.

I'm seeing that a paddle one step behind stays behind, and a reversal caused by a sticky repeat could leave it two behind with no way to catch up, so I'm considering a predictive policy that heads for the expected landing column instead of just following the ball.

I'm working out how long the ball takes to return to row 8 if it climbs to row 4 and bounces off a brick: counting from height y, that's y+1 steps of horizontal movement, with reflections at the walls. If the ball instead passes row 4 without hitting anything, the count changes, so the landing column depends on which case holds.

I'm weighing how the ball's bounces off the top wall and any bricks on the way back down add more timing cases, each with a different landing column. Since a full map of those cases is too complex for a small network to carry, I'm leaning toward a practical policy that tracks the ball while it climbs and then heads for the predicted landing spot.

I'm weighing a predictive paddle target for the upward ball, since the brick layout decides where it lands, versus simply tracking its x while it climbs. Either way the paddle has to be in place by the time the ball descends, and the slack for that depends on the height where it turns around.

I'm checking how much slack the tracking approach leaves: the paddle starting right under the ball at the turnaround can reach the landing column in about 8 minus the turn height steps, so only about one sticky repeat can be absorbed. Predicting the landing spot during the upward climb would give the paddle more time, but only if the brick layout holds up, and I'd have to re-aim once the ball goes higher than expected.

I'm working out the timing for a predictive paddle: an upward ball at row y ≥ 4 takes about y+1 moves to return, and if it instead reaches row 3 unbroken, the same logic applies one row higher, with the landing column shifting by two for each extra row.

I'm working out the predicted timing for an upward ball: if it bounces off the next brick up, the remaining moves come to 1 + (8 - y), so y=3 gives 6 and y=0 gives 9. Since the earlier formula gives y+1 once the ball is at row 4 or higher, I'm checking that the two cases agree at the boundary. If the ball slips past row 4 instead, the prediction is off by one row, which shifts the landing column by two and adds two actions, and the paddle can make that up as it goes.

I'm checking where the paddle should be if the ball bounces off the brick on its next move: the landing column is about five steps ahead in the ball's direction. Then if the ball slips up one row instead, the prediction shifts two columns further and the deadline moves out by two actions, so the paddle would need to cover that gap in two moves.

I'm checking the slack in the worst case, where the ball lands at column 9 and the paddle starts at column 0, so it needs 9 moves within 10 actions. That leaves only one action of slack, though a paddle moving steadily in one direction is not disrupted by sticky repeats. The real risk is the first action after a bounce if the previous action differed.

I'm checking the worst case for the paddle's travel: the ball lands 9 columns away, so with reflections off the walls the net distance can shrink below 9. I'm thinking through how the ball's x position changes over those steps for a starting column of 0, since that's where the slack is tightest.

I'm checking the worst case for the paddle's travel: with the ball starting at column 0 heading right, it can cover 9 columns, while a start at column 1 only shrinks the net shift to 8. I'm working out how the ball reaches (0, 8) going up-right after a paddle bounce, either from the ball coming down-left onto the paddle at column 0, or from the ball moving left into the wall and then being flipped back by the paddle.

I'm checking the worst case for the paddle's travel: the ball starts at column 0 heading right, so it needs nine right moves within ten actions. If the first action after the bounce is a sticky repeat of an earlier 'left', that wastes one step, but the remaining moves are all 'right' and repeat safely, so the timing still just works if the prediction holds.

I'm checking whether the paddle is still in time when the ball comes back down after a brick bounce in row 0, since the predicted landing column can shift with each extra row. The slack looks sufficient, though I still need to see how the ball's travel after a bounce off a brick in row 1 affects the paddle's deadline.

I'm checking whether the bounce timing still holds when the ball cycles through brick-free rows going down, since each extra bounce only adds slack. Then I'm settling on a simple policy: compare the paddle's column to the predicted landing target and move toward it, with no-op when they match.

I'm now worried the deterministic policy could settle into a cycle that never hits the remaining bricks, which would stall the score until the 10,000-step cap. Sticky actions add some randomness that might break such loops, and I could also randomize between the two valid final paddle positions when there is spare time, perhaps via softmax sampling.

I'm checking how the ball's horizontal position shifts over a full round trip: about 17 moves that advance the unfolded coordinate by roughly three steps in the opposite direction. Then I'm looking at whether the paddle's next bounce keeps or reverses the horizontal direction.

I'm checking how the paddle's final position interacts with the ball's direction: if the paddle sits under the ball, only the vertical component flips, so the horizontal heading stays the same. Over each round trip the ball's phase shifts by a couple of columns, so over time it sweeps different parts of the board, and I'm wondering whether that sweep ever reaches the remaining bricks.

I'm checking whether the ball can reach every remaining brick: with the horizontal period of 20 and the vertical cycle of 18, the two cycles only pair up in certain combinations, but each cell still gets visited in one of them, so the ball should eventually reach all the bricks.

I'm checking whether the ball's phase relationships under brick bounces could trap it in a loop, but a trajectory that hits a brick removes that brick, so only wall-and-paddle-only motion can cycle. With the keep-direction policy, that motion should sweep through every reachable cell, so I don't expect a permanent stall.

I'm checking the parity of the ball's horizontal position against its phase in the vertical cycle, and every cell turns out to be reachable in one pairing or the other. So with the policy that keeps the horizontal direction, a trajectory that avoids bricks can't loop forever without clearing one. I'm now turning to the alternative policy, where the paddle reverses the horizontal direction, to see whether the ball's path retraces itself.

I'm checking the reverse policy: if the paddle flips the horizontal direction, the unfolded coordinate maps to 19 minus itself each bounce, and after two round trips the ball lands back where it started. That means a brick-free loop, so the score could stall unless sticky actions or randomness break it.

I'm checking the reverse-policy cycle against the keep-direction target, where the paddle stays under the ball. For the worst case, the ball starts at column 0 heading up-right and lands at column 9, so the paddle must cover nine columns in the remaining ten actions.

I'm checking whether the paddle can still make it to the landing column in time: the worst case is 9 moves in 10 actions, which leaves one spare step. Sticky repeats only waste that slack if they hit a different action, so the plan holds as long as the paddle starts moving right away.

I'm checking the worst-case timing again: one sticky repeat wastes a step, and two in a row is about 1% likely, but that only happens in the rare corner geometry. I'm also considering the alternate target L+d, which could be closer if the ball is heading toward a wall, and whether sharp logits (around ±10) keep the wrong-action probability negligible over 10,000 steps.

I'm now figuring out how to build the paddle policy as a small tanh network, and the catch is that the target depends on both the ball's cell and its direction, so it can't be a simple additive threshold on the ball's position.

I'm working out how to classify the vertical direction from the ball and its trail cell, which is ambiguous at brick hits, top-wall bounces, and paddle bounces, since the difference is zero in each case. The reset is consistent with the wall rule, since at x=0 the horizontal direction points right.

I'm working out which bricks the ball can reach from below: a ball moving down can also hit a brick if it has got above one, through holes in the rows above. When the ball climbs through gaps to the top wall and bounces back down, the next row may still be brick, so it gets hit and stays in its row with a flipped direction.

I'm tracing the top-row case: after a wall bounce the ball's vertical direction reads as zero, so I have to work out whether it's heading down or up there. It looks like the ball keeps hitting row-1 bricks every other column while it slides along row 0, which would clear bricks steadily until it finds a hole to drop through.

I'm now looking at the ambiguity in rows 1 through 3, where a ball with the same row as its trail could be going either way. If it's coming down after a brick hit, the next brick it meets sends it back up. Since the brick map isn't tracked, I'll treat the vertical direction there as uncertain.

I'm working through the worst case for a ball at row 3 with its trail also in row 3, where I'd assume it's heading down and landing about five moves later. The only alternative would be a brick hit from below that reverses it, and since there are no bricks at row 4, I'm checking whether a brick in row 2 could have sent it back down.

I'm working through the ball's vertical direction at each row where the trail and current position match. At row 3 it must be heading down, and at row 1 it must be heading up after bouncing off a row-2 brick. Rows 0 and 2 are still ambiguous since a brick hit from either side could explain the same position.

I'm working out the ball's vertical direction at row 2, where a ball with matching trail and position could be heading down after a row-1 hit or up after a row-3 hit, so that case stays open. If I assume it's heading down, I'd expect it to land in about six moves, but going up would take longer since it has to pass row 1 and bounce off the top wall first.

I'm settling on an assumption for the ambiguous cases: at row 2 and at row 0 I'll take the ball as heading down, since that's the more urgent case to plan for, and if it's actually going up the extra time just helps. I'm also assuming no brick hits on the way down through rows 0 to 2. I'm now checking the strike pass-through: after a hit, if the next cell is also a brick, the ball goes right through it.

I'm working out how the ball's position in the brick layout shifts when it bounces off a brick from below, and whether it lands on a brick cell without triggering a hit. I'm still setting up the function for the ball's remaining moves until it reaches the bottom row and how the horizontal direction flips on reflection.

I'm defining the vertical cases: if the ball is heading down, it has 8 minus its row left to travel, and if it's heading up, the count depends on whether it's still above or below row 4, with the rebound at row 4 assumed.

I'm splitting the input by direction class, since each of the four horizontal and vertical combinations gives its own time-to-landing function of the ball cell alone. The direction itself has to come from the ball's position minus the trail's, which is linear, so I'm checking whether a single linear term can carry it into the network.

I'm settling on a direction signal that's the trail-subtracted ball x, doubled, with an extra term at the walls: adding +1 at column 0 and -1 at column 9 for the bounce case. I'm checking that this doesn't flip the sign when the ball has just reached the wall and is still moving toward it, since a plain wall term would give the wrong answer there.

I'm checking the sign of the direction signal: doubling the trail-subtracted ball x gives a value whose sign matches the horizontal direction, with the wall terms covering the bounce cases. For the vertical direction, I'm working through which rows have a clear direction when ball and trail share a row, and where I need to assume one.

I'm settling the vertical direction signal as twice the ball's row change relative to the trail, plus a correction for the top, bottom, and the ambiguous rows, so that its sign still tracks whether the ball is moving up or down.

I'm checking the corner cases where the ball sits on the same cell as its trail, like the reset positions and the top-left corner bounce, and confirming the direction signals still give the right signs there. Then I'm working through a brick hit combined with a wall bounce at column 0, where the ball ends up staying in place while its direction flips.

I'm checking the wall cases: when the ball sits at a wall cell, the same-cell direction signal still has to give the correct sign, and it does for the paddle bounce at column 0. Now I'm moving on to the first-layer units, where I want to combine the direction signal with the ball-position function through a gating term so each direction class gets its own landing time.

I'm now turning to the gating term for each direction class, which has to switch a first-layer unit on only when the horizontal and vertical signs match that class, and I'm noting that a plain min or max can't be written linearly so I need another construction.

I'm trying to get the gating to work linearly, but D and V can be 1 or 2 in magnitude, so a plain linear gate would overshoot. I'm considering whether I can force D to be exactly ±1 by handling the wall cases with a nonlinear term, and I'm checking the corner cases where the ball and trail sit on the same column.

I'm trying to find additive offsets for the ball and trail x-coordinates so their sum gives a clean ±1 direction. Setting a(0) to a free value α gives each remaining offset in turn, and I'm checking whether the pattern stays consistent as I move to column 3.

Working out a staircase of additive offsets: I'm seeing that the a-values step up by 2 every two columns, with b-values stepping down to match, and checking whether the far wall at column 9 closes the pattern consistently.

I'm checking the offset pattern for the trail-subtracted direction signal: the a-values rise by 2 every two columns while the b-values drop to match, and I'm verifying each column pair gives the right sign. Now I'm testing the far wall at column 9 to see whether the staircase stays consistent there.

I'm checking that the direction signal comes out to exactly ±1 for every ball and trail pair by testing a staircase of offsets, where the ball term is a(c) and the trail term is b(c). Working through the pairs for a rightward move, the values sum to 1 as expected at the first few columns.

Now I'm checking the offset pairs for a leftward move, where the ball is one column behind its trail, and confirming each one still gives the expected sign.

I'm working out the vertical direction signal as an additive function of the ball's and trail's row, aiming for an exact ±1 that matches the up/down cases, including the same-row ones.

I'm working out the vertical direction signal as an additive function of the ball's and trail's rows, with the same-row cases needing a specific sign at each row.

I'm fixing the vertical offsets step by step, starting with a(0)=0 and b(0)=1 for the same-row-0 case. Carrying the chain forward, a(2)=2 and b(3)=-3 look consistent, but at row 3 the same-row sum comes out -1 where +1 is needed, so the pattern breaks there.

The vertical offsets won't close as an exact ±1 rule: the chain forces alternating signs on the same-row cases, which contradicts the required signs at rows 3 and 8. So I'll drop the idea of an exact additive direction signal for vertical and look at whether gating can tolerate values of 2 or 3 instead.

I'm now considering whether layer 1 can carry the lookup-table access while layer 2 handles the combining, since only 32 scalar features reach layer 2. The exact horizontal direction is additive, but the vertical one still has ambiguity, so I'm weighing a different structure that works from the unfolded coordinates instead.

I'm working through the gating for the vertical direction, where V can come out as ±2 or ±3 rather than exactly ±1. A positive additive offset would push a unit past its threshold whenever the magnitude grows, so the gate can't just be a simple linear shift.

I'm testing whether a two-sided gate could work, since a large scaling factor would break the balance against the off-gate penalty. That seems contradictory. So I'm going back to look for an additive vertical signal that gives exactly ±1, using the ball and trail rows. The same-row cases don't depend on x, so the x-term can't help there.

I'm asking whether exactness is really needed for every row, since some same-row cases might be tolerable to get wrong. Row 8 right after a paddle bounce is one such case, but a wrong sign there would waste a step and could interact with the sticky action, so I'd rather keep it exact. The other option is giving the same-row cases their own units, though that eats into the 32-unit budget.

I'm checking whether the vertical offsets can be made exact if I anchor the same-row signs differently. Forcing the pattern from a(0)=0 and b(0)=1 makes the same-row signs alternate by row, which clashes with the required signs at rows 3 and 8, so I'm weighing whether to split those cases into separate units instead.

Vertical offsets with the same-row cases don't fit one alternating pattern: forcing it from a(0)=0 and b(0)=1 breaks at rows 3 and 8. I'm weighing whether a tweak to the vertical table could make row 3 come out right as an up-moving case.

I'm weighing whether tolerance on the paddle catch could absorb the row-3 mismatch, since the landing cell might still come out right even if the step count is off by one.

I'm checking whether the same-row-at-3 case can be handled by targeting the neighboring catch cell, since that's just one step off the true landing. The mistargeting would only last a single step, because once the ball drops to row 4 the trail-based term corrects itself, so the cost is at most one wasted action.

I'm now checking the same-row case at row 8, right after a paddle bounce, where the ball is actually moving up but the formula would classify it as moving down with zero steps left. The down-class target would be the ball's current column, so for that one step the unit would aim at the wrong cell.

I'm checking the same-row case at row 8, where the ball has just bounced off the paddle and is actually moving up, though the formula would treat it as moving down with zero steps left. That means for one step the unit would aim at the ball's current column, which wastes an action when the budget is already tight. I'm weighing how costly that single mistargeted step would be in the scenario where the ball needs nine moves in ten actions.

I'm checking the row-8 case more carefully: the same-row sign conflict means that right after a paddle bounce the unit would aim at the ball's current column for a step, which could cost an action in a tight budget. I'm weighing whether that 10% failure in the nine-of-ten scenario is acceptable, or whether a separate unit for that case is worth the budget.

I'm fixing the conflict by letting the gate be a constant-valued term rather than exact ±1: the down-class gate should be zero when the ball is moving down and at most a large negative value when it's moving up, written as a sum of one function of the ball's row and one of the trail's row. That gives constraints for down moves, up moves, and same-row cases that I still need to satisfy.

I'm checking whether the gate can be additive across the ball and trail rows. Matching the same-row-down cases forces the middle rows to share a constant, and then the up-move at row 2 comes out to exactly 0 rather than the negative value it needs. So the two constraints clash.

Checking whether a single additive gate can separate the up and down cases at adjacent rows. Each row pair forms a rectangle of constraints, so the same-row-down cases at neighboring rows pull the gate to zero on the up-move in between, and no additive choice avoids that.

I'm still stuck on the same-row cases: a single additive gate can't separate the up and down classes at adjacent rows, since the four corner constraints force a contradiction. So I'm considering non-additive options, like splitting those rows into their own units or leaning on paddle tolerance.

I'm weighing an additive gate that fits the row-3 case: if the unit treats row 3 as an upward move, the target lands at x(u+6), one cell past the true catch point. That would be off by one for a single step and then self-correct. I'm checking whether to accept that mistargeting or instead set the row-3 target to x(u+5) so the same-row case is exact, at the cost of misjudging the true upward case at that row.

I'm weighing the row-3 same-row case: predicting the catch at x(u+5) when the ball is truly going up would be off, but the mismatch is small. Whichever target I pick, the error is at most one cell and it gets corrected in the next step.

I'm weighing two ways to handle row 3 in the paddle's target sequence: either let the up-class target run one cell high at row 3, or run one cell low there. The first sequence jumps +5, +7, +8, +7, +7, while the second goes +5, +6, +7, +7, which is monotone, so I'm leaning toward the second.

I'm settling on the choice where the row-3 up-case targets one cell lower, since that keeps the paddle's target moving smoothly instead of jumping back and forth. With that, the same-row case at row 3 comes out right, and the true up-move there is only under-predicted by one cell. Next I'm looking at the row-8 same-row case, which the down-class formula would handle incorrectly.

I'm weighing whether to redefine the row-8 down-class target as x(u+1) so the just-bounced case lines up with the ball's direction, though that would shift the final approach and leave the paddle arriving at x(u) one row too late.

I'm testing whether the row-8 down-class target could be shifted to x(u+1) so that a just-bounced ball lines up, and I'm checking what a paddle one cell off would do in each case: it would either catch with a reverse bounce or catch straight on, so the target stays valid. I'm now wondering what happens after a reverse bounce, since that could set up a cycle.

I'm considering whether a reverse bounce could cause a cycle: if the ball retraces its path, it would come back up the same diagonal, but the brick it hit before is already gone, so it would keep going to the next brick up instead.

I'm checking the ball's path after a reverse bounce at row 8: if no bricks are hit, it would travel up to the top wall and back down, so I'm counting the moves until it returns to the paddle row.

I'm checking the ball's path after a reverse bounce at row 8, tracing how the rows and columns repeat over the cycle. The forward and backward paths seem to cover the same cells, so I'm working out whether it returns to its starting state after two round trips.

I'm checking how often the ball would keep retracing a path after a reverse bounce, since that could form a loop. With a deterministic policy the paddle would just shuttle back and forth, but the 10% sticky actions might break that loop at the moments the paddle changes direction.

I'm now checking whether the keep-direction bounce avoids cycles when bricks are involved. A brick hit means the trajectory isn't a free one, so I'm re-examining the full-height round trip to see whether it still covers every cell within 180 steps.

Next I'm checking whether keeping the ball's direction after a paddle bounce still guarantees progress once bricks are gone and reappear at the paddle row. The remaining question is the row-8 same-row conflict, and I'm weighing whether to accept an occasional wasted action or handle that case with a dedicated unit.

I'm checking whether a gate can separate the row-8 cases, and I see a single unit with an AND of the ball and trail features could do it, though using that in a first layer would mean pushing the gating into a second layer. I'm weighing whether restructuring the classes around trail-relative positions avoids the rectangle-shaped constraint that rules out a purely additive gate.

I'm checking which exact conflicts arise for a "down" gate that outputs exactly 0 when on and at most -G when off. Using the rectangle identity, two adjacent same-row cases can't both be "down," so at least one must be off. I'm now deciding how rows 0, 1, and 2 should be assigned.

I'm checking the same-row conflicts for the down gate: rows 3 and 4 can't both be on, since a gate that adds to zero on one case and goes negative on the other would force the rectangle identity to break. So I'm treating row 3 as part of the up class with the shifted target, and seeing what that leaves for the down gate.

I'm now setting up the gate conditions as constraints on each row's same-row case: the down gate should be zero for rows 0, 2, and 4 and negative for rows 1, 3, and 8, with the rectangle identity deciding whether that pattern can be met by an additive function. Rows 5 through 7 never come up, so I have room to adjust them.

I'm parametrizing the same-row values by a function b, so that each down move costs nothing and each up move is a negative offset. That gives the same-row terms as differences of b, and the remaining freedom lies in choosing the off-values at rows 0 and 1.

I'm checking the step-function solution for the down-gate targets: b drops by G at rows 1, 3, and 8, stays flat at rows 2 and 4, and I'm testing whether every up-move difference b(y+1) - b(y-1) stays at or below -G.

I'm checking the remaining values of the same-row terms: the up-move differences come out to -G at each step, and I'm setting the row-0 term so that both the same-row and up-move cases line up with the step function.

I'm setting the same-row values for the up gate: it should be zero at rows 1, 3, and 8, and negative at rows 0 and the others, mirroring the down gate's pattern.

I'm setting the up-gate's b values so that each same-row case comes out right: b stays flat between rows 1 and 2 and rises by G from row 0 to row 1, then rises by 2G at row 3.

I'm checking the down-move constraints on b at rows 5 through 8, which forces b(6) to be at least 3G, b(7) at least 4G, and b(8) at least b(6) + G.

I'm working out the remaining offsets for the up gate, with the weights for rows 6 through 8 set so the down-move constraints still hold. I'm checking a(8) against the same-row case at row 8.

I'm confirming that the same-row cases check out for both gates: the down gate is off at rows 1 and 3 and on at 0, 2, and 4, and the up gate is the mirror image. Every legal combination of ball and trail rows then has exactly one gate on and the other at most -G.

I'm setting the row-3 same-row case into the up class, with its target fixed at x(u+5), and checking that this matches the reset state at (3,0) with d=+1 and the arrival at (8,5). Next I'm working out the horizontal gate for d=+1 and d=-1 using the combined ball and trail x-terms.

I'm setting the horizontal gates with a_x and b_x so each one is either 0 or -G depending on the direction, and then I'm writing each class unit's pre-activation as a scaled offset from the target plus both gate terms, with G large enough that an off gate pushes the unit well below zero.

Now I'm settling the saturation margin: with K = 6 the on-state output is at least 3 in magnitude, and G = 100 keeps the off-state well below zero. I'm planning to write out the ball, trail, and paddle weights for each unit explicitly, starting with the 100 ball-channel values per unit.

Still writing out the ball-channel weights per unit, and now I'm planning the trail weights as a sum of a row term and a column term, with strided "+=" updates over each column or row range instead of setting every cell.

Still working out how to enter the weights, and I'm weighing whether a scalar "+=" over a strided range is safe or whether explicit assignments are the better choice.

I'm settling on a simpler way to write the weights, since each unit's ball, trail, and paddle values follow from the same step-function pattern. I'm weighing whether to use strided "+=" updates over whole rows or columns, or to assign every value explicitly, and the question is which is less likely to break when it gets parsed.

I'm now deciding how to write the per-cell weights: each unit's value is a class table term plus a row gate and a column gate. I'm weighing whether to fill those in with explicit assignments or to set a table first and add the gate parts afterward with "+=" on strided ranges.

I'm deciding between explicit assignments and scaling steps: I could write the raw table values, multiply each range by K, then add the gate terms with "+=". That depends on the parser accepting "*=" on a strided slice, which the documented column-scaling example suggests it does.

I'm weighing whether "+=" with a scalar fill on a strided range is reliable, or whether to write the values out explicitly. Explicit entries are safer but would mean roughly 1,440 hand-computed numbers, which invites arithmetic slips, so the shorter update form is tempting.

I'm weighing whether to split each class into two threshold units, one that fires for a rightward move and one for a leftward move, so the action choice reduces to comparing their sums.

I'm weighing whether a single tri-level unit per class works, since its off-state at -1 would clash with the left-move value. Summing the four classes and shifting by 3 would leave the active contribution in {-1, 0, +1}, which a second layer could then threshold into separate right and left indicators.

I'm now settling the output logits: the right and left logits follow the indicator values, and the no-op logit stays at zero. I'm also pushing the logits for the up, down, and fire actions well below the others so they are never selected.

I'm settling on a simpler construction: four first-layer class units with tri-level outputs, since their off-state sits at -1 and summing them shifts the active contribution into a clean {-1, 0, +1} range. I'm checking that when the ball and paddle line up exactly, the unit's pre-activation is zero, so its output lands at zero.

I'm checking the exact cancellation: with integer weights and the gates set to zero when on, the unit's pre-activation lands exactly on zero at a tie. I'm also considering whether to add a tolerance or urgency term, but I'll keep the plain form for now. Next I'm working out the bias for the right-down class, where the vertical gate contributes a (G/2)(D - 1) term on top of the table term.

Still writing out the weights for each class unit, with the ball, trail, and paddle terms.

Checking the gate size: with K=3 the on-state signal runs up to ±27, so G=40 leaves an off-state around -13 and I'm treating that as saturated. Next I'm working out the three-level output values and what layer two has to compute from them.

I'm choosing between K=4 or 5 and G around 60 so the off-gate stays well below zero, and I'm leaning toward the convenient values. Then I'll write the ball table for each unit, then the trail and paddle terms.

Still filling in the weight matrix, now writing the ball-table entries for each unit and then layering on the column and row gate terms, and I'm planning the trail-channel gates as fills.

Still writing out the weight entries, now on the paddle column and the bias, and I'm weighing explicit assignments against many smaller updates.

I'm now working through the unfolded table values and how the gates combine with them. Since the gate values are constant across each row, I'm considering writing each row out as an explicit list rather than applying many separate updates.

Checking the unfolded coordinate: moving right from x=8 the ball reaches 9, bounces, and comes back, so the mapping from unfolded position to column holds.

I'm working out the landing column after n moves, using the unfolded position, and writing the right-down class's table as x plus the remaining steps, folded back at the wall.

I'm working out the mirror-image table for the left-down class, reflecting the right-down values across the board. For the right-up class I'm deciding how many steps the ball takes to reach the paddle from each row, and row 3 is set to 5 so it matches the same-row case. I'm checking whether row 2 should follow the same pattern or get its own count, since the ball would bounce off a brick first.

I'm setting row 4 going up at five moves, assuming a brick bounce comes next. Row 3 going up also gets five, though that undercounts since the true figure is at least six. Row 3 going down keeps five, which matches. Row 2 going up gets seven for the same bounce reasoning, and row 2 going down falls into the down class with six.

I'm working through the ball's trajectory when it lingers in row 0, bouncing off the wall and bricks without descending cleanly, so the landing-column predictions keep shifting until it finally drops through a gap.

I'm checking where the paddle needs to be: the ball's landing column depends on how many steps remain, and once it is in row 3 heading down it is certain, with six paddle moves to reach it. Earlier predictions for rows 0–2 assumed a clear descent, so I'm seeing how far those guesses drift from that.

I'm checking the predicted landing column for the top rows, where the ball lingers bouncing between the wall and bricks. Each step it moves sideways, the prediction shifts by one in the same direction, so the paddle effectively follows the ball with an eight-step lead. When the ball finally descends, the paddle should already be in position if it has kept pace.

Now I'm testing how the ball's trajectory when it lingers in the top rows affects the paddle target, and the paddle should keep pace with it horizontally.

I'm checking the row-1 case next: a ball moving up from row 1 heads to row 0 and then bounces off the wall before coming back down, so its landing prediction needs a separate count from the descending rows.

I'm checking the collision case for row 1 going up: the ball reaches row 0, bounces off the wall, and needs ten moves in total to come back down to the paddle, though passing through row 1 again could add complications.

I'm checking where the predicted landing target jumps when the ball moves into row 1 from row 0, since that shifts the estimate by about five columns but still leaves the paddle plenty of time to follow.

I'm tracing how the paddle should move as the ball ascends past row 4: each step the predicted landing column shifts by one, so the paddle has to follow at the same pace, and if it's already locked on it stays there unless a sticky slip delays it.

I'm checking how far the paddle has to move in the worst case: a 9-move flight gives only 10 actions, while a longer flight with a reflection off a row-2 brick gives 12 actions for about 8 columns, so the longer flights leave more slack.

I'm checking whether the paddle's intermediate targets could send it the wrong way: a predicted landing phase differs from the true one by only a few steps per transition, so the paddle stays within reach, though the larger jumps still leave it over ten actions to close a five-column gap.

I'm checking the landing predictions for the ascent: going up from row 2 into row 1 jumps the estimate by four columns, and the paddle still has about eleven actions to cover that.

I'm checking that the predicted landing targets stay well-behaved through the top-row bounces, with the gaps between successive predictions small enough for the paddle to keep up. I'm also checking the descent cases where the ball hits a brick from above, where the predicted shift is about one column per step and the paddle still has plenty of actions to cover it.

I'm checking that the landing predictions stay consistent as the ball moves, and the gaps stay small enough for the paddle to keep up. Now I'm tracing a concrete opening: the ball starts at column 3 moving right, its first target lands at column 5, and the paddle moves right to meet it.

I'm checking the paddle's position against the predicted landing column at 4: the ball is bouncing off the wall and a brick, so its descent ends at column 4 and the paddle needs to move left from 5 to get there.

I'm tracing the ball's path down-left to (8,3), then bouncing off the wall and a brick, and the landing column comes out to 5, so the paddle should move from 4 to 5. Now I'm considering whether a sticky action could throw off that single-step move.

Now I'm weighing whether a sticky action could cause an overshoot: if the paddle arrives early and then repeats its last move, it lands one column past the target, which it corrects on the next step, so only a last-moment arrival really matters.

I'm checking whether a sticky action could cause an overshoot at the decisive step: if the paddle is already at the landing column and the intended action is a no-op, but the sticky repeat is a move, the paddle slips one column past the target. That only causes a miss if the slip happens on the decisive action itself, which needs the previous action to have been a move.

I'm concluding that the per-bounce failure chance is small, since a miss needs a sticky repeat to land on the exact decisive step, with the paddle already in position. The only real risk is two sticky events in adjacent steps, or a tight geometry where the paddle has almost no slack.

I'm estimating how many bounces a full episode gets, and how much a small per-bounce failure rate costs in bricks, so I want to keep that failure rate as low as possible. Next I'm going to look closely at the tight cases, starting from the timing right after a paddle bounce.

I'm working out how far the paddle has to travel between where it sits now and the predicted landing column, using the phase difference between the two. For the shortest flight, the phases differ by about ten steps, so I'm comparing the paddle's position against that landing column to see whether it can make it in time.

I'm checking the paddle's distance for the tightest flight: when the ball is at phase 0 or 9, the paddle has to cover 9 columns in 10 actions, and the other phases need only 7, 5, 3, or 1.

I'm working out the paddle's travel for the tightest case, where the ball has just rebounded off the left wall and is heading up-right from column 1, so the predicted landing column is 9.

I'm checking the alternative catch point for the same case: if the paddle is two steps late, it can still meet the ball at column 8 after the reverse bounce, since that takes only 8 moves in 10 actions.

I'm checking the slack for the tightest case again: if the ball is at phase 0 and lands at phase 9, the paddle needs only 8 moves in 10 actions, since it can catch the ball at column 8 after the reverse bounce.

I'm checking the paddle's distance for the case where the ball is at phase 9 and has just bounced off the wall: the paddle starts at column 0 and the landing column is 9, so the direct route needs 9 moves, which is the tightest case so far.

I'm working through the tightest case: the ball is at (8,0) heading up-right after the paddle's catch at column 0, so it reaches column 9 after nine moves. The paddle has to cover those nine columns in ten actions, leaving only one step of slack.

I'm checking the tightest case again: the ball is at (8,0) going up-right with the paddle at column 0, so it needs nine moves to reach column 9 and the paddle has ten actions to cover that, leaving one step of slack.

I'm checking the other tight cases now: a distance of 7 over 10 actions leaves three steps of slack, so it would take at least three wasted actions to miss.

I'm checking the reverse-bounce case next: if the paddle sits at column 0 and the ball lands at column 9 from phase 0, that's another 9-of-10 distance, the same tight slack as before.

Now I'm checking the remaining failure modes: the mistuned tables and whether the keep-direction policy can cycle without scoring. I'm also setting the softmax logit gaps wide enough that sampling noise stops mattering.

I'm double-checking whether the scoring loop could run forever: bricks only count as hit right after a bounce, so the ball can't keep passing through them without scoring. Bricks also respawn at the next paddle bounce, so there's no stuck state there either.

Now I'm checking the catch condition for the row-8 ball moving down, which is tested after the brick check since row 9 has no bricks: the paddle has to be at the ball's pre-move column or its clamped new column after this action. From there I'm working out the target for the case where the ball is at row 8 heading down, which starts from the current ball column.

Now I'm setting up the lookup tables for each ball class, working out the target column for every position in the grid.

Now I'm filling in the lookup table for the right-down ball class, row by row: each row's target column is the current column plus the remaining moves, folded back at the wall.

Now I'm filling in the rest of the row-by-row lookup table for the right-down ball class, where each target column is the current column plus the remaining moves, folded back at the wall.

I'm filling in the lookup table for the left-down ball class, where the target column is the mirror image of the right-down table.

Now I'm working out the mirror-image table for the left-down ball class, row 5 next.

Now I'm filling in the mirror-image table for the left-down ball class, working through rows 4, 3, and 2, each one flipped from the matching right-down row.

Now I'm checking the left-down table for the bottom rows, where each entry is the mirror of the matching right-down row, reversed and flipped back.

Now I'm writing out the up-right ball class: the paddle-row distances for each row, with row 3 taken as five, row 2 as seven, and row 1 as ten.

I'm settling on n=7 for row 2 going up, since that matches the case where the ball hits a brick in row 1 and bounces back down through row 2. I'm also fixing row 1 going up at n=10 and row 0 going up at n=9, then starting on the right-up lookup table.

Now I'm filling in the right-up lookup table, working through each row's target column from the row's fixed move count, folded back at the wall. Row 8 comes out as 9, 9, 8, 7, 6, 5, 4, 3, 2, 1, and the rows above shift by one step each.

Now I'm writing out the mirror table for the left-up class, flipping each row of the right-up table across the center.

Now I'm writing out the mirror table for the left-up class, flipping the right-up rows across the center, starting with row 5.

Filling in the left-up table now: row 1 comes out as a straight mirror, 9 minus the column, and row 0 matches row 8 once the last entries are read off.

Now I'm setting up the horizontal gating weights, with the ball column and trail column feeding into a combined signal.

I'm working out the horizontal gate weights for the right and left gates, with the ball and trail columns feeding into the combined signal and a fixed bias. Then I'm setting up the vertical down gate, with the ball row and trail row each contributing their own weights, and I'm going to check that gate again.

I'm checking the up-move condition for each row of the down-gate weights, where the ball's row gets a negative contribution against the trail row.

Now I'm checking the up-gate values for each row, with the ball row weights running from -G at the top through -5G at the bottom, and confirming the same-row cases stay switched on or off as intended.

Now I'm checking the up-move condition for the down gate against the trail row, verifying each row's sums come out to zero.

I'm checking the verification arithmetic for the vertical gates: the down-move and up-move sums come out to zero or negative as intended, and the same-row cases switch on only at the right rows. That confirms exactly one vertical gate and one horizontal gate are on in every legal configuration.

I'm checking whether same-row cases can show up at rows 5 through 7, and concluding they can't: bricks only sit in rows 1 to 3, so a bounce off a brick leaves the ball in rows 2 to 4 or 0 to 2, with the top wall covering row 0.

Now I'm checking the same-row cases for the down gate: a hit from above at row 2 leaves the ball going up but still classified as down, which is harmless, and row 0 going down gets the same treatment.

I'm settling the constants: K=4 keeps the signal range within ±36, and with G=60 and H=30 the worst off-state gives z=-24, so the gate sits at essentially -1. For a matched state the on-value is tanh(4), about 0.99933, which is still clearly on.

Now I'm weighing a different scale: K=5 gives tanh(5), which is about 0.99991, but then the constants get large, around 700 at the top end. I'm testing K=4 with H=25 and G=50 instead, which keeps the numbers smaller and leaves the worst off-state at -14.

I'm writing out the per-row offset arrays for the horizontal and vertical gates, with the ball and trail tables scaled by H and G. I'm also considering a simpler choice of G=100 and H=50, since multiples of 100 keep the gate values cleanly separate from the K·T signal.

Now I'm weighing whether to keep the gate weights as explicit numbers or use an incremental approach, and I'm leaning toward the explicit version with the hundreds digit carrying the gate value and 4T supplying the small part.

Now I'm checking the sizing of the output weights: with c = 20, when s is near 1 the right logit comes out around +20 and the left around -20, so the two outputs stay well separated.

Now I'm weighing the output biases: the noop logit sits at 0, and I'm setting the up, down, and fire biases to -40 so they stay effectively unsampled. I'm checking that with the gate signal near zero, right and left both come out around -20, and the wait-state stays as a plain no-op with nothing added to it.

I'm weighing whether the paddle's overshoot after a last-moment arrival could cause a miss. If the paddle keeps moving in the ball's direction, the catch still works, but if it moves the opposite way, the ball gets missed.

I'm checking whether the paddle could overshoot at the last moment. If it arrives right at the decisive step and a sticky repeat fires, it could keep going past the catch point, and I'm still weighing how often that happens.

Now I'm checking the paddle's catch window: if the ball keeps climbing through the holes, its target drifts one column per step, and once it comes back down the target locks in place.

I'm checking whether the paddle's path to the intermediate target x(u0+9) could carry it away from the final catch point at x(u0+11), since the reflected path has a couple more steps to go.

I'm now checking the cases where the ball is in the same row as a brick or the paddle, and working out the worst-case misses from sticky repeated moves. Each bounce looks like it has well under a 1% chance of failure, so the bigger risk is an error in my understanding of the rules or in the weight tables.

I'm now weighing whether the paddle could lag behind the ball when it lingers at the wall. The target holds at the same column for a step, so a repeated move at that point would carry the paddle past the intended position, and I'm checking how much that lag could cost.

Now I'm weighing whether the ball coming down at row 2 could hit a brick at row 3 next to its hole, since the neighbor cell might still be filled, and I'm checking that against the trail before trusting the no-obstacle assumption.

I'm checking the bounce sequence after a brick hit: the ball moves from row 2 down into row 3, and since the hit just happened, the brick there is passed through rather than bounced off. Then it clears and continues downward.

I'm checking the ball's path once it bounces off a brick in row 2 and heads down: the next cell in row 3 gets passed through if it's a brick, since the hit just happened. Hits from above behave differently: a ball in row 1 or row 0 heading down bounces back up, and the top wall handles the reversal in row 0.

Now I'm checking the brick-respawn timing: once all bricks are cleared, they come back when the ball bounces off the paddle row, so from row 8 heading up the ball should hit a row 3 brick, and that part of the prediction still holds.

I'm settling on the core policy as ready, and I'm considering whether to use the spare capacity in layer 1 for extra robustness. Extra redundancy doesn't look necessary. I'm also weighing an "anticipate the next target" idea, but at the decisive step it would come too late or too early, so I'm setting it aside.

I'm checking whether a paddle that arrives one step before the decisive move could overshoot if a sticky repeat fires, and how often that actually happens. It only matters when the paddle has been lagging, so I'm estimating how many moves it needs before the rebound.

I'm checking the rough failure rate per bounce, which looks like a few times ten to the minus four up to a thousandth, so the scores should stay well above what RL-trained baselines usually reach. I'm also confirming the time budget for the keep-direction bounce, where the paddle starts one cell behind and needs at most nine moves to reach the catch point. Finally I'm noting that the sticky repeat at the very first step is harmless since the previous action is probably zero, and I'm moving on to the second layer and the outputs.

Now I'm setting the second-layer weights for the "go right" unit: each of the four input units gets weight 8, with a bias of 20. Checking the cases, a strongly active signal gives about +1, a neutral one gives about -0.999, and an inactive one gives -1. For the "go left" unit I'm using negated input weights with a mirrored bias.

I'm settling on the bias and weights for the "go left" unit, and I see that with κ = 8 the outputs land near ±1 but not quite at the extremes. Raising κ to 12 pushes them closer to ±1 while keeping the checks consistent.

Now I'm setting the biases for the output units: the "go right" unit gets a bias of 30 and the "go left" unit gets -42, using the larger scale of 12.

Now I'm checking how the input channels map onto the grid, with the paddle, ball and trail each sitting at their own offsets within the cell.

Now I'm fixing the constants for the gating units, with K at 4 and a large negative offset so the off state saturates. Next I'm assigning each of the four output units to a direction: right-down, left-down, right-up, and left-up.

Still writing the weight tables for the ball and trail cells...

Still writing the weight tables for the ball and trail cells...

Still writing the per-unit weight tables...

Still working out the weight table for the ball cells, row by row.

Still working out the weight table for the ball cells, row by row...

Still working out the per-cell weights for the ball, row by row...

Still working out the trail weights for unit 0...

Still working out the trail weights for unit 0...

Still working out the weight for the ball cell at row 4, column 1, and checking the trail and paddle contributions against the bias.

Still working out the weights for the left-down unit's ball cells...

Still working out the weight table for the left-down unit's ball cells...

Still working out the left-down unit's ball weights, row by row...

Still working out the left-down unit's ball weights, row by row...

Still working out the left-down unit's ball weights, row by row...

Still working out the trail weights for the left-down unit...

Still working out the left-down unit's trail and paddle terms, checking the sum against the bias.

Still checking the unit 0 values against the ball, trail and paddle terms for the right-down unit at this state...

Still working out the right-up unit's ball weights, row by row...

Still working out the right-up unit's ball weights, row by row...

Still working out the right-up unit's weights for the next rows...

Still working out the right-up unit's weights for the bottom rows...

Still working out the right-up unit's trail weights...

Still working out the trail weights for unit 2...

Still checking the right-up unit against a reset state...

Still working out the left-up unit's ball weights, row by row...

Still working out the left-up unit's weights, row by row...

Still working out the left-up unit's weights for the bottom rows...

Still working out the left-down... no, wait, this is the left-up unit's ball weights for the lower rows, and I'm on row 6 now.

Still working out the left-up unit's weights for the bottom rows...

Still working out the trail weights for the left-up unit...

Still checking the left-up unit's weights against the reset state on the right side.

Still working out the trail and paddle terms for the left-down unit...

Still working out the checks for the remaining units at the reset state...

Still checking the unit 2 values at the reset state, and the right-side sums come out to the expected +1 and -1 outputs.

Still working out the trail and ball checks for the right-down unit through the next few steps...

Still working out the right-up unit's trail and ball checks for the next few steps, tracing the ball from row 6 up to row 5.

Tracing the ball forward from row 5 to row 4 after the bounce, I'm checking the left-up unit's weight at that cell, which gives 4 and matches the expected movement.

Still checking the ball's bounce off the brick, then tracing its path down-left with the trail still pointing left.

Still checking the ball's path through the lower rows, where the left-down weights keep the trail at 4 as it moves down-left.

Tracing the ball forward, I'm checking the left-up unit's weights for the next two rows, and both give 5 at the expected cells, so the paddle should move right.

Still checking the left-down bounce, tracing the ball back down-right from the brick hit.

Still checking the left-up unit's weights at row 3 against the bounce off the removed brick, since the ball now moves into an open cell.

Still working out the left-down and left-up paths after the brick breaks, and the paddle shifts left to 2 as the ball drops toward the lower rows.

Now I'm checking the top-row case: if the ball moves up-right from row 1 with the trail one column to the left, the left-up weights should place the paddle at the expected column.

Now I'm checking the top-row case again: with the ball at row 0 and the trail one row below, the up-right weights still give the same target column, and the down-right weights pick it up consistently after the bounce. Next I'm testing the up gate at row 0, where the trail sits at row 1.

Checking the tables and class definitions by hand on a full game segment, with attention to the holes.

Working out the paddle position for the reverse-bounce case: if the ball comes back along the same path, the catch point shifts with the phase, and I'm testing whether the wall case at column 0 just gives the same position again.

Still tracing the ball's phase and landing columns after each bounce, and the pattern looks like it settles into a two-position cycle while the bricks at row 3 get cleared one column at a time.

I'm checking whether the paddle can still catch the ball if the first action gets wasted by stickiness: if the first move is lost, all the remaining actions would need to go right, and a second sticky repeat would break that, since the alternative catch point doesn't help for this wall-edge case.

Now I'm checking the edge case where the ball lands at column 0 with the paddle at 9 moves away, which would mean a full nine-step run with only one action of slack. The failure odds there look like about 1% per event, and since that only happens occasionally, the overall chance per bounce comes out near a tenth of a percent.

I'm noting that the landing phase w stays odd throughout, since each flight adds an even amount to the phase under keep-direction bounces, so I'll check which of the odd values from 1 to 19 actually come up over a game.

Now I'm checking the even-parity case after a reverse bounce: for w = 0 the catch sits at column 0, and the next landing shifts to column 9, so the paddle would have a full nine-step move with only one action of slack.

I'm weighing whether the tight case is worth a fix: when the ball is at column 0 or 9 and the paddle has to cover nine columns in ten actions, a double sticky at the start fails about 1% of the time. Those tight phases come up for roughly a fifth of row-4 rebounds, so the overall risk is around a tenth of a percent per bounce, which is near the budget.

I'm weighing whether the paddle can start moving before the bounce, but the decisive catch for that landing needs it already at column 0, so it can't pre-move. I'm then considering whether a reverse bounce earlier could change the landing phase parity and avoid the tight case, and I'm about to recompute the distances for that option.

I'm setting up the two catch options for a landing at phase w: keeping the paddle at x(w), or reversing to x(w+1). For the keep option, the next landing is at w+10, so the paddle would need to cover a distance of |9 − 2x(w)| from where it sits.

Now I'm tabulating the catch distances for each landing phase: for the keep option it's 9 at w=19 and w=9 and 9 at w=10, while the reverse option gives 9, 9, and 8 at those same phases. For the rest, the distances are smaller, so those cases have more slack.

Now I'm checking the catch distances for the reverse option: with m = w+1, the paddle would need to cover 8 or 9 columns in the tight cases, and only at m = 4 does the reverse option land exactly on target.

I'm listing which tight cases can occur: a keep-bounce at w=19 or w=9, and a reverse-bounce at w=8 or w=18, each one leaving the paddle at the edge with almost no slack.

I'm working out which landing phases are the tight ones: forcing a catch at the wall at w=19 always leads to a tight w'=9 landing, since reversing gives the same cell. So I'm considering whether to pick between keeping and reversing at the previous bounce to steer away from phases 9 and 19.

I'm weighing whether to reduce the tight-flight risk by timing the paddle's last move before the bounce, since a "left" action at the decisive step would leave it harmlessly clamped at 0, so the remaining risk is only a "right" move that would pull it away.

I'm checking how often the tight landings (phases 9 and 19) actually come up, and the rough estimate is about a 1% failure chance per tight flight, which could add up to roughly a fifth of a percent of bounces overall.

I'm estimating that the yearly bounce count lands around 500 before a failure, which is still far above typical RL baselines on MinAtar Breakout. Even so, I'm checking whether the tight-flight failure can be reduced cheaply, and concluding that the 1% sticky-action risk can't be avoided by changing the paddle's last move.

I'm now looking at whether the tight landings can be avoided by choosing reverse bounces earlier, since a keep-catch at phase 9 or 19 leads to a tight next landing. The trouble is that the rule depends on the number of row-3 hits, so I can only steer away from those phases when the bounce count is predictable.

I'm checking whether the tight chain can be entered from a non-tight landing: the arrival flight has different geometry, but the flight after it lands on phase 9 or 19 and carries the roughly 1% risk. Following the alternation from 19 to 9 and back, the first flight hits the brick at column 5 in row 3, the next hits column 4, and once the column-5 brick is gone the chain breaks out on an 11-step flight.

I'm checking how often the tight flights actually happen: they need a landing at phase 9 or 19 plus a row-4 rebound, and the chain only lasts while the bricks at columns 4 and 5 in row 3 are still there. That limits it to maybe two or three per board, so the failure risk works out to about 0.1% per bounce, and I estimate around 1000 bounces before a failure, which is roughly the step cap anyway.

Roughly 500 bounces seems fine here. I'm wondering if there's a cheap way to avoid the tight flights, like choosing the alternative catch position at the previous bounce, but the entry point depends on the row-4 rebound and the brick layout, so it isn't predictable. A reverse-default catch doesn't obviously help either, since it just moves the tight phases to different landings. I'm also considering whether an early paddle move at the decisive step could shave off the risk in the tight case.

I'm still weighing whether a different paddle move at the decisive step could help, and I'm concluding it can't: the 'left' action just clamps at 0, and the next required move is 'right', so sticky actions still cost about 1% per tight flight.

I'm checking whether the tight flights could be avoided by not landing on phases 9 or 19 in the first place. That depends on the previous flight, so I'm looking at which arrivals from other bounce counts could lead into that chain.

I'm estimating how often the ball lands on phase 9 or 19 while the relevant row-3 brick is still present, since on a fresh board that seems plausible for the first flights after a respawn.

I'm checking whether the chain really keeps going: the ball from 19 would hit the column-5 brick in row 3, but once that brick is gone it passes through and hits the next one in row 2, so the third flight isn't tight.

I'm tracing the early flights from a fresh board: the ball starts at column 5 and bounces between landing phases 5 and 15, clipping bricks at columns 8 and 1 in turn. Tight flights would only arise if the ball later reaches phase 9 or 19 while the middle row-3 bricks are still standing.

Tracing the ball's path from the fresh-board start, I'm checking which bricks in row 3 it clips next and how the phases shift after each bounce.

I'm tracing how the ball's phase could wander into the tight chain: an n=11 flight from w=17 lands on 9, and from there the row-3 bricks at columns 4 and 5 would trigger about two tight flights per board, roughly a 2% failure risk.

I'm checking whether the paddle's waiting moves could reduce the 1% risk in the tight case at w=19, but any repeated 'left' at the wall is still wasted if sticky actions replace the needed 'right' at A1.

I'm weighing whether the tight chain could be broken at the wall-clamped waypoint by choosing a keep or reverse catch at w=17, since the next phase depends on whether the flight is 9 or 11 steps long.

I'm settling that from w=9 the catch is forced, so the next flight heads back to w=19 and is tight. That gives roughly two tight flights per board.

I'm checking whether the wasted moves at the start matter: for the tight flights, I need nine moves within ten actions, so two wasted actions in a row cost about 1%. With zero-or-two wasted moves the margin still holds, and three wasted moves would be about 0.1%. So I'll accept the small risk.

I'm checking the overshoot case now: if the sticky action repeats when the paddle reaches its target, it can push the paddle past the spot it needs, costing a correction step. In the tight case at phase 9, that repeated 'right' would just clamp at the wall.

I'm checking the overshoot case for a paddle that arrives at its target around action 7 with a 9-step flight. If the sticky action repeats, the paddle can overshoot, get pulled back, and then overshoot the other way at the decisive step, landing one cell short of the catch point.

I'm checking the overshoot case for the m=7, n=9 flights: an overshoot at the eighth action, a return, then a sticky repeat that pushes the paddle past the catch point on the wrong side. That's about 0.5% risk per flight, and it only bites when the paddle approaches against the ball's landing direction.

I'm checking the overshoot timing in the m=7, n=9 flights: if the paddle arrives at action 7 and the sticky repeat fires at the last step, it can end up on the wrong side of the catch point. That works out to roughly 0.9% per flight, and only when the approach direction opposes the ball's landing direction.

I'm checking the overshoot case for the m=7, n=9 flights again, this time when the sticky repeat hits on the second step as well, so the paddle ends up a cell past the catch point on the far side.

I'm checking whether the overshoot timing changes the picture: if the paddle is still moving at the decisive action, the sticky repeat can push it past the catch point, and that seems to be the main source of miss risk here.

I'm checking how the overshoot timing plays out when the arrival is at step k: the paddle only ends up moving unintentionally at the decisive step if it was still correcting right before then, and each correction step decays that chance by about 0.09.

I'm working out the miss probability when the paddle reaches its target at different points before the decisive action: if it arrives one action before, the sticky repeat alone gives about 10%, if two actions before it's roughly 1%, and if three before it drops to about 0.9%.

I'm working out the overshoot odds for the m = n flights: if the paddle arrives exactly one action before the decisive step, the sticky repeat alone gives about a 10% miss chance, depending on which way the ball lands.

I'm checking the tight flights at m = 9 and n = 9, where the target is the wall, so an overshoot is clamped and can't happen. For m = 8 the arrival lands one action before the decisive step, giving about a 1% miss chance. If one wasted move occurs at the start, the arrival shifts to the decisive step itself, so the miss chance rises to about 10%, depending on the ball's direction.

I'm checking the m=7 flights on the n=9 schedule, where the paddle arrives two actions before the decisive step, and the miss chance from a stray repeat lands around 1% either way.

I'm working out the miss probability when the paddle arrives two actions before the decisive step: an overshoot at the eighth action, a return, and then a sticky repeat at the last action can land it on the wrong side of the catch point, with the chance depending on the ball's landing direction.

I'm working out that the m=7 flights miss about 1% of the time, since the overshoot chain can leave the paddle one cell off the catch point. The m=5 flights are far safer at roughly 0.1%, and the m=3 and m=1 cases are negligible. What I still need to settle is how often those m=7 flights actually come up.

I'm looking at the flights where the paddle has to travel seven cells, since those seem to carry about a 1% miss risk. Going by the wall-position pattern, the m=7 case comes up fairly often, so its share of the total matters. I'm figuring the average miss rate across flight distances from that distribution.

I'm estimating the per-bounce miss rate for the n=9 flights at roughly 0.4%, which would only give a few hundred bounces before a failure. I want to cut that by about an order of magnitude with better control, and I'm starting with the overshoot problem: arriving at the target makes the intended action switch to a no-op, so a sticky repeat pushes the paddle past it. One idea is a tolerance window, where a catch succeeds at either of two adjacent cells, so an overshoot toward the open side doesn't cost anything.

I'm working out a tolerance zone for the paddle: it stops when it reaches either of two adjacent cells, so one overshoot still lands inside the zone and costs nothing.

I'm settling on a two-cell target zone, the cells x(w) and x(w+1), so the paddle stops anywhere inside it. Going right if it's left of the zone, left if it's right of the zone, and doing nothing otherwise. I'm also noting that at wall turns the zone collapses to one cell, where overshoot can't happen anyway.

I'm now thinking about the deadband as two separate units per class, one firing when the paddle is left of the zone and one when it's right of it. That brings the hidden layer to eight units, with the output layer summing each class's two units and offsetting by the gating constant.

I'm weighing a simpler encoding: one unit per class centered on the zone, with the offset set so the deadband covers both cells. That keeps the layout smaller, but I still need to check how the wall-turn case, where the zone collapses to a single cell, separates from the no-op region.

I'm checking whether a tri-level threshold works here: with K=1 the zone-center offsets give tanh values of about 0.46 for the edge cells and 0.76 for outside, so a threshold near 0.61 separates them. A large second-layer gain then turns that into a clean on/off signal, and gating at -100 keeps the off-state at exactly -1.

I'm settling the zone-center encoding with a scale factor of about 1.1, where the midpoint threshold sits near 0.65 and the margin is roughly 0.15. I'm weighing whether to keep the weights as non-integers or rescale the centers into doubled units to keep the arithmetic clean.

I'm settling on K=1 for the single-unit encoding, since the zone-center values then come out to simple half-integer or integer weights, with a threshold near 0.61 separating the edge and outside cases. I still need to check how the wall-turn landings, where the zone collapses to one cell, behave under that same threshold.

I'm settling on centers at half-integers by placing the wall-turn zones virtually, so each no-op cell sits at a distance of 0.5 and each move cell at 1.5 or more. That keeps every z-value either ±0.5 or beyond ±1.5, which should let me push the threshold further and raise the margin.

I'm comparing the tanh outputs for several values of K, checking the gap between the in-zone and out-of-zone values and the margin it leaves around the midpoint.

I'm settling on K=1 with half-integer centers, which gives a margin of about 0.22 between in-zone and out-of-zone outputs. Now I'm setting up the second layer with a threshold near 0.68 and a steep gain so the on/off signal stays clean.

I'm settling on a scale of 100 for the gates, since the off-state then saturates to exactly -1 and the arithmetic stays simple. Next I'll check whether the zone-based policy holds up.

I'm checking whether the paddle approaching from the ball's heading side always stops at the far cell of the zone, which would make R-catches common. Since the catch type depends only on which side the paddle comes from, I'm wondering if that creates a non-scoring cycle, like a repeated pure-R pattern bouncing between two paths.

I'm checking the ball's bounce pattern after a paddle catch: a free flight of 17 cells sends the next landing to w' = 15 - w, so the zone shifts and the catch type could repeat. If it's R both times, the two-step cycle returns to w, which would mean a non-scoring loop.

I'm checking the example: with the paddle arriving at 6 from the right, it heads toward the zone {3, 4} and stops at 4, which is the x(w+1) cell, so that's another R-catch. I'm tracing the pattern further to see whether the paddle keeps landing on the same side of the zone on each bounce.

Now I'm checking the failure mode: if the paddle keeps catching on the same side, the ball can bounce between two paths forever without scoring. Sticky actions would eventually break that loop, but each round trip wastes about 18 steps.

I'm weighing how the sparse-board phase costs time: with a K-only policy the ball sweeps the remaining bricks within about 180 steps, while an R-heavy policy wastes more steps on long free flights. Since the budget is 10,000 steps and the score is bricks cleared, the rate per step is what matters, so I'm estimating roughly 15 steps per brick on average.

I'm considering whether the zone should depend on the ball's row: when the ball is still far away, a single precise target cell makes sense, and only when it is close, within a couple of actions, would I widen the deadband to include the overshoot cell.

I'm considering whether the zone should narrow to a single cell on the rows far from the paddle, and widen to two cells only on the last couple of rows, where there's little time left to correct. That would give two zone widths, each with its own center, and I'm checking whether one gain can separate both cases cleanly.

I'm weighing a different encoding for the two-cell rows: scaling the centers and using separate units per row group, so each group gets its own gain. Then I'm considering two threshold units, one for each direction, with integer cutoffs.

I'm now defining two threshold units, one for each direction, with the ball-side tables set so the left and right bounds match on most rows and split only on the late rows. I'm working out the weight arithmetic for each unit and how many tables I'll need to write.

I'm now weighing whether to write the 1,520 weight values out by hand or to restructure the tables so there are fewer of them to compute. Shared trail and gate weights between the R and L units of a class could cut the manual arithmetic, but I'm still deciding which approach is less error-prone.

I'm thinking about whether the paddle can avoid overshooting by changing the deadband near the end: a single cell when the ball is far, two cells only on the last rows, since sticky actions can repeat a correction and loop.

I'm now checking the failure case at the decisive action: the paddle has to end up either on L or on L+d. I'm sorting the possibilities by the paddle's position and by which move it made last, since a sticky repeat of that move is what could push it out of the zone.

I'm checking which paddle positions lead to a miss on the final action: sitting at L after a move away from L+d, or at L+d after a move toward it, can repeat under sticky actions and push the paddle outside the zone.

I'm checking how the paddle can end up at L with its last move being a sticky repeat, since that's what pushes it out of the zone. If it moved toward L from the far side on the previous step, a sticky repeat could carry it past L, so I'm tracing which starting configurations lead to a miss at the decisive action.

I'm checking whether a miss needs two sticky repeats in the final two actions, or one sticky repeat at the last action when the paddle is already in a wrong-way state. Following the zone rule for those rows, I see that a single sticky event at the decisive step can't push the paddle out of the zone unless it arrived late.

I'm checking whether a miss needs two sticky repeats in the final actions, since a single sticky event at the decisive step can't push the paddle out of the zone unless it arrived late. If the paddle lands in the zone at the last step, whichever way it came in, the one repeat still leaves it inside, so only a late arrival or a prior sticky event leaves a real risk, around 1%.

I'm checking the case where the paddle overshoots on the row before the decisive one: if it lands on L+d, it stays in the zone and catches on the right, which is fine. If it lands on L-d, a sticky repeat can still pull it back to L, but another sticky event on the last step would leave it outside the zone.

I'm checking a flight where the paddle arrives at L on the last move, then works through the remaining steps. Sticky repeats could push it one cell off on the earlier row, but on the last rows the two-cell zone absorbs that, so the chance of a miss comes out around 0.1%.

I'm checking whether a miss needs the paddle to get pushed off the wrong way, and I'm arguing that on the -d side there's no tolerance for overshoot. I'm thinking about whether the resting spot should shift to the far cell when approaching from that side, so that a sticky overshoot still lands inside the zone.

I'm comparing three policies for the end of the flight: an always-on zone that absorbs single overshoots but causes R-catches whenever the paddle approaches from the +d side, the single-cell target that leaves roughly a 0.4% failure rate, and a mixed approach that would use single cells early and the wider zone only near the end.

I'm working through the paddle's approach to the zone for the next row group, where the zone's two edges come from the ball's landing column and the column one step over. The paddle is at x(w) and needs to reach that zone, so I'm checking how its starting cell relates to the two target cells.

I'm checking which cell the paddle reaches first on the next ball arrival. The two zone cells depend on the starting position a and the direction d: for d = +1 and a = 2 the paddle hits the right cell first, which is an R-catch, while for a = 7 it hits the left cell first, a K-catch, so the outcome turns on the geometry.

I'm checking whether a cycle can form where every catch is an R-catch, which would mean the landing index goes from w to 15 - w and the paddle has to keep approaching from the right side.

I'm checking how often the ball would land in one of these R-R cycles without scoring, since each loop wastes roughly 180 steps before a sticky event breaks it.

I'm weighing whether a non-scoring cycle is a real concern. It would need a sparse board, since those paths cross several rows of bricks, so it only becomes likely once few bricks remain. A fixed single-cell target sweeps the ball systematically and tends to find bricks sooner, while an always-on zone adds an unpredictable mix of catches. One option I'm considering is a single-cell target by default, with the wider zone only for the last few actions so late overshoots are tolerated.

I'm checking what happens if the paddle arrives at L late in the flight and an overshoot follows. The return move usually fixes it, but each overshoot shrinks the chance of staying in the zone, so the residual risk fades over a few steps.

I'm working through the case where the paddle starts with its last move as a sticky repeat in the +d direction, where a single further sticky event keeps it inside the zone, so the miss chance is about 0.1%. Next I'm looking at the case where it starts on the -d side, where one sticky event at the first step can pull it back off the zone and cause a miss.

I'm checking the cases where the paddle starts with a last move of +d or -d, with one sticky overshoot at the decisive steps. The ones that start near the zone carry roughly a 1% miss risk, since a single overshoot followed by another sticky event can push the paddle out.

I'm estimating the miss probability for the live states at zone entry: an overshoot from L in the -d direction, followed by a return, leaves about a 1.9% chance of a miss, and about 1 to 2% overall from those states.

I'm estimating the miss risk for arrivals right at the boundary: about 0.1% if the paddle lands with its last move in the +d direction, and about 1% if it lands in the -d direction. For arrivals a few steps earlier, the chance of an overshoot plus a later slip is only around 0.2%, and it drops further the earlier the paddle arrives.

I'm now checking the case where the paddle arrives at the near zone cell and then sticky-overshoots to the far cell. A second sticky event would push it out, but the return move usually brings it back, so a miss takes two unlikely events in a row.

I'm checking the miss rate for the zone-only policy: if the paddle arrives exactly one step before the last action, two sticky overshoots push it out, about 1%. Arriving two steps early gives about 0.1%, and the risk drops again for earlier arrivals. Under that policy the paddle may also reach the near cell a step sooner than under the single-cell policy.

I'm estimating the miss rate for arrivals when the paddle reaches the wall cell exactly on the final move, where overshoot isn't possible, so any miss would need two sticky wastes at the start.

I'm now checking the miss rate for the S policy at arrival time m=7, which is about 1%, and comparing that with M2 where it is 0.1% or 1% depending on the direction of the last move. Under Z, the near-cell arrival may come a step or so earlier, which gives a similar miss rate of roughly 0.01 to 0.1%. For the K-chains at m=7, I'm looking at the cases w=1 and w=11, starting with w=1 mapping to w'=11.

Now I'm checking the case where the paddle starts at x(1)=1 and the ball heads back the other way, so the landing column becomes 8 and the paddle approaches from the left, opposite to the new direction of travel. That makes it the unlucky direction under M2, where the miss risk is about 1%. Under Z, the paddle would instead settle on the near cell at 7 one step sooner, which is an R-catch.

I'm going back and forth on the m=7 case: under the single-cell-plus-zone policy, flights where the paddle approaches from the left hit a 1% miss risk, while the zone-only policy cuts that risk but lands the paddle on an R-catch. I'm also wondering whether a mid-flight change of strategy, like slowing down before arrival, could avoid creating a live overshoot state in the first place.

I'm considering whether the paddle can avoid the overshoot problem by interleaving no-ops as it approaches the target. A sticky repeat after a no-op only delays, but after a move it pushes one more step toward the target, which is harmless until the final approach. Right at distance one, the last move is still followed by an intended no-op that can overshoot, so interleaving doesn't remove the risk.

I'm weighing whether the R-catches under the always-zone policy are actually costly, so I'm going to simulate free flights without brick hits over 17 steps to see whether they produce cycles. Each catch leaves the ball and paddle in a state I can track: a K-catch at w puts the ball at phase w+1 with the paddle on x(w), and an R-catch at w puts the ball at phase 18-w with the paddle on x(w+1).

I'm checking whether the paddle can stay on a zone cell after a wrap, since if it starts on x(w), the next zone sits one cell away and the paddle slides to the far side, producing an R-catch.

I'm checking the next step in the cycle: after an R-catch the free flight lands the ball on a new zone, and I want to see whether the paddle ends up on the near or far cell there. I'm working through where the zone sits relative to the paddle's current column to decide which type of catch comes next.

I'm seeing that the ball then keeps landing in zone cells that make the paddle step to the R-cell again, so the pattern repeats in a two-flight cycle. Only a sticky overshoot at arrival breaks it, at roughly 10 to 19% per flight.

I'm checking how the cycle plays out as the board empties: under the always-zone policy, free flights keep the ball in a two-flight loop of R-catches, and only a sticky overshoot breaks it. Each new phase pair then takes about ten flights to reach, so on sparse boards the exploration slows a lot, while the K-only policy covers every path in ten flights.

I'm checking how many bricks could be cleared within the 12 cells a pair of free flights covers, since a miss there means the policy stalls until a sticky overshoot breaks the cycle. Under the K-only policy, by contrast, the sweep reaches every path within about ten flights.

I'm now weighing a middle-ground policy: apply the zone rule only for the final few actions, so that single-cell targeting usually lands the paddle early on the near cell and only late arrivals or overshoots produce an R-catch. Under free flights that would behave much like the K-only sweep, which covers every path in about ten flights, and it would keep some of the robustness to sticky overshoot. Next I want to decide which rows should get the zone rule.

I'm testing a refinement for the early phase, where the single-cell target would leave the paddle on the far side after an overshoot. One option is to stop at the right-hand cell whenever the paddle reaches it, which is the always-on zone rule, but that only helps when the paddle comes in from that side. Approaching from the other side would mean passing through the right cell to reach the left one, which invites an overshoot back toward the wrong side.

I'm now setting out the miss probabilities for the M_j policies over the last few flights, defining each position relative to the target cell so the single-cell and zone rules can be compared directly.

I'm working out the miss probabilities for the zone-window policy, starting from the terminal condition that a catch needs the paddle to end on cell 0 or 1. Working backward from zero remaining actions, I'm setting up the single-action case at q=0, where a sticky repeat of the move toward -1 is the one path that misses.

I'm working out the miss probabilities for the zone rule one action from the end, checking each starting position and the effect of a sticky repeat on whether the paddle ends on a catch cell.

Now I'm working out the miss probabilities for the zone rule with two actions left, starting from the state where the paddle already sits on the left target cell.

I'm working through the two-action case for the zone rule, checking each starting position and how a sticky repeat changes whether the paddle ends on a catch cell. Starting from the left target cell, the miss chance stays at zero for the intended move, and the next question is what happens to the cell just past the right-hand one when the last move is repeated.

I'm working out the miss probabilities for the zone rule with two actions left, checking the cases for a paddle sitting two cells past the left target and for the cell just beyond the right one. For the far-right start, a sticky repeat of the outward move still lands off the catch cells, so the miss chance there is high.

Next I'm computing the miss probabilities at three actions remaining: when the paddle already sits on the left target cell, a sticky repeat of the move outward gives a small chance of missing, and the same check for the right-hand cell shows a larger chance.

I'm checking the miss probabilities for the zone rule with three actions left, stepping through the cases where the paddle sits just outside the target cells and a sticky repeat pushes it back or further away.

Now I'm checking the miss probabilities for the zone rule with three actions left at the edge cases, and working out the entry states for the single-cell rule.

I'm checking the miss probability for the zone window of three actions, starting from the case where the paddle is approaching from the right-hand side and lands on the left target cell at the third-to-last step. For that entry state, the chance of a sticky overshoot causing a miss is small, at about 0.1% in one direction and about 1% in the other.

Now I'm checking the zone window of four actions, where the paddle arrives from the right side and sits on the right-hand catch cell at the start of that window. A sticky repeat of the last move is the only thing that could push it off, and that happens only about 0.1% of the time, so that entry state is nearly safe. The cost is that every unlucky approach from that side ends as an R-catch.

I'm checking the sparse-board case next, where free flights give the window only three or four actions and the paddle usually reaches its target early. The dense-board R-catches look harmless, since the bricks keep changing the ball's path.

I'm now working out the miss probabilities for the zone-window policies, first checking which direction the paddle approaches from on each of the K-chain flights, and how that changes the entry state.

I'm working out which way the paddle approaches on each flight, since the sign depends on whether the starting cell is on the left or right of center. For the rightward ball, the approach is from the right side for starting cells up to 4 and from the left side beyond that, and the leftward ball flips those signs. Next I'm listing the odd starting cells to get the distances that feed the miss probabilities.

I'm checking the odd-parity K-chain flights: the m=7 cases approach from the right side, while m=5 and m=1 come in from the left, and the wall case at m=9 is separate.

I'm working out the S-rule miss probabilities for m = 7, starting from the arrival at q=0 with the remaining three actions. At one action left, the paddle at 0 misses with probability 0.1 when the sticky repeat pushes it toward -1, while the cell at 1 doesn't miss on that step.

Now I'm tabulating the one-action miss probabilities for the zone rule, checking where a sticky repeat pushes the paddle off the catch cells from each starting position.

Now I'm tallying the miss probabilities for the single-cell rule with two actions left, working through each starting cell and how a sticky repeat changes whether the paddle lands on a catch cell.

Now I'm checking the policy S miss probabilities for the m=7 flight: the paddle arrives at cell 0 at the third-to-last step, and its chance of missing is about 1% there. If the start wastes one action, the arrival is still at 1%, and if it wastes two, the miss chance drops to about 0.1%.

Checking the miss probability at the third-to-last step again, I get 1% for the single-cell arrival from the right. The window policy M_3 doesn't help here: starting at (0, -1) with three zone actions still gives 1%, because a sticky repeat pushes the paddle to -1 and from there the miss chance is 0.1%-level damage that still adds up. Total for this flight is about 1.1%.

I'm now checking the window policy M_4 for the m=7 flight: the paddle sits at q=1 with the last move at -1, and the chance of missing is about 0.1%, since only a sticky overshoot to 0 with the three-action window could send it wrong. If the start wastes an action, the paddle is at q=2 at A7 and I still need to follow that case through with the three-action window.

Checking the m=5 flight next: its arrival is from the left side, so after one single-rule step the paddle sits at the edge of the window and the miss chance is about 0.02%. Now I'm turning to the m=3 flights, which approach from the right.

Now I'm checking the m=3 flights, which approach from the right: the paddle steps to 0 and then has to hold through the single-rule steps, with a sticky overshoot chance at each one. Working through those branches, the window policy M_4 keeps the total miss chance negligible.

Checking the m=9 tight flights next: they're the main remaining risk, at roughly 1% each when the start wastes two actions, while the m=7 flights sit near 0.1% under the four-action window. Even with those, the total miss rate per n=9 flight stays small, and I'm going to think about whether the tight flights can be handled differently.

I'm trying to shave down the two-wastes risk on the tight flights. If the decisive action just before the first catch were "right" instead of the repeating move, the sticky-repeat chain would break earlier, but I'm not sure that actually changes the start-waste probability.

I'm considering whether the tight flights can be made safer, like using a different action at the wall, but that doesn't change the two-wastes risk. Flights with n=11 or more have more slack, so I'm checking how the target shifts during those longer flights.

I'm tracking the paddle's target as the ball moves up through the rows: at t=4 the prediction is u0+9, then it shifts to u0+10 at t=5 and settles at u0+11 at t=6, so the paddle has to make two extra moves over those steps.

Now I'm checking the target shifts during the row-3 and row-2 flights: the paddle's predicted point moves by one or two cells at t=5 and t=6, so it still has time to settle before the decisive action. I also want to look at the wall cells for the downward-moving states at rows 8 through 5, since those set the window for the next catch.

I'm weighing whether a wider window, covering the down-states at rows 4 through 8, would help the m=7 flights that start late, or whether the current four-state window already handles them well enough.

I'm checking whether j=4 or j=5 makes a real difference for the m=7 flights. Either way m=7 gets R-caught, and after an R-catch the parity flips, so the remaining distances change. Without any start waste, the paddle has moved from 7 down to 1 by A6, and I'm working out what state it's in at A7.

I'm mapping the turn-by-turn timeline for the n=9 flight: the bounce at row 8, then the ball climbing through rows 7 to 4 while the paddle acts at each step. So the action A_k is taken while the ball is at state t = k-1, with A10, the decisive one, taken at the row 8 down state.

I'm settling on a window of the last four actions, covering the down-going states at rows 5 through 8, where the paddle should hold a two-cell zone. Rows 0 through 4 and all the up states stay with a single cell, since the zone only helps once the ball is coming back down toward the paddle.

Now I'm checking the m=7 approach from outside: the paddle is at -1 before A7, the zone rule sends it to (0,+1), and the 0.001 miss chance holds if the sticky moves don't break it. For m=8 with a=-1, the paddle goes to q=1 at A7 and the three-action window still gives about 0.001.

I'm working out the residual miss risk: if the ball arrives at A_{n-1} from the outside, there's about a 1% chance of losing it, since two sticky moves in a row push the paddle past the far side. A 3-cell zone wouldn't help, because only two cells catch. Arrival at A_n from that side is safe, with M_1 giving zero miss chance.

I'm checking the tight flights' residual risk by arrival timing: arriving at A_{n-1} from outside is the worst case at about 1%, while arriving at A_n or later is essentially safe. For the odd-parity m=7 and m=9 flights, a clean start gives roughly 0.1% and 1% respectively, and with one wasted start action the m=7 case drops to zero.

Estimating the brick rate now: a dense board gives roughly one brick every 10 steps, slowing to about 12 as the row-3 bricks thin out, so the 10,000-step cap should be the real limit rather than the ball being lost.

I'm estimating the brick rate at roughly 13 to 15 steps per brick, which works out to about 700 bricks per episode. Since the cap is the real limit, I'm asking whether the policy can speed that up through aiming, and I'm leaning toward leaving it simple.

Next I'm checking the paddle's approach for the short flights: after a K-move, the paddle sits two cells from the landing spot on the side the ball came from, so it should reach the catch point in two actions and then hold there. If the start action overshoots by one, the paddle has to come back, and it may overshoot again before it settles, but by the time the window opens there's plenty of time to correct.

Now I'm settling the final policy: single-cell targets for the up classes and for the down classes in rows 0 through 4, and a two-cell zone for the down classes in rows 5 through 8, keyed to the ball's direction at landing. For the implementation I'm planning two thresholds per class, one for each side, so the comparison can be written as a sign test.

Now I'm setting up the unit weights for each class: two units per class, one for each side, with the R-unit and L-unit thresholds taken from the lo and hi tables. Where a row has a single target, both thresholds coincide, so the two weights are just mirror images of each other.

I'm now working out the landing-phase bounds for the right-moving down class: when the landing phase is at most 8, the zone is the two cells from that phase on, and near the bottom-right corner I'm taking the single cell or the pair that the wall mirroring allows.

Now I'm writing out the lookup tables for the rightward-moving down states in rows 5 through 8, working from the landing phase so each row's lower and upper cell bounds are set.

Now I'm filling in the lookup table for row 5, where the landing phase offsets the cell bounds by three, so the zone shifts accordingly near the right wall.

Now I'm filling in the lookup table for row 5 and checking it against the L table, where the single target cell should sit in either bound. Then I'm writing the rows 0 through 4 rightward-down tables, where the bounds coincide at the target, starting with row 4.

Working out the mirrored lookup tables for the leftward-moving down states now, starting with row 8 and reflecting the rightward bounds across the board's center.

Working out the mirrored lookup tables for the leftward-moving states in row 7 now, checking each entry against the rightward bounds.

Now I'm checking the left-moving down-state table for row 6, mirroring the rightward bounds across the board's center.

I'm checking the left-moving down-state tables for rows 5 and 6 against the mirrored bounds, using the same reflection across the board's center.

Checking the left-moving down-state tables for row 5 against the mirror bounds, I'm confirming the lo and hi values line up with the zones at each column. Next I'm filling in the rows 0 through 4 tables for the leftward down states, where the lo and hi bounds coincide at the single target cell, starting with row 4.

Still writing the unit weight tables...

Still writing the unit weight equations...

Still weighing the scaling: with K=4 the on-state margins are only about ±0.96, so I'm considering K=6 for sharper saturation, though that makes the off-state gate arithmetic heavier.

I'm settling on a gain of K=4 for the unit weights, since the on-state outputs only need to be about ±0.96 for the second layer to re-saturate them. Checking the off-state margin, the gates push the worst-case pre-activation to about -66, so it stays clearly negative. Now I'm starting the second-layer weights for the go-right unit, summing the right-moving unit outputs with a shared scale.

I'm settling on logits that fold the up/down/fire actions into the same baseline as no-op, so the only real difference comes from the go-right and go-left units. I'm checking whether leaving those three at zero would let them be sampled as often as no-op, and the answer depends on how the noop logit is set.

Now I'm setting the suppression for the up, down, and fire logits, so they sit well below no-op and only the left and right units decide the move.

Still writing the per-unit ball terms...

Still writing the trail offsets for the down and up units...

Still writing the trail offsets for the unit weights...

Still writing out the trail offsets and gate terms for each unit, which is tedious but straightforward. Rather than splitting the weights into many small blocks, I'm considering filling the whole 100-cell table at once, though the row-by-row lines are easier to check.

Checking the trail gate on the catch state now: after a right-side paddle catch the ball's direction flips, but the trail still records the old cell, so the horizontal gate reads it as rightward motion. That mismatch is the problem I need to resolve.

I'm checking how the trail gate behaves right after a paddle catch: on an R-catch the ball's direction reverses, so the trail suggests rightward motion when it is actually leftward. The ambiguous state is a ball one cell off its trail on row 8, which could be either a continuing or a reversed catch. I'm now wondering whether the paddle's position can tell the two cases apart.

Now I'm working through the paddle-dependent case: if the paddle sits under the ball's column, the ball has reversed, and if it sits under the trail column, the ball is still on its original heading, so the target cell depends on which of the two it is.

Now I'm checking whether one threshold per cell can handle the paddle-dependent case: the paddle sits either at the ball's column or one step behind it, and the two cases need different cutoffs for the right-moving unit.

I'm checking which paddle positions make the right-moving and left-moving units fire for this state. The right-moving unit fires for every case when the lower bound sits at least one cell past the ball, but only for the continuing-direction case when the bound matches the ball's column, and the left-moving unit works the same way in reverse.

Checking the right-moving case first: with the paddle one cell behind the ball, the target works out to the right for the early columns and to the left from column 6 onward. Then I'm switching to the reversed case, where the ball's phase depends on the opposite horizontal direction.

Now I'm checking the right-moving case when the ball is at column 9: the target lands at 0, which is the far side of the board from where the paddle would sit, so the comparison flips again from the cells before it.

Checking the right-moving unit for row 8: when the ball is at columns 1 through 3, it should fire whether the paddle is where the ball was heading or where it reversed, so its lower bound has to sit at or past the ball's column. At column 4 the continuing case still needs to move right but the reversed case should stay put, so the cutoff lands exactly on column 4.

Still working out the row-8 thresholds for the right-up class, where the ball sits at column 0 and only the continuing-direction case applies, so the right-moving unit should fire against the paddle there.

Now I'm checking the threshold for column 4 on this row. If the lower bound sits at 4, the case where the paddle is at 3 still fires toward the right, so I'm weighing whether that one-cell overlap is acceptable or whether the upper bound needs to shift to keep the two cases apart.

Still working out the thresholds for the right-up class at row 8: with the ball at column 6, the paddle is closer to the K-case target at 4, so the low bound needs to sit at or below 5 and the high bound at or below 4.

Checking whether the same threshold logic still holds once the next state follows an R-catch, where the ball sits on row 7 and the trail is on row 8, so the direction has to come from that offset.

I'm mirroring the left-up row-8 case onto the right-up one: with the trail on the other side, the paddle now sits at c+1 in the continuing case and at c when the ball has reversed. I'm lining up the left-up target table against the right-up one, so the adjustments I already made at column 4 and 5 carry across to the mirrored columns.

Checking the mirrored cases for the left-up row: at column 5 the paddle would sit at 6 if the ball kept its heading, and the target there is still to the left, so the left-moving unit should fire. If the ball has reversed, the paddle stays at 5 and nothing should fire. At column 4 the thresholds need to split the two paddle positions the same way.

Now I'm checking the remaining columns for the right-up class: at column 3 both paddle positions should send the ball right, so the thresholds there can stay at 5.

Checking the left-up row-8 thresholds at the wall: with the ball at column 9 and the paddle at 9, the target is 0 and the action is left. The remaining columns around 0 look consistent, so the last piece is the left-moving cutoff there.

Now I'm checking the right-up row-8 cases against each other: at column 0 and column 1 the target is still to the right, and for the reversed paddle at column 1 the target is also right, so both thresholds can be set to 9.

Now I'm checking the row-8 cases at columns 6 through 9 for the right-up class: a threshold of 4 works for column 6, and columns 7 through 9 hold up with thresholds of 3, 2, and 1. Then I'm confirming that both the K and R cases at column 9 send the ball left. So this state is settled, with only columns 4 and 5 needing the small tweak, and since the paddle after a catch can only sit at one of two positions, no other paddle placements need checking.

Checking the collision case where the ball is one cell from the wall: after a right-moving catch at column 8 with the paddle at 9, the ball reverses up-left and the trail sits one cell behind it, so the same direction logic applies. I'm now going through what happens when the ball's next move would reach the wall right after a catch.

Now I'm checking the trail-based direction on the K-catch at column 8: the ball lands on column 9 heading up-right, the trail stays at column 8, and that still reads as right, so the target is the wall turn at 9 and then left, which gives T_K(9) = 1.

Checking the left-moving case at the wall: with the ball at column 0 and the paddle at 1, the K-catch sends it up-right, and the trail still reads as left, so that needs to be covered. When the ball is at column 1 the paddle can also sit at 0 after the reversal, and the right-moving unit has to fire there. So both placements at column 0 are settled.

Checking the row-8 tables once more: the right-up thresholds get the small fix at columns 4 and 5, and the left-up thresholds get the mirrored fix, so both classes should now send the ball the right way on every column.

Checking the left-up row-8 thresholds at column 5 against the K-case target of 3: with the paddle at 6, the left-moving unit should still fire, so the cutoff has to sit just below that.

Checking the right-up thresholds at column 5: with the K-case target at 5, the paddle at 4 should still send the ball right, so the right-moving cutoff there needs to sit at 4.

Now I'm checking the down-class rows against the same wall and paddle cases, and I'm double-checking that the row-8 fix for columns 4 and 5 still gives the right direction at column 6.

Now I'm thinking through how the R-catch changes the phase, where the paddle lands on the ball's spot and the ball retraces its path. I'm checking whether the pre-window approach from the right side still holds near q=1, and whether the K-case margin of 4 with a ±2 offset keeps the sigmoid-like unit firing cleanly on each side of the threshold.

I'm checking the gate magnitudes next: the off-state pre-activation stays at or below about -66, and the on-state margins come out to about ±0.964 after the layer-2 scaling, so the gating should hold.

Now I'm setting up the weight tables for the policy network, working out the constant arrays for the right and left cases and the per-row values for the remaining columns.

Writing the weight tables for unit 0...

Now I'm filling in the lookup tables for unit 0, which follow the same pattern as the earlier rows.

Still filling in the row 7 values with the same scaling and offset pattern...

Still filling in the row 5 lookup values for the second unit...

Still writing the weight tables for the hi-side unit...

Still filling in the hi-side values for unit 1...

Still working through the Row 5 values for the hi-side unit, where the offsets step up across the columns...

Still working through the Row 8 lookup values for the hi-side unit, where the offsets keep stepping up across the columns...

Still working through the unit 1 values, checking the hi-side table for row 8 where the trail and paddle offsets combine.

Still working through the lookup tables for the left-down unit, filling in the rows of the lo-side values.

Still writing the lookup rows for the left-down unit...

Still writing the lookup rows for the left-down unit...

Still writing the lookup values for the left-down table, with the Row 8 entries continuing the same offset pattern...

Still writing the unit 3 lookup tables...

Still writing the lookup rows for the down-right unit...

Still writing the lookup rows for the hi-side unit...

Still writing the hi-side weight table for the left-down unit...

Still working through the Row 8 lookup values for the left-down unit, where the offsets keep stepping across the columns.

Still writing the lookup tables for the unit 4 right-up side...

Still working through the lookup rows for the unit 4 table, the remaining columns and the row 8 tweak.

Still working through the unit 4 weight values, filling in the remaining rows of the right-up table and the row 8 adjustment.

Still verifying the row 0 through row 2 lookups against the unit 4 offsets...

Still working through the unit 4 lookup values, filling in the row 3 through row 5 entries with the same offset pattern.

Still working through the row 6 and row 7 lookup values for unit 4, applying the same offset and scaling pattern.

Still working out the lookup values for unit 5, the right-up side, applying the same sign flip and offset pattern to each row.

Still working through the unit 5 lookup values, applying the same sign flip and offset pattern to the remaining rows.

Still working through the unit 5 lookup values, applying the same sign flip and offset pattern to the remaining rows.

Still working through the unit 5 lookup values, applying the same sign flip and offset pattern to the remaining rows.

Still working out the lookup values for unit 6, the left-up side, with the row 0 and row 1 entries now in view.

Still working through the unit 6 lookup values, filling in the row 3 through row 8 entries for the left-up side...

Still checking the unit 6 offsets for row 2, where the lookup values shift across the columns.

Still checking the unit 5 offsets, now working through the Row 5 lookup entries for the left-up side...

Still checking the unit 6 offsets for the remaining rows, working through the row 6 and row 7 values against the left-side constants.

Still working out the lookup values for unit 7, the left-up side, where the offsets are negated before the constants are added.

Still working out the lookup values for unit 7, with the left-up offsets applied row by row...

Still computing the row 3 values for the left-up unit, working through the offsets and the trailing columns.

Still working through the row 6 lookup values for unit 7, where the offsets step down across the left-up table.

Still writing the row 8 lookup values for unit 7...

Still filling in the trail offsets for the remaining row 5 entries...

Still filling in the trail-based lookup values for the left-down unit...

Still working through the trail-based lookup tables, filling in the right-up rows for units 4 and 5.

Still working through the lookup values for the LU units, where the trail and base offsets line up row by row.

Still working out the trail weight tables, checking that the pairs of units match and whether a 2D block assignment is workable or if each column needs its own statement.

Now I'm checking the reset-left state end to end, starting with the ball at row 3 column 0 and the paddle at position 4, and I'm testing unit 4 first.

Still checking the unit 4 and 5 results at ball (3,0), and I'm confirming that the remaining units stay off with the paddle offsets applied.

Still checking the reset-right state now, with the ball at row 3 column 9 and the paddle at position 4, starting with unit 6.

Still checking the state-C case: with the ball at (8,6) and the paddle at 5, I'm testing units 4 and 5 against their lookup values.

Still checking state D: with the ball at (8,5) and the paddle at 5, the left-up unit fires, matching the left target.

Still checking the state-C and state-D cases by hand, now testing the unit 4 trail value at ball (8,4) for the reset-left state.

Still checking the trail-based unit 6 case at ball (8,3), where the paddle at 4 gives a right-firing value.

Still checking the state-C and state-D cases by hand, now testing the unit 6 and unit 7 results at ball (8,4) for the right-up and left-up states.

Still checking the zone case for the right-down unit at ball (7,4), where the paddle at 5 sits inside the stay band.

I'm checking the unit 1 values at ball (7,4), where the paddle at 6 keeps it in the stay zone and the paddle at 7 pushes it to fire left. Now I'm weighing whether to refine the design with the spare hidden capacity, looking first at the tight-flight and stuck-cycle cases under the final policy.

Now I'm checking the trickiest case, a flight after a right-side catch. I'm tabulating the distance from the paddle to the next landing spot for each catch position, starting with the first few.

Now I'm tabulating the distance from the paddle to the next landing spot for each catch position, checking the tight case at q=9 where the landing cell wraps around and the distance is largest.

Now I'm checking the tight-flight case, where the landing spot sits nine cells from the paddle and the wrap-around makes it the longest gap.

Now I'm checking the tight-flight case again, and I'm questioning whether the same-row hit from above at row 2 is handled correctly, since the ball would land one row higher than I'd assumed.

Now I'm checking the top-row trail cases for the up-moving ball, where a same-row hit at row 3 means the ball is truly moving up from row 4, and I'm working through the trail values for that class.

I'm checking how the up-moving ball's trail gets classified for each row, and working out how many moves it takes to reach the next landing, including the wall bounce at row 0. I'm also wondering whether a ball moving up through row 1 could run into a brick while the strike window is open.

I'm checking whether going upward from row 3 to row 2 could pass through a brick, which it can't after a hit from below since the ball reverses to moving down, but it can after a hit from above. So the upward pass-through only matters in that case, and the timing assumption holds. Next I want to confirm that row 4 moving up should use the n=5 count.

Still writing out the layer 2 weights, where the even-indexed units feed the go-right output and the odd-indexed units feed the go-left output, with a fixed scale and bias.

Now I'm settling the output layer: the two output units get a scale of 20 each, with biases that keep the no-op choice at zero when neither fires, so the right-or-left choice is close to certain.

I'm checking whether any brick-free orbit can loop forever under this policy: with the K-catches and free flights, the phases shift by two each flight, so the ball covers every phase in its parity class. I'm now testing whether each cell is reached from one of its parity combinations.

I'm confirming that every cell gets covered: each one has two parity-matching combinations of the ball's horizontal and vertical phases, so both parity classes reach it. Under the K-catch flights the phases walk through all ten values in the class, and the combined cycle of 180 steps visits every matching pair, so any remaining brick gets hit within that window.

I'm checking whether the policy can ever get stuck in a brick-free loop: after each K-catch the next landing sits two cells over, so the paddle arrives early on the far side and catches it. Near the walls the paddle reaches its target a bit differently, so I'm setting those edge cases aside for now.

