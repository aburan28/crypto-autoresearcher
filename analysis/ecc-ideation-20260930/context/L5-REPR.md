# Lane L5-REPR context (generated 2026-09-30 from committed ledger state; read-only)


## RQ-ECDLP-623a32  (ledger/questions/RQ-ECDLP-623a32.yaml)

```yaml
research_question:
  id: RQ-ECDLP-623a32
  title: >-
    Which representations of points on a prime-field elliptic curve -- outside the
    Kummer-line and degree-d-function-on-E paradigm already closed at model lever 1 --
    change the charged cost of a named ECDLP attack stage (factor-base membership,
    relation decomposition, collision structure, linear algebra, descent) rather than
    merely reparametrising it?
  scope:
    curve_families:
      - ordinary prime-order short-Weierstrass curves over F_p with generic j
      - CM and special-j curves only as explicitly labelled structured controls
      - matched random-curve and random-reparametrisation (PGL_2) null objects at the same p
    field_types: [prime]
    bit_sizes:
      - toy instances (p up to ~32 bits) for executable falsification only
      - symbolic and asymptotic models for scope statements
      - standardized public curves only when no secret scalar or live key is targeted
    methods:
      - R1 field representations of coordinates (integer, digit, quadratic-order residue, redundant)
      - R2 curve models and embeddings (theta and level-n normal forms, Jacobi intersections, Hessian, Edwards, Montgomery and Kummer as controls)
      - R3 non-function representations (elliptic nets, modular-curve and torsor coordinates, cubical and biextension lifts, E x E and Kummer-surface and gluing representations, Weil restriction and local-ring representations)
      - lossy-projection audit and one-step propagation measurement (the loss and branching meter of IDEA-20260802-002)
      - summation-polynomial and decomposition-system degree, Newton polytope, monodromy and solving-degree profiles
      - matched Pollard rho and BSGS controls before any attack-cost statement
  motivation: >-
    The model lane (RQ-MODEL-e61cb2) established at proposal level that every degree-2
    coordinate on a prime-order curve is a Moebius reparametrisation of the Kummer line
    (IDEA-20260807-8027a2, IDEA-20260807-e6d79e, IDEA-20260807-dadcd2) and that the model
    lever on the decomposition system is exactly 1 there; IDEA-20260808-2e14f7 extends the
    question to degree-d maps E -> P^1, and IDEA-20260806-0c9de1 and IDEA-20260808-fa1d80
    to torsor and abelian-surface representations. On user instruction (2026-09-05) genuinely
    new point representations -- ones the program has not yet considered -- become a
    standing avenue of GOAL-ECDLP-001. What is missing is a representation whose
    lossy-projection audit passes both clauses (it loses information and the retained part
    still propagates deterministically), or which changes a charged stage cost by a stated
    exponent or constant against a null object of the same shape.
  decision_target: >-
    For each candidate representation, decide with the cheapest discriminating test whether
    it (a) is a reparametrisation (the null battery reproduces every measurement), (b) changes
    a stage cost by a measured constant only, or (c) changes a degree, monodromy, Newton
    polytope or membership-description degree in a way that alters an end-to-end exponent
    under named, validated heuristics. Only (c) authorizes scaling work. A negative closes only
    the tested representation family and records its obstruction.
  constraints:
    - Lawful defensive cryptanalysis on public constructions and toy benchmarks only; no live keys, wallets or deployed systems.
    - Every representation proposal carries the lossy-projection audit of docs/inventor-protocol.md section 2 in the proposal itself, before any experiment.
    - The PGL_2(F_p) random-reparametrisation battery and the translation-conjugate null of IDEA-20260807-4fc635 are mandatory controls for any measurement attributed to a representation.
    - Generic-group lower bounds apply to any method that uses a representation only as a black-box group encoding; a proposal must name the non-generic operation the representation makes cheaper.
    - Pollard rho with distinguished points and BSGS are mandatory matched controls; on CM curves the automorphism-discounted rho baseline is the control (KN-TECH-018).
    - Every claimed solve or relation requires a certificate re-verified independently of the solver (docs/claims-and-verification.md).
    - Timeouts, crashes and infrastructure failures are never negative mathematical evidence (AGENTS.md rule 5).
    - 'Evidence from toy runs is capped at claim_tier: toy; no exponent claim without validated heuristics and full charging.'
  status: active
  owner: coordinator

```


## RQ-ECDLP-4fcbd3  (ledger/questions/RQ-ECDLP-4fcbd3.yaml)

```yaml
research_question:
  id: RQ-ECDLP-4fcbd3
  added: '2026-09-05'
  title: >-
    Does the coordinate bias of prime-field point addition carry discrete-log
    information, and can that information concentrate on a cheaply decidable
    structured subset so that a coordinate distinguisher leaks into key recovery
    below the square-root bound?
  scope:
    curve_families:
      - ordinary prime-order short-Weierstrass curves over F_p (the primary object)
      - cyclic even-order curves with one F_p-rational 2-torsion point (known-true
        positive control, where a coordinate predicate IS a group character)
      - small-embedding-degree subgroups where a Tate pairing with a fixed point is
        a cheap coordinate-computable group character (second known-true object,
        optional arm)
      - matched random curves of the same size and random-label walks as null objects
    field_types: [prime]
    bit_sizes:
      - toy instances (field_bits 12 to 24, prime-order subgroups up to about 2^24)
        for exhaustive discrete-log tabulation and executable falsification
      - symbolic character-sum models for the ceiling and the break-even statement
    methods:
      - exhaustive discrete-log tabulation and Fourier analysis over the group
        character basis (the DL-spectrum of a coordinate function)
      - r-adding walk transition operators, coordinate lumping, itinerary classes
      - factor-base sumset x-histograms and their additive-character transform
      - matched Pollard rho, BSGS, random-label and random-curve controls
  motivation: >-
    Point addition over F_p is a rational map of bounded degree; the x-coordinate of
    P+Q over structured inputs (factor-base sums, walk iterates) is not perfectly flat
    and the program has treated such deviations as noise. The proposal behind this lane
    is that a bias is information, and that if the walk's transition operator has an
    eigenvector correlated with something cheaply computable from coordinates, the
    result is a distinguisher, and a distinguisher for a hard-core predicate of the
    discrete log leaks into key recovery through the known bit-security reductions
    (KN-LIT-043, KN-LIT-5602, KN-LIT-4155). Two facts fix the shape of the question.
    (1) In the random-branch model of the additive walk the transition operator is a
    convolution on the cyclic group, its eigenvectors are exactly the group characters
    chi_a(W) = e(a*log_P(W)/N), and a correlation between an eigenvector and a cheap
    coordinate function is exactly a mixed character sum of Kohel-Shparlinski type,
    which is bounded at the Weil level c*deg*sqrt(p) for bounded-degree coordinate
    functions (recalled; unverified in this program). That is the wall the proposal
    itself names. (2) The counting in the wall as usually stated is off by a square:
    detecting a per-sample bias eps needs Theta(eps^-2) samples, so a Weil-level bias
    p^(-1/2) needs Theta(p) samples, worse than generic, and the bias that merely
    breaks even with rho is p^(-1/4). The escape therefore needs the bias to be
    concentrated by a factor p^(1/4) above the Weil level on some structured subset, of
    points or of frequencies. Whether any cheaply decidable subset does that is a
    question the ledger has not asked in this form: IDEA-20260830-c5c614 measures the
    target-side yield lift of x-line predicates and IDEA-20260905-afa907 measures a
    coupling defect of feature-only simulators, but neither computes the DL-spectrum
    of a coordinate function, the lumped spectrum of the real deterministic walk, or
    the itinerary-class concentration where the character-sum bound goes vacuous.
  decision_target: >-
    Either (a) record the coordinate-bias lane as closed at the character-sum ceiling
    with a MEASURED obstruction (the maximal DL-spectral spike of every cheap coordinate
    function in a frozen library, its decay slope in p, and the itinerary depth at
    which the bound is vacuous yet no concentration appears), with the two known-true
    objects shown to be detected by the same instrument; or (b) identify a cheaply
    decidable class of points or frequencies on a prime-order subgroup whose
    DL-concentration does not decay at the Weil rate, in which case the deliverable is
    a replication at a second scale and an independent review before any exploit
    cost is modelled. Toy-scale evidence authorizes scaling work only; it never
    satisfies GOAL-ECDLP-001 or GOAL-CRYPTO-001.
  constraints:
    - Lawful defensive cryptanalysis on self-generated toy curves only; no live keys,
      wallets, or deployed parameters are targeted.
    - The discrete logarithm of every point is tabulated at toy scale to COMPUTE the
      observables; no observable may use the logarithm as an input to the predicate it
      evaluates, and every predicate must be evaluable from coordinates at charged cost.
    - Every reported signal is an artifact until the identical measurement has been run
      on a null object of the same shape (random-label walk, random curve, random factor
      base) and a decay test in p has been passed (docs/inventor-protocol.md section 3).
    - Every known-true positive control (2-torsion descent character, pairing character)
      must be detected by the instrument, or the instrument is void.
    - Pollard rho and BSGS remain the mandatory cost baselines; any exploit cost derived
      from a measured concentration is a modelled number, labelled as such, never a claim.
    - Every claimed solve or relation carries a certificate re-verified independently
      of the producer (docs/claims-and-verification.md).
    - Timeouts, crashes and memory exhaustion are infrastructure outcomes, never
      negative mathematical evidence (AGENTS.md rule 5).
    - Evidence from this lane is capped at claim_tier toy until a medium-scale
      replication exists; no crypto-scale statement may be made from it.
  related_questions: [RQ-CRYPTO-001, RQ-ECDLP-002, RQ-EWALK-8fa147, RQ-FBG-001]
  goal_ids: [GOAL-ECDLP-001, GOAL-CRYPTO-001]
  status: active
  owner: coordinator

```


