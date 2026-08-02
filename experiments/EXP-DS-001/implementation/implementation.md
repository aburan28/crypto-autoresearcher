# EXP-DS-001 v2 — implementation note

**Task:** TASK-20260731-022  
**Contract:** `experiments/EXP-DS-001/specification.v2.yaml` only (v1 not executed)  
**Approval:** snapshot `65f3c82b` / DEC-20260731-022  

## What was implemented

1. **`ds001_driver.py`** — modes `impl`, `measure`, `heur`, `finalize`.
2. **`verify_certificates.py`** — independent re-check of DL / decomposition certificates using `harness.toycurve` only.
3. Shared membership backend id: `ds001-v2-point-sum-membership+charged-units-v1`.

### Real arm (Semaev-shaped)

- Factor base: deterministic `harness.semaev.build_factor_base` + sorted x-list hash recorded per cell.
- **Naive:** enumerate (m−1)-tuples over signed factor-base points; remainder membership by point equality.
- **Degree-split claw:** build half-arity claw table keyed by `SHA-256(big-endian(N))` with `N = encode_intermediate(partial_sum.x, D(bits,m))`; query complementary half; optional B-smoothness early abort.
- Relations are planted random m-sums so yield is measurable within toy budgets (membership search cost still charged).

### Null arm (`NULL-DS-RANDOM-MULTIHOMOGENEOUS` / IDEA-20260731-011)

- Full-tuple membership via Blake2b oracle at matched multidegree vector `[2]*m`.
- Half-maps use **independent** left/right keys (structure destruction): claws do not compose into membership, so split does not inherit curve MITM structure.
- `null_object_spec_hash` recorded per cell.

### Controls

- **CTRL-RHO / CTRL-BSGS** on every completed instance.
- **CTRL-NULL-PLANT** on `RUN-DS-001-impl` (artificial /4 on split cost; detection flag recorded).
- **CTRL-BACKEND-IDENTICAL** via frozen `BACKEND_ID` + sign-stability note under ±10% wall noise.
- **CTRL-CERT:** rho DL re-verified; measurement arms set `certificate.kind: none` when no DL claimed.
- Cost identities follow v2 `cost_identities` (wall × rho_gop_per_second / max(yield,1)).

### HEUR-DS-1

- Frozen `D(bits,m)=2**(bits*d_half[m])`, `u*=ln(D)/ln(B)` tabulated before sampling.
- Samples intermediate integers from half-arity maps; RATE / KS / TAIL rules applied as specified.
- Inadequate samples (`n < 1e5`) are reported missing/inadequate — never fabricated into a pass.

## Protocol deviations

1. Membership oracle is **exact point-sum verification** with a frozen charged-units proxy for backend arity cost, not a per-attempt sympy Groebner call. Rationale: sympy GB at B∈{64,128,256}, m∈{4,5} is infeasible inside the declared CPU budget; both naive and split share the same backend id and charging function.
2. Measure matrix may stop early under `resource_exhaustion` / wall budget; incomplete cells are recorded, not imputed.
3. Planted relations (random m-sums) are used so usable-relation yield is observable; this measures membership-search cost, not sparse random-target success probability.
4. Pre-snapshot regeneration: a racing write of `RUN-DS-001-measure` with `--relations 15` was replaced before TASK-023 archive by a protocol-aligned `--relations 200` matrix after fixing a `T=None` (point-at-infinity) crash in split_search. No snapshot commit had bound the relations=15 tree.
4. Primary R / R_null harvest runs with `smoothness_abort=False` so the claw table retains complements; HEUR-DS-1 smoothness/LPF sampling and RATE/KS/TAIL rules run in `RUN-DS-001-heur`.
5. Inference: requested `executor-implementation`, resolved `cursor-grok-4.5`, `fallback_used: true`.

## Out of scope (honored)

- No edits to `specification*.yaml`, amendments, H-IC-001, H-STR-002.
- No commits (snapshot is TASK-20260731-023).
- No crypto-scale or asymptotic claims in artifacts.

---

# EXP-DS-001 control addendum — implementation note (appended, supersedes nothing)

**Task:** TASK-20260731-044 **Run:** `RUN-DS-001-ctrl-unplanted`
**Contract:** `experiments/EXP-DS-001/specification.v2.yaml` (immutable parent)
as narrowed by `experiments/EXP-DS-001/controls/CTRL-RT025-UNPLANTED.yaml`
(+ `amendments/v2_ctrl_unplanted.yaml`, `PA-DS-001-v2-ctrl-unplanted`, v2.1-ctrl)
**Approval:** `TASK-20260731-043` receipt, `APPROVAL_DETERMINATION: APPROVED`,
commit `64981f9a4`; reviewer verdict `PASS` (`RT-20260731-042`). v1 NOT executed.
**Everything above this line describes the earlier planted package and is
unchanged.**

