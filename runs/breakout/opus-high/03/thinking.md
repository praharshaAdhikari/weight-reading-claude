I'm working out a hand-built policy for Breakout: the simplest idea is to have the paddle move toward the ball's column, or the column where the ball will land. I'm checking whether that works, since the ball and paddle each move one cell per step, so a paddle directly under the ball should keep pace as the ball moves diagonally.

I'm checking the catch rule: the paddle has to be in the ball's column or one step from it when the ball reaches row 9, since it moves before the ball does. Tracking the ball's x gives a two-cell catching window, but the paddle lags one cell behind whenever the ball changes direction, which could make the catch miss.

Rather than fixing the paddle on the ball's current column, I'd have it aim for where the ball will be next: the ball's x plus its horizontal direction, clamped at the walls. That keeps the paddle in place to catch it at row 9, and a lag of one cell is still fine as long as the paddle moves that step. If the paddle falls further behind, though, it can't recover in time, so the real risk is the paddle starting far from the ball.

I'm checking how the paddle stays ahead of the ball's horizontal drift: the ball takes about five steps from row 3 to row 8, and since the paddle moves at the same speed, it can stay aligned once it matches the ball's x. Wall bounces make the ball's x follow a triangle-wave pattern over time, so tracking its trajectory should work as long as the paddle isn't starting far away.

Now I'm checking the ball's horizontal movement against the paddle's position, since the paddle should land in the right column at row 9. The ball reverses horizontally when it hits a wall or the paddle, so I'm tracing how its direction flips on each kind of bounce.

I'm checking whether the paddle can hold a lead on the ball's next column, so a lag of one cell still gets caught at row 9 if the paddle moves that step. The real exposure is the paddle's starting distance, since the ball's horizontal speed matches the paddle's and it can't close a gap faster than one cell per step.

I'm working out the steady state: if the paddle already sits under the ball, matching the ball's next column just means moving one step in the ball's direction each time. That leaves the paddle aligned for the final step, and on row 9 the catch works either if the paddle has moved onto the ball's new column or if it stays put under the ball's current one, since both trigger a bounce.

I'm seeing that the lead-tracking target is more forgiving: if the paddle is already at the ball's next column before the final step, either a bounce from the ball's column or from the paddle's new column still catches it. Still, the ball also bounces off bricks and walls along the way, so I need to consider how those change its path.

I'm checking the wall case: when the ball sits at x=9 and bounces back, it stays in place for one step, so the paddle's target clamps to 9 and it simply holds. The ball's apparent direction then reads as zero, and the paddle will lag one cell when the ball starts moving left again.

I'm checking what happens to the lag when the ball hits a wall: the paddle stays one cell behind, moving the same way the ball does. Once the ball reaches the wall and stops for a step, the paddle can catch up, so a lag of one only persists until the next wall.

I'm now handling the edge cases: at a wall with zero horizontal change, the ball's real direction is the one pointing away from the wall. After a brick hit or a paddle hit, the vertical change can be zero, so I can't rely on it, but the horizontal change still tells me which way the ball is moving.

I'm checking the case where the ball bounces off the paddle and moves sideways into the new column, which makes the trail's horizontal change point the wrong way for the next step. Since the ball is heading up toward the bricks and back down, there's enough time to correct, but if the paddle follows the misleading direction once, it could end up two cells off.

I'm tracing the paddle's position after the ball's up-left bounce: it moves right to x+2 while the ball heads back left to x, which leaves the paddle two cells ahead and then a fixed gap behind as the ball changes course. I'm noting that the gap only closes when the ball reaches a wall, where it stays put for one step and the paddle can catch up.

I'm checking the case where the ball moves left after a paddle bounce: the trail's horizontal change points the wrong way, so if the paddle follows it, the paddle can end up two cells behind and miss the catch at row 9. I need to get the direction right in that case, and also consider how a brick hit with the strike flag already set might send the ball into a brick cell.

