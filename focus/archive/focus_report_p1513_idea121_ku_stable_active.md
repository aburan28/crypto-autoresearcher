# Focused Autoresearch Plan

Find a generic ordinary prime-field ECDLP algorithm with independently verified end-to-end time exponent below the Pollard-rho and Shoup generic boundary, without confusing toy correctness, relation validity, or preprocessing advice with a break.

## Critical Experiments

| Rank | ID | Status | Score | Wall h | CPU h | Memory GiB | Max runs |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | `P1513` | active | 62 | 2 | 8 | 8 | 1 |

## Claim Matrix

| Claim | Verdict | Independently verified | Linked experiments |
|---|---|---:|---|
| `CLM-P1509-LOCAL-HASSE-SECTION` | reproduced | true | `ECDLP-IDEA-068` |
| `CLM-P1510-GLOBAL-COMPILER` | reproduced | true | `ECDLP-IDEA-068`, `P1510` |
| `CLM-P1511-FD-JOIN-WIDTH` | not_reproduced | true | `P1511` |
| `CLM-P1511-FACTORIZED-SEMIJOIN` | not_reproduced | true | `P1511` |
| `CLM-P1512-SOURCE-LINEAR-COMPLEX` | not_reproduced | true | `P1512` |
| `CLM-P1513-SHARED-COMMON-NORM` | not_reproduced | true | `P1513` |
| `CLM-ECDLP-RELATION-COLLECTION` | not_attempted | false | `P1510`, `P1511`, `P1512`, `P1513` |
| `CLM-ECDLP-BLIND-DESCENT` | not_attempted | false | `P1510`, `P1511`, `P1512`, `P1513` |
| `CLM-ECDLP-SUBRHO-END-TO-END` | not_attempted | false | `P1510`, `P1511`, `P1512`, `P1513` |

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

**Observed:** P1510 constructs all 15 global coefficient polynomials with the proved recurrence O(r^2 + r M(r) log r + M(r^2) log r), replays all 900 nonreturn endpoints and 8 return controls, and has an independent 12/12 audit with exact agreement on all real and synthetic vectors.

**Scope deviations:**
- The exact fixtures are generated ordinary prime-field curves and deterministic synthetic factor systems, not cryptographic-scale relation campaigns.
- The compiler emits a complete quadratic endpoint object for one target; it does not filter relation incidences across enough targets for full rank.

### CLM-P1511-FD-JOIN-WIDTH

**Statement:** Functional dependencies and degree-aware worst-case-optimal join planning alone provide a source-complete per-target five-term relation query with exponent below 3/2 in r.

**Scope:** The exact serial P1511 transition schema with oriented factor sources, public target labels, complete provenance, and the frozen P1490/P1491/P1505/P1510 evidence family.

**Target:** A closed-set or degree-bound theorem plus implicit iterators that filters complete A2/A3 incidence before quadratic pair or cubic triple materialization.

**Observed:** The source-labelled transition query has a valid acyclic join tree once its relations are supplied, but the functional dependencies determine only intermediate points after source choices. Current exact input generation is Theta(r^2) per target or Theta(r^3) over the relation campaign, and no sub-r^1.5 implicit iterator is derived.

**Scope deviations:**
- This rejects the current FD-width/join-planning mechanism only; it is not an unconditional lower bound against factorized algebraic semijoins or other ECDLP representations.

### CLM-P1511-FACTORIZED-SEMIJOIN

**Statement:** P1510-style product circuits for batched A2 and partitioned A3 supports admit source-complete common-factor extraction below r^(5/2) total work.

**Scope:** The exact P1510 multiplicative product grammar plus favorable planted linear-leaf systems at r in {4,6,8,12,16,24,32}, with complete target and five-factor provenance.

**Target:** A factorized gcd, subresultant, or Hasse semijoin whose input circuit, common-factor output, and source inverse all remain below rho.

**Observed:** Every planted common factor and five-factor source row is recovered exactly, but each side of the declared P1510 grammar has r^3 provenance leaves and degree r^3 before gcd. The leaf-count/rho ratio is sqrt(r), reaching 5.657 at r=32; the independent audit passes 10/10 and rejects six mutations.

**Scope deviations:**
- This closes the declared per-target P1510 product grammar, dense batch gcd, and direct product/remainder-tree repackagings; it is not a lower bound against a new target-uniform representation built before leaf emission.

