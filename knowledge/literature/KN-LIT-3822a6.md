---
id: KN-LIT-3822a6
type: literature
title: "The Optimal Choice of Hypothesis Is the Weakest, Not the Shortest"
authors:
  - "Michael Timothy Bennett"
year: 2023
venue: "AGI 2023 (Artificial General Intelligence, LNCS 13921, Springer)"
identifiers:
  eprint: null
  doi: "10.1007/978-3-031-33469-6_5"
  arxiv: "2301.12987v4"
  url: "https://arxiv.org/abs/2301.12987v4"
tags: [methodology, hypothesis-selection, induction, generalisation, occams-razor, mdl, description-length, weakness, bennetts-razor, enactive-cognition, agi, research-protocol, non-cryptographic]
confidence: reported
citation_verified: full_text
added: "2026-08-05"
superseded_by: null
---

## Contribution

A candidate replacement for Occam's Razor in hypothesis selection. Given observations
that admit many consistent hypotheses, the standard advice is to take the shortest
(minimum description length, MDL). Bennett argues the criterion to maximise is instead
**weakness** — the size of the set of situations a hypothesis is compatible with — and
proves, inside a specific formalism and under a uniform prior over tasks, that weakness
maximisation is both necessary and sufficient to maximise the probability that an
inferred hypothesis generalises, while MDL minimisation is neither.

Source frozen at `inputs/BENNETT-WEAKNESS-2023/` (SRC-BENNETT-WEAKNESS-2023);
arXiv v4 PDF read in full for this entry.

## The formalism (Definitions 1–3, 7)

Necessary because "weakness" and "description length" both have to be well defined on the
same object:

- **Environment.** A set `Φ` of states; a *declarative program* is `f : Φ → {true,false}`;
  `P` is the set of all of them.
- **Implementable language.** A finite vocabulary `v ⊂ P`; statements are the satisfiable
  subsets `L_v = {l ⊆ v : ∃φ ∀p∈l, p(φ)=true}`. The **extension** of a statement is
  `Z_a = {b ∈ L_v : a ⊆ b}` — every statement that entails it. Because `v` is finite,
  `L_v` is finite and everything below is computable in principle.
- **v-task.** `α = ⟨S_α, D_α, M_α⟩`: situations `S_α ⊂ L_v`, correct decisions
  `D_α ⊆ Z_{S_α}`, and *models* `M_α = {l ∈ L_v : Z_{S_α} ∩ Z_l = D_α}` — the hypotheses
  that decide α exactly right. `α ⊏ ω` ("child of") when `S_α ⊂ S_ω` and `D_α ⊆ D_ω`;
  induction is inferring from a child a hypothesis that is still a model of the parent.
- **Proxy.** `q_v : L_v → ℕ`, to be maximised. **Weakness** is `q_v(l) = |Z_l|`.
  **Description length** as a proxy is `q_v(l) = 1/|l|` (shorter is better).

Note what weakness is *not*: it is a property of a statement's extension, not of its form
or length. The paper's own gloss — a simple statement need not be weak ("all things are
blue crabs"), and a long one can assert almost nothing.

## Key claims (as reported)

- **Proposition 1 (sufficiency).** For `h ∈ M_α` and unknown parent `ω ⊐ α`,
  `p(h ∈ M_ω | h ∈ M_α, α ⊏ ω) = 2^{|Z̄_{S_α} ∩ Z_h|} / 2^{|Z̄_{S_α}|}`, which is maximised
  by maximising `|Z_h|`.
- **Proposition 2 (necessity).** Generalisation requires `D_ω ⊆ Z_h`, so `|Z_h| ≥ |D_ω|`
  is a precondition; the probability of meeting it is maximised by maximising `|Z_h|`.
  Hence weakness (or a function of it) is the necessary proxy.
- **Proposition 3.** MDL is neither necessary nor sufficient, shown by an explicit
  11-symbol counterexample (`v = {a..h,j,k,z}`, one task with `M_α = {{z}, {j,k}}`)
  where weakness selects `{j,k}` and description length selects `{z}`. Minimising
  length neither implies nor is implied by maximising weakness.
- **Remark 1 (prior).** Absent any task, `p(h ∈ M_ω | h ∈ L_v) = 2^{|Z_h|}/2^{|L_v|}`,
  a computable distribution over all conceivable hypotheses in the language. It is
  maximised by `h = ∅` — assume nothing when you know nothing.
