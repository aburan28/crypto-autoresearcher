# Lane L1-SSIQ context (generated 2026-09-30 from committed ledger state; read-only)


## RQ-SSIQ-9702af  (ledger/questions/RQ-SSIQ-9702af.yaml)

```yaml
research_question:
  id: RQ-SSIQ-9702af
  title: >-
    Which exponent-carrying factor of the p^{1/3+o(1)} supersingular isogeny
    algorithm can move, and does any admissible movement of it reach
    p^{1/4+o(1)} time over F_{p^2} — or does a method ceiling close the route?
  scope:
    curve_families:
      - supersingular elliptic curves over F_{p^2} (the general OneEnd /
        EndRing / Isogeny setting of eprint 2026/1486, archived in-repo at
        inputs/P13-WESOLOWSKI-2026/paper_fulltext.md)
      - >-
        supersingular elliptic curves defined over the prime field F_p (the
        Delfs-Galbraith subfield locus), IN SCOPE ONLY as the E ≅ E^{(p)}
        degenerate stratum of the same object and as a contested comparison
        baseline (KN-TECH-058 RC4), NEVER as the target problem
    field_types:
      - "F_{p^2}"
      - "F_p"
      - "quaternion algebra B_{p,infinity} (Deuring side)"
    bit_sizes:
      - "asymptotic in p; toy validation at log2(p) in [20, 60]"
      - "cost-model evaluation at log2(p) ~ 250 (SQIsign level I) and ~500 (level V)"
    methods:
      - exponent-budget decomposition of the archived algorithm into its
        separately-quantified factors (structural degree bound, split exponent,
        list cardinality, inverse success probability)
      - method-ceiling audit per docs/inventor-protocol.md section 8
        (KN-TECH-080) applied to each enumerated lever before any expensive work
      - lattice / quaternion-order arguments bounding the minimal degree of
        E -> E^{(p)} from below (Minkowski-type obstructions)
      - restricted-family list constructions with measured
        cardinality-versus-hit-probability tradeoff
      - subfield-descent composition (distance-to-F_p measured by the minimal
        E -> E^{(p)} degree, which is 1 exactly on the F_p locus)
      - toy-scale enumeration and sampling experiments under frozen contracts
        with pre-registered null-object and instrument-fidelity controls
  motivation: >-
    The archived source proves, under Heuristic 1, expected time AND memory
    p^{1/3+o(1)} for OneEnd and (via the reductions it cites, never checked by
    this program) for EndRing and Isogeny. Reading the proof of Theorem 1.1
    (paper_fulltext.md lines 177-218), the exponent 1/3 is not a single
    quantity but a product of separately-sourced factors:
      (F1) Theorem 1.5 of [4]: every supersingular E/F_{p^2} admits an isogeny
           E -> E^{(p)} of degree at most (p/2)^{1/3};
      (F2) a balanced two-way split of a B-smooth degree, giving each side
           degree at most X = B^{1/2}(p/2)^{1/6};
      (F3) list cardinality Psi(X,B) * X^{1+o(1)} = X^{2+o(1)} = p^{1/3+o(1)},
           because there are ~X admissible degrees and ~d cyclic isogenies of
           each degree d;
      (F4) inverse success probability P0^{-1} = u^{u(1+o(1))} = p^{o(1)} at
           B = e^{(1/3)sqrt(log(p/2))}.
    F4 already carries no exponent, so no exponent can be recovered there. A
    p^{1/4+o(1)} algorithm therefore requires a specific, nameable movement in
    F1, in F2+F3 jointly, or in the collision mechanism that F3 feeds. Stating
    which one, and with what numeric target, converts an aspiration into a
    falsifiable research question — and makes it possible to CLOSE routes with
    ceiling arguments rather than to drift.
    The target profile (docs/target-result-profile.md) is exponent-moving
    results on central hard problems, and this is the same problem, the same
    exemplar, and the next exponent below it. The symmetric failure mode named
    by docs/inventor-protocol.md is premature closure: "1/3 was just proved,
    therefore 1/4 is out of reach" is not evidence and is not admissible here.
  decision_target: >-
    For each enumerated lever: whether it is (a) CLOSED by a committed ceiling
    argument or executed falsification test, (b) OPEN with a specified
    falsifiable hypothesis and a designed minimal discriminating experiment, or
    (c) ADVANCED to a mechanism with a charged cost model whose time exponent
    over F_{p^2} is strictly below 1/3. Nothing here decides whether p^{1/4} is
    attainable; it decides which levers survive contact with their own ceilings.
  constraints:
    - >-
      0.25 IS A TARGET, NOT A CLAIM. No record under this question may state,
      imply, or be structured so as to suggest that a p^{1/4} algorithm exists,
      is likely, or is nearly obtained. Claim tiers are governed by
      docs/claims-and-verification.md and no evidence record may assert above
      its tier.
    - >-
      The Delfs-Galbraith Otilde(p^{1/4}) figure is for the F_p-RESTRICTED
      problem, is carried in this corpus at confidence relayed_from_abstract,
      and is CONTESTED ACROSS RETRIEVALS (KN-TECH-058, "What is NOT corrected
      here", RC4). It may not be cited as evidence that exponent 1/4 is
      reachable for the general F_{p^2} problem, and it may not be upgraded
      without the published paper in hand.
    - >-
      Every exponent comparison names its tier: p^{1/2}*(log p)^{O(1)}
      unconditional at polynomial memory, versus p^{1/3+o(1)} time AND memory
      conditional on Heuristic 1, and says where on the van Oorschot-Wiener
      interpolation curve sqrt(N^3/w) the candidate sits. Beating only the
      unconditional tier is not an improvement.
    - >-
      Memory is charged beside time in every estimate. A p^{1/4} time exponent
      obtained at p^{1/4} memory must say so; the archived source names its own
      memory cost as "a serious obstacle for any deployment".
    - >-
      The o(1) in the archived result hides a superpolynomial overhead
      disclosed by its own author. No concrete-parameter conclusion may be
      computed above it, and no candidate's o(1) may be silently assumed
      smaller than the incumbent's.
    - >-
      Heuristics are numbered, stated, and separately validated. A candidate
      resting on a new smoothness, equidistribution, or independence assumption
      inherits the incumbent's obligation, not a waiver of it.
    - >-
      Toy-scale evidence is never presented as crypto-scale, and negative
      evidence closes only the exact tested scope. A lever closed at toy scale
      is closed at toy scale.
    - >-
      Rule 9 applies with force here: a lever may only be deprioritized with a
      recorded ceiling argument or executed control, its budget, its test
      boundary, its remaining uncertainty, and a named successor or revisit
      condition. "Looks saturated" is not a closure.
  status: active
  owner: coordinator

```


