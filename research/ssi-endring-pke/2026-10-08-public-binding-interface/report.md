---
title: "Public-binding interfaces for EndRing PKE"
subtitle: "GOAL-SSI-2fa82a / BATCH-fc23a6"
date: "2026-10-08"
geometry: margin=0.72in
fontsize: 10pt
colorlinks: true
---

# Result

This batch encoded the requested **propose -> evaluate -> propose if useful ->
evaluate** methodology at the public-binding layer of an EndRing-based PKE
search. Two mutually blind producers generated materially different candidate
relations. Their bytes were frozen before a validator, red team, and T5
reviewer independently evaluated the five prespecified joints. Both raw,
candidate-specific independence checks passed. [Method] [Snapshot] [Initial]

The result is **two typed obstructions, zero surviving public-binding
interfaces, and zero PKE candidates**. Candidate A, RCF-Bind, has four broken
joints and one inconclusive joint. Candidate B, BDEB, also has four broken
joints and one inconclusive joint. No single repair could change either
disposition, so the optional revision slot was skipped under the frozen early-
stop rule. [Final] [Decision]

No secure or novel PKE, IND-CPA/IND-CCA theorem, complete reduction to the
supersingular endomorphism-ring problem, implementation, parameter set,
benchmark, or impossibility theorem was established. The round was analytical
and zero-run: no scientific, implementation, formalizer, experiment,
benchmark, or parameter-selection run occurred. Candidate-specific failures
do not imply that EndRing PKE is impossible. [Final]

![Candidate and review flow. Yellow nodes are proposals, blue is independent
review, red is a scoped rejected interface, and green is the controlled stop
and future action. The diagram is navigation, not evidence.](interface-flow.svg){ width=88% }

# Methodology encoded in the repository

The batch begins before a PKE wrapper. A candidate must define a public,
polynomial relation

```text
R_E(x, y) in {0,1}
```

on a bare supersingular curve `E` drawn from the exact declared EndRing
challenge distribution. `Sample` and `Eval` may use only public information.
For every honest `y`, every accepted preimage must lie in one public
equivalence class, and that equivalence must preserve the functionality used
for actual-message recovery. One uniform `Inv(E,B,y)` must work for **every**
valid complete evaluable basis `B` of `End(E)`, including arbitrary valid
`GL_4(Z)` presentation changes. [Method] [Schema]

The security direction is frozen as

```text
scheme attacker
    -> accepted preimage or functionality-preserving class
    -> complete evaluable basis of End(E).
```

The reverse implication—an EndRing solver can decrypt or invert—is an attack
route, not a security reduction. Interface one-wayness is not automatically
IND-CPA. Complete-ring necessity needs either a non-factorization result over
the declared smaller-witness class or a theorem reconstructing a saturated,
evaluable rank-four ring from the smaller witness. [Method]

Two blind proposal tasks were assigned different central relation families.
Candidate A could not use a walk endpoint, selector, parity mask, or finite
point-evaluation tuple. Candidate B had to differ in domains, relation,
equivalence, public operations, and inverse. After the immutable snapshot,
T1--T2, T3--T4, and T5 had separate owners. Composition copied owner verdicts
without voting. A third proposal was permitted only if one smallest repair
could plausibly change a disposition. [Plan] [Snapshot]

| Joint | Frozen security/interface question |
|---|---|
| T1 | Bare-`E` public generation and fixed-`y` binding |
| T2 | Every-basis inversion and message invariance |
| T3 | Complete-ring necessity versus smaller witnesses |
| T4 | Quantitative attacker-to-complete-ring extraction |
| T5 | Syntax, history, controls, sources, and prior art |

# Candidate A: RCF-Bind

RCF-Bind proposes a characteristic fiber indexed by the reduced trace and
norm `(t,n)` of a primitive noncentral endomorphism `alpha`. The accepted pair
contains `alpha` and its dual and satisfies

```text
alpha + alpha_dual = [t]
alpha * alpha_dual = [n]
Delta = t^2 - 4n < 0.
```

The intended public equivalence identifies all accepted maps in one fixed
trace/norm fiber through rational conjugacy in the definite quaternion
algebra. This differs materially from endpoint and finite-evaluation
relations. The producer correctly stopped with a typed obstruction rather
than claiming a construction. [A]

The T1 owner independently rederived the conditional conjugacy argument, but
T1 **breaks** because the packet supplies no public
`SampleNoncentralEnd(E,D;rho)`, exact law, runtime, or success bound. Scalars
and immediate isogeny/dual backtracks have `Delta=0` and are rejected, so they
do not fill this first missing arrow. [VA]

