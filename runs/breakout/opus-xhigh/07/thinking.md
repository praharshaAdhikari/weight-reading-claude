I'm setting up a hand-designed policy network for MinAtar Breakout, starting from the game's dynamics: a 10x10 grid where the paddle moves first each step and the ball then advances diagonally in one of four directions.

I'm checking the ball's bounce rules at the bottom row: if the paddle sits under the ball, the direction flips back up, and if the paddle sits at the destination column, it flips the other way. Walls clamp the x-position and flip the horizontal direction, so the ball just moves straight down one row on that turn.

The catch window is effectively two cells wide, since the ball's current column and its next column both count. Tracking the ball's column should usually be enough, because the ball and paddle both move one cell per step. If the paddle is directly under the ball and the ball moves sideways, the paddle can match that move and stay aligned. The harder case is when the ball reverses, since then the column it arrives at on row 8 is what really matters.

I'm checking whether tracking the ball's current column is enough, and I'm starting from a case where the ball enters from the left and the paddle is at column 4. The ball reaches row 8 at column 5 after five steps, so the paddle has time to get under it. The real question is whether simply chasing the ball's current x is optimal or whether the paddle needs to predict where the ball will land, and I'm leaning toward checking if a lagging paddle can ever catch up once the ball moves away from it.

I'm checking the ball's bounce rules here: bricks and the top wall only flip its vertical direction, side walls only flip its horizontal one, and a paddle hit at the destination column reverses the ball's full direction, so it heads back the way it came. I'm working through what that means for the ball's position on the next step.

I'm checking how the ball's horizontal position evolves over time, since it bounces between the side walls at speed one, and I'm working out how long it lingers at each edge.

I'm working out how the paddle's lag plays out: if it chases the ball's current column, the gap can stay at one cell while the ball moves sideways, and I need to check whether that still lets it catch the ball when it drops to row 8.

I'm noting that the paddle only needs to match the ball's current column, since a lag of one still lands inside the catch window. Tracking toward the ball's next column would align it even earlier, though either approach works. The ball's x-motion stays the same on the way up, so the paddle can keep mirroring it from the starting position at column 4.

Checking the wall case again: the paddle starts at 4 and the ball enters from 0, so it moves left to meet the ball at column 2 and then stays under it. If the paddle stays one cell behind the ball, it still falls inside the catch window when the ball reaches row 8.

I'm weighing whether a lag of one or two cells matters, since a paddle that falls behind by two will miss the ball at row 8. Tracking the ball's current column is simple, but a sticky no-op could leave it stranded, so predicting the landing column and positioning the paddle there early looks more robust.

I'm thinking about a tighter rule: aim the paddle at the ball's next column, so that once it's aligned it stays aligned. Then at the moment the ball reaches row 8, the paddle moves onto the incoming column and catches it through the side-reversal case.

I'm looking at how errors accumulate: a missed move while the ball drifts away leaves the paddle one cell behind, and since it can't close the gap at the ball's speed, a second miss at catch time would lose the ball. The chance of that depends on whether sticky repeats of the previous action are harmless, which they are when the paddle was already moving the same way.

I'm working out how the ball's horizontal motion is periodic, bouncing between the side walls, and how that sets where it will be when it drops to row 8. The paddle's direction changes are the weak point, since a sticky repeat of the old action would leave it lagging, so I'm considering predicting the landing column and positioning early instead.

I'm weighing whether to track the ball's current x directly or aim for the column it reaches next, since a reflected landing point is hard to predict when bricks interrupt the upward path. The horizontal motion doesn't depend on bricks, so the paddle can mirror it, and the open question is just how much slack it needs at the moment the ball drops to row 8.

I'm weighing whether aiming the paddle at the ball's next column keeps it aligned through the catch, with the open question being what a sticky repeat of the previous action would do to that alignment.

I'm weighing whether keeping the paddle one cell ahead of the ball's direction of travel gives extra slack, since a missed move would only bring it back to alignment. The wall is the catch: when the ball reaches the edge, the paddle can't go further and has to wait for the ball to turn around.

I'm weighing how sticky actions interact with the paddle's lag: if the previous action was a no-op while the ball drifts away, the paddle falls behind and can't close the gap. Since the ball's landing point depends on when it descends, which bricks can delay, I'm wondering whether the paddle can position itself in advance from the ball's descent timing and the reflected column.

I'm checking whether the paddle can still reach the landing column during the descent, since the ball's horizontal position at that point follows from the wall reflections, and the gap only needs to be covered within the steps left before row 8.

I'm considering a policy that aims the paddle at a predicted landing column for the descending ball, using a reflection rule on its horizontal position, and I'm weighing whether that can be computed cleanly with a small network. The hard part is the ascending case, where a brick or the top wall decides when the ball comes back down, so I'm thinking about approximating that from the current position.

Ascending, the ball will return down whatever bounce happens, so tracking its current x keeps the paddle in the right place either way. The weakness is that a missed move during its outward drift leaves a lag that only closes when the ball turns back toward the paddle. Aiming at the predicted landing column during descent might avoid that lag.

I'm checking the slack in the descent: the ball at row 5 needs three steps to reach row 8, so the paddle has four moves to reach column 6 or 7, which leaves no margin. Tracking the ball at a lag of one gives the same result, since the paddle ends up on the landing column either way.

I'm weighing how much the paddle actually lags at a wall bounce, since that's where the needed action flips and a sticky repeat of the old move would keep it moving the wrong way.

I'm working through the wall case: with aligned tracking, the ball reaching column 9 leaves the paddle at 9 too, and the clamp means "move right" does nothing there. I'm checking whether the direction flip then leaves the paddle in the right place for the return trip.

I'm checking the ball's horizontal direction at the walls, since the trail only shows vertical motion when the ball sits in the edge column. At column 9 the ball must have just bounced off the right wall, so it's heading left; at column 0 the opposite holds. Near the top row, the vertical flip only happens on the step after reaching row 0.

I'm checking how a brick strike changes the ball's motion: the ball keeps its row and moves sideways, so the trail shows only horizontal travel and the vertical flip has to be inferred. A same-row trail at row 8 would instead mean the ball just bounced off the paddle and is ascending.

I'm checking whether a trail in the same row can tell the ball's vertical direction: at row 8 it means the ball just bounced off the paddle and is ascending, while elsewhere it means a brick strike has sent it back down.

I'm going over the case where the ball comes back along the same row, since a same-row trail means the ball just bounced off the paddle at row 8, but elsewhere it could be a brick strike sending it back down. I'm also noting that a brick hit with the strike flag already set lets the ball move into the brick cell, which is an odd edge case. For paddle control, tracking the ball's x mostly avoids needing the vertical direction, so I'm focusing on reading the horizontal direction from the trail column versus the ball column.

I'm checking the wall case more closely: with the ball at column 9 and its trail at column 8, the clamp holds the next position at 9, but with the trail also at column 9 the ball is heading back to 8.

I'm checking how a paddle bounce flips the ball's direction: when the ball meets the paddle head-on it reverses vertically and moves sideways, so the trail at row 8 can point the wrong way for the horizontal motion.

Checking the paddle-bounce case where the ball lands on the paddle's destination column: the trail still points sideways, so the ball looks like it's moving toward the paddle's side when it's actually heading back up the other way.

I'm checking the paddle's lag after a type 1 bounce: the paddle at x with the ball at x+1 moving right means the next target is x+2, so the paddle trails by one column. A type 2 bounce leaves the paddle under the ball while the trail suggests rightward motion, so the paddle should move left. Either way, the paddle needs the right correction at the moment of contact.

I'm weighing a predictive strategy: move toward the predicted landing column while the ball descends, and track its x while it ascends. The concern is a one-column lag from type-1 bounces, so I'll need the right correction at the moment of catch, and I'm asking how reliably a sticky repeated move would get it wrong.

I'm weighing how often the paddle will need a correction it gets wrong, since a sticky repeat only fails when the needed action changes. With a strongly peaked policy, the chance of a wrong move is small, so the main risk is the few catch moments where the action flips. I'm also considering how a typical MinAtar Breakout run plays out: long episodes that can break a few hundred bricks.

I'm working out a linear rule for the paddle: the target column is the ball's x plus its horizontal direction, which I can get from the difference between ball and trail columns, and the paddle moves left or right depending on whether it sits past or short of that target.

I'm writing the paddle target as a linear combination: the ball's column plus its horizontal velocity, which is the trail-to-ball difference, then subtracting the paddle column. Thresholds on that value will drive left, right, or no-op, and the wall and paddle-bounce cases still need their own corrections.

I'm checking the wall edge cases: at column 9 with the trail at 8, the formula overshoots to 10, but the clamp keeps the true next column at 9, so moving right is harmless. With both ball and trail at column 9, the formula predicts 9 when the real next column is 8, which only costs a no-op at the paddle's edge. The same-column trail only shows up at the walls, so these are the only cases where the linear rule needs a correction.

I'm checking the type 2 paddle bounce, where the ball at (8, x+1) moves up-left and the trail still points right. The linear rule would predict x+2 and push the paddle right, but the real next column is x, so the paddle ends up overshooting and has to come back left once the ball is ascending.

I'm working out a fix for the type 2 paddle bounce: when the ball is on row 8 and its trail is also on row 8, the ball has just bounced off the paddle and is ascending, so the paddle should not chase the formula's predicted column.

I'm separating the two paddle-bounce cases by whether the paddle sits under the ball or under the trail: if the paddle matches the ball's column, the true next column is the trail's, but if it matches the trail's column, the formula's x+2 holds.

I'm checking the case where the ball and its trail both sit at the wall cell (8,9): the formula predicts column 9 for the next step, but the ball actually moves up-left to column 8, so the paddle stays put on a no-op, which is a minor error.

I'm considering whether to use the current ball column as the target instead of the predicted next column. That would leave the paddle lagging by one column in steady state while the ball moves away, but it avoids overshooting on the type 2 bounce.

I'm considering whether the target should be the ball's next column or a column further ahead, and I see that aiming even one step past the next column would make the paddle overshoot on the catch step, so the next column is the safer target.

I'm checking the type 2 bounce once more: with the paddle moving dx, it lands on x+2dx while the ball has already gone back to x. That leaves the paddle two columns ahead of the ball, and nothing in the plain next-column target pulls it back quickly.

I'm checking how far the ball travels before the paddle can catch up after a type 2 bounce. Ascending to a brick and descending back to row 8 takes about nine or ten steps, so the ball can cover a lot of horizontal distance, and the two-column lag may persist until a wall turns it around.

I'm checking whether a wall will be reached before the ball can come back, since the paddle then has to make up its two-column gap after the type 2 bounce. Then I'm leaning toward handling type 2 directly, by keeping the paddle under the ball at the catch so the bounce stays type 1 and the lag stays at one column.

I'm now checking whether the alignment holds after a type 1 bounce: the paddle lags by one column, and that is still catchable but needs a correct move at the catch. I'm considering a special rule for the case where the ball and its trail are both on row 8 and the paddle sits under the ball: the target should be the trail column, which pulls the paddle back so the ball returns to it and the alignment is restored.

I'm checking the sticky-action risk after the catch: the paddle has just moved +dx, so a 10% sticky repeat would push it to x+2dx and leave a two-column gap. So I'm considering instead staying put at the catch, which gives a type 1 bounce and keeps the paddle under the ball's column, but a sticky +dx there would still turn it into a type 2 bounce.

I'm weighing whether to fix the catch step explicitly, since every catch involves a change of action and a sticky repeat could leave the paddle two columns behind. I'm also wondering if, during the ascent and brick phase, I should track more loosely instead of holding a strict alignment.

I'm weighing whether the paddle should head straight for the landing column once the ball turns downward, since the bounce timing is uncertain but the descent reveals where it will land. With the paddle lagging two columns, I'm checking whether a direct move to that landing spot recovers alignment before the catch.

I'm working through a worked example near the wall: the ball descends at x=7 while the paddle sits at 5, so the gap is two columns. The ball's path to row 8 bends off the wall and lands at 8, with a catch window of {7, 8}. Two moves from 5 to 7 fit easily within the five steps left, so the paddle can recover its alignment here.

I'm tracing the paddle's chase step by step: it moves from 5 to 6, then 7, then 8 as the ball reaches the wall side, and I'm checking where it ends up at the catch.

I'm checking the wall-bounce case next: the ball reaches column 8 moving right and the paddle follows to 9, but the formula keeps predicting past the edge, so the paddle sits on a no-op while the ball flips direction. I'm estimating how often errors like that happen per catch cycle to judge whether simple tracking holds up over a long episode.

I'm adding special cases for the wall columns: when the ball and its trail are both at column 9 or both at column 0, the target becomes 8 or 1 instead of the formula's out-of-bounds prediction. With that fix, the paddle and ball line up again after a wall bounce, though a sticky repeat of the previous move could still leave a one-column lag.

