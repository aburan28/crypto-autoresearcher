# EXP-MTIC-001 implementation note (Executor, TASK-20260727-001)

Frozen protocol: `experiments/EXP-MTIC-001/specification.yaml` **version 2**
(approved, frozen), incorporating amendment `amendments/AMEND-001.yaml`
(AMEND-EXP-MTIC-001-001). This note describes the implementation and discloses
every design decision taken inside the protocol's explicit latitude. No
protocol element was changed; no amendment was requested. The v1 stop report
(specification_error) is preserved at
`execution-report-specification-error-v1.yaml`.

## Code

- `code/run_mtic.py` — the entire driver, one CLI entry per planned run:
  `python3 experiments/EXP-MTIC-001/code/run_mtic.py --run-id RUN-MTIC-00X`
  (recorded verbatim in each `command.txt`). `--out-root` exists for scratch
  smoke tests only and is recorded in the command when used.

Reused read-only code (disclosed per handoff): `harness/toycurve.py`
(curve arithmetic, `generate_instance`, `_seed_int`), `harness/semaev.py`
(`build_factor_base`, `s4_expr`, summation symbols), `harness/rho.py`
(matched rho baseline, `total_group_operations` accounting). Patterns adapted
from `experiments/EXP-ENDO-001` (run-record writer, enumeration engine,
Berlekamp–Massey/Wiedemann, chunked modular Gaussian elimination, BSGS,
budget guard, git-state/dirty basis) per the handoff's reuse invitation.
Nothing outside `experiments/EXP-MTIC-001/` was modified. `harness/runner.py`
was *not* used: its artifact naming predates the spec's `required_artifacts`
naming; the ENDO-style writer emits the spec's names plus byte-identical
docs-style duplicates.

## Design decisions inside the protocol's latitude

1. **Instances (pinned by AMEND-001).**
   `generate_instance(seed, field_bits, min_prime_order_bits=field_bits-2)`,
   seed 1 → 16 bits, seed 2 → 20 bits, seed 3 → 24 bits. Recorded per
   instance with full derivation and core checks (p prime, n prime, P/Q on
   curve, Q = k·P, n·P = O).
2. **Derivation tags (frozen-derivation-tag convention).** Targets:
   `R = a·P + b·Q` with `a = _seed_int(seed, "{tag}a{j}") % n`,
   `b = _seed_int(seed, "{tag}b{j}") % n`, skipping R = O. Tags: `desc`
   (50 descent), `harv` (2000 harvest), `cal` (3 rho-calibration, disjoint
   stream). All (a, b) recorded in `frozen-instances.yaml`.
3. **Factor bases.** Primary `B = ceil(sqrt(N))` via
   `harness/semaev.py build_factor_base(inst, B)` (seeded `fb{j}` stream of
   the frozen instance seed); 20-bit ablations `ceil(N^(1/3))` and
   `ceil(N^(2/5))` via the same function at those sizes (exact integer
   roots). All frozen with SHA-256 in RUN-MTIC-001.
4. **Calibrations (frozen in RUN-MTIC-001 before any descent).**
   `rho_walk_rate = Σ total_group_operations / Σ wall_seconds` over 3 seeded
   calibration targets + the instance's own Q (4 solves per size).
   `bsgs_construction_rate = m / build_seconds` of one BSGS baby-table
   construction (m = isqrt(N)+1). Measured values: rho 1.26e6–1.56e6 ops/s;
   bsgs 2.78e5–1.46e6 ops/s. The 16-bit bsgs rate is 5.6× below the rho rate
   (HEUR-001 anticipates ≤2×); this is a tiny-sample timer-granularity
   artifact (m = 133 adds ≈ 0.5 ms total) — recorded as an anomaly; no
   decision can flip on it at the measured magnitudes (decision 10).
5. **Cost accounting (HEUR-001 three accountings).** IC phase costs are
   measured wall seconds × the frozen per-size calibration rate:
   `group_ops_rho` (primary; rho-walk rate), `group_ops_bsgs`
   (bsgs-construction rate), `wall_seconds` (raw seconds; sqrt(N) realized
   as sqrt(N)/rho_rate, N in the frontier product realized as
   N/rho_rate³ — the product S·T² is **cubic** in the cost unit; a squared
   conversion was a unit bug caught in pre-run unit checks). T_verify = 3
   group ops (m = 3 summands; the frozen reading recorded in the v1 stop
   report) in op accountings, measured seconds in the wall accounting. The
   wall and rho ratios are then identical up to the T_verify conversion
   (relative difference ~1e-6 here) — disclosed in every aggregation; the
   non-trivial audit is rho-vs-bsgs constants. The rho baseline is reported
   natively (`total_group_operations`) in op accountings and in seconds in
   the wall accounting. Native secondary counts (tuple evaluations,
   Wiedemann field ops) are recorded beside the charged costs.
