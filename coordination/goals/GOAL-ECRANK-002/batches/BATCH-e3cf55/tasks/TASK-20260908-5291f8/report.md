# TASK-20260908-5291f8 — EXP-ECRANK-73275e v2 replication round (R9–R15)

Executor run record for GOAL-ECRANK-002 / BATCH-e3cf55.
Observations only; no interpretation of significance, no interpretation branch
selected (CONV-RESOLVED / TENSION-REAL / MIXED), no conclusion about HEUR-1, no
finding label, no status change. Mapping the recorded facts to the frozen
success / falsification criteria is Coordinator work under /review-evidence.

* Frozen protocol: `experiments/EXP-ECRANK-73275e/amendments/v2_replication_protocol.yaml`
  (sha256 `6f61031861c97da69eac11b947fb7f51e0cf522e3676d3820a5411d8933f847d`),
  approved by `DEC-20260908-614199`; on top of the untouched v1 frozen contract
  `specification.yaml` (sha256 `ae6d170af4fe2e6ffb8f136304f4735b1461c7541f68119a5322888116483c8e`).
* Environment: Python 3.12.8 (pyenv), macOS 26.6 (Darwin 25.6.0, arm64),
  machine Adams-MacBook-Pro.local. Stdlib-only pipeline; no PARI, no network,
  0 descent calls, 0 `ellrank` calls.
* Requested inference policy: `executor-implementation`; model that answered:
  `vllm/qwen3.8-27b` (backend `opencode_native`, `model_verified: false`,
  `fallback_used: true` — native OpenCode session acting as Executor;
  `orchestration.adapter doctor` unconfigured in this session). Bedrock guard
  checked (rule 16): resolved provider contains no `bedrock`.
* Budget: 7200 s wall cap per run; counted-ops cap 1.0e8 (R14: 2.0e9); attempt
  ceiling 12. No cap was hit in any run.

---

## 1. Headline measurements (quoted from named run artifacts)

| run | slot | seed | status | counted ops | found | key observation |
|---|---|---|---|---|---|---|
| R9 | known-false d=(1..1) control (IV-1R n=6 + IV-1C ladder n=8) | 760912 | completed | 830,273 | 0 (n=6) | IV-1R PASS; IV-1C CERTIFIER_LIMITED |
| R10 | planted ELLIPTIC n=6 detection (IV-3R) | 760908 | completed | 2,702,484 | 9/9 recovered | detection 9/9; exponent gate + per-decade calibration fail (recorded) |
| R11 | planted n=8 control, R7 family | 760914 | completed | 930,367 | 9 plants | all deg s=3; ladder applied |
| R12 | construct-n6 fresh-seed replication + N2R | 760906 | completed | 9,447,724 | 33 | N_6(10^4)=33; N2R tables both conventions |
| R13 | determinism replay of R12 (IV-2R) | 760906 | completed | 9,447,724 | 33 | bit-for-bit identical (list, counts, ops) |
| R14 | construct-n8 rescoped (N3R, cap 2.0e9) | 760910 | completed | 1,503,696,145 | 0 | completed in-cap; found=0, feasible=0, near_miss=0 |
| R15 | null object re-run (IV-4R + RD-1) | 760916 | completed | 37,663 | 0 | IV-4R PASS (0 solutions, infeasibility flag raised) |

