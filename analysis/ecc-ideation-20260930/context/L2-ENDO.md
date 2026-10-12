# Lane L2-ENDO context (generated 2026-09-30 from committed ledger state; read-only)


## RQ-ECDLP-912694  (ledger/questions/RQ-ECDLP-912694.yaml)

```yaml
research_question:
  id: RQ-ECDLP-912694
  title: >-
    Can an ordinary special-j curve leave its CM automorphism locus through a
    public rational odd-degree isogeny?
  scope:
    curve_families:
      - y^2 = x^3 + b with j=0 and p congruent to 1 mod 3
      - y^2 = x^3 + a*x with j=1728 and p congruent to 1 mod 4
      - extension-field special-j controls where the named automorphism is not F_p-rational
    field_types: [prime field F_p]
    bit_sizes: [7, 8, 9]
    methods: [exact finite-field point enumeration, odd-degree Velu quotient, CM splitting classification]
  motivation: >-
    The existing isogeny-class screen measured no end-to-end transfer gain but
    did not isolate whether changing representatives can remove or preserve
    the public low-degree CM automorphism itself. This is the structural gate
    before treating a different j-invariant as a new endomorphism source.
  decision_target: >-
    Determine the finite-scope split/non-split and exceptional-prime boundary
    for special-j rational isogeny closure, without claiming a crypto-scale theorem.
  constraints:
    - Ordinary curves only; supersingular and extension-field-only maps are out of scope.
    - Odd prime degrees ell in {3,5,7,11,13}; even-degree formulas are not implemented.
    - Every kernel and quotient map must carry an independent curve-membership certificate.
    - Exception cells are controls and cannot be used as unqualified falsification evidence.
  status: active
  owner: coordinator

```


## RQ-JINV-8fc13a  (ledger/questions/RQ-JINV-8fc13a.yaml)

```yaml
research_question:
  id: RQ-JINV-8fc13a
  title: Do special j-invariants (0, 1728, small |D_0|, small height) confer any ECDLP advantage beyond
    the sqrt(|Aut|) automorphism-quotient constant?
  scope:
    curve_families:
    - toy ordinary prime-field short-Weierstrass curves enumerated by isogeny class
    - CM curves with small fundamental discriminant, including j=0 and j=1728
    - matched random-curve null objects at the same p
    field_types:
    - prime
    bit_sizes:
    - toy instances (p up to ~32 bits) for executable falsification only
    - symbolic and asymptotic models for scope statements
    methods:
    - R2 curve equation and model
    - R3 End(E) as a ring
    - Compare curves with small CM fundamental discriminant against generic-D_0 curves at matched
      p and matched N on every measured functional, separating the known automorphism discount from
      anything else.
  motivation: Lane of GOAL-ENDO-001, the resource-labelled subproblem decomposition of prime-field
    ECDLP in analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md. Every lane must name the
    non-generic resource it consumes, because the generic-group route is closed at exponent 1/2 for
    incidence and endomorphism-image oracles (KN-FIND-b7e091) and because every endomorphism acts
    as a scalar on a prime-order subgroup (H-ENDO-001).
  decision_target: Any claimed advantage must be stated against the automorphism-discounted rho baseline;
    a constant factor at or below sqrt(6) is baseline calibration and is recorded as such, never as
    an attack.
  constraints:
  - Lawful defensive cryptanalysis on public constructions and toy benchmarks only.
  - No targeting or recovery of live private keys, wallets, or deployed systems.
  - Pollard rho with distinguished points and BSGS are mandatory matched controls; on CM curves the
    automorphism-discounted rho baseline is the control (KN-TECH-018).
  - Every measured quantity requires a null object of the same shape and a decay test before it is
    believed (docs/inventor-protocol.md).
  - Every claimed solve or relation requires a certificate re-verified independently of the solver
    (docs/claims-and-verification.md).
  - 'Evidence from these runs is capped at claim_tier: toy.'
  - Timeouts, crashes and infrastructure failures are never negative mathematical evidence (AGENTS.md
    rule 5).
  status: active
  owner: coordinator

```


## RQ-ICINV-475b5e  (ledger/questions/RQ-ICINV-475b5e.yaml)

```yaml
research_question:
  id: RQ-ICINV-475b5e
  title: Is any prime-field ECDLP attack-cost functional non-constant across an F_p-isogeny class,
    and is a minimiser reachable?
  scope:
    curve_families:
    - toy ordinary prime-field short-Weierstrass curves enumerated by isogeny class
    - CM curves with small fundamental discriminant, including j=0 and j=1728
    - matched random-curve null objects at the same p
    field_types:
    - prime
    bit_sizes:
    - toy instances (p up to ~32 bits) for executable falsification only
    - symbolic and asymptotic models for scope statements
    methods:
    - R1 field-representation of x-coordinates
    - R2 curve equation and model
    - R4 isogeny graph
    - Enumerate a complete toy isogeny class; measure Semaev/Groebner solving-degree proxies, first-fall
      degree, relation yield and factor-base decomposition probability on every curve in it; compare
      within-class variance against between-class variance and a matched random-curve null at the
      same p.
  motivation: Lane of GOAL-ENDO-001, the resource-labelled subproblem decomposition of prime-field
    ECDLP in analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md. Every lane must name the
    non-generic resource it consumes, because the generic-group route is closed at exponent 1/2 for
    incidence and endomorphism-image oracles (KN-FIND-b7e091) and because every endomorphism acts
    as a scalar on a prime-order subgroup (H-ENDO-001).
  decision_target: Admit a cost functional only if its within-class variance exceeds its matched-null
    variance AND the minimiser is reachable by a local test during an isogeny walk. Zero within-class
    variance closes this axis for that functional with a named obstruction, which is itself a deliverable.
  constraints:
  - Lawful defensive cryptanalysis on public constructions and toy benchmarks only.
  - No targeting or recovery of live private keys, wallets, or deployed systems.
  - Pollard rho with distinguished points and BSGS are mandatory matched controls; on CM curves the
    automorphism-discounted rho baseline is the control (KN-TECH-018).
  - Every measured quantity requires a null object of the same shape and a decay test before it is
    believed (docs/inventor-protocol.md).
  - Every claimed solve or relation requires a certificate re-verified independently of the solver
    (docs/claims-and-verification.md).
  - 'Evidence from these runs is capped at claim_tier: toy.'
  - Timeouts, crashes and infrastructure failures are never negative mathematical evidence (AGENTS.md
    rule 5).
  status: active
  owner: coordinator

```


## RQ-GGMB-6eaabc  (ledger/questions/RQ-GGMB-6eaabc.yaml)

