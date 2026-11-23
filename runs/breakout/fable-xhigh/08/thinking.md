I'm setting up a hand-designed policy network for MinAtar Breakout, starting from the game's dynamics. The state is the ball's position and direction (four diagonal options) plus the paddle's row, with a trail marker for the last position. Each step the paddle moves first, then the ball advances, and if its x-coordinate would leave the board, I clamp it and flip its horizontal direction.

I'm working out the collision rules at the paddle row: if the ball would reach row 9 and the paddle is under its current x or its next x, the vertical direction flips, and the corner case at the wall gets the same treatment. The plan is to keep the paddle under the ball's predicted landing spot, since the ball moves one column per step and the paddle moves one as well.

I'm checking whether a paddle that only trails the ball's x can keep up, given the paddle and ball both move one column per step, and that sticky actions will force some slack. The starting case is the key one: from x=0 the ball reaches row 8 at x=5, so the paddle needs to be at 5 or 6 on the next step, and it's currently at 4.

Checking the start cases again: from x=9 heading down-left, the ball lands at x=4 after five steps, and the paddle is already there. Next I'm weighing whether to predict the landing column directly or just track the ball's x, and which choice is easier to express with a small tanh network.

I'm weighing whether tracking the ball's current x is enough, since the ball's x can stay put when it bounces off a wall.

I'm checking whether lagging the paddle by one column still works at the critical moment. If the paddle sits one step behind the ball and then moves onto the ball's current column, the ball's next step lands on row 9 in a column the paddle already covers, so it only bounces vertically and keeps its horizontal direction. That means tracking the ball's observed x with a one-step lag is enough.

I'm thinking about using the trail to predict the ball's next x, since that's 2*ball_x - last_x, but walls complicate it. When the ball sits at the wall right after bouncing, its direction is ambiguous from position alone until it moves off the wall again.

I'm checking the edge cases at the walls and after brick hits. When the ball bounces off a brick, it keeps moving horizontally while its vertical direction flips, and the same holds for a paddle bounce with both directions reversed.

I'm checking how the trail marker settles the direction after a paddle bounce: if the paddle sits under the trail's column, the ball keeps its horizontal direction, but if the paddle sits under the ball's current column, the ball reverses. So the trail alone doesn't fix the direction here, and the paddle position has to settle it. I'll keep the tracking simple and robust, since the sticky actions can make the paddle lag.

I'm checking whether simply tracking the ball's current x holds up. If the paddle trails the ball by one column in steady motion, it keeps moving the same direction and stays aligned, but the sticky-action repeats could cause a misstep whenever the ball changes direction off a wall.

I'm checking the paddle's position relative to the ball's predicted column at the moment it reaches row 8. If the paddle sits one step behind and moves in the ball's direction, it lands on the right column, but if it stays put it misses, so the ideal is to hold the paddle directly under where the ball will be.

I'm weighing a predicted-landing policy, where the paddle goes to the column the ball will occupy at row 8, but computing that reflected landing point inside a small tanh network looks awkward. A simpler option is to aim for the ball's next column, taking the current ball x plus its horizontal direction.

I'm using a linear target of 2*ball_x minus the trail's x, so the paddle steers toward the predicted next column using only weighted sums of the inputs. The wall case at x=0 gets clamped, so the paddle just stays put there, and once the ball sits still at the wall with the trail matching it, the paddle holds.

I'm checking how a wall bounce affects the lag: after the ball reverses at x=0, the paddle ends up one column behind, so the clamped linear target doesn't fully fix it. I'm considering whether special terms for when the ball and trail share a column at the wall could push the paddle toward the returning direction.

The ball spends the round trip between paddle hits going up to the bricks and back down, so there are roughly nine steps for it to drift sideways before the next paddle contact. That means the paddle only has to be right at the moment of impact, not the whole time the ball is in the air.

I'm comparing two targets for the paddle: aiming at the ball's current column, or at the column one step ahead. Holding the paddle one column behind the ball works in a straight run, since each sticky repeat of the same move still lands on the ball's column at impact.

I'm tracing the wall-bounce case: the ball goes down-left along the wall to x=0, bounces, and heads back out. Tracking the ball's x with a one-column lag still gets the paddle onto the right column at impact, as long as the sticky repeat of the previous move doesn't push it off the wall.

I'm checking the wall case again: a ball bouncing off a brick only flips vertically, so horizontal direction changes come from the walls and paddle hits. Next I'm following a ball coming down-left to x=0 at row 8, where the wall bounce flips its direction before the paddle step, and working out what column the paddle needs to cover at that moment.

I'm checking that a lag of one column is still safe when the paddle follows the ball in a steady run, since the repeated sticky action keeps it aligned. The trouble comes when the intended action changes, because a sticky repeat of the old action can push the paddle the wrong way. I'm also following the ball as it travels toward the wall at column 9.

I'm checking a lag-one tracker against the sticky actions: if the paddle sits at the wall when the ball has just bounced, the repeated no-op lets the gap widen to two columns. From there the paddle stays behind, and at the critical step the ball's column gets missed.

I'm realizing that a lag of two columns is fatal at the critical moment, and the only thing that closes the gap is a wall bounce, since the ball briefly holds still there. Sticky repeats make each change of intended direction a small chance of slipping, so the tracker's reliability depends on how often the paddle has to reverse.

I'm weighing a second strategy: predict where the ball will land and move there early, then hold with no-ops. Arriving early gives slack for sticky repeats, though a move that was already in progress can overshoot by a column when I switch to a no-op.

I'm noting that the sticky-action rule means the executed action repeats the previous one with probability 0.1 per step, so a streak of repeats can stack up. That makes the paddle's lag risky, and a landing-prediction policy that parks the paddle early and holds with no-ops looks more robust. What remains is working out how to compute the landing column with wall reflections inside a small network.

I'm working out what the landing column depends on: ball x, ball y, and the horizontal and vertical directions. For a ball falling toward row 8, its column follows a folded path that bounces off the walls with a one-step pause, so I can express it with a reflection formula. Predicting upward-moving balls is harder, since the brick layout would matter, so I'm setting that aside.

I'm estimating how much slack the paddle has: the ball needs about 8 − y0 steps to drop back to row 8 after a brick hit, so the paddle has to cover the gap to the landing column in that window. If it has been tracking the ball closely on the way up, the gap is only one or two columns, which is tight but possibly workable.

I'm weighing a "target the landing column" tracker against one with a lead, where the paddle sits at b + dx and holds there with no-ops. In steady state the paddle sits right under the ball each frame, so the sticky repeats mostly cost nothing, and I'm checking whether leading the ball during the ascent leaves enough slack for the descent.

I'm checking a target of b + dx: if the paddle sits one column behind the ball, it still reaches the ball's column at impact, and one column ahead it only fails if a sticky repeat pushes it further. That gives roughly one slip of slack. I'm about to follow the case where the ball's column matches the paddle after the bounce.

I'm checking what happens after the bounce: the trail marker makes it look like the ball is still heading the old way, so a naive estimate would push the target two columns past the ball. Tracing it forward, the paddle ends up trailing the ball by two columns as the ball climbs back up.

I'm running through the case where the ball goes all the way down-left to the wall, checking whether the paddle's lag still works out as the ball climbs back up and returns.

I'm working through the case where the ball is at row 8 with the trail also at row 8, meaning it just bounced off the paddle. Whether its direction reverses depends on whether the paddle sits under the ball's x-coordinate at that moment.

I'm weighing whether a paddle that sits at the trail's column, rather than the ball's, would let the direction carry on, and I'm noting that the observation right after a bounce already shows where the paddle was, so the reversal is determinable from the state. I'm also considering whether to sidestep the issue by aiming for the lag-one position, though I'm not yet sure which of the two approaches is more reliable.

I'm considering whether a linear readout can produce a target that depends on both the ball's position and its direction. The ball and trail one-hot encodings give a sum of position-dependent terms, so the direction would have to come from the difference between the ball and trail positions.

I'm checking whether a single linear readout can encode the target, since the ball and trail one-hots only add position-dependent terms. The direction would have to come from the gap between ball and trail, but the vertical motion flips the trail's row, so the same trail cell means different things going up versus down. That conflict is what I need to resolve.

I'm testing whether the additive form A(ball) + B(trail) can cover both directions, since the same trail cell is consistent with the ball being above or below it. Taking the downward case, the target works out to b(9−y) − tx(7−ty), which fits the form. The upward case needs a different coefficient, and that's where the two readings conflict.

I'm seeing that a single linear readout can't cover both directions, since the coefficients on ball and trail don't sum to 1 in the upward case. The fix would be to spend some hidden units on detecting whether the ball is moving up or down, and let those units switch between the two target formulas.

I'm now sketching the hidden layer: threshold units on linear functions of the input, with down-mode comparisons of the target against the paddle at a few cutoffs. Layer two would combine those with AND/OR-style gating, and the output is a linear readout over that.

I'm weighing whether a single linear readout can handle the folding at the walls: the unfolded target needs a reflection, which isn't linear in the inputs. That pushes me toward giving each ball-and-trail pair its own additive term, with the down-moving case treated separately.

I'm checking whether the ball's trail can be matched cell by cell: for each row, the paddle offset has to work for both ball directions, and I'm testing whether a single additive assignment of values to ball and trail positions covers every case.

I'm checking the bipartite structure of the additive decomposition: each ball position b links to the trail positions b−1 and b+1, with the wall cells linking only inward. That chain is what determines whether the two one-hot terms can be solved for separately.

I'm checking the bipartite structure of the additive decomposition: each ball position links to two trail positions, and the wall cells link only inward, so the whole thing forms one cycle of twenty unknowns. With twenty equations on that cycle, the system is short by one, and solvable only if the alternating sum of targets around the loop vanishes, which I doubt holds generically. I still have one free parameter to play with before deciding.

I'm trying to handle the wall bounce by splitting the hidden units on direction, so the horizontal step can be read off from the ball-trail gap. The trouble is the edge cells: when the ball sits at column 0, a trail at 0 means it's moving right while a trail at 1 means it's moving left, and a plain difference can't tell those apart without an extra correction term.

I'm checking whether a single signed expression in the ball and trail columns gives the horizontal direction, with a correction at each wall so the edge cells read correctly. Then I'll need to handle the paddle-bounce and brick-bounce frames separately, since there the direction isn't fixed by the positions alone.

I'm weighing whether a simpler, more robust policy would beat the fully exact additive construction. Typical RL agents on MinAtar Breakout score only around 10 to 50, while a perfect policy could clear hundreds of bricks within the step cap, so staying robust to sticky actions matters most.

I'm working out the paddle's safe positions for the critical step: if the ball is at column b and moving with direction dx, the paddle has to end up at either b or the clamped next column. I'm also sorting the two outcomes by which case the paddle lands in, since each case sends the ball back up with a different horizontal direction.

I'm thinking about where the paddle should sit before the ball arrives: the two cells {b, b+dx} are both safe landing spots. If the paddle is already on one of them and can hold still, an intended no-op is fully safe, so the plan is to reach a landing cell early and wait there.

I'm weighing a safer approach: if the paddle reaches one of the two landing cells early and stays put, a no-op is safe even with sticky actions. Approaching from the x8 side and stopping there, an overshoot still lands on x8+dx, which is inside the safe pair, so only a repeated sticky action would push it out.

So the plan is to stop the paddle once it enters the two-cell zone, so a single overshoot still lands safely. A failure then needs two sticky events in a row, and only when the arrival is too late to correct. The harder part is timing: after the ball turns downward at a brick, the paddle needs to already be near the landing spot, and the paddle moves at the ball's horizontal speed. To judge that, I need to trace where the ball goes during its upward phase after leaving the paddle.

I'm working out the timing: if the ball leaves the paddle at x0 going direction d, it reaches the brick row and comes back to row 8 after a known number of steps, so I can compute the folded column where it will arrive for the critical step.

I'm now looking at how the ball's path changes after it turns back down, since the landing time depends on which brick it hits and whether it bounces off the top wall. The paddle only gets to see the ball descending for part of that trip, so the timing is not fixed.

I'm checking what happens after a brick bounce: the ball can turn back down from a brick, or it can hit a brick from above while moving down, which flips it upward again. So the row alone doesn't settle the vertical direction, and the paddle bounce is the only case where row 8 means the ball is headed up.

I'm checking the top-wall bounce: when the ball rises to row 0 and flips, the trail lands on the same row with a horizontal offset, so I'd treat that as a downward ball. Upon first seeing the ball turned at row 4, I still have four steps before it reaches row 8, and I'm working out the column it will land in.

I'm checking how many moves the paddle gets before the critical step: the observations at rows 4 through 8 give five actions. If it's already at the turn column and tracking the ball, it has one spare move. A lagging paddle would have none, though a constant-direction run carries no sticky risk.

I'm settling on a lead-tracking rule where the paddle aims L cells ahead of the ball in its direction of travel, since it then moves at the ball's speed and changes direction only at walls or paddle hits, which keeps sticky-action risk low.

I'm settling on a lead of one cell, so the paddle moves at the ball's speed with a constant action. A lag of one cell is still safe, and being one cell ahead is safe too as long as the intended action is a no-op.