I'm working out how sticky actions affect the paddle near the wall: a repeated "right" at column 9 leaves it in place, which costs at most one column of lag. I'm also comparing that with simply staying put at column 9 when the ball is about to bounce, since both lead to the same position. Next I'm modeling each step as having a 10% chance of repeating the previous action, so I can estimate how often a change of intent gets misexecuted.

I'm considering a trick here: since "right" at column 9 does nothing, I could keep pressing it while the ball sits at the wall instead of switching to a no-op, so a later sticky repeat would be harmless. Every intended change still carries a sticky risk, though, because a repeat of the previous executed action can override it.

Now I'm weighing what happens when the paddle is already aligned under the ball at the catch: it can stay put for a type 1 bounce or move with the ball's direction for a type 2 bounce, and I need to see which choice keeps the alignment intact.

I'm now considering the case where the paddle is one column ahead of the ball, so it has to either stay put or step back against the ball's direction. I'm also noting that the paddle's previous move was likely in the same direction as the ball, which is relevant to the sticky-action risk at that point.

I'm working through what a catch does to the paddle's alignment: if the paddle is under the ball, a type 2 bounce leaves it one column behind after a sticky repeat, and a type 1 bounce leaves it a column behind right away. Every catch seems to carry some risk of a lag building up, so I'm asking whether that lag actually matters once the walls start bouncing the ball.

I'm working out how long an episode a simple tracking policy could last. The ball usually hits a wall within one catch-to-catch cycle of about ten steps, and a lag of one or two columns can close again on the way back from that bounce.

I'm considering the case where the ball lands at x=0 before any wall bounce, which would leave a type 2 catch on the left side to deal with. When the ball does reach a wall, the gap closes quickly as it comes back toward the paddle, but if the paddle is lagging behind the ball's direction and no wall comes first, the ball could land before the paddle catches up.

I'm estimating the per-catch error rate at roughly 1-3%, which over an episode of about fifty catches is still a modest share of failures. I'm wondering whether the paddle can avoid accumulating lag at all, since the ball's horizontal path between wall bounces is fully deterministic and might give the paddle some slack to work with.

I'm noting that the catch window is really four cells relative to the ball's position at observation: lag one, aligned, one ahead, or two ahead, since one move can reach either of the two catch cells. That gives the paddle more slack than I'd assumed, so steady tracking with a small lead looks like the way to keep lag from building up.

I'm weighing whether being slightly ahead of the ball is the safer target, since most errors leave the paddle lagging, so leading by one column gives more room to absorb a missed move. The trade-off is at the walls, where a paddle sitting ahead has to reverse earlier when the ball bounces back.

I'm checking how being one column ahead of the ball holds up at the walls: the paddle reaches the edge, then has to reverse early as the ball comes back. The tricky part is that a paddle sitting ahead must stay put during the catch, which sends the ball back up toward a paddle that now needs to keep moving the other way.

Working through the catch case again: if the paddle stays under the ball, the reversal leaves it aligned after one move, and it can only get ahead again once a wall turns the ball around. The other option, moving back with the ball, leaves the paddle a column behind, so I'm weighing which of the two keeps the alignment intact.

I'm working out the descent phase: knowing where the ball will land lets the paddle move into the catch window ahead of time and wait there. Stopping right at the catch is risky, because a sticky repeat of the previous move could carry the paddle past the window.

I'm planning to park the paddle at the catch landing spot ahead of time and wait there with no-ops, so a sticky repeat can't push it out of position at the catch. Whether it should settle on the landing column or one column over depends on how the ball will bounce after the catch.

I'm thinking about the ball's landing spot as the path is reflected, and whether a small two-layer network could compute that position directly. For now I'm planning to track the ball during the ascent and only switch to predicting the landing column once it starts descending.

I'm mapping the horizontal motion onto a single period-20 coordinate, where walls make the ball hold for one extra step, so that moving right at column x is u = x and moving left is u = 19 − x.

I'm mapping the wall cases onto the unfolded coordinate: moving right at column 9 and moving left at column 9 land on different values of u, and the same holds at column 0. Then I'm stepping forward by the number of rows left to descend, folding back to get the landing column and the paddle target.

I'm considering whether a lookup can stand in for the full landing calculation: since the ball is one-hot on the grid, a first-layer unit's pre-activation can be any arbitrary function of the ball's cell, so the landing column for each cell could be stored directly in the weights.

I'm sorting out whether the ball's direction can be read from a single lookup, since the ball and its trail are each one-hot and a first-layer unit can only weight them separately. Direction needs both cells together, so I'm checking how much of the landing calculation can still be folded into one unit's weights.

I'm now trying a different angle: the ball's position after k steps is (k+1)b − kt, but because the product of the remaining rows and the horizontal difference isn't linear in the one-hot cells, that shortcut doesn't directly work.

I'm reworking the landing formula with the trail cell included: the ball's column multiplies a coefficient set by its row, and the trail's column gets a separate coefficient set by its own row. Written that way, the landing column splits into one term for the ball cell and one for the trail cell, so a single first-layer unit can hold the whole descending-ball landing value as a lookup.

I'm checking the ascending case: with the trail one row above the ball, the same linear form gives the unfolded landing coordinate, so one lookup could handle both directions if the trail's row is accounted for.

I'm checking the trail-based formula for an ascending ball, where the trail sits one row below and the sign of the row offset flips. Working the algebra again to see whether a separable term for the trail cell still holds in that case.

I'm folding the unfolded landing coordinate back into the 0–9 column range, and the fold has to handle values that go negative or past 17.

I'm working through the left-moving case at the walls: with the ball moving left, the unfolded coordinate reflects so that X = -1 maps to column 0, X = -2 maps to column 1, and for X above 9 the fold runs the other way, so X = 10 gives 9 and X = 11 gives 8.

I'm checking whether the paddle target can just be the landing column during the catch, so the paddle settles there and waits.