```yaml
research_question:
  id: RQ-GGMB-6eaabc
  title: For each new oracle class the campaign invents, is it generic-group simulable?
  scope:
    curve_families:
    - toy ordinary prime-field short-Weierstrass curves enumerated by isogeny class
    - CM curves with small fundamental discriminant, including j=0 and j=1728
    - matched random-curve null objects at the same p
    field_types:
    - prime
    bit_sizes:
    - toy instances (p up to ~32 bits) for executable falsification only
    - symbolic and asymptotic models for scope statements
    methods:
    - 'audit lane: consumes no resource, classifies the resources others claim'
    - Construct an explicit simulator, or an explicit proof that no simulator exists, for every oracle
      proposed in the other lanes; extends KN-FIND-b7e091 to new oracle classes.
  motivation: Lane of GOAL-ENDO-001, the resource-labelled subproblem decomposition of prime-field
    ECDLP in analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md. Every lane must name the
    non-generic resource it consumes, because the generic-group route is closed at exponent 1/2 for
    incidence and endomorphism-image oracles (KN-FIND-b7e091) and because every endomorphism acts
    as a scalar on a prime-order subgroup (H-ENDO-001).
  decision_target: A simulable oracle is closed at exponent 1/2 immediately and its lane is stopped
    before compute is spent. This is the campaign's cheapest falsifier and runs before expensive experiments.
  constraints:
  - Lawful defensive cryptanalysis on public constructions and toy benchmarks only.
  - No targeting or recovery of live private keys, wallets, or deployed systems.
  - Pollard rho with distinguished points and BSGS are mandatory matched controls; on CM curves the
    automorphism-discounted rho baseline is the control (KN-TECH-018).
  - Every measured quantity requires a null object of the same shape and a decay test before it is
    believed (docs/inventor-protocol.md).
  - Every claimed solve or relation requires a certificate re-verified independently of the solver
    (docs/claims-and-verification.md).
  - 'Evidence from these runs is capped at claim_tier: toy.'
  - Timeouts, crashes and infrastructure failures are never negative mathematical evidence (AGENTS.md
    rule 5).
  status: active
  owner: coordinator

```


## RQ-INSTR-f8faa0  (ledger/questions/RQ-INSTR-f8faa0.yaml)

```yaml
research_question:
  id: RQ-INSTR-f8faa0
  title: Do the campaign's instruments detect planted signals and reject matched nulls?
  scope:
    curve_families:
    - toy ordinary prime-field short-Weierstrass curves enumerated by isogeny class
    - CM curves with small fundamental discriminant, including j=0 and j=1728
    - matched random-curve null objects at the same p
    field_types:
    - prime
    bit_sizes:
    - toy instances (p up to ~32 bits) for executable falsification only
    - symbolic and asymptotic models for scope statements
    methods:
    - 'audit lane: instrumentation, null objects, certificates'
    - Every measured quantity gets a null object of the same shape, a decay test in the structure-destroying
      parameter, and a planted-signal positive control; every claimed solve or relation gets a certificate
      re-verified independently of the solver.
  motivation: Lane of GOAL-ENDO-001, the resource-labelled subproblem decomposition of prime-field
    ECDLP in analysis/endomorphism-isogeny-decomposition/DECOMPOSITION.md. Every lane must name the
    non-generic resource it consumes, because the generic-group route is closed at exponent 1/2 for
    incidence and endomorphism-image oracles (KN-FIND-b7e091) and because every endomorphism acts
    as a scalar on a prime-order subgroup (H-ENDO-001).
  decision_target: An instrument that cannot detect a planted signal cannot support a negative, and
    one that fires on a matched null cannot support a positive. Both directions are required before
    any lane's result is citable.
  constraints:
  - Lawful defensive cryptanalysis on public constructions and toy benchmarks only.
  - No targeting or recovery of live private keys, wallets, or deployed systems.
  - Pollard rho with distinguished points and BSGS are mandatory matched controls; on CM curves the
    automorphism-discounted rho baseline is the control (KN-TECH-018).
  - Every measured quantity requires a null object of the same shape and a decay test before it is
    believed (docs/inventor-protocol.md).
  - Every claimed solve or relation requires a certificate re-verified independently of the solver
    (docs/claims-and-verification.md).
  - 'Evidence from these runs is capped at claim_tier: toy.'
  - Timeouts, crashes and infrastructure failures are never negative mathematical evidence (AGENTS.md
    rule 5).
  status: active
  owner: coordinator

```


## goal head GOAL-ENDO-001
```
# GOAL-ENDO-001 — head projection from ledger/goals/GOAL-ENDO-001/goal.yaml
# Resume fields only; ad-hoc keys and checkpoint bodies are not shown.

id: GOAL-ENDO-001
status: active
title: Resource-labelled subproblem decomposition of prime-field ECDLP, centred on endomorphisms, isogenous curves, and j-invariant structure
current_batch_id: BATCH-e59907
dispatch_queue_path: coordination/goals/GOAL-ENDO-001/batches/BATCH-e59907/dispatch_queue.json
next_action: Coordinator refresh the existing EXP-JINV-bd141d specification, amendments and executable-plan dependency checks using the completed BATCH-e59907 static prerequisite receipt; continue only its eligible existing preparation task, naming any remaining prerequisite. Do not repeat this completed repair, treat presence PASS as experiment approval, or admit new witness-domain work in execution mode.
campaign_budget:
  _omitted: +1 earlier keys not shown; goal_head.py show GOAL-ENDO-001 --field campaign_budget
  total_wall_clock_seconds: null
  max_concurrent: 6
completion_criteria:
- C1. For every one of the fourteen lanes, either an archived experiment contract with an executed, independently reviewed run, or an archived decision recording why the lane is closed that names an obstruction, an argument, and concrete forward guidance. A count of screened-and-rejected mechanisms does not satisfy C1 (docs/inventor-protocol.md closure standard).
- 'C2. RQ-ICINV-475b5e, the gating lane, is adjudicated: either the within-class variance of at least one attack-cost functional exceeds its matched null with the reachability gate T5 addressed, or the isogeny-class invariance of the measured functionals is recorded as a scoped negative with its obstruction named and its test boundary stated.'
- C3. Every oracle class invented by any lane has been passed through RQ-GGMB-6eaabc and is recorded as simulable (hence closed at exponent 1/2) or non-simulable with an explicit argument.
- 'C4. Every instrument used to support any conclusion has passed both directions of its RQ-INSTR-f8faa0 control: it detects a planted signal and it rejects a matched null.'
pause_conditions:
- P1. The instrument fails its RQ-INSTR-f8faa0 two-directional control. Measurement stops until the instrument is repaired under a new contract; existing measurements taken with the failed instrument are marked attempted_and_inconclusive, never negative evidence.
- P2. A lane result would bear on H-STR-002 in either direction. Work pauses until DEFER-BATCH009-001 is discharged under GOAL-ECDLP-001; this campaign may not transition that hypothesis.
- P3. Any candidate appears to exceed the automorphism-discounted rho baseline. Work pauses for an independent review-adversarial session before any record states the excess, and for review-breakthrough at max effort before any record calls it a break.
latest_verified_commit: 61f5413c879be98c3b04f10661e5ec7da355350f
question_ids:
- RQ-ICINV-475b5e
- RQ-VOLC-f6253b
- RQ-JINV-8fc13a
- RQ-EQIC-8cb959
- RQ-EQLA-0d3f40
- RQ-EWALK-8fa147
- RQ-TORS-8c7b79
- RQ-PAIR-21313f
- RQ-CANL-63098f
- RQ-CLGP-b99df5
- RQ-MODEL-e61cb2
- RQ-GGMB-6eaabc
- RQ-MTGT-2cabee
- RQ-INSTR-f8faa0
active_hypothesis_ids: []
owner: coordinator
updated_at: '2026-09-29'
_ad_hoc_keys_not_shown: 80 undeclared top-level keys on this record (goal_head.py audit GOAL-ENDO-001)
_checkpoint_shards: 13 shard(s), latest BATCH-de621d (ledger/goals/GOAL-ENDO-001/checkpoints/)

```


