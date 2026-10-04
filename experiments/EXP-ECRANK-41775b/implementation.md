# Implementation note — EXP-ECRANK-41775b v1 (executor, TASK-20260910-87e6fd)

Executor implementation note for the frozen, APPROVED contract
`experiments/EXP-ECRANK-41775b/specification.yaml` v1 (frozen bytes
sha256 e119117426fa41eb40d353c553c09c2f06d1b211cc7db01897a92a2650e2471f,
approved per DEC-20260910-c10298). Observations only: this note and the
run records interpret nothing, select no branch, use no hypothesis
language, and change no status.

## Source layout

- `source/run_package.py` — SUPERSEDED DRAFT (preserved immutable, never
  executed as a run): an early calibration family-1 constructor whose
  convention-A/B counts mismatched the frozen hand expectations in a dev
  smoke check (Fractions auto-reduced (q+7)/q so the high-root heights
  landed above 10^3; convention A and B placed roots in different bands).
  No run record was written from it; the mismatch was found by the dev
  self-check before any run executed.
- `source/run_package_v2.py` — the executed implementation (all five
  runs). Supersedes the draft.
- `source/_scratch_inspect*.py` — read-only reconnaissance scratch used
  during implementation (bound-byte hashing, committed-data inspection,
  pre-verification of the coset reconstruction and certificate path,
  op-cost breakdown). Not protocol artifacts; not imported by any run.

## Protocol deviations

NONE. The frozen contract was executed exactly as written. Specific
fidelity notes (implementations of frozen text, not deviations):

1. **SR-4 at every run start.** All 11 bound source files hash-verified
   against the committed R12 manifest values (which the v2 amendment's
   `bound_source_hashes` bind) before every run; all matched, so no
   SR-4 stop fired. Input data files are hashed at run start into each
   run record's `inputs.input_data_hashes` (custody record).

2. **R1 (T4, admission first).** The counting/decade-ratio instrument is
   reimplemented from the N2R convention definitions in the bound
   `source-v2/n2r.py` (conventions A and B; `rat_height` predicate
   verbatim from bound `source/construct.py` lines 23-24), exact
   Fractions, no floating point. The two families are deterministic
   constructors (no seeds). Family 1: K=200 tuples, two admissible roots
   each — low root t an integer in [2,99] with r-vector constant (heights
   in [2,99] < 10^2), high root t = n/1000 (n odd, 5∤n; lowest terms,
   height exactly 1000 = 10^3, inside [10^3,10^4)); the r-vector-constant
   construction makes both conventions read the same height per root.
   Family 2: one root per tuple, exactly 40 roots in each band
   [10^d, 10^(d+1)), d=1..4. The family-definition note (in
   instrument-verdicts.json and calibration-families.json) states
   exactly that these are instrument known-answer families for the
   counting/ratio stage (the stage the frozen protocol calibrates), with
   the b field recording lineage only. Both families reproduced every
   hand-computed count and ratio exactly (family 1: N^A = N^B =
   {10^2:200, 10^3:400, 10^4:400}, ratios [2,1], two-decade 2; family 2:
   40 per decade under both conventions). Calibration PASS; SR-2 did not
   fire.

3. **R2 (T1).** Static ast trace (stdlib `ast`) of the bound
   `source/construct.py` and `source-v2/construct_v2.py` over the frozen
   function set; every H/H_top use site with line number, source line,
   and syntactic role. solve_n8's trace is recorded verbatim and
   DESCRIPTIVE only (its H uses: line 305 `Bbox = min(int(H), 20)`
   coefficient-box width, line 333 `if h > H` admission filter — both
   inside solve_n8, no n=8 adjudication claimed). construct_arm /
   construct_arm_v2 have no H/H_top parameter (H enters via
   H_levels -> H_top = max(H_levels) at v1 line 366 / v2 line 45 and the
   cumulative count loop; recorded as use-site notes with line numbers).
   P1 criterion: in solve_n6 (bound lines 65-95) H appears ONLY at line
   86 (`if h > H:`) — met; no SR-3 stop. Dynamic double-invocation of
   the bound `solve_n6` at H=10^4 and H=10^9 on the frozen b_index
   649/1299/4995 tuples (read from the committed R12 bytes): meta
   (A, B, C, n_rational_roots) identical and root-set unions identical
   on all three tuples; the kept/near partition differs only by the
   height filter (all six invocations returned the same kept sets here —
   the committed roots of those tuples all have heights <= 10^4, so the
   partition is in fact identical too; the check machinery is recorded
   in dynamic-diff.json).

