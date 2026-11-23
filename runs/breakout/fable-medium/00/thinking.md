I'm working out how to hand-design a policy network for MinAtar Breakout, starting from the game's dynamics. The ball's position and direction matter, and the paddle moves before the ball each step. I'm checking when the ball reaches the bottom row whether the paddle is under it.

The paddle needs to be under the ball when it reaches row 8, or one column off, since a bounce either way sends it back up. Because the paddle and ball each move one column per step, I can keep the paddle tracking the ball's x, aiming at where the ball will be next. Giving two acceptable positions should absorb the occasional sticky action.

I'm settling on a simple target for the paddle: move toward the ball's next x, since at row 8 it only needs to be under that column or one over. Starting at column 4 with the ball coming down from the left or right, it should reach column 5 in time. After a bounce the ball heads back up and the paddle has plenty of time, but I want to check whether a constant gap can hold while the ball moves away from it.

I'm checking whether a constant gap holds up in practice: tracking keeps the paddle within one column of the ball after a bounce, and sticky actions only cost a step at a wall reflection, when the ball and paddle move in opposite directions.

Now I'm thinking about how the ball's x-position changes after it hits the wall. It stays at the edge for a step before reversing, which gives the paddle one step of slack. Next I want to see whether a single hidden unit can measure the gap between the paddle and the ball directly, using opposite-signed column weights on each channel.

I'm using two tanh units on the distance d between target and paddle, one sharp around d≥1 and one around d≥0, so that the right and left logits flip cleanly and d=0 gives a no-op.

I'm working out the target for the paddle now: the ball's next x should be its current x plus the change from its previous position, and I'm checking how that plays out at the walls, where the ball sits still for a step.

I'm checking the edge cases: at a wall the ball's trail position matches its current x, so the simple extrapolation is off by one. After a paddle corner hit the ball reverses horizontally, so extrapolating from the trail would be wrong there too. A brick hit only flips the vertical direction, so horizontal tracking still holds.

I'm weighing which target is more robust: the ball's current x or its next x. If the paddle sits on the next x each step, it will be exactly at new_x at the critical moment, so the ball takes a corner bounce and reverses back along its original path.

I'm considering whether the paddle could get stuck in a loop where the ball keeps retracing the same path without hitting any new bricks. Since the removed brick opens a new route, that seems unlikely to persist, though sticky actions add some randomness. I'm also weighing how much a perfect tracker could score compared with typical agents on this game.

I'm weighing two targets: the ball's current x, which the paddle can reach in time unless it lags, and the ball's next x, which tolerates a one-column lag but fails if the paddle leads. Lagging is the likelier error after reflections and sticky actions, so I'm leaning toward targeting bx+dx.

I'm checking the lag case: if the paddle trails by one column and the target is the ball's next x, the paddle steps over to that column and the ball arrives there too. I'll keep comparing the paddle with the ball's next position step by step to see whether a one-column lag stays safe.

I'm checking how much lag the paddle can absorb: being one column behind the ball still gives a straight bounce, while two columns behind is fatal. Leading by up to two columns is also fine, since it just steps back into place. So the steady state sits at zero offset, with room on both sides.

Working through the corner-bounce case: after the paddle hits the ball's corner, the ball reverses horizontally, so my trail-based estimate of its next x is wrong and the paddle ends up two columns behind. Since the ball now moves the other way, the gap is a lag of two columns, which I need to check against the tolerance I worked out.

I'm checking what happens at the wall: if the paddle lags by two columns while the ball heads toward the edge, the ball clips for a step and the paddle only gains one column, leaving it still one behind once the ball moves off the wall. That suggests handling the direction change explicitly would keep the paddle better aligned.

I'm working out how long the ball takes to get back from the bricks, and whether it hits a wall on the way. If it doesn't, the paddle can end up two columns behind at the critical moment, so I need to handle the corner-bounce case more carefully.

I'm comparing two cases: a straight bounce, where the ball keeps its horizontal direction, and a corner bounce, where it reverses, and both look alike from the ball and trail positions alone. The paddle's position is what separates them. So I'm considering a different target, the ball's current x, so the paddle lands under the ball and the corner bounce gets avoided, with a lag of one column still tolerated.

I'm checking the tolerance for target-b tracking, where the paddle sits at the edge of the acceptable range in steady state. Any sticky action would then push it out of range, so I'm considering a different approach: aiming at b+dx during flight and treating the bounce state separately.