**Control-admission gate: PROCEED.** R9 IV-1R PASS and R15 IV-4R PASS, so the
readings R12/R13/R14 were authorized. R10 detection is 9/9, so the R12 n=6
counts upgrade from LOWER BOUNDS to MEASURED counts at the tested scope (the
amendment's IV-3R upgrade clause).

---

## 2. The control runs, precisely

### R9 — known-false d=(1..1) control (IV-1R + IV-1C)
- IV-1R (n=6): all 8 tuples rejected `degenerate_deg_s_2`; all x^2
  coefficients nonzero (`119629/64, 1421541/64, 17353/4, 225/4, 3969/4,
  1300861/64, 11649/4, 1578325/64`); certified n=6 total = 0. **PASS.**
- IV-1C (n=8 ladder): top-rung (100000) totals `[6,6,7,7,7,7,7,6]` vs the
  closed form 7 → **CERTIFIER_LIMITED** (a graded instrument-boundary outcome,
  not voiding).
- Ladder no-op (recorded, not interpreted): for every n=8 tuple the certified
  total and op cost are identical across the three rungs (1500/10000/100000);
  e.g. b_index 0: `[(1500,6,34095),(10000,6,34095),(100000,6,34095)]`. The
  committed certifier's good-prime list is capped at 60 primes, all below 1500
  for these tuples, so raising `max_prime` adds no good primes.

### R10 — planted ELLIPTIC n=6 detection (IV-3R)
- 9 plants built, all elliptic (deg s=4), all in-box (h_A ≤ 10^4), 9 distinct
  (b-tuple, pattern) pairs, 9 distinct h0 (IV-9).
- (a) DETECTION: 9/9 recovered (ratio 1.0). **PASS.**
- (b) EXPONENT GATE: `all_in_window=False`. Per-plant height ratio
  (h_A/h_B, the documented IC-V2-6 reading) =
  `[10.0, 14.3, 15.09, 18.18, 7.0, 1.667, 1.053, 18.89, 2.636]` vs the frozen
  window `[0.699, 1.301]`; only idx=6 (1.053) is in window.
- (c) PER-DECADE: cumulative `{100:4, 1000:9, 10000:9}`, ratios `[2.25, 1.0]`
  vs window `[5,20]`; `spans_decades=True`.
- Aggregate log-log slope of the planted yield: 0.176.
- Per the amendment, (b)/(c) void ONLY the planted-height calibration reading;
  detection (a) stands and upgrades the R12 counts to MEASURED.

### R11 — planted n=8 control (R7 family)
- 9 plants, all elliptic (deg s=3); ladder applied; top-rung totals
  `[5,7,7,7,7,7,5,6,6]`; not all 7. Ladder no-op across rungs (recorded).

### R15 — null object re-run (IV-4R + RD-1)
- 64 tuples; total solutions = 0; infeasibility flag (`no_real_root`) raised
  for all 64. **IV-4R PASS.**
- RD-1: non-destructive per-b_index proof ledger (64 entries); the b_index-0
  proof is retained (sha256 `816b712487358909c740babf69451026d215bf2b0ea1366fcc9d46aee6f16613`).
  The v1 PD-1 defect (null_proof_first overwritten after b_index 0) is not
  repeated.
- Detail: the d=(1..1) family at n=6 is a conic (deg s=2, no x^5 ellipticity
  condition), so the derived ellipticity quadratic is degenerate (A=B=0) and
  the null family is the "1=0" sentinel (C_null=1): infeasible via
  `no_real_root=True`, not via a negative discriminant (disc=0, so
  `disc_negative=False`).

---

## 3. The readings

### R12 — construct-n6 fresh-seed replication + N2R (seed 760906)
- 10^4 b-tuples, no exhaustion. found=33, feasible=22 (feasibility fraction
  0.0022).
- counts_per_H (convention A, the recorded r_height): `{100:20, 1000:28, 10000:33}`.
- N2R dual-convention reconciliation (verbatim predicates recorded before any
  count):
  - N_per_H convention A: `{100:20, 1000:28, 10000:33}`.
  - N_per_H convention B (solved free coordinate t=r_0): `{100:26, 1000:33, 10000:33}`.
  - out_of_box_B observations: 0. Cross-tabulation: 33 rows.
  - Decade ratios (descriptive frozen tail_checks; reported, never interpreted):
    - convention A: `[1.4, 1.179]` (smallest 1.179, largest 1.4, two-decade 1.65).
    - convention B: `[1.269, 1.0]` (smallest 1.0, largest 1.269, two-decade 1.269).
    - exponent+2 prediction per decade: 100.
- Certificate coverage (IV-8): all 33 verdicts PASS; n_classes distribution
  `{3:33}`; 0 of 33 instances exhibit 4 distinct twist classes.

### R13 — determinism replay of R12 (IV-2R, RD-2)
- instance_list_identical=True; counts_identical=True (RD-2 canonical
  string-keyed sorted comparison); ops_identical=True (9,447,724 = 9,447,724).
- **IV-2R PASS.**

### R14 — construct-n8 rescoped (N3R, cap 2.0e9, seed 760910)
- 10^4 b-tuples, **completed in-cap** (1,503,696,145 < 2.0e9; no wall-clock
  breach; exhaustion=null). found=0, feasible=0, near_miss_total=0.
- counts_per_H (convention A): `{100:0, 1000:0}`; N2R N_per_H A and B both
  `{100:0, 1000:0}`; n_instances=0.
- Box disclosure (IC-732-3, verbatim): the n=8 Bézout enumeration is exhaustive
  on the integer (a,b) coefficient box `[-min(H,20), min(H,20)]^2` with c solved
  exactly; non-integer (a,b) are outside this run's enumerated scope and are not
  claimed empty. Full rational height-H lattice enumeration at n=8 is NOT
  attempted and is recorded as unmeasured scope.
- A completed in-cap zero is reported as a completed zero; the F3_n8 decision
  (which requires a recorded infeasibility pattern) is Coordinator work.

---

## 4. Deviations, anomalies, and infrastructure events — all recorded

1. **R15 attempt 1 (PD-V2-1).** Attempt 1 used a too-strict `iv4r_pass` check
   (required `disc_negative`, which is False for the degenerate null family).
   The underlying observation (total_solutions=0, `no_real_root=True` for all
   64) was valid and satisfies IV-4R. The check was corrected to use
   `no_real_root` and the run re-executed (attempt 2). Attempt 1 is preserved
   under `runs/RUN-ECRANK-73275e-R15-null-v2/attempt-1-iv4r-check-too-strict/`
   per IV-6. No 13th attempt was made (IV-6 ceiling respected).
2. **R9 IV-1C CERTIFIER_LIMITED.** The fixed ladder is a no-op across rungs for
   the tested tuples (committed certifier good-prime cap of 60, all below
   1500); top-rung totals `[6,6,7,7,7,7,7,6]`. Recorded as an
   instrument-boundary observation.
3. **R10 exponent gate (b) and per-decade (c) calibration checks fail**
   (recorded with exact values); detection (a) is 9/9.
4. **R14 completed in-cap with found=0, feasible=0, near_miss_total=0** (a
   completed in-cap zero within the disclosed integer-box convention).
5. **Same-machine replication.** This v2 round executes on the same machine as
   the v1 round (BATCH-a2bf8b); a second independent machine/runtime was
   unavailable. Same-machine replication with fresh seeds tests seed-sensitivity
   and pipeline determinism; it does NOT test machine-dependent behavior.
   Carried verbatim in every run manifest.

---

## 5. Artifacts

```
experiments/EXP-ECRANK-73275e/
  implementation-v2.md                    implementation note (provenance, IC-V2-1..8, deviations)
  execution-report-v2.yaml                observations-only execution report (this round)
  source-v2/                              new v2 code (reuses v1 source/ by import)
    __init__.py  v2_common.py  certify_ladder.py  plant_builder.py
    n2r.py  construct_v2.py  run_v2.py
  runs/RUN-ECRANK-73275e-R9-known-false-v2/          } each: manifest.yaml, command.txt,
  runs/RUN-ECRANK-73275e-R10-planted-elliptic-n6/    } environment.json, stdout.log,
  runs/RUN-ECRANK-73275e-R11-planted-n8/             } stderr.log, raw-result.json
  runs/RUN-ECRANK-73275e-R12-construct-n6-replication/ } (+ checkpoints/)
  runs/RUN-ECRANK-73275e-R13-construct-n6-replay/      } (+ checkpoints/)
  runs/RUN-ECRANK-73275e-R14-construct-n8-rescoped/    } (+ checkpoints/)
  runs/RUN-ECRANK-73275e-R15-null-v2/                  } (+ attempt-1-iv4r-check-too-strict/)
coordination/goals/GOAL-ECRANK-002/batches/BATCH-e3cf55/tasks/TASK-20260908-5291f8/
  report.md                               this file
```

Every run manifest carries the nested run schema (id, experiment_id, status,
code, environment, inputs, result, inference, stdout, stderr, validity,
timing, resources), the inference block (requested policy, backend, resolved
model, model_verified, fallback), and the verbatim same-machine independence
disclosure. `ops_cap_respected: true` in all seven.

Nothing was written outside the declared write scope. No git commit was made.
No v1 artifact was edited.
