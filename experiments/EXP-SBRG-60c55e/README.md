# EXP-SBRG-60c55e — Syzygy-aware batched Semaev relation generation

This experiment turns the SMS/PQC slide-review lead into a falsifiable ECDLP relation-generation program.  Phase A asks a deliberately narrower question than "does Semaev beat Pollard rho?": **is there reusable algebraic structure in the fixed part of a descended point-decomposition system that survives matched controls and representation changes?**

The experiment is currently **draft / implementation-only**.  The pure-Python matrix instrumentation has unit tests; no mathematical run result is claimed until the Sage driver is executed under the frozen/approved experiment contract and its artifacts are independently reviewed.

## Core split

For a target point `R`, write the descended ideal as

```text
I_R = <S_struct, P_R>
```

`S_struct` contains the S_3 constraints that depend only on the curve, factor base, field basis, and addition-tree topology. `P_R` is the final block containing `x(R)`.  For a chain with `t=4`, for example,

```text
S_3(u1, x1, x2)       = 0     fixed
S_3(u1, u2, x3)       = 0     fixed
S_3(u2, x4, x(R))     = 0     target-specific
```

The balanced `t=4` form instead uses

```text
S_3(u1, x1, x2)       = 0     fixed
S_3(u2, x3, x4)       = 0     fixed
S_3(u1, u2, x(R))     = 0     target-specific
```

For `t=3`, a direct `S_4` resultant is included as a degree/variable-count control against the chained two-`S_3` representation.

## What `fall_dim` actually measures

All descended equations live in the Boolean quotient

```text
B = F_2[z_1,...,z_N] / (z_i^2 - z_i).
```

At Macaulay degree `D`, for every generator `f_i` of degree `d_i`, the driver includes all Boolean-reduced products `m*f_i` with square-free `deg(m)=D-d_i`.

Let:

- `H_D` be the row matrix projected onto monomials of degree exactly `D`;
- `M_D` be the same rows with all monomials of degree at most `D`.

Then the instrumentation records

```text
fall_dim(D)    = rank(M_D) - rank(H_D)
syzygy_dim(D) = rows(M_D) - rank(M_D)
```

`fall_dim` therefore counts independent row combinations whose degree-`D` part cancels but which leave a nonzero lower-degree relation. `syzygy_dim` counts exact zero dependencies among the same rows. This deliberately avoids the unsupported inference `first fall degree ~= degree of regularity`.

## Matched null

For each real descended Boolean equation the control generator preserves the **number of monomials at every degree**. A Boolean root is planted by swapping one selected monomial for an unselected monomial of the same degree and opposite evaluation whenever possible. If that is impossible, the constant term is toggled and the result is explicitly marked `degree_histogram_exact=false`.

The control answers: *is the observed rank defect more than what Boolean reduction, variable count, and the equation-degree profile already create?*

## Batch-reuse metric

For a batch of target points the driver computes the fixed Macaulay basis once, then reduces every target block against cloned fixed pivots. It reports both

```text
baseline_total_xors = rebuild <S_struct,P_R> from scratch for every R
batched_total_xors  = build S_struct once + incremental target reductions
xor_speedup         = baseline_total_xors / batched_total_xors
```

This is a deterministic operation-count proxy for reuse, not a wall-clock solver claim. Phase B must replace it with actual F4/F5-equivalent solver measurements.

## Phase-A commands

Smoke-test a chained `t=4` cell:

```bash
sage experiments/EXP-SBRG-60c55e/driver/run.sage \
  --n 10 --t 4 --representation chain \
  --basis power --orientation prefix \
  --targets 4 --max-degree 5 \
  --seed 20260824 \
  --output experiments/EXP-SBRG-60c55e/runs/smoke-chain-n10.json
```

Compare the balanced tree:

```bash
sage experiments/EXP-SBRG-60c55e/driver/run.sage \
  --n 10 --t 4 --representation balanced \
  --basis power --orientation prefix \
  --targets 4 --max-degree 5 \
  --seed 20260824 \
  --output experiments/EXP-SBRG-60c55e/runs/smoke-balanced-n10.json
```

Compare direct `S_4` to the `t=3` chain; direct form needs a higher degree ceiling because it trades auxiliary variables for polynomial degree:

```bash
sage experiments/EXP-SBRG-60c55e/driver/run.sage \
  --n 10 --t 3 --representation direct \
  --basis power --orientation prefix \
  --targets 4 --min-degree 4 --max-degree 9 \
  --max-columns 300000 --seed 20260824 \
  --output experiments/EXP-SBRG-60c55e/runs/smoke-direct-n10.json
```

Representation/basis sweeps should use the exact matrix in `specification.yaml`; do not choose a winning degree or basis post hoc.

## Local instrumentation tests

The matrix code is Sage-independent:

```bash
pytest -q experiments/EXP-SBRG-60c55e/tests/test_macaulay.py
```

The tests cover Boolean product cancellation, GF(2) rank, degree-fall detection, exact syzygies, planted matched controls, deterministic seeding, and equality of batched versus from-scratch row-space ranks.

## Promotion gates

Phase A does **not** promote on one unusually easy instance. The preregistered gate requires a persistent real-vs-control signal across increasing `n`, multiple seeds, and representation changes, plus measurable fixed-rowspace amortization. Only then does Phase B measure an actual solver. Only after Phase B does Phase C charge decomposition probability, relation-matrix cost, preprocessing, individual descent, and matched rho/BSGS baselines.

A negative result is still useful: if the extra rank defects track the random controls or vanish under basis/tree changes, that is evidence that the apparent low-degree structure is a representation artifact rather than a route to cheaper relation generation.

## Literature anchors

All references below were retrieved during the 2026-08-24 design pass, rather than cited from model recall:

- **Semaev (2015), _New algorithm for the discrete logarithm problem on elliptic curves_, arXiv:1504.01175.** Chained `S_3` systems over binary fields and the regularity/first-fall heuristic context.
- **Kosters–Yeo (2015), _Notes on summation polynomials_, arXiv:1503.08001.** Shows characteristic-2 first-fall behavior can be unexpectedly low and explicitly warns against over-interpreting first-fall heuristics.
- **Kousidis–Wiemers (2019), _On the first fall degree of summation polynomials_, J. Math. Cryptol. 13(3–4).** Improved first-fall bounds for Weil-descended summation-polynomial systems.
- **Hodges–Petit–Schlather (2014), _First fall degree and Weil descent_, Finite Fields and Their Applications 30.** General Weil-descent first-fall framework and experimental complexity context.

The novelty claim here is intentionally narrower: **explicit fixed/target quotient instrumentation plus exact low-degree fall/syzygy rank accounting and batched row-space reuse as a staged gate**, not the discovery of Semaev systems, first-fall degree, or Weil descent.