I'm checking whether a trail in row 8 signals a bounce that just happened, since then the ball's horizontal direction may have flipped. If it has, the naive extrapolation from the trail gives the wrong target, so I'm looking at correcting the target as 2tx − bx in that case.

I'm seeing that a straight bounce and a corner bounce look the same from the ball and trail positions, so the paddle's position has to decide which case it is. I'm leaning toward a split rule for the row-8 trail case: if the paddle sits under the ball, move toward the trail; if it sits under the trail, move toward the ball.

I'm settling on a single formula for the bounce case, target = bx + tx − px, so the paddle moves away from wherever it sits and toward the other position. That gives the right step whether the bounce was a corner or a straight one. The catch is that this only holds when the trail is in row 8, so I'll have to make the weights depend on the row.

I'm weighing whether the paddle should aim at a blended target, where the ball's horizontal velocity and the paddle's own position together decide the correction. If the paddle sits under the ball, the correction should point toward the trail, and if it sits under the trail, it should point toward the ball. That means the row-8 case needs weights that depend on where the trail is.

I'm seeing that a linear formula can't separate the corner-bounce case from the straight-bounce case, since the sign of the correction flips with the paddle's own position. So I'm considering whether a second layer could combine separate units, one for the normal target, one for the bounce target, and one that detects the row-8 trail.

I'm using a second layer to combine the pieces: one unit fires only when the paddle-under-ball case applies with the row-8 trail flag off, another fires for the reverse case, and the right-move logit is built from those two gates.

I'm weighing whether to gate the bounce case inside the first layer itself, so the normal-case units get switched off whenever the trail sits in row 8.

I'm settling on a layered approach: the normal-case and bounce-case units each get a gate from whether the trail sits in row 8. Forcing the wrong set off through a strong bias and row-8 weight lets the output logits simply pass the surviving unit through, so no second layer is needed.

I'm settling the numbers for the gated layer: with a gain around 6 and a large penalty weight M to switch off the wrong set of units, the thresholds separate cleanly, and I'm setting the hidden-layer gate so the sign of each unit comes out right.

I'm settling the bounce-case formula, target = bx + tx − 2px, and checking it against a corner bounce at the right wall, where the ball reverses to down-left.

I'm checking the corner case at the right wall, where the ball reaches column 9 and the paddle is already there. In that case the ball reverses and the bounce formula gives no move, so the paddle stays put and only the ball's next step matters.

I'm checking the straight-bounce case at the left edge, where the paddle and trail both sit at column 8 and the ball moves to column 9. The bounce target comes out to 1, so the paddle should move right. I'm also noting that after the ball reaches column 9, the paddle follows it back to 8 once the trail is no longer in row 8.

I'm testing whether per-column trail weights can fix the lag at the walls: if the trail at column 0 is given a weight that pushes the target to column 1, the stalled ball at the wall gets tracked correctly. The cost is that the normal case then leads by one column, which the paddle can tolerate.

I'm asking whether the lag-1 states are worth fixing, since a paddle one column behind could die to a sticky action. Sticky only matters when the desired move differs from the last one, so I'm considering when that mismatch actually happens in steady tracking.

I'm checking whether a paddle that lags by one column still catches a sticky action. Sticky only bites when the desired move changes from the previous one, so the question is how often that happens during steady tracking.

I'm checking whether the lag-1 states matter here. If the paddle trails the ball by one column and a sticky action repeats the last move, it loses a column, but that is still recoverable. Without the wall correction the target sits at the paddle's column, so a sticky no-op could push the lag to two, which is the dangerous case, unless a wall arrives first to pull it back.

I'm checking the corner case where the ball is clipped at the left wall while a brick sits above it, since the trail and ball would then share a column and the bounce direction has to be tracked through the wall.

I'm checking the brick-strike case where the ball sits in the same cell as the trail at the left wall: the target comes out to 1, so the paddle should step right. I'm also looking at the trail-at-0 case with the ball at 1, where the target overshoots by one column but that lead is harmless.

I'm checking whether a paddle at column 2 can be one column ahead of a ball at column 1 with the trail at column 0, since then the wall-adjusted target would land it at 3 and the tracking would fail.