T2 is **inconclusive**. Trace and norm are invariant under a valid unimodular
basis change, and a packing argument bounds the number of norm-bounded lattice
elements by `O(D^2)`. But no uniform inverse is specified with basis-input and
map-conversion costs, full domain checks, retry guarantees, or a recovery
function constant on every accepted conjugacy fiber. Conditional conjugacy
does not make arbitrary encoding- or point-action-based message recovery
invariant. [VA]

T3 and T4 **break**. One accepted `alpha` gives an evaluable embedding of a
quadratic order; all polynomials in `alpha` and its dual remain in a
two-dimensional rational algebra. That is strictly less output than a
saturated rank-four basis. The packet has neither bare-`E` challenge sampling
nor a theorem turning accepted attacker outputs into noncommuting rank growth,
index certification, saturation, and evaluable full-ring generators. No
uniform extraction probability, loss, runtime, or abort bound is supplied.
[RA]

T5 **breaks** because the exact field/extension and rational-map byte grammar,
unique function-field normal form, failure precedence, oracle history, and
primary-source novelty boundary are incomplete. The review also corrected
categorical absence language: a missing algorithm is “not supplied” or “not
established,” not proved nonexistent. [T5A]

# Candidate B: BDEB

BDEB proposes binding a degree-at-most-`D` endomorphism by its full action on
an ordered list of `M=4D+1` public points. Its honest support chooses scalar
maps `[a]`; the transcript contains the points and images, and inversion
enumerates the bounded scalar family. At the reviewed semantic level, the
degree parallelogram identity and kernel-size bound can force two genuine
degree-bounded maps agreeing on all listed points to be equal. [B] [VB]

T1 is nevertheless **inconclusive**. The exact public point-draw law,
positive parameter regime, capped success probability, root selection,
runtime, and common retry accounting are not fully fixed. Semantic map
equality also does not substitute for a canonical byte representation. [VB]

T2 **breaks**. The stated inverse first validates the supplied complete basis,
so its literal runtime cannot be invariant under arbitrary `GL_4(Z)` shears
whose encodings grow without bound. More importantly for the construction,
the successful public enumeration ignores the basis entirely. [VB]

T3 and T4 **break** decisively on the honest support. The scalar preimage is
publicly recoverable; arbitrarily many recovered witnesses remain on the
rank-one scalar line and supply no noncentral generator, rank-four order,
index, saturation, or evaluable complete basis. The simulator already knows
the scalars it sampled. Fresh coins and repeated success cannot turn this
rank-one certificate into full EndRing output, and no generic IND-distinguisher
to map-preimage compiler is supplied. [RB]

T5 **breaks** because exact map/mask serialization, quotient-function-field
normalization, algorithm-specific malformed-input behavior, attempted-call
rather than accepted-call accounting, coin visibility, and primary-source
overlap remain incomplete. These specification gaps are additional to, not a
repair for, the scalar-support collapse. [T5B]

# Evaluation matrix and revision decision

| Candidate | T1 | T2 | T3 | T4 | T5 | Disposition |
|---|---|---|---|---|---|---|
| RCF-Bind | breaks | inconclusive | breaks | breaks | breaks | typed obstruction |
| BDEB | inconclusive | breaks | breaks | breaks | breaks | typed obstruction |

The raw independence checker passed separately on the three owner reports for
each candidate: every joint was owned and attested, blindness was respected,
and controls were declared. Before any review returned, the coordinator added
candidate-specific plans containing checker-required `blind_rederivation`
quantity and `blind_from` fields. `PD-PLAN-SPLIT` is disclosed as a checker-
shape-only correction; candidate bytes, owners, attacks, and evidence scope
did not change. [Initial]

No revision was dispatched. Repairing only RCF-Bind's sampler would leave its
T2 unresolved and T3--T5 broken. Replacing BDEB's scalar support would replace
the mechanism that makes its public sampling and inversion work, forcing new
`Sample`, `Inv`, extraction, and view definitions. The apparent shared gap—
public noncentral generation outside an enumerable proper witness **and**
preimage-to-complete-ring reconstruction—contains two independent missing
algorithms. It is a new architecture, not one bounded repair. [Gap] [Decision]

# Controls and inherited correction scope

