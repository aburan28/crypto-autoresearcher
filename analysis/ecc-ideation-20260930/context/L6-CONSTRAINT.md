# Lane L6-CONSTRAINT context (generated 2026-09-30 from committed ledger state; read-only)


## RQ-ECDLP-f0a7b0  (ledger/questions/RQ-ECDLP-f0a7b0.yaml)

```yaml
research_question:
  id: RQ-ECDLP-f0a7b0
  title: >-
    Can SAT, SMT, model-counting and proof-producing constraint technology change the
    charged cost -- or the certifiability -- of factor-base design, relation finding
    (point decomposition) and the Groebner or algebraic step of prime-field and
    extension-field elliptic-curve index calculus, beyond the binary-field
    point-decomposition solver comparison of RQ-SATIC-1ae57a?
  scope:
    curve_families:
      - ordinary prime-order short-Weierstrass curves over F_p with interval, digit-presented (IDEA-20260830-84cdb7) or structured factor bases
      - binary and low-degree extension-field curves with subspace factor bases after Weil descent, the setting of the frozen source SRC-SATIC-TRIMOSKA-2019
      - shape-matched random Boolean and random F_p polynomial systems as null objects
    field_types: [prime, binary_extension, low_degree_extension]
    bit_sizes:
      - toy instances (p up to ~32 bits; F_{2^n} with n up to ~40 and l in 6..9) for executable falsification only
      - larger parameters only after a toy-scale instrument-validity gate passes
    methods:
      - CNF, CNF-XOR and ANF encodings of decomposition systems; bit-vector and finite-field SMT theories; CDCL(T) with algebraic propagators
      - incremental and assumption-based solving across targets sharing one curve and factor base
      - approximate and projected model counting for decomposition probability
      - proof-producing solving (DRAT, LRAT, FRAT) as certificates of non-decomposability
      - symmetry detection and breaking beyond S_m; cube-and-conquer and lookahead as tests of above-leaf pruning
      - ANF preprocessing (XL and ElimLin style), crossbred and hybrid guess-and-solve, first- and last-fall-degree instrumentation of learned constraints
      - SAT, ILP and MaxSAT search over factor-base choice (subspace, interval, digit base) against a declared hardness proxy
      - Groebner basis (F4 and F5 via Sage and Singular) as the incumbent baseline; matched Pollard rho and BSGS controls before any attack-cost statement
  motivation: >-
    RQ-SATIC-1ae57a (opened 2026-09-04) asks whether an XOR-aware SAT solver replaces the
    Groebner step on the binary-field point-decomposition problem and which structural
    property does the work; its five proposals (IDEA-20260904-3c7a91, IDEA-20260904-7fd218,
    IDEA-20260904-96c4f3, IDEA-20260904-b40e6d, IDEA-20260904-e12b5a) predict a ceiling of
    exactly ml - log2|G| search bits with no above-leaf pruning. On user instruction
    (2026-09-05) the program doubles down on SAT and SMT technology for relation finding,
    factor-base design and Groebner speedups. That is broader than one solver comparison:
    it covers prime fields, where the SATIC question forbids transfer; the stages around the
    decomposition step (factor-base choice, yield measurement, certification, amortisation
    across targets); and the interaction between learned Boolean constraints and low-degree
    ideal membership. A local search of ledger/proposals on 2026-09-05 found no proposal on
    incremental solving, model counting, proof certificates or symmetry detection for these
    systems; that absence is a search result, not novelty evidence.
  decision_target: >-
    For each proposed use of constraint technology, decide with the cheapest discriminating
    test whether it (a) moves a search exponent, falsifying the SATIC ceiling or its
    prime-field analogue, (b) moves a constant or an amortised per-target cost by a measured
    factor, or (c) changes only certifiability or measurement fidelity, which is a legitimate
    tooling deliverable. Any (a) requires the null ladder of IDEA-20260904-b40e6d before
    belief. A negative closes only the tested encoding, solver and parameter cells.
  constraints:
    - Lawful defensive cryptanalysis on public constructions and toy benchmarks only; no live keys or deployed targets.
    - Conflict, decision and leaf counts are primary metrics; wall-clock is secondary and always carries its pinned solver version, commit, hardware and seed.
    - SAT and UNSAT instances are measured and reported separately; a pooled average is a composition artifact.
    - A timeout, memory-limit abort or crash is an infrastructure outcome, never evidence of unsatisfiability or of any mathematical property (AGENTS.md rule 5).
    - Every claimed decomposition carries a certificate (the explicit factor-base points) re-verified against the curve independently of the solver; every claimed non-decomposition carries a checkable proof or is reported as unproved.
    - Shape-matched random systems of identical shape are a mandatory null object before any claim that structure rather than size explains a solving cost (docs/inventor-protocol.md).
    - Magma is unavailable; Sage and Singular Groebner ratios are not comparable to the published Magma ratios and no record may present them as such (notes/satic_solver_environment_20260904.md).
    - No end-to-end ECDLP exponent claim without relation yield, linear algebra, descent and a matched rho baseline, which live in RQ-RELN-001 and RQ-ICEX-001.
    - 'Evidence from these runs is capped at claim_tier: toy until an independent reproduction gate passes.'
  status: active
  owner: coordinator

```


