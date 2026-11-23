I'm setting up a hand-designed policy network for MinAtar Breakout and first working through the game dynamics. The ball moves diagonally each step, and when it reaches the paddle row I need to decide how it bounces depending on whether it hits the paddle's position.

I'm working out the bounce rules at the paddle row: if the ball's old x matches the paddle, it reflects straight back, and if only the new x matches, it reflects diagonally the other way. Otherwise the ball is lost. Next I'm considering how the paddle has to line up with the ball's position at row 8 before the next step.

I'm checking the paddle's alignment with the ball: tracking the ball's x each step means the paddle stays within reach, so it should catch the ball whenever it's moving toward the bottom row. I'm also noting that sticky actions will occasionally cause a miss, so the policy's logits need to be large to stay near-deterministic.

Now I'm tracing the ball and paddle step by step from the start. The ball drops from x=0 while the paddle at 4 slides left, and by step 4 they line up at x=3. I still need the paddle at 5 or 6 when the ball reaches row 9, and it's close enough to get there.

I'm weighing whether to aim the paddle at the ball's current x or the x it moves to next. Either way, if the paddle sits on one of those two columns when the ball reaches row 8, the catch succeeds, so I'm checking which placement tolerates a sticky action best.

I'm weighing the two placements: with the paddle on the ball's current column, a noop catches, and moving along the ball's direction also catches, while moving the other way misses. If the paddle already sits on the ball's next column, a noop catches, and moving back toward the current column catches too. Since sticky actions only repeat what the paddle was just doing, tracking the ball's x should stay robust at the critical step.

I'm checking the tracking strategy against the wall and brick cases: x changes by at most one per step, so a paddle that matches the ball's column stays aligned. I'm also noting that if the paddle always sits under the ball, the first bounce rule (straight vertical reflection) applies every time, so the ball's horizontal direction is preserved.

I'm considering whether the bouncing might cycle forever without hitting the remaining bricks, since the ball's horizontal motion repeats every 20 steps. I'm thinking about adding some stochasticity when the ball is far from the paddle, though the sticky actions already provide a little, and I'd rather keep the policy mostly deterministic with moderate logits.

I'm checking whether the bounce cycle can repeat forever. The horizontal motion repeats every 20 steps, and vertically the ball goes up to row 0, pauses there for a frame, comes back down to row 8, and pauses again, which makes a period of about 18. I'm considering whether adding noise is worth it, since it could disturb the catch at the critical step.

I'm now building the network by hand: I'll use two tanh units keyed to the difference between the ball's x and the paddle's x, with thresholds at plus and minus half a column, so the output is a clean sign with a dead zone at zero.

I'm setting the logits so the action only depends on the sign of the difference: a large positive logit for right when the ball is at least one column to the right, a large negative for left when it's at least one column left, and zero otherwise. The remaining actions are all effectively no-ops, so their bias doesn't matter much, but I need the right logit to be big enough to beat the zeros.

I'm setting the bias for the remaining actions to -20 so they stay out of the way, and I'm keeping the two hidden layers in place for the sign computation. Then I'm checking whether the ball's trail channel could help with targeting, but it only adds a second ball cell, so I'll stick with the ball channel alone and verify the start-from-zero case against the wall case.

I'm checking the lag cases now: the paddle might still be one column behind the ball, so the sticky repeat of the previous move decides the catch. Reversals in the ball's horizontal direction only happen at the walls or off the paddle, so they should be far from the critical step.

I'm checking the lag case: the paddle is usually one column behind, so the critical step needs a move in the ball's direction, and the sticky repeat of the previous move covers it. The only real risk is a direction change in the last step, where the repeated action could be the wrong one.

I'm checking the catch at the critical step: if the paddle is still lagging at column 7 while the ball is at column 8, moving right twice puts it under the ball, but then the ball bounces back and the paddle has to match column 8 again, so staying put at 9 would miss.

I'm considering a fix for the lag failure: instead of aiming at the ball's current column, the paddle could target where the ball will be next, estimated as roughly twice its current x minus its previous x, which should cover the wall-bounce and direction-change cases better.

I'm checking whether a paddle that anticipates the ball's wall bounce could avoid the failure case, since a plain linear tracking rule can't capture that. A lookup-style approach with the extra hidden units might handle it.

I'm estimating how often the lag case actually bites: roughly one catch in a hundred might fail, which still leaves a decent score. I'm considering a targeted fix for the wall case, where the ball sits in column 9 on row 7 and its next column is 8, so the paddle should aim one column left there instead.

I'm testing whether a trail-based correction at the wall case can avoid the miss, by giving the trail cell one row up and in the rightmost column a small negative weight so the paddle aims one column left there.

I'm testing whether a trail-based correction can fix the wall case: with the trail cell at row 6, column 9 given a small negative weight, the paddle aims one column left when the ball is in column 8 heading left-down. I'm checking a few trajectories, and the paddle catches the ball each time, including the sticky-repeat step.

I'm checking the case where the ball is at column 9 on row 7 with the trail at column 9 on row 6, which should make the paddle move one column left to 8. I'm also noting that the same idea could work mirrored at the left wall, by giving the trail cells in the left column a small positive weight.

I'm checking the case where the ball is at column 9 on row 8, with the trail at column 9 on row 7. Without any adjustment the paddle would stay at 9, and the catch works either way. I'm also considering the −1 trail weight, which would make the target 8 there instead.

I'm checking whether the trail-based fix covers the other cases. The stay-frame problem at row 7 is the only one that needs it. The same pattern at row 6 into the left-moving ball doesn't cause trouble, since the paddle is already moving left by then. So I'll apply the correction only to the trail cells at row 6 in the wall columns, column 9 and column 0. A ball going back up past those cells shifts the target by one for a moment, which is harmless.

I'm checking that the paddle at 9 moves left when the ball is at (8,7) with its trail at (9,6), since the target is 7. Then I'm looking at the other risks: after a paddle bounce the ball climbs to the brick row and comes back down well before the next catch, so the horizontal direction is unaffected there. The remaining case is a reversal off the paddle, where the ball's x flips and heads back toward its previous column.

I'm checking the softmax noise margin: with a scale of 20 the errors are around e^-20, so they're negligible. For the gains, I'm using weights of 6 per column unit so the first tanh saturates near ±0.995, and the second layer scales that again, with the logits set to ±20 and the other actions pinned at -20.

Still writing weight initialization for the ball-channel columns...

Still working out the left-wall case, where the ball at column 0 with its trail at column 0 should make the paddle aim one column right, mirroring the right-wall fix.

