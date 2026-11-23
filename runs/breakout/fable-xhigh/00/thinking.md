I'm working out how to hand-design a policy network for MinAtar Breakout, starting from the game's dynamics. The ball's state is its position and one of four diagonal directions, with the paddle fixed on row 9. Each step the paddle moves before the ball, and the ball's new position gets clamped at the edges.

I'm checking the paddle-bounce rules: when the ball is at row 8 heading down, the paddle has to be at the ball's old column or the new one after its move, or the ball is lost. I'm working out where the ball lands and how its direction flips once it bounces off the paddle.

I'm settling on the bounce rule: after a hit, the ball's direction flips so it heads up, and the exact new heading depends on whether the ball's old column or its new column matched the paddle. That means the paddle only needs to cover one of two adjacent cells when the ball reaches row 8 moving down, which gives a tolerance of two cells. So the policy should aim the paddle at where the ball will arrive, not at where it currently is.

Now I'm checking the ball's path from the start: it reaches row 8 around column 5, so the paddle only needs to be near columns 5 or 6 when it drops, and at paddle position 4 that's easy to reach. I'm also thinking about the general case, where the ball bounces off the paddle, climbs through the bricks, and comes back down, with the paddle tracking its column one step at a time.

I'm noting that a brick hit only flips the vertical direction, so the horizontal heading carries through unchanged, and only walls or a paddle hit on the far side can turn it. That means a paddle tracking the ball's column should stay aligned as it moves. At the right wall the ball holds its column for one extra step, so the paddle can simply wait there. I'm now considering what the network will actually see before it chooses an action.

I'm weighing whether a simple tracker is enough: nudge the paddle toward the ball's next column, since the ball moves after the paddle. Then I'm wondering whether a fully predictive policy would do better, with a 32-unit hidden layer.

I'm checking whether simple tracking is enough to keep the paddle aligned with the ball. Since paddle and ball both move one cell per step, a paddle that starts aligned can stay aligned, though sticky actions occasionally add a one-step lag that the two-cell tolerance should absorb.

I'm weighing whether the paddle should aim at where the ball will be after its next move rather than where it is now. Targeting the next column means the paddle is already under the ball when it reaches the critical row, so a full reversal catches it. Targeting the current column works too, but leaves no margin if the paddle lags by one step.

I'm thinking about what happens when the ball's horizontal movement changes: a wall bounce means the ball holds its column for one step, so the paddle should wait, while a paddle bounce is where errors can creep in. Since sticky actions only repeat the last move, a paddle that is already tracking the ball's direction stays on target, and I can make the policy effectively deterministic by scaling the output logits up.

I'm checking whether simple tracking holds up when the ball moves away from the paddle: if the paddle falls a cell or more behind, the ball will reach a wall and turn back, which brings them into alignment again.

I'm realizing the paddle could end up two cells behind after a sticky action, and then it would have to chase a ball moving away at full speed, so it might not catch up before the ball lands. That makes me think aiming at the predicted landing spot is more robust, since the paddle gets many steps to reach it, even if computing that position with a 32-unit hidden layer is harder.

I'm now considering whether the landing position can be computed directly: for a descending ball below the bricks, the landing column is a fixed function of its column, row and horizontal direction, with wall reflections. I'm checking which linear features of the ball and paddle positions a 32-unit hidden layer could represent to capture that.

I'm working out the ball's wall behavior as a folded coordinate: it reflects off the edges and holds its column for one step at each wall, so its position repeats on a period of 20. For a descending ball at a given row, the landing column would then be a fixed function of where it is and its horizontal direction.

I'm working out the paddle target at the critical step: the ball's column there is the fold of its current column plus its horizontal direction times the rows left to row 8, and the paddle needs to be on that column or the next one. I'm also wondering whether the ball might hit bricks on its way back down, which would change the landing column.

I'm checking whether the ball can hit bricks while descending through rows 1 to 3 after bouncing off the top, since that would change the landing column. Once it's below row 3, though, the path is clear and my fold-based landing prediction holds.

I'm considering how far the paddle could drift during the ascent: if the ball is at row 4 heading down, the paddle gets about five moves before the critical step, so it could be as far as nine cells off. That means tracking the ball's column during the ascent as well, not just predicting from the descent.

I'm picturing the ball's path after it bounces off the paddle: it climbs to row 4, takes one step to hit a brick, then drops back to row 8, which adds up to roughly ten columns of horizontal travel. I'm checking whether a paddle that simply tracks the ball can stay aligned over that whole stretch, with sticky actions as the main risk.

I'm weighing whether to track the ball's x-position directly while it's ascending, since the bounce point depends on bricks and can't be predicted. Once it's descending below the brick rows, I'd switch to the landing prediction. A simpler universal target, just the ball's current column with a one-cell lag tolerance, is the fallback, and I want to check how it holds up under sticky actions.

I'm weighing a simple tracker against the landing-prediction design, and I'm about to work through how the tracker would be built: the hidden unit would compare the ball's column with the paddle's column, giving a signed difference that picks left, right, or stay.

I'm settling on a two-unit design for the tracker: one unit fires when the paddle is left of the target and one when it's right, so the logits can pick left, right, or stay. The target is the ball's x-position, but its direction needs care at the walls. When the ball stalls on an edge column, its direction has already flipped, so I'd infer the sign of its next move from that rather than from the raw difference.

I'm settling how the ball's next x-position depends on its trail: away from the walls it's the current column plus the last horizontal step, folded back at the edges. When the ball is sitting on a wall column, the trail matches the current column, so the direction is taken as inward, giving column 1 at the left wall and column 8 at the right.

I'm checking the linear extrapolation of the ball's next column, 2*bx - tx, and it's off by one at the walls: at the edges the ball stalls, so I need corrections. Since the ball and trail positions are encoded separately, I'm trying to see whether additive per-cell terms f(bx) + g(tx) can fix those cases.

I'm checking the remaining edge cases of the wall correction: at the right wall the ball's column should be 17 instead of 18 for the folded term, and the left wall needs the matching fix at 0 instead of 1, which works out consistently with the neighboring cells.

I'm checking whether full reversal is actually desirable: if the paddle always sits exactly under the ball's next column, the ball just retraces its earlier diagonal, which would send it back toward bricks it already hit.

I'm checking whether full reversal could trap the ball in a cycle: it might retrace a path up to the top wall and back down to the paddle without hitting any bricks, which would stall scoring until the step cap.

I'm checking whether full reversal could trap the ball in a cycle: after a paddle bounce, it could retrace the same path up to the top and back to the paddle without hitting any bricks. Sticky actions might break that loop now and then, but the step cap would still stall scoring. When all bricks are cleared, a refill only happens at the paddle-row check, so that's when the path changes.

I'm now weighing how a sticky action might cause the paddle to lag one step, which could turn a clean reversal into a different bounce. I want to see whether a no-reward loop can form and how often sticky actions would break it.

I'm thinking about how a sticky action could make the paddle overshoot a target and then correct, which could repeat. The policy can't see the previous action, so it has to rely on the paddle position and keep its motion predictable.

I'm checking the catch window at the critical step: if the ball is at the wall column, the paddle's allowed landing cells shift, so the tolerance has to account for that.

I'm settling on a policy that parks the paddle under the ball's landing cell and then holds still, since a sticky repeat of a no-op is harmless. The only real risk is overshooting on arrival, so it's worth getting there early.

I'm considering whether the paddle should target either of the two candidate cells at the critical step, since landing within one cell of the predicted spot is acceptable. During the ascent, I'd lean toward aligning the paddle with the ball's x-position, because the eventual landing cell depends on where the ball reverses at a brick.

I'm reasoning that tracking the ball's column during its run means the paddle keeps moving the same way each step, so sticky repeats don't hurt. The risk is only when the ball reverses direction at a wall, where it stalls for a step before bouncing back.

I'm weighing whether to lead the paddle during the ascent instead of tracking the ball's column exactly. If the ball bounces off a brick at some row, it keeps its horizontal direction, so its landing column depends on how many steps pass before it comes back down to row 8.

I'm working through where the ball lands by counting steps: a brick hit at row r adds a fixed number of moves before it returns to the paddle row. I'm also checking how the ball behaves when it reaches the top wall, since it stalls there for a step and then starts back down.

I'm now considering whether tracking the ball's x-position during the ascent is good enough, since the landing column depends on which brick the ball hits and at what row.

I'm working through the paddle's timing at the brick-bounce reversal: with the paddle tracking the ball, it ends up at the predicted landing column exactly when the ball reaches row 8, with one spare move to spare.

I'm working through the paddle's behavior at a wall bounce: the ball stalls for a step at the edge before reversing, so the paddle's intended action changes and a sticky repeat could knock it out of sync.

I'm looking at what happens at the right wall: the ball stalls there for a step, so the paddle can press "right" and simply stay put, since moving into the wall is a no-op. The action sequence then flips from right to left once the ball starts back, and with a sticky repeat the paddle could be left one cell behind as it starts tracking the other way.

I'm weighing whether the paddle should anticipate a wall bounce rather than chasing the ball into the wall. A one-cell lag still lands within tolerance, but two stuck actions in a row at a reversal would be fatal, so I'm looking at whether leading the paddle toward the wall would give more slack.

I'm considering whether the paddle could anticipate the ball instead of chasing it. If the ball is heading right at x=7 and will bounce off the wall, the paddle could hold near x=8 and wait there rather than following the ball into the edge, which gives it more time to arrive. Then I'm estimating how often two sticky actions in a row would break a reversal: roughly a 1% chance per direction change, which over a long episode adds up to a real number of failures.

I'm weighing how far this design needs to go: the simple tracking policy might already reach around 1,000 steps, but pushing toward the 10,000-step cap would call for landing prediction. I don't have a way to test code, so I'm leaning toward a simpler, verified design over a fancier one that could hide bugs.

I'm working out how to express the descending ball's landing column: with the ball's unfolded position u and direction dx, the predicted column at row 8 is the fold of u plus dx times the remaining steps, and the next-step target is the same expression one step further.

I'm checking whether the ball's direction can be read from the ball and trail cells: the horizontal sign comes from their x difference, but after a brick hit the ball and trail share a row, so I can't tell from those two cells alone whether it's now heading up or down.

I'm checking which way the ball is moving right after a brick hit, since the ball and its trail then share a row and that alone doesn't settle it. At the paddle row or the top wall the direction is clear, but in the middle rows the answer depends on which side the brick was hit from, so I'm leaning toward row 3 meaning the ball is descending.

I'm now checking the ambiguity at each row: a ball sitting in the same row as its trail after a brick hit could be going either way, depending on which side the brick was struck from. Row 3 and 4 resolve to descending, but rows 2, 1 and 0 can each mean either direction.

I'm tracing the brick-collision branch: when the ball lands on a brick cell, the strike flag gets set, and if a strike was already in progress the ball just passes into the brick without bouncing. That means a ball coming down at row 0 that hits the row-1 brick flips to ascending, which is the case I still need to sort out.

I'm checking the edge cases around the top wall: a ball descending at row 0 that hits a row-1 brick flips to ascending but stays in row 0, and the next step it flips back to descending, so it can bounce along the top row erasing bricks at two steps each. I also notice that a ball sitting on a brick cell after a strike just passes through without bouncing, which matters for the direction logic.

I'm noting that the vertical direction can be read from the ball and trail rows when they differ, with a same-row case resolved by the row number: at rows 4 or above it reads as descending, and at the paddle row it reads as ascending. That lines up with the reset position, where the ball starts descending from row 3.

I'm expressing the descending ball's landing column as a linear function of the ball and trail positions, since the direction is their x difference. That makes the target a product of that difference and the rows remaining to row 8, which a single first layer can't compute directly.

I'm looking at the diagonal identity as a way around the product: for a ball moving down-right, bx - by stays constant along its path, and for down-left, bx + by does. Since the trail sits on that same diagonal, the trail cell gives me the invariant without needing the direction as a separate input.

I'm weighing whether the product term can be avoided: for a ball moving right, the landing column is 8 + (bx - by), and for a ball moving left it's (bx + by) - 8. So the direction is the only missing piece, and it would decide which diagonal to use.

I'm now setting up the four target functions, one per direction case, each a fold of a linear expression in the ball's cell, and I'm planning to compare each against the paddle position with a steep tanh unit in the first layer.

I'm setting up the layer-1 units so each direction case gets a pair of comparisons against the paddle, and then a second layer that selects the right case and combines them. The remaining question is how to detect the horizontal direction from the ball and trail positions, including the wall-stall case.

I'm working out a landing column for the stalled case, where the ball and trail share column 9 and the direction has flipped to leftward. I'm checking whether the unfolded position and direction still give the right target when the ball sits against the right wall.

I'm checking how the sign of the horizontal direction works out at the walls: at column 0 with the trail also there, it should count as rightward, and at column 9 with the trail also there, as leftward. A simple difference of ball and trail columns gets those edge cases wrong, so I'm looking at whether a small offset on the edge columns can fix it.

I'm now working out the vertical direction the same way: a sign term from the ball's row compared against the trail's row, with the same-row cases settled by the row number.

I'm defining the vertical direction test as a shifted row difference: the ball's row plus a half offset, compared against the trail's row. That gives the right sign for equal rows, one row up, and one row down, and near the paddle row it flips correctly.

