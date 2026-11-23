I'm setting up a hand-designed policy network for MinAtar Breakout and first want to pin down how the ball and paddle interact each step. The ball's state is its position plus one of four diagonal directions, and the paddle moves before the ball does on every step.

I'm now checking the bounce rules at the bottom row: if the ball's old x matches the paddle, only the vertical direction flips, and if the new x matches, both directions reverse. So the paddle has to sit under one of those two x positions on the step when the ball is at row 8 moving down.

I'm noting that the ball never shows up on row 9 unless the episode ends, and that from row 8 moving down it stays on row 8 and turns upward. So the paddle needs to track where the ball will be at that critical row-8 step, and since both move one column per step, I'm considering a policy that steers the paddle toward the ball's next x.

I'm checking that the paddle can match either the ball's current x or its next x at the critical step. If it tracks the ball one column per step, it stays in sync with the ball, so when the ball is at row 8 moving down, the paddle is already under it. That leaves a slack of one column: the paddle can either stay or step toward the ball's next x, and both choices work.

I'm weighing whether a simple tracking rule would be enough, which would mean steering the paddle toward the ball's x at each step. Sticky actions could make it lag by one column, but the slack at the critical step should absorb that most of the time. I'm also considering a linear estimate of the ball's next x from its current and previous positions, since a more elaborate landing prediction would be harder to fit into the network.

I'm wiring the two hidden units so that one fires when the paddle is at least one column left of the target and the other when it is at least one column right. Those two signals then feed the right, left and no-op logits, with the no-op staying at zero.

I'm checking whether simple tracking is really the best strategy, and how the ball's horizontal motion and wall bounces could break the paddle's sync with it. I'm also starting to trace the ball's opening path from the corner, stepping it down toward row 8 to see where the critical step falls.

I'm checking the paddle's position against the two possible landing columns for the ball's next critical step, and working through the opening path from the bottom-left corner where the paddle only needs to stay put.

I'm checking the corner case where the ball sits on the right wall at row 8 moving down-right. The clamped x keeps it at column 9, so the vertical flip sends it back up with the same x, and the ball and its trail end up on the same cell.

I'm checking the corner case where the ball sits on the right wall and bounces back up, since that leaves the ball and its trail on the same cell with a down-left direction. Along the side walls the direction is fixed away from the wall, and I'm now turning to the question of when the paddle falls out of sync with the ball.

I'm now looking at how the ball's horizontal speed and the paddle's step size interact. Once the paddle is in sync with the ball, it stays in sync, except when sticky actions cause a lag or when the ball's horizontal direction flips at a wall bounce.

I'm working out what happens when the paddle lags a column behind the ball: the sticky "no-op" can stand in for a needed move, so the paddle falls behind and stays behind until the ball reverses at the other wall and gives it a catch-up step. With the paddle one behind, the question is how to pick the target column at the critical step so it still lines up with the ball's next x.

I'm working out how the paddle would stay in sync if it aims at the ball's current x instead of its next one. After each move the paddle sits on the ball's column, and then the ball steps over, so at the critical row-8 step the paddle is already positioned to bounce it.

I'm weighing whether to aim the paddle at the ball's next x or its current x, since a sticky action could leave it a column short either way. Aiming at the next x seems to leave some slack, but I'm also wondering whether predicting the landing spot directly would be cleaner than tracking.

I'm noting that the paddle needs to reach the critical row-8 spot, and from row 4 moving down the ball's landing is deterministic, so the paddle has about five steps to get in position. Bricks only matter in the top rows, so below row 4 the prediction holds, though a paddle that starts far away could still be too slow to cover the distance.

I'm now seeing that the ball's horizontal motion is independent of bricks, since bricks only flip its vertical direction, so the paddle can simply track the ball's x. That x follows a fixed bouncing pattern between the walls, with a pause at each wall, and only a paddle reverse-bounce changes its horizontal direction.

I'm checking whether the paddle can reverse-bounce the ball: if it meets the ball at row 8 by moving against the ball's direction, the ball's horizontal direction flips and it goes back up one column over. That means the ball's x sequence can bounce back and forth, like b, b+d, b, so the paddle's tracking target has to account for that reversal.

I'm checking the two bounce cases at row 8: a straight bounce leaves the paddle at the trail's x, while a reverse bounce leaves it at the ball's x, so the paddle position is what tells them apart. I'm also checking the wall case at column 9, where the ball stays put and flips direction before the vertical flip.

I'm working out how a brick bounce differs from a paddle bounce: when the ball hits a brick, its horizontal direction stays the same and only the vertical flips, so the ball and its trail end up on the same row but offset by the horizontal step. That offset gives the horizontal direction, which I can use to check where the ball came from.

I'm checking the wall case and the start state, and both come out consistent: at the side walls the ball stays in place and flips direction, so ball_x and trail_x match and the direction points away from the wall. That leaves a simple rule for the predicted next x: step by the difference between the ball's x and its trail, except when both sit on the right wall, where it pulls back to 8.

I'm checking whether a simple rule works: the predicted next x is the ball's x plus its step from the trail, clamped at the walls, with the exception of a paddle reverse-bounce. I'll test whether just tracking the ball's current x is enough, since the paddle would then sit where the ball was a step earlier and line up for a straight bounce.

I'm checking how the paddle falls out of sync with the ball: if it's told to move left but a sticky no-op makes it stay put at the right wall, it ends up a column behind. I'll check whether that lag persists until the ball bounces off the far wall and gives the paddle a catch-up step.

I'm estimating the cost of a sticky-action lag: each direction change at a wall has roughly a 10% chance of leaving the paddle one column behind, and that lag lasts until the ball reaches the opposite wall, which is around ten steps. If the critical step falls inside that window, the ball is missed, so each wall bounce carries roughly a 4% death risk.

I'm estimating the payoff of a policy that targets the predicted next x (b + d) instead of the current one. If the paddle is in sync, it catches the reverse bounce, and even with a one-column sticky lag it still gets a straight bounce, so this version tolerates a lag of one.

I'm checking the lag that follows a reverse bounce: the paddle ends up two columns off the ball's path, and the naive estimate keeps pulling it the wrong way, so the lag stays at two.

I'm working through how often a lag would cost the paddle the critical step. The ball takes roughly ten steps to go up to the bricks and come back to row 8, and with its horizontal motion it hits a wall about once in that span, so the paddle gets a catch-up step. That means a single column of lag is fine for the next-x policy, though it leaves no spare slack.

I'm weighing whether to detect the reverse bounce directly, since treating the paddle as always making a straight bounce would lose robustness. Then I'm comparing the two targeting options: aiming for the ball's own x works when the paddle is in sync, while aiming one step ahead handles a one-column lag, so I want a policy that lands on the predicted landing spot instead.

I'm weighing whether to always aim for the ball's landing spot, since if the paddle never reverse-bounces, the horizontal motion is a fixed period-20 cycle that only needs tracking at the critical step.

I'm now weighing a deeper design: thinking about the death probability per cycle for Policy B with the reverse bounce handled properly, and what an ideal handcrafted policy could look like under the 600→32→32→6 network's constraints.

I'm now looking at what the first layer can represent: each unit is a tanh of a sum of lookup terms over the ball cell, the trail cell, and the paddle column. If the ball's destination can be written as an additive function of ball and trail positions, a single unit could encode the paddle target directly.

I'm checking whether the landing x can be written as a sum of a ball term and a trail term. Since the trail's row is always one below the ball's while moving down, the cross term between the trail's x and the ball's row can be folded into the trail's lookup table, so the whole prediction stays additive.

I'm working out whether the reflection at the walls can be handled by a few threshold units in the first layer, since the folded landing position is piecewise linear in the unfolded value and each fold is just a step change.

I'm weighing whether the folding at the walls can be done with threshold units in the first layer, since the landing position is piecewise linear and each fold is a step change. The catch is that the fold depends jointly on the ball and trail cells, so it can't be an additive lookup, and I'd need to gate the units by direction somehow.

I'm working out how the ball's horizontal position cycles: it follows a period-20 phase that advances by one each step, with the position mirrored on the far half. The next piece is working out whether the ball's phase can be read from its position and trail alone.

I'm checking whether the phase can be split into a ball term plus a trail term: moving right it equals bx, moving left it equals 19 - bx, with special cases at the walls. That means the trail's x has to shift the sum for each direction, and I'm testing whether additive tables can satisfy that for the middle columns.

I'm solving for the remaining terms of the phase function: g(t) comes out quadratic, with a leading coefficient of -1/2 and a linear term of 9.5. Then I'm substituting back to get f(b), and I want to check the second equation to confirm the two constraints are consistent.

I'm checking that the pair constraints close up: the nine pairs with b one above t, the nine with b one below, and the two wall cases give twenty equations for the twenty unknowns in f and g.

I'm tracing the constraint graph that links the f-terms and g-terms: each f_b connects to the g-terms one step either side of it, with f_0–g_0 and f_9–g_9 as the extra links. The result splits into two parity-based components that are joined at the two wall edges, which looks like a single chain of ten nodes followed by the return path.

I'm checking whether the 2D version of the phase function stays additive, which adds more unknowns and constraints than the 1D case and may over-determine the system.

I'm moving on from the additive-function approach to think about what actually causes deaths, and I'm considering a prediction-based policy instead: when the ball is heading down past the brick rows, I can compute its exact landing column and aim the paddle there, allowing for the reverse-bounce case.

I'm checking how the paddle keeps up: if it reaches the predicted landing column early and waits there, small overshoots can be corrected, but the ball's descent from row 4 leaves only about five moves, so when the paddle starts far away I'll need to anticipate the horizontal position while the ball is still climbing.

I'm working out the timing of the ball's trip: after the paddle bounce it climbs from row 8, hits the row-3 brick and comes back down, so the full cycle is ten steps and the horizontal phase advances by ten in that time.

I'm checking how the paddle has to cover the distance to the mirrored position in the next cycle, which is always doable since the travel is at most 9. I also note that as bricks clear, the ball can climb to the top row and make longer cycles, up to 18 steps, so tracking its horizontal position in the meantime still works.

I'm now checking Policy B's failure cases, starting with a ball moving right at steady state, where the paddle keeps stepping right and sticky repeats cause no trouble. At the right wall the target saturates at 9, so the paddle briefly holds still before turning left, and I'm looking at whether a repeated action at that turn could leave it one cell behind.

I'm checking the lag case next: with the paddle one cell behind after a sticky N, the straight bounce still works, but after it the ball's true next x is b+2d while my estimate of d gives the same target, so the error shows up one step later.

I'm now looking at the lag-2 case: if the paddle overshoots once by a sticky repeat while the true target is b, the error stays at two cells and only shrinks when the ball hits a wall.

I'm checking the wall case concretely: with the ball at 8, 9, 9, 8, 7 and targets 9, 9, 8, 7, 6, a paddle starting two cells behind should close the gap when it reaches the wall, so the error from the reverse bounce should be absorbed within the next cycle.

I'm checking the wall bounces with a lag of 2: the paddle reverses early at the wall and comes back into sync, since the ball turning around means the paddle is now ahead of it in the new direction. So a lag behind the ball tends to correct itself at each wall hit, and I'm about to look at what happens when the lag is only 1 before the wall.

I'm checking the wall case again: after any wall bounce a lag of up to about three cells gets fixed, since the paddle ends up ahead of the ball once it turns. The risky moment is the reverse bounce, where a sticky repeat can leave the paddle two cells off, though at least one wall hit in every ten-step cycle should clear that before the next critical step.

I'm noting that wall bounces happen exactly every ten phase steps, and since each critical step is at least ten steps apart, there's always one wall transition in between to catch up a lag from a sticky repeat. I'm checking the reflected phase after a reverse bounce to confirm the wall timing still lines up.

I'm checking the case where the critical step is itself the wall-stay transition: with the ball at (9,8) moving right, the target is 9, but a paddle running two cells behind only reaches 8. That would be a death, so the lag-2 risk is worse right at the wall.

I'm checking the case where the ball bounces back to x=0 with the paddle at 0: the reverse move is clamped at the wall, so a sticky repeat leaves the paddle only one cell off, which is a harmless lag of 1.

I'm checking the two-step lag case with the ball at 9 moving right: if the paddle starts two cells behind, it reaches 8 while the target is still 9, so this is where a lag of 2 would be fatal.

I'm checking the wall-bounce and sticky-action cases: a botched "N" at the wall is harmless, and a botched "L" only leaves a lag of 1. Any single sticky repeat is mostly survivable, since direction changes are the only places it can cause a problem.

I'm checking a lag of one cell at the wall: the paddle catches up within a couple of steps, and a single botched reversal there just leaves it one cell behind again. A double sticky event is the rarer case I still need to think through.

I'm checking the sticky-action code next: in MinAtar, a repeated action is the last executed one, so a sticky event at a wall bounce only leaves a two-cell lag about 1% of the time. I'm estimating that this kind of double slip happens roughly once per hundred or so wall bounces, which would make it a real but modest source of losses over a long game.

