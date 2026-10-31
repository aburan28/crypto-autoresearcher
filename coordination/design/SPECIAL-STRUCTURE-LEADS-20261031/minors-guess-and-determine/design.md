# Design: LEAD-EXO-minors-guess-and-determine (design only, nothing run)

## Lead and question
New lead (not in the atlas; `--match` finds nothing). Toy claim boundary only. Question: at 20-40 bit prime orders, what is the charged cost (field-multiplication equivalents, FM) of a minors guess-and-determine search for a planted discrete log versus matched negation-map rho on the same instances, and is the fitted exponent below or above 0.5?

## What the lead already says
Nothing directly. Neighbours: LEAD-ICE-generic-oracle-arity-cost-floor (closed_obstructed: product law, zero sub-rho cells for ENUM/MITM oracles; CHW 2026/384 structured generic-group bound); LEAD-EXO-curve-model-representation (closed_obstructed: model changes give constants only); KR-IC-401ebf (naive Semaev IC over F_p no better than generic, heuristic); KR-IC-cd159a (lifting/xedni fails); LEAD-RHO-matched-rho-calibration (toy rho carries set-up bias, alpha 0.31-0.45; this study must report rho's own fitted exponent, not assume 0.5).

What the four papers state (abstract pages only; full texts and PDFs NOT opened):
- 1703.07544: Las Vegas algorithm, "not generic", depends on a property of E(F_q), similar to index calculus. No matrix, guess, bound or measurement on the page.
- 2005.05039: "conjecture of initial minors" via Schur complements; code written; "solved groups of order up to 2^50". No matrix, bound or cost.
- 2310.04132: earlier work "tried to find a zero minor in a matrix over the same finite field"; results "mostly computational". Nothing else on the page.
- 2607.09814: reduces ECDLP to finding a zero minor of a matrix; finds it with the intersection poset of a hyperplane arrangement; "complexity and success probability" discussed. The page does not say what "guess" means, the matrix size or entries.
So the matrix, the guessed object and the cost are unread. Everything below is a reconstruction.

## Reconstructed algorithm (implementable; every choice is an open question)
Basis f_1..f_n of the Riemann-Roch space L(nO): n=2: 1,x; n=3: 1,x,y; n=4: 1,x,y,x^2. For columns c_j = (f_i(R_j))_i with R_j in B = {iP : 1<=i<=M} U {Q+jP : 1<=j<=M}, M = ceil(sqrt N), an n x n minor vanishes iff its n points are zeros of a function with pole divisor nO, i.e. sum to O. A minor mixing both families gives a (a)P=(b)Q relation, so k = a/b mod N. Guess: n-1 columns (one from each family at least); determine: the cofactor vector h of the (n-1) x n submatrix, then scan all 2M columns for h.c = 0 (a dot product of length n). Guess count is the number of (n-1)-subsets tried until a hit; the poset-based ordering of 2607.09814 is replaced by random order (open question). n=2 is exactly a collision search (BSGS-equivalent) and is the built-in sanity case. Success probability per scan is about 2M/N.

## Hypotheses
H0 (the lead's own analysis, expected): the search is an n-sum relation search in determinant clothing; cost has exponent >= 0.5 in N and is above matched rho at all sizes (expected loss). The reconstructed n=2 variant should land near BSGS cost, above rho.negation. H1: some size or the fitted exponent shows minors below rho. Falsifier of the closure: alpha_minors upper 95% bound < 0.5, or FM ratio minors/rho < 1 with interval excluding 1 at a size >= 32 bits.

## Instances
Sizes log2 N in {20,24,28,32,36,40}; 24 instances each (144). Curve: `generate_prime_order_curve(bits, seed=i)` from `src/crypto_autoresearcher/index_calculus/curve.py` (certified prime order), order cross-checked by PARI `ellcard` (probe: `echo 'print(ellcard(ellinit([1,3],1000003)))' | gp -q` printed 1000894, confirming gp is available; a probe only). k = SHA-256(protocol_sha256|size|i) mod N, Q = kP. All seeds are SHA-256 of the protocol hash and (arm,size,instance,replicate), frozen by rule.

## Arms and controls
Reference rho-neg (negation map, 32-adding walk, distinguished points; reuse `index_calculus/rho.py` semantics, and port to Rust per `ic_boundary::RhoWalk` in the crypto repository, whose presence is not assumed). Candidate minors-recon (n=2,3,4 all run; headline = smallest median per size, declared up front). A/A: rho-neg-aa, disjoint seeds. Negative: minors-randmat, same shape and charging on uniform columns; a saving relative to it is attributable to curve structure (claim C3). Positive: minors-planted, all prime-order curves of 12-20 bits (must recover k) plus a matrix with an injected dependent column set (must find it); a miss voids the arm. Baseline role not used (rho is the reference).

## Counted metrics
FM = M + S + 10 I (inversion weight 10 fixed; sensitivity 5 and 40 reported). Charged: every curve addition and doubling used to build columns (affine: 1I+2M+1S; doubling 1I+2M+2S), every function evaluation (x^2, xy products), every elimination step of every determinant or cofactor computation (counting field type, no uncharged shortcut), every dot product in the scan, rho's walk, step table, starting points and the negation-map canonicalisation (0 multiplications, listed as uncharged counter). Uncharged to all arms equally: curve setup and order computation. Secondary: determinant count, GAE (ecbench-compatible), censored fraction. Wall time is never a metric. Cap 2^40 FM per row; capped rows are right-censored lower bounds, not costs. Exponent: OLS slope of log2 median FM on log2 N over sizes with >= 20/24 completed rows.

## Decision rule
Confirm closure (closed_obstructed, measured, toy, reconstructed variant): alpha_minors lower bound > 0.5, minors above rho at every fitted size, no saving versus random matrix. Reopen with next_action = full-text re-implementation and larger sizes: alpha_minors upper bound < 0.5, or ratio < 1 at >= 32 bits, or log-ratio slope interval wholly below 0. If random-matrix is as cheap as the curve matrix, the curve gives no structure. Positive-control miss: invalid_measurement. Fewer than 4 fitted sizes: inconclusive. p-value arithmetic: 9999 permutation resamples, min p 2/10000 = 2e-4 < alpha/m = 0.05/4 = 0.0125 (Bonferroni, m=4). This resolves a ratio of about 1.5x, not 10 percent.

## Inadmissible moves
Changing sizes, n, M, FM weights, seeds or guess order after data; dropping column-generation or evaluation cost; reading a capped row as a cost; selecting instances; attributing results to the papers' full algorithms; extrapolation beyond 2^40.

## Cost estimate
Implementation 3-4 days (Rust: field type with counters, determinant/cofactor, rho port or FFI to existing; Python orchestration). Compute: rho trivial (<= 2^21 steps at 40 bits). Minors cost is a model: n=2 about sqrt(N) scale; n>=3 expected larger; 2^40 FM cap x up to 36 capped rows is the bound, about 8 h on one 4-core host worst case, under 1 h if minors completes below 2^30 FM.

## Implementation plan and independent checker
Reuse `curve.py`, `rho.py`, `representation_controls.py` for curve generation and the Python rho reference. Rust binary `minors_probe` with counting field arithmetic; Python harness writes records.jsonl and the export via `experiment_protocol.py from-rows`. Checker: separate Python script, no shared code, recomputes the order via PARI, checks [k]P=Q, re-derives the seeds, replays a nonce sample of recorded inputs through its own big-integer counting implementation of the declared charging rules and compares FM exactly; tamper test flips one count and one relation and must fail.

## Open risks
(1) Biggest: the reconstruction may not be the papers' algorithm; a loss of the reconstruction does not close the papers. Full texts must be read (not opened here) before the Coordinator freezes. (2) The papers' 2^50 solves suggest a structure or success regime not visible in abstracts (a "defect" parameter, group structure condition); prime-order curves may be a hostile family, so a composite-order or smooth-cofactor family may be needed for the positive control. (3) Rho toy bias (alpha < 0.5) can flatter the reference at small sizes. (4) Inversion weight is a convention; sensitivity reported. (5) 2^40 cap may censor minors at 36-40 bits, leaving 4 fitted sizes at best.
