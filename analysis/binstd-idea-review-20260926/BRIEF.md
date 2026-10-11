# BRIEF: review of the remaining RQ-BINSTD-b6f698 proposals and a fresh ideation round on index calculus for ECC2K-130

Date: 2026-09-26. Top-level session on branch `claude/index-calculus-ecdlp-ecc2k-rm3mrv`,
base `a36978c037219ffd0fe61b3a1f54ed025f7737f2` (= `origin/main` at session start).
User request (verbatim intent): "review the rest of the ideas for index calculus
for ecdlp on ecc2k 130 ... establish some new novel ideas and concrete experiments examples."

This file is the shared handoff context for six subagent lanes (three reviewers,
three idea generators). It is a working analysis, NOT a ledger record: it changes
no status, approves nothing, and every number in it is a pointer to the record
that carries it. Lane cards are in `handoffs/`.

## 0. Authority and prohibitions (bind every lane)

- Proposals only (AGENTS.md "Standing user authorization"). No hypothesis, no
  experiment contract, no approval, no status change. Designing is not approving.
- NEVER edit an existing record. Reviews go under
  `analysis/binstd-idea-review-20260926/reviews/`; new proposals go to
  `ledger/proposals/<pre-minted id>.yaml` only. IDs are assigned below; never
  mint or invent one.
- No runs. Reviewers may do zero-run arithmetic in Python (a few seconds, no
  solver, no experiment); generators have no shell. Never report an imagined
  outcome, timing, or statistic. "Expected cost" is an order-of-magnitude
  estimate labelled as such.
- Citations carry provenance `recalled | retrieved | kb | internal`
  (`templates/research-records.md`, "Citation provenance"). `retrieved` only if
  you actually fetched and read the source this session. A proposal whose only
  literature is recalled is `novelty_status: unverified`.
- Rule 9 / rule 5: no fabricated commands, outputs, timings, citations, runs.
- Premature closure is a failure mode symmetric with overclaiming
  (`docs/inventor-protocol.md`); a closure needs a named, measured obstruction.

## 1. Where the lane stands (read before anything else)

`RQ-BINSTD-b6f698` (ledger/questions/) is owned by `GOAL-ECDLP2M-001`. The
2026-09-22 batch filed 30 proposals under it. `DEC-20260924-99ce20` ranked all
36 open proposals of the cluster and SELECTED two for design:
`IDEA-20260922-7d6d43` (NISTBIN, 571 cell) and `IDEA-20260922-261004` (BINSTD,
absorbing b19793 and dacfc2). Their designs went through one review round
(`DEC-20260924-124667`, `DEC-20260924-286589`: both REVISE) and are now in a
two-lane revision design batch `BATCH-b67954` (`DEC-20260925-89573b`). Nothing
in this brief touches those three proposals or that batch.

"The rest of the ideas" = the other 26 BINSTD proposals. Their official
disposition and hold text are extracted verbatim per idea in
`ranking-context-DEC-20260924-99ce20.yaml` (same directory). Dispositions:

| disposition | ideas |
| --- | --- |
| queued_for_design (HOLD-B..G) | 1a081a, c07598 (into 1a081a), 6cf862, 29b1c5, 6028ed, 818b73 (into 6028ed), 77bf31 |
| design_after (HOLD-H..N) | d11575, 0e3641 (into d11575), f37254 / 9d12bd / 99294c (into NISTBIN cdca3a), 8ac1ea, 8278db, 2e2a58, 9e5383 |
| return_for_revision (HOLD-K,O,Q,R,S,T) | 1b16d7, 153a90 (into 1b16d7), e3048d, c2bbe6, 7ab503, 2a3771, 493606 |
| hold (HOLD-P,U,V) | 845a77, faa8d2 (into 845a77), 793fd8, 6237e5 |

The ranking's own limitation: "The other 29 pool proposals were weighed at the
level of the ranking report and dedup map, not re-read." This review re-reads
them in full. It is advisory input to the next `/coordinate` selection point
(`DEC-20260924-99ce20` NA-3, NA-4, NA-7); it decides nothing.

## 2. The ECC2K-130 frontier as this corpus has established it

Every new idea and every review is priced against these. Cite the record, not
this brief.

**The object.** ECC2K-130: `y^2 + xy = x^3 + 1` over
`F_2[z]/(z^131 + z^13 + z^2 + z + 1)`, group order `4*l`, `l` a 129-bit prime
(KN-LIT-096, KN-LIT-661e97, frozen source `inputs/BAILEY-2009-541-ECC2K130/`).
`n = 131` is prime: no proper subfield, GHS empty by construction. Cofactor 4
with cyclic 2-Sylow (Z/4), so the quotient chain `E -> E/2E -> E/4E` exists
(the HOLD-O correction to e3048d: `gcd(4,l) = 1` does NOT make every lossy
quotient trivial).

