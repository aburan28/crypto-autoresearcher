# Design: specialising the Legendre unbounded-rank family at t0 (control)

Protocol: `protocol.json` (ULMER-SPEC-CTRL-001, draft, `validate.txt` = OK). Probes in `probe/` are feasibility probes (p <= 31, under a second each), not results.

## Lead and question
LEAD-TRF-function-field-xedni-lift and LEAD-ICP-xedni-function-field-sections (both closed_obstructed) reopen on "a surface with a dimension surplus whose lift exponent is below 1/2". Candidate C1 offers the Legendre curve over F_p(u), u^(p+1)=t0. Question: do the known sections of the fibre L_t0 behave like a random subset of E(F_p) (coverage, mu_(p+1)-characters), and does a lift finder beat generic meet-in-the-middle (MITM), and if so does the complete discrete-log cost stay above matched rho?

## What the lead already says
alpha = 3 (EV-XEDN-001) holds for rational surfaces with frozen shapes only. LEAD-EXO-global-lift-height (open_next_step, T_section) and LEAD-TRF-global-lift-small-height (closed_known, KR-IC-cd159a) ask for a rank-growing lift. LEAD-ICP-pkm-tower-algebraic-oracle: torus F4 solving degree grows with N. Report C1 predicts: lift exists by counting, finder is a knapsack costing at least MITM, character structure null.

## Checks of the report (what I relied on)
- Explicit point verified: (u+1)^(d-1)=u^(d-1)+1 in char p. The "sections" are exactly the points with x in the norm-t0 coset, and P(u^p) = Frob P(u), so the usable items are traces Tr P(u), about (p+1)/2 of them.
- Probe: the null "traces ~ random subset" is already doubtful in E(F_p): distinct traces are ~25% of |E| versus 39% under the coupon model, and hit 2-3 of 6-8 square-class strata (x, x+1, x+t0 square classes are tied to N(1+u) and t0). Full 2-torsion forces |E| = 0 mod 4, so the test must live in the odd prime-order G (N >= |E|/16), stratified.
- Probe: every non-2-torsion trace has exactly 2 or 4 torus preimages (p = 23, 29, 31). That is a degree <= 4 polynomial in the torus parameter, so membership in the family is table-free and polylog(p). I did not verify this beyond p <= 31. If it holds, the report's "the finder is a knapsack, cost >= MITM" is wrong at w = 2.
- The report's permutation null for the character test is invalid: ell(zeta) = ell(c/zeta), c = u0^(p-1), so the null must permute whole orbits.
- Not used: Ulmer U_d (explicit points not retrieved; add only behind an on-curve gate); report arm (A) relation counts (generic, no discriminating power).

## Hypotheses
H0 (generic homomorphism): coverage and characters equal the random-subset control; complete-solve exponent 0.9 to 1.1, ratio to rho growing like N^(1/2) polylog. Expected loss of the route. Per-lift cost (P3): I predict the candidate IS below MITM (polylog versus ~2 sqrt(N)); the lead text predicts not. H1: a character bias depending on fibre or target, or a complete-solve exponent below 1/2.

## Instances
Legendre fibres y^2 = x(x+1)(x+t0), t0 in F_p \ {0,1}; F_(p^2) = F_p[s]/(s^2-n). p = largest prime below 2^k: k = 8..13 (coverage, character), k = 10, 12, ..., 22 (cost). Fibres: first T accepted in SHA-256('ulmer-ctl-v1'|p|i) order, accepted iff N >= |E|/16; T = 16 / 8. Targets: all of G (coverage); 64 per fibre by SHA-256 rule (cost). Items: Tr P(u) projected by the cofactor h into G. Seeds from the protocol hash.

