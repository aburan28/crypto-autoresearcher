---
id: KN-TECH-6785f2
type: technique
title: Adjudicating "is this differential path new" - census schema, verified equivalence generators, two-sided decoys, and the dependency-graph audit without which an ablation battery cannot be read
tags: [methodology, adjudication, novelty-claims, census, equivalence-relation, canonical-form, ablation-battery, functional-dependency, null-object-control, two-sided-control, known-false-instrument, differential-cryptanalysis, md5, sha1, instrument-calibration]
confidence: reported
complexity: not an algorithmic cost claim - a construction-and-control protocol for building an adjudicator and for measuring what its controls can and cannot detect
applicability: >-
  Any research program that must decide whether a candidate object is already
  present in a body of published work under a declared notion of sameness -
  differential paths and disturbance vectors here, but the machinery is
  primitive-agnostic and recurs for every object a program asks "is this new"
  about. The dependency-graph audit applies to any exact-key membership test
  whose key has more than one component.
source_refs: [KN-TECH-056, KN-TECH-080]
added: "2026-08-26"
superseded_by: null
---

## Epistemic status, and what this entry is not

This is GOAL-DIFFP-84d641's abstraction from three measured batches of its own
instrument work. It is adopted on the merits of those measurements.

**It asserts nothing about MD5 or SHA-1.** No differential path is claimed new
for either primitive at any tier. No cryptanalytic improvement of any kind is
claimed. A passing control is not an improvement, and an instrument whose
profile becomes readable is a better-understood instrument, not a result about
a primitive.

Every number below was measured on a **synthetic shadow population of 16
planted entries** against a **readable census of size zero**. The census
completeness is `readable 0 / quarantined_not_read 1 / acquisition_gap 8` —
three counts that are **never summed** — with `shadow_planted 16` carried
separately. **With a readable census of zero, a NON-MEMBER verdict carries no
information about the literature at all.** Every planted MD5 entry carries a
weight-1 message difference that no real MD5 collision characteristic has, and
adjudicator correctness against a published characteristic remains **untested**.

Provenance of this entry's identifier, carried because it differs from every
other identifier this campaign minted: `tools/allocate_id.py` has **no
`knowledge` type**, so `--next` could not emit it. The driving session drew a
state-free random 6-hex token with `secrets.token_hex(3)` — drawing no state,
which is exactly the reasoning `CLAUDE.md` gives for using `--next` in the first
place — and confirmed it well-formed and free with `--check` against the full
identifier union. That gap is a **harness finding**, named in
`DEC-20260825-1dc43c`: a convention that instructs an agent to mint an
identifier with a tool that will reject the request is a defect in the
convention or the tool. It is infrastructure signal and says nothing
mathematical.

## 1. The three things that must exist before "new" is falsifiable

A claim that an object is new is unfalsifiable until the program holds all
three, and each must have a control that can answer **no**.

