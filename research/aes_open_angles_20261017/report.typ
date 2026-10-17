#set page(paper: "a4", margin: 16mm)
#set text(font: "DejaVu Sans", size: 9pt)
#set table(inset: 3pt)
#show table: set text(size: 7.4pt)
#set par(justify: false)
= AES: open attack angles and a native discovery laboratory
<aes-open-attack-angles-and-a-native-discovery-laboratory>
17 October 2026. #strong[Advisory research assessment and engineering
work], not an official goal transition, a security proof, or a claim to
have broken AES. The implementation and first frozen synthetic suite are
in
#link("https://github.com/aburan28/cryptanalysis/tree/codex/aes-distinguisher-research/tools/aes-discover")[`aburan28/cryptanalysis`].
The native mirror is applied in `crypto` under current standalone
authorization; its verification/delivery and separate scientific
admission obligations are tracked in
#link("../../problems/aes-lab-conductor-and-campaign-admission.md")[the problem record].

== Assessment
<assessment>
The strongest research direction is to track #strong[relations among
several texts, their joint compatibility, and key-dependent
constraints], while building an instrument that can distinguish these
mechanisms from data-generation and search artifacts. Counting active
S-boxes or running a larger undisciplined search is insufficient. A
useful binary needs a proposal engine, an exact cipher identity, a
frozen observable, independent validation and complete cost records.

Recent primary literature gives concrete reasons to continue structural
work. Shin et al. report a seven-round secret-key structural
distinguisher with approximately `2^126.2` data, time and memory and
77.8% modeled success, with small-scale verification. Yan et al. report
exchange/shift related-differential distinguishers through seven rounds.
These results identify additional structure; their round counts and
access models do not establish a practical attack on the 10/12/14-round
standard ciphers. Both sources were inspected at abstract level, not
independently reproduced.
#link("https://eprint.iacr.org/2026/980")[S03],
#link("https://eprint.iacr.org/2026/1039")[S04]

The cross-ratio preprint reports improved matching for a seven-round
AES-128 meet-in-the-middle attack and reduced-round quartet
distinguishers. It explicitly does not claim a threat to full AES. Our
component experiment tests a known inversion identity and the AES
output-affine layer; it does #strong[not] reproduce that complete
construction. Full algorithm retrieval remains a prerequisite to an
attack-level reproduction.
#link("https://eprint.iacr.org/2026/1549")[S05]

The frontier is consequently open to better mathematics and engineering,
with no basis here for predicting an imminent practical full-AES break.
We preserve costly intermediate advantages as legitimate research
outcomes: a reduced-round result, a memory reduction, or a model
correction can matter without immediately recovering a practical key.
Each needs its own evidence and accounting.

== Coverage of attack directions
<coverage-of-attack-directions>
This is a broad taxonomy, not a proof that every conceivable method has
been enumerated. `Open` means a specified research obligation remains;
it does not mean a weakness is established. Priorities below are
advisory to this tool project and do not reorder the existing official
AES campaign queues.