**The matched baseline.** Pollard rho with negation and the 131-fold Frobenius
class reduction: convention `sqrt(pi*r/(4k))`, `k` = Frobenius class order
(CORR-20260922-81aeab as applied in DEC-20260924-99ce20 S2 C2). On ECC2K-130
that is about `2^60.8` iterations (KN-FIND-aa2efc quotes 2^60.8090; Bailey et
al. quote 2^60.9). The original effort ran about `2^58.3` of those iterations
and collected about `2^33` distinguished points (KN-LIT-661e97); DPs were
normalised to the lexicographically smallest of `x, x^2, ..., x^{2^130}` in
normal basis; seeds were random 64-bit, not enumerated.

**The product-law floor (the number every ECC2K-130 index-calculus idea must
confront).** KN-FIND-aa2efc / EV-ICPERF-10c5fc (toy-tier derivation, external
provenance, NOT reviewed in this program): for a decomposition-oracle family at
arity `m`, `relations x targets x oracle = m * 2^131` independently of `dim V`,
so even a FREE oracle costs, against rho's 2^60.81:

| m | free-oracle floor | oracle budget per attempt to tie rho |
| --- | --- | --- |
| 2 | 2^89.25 | none (closed) |
| 3 | 2^68.58 | none (closed) |
| 4 | 2^56.40 | about 2^4.4 group-op equivalents |
| 5 | 2^48.44 | about 2^12.4 |
| 6 | 2^42.85 | about 2^18.0 |
| 8 | 2^35.61 | about 2^25.2 |

Read plainly: on ECC2K-130, arity `m <= 3` cannot beat rho with any oracle; the
lever is arity `m >= 5` with an oracle whose per-attempt cost grows slowly in
`m`, which no algebraic solve this program has measured does (Semaev S_{m+1}
descent costs grow super-exponentially in m; DEC-20260924-99ce20 HOLD-P). Any
proposal that does not state which `m` it targets and what per-attempt oracle
cost it needs is incomplete. (Re-derive the table's arithmetic if you rely on
it; the finding is unreviewed and says so.)

**What is closed at n = 131 (cite before re-proposing).**
- Frobenius-stable F_2-subspaces of F_{2^131}: only dimensions 0, 1, 130, 131,
  because `ord_131(2) = 130` (IDEA-20260918-9abf42, KN-OPEN-095df5). Orbit
  UNIONS of any size exist since 131 is prime; the (representative, shift)
  parameterisation is measured cost-neutral at m = 2, toy tier, unverified
  (KN-FIND-47da4e).
- Quasi-subfield polynomial factor bases with F_2 coefficients at n = 131:
  `beta > 1/2` for every completely splitting `X^{2^{n'}} - lambda(X)` with
  `n'` not dividing `n` (KN-FIND-617d78, derivation tier at
  review-breakthrough; IDEA-20260918-6c07e1); injection bound `|V| <= 2401` at
  `n' = 33, deg lambda <= 7` (IDEA-20260916-3f7a1c). Open: a LOWER bound on
  the solving exponent kappa (KN-OPEN-ac409f); the twisted-coefficient variant
  (KN-TECH-54c38e "Limits").
- Couveignes-Lercier Galois-invariant factor bases: both written constructions
  excluded at n = 131 over F_2; no abelian variety of dim <= 4 has 131 | #A(F_2)
  (KN-OPEN-095df5).
- Rigidity: on a prime-order subgroup no lossy projection propagates under the
  full translation action (IDEA-20260806-c5d183; KN-FIND-ffe1df Theorem C);
  lossy objects under an operation set Sigma are the block systems of <Sigma>
  (IDEA-20260901-863e36). Consequence for sieving: no translation-compatible
  lossy test on the prime-order TARGET subgroup; legs live in the composite
  order-4l group where the trace-parity quotient exists (IDEA-20260922-153a90,
  consolidated into 1b16d7).
- Frobenius on the descended system is an EQUIVARIANCE between conjugate
  targets (the system for sigma(R) is the image of the system for R), not a
  symmetry of one instance (IDEA-20260906-a77711). HOLD-R/S/T returned 7ab503,
  2a3771, 493606 on exactly this.
