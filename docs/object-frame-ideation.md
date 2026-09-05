# Object-frame ideation for the ECDLP

A reusable handoff block for asking the Idea Generator to devise **new
arithmetic** — new tracked objects, representations, or relation mechanisms —
for the prime-field ECDLP, including new index-calculus approaches. It exists
because `docs/inventor-protocol.md` §1 (object-first generation) says it cannot
run at full strength for the ECDLP until the tracked-object enumeration
(`KN-OPEN-019`) is written, and because the program has since proved enough
about that enumeration to make an unframed request regress to a known family
in new notation. Adopted 2026-09-05 with search bias 6 of
`agents/idea-generator.md`.

Nothing here relaxes `AGENTS.md`. The block steers *where* the generator
searches; every proposal it returns is still a `proposed`, unapproved,
novelty-`unverified` record until the ordinary lifecycle says otherwise.

## 1. The frame, in the program's own results

Read these before writing the handoff; cite them in it so the generator
searches the complement of what is closed instead of rediscovering it.

| record | what it fixes |
| --- | --- |
| `IDEA-20260806-c5d183` | On a prime-order group, a projection that propagates deterministically under the **full translation action** is constant or injective (five-line orbit argument). Every lossy tracked object therefore falls in exactly one of three classes: **partial-action** (propagates under a proper sub-action only), **branching** (propagates probabilistically), **coordinate-dependent** (a function of the representation, not of the group element). |
| `IDEA-20260807-df906f`, `IDEA-20260815-f558e4` | The same rigidity as a congruence statement, and the Cauchy–Davenport ceiling: the strict propagation rate of every balanced lossy partition of a prime-order subgroup is zero. |
| `KN-FIND-ffe1df` Theorem C | Validator-confirmed: an exactly sum-compatible bucket index is a surjective homomorphism onto a group of order dividing `N`, impossible for prime `N` and `1 < M < N`. This is the homomorphism form of the barrier, at the tier actually verified. |
| `IDEA-20260901-863e36` | Propagation is a property of a projection **paired with an operation set** Σ. The lossy objects on a prime-order subgroup that propagate under Σ are exactly the block systems of ⟨Σ⟩ acting on the subgroup. Translation is one slice of this; multiplication by a subgroup Γ ≤ (Z/n)^* is another and yields the negation and GLV quotients. The quotient-search family reduces to one measurable number, the cost of canonicalising a Γ-orbit. |
| `IDEA-20260802-002`, `H-TLD-f4c8ba` | The families F1–F7 named as off-limits (below), and an executable meter — loss `L(π)` and branching `b(π)` — that makes the lossy-projection test a measurement. `H-TLD-f4c8ba` is the specified hypothesis for a generator over a frozen grammar of lenses typed by the trichotomy. |
| `KN-OPEN-020` | Every bounded-degree algebraic factor base over a generic prime-field subgroup is scoped out with charged costs. The universal statement is open; the open class is high-degree, implicit, or target-dependent descriptions. |
| `RQ-ECDLP-623a32`, `KN-OPEN-003` | The representation question: which of R1 (field representations of coordinates), R2 (curve models and embeddings), R3 (non-function representations: elliptic nets, torsor and modular-curve coordinates, cubical and biextension lifts, `E×E` and Kummer-surface gluings, Weil restriction, local rings) change the charged cost of a named attack stage. The degree-`d`-function-on-`E` and Kummer-line paradigm is closed at model lever 1. |
| `KN-OPEN-019` | The enumeration question itself. Still open: no finding resolves it. |

The consequence that shapes every handoff: **a new arithmetic for the ECDLP is
never a new projection of the group alone.** It is a pair — a representation
of the point and an operation set the object must survive — or it is a
branching object whose loss and branching are measured, not asserted.

## 2. Off-limits as the primary lens

From `IDEA-20260802-002`, restated so a handoff can paste it. Declaring a
family off-limits forbids it as the *lens*; a candidate may still use one as a
component if it says so.

- **F1 walk-collision** (rho, kangaroo, van Oorschot–Wiener, BSGS): tracks a group element carried with its known representation `aP + bQ`.
- **F2 factor-base decomposition** (Semaev summation polynomials, Gaudry, Diem, descent): tracks a relation vector over a factor base.
- **F3 isogeny path**: tracks a vertex or walk in an isogeny graph.
- **F4 pairing transfer** (MOV, Frey–Rück): tracks the image in `F_{q^k}^*`.
- **F5 p-adic lift** (Smart, SSSA): tracks a lift into a formal group.
- **F6 endomorphism or automorphism orbit**: tracks an orbit representative.
- **F7 preprocessing table**: tracks a precomputed advice string.

Add to this list, per handoff, whatever the target lane has itself closed
(for a factor-base question: the bounded-degree algebraic factor base of
`KN-OPEN-020`; for a representation question: the Kummer-line paradigm).

## 3. The constraint block

Paste into the `constraints:` list of the `handoff` record (schema in
`templates/research-records.md`), editing the bracketed parts. The
`inputs:` list must carry every record cited in §1 that the handoff relies
on, plus the target `RQ-*`.

