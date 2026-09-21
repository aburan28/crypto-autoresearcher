---
id: KN-LIT-7653
type: literature
title: "Learning the Word Problem: Geodesic Lengths and Cryptographic Applications"
authors:
  - "Elisabeth Fink"
year: 2026
venue: "arXiv preprint arXiv:2607.26241 [cs.CR, cs.LG, math.GR]"
identifiers:
  eprint: null
  doi: null
  arxiv: "2607.26241"
  url: "https://arxiv.org/abs/2607.26241"
tags: [word-problem, group-theory, non-commutative-crypto, machine-learning, graph-neural-network, cryptanalysis, broken-platform, baumslag-solitar, artin-group, structural-leakage, ml-to-theorem]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Introduces **WPNet**, a graph-neural-network architecture that solves the **Word
Problem heuristically** by mapping unreduced words to dynamic graph structures and
learning to cluster algebraically equivalent elements in a continuous embedding space —
identifying a word's **geodesic representative without executing discrete reduction
steps**.

Demonstrated on the Baumslag–Solitar group `BS(1,2)` and on an Artin group. A model
variant predicts the **geodesic length** of an unreduced word in both groups. As a
cryptographic application, WPNet is reported **successfully deployed against the
Wagner–Magyarik public-key cryptosystem**.

## Key claims (as reported)
- A GNN can learn geodesic representatives and geodesic lengths for `BS(1,2)` and an
  Artin group, heuristically — the abstract says "heuristically," and reports no
  guarantee, no accuracy figure, and no failure rate.
- Geodesic length is **structural leakage** exploitable against a word-problem-based
  cryptosystem; the Wagner–Magyarik scheme is reported broken by it.
- The Word Problem is generally undecidable, but the platform families used in
  post-quantum proposals are chosen precisely for having fast word problems — which is
  the tension the paper exploits.

## Relevance to this program
Two threads, and the second is the one that matters for this harness.

**Non-commutative group-based cryptography** is the sibling family to the algebraic
platforms this program tracks. Wagner–Magyarik is an old and long-suspect scheme, so
"broken" here is a low bar and this entry does not treat it as a landmark break. What
is worth recording is the **attack surface**: a hardness assumption stated as "the word
problem is hard" leaks through a *quantitative* correlate — geodesic length — that need
not be computed exactly to be useful. The generalizable rule is that an assumption
about a **decision** problem can be defeated by an **approximate metric** correlated
with the hidden structure, and any proposal in this program resting on
"reduction/normalization is expensive" should be checked for such a correlate.

**Learned models as cryptanalytic instruments.** This is another data point in the
thread [[KN-LIT-7614]], [[KN-LIT-7594]], [[KN-LIT-7595]] and [[KN-LIT-7588]] track:
a neural model producing a usable cryptanalytic result on a mathematical object. Two
honest qualifications: the target is weak, and a **heuristic** solver with no reported
accuracy is not a certificate. Under `docs/claims-and-verification.md`, a learned
geodesic predictor produces at best a *candidate* — the certificate is the recovered
word, checkable by reduction. Nothing in the abstract states whether outputs were
verified that way.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the arXiv API abstract for 2607.26241,
retrieved 2026-08-01 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-28, categories cs.CR, cs.LG and math.GR, single author. Preprint — not
peer-reviewed, no DOI or venue as of this entry.

NOT verified here: the WPNet architecture; any accuracy, generalization, or failure
rate (the abstract reports none); the geodesic-length prediction quality; the parameter
sizes at which Wagner–Magyarik was attacked; and whether recovered solutions were
independently verified. **"Successfully deployed against Wagner–Magyarik" is relayed
verbatim and is not a scoped break claim in this program's tiers.**
