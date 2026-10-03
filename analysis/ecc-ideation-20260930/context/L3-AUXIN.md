# Lane L3-AUXIN context (generated 2026-09-30 from committed ledger state; read-only)


## RQ-AUXIN-f8d8c0  (ledger/questions/RQ-AUXIN-f8d8c0.yaml)

```yaml
research_question:
  id: RQ-AUXIN-f8d8c0
  title: >-
    Where does auxiliary-input discrete logarithm (Cheon) actually stop at
    deployed parameters, once the divisor structure of r±1 is computed exactly
    and the auxiliary-point supply is charged to a named protocol rather than
    assumed?
  scope:
    curve_families:
      - standardized prime-field curves (NIST P-224/P-256/P-384/P-521,
        secp256k1, brainpool, Curve25519/Ed25519 group order)
      - pairing-friendly curves as deployed (BN254, BLS12-381) where q-SDH-style
        assumptions are actually instantiated
      - synthetic curves with planted divisors of r-1 or r+1, for mechanism
        reproduction only
    field_types: [prime]
    bit_sizes: [toy 16-40 for reproduction, 224-521 for the deployed-parameter census]
    methods:
      - exact integer factorization of r-1 and r+1 for standardized orders
      - Cheon auxiliary-input DLP (baseline, known prior art)
      - Kozaki-Kutsuma-Matsuo variants
      - protocol-level audit of which powers [x^i]P a scheme releases
  motivation: >-
    This program has already met Cheon's algorithm once, from the wrong
    direction. BATCH-032 produced APR-206, an "augmented-input" route with a
    balanced N^{1/4} row, and DEC-20260802-204 correctly reclassified it as a
    rediscovery of Cheon's DLP-with-auxiliary-input rather than a new
    conditional theorem. That decision also recorded the gate that makes the
    reclassification stick: acquisition of A = [x^d]P from ordinary input
    (P, Q = [x]P) "remains unestablished below rho-scale work", so nothing about
    Cheon improves ORDINARY ECDLP.

    That gate is correct and this question does not reopen it. What the gate
    leaves entirely untouched is the case where the auxiliary points are not
    acquired at all because a protocol PUBLISHES them: q-SDH, Boneh-Boyen
    signatures, and several pairing and threshold constructions release
    [x]P, [x^2]P, ..., [x^q]P by design. In that setting the acquisition cost
    is zero by construction, and the only remaining question is arithmetic:
    does r±1 for the curve actually carry a divisor d that makes
    O(sqrt(r/d) + sqrt(d)) bite?

    That arithmetic question is FINITE, EXACT, and unasked. No goal or research
    question in this ledger mentions Cheon, auxiliary-input DLP, or q-SDH
    (verified 2026-08-31 across ledger/goals and ledger/questions: zero hits).
    The seventeen ledger files that do mention Cheon are the BATCH-032/033
    corrections, decisions and proposals that closed the ordinary-ECDLP route.
    The lane is open, and it is open on the side where the attack is real.
  decision_target: >-
    A per-curve verdict, backed by an exact factorization certificate: for each
    standardized curve, the best exponent any Cheon-type auxiliary-input attack
    can reach given the divisors r-1 and r+1 actually have, together with the
    number of auxiliary powers a named deployed protocol actually releases.
    Two outcomes are both decisive and both publishable. If deployed orders
    carry no useful divisor, the entire attack class is inert at deployed
    parameters independent of protocol, and the lane closes with a certificate
    rather than an opinion. If some do, the result names which protocol
    instantiations sit inside the reachable region.
  constraints:
    - >-
      NOTHING IN THIS QUESTION IS AN ORDINARY-ECDLP CLAIM. DEC-20260802-204 and
      DEC-20260802-206 stand: the auxiliary points are an INPUT supplied by a
      protocol, never an achievement of the attack. Any record under this
      question that states or implies an ordinary-ECDLP improvement is invalid
      on its face and must be superseded.
    - >-
      Cheon's algorithm is KNOWN PRIOR ART, already classified as such by
      DEC-20260802-208 with a filed primary source. No record here may assert
      novelty for the algorithm. Novelty, if any, is confined to the
      deployed-parameter census and the protocol supply audit, and must be
      argued against the literature, not assumed.
    - >-
      Every literature reference reaching this question through the 2026-08-31
      coverage-gap input document is `recalled` provenance and supports nothing
      until an agent reads the primary source and files a KN-LIT record. No
      experiment beyond the pure-arithmetic divisor census may be DESIGNED
      until the Cheon primary sources are filed.
    - >-
      The divisor census reports factorizations, not difficulty. A divisor of
      the right size is a NECESSARY condition for the attack to bite; it is not
      sufficient, and the census may not be reported as a vulnerability.
  status: active
  owner: coordinator
  added: '2026-08-31'

```


