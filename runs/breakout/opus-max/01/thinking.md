I'm setting up the MinAtar Breakout policy by hand, starting with the grid layout: the paddle sits on row 9 at some column position, and the ball has a row, column, and one of four diagonal directions.

I'm working through the ball's movement rules now: each step the paddle moves first, then the ball advances by its direction, with wall bounces flipping horizontal direction and ceiling bounces flipping vertical. I'm also checking the brick-collision case, where a second strike in a row leaves the brick in place and the strike flag stays set.

I'm going through the ball's bottom-row cases: if it lands on the paddle column it bounces back up, staying at row 8 with its vertical direction flipped, and if it only reaches the paddle's edge it reverses diagonally instead.

I'm checking whether the paddle catches the ball, which depends on the paddle's position after it moves this step matching either the ball's current column or the column it's moving into. If the ball would move past the wall, I'm tracking that the x-coordinate gets clamped and the horizontal direction flips first, so the catch test then uses the clamped column.

So the paddle has to be at either the ball's column or the column it's moving into, since that gives the catch some slack. After a catch the ball stays on row 8 and slides one cell sideways with an upward direction. Next I'll look at how the observation channels encode the ball's position.

Next I'm checking what the trail cell tells me about the ball's direction. The horizontal and vertical steps can be read from the ball and trail positions, except where a wall or brick has changed them, and a paddle hit or brick strike makes that reading misleading.

I'm checking how the trail cell reveals the ball's motion, and the edge cases at the top and side walls. At row 0 the ball just slides sideways and its direction flips downward, and at the side walls it moves only vertically after the clamp. So the trail only gives a reliable direction away from those boundaries.

I'm working out how the trail cell reveals the ball's direction. If the apparent motion is diagonal, it matches the true direction unless a wall clamp or bounce changed it during that step, and a clamp at the side walls zeroes out the horizontal component.

I'm checking the brick cases where the ball's horizontal direction gets flipped by a side wall at the same time, since the brick strike can flip it again and leave the ball in place with no visible motion.

I'm checking what the trail tells me when the apparent motion is zero in one direction. A vertical flip with no visible vertical change can be a wall or brick effect, and I need to figure out which way the ball was moving before that flip.

I'm working out how a paddle hit reverses the ball, and it comes down to whether the paddle sits at the ball's column or the column it's moving into. Either way the ball ends up at row 8 sliding horizontally, so the apparent motion there is purely sideways, and I still need to sort out which vertical direction the hit leaves it with.

So the paddle's position decides which case applies. If it sits on the ball's old column, the horizontal direction is kept, and if it sits on the new column, the direction is fully reversed. I can't tell the two apart from the ball and trail positions alone, and at a wall both collapse to no visible motion.

I'm weighing whether a simple rule works: shift the paddle toward the ball's column each step. Since both the paddle and the ball move one column per step, the paddle could keep pace once it's aligned, though the order of moves matters for whether it actually catches the ball.

I'm testing whether a paddle that trails the ball by one column can still catch it. Because the paddle moves first and the ball then advances, a simple follow-the-ball rule leaves the paddle one step behind, so I need to check whether the catch condition still holds when it reaches row 8.

Checking whether a lagging tracker still catches the ball, I'm thinking the paddle can stay one column behind and still meet the ball on row 8 by moving toward it. The open question is whether the horizontal gap holds up after a wall bounce, since the ball then approaches the paddle.

I'm working out how much time the paddle has: after a catch the ball climbs to the bricks, bounces back down, and returns to row 8 about eight or nine steps later, which is enough horizontal distance for the paddle to cover if it stays close.

I'm checking that a simple tracker, one that moves the paddle toward the ball's column, keeps up once aligned, since both move one column per step. I'm tracing the ball from (3, 0) down-right to see when it reaches row 8.

I'm checking that the paddle starting at column 4 can follow the ball down from column 0. A tracker that moves toward the ball's column should line up with it at row 8, since both move one column per step. I want the logits to favor the correct move strongly so sticky actions don't throw it off.

I'm considering whether the paddle can be positioned in advance by predicting where the ball will land on row 8, which would mean modeling the wall reflections. That could be hard for a small network to represent, though it might be manageable.

I'm working out the clamped reflection at the side walls: a ball that hits column 9 sits there for two steps before heading back, so the column sequence reads like ...7, 8, 9, 9, 8, 7... That folds into a single coordinate with period 20, which gives a clean mapping back to the column.

I'm settling on a policy that aims the paddle at the landing column: when the ball is heading down, I'd work out which column it reaches on row 8, accounting for the ball's direction, and steer the paddle toward that spot.

I'm checking the case where the paddle sits one column ahead of the ball after a wall bounce, since that's the remaining situation for a pure tracker to verify.

I'm checking that a tracker keeps the paddle within one column of the ball, since the ball's horizontal speed matches the paddle's, so the gap can't widen once the paddle is close.

I'm checking how the paddle's offset from the ball changes each step: the paddle moves toward the ball, and the ball's horizontal move can shrink or widen that gap, except at the side walls where the ball's column stays put for a step.

I'm checking that the paddle's gap from the ball can't grow past one column when everything runs as planned, since each step the paddle closes the gap by one while the ball's horizontal move changes it by at most one. Sticky actions and sampling noise can push the gap to two, and then a ball moving away from the paddle keeps it there, so I'm looking at how that recovers.

I'm seeing that a sticky action that repeats the previous move can push the paddle's offset from the ball to two columns. Once that happens while the ball is moving away, the gap doesn't close on its own, so the catch fails unless the ball reverses at a wall first. With sticky actions at 10%, that kind of error should come up often enough to matter.

I'm now checking the case where the paddle lags the ball by one column. If the ball moves diagonally and the paddle trails it, the tracker always takes the same move in the ball's direction. Then when the ball hits the side wall, I'm working out how the direction flips and where the paddle ends up.

I'm checking how the tracker behaves at the side walls: the paddle stays clamped there, so a sticky repeat of "right" does no harm. Moving left with the ball, the paddle keeps a one-column lag and stays in place. I want to see whether the paddle can still meet the ball at the moment it drops onto row 8.

I'm checking whether the tracker's action changes in steady state: the ball's horizontal direction only flips at side walls or a paddle hit, so the action mostly stays constant. At the side wall the paddle is clamped, so a repeated "right" does no harm, and I'm testing that case where the ball sits at column 8 with the paddle one behind.

I'm checking the wall case again: when the ball bounces off column 9, the paddle stays clamped there, so a sticky "right" does no harm. The real risk is when the intended move is "left" and a sticky "no-op" repeats instead, which would leave the paddle at distance two.

I'm working out the failure case: if the paddle ends up two columns behind the ball while the ball moves away, it misses, and a sticky "no-op" at the right wall can cause exactly that roughly 10% of the time. That makes pure tracking too fragile, so I'm leaning toward a policy that positions the paddle ahead of the predicted landing column.

I'm thinking about switching from pure tracking to aiming at the predicted landing column, since the ball's horizontal path is deterministic and the wall clamping can be folded into one unfolded coordinate. I want the paddle to sit where the ball will drop onto row 8 rather than chase it.

I'm checking the reflection rule for the unfolded coordinate on the left wall, where x goes 1, 0, 0, 1 as the ball bounces back, and I want to confirm the top-wall step keeps the same x behavior.

I'm checking how the horizontal motion behaves at the top wall and at the bricks, where the ball's column advances normally and only the side walls clamp it. The question is what happens when a side-wall clamp and a vertical event happen on the same step, as when the ball sits at row 8 in column 9 heading down-right.

I'm working out how many steps the paddle has before the ball reaches row 8, since the paddle moves first each step and the catch is checked after that. The time available when the ball is heading down from row y is the vertical distance to row 8, plus one more move for the check itself.

I'm working out how far ahead the paddle has to be, since the time before the ball reaches row 8 is the number of rows it still has to fall, plus the check step. With the ball coming down from row 4, that gives about five moves, while the ball itself covers about four columns, so a paddle within a column or two of the ball's current position could still get under the landing spot.

I'm weighing a predictive approach, where the paddle heads for the ball's landing column rather than its current position, since there's usually enough time to get there. The catch is that the network would have to learn a nonlinear landing-column function from one-hot inputs, and I'm wondering whether 32 hidden units per layer can represent that, or whether a simpler lead offset from the ball's direction would do.

I'm working out how to encode the landing column for the MLP: since the ball and trail are one-hot, a hidden unit can take an arbitrary table of each cell's contribution, so the tanh units can combine ball, trail, and paddle positions additively. The trouble is the direction term, which depends on the ball and trail together rather than separately, so I'm looking for a channel combination that captures "trail is left of ball" in a linear way.

I'm sketching how the network could pick the paddle move: each feature is a linear function of the ball, trail, and paddle channels, so the ball-minus-trail difference gives the direction in one step. The action comes from comparing the target column with the paddle, and I'm starting to look at threshold units in the first layer that measure the gap to the paddle.

I'm setting up threshold units that compare the ball's column against the paddle's: one fires when the ball is at least a column to the right of the paddle, and another when it's at least a column to the left. Those two signals would map directly onto the right and left actions.

I'm checking the predicted-landing idea against the pure tracker: the right and left signals are clean when the paddle is off by one, but the real question is how to get a landing-column target out of the ball and trail features, since the true direction depends on both of them jointly.

I'm listing the direction changes for the unfolded dynamics: a side wall clamp gives dx_a = 0 with the true dx flipping toward the interior, the top wall forces dy to +1, and a brick reverses dy from whatever it was.

I'm listing the remaining cases where the apparent motion and the true direction disagree: a paddle catch can flip dx or leave it alone, and the ball always ends up moving up at row 8. Wall-plus-top and similar corner cases leave the ball where it is with both apparent deltas at zero, so the true direction has to come from elsewhere.

I'm checking the corner cases now: at the top-left and top-right corners the ball's direction follows from its position, and when it lands on the right wall from below it heads down-left. I'm also sorting out the paddle catch at row 8, where the paddle's position relative to the old ball column tells me whether the horizontal direction was kept or reversed.

I'm checking which way the paddle has to move to cover the ball's next column, and whether the last move was a bounce off the paddle.

I'm weighing whether a predictive target, the ball's landing column, beats pure tracking. Tracking leaves the paddle within a column of the ball, but any stickiness or noise leaves a persistent offset that only clears when the ball reverses horizontally. Aiming at the landing spot instead lets the paddle wait there while the ball falls, though it has to stop exactly on the target, since an overshoot from sticky actions takes a step to correct.

I'm now considering whether the landing column can be predicted when the ball is heading up, since its return depends on which brick it hits. Rather than model that, I'm thinking about expressing the landing time as the number of steps until the ball reaches row 8 while moving down, with the landing column shifted by that count.

I'm working out how far the ball travels on its way back down when it's moving up: it climbs from its current row to the row where it turns around, then takes one step to bounce, then falls the rest of the way to row 8, so the total steps depend on where that turnaround row is.

I'm working out the landing time when the ball is moving up: it climbs to the row where it turns around, takes one step to bounce there, then falls back to row 8, so the total comes to y + 9 - 2r, and for a top-wall bounce (r = 0) that simplifies to y + 9.

I'm checking the catch timing for the downward case: once the ball reaches row 8 the paddle needs to be at the landing column or one step from it, and that gives T + 1 actions in total. The open question is how bricks along the upward path change the turnaround row, since only the diagonal cell ahead is checked for a hit.

I'm weighing how good the score needs to be, and recalling that trained MinAtar Breakout agents typically reach scores in the ~10-100 range depending on the method, so a simple tracking strategy with a small lead may already be competitive.

I'm estimating what score is realistic here: a perfect agent could keep playing for a long time, since the game is deterministic apart from sticky actions, so the ceiling is high. Each brick is worth one point, and a ball round trip takes roughly ten to sixteen steps, which puts the theoretical maximum in the hundreds over a 10,000-step episode.

I'm noting that a ball entering row 0 can bounce along the top wall and break a brick every other step, since it alternates between the wall and the bricks below it. The open point is whether the strike flag changes that pattern on the next step.

I'm weighing how strong a score is realistic: the brick-hit strike rule means each brick still counts when the ball bounces along the top, and trained DQN-style agents land somewhere around 15 to 30, with stronger methods reaching 30 to 90. Since any miss ends the episode, the hand-built policy needs to rarely miss.

I'm thinking about how much robustness matters here: with sticky actions, any single step of error can cost the whole episode, so the paddle should already be in position well before the ball arrives.

I'm settling on margins of around 15-20 in the logits, since at that size the softmax noise drops to roughly 3e-7 per action and the chance of a stray action from noise becomes negligible over a long episode. The sticky-action repeat is a separate effect I still have to plan around.

