I'm going to hand-design a policy, starting with the simplest idea: move the paddle toward the ball's x position. A better version would predict where the ball will land and aim for that column instead.

I'm checking that the paddle keeps pace with the ball: if it starts level with the ball's column, it ends up one step behind, but it still catches the ball as long as it stays within that lag. Chasing the ball's current x works well enough, though it falls behind when the ball moves away from it, so predicting the landing column may be worth the extra complexity.

Now I'm working out the landing column for a descending ball, unfolding its x-position across the wall reflections over the steps remaining until the bottom row.

I'm checking whether the landing column can be computed from the ball's position and its previous position, since the direction is just the difference between them. The wall bounce complicates that, so I'm tracing what happens when the ball sits against the edge.

I'm checking the wall case: when the ball sits against an edge, its trail x matches its current x, so the direction has to be read from which way it points away from the wall. Brick hits work differently, since the vertical direction flips while the horizontal move still happens. I'm settling on a target column as the plan, and I'll work out how to express it with linear threshold features.

I'm weighing whether the target can be folded into a single linear quantity: if the target column minus the paddle position comes out as one input-linear term, the action is just the sign of that difference.

I'm checking whether the target can be a linear function of the input, and it can't, since the landing column depends on the ball and trail positions together. So I'm considering a simpler fallback: following the ball's x with a lead term based on its horizontal motion, and wondering how well that holds up once the ball bounces off the paddle and moves away.

I'm checking the catch condition more closely: if the paddle moves to the ball's current x each step, it ends up exactly under the ball after its move, and then the ball steps sideways to a neighboring column.

I'm tracing a concrete case by hand: the ball starts at the left wall heading down-right, and the paddle starts at column 4. I'm stepping through each move to see whether the paddle catches it, and so far the paddle keeps closing in on the ball's column, one step at a time.

I'm checking the case where the paddle ends up one step behind the ball: the ball keeps moving away, so the paddle can't close the gap unless the ball changes direction. A small sticky-action error can cause that, so I'm considering whether a lag of one column is still recoverable.

I'm weighing whether the paddle should aim for the ball's next column rather than its current one, since a one-column lag would be unrecoverable while the ball keeps moving away. Aiming at the next column leaves a margin of one step either way, so a sticky-action error could still be caught.

I'm checking the paddle-tracking case more carefully: if it always moves to the ball's current x, it stays level with the ball's column at every step, and the ball's x only changes by one or zero per step. That holds through the wall clamps and the brick and top-wall bounces. Without noise, the tracking is deterministic, so the only open question is how the softmax sampling and sticky actions disturb it.

I'm noting that the paddle's action at each step is just the direction the ball moved on its previous step, so with sticky actions a wrong move would repeat the last direction. I'll keep the logits far apart so the policy is nearly deterministic, since that limits how often a sampling error breaks the tracking.

I'm considering what happens if the paddle's sticky action pushes it the wrong way while the ball's x-velocity changes, like when the ball stalls at the wall. If the paddle ends up a step behind while the ball moves away, it can't close the gap until the ball reaches the wall and stalls there.

I'm weighing a lead-based target instead: aim the paddle at where the ball will be after its next move, which would also absorb a one-step sticky error. Working out the next position from the ball's current and previous x would mean handling walls and bricks separately, so I'm deciding whether the extra complexity is worth it.

I'm weighing whether to wait at the landing column rather than chase the ball, since sitting there early leaves room to correct a one-cell error. A sticky-action slip that pushes the paddle off by one could then be fixed before the ball arrives.

I'm working out how the ball's direction is read from its trail, but the trail breaks down after paddle and brick bounces and at the top wall, so those edge cases need their own handling.

I'm trying to make the policy's target a linear function of the inputs, which is hard because the landing column depends on the ball and trail positions together. One option is a separate group of hidden units for each direction, so the descending-right case gets its own linear feature.

I'm checking whether the direction can be read linearly: the difference between the trail's column and the ball's column gives the horizontal direction, and the same trick works for the vertical one. That makes the landing column a product of linear quantities, which I'll need to handle with one-hot inputs.

I'm looking for a way to turn the threshold comparisons into linear units: if I can write the ball's and trail's positions as linear sums, then a gated unit per direction could test whether the landing column passes each cutoff.

I'm working out how to keep the dx term from blowing up the threshold units: if I gate each direction with a large weight on the ball's horizontal offset, the descending-right case gets its own linear unit, and I'm checking whether dx stays bounded in {-1, 0, 1} so the other cases don't overflow.