I'm settling the paddle's ramp-up: once the catch step comes, the paddle just waits at the landing column with no-ops, so a sticky repeat can't push it off the target. For the ascent, I'm weighing three possible targets (tracking the ball's current column, aiming at the landing spot assuming an immediate brick bounce, or a virtual landing at the lowest brick row) and I'm still unsure which one the formula should use for an ascending ball.

I'm checking whether the ascending case can be handled by the same separable lookup. With the trail one row below the ball, the trail term doesn't line up, so the linear form gives a meaningless value for the ball's horizontal offset.

I'm considering whether a single lookup can cover both directions, since the ascending ball needs a sensible value too. Its vertical direction comes out linearly from the ball and trail rows, so a gate on that sign could switch between the descending landing formula and an immediate-bounce estimate.

I'm checking the ascending case again: if the ball would bounce off a brick right away, its landing column comes out as c + dx(9 − r), one row further than the descending formula gives. The ball and trail tables would have to differ for the two cases, so I can't reuse the same lookup for both directions.

I'm checking whether the ascending case still matches the descending formula with one extra term: the difference works out to c − c', so the descending expression evaluated on an ascending ball gives the landing as if the ball turned around in place.

I'm checking the trail-term table for the ascending case and finding that it differs from the descending one by a term in c', so a single lookup can't serve both directions. The ball's table and the trail's table would need to change with the vertical direction, which a cell-only lookup cannot express.

I'm checking whether g(ball) + h(trail) can represent the landing value for every pair of neighboring cells. Treating the cells as nodes in a graph, a sum of per-cell terms has to agree around every cycle, so the four-cell loops will show whether the separable form can work at all.

I'm checking whether a separable sum of per-cell terms can represent the landing value across all neighbor pairs, which comes down to whether the constraints around each four-cell loop are consistent. If they aren't, the plan shifts to several first-layer comparison units combined by a second layer, with the target column compared against the paddle position.

I'm working out the right-move condition by folding the landing coordinate back into the board. Splitting it into a band for X between P+1 and 18−P plus a separate case for X at or below −P−2 means each piece is just a linear threshold.

I'm working out the left-move condition as a pair of thresholds: in the middle band the paddle has to sit to the right of the landing column, and in the negative region the reflected coordinate flips that comparison. For the right-move side, I'm splitting the fold into a band and a far-negative piece, so each case is a single linear threshold on X and P.

I'm checking the wall case for the descending formula: X ranges from about -8 to 17, so reflections beyond the board's edges never occur. The remaining concern is a ball sitting at a wall right after a bounce, where the difference c - c' is zero and the unfolded coordinate would come out wrong, so I need a separate rule for that situation.

Now I'm checking the corner case where the ball and trail both sit in column 9: the unfolded position should count as a leftward move there, so I treat the effective direction as -1 and get X = 9 − k. Then I'm testing the separable form g(b) + h(t) against that same corner to see what the column terms come out to.

I'm checking the corner case where the ball and trail both sit in column 9: the separable formula gives 9 there, but the right answer should be 1 + r, so the term needs a correction.

I'm checking the corner case at column 9 more closely: the separable formula gives 9 when the true landing should be r+1, so a correction of r−8 is needed there. The same column-9 ball also appears with a trail coming from column 8, where the formula is correct, so one shared term can't fix both, and I'm wondering whether the fold itself can absorb the difference.

I'm checking whether the separable form can absorb the wall correction for a ball and trail both in column 9, since the same column-9 cell also serves a different arrival case. A single shared term may not fit both, so I'm looking at whether the fold can account for the difference.

I'm testing whether the general formula for the landing column breaks down only in the cases where the ball and its trail share a column, since that's where the wall reflection is ambiguous.

I'm now looking at the separable sum for the wall cases where the ball and trail share column 9 or column 0, testing whether giving each column-9 cell its own weights can handle both the c = c' = 9 and the ball-from-column-8 arrivals.

I'm checking the case where the ball sits in column 9 and the trail in column 8, which gives the bounce term a_r = 81 − 9r if the column-8 trail weights stay standard. Then I'm checking the opposite case, the ball in column 8 with the trail in column 9, where the bounce term for the trail comes out to −(8 − r)·9.

I'm checking the wall-case corner where the ball and trail both sit in column 9: the separable sum gives 9 there, but the true landing is r+1, and no fold equivalence makes those match except at r = 8 or 9. I'm considering whether a separate correction unit for the c = c' cases would be cleaner than forcing the per-cell terms to absorb it.

I'm weighing whether pure tracking of the ball's next x is good enough, or whether predicting the landing spot during descent is worth the extra units. Predictive play seems more robust, since the paddle can head to the landing column early and wait there, and small errors during the descent can still be corrected.

I'm weighing whether to predict the landing column during the ascent as well, since the paddle could head toward the likely bounce spot before the descent even starts.

I'm now checking how the ascent prediction would work: if I assume the ball reflects right where it is, the landing column shifts by the remaining descent distance, so the target moves as the ball climbs.

I'm weighing a different target for the ascent: the landing spot as if the ball flew all the way to the top wall before descending. Since the ball's real flight continues upward, that target barely shifts as the ball rises, which may be steadier for the paddle than chasing a moving prediction.

I'm checking how the target behaves during the ascent: with no bricks, the landing spot would stay fixed as the ball rises, since the extra flight up and back down cancels out. Bricks would pull the landing earlier, so the real spot sits somewhere on the ball's horizontal path between now and that fixed point.

I'm working out the landing column with brick bounces in mind: a bounce at row r_b shifts the landing to u0 + r + 9 − 2r_b, so the top-wall case gives the farthest landing and each brick row pulls it earlier by an even amount.

I'm weighing the ascent case: since any brick bounce could pull the landing earlier, the paddle should keep tracking the ball's current x and only commit to a landing spot once the ball turns downward, when it has a few steps to reach the column.

I'm weighing how far ahead the paddle can sit when the descent begins: if it leads the ball by a, the slack grows to 1 + a, and the paddle can still cover the remaining distance as long as a stays within about 2k + 1.

I'm weighing a predictive target that sits ahead of the ball during the ascent, since a paddle placed early gives the descent more slack, as long as the lead stays within about 2k + 1 steps. Folding the target back into the board's coordinates is the awkward part, so I'm planning to aim for the earliest plausible landing column and see how that works out.

Working the paddle's lag through the numbers: if it starts at the landing column and only moves one cell per step, it can't keep pace with the predicted landing, which drifts two cells per step as the ball rises.

I'm considering whether the paddle can get ahead of the ball, since both move one cell per step, so it only gains ground when the ball reflects off a wall or the paddle already starts out ahead. Then I'm checking how the paddle's position relative to the ball, along the direction of travel, affects how much slack it has.

I'm working out how far ahead of the ball the paddle can sit when it starts descending: with a lead of a cells and a landing k steps away, the paddle can still reach the spot if a stays within 2k+1.

I'm considering a target that assumes the ball bounces at its current row, which gives the earliest possible landing, and whether the paddle should just hold still until the ball starts coming down.

Tracking the ball's current position stays the safe choice through the ascent, since every possible landing point lies on its future path. Once it turns downward, the paddle will have a fixed number of moves to reach the landing window, and that is when to commit to a target.

I'm now looking at sticky actions: if the paddle keeps repeating the same move, that's harmless, and the real changes in direction come from the ball bouncing off a wall or at the catch.

I'm checking the wall-reversal case step by step: with the ball moving right into column 9, the paddle tracks it there, and once the ball bounces back left, the paddle has to start moving left as well, even if a sticky action keeps it in place for a step.

I'm checking the lag after a sticky miss: if the paddle falls one cell behind at a wall, it recovers when the ball pauses there, so a single error is tolerable. Two misses between walls would be the real problem, and I estimate that at roughly 1%. Next I'm looking at the catch itself, where the paddle is aligned with the ball and the intended move matches the previous action.

I'm checking the catch case under sticky actions: if the paddle repeats its previous move instead of reversing, it ends up two cells behind the ball, which stays a problem until the ball reaches a wall and turns back toward the paddle.

I'm checking the wall-bounce timing: if the ball moves away from the paddle toward the wall, the gap stays open until the ball reverses, and I'm asking whether it can land before that happens. From row 8, the ball needs several steps to reach the brick row and come back down, so I'm comparing that travel time against the distance to the wall.

I'm tracing the ball's path after the catch: it moves nine horizontal cells before the next catch observation, so the question is whether it reaches the left wall first and turns back.

I'm checking the paddle's lead after a missed sticky move: if it falls two cells behind while the ball heads toward the left wall, it should close the gap once the ball bounces back toward it.

I'm checking whether the paddle can recover in time if it falls behind at the left wall: the ball is still moving toward that wall, and the paddle closes the gap once the ball pauses and reverses, so the catch should line up again before the landing.

I'm checking the catch case where the ball is at its starting column after the wall: if the paddle lags two cells, it can only recover when the ball's next move lands within reach, which happens for most catch positions but fails when the catch column is 8 or 9 with the ball heading left. I still need to weigh how often the catch lands in that range, and whether different brick heights change the timing.

I'm now weighing a third option: holding the paddle at the predicted landing spot during the descent and waiting there, so the catch can be a plain no-op and the sticky-repeat problem stops mattering.

Now I'm weighing whether the paddle can afford to just follow the ball after a catch. The ball moves away at the same speed the paddle does, so any lag it picks up from a sticky miss never closes until a wall turns the ball back. That means a lag of two or more is a real risk before the next landing unless a wall intervenes.

I'm weighing whether a catch that sends the ball toward the nearer wall could let the paddle gain a step, since the ball pausing at the wall gives it time to catch up. I'm also considering a different setup where the paddle sits one cell ahead at the moment of the catch, so a reversal lands it in a better spot than a plain follow-through would.

I'm comparing the two catch options here: after the paddle catches the ball, a type-2 move leaves it trailing by one cell, while a type-1 move puts it at the catch column with the ball moving away from it.

I'm noticing that a type-1 catch leaves the paddle a cell behind even with perfect play, since the ball moves sideways at the catch while the paddle stays put. A type-2 catch avoids that by having the paddle move along with the ball.

I'm now comparing a paddle that stays put at the catch against one that is already a cell ahead of the ball. If the paddle sits one cell ahead and stays still when the ball reverses, it might end up better placed than a plain follow-through.

I'm noticing that the paddle has an advantage if it approaches the landing spot from ahead rather than behind: if it is already two cells out and steps toward the ball at the catch, the reversal leaves it on the right move with no change in action, so the sticky repeat can't throw it off.

I'm now considering approaching the ball from the front instead: if the paddle moves toward the ball and catches it with a reversal, the ball then travels the same direction the paddle is already moving, so no change of action is needed. A type 1 catch, by contrast, leaves the paddle a cell behind that persists, so that version is less appealing.

I'm weighing the waiting strategy: the paddle holds at the landing point, but once the ball reverses, it has to start moving, and each start carries roughly a 10% chance of a one-step delay that turns into a lag of two.

I'm working through the "moving catch" idea: if the paddle is ahead of the ball and moving toward it at the moment of the catch, a reversal leaves the paddle moving in the same direction as the ball, so no change of action is needed. Taking the catch with the paddle two cells ahead and stepping one cell toward the ball, I'm checking what the ball and paddle look like right after.

I'm checking whether the paddle can get ahead of the ball once it reaches the left wall: the ball would stop at the wall and reverse, but a paddle that has already caught up sits level with it rather than in front.

I'm seeing that the paddle could get ahead of the ball near the wall: if it stops and reverses early while the ball is still a cell or two away, it ends up in front of the ball after the bounce. I still need to check how much lead that gives before the ball descends.

I'm considering a predicted-landing target that is exact for descending balls, and wondering whether ascending balls could use a fixed bounce row or a mirrored trajectory instead.

I'm considering using the same landing formula for ascending balls, treating the current row as if the ball bounced there, so X = c + dx(8 - r). That gives a rough estimate of where the ball would end up if it reflected vertically right where it is.

I'm trying the same landing formula for ascending balls, treating the current row as if the ball reflected there, so the target is the current column plus the horizontal step times the rows left to the top. As the ball climbs, that target moves faster than the paddle can, so the paddle falls behind it but stays ahead of the ball. At the actual bounce row the landing shifts by one more horizontal step, and I'm checking how far the prediction drifts from that.

I'm checking how the ascending-ball target behaves: since the paddle moves at speed 1 while the target moves at speed 2, the paddle keeps chasing it in the ball's direction and stays aligned rather than getting ahead. The real question is what happens when that target folds back off the wall, because that's where the paddle would have to reverse.

I'm considering the paddle's approach to the landing spot: an immediate-reflection target that treats the ball as bouncing right where it is, which sits behind or at the true landing. Since the real landing always lies further along the path, that target gives the paddle a safe, conservative point to aim for.

Still working out how the paddle should move right after the catch, since the ball's trail on the same row changes the formula.

I'm working out how a type 1 catch from rest leaves the paddle two cells behind the ball. Once the ball rises again, that lag persists, and I'm weighing how much it costs by the time the ball descends and the paddle has to reach the landing spot.

I'm checking the lag condition at the bounce: once the ball reverses off a brick, the paddle needs 10 - r_b moves to reach the landing spot, and with a one-cell lag it needs exactly that many, so there's no slack.

I'm looking at the lag problem: any lag of two or more at bounce time leaves the paddle unable to reach the landing spot, so the catch has to be made while the paddle is already moving in the direction the ball will travel.

I'm comparing the catch options: approaching the ball from ahead, moving against its horizontal direction, so the paddle is already aligned after the reversal. A catch made while the paddle is stepping into the ball's path avoids any change of action, but starting from a stop carries the sticky-action risk that leaves the paddle one cell behind.

I'm weighing whether a quantitative evaluation is worth it, since I can't simulate the game directly. A simple tracking design with a fix for type-2 catches may be good enough, and I'm wondering whether a smarter target for ascending balls would beat it.

I'm thinking about lag as something that only builds up when the paddle changes direction at the wrong moment. Near the right wall, if I keep tracking the ball's next column, the paddle can end up one cell behind after a sticky action, and I need to see where that lag comes from before the ball turns back.

I'm noticing that at the right wall, the paddle could turn back early, so that after the bounce it sits a cell ahead of the ball instead of behind it. I'm now testing whether aiming two steps ahead along the ball's path, rather than at its next column, keeps the paddle in front.

I'm testing a target two steps ahead along the ball's unfolded path, and checking how the paddle stays in front of the ball through the right-wall bounce: it moves right with the ball, then turns left early so it reaches the next landing column first.

I'm checking whether the paddle can stay a cell ahead of the ball by aiming at the window of landing columns, but the plain tracking target would overshoot and miss on a descending catch at row 8. Switching to the landing prediction means the paddle would need a reversal, which is risky if a sticky action fires, so I'm weighing aiming for the column it can reach with a no-op instead.

I'm weighing whether the paddle should hold the window's right-hand column and wait there for a stationary catch, which avoids a direction change at the last moment.

I'm settling on aiming for the cell just right of the landing column, so the paddle sits directly under the ball. Then the ball reverses and heads back the other way, and the paddle only has to start moving in that direction, which keeps any slip to a single cell of lag.

I'm working out the post-catch lag: if the first move after the catch succeeds, the paddle ends up directly under the ball, and otherwise it falls one cell behind. Then on the ascending leg I'm keeping the paddle tracking the ball, since it can't get ahead of a ball moving away, and at the bounce I'll switch to aiming at the landing window.

I'm working out the descent timing: from the bounce, the ball needs (9 - r_b) steps to reach the catch, and the paddle needs that same number of moves to reach the target column, so there's no slack at all.

I'm settling on the window rule: the paddle should head for whichever landing-window cell it can actually reach in time. If it's behind the landing column, it moves in the ball's horizontal direction, and if it's already ahead, it moves back the other way.

I'm checking whether the ball can ever move away from the paddle without lag, and concluding that after a catch it either continues or reverses, so the paddle only avoids lag if it's already moving in the ball's new direction at the catch step.

I'm reasoning through what a head-on approach to the descending ball would require: the paddle has to be ahead of the ball before the catch, so the ball moves toward it. Then the paddle can turn early at the wall to gain a lead, though that turn carries the sticky-action risk.

I'm weighing the "ahead" policy against simply accepting the failure rates: ball moving away means the paddle follows, the wall lets it turn early for a lead, and when the ball heads back toward it the paddle positions itself and waits. Every option involves action changes, so the real question is which ones still leave slack if they fail.

I'm now sketching how the target computation would look: I'll pull out the ball column, the trail column, and the paddle column, then predict the next ball column as roughly twice the ball's column minus its previous one, with special handling near the walls.

I'm writing out the activation for the target-difference feature: the right and left units fire on whether the gap D = T - p is at least one cell in either direction, so a zero gap leaves both negative and the paddle stays put. I'm also noting two wall cases where the tracking estimate overshoots by one, so I need a correction at column 0 and column 9.

I'm working through the wall-clamp cases for the tracking target: at row 8 the ball's next column can be clamped at the edge, so the formula needs a correction there too.

Working through the bounce cases at row 8: if the paddle is under the ball, it reverses vertically and the ball lands one column over, and if the paddle sits at the destination column instead, the ball bounces back with a horizontal flip. The wall cases need their own handling, since a clamped x leaves the ball in place while the direction still flips.

I'm sorting out the bounce cases at row 8: when the paddle sits under the ball, the ball reverses vertically and stays in its column, and if the paddle is at the destination column, it flips direction. The wall cases need their own handling, since a clamped position leaves the ball and trail in the same cell, and the paddle position tells me which case it is.

I'm checking the corner case where the ball lands at the top-right corner: it reverses both vertically and horizontally, so the ball and its trail end up in the same cell. The usual extrapolation would give column 9, but the correct next column is 8, so this case needs its own correction.

I'm listing the wall-correction cases for the tracking target: when the ball and its trail are both in the rightmost column, the predicted column should be one less than the formula gives, and when both are in the leftmost column, one more.

I'm now checking the bounce correction when the paddle sits under the ball on row 8 with the trail in a different column: the target should fall back to the trail's column, which means shifting the formula's result by twice the horizontal step. The corner cases where ball and trail share a wall column are already covered by the earlier wall corrections.

I'm checking how to handle the paddle-bounce correction at row 8: when the ball and its trail share a row there, I need to tell whether the paddle sits under the ball or at the trail's column. If it's at the trail's column, the target works out to a gap of twice the horizontal step, so I'd need a separate unit to catch that case.

I'm checking the case where the ball and its trail share row 8: if the paddle is under the ball, the correct target is the trail's column, so the raw formula's sign is flipped. I'm considering whether the gap's magnitude (1 versus 2) can tell the two paddle cases apart, so the network can apply the right correction.

I'm trying to find a linear target T' = αc_b + βc_t that gives the right move in both paddle cases. Taking α + β = 1 keeps the type-1 result independent of c_t, and α > 0 keeps its sign tied to dx, so I'm checking whether type 2 can be satisfied with those constraints too.

I'm settling on a linear target that gives the right move in both paddle cases: weighting the ball and trail columns equally, then doubling the gap to the paddle. That leaves a signed difference of plus or minus the horizontal step, so for the same-row case I'll compute D' as the sum of the ball and trail columns minus twice the paddle column.

I'm weighing a gated correction for the same-row case: D minus a term that switches on only when the ball and trail share row 8, but a plain linear gate doesn't work since that term depends on the paddle column too.

I'm testing whether a gated unit can catch the same-row case at row 8: firing when both the ball and its trail sit in row 8 and the signed gap D is positive, so the paddle would move the wrong way there. The obvious version runs into trouble, since in the paddle-at-trail case D is twice as large, so I need to check whether a threshold can separate the two.

I'm checking the case where the ball and its trail share row 8 and the paddle sits under the ball: there the formula's move has the wrong sign, so I'd need a special unit that fires when that configuration holds and the gap is exactly one cell, with a second unit to separate it from the two-cell gap in the other paddle case.

I'm checking whether the row-8 same-row case can arise with the paddle anywhere other than under the ball or at the trail's column, and it can't, since the catch requires the paddle to sit at one of those two cells. Bricks only occupy rows 1 to 3, so the ball can't pick up that configuration from a brick hit at row 7 either. Next I'm considering the descent at row 8 with tracking aligned to the ball: the target is c_b + dx and the gap is 1, so the paddle moves dx and catches it, after which the correction should flip the move to -dx, which leaves a 10% chance the paddle ends up at c...

I'm checking the post-catch case: if the paddle stands under the ball, a correction move of -dx leaves the ball two cells from the paddle under sticky actions, which can be fatal unless a wall intervenes. Choosing a no-op at the catch instead has the same 10% risk of a two-cell gap, so neither option avoids it.

I'm working through the descent strategy where the paddle waits at the window cell, so the paddle starts the move from rest. If the move fails, the lag is one cell rather than two, which I can live with. Then I'm checking the ascent after the catch and the bounce, where the lag carries over and I need to see whether it gets corrected before the ball reaches the brick.

Now I'm working out the descent with the paddle already tracking at distance 9 minus the ball's row, so every remaining step has to be a move in the same direction. Since nothing changes direction in that stretch, a sticky failure doesn't matter, and the one-cell lag carries through the catch.

I'm checking the lag-2 risk at a bounce: action changes are where the paddle falls behind, so I want to keep the paddle moving in one direction whenever the ball is moving away from it. Waiting at the landing window cell after the catch means the paddle starts from rest, so a failed start only leaves a one-cell lag, and I'm working through how that lag carries into the next descent.

I'm working out the lag on the descent: with the ball at row r_b and the paddle starting at c + dx, the target cell is one step further than the landing column. Counting the moves left before the catch, the paddle has 9 − r_b steps but needs only 8 − r_b to arrive, so a lag of zero leaves one spare move.

Now I'm weighing whether the paddle should wait at the landing cell itself or one step past it. If it reaches the one-past cell while moving, the ball will bounce back and force a reversal that can easily leave a two-cell gap. So I'd rather the paddle aim for the landing column directly, arriving there at the catch step, and only wait there early if it gets in ahead of time.

Now I'm checking the case where the paddle arrives at the landing window from behind while the ball is still moving toward it. If it gets there early, it has to wait, and a later catch from rest risks a two-cell lag, so I'm weighing whether it should instead arrive exactly on the catch step while still moving.

I'm settling on the descent policy: aim for the landing window and prefer to be waiting at x_c + dx early, since a paddle coming from ahead can catch the ball on its move without a reversal. The lag risk after the catch stays at most one cell, with about a 10% chance per action change.

I'm weighing two options for the descent: aim for the window cell one step past the landing column, or for the landing column itself. If the paddle is behind and reaches the landing column at the catch step, it has to keep moving through the catch, so I'd rather not let it overshoot into the far cell while moving.

I'm weighing the two options at the landing window: if the paddle is behind and moves into the far cell, a reversal is needed, and if it waits at the near cell, it has to start from rest, and the failure risk is about the same either way. I'll aim for the far cell, the type-2 cell, since the paddle can head there from either side and stop there.

I'm weighing the paddle coming from ahead: it can't simply stop at the landing cell, since that leads to an early arrival and a later restart. The only clean option is to start moving at just the right moment so it reaches the catch cell on the catch step, but a failed start leaves it one cell short and the ball gets past.

I'm weighing whether the paddle should cover the ball with a type-1 or type-2 cell during descent, since both carry about the same failure risk. Aiming for one fixed cell and estimating per-cycle death probability would be the cleanest way to pick a policy I can actually implement.

I'm weighing pure tracking as a baseline: the paddle stays aligned with the ball, so the catch is a type-2 move into the far cell. After the catch the ball reverses, and I'm checking whether a simple next-x target, with wall handling, keeps the lag small enough to survive.

I'm estimating how far the ball travels before the next landing, which depends on where it bounces: a bounce at row 4 gives a flight of about 9 horizontal steps, while a higher bounce makes it longer. So whether a lag-2 gap after the catch is fatal depends on how close the catch column sits to the wall on the far side.

I'm working through the wall-bounce case with the paddle tracking the ball: it sits at 9 while the ball trails to 8, so the target is to move left. If that move sticks for one step, the paddle falls one cell behind, and that one-cell lag carries into the next catch.

I'm estimating the per-catch death risk for pure tracking at roughly 2–3%, since a failed action change only matters when the ball is headed toward a distant wall. Over a typical episode that adds up to around 40 catches, so I'm weighing that against what published DQN results suggest for this game.

I'm settling on the descent policy and weighing whether a type 1 catch with the paddle already moving in the ball's new direction avoids any action change, which would remove the reversal risk entirely.

I'm sorting the catches by how the paddle arrives and which way it's moving: arriving from ahead while moving against the new direction, or from behind while moving with it, gives a clean catch, whereas a type 1 catch from rest or a type 2 catch moving the wrong way risks a two-cell lag. Next I'm going to work out the descent target that favors the good cases.

I'm checking the case where the paddle is behind the landing column and moving in the ball's direction. If it can reach the landing column with a cell to spare, it can wait there and catch from rest, which is clean. If the distance is exactly one move short, every option risks a reversal or a one-cell miss, so I'm weighing which of those failure modes is least likely.

I'm weighing whether to stop early and wait at slack 1, since every stop and restart adds another 10% chance of a lag, so the choice comes down to which failure is least likely.

I'm weighing the pause-then-resume idea: pausing early costs nothing if the paddle stays moving, but restarting from rest carries a 10% chance of slipping a cell, which eats the slack I'd need to spare.

I'm trying to work out how much slack the paddle has when it starts descending. If the distance to the landing column is one move short of what's available, every option carries some risk: overshooting means a reversal at the catch, and stopping early means a restart from rest that can slip a cell. Pausing to wait and then resuming doesn't help, since the resume itself could leave the paddle one cell short with no slack left.

I'm noticing that a lag of one cell behind the ball is actually safer for catches from behind than sitting aligned with it, since it removes the need for a reversal or a restart at the catch. So I'll try tracking deliberately at one cell back, moving every step, which means the only action changes left are at the walls.

I'm checking the wall case more carefully: when the ball is at the edge and the paddle needs to reverse direction, that change carries a 10% chance of a one-cell lag, so I'm looking for a target that avoids the reversal at the wall.

I'm testing the wall turn for lag-1 tracking, and I'm looking at whether the paddle can stay pressed against the wall so that a sticky "right" is harmless while it waits to reverse.

I'm considering what happens at the wall: the paddle has to start moving left from rest at column 9, and that start can fail with 10% probability. If it fails on the first opportunity, the paddle ends up one cell behind, which is acceptable, but a repeated left move that also sticks would push the lag to two.

I'm working through the wall case: the paddle can turn early when the ball first reaches the edge, so it gains a cell of buffer and a single sticky failure only costs one cell. Two failures in a row would be needed to fall two cells behind, which is rare. I'm considering a target that leads the ball by about one cell in its direction of motion during the ascent, so the paddle carries slack into the next catch.

I'm checking whether a single target formula can work for both the ascent and the descent, with the ball's vertical direction folded in as an additive term. If the target can be written as a sum of a function of the ball's cell and a function of its trail cell, then a thresholded first layer and a simple combining second layer could implement it.

I'm testing whether the target can be written as a sum of a ball-cell term and a trail-cell term, so the coefficient on the ball's offset depends on whether it is ascending or descending.

I'm checking whether the target can be split into a ball term plus a trail term, but the constraint forces the gain on the ball's offset to depend only on row parity, which doesn't help with descent landing. So I'm looking at whether the column weights could carry the extra structure.

I'm testing whether the target can be split into a ball-cell term plus a trail-cell term, and checking whether that separable form can capture the descent case where the gain depends on the remaining distance.

I'm testing whether the descent target can be written in a form the network can implement, checking the ball's relation to its neighboring cells under each vertical and horizontal direction. Comparing pairs of ball positions that share a trail cell shows that the cross-term weights would have to satisfy a constraint I haven't resolved yet.

I'm checking whether the ascending function has to match the descending one at this pair of positions, since both share a trail cell. Working through the algebra with the unfolded form, the left side comes out to 2r − 18, which pins down a constraint on what the ascending function must satisfy.

I'm checking whether the ascending function has to match the descending one, and working through the constraint with the unfolded form, which gives a candidate ascending formula that looks like the same immediate-reflection target.

I'm checking whether one linear formula can serve both the ascent and the descent, and it can't: matching the constraints from the shared trail cells forces conflicting coefficients on the trail term. So the plan is to handle the two vertical directions separately and use a gating term to switch between them.

I'm turning to the gated units now: each one fires only for the matching vertical direction, so a descending-or-ascending switch can select the right threshold. I'm also noting that same-row cases will need separate handling, since the direction signal is only defined for the two vertical moves.

I'm sizing the threshold units, three per mode for each of the left and right conditions, which gives twelve across both modes plus the gating, and that still fits within the budget. I'm also noting that the descent window and the single folded target T need to be pinned down before the gating can select the right threshold.

I'm now gating each threshold unit with a big-M term on the descent indicator, so that in ascending configurations the unit is forced off. The bound on the folded value is modest, so a constant around 200 should be large enough. The open question is that a single layer-1 unit can only threshold one linear function, so each fold-region piece still needs two thresholds combined by an AND.

I'm sorting out the same-row cases: at row 8 the ball is ascending, at row 0 it's descending, and for rows 1 through 7 I'll treat a same-row hit as descending, since a brick hit from above is rare.

I'm checking the same-row case, where a ball turns downward after a brick hit from below. The landing formula I'd planned is off by one trail term there, so the descending features will need a separate correction for that situation.

I'm working out that same-row descent: after a brick or top-wall bounce the trail sits in the ball's own row, so the landing formula's trail coefficient no longer matches the ordinary descending case. That conflict means the same-row case needs its own gated units.

I'm running into a problem with the same-row case: a single linear trail term can't capture it, because the coefficient on the trail column depends on whether the ball's row matches the trail's row. I'm considering whether a different decomposition of the landing formula could avoid mixing the ball row with the trail column.

Gating by vertical direction won't cover everything, since a same-row hit needs its own case: the trail sits in the ball's row, so the landing formula's trail coefficient changes. That means I'll probably need a third gated family alongside the two vertical ones, with the unit count rising to accommodate it.

I'm weighing whether the landing column can be computed without knowing the direction of the ball's horizontal motion, which would avoid the fold entirely. Using a lookup keyed on the ball and trail positions, or gating units on the sign of the horizontal offset, might cover that, though it would push the unit count toward the budget limit.

I'm switching to a different encoding: if I know the horizontal direction dx, the landing column depends only on the ball's own cell, so I can fold it directly into the ball weights. Gating on dx and the vertical direction would let each case use a fixed lookup, removing the need for the extra fold thresholds.

I'm making the landing column depend only on the ball's own cell once the horizontal direction is fixed, so the fold can be baked into the ball weights. The same function then covers both normal descent and a same-row turn after a brick hit, and only the gating condition differs. I still need to handle row 8, where a same-row ball has just bounced off the paddle and is ascending.

I'm working out how the gate should treat row 8: after a paddle bounce the ball is ascending, so the descending gate must be off there, and I'm considering whether shifting the gate pre-activation for ball-at-row-8 cells can enforce that with a single offset.

I'm handling the row-0 case next: a ball moving up there will turn back down, so the gate should count it as descending, and the landing column then follows from the ball's own cell and the horizontal direction.

I'm handling the edge columns now: a ball stuck at column 9 or 0 with the trail in the same column still has a horizontal direction, so I'll nudge the dx gate by half a unit at those walls to recover it.

I'm checking the landing column for a ball in the rightmost column, using the fold formula for a rightward move. If the trail is in column 8, the ball keeps moving right and gets clamped at 9, so the landing column works out to 10 minus the remaining rows, which I'll verify with one specific case. I'm still sorting out the case where the trail also sits in column 9, which reverses the horizontal direction.

I'm setting the landing table for the leftward case and realizing a ball in the rightmost column with the trail in the same column has to be treated as moving left, so the gate for that table has to fire on a zero horizontal offset there.

I'm settling the direction for the ball: the gate on horizontal motion gets corrected at the walls, so the effective direction comes out as either +1 or -1. Then I'll compare the landing column from the matching table against the paddle position, with separate units for each direction.

I'm turning the gating into big-M constraints: one gate for the descending case, built from the vertical offset with a correction on row 8, and one for the effective horizontal direction, corrected at the side walls, with the landing target taken from the matching table.

I'm checking whether the gate values can be made exact 0/1 indicators, since the big-M sum has to stay zero when only one gate is satisfied and the threshold is not met.

I'm trying to make the gate features exact: I want one linear function of the vertical offset and the row-8 indicator that is zero when the descending case holds and at most -1 when it doesn't, which pins down the coefficients.

I'm trying to write the gate as a linear function of the ball row and trail row, splitting it into a part that depends only on the ball's row and a part that depends only on the trail's row. The aim is to make it zero for descending cases, zero for same-row cases above row 8, and at most -1 for ascending cases.

I'm checking that the gate for descending motion can be written as one linear function of the ball and trail rows, with h constant over rows 0 to 7 and a lower value at row 8 so the same-row case there is excluded.

I'm realizing that a single linear gate on the ball and trail rows can't separate the descending, same-row, and ascending cases, so the gating has to move out of the first layer. I'm planning to have layer one compute the condition thresholds and the gate indicators as separate units, then combine them in layer two with a tanh that only fires when all three hold.

I'm checking whether a single threshold on the ball and trail rows can separate the descending and same-row cases from the ascending ones, trying g(r) = r for the ball and h(r') = -r' for the trail, so that V = 1 clears the bar and V = 0 needs to land at or above zero.