Now I'm settling the vertical direction with a shifted row test, giving two units that output ±1 for the up/down sign. After that I'll set up four comparator pairs, one per direction case, and combine them in a second layer.

I'm now building the layer-2 gates: each direction case combines its direction signals with its comparator into a ±1 AND, and the right and left logits are sums of those gates.

I'm settling on the right and left logits: the right one is 2M when a rightward case is active, the left one is 2M when a leftward case is active, and the noop logit is a constant M. That gives the right move a clear margin over the others. I'm still deciding what to do with the other actions, whether they should just be noops or get strongly negative biases, since sticky actions can repeat the previous move.

I'm setting the comparator inputs: each first-layer unit gets K times the target column on the ball's channel, minus K times the paddle position on the paddle row, with K around 8 so the tanh saturates cleanly.

I'm now defining the case-by-case target columns for descending-right, and I'm planning to check how they stack up against the paddle position.

I'm now weighing the two possible landing targets for the descending case, L or L'. Aiming at L means a noop works if the paddle is already there, so I'm checking how robust each choice is against the paddle's current position.

I'm comparing the two landing choices for the descending case: aiming at L means a noop works when the paddle is already there, while aiming at L' means the same holds for that column. The trouble is sticky actions: if the paddle arrives just at the last step, a leftover move can carry it past the target, and whether that slip lands it on L or L' depends on which side it came from.

I'm weighing whether to aim the paddle at L or L' for the descending case. Landing on L only flips the vertical direction, while L' reverses the ball fully, and at the wall the two coincide, so the ball just flips vertically again. I'm thinking about which outcome keeps the ball from looping without bricks.

I'm looking at the vertical motion now: the ball alternates between the paddle row and the top, so I'm checking whether a pure bounce pattern without bricks would cycle forever, and whether its combined period with the horizontal one is long enough to matter.

I'm checking whether a pure bounce path, with only the vertical flip at the paddle, could avoid every remaining brick. The combined motion visits every cell with matching parity over the 180-step cycle, so any brick left anywhere would eventually be hit.

I'm checking the full-reversal option: the ball would retrace its incoming diagonal, so if a brickless path came from the paddle and reached the ceiling, it would bounce back to the same paddle spot and repeat in a two-step loop. Vertical-flip-only catches avoid that, since every cell gets visited within the 180-step cycle.

I'm weighing whether the vertical-flip catch is the safer default: it keeps the ball moving through every cell over the full cycle, so no brickless loop can trap it, whereas a full reversal can bounce back and forth between the same two paddle spots. Occasional overshoot to L' is acceptable, since random perturbations break any loop anyway.

I'm checking how the paddle stays one step behind the ball after a vertical-flip catch, and whether that offset persists as the ball ascends in the same horizontal direction. It looks like the gap only closes when a wall event occurs.

I'm checking how a one-step lag behaves under sticky actions: with full reversal the paddle ends up directly under the ball and stays in sync, but with the vertical-flip catch it stays a step behind, leaving no slack against a single mistimed move.

I'm working out the landing targets for the ascending ball: for each possible brick row, the paddle column depends on the ball's current x, its vertical position, and the horizontal step, with the stall at the walls folded in.

I'm working out where the paddle should land for each possible brick row: a bounce at row r takes y + 7 − 2r steps in total, and the landing columns for successive rows are offset by two.

I'm considering a simpler target for the ascending ball: aim for the earliest possible return, at brick row 3, as T = fold(u + dx·(y+1)). If the ball actually goes higher, the landing shifts by two columns but also gives two more steps, so the paddle keeps its slack in the worst case.

I'm settling on aiming for the earliest possible bounce, row 3, since any later bounce just shifts the landing spot and gives extra steps to cover it. For the ascending ball at column x with horizontal step dx, I'm computing the target as the folded column of u + dx·(y+1) when it's still above row 4, and adjusting the offset for the rows below that.

I'm checking the ascending case for a ball low on the board: after a bounce, the landing column depends on how many steps remain before the ball returns, which works out to 9 minus its row. So I'm setting the target column as the folded value of the current position plus that step count times the horizontal direction, for rows up to 4, and I'm working out what happens with the row-1 case separately.

I'm settling the ascending targets: for a ball at row 1 the return takes 10 steps, at row 0 it takes 9, and from row 4 up it's the earlier-bounce offset. For the descending case I'm using fold(u + dx·(8 − y)), and I'm noting that rows 0 to 3 could send it back up after a brick hit. Next I'm checking how much time the paddle has against the distance it has to cover at the bounce moment.

I'm now counting the paddle's moves against the ball's path: the ball goes up from row 8, stalls at the brick row, comes back down to row 8, so there are ten observations and ten actions in all, with the critical one last.

I'm checking the paddle's slack after a vertical-flip catch: it starts one cell behind the ball's travel direction, so reaching a target nine cells ahead means ten moves in ten actions with no room to spare. I'm about to redo the same count in folded coordinates.

I'm checking the paddle's slack once more: if it starts one cell behind the ball, a wall fold in the path makes the folded distance shorter than the unfolded one, so the target comes out closer than the worst case.

I'm checking the paddle's slack in both catch cases: a full-reversal catch leaves at most a distance of 9 with 10 actions, so at least one step to spare. Hitting bricks higher up gives more time, and the target shifts by at most two columns per two steps, so the margin holds or grows.

I'm settling on the slack analysis: with the earliest-landing policy, the paddle keeps at least one step to spare in the worst case, and a longer path only adds time. The risk comes when the action switches direction, since a sticky action can delay the first step of the new heading.

I'm working out the failure odds: if I'm already waiting at the landing spot, a sticky no-op only costs one step, which the single step of slack covers. Only the rare worst-case geometry combined with a second sticky action would break it, so the per-catch failure chance looks very small.

I'm weighing whether to keep waiting at L with a noop at the critical step, or to use the last bit of slack differently, such as choosing between a noop and moving to L' so the next target ends up closer. Moving adds loop risk, so I'm leaning toward the simpler noop at L.

I'm settling on the critical-step choice: if the paddle is already at the landing spot L or the mirrored spot L', a noop keeps it in place. If it's short, it moves toward L, and if it overshot, it moves back, though a sticky repeat of the previous move could still push it past L.

I'm setting up the comparators with separate thresholds: the paddle moves right when it's left of the lower bound T_lo for the ball's cell, and left when it's right of the upper bound T_hi. For the critical descending case at row 8, T_lo is L and T_hi is L', so the paddle stays put anywhere between them.

I'm now checking the ascending target for when the ball is above row 4, using the folded position plus the horizontal step over the steps it takes to get there. I'm working out how the wall fold handles negative positions for a leftward direction, since that determines where the ball lands.

I'm checking the folded target for the rightward case: the wrap has period 20, so values past 19 fold back to 0, and the stall at each wall keeps the mapping consistent on both sides.

I'm checking the folded target for an ascending ball at row 4 and seeing that it lines up with the descending case once the ball stalls at the wall. I'm now working out where the ball lands if there's no brick at row 3 in that column, since that sets the next ascending target.

I'm checking the descending case for a ball in rows 0 to 3, since it might hit a brick from below and bounce back up before reaching the paddle. The target I had assumed is only valid if the path is clear, so that case needs a separate look.

I'm checking the ascending-ball case as well: if the ball is heading up through rows 0 to 3, a brick hit could flip it back down, which would lengthen its travel time. I'm taking the earliest-landing target as the baseline and noting that any extra delay shifts the target by no more than the number of added steps, so the slack still holds. For a ball in the same row as its trail, I'm treating it as descending for now and working out the target from there.

I'm checking the case where the ball is actually moving up at row 2, since a brick at row 1 could let it pass through and keep climbing. That would mean a longer trip before it returns to the paddle, so my earlier target is off by a few cells. The paddle will only be a step or two wrong, and the next observation will show the ball rising, which corrects it.

I'm checking the row-0 case where the ball is on the same row as its trail. If it came off the ceiling it's descending and the landing is eight steps out, but if it struck a brick from above it would be ascending again at row 0, so that case needs its own look.

Now I'm checking the step where the ball hits the ceiling on row 0 and bounces back down, which should make the landing eight steps out, though it turns out to be nine once the stall at the wall is counted, so I'm accepting the one-step error as minor. The architecture comes together as 4 direction cases with 2 comparators each, plus the horizontal and vertical direction units, giving 10 first-layer units feeding 8 AND units, with room for extra units to handle a 2-cell dead zone at the critical row.

I'm checking the reset state next: the ball starts at the trail cell on row 3, and the sign tests on its column decide whether it heads right or left and that it is descending. For the paddle-bounce state, I'm setting up the direction from the sign of the horizontal difference between the new position and the previous one, with the ball now moving up from row 8.

I'm realizing the trail can't tell a vertical-flip catch from a full-reversal catch: after a reversal the ball's last move looks like dx, but it's actually heading back toward L, so the horizontal-sign test would pick the wrong direction.

I'm now checking the case where the ball has just bounced off the paddle at row 8, since the trail alone can't tell a vertical flip from a full reversal. The paddle's position does: if it sits on the trail's cell the direction is the trail's horizontal step, and if it sits on the ball's cell the direction is reversed. I'll accept one possibly wrong action in that single observation, since the next step makes the direction clear.

I'm weighing a fallback for the just-bounced state: if the paddle sits on the ball's own column, a full reversal has happened and the ball is heading back toward the trail's side, so I'd aim at fold(bx - 9dx) instead of the trail-direction target.

I'm now considering a fifth case for the just-bounced state, where the ball is at row 8 heading up and the paddle sits on the ball's own column, which means a full reversal. Ball and trail sharing row 8 is what identifies that state, so the ascending check at row 8 separates it from everything else.

I'm checking the just-bounced row-8 state, where the ball is heading up and the trail has the same row. Here the comparators can't infer direction from the paddle alone, so I need to separate the vertical-flip case from the full-reversal case.

I'm now working out the full-reversal target for the just-bounced state, where the paddle sits on the ball's own column. The ball would then head back up-left, so the aim is fold(bx − 9), which comes to 8 − bx for bx ≤ 8 and 0 when bx = 9.

I'm working through the just-bounced row-8 case with the paddle on the trail's cell: the ball then continues rightward, so the target folds to 10 − bx for bx ≥ 1, and the wall-stall edge case at column 0 needs a separate check.

I'm working out the just-bounced case where the ball is on row 8 heading up and to the right. If the paddle sits on the trail's cell, the target is 10 minus bx, so the move is right for small bx and left once bx reaches 6. If the paddle sits on the ball's cell, the target is 8 minus bx, which pushes right for bx up to 3.

Now I'm setting the thresholds for the just-bounced case: for small bx the ball keeps heading right, so the right-move threshold sits just above bx, while for bx from 6 upward both paddle positions point left, so the left-move threshold drops below bx.

I'm settling on the just-bounced row-8 case with a separate low and high threshold on the paddle position, which handles both catch types. Then I'll extend that to all four direction cases over every ball cell, which means writing out the per-cell thresholds for each table.

I'm now filling in the weight values for all eight direction units over the 100 ball cells, which is a lot of numbers but manageable by exploiting the mirror symmetry between UL and UR. Each row gets a block of ten values per unit, written into the appropriate channel-3 entries.

I'm now writing the comparator weights as plain integer tables first, then scaling each column by K, so that the bias for each comparator becomes -0.5K.

Writing the comparator and output weight formulas...

Now I'm settling the output layer: summing the right-move and left-move signals over the direction cases, then scaling so the right-move and left-move logits dominate the no-op logit when a case fires.

Setting the comparator gain and the layer-two gains so that each unit saturates cleanly: with the scale at 8 and gain 4, the direction units come out near ±0.9993, and summing the four case units gives about -4 when none fires and about -2 when one does.

Now I'm formalizing the state: the ball's position and direction, the paddle's column, and the previous action, which is hidden. The agent's intended action only goes through with probability 0.9, since sticky actions can repeat the last move. Next I'm splitting the play into five phases: just-bounced, ascending, the brick zone, descending, and the critical row 8 step. At the critical step, I'm aiming for the earliest landing column, with a dead zone where staying still is enough.

Now I'm weighing which catch position to wait for at the critical step. If the paddle is already at the vertical-flip landing column, the ball will carry on from the neighboring column, so I need to check how far the paddle then sits from its next target.

Now I'm checking the slack for the vertical-flip case when the ball is moving right: starting at column 1 leaves only one spare action, which is the tightest of any landing column.

Now I'm checking the slack for the full-reversal case: the ball's target folds to 8 minus its column, and the paddle has to reach it within the same ten actions, which leaves less room than the vertical-flip case.

Now I'm checking the slack for each landing column in the dx=+1 case, comparing the vertical-flip distance against the full-reversal distance. Full reversal is tightest at column 9, where the ball has to travel all the way back to column 0 and the paddle is 9 away. Vertical flip gives the most room around columns 3 to 4, while full reversal gives the most room around column 4, where its distance is zero.

Checking the slack per landing column, I'm noticing that sending the ball back with a full reversal is the tighter choice near the left edge, while a vertical flip leaves the least room near the middle. Splitting the choice by landing column, with full reversal for the early columns and vertical flip for the later ones, would give at least four spare actions every time, far more than the one I had before. I still need to check whether that position-based rule can loop back on itself.

