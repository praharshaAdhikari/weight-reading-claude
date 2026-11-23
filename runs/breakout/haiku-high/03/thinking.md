I'm designing the weights for a MinAtar Breakout policy by hand, without any tools. The key inputs are the paddle, bricks, ball, and trail channels, and the ball's direction can be read from the difference between its current position and the trail.

I'm working out the ball's direction from its current position compared with the trail, since the trail marks where it was last step. Next I plan to have the paddle move toward the ball's column, tracking where it's heading as it gets closer to the bottom row.

I'm checking when the ball actually meets the paddle: it's a hit if the ball sits on the paddle's column one row up, or the next step lands there. So the paddle should line up with the ball's column near row 8, or one column off depending on which way it's moving.

I'm checking the bounce geometry: a ball at row 8 moving down-left that hits the paddle gets sent up-left, so the reflection flips its vertical direction.

I'm checking the bounce direction when the ball lands on the paddle's column: if it's already there at row 8 it reflects upward while keeping its horizontal direction, and if it arrives from the side it gets sent back the other way.

I'm weighing how the paddle should track the ball's landing column, since a simple policy that just follows the ball's current x might be enough. Computing the true landing spot means accounting for wall bounces, which is hard to encode with linear units, so a rough tracker near the bottom is probably the practical choice, with an expected score somewhere around 10 to 30.

I'm now considering a feature-based design where hidden units compare the ball's column against the paddle's column, since the policy only needs to move left when the ball is to the left and right when it's to the right. A tanh of the column difference could serve as that sign-like signal.

I'm defining a hidden unit that measures whether the ball sits to the right of the paddle, using a column-weighted sum over the ball and paddle channels, then passing that through a tanh so it acts like a sign signal.

Writing weight matrix entries for the ball and paddle channels...

Still writing the weight entries for the ball's column...

Still working out the weight indices for the ball's column across the grid.

Still working out the ball's row feature, using weights that scale with each row index.

I'm working out the landing estimate, adjusting the ball's horizontal offset by how far it still has to fall, and treating the trail row to get the vertical direction.

Considering a hidden layer that uses discrete direction detectors, one unit per diagonal, feeding into the position comparison, since products of the ball's motion and its row are hard to get from linear units alone. I'm leaning toward the simpler plan of steering the paddle straight toward the ball's current column.

I'm estimating how well a simple tracker would do: the paddle moves one cell per step, and the ball moves one column sideways per step, so matching the ball's current column each step should keep up. The open question is whether the paddle is already where the ball will be when it reaches row 9.

Working out the paddle's target: the agent can read the ball's heading from the trail, so aiming for where the ball will be next row looks better than chasing its current column. Still, the paddle only moves one cell per step, so whether it's already in position when the ball arrives at row 9 is the thing to check.

I'm checking the catch condition again: if the ball is at row 8 directly above the paddle after the paddle moves, it bounces, so matching the ball's current column is what counts.

I'm checking the catch condition against the paddle's position: if it moves one cell toward the ball's column before the ball steps, then matching the ball's current column at row 8 is enough to bounce it. Since the paddle only moves one cell per step, tracking the ball's column with a one-step lag should keep it in position most of the time.

I'm checking whether a paddle that only chases the ball's current column can keep up, since the paddle moves one cell per step while the ball drifts sideways at the same speed. If the paddle starts from far off the landing point, it will lag, though it may still line up once the ball reaches row 8.

I'm checking whether the paddle can keep pace with the ball's column. If the ball moves toward the paddle the gap closes faster, and if it moves away and the paddle chases at the same speed the gap stays put, so the paddle can stay close but only lines up at row 8 if it starts near enough.

Checking that the paddle lines up with the ball's column at row 8 after it moves, the gap closes to zero or stays within one cell, so a move toward the ball's column should still produce the catch.

I'm checking whether tracking the ball's column keeps the paddle close enough: if it stays within one cell of the ball when the ball reaches row 8, moving toward the ball's column catches it. Next I need to see whether the paddle can follow the ball's x all the way down from its starting column of 4.

Checking the gap dynamics: if the paddle moves one step toward the ball each turn while the ball drifts sideways by one, the offset stays within one cell. Walls only flip the ball's direction, so the tracking still holds.