## RQ-ECDLP-c1b7b1  (ledger/questions/RQ-ECDLP-c1b7b1.yaml)

```yaml
research_question:
  id: RQ-ECDLP-c1b7b1
  added: '2026-09-05'
  title: >-
    Silverman's two lifting faces without an algorithm. Can the hard lift T^ = m S^
    be described succinctly and manipulated without writing its coordinates, and
    does any computable canonical non-homomorphic local section carry scalar
    information beyond the anomalous fragment?
  scope:
    curve_families:
      - >-
        ordinary cofactor-1 prime-order short-Weierstrass curves over F_p (the
        primary object, gcd(n, p) = 1)
      - >-
        anomalous toy curves with group order equal to p (the known-true object
        where the p-adic route is a linear-time attack; calibration only, never a
        target)
      - >-
        global models E^/Q with a small-height rational point S^ reducing to a
        generator S, for the explicit-lift arm
      - >-
        subgroups of small embedding degree as the second known-false object of the
        succinct-description dichotomy (named, not executed)
    field_types: [prime]
    bit_sizes:
      - >-
        toy, field_bits 10 to 20, for exhaustive discrete-log tabulation and
        p-adic work at precision 2 and 3
      - >-
        exact rational arithmetic on multiples m S^ up to m of a few hundred for the
        size law
      - symbolic models for the dichotomy, the class boundary and the scale statement
    methods:
      - >-
        Hensel and Teichmuller lifts, the unique homomorphic (torsion) section via
        multiplication by n and the formal parameter, formal logarithm to precision 3
      - >-
        the DL-spectrum census instrument of EXP-ECDLP-184fc4 applied to canonical
        p-adic digit functions
      - >-
        the Smart / Satoh-Araki / Semaev scalar recovery on anomalous toy curves as
        the instrument's positive control
      - exact big-rational multiples over Q with the naive height as the size proxy
  motivation: >-
    Of Silverman's four lifting faces (KN-LIT-6935a1, KN-TECH-06bb4e) two carry a
    concrete attempt and a named failure; the two others carry only an observation.
    Hard lifting (face F4b) has the observation that a lift T^ = m S^ of T exists
    and the unconditional bound h^(T^) = m^2 h^(S^), so any explicit T^ has
    coordinates of about p^2 bits at m of size p; no algorithm has ever been
    proposed and Silverman's closing question asks for a succinct or implicit
    description (straight-line program, arithmetic circuit) that could be
    manipulated without writing coordinates down. Almost nothing is written on
    that, in the literature or in this ledger (no proposal mentions the hard lift
    or the four faces by name; the August 7 canonical-lift closures name a
    compressed representation of high-height points as the most valuable open
    attack point, IDEA-20260807-6533fd and IDEA-20260807-cfe576 class (iii)).
    Local torsion (face F2) is circular: the unique n-torsion lift preserves
    T^ = m S^ and is a group isomorphism onto the original instance
    (KN-TECH-73630e), so multiplying into the formal group kills it and every
    group-theoretic invariant is constant; the one fragment that paid, the
    anomalous case #E = p, is fully worked out (KN-TECH-033, KN-LIT-087/088/089).
    What the ledger leaves open is exact: coordinate and valuation invariants of
    the torsion lift (KN-OPEN-3417fc, made falsifiable as ECDLP-IDEA-436 and never
    run), and a target-dependent non-torsion section whose formal-group defect
    lies in a compact family with a joint decoder (ECFG-P1543-R0/R1 in
    ledger/FINDING-PF-IC-001.md, disposition STRUCTURED_DEFECT_DECODER_UNCLASSIFIED;
    IDEA-20260807-cfe576 class (i)). This question binds the two faces through one
    identity: for gcd(n, p) = 1 the local points split as torsion section plus
    formal group, the global hard lift's formal-group component has logarithm
    m times a computable unit, and therefore any explicit lift leaks m through one
    p-adic digit while any description of T^ constructible from T alone is a
    function of T. The lane's open content is then (a) a derivation-level closure
    of the succinct-description route with its two known-false objects, and (b) a
    measurement of the canonical cheap digit functions (the Fermat-quotient digit of
    the Teichmuller lift, the torsion lift's second digit, and their defect) for
    discrete-log correlation, with the anomalous attack as the object on which the
    same instrument must read linear.
  decision_target: >-
    Either (a) record hard lifting as closed at the level of succinct descriptions
    by the decodability dichotomy (every polylog description of T^ constructible
    from (E^, S^, T) is polynomially equivalent to T or to (T, m)), with the
    identity and the size law verified on toy global lifts, and record the
    canonical p-adic digit functions as measured obstructions (white DL-spectra
    with the anomalous object reading linear on the same instrument); or (b) find
    a canonical cheap digit whose DL-spectrum concentrates on a non-decaying
    frequency set, which is the first computational handle in face F2 and triggers
    replication and independent review before any exploit is modelled. Toy-scale
    evidence authorizes scaling work only; it never satisfies GOAL-ECDLP-001 or
    GOAL-CRYPTO-001.
  constraints:
    - Lawful defensive cryptanalysis on self-generated toy curves and self-chosen
      global models only; no live keys, wallets or deployed parameters.
    - The scalar m is known to the instance generator and is used only to tabulate
      logs and to produce explicit global lifts for the size-law and leak arms; no
      predicate evaluated in a census may take m as an input.
    - Every p-adic quantity is reported with its precision, and every digit function
      charges the precision it was evaluated at; a result at precision k must agree
      with precision k + 1 truncated, or it is an instrument defect.
    - Every reported signal is an artifact until the identical measurement has been
      run on a null object of the same shape and a decay test in p has passed.
    - The anomalous control must reproduce the known linear-time recovery exactly,
      certified by [m]P = Q, or the instrument is void; a reproduced known attack is
      a calibration, never a result.
    - Pollard rho and BSGS remain the cost baselines; any cost derived from a
      measured concentration is a modelled number, labelled as such.
    - Timeouts, crashes and memory exhaustion are infrastructure outcomes, never
      negative mathematical evidence (AGENTS.md rule 5).
    - Evidence from this lane is capped at claim_tier toy until a medium-scale
      replication exists.
  related_questions: [RQ-ECDLP-4fcbd3, RQ-CANL-63098f, RQ-XEDN-001, RQ-CRYPTO-001, RQ-ECDLP-002]
  goal_ids: [GOAL-ECDLP-001, GOAL-CRYPTO-001]
  status: active
  owner: coordinator

```