I'm gating each threshold unit on the ball's horizontal direction, so the right-moving case gets its own linear unit while the other cases are pushed strongly negative.

I'm working through the wall cases next: at column 0 the ball should count as moving right, so I'm adding a bonus term there, and a ball arriving at the wall from the other side gets pushed off the gate.

I'm checking the wall case where the ball arrives at column 0 moving left: it stays put for one step and then reverses, so I'm treating that bounce as a reflection in the landing calculation. For the left-moving unit, a ball at column 0 with the trail at column 1 already gates the left branch on. The remaining case, a ball sitting at the wall while heading right, still needs its own landing formula.

I'm checking the vertical direction next: the ball is descending when its row is one more than the trail's row, and ascending when it's one less. After a paddle or brick bounce the trail row matches the ball's, so those cases need their own handling.

I'm now adding a gate on the vertical direction too, which means four direction cases times the landing thresholds, and that seems like too many units. For the descending case alone it's two directions times nine thresholds, so eighteen units. For an ascending ball the landing depends on brick bounces I can't predict, so I'm leaning toward just tracking the ball's current x during ascent.

I'm now checking the ascending case: rather than guessing where the ball will bounce, I'd track its current column while it climbs, then switch to the landing calculation once it turns downward. The paddle gets 8 minus the ball's row moves to reach the landing column, plus one extra move before the catch check.

I'm settling the landing target for the moment the ball reaches row 8: the paddle needs to cover either the ball's current column or the one it moves into next. I'm weighing whether to aim straight at the current column, which sends the ball straight back the way it came, or at the next column, which gives a diagonal bounce.

I'm checking whether the paddle has to land on the ball's column or the one next to it, since both catch it but bounce it in different directions. A straight hit sends the ball up and to the right, while a diagonal one sends it up and to the left. The remaining worry is whether the ball could bounce forever between the paddle and the top wall without ever reaching the bricks.

I'm checking the case where the ball is moving up rather than down, since the landing calculation only works once it turns toward the paddle. Bricks block most upward paths, but once some are cleared the ball could settle into a loop that misses them, so the sticky-action randomness is what might break it. For now I'm going to track the ball's current column whenever it isn't descending.

I'm settling the ascent case: I'll track the ball's current column while it climbs, since bricks make its later bounces impossible to predict. Once it starts descending, the landing calculation takes over, and I'm checking that the paddle has enough steps to cover the distance to the landing column.

I'm weighing whether tracking the ball's current column during ascent holds up, since a one-step paddle error can't be recovered once the ball turns down, while aiming at a predicted landing spot leaves a bit of slack. The open question is what target is best while the ball is still climbing, since the row where it turns is unknown.

I'm thinking a lead might help during ascent: aim a step or two ahead of the ball in its horizontal direction, since side walls flip that direction but bricks and the top wall don't. That would give the paddle extra slack once the ball turns down.

I'm weighing a lead target during the ascent: the paddle aims at the ball's current column shifted ahead by its horizontal direction, scaled by how far the ball might still climb before turning, so the paddle has extra slack once the ball comes back down.

I'm working out how the paddle should aim while the ball is still climbing: if I pick a guessed turning row, the target becomes the ball's column shifted by its horizontal direction times the remaining distance, though that gets awkward once the guess is passed.

I'm settling the ascent target by assuming the ball turns as soon as it can: the paddle aims at the column the ball would reach if it turned right now when it's below row 4, and at the column for a turn at row 4 when it's above. Since bricks only occupy rows 1 through 3, the ball can't turn any lower than row 4, so this guess never assumes a turn that's too late.

I'm checking the ascending target: assuming the ball turns at the earliest possible row, the paddle aims at the column for that turn, which is always at or ahead of where the ball can actually land. The descending target stays exact after the turn, and the formula is continuous at row 4, so the paddle won't overshoot.

I'm looking at the cases where the ball's vertical movement is zero, which happens on a paddle bounce. There the observed horizontal shift can't tell me whether the ball went straight up or diagonally, so I need another way to tell the two apart.

I'm now checking the row-8 case where dy is zero, which covers both a paddle bounce and a brick hit. For those, tracking the ball's current column is a reasonable fallback, though a brick hit may leave a large gap from the proper ascending target.

I'm treating a zero vertical move at row 8 as a paddle bounce, and for rows above that I'm weighing whether to assume the ball is descending, since a brick hit would make that wrong.

I'm checking the edge cases where the ball's vertical move is zero: at the left or right wall, the observed horizontal shift is clamped, so the direction is unclear, and I'm considering whether an arriving ball can sit on column 0 at all.