I'm checking whether L=2 works: the paddle would end up at b+2dx, which is outside the safe pair, so it fails at the critical step. I'm now considering a zone rule instead, where the paddle stays put if it's already inside [b, b+dx] and only moves when it falls outside, which would give a steady pattern with a constant action.

I'm comparing the two tracking rules now: the zone rule can absorb one slip ahead, while the exact L=1 rule can absorb one slip behind. The main risk I want to check is the ball changing direction, starting with the wall bounce where its x-coordinate stalls at 0 for a step before reversing.

I'm tracing the paddle's pre-move positions as the ball bounces off the left wall, where the target clamps to 0 for two frames. In that stretch a sticky action is harmless, since it's clamped at the edge, but when the ball turns back right the paddle stays behind and has to catch up.

I'm checking whether the paddle can recover a one-cell lag at the walls. When the ball pauses at the edge for a frame, the paddle catches up by one cell, so the slip gets absorbed there.

I'm checking the paddle's sticky-action risk at the paddle-hit reversal: a sticky repeat there would leave it two cells behind the ball, which makes the next wall-bounce case the one to watch.

I'm checking the sticky-action case right after a paddle bounce: if the repeated action pushes the paddle two cells past the ball, it ends up two cells behind in the new direction. I'm considering whether a later wall bounce can recover that lag before the next landing.

I'm checking the paddle's lag after a wall bounce: with the ball pausing at the edge and then reversing back toward the paddle, a lagging paddle catches up to sync, so the lag resets at each wall. Then at the paddle hit, where the ball reverses, I'm weighing the action change there against the sticky-action risk.

I'm checking whether a lag of two cells after the paddle hit can be recovered before the next landing. The ball has at least nine steps to return to row 8, and if it reaches a wall during that stretch, the paddle gets back in sync.

I'm checking the edge case where the ball starts at x=9 moving left: it reaches the wall exactly at the critical step, so a paddle two cells behind fails there, while one cell behind still works. Since a wall bounce usually resets the lag, the question is whether that rescue happens in time.

I'm checking the two bounce cases near the landing. If the ball comes down the left wall and turns right at row 8, a paddle at 0 can still catch the new-x hit at 1 or the old-x hit at 0, so both are safe. If the ball is at (1,7) and reaches 0 at row 8 moving left, the paddle has to be at 0 by the critical step, so I'm tracing where it needs to be one step earlier.

I'm checking the paddle's sticky-action risk at the far-side bounce: if the paddle is one cell behind when the ball reaches (0,7) and then (1,8), a repeated no-op leaves it stuck, but a subsequent slip could still put it at the wrong cell for the critical step.

I'm weighing the remaining death odds at roughly 1% for the specific bounce configurations, and I'm estimating the survival from that. I'm about to define the target as an exact function of the observations so I can work out how to implement it in the network.

I'm writing the target as two times the ball's x minus its next x, so the paddle moves toward that point. At the wall the target clamps, and on the second frame of a bounce it stays put until the ball moves off the edge.

I'm testing a target of 2b minus tx against the paddle, which works in the normal case but leaves the paddle one cell behind after each wall bounce. A wall term would fix the bounce at 0 but would break the case where b is 1, so the correction has to depend on both the ball and the target together.

I'm adjusting the target so the ball's column gets a small offset at the edges: the left wall counts as 1 instead of 0, and the right wall as 17 instead of 18. That way the paddle no longer falls a cell behind after each wall bounce.

I'm checking whether a wall-adjusted target, with the ball's column offset to 1 at the left edge and 17 at the right, handles the bounces exactly. Next I'm going through the brick-bounce frames, where the trail gives the horizontal direction and the target stays at b+dx, and then the top wall and corner cases.

I'm checking the corner case where the ball moves from (1,1) to (0,0) and both walls bounce it, so the direction changes to down-right. At (0,0) the target evaluates to 1 with the adjusted column value. I'm also checking the initial frames at the left and right edges, where the target comes out to 1 and 8.

I'm re-deriving the paddle's lag after a new-x hit: the linear target would have it trail the ball by two cells, which I'm checking against the tracking rule.

I'm working through the lag-2 case: if the paddle sits two cells behind the ball, it only resyncs once the ball hits a wall and comes back, so a trajectory with no wall bounce before landing would be fatal. I'll simulate the ball moving left from that state to see whether a wall bounce near row 7 saves it.

I'm simulating the ball's path from the left edge with a lag-2 paddle: it tracks leftward, reaches the wall, and with the adjusted target the paddle lands at column 1 just as the ball arrives at row 8, so the new-x hit is safe. I'm still checking how a sticky action on that final step would change the outcome.

I'm weighing a fix for the paddle-bounce frame: if the paddle is already under the ball, the ball must be heading back toward where it came from, so the target should point back to the trail side. Otherwise the usual rule holds, and I'm checking whether that removes the lag-2 problem near the walls.

I'm testing whether the paddle's target should flip sign when the paddle is already under the ball, since the linear rule points the wrong way there. I'm trying a scaled difference in the trail row, but the first check fails: when the paddle sits on the trail cell, the correction has to be different from when it sits on the ball cell.

I'm trying a combined target, d' = b + tx - 2p, for the paddle-bounce frames in row 8. When the paddle already sits on the trail cell, this gives the right sign for the horizontal step, and when it sits under the ball it points back toward the trail side.

I'm now weighing a combined target, d = 2b - tx - p, against one that depends on whether the trail is in row 8. The ball's weight has to stay near 2b for the critical frame, so the row-8 correction can only act through the trail and paddle terms.

I'm checking whether one linear rule can handle the paddle-bounce frame in both cases. Whichever way the ball came in, the terms can't separate the two cases: the sign needed when the paddle sits on the trail cell conflicts with the sign needed when it sits under the ball.

I'm looking at a lag-1 tracker as an alternative: the paddle stays one cell ahead of the ball so new-x hits happen in the old-x direction and the linear rule stays consistent. The catch is that a wall bounce would force an action change with no slack behind, so I need to check whether that slips into a lag-2 state.

I'm checking the lag case after a new-x hit: the paddle ends up moving the wrong way, so it drifts further behind the ball. I'm weighing that against the exact tracker, where the wall bounce only costs one cell of slack.

I'm checking the lag-2 risk after a new-x hit: if the paddle slips on that frame, it ends up two cells behind the ball. Walls usually rescue that, but hits near the edge with a brick far up could leave no bounce in time, so I'm weighing a mixed approach at the hit itself.

I'm weighing whether the paddle should aim for a predicted landing spot during the descent instead of just following the ball, since a descent lasts several frames and gives time to position early. The safe landing cells are the ones the ball could reach at row 8 and the step after, so I want a target that keeps the paddle inside that set.

I'm weighing whether the paddle should head for a predicted landing spot during the ascent, since the ball can't be outrun and the paddle only arrives in time if it's already positioned ahead. Wall bounces are where prediction pays off, because the paddle can skip following the ball to the wall and back. So the question is where the paddle should sit at the moment the ball turns downward.

I'm estimating where the ball would land if it bounces off a brick at each possible row: the number of frames to reach row 8 depends on the hit row, so the paddle's target should be the fold of the ball's column after that many steps.

I'm working out whether the paddle can lag the ball without an early wall bounce to rescue it. The paddle can't move faster than the ball, so tracking exactly is always enough, and any prediction only buys robustness. The real issue is managing slack, since wall bounces are where the paddle can gain ground by cutting the corner.

I'm reasoning about whether the paddle can stay "ahead" of the ball in unfolded coordinates, since a lead of k steps would let it absorb k slips. But the lead only helps if it stays small at the critical step, and standing still would erode it, so the paddle has to keep moving at ball speed to hold the lead.

I'm considering a plan where the paddle heads for a predicted landing spot during the descent and waits there, since that keeps it still at the critical moment. During the ascent I'd need some lead-ahead target instead, maybe assuming the ball turns at row 4, and I'm working out how that could be implemented in the first layer.

I'm checking how the paddle's target should depend on the ball's cell and the trail cell for each descent row, since the ball and trail positions pin down the direction. The pairs that matter are the ones where the two differ by one column, plus the wall cases, and I need one consistent rule across all of them.

I'm parametrizing the ball's state as a single phase on a 20-step cycle, where moving right gives phase equal to the column and moving left gives 19 minus the column. Each step advances the phase by one, and the visible column is the fold of that phase, which should let me check the wall transitions directly.

I'm writing out the phase mapping for the 20-step cycle: moving right gives phase equal to the column, moving left gives 19 minus the column, with the wall cases at 0 and 10. From there I'm checking which trail positions go with each ball position, and I'm planning to express the landing cells as folds of the phase plus the remaining steps down to row 8.

I'm writing each row's pair of position values as a sum of an ascending term and a trail term, with the target set by the landing cell. The catch is that these same values get reused by the ascending case and the bounce frame, so the two modes would constrain each other unless a gate separates them.

I'm considering a gate in the first layer: a term proportional to the vertical difference between ball and trail, so the descending-mode unit only fires when the ball is actually falling. That would keep the ascending and bounce cases from sharing constraints through the same weights. I'm also weighing whether a second-layer AND gate would be simpler to implement.

I'm adding a gate to each mode: a term proportional to the vertical gap between ball and trail, so the descending comparison is switched off whenever the ball isn't actually falling. That keeps the three cases from sharing weights, and the OR in the second layer combines them.

I'm working out the cycle structure: each row is its own independent 20-step loop, with the ball states alternating against trail states. Before I can pick consistent targets, I need the alternating sum around that loop to come out to zero.

Now I'm tracing the alternating cycle of ball and trail states around the loop, stepping through each edge and its phase value.

I'm tallying the ball-state edges around the cycle, where the even phases all carry a plus sign and the odd phases a minus, so the consistency condition reduces to checking that the sum of the targets over the even phases works out.

I'm checking the alternating sums around the cycle: the even phases add up to 45, and so do the odd ones, so the consistency condition holds for the landing target fold(φ+n) regardless of n.

I'm checking the n=1 case next: the additive split A(b) + B(t) should give the next landing column, with A running 1, 2, 4 up to 17 and B(t) = -t. For the interior right-moving states that works out to b+1, and for the left-moving states it gives b-1.

I'm solving for the additive terms around the cycle, splitting each landing target into a ball term plus a trail term for general n.

I'm checking the constraint for the rows closer to the top. Setting n to 0 through 4 covers the rows nearest the paddle, and I'm thinking about whether the descent from higher rows could also be covered once bricks are gone.

I'm checking whether the ascent and descent constraints can be kept separate with a gate on the vertical gap, and whether that covers the higher rows, where the ball takes longer to land and precision matters less. I'm still weighing whether to compute all nine rows or use a simpler approach for the upper ones, since the paddle still has to end up near the right spot.

I'm weighing how to encode the weight matrix for the multiple units, since each unit's column needs its own explicit values. Writing row-wise slices for the ball and trail entries plus the paddle term adds up to a lot of numbers, so I'm checking whether a 2-D block assignment would let me fill several columns at once.

I'm weighing how to fill the weight matrix for the descending-mode units, since each unit's column needs its own values. Filling a single input across several units at once, or scaling a finished column, could cut down the number of statements I have to write.

I'm now checking whether the ascending target can reuse the same additive ball and trail weights, since the three cases would share one set of values and only the pairing would change.

I'm working out the ascending case now: the ball rising from row 7 with the trail at row 8, where the trail's weights are still free since no descending frame uses them. The constraints for the ball's column pair with the row above, so the ascending target is pinned by the descending system rather than chosen separately.

I'm working out the ascending-mode target for the lower rows, and a simpler row-independent tracking formula could cover those cases with fewer weights to write.

I'm checking whether the landing-prediction part of the descent is even needed, or whether a simple tracker that follows the ball's column would do. I'm estimating how often that tracker would lose the ball, going through the wall-bounce and paddle-bounce frames to see where the action has to change.

I'm checking how a wall bounce interacts with the paddle's sticky slips: the intended left, neutral, and right actions can each get replaced by the previous action, so the paddle can fall behind by one or more cells after the bounce. That gives about a 10% chance of lagging by one cell, and roughly 1% for two.

I'm checking how the paddle lag plays out after a wall bounce: a slip can leave it one cell behind, and the next bounce brings it back into sync. A direct reversal from right to left at the second bounce is handled by the paddle stepping back toward the ball.

I'm checking the paddle-hit case: if the paddle's slip repeats its previous move right after a hit, it ends up two cells behind the ball, about a 10% chance each time. That lag is only recovered if a wall bounce comes before the ball lands, which isn't guaranteed.

I'm checking the lag-2 case after a paddle hit: if the wall bounce happens at the right moment before landing, the paddle can still catch up, but if the bounce comes too late or never comes, the paddle ends up two cells short. I'm about to enumerate when the ball returns to row 8 after the nine-step cycle.

I'm checking where the left-wall bounce falls in the cycle: if the hit happens at x0 ≤ 7, the wall's first frame comes early enough for the paddle to catch up, but at x0 = 8 the timing is off by a step, so I'm counting the steps carefully from the hit through the brick bounce to the critical landing.