## RQ-SATIC-1ae57a  (ledger/questions/RQ-SATIC-1ae57a.yaml)

```yaml
research_question:
  id: RQ-SATIC-1ae57a
  title: >-
    Can a dedicated XOR-aware SAT solver replace the Grobner-basis step of
    summation-polynomial index calculus, and which structural property of the
    descended system -- not which solver -- is doing the work?
  scope:
    curve_families:
      - ordinary and Koblitz binary elliptic curves over F_{2^n}, prime n first
      - low-degree extension-field curves where a Weil descent is defined
      - matched random Boolean polynomial systems of identical shape as null objects
    field_types: [binary_extension, low_degree_extension]
    bit_sizes:
      - toy instances (l in 6..9, n up to ~40) for executable falsification
      - larger l and n only after a toy-scale instrument-validity gate passes
    methods:
      - Semaev summation polynomials with Weil descent to F_2
      - CNF-XOR modelling of the descended point-decomposition (pdp) system
      - WDSat (DPLL with CNF / XORSET / XORGAUSS modules)
      - CryptoMiniSat, CaDiCaL, Glucose, MiniSat as generic-solver controls
      - Grobner basis (F4/F5, grevlex) as the incumbent baseline
      - custom branching order restricted to the ml core variables
      - symmetry breaking on the unordered m-tuple of factor-base points
      - matched Pollard rho / BSGS controls before any attack-cost statement
  motivation: >-
    Trimoska-Ionica-Dequen (ePrint 2019/313, frozen at SRC-SATIC-TRIMOSKA-2019)
    report that WDSat solves the binary-field pdp up to ~300x faster than Magma's
    F4, and that memory rather than time is the Grobner wall: F4 exceeded 200GB at
    l=8 while WDSat stayed near 17MB. That is a large reported effect on exactly
    the step this program models as C_decomp, and this repository has never run a
    SAT solver against a summation-polynomial system. But the same source contains
    the finding that matters more than the headline: patching a core-variable
    branching order into stock CryptoMiniSat recovered most of the gap by itself,
    and Gaussian elimination -- the feature that supposedly makes XOR solvers
    right for this problem -- measurably HURT. Those two facts together say the
    speedup is a property of the MODEL (ml core variables whose assignment
    propagates everything else, Proposition 1) rather than of any solver brand.
    If that is right it is portable, and it is testable cheaply.
  decision_target: >-
    Decide whether the reported SAT-over-Grobner advantage on the pdp is (a) real
    and reproducible here, (b) attributable to a named structural property that
    transfers to solvers and parameter ranges the source did not test, and (c)
    large enough to survive full charging against matched rho once relation yield
    and linear algebra are added. A negative on (a) or (b) closes only the tested
    cells and is itself a deliverable. Reproducing (a) without isolating (b) is
    explicitly NOT sufficient to advance this question.
  constraints:
    - Lawful defensive cryptanalysis on public and toy curves only; no live keys or deployed targets.
    - >-
      Every number in SRC-SATIC-TRIMOSKA-2019 is reported, not reproduced here. No record
      under this question may cite those timings as measured-in-repo, and no cross-hardware
      speedup ratio may be formed against them.
    - >-
      Solver runtime is hardware-, version- and seed-dependent. Conflict counts and node counts
      are the primary reported metrics; wall-clock is secondary and always carries its pinned
      solver version, commit, hardware and seed.
    - >-
      A timeout, memory-limit abort or crash is an infrastructure outcome, never negative
      mathematical evidence, and never evidence that a system is unsatisfiable (AGENTS.md rule 3).
    - >-
      SAT and UNSAT instances are measured and reported separately. Their cost profiles move in
      opposite directions between SAT solvers and Grobner bases, so any pooled average is a
      composition artifact.
    - >-
      Every claimed decomposition requires a certificate -- the explicit m factor-base points --
      re-verified against the curve independently of the solver that produced it
      (docs/claims-and-verification.md).
    - >-
      Matched random Boolean systems of identical shape are a mandatory null object before any
      claim that structure rather than size explains a solving cost (docs/inventor-protocol.md).
    - >-
      This question concerns the pdp step only. No end-to-end ECDLP exponent claim may be made
      here without relation yield, linear algebra and a matched rho baseline, which live in
      RQ-RELN-001 and RQ-ICEX-001.
    - 'Evidence from these runs is capped at claim_tier: toy until an independent reproduction gate passes.'
  status: active
  owner: coordinator

```