I'm noticing that the ball's landing column decides which bounce rule to use. Landing going right from column 4 or beyond sends the ball on rightward, while a landing at column 3 or less sends it back the way it came. Going left, the cutoff shifts so that columns 6 and up reverse and columns 5 and below carry on, so the ball always ends up heading toward whichever side is nearer.

I'm checking whether a brickless path could cause a loop: if the ball crosses the full width and reaches the ceiling without hitting anything, the x-travel adds up to about 17 steps, which I need to compare against the paddle's reach.

I'm now checking whether the bounce rule can trap the ball in a loop. If the ball retraces a brickless path back to the previous catch spot, landing there in reverse and getting the same full-reversal rule again would repeat forever.

I'm tracing an example where the ball leaves x=6 heading right and bounces off the ceiling without hitting any bricks. Its path comes back down to row 8 at x=3 going right, which lands in the full-reversal case, so I'm checking whether that sends the ball back along the same path.

I'm checking whether the full-reversal rule can lock the ball into a loop: if the path back up is brickless, the ball can return to the same catch spot going the opposite way and get the same rule again. Sticky actions might break that cycle by flipping one of the paddle's moves, but only after several rounds.

Now I'm estimating the expected escape time: with a 10% sticky chance at each critical step in a pure FR-FR loop, the loop should break within a few catches, though the exact figure depends on how many catches take place per cycle.

I'm weighing whether a pure full-reversal policy could trap the ball in a 2-cycle, which would waste roughly 170 steps before a sticky action breaks it. I'm also considering a pure vertical-flip policy instead, which has at least one spare action in the worst case and visits every cell within 180 steps, so no loop is guaranteed to persist.

I'm considering whether a pure vertical-flip policy still leaves a tight case: landing at column 1 going right gives only one spare action, and the corner landing at column 9 going left is similarly tight. I'm wondering if using full reversal just in those extreme columns would widen the slack there.

I'm considering using full reversal only at the edge landings, like going right from column 1 where it cuts the distance from 9 to 6, and maybe column 2 as well. The catch is that a full-reversal retrace could bounce the ball back and forth between the same two spots, so I need to check whether the reversed landing point also calls for full reversal.

I'm checking whether full reversal is actually reversible here: the ball retraces its path, but stalls at the wall make the mapping only approximately time-symmetric. A full-reversal landing at L' would send the ball back up through the cell it came from, so the retrace might not line up exactly.

I'm noticing that the retrace isn't an exact reversal, since a full-reversal landing shifts the path over by one diagonal. To test the loop example properly, I'm tracing the ball's positions step by step from the departure at x=6.

I'm tracing the ball through the full reversal at column 3 and landing at column 4, with the path bouncing back and down to row 8 at column 7 heading left. That gives a new landing point of column 6, so I'm checking whether it retraces the original departure from column 6 going up-right.

I'm now testing whether restricting full reversal to just the extreme landings would break the systematic 2-cycles, since two FR endpoints are what close the loop, and I'm checking the corner case at column 1 going right.

I'm checking the unfolded position: starting from x=1 and moving 17 steps left gives −16, which folds back to column 4. I'm now trying to pin down which direction the ball is travelling at that folded point, since the sign of the fold determines whether it moves toward or away from the paddle.

I'm testing whether a full-reversal landing at column 4 going left, with its neighbour at column 3, creates a loop, and it doesn't since that pairing takes the ordinary vertical-flip rule. For a two-cycle both endpoints would have to use full reversal, so I'm checking whether restricting it to the extreme landings rules that out, starting from the brick at row 3.

I'm checking the bounce at row 8 when the ball comes down at x=9 going left, which lands on the wall-type case, and at row 7 it lands at L=8 going left, so neither one is an extreme landing that restricted full reversal would touch. That means no immediate 2-cycle shows up under that rule, though longer loops are still possible and hard to rule out fully. Next I want to estimate how often a pure vertical-flip policy runs into trouble, starting from the distance to the paddle for each catch position.

I'm weighing how a pure vertical-flip policy fares: each catch gives a slack of 10 minus the distance to the next target, and a sticky action that forces a wasted step eats one unit of that slack. Reversing the previous move costs two steps, while stalling on arrival costs little unless the ball is close to its critical point.

I'm checking the paddle's behaviour once the ball is close to its target. A sticky action that makes the paddle overshoot by one step, then a correction that overshoots the other way, makes the chance of failure drop off roughly geometrically. The paddle only ends up outside the two critical landing cells if that chain of mistakes runs long enough at the critical action.

I'm working out the failure odds for slack of one: losing two steps at the start is about 1%, and losing exactly one still lands the paddle on the target on time, since that final move continues the same direction and carries no sticky risk. If there's no loss at all, the paddle reaches the target a step early, so at the critical observation it's sitting on the cell with a noop intended.

I'm checking where the paddle stands relative to its target when the ball reaches the critical cell. The question is whether a sticky action would push it one step past the target and off the cell it needs to cover.

I'm checking the paddle's approach in the wall case: if it reaches the target moving right and overshoots, it stays put at the wall, so that's safe. In general, an overshoot is harmless only when the paddle keeps moving in the ball's landing direction, and it goes wrong when the paddle is moving against it, except at a wall.

I'm working out how the paddle's overshoot risk depends on the landing spot. For a start at x0=1 heading right, the target is 9 with the ball arriving left, and the same reasoning applies to x0=2 heading to 8. The danger is concentrated in the tight-slack cases, where the paddle arrives exactly on the critical step and overshoots only when it's moving against the ball's landing direction.

I'm now checking the pure vertical-flip policy case by case, starting with the ball descending to the right and the paddle waiting at column 9. There the landing point is 9 and the target folds to 0, giving a slack of 1, and I'm asking whether a ball going right can really arrive at that cell.

I'm tabulating the slack for each landing position: column 8 going up-right leaves a slack of 3, column 0 leaves 1, column 1 leaves 3, and the remaining columns from 2 to 4 leave larger slacks of 5, 7, and 1 as the distances shrink.

I'm tallying the slack values across the landing positions: four of the twenty configurations have slack 1, at the two edge columns for each direction, and the rest have larger slack. That puts roughly a 20% share of cycles at slack 1, where the failure chance is around 1% each, so the per-cycle risk from this is only about 0.2%.

I'm weighing the improvement options now, starting with full reversal at the extreme landing cells to shorten the paddle's distance. For the case where the ball descends rightward and the paddle waits at column 0, I'm considering moving right to column 1 so the ball goes up-left under that rule.

I'm checking whether a full-reversal tweak at the corner landing could help, since the paddle is already sitting on the cell where the ball arrives. Once the ball is heading into the wall at column 9, the target is forced to 0 with a slack of only 1, so I'm asking whether any earlier adjustment could keep the ball off that corner.

I'm checking whether the corner case can loop back into itself: if the ball goes up-left from (9,8) and meets a brick, it could return to a corner landing at column 0 with slack 1 again.

I'm checking the corner-bounce option now: a ball rebounding off the wall at row 3 could send it back into a corner landing, so the slack-1 problem might recur. I'm also looking at reducing the start-up loss by having the paddle already move in the new heading direction at the critical step, so a sticky action doesn't cost anything, but the wall-clamped case doesn't benefit from that.

I'm checking whether a full reversal at the L=0 landing helps, since moving right to column 1 would put the paddle already heading in the ball's new direction. That would cut the failure odds there from about 1% to roughly 0.1%, because only the critical action itself carries sticky risk. The corner case at column 9 has no such fix, since the paddle's wait at 9 has to stay a noop.

I'm checking the corner case again: with the paddle already at 9 and intending a noop, a sticky action on the next step could still pull it back, and I'm asking whether the slack really is 1 there.

I'm checking the corner-to-corner case: if the ball goes up-left from (9,8) and comes back down to land at column 0 after nine moves, the paddle has to cover nine cells in ten actions, so the slack is still just 1.

I'm checking whether the corner case can be avoided: if the ball bounces off the row-3 brick, it lands on column 0 with slack 1, but if it bounces higher, the target shifts by two as time goes up by two, so the slack comes out larger. That makes the failure risk from corner landings depend on where the bricks are, and I estimate it at roughly 0.0005 to 0.002 per cycle once the full-reversal fix is applied to the non-corner extreme cases.

I'm checking the expected-failure estimate over 700 cycles, which gives roughly a 50–70% chance of surviving to the cap, and I'm thinking about whether the hand-computed tables are reliable enough to trust.

I'm now checking the remaining edge cases in how the ball's trail tells me its direction, including the bricks and wall-clamping rules that could shift the landing point.

I'm working through the remaining cases where the ball hits the walls or the ceiling, tracking how the trail reveals each ball's horizontal and vertical direction, including the corner at (0,0).

I'm matching the ball's trail to its direction in the remaining cases: a wall stall, a brick strike from below with a wall bounce, a ceiling bounce, and a paddle hit, and I'm noting that a brick struck from above gets read as descending, which I'll accept.

I'm checking the remaining bounce cases against the trail: the paddle hit sends the ball down-left when it comes in from the right, and the row-8 ascending check comes out to a -0.5 shift, so the direction reads correctly.

Writing the weight-layout code for the Dx unit now...

Still setting the weights for the Dx unit, filling each column's ball and trail cells with the column's value and its negated target; then I'll scale the whole column by 8. Next up are the paddle comparator weights on row 9.

I'm setting up the lookup tables for the main policy, working out for each case and ball cell what the paddle's target should be, with a dead zone on the critical row and a preference for full reversal in the extreme landings.

I'm now looking at the ascending bounce case, where the paddle's position changes what the target should be. For the descent toward the left edge, I'm considering setting the target to the paddle's landing cell, so the paddle is already heading into the ball's new direction and the sticky-action risk drops.

I'm checking the special case where the ball lands at the left wall with a rightward heading, since the target would be forced to the paddle's own landing cell and I want to see what that does to the sticky-action risk.

I'm checking the leftward landing cases here: the ball at column 0 after a wall stall is heading right, so the paddle's best target is the cell it will land on, column 1. For the mirrored right-side case at column 9, the target should be column 8 for the same reason.

I'm checking the mirror case on the right: with the ball landing at column 9 heading left, the paddle sitting at 9 leaves slack 1, but moving to 8 early gives slack 4. I'm also weighing the next-worst landing, column 1 heading right, to see how much slack it leaves under each option.

I'm weighing whether the full-reversal preference should extend to the next-worst landing, column 1 heading right, where the slack is only 3 with the paddle staying put. I think 3 is still safe, so I'll keep the reversal rule limited to the true extremes to avoid creating loops. I'm also wondering whether the forced reversal at column 0 could keep recurring on a cycle that never clears.

I'm checking whether a brickless orbit that includes a full-reversal step could keep cycling, since the ball would return to the extreme landing each time. I think sticky actions should break any exact period, because the reversal step itself has about a 10% chance of falling back to the ordinary target, so I'm willing to accept that risk.

I'm now working through the cycle more carefully: a brickless orbit shifts the unfolded landing position by −2 each time, so the landing states only cycle through one parity class. I'm checking which landing state would count as the extreme case where full reversal applies.

I'm checking the cycle more closely: with only the paddle-bounce shift, each brickless return moves the landing state back by 2, so the landings stay in one parity class and periodically hit the extreme cells where full reversal would apply.

I'm tracing how the ball's unfolded position moves after a full reversal: each brickless return shifts it by 17 steps, so the landing cell goes from 0 to 1 and then keeps stepping through odd values. That puts it on the corner cells at 9 and 19, where the wall forces the reversal again.

I'm checking whether the two parity classes of states split the cells evenly, since each interior cell has four states that sit on opposite parities.

I'm assigning each row a pair of phase values, one for the downward pass and one for the upward pass, so every interior cell gets four states split evenly between the two parities.

I'm checking that the pure paddle-bounce orbit can't loop forever without a brick hit, since the full-reversal steps flip it to the other parity class where it keeps covering every cell. I'm also turning to whether the full-reversal target, set to the landing cell, holds up in the transitions.

I'm weighing whether the dead zone at the critical row should cover both the current landing cell and the next one. If the paddle is already at either cell, holding still is safer than moving, because any action the game actually executes will keep it inside the catch zone.

I'm settling on a single dead zone at the critical row, covering both the current landing cell and the next one, with the full-reversal extremes keeping the same zone and just preferring the far cell.

I'm now handling the cases right after a bounce off the paddle at row 8. The ball's true heading has to be read two ways, depending on whether the paddle made the ordinary catch or the full reversal. Then I'm setting the ascending-row targets, each one offset from the ball's folded position by a number of steps that depends on the row.

I'm settling the ascending-row offsets: the row-3 case comes out to 6 steps, row 2 to 7, and row 1 to 10 once the ball has to pass through the ceiling stall and come back down the full column.

I'm now setting the descending-row targets: the ball needs 8 − y steps to reach the paddle row, so the target is the folded landing position x ± n. When the landing would sit on an extreme cell, I'm preferring the far cell instead, using the same dead zone as before.

I'm now asking whether the full-reversal preference should carry over into the ascending-row prediction too. If the predicted landing hits an extreme cell, I'd use the far cell there as well, so the target doesn't flip back and forth as the ball turns around.

I'm defining the target for the upper-middle rows as a function of the predicted landing column, with the same far-cell preference at the extremes. Where the landing would sit at column 10 or −1, the target moves to the far cell, so it stays consistent across the turnaround.