I'm checking the x0 = 9 case, where the hit lands on the right wall. There the lag-2 paddle would be at 1 rather than 2 after the slip gets clamped, so the earlier death estimate doesn't carry over directly, and I need to recompute how far the paddle falls behind at that point.

I'm checking the case where the paddle hits the ball near the right wall: after the hit the paddle is one cell ahead and a slip only leaves it one cell behind, so the lag stays at one. With the row-3 bricks still intact, a lag of two after a hit seems to get recovered by a wall bounce every time, but I still need to see how longer flights after bricks are gone change that.

I'm checking whether a wall bounce can re-sync a paddle that's two cells behind, since a bounce in that state brings the paddle back toward the ball's column.

I'm checking whether a death is even possible: the lag-2 paddle only fails if no wall bounce happens before the ball lands, and for any flight length that would need the ball to start at the very wall. Working through the cases, the only candidate is the clamped right-wall hit, which leaves the paddle one cell behind rather than two, so the failure seems to never actually occur.

I'm considering whether a pure linear tracking rule would be enough, since after a new-x hit it only costs one step of lag, and a wall bounce should catch the paddle back up. The remaining worry is that a wall bounce's own slip could leave the paddle one cell behind again.

I'm re-checking the lag-2 rescue for a hit near the left wall: with the ball moving right and the paddle stepping onto column 1, the reversal leaves the ball heading left-up from there, so I need to confirm the wall timing still works out in that geometry.

I'm checking whether a lag of one cell is safe, and it looks like it is, since the linear tracker only falls behind after a new-x hit and the walls catch it back up. The real remaining risk is a double slip, which I'll come back to. For old-x hits with the paddle already one cell behind, the rule just keeps moving in the same direction, so there's nothing to change there.

I'm working through the wall-bounce timing for the lag-1 paddle: with no action changes while moving steadily, the only change comes at the wall, where the slip gets clamped and the lag stays at one. A second slip is what would push the paddle to two cells behind, and I'm estimating that at about 1% per wall bounce.

I'm estimating the death risk after each wall bounce: a lag-2 paddle only dies if a landing happens before the next wall bounce rescues it, which works out to roughly 0.8% per bounce.

I'm checking the wall-bounce rescue for a lag-2 paddle: the wall timing has to be traced frame by frame, with the paddle's pre-move positions lined up against the ball's.

I'm working out the wall-bounce timing for the lag-1 paddle, where the ball's frames at the wall determine whether the paddle falls behind. A double slip is the only way to reach lag 2 there, which I estimate at about 1% per bounce. I'm now considering whether the paddle could cut corners near the walls to build some slack.

I'm considering whether the paddle can lead the ball by a larger margin while the ball is high and then shrink that lead to one as it nears row 8, so there's slack before the landing. The lead has to end at one or less on the landing frame, but it can be bigger earlier in the descent.

I'm weighing whether the paddle can lead the ball more while it's ascending, since the landing row isn't known yet. If it aims for the earliest plausible landing, then once the ball passes row 4 I'd know the brick row is at most 2, so the target can shift by two steps.

I'm weighing whether the paddle could target the earliest plausible landing during the ascent, since a brick bounce at row 3 gives the shortest flight and any later turn only adds steps. I'm considering a simple heuristic: assume the ball turns right away, so the target is where it would land if it descended now, and see how that holds up if the ball keeps rising for a few more steps.

I'm working out how far the paddle can lead the ball during the ascent, since a landing would then come after two more steps of travel for each further step the ball rises. The paddle can only move one cell per step, so I need to check whether it can still reach the landing spot in time once the ball turns.

I'm working out the slack the paddle gets when it leads the ball by k cells: with n+1 moves available before the landing check, a lead of k still leaves about k cells of margin to reach the landing spot. I'm about to check what happens once the lead grows past n+1, since then the paddle has to move a lot more than the ball's remaining frames allow.

I'm weighing a lead of about 9 minus the ball's row during the ascent, since a bounce at that row leaves roughly n+1 spare moves for the paddle to correct any offset. The slack stays largest when the lead is close to n+1, and it shrinks as the lead drifts away from that value.

I'm working out how the paddle's lead should grow during the ascent: the target moves two phase steps for each step the ball rises, while the paddle can only move one, so a naive lead would keep slipping. The only place the paddle can gain ground is by cutting corners at the walls.

OK, so a paddle at position x can match the ball's phase in two ways, at x and at 19 − x, which means "lead" isn't one fixed number. I'm checking the turn frame directly instead: with n steps left before row 8, the paddle needs to be within n+1 cells of the landing spot.

I'm weighing a predictor that targets the exact landing cells during descent, with the paddle stopping once it's inside that zone. During the ascent I'm considering either the same tracker with a slightly larger lead or the plain lead-one version, which is where I'm at now.

I'm pondering whether a larger lead during the ascent helps: more lead means more spare moves once the ball turns, so I'm considering a lead of about five or six cells while it's still rising.

I'm checking whether the paddle can build a larger lead by moving backward against the ball's direction. Since it moves at the same speed as the ball in phase terms, it can't gain ground by simply following, so I'm looking at whether the wall folding gives it a way to shift ahead.

I'm testing a case where the paddle starts at the ball's column and moves right with it, reaching the target only after a few steps. Once it catches the target, it's about five cells ahead, so it can turn back toward the wall and bank that lead by cutting the corner.

I'm checking whether the lead-of-five idea holds during the ascent: if the paddle tracks the ball in sync, it stays feasible, and the lead only grows when it catches the target and cuts back at the wall.

I'm checking whether a lead of five cells stays safe during the ascent, and I'm concluding that it does, since at the turn frame the paddle needs at most the spare moves it has. The remaining worry is the wall fold, where one position corresponds to two phases, so I need to check how the paddle picks the shortest path to its fixed target.

I'm now thinking about the ascent case: the target would be the landing cell at lead L, which depends on the row, so maybe a larger lead near the top wall, since the earliest possible turn there leaves the most frames to correct.

I'm working out the ascent target for a ball at row 5 that's still going up: a turn could only happen at row 4, so the landing prediction shifts by one more phase step, giving a lead of about seven cells.

I'm checking the landing prediction for when the ball reaches row 8, assuming it bounces off row 3: from row y it takes y+1 steps, so the landing cell is offset by y+2 phase steps from the current phase. That gives the same mirror-like result once the ball is at the top wall.

I'm settling on how the paddle's lead should look during the ascent, with the landing prediction shifting by the row the ball is on. If the ball is at row y going up, I'd assume it turns at row 3, which puts the landing two phase steps past the current phase plus y. Checking the numbers, that lines up with the lead I had at row 4 and gives a smooth step from one frame to the next.

I'm settling the ascent target by how high the ball is: for rows 4 and up I use a lead of 6 plus the distance above row 4, and for rows above that the lead is 10 minus the row, assuming an immediate turn. At the top wall the next frame's bounce gives the same value, so the lead stays consistent across the whole ascent.

I'm checking whether a large lead is actually achievable, since the paddle has to reach the target using only the moves it can make. For a ball that just bounced at x=2 and is heading right, I'm testing whether the paddle can keep pace with the target as it shifts.

I'm checking whether the paddle can stay ahead of the ball's landing spot on the way up. The worry is cases where the ball lands sooner than I predicted, so I'm testing how early a turn could happen from each row.

I'm checking whether a strike could make the ball land earlier than my prediction: if it breaks a brick and bounces right away, it could turn sooner than I assumed. The bricks only regenerate when the ball reaches the bottom, so I'm working through whether that changes the timing for an ascending ball.

I'm checking whether two brick strikes in a row can happen, which would need the ball to bounce off a brick and immediately land on another one in the next row. The cases I'm testing are a ball moving down past a partially cleared row 1, since that's where a second hit could line up.

I'm checking whether a strike could make the ball land earlier than predicted. A ball going up through a brick row can pass through one without bouncing and keep moving, and a descending ball that bounces off a brick only lands later than my estimate. So the free-descent prediction still looks like the earliest possible landing in every case I'm testing.

I'm checking whether a later landing is safe: the paddle should already be near the earliest landing spot, and any delay of an even number of steps means it has at least that many spare moves to reach the new spot.

I'm checking the paddle's tracking gap at the bounce frame: the target sits at phase φ4 + 14 − 2y_t, while the paddle has only reached φ4 + 11 − y_t, so I need to see how much ground remains to close.

I'm checking the spare moves at the bounce frame: the paddle still has a gap of 4 − y_t cells against a budget of 9 − y_t moves, leaving 5 spare. Even if the paddle only tracked the ball at lead 0, it would still have exactly enough moves to reach the bounce target. So I'm settling on one policy for all three cases, where the target is fold(φ + L) and the paddle just steps toward it.

I'm weighing whether the paddle should aim for x9 or x8 at the critical frame. Aiming for x9 means any arrival leaves the previous and intended actions consistent in direction, so it's safe either way, whereas aiming for x8 risks a sticky old-x hit.

I'm checking the case where the paddle arrives early and waits at the target, then the ball hits and reverses; the paddle's next target is recomputed from the bounce frame. The other case is the paddle coming in from beyond the target: it overshoots onto the neighboring cell, which is still inside the safe zone, though the rule would then pull it back.

I'm weighing whether the zone logic is worth its cost: it needs separate comparisons against both x8 and x9, so the descent case would take four comparison units. I'm asking whether an early arrival that overshoots to a neighboring cell actually causes a problem often enough to justify that.

I'm weighing whether a paddle that arrives early and overshoots by one cell can recover in time, comparing an approach from the x8 side against one from the far side. Aiming for x8 instead would keep an overshoot inside the safe cells.

I'm settling on zone logic for the critical frames: the paddle stops as soon as it enters either of the two safe cells, so a one-cell overshoot still lands somewhere safe and never needs a correction. The cost is extra comparisons, so I'm checking whether the unit budget of 32 in layer 1 can cover it, and whether ascent needs the same treatment or just an approximate target.

I'm checking whether the ascent target can be written as one formula, fold(φ + L), with the same comparison units used on the way down. The 20-step cycle works out to the same total for even and odd phases, so the sums stay consistent.

I'm checking whether one shared set of comparison units can cover the descent, ascent, and bounce cases, since each brick row's values get reused across all three and the equations don't all fit together. That overlap makes it look like each mode will need its own separate unit, gated by the current mode.

I'm setting up the descent "right" unit so its pre-activation is K·(T − p − 0.5) plus a gating term M·(y − ty − 1), which pushes it strongly negative whenever the ball isn't descending. For the "left" unit, I'm mirroring that with the sign of the comparison flipped.

I'm folding the row-index terms into the weights: the gate adds M·y to the ball-row weights and subtracts M·ty from the trail-row weights, and those cancel out in descent. Rather than leave them as separate gating terms, I can absorb them into the per-row numbers, which is cleaner to implement.

I'm now settling on separate layer-1 comparison units without gating, with a second layer doing the AND, since that seems cleaner. Then I'll turn to the paddle-bounce frame, where the ball and trail are both in row 8, and work out how paddle position resolves the direction when the hit is ambiguous.

I'm working out the bounce frame, where the ball and trail are both in row 8 and the paddle's position decides the direction. If the paddle sits at the trail's x, the ball keeps its old direction; if it sits at the ball's x, the direction reverses, so the phase becomes 19 minus the original. The target then comes from shifting the phase by 10 and folding it back into the cycle.

I'm working out the bounce frame's target: the mirror position 9 − b is the same whichever way the ball is moving. The zone cells, though, depend on direction, since the nearby cell sits at 9 − b + dx.

I'm now considering whether the ascent target should also be a single point, x9, computed from the phase plus the lookahead for the row. If the paddle parks on x9 during ascent, it's already inside the safe zone when descent begins, so I don't need a zone for ascent. In the bounce frame, the mirror position 9 − b works out to the same target regardless of direction, which is a useful coincidence, though it only holds for that particular lookahead.

I'm sorting out the bounce frame, where the ball and trail both sit in row 8: the target there works out to 9 − b − p, so it depends only on the ball's column and the paddle. The row-7 ascent frames need the trail-row-8 term too, so I'm checking whether one ascent unit can carry both cases with consistent weights.

I'm checking whether the row-7 ascent target reduces to 9 − t, which would force a fixed weight on the trail-row-8 term. That conflicts with the bounce frame's requirement, so the bounce frame's ball-column term would have to absorb the difference.

I'm checking the bounce frame against the ascent unit's weights: if the target is set to 9 − t, it comes out as x9 plus the trail's offset, one cell past x9 on the side away from x8. So the bounce case doesn't fit cleanly into a single shared ascent unit.

I'm checking whether one frame of error is acceptable: for the bounce frame the paddle could briefly head the wrong way before correcting on row 7. Since the ball's flight gives about ten moves and the worst-case distance to the mirror target is nine, there's only one spare step, so I'm weighing whether dithering here actually matters.

I'm working out the bounce frame separately, with gating on the trail and ball both sitting in row 8, since the target there is 9 − b − p and the ascent unit can't carry it cleanly.