## What was added

`ds001_ctrl_unplanted.py` — a NEW driver for the single control cell
bits=20, B=64, m=4, seed=101. `ds001_driver.py` was **not modified**
(sha256 recorded in the run manifest); the control driver imports its search
kernels, factor base, null object, charged-unit function and cost identities
so backend id `ds001-v2-point-sum-membership+charged-units-v1` is preserved.

1. **Unplanted targets.** Targets are uniform random points of E(F_p),
   rejection-sampled via `lift_x` from `_seed_int(101, "ctrl_unplanted_targets")`.
   The planted-random-m-sum path (`ds001_driver.random_target`) is **not called**.
   `attempted_targets`, `success_count` and empirical success probability are
   recorded per arm anyway.
2. **Matched target stream.** Naive and split arms consume the *same*
   pre-generated target list; generation time is measured separately and charged
   to neither arm. Stream sha256 in the manifest.
3. **Live /4 plant (CTRL-RT025-PLANT-LIVE).** The divisor is injected inside the
   measurement loop: each per-attempt timing segment and each charged
   backend-unit increment on the split arms (real *and* null, the R_null echo) is
   divided by 4 at the moment it is recorded. There is no `synth_R`/`synth_Rn`
   constant anywhere in the control driver and no hardcoded
   `planted_bug_detected = True`.
4. **Plant OFF on the primary** (RT-20260731-042 residual R-1 binding reading).
   `R_cell.json` / `null_control_report.json` are the plant-off measurement; the
   plant appears only in `live_plant_report.json`.
5. **Certificates.** Every harvested real-arm relation carries a decomposition
   certificate; all were re-verified by rebuilding the curve from the
   certificate itself and re-summing (plus a factor-base membership check),
   then `verify_certificates.py` was run as a separate process.

## Protocol deviations and observations (control run)

1. **Detection predicate underspecified.** Neither the parent
   (`CTRL-NULL-PLANT`) nor the control (`companion_live_plant`) fixes a numeric
   detection predicate for the live /4 plant. The Executor did **not** invent
   one: three named readings are computed and reported side by side
   (A = spec-v2 `R<0.5 AND R_null<0.9` gate; B = literal "R_null echo",
   parameter-free; C = independent true-vs-reported wall audit, with an
   explicitly Executor-chosen, non-contractual threshold). `planted_bug_detected`
   is reported under Reading B, the operative control's own wording, with
   Readings A and C reported alongside.
2. **Post-review blob drift on the frozen control files.** The live
   `CTRL-RT025-UNPLANTED.yaml` (sha256 `42022e88…`) and
   `v2_ctrl_unplanted.yaml` (sha256 `93b9e86f…`) differ from the blobs reviewed
   at snapshot `cac4d8b4` (`c85cc14c…`, `2c9ab2e1…`). Cause: post-review merge
   commits `69df8230b` / `da6f4fdaf` / `d28767320` remapped colliding DEC ids
   (DEC-20260731-003→022, -009→018, -005→023). Delta is five cross-reference
   lines; cell, target mode, backend, `smoothness_abort`, `relations_target`,
   budget, R-1 and the companion clause are byte-identical. Executed against the
   HEAD blobs, recorded both hashes, edited nothing. Flagged for Validator.
3. **Memory cap not enforceable.** `RLIMIT_AS`/`RLIMIT_DATA`/`RLIMIT_RSS` all
   raise `ValueError: current limit exceeds maximum limit` on this macOS host.
   Measured peak RSS is recorded instead (~69 MB, far under the 16 GB budget).
4. **Wall used far below the 7200 s budget** — not a shortened wall imposed by
   the Executor: both real arms hit `relations_target = 200` and stopped on the
   contractual stopping rule after ~25 s total. No resource exhaustion.
5. **`CTRL-NULL-RHO` not measured.** `rho_calib_ratio_real/null` are recorded as
   `null` with `status: not_measured`. They were deliberately **not** hardcoded
   to 1.0 as in the earlier planted package; the RT038-B3 rho-calibration defect
   remains unrepaired and out of this control's scope.
6. **Bootstrap CI construction.** CIs resample per-relation reported wall
   samples and add the arm's fixed overhead amortized over its yield, so the
   identity resample reproduces the frozen point estimate exactly.
   `rho_gop_per_second` cancels in R.
7. **Internal replicate.** `companion_baseline_plant_off` is a same-settings
   repeat of the primary measurement inside the single authorized run:
   R 0.03216 vs 0.03178, R_null 111.45 vs 108.84. Timing-derived costs are not
   bit-reproducible; seeds, factor base, target stream and yields are.
8. **Inference.** Requested `executor-implementation`; this Claude Code harness
   cannot resolve GPT-5.6-family policy aliases, so `resolved_model_id` is the
   runtime Claude model, `fallback_used: true`, `model_verified: false`.

