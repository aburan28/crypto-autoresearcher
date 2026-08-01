# Focused Autoresearch Plan

Find a generic ordinary prime-field ECDLP algorithm with independently verified end-to-end time exponent below the Pollard-rho and Shoup generic boundary, without confusing toy correctness, relation validity, or preprocessing advice with a break.

## Critical Experiments

| Rank | ID | Status | Score | Wall h | CPU h | Memory GiB | Max runs |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | `P1515` | queued | 59 | 2 | 8 | 8 | 1 |

## Claim Matrix

| Claim | Verdict | Independently verified | Linked experiments |
|---|---|---:|---|
| `CLM-P1509-LOCAL-HASSE-SECTION` | reproduced | true | `ECDLP-IDEA-068` |
| `CLM-P1510-GLOBAL-COMPILER` | reproduced | true | `ECDLP-IDEA-068`, `P1510` |
| `CLM-P1511-FD-JOIN-WIDTH` | not_reproduced | true | `P1511` |
| `CLM-P1511-FACTORIZED-SEMIJOIN` | not_reproduced | true | `P1511` |
| `CLM-P1512-SOURCE-LINEAR-COMPLEX` | not_reproduced | true | `P1512` |
| `CLM-P1513-SHARED-COMMON-NORM` | not_reproduced | true | `P1513` |
| `CLM-P1514-NONLINEAR-APOLAR-FLAT-EXTENSION` | open | false | `P1514` |
| `CLM-P1515-SQUAREFREE-SOURCE-SHELLING` | not_attempted | false | `P1515` |
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

**Observed:** The shared identities are exact and favorable controls have r^2 leaves, degree-r^3 norms, exactly r common roots, and complete source rows. Independent audits close specialization, explicit norms, dense fiber products, fixed-point truncated resultants, 2026 algebraic relation-matrix modular composition, classical intrinsic-degree geometric resolution, generic straight-line GCD/factorization, and the standard KU coefficient-ring, query-triangular, primitive-element, dense-input, and transposed-power-projection embeddings in their declared models. A nominal degree-r^2 KU call over the degree-r selector algebra has r^3 base-field coordinates, or sqrt(r) times rho. A conditional source decoder given the common factor has quadratic dimension, but no new nonlinear output-sensitive circuit locator has been derived.

**Scope deviations:**
- The negative is scoped to the tested standard, intrinsic-degree, generic-SLP, and standard KU representation routes. It is not an unconditional lower bound against arithmetic circuits or a specialized nonlinear output-sensitive common-factor algorithm.

**Blockers:**
- No nonlinear output-sensitive product-circuit common-factor locator outside the screened standard KU representations is frozen.
- The quadratic target/start/source Hasse decoder remains conditional on already knowing the common factor.

### CLM-P1514-NONLINEAR-APOLAR-FLAT-EXTENSION

**Statement:** A compact target-local nonlinear apolar functional can be constructed directly from recursive S3 equations, attain a flat Hankel extension below rho, and invert biconditionally to every accepted signed five-source tuple without reconstructing a P1513 norm or common factor.

**Scope:** The theorem-gated ECDLP-IDEA-133 mechanism on generic ordinary prime-field curves, including exceptional fibers, multiplicities, construction, multiplication spectra, source output, rank, factor logs, and blind descent.

**Target:** An independently auditable compact Lambda_R constructor and source-biconditional multiplication algebra with complete lambda,mu<=0.45 and a proof of independence from P1512 scalar-linear atomization and every P1513 common-norm route.

**Observed:** The immutable producer receipts and append-only static scope correction record reusable B^3 total time/state, streamed B^4=N^0.8 campaign time with B^2 memory, direct B^5 precompute/state versus B^6 rescanning, sufficient-cutoff-only dense Macaulay scope, and nonreduced primary/nilpotent recovery. Multiple verifier revisions were executed outside the authorized workspace and are invalid as current claim evidence. The corrected repository-confined verifier is planned and unrun. Adaptive, sparse, multihomogeneous, and structured moment constructors remain open.

**Scope deviations:**
- The static negative is scoped to supplied-moment decoders miscast as constructors, direct enumerative implementations, the frozen reusable/streamed meet-in-the-middle routes, and the dense Macaulay instantiation at a sufficient cutoff. It is not independently verified current run evidence or a lower bound against adaptive or structured constructors.

**Blockers:**
- No public-input structured nonlinear Lambda_R constructor with per-query B exponent at most 1.25 exists.
- No all-strata proof supplies ann(Lambda_R)=I_R, joint primary and nilpotent source recovery, factor-log calibration, and blind descent below the complete cap.
- The corrected repository-confined scope verifier remains planned and unrun under a retired, review_required, zero-run contract.

### CLM-P1515-SQUAREFREE-SOURCE-SHELLING

**Statement:** A target-independent squarefree degeneration of the labelled five-source relation ideal admits sub-rho accepted-facet navigation and exact deformation lifting to every signed source tuple.

**Scope:** The theorem-gated ECDLP-IDEA-098 mechanism on generic ordinary prime-field curves, including squarefreeness, shellability, degree, facet grammar, source lifting, relation collection, factor logs, blind descent, output, and memory.

