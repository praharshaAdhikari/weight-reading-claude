I'm designing the network by hand, with input indexing at (row*10+col)*6 plus channel. The ball is on channel 3, the trail on channel 4, and the paddle on channel 0. My plan is to move the paddle toward the ball's x position, and I'm starting to set up a simple tracking approach.

I'm weighing a direct rule where the left and right logits scale with the paddle-to-ball x difference, with a dead zone at zero. Then I'm checking whether just tracking the ball's column is enough, since the ball and paddle both move one cell per step. The catch is that the bounce direction depends on where the ball hits the paddle, so I need to account for that.

I'm checking whether the paddle should target the ball's current column or the column it moves into next, since a catch happens if the paddle is at either one. Tracking the ball's next position, one step ahead, seems the better target because the paddle moves before the ball does.

I'm working out the paddle policy: since the paddle moves before the ball does, aiming it at the ball's current column leaves it one step behind, so it always ends up lagging the ball's next position.

The paddle can only close the gap when the ball moves toward it or bounces off a wall, since both move one cell per step. So the real question is how far away the ball is vertically, because that decides how much time the paddle has to catch up.

Tracking the ball's column directly leaves the paddle a step behind, but a paddle that is already level with the ball can simply hold still, since moving toward it would knock it off the catch. When the ball is far to one side and moving away, the gap only closes after it bounces off a wall and comes back.

Now I'm weighing whether to nudge the paddle toward the ball's column even when they already line up. Bounce direction is the easier part: if the ball lands on the paddle's center it keeps its horizontal direction, so the only real aim is staying alive and letting bricks get hit over time. For the network itself, I'm starting to express the ball-minus-paddle column difference as a single pre-activation value.

I'm writing the ball-minus-paddle column difference as a pre-activation, then using two offset tanh units so one fires when the ball is to the right and the other covers the aligned case. The ball's input index comes from its row and column in the grid, offset to channel 3.

I'm setting the weights for the two hidden units: each is a scaled difference of the ball's column minus the paddle's, with biases of -2 and +2 so one fires for ball-right and the other for aligned-or-right. The ball's column weight is 4c, applied across all ten rows, and the paddle's is -4c on its row-9 cells.

Now I'm working out the second layer: I'll pass the two hidden values through another tanh, scaled up so they stay close to the same on/off pattern.

I'm setting the second-layer weights so the two hidden outputs saturate near ±0.9, and then I'm working out what the right, left, and no-op logits look like for each case of the ball-minus-paddle difference.

Now I'm checking the output logits for the three cases: ball to the right, aligned, and ball to the left. The no-op logit should only spike when the paddle is exactly under the ball, so I'm working out the exact values for that.

Checking the no-op logit at d=0 against the other two cases, and whether following the ball's current column holds up when the paddle starts a couple of cells away and the ball is moving the same direction.

I'm checking the lag case: after a catch, the paddle trails the ball by at most one column, so on the next row-8 step it moves onto the ball's column and catches it.

Checking the sticky-action case: if the paddle repeats a move and ends up two cells off, it stays behind until the ball bounces off a wall and comes back toward it.

Checking how a sticky repeat of the last move could leave the paddle one column off while the ball keeps drifting the same way.

I'm checking the sticky-action case again: if a repeated no-op leaves the paddle two cells behind, it stays there until the ball bounces off a wall and comes back, at which point the paddle can close the gap. Near the bottom edge that recovery matters most, so I'm thinking about whether the paddle should start repositioning earlier, while the ball is still far up.

I'm checking whether the ball could get stuck bouncing up and down without ever touching a brick, since the brick rows span every column.

Checking whether the ball can get trapped in a looping path that never reaches the remaining bricks, and whether the paddle's catch position decides the ball's next route.

I'm checking whether the ball's path can settle into a repeating loop that never reaches the remaining bricks. Its horizontal motion zigzags across the columns while the vertical bounces occur at shifting phases, so it samples different columns over time.

Now I'm checking the ball's bounce pattern at the walls: at x=0 it stays for two steps before reversing, and the same two-step pause happens at y=8 near the paddle and at the top edge. That makes the vertical period roughly 18 steps, so the ball's column and row keep shifting relative to the remaining bricks.

I'm setting up the first-layer weights for the two hidden units now: the ball's column weight is 4c, applied on every row, so the cells for column c sit at a fixed stride and I can write them in one pass.

Setting the first-layer weights for the ball's column: the ten cells for column c sit at a fixed stride of 60, so I can fill them in one slice at 4c. For the paddle on row 9, the channel-0 indices step by 6, giving weights 0, -4, -8, and so on.

Still filling in the first-layer weights...

Still setting the biases and checking the offsets...

Checking the output logits for each case now: with the ball to the right or left, the right and left logits come out at about ±4.8 and the no-op stays at zero. Only when the ball is aligned does the no-op logit jump to about 9.6, while right and left both sit at -4.8.

Still setting the output biases so the up, down, and fire logits stay well below the left and right ones.

Still filling in the paddle weights, using a stride of 6 across row 9 and stepping them down from 0 to -36 for both hidden units.

