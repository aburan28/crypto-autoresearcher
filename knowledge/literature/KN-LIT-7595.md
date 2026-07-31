---
id: KN-LIT-7595
type: literature
title: "Mythos Preview's Chain of Thought in Discovering the AES Möbius Bridge"
authors:
  - "Claude Mythos Preview"
  - "Anthropic (abstract only)"
year: 2026
venue: 'Anthropic document, 28 July 2026 (model-authored transcript, rewritten by the model for clarity; only the abstract is human-written)'
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: https://anthropic.com/document/aes_mobius_bridge_cot.pdf
tags: [research-methodology, agentic-harness, inventor-protocol, tracked-object, negative-closure, control-experiment, pareto-domination, sota-honesty, deliverable-schema, prior-art-triage, cross-ratio, pgl2, aes, s-box, primary-methodology-source]
confidence: reported
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

## Contribution
A published, section-by-section transcript of one autonomous research session — the one in
which the projective/Möbius object that became the Möbius bridge ([[KN-LIT-7593]]) was
first identified. **This session did not produce an attack.** It produced two
measurements and a negative closure, and it is far more useful to this program as a
specification of a working research protocol than as cryptanalysis. It is the primary
source for the harness changes recorded in `KN-TECH-056` and `docs/inventor-protocol.md`.

## The harness, as revealed by the transcript
- **Three resource trees.** `/opt/aes/ref/` — one working reference implementation of a
  classic attack, "provided as a reference point for what a complete attack looks like."
  `/opt/aes/sota/` — the SOTA table, a file of confirmed structural lemmas, a findings
  digest, and the actual PDFs of the competing papers. `/opt/aes/board/` — the shared
  workspace left by the *previous generation* of agents: `findings.md`, a ~44 kB
  `critique.md`, and `notebooks/`, `reports/`, `threads/`.
- **A brief that forbids the known families.** The task is to invent attack family (F).
  Five families are declared **off-limits as the primary analytical lens**: (D) XOR
  differences, (L) GF(2)-linear correlations, (I) algebraic degree / structured sums,
  (M) large precomputed tables, (A) direct algebraic system solving. Roughly 200 variants
  drawn from (D)(L)(I)(M)(A) had already been tested by an automated "farm" and every one
  was dominated.
- **A generative frame.** The brief frames each historical family as **a change of
  tracked object** — differential tracks pairs, linear tracks parity bits, integral tracks
  whole sets, boomerang tracks adaptive two-directional oracle use, division property
  tracks algebraic degree. The session's organizing question is therefore *"what object
  haven't we tracked through rounds?"*, and nine candidate directions are supplied as
  seeds without committing to any.
- **An explicit honesty protocol on the deliverable.** `metadata.json` must name, in a
  `dominated_by` field, the SOTA row that dominates whatever the session produces; it may
  be set to `null` **only after checking against every row on the Pareto frontier**, and
  a quantitative `sota_delta` must state exactly how the numbers compare.
- **A validated-row bar.** The prior board's twelve rows are "validated" in the sense of
  passing **3/3 independent random-key checks**.
- **A depth instruction.** "Depth over breadth — stay with one object until you fully
  understand why it does or doesn't work," with the rationale that the *why* usually
  points at the next object.

## The working pattern (the part worth copying)
1. **Read the whole board before touching anything.** The session opens by reading the
   findings digest, the SOTA table, the confirmed lemmas, and all four prior inventor
   threads in full — "the worst possible outcome for this session would be to spend hours
   mining a lane that an earlier inventor has already explored and exhausted."
2. **Three fixed rejection axes, applied to every candidate object.** Is it *genuinely
   new*, or secretly a repackaging of a known object? Is it *concretely testable* — can
   its one-round propagation be defined and measured? *How many rounds* does it survive?
