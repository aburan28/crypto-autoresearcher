#set page(paper: "a4", margin: 1.7cm, numbering: "1")
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: "1.")
#show table: set text(size: 8pt)

= Evidence review: the isogeny-chain encoding with the chain variables eliminated first (m = 3)

*Decision* DEC-20261019-b01514: *reject_scoped* (scope widened to block elimination orders at $m = 3$) · *evidence* EV-ECDLP-97cb57 (contradicts, replicated, toy tier) · *validation* VAL-20261019-e750db (passed) · *runs* RUN-ECDLP-20a588-01, -03 · *experiment* EXP-ECDLP-20a588 · *goal* GOAL-ECDLP-001.

*Scoped claim.* For Semaev $m = 3$ on toy primes (10–22 bits, $L = 3..7$), solving the chain encoding of the factor-base set with the chain variables eliminated first (msolve `-e`, Singular block order) removes the growing penalty of plain grevlex but stays slower than the dense encoding of the same set: msolve paired median ratios 1.34, 1.86, 2.27, 1.94 at $L = 3..6$ (95% intervals all above 1); Singular 1.61 and 1.42 at $L = 3, 4$; both msolve arms are retired together at $L = 7$.

== Question
EXP-ECDLP-502ae2 left one route open: the chain's equations are triangular, so a block order that eliminates the chain variables first might undo the loss that plain DRL showed. This experiment tests that on the same $m = 3$ instances with both solvers.

== Observation
#figure(image("block-order-vs-L.svg", width: 100%), caption: [Median basis time per arm vs $L$ (measured); bars min–max over completed instances; × = every instance timed out at 600 s; $n = 6$ per cell. Runs RUN-01 ($L = 3..6$) and RUN-03 ($L = 7$).])

#table(columns: 2, stroke: 0.4pt, [*frozen criterion block*], [*derived from the recorded medians (criteria.json)*],
[msolve A_elim vs B],[`{"jointly_completed_L": [3, 4, 5, 6], "a_faster": 0, "ratio": {"L3": 1.3, "L4": 1.91, "L5": 2.31, "L6": 1.96}, "largest_L": {"A_elim_ms": 6, "B_ms": 6}, "retired_at": {"A_elim_ms": 7, "B_ms": 7}}`],
[Singular A_block vs B],[`{"jointly_completed_L": [3, 4], "a_faster": 0, "ratio": {"L3": 1.61, "L4": 1.43}, "largest_L": {"A_block_sg": 4, "B_sg": 5}, "retired_at": {"A_block_sg": 5, "B_sg": 6}}`],
[dynamic range A_drl vs A_elim (msolve)],[`{"jointly_completed_L": [3, 4], "a_faster": 0, "ratio": {"L3": 4.43, "L4": 16.81}, "largest_L": {"A_drl_ms": 4, "A_elim_ms": 6}, "retired_at": {"A_drl_ms": 5, "A_elim_ms": 7}}`],
[elim_equals_B],[`{"L3": "6/6", "L4": "6/6", "L5": "6/6", "L6": "6/6"}`]
)

_Paired per-instance ratios (supplementary, not a frozen criterion): the two arms run on the same instance; median of the ratios with a 95% percentile bootstrap interval (4000 resamples, deterministic seed). Intervals are wide for n = 4..6 and are reported as such._

#table(columns: 5, stroke: 0.3pt, [*pair*],[*L*],[*n*],[*median ratio*],[*95% CI*],
[ms A elim over B],[L3],[6],[1.34],[1.11–1.58],
[ms A elim over B],[L4],[6],[1.86],[1.82–2.04],
[ms A elim over B],[L5],[6],[2.27],[2.18–2.35],
[ms A elim over B],[L6],[6],[1.94],[1.78–1.99],
[sg A block over B],[L3],[6],[1.60],[1.52–1.64],
[sg A block over B],[L4],[6],[1.42],[1.33–1.73],
[ms A drl over A elim],[L3],[6],[4.57],[3.71–4.95],
[ms A drl over A elim],[L4],[6],[16.21],[15.58–17.91]
)