I'm now looking at the edge case where the ball bounces off the paddle at the bottom row, since the trail's horizontal change can mislead about its next direction. To tell whether it reversed or carried on, I'd check whether the paddle sits at the trail's column or at the ball's column.

I'm now working through the case where the ball bounces off the paddle while moving up, since the trail's horizontal change can point the wrong way. If the paddle sits at the ball's current column, the ball must have reversed, so its true direction is the opposite of the observed one. Since the ball spends a long time climbing toward the bricks and back, I'm weighing whether that slack is enough to ignore direction during the ascent.

I'm weighing a tracking policy against predicting where the ball will land, and tracking looks more practical given the brick bounces. If I set the paddle's target to the ball's position plus its true direction, it should stay aligned through steady motion, but I still need to check how it behaves when the ball reaches a wall.

I'm checking the wall case: if the ball is at column 9 and its horizontal change reads zero, its real direction has to be leftward, and at column 0 it has to be rightward. With that correction the paddle stays aligned through a wall bounce.

I'm checking the wall case again: at column 9 with no horizontal change, the ball must be heading left, so the paddle should target column 8 rather than holding still. A brick hit in the corner, where the ball meets a wall and a brick on the same step, still needs a closer look.

I'm checking the case where the ball bounces off a wall in the corner: it stays in place for a step, so it reads as no horizontal movement. I'm also noting that the paddle's position tells me whether the ball reversed or kept going. Then there's the brick strike flag: after one brick hit, a second brick in a row doesn't reflect the ball, so it passes straight into that brick cell.

I'm checking the starting state: with the ball at column 0 and no horizontal change, it must be heading right, so the paddle targets column 1, and the same reasoning puts the paddle at column 8 for a ball at column 9.

I'm checking the paddle-bounce case where the paddle moves right and the ball deflects up-left, so the trail's horizontal change is misleading. If the paddle ends at the ball's column, the ball must have reversed, so its true direction is the opposite of what I observed, and the paddle should move back left to match.

Checking the lag case: if the paddle sits one cell behind the ball's target on the final step, it has to move to catch up, and that only fails when the sticky action and the previous move disagree with the ball's direction.

I'm checking how the paddle behaves when the sticky action repeats a direction that no longer matches the ball. At the wall, if the paddle sits at 9 and the ball reverses to heading left, a repeated "right" action would leave the paddle in place while the ball drops to 8, so it falls one cell behind. The paddle generally keeps pace with a correct direction estimate, so this failure only shows up when the action changes.

I'm checking whether the lag stays stable or grows: a paddle one cell behind isn't losing ground on its own, it only gets worse once there are more misses. Wall bounces should help, since the ball holds its column for a step while the paddle catches up, and I'm testing that with a ball at 8 moving right and the paddle at 7.

I'm settling on a rule for the paddle: compute the direction D, set the target as the ball's column plus D, and move toward it. If the paddle is left of the target it moves right, if it's right of the target it moves left, and if it's already there it stays put. Walls should keep that rule working without any clamping.

I'm now turning the policy into a network: the target offset is linear in the one-hot ball and paddle positions, so the first layer can compute differences of column indices directly with tanh units.

I'm working through the special case where the ball and its trail share a column, which happens at the walls and at the start. There the direction can't come from the horizontal change, so the paddle's target needs a fix, and a plain linear formula gives the wrong offset at column 9 and column 0.

I'm checking the special case where the trail and ball share a column, since a uniform linear formula gives the wrong offset at the walls. Changing how the trail is weighted might fix the wall case, though at column 9 the off-by-one is harmless, since the paddle can't move past the edge anyway.

I'm checking whether the target can be clamped to the board's edges, which would handle the wall cases without special branches. At column 9 a ball arriving from the left should target 9 and a bounced ball should target 8, and the mirror holds at column 0.

I'm testing whether a single linear formula for the target can cover the wall cases, by checking the values for the ball in column 9 against each possible trail column. The cases where the ball sits on the trail's column need their own values, since a uniform formula only gets close there.

I'm checking the clamped target for the edge columns: at column 9 the ball should map to 8 when it's bouncing back, and I'm testing whether a weighted per-column formula can encode that without separate branches.