I'm checking whether a single linear gate f = V + 0.5 - [ball in row 8] can separate the descending and same-row cases from the ascending ones, with the threshold at zero.

I'm working out the layer-one units now: one gate that flags when the ball is descending, built from the vertical offset with the row-8 correction, and one that tells the horizontal sign apart as +1 or -1. Then I'll add the comparison units for each sign that check the landing column against the paddle.

I'm adding two more units for the paddle comparison, one for each direction, and then a second layer that combines the descending gate, the direction gate, and the comparison units with an AND. The output then sums the right and left indicators. I'm also wondering whether the direction gate can be folded into the comparisons through a single linear term.

I'm checking whether a gate that is zero for the descending case can be built so that it stays exact, by setting the scaling on the ball-column and trail-column difference. The direction term dx_raw is either -1, 0, or +1, so I'm adding a correction for the ball sitting in column 0 to pick out the right-moving cases.

I'm checking that the extra term E is exactly zero for the +1 direction and at most -1 for the -1 direction, so the big-M factor can switch off the wrong side. The range of the L_+ offset is wide enough that M around 20 should do it. I'm now running into the same snag for the descending gate: no single linear function makes it exactly zero, so I'm considering moving that part into the second layer.

I'm weighing whether the gate should live in layer two, since the descent condition can't be cleanly separated in layer one. Next I need to pick the right target for the descending ball: either the landing column itself or the cell one step ahead in the direction of the paddle's approach.

