# Arithmetic-rigidity control (family A, C1)

## Lead and question
Does the charged cost of negation-map rho, and of one fixed small-x index-calculus (IC) engine, depend on the arithmetic of (p, N, t, D, conductor f, h(D), p+-1, N+-1) beyond N and |Aut|? Toy and public parameters only; planted logs on curves built here.

## What the lead already says
LEAD-STR-isogeny-class-generic-invariance (closed, theorem T1 plus 403,168-run census) varies the curve only inside a fixed (p, N). LEAD-ICE-curve-presentation-invariance is also within-class. LEAD-EXO-augmented-oracle-ggm and KR-RHO-13bf67 give the theorem side. LEAD-RHO-matched-rho-calibration leaves an unexplained toy excess (1.453x floor, alpha 0.398 [0.308, 0.476]). The lead's own prediction is a null; nobody has varied (p, N, t) at fixed size.

## Hypotheses
H0 (expected): every preregistered invariant moves ln S by less than the margin (0.05 for rho, 0.15 for IC, per SD or per stratum). H1: some invariant does. For rho any effect is instrument bias, not mechanism. For IC the small-x factor base is an integer-lift object, so a constant-level effect is possible. I expect H0 for rho; IC is the only live uncertainty.

## Instances
All curves are made by one gp (PARI 2.15.4) generator, so the downstream path is identical. Per size bin (24, 28, 32, 36, 40 bits) and per stratum, 6 curves; curve = first hit of a stream seeded by sha256(protocol hash|stratum|bin|index).
- Random A (12/bin) and random B (12/bin, |ln N/N_A| <= 0.01): the A/A pair.
- S1 Hasse boundary (|t| >= 2sqrt(p) - 2^8, D0 in {-3,-4,-7,-8,-11,-19,-43,-67,-163}); S2 small |D0|, |t| < 2^8; S3 large conductor (v >= 8, h(D) <= 200); built by polclass(D), a root j mod p, ellfromj, with N or its twist prime.
- S4 N-1 2^10-smooth; S5 p-1 smooth; S6 N+1 and p+1 smooth; S7 p = 2^k - c, c < 2^(k/4), random curve.
- Each stratum curve is N-paired to a random-A curve. j=0 and j=1728 curves are excluded from these strata.
- Positive-control j=0 set: 30 curves. Presentation control: 90 stratum curves re-run on a random isomorphic model.
- IC arm: bins 24, 26, 28 only, 12 random and 4 per stratum per bin (120 curves, 3 solves). Total 330 rho curves plus the controls.
Recorded exactly per curve: p, a, b, N, t, j, base point, planted k, End conductor (smallest u | v with polclass(D0 u^2)(j) = 0), D0, h(D), factorisations of N+-1 and p+-1, p mod 8 and 12, embedding-degree bucket, special-form flag.
Probe (not a result): gp built CM curves with prime N at 30 bits for D=-163 and D=-147 in 7.5 s; D=-163, 32 bits gave 50 curves with prime N and N-1 2^10-smooth per 400k tries; a Hasse-boundary search for D=-7 returned 0 in one run (the sieve needs tuning); IC solves took 1.3 s at 24 bits, 10 s at 28 bits, over 50 s at 32 bits, hence the IC cap at 28.