I'm sorting out the paddle-bounce frame with its own pair of comparison units, gated on the ball and trail both sitting in row 8. Their pre-activation is a scaled offset 9 − b − p, with a gate term that pushes them strongly negative whenever the ball isn't in row 8, so they stay clear of the ascent units. That leaves two units for the bounce frame and two for ascent, and I'm about to gate the ascent pair by the vertical direction.

I'm now sorting out the remaining frames where the ball stays in the same row as its trail, which covers bounces off bricks and the top wall. Each of those needs its own per-row weights, so I'm checking whether they can be folded into the descent units or need to stay separate.

I'm checking the same-row frames, where the ball and trail sit in one row, to see whether their target can come from the descent units' weights. The trail's row weights seem to carry over from the row below, so I'm testing whether that reuse holds.

I'm working through the general solution for the lead-L case, with a closed form for the per-row terms on the cycle.

I'm extending the unknown functions to all integers with the fold's reflection symmetry, so the equation A(x) + B(x−1) = F(x+L) holds uniformly across both travel directions. The symmetry about −0.5 and 9.5 should let one closed form cover both phases.

I'm requiring the two symmetry-extended functions A and B to satisfy the shifted relation, and reflecting x to −x gives a second equation that pairs A(x−1) with B(x) against the mirrored target.

I'm checking whether a single sum over shifted fold values can satisfy the difference equation A(x+1) − A(x−1) = F(x+L+1) − F(x−L−1), which would give a closed form for A on the cycle.

I'm checking that the alternating sum A(x) = F(x+L) + F(x+L−2) + … + F(x−L) is symmetric under x → −1−x, since F(−1−z) = F(z) makes the two sets of terms match.

I'm checking the closed form on a few values: for L=1, A(x) = F(x+1) + F(x-1) gives 1, 2, 4, and 17 at the points I tested, and B(x) = -x matches the earlier lead-1 solution. So the general pattern holds.

I'm working out the lead-L solution for each row, taking the descent case first: for ball row y with the trail in row y−1, the x9 target uses lead 9 − y and the x8 target uses lead 8 − y, with y running from 1 to 8.

I'm considering whether a constant lead for the ascent frames would work, since that would let every row share one set of twenty weights instead of a separate table per row.

I'm weighing a constant lead of 6 for the ascent frames: it keeps the paddle about six cells ahead of the ball, so it moves steadily instead of waiting, and the target converges on the ideal spot by row 4.

I'm considering how the paddle should respond to a constant lead of 6 near the walls, where the target pauses for a step, and I'm checking that the one-cell lag this creates still leaves enough slack. Then for the rows below the brick band, I'm comparing that fixed lead against the ideal value, which falls from about 10 down to 7, to see how far the paddle would lag at the moment of a bounce.

I'm checking whether the constant lead of 6 still holds for the paddle-bounce frame, where the ball has reversed direction. The ascent unit would decode the phase the wrong way there, so I'm weighing whether the spare steps are enough to absorb that.

I'm checking the worst case for the paddle-bounce frame: if the ball hits the wall at column 9 and the paddle has to reverse, the remaining moves could run short by one.

I'm weighing whether to treat the paddle-bounce frame separately, with its own target of 9 − b, since reusing the ascent units would cost spare steps on interior hits.

I'm deciding whether the bounce frame can just be a no-op, since that wastes at most one move and avoids any wrong-direction steps. The tight case is when the ball hits the wall, where the spare time looks like it could drop to zero, so I'm checking the target zone for that specific configuration.

I'm weighing whether to act in the bounce frame itself rather than waiting. A no-op there would leave zero spare moves in the wall case, since one slipped action would be fatal, so I'm leaning toward a proper bounce-frame target of 9 − b.

I'm simplifying the descent case: rather than tabulating a separate lead for every row, I'm thinking about whether one set of tables per lead value, L from 0 to 8, can cover it, since the x8 table for one row matches the x9 table for the row below.

I'm checking whether the descent case can be reduced further, since the lead-L tables look like they repeat across rows, and I'm testing the antisymmetry relation A_L(9−x) = 9(L+1) − A_L(x) as a way to halve the stored values.

I'm considering whether the rows above the bottom band even need exact predictions, since a paddle already riding a lead of about five should be in position by row four. So I'm testing a capped lead of min(9 − y, 5) for descent, which would leave only rows four through eight needing exact tables.

I'm now settling on a split for the descent case: lead 5 for the x9 target and lead 4 for the x8 target, applied uniformly across the rows instead of tabulating each row separately. I'm also sketching the mode check from the row change, treating the ball as descending, level, or ascending, and I'm about to work out what zone to aim for in the rows above the brick band.

I'm settling on one table per lead value so the descent tables can be shared across rows: the ball at row y lands on the same pattern whether I read it from the descent frame or the same-row frame. That means B's indexing has to follow the ball's row, not the trail's, so the same-row and descent cases stay consistent.

I'm checking whether one set of tables can serve both the descent and same-row frames, since the B table for a given row would then have to match two different lead values. That conflict shows up most clearly at row 4, where the brick-bounce frame is the most common turn. I'm wondering if forcing the lead to stay constant across rows 4 and 5 would remove it.

I'm weighing whether same-row frames can simply reuse the ascent unit with its constant lead, since that avoids giving them their own table and removes the row-4 conflict. The trade-off is that the ascent unit would be gated to fire on same-row and ascending frames, except at row 8.

I'm settling on a constant lead of 5 for the ascent unit, which also covers same-row frames, since at row 4 that target is exactly right. Higher bounce frames will lag by a few cells, so I'll let the descent unit take over once the ball starts falling. The paddle-bounce frame at row 8 needs to be excluded from this unit.

I'm checking the paddle-bounce frame against the ascent unit, which uses a constant lead of 5 and so would also cover that case. For a hit on the paddle's own cell, the phase matches, but the fixed target sits five steps short of the ideal mirror point, so I'm testing whether it still moves the paddle in the right direction, starting with a ball at column 3.

I'm checking the paddle-bounce frame at row 8 against the ascent unit's lead of 5: the target lands a few cells off the ideal mirror point, but the paddle still moves the same way for most phases. A few cases go the other direction, so I'm tracing the paddle's path through a run of ball positions to see whether it converges.

I'm checking the special case where the ball and its trail sit in the same cell at column 9 and row 4, which gives phase 10 and a zero mode. The paddle's path from 4 to 5 to 6 to 7 and back to 4 is longer than needed, but every move keeps enough slack to still reach the landing spot in time.

I'm checking whether a constant lead of 5 for the ascent table still holds up in the paddle-bounce frame when the hit lands on a new cell, since the fixed target sits a few steps short of the ideal mirror point.

I'm checking the paddle-bounce case where the ball reverses, since the apparent and true phases differ. With the ball at column 5 and the paddle there too, the constant-lead target sends the paddle right when the ideal mirror point is to the left, so I'm tracing the next frame to see whether it recovers.

I'm checking the paddle's path after the reversal: the ball is moving left from column 4, and the constant-lead target keeps the paddle trailing it by about two cells while the target sweeps back toward the centre. I'm tracing the next few frames to see where the paddle and target meet.

I'm checking the paddle's path through the wrong-direction first move and the later frames, where the constant-lead target sweeps back toward the brick-bounce point at row four, and I'm working out where it settles.

I'm checking the wrong-direction case where the ball was hit at column 1 by a new-x reversal. The constant-lead target still points the paddle the correct way there, by luck, and I'm now looking at the mirror case near column 8.

I'm checking whether using the ascent unit in the paddle-bounce frame causes trouble in the tight cases, since a constant target might pull the paddle the wrong way there.

I'm checking the wall cases next: at column 9 the ball and trail share a cell, giving phase 10, and the L5 target is 4, so the paddle moves left as it should. At column 0 the target is 5, moving right, which is also correct.

I'm confirming that a top-wall bounce frame, where the ball is same-row and now descending, still works under the constant L=5 table, since the paddle has plenty of time to correct the remaining gap of about four cells. Then I'm turning to the brick-hit frame where the ball starts ascending.

I'm checking the opening frames: with the ball starting at column 0 or column 9, the constant-lead target still puts the paddle in a landing zone that the ball reaches. Then I'm weighing whether the descent units should aim at a single target or a zone of two cells, since the paddle tends to arrive early and wait.

I'm checking whether a single paddle target for the descent units holds up when the paddle arrives early and has to wait, since a slip could push it one cell past the landing spot. Repeated slips would need several in a row, so the risk only matters when there is little spare time, which is the tight case I'm looking at next.

I'm working through the paddle's position for the last-moment arrivals now. If the paddle is already on the landing cell when the ball arrives, any of the three target choices keeps it safe, since a single wrong move still leaves it on a neighbouring cell the ball can reach. The risky case is when the paddle is one step behind, and I'm checking whether every target choice still covers it.

I'm testing the paddle's response in the two zone cases, where it steps onto the landing cell and where it's one cell short, and checking whether a slip would knock it out of the safe range.

I'm weighing whether a single target at x9 is riskier than the zone, since arriving at x9 from behind and then having to hold still means a slip in the last frame could push the paddle off the landing cell.

I'm comparing the single-target options against a zone of two cells for the last-moment arrivals. Each single target seems to carry about a 10% death risk in one of the early-arrival scenarios, while the zone logic drops that to roughly 1%, so the zone looks more robust for those cases.

I'm looking at the paddle's position one frame before the critical arrival, where it sits one cell ahead of the landing zone. Staying put under the zone logic, with the previous move still carrying over, is the case I'm checking for a slip.

I'm weighing the zone approach against single targets for the descent units: with a single target at x9, a one-frame-early arrival can leave the paddle exposed to a slip, while the two-cell zone keeps that risk around 1%. The catch is that the zone needs four comparison units, R8, L8, R9, and L9, each with tables for the ball and trail rows.

I'm considering a midpoint target m = (x8 + x9)/2 instead of two separate comparisons, since the two zone cells are usually one apart. When they differ, m lands halfway between them, so the paddle's distance to m tells me whether it's inside the zone or not. When they coincide at the walls, m is just that single cell, and the threshold separates in-zone from out-of-zone the same way.

I'm folding the two zone cells into one midpoint table, so the descent needs only two units, one for each direction. The threshold sits at 0.75 cells, with the midpoint values at 0.5 and 1 on either side. Ascent and same-row cases will keep two units with a constant lead-5 table and an exact threshold at 0.5.

I'm weighing whether the ascent units should also use a zone: averaging the two cells that the moving target spans would keep the paddle riding the trailing edge, so a single target of lead 5 is the simpler alternative I'm comparing it against.

I'm checking whether the ascent units can keep a single lead-5 target when the paddle arrives early at the bounce frame, since the paddle should ride the trailing edge of the moving target and then sit inside the descent zone with time to spare.

I'm weighing a constant lead of 4.5 for the ascent, which would put the paddle in the descent zone at the bounce frame. I'm checking whether a lead of 5 instead lands the paddle on the right cell on the last ascent frame, so it's already in position when the ball turns.

I'm comparing a constant lead of 6 for the ascent, but it pushes the paddle one cell past the landing zone at the bounce frame, so it would have to move back during descent. A lead of 5 avoids that back-and-forth, and I'm now checking whether a zone-style ascent with a 4.5 midpoint and a 0.75 threshold does any better.

I'm settling on a single lead-5 target for the ascent units, since a constant offset keeps the paddle on the trailing edge of the moving target and lands it at fold(φ_b + 4) at the bounce frame. That's a simpler integer table than a zone, and it avoids the back-and-forth a lead of 6 would cause.

I'm settling on a single lead-5 target for the ascent, and now I'm checking how that plays out in tight timing cases where the paddle starts far from the target. After a hit at x_h, there are ten frames before the landing at phase φ0 + 10, so I'm checking whether the paddle can reach the landing zone in time when it moves toward fold(φ + 5) throughout the ascent.

I'm checking how the paddle fares in tight timing cases, tracing the frames from the bounce at φ0 through the descent to the critical row. I'm considering what happens when the paddle starts on fold(φ0) versus fold(φ0 − 1), since the starting offset decides whether it can catch the target in time.

I'm checking whether the paddle can always reach the landing zone in time when it tracks the target by lead 5, including cases where the ball's x-motion makes the shortest path differ from simply following the phase. I'm working through one case where the paddle is already on the target and the ball reverses, to see if it still catches up.

I'm checking whether the paddle can still reach the landing zone in time: each step it closes on the target at up to speed 1, and the target's x-motion can only slow that down, so the gap can't grow. Starting from at most 5 to 7 cells away, I'm tracing what the gap looks like when the bounce frame arrives.

I'm checking the distance condition at the bounce frame: the paddle needs to close within five moves, and from a lag-0 start the gap is at most five cells, so it can still reach the landing zone in time.

I'm checking the spare-move margin for each case: with the paddle lagging zero, it has one move to spare at the bounce frame, but a lag-one start leaves none, and a wrong-way first move only works if the target folds somewhere in the flight.