I'm weighing the target T = L + s_c against the paddle position: if the paddle starts behind the ball with enough slack to reach T before the catch step, it can wait there, but with exactly enough slack to reach T at the catch step, it ends up moving the wrong way.

I'm checking the case where the paddle is behind the ball and has just enough slack to reach the target at the catch step, since that's where the target choice seems to break down.

I'm checking how often the case where the paddle has exactly enough slack to reach the target at the catch step actually comes up. That depends on the ascending-phase policy, and if the paddle tracks the ball at the bounce, I'd need to recompute the distance to the landing column from there.

Checking the aligned-tracking case: if the paddle is under the ball at the bounce and steps with it, it ends up exactly the bad distance from the target, so that tracking policy lands in the failure case.

I'm working out the ascent policy: the paddle should aim at the landing point the ball would reach if it reflected right now, which keeps the paddle ahead of the ball. If it starts aligned or behind, it moves toward that target at full speed and ends up where it needs to be.

I'm seeing that if the paddle stays aligned with the ball during the ascent, the bounce leaves it in the bad descent case. Lagging by one cell keeps cycling without change, so neither ascent pattern clearly fixes the problem without walls.

I'm noticing that a lag-1 paddle never really corrects itself: it just keeps moving in the ball's direction, so both go toward the same wall. Near that wall the ball reverses and the paddle, still one cell behind, arrives at the wall column as the ball is turning.

I'm checking what happens at a wall turn: the ball reverses and stays one extra step, so a paddle that's one cell behind catches up to aligned. If its previous move was still "right," the sticky move does nothing and the paddle drifts to lag 1 again, with only a small chance of falling to lag 2.

I'm considering the alternative where the paddle turns early at the wall to build a lead: with the ball parked at the wall and the paddle one cell back, moving away from the wall would leave it two cells ahead once the ball starts back.

I'm working through the slack as a function of the paddle's lead a: with a paddle one or more cells ahead of the ball, the paddle reaches the target with spare moves, so it can wait there and still catch the ball.

I'm weighing whether the paddle should keep pace with the ball during the ascent so it holds a lead, since a lead of at least one gives slack for the descent. That leaves the case where the paddle starts at rest directly under the ball after a catch, with zero lead, and I'm stuck on whether that forces a bad descent or whether walls can rescue it.

I'm weighing the lead-0 case, where the paddle sits right at the landing cell when the catch comes. Moving on means a reversal that could go wrong, and holding still means restarting the move from a standstill, so either way I'm risking a two-cell lag. Pausing earlier during the descent just shifts the same problem, since resuming from rest has the same chance of failing.

I'm working out the lead-0 case: with the paddle sitting at the landing cell, I could either hold still and restart the move after the catch, or move into the reversal, and both carry a 10% chance of dropping to a two-cell lag. Pausing earlier just pushes the same restart risk later, and since the ball keeps heading toward the same wall, the next landing is probably out of reach before that wall turn matters.

Lag-2 after a type-1 catch is probably fine, since the ball keeps heading toward the wall in direction d, the paddle catches up during the wall turn, and that should happen before the next landing. A type-2 reversal is different: it sends the ball back the other way toward a far wall, so the margin is much tighter.

I'm checking whether the ball can reach the wall before it lands again. The paddle trails behind the ball, so as the ball comes back from the wall the gap closes, and the paddle doesn't need to reach the wall itself. That only fails if the ball lands before it gets there, so I'm checking whether the wall distance fits within the round trip.

I'm now weighing whether to just accept some performance loss and pick the simplest robust policy instead of chasing a perfect one. Perfect tracking would be easy without stickiness, but with a 10% chance of a delayed move, I'm expecting roughly a 1-3% failure rate per cycle, which still leaves a good number of catches.

I'm thinking about how a lead on the paddle could be built up, using the walls: if the paddle turns early at a wall, it gains ground on the ball. Right after a catch the paddle would be sitting right under the landing cell, so I'm stuck weighing whether a later approach from ahead could leave it with a usable lead.

I'm considering a "mirror" idea instead: during the ascent the paddle wouldn't need to chase the ball, just reach the landing spot. That landing spot depends on whether the ball bounces off the top wall or a brick row, so I'm thinking about using the top-wall case as a predictable target.

I'm settling on the paddle's target during the ascent: the landing cell if the ball bounces at row 4, the first row below the bricks, or the immediate reflection point if the ball is already above that row. Since bricks only fill rows 1 to 3, that row-4 bounce is the earliest one possible.

I'm working out the ascent target: if the ball bounces off the row-4 bricks, the landing cell is fixed in unfolded coordinates during the climb from row 8 to row 4. If it bounces higher, the landing moves further along the path, two cells for each row.

I'm pinning down the ascent target: if the ball bounces off the row-4 bricks, the landing cell stays fixed while the ball climbs from row 8, and if it gets past row 4 without bouncing, the target becomes the immediate reflection point, which matches the row-4 value at the boundary.

I'm noting that the paddle can keep up with the landing point because each extra row of flight adds two cells of travel and two extra steps, so a later landing leaves the same slack as the earliest one. Now I'm checking how much slack the paddle has at the earliest landing right after a catch, where the ball sits at row 8 moving with direction s and the landing cell is fold(x + 9s).

I'm checking the paddle's slack against the earliest landing cell: the ball's path folds at the walls, so the paddle's distance to the target stays within the ten moves available. With the right wall bounce, the target can even coincide with the paddle's current column, so it can just wait there.

I'm checking the claim that the next target is always within nine cells, so ten paddle moves suffice even after one delayed move.

I'm now checking the distance from the paddle to the next landing cell after a type-2 catch: the ball heads back the other way, so the target sits at the folded position L − 8s, while the paddle is at L + s. I want to know whether that gap fits within the moves available before the next catch.

Now I'm working through the landing cell after the ball's descent and bounce at row 4, folding the unfolded path at the walls to find where the paddle needs to be. I'm checking whether the reversal from the wall lands it within the ten moves I have, and I'm keeping track of the counting so the offset stays right.

I'm checking the landing for a ball that starts at column 8 moving left, which folds back to column 0 at the wall, and I'm noting that the paddle would only need to reach about 3 cells from where it sits.

I'm checking the edge case where the ball's landing column is at a wall: the catch window shrinks to a single cell, so the paddle has to be exactly there. Even so, the distance is about nine cells, which still fits within the ten available moves.

I'm checking the worst case for slack: when the landing window sits right at a wall, it shrinks to one cell and the paddle needs about nine moves, which still fits in ten. I'm also noting that a higher bounce shifts the landing and the flight time by the same amount, so the slack holds, but the paddle must wait at the earliest landing spot to keep it.

I'm checking what happens if the ball passes row 4 without bouncing, so the target becomes the immediate reflection point and moves two cells per step. The extra flight time per row matches that movement, so the paddle's slack carries over, but I still need to confirm it can keep pace with speed one.

I'm now asking whether the paddle can keep pace if the ball bounces higher: the target moves two cells per step while the paddle moves one, but the landing also gets two more steps per row, so I'm counting how many moves remain against how many are needed.

Now I'm checking that the paddle keeps its slack after the target jumps: the gap grows by one cell per step, but the available moves grow by one too, so the margin holds. Folding at the walls only makes things easier, and if the paddle had been waiting, it now has to start moving, which costs one delayed move.

I'm thinking about how the ball keeps bouncing between the top wall and the bricks and breaking many of them. My plan is to target a predicted landing cell for both descending and ascending phases, since both are just "where the ball could land" problems.

I'm now checking the bounce timing for an ascending ball: it's at row r, climbs to row 4 to hit the brick, and drops back to row 8, so the steps add up to r + 1 for any r of 4 or more. Bounces above row 4 take a different count, which I'll work out next.

I'm sorting out the ascending case for a ball at row 4 or higher: its earliest landing comes from a bounce at row 4, which gives a step count of r + 1. Above that, with a ball at row 3 or higher, the bounce is immediate, so the step count is 9 − r. When the paddle has already settled on the earliest landing, a later bounce shifts the target, and I need to handle that shift.

I'm weighing whether to aim the paddle at the landing cell itself or one cell ahead of it, since the catch type changes how much waiting the paddle can afford. Aiming for the plain landing cell lets the paddle wait there, but a catch from that spot leaves the ball moving away, which costs a delayed move.

I'm working out where the ball lands after a type-1 catch: it keeps moving in the same direction, so the landing folds to the mirror position 9 − L. After a type-2 catch it reverses, so the landing folds to a different spot that depends on whether L is below or above 8.

I'm comparing the two catch types for the next step: a type-1 catch leaves the paddle at L with the next landing near 9 − L, while a type-2 catch puts it at L + 1 with the landing near 7 − L. Since the paddle can choose which catch to make, I'm looking at which one leaves the shorter trip to the next landing, especially near the walls where one option can be far away.

I'm comparing the two catch options for a ball at row 8 moving right. If the paddle stays at L, the next landing is about 9 − L, and if it shifts to L + 1, the landing moves to around 7 − L or L − 8 near the right wall. At L = 4, the plain catch leaves the paddle only about one cell from its next target.

I'm considering whether the descent target should be a lookup table over (ball cell, direction), so I can pick the best catch cell for each position by hand instead of relying on a single formula. I'm also wondering how to handle the ascending case the same way, since the landing depends on the bounce row.

I'm now settling on the network layout: for each mode and each direction, a lookup table gives the target cell, and the paddle compares that target with its own position to decide whether to move right, left, or stay. That needs eight comparison units in the first layer. I'm also checking whether the direction gate can be folded into the comparison itself using an exact-zero trick.

I'm testing whether the mode gate can also be an exact-zero expression, by checking which trail-row and ball-row combinations make it vanish for the descending case.