#figure(
  align(center)[#table(
    columns: 4,
    align: (auto,auto,auto,auto,),
    table.header([Direction], [Concrete open question /
      obstruction], [First discriminating experiment], [Access and
      evidence boundary],),
    table.hline(),
    [Differential trails and hulls], [How much endpoint probability is
    missed by one trail or a capped beam, and which local paths are
    actually compatible?], [Exact toy endpoint enumeration versus
    DDT-model/beam mass, then per-key AES endpoint tests], [Chosen
    plaintext; local DDT products are not fixed-key probabilities or
    bounds on a hull],
    [Related differences, exchange and joint quartets], [Can a compact
    joint relation predict more than independent marginal
    events?], [Count marginals, intersections and complete quartet
    predicates on a complete toy domain], [Keep CP and adaptive CP
    distinct; published seven-round costs are not a local-run budget],
    [Cross-ratio / algebraic matching], [Which information must survive
    the real output-affine map and multi-byte mixing for a useful
    match?], [Local inversion/affine ablations, then exact super-box
    witnesses], [Component identity does not imply complete-round
    propagation; reject degenerate quartets],
    [Boomerang / rectangle / retracing], [Which middle-switch
    dependencies amplify, cancel or forbid the proposed
    quartet?], [Exact BCT including its nonzero diagonal; fixed-delta
    returns against a consistent forward/inverse PRP], [Adaptive inverse
    access is a stronger model than CP; never choose delta from the
    observed ciphertext pair],
    [Differential-linear and linear hulls], [Do multi-round dependencies
    change the prediction from separate differential and linear
    scores?], [Exact local DL tables and direct toy joint counts before
    combining scores], [A correlation/model product requires its
    dependency assumptions to be checked],
    [Integral / higher-order / division property], [Which set summaries
    yield sound balance predictions, and which are merely permitted
    abstract trails?], [Known three-round 256-text integral, one-member
    mutants, exact toy transition checks and next-round decay], [A
    solver-allowed trail is not a balance certificate; a failed search
    is not security],
    [Impossible differentials / zero correlation], [Can exact state/key
    constraints rule out a new class beyond existing scoped
    exclusions?], [SAT witness/UNSAT-certificate replay against complete
    toy enumeration], [Zero observed events is not impossibility;
    existing one-word-in/one-word-out exclusions must not be rebranded
    as new],
    [Key schedule / related-key / weak-key classes], [Does a statistic
    depend on real expansion, a small key subset, or the data path
    alone?], [Real schedule versus independent round keys, with per-key
    histograms; related-key panels separately], [Related keys need a
    related-key ideal-cipher comparison and do not establish an ordinary
    single-key attack],
    [DS-MitM / partial sums / bicliques], [Can matching constraints
    lower complete time/data/memory costs?], [Reproduce a named matching
    subproblem; count offline work, online work and large-table accesses
    separately], [A cheaper subroutine is not a complete key-recovery
    improvement; biclique shortcuts remain enormously expensive],
    [Algebraic / SAT / Gröbner / hybrid solving], [Can exact value
    constraints or elimination exploit structure beyond a compact
    equation description?], [Exhaustive S-box encoding equivalence,
    planted toy witnesses, solver counting and independently checked
    certificates], [Timeout is not UNSAT; small-scale/known-bits results
    do not establish full-key AES scaling],
    [Learned proposal/statistic models], [Is there incremental
    information beyond classical histograms on untouched keys and
    structures?], [Native key-disjoint data, simple baselines, shuffled
    labels, matched PRPs, then one untouched final
    test], [Training/checkpoint selection and negative-generator
    artifacts can manufacture accuracy; charge all training and
    inference],
    [Invariants, subspaces and alternative representations], [Is the
    observable genuinely lossy and useful, with valid propagation under
    the actual operations?], [Equal-observable collision pairs passed
    through each real layer; matched random-bijection/null
    ablations], [Inversion is not the complete AES S-box; preserving
    values differs from propagating differences],
    [Quantum search / structured quantum cryptanalysis], [What changes
    under Q1 versus coherent Q2 access, with realistic
    circuit/depth/memory accounting?], [Reproduce resource estimates on
    reversible S-box / structured-search subproblems], [Separate from
    this classical binary and from practical quantum hardware; no
    numerical quantum claim is made here],
    [Faults, leakage, white-box and protocol/mode failures], [What
    additional access or misuse explains an observed
    compromise?], [Separate synthetic implementation fixtures and
    explicit access models], [These are important security tracks but do
    not by themselves demonstrate a mathematical core-cipher break],
  )]
  , kind: table
  )

