---
title: "Basis-independent EndRing trapdoor-interface funnel"
subtitle: "GOAL-SSI-2fa82a / BATCH-cb7b9a"
date: "2026-10-07"
geometry: margin=0.72in
fontsize: 10pt
colorlinks: true
---

# Result

This batch ran the requested **propose -> evaluate -> gap-feed -> propose ->
evaluate** method at the interface layer that blocked the preceding EndRing
PKE candidates. It generated three typed `Trap_E` packets, froze both review
inputs, and obtained independently owned T1--T5 verdicts. The result is **zero
surviving trapdoor-interface candidates and zero PKE finalists**. [Method]
[Final]

No secure PKE, correctly directed reduction to EndRing, novelty result,
implementation, parameter set, or impossibility theorem was established. All
work was symbolic: zero scientific, implementation, formalizer, benchmark, or
parameter-selection runs. The packets are scoped obstructions to their exact
interfaces, not evidence that EndRing PKE cannot exist. [Final]

![Candidate and review flow. Yellow nodes are proposals, blue nodes are
independent review, red nodes are scoped failures, and green nodes are the
selected gap/next action. The diagram is navigation, not evidence.](interface-flow.svg){ width=100% }

# Method

The frozen method studies a basis-independent map

```text
Trap_E : X_E -> Y_E
```

before another encryption wrapper is admitted. Public `Sample` and `Eval`
must run from a bare supersingular curve on the exact EndRing challenge
distribution. `Inv` must work from every complete evaluable basis of
`End(E)`, including arbitrary `GL_4(Z)` presentation changes. Complete-ring
necessity needs a non-factorization theorem or a reconstruction theorem from
the smallest sufficient witness. The reduction direction is fixed as

```text
selected-message attacker
    -> interface inverter or distinguisher
    -> complete evaluable End(E) basis.
```

An EndRing solver that can invert is an attack implication, not a security
proof. Two mutually blind producers proposed distinct interfaces; the packets
were snapshotted; a validator owned T1--T2, a red team owned T3--T4, and a
third reviewer owned T5. Composition selected one structured gap for a fresh
producer, whose packet received a second independent review. [Method] [Plan1]
[Plan2]

| Joint | Frozen question |
|---|---|
| T1 | Are public sampling/evaluation exact and simulable from bare `E`, including distribution and abort mass? |
| T2 | Is inversion typed, polynomial, and correct for every complete basis and basis change? |
| T3 | Is the complete ring necessary, or does inversion factor through a smaller witness without reconstruction? |
| T4 | Does an attacker yield a complete ring basis with explicit embedding, simulation, loss, runtime, and abort terms? |
| T5 | Are encodings, malformed inputs, repetition, controls, sources, prior art, claims, and documentation complete? |

# Initial proposals and evaluation

## UTTK: unoriented torsion-transport kernel interface

UTTK publicly samples a smooth cyclic kernel and a torsion basis, then emits
the quotient curve and transported torsion points. Its intended inverse would
compile any complete ring basis to one attack-suitable endomorphism `theta`
and run a torsion-recovery procedure. The producer correctly returned a typed
obstruction: the any-basis compiler is undefined, the recovery theorem is not
verified at this scope, and the route factors through the smaller witness
`theta`. Primary Séta text was not read; repository pointer scope suggests
substantial overlap, so novelty is unverified. [A]

The validator found T1 inconclusive because the exact random-point law,
rejection tails, and abort mass are unspecified, and T2 breaks because no
`GL_4(Z)`-invariant any-basis inverse exists. [V1] The red team found T3 and
T4 break: the only inverse architecture is `B -> theta -> kernel`, and a
bare-curve simulator that samples the kernel already knows what an inverter
returns. No selected-message embedding or inverter-to-ring extractor exists.
[R1] T5 breaks because adversarial transcript validity, codomain-isomorphism
encoding, and repeated-use semantics are incomplete. [T51]

## RWER-Trap: random-walk endpoint routing

RWER publicly samples an explicit small-degree isogeny walk and publishes a
canonical endpoint relation. A desired trapdoor router would use any complete
source ring basis to find a path to the endpoint. A different returned path
could be composed with the sampled path to form a source endomorphism. [B]

T1 is inconclusive because the exact edge law, automorphism normalization,
field/model encoding, and retry tails are incomplete. T2 breaks because no
basis-independent route algorithm is supplied. [V1] T3 remains inconclusive:
a target path is a smaller target-specific witness, but no polynomial reusable
smaller witness was proved sufficient. T4 breaks because guaranteed
edge/dual-edge collisions yield scalar loops, while a valid inverter may
return the original, canonical, or padded path; success gives no probability
of non-scalar rank growth or maximal-order saturation. [R1] T5 breaks on
endpoint/tag/certificate grammar and repeated-use view. [T51]

| Initial interface | T1 | T2 | T3 | T4 | T5 | Disposition |
|---|---|---|---|---|---|---|
| UTTK | inconclusive | breaks | breaks | breaks | breaks | typed obstruction |
| RWER-Trap | inconclusive | breaks | inconclusive | breaks | breaks | typed obstruction; one gap selected |

# Gap-fed proposal and fresh evaluation

The initial composition selected one gap only: strengthen or replace the
endpoint relation so that successful adversarial inversion quantitatively
forces useful non-scalar independent loops and full-order saturation, without
assuming a selector, endpoint ring, connecting ideal, orientation, or planted
alignment. [C1] [Gap]

The fresh producer proposed saturation-filtered RWER. For sampled walks `x`
and returned walks `x'`, the reduction forms

