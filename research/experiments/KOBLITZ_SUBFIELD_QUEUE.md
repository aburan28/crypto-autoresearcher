# Koblitz / subfield index-calculus execution queue

This queue exists so promising research threads cannot disappear after ideation. It is the human-visible front door for the campaign in `koblitz_subfield_followthrough.yaml`.

## Coordinator rule

Before generating another nearby Koblitz/subfield IC idea, inspect this queue and advance the highest-priority unblocked item that has not produced a new artifact in 7 days. Every run must attach an artifact (code, dataset, metrics, result, or blocker) and update the thread state.

## North-star metric

Primary: **seconds per newly independent verified relation**. Secondary: projected end-to-end work versus the applicable Frobenius/automorphism-accelerated Pollard-rho baseline. Never infer an attack from a toy-field solver speedup.

## P0 — execute now

- [ ] **IC-KS-01 Orbit-coordinate decomposition.** Encode factor-base points as Frobenius-orbit representative + relative shift; compare against ordinary Semaev and invariant-factor-base baselines. Measure variables, equations, solver time, Macaulay rows/NNZ, verified relations/sec.
- [ ] **IC-KS-02 Frobenius-aware Gröbner/Macaulay.** Test symmetry-adapted variable/monomial ordering and orbit-block structure. Record solving/last-fall degree, peak matrix dimensions, NNZ, rank trajectory and wall time.
- [ ] **IC-KS-03 Frobenius-factor telemetry.** Instrument raw points, orbit representatives, effective relation columns, solver work, relation work, linear-algebra dimension and end-to-end work. Report measured factors rather than assumed `n`/`n^2` gains.
- [ ] **IC-KS-11 Decomposition-likelihood model.** Build a frozen corpus of decomposable/non-decomposable targets; features include trace, orbit length, subspace projections, tau-adic weight and invariant evaluations. Track Brier score, log loss, calibration, solver-call avoidance and false negatives. Ranking is allowed immediately; hard rejection requires zero missed decompositions on held-out validation.
- [ ] **IC-KS-12 Algebraic telemetry.** Persist Hilbert/degree profile, solving degree, Macaulay rank/NNZ, syzygy summaries, support size, orbit stabilizers and solver trajectory for every decomposition-system experiment.

## P1 — run after shared telemetry is present

- [ ] **IC-KS-04 Factor-base search.** Optimize Frobenius-stable subspaces for verified-relation yield divided by solver and linear-algebra cost, not factor-base cardinality alone.
- [ ] **IC-KS-05 Trace-zero × Frobenius bases.** Intersect trace-zero constraints with Frobenius-stable low-dimensional coordinate conditions; compare relation probability and solver complexity to matched controls.
- [ ] **IC-KS-06 Hybrid SAT → Gröbner.** Let SAT handle orbit indices, membership and symmetry breaking; pass the nonlinear residue to F4/F5. Compare total verified-relation cost to pure SAT and pure Gröbner.
- [ ] **IC-KS-07 One/two-large-orbit relations.** Permit one or two out-of-base orbit representatives, canonicalize under Frobenius, recombine through a relation graph, and measure graph yield versus added linear algebra.
- [ ] **IC-KS-08 Tau-adic generation.** Compare uniform target generation against matched sparse tau-NAF strata. Measure generation cost and decomposition probability separately to detect mere arithmetic speedups or sampling bias.

## P2 — broader generalization

- [ ] **IC-KS-09 Generic endomorphism quotienting.** Generalize orbit canonicalization from Frobenius to efficiently computable endomorphism groups (including GLS-style cases) and measure effective factor-base and solver reductions.
- [ ] **IC-KS-10 Partial Weil descent.** For `n = ab`, benchmark descent only to `F_(q^a)` across divisors `a`; jointly record descended genus/system dimension, relation probability, solver cost and projected e2e exponent.

## Required experiment ladder

For every item: `specified -> implemented -> tiny_verified -> benchmarked -> held_out -> e2e -> reviewed -> promoted|retired`.

Promotion requires correctness on the original curve, replicated benefit across seeds/instances, held-out confirmation, and an end-to-end accounting that includes relation collection and linear algebra. Retirement requires a recorded negative result or scaling barrier, not silent abandonment.

## Scale ladder

Tiny instances exist only for correctness. After that, move through progressively larger binary extension degrees and include Koblitz-relevant prime degrees (for example 37, 53, 83) where the formulation permits. Do not extrapolate a cryptographic-scale claim from tiny fields.

## Literature anchors / motivation

The historical baseline matters: subfield-defined curves admit Frobenius conjugacy-class speedups for generic rho, so all comparisons must include that advantage. The older ECC literature also records successful Weil-descent/index-calculus attacks for some composite extension degrees while noting that those methods did not apply to the prime-degree binary fields commonly selected for deployed ECC. The purpose of this queue is to test whether newer orbit-aware decomposition methods change that boundary, not to assume that they do.