I'm checking whether the paddle can keep up when the ball's x-motion folds: a fold pause lets it gain a cell, but if the target never folds during the ascent, the landing spot stays fixed, so I'm measuring the paddle's x-distance to that spot directly.

I'm checking whether the paddle can still reach the landing zone if the ball's phase never folds during the ascent, since then the landing spot stays fixed and the paddle has to cover the x-distance directly. The fold pairs limit how long such a stretch can run without a pause, so I'm working out which starting phases would even allow it.

I'm checking the starting phase with lag 0: at φ0 = 10 the paddle sits at fold(10) = 9 and has to reach the single zone cell 0, which takes 9 moves against 10 available, leaving one spare. A lag-1 start gives the same 9-move distance since fold(9) = fold(10), so the walls still leave at least one move to spare.

I'm working through the tightest case: a wall-to-wall flight where the ball leaves x=9 heading left at phase 10 and lands at (0,8). The paddle has to cover nine cells in ten moves, so I'm stepping through the targets frame by frame, with the paddle shifting left from 9 toward 4 before the bounce frame.

I'm checking the worst case, where the ball crosses the full width, and the paddle has to cover nine cells in ten moves. Moving left every step reaches the zone in time, with the last move landing as the ball arrives. The only risk is a slip on the first move, which would cost one cell.

I'm working out how often the wall-hit case comes up, and the mirror pattern from one bounce to the next sets the hit positions, so I'm tracing how the phase shifts with each hit.

Now I'm checking the paddle's state after a hit: it sits in the zone {x8, x9}, landing at x8 means the ball continues with the paddle one step behind, and landing at x9 means the ball reverses with the paddle on the true phase. Both cases look fine. I'm also weighing whether the descent rows above row 4 can share one table with a constant offset, instead of needing separate ones for each row.

I'm now sorting out the descent tables, using a constant offset for rows 4 and above so they can share one table. For each ball row from 8 down to 5 I need a zone table paired with a trail-row table, and rows 1 to 4 will fall under the same pattern.

I'm now building the lookup tables for the descent, with the zone and trail tables for each ball row, and rows 1 through 4 sharing one pair of half-step tables. Next I'm computing the base tables A_0 through A_5 and B_0 through B_5, starting from the fold function F.

I'm writing out the lookup formulas for the two tables: the A table sums the fold values at steps of two around x, and the B table is the negated sum of the offset set. I also see that B_L is just the negative of A_{L-1} shifted to match, which should let me reuse the same computation.

I'm tabulating A_1 for each x by adding the fold values at x+1 and x-1, starting with x=0 and working up through the lookups.

Now I'm tabulating the second-order sums for A_2, taking each x and adding the fold values at x+2, x, and x-2. I've got the first few entries so far, starting from x=0.

Computing the next row of the lookup table, A_3, by summing fold values at x+3, x+1, x-1, and x-3 for each x.

Now I'm tabulating the A_3 values across the row, summing fold terms at steps of three and one, and checking the wall-clamped entries as I go.

I'm filling in the next row of the lookup table, A_4, by summing fold values at steps of four, two, zero, and negative two and four for each x. The first entries come out to 10, 11, and 13 as I go.

I'm filling in the next lookup row, A_5, by summing fold values at steps of five, three, one, and so on down to x-5 for each position.

Now I'm working through the A_5 row, summing the fold values at steps of five, three, one, and the negative steps, checking the first few entries as I go.

Checking the last column of A_5 by summing the fold values at steps of five, three, one, and the negatives, the sums come out to 29, 33, 36, 38, and 39 across the row, with the pairs adding to 54 as expected.

I'm checking the trail-table shift on a few sample positions, where the ascent target is fold(8) = 8 from b=3, t=2 and the difference of the two tables comes out to 8 as expected.

I'm spot-checking the ascent table against a few more positions, with paddle and ball pairs at the edges and middle, and each difference matches the expected target, so the table holds up.

Now I'm setting up the descent zone midpoint for each ball row, using the average of two adjacent tables, and I'm doubling it to keep the arithmetic in whole numbers. I'm defining a sum S_L that combines the base table values at L and L+1.

Next I'm writing out the sums S_0 through S_3 by adding the adjacent base tables, such as A_0 plus A_1 and A_2 plus A_3, so I can get the descent midpoints in whole numbers.

Computing the midpoint sums for the descent zones, I'm adding adjacent base tables so each ball row gets a whole-number value. Next I'm working through S_3 across the board.

Now I'm checking the descent sums against the ball-row-8 case, using the trail term of minus t, and testing a rightward move at b=3 where the midpoint comes out to 7.

Checking the descent midpoints for ball row 8 against a few positions, the sums come out right at b=3, 9, and 0. Now I'm setting up the row 7 check, where the ball term is S_1 of the ball position and the trail term is S_0 of the trail position.

Now I'm checking the descent pairs for ball row 6 and row 8, and the row 5 setup with the ball term S_3 and the trail term S_2.

I'm checking the descent midpoints for ball rows 5 through 4 against a couple of sample positions, and the sums match the expected x8 and x9 values. Now I'm testing the rows 1 through 4 case with the larger ball term and the trail term from S_3.

I'm folding the gating term into the descent unit, so that it contributes nothing when the ball moves down one row and is penalized otherwise. The remaining step is to choose a gate strength G that is larger than any |U| that could occur in the non-descent modes.

Now I'm settling the gate strength, working out the range of U in the non-descent modes so that G clears it. With a gain K of 8, the margin makes the unit saturate cleanly, so I'm setting the gate weight to 800 per row.

I'm switching the gating into layer 2 instead, so the layer-1 weights stay small: a mode unit D that is positive only when the ball moves down one row, combined with the descent unit's output through a tanh with gain 3.

I'm settling the layer-2 gating: a layer-1 mode unit D that is positive only for a one-row descent, and four AND-style units combining each directional unit with D or its negation. The output logits are then built from those four gates.

I'm setting the logit for moving right to w times the sum of the right gates plus one, so it sits at -w when neither gate fires and at +w when one does. The no-op actions can stay at zero, since they are all equivalent.

I'm checking that the soft gate weights hold up: with c = 5 the tanh outputs sit very close to ±1, so the layer-2 logits stay cleanly at ±w for the right-move decision.

I'm setting up the layer-1 units for the gate: a single mode unit D for the one-row descent, plus units that fire on each directional comparison. I'm weighing whether the gating can sit in layer 2 as an AND instead, which would need five layer-1 units with tanh gains around 8 to keep the comparisons sharp.

I'm checking the gating at the edges: with D at ±1 and the layer-1 comparisons saturated, the AND units come out near ±1 as long as the tanh gain is large enough to keep the off cases negative.

I'm checking the edge cases now: the ball is always visible and the trail is always present in channel 4, so the paddle weights sit at 540 + 6c in row 9. I'm also confirming that a descent step, where the ball moves from the trail cell down one row, is the only case that should make the descent unit fire.

I'm checking the edge cases for a descent step: a ball that bounces off the wall and lands on the same column still counts as moving down one row with the right direction. The paddle-hit frames stay on row 8, so they don't trigger the descent unit. Now I'm looking at the top wall, where the ball moves from row 1 to row 0 and that counts as an ascent.

I'm checking the edge cases for the same-row frames now: brick bounces, top-wall bounces, paddle bounces, and the initial frame all keep the ball on its row, so they should all get the ascent target. The descent unit only needs to fire on a true one-row drop, and the phase check holds for each case.

I'm checking the same-row frames against the paddle-hit and brick-bounce cases, and the ball's last positions tell me whether it's descending or ascending from that row. Bricks only sit in rows 1 to 3, so a bounce off one leaves the ball at row 4 or above, and the descent target at L=5 still lines up with the valid zones.

I'm now checking the edge cases for a descent step from the top wall: a ball that turns at row 0 and then descends through rows 1 to 4 falls in the riding zone with L=4.5, and only from row 5 down does the exact target apply. The paddle rides the fold in that range, and at row 4 the exact zone still holds, so the paddle stays in or near it.

Now I'm checking the paddle's moves along the zone's trailing edge, where the zone folds at the walls: R, R, then stay, then L, L. The ascent ride with the single L=5 target works the same way.

I'm checking the paddle-bounce case now, where the paddle hit reverses the ball's phase and the ascent target may send it the wrong way, and I'm working out whether there's still enough time to reach the zone.

I'm working through the paddle-bounce case: the true landing zone lands at phases φ8+11 and φ8+12 in apparent-phase terms, which mirrors the ascent target I'd been using.

I'm checking the paddle-bounce case against the true phase: after the hit, the paddle is still heading toward the wrong zone, and the ideal landing zone is mirrored to the other side. I'm working out how far the paddle has to travel from the hit position to reach it, since that distance sets how much time is left.

I'm checking the paddle-bounce cases by how far the hit position is from the mirrored target. The distance is 9 for the edge hits, and for the middle ones it shrinks, so I'm testing whether the paddle still has enough frames left to reach the zone after a wrong first move.

I'm checking the paddle-bounce cases with x_h = 8: if the ball arrives with phase 7 or 10, the paddle lands on 8 either way, and the reversed phase puts the mirrored target at cell 1. The ascent target of 3 still pulls the paddle left, in the right direction.

I'm checking the paddle-bounce cases with x_h at 1 or 8 by symmetry, and the wrong first move still leaves enough frames to reach the mirrored zone. Next I'm testing whether the paddle can still reach the L=5 ascent target by the row-4 bounce if it starts from a distance of about 5 or less.

I'm checking the paddle-bounce case where the hit lands at x=9 and the ball starts at 9 moving left: the target cells fall 3, 2, 1, 0, 0 over the next frames. If the first move goes the wrong way, the paddle starts about 6 cells away and has to chase the target as it shifts.

I'm checking whether the paddle ever has to move away from the final landing zone when time is tight. The L5 ascent target is fold(φ+5), and I need to confirm it always sits on the same side as the final zone relative to the paddle.

I'm checking whether the paddle ever has to move away from the final landing zone when time is tight. The L5 target and the final zone could land on opposite sides of the paddle, which would mean the ball folds back past it, so I'm working through whether there's still enough slack to recover.

I'm testing whether the paddle can ever be forced to move away from the final landing zone, since the ascent target and the zone might sit on opposite sides of it. If that happens, the paddle loses a step of slack each time it moves the wrong way, so I'm working out how many such moves could occur before it settles onto the target and rides along with it.

I'm checking how the paddle moves toward the L=5 ascent target before it catches that target, since once it's riding at lead 5 the remaining slack looks comfortable.

I'm checking whether the paddle ever drifts away from the final landing zone: when the ascent target sits on the opposite side of it, the paddle moves the wrong way and loses slack. I'm looking at the case where the paddle is already on the ball's path and the target is across the wall, which would force it to jump ahead of the ball.

I'm checking whether the paddle can keep up with the landing zone: the L=5 target stays on the same side as the final zone once the paddle is riding it, and before that, any wrong-way move costs at most a small lag that the remaining frames can absorb.

I'm confirming the paddle keeps enough lag margin at the bounce: if it's one step behind at the hit, the descent zone offsets still let it land in time, so the design holds.

I'm checking the lag case at the hit: the paddle sits one step behind the ball's phase, and if it keeps moving toward the target without shortcuts, it stays one behind until the target folds.

I'm checking the worst case at the wall: the paddle starts at 8, the ball at 9, and the zone lands on cells 1 and 0, leaving the paddle seven cells away with ten moves available. That leaves about three spare moves, so the bounce still makes it.

I'm checking the spare moves for the remaining bounce cases: with the ball at 9 and the paddle at 9, the zone is just cell 0, leaving one spare move. Shifting the ball to 8 gives two spare moves, and a paddle hit at 8 leaves four, so the slack never drops below one.

I'm weighing whether the paddle can improve its slack by choosing which zone cell to hit from. Sitting on the old-x cell lets the ball continue, while the new-x cell reverses it, and each option leads to a different next landing zone.

I'm comparing the two hit options by how far the paddle has to travel to the next landing zone. Sitting on the old-x cell gives a distance of min(|9 − 2·x8|, |9 − x9 − x8|), while a new-x hit measured from x9 gives a different distance to its mirrored zone.

I'm working out the distance from the paddle to the next landing zone for both hit options, and both come out to roughly nine cells with ten moves available. Neither option is clearly better, so I'll leave that choice aside. The ascending case in rows 5 to 7 looks fine, with the L=5 target not being the final one.

I'm weighing how tight the timing gets after each bounce: the first move can slip, and that only becomes a real risk when the paddle is nine or more cells from the next landing zone, which happens mainly on straight flights that hit near a wall.

I'm estimating how often the paddle would slip out of the zone while it's sitting still. Each cycle is dangerous only if the paddle is already lagging when it arrives, so I'm checking that the usual arrival timing leaves it safe.

I'm estimating the death rate per cycle: the tight cases, where slack is one move or less, come up in roughly 10% of cycles with a 1-2% chance of failure each time. That puts the expected run somewhere around a few hundred to a thousand cycles, so the 10000-step cap is reachable.

Now I'm writing out the output-layer formulas: the two layer-1 threshold units, the downward-move units, and the layer-2 combinations that mix them with the D gate.

