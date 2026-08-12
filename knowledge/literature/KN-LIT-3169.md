---
id: KN-LIT-3169
type: literature
title: "Correcting Subverted Random Oracles"
authors:
  - "Alexander Russell"
  - "Qiang Tang"
  - "Moti Yung"
  - "Hong-Sheng Zhou"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The random oracle methodology has proven to be a powerful tool for designing and reasoning about cryptographic schemes, and can often act as an effective bridge between theory and practice. In this paper, we focus on the basic problem of correcting faulty—or adversarially corrupted—random oracles, so that they can be confidently applied for such cryptographic purposes.

## Key claims (as reported)
- We prove that a simple construction can transform a “subverted” random oracle—which disagrees with the original one at a negligible fraction of inputs—into a construction that is indifferentiable from a random function.
- Our results permit future designers of cryptographic primitives in typical kleptographic settings (i.e., with adversaries who may subvert the implementation of cryptographic algorithms but undetectable via blackbox testing) to use random oracles as a trusted black box, in spite of not trusting the implementation.
- Our analysis relies on a general rejection re-sampling lemma which is a tool of possible independent interest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993222 (1).pdf`
- `downloads/10993222.pdf`