## goal head GOAL-SATIC-c49b77
```
# GOAL-SATIC-c49b77 — head projection from ledger/goals/GOAL-SATIC-c49b77.yaml
# Resume fields only; ad-hoc keys and checkpoint bodies are not shown.

id: GOAL-SATIC-c49b77
status: active
title: SAT correctness and measurement campaign for summation-polynomial systems
current_batch_id: BATCH-1a527c
dispatch_queue_path: coordination/goals/GOAL-SATIC-c49b77/batches/BATCH-1a527c/dispatch_queue.json
next_action: Dispatch a bounded successor that classifies instrument A's parent-sha gap (A-T4, A-T5) as a predicate defect or a verifier defect, without relaxing the frozen detect() formula and without re-scoring the cells. IMP-3's first recheck condition is satisfied; its second remains untouched; IMP-3 still stands. TASK-20260905-e2c12f and TASK-20260905-86ea49 remain blocked. Neither completion criterion is met.
campaign_budget:
  _omitted: +1 earlier keys not shown; goal_head.py show GOAL-SATIC-c49b77 --field campaign_budget
  total_wall_clock_seconds: null
  max_concurrent: 2
completion_criteria:
- An independently reviewed standalone toy-polynomial benchmark package establishes encoding correctness, SAT witness validity and sound UNSAT treatment against matched controls within declared parameters.
- A committed Coordinator decision answers the selected RQ attribution questions within the tested scope, with unresolved prerequisites and extrapolation limits explicit; tooling readiness or design intake alone never satisfies this criterion.
pause_conditions:
- Missing or unverifiable solver/certificate dependencies prevent the exact planned task.
- A frozen protocol, archive binding or required independent review is unavailable or invalid.
- An individual task reaches its wall-clock or memory cap.
latest_verified_commit: bfd34aecb354d62ae5cd69af99efdfacf4476ad0
question_ids:
- RQ-SATIC-1ae57a
active_hypothesis_ids: []
owner: coordinator
updated_at: '2026-09-05'
_ad_hoc_keys_not_shown: 2 undeclared top-level keys on this record (goal_head.py audit GOAL-SATIC-c49b77)

```


## Existing hypotheses in these lanes (id | status | question | title)

- H-SATIC-5ed537 | specified | RQ-SATIC-1ae57a | Stage 0 two-axis factor attribution pdp toggleable ingredient identities — n=3 — before any later stage is authorized 
- H-SATIC-681e8a | specified | RQ-SATIC-1ae57a | Stage 0 four-tier null-ladder identities — four tiers — before any CNF-XOR sat rate is believed 
- H-SATIC-688b3c | specified | RQ-SATIC-1ae57a | Stage 0 subspace-membership identities — l=3 linear test — before any factor-base membership is treated as free 
- H-SATIC-6af9d1 | specified | RQ-SATIC-1ae57a | 
- H-SATIC-6fdb7a | specified | RQ-SATIC-1ae57a | 
- H-SATIC-74fcbd | specified | RQ-SATIC-1ae57a | Stage 0 no-above-leaf identities — m=3 complete enumerator — before any SAT solver is treated as a pruner 
- H-SATIC-9c4874 | specified | RQ-SATIC-1ae57a | 
- H-SATIC-b58495 | specified | RQ-SATIC-1ae57a | 
- H-SATIC-c5ba6f | specified | RQ-SATIC-1ae57a | Stage 0 gaussian elimination inert pdp cnf-xor model identities — n=2 — before any later stage is authorized 
- H-XOR-2c2c85 | proposed | RQ-ECDLP-002 | 
- H-XOR-56cc0a | approved | RQ-ECDLP-002 | 
- H-XOR-YIELD | weakened | RQ-ECDLP-002 | 
- H-XOR-a227dc | weakened | RQ-ECDLP-002 | 
- H-XOR-d1a480 | rejected | RQ-ECDLP-002 | 