### CLM-P1512-SOURCE-LINEAR-COMPLEX

**Statement:** A target-uniform source-labelled linear Chow/Tate or exterior-syzygy complex can be constructed before P1510 leaf emission with sub-rho payload and kernel atoms in bijection with exact five-factor sources.

**Scope:** The universal signed five-factor elliptic relation incidence, including repeated, vertical, infinity, nonreduced, and blind-target fibers.

**Target:** One explicit target-independent complex with proved exactness, source inverse, and complete construction, specialization, kernel, rank, and state exponents below 5/2 in r.

**Observed:** The canonical unordered signed five-source cycle has length binomial(2r+4,5). For an m by m scalar-linear matrix on a plane cubic, local Smith form gives ord_R(det M)>=nu_R while the global determinant divisor has degree 3m. Hence m>=ceil(binomial(2r+4,5)/3)=Omega(r^5), already above rho. The producer and independent audit each pass 12/12 and preserve nonlinear target-specialized circuits as untested.

**Scope deviations:**
- This closes independent scalar-linear kernel/cokernel atomizers and standard determinant-of-cohomology realizations of the complete labelled cycle; it is not a lower bound against target-specialized nonlinear circuits that emit only common fibers.

### CLM-P1513-SHARED-COMMON-NORM

**Statement:** One shared r^2-leaf bivariate P1510 circuit supports source-complete common-factor extraction between its target and factor-start norms below r^(5/2) total work without expanding either degree-r^3 norm.

**Scope:** The exact symbolic P1510 circuit H(U,W), degree-r public target and factor-start selector polynomials, complete marker provenance, and all exceptional elliptic addition fibers.

**Target:** An explicit common-norm recurrence returning every common endpoint plus target, start, and four transition-source labels with complete base-field work and state exponents below 5/2.

**Observed:** The shared identities are exact and favorable controls have r^2 leaves, degree-r^3 norms, exactly r common roots, and complete source rows. Independent audits close specialization, explicit norms, dense fiber products, fixed-point truncated resultants, 2026 algebraic relation-matrix modular composition, classical intrinsic-degree geometric resolution, and generic straight-line GCD/factorization in their declared models. No direct KU-compatible circuit reduction or source-jet recurrence has been derived.

**Scope deviations:**
- The negative is scoped to the tested standard, intrinsic-degree, and generic-SLP routes. It is not an unconditional lower bound against arithmetic circuits or a specialized output-sensitive common-factor algorithm.

**Blockers:**
- No direct reduction to a bounded number of degree-r^2 Kedlaya-Umans-compatible operations is frozen.
- Complete target/start/source Hasse jets have not been derived without degree-r^3 norm access or equivalent source splitting.

### CLM-ECDLP-RELATION-COLLECTION

**Statement:** A compiled reporter supplies enough independently verified factor-base relations with complete source rows below the generic rho work boundary.

**Scope:** Generic ordinary prime-field ECDLP, including all relation-generation and verification costs.

**Target:** Full-rank relation collection with public source replay and asymptotic plus measured sub-rho accounting.

**Observed:** P1510 removes the prior cubic all-endpoint source-opening path for one two-step target. P1511 closes FD-aware joining and direct product-circuit semijoins; P1512 closes universal scalar-linear source atomizers. P1513 preserves one shared symbolic r^2-leaf circuit, but independent route screens leave only an unproved direct KU-compatible common-norm reduction. No sparse full-rank relation campaign has run.

**Blockers:**
- A complete A2/A3 candidate supply and source intersection below r^(5/2) total work is not derived.
- Factor-log-plus-challenge rank from the P1510 mechanism has not been measured on a candidate path.
- A source-complete shared common-norm recurrence below r^(5/2) is not derived.

### CLM-ECDLP-BLIND-DESCENT

**Statement:** The same public mechanism performs blind target descent without hidden source labels or target-selected advice.

**Scope:** Fresh held-out ordinary prime-field targets after all construction choices are frozen.

**Target:** Complete independently verified target recovery with every online and amortized cost charged.

**Observed:** No blind descent has been attempted from the P1510-P1513 mechanism.

**Blockers:**
- Sparse full-rank relation collection is not established.

### CLM-ECDLP-SUBRHO-END-TO-END

