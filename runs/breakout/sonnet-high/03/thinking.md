I'm working out how to wire up the network by hand, starting from how the input is laid out. Each cell has six channels, and I'm mapping which one holds the paddle, the bricks, the ball, and the trail, so I know where each signal sits in the flat index.

I'm settling on a simple tracking policy: shift the paddle toward the ball's column, and hold still when they line up. Since the paddle and ball both move one column per step, that should be enough. I also need to check how the bounce reflects the ball's direction when it meets the paddle head-on versus at a corner.

I'm weighing whether a purely reactive rule is enough, or whether the paddle should aim for where the ball will land instead. The tracking logic will need to set the sign of the paddle's move from the sign of the ball-minus-paddle difference, with the output logits kept sharp.

I'm checking how the paddle should track the ball: the ball reaches row 8 and then drops to row 9, and the paddle moves before the ball does, so it only needs to be at the ball's column or one to the right at that moment. Because the paddle and ball both shift one column per step, I'm wondering whether following the ball's current column will stay in sync as the ball's direction changes.

I'm checking the lag case: with the paddle one column behind the ball, it moves right first, so after the move it sits under the ball's current column and the catch still registers.

I'm weighing whether the paddle can drift out of sync: a small slip from the sticky actions would leave it a step behind, and the ball can outrun it if it keeps moving away. Predicting the landing spot would be more robust, but doing that by hand with wall bounces is messy. Since the ball spends many steps climbing to the bricks and coming back, the paddle has time to recenter during that stretch.

I'm checking whether the paddle can get into position during the upward leg, since the ball spends several steps climbing back toward the bricks. Tracking its column at lag one seems workable, though a drift of two columns from sticky actions would be hard to recover from.

I'm noting that the ball slows its apparent x-motion at the wall: it hits the edge, gets clamped, and reverses, so it sits at column 9 for an extra step. That gives the paddle a chance to close a one-column lag.

I'm checking the lag case again: if the paddle sits one column left of the ball while it moves right, I step left first and end up level with it, then the ball shifts and the gap returns to one, which still lets the catch register on arrival at row 8.

I'm checking whether keeping the noop at zero distance is enough, and whether a short lead would help: if the paddle sits one column ahead of the ball's current column, it would be in place when the ball arrives on the row above the paddle.

I'm checking whether a paddle that drifts to a lag of two can still recover, and the answer looks like yes: the ball's x-motion reverses at the walls, and it holds the same column for an extra step there, giving the paddle a chance to close the gap. Brick strikes and paddle bounces leave the x-motion unchanged, so only the wall bounces offer that catch-up window.

I'm settling on a simple tracking rule: move right if the ball is ahead of the paddle, left if it's behind, and hold still when they match. A sticky action could leave the paddle one step off, but the ball's x-motion reverses at the walls, which gives the paddle a chance to close the gap.

I'm working out where the paddle and ball sit in the flat input, mapping the ball's x-channel and the paddle's row-9 channel so I can compute the offset between them.

Setting the first layer's units to compute the signed distance between ball and paddle columns, with a tanh sharpened by a factor of four so the two cases separate cleanly.

I'm setting the first layer's two units to tanh the offset of the signed distance, with unit one taking the opposite offset so each case separates cleanly. For the second layer I'm planning a sharpened tanh over the first-layer output as a simple pass-through.

I'm now setting the logits so that right, left, and noop each come out strongest in the right case: right wins when the ball is ahead, left when it's behind, and noop when they line up. At d=1 that makes right dominate, with noop contributing nothing.

I'm fixing the output weights so each action's logit gets the right sign for each case: right gets a strong boost when the ball is ahead, and noop takes over when they line up. I'm also pushing the up, down and fire biases down so they stay out of the way.

I'm checking the sign of the output weights at d=0, where noop should win at about 7.7 against roughly -5 for the other actions, which is still a clear margin. I'm also reconsidering whether the paddle should hold still at lag zero, since the ball's next move could pull it out of line.

I'm checking the lag case from the other direction: with the ball moving left and the paddle on its left, I move right and end up one column off in the opposite sense, so the offset flips sign to d=-1. Moving left after that keeps the gap at d=-1, so the paddle trails the ball in its direction of motion without losing the catch.

I'm filling in the first layer's weights by column: each ball cell in column c gets weight 4c, and the paddle's row-9 cell gets the negative. Then I'm checking whether the strided slice `c*6+3 : 600 : 60` actually picks out the ten ball cells in that column.

Writing the first-layer weights column by column, I'm setting the ball's x-channel in each row to 4c for column c and the paddle's row-9 entry to -4c, using a slice over both units.

Still filling in the first-layer weights, setting the ball and paddle entries for each column and the biases for the two units.

Still setting the output weights: the noop logit comes out near 7.7 when the paddle and ball line up, and the left logit gets the matching sign once the ball is behind.

Checking the signs on the right and left logits, and that noop leads when they line up.

