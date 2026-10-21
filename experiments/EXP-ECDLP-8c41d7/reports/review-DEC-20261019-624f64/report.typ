#set page(paper: "a4", margin: 1.7cm, numbering: "1")
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: "1.")
#show table: set text(size: 8pt)

= Evidence review: the chain-first block order at $m = 4$

*Decision* DEC-20261019-624f64: *reject_scoped* (scope widened to $m = 4$) · *evidence* EV-ECDLP-a3659c (contradicts, preliminary, toy tier) · *validation* VAL-20261019-0cb05d (passed, with concerns) · *runs* RUN-ECDLP-8c41d7-01 .. -04 · *experiment* EXP-ECDLP-8c41d7 · *goal* GOAL-ECDLP-001.

*Scoped claim.* For Semaev $m = 4$ on toy primes (9–19 bits, $L = 2..4$), the chain encoding with the chain variables eliminated first is not faster than the dense encoding of the same set: msolve paired median ratios 1.12 and 1.22 at $L = 2, 3$ (and 1.2× at $L = 3$ in the preregistered medians), Singular 2.3 and 4.9; at $L = 4$ the dense msolve arm completes (518–586 s, cap 600 s) while the chain arm times out on every instance. Only $L = 2, 3$ give uncensored paired comparisons.

== Question
The proposed $P$-256 route needs $m = 6$, so the $m$-dependence of the chain/dense gap matters. EXP-ECDLP-20a588 found a roughly constant factor of about 2 at $m = 3$ under the block order; this experiment adds $m = 4$ (five-point decomposition, $S_5$ of degree 8 in each of four variables) with the same arms, instruments and controls.

== Observation
#figure(image("block-order-vs-L.svg", width: 100%), caption: [Median basis time per arm vs $L$ (measured); bars min–max over completed instances; × = every non-degenerate instance timed out at 600 s; $n = 5$–6 per cell (one degenerate planted target at $L = 3, 4$). The $L = 4$ column mixes two primes: Singular arms at $p = 65551$, msolve arms at $p = 262271$.])

#table(columns: 2, stroke: 0.4pt, [*comparison*], [*derived from the recorded medians (criteria.json)*],
[msolve A_elim vs B],[jointly completed L = [2, 3]; A_elim_ms faster in 0 of 2 cells; median ratio A_elim_ms/B_ms by L: L2: 1.13, L3: 1.21; largest L completed: A_elim_ms 3, B_ms 4; retired (every non-degenerate instance timed out) at L: A_elim_ms 4, B_ms None],
[Singular A_block vs B],[jointly completed L = [2, 3]; A_block_sg faster in 0 of 2 cells; median ratio A_block_sg/B_sg by L: L2: 2.31, L3: 4.9; largest L completed: A_block_sg 3, B_sg 3; retired (every non-degenerate instance timed out) at L: A_block_sg 4, B_sg 4],
[dynamic range A_drl vs A_elim (msolve)],[jointly completed L = [2, 3]; A_drl_ms faster in 0 of 2 cells; median ratio A_drl_ms/A_elim_ms by L: L2: 1.61, L3: 4.75; largest L completed: A_drl_ms 3, A_elim_ms 3; retired (every non-degenerate instance timed out) at L: A_drl_ms None, A_elim_ms 4],
[elim_equals_B],[eliminated chain basis equals the dense basis: L2: 6/6, L3: 5/5]
)

_Paired per-instance ratios (supplementary, not a frozen criterion): the two arms run on the same instance; median of the ratios with a 95% percentile bootstrap interval (4000 resamples, deterministic seed). Intervals are wide for n = 4..6 and are reported as such._

#table(columns: 5, stroke: 0.3pt, [*pair*],[*L*],[*n*],[*median ratio*],[*95% CI*],
[ms A elim over B],[L2],[6],[1.12],[0.97–1.27],
[ms A elim over B],[L3],[5],[1.22],[1.12–1.27],
[sg A block over B],[L2],[6],[2.33],[2.20–2.53],
[sg A block over B],[L3],[5],[4.90],[4.85–5.31],
[ms A drl over A elim],[L2],[6],[1.61],[1.48–2.13],
[ms A drl over A elim],[L3],[5],[4.80],[4.55–4.93]
)