I'm settling on the no-op actions: since 0, 2, 4, and 5 all do nothing, I'll just make the non-noop actions strongly negative so the choice is effectively between staying, left, and right. The real risk is the 10% sticky repeat, so I need the policy built to absorb that.

I'm comparing three targeting options for the paddle: pure tracking of the ball's column, tracking one step ahead to account for the ball's motion, and predicting the landing column while the ball is falling. I'm considering how each one handles the errors that come from action changes at wall bounces.

I'm checking whether the paddle can still make the catch if I switch to the landing target once the ball turns downward, since it would have only a single spare step. Tracking the ball's column keeps the paddle within one cell, so a sticky error would leave a lasting offset of two, and I'm wondering whether to predict the landing spot during the upward leg as well.

I'm working through the paddle's lag under sticky actions on a right-bounce: when the ball reverses at the wall, the paddle has to switch direction, and a repeated previous action can leave it two cells behind the ball.

I'm seeing that a single sticky repeat at the right wall leaves the paddle two cells behind, and since the ball then moves away from it, that offset persists until the ball lands. Simply chasing the ball's column won't be reliable, so I'm considering aiming at a point ahead of the ball to close that gap. Next I'm weighing how to set the target to the ball's predicted position.

I'm setting the target to the ball's predicted next column, so the paddle sits directly under the ball after each step. When the ball bounces off the right wall, the paddle reaches the wall at the same moment, and the next move has to reverse direction.

I'm working through the lag case now: after the wall bounce the ball turns left, the paddle's repeated action keeps it at the wall, and the gap opens to one cell. With the target set one step ahead, that leaves the paddle a cell behind the ball, and I'm asking whether a one-cell lag is still safe at catch time.

I'm seeing that with the lead-one target, a single sticky error leaves the paddle one cell behind the ball, which still catches. Only two sticky errors in the same leg would push the lag to two and cause a miss, so the failure risk per leg is about 1%.

I'm checking the lag case once more: after one sticky error the paddle trails the ball by one cell while moving left, and it keeps the same action until the next wall bounce. I'm now tracing what happens at the left wall, where the ball stays at column 0 for a step before reversing.

I'm checking what happens at the left wall: the ball bounces there and turns right, and the paddle's clamp at the edge lets it catch up to a lag of one. So a single sticky error at the left wall doesn't push the lag to two.

I'm checking the lag after a wall bounce: a sticky repeat right at the bounce leaves the paddle one cell behind, which is still within the catch window. During the steady leg the action doesn't change, so no new sticky errors can occur until the next bounce.

I'm checking the synchronized case now: with the paddle under the ball and the ball moving left, I'm testing whether a left move of the paddle lands where the ball will go.

I'm checking the synchronized case: when the paddle sits directly under the ball and moves left, it actually catches the ball and reverses its horizontal direction. So the observation would show the ball moving away from the paddle, even though the true direction has flipped, and the network has to recognize that reversal.

I'm checking whether the paddle gets the wrong direction read when it hits the ball with the reversal case. If the paddle sits under the ball while the ball is on row 8 with no vertical trail, the network has to treat that as a reversal rather than a straight continuation.

I'm noticing the case split matters here: if the paddle sits at the trail's column, the original direction holds, but if it sits at the ball's column, the hit reverses the direction, so the network has to read the paddle position against the trail to tell them apart.

I'm checking the corner case where the ball sits on row 8 at column 9 after bouncing off the right wall, with the trail also at column 9, so the observed direction reads as a wall-consistent leftward move. Next I'm turning to the ball on row 7 at column 9 moving down-right.

I'm checking the ball's landing position after it bounces off the right wall, and the rule for reflecting its horizontal direction at the edge.

I'm checking the lag after a wall bounce: a sticky repeat at the bounce can leave the paddle one cell behind, and I need to see whether that lag clears at the next wall. Next I'm tracing the synchronized case on a down-left ball, where the paddle steps left onto the ball's cell and the hit reverses the ball's horizontal direction.

I'm checking the case where the paddle is two cells behind after a sticky repeat: the paddle moves right toward the ball, but the lag stays at two until the ball reaches a wall. I'm estimating how many steps the ball needs to return to row 8 after bouncing off the bricks, and whether it would reach a wall before then.

I'm tracing the lag-2 case at the right wall: the paddle at column 6 with the ball at 8 moving right catches up one cell per step, reaching column 8 just as the ball bounces at column 9. At that point the paddle is one cell behind, and the next action has to reverse direction to keep pace.

I'm checking the lag after a wall bounce: if the ball turns at the wall, the paddle stays a cell behind until the wall-step closes the gap. With lag 2, the paddle catches up one cell per step as the ball sits at the edge, so the question is whether the ball comes back down before that happens.

I'm weighing Option C, landing prediction, against Option B, since tracking one cell ahead means a transition error at every paddle hit and wall bounce. Option C would have the paddle move to the expected landing spot and wait there, but that landing spot depends on where the bricks are on the way up, which makes it harder to compute. I'm now checking whether the timing works: the paddle needs to cover the distance to the landing spot within the steps the ball takes to come back down to row 8.

I'm working out whether the paddle can catch up with the ball if it waits at the predicted landing spot: when the ball turns at the turnaround row r, the paddle has about 8 - r steps to close the gap, so one sticky error is tolerable but two would make it miss. I'm also considering pre-positioning during the ascent, using a guessed turnaround row to predict where the ball will land.

I'm weighing a fallback where the paddle tracks the ball's current x during the ascent, which keeps the distance at the turnaround within the 8 - r steps available. I'm also considering pre-positioning at a guessed landing spot. Next I'm sketching how a two-layer network could compare the target against the paddle position.

I'm now considering a direction-by-direction case split for the target position, since the horizontal component is linear in ball and trail but the full direction isn't, and the wall folding still has to be handled.

I'm now writing out the direction test for the target, which will use the ball's position alone once the direction is known.

I'm now checking the direction test for down-right: the apparent motion value dy+dx equals 2 only when the ball is truly moving down-right, so subtracting 2 gives zero for that case and a negative value otherwise. I can gate a threshold comparison on that, so the unit only fires when the direction is down-right and the target clears the paddle by the given amount.

I'm turning to the unit count: two gated threshold units per apparent direction should fit within the 32 available, so the "move right" test for each direction can be a single linear function of the ball one-hot and the paddle one-hot, gated by that direction.

I'm now working out the direction test for each case: combining the per-direction gated units into one indicator for moving right, then handling the bounce cases and the target table for each direction.

I'm working out how the target table handles the bounce cases, since the apparent direction can be off when the paddle or a wall changes the ball's horizontal or vertical step. The two cases I've checked so far are down-right, which is unambiguous, and down-left, which is next.

I'm handling the vertical-bounce cases now: a ball moving up at row 0 turns downward, and one at the paddle row turns upward with its horizontal step set by the paddle case. Rows 1 to 7 are harder, since the trail sits on the same row and doesn't reveal whether the ball came from below or above, so I'm considering whether the brick layout can settle it.

I'm working out the bounce cases for vertical motion: a ball at row 0 that has stopped moving vertically was heading up and now turns down, while rows 2 to 4 could mean a brick strike from below. Rows 1 to 7 are ambiguous, since the trail can't show whether the ball came from above or below the brick row.

I'm sorting out the bounce cases by row: a ball at row 4 or 3 that stopped moving vertically must have struck a brick from below and is now heading down, and at row 1 it must have come from above and is heading up. Rows 0 and 2 are the trouble spots, since a brick above or below could explain the same stalled motion there.

I'm checking the top-wall case at row 0: a ball that arrived there moving up bounces and turns down, but a brick hit from above leaves it at row 0 moving up after a bounce, so the stalled vertical motion alone can't tell these apart.

I'm checking the row 0 case: the ball's next move depends on whether there's a brick at (1, x+dx), and if there isn't, the direction state decides whether it drops to row 1 or bounces off the top and moves down one step later.

I'm checking the side-wall cases now: a horizontal-only apparent move means the ball hit a side wall, so its true horizontal step flips toward the interior (right at column 0, left at column 9), while the vertical step stays as it was.

I'm now checking the zero-zero case: a ball at a side wall that also hits the top, a brick, or the paddle shows no apparent motion, so its true horizontal step points inward (right at column 0, left at column 9), and its vertical direction depends on the row.

I'm working out how to read the true horizontal direction: when the apparent horizontal step is nonzero it's used directly, except after a paddle bounce where it gets flipped, and when it's zero the side wall decides it, so x=0 means moving right and x=9 means moving left. Next I'm tying the vertical direction to the same kind of reading.

Still working out the ball's true vertical direction when its apparent vertical step is zero: at row 8 it must be heading up after the paddle, at rows 3 and 4 it is heading down after a brick strike from below, and at row 1 it is heading up. Rows 0 and 2 stay ambiguous, since a top-wall bounce or a brick hit from either side could explain the stalled motion there.

I'm sorting the ball's motion into four diagonal classes, plus a fifth for purely horizontal moves where a vertical bounce happened, split by whether the row is the paddle row, the top wall, or a brick row.

I'm sorting the ball's motion into classes by its apparent step, splitting the purely horizontal moves by row, and working out the paddle-bounce case where the true horizontal direction is flipped.

I'm now checking how the paddle's position relative to the ball changes the true horizontal direction, since that changes the target. Two separate units for the two paddle cases would avoid making the target depend on the paddle position in a nonlinear way.

I'm checking whether the ball sits on row 8 by testing the row value, since it can never reach row 9 without the episode ending, so that condition can be written as an inequality that is tight only at row 8.

I'm now checking whether the paddle sits at the ball's column, since that decides whether the horizontal step gets flipped, and I'm looking for a way to express "paddle at ball_x" with one-sided linear gating terms.

I'm now treating the ball's next position as a linear function of its current and trail coordinates, since a wall-free step gives x + dx times the remaining rows. That would let the landing target come out of a single linear expression rather than a pile of separate gated cases.

I'm now seeing that the landing cell is the ball's position plus its step times the remaining rows, which is x + dx*(8 - y). Writing dx as x minus the trail column turns this into x(9 - y) - x_t(8 - y), and with the trail row tied to the ball row, it splits into one term that depends only on the ball cell and one that depends only on the trail cell.

I'm now setting each class's target as a function of the ball cell and the trail cell, so the landing position splits into a ball-only term and a trail-only term. For every class I'd use two units, one checking the target lies above the paddle and one below, both gated so they only fire when that class is active.

I'm writing the gate terms for the remaining direction classes, with the same linear form as the diagonal ones, and I'm hitting the horizontal-right case, where I need dy_a to be exactly zero and a two-sided condition can't be written as one linear inequality.

I'm checking whether the ball is at row 8 and the trail is at row 8 together, since those two conditions can be written as one-sided linear terms, but checking whether the ball and trail share a row in general can't be done that way.

I'm now considering a grouped approach: rather than one class per row, I could cover the horizontal moves at rows 1 through 4 together, since a downward landing from any of those rows can be written with the same expression. That would cut the unit count from 24 down to something manageable.

I'm trying to make the brick-bounce case reuse the DR table, so I'm adjusting the DR gate so it also fires when the horizontal step is +1 and the vertical step is zero at rows 3 and 4, and I'm working out what term that adjustment needs.

I'm going through the possible trail positions for a true DR ball: a normal diagonal step from the upper-left, a brick or top-wall bounce that leaves the trail directly to the left, and a left-wall bounce where the trail sits straight above at column 0, plus the stationary corner case.

I'm weighing a gate built from a lookup table on the ball cell plus one on the trail cell, which could stay separable if the trail row is tied to the ball row. For the DR class, that means the gate should be zero for normal diagonal motion and also for the brick or wall cases where only the horizontal step is present, but the zero-step cases at the left wall make the expression harder to write cleanly.

I'm now looking at a leaner option: getting the true direction from layer 1 and computing the target in layer 2, though that would force the ball position through layer 1 as a bottleneck. Instead I'm thinking of gating on the trail-relative position, so the gate is separable as a function of the ball cell plus a function of the trail cell, and the DR class should be active for every trail position consistent with a down-right move from the current ball cell.

I'm trying to pin down which trail positions are consistent with a down-right move for the ball at each cell, since that decides the gate. A linear split of the form a·y + b·x on each side could make the DR gate zero for the normal diagonal case, but the brick-bounce and wall cases still need to be handled. I'm considering whether simply adding more units would be cleaner than forcing everything into one separable gate.

I'm now weighing a two-stage design: first layer 1 picks out the true direction and compares the candidate landing cell with the paddle, then layer 2 combines those units with AND logic.

