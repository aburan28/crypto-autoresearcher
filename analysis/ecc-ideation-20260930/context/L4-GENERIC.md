# Lane L4-GENERIC context (generated 2026-09-30 from committed ledger state; read-only)


## RQ-GRUMPY-964876  (ledger/questions/RQ-GRUMPY-964876.yaml)

```yaml
research_question:
  id: RQ-GRUMPY-964876
  added: '2026-09-06'
  title: >-
    The exact average-case constant of the two-grumpy-giants-and-a-baby algorithm.
    For a uniform random target in a generic group of prime order l, what is the
    leading coefficient c in c * sqrt(l) * (1 + o(1)) expected group operations at
    the algorithm's optimal step schedule, and can that constant be proved or
    exactly certified rather than fitted?
  scope:
    curve_families:
      - >-
        the generic prime-order group model realised as Z/l with addition (the
        null-cost instance on which every operation count is exact and the curve
        plays no role)
      - >-
        prime-order subgroups of self-generated ordinary short-Weierstrass curves
        over F_p at toy sizes, as the elliptic consistency arm only; the constant
        is a generic-group quantity and the elliptic arm may not change it
    field_types: [prime, generic-group]
    bit_sizes:
      - >-
        exhaustive enumeration over every target x in Z/l for a ladder of l from
        about 2^10 to whatever l the exact per-target count remains affordable at
        (the exact mean over all l targets is an integer sum divided by l)
      - >-
        sampled targets only for larger l, reported as intervals with the sample
        size, never as the constant
      - symbolic proof work at all l
    methods:
      - >-
        Bernstein-Lange two-grumpy-giants-and-a-baby (baby steps, a giant walking
        forward, a giant walking backward, collisions between any two sequences),
        with and without the negation map, at a declared step-count schedule
      - >-
        baby-step giant-step (average and worst case, interleaved and classical)
        and a truly random walk as the two comparison rows the paper itself uses
      - >-
        exact first-collision-time analysis of the three sequences as a function
        of the target, and exact combinatorial summation over all targets
      - independent blind re-derivation of any claimed closed form
  motivation: >-
    User-supplied target (2026-09-06, verbatim): 'the exact average-case constant
    for grumpy giants'. The user names it as a tractable target with a sound
    verifier, in contrast to subexponentiality questions where near-zero measured
    batch ratios are exactly what one expects. The ledger holds a single literature
    record on the algorithm, KN-LIT-7291 (Bernstein and Lange, 'Two grumpy giants
    and a baby'; confidence reported, citation_verified read, relayed from the
    paper's first pages), which records fixed-budget success probabilities after
    (1.5 + o(1)) sqrt(l) additions: 0.5625 + o(1) for baby-step giant-step,
    0.6753... + o(1) for a truly random walk, 0.71875 + o(1) for the grumpy-giants
    method. The average-case constant of the grumpy-giants method itself is not
    recorded anywhere in this ledger, and the one proposal that mentions the paper
    (IDEA-20260901-753636, RQ-ECDLP-165d4b) uses it only as a rho-anti-collision
    pointer. Recalled and not opened by any agent in this program: later analyses
    of baby-step giant-step variants including the grumpy giants exist in the
    literature (Galbraith, Wang and Zhang are the recalled authors); the generator
    must open and cite before any claim about what is already proved. The reason
    this is a sound target: the quantity is a well-defined expectation over a
    finite uniform distribution, so at every toy l it has an exact value computable
    by enumeration, and any proposed closed form or asymptotic constant is
    checkable against those exact values before a single sampled run is believed.
  decision_target: >-
    Either (a) a theorem giving the constant c (or a proof that it equals a named
    number such as a rational multiple of sqrt(2) or an integral in closed form)
    for a stated step schedule, with the quantifier order explicit (for which
    schedule, which cost unit, with or without the negation map), verified by an
    independent blind re-derivation AND by agreement with the exhaustively
    enumerated exact means at every ladder l within the stated o(1) term; or (b)
    absent a proof, a certified numerical statement: the exact all-target mean at
    each ladder l as an integer ratio, the normalised value mean / sqrt(l) as a
    table, and an interval for the limit derived from a declared extrapolation
    model, labelled as modelled. A constant fitted from sampled targets without the
    exhaustive column is not a result. Whichever branch closes, the record states
    the optimal schedule found, the cost unit, the storage charged, and the
    comparison to the baby-step giant-step and random-walk constants on the same
    instrument. No claim about elliptic curves follows; the constant is
    generic-group.
  constraints:
    - >-
      Cost unit is group additions; table lookups, comparisons and storage are
      charged separately and reported, never folded into the addition count.
    - >-
      Every reported mean at a ladder point is either exhaustive (all l targets,
      exact integer sum) or sampled with the sample size and a confidence interval;
      the two are never mixed in one column.
    - >-
      The step schedule (number of baby steps, giant step sizes and directions,
      where the giants start) is a declared input; 'optimal' means optimal over a
      declared finite family of schedules, and the family is reported.
    - >-
      The negation-map variant is a separate parameter with its own constant; a
      result for one is not a result for the other.
    - >-
      The elliptic arm must reproduce the Z/l counts exactly at equal l (the
      algorithm is generic); a discrepancy is an instrument defect, not a finding.
    - >-
      Any closed form must be checked against the exhaustive means before it is
      recorded; a proof that disagrees with an exhaustive value at some l is wrong
      at that l, whatever its asymptotics claim.
    - >-
      Timeouts, crashes and memory exhaustion are infrastructure outcomes, never
      negative mathematical evidence (AGENTS.md).
    - >-
      Claim tier toy for measurements; a proof is a derivation-level claim scoped
      to its stated schedule and cost unit.
  related_questions: [RQ-ECDLP-165d4b, RQ-ECDLP-002, RQ-LHW-1877bb]
  goal_ids: []
  status: active
  owner: coordinator

```