## Arms and controls
Reference: rho-random-A. Baseline: ic-random. Candidates: rho-strata, ic-strata. A/A: rho-random-B (N-matched random set) and rho-presentation (same curve, isomorphic model, separates construction route from invariants). Positive: rho-injected-dose (counting layer multiplies S by 1.03, 1.05, 1.10 on a sealed-key invariant bin, same code path; must be detected at 5% in at least 90% of 200 replays) and rho-aut-j0 (Aut-quotient walk against negation-only walk on the same j=0 curves, expected ln ratio -0.549, since 6 against 2 gives sqrt(1/3)). Negative: rho-null-synthetic (S redrawn from the generic rho law at each real curve's N and invariants, 1000 datasets, family-wise rejection at most 0.05). BSGS is a built-in zero: its table is target independent, so only N moves it.

## Counted metrics
Primary: ln(mean S / sqrt(pi N / 4)) over 64 verified rho runs per curve; ln(mean s3_solves) over 3 IC solves. S counts every add and double after the target is known: 20 table entries, walk starts, look-ahead retries, cycle escapes, abandoned walks. Charges: add = 1 inv + 2 mul + 1 sqr; double = 1 inv + 2 mul + 2 sqr; canonicalisation = 1 negation, in its own uncharged counter, with DP storage and verification also reported uncharged. IC group_ops, la_ops, relations and attempts are separate columns, never summed. No clock is read; a special-form reduction cost is invisible to counts, so no step-cost claim is possible.

## Confounding with N
(1) Response divided by the exact floor at exact N. (2) Size-bin fixed effects plus ln(N/2^bin) absorb the finite-size excess R(N) = 1 + c/N^beta. (3) Invariants are scale-free (log f/log p, log P+(N-1)/log N, |t|/2sqrt(p), h/sqrt|D|), so they are not proxies for N. (4) Pairing by N within 1%; report VIF (flag above 5) and the partial R^2 of ln N. (5) Permutations are within size bin. (6) Stratum is not a random effect, because that would absorb the invariants under test; it enters only through clustered SEs and paired contrasts. Rho S has CV about 0.52, so 64 runs give SE 0.065 per curve.

## Decision rule and dispositions
Model: OLS of ln S on bin effects, ln N and 12 standardised invariants (theta, f_End, D0, h, four smoothness terms, p mod 8, p mod 12, special-form flag, embedding bucket), stratum-clustered SE. Freedman-Lane max-T permutation, N = 19999 resamples, so the minimum p is 2/(N+1) = 1.0e-4, below alpha/m = 0.05/26 = 1.9e-3 (12 invariants x 2 meters plus 2 held-out omnibus tests; Holm). The omnibus fits ridge plus boosted trees on a hash-assigned 2/3 and tests predictive gain on the held-out 1/3.
- Confirms the closure: all CIs inside the margin and every control passes; the atlas gets one measured row, and no future idea built on arithmetic numbers is admitted without escaping it.
- FALSIFIES the disposition: an IC invariant with Holm p < 0.05, |effect| above 0.15, replicated on the held-out third. That reopens a constant-level IC lead (next step: 30-bit replication). Any rho effect is instrument bias and reopens LEAD-RHO-matched-rho-calibration.
- Failed positive control, A/A or null: invalid, nothing is concluded. Rare strata are inconclusive when SE exceeds the margin.

## Inadmissible moves
Changing strata, invariants, margins or unit after a look; replacing a curve after its cost is known; a clock as step-cost evidence; a non-preregistered correlation presented as a finding; any claim past 40 bits or about deployed curves; a null without the passing 5% positive control.

## Cost
Rho runs (about 31k, estimate not measured): about 3 CPU-hours, dominated by the 40-bit bin, so about 1 hour on 4 cores. IC about 30 minutes. Generation and gp checks about 30 minutes. About 2.5 hours wall including 20k permutations (pure Python, no numpy or scipy here). Implementation: about 3 days (Rust rho of ~600 lines, generator, adapter, analysis).

## Implementation plan
New Rust binary `tools/arithrig` (prime-field affine Weierstrass, u128 modmul, r-adding walk matching `src/crypto_autoresearcher/index_calculus/rho.py`'s documented guards). Reuse unchanged: `index_calculus` solve_index_calculus with a supplied Curve (thin adapter), `generate_prime_order_curve_j0` for the j=0 set, and `harness/endosweep/toyverify.py::cm_curve_from_class_polynomial` as a CM cross-check. gp does construction; Python only orchestrates and analyses. No Rust prime-field rho exists in this checkout (searched: only binary-field rho.c and Koblitz fixtures); ecbench is a sibling repo and is named only as the target export backend.

## Independent checker
Python stdlib plus gp, no runner code. It recomputes from recorded (p, a, b, P, Q) that p and N are prime, N = #E (gp ellcard) and [N]P = O, [k]P = Q by bigint; recomputes t, D, v, factorisations and mod-classes; recomputes h(D) by counting reduced forms for |D| < 2^26 (gp qfbclassno above, a declared shared dependency). It replays a nonce-sampled 5% of walks from the recorded seed using its own implementation of the written walk spec and must match the S count exactly. Tamper tests: change one count, one coefficient of a curve, and one planted k; each must be rejected.

## Open risks
(1) IC variance is unknown: a 40-curve pilot sets feasibility, and the IC arm may only reach "inconclusive". (2) Hasse-boundary and 40-bit smooth strata may be short (sieve tuning). (3) Construction route is not fully separable from small |D|; rho-presentation addresses only presentation. (4) The 3-day implementation figure is an estimate. (5) The unexplained toy excess may be walk-specific and invisible to arithmetic; the study cannot explain it, only exclude arithmetic.