I'm now counting the layer-1 units: two comparison units per direction, eight in total. The direction indicators are harder, because each true direction may need several units for the different trail patterns, and layer 2 would have to OR them together.

Now I'm laying out the layer-2 AND unit that combines the direction indicators with the comparison term, and checking that the thresholds keep it a clean AND when only one indicator fires. Then I'm setting up the plan with eight comparison units in layer 1, two per direction.

I'm now listing the direction-pattern detectors for the DR class: the normal diagonal move, a horizontal right step at rows 0, 3, and 4 (where it can mean a downward bounce), a downward step at the left wall, and the stationary corner case.

I'm listing the layer-1 pattern detectors for the UR class: the normal up-right move, horizontal moves at row 8 from a paddle bounce, horizontal moves near the top rows that mean a brick bounce from above, and the vertical up move at the left wall.

I'm going through the stationary corner cases at the left wall, specifically row 8 where a down-left move bounces to the right and then upward off the paddle, and I'm checking whether a similar case at row 1 also counts. That makes the pattern detectors for the up-left class mirror the right-hand ones. Breaking down the full set of patterns for each direction class is going to add a lot of layer-1 units, so I'm considering whether some of them can be merged.

I'm checking whether one separable function, a table on the ball cell plus a table on the trail cell, can pick out the true down-right pattern set: the main diagonal trail always, plus the left and above trail positions only at certain rows and the left wall.

I'm trying a separable gate where each side's term is a table over the ball cell and the trail cell. With unit coefficients on the row and column, the normal down-right step gives a sum of 2 plus the table values, and I need every other trail offset to fall below zero.

I'm testing how the patterns with a sum of 1, the trails directly to the left and directly below, could be kept while the diagonal-neighbor cases on the wrong side get excluded, and I'm noting that the stationary trail at sum 0 ties with the two cases I need to rule out.

I'm checking the wall-case trails now: at x = 0 the DL ball still reads as DL at this step, even though the clamp will flip its horizontal move on the next one.

I'm checking the trail cell for the DL case at the left wall, since a ball at (y, 0) moving down-left will be clamped and turned around on the next step. That means the target table for DL at x=0 already gives the correct landing column. The harder part is that a trail at (y-1, 1) and one at (y-1, 0) both sit next to a ball at the left wall, so a trail-only term may not separate them.

I'm checking which (ball, trail) pairs are actually possible, starting with the interior columns. There the ball can only have moved horizontally by one step, so the horizontal component of its motion is always ±1, and the trail offsets with zero horizontal shift can be ignored there.

I'm checking the left-wall case where the ball is at column 0 with a dx of -1 or 0, since a paddle bounce at row 8 could flip that sign. If the ball came from column 1 moving down-left and the paddle lands on column 0, the hit would make its true horizontal direction positive, so I need to verify that condition.

I'm working out the horizontal direction for each ball position: on the interior columns the true dx follows the trail offset, with the opposite sign at the walls. The paddle-bounce exception at row 8 still needs its own check before I settle the rule.

I'm trying to split the horizontal direction into a separable form, with one term for the ball's column and one for the trail's column. The rule is that dx is +1 when the trail sits to the left of the ball, or when both are at column 0. So I'll write G(ball) plus H(trail) and check the inequalities for the middle columns, where the trail is one step left or one step right.

I'm checking the edge cases now: at column 0 the gate needs a positive offset when the trail is at the same column, and at column 9 a negative one, so I'm setting a half-unit bias at each wall. Plugging in the four corner pairs, they all land on the correct side of zero.

I'm turning to the vertical direction now, and I'm considering the trail rows that can appear for a given ball: one row above, one row below, or the same row in a bounce case.

I'm now going through the vertical cases: the ball moving down when the trail sits one row above, moving up when it sits one row below, and the bounce cases on the same row. Whether a same-row trail means up or down depends on the row, with the top wall and brick bounces making rows 0 through 2 ambiguous.

I'm splitting the vertical direction into a separable gate too, with one term for the ball's row and one for the trail's row. A trail one row above means moving down and one row below means moving up, so the same-row cases at rows 0, 2, 3, and 4 need the sign biased one way and rows 1 and 8 the other.

Now I'm handling the paddle exception: when the paddle catches the ball at row 8, the horizontal direction flips, so I need to separate the two cases, where the paddle sits under the trail or under the ball, before the dx gate can be finalized.

I'm working through the paddle-bounce case at the wall: if the ball sits at column 0 on row 8 with the trail one column over and the paddle at 0, the horizontal direction flips to the right, so I need to fold that into the dx condition.

I'm checking the case where the ball sits at column 1 after moving down-right from column 0, which would show up as a trail at column 0.

I'm sorting out how the paddle exception fits into the horizontal rule: if the paddle sits under the ball's old cell, the ball reverses, and if it sits under the cell it moves into, that's the case where the direction flips to the other diagonal. Next I need a dx term that depends on the full cell, so the row-8 case can be included without breaking the separable form.

I'm working out the vertical case for paddle exceptions, where the test depends on whether the paddle sits under the trail or the ball. I'm testing combinations of trail and paddle positions relative to the ball to see which sign of the horizontal direction each one gives.

I'm testing which combinations of the paddle position and the trail's column relative to the ball give a +1 or -1 horizontal direction at row 8. Checking the pairs where the paddle sits on the trail or on the ball, I'm trying to find a quantity that separates the four cases, but so far it doesn't come out as a simple threshold.

I'm testing a combined rule for the row-8 paddle case, where dx depends on the ball, trail, and paddle positions together. A linear form b + t - 2p gives the right sign for all four combinations, so I'm going to check the remaining paddle-bounce cases with it.

I'm checking the row-8 paddle case against the wall: the rule dx = sign(b + t - 2p) gives zero when the ball, trail, and paddle all sit at column 0 or 9, so I'll add a half-unit edge bias there. Then I'll test the remaining wall neighbors to confirm the bias doesn't flip any of them.

I'm checking the row-8 paddle case with the combined rule b + t − 2p, plus a half-unit edge bias at the walls, and the sample cases at column 0 and column 1 all come out on the right side. The open question is whether one cell-dependent table can cover row 8 as well as the other rows, where dx is just b − t.

I'm fitting the paddle term into the same dx rule, and the trouble is that a -2p term would wreck the other rows. My thought is to scale the row-specific terms up so they dominate the paddle term on rows other than 8, and then check that row 8 still comes out right.

I'm checking whether the row-8 formula for the trail can coexist with the case where the ball is at row 7 moving up, since the same trail cell would then need a different weight. The trouble is that one trail term can't serve both contexts without a correction from the ball's row.

I'm checking whether a single trail coefficient can serve the row-8 paddle case and the row-7 upward case at once, and it can't, since one needs it positive and the other negative. So I'm going to split off a dedicated paddle-bounce unit for row 8.

I'm weighing whether a no-op at the row-8 bounce step is acceptable, since the ball needs at least nine steps to return and only the sticky-action delay is at stake. I'm also considering treating that observation as don't-care and leaving the target unset.

I'm working out what the paddle should do right after the catch at row 8: the ball heads back up, so the next landing is at least nine steps away, and its x depends on how high it climbs before turning.

I'm thinking about how the paddle should track the ball during its ascent: since the landing time depends on how high the ball climbs, the exact target can't be known at the bounce, but once the ball turns at row r and starts descending, the target is fixed at the folded column of u plus the remaining 8 − r steps. The paddle then has 8 − r + 1 actions to get there or into the catch window.

I'm checking where the paddle should stand for the catch: either exactly on the target column τ, or one step ahead of it in the direction of travel. If the paddle is coming from behind, it has to land on τ itself, but if it's already ahead, one step past τ is enough. The tracking during the climb gives me only one spare action, so a single sticky delay on the way down could cost the catch.

Turning the ball's path up toward the first brick it would hit along its diagonal would tell the paddle where the turnaround happens, but that depends on the brick map, so it can't be computed in one separable layer. Without it, the paddle can't predict the landing during the climb, so I'm weighing whether a reliable fixed target is possible at all.

I'm considering a rough approximation for the turnaround: assume the ball bounces off the bottom of the brick layer, so the landing can be estimated from the current row. I'd keep the paddle slightly ahead of the ball during the ascent, a few columns out, rather than trying to compute the exact target.

I'm sizing up how much slack a paddle that leads the ball by a few columns would have at the turnaround, since the landing is 8 − r steps away and the paddle only needs to cover that distance minus its lead. With a lead of 2 or 3, there are 3 to 4 spare steps, which would absorb a sticky-action delay. The catch is that a lead bigger than the remaining distance means the paddle has to back off again.

Keeping the paddle a few columns ahead of the ball would give extra slack, since it only has to cover the remaining distance minus its lead. The catch is that the paddle moves at the same speed as the ball, so it can't pull ahead on its own after a catch, and building up that lead is the hard part.

I'm tracing the ball's folded position as it moves toward the right wall: at x=7 with a lead of 3, the target lands on column 9, then the paddle chases a reflected target as the ball bounces back left.

I'm realizing the paddle can't build a lead during the descent: when the ball reverses off a wall, the paddle can only hold its spot and let the ball return to it, so the gap only opens if the paddle stays still at the right moment.

I'm asking what typical turnaround row r is likely, since the paddle's aim during the ascent depends on how far the ball will climb before it turns back down.

I'm working out where the turnaround row falls: bricks on rows 1 to 3, so the ball turns at row 4 while the row-3 bricks are intact, and moves to row 3 or higher as columns get cleared, or all the way to the top when a column is empty.

I'm testing whether a paddle aiming for a return at row 4 still has enough time if the ball actually turns at row 2 or row 0, since each mismatch shifts the landing column by a different amount.

I'm noting that once the ball starts its ascent, the target column stays fixed, because moving up one row shifts the unfolded position and the row offset in opposite directions. So the paddle can go to the spot and wait. If the turnaround row turns out different, the target only needs to shift by twice the row difference. I'm now asking what happens if the ball keeps going past row 3 where there is no brick.

I'm now considering the earliest possible turnaround: as the ball climbs past each row without hitting a brick, the minimum return row drops, so the paddle's target can be updated to match that row. If the ball is at row y and moving up, the soonest it could bounce is right there at row y, which puts the landing at a column I can compute from its current position.

I'm noticing that the target drifts by two columns for each row the ball climbs without hitting a brick, so the paddle can't keep up at speed one and will fall behind. If the ball eventually turns at some row, the paddle will be short of the true landing by however many steps it lagged during the climb.

I'm working out the paddle's target from the turnaround row, with the landing at row 8 given by the ball's unfolded position plus the steps left. If the paddle tracks the ball's folded column, the distance to the landing has to stay within the 9 − r actions still available.

The lead L is the problem: after the ball reverses off a wall, the paddle can't really pull ahead, since it moves at the same speed as the ball. So I'm asking what lead the paddle can actually hold during the climb. Whether a lead is even meaningful depends on how the ball's folded position and the paddle's position map onto each other over time.

I'm working out the timeline between catches: the ball climbs from row 8 to the turnaround row r, bounces, and descends back, which takes 2(8 − r) + 2 actions in total. At r = 4 that's 10 actions, and the ball covers about 9 columns in that span.

I'm recounting the timeline after the catch: the ball climbs from row 8 to row 4, bounces there off the row-3 brick, and descends back to row 8, which comes to ten observations and ten actions including the catch.

I'm checking the paddle's starting position against the landing: after the bounce the ball covers 17 − 2r steps to reach row 8, so the landing column is u0 + 17 − 2r, and the paddle needs about 18 − 2r actions to get there.

I'm checking the worst case, where the ball climbs all the way to the top: the paddle starts aiming for the row-4 landing, and if the ball passes row 4 without bouncing, the target shifts to the row-3 landing, and so on.

I'm checking how the paddle's target moves for a few starting columns, with the ball starting at column 0 and the target at column 9 for a turn at row 4. Then I'll see how quickly the paddle reaches each new target as the ball climbs past rows 3, 2, 1, and 0.

I'm checking the paddle's timing against the descent: the ball reaches row 2 and then row 1 while the paddle shifts toward the row-0 landing, and I'm working out how many actions remain before the catch at row 8.

I'm checking that the paddle can still make it: a target that moves two columns per row climbed is faster than the paddle's speed of one, but the paddle starts with enough spare actions to cover the shortfall.

I'm checking whether the folding causes the target to jump to the opposite side, so the paddle could end up moving the wrong way. With u0 = 5, the target starts at column 5, then shifts to 3 and then 1 as the ball climbs past rows 3 and 2, and I'm tracking where the paddle lands at each step.

I'm checking whether the paddle can still reach the final target: each row the ball climbs moves the target by up to two columns, faster than the paddle's single step, so I'm tracking how much slack remains when the ball turns at row r.