## Arms and controls
- Arm 1 coverage: fraction of G (and of E(F_p), per 2E-stratum) that is a signed sum of <= w family traces, w = 1, 2 exhaustive; fraction of full-2-torsion isomorphism classes hit by fibres (p < 1100).
- Arm 2 characters: ell_j = log_G(h Tr P(g^j u0)); z = max over k, a <= 16 of the Fourier sum / sqrt(orbits); orbit-respecting null, 19,999 resamples; also the target-residual version log(Q - Tr).
- Arm 3 cost: reference mitm-ref (group elements only, K grid sqrt(N)*{1/4..4}, best per size); candidate torus-cand (random u1, solve degree-<=4 polynomial from S_3(x(tau), x(tau)^p, x(R)) = 0, accept; complete-solve variant on a subgroup coset of index ~sqrt(p+1) with sparse elimination mod N); baseline rho-base (rho with negation on G, same unit).
- Controls: A/A (candidate under a disjoint seed stream plus a seeded fibre split); positive (Q a known sum of 1-2 traces must be recovered 100%; planted periodic component at eps 0.05/0.10/0.25 must be detected, giving the sensitivity); negative (random subset of E(F_p) of the same distinct size, same orbits, through the same pipeline; its character p-values must be uniform, KS at 0.01). The table-free finder has no negative control (random subsets have no algebraic membership), stated.

## Counted metrics
Per-lift cost and complete cost in F_p multiplication equivalents: instrumented field type counts mul, sqr, inv; add 1I+2M+1S, double 1I+2M+2S; F_(p^2) mul 4M; hash insert and probe counted apart (and priced at 1M in a sensitivity row); totals at I/M in {1, 10, 30}; item generation and table setup charged; mult mod N in linear algebra charged as M and listed. Coverage is exact; the character statistic is rank against the null. No clock is a metric.

## Decision rule
- Closure stands (restated: relation count and linear algebra, not a knapsack): C2, C3 supported and C5 (complete exponent lower bound above 1/2, ratio to rho non-decreasing). C4 alone (per-lift below MITM) is a correction to the report, not a reopening.
- Reopen both leads: C5 fails (interval below 1/2, or ratio to rho falling to below 1), or a character bias that depends on t0 or Q reproduces across the A/A split, or coverage in G differs from the control at 4 of 6 sizes.
- Invalid: positive control misses eps 0.25, A/A outside the null, negative p-values non-uniform.
Falsifiers (brief): finder cost scaling below MITM (expected to fire, see above); a target-dependent character bias (expected not to).

## Inadmissible moves
Changing ladder, fibre rule, weights, K grid, subgroup rule or charges after data; per-lift gain read as a DL speedup; any finder reading a log table; coverage without strata; characters without the orbit null; per-instance MITM tuning; wall time; deployed-size curves.

## Cost estimate
Implementation 3-4 days (field and curve layer, torus root finder, MITM, rho, sparse elimination, checker). Compute: character null dominates, ~1e12 flops at k = 13, about 1-2 h on 4 cores; cost arm about 30 min; everything under 4 h wall on one 4-core host (estimate; replace by one timed call per arm before freezing).

## Implementation plan
Rust crate (new; no elliptic-curve Rust exists in this repo: experiments/EXP-ECDLP-84af7b/implementation is a number-field runner). Python orchestration only. Reuse for design reference and the checker: `src/crypto_autoresearcher/index_calculus/{rho.py (walk_ops/setup_ops split), semaev.py (s3), polyfp.py (roots), curve.py (OpCounter, sqrt_mod), linalg.py}`, `tools/experiment_protocol.py` (validate, seeds, blind, from-rows). ecbench named as target backend only if the Coordinator wants the harness unit; nothing here depends on it.

## Independent checker
Python, no code shared with the Rust runner: recomputes |E|, N, G, every claimed representation Q = sum of signed traces from the recorded u values with its own F_(p^2) arithmetic, recomputes coverage for a nonce-sampled 10% of fibres, re-derives the Fourier maximum and null p-value on a sample, replays recorded counters on a sampled row against its own instrumented count. Tamper test: flip one recorded u, one coverage bit and one counter; each must be caught.

## Open risks
Degree-4 preimage claim verified only to p = 31; cost of the complete-solve variant depends on a subgroup-membership rule I have not implemented; I could not reconcile the report's "Gaudry n = 2 tie" with a group G of size ~p (my estimate: exponent 1 versus rho 1/2); k = 8..13 may be too small for the cofactor rule to yield enough fibres at k = 8 (fallback is a listed T reduction, decided before data); character sensitivity at small N may be coarse.