Sources for these families include the designers\' wide-trail and
plateau analyses, BCT and differential-linear dependency work,
state-propagation/SAT, small-scale algebraic work, DS-MitM, related-key,
yoyo and quantum analyses.
#link("https://cs.ru.nl/~joan/papers/JDA_VRI_Wide_2001.pdf")[S02],
#link("https://cs.ru.nl/~joan/papers/JDA_VRI_Plateau_2007.pdf")[S07],
#link("https://eprint.iacr.org/2025/396")[S08],
#link("https://eprint.iacr.org/2018/161")[S09],
#link("https://eprint.iacr.org/2024/255")[S10],
#link("https://eprint.iacr.org/2020/1093")[S11],
#link("https://eprint.iacr.org/2022/695")[S12],
#link("https://cic.iacr.org/p/2/4/38")[S06],
#link("https://eprint.iacr.org/2009/317")[S13],
#link("https://eprint.iacr.org/2017/980")[S16],
#link("https://eprint.iacr.org/2019/272")[S17].

== What the first binary implements
<what-the-first-binary-implements>
The native Rust `aes-discover` crate implements AES-128/192/256 with
explicit rounds and last-round MixColumns, exact DDT/LAT/BCT summaries,
bounded value-level beam proposals, empirical endpoint discovery, hashed
frozen validation, integrals, local quartet ablations, key-schedule
differences, fixed-delta boomerang checks, and JSONL dataset export.
Search considers byte and bit equalities of XOR projections of output
differences. This is a first finite search family, not a generic solver
for every taxonomy row.

The validator fixes a key across queries, uses new keys and plaintexts,
excludes duplicate/reversed pairs, retains every key/event row and tests
an independent lazy PRP. It uses conservative Chernoff bounds with
finite-query coupling slack and family correction, rather than a
sparse-cell normal approximation. A candidate must pass its frozen
direction on every tested key, with the null family passing. No
universal-key or optimality statement follows. The outer command card
binds executable, sources, lockfile, protocol, exact commands and
transcripts. Hashing an artifact does not independently certify its
execution.

The first suite is a #strong[separate engineering/measurement study]. It
searches sixteen input differences per family and validates two events
on eight new keys. Twelve predeclared families include ordinary
full-round AES and random-control families, alongside the reduced-round
positive controls. Other commands probe known integrals and component
relationships. The native engine and frozen card are in the companion
`cryptanalysis` PR; actual raw data and source bindings are published
there. See
#link("../../experiments/aes-distinguisher-lab-20261017/README.md")[the experiment adapter].

== Why the instrument comes first
<why-the-instrument-comes-first>
The source audit found issues that a new experiment should not inherit:

- Existing `milp.rs::enumerate_low_weight_trails` contains hard-coded
  small-round counts despite describing a search. It is not an
  exhaustive search certificate.
- Existing `differential.rs::propagate_one_round` marks an entire output
  column active if any input is active. For multiple active inputs, this
  is a possible activity visualization, not exact propagation. Two-byte
  cancellations exist; branch number five does not force all four
  outputs active in that case.
- Existing boomerang uniformity code skips `a == d`\; the definition
  only excludes zero differences. A separate boomerang path sets output
  delta equal to the realized ciphertext difference and therefore
  returns for every permutation.
- Historical neural iterator code restarts a deterministic stream on
  each iterator creation, and repeatedly selects checkpoints using one
  evaluation set. Its independent-random-output negative class also
  differs from a shared PRP oracle. These are source findings, not a
  claim that every historical result has been experimentally refuted.

The new native path avoids these constructions. Historical files remain
unchanged. KN-FIND-028/029 reinforce the same boundaries: MixColumns
supplies a particular linear map, not every possible linear
transformation; local value geometry is not difference propagation;
actual exercised coverage and sibling nulls matter. No official
conclusion is revised by this source audit.

== Ranked follow-up experiments
<ranked-follow-up-experiments>
The machine-readable cards in
#link("hypotheses.json")[`hypotheses.json`] contain the object,
prediction, controls, falsification, resource envelope and acceptance
criteria. Their novelty is #strong[unverified] and `sota_delta` remains
null.

+ Expand the native instrument panel: mutation/no-op controls, more null
  keys, independent implementation replay and counterexamples for every
  convention.