## Existing proposals in these lanes (id | status | question | title) -- DO NOT DUPLICATE

- IDEA-20260904-3c7a91 | proposed | RQ-SATIC-1ae57a | The pdp CNF-XOR model admits no above-leaf pruning: the "SAT solver" is a complete enumerator of V^m modulo S_m with a unit-propagation leaf test, so the search exponent 
- IDEA-20260904-7fd218 | proposed | RQ-SATIC-1ae57a | Two-axis factor attribution for the pdp - every toggleable ingredient moves EITHER the leaf count OR the cost per leaf, never both, and the leaf-count budget is exactly l
- IDEA-20260904-96c4f3 | proposed | RQ-SATIC-1ae57a | Charge the pdp honestly - a subspace factor base makes membership a GF(2) linear test, so an (m-1)-fold loop solves the pdp in 2^{(m-1)l}/(m-1)! group operations at poly 
- IDEA-20260904-b40e6d | proposed | RQ-SATIC-1ae57a | A four-tier null ladder for the CNF-XOR pdp model - if a shape-matched random Boolean system with the same ml-variable backdoor costs the same, the reported SAT advantage
- IDEA-20260904-e12b5a | proposed | RQ-SATIC-1ae57a | Gaussian elimination is inert on the pdp CNF-XOR model for a derivable reason - under the block core order NO parity row has a determined variable before depth (m-1)l - a
- IDEA-20260905-24d827 | proposed | RQ-ECDLP-f0a7b0 | The prime-field analogue of the SATIC ceiling - a bit-blasted or Groebner-theory CDCL(T) search on the digit-presented decomposition system visits (1 +- eps) 2^{ms}/m! le
- IDEA-20260905-3993c3 | proposed | RQ-ECDLP-f0a7b0 | Projected model counting for coverage is dominated by loop-sampling by at least the number of hashed SAT calls - each hashed call on the free-target formula is predicted 
- IDEA-20260905-3de445 | proposed | RQ-ECDLP-f0a7b0 | Learned clauses are elements of the elimination ideal - the block-support profile of every clause a CDCL solver derives on the pdp is predicted to be FULL (all m blocks),
- IDEA-20260905-79112a | proposed | RQ-ECDLP-f0a7b0 | Incremental assumption-based solving across targets amortises nothing - with the target's n bits as assumptions every learned clause is predicted to contain assumption li
- IDEA-20260905-a6f98e | proposed | RQ-ECDLP-f0a7b0 | Two certificates of non-decomposability and a proof-size dichotomy - the LRAT refutation of an UNSAT pdp instance has length equal to its leaf count (no compression), whi
- IDEA-20260905-a94b5f | proposed | RQ-ECDLP-f0a7b0 | An automorphism census of the encoded system - graph-automorphism detection on the pdp CNF is predicted to return exactly the S_m block interchange (log2 m! bits) and not
- IDEA-20260906-412391 | proposed | RQ-SATIC-1ae57a | Certified nonlinear-to-XOR consequences before core-variable branching
- IDEA-20260906-9f56ad | proposed | RQ-SATIC-1ae57a | Chordal compilation of Semaev residual fibres into a shared decision graph
- IDEA-20260906-bc08f4 | proposed | RQ-SATIC-1ae57a | Target-transported residual caching under certified affine equivalences
- IDEA-20260906-c8f2f6 | proposed | RQ-SATIC-1ae57a | Separator interpolants as a two-free-block finite-field propagator
- IDEA-20260920-18dc28 | proposed | RQ-SATIC-1ae57a | Combined arm -- WDSat symmetry breaking plus 2/4-torsion symmetrization plus coset-typed factor bases on binary curves
- IDEA-20260926-b11cb1 | proposed | RQ-SATIC-1ae57a | GAUSSIAN ELIMINATION IN SAT HAS A SOLVER-FREE CEILING, THE IDEAL-XG LAW: linearising the restricted descended system at every node closes the last block of the direct S_{