4. **R3 (T2).** No solver re-run, no new b-tuples, no seeds. P2
   precondition: the committed R12 near-miss ledger is EMPTY
   (near_miss_total 0, ledger length 0, r_height entries 0) — recorded
   exactly, with the shortfall note and lower-bound labeling discipline
   per C3 (the recoverable subset is the kept set; the found[] instances
   carry complete exact root data, t = r_0 exactly since b_0 = 0). For
   each of the 33 committed found instances: r_i = g(b_i) with g = [t,1]
   recomputed exactly (all 33 match the committed r vectors), h_A / h_B
   per the bound conventions, `engine.build_instance(xs, dpat, r, 6)`
   re-run (H-independent; all 33 kept). Band counts
   N^{A,ext}(H') = N^{B,ext}(H') = 33 for all H' in {10^4, 10^5, 10^6,
   10^7} (max h_A 4304, max h_B 378 — all below 10^4 already); every
   decade ratio exactly 1 under both conventions; three-decade ratio
   10^4->10^7 exactly 1; saturation ceiling 33 under both conventions
   (33 kept + 0 recoverable re-admissible roots); multiplicity histogram
   {1: 11, 2: 11}, max multiplicity 2 (= the Bezout bound). n=8 band
   VACUOUS verbatim from the committed R14 zeros (found 0,
   near_miss_total 0) — no computation performed on that band.
   **C6 certificate recomputation (disclosed in-run):** the same
   certificate path as R12 (bound `certify76.certify_instance` with the
   committed coset — reconstructed exactly from the committed R12 seed
   760906 derivation and cross-checked against the committed coset_V
   before use — and the committed exact_certify module) was run over the
   found instances in committed order and STOPPED exactly at the frozen
   1.0e6 counted-ops cap (IC-1) after 19 of 33 rows (ops 1,066,392);
   reported AS exhaustion per SR-1 (rules 3/5), never re-scored. All 19
   certified rows match the committed certificates exactly (verdict PASS
   and aggregate totals). Rows 20-33 are recorded as
   not-certified-in-run, never dropped. The readmission path itself
   (peval + build_instance over 33 rows) cost 59,740 counted ops, inside
   the cap.

5. **R4 (T3).** `derivation.md` (authored text) carries the numbered
   steps 1-12 with the citation provenance table; every recalled pointer
   (Hasse-Minkowski per Serre Ch. IV as recorded in H-ECRANK-ee6e0e; the
   Schinzel/Nagao/Birch genre pointers) stays marked recalled-not-
   verified, and Step 5 shows Hasse-Minkowski is not load-bearing for
   this derivation. HEUR-1-C is stated as CANDIDATE text, status
   proposed, never validated. The proves-too-much control (Steps 10-12;
   machine record in proves-too-much-control.json) applies the
   structural argument to the draw-side committed data and records the
   explicit diverging step (the draw-side sub-box of 5 seeded
   coordinates grows with H by construction, so the fixed-multiset
   saturation premise fails there); the argument does NOT predict
   draw-side saturation where F1 fired — no DEFECT recorded. Spot checks
   (spot-check.json): exponent form 5-n/2 at n=6/8/10 -> 2/1/0 exact
   Fractions; per-decade prediction factor 100 at n=6; the committed
   measured v2 ratios as exact Fractions (A 7/5, 33/28; B 33/26, 1);
   the construct candidate bound <= 2; R12 height extrema; the R3
   extended-band ratios re-quoted exactly.

6. **R5 (determinism).** Fresh-process replay: R1 verdict bit-for-bit
   identical, all 13 quoted R3 fields identical, R2 trace recomputed
   identical, 12 R2/R4 artifacts re-hashed; replay-diff.json empty
   (`replay_diff_empty: true`).

## Environment and provenance

All runs: CPython 3.12.8, macOS 26.6 (Darwin 25.6.0) arm64,
Adams-MacBook-Pro.local, stdlib-only, no network, no seeds drawn, no
floating point in any verdict or checked statement. Code revision at
runs: commit a223443530eee62cfdd5c18601b06265e6492e59, dirty true (this
experiment's own new files under experiments/EXP-ECRANK-41775b/ plus the
BATCH-2305cb task directory; nothing outside the write scope was
touched). Resolved runtime/model provenance is recorded as reported by
the runtime (vllm/qwen3.8-27b, opencode_native, model_verified false, no
adapter probe claimed); Bedrock guard negative (rule 16). Workers made
no commits; all artifacts await the Coordinator's snapshot task
TASK-20260910-59f080.

## Reproduction

Each run directory's `command.txt` records the exact command
(`python3 experiments/EXP-ECRANK-41775b/source/run_package_v2.py --run
R{1..5}`); `manifest.yaml` carries the nested run record with commit,
command, environment, input hashes, timing, and metrics;
`raw-result.json` carries the full observation payload; SR-4 bound-hash
verification re-runs at every invocation.