## RQ-SSI-001  (ledger/questions/RQ-SSI-001.yaml)

```yaml
research_question:
  id: RQ-SSI-001
  title: >-
    Can an algorithmic mechanism materially improve cryptanalysis of a
    surviving supersingular-isogeny hardness assumption after the SIDH break?
  scope:
    curve_families:
      - supersingular elliptic curves over F_p2
      - supersingular elliptic curves over F_p (CSIDH / oriented)
      - supersingular isogeny graphs (CGL / path-finding)
    field_types:
      - prime fields and quadratic extensions used by supersingular constructions
    bit_sizes:
      - toy and mid-size parameters sufficient for decisive gates
      - published CSIDH / SQIsign / CGL parameter regimes as comparison targets
    methods:
      - endomorphism-ring recovery and Deuring correspondence
      - classical and quantum isogeny path-finding
      - class-group action / hidden-shift attacks (CSIDH)
      - orientation, torsion, and other auxiliary-structure exploitation
      - higher-dimensional / Kani-style embeddings when torsion images are published
      - full-cost classical and quantum cost models
  motivation: >-
    The 2022 SIDH/SIKE break collapsed one supersingular assumption by using
    published torsion-point images. The survivors (CGL path-finding, SQIsign's
    endomorphism-ring foundation, and CSIDH's commutative group action) now
    carry the post-quantum load. The program already records the open hardness
    and cost questions (KN-OPEN-013, KN-OPEN-014, KN-OPEN-015) and an adjacent
    literature spine (KN-LIT-062..079, KN-TECH-024..029). This question asks
    whether a concrete, novelty-screened mechanism can improve a matched
    baseline against one of those surviving problems under fully charged costs.
  decision_target: >-
    Select the cheapest decisive derivation or experiment for any mechanism
    that survives novelty, baseline, auxiliary-structure, and full-cost
    screening against a surviving supersingular hardness assumption.
  constraints:
    - Academic / defensive cryptanalysis only; no operational key recovery against live systems.
    - Distinguish SIDH/SIKE (broken; torsion images published) from survivors that publish no torsion images under a secret isogeny.
    - Do not reuse RQ-ISO-001 / EXP-ISO-001 scope (ordinary-curve Semaev neighbors, not supersingular PQ hardness).
    - All preprocessing, memory, oracle, quantum-query, and verification costs must be charged; toy-only effects are hypothesis-generating only.
    - No claim may exceed the exact problem, parameter regime, oracle model, and cost convention analyzed.
    - Timeouts, crashes, and resource exhaustion are infrastructure outcomes, not cryptanalytic evidence.
  status: active
  owner: coordinator

```


## goal head GOAL-SSIQ-001
```
# GOAL-SSIQ-001 — head projection from ledger/goals/GOAL-SSIQ-001/goal.yaml
# Resume fields only; ad-hoc keys and checkpoint bodies are not shown.

id: GOAL-SSIQ-001
status: active
title: 'Toward p^{1/4}: which exponent-carrying factor of the p^{1/3+o(1)} supersingular isogeny algorithm can move, and what closes the ones that cannot'
current_batch_id: BATCH-014
next_action: 'TASK-20260808-d458a3 HAS RETURNED. Its producer run RUN-SSIQ-a85692-k DEFERRED AT G-0c on the gate''s first evaluation and computed NO delta_E value of any kind (n_sweep_points_attempted/succeeded/failed = 0/0/0). The frozen order [G-0c, G-0, G-0b, G-1, G-2, G-2b, G-3] was evaluated in exactly that order and the six later branches were never reached. The mismatch is on all three compared dimensions: execution host macOS-26.6-arm64-arm-64bit-Mach-O / arm64 / os.cpu_count() 14 against RUN-SSIQ-a85692-h''s archived Linux-6.18.5-fc-v18-x86_64-with-glibc2.39 / cpus_available 4 -- and that archived en … [truncated, 3094 chars total; goal_head.py show GOAL-SSIQ-001 --field next_action]'
campaign_budget:
  _omitted: +6 earlier keys not shown; goal_head.py show GOAL-SSIQ-001 --field campaign_budget
  total_wall_clock_seconds_amendment_20260806_no_ceiling: Uncapped (null, superseding 43200) under the same "No budget constraints" user authorization as maximum_batches above. Per-run wall-clock/CPU/memory budgets remain individually bounded and pre-registered in each experiment's own frozen contract regardless -- this removes only the campaign-level aggregate ceiling, not any single run's own budget discipline.
  max_concurrent: 3
completion_criteria:
- 'An exponent-budget decomposition of the archived p^{1/3+o(1)} algorithm is committed and independently verified against primary text: every exponent-carrying factor F1-F4 (as corrected) re-derived with its line locators, and the p^{1/4} target expressed as explicit numeric conditions on named factors — which factor must move, to what value, for the total to reach 1/4.'
- 'Every enumerated lever carries a committed method-ceiling audit per docs/inventor-protocol.md section 8 (KN-TECH-080): the exact statement that would have to be true, the nearest known obstruction or lower bound, a nearby-object control, and a cheap pre-compute falsification test actually executed — with the audit''s verdict recorded whichever way it falls.'
- At least one surviving lever is advanced to a specified falsifiable hypothesis with a frozen experiment contract, executed bounded runs with pre-registered null-object and instrument-fidelity controls, and independent Validator and Red Team review admitting the package.
- IF a mechanism whose charged time exponent over F_{p^2} is strictly below 1/3 survives that review, it carries a full cost model — time, memory, disclosed o(1) overhead, position on the van Oorschot-Wiener curve, parallelisation, numbered heuristics with validation evidence — a claim-tier-correct evidence record, and a scoped statement of which schemes and parameter sets are affected, inherited unwidened from the source's own scope.
- Coordinator evidence, decision, and any warranted knowledge entry are committed through a verified ledger archive, with every conclusion scoped to the exact objects, parameters, solver and budget actually used.
pause_conditions:
- The eight-batch campaign budget is exhausted without an admissible next lever or next mechanism.
- Every enumerated lever — including any added by producers under the completeness disclaimer — is CLOSED by a committed ceiling argument or executed falsification, and no successor route is identified. Pausing here requires the successor/revisit record of AGENTS.md rule 9, not a bare "closed".
- A definitive infrastructure, authentication, or dependency blocker prevents the next approved task.
- The user requests a pause.
latest_verified_commit: e2102bfedec5bd0c5790bed768d948ca49b98656
question_ids:
- RQ-SSIQ-9702af
active_hypothesis_ids: []
owner: coordinator
updated_at: '2026-08-28'
_ad_hoc_keys_not_shown: 21 undeclared top-level keys on this record (goal_head.py audit GOAL-SSIQ-001)
_checkpoint_shards: 14 shard(s), latest BATCH-014 (ledger/goals/GOAL-SSIQ-001/checkpoints/)

```


