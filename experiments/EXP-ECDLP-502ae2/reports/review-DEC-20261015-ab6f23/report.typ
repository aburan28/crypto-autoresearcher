#set page(paper: "a4", margin: 1.7cm, numbering: "1")
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: "1.")
#show table: set text(size: 8.5pt)

= Evidence review: the isogeny-chain factor base under an F4 solver

*Decision* DEC-20261015-ab6f23: *reject_scoped*, scope widened to msolve · *evidence* EV-ECDLP-7e970a (contradicts, replicated, toy tier) · *validation* VAL-20261015-280100 (passed) · *run* RUN-ECDLP-502ae2-01 · *experiment* EXP-ECDLP-502ae2 · *predecessor* EXP-ECDLP-f49f75 (DEC-20261015-a08389, Singular) · *goal* GOAL-ECDLP-001.

*Scoped claim.* On the same $m = 3$ instances as EXP-ECDLP-f49f75 ($p$ 10–22 bits), msolve 0.6.5 (F4 + FGLM) solves the 2-isogeny-chain encoding of the factor-base set more slowly than the dense encoding of the same set and no faster than a random set, and the chain arm is retired first. The Singular-only rejection of H-ECDLP-60de36 extends to this F4 solver.

== Question

DEC-20261015-a08389 left one obvious objection open: Singular's `std`/`slimgb` are Buchberger-type algorithms, and the chain's many low-degree equations are exactly the structure F4-style linear algebra is meant to exploit. This experiment re-ran the identical $m = 3$ instances under msolve.

== Observation

#figure(image("msolve-cost-vs-L.svg", width: 100%), caption: [Median full-solve time (msolve `-P 1`, measured) vs $L$; dotted: Singular on the same instances; × = all instances timed out at 600 s. Right: maximum F4 degree reached. n = 6 per cell.])

#figure(image("ratios.svg", width: 78%), caption: [A/B median-time ratio (derived from measured medians, `summary.json`). The basis-only ratio isolates F4 from msolve's `-P 1` genericity retries, which inflate A's full-solve time about 5× (validator check 4c). At $L = 5$ A's basis step timed out on 6/6, so the bar is a lower bound.])

#table(columns: 3, stroke: 0.4pt,
[*frozen criterion*], [*threshold*], [*observed*],
[A faster than B in jointly completed cells], [≥ 80% supports; A ≥ B in ≥ 80% falsifies], [0/2 faster (L = 3: 16.5×, L = 4: 150× slower)],
[retirement], [A must complete a larger L than B and C], [A retired L = 5; B, C retired L = 7],
[positive control], [100%], [32/32 planted points satisfy msolve's reduced basis],
)

== Comparison

- *Robust to the instrument's solve step:* basis-only ratios are 8.0×, 30.5× and > 79× at $L = 3, 4, 5$.
- *Lower degree, higher cost:* the chain keeps the maximum F4 degree at 12–13, while the dense arms climb 16 → 24 → 40 → 72 (≈ the univariate degree $2^L$). With $3L$ variables the F4 matrices still grow faster than the degree saving helps.
- *No structure seen:* B (isogeny set) and C (random set) cost the same; enumeration needs 629 group operations at $L = 5$.
- *Across instruments:* msolve is faster than Singular on the dense arms from $L = 4$ (Singular/msolve ≈ 2.8–11× at $L = 4, 5$ for `std`) but not on the chain arm (≈ 0.2–0.8×). The secondary ratio divides Singular's internal timer by msolve wall time and is indicative only.

== Inference

Moving from Buchberger to F4 does not rescue the chain encoding. The question that DEC-20261015-a08389 left open — instrument dependence — is answered negatively for the obvious F4 solver. The decomposition step needed for the proposed $N^(1/3)$ P-256 route remains without any toy-scale signal.

== Limitations

- $m = 3$ only, toy primes, msolve 0.6.5 single-threaded, DRL in the launcher's variable order, `-c 2`, 600 s per step. Block or elimination orders that exploit the chain's triangular shape, other F4/F5 implementations and $m >= 4$ were not tested. msolve 0.6.5 crashes on the $m = 2$, $L = 8$ dense system, so $m = 2$ was not re-run.
- At $L = 6$ the dense arms completed only the two random (empty-variety) targets; counting planted instances only, B and C reach $L = 5$ against A's $L = 4$ — same verdict.
- `-P 1` over tiny fields sometimes lists an incomplete solution set (both arms, random); "solve ok" means msolve finished. No peak-memory record in the run (validator measured 252 MB for A, 20 MB for B at $L = 4$).

== Next actions

+ Problem record stays open; the F4 unblock path is tested and negative. Remaining routes: a block order eliminating the chain variables first, and an $L$-independent degree-of-regularity argument.
+ No further P-256 work on this route unless one of those beats the dense and random controls on this frozen grid.