I'm handling the wall case for the effective horizontal step: when the ball's vertical move is zero, the observed shift is zero only at a side wall, so I'm checking which wall it's at to pick the right direction.

I'm working through the edge case where the ball's horizontal move is zero, which only happens at a side wall. I'm deciding the effective direction by checking whether the ball sits on column 0 or 9 together with the trail, and testing a weighted threshold to separate that case from a normal one-column move.

I'm now thinking about cutting the gated units down: the ascending target depends on the vertical offset as well as the horizontal direction, so separate units per direction and threshold would need 36 of them, more than the 32 I have. I'm looking for a way to drop the dependence on vertical movement.

I'm checking how the ascending target depends on the vertical offset, since the gated units can't cover both directions and both vertical cases without running out of slots. I'm trying to encode that dependence through the trail cell, which is fixed once the horizontal direction is gated.

I'm considering a unified formula that drops the dependence on vertical movement, since separate gated units for each direction and vertical case won't fit in the 32 slots I have.

I'm checking whether using 8 minus the ball's row as the lead works for the ascent: it still underestimates the true lead, so the paddle is never pushed too far, and the lead shrinks to zero at the bounce. The open question is whether the target can keep pace with the ball at one column per step while it climbs.

I'm noting that with m = 8 - y the target moves two columns per step while the ball climbs, so the paddle can't track it exactly. That's fine, though: the paddle only needs to keep moving in the right direction, and since this lead underestimates the true landing column, it won't overshoot.

I'm considering whether to use a uniform lead of 8 minus the ball's row for both ascent and descent, since that removes any dependence on the vertical direction and so needs no extra gated units. For the ascent it underestimates the true landing column, which keeps the paddle from overshooting, so I'm checking whether that holds well enough near the walls.

I'm now writing the target as a single expression: the paddle aims at the column the ball reaches after moving its effective horizontal direction times the distance to the bottom row. Since that distance alone sets the target, the vertical direction and trail drop out. The next step is to compare that target against the paddle's position to decide whether to move right, left, or stay.

I'm now folding the ball's horizontal and vertical offsets into a gated unit for each direction, since the target under each gate depends only on the ball's cell. Each of those units compares the target against the paddle's position, with a gate term that switches it on only for the matching direction.

Now I'm testing whether a gate can express "right-moving" without the extra 0.6 offset. Giving the column-0 indicator full weight makes the stay-at-column-0 case cancel out to zero, and the arrival cases come out right.

I'm settling on a signal scale of A = 4, since that gives a clean saturation near the threshold. The gate weight needs to be large enough that it overrides the maximum signal swing, so I'm setting it to 100 and checking that the off case falls well below zero.

I'm writing out four gated units, one per direction and per comparison, each comparing the target for that direction against the paddle position with a gate term that turns it on only for the matching ball movement. Then I'm checking that exactly one gate is always active, including the edge cases at the side walls, and confirming the starting state picks the right-moving gate.

I'm checking the edge case where the ball bounces off a brick at the wall column, and confirming the right gate still fires there. The two gates stay mutually exclusive. Next I'm working out how the output logits for right and left follow from the four units, and what values each unit takes for each comparison of the target against the paddle.

I'm checking the layer-two units now: the right logit should come from the two right-gated outputs, which is +1 when the right gate is active and -1 otherwise, so I'm using a tanh of their sum shifted by one.

Now I'm finishing the output layer: the right and left logits come from the two layer-two units, with the noop logit held at zero.

I'm checking whether the target stays sensible during the ascent, starting with a ball at column 2 moving left: the estimated landing drifts to 0 and then to 1 after the ball reaches the wall. Then I'm tracing the true path after it bounces back, to see how far the estimate lags.

I'm checking whether the paddle can keep up during the ascent. The worst case is a long horizontal drift after a bounce, so I'm testing whether the paddle can cover that distance in the time the ball takes to return, and whether the underestimated target still points it the right way.

I'm checking whether the paddle can keep up when the ball's path is folded back by the walls. If the target is underestimated it might lag, but since the paddle moves one step at a time and the folded landing point shifts at most about one cell per step, it should still have time to get there. The descending phase uses the exact target, so I'm treating the ascent as the only part where that's unclear.

I'm checking whether the paddle can stay ahead during the ascent, since the estimate is only an underestimate. Without walls, the target moves twice as fast as the ball, so the paddle keeps catching up, but the bounces and folding could make it lag.

I'm checking a worst case where the ball bounces off the right wall and its path folds back, to see whether the paddle can keep up. Tracing the targets as the ball climbs, they jump around the wall in ways that could leave the paddle on the wrong side, so I'm testing whether there is still enough slack to reach the landing point.

