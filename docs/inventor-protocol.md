# The inventor protocol

Adopted 2026-07-28. Source: `KN-TECH-056`, abstracted from the published
Möbius-bridge discovery session (`KN-LIT-7595`) and the results and program
account around it (`KN-LIT-7592`, `KN-LIT-7593`, `KN-LIT-7594`).

This document governs **ideation and closure**. It sits alongside
`docs/target-result-profile.md`, which governs *what kind of result is worth
having*; this one governs *how the search for one is run and how it is allowed
to end*. Where they conflict, the target profile wins on direction and this
document wins on procedure. Neither relaxes `AGENTS.md`.

## Why this exists

Two failure modes, both observed, pointing in opposite directions.

The program's entire rule set is tuned against **overclaiming**. But
`KN-LIT-7594` records the opposite failure being the binding one in practice: a
model declining to attempt AES cryptanalysis because the target was
exhaustively studied — "this is the most-studied block cipher in existence" —
immediately before the same model, differently prompted, improved the
best-known attack. Premature closure is cheap to produce, reads as rigour, and
is almost never challenged, because a rejection needs no evidence under the
current contract.

Second, this program scores batches by whether a hypothesis survived. The
session that produced the Möbius object **closed negative and under-delivered
against its own brief**, and was still the origin of the published attack: a
later agent found a use for the object that the originating session never
considered. The durable deliverable was a well-characterized object plus an
honest map of where it fails.

## 1. Object-first generation

Frame an attack family as a choice of **tracked object** — the thing followed
through the computation. On the symmetric side the enumeration is legible:
differential tracks pairs, linear tracks parity bits, integral tracks whole
sets, boomerang tracks adaptive two-directional oracle interaction, division
property tracks algebraic degree.

**This program has no such enumeration for the ECDLP.** Writing one down is
`KN-OPEN-019`, and it is a prerequisite for using this section at full
strength. Until it exists, apply §§2–5 — which do not depend on it — and treat
any partial mapping of ECDLP families to objects as a sketch, not a taxonomy.

When generating against a well-mined target:

- **Name the established families and declare them off-limits** as the primary
  lens for the session. Without this, candidates regress to variants, and the
  regression is often invisible because the variant arrives in new notation.
- Score every candidate on three axes: is it **genuinely new** or a
  repackaging; is it **concretely testable** (can its one-step propagation be
  defined and measured); **how far does it survive** before the structure
  dissolves.

## 2. The lossy-projection test

**A tracked object must be a genuinely lossy projection of the underlying
state, and what it discards must be discarded compatibly with the target's
operations, so the retained part still propagates deterministically.**

A projection that loses nothing is a change of coordinates, not a new object.
The worked example from `KN-LIT-7595`: tracking `(Δ, Π) = (x ⊕ y, x·y)`
propagates cleanly through inversion and through field-affine maps — and is
worthless, because in characteristic 2 the unordered pair `{x, y}` is
recoverable as the roots of `t² + Δt + Π`. Nothing was discarded, so nothing
was gained.

This test is algebraic, costs no compute, and should be applied before any
experiment is proposed. It is the cheapest available answer to "is this
actually new."

## 3. Controls before belief

Any apparent signal is an artifact until a control says otherwise. Two moves,
in order:

1. **Look for a structural tell.** A quantity that should decay and does not is
   the canonical one. From the source session: an excess essentially identical
   at 3, 4 and 5 rounds — "an excess that stays constant across rounds is
   instead the signature of an artifact," because genuine structure should
   decay as more mixing is applied. Ask what the measured quantity *should* do
   as the parameter that is supposed to destroy it increases; if it does not do
   that, suspect the measurement.
2. **Run the identical measurement against a null object** — a random function,
   a random bijection, a random instance of the same shape. If the numbers
   match, record a **controlled null**, not a finding.

This extends `AGENTS.md` rule 3 from infrastructure failures to statistical
ones: a timeout is not negative mathematical evidence, and neither is an
uncontrolled correlation positive mathematical evidence.

## 4. The closure standard

A negative result is a first-class deliverable and must be recorded with its
**mechanism**, so the next agent does not re-tread it. But closures are held to
a standard, and most of what this program currently calls a closure does not
meet it.

**Not a closure:** "we screened N mechanisms and all were rejected." That is a
fatigue report. It is a statement about the search, not about the problem, and
its honest status is `unverified`.

**A closure:** a named obstruction, an argument, and a redirection. The model is
the source session's: *the S-box factors as `L ∘ Inv`; GF(2)-based invariants
survive `L` and die at `Inv`; projective invariants survive `Inv` and die at
`L`; the jointly generated group `⟨PGL(2,2⁸), GL(8,2)⟩` acts transitively
enough on byte tuples that only trivial invariants survive both; therefore
there is no sixth per-byte-algebraic lens* — followed by **forward guidance**
naming the classes that remain open (multi-byte-coupled, information-theoretic,
adaptive).

This applies with full force to this program's own saturation reports. The
2026-07-20 completeness sweep and the idea-generation series have repeatedly
concluded that the classical ECDLP space is saturated. Under this standard
those conclusions are `unverified` until someone writes the enumeration
(`KN-OPEN-019`) and the argument.

## 5. Honest accounting in the deliverable

Every ideation or closure session emits a structured record carrying:

- the **object** studied;
- the **depth of verified structure**, stated at the tier actually verified —
  deterministic and probabilistic results are not interchangeable, and
  structure that re-derives established results through a new lens is recorded
  as exactly that;
- **`dominated_by`** — the best-known result that dominates this one, in the
  Pareto sense across every cost axis (time, memory, data/queries). It may be
  set to null **only after checking against every row on the frontier**, and
  `null` without that check is a fabrication under `AGENTS.md` rule 5;
- **`sota_delta`** — quantitatively, how the numbers compare. "Faster" is not a
  value;
- the **enumerated closures**, each with its mechanism, at the §4 standard;
- **open directions** for the next session.

A session that finds nothing still emits all of these. `dominated_by: "n/a (no
result claimed)"` and `sota_delta: "no attack; conceptual/measurement
contribution only"` are valid, complete answers.

## 6. The validation ladder

When a claimed improvement cannot be executed at the scale where it would
matter — the normal case here — correctness is established by parts.
`KN-LIT-7593` §5 is the worked example; the ladder generalizes:

1. **Isolate each assumption the complexity analysis rests on and measure it
   separately** at a scale where measurement is possible, naming the specific
   failure mode being hunted. (There: a hidden algebraic relation among
   fingerprint coordinates, probed over `3×10⁹` samples and excluded to within
   `1.1σ`.)
2. **Run the entire pipeline on a scaled-down instance** of the same shape —
   chosen as the smallest one on which the baseline's parameter space is fully
   enumerable — and check that the predicted improvement appears as a
   **measured ratio against the baseline**, not as an extrapolation. Check the
   predicted *negative* cases too.
3. **Run the real object with cheats**, each named individually and each
   classified as completeness-preserving or soundness-losing, with the lost
   soundness explicitly delegated to a specific measurement from step 1.
4. **Verify the reproducibility pointer is not a lie** — rebuild every artifact
   from scratch and list it, rather than asserting availability.

Step 2 is the one this program most often skips, and it is the one that
converts a claimed speedup into an observed one.

## 7. What this does not license

- Nothing here relaxes `AGENTS.md`. Rule 4 scoping, rule 5 on fabrication, and
  the claim tiers in `docs/claims-and-verification.md` apply unchanged.
- The protocol is adopted **on its merits as a protocol**. Its source is a
  model-authored rewrite of one successful session selected from many that
  produced nothing (`KN-LIT-7595`, provenance caveat). There is no published
  base rate, and no one may cite this document as evidence that following it
  produces results.
- "Do not declare a direction impossible" (Idea Generator prohibition) is
  unchanged and is not in tension with §4. A closure names an obstruction
  within a stated scope and says what remains open; it does not declare a
  problem unsolvable.

## 8. Proof-architecture portfolio

Source: `KN-TECH-080`, abstracted from the ten-paper collection recorded in
`KN-LIT-7640` and `SRC-OAI-TEN-PROOFS-2026`. The collection reports major
mathematical results, but this intake did not independently verify them. What
is adopted here is a set of falsifiable search transforms, not the truth of the
source's theorem claims and not a claim that the transforms improve discovery
rates.

For any proof-oriented proposal, asymptotic claim, certificate family,
reduction, or closure argument, fill `proof_search_map` before compute. Four
cheap audits run by default:

1. **Baseline reproduction.** Name the exact bottleneck and the parameter
   slice that reproduces the best-known baseline. Verify the reproduction
   symbolically or with a frozen fixture. A curve on a plot that looks similar
   to the baseline is not an embedding.
2. **Observation collision.** Name the observable, invariant, quotient,
   transcript, functor, or certificate supporting the conclusion. Search for
   distinct ground-truth objects with the same observable, preferably one on
   each side of the claimed conclusion. A collision is a direct falsifier of
   identifiability unless an additional condition separates it.
3. **Quantifier order.** Rewrite the claim with explicit `forall` and `exists`
   order. Check whether a witness is allowed to depend on an instance, family
   member, characteristic, parameter, or seed in a way the claimed uniform
   conclusion forbids.
4. **Method ceiling and nearby-object control.** Bound what the proposed method
   could prove under ideal tuning, then apply it to the closest object where
   the hoped-for conclusion fails. A method that cannot distinguish the pair
   has not identified the load-bearing structure.

After those audits, select only constructive transforms whose prerequisites
are present:

- **baseline-as-boundary lift** - enlarge the certificate family and prove a
  strict inward improvement, not merely feasibility;
- **stronger compositional invariant** - preserve more state than the final
  goal requires because that stronger state is what survives recursion;
- **telescoping potential** - randomize the location of an unstable increment
  and charge it to a global martingale, entropy, energy, or filtration budget;
- **specialize-measure-pack** - build a problem-specific resource measure,
  realize it by a specialization, and add charges only over proved-disjoint
  blocks;
- **representation/reduction chain** - move to a model where the hypothesis is
  an exact equality, dimension, rank, or vanishing condition, with separate
  encoding, completeness, soundness, transfer, and cost-loss obligations;
- **observable-fiber counterexample** - hold the observable fixed, vary the
  forgotten structure, and find an intrinsic invariant distinguishing the
  resulting objects.

No proposal must use every transform. A non-applicable audit records why it is
non-applicable; it is not silently omitted. The full field schema lives in
`templates/research-records.md`, and the detailed technique with ECDLP limits
is `KN-TECH-080`.