- **No-free-lunch framing.** Under the uniform distribution over `Γ_v` no proxy can match
  weakness maximisation everywhere and beat it somewhere; another proxy can win on
  cherry-picked child/parent pairs only by losing on the rest.
- **Experiments.** Toy 8-bit string prediction (4-bit input + 4-bit output binary addition
  and multiplication), 256 states, propositional-logic vocabulary, PyTorch/SymPy/A*;
  child tasks sampled with `|D_k|` from 4 to 14, 75–256 trials per value. Reported
  generalisation rate for the weakest model was 110–500% of the MDL model's, and the
  average extent of generalisation 103–156%. Example (binary addition, `|D_k|=14`):
  rate .68 ± .106 for weakest vs .24 ± .097 for MDL.
- **"Bennett's Razor."** *Explanations should be no more specific than necessary.*
- **Application.** Offered as a simpler explanation of why DeepMind's Apperception Engine
  generalises well: its universally quantified formulae are weak by construction, and its
  tailored language is a choice of `v`. Speculative closing remarks on LLM fabrication and
  grokking as weakness-related — explicitly flagged as future work by the author.

## Relevance to this program

This is an epistemology/AGI paper with **no cryptanalytic content**. It is in the corpus
as methodology, and it bears on exactly one thing: how the Idea Generator and the
Coordinator choose between candidate hypotheses that fit the same evidence.

Two things it sharpens:

1. **The program's default is length-flavoured and unexamined.** "Simplest explanation
   consistent with the runs" is the reflex when a batch of evidence admits several
   readings. Proposition 3's counterexample is a reminder that short and weak are
   independent axes, so the reflex is a choice, not a neutrality.
2. **It names the failure mode of over-specific hypotheses.** A hypothesis fitted tightly
   to the curves, parameters, and budget actually tested has a small extension: it is
   *strong*, and by this argument it is exactly the kind that fails to survive a change of
   parameters. That is the same phenomenon the program's rule 4 scoping discipline guards
   against from the other side.

The distinction to hold onto, because conflating them would corrupt both: **weakness
constrains which hypothesis to prefer among those equally consistent with the evidence;
rule 4 constrains what the evidence is allowed to be said to support.** A weak hypothesis
is not a licence for a broad claim. Preferring the least-specific hypothesis and reporting
the narrowest defensible evidence claim are compatible and must both hold.

Distilled as a technique in [[KN-TECH-276d30]]; the untested question of whether any of it
survives a non-uniform task distribution is [[KN-OPEN-875d43]].

## Limits of applicability, and what was not verified

- **The optimality result is conditional on a uniform distribution over tasks**
  (Definition 4), and the author states this in the abstract, the footnotes, and the
  conclusion. Cryptanalytic hypothesis spaces are about as far from uniform as a task
  distribution gets — structure is the entire subject matter. Nothing in the paper
  establishes what weakness maximisation does under a structured prior, and the paper's
  own no-free-lunch framing implies that under a non-uniform prior some other proxy may
  dominate it.
- **It is conditional on the enactive formalism.** The author flags this (footnote 2:
  "conditional upon certain assumptions regarding the nature of cognition as enactive").
  Whether this program's hypotheses can be embedded in a finite `L_v` at all — such that
  `|Z_h|` is defined, let alone computable — is untested and is the practical blocker.
- **Proofs read, NOT independently re-derived here.** They are short informal
  cardinality arguments, not machine-checked. Step 3 of Proposition 1 (that
  `|Z̄_{S_α} ∩ Z_h|` increases monotonically with `|Z_h|`) is asserted with a
  one-line justification and is the step to examine first if this is ever relied on.
- **Experiments NOT reproduced.** The appendices and code (ref [1],
  doi 10.5281/zenodo.7641742) were not retrieved. Scale is 8-bit toy arithmetic with an
  A* search over models; the paper reports no cost for computing the weakest model, and
  weakness maximisation is a search over `M_α`, which is where any practical objection
  would land. The 1.1–5× figure is the paper's, at that scale, on those two operations.
- **`confidence: reported`** — full text read, claims relayed. Nothing in this entry has
  been verified by this program.