I'm now testing whether the mode gate can be made exact too: splitting by the vertical direction V works for V = +1 and V = -1, since each has an exact-zero gate, but V = 0 needs a two-sided test that isn't linear, so I'm looking at combining the terms in one pre-activation instead.

I'm trying to make the same-row cases fit cleanly into the descending gate, but no exact-zero expression for the vertical direction seems to work. I'm considering whether a different split, or a combined pre-activation, could handle the V = 0 cases without a two-sided test.

I'm testing whether the mode gate can be made exact, but the vertical-direction terms don't line up: the approximate-zero version fails because it forces the middle rows to match each other while the ascending case needs them to differ. So the mode gate needs a separate layer-1 unit, and the two modes get combined in layer 2.

I'm now laying out the second layer, which will combine the mode and direction units from the first layer through a logical AND.

I'm building the layer-2 unit that ORs the two descending-direction comparison outputs, since only one of them can be on at a time, and then ANDing that with the descending mode gate.

I'm checking whether the descending-mode output can be an OR of the two direction units ANDed with the mode gate, and I'm testing the sums for each combination of mode and direction: with one direction unit on and the mode positive, the result lands on the positive side, and every other case stays negative.

I'm writing out the output logits for the right, left, and no-op actions, with the right action winning when one of the direction gates is on and the no-op winning otherwise. I'm also setting the up, down, and fire biases low enough that those actions never get selected.

I'm settling the no-op logits: the up, down, and fire outputs can sit at zero since they have the same effect as no-op, and the margin for moving right comes out to about one in a million.

I'm checking the type-2 catch case, where the ball reverses, so the direction shown by the trail is the opposite of the one I've been using, and the layer-1 design has to account for that.

I'm checking the type-2 case for row 8: a ball arriving there with the paddle directly under it means the trail shows the reverse of the true direction, so the ascending table has to handle the wrong sign.

I'm checking the type-2 row-8 case, where the trail shows the reverse of the true direction, and asking whether one target value T can give the right action for both the type-1 and type-2 paddle positions. If the two needed actions conflict, the only value that works is T = x, which pins the target to the ball's own column.

I'm checking whether a single target T can satisfy both the type-1 and type-2 paddle positions, since the thresholds would have to sit on either side of a half-cell offset. Using T = x - 0.5 with thresholds at ±0.4 gives the right decisions for both cases, though the stay outcomes don't fit that half-integer encoding.

I'm checking the type-2 row-8 case again: the single target T has to give the correct move for both paddle positions, and only some combinations of desired actions can be met by one value. I'm working out which post-catch behaviors fit that constraint before settling the encoding.

I'm checking whether a "type 2" detector can be built as a correction unit, since the paddle sits under the ball in that case, which means the condition is a two-sided equality on the paddle and ball columns. I'm considering a product form for that, but a linear version would need the s-gated units to handle it instead.

I'm checking the type-2 detector for row 8: a unit that fires when the paddle sits on the ball's column, using the s=+1 gate and a same-row gate built from one-hot ball and trail lookups. The gate's bias of -2 should make it exactly zero only when the ball and trail are both in row 8.

I'm settling the post-catch case for the type-2 row-8 situation, where the paddle sits under the ball and the trail points the wrong way. I'm checking whether a gate on paddle-equals-ball-column can be written as an exact-zero expression, since the difference is zero in that case and minus one otherwise.

I'm checking whether the post-catch case needs special handling, since the trail points the wrong way there. A big-M gate on the paddle-to-ball offset could isolate that case, but the coefficients have to be ordered so the other gates still dominate.

I'm working through the type-1 and type-2 cases for the ascending table at row 8: type 1 has the paddle one cell behind the ball, type 2 has it directly under, and I'm checking whether one target value can give correct decisions for both.

I'm checking the target values for the type-1 case, where the paddle sits one cell behind the ball, and working out how the wraparound folds the landing column, so I can decide the windowing before returning to the corner case.

I'm now setting up the ball's position as an unfolded coordinate that advances by one each step, so the direction is encoded by which half of the cycle it sits in. That way the wall reflections and the paddle bounce become a single rule instead of separate cases.

I'm modeling the ball's horizontal position as an unfolded counter that ticks up each step, so a ball heading right and one heading left are just different halves of the cycle. At the wall the counter turns over, and the trail's column tells me which half I'm in, except right at the bounce, where the trail can briefly point the wrong way.

I'm settling the window for the catch: the paddle can land on either fold(u_c) or fold(u_c + 1), and at the walls that window collapses to a single cell. I'm now sorting out the catch types next.

I'm working out what happens after a type-1 catch, where the ball keeps its horizontal direction, and after a type-2 catch, where the paddle lands one cell ahead and the ball reverses. In unfolded coordinates the reversal sends u to 19 - u at the same column, so a ball at column 5 moving right becomes u = 14 when moving left. I'm checking where the ball lands next once that reversed direction is applied.

I'm checking the post-catch case where the paddle lands one cell ahead of the ball: the reversed direction maps to u = 18 - u_c, so the next positions line up. At the wall, with u_c = 9, the window collapses to a single cell, and a paddle there counts as a type-1 catch that flips the horizontal direction and then the vertical one.

I'm now working out the ascending case: the bounce happens at some row, the ball climbs to it, flips horizontally, and descends again, so the landing column depends on the starting row and the bounce row.

I'm working through the bounce rules for the ball's strike flag: after a brick hit the strike is set, and if the ball then descends toward a brick at row 3, the toggle logic interacts with that flag in a way I still need to pin down.

I'm working out the earliest bounce row for an ascending ball: the bounce happens at whichever row the ball reaches first, and the landing column depends on that row.

I'm deciding the earliest landing for an ascending ball: for rows 4 and up the bounce is at row 4, and for rows 3 and below it happens right at the current row, which gives a closed form for each case.

I'm now looking at how the paddle should position itself while the ball is still climbing, since the landing column shifts by two for each row the ball rises past the earliest bounce point.

I'm working out how the post-catch windows line up for the next cycle, checking the worst case for an ascending ball that lands at the earliest bounce.

I'm working through the paddle's move budget: from the post-catch position there are about ten moves before the next landing. For a type-1 catch, the paddle sits one cell behind the ball's post-catch position, so I'm checking how far that is from the next window in folded coordinates.

Now I'm checking how the folded distance works out: since fold(a + 10) equals 9 minus fold(a), the landing cell fold(u_p + 9) relates directly to the paddle's current cell fold(u_p - 1) by that reflection.

I'm comparing the paddle's distance to the next landing window by folding both positions, and the reflection identity fold(a + 10) = 9 − fold(a) lets me express each window cell in terms of the catch cell. That gives a distance of |9 − 2x_c| to the first window cell, and I still need to check the second one.

I'm checking the worst case for type-2 catches next, where the paddle sits one cell ahead and the ball reverses, so the post-catch position is 18 minus the catch column.

I'm working out the distance from the paddle at x_n to the window cell fold(u_c − 9), which comes to |9 − 2x_n|, and I'm getting the other window cell fold(u_c − 8) in folded terms next.

I'm checking that the paddle can still reach the next window with one move of slack, even in the worst case near a wall. The remaining worry is the stop condition: if the paddle overshoots by one cell on arrival, it would have to come back, which eats into that slack.

I'm checking whether an overshoot at the target would be fatal: if the paddle passes it by one cell, it has to come back, which costs two moves of slack. But the window has two cells, so overshooting forward would leave the window entirely, while overshooting from the far side would land on the other cell, fold(u_c), which still works.

I'm checking whether the target should depend on which side the paddle approaches from. Aiming at the near window cell means an overshoot still lands on the other cell, which keeps the catch valid.

I'm settling on a deadband policy: if the paddle is already inside the window, it stays; otherwise it moves toward the window. That means the controller only needs two thresholds per ball cell, a left edge and a right edge, which can be encoded with the same number of comparison units as before.

I'm checking whether the paddle can still reach the window if it overshoots by one cell, and an overshoot from either approach direction still lands on the other window cell, so that's fine. Now I'm asking whether each restart costs a 10% delay, which would eat the remaining slack once the target shifts.

I'm checking whether the paddle can still make the later landing if it waits at the earliest window: the window drifts two cells per row, so a later bounce sits roughly 2j cells farther off.

I'm checking whether brick information could predict a bounce at row 4, since the ball's landing depends on it, though that would need many more comparison units. I'm leaning toward keeping the simpler earliest-bounce policy, and I'm wondering whether the paddle's wait will matter once later rounds clear more bricks and the ball climbs higher.

I'm checking the post-catch case where the ball and trail sit in the same cell at the wall, which is where the type 1 handling has to apply.

I'm now writing out the post-catch cases for both catch types: for a type-1 catch the paddle stays at the trail cell, and for a type-2 catch it sits at the ball cell with the direction reversed. Then I'm folding the next landing window for each case so I can compare the distances.

I'm tabulating the post-catch cases for a ball moving right, where u_c is at most 8 and the ball sits one cell past the trail. The type-1 window is built from the trail cell and the ball cell, and for u_c = 8 the folded cell fold(10) wraps to 9, so that edge needs its own check.

Now I'm sorting out the Type 1 case: with the paddle at x_t, the window runs from 8 − x_t to 9 − x_t, so I'm checking when the paddle should move right, which is when x_t is at most 3.

I'm working through the post-catch cases for a ball moving right, comparing the windows for each catch type against the paddle's position. Type 1 sends the paddle right for small trail columns, stays at the middle, and sends it left for larger ones, while type 2 shifts those thresholds by one cell. Laying the pairs out by trail column, every combination stays within the allowed set.

Now I'm checking whether the row-8 entries of the ascending tables can serve both post-catch cases at once, since a ball at row 8 heading up can only occur right after a catch. With the trail at row 8 and the ball moving right, the two catch types give the same threshold pattern, so one encoding per ball cell should cover both.

I'm setting the threshold for the case where the trail stays at column 3: both catch types should move the paddle right toward the window, and I'm choosing the low threshold just above the ball cell so that holds.

I'm checking the edge cases for the post-catch threshold when the trail sits at column 4: the paddle should stay put for the type-1 catch and move left for type-2, so both thresholds have to collapse to the single value just under the ball cell.

I'm checking the corner case at the wall, where the ball and trail share cell (8, 9). There the paddle can only be the type-1 catcher, and the left-moving window collapses to a single cell, so nine moves out of the ten available are enough to reach it.

I'm now laying out the modes for the ball's motion, starting with the case where the vertical gap between ball and trail is +1, which is the normal descending case.

I'm checking the mode unit next: the ball is descending when the vertical gap is +1, or when the gap is 0 and the ball is not on row 8. Everything else, including the post-catch case at row 8, counts as ascending, so one threshold per cell can separate the two.

I'm checking the top-row case next: if the ball sits on row 0 with the trail beside it, it is already descending, so the desc table at that cell gives the landing column as u + 8. If the ball has just arrived at row 0 from below, the earliest bounce happens right there, at u + 9.

I'm laying out the window bounds for each mode and spin direction as layer-1 threshold units, with the deadband terms tied to the one-hot column differences.

I'm checking whether dx_raw can be zero away from the walls, and it can't: the ball and trail only share a column at the edges, so the gate term is only active at columns 0 and 9.

I'm checking the corner cases where the ball and trail share a cell, since there dx_raw is zero and the gate only turns on at the walls. At the top-right corner (0, 9) the ball has just bounced off both walls and now heads down-left, so the descending table at that cell should give a landing at fold(18).

I'm checking the corner bounce cases: at the top-right corner the ball heads down-left and lands at column 1, and after a wall bounce at (4,9) it lands at column 5. Next I'm setting up the layer-2 combinations.

Now I'm writing the layer-2 gates for the descending case: one fires when the mode unit is on and exactly one right-moving window is active, and the left-moving version is set up the same way. Next comes the ascending gate.

I'm checking the selection gates for the Q units, since mode exclusivity should keep only one of each pair active and the output reduces to right = A or −A depending on which Q fires. The remaining question is the case where both spin gates are off.

I'm checking the starting position at reset, where the ball and trail share a cell on the left or right edge, and the descending table there should give a landing column of 0.

I'm defining the descending window for each ball cell and spin direction, with the landing column computed as u + 8 − r and the window covering that column and the next one. Next I'll set up the paddle position as a weighted sum over the bottom row.

I'm weighing whether the descent window should be set narrower to shorten the paddle's travel after a catch, choosing between the two cells by which one leaves the next window closer. The worst case, a distance of 9 with 10 moves available, looks tight enough that this choice might matter.

I'm weighing whether to narrow the descent window to cut the paddle's travel after a catch, since the worst case leaves only one move of slack.

I'm now comparing the two paddle positions after a descent landing, checking how far the next window sits for each catch type, with the landing at column u_c.