I'm estimating how far the paddle lags behind the target during the climb: about one column per step above row 4, plus whatever gap it has when the ball reaches row 4, which could be several columns if it started far away. I'm checking whether that lag still fits within the actions left if the ball bounces at row 4.

I'm checking whether the paddle can still catch the ball if it returns from a bounce at row 4, since it would be roughly five or six columns behind at that point. Approaching from behind means it has to reach the ball's column at row 8, while approaching from ahead lets it stop one column past, so I'm working out which case applies to the worst-case lag.

I'm checking the edge case where the ball starts at column 0 and the paddle has to sit at column 0 or 1 at the catch, since the trail position can't go below zero. That makes the worst-case slack zero, so I'm looking at the case where the paddle tracks the ball's folded column instead.

I'm checking the edge case where the paddle starts at b and the ball sits at column b+1 after the catch. In that setup the landing folds to 9 − b, which leaves the paddle with about one spare action if it starts at column 0.

I'm considering whether the paddle can always move in time, and settling on a heuristic: since the network can't easily tell where the ball might turn, I'd use the row the ball is at, or row 4 as a floor, as the turnaround estimate.

I'm settling on the turnaround estimate: the ball can only turn at row 4 or above, so for a ball at row y I'm taking the earliest possible turn as min(y, 4), and working out the landing column from that.

I'm settling on the earliest possible turnaround as the estimate, since a ball at row y can only turn at row y or above, and bricks sit no higher than row 3. So for rows 4 and below I take the turn at y itself, and for rows above 4 I assume a turn at row 4, which gives the paddle a safe target that never runs ahead of the ball.

I'm working out the timing at the turnaround: once the ball bounces at row r, the paddle has 9 − r actions until the catch, so its target is fold(u_r + 8 − r). I'm now checking what the target was just before the bounce, when the ball was still climbing.

I'm checking the target the paddle aims for just before a bounce: at the observation before the ball turns at row r, the earliest-turnaround estimate already gives the true landing column. If the ball keeps climbing instead, the estimate shifts to the next row up.

I'm checking that the paddle can keep up: the target is fixed during the descent from row 8 to row 4, then shifts by two columns for each row above that, so I'm testing whether the paddle has enough actions left to get there from the bounce point.

Now I'm checking the paddle's starting position against the target. It's either at the ball's folded column or one step behind it, depending on whether the catch was a direct reversal, so I'm measuring the folded gap between those two spots and the landing.

The worst case leaves no slack at all: the paddle needs every one of its ten actions, since a distance of up to ten columns only fits if the start and target sit at the two ends of the grid, which isn't possible without folding. So I can't count on any spare step for r = 4.

I'm checking the worst case for the paddle's slack: with the paddle at one wall and the landing at the other, the folded distance is at most 9, so the 10 available actions leave at least one spare step. I'm also looking at whether the catch window, which is a single column when the ball is arriving at the wall, adds any extra room.

I'm checking the worst case for the paddle's slack, where the start is at one wall and the target is at the other. The folded distance can be as large as 9, but sometimes it shrinks to 8 when the ball's starting column is one step in from the edge.

I'm checking how far the paddle's target lands from its current spot across the column range: a catch near a wall that the ball then moves away from produces the largest gap, so those positions need the most care. Keeping the paddle ahead of the ball when possible seems more robust, but it's tied to where the ball reaches the catch, so I'm considering whether the ascent target should also account for that.

I'm checking how the folded geometry affects the paddle's path, since if the ball turns at a lower row the target shifts further. I'm also looking at sticky actions: a single transition might cost one step, but once the paddle is moving steadily there should be no further delays, so at most one error is likely.

I'm checking the worst-case failure rate for the paddle: a few sticky-action errors would be needed in a tight spot, so it's probably around 1% or less. Rows below 4 move the target, which may force reversals and add risk. I'll stick with the earliest-turnaround target for simplicity, since it depends only on the ball's cell and direction, and I'm now looking at the ascent from row 8 to row 4 with folded geometry, where the target stays fixed at fold(u0 + 9).

I'm working out where the target lands for the higher rows: above row 4 it shifts by two columns per row, so at rows 3, 2, 1, and 0 it's fold(u0 + 11), fold(u0 + 13), fold(u0 + 15), and fold(u0 + 17). For a ball that reaches the top row, the bounce adds one more step before it descends, so the target there is fold(u + 9), counting from the arrival position.

I'm checking the row-0 case now: a ball that has just come off the top wall and is moving down may hit a brick at row 1 and rebound upward, so it can keep rattling along the top row and break through before it finally descends.

I'm still weighing the row-0 case: if the ball is heading down after the top bounce, its landing is u + 8, but if it's about to bounce off the top again, it's u + 9. Either estimate works since there's plenty of time up there, and any one-column mistake gets fixed later. Next I'll check how the ball descends through the cleared columns in rows 1 to 3.

I'm working out the ball's target for the descent: if it's moving down, it reaches row 8 after 8 − y steps unless a brick above stops it, so I'm setting the target to fold(u + 8 − y) and will revise it if a brick gets hit.

I'm checking the target for the upward climb: above row 4 it's fold(u + y + 1), and at or below row 4 it's fold(u + 9 − y). Mapping the ball's column back to its folded position depends on the direction it's traveling, so I'm keeping both cases.

I'm checking the catch window now: the paddle can sit at the ball's landing column or one step ahead of it, so if it's ahead, moving back toward the landing column is still inside the window, and even two steps out it can reach the edge of that window in time.

I'm weighing whether the paddle should stop at the ball's landing column or the one beside it, since both count as a catch. If it's already in that two-column window, it can stay put, and if it has drifted a step past, it should move back toward the window. I'm also checking that this doesn't misfire under sticky actions, because repeating a previous move could carry the paddle out of the window.

I'm weighing whether to aim the paddle at the near edge of the catch window or its center. If it approaches from behind and reaches the first window cell, a repeated move still keeps it inside the window, so stopping there is safe under sticky actions.

I'm settling on a catch target that is a window rather than a single cell: if the paddle is already in the two-column window, it stays put, and otherwise it moves toward the window. With sticky actions, overshooting by one column still lands inside the window, so this is the safer choice. I'm also noting that the window target only makes sense for the landing at row 8.

I'm working out the catch window near the right wall: when the window's two cells would be fold(u + 8 − y) and fold(u + 9 − y), the target can collapse to the single cell 9, and an overshoot there is clamped, so it's safe. If the ball arrives moving left, the window becomes {9, 8} instead.

I'm turning the window into a concrete rule: the paddle should go right if it's left of the low edge, left if it's right of the high edge, and stay put if it's anywhere inside, with the same treatment for ascent estimates as for the final landing.

I'm now sorting the four true-direction classes, each needing its own pair of comparison units for the lower and upper edges of the catch window. That's eight comparison units, and layer two will AND each one with its direction class to produce the output.

I'm now writing the layer-2 AND units, one per direction class for each of the right and left outputs, and combining them with an OR so that only the active class contributes.

I'm now splitting the horizontal direction into two cases: a general formula for most positions, and a separate one for when the ball and its trail are both on row 8. A detector will pick between them, and the output will combine that choice with the four direction classes.

I'm now splitting the bounce at row 8 out as its own pair of classes, since the ball moves straight up there and only the horizontal direction varies. The row-8 targets look like the ones for the upward classes, so those tables might be shared.

I'm settling the row-8 bounce case: the UR comparison units can be reused there, and only the gating changes, so at row 8 the direction membership should come from the bounce-specific dx formula rather than the general one.

I'm writing the horizontal direction as a sign test on the ball and trail columns plus an edge bias, with the paddle term only mattering in the row-8 bounce case, where I need to subtract twice the paddle column.

I'm trying a different route for the row-8 bounce: instead of folding the paddle into the trail term, I'd compute the dx sign from the paddle's position against the ball's column, since at the bounce the paddle either sits on the ball's column or on the trail's, and dx flips depending on which.

I'm checking whether a signed form like 2b − t − p gives the right sign in both cases, since it would avoid the separate row-8 formula.

I'm checking whether case 2 can be avoided by accepting a wrong dx at the row-8 bounce, but one wrong step costs up to two steps of slack, which is too much. Before deciding, I'm going to estimate how often case 2 actually comes up under the window policy.

I'm now setting up a separate unit to flag the row-8 bounce state, where the ball and its trail are both on row 8, so the direction can be computed differently there.

Writing the layer-1 units for the paddle-dependent dx test...

I'm splitting the UR and UL classes into two layer-2 units each, one for the normal case gated by not-bounce with the general dx, and one for the bounce case gated by bounce with the bounce-specific dx. Each of these is a plain AND of ±1 units, so it stays linearly separable. Now I'm writing the DR_R and DR_L layer-2 units as ANDs of the general dx, dy+, and the right/left target detectors.

Now I'm listing the remaining layer-2 units: DL and UR/UL for each side, then the bounce units gated by Z, which makes twelve in total and lets the output take the sum over the six right-side ones.

I'm checking that the dy unit gives "up" under Z, since ball and trail are both on row 8 and the class gating stays consistent. Then I'm tallying the layer-1 units so far: four for Z, dxA, dxB and dy, plus eight comparison units, which leaves plenty of the 32 available. Next I'll revisit the comparison tables for each class's window.

I'm now checking the edge cases for the DR and DL windows, starting with balls near the top wall at row 0 after a bounce, since the comparison tables have to hold there too.

I'm settling the window thresholds now, picking a margin K so the comparison units saturate cleanly. A value of K around 10 keeps the separation between the lower and upper edges well away from the decision boundary, and the pre-activations stay small enough that nothing overflows.

Writing the dxA weights for the ball and trail channels so the sign of b − t comes out right, with the edge columns 0 and 9 nudged by half a step.

Checking the row-8 bounce: the ball and trail are both on row 8, so the direction there has to come from the paddle-aware formula. I'm also re-examining a case where the plain dx sign looks right but the true direction comes out opposite, starting with the brick-and-wall corner at the right edge.

Checking the top-wall bounce: at (0, 9) moving UR, the ball ends up at the same cell heading DL, and the row-0 dy test still reads down. Now the paddle-and-wall corner at row 8: the ball at (8, 9) heading DR has both its column and trail on 9, so the bounce flag is set and the bounce-specific dx test applies.

I'm checking the case where the ball is moving down-left at row 8, column 9, where the paddle catches it and sends it up-left, then confirming the vertical flip from DL gives UL.

Checking the same-row case for the dy unit: if the ball and trail sit on the same row, the vertical direction depends on which row it is. Rows 0, 2, 3 and 4 give a downward move, while rows 1 and 8 give an upward one. Now I'm working through the remaining rows to see whether any same-row case can occur there.

Checking the same-row case for the vertical direction: it only arises after a top-wall, brick, or paddle bounce, and rows 5 through 7 can't produce one, so that term is free there. Next I'm checking the starting position, where the ball at row 3 with its trail on the same row gives a downward vertical move and a rightward horizontal one, and I'm moving on to the row-2 case where a brick could be involved.

I'm weighing which row-2 case is more common: a ball rising through a gap and bouncing off a brick at row 1, or one falling from the top and hitting a brick at row 3. The first is the usual early-game pattern, while the second shows up later once rows have been cleared and the ball starts getting above row 3.

I'm weighing the row-2 case for the dy unit: if the ball is moving down there, the landing target is u + 6, but treating it as moving up would put the target one step off. Either error is small, so I'm going with "down" for row 2.

I'm working out the row-0 and row-1 cases for the vertical direction: on row 0 I'll treat the same-row case as downward, accepting a one-step error if the ball is actually heading up. On row 1 the ball must be moving up, since there's no brick above it to bounce from below.

I'm working out the top-wall case for the vertical direction: a ball at row 1 moving up can't bounce off a brick at row 0, so it reaches the top wall first and only turns around there, which shifts the landing estimate by a step.

I'm working out the landing time for a ball moving up from row y, which depends on the row where it turns around: for rows 5 and up it turns at row 4, for rows 2 through 4 it turns where it is, and for rows 0 and 1 it has to reach the top wall first.

Working out the landing time for a ball moving up depends on its starting row: from rows 5 through 8 the ball turns at row 4 and lands at about u + 9 regardless, while from rows 2 through 4 it turns where it is, which pushes the landing out to u + 11 and beyond. I'm now tracing the upper rows, where row 1 and row 0 both have to reach the top wall first.

Working out the landing time for a ball moving down: it's u + 8 − y, assuming no brick gets in the way from above. Then the catch window at row 8 is the pair of folded targets for u_L and u_L + 1, and I'm picking the lower bound from there.

Next I'm checking the paddle timing against the catch observation: the window applies to the paddle position after that step's action. If the paddle is left of the window it moves right, right of it moves left, and inside it stays put so the ball gets caught.

