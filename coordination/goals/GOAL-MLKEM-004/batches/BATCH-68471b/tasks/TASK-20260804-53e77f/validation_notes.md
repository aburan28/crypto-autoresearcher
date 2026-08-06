# Validation Notes — TASK-20260804-53e77f

**Producer task**: TASK-20260804-52cc2b  
**Snapshot commit**: `a54fe74d94e796d4cb8d1d5fe90a48a768425e78`  
**Validated at**: 2026-08-04  
**Verdict**: **ACCEPT**

---

## Session context

This is an independent validator session. The artifact reviewed is the
output of a 150-run bgj1_sieve variance measurement on a fixed LWE
instance (m=35, n=25, q=127) with independently randomized Siever seeds.
The experiment asks whether the empirical variance of T_N across 150 runs
is consistent with the independence prediction N₀ × Var[s_i].

---

## CHK-1: Hash verification

All 5 artifacts were verified against `TASK-20260804-acb3aa/snapshot_receipt.json`
using both the working-tree SHA256 and the git-blob SHA256 at the snapshot commit:

| File | Receipt SHA256 | Working-tree ✓ | Git-blob ✓ |
|------|---------------|---------------|-----------|
| rebuild_transcript.txt | 7bd97307... | ✓ | ✓ |
| receipt.json | 42cd9f04... | ✓ | ✓ |
| variance_results.json | 57d39474... | ✓ | ✓ |
| report.md | 21b9d3bf... | ✓ | ✓ |
| variance_test_b3.py | 43b46ccb... | ✓ | ✓ |

The snapshot commit:
- Is reachable from HEAD ✓
- Has parent `45b9b5fd` matching `snapshot_receipt.parent_sha` ✓
- Changes exactly the 5 declared artifacts — no scope expansion ✓

---

## CHK-2: Arithmetic re-derivation

All statistics were recomputed independently in Python from the raw `TN_values`
array (n=150). All values match to floating-point precision (< 1e-9 absolute error):

| Quantity | Reported | Recomputed | Match |
|----------|----------|-----------|-------|
| empirical_var_TN (ddof=1) | 8492.309645148742 | 8492.309645148742 | ✓ |
| independence_predicted_var | 6102.657463538211 | 6102.657463538211 | ✓ |
| variance_ratio | 1.3915756694338621 | 1.391575669433862 | ✓ |
| chi2_stat | 207.34477474564545 | 207.344774745645 | ✓ |
| p_value | 0.001122555172757167 | 0.001122555172757 | ✓ |
| CI_lower (ratio) | 1.1226822967504917 | 1.1226822968 | ✓ |
| CI_upper (ratio) | 1.770694675325302 | 1.7706946753 | ✓ |

Additional internal consistency checks passed:
- All 150 `TN_values` entries match corresponding `run_records[i].T_N` exactly
- All 150 `run_records` have `valid: true`
- All 150 `run_records` have `N_vectors: 17919`
- All 150 siever seeds in `run_records` match `parameters.siever_seeds`
- Siever seed expression `numpy.random.default_rng(20260804001).integers(0, 2**32, size=150)`
  reproduces the stored seed list (first 5 and last seed confirmed)

---

## CHK-3: Scope

- `states_a_finding: false` confirmed in variance_results.json, receipt.json, and report.md
- `compared_against_matzov_nf: false` confirmed in all three files
- The only occurrence of "matzov" in variance_results.json is the key name
  `"compared_against_matzov_nf": false` — no substantive MATZOV/Nf reference
- No "Nf", "cost_model", "cost-model" terms appear in variance_results.json
- report.md explicitly states: "OUTPUTS ONLY observations. States no finding.
  No comparison against MATZOV.Nf."
- rule12_status correctly states UNMET and UNWAIVED (no finding triggers Rule 12)

---

## CHK-4: Platform and run count

- Platform confirmed Linux x86_64 from three independent sources:
  - `variance_results.json` → `"Linux-6.12.76-linuxkit-x86_64-with-glibc2.41"`
  - `receipt.json` → `docker_platform_flag: linux/amd64`, `container_arch: x86_64`
  - `rebuild_transcript.txt` lines 2–3 → `x86_64` and uname output confirming x86_64
- `n_runs_completed: 150` in both variance_results.json and receipt.json
- `n_runs_failed: 0` in receipt.json

---

## CHK-5: within-env Var[s_i] provenance

- `independence_test.single_score_source` = `"within-environment run-0 sieve vectors"`
- The variance_test_b3.py script confirms: `compute_single_score_var_from_run0`
  is called at `i == 0` using the run-0 `coeffs` and `Bused` arrays directly —
  not from any external file
- receipt.json deviation record explicitly documents that this differs from
  batch-2 (which used batch-1 raw_scores.json), and states "This is by design
  for batch-3 per task specification"
- No batch-1 file is read in variance_test_b3.py

---

## Qualifications

**QUAL-1** (informational): The handoff briefing estimated `empirical_var_TN ≈ 7296.8`
but the actual value is 8492.31. The artifact is self-consistent; the briefing
estimate was inaccurate. The artifact takes precedence.

**QUAL-2** (informational): The executor and this validator share the same resolved
model (`amazon-bedrock/us.anthropic.claude-sonnet-4-6`). This is a structural
limitation of single-backend deployment per AGENTS.md.

**QUAL-3** (informational): `model_verified: false` in both the executor receipt
and this validation — adapter doctor has not been run to confirm the backend.

**QUAL-4** (informational): The within-env single_score_var (0.340569) is derived
from a single run's vector set (run-0, seed=1873347320). The independence
prediction denominator is therefore seed-dependent; downstream consumers should
note this when interpreting the ratio and CI.

---

## Overall assessment

The run is an admissible research receipt. The artifact is:
- Fully hash-locked to the committed snapshot
- Arithmetically self-consistent (all statistics independently verified)
- Correctly scoped (no finding stated, no MATZOV comparison)
- Executed on the correct platform (Linux x86_64)
- Complete (150/150 runs, all valid)
- Transparent about methodology (within-env variance baseline, batch context)

The four qualifications are informational and do not affect admissibility.