## RQ-ECDLP-165d4b  (ledger/questions/RQ-ECDLP-165d4b.yaml)

```yaml
research_question:
  id: RQ-ECDLP-165d4b
  title: Prime-field non-generic hardness census
  scope:
    curve_families:
      - ordinary prime-order short-Weierstrass curves over F_p
      - CM and special-j candidates with a verified F_p-defined automorphism
      - bounded-degree F_p-rational isogeny neighbors of the above
    field_types:
      - prime_field
    bit_sizes:
      - 16
      - 20
      - 24
      - 28
      - 32
      - 36
    methods:
      - Pollard rho
      - negation quotient
      - automorphism quotient
      - charged isogeny transfer
  motivation: >-
    Prime-field status alone does not imply generic hardness. Known anomalous,
    pairing-friendly, and endomorphism-rich curves show that public structure
    can matter. The prior isogeny-transfer lane did not test the orbit-quotient
    form of this mechanism and did not preserve matched controls in its special-j
    summary.
  decision_target: >-
    Decide whether to prioritize endomorphism-orbit methods or short isogeny
    transfer as a live ECDLP research direction, while preserving the exact
    scope of any null result.
  constraints:
    - No hidden scalar-dependent advice or oracle access.
    - No uncharged precomputation, transfer, memory, or serialization.
    - Primary curves must be ordinary, prime-order, non-anomalous, and have
      declared embedding-degree and twist checks.
    - Toy and medium runs cannot be promoted to cryptographic-scale claims.
    - All positive observations require independent validation and red-team review.
  status: active
  owner: coordinator

```


## RQ-PFDR-ae2fba  (ledger/questions/RQ-PFDR-ae2fba.yaml)

```yaml
research_question:
  id: RQ-PFDR-ae2fba
  title: >-
    For prime-field ECDLP (E/F_p, no Weil descent, exemplar P-256), does any
    representation or factor-base definition make the Semaev point-decomposition
    systems simultaneously LOW-DEGREE (solving degree / first-fall degree bounded
    or growing strictly slower than the support-matched semi-regular null) and
    USEFUL (decomposition probability high enough that relation collection plus
    linear algebra beats Pollard rho), and is that degree-versus-yield tradeoff
    exponent-relevant rather than a constant?
  scope:
    curve_families:
      - generic prime-field short-Weierstrass curves E/F_p, >=3 curves per cell
      - alternative models of the same curves (Montgomery, twisted Edwards,
        Jacobi quartic, Hessian) used only as representations, never as a
        change of curve
    field_types: [prime field F_p]
    bit_sizes:
      - "toy: log2 p in 12..40 for full decomposition and solve cells"
      - "sampling / correspondence cells: system shapes scaled to 64..256-bit
        proxies with no curve constructed (per IDEA-20260731-009 discipline)"
      - "symbolic: asymptotic degree bookkeeping stated per representation"
    methods:
      - Semaev summation polynomials S_3 and S_4 (S_m, m>=5 only if a cell
        already costed at m=3,4 motivates it), symmetrized and unsymmetrized
      - factor bases defined by x-coordinate intervals, algebraic subsets
        (images of low-degree maps, torsion and isogeny structure, endomorphism
        orbits), and representation-specific coordinates
      - Groebner / XL / resultant elimination with first-fall degree d_ff,
        solving degree d_reg, and Macaulay-rank deficit measured against a
        support-matched semi-regular null (T11 discipline from RQ-DREG-001)
      - decomposition-yield counting with matched random-base control and
        permutation null (RQ-FBG-001 discipline)
  motivation: >-
    RQ-DREG-001 asks the degree-of-regularity question for the BINARY Weil-
    descent Semaev system, where the factor base is fixed by the descent
    (H-DREG-001, EV-DREG-001..003: deficit series 1,322/1,862/1,823/1,999 at
    n=12/15/17/18, no d_reg reached at D=5; KN-FIND-006: the excess is 8*dim V
    of structural syzygies over the Frobenius+Koszul generic baseline). Over a
    prime field there is no descent, so the factor base is not given and every
    proposed one has its own polynomial system. The program's current state on
    the prime-field side is: (i) with set-theoretic membership f_V of degree B
    the semi-regular reference is d_reg = ceil((m(B-1)+D_S)/2), linear in B
    (IDEA-20260808-093497), the ideal is CRT-degenerate at every arity
    (IDEA-20260830-cb8e46), hybrid guessing dominates the algebra
    (IDEA-20260808-da1428), and the committed "d_reg = 2 flat" readings of
    EV-REP-001/002 were a Groebner-output proxy with no dynamic range
    (IDEA-20260807-1354d8); (ii) any factor base cut out by a low-degree
    target-independent locus is Bezout-bounded (IDEA-20260801-021,
    KN-OPEN-020), so the escapes are auxiliary-variable descriptions
    (IDEA-20260830-84cdb7, the base-d digit map, whose H1 "d_ff bounded in the
    digit length" is unmeasured), lattice-describable windows
    (IDEA-20260808-486ae2, IDEA-20260808-e2315e), sparse binomial cosets
    (IDEA-20260808-9ef88c) and implicit membership (IDEA-20260902-701458);
    (iii) mean decomposition yield is conserved across base geometries
    (KN-FIND-007, EV-FBG-001), so "useful solutions" is fixed by |V| and the
    arity window, and the only quantity a representation can move is the
    charged cost of finding them (sigma of IDEA-20260808-812554, which must be
    below 1 - 2/(m-1)); (iv) the one recorded prime-field early fall, d_ff <
    D_reg on a symmetric m=3 representation (EV-ALPF-001 / EXP-ALPF-011), was
    never replicated under a validated meter with a matched null, and the
    shared S_4 instrument carries a confirmed defect (KN-OPEN-5b3a08). The
    bottleneck for P-256-class curves is therefore not writing down S_3 or
    S_4 but finding a representation in which the systems stay low-degree AND
    retain useful solutions, with both columns measured on the same base.
    RQ-SDEG-001 holds the scaling law of the direct presentation and
    RQ-FBG-001 the yield column; the coupled per-representation table has no
    host record. This one holds it.
  decision_target: >-
    A per-representation table of (d_ff, d_reg or its lower bound, Macaulay
    deficit vs null, decomposition probability, per-relation cost) with growth
    arms in log2 p, and a decision on whether ANY representation exhibits a
    degree deficit or yield advantage that grows with p (alive: feeds a costed
    relation-collection contract) or all effects are constant / tracked by the
    null (scoped kill of the representation channel for prime-field
    decomposition at the tested scale).
  constraints:
    - Toy scale only for solve cells; no crypto-scale claim regardless of
      outcome (AGENTS.md rules 4 and 6); every cell states its curves, p,
      base, solver, and budget.
    - A degree measurement without a matched yield measurement on the same
      base, and vice versa, is a half-cell and does not enter the decision
      table.
    - Support-matched semi-regular null and matched random base are mandatory
      controls; subset-column ranks are not evidence (RQ-DREG-001 finding iv).
    - Pollard rho on the same toy curves is the mandatory matched cost control.
    - Timeouts, OOM, and solver crashes are failed_infrastructure, never
      evidence (AGENTS.md rule 3).
    - Lawful defensive cryptanalysis on public toy curves only; no live keys.
  status: active
  owner: coordinator
  related_questions: [RQ-DREG-001, RQ-SDEG-001, RQ-FBG-001, RQ-MODEL-e61cb2, RQ-ECDLP-002]
  related_open_problems: [KN-OPEN-002, KN-OPEN-003, KN-OPEN-020, KN-OPEN-5b3a08]

```