## RQ-LHW-1877bb  (ledger/questions/RQ-LHW-1877bb.yaml)

```yaml
research_question:
  id: RQ-LHW-1877bb
  added: '2026-09-06'
  title: >-
    A low-storage algorithm for the low-Hamming-weight discrete logarithm problem
    whose running time matches sqrt(binom(m, w)) up to polynomial factors. For a
    logarithm of bit-length m and Hamming weight w in a generic prime-order group,
    can the meet-in-the-middle time bound be reached with polylogarithmic (or
    polynomial in m) storage, or is there an obstruction in a stated model?
  scope:
    curve_families:
      - >-
        the generic prime-order group model realised as Z/l with addition (exact
        operation counts, curve-free)
      - >-
        prime-order subgroups of self-generated ordinary short-Weierstrass curves
        over F_p at toy sizes, with the logarithm planted from the promise class
        W(m, w) of weight-w integers below 2^m
    field_types: [prime, generic-group]
    bit_sizes:
      - >-
        a ladder in (m, w) chosen so that sqrt(binom(m, w)) runs from about 2^10
        to about 2^24 group operations, with w between about m/8 and m/2
      - >-
        the plain-integer instance (subset sum / low-weight knapsack of the same
        (m, w)) as the dynamic-range arm where representation techniques are
        known to work
    methods:
      - >-
        Coppersmith splitting and Stinson-style meet-in-the-middle on the weight
        (the time baseline at sqrt(binom(m, w)) times a polynomial, with storage of
        the same order)
      - >-
        parameterized splitting systems (KN-LIT-2177) and the baby-step giant-step
        variants of KN-LIT-2135
      - >-
        low-memory collision techniques: Pollard-rho style walks restricted to the
        class, nested collision finding and representation-based algorithms with
        polynomial memory (KN-LIT-4794 as the reported state of the art)
      - >-
        obstruction arguments in a stated model (e.g. a collision-finding lower
        bound on the class, or a mixing-time bound for walks on W(m, w))
  motivation: >-
    User-supplied target (2026-09-06, verbatim): 'a low-storage algorithm for
    low-Hamming-weight DLP matching sqrt(m choose w)'. Named by the user as a
    tractable target with a sound verifier. What is on the ledger: KN-LIT-4794
    (Esser and May, 'Low weight discrete logarithm and subset sum in 2^{0.65n}
    with polynomial memory'; confidence reported) records a polynomial-memory
    algorithm whose time interpolates to Pollard's sqrt(|G|) for general instances
    and improves on prior low-weight algorithms, which places the reported
    low-memory frontier ABOVE the sqrt(binom(m, w)) meet-in-the-middle time that
    memory-heavy splitting attains; KN-LIT-2177 and KN-LIT-2135 record splitting
    systems and baby-step giant-step variants for low-weight and product-of-
    low-weight exponents. Inside the program, H-ICEX-8f9ea2 (proposed, bound to
    RQ-ECDLP-002) and its draft contract EXP-ICEX-850e41 treat W(m, w) as a promise
    class and ask whether the certified solve cost is |W|^{1/2 + o(1)} for a
    meet-in-the-middle and a representation-style solver; storage is not that
    record's object and no run exists. The gap the user names is therefore
    precise: time sqrt(binom(m, w)) is known WITH storage of that order, and
    polynomial memory is known only at a worse exponent (as reported). The sound
    verifier is that every claimed solve carries a certificate [x]P = Q with
    popcount(x) = w and x < 2^m, re-verified independently, and every claimed
    memory bound is a measured peak-words trace on the same run, so a claim of
    'time T with storage S' is checkable instance by instance.
  decision_target: >-
    Either (a) an algorithm, implemented and run on planted instances across the
    (m, w) ladder, whose measured group-operation count divided by sqrt(binom(m,
    w)) is bounded by a declared polynomial in m over the whole ladder while its
    measured peak storage is bounded by a declared polynomial (ideally polylog) in
    m, with every solve certified; the record states the exponent fit, its
    interval, the heuristic assumptions numbered with validation routes, and the
    comparison rows (memory-heavy meet-in-the-middle at the same (m, w), plain
    Pollard rho on the group ignoring the promise, and the reported 2^{0.65n}-type
    low-memory algorithm reproduced as a control); or (b) a stated-model
    obstruction: a proof or a controlled measurement showing why a named class of
    low-memory methods (walks on W(m, w) with a declared step rule, nested
    collision finding with declared depth) cannot reach the meet-in-the-middle
    exponent, scoped exactly to that class; or (c) a heuristic algorithm reaching
    the bound conditionally on explicit numbered heuristics, each with a cheap
    validation route, recorded as conditional. A time bound without the memory
    trace, or a memory bound without certified solves, is not a result.
  constraints:
    - >-
      Instances are self-generated: the planted logarithm is known to the
      generator only for planting and certificate checking; no solver takes it as
      input.
    - >-
      Storage is measured as peak words of group elements plus indices, reported
      per run alongside the operation count; 'polynomial memory' is a measured
      curve over the ladder, not an assertion.
    - >-
      The meet-in-the-middle baseline at the same (m, w) must be run on the same
      instrument, with its own storage trace, so the trade-off is measured rather
      than quoted.
    - >-
      Plain Pollard rho on the group (ignoring the promise) is the outer baseline;
      a promise-class algorithm is only interesting where it beats it, and that
      crossover is reported.
    - >-
      The plain-integer (subset-sum) arm is the dynamic-range control: a technique
      that fails there is not expected to work on the group and the failure is
      reported as instrument range, not as a group-theoretic finding.
    - >-
      Reported exponents from the literature are treated as reported until
      reproduced on this instrument.
    - >-
      Timeouts, crashes and memory exhaustion are infrastructure outcomes, never
      negative mathematical evidence (AGENTS.md).
    - Claim tier toy; no deployed parameter is an instance.
  related_questions: [RQ-ECDLP-002, RQ-ICEX-001, RQ-GRUMPY-964876]
  goal_ids: []
  status: active
  owner: coordinator

```