I'm writing out the output logits now: the right-move logit combines the right-up and right-down gates plus a bias, and the left-move logit does the same with the left gates, with the other actions left at zero. I'm checking the sign cases: when a gate is inactive both terms sit near -1 and the logit comes out to -w, and when the up gate fires the logit goes to +w.

I'm checking the output logits against the gating: the right-move logit should come out near w when the ascent gate fires, since RD then sits near -1 and adds almost nothing. The no-op actions stay at zero, and the sign cases look consistent with what I expected.

I'm checking the descent lookup tables now, starting with row 8, where the ball's weights are 1, 3, 6, 9 and so on up to 26 while the trail's weights run negative across row 7. For the cases I've tried so far, the combined sums come out right: with the ball and trail both at 9 the sum is 17, and at 9 against 8 it's 18.

Checking the remaining lookup entries: for row 8 with the ball at 8 and the trail at 9, the sum comes to 15, and the ball at 8 against the trail at 7 gives 17. The low-column cases also check out, with the ball at 1 against the trail at 0 giving 3 and against 2 giving 1, and the ball and trail at 0 giving 1 and 0.

I'm checking the row 7 lookup entries now, starting with the ball at 0 and the trail at 0, which gives a sum of 3 once the fold positions are worked out. The ball at 0 against the trail at 1 comes to 1, so both low-column cases match the expected values.

I'm checking the row 7 lookup entries against the fold positions, and the cases with the ball at 1 and trail at 0, and at 9 and 8, both come out to the expected sums. Working through the mid-column pairs like ball at 5 and trail at 4 is next.

Checking the row 6 lookup entries now, starting with the ball at 0 against the trail at 0, which gives 5 once the fold positions are worked out. I'm also verifying the mid-range pairs in that row against the expected sums.

I'm checking the row 6 lookup entries, verifying the mid-column pairs like ball at 7 against trail at 6 and 8, plus the wrap-around cases near 9, and they all match the expected sums so far.

Checking the row 5 lookup entries now, with the ball at 0 giving a sum of 3 once the fold positions are worked out.

Checking the row 5 lookup entries against the fold positions, the ball at 0 against the trail at 1 comes to 5, and the ball at 6 against the trail at 5 gives 18, both matching the expected sums.

Checking the row 5 lookup entries against the fold positions, the pairs with the ball at 9 and the trail at 9 and 8 give sums of 11 and 13, both matching.

I'm checking the remaining row 4 lookup entries against the fold positions, and the cases with the ball at 0 against the trail at 1, and the ball at 5 against 4 and 6, all come out to the expected sums.

I'm spot-checking the last few row 4 and row 7 entries against their fold positions, and each one matches the expected sum.

Now I'm checking the descent threshold in the paddle-zone cases, and confirming the zone values work out when the paddle and ball columns differ.

Now I'm stepping the first few frames forward from the start state, checking the ball and paddle moves and the descent sums in rows 4 and 5.

I'm checking the row 5 entries against the fold positions and getting matching sums, so the descent logic holds through this stretch. I'm stepping the ball forward to the next cell, where it lands on the paddle's column and reverses to up-right.

Now I'm tracing the next few frames from where the ball lands at (6,8), checking the ascent sums against the fold positions as the paddle shifts right.

Now I'm checking the ascent sum at frame 9, where the ball has moved to (9,5), and the paddle shifts left to 5 as the ball heads up-left toward row 4.

Now I'm tracing a ball that lands on the paddle's column at row 8, so the paddle holds position at 4 and the ball heads down-left toward (7,5).

Now I'm stepping through frames 12 to 15, checking the descent sums in rows 5 and 4 against the fold positions, and each one stays within the no-op zone. At frame 15 the ball reaches (4,8) and the paddle holds at 3, so the ball heads up-right toward (3,8).

I'm checking the ascent sum at frame 16 against the fold positions, where the ball at (3,8) with the trail at (4,8) gives 1, and the paddle moves left. Then at frame 17 the ball has moved to (4,7), and the sum of 9 sends the paddle right to 3 as the ball heads to (5,6). I'm still tracing the next step at frame 18.

I'm tracing the ball's path frame by frame, checking each ascent target against the fold positions. At frame 20 the ball slips into the hole left by the broken brick and keeps climbing, so I'm continuing from (8,3) with the paddle already moving toward the target at frame 21.

Checking the ball's next step at frame 22: it sits at (9,3) with the trail at (8,3), and the paddle moves left to 5 to match the target. The ball then bounces off the right wall and heads down-right to (9,4), which has no brick. At frame 23 I'm checking the descent sum for the ball at (9,4) against its trail at (9,3), which comes to 9 and falls in the zone where the paddle stays put.

I'm checking the descent case where the ball at (9,4) with its trail at (9,3) gives a sum of 9 against the paddle's zone, so the paddle holds. The ball then drops through (8,5), (7,6), and (6,7) before it reaches the critical spot at (5,8), where the paddle's column matches and the old-x hit applies. I'm also thinking about whether the descent and ascent checks hold for every ball and trail pair near the walls, since those are the cases where the two cells can share a column.

Checking the wall bounce case next: the ball at (8,4) moving up-right hits a brick at (9,3) and reflects to (9,4), then flips horizontal direction at the wall, which stays consistent with the rule. I'm also confirming that the brick-clearing refill at row 9 is handled correctly, so the ball comes back to row 8 with the bricks restored.

I'm checking the robustness of the policy against slips during descent: if the paddle slips while already in the zone, the sticky action still keeps it in place. Then at frame 11, the bounce, the paddle moves left to 3 as before. At frame 12 a slip could push it out of the zone, and I'm working out how the next frame would correct that.

I'm working through the slip case: if the paddle slips three times in a row during frames 12 to 14, it ends at the edge and misses the ball at frame 15, which works out to about a 0.1% chance per cycle, so I need to decide whether that risk is acceptable.

I'm weighing whether to tighten the ascent targeting so the paddle reaches its final spot directly instead of wandering with the L=5 ride, since that would arrive earlier and leave more slack before the slip-risk window closes.

I'm weighing whether the paddle can keep riding in its current direction past the zone, since a slip there only costs a few cells and can be corrected in the frames left before the critical moment.

I'm working out the slip tolerance at the bounce frame: one slip keeps the paddle in the zone, but three consecutive slips push it out of reach by frame 15, about a 0.1% risk per cycle. Two slips can still be recovered in time, so the threshold is the same either way.

I'm working out how to tighten the ascent so the paddle arrives earlier: if the target stays fixed while the ball climbs from row 7 to row 4, the paddle can reach its spot sooner and sit there, leaving more slack before the slip-risk window closes.

I'm sizing up what a row-dependent ascent table would cost: I'd need the lead values for L = 6 through 9, plus a matching trail-row entry for each ball row, which adds complexity but stays manageable.

Now I'm working out the row-dependent ascent tables, where the ball rows 0 to 3 use one lead value and the trail rows carry the matching negative offset. I'm checking that the same-row case still gives a consistent target at row 3, where the leftover term for the ball in row 4 reduces to a single value.

I'm weighing a fix for the same-row case, where the bounce frame at row 4 would give a target one cell past the paddle's spot. I'm considering dedicated units gated on the same-row condition, or falling back to the descent zone logic there, since the shared ascent tables conflict.

I'm checking whether the descent unit can cover same-row frames at rows 1 to 3, since the ascent and descent lead values match there. Row 4 is the awkward case: the ball's entry uses one table while the trail's uses another, so the pairing gives a different target than I'd want.

I'm settling on a separate same-row mode, since the shared ascent tables give the wrong target at row 4. That takes two more layer-1 units, a same-row unit and its mirror, on top of the descent and ascent ones, so eight in total. The same-row tables are still being set up, indexed by ball row and trail row.

I'm working out the same-row case for rows 0 through 4 with a single table, where the ball and trail both sit in the same row, giving a target of S_4 minus S_3. For the paddle-bounce frame at row 8, I'll just aim directly at the mirror target of 9 minus b, since that's simpler.

I'm checking the ball-row-8 case with weights 18 − 2b and a zero trail term, which gives exactly one target, 9 − b, at the paddle-bounce frame. Then at the next frame, with the ball in row 7 and ascending, the ascent target of 9 lands on the same cell as the mirror target, so the two rules agree.

I'm weighing whether the ascent should use a zone or a single target. A zone lets the paddle stop at its near cell and guards against overshoot, but a single target at x9 might pull it to x9 while the zone's near cell is x8, and I need to check which of those costs fewer corrections.

I'm checking the overshoot case: if the paddle sits at x8 and the bounce-frame rule pulls it to x9, that's an extra move, but the zone still covers it. After moving to x9, a slip on the next frame could push it past the edge, and I'd have enough frames left to correct it.

I'm settling on a zone-based ascent target, since a single target at x9 would cost an extra move near the mirror frame. I'm also checking whether a simpler expression for the ascent target, tied to how many steps have passed since the paddle hit, could replace the full table of lead values.

I'm working out whether I can avoid tabulating every offset: the ascent target could come from the trail position alone at row 7, since the fold at that step reduces to 9 minus the trail x. For rows above that, the two-step-back position isn't directly available, so I'll need the tables after all. Before building them, I want to check whether the larger-L values follow from the antisymmetry and period, which would shorten the work.

I'm writing out the recurrence for the tables A_L, each term built from two terms two steps back plus a fold at x+L and x-L. Next I'll be filling in the F values from z = -10 upward.

I'm tabulating the next values of the ascent recurrence, starting with A_6 at x=0 and x=1. Each entry adds the two-steps-back term to the fold values at x plus and minus 6.

Now I'm filling in the next row of the ascent table, A_6, at each position from x=2 through x=9, and the list comes out as 21, 22, 24, 27, 30, 33, 36, 39, 41, 42 with pairs summing to 9.

Still computing the ascent table, A_7, one position at a time.

Still computing the ascent table, working through the A_8 values one position at a time.

Still computing the A_8 values, checking each position against the fold terms.

Now I'm finishing the ascent table, A_9, by adding the fold terms at x plus and minus 9 to the A_7 values, and the results come out as 45 for each position from 0 through 7.

Checking the ascent tables against the known pattern: the row-7 target comes out as 9 minus the trail position, and A_9 is constant at 45. Next I'm verifying the row-6 case with T_8 = A_8(b) − A_7(t).

I'm checking the row-6 and row-7 targets against sample states, and each one matches the fold formula. I'm working through the row-7 case for ball position 5 and trail position 4, where the value comes out as 37.

I'm checking the row-6 targets against sample states, and the values match the fold formula so far.

Working out the ascent targets row by row now: the row-7 case reduces to 9 minus the trail position, and for the rows below I'm pairing each ball-row table with the trail-row table one step back.

I'm weighing a constant lead of 6 for rows 0 through 3 against exact per-row values of 7 through 10, and the exact version fits the turn-immediately timing better.

I've got the ascent table for row 10 now: it comes out to 54 minus x, so the target at row 0 reduces to 9 minus b, the mirror value. Now I'm weighing whether the exact turn-immediately targets for rows 3 and below actually beat a constant lead of 6, since a hole in row 3 changes the target when the ball comes up through it.

I'm weighing whether exact turn-immediately targets for rows 3 and below beat a constant lead of 6. A constant lead would keep the paddle moving steadily in one direction, while the exact target shifts by two cells per step once the ball climbs, so I need to check whether it gets the paddle to the landing point sooner.

I'm checking the mismatch between the exact and zone-based targets for rows 2 and 3, since the paddle gets pulled back for a frame at the bounce before settling into the descent.

I'm checking whether the zone's lower edge would pull the paddle back at the bounce frame, since that could cost an extra move and a slip risk, but the paddle would still reach the final zone in time.

I'm making the descent and same-row targets exact as well, using the sums S_{8-y}(b) minus S_{7-y}(t) so the paddle's zone stays consistent through the bounce.

I'm defining the descent tables now, with each ball row y weighted by S_{8-y} and each trail row r weighted by -S_{6-r}, so the trail lookups line up one row behind the ball.

I'm defining the same-row targets as S_{8-y}(b) minus S_{7-y}(t) for rows 0 through 4, with row 8 using 18 minus 2b and the unused rows left at zero. For the ascent I'm setting the target as A_L(b) minus A_{L-1}(t), with L running from 6 at the middle rows up to 9 at row 7.

I'm settling on the ascent targets as a single value x9 for the rows above the paddle, since the row-3 turn can be handled by per-row L values of 6 plus the distance from row 4. I'm checking whether the tables for rows 0 through 3 need exact per-row values or whether a constant fits well enough, and the remaining question is how a hole in row 3 would shift the target.

I'm checking that the ascent target x9 stays consistent with the zone {x8, x9} used for the same-row and descent frames, since the previous ascent frame's target lands on the same x9 as the bounce frame. Once the paddle approaches x9 from the x8 side, it will pass x8 on the way, and I'm confirming that the timing still works out.

I'm weighing whether the ascent should use a zone like the other frames instead of a single target, since the paddle would stop at x8 and overshoot toward x9. A single target is fine here because any overshoot during ascent gets corrected with plenty of frames to spare, but a zone would keep the logic uniform across all the units.