**Target:** A target-uniform squarefree initial ideal, source-biconditional facet inverse, accepted-facet navigation theorem, and complete lambda,mu<=0.45 without a tuple-indexed complex or dense Grobner object.

**Observed:** An unreviewed non-run theorem receipt proves that every explicit source-biconditional universal facet deck has work Omega(B^m+N/B^(m-1)), minimized at exponent m/(2m-1)>1/2 and 5/9 for five sources. It also corrects the scope: a fixed target fiber has degree d_R rather than B^m. A second non-run receipt instantiates the surviving navigator gate: explicit 2+3 and offline six-list controls cost at least B^3 over the campaign, while the checked 2026 kSUM-Indexing upper bound has setup exponent at least 4.5 in the five-source instantiation and is not an elliptic lower bound. Only a concrete field-specific recursive-S3 grammar remains open. No P1515 run, squarefree degeneration, grammar, or source lift exists.

**Scope deviations:**
- A squarefree initial ideal, shelling, lifted toy relation, or short monomial-generator list is not evidence that accepted facets can be found or lifted below rho.
- The explicit-facet theorem is not a lower bound against a target-local compressed grammar that constructs neither the universal facet deck nor an equivalent source/output dictionary.
- The checked kSUM-Indexing result is an upper-bound control in a neighboring algebraic setting, not an impossibility theorem or a proved elliptic-group transfer.

**Blockers:**
- No target-uniform squarefree source degeneration is proved for the recursive-S3 relation family.
- No concrete target-independent term order or compressed recursive-S3 facet grammar is proved with setup exponent at most B^2.25, per-target query exponent at most B^1.25, exact all-strata source lifting, and a finite-field coordinate identity separating it from generic sum indexing.

### CLM-ECDLP-RELATION-COLLECTION

**Statement:** A compiled reporter supplies enough independently verified factor-base relations with complete source rows below the generic rho work boundary.

**Scope:** Generic ordinary prime-field ECDLP, including all relation-generation and verification costs.

**Target:** Full-rank relation collection with public source replay and asymptotic plus measured sub-rho accounting.

**Observed:** P1510 removes the prior cubic all-endpoint source-opening path for one two-step target. P1511 closes FD-aware joining and direct product-circuit semijoins; P1512 closes universal scalar-linear source atomizers. P1513 preserves one shared symbolic r^2-leaf circuit, but independent route screens now include all standard KU representations; only a new nonlinear circuit locator remains outside scope. No sparse full-rank relation campaign has run.

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
| `RUN-P1513-DIRECT-KU-CIRCUIT-REDUCTION` | `P1513` | completed | `RUN-P1513-IDEA121-FINAL-CORPUS-REPLAY-AUDIT` | - |
| `RUN-P1513-DIRECT-KU-CIRCUIT-REDUCTION-AUDIT` | `P1513` | completed | `RUN-P1513-DIRECT-KU-CIRCUIT-REDUCTION` | - |
| `RUN-P1514-APOLAR-NONLINEAR-THEOREM` | `P1514` | cancelled | `RUN-P1513-DIRECT-KU-CIRCUIT-REDUCTION-AUDIT` | Superseded before evidence emission by the versioned producer and independent-audit run IDs after the frozen hypothesis changed. |
| `RUN-P1514-APOLAR-MOMENT-CONSTRUCTOR-GATE` | `P1514` | invalid | `RUN-P1513-DIRECT-KU-CIRCUIT-REDUCTION-AUDIT` | The immutable producer receipt is REVISE: it conflates reusable and streamed MITM costs and treats a sufficient Macaulay cutoff as a compulsory minimum. External producer outputs are not current claim evidence. |
| `RUN-P1514-APOLAR-MOMENT-CONSTRUCTOR-GATE-AUDIT` | `P1514` | invalid | `RUN-P1514-APOLAR-MOMENT-CONSTRUCTOR-GATE` | The executed verifier revision read and wrote outside the authorized checkout and certified the producer's two overclaims. Its external outputs are excluded from current evidence. |
| `RUN-P1514-APOLAR-SCOPE-CORRECTION` | `P1514` | invalid | `RUN-P1514-APOLAR-MOMENT-CONSTRUCTOR-GATE-AUDIT` | The append-only static correction is retained, but its associated execution used external contracts, code, state, and notes outside the authorized checkout. The execution is invalid as current evidence. |
| `RUN-P1514-APOLAR-SCOPE-CORRECTION-AUDIT-V1` | `P1514` | invalid | `RUN-P1514-APOLAR-SCOPE-CORRECTION` | All arithmetic and mutation checks passed, but three static checks failed on Markdown line wrapping and exact phrase selection. |
| `RUN-P1514-APOLAR-SCOPE-CORRECTION-AUDIT-V2` | `P1514` | invalid | `RUN-P1514-APOLAR-SCOPE-CORRECTION` | All mathematical, scope, and mutation checks passed, but one static check requested a semantic phrase absent from the immutable receipt. |
| `RUN-P1514-APOLAR-SCOPE-CORRECTION-AUDIT-V3` | `P1514` | invalid | `RUN-P1514-APOLAR-SCOPE-CORRECTION` | The semantic-token revision was executed through external contract and output paths despite the workspace boundary and zero-run lifecycle. Preserve its source, but exclude the run from current claim evidence. |
| `RUN-P1514-APOLAR-SCOPE-CORRECTION-AUDIT-V4-INREPO` | `P1514` | planned | `RUN-P1513-DIRECT-KU-CIRCUIT-REDUCTION-AUDIT` | - |
| `RUN-P1515-SQUAREFREE-SOURCE-GATE` | `P1515` | planned | `RUN-P1514-APOLAR-SCOPE-CORRECTION-AUDIT-V4-INREPO` | - |

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
- `P1513` -> `P1514` (dependency)
- `P1514` -> `P1515` (dependency)
- `ECDLP-IDEA-068` -> `P1510` (verified_positive_expansion)
- `P1510` -> `P1511` (verified_positive_expansion)