I'm going to check whether the earliest-return target is actually the best choice for the ascent, since a later return would shift the window. If the ball comes back later than the earliest estimate, the paddle simply has more time, so the question is how much slack the earliest-return strategy leaves in the worst case.

I'm checking how the paddle's slack changes if the ball goes higher than row 4, since each extra row shifts the landing target and the paddle has to keep up.

I'm checking that the earliest-return strategy never loses slack: each extra step adds two to the remaining time and moves the target by at most two, so the paddle stays on track.

I'm checking the slack in the worst case: after the catch, the paddle lands on one of two neighboring cells depending on whether the ball keeps its horizontal direction, and I'm working out how that affects the remaining distance.

I'm working out the two cases after the catch: if the paddle stays put, the ball keeps its horizontal direction and lands 9 columns further on, while if the paddle moves to the other window cell, the ball reverses and I have to recompute its starting point in the opposite unfolding. Now I'm looking at case 1, where the paddle sits one column behind the ball's new position.

Now I'm tabulating the folded distance from the paddle's position to the target window, looking at each value of the ball's position, starting with the case where the ball keeps its direction.

I'm checking whether the paddle can actually reach the window in the case where it stays one column behind the ball, since the folded distance could reach 10 if no folding happens between the two endpoints.

I'm checking the folded distance in case 1, where the paddle sits at the ball's previous column. Splitting the unfolded positions by where the wall bounce falls, the distance works out to |9 − 2a|, which reaches its maximum of 9 when the paddle starts at column 0 or column 9.

Checking the window for the catch, I find that with the ball at column 0 the paddle needs 8 moves to reach the window, leaving slack 2. The worst case is the paddle at column 9 with the ball moving left, where the window sits at column 0, a distance of 9 with 10 actions, so slack 1.

I'm checking how much the earliest-return strategy can fail: losing two steps would cost the slack-1 case, but that needs a second error, and with large logit margins the softmax noise is negligible. The real risk is transitions during the long traverse, since a target shift when the ball rises above row 4 could cause a direction change and a sticky step. Even so, the extra time from a later return should offset that, so the failure probability per catch in the worst geometry is small.

Now I'm weighing whether the paddle can be pushed to the wall-side window to improve the worst case, since a catch at the right wall with the ball moving right might be steered by choosing the reversing option.

If the ball goes right and bounces off the wall, the paddle at column 8 needs 7 steps to reach the landing spot, which is easy. Reversing the ball by having the paddle step to 9 instead sends it to column 0 at distance 9, so that option is clearly worse here.

I'm now comparing the two catch choices for the next landing: staying put keeps the ball's direction, while stepping onto the other window cell reverses it, and each leaves the paddle at a different distance from the following target.

Now I'm checking the case where the paddle stays put and the ball keeps moving right: the landing column comes out to 9 minus b, and the window sits at 8 minus b, so the paddle's distance depends on whether b is small or large.

Now I'm working through the case where the paddle stays put: the ball moves right, and I'm tabulating the landing distance for each starting column b, finding the slack is smallest (2) at b=0. For b=8 the next landing window sits at columns 0 and 1, a distance of 7. Next I'm turning to the reversed case, where the ball heads left after the catch and I need its unfolded starting point.

I'm working out the case where the paddle stays put and the ball reverses: for small starting columns b the paddle's distance to the window is 6 − 2b, falling to 0 at b = 3, and for larger b it grows again, reaching 7 at b = 7.

I'm comparing the two catch options for each landing column b, where case 1 keeps the paddle at b and case 2 moves it to the other window cell. Case 2 looks better at columns 0 through 3, while case 1 wins around column 4 and beyond. Column 9 is the exception, since both options collapse to the same target there.

I'm checking the ball's trajectory after the catch: if it lands at column 0 moving right, staying put sends it on a path back to the left wall, while stepping to the other window cell reverses it. I'm working out the next landing for the staying-put option before comparing the two.

Now I'm comparing the two catch options for the next landing: if the ball lands moving right with the paddle on the left, the reversing choice tends to shorten the trip back, and the distances work out to 6, 4, 2, 0, 0, 1, 3, 5, 7, 9 across the landing columns.

I'm weighing a single-cell target at the catch step instead of the whole window, since the case choice changes the next landing distance a lot. That would drop some of the sticky-paddle robustness, though, because a move that doesn't register would leave the paddle on the wrong cell.

I'm weighing a better approach: during the descent, target the preferred cell rather than the whole window, and only switch to the window at the final step. The risk is that an overshoot near that cell could land the paddle in the other window cell or outside the window entirely.

I'm going back and forth on whether to target the whole window during the descent or a single preferred cell, since a cell target helps the return but risks overshooting into the other window cell or out of the window entirely. I'm leaning toward keeping the window for simplicity and accepting a worst-case slack of 1, while wondering whether a different ascent target, centered rather than the earliest return, would do better once the bricks are in play.

I'm estimating how often a sticky action costs a step: each change in movement direction carries roughly a 10% chance of a one-step delay or overshoot. Since most catches leave at least two steps of slack, a single slip usually doesn't cause a miss, so the failure probability stays small.

I'm checking the failure odds for the slack-1 catches: one sticky delay at the start still lands the paddle just in time, so it would take a second delay to miss, and the ascent has no target changes that could cause one. That makes the chance of two delays well under 1%. I still need the row-8 bounce target to be computed correctly, including the Z gating.

I'm estimating the overall score next: with roughly 12 steps per catch and the 10,000-step cap, the ceiling is well above what we'd reach, so the cap isn't the limit. Recalling the MinAtar paper's Breakout numbers, DQN-style agents land somewhere around the high single digits to around twenty, so I'm treating that as the benchmark to compare against.

Now I'm weighing how the scores of known RL agents compare against what this hand-built policy might reach. Recalled figures for PPO on MinAtar Breakout vary a lot, so I won't lean on any one number. The policy should land well above them if the catches hold up. I also need to handle the case where the ball goes through a gap to the top row and bounces between the ceiling and the bricks, since the row-0 direction is ambiguous there.

I'm checking the row-0 case, where the ball rattles between the ceiling and the bricks. When it's on the top row moving down after a bounce and then hits a brick, it reverses up, and the trail shows the same row, so I'd read it as moving down and aim at fold(u + 8). If it's really moving up, the landing would be u + 9 instead.

I'm checking whether the ball's row-0 rattle stays manageable for the paddle. If the ball is moving down along the top row, the target sits one column ahead of where it was; the next observation corrects it, so the paddle shifts by one cell at a time. Since the ball needs eight or more steps to come back down, there's enough time for that small jitter, and the overlap between consecutive windows means the paddle often doesn't need to move at all.

I'm now checking the case where the ball drops from row 0 through the brick rows: if it hits a brick from above, it bounces back up, and a same-row trail at row 1 reads as moving up, which is fine, but at row 2 it reads as moving down, which is ambiguous. It might also get trapped bouncing between bricks, but the paddle has enough time for that.

I'm defining the policy as four lookup tables, one per direction class, keyed by the ball's row and column. For a downward ball the target is just the straight-line landing, and for an upward ball the return row adjusts depending on how high it is. The last window cell is still being worked out.

I'm checking the fold function and the target formulas for the descending and ascending cases, and confirming that the row-8 and row-0 entries line up with the window logic I've already set.

Now I'm working out the lookup tables for each of the four directions, one row at a time, which means a lot of entries to fill in.

Writing the weight entries for the comparison units now, one statement per row for the ball's lookup values.

Writing the weight matrix for the scale K = 5 now, and checking that the soft tanh values still keep the three-way AND clean.

Setting the comparison threshold at K = 10 means every pre-activation is at least 5 in magnitude, so tanh saturates cleanly and the binary signals stay crisp.

I'm settling on the comparison units' threshold: with K = 10, every pre-activation lands at least 5 in magnitude, so the tanh outputs saturate to essentially binary values. Now I'm turning to the direction detector for the bounce case, where the ball and trail both sit on row 8.

Writing the weight entries for the dxA and dxB direction units now, using the ball and trail columns with scaled coefficients.

I'm double-checking the edge cases at row 8: with the ball and trail both at column 0 and the paddle at 0, the direction comes out as up-right, and with both at column 9 and the paddle at 9, it comes out as up-left. I'm also working through the case where the ball moves from column 1 to column 0 with the paddle at 0, so the trail sits at column 1 and the direction stays consistent.

Checking the sign for the bounce case where the ball sits at column 1 with the trail at column 0 and the paddle at 0; the direction unit should still come out as up-right.

Checking the case where the ball sits at row 8 on column 0 and the trail is at column 1 from the previous step, I'm working through the left-edge clamp and the paddle position for that state.

Still writing the direction-detector weights for the bounce states...

Still writing the direction-detector weights...

Still working out the edge-case margins and the layer-2 AND units, starting with the direction-class detectors for the normal and bounce cases.

Still writing the layer-2 AND weights for the bounce-class units...

Still writing the layer-2 AND weights for the bounce-class units...

Checking the output layer now: with exactly one active class, its R-unit contributes about α to the right-side logit while the others net to zero, so the logit sums need a quick check.

Checking whether exactly one class can be active at a time, since the output logits only work out if that holds.

Checking that the inactive classes stay quiet: each one is held at about -1, so its contribution to the output logits is tiny, though I'm considering a larger weight scale for extra margin.

I'm now checking the actions: with the down, up, and fire actions effectively acting as no-ops, I'll push their output biases low so they're never picked.

Now I'm checking the remaining edge cases: the paddle moves before the ball each step, so the catch at row 8 is evaluated against the paddle's new position, and the window logic should hold whether the ball is descending from far away or already near the paddle.

I'm checking the strike-flag quirk next: on consecutive brick hits, the second hit doesn't bounce, so the ball passes into the brick cell and keeps its direction, and the strike stays set for the following step.

Checking the strike flag on back-to-back brick contact: a second hit in a row doesn't bounce, so the ball drifts into the next brick cell and keeps its direction. I'm working through the cases where the ball is already moving up after striking from below, and whether the diagonal cell is a brick or empty.

I'm checking how the strike flag lets the ball pass through consecutive brick cells without breaking them, and whether the apparent diagonal motion still matches the direction I've inferred. The bounce-free passage only delays the return, so the earliest-return target still holds.

Checking the ball's movement at the top: with the ball at row 0 moving up, I'm predicting a top bounce and then a descent, so the target is column 9. I'm also considering the case where the ball moving down hits a brick from above and bounces up at row 1 or 2, since a row-2 observation would read as downward and cause one step of wrong target before it corrects itself.

I'm checking the earliest-return target while the ball moves up past row 5, which assumes a brick sits at row 3 in the column the ball reaches. If that cell is empty, the target shifts, and the paddle will need to adjust.

I'm checking the paddle timing for the catch: after the bounce the ball sits at column 9 with a target window of column 0, so the paddle needs nine moves in the ten available steps. A single sticky noop would cost one step and still leave enough moves to land exactly on the catch. The target stays at column 0 through the ascent, so a bounce at row 4 shouldn't shift it.

Checking the edge case where the target shifts during the ascent: if the target moves from the far wall toward the other side, the paddle would have to reverse, so I'm looking at whether that can happen when the ball rises past row 4.

The descent target stays fixed unless a brick bounce changes it, and the earliest-return target already holds at the bounce observation. The only real risk is when the ball rises above row 4, since each extra row adds two steps and shifts the target, so I'll watch the paddle's slack through that stretch.

I'm working the initial-state case for a ball starting at the left edge of row 3: it moves down-right, so the target window lands on columns 5 and 6, and the paddle steps right to meet it before the ball reaches the catch row.

Working out the fold mapping for the target positions next, so I can write the lookup tables for each direction class and cell.

I'm double-checking the upward targets by row: from row 3 the turn happens at row 3, so T is 6; from row 2 it's 7; from row 1 it's 10; and from row 0 it's 9. For rows 4 and up, the target is simply one more than the row, since the bounce comes right off the brick at row 3.

Now I'm working out the window bounds for each target value: the low and high cells come from folding v and v+1, and they coincide at the wall points.

Now I'm tabulating the lookup windows for the down-right class, working through each row and its fold values.

Still tabulating the down-right windows, now for the row-1 entries, computing each fold window from v = x + 7.

Still tabulating the down-right windows, now filling in the row-3 entries from v = x + 5.

Still tabulating the down-right windows, now filling in the row-5 and row-6 entries from v = x + 3 and v = x + 2.

Now I'm filling in the down-left windows, starting from the mirrored offsets for each cell in the row.

Now I'm computing the down-left windows for row 0, using v = 27 - x and folding each value into the grid.