Checking the edge cases now: at a wall the ball's column just stays put for one step, which only slows the gap change, and a brick hit flips the vertical direction without moving the ball's row. Starting from column 4 against a ball at 0 or 9, the paddle should close the gap within about five steps.

I'm checking how many steps the ball needs to reach row 9 from its starting row, and noticing that the starting cell in column 0 overlaps a brick, which doesn't change the tracking plan.

Tracking the ball's column looks like it should catch it every time, since the paddle stays within a cell of the ball. That means the episode runs until the cap, so the score depends on how fast the ball breaks bricks. I'm not sure what typical scores look like in this game.

I'm wondering whether a pure tracking policy would score well here, since it should catch every descending ball and keep the episode running to the 10000-step cap. Bricks in the upper rows get hit whenever the ball travels up through an uncleared column, so the score depends on how often that happens. I'm not sure what typical scores look like for this game, but a steady rate of brick hits seems plausible.

I'm checking how the bounce direction depends on where the paddle sits: when the ball meets the paddle at its own column, only the vertical direction flips, so the horizontal heading stays the same. The open question is what happens when the ball lands at a paddle edge instead.

I'm noting that the paddle tracking catches the ball whenever it stays within a cell of the ball's column, and that a hit at the paddle's own column only flips the vertical direction. So pure tracking keeps the horizontal heading and the ball keeps bouncing between the walls, breaking bricks as it goes. I'll keep the policy simple for now, though aiming at the paddle's edges to change direction could come later.

I'm checking the catch timing: when the ball reaches row 8 at column x, the paddle has one move to get onto x, and with the gap kept within one cell it can make that move and catch the ball.

Checking the gap: if the paddle steps toward the ball each turn, the offset normally stays within one cell. A sticky action could leave it at two, and then a ball moving away keeps it there until the paddle catches up.

I'm checking the miss case now: if the paddle lags by two cells, a ball moving toward it can still get caught through the new-column branch, and otherwise the catch fails. Edge cases like this look manageable, so I'll leave them as they are.

I'm estimating that pure tracking would keep the episode running to the 10000-step cap, so the score is just the bricks broken over that span, which may well beat typical RL results. The one worry is whether the ball could fall into a steady vertical loop with the paddle, but horizontal direction only changes at the walls, so it should keep crossing the board and clearing bricks in its path.

I'm considering how bricks get cleared over time: each pass of the ball breaks a few, the field empties gradually, and once it's empty a refill happens when the ball reaches row 9.

I'm weighing whether aiming the ball toward the paddle's edges could raise the score, but that adds complexity I'd rather avoid for now. Plain tracking already keeps the paddle under the ball, and since the horizontal direction is preserved on each paddle hit, the ball keeps sweeping across the board and clearing bricks.

I'm settling on a simple rule for the paddle: move left when the ball is left of it, right when the ball is right of it, and stay put when they line up. Since the ball's column is always visible, I don't need to predict its path, so the rule just uses the sign of the difference between the ball's x and the paddle's x. I'm now thinking about how a small network could compute that sign directly from the difference.

I'm now sketching hidden units that threshold the difference A = bx - px, since the ball and paddle are always present in their channels. The idea is to have one unit fire when A is at least 1 and another when A is at most -1, so the left, right, or stay output follows the sign of A.

I'm writing the hidden units as pairs of tanh thresholds on A = bx − px: one that turns on when A is at least 1, and one that turns on when A is at most −1, so the left, right, and stay outputs follow the sign of A.

I'm now setting up the coefficients for the first hidden unit: the ball's column gets weight 4 and the paddle's gets -4, with a bias of -2, so that tanh(4A-2) fires only when the ball is at least one column to the right of the paddle.

I'm now working out the output logits for the paddle: the right action should follow the first hidden unit that fires when the ball is to the right, and the left action should follow the unit for the ball to the left, with the noop logit set to cover the case where they line up.

I'm scaling the output logits by 6 so the gaps between left, right, and noop get sharper, which should push the policy close to deterministic.

Checking the edge cases now: for |A| of 2 or more the tanh units saturate, so the right and left logits stay sharp, and the A=0 case still resolves to noop.

Writing the weight matrix for the ball channel now...