I'm checking whether a slightly negative trail offset at column 0 could tighten the wall case without creating a lead that's too large, since a paddle at column 2 with the ball at column 1 would be a problem.

I'm testing whether a trail offset of −0.6 at column 0 would be a softer fix than −1, since it would push the clipped-wall target to 0.6 and still clear the threshold. The margin looks too thin with a gain of 6, so I'm keeping −1 at column 0 and 10 at column 9. I'm also checking whether a paddle one column ahead could overshoot when the trail sits at 0 and the ball is at 1, and it looks harmless.

I'm checking the right-wall case with the trail at column 9: the bounce estimate gives no move, but the ball actually heads back to column 8. I'm considering a bounce-trail weight of 8 for column 9 so the paddle steps left there.

I'm checking the right-wall corner as well: with the trail at column 9 and the paddle at 8, a bounce weight of 9 gives the correct move right, while 8 would stall. I'll keep the weight at column c and accept that the same-cell case and the clipped-corner case both leave the paddle one column behind until the next wall corrects it.

I'm switching the bounce-trail weights at the walls to half values, so the corner cases land at ±0.5 and a threshold of ±0.25 separates them cleanly with a gain of 12. I'm not planning to do the same for the A units, since the integer cases already work there.

I'm thinking about whether the steady-state dynamics could fall into a deterministic loop when no bricks remain in the ball's path. A corner bounce sends the ball back along the path it came down, so the ball could retrace its route up to the top wall and back, with sticky actions and softmax being the only source of variation.

I'm checking whether a corner bounce could trap the ball in a two-cycle: if the path between two paddle hits has no brick strikes, the ball might simply retrace it forever when both bounces are corners, which lag-0 tracking tends to produce. Only sticky-action perturbations would break such a loop.

I'm checking whether sticky actions at direction changes break up the loops, and how long a bounce cycle runs before the step cap. I'm weighing whether straight bounces keep the ball moving more predictably than corner bounces do, since the horizontal motion repeats with a period of 20.

I'm checking how the ball's bounce period lines up with the horizontal period of 20, since the vertical cycle of 18 steps mixes phases with it and gives broad coverage of trajectories for straight bounces. Corner bounces just reverse the ball back along its path, so I'm considering whether I can make the policy prefer straight bounces at the critical step.

I'm now checking a design that prefers a straight bounce at the critical step: with the paddle already under the ball, a no-op keeps it there, and if a sticky action instead repeats the previous move, the corner bounce it produces is still safe.

I'm working through whether a target of exactly b when the ball is on row 8 with the trail on row 7 covers every paddle offset: a paddle already under the ball stays put, and one a step behind moves over. That makes most bounces straight and only the sticky-action cases corner, which should break up the retracing loops.

I'm checking how far the ball travels after a bounce before it gets back to row 8 for the next critical observation. Starting from the bounce column and heading one step in the new direction, the shortest flight (up to row 4, a brick strike, then back down) still takes about nine horizontal moves, so I'm asking whether that flight forces a wall contact before the next decision.

I'm checking the wall cases where the ball clips at column 9: starting from column 1 with a rightward step, the ball reaches the right wall after eight moves and stays there on the ninth. Then I'm looking at the paddle one column behind, which has to move right to meet it.

I'm now checking whether lag-2 states can arise from a sticky no-op right after a straight bounce, since the ball would then be two cells ahead of the paddle and need a wall to pull it back.

I'm checking whether a lag of 2 at the wall gets fully corrected: the ball stalls at column 0 while the paddle closes in, and after one more step it's back on target at column 1. I'm also testing lag 3, which the wall seems to recover in the same way, so every lag I've checked ends up at zero.

Wall bounces seem to pull the paddle back into sync, so a lag only matters if the critical moment comes right after a wall. The real worry is a lag of two or more that gets carried over from a sticky no-op right after a bounce. I'm wondering whether a critical-step target that sometimes favors a corner bounce would reduce that risk.

I'm checking whether a ball that bounces off the paddle could end up a step ahead of it, with a lag of two, when the bounce sends it back along a path. I'm noting that each flight has at least one wall contact, so the lag gets corrected before any critical moment, except when the wall clip comes right at the end. That edge case is the one still worth worrying about.

I'm checking that the paddle ends up within reach after a wall clip: if it's two behind when the ball hits the wall, it still ends up a lead of one or two in the new direction, which the next critical step can absorb. So only lags up to about three survive a clip, and a death needs two mishaps in a row.