1. **A machine-readable census with per-entry citation provenance.** Carry its
   completeness as separate counts that are never summed: readable, held but
   deliberately unread (another goal's firewall, a licence bar), and known
   sources not yet obtained. Carry a synthetic planted population **apart from
   all three** — it is scaffolding for the controls, never census content.
2. **A declared equivalence relation with a verified generating set.** Every
   generator is *individually* verified to map conforming objects to conforming
   objects, or is excluded and listed as unverified. **Record each generator's
   orbit action alongside its verification status**, because a generator can be
   verified and still emit no orbit image at all — this program has two such,
   and their existence made a recall criterion unsatisfiable as written.
3. **A verifier that adjudicates candidate-versus-census membership under that
   relation**, with a planted-positive control and a random-negative null
   control.

## 2. Two-sided known answers, and why a passing control proves little

A control with one known answer is passed by degenerate instruments. Build
**two-sided decoys**: objects whose correct verdict is MEMBER and objects whose
correct verdict is NON-MEMBER, constructed by the same machinery.

The measured cautionary datum: an adjudicator whose canonical key **cannot see
the message difference at all** — the primary datum of a differential
characteristic — scored planted-positive recall 96/96 and null false-positives
0/3000, *identical to the honest one to the digit*. **Those are true integers
that do not mean what a reader would take them to mean.**

Standing warning: in an exact-key adjudicator a reported "closest distance" is
a diagnostic, **never a margin and never a decision variable**.

## 3. The ablation battery, and the dependency-graph audit without which its output cannot be read

The natural next control is an ablation battery: delete one key component,
re-adjudicate, and report which deletions the suite detects. **That output is
uninterpretable on its own**, and this is the entry's central content.

A NOT DETECTED verdict can mean at least four different things, and a
single-column battery cannot tell a reader which:

- **provably undetectable by any family** — the deleted component is a function
  of a component the row retains, so the ablated key separates exactly what the
  unablated key separates;
- **not probed by a declared family** — no family in the declared set moves it;
- **probed and genuinely not detected**;
- and, for DETECTED rows, **entailed by the perturbing family's own
  declaration** versus **contingent on the instrument**.

So: **before reading an ablation battery, compute the membership key's
functional-dependency graph over every ordered pair of key components, per
primitive.** Then partition every verdict by that graph.

Three rules fall out, and each carries a measured limit that must travel with
it. **Stating any of them without its limit reproduces the deflation this
entry exists to correct.**

**Rule A.** *A control family that perturbs exactly the set S of key components
while holding every other key component fixed makes the row deleting S DETECTED
by construction, so a power measurement must live off the diagonal.*
**Limit, measured, and it is a false instance rather than a caveat:** the rule
reads a family's *name* where it must read the family's *behaviour*. A family
that honestly recomputes a component derived from the one it perturbs moves
**two** components, not one. Measured here: the message-difference family on
SHA-1 recomputes the in-code flag from the perturbed difference, so its
diagonal cell measures **NOT DETECTED** while the rule states DETECTED as a
theorem — and the same cell measures DETECTED on MD5, where the flag is not a
key component. Instantiate S from the family's **actual moved-component set per
primitive**; the theorem then correctly applies to the depth-2 row deleting the
pair.

**Rule B.** *A key component that is a function of another retained component
cannot be detected by any family, so an ablation lattice treating key components
as independent coordinates measures its own defect first.*
**Limit, measured:** the quantifier "by any family" ranges only over families
whose draws a well-formedness gate admits — and the gate may **assert the very
predicate the dependency states**. Measured here: the gate check for the in-code
flag is, character for character, the edge. Every admitted family satisfies the
edge *by admission*, so the theorem is about the serialisation format and the
gate rather than about the key. It is also worth knowing what such theorems
usually turn out to be: of two rows proved undetectable here, the grounds were
*a tuple carries its own length*, *a field is absent on one primitive*, and *a
recomputed predicate is a function of its own argument*.

**Rule C, this program's own addition.** *An exclusion rule computed under the
honest instrument cannot bound an instrument-dependent quantity.*
Cells excluded because "a component the row retains determines the deleted one"
are excluded on a property of the **honest** key. A known-false instrument whose
projection **drops that determiner** has no such antecedent, and the cell is not
excluded for it. Measured here: recomputing the forcing predicate *per
instrument* re-admitted the single cell in a 72-cell per-primitive matrix on
which the honest instrument and a known-false one differ — the cell the
instrument-independent rule had removed.

**Two further discipline rules the audit needs to be readable at all.**

- **Label an edge whose determined column is constant on the population
  separately.** A constancy detector returns EDGE for every X when Y is
  constant, and that is a true statement of the rule and *not a dependency*.
  Measured here: of 36 EDGE verdicts across two primitives, **exactly one** had
  a witness with a demonstrated capacity to fail. A sentence of the form "the
  graph contains N edges" was off by a factor of more than thirty in what it
  suggested. Require a **written derivation from committed source** as well as
  a witness, and reserve words like *theorem* and *provably* for edges that
  carry one.
- **Emit an unmeasured cell as `null`, never as integer `0`, in the artifact
  itself.** A family that a gate rejects on every draw is reported as **NOT
  CONSTRUCTIBLE with its derivation**, never as a family that produced zero
  detections. Half a matrix can be decided by constructibility before any
  adjudication runs, and a machine consumer reading the JSON alone must not be
  able to misread a coverage gap as a measured negative.

## 4. Null-object controls for the counting rule, and the capacity they do not buy

Any scalar summarising a power profile — a differing-cell count between an
honest instrument and a known-false one — must be run through **the identical
counting code** with degenerate instruments, so the scalar has a demonstrated
capacity to be large. The strongest available form of that guarantee is
structural: make the cell-verdict function **take no instrument argument at
all**, so it *cannot* special-case a degenerate instrument because it cannot
tell which one it is serving.

**What the control buys and what it does not, and the two are routinely
conflated.** An instrument returning MEMBER for everything flips every
NOT-DETECTED cell *by construction*. That demonstrates the **counting rule** can
emit a large number. It demonstrates **nothing** about whether any real
instrument could be told apart by *these* cells built from *these* families.

**A control that cannot fail is not a control.** Measured here: the
always-NON-MEMBER arm's predicted extreme was zero *only because* the honest
instrument reported DETECTED on none of the adjudicated cells, so the arm was
arithmetically pinned and could not fail. Its two-sided capacity was
demonstrated in one direction only. The named repair is cheap: admit cells whose
honest value is DETECTED into a **separate capacity-only arm**, kept out of the
count's denominator.

**And the decisive measurement, which is what makes this section worth
keeping.** The differing-cell count could **not** distinguish the honest
instrument from one that returns NON-MEMBER for every object — both gave 0 over
the same cells — while that instrument failed the planted-positive control
outright at 0 hits of 96 against 96 of 96. **The count is a diagnostic and never
a decision variable.** Report the per-cell table and the per-instrument verdict
vector; drop the aggregate as a headline. If an aggregate is wanted, the honest
one is the number of cells on which *any* declared instrument differs from *any*
other, which reveals immediately when a cell set has no variance.

Finally, a tail check worth applying to any such table: **a quantity exactly
flat in every parameter meant to modulate it is an artifact tell**
(`docs/inventor-protocol.md` §3) and must never be cited as robustness.

## 5. What a program should expect to find, stated as an expectation and not a law

Across three batches of this instrument, each control that was strengthened
measured that the *previous* reading had been about something other than what it
appeared to be about: a pass became a fraction; the fraction became largely a
property of the ablation lattice and the perturbing families; the family-by-row
profile became largely a property of key-format redundancy and family
constructibility; and the exclusion rule that decided what was adjudicable
turned out to be blind to the instrument under test.

The useful posture is to expect the same move again and to name it in advance,
so that if it happens no close can present it as a surprise, and if it does not
happen that is also informative.

## 6. Boundaries

Scoped to one adjudicator's strict serialisation under one verified generator
set, two primitives, eight frozen seeds, a 16-entry synthetic shadow census,
strict mode only, and six declared perturbing families of which three were
constructible. Permissive mode is unmeasured and its cells are `null`, never
`0`. Four known-false instruments used here were built once by one session and
re-executed from the same file, which is **re-execution and not independent
construction**. The per-instrument re-admission measurement of §3 Rule C is a
single-session result by one implementation and is **not replicated**.

No transfer to any other primitive, census, generator set, seed set or mode is
claimed, and no novelty status, cost or attack complexity is asserted anywhere.
The MD5 acquisition lane referenced by the source campaign is **blocked, not
closed**.

## Sources

Composed by the Coordinator at the BATCH-145531 close under
`DEC-20260824-257f35`, discharging a bounded obligation set by
`DEC-20260824-c5bb72`. Measurements are in `EV-DIFFP-b878aa`,
`EV-DIFFP-b16b01` and `EV-DIFFP-afd96c`, with the disposing decisions
`DEC-20260824-af6d5c`, `DEC-20260824-c5bb72` and `DEC-20260824-257f35`, the
corrections `CORR-20260824-c1c8b1` and `CORR-20260824-ad7f2c`, and six
independent review reports across three sibling-blind rounds.