I'm checking the lag-2 case again: with the ball moving right, the paddle goes 6→7, then 7→8, then holds at 8 after the wall. The only failure is if the middle observation lands on row 8 at the critical step, which needs the ball at phase 9 there, so otherwise the lag gets corrected.

I'm checking a botched reverse bounce one cell further out: with the ball at (2,8) moving left and the paddle at 1, the reverse bounce puts the ball at (1,8) heading up-right, the paddle should move to 2, but a sticky L leaves it at 0, a lag of 2. From there the ball needs about eight steps to reach the wall, so the next row-8 check should come after the lag has had a chance to close.

I'm checking the lag-2 case on the reverse bounce: with the ball at (9,8) moving left and the paddle a cell behind, the target comes out to 8 and the paddle already sits there, so it lines up. The same lag-2 reasoning also holds for the earlier wall arrival, so a single sticky slip should get corrected before a critical step.

I'm now trying to write the decision as a function of the ball's cell, its trail cell, and the paddle column, so the sign of the target minus the paddle position comes out directly. The idea is to use layer-one units built from the ball and trail terms, and I'm checking whether the target can be treated as an additive sum of the two, which depends on a consistency condition across the 20-step cycle.

I'm trying a linear form T = 2b − t for the paddle target, which works for most of the wall and moving-left cases. It gives the right answer at (9,8) and (0,1) up to harmless clamping, but at (9,9) it yields 9 where the correct target is 8, so the simple linear version breaks there.

I'm trying to find a target function that fits every wall and reverse-bounce case, since a plain linear form breaks at (9,9) and (0,0). The idea is to let the two lookup tables for the ball and the trail be free, with the wall cases only needing to land on the correct side of the paddle. The next step is solving that chain of constraints for the values.

I'm settling on a concrete form for the correction terms: the even-indexed ball cells get α = 1 and the odd-indexed trail cells get β = -1, so each consistency constraint in the chain holds.

I'm checking the cases where the ball is at an even column and the trail at an odd one, and the same parity pattern for the remaining pairs. Setting the ball term to 2b plus one when b is even, and the trail term to minus t minus one when t is odd, gives a consistent target across the cases I've tested.

I'm checking whether the parity-corrected form stays exact when the ball and trail sit in row 8, since the paddle's position then decides between the straight and reverse bounce.

I'm trying to make the target sit exactly halfway between the paddle and the trail cell, so the sign of the difference picks the direction. Whether the paddle is on the trail or one cell past it, that threshold gives the right move.

The paddle has to be compared against two different targets depending on the bounce direction. For the reverse case with the ball one row above and moving the other way, the sign flips, so I want the paddle to move left when it sits on the trail cell and right when it sits one cell past it. Since the paddle's coefficient is fixed across cases, I can't just scale the difference by two, so I'm working out a separate threshold in the other direction.

I'm settling on a threshold at the midpoint between the ball and trail cells, so the paddle moves right whenever it sits below that point and left whenever it sits above it, with no dead zone in between.

I'm working out the row-8 case, where the right and left units each need their own target table: the right unit sits half a cell above the midpoint between the ball and trail, and the left unit half a cell below it, so both thresholds land in the same spot.

I'm now setting up the table for the row-8 cases, where each unit needs its own target function so that the paddle's left and right decisions split cleanly at the midpoint between the ball and trail columns. The plan is to work through the cases by row, starting with the ball in row y and the trail one row above it moving down.

I'm working through the remaining cases by row: the ball in row y with the trail one row off, moving down or up, where the target is just the next column. Brick bounces keep the direction and use 2b − t, with the wall corners at (9,9) and (0,0) as special cases. The row-8 paddle bounces are the last group to handle, including the wall corners there.

I'm now checking the remaining reset states and the wall-adjacent cases, where the ball sits at (0,3) or (9,3) and the trail matches it, to confirm the target comes out to 1 or 8 with the paddle at 4. After that I'll look at whether the ball's row can ever equal the trail's row in a non-paddle bounce.

I'm checking a special case in the brick logic: if the ball already struck a brick on the previous step, it seems to pass straight into the brick cell without bouncing, and the strike flag stays set as long as consecutive brick hits happen.

I'm checking the strike flag in the brick logic: if the ball hits a brick on consecutive steps, the flag stays set, and a ball moving down from row 0 into a brick at row 1 would trigger it again.

I'm now checking how the brick-strike flag behaves when the ball passes into consecutive brick cells, which doesn't change the horizontal motion. I'll set up the additive table for the R-unit next, treating the row-8 cases separately.

I'm now working out the same-row brick-bounce tables, so I'm fixing F_y(b) = 2b + [b even] and G_y(t) = -t - [t odd] as the row-independent solution for the diagonal cases.

Checking the same-row brick bounces next: the ball keeps its horizontal direction, so the same tables apply. At the right wall, a ball at column 9 that bounces off a brick directly above it ends up moving left with the trail still on its own cell, which fits the existing target.

Now I'm checking the row-8 cases: the ball in row 8 with the trail one row above it, and the ball in row 8 with the trail on the same row. That means F_8 and G_8 might need to differ from the generic tables, as long as their sum still matches the paddle-bounce target.

I'm working through how to make the 8-row targets consistent: if the ball's F-term at row 8 stays fixed, the trail's G-term at row 8 has to absorb the shift so that the paddle-bounce sums still match.

I'm checking whether F_8 can deviate from the generic table, since the generic G_7 seems to force it to match exactly, including at the wall values. The remaining question is whether the row-7 and row-8 tables can shift together without breaking the up-moving and paddle-bounce constraints.

I'm noticing that the freedom I had in mind doesn't come from shifting whole rows, since the cycle of constraints ties every row together and only a global constant can move. So I'm checking whether the target values themselves have any slack: the R-unit only needs its sign to be right relative to the paddle position, so the exact numbers might not have to match the midpoint.

I'm trying to see whether the row-8 same-row constraints can be met by a looser target, since a tolerance of about half a cell either way still gives the right paddle decision. I'm writing the R-unit condition for the case where the ball and trail share row 8 and the ball sits one column right of the trail, so the unit should switch on exactly when the paddle is at or left of the trail column.

Working out the row-8 same-row targets for the R-unit: when the ball moves right along row 8, the target should be one less than the usual rule gives, and when it moves left, two more. So the R-unit's ideal value turns into b for one direction and b+1 for the other, which is the sticking point I'm checking now.

I'm now working out the row-8 tables separately for the R-unit and L-unit, since a single shared target can't satisfy both paddle directions. Next I'll set up the unknowns for the R-unit's row-8 values.

I'm weighing whether tolerance alone can absorb the row-8 same-row shifts, since the F_8 and G_8 tables are pinned by the diagonal constraints with row 7. Forcing F_8 and G_8 to match the generic tables leaves the paddle-bounce sums one cell off in each direction, so I need another source of slack.

I'm now weighing a layer-1 unit that detects when the ball and trail both sit in row 8, then using layer 2 to pick between the R and L outcomes based on the paddle position under that gate.

I'm working on a layer-2 selector that picks the special row-8 unit when the same-row detector fires and the normal unit otherwise, using a saturating tanh combination of the ±1 signals.

I'm settling on a layer-2 gate: one AND-style unit takes the normal R-unit output while excluding the row-8 same-row case, and another takes the special row-8 output only when that case holds. Both feed a combined logit for the R decision, so the two cases stay separate without needing one table to satisfy both.

Now I'm weighing whether a lead-ahead policy would be more robust than the plain tracking one, since the paddle could aim slightly ahead of the ball when it's moving up and far away.

I'm checking the wall case for the ball moving right: at column 9 the paddle clamps, so the target value and the actual move can disagree, and I'm working out which action still keeps the paddle in sync.

I'm checking the wall case again: when the ball sits at column 9 and moves right, a botched R action leaves the paddle at 9, giving a lag of 1 that stays until the next reversal. Two botched moves in a row would make the lag 2, which is the dangerous case.

I'm checking what a double botch at the wall would do: if the paddle repeats its move and sticks at column 9 for two steps, the lag grows to 2, and the critical bounce step is very likely to fall before the next wall hit, so that case is close to fatal. Roughly one percent of wall hits could end the run this way, which makes me wonder whether the wall handling can be made more robust.

I'm looking at what happens when the paddle sticks at the right wall for two steps: it ends up one cell behind where it needs to be when the ball comes back. That's a fatal lag, so I'm considering whether the paddle could start moving toward the wall earlier to avoid being caught there.

I'm considering a more complex policy where the paddle doesn't track the ball's next x exactly, but instead cuts the corner when the ball is high or heading up, since it has time to wait. Waiting at column 8 instead of going to the wall could avoid the lag problem, but it's only safe if the ball isn't at column 9 when the critical bounce happens.

I'm weighing whether a lead of one cell would help, but leading puts the paddle ahead of the ball and a lead of two would need the paddle to wait at the edge, which brings its own timing risks.

I'm considering whether a lead of one cell could help, but the lead has to be removed before the critical bounce step, which means a slowdown that can itself be botched. Under a botched correction the lead shrinks by two cells per step rather than one, so I'm checking whether that leaves the paddle at the wrong cell at the critical moment.

I'm now thinking of the relative offset e as paddle position minus the ball's next x, signed by the ball's direction. A paddle move keeps e the same, a no-op drops it by one, and moving against the ball drops it by two, so e can only shrink apart from wall or reversal events.

Now I'm checking how the paddle's position relative to the ball's next x behaves across the wall turn. Before the turn the paddle sits at some p, and after the ball reverses, the offset e = 8 − p means that waiting at 8 keeps e at zero while waiting at 7 would leave a lead of one.

Checking whether a paddle that waits at 7 or 8 could avoid the wall-turn lag, I find the same vulnerability: any time the paddle has to start moving, two consecutive botched actions still leave it a cell out of position.

I'm considering a lead of one cell: the paddle runs ahead of the ball by one while moving, so a double botch still leaves it in range. The lead has to come down before the critical step, which means one deliberate no-op while the ball is on row 7, and I'm checking whether a botched version of that single step is still safe.

I'm checking the critical-step policy with the paddle at e=+1: if it's at T, a no-op gets it in sync, and if a botched no-op turns into a move, the paddle lands two cells off.

I'm now checking the lead policy: when the ball is far from landing, the paddle targets one cell ahead, and when the ball is about to land on row 7, it drops back to targeting the ball's next x. In that setup the paddle ends up exactly on target at the critical step, so a botched no-op still leaves it on a straight bounce, and a turn with botches only moves the lead from +1 to 0 to -1, which is still within tolerance.

Now I'm checking the landing case with a lead: if the paddle keeps its lead into the critical step, a botched no-op turns into a move and leaves it two cells off. So I'm looking at slowing down earlier, at row 6, so the correction happens before the ball reaches the bottom.

I'm weighing the fixed costs of changing direction: any time the paddle has to switch actions, a botch can leave it a cell off. Leading at row 6 or 7 just moves that same exposure to a different step, so no placement removes the risk entirely.

I'm considering stationary waiting as an alternative: the paddle reaches its landing spot early and holds N through the critical step, so there are no action changes close to the bounce. Each change of action carries a botch risk, so limiting changes near the critical step may matter more than the exact cell the paddle targets.

I'm now working out whether the paddle can wait at a spot ahead of time, since the ball needs about five steps from the brick bounce to the critical bounce. That would keep the paddle from making late action changes, but it depends on predicting where the ball will come down from the brick layout.

I'm considering whether a brick-aware policy could work: from the ball's phase going up, I'd predict where it comes back down by checking whether a brick sits in its path at row 3. That lookup depends on both the brick layout and the ball's timing, so it multiplies out to many cases, and with only 32 hidden units I'd only be able to cover a limited version of it.

I'm working through whether a straight bounce keeps the phase the same while a reverse bounce mirrors it, which determines where the next critical observation lands.

I'm working out the reverse-bounce case: after a reversal, the paddle should step back toward the ball's next x, but a botched move in the wrong direction would leave it two cells off, which would be a problem at the next critical step.

I'm checking the wall-turn case: with the ball reversing off the wall, the phase mirrors, and the next critical observation depends on whether the range between bounce and critical step crosses a wall. I'm noting that only the edge phases 0 and 10 avoid a wall transition in that window, and tracing which prior phase leads to phase 0.

I'm checking the wall case: if the ball is at the left edge moving up-right, the paddle wanting to go right gets clamped at 0 on a botched left move, so the lag stays at one. When the wall falls inside the window, the lag of two gets corrected, since the paddle turns early and ends up in sync by the next critical step.

I'm checking which case actually breaks the lag-2 state: a reverse-bounce botch leaves the paddle two cells behind, and I need to see whether the next wall turn can still correct it or whether a further botch at that point finishes it off.

I'm checking the lag-2 case near the right wall: with the paddle two cells behind, the critical observation at phase 9 or 19 would leave it one cell short of the ball, which is fatal, so I need to work out when that phase lines up with the approach.

I'm checking the lag-2 case near the right wall, where the critical observation would land at phase 8 after a reverse bounce. If the paddle botches its move back toward the ball's next x, it ends up two cells behind, and I'm tracing how the ball's phase advances from there.

