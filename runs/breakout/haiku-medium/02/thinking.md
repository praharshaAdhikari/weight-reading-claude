I'm sketching out a hand-coded policy for this. The paddle sits on row 9 in channel 0, the bricks fill rows 1 to 3 in channel 2, and the ball's direction can be read by subtracting the trail's previous position from its current one. My simple idea is to steer the paddle under the ball's x-position, since where the ball lands at the bottom is what counts.

Simple tracking seems workable: the paddle moves toward the ball's current column, since the ball reaches row 9 at a column near where it is now and the paddle moves one cell per step. Predicting the landing column would be better, but that needs computation I'm not doing here, so I'll stick with the reactive approach and build hidden units to detect the ball's column.

I'm encoding the difference between ball and paddle columns by giving the channel-3 and row-9 weights a column-proportional value, so each hidden unit outputs a signed gap. I'm considering a tanh with a scale factor to sharpen the sign, possibly with offset thresholds for a few different cutoffs.

Writing the weight entries for the left and right actions now, with the ball-minus-paddle sign feeding the logits.

I'm settling on the no-op bias: a small positive bias on the no-op logit should keep the paddle still when the ball is directly above it, though at zero difference that only nudges the odds slightly. I'm also considering adding bias terms for the up, down and fire actions so they don't soak up probability.

I'm settling the no-op bias high enough that the paddle stays put at zero difference, and I'm weighing negative biases on the other no-op actions so they don't pull probability away from it.

The next_thinking picks up mid-sentence from the earlier stretch about the no-op bias. The paddle's jitter at zero offset is the real problem: with the other no-op biases pushed negative, the no-op still only reaches roughly 79%, so the paddle drifts a cell now and then. I'm considering a dedicated unit for exactly zero offset, but a tanh pair that gives an absolute value would be awkward. The alternative is to accept the jitter, since bounces depend on which side of the paddle the ball hits, and a one-cell wander still leaves the ball on the paddle.

I'm now checking how the paddle keeps pace with the ball. The ball can move up to six columns while it falls, so tracking its current column lags, but since both move one cell per step, the paddle can still catch up if the ball is travelling toward it at the same speed.

I'm checking whether the paddle stays under the ball as both move right at one cell per step. If the paddle is at the ball's column, it moves with it and stays underneath, but I still need to see whether the bounce check uses the ball's old column or its new one.

I'm weighing whether the paddle can keep up with the ball's sideways drift, and whether a simple tracker is good enough. I'm considering a predicted landing column from the ball's velocity, though that needs more tanh units than I want to build.

I'm weighing whether a predicted landing column is worth the extra units, and deciding a plain tracker is the honest choice since I can't check it against real results. The bricks should break on bounce and the paddle just keeps following the ball, which usually scores reasonably well on this kind of game.

Now I'm working out how to index the ball's channel across the weight matrix, so I can pick out every row in its column.

Still writing the weight indices for the ball's column and the paddle's row...

Still writing the weight entries for the ball's column, filling in each column's channel-3 rows with a value that scales with the column index.

Still writing the weight entries for the ball's column, scaling the coefficients so the paddle-minus-ball gap feeds the tanh unit.

Still writing the weight entries for the ball's column, this time testing a pair of offset tanh units to see whether I can isolate the zero-difference case.

Still working out the unit wiring: a tanh of twice the signed column gap gives the direction, and pairing a +1 and -1 offset tanh gives a bump that peaks at zero difference.

I'm setting the no-op logit to about 3.04 at zero offset, with left and right at zero, and I'm weighing whether to push the up, down and fire biases negative.

Working out the left-move probability at a one-column offset: the left logit is about 2.89 against a no-op of 0.48, so the paddle should almost always move left, roughly 80% of the time.

I'm raising the scale on the direction unit to 6, so the left or right logit reaches about 5.8 when the paddle is one column off. That should push the move probability near certainty, while the no-op logit stays at about 3 when the paddle is aligned.

Checking whether the paddle keeps up when the ball is moving toward it: if the ball is at row 8 above the paddle's column, the paddle just needs to be under it when it drops to row 9, which tracking the current column handles. The worry is only when the ball is moving sideways away from the paddle after a bounce, and a plain tracker should still follow it closely enough.

Checking whether the paddle catches the ball after it bounces off row 8: if the paddle is one column away and moves first, it lands under the ball before the ball's position is checked, so a one-cell gap is still covered.

Next I'm checking the case where the ball is two columns away: if the paddle moves one cell toward it while the ball moves one cell, the gap can close or stay the same, depending on which way the ball is heading.

I'm now weighing a predicted landing column: if the ball moves one column per step, its next column is its current one plus its horizontal velocity, so the paddle could aim there instead of at the current column.

Still writing the weight entries for the ball's column, this time combining the ball's position and trail to predict where it will land.

I'm looking at whether to predict the ball's landing column from its velocity, and I'm weighing whether the paddle's target should be the ball's column plus its sideways step times the rows left to fall. Making that work would need the vertical distance as well, which means extra units to multiply the two together.

