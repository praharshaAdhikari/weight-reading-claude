I'm weighing a simple policy where the paddle just tracks the ball's x position, since it moves one step per turn and the ball travels diagonally. I'm also considering whether predicting the landing point would do better, and I'm starting to think about the catch condition when the ball reaches row 9.

I'm checking the catch condition: the paddle moves before the ball, so it only needs to sit at the ball's old or new column when the ball reaches row 9. If the paddle tracks the ball's current x, it keeps pace since both move one column per step, and wall bounces just hold the ball in place for a step. I'm now working through the starting positions to see whether a simple "move toward ball x" rule is enough, or whether the case where they're already aligned needs special handling.

I'm working out the lag: if the paddle trails the ball by one column, it can still catch on the landing step by moving toward the ball. A lag of two might not be enough, though, so I'm considering aiming at the ball's next position instead, using the difference from its previous x to infer its direction.

I'm planning to give the network a hidden unit that compares the ball's column with the paddle's, so the sign of the difference tells it which way to move. The ball and paddle positions would be summed from their input channels, with thresholds set at half a column so the two sides separate cleanly.

I'm considering a refinement where the target is the ball's predicted next column, estimated from its current and previous x positions. I'm also checking whether plain tracking holds up: with equal speeds and a lag of at most one column, the paddle should still catch the ball on landing.

I'm checking how the gap between paddle and ball changes over time: since both move one column per step, the gap can't grow while chasing, and it only closes when the ball bounces off a wall. Starting from the paddle at 4 and the ball at x=0 moving right, the paddle is closing the gap by two each step.

I'm checking the step-by-step gap again, and I'm getting ready to add a margin to the logits so the policy stays deterministic despite softmax noise and sticky actions. I'm also considering whether aiming at the ball's next column, estimated from its trail, would give the paddle more room for error.

I'm settling on a target of the ball's column plus its direction of travel, so the paddle stays a step ahead instead of lagging. If it's already in line with the ball, it moves in the ball's direction, and that keeps the catch even if a sticky action delays it.

I'm considering a refinement where the paddle's target is the ball's column plus its direction, so the paddle stays a step ahead. That gives a few more catchable starting positions than plain tracking, and at the wall the target clips to the edge, which still works out.

I'm checking the edge cases: at a wall the target just clips to the edge, and after a brick hit only the vertical direction flips, so the horizontal trail still holds. When the ball resets, I'd set the trail equal to the ball's position with no direction. Computing the target as 2·bx − trail_x is the part I'm still working through.

I'm now setting up the network's linear sum as 2·ball_x − trail_x − paddle_x, so the sign of that value gives the direction. Two hidden units, one with the threshold at +0.5 and one at −0.5, turn that sum into right and left signals. Scaling those signals into the output logits should make the policy nearly deterministic.

I'm settling the weights: the right and left signals get scaled to about ±10 so the softmax is nearly deterministic, and the other actions are pushed far negative. When the sum is zero, both signals come out negative, so the policy falls back to doing nothing.

I'm checking whether chasing the ball's target still holds when it ascends, and I think the x-direction prediction works fine there. The gap between paddle and ball can't grow while the paddle chases, so a simple follow rule should keep up, though the wall bounces need a closer look since the target jumps there.

I'm checking the wall case again: the target jumps from 9 to 7 when the ball sits at 8 after reflecting, so the paddle ends up lagging by two. Since the target is one column behind the ball, a lag of two from the target is still only one from the ball, so the catch holds, just with no margin. I still need to confirm that clamping at the wall keeps the target at 9 when the ball sits on the edge.

I'm noting that at the wall, when the ball sits at column 9 with its previous column also 9, it must have been clipped from a right-wall bounce and is now moving left, so the paddle could already shift toward 8. Starting at the left wall with trail 0, the ball must be moving right. Either way, the wall cases only change the prediction, not the overall tracking plan.

I'm working out how the paddle's target should handle the wall case. When the ball sits in the rightmost column, the trail has the same value, so the target clamps and the paddle stays put. I'm considering a separate correction for that edge, since a single linear weight on the ball and trail columns can't express it cleanly.

I'm making the ball weights non-uniform, with the column-9 and column-0 entries shifted by one, so the linear sum lands exactly on the ball's next column at both walls. Then I'll check how the gap between paddle and target behaves over time.

I'm checking the gap dynamics: the target moves by at most one column per step, and the paddle closes on it, so the distance can only shrink or hold steady. Since the paddle has to land on the ball's column, it's enough to make sure the gap is at most one when the ball reaches the bottom.

I'm working through the start conditions: the ball begins at column 0 with the paddle at 4, so the gap is 3, and the paddle closes on the target by two each step until the ball reaches the bottom row.

Writing the weight assignments for the network now...

Still writing the weight assignments for the network...

Still writing the weight indices for the ball, trail, and paddle channels...

I'm verifying the indexing formula for the ball's channel in each cell, which works out to row times 60 plus column times 6 plus 3.

