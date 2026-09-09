# Implementation note — EXP-ECRANK-73275e v2 replication round / TASK-20260908-5291f8

Executor implementation of the APPROVED additive protocol amendment
`experiments/EXP-ECRANK-73275e/amendments/v2_replication_protocol.yaml`
(sha256 6f61031861c97da69eac11b947fb7f51e0cf522e3676d3820a5411d8933f847d,
approved by DEC-20260908-614199) on top of the untouched v1 frozen contract
(`specification.yaml`, sha256 ae6d170af4fe2e6ffb8f136304f4735b1461c7541f68119a5322888116483c8e).
Observations only; no status language; no HEUR-1 verdict; no interpretation
branch selected.

## Provenance

- `source-v2/` is NEW code. It reuses the v1 `source/` modules
  (`ecrank_engine`, `construct`, `null_family`, `certify76`) BY IMPORT
  (the v1 files are not edited). The v1 source is hash-bound by the
  amendment (`bound_source_hashes`) and by per-run manifests
  (`source_sha256_v1`).
- The committed F_l certifier
  (`coordination/goals/GOAL-ECQ-002/.../exact_certify.py`, sha256
  1bc7c05954fdf9531c41eb942e91f918e401098971b2211501a9628ae011ea8e) is
  imported byte-identical via `ecrank_engine.load_exact_certify` and run
  unchanged; only its prime search bound is threaded through rung by rung
  (IC-V2-1).
