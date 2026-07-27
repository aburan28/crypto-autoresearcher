---
id: KN-LIT-3874
type: literature
title: "Fiat-Shamir Transformation of Multi-Round Interactive Proofs"
authors:
  - "Thomas Attema"
  - "Serge Fehr"
  - "Michael Klooß"
  - "⋆ ⋆ ⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, provable-security, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The celebrated Fiat-Shamir transformation turns any publiccoin interactive proof into a non-interactive one, which inherits the main security properties (in the random oracle model) of the interactive version. While originally considered in the context of 3-move public-coin interactive proofs, i.e., so-called Σ-protocols, it is now applied to multiround protocols as well.

## Key claims (as reported)
- Unfortunately, the security loss for a (2μ + 1)move protocol is, in general, approximately Qμ , where Q is the number of oracle queries performed by the attacker.
- In general, this is the best one can hope for, as it is easy to see that this loss applies to the μ-fold sequential repetition of Σ-protocols, but it raises the question whether certain (natural) classes of interactive proofs feature a milder security loss.
- In this work, we give positive and negative results on this question.
- On the positive side, we show that for (k1 , . . . , kμ )-special-sound protocols (which cover a broad class of use cases), the knowledge error degrades linearly in Q, instead of Qμ .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470021 (1).pdf`
- `downloads/137470021.pdf`
