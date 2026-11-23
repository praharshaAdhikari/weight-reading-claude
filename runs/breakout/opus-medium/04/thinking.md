I'm working out a paddle policy: the simplest version tracks the ball's column, and a better one predicts where the ball will land. Since the ball and paddle both move one column per step, following the ball's x position should mostly keep up as it descends.

I'm checking whether the paddle can actually catch the ball: if it aims at the ball's current column or its next one, the catch works out. Since both move one column per step, the gap stays the same unless the ball bounces off a wall, and the ball needs several steps to fall, so the paddle has time to close any distance.

Pure tracking might fall short if the ball drifts away from the paddle with a gap larger than one, though wall bounces can reverse that. Predicting the landing column from the ball's position, direction, and the wall reflections looks more reliable, even if it's more involved. I'm weighing whether the 32 first-layer units have room for that.

I'm working out how the paddle would land on the ball's column at row 8, accounting for the wall reflections that fold the ball's horizontal path back on itself. That means an unfolded coordinate that reflects at the edges, which is tidy to write down but awkward for a small network with 32 first-layer units to reproduce across the ascending phase too.

I'm checking whether tracking the ball's x position works when the ball and paddle move at the same speed. If the ball bounces off a wall, the gap can close, so the paddle can mirror the ball's horizontal motion as it rises and falls.

I'm now checking whether aiming at the ball's next column, x plus its direction, keeps the paddle within one step of a catch. I still need to work out how to get that direction from the last two ball positions, since at a wall it can read as zero.

I'm checking how the ball's horizontal direction flips on a paddle hit and at a wall, since a clipped wall step leaves its x unchanged and makes the difference read as zero.

I'm checking whether aiming at the ball's current column still works if the paddle lags by one step. If it's one column behind and the ball moves toward it, the paddle lands on the ball's column at the final step, so the catch holds. Sticky actions could throw that off, but even then the paddle tends to end up in the right column.

I'm now testing a target of x plus the ball's direction, the next column. If the paddle sits under the ball and moves right with it, it lands on the ball each step and the catch holds, and a no-op isn't a problem since a right move repeats anyway. The risk is a stale previous action when the direction changes at a wall.

I'm checking which cells are safe from the paddle's current spot: staying put or moving right both work when the paddle sits under the ball, so I'll aim at the ball's next column, clipped at the walls. The remaining question is how the network can infer the ball's horizontal direction from the recent positions.

I'm checking how the ball's horizontal direction can be inferred from its last two positions, since the difference reads as zero right at a wall. At the wall the ball stays in place for a step and then reverses, so the direction flips there instead of simply following the last move.

I'm checking whether the ball's horizontal direction can be read from its last two positions: when the difference is zero, the ball is at a wall and will move inward next. So aiming at the clipped next column should keep the paddle under the ball, and I'm weighing how a paddle bounce that reverses direction could throw that off.

I'm checking that the paddle stays in sync once it catches the ball: it mirrors the ball's x position and can keep up without losing it. I'm also considering whether the brick-strike rule, specifically how a strike flag interacts with a brick cell, could change that.

I'm now asking whether the strategy could loop forever without ever breaking a brick, since the paddle always lands on the ball's next column and that keeps reversing the ball's direction. The ball still rises toward the bricks on each pass, so as cleared bricks open up, it should reach higher rows and keep making progress.

I'm settling on the idea that sticky actions mostly don't matter, since the paddle usually repeats a right move, and the trouble comes only when the ball changes direction at a wall. I'm weighing whether a little softmax noise is enough to keep the paddle from settling into a loop.

I'm checking the case where the paddle reverses too late: it lags one column behind the ball, and the ball heads toward the wall. Moving left keeps the paddle within the allowed cells, and even a sticky leftover action still lands it on the ball's column, so a gap of one behind is fine as long as the policy keeps moving.

Gap of two behind would be the failure case, but sticky no-ops only open a gap when the paddle was already idle, and with the target set to move with the ball the paddle is almost always moving. Walls should resync it, since the ball stalls there for a step. Even so, I expect this policy to score well, though not perfectly, because random action noise can still break the cycle.

I'm setting up the paddle target as a linear function of the inputs: the ball's column doubled minus the trail column, minus the paddle column, which gives the gap between where the paddle should go and where it is. That should map cleanly onto the first-layer units, though the clipping at the walls still needs handling.

I'm testing a linear target, 2×ball column minus trail column, which should give the right next column except at the walls. The edge cases at columns 0 and 9 don't fit that formula, so I'm working out per-column weights for the ball and trail inputs that fix those cases.

I'm checking the edge columns: at column 0 the ball's weight needs a +1 correction, and at column 9 it needs +17 so the target clips correctly. With those, the linear target lands right everywhere, including the brick and paddle bounce cases.

I'm checking the starting position: the ball and its trail begin in the same column, so the target comes out one column to the right or left depending on the wall. Then I'm settling on the paddle action as the sign of the gap between the ball's next column and the paddle's current column, with no move when they match.

I'm setting the hidden units to compare the target column against the paddle, with a thresholded tanh pair that gives a positive signal for moving right and a negative one for moving left. A second layer then scales those into the right, left and no-op logits, so a one-column gap produces a clear move.

I'm setting the hidden units to measure the gap s = target minus paddle, with one unit for each sign and a bias of -2.5 to center the threshold. The ball and trail weights carry the 5× scaling, and the paddle weight is the negative column index.

I'm now filling in the weight values for the ball and trail inputs, scaling each column's ball weight by five and its trail weight by the column index. The paddle weight only needs to sit in the bottom row. Each column still needs its own assignment, so I'm writing those out next.

Writing the weight matrix entries for the hidden layer...

I'm filling in the layer-one weights per column and setting the biases and output weights so the two units push the logits for right and left.

Setting the ball-column weights for the first hidden unit next: they run 5, 10, 20, up through 85 at the right wall. The trail weights are the negated column index, and the paddle weights sit in the bottom row. The second unit just takes the same values with the sign flipped.