3. **Rejections are reasoned and recorded, not skipped.** Worked examples: commutators
   and conjugates are rejected because differential cryptanalysis is already the special
   case with `φ` drawn from the translation group; fixed points and cycle structure are
   rejected because iteration is unnatural under a fixed key schedule and because
   "fixed point" presupposes an identification of input and output space that is a choice
   of representation, so "any signal found this way could be an artifact of the
   coordinates rather than of AES itself"; matrix rank is rejected because ShiftRows is
   not of the form `M ↦ PMQ`; spectral/operator objects are rejected because the tractable
   projection is single-byte transition data, i.e. family (D)/(L) repackaged.
4. **One rejection produced a reusable criterion.** Tracking the joint object
   `(Δ, Π) = (x ⊕ y, x · y)` propagates deterministically through inversion and through
   field-affine maps — and is then discarded on noticing that in characteristic 2 the
   unordered pair `{x, y}` is recoverable as the roots of `t² + Δt + Π`, so the projection
   loses no information and is differential cryptanalysis "with extra bookkeeping."
   The stated lesson: **a useful object must be a genuinely lossy projection of the tuple
   of texts, and what it discards must be discarded in a way compatible with the cipher's
   operations, so the retained part still propagates deterministically.**
5. **A promising statistical signal is assumed to be an artifact until a control says
   otherwise.** Experiment E8 measured an apparent 3× excess on the cross-ratio diagonal
   at `r = 3, 4, 5` with χ² z-scores of 3.58–4.78. The signal was rejected on a structural
   tell before any control was run: *"the excess is essentially the same at r = 3, 4, and
   5. That is suspicious. Any genuine statistical structure in AES should decay as more
   rounds of mixing are applied... An excess that stays constant across rounds is instead
   the signature of an artifact."* Several candidate explanations were then worked through
   (non-uniform marginal collision probability; conditioning on non-degeneracy; the S₄/V₄
   equivariance of the cross-ratio), and the matter was settled by **running the identical
   measurement on a random function and a random bijection in place of AES**, which
   reproduced the numbers exactly. Recorded as a *controlled null*.
6. **Negative closures are first-class deliverables, enumerated so the next agent does
   not re-tread them.** Five were recorded, each with its mechanism: the χ-statistical bias
   at `r ≥ 3` is null against a random-bijection baseline; multiplicative-character bias
   is null at `r ≥ 3`; the GF(2^8) rank of the Δ-set matrix is always full at `r ≥ 4`
   (verified over 10^4 keys), the rank drop existing only at `r = 3`; tracking GF(2)-flats
   is mathematically equivalent to a second-order differential and buys nothing; the
   state-rotation commutator fails because ShiftRows commutes with none of the row/column
   symmetries.
7. **Honest accounting of what was found.** The brief asked for structure at 4+ rounds.
   The cross-ratio gave **2** deterministic rounds. The session records
   `rounds_structure: 2`, states plainly that this "does not reach the 4-round target set
   by the brief," notes that the 2-round structure "re-derives established geometry" (the
   known subspace-trail fact) through a new lens, and sets `dominated_by: "n/a (no attack
   claimed)"` and `sota_delta: "no attack; conceptual/measurement contribution only."`
   The 3-round rank-drop event (`P ≈ 4/256 ≈ 1.5%`) is explicitly **not** claimed as new
   because its mechanism reduces to a lemma already established by a prior thread.
8. **The closure argument is a real argument, not a fatigue report.** The session's
   thesis — *there is no sixth per-byte-algebraic lens* — is argued from group theory:
   the S-box factors as `SB = L ∘ Inv`; GF(2)-based invariants survive `L` but die at
   `Inv`, projective (PGL) invariants survive `Inv` but die at `L`; the group generated
   jointly, `⟨PGL(2,2^8), GL(8,2)⟩`, is transitive enough on byte tuples that only trivial
   invariants (byte equality, the full multiset — i.e. the already-known yoyo and integral
   families) survive both. **The closure then converts into forward guidance**: a sixth
   family, if it exists, must be multi-byte-coupled, information-theoretic, or adaptive.