I'm checking the two-lag case once more: after a botched reverse bounce, the paddle is two cells behind, and a wall turn inside the window pulls it back into sync before the critical observation. The only window where it stays two cells off at the critical step is one with no wall transition, and that needs the phase right at the edge, so I'm working out how likely that is under the double-botch scenario.

I'm working out the phase bookkeeping for the bounce: a reverse bounce sends the phase to 18 minus the critical phase, and counting the steps from the bounce to the next critical observation gives a cycle of ten, landing at phase φ' + 9.

I'm working out the phase cycle: with reverse bounces every time and ten-step cycles, the critical phase alternates between two values, so I'm tracing one concrete start, with the ball going down-right from row 3 and reaching row 8 at phase 5, and following its path after a reverse bounce up through the bricks and off the wall.

I'm tracing a concrete bounce: after the reverse bounce the ball heads up-left, clips the wall and the brick at row 2, and I'm checking whether the brick there is still present before it gets hit.

I'm now checking the death rate under this policy: a wall double botch followed by a critical observation before the next wall turn is the main risk, at roughly 1% per occurrence.

Now I'm double-checking the wall case: if the paddle is clamped near the edge, a botched move there only costs one cell, but a second botch would leave it two behind, and I need to see whether the reverse-bounce lag can combine with that.

I'm now checking the case where the paddle is one cell behind from a single wall botch: the ball keeps its straight path and the lag stays at one. At the next wall turn the paddle moves right twice and then stops, and a single botch there leaves it at one cell behind while a double botch leaves it at two.

So the death rate per cycle comes out to about 1% from a double botch at the wall, plus a small extra term. Over roughly 100 cycles that is on the order of 100 points, since the ball tends to hit at least one brick per cycle. I'm still unsure whether the ball can bounce between the bricks and the top wall before it comes back down.

I'm now looking at the wall-turn fix: when the ball is high and moving up, the paddle could cut the corner by clamping its target early, so a single botched wall move no longer leaves it open to a second miss.

I'm thinking about a paddle strategy that starts moving before the ball reaches the wall, so that a single botched move near the turn can't leave it two cells behind. The idea is to track the lead, the gap between the ball's target and the paddle, and only begin the leftward move once that gap closes to zero.

I'm weighing whether a paddle that starts moving early, while still a cell ahead, can be made safe: any lead of one must be shed at least two steps before the critical observation, since a botched hold there would be fatal. That makes simply waiting at the landing spot and staying put look like the most robust option.

I'm now thinking about a prediction-based approach: once the ball is moving down below the bricks, its landing spot is fixed, so the paddle can head there early and wait, without needing to correct at the last moment.

I'm checking whether the paddle can afford to wait near the landing spot, and concluding that when the ball is moving down toward the bottom row, the paddle has no slack to spare, so tracking is already the best option. The only real danger is at the turns, especially the wall turn, so that's where I need to focus.

I'm weighing whether the paddle should cut the corner at a wall turn by leading into it early, since a wait-then-reverse still leaves it exposed to a double botch. If it leads by two and drops the lead with waiting steps, that looks like the same policy applied from a position already ahead.

I'm weighing whether the paddle can avoid the N→L transition altogether by keeping a lead of +1 and moving L steadily. The catch is that it would need to drop that lead with an N step later, and a botched L there would leave it at -1, which is survivable, but a double botch would be fatal.

I'm seeing that the N→L switch is where the trouble lies: a 10% botch on the first L leaves the paddle one behind, and a second one makes it two, so each transition carries about a 1% double-botch risk. If the paddle reverses directly from R at a wall, a botched R costs two cells, which is even worse.

I'm reasoning through why a pure moving strategy still leaves about a 1% death floor at each turn, since any N-to-L switch can be hit by a double botch. Deaths only happen if the critical observation falls before the next wall turn, so I'm checking where the critical phase sits relative to that turn.

I'm checking whether a stationary approach at the landing spot holds up: if the paddle approaches in the ball's horizontal direction and aims for the target, a single overshoot still lands in the acceptable window, though a double botch would overshoot too far and leave little time to correct.

I'm weighing whether an early-arrival, wait-and-hold approach is worth its complexity, since the landing time depends on which bricks are still present (roughly 10 to 18 steps out). The simple policy probably lands near 100 points, so the question is whether the extra planning actually improves on that.

I'm weighing whether a brick-aware landing predictor is worth building within the code budget, since the landing time depends on which bricks remain. I'm also looking for cheaper fixes for the wall-turn double-botch risk and the reverse-bounce lag, perhaps by exploiting reverse bounces in the 10-step cycle.

I'm noticing that with straight bounces at the center, the ball's mirrored position means the paddle only needs to shift about one cell per cycle, which is much less movement than the reverse-bounce route.

I'm sketching out a paddle that stays near the center, since with straight bounces the ball's mirrored path only needs the paddle to shift about one cell per cycle. I'm also wondering whether a predictive rule based on where the ball will be in the next cycle could help, though I haven't settled on what that rule would look like.

I'm now considering whether the paddle can stay within reach of the critical spot by checking how far it must move over the remaining steps, allowing for a botched move. Working backward, the paddle's feasible range shrinks as the critical step approaches, so the tracking position sits at the edge of that range whenever no wall lies in between.

I'm working out the safe zone for the paddle: if it starts one cell ahead of the ball, it has enough slack to survive a double botch, which bounds the allowed range to roughly b+1 through b+2k-2.

I'm looking at the paddle staying ahead of the ball in its direction of travel, so that it can head for the landing spot and wait there once the ball is clearly descending below the bricks. A wall between the ball and its landing point would widen the safe zone, and tying the paddle's lead to the ball's phase would also handle corners at the walls.

I'm sketching a policy that aims the paddle a few phase steps ahead of the ball during its upward flight. Once the ball is descending below the bricks, the target becomes the predicted landing spot, x at the critical phase, and I'm writing that as a rule for the downward leg.

I'm settling on a dead-zone rule for the paddle: if it's already inside the two-cell landing window, it holds; if it's left of the window it moves right, and if it's right of it, it moves left. Whichever cell it reaches first can serve as the target, depending on which side it approaches from.

I'm now thinking about whether the paddle's target can be a simple additive rule: aim for the leftmost of the two landing cells when moving right, the rightmost when moving left, and hold if already inside the window. Whether that composes cleanly across the cycle still needs checking once the row effects are included.

I'm checking where the paddle ends up under the "N if within the window" rule. If it comes in from behind the ball's direction of travel, it reaches the first landing cell and stops there, so the bounce is straight. If it comes from ahead, it reaches the second cell first and the bounce reverses.

I'm realizing the paddle can't overtake the ball once it has reversed, since both move at speed one, so any lead has to come from a wall corner. After a reverse bounce the paddle sits at the ball's position and only gets ahead of it once it cuts a corner at a wall.

I'm working through how the paddle chases the ball up after a bounce. If it starts behind or level with the ball, it keeps pace until the ball nears the wall, and aiming a few phase steps ahead lets it start turning before the ball does. I'm tracing that target as the ball's phase advances, to see how the paddle's path sequences out.

I'm checking the paddle's reversal sequence: a direct R-to-L turn gets botched, the paddle clamps at the wall, and it still survives a double botch thanks to corner cutting. Once the ball descends, the paddle should already be waiting in the landing window.

I'm checking how far the paddle would have to travel to reach the landing window if it starts with a large lead, since a bigger lead gives more slack but could leave it too far ahead when the ball lands. Once the ball is descending, the paddle just needs to hold inside the window or step back toward it, and I want to confirm that a step back is always possible in time.

I'm checking the timing of the switch into descent mode: if the ball bounces off a brick at row 4, the first descent observation has five moves left before the landing. I also want to make sure that a lead in phase doesn't get confused with a lead across a wall turn, since the up-flight target can point the same direction the ball is already moving.

I'm now working out the paddle's target in descent mode, where it depends on the ball's row and phase, and then I'm checking whether a single up-flight target can cover both the rising and brick-bounce cases.

I'm working out where the ball lands if it rises and bounces off the top: the earliest landing phases are φ+9, then later ones at φ+11, 13, 15, and 17 if it goes all the way up and back down. I'm tracking which landing cells those phases map to, so the paddle's window can cover every case.

I'm working out the landing windows for the ball's possible descent phases, and the paddle should be within reach of each one by the time the ball gets there.

I'm weighing a phase-lead target of a = 3 against a = 1: with a = 3 the paddle stays within about one cell of the ball's landing window and keeps roughly four cells of slack, while a = 1 leaves only about two.

I'm checking the slack again under the pure phase-lead target: with the paddle starting in sync at x(ψ) and five moves before the critical observation, it needs to cover four cells to reach x(ψ+4), which leaves one move to spare. That means the Policy B slack is one, so my earlier claim needs a second look against the actual target.

I'm checking how far the paddle can lead the ball: a target of x(ψ+a) means the paddle sits at x(ψ-1+a) before moving, so with a = 3 it's two cells ahead of the ball's phase and stays within reach of the landing window. A larger a would put it right on the earliest landing spot, though it can't get ahead of the ball without a wall corner to cut.

I'm now checking the paddle's chase after a bounce: with the ball at 5 moving right and the paddle one cell behind, a lead target of a=4 has it moving right until the wall region, then turning back as the target reverses. I'm tracing how it tracks the target step by step, to see where it sits when the landing at phase 14 comes.

I'm checking the paddle's chase through the descent: with the ball at 5 moving left and the target window at {5, 4}, the paddle steps left into it and then waits. I still want to confirm that the transitions between chasing, holding, and moving back stay within slack at each step, and whether the reverse-bounce case behaves the same way.

I'm checking whether a straight bounce, which leaves the paddle one cell behind the ball, is risky in the same way, since that sets the paddle's lead differently from a reverse bounce, where it stays level.

I'm checking the straight-bounce case next: the paddle starts one cell behind the ball, and since the ball has to reach the wall before landing, it has to stay at the corner to avoid being caught out.

I'm checking the corner case where the ball bounces straight back from the top-right, so the paddle starts in sync with the ball and has to travel the full width to the far corner. Any single missed move there would leave it stranded, so the timing has no slack.

I'm checking how the paddle can tell a straight bounce from a reverse one: if its position matches the ball's x it's a reverse bounce, and if it matches the trail's x it's a straight one. The same-row observation at row 8 is ambiguous about which it is.

I'm considering whether to enforce straight bounces only, so the paddle always ends up directly under the ball. The trouble is that noise could still produce a reverse bounce, and then inferring direction from the trail would send the paddle the wrong way, though the next diagonal observation should reveal the mistake.

I'm checking the lag after a straight bounce: with the paddle trailing by one or two cells it still catches up before the next landing, since a wall turn comes every ten steps. The only exception is when the bounce lands in a corner, where there's no slack left.

I'm now looking at the reverse-bounce case, where the ball ends up at the wall and the paddle moves away from it. If the paddle sits one cell behind the ball, the trail tells me the direction, and if it's level with the ball, the bounce was reverse.

I'm settling on a "Policy D" design: when the ball is moving down, the paddle follows a lead target, and the descent mode covers rows 4 and below, treating the ball as descending when its trail is one row above. The case of the ball at row 3 or higher moving down is still uncertain, since it could bounce off a brick below, so I'm leaning toward treating that as upward mode.

I'm settling on a flight-mode target of x(φ+4) so that it lines up with the descent window at row 4, and I'm considering whether a lead that large is actually safe before I simulate a full 10-step cycle.

I'm working through a flight-mode target of x(φ+4): if the paddle steps straight after a bounce, it chases the landing spot, reaching the wall region before the row-4 arrival. I'm tracing a few steps of that chase to see where the paddle sits when the ball reaches row 4 and whether it has to wait for the next same-row observation.

Now I'm checking the paddle's timing in the descent: at phase 10 it holds at 6 and steps left to 5, then waits through phases 11 to 13 so it sits at 5 for the critical observation at 14 and bounces straight. I'm also testing how robust this is: a single mistaken move on either side still leaves the paddle within reach, so a couple of botches wouldn't break the plan.

I'm working through the paddle's chase after the wall bounce: starting at 9 with the ball at 8 moving left, it steps left each turn to keep up with the target, reaching 5 by phase 14. At phase 16 it's descending, so it creeps left one cell per step to stay inside the window, and it should still be in reach of the ball at row 6.

I'm checking the worst case next: when the ball lands at phase 10 with no wall turn before the landing, the paddle has no slack, so I'm tracing how far it can lag behind.

I'm checking the slack for a couple of other cases: when the ball lands at phase 19, the paddle has to cover nine cells in ten steps, leaving only one step of slack. I'm also checking the case where the ball is at (9,8) after a straight bounce, where the paddle needs seven moves in ten, which leaves three steps of slack.

I'm checking how the paddle's lead holds up when the ball rises above the bricks and later drops back through a gap. In flight mode the paddle keeps tracking a lead target, and once the ball reaches row 4 moving down, the descent window should take over.