## goal head GOAL-SSI-001
```
# GOAL-SSI-001 — head projection from ledger/goals/GOAL-SSI-001/goal.yaml
# Resume fields only; ad-hoc keys and checkpoint bodies are not shown.

id: GOAL-SSI-001
status: active
title: Supersingular-isogeny cryptanalysis after the SIDH break
current_batch_id: BATCH-5e4996
dispatch_queue_path: coordination/goals/GOAL-SSI-001/batches/BATCH-5e4996/dispatch_queue.json
next_action: 'THE SUCCESSOR-RECORD STREAM, RANKED, AND NO MAKE-WORK. BATCH-5e4996 is terminal: the enactment is performed and composed by DEC-20260909-e7a4fe and EV-SSI-d9d1a4 and checkpointed at ledger/goals/GOAL-SSI-001/checkpoints/BATCH-5e4996.yaml; GOAL-SSI-001 stays `active` and no hypothesis, experiment, or goal status moved. WHAT REMAINS, each a ranked candidate and none dispatched without ranking: (1) any decision authorizing runs of EXP-WESOVOW-001 under version 2 - a further, separate Coordinator decision, with clause_4''s raw-output status needing a conforming execution; (2) the successor records … [truncated, 1179 chars total; goal_head.py show GOAL-SSI-001 --field next_action]'
campaign_budget:
  _omitted: +1 earlier keys not shown; goal_head.py show GOAL-SSI-001 --field campaign_budget
  total_wall_clock_seconds: null
  max_concurrent: null
completion_criteria:
- A mechanism is specified with reproducible derivation or implementation evidence and a fully charged attack estimate that materially improves a matched baseline for at least one surviving supersingular hardness assumption at a stated parameter regime.
- Independent red-team (or validator) review verifies novelty, correctness, scope, and the absence of uncharged oracle, torsion-image, preprocessing, memory, or quantum-query costs.
- Coordinator evidence, decision, and any warranted knowledge entry are committed through a verified ledger archive.
pause_conditions:
- A definitive infrastructure, authentication, or dependency blocker prevents the next approved task.
- The user requests a pause.
latest_verified_commit: 7c24aaeff9e0e0298604b74947c7235450b43dd7
question_ids:
- RQ-SSI-001
active_hypothesis_ids: []
owner: coordinator
updated_at: '2026-09-10'
_ad_hoc_keys_not_shown: 47 undeclared top-level keys on this record (goal_head.py audit GOAL-SSI-001)
_checkpoint_shards: 56 shard(s), latest BATCH-dc1424 (ledger/goals/GOAL-SSI-001/checkpoints/)

```


## goal head GOAL-P13-001
```
# GOAL-P13-001 — head projection from ledger/goals/GOAL-P13-001.yaml
# Resume fields only; ad-hoc keys and checkpoint bodies are not shown.

id: GOAL-P13-001
status: closed_at_budget
title: Assess the Wesolowski 2026 p^{1/3+o(1)} supersingular isogeny attack
current_batch_id: BATCH-8e1671
dispatch_queue_path: coordination/goals/GOAL-P13-001/batches/BATCH-8e1671/dispatch_queue.json
next_action: 'GOAL-P13-001 IS CLOSED_AT_BUDGET (DEC-20260810-0875ae). NO FURTHER EXECUTOR BATCH IS AUTHORIZED AGAINST THIS GOAL UNDER THE CURRENT (SPENT) CAMPAIGN BUDGET. The single next action is the RESUME CONDITION, not a dispatch: resume only when (a) NC-3/NC-6, Heuristic 1''s tail validation at the operating point (EXP-P13-NC36/specification.yaml, frozen, not itself repaired or re-approved here), can be executed to a determinate outcome -- pass, fail, or an honestly-reported feasibility verdict, NOT another infrastructure failure -- under a working isogeny-walk-capable execution environment, with an exp … [truncated, 2103 chars total; goal_head.py show GOAL-P13-001 --field next_action]'
campaign_budget:
  _omitted: +6 earlier keys not shown; goal_head.py show GOAL-P13-001 --field campaign_budget
  batches_consumed_correction_20260810: Corrected 3 -> 4 by DEC-20260810-0875ae, counting BATCH-403f13 (the hex-token batch that actually executed the historical "BATCH-004" next_action; see head_correction_20260810 above for why it was missed by earlier shallow current_batch_id reads). No other batch is added or removed from the count.
  batches_remaining: 0
completion_criteria:
- An empirical per-entry cost calibration (NC-2) decides the NIST-I margin with error below the irreproducibility band, and the result survives independent Validator and Red Team review.
- A Coordinator evidence record, decision, and hypothesis-status update are committed through a verified ledger archive.
pause_conditions:
- Heuristic 1 is refuted or proven by external work, making further internal controls moot.
- The empirical calibration cannot be brought below the irreproducibility band within the campaign budget.
- A definitive infrastructure or dependency blocker prevents the next approved task.
latest_verified_commit: 84356221fbb448127245539e944c896a6e97cee5
question_ids:
- H-WESO-001
active_hypothesis_ids:
- H-WESO-001
owner: coordinator
updated_at: '2026-08-10'
_ad_hoc_keys_not_shown: 17 undeclared top-level keys on this record (goal_head.py audit GOAL-P13-001)

```


## Existing hypotheses in these lanes (id | status | question | title)