**Statement:** The complete generic ordinary prime-field ECDLP algorithm has independently verified end-to-end time below Pollard rho and the Shoup generic boundary.

**Scope:** One-shot and amortized attacks with preprocessing, relation collection, linear algebra, target descent, verification, memory, and unsuccessful trials all charged.

**Target:** A proved and measured exponent below one half with complete public transcripts and independent verification.

**Observed:** P1510 is an independently verified exact global compiler for one quadratic endpoint surface. P1511-P1513 have closed several consuming routes but have not produced relation collection, factor-log rank, blind descent, or end-to-end sub-rho accounting.

**Blockers:**
- Sparse relation collection, factor-log linear algebra, blind descent, and complete complexity accounting remain open.

## Run Table

| Run | Experiment | Status | Depends on | Failure reason |
|---|---|---|---|---|
| `RUN-P1509-PRODUCER` | `ECDLP-IDEA-068` | completed | - | - |
| `RUN-P1509-AUDIT` | `ECDLP-IDEA-068` | completed | `RUN-P1509-PRODUCER` | - |
| `RUN-P1510-COMPILER-PREFLIGHT` | `P1510` | completed | `RUN-P1509-AUDIT` | - |
| `RUN-P1510-COMPILER-AUDIT` | `P1510` | completed | `RUN-P1510-COMPILER-PREFLIGHT` | - |
| `RUN-P1511-SPARSE-INCIDENCE-DERIVATION` | `P1511` | completed | `RUN-P1510-COMPILER-AUDIT` | - |
| `RUN-P1511-FD-WIDTH-AUDIT` | `P1511` | completed | `RUN-P1511-SPARSE-INCIDENCE-DERIVATION` | - |
| `RUN-P1511-FACTORIZED-SEMIJOIN-DERIVATION` | `P1511` | completed | `RUN-P1511-FD-WIDTH-AUDIT` | - |
| `RUN-P1511-FACTORIZED-SEMIJOIN-AUDIT` | `P1511` | completed | `RUN-P1511-FACTORIZED-SEMIJOIN-DERIVATION` | - |
| `RUN-P1512-LINEAR-CHOW-THEOREM` | `P1512` | completed | `RUN-P1511-FACTORIZED-SEMIJOIN-AUDIT` | - |
| `RUN-P1512-LINEAR-CHOW-AUDIT` | `P1512` | completed | `RUN-P1512-LINEAR-CHOW-THEOREM` | - |
| `RUN-P1513-SHARED-COMMON-NORM-STANDARD-ROUTE-SCREEN` | `P1513` | completed | `RUN-P1512-LINEAR-CHOW-AUDIT` | - |
| `RUN-P1513-SHARED-COMMON-NORM-STANDARD-ROUTE-AUDIT` | `P1513` | completed | `RUN-P1513-SHARED-COMMON-NORM-STANDARD-ROUTE-SCREEN` | - |
| `RUN-P1513-IDEA121-KU-ROUTE-SCREEN` | `P1513` | completed | `RUN-P1513-SHARED-COMMON-NORM-STANDARD-ROUTE-AUDIT` | - |
| `RUN-P1513-IDEA121-KU-ROUTE-AUDIT` | `P1513` | completed | `RUN-P1513-IDEA121-KU-ROUTE-SCREEN` | - |
| `RUN-P1513-IDEA121-FINAL-CORPUS-REPLAY` | `P1513` | completed | `RUN-P1513-IDEA121-KU-ROUTE-AUDIT` | - |
| `RUN-P1513-IDEA121-FINAL-CORPUS-REPLAY-AUDIT` | `P1513` | completed | `RUN-P1513-IDEA121-FINAL-CORPUS-REPLAY` | - |
| `RUN-P1513-DIRECT-KU-CIRCUIT-REDUCTION` | `P1513` | planned | `RUN-P1513-IDEA121-FINAL-CORPUS-REPLAY-AUDIT` | - |

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
- `P1510` -> `P1511` (dependency)
- `P1511` -> `P1512` (dependency)
- `P1512` -> `P1513` (dependency)
- `ECDLP-IDEA-068` -> `P1510` (verified_positive_expansion)
- `P1510` -> `P1511` (verified_positive_expansion)

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

Plan SHA-256: `b197ffd4de9ae253b8ccd26356375c111c12f0f6e9f5b491c70cabfa6107fee0`