## goal head GOAL-ECDLP-bbc21f
```
# GOAL-ECDLP-bbc21f — head projection from ledger/goals/GOAL-ECDLP-bbc21f/goal.yaml
# Resume fields only; ad-hoc keys and checkpoint bodies are not shown.

id: GOAL-ECDLP-bbc21f
status: active
title: 'Batch ECDLP with precomputation: fewer stored distinguished points at fixed online cost'
current_batch_id: null
dispatch_queue_path: coordination/goals/GOAL-ECDLP-bbc21f/batches/BATCH-e9fd22/dispatch_queue.json
next_action: 'RANK 1 (the ONE next action; this goal''s ranked ECC work, successor to BATCH-d7e987 authorship recorded in DEC-20260907-d806f5): a FRESH independent approval gate on PA-ECDLP-6ac801-v2-to-v3-r2 (the addenda now on experiments/EXP-ECDLP-6ac801/specification.v3.yaml and amendments/v2_to_v3.yaml, plus amendments/v2_cf3_control_b.yaml and the AM-1 report under BATCH-d7e987). Session must be neither TASK-20260907-b1b54b, nor TASK-20260907-058c69, nor TASK-20260907-9c0626. Confirm the ten remedies landed, the two normative documents agree letter for letter on the controls, and nothing frozen moved. … [truncated, 10206 chars total; goal_head.py show GOAL-ECDLP-bbc21f --field next_action]'
campaign_budget:
  _omitted: +2 earlier keys not shown; goal_head.py show GOAL-ECDLP-bbc21f --field campaign_budget
  max_concurrent: 2
  unlimited_budget_note_20260906: 'ECC goal: campaign budget is UNLIMITED by declared policy (orchestration/research-priority.yaml, user instruction 2026-09-04); maximum_batches and total_wall_clock_seconds are null from creation and check_ecc_budget_is_unlimited enforces it. max_concurrent stays bounded -- it is machine headroom, not a research budget: this is a 4-core, 15 GB container and 2 is its headroom (each contract declares maximum_workers 1 and maximum_memory_gb 8). Per-experiment budgets remain those frozen in each contract and are never raised by this field.'
completion_criteria:
- id: C1
  statement: 'A committed evidence record for EXP-ECDLP-612fb1, independently validated and red-teamed, reporting T_resel(U)/T_static at fixed (L, epsilon) at a = 1/4 with a confidence interval, the early-batch penalty (first 10% of the batch, U_ss and cumulative U*), and the outcomes of the NULL-A / NULL-B nulls and the phi decay -- in EITHER direction: the T/2 re-selected table reaching static T within CI at U = 8T (S1-S4), or remaining CI-separated below it at U = 16T (F1), on the tested (N, a, r, k, cap, walk, solver) grid at claim_tier toy.'
  status: MET
  status_note: 'Flipped OPEN -> MET by TASK-20260906-ae5bb4 (BATCH-f3a30a), per completion_criteria_progress_20260906_f3a30a: EV-ECDLP-60e266 (negative direction, T_sel = T/2) and EV-ECDLP-f6b3f5 (re-scoped T_sel_grid_v2, direction supports) together are the committed, independently validated and red-teamed evidence this criterion''s "in EITHER direction" text asks for, on the tested grid at claim_tier toy.'
- id: C2
  statement: The instrument EXP-ECDLP-869870 committed with its basin-law measurements (survival slope, cutoff), its oracle-ceiling measurements (exact top-T share against C_max(a)), its published-rule measurements (the seven-cell primary-source fixture and C_rule/C_oracle as a function of N/T), and their N-independence verdict across 2^20..2^30 (V5), each with a confidence interval and the model value beside it, never in one column.
  status: OPEN
- id: C3
  statement: 'CLOSURE STANDARD, failing a positive on C1: a committed evidence record carrying a complete measured `obstruction` block per docs/inventor-protocol.md -- the quantity that bounds the gain (rho_T(16T) with its CI, or the static table''s measured estimation-loss gap to the exact oracle share), its value with units and error bars, the runs it is read from, the scope it is claimed over, and a genuinely asked resource_check. A closure whose obstruction is prose does not meet this criterion.'
  status: MET
  status_note: 'Flipped OPEN -> MET by TASK-20260906-ae5bb4 (BATCH-f3a30a), per completion_criteria_progress_20260906_f3a30a: EV-ECDLP-60e266''s obstruction block (T_sel = T/2 disjointness at a = 1/4, with a genuine resource_check) satisfies this criterion, unchanged and not retested by BATCH-f3a30a.'
pause_conditions:
- a snapshot or ledger archive fails post-commit verification
- a required review policy cannot be honoured without a silent downgrade
- the toy-curve arm cannot certify a solved logarithm
- the user declines approval and gives no revision direction
open_batches: []
latest_verified_commit: bc48281293f0a8adc7f806e6d4c1d95bcc7d5073
question_ids:
- RQ-ECDLP-78dbc5
active_hypothesis_ids:
- H-ECDLP-37dc01
- H-ECDLP-3550b8
owner: coordinator
updated_at: '2026-09-07'
_ad_hoc_keys_not_shown: 36 undeclared top-level keys on this record (goal_head.py audit GOAL-ECDLP-bbc21f)
_checkpoint_shards: 6 shard(s), latest BATCH-f3a30a (ledger/goals/GOAL-ECDLP-bbc21f/checkpoints/)

```