## goal head GOAL-AUXIN-a93442
```
# GOAL-AUXIN-a93442 — head projection from ledger/goals/GOAL-AUXIN-a93442.yaml
# Resume fields only; ad-hoc keys and checkpoint bodies are not shown.

id: GOAL-AUXIN-a93442
status: active
title: 'Auxiliary-input discrete logarithm at deployed parameters: the exact divisor census of r±1, and the protocol audit of which powers are actually released'
current_batch_id: BATCH-bed104
dispatch_queue_path: coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-bed104/dispatch_queue.json
next_action: 'Under DEC-20260930-224fc1 + BATCH-bed104 closed (wiring snapshot 115fe9f50): /run EXP-AUXIN-339fb0 subject to admission_gate / F-CUSTODY at launch; do not edit specification.yaml (6a1dca32…). Host may still fail admission on missing ecm/cypari2/pypdf (IMP-ADMISSION-TOOLS-1; infrastructure, not math). H-AUXIN-6db354 stays proposed. current_batch may stay BATCH-bed104 closed_archived. Deferred: GOAL-ECDLP2M-001 TASK-20260925-a9c531.'
campaign_budget:
  _omitted: +2 earlier keys not shown; goal_head.py show GOAL-AUXIN-a93442 --field campaign_budget
  max_concurrent: 2
  unlimited_budget_note_20260904: 'ECC goal: campaign budget is UNLIMITED by declared policy (orchestration/research-priority.yaml, user instruction 2026-09-04). Prior finite values, preserved and NOT retracted: maximum_batches=4. max_concurrent stays bounded -- it is machine headroom, not a research budget. Unlimited removes the batch ceiling, not the duty to rank: never dispatch a task you cannot rank ahead of doing nothing.'
completion_criteria:
- 'The divisor census is complete for a declared, frozen list of standardized curve orders: r-1 and r+1 fully factored (or factored to a stated bound with the unfactored cofactor reported as such, never silently), each factorization independently recomputed by the run wrapper, and the best achievable exponent min over admissible d of the Cheon cost tabulated per curve against the sqrt(r) rho baseline at identical accounting.'
- 'The protocol supply audit is complete for a declared list of deployed instantiations: for each, the number and form of released auxiliary powers, cited to the specification, with instantiations whose parameters are not publicly pinned reported as UNDETERMINED rather than guessed.'
- A joined verdict table with one row per (curve, protocol) pair, each cell either a stated reachable exponent with its certificate, or an explicit not_applicable with the reason. Cells that are inert because of (1) are distinguished from cells that are inert because of (2).
- Either the mechanism reproduction passes its planted-divisor positive control AND its no-divisor null control at toy scale, or the goal records why it could not be run and claims nothing about the mechanism.
pause_conditions:
- The Cheon primary sources cannot be filed as KN-LIT records. Everything beyond the pure-arithmetic divisor census is gated on them; the census itself depends on no citation, only on the algorithm's stated cost, which is already filed as prior art by DEC-20260802-208.
- 'Any record under this goal states or implies an ordinary-ECDLP improvement. Pause and supersede: DEC-20260802-204''s acquisition gate is binding and this goal is scoped to protocol-supplied inputs only.'
- 'The divisor census returns a hit near sqrt(r) on a deployed curve. That is a stop-and-escalate condition, not a proceed condition: it goes to independent validation and red team BEFORE any further work, because a surprising positive on standardized parameters is exactly the class of claim this program is least entitled to make quickly.'
open_batches:
- batch_id: BATCH-cae584
  dispatch_queue_path: coordination/design/BATCH-cae584/dispatch_queue.json
  branch: cursor/design-auxin-df4197-8a78
  opened_by: coordinator
  opening_decision_id: DEC-20260913-515d80
- batch_id: BATCH-ba0b0d
  dispatch_queue_path: coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-ba0b0d/dispatch_queue.json
  branch: claude/factor-base-field-comparison-kn8wt7
  opened_by: coordinator
  opening_decision_id: DEC-20260922-19b645
- batch_id: BATCH-09aadd
  dispatch_queue_path: coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-09aadd/dispatch_queue.json
  branch: claude/factor-base-field-comparison-kn8wt7
  opened_by: coordinator
  opening_decision_id: DEC-20260923-bd46e6
  review_plan: coordination/review/auxin-20260923-09aadd/review-plan.yaml
  lane_note: Design round for AMD-EXP-AUXIN-7e2e3d-20260923-d1d10. Registered with `goal_lanes.py open-lane` by the top-level session after TASK-20260923-fa1faf verifies.
- batch_id: BATCH-2fc87b
  dispatch_queue_path: coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-2fc87b/dispatch_queue.json
  branch: claude/crypto-autoresearcher-harness-fc3lc6
  opened_by: coordinator
  opening_decision_id: DEC-20260926-0eed78
  review_plan: coordination/review/auxin-20260926-2fc87b/review-plan.yaml
  lane_note: Revision design round for AMD-EXP-AUXIN-7e2e3d-20260926-typed (under H-AUXIN-6db354). The top-level session registers it with `goal_lanes.py open-lane` after TASK-20260926-4d156e verifies.
- batch_id: BATCH-7b6678
  dispatch_queue_path: coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-7b6678/dispatch_queue.json
  branch: coord/ecdlp-portfolio-20260927
  opened_by: coordinator
  opening_decision_id: DEC-20260927-35dc6c
  review_plan: coordination/review/auxin-20260927-7b6678/review-plan.yaml
  lane_note: Narrow corrective amendment design round (ranking option 3, RS-C) for AMD-EXP-AUXIN-7e2e3d-20260927-narrow under H-AUXIN-6db354. Lane registration with `goal_lanes.py open-lane` is left to the top-level session; none existed when DEC-20260927-35dc6c was written.
- batch_id: BATCH-104724
  dispatch_queue_path: coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-104724/dispatch_queue.json
  branch: coord/ecdlp-portfolio-20260927
  opened_by: coordinator
  opening_decision_id: DEC-20260928-2f8768
  review_plan: coordination/review/auxin-20260928-104724/review-plan.yaml
  lane_note: 'Scope-ranking revision design round under DEC-2
```