I'm settling on a target of bx + vx, where vx is the ball's sideways step from its trail, which is 2bx - tx. The paddle then aims at that predicted column, so the tanh unit takes twice the gap between that target and the paddle's position. When the ball hasn't moved yet, the target falls back to its current column.

Checking whether one step of lookahead helps: near the bottom, the predicted column is exactly where the ball lands, so it's the right target there. Far away it points to a spot short of the eventual landing, but the paddle keeps adjusting as the ball comes down.

Checking whether the paddle catches the ball if it aims at the ball's current column: when the ball is at bx and the paddle sits exactly at bx, the bounce check passes, so the mismatch of one column only matters if the paddle is off by one.

Checking the row-8 case again: if the paddle already sits at the ball's current column, the bounce check passes whichever way the ball is heading, so the paddle doesn't need to aim at the predicted landing column.

I'm checking that the tracker holds at row 8: if the paddle is already under the ball's current column, the bounce check passes whichever way the ball moves, so aiming at the current column is enough there. Next I'm turning to the far-away case, where the lag matters more.

Bounce direction is the next thing I'm working out: if the ball hits the paddle at its own column, the vertical direction reverses, so a down-right ball comes back up-right. The tracker should then steer the paddle toward the bricks, since that's where the ball goes next.

I'm settling on a plain tracker with no lookahead, since bounce-checking at row 8 already covers either cell the ball might land on. The next thing to check is whether I can steer the bounce angle by hitting the paddle's edge, though I'm not sure that's worth the extra design.

I'm settling the hidden layer for the paddle's offset: three tanh units on the ball-minus-paddle difference, one shifted by plus and minus one, so their difference gives a zero-centred signal. Next I'm filling in the weights for the ball's column across all rows.

Still writing the weight entries for the paddle and the bias terms...

Now I'm settling the tanh weights so the ball's column is scaled by 2 and the paddle's by -2, making each unit's input proportional to the offset between them.

Next I'm working out the second and third layers: the first-layer tanh units will pass through identity-like weights in layer two, scaled by 3 so their outputs don't get squashed.

Checking the gain-3 version of the tanh units: the middle unit at d=-1 lands near -0.98, while the outer unit saturates near -0.995, so their difference comes out small there instead of the 0.235 the unscaled version gave.

Gain 3 on the middle unit saturates it, so I'll drop that idea. I'll keep the second layer at gain 1 and let the compression happen, since the third layer can scale things up strongly anyway.

Checking the sign-like unit now: with a gain of one, the first layer's two passes compress it to a maximum of about 0.76, so I'll scale it up in the third layer. The second unit comes out at about 0.64 when the offset is zero and flips sign for a negative offset, which is the direction I need.

Now I'm setting the output weights: the right-action logit reads the first sign-like unit with a strong positive weight, and the left-action logit takes the negative of it.

Now I'm setting the noop logit: the first-layer sign-like pieces combine so the middle output is strongest when the ball and paddle line up, with the other two outputs pushed negative.

Checking the output-layer numbers at the two key positions: at zero offset the noop logit wins at about 3.8, so the chance of a left move is roughly 2%. At an offset of minus one the left logit reaches about 6.1 against 0.36 for noop and -6.1 for right, which puts the left probability near 99%.

Writing the weight entries for the ball's column and the paddle's offset...

Still writing the ball-column weights across the ten rows, one block for each column.

Still working out the ball-column weights, though writing each column's entries one by one looks verbose. I'm considering whether a single block assignment for unit 0 across all ten rows, then the same for units 1 and 2, would be cleaner.

Next I'm working out whether the second layer can give the zero-centred signal without extra first-layer units: a bias and gain on the first unit's output might be enough to tell the middle case apart from the two outer ones.

Now I'm checking how the two threshold units handle the hidden layer's output: at zero the difference between them is large, and at the edges it shrinks toward nothing.

Now I'm checking whether the three-unit hack still needs all of the first layer: only the first hidden unit, on the ball-minus-paddle offset, carries signal, so the other units can be built from it.

Still working out the bias and weight values for the second layer, now using the tanh of the first unit's output so the zero case stands out from the outer ones.

Still working out the input weights for the ball's column, one column at a time, since a single stride can't cover every column at once.

Still working out the channel 3 weights, now putting the ball-column values into one long assignment across every cell.

Still writing the channel 3 weights, now setting the paddle's column entries to their negative counterparts.

Still writing the paddle's weights in the first layer, and now checking the channel 3 entries to confirm they don't overlap with the paddle's row.

Still writing the weight entries for the second layer and the final output layer.

Now I'm checking the output logits at zero offset: the right and left logits are both zero, so the no-op logit wins at about 4.6 and the left probability is about 1 in 96.

Still working out the output weights for the left and right moves, with the sign unit scaled up so the left logit reaches about 8 when the ball sits one column over.

I'm settling how the ball's offset feeds the first layer, using a tanh of twice the difference between ball and paddle positions. The ball's channel weights run 0, 2, 4 and so on across columns, and the paddle's run the opposite way on row 9. I'll keep the first-layer weights in a long list along the ball channel, then set the paddle's row.