## goal head GOAL-CRYPTO-001
```
# GOAL-CRYPTO-001 — head projection from ledger/goals/GOAL-CRYPTO-001.yaml
# Resume fields only; ad-hoc keys and checkpoint bodies are not shown.

id: GOAL-CRYPTO-001
status: active
title: Reproducible cryptographically relevant ECDLP breakthrough search
current_batch_id: BATCH-98edec
dispatch_queue_path: coordination/goals/GOAL-CRYPTO-001/batches/BATCH-98edec/dispatch_queue.json
next_action: 'RESTORED 2026-09-08 by DEC-20260907-01c14f, VERBATIM from integrity_recovery_20260907.prior_selection.next_action, now that the BATCH-1f4d53 custody detour is independently validated and ledger-archived: Keep GOAL-CRYPTO-001 active (DEC-20260731-002 / EV-CRYPTO-013). Await newly retrieved primary sources or externally supplied formal mechanisms with quoted source semantics and a field-by-field fingerprint showing a falsifiable gain outside prior CRYPTO routes; require every readiness cost and certificate field before any curve work. Further experimental batches require an explicit Coordinator … [truncated, 2318 chars total; goal_head.py show GOAL-CRYPTO-001 --field next_action]'
campaign_budget:
  _omitted: +5 earlier keys not shown; goal_head.py show GOAL-CRYPTO-001 --field campaign_budget
  total_wall_clock_seconds_status_at_20260828_fund_all: SET TO null (UNBOUNDED) BY BUDGET-AMEND-20260828-2a257e on the user's explicit 2026-08-28 instruction "Fund every goal" (scope "All 47 active goals"), recorded in DEC-20260828-2a257e. The prior value 21600 is SUPERSEDED, not spent-or-exceeded by this record; any accounting note already attached to it stands immutable.
  max_concurrent: 3
completion_criteria:
- A certificate-verified discrete logarithm or relation-to-solve pipeline completes on a recognized curve above 96 bits and independently reproduces a fully charged wall-clock or operation-count advantage over the matched Pollard-rho baseline.
- Independent Validator and Red Team sessions verify the result, its receipts, scope, cost model, and absence of hidden preprocessing or supplied-witness leakage.
- A Coordinator crypto-tier evidence record, decision, and promoted KN-FIND entry are committed through a verified ledger archive.
pause_conditions:
- The declared campaign batch budget is exhausted without an admissible next mechanism.
- Required cryptographic computation exceeds the declared campaign budget after cheaper falsification gates are exhausted.
- A definitive infrastructure, authentication, or dependency blocker prevents the next approved task.
latest_verified_commit: 281a70a3cb0bbc9b75121330ab590e150f8cd402
question_ids:
- RQ-CRYPTO-001
active_hypothesis_ids: []
owner: coordinator
updated_at: '2026-09-08'
_ad_hoc_keys_not_shown: 11 undeclared top-level keys on this record (goal_head.py audit GOAL-CRYPTO-001)

```


## Existing hypotheses in these lanes (id | status | question | title)