## Existing hypotheses in these lanes (id | status | question | title)

- H-ECDLP-0e7bf2 | proposed | RQ-ECDLP-912694 | 
- H-ECDLP-3cf1d8 | proposed | RQ-ECDLP-912694 | 
- H-ECDLP-3ffc94 | proposed | RQ-JINV-8fc13a | The special-j support drop is a property of the depressed short-Weierstrass normalisation and not of the curve, so it vanishes under the one model change every curve over
- H-ECDLP-53db9d | specified | RQ-ECDLP-912694 | Stage 0 class-number identities — h(-3)=h(-4)=1 — before any self-pairing address is claimed 
- H-ECDLP-5bc40d | specified | RQ-ECDLP-912694 | Stage 0 special-j Aut orbit identities — m=3 at j=0, partition [1,1,3,3] at ell=5 — before any walk is sampled 
- H-ECDLP-66d6fc | proposed | RQ-ECDLP-912694 | 
- H-ECDLP-84ca6a | proposed | RQ-INSTR-f8faa0 | Four fabricated artifact hashes passed reviewer, validator and red team undetected, so a two-stage detector and a review-role calibration are both warranted; but the prop
- H-ECDLP-9a49a8 | proposed | RQ-INSTR-f8faa0 | 
- H-ECDLP-e32126 | proposed | RQ-JINV-8fc13a | Replace the saturated degree meter with the graded Hilbert function of the m = 3 Semaev relation ideal, because a first-fall degree cannot fall below a null that already 
- H-ECDLP-f9aa58 | proposed | RQ-JINV-8fc13a | 
- H-ENDO-001 | approved | RQ-ECDLP-002 | 
- H-ENDO-276565 | approved | RQ-ECDLP-002 | 
- H-ENDO-b1e638 | proposed | RQ-EQIC-8cb959 | 
- H-GGMB-da21f5 | proposed | RQ-GGMB-6eaabc | 
- H-GGMB-e85e0e | specified | RQ-GGMB-6eaabc | Stage 0 generic group bound quoted barrier interesting identities — n=2 — before any later stage is authorized 
- H-ICEX-068cec | proposed | RQ-JINV-8fc13a | 
- H-ICEX-51839b | proposed | RQ-JINV-8fc13a | ARE THE SEMAEV-SPECIAL j ALSO ARITHMETICALLY SPECIAL - each degeneration j is a FIXED RATIONAL, so it defines one curve over Q whose reductions form a family indexed by p
- H-ICEX-604b5f | proposed | RQ-JINV-8fc13a | THE SINGULAR LOCUS OF THE SEMAEV HYPERSURFACE AT m = 3 IS THE 2-TORSION LOCUS AND IS (dim, deg) = (0, 6) FOR EVERY NONSINGULAR CURVE - DERIVED AND VERIFIED BY HAND HERE -
- H-ICEX-77c62a | proposed | RQ-JINV-8fc13a | 
- H-ICEX-ce964e | proposed | RQ-JINV-8fc13a | REDUCIBILITY IS THE ONLY DEGENERATION FUNCTIONAL A SOLVER CHARGES FOR, AND THE PREDICTION IS NEGATIVE - with two corrections computed here- the elimination-degree ratio i
- H-ICEX-e1c3b6 | proposed | RQ-JINV-8fc13a | 
- H-ICINV-0715b6 | specified | RQ-ICINV-475b5e | Stage 0 endomorphism-representation cost delta sqrt disc end identities — n=3 — before any later stage is authorized 
- H-ICINV-23c59a | specified | RQ-ICINV-475b5e | Stage 0 class extremal budget gating lane asking identities — n=3 — before any later stage is authorized 
- H-ICINV-2ac450 | specified | RQ-ICINV-475b5e | Stage 0 existential circuit pullbacks transported factor-base membership identities — n=2 — before any later stage is authorized 
- H-ICINV-492715 | specified | RQ-ICINV-475b5e | Stage 0 global address all-or-nothing free part exactly identities — n=4 — before any later stage is authorized 
- H-ICINV-52d311 | specified | RQ-ICINV-475b5e | Stage 0 isogeny-class relation aggregation exactly cost-neutral stays identities — n=2 — before any later stage is authorized 
- H-ICINV-6c7920 | rejected_scoped | RQ-ICINV-475b5e | 
- H-ICINV-6d1b45 | specified | RQ-ICINV-475b5e | Stage 0 whole f-v-free panel factor just elimination identities — n=3 — before any later stage is authorized 
- H-ICINV-82ee6a | analyzed | RQ-ICINV-475b5e | 
- H-ICINV-83d798 | specified | RQ-ICINV-475b5e | Stage 0 certified exhaustive isogeny-class search prime-field curve identities — n=3 — before any later stage is authorized 
- H-ICINV-8ba1f6 | specified | RQ-ICINV-475b5e | Stage 0 fourier flatness coordinate-defined factor base functional identities — n=3 — before any later stage is authorized 
- H-ICINV-9d04af | specified | RQ-ICINV-475b5e | Stage 0 exact transported-walk coupling separates coordinate rules identities — n=2 — before any later stage is authorized 
- H-ICINV-9ed4f0 | specified | RQ-ICINV-475b5e | Stage 0 class torsor cost functional fourier spectrum identities — n=3 — before any later stage is authorized 
- H-ICINV-b78126 | specified | RQ-ICINV-475b5e | Stage 0 one-sided transport envelope detectable endpoint cost identities — n=2 — before any later stage is authorized 
- H-ICINV-b81659 | proposed | RQ-ICINV-475b5e | The number r of F_p-roots of x^3 + a x + b is a gauge-invariant, class-varying, locally computable invariant that stratifies the Semaev solving-degree proxy within a sing
- H-ICINV-b96cc7 | proposed | RQ-ICINV-475b5e | 
- H-ICINV-d5e351 | refined_scoped | RQ-ICINV-475b5e | 
- H-ICINV-dd38db | specified | RQ-ICINV-475b5e | Stage 0 isogeny-class invariants argue difficulty uniform themselves identities — n=2 — before any later stage is authorized 
- H-ICINV-e6efa4 | specified | RQ-ICINV-475b5e | Stage 0 transport modulus detectable endpoint cost valleys identities — n=2 — before any later stage is authorized 
- H-ICINV-f13517 | specified | RQ-ICINV-475b5e | Stage 0 five-curve elimination lead converted observation pre-registered identities — n=3 — before any later stage is authorized 
- H-INSTR-066027 | specified | RQ-INSTR-f8faa0 | Stage 0 lane committed verdicts exactly attainable outcome identities — n=4 — before any later stage is authorized 
- H-INSTR-2c5606 | specified | RQ-INSTR-f8faa0 | Stage 0 control battery power matrix measured deliberately identities — n=3 — before any later stage is authorized 
- H-INSTR-444c7b | specified | RQ-INSTR-f8faa0 | 
- H-INSTR-62822b | specified | RQ-INSTR-f8faa0 | Stage 0 headline number whose producing code path identities — n=4 — before any later stage is authorized 
- H-INSTR-814852 | specified | RQ-INSTR-f8faa0 | Stage 0 matched names family different nulls question identities — n=3 — before any later stage is authorized 
- H-INSTR-a648c2 | specified | RQ-INSTR-f8faa0 | Stage 0 frozen protocol requires comparison quantity nobody identities — n=3 — before any later stage is authorized 
- H-INSTR-b7072d | specified | RQ-INSTR-f8faa0 | Stage 0 glv decomposition accepted constant-factor speedup nobody identities — n=2 — before any later stage is authorized 
- H-INSTR-beaccd | specified | RQ-INSTR-f8faa0 | Stage 0 cost number campaign comes machine never identities — n=2 — before any later stage is authorized 
- H-INSTR-d04b9c | proposed | RQ-INSTR-f8faa0 | 
- H-INSTR-ebb306 | proposed | RQ-INSTR-f8faa0 | 
- H-INSTR-fb662a | specified | RQ-INSTR-f8faa0 | Stage 0 lane buys detection resolution eighth power identities — n=3 — before any later stage is authorized 
- H-INSTR-fffbfb | supported_scoped | RQ-INSTR-f8faa0 | 
- H-ISOU-c5bfea | specified | RQ-ECDLP-002 | 
- H-IT-001 | weakened | RQ-ECDLP-002 | 
- H-JINV-0e8819 | proposed | RQ-JINV-8fc13a | Setting a = 0 (j = 0) or b = 0 (j = 1728) in the Semaev decomposition system is a support and coefficient reduction on the UNSPECIALISED polynomial and NOTHING on the spe
- H-JINV-1e7068 | specified | RQ-JINV-8fc13a | Stage 0 cell unit measurement lane reporting single identities — n=3 — before any later stage is authorized 
- H-JINV-1f0b8b | specified | RQ-JINV-8fc13a | Stage 0 place program aut separates d-0 depth-1 identities — n=2 — before any later stage is authorized 
- H-JINV-28621d | specified | RQ-JINV-8fc13a | Stage 0 direct answer lossy-projection failure stop measuring identities — n=2 — before any later stage is authorized 
- H-JINV-3a5637 | specified | RQ-JINV-8fc13a | Stage 0 crater cardinality d-0 structure genus theory identities — n=2 — before any later stage is authorized 
- H-JINV-434c3e | specified | RQ-JINV-8fc13a | Stage 0 small d-0 gives smaller horizontal crater identities — n=2 — before any later stage is authorized 
- H-JINV-4aff25 | specified | RQ-JINV-8fc13a | Stage 0 fractional part hurwitz mass free exact identities — n=4 — before any later stage is authorized 
- H-JINV-51b60c | specified | RQ-JINV-8fc13a | Stage 0 matched-order family representative-selection procedure itself correlate identities — n=4 — before any later stage is authorized 
- H-JINV-5a0b9e | specified | RQ-JINV-8fc13a | 
- H-JINV-5cb494 | specified | RQ-JINV-8fc13a | Stage 0 endomorphism claw priced covolume identity small identities — n=2 — before any later stage is authorized 
- H-JINV-704e55 | specified | RQ-JINV-8fc13a | Stage 0 gate worked end class admits committed identities — n=2 — before any later stage is authorized 
- H-JINV-784ddf | specified | RQ-JINV-8fc13a | Stage 0 special-j curves excluded control program automorphism identities — n=2 — before any later stage is authorized 
- H-JINV-b3b975 | specified | RQ-JINV-8fc13a | Stage 0 verdict degeneration divisor decided counting rather identities — n=2 — before any later stage is authorized 
- H-JINV-bfacc0 | specified | RQ-JINV-8fc13a | Stage 0 twist-pair identity zero-noise instrument test campaign identities — n=2 — before any later stage is authorized 
- H-JINV-db2776 | proposed | RQ-JINV-8fc13a | 
- H-JINV-dfddfa | specified | RQ-JINV-8fc13a | Stage 0 lane yardstick unmeasured double-counted rq-jinv-8fc13a decision-target identities — n=3 — before any later stage is authorized 
- H-JINV-f058eb | specified | RQ-JINV-8fc13a | Stage 0 sextic-twist family curve supplies six distinct identities — n=3 — before any later stage is authorized 
- H-JINV-f73bb6 | specified | RQ-JINV-8fc13a | Stage 0 discharging outcome stated computation classes orbit identities — n=3 — before any later stage is authorized 
- H-JINV-fde335 | specified | RQ-JINV-8fc13a | Stage 0 arithmetic half lane measured design removes identities — n=2 — before any later stage is authorized 
- H-PFDR-6b9f1a | proposed | RQ-JINV-8fc13a | 
- H-PFDR-9c5065 | proposed | RQ-JINV-8fc13a | A nondegenerate self-pairing would recover the secret outright, which is exactly why it is forced trivial: Galois equivariance puts t_N(P, P) in the intersection of the N
- H-PFDR-df0127 | proposed | RQ-JINV-8fc13a | 
- H-PFDR-ebec07 | proposed | RQ-JINV-8fc13a | 