I'm checking the edge cases where the ball's unfolded landing position hits an extreme, like u = 20 or u = −11. Those can't actually occur given the paddle bounce and the wall clamping, so the corner rule only needs to cover u = −10, where the landing cell is 9 and both cells coincide.

I'm going through the fold mapping for the descending targets: positions 10 through 19 reflect back to 9 down to 0, and the negative side reflects up through 0 to 9. I'm also applying the far-cell adjustment so that 10 maps to 8 and −1 maps to 1.

I'm working through the landing cell for the ball at row 8 heading down-left from the right wall. Its predicted landing is 10, which gets pushed back to 9 by the wall, so the paddle should aim at 8 and treat a hold there as the full-reversal case. Once it bounces, the ball goes up-right from (8, 8), and I'm starting to track its position and trail from there.

I'm now working through the just-bounced tables for the upper-right case, where the ball has moved right from column b. For the paddle bounce at row 3 the unfolded target is b + 9, and for b = 1 that lands on 10, which gets the far-cell preference and goes to 8.

I'm tabulating the upper-right just-bounced cases, where the ball has moved right from column b and the paddle target comes from shifting the unfolded position by 9 and folding it back. For b = 1 and b = 2 the target lands on 8 after the far-cell adjustment, so the paddle should move right, and for b = 3 through 5 it also moves right toward the target. From b = 6 onward the target sits to the left of the trail position, so the paddle should move left.

Now I'm working out the just-bounced cases where the ball has moved left from column b. For b from 1 to 7 the paddle should head right toward the folded target, and at b = 8 the target lands on 1, so the paddle moves left there.

I'm working through the thresholds for the upper-right case on row 8, where the paddle should move right whenever it sits left of the lower bound and left whenever it sits right of the upper bound. For the ball at column 0, the target comes out to 9, so the paddle starts by moving right.

I'm setting the thresholds for the upper-right case at row 8, with the paddle moving right while it sits left of the lower bound and left once it sits right of the upper bound. For columns 1 through 4, the targets already settle the direction, so each one gets a single matched pair of bounds.

I'm settling the thresholds for the upper-right case at b = 6 through 9, where the paddle sits in the left-bound region and should keep moving left, with the bounds collapsing to a single cutoff at each column. I'm also wondering whether column 9 can be reached with a far-cell preference at all.

I'm working through the just-bounced cases at row 8 where the ball has moved left from column b, checking that the paddle should move left whenever it sits right of the upper bound. Then I'm moving on to the mirrored up-left table, where the trail sits at b + 1.

I'm filling in the mirrored up-left table by reflecting the up-right thresholds across the middle column, so each ball position gets its paddle bounds from the opposite side. I'm running through the values for each column, starting with the corner cases at 0 and 9.

I'm checking the upper-left table against the upper-right one by mirroring the bounds. For the ball at column 4 with the trail at 5, a paddle at 5 should move left and a paddle at 4 should move right, and the bounds (5, 4) match both.

I'm checking the upper-left table at b = 9 with the trail also at 9, which is the corner case where the ball is already against the wall.

Now I'm working out the tables for the upper-left case on row 8, where the ball moves left from column 8 and the paddle target folds back to 2 through the far-cell rule.

Working through the row-8 zone bounds for the down-right case, where the lower bound is the ball's own column and the upper bound is one step further right, capped at 9. For the down-left case the mirror applies, with the lower bound one step left of the ball's column.

Now I'm writing out the lookup values for the upward-moving targets, starting with the rightward mapping for the first few positions.

Now I'm checking the fold values for the right-moving and left-moving targets, where the far-cell preference shifts a few of the edge cases. I'm also wondering whether that preference causes trouble at the critical observation on (9,8).

Working out the dead-zone and landing-cell tables for the down-right case, where the trail cell is the ball's column and the bounds collapse to a single target. I'm now writing the row-0 entries of the DR table, with the target for each column coming from shifting the unfolded position by 8 and folding it back.

Filling in the down-right table row by row now, with each cell's target coming from the unfolded position shifted by the row's distance and folded back.

Filling in the down-right table row by row, with each cell's target coming from the unfolded position shifted by the row's distance and folded back. Row 7 is the last full row, and I'm checking its final cell at x = 9, where the ball heads to the wall and then drops to (9,8) moving left.

Now I'm writing out the DL table row by row, starting with row 0 and working through the leftward targets for each column.

Checking the mirror relation for the down-left row 0 against the down-right one, and the entries line up: [7,6,5,4,3,2,1,1,0,1]. Now starting row 1 of the DL table by mirroring the DR row 1 values.

Still working through the down-left table: I'm computing row 3 by reflecting the down-right row 3 values and folding them back.

Still filling in the down-left table, now with the reflected down-right values for rows 4 through 6...

I'm now setting up the up-right table, starting with row 7 where the bounce offset is 8, and the targets come out the same as the first down-right row.

Still filling in the up-right table, now with the remaining rows of numbers...

Still filling in the upper-left table, now with the remaining rows of the mirrored values...

Still working through the up-right and up-left lookup rows, checking the folded values for the final rows against the mirrored table.

I'm checking the up-left table against the up-right one, and the bounds for columns 4 and 5 line up. Next I'm verifying the just-bounced case for the up-right row 8 by tracing a ball that is descending right at column 4.

Now I'm tracing the just-bounced case where the ball is at (5,8) heading up-right with the paddle at 4, so the paddle needs to move right to catch the rebound path through columns 6 to 9.

Now I'm checking the fold for a ball descending right at (3,8), where the paddle would sit at 3 and the far-cell preference changes the target to 4.

I'm checking the up-left case from the paddle at 4 with the ball at (4,8): the paddle stays put, and the ball heads up-left toward the wall and back, landing at column 4 again, so the target is still 4. Next I'm looking at the ball one row up at (3,7) with the trail at (4,8) to see how the bounds shift.

Checking the up-left row 7 entry at column 3 now: the offset gives a target of 4, which matches the table. Next I'm looking at the row-4 stall state, where the ball's row equals the trail's row and it counts as descending, so the down-right or down-left table applies with n = 4. Then I want to revisit the vertical direction sign for rows 0 through 4, where the ball's row matches the trail's.

I'm setting the vertical speed values for each row, where the descending rows count up from 0.5 and the ascending rows come out negative when the ball is above the trail. The unit gain then comes from tanh of 8 times that difference, which gives at least tanh(4) in magnitude.

Still writing the layer-2 gate formulas...

Still wiring the layer-2 gates: each one adds the matching comparator and the two direction signals, shifts by the bias, and squashes with tanh.

Still filling in the policy weights: the right-action and left-action output weights each get M = 20, with the noop bias set at M and the other actions pushed negative.

Still checking the action weights and the tanh saturation bounds, making sure the summed gates stay close enough to ±1 that the output logits remain comfortably separated.

Still wiring the gate weights and checking the comparator margins, since each comparator needs a wide enough gap to saturate cleanly.

Still wiring the weight indices for each row slice, and I'm about to sanity-check the n counts and the start and edge cases by simulating a few episodes by hand.

I'm tracing the first observation from the start state, with the ball at (0,3) and the paddle at 4. The ball is descending right, and its target column comes out to 5, so the paddle moves right to 5. The ball's next position lands at (1,4), which has no brick and isn't on the paddle row.

I'm tracing the ball through the first few steps: it moves down-right from (1,4) to (5,8), with the target column staying at 5 the whole way, so the paddle just holds. At the fifth observation the ball is at (5,8) with its trail at (4,7), and I'm about to check the down-right row 8 lookup for column 5, where the bounds are lo=5 and hi=6 and the paddle sits at 5.

Checking the ball's next step from (5,8): it bounces off the paddle at column 5 and heads up-right to (6,8), and the paddle sits on target. Now I'm testing the ascending up-right case at (6,8) with the paddle at 5, where the target is column 4, so the paddle needs to move left.

I'm tracing the ball forward from (9,5): it bounces to up-left at (9,4), then strikes the full row-3 brick at (8,3) and turns down-left, which lands the trail at column 4 again. That confirms the up-right lookup gives 4, matching the fold of 15.

Checking the up-right table for row 5 at column 9 gives a target of 4 as well, and the trail matches that up-right direction, so the paddle stays where it is.

Now I'm checking the left-moving cases at the bottom of the lookup table, with the ball at column 9 on row 4 and the lookup values holding at 4. Next I'm tracing the down-left case from (8,4) and the down-left lookup for row 5 at column 7.

Now I'm checking the up-left case from (3,8) with the paddle at 4, where the lookup for row 8 at column 3 should give the target I need.

I'm checking the ball's path from the stall at (0,4) through the brick strike at (1,3), which sends it back down to column 5 on the right-hand side, so the target stays at 5. Next I want to confirm the ascending target still holds once the brick at (3,8) is gone.

Now I'm checking the ball's next step up to (8,3) on the ascending path. The lookup there gives a target of 2, down from the earlier 4, because the extra bounces shift the landing column.

I'm weighing whether to accept the paddle's wasted motion from moving toward a predicted target that might shift by up to two columns. Each change of direction risks a sticky action, about a 10% chance of the opposite move, which could cost up to two steps of slack. That mainly matters when the slack is already tight, so I'm considering whether the brick information could avoid some of those reversals.

I'm checking the worst-case slack: after a bounce the paddle has about ten actions to reach the target, and the target can shift by no more than the extra time the ball takes to get there, so the paddle should still make it. I'm also weighing the forward-preference tweak at tenth step, since the alternate catch column might cover that case.

Now I'm checking the case where the ball moves up from row 4 to row 3 without hitting a brick at the expected spot: the target column still gets predicted, and the paddle can correct itself later with enough slack to spare.

Now I'm checking how the target shifts when the ball moves from row 4 up to row 3: the unfolded landing position moves by two columns, and I get two extra steps of time, so the paddle should still have enough slack even with the grid adjustment adding a column or so.

Now I'm checking the ascending cases for the next row up: the unfolded target shifts by about two columns per row, and the extra steps in the ball's path give the paddle enough time to cover it, and the shift is still within that margin once the grid adjustment is included.

I'm checking the ascending-row cases at the top of the board, where a ball coming down from row 0 can bounce off a brick and reverse into an ascending path. The detection treats it as a descending ball with one fewer step, so the predicted target ends up off by one column.

I'm checking the edge case where the ball is descending at row 0 and a brick above it sends it back into an ascending path. The detection still counts it as a descending ball, so the target might be off by one column, but the paddle has had many steps to get near the target already. Any misprediction here costs little, so I'll accept it.

I'm checking the pass-through cases: a ball ascending at row 4 that hits a brick at row 3 turns descending with the strike flag set, and the flag resets once it reaches an empty cell. A ball bouncing off row 2 from row 3 stays on row 3 and turns descending, and the next cell is empty, so nothing changes there.

Now I'm checking the ascending ball that hits a brick at row 1 from row 2: it stays on row 2, turns descending, and any brick it meets on the way down gets passed through, so the predicted n = 6 still holds.

I'm checking whether the paddle can still reach the target if the ball's path changes after a bounce off the top. Since the ball can drop back onto row 0 and skim along it, the predicted landing keeps shifting, so I want to see whether the paddle's remaining steps always cover that shift.

Now I'm checking the starting positions: paddle at 4 with the ball coming down on the right gives a target of 5, and the left case from (9,3) gives 4, so the paddle stays put. Then I'm tracing the sticky action at the start, where the first move is likely to repeat the last action with a 0.9 chance.

Now I'm weighing the failure odds near the corner: after a wall bounce the paddle has about nine steps to cover a distance of nine, so a single sticky repeat at the start would cost it a step. I'm checking whether a cheap adjustment could cut that risk.

I'm weighing a fix for the corner case: after a wall bounce the paddle has only one step of slack, so a single sticky repeat is survivable but two would cause a miss. Waiting at 8 and moving right at the critical step doesn't help, since the next heading is leftward, so I'm looking at whether pre-moving toward the corner can absorb that risk.

I'm looking at the corner case again: the paddle can't avoid a sticky repeat here because the required positions only allow noop or right as the prior action. Pressing into the wall doesn't help either, since it acts the same as noop. So I'm accepting about a 1% failure risk in this scenario.

I'm checking whether the corner landing at 0 is actually likely, since it only arises when the ball lands at 9 heading right with the right phase mod 20. Even then, a specific brick layout is needed to produce the slack-one path, so I estimate about 0.05% failure per cycle and judge that acceptable.

Now I'm estimating the per-cycle failure rate: the remaining low-slack cases add only about 1e-5 each, so the corner case dominates at roughly 5e-4 per cycle, and I'm checking how many cycles fit in an episode.

I'm estimating how many cycles fit in an episode and how much each one costs, then asking whether the corner case could be avoided by changing the paddle's position at the catch.

Now I'm weighing whether the corner landing can be avoided one cycle earlier, so the paddle never ends up needing a full-width move with only one step of slack.

I'm working through the corner landings again: one comes from a bounce off the opposite wall, and another from reversing direction with a position-folding rule that sends the target to the far side of the board.

I'm working through how the ball's bounce row shifts the unfolded landing phase, checking which starting states would end up at the corner again. The fold mapping gives a corner landing when the previous position was 8 with the reversal at 9, and other bounce rows map to different phases, so I'm tallying those cases.

