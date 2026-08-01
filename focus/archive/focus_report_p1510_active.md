# Focused Autoresearch Plan

Find a generic ordinary prime-field ECDLP algorithm with independently verified end-to-end time exponent below the Pollard-rho and Shoup generic boundary, without confusing toy correctness, relation validity, or preprocessing advice with a break.

## Critical Experiments

| Rank | ID | Status | Score | Wall h | CPU h | Memory GiB | Max runs |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | `P1510` | active | 62 | 6 | 24 | 16 | 30 |

## Claim Matrix

| Claim | Verdict | Independently verified | Linked experiments |
|---|---|---:|---|
| `CLM-P1509-LOCAL-HASSE-SECTION` | reproduced | true | `ECDLP-IDEA-068` |
| `CLM-P1510-GLOBAL-COMPILER` | open | false | `ECDLP-IDEA-068`, `P1510` |
| `CLM-ECDLP-RELATION-COLLECTION` | not_attempted | false | `P1510` |
| `CLM-ECDLP-BLIND-DESCENT` | not_attempted | false | `P1510` |
| `CLM-ECDLP-SUBRHO-END-TO-END` | not_attempted | false | `P1510` |

### CLM-P1509-LOCAL-HASSE-SECTION

**Statement:** The first nonzero source-marked Hasse form decodes each nonreturn endpoint's exact two-transition selector-factor pair with two public code coordinates per side.

**Scope:** All 908 endpoints in the eight frozen P1490 cells over generated ordinary prime-field curves with r in {4,7,12}, including both nonces and the growing public return control.

**Target:** Exact source-pair recovery, complete multiplicity handling, agreement with P1505 source partitions, and independent mutation-sensitive replay.

**Observed:** All 900 nonreturn endpoints have Hasse order one or two, all source pairs and sign/start branches replay, and the independent audit passes 12/12 checks.

**Scope deviations:**
- P1509 uses one endpoint-wise gcd as a verifier and does not construct the global marked eliminant.
- The fixtures are generated development curves and do not establish cryptographic-scale relation collection or descent.

### CLM-P1510-GLOBAL-COMPILER

**Statement:** The degree-at-most-two marked resultant can be constructed globally in O(r^2 polylog r) work and O(r^2) state without endpoint roots, per-endpoint gcds, or source tables.

**Scope:** The exact 15-component truncated marker ring on P1490 fixtures plus frozen increasing synthetic sizes.

**Target:** A source-blind global compiler whose coefficient polynomials agree exactly with every P1509 local leading form and whose full charged complexity is near quadratic.

**Observed:** P1509 proves only the local identity and an O(r^2) coefficient-slot bound; no compliant global construction has run.

**Blockers:**
- No exact truncated-resultant construction and operation counter are frozen.
- Generic determinant or per-key opening paths may restore cubic work.

### CLM-ECDLP-RELATION-COLLECTION

**Statement:** A compiled reporter supplies enough independently verified factor-base relations with complete source rows below the generic rho work boundary.

**Scope:** Generic ordinary prime-field ECDLP, including all relation-generation and verification costs.

**Target:** Full-rank relation collection with public source replay and asymptotic plus measured sub-rho accounting.

**Observed:** No relation-collection campaign has been run from the P1509 mechanism.

**Blockers:**
- P1510 global compiler gate is open.

### CLM-ECDLP-BLIND-DESCENT

**Statement:** The same public mechanism performs blind target descent without hidden source labels or target-selected advice.

**Scope:** Fresh held-out ordinary prime-field targets after all construction choices are frozen.

**Target:** Complete independently verified target recovery with every online and amortized cost charged.

**Observed:** No blind descent has been attempted from the P1509 mechanism.

**Blockers:**
- Global compiler and relation collection are not established.

### CLM-ECDLP-SUBRHO-END-TO-END

**Statement:** The complete generic ordinary prime-field ECDLP algorithm has independently verified end-to-end time below Pollard rho and the Shoup generic boundary.

**Scope:** One-shot and amortized attacks with preprocessing, relation collection, linear algebra, target descent, verification, memory, and unsuccessful trials all charged.

**Target:** A proved and measured exponent below one half with complete public transcripts and independent verification.

**Observed:** P1509 is a local exact identity only; no end-to-end algorithm or generic-bound break exists.

**Blockers:**
- Global compilation, relation collection, linear algebra, and blind descent remain open.

## Run Table

| Run | Experiment | Status | Depends on | Failure reason |
|---|---|---|---|---|
| `RUN-P1509-PRODUCER` | `ECDLP-IDEA-068` | completed | - | - |
| `RUN-P1509-AUDIT` | `ECDLP-IDEA-068` | completed | `RUN-P1509-PRODUCER` | - |
| `RUN-P1510-COMPILER-PREFLIGHT` | `P1510` | planned | `RUN-P1509-AUDIT` | - |

## Experiment Dependencies

- `P1499` -> `P1500` (dependency)
- `P1499` -> `P1501` (dependency)
- `ECDLP-IDEA-056` -> `ECDLP-IDEA-059` (dependency)
- `ECDLP-IDEA-059` -> `ECDLP-IDEA-050` (dependency)
- `ECDLP-IDEA-050` -> `ECDLP-IDEA-053` (dependency)
- `ECDLP-IDEA-053` -> `ECDLP-IDEA-052` (dependency)
- `ECDLP-IDEA-052` -> `ECDLP-IDEA-049` (dependency)
- `ECDLP-IDEA-049` -> `ECDLP-IDEA-058` (dependency)
- `ECDLP-IDEA-058` -> `ECDLP-IDEA-068` (dependency)
- `ECDLP-IDEA-068` -> `P1510` (dependency)
- `ECDLP-IDEA-068` -> `P1510` (verified_positive_expansion)

## Corrections

No corrections recorded.

## Gates

- `all_ambiguities_resolved`: true
- `all_selected_dependencies_terminal`: true
- `all_selected_have_resource_estimates`: true
- `candidate_and_run_graphs_acyclic`: true
- `claim_evidence_uses_completed_runs_only`: true
- `corrections_preserve_prior_values`: true
- `failed_cancelled_invalid_runs_are_not_claim_evidence`: true
- `focus_cap_respected`: true
- `positive_expansion_requires_independent_verification`: true
- `reproduced_claims_independently_verified`: true

Plan SHA-256: `158b8c0207cb787b3233019b902cfd76fd281e814a77fbda0b87699ddc55079b`