```text
alpha_i = dual(x'_i) o x_i in End(E).
```

It also wrote the minimal selected-message mask adapter `(y, m xor h(x))`.
The packet identifies two real barriers: decryption through arbitrary valid
inverses needs `h` to be fiber-constant, while predicting a fiber bit supplies
no decision-to-search compiler; ordinary endpoint validity also contains no
rank, discriminant, or maximal-order predicate. [C]

Fresh validation found the positive T1/T2 repair breaks. The sampler law,
abort/cost accounting, and repeated view remain prose, while the universal
any-basis `Inv` is explicitly missing. The artifact is coherent only as a
typed obstruction. [V2]

Fresh red-team review preserved the T4 missing-arrow obstruction but corrected
the producer's strongest T3 statement. The equation
`epsilon^q * u_I` is unjustified without an independence and repeated-call
model. Moreover, “no positive lower bound was derived” is not yet a proof that
the concrete infimum is zero: a canonical or padded selector must be shown to
preserve the exact fixed-length, degree-word, and endpoint rules. T3 is
therefore **inconclusive**, not a proved zero-bound theorem. [R2]

T5 breaks because the exact byte grammar, equality role of degree words and
tags, repeated-use adaptivity/state/randomness coupling, and composed abort
semantics are unspecified. [T52]

| Gap-fed interface | T1 | T2 | T3 | T4 | T5 | Disposition |
|---|---|---|---|---|---|---|
| Saturation-filtered RWER | breaks | breaks | inconclusive | holds only as scoped missing-arrow obstruction | breaks | typed obstruction with reviewer correction |

# Authorized correction controls

This batch carried the earlier J4/J5 correction semantics as regression
constraints rather than revoting the historical packet. The fresh T5 review
verified the additive Milne metadata mapping against the frozen independent
audit record: printed pages 69--70 map to PDF 74--75, printed 74 to PDF 79,
and printed 75/Lemma 6.12 to PDF 80 for source bytes SHA-256
`646c0c4f193cdaa35f32c7d60fbd46a75e2f5187db4301810e8613726e3ebbee`.
No fresh primary PDF read occurred, and historical J4/J5 verdicts are
unchanged. [Correction] [T51]

The normalized `x(X)`, `P=O`, lower-order-point, and digit-loop controls were
also preserved: weakened exact-order premises are controls rather than valid-
input attacks, and no digit-loop output is inferred without tie-handling
pseudocode. Neither new interface relies on an `x(X)`-only collision. [Method]

# Requirement-to-evidence table

| Requirement | Outcome | Evidence |
|---|---|---|
| Two distinct initial interfaces | complete | [A], [B] |
| Immutable initial snapshot | complete | [S1] |
| Independent initial T1--T5 review | complete | [V1], [R1], [T51] |
| One structured gap-fed proposal | complete | [Gap], [C] |
| Immutable gap-fed snapshot | complete | [S2] |
| Fresh revision T1--T5 review | complete | [V2], [R2], [T52] |
| Corrected locator/control carry-forward | complete at metadata/regression scope | [Correction], [T51], [T52] |
| Secure EndRing PKE or surviving interface | **not established** | [Final] |

# Exactly one next action

Before another PKE wrapper or RWER variant, define and audit a publicly
checkable binding relation whose honest output has a unique or publicly
equivalent preimage, while `Sample/Eval` use only bare `E` and `Inv` works from
every complete evaluable ring basis. The exact parser and repeated-use game
must precede the reduction. The binding predicate may not hide a canonical
selector, endpoint order, connecting ideal, orientation, or planted basis.
This successor is not launched automatically. [Final]

# Source index

- [Method] [Frozen methodology](methodology.md)
- [Plan1] [Initial review plan](../../../coordination/design/TASK-20261007-d54864/review-preparation/review-plan.yaml)
- [Plan2] [Revision review plan](../../../coordination/design/TASK-20261007-d54864/review-preparation/revision-review-plan.yaml)
- [A] [UTTK packet](../../../coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-6f5135/candidate.md)
- [B] [RWER-Trap packet](../../../coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-61dd3f/candidate.md)
- [S1] [Initial snapshot](../../../coordination/design/TASK-20261007-d54864/archives/TASK-20261007-4057bd/snapshot-receipt.json)
- [V1] [Initial T1--T2 validation](../../../coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-ab8d2f/validation-report.yaml)
- [R1] [Initial T3--T4 red team](../../../coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-df7b77/red-team-report.yaml)
- [T51] [Initial T5 review](../../../coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-70a40e/t5-report.yaml)
- [C1] [Initial composition](../../../coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-06c0cd/composition.yaml)
- [Gap] [Structured gap](../../../coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-06c0cd/gap-packet.yaml)
- [C] [Gap-fed packet](../../../coordination/design/TASK-20261007-d54864/tasks/TASK-20261007-3ba2ff/candidate.md)
- [S2] [Gap-fed snapshot](../../../coordination/design/TASK-20261007-d54864/archives/TASK-20261007-6cd2cb/snapshot-receipt.json)
- [V2] [Fresh T1--T2 validation](../../../coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-64221a/validation-report.yaml)
- [R2] [Fresh T3--T4 red team](../../../coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-e2c5d4/red-team-report.yaml)
- [T52] [Fresh T5 review](../../../coordination/design/TASK-20261007-d54864/reviews/TASK-20261007-b67a0f/t5-report.yaml)
- [Correction] [Additive locator correction](legacy-correction-addendum.md)
- [Final] [Final composition](../../../coordination/design/TASK-20261007-d54864/composition/TASK-20261007-80466d/final-composition.yaml)