I'm checking the corner-to-corner chain: the paddle has no way to escape it since the catch type is forced there. I'll accept the residual risk and move on to verifying the Dx detection in the brick-hit states.

Now I'm confirming the detection logic at the brick-hit states: with the ball at (x+dx, y) and the trail at (x, y), the horizontal offset is just dx, so the sign checks out. For the ball at x=0 with the trail at x=1, the offset is -0.5, which reads as moving left and matches the expected stall at the wall. I'm also checking the up-left tables near the stalls, starting from (0, 7) with the trail at (1, 8), to see whether the predicted target lands where the simulation says it should.

I'm checking the opposite-direction case next: the ball starts at (0,6) moving up-right, and I'm tracing it through the brick hit at (3,3) to confirm it lands at 7 after seven steps, which matches the formula.

Now I'm working out the comparator weights for the paddle units, where each one sums the ball's contributions from rows 0 through 8. Then I'm checking the gating for each case: for the down-right case, the unit should fire only when the horizontal and vertical offsets are both positive.

Still writing the weight matrix for the second layer...

Still writing the weight matrix for the second layer...

Still writing the weight matrix for the output layer...

Now I'm settling the gain: with the weights at 5 and the bias at -10, I'm checking how far the layer-one activations saturate. Then I'm considering a larger gain of 10 so the tanh outputs sit closer to ±1.

I'm settling the comparator gain at 10 so its outputs saturate cleanly, and checking a full descending-right trace toward the corner with no sticky actions involved.

I'm checking the paddle's behavior at the corner: the ball comes down to row 8 at x=9, the paddle stays put, and the ball rebounds up-left. I'm now verifying the detection values for that moment, starting with the horizontal offset.

Tracing the ball back up-left from (9,8), I confirm the left-move decisions at each step: the paddle shifts left from 9 to 8 to 7 to 6 as the ball climbs through rows 8, 7, and 6.

I'm tracing the descent on the left-diagonal path: at row 4 the paddle moves from 4 to 3, and the ball's next position is (3,5) with the check still passing. Then on row 5 the paddle shifts to 2 as the ball heads to (2,6).

I'm tracing the ball down the left diagonal to the wall at (0,8), where the paddle holds still at 0 and the ball bounces up-right.

I'm checking the corner-to-corner path once more: the paddle reaches 0 a step early, and the sticky left move at the wall is harmless. Next I'm looking at the down-left tables at u = -1, starting from the ball at (0,7).

I'm checking the stall case where the ball sits at (0,8) with the trail at (0,7): the offset points right, and the paddle at 1 means I hold still. Then the ball heads up-left to (1,8), and the up-right table for that trail position says the paddle should move right toward 7.

I'm checking the tail of the ball's path on the left side, where it stalls at the wall and then heads right toward (7,8), which gives a landing at column 7. Then I'm confirming the up-left table for the trail at (1,8) and the ball at (0,7), and it matches the expected target at 7.

I'm double-checking the just-bounced thresholds for the up-right case with the first-reach preference, and the target of 8 still sends the paddle right. Then I'm considering whether the zone at row 8 causes trouble when the paddle happens to sit at the left edge, and I don't think it does. Last, I'm wondering whether long deterministic loops could form when bricks are present, since the brickless analysis only covered the extreme cases.

Next I'm checking whether the paddle's arrival overshoot could snowball: if the paddle lands on its target with a sticky move still pending, it can drift past, and the corrections may wander back and forth.

I'm checking how a sticky action could push the paddle off its target, and whether that matters depends on how many steps remain before the critical action. If the paddle arrives early enough, a single overshoot still leaves it in the zone.

I'm estimating how often a sticky action makes the paddle miss its target when the arrival lands right at the critical step. A sticky move at arrival fails about 10% of the time when the critical action comes immediately after, and about 1% when it comes one step later. Checking when the arrival falls exactly one step before the critical action is where I'm heading next.

I'm checking the slack in the tight cases: the paddle has to cover the distance from where the last bounce sent it, and for the rightward-moving ball that distance depends on the starting column.

I'm checking the slack on the tight cases: corners leave only one step of slack, and accidental bounces at the extremes leave two. Most other starting columns give three or more, so the paddle has room to recover from a sticky move.

I'm estimating the failure odds for the slack-3 cases: losing three steps at the start leaves no slack and still lands fine, while losing four or more is roughly a 1e-4 chance. The two-loss case leaves one step of slack, so a sticky overshoot at arrival could still fail it.

I'm checking the overshoot risk for the slack-3 case where the paddle starts at column 1 heading right: after a sticky move at arrival, it ends at 9 instead of landing on 8 or 7. That gives roughly a 9e-4 failure chance, about as large as the corner case. I'm considering using first-reach preference for those starting states too, which would add slack.

I'm considering choosing the target as whichever of the two wall-adjacent cells is nearer the paddle, so that a sticky overshoot lands on the other one and stays in the zone. That means using the range between L and L' for every row, not just row 8: move right if the paddle is left of both, move left if it's right of both, and stay put when it's on either one.

I'm weighing a variant where the target is whichever of the two wall-adjacent cells the paddle reaches first, so an overshoot lands on the other one and stays in the zone. That saves a step of travel when approaching from the far side, but it means the catch type depends on which side the paddle comes from, so the loop analysis and the slack trade-offs between the two catch types would both need redoing.

I'm now checking the two zone variants against each other: a zone of both wall-adjacent cells, or a single target chosen by where the ball catches. The catch side looks like it matters most for the bad cases, so I'm weighing whether to pick one target per state.

I'm seeing that the zone rule can produce a 2-cycle: the paddle moves from 6 toward the zone and stops at 4, then moves back and stops at 6, so the ball keeps bouncing between x=4 and x=6 under the ceiling. Stickies could break that cycle, but I'd need to check how often they fire at each action change.

I'm weighing a fixed target of L for every state, with the wall-adjacent zone narrowed to just the critical row, since a zone spanning both cells would let the paddle shuttle back and forth and waste steps.

I'm estimating failure odds for the corner states, which have only one step of slack: if two or more sticky losses happen at the start, the paddle misses, roughly a 1% chance. Next I want to see how often the zero-loss path still fails when the arrival lands right at the critical action.

I'm checking how often the paddle would land one step early versus exactly on the critical step, and how the corner cases with a row-3 bounce change those odds. The failure chance looks around 1% for corners, but it depends on whether a brick sits where the ball would bounce.

I'm now estimating the corner failure rate at about 0.5% per landing, which makes it roughly 5e-4 per cycle. Extreme columns look fine thanks to first-reach preference, since there the paddle has four steps of slack. I'm flagging the near-extreme columns next, the ones adjacent to the walls, because that's where the remaining risk is concentrated.

I'm now checking the near-extreme start states with slack 3: for the rightward approach from column 2 to target 8, an arrival-time overshoot is harmful. I'm tallying the failure odds by how many sticky losses happen at the start, with two losses giving about 9e-4 and one loss leaving only two steps of slack.

I'm testing the case where the paddle arrives at the target two steps before the critical action. A sticky move at arrival pushes it one cell off, and a second sticky on the next step pushes it further, so the failure chance here works out to about 0.9%.

I'm now working out the failure odds when the paddle arrives at its target with some steps of slack left over. If it overshoots on the wrong side, a sticky move on the next step can push it out of the zone, and that chain gives roughly a 0.9% chance of failure. I'm going to define the probability carefully as a function of how many observations remain before the critical action.

I'm checking how the failure chance changes with r, the number of observations left before the critical action. With no slack, a sticky move at arrival puts the paddle off target, and with one step of slack the overshoot chain still comes out near 1%.

I'm checking the failure odds for the case where the paddle arrives at its target with two steps of slack: an early overshoot followed by a second sticky can leave it off the zone, which comes to about 1% when the overshoot lands on the wrong side and about 0.1% when it lands on the right one.

I'm checking the r=3 case: the paddle overshoots once, returns, then overshoots again on the critical step. That chain gives roughly 9e-4 failure odds whichever side the zone sits on, so it's small but not negligible.

I'm working out the failure odds for each remaining gap r between arrival and the critical action. With no slack and a sticky move on arrival, the paddle can end up at the wrong cell, about 10%, and at one or two steps of slack it's about 1%. With three steps of slack the chain drops to about 0.2%, and it keeps shrinking as slack grows.

I'm now working through the arrival-jitter cases, where a sticky move at landing can push the paddle off the zone. I'm considering a wider zone covering both adjacent catch cells, so that an overshoot onto the second cell still counts as on target.

I'm checking whether the zone rule holds up at arrival: if the paddle overshoots once, the farther zone cell still counts as on target, so a single sticky move doesn't break it. The risk comes from two consecutive sticky moves, which is about 1% when the critical action is only one observation away.

I'm checking whether a zone covering both adjacent cells helps here: an overshoot lands on the farther zone cell and still counts as on target, which cuts the failure odds at two or more steps of slack. The catch is that a zone rule in every row could make the catch side depend on the approach direction, so I'd have to nudge toward a preferred cell at the critical step to avoid loops.

I'm settling on a preferred cell within the zone at the critical step, since both catch cells count as on target. Moving toward that cell there adds no risk beyond what the sticky action already carries, so the zone rule works without loops.

Next I'm weighing the row-8 catch choice: both zone cells are equally risky at the critical step, so I can pick the preferred one there. That keeps the default catch type while still avoiding loops, but I need to check what it costs in terms of the remaining failure rate.

I'm weighing whether the catch type matters at the critical step: when the paddle is at the lower cell L and came in from the L side, a no-op there still lands it in the zone, so that case is safe as well.

I'm checking whether a zone covering both adjacent catch cells still works at the extremes. Moving to the preferred cell at the critical step is free of extra risk, since both cells are reachable either way, but the paddle might stop at the non-preferred cell, and then the critical move leaves a 10% chance of the wrong catch type.

I'm now weighing a zone of both cells for the extremes in rows below 8: it costs about a 0.1 chance of the paddle ending on the wrong catch type, but with two or more steps of slack that only adds around 1e-4 to the failure rate, which is acceptable.

I'm working out the extreme-case catch rule: for a landing at the wall, the paddle approaches from the inside, so it reaches the inner zone cell first and stops there, and the outer cell only matters if it's already sitting on it. Then I'll set row 8 to target the inner cell and leave the corner single-cell case alone, since overshooting into a wall is harmless.

I'm settling the catch rule for rows above the critical one: the zone covers both cells L and L', and row 8 then targets one preferred cell, L normally and L' at the extremes, since the critical move is no riskier than any other action there.

I'm weighing the extreme cases next: for the landings at the walls, I could target the far cell instead, since it's reached in fewer steps, and a small slack advantage for the forced-fresh-catch variant. I still need to check whether the slack numbers for rows 0 and 1 hold up when the zone counts as on target.

I'm keeping the VF catch for the L=8 case going right, since the distance is 7 against 9 for FR, so slack is 3. The zone covers cells 0 and 1, and the paddle stops at 1 and overshoots to 0, which still counts as on target. A failure here needs several consecutive sticky moves, roughly 1e-4 to 9e-4.

I'm now recomputing the failure probability for the case with one sticky loss, using the new zone design. At the row-7 observation the paddle already sits in the zone, so the intended move is a no-op, and a sticky outcome would send it to the other zone cell. I need to check how much that single loss actually adds to the failure rate.

I'm now checking the failure rate for the one-loss case with this zone design: if the paddle sits in the zone and a sticky move hits at the critical step, the catch type can flip, so the chance is about 0.01. Combined with the chance of a start-up loss, that gives roughly 9e-4 for slack-3 states, and the two-loss case adds another small piece on top of it.

Now I'm checking the total failure rate for the slack-3 states: the start-loss cases at one and zero sticky events each add about 9e-4, which comes to roughly 1.8e-3 overall. That's higher than I'd like, so I'll look at whether a different target cell at the critical step could reduce it.

I'm estimating the failure rate when the paddle arrives with little slack: roughly 0.1–0.2% for low-slack arrivals, and about 1e-4 or less once there are three or more steps of slack. The pattern looks like a factor of ten for each extra step, which makes the zone design work well enough. I'm now asking whether the arrival overshoot can be widened, since the zone only covers two physical cells.

I'm estimating how often the arrival-jitter failure actually matters: for a paddle that arrives with only a few steps of slack, the chance of a catch-type error is around 1e-3, but with three or more steps it drops to roughly 1e-4 or less. Typical bounces leave plenty of slack, so the per-cycle failure rate should be small overall. What I still need is how often the high-distance cases, where slack is 3 or less, come up in the VF and FR tables.

I'm now working through the landing cells for the vertical-fall case, where the zone is the pair of cells around the landing point. For the start positions near the middle, the distance from the paddle to the zone shrinks as the ball's start column moves, and I'm tracking where that distance drops to zero.

I'm tabulating the VF distances across starting columns, where the slack shrinks to zero at x0=5. Next I'm working out the FR case: with the ball heading left from x0, the landing cell depends on fold(x0 − 9), which gives 8 − x0 for most columns and needs a separate check at x0=9.

I'm tabulating the zone distances for the paddle starting at each column, where the corner case at x0=9 leaves a zone of just the one corner cell at distance 9, and the rest of the columns give zones of two adjacent cells with distances falling to zero at x0=4.

