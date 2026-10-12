# EXP-SEMBIN-79a02d — RESULTS (Stages 0–3, TASK-20261002-fc71d6)

## Outcome label

**O-DFF-ANOMALY** (H-SEMBIN-8e8bef). **ESCALATE per SR-7**: this must not be summarized as ordinary separation.

The label was applied mechanically by `implementation/aggregate_census.py`, using the precedence frozen in
`stage0/definitions.md` §5 before any computation (freeze time 2026-10-05T16:48:10Z, `stage0/FREEZE.sha256`).
The frozen trigger is "d_ff_ic < 4 on at least one valid primary-arm instance". It holds on 34 of 34 primary
instances: d_ff_ic = 2 on every planted, uniform-z and DREG-anchor instance at n = 12 and n = 15. No
higher-precedence condition triggered.

| # | condition (frozen precedence) | triggered |
|---|---|---|
| 1 | O-BUILDER-MISMATCH | no (Stage 1 PASS) |
| 2 | O-IMPEDIMENT (Stage 2 incomplete) | no (82/82 records ok) |
| 3 | O-ARTIFACT (dual-rank disagreement / pooling / soundness) | no (0 disagreements in 533 dual cells; no pooling) |
| 4 | O-C2-FALSE | no |
| 5 | O-A1-COST-FAIL | not evaluable (neither frozen cell is a Semaev Table 1/2 row) |
| 6 | **O-DFF-ANOMALY** | **yes: 34/34 primary instances have d_ff_ic = 2** |
| 7 | O-C3-FALSE | no (rank < nrows at every measured D ≥ 4 cell; Stage-0 target = nrows) |
| 8–9 | O-C1-FALSE / O-C1b-FALSE | not evaluable (Stage 3 impeded) |
| 10 | O-COINCIDE | not evaluable (d_F4 unmeasured) |

Without condition 6, the remaining measured conditions would have met the frozen O-SEPARATED clause. That
reading is recorded for the reviewers only; it is not the label.

**Precedence caveat.** The ordering of labels is an executor operationalization, frozen before any data and
flagged in definitions.md §5 for Coordinator ratification. The hypothesis text itself does not order the labels.

## Observations (no interpretation beyond the frozen rule)

Tested scope: only the cells n ∈ {12, 15}, m = t = 3, k = ceil(n/3) (N = 24 and N = 30 Boolean variables),
with B = α, A = 1 and the Conway modulus. The off-diagonal arm uses k' = k + 1. Nothing here transfers to other
n, to the paper's B conventions, or to cryptographic scale. No claim is made of a break, an exponent, or an
Assumption-1 verdict.

### d_ff
- **d_ff_ic** (the spec-named `ic_first_fall_fast` definition) is **2** on every Semaev-derived instance:
  primary, both known-false arms and both anchors.