I'm checking the paddle-bounce case where the ball and trail share a row and the paddle sits right under the ball. There the true direction is the reverse of the trail's, so the linear formula points the wrong way, with the sign of the offset flipped.

I'm checking the paddle-bounce case at the right wall: a ball at column 9 that reflects off the paddle should come back with the paddle staying in place, so the target is 8 and the direction is reversed. I'm also testing a ball at column 8 moving right with the paddle moving to column 9, to see whether the new position gets clamped correctly.

Checking the edge where the paddle sits directly under the ball after a bounce: the trail says the ball is moving right, but the reversal means the true direction is left. The linear target would wrongly give a no-op there, so I'll need a dedicated detector for the case where the ball and paddle share a column in the bottom rows.

I'm looking at the row-8 case after a paddle bounce, where the ball and its trail share a row. If the paddle is directly under the ball, it was a reversal and the move should go back toward the trail. If the paddle is under the trail, the ball is continuing, so the move goes the same way as the ball.

I'm working through the row-8 case after a paddle bounce, where the paddle could be under the ball (a reversal) or under the trail (a continuation). The two cases want opposite moves, so a single target won't do. I'm wondering whether one linear combination of the ball, trail, and paddle columns can cover both.

I'm checking a single formula for the row-8 case after a paddle bounce: s = 2bx + tx - 3p. If the paddle is directly under the ball it gives tx - bx, which is the reversal, and if it's under the trail it gives 2(bx - tx), which is the continuation. Both match the true direction, so one linear combination covers both cases.

I'm adding a correction for the case where the ball and its trail share row 8 after a paddle bounce, since the paddle's column decides whether the move reverses or continues. That needs a gate that only fires in that row-8 case, and I'm checking the wall cases at column 9 separately, where the row-8 formula gives 0 when the true move is -1, though the sum works out to -1 when the trail is at 8.

I'm checking the row-8 reversal case at the right wall, where the ball and its trail both sit in column 9 after a paddle bounce. The trail's column gives the true move of -1, and the adjusted formula with f(9)=17 still produces -1 there. I'll do the same check at column 0, where the true target is 1 and the formula should match.

I'm checking the row-8 correction for the wall cases: with the ball and trail both at column 9 or column 0 the extra term vanishes, and for the reversal from column 8 the adjustment gives a left move of -2, which is the right direction.

I'm checking the paddle-bounce case at the left wall, where the ball is at column 0 with the trail at column 1 and the paddle also at column 0. The normal formula gives zero there, and the correction adds 2 for the right move, but I'm working out what the formula gives once the ball and paddle sit in column 1 and the trail is at column 0.

I'm checking whether the row-8 reversal case can be gated with a correction term: when the ball and its trail both sit in row 8, the paddle's column decides between reversal and continuation. I'm working out how to detect that gate in the network, since it has to fire only for that row-8 condition.

I'm settling on a gate for the row-8 reversal case: units that only switch on when the ball and its trail both sit in row 8. Then I'd saturate the normal threshold units with a large bias in that case, so the gated row-8 formula takes over the output.

I'm now thinking about how to lay out the network: first a layer of threshold units on the combined score s, then a second layer to turn those into a decision. The row-8 correction needs a gate that saturates differently in the two cases, so the downstream layer gets a fixed signal either way, and I still have to work out how to compensate for that.

I'm splitting the network into normal and row-8 units: the normal ones work from the usual formula, and a gate pushes them to a fixed value whenever the ball and its trail both sit in row 8. I'm working out how to bias each case so the second layer gets a consistent signal either way.

I'm adding a term that pushes the normal threshold units off when both the ball and its trail are in row 8, but a simple linear penalty on those two indicators can't separate "both" from "neither" without also shifting the neither case.

I'm going to use a second layer to do the gating: one unit flags whether the ball and its trail are both in row 8, and the normal and row-8 decisions get combined there.