Working through the opening phase: the ball starts at column 0 and the paddle at 4, so the paddle steps left to meet it, and then follows the ball along the bottom until the critical moment at row 8 with the ball at column 5.

I'm now covering the start position, where the ball sits at (0,3) and the paddle moves toward it. Then I'm setting up the special case: when the trail is on row 7 and the ball on row 8, I'd aim for the ball's column directly instead of the usual extrapolated target, though I still need to separate descending from ascending motion.

I'm now trying to pin down how to handle the critical step. The simplest fix is to drop the ball-in-row-8 weight for the A units, but the trail contribution in row 7 can't tell a descending ball from an ascending one, so I'm weighing gating the A units off whenever the ball is in row 8 and adding a separate term for that case.

I'm settling on three pairs of hidden units: the usual A pair turned off while the ball sits in row 8, a B pair that only switches on when the trail is in row 8, and a new C pair that turns on only when the ball is in row 8 and the trail isn't. That gives six hidden units in total. I'm weighing whether the C-mode straight-bounce preference is worth keeping over dropping it, since corner bounces risk retracing loops.

I'm checking the C-mode cases: if the paddle is one column off in the direction of the bounce, it should still move back to the ball's column, and if it's two columns off, the move lands it one column from the ball. The wall clip cases also come out right, since the target stays at the wall column. Next I'm going to verify the B-mode cases against the same checks.

I'm checking the bounce cases numerically now. For a straight bounce with the paddle on the ball's column, the paddle-side term comes out to about −1.5 at the right wall and +1.5 at the left, so the direction is correct. For a corner bounce, the difference lands at +0.5 or 0, which still points the paddle the right way.

I'm checking the bounce cases for the B units: with the ball one step off the paddle, the paddle-side term still comes out to about −0.5 at column 5 and −1.5 at the walls, so the paddle moves back the right way. I'm also checking the same-cell case at each wall, where the paddle should move inward and the ball's side term still points that way. Next I'm going to look at whether a paddle sitting elsewhere could come up, and I'm satisfied that after a bounce the paddle is always at either the trail or the ball column, so nothing new shows up there.

I'm checking where the brick-respawn rule and the row-8 gating actually collide. Bricks only sit in rows 1–3, so row 8 is only reached on a descent or just after a bounce. The catch is that right after a bounce the trail is in row 8 while the ball is heading back up to row 7, so a gate keyed only on the trail being in row 8 would fire on ordinary ascents too. The B gate needs both the ball and the trail in row 8 to avoid that.

I'm setting up the B-mode gates now: the ball-in-row-8 and trail-in-row-8 inputs go in with a large bias so the units only fire when both are true, and I'm checking that the pre-activation stays negative when either gate is off, with the margin M large enough to dominate the paddle term.

I'm setting up the C units now: their ball-side weight only applies in row 8, and they switch off when the trail is also in row 8, so they only handle the descending critical step. I'm checking that the gating margin M dominates the paddle and ball terms in each case.

Next I'm setting up the A units, where the ball's column carries twice the weight, and I'm working out how the row-8 cutoff interacts with that term.

I'm checking the gating margins for the A units: the ball-in-row-8 gate pushes A1 off and A2 on with a large weight, and the pre-activations stay well clear of zero in both cases. I'm settling on K = 8, which gives a margin of about 4 and tanh near 0.9993.

I'm settling the constants now, with K=16 for the B units so their margin is 4, and checking that the B terms stay well inside the gate margin M=1000. Next I'm listing the hidden units: A1 and A2, then B1 and B2, then C1 and C2. I'm also checking that the layer-two unit's pre-activation gives −0.964 when none of the A, B, or C units are active, and 2 when one is.

Next I'm fixing the output-layer scale so the two hidden-layer signals map cleanly to right and left logits, with the no-op logit held at zero. Then I'm starting to write the first-layer weights, indexed by cell and channel, beginning with the paddle channel.

Still writing the paddle-channel weights for the A and B units...

Still writing the weights for the ball channel...

Still writing the row 8 ball-channel weights for the B and C units...

Still writing the trail-channel weights for the A units...

Still writing the trail-channel weights for the B and C units...

Still writing the trail-channel weights for the A units...

Still writing the output-layer weights...

Still writing the output-layer weights...