#table(columns: 6, stroke: 0.3pt, [*L*],[*arm*],[*ok/to/deg*],[*median ms [min–max]*],[*planted*],[*max F4 deg*],
[2],[A_block_sg],[6/0/0],[113 [109–127]],[4/4],[—],
[2],[A_drl_ms],[6/0/0],[40 [38–63]],[4/4],[32],
[2],[A_elim_ms],[6/0/0],[25 [23–28]],[4/4],[32],
[2],[B_ms],[6/0/0],[22 [20–27]],[4/4],[32],
[2],[B_sg],[6/0/0],[49 [48–50]],[4/4],[—],
[3],[A_block_sg],[5/0/1],[344,621 [344,433–349,883]],[3/3],[—],
[3],[A_drl_ms],[5/0/1],[61,421 [59,168–62,017]],[3/3],[32],
[3],[A_elim_ms],[5/0/1],[12,929 [11,990–13,389]],[3/3],[32],
[3],[B_ms],[5/0/1],[10,700 [10,378–10,976]],[3/3],[32],
[3],[B_sg],[5/0/1],[70,364 [65,931–71,061]],[3/3],[—],
[4],[A_block_sg],[0/5/1],[— [—–—]],[—],[—],
[4],[A_drl_ms],[0/4/1],[— [—–—]],[—],[—],
[4],[A_elim_ms],[0/5/1],[— [—–—]],[—],[—],
[4],[B_ms],[5/0/1],[582,996 [518,230–586,271]],[3/3],[40],
[4],[B_sg],[0/5/1],[— [—–—]],[—],[—]
)

== Comparison
- *msolve:* chain-first block order over dense, same instances: 1.12× ($L = 2$, interval 0.97–1.27, a difference of about 3 ms) and 1.22× ($L = 3$, interval 1.12–1.27, $n = 5$). With plain grevlex the chain is 1.6× and 4.8× the block order, so the order again recovers most of the loss. At $L = 4$ the dense arm completes in 518–586 s on all non-degenerate instances while the block-order chain exceeds the 600 s cap on all of them: the chain arm is at least 1.02–1.16× the dense arm per instance there.
- *Singular:* chain over dense 2.3× ($L = 2$) and 4.9× ($L = 3$), larger than at $m = 3$ (1.6×); both Singular arms time out on all instances at $L = 4$ (a tie).
- *Compared with $m = 3$:* the msolve ratio at $L = 3$ is similar (1.3× at $m = 3$, 1.2× at $m = 4$), so the msolve gap does not visibly grow with $m$ at these sizes; the Singular gap does.
- *Cap sensitivity (validator):* the $L = 4$ retirement comparison is knife-edge on the 600 s cap, because the dense arm finishes 2.3–2.8% below it on planted instances; the clause becomes a tie if the cap fell below 583 s. The falsification verdict does not depend on it: the first clause (chain not faster in every jointly completed cell) holds for any cap of at least 14 s (msolve) or 350 s (Singular).

== Inference
The block-order chain does not beat the dense encoding at $m = 4$ under either solver, and under msolve the constant factor at $L = 3$ is about the same as at $m = 3$. The data cannot say whether the factor grows at larger $L$ or $m$: $L = 4$ is censored, only $L = 2, 3$ are uncensored, and the $L = 2$ difference is milliseconds.

== Limitations
- Toy scale: $m = 4$, $L <= 4$, primes up to 19 bits, single-threaded, 600 s cap; $n = 5$ at $L = 3, 4$ because of a degenerate planted target (sum equal to the point at infinity). Random targets have the trivial basis $[1]$ at every $L$; planted-only gives the same verdicts.
- *Mixed-prime $L = 4$ cell.* RUN-03 ran every arm at $p = 65551$, but msolve 0.6.5 segfaults on 17- and 18-bit primes (range widened by NOTE-01 and the validation; CORR-20261019-e6f65b). AMD-03 re-ran only the msolve arms at $p = 262271$ (filed after RUN-03's data was seen). Comparisons within a solver family share instances and are valid; any $L = 4$ contrast between msolve and Singular confounds solver, prime and instances.
- *Interruptions:* RUN-01, RUN-02 lost to VM restarts in $L = 3$ and $L = 4$; resumed under AMD-01 and AMD-02 with launcher, seeds, arms, timeout and stopping rule unchanged.
- One $A$\_drl\_ms solve at $L = 4$ was killed (signal 9) after 184 s; the validator measured that arm alone reaching 3.4 GB by 200 s, so four concurrent copies may have exceeded memory (unproven). It is counted as a failure, not a timeout, so that arm is not retired at $L = 4$.
- Positive control at $L = 4$ covers only the dense arm (3 planted); the elimination-equals-dense control is not evaluable there because the chain arm never finished.

== Next actions
+ Matrix-size accounting for chain vs dense (msolve `-v 2`), the first discriminating experiment of the reframed problem.
+ If $m$-dependence is to be measured further, run $L = 3$ with more instances at $m = 4$ and, with a prime outside the msolve crash range, $m = 2$ and larger $L$ — a new protocol.
+ No further P-256 work on this route unless some order or encoding beats the dense and random controls on the frozen grid.