I'm tabulating the remaining landing distances per column, where FR is better for the first four cells and VF for the rest, which leaves the slack near zero only at the middle columns. The corner case stays forced at distance 9, and a VF-default with FR only at L=0 gives a distance of 6 there.

I'm checking the slack values for the corner and edge cases: the corner state has slack 1 and the L=8 case has slack 3, and those are the two bad spots in the design.

Now I'm checking the slack-3 failure estimate again, and the terms for slack 4 and slack 5 look small enough that they don't change the design.

I'm tallying the per-cycle failure rate now: the corner landings dominate, at about 1e-3 per cycle if they make up 10% of landings with row-3 bounces. Realistically that's closer to 5e-4, which over roughly 800 cycles gives something like 0.4 to 1 failure per episode.

I'm weighing whether the corner failure can be reduced by changing where the paddle waits at the critical step, since the corner landings dominate the per-cycle risk. I'm also checking the idea of staying at column 8 before the critical observation instead of sitting at 9.

I'm looking at whether the corner failure can be avoided by changing the landing choice, since a single sticky step can't be undone once the paddle has to reach the far wall. Each catch's sticky risk is independent, so the two-in-a-row chance stays around 1% no matter how I order the actions. The real lever seems to be steering away from corner landings in the first place, when the alternatives are both feasible.

I'm checking whether the corner landings can be steered away from in the first place. With row-3 bounces, a corner comes only from another corner under the VF move, or from the FR move at one specific column, so I can avoid them by choosing the alternative when it's feasible. I'll check how the row-2 bounces, which shift the landing by 11 instead of 9, change that pattern.

I'm checking whether a row-2 bounce shifts the landing so that a ball starting from column 7 heading right ends up in the corner again. I'm tracing that path through the brick at row 2 to see how many moves the paddle would have to make.

I'm tracing how the corner-to-corner chain could start: a ball lands in a corner after a higher bounce, which leaves more slack, and then the chain only keeps going when the row-3 bricks sit in the right cells for each corner.

I'm estimating how often the chain of corner landings actually happens: maybe 5% of landings end in a corner, and about 40% of those give the one-slack flight, mostly on early boards where the brick is still there. That works out to roughly 2e-4 per cycle, about the same order of magnitude as the other failure terms.

I'm checking whether the slack-3 case can be improved: waiting at column 9 for a right-going fold just sends the ball into a corner with distance 9, which is worse, so the vertical-fall move stays. I'm also thinking about how arrival jitter scales with the number of steps of slack, roughly a factor of ten per extra step.

I'm checking whether the arrival-timing risk can be removed by changing the policy when the paddle is one step from the zone. If the paddle moves on to the second zone cell at row 7 instead of holding, the sticky-action risk at the critical step goes away.

I'm checking whether the arrival risk can be reduced by changing how the paddle approaches the zone. If it overshoots from the first zone cell into the second, the prior action stays the same, so the next step carries another sticky risk. Once it lands without a sticky action, though, the previous action is a noop and the zone holds, so each arrival fails with about 1% chance, and recovery from a miss needs several steps.

I'm considering whether to stop the paddle one cell short of the zone, giving a three-cell tolerance, but that doesn't hold up. Instead I'm looking at the reverse case: if the paddle is already inside the zone at Z2 and a sticky action pushes it out, an intended move back toward Z1 might recover it.

I'm weighing whether the arrival failure can be made smaller: if the paddle is already inside the zone and a sticky action sends it into the second cell, intending noop there is still the right choice, because moving back toward the first cell would open a new sticky risk on the far side. With that, the per-arrival failure works out to roughly 10^-(r+1), and since the slack is usually three or more, it stays around 1e-4 or less. The corner case remains the one inherent risk, so the design looks reasonable, with most episodes plausibly reaching the cap.

I'm testing whether choosing the forward-right move for the lower columns would give more slack, by tracing the brickless parity classes of landing positions under each move.

I'm tracing the orbits of the landing positions under the two moves: vertical-fall shifts u down by 2 in one range, and forward-right maps u to 15 − u in the others. Starting from 9, the chain runs 9 → 7 → 5 → 3, then bounces between 3 and 12 under forward-right.

I'm checking the brickless orbits under the forward-right move for the lower columns: the cycles {3, 12} and {2, 13} would loop forever without a critical-step break. Restricting forward-right to only columns 0 and 10 gives a single odd cycle of ten states that covers every landing cell.

I'm checking the cycle {1, 14, 12, 10, 5, 3}, which may not cover every cell and could loop, so I'm keeping the forward-right move only at columns 0 and 10. I still need to verify the "+17" and "+18" offsets in the brickless analysis, since the ceiling path determines the critical-step landing.

I'm working through the zone boundaries for the upper rows, switching from a single target cell to a (lo, hi) pair taken from the smaller and larger of the two fold positions. For right-facing landings the pair is simply (u, u+1) for the lower columns, collapses to (9, 9) at u = 9, and then steps down one cell at a time as u climbs toward 18.

Now I'm writing out the right-facing zone bounds for each landing position: the low and high cells are just u and u+1 until the fold kicks in around u = 9, then they step back down toward 0 as u climbs past 10.

I'm now working out the left-facing zone bounds: for u from 1 to 9 the pair is (u−1, u), it collapses to (0, 0) at u = 0, and for negative u it runs from (0, 1) up to (8, 9) before settling at (9, 9) at u = −10.

I'm now checking the mirror symmetry of the left-facing zone bounds against the right-facing ones, confirming that each lo value equals 9 minus the hi value at the mirrored position, and it holds at the edges. Next I'll build the row 0 to 7 zone tables, four lo and hi variants each, and treat row 8 separately.

I'm recomputing the just-bounced thresholds using zones instead of single targets. For the upper-right case, with the ball at column b heading right, the zone comes out as (9 − b, 10 − b), so I'm checking the first few columns against that.

I'm checking the just-bounced zones for the rightward case with the paddle on the far side: at b=5 the paddle at 4 is already inside the zone, so it holds, and beyond that the zone pulls left. For the leftward-heading case, the zone shifts one cell per column, so I'm stepping through b=1 to 4 to confirm each one still points right.

I'm filling in the Breakout thresholds for the just-bounced states on the upper rows, using the zone bounds. For the wall case at column 0 the zone is the single cell 9, so the paddle moves right, and for columns 1 through 3 the paddle sits left of the zone on both trail cases, so the threshold pairs are (7, 8), (6, 7) and (5, 6) for the 2nd through 4th entries.

I'm filling in the remaining just-bounced thresholds for the upper-row cases at columns 4 through 7, and each pair gives the paddle a clear direction for every position it could be in.

I'm checking the Breakout thresholds for the just-bounced states at columns 4 and 5, where the pattern between the two zone cases doesn't line up cleanly. With the ball at column 5 after a rightward bounce the zone is (4, 5), but the leftward case at the same column wants (3, 4), so I'm weighing whether a single threshold pair can cover both without sending the paddle the wrong way.

I'm checking the just-bounced thresholds for the upper-right row 8 cases, and at column 4 the zone is (4, 5) with the paddle at 4 treated as inside it, so I'll set the bounds to (4, 4) to avoid losing a step. The remaining columns 6 through 9 line up with their VF zones, so I'm moving on to confirm each lo and hi pair against the paddle positions.

Now I'm computing the mirrored thresholds for the upper-left row 8 cases, flipping the upper-right bounds around the center. That gives the lower bounds from the reversed upper values, and I'm filling in the rest of that list.

I'm checking the upper-left row 8 thresholds for the wall case at column 0 and the VF trail, where the zone runs from (8, 9) and the paddle at 1 still sits left of it, so it moves right.

Checking the upper-left row 8 thresholds for the trail cases at column 3, where the zone lands at (5, 6) and both paddle positions point right, then moving on to column 8.

I'm checking the upper-left row 8 thresholds for the trail cases at columns 6 through 8, where the zones for both the bounced and trailing positions point left, and then moving on to column 1 with its two trail cases.

I'm filling in the descending-row targets for row 8 now: for the right-heading case the preferred cell is just the ball's column, except at column 0 where it's 1, giving the list 1, 1, 2 through 9. For the left-heading case it's the column itself, except at column 9 where it drops to 8.

I'm weighing whether to enforce the just-bounced move on the critical observation, where the paddle sits at the far zone edge and I'd move toward the ball's column. Moving away from the ball risks a sticky reversal that costs two steps, while holding still lets the paddle accept the fold-reset, which could cause loops like {3 ↔ 12} if it happens too often.

I'm weighing whether to enforce the critical-row move, since holding still would let the fold-reset trigger repeated two-cycle loops, while enforcement breaks those loops within a cycle or two at the cost of a rare sticky reversal.

I'm reasoning through the critical-row case: if the paddle steps from the landing cell toward the ball's column, the next ball direction makes it sticky when the ball is heading right at columns 1 through 4. That costs two steps, so I'm checking whether the slack on those columns can absorb it.

I'm weighing a sticky-reversal case for the critical row: at columns 2 and 3, the paddle has to step back the opposite way on the next catch, and each repeated sticky uses up two steps of slack. I'm checking that the chance of running out of slack is tiny, since it takes several stickies in a row.

I'm settling the extreme cases for the descending-row targets: at column 0 the ball's landing cell and the preferred cell both sit at 1, so the paddle holds there on the critical observation. If it approaches from the right it stops at 1 and the fold-reset is accepted, and if it's already at 0 it steps right to 1 on the critical move, accepting the reset most of the time.

I'm weighing whether enforcing the critical-row move is worth it for the L=8 case going right: if the paddle is at 8 and the ball lands at 9, the fold-reset would send the paddle left, which is consistent with the just-bounced heading, so it costs no slack. The slack of three leaves room for a sticky reversal before the catch fails.

I'm now writing out the lookup bounds for the right-heading case, using the same zone layout as before with u = x + n, and listing the low and high threshold arrays for all twenty values of u.

Filling in the lower and upper threshold arrays for the down-right row 8 cases, starting with row 0 and moving through rows 1 and 2.

Filling in the lower and upper threshold arrays for the down-right row 4, 5, and 6 cases, using the same zone pattern as before.

I'm filling in the Row 7 thresholds for the right-heading case and then checking the two corner positions on that row: the ball at x=9 stalls and drops to row 8 heading left, and the ball at x=8 lands on the corner cell with zone (9,9).

I'm mirroring the right-heading row 8 thresholds for the left side: the low bounds for DL come from the reversed upper values of DR, and I'm starting the row 0 list with those.

I'm deriving the down-left row 1 thresholds by mirroring the down-right values: the lower bounds come from the reversed upper bounds, giving 6, 5, 4, 3, 2, 1, 0, 0, 0, 1.

Now I'm working through the down-left row 2 thresholds by mirroring the down-right values: the upper bounds come out as 7, 6, 5, 4, 3, 2, 1, 0, 1, 2, and I'm starting the lower bound list for that row.

I'm filling in the down-left row 3 thresholds by mirroring the down-right values, giving low bounds 4, 3, 2, 1, 0, 0, 0, 1, 2, 3 and high bounds 5, 4, 3, 2, 1, 0, 1, 2, 3, 4.

I'm filling in the down-left row 4 thresholds by mirroring the down-right values, giving low bounds 3, 2, 1, 0, 0, 0, 1, 2, 3, 4 and high bounds 4, 3, 2, 1, 0, 1, 2, 3, 4, 5. Now I'm starting the row 5 lower bounds from the reversed upper values.

Now I'm finishing the down-left row 6 thresholds by mirroring the down-right values, giving low bounds 1, 0, 0, 0, 1, 2, 3, 4, 5, 6 and high bounds 2, 1, 0, 1, 2, 3, 4, 5, 6, 7.

Now I'm filling in the down-left row 7 thresholds by mirroring the down-right values, giving low bounds 0, 0, 0, 1, 2, 3, 4, 5, 6, 7 and high bounds 1, 0, 1, 2, 3, 4, 5, 6, 7, 8.

I'm filling in the up-right row 5 lookup thresholds, continuing the same zone layout with the row 7, 6, and 5 values.

Filling in the up-right row 1 thresholds from the same pattern, starting with the low bounds from 8, 7, 6, 5.

Filling in the up-left lookup thresholds now, mirroring the up-right values row by row, starting with row 6.

Still filling in the up-left lookup rows, filling the remaining threshold arrays by mirroring the down-left values.

Still filling in the up-left row 1 thresholds, working out the low and high bounds from the mirrored up-right values.

Still working out the mirrored thresholds for the up-left row 1, then checking the row 0 bounds at the edges.

Now I'm checking the unfinished upper-left boundary values against the direct zone computations, and they line up. Next I'm about to set the weights for the comparator units.

I'm settling the weight signs for the B units: the hi values need to go in negative, so I'll write them as positive and flip the whole column by −K, which makes the ball-cell weights −K·hi and the paddle weights +K·c.

Still writing the comparator weights...

Writing the comparator weights directly: I'll put K = 10 into the ball-cell and paddle values instead of scaling columns afterward. For the go-right units I'll use 10 times the lower bounds, and for the go-left units −10 times the upper bounds, with paddle weights that match in sign.

Writing the Dx weights now: ball-cell values scaled by 10 from the per-column gains, and trail-cell values going down in steps of 10 across each row.

Still writing the Dx weights, filling the ball-cell and trail-cell columns by stride and deciding whether a strided scalar fill is supported.

Still writing the Dy weights, filling in the ball-row and trail-row values column by column across the strided ranges.