## RQ-ECDLP-78dbc5  (ledger/questions/RQ-ECDLP-78dbc5.yaml)

```yaml
research_question:
  id: RQ-ECDLP-78dbc5
  id_allocation_provenance: >-
    Token minted 2026-09-06 with `python3 tools/allocate_id.py --next
    research_question --area ECDLP` and confirmed free with `--check`
    (0 occurrences across 12197 identifier-bearing paths). Not derived by
    scanning state.
  goal_id: null
  goal_id_note: >-
    Not yet bound to a GOAL record. The umbrella question RQ-ECDLP-002
    (GOAL-ECDLP-001) lists "multi-target, preprocessing, and memory-time
    tradeoffs" in its methods scope; this question isolates one precise
    quantity inside that scope so that ideation and experiments can be
    ranked against a single frontier. Binding to GOAL-ECDLP-001 or to a
    dedicated goal is a Coordinator decision recorded separately.
  title: >-
    Batch ECDLP with precomputation: can the number of stored distinguished
    points T needed for a fixed per-target online cost and success
    probability be reduced below the Bernstein-Lange selected-table
    frontier, and by how much, in a fully charged (precomputation, table
    bits, online operations, batch size) cost model?
  created_at: '2026-09-06T00:00:00-07:00'
  updated_at: '2026-09-06T00:00:00-07:00'
  status: active
  owner: coordinator
  scope:
    curve_families:
    - toy ordinary prime-field short-Weierstrass curves of prime order N
      (the object under study is the walk/table structure, which is
      generic; the curve supplies a concrete group and a certificate check)
    - matched random-curve and random-relabelled null objects at the same N
    - the multiplicative group of a prime field or an interval instance may
      be used ONLY as an additional generic control, never as the headline
      object
    field_types:
    - prime
    bit_sizes:
    - toy instances (N from ~2^20 to ~2^48) for executable falsification and
      constant measurement with confidence intervals
    - symbolic S*T^2 / T*W^2 models for scope statements and extrapolation
    methods:
    - Bernstein-Lange cube-root precomputation table (KN-LIT-3060) with
      over-generated walks and most-popular-distinguished-point selection
      as the mandatory baseline frontier
    - Pollard rho with distinguished points and van Oorschot-Wiener parallel
      collision search as the no-table control
    - Kuhn-Struik / batch-rho reuse of solved-target walks, and any
      table-growth-during-online scheme
    - walk-selection, coverage-weighting, ancestry-size estimation, variable
      distinguishing probability, and any table-compression scheme that
      keeps a reconstructible log for each stored point
    - interval (kangaroo) variants only where they serve as a control for the
      full-group result
  definitions:
    N: prime order of the group in which logarithms are computed
    T: number of distinguished points STORED in the table after selection
    T_gen: number of precomputation walks generated before selection
    W: expected walk length between distinguished points (1/theta)
    U: number of targets solved in one batch against one table
    P: precomputation cost in group operations
    S: table size in bits (T entries times bits per entry)
    L: expected online group operations per target
    epsilon: per-target success probability within the online budget
    fewer_DP: >-
      Formalised as a reduction of T at fixed (N, U, L, epsilon) relative to
      the selected Bernstein-Lange table built under the same charged model
      and the same P budget, reported as a ratio with a confidence interval.
      A reduction of T obtained by raising P, L, U, or bits-per-entry is a
      tradeoff, not an improvement, and must be reported as a point on the
      (P, S, L, epsilon, U) frontier.
  motivation: >-
    Bernstein-Lange (KN-LIT-3060) report that a table of ell^{1/3}
    distinguished points, selected from a larger over-generated set,
    computes a logarithm in a group of order ell in about 1.77 ell^{1/3}
    multiplications after 1.24 ell^{2/3} precomputation; Corrigan-Gibbs and
    Kogan (KN-LIT-013) prove S*T^2 = Omega~(epsilon N) for every generic
    algorithm with preprocessing, and the bound is tight. The exponent is
    therefore closed in the generic model, and the honest research target is
    the constant: how much of the table's coverage is redundant, how much
    coverage a stored point buys as a function of how it was selected, and
    whether a batch of U targets lets the table shrink (because online walks
    of a batch also collide with each other and with each other's earlier
    solved walks). The program has no committed measurement of that constant,
    and no committed statement of which selection rules beat the
    most-popular-point rule, on any group at any size. Every existing
    MTGT-lane record (RQ-MTGT-2cabee) concerns transporting a table between
    curves, not shrinking it.
  decision_target: >-
    Admit a candidate only if, on toy prime-order curves at at least three
    sizes, it reduces T at fixed (N, U, L, epsilon) by a measured factor whose
    confidence interval excludes 1.0 against the selected Bernstein-Lange
    table built under the same P budget, survives a random-relabelling null
    object and a decay test (the gain must vanish when the selection signal
    is destroyed), and states which point on the (P, S, L, epsilon, U)
    frontier it occupies. Any claim of a super-constant reduction must
    identify the non-generic structure it uses and reconcile itself with
    KN-LIT-013 explicitly. A negative batch narrows the constant's known
    range; it does not close this question.
  constraints:
  - Lawful defensive cryptanalysis on public constructions and toy benchmarks
    only. No targeting, recovery, or testing of live private keys, wallets,
    or deployed systems.
  - The selected Bernstein-Lange table (over-generation plus
    most-popular-distinguished-point selection), the unselected uniform table
    of the same T, and rho-with-distinguished-points with no table are
    mandatory matched controls, all charged in the same unit (group
    operations, counted, never wall clock).
  - The generic S*T^2 = Omega~(epsilon N) bound (KN-LIT-013, KN-TECH-005) is
    the ceiling; a proposal must say whether it moves the constant, a log
    factor, or claims non-generic structure.
  - Every solved logarithm carries a certificate re-verified by an
    independent scalar multiplication (docs/claims-and-verification.md).
  - Every measured gain requires a null object of the same shape and a decay
    test before it is believed (docs/inventor-protocol.md).
  - Success probability and online cost are reported as distributions over
    seeded targets with confidence intervals, never as single runs.
  - 'Evidence from these runs is capped at claim_tier: toy; extrapolation to
    cryptographic sizes is a stated assumption, never a result.'
  - Timeouts, crashes and infrastructure failures are never negative
    mathematical evidence (AGENTS.md rule 5).
  literature_anchors:
  - ref: KN-LIT-3060
    provenance: kb
    note: Bernstein-Lange, Computing small discrete logarithms faster (cube-root table, 1.77 ell^{1/3} online)
  - ref: KN-LIT-5230
    provenance: kb
    note: Bernstein-Lange, Non-uniform cracks in the concrete (free precomputation against P-256)
  - ref: KN-LIT-013
    provenance: kb
    note: Corrigan-Gibbs and Kogan, S*T^2 = Omega~(epsilon N) generic preprocessing bound, tight
  - ref: KN-LIT-5229
    provenance: kb
    note: Coretti, Dodis, Guo, non-uniform bounds in the generic-group model (presampling)
  - ref: KN-LIT-5040
    provenance: kb
    note: Multiple discrete logarithm problems with auxiliary inputs (batch setting)
  - ref: KN-LIT-7046
    provenance: kb
    note: The query complexity of preprocessing attacks
  - ref: KN-LIT-012
    provenance: kb
    note: van Oorschot and Wiener, parallel collision search with distinguished points

```