Now I'm weighing whether the ascent should use a zone for rows 0 through 3 as well, since the same zone-style targets would cost no new tables. The paddle-bounce frame is the snag, because its direction is ambiguous, so I'll use the single mirror target there instead.

I'm checking whether a zone in the ascent would hold up near the walls, where the zone collapses to a single cell anyway. Then I'm weighing the overshoot case: with a single target at x9, the paddle arrives from the x8 side, and a 10% slip sends it one cell past, so I'm estimating how often that correction is needed.

I'm weighing whether the ascent should use a zone like the other units, since the same lookup tables already cover it. A zone would let the paddle stop at the near edge and absorb a slip without dithering back and forth, so I'm leaning toward using it there too.

I'm comparing whether the ascent should use a zone or a single target, and a zone seems better because it cuts down on dithering near the edge at no extra table cost. Now I'm considering whether to merge the descent, same-row, and ascent units, but each one weights the ball rows differently, so they have to stay separate.

I'm settling the weights for the descent and same-row units: ball rows 1 through 4 share the same weights in both, while row 0 only appears in the same-row case and rows 5 through 8 only in descent. I'm also going through the trail-row weights for each mode, since the ascent ones are indexed differently from the other two.

I'm working out the row-8 case, where the descent and same-row tables overlap. The ball-row-8 weight from the descent table doesn't match the same-row target of 18 minus 2b, so I'm checking whether a trail-row-8 weight can absorb the difference, since no descent frame ever has the trail in row 8.

I'm concluding that the three unit types can't be merged, since the trail-row weights conflict between descent and same-row, so I'll keep six separate comparison units, each with its own ball and trail tables plus the paddle values.

I'm weighing a different way to cut the writing down: a single unit per mode whose linear-regime output gets thresholded in the next layer, which would avoid writing separate left and right units.

I'm considering a tanh in the first layer with a small scale, so it behaves almost linearly near zero, and then using a second layer with a steep tanh to make the thresholds sharp. The cubic error stays small in the range that matters, so the two-layer version could replace separate left and right units.

I'm checking whether a single tanh unit per mode, kept in its near-linear range, can replace the separate left and right units, with a second layer doing the sharp thresholds. The open concern is whether the garbage values outside the valid frames stay under control.

I'm checking the precision of the layer-1 linear unit, where u = tanh(ε·v) with v an integer in [-18, 18] and thresholds at v = ±1.5. That should keep the nonlinearity negligible in the range that matters.

I'm settling on ε = 0.02 with a second-layer gain of 400, so the thresholds at ±1.5 in the integer domain land cleanly at ±4 after the sharpening.

I'm settling on a two-layer design where layer one is a near-linear tanh per mode, and layer two sharpens it into thresholds. Each mode gets a gate from a mode unit, with a strong penalty pushing the off-mode outputs toward minus one. I'm now defining the D and U mode units from the y and target differences.

I'm checking that the D and U mode gates saturate cleanly at their extremes, then laying out the layer-one units as five (the three linear units plus D and U) and the layer-two units as six, one per side for each mode.

Now I'm computing the remaining rows of the lookup tables, starting with the ball-position sums for the first few sets.

Double-checking the A_6 and A_7 rows by computing one T value directly.

I'm spot-checking a few more entries of the transition table against the fold formula, and each one matches: the b=3 and b=8 cases, plus the b=1 pairs, all come out as expected.

I'm running spot checks on the transition table, verifying a batch of entries against the fold formula for the b=6, b=2, b=4, b=5, and b=7 cases, and each one matches.

I'm verifying the remaining T_7 entries against the fold formula and they all match, so the A_6 and A_7 rows are confirmed. Now I'm starting the T_6 table, beginning with the b=0, t=0 entry.

I'm spot-checking the T_6 entries for b=1 through b=4 against the fold formula, and each one matches the expected difference.

I'm checking the T_6 entries for b=5 through b=8 against the fold formula, and each one matches the expected difference.

I'm checking the T_8 entries against the fold formula, starting with b=3 and b=9, and those match too.

I'm spot-checking the last few transition entries against the fold formula, the b=7 and b=2 cases, and they match so far.

Generating the lookup tables for the S sums...

Still filling in the sums for the S tables...

Still filling in the sums for the S tables...

I'm writing out the lookup table entries for the descent unit, pairing each ball row with the matching S sum and each trail row with a negated one.

Now I'm laying out the descent unit's lookup: each ball row y from 1 to 8 pairs with S of 8 minus y, and each trail row from 0 to 7 gets the negated S of 6 minus the row. The same-row unit follows the same pattern, pairing ball rows 0 through 4 with S values and trail rows with the negated S of 7 minus the row.

Still setting up the ascent unit's lookup, working through which zones each row falls into.

Still working out the ascent unit's lookup, matching the ball rows and trail rows to the right S values for the lower zones.

I'm checking how the ascent unit's zones line up at the boundaries: a turn at row 4 should match the bounce frame one phase later, and the row 7 landing zone should agree with the row 3 turn.

Checking the row-3 turn against the bounce frame one phase later, the zone comes out to the same pair of fold values, so the two rows agree. The top-wall bounce at row 0 lines up with the zone for the ascending case as well. Next I'm verifying the row-7 ascent entry numerically.

Checking the row-7 ascent entries numerically now, and the last few all match: the b=5 and b=9 cases, plus the b=0 case for the ball at the top of its path.

I'm double-checking the ascent row 0 entries numerically, and both match: at b=3 with t=2 and with t=4, the weights come out to 13 and 11. Before I commit to the three-mode design, I want to make sure I haven't made a typo in the assembly, since that is where errors are most likely to creep in.

I'm checking the same-row frames: they happen after a brick hit, a paddle hit, or a top-wall bounce, and for the starting cell. The starting check works out, with the ball at row 3 giving zone {5,6} and the mirrored position giving {3,4}, both matching the landing zones I already had. Now I'm moving on to the remaining pieces of the assembly.

I'm checking the paddle-bounce frame now: the zone is {x8, x9}, and a paddle already inside that zone only gets nudged to x9, which is harmless. I'm wondering whether a wider threshold would avoid that unnecessary move.

I'm working through the paddle-bounce frame and whether the mirror target of 9 minus b is the right threshold, and I've decided to keep the exact mirror, so the unit fires when 18 minus 2b minus 2p is at least 2. Then I'm moving on to the second-layer threshold implementations and the linear layer-one units.

Next I'm writing out the first-layer units: one for the descent mode, one for the same-row mode, and one for the ascent mode, each a tanh of its weighted sum of ball and trail terms minus twice the paddle position, with no bias. I'm also adding the down and up units as tanh terms scaled by k around the target row. The concern is that in the wrong mode these sums can get large, reaching about 89 in one case, so I'll need to keep that in mind.

I'm working out the threshold for the first second-layer unit: the tanh gate should switch on just past the midpoint between the two expected activation levels, which puts the cutoff at about 0.03.

I'm switching the design to a steeper tanh with ε = 0.05, which moves the midpoint threshold to θ = 0.075 and lets me set the second-layer gain to K2 = 200. With these values the margins on both sides come out near ±5, and the largest pre-activation of 18 only reaches about 0.72, so the scheme stays well-behaved.

Now I'm writing out the gating for the left-descent, right-same-row, and right-ascent units, each built from its tanh-scaled activation with the direction-mode terms subtracted, and checking that the same-row case nets to zero.

Still filling in the layer-2 weights and biases, working through which first-layer units feed each gate.

Now I'm writing out the output layer's weights, starting with the entries that feed the action units from the left-descent and right-ascent gates.

Next I'm fixing the output weights: the right-move logit gets a bias of 2w and a weight of w from each of the three right-side gates, and the left-move logit does the same with the left-side gates. With w = 20, an active gate gives a right logit of 20 against an inactive one at -20, so the no-op wins when nothing fires. I also want to make sure the two directions can't both be active at once, since they need v ≥ 2 and v ≤ -2 respectively.

Writing the mode-unit weights now: the descent-mode unit gets +k·r on the ball channel and -k·r on the trail channel for each row, with a bias of -10, and the ascent-mode unit is the mirror image.

Still filling in the first-layer weights for the descent unit, working through the ball-row sums by row.

Still entering the trail-channel values for the descent unit, row by row.

Checking the trail-channel values for the descent unit against the ball-channel sums, and confirming the paddle weights line up.

Checking the descent-row examples for row 3 now, working through the zone values for a few ball and trail positions and confirming each one comes out to the expected sum.

Checking the row-1 descent entries by hand now, with the ball and trail sums for the two cases I haven't verified yet.

Checking the row-1 descent entries by hand, I'm verifying the remaining ball and trail pairs against the expected sums, and they all match.

Still entering the unit-1 ball-row values, then starting the trail entries for the same unit.

Still entering the trail-channel values for the same-row unit, and checking the row-4 example against the expected sum.

Still checking the row-0 top-bounce frame, working through the zone values for the ball at row 4 and the trail at row 3 to confirm the sums match.

Now I'm writing out the first-layer weights for the up-ascent unit, starting with the ball-row values for each row.

Still filling in the ascent unit's trail-channel entries, checking the rows for the upward mode against the expected sums.

Still checking the ascent unit's trail entries row by row, confirming each pair against the expected sums.

Now I'm checking the ball at row 7 against the trail at row 6: the zone comes out to {3,4} and the sum to 7. Then on the paddle-bounce frame the mirror gives a move left, and the paddle steps to 4 before settling.

Now I'm checking the last few frames. On frame 8 the ball is at (8,6) with the trail at (7,7), and the sums come out to 7. Frame 9 and frame 10 both check out at 7 as well.

Now I'm checking the descent-mode unit's ball and trail entries for the remaining rows, confirming the paddle-bounce and critical frames all come out to the expected sums.

Next I'm double-checking the mid-layer thresholds with the ε = 0.05 scaling, where the pre-activations for the right-descent gate come out to about +4.9 when the mode is right and about -5 when it isn't.

Checking the tanh saturation on the mode units now: the descent pre-activation works out to k·dy minus k/2, so with k = 20 and dy = 1 it comes to 10, which should push the unit firmly into saturation.

Now I'm going through the risky scenarios, especially how the zone logic holds at the critical frame and what the paddle does on the bounce frame, checking the paddle-at-x9 and paddle-at-x8 hit cases.

Now I'm working out the worst-case distance the paddle has to cover after a hit, depending on whether the ball hits the paddle's new or old position and which way it's heading.

I'm checking the worst-case paddle distance after a hit: if the paddle is at the old x-position with the ball at the wall, the zone is {1, 0} and the distance is 7, which is fine. In the other wall case, the zone folds to {0} and the paddle needs 9 steps plus the bounce frame, leaving one spare move.

Working out the worst case: if the ball leaves from a wall cell at phase 10 or 0, the paddle needs 9 moves, all to the left, so there is one spare move. From a non-wall start the spare is larger, and the mode switch happens at the paddle-bounce frame.

I'm weighing whether the paddle should stay at x8 or move to x9 after a hit, since that choice decides whether the ball reaches the wall with a phase of 9 (leaving a 7-step distance) or reverses with a phase of 10 (leaving a 9-step distance with only one spare move).

I'm weighing whether the paddle should stay at x8 or move to x9 after a hit, since the zone it has to reach afterward depends on that choice. The trajectory itself, not just the paddle's choice, decides how far it has to travel, so I'd rather not try to steer the ball. The paddle just stops at the first zone cell it reaches, which is fine. Rough estimate: wall departures happen maybe 10% of the time and carry about a 1% death risk each, so the per-cycle risk is around 0.1%, which should mostly keep episodes near the cap.

Checking the wall-departure case more closely: if the paddle slips on the bounce frame and then slips again on the next one, it ends up nine cells from the zone with only eight moves, so that's about a 1% death risk per such departure. Maybe moving earlier, before the hit, could help in those cases.

I'm weighing whether the paddle should hold at x8 or shift to x9 for the zone {8, 9} case, since staying at 8 keeps the next approach shorter. If the ball arrives at 9 on its first frame, the zone collapses to {9} and the departure leaves only a 9-step distance.

I'm tracing which landing phases are the risky ones: if the ball lands at phase 9, the zone collapses to a single wall cell and the paddle gets stuck with a 9-step trip. That happens when the departure starts at phase 0, a wall-to-wall bounce.

Now I'm tracing the wall-to-wall cycle: a departure from phase 0 lands at phase 9 on the far wall, which forces a hit there and sends the ball back with phase 10, so the pattern can repeat. I'm checking whether the brick in row 3 breaks that loop along the return path.

I'm tracing the wall-to-wall cycle forward: the ball bounces off brick (4,3), then (5,3), and after that those bricks are gone, so the path reaches row 2 and adds a few more steps. That longer flight shifts the landing phase and breaks the loop. Each of those hits carries about a 1% death risk, so the cycle isn't persistent, and my overall estimate is a death rate around 0.1–0.3% per cycle.