6. **S_rel (enumeration-assisted relation collection).** Pair-sum x-table
   over the frozen factor base (x(G_i ± G_j), i < j; vectorized exact mod-p
   arithmetic in numpy int64; adapted from EXP-ENDO-001) plus per-target
   probes x(R − G); a table hit is resolved into an exact **signed**
   relation R = σ₁G₁ + σ₂G₂ + σ₃G₃ and certificate-verified with
   `harness/toycurve` arithmetic (independent path). Collection stops at
   ceil(1.2·B) distinct verified relations, at 5e7 tuple evaluations, or at
   1500 s cumulative (frozen stop rule); a partial yield would be recorded
   as a censored lower bound (did not occur). Yield curve checkpointed every
   25 targets. Two engine corrections versus EXP-ENDO-001's collector,
   both found in smoke and disclosed:
   (a) ENDO's resolver mis-signed the `x(G_i − G_j)`/positive case as
   `[Gg, Gi, Gj]`; its final EC verification rejected those valid relations
   (an undercount, never a false relation). Fixed here as `[Gg, Gi, −Gj]`.
   (b) Relation matrix rows must carry the summand **signs** (`[[col, ±1]]`)
   to be consistent with the true harvested rhs; ENDO's all-+1 structural
   rows were harmless only because its solves used synthetic rhs. Verified
   in smoke: signed rows make the harvested system exactly consistent
   (0 row failures on all rows).
7. **Relation consistency (subgroup-component logs).** The rhs of relation t
   is `a_t + b_t·k (mod n)` (recorded (a, b) + frozen k). Every relation is
   consistent with the vector of subgroup-component logs: writing an FB
   point G as G_N + G_c with G_N = g·P in the prime-order subgroup, the
   point relation implies Σσg = a + b·k (mod n). (If n² | #E the component
   decomposition is not canonical; the solution verification against ALL
   harvested rows is the executable check — it passed at all three sizes.)