## Existing proposals in these lanes (id | status | question | title) -- DO NOT DUPLICATE

- IDEA-20260807-070d03 | proposed | RQ-GGMB-6eaabc | THE FACTOR-BASE MEMBERSHIP ORACLE, ADJUDICATED PROPERLY: it is the one place index calculus genuinely leaves the generic group model, and it is nevertheless worthless, be
- IDEA-20260807-0a3272 | proposed | RQ-ICINV-475b5e | A CANDIDATE FUNCTIONAL WITH A CLASS-VARYING CAUSE THE DECOMPOSITION'S T4 LIST OMITS: the GROUP STRUCTURE of E(F_p) varies inside an isogeny class even though its ORDER do
- IDEA-20260807-0ff796 | proposed | RQ-ICINV-475b5e | CLOSURE WITH A NAMED OBSTRUCTION: length-2 relation yield and factor-base decomposition probability are EXACT isogeny-class invariants in the mean, because the Semaev rel
- IDEA-20260807-1c14d7 | proposed | RQ-INSTR-f8faa0 | COMPLETENESS OF AN ENUMERATED ISOGENY CLASS IS A WEIGHTED CARDINALITY CHECK AND THAT IS NOT ENOUGH: the committed Hurwitz-Kronecker census validates the enumerator agains
- IDEA-20260807-257001 | proposed | RQ-INSTR-f8faa0 | A TRANSPORT CERTIFICATE THAT DOES NOT RE-RUN VELU: certify the transported instance rather than the map, by (i) recomputing the target curve's trace with an independent c
- IDEA-20260807-34754f | proposed | RQ-INSTR-f8faa0 | THE CAMPAIGN'S ISOGENY-CLASS NULL, DEFINED: replace the free label-permutation null with a nested variance-components design whose permutation is stratified on the group 
- IDEA-20260807-413fcc | proposed | RQ-GGMB-6eaabc | CLOSURE WITH A NAMED OBSTRUCTION -- the zero-information oracle class: any oracle whose answer is a function of the curve data and adversary-supplied field elements alone
- IDEA-20260807-427cf3 | proposed | RQ-ICINV-475b5e | THE FINEST ALGEBRAIC FUNCTIONAL IN THE LANE, AND A DERIVATION THAT FORCES IT: the Macaulay rank profile and Hilbert function of the Semaev decomposition ideal are determi
- IDEA-20260807-477e40 | proposed | RQ-JINV-8fc13a | Decide, by exact symbolic support computation rather than by timing, whether setting a=0 (j=0) or b=0 (j=1728) in the Semaev decomposition system is a DEGREE reduction, a
- IDEA-20260807-51675e | proposed | RQ-JINV-8fc13a | The affected-versus-safe scope audit for L3, built on the observation that deciding "is |D_0| one of the nine class-number-one discriminants" costs NINE INTEGER SQUARE TE
- IDEA-20260807-569c82 | proposed | RQ-GGMB-6eaabc | THE PAIRING ORACLE IS THE CONSTANT ORACLE ON A PRIME-ORDER SUBGROUP, AND NO CM ENDOMORPHISM CAN RESCUE IT: the Weil pairing is alternating so e(R,S) = 1 identically on G 
- IDEA-20260807-5876b8 | proposed | RQ-GGMB-6eaabc | THE ORACLE-FRAMING COLLAPSE: because a prime-field ECDLP instance is fully specified by public data, every realizable augmenting oracle is either GGM-simulable (hence clo
- IDEA-20260807-5ddd98 | proposed | RQ-GGMB-6eaabc | THE ADJUDICATOR'S CONTROL CATALOGUE AND THE EMPTINESS OBSERVATION: a four-quadrant two-directional control set for the L12 instrument, whose most informative entry is the
- IDEA-20260807-63056d | proposed | RQ-GGMB-6eaabc | THE L12 ADJUDICATION PROCEDURE: a six-question decision tree with a fixed verdict alphabet, a mandatory witness artifact per verdict, and a declared ceiling of one hour o
- IDEA-20260807-692e9b | proposed | RQ-ICINV-475b5e | IS THE PROGRAM'S OWN CENTRAL QUANTITY A CLASS INVARIANT? Measure the H-PSEUDO factor-base flatness constant C(E) across a complete isogeny class, against the FIELD-SIDE a
- IDEA-20260807-6eb96b | proposed | RQ-ICINV-475b5e | THE CONTROL THIS LANE CANNOT BE RUN WITHOUT: the matched null for a within-class variance measurement is the GAUGE ORBIT of one curve -- the (p-1)/2 Weierstrass equations
- IDEA-20260807-7270d1 | proposed | RQ-GGMB-6eaabc | GRADED SIMULABILITY BY EXISTENTIAL WIDTH: the formal-linear-form simulator for an oracle whose answer is an existential over a candidate set of size Z errs with probabili
- IDEA-20260807-778375 | proposed | RQ-JINV-8fc13a | Small |D_0| makes the Hilbert class polynomial, the CM ideal factorisation of (pi - 1), and Lenstra's O-module structure E(F_p) = O/(pi-1) all cheaply COMPUTABLE - and th
- IDEA-20260807-7c00e6 | proposed | RQ-ICINV-475b5e | FILED AS A RECORDED CLOSURE, INADMISSIBLE ON ITS FACE: transporting one ECDLP instance to every member of its isogeny class and combining the resulting ensemble adds no c
- IDEA-20260807-899c5e | proposed | RQ-INSTR-f8faa0 | THE SOLVING-DEGREE METER CARD: sympy reports the maximum total degree of the REDUCED Groebner basis, which is a property of the OUTPUT and is neither an upper nor a lower
- IDEA-20260807-8b9486 | proposed | RQ-ICINV-475b5e | THE ONLY WITHIN-CLASS VARIATION OF THE SUMMATION-POLYNOMIAL COEFFICIENT STRUCTURE, LOCATED EXACTLY AND CAPPED EXACTLY: the support of S_m is a function of the vanishing p
- IDEA-20260807-94f953 | proposed | RQ-JINV-8fc13a | At small |D_0| the isogeny crater has exactly h(D_0) vertices, so for the nine class-number-one discriminants it is a SINGLE curve whose address is free - which simultane
- IDEA-20260807-9fb27c | proposed | RQ-ICINV-475b5e | THE sqrt-VELU COST-MODEL RE-AUDIT, AND WHY THE KNIFE EDGE IS ILLUSORY: the minimal non-scalar endomorphism of an ordinary E/F_p has degree d = |D|/4 ~ p, so a naive appli
- IDEA-20260807-a3d644 | proposed | RQ-JINV-8fc13a | The matched-null battery for "special j", including the fact that an exact (p, N, cofactor) match across different D_0 is IMPOSSIBLE by T4 so the null must be built throu
- IDEA-20260807-a4f5c5 | proposed | RQ-INSTR-f8faa0 | FAULT-INJECTION TESTING OF THE CERTIFICATE AND RUN-RECORD PIPELINE: the campaign's certificate discipline has never been exercised, because every run it has produced carr
- IDEA-20260807-bfa86b | proposed | RQ-JINV-8fc13a | The POSITIVE control for lane L3 - plant a known-answer sub-birthday weakness and require the instruments to find it at the predicted cost, because an instrument that can
- IDEA-20260807-c015f5 | proposed | RQ-INSTR-f8faa0 | A DECAY-PARAMETER TABLE FOR ALL FOURTEEN LANES, ANCHORED BY A CLOSED-FORM NULL FOR THE ONE DECAY TEST THE CAMPAIGN HAS ALREADY RUN: the windowed liftable-count within-cla
- IDEA-20260807-c36472 | proposed | RQ-ICINV-475b5e | THE T5 REACHABILITY GATE, RE-COSTED AND THEN MEASURED: transporting a specified class member is AFFORDABLE at Otilde(p^{1/4}), so T5 does not die on transport cost as DEC
- IDEA-20260807-caf061 | proposed | RQ-INSTR-f8faa0 | THE CAMPAIGN'S DETECTION FLOOR AND ITS ADJUDICATION CONTRACT: one committed run already reports 37 statistical verdicts with no multiplicity accounting, so about 1.9 fals
- IDEA-20260807-d329e2 | proposed | RQ-JINV-8fc13a | Index the factor base by the Aut-QUOTIENT coordinate on special-j curves (w = y^2 for j=0, w = x^2 for j=1728) and derive the resulting summation polynomial: the derivati
- IDEA-20260807-d73e83 | proposed | RQ-GGMB-6eaabc | THE ISOGENY-TRANSPORT ORACLE IS A RELABELING: an explicit generic-group simulator answers phi(P), phi(Q) queries at O(1) amortized cost per query by issuing fresh labels 
- IDEA-20260807-dc14b4 | proposed | RQ-ICINV-475b5e | A ZERO-COMPUTE DECISION PROCEDURE THAT PREDICTS EVERY L1 MEASUREMENT BEFORE IT IS RUN: a cost functional is isogeny-class invariant whenever it factors through the ISOGEN
- IDEA-20260807-efc8de | proposed | RQ-INSTR-f8faa0 | THE PLANTED-SIGNAL POSITIVE CONTROL, INJECTED INTO THE REAL PIPELINE: three planted families -- a synthetic per-class offset that yields a per-functional minimum detectab
- IDEA-20260807-f00729 | proposed | RQ-JINV-8fc13a | CLOSURE with a named obstruction: the automorphism quotient E -> E/Aut is a lossy projection that is NOT a group homomorphism - the orbit of P+Q is not determined by the 
- IDEA-20260807-f6137c | proposed | RQ-INSTR-f8faa0 | CLOSURE: three instruments this campaign should not build, each with a named obstruction, an argument and forward guidance -- a "true degree of regularity" meter for Sema
- IDEA-20260807-f8a045 | proposed | RQ-JINV-8fc13a | Charge the j=0 / j=1728 automorphism gain in the RELATION SYSTEM exactly: one successful decomposition on a mu_k-stable factor base yields |Aut|/2 relations and permits a
- IDEA-20260807-fd2d89 | proposed | RQ-GGMB-6eaabc | THE CANONICAL-HEIGHT ORACLE IS NON-SIMULABLE AND QUANTITATIVELY USELESS, AND CM MAKES IT WORSE RATHER THAN BETTER: any lift in which the height data depends on k must sat
- IDEA-20260808-031a59 | proposed | RQ-ICINV-475b5e | Isogeny-class relation aggregation is exactly cost-neutral, and it stays cost-neutral even if transport between curves is free: collecting relations on all h ~ sqrt(p) cu
- IDEA-20260808-45af43 | proposed | RQ-JINV-8fc13a | The sextic-twist family of a j=0 curve supplies SIX distinct group orders - exactly the second modulus whose absence is the named obstruction O-ONEMODULUS - and it still 
- IDEA-20260808-8aaddb | proposed | RQ-INSTR-f8faa0 | A headline number whose producing code path CRASHES on the recorded inputs is undetectable today: an executable-provenance checker that re-runs the named path on the RECO
- IDEA-20260808-90c7ab | proposed | RQ-INSTR-f8faa0 | Two committed ledger records were rewritten in place 93 minutes after archival, in a commit that added no run record — so the detector is a CONSERVATION LAW, not a diff: 
- IDEA-20260808-b3c97b | proposed | RQ-INSTR-f8faa0 | Four fabricated artifact hashes passed reviewer, validator AND red team undetected, so the review pipeline is itself an uncalibrated instrument: a defect ladder built fro
- IDEA-20260811-18bbf9 | proposed | RQ-JINV-8fc13a | THE SHAM CURVE - a null object of the same SHAPE as a special-j Semaev system but with no curve behind it: take a generic curve's S_m and delete exactly the monomials tha
- IDEA-20260811-22b6b8 | proposed | RQ-JINV-8fc13a | THE T5 GATE, WORKED END TO END IN THE ONE CLASS THAT ADMITS IT - the committed p = 4001, t = 30 class contains exactly one degeneration vertex (j = 2257) among 138, and m
- IDEA-20260811-245481 | proposed | RQ-ICINV-475b5e | THE FIVE-CURVE ELIMINATION LEAD, CONVERTED FROM AN OBSERVATION INTO A PRE-REGISTERED NUMBER BEFORE ANY SUCCESSOR CONTRACT IS WRITTEN: if I_3 intersect F_p[x_3] is the cur
- IDEA-20260811-332ce9 | proposed | RQ-JINV-8fc13a | DISCHARGING IDEA-20260807-18d2f7 OUTCOME 2 FOR TWO STATED COMPUTATION CLASSES: an orbit invariant for an endomorphism alpha is a rational function f on E with deg(f o alp
- IDEA-20260811-34f29d | proposed | RQ-JINV-8fc13a | IS THE DEGENERATION GEOMETRIC OR ONLY COMBINATORIAL? Measure the SINGULAR LOCUS of the Semaev hypersurface S_m = 0 at each of the eight j-line degeneration loci - dimensi
- IDEA-20260811-3e08e0 | proposed | RQ-JINV-8fc13a | THE T5 VERDICT ON THE DEGENERATION DIVISOR, DECIDED BY COUNTING RATHER THAN BY WALKING - each weight-12 locus is EXACTLY ONE QUADRATIC-TWIST PAIR (p - 1 points in the (a,
- IDEA-20260811-444b45 | proposed | RQ-ICINV-475b5e | THE GLOBAL ADDRESS IS NOT ALL-OR-NOTHING, AND THE FREE PART IS EXACTLY mu - 1 BITS. Castryck-Houben-Vercauteren (KN-LIT-1013) evaluate the ASSIGNED CHARACTERS of the unkn
- IDEA-20260811-473c2e | proposed | RQ-JINV-8fc13a | THE ARITHMETIC HALF OF THIS LANE, MEASURED WITH THE ONE DESIGN THAT REMOVES ITS CONFOUND - fix N = 19507 and vary the trace, so D = (t-2)^2 - 4N sweeps 46 DISTINCT fundam
- IDEA-20260811-5e58dc | proposed | RQ-ICINV-475b5e | THE CLASS EXTREMAL BUDGET: the gating lane has been asking a SIGNIFICANCE question ("does within-class variance beat the null?") when the decision-relevant quantity is an
- IDEA-20260811-6034d0 | proposed | RQ-JINV-8fc13a | THE ONLY DEGENERATION THAT WOULD SURVIVE THE LOSSY-PROJECTION TEST - REDUCIBILITY. Support is cost-invisible (committed: -30.8% support, -0.44% time at j = 0) but a summa
- IDEA-20260811-6c893b | proposed | RQ-JINV-8fc13a | IS SEMAEV-SPECIAL ALSO ARITHMETICALLY SPECIAL? Each degeneration j is a FIXED rational number, so it defines ONE curve over Q whose reductions are a family indexed by p; 
- IDEA-20260811-7734c5 | proposed | RQ-ICINV-475b5e | FOURIER FLATNESS OF THE COORDINATE-DEFINED FACTOR BASE, THE FUNCTIONAL IDEA-20260807-0ff796 NAMES AS NOT CLOSED: the additive energy of F_V(E) = {P in E(F_p) : x(P) in V}
- IDEA-20260811-7a44a5 | proposed | RQ-JINV-8fc13a | THE LANE'S OWN YARDSTICK IS UNMEASURED AND DOUBLE-COUNTED: RQ-JINV-8fc13a's decision_target and GOAL-ENDO-001 pause condition P3 both use sqrt(6) as the calibration thres
- IDEA-20260811-97e244 | proposed | RQ-JINV-8fc13a | THE DIRECT ANSWER TO THE LOSSY-PROJECTION FAILURE - stop measuring support and measure the NEWTON POLYTOPE. A support drop moves a cost functional if and only if it remov
- IDEA-20260811-99cc67 | proposed | RQ-JINV-8fc13a | THE ONE PLACE IN THIS PROGRAM WHERE |Aut| SEPARATES FROM |D_0| - the depth-1 107-volcano at N = 19507, t = 211, p = 19717, D = -3*107^2, whose CRATER is a single j = 0 ve
- IDEA-20260811-9ba2aa | proposed | RQ-ICINV-475b5e | THE WHOLE f_V-FREE PANEL MAY FACTOR THROUGH E[2], NOT JUST THE ELIMINATION FAMILY: the singular locus of S_3 = 0 is the 2-torsion locus by the discriminant identity, so s
- IDEA-20260811-a7c1df | proposed | RQ-JINV-8fc13a | NAME THE OBJECT - the SEMAEV DEGENERATION DIVISOR on the j-line. Every factor of the form alpha*a^3 + beta*b^2 dividing a block of S_m coefficients cuts out the SINGLE ra
- IDEA-20260811-b2806a | proposed | RQ-GGMB-6eaabc | THE SIMULABILITY AUDIT OF THIS SESSION'S THREE NEW ORACLE CLASSES, PLUS THE BOUNDARY OF KN-FIND-b7e091 STATED WHERE IT ACTUALLY LIES: a curve-only local label and a genus
- IDEA-20260811-bbcd68 | proposed | RQ-JINV-8fc13a | THE TWIST-PAIR IDENTITY - a ZERO-NOISE instrument test the campaign already has the data for. Quadratic twisting is an involution carrying the isogeny class of trace t bi
- IDEA-20260811-c05798 | proposed | RQ-JINV-8fc13a | THE CLOSURE, WITH A NAMED OBSTRUCTION AND A TWO-LINE PROOF - O-SEMICONTINUITY. The Macaulay matrix of the Semaev system has entries polynomial in (a, b), so its rank is L
- IDEA-20260811-c72830 | proposed | RQ-ICINV-475b5e | THE ENDOMORPHISM-REPRESENTATION COST Delta(E) = N*sqrt(|disc End(E)|)/(2 pi): the campaign's FIRST class-varying cost functional that is exponent-scale (it varies by the 
- IDEA-20260811-cd7c10 | proposed | RQ-JINV-8fc13a | THE FRACTIONAL PART OF THE HURWITZ MASS IS A FREE, EXACT DETECTOR FOR SPECIAL-|Aut| VERTICES - since the Deuring mass is the sum of 2/|Aut| over the class, it is an INTEG
- IDEA-20260811-d7856a | proposed | RQ-JINV-8fc13a | IS THE DEGENERATION DIVISOR A PROPERTY OF THE CURVE OR OF THE COORDINATE? Translate the x-line by a constant - the one model change that EVERY curve admits, unlike Montgo
- IDEA-20260811-df6c0f | proposed | RQ-JINV-8fc13a | "SPECIAL j" HAS TWO INEQUIVALENT MEANINGS IN THIS LANE AND THEY ARE DISJOINT - five of the six Semaev degeneration j-values are NON-INTEGRAL RATIONALS (55296/5, 55296/59,
- IDEA-20260811-e1ae92 | proposed | RQ-JINV-8fc13a | j IS LITERALLY THE ORDER OF THE CHEAP SYMMETRY GROUP OF THE x-LINE, AND THE LANE IS USING ONLY A THIRD OF IT: the Mobius transformations of P^1 = E/{+-1} induced by curve
- IDEA-20260811-faf43c | proposed | RQ-INSTR-f8faa0 | A FROZEN PROTOCOL THAT REQUIRES A COMPARISON AGAINST A QUANTITY NOBODY EVER RECORDED IS UNEXECUTABLE BY CONSTRUCTION, AND THIS CAMPAIGN HAS PRODUCED THE PATTERN MORE THAN
- IDEA-20260812-c49409 | proposed | RQ-ECDLP-912694 | The automorphism locus of an ordinary F_p-isogeny class is ONE vertex, it is reached by VERTICAL ascent rather than horizontal search, and the sqrt(3) rho discount waitin
- IDEA-20260815-6c956e | proposed | RQ-JINV-8fc13a | SPECIAL-j CURVES ARE EXCLUDED FROM EVERY CONTROL IN THIS PROGRAM AS AUTOMORPHISM ARTIFACTS: measure what they actually do, since a systematically excluded family is a sys
- IDEA-20260815-6d4580 | proposed | RQ-ICINV-475b5e | ISOGENY-CLASS INVARIANTS ARE USED TO ARGUE DIFFICULTY IS UNIFORM, BUT THE INVARIANTS THEMSELVES ARE NEVER MEASURED ACROSS A CLASS: enumerate a full small isogeny class an
- IDEA-20260815-c4a653 | proposed | RQ-INSTR-f8faa0 | EVERY COST NUMBER IN THIS CAMPAIGN COMES FROM ONE MACHINE AND THE CAMPAIGN HAS NEVER MEASURED ITS OWN MACHINE VARIANCE: run the standard battery on a second machine and r
- IDEA-20260815-e0b239 | proposed | RQ-INSTR-f8faa0 | GLV DECOMPOSITION IS ACCEPTED AS A CONSTANT-FACTOR SPEEDUP AND NOBODY HAS MEASURED WHETHER THE CONSTANT IMPROVES POLLARD RHO'S WALK RATHER THAN JUST ITS ARITHMETIC
- IDEA-20260815-f7d8eb | proposed | RQ-GGMB-6eaabc | THE GENERIC GROUP BOUND IS QUOTED AS A BARRIER BUT EVERY INTERESTING METHOD LEAVES THE MODEL: enumerate the exact model extensions each known method requires and check wh
- IDEA-20260816-1c2177 | proposed | RQ-INSTR-f8faa0 | Reduce every leakage-or-fault assumption in this ledger to a five-slot predicate -- observable, granularity, error rate, observations per invocation, obtainability class 
- IDEA-20260816-2f049b | proposed | RQ-INSTR-f8faa0 | Before trusting any leak detector, measure its detection power as a surface: plant leaks of graded magnitude into an otherwise branch-free routine, sweep the plant size a
- IDEA-20260816-acdc1d | proposed | RQ-INSTR-f8faa0 | Instrument this repository's own Python routines with a bytecode-level event tracer and report the mutual information, in bits per invocation, between the emitted (branch
- IDEA-20260821-805cae | proposed | RQ-GGMB-6eaabc | THE CURVE-MEASURABLE CLOSURE IS STATED ON ARGUMENTS AND SAYS NOTHING ABOUT RANGE: coordinate-selected OUTPUT oracles CSEL(pi), which take no group handle and RETURN one c
- IDEA-20260826-2259f8 | proposed | RQ-JINV-8fc13a | THE d_reg METER READ 2 FLAT AND HAD NO DYNAMIC RANGE (EV-REP-001/002): replace it with a FIRST-FALL-DEGREE and Hilbert-staircase meter on the m=3 Semaev ideal and ask whe
- IDEA-20260826-228fa6 | proposed | RQ-ICINV-475b5e | THE CLASS IS A Cl(O)-TORSOR, SO A COST FUNCTIONAL ON IT HAS A FOURIER SPECTRUM: measure whether the committed within-class cost variation is concentrated on low-frequency
- IDEA-20260826-4bc5d2 | proposed | RQ-JINV-8fc13a | THE FACTOR-BASE INCIDENCE DEVIATION IS A DIFFERENT OBJECT FROM THE RELATION-YIELD MEAN: track the coordinate-placement discrepancy S_B(E) = #{P in G : x(P) in [0,B)} and 
- IDEA-20260826-d61c49 | proposed | RQ-JINV-8fc13a | SMALL |D_0| GIVES A SMALLER HORIZONTAL CRATER, NOT A LARGER ONE: track the curve identity (the Cl(O)-orbit position of j) under the CM class-group action as a genuinely l
- IDEA-20260828-2b2bb2 | proposed | RQ-JINV-8fc13a | THE "SMALL HEIGHT" AXIS OF THE RQ'S OWN TITLE IS UNTESTED: fix ONE small- integer global short-Weierstrass model (A,B) in Z, generically NON-CM, and track it through redu
- IDEA-20260828-b39886 | proposed | RQ-JINV-8fc13a | THE MATCHED-ORDER FAMILY'S (a,b)-REPRESENTATIVE-SELECTION PROCEDURE MAY ITSELF CORRELATE WITH |D_0|, AND H-JINV-5a0b9e DOES NOT AUDIT IT: before the pending Stage 1/2 run
- IDEA-20260828-f3c50e | proposed | RQ-JINV-8fc13a | THE CRATER'S CARDINALITY h(D_0) IS NOT ITS ONLY STRUCTURE: genus theory partitions the h(D_0) vertices into 2^{t-1} AMBIGUOUS (order-<=2 ideal class) vertices and the res
- IDEA-20260829-1859dd | proposed | RQ-INSTR-f8faa0 | THIS LANE BUYS DETECTION RESOLUTION AT THE EIGHTH POWER OF COMPUTE, AND NOBODY HAS WRITTEN THE EXPONENT DOWN: class size grows like p^{1/2} so the minimum detectable effe
- IDEA-20260829-28e420 | proposed | RQ-INSTR-f8faa0 | THE CONTROL BATTERY'S POWER MATRIX, MEASURED AGAINST DELIBERATELY BROKEN IN-SCOPE INSTRUMENTS: the campaign's committed positive control never touches a curve and its str
- IDEA-20260829-60be01 | proposed | RQ-INSTR-f8faa0 | "MATCHED AT THE SAME p" NAMES A FAMILY OF DIFFERENT NULLS AND THE QUESTION'S SCOPE DOES NOT SAY WHICH: make the MATCHING KEY -- the invariant vector a null sampler condit
- IDEA-20260829-882739 | proposed | RQ-ECDLP-912694 | THE EXIT BOUNDARY IS "ell DIVIDES f", NOT "ell = 3": because h(-3) = h(-4) = 1 the crater is a single vertex, so EVERY horizontal rational odd-degree isogeny from a speci
- IDEA-20260829-8bde84 | proposed | RQ-ECDLP-912694 | THE EXIT FAN IS COLLAPSED BY THE AUTOMORPHISM ITSELF: the group Aut(E) modulo plus-minus-one acts FREELY on the descending ell-isogeny kernels at a special-j crater, so t
- IDEA-20260829-920b16 | proposed | RQ-ECDLP-912694 | THE CM AUTOMORPHISM IS A FREE, PUBLIC, CONSTANT-TIME ORIENTATION - which is the one ingredient the self-pairing machinery (Castryck-Houben-Merz; Galbraith-Gilchrist-Rober
- IDEA-20260829-a250ee | proposed | RQ-ECDLP-912694 | THE RQ'S OWN THIRD CONTROL CELL IS PROVABLY EMPTY: for an ORDINARY curve over ANY finite field, End is commutative and contains Frobenius, so EVERY endomorphism - hence e
- IDEA-20260829-bd9f66 | proposed | RQ-INSTR-f8faa0 | FOUR OF THIS LANE'S COMMITTED VERDICTS HAVE EXACTLY ONE ATTAINABLE OUTCOME, SO `invariant` IS NOT IDENTIFIABLE: harness/run_icinv.py::analyse routes the group order N = p
- IDEA-20260901-054dd4 | proposed | RQ-JINV-8fc13a | THE CELL IS THE UNIT OF MEASUREMENT AND THIS LANE HAS BEEN REPORTING SINGLE CELLS. Special j is structurally n = 1 per prime - at most one D_0 = -3 class exists at each p
- IDEA-20260901-6b63a4 | proposed | RQ-JINV-8fc13a | A CHEAP ENDOMORPHISM CANNOT HAVE A SMALL ORBIT. For every ordinary E/F_p and every non-unit alpha in End(E) of norm n, the multiplicative order h of the scalar lambda_alp
- IDEA-20260901-c4730d | proposed | RQ-JINV-8fc13a | THE GROUP ORDER OF EVERY ORDINARY CURVE IS A VALUE OF ITS OWN CM FORM - 4 #E = (t-2)^2 + |D_0| f^2 - so every prime divisor of #E splits in Q(sqrt(D_0)) on EVERY curve, a
- IDEA-20260901-e4184f | proposed | RQ-JINV-8fc13a | THE ENDOMORPHISM CLAW, PRICED BY A COVOLUME IDENTITY. Small |D_0| supplies about sqrt(p/|D_0|) times MORE endomorphisms per norm bound than a generic curve, which is the 
- IDEA-20260901-f375a9 | proposed | RQ-JINV-8fc13a | THE SELF-PAIRING WOULD SOLVE THE INSTANCE OUTRIGHT, WHICH IS EXACTLY WHY IT IS TRIVIAL. Bilinearity gives t_N(Q, Q) = t_N(P, P)^{s^2} for Q = sP, so a nondegenerate compu
- IDEA-20260903-47f358 | None | RQ-ICINV-475b5e | Certified exhaustive isogeny-class search for a prime-field curve model whose point-decomposition presentation has a lower first-fall / root-finding degree
- IDEA-20260905-030f9e | proposed | RQ-ICINV-475b5e | A one-sided transport envelope for detectable endpoint cost valleys
- IDEA-20260905-77d3ae | proposed | RQ-ICINV-475b5e | A transport modulus for detectable endpoint cost valleys
- IDEA-20260906-01e1dc | proposed | RQ-ICINV-475b5e | Existential circuit pullbacks of transported factor-base membership
- IDEA-20260906-906dcc | proposed | RQ-GGMB-6eaabc | Coefficient-sketch canonicalizers for arithmetic scalar orbits
- IDEA-20260906-ffaab0 | proposed | RQ-ICINV-475b5e | Exact transported-walk coupling separates coordinate rules from class invariants