Now I'm stress-testing the policy for systematic bugs that would end episodes quickly, covering holes in row 3, the top wall, and the corner cases where the ball and trail share a cell.

Now I'm tracing the trail from frame 20: the ball is ascending through row 4 toward the zone {6, 7}, and I'm reworking the paddle's path from frame 16 under the new policy. The paddle had already moved to x=4 at frame 6 and held there through the zone {3, 4} frames, so I'm recomputing the critical frame at frame 15 from that position.

Now I'm tracing the frames after the bounce: the ball heads up-left to (3,8), and the paddle shifts from 4 to 5 on the bounce frame. On the next frame the ball rises into row 7 and the zone {5,6} already covers the paddle's new spot, so it stays put.

Now I'm tracing the ball's path after the brick bounce: it drops down-right through row 4 toward row 8, landing on the critical frame, and the paddle at 5 gets hit and sends the ball back up-right. On the bounce frame the paddle shifts left to 4, and the zone {3, 4} already covers it, so it stays there.

Checking where the ball ends up after the bounce off the brick at (8,3): it reaches (7,2), which is a brick, so it breaks and the ball stays in row 3 with the direction flipped down-left. On the next step it moves to (6,4), which is clear, so the strike toggle resets.

I'm checking the paddle's response to the ball coming back up through the brick gap: at phase 11 the zone is {1, 2}, so the paddle shifts from 4 to 3. Then I'm tracing the next frame, where the ball moves into row 3 and its zone changes again.

Now I'm checking a top-wall case: the ball climbs through cleared columns toward row 0, and I'm tracing how the zone and paddle respond as it approaches the ceiling.

I'm checking the top-wall case step by step: the ball climbs to row 0, bounces off the ceiling, and then I verify the zone at each frame. The numbers line up so far, and I'm now checking what happens if the next cell holds a brick.

I'm checking the trail-and-zone bookkeeping on the top-wall case: the ball's zone drifts by one cell per step as it bounces along the ceiling, and the paddle follows that drift. When the ball finally descends, the zone still lines up with the paddle's position, so the policy stays consistent.

I'm checking the corner case where the ball reaches (0,0) and the trail sits on the same cell. The zone works out to {8, 9} on the ascent, and on the next frame, with ball and trail overlapping, the zone still comes out to the same values. Next I want to look at descending into a brick from above.

I'm checking the paddle's response in the sticky-action case: the zone stays constant frame to frame through the ascent, the bounce, and the descent, so the paddle just keeps holding. Next I want to settle what target the paddle should use on the paddle-bounce frame itself, since the zone isn't known yet at that point.

I'm checking the paddle-bounce frame against the mirror rule: when the paddle already sits at the mirror's neighbor, the rule moves it one cell unnecessarily, though nothing breaks.

I'm weighing whether to make the paddle-bounce rule lazier, moving only when the gap is at least 2 cells. The paddle weight is shared across rows, so changing the threshold for this row alone would need a different approach, and I'm considering adjusting the ball-row-8 weights instead.

I'm weighing whether the paddle should stay put on the bounce frame rather than move to the mirror position, since moving when it's already in the zone would be an unnecessary shift. I'm checking the parity of the mirror condition to see when the paddle and its mirror could line up.

I'm checking the new-x case: if the paddle is at b and the ball reverses to move right, the zone only covers the paddle when b is 5 or 4, so the mirror rule would move it one cell left to 4 for no reason.

Now I'm working through the slip probabilities for the paddle-bounce frame, checking whether a slip there just leaves it in the zone and whether the extra move converges back within a few frames. Next I'm starting to check how the tanh-scaled linear units behave across the valid value range.

Now I'm setting the weights for the ball and trail rows, with the ball's vertical gating folded into the same first-layer units.

Still writing the first-layer weights...

Still writing the first-layer weights...

Still writing the first-layer weights...

Still writing the first-layer weights...

Still writing the first-layer weights...

Still writing the remaining first-layer weights...

Still working out the zone at the wall-bounce frames: at the top-right corner the zone comes to {9}, and at the top-left corner it comes to {0}, both checking out.

I'm checking whether the policy could stall in a periodic trajectory that never reaches the remaining bricks, which would leave the score stuck until the step cap.

I'm checking whether the phase shift on each bounce could lock the ball into a cycle that never reaches the remaining bricks. The parity of the phase matters here, since it limits which cells the ball can visit.

Checking whether a slip could ever stall the ball: the top-wall bounce cycle shifts the phase so that, over ten cycles, every column at each row gets visited, so the remaining bricks should all eventually be reached.

I'm checking whether the policy could get trapped bouncing between the top wall and the row-1 bricks, since each hit there would clear a brick. I'm also weighing whether the ball's horizontal direction after a wall bounce could keep it from ever reaching the remaining cells.

I'm working through the ball's bounces along the top row: it breaks every other brick in row 1 from above, with strike toggling as it bounces off the ceiling. Once the bricks are all cleared and the ball returns to the bottom row, the rows respawn, and the ball is still in range to keep the cycle going. I'm also considering whether the paddle can keep up with the ball's lead when it rises through the open columns and then turns around.

I'm checking the timing on a descent: with the ball rising through row 4 and moving up toward row 3, the paddle's target zone shifts by one phase step per frame, so it has to keep moving to stay in range. If the ball then meets a brick at row 2, the same-row zone at row 3 still lines up with where the paddle has already moved.

I'm checking the timing through the descent: the paddle has seven frames in total, covering the ascent, the bounce, and five rows down, so even the two-cell move to reach the zone fits comfortably. Next I want to look at whether the paddle's mirror target could push it somewhere it shouldn't go on the bounce frame.

I'm checking the slip-recovery case: if the paddle enters the zone at the near cell and a slip carries it to the far cell, it's still inside and keeps holding. Only a second slip, which is rare, would push it out, and returning then takes a couple of moves that still fit the timing.

I'm looking at the cases where the paddle's arrival lands right at the deadline, and noting that wall-side zones are safe since overshoot is clamped. The main risk I see is a double slip early in a long move, which should be rare.

I'm now checking whether the paddle's position within the zone matters at the moment the ball is rising, and whether the ball's direction after a hit changes which zone it needs for the next flight. Then I want to confirm the timing: counting the actions between the critical frame, the paddle-bounce frame, and the ball reaching row 5 gives enough frames for the paddle to get into position.

Now I'm checking the timing in the ball's flight: from the critical frame, the paddle gets one action after the bounce, then a move on each row up to row 8, which gives about ten moves in total. For a distance of nine cells, that means nine moves plus one more at the wall, so the arrival still fits.

I'm weighing whether the paddle should target the old-x cell or the new-x cell at each wall-adjacent phase. Tracing a couple of cases by hand, preferring the old-x cell keeps the paddle closer on the next flight, so I'm checking whether that holds more generally.

I'm comparing the paddle's distance for the two options at each wall-adjacent phase: staying at the old-x cell versus moving to the new-x cell. For interior positions on the left side, the new-x choice ends up closer to the next zone, while on the right side the old-x choice does.

I'm working out whether the paddle should aim for the old-x or new-x cell at each wall-adjacent phase. For moves toward the far wall, the new-x choice sits closer to the next zone, while toward the near wall the old-x choice does, and the only case that reaches distance 9 is the forced one at the wall. I'm now asking whether I can simply prefer the old-x cell in the zone logic.

I'm weighing whether to have the paddle target the near cell x8 instead, at least during the ascent and early descent, since that would keep it off the wall cell. The cost is the small risk of a late slip in the approach. Entering from the wall side, the paddle would naturally stop at x8, so the tight cases are mostly the forced ones where φ8 is 9 or 19.

I'm checking the φ8 = 9 case concretely: the ball at (8,7) with phase 8 gives a zone of just cell 9, and the paddle is already there. On the next frame the ball reaches (9,8), and the paddle's target still works out to 18 in the timing check. So the paddle stays put and the critical step is next.

I'm checking the zone values for the ball's ascent: after the bounce it's at (9,8) heading up-left, and the paddle-bounce frame gives the paddle a -18 value, so it moves left. The mirror target is 0, and for the next frame the ascent zone at row 7 works out to {0}, which lines up.

I'm settling on a scaling approach for the first layer: multiplying the first weight column by 0.05 in place, the same way the earlier example scales a column, rather than pre-multiplying each number by hand, since that would be error-prone.

I'm deciding to keep the scaling as a single in-place column multiply rather than hand-scaling hundreds of numbers, with a quick worry about whether the `*=` form will parse for that first weight block.

I'm considering whether to scale the weights by 0.1 instead of 0.05, since dividing by ten is an easy decimal shift, and I'm checking that tanh(0.1v) stays monotonic over the range I need. The thresholds and the gain K2 need to be recomputed for that scale, and I'm noting that the ±4.9 margin works out with K2 = 100.

I'm settling on ε = 0.1 as the scale, since dividing by ten is a clean decimal shift, and tanh stays monotonic so the threshold comparisons still hold exactly. I'm weighing whether to rely on the `*=` column-scaling form or write the decimals out directly, and I'm leaning toward trusting the documented syntax while keeping the direct-decimal fallback in mind.

I'm weighing whether to write the scaled weights as plain decimals, since ε = 0.1 just moves each value's decimal point one place, like 64 becoming 6.4. That would avoid depending on the `*=` column-scaling statement, though it means hand-converting hundreds of numbers.

I'm settling on ε = 0.1 and writing the scaled values directly as decimals, since dividing each table entry by ten is simpler than relying on a column-multiply statement. Next I'm working out the layer-2 thresholds: tanh(0.1) and tanh(0.2) set the boundary, and I'm picking a gain K2 that gives the margins I need.

I'm setting the gain and bias for the second layer's three gated units: the down-ward, sideways and up-ward ones, each with its own constant so the gate terms cancel correctly in each direction.

I'm settling the output layer: the three gated units get a weight of 20 on the matching action outputs, with bias 40 so the inactive case comes out near -20. I'll leave the redundant no-op-style outputs alone, since they just repeat the previous action and do no harm.

I'm writing out the per-row weight lists for the D and U units, using 20 times the row index for the ball and trail inputs, and I'm planning to spell each list out explicitly rather than rely on a fill statement.

I'm considering folding the up and down checks into one signal that reads +1 for descent, 0 on the same row, and -1 for ascent, then gating the three actions off that single value.

Still writing out the scaled weight tables for the first layer...

Still writing out the scaled weight table for the first layer...

Still checking the scaled table values for the first layer...

Now I'm checking the exhaustive consistency of the scaled thresholds, verifying each consecutive pair of zone values (S_5 against S_4, then S_6 against S_5, and so on) against the fold sums across all twenty phases.

Now I'm checking the layer-difference pairs for the zone values, working out the fold sums for each phase and starting with the case where the wrap-around index is zero.

Now I'm checking the pair-difference values by fold sums, working through the lookup table g and the mod-20 indexing for each offset L.

I'm checking the pair differences for the L=4 case, comparing S_4 against S_3 across the phases and confirming each one matches the fold sum.

I'm checking the pair differences for L=4 across the remaining phases, comparing S_4 against S_3 and confirming each one matches the fold sum.

Still checking the pair differences for L=5, comparing S_5 against S_4 and confirming each one matches the fold sum.

Still checking the pair differences for L=5, verifying each phase against the fold sums.

Still checking the pair differences for L=5, working through the remaining phases against the fold sums.

Still checking the pair differences for L=6, working through the phases against the fold sums.

Still checking the pair differences for L=6, confirming each phase against the fold sums.

Still checking the pair differences for L=6, confirming the remaining phases against the fold sums.

Still verifying the S_7 and S_8 pair differences against the fold sums, checking the remaining phases.

Still verifying the L=7 pair differences against the fold sums, checking each phase through the wrap-around.

Checking the L=8 pair differences now, comparing S_8 against S_7 across the phases; the first few match the fold sums.

Still checking the L=8 pair differences, confirming the remaining phases against the fold sums.

Still verifying the L=9 pair differences, checking the phases against the fold sums.

Still checking the L=3 pair differences, comparing S_3 against S_2 phase by phase against the fold sums.

Still verifying the L=3 pair differences, checking each phase against the fold sums through the wrap-around.

Still checking the L=3 pair differences, confirming the remaining phases against the fold sums.

Still checking the L=2 pair differences, working through the phases against the fold sums.

Still checking the L=2 pair differences, confirming the remaining phases against the fold sums.

Still checking the L=1 pair differences, working through the phases against the fold sums.

Still checking the L=1 pair differences, working through the phases against the fold sums.

Now I'm checking the L=0 values, working through the phases against the fold sums.

Still checking the L=0 values, confirming each phase against the fold sums.

Still checking the mode assignments, working through each row from the descent side and confirming the ball and trail tables line up.

Now I'm checking the ascent case for rows 4 to 7, where the ball's table index is one above the row and the trail uses the row itself.

Still verifying the mode assignments for the ascent rows, checking how the ball and trail tables line up for rows 4 through 7.

I'm checking the ascent case at row 4 against the "immediately" assumption: if the ball is heading up and hits a brick at row 3, the bounce frame lands at row 4 one phase later, so the zone is φ+5 and φ+6.

