# Focused Autoresearch Plan

Comprehensive four-track user request, ranked as two-at-a-time toy pilots; design ranking does not approve execution.

## Critical Experiments

| Rank | ID | Status | Score | Wall h | CPU h | Memory GiB | Max runs |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | `EXP-IC-18a59e` | queued | 45 | n/a | n/a | 2 | 1 |
| 2 | `EXP-IC-de9929` | queued | 45 | n/a | n/a | 2 | 1 |

## Attention Contracts

### EXP-IC-18a59e

**Decisive evidence:** Canonical immutable run with actual exact certificate and complete control coverage, followed by independent review on the named joint.

**If inconclusive:** Keep scoped instrument limit or unknown yield, repair only through a new frozen revision/admission; do not widen search automatically.

**Local ambiguity rule:** Canonical lex/seed schedule and explicit inadmissible cells; no adaptive replacement.

**Rerank trigger:** Each completed or failed critical observation before another scientific admission.

**Excluded peripheral work:**
- New curves/parameter enlargement beyond frozen set
- Asymptotic/security/novelty claim
- Free oracle recovery counted as candidate success
### EXP-IC-de9929

**Decisive evidence:** Canonical immutable run with actual exact certificate and complete control coverage, followed by independent review on the named joint.

**If inconclusive:** Keep scoped instrument limit or unknown yield, repair only through a new frozen revision/admission; do not widen search automatically.

**Local ambiguity rule:** Canonical lex/seed schedule and explicit inadmissible cells; no adaptive replacement.

**Rerank trigger:** Each completed or failed critical observation before another scientific admission.

**Excluded peripheral work:**
- New curves/parameter enlargement beyond frozen set
- Asymptotic/security/novelty claim
- Free oracle recovery counted as candidate success

## Optional Stage Estimates

| Experiment | Stage | Wall seconds | CPU h | Memory GiB | Shards | Dominant |
|---|---|---:|---:|---:|---:|---:|
| `EXP-IC-18a59e` | `prepare` | n/a | n/a | 2 | 1 | false |
| `EXP-IC-18a59e` | `execute` | n/a | n/a | 2 | 1 | true |
| `EXP-IC-18a59e` | `evaluate` | n/a | n/a | 2 | 1 | false |
| `EXP-IC-18a59e` | `package` | n/a | n/a | 2 | 1 | false |
| `EXP-IC-de9929` | `prepare` | n/a | n/a | 2 | 1 | false |
| `EXP-IC-de9929` | `execute` | n/a | n/a | 2 | 1 | true |
| `EXP-IC-de9929` | `evaluate` | n/a | n/a | 2 | 1 | false |
| `EXP-IC-de9929` | `package` | n/a | n/a | 2 | 1 | false |

## Claim Matrix

| Claim | Verdict | Independently verified | Linked experiments |
|---|---|---:|---|
| `CLAIM-pairing` | not_attempted | false | `EXP-IC-de9929` |
| `CLAIM-factorbase` | not_attempted | false | `EXP-IC-18a59e` |
| `CLAIM-polynomial` | not_attempted | false | `EXP-IC-74cbb1` |
| `CLAIM-combined` | not_attempted | false | `EXP-IC-ab2c47` |

### CLAIM-pairing

**Statement:** Determine scoped pairing correctness and valid output/zero-yield under frozen controls.

**Scope:** Exact synthetic toy schedule only.

**Target:** Certificate-valid discrimination; no benefit assumed.

**Observed:** Not attempted.

**Blockers:**
- Implementation,ready protocol,published approval and scientific admission pending.

### CLAIM-factorbase

**Statement:** Determine scoped factorbase correctness and valid output/zero-yield under frozen controls.

**Scope:** Exact synthetic toy schedule only.

**Target:** Certificate-valid discrimination; no benefit assumed.

**Observed:** Not attempted.

**Blockers:**
- Implementation,ready protocol,published approval and scientific admission pending.

### CLAIM-polynomial

**Statement:** Determine scoped polynomial correctness and valid output/zero-yield under frozen controls.

**Scope:** Exact synthetic toy schedule only.

**Target:** Certificate-valid discrimination; no benefit assumed.

**Observed:** Not attempted.

**Blockers:**
- Implementation,ready protocol,published approval and scientific admission pending.

### CLAIM-combined

**Statement:** Determine scoped combined correctness and valid output/zero-yield under frozen controls.

**Scope:** Exact synthetic toy schedule only.

**Target:** Certificate-valid discrimination; no benefit assumed.

**Observed:** Not attempted.

**Blockers:**
- Implementation,ready protocol,published approval and scientific admission pending.

## Run Table

| Run | Experiment | Status | Depends on | Failure reason |
|---|---|---|---|---|
| `RUN-IC-a784bc` | `EXP-IC-de9929` | planned | - | - |
| `RUN-IC-ffda66` | `EXP-IC-18a59e` | planned | - | - |
| `RUN-IC-0dacba` | `EXP-IC-74cbb1` | planned | - | - |
| `RUN-IC-c497d3` | `EXP-IC-ab2c47` | planned | `RUN-IC-ffda66`, `RUN-IC-0dacba` | - |

## Experiment Dependencies

- `EXP-IC-de9929` -> `EXP-IC-74cbb1` (dependency)
- `EXP-IC-18a59e` -> `EXP-IC-74cbb1` (dependency)
- `EXP-IC-18a59e` -> `EXP-IC-ab2c47` (dependency)
- `EXP-IC-74cbb1` -> `EXP-IC-ab2c47` (dependency)

## Corrections

No corrections recorded.

## Gates

- `all_ambiguities_resolved`: true
- `all_selected_dependencies_terminal`: true
- `all_selected_have_attention_contracts`: true
- `all_selected_have_resource_estimates`: true
- `candidate_and_run_graphs_acyclic`: true
- `claim_evidence_uses_completed_runs_only`: true
- `corrections_preserve_prior_values`: true
- `failed_cancelled_invalid_runs_are_not_claim_evidence`: true
- `focus_cap_respected`: true
- `positive_expansion_requires_independent_verification`: true
- `reproduced_claims_independently_verified`: true
- `stage_estimates_are_advisory`: true

Plan SHA-256: `f85dd49395354d830babb23d510e1447103e040111e4bb9c16135ebc7d41d678`
