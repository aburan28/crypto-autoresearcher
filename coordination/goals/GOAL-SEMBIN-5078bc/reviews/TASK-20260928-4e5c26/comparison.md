# Comparison: blind re-derivation vs RUN-SEMBIN-c68773 (TASK-20260928-4e5c26)

## Provenance and order of events

1. I wrote and ran the blind derivation (`blind_derivation.md`, `blind_rederive.py`,
   `blind_rederived.json`, `blind_rederived_primary_cells.csv`, `blind_rederive_mext.txt`)
   and hashed it in `pre_reveal_hashes.txt` (recorded 2026-09-30T21:12:48Z, HEAD
   `980abd8f`). **Only after that** did I open
   `experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773/raw-result.json`
   (sha256 `9569c9c0…8e5126`, clean in the tree, last touched by commit `3c97c0d4`;
   I read only that commit's hash and date, not its message).
2. After the reveal I read **only** `raw-result.json`. I still have not opened the
   experiment's `code/`, `RESULTS.md`, the specification, DEC-20260928-7c3d91,
   TASK-20260928-e4f7b2, H-SEMBIN-8e7ae3, any PR text or commit message for this
   experiment, or the sibling review directories `reviews/TASK-20260928-a1c7e5/` and
   `reviews/TASK-20260928-d8b371/` (which I saw as names only).
3. Post-reveal analysis is kept separate from the blind files and does not change
   them:
   - `reconcile_after_reveal.py` and `reconcile_after_reveal.stdout.txt`
   - `convention_factorial_after_reveal.txt`

## Bottom line

**The numbers agree once three named conventions are aligned, and they reproduce
exactly.** I re-ran my blind formulas under the conventions `raw-result.json` exposes:

- C1: K = |F| (mine: |F|/2).
- C2: linear algebra |F|^2 (mine: m*K^2).
- C3: real d on a 0.05 grid (0.25 for the store-free rows) over [1, n] (mine: integer
  d in [1, n-1]).

Under those, my formulas reproduce all of the following with **0 mismatches**:
- all **150/150** `min_store_for_subrho` rows (store, d, total to 1e-4);
- all **15/15** `n = 131` `mitm_store_free` rows;
- all **10/10** `min_store_by_degree` summaries;
- the C-M3-ANCHOR value (131.585 flat).

So neither implementation has an arithmetic error. Every disagreement is a modelling
convention, and each one is attributed below.

The structural model agrees term for term:
- RC = K * m! * N / |F|^s (the |F|^m cancels);
- uncapped trials per relation;
- store = |F|^s, with its construction not charged;
- s from 0 to floor(m/2);
- B = log2(0.886) + N_bits/2, with N = r at n = 131;
- published ECC2K-130 rho = 60.809.

**Largest disagreement:**
- Minimum store: **3.0 bits at n = 239** (blind 180 vs producer 177.0), then 2.6 bits
  at n = 97 (88 vs 85.4). Both come from C3 (integer d).
- Total at the reported cell: 3.40 bits at n = 239. The two sides report different
  cells: my (m=10, d=36, s=5) against the producer's (m=10, d=35.4, s=5).
- The m = 3 total differs by exactly **1.000 bit** everywhere (C1).

## Agreements

| # | Item | Blind | Producer | Status |
|---|---|---|---|---|
| A1 | Baseline B per n | 48.3254, 54.3254, 64.3254, 81.3254, 95.3254, 116.3254, 119.3254, 141.3254, 204.3254, 285.3254 | same `target` / `log2_rho_vow` | exact |
| A2 | 60.8090 = rho with negation and Frobenius on r | log2(sqrt(pi r/4)/sqrt 131) = 60.80904 | `log2_rho_published` 60.809 | exact |
| A3 | No m <= 7 reaches B at any n | proven (s <= 3 infeasible) and computed | every m <= 7 row `reachable: false` | exact |
| A4 | Minimising m at n = 97, 109, 131, 163, 409 | 8, 8, 8, 8, 12 | 8, 8, 8, 8, 12 | exact |
| A5 | Minimising m at all 10 n with real d | 8, 8, 8, 8, 10, 10, 10, 10, 12, 14 (blind continuous relaxation, saved pre-reveal) | 8, 8, 8, 8, 10, 10, 10, 10, 12, 14 | exact |
| A6 | Store needed exceeds rho's total work, every n | excess 37.67 to 90.67 bits (integer d); 35.69 to 89.20 (real d) | 37.07 to 90.57 bits | agree; differences explained in D1 and D3 |
| A7 | n = 131 minimum store | 108 at (m=8, d=27, s=4); 105.30 with real d | 106.8 at (m=8, d=26.7, s=4) | agree within 1.2 bits (D1, D3) |
| A8 | n = 131, store unconstrained: smallest m strictly below 60.8090 | **8** (59.2064 at d=29, s=4) | **8** (`mitm_store_free_first_m_below_published_rho_at_131`, 58.6917 at d=29, s=4) | agree on m (margin differs, D2) |
| A9 | n = 131 unconstrained totals are not below 60.809 for m = 2..7 | 129.0, 130.585, 89.32, 91.13, 70.11, 71.58 | 130.0, 131.585, 89.98, 91.52, 70.27, 71.66 | agree in sign; values differ by the C1 and C2 offsets |
| A10 | m = 3 total is flat in d until LA takes over | 3(N + 4^(d-1)), flat to d ≈ 60 | ENUM and MITM flat over d in [10, 60], spread 0.0004 bits | agree on shape; level differs by 1 bit (D1) |
| A11 | Enumeration with s <= 1 never beats rho | RC >= m! N / 2 | `enum_beats_rho_anywhere: false`; P1 totals = m! N | agree; level differs by 1 bit (D1) |
| A12 | No sub-rho cell with store <= 2^80 (P5) | every primary minimum store is >= 84.0 bits | `P5` empty | agree **under the stated m! accounting**; see S1 |
| A13 | Every sub-rho cell needs a free store larger than the rho work | identity I1: RC * store = K m! N | `store_exceeds_baseline_work_by_bits` > 0 everywhere | agree |

## Disagreements

Each disagreement names its cause, which side I believe is right, and why.

### D1. Relation count K: blind K = |F|/2, producer K = |F| (convention C1)

**Effect.**
- RC is 1 bit higher for the producer.
- The m = 3 total: blind 130.585 vs producer 131.585 (exactly 1.000 bit).
- Minimum stores are about 1.3 to 1.4 bits higher for the producer at matched d-domain
  (at n = 131 on the 0.05 grid: 105.4 vs 106.8).
- The n = 131 unconstrained m = 8 total: 58.29 vs 58.69 (at matched LA).

**I believe the blind convention is right.** Both sides use
lambda = |F|^m/(m! N). That formula is correct when F is a negation-closed set of
points: the sign choices are already inside F. For such an F the unknowns are one per
±-pair (log(-P) = -log P), so K = |F|/2. Using the same lambda with K = |F| mixes two
conventions. The other consistent option counts ±-classes and has lambda carry 2^m,
with the oracle enumerating signed elements; that is the same model with F relabelled.

**This makes the producer's numbers about 1 to 1.4 bits IC-pessimistic.** That is the
conservative direction for its negative conclusion, so it changes no sign.

**Caveat on the evidence.** The raw result's C-M3-ANCHOR reports a
`measured_implicit_base` of 132.58. That is 1 bit above the producer and 2 bits above
my primary. It equals log2(3 * 4r) = 132.585, which is **my convention (K = |F|/2)
with lambda over #E = 4r**, i.e. my V5 at n = 131. I have not read the definition of
that measurement, so I record this as suggestive, not decisive. If it is
like-for-like, both sides should use #E rather than r in lambda at n = 131 (S3).

### D2. Linear-algebra cost: blind m*K^2, producer |F|^2 (convention C2)

The producer's inherited assumption reads "Sparse linear algebra at |F|^2 time".

**Effect.**
- Minimum stores: none except n = 97. The minimum-store cells are RC-bound, so LA
  moves the n = 97 store by only 0.4 bits (85.8 vs 85.4 at K = |F| on the grid).
- The **n = 131 unconstrained question**, where LA and RC balance:
  - Producer's margin under 60.809 at m = 8: 2.12 bits (58.69).
  - With the producer's own K = |F| and the row weight restored (m*|F|^2), the margin
    falls to 0.29 bits (grid d) or **0.018 bits** (integer d, 60.7912).
  - With a Wiedemann constant of 3 as well (V7), m = 8 **fails** (61.45) and the
    smallest m becomes **10**.

**I believe the blind convention is right.** A Lanczos or Wiedemann matrix-vector
product costs (row weight) x (dimension), which is m*K. About K to 3K of them are
needed. Dropping the weight m is IC-optimistic by log2(m) bits at fixed K. The answer
"m = 8" is correct under the producer's model and under my primary, but it is not
robust. It survives only through the omitted row weight (with K = |F|) or through the
negation halving (with the weight kept). Any claim resting on "m = 8 is the smallest m
below 60.809" should carry that sensitivity.

### D3. Domain of d: blind integer d in [1, n-1], producer real d on a grid (convention C3)

**Effect.** This is the whole of the minimising-m disagreement:

| n | blind (integer d) | producer | blind continuous (saved pre-reveal) |
|---|---|---|---|
| 191 | m = 8 | m = 10 | m = 10 |
| 233 | m = 12 | m = 10 | m = 10 |
| 239 | tie {8, 10, 11, 12} | m = 10 | m = 10 |
| 283 | m = 12 | m = 10 | m = 10 |
| 571 | m = 16 | m = 14 | m = 14 |

It is also the largest store gaps: 3.0 bits at n = 239 and 2.6 at n = 97. The
factorial in `convention_factorial_after_reveal.txt` confirms it: with a real d, every
K/LA combination gives the producer's argmin m at all 10 n.

**I believe the producer is right for the quantity as posed.** The statement specifies
an abstract MITM oracle over "a factor base F of size 2^d". A meet-in-the-middle
m-sum search needs no subspace structure, so |F| can be any size and a real d is
legitimate. My integer d is the stricter Semaev-style reading, where F = {P : x(P) in V}
and V is a subspace. That reading is *also* defensible, and under it the minimising m
is fragile: n = 239 is a four-way tie. **The minimising m is a rounding-sensitive
quantity and should not be treated as load-bearing.** The minimum store is stable to
within about 4.4 bits across the two readings.

### D4. Numeric table (blind primary, integer d, as saved) vs producer

| n | blind m* | producer m* | blind store | producer store | Δstore (blind − producer) | blind total | producer total | blind excess | producer excess | cause |
|---|---|---|---|---|---|---|---|---|---|---|
| 97 | 8 | 8 | 88 | 85.40 | +2.60 | 46.1573 | 48.2797 | 39.6746 | 37.0746 | D3 (+), D1 (−), D2 (+) |
| 109 | 8 | 8 | 92 | 93.40 | −1.40 | 54.3083 | 54.2569 | 37.6746 | 39.0746 | D1 |
| 131 | 8 | 8 | 108 | 106.80 | +1.20 | 62.3083 | 64.2000 | 43.6746 | 42.4746 | D3 (+), D1 (−) |
| 163 | 8 | 8 | 128 | 129.40 | −1.40 | 81.2992 | 81.2492 | 46.6746 | 48.0746 | D1 |
| 191 | 8 | 10 | 148 | 147.00 | +1.00 | 94.2992 | 95.1911 | 52.6746 | 51.6746 | D3 |
| 233 | 12 | 10 | 174 | 173.25 | +0.75 | 115.8355 | 116.1911 | 57.6746 | 56.9246 | D3 |
| 239 | 8/10/11/12 | 10 | 180 | 177.00 | **+3.00** | 115.7911 | 119.1911 | 60.6746 | 57.6746 | D3 |
| 283 | 12 | 10 | 204 | 204.50 | −0.50 | 140.8355 | 141.1911 | 62.6746 | 63.1746 | D3, D1 |
| 409 | 12 | 12 | 282 | 280.50 | +1.50 | 201.8355 | 204.0855 | 77.6746 | 76.1746 | D3 |
| 571 | 16 | 14 | 376 | 375.90 | +0.10 | 285.2501 | 285.1432 | 90.6746 | 90.5746 | D3 |

The blind *continuous* relaxation, saved pre-reveal, sits uniformly 1.38 to 1.50 bits
**below** the producer at every n: 84.01, 91.98, 105.30, 127.97, 145.58, 171.83,
175.58, 203.08, 279.01, 374.52. That is D1 plus the producer rounding up to its 0.05
grid.

"Total at the cell" is the least informative column. Both sides report the cell with
the smallest feasible d, so the total sits just under B by construction; the gaps come
from integer versus grid rounding of d.

## Issues shared by both (agreement here does not certify them)

A blind re-derivation cannot catch a modelling choice both sides made. Both followed
the prompt's term list. The blind derivation still flagged these independently,
before the reveal.

- **S1. m! overcharge; the model mixes two regimes.**
  - Every sub-rho cell needs 2^-37.7 to 2^-227.5 of a single full oracle call
    (lambda >> 1). So it is only reachable by *truncating* the MITM enumeration. The
    producer's HEUR-GENERIC-MSUM says as much ("partial meet-in-the-middle").
  - In a truncated pass, a probe hits a distinct s-sum key with probability
    |F|^s/(s! N), and duplicates are negligible. The cost per relation is therefore
    s! N/|F|^s, not m! N/|F|^s. Both sides overcharge by m!/s! (10.7 bits at m = 8).
  - Correcting this (blind V4) lowers every minimum store by 15 to 32 bits
    (n = 131: 90 instead of 108 / 106.8).
  - It **flips P5 at n = 97 and 109**: V4 finds sub-rho cells with stores 2^70
    (n = 97; m=10, d=14, s=5; total 46.91 < 48.33) and 2^77 (n = 109; m=14, d=11, s=7;
    total 54.2992 < 54.3254).
  - The qualitative conclusion survives: the store still exceeds the rho work by 21.7
    to 58.7 bits.
  - Under the opposite, consistent reading (atomic oracle calls, strict probability;
    blind V2), **no cell beats rho at any n** and the minimum store is undefined.
  - The reported numbers therefore belong to a hybrid of the two regimes, and are an
    upper bound on the truncated-oracle cost.
- **S2. Store construction is never charged.**
  - Identity I1: RC * store = K m! N >= N. So with the build charged, **no cell at any
    n, m, d, s is sub-rho** (blind V3).
  - The producer's C-NULL-NO-MEMORY-CHARGE uses a store *cap* as its "memory charge".
    Its 14 surviving "charged" cells (n = 97 and 109, budgets 2^90 and 2^100) all have
    stores of 90 to 100 bits against totals of 40 to 54 bits, so each survives only
    because the store is free.
  - Under a build-time charge the correct count is 0, not 14. The control's
    conclusion ("the charge discriminates") holds, and more strongly than it states.
- **S3. Group order at n = 131.**
  - Both use r in lambda, as directed. The factor-base points live in E(F_{2^131}) of
    order 4r, so lambda should arguably use 4r: +2 bits on RC.
  - With that change (blind V5) the n = 131 answers hold. The minimum store stays 108
    and m = 8 is still the smallest below 60.809 (59.69). But at integer d the
    minimum-store cell clears B by only 0.024 bits.
  - The measured anchor (D1) matches this reading.
- **S4. Units.** Both sides count a probe into a 2^85 to 2^376-entry table, and a
  mod-r multiply-add, as one group operation. This is optimistic for index calculus
  and is not flagged in the raw result's row fields.
- **S5. Frobenius.** 60.8090 gives rho the Frobenius speedup (sqrt 131, 3.52 bits)
  that neither IC model exploits. That is correct as a comparison against the
  published figure, but it is not like-for-like.

## Review attestation

```yaml
review_attestation:
  task_id: TASK-20260928-4e5c26
  role: validator (blind re-derivation)
  joints_owned: [blind re-derivation of the minimum-store / sub-rho cost quantity for EXP-SEMBIN-04ec3c]
  blind_from_respected: true
  sources_read_before_derivation_saved:
    - AGENTS.md
    - agents/validator.md
    - CLAUDE.md (injected)
    - dispatch prompt
    - directory listings only: coordination/goals/GOAL-SEMBIN-5078bc/**, experiments/EXP-SEMBIN-04ec3c/ (names only)
  sources_read_after_derivation_saved:
    - experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773/raw-result.json
    - git log -1 --format='%H %cI' for that file (hash and date only, no message)
  not_read: [experiments/EXP-SEMBIN-04ec3c/code/, RESULTS.md, specification.yaml (entire file),
             ledger/decisions/DEC-20260928-7c3d91.yaml, ledger/handoffs/TASK-20260928-e4f7b2.yaml,
             ledger/hypotheses/H-SEMBIN-8e7ae3.yaml, PR descriptions, commit messages,
             coordination/goals/GOAL-SEMBIN-5078bc/batches/** (earlier reviews and rederivations),
             knowledge corpus / KB]
  read_sibling_reports: false
  sibling_dirs_observed_by_name_only: [reviews/TASK-20260928-a1c7e5, reviews/TASK-20260928-d8b371]
  accidental_exposure: none (no producer number seen before pre_reveal_hashes.txt was written)
  joint_verdict: holds
  joint_verdict_scope: >-
    Arithmetic is reproduced exactly under the producer's conventions (150/150, 15/15, 10/10).
    The disagreements are conventions D1 (K) and D2 (LA weight), where I judge the blind
    convention more defensible, and D3 (real d), where I judge the producer's more
    defensible. Two fragilities: the minimising m is rounding-sensitive (D3), and
    "smallest m below 60.809 = 8" depends on the omitted LA row weight (D2). Shared caveats
    S1-S3 bound what the quantity can claim; S1 flips P5 at n = 97 and 109.
```
