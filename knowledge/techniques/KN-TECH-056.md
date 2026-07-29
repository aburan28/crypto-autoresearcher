---
id: KN-TECH-056
type: technique
<<<<<<< HEAD
title: Supersingular isogeny-problem baselines, corrected against archived primary text (supersedes KN-TECH-029's classical F_p^2 figure)
tags: [isogeny-problem, path-finding, endomorphism-ring, meet-in-the-middle, claw-finding, cost-model, corpus-currency, supersession, isogeny, adjacent]
complexity: "F_p^2 unconditional: p^{1/2}*(log p)^{O(1)} time at polynomial memory. F_p^2 conditional on Heuristic 1 of the archived source: p^{1/3+o(1)} time AND memory, above a superpolynomial o(1) disclosed by the source. F_p: Otilde(p^{1/4}), carried at confidence relayed_from_abstract AND contested across retrievals, see RC4."
applicability: choosing the baseline a proposed supersingular-isogeny or endomorphism-ring attack must beat
source_refs: [KN-TECH-055, KN-LIT-078, KN-TECH-029]
supersedes: KN-TECH-029
confidence: reported
=======
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
>>>>>>> origin/main
added: 2026-07-28
superseded_by: null
---

<<<<<<< HEAD
## Why this entry exists

`KN-TECH-029` records the classical baseline for the supersingular isogeny
problem over `F_{p^2}` as *"expected Otilde(p^{1/2}) time and space"* in its
`complexity` field and in its "Complexity landscape" section. That figure is
**stale against this repository's own archived primary text**. It is not wrong
as a statement about meet-in-the-middle; it is wrong as a statement about the
best known complexity of the problem.

`KN-TECH-029` is **superseded, not edited.** It remains in the corpus exactly as
written, per the immutability rule of `AGENTS.md`. This entry is the current one.

This is a **corpus-currency supersession sourced to archived primary text**. It
is not a `KN-FIND` promotion of an internal finding, and it asserts no result of
this program's own.

**No back-pointer exists on `KN-TECH-029`, and none may be added.** The
independent review `RT-20260728-013` counted the corpus convention rather than
assuming it: `knowledge/` carries 7655 `superseded_by: null` fields and **zero**
non-null ones, so this corpus has never filled a back-pointer, and filling
`029`'s would be an edit to an immutable record. The consequence is that a
reader landing on `KN-TECH-029` directly will not learn that it is superseded.
The regenerated `knowledge/INDEX.md` is the only place the `supersedes` edge is
rendered, and it must render it in both directions.

## The archived primary text

All quotations below are from
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, a frozen verbatim source record
in this repository, and were read directly with the line locators shown. All
thirteen locators were independently re-extracted and matched verbatim by
`RT-20260728-013` (gate R2-1, a full check rather than a sample).

**Line 1 (title):**

> THE SUPERSINGULAR ISOGENY PROBLEM IN TIME AND MEMORY p^{1/3+o(1)}

**Line 11 (abstract):**

> We prove that under a plausible heuristic assumption (on the smoothness of
> certain random integers), the supersingular isogeny problem can be solved in
> time and memory p^{1/3+o(1)}. This improves upon the previous best complexity
> of p^{1/2} · (log p)^{O(1)}.

**Line 19 (Theorem 1.1):**

> Assuming Heuristic 1, there is a Las Vegas algorithm which, given a
> supersingular elliptic curve E/F_{p^2}, finds a non-scalar endomorphism
> α ∈ End(E) \ Z in expected time and memory p^{1/3+o(1)}.

**Line 23 (Corollary 1.2):**

> Assuming Heuristic 1, there is a Las Vegas algorithm of expected complexity
> p^{1/3+o(1)} for the supersingular endomorphism ring problem ... and for the
> supersingular isogeny problem ...

**Line 25 (what the previous baseline was):**

> The previous best algorithms to solve them had complexity p^{1/2} · (log p)^{O(1)},
> starting with [21]. This complexity had stayed remarkably stable, with
> subsequent improvements only impacting the logarithmic cofactor [15, 24, 26, 40].

## The corrected baseline

**Two tiers, and they must not be collapsed into one.**

1. **Unconditional tier — `p^{1/2} · (log p)^{O(1)}` time at polynomial memory.**
   Unchanged. The source itself places *"the classic p^{1/2+o(1)} algorithms with
   polynomial memory like [21]"* at this point (line 39). A proposed attack that
   reaches `p^{1/2+o(1)}` matches a baseline established in 1997 and improves
   nothing.

2. **Heuristic-conditional tier — `p^{1/3+o(1)}` time AND memory, conditional on
   Heuristic 1 of the archived source.** This is the current best known
   complexity of the supersingular isogeny problem, the supersingular
   endomorphism ring problem, and the `OneEnd` problem (Theorem 1.1 plus
   Corollary 1.2 via the cited reductions `[35, Theorem 1]` and
   `[35, Proposition 8.5]`). **It is conditional and must never be quoted
   unconditionally.** The two cited reductions have **never been verified by any
   session in this program** — `[35]` is not in this repository — so the
   corollary is carried exactly as the source states it and the cascade to
   `EndRing` and `Isogeny` is **inherited, not checked** (`RT-20260728-013`
   RSC1).

**Three qualifications the source discloses about its own result, carried inline
because dropping any of them misrepresents it. All from line 39 and line 13.**

- *"the overhead hiding in the o(1) term is superpolynomial, much larger than the
  previous (log p)^{O(1)} cofactor"* (line 39). **No concrete-parameter
  conclusion follows from the exponent alone**, and no figure computed above
  that `o(1)` is a threshold anyone can evaluate at a realisable `p`.
- *"its memory cost is essentially as high as the complexity p^{1/3+o(1)}, a
  serious obstacle for any deployment of the algorithm on instances of
  cryptographic size"* (line 39). Memory is **not** polynomial in this tier.
- *"The impact on concrete parameter sets remains to be clarified"* (line 13).
  The source does not claim a break.

**The time–memory interpolation, quoted rather than paraphrased (line 39):**

> The time-memory tradeoff of van Oorschot–Wiener [43] solves a claw-finding
> problem of this size in time essentially √(N^3/w) = p^{1/2+o(1)}/w^{1/2} with
> memory w. This allows one to interpolate between the p^{1/3+o(1)} high-memory
> algorithm presented here and the classic p^{1/2+o(1)} algorithms with
> polynomial memory like [21].

So the two tiers are endpoints of one curve, not rival algorithms. A candidate
claiming an advantage must say **where on that curve** it sits.

**Parallelism (line 39, line 41):** *"The algorithm parallelizes perfectly"*, and
the van Oorschot–Wiener variant gives *"an attack in time p^{1/2+o(1)}/(w^{1/2} n)
with memory w and n parallel processors."*

## What is NOT corrected here

- **The `F_p` figures.** `KN-TECH-029`'s Delfs–Galbraith line — descend to the
  `F_p`-rational subgraph for `Otilde(p^{1/4})` — is **not superseded by this
  entry**, because the archived source does not address it. It remains at
  `KN-LIT-078`'s own stated confidence, `reported` / relayed from the abstract,
  and it is additionally **contested across retrievals**: `GOAL-SSI-001`
  `TASK-20260728-011` observed that two retrievals under the identifiers
  `KN-LIT-078` lists returned **two different abstracts, one of which contains
  no `p^{1/4}` figure at all**. That is a stronger sourcing defect than
  "relayed", and it is why the front-matter `complexity` field above carries the
  marker beside the label. The direction of the discrepancy is unknown, the
  likeliest explanation (an arXiv-versus-DCC version difference) is itself
  unverified, and **absence of a stable source is not evidence the figure is
  wrong**: no `F_p` ranking is downgraded here.
- **The descent structure.** The same task obtained the descent as one long
  random walk from each of `E_0`, `E_1` *"until we hit a supersingular curve
  defined over F_p"*, **from ar5iv's rendering of arXiv:1310.7789**. It is
  **unverified for the published DCC version**, and those are exactly the two
  objects the two-abstracts observation showed apart (`RT-20260728-013` O10).
  The quantitative memory profile of the inner `F_p` search was **not**
  obtained. **Do not upgrade the `F_p` confidence label without the paper in
  hand.**
- **The quantum figures.** `KN-TECH-029`'s quantum `Otilde(p^{1/4})` line and its
  CSIDH-side subexponential line are untouched here.
- **The scheme scope.** Per line 31 the source names the affected set — CGL,
  the SQIsign family, GPS signatures, PRISM, ⊗-MIKE — and per lines 33–37 names
  as out of range *"all group-action-based constructions like CSIDH ... as well
  as torsion-based key exchanges like M(D)-SIDH, FESTA and POKE"*, on the stated
  ground that *"other cryptanalytic algorithms dominate the security analysis of
  these schemes"*. That scope is the source's, not this program's, and must not
  be widened when this entry is cited.

## How to use this entry

When benchmarking a proposed mechanism against the supersingular isogeny or
endomorphism ring problem:

- Benchmark **time exponents**: `p^{1/2+o(1)}` unconditional, `p^{1/3+o(1)}`
  conditional on Heuristic 1, over `F_{p^2}`.
- State which tier you are beating, and if you beat only the unconditional tier
  say so, since the conditional tier already sits below it.
- Do **not** benchmark against a full-cost figure computed above the disclosed
  superpolynomial `o(1)`; it is a threshold nobody can evaluate at any realisable
  `p`.
- Charge memory beside time. The conditional tier's memory is `p^{1/3+o(1)}`,
  not polynomial.

## Applicability limits

- The `p^{1/3+o(1)}` tier is **conditional on Heuristic 1** of the archived
  source. This program has neither validated nor challenged that heuristic, and
  holds no evidence bearing on it.
- Every figure here is asymptotic. Nothing in this entry establishes concrete bit
  security for any parameter set, and the source explicitly declines to
  (line 13, line 43: the concrete estimates of Section 4.1 *"make optimistic
  assumptions on the actual cost of certain steps, hence should not be
  interpreted as accurate predictions"*).
- This entry is a **corpus-currency correction**. It reports what an archived
  primary source says. It contains no result of this program's own, no empirical
  claim at any scale, and no cryptanalytic result.
- Provenance of the correction: `GOAL-SSI-001` correction C-β, raised in
  `TASK-20260728-005`, carried through `TASK-20260728-007` and
  `TASK-20260728-009`, and drafted with independently verified line locators in
  `TASK-20260728-011`. Zero curve computation was performed in any of them.

## Promotion provenance and the deltas from the drafted text

Promoted into the corpus by the `GOAL-SSI-001` `BATCH-003` ledger archive
`TASK-20260728-014`, under evidence `EV-SSI-003` (strength `preliminary`) and
decision `DEC-20260728-005` (`revise`), on the `ADMIT` verdict of gate R2 of the
independent review `RT-20260728-013`. The drafted source text is
`coordination/goals/GOAL-SSI-001/batches/BATCH-003/tasks/TASK-20260728-011/KN-TECH-056-draft.md`,
committed immutably in the producer snapshot.

Three deltas were applied to that draft by the archiving Coordinator, each
recorded here rather than left silent, and none of them changes an exponent, a
tier, or a scope:

1. Admit condition **AC2**: the marker `contested across retrievals, see RC4`
   was appended to the front-matter `complexity` field's `F_p` clause, and the
   two-abstracts observation was raised from the body's narrative into the
   "What is NOT corrected here" section. The reviewer's ground: the
   front-matter field is the field downstream readers grep, and *relayed* and
   *contested* are different defects.
2. Objection **O10** / control **RC14**: the descent finding is relabelled as
   ar5iv's rendering of arXiv:1310.7789 and marked unverified for the published
   DCC version.
3. Admit condition **AC1**: the missing back-pointer on `KN-TECH-029`, the
   corpus convention that produces it, and the instruction that
   `knowledge/INDEX.md` carry the `supersedes` edge in both directions are
   recorded in "Why this entry exists".

**Evidence-strength caveat carried into the corpus.** `EV-SSI-003` is capped at
`preliminary` because model independence was unavailable: producer, discharge
and reviewer sessions all resolved to one self-reported model identity, the
fifth consecutive `GOAL-SSI-001` session to do so. That cap bars an internal
finding from promotion; it does not bar this entry, which reports an archived
primary text rather than a result of this program's own.
=======
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
>>>>>>> origin/main
