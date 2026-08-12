# EXP-ENDO-001 implementation note (Executor, TASK-20260727-002)

Frozen protocol: `experiments/EXP-ENDO-001/specification.yaml` v1 (approved,
frozen). This note describes the implementation and discloses every design
decision taken inside the protocol's explicit latitude. No protocol element
was changed; no amendment was requested.

## Code

- `code/endo_common.py` — shared implementation (instances, factor bases,
  enumeration engine, displacement/rank, Wiedemann, baselines, run-record
  writer).
- `code/run_ENDO.py` — one CLI entry per planned run:
  `python3 experiments/EXP-ENDO-001/code/run_ENDO.py --run-id RUN-ENDO-00X`
  (recorded verbatim in each `command.txt`).

Reused read-only code (disclosed per handoff): `harness/toycurve.py`
(curve arithmetic, `generate_instance`, `_seed_int`), `harness/rho.py`
(rho baseline), and the Berlekamp–Massey/Wiedemann and x-translation
displacement approach of `experiments/EXP-STR-001/str1_ap_matrix.sage`
(re-implemented in pure Python with field-op counters; no Sage available).
`harness/endomorphism_la.py` (EXP-STR-002) was read for the GLV filters
(zeta3 search, phi maps) and its limitations (incomplete orbits, noisy
penalty) were repaired as the protocol requires. Nothing outside
`experiments/EXP-ENDO-001/` was modified.

## Design decisions inside the protocol's latitude

1. **Seed→size mapping.** "seeds {1,2,3} mapped one-to-one to sizes within
   each family": seed 1 → 16 bits, seed 2 → 20 bits, seed 3 → 24 bits
   (same pinning as EXP-MTIC-001 amendment AMEND-EXP-MTIC-001-001).