## Corrections

### COR-P1514-20260718-CLAIM-VERDICT

- Record: `claim:CLM-P1514-NONLINEAR-APOLAR-FLAT-EXTENSION`
- Field: `verdict`
- Prior: `not_reproduced`
- Corrected: `open`
- Reason: The producer receipts are REVISE and the corrected repository-confined verifier remains unrun, so there is no valid completed run supporting an evidence-bearing verdict.

### COR-P1514-20260718-CLAIM-VERIFICATION

- Record: `claim:CLM-P1514-NONLINEAR-APOLAR-FLAT-EXTENSION`
- Field: `independently_verified`
- Prior: `True`
- Corrected: `False`
- Reason: Every executed P1514 verifier revision used unauthorized external state or output paths; the path-confined canonical verifier is planned and unrun.

### COR-P1514-20260718-PRODUCER-RUN

- Record: `run:RUN-P1514-APOLAR-MOMENT-CONSTRUCTOR-GATE`
- Field: `status`
- Prior: `completed`
- Corrected: `invalid`
- Reason: The immutable producer receipt conflates MITM tradeoffs and treats a sufficient Macaulay cutoff as compulsory.

### COR-P1514-20260718-EXTERNAL-AUDIT-RUN

- Record: `run:RUN-P1514-APOLAR-MOMENT-CONSTRUCTOR-GATE-AUDIT`
- Field: `status`
- Prior: `completed`
- Corrected: `invalid`
- Reason: The executed verifier revision escaped the authorized checkout and certified the producer's overbroad formulas.

### COR-P1514-20260718-SCOPE-CORRECTION-RUN

- Record: `run:RUN-P1514-APOLAR-SCOPE-CORRECTION`
- Field: `status`
- Prior: `completed`
- Corrected: `invalid`
- Reason: The static correction is retained, but its associated execution used external contracts, code, state, and notes outside the workspace boundary.

### COR-P1514-20260718-V3-RUN

- Record: `run:RUN-P1514-APOLAR-SCOPE-CORRECTION-AUDIT-V3`
- Field: `status`
- Prior: `completed`
- Corrected: `invalid`
- Reason: The semantic-token source was executed through external contract and output paths despite the zero-run lifecycle.

### COR-P1514-20260718-CANDIDATE-VERIFICATION

- Record: `candidate:P1514`
- Field: `outcome.independently_verified`
- Prior: `True`
- Corrected: `False`
- Reason: IDEA-133 remains deferred and the only admissible current verifier is planned and unrun.

### COR-P1514-20260718-CANDIDATE-RUN-BUDGET

- Record: `candidate:P1514`
- Field: `resource_estimate.maximum_runs`
- Prior: `1`
- Corrected: `0`
- Reason: The retired review_required IDEA-133 contract permits zero runs; an approved versioned successor is required before execution.

### COR-P1514-20260718-CANDIDATE-NEXT-ACTION

- Record: `candidate:P1514`
- Field: `next_action`
- Prior: `Retain the independently audited scoped negative, require a mechanism-new structured nonlinear moment oracle for any IDEA-133 successor, and advance the semantically distinct IDEA-098 squarefree source-shelling theorem gate.`
- Corrected: `After independent static review and versioned coordinator approval, run the repository-confined canonical verifier without --write; keep IDEA-133 deferred until the missing structured constructor exists.`
- Reason: The prior action relied on an invalid independently-verified state and skipped the zero-run lifecycle gate.

### COR-P1514-20260718-P1515-DEPENDENCY

- Record: `run:RUN-P1515-SQUAREFREE-SOURCE-GATE`
- Field: `depends_on_runs`
- Prior: `['RUN-P1514-APOLAR-SCOPE-CORRECTION-AUDIT-V3']`
- Corrected: `['RUN-P1514-APOLAR-SCOPE-CORRECTION-AUDIT-V4-INREPO']`
- Reason: P1515 must not depend on an externally executed invalid P1514 audit.


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

Plan SHA-256: `974c7b7c42988227accd84849a3d0ff5562a0655cb213672c70bc40230d71b77`