I'm mirroring the down-right windows to get the down-left ones, using the fold of each cell's reflected position. For the first cells the window comes out to {7, 8} at column 0, and I'm checking the column-7 entry next.

I'm mirroring the down-right windows to get the down-left ones: each cell's left-side window is the reflection of the right-side window at the mirrored column, so I'm checking the cells near the right wall to confirm the symmetry holds.

Filling in the up-right windows row by row, starting with row 0 where the target is v = x + 9.

Now I'm filling in the up-right windows for row 2, where the target is v = x + 7 and each cell folds to its window.

Still filling in the up-right windows, now for the row-4 entries.

Still filling in the window tables, now the up-right rows near the bottom of the grid.

Now I'm checking the up-right windows for the bottom rows, and the ball's path from (8, 1) after a bounce off the brick at row 3.

Now I'm tracing a sample path from (8, 1): the ball reaches row 4, bounces off the brick at row 3, and comes back down to column 9 at row 8 on the ninth step, so the target is 9 for that case.

I'm checking the upward targets for the up-right class at each row, confirming that a ball rising from row 1 takes ten steps to return and one from row 0 takes nine. I'm also noting that the up-left windows are just the mirror of the up-right ones, and that the down-going targets at row 0 only arise after a top bounce, so they hold at 8.

I'm checking whether the ball could be moving up while still on row 8, which would change the target for the bottom-row lookup. I'm also confirming that the bottom-row tables already cover the bounce case.

I'm checking whether row 8 can ever have the ball moving up with a trail on row 7, and concluding it can't: the only upward state there is the bottom-row bounce. Downward moves from row 8 follow the normal descent tables.

I'm checking the end of the mirror-symmetry case and the edge points where the trail meets the ball, then listing the layer-one units: a Z flag, the two direction-and-wall checks, the vertical check, and the two right and left descent entries.

Still writing the layer-2 unit definitions...

Writing the output-layer weights now: the logit for the right action sums the even-indexed v units with weight α/2 and a bias of 3α, so I'm setting those entries in W3 and b3.

Setting the output-layer bias and weights: the right-move logit gets the even-indexed v units at half the scale, and I'm picking α = 40 so the no-op logit sits at 20 and an active move at 40.

I'm checking that the policy never asks the paddle to move left at the wall, since the lower bound is never below zero. I'm also planning to sanity-check the rules by tracing a few cycles from the starting state.

Now I'm tracing a single episode by hand from the start state: the paddle moves right to column 5, and the ball travels down-right through the lookup windows without needing any paddle correction until it reaches row 8 at column 5, where the catch triggers an up-right bounce.

Now I'm checking the ball's next position after the bounce: it moves up to row 4 and turns to the left, so I'm tracking where it lands and what the paddle window looks like from there.

Checking the bounce from the ball at row 4 and the brick at row 3 to confirm the path leads to DL from (4, 8). Now I'm working out the DL window at row 4, column 8, by mirroring the DR entry at the reflected column.

Now I'm testing the wall case: a ball coming down-right to the last column at row 8, where the paddle's window collapses to a single cell at column 9.

Checking the catch case at (8, 0) as the ball comes down-left, and working out the window there.

Checking the ball's trail across the next few observations, I'm verifying the target stays at {0} as the ball moves up-left from (7, 8) through the mirrored window for row 7.

I'm checking the trail-following cases at each step, confirming the target stays at {0} as the ball moves down-left after the bounce, and the window keeps matching the mirrored up-right entries.

I'm checking the case where the brick at (3, 4) is gone, so the ball keeps going up-left to (3, 4). The mirrored window for that row shifts the target from {0} to {1, 2}.

Checking the paddle's position against the worst-case sticky-action scenario: if the first L is replaced by noop, the remaining nine left moves still land the paddle on the catch cell at t9, so the plan survives with no slack to spare. Any further delay would cause a miss, but since the action stays constant at L from t1 onward, a sticky repeat doesn't break it, leaving only negligible softmax noise as a real risk.

I'm checking the sticky-action delay chain: if the paddle is delayed at the first step, a second sticky repeat at the next step compounds it. So with slack s, the failure chance is about 0.1 to the power s+1, which is 1% for one spare step and 0.1% for two.

Checking the worst case again: the ball lands at (8, 9) and the paddle has to travel nine cells to reach the catch at (8, 0). Each sticky repeat costs a step, so slack of one gives about a 1% failure chance, and the average across episodes looks closer to 0.2 to 0.3%. That still suggests a few hundred catches per episode. I'm wondering whether a different choice at the wall could shorten that worst-case trip.

I'm comparing the two catch options at each landing column to see which leaves the paddle the least distance to travel. For a landing at column 8 moving right, case 1 leaves slack 3 while case 2 leaves only slack 1, so case 1 is the better choice there.

I'm comparing the two catch options for landings where the ball comes in from the left, and for small columns case 2 seems to give the shorter trip. For the window at column 0 moving right, case 2 leaves the paddle at column 1. Approaching from the left, the paddle settles on the lower edge of the window, which is the case-1 cell.

I'm weighing whether to change the targets so the paddle settles on the better cell. A single-cell target for the b = 8 case could help, since the worst case only bites when the ball lands at the far wall, but an overshoot would then have to be corrected.

I'm considering a narrower target of just cell 8 when the ball lands moving right, since a sticky move right at the wall gets clamped at 9 and the ball is still caught there. During the descent the paddle would then settle on 8, either by moving left from 9 or right from 7, with the overshoot risk to check.

I'm testing whether the window for b = 0 moving right can shrink to just cell 1, since the paddle at column 0 would otherwise need eight moves to reach the catch, leaving only two steps of slack.

I'm checking the case where the non-preferred cell sits on a wall: a sticky move there gets clamped, so the catch still works. The trouble starts when the non-preferred cell is interior, like with a ball at column 7 moving right and a window of {7, 8}. If the paddle is at 8 and a sticky right move sends it to 9, the catch fails.

Now I'm testing whether the target can be narrowed at the walls: for a ball landing at column 0 moving right, preferring cell 1 gives more slack, and for column 8 preferring cell 8 does the same, since a sticky move toward the wall just gets clamped there. The mirrored cases on the left side work the same way.

I'm re-deriving the corner case: the ball at (8, 0) moving down-left gets clamped to column 0 and flips to down-right, with the window collapsing to the single cell {0}. I'm tracing how it got there from (7, 0) via a wall bounce, and then checking the window at the catch.

Working out the slack for the landing at column 0: preferring case 2 (paddle at column 1) gives the ball a future landing at column 7 with slack 4, versus slack 2 for case 1. So the target can be narrowed to cell 1 there, since the non-preferred cell 0 sits on the wall and a sticky move gets clamped.

I'm looking at the corner landings now: when the ball reaches column 9 or column 0 on row 8, the window collapses to a single cell, leaving only one step of slack that I can't change. I'm wondering whether the ball's trajectory parity means these corner cases come around repeatedly in a cycle, which would add a fixed risk each time.

I'm checking the parity of the ball's path: each normal diagonal step keeps x + y the same parity, while a wall bounce or clamp flips it. So whether the ball lands on (8, 9) depends on how many bounces and clamps occur along the way.

I'm checking the corner landing at (8, 9) again: the window collapses to just cell 9, so there's no extra slack after the catch. I'll look at how the slack changes for each landing setup, focusing on where it drops to two or fewer.

I'm narrowing the descent target to a single cell at the wall-adjacent windows, with cell 8 preferred when the ball lands moving right at column 8, since that gives the paddle more slack.

I'm working out the special window cases near the walls: when the ball lands at column 8 moving right, case 1 leaves the paddle with more slack, so I'll narrow the target to just cell 8. I'm also considering the mirrored version on the left side.

I'm checking the mirror case for a ball at column 1 moving left: the window is {0, 1}, and preferring cell 1 gives the paddle more slack than preferring cell 0. I'm confirming that the window should shrink to just cell 1 there.

I'm checking the window for landings at column 0 moving right, where preferring cell 1 gives more slack. I'm also testing the mirror case at column 9 moving left, which should prefer cell 8 for the same reason, and I'm tracing the ball's path from (8, 9) to confirm the distances.

I'm working out the overrides for the final landing window: when the target window is {0,1} or {0,1} mirrored, I narrow it to the single cell 1, and for the wall-adjacent cases at windows {8,9} and {9,8} I narrow it to cell 8, since that leaves more slack before the catch.

I'm checking the paddle's safety at the catch step for the window that starts at 0: with the paddle at 0 and a target of {1}, every sticky outcome still ends at a catchable cell. The paddle at 2 is the problem, since a sticky right move pushes it to 3 and a noop leaves it at 2, so I need to compare that against the original window's requirement of moving left.

I'm working through the paddle's approach for the narrowed target windows. A paddle coming from the right toward cell 1 just keeps moving left and stops there, and even if a sticky move nudges it to 0, it still stays inside the {0, 1} range, so the catch holds. For the window at 8, I'm checking the same approach from the left.

I'm checking the window overrides against the wall-adjacent cases and confirming that the paddle stays inside the narrowed target. I'll apply the override in the window function so it covers both descent and ascent targets, and I'm about to test the case where the window is {1, 2}.

I'm checking the slack for the case where the ball is at column 7 moving right, with the window at {7, 8}. Preferring the paddle at 7 gives slack 5, while preferring 8 sends the ball toward a window near the left wall.

Two corner landings, at columns 9 and 0, leave only one cell of slack each, so I'm checking whether the diagonal path afterward can be steered to help.

I'm accepting that the corner landings at columns 0 and 9 leave only one cell of slack, since predicting the next landing would need knowledge of the bricks that I don't have. Steering the ball earlier would mean forecasting the path after each catch for both choices, which is too complex to build into this policy.

I'm estimating how often the corner landings come up, using the cycle analysis of the earliest-return trip, which spans nine columns from row 8 back to row 8. Whether the next landing shifts by ten columns or reverses depends on whether the catch is case 1 or case 2, and I'm checking how that maps through the fold.

I'm checking the mirror symmetry of the unfolding: shifting by ten columns sends each landing to its reflection, 9 minus the original, with the horizontal direction reversed. For the reversed case, I'm recomputing the starting unfolded position from the catch column.

I'm reworking the reversed-direction case, where the catch reverses the ball, and finding that the landing column then follows 7 minus the previous landing column modulo 20. Under the usual r = 4 trips, case 1 shifts the unfolded position by 10 while case 2 maps it to that reflected value, so I'm tracking how those two moves alternate the landings.

I'm working out the corner landing case: if the ball lands at column 9 moving right, the catch leaves it at (8, 9) heading up-left, which puts its unfolded position at 10.

I'm noticing that corner landings would repeat: from column 9 the ball returns to column 0, and from there back to 9, each with only one cell of slack. That would keep happening until the bricks along the diagonal path change, and I'm thinking through which bricks lie on that path.

Now I'm checking whether the corner-landing cycle breaks: once the brick at (3, 4) is gone, the ball's path changes and the row-3 bounce shifts the landing by two columns. I'm estimating the average failure rate per catch at roughly 0.3%, and wondering whether moving the ascent targets closer to the center would help, though the earliest-return target already looks fine.

I'm weighing whether the paddle can start moving earlier to cover the corner distance, but at the catch observation it has to stay put, so that won't work. Switching the catch action to R doesn't help either, since the next move still needs to be L.

Now I'm double-checking the earliest-return target against the strike pass-through quirk, since that could shift the paddle's timing near the wall.

I'm checking the dxA unit's sign at the wall cells, where the ball at column 0 gives a positive offset and the ball at column 9 gives a negative one, and confirming that the trail values still produce the right sign in every reachable configuration.

I'm checking the sign of dxA when the ball sits on the wall at column 0 with the trail at column 1: it should be negative, since the ball is moving left, and that still holds after a brick bounce. Once the ball clamps at the wall, the offset stays correct, so the dx unit is right for every non-Z state. Next I'm turning to the dy pre-activation.

I'm checking the corner-bounce cases at rows 2 through 4, where the ball hits both a wall and a brick. At (4, 9) moving up-right, the bounce sends it down-left with the same row, so the dy and dx signs still come out right. I'm now looking at the ball at (1, 9) moving down-right, which ricochets off the brick at (2, 9).

I'm checking the ball's direction at the corner cell (0, 0) after it has bounced off the wall and then the brick at (1, 0). Tracing the bounce, the ball should end up moving up-right, not down-right as I had written, so I'm marking that earlier note as wrong.

I'm checking the Z unit next, which depends on whether the ball is on row 8 with the trail also on row 8, and that case can only come from a paddle bounce. I'm also starting to look at dxB for every Z configuration, beginning with how the ball's clamped horizontal position follows from the trail column and its direction.