2. **Instance generation.** p from `generate_instance`'s exact seed formula
   (tag `"p"`), advanced by `nextprime` to the GLV congruence (p≡1 mod 3 for
   j=0; p≡1 mod 4 for j=1728). j=0: seeded `b` stream; j=1728: seeded `a`
   stream; subgroup = largest prime factor of #E with `n.bit_length() >=
   bits-2` (MTIC amendment precedent); generic arm:
   `generate_instance(seed, bits, min_prime_order_bits=bits-2)` with
   j-invariant ∉ {0,1728}. All derivations recorded per cell in
   `frozen-instances.yaml`.
3. **Factor bases are complete-orbit unions by construction** ("Union of
   complete phi-orbits"): FB_size = 3·⌈B/3⌉ (j=0) or 2·⌈B/2⌉ (j=1728,
   generic). For j=0/p≡1 mod 3 and j=1728/p≡1 mod 4, orbit x-coordinates are
   automatically on-curve (proved identities recorded in run records), so the
   audited orbit-completeness fraction is expected to be exactly 1.0; the
   audit is performed and recorded regardless (RUN-ENDO-002). EV-STR-002's
   instance-dependent incompleteness came from truncating a partial orbit;
   this construction never truncates.
4. **Column conventions (bookkeeping, pre-registered).** GLV arms: columns
   are x-coordinates; the phi-shift acts on x as x→ζ₃x (j=0, r=3) and x→−x
   (j=1728, r=2 — φ² is negation, trivial on x; this is the spec's "orbits
   merged with negation, effective r=2"). Generic arm: negation is trivial on
   x-coordinates, so its columns are **signed points** {(x,y),(x,−y)} (r=2);
   this is the only convention under which the negation-orbit arm is
   non-vacuous, and it is disclosed here and in the run records.
5. **Relation collection ("enumeration-assisted … as in EXP-MTIC-001").**
   Pair-sum x-table over the factor base (x(G_i+G_j), x(G_i−G_j) for all
   i<j, vectorized Fermat inversion in numpy int64, exact mod p) plus
   per-target probes x(R−G). A table hit yields an exact signed relation
   R = G + σ(G_i ± G_j) resolved and re-verified with `harness/toycurve`
   addition (independent code path). A **harvesting pool of 2000 targets per
   cell** with known seeded (a,b) is used for relation collection (the MTIC
   protocol); the **200 decomposition-test targets** are a disjoint seeded
   stream used only for hit-rate/penalty measurement, shared identically
   across all arms of a cell (control comparability).
6. **Evaluation accounting.** One "tuple evaluation" is charged per pair-sum
   x computation and per probe x computation; counts are recorded per cell
   against the 5e7 cap (all cells finish far below it; e.g. ~1.76e7 at the
   24-bit cells). Per-cell 1500 s cumulative cap and censor flags per the
   frozen stop rule.
7. **Hit rate.** Fraction of the 200 decomposition-test targets with at
   least one valid (sign-resolved, non-degenerate, independently verified)
   decomposition within the cell's enumeration budget; Wilson 95% intervals
   per cell. Penalty = (random hit rate)/(structured hit rate) per cell,
   exactly as the frozen metric definition.
8. **Square matrices.** R = B = FB_size per arm ("square matrix of verified
   relations" stop rule); structured-arm rows are orbit-closed
   (rel, φrel, φ²rel / (rel, φrel) / (rel, −rel)) in block order; random-arm
   rows are the first FB_size distinct harvested relations in collection
   order. Every matrix row's underlying relation is certificate-verified
   (decomposition recompute) before the matrix is used.
9. **Displacement operators.** phi arms: block-cyclic Z_phi on orbit blocks
   (the frozen (Z_phi, Z_phi^T) pair; alpha = rank(M − Z_phi·M·Z_phi^T) over
   F_n). Random baseline: the *same* block-cyclic operator on consecutive
   r-blocks (a random matrix w.r.t. any fixed shift sits at the generic
   maximum ~min(R,B), per EV-STR-001). Ablation: seeded random permutation
   (non-phi) on the phi-invariant matrices. AP benchmark: EV-STR-001's
   x-translation displacement (Z_r M − M Z_c with matched shifts) plus the
   classic (Z,Z^T) rank, on the AP-support matrix at 20-bit cells.
10. **Rank computation.** Exact dense Gaussian elimination over F_n in numpy
    int64 (n prime, all intermediates < n² < 2⁵⁰; no floating point, no
    probabilistic rank). Commutation residual ||M·Φ − Φ·M||₀ counted exactly
    with the orbit/sign bookkeeping recorded.
11. **Wiedemann calibration.** Pure-Python Berlekamp–Massey Wiedemann
    (adapted from EXP-STR-001, no Sage dependency) on the largest-B
    structured matrix per family (24-bit cells), ≤5 randomizations; solution
    verified by an in-solve matvec against b and by an independent numpy
    matvec recomputation; field-op counts instrumented (matvec / dot / BM /
    combine). Model = 2·B²·m field ops (m=3, the matvec-work model per
    EV-STR-001). Calibration reported for matvec ops (the model's scope) and
    total ops (honesty: dots+BM+combine add ~1.1x more). A solve that fails
    to converge in its cap is recorded with entry status
    `resource_exhaustion` and its model ratio reported uncalibrated and
    flagged (frozen stop rule; disclosed interpretation: entry-level status,
    the run completes the remaining solves).

11a. **Rank observation driving the solve construction (measured pre-run).**
    Weight-3 0/1 relation matrices are generically ~4-6% rank deficient at
    these sizes: uniform random weight-3 0/1 B×B matrices show the same
    deficiency (~6% at R=B, ~0.4% at R=2B, closing near R≈3B). Plain
    Wiedemann on the raw square matrix hits a sequence minpoly with an X
    factor (M|im defective) and cannot converge. The calibration solves
    therefore run on **greedy full-rank B×B subsystems of freshly harvested
    phi-invariant relations** (the EV-STR-001 precedent: "greedy full-rank
    square subsystem from AP rows over F_n"); collection harvests ≥3.2·B
    fresh base relations per cell so the subsystem exists. Raw square-matrix
    ranks are recorded in RUN-ENDO-009 as an observation.
12. **Cost accounting (fully charged).** Group-operation equivalents:
    1 tuple evaluation = 1 EC add (conservative over-estimate — actual work
    was x-only); 1 EC add = 19 F_p muls (EV-STR-001 charging, 4+15); 1 F_n
    op = 1 F_p mul (n≈p at toy scale). S_rel = measured evaluations;
    penalty-adjusted S_rel = S_rel × measured penalty (structured arms),
    ×1.0 random; S_LA = 2B²m × median measured/model calibration ÷ 19;
    T_desc = B probes per target; T_verify = 3 + 1.5·log2(n) EC adds. All
    components reported separately next to the totals.
13. **Rho/BSGS baselines.** `harness/rho.py` per-target solves on the same
    200 targets per curve (verified by recompute AND by the frozen-secret
    cross-check k_R = a + b·k mod n); BSGS with group-op counting.
14. **Artifact naming (deviation, recorded in every manifest).** The frozen
    `required_artifacts` name `raw.json`, `summary.json`, `stdout.txt`,
    `stderr.txt`; `docs/evidence-and-reproducibility.md` names
    `raw-result.json`, `stdout.log`, `stderr.log`. Both sets are emitted
    byte-identical; the deviation is recorded in each manifest and in
    `execution-report.yaml`. Extra side artifacts: `matrices.json` in
    RUN-ENDO-003/004/005/006 (relation matrices consumed by later runs).
15. **Budgets enforcement.** Per-run hard cap 1800 s: internal self-cap at
    1700 s raises a `ResourceExhaustion` recorded with that terminal status.
    Memory: darwin rejects `setrlimit(RLIMIT_AS)` (documented mechanism in
    every manifest); the 4 GB cap is enforced post-hoc against measured peak
    RSS (`getrusage`, bytes on darwin), with a proactive self-abort at
    3.75 GB. Overflow → `resource_exhaustion`.

## Corrections found in pre-run smoke testing (fixed before any real run)

Smoke runs into a scratch root (`--out-root`, disjoint from the experiment's
run records) exposed five implementation defects, all fixed before the
recorded execution; no recorded run was produced by the defective code:

1. **Smooth j=0 twist orders.** The first seed-derived 24-bit p gave all six
   sextic twist orders with largest prime factor ≤ 2^15.3 (400 b's rejected).
   The generators now walk the deterministic nextprime chain to the next
   congruent p ("regeneration", the frozen stop rule's contemplated case;
   count recorded per cell). Also: `order_bsgs` can return a small common
   annihilator of its two probe points; the order candidate is now verified
   on 3 seeded points with exact naive-order fallback (bsgs matched naive
   exactly in a spot check).
2. **Exact-membership resolution for point-column factor bases.** An x-wise
   hit whose resolved signed summands are not exact FB members is not a
   decomposition over a signed-point FB; the engine now filters those for
   point-column arms (x-column arms keep free-sign bookkeeping). Without
   this the generic random baseline overcounted hits and dropped rows.
3. **Repeated-summand relations excluded** (2G_i + G_j = R) so all matrix
   rows are strict 0/1 (counted in resolve_stats; negligible rate).
4. **Wiedemann solve construction** (decision 11a above).
5. **Chunked Gaussian elimination.** Whole-submatrix temporaries in the
   dense modular GE fragmented the darwin allocator to 6.9 GB RSS on the
   10809×3318 subsystem pool (tripped the 3.75 GB self-abort in smoke);
   elimination now runs in 512-row chunks with reused buffers (peak ~A+50 MB).

## Certificate strategy

- Relation matrices: every row's decomposition certificate re-verified with
  `harness/toycurve` arithmetic (independent of the numpy x-engine) before
  use; failure would make the run `completed_invalid`.
- Rho baselines: discrete-log certificates, independently recomputed and
  cross-checked against the recorded (a,b) and frozen secret.
- Measurement-only runs (displacement, penalty, aggregation, AP): `kind:
  none` with the verifier named.

## Known limitations (disclosed, not smoothed)

- Hit rates near 1.0 on all non-AP arms at these sizes (near-census of the
  tested distribution): the penalty measurement is tight but the
  wider-aperture regime (smaller B relative to N) is untested at this tier.
- alpha = 0 (exact invariance) makes B/alpha an infinite threshold; this is
  recorded as `threshold_infinite_because_alpha_zero`, never as a number.
- The generic arm's signed-point columns differ in kind from the GLV arms'
  x-coordinate columns (decision 4); comparability is via identical column
  count, curve, targets, and measurement code.