The analytical reviews exercised leaked-witness/public-inverse, scalar and
backtrack, finite-action/proper-witness, oriented/torsion-aided nearby-object,
valid basis-shear, repeated-output rank, and full-rank-but-nonsaturated-order
controls. These show where the submitted reasoning fails; they do not prove
unconditional separations between OneEnd-like and EndRing problems. [RA] [RB]

The batch preserved the authorized J4/J5 correction semantics as inherited
regression controls. The additive mapping remains printed pages 69--70 to PDF
74--75, printed 74 to PDF 79, and printed 75/Lemma 6.12 to PDF 80 for the
previously recorded source bytes. No fresh primary PDF read occurred here and
historical J4/J5 verdicts were not recoded. Likewise, normalized-`x(X)` claims
retain their fixed-model, simultaneous-normalization, `p>3`, and exact-order
`ord(P)=N>4D` scope; weakened order premises are controls, not valid-input
attacks. No digit-loop output is inferred without complete tie-handling
pseudocode. [Correction] [Method]

# Requirement-to-evidence table

| Requirement | Outcome | Evidence |
|---|---|---|
| Two materially distinct blind proposals | complete | [A], [B] |
| Immutable producer snapshot | complete | [Snapshot] |
| Independent T1--T5 owner review | complete | [VA], [VB], [RA], [RB], [T5A], [T5B] |
| Raw candidate-specific independence checks | pass twice | [Initial] |
| Compose without voting | complete | [Initial] |
| At most one decision-changing revision | skipped by frozen early-stop rule | [Gap], [Decision] |
| Exact final counts and claim boundary | complete | [Final] |
| Primary-source novelty review | not performed | [T5A], [T5B] |
| Secure EndRing PKE or surviving interface | **not established** | [Final] |

# Exactly one next action

Study **ENDRING-PUBLIC-NONCENTRAL-SAMPLER-FEASIBILITY** before another PKE
wrapper. On the exact bare-`E` EndRing distribution, either supply a polynomial
public sampler for a canonically encoded noncentral evaluable endomorphism—with
an exact law, inverse-polynomial success, runtime, retry bound, and controls—
or retain a scoped obstruction at its first missing arrow. The output must not
collapse to scalars, immediate backtracks, a leaked orientation/ideal/tag, or
another efficiently enumerable proper witness family. [Final]

This action deliberately excludes the separate preimage-to-complete-ring
reconstruction problem. It does not launch automatically and, even if solved,
would not itself establish a secure PKE or EndRing reduction. [Final]

# Source index

- [Method] [Frozen methodology](methodology.md)
- [Schema] [Binding-interface schema](binding-interface-schema.yaml)
- [Plan] [Initial review plan](../../../coordination/design/TASK-20261008-46d7e4/review-preparation/review-plan.yaml)
- [A] [RCF-Bind packet](../../../coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-ba8247/candidate.md)
- [B] [BDEB packet](../../../coordination/design/TASK-20261008-46d7e4/tasks/TASK-20261008-896b35/candidate.md)
- [Snapshot] [Immutable producer snapshot](../../../coordination/design/TASK-20261008-46d7e4/archives/TASK-20261008-eb1230/snapshot-receipt.json)
- [VA] [Candidate A T1--T2 review](../../../coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-417e47/candidate-a-review.yaml)
- [VB] [Candidate B T1--T2 review](../../../coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-417e47/candidate-b-review.yaml)
- [RA] [Candidate A T3--T4 review](../../../coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-5b590b/candidate-a-review.yaml)
- [RB] [Candidate B T3--T4 review](../../../coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-5b590b/candidate-b-review.yaml)
- [T5A] [Candidate A T5 review](../../../coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-f0f824/candidate-a-review.yaml)
- [T5B] [Candidate B T5 review](../../../coordination/design/TASK-20261008-46d7e4/reviews/TASK-20261008-f0f824/candidate-b-review.yaml)
- [Initial] [Initial composition](../../../coordination/design/TASK-20261008-46d7e4/composition/TASK-20261008-2b605a/composition.yaml)
- [Gap] [No-revision gap packet](../../../coordination/design/TASK-20261008-46d7e4/composition/TASK-20261008-2b605a/gap-packet.yaml)
- [Decision] [Interim no-revision decision](../../../ledger/decisions/DEC-20261008-884ec2.yaml)
- [Correction] [Inherited J4/J5 correction addendum](../2026-10-07-trapdoor-interface/legacy-correction-addendum.md)
- [Final] [Final composition](../../../coordination/design/TASK-20261008-46d7e4/composition/TASK-20261008-2464ec/final-composition.yaml)