## Existing hypotheses in these lanes (id | status | question | title)

- H-ECDLP-32fad8 | specified | RQ-ECDLP-78dbc5 | THE BATCH-GROWN TABLE WITH RELATION-GRAPH ACCOUNTING: precompute only T_0 < T_BL selected entries, let the U targets' own terminal distinguished points (solved or not) jo
- H-ECDLP-3550b8 | analyzed | RQ-ECDLP-78dbc5 | THE BASIN-PARTITION COVERAGE INSTRUMENT: the coverage of a Bernstein-Lange distinguished-point table is a sum of disjoint exact basin sizes; the basin-size law is Borel(1
- H-ECDLP-37dc01 | analyzed | RQ-ECDLP-78dbc5 | THE BATCH-RESELECTED FIXED-SIZE TABLE: with the advice size held at exactly T entries, letting the batch's own SOLVED walks feed Bernstein-Lange's candidate pool and re-s
- H-ECDLP-4b54a2 | approved | RQ-ECDLP-78dbc5 | PREPROCESSING RE-READING OF THE WINDOWED SMALL-ROOT FAMILY AT (m = 3, w = 1): does the JOINT small-root region of the coupled summation system {S_3(x1, x2, y), S_3(y, x3,
- H-ECDLP-f2bdd0 | specified | RQ-ECDLP-78dbc5 | THE BOREL CEILING AS A CHECKABLE DERIVATION ARTIFACT: for a uniformly random function on N points with a uniform distinguishing rule of expected walk length W (theta = 1/
- H-GRUMPY-1ead49 | approved | RQ-GRUMPY-964876 | 
- H-GRUMPY-94a295 | proposed | RQ-GRUMPY-964876 | Exact Bellman certificates for the fixed three-sequence grumpy-giant family
- H-GRUMPY-c09652 | specified | RQ-GRUMPY-964876 | Stage 0 discrepancy-interval identities — a<=b on a declared pair — before any grumpy mean is certified 
- H-GRUMPY-f7f335 | specified | RQ-GRUMPY-964876 | Stage 0 certified exhaustive ladder grumpy-giants constant negation identities — n=3 — before any later stage is authorized 
- H-LHW-8e8cff | proposed | RQ-LHW-1877bb | 


## Existing proposals in these lanes (id | status | question | title) -- DO NOT DUPLICATE

- IDEA-20260906-05ffb8 | proposed | RQ-ECDLP-78dbc5 | BEYOND THE BERNSTEIN-LANGE WEIGHT: at equal precomputation P and equal table size T, rank candidate distinguished points by the Galton-Watson posterior mean of the basin 
- IDEA-20260906-3493fe | proposed | RQ-LHW-1877bb | Separator checkpointing in nested low-weight collision generators
- IDEA-20260906-7bd805 | proposed | RQ-GRUMPY-964876 | THE SET OF TARGETS SOLVED BY THE GRUMPY-GIANTS ALGORITHM AFTER n ADDITIONS IS TARGET-INDEPENDENT -- a union of three explicit interval systems in Z/l -- SO THE AVERAGE-CA
- IDEA-20260906-7d5c16 | proposed | RQ-LHW-1877bb | Nonbacktracking exchange lifts for low-weight collision mixing
- IDEA-20260906-a3d6ae | proposed | RQ-ECDLP-78dbc5 | THE BATCH-GROWN TABLE WITH RELATION-GRAPH ACCOUNTING: precompute only T_0 < T_BL selected entries, let the U targets' own terminal distinguished points (solved or not) jo
- IDEA-20260906-a7270e | proposed | RQ-GRUMPY-964876 | Residue-phase discrepancy certificates for the grumpy mean
- IDEA-20260906-ab08cb | proposed | RQ-LHW-1877bb | THE FIBRE-SURPLUS LAW FOR POLYNOMIAL-MEMORY WALKS ON THE LOW-WEIGHT CLASS - for any walk whose state is a known coefficient pair (S, T) carried as [S]P + [T]Q and whose s
- IDEA-20260906-ac100b | proposed | RQ-ECDLP-78dbc5 | THE BOREL CEILING AS A DERIVATION: for a random-function walk with a uniform distinguishing rule of expected walk length W, prove (as a checkable derivation artifact, nev
- IDEA-20260906-aed829 | proposed | RQ-ECDLP-78dbc5 | THE BASIN-PARTITION COVERAGE INSTRUMENT: measure the coverage constant of a Bernstein-Lange distinguished-point table as a sum of disjoint basin sizes, against the Borel 
- IDEA-20260906-c37df9 | proposed | RQ-LHW-1877bb | Microcanonical carry mixtures for uniform low-weight representation supply
- IDEA-20260906-c9ac0d | proposed | RQ-GRUMPY-964876 | A CERTIFIED EXHAUSTIVE LADDER FOR THE GRUMPY-GIANTS CONSTANT WITH THE NEGATION MAP AS A SEPARATE ARM: exact all-target means by per-target simulation on Z/l from 2^10 to 
- IDEA-20260906-cf3b76 | proposed | RQ-ECDLP-78dbc5 | THE OFFSPRING-VARIANCE INVARIANCE CONTROL: every point-local distinguishing rule at fixed expected walk length W (in-degree-gated, parent-gated, two-class theta by a poin
- IDEA-20260906-d5defc | proposed | RQ-GRUMPY-964876 | Bellman certificates for nonstationary grumpy-giant schedules
- IDEA-20260906-ee3543 | proposed | RQ-ECDLP-78dbc5 | THE BATCH-RESELECTED FIXED-SIZE TABLE: keep exactly T stored entries, but let the batch's own SOLVED walks be Bernstein-Lange's "larger pool" -- every solved target's ter
- IDEA-20260923-5d07e3 | proposed | RQ-ECDLP-78dbc5 | THE WALK'S IN-DEGREE VARIANCE IS A TABLE CONSTANT: an r-adding walk has in-degree Binomial(r, 1/r) with variance sigma^2 = 1 - 1/r, not the Poisson(1) assumed by IDEA-202
- IDEA-20260923-9e4b71 | proposed | RQ-ECDLP-78dbc5 | THE PREPROCESSING RE-READING OF THE SMALL-ROOT CLOSURE: in the S*T^2 model of RQ-ECDLP-78dbc5 the relation-count and linear-algebra constraints of prime-field windowed in
- IDEA-20260923-c2a85f | proposed | RQ-ECDLP-78dbc5 | THE HUB-COVER CEILING: the basin-partition ceiling C_max(a) of IDEA-20260906-aed829 bounds tables whose online walk STOPS AT THE FIRST distinguished point; in the RQ's ow