## Out of scope (honored, control run)

- No edit to `specification*.yaml`, `controls/`, or `amendments/`.
- Single cell only; no 54-cell matrix re-run; no HEUR re-run.
- No commit (`TASK-20260731-045` archives). No hypothesis status changed.
- No adjudication of S1/F1/F2/F3; claim ceiling `toy`.

---

# RUN-DS-001-ctrl-matched-null (BATCH-021 / TASK-20260801-005)

Driver: `experiments/EXP-DS-001/implementation/ds001_ctrl_matched_null.py`
Control: `experiments/EXP-DS-001/controls/CTRL-RT047-MATCHED-NULL.yaml`
Amendment: `PA-DS-001-v2-ctrl-matched-null`
Parent contract: `specification.v2.yaml`, sha256 verified at execution as
`898304bfc9225062e68c5d7977d1490cad95957e856847676ef7ae1423a5636a`.
Run authorization: `TASK-20260801-004` snapshot receipt records
`APPROVAL_DETERMINATION: APPROVED` at commit
`d9e396142776c3f78f0598907d36258808585a28`, reachable from `HEAD`; the
reviewer verdict at `TASK-20260801-003` is `PASS` /
`recommendation_to_task_004: APPROVE`. The driver re-reads the receipt at
startup and refuses to run if the determination is not `APPROVED`.

**This section is an APPEND. Nothing above it was edited.**

## What was added, and what was not touched

- `ds001_driver.py` and `ds001_ctrl_unplanted.py` are **unmodified**
  (`shared_backend_module_modified: false`, and the same for the BATCH-020
  driver module). Both are imported.
- `naive_search`, `split_search`, `build_claw_table`, `charge_backend_units`,
  `encode_intermediate`, `claw_key`, `cost_from_wall`, `frozen_D`,
  `null_naive_search` and `null_split_search` run **unchanged**; the SHA-256 of
  each function's source text is recorded in
  `raw-result.json:algorithm_invariance.search_kernels_source_sha256`.

## How the object was swapped without touching search logic

`AdditiveGroupZN` exposes exactly the two methods the frozen kernels call on
the object — `.add` and `.negate`. A group element is a 1-tuple `(g,)` for a
nonzero residue and `None` for the identity residue 0, so `pt[0]` supplies the
residue where a curve supplies an x-coordinate, and the kernels'
`if s is None: N = 0` branches and `rem in S` membership tests behave exactly as
on the curve. No kernel was parameterized, subclassed, monkeypatched or copied.

## PROTOCOL DEVIATION PD-1 — the harvest wrapper is a copy

`harvest()` in the new driver is a copy of
`ds001_ctrl_unplanted.harvest_real` with instrumentation added. The complete
unified diff is computed at runtime by `difflib` and archived verbatim in
`raw-result.json:algorithm_invariance.harvest_wrapper_diff`. It is declared here
rather than absorbed silently, per
`CTRL-RT047-MATCHED-NULL.algorithm_invariance.binding`.

Why it was necessary: the control's own `required_per_arm_fields` mandates
`n_enum`, `per_arm_capped_attempt_count` and `peak_rss_bytes` **for every arm**,
and the reviewer additionally recommended `claw_table_build_count`.
`harvest_real` emits none of these, so the contract cannot be satisfied by
calling it unmodified.

What the copy adds: accumulation of `ar.n_enumerations`; a capped-attempt
counter and a separate arm-budget-truncated counter; per-arm RSS sampling;
`claw_table_build_count`; a `backend_object` label; and a `cert_fn` parameter so
each object supplies its own certificate constructor.

What the copy does **not** change: the search calls, the deadline arithmetic
(`min(arm_deadline, seg0 + PER_TARGET_CAP_SECONDS)`), the charging, the
stopping rule, the `for/else` stop-reason logic, the overhead accounting, and —
critically — the amortization structure: the claw table is built **once**,
before the target loop, exactly as in `harvest_real`.

The **same** wrapper serves all four matched-null and real arms, so no arm is
advantaged by the instrumentation. `harvest_legacy_null` is the corresponding
instrumented copy of `harvest_null` and serves both legacy arms.

## Amortization parity (the RT047-B2 / legacy-null defect)

- `matched_null_split`: `claw_table_build_count = 1`,
  `table_build_reported_wall_seconds = 0.009157 s`,
  `peak_claw_table_entries = 8256`.
- `real_split_remeasure`: `claw_table_build_count = 1`,
  `table_build_reported_wall_seconds = 0.010870 s`,
  `peak_claw_table_entries = 8256`.