#table(columns: 6, stroke: 0.3pt, [*L*],[*arm*],[*ok/to/deg*],[*median ms [min–max]*],[*planted*],[*max F4 deg*],
[3],[A_block_sg],[6/0/0],[121 [112–130]],[4/4],[—],
[3],[A_drl_ms],[6/0/0],[146 [133–160]],[4/4],[12],
[3],[A_elim_ms],[6/0/0],[33 [27–41]],[4/4],[14],
[3],[B_ms],[6/0/0],[25 [19–32]],[4/4],[16],
[3],[B_sg],[6/0/0],[75 [74–80]],[4/4],[—],
[4],[A_block_sg],[6/0/0],[7,329 [7,116–7,984]],[4/4],[—],
[4],[A_drl_ms],[6/0/0],[9,933 [8,947–10,140]],[4/4],[13],
[4],[A_elim_ms],[6/0/0],[591 [512–642]],[4/4],[32],
[4],[B_ms],[6/0/0],[309 [277–336]],[4/4],[24],
[4],[B_sg],[6/0/0],[5,112 [4,472–5,458]],[4/4],[—],
[5],[A_block_sg],[0/6/0],[— [—–—]],[—],[—],
[5],[A_drl_ms],[0/6/0],[— [—–—]],[—],[—],
[5],[A_elim_ms],[6/0/0],[16,183 [14,145–16,526]],[4/4],[65],
[5],[B_ms],[6/0/0],[6,993 [6,559–7,195]],[4/4],[40],
[5],[B_sg],[6/0/0],[370,938 [274,132–376,859]],[4/4],[—],
[6],[A_elim_ms],[6/0/0],[411,159 [347,985–418,707]],[4/4],[133],
[6],[B_ms],[6/0/0],[210,271 [194,599–213,522]],[4/4],[72],
[6],[B_sg],[0/6/0],[— [—–—]],[—],[—],
[7],[A_elim_ms],[0/6/0],[— [—–—]],[—],[—],
[7],[B_ms],[0/6/0],[— [—–—]],[—],[—]
)

== Comparison
- *The order matters a lot, then stops mattering:* plain DRL over the block order, $4.6 times$ at $L = 3$ and $16 times$ at $L = 4$ (dynamic-range control passes). The block-order chain is then about $2 times$ the dense arm, flat in $L$ within the intervals (1.34, 1.86, 2.27, 1.94), not growing like the plain-DRL gap (8× → >79×).
- *Same ideal:* the eliminated chain basis equals the dense basis on all 24 instances where both finished, so the extra cost is the chain rows and the path, not a different problem.
- *Singular agrees in sign:* block-order chain 1.6× and 1.4× at $L = 3, 4$, retired at $L = 5$ against the dense arm's $L = 6$.
- *Exploratory (not preregistered):* msolve's maximum F4 degree on the dense arm is $2^L + 8$ on every instance; on the chain arm with block order it is 14, 32, 65, 133 for instances that have a solution (about $2^(L+1)$) and close to the dense value on instances with no solution (7 of 8 of those have the unit ideal as basis, which ends the computation early). Treat as a lead, not a result.

== Inference
A block order recovers the chain's plain-DRL loss but leaves a roughly constant factor of about 2 over the dense encoding for $L = 3..6$ under both solvers; it does not make the chain competitive, and the retirement comparison at $L = 7$ is a tie of right-censored cells. The $L$-independent-degree route is not supported (the degree observation points the other way).

== Limitations
- Toy scale: $m = 3$, 10–22-bit primes; $n = 6$ per cell (percentile bootstrap at $n = 6$ is coarse). Only one block-order configuration per solver; other weighted or interleaved orders untested.
- All twelve $L = 7$ solves are right-censored at 600 s: they set the retirement $L$ under the frozen stopping rule and say nothing about relative cost. The ratio's trend beyond $L = 6$ is unmeasured; the validator's probes show memory growing about 17–19× per $L$ (A: 2.7 GB, B: 1.3 GB at $L = 6$), so it may bind at $L = 7$.
- Process: RUN-01 was killed by the host 2-hour limit in $L = 7$; RUN-02 (the AMD-01 re-run) was lost to a VM recycle; RUN-03 (AMD-02) ran $L = 7$ for the two arms the stopping rule had not retired. No 17-bit prime was used, so msolve's crash on 17-bit primes (CORR-20261019-e6f65b) affects no value here. Resource records (peak memory, CPU time) were not kept in the run receipts.

== Next actions
+ Account for F4 matrix dimensions (msolve `-v 2` logs) for chain vs dense per $L$, the first discriminating experiment in the reframed problem.
+ Read the $m = 4$ experiment (EXP-ECDLP-8c41d7) for the $m$-dependence of the constant factor.
+ No further P-256 work on this route unless some order or encoding beats the dense and random controls on the frozen grid.

