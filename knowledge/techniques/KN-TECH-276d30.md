---
id: KN-TECH-276d30
type: technique
title: Weakness maximisation as a hypothesis-selection proxy — prefer the least specific hypothesis that still fits every observation and control
tags: [methodology, research-protocol, hypothesis-selection, induction, generalisation, weakness, mdl, occams-razor, bennetts-razor, null-object-control, inventor, agentic-harness]
confidence: reported
complexity: >-
  Not a computational technique. In Bennett's formalism the criterion is exactly
  |Z_h|, computable only because the vocabulary is finite and the language toy-sized;
  in this program's hypothesis space it is not computable and is applied as a
  qualitative ordering over candidate hypotheses at review time. Cost is agent-turns
  during ideation and evidence review, plus the extra candidate hypotheses that have
  to be written down before one is chosen.
applicability: >-
  Any point where several distinct hypotheses reproduce the same body of evidence and
  one has to be preferred: Idea Generator candidate ranking, /design-experiment when a
  proposal is turned into a stated hypothesis, and /review-evidence when a decision
  records what a batch of runs supports. Explicitly NOT applicable to deciding what a
  body of evidence is allowed to claim -- that is rule 4 scoping and is a different
  axis (see "Two axes, never conflated").
source_refs: [KN-LIT-3822a6, KN-TECH-056, KN-TECH-080]
added: 2026-08-05
superseded_by: null
---

## The pattern

From Bennett, AGI 2023 ([[KN-LIT-3822a6]], arXiv:2301.12987v4). Two moves, in order:

### 1. Validity first — the hypothesis must fit exactly

A hypothesis is admissible only if it reproduces the observations exactly: in the
formalism, `h ∈ M_α` means `Z_{S_α} ∩ Z_h = D_α`, so `h` must admit every correct
decision **and no incorrect one**. This clause is doing more work than it looks like it
is, and skipping it turns the whole technique into a licence for vacuity: the empty
statement is the weakest of all and explains nothing.

For this program the "no incorrect decision" clause is already instrumented — it is the
null-object control and the nearby-object control of the inventor protocol
([[KN-TECH-056]], [[KN-TECH-080]]). A mechanism that also "explains" the null object has
admitted an incorrect decision. It is not an appealingly weak hypothesis; it is an
invalid one, and it is disqualified before selection begins.

### 2. Among the valid, take the weakest

Weakness is the size of a hypothesis's extension `|Z_h|` — how much it is compatible
with. Prefer the candidate that is **least specific**: that assumes the fewest structural
preconditions on the object, that would produce the same observation across the widest
family of curves/parameters/instances, that rules out the least beyond what the runs
actually ruled out.

Bennett's razor, as stated by the author: *Explanations should be no more specific than
necessary.* The claimed result is that under a uniform prior over tasks this is
**necessary and sufficient** to maximise the probability that the hypothesis generalises,
and that minimum description length is **neither** — short and weak are independent axes,
demonstrated by an explicit counterexample (`M_α = {{z}, {j,k}}`: MDL takes `{z}`,
weakness takes `{j,k}`).

## Operational form in this program

`|Z_h|` is not computable here, so the technique reduces to an ordering discipline
applied by hand. Concretely, at the point where a hypothesis is written down:

1. **Write more than one.** The technique has no content when only one hypothesis was
   ever articulated. Two or three candidates that fit the same runs is the minimum input.
2. **Disqualify on the controls, not on taste.** Any candidate whose mechanism would also
   have produced the observed signal on the null object or the nearby-object control is
   out (step 1 above).
3. **Rank the survivors by how much they assume.** The one that names the fewest
   preconditions on the object — the smallest set of "this works because the curve
   additionally has property X" clauses — is the weakest. Where two differ only in that
   one adds a qualifier the evidence never tested, the qualifier is added specificity
   bought with nothing, and the unqualified form wins.
4. **Record the runner-up and why it lost.** A one-line note in the decision record. If
   the choice was made on length, simplicity, or elegance rather than on specificity, say
   so — that is a different proxy and the point of this entry is that it is a choice.

## Two axes, never conflated

The dangerous misreading is that a weaker hypothesis licenses a broader claim. It does
not, and this program's rule 4 is untouched by anything here:

- **Weakness** governs *which* hypothesis to prefer among those equally consistent with
  the evidence. It is about the hypothesis's content.
- **Rule 4 scoping** governs *what the evidence supports*. It is about the claim's
  warrant, and it stays bound to the tested curves, parameters, solver, and budget
  regardless of how weak or strong the hypothesis is.

Preferring the least specific hypothesis and reporting the narrowest defensible evidence
claim are complementary. Their combination is the honest position: "the weakest mechanism
consistent with these runs is X; these runs establish X only at the tested scale."

## Known limits

- **The optimality proof assumes a uniform distribution over tasks** and the author says
  so repeatedly. This program's hypothesis space is not uniform — structure is its
  subject matter — and the paper's own no-free-lunch framing implies another proxy may
  dominate weakness under a structured prior. The result is therefore a **motivation**
  for this discipline, not a proof that it is optimal here.
  Open problem: [[KN-OPEN-875d43]].
- **Not validated in this program.** Adopted from external work, zero internal evidence,
  no experiment has compared it against the previous informal default. `confidence:
  reported`, and this entry is a candidate practice rather than a validated instrument.
  It does not meet the "validated across two or more experiments" bar the corpus normally
  asks of a `KN-TECH`; it is filed here because it is a selection rule agents apply, and
  it is flagged as unvalidated so nothing downstream can cite it as established.
- **Weakness is undefined, not merely uncomputable, if the hypothesis cannot be embedded
  in a finite language.** Step 3 above is a surrogate for `|Z_h|` chosen by this program,
  not a quantity Bennett's result is about. No claim is made that the surrogate inherits
  any of the paper's guarantees.
- **It says nothing about which hypotheses to generate**, only which to prefer once
  generated. Generation stays governed by [[KN-TECH-056]] and [[KN-TECH-080]].
- **Cheapness is the reason to try it.** Applying it costs a paragraph in a decision
  record. If it is wrong, the cost of having tried it is that paragraph.