8. **S_LA (Wiedemann over Z/N).** Weight-3 signed 0/1 relation matrices at
   the frozen ceil(1.2·B) row count are generically rank-deficient
   (measured: rank 129/133, 364/374, 3272/3317), and plain Wiedemann on the
   singular square matrix cannot converge (M|im defective, C[L]=0; measured
   in pre-run smoke at all three sizes, consistent with EXP-ENDO-001's
   recorded observation). Construction (EXP-ENDO-001 DEV-7 greedy-subsystem
   precedent, adapted to the frozen 1.2B harvest): greedy row basis × a
   column basis of it → nonsingular r×r block; true-rhs Wiedemann (≤5 seeded
   attempts); solution zero-extended on the B−r free columns → a particular
   solution of the FULL system (dropped rows are linear combinations;
   consistency verified on **all** harvested rows — the spec's "sample of
   harvested relations" executed at the full set). Free columns are not
   determined by the 1.2B-row system (rank deficit recorded); the table is a
   valid particular solution, which is all the metrics and the
   non-interference control require (the table is never used for descent —
   T_desc is measured by Groebner). If the block solve had failed, a
   consistent-rhs attempt (b = M·x0 seeded, ≤3 attempts) was the recorded
   last resort, then `resource_exhaustion` per the frozen stop rule. Rank
   selection and column-basis seconds are recorded separately from
   `s_la_seconds` (the Wiedemann solve wall time).
9. **T_desc (S_4 Groebner solves).** System per target:
   `<S4(x1,x2,x3,xR), fV(x1), fV(x2), fV(x3)>` over F_p, grevlex
   (`harness/semaev.py` convention), sympy Buchberger (`sympy.groebner`,
   `modulus=p`). S4 from `harness/semaev.s4_expr`. fV(x) = ∏(x − v) built by
   exact numpy int64 convolution (entries < p < 2²⁵, products < 2⁵⁰) —
   byte-exact versus `sympy.prod` expansion, verified by full coefficient
   equality at B ≤ 500 (all three variables) and by 3-point seeded
   evaluation at larger B (verified every setup; failure would raise).
   Setup (S4 resultant + fV) is one-time per (curve, factor base),
   preprocessing-derivable, recorded per instance and **excluded** from
   per-target T_desc. Per-solve hard cap 60 s (SIGALRM); capped solves
   charge the full 60 s and record `trivial_ideal = None` (verdict unknown,
   never conflated with non-trivial); the frozen cumulative cap 1500 s
   leaves unattempted targets `cancelled_by_budget` with the measured prefix
   retained. Aux ground truth per attempted target (enumeration probe +
   signed certificate; **not charged to any metric**, costs recorded
   separately): cross-checks the ideal verdict (disagreements are anomalies)
   and times T_verify.
10. **Descent execution order (latitude).** The frozen protocol pins 50
    targets per instance (25 per ablation base) and the cumulative cap but
    not the order across instances/bases. Pre-run probes showed every solve
    caps at 60 s, so a sequential order would have cancelled the 24-bit
    instance wholesale. Targets are therefore attempted **round-robin**
    across jobs under the shared cap so every instance/basis receives
    measured targets (13/12 at 20/24-bit with 25 attempts). Recorded in run
    metrics.
11. **CTRL-NONINTERFERENCE execution.** The table (curve id, FB hash, matrix
    hash, solve mode, solution) is built fully under three protocols:
    (a) as-is — the single frozen table served to every descent target
    (served hash echoed per target; the control's "identical for every
    descent target" realized without 50 redundant rebuilds, since the table
    is built once and never rebuilt); (b) with the descent list permuted
    (seeded permutation passed to the build entrypoint, accepted-but-unused);
    (c) withheld — descent targets generated only after the table freeze
    (in-run ordering). Three content SHA-256s compared; RUN-005's solution
    reproduction recorded as a determinism bonus. Static audit: the build
    code path receives only (instance, factor base, relations, seed).
12. **CTRL-RHO-BASELINE / CTRL-BSGS-BASELINE.** `harness/rho.py` per-target
    solves on the same 50 descent targets (discrete-log certificates:
    independent recompute k·P == R AND cross-check k_R = a + b·k mod n
    against the recorded (a, b) and frozen secret). BSGS full solve per
    instance on descent target 0 with group-op counting, table entries, and
    a labeled memory estimate (`sys.getsizeof` dict + per-entry).
13. **CTRL-SINGLE-TARGET.** K = 1 total IC cost (S_rel + S_LA + T_desc +
    T_verify) vs measured rho median per target, under all three
    accountings. Partial-component rule (disclosed): a missing/unconverged S
    component is ≥ 0, so a measured partial sum already exceeding rho makes
    the comparison robust; otherwise it is recorded undecidable. A violation
    would trigger the K* = 1 falsifier path (recorded, not classified).
14. **Aggregation (RUN-MTIC-010).** Per instance and accounting: S, T, K*
    (ceil, infinite when denominator ≤ 0), frontier_product_ratio, amortized
    C_IC(K*)/K* and at 10·K* vs rho median, regime classification
    ((i) / (ii) / FLAG-K*=1 / FLAG-below-frontier recorded verbatim and
    escalated, never classified), stability across the three accountings
    (CTRL-CALIBRATION-AUDIT). Partial path (disclosed): when T_desc is
    measured but an S component is missing, the K*-infinite sign (denominator
    ≤ 0) is S-independent and recorded; the frontier product is then not
    computable and recorded as such. Censoring per the frozen rule
    throughout; IQR ≤ median computed on uncensored solves per the frozen
    decisiveness note. `analysis.md` is observation/comparison/limitation
    only — no conclusion about H-MTIC-001.
15. **Artifact naming (deviation, recorded in every manifest).** Frozen
    `required_artifacts` name raw.json/summary.json/stdout.txt/stderr.txt;
    `docs/evidence-and-reproducibility.md` names raw-result.json/stdout.log/
    stderr.log. Both sets emitted byte-identical. Extra side artifact:
    `relations.json` in RUN-MTIC-002/003/004 (harvested relations consumed
    by RUN-MTIC-005/006; EXP-ENDO-001 matrices.json precedent).
16. **Budgets.** Per-run hard cap 1800 s: internal self-cap 1700 s raises
    `ResourceExhaustion` recorded with that terminal status. Memory: darwin
    rejects `setrlimit(RLIMIT_AS)`; the 4 GB cap is enforced post-hoc
    against measured peak RSS (`getrusage`, bytes on darwin) with a
    proactive self-abort at 3.75 GB (mechanism in every manifest).
17. **Git state.** Manifest commit = `git rev-parse HEAD`; dirty computed
    over `git status --porcelain --untracked-files=no` excluding AppleDouble
    `._` paths (exFAT artifact; basis string recorded in every manifest).
    No git mutations of any kind by the Executor; this experiment's new
    files are untracked (archived later by the Coordinator's snapshot task).

## Smoke-test corrections (fixed before any recorded run)

All validation below ran into a scratch `--out-root` (no experiment record
was produced by defective code):

1. Signed matrix rows (decision 6b) — 31–708 row verification failures with
   unsigned rows at all sizes; 0 after the fix.
2. Maxrank subsystem LA construction (decision 8) — plain/consistent-rhs
   Wiedemann on the rank-deficient square matrices failed all measured
   attempts at all sizes; the r×r block construction converges on attempt 1
   at all sizes and verifies on all rows.
3. Cubic wall-accounting conversion (decision 5) — caught by unit check.
4. ENDO resolver s==1 sign bug (decision 6a) — fixed; relations are
   EC-verified regardless.
5. fV fast construction (decision 9) — sympy expansion extrapolated to
   ~6 min at B = 3317; numpy convolution with verification runs in seconds.

## Known limitations (disclosed, not smoothed)

- Pre-run probes show every S_4 solve at every size caps at 60 s: T_desc is
  censored-heavy by design of the frozen solver/cap. The frozen censoring
  rule (full cap charge) makes the regime-(i) sign robust exactly as the
  pre-registered prediction notes.
- The factor-base log table recovers B−r of the B logs only (rank deficit
  measured); sufficient for the metrics and control at hand.
- The 16-bit bsgs calibration constant is timer-granularity-noisy
  (decision 4); the audit reports decisions under it unchanged.
