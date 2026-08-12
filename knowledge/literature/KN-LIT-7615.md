---
id: KN-LIT-7615
type: literature
title: "Certified in Theory, Broken in Practice: Assumption Gaps in Cryptographic Model Certification"
authors:
  - "Carter Luck"
  - "Olive Franzese-McLaughlin"
  - "Elisaweta Masserova"
  - "Akira Takahashi"
  - "Antigoni Polychroniadou"
  - "Nicolas Papernot"
year: 2026
venue: 'arXiv preprint arXiv:2607.21839 [cs.CR]'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.21839'
  url: https://arxiv.org/abs/2607.21839
tags: [assumption-gap, certification, zero-knowledge-proof, auditing, benchmark-overfitting, scope-of-claim, security-definition, methodology, claim-tier, adjacent]
confidence: reported
citation_verified: web
added: "2026-07-29"
superseded_by: null
---

## Contribution
Shows that cryptographic model certification (CMC) schemes built on zero-knowledge
proofs certify the **wrong thing**: they prove a property holds on a *fixed audit
dataset*, without ensuring it generalizes to other datasets from the same
distribution.

The gap is exploitable. As reported, an adversarial model provider can engineer
training data so that the model certifies **over 99% accuracy on the audit dataset**
while achieving **under 30% accuracy on fresh samples from the same distribution** —
and the proof is perfectly valid throughout. The paper then formalizes security notions
that close the gap, gives a generic protocol template, and proves it satisfies them.

## Relevance to this program
Ingested as a **claim-discipline** entry. This is not cryptanalysis and has no ECDLP
content whatsoever — it concerns privacy-preserving ML auditing. **Does not bear on the
ECDLP.**

It is here because it is a clean, adversarially-demonstrated instance of the exact
failure mode `AGENTS.md` rule 4 and `docs/claims-and-verification.md` exist to prevent:
**a proof that is sound but whose statement is scoped more narrowly than the claim it
gets read as supporting.** The cryptography is not broken; the *binding between what
was proven and what the reader concludes* is broken. Nobody lied, and the certificate
verifies.

The direct analogue in this program is the gap between a **measured** result and the
**scope** it is reported under: a solver that succeeds on a fixed, frozen instance set
at toy scale, whose run records all verify, presented as evidence about the problem
class at cryptographic scale. The program's defence is rule 4's scoping requirement and
the solution-certificate re-verification in `docs/claims-and-verification.md`. This
paper is evidence that the defence is load-bearing rather than ceremonial — the
99%-versus-30% gap is what the failure looks like when someone is actively trying.

Worth pairing with `KN-TECH-049` (calibrating claims against public challenge records)
and `KN-TECH-052` (extrapolating cost exponents from bounded experiments), both of
which address the same "does this measurement support the claim being made from it"
question from the statistical side rather than the definitional side.

No harness change is proposed here; the existing rules already cover the failure mode.
This is a citable external instance of *why* they do.

## Not verified here
Full paper not read; claims relayed from the arXiv abstract retrieved from the arXiv
API on 2026-07-29 (hence `confidence: reported`). arXiv metadata: submitted
2026-07-23, primary category cs.CR. Preprint — not peer-reviewed, no DOI or venue as of
this entry.

NOT verified here: the attack construction; the 99%/30% figures, which are relayed from
the abstract and were **not** independently reproduced; the proposed security notions;
and the claim that the generic protocol template satisfies them. The analogy to this
program's scoping rules is **this entry's reading**, not a claim made by the paper.