- Both naive arms record `0` and `0.0` rather than `null`.
- `legacy_null_split`: the table is rebuilt **inside every attempt** by the
  frozen `ds001_driver.null_split_search`, so its build time is folded into the
  per-attempt segment and cannot be separated without editing that kernel. It is
  recorded as `table_build_reported_wall_seconds: 0.0` with
  `table_build_measurable: false`, an explanatory `table_build_note`, and
  `claw_table_build_count = 269` (one per attempt). The asymmetry is reported,
  not repaired.

The BATCH-020 admissibility failure — both fields recorded as `null` — does not
recur: every arm carries both fields as numbers.

## Declared parameter

`PER_TARGET_CAP_SECONDS = 5.0` appears in `manifest.json`, `raw-result.json`
and `summary.json`, with `per_arm_capped_attempt_count` for all six arms. All
six are `0`. The largest single-attempt per-relation wall observed was
`0.10789 s` on `real_naive_remeasure`, about 46x under the cap.

## Live plant

None. `plant_divisor = 1.0` on every arm; `plant_applied: false`;
`synthetic_known_answer_used: false`. `CTRL-RT025-PLANT-LIVE` remains
undischarged.

## Certificates

Every claimed relation on every arm carries a certificate, re-verified by a
verifier path independent of the solver:

- matched-null arms — `independent_verify_additive`, plain Python integer
  arithmetic mod N rebuilt from the certificate alone (arity, range,
  factor-base membership, sum equality);
- real arms — `ds001_ctrl_unplanted.independent_verify_decomposition`, which
  rebuilds the curve from the certificate;
- legacy null arms — `independent_verify_legacy_null`, which re-derives the
  blake2b acceptance predicate **inline** rather than calling
  `ds001_driver.null_full_hit`.

Result: 200/200 on all six arms, 1200/1200 overall.

## Notes, deviations and unexpected observations

1. **PD-1** above.
2. **PD-2 — mechanics smoke test before the authoritative run.** A single
   smoke test was executed at `--relations 5 --real-targets 60` writing **only**
   into the session scratchpad; it produced no run-package artifact and no
   number in this package. It was run to validate wiring, not to select a
   result. Disclosed rather than omitted. Exactly one authoritative execution
   was then performed (`maximum_runs: 1`), and it is the one recorded.
3. **Memory cap not applied.** `resource.setrlimit` raised
   `ValueError: current limit exceeds maximum limit` for `RLIMIT_AS`,
   `RLIMIT_DATA` and `RLIMIT_RSS` on this macOS host. The 8 GB cap was
   therefore requested but **not enforced**; the errors are recorded in
   `budget.memory_cap_errors` and `environment.json`. This is identical to the
   BATCH-020 host behaviour and is not new. Observed peak RSS was 70.4 MB
   against an 8 GB allowance, so the unenforced cap did not bind in practice.
4. **AUXILIARY POST-RUN OBSERVATION (not a run-package number).** Rebuilding
   the claw table for both objects outside the run gives identical entry counts
   (8256 = C(129,2) on 128 signed elements) but different **distinct key**
   counts: 4079 on the curve versus 8159 on the additive object. Cause: a curve
   point and its negation share an x-coordinate, so `encode_intermediate` maps
   `P` and `-P` to the same claw key, whereas residues `g` and `N-g` are
   distinct. This is an inherent consequence of removing the curve, and the
   control prescribes exactly the encoding used (element = residue, join =
   equality of residues). Recorded because it is a real asymmetry between the
   two objects that the "matched" label does not by itself cover; the Executor
   draws no conclusion from it.
5. **No object-cost-parity measurement** was performed — the per-operation cost
   of modular addition versus curve addition on this host was not measured. It
   is out of this run's scope and is named in the reviewer's DEF-4 as a
   condition on certain readings.
6. **Bootstrap CI**: only the current (overhead-unresampled) estimator was
   computed. RT047-M1's advisory is carried verbatim in the artifacts; an
   overhead-resampled variant was not constructed because that would introduce
   new statistics and the control forbids new mathematics.
7. **`rho_gop_per_second`** comes from one CTRL-RHO capture on the curve
   instance and is reused for every arm including the matched-null arms. It
   cancels in every ratio. It is not a calibration of the additive object.
8. **Inference.** Requested `executor-implementation`; this Claude Code harness
   cannot resolve GPT-5.6-family policy aliases, so `resolved_model_id` is the
   runtime Claude model, `fallback_used: true`, `model_verified: false`.

## Out of scope (honored)

- No edit to `specification*.yaml`, `controls/`, `amendments/`,
  `ds001_driver.py`, `ds001_ctrl_unplanted.py`, or any BATCH-020 artifact.
- Single cell only; no B sweep; no 54-cell matrix; no HEUR re-run; no v1.
- No commit (`TASK-20260801-006` archives). No hypothesis status changed.
- **No disposition stated.** This run is deliberately NOT classified against
  the frozen D-1..D-5 map; that is `TASK-20260801-009`'s exclusive job.