I'm checking the clamped case, where the ball bounces off the wall and stays on column t, so its offset comes out to e(t): -0.5 when t is 9 and +0.5 when t is 0, both giving the correct horizontal sign. Next I'm looking at the unclamped case with the paddle directly under the trail, where the offset becomes d + e(t + d).

I'm checking the case where the paddle sits under the trail, which gives dx = d + e(t+d), and confirming the sign holds for every reachable column. Then I'm looking at the other case, where the paddle sits under the ball and the offset flips to -d + e(b), and working through the values when b is 9.

Now I'm going through the window table for the comparison units, with overrides at w = 0 and w = 8 and the values for the rest following the same pattern.

Now I'm checking the window table for the comparison units: the entries for w = 10 and w = 18 take the overridden values, and the pattern of the remaining entries continues from there. I'm also reconsidering whether w = 0 can actually occur, since a ball at row 7, column 0 moving left would clamp to column 0 and bounce into row 8 heading right.

Now I'm filling in the DR class's window values, row by row, starting from row 0 where the overrides at w = 8 and w = 9 apply.

Filling in the DR window table for rows 0 and 1, I'm working out each column's lower and upper bounds, with the overrides at w = 8, 9, and 10 applied.

Now I'm filling in the lower and upper bounds for the DR window table across rows 2 and 3, with the overrides at w = 8, 10 and 9 applied as before.

Now I'm filling in the lower and upper bounds for row 5 of the DR window table, which has the same pattern of overrides, but I'm still working out how those values continue through the rest of the rows.

Still filling in the DR window table, now for rows 5 and 6.

Still filling in the DR window table, now for the lower and upper bounds of row 8.

I'm finishing the DR window table by checking the edge cases at row 8, where the ball at x = 0 gives target {1} and the ball at (7, 9) clamps into (8, 9), landing on {8}. Next I'll start on the DL class, which mirrors DR.

I'm checking the mirror symmetry for the DL table: the DL bounds should be the reflection of the DR bounds, with each window shifted by ten. Testing that at w = 0, the DR window (1,1) mirrors to (8,8), which matches the override at w = 10.

I'm now working out the DL window table by mirroring the DR values, since the left-moving class is the reflection of the right-moving one. Starting with row 0, I'm mapping each column to its window index and looking up the bounds, with the overrides at w = 0 and w = 19 still to be checked.

I'm checking the mirror symmetry for the DL table by reversing the DR rows: the lower bounds come out as 9 minus the DR upper bounds, and the upper bounds as 9 minus the DR lower bounds. For row 0 this gives lower bounds 7, 6, 5, 4, 3, 2, 1, 1, 0, 1 and upper bounds 8, 7, 6, 5, 4, 3, 2, 1, 0, 1, which match the direct calculation.

Still filling in the DL window table, now working through rows 1 and 2 with the mirrored bounds.

Still filling in the DL window table, now working through rows 3 and 4 with the mirrored bounds.

Now I'm writing out the DL table for row 5 and starting row 6, working through the window bounds with the mirrored offsets.

Still filling in the DL window table, working through rows 6 and 7 with the mirrored bounds.

I'm filling in the DL window table for rows 8 and 9's neighbors, checking that the end cases line up: the ball at (8, 9) moving left lands on {8} because of the override at w = 10, and the ball at (8, 0) gives {0}.

I'm now filling in the UR window table, starting with row 0 where the ball's offset is 9, so the windows run from 9 to 18 and each one's lower and upper bounds come from the paddle's reachable columns.

Filling in the UR window table for rows 1 and 2, working out each window's lower and upper bounds from the offset, and the windows for row 2 start at w = 7.

Still filling in the DL window table, now the bounds for rows 3 and 4.

Still filling in the UR window table, working through the rows of numbers for the lower and upper bounds.

Working through the UL window table now, starting with row 0 where the offset gives windows that wrap around the mod-20 boundary.

Checking the UL row 0 lower and upper bounds against the mirror of the UR row 0 values, and they agree at x = 0 and x = 1.

Now I'm working out the UL row 1 values with the offset of 10, where each window's bounds come from the mirrored UR entries.

Still computing the UL window table, now working through rows 2 and 3 for the lower and upper bounds.

Still working out the UL window table for rows 3 and 4, with the mirrored bounds.

Still filling in the UL window table, now working through rows 5 through 7 with their mirrored bounds.

Still working out the UL window table, now double-checking the row 8 bounce cases at x = 8 and x = 9.

Now I'm tracing the UL row 8 bounce by hand: from (8, 8) moving up-left, the ball bounces off the brick at (3, 3) and comes back down to land at (8, 0) heading down-right, which takes nine steps.

Now I'm checking the override at w = 0 in the ascent case: the ball reaches (8, 0) moving down-right, the paddle at 1 hits it, so it reverses up-left. From (8, 1) the next landing is at w = 7, which is (7, 8), and the paddle at 1 is six away, leaving slack of four.

Writing the comparison units' weights now: the left-class unit gets negative ball weights from the hi bounds, positive paddle weights scaled by x, and a bias of -0.5K.

Settling on K = 10 for the comparison and direction units, since the margins are clear and tanh saturates cleanly at that scale. Now I'm deciding the layer-2 weight, leaning toward 6 for the AND gates.

Now I'm settling the output weights: with each unit near ±1, the logits come out to 0 or 40, and the no-op bias is set to 20.

I'm checking that the comparison units stay exclusive, since the left and right checks can't both hold when lo ≤ hi, so the noop case is just when the paddle sits inside the window. That leaves the logits at noop 20 and R or L at 40 when active, with the other actions pushed down to -40. Now I'm turning to how MinAtar's sticky action wrapper replays the last action, since that affects whether the policy's output gets overridden.

Now I'm checking the top region, where the ball might pass through a brick cell; the channels are kept separate, so the paddle target doesn't change from that.

Checking the row 4 same-row case again: a brick from below sends the ball down, which is the only way it applies, and the brick-from-above case can't happen there since row 5 is empty.

I'm checking the same-row cases for the bounce rules: on row 0 the ball goes down after a top bounce, and on row 1 it goes up when there's a brick above, and rows 5 through 7 can't have same-row bounces at all. Since the ball moves at most one cell per axis each step, I don't need to worry about the trail reaching two cells away. I'm now going over where the ball sits at row 8.

Checking the catch step now: with the ball on row 8 moving down and the paddle already inside the window, I'll stay put, but sticky actions could still nudge the paddle off target if the policy had just been moving it. If the window is two cells, the extra step lands on the second cell and stays in range, but a single-cell window like {9} at a corner is tighter.

Now I'm checking the sticky-action risk at the catch step: if the paddle arrived at the edge of a two-cell window, a repeated move could carry it out of range, so I need to look at how it arrived.

Now I'm checking the sticky-action overshoot: once the paddle reaches its target, a repeated move can carry it past the window, and for the {8} override approached from the right, that sends it to 7 and then needs a correction chain, though each correction has its own 10% chance of slipping again. With enough steps it should settle back into the window.

I'm checking whether the {8} override could backfire: if the paddle is already at 9 and the ball lands at 8, the policy moves it left early, but a late move could let a sticky repeat carry it out of the window. The risk only shows up when the paddle is close to its target at the moment of the catch.

I'm weighing whether to keep the {8} override everywhere or only on the earlier stretch of the trajectory, since the paddle at 9 would trigger the left move and sticky repeats could carry it past the window near the catch. Using the original window during the final descent and the override earlier, when there's time to correct, would avoid that risk.

I'm weighing whether the {8} override should apply at every row or only earlier in the descent. If the paddle starts moving left from 9 while the ball is still high up, any sticky overshoot has time to be corrected. Near the catch, though, a late move could leave it outside the window, so the override is safer applied only up to about row 6.

I'm weighing whether the {8} override is worth its risk near the catch, since a paddle at 9 that's told to move left could overshoot out of the window on a sticky repeat. Keeping the override only for the earlier part of the descent, where there's time to correct, looks safer than applying it all the way down.

I'm weighing whether the {8} override is worth applying only on the wall side, since the override changes behavior only when the paddle is sitting at 9. Approaching 8 from 7 gives the same result either way, so the risk is limited to the paddle starting at 9.

I'm weighing the risk of the {8} override for the paddle sitting at 9: if it moves left to 8 early, a sticky overshoot to 7 can be corrected in time, but if the paddle is still at 9 near the catch, the override could leave it short of the window. Without the override it would just stay at 9, which is safer near the catch but gives less slack afterward.

I'm weighing the override at the turnaround: if the target becomes {8} at row r ≤ 4, the paddle at 9 has at least five steps to move left, so a sticky overshoot to 7 can be corrected before the catch.

I'm checking the sticky-action chain step by step: the paddle goes from 9 to 8 on the first move, and a repeated left can carry it to 7, after which a right brings it back toward 8 or a further left takes it to 6. I want to see whether it settles before the catch step.

The override's risk is about 0.1%, which beats the roughly 1% failure from leaving the paddle at 9. So the override stays, and at the catch step it's fine whether the paddle stays at 9 or moves to 8.

I'm now looking at the landing cases for each window and how far the paddle has to travel from its catch cell to the next target, starting with the rightward landings at w = 0 through 9.

I'm tabulating each landing column from w = 0 upward, checking what window the ball lands in and how many steps the paddle has to get back. For w = 0 the case-1 catch at column 0 sends the next landing to w = 10, which gives the window at 8 and a distance of 8, so two steps of slack; the case-2 catch at column 1 sends it to w = 7.

Working through the remaining landing cases now, checking for each rightward window which catch cell gives the next return the most slack. For w=1 the two catch options give slack 4 and 6, and for w=2 slack 6 and 8, so the case-2 catches keep looking better. At w=3 the case-2 catch at column 4 leaves zero distance, which is the tight one I need to watch.

Now I'm tabulating the remaining landings: for w=5 the catches give slack 1 and 3, for w=6 slack 3 and 5, and for w=7 the case-1 catch at 7 gives slack 5 against 3 for the override, so I'll compare the case-2 options at w=8 next.

I'm checking the corner landing at w = 9, where the ball stays at 9 moving left and the next return lands at w' = 19 with only one step of slack, which is the tightest case.

I'm checking whether the slack holds when the ball passes row 4 without bouncing. Shifting the target by two while also gaining two steps keeps the slack at least as large as before, though a paddle that has to reverse direction could still pick up sticky-action risk.

I'm checking whether the target reversal is costly: if the paddle has to switch direction toward a new target on the other side of a wall, a sticky repeat could cost it two steps of slack.

I'm checking whether reversing direction toward a new target costs extra slack, since a sticky repeat could send the paddle the wrong way for a step. I'm also wondering whether the paddle's noop while waiting could be swapped for something that lowers that sticky risk, though nothing obvious comes to mind.

I'm checking whether the target reversal is the only remaining issue here. Wait, I'm also going back over the policy at the catch observation, when the ball is coming down at row 8 and the paddle sits just outside the window, to confirm a single step lands it in the window.

Now I'm checking the ball's state right after a case-2 catch at the wall, where it sits at (8, 9) with its trail at (8, 8) and the paddle at 9, and computing the dxB value from those positions.

I'm checking the case-2 catch at row 8: the ball comes down from column 5 moving DL toward the window at (4, 5), and the paddle at 4 reverses it to UR. Plugging the ball and trail positions into the bounce formula gives dxB = 1, which is what I'd expect for that reflection.

I'm tracing the ball's path from (8,4) moving up-right: it passes through open cells, hits a brick at (3,9) and reverses, then I'm following the bounces down toward row 8 to check where it lands against the window at (5, 6).

I'm writing out the layer-1 weights now, starting with the unit for the ball's vertical motion and the units that track the paddle's direction.

Now I'm assigning weights for the zero-unit, which checks whether the ball is in row 8 and the trail is too, and the dxA unit that scales the ball's column position across rows 0 to 8.

Still writing the dxA weights for the ball and trail cells...

Writing the weight matrix by row-group now...

Still writing the dy weights for the ball and trail cells...

Still writing the dy weights...

Still writing the weights for the comparison units...

Still writing the weight matrix for the second layer...

Still writing the layer-2 weights for the four-way AND units...

Still writing the layer-2 weights for the BR units...

Still writing the layer-2 weights for the BL units...

Still writing the output weights for the layer-3 units...

Still writing the output weights for the four-way AND layer...

Checking the dxB unit's pre-activation in the non-Z states, where the sum could land near zero, and confirming the Breakout policy's bounce-case AND gates still hold under tanh's small-output range.

Still checking the edge cases: the ball's position against the comparison thresholds holds up, and the inactive AND gates stay well off their thresholds. Next I'm working through the scenario where the ball's class detection lands on the wrong case near row 0 or 2, but the effect is only a slightly off target, not a failure.