## Existing hypotheses in these lanes (id | status | question | title)

- H-AUXIN-269efd | specified | RQ-AUXIN-f8d8c0 | Stage 0 generic-span identities — {1,x} does not contain x^2 — before any GGM lower bound is claimed 
- H-AUXIN-52eb55 | specified | RQ-AUXIN-f8d8c0 | Stage 0 finite-difference identities — (x+1)^2-x^2=2x+1 — before any token compiler is built 
- H-AUXIN-66e6fd | approved | RQ-AUXIN-f8d8c0 | 
- H-AUXIN-686282 | approved | RQ-AUXIN-f8d8c0 | 
- H-AUXIN-6db354 | proposed | RQ-AUXIN-f8d8c0 | 
- H-AUXIN-7c52b2 | proposed | RQ-AUXIN-f8d8c0 | 
- H-AUXIN-9bb701 | specified | RQ-AUXIN-f8d8c0 | Stage 0 two-valued SafeCurves-row identities — arithmetic fact and protocol-conditional — before any curve is scored weak 
- H-AUXIN-d2f0bb | specified | RQ-AUXIN-f8d8c0 | Stage 0 Cheon balanced-memory identities — at d=4, r=16, sqrt(d)=2 equals r^{1/4} — before any frontier is swept 
- H-AUXIN-e73988 | specified | RQ-AUXIN-f8d8c0 | Stage 0 Cheon planted-divisor cost identities — sqrt(4)+sqrt(4)=4 at r=17, d=4 — before any solver is run 


## Existing proposals in these lanes (id | status | question | title) -- DO NOT DUPLICATE

- IDEA-20260905-830138 | proposed | RQ-AUXIN-f8d8c0 | Typed auxiliary-input availability and divisor certificates
- IDEA-20260906-3d57e8 | proposed | RQ-AUXIN-f8d8c0 | Finite-difference compilation of shifted auxiliary powers
- IDEA-20260906-81648b | proposed | RQ-AUXIN-f8d8c0 | CRT composition of several supplied Cheon first-stage constraints