I'm comparing the next-cycle distances for each landing column, and for the low columns the second catch type comes out ahead.

I'm comparing which landing cell leaves the next window closer for each column from 3 up to 9, and for columns 4 through 8 the first catch type comes out ahead.

I'm weighing a different choice for the descent window: for landings in the left half, the paddle should sit at the second cell, which sends the ball back toward the left, while for the right half it should sit at the first cell so the ball heads toward the right wall and returns. That should cap the worst-case distance at about 7, apart from the single-cell wall landing. Picking one cell rather than a window does cost the deadband tolerance, though.

I'm weighing the risk of an overshoot during the stop: if the paddle is sent back to the preferred cell and the stop fails, it can slide out of the window entirely, so the extra correction near catch time could cost more than the better next-cycle distance gains.

I'm weighing a compromise: keep the paddle on the preferred cell while the ball is high, since there's time to get there, and switch to the full window once the ball reaches rows 6 to 8, where the paddle only needs to land somewhere inside it.

Now I'm worried that a stop that overshoots could leave the paddle outside the window right before the catch, so I'm thinking about whether to aim at the preferred cell or keep the full window for the ascending tables too. For the ascending case, the earliest landing is a little different, so I'm checking which cell in the window fits best.

I'm going to use the preferred cell during the ascent as well, so the target stays the same when descent begins and there's no extra one-step correction.

I'm weighing whether the ascent target should follow the same preferred cell as the descent, since the ball may go higher than the earliest prediction and shift the landing. The bricks in rows 1 to 3 may be cleared, in which case the immediate-bounce prediction will often be wrong, but the slack should absorb that.

Now I'm checking the catch case where the ball descends into row 8 and the paddle has to be under the landing cell, which the descending table gives as the same cell as the ball's column or the one next to it. I'm also wondering what happens if the paddle can't reach the window by the time of the catch.

I'm working out the exact target for a descending ball: its landing column comes from the ball's position and spin, and the two candidate cells are the landing column and the one beside it. I'm defining the preferred cell by which side of the board the landing falls on, then mirroring that rule for the other spin direction.

Now I'm settling the preferred cell for the landing column itself: for landings in columns 0 through 8 the ball is heading right, so the paddle sits one cell over at u_c+1 when the landing is in columns 0 to 3, and stays on u_c for columns 4 to 8. Column 9 is the single wall cell, so it just stays at 9.

I'm writing out the paddle target for the upper landing range, where the ball heads left: for landing columns 10 to 13 the preferred cell is the right neighbor at 18 minus the landing column, and for 14 to 18 it's the landing column itself, with 19 mapping to 0. I'm filling in the full lookup table from 0 to 19 to check each entry.

I'm checking the mirror symmetry of the paddle-target table: reflecting the board maps landing column u to u + 10, and the preferred cell P should satisfy P(u + 10) = 9 − P(u). Spot checks at u = 0, 3 and 4 against their mirrors at 10, 13 and 14 hold up.

I'm checking the lookup values against the mirror rule, and they hold for u_c = 4, where the paddle already sits in the next window. For u_c = 3 the preferred cell is 4, the type 2 choice, and I'm working out its next window from there.

I'm settling on the preferred paddle cell for descending landings, and the lookup table checks out against the mirror symmetry. For a descending ball that is still high, I'll aim at the preferred cell, and switch to the full window near the catch, where any spot inside it still catches the ball.

I'm checking the sticky failure case at row 7: if the paddle moves from the non-preferred window cell to the preferred one, then at row 8 the target says stay, but a sticky slip could carry it out of the window, so the move to the preferred cell right before the catch looks risky.

I'm weighing the sticky-stop risk at row 5: if the paddle moves to the preferred cell there, a 10% overshoot at row 6 followed by a correction could leave it outside the window by row 8, roughly a 1% chance of missing. Starting the full-window approach earlier, at row 4, would let the paddle stop inside the window more reliably before the catch.

I'm settling on the ascent target now: the paddle should head for the preferred cell while the ball is still climbing, then switch to the full window once the descent reaches row 5 or below, since that leaves room to correct an overshoot before the catch.

I'm checking the ascent case now: if the ball skips the row-4 bounce and is climbing at row 3, the immediate-bounce formula gives a landing column of u + 6, so I'm working out how that shifts the predicted window.

Now I'm working out the post-catch case: the ball is at row 8 heading up, and I need the next landing window for both bounce types, using the preferred cell rule.

I'm now working out the post-catch case for each starting position: for the paddle-type choice, the next landing is the ball's column plus ten, and the alternative branch lands at seven minus the trail column, with the matching paddle cells being the trail column and the ball column.

I'm tabulating the remaining post-catch cases for each trail column, comparing the two landing cells and the paddle cell each bounce type needs. For columns 0 through 2 both choices need the paddle to move right, and at column 3 the alternative branch lands on the paddle's current cell, so it can stay put.

Checking the post-catch cases for the trail columns 4 through 8: for each, the first bounce type lands on one cell and the alternative lands on another, and the paddle has to move left in most of them. The table covers every trail position with a representable pair of paddle choices.

I'm checking the x_t = 4 case: the paddle sits on the preferred cell 4 after the last catch, but the next landing at column 14 wants cell 5, so it would have to step over. Moving one cell gives plenty of time before the catch, but I'm wondering whether the full window during ascent would avoid the extra start and stop.

I'm weighing whether to keep the paddle on the preferred cell during ascent or use the full window, since a paddle that approaches from behind arrives at the preferred cell first, while one coming from ahead reaches the other window cell first.

I'm weighing whether overshooting by one cell during ascent matters: with the slack I have before the catch, a single extra correction is cheap, and starting from the preferred cell keeps the later descent move short.

I'm working through the post-catch case where the ball is at the wall, where only one paddle cell is valid. That leaves almost no slack, since the paddle has to cover nine cells in ten moves, and a single sticky delay would already eat most of the margin.

I'm checking whether the wall case is really safe: the paddle has to cover nine cells in ten moves, but moving continuously produces no stop changes, so the only real exposure is a single sticky start delay, which the slack absorbs.

I'm also checking the wall-corner catches, where the paddle needs nine cells in ten moves, and the earlier bounce timing at row 4 should cover the ball climbing higher, so the target may shift and the paddle might reverse, but there is enough time for that.

Now I'm checking whether the ascending case at row 4 holds: the earliest bounce there is predictable, so the landing window stays fixed. If the ball is climbing through rows 5 to 8 with a downward trail, the normal descent logic applies.

I'm now laying out the explicit lookup tables for each ball cell and both modes, with the descent case using the preferred cell in the upper rows and the full window from row 5 down. I'm also checking whether the catch observation at row 8 still leaves the paddle inside the window.

I'm now writing out the descent-mode rules and the ascent-mode targets, with rows 0 to 7 using the preferred cell from the computed bounce column, and I'm about to work through the row-8 post-catch table for each starting direction.

I'm working out the post-catch window for ball column x_b = x_t + 1, and for the first case where x_t is 0 both bounce types need the paddle to land on a cell at least x_b + 1, so I'm setting the target to the smaller of the two preferred cells so both decisions stay valid.

I'm filling in the post-catch table for the case where the ball sits at column 4 after the paddle cleared column 3. I'm checking that type 1 still lands the paddle correctly, and then I need to work out what the paddle should do for type 2, where both bounds might sit on the same cell.

I'm settling on thresholds of 0.25 instead of 0.5, since the exact-boundary case at x_b = 5 leaves the type-1 decision sitting right on zero, so the lookup for that column needs a little more margin.

I'm settling the thresholds at 0.25 with K = 40, since a half-integer target like 4.5 leaves the type-1 and type-2 decisions with a workable margin of 0.25 each.

I'm working through the post-catch case for ball column 6, where both bounce types need the paddle to move left, so the target has to sit about a quarter cell below x_b - 1. I'm keeping the gating margin large enough that the off-branches saturate cleanly.

Now I'm settling the post-catch targets for the trail columns: for ball columns 7 through 9, I'm setting the target to 3, 2, and 1, since both bounce types need the paddle to move left there and the exact value only affects this one decision.

I'm mirroring the right-moving post-catch targets for the leftward case: each ball column maps to 9 minus the matching target, so x_b = 8 gets 2, 7 gets 3, 6 gets 4, and 5 gets 5, with the next column still to come.

I'm settling the mirrored post-catch targets for the leftward case, with the wall-corner ball at column 9 needing the paddle to move left toward cell 0.

I'm checking the corner case at column 0 for the ball moving up-right: the paddle at column 0 bounces it, so the next target is cell 9, which gives the mirrored entry of 0 at column 9.

Now I'm double-checking the mirrored table entries for the leftward case by computing x_b = 4 directly: the previous catch landed at column 5 moving left, so the paddle's two possible positions both put the ball at column 4, and the preferred cell comes out at 4 either way.

I'm checking the mirrored table entry at column 5 for the leftward case, where the type-1 decision should move left and the type-2 decision should hold, so the target sits at 5.

Now I'm finishing the remaining trail entries for the descent tables, and I'm checking each paddle target against the bounce rules.

Now I'm encoding the policy's gating and threshold weights into the first layer, with each unit's pre-activation built from the target window, the paddle position, a fixed margin, and a large gating term.

Writing the weight encoding for the mirrored case now...

Writing the ball-channel weights for the mirrored case now...

Still writing the weight encoding, with the paddle-channel entries for row 9 set to step down by K per column.

Still working out the weight encoding for the mirrored case, with the ball-channel values built from the table entries plus a scaled position term.

Now I'm checking the mode unit's threshold, where the pre-activation depends on the row the ball sits in and the drop of one when it reaches row 8, before I fill in the full tables.

Now I'm checking the mode unit's threshold with K_m = 10: descent cases come out at or above 0.5 and ascent cases at or below -0.5, and the row-8 corner still lands on the right side of the boundary.

I'm checking the edge cases where the ball and the trail share a cell: at (3,0) with V=0 in row 3 the mode stays descent, and at (8,0) or (8,9) it is ascent after a paddle catch. I'm also confirming that a top-corner collision at row 0 still leaves the ball descending.

Now I'm settling on the softmax gain for the output layer, since a large A keeps the chance of a wrong move per step tiny over a long episode.

I'm settling the softmax output weights now, with the right and left logits each built from their two Q units and a large gain of 30. For the stay-put and vertical actions I'm leaving the logits at a strongly negative bias so that no-op dominates.

I'm now tabulating the preferred-cell values, where the lookup maps each fold position to its target, with 0 and 10 bouncing back toward the middle.

Now I'm listing the window for each fold position: the two cells the ball can land on, from 0 through 14, with the pairs at 9 and 10 collapsing near the middle.

Now I'm checking the window values for the edge positions, where the window at u = 8 covers cells 8 and 9 and the preferred cell is 8 since the ball is on the right half. At u = 0 the window is cells 0 and 1, with the preferred cell at 1. I'm also confirming that u = 18 gives the same pair as u = 0 because of the fold.

Now I'm checking the case where the ball sits at column 0 and is moving left, using the mirrored rule: the paddle should go to 1 for that column, and I'm confirming the type 1 and type 2 distances agree on that choice.

Now I'm checking the descent tables, where the lookup for each row is the paddle's preferred cell when the window is narrow and the two-cell window when the ball is lower.

Next I'm checking the descent tables: rows 0 through 4 can just use the preferred cell, and bricks below shouldn't change that. Now I'm setting up the ascending tables, where the target depends on whether the ball is in the upper or lower rows and on the strike timing.

Now I'm working out the descent table for mode D with the paddle going right, starting with row 0, where the target cells run from 8 up through 2 as the ball's column shifts.

Now I'm filling in the per-row target lookup for the descent tables, going row by row from row 0 down to row 5.

Still filling in the lookup tables, now on rows 7 and 8 of the descent table for the rightward case.

Still filling in the mode D table for the leftward case, starting with row 0, where the target cells for each column come from the shifted position of the ball.

Checking the mirrored row-0 table for the leftward case: each entry should be the reflection of the rightward one, and the first values line up with the preferred-cell lookup.

Now I'm using the mirror symmetry to fill in the leftward descent tables from the rightward ones, so that each leftward entry is 9 minus the rightward entry at the reflected column, with the window bounds swapping sides.

Now I'm working through the row 1 entries for the leftward descent table, using the mirror of the rightward values and checking a few cells directly against the shifted position.

Still working out the mirrored descent tables for the leftward case, checking the row 2 and row 3 entries against the reflected rightward values.

Still working out the mirrored lower-window entries for the leftward descent table, going through the remaining columns of row 5.

Now I'm checking the leftward lower-window entries for row 6, using the mirror of the rightward values and verifying a few cells directly against the shifted position.

Now I'm using the mirror symmetry to fill in the remaining leftward lookups for row 7, flipping the rightward values around the centre column.

