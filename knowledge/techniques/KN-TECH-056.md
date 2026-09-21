---
id: KN-TECH-056
type: technique
title: Object-first invention protocol — tracked-object search with forbidden families, controlled nulls, mandatory closures, and Pareto-domination honesty
tags: [methodology, research-protocol, agentic-harness, tracked-object, negative-closure, control-experiment, pareto-domination, sota-honesty, deliverable-schema, prior-art-triage, saturation-discipline, inventor]
confidence: reported
complexity: not a computational technique — a session protocol; cost is measured in agent-turns and validation time, with an observed ~1:4 discovery-to-validation time ratio for results that cannot be run end-to-end
applicability: >-
  Research sessions whose goal is a genuinely new mechanism against a well-studied
  target, where (a) prior work is extensive enough that keyword novelty is
  worthless, (b) the candidate space is large and unstructured, and (c) the
  headline result cannot be executed at the scale where it would matter, so
  correctness must be established by parts.
source_refs: [KN-LIT-7595, KN-LIT-7593, KN-LIT-7594, KN-LIT-7592, KN-TECH-035, KN-TECH-055]
added: 2026-07-28
superseded_by: null
---

## The pattern

Abstracted from the published Möbius-bridge discovery session ([[KN-LIT-7595]]) and the
two papers and program account it belongs to ([[KN-LIT-7593]], [[KN-LIT-7592]],
[[KN-LIT-7594]]). Eight components. They are separable — a session can adopt any subset —
but components 4, 6 and 7 are the ones this program most conspicuously lacks.

### 1. Frame the family as a choice of tracked object
Historical attack families are each characterized by *what object is followed through the
computation*: differential tracks pairs, linear tracks parity bits, integral tracks whole
sets, boomerang tracks adaptive two-directional oracle interaction, division property
tracks algebraic degree. A search for a new family is then a disciplined enumeration over
candidate objects, not a search over "ideas."

### 2. Forbid the known families explicitly
Name the established families and declare them off-limits **as the primary analytical
lens**. Without this, candidate generation reliably regresses to variants — and the
regression is often invisible, because the variant arrives dressed in new notation.

### 3. Score every candidate on three fixed axes
- **Genuinely new, or a repackaging?** — the axis that does the real work.
- **Concretely testable?** — can the object's one-step propagation be defined and
  measured?
- **How far does it survive?** — how many rounds/steps before the structure dissolves.

### 4. Require lossy-but-compatible projection
A tracked object must be a **genuinely lossy projection** of the underlying state, and
what it discards must be discarded compatibly with the target's operations, so the
retained part still propagates deterministically. A projection that loses nothing is a
change of coordinates, not a new object — the transcript's worked example is
`(Δ, Π) = (x ⊕ y, x·y)`, discarded on noticing that in characteristic 2 the pair `{x, y}`
is recoverable as the roots of `t² + Δt + Π`. **This is the cheapest available test for
"is this actually new," and it is purely algebraic — no experiment required.**

### 5. Read the whole board before generating anything
Prior findings, the SOTA table, confirmed lemmas, and every prior thread — in full, before
committing to a direction. The stated rationale is avoiding re-mining an exhausted lane;
the observed side-effect is that the prior work's *closures* become the generator's map.

### 6. Treat any signal as an artifact until a control says otherwise
Two moves, in order. First, **look for a structural tell** — in the source case, an excess
that was identical at 3, 4 and 5 rounds, when a genuine property should decay with mixing:
"an excess that stays constant across rounds is instead the signature of an artifact."
Second, **run the identical measurement against a null object** (a random function and a
random bijection replacing the cipher). Matching numbers ⇒ record a **controlled null**,
not a finding. This is `AGENTS.md` rule 3 generalized from infrastructure failures to
statistical ones.

### 7. Make negative closures a first-class deliverable
Enumerate every dead end **with its mechanism**, so the next agent does not re-tread it —
and hold closures to a real standard. A closure that says "we tried 200 variants" is a
fatigue report. A closure worth recording looks like the source session's: *the S-box
factors as `L ∘ Inv`; GF(2)-based invariants survive `L` and die at `Inv`; projective
invariants survive `Inv` and die at `L`; the jointly generated group `⟨PGL(2,2^8),
GL(8,2)⟩` is transitive enough on tuples that only trivial invariants survive both;
therefore no sixth per-byte-algebraic lens exists* — a named obstruction, an argument, and
then **forward guidance** naming the classes that remain (multi-byte-coupled,
information-theoretic, adaptive).

### 8. Honest accounting in a machine-readable deliverable
Every session emits a structured record carrying, at minimum: the object studied; the
depth of verified structure, stated at the tier actually verified (deterministic vs
probabilistic); a **`dominated_by`** field naming the state-of-the-art row that dominates
the result, settable to null **only after checking against every row on the Pareto
frontier**; a quantitative **`sota_delta`**; the enumerated closures; and open directions
for the next session. Structure that "re-derives established geometry through a new lens"
is recorded as exactly that, not as a finding.

## Validation ladder, for results that cannot be run

Component 8 forces the question of how a claim gets believed when it costs `2^89` to
execute. [[KN-LIT-7593]] §5 is the worked answer, and it generalizes:

1. **Isolate each assumption the complexity analysis rests on and measure it separately**
   at a scale where measurement is possible — naming the specific failure mode hunted
   (there: a hidden algebraic relation among fingerprint coordinates, probed at
   `N = 3×10^9` samples).
2. **Run the entire pipeline on a scaled-down instance** of the same shape, chosen as the
   smallest one on which the baseline's parameter space is fully enumerable — and check
   that the predicted speedup appears as a **measured ratio against the baseline**, not as
   an extrapolation. Check the predicted *negative* cases too.
3. **Run the real object with cheats**, each named individually and each classified as
   completeness-preserving or soundness-losing, with the lost soundness explicitly
   delegated to a step from (1).
4. **Verify the reproducibility pointer is not a lie** — rebuild every artifact from
   scratch and list it, rather than asserting availability.

## Why this is recorded here

Two of this program's standing weaknesses are addressed directly.

**Saturation reports.** This program has repeatedly produced "the space has been mined,
no survivor" conclusions. [[KN-LIT-7594]] records a model refusing to attempt AES
cryptanalysis on exactly that reasoning — "this is the most-studied block cipher in
existence" — immediately before the same model, differently prompted, found a result.
Component 7 is the standard a saturation claim must meet to be worth recording; below it,
the honest status is `unverified`.

**Scoring sessions by hypothesis survival.** The session that produced the Möbius object
**closed negative and under-delivered against its own brief**, and was nonetheless the
origin of the published attack — the object was carried forward by a later agent to a use
the originating session never considered. The durable deliverable was a well-characterized
object plus an honest map of where it fails.

## Limits and cautions

- **Provenance.** [[KN-LIT-7595]] is a model-authored rewrite of a model's own transcript,
  and one successful lineage selected from many sessions that produced nothing. The
  protocol is adopted **on its merits as a protocol**; there is no published base rate, and
  this entry must not be cited as evidence that following it produces results.
- **Not a computational technique.** Nothing here changes any complexity. It is a session
  contract.
- **No ECDLP transfer of content.** The source material is symmetric-key cryptanalysis and
  lattice cryptanalysis. What transfers is the protocol; every mathematical claim in the
  sources stays in its own domain. See [[KN-OPEN-019]] for the open question of whether
  component 1 has an ECDLP analogue at all — it is a question, not an assumption.