- H-CREP-001 | approved | RQ-CRYPTO-001 | 
- H-ECDLP-09125b | analyzed | RQ-ECDLP-c1b7b1 | 
- H-ECDLP-0bc396 | proposed | RQ-ECDLP-4fcbd3 | 
- H-ECDLP-0f47ab | specified | RQ-ECDLP-165d4b | Stage 0 Teske-aperture identities — 32 branches, 32-by-32 A_M — before any charged rho census 
- H-ECDLP-15d016 | specified | RQ-ECDLP-623a32 | Refinement-automata Stage 0 identity — one-step next-feature split on Z/7Z; translation-equivariant homomorphism claim is rejected 
- H-ECDLP-1853dc | specified | RQ-ECDLP-165d4b | 
- H-ECDLP-24d15c | proposed | RQ-ECDLP-165d4b | 
- H-ECDLP-3c2f5a | specified | RQ-ECDLP-623a32 | Stage 0 (2,2)-gluing count identities — two 3-cycles in S_3 — before any Mumford divisor is built 
- H-ECDLP-3ca750 | proposed | RQ-ECDLP-4fcbd3 | 
- H-ECDLP-5b245d | proposed | RQ-ECDLP-4fcbd3 | 
- H-ECDLP-63d136 | specified | RQ-ECDLP-165d4b | 
- H-ECDLP-63eecd | specified | RQ-ECDLP-165d4b | 
- H-ECDLP-6a9479 | analyzed | RQ-ECDLP-c1b7b1 | 
- H-ECDLP-78337d | specified | RQ-ECDLP-623a32 | Twist-coset Stage 0 identity — prime-order / twist-order split on y^2=x^3+3 over F_7; composite-order nearby curve is rejected 
- H-ECDLP-7b7398 | specified | RQ-ECDLP-623a32 | Cubical-lift Stage 0 identity — unique N^2-th root on F_p^* when gcd(N, p-1)=1; embedding-degree-1 nearby object is rejected 
- H-ECDLP-80fceb | specified | RQ-ECDLP-165d4b | 
- H-ECDLP-84eb73 | specified | RQ-ECDLP-623a32 | Embedding-order Stage 0 identity — ord_N(p) and the forced cyclotomic factor-degree multiset; k=1 nearby pair is rejected as generic 
- H-ECDLP-9f3c7a | proposed | RQ-ECDLP-165d4b | 
- H-ECDLP-c48f2a | proposed | RQ-ECDLP-c1b7b1 | 
- H-ECDLP-cacf58 | specified | RQ-ECDLP-623a32 | Quadratic-order residue Stage 0 identity — split-prime Gauss-norm table is well-defined; inert prime is rejected 
- H-ECDLP-e42bda | specified | RQ-ECDLP-165d4b | 
- H-ECDLP-ee4740 | specified | RQ-ECDLP-165d4b | Stage 0 closed-form sensitivity-gap identities — D=1 on planted-weak families and Aut-discount squares — before any weak curve is built 
- H-ECDLP-ef73ed | specified | RQ-ECDLP-165d4b | Stage 0 closed-form census-column identities — {j, f, |Aut|} and Aut-discount squares — before any class is enumerated 
- H-ECDLP-f1e714 | proposed | RQ-ECDLP-c1b7b1 | 
- H-ECDLP-f6d060 | specified | RQ-ECDLP-165d4b | 
- H-ECDLP-f80d6e | specified | RQ-ECDLP-165d4b | Stage 0 Kuhn-Struik m=1 identities — A(1)=1 at T=0, c=0.886 — before any Velu transport 
- H-ECDLP-ff38dc | proposed | RQ-ECDLP-165d4b | No cell of this census is comparable to any other until the charged rho instrument's own finite-size bias is calibrated; the bias law is R(N) = 1 + c N^(-1/2), the fitted
- H-PFDR-05d754 | proposed | RQ-SBRG-f31cb2 | The reachable chain-node set W of a Weil-descended chained Semaev system carries NO low-degree boolean vanishing relations beyond the trivial count (excess_d = 0) -- and 
- H-PFDR-064546 | proposed | RQ-ECDLP-001 | Within the two-term cost model at arity m = 2, prime-field Semaev index calculus has a free-oracle floor of Theta(N^{2/3}) time at Theta(N^{1/3}) memory and costs Theta(N
- H-PFDR-06fd60 | specified | RQ-PFDR-ae2fba | Theorem (conditional on HEUR-001): under a last fall degree bounded by D_0 the hybrid optimum of the digit-presentation decomposition oracle flips from full guessing (the
- H-PFDR-09e1b0 | specified | RQ-PFDR-ae2fba | At fixed digit shape (m, d, s) the graded Macaulay invariants of the prime-field digit-presented decomposition system are p-independent above a small threshold prime, bec
- H-PFDR-0cc7e8 | specified | RQ-PFDR-ae2fba | 
- H-PFDR-14ca22 | proposed | RQ-PAIR-21313f | On a cyclic group of prime order N every bilinear map into H is determined by the single element h = b(P, P) in H[N], so the space of self-pairings is ONE-dimensional and
- H-PFDR-152561 | proposed | RQ-HQC-001 | 
- H-PFDR-1b2386 | proposed | RQ-FBG-001 | Conservation binds only on the WHOLE group, so relation collection is free to attempt only targets in a set decidable from the target REPRESENTATION x(R) -- one point add
- H-PFDR-1f2945 | proposed | RQ-ECTD-001 | 
- H-PFDR-2139a5 | specified | RQ-PFDR-ae2fba | Definition and quantifier certificates for first-fall comparisons
- H-PFDR-232b3a | specified | RQ-PFDR-ae2fba | Separate top-kernel onset from nonzero survival in the prime-digit first fall
- H-PFDR-26bcee | proposed | RQ-FBG-001 | A CHANNEL-SCOPED closure of the factor-base geometry family on the yield, coverage and rank channels -- and the rank channel discriminator must be rebuilt, because the so
- H-PFDR-2beb62 | specified | RQ-PFDR-ae2fba | Stage 0 symmetrization smallness compose obstruction degree sequence identities — n=2 — before any later stage is authorized 
- H-PFDR-2d78b6 | specified | RQ-PFDR-ae2fba | Stage 0 finite-state carry constraints prime-field decomposition circuit identities — n=2 — before any later stage is authorized 
- H-PFDR-3c7d1e | proposed | RQ-PFDR-ae2fba | 
- H-PFDR-4148b8 | specified | RQ-PFDR-ae2fba | The first fall degree of the d = 2 digit-presented Semaev system is a closed form in (m, s) alone -- d_ff(m, 2, s) = m 2^{m-1} + floor((s - 2^{m-1})/2) + 1 -- curve- and 
- H-PFDR-4765e4 | specified | RQ-PFDR-ae2fba | 
- H-PFDR-5b4a4f | proposed | RQ-SBRG-f31cb2 | Batch reuse of a target-independent Macaulay row space is capped by the reciprocal of the target-dependent row fraction, 1/rho_D = t-1 -- but the source idea pre-register
- H-PFDR-5b5c46 | proposed | RQ-ECDLP-002 | 
- H-PFDR-5e230f | proposed | RQ-ECDLP-002 | The corpus reads as a run of negatives because it is scored against a break: under a spectrum of intermediate result classes fixed IN WRITING BEFORE the corpus is looked 
- H-PFDR-6189d0 | proposed | RQ-EQIC-8cb959 | The corpus's nominal breadth of proposed prime-field ECDLP attack systems materially overstates the number of DISTINCT constructions: under a frozen, decidable normal for
- H-PFDR-621852 | proposed | RQ-ECDLP-002 | Direct-box S4/S5 planted recovery with exact modular Jochemsz-May lattices and finite ideal extraction
- H-PFDR-673eed | proposed | RQ-ECDLP-002 | 
- H-PFDR-6b8c0f | specified | RQ-PFDR-ae2fba | Stage 0 window-shape identities — (m,w)=(4,2), 4 leaves, 3 S3 blocks — before any re-parametrization 
- H-PFDR-6b9f1a | proposed | RQ-JINV-8fc13a | 
- H-PFDR-724ad2 | proposed | RQ-ECDLP-002 | The closed-form target-descent cost gate is BOTH passable and currently unpassed: a decidable ten-element descent certificate, calibrated on a curve-free positive control
- H-PFDR-80b6fb | specified | RQ-PFDR-ae2fba | Stage 0 yield clamp memory column lane cost identities — n=2 — before any later stage is authorized 
- H-PFDR-870647 | specified | RQ-PFDR-ae2fba | Stage 0 auxiliary-count identities — 4 leaves are bounded unknowns — before any tree shape is treated as demand 
- H-PFDR-8a4f44 | proposed | RQ-ECDLP-002 | 
- H-PFDR-9aadc0 | specified | RQ-PFDR-ae2fba | The prime-field digit twin of the binary chained Semaev system has neither ingredient of the exhibited binary degree-3 syzygy (the Boolean identity P(1 + P) = 0 fails in 
- H-PFDR-9c5065 | proposed | RQ-JINV-8fc13a | A nondegenerate self-pairing would recover the secret outright, which is exactly why it is forced trivial: Galois equivariance puts t_N(P, P) in the intersection of the N
- H-PFDR-a21e55 | specified | RQ-PFDR-ae2fba | Stage 0 supply-demand slack identities — 8/9-8408/10000=4328/90000 — before any strategy is called optimal 
- H-PFDR-a2258e | proposed | RQ-ECDLP-002 | 
- H-PFDR-a79efd | proposed | RQ-ECDLP-002 | 
- H-PFDR-aa86d0 | specified | RQ-PFDR-ae2fba | Stage 0 symmetrized s-4 system h002 never had identities — n=3 — before any later stage is authorized 
- H-PFDR-bb9a37 | specified | RQ-PFDR-ae2fba | 
- H-PFDR-c761e4 | proposed | RQ-ECDLP-001 | The toy S_3 Groebner instrument is not measuring a Semaev solving degree: because the factor-base membership polynomial is squarefree and splits completely, the ideal is 
- H-PFDR-c88f14 | specified | RQ-PFDR-ae2fba | No bounded-last-fall-degree theorem transfers to the prime-field digit presentation (the Frobenius cyclic-shift lemma of arXiv:2103.07282 has no F_p analogue and the redu
- H-PFDR-cb9606 | proposed | RQ-ICEX-001 | THE RESIDUAL IS THE OBJECT. Crediting only the residuals that land in the factor base discards, at rate 2 per charged operation, partial relations that combine in pairs; 
- H-PFDR-cbb5c4 | proposed | RQ-QALG-122b59 | 
- H-PFDR-d3c527 | proposed | RQ-ECDLP-160d89 | The conditioned cross-collision row of a keyed LEAF join is the keyed ADDITIVE ENERGY of the fibre system, and its Fourier dual turns any concentration beyond uniform int
- H-PFDR-d5f90f | specified | RQ-PFDR-ae2fba | Certified finite degree-growth ladder with blocking controls
- H-PFDR-df0127 | proposed | RQ-JINV-8fc13a | 
- H-PFDR-e02f3b | specified | RQ-PFDR-ae2fba | The one recorded prime-field early fall (EXP-ALPF-011 e-ring, quoted by EV-ALPF-001 and RQ-PFDR-ae2fba as 'POSITIVE (SURVIVED)') is a closed-form membership-only shared-f
- H-PFDR-e0988d | proposed | RQ-ECDLP-002 | The additive/multiplicative mismatch stated with quantifiers, and the residual-correlation question it cannot settle: integer lifts of x-coordinates along a scalar orbit 
- H-PFDR-ebec07 | proposed | RQ-JINV-8fc13a | 
- H-PFDR-f3fe89 | specified | RQ-PFDR-ae2fba | 
- H-PFDR-f7161e | proposed | RQ-DREG-001 | The amalgam Hilbert-series identity H_full = H_A * H_B / H_{k[U]} is a CANDIDATE predictor of the committed boolean chained-Semaev rank deficits, and its first obligation
- H-PFDR-f73cc9 | proposed | RQ-PAIR-f2e31f | 
- H-TLD-f4c8ba | specified | RQ-ECDLP-002 | 


## Existing proposals in these lanes (id | status | question | title) -- DO NOT DUPLICATE

- IDEA-20260829-172151 | proposed | RQ-ECDLP-165d4b | THE CENSUS CANNOT REPORT AN EMPTY CELL WITHOUT A DETECTION FLOOR, AND THE LANE'S ONLY SPECIFIED DESIGN HAS A CLOSED-FORM ONE: derive the exact minimum-detectable-effect o
- IDEA-20260829-20b05f | proposed | RQ-ECDLP-165d4b | THE CENSUS'S COLUMN SET IS PROVABLY FINITE AND HAS EXACTLY THREE ENTRIES: Tate's isogeny theorem makes every order-derived non-genericity constant across an F_p-isogeny c
- IDEA-20260829-2dc43c | proposed | RQ-ECDLP-165d4b | THE AUTOMORPHISM COLUMN OF THIS CENSUS IS FINITE AND CLOSABLE, NOT SAMPLEABLE: the unit group weight w(D) = |Aut(E)| that a 2026 distribution law uses to make CM orders e
- IDEA-20260829-34f3ed | proposed | RQ-ECDLP-165d4b | NO CELL OF THIS CENSUS IS COMPARABLE TO ANY OTHER UNTIL THE INSTRUMENT'S OWN FINITE-SIZE BIAS IS MEASURED: the RQ declares bit sizes 16 through 36 while every prime-field
- IDEA-20260901-3e68ad | proposed | RQ-ECDLP-165d4b | THE CENSUS'S "AUTOMORPHISM QUOTIENT" COLUMN CANNOT BE ENLARGED BY ANY SYMMETRY OF THE CURVE THAT MOVES THE ORIGIN: on a prime-order curve every finite F_p-rational group 
- IDEA-20260901-753636 | proposed | RQ-ECDLP-165d4b | PLAIN RHO SEES THE CURVE THROUGH EXACTLY ONE APERTURE -- THE PARTITION h(R) = x(R) mod r -- AND THE ISOMORPHISM ORBIT OF AN INSTANCE IS THE UNIQUE NULL OBJECT THAT VARIES
- IDEA-20260901-e3ffc2 | proposed | RQ-ECDLP-165d4b | THE CENSUS'S "CHARGED ISOGENY TRANSFER" COLUMN IS EMPTY PER INSTANCE AND NON-EMPTY PER POPULATION, AND THE TWO READINGS ARE SEPARATED BY ONE CHARGED TOY RUN WITH TWO FORC
- IDEA-20260903-26aa81 | proposed | RQ-PFDR-ae2fba | AT FIXED (m, d, s) THE DIGIT-PRESENTED DECOMPOSITION SYSTEM IS ONE INTEGER MATRIX FAMILY, so its graded ranks over F_p equal their generic rank over Q except on a rank-dr
- IDEA-20260903-399a18 | proposed | RQ-PFDR-ae2fba | THE COUPLED DEGREE-BY-YIELD TABLE AS A PRE-REGISTERED MEASUREMENT CONTRACT - six representation rows (direct f_V, digit d = 2, digit d = 4, multiplicative coset, window +
- IDEA-20260903-751062 | proposed | RQ-PFDR-ae2fba | THE ONE RECORDED PRIME-FIELD EARLY FALL IS A CLOSED-FORM MEMBERSHIP ARTIFACT AND ITS OWN ARCHIVE ALREADY SAYS SO - EV-ALPF-001 and RQ-PFDR-ae2fba quote the EXP-ALPF-011 a
- IDEA-20260903-afa56b | proposed | RQ-PFDR-ae2fba | THE YOKOYAMA SEMI-NORMALITY OBJECT IS A PRIME-FIELD OBJECT AND WAS APPLIED TO THE WRONG FIELD: reconstruct it from the literature (the D5_YOKOYAMA_OBJECT.md the honest le
- IDEA-20260903-cf63ad | proposed | RQ-PFDR-ae2fba | THE PRIME-FIELD DIGIT TWIN OF THE BINARY CHAINED SEMAEV SYSTEM HAS NEITHER INGREDIENT OF THE EXHIBITED BINARY DEGREE-3 SYZYGY: the Boolean identity P(1+P) = 0 fails for a
- IDEA-20260903-d52480 | proposed | RQ-PFDR-ae2fba | THE BOUNDED-LAST-FALL-DEGREE THEOREM OF arXiv:2103.07282 RESTS ON ONE LEMMA THE DIGIT PRESENTATION CANNOT SUPPLY (Frobenius acts as a cyclic shift on Weil-descent coordin
- IDEA-20260903-dcf857 | proposed | RQ-PFDR-ae2fba | THE CONDITIONAL COST TABLE OF THE DIGIT-PRESENTATION DECOMPOSITION ORACLE UNDER A BOUNDED LAST FALL DEGREE, with the semi-regular slice reproducing IDEA-20260808-da1428 e
- IDEA-20260903-e0a3e8 | proposed | RQ-PFDR-ae2fba | SYMMETRIZATION AND SMALLNESS DO NOT COMPOSE, AND THE OBSTRUCTION IS THE DEGREE SEQUENCE OF THE INVARIANT RING: the image of the window box [0,B)^m under the elementary sy
- IDEA-20260903-e1e38b | proposed | RQ-PFDR-ae2fba | THE p-ARY ALGEBRAIC IMMUNITY OF THE DIGIT-SUBSTITUTED SEMAEV TOP FORM IS 1/m OF THE GENERIC VALUE AND IT IS DERIVABLE, NOT ONLY MEASURABLE - at d = 2 the top form of S_{m
- IDEA-20260903-f7e8a6 | proposed | RQ-PFDR-ae2fba | THE SYMMETRIZED S_4 SYSTEM OF H002 HAS NEVER HAD ITS OWN NULL, AND THE NULL ABSORBS THE WHOLE 6:1 - the S_3-invariant Hilbert series of the membership complete intersecti
- IDEA-20260903-fc1355 | proposed | RQ-PFDR-ae2fba | THE NESTED DIGIT LADDER IS PROFILE-BLIND UNDER THE SEMI-REGULAR NULL: for any ladder profile (s_1, ..., s_m) the null solving degree ceil((S(d-1) + 2m)/2) and the KN-FIND
- IDEA-20260904-39336c | proposed | RQ-PFDR-ae2fba | THE CLOSURE'S SUPPLY NUMBER IS ONE STRATEGY'S VALUE, NOT AN OPTIMUM, AND THE GAP IS 0.1592 WHILE THE MISS IS 0.0481: run the 2024-2026 provably optimal / provably correct
- IDEA-20260904-742c48 | proposed | RQ-ECDLP-165d4b | THE ENDOMORPHISM-ORBIT LANE IS CLOSED BY A COST INEQUALITY, NOT BY A NORM BOUND, AND THE PROGRAM'S CURRENT CLOSURE USES THE WRONG COST MODEL: an endomorphism of degree n 
- IDEA-20260904-8dccc9 | proposed | RQ-PFDR-ae2fba | THE WINDOW DOES NOT HAVE TO BE ONE UNKNOWN: re-parametrizing the SAME interval factor base by r bounded digits is exactly volume-preserving, hence provably demand-neutral
- IDEA-20260904-ab226c | proposed | RQ-ECDLP-165d4b | THE CENSUS HAS BEEN COUNTING THE WRONG CELL BY A FACTOR OF sqrt(p): the endomorphism-relevant quantity is delta(E) = |disc End_{F_p}(E)|/4, the EXACT degree of the cheape
- IDEA-20260904-c583dd | proposed | RQ-PFDR-ae2fba | THE YIELD CLAMP AND THE MEMORY COLUMN: the lane's cost model lets the target count m!N/B^m fall below 1, which credits fractional targets and moves the admission gate fro
- IDEA-20260904-cb1199 | proposed | RQ-ECDLP-165d4b | THE RQ'S DECISION TARGET IS A FALSE DISJUNCTION AND ONE EXTERNAL 2025 THEOREM COLLAPSES IT: joining two SPECIFIED curves of one ordinary F_q-isogeny class is rigorously O
- IDEA-20260904-cc1b0d | proposed | RQ-ECDLP-165d4b | THIS CENSUS MEASURES NON-GENERIC HARDNESS WITH FOUR GENERIC INSTRUMENTS AND HAS NEVER ONCE BEEN SHOWN A CURVE IT COULD DETECT: run the census's own declared method set un
- IDEA-20260904-e9675e | proposed | RQ-PFDR-ae2fba | THE TREE HYPOTHESIS IS NOT LOAD-BEARING ON THE DEMAND SIDE: eps_required depends only on the NUMBER of bounded auxiliary unknowns A, not on how they are wired, so "non-tr
- IDEA-20260905-05648a | proposed | RQ-ECDLP-623a32 | THE TORSION-QUOTIENT COORDINATE IS SEMAEV ON THE QUOTIENT CURVE: for a cyclic rational torsion subgroup C of order k on a cofactor curve, the coordinate t = x' o phi_C (r
- IDEA-20260905-0e0982 | proposed | RQ-ECDLP-623a32 | THE PAIR (P, Q) AS ONE MUMFORD DIVISOR - on a prime-order curve Frobenius acts on E[2] as a 3-cycle, so EXACTLY TWO F_p-rational (2,2)-gluings of E with itself are Jacobi
- IDEA-20260905-24b41a | proposed | RQ-ECDLP-623a32 | NETS, CUBICAL LIFTS, MILLER FUNCTIONS AND DUAL-NUMBER LIFTS ARE ONE OBJECT - a G_m- or G_a-torsor over the point - and on a prime-order prime-field curve its rational con
- IDEA-20260905-3a30d5 | proposed | RQ-ECDLP-c1b7b1 | THE FERMAT-QUOTIENT DIGIT: the Teichmuller lift of a coordinate has second p-adic digit x times the Fermat quotient of x, the unique homomorphic (torsion) lift has its ow
- IDEA-20260905-579fcc | proposed | RQ-ECDLP-623a32 | MULTISETS OF x OVER A SHIFT SET ARE EITHER A CHANGE OF COORDINATES OR THE SHIFTED KUMMER COORDINATE, NOTHING IN BETWEEN - for S subset Z/N of size r >= 2 and fixed R, P |
- IDEA-20260905-5a1ea2 | proposed | RQ-ECDLP-4fcbd3 | THE SUMSET ENVELOPE, GRAMMAR-FREE AND WITH ITS BLIND SPOT NAMED: the x-histogram of P+Q over a factor base F has an additive-character transform whose maximum bounds the 
- IDEA-20260905-848b77 | proposed | RQ-ECDLP-c1b7b1 | THE HARD LIFT, LOCALISED: for gcd(n, p) = 1 the p-adic points split as torsion section plus formal group, so the global hard lift T^ = m S^ is the torsion lift of T plus 
- IDEA-20260905-850460 | proposed | RQ-PFDR-ae2fba | Retained-control exact degree-growth ladder for binary-digit systems
- IDEA-20260905-9c4f0c | proposed | RQ-ECDLP-4fcbd3 | THE REAL WALK IS NOT THE CONVOLUTION: the r-adding walk chooses its branch from coordinates, so its transition operator is not translation-invariant and its itinerary cla
- IDEA-20260905-ab4a6e | proposed | RQ-ECDLP-623a32 | THE QUADRATIC-ORDER BOX FACTOR BASE - x(P) read as a residue of a small element u + v*omega of an imaginary quadratic order O_K modulo a split prime, small meaning |u|, |
- IDEA-20260905-b6154d | proposed | RQ-ECDLP-4fcbd3 | THE WALL, MADE EXACT, AND THE TWO DOORS IN IT: for a bounded-degree coordinate function on an odd-prime-order subgroup every discrete-log character correlation is at the 
- IDEA-20260905-d0fee4 | proposed | RQ-ECDLP-623a32 | THE KUMMER LINE IS BEZOUT-OPTIMAL AMONG ALL COORDINATES E -> P^1, NOT ONLY AMONG DEGREE-2 ONES - for every F_p-rational f of degree n the window factor base f^{-1}(W) has
- IDEA-20260905-dacf4f | proposed | RQ-ECDLP-c1b7b1 | ONE p-ADIC INSTRUMENT FOR FIVE WAITING RECORDS: the ledger holds cost models of the anomalous attack but no implementation of Hensel lifting, the Teichmuller lift, the to
- IDEA-20260905-df55e9 | proposed | RQ-PFDR-ae2fba | Definition and quantifier certificates for prime-field digit fall claims
- IDEA-20260905-e6e2e5 | proposed | RQ-PFDR-ae2fba | Corrected top-rank and nonzero-survival conditions for the binary-digit first-fall law
- IDEA-20260905-f31bc4 | proposed | RQ-ECDLP-4fcbd3 | THE DL-SPECTRUM CENSUS: tabulate the discrete log of every point of a toy prime-order subgroup, Fourier-transform a frozen library of cheap coordinate functions in the gr
- IDEA-20260906-09b937 | proposed | RQ-ECDLP-623a32 | Quadratic-order residue representation of x-coordinates: the factor base of points whose x has a small-norm lift in O_K modulo a split prime is an implicit-membership bas
- IDEA-20260906-0c1bbd | proposed | RQ-PFDR-ae2fba | A valuation-semigroup presentation of the decomposition coordinate ring
- IDEA-20260906-31a35f | proposed | RQ-PFDR-ae2fba | Finite-state carry constraints for a prime-field decomposition circuit
- IDEA-20260906-476f20 | proposed | RQ-ECDLP-623a32 | F_{p^2}-twist coset representation: E(F_{p^2}) = G (+) G' with G' the twist points, the coset P + G' is a block system of translation by G' and of Frobenius (a genuine pa
- IDEA-20260906-86cc17 | proposed | RQ-ECDLP-623a32 | Cubical lift over the prime-order subgroup: the N^2-th-root canonical section splits the lift with zero information (multiplicative Schur-Zassenhaus), and the residual co
- IDEA-20260906-a056ea | proposed | RQ-PFDR-ae2fba | Commutator-certified border reduction of sparse decomposition algebras
- IDEA-20260906-aa6da3 | proposed | RQ-ECDLP-623a32 | Level-N linearisation: translation by the prime-order subgroup acts F_p-linearly on the Riemann-Roch space L(N.O), giving the regular representation of G whose F_p-irredu
- IDEA-20260906-e07475 | proposed | RQ-ECDLP-623a32 | Predictive refinement automata for history-dependent point features
- IDEA-20260911-2dd68d | proposed | RQ-ECDLP-c1b7b1 | Resolution-matched, degeneracy-screened re-test of the Teichmuller non-homomorphic contrast (repairing H-ECDLP-6a9479 claim 3)
- IDEA-20260928-4e2be7 | proposed | RQ-PFDR-ae2fba | Harvest every x-key collision the mitm engine already computes, and census their excess over a random base. Table-table, table-base and search-search coincidences are cur
- IDEA-20260928-ce3ab0 | proposed | RQ-PFDR-ae2fba | The generic collision floor. Any index-calculus engine that gets its relations only as x-key collisions among group elements it computed pays at least (1/2)*sqrt(r*N) S_3
- IDEA-20260928-fd7f5d | proposed | RQ-PFDR-ae2fba | The incomplete-sum regime of Hom(E,G_m) = 0. Do multiplicative characters that are CONSTANT on a coset (or Dickson) base bias the characters of x(P+-Q) for P, Q in the ba