I'm working out how a ball moving down at rows 3 or higher behaves, since it might pass through a gap or bounce back off a brick. If I treat it as a descent, the paddle's target would be off by a few phases, and the paddle can only move one cell per step, so it might lag in catching up.

I'm weighing whether the target can be written as one additive rule, a function of the ball's cell plus a function of its trail cell, separately for the rightward and leftward cases. I'd need to check that against every observation type, including the top-wall bounce on row 0.

I'm now sorting the observations by type: up-diagonal ones where the ball moves up, down-diagonal ones where it moves down, and same-row ones at rows 0 through 4. For each, I'll take the phase from the ball's and trail's x-positions, with the wall-corner cases handled separately.

I'm sorting the same-row observations by row: at row 4 they follow the descent target, while at rows 0 through 3 the vertical direction is ambiguous after a brick or ceiling bounce, so I'll keep them in flight mode.

I'm checking the paddle's timing against the ball's path for the two starts: from (0,3) the paddle stays at 4 and the descent window picks it up at 5 and 6, and from (9,3) it shifts to 5 for the next observation.

I'm now going through the paddle's target for the same-row observations at row 8, where the direction depends on whether the paddle sits under the trail or the ball. I'm checking the special wall cases at the edges separately, since they shift the phase used for the target.

I'm working out the target interval for the paddle's two movement units: the right unit should fire when the paddle sits left of the lower bound, and the left unit when it sits right of the upper bound, so each unit's center lands at the bound itself. I'm checking the margin around that center, since a tolerance of roughly a quarter cell with a steep sigmoid should keep both units reliable.

I'm now writing the flight-mode target as a function of the ball's column and its trail, splitting the rightward case (where the phase is the ball's x) from the leftward case (where it's 19 minus the ball's x).

I'm now setting the flight-mode target as a rough additive function of the ball's column and its trail, with a lead of about three to five cells and a turn near the walls. For the descent rows, I want exact windows: the two cells at the ball's projected landing spot, offset by the row, for rows 4 through 8.

I'm now assigning the descent-row tables for rows 5 through 8: each ball row y gets its own pair of right and left tables for the ball's column, and the trail row y-1 gets its own pair, so the target for that observation can be set exactly.

I'm assigning the tables in pairs so each descent row gets its own windows: the ball row's right and left tables, and the trail row's, with the same trail tables reused by the neighboring up-diagonal observations.

I'm now setting up the descent tables for each row: the pair (F_y, G_{y-1}) for the ball's column and the trail's row, with the flight values at the up-diagonal rows falling out of those tables as a byproduct. The shared tables mean I can't set every row independently, so I'll have to check whether the constraints stay consistent or need approximating. I'm formulating that as a pair-table problem: one unknown function of the ball's column and one of the trail's column, constrained by the 20 observation phases.

I'm now working through the cycle of pair constraints, starting from f0 and stepping across the edges to get each consistency condition on the tables.

I'm tracing the cycle of pair constraints edge by edge, pairing each table entry with the phase it corresponds to: for example (6,7) gives φ=13, (8,7) gives φ=8, and the diagonal (9,9) gives φ=10. I'll keep going through the remaining edges until the full cycle closes back at (0,0).

I'm checking the alternating-sum condition over the cycle of edge phases, to see whether the pair tables can be made exactly additive.

I'm checking the cycle of pair constraints against the phase values, and the sum over the odd phases comes out equal to the sum over the even ones. That means a pure shifted position function x(φ + c) fits exactly, whatever the shift. Next I'm testing whether the lower-bound version, the minimum of two adjacent cells, can also be made consistent with the same cycle.

I'm checking whether the wall-corner minimum can also be made additive: its even-phase sum comes out to 40 and its odd-phase sum to 41, so it's off by one in total. That means it can't be fit exactly, and I'd have to spread the one-unit error across the 20 constraints or absorb it at a single flexible spot.

I'm checking whether the lower-bound target can be pushed to 10 at ψ=9 without hurting anything, since at that point the right unit is clamped anyway. Changing that odd-phase value would only make the sum worse, so I'm setting ψ=19 to -1 instead, since any target at or below zero never fires the right unit, and that balances the odd and even sums exactly.

I'm checking the upper-bound version of the paddle target the same way: hi takes the max of two adjacent cells, and its even and odd phase sums come out to 50 and 49. Setting the tie-break at ψ=9 to 10 makes the sums match, so both bounds can be fit exactly.

I'm now reducing the problem to a small set of cycle-consistency checks on the descent tables, which would otherwise mean juggling 360 hand-computed values. The next step is to look for closed forms that make those tables manageable.

I'm now looking at whether the hidden units can be split into dedicated pairs per observation type, with a gating layer to combine them, which would avoid forcing every table to satisfy one shared set of constraints.

I'm now thinking about whether the gated pair units could share descent tables, since each mode only uses its own F_y and G_{y-1} and those sets don't overlap for the descent rows 5 through 8.

I'm trying to make the descent-row tables share cleanly: one pair of units for the descent rows, with the shared entries for the start-of-row case forced to match.

I'm checking whether the shared tables can stay consistent across rows: G_4 is fixed by the row-4 solution, but the row-5 flight table F_5 would then have to satisfy two constraints at once, which looks overdetermined. If that fails, S_4 needs its own unit pair or a special flight-mode target.

I'm checking whether descent mode is even needed for rows 5 through 8, since a flight target of x(φ+4) might cover those rows as well. I'm also considering whether S_4 and D_4 can both use that same point target inside W_4.

Since the trail's row and the ball's row can't both be fixed by one flight target, I'm weighing a row-dependent lead instead: aiming at the landing spot directly for each row. For the downward rows after the first, the paddle would need to hold still at the reverse-bounce position, which shifts with each row.

I'm weighing whether the lead should depend on the row: if the ball bounces at row 3, the landing comes roughly y+1 to y+2 phases later, so a fixed lead could be a reasonable shortcut. I'm leaning toward a constant target around a=4 and am about to check which value works best for flight mode at the D_4 and S_4 observations.

Now I'm weighing how big the lead should be: with a = 4 the paddle sits one step short of the landing spot, with a = 5 it's already on it, and with a = 6 it's one past. A smaller lead means more chasing after bounces, while a larger one turns the paddle early at the walls and pulls it ahead in phase.

I'm weighing a fixed flight target at x(φ+4) against an interval of two cells, x(φ+4) and x(φ+5). The interval would make the paddle lazier and move less often, but it's unclear whether that helps robustness, since the paddle moves on almost every step while following the ball's phase anyway.

I'm settling on a lead of ℓ = 8 − y for the descent rows y = 5 through 8, which gives 3, 2, 1, 0, and a fixed lead of 4 everywhere else, with each target being an interval of two adjacent cells. Next I'm setting up the lookup tables V_R and V_L so that each one is the lower or upper bound of the paddle target at its lead.

I'm checking whether one shared pair of hidden units can cover all the row cases: the up, down, and same-row tables each seem to pair up with distinct F and G tables, so they shouldn't conflict if the same value is used across rows.

I'm checking the overdetermined chain: fixing G_4 forces F_5 to satisfy too many constraints at once, and that propagates through G_6, F_7, G_8, and finally the row-8 pair with F_8, while F_4 feeds G_5 and F_6 on the other branch.

I'm treating the descent constraints as hard and the flight ones as soft, so each descent row y=5 through 8 pins down its own pair of tables: D_5 fixes F_5 and G_4, D_6 fixes F_6 and G_5, and so on down to D_8. The flight constraints can then absorb whatever slack is left over.

I'm working out whether the by-product flight targets that come from solving the descent tables are sensible, since each descent pair fixes its own constants and leaves the flight constraints to absorb the slack.

I'm testing whether the descent tables can be written as an arbitrary function of the ball's column plus a term that depends only on the direction, with a linear term in the column for the quadratic case. That would explain why the constraints look tangled.

I'm checking the parity trick at the wall cells: it only affects the same-cell pairs at the edges, flipping a value by one there, and elsewhere it cancels out. Since the two tables can be any functions of the ball's column, the only real constraint is that the edge values add up correctly, so I'm considering how to express the target x(φ + c) in terms of the column b and the direction, with the reflection at the wall handled separately for moving right.

I'm working out the paddle's bounce geometry in the wall-reflection case: unreflected, the target reduces to a linear function of the ball's column, with the direction term giving the offset. Near the walls the reflection breaks that pattern, so I need to solve the cycle of tables numerically for each lead value c.

I'm weighing a gated design instead of the hand-solved cycle, since separate units per mode would keep the flight and descent tables from interfering. That means roughly ten systems of twenty equations, which is a lot of hand propagation with real room for error.

I'm setting up a gate unit to tell descent mode apart from the other cases: it should fire only when the ball is in rows 5 through 8 and the trail sits one row above it. I'm using a linear score that takes the ball's row minus the trail's row, with a penalty for ball rows 4 and up, so it comes out high only for a downward step.

I'm adding a gate for paddle-bounce mode that fires when the ball and its trail are both on the bottom row, plus a matching pair of units for deciding the paddle's move there. The output layer then combines the three R-side units (flight, descent, bounce) and does the same for the left side, with the tables for each mode kept separate.

I'm considering splitting the descent case into separate units for each wall fold, since the unreflected linear formula works but the wall reflections break it.

I'm now converting the wrap-around at the walls into a single unfolded coordinate, so that "the paddle is left of the target" becomes two linear inequalities on the unfolded position and the paddle column.

I'm now working out the left-wall case: the window's lower bound folds as max(u − 1, −1 − u), so "the paddle is left of the target" becomes an OR of two threshold conditions rather than an AND.

I'm now writing the lower bound in terms of an unfolded coordinate u, where the rightward case uses a window that folds at the right wall and the leftward case folds at the left wall, so I'm trying to express both through a single expression.

I'm now folding the lower bound on the left side: with u as the unfolded position, the leftward window's low end is the larger of u − 1 and −1 − u, which is |u| − 1 away from the center and 0 at u = 0. I'm also starting on the upper bound for the rightward case, where it should be the smaller of u + 1 and 19 − u.

I'm comparing the lower bound for the rightward case, lo⁺ = min(u, 18 − u), against the leftward one, lo⁻ = max(u − 1, −1 − u), and they don't match, since the leftward version is shifted down by one. I'm checking whether the shift can be absorbed by a constant offset in the paddle comparison, so that one unit serves both directions.

I'm folding the lower bound into a single expression: with u' shifted by the direction term, the rightward and leftward bounds are both expressible as a min of a max, which should hold for either direction since each branch only matters on its own side of the walls.

I'm writing the left-side condition as a min of two terms, hi⁺ on the rightward side and hi⁻ on the leftward side, and turning each comparison into threshold units on the shifted coordinate u'.

I'm folding the ball's offset into a single coordinate u' = b + (ℓ + 0.5)(b − t), where ℓ is 8 − y for descent rows and 4 otherwise, so the rightward and leftward wall cases can both be handled by one set of threshold units.

Now I'm working out the descent units, where the coefficient on the ball's row depends on how far the ball is above the bottom. That clashes with the flight units, which use a fixed lead, so I'll keep the two sets of tables separate.

I'm now turning the two "OR" cases into a sum of AND-style units, so the output layer can decide which side wins by comparing logit totals against a fixed threshold.

I'm now checking the wall-same cases, where b equals t and the direction comes out as zero instead of ±1. The linear formula gets those two pairs wrong, so I'm considering small corrections on just those positions that would fix the sign without disturbing the neighboring pairs.

I'm working out the parity trick for the wall-same pairs: a correction on the odd-ball-row positions and the even ones alternates so that the (9,9) fix of δ is balanced by a −δ at (0,0). For the direction term, the corrected value at (9,9) should use d = −1 instead of 0, which means the offset needs to be chosen to match that sign.

I'm writing the closed-form expression for the unfolded coordinate, and the wall-same corrections give a term that is +κ at (0,0) and −κ at (9,9) with κ = ℓ + 0.5, which is exactly what's needed to fix the direction sign there.

I'm weighing whether to encode the wall-fold behavior as six threshold units per mode, which fits the unit budget, or to write out exact per-cell tables with two units per mode. The formula route is less error-prone to write by hand, even though each unit still needs a weight for every ball and trail cell.

Writing the weight tables as strided ranges now...

Now I'm weighing whether to spell out the weight tables as strided ranges, since the formula stays the same for each column but the layout repeats across rows.

I'm weighing whether a constant lead of one step is enough, or whether the lead should scale with the ball's row so the paddle can arrive early and wait.

I'm now checking how the paddle should lead the ball on the way up: when the ball is at row 8 right after a bounce, the target window is the two cells just ahead of it, and the lead for the higher rows grows by one per row.

I'm checking how the paddle's lead should grow as the ball climbs: each row up adds two phases to the target window, so the paddle keeps chasing but the target recovers once the wall shows up. That suggests using one lead that depends only on the ball's row, so the same unfolded coordinate works for both directions. I'm starting to write that unfolded coordinate with the row-based lead.

I'm trying to make a single additive decomposition work for the product term ℓ(by)·(b − t), since the trail's weight can't depend on the ball's row directly. The trail row can be the ball's row or one off from it, so I need to check whether the cross term can be split into separate ball and trail contributions.

I'm checking whether the lead can be a single function of the ball's row, and the trail's weight can't follow the ball's row directly, so the cross term doesn't split into separate ball and trail pieces. I'm considering whether per-row tables for each observation type could still be consistent, by counting the unknowns against the constraints.

I'm checking whether the per-row lead can stay consistent across the up, down, and same-row cases. Counting the constraints against the unknowns, there are far more equations than free values, but the linear form reduces them: every row's lead has to match across the three cases, which forces one shared lead per ball row.

Checking whether the lead can depend on the ball's row alone: the per-row constants have to agree across the up, down, and same-row cases, which seems to force them to match in pairs across neighboring rows.

I'm finding that the lead can't vary by row in a linear form: the offsets for up, down, and same-row observations share the same ball-row coefficient, which forces all the leads to match. So a single constant lead is the only option unless I move to non-linear, reflection-aware tables.

I'm working through the earlier idea where the descent constraints fix each pair of F and G terms up to a constant, and the flight cases come out as by-products of those sums. In the linear, unreflected regime, the F terms come out as (9 − y)·b plus a constant, and the G terms as −(8 − y)·t minus that same constant.

I'm seeing that a row-dependent lead can't work as a single linear unit, since the up, down, and same-row constraints tie every row's lead to the same value. The by-products of the descent constraints come out as 3b plus a constant, which doesn't match the b + ℓ·d shape I need. So a single unit can't do it, and I'll have to gate the two modes.

I'm settling on a gated two-mode design, since a single linear unit can't give the row-dependent lead. One pair of units handles the flight target with a fixed lead, another pair handles the descent targets by row, and a gate switches between them based on whether the ball is in the descent rows.

I'm settling on how to combine the two modes: the gate GD switches between the flight targets and the descent targets, and a separate pair of units handles the case where the ball and trail both sit on the top row. Then I'm setting the output logits so that the R and L outputs get a constant offset, so that "no action" wins when none of the six layer-two units fire.

I'm settling the output layer so that "no action" wins by default: each of the six gated units adds a fixed offset, and the R and L logits get a bias so that only a firing unit lets them beat the no-op logit.

I'm considering whether the paddle's extra lead for row 8 could come from the flight tables alone, without a separate gate, since the descent unit already handles the cases where the ball row is 8.

I'm checking whether the flight unit can take its own free pair for the row-7 case, since the descent unit already covers row 8 through its gate. That leaves the paddle-on-row-8 target to be fit by a separate table, and I'm working out what the remaining constraints require of it.

I'm now checking the paddle-mode target: if the paddle sits on the ball's cell, the straight and reverse cases need different phases, so I'm working out what the lead should be for each.

Now I'm working out the paddle's target in paddle mode. The ball's next phase flips relative to the paddle, so a straight bounce means moving with the ball's direction and a reverse bounce means moving against it, except near the walls where the target window gets too close to matter. At the right wall, a straight bounce pushes the paddle left, while a few steps earlier the target sits right where the paddle already is, so it holds still.

I'm checking the paddle's simple rule near the right wall: when the ball is at column 9 and the paddle at 8, a straight bounce would have the paddle move toward the wall, and I'm weighing whether that one-step error is acceptable since later steps fall back to the flight target.

I'm now setting the paddle's rule in the monitored cases: since the paddle only matters when the ball is on its cell, I need a threshold that depends on the paddle's own position. Each ball-and-trail pair leaves two possible paddle positions, and each needs its own correct move, so I'll build the right-move unit around that dependence.

Now I'm checking the paddle-mode cases, where the straight-bounce target for each ball row sits just to the right of the paddle, and seeing whether the on-condition can be written as a simple threshold on the paddle position.

I'm checking the paddle-mode targets for the cases where the ball is on the paddle's cell, and listing the desired action for each. For the straight-bounce cases the paddle should keep moving right for the lower ball columns, then hold at column 7 and move left near the right wall. For the reverse-bounce cases at the left edge, the first one calls for a move right, and the next few are cases where the paddle should hold still.

I'm checking the rest of the paddle-mode cases for the reverse-bounce column, where the desired move is left for most ball positions, with a few exceptions near the left edge. Each pair gives a straight-bounce and a reverse-bounce action, and I'm noting that both sets are ordered so that the right move comes for lower paddle positions and the left move for higher ones.

I'm working out the threshold for the R unit in the descent-adjacent cases: it should switch on when the paddle is one cell below the ball's row and stay off when it's level, which means setting the threshold between those two paddle positions. Near the edges of the board, the threshold has to stay clear of the wall cases so the unit doesn't fire when it shouldn't. I'm now starting on the matching threshold for the L unit.

I'm checking the threshold bounds for the L unit in the mirrored case, where the ball moves the other way and the straight and reverse paddle targets swap sides. Working through each ball column from the mirror, the paddle should move left for most of them, with only a few cases where it holds still or moves right.

I'm now working out the threshold bounds for the R and L units across the wall-adjacent paddle cases, mapping each ball column to the paddle positions where the unit should switch on or stay off. The same-cell corner case at (9,9) has its own fixed target, with the paddle needing to move left toward the interval near columns 4 and 5.

I'm checking the reverse-bounce cases for the wall pairs, where the requirement for the R unit is to be on at the low end and off at the high end. Next I want to see whether the additive form F_8(b) + G_8(t) can match those targets, since the alternating-sum condition around the 20-cycle looks like it leaves enough slack to work.

I'm checking the b=1 reverse case, where the target requires the paddle to stay put at column 1 rather than move right, so the threshold for that pair has to drop to 1 instead of 2.

I'm now trying to fit exact values for the paddle's left and right units using the two additive forms, one over the ball's column and one over its trail. The current target bounds leave some slack, so I'm testing whether a clean assignment exists across the pairs.

Trying a simple form here: each side's threshold gets a base value from the ball's column plus a per-column offset, with the offsets chosen so the alternating constraints around the cycle close up.

I'm working out the additive split for the R-unit thresholds: writing each side as a function of the ball's column and its trail, the sum comes out to max(b, t) for the adjacent-column pairs, and the wall-corner case still has to be checked against the same form.

I'm checking whether the b=1 reverse case can be pinned down: its target is to hold still at column 1 rather than move right, so the threshold needs to sit at 1 instead of 2, and the alternating-sum setup still has to close around the cycle.

I'm testing whether the R-unit thresholds can be split into a per-column base plus an offset, since the wall cases still need a check.

I'm now trying to tune the endpoint values individually, since f(9) and g(8) need adjusting to bring A_9 into range, and B_8 has the same problem.

I'm adjusting the endpoint values now: pulling g(8) and g(9) each down by one, and f(8) down by one, so the boundary cases for B_8, A_8, A_9, and B_7 fall inside their target ranges.

I'm lowering f(8) by one to fix the boundary cases, then checking the neighboring pairs. Those all land inside their target ranges, and C9 drops to 7.5, still within bounds. The low end is short too: A_1 and B_0 both need to reach at least 2, so I'm raising f(0) by one to cover them.

I'm settling the P-mode table for the R unit: the b-odd entries come out to b/2 and the b-even entries to b/2 + 1, after adjusting f(0) and g(0) upward to clear the low-end bounds.

I'm settling the end-case values now: f(0) and g(0) go up to 2 and 1.5, f(8) comes down to 4, and g(8) and g(9) each drop by one so the boundary pairs fall inside their ranges.

I'm checking the R-unit table against the L-unit mirror, and wondering whether flight mode needs exact values or whether a looser scheme would do. Before committing to the flight-mode details, I want to confirm the P-mode assumptions hold: paddle positions outside the ball's row and trail can't occur at a non-terminal step, and row 8 can only be reached by a paddle bounce.

I'm weighing whether the flight-mode targets should be a two-cell interval or a single point, since the interval leaves some slack for the paddle's dead zone. I'm also setting up the two lookup functions, one for each direction, with a small correction at the wrap-around angle.

I'm working out how the paddle settles into a trailing position: each time the interval shifts, the paddle steps to the ball's trailing cell, so in steady state it sits at x(φ + a). I'll take the interval version for its hysteresis, with a = 4 as the lead.

Now I'm settling on the descent rows: with the paddle already at the straight-bounce cell L0 from the previous flight move, each descent row keeps it there, so the ball bounces straight back.

I'm weighing a=5 against a=4 for the descent rows, since the paddle has to reach the straight-bounce cell L0 before the ball arrives. With a=4 it gets there in time, and a single extra botched move still keeps it inside the row's target interval.

I'm weighing whether a larger lead value, like a=6, would work in the flight rows. It would put the paddle further ahead, and at the descent row it would end up one cell past the target interval, which I can correct with a single move back.

I'm weighing how far ahead the paddle should lead in flight mode, and whether a larger lead causes overshoot at the descent rows. Once the paddle has made a straight bounce, it starts from a lag behind the ball, so I'm checking how much lead it can gain at a wall turn.

I'm now checking where the paddle ends up if it keeps a lead of four cells: the target slides toward the wall, turns back, and the paddle has to move to meet it at the next observation.

Checking the paddle's meeting point: at obs phase 7 it moves right to 7, then holds at 7 at phase 8, and steps left at phases 9 and 10. By phase 10 it sits at x(14), four cells ahead of the ball, so the lead is restored.

I'm now checking the worst case: if the ball lands soon after a bounce with no wall turn in between, the paddle has less time to close the lead. I'm testing a landing two steps after a wall turn, tracking the paddle step by step as it chases the ball rightward.

I'm checking the paddle's meeting point against the flight interval: it reaches 7 at obs 7, which falls inside the descent target, so it holds there through the remaining descent rows.

I'm checking the worst case next, where the ball lands right after a reverse bounce with the paddle starting at the far wall. That leaves about nine moves to cover in ten steps, so there's only one spare move, and I'm tracking how the paddle chases the ball rightward.

I'm checking the worst-case corner where the ball starts at the left edge with the paddle also at the wall, so the paddle has to cross nine cells in ten steps. Tracking it step by step, it reaches cell 9 just in time with one spare move, so a single botched move is survivable but two would not be.

I'm settling on the overall policy: flight mode tracks a lead-4 interval, descent rows hold the wall-target cells for D_5 through D_8, and P-mode handles the bounces. I also want to gate the +1 correction so it only applies to downward-moving balls in rows 5 through 8, and I'm considering a logit margin of 20 for the softmax.

I'm working through the layer-2 AND gates with tanh saturation, where the gate output is about ±0.9993, and the logit margin M is near 20 with K set to 4.

Now I'm working out the lookup tables, starting with the phase mapping from each ball position and trailing row.

I'm filling in the lookup tables now: mapping each ball position and trailing row to a phase, and defining the lower bound of the paddle's target interval for each phase, with the edge cases at the wrap-around checked.

I'm tightening up the boundary tables for the paddle's target interval: the lower bound gets a wall tweak at one end, and the upper bound a matching one at the other. Checking the even-indexed sums, the lower-bound values come out to 40 so far, and I'm continuing through the odd indices.

I'm checking the upper bounds of the paddle's target interval and confirming the sums come to 50 on both parities. I also note that shifting by an odd or even amount keeps the totals equal, and that mirroring the board maps each phase to the one ten steps later.

I'm checking that the lower and upper bound tables are mirror images of each other, so the left-moving table follows from the right-moving one by reflecting the board. I'm tracking how the sums and the wrap-around entries line up under that reflection.

Now I'm setting up the L-unit weights as mirror images of the R-unit weights, flipping the column index so the ball and trail terms map to 9 minus their x.

Now I'm building the flight-mode lookup for the right-moving paddle unit, matching each phase's target to the lower bound four cells ahead, with the wall tweak at phase 15.

I'm working out the lookup values for the right-moving unit, listing the target bounds for each phase and checking that the even and odd sums both come to 40.

I'm solving for the flight-mode table by fixing f(0)=4 from the starting state, which gives g(1)=-1 from the next cell, and I'm continuing to pin down f(2) and the rest of the row values.

I'm solving the flight-mode table by working down the diagonal: with f(2)=7 and g(3)=-6 fixed, I get f(4)=14, then g(5)=-15, f(6)=23, g(7)=-22, f(8)=28, g(9)=-25, and f(9)=29. Now I'm moving on to the cells along the trailing edge at row 9.

I'm filling in the flight-mode values for the remaining cells: with f(7)=26 from the row-7 step, g(6) comes out to -19, and that fixes f(5)=19. Working down the trailing column, g(4)=-10 follows, then f(3)=10, g(2)=-3, and finally f(1)=5 from the cell at row 1.

I'm checking that the right-moving flight table closes consistently: starting from f0=4 and stepping back to phase 1 gives 5 again, which matches. I'm now reading off the full set of values for both the f and g rows.

Now I'm checking the left-moving flight table by reflecting the right-moving values across the board, so each entry lines up with the mirrored phase.

I'm checking the L-unit against a couple of cases: for ball at column 5 moving right, the hi bound is tweaked to 10, so the L unit stays off for every paddle position, and the computed value p - 10.5 confirms that. For the ball at column 3 moving left, the L unit should only switch on once the paddle reaches column 9, and I'm setting up that sum to verify it.

Now I'm checking the left-moving flight tables against the mirror relation, and noting that the flight-mode values can stay the same for every row, since the P-mode units handle the bounces.

I'm now checking the P-mode constraints on the shifted row-8 table, listing the required values and inequalities for the cells on both diagonals, with the fixed flight-mode g values in place.

Checking the paddle's response in the P-mode again, I see that one fixed flight table can't cover the bounce cells without breaking the gap condition, so the bounce cases need their own units and gating. I'm also weighing whether simple straight-and-reverse rules could replace the exact tables, though the end tweaks probably make that too fragile. Now I'm turning to the descent tables.

I'm setting up the descent tables for each row from 5 to 8, each pairing a ball unit with the trailing unit one row up and using a target offset that shrinks as the row gets closer to the paddle. I'm fixing the gauge at g0 = 0 and then chaining through the cycle of ball and trail positions, solving for each f and g in turn from the target values.

Still working through the descent tables: I'm chaining the remaining f and g values from the target bounds, moving from the paddle side back up through rows 6 and 7.

I'm working through the remaining descent values for the ℓ=3 table, solving for f3, g2, and f1 from the target bounds and checking that the cycle closes back to phase 1. I'm also setting up the lower-bound lookup values that the ℓ=3 case needs.

Continuing the descent table for ℓ=3, I'm solving for each value in turn from the target bounds: g0=0, then f0=3, g1=-1, f2=6, and g3=-6. I'm about to work out f4 from the next cell.

Still solving the descent table: with g8 and f7 fixed, I'm working back through the trailing cells to get g6 = -17, and I'm about to work out f5 from the target at phase 14.

Now I'm checking the ℓ=3 descent table by solving it out in full: after the earlier steps, f5 comes to 18, which gives g4 = -10 and f3 = 9. Then g2 = -3 and f1 = 4, and the closure check holds because f1 + g0 matches V(1) = 4.

I'm tabulating the target values for the ℓ=2 descent table, starting with φ=0 through 17 and noting the tweak at φ=17.

Working out the ℓ=2 descent table now, chaining the values through from g0 = 0 and f0 = 2 while tracking the tweak at the lower end of the cycle.

Now I'm working through the right-moving descent values for the ℓ=2 table, carrying the chain down to f1 and checking it against the closure at phase 1.

Now I'm working out the ℓ=1 descent table, with the target values for the trailing-edge lookup and the tweak at φ=18.

I'm finishing the ℓ=1 descent table by chaining the remaining values: g1 = -1, f2 = 4, g3 = -4, f4 = 9, g5 = -7, f6 = 14, g7 = -10, f8 = 19, g9 = -13, and then f9 = 7.

Still working out the ℓ=1 descent values, now filling in the f and g chain down the trailing column.

Now I'm working out the ℓ=0 descent table, with the target values for the trailing-edge lookup and the tweak at φ=19.

Still working through the descent table for ℓ=0, solving the trailing cells in order: f4 = 6, g5 = -3, f6 = 9, and g7 = -4. Then I'm moving on to f8 = 12 and g9 = -5, and from there f9 = 13, g8 = -4, f7 = 10, g6 = -3, and f5 = 7.

Now I'm finishing the ℓ=0 descent table, checking f3 = 4, g2 = -1 and f1 = 1, and confirming that the cycle closes back to V(1).

Checking the descent values for the ℓ=0 table against the target windows, and each one comes out consistent. Next I'm setting up the descent tables for rows 5 and 6.

Now I'm checking the remaining descent tables: the row-5 trail entry pairs with ball row 7's f^{(1)} and trail row 6's g^{(1)}, and ball row 8's f^{(0)} with trail row 7's g^{(0)}. The other rows fall outside the gate, so their units stay off. I also considered folding the descent and flight units together, but they'd conflict because both use the same shared flight values, so I'm keeping them separate.

Now I'm defining the gate for the descent units: it should fire only when the ball is in rows 5 to 8 and the trailing unit sits exactly one row above it. I'm building that as a weighted sum over the ball and trail cells, with a large negative weight for the rows that should stay off.

I'm checking the gate for the descent units: with the ball-row weights set to y for rows 5 and up and to a large negative value below that, and the trail-row weights set to -y, each valid descent pair scores +1, the same-row pair scores 0, and the upward pairs score -1. With a threshold at 0.5 and gain 8, the descent pairs land at +0.5 gain, so the gate fires cleanly on them while staying off everywhere else. Now I'm turning to the gate for the paddle.

Now I'm working out the paddle-mode units, which need tables for the ball and trail on row 8. I'm checking the gate for them: it should score +0.5 only when both the ball and the trail sit on row 8, and go negative otherwise. For the straight case, where the paddle matches the trail, I'm deriving the phase from the ball-and-trail pair.

I'm working out the P-mode phases for the wall-edge cases: when the paddle is on the ball's side, the phase flips to 19 − b for a rightward ball, and I'm also checking the corner situations at (9,8) with a down-left direction.

I'm working through the bounce cases at the bottom-right corner now: when the ball is at (8,8) moving down-right and the paddle sits under the ball, the ball ends up at (9,8) heading up-right, which gives phase 9.

Next I'm working through the bounce cases at the bottom-right corner, checking which phase the ball lands on when the paddle sits under it versus one cell over. I'm tabulating the flight intervals for the rightward pairs, starting with the straight case.

Now I'm checking the paddle cases for each ball column: when the paddle sits under the ball, the reverse interval gives the right-moving results for b=1 and the null result for b=2, and b=3 goes left.

Now I'm checking the right-moving cases for the paddle bounce, where the ball's column and the trail's column decide whether the interval sends the ball right, left, or nowhere.

Now I'm checking the reverse-bounce cases for the downward-left pairs, working out the flight interval for each ball column and where the paddle sits relative to it.

Now I'm working through the reverse-bounce cases for the upward-left pairs, checking the flight intervals for each ball column and where the paddle sits.

Now I'm working out the reverse-bounce cases for the right-moving pairs, checking which column of the trail the paddle occupies, and finding the right threshold for the unit.

I'm now settling the reverse-bounce cases for the P-mode units, checking which thresholds each column needs so the right-moving and left-moving results come out correct. I'm working through the base values for the bounce function f across the ball columns, and I'm about to tune the edge values at f(0) and f(8) and the trail values for g.

Checking the tabulated values against the pairing rule: the fractional entries line up with each ball column, and so far each match comes out as expected.

Now I'm checking the flight-interval values for the rightward pairs, confirming each one lands on the expected sum, and then running the same check for the leftward pairs.

I'm checking the reverse-bounce values for the ball-trail pairs, starting with the b=1 case where the paddle sits under the ball, and confirming the sums against the targets.

Checking the remaining pairs for the right-moving case: the b=8 pair comes out to 7, which stays off for paddle position 7 as required. Now I'm finishing the b=9 pair, which sums 4.5 and 3.5 to 8.

Now I'm checking the remaining pairs on the rightward-ball side, where the sums land on the right values for b=2 through b=5, and I'm about to test the b=6 pair against paddle positions 6 and 7.

I'm checking the last few gate margins: the descent and upward pairs come out to the right sums, and the wall cases at (9,9) and (0,0) land where they should. Every margin holds at 0.5 or more, so the weights look settled.

I'm checking that the L unit is the mirror image of the R unit, using the board's left-right symmetry. For the case with the ball at 9, trail at 8, and paddle at 8, I'm plugging in the mirrored values f(0), g(1), and the paddle offset to confirm the sum works out.

I'm checking the L-unit against the R-unit for the (5,4) case at p=4, where the R-unit sum comes out to 0.5 and so fires.

I've confirmed the paddle-mode tables are done, and the L-unit checks out as the mirror of the R-unit. Now I'm wondering whether the same-row cases in the flight mode, where the ball and trail sit on the same row, are handled properly by the same phase inference.

I'm checking the wall cases for the same-row observations, confirming that a horizontal clamp flips the direction so the position pair still tells me which way the ball is heading. Then I'm testing the case where the ball sits at x=9 and the trail matches it, to see whether a ball moving right could produce that same pair.

Next I'm working through the descent-mode case for ball row 7 moving down, where the paddle has to land on a cell in the window set by the ball's phase.

Now I'm tracing the flight-mode sequence from reset: the ball starts at (0,3) with the paddle at 4, and I'm checking the R and L units against that case, where the right-unit comes out negative and stays off.

Now I'm checking the descent case where the ball reaches row 5 and the paddle window is set by its phase, confirming that staying at 5 is the right move.

Now I'm tracing the descent-mode sequence, checking the paddle window for each row as the ball drops toward the bottom.

Now I'm checking the paddle-bounce case for the ball at column 5, where the paddle sits right under it. That gives a straight bounce, so the vertical direction flips to up-right. Next the ball moves to column 6 with the trail at 5, and the right-moving check for the P unit comes out on.

Next I'm tracing the bounce at the brick: the ball moves up-left to (8,3), which flips it to down-left with the ball at (8,4) and the trail at (9,4).

Checking the ball's path down the board, I see it reach row 8 at column 4 and bounce straight off the paddle at 4, heading up-left. I'm now setting up the next paddle check for that position, where the paddle would have to be at 3 to bounce it back.

Now I'm checking the paddle's straight bounces at the left edge, where the ball's x, trail, and paddle offsets all line up with the mirror-image rule for the L unit.

I'm checking how the paddle reacts to sticky events during the wait and the flight, where a steady move covers the two-cell lead. If the paddle overshoots by a cell on the turn, the next intervals pull it back in time, so it still reaches the descent window with three steps to spare.

I'm checking how a botched paddle move affects the timing. If the paddle misses once or twice, the remaining steps still bring it to the window by the time the ball reaches row 7, and even a third miss only just makes it in time.

Next I'm checking the botch-recovery scenarios at the descent transitions, where a single missed paddle move still leaves enough slack to reach the window, but a chain of three misses near row 7 would push the paddle out of range.

I'm checking how the paddle recovers from a botched move in the final stretch before the descent. A single miss or even a double miss still leaves the paddle in the window in time, but a triple miss in a row would leave it one cell out when the ball reaches row 8.

I'm thinking through the paddle's steady-state behavior: it trails the ball's phase, sometimes moving with the ball and sometimes against it when a wall turn is ahead. If a botched move makes it overshoot toward the left in the ball's direction, it ends up past the L0 cell, toward L1.

I'm working out what happens when the paddle's lead is absent after a straight bounce, since it then chases the ball until a wall turn gives it the lead. I'm also noting that a three-botch chain near the landing only gives roughly a 0.1% chance per cycle, which would still be long enough to reach the step cap in practice.

I'm working out how far the paddle is from the landing window for each starting phase after a straight bounce, since the distance determines how many spare moves it has.

I'm working out how far the paddle can drift before the landing window, and for starting phases up to 5 the slack is simply twice the phase, since the paddle is already close to the window.

I'm checking the worst case for the paddle's slack: a ball at (1,8) moving right, reached either by a straight bounce from (0,8) or by a reverse bounce off a ball at (2,8) moving left. In both paths the paddle starts one cell from the landing window, which leaves only about two spare moves.

I'm checking the corner cases now, where the paddle has the least slack. If the ball lands at phase 0 or 19, the paddle starts at the wrong edge and has only about one spare move. So I'm wondering how often the ball actually lands in that corner.

I'm checking the corner cases where the ball lands at phase 19 or 0, since the paddle has only about one spare move there. I'm weighing whether a single botched move at the transition is enough to break the window, and how often that double-botch could actually happen.

Now I'm checking the reverse-bounce case at L1, where the ball arrives from the far side and the paddle has to flip the direction instead of going straight.

I'm confirming the reverse-bounce phase comes out to 18 minus the critical phase, which is consistent with the earlier inference. Next I'm checking whether the descent window is still reachable when the paddle starts far away after an unusual reverse bounce.

I'm working through how the paddle should move for the descent. The ball's phase and the paddle's lead decide whether it reaches the landing window in time. Next I'm setting up the layer-1 units for the gating logic, starting with the flight and descent right and left detectors.

I'm laying out the layer-2 gating units now, each one firing only when its layer-1 detector and gate signals line up, with the paddle-chase and descent pairs set to match.

I'm checking whether the layer-1 units are always saturated: some may sit near zero where their table entries are zero, but the AND gates still switch the gated-out units off, since RD + GD - 1 stays between -3 and -1 when the gate is near -1.

I'm now setting the output logits: the no-op action gets bias zero, while left and right each get a bias of 2M so that one active gate flips the logit to +M and none active leaves it at -M. The other three actions are pushed down with a large negative bias so they never get picked.

I'm checking the numbers on the output logits: with M=20, a wrong action is off by about 3e-7 or 6e-7, which is negligible. I'm also confirming that the layer-1 pre-activations keep a clear margin, so the float arithmetic stays exact.

I'm checking the flight-mode units against every observation type where they should fire, especially the upward-moving cases in rows 5 to 7, and confirming that the gate units stay off there. For the descent observations at row 8, the descent gate is on while the paddle gate stays off, and the numbers still work out to the right sign.

I'm checking the descent and paddle unit tables, where anything outside the defined rows is left at zero. Next I'm weighing whether a lead of 4 is the right choice, and whether the paddle should wait at L0 after a straight bounce or move to L1 for a reverse one.

I'm now checking the reverse-bounce case from the other side: the paddle sits at the ball's position, and the landing window is measured from there, leaving roughly 9 or 10 cells of distance depending on the phase.

I'm checking which bounce leaves the paddle better placed. For a ball at phase 5 moving right, a straight bounce leaves the paddle just one cell from the landing window, while a reverse bounce leaves it three cells away.

I'm comparing the two bounce options for a ball at (1,8) moving left. Going straight leaves the paddle with 3 spare moves, while a reverse bounce leaves only 1, so the straight bounce is the better choice here.

I'm checking which W cell the paddle reaches first when the ball lands from the other side: if it comes from the left, it hits L1 at cell 7 before cell 8, so a reverse bounce is the natural choice there.

I'm working through the paddle's slack once more: with the ball at (7,8) moving right, the paddle is four cells from the next landing window and has about six spare moves. I'm also weighing whether to add a preference for L0 when there's time, but I'll leave that out for now and turn to cycles longer than ten, which look fine, before checking how the flight interval behaves at the walls.

Next I'm checking the trail channel to confirm it holds the ball's position from the step before, and that after a paddle bounce both the last and current positions sit on the same bottom row.

Now I'm checking how the observation channels are indexed: each cell gets six channels, with the paddle, bricks, ball, and trail in channels 0, 2, 3, and 4, so I can confirm the lookup is right.

Now I'm writing the weights for the ball and trail channels, and for the paddle row.

Writing weight tables for the paddle row...

Now I'm scaling the weights and setting the bias for the layer-1 units, keeping the ordering of the statements in mind. For the mirrored left-side units I'm filling in the ball, trail, and paddle columns using the reflected positions.

Now I'm filling in the trail and paddle tables per column, since the flight units are row-independent. Writing the full weight layout for those two units would mean dozens of strided assignments, so I'll group them by row instead.

Still writing the weight tables, filling the flight units' ball and trail channels column by column with strided fills.

Still writing the weight tables, deciding whether to fill the strided ranges with scalars or explicit lists.

Still writing the weight tables, now deciding whether to fill the flight units row by row with explicit lists or column by column with single values.

Still writing the weight tables, now deciding whether to fill the flight units' trail channel row by row with explicit lists or column by column with single values.

Still writing the weight tables, now weighing whether explicit lists per row are safer than one-line fills per column for the strided ranges.

Still writing the weight tables, now laying out the flight units' rows explicitly, with the paddle row and gate weights to come after.

Still writing the weight tables, now scaling the ball and trail columns and filling in the gate rows, with the paddle and gate weights to follow.

Still writing the weight tables, now deciding to scale the layer-1 columns by 10 instead of 8, since multiplying by 10 is simpler to do by hand and still saturates the units.

I'm switching the tables to be written directly at ten times the scale, so the flight and paddle values are fixed integers and the scaling step can go. I'm also rechecking whether the flight-mode logic still holds when the phase inference is wrong, especially for the first observation after a paddle step.

Still checking the bounce edge cases, especially whether a brick just below the ball flips its direction before it lands.

Checking the descent-mode table against a concrete case now: with the ball at (7,5) and the trail at (8,4), the landing window comes out as cells 3 and 4, and both the right-bounce and left-bounce formulas give the expected values.

I'm checking the descent case for a ball at (5,7) with the trail at (6,6): the right-bounce formula gives a landing window of 3, and the left-bounce formula gives 4, both matching the expected values. Then I'm running the same check for a ball at (4,8) with the trail at (5,7), where the right-bounce result is 3 and I'm partway through the left-bounce calculation.

Now I'm checking the descent-mode formulas at the far wall, where the ball at (9,8) with the trail at (8,7) should give a landing of 9 for the right bounce and 10 for the left.

Now I'm checking the descent cases near the left wall, with the ball at (0,8) and the trail at (1,7), where the left bounce only applies when the paddle is at cell 1 or beyond.

Still checking the descent cases, now with the ball at (2,5) and the trail at (1,4), where the left-bounce formula still needs working through.

Checking the descent cases for a ball at (2,5) with the trail at (1,4), I get a landing window from 5 to 6. For the ball at (0,5) with the trail at (0,4), the window comes out as 3 to 4, and for the ball at (8,5) with the trail at (9,4) the left edge is 4, with the right edge still being worked through.

Still checking the descent-mode cases, now verifying the lower bound for a ball at (1,6) with the trail at (2,5), which lands on 0, and the upper bound, which lands on 1.

Checking the flight-mode samples now: for a ball at (7,7) with the trail at (6,8), the landing window comes out to 7 on the lower bound and 8 on the upper. For a ball at (9,5) with the trail at (8,6), the lower bound is 5 and the upper is 6, and I'm verifying both against the formulas.

Now I'm checking the flight-mode cases where the ball is at row 4 and the trail at row 5, where the left bounce comes out to 0 and the right bounce to -1, and then the same for a ball at row 5 with the trail at row 4, where the bounce lands at 9 and 10.

Now I'm working out the worst case at the wait transition: if the paddle overshoots on D_5 and D_6, it ends up past the landing window, so I need to check how many botches that takes to lose the ball.

I'm now checking the paddle timing for the case where it overshoots: if it botches at D_5 and D_6, it lands past the window, so the ball is lost only after three consecutive botches, roughly a 0.1% chance per cycle. With the paddle arriving early at L0 and the corrective moves, the remaining botch cases at D_7 and D_8 still work out.

Now I'm comparing a paddle offset of 3 against 5 for the wait transition, and both need three consecutive botches before the ball is lost.

I'm settling on keeping the paddle lead at 4, since starting it at 5 gives the same triple-botch failure but less slack on the leading side. The ball bouncing off bricks in the wider region doesn't change the cycle length, so the paddle's phase lead still holds. Next I'm listing the remaining double-botch death cases, starting with corner landings where the slack is only one or two cells.

I'm working through the paddle's timing after a straight bounce, since its slack depends on the phase. With one unit of slack left, a double botch is survivable, but at zero slack even one botch kills the catch, and I still need to estimate how often the landing phase falls at the corners.

Now I'm checking the brick-hit edge case in the top row, where a ball moving up would have its y go to -1 and flip back down.

I'm now going through the edge cases of the phase model: the horizontal movement is clamped at the walls, and when a brick is hit, the ball's y stays the same while only x changes. Since those cases all hold up, I'm treating the horizontal phase model as robust.

Now I'm checking the descent case where the ball is moving down through rows 5 to 8: the trail is always one row above the ball, and since no bounce happened there apart from the paddle, the direction stays down. I'm also wondering whether the paddle could ever end up somewhere other than the trail or landing cell during the paddle phase.

I'm now checking the paddle's "flight" position at the far side: the catch needs the paddle at the ball's old x or new x, and the descent-mode timing should place it at the landing cell by the time the ball reaches row 5 through 8.

I'm checking that the paddle's lead of three phases keeps the flight and descent modes consistent, so that by row 4 it sits on the landing cell. I'm now going to revisit the P-mode design, comparing left and right mirrored versions.

Writing out the layer-one weights now, scaled by ten...

Still writing the layer-one weights, with the left-facing unit set out: reversed ball and trail terms plus the paddle penalty and bias. I'm checking one case by hand, with the ball in column 3, the trail in column 2, and the paddle at 9, to confirm the pre-activation comes out right.

Still writing the weight table for the right-descent unit...

Still writing the weight table for the left-descent unit...

Still writing the weight table for the left-descent unit...

Still writing the weight table for the left-descent unit...

Still writing the weight table for the down-going gate, checking the ball-row and trail-row terms against the expected sign.

Still writing the layer-two weights, with the first unit set out: the ball-on-row-0 term, the down-going and bounce-gate terms, and the bias.

Still writing the layer-two weights for the remaining units...

Still writing the weight table for the output layer, setting the action weights and biases for the right and left moves.

Next I'm checking that the left and right bounce conditions never fire together in flight, covering each ball and trail pair to confirm the lower bound never exceeds the upper one.

Checking the left and right bounce ranges: the lower bound sits below the upper bound at both ball rows, so the two moves can't both fire in flight. Next I'm going back over the P-mode dynamics to make sure the actions come out right.

Now I'm checking the reverse-bounce case: the ball at (4,8) heads left, the paddle sits at 3, and the ball's direction flips to up-right. With the paddle exactly under the ball, the right-move unit should fire, and I'm confirming that the pre-activation for it comes out positive.

Still working through the corner cases in the P-mode table, checking the paddle's left and right responses at the edges.

Still checking the P-mode gating: the right-move unit needs both the ball term and the trail term, so I'm confirming at the bottom corners that the sums come out to the expected margins.

Checking the start-of-game cases next, to make sure no failure repeats systematically. After a straight bounce from the left edge, the paddle chases with lag and wraps at the wall, ending up ahead of the ball; the earliest landing is nine steps after the observation.

I'm checking the edge case where the paddle starts at column 0 with the ball also at column 0, which leaves a slack of one. Then I'm working through the variant where the ball bounces straight from column 0 and lands at column 9 with the paddle needing to reach column 8, giving a slack of two.

Now I'm checking the second start, with the ball at (9,3) and the paddle at 4, by working out which columns the ball can reach in the flight phase.

I'm checking the second start now, tracing the ball down the right side while the paddle holds at column 4 and stays in the catch range through each descent step.

Next I'm tracing the game forward from the paddle at 3: the ball's flight checks send the paddle left to 2, then right to 3 and 4 as the ball rises along the top-left edge. After the brick bounce at (1,3) the ball is heading down again, and I'm following its descent toward row 8.

I'm now thinking about what happens when the ball gets stuck bouncing between the ceiling and the bricks without scoring, checking whether the straight-bounce trajectories could cycle through the same phases forever.

I'm checking whether the ball could keep cycling through brick-free loops without ever hitting the remaining bricks. Each wall or paddle bounce flips the parity of its position, so every cell should be reachable, and sticky actions add enough randomness that I don't need to worry about it.

Now I'm checking the Breakout flight table for the right-moving case, with the ball at column 1 and its trail at column 0: the pre-activation works out to 5, which matches the lower bound I had for that state.

Still checking the flight table values for the moving-right cases, confirming each sum matches the lower bound I had for that column.

Still checking the flight table values, working through each column on the left-moving side to confirm it matches the lower bound.

Still checking the flight table values for the right-moving cases, confirming the pre-activation sums land on the expected lower bounds for each column.

Still checking the flight table values for the left-moving cases, confirming the sums for columns 0 through 2 land on the expected lower bounds.

Still checking the flight table values, this time for the ℓ=2 case and its left-moving entries.

Still checking the left-moving flight entries for the ℓ=2 case, confirming the sums at each column land on the expected lower bounds.

Now I'm verifying the left-moving entries for the ℓ=2 table, checking each column's sum against the lower bound to confirm the remaining values land where they should.

Now I'm checking the ℓ=1 flight table for the moving-right cases, confirming each column's sum lands on the expected lower bound.

Checking the last row of the left-moving entries for the ℓ=1 table, where each sum lands on the expected lower bound up through column 8, and the corner at (9,9) is still being worked out.

Now I'm verifying the ℓ=0 table: for the moving-right entries, the sums at columns 1 through 7 each match the expected lower bound.

Now I'm checking the leftmost-moving entries of the ℓ=0 table, where each column's sum should land on its expected lower bound.

Now I'm checking the mirrored left-move entries: the wall-same case at (9,9) should sit at phase 10, matching (0,0) at phase 0, and reflecting the board should map each left-moving cell onto a right-moving one. That gives the left table as 9 minus the right-table value at the mirrored cell.

I'm cross-checking the mirrored left-move formula against the right-move values, using the reflection identity to confirm the phase offsets line up. The descent at row 8 gives a clear split: the ball can only go left if the paddle is at column 1 or beyond, and it can only go right if the paddle is at column 8 or below.

I'm now going back over the layer-one weights, since the saturation doesn't matter for the ball rows near the top. Then I'm considering whether I can use the paddle's choice at landing to steer the next cycle's slack away from the tight phases, starting with the case where the ball sits at (0,8) moving left, where the only waiting cell is forced.

Now I'm weighing which waiting cell the paddle should pick after a landing, to keep the next cycle's slack away from the tight phases. With the ball at (1,8) moving left, the straight option leads to slack 3, while the reverse one drops to slack 1, so I'd take the straight option. From (0,8) moving right, the reverse option gives slack 4 against 2 for the straight one, so that's the better pick.

Next I'm working out which waiting cell the paddle should choose at landing for the case where the ball is at (0,8) moving right, since the reverse option looks like it leaves more slack for the following cycle.

Now I'm checking the corner case at the left wall: with the ball at (0,8) moving left, the paddle has only one waiting cell, so that outcome is forced.

Checking the bounds for the remaining cases, then working out the mirrored formula and how the paddle should pick its waiting cell at landing to keep the next cycle's slack off the tight phases.

I'm checking the cycle lengths: bricks only sit in rows 1-3, so a ball bouncing off row 4 or below can't be shortened by a brick. Now I'm working through the paddle's move at a straight bounce near the right wall, where it should step away from the edge. I'll then look at the next flight observation after that move.

Now I'm tracing the ball's path down from row 5 to row 8 on the left side, checking the paddle's waiting cells at each landing step to see where it should sit.

Now I'm working through the paddle-and-ball trace: the ball bounces back to the paddle side, and I'm checking each flight step to confirm the paddle lands where it needs to be.

Now I'm checking the paddle's lead in the near-wall loop: the paddle reaches the waiting cell by the time the ball comes down to row 5, with a slack of about 3. The rest of the layer-2 and layer-3 construction looks fine, and I'm asking whether the unused actions stay far enough below the others to avoid overflow.

Still writing the weight-matrix setup for the ball channels...

Still writing the weight entries for the paddle channel...

Still writing the weight entries for the paddle channel...

Still writing the layer-one weights for the left-moving unit, filling in the ball and trail columns row by row.

Still writing the layer-one weights for the right-descending unit, filling in the ball and trail columns row by row...

Still writing the weight entries for the right-descending unit's ball and trail rows...

Still writing the weight entries for the left-descending unit, filling in the ball rows and trail rows.

Still writing the weight entries for the left-descending unit's trail rows...

Still writing the lookup values for the right-descending and left-descending units...

Still writing the reversed lookup lists for the left-descending unit's trail rows...

Still writing the weight entries for the paddle channel of the right-descending unit...

Still writing the layer-one weights for the left-moving and right-descending units...

Still writing the weight entries for the Unit 6 ball and trail rows...

Still writing the weight entries for the Unit 7 paddle and trail rows...

Now I'm reconsidering the chase after a straight bounce: if the paddle has been waiting with no-ops and a botched move drops one step, the slack shrinks, and the cases where the ball is only one or two phases from landing are the tight ones.

Now I'm weighing whether the paddle should stop waiting at the corner cell and hover one step over, since the slack after a straight bounce depends on where it lands. Straight bounces leave slack that grows with the landing phase for the early cases, then shrinks toward the wall, bottoming out at 1 in the corner.

Still working out the reversed slack values for the paddle's waiting cells as the ball comes back toward the middle.

Comparing the two options for each landing phase now: the straight bounce gives slack 2 at the left edge and climbs to 10 mid-board, while the reverse gives 4 and rises to 10 at φ_c=3.

Still working out which waiting cell the paddle should hold at landing, since the slack values look tight near the wall, and I'm comparing those against the reverse options to pick the safer one.

Working through the paddle's path at the far end: with the ball landing at x=0, the paddle's trajectory lands it on x=0 already at φ=15, so the straight bounce leaves a slack of 2 rather than the 1-step lead I had assumed.

I'm comparing the paddle's options at the wall: landing at the edge cell gives only 1 or 2 steps of slack when the ball comes down near the corner, so I'm considering biasing the descent toward the neighboring cell for those landing phases.

I'm weighing whether the paddle's corner-landing cases are worth redesigning: the straight-bounce slack of 2 at φ_c ∈ {0, 10} only becomes fatal after three botched moves, so the risk is about 0.1%. The slack of 1 at φ_c ∈ {9, 19} is forced by the corner and would need two botches to fail, around 1%.

Now I'm checking whether the corner landings at phases 9 and 19 can be avoided by changing the bounce type earlier in the cycle.

Now I'm checking the slack for the corner case at φ_c = 9, where the paddle sits at 9 and the ball heads down-right. After the bounce the paddle has to step left to 8 while the ball traces back along its flight path, and I'm stepping through that descent.

Checking the paddle's landing slack for the corner cases, I'm confirming the trace: the paddle gets to cell 0 at the right step, with one step of slack at the wall.

I'm checking the paddle's timing against the next few landing phases: for the bounce at φ'=8 the paddle is already on 7, so it holds; at φ'=9 it steps left to 6-5 range and that's a left move; for the reverse bounce at φ''=8 the paddle on 8 steps left, and at φ''=7 it holds.

Now I'm double-checking the sticky previous-action behavior against the timing analysis, and it holds. Next I'm confirming the ball-channel gating: in the descent observation the descent units are on and the flight units are off, and the reverse holds in flight.

Now I'm checking the layer-two AND gate for the right-descending unit: with three inputs, the pre-activation works out so that only the case where the ball channel is on, descent is off, and the paddle gate is off clears the threshold, and every other combination stays well below it.

Now I'm testing a long-flight case where the ball comes down from the top-left moving right, starting at (2,0), so I can check that the paddle doesn't get stuck far away when the flight interval drives the target.

Now I'm tracing the paddle through the remaining descent steps, where the ball hits the bottom rows at x=9 and the window stays at {9, 8} the whole way down. At the final step the ball lands at x=8, and the paddle is already at 9 or 8, so it holds within the target.

Checking the bounce case where the ball is at (8,8) heading up-left with the paddle at 9: the paddle holds on the left-move unit and the right-move unit stays off, which fits the plan. Now I'm testing a descent case where the ball comes down the left side, starting from (1,5) moving down-left.

Checking the wall cases for consistency: the ball coming down the left edge still lands in the paddle's window {1,2} at every step, and the model holds with no gaps.

Now I'm checking the edge cases where the ball is at the wall: with the paddle on 1 or 0 and the ball on row 0, both the straight and reverse bounces should still land in the paddle's window.

Now I'm checking the paddle's waiting cells against the reverse-bounce cases, confirming the Breakout policy still catches the ball for each landing phase.

I'm now weighing whether waiting at the left edge and bouncing straight is the better choice, or whether the idle steps can be used for something useful. I'm also checking the triple-botch risk at the D_5 "N" transition, where the paddle has been moving in the ball's direction, to see if an earlier steady state would be safer.

Checking the tail risk of the paddle's lead-tracking: every step it moves, so three consecutive botched moves at the D_5 transition would be fatal, roughly a 0.1% chance per cycle. Over the full episode that adds up to something like a coin flip, so I'm considering a design that aims the paddle at the exact landing cell instead of anywhere inside the window.

I'm considering whether shrinking the lead by one step would help, since the paddle would stop earlier and leave less room for consecutive botched moves near the wall. With the current lead of 4, three botches in a row during the first few steps after it reaches the target cell would push it out of the catch window.

Now I'm weighing a lead of 5 instead of 4: the paddle would reach the target cell one observation earlier and then hold there, but three consecutive botches would still knock it out of the catch window, so the triple-botch risk comes out about the same either way.

Now I'm weighing whether a larger lead would cut the triple-botch risk, and it doesn't: with a = 3 the failure still needs three consecutive botches, and a = 2 drops to two. So the lead of 4 stays the best of these, even though three botches in a row at the D_5 transition would still be fatal.

I'm weighing whether a lead of 4 can be improved by stopping the paddle earlier, but the landing spot isn't known until the descent starts, so the paddle can't settle before row 4. Shifting the flight interval or trying to pause the paddle doesn't help either, since the target keeps moving and the paddle has to keep moving with it.

Now I'm weighing a lead of 5 for the ball's trail, where the paddle would sit one step ahead while the ball is still in the bricks. At row 4 the target window would then be {L0, L1}, so the paddle should already be on L0 from the previous step and simply hold there.

I'm weighing a lead of 5 with the descent mode starting at row 4, so the paddle goes to L0 one observation sooner. That would require four consecutive botched moves to push it out of the window, cutting this failure mode roughly tenfold, but the table for row 4 would be shared between the ascent and descent cases, which I still need to sort out.

Now I'm checking whether the two tables can share a single G_4 entry: S_4 and D_4 both need the same value function at row 4, but D_5 seems to want the row-3 version of G_4, so I'm weighing whether a gauge shift could reconcile the two.

I'm considering whether the two tables can share a single G_4 entry, since the gauge and the one flexible entry don't seem to resolve the conflict. Another option is to give S_4 its own unit pair with a separate gate so the descent tables stay consistent.

I'm now working out what the paddle's targets look like at row 4 if the lead is 5, including the gate that would let S_4 and D_4 use the descent unit.

I'm weighing whether a lead of 5 can work if the descent mode starts at row 4, since the paddle would then reach L0 one observation sooner. The remaining question is whether the flight tables need recomputing for the longer lead, or whether the lead-4 desired actions are close enough to keep.

I'm now settling on a flight lead of 5 with descent mode starting at row 4, so the paddle already sits on L0 when the descent is recognized. That means the first-step and paddle-at-L0 checks are consistent for both S_4 and D_4, since the previous after-move position works out to L0 in each case. The price is three extra units and recomputed flight and P tables, and the payoff is a tenfold drop in the triple-botch failure mode.

I'm estimating how often the triple-botch failure actually happens: a botch at D_5 followed by two more at D_6 and D_7 comes to about 0.1% per cycle. Over roughly 700 cycles that is about a 50% survival chance from this failure alone, and the quadruple-botch version would raise it to around 93%, which could meaningfully lift the mean score.

I'm weighing whether the paddle's overshoot at the wait start is the real bottleneck, since its triple-botch failure rate is about as large as the others. I'm checking which direction the paddle moves from L0 to L1 when the ball's x-trajectory keeps going the same way without a wall in between.

I'm now checking the corner landings: the slack-1 cases near the walls seem to add roughly the same failure rate as the triple-botch mode, since those two frequencies come out comparable.

I'm checking the corner landings for Breakout: when the ball lands at phase 9, the paddle has to cover the distance to the opposite corner in the next cycle, and the remaining slack there looks small enough to matter.

I'm working through the corner cases now: when the ball lands at the corner, the next cycle is a 10-cycle only if the brick at that column has already been cleared, so corner-to-corner repeats at most twice in a row. I estimate this corner failure at roughly 0.03 times 0.01, about 0.0003 per cycle.

I'm looking at the corner landings again: after the ball lands at phase 9, the paddle has to cross to the far side, so a botched move there is only harmless at the wall and a second miss is fatal. I'm considering whether to avoid corner landings by changing the previous bounce, but that would need brick prediction, so I'm setting it aside. I'm also noting that the low-slack straight-bounce case after phase 1 looks fine, and I'm checking whether any other double-botch failure is as large as these.

I'm checking whether the paddle's lead-tracking still holds when it turns at the wall: near x=8 and 9 a botched move just clamps harmlessly, so it takes four or more misses to lose ground. Away from the wall, though, a missed move during the chase can leave the paddle overshooting and lagging the target, which I still need to work out.

I'm weighing whether a third gated mode for S_4 is worth the added complexity, since that would mean a bug could be costly even if the failure-rate gain looks real.

I'm weighing whether to shift the flight lead to 5 so the paddle can idle on L0 one observation sooner, but that would mean rebuilding the flight and P tables and adding gated units for row 4. I'm also considering whether the simpler alternative of keeping lead 4 and just adjusting the descent window can get the same benefit, since the real question is when the paddle first becomes stationary.

I'm now weighing a lead of 5 with descent starting at row 4 against keeping the flight tables as they are, since under the lead-5 version the paddle would first hold still on L0 one observation earlier. Checking the flight-interval variant, the paddle would only reach L1 and D_5 would have to make the first hold decision there, which looks worse.

I'm considering whether S_4 could use the descent unit too, by fitting a separate ball-row-4 table against the existing trail-row-4 table, though that leaves the system overdetermined for the 10 unknown values.

I'm checking whether the same-row paddle modes for row 4 and row 8 could share one gated unit pair, since both would compare ball and trail positions on a single row. The row-4 table can't be reused from the row-8 one, though, so they'd need separate entries inside the shared pair.

I'm folding the row-4 same-row case into the existing row-8 pair: one gate that fires when the ball and trail are both on row 4 or both on row 8, using a threshold of 1.5 over four inputs so mixed-row combinations can't trigger it. That gives the gated mode with no new units, just extra table entries for rows 4 and 8.

I'm reworking the row-4 descent check: the ball-row-4 table gets the ℓ=4 values, the trail-row-3 table gets the matching negatives, and the gate widens to cover rows 4 through 8. I'm verifying that this gate still stays off for the same-row and one-row-off cases at row 4.

I'm now working out the Breakout policy for the lead-5 flight variant: the flight tables need recomputing for a=5, and I'm folding the row-4 descent and same-row modes into existing units and gates rather than adding new ones.

Now I'm re-tracing the cycle with the flight lead at 5: the paddle holds on L0 at the start, descent starts at row 4, and it stays put through the descent rows until the ball reaches the straight segment at phase 6.