- H-AUX-4a0506 | specified | RQ-SSI-001 | 
- H-GEN-7a1474 | specified | RQ-SSI-001 | 
- H-P13-001 | None | None | Wesolowski 2026 p^{1/3+o(1)} attack on the supersingular isogeny problem: conditional validity and concrete threat
- H-PEC-189c70 | specified | RQ-SSI-001 | The crossover locus p*(w) is conditioned on the SIGN of this campaign's modelled margin, which BATCH-003 established as robust, rather than on its MAGNITUDE, which BATCH-
- H-SPC-5a6007 | specified | RQ-SSI-001 | 
- H-SPR-71a843 | specified | RQ-SSI-001 | 
- H-SSI-001 | approved | RQ-SSI-001 | 
- H-SSI-04aea1 | specified | RQ-SSI-001 | Stage 0 descent-cocycle obstruction compositional isogeny certificate identities — n=2 — before any later stage is authorized 
- H-SSI-058ee8 | specified | RQ-SSI-001 | Stage 0 planted-orientation instances positive control constructed deuring identities — n=2 — before any later stage is authorized 
- H-SSI-070db8 | specified | RQ-SSI-001 | Stage 0 csidh-collimation-fc0 typed resource-vector gate binary collimation identities — n=2 — before any later stage is authorized 
- H-SSI-0fc4e6 | specified | RQ-SSI-001 | Stage 0 re-randomisation loop purchase known exchange rate identities — n=2 — before any later stage is authorized 
- H-SSI-0ff9b3 | specified | RQ-SSI-001 | Stage 0 memory-crossover identities — two algorithms — before any asymptotic comparison is treated as a crossover 
- H-SSI-22bd38 | specified | RQ-SSI-001 | Stage 0 effective orientation known small-degree endomorphism kn-tech-050 identities — n=2 — before any later stage is authorized 
- H-SSI-2c1f85 | specified | RQ-SSI-001 | Stage 0 measurement work exponent heuristic stated uniformly identities — n=3 — before any later stage is authorized 
- H-SSI-2c7810 | specified | RQ-SSI-001 | Stage 0 memory-exponent identities — one named open memory exponent — before any time exponent below 1/3 is claimed 
- H-SSI-32901e | specified | RQ-SSI-001 | Stage 0 OneEnd-locus identities — one F_p-rational locus — before any CSIDH break is inferred 
- H-SSI-366185 | specified | RQ-SSI-001 | Stage 0 named-avenue identities — one producer-named avenue — before any closed avenue is treated as still open 
- H-SSI-38d10c | specified | RQ-SSI-001 | Stage 0 kn-open-015 asks auxiliary data collapses isogeny identities — n=3 — before any later stage is authorized 
- H-SSI-3b89b3 | specified | RQ-SSI-001 | Stage 0 third-aggregation identities — three structures — before any missing third is treated as exhibited 
- H-SSI-4295dc | proposed | RQ-SSI-001 | Structured-target covering: a streamed smooth-degree codomain list from a random supersingular E hits the radius-r ball around the F_p-rational locus at the rate a unifor
- H-SSI-4f50f1 | specified | RQ-SSI-001 | Stage 0 existence-versus-construction identities — two outcomes — before any tau is constructed 
- H-SSI-512bdc | specified | RQ-SSI-001 | Stage 0 schur-complement norm slicing explicitly supplied quaternion identities — n=4 — before any later stage is authorized 
- H-SSI-5c00c7 | specified | RQ-SSI-001 | Stage 0 kn-open-015 scope fence never research object identities — n=3 — before any later stage is authorized 
- H-SSI-5d6b1d | specified | RQ-SSI-001 | Stage 0 csidh key recovery subset-sum meet-in-the-middle never identities — n=4 — before any later stage is authorized 
- H-SSI-63817e | specified | RQ-SSI-001 | Stage 0 complementary second-moment identities — two moments retained — before any multiplicity is assumed uniform 
- H-SSI-640035 | specified | RQ-SSI-001 | Stage 0 csidh sits frozen source safe list identities — n=3 — before any later stage is authorized 
- H-SSI-6990cc | specified | RQ-SSI-001 | Stage 0 endomorphism-ring problem isogeny linked polynomial reductions identities — n=2 — before any later stage is authorized 
- H-SSI-6c4d29 | specified | RQ-SSI-001 | Stage 0 frozen source affected list omits reference identities — n=3 — before any later stage is authorized 
- H-SSI-6cd92f | specified | RQ-SSI-001 | Stage 0 frobenius-orbit quotient two-stage supersingular path collisions identities — n=2 — before any later stage is authorized 
- H-SSI-7391a3 | specified | RQ-SSI-001 | Stage 0 missing-goal identities — zero CSIDH-quantum goals — before any deferred lane is treated as a goal 
- H-SSI-7fe2bf | approved | RQ-SSI-001 | The Wesolowski/Delfs-Galbraith comparison is decidable as a locus p*(w) where it is undecidable as a scalar margin, and its SIGN is fixed by the memory-charging conventio
- H-SSI-835509 | specified | RQ-SSI-001 | Stage 0 one-sided-detector identities — one detector — before any delta(E) test is treated as an exponent 
- H-SSI-8ff06b | proposed | RQ-SSI-001 | 
- H-SSI-924c53 | specified | RQ-SSI-001 | Stage 0 three-claw identities — three independent claws — before any one claw is treated as End(E) 
- H-SSI-93c139 | specified | RQ-SSI-001 | Stage 0 ball meet-in-the-middle cost exponent a-g times identities — n=2 — before any later stage is authorized 
- H-SSI-ad23a2 | specified | RQ-SSI-001 | Stage 0 csidh class-group action dimension test measure identities — n=2 — before any later stage is authorized 
- H-SSI-b17f73 | proposed | RQ-SSI-001 | 
- H-SSI-bb6bfc | specified | RQ-SSI-001 | Stage 0 disposition-null run goal obligation-ledger protocol structure-free identities — n=2 — before any later stage is authorized 
- H-SSI-bdbb2c | specified | RQ-SSI-001 | Stage 0 second-moment identities — two named moments — before any rare-stratum claim is made 
- H-SSI-bdc41f | proposed | RQ-SSI-001 | 
- H-SSI-c1e29a | specified | RQ-SSI-001 | Stage 0 descent-cocycle obstruction compositional isogeny certificate identities — n=2 — before any later stage is authorized 
- H-SSI-c3aea9 | specified | RQ-SSI-001 | Stage 0 affected-system identities — CGL is one named system — before any p^{1/3} scope is treated as hash-free 
- H-SSI-cd6f34 | proposed | RQ-SSI-001 | 
- H-SSI-d1eb7f | specified | RQ-SSI-001 | Stage 0 algorithm exactly canonical target level structure identities — n=2 — before any later stage is authorized 
- H-SSI-df550b | proposed | RQ-SSI-001 | 
- H-SSI-e52d84 | specified | RQ-SSI-001 | Stage 0 frozen sqisign fiat-shamir transcript model sqi-fs-t0 identities — n=2 — before any later stage is authorized 
- H-SSI-e92d1c | specified | RQ-SSI-001 | Stage 0 cgl affected statement endomorphism collision equal-length identities — n=2 — before any later stage is authorized 
- H-SSI-ea9d21 | specified | RQ-SSI-001 | Stage 0 automorphism-valued holonomy nonbacktracking isogeny cycles identities — n=2 — before any later stage is authorized 
- H-SSIQ-055a36 | proposed | RQ-SSIQ-9702af | The memory lever is ONE object: every rebuild-and-shard scheme is dominated by van Oorschot-Wiener by exactly the shard count S, so memory below p^{1/3} at time p^{1/3} r
- H-SSIQ-137200 | analyzed | RQ-SSIQ-9702af | 
- H-SSIQ-1387eb | specified | RQ-SSIQ-9702af | Stage 0 optimistic-flag identities — one flagged table — before any concrete-cost table is treated as a prediction 
- H-SSIQ-18dc91 | analyzed | RQ-SSIQ-9702af | 
- H-SSIQ-2efc5c | proposed | RQ-SSIQ-9702af | 
- H-SSIQ-36e970 | analyzed | RQ-SSIQ-9702af | 
- H-SSIQ-3d5ff4 | specified | RQ-SSIQ-9702af | Stage 0 classical-only identities — zero quantum words in the exponent programme — before any quantum lever is treated as already installed 
- H-SSIQ-47e61d | specified | RQ-SSIQ-9702af | Stage 0 hitting-potential identities — one potential — before any drift is treated as a free improvement 
- H-SSIQ-545e66 | proposed | RQ-SSIQ-9702af | 
- H-SSIQ-678e04 | specified | RQ-SSIQ-9702af | Stage 0 smoothness thing guarantee balanced divisor replace identities — n=2 — before any later stage is authorized 
- H-SSIQ-6e0748 | analyzed | RQ-SSIQ-9702af | 
- H-SSIQ-75e596 | specified | RQ-SSIQ-9702af | Stage 0 quadratic-list-lever identities — L2 and L3 — before F3 is treated as non-quadratic 
- H-SSIQ-8de17f | specified | RQ-SSIQ-9702af | Stage 0 local-density corrected factorial moments smooth primitive identities — n=2 — before any later stage is authorized 
- H-SSIQ-8f34d8 | specified | RQ-SSIQ-9702af | Stage 0 successive minima trace-zero lattice independent aubry-oyono-vincent identities — n=3 — before any later stage is authorized 
- H-SSIQ-90e07b | proposed | RQ-SSIQ-9702af | 
- H-SSIQ-9353a6 | specified | RQ-SSIQ-9702af | Stage 0 write exponent equation down relation-collection cost identities — n=2 — before any later stage is authorized 
- H-SSIQ-9e2c71 | analyzed | RQ-SSIQ-9702af | 
- H-SSIQ-a9df38 | approved | RQ-SSIQ-9702af | 
- H-SSIQ-be47d5 | specified | RQ-SSIQ-9702af | Stage 0 turn twelve avenues closed theorem stated identities — n=3 — before any later stage is authorized 
- H-SSIQ-c892c5 | specified | RQ-SSIQ-9702af | Stage 0 absolute detection predicate algebraic form names identities — n=3 — before any later stage is authorized 
- H-SSIQ-d547fd | specified | RQ-SSIQ-9702af | Stage 0 two-line-theorem identities — two lines — before any orientation plateau is treated as an exponent below 1/3 
- H-SSIQ-dad689 | proposed | RQ-SSIQ-9702af | 
- H-SSIQ-e9f20c | specified | RQ-SSIQ-9702af | Stage 0 three-parameter identities — log_p(det), rank, c — before c=2 is treated as the only admissibility law 
- H-SSIQ-edba14 | specified | RQ-SSIQ-9702af | Stage 0 smoothness heuristic validated primes tail algorithm identities — n=2 — before any later stage is authorized 
- H-SSIQ-ee9627 | specified | RQ-SSIQ-9702af | Stage 0 local-density corrected factorial moments smooth primitive identities — n=2 — before any later stage is authorized 
- H-SSIQ-f2463c | specified | RQ-SSIQ-9702af | Stage 0 three-factor identities — table, attempt, inverse-success — before any one factor is treated as known-binding 
- H-SSIQ-fe47d7 | proposed | RQ-SSIQ-9702af | 