I'm now checking a case where the ball moves up from row 6 near the right wall, bouncing off the wall and then a brick, to see where it ends up and whether the landing window still holds.

I'm checking the top-region case now, where the ball rises through a gap to row 0, bounces off the ceiling, and then heads back down toward a brick.

I'm working out what happens when the ball descends through the brick rows from the top: if it clips a brick at row 3 coming down, it bounces back up toward row 2, and my rule for that case is still unsettled.

I'm checking what happens when the ball bounces back up off a brick in the top rows, since my target is wrong for a step until the next observation fixes it. I'm also weighing the scoring, since each brick hit is a point and the policy should do well. Last, I'm revisiting the sticky-action risk at the catch: if the paddle needs to move but the previous action was noop, it could stay put and miss.

Checking the paddle's sticky-action risk at the catch: if it has to move at the last step but the previous action was noop, it would stay put and miss. Arriving just in time carries about a 10% failure chance, but only when the previous action differs. If the paddle has been moving continuously in that direction, the sticky repeat is harmless, so the corner case comes out to roughly 1% failure from two delays at the start.

I'm estimating how often the paddle ends up landing at a corner, working through the early returns where each landing either shifts by 10 or reflects around 7. The first landing is at column 5, and the paddle moves into the window, which sends the ball back up at x = 4 moving left. I'm checking whether the paddle's position at that point matches the ball's column, which would count as a case-1 catch.

Checking the ball's path from (8, 6) moving up-right: it reaches the wall at column 9, reflects, and the next cells to check are around row 4 near the brick at row 3.

I'm tracing the ball's path after the catch at (8,4): moving up-left it passes the top wall, bounces back down to row 4, and breaks the brick at (3,1) on the way.

I'm tracing the ball onward: from (8,5) it heads back up-right, and the brick at (3,8) is now gone, so it continues up to (3,8) moving up-left. My target for that position is the window at columns 1 to 2, and I'm checking the next bounce off the brick row at (2,7).

I'm checking the landing table at (3,7) for the DL case, where the window is columns 1 to 2. Corner landings come up now and then, so I'm wondering whether the policy can steer away from them. The corner at w=9 traces back to a catch from w=19, or from w=18 after the fold, so I'm looking at whether the earlier steps can avoid it.

I'm checking the corner case through the override: at w = 18 the policy should prefer catching at x = 1, since the alternative reflection lands the ball on the corner at w = 9. Preferring case 1 there sends the ball to (8, 8) instead, which avoids the corner. I'm also noting that corner landings from the other returns shift by two each time, so the same idea may apply there.

The corner landing is still a problem for some returns: for r = 3 (k = 1), case 2 from w = 0 sends the ball straight into the corner at w = 9. So whether the override helps depends on r, and I can't know r at the catch.

I'm working out a parity rule for the catch: case 1 keeps the landing parity the same as w, while case 2 flips it, and since corners sit on odd columns, I can pick the case that leaves the next landing even and avoid corners entirely.

I'm working out the timing between catches: the unfolded coordinate advances by one each step regardless of bounces, so I need to count the steps from the catch up to row r, the bounce, and back down to row 8.

I'm noticing that each step between landings takes 18 minus twice the row count, which is always even, so a case-1 catch keeps the landing parity unchanged. Extra steps from brick bounces and ceiling rattles would change the count, so I need to check how those affect the parity before relying on it.

I'm counting the steps between landings: the catch step leaves the ball's row unchanged, the brick or top bounce does too, and the up-and-down legs cancel out, so the total comes to 18 minus twice the row count, which is always even.

I'm checking the parity argument against multiple vertical bounces: after the catch, an odd number of further bounces is needed to return to row 8 moving down, so the total count of bounce steps stays even and the landing parity still holds.

I'm checking whether the parity argument still holds when the ball takes the mirrored path in case 2, since the unfolding direction reverses there.

I'm working out a parity rule for the catch: if the landing column is even, I take case 1 so the next landing stays even, and if it's odd, I take case 2, which flips it back to even. Since corners only sit on odd columns, that keeps the ball off them from then on.

I'm checking whether the even regime holds by always picking case 1, which means catching at the ball's x for rightward motion and at the mirrored x for leftward motion. Even w then corresponds to either an even x moving right or an odd x moving left. I'll trust the u-parity argument for now, since it holds regardless of which way the ball is moving.

I'm settling on the opening move: the first landing at w = 5 is odd, so I take case 2 there, and after that I keep choosing case 1 so the parity stays even and the ball never lands on a corner. I still need to check how the w = 0 override interacts with this.

I'm now checking the case-1-only strategy from w = 0, where catching at x = 0 means the next window lands at x = 9 and the slack comes out to 1, which looks like a problem worth redoing the table for.

I'm now checking the even-w cases: the paddle at fold(w), with the next landing at w + 10, so the distance is |9 − 2·fold(w)|. That gives slack 1 when fold(w) is 0, and I need to see which positions actually hit x = 0 or 9.

I'm testing the alternative where the window covers both cells: from w = 0, choosing case 2 lands at x = 1 and flips parity to odd, which could bring a corner back in at r = 3. So the simple always-case-1 rule has a weak spot at the walls, where the distance to the next landing is 9 and leaves only one cell of slack.

I'm comparing the two catch options for the r = 4 case: case 1 puts the next landing at the mirror of the current paddle position, so the gap is about 9 minus twice the paddle column. Case 2 sends the ball reversed to a different spot, which I still need to map out.

I'm now weighing the distances under both catch options, since case 1 keeps the ball near center and case 2 works better for paddles nearer the left. The flight time depends on the row count r, which shifts where the next landing falls, so the rule has to account for r as well.

I'm checking the window targets with the parity rule in place: even w takes case 1, odd w takes case 2. For r = 4 with w = 0, case 1 lands the next catch at x = 9, which leaves only one cell of slack, so the wall cases need a closer look before I trust the rule there.

I'm tabulating the slack for each even w under the parity rule, and the wall positions x = 0 and x = 9 come out with only one cell of slack, while x = 4 and x = 5 sit close behind. Those cases are where the ball has the least room to recover if the window shifts by one.

I'm testing the wall cases with the parity rule: from the paddle at 0, the next landing at x = 9 is far away, so I'm checking whether the nearer window cell at 8 gives better slack, and weighing that against the parity preference for 9.

I'm estimating the failure rate from the slack values: each extra lost step costs about a 10% chance, so a slack of 1 means roughly a 1% failure chance and a slack of 2 about 0.1%. Slack-1 cases dominate, so the expected failures per catch come out near 0.06%.

I'm estimating the score from the step cap: at roughly 12 steps per catch, about 830 catches fit in 10,000 steps, so a low failure rate could put the policy in the several-hundred range. That would likely beat typical RL baselines on this game. I'm now going back to the slack-1 cases, specifically the corners at w = 9 and 19 for r = 4, and checking the remaining ones.

I'm concluding that the slack-1 and slack-2 cases only come up on r = 4 returns, since for r ≤ 3 the next window is at least 12 actions away and at most 9 cells, giving slack of 3 or more.

I'm checking the corner case: the slack there is only 1 when the next return is r = 4. Once the ball breaks the brick on that diagonal, any later corner trip has r ≤ 3, so the corner risk comes out to roughly 1% times the chance of a brick being present. I'm fairly confident in the policy overall, but I still want to verify that the target shift is handled correctly when the paddle is already waiting and the ball passes row 4.

I'm settling on the ascent target as the earliest return, since a later return only gives the paddle more time, so that choice is the safest. If the target shifts by two rows when the ball passes row 4, the extra distance is matched by the extra two steps, so the slack stays the same.

I'm checking the step cap next, which bounds the score, and then confirming the network's response at row 8 when the ball is coming down. At that point the trail sits on row 7, so the dy check gives a downward move, and I'm verifying the down-direction tables for both diagonals. I also want to see what happens if the paddle is already in the window but an override still tells it to move.

Checking the remaining positions now: with the ball at (8,8) moving right and the target at {8}, a left move puts the paddle on 8 for case 1, and a sticky noop still lands it on 9 for case 2. The ball at (8,0) and (8,9) work the same way, so every case is caught.

I'm checking the paddle's position for the w = 8 landing: if it has been waiting at 9 since earlier, the step toward 8 could overshoot on the sticky action and cause a miss at the catch.

I'm checking the paddle's timing for the w = 8 landing: if it overshoots to 9 on a sticky step, an extra L could carry it past 8 to 7 at the catch, so I'm looking at how the sticky chain could play out near the end of the descent.

I'm checking the risk when the paddle arrives at 8 from the left and the override pushes it past to 9. A correction L brings it back to 8, but a sticky L during the wait could drop it to 7, and a later sticky at the catch step would leave it short, so that chain is about 0.1% if the timing is tight.

I'm weighing that overshoot risk against the corner problem: if case 2 is used at w = 8, the ball returns to a corner window at w' = 19 with only one cell of slack when r = 4. Accepting about a 0.1% chance of a sticky miss to avoid that is the better trade.

I'm now settling on which case to prefer at w = 18: catching at x = 1 sends the ball back into a window at 8 with a wide margin, while catching at x = 0 leads to a corner at w = 9. So the target there is {1}. I'm leaving w = 0 for later, since its choice depends on the same corner trade-off.

I'm comparing the two catch options for the w = 10 landing: catching at 8 sends the ball back to a window near 2 with a slack of about 4, while catching at 9 lands it at x = 0 heading right, which is the corner trade-off I'm still weighing.

I'm checking which overrides avoid corner landings at w' = 9 or 19: case 2 at w = 18 or 8 would lead there, so those overrides keep the ball out of the corners. For r = 3, the case-1 landing at w = 17 is the next one to examine.

I'm now looking at the r = 3 case: corners show up when case 1 catches at w = 7 or 17, and when case 2 catches at w = 0 or 10. Those r = 3 corners carry more slack, so I'm checking what happens on the return after a corner catch, which only gets tight if that return is r = 4.

I'm double-checking the earliest-return target and the wall handling for the top region, though I think the design holds. I'm also noting that the Z state, where the ball and its trail both sit on row 8, still needs a look to confirm it's covered.

Now I'm writing out the lookup tables for the comparison units, converting each class's lo and hi lists into weights for the R and L sides.

Writing the lookup tables for the DR comparison unit, row by row, with the lo and hi lists...

Writing the DR lookup table row by row now, filling in the lo and hi lists for each row.

Writing the DR table row by row, filling in the lo and hi lists for each position.

Still writing the DR lookup rows...

Still writing the DR lookup rows...

Still filling in the DR lookup rows...

Still filling in the DR lookup rows...

Still working out the mirrored DL lookup values from the DR table...

Still filling in the mirrored DL lookup rows...

Still working out the mirrored DL lookup values from the DR table...

Still filling in the mirrored DL lookup rows...

Still filling in the mirrored DL lookup rows...

Still filling in the UR lookup rows...

Still filling in the UR lookup rows...

Still working out the UR lookup values for the remaining rows...

Still filling in the UR lookup rows...

Still filling in the UR rows, and the paddle lookups for the last two rows mirror the earlier ones.

Still working out the mirrored UL lookup values, checking each row against the UR table.

Still computing the mirrored UL lookup values, row by row.

Still working out the mirrored UL lookup values, row by row.

Still working out the mirrored UL weights for the remaining rows.

Still settling the comparison units: with K = 10, the pre-activation works out to 10*lo − 10*p − 5, so a full match at lo = 9 and paddle at 0 gives 85.

Checking the ball's row transitions now: at row 0 after the top bounce it heads down with a DR/DL lookup at T = 8, and from row 1 moving down it uses DR at T = 7. Coming up from row 2 at row 1, the dy term comes out to -15, so it uses the UR class at T = 10. I'm also confirming the ball never reaches row 9 in a non-terminal state, so that case is clear.

Checking the first ball case for the Z unit: the ball is not on row 3 in a way that triggers it. For the dx term, 5 minus 0 gives a positive move, and the dy term gives 5 so the ball heads down. The DR lookup at row 3, column 0 has lo 5 and hi 6, so the right-side pre-activation is 5, which is above zero and fires R, while the left side comes out at -25 and stays off. That makes the action R.

Writing the weight entries for the Z unit now: the ball and trail on row 8 each get weight 10, with a bias of -15.

Still writing the weight index ranges for the distance channels...

Now I'm laying out the weights for the dx unit, starting with the ball's contribution on each row.

Still writing the weight entries for the dx and dy units, and the second-layer weights are starting now.

Still writing the second-layer weights for the comparison units.

Still filling in the second-layer weights for the units that fire on the right and left comparisons.