I'm weighing whether a hybrid targeting rule, one that only partly leads the ball during the ascent, would hold up better against small errors than tracking the ball exactly.

I'm settling on the lead version for the ascent: the paddle aims at the landing column computed with the remaining distance to the bottom row, so it stays ahead of the ball, and the target becomes exact once the ball turns. I'm also checking whether the folded target could pull the paddle past the eventual landing point, and the worked example suggests it still recovers in time.

I'm checking the ascent case where the ball keeps going up through the tunnel, where the lead estimate stays a slight underestimate. During the descent at the bottom row the target is just the ball's column, and one row above it's the folded landing column. I'm also flagging the diagonal bounce case, where the trailing position needs a separate check.

I'm checking the case where the ball bounces off the paddle with a diagonal move, and confirming that the target stays at the paddle's current position so it does nothing. Next I'm working out the target for each row, folding the landing column back by the distance to the bottom row.

I'm now defining the target function for the unit, where the target is the folded landing column for the ball's position, with values bounced back off the walls. Then I'm writing out the weights for the first right-direction unit: a ball channel term built from that target plus a wall-gate term, a trail channel term, and a paddle term that subtracts the paddle's column.

I'm writing the weights for the remaining two units: the first one for the left-moving case, where the ball channel gets the negated target and the paddle term flips sign, and the second for the left-gated output, which uses the left target and checks the edge cases at both walls.

Now I'm writing the last unit, the left-moving case: the ball channel takes the negated left target with the gate term, the trail term stays the same, and the paddle term adds the column instead of subtracting it.

Still writing weights... Now I'm laying out the ball, trail, and paddle entries for each unit, one row at a time.

Still writing weights... Now I'm settling on how to fill the ball channel for each unit in one sweep across the grid.

Still writing weights... Now I'm working out the values for the ball channel by computing each cell's target and gate term, since slice-based shortcuts are uncertain.

Still writing weights... Now I'm working out the target table for each row by folding the landing column back off the walls.

Still writing weights... Now I'm tabulating the target values for each row, working out the folded landing column for the descending and ascending cases.

Still writing weights... Now I'm tabulating the left-moving target values row by row, checking that they mirror the right-moving ones.

I'm checking the wall cases: the folded target at the left edge should be 0 when the ball is at x=0 on row 7, and the gate should still read it as moving left.

Still writing weights... Now I'm working out the target values for the right-moving unit across the grid, and deciding to fill the ball channel in row-wise blocks rather than one huge list.

Still writing weights... Now I'm working out the ball-channel values for the first unit by combining each cell's target with the column term, and then doing the same with the sign flipped for the second unit.

Still writing weights... Now I'm filling in the ball-channel values for the h2 and h3 units, using the left-moving targets with the column offsets.

Still writing weights... Now I'm filling in the h0 ball-channel values row by row, combining each cell's folded target with the column term.

Still writing weights... Now I'm filling in the h0 ball-channel values for the remaining rows, each one the base column term plus four times the folded right-moving target.

Still writing weights... Now I'm filling in the h1 ball-channel values for each row, negating the folded right-moving target and adding the column term.

Still writing weights... Now I'm filling in the h2 ball-channel values row by row, using the folded left-moving target scaled by four and the negated column offsets.

Still writing weights... Now I'm filling in the h2 ball-channel values for the next few rows, using the folded left-moving target scaled by four and the negated column offsets.

Still writing weights... Now I'm filling in the h2 ball-channel values for the lower rows, using the folded left-moving target scaled by four.

Still writing weights...

Still writing weights... Now I'm filling in the trail entries, which depend only on the column, so I'm setting them per column instead of per cell.

Still writing weights... Now I'm settling on setting the trail entries per column, one scalar fill for each column across the units.

Still writing weights... Now I'm working out the index ranges for the trail entries per column, and the ball and paddle rows they cover.

Still writing weights... Now I'm checking a sample cell by hand: the ball and trail values come out to 14 for the right-moving unit and -18 for the left-moving one, which match the expected outputs.

Still writing weights... Now I'm checking the layer-2 outputs: the right-moving unit sums the h0 and h2 terms with a bias of 3, and the left-moving unit uses h1 and h3.

Still writing weights... Now I'm checking the output weights and bias for the noop and fire actions, and confirming that the sticky-action detail doesn't need any extra handling.

Still writing weights... Now I'm tracing a ball that starts at (0,3) with the right-moving gate, checking that it reaches x=5 and bounces, and that the paddle ends up waiting at column 5.