9. **The positive contribution is framed candidly.** The two genuinely new items — the
   Inv/L duality and the Projective Approximation Table of `L` (conditional output entropy
   `H = 7.973` bits against a uniform maximum of `7.989`, `|λ₂| ≤ 0.018`, max bias
   `2^-8.8`) — are summarized as: "they don't attack AES — they explain AES." The one-line
   comparison offered is that `L` destroys projective structure roughly 64× harder than
   `Inv` destroys linear structure (`2^-8.8` vs the LAT maximum `2^-3`).
10. **Reproducibility is checked, not asserted.** Before closing, all five C testbeds are
    recompiled from scratch "to make sure that pointer is not a lie," every deliverable is
    listed with its byte size, and each experiment is stated to reproduce in at most five
    minutes on a single core. Three open directions are left for the next thread.
11. **Session close is recorded as a fact**: 35 turns, ~19 minutes wall-clock, "ended by
    natural completion — the research questions resolved and every deliverable committed —
    rather than by hitting a time or resource limit."

## Relevance to this program
**No ECDLP content whatsoever.** Its value is entirely methodological and it is the direct
source for `KN-TECH-056` and for the harness changes made on 2026-07-28.

The single most important observation for this program: **the session that produced the
Möbius object closed negative and under-delivered against its own brief, and was still
the origin of the published attack.** The object was carried forward by a later agent that
found the one place where projective invariance *did* pay — eliminating a key-byte guess
in a meet-in-the-middle table — a use the originating session never considered. This is a
concrete argument against the program's habit of scoring a batch by whether its hypothesis
survived: the deliverable that mattered was a well-characterized *object* plus an honest
map of where it fails, not a confirmed hypothesis.

Read against [[KN-LIT-7594]], the two documents cut in the same direction from opposite
ends. The blog records a model refusing to start because the target looked saturated; this
transcript shows what a saturation claim has to look like to be worth anything — a group-
theoretic argument with a named obstruction and a redirection, not "we tried 200 variants."
This program's own saturation reports (see the idea-generation series recorded in the
memory index, which has repeatedly reported "no classical survivor") should be held to the
standard in item 8, and demoted to `unverified` where they cannot meet it.

## Not verified here
Document retrieved from the official Anthropic URL above on 2026-07-28 and read in
substantial part — §§1.1–1.2, 2.1, 5.1, 7.1–7.4 in full, remaining sections at the level
of headings and the summaries in §7; `confidence: reported`. Quoted phrases are verbatim
from the transcript.

NOT verified here: any AES mathematical claim in the transcript, including the two-round
per-column cross-ratio equality (reported as 1000/1000 random keys), the rank profile
`r ∈ {0,1} → 2, r = 2 → 5, r = 3 → {17: 98.5%, 16: 1.5%}, r ≥ 4 → 17`, the PAT(L) figures
(`H = 7.973`, `|λ₂| ≤ 0.018`, bias `2^-8.8`), the E8 control result, and the
group-theoretic no-sixth-lens argument — none of which has been re-derived or re-run here,
and none of which appears to have been peer-reviewed anywhere.

**Provenance caveat, which matters more than usual.** By Anthropic's own statement this
document is *a rewrite by the model of its own transcript*, edited for clarity: "The
rewrite preserves one-for-one every action that Claude took throughout the process, but
summarizes the programs executed and outputs observed." Only the abstract is human-written.
It is therefore a **model-authored account of model reasoning**, not a raw log, and the
selection of one successful-lineage session out of many — the blog notes that "many
sessions resulted in no new discoveries" — makes it a survivorship-biased sample of the
harness's behaviour. The protocol described above should be adopted on its merits as a
protocol, which is how `KN-TECH-056` treats it; it should **not** be cited as evidence
that this protocol reliably produces results, because the base rate is not published.