Still writing the Dx and Dy weights, checking the gain-10 margins on the AND gate.

Still checking the Dx and Dy weight fills and the AND gate margins, then re-running the Breakout simulation from the start position with the zone tables.

Checking the upper-right row 7 thresholds at x=7 and row 8 at x=6: the ball is heading up-right toward the paddle, and the paddle sits at 4, inside the zone for that cell, so it stays put. The ball moves on to row 8 at x=6, and I'm verifying the next zone lookup there.

Checking the right-moving zone thresholds for the remaining rows, the paddle stays within the expected zone at each cell. Next I'm working through the down-left thresholds across rows 4 to 7 and the ball's path toward the critical cell.

I'm checking the down-left critical cell again, this time with the paddle arriving from the left and stopping at 3 instead of 4. The ball at x=4 would then be a miss unless the comparator logic still holds, so I'm verifying that case against the zone table.

Now I'm checking the edge cases: with the ball at the corner (b=0) the paddle has to sit at 0, and with the ball at the far end (b=9) heading left, the paddle should be at 8.

Now I'm checking the ball-bounce edge cases on the walls: a ball heading down-right at column 8 lands at 9, and I'm confirming the up-right lookup at column 9 sends the paddle left to 8. A stray step where the paddle goes right from 9 still resolves left, so that case holds too.

Still checking the corner and wall cases against the zone tables, now looking at the up-left ascent at the left edge.

Now I'm checking the ball's path up the right side: at row 4 moving right with the trail at column 5, the zone gives a paddle range of 8 to 9, and with no brick at row 6 the ball keeps climbing. At row 3, column 6 puts the paddle in the 6 to 7 zone, so the slack shifts by two and holds.

Now I'm tracing the ball's path upward from row 3 at column 7, checking the up-right zone there. Without a brick at row 1, the ball climbs to row 0 at column 9 and the zone still holds, so the next step is the ceiling bounce.

I'm checking how the ball descends from the top rows, where it passes through the bricks. The paddle should keep following the earliest-landing prediction, so I'm verifying that the zone lookup still gives a consistent answer at each step.

I'm considering a brick hit from below row 3 where the ball stays at row 2 but is still ascending, so the prediction briefly treats it as descending. On the next step the ball reaches row 1 heading up, which shifts the predicted landing by five while the time to reach it grows, so the paddle stays consistent apart from that one misread step.

I'm checking the slack argument for misread steps: a ball that brushes a brick from below can make the paddle chase the wrong landing for a moment, but the true landing is at least ten steps away then, and any paddle position can reach any zone within nine moves. So that kind of error can't cause a miss, and the invariant should still hold from the just-bounced state.

Still writing the per-row weight tables for the 16 units, starting with the A_DR unit's ball weights and paddle weights.

Still writing the weight tables, now filling in the lookup values for the DR lo unit row by row.

Still writing the DR hi weight table, row by row.

Still filling in the DL tables, row by row.

Still filling in the DL hi weight table, row by row.

Still writing the DL lo weight table, checking the row 4 values against the direct formula for the lower bound.

Still checking the row 4 values against the direct formula, and confirming the high-side entries match too.

Still filling in the DL hi weight table, checking row 0 against the direct formula for the upper bound.

Still writing the DL lo weight table, checking the row 2 values against the direct formula for the lower bound.

Still checking the row 3 and row 5 tables against the direct formula for the lower and upper bounds.

Still filling in the DL hi weight table, checking the row 6 values against the direct formula for the lower bound.

Still checking the weight tables against the direct formulas, now for the DR unit's first row.

Still checking the DR weight rows against the direct formulas, confirming the row 4 lower and upper bounds.

Still writing the weight tables, now the UR unit's lo values for rows 0 through 2.

Still writing the UR weight tables, now the remaining rows of the lo and hi values.

Still filling in the UR weight tables, checking the row 0 values against the direct formula for the upper bound.

Still writing the UR weight tables, now checking the row 4 values against the direct formula.

Still working through the UR r5 weight values, checking the lower and upper bounds row by row.

Still writing the UR weight tables, now the r7 row.

Still writing the UL lookup tables, now the lo values for the remaining rows.

Still writing the UL weight tables, filling in the hi values row by row.

Still working through the UL weight tables, now checking the row 1 values against the direct formula for the lower bound.

Still checking the upper-left weight values, now the UL r8 row's lo entries.

Still checking the upper-left bounds, now verifying the UR r8 entries against the direct formula for each column.

Still checking the bounce cases at the upper-left corner, comparing each column's bounds against the direct formula.

Now I'm laying out the index ranges for each ball row's weight slice, six apart, and the paddle row's slice at the end.

Still filling in the unit 0 weight slices, now the DR lookup values across the ball rows.

Still writing the weight tables for unit 1, the B_DR unit, filling in its negative hi values row by row.

Still writing the weight tables, now filling in the paddle row's weight values for unit 1.

Still writing the weight tables, now the DL unit's lo values for rows 6 onward.

Still writing the weight tables for unit 3, the B_DL unit, with its negative hi values row by row.

Still writing the unit 4 weight table, starting with the A_UR lo values.

Still writing the weight tables, now the B_UR unit's negative hi values for the upper-right rows.

Still writing the unit 5 weight table, row by row.

Still writing the Unit 6 weight tables, now the A_UL lo values for the remaining rows.

Still writing the unit 7 weight table, now the remaining rows of the hi values.

Still writing the unit 8 weight slices, filling in the ball-column values row by row.

Still writing the unit 9 weight slices, now the Dy column values for each ball column.

Still filling in the W2 weight entries, working through the diagonal direction units one at a time.

Still writing the W2 weights, filling in the row 8 and row 9 entries for the remaining units.

Still writing the weight tables, now the W3 entries and a check of the layer-2 logic against the initial state.

Still checking the DR and DL unit values against the direct formulas, confirming the ball-versus-paddle sums come out to the expected signs.

Still checking the DR and DL sums by hand, and the upper-right bounce case is coming out as expected.

Still checking the edge cases, now thinking about whether the ball and its trail can land in the same cell at the walls, and whether brick hits during a horizontal wall bounce break the diagonal assumptions.

Checking the edge case where the ball leaves the upper-left corner after a brick strike: the new row is 4 and the ball is heading down-right, so the right-diagonal weights should fire.

Checking the upper-row bounce values against the direct formula, and confirming the row 0 edge case comes out consistent: the ball moves up to row 0 and then heads back down.

Checking the paddle's catch cases at the critical moment: if the paddle sits one cell beyond the target zone on either side, it still moves onto the zone cell before the ball arrives, so those positions are covered too.

I'm considering whether the corner case can be avoided by changing how the paddle waits after a landing. Keeping the paddle pressed toward the corner gives nothing once the ball heads back the other way, so that's not the fix. Routing the ball away from corners earlier would work in principle, but the setup is too involved to be worth it, so I'll leave it.

I'm weighing whether the paddle could start moving a step earlier at the critical moment, since the ball's loss comes from sticky actions on the first step after a bounce. Moving toward the other catch cell would change the catch type, though, and from the paddle's current spot the only options keep it on one of the two target cells.

Still weighing whether the corner case is worth fixing; going to the other catch cell on the critical step would change the heading, so I'll leave the paddle where it is and accept the small failure rate.

I'm checking whether the paddle can always reach the right cell in time: if the paddle is at the far left, it simply moves right once and gets there. I'm not going to switch the catch at the wall, since that would put the ball back into a corner. The corner-to-corner chain still carries about a 1% failure chance per bounce, and I'm weighing whether a different route off the upper-left corner could avoid that.

Now I'm working out how often the paddle lands in a corner. Each bounce row gives a fixed offset in the ball's path index, so the starting positions that end in a corner are easy to list. I'm also checking the far-extreme catch case, where the paddle has to reach the target cell from beyond the edge.

I'm rechecking the wraparound arithmetic for the corner landings: starting from u=0, a far-right catch gives u' = 18, and adding the bounce offsets (9, 11, 13, 17) wraps to 7, 9, 11, and 15. The row-2 bounce lands back in a corner at index 9, so roughly one in ten landings ends in a corner, and only those need the row-3 brick to stay clear of the slack-one failure.

Checking the boundary numbers again: the row-3 brick cells should fill in a repeating pattern when the board is full. I'm tracing whether the ascending path from the start position hits the brick at column 8 on each bounce, since that decides if the two phases alternate cleanly.

I'm tracing the brick pattern further: each row-3 bounce removes a brick, so the path shifts and later landings go down to row 2. I estimate corners show up about one time in ten, and in a fresh board the corner-to-corner chain is the likely next step.

I'm reconsidering the corner failures: the slack-one flight only happens when the corner's row-3 brick is still present. Each of the two corner bricks can only be hit once per board, so there are at most two such flights per board, which keeps the expected failure count fairly small across a full game.

I'm checking which bricks can be hit along the corner diagonal: a ball moving up-left through (5,4) could only have come from the corner bounce at (9,8), so the brick at (4,3) is only reachable that way. I'm now looking at the other approach, a ball going up-right from (3,4) into the same brick.

I'm checking which bricks along the diagonal could have been hit from the upper-left stall, and whether (4,3) can also be reached by a ball coming down from row 2. That would mean brick (4,3) often disappears through other paths before the corner chain matters.

I'm estimating how many of the corner-brick slack-one flights happen per board, and then how much failure that adds up to over a full episode. I'm also considering the L=8 case, where the flight from the paddle's target cell runs through the corner brick at (5,3) and, if that brick is already gone, drops into a row-2 bounce with extra slack.

I'm estimating how the generic arrival failures add up: at roughly 10^-(r+1) per cycle for bounce row r, the row-3 case comes to about 1e-4 per cycle, which over the roughly 800 cycles in an episode is an 8% chance of failure, so I'll need to check that number more carefully.

I'm working out the per-cycle failure estimate for row-3 bounces by looking at how many moves the paddle needs to reach the catch zone. I'm reading the distribution of required moves from the policy table, which gives a set of values for r that are mostly 3, 5, 6, 7, 8, and 9 across the starting positions.

I'm weighing the failure estimates by starting state: the states with the paddle at offset 3 or 4 carry about 3e-4 and 4e-5 per flight, the ones at offset 2 about 1.9e-3, and the corner case around 1e-2. I'm about to average these over the ten state types to get the per-cycle rate.

I'm estimating the per-cycle failure rate for row-3 bounces by averaging over the ten state types, which comes to roughly 1.3e-3 if every state is equally likely. But the corner and L=8 flights are limited by the specific row-3 bricks that must still be present, so I'm now checking how many such flights each board actually allows.

I'm estimating that row-3 flights come to about 10 per board, and averaging the per-state failure rates gives roughly 1.3% per board. Over a full episode with about 25 boards, that would add up to something near 30%, which is being driven mostly by the corner cases.

Now I'm estimating the row-2 bounce cases, where the paddle shifts its target by two cells once the ball passes row 3, so those arrivals carry more slack and contribute little to the total.

I'm checking whether the corner landing can be avoided earlier in the flight, since the brick at (4,3) makes the corner chain risky. Once the ball is already heading right toward (9,8), that landing looks forced, so any fix would have to come from the step before it.

I'm weighing whether the corner landing could be avoided by changing the previous catch, either choosing a different VF/FR action, but that would depend on the brick layout along the path, which is too complicated to track. I'm considering instead whether the action taken just before the corner can help. At the critical step the paddle should stay put, and the step before that, it's a wall-adjacent move where a sticky action would cost only one step.

I'm weighing whether the corner landing could be avoided by taking a different action earlier, but with sticky actions each wall-adjacent step still carries about a 10% chance of slipping, so the risk doesn't really go away. I'm considering whether an optimal agent should steer clear of corner states altogether, though I don't yet see a cheap way to do that.

I'm weighing a way to steer clear of the corner entirely, since the flight from u=7 could end in a corner if the brick at (6,3) is gone, but I can't tell which brick is present without tracking the layout, so I'm leaning toward accepting that risk.

I'm considering whether to avoid corner states entirely by picking the catch type for each state, so that no bounce row can send the ball into a corner. For a VF catch the next landing spot depends on which bounce row it hits, and for an FR catch on the right-moving side it lands at a few fixed offsets, so I'm checking whether some combination of choices keeps every outcome away from the corners.

I'm checking which catch types could ever send the ball into a corner. Vertical-flight catches from odd-numbered states can reach a corner depending on the bounce row, while odd states 3 and 13 never can via that route. Flipping to the other catch type changes the parity, so I'm looking at how that shifts the outcomes.

I'm sorting the catch types by parity: VF keeps a state's parity, and FR flips it. Even states never land in a corner under VF, and the FR results from odd states are even, so using VF on even states and FR on odd ones should keep every bounce outcome out of the corners.

I'm checking whether keeping the landing parity even would rule out corners altogether, since even states seem never to produce a corner under VF. If the ball stays in even states, pure VF would keep it out of the corners, as long as bounces from below go as modeled. I'm still unsure how irregular bounces from above would change the parity.

I'm checking the parity argument against bounces from above: a descending ball that hits a brick at row 1 or 2 seems to add an even number of steps, so the parity should hold. The case I'm still working through is a ball that passes row 2 and then meets a brick at row 3 from above, since that changes which row it strikes next.