```yaml
constraints:
  - >-
    OBJECT FRAME. Every candidate is a PAIR (representation of the point,
    operation set Sigma the tracked object must survive). Name both
    explicitly in `mechanism`. Sigma must not be the full translation action,
    which is closed for lossy objects by IDEA-20260806-c5d183 and
    KN-FIND-ffe1df Theorem C; if Sigma contains translation, the candidate is
    a branching object and must say so.
  - >-
    TRICHOTOMY. Place each candidate in exactly one class of
    IDEA-20260806-c5d183 -- partial-action, branching, or
    coordinate-dependent -- and give the one-line reason in `mechanism`.
    A candidate that cannot be placed is returned as `unverified` with the
    obstruction named, not silently dropped.
  - >-
    LOSSY-PROJECTION TEST, AGAINST THE NAMED OPERATION SET. Per
    docs/inventor-protocol.md section 2 and IDEA-20260901-863e36: state what
    the projection discards, show the discard is compatible with Sigma (a
    block system of <Sigma>, or a stated branching bound), and show it is
    lossy in the representation actually used. A projection that loses
    nothing is a change of coordinates and is not returned.
  - >-
    PRICE THE ONE OPEN NUMBER. For a quotient object, the cost of
    canonicalising a <Sigma>-orbit, charged end to end. For a branching
    object, the loss L and branching b of IDEA-20260802-002, with the
    minimal test stating how they are measured on a toy curve against the
    identity, random-label, and generic-group (relabelled Z/nZ) controls.
  - >-
    OFF-LIMITS AS PRIMARY LENS: families F1-F7 of IDEA-20260802-002
    [plus the lane-specific closures: ...]. A candidate that uses one as a
    component names it and states what is added.
  - >-
    FACTOR-BASE ESCAPE. Any candidate factor base or relation mechanism must
    say which of the KN-OPEN-020 open classes it belongs to -- high-degree,
    implicit-membership, or target-dependent description -- and charge
    description, membership, relation, descent, time and memory costs, or
    declare itself inside the scoped-out class and stop.
  - >-
    REPRESENTATION CLASS. Name the R1/R2/R3 class of RQ-ECDLP-623a32 the
    representation belongs to, and the attack stage (factor-base membership,
    relation decomposition, collision structure, linear algebra) whose
    charged cost it claims to change. Kummer-line and degree-d-function-on-E
    representations are closed at model lever 1 and are not returned.
  - >-
    PROOF SEARCH MAP before any compute (docs/inventor-protocol.md section 8):
    exact bottleneck, baseline embedding, observation collision, quantifier
    order, method ceiling with a nearby-object control.
  - >-
    HONEST ACCOUNTING. Novelty `unverified` unless checked against knowledge/
    and ledger/hypotheses/; `dominated_by` and `sota_delta` per section 5;
    `target_complexity` with exponents; `heuristic_assumptions` each with a
    validation route. A session that returns no candidate still returns the
    section 5 block, and a closure meets the section 4 standard or is
    recorded as `unverified`.
  - >-
    NO COMPUTE, NO STATUS CHANGE. Proposals only; no experiment, hypothesis,
    or approval; do not edit any existing record.
```

## 4. Where the declarations go in the idea record

The idea schema is fixed (`agents/idea-generator.md`, "Required output");
copy it, do not add fields. The object-frame declarations map onto it as:

| declaration | field |
| --- | --- |
| representation, operation set Σ, trichotomy class and reason | `mechanism` (first paragraph) |
| what is discarded and why the discard is Σ-compatible | `mechanism`, and `proof_search_map.observation_collision.observable` |
| the object as a constructive transform | `proof_search_map.constructive_transforms[].proposed_object` (transform `representation_reduction` or `observable_fiber`) |
| the priced open number and how it is measured | `predictions[]` (metric named), `minimal_test` |
| the off-limits component used, if any | `assumptions` |
| the KN-OPEN-020 class of a factor base | `interpretation_limits` |
| R1/R2/R3 class and attack stage | `claim` (one clause) |

## 5. How to use it

- `/propose-ideas RQ-ECDLP-623a32` (or any mined ECDLP question): step 3 of
  the skill pastes §3 into the handoff's `constraints:` and §1's records into
  `inputs:`.
- `/deep-research` with an ECDLP scope: step 3 hands the generator this file
  instead of restating the off-limits list.
- A campaign coordinator opening a batch on a factor-base or representation
  lane copies §3 into the lane's `TASK-*` handoff and prunes the bracketed
  parts to the lane.
- The enumeration that §1 of the inventor protocol is waiting on is a
  separate deliverable (`TASK-20260905-f8563d`); when it lands as a `KN-TECH`
  entry, cite it in `inputs:` ahead of the individual records above.

## 6. What this does not do

It does not make a proposal approved, does not change any status, does not
assert that outcome 2 or 3 of `KN-OPEN-019` is reachable, and does not
license a claim above the tier its evidence supports. It is a steering
document: it decides what the generator is asked, not what is true.