- On a Koblitz curve `y^2 + xy = x^3 + 1`, `x` is an x-coordinate iff
  `Tr(x) = Tr(1/x)` (substitute y = xz: z^2 + z = x + 1/x^2, solvable iff
  Tr(x + 1/x^2) = 0, and Tr(u^2) = Tr(u)). One-line derivation; re-check it
  before use. This is the membership half of 1b16d7's trace-parity lever.

**What is measured (the concrete cells to reuse).** RQ-CERTBIN-836ce2 owns
measured decomposition cost on prime-degree siblings and has two supported
toy cells: RC-1, `n = 17, m = 2, l = 9`, polynomial-basis V = {deg < 9},
curve `A = 97044, B = 126251`, x(2E) subgroup targets (DEC-20260926-cb4487
SUPPORT); and `n = 19, f = t^19 + t^5 + t^2 + t + 1, m = 2, l = 10,
A = 46693, B = 306147, h = 2` (DEC-20260926-901ea1 SUPPORT). Finding: plain
Macaulay's "not reached at D <= 4" on unsatisfiable S_3 descents is a closure
artifact; the degree-4 mutant closure W_4 refutes 400/400 with verified
certificates (KN-FIND-5a8d3e). Instruments are pure Python, no external
solver: `experiments/EXP-CERTBIN-e94b27/impl/` (gf2n.py, curve.py,
macaulay.py, closure.py, elim.py, oracles_rc1.py, instances.py, selftest.py).
No WDSat, CaDiCaL, msolve, M2, Singular, Sage or Magma binary is installed in
this container; a concrete experiment must either use these Python instruments
or declare the missing engine as a prerequisite, never assume it.

**Ownership (DEC-20260924-4f8a03 R2).** RQ-BINSTD-b6f698 owns the
population-indexed reachability table and structural-emptiness certificates
and NO mechanism. RQ-CERTBIN-836ce2 owns measured decomposition cost on the
Certicom family and its prime-degree toy siblings. FROB owns the Frobenius
mechanism (RQ-FROB-7d8dd4), RELN relation yield, SDEG/DREG solving degree,
SEMBIN Semaev-2015, ICPERF phase costs, SATIC SAT formulation, QSP
(RQ-QSP-f9bbdb) quasi-subfield bases. A NEW proposal picks its `question_id`
by this rule (a measured ECC2K-130-sibling decomposition mechanism belongs to
RQ-CERTBIN-836ce2; a structural certificate or table column to
RQ-BINSTD-b6f698) and says why in `origin.scope`.

## 3. Record conventions for new proposals