I'm working through the gating with two output units: one picks the normal decision when the ball and trail are not both in row 8, and the other picks the row-8 decision when they are. Their signs combine into the right, left, and no-op logits.

I'm weighing whether this hand-built gating is even worth it, since a trained RL agent might score far better on Breakout than a hand-tuned network.

I'm wondering whether the ball could get stuck cycling between the paddle and the wall without ever reaching the bricks. My policy always puts the paddle under the next column, so the bounce reverses the ball in a fairly predictable way, which could lead to repeating trajectories, though sticky actions and sampling randomness might break those loops.

I'm checking the steady-state case at the final step: with the ball descending in row 8 and the paddle under it, a bounce reverses the ball, and if a sticky action keeps the paddle in place, it continues instead. Both outcomes look fine. I'm also noting that the trail and brick-strike cases don't need anything special.

Checking the brick cases near the edges: a ball moving up-right at (4,9) hits a brick at (3,9), and the vertical reflection sends it back down-left, so with the trail also in column 9 the horizontal move comes out as -1.

I'm checking the wall-adjacent cases against the f table: with the ball at column 9 and the trail at 8, f(9) minus 8 gives 9, and the other wall combinations also come out right.

I'm checking the starting state next, and then a special case: a ball at row 8 descending into column 9 from (7,8) with the paddle at 9. The steady-state formula gives a no-op, and the bounce sends the ball up-left while it stays at (8,9), so the row-8 case should give a left move.

I'm double-checking the row-8 formula against the wall and bounce cases, and the reversal at p = bx works out to tx - bx in the interior. I'm also confirming that the paddle can only be at the trail or the next column, since a bounce needs it in one of those two spots. Next I'm testing the case where the ball sits at (8,9) with the trail at (8,8) and the paddle at 9, to see whether that bounce sends it up-left.

I'm checking the row-8 bounce case where the paddle sits on the trail column, which gives a different trail offset, and I'm confirming that the state comes out to s = -2 after the bounce.

Writing the neural network weights now...

Writing the unit definitions for the gated network now...

Writing the output layer weights now...

I'm setting the bias logits for the up, down and fire outputs to a negative value, so the no-op choice carries most of the probability mass whenever the network doesn't want to move.

I'm setting the remaining output biases so the no-op case comes out right, and checking that the noop logit stays at zero while right and left go to roughly -8 when neither direction is wanted.

I'm checking the row-8 case for the final step: the gate G only fires when both the ball and its trail are in row 8, so when only one of them is there the normal formula applies. In the descending case with the trail still at row 7, and in the ascending case after a bounce with the trail at row 8, the normal decision still matches the true horizontal direction.

Now I'm checking whether the tracking strategy can get stuck bouncing in a loop without reaching the bricks, since the reversal bounce might retrace the same path.

I'm checking whether the ball could get stuck looping, since the ascending path from a reversal bounce lands on a different diagonal than the descending one, so it doesn't simply retrace. I'm also looking at parity: each normal diagonal step keeps the parity of row plus column, but wall clamps and brick bounces flip it.

Now I'm setting the ball-channel weights for the first hidden unit, scaling each column's value by the gain so the column-dependent signal comes through clearly.

Still setting the first hidden unit's weights by column...

Still setting the first hidden unit's weights, now for the remaining hidden units: the trail and paddle columns, plus the row-8 gate.

Writing the layer-2 weights now...

I'm checking the output layer's gate values for the right and left decisions, confirming that the saturated cases come out near -1 and the active ones near +1 with the expected margins.

Still setting the output weights and biases, checking that the right and left logits saturate to roughly 8 when active and the no-op case stays clearly dominant.

I'm sanity-checking a bounce cycle by hand: with the ball at (7,4) and the paddle at column 4, the steady-state value comes out to 1, so the policy should move right.

I'm tracing a sample sequence through the policy: the paddle moves right to column 6, and the ball bounces up-left at (8,6). Next the gated row-8 rule says to move left, and then the ball's state puts the paddle back under it at column 4, which checks out.

Now I'm writing up the design notes and applying the edits, leaving the unused units at zero.