I'm checking whether the parity argument survives bounces from above, working through a descending ball that returns to the same row after stalling at the ceiling. Each round trip between a row and the ceiling looks like it takes an even number of steps, so the parity should hold in general.

I'm noting that each bounce cycle between the paddle and a reflector takes an even number of steps, and so does a round trip to the ceiling. Since the ball advances one column per step, that means the parity of the column index stays fixed under vertical-flight catches.

I'm noting that pure VF keeps the landing index's parity fixed, so the odd class is the only one that contains the corners. Using FR at the extremes u=0 and u=10 would flip the ball into that odd class, which is the opposite of what I want.

I'm checking the even-class extremes now: starting from u=0 with pure VF, the row-3 flight lands on u=10, where the paddle gap is 8 and the failure chance is about 1%, the same size as the corner risk. Then from u=10 the next flight returns to u=0, giving the same ~1% failure again.

I'm now weighing the alternative of using FR at the extremes, which would flip the ball into the odd class where the corners are, so I'd need to find a safe odd state from which FR flips back to even.

I'm now looking at the odd-class states, where an FR action flips the ball back to the even class. At L=1 and L=3 (and their mirrored states), FR gives a safer paddle gap than VF, and at L=5 it's also fine. The state u=7 is less clear, since FR there leaves a larger gap than VF would.

I'm considering using FR at the extremes instead, which would move the ball into the odd class where the corners are, and then checking whether a row-2 bounce from the first step could land on corner 9.

Now I'm looking at the corner-9 case: a row-2 bounce from the first step would send the ball into a forced corner catch, and then the next flight back toward corner 0 only has about 1% slack if the brick at (4,3) is there. I'm considering how often that kind of chain happens across the different schemes, and which overall approach keeps the corner exposure lowest.

I'm now reasoning about the odd class with pure VF: the landing states there step through ten values, and the two corners would come up about a fifth of the time. Each corner landing depends on a brick at (4,3) or (5,3), and each one carries roughly a 1% failure chance, so I'm checking how many of those can happen on a board.

I'm now checking how the two parity classes interact under scheme A: once the ball has hit an extreme and moved into the odd class, it seems to stay there, so corner landings would keep recurring. I'm also asking how the bricks at (4,3) and (5,3) could get removed otherwise, since the corner-9 path and a route through (3,4) both lead to them.

I'm now comparing a pure vertical-flight policy, with no deliberate flips, against the mixed scheme. The odd-class corner risk still shows up in the estimate, roughly 1.5% per board. Next I'm checking where a ball from the left or right edge would land under pure VF.

I'm weighing a scheme where the ball leaves the odd class, which holds the corners, and settles into the even class. That would mean one deliberate FR at the first catch, since the game starts odd, and then pure VF with some way of handling the extremes.

I'm now setting the rule for scheme C: on even states off the extremes I keep using vertical flight, at the extremes I switch to the flip action, and on odd states that aren't corners I flip back to even. I still need to check whether the flip is always safe at each odd state.

I'm checking the flip at the odd states, where FR at L=7 leaves a gap of 7 against 5 for VF. With VF the ball stays in the odd class and could land on a corner next, so I'm weighing whether the safer flip is worth it.

I'm weighing the corner risk against the extremes: the game's parity classes mean the even-class extremes fall into the odd class, so I'm estimating how often each scheme lands on a corner. Extremes make up about a fifth of even-class landings, and I'm working out what fraction of flights each scheme leaves exposed.

I'm now working through the even-class extremes: a pure flight from u=0 is nearly safe when I flip, but the flip sends the ball into the odd class, where a few landings (like the corner at 9) carry roughly 1% failure risk each, so I'm tallying how often those odd-class states come up.

I'm now weighing the extreme-landing option against the alternative of sticking with vertical flight at the extremes. The even-class extremes are about a fifth of landings, and each leads either into a 1/4–1/3 chance of a row-3 bounce with tiny flip risk or a 1/4 chance of a corner catch that's risky only if the brick at (4,3) is present. Using vertical flight there instead carries roughly 1% risk per extreme, depending on whether the row-3 brick is in play.

I'm going back over how many row-3 bricks could be hit from below, since each of those hits is a tight flight that carries the risk I'm trying to count.

I'm tallying how many row-3 bricks each bounce column can reach from below, since each column gets hit by exactly two just-bounced states, and that count is what sets the per-flight risk.

I'm enumerating the twenty just-bounced states, starting with the ones that send the ball rightward. The first one, from the corner catch at x0=0, lands on corner 9 with no slack and about a 1% risk, tied to the brick in column 5.

I'm tallying the remaining just-bounced states for the rightward flights, each tied to the row-3 brick it hits. The x0=1 case via a flip has about 0.2% risk, and x0=2 through x0=5 are much safer, with the tight ones falling at x0=5. For x0=6 I'm comparing a vertical flight, which leaves one row of slack, against a flip.

I'm now tallying the mirrored left-moving flights, checking the same landing zones and paddle positions for each starting point, and noting which row-3 brick column each one hits.

I'm going through the remaining just-bounced states for the leftward flights, matching each starting point to the row-3 brick column it hits. The x0=9 corner catch lands on corner 0 with about a 1% risk tied to column 4, and x0=8 carries a 1% VF case plus a 0.2% FR case tied to column 3. For x0=7 down through x0=1, I'm checking the VF and FR distances and their brick columns, and x0=0 is just a plain VF.

I'm now listing which row-3 brick columns each of the two attacking states can reach: columns 5 and 4 each get one corner-catch state at about 1% risk and one VF state at about 0.19%. Column 6 has a 1% and a 0.19% attack from the left side, while its other attacker from x0=8 is safe. I'm continuing the same tally for column 3.

I'm now going through the odd-class scheme, where the corner bounces on bricks in columns 5 and 4 carry roughly 1% risk each whenever they happen, and I'm checking which landings lead into them under pure vertical flight.

I'm now looking at the odd-class scheme, where the corner bounces are the only thing that clears the row-3 bricks at columns 5 and 4 from below, since the even-class attackers don't occur there. That leaves those bricks standing until a corner bounce happens, which adds a per-board risk I'm trying to size. I'm also starting on the even-class variant, where the extreme VF flight from x0=1 going right carries the main 1% exposure.

I'm now checking the even-class option where the ball is sent back at the extremes with a flip instead of a vertical flight. That would send the ball leftward from column 1, where it attacks brick column 3 with only about 3e-4 risk, so I'm working out whether that swap makes the even-class scheme safer overall.

I'm now ranking the landing states by risk, starting from the first landing at u=0. Sending the ball right with a vertical flight puts it at about 1% risk, while a flip sends it left with only about 0.03% risk, so the flip looks safer there.

I'm checking the remaining landing cases one at a time: from L=2 the vertical flight gives a row-3 distance of 4 and the flip gives 2, and from L=3 the vertical flight gives 2 and the flip gives 0. Then at L=4 and L=5 I'm comparing the same vertical-versus-flip risks.

I'm running through the remaining landing cases from L=1 up to L=9, comparing the vertical flight against the flip at each one. The flip is safer at the low end, and the corner landing at L=9 is forced to a flip with roughly 1% risk.

I'm now setting up transition rules for the policy: the ball goes fast-reverse when the landing is near the left side and vertical-flight otherwise, with the corner case forced. I'm starting to trace the ceiling and wall transitions for the first u value at 4.

I'm working through the transition table for the remaining states: for each landing position, the next ball positions under a vertical flight versus a flip, with the corner cases at 19 and 9 noted. The low-u states (0 through 3) are best handled by flipping, and the higher ones by vertical flight, which keeps the corner risk limited to the forced cases.

I'm now working out which attack states under rule D hit the column 5 brick from below, checking how the corner and row-2 or row-1 bounces line up with that column.

I'm checking whether the brick in column 5 can be cleared by the right-moving state at x0=9 (a vertical flight at u=8), since Rule D permits that at about 0.19% risk. But Rule D also has brickless loops between states 3 and 12 and between 2 and 13, so I'm wondering whether a sticky paddle that waits at its preferred cell could break those cycles.

I'm checking whether the loops between states 3 and 12, or 2 and 13, can last indefinitely on a brickless board. If the paddle parks on its preferred cell and just waits, no sticky effect ever fires, so the cycle would be deterministic. Only an overshoot that then gets corrected could break it, and I'm working out how long the ball could stay in such a loop.

I'm weighing Rule D against a pure vertical-flight policy, since Rule D can trap the ball in brickless loops that never reach the remaining bricks. I want to check that pure vertical flight still visits every cell within a bounded number of steps, which would rule out getting stuck. I'm verifying that by tracking how the (u, v) coordinates advance together each step.

I'm checking that the orbit of the (u, v) coordinates covers every cell, since each step advances u and v together. The cell (x, y) corresponds to two values of u and two of v, so I'm working out which of those combinations fall in the same parity class.

I'm checking the pure vertical-flight policy by looking at how the ball's two coordinates advance together each step. The orbit covers every cell within 180 steps, since each cell appears in both parity classes, so a brick will always eventually be hit.

I'm checking whether a scheme that keeps the ball in the even class, flipping at odd non-corner states and using vertical flights at even ones, avoids brickless traps. The extremes are the open question, since a vertical flight there carries about 1% risk while a flip sends the ball into the odd class.

I'm testing a scheme that stays in the even class, using vertical flights everywhere except the extremes. But at u=0 that sends the ball to 15, and a flip there loops back to 0, so I need a different arrangement of flips to avoid a brickless trap.

I'm checking whether a scheme that flips at the extremes can still fall into a short brickless cycle, since a mix of vertical flights and flips could trap the ball in a few states that never cover the board. I'm working through a few candidate arrangements to see which ones stay clear of such loops.

I'm checking whether a 4-cycle of landing states could even cover enough brick cells to rule out a trap, since each ceiling flight only crosses a handful of the rows 1 to 3 cells.

I'm comparing the two classes under pure vertical flight to see which one has fewer risky bounces. The even class has its extremes at risk whenever the row-3 brick is present, and the odd class has its corner bounces at column 5 and column 4. I'm weighing those two sets of risks against each other.

I'm now listing the risky flights in the odd class under pure vertical flight, where the just-bounced states from each odd value of u carry small but nonzero risks. Those add up to roughly 2% per board when the corner bounces line up with the bricks at (5,3) and (4,3). Next I'll tally the even class's risky flights for comparison.

I'm comparing the extremes in the even class: a vertical flight at u=0 carries about 1% risk, and with the extremes costed this way the even class comes out slightly worse than the odd class. Switching to a flip at the extremes just moves the ball into the odd class, where pure vertical flight is all that remains, so that option is really the same as the odd-class policy. I'm now checking what a different treatment of the even-class extremes would look like.

I'm checking whether the even-class extremes can be handled with a flip that returns to the even class, but the brickless dynamics show that flipping at u=0 lands on 15 and can loop back, so I'm now tracing where the odd-class flips need to go to avoid a trap.

I'm testing whether a schedule that flips at the odd states could avoid trapping the ball. A cycle like 0 → 15 → 13 → 2 → 0 covers only a few landing states, so it might not reach every brick cell. Splitting the odd-state flips into two separate sets of six landing states each looks like a way to keep both cycles covering the board.

I'm weighing the two classes against each other: the odd class's corner bounces carry roughly 2% risk per board, while the even class's extremes add up to a bit more. Since a trap costs as much as dying, I'm leaning toward a pure vertical-flight policy within one class. I'm now wondering whether I can reduce the corner risk with some brick-aware handling.

I'm weighing whether to avoid entering the corner at all when the dangerous brick sits there, but that would mean switching classes, which makes the scheme too complicated to keep trap-free.

I'm weighing whether the even class's extremes could be handled without a trap, but the only clean option so far is to stay inside one class with pure vertical flight.

I'm checking the even-class extreme at u=0 again, where a vertical flight sends the ball to the right-wall state and the risk depends on whether the brick at (6,3) is present. The failure chance there is about 0.9% from a double-sticky paddle error on arrival, with a smaller contribution from the later steps.

I'm checking the even-class extreme at u=0 with the row-3 brick present. The first overshoot is protected by the wall, since a right move at 9 can't go further, so the only real failure there is a triple sticky error, which is very unlikely.

I'm rechecking the wall effect on the first flight: once the paddle reaches the wall, an overshoot can't leave the zone, so the risk drops to about 0.1%. The same holds for the flight from L=8 going right, which lands in the zone at the left wall, bringing its risk down to roughly 0.01%.

I'm rechecking the corner flight with the wall in mind: zone (0,0) gives 9 actions of slack, so the paddle can only fail on two or more sticky errors, about 1%. Next I'll run the same check for the neighboring states to see how much the walls reduce their risk.

I'm now checking the wall-protected zones: the flight from x0=1 with a 0.1% risk, then the FR arrival at 0.01%. For the x0=2 flight into zone (7,8), I'm estimating the overshoot failures at each remaining slack level, which each come out to roughly 1e-4.

I'm now checking the wall-protected zones for the remaining flights. The flight from x0=2 gives about 2.7e-4, and the one from x0=3 is only around 3e-6. The flight from x0=8 into zone (1,2) is the next one to estimate, where the overshoot risk looks small but still needs a number.

I'm now checking the remaining flights, where the wall-protected zones bring the failure risk down to about 1e-4 for the x0=9 case, with the mirror-image flights handled by symmetry.