## Existing proposals in these lanes (id | status | question | title) -- DO NOT DUPLICATE

- IDEA-20260725-001 | None | RQ-SSI-001 | Full-cost re-baselining of classical supersingular path-finding
- IDEA-20260725-002 | None | RQ-SSI-001 | Effective orientation from a known small-degree endomorphism vs KN-TECH-050 path-finding baselines
- IDEA-20260725-003 | None | RQ-SSI-001 | Frozen SQIsign Fiat-Shamir transcript model SQI-FS-T0 and KN-OPEN-015 auxiliary-sufficiency test
- IDEA-20260729-001 | None | RQ-SSI-001 | CSIDH-COLLIMATION-FC0 typed resource-vector gate for the binary collimation sieve
- IDEA-20260801-007 | None | RQ-SSI-001 | CSIDH class-group action dimension test: measure the distinguished-point collision surface before any new path-finding mechanism
- IDEA-20260803-48e258 | proposed | RQ-SSI-001 | Stop reporting the Wesolowski margin as a number at one point - emit the crossover curve p*(w), the prime size at which the corrected p^(1/3+o(1)) method overtakes Delfs-
- IDEA-20260803-82b2b7 | proposed | RQ-SSI-001 | Stop trying to construct tau and decide whether it can exist - a trace-collision test for QM-STOPPING that terminates the FC0 lane in one batch, either with a named obstr
- IDEA-20260804-170692 | proposed | RQ-SSI-001 | Local transport signatures as a lossy quotient of supersingular paths
- IDEA-20260804-4c9ac0 | proposed | RQ-SSI-001 | Kernel-Frobenius type profiles for path-half compatibility
- IDEA-20260804-84328c | proposed | RQ-SSI-001 | Frobenius-orbit quotient for two-stage supersingular path collisions
- IDEA-20260805-062bee | proposed | RQ-SSI-001 | The exponent 1/3 is a covering-threshold exponent, not an algorithmic constant: measure (beta, gamma) in P(delta(E) <= D) ~ c * D^beta * p^{-gamma} and the best-known sup
- IDEA-20260805-250e50 | None | RQ-SSIQ-9702af | The screen-threshold cost identity: rewriting the p^{1/3+o(1)} exponent as E(theta, s, gamma) = (1/2 - 3theta/2)_+ + max(gamma, theta - s), which reproduces 1/3 exactly a
- IDEA-20260805-2d2c41 | None | RQ-SSIQ-9702af | Heuristic 1 is stated for a uniformly random curve, and every route that lowers the degree threshold conditions on a rare event: a smoothness conditioning audit on values
- IDEA-20260805-93ee20 | proposed | RQ-SSI-001 | The disposition-null: run this goal's own obligation-ledger protocol on a structure-free target whose correct verdict is derivable in advance, and find out whether twenty
- IDEA-20260805-bc8246 | proposed | RQ-SSI-001 | Three conventions, three verdicts: the van Oorschot-Wiener supersingular claw curve is exactly AT^2-isocost, and under plain area-time the p^{1/3+o(1)} algorithm is p^{1/
- IDEA-20260805-c60813 | None | RQ-SSIQ-9702af | Write the other exponent equation down: a relation-collection cost architecture on the quaternion side, its one-page kill (the Brandt object is a groupoid whose abelianis
- IDEA-20260805-d66193 | proposed | RQ-SSI-001 | Two 2026 claims about End(E) differ by an exponential factor and cannot both be about the same input: a quantifier-order and observation-collision adjudication that eithe
- IDEA-20260805-de1490 | None | RQ-SSIQ-9702af | The random arm of lever L4's own instrument has a forced value of exactly 1/2 and returned 0.4014: anchoring the descent estimator to a theorem it already contains, and d
- IDEA-20260805-e7ee4a | None | RQ-SSIQ-9702af | N5 executed at zero compute: the trace-vanishing mechanism as a selection rule, and an auxiliary-target census against the criterion log_p(det)/rank <= 1/4 -- the one nei
- IDEA-20260806-62ba9d | proposed | RQ-SSI-001 | SCOPE AND COST-MODEL WORK, NOT EXPONENT WORK: the campaign's 2^{120-123} figure is quoted for SQIsign but the theorem it rests on is about OneEnd, and the two polynomial-
- IDEA-20260806-7955a5 | proposed | RQ-SSI-001 | A CORRESPONDENCE THE PROGRAM RUNS BOTH HALVES OF AND HAS NEVER WRITTEN DOWN: the ECDLP is the RANK-ONE, HIDDEN-DEGREE case of exactly the input format the SIDH break cons
- IDEA-20260806-9c2f80 | proposed | RQ-SSI-001 | Every one of this goal's twelve closures quantifies "for all E, with no advice": the (S, T) preprocessing frontier for OneEnd under the changed quantifier "for all p, the
- IDEA-20260806-a3ef00 | proposed | RQ-SSI-001 | A FUNDAMENTALLY DIFFERENT DECOMPOSITION -- LOCAL-GLOBAL RATHER THAN DEGREE-SPLITTING -- APPLIED TO THE OBJECT THAT CARRIES SUPERSINGULAR HARDNESS: decompose EndRing's inf
- IDEA-20260806-b60c35 | proposed | RQ-SSI-001 | MEASUREMENT WORK, NOT EXPONENT WORK: Heuristic 1 is stated uniformly in p and the only experiment ever run for it used exactly the two DEPLOYED SQIsign primes and no cont
- IDEA-20260806-b7fdc3 | proposed | RQ-SSI-001 | A NEW ALGEBRAIC INVARIANT THIS CORPUS ALREADY OWNS AND HAS NEVER USED: the oriented self-pairing of Castryck-Houben-Merz (KN-LIT-7489) is a computable, orientation-sensit
- IDEA-20260806-bcbcf5 | proposed | RQ-SSI-001 | RANDOM-MATRIX ANALYSIS OF ISOGENY GRAPHS HAS THE WRONG NULL, AND USING IT GUARANTEES A FALSE POSITIVE: the eigenvalues are Hecke eigenvalues, so a measured deviation from
- IDEA-20260806-d5a34e | proposed | RQ-SSIQ-9702af | Turn "twelve avenues closed" into one theorem in one stated model: the isogeny-graph query model, in which the incumbent algorithm is LITERALLY an algorithm, a matching O
- IDEA-20260806-e4c719 | proposed | RQ-SSIQ-9702af | The exponent identity has a third parameter and the committed census does not contain it: exponent = c*log_p(det)/(2*rank), where c is the degree-count exponent of the am
- IDEA-20260807-6c89a8 | proposed | RQ-SSIQ-9702af | The entire supersingular exponent programme is CLASSICAL-ONLY: the word 'quantum' does not occur in GOAL-SSIQ-001's goal record or any of its thirteen checkpoint shards, 
- IDEA-20260807-6cdff2 | proposed | RQ-SSI-001 | The one avenue GOAL-SSI-001's own producer called 'The only open avenue' was closed by a SIBLING ARTIFACT from the same task, on an abstract-level reading, without doing 
- IDEA-20260807-726e55 | proposed | RQ-SSI-001 | CSIDH / class-group-action quantum security has NO goal anywhere, its only lane was deferred as 'requires quantum resources' -- which is wrong, since a Kuperberg/collimat
- IDEA-20260807-7424a9 | proposed | RQ-SSIQ-9702af | Levers L2 and L3 -- the QUADRATIC list factor F3 and the collision mechanism it feeds -- are recorded OPEN and unchanged in all thirteen GOAL-SSIQ-001 checkpoints, while 
- IDEA-20260807-7d8ba9 | proposed | RQ-SSI-001 | KN-OPEN-015 is used only as a SCOPE FENCE, never as a research object: its actual open question -- a general characterization of WHICH auxiliary data collapses an isogeny
- IDEA-20260807-a6a038 | None | RQ-SSI-001 | Planted-orientation instances: a positive control constructed by Deuring reduction of small-discriminant Hilbert class polynomials, run over a discriminant ladder to meas
- IDEA-20260807-d53a93 | None | RQ-SSIQ-9702af | The coverage ratio rho = 12M/p and the rho-stability test: a subsampling instrument that classifies every toy statistic in the Q2/Q3 slices as rho-stable (extrapolable) o
- IDEA-20260807-edb3f3 | None | RQ-SSIQ-9702af | The p^{1/4} certificate: four independently checkable necessary conditions (N1-N4) for the list-and-close architecture, and the observation that "enlarge the closable fam
- IDEA-20260808-70243a | proposed | RQ-SSI-001 | Harvest three independent claws instead of one and output a basis of End(E) directly, bypassing [35, Theorem 7.2] -- whose only explicit exponent, Omega((log N)^{-12}), t
- IDEA-20260808-71c2b2 | proposed | RQ-SSIQ-9702af | Overshoot the Aubry-Oyono-Vincent degree bound instead of matching it: treating the search radius T as a free parameter ABOVE (p/2)^{1/3} converts the paper's rare-event 
- IDEA-20260808-8a6cb5 | proposed | RQ-SSI-001 | delta_E is Lipschitz along isogeny edges but the SUCCESS indicator need not be: measure the autocorrelation of 1{delta_E is B-smooth} along non-backtracking walks against
- IDEA-20260808-dfd76a | proposed | RQ-SSI-001 | The frozen source's affected list omits its own reference [6]: a trusted setup whose entire purpose is producing a supersingular curve of unknown endomorphism ring must n
- IDEA-20260808-f313da | proposed | RQ-SSIQ-9702af | The three successive minima of the trace-zero lattice are NOT independent -- Aubry-Oyono-Vincent's own Gram identity forces p/4 <= N1 N2 N3 <= p/2 -- so Remark 1's multip
- IDEA-20260815-1cc763 | proposed | RQ-SSI-001 | THE ISOGENY GRAPH'S EXPANSION IS ASSUMED IN EVERY MIXING ARGUMENT AND MEASURED IN NONE OF THIS PROGRAM'S RECORDS: measure the spectral gap of the 2-isogeny graph at toy p
- IDEA-20260815-45aa63 | proposed | RQ-SSIQ-9702af | THE p^(1/3) RESULT IS THIS PROGRAM'S CANONICAL EXEMPLAR AND ITS OWN CONCRETE-COST TABLE FLAGS OPTIMISTIC ASSUMPTIONS: recompute the table with each flagged optimism remov
- IDEA-20260815-72c70d | proposed | RQ-SSI-001 | THE CGL HASH IS NAMED AS AFFECTED BY THE p^(1/3) RESULT AND ITS SECURITY LEVEL IS SET BY THE SAME PROBLEM: recompute its collision and preimage margins under the new base
- IDEA-20260815-854159 | proposed | RQ-SSIQ-9702af | WHICH OF THE THREE EXPONENT-CARRYING FACTORS IN THE p^(1/3) ALGORITHM IS ACTUALLY BINDING? Re-derive the exponent with each factor idealised in turn, so the campaign atta
- IDEA-20260815-86b09c | proposed | RQ-SSIQ-9702af | THE CLAW-FINDING TABLE IS KEYED AND ITS COLLISION BEHAVIOUR DETERMINES THE ALGORITHM'S SUCCESS: measure the table's actual key collision rate at toy primes against the un
- IDEA-20260815-943839 | proposed | RQ-SSI-001 | DELFS-GALBRAITH AND THE p^(1/3) ALGORITHM ARE COMPARED ONLY ASYMPTOTICALLY; MEASURE THE CROSSOVER PRIME WHERE THE NEW ALGORITHM ACTUALLY WINS UNDER MATCHED MEMORY CHARGIN
- IDEA-20260815-af4007 | proposed | RQ-SSI-001 | THE SIDH BREAK NEEDED TORSION IMAGES OF KNOWN DEGREE; ENUMERATE WHICH POST-SIDH SCHEMES STILL PUBLISH BOTH, AS A STANDING SURFACE AUDIT RATHER THAN A PER-SCHEME REACTION
- IDEA-20260815-bf2b26 | proposed | RQ-SSI-001 | THE ENDOMORPHISM-RING PROBLEM AND THE ISOGENY PROBLEM ARE LINKED BY POLYNOMIAL REDUCTIONS THAT NOBODY IN THIS PROGRAM HAS COSTED: measure the reduction network's actual p
- IDEA-20260815-e94ea3 | proposed | RQ-SSIQ-9702af | THE MEET-IN-THE-MIDDLE STEP IS WHERE THE p^(1/3) ALGORITHM SPENDS ITS MEMORY: check whether a van Oorschot-Wiener collision search replaces the keyed table and moves the 
- IDEA-20260815-ee8f82 | proposed | RQ-SSIQ-9702af | THE SMOOTHNESS HEURISTIC WAS VALIDATED AT TWO PRIMES AND ITS TAIL IS WHERE THE ALGORITHM LIVES: resample Heuristic 1 concentrating entirely on the smooth tail rather than
- IDEA-20260821-167fd9 | proposed | RQ-SSIQ-9702af | The memory lever is ONE object, not a family: every rebuild-and-shard reduction is dominated by van Oorschot-Wiener by exactly the shard count, so memory below p^{1/3} at
- IDEA-20260821-e99afd | proposed | RQ-SSIQ-9702af | The exponent is alpha/3. The whole 1/3-versus-lower question collapses onto ONE named quantity -- the cost exponent alpha of bounded-degree conjugate DETECTION -- which t
- IDEA-20260821-f48215 | proposed | RQ-SSI-001 | The preprocessing axis nobody has charged: shared-precomputation batch attacks on the supersingular endomorphism problem lie on the exact frontier (per-instance time) x (
- IDEA-20260901-1ddfd4 | proposed | RQ-SSI-001 | THE BALL MEET-IN-THE-MIDDLE COST EXPONENT IS a_g TIMES b_g OVER 2, WITH b_g = 1 + g(g+1)/2 FORCED COMBINATORIALLY BY THE COUNT OF MAXIMAL ISOTROPIC SUBGROUPS. The g = 1 s
- IDEA-20260901-1f5a62 | proposed | RQ-SSIQ-9702af | SMOOTHNESS IS USED FOR ONE THING ONLY -- to guarantee a balanced divisor -- so replace the smooth split (F2) by a DIVISOR split: list ALL cyclic isogenies of degree at mo
- IDEA-20260901-22428d | proposed | RQ-SSIQ-9702af | THE ABSOLUTE DETECTION PREDICATE HAS AN ALGEBRAIC FORM, AND ITS FORM NAMES THE CEILING: the stratum S_{<=D} = {E : delta_E <= D} is exactly the set of supersingular F_{p^
- IDEA-20260901-2fc431 | proposed | RQ-SSI-001 | THE RE-RANDOMISATION LOOP IS A PURCHASE AT A KNOWN EXCHANGE RATE, AND THE RATE IS THE SUCCESSIVE-MINIMA COUNT. Buy the P0 inverse with table instead of with attempts: a s
- IDEA-20260901-65c009 | proposed | RQ-SSI-001 | A CHEAP SUBLEVEL DETECTOR FOR delta(E) IS WORTH AN EXACT EXPONENT. Any one-sided detector of the event delta(E) <= Y computable in time p^c moves the OneEnd exponent from
- IDEA-20260901-6a7a3e | proposed | RQ-SSIQ-9702af | THE delta_E LANDSCAPE IS MADE OF ORIENTATION PLATEAUS: a two-line theorem (every minimal conjugate isogeny phi: E -> E^{(p)} of degree d makes alpha = Frob o phi a trace-
- IDEA-20260901-871141 | proposed | RQ-SSI-001 | CSIDH KEY RECOVERY IS A SUBSET-SUM MEET-IN-THE-MIDDLE THAT HAS NEVER BEEN GIVEN THE REPRESENTATION TECHNIQUE, AND THE EXACT REASON IS A MISSING OBJECT WITH A NAME. The te
- IDEA-20260901-deaf80 | proposed | RQ-SSI-001 | THE ALGORITHM HAS EXACTLY ONE CANONICAL TARGET AND LEVEL STRUCTURE OFFERS MORE. Adding a level N to the instance replaces the single Frobenius conjugate by an Atkin-Lehne
- IDEA-20260904-31f1fa | proposed | RQ-SSI-001 | KN-OPEN-015 ASKS WHICH AUXILIARY DATA COLLAPSES AN ISOGENY ASSUMPTION AND THIS PROGRAM HAS ONLY EVER USED IT AS A SCOPE FENCE: the answer proposed here is a SHARP DICHOTO
- IDEA-20260904-5b0fc9 | proposed | RQ-SSI-001 | "CGL IS AFFECTED" IS A STATEMENT ABOUT AN ENDOMORPHISM AND A CGL COLLISION IS A STATEMENT ABOUT TWO EQUAL-LENGTH 2-POWER PATHS, AND THE TWO ARE SEPARATED BY A LENGTH OVER
- IDEA-20260904-6e8793 | proposed | RQ-SSI-001 | CSIDH SITS ON THE FROZEN SOURCE'S "SAFE" LIST BY A MARGIN OF EXACTLY ONE NUMBER, AND THAT NUMBER IS alpha = 3/4: CSIDH key recovery has a SECOND route nobody in this prog
- IDEA-20260904-9b58ab | proposed | RQ-SSI-001 | THE MEMORY EXPONENT IS THE FROZEN SOURCE'S OWN NAMED OPEN PROBLEM AND IDEA-20260901-6a7a3e ALREADY BUILT THE OBJECT THAT ANSWERS IT AT THE BOUNDARY, THEN READ ONLY THE TI
- IDEA-20260904-9bf9c6 | proposed | RQ-SSI-001 | ONEEND IS POLYNOMIAL-TIME ON THE F_p-RATIONAL LOCUS AND CSIDH IS STILL NOT BROKEN, SO COROLLARY 1.2'S CASCADE CANNOT BE UNIFORM IN THE RETURNED ENDOMORPHISM: an explicit 
- IDEA-20260904-ec17aa | proposed | RQ-SSI-001 | THE "THIRD AGGREGATION STRUCTURE" THAT IDEA-20260901-22428d DECLARED MISSING AND UNEXHIBITED EXISTS IN THE LITERATURE AND WAS VERIFIED THIS SESSION: Udovenko's bivariate 
- IDEA-20260905-4b07f5 | proposed | RQ-SSI-001 | Descent-cocycle obstruction as a compositional isogeny certificate
- IDEA-20260905-931866 | proposed | RQ-SSIQ-9702af | Local-density corrected factorial moments for smooth primitive norm values
- IDEA-20260905-9a5462 | proposed | RQ-SSI-001 | Second-moment geometry of Frobenius correspondences before rare-stratum claims
- IDEA-20260905-c6aae0 | proposed | RQ-SSIQ-9702af | Local-density corrected factorial moments for smooth primitive norm values
- IDEA-20260905-cea1d6 | proposed | RQ-SSI-001 | Second-moment geometry of Frobenius correspondences before rare-stratum claims
- IDEA-20260905-da0612 | proposed | RQ-SSI-001 | Descent-cocycle obstruction as a compositional isogeny certificate
- IDEA-20260906-74c257 | proposed | RQ-SSIQ-9702af | Capacity-controlled hitting of low-degree Frobenius strata
- IDEA-20260906-953896 | proposed | RQ-SSI-001 | Schur-complement norm slicing for an explicitly supplied quaternion coset
- IDEA-20260906-d95de0 | proposed | RQ-SSI-001 | Automorphism-valued holonomy of nonbacktracking isogeny cycles
- IDEA-20260926-442b92 | proposed | RQ-SSI-001 | The oriented Frobenius-twin route regresses to a known result. With a published orientation, OneEnd is immediate, and EndRing costs about disc(Z[alpha])^{1/4} classically
- IDEA-20260926-e1b48e | proposed | RQ-SSIQ-9702af | The "rank 4 with det <~ p" window of GOAL-SSIQ-001's admissibility criterion cannot be entered. Every full-rank sublattice of any Hom(E, E') under the degree form has Gra