- **d_ff_sem** (secondary, Semaev §4.4 operational fall) is also 2 on all of those instances.
- The null arm gives **> 4** (censored at max_D = 4) on all 16 null instances.
- This matches the executor derivation written into `stage0/preregistered-predictions.json` before any run: the
  combination Tr(z⁻²·S₃(u,x₃,z)) of the n descended coordinates of S₃(u₁,x₃,z) has no quadratic part, so a
  degree-≤1 polynomial lies in M₂. It is also consistent with KN-FIND-006 ("subset-sum of descended quadrics
  degenerates to an affine form").
- The source idea predicted d_ff = 4. Whether this fall is a convention difference from Semaev's §4.5 statement
  (which concerns S₃ with all three arguments variable) is a question for review, not for this executor.

### SOLV4 (iterated closure W_4, definitions.md §2)
- **True** on every primary instance in both strata:
  - planted: 16/16;
  - uniform-z SAT: 2/2;
  - uniform-z UNSAT: 14/14 (1 ∈ W_4);
  - both anchors.
  The closure reaches a fixed point in 3 productive rounds at n = 12 and 4 at n = 15.
- **known_false_a** (one constant flipped; UNSAT by both enumerations): 1 ∈ W_4 on 16/16 instances. SOLV4 does
  not return the planted count.
- **known_false_b** (off-diagonal k' = k+1): SOLV4 is **true** on 16/16 (codim = |V|; 5 rounds at n = 15). This
  is contrary to the source idea's kf-b prediction "SOLV4 false". It is recorded as an observation and is not
  C2-false under the frozen consistency reading (§3).
- **null**: SOLV4 false on 16/16 (no degree-<4 elements; 0 closure rounds); d_solv > 4.
- C2 consistency holds on every instance:
  - soundness certificate (independent NumPy evaluation of all W_D basis vectors at all enumerated
    solutions) passes on every SAT instance;
  - no 1 ∈ W with |V| > 0;
  - codim ≥ r_V everywhere;
  - E1 and E2 enumerations agree wherever both apply (E2 is skipped for kf-b at n = 15, N = 33, per §4).
- d_solv = 4 on every Semaev-derived instance. The chain d_ff_ic (2) ≤ d_solv (4) holds; d_F4 was not measured.

### Macaulay rank vs nrows (C3)

| cell | D | nrows | rank | nrows − rank | deficit vs pred | dual |
|---|---|---|---|---|---|---|
| n=12 primary/kf-a | 4 | 3912 | 3802 | 110 | 32 (= 8k) | agree |
| n=12 anchor | 5 | 31512 | 28096 | 3416 | 1322 | agree |
| n=12 planted | 5 | 31512 | 28096–28097 | — | 1321–1322 | agree |
| n=12 uniform-z | 5 | 31512 | 28086–28096 | — | 1322–1332 | agree |
| n=12 kf-b (k=5) | 4 / 5 | 4884 / 44196 | 4772 / 40624 | 112 / 3572 | 34 / 1244 | agree |
| n=12 null | 4 / 5 | 3912 / 31512 | 3834 / 29418 | 78 / 2094 | 0 / 0 | agree |
| n=15 primary/kf-a | 4 | — | — | 160 | 40 (= 8k) | agree |
| n=15 kf-b (k=6) | 4 | — | — | 162 | 42 | agree |
| n=15 null | 4 | — | — | 120 | 0 | agree |

- rank < nrows at every measured (n, D ≥ 4) cell in every arm.
- The IDEA band nrows − rank ≥ n_q + C(n_q, 2) holds:
  - n = 12: 110 ≥ 78;
  - n = 15: 160 ≥ 120.
  The null sits exactly on that band.
- External anchor: both arms reproduce EXP-DREG-001's Sage/M4RI values (n = 12, D = 5) on the hash-matched
  instance: nrows 31,512, ncols 46,717, rank 28,096 and pred 29,418.
- Stage-0 target: in EXP-DREG-001 analysis.md:122-126 the "full rank" comparison for d_reg is against nrows. The
  instrument code (h012c:316-319) compares only against pred[D] (the deficit) and emits no degree.
- **Not measured:** D = 5 at n = 15, in every family. This was frozen budget-priority item 4. The d5 phase was never
  launched (session usage limit; the resumed task authorized aggregation only). It is censored and is not
  evidence.

## Per-stage status

| stage | status | artifact |
|---|---|---|
| 0 | completed; frozen 2026-10-05T16:48:10Z before any instance build | stage0/{definitions.md, dreg-comparison-target.md, preregistered-predictions.json, sources-read.md, FREEZE.sha256} |
| 1 | completed, **PASS** | stage1/builder-equality.json |
| 2 | completed (D=5 at n=15 censored) | stage2/census.json (82 instances, 533 dual cells, 0 disagreements) |
| 3 | stopped, **O-IMPEDIMENT** (no per-step-degree open-source F4/XL engine installed or vendored) | stage3/impediment.json |

Stage 1 detail: an independent descent hashes byte-identically to the DREG anchors at n=12 (Conway C(2,12), z=1875)
and n=15 (C(2,15), z=24959). The DREG integer variable index is N−1−i (PolyBoRi order); the variable names and all
coefficients are equal.

## Runs (5 of the 8 allowed)

| RUN | purpose | status | elapsed | peak RSS (children) |
|---|---|---|---|---|
| RUN-SEMBIN-004d51 | Stage 1, first attempt | failed_implementation (identity index map only; aborted) | ≈300 s | not recorded |
| RUN-SEMBIN-bdfd41 | Stage 1 builder equality | completed_valid, PASS | 67.5 s | 224.6 MB |
| RUN-SEMBIN-694183 | Stage 2 census n=12 | completed_valid, 41/41 | 340.0 s | 571.1 MB |
| RUN-SEMBIN-5d7618 | Stage 2 census n=15 | completed_valid, 41/41 | 1099.1 s | 866.1 MB |
| RUN-SEMBIN-6c5c56 | Stage 3 engine inventory | completed_valid → O-IMPEDIMENT | 0.6 s | 50.6 MB |

Total recorded wall time is about 1,510 s, against a 14,400 s budget. Peak RSS stayed below 1 GB against an 8 GB cap.

## Rank libraries per arm
- **Arm A:** `implementation/gf2_armA.c`, row-insertion Gaussian elimination.
- **Arm B:** `implementation/gf2_armB.c`, Four-Russians block elimination.
- **Common to both:** written in this task in C and built with gcc 13.3.0 `-O3 -march=native`. Both are M4RI-free;
  no libm4ri of any version is installed or linked.
- **Shared code:** `gf2_common.h` holds parsing, the monomial index and the polynomial products. The elimination
  code is fully separate. Every Macaulay cell compares matrix fingerprints between the two arms; they matched on
  every cell.

## Deviations and disclosures (including N1–N4)

1. **N1 (blindness):** respected. Nothing from EXP-SEMBIN-35bf67 or EXP-SEMBIN-7e1371 was read or used, before or
   after the freeze. The sources read are listed in stage0/sources-read.md.
2. **N2 (closure definition):**
   - The iterated W_4 closure is recorded as the specification's own definition.
   - Three choices are executor operationalizations, flagged in definitions.md §2–§3 and not self-amended:
     variable-only re-multiplication of degree-<4 elements, generator products with Boolean degree falls at
     level 0, and the C2 consistency reading.
   - Sufficiency uses both quantities: codim = |V| and 1 ∈ W.
3. **N3 (Sage):** not used. `src/` was used only as a reference. The DREG builder was checked through its recorded
   hashes rather than by executing it.
4. **N4 (M4RI):** libm4ri was not used. Both arms are M4RI-free, but they were written by the same executor and
   share the I/O and product code, so their independence is at the elimination-code level only. A third-party
   cross-check exists only at the n=12 D=5 anchor (DREG's Sage/M4RI rank).
5. **Aborted run:** RUN-SEMBIN-004d51 was aborted. A broad `pkill` also killed its wrapper, so its manifest was
   hand-written. The cause (reversed index convention) was found by a side check in the executor shell, outside
   any run directory, and was then reproduced in RUN-SEMBIN-bdfd41.
6. **Freeze-time field:** `preregistered-predictions.json` carries the placeholder `frozen_at_utc` "16:5xZ". The
   authoritative freeze time is the FREEZE.sha256 timestamp 16:48:10Z. The file was not edited after the freeze.
7. **Pre-run tests and probe:**
   - Development tests ran at n = 9, which is not a frozen cell.
   - One n = 15 timing probe used a separate RNG namespace ("PROBE-timing-only"). It ran outside run records, and
     only its timings were looked at.
8. **Stage 3 concurrency:** the Stage-3 inventory (RUN-SEMBIN-6c5c56) ran concurrently with the Stage-2 n=12 census
   (RUN-SEMBIN-694183). It is a read-only environment probe, with no shared inputs or outputs.
9. **Enumeration details:**
   - known_false_a was accepted on E1 = 0 at construction; E2 confirmed it afterwards on all 16 instances.
   - kf-b at n = 15 (N = 33) has E1 only.
10. **Degenerate planted draws:** 4 of 8 planted draws at n=12 (seeds 0–3) give z ∈ V. These are decompositions with
    P_i = −P_j, which the frozen rule allows, and they give |V| = 19. The same draws carry into kf-a seeds 0–3.
    This is an unexpected observation, kept as-is.
11. **n=15 log file:** RUN-SEMBIN-5d7618's stdout.log was committed at 0 bytes mid-run, by the Coordinator's interim
    commit. The complete stdout is in stdout.final.log. Run files were not modified.
12. **Censored cells:** D=5 at n=15 was not executed (see above). This is censored and is not evidence.
13. **Curve coefficient:** B = α (the DREG convention), not the paper's B = 1 or a random B.