- The plant builders are FROZEN in `source-v2/plant_builder.py` BEFORE any
  R10/R11 step (the v1 null_family freeze discipline applied to plants, per
  the amendment's IV-3R plant_builder_freeze). They derive plants
  constructively and never import R3's found-instance list.

## Implementation choices (not protocol changes)

- IC-V2-1. Certifier ladder (IV-1C / R11). The committed certifier exposes
  `certify(a_invariants, points, max_prime=1500, ...)`. The v1
  `certify76.certify_instance` calls it with the DEFAULT max_prime=1500 and
  does not expose the bound. `source-v2/certify_ladder.py` reuses v1
  `certify76.certify_instance` by import and threads the bound through by
  temporarily wrapping the committed module's `certify` entry point with the
  requested max_prime (restored in a `finally` block, so the committed module
  is left unmodified after each call). Nothing else about the certificate
  changes. The FIXED three-rung ladder is 1500 / 10000 / 100000; all rungs
  are reported for every tuple with op costs; the ladder is non-adaptive.
  OBSERVED (recorded, not interpreted): the committed certifier's good-prime
  list is capped at 60 primes (`max_good_primes=60`), and the first 60 good
  primes are all below 1500, so raising `max_prime` from 1500 to 100000 adds
  no good primes for the tested tuples; the certified totals and op costs are
  identical across rungs. This is an instrument-boundary observation recorded
  in the per-rung ledgers; IV-1C is graded on the top rung per the amendment.
- IC-V2-2. Plant builders (IV-3R / R10, R11). `build_plants_n6` builds the
  R3-FAMILY SHAPE: the prescribed-square pattern (dpat from a seeded coset)
  with carrier r_n and the n=6 univariate quadratic solve in t (g = x + t);
  it keeps rational in-box roots that produce ELLIPTIC instances (deg s = 4,
  disc != 0), a distinct (b-tuple, pattern) pair, no shared h0, inside the
  frozen box (r-height <= 10^4). `build_plants_n8_r7` builds the R7 family
  (d=(1..1)) at n=8 (elliptic, deg s = 3); each plant is determined by its
  b-tuple. Both derive every object from the named run seed via
  `random.Random(seed)` (no derived-seed practice). Each plant records its
  b-stream position (the index of the (b, dpat) sample that produced it,
  1-indexed over all samples).
- IC-V2-3. N2R convention B height. For n=6 the free coordinate is t with
  g = x + t, so r_i = t + b_i and, since b_0 = 0 (affine normal form),
  t = r_0 exactly; h_B = rat_height(r_0). For n=8 the free coordinate solved
  by the quadratic is c with g = x^3 + a x^2 + b x + c, so g(0) = c and,
  since b_0 = 0, c = r_0; h_B = rat_height(r_0). Thus h_B = rat_height(r[0])
  for both n=6 and n=8, in canonical minimal form. Convention A is the
  recorded r_height (h_A = max_i rat_height(r_i)). Both predicates are
  recorded VERBATIM from the frozen source into the R12/R14 raw results
  BEFORE any count (n2r_reconciliation exact_predicate_binding).
- IC-V2-4. Construct arm (R12/R13/R14). `source-v2/construct_v2.py` is a
  copy-with-record of v1 `construct.construct_arm`. The ONLY changes: the
  counted-ops cap is a parameter (v1 used the module global OPS_CAP = 1.0e8),
  and a wall-clock cap check (7200 s) is added inside the b-tuple loop (v1
  had no wall-clock check in the loop), per the amendment's per-run stopping
  rule. All helper functions are imported from v1 `construct` (read-only).
  For R14 the cap is 2.0e9; because v1 `solve_n8` reads the module global
  `construct.OPS_CAP` internally, `construct.OPS_CAP` is set to 2.0e9 for the
  duration of the R14 arm and restored afterward.
- IC-V2-5. Null run (R15). A dedicated `run_r15` (not `construct_arm`) records
  the non-destructive per-b_index proof ledger (RD-1): an append-only ledger
  with the b_index-0 record written first and never overwritten; the raw
  result retains the b_index-0 proof and its sha256. The v1 PD-1 defect
  (null_proof_first overwritten after b_index 0) is not repeated.
- IC-V2-6. R10 exponent gate "height ratio" (IV-3R (b)). The amendment's
  "each recovered plant's reported height ratio" is computed as
  height_ratio = h_A / h_B = (recorded r_height) / (rat_height of the solved
  free coordinate t = r_0), checked against the FROZEN v1 window
  [0.699, 1.301] (SR-6 carried verbatim). This is a documented
  implementation choice for an imprecise term; the exact per-plant values are
  recorded so the Coordinator/reviewers can re-interpret. Per the amendment,
  failure of (b)/(c) voids ONLY the planted-height calibration reading (not
  detection or counts). The aggregate log-log slope of the planted yield is
  additionally recorded for context (the IC-7 "exponent gate" reading).
- IC-V2-7. IV-2R / RD-2 canonical comparison. The R13 counts-identity flag is
  computed on canonically serialized (string-keyed, sorted) dicts AFTER JSON
  serialization (`json.dumps(..., sort_keys=True, default=str)`); the raw
  flag records the comparison basis. This repairs the v1 R4 int-vs-str bug.
- IC-V2-8. R15 infeasibility flag (IV-4R). The infeasibility flag is
  `no_real_root` (the null quadratic has no real root, hence no rational
  in-box root). For the d=(1..1) family at n=6 the ellipticity quadratic is
  degenerate (A = B = 0; the objects are conics with no x^5 condition), so
  the null family is the "1 = 0" sentinel (C_null = 1), infeasible via
  `no_real_root = True` (the A == 0 and C_null != 0 and B == 0 branch of
  `null_family.infeasible_proof`), NOT via a negative discriminant (disc = 0,
  so `disc_negative = False`). `disc_negative` is recorded per tuple as a
  detail. (Attempt 1 of R15 used the too-strict `disc_negative` check and is
  preserved under `attempt-1-iv4r-check-too-strict/` per IV-6.)

## Seeds (fresh, declared pre-run, disjoint from v1, never adjusted)

- 760906 -> R12 construct-n6 replication AND R13 bit-for-bit replay (IV-2R).
- 760908 -> R10 planted ELLIPTIC n=6 detection control (IV-3R).
- 760910 -> R14 construct-n8 rescoped.
- 760912 -> R9 amended known-false d=(1..1) control (IV-1R n=6 + IV-1C n=8).
- 760914 -> R11 planted n=8 control (R7 family).
- 760916 -> R15 null-object re-run (IV-4R).

All derivations (coset choice, b-tuple order, coefficient sub-boxes, planted
positions) via `random.Random(seed)`, as in v1. No derived-seed practice.

## Deviations

None from the frozen protocol fields. Run slots, seeds, H boxes, the fixed
certifier ladder, the frozen sample sizes (10^4 b-tuples per construction
arm; 64 for the null run, matching v1 R6), the per-run counted-ops caps
(1.0e8; R14 2.0e9), the 7200 s wall cap, the attempt ceiling (12), and the
control-admission ordering are as specified. The n=8 integer-box convention
(IC-732-3) is RETAINED and disclosed verbatim in every R14 raw result (N3R).
The only recorded attempt beyond the first is R15 attempt 1 (a driver
check-logic defect, preserved per IV-6; the underlying observation was valid).