Schema: `agents/idea-generator.md` "Required output" plus the lane's extra
fields, exactly as in `ledger/proposals/IDEA-20260922-845a77.yaml` (read it in
full as the exemplar): `question_id`, `added: '2026-09-26'`,
`status: proposed`, `approved_by: null`, `origin {kind, date, scope,
overlap_review}`, `citations[]` with provenance, `citation_note`,
`assumptions`, `proof_search_map`, `predictions`, `minimal_test`,
`falsification_conditions`, `confounders`, `interpretation_limits`,
`heuristic_assumptions`, `target_complexity`, `estimated_cost`,
`asymptotic_claim`, `dominated_by`, `sota_delta {time, memory, data_queries}`,
`frontier_check`, `recommended_priority`, `priority_rationale`,
`first_deliverable`, `next_gate`, `discriminated_from`, `source_refs`,
`id_allocation_provenance` ("ID pre-minted and assigned by the dispatching
session (top-level, 2026-09-26) for lane <TASK id>; not minted by this agent").
Keep titles under about 60 words. YAML must parse (`python3 -c
"import yaml; yaml.safe_load(open(path))"` is what the validator does first).

**The concrete-experiment requirement (user asked for it explicitly).** Every
new proposal's `minimal_test` names a runnable-shaped cell: curve family and
size (`n`, reduction polynomial, `a`, `b`, group-order shape `2l`/`4l`, or one
of the CERTBIN cells above), factor base `V` (dimension, basis, or orbit
union), arity `m`, `l`, number of targets and attempts, seeds policy, the
instrument path, metrics with units, controls (a null object of the same
shape: random V of matched dimension; the ordinary curve of the same size as
the Koblitz control; a relabelled Z/NZ generic-group control where a
group-structure claim is made), the falsification threshold stated before any
run, and an order-of-magnitude cost estimate labelled as an estimate. Include
a three-row outcome table: what a positive, a negative, and an artifact
reading each mean.

## 4. Object-frame constraint block (binding on the generator lanes)

From `docs/object-frame-ideation.md` section 3, pruned to this lane:

- OBJECT FRAME. Every candidate is a PAIR (representation of the point,
  operation set Sigma the tracked object must survive). Name both in
  `mechanism`. Sigma must not be the full translation action (closed by
  IDEA-20260806-c5d183 and KN-FIND-ffe1df Theorem C); if it contains it, the
  candidate is a branching object and says so. Index calculus is Class I,
  partial-action (translation by factor-base elements only).
- TRICHOTOMY. Place each candidate in exactly one class of IDEA-20260806-c5d183
  (partial-action, branching, coordinate-dependent) with a one-line reason.
- LOSSY-PROJECTION TEST against the NAMED operation set (inventor-protocol
  section 2, IDEA-20260901-863e36): what is discarded, why the discard is
  Sigma-compatible, why it is lossy in the representation used.
- PRICE THE ONE OPEN NUMBER: orbit-canonicalisation cost for a quotient
  object; loss L and branching b (IDEA-20260802-002) for a branching one,
  measured on a toy against identity, random-label and relabelled-Z/nZ
  controls.
- OFF-LIMITS AS PRIMARY LENS: F1-F7 of IDEA-20260802-002, plus the lane
  closures in section 2 (Frobenius-stable subspaces at 131; F_2-coefficient
  QSP at 131; Couveignes-Lercier at 131; bounded-degree algebraic factor bases
  of KN-OPEN-020). A candidate that uses one as a component names it and
  states what is added.
- FACTOR-BASE ESCAPE. Any factor base names its KN-OPEN-020 class
  (high-degree, implicit-membership, target-dependent) and charges
  description, membership, relation, descent, time and memory.
- REPRESENTATION CLASS. R1/R2/R3 of RQ-ECDLP-623a32 and the attack stage
  whose charged cost changes.
- PROOF SEARCH MAP before any compute (KN-TECH-080): exact bottleneck,
  baseline embedding, observation collision, quantifier order, method ceiling
  with a nearby-object control.
- HONEST ACCOUNTING: novelty `unverified` unless checked; `dominated_by` and
  `sota_delta`; `target_complexity` with exponents; every heuristic with a
  validation route. A lane that returns fewer ideas still returns the
  inventor-protocol section 5 block.
- NO COMPUTE, NO STATUS CHANGE.

## 5. Lane assignments

Reviewer lanes (agent: general-purpose, adversarial reading, output one YAML per
idea to `reviews/<IDEA id>.yaml` using the schema in section 6, plus
`reviews/<TASK id>-summary.md`):

| lane | ideas |
| --- | --- |
| TASK-20260926-002d0e (R1, queued_for_design) | 1a081a, c07598, 6cf862, 29b1c5, 6028ed, 818b73, 77bf31 |
| TASK-20260926-5d1a51 (R2, design_after) | d11575, 0e3641, f37254, 9d12bd, 99294c, 8ac1ea, 8278db, 2e2a58, 9e5383 |
| TASK-20260926-843cf5 (R3, revision and hold) | 1b16d7, 153a90, e3048d, c2bbe6, 7ab503, 2a3771, 493606, 845a77, faa8d2, 793fd8, 6237e5 |

Generator lanes (agent: idea-generator; 4 pre-minted IDs each; write each
complete record to `ledger/proposals/<id>.yaml`; return the ranking rationale
and the section-5 honest-accounting block in the final message and ALSO write
it to `reviews/<TASK id>-generator-report.md`):

| lane | seam | IDs |
| --- | --- | --- |
| TASK-20260926-995431 (G1) | THE ARITY LEVER AGAINST THE PRODUCT LAW: decomposition oracles whose per-attempt cost grows polynomially (or better) in m at fixed field size, so that m >= 5 becomes priceable on ECC2K-130 -- group-arithmetic meet-in-the-middle and k-list constructions (what stops Wagner's k-tree on a prime-order group is exactly Theorem C: say what replaces the additive low-bits coordinate), tau-adic / Z[tau]-module structure of a Koblitz curve as an operation set, orbit-union factor bases with orbit arithmetic, double-large-prime and graph/cycle compositions (GTTD form; HOLD-Q's revision route) and rho-plus-index-calculus hybrids. Every idea states its target m and the per-attempt oracle budget it must meet from the section-2 table. | IDEA-20260926-136bd3, IDEA-20260926-178821, IDEA-20260926-1db0e8, IDEA-20260926-4b65e3 |
| TASK-20260926-aa3c9f (G2) | THE SOLVER-SIDE ASYMMETRY AT THE MEASURED CERTBIN CELLS: the per-attempt cost is dominated by UNSATISFIABLE attempts (success probability is tiny), so cheap refutation is the lever -- mutant-closure / early-abort refutation as an attempt filter, the sat/unsat cost asymmetry, degree-fall structure of S_3 and S_4 descents, amortising elimination across many targets (respecting IDEA-20260906-a77711's equivariance reading and discriminating from IDEA-20260923-5d0b8e's trace-replay), normal-basis versus polynomial-basis descent, trace-conditioned factor bases (Tr(x) = Tr(1/x) on Koblitz), the E/2E and E/4E quotient chain of the cofactor (HOLD-O's corrected reading of e3048d). Concrete experiments reuse `experiments/EXP-CERTBIN-e94b27/impl/` and the RC-1 / n = 19 cells wherever possible. Question owner is usually RQ-CERTBIN-836ce2. | IDEA-20260926-89886c, IDEA-20260926-917981, IDEA-20260926-a79052, IDEA-20260926-ae8f0a |
| TASK-20260926-b3c93a (G3) | REPRESENTATION AND RELATION-COLLECTION OBJECTS SPECIFIC TO ECC2K-130'S OWN STRUCTURE (R1/R2/R3 of RQ-ECDLP-623a32): the curve is defined over F_2 so E(F_{2^131}) is a Z[tau]-module and every relation has 131 conjugates; the 2^33 already-collected distinguished points and their normal-basis normalisation as data; x-only (Kummer-with-Frobenius-classes) relation search; alternative descent coordinates (normal basis, Gaussian normal basis, a tower-free redundant representation) as a controlled confound in solving degree (HOLD-I's generator seam); target-dependent factor bases (KN-OPEN-020's open class) that read the curve coefficients b = 1 (answering 1a081a's curve-blindness); certificates and controls for each. | IDEA-20260926-b48c9d, IDEA-20260926-b6cc43, IDEA-20260926-cafcf1, IDEA-20260926-d128eb |

Spare IDs (unassigned, held by the top-level session): IDEA-20260926-d1f6bf,
IDEA-20260926-ef2bd8. Spare handoff id: TASK-20260926-c1e939.

Generators must not duplicate the 30 filed BINSTD proposals, the CERTBIN
proposals (`rg -l RQ-CERTBIN-836ce2 ledger/proposals`), or the FROB / QSP /
SEMBIN / ICPERF proposals that mention ECC2K-130 (`rg -li ecc2k ledger/proposals`
lists 29). Read titles and claims of the nearest ones and fill
`discriminated_from`.

## 6. Review schema (reviewer lanes)

```yaml
review:
  idea_id: IDEA-20260922-xxxxxx
  reviewed_at: '2026-09-26'
  reviewer_lane: TASK-20260926-xxxxxx
  ranking_context:            # copied from ranking-context-DEC-20260924-99ce20.yaml
    rank: 0
    disposition: ''
    hold_id: ''
  claim_restated: >-          # one paragraph, in your own words
  core_argument_check:        # every load-bearing step; re-derive any number
    - step: ''
      verdict: holds | defective | unchecked
      note: ''
  verdict: sound | sound_with_corrections | defective | dominated | superseded_by_program_state
  defects:
    - what: ''
      where: ''               # field of the record
      fix: ''
  ecc2k130_bearing: >-        # what it says about ECC2K-130 specifically, priced against
                              # the 2^60.8 matched rho and the product-law floor at its m
  agreement_with_hold: agrees | disagrees
  agreement_note: ''
  concrete_experiment:        # the sharpest test that would settle the idea
    cell:
      curve: ''               # family, n, reduction polynomial, a, b, order shape, or a CERTBIN cell id
      m: 0
      l: 0
      factor_base: ''
      targets: ''
      seeds: ''
    instrument: []            # paths under this repository, or 'missing: <engine>'
    procedure: []             # numbered steps
    metrics:
      - name: ''
        unit: ''
        definition: ''
    controls: []
    outcomes:
      positive: ''
      negative: ''
      artifact: ''
    falsification_threshold: ''
    estimated_cost:
      implementation: low | medium | high
      compute: ''             # order of magnitude, labelled estimate
    zero_run_prerequisites: []
  successor_seam: >-          # what NEW proposal this review seeds, or 'none'
  records_read: []
  not_read: []
```

Per-lane summary (`reviews/<TASK id>-summary.md`): a table (idea, verdict,
agrees-with-hold, one-line concrete experiment, successor seam) and a short
ranked list of which of the lane's ideas are worth designing next and why,
with the arithmetic checks you performed listed by record.