Now I'm filling in the leftward table for row 8, checking the window bounds against the mirrored rightward values at column 5.

Now I'm working through the ascending tables for the rightward case, starting with row 0, where the target cells run from 9 down to 1 as the ball's column shifts.

Now I'm writing out the ascending tables for rows 3 through 8, where each row's target cells shift with the ball's column.

Now I'm checking the post-catch case at column 9 for both paddle positions: the paddle at 8 gives a target of 1, while the paddle at 9 gives 0, and both still lead to a leftward move.

Now I'm writing out the mirrored ascending table for row 0 on the leftward case, reflecting the rightward values around the centre column.

Still working out the mirrored ascending table for the leftward case, checking the row 3 and row 4 entries against the reflected rightward values.

Still working out the mirrored ascending table for the leftward case, filling in the post-catch row 8 values from the corner column across.

Now I'm checking the mirror symmetry for the post-catch row 8 ascending table, and it matches once I reflect the values around the centre column. I'm also noting that the rightward descent table for mode D still needs its lower-bound entries filled in.

Now I'm laying out the layer-1 units: one for the mode, and eight for the paddle targets covering the descent and ascent cases in each direction.

Now I'm setting the weights for the right-moving and left-moving units in the ascending case: the ball's target cell scaled by 20, a large term on the ball's column for the sign of the move, and a penalty on the trail column.

Still writing the weight terms for the left-moving units: the descent-side ball weights get a large mode-dependent multiplier, and I'm setting the trail penalty and bias to match.

I'm settling the sign gate for the ascending-side units: the ball term goes on with a large multiplier that is shut off when the ball's move would be negative, and I'm checking that the off case stays below the activation threshold.

Now I'm checking the sign gate for the ascending units: when the move is negative, the ball term is switched off with a large multiplier, and I'm confirming the off case still falls below the activation threshold. I also need to settle the half-integer table entries with a 0.25 margin.

Checking the half-integer margins for the activation cases: at (8,5), the rightward ascent unit fires for paddle at 4 but stays off for paddle at 5, and the leftward one does the opposite. For whole-number targets, a zero difference gives a pre-activation of -5, so the unit stays off.

Now I'm setting up the mode D weights for the mid-ball unit, scaling the ball's row contribution by 10 and subtracting the trail.

Now I'm checking the margins on the integer and half-integer target cells, and the mode-D unit's bias and weights hold up. I'm setting up the layer-2 unit for the right-descent case, where the summed inputs from the mode and the two right units should put it fully on.

Now I'm finishing the layer-2 output weights, setting the right-move output from the two right-descent and right-ascent units.

Now I'm checking the leftward output weights, setting the left-move logits from the two left-descent and left-ascent units, with the noop and other actions pushed down.

Now I'm stepping through a sample start to check the policy: the ball begins at row 3, column 0, heading down-right, with the paddle at 4. The descent table gives 5 there, so the right move fires, and after the paddle shifts to 5 the ball moves to row 4, column 1.

Now I'm checking the catch step at (8,5): the paddle stays put and the ball goes up-right. Then after the catch, the ascent table gives a target of 4 from the paddle at 5, so I move left.

Now I'm tracing the ball down to row 4 at column 9, where the left-hand gate switches on and the paddle should stay at 4.

Now I'm checking the descending case at row 4: the ball sits at column 8 with the paddle at 4, and the window lands on 4, so the paddle holds.

Now I'm checking the lower-bound table entries for rows 5 through 7 on the descending case, and they hold at 3 and 4 across those columns.

Now I'm tracing the ball's next moves: from (8,3) it heads up-left, and with the paddle at 4 the post-catch table gives a target of 5, so the paddle shifts right.

Checking the catch and bounce cases at the bottom row, the ball at (5,0) flips to up-right and lands on the brick at (3,1), and the paddle stays at 5 by the same type-1 rule. That makes the ideal sequence a symmetric bounce where the paddle oscillates between 4 and 5. Each cycle starts with a post-catch move that I'm still tracing.

Now I'm checking how the ball behaves once a gap opens up in the row 3 bricks: at (3,8) there's nothing to hit, so the ball keeps rising, and the ascending table there gives a target of 2 from the current column.

Now I'm checking the far-wall case: the ball reaching the corner column at the bottom row and how the ascending table handles a catch there.

Now I'm working the ball's path into the far corner: a catch at column 9 means the paddle has to sit at 9, and the post-catch table moves it left one step at a time.

I'm checking the paddle's catch-and-return timing at the far corner: if the paddle has to cover the full distance, one delayed step leaves one slack, but a second delay would make it miss. I'm wondering what could cause that second delay, such as a sticky action at the start or the previous action carrying over after a failed start.

I'm checking whether the paddle can stay inside the window once the ball reaches the descent rows, since the rule changes from the preferred target to the full window at row 5 and below.

Now I'm checking the descent prediction once the ball passes down through the brick area, and whether a brick in its path near row 3 sends it back up.

Now I'm checking the folded case for the ascent above row 4: the target moves two cells per step while the paddle can only move one, so I need to confirm the paddle still keeps up once the ball's motion is measured along the fold.

Now I'm going back over the paddle's slack at the far corner. A second delay would make it miss, so I'm weighing how likely that is if a start failure is followed by a sticky action on the next step.

Next I'm checking the direction-flip and margin definitions for the R and L units in A-mode, using the single threshold T rather than separate bounds. The remaining question is the initial reset, where the ball starts at the right edge heading down-left with its trail on the same cell.

Now I'm checking the start state at (3,9) heading down-left with the paddle at 4: the descent table gives 4 there, and the projected landing at column 4 also falls inside the window, so the paddle stays put.

Now I'm checking the paddle's position after a type-2 catch, where it lands at the ball's next column, and after a type-1 catch, where it stays at the catch column.

Now I'm checking the corner case at column 9: a type-2 catch from (8,8) moving right puts the ball at (8,9) heading up-left with the paddle on 9, so the post-catch observation gives a +1 shift.

Now I'm checking the post-catch case at (8,9): if the paddle is at the ball's column, a catch sends the ball up-left and the post-catch table shifts the paddle left, and the pos-8 version ends up at (7,9) moving up-left, which matches the predicted column.

Now I'm checking the ascent table for row 8 against the post-catch decision, and whether the target at row 7 lines up with the intended move.

Now I'm checking whether the full window should also apply to the ascending rows, or whether the preferred cell still works there. The descending rows 0 to 4 use the preferred cell, and a ball descending after a top bounce might land somewhere unexpected if bricks are below it.

Now I'm weighing whether a brick-aware bounce check is worth adding, since there's spare hidden-unit capacity but the extra complexity could introduce new mistakes.

I'm weighing the risk profile now: the main exposure is a far landing with only one step of slack, which carries roughly a 1% chance of a miss. If the ball's predicted bounce row shifts higher, the target moves too, and I'd have to account for that shift rather than assume the original landing holds.

I'm checking the slack on a paddle that has to cover a longer distance after the ball's bounce row shifts higher: the target moves two cells, so the paddle needs two more steps, and since it has been waiting early it should still have plenty of moves left. I'm also noting that the main exposure is still the far-corner cases, where the risk is about 1%.

Now I'm testing the far-landing worst case: with preferred-cell choices, the distance after a catch is at most 7 except at the corner columns, where it reaches 9.

Now I'm tallying the distances for each catch column: for the left-side cases the gap is 6, 4, 2, or 0 depending on the column, and for the right-side cases it runs from 0 up to 7, with the corner column 9 giving 9. Those figures measure to the nearest edge of the window, so the preferred cell could add one more.

Now I'm checking the corner distances: the far landing tops out at 7 everywhere except the corner, where it reaches 9 with only one step of slack. Corner catches seem fairly rare, so the overall risk should be small, but I'm wondering whether the ball's path from (8,9) up-left toward the far corner can be steered more safely.

I'm sketching the corner-to-corner loop: the ball bounces between the two corner columns, and the paddle covers about nine cells each cycle until the bounce row shifts. Because the catch at the corner is forced, I can't steer it, so I'll accept the small risk and check how the slack works out when the paddle has a distance of seven and only ten moves.

Now I'm checking the slack that remains after a misprediction: if the ball rises higher than expected, the target shifts but the paddle still has time to cover it. I'm also confirming that the descent case from row 0 holds with a paddle waiting somewhere, and that the two edge gates at columns 0 and 9 can't both fire when the horizontal difference is zero.

Checking the left-wall case now: when the ball sits at column 0 and its trail is also at column 0, the vertical bounce counts as a stay step and the direction flips to up-right, so the ball is treated as moving right. I'm verifying the A-mode table entry for row 4 at column 0 gives 5, which matches the predicted landing.

Now I'm checking the ball at row 8, column 0, wondering whether a type 2 catch could send it up-left to (7,0) with the trail at (8,0), since that move would clamp at the wall.

Now I'm checking the case where the ball reaches row 8 at column 0 after a type 1 catch at column 18, with the paddle at column 1 moving to column 0, so the ball heads up-left, clamps at the wall, and lands at (7,0) moving up-right.

Now I'm writing out the ball-weight lists for each unit, one 100-entry list per unit, building them from the same landing formulas I've already checked.

Now I'm writing out the ball-channel weights for each unit, using the gate offsets G+ and G- and the scaled landing tables.

Now I'm weighing whether to fill each unit's ball weights by multiplying the landing tables and adding the gate offsets in one pass, or to write the table part first and add the gates afterward, since the large gate values make the direct arithmetic error-prone.

I'm weighing how to fill the ball-channel weights for each unit: either writing the full 100-entry lists directly, or using column-wise additions for the gate offsets, since the large gate values make direct arithmetic error-prone and I'd rather not depend on an uncertain `+=` syntax.

Still writing the ball-channel weights...

Still writing the ball-channel weights, now leaning toward adding the gate offsets with `+=` on each column slice.

Still writing the ball-channel weights, now weighing whether to add the gate offsets separately or restructure the gating across layers instead.

Still writing the ball-channel weights, now settling on a layer-2 layout with separate AND units for each gate state.

I'm designing a sign-gate unit that fires on the direction of travel: it gets a positive weight for a rightward move and a negative one for leftward, with half-weight adjustments for the edge columns where the direction is ambiguous.

Now I'm working out the sign gate for the ball's direction: it's a tanh of a scaled signed difference, with the edge columns nudged by half a unit so the wall cases still read correctly. I'm setting its ball weights to the column ramp and its trail weights to the negative column, with no bias.

Still writing the layer-2 AND units...

Still working out the output layer: I'm checking whether the tanh-gated sums hold up at the edge values, with the bias set so that "none on" gives a negative logit and "one on" gives a positive one.

I'm settling the layer-1 design: the gate and comparison units will be built from tanh-scaled sums, with the right and left weights set so that one of the paddle-side checks fires at a time.

Now I'm laying out the weights for the layer-1 units: M_D and G_S first, then the right and left comparison units, with the ball weights scaled by 20 and the paddle weights set in the opposite sign for each.

Still writing the ball-channel weights for the M_D and G_S units...

Still writing the ball-channel weights and the paddle rows for the comparison units...

Still writing the layer-2 weights...

Still writing the layer-2 weights...

Still writing the ball-channel weights for the layer-1 units...

Still writing the ball-channel weight tables...

Still writing the ball-channel weight tables...

Still checking the row-by-row window values for the right-side mode, verifying each column's two-cell range at rows 6 through 8.

Still checking the row 4 to row 2 values, verifying the descending preferred windows for the right-side mode.

Still writing the descending-mode window tables...

Still writing the descending-mode window tables...

Still writing the descending-mode window tables...

Still checking the row 4 descending values, verifying the window ranges as the column index moves across the board.

Still checking the descending-mode window values for the left side, verifying the low and high ranges at rows 6 through 8.

Still checking the window values for the descending left side, confirming the clamped edge cells at rows 5 through 8.

Still writing the table rows for the descending-mode values.

Still checking the table values for the mode A sweep, confirming the descending rows and the edge entries in row 8.

Still writing the mode A sweep tables...

Still checking the mode A values on the left side, verifying the descending window entries at rows 0 through 8.

Still checking the row 7 values for the mode A sweep, confirming the descending entries as the column index moves left to right.

Still writing the ball-channel weight tables...

Still writing the ball-channel weight tables...

Still writing the ball-channel weight tables...

Still writing the ball-channel weight tables...

Still writing the descending-mode ball-channel tables...

Still writing the ball-channel weight tables...

Still writing the ball-channel weight tables...

Still writing the ball-channel weight tables...

Still writing the weight tables for the remaining units...

Still writing the descending-mode ball-channel tables...

Still writing the weight tables for the mode A units...

Still writing the ball-channel weight indices for the M_D unit...