+ Enumerate a complete small-scale domain to compare endpoint hulls,
  beam proposals and per-key trail feasibility. Plateau behavior makes
  pooled-only claims particularly risky.
  #link("https://cs.ru.nl/~joan/papers/JDA_VRI_Plateau_2007.pdf")[S07],
  #link("https://eprint.iacr.org/2025/396")[S08]
+ Implement the #strong[full] joint-quartet and related-difference
  predicates after retrieving their algorithms, then measure joint
  rather than multiplied marginal events.
  #link("https://eprint.iacr.org/2026/980")[S03],
  #link("https://eprint.iacr.org/2026/1039")[S04]
+ Connect local cross-ratio information to a precisely defined
  multi-byte matching object; expose affine-map and pole cases
  explicitly. #link("https://eprint.iacr.org/2026/1549")[S05]
+ Add conditional boomerang / differential-linear switch checks and a
  certificate-producing SAT backend.
  #link("https://eprint.iacr.org/2018/161")[S09],
  #link("https://eprint.iacr.org/2024/255")[S10],
  #link("https://eprint.iacr.org/2020/1093")[S11]
+ Extend integral certificates and schedule-isolating sibling controls,
  then attempt learned ranking only after the native classical baselines
  are sound. #link("https://eprint.iacr.org/2024/1300")[S15]

These are proposals, not completed experiments. The existing three
campaign queues retain their priorities. No scientific state changes or
approvals are recorded here, and no held D-2 arm is launched.

== Claim screening and remaining gaps
<claim-screening-and-remaining-gaps>
A credible new claim must identify the exact game and access model, full
round count, unknown key bits, fixed versus key-averaged behavior,
selected versus untouched data, complete probability or success
criterion, preprocessing and per-target work, memory and memory
accesses, and an independent reproducible check. A “faster than
exhaustive search” headline alone does not establish practicality; a
fixed-key trail is not a differential hull. Historical biclique results
illustrate the distinction.
#link("https://eprint.iacr.org/2011/449")[S14]

An August 2026 black-box preprint reports experiments with up to 80
unknown key bits when the other 48 are known, then extrapolates to the
full-key case. We do not treat that extrapolation as an accepted
full-AES break. Its full argument has not been independently reviewed
here. #link("https://arxiv.org/abs/2608.22904")[S18]

Open gaps are explicit: exact SAT/UNSAT certification, exhaustive toy
hull accounting, full published quartet constructions, learned-model
training, GPU search, controlled external performance comparisons, and
official campaign admission are not implemented by this first release. A
small negative search settles none of them. No new mathematical theorem
or Lean proof is claimed.

== Sources and provenance
<sources-and-provenance>
#link("sources.json")[`sources.json`] records URLs, read scope,
retrieval date and provenance. Most ePrint sources were inspected
through their primary abstracts; their full PDFs returned HTTP 403 in
this environment. The CiC DS-MitM PDF and the designers\' plateau paper
were retrieved and relevant sections inspected. An abstract-only read
supports a report of the authors\' claims, not an independent
verification of their construction or costs.

The committed AES goal heads and relevant RQ/KN records were read at
`crypto-autoresearcher@509d83b69a1f65230422e58bf4491cbbec1ad5da`, with
source audits at `crypto@c6d64436` and `cryptanalysis@6346d31a`. The
partial symmetric frontier was consulted without modifying it. No
callable `search_knowledge` or `find_related` MCP was available; the
sparse focused scan is not a complete corpus or novelty audit.
Independent advisory and software reviews were used; they are not an
official scientific review round.

Existing canonical curve graphs, IC scoreboards and performance
leaderboards remain unchanged: this assessment adds no curve, IC
measurement or speed claim. The editable
#link("research-map.svg")[research map] distinguishes implemented
instruments from proposed extensions. The report PDF includes the map
and source links. A software merge or green tests do not promote a
scientific hypothesis.

#box(image("research-map.svg"))