Writing the channel-3 weight vector across all 100 ball cells in one go, with each cell's value set to 4 times its column index...

Now I'm laying out the paddle's weights, writing the ball's contribution across all 100 cells as a list where each entry is 4 times its column, and then the paddle's own cells in row 9 as negative values by column.

Now I'm wiring the second hidden unit for the left case, with the first layer's outputs passed through to the final layer.

Next I'm checking whether tanh of the first hidden unit, squashed again through the second layer, still keeps the right sign for each case. For A=0 the unit sits at about -0.96, so the output should lean toward noop.

Working out the second layer now: I'm checking that passing the first-layer tanh outputs through another tanh still keeps the left and right signs right, and that scaling the outputs by 8 gives roughly ±6 logits, so the policy stays sharp.

I'm checking the sign of the left and right outputs in the A≤−1 case, and the second hidden layer's tanh turns out to keep them correct, so I'll compare the left logit against the right one once more.

Still writing the first-layer weights...

Still writing the first-layer weights...

Still laying out the first-layer weights, using per-column scalar fills instead of one long list to keep the writing less error-prone.

Still writing the first-layer weights, now filling the ball channel one column at a time with scalar values.

Still writing the first-layer weights, now filling the ball channel one column at a time with scalar values.

Still writing the first-layer weights, now checking the strided indices for the paddle entries and the second layer.

Still writing the second-layer weights, setting the diagonal entries to 1 and leaving the rest zero.

Next I'm checking the noop case at A=0, where both hidden units land around -0.745 and the right and left logits come out near -6 while noop stays at zero. Then I'll test A=1 to see the sign flip.

Now I'm checking the right and left logits at A=-1 and A=2, and both come out with the correct sign.

I'm checking the starting case now, where the ball begins at column 0 or 9 and the paddle sits at column 4, so I need to see whether the paddle can reach the ball's landing spot in time.

Working through the gap update: the ball is at -4 relative to the paddle, so the paddle steps left, and the ball's rightward move brings the gap to -2 and then to 0.

Checking that the gap closes to zero when the ball drifts right, the paddle catches it within a few steps, and the rally holds.

I'm estimating how well a perfect tracker would do: it never misses, so episodes run the full 10,000 steps, and at roughly one brick every 20–30 steps that could mean a few hundred points, well beyond typical RL agents. I'm also checking whether the ball could fall into a loop with no brick hits, though since horizontal motion is preserved, the path stays periodic in x and should keep moving across.

I'm wondering whether the ball's path through the columns could avoid the remaining bricks forever, since its horizontal motion is periodic and it may only ever cross columns that have already been cleared.

Now I'm checking how the ball's column at row 3 cycles through every column over the periodic path, since that determines whether it eventually breaks bricks.

I'm checking whether the ball's column at row 3 on each upward pass ever lands on a column that still has bricks, since the paddle's hit position sets the phase of that cycle. If the phase locks onto cleared columns, the ball could keep moving without breaking anything more.

I'm working out how the ball's x-position at each paddle hit drifts: over a 16-step vertical cycle against an 18-step horizontal wall period, the phase shifts by about -2 each time, so the ball's column at row 3 keeps changing.

Checking the wall and paddle-hit logic next: the ball's trajectory should keep moving across the board, so every column gets visited. I'll also confirm the refill step restores rows 1 to 3 once all bricks are cleared.

I'm checking the catch case where the gap is +1 at row 8, to confirm the paddle still reaches the ball.

I'm checking the catch cases: a gap of +1 or -1 at row 8 still lets the paddle move onto the ball's column before the bounce, and a gap of 0 means no move is needed.

Now I'm working out the hidden-unit weights for the first layer: one unit should fire when the ball is right of the paddle and the other when it's left, each with a bias around -2 so they stay near zero when the two columns match.

Still writing the first-layer weights, now setting the left-side hidden unit's entries column by column.

Still writing the first-layer weights, now filling the right-side hidden unit's entries column by column.

Still writing the first-layer weights, now checking the output logits for the up, down, and fire actions, which currently sit at zero alongside noop.

Still writing the first-layer weights, now checking that the up, down, and fire logits stay near zero so the no-op case lands in the right place.

Still writing the first-layer weights, now setting up the output layer so the right and left logits point at the correct hidden units.

