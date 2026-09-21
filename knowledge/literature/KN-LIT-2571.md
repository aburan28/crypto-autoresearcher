---
id: KN-LIT-2571
type: literature
title: "Approximate Trapdoors for Lattices and Smaller Hash-and-Sign Signatures"
authors:
  - "Yilei Chen"
  - "Nicholas Genise"
  - "Pratyay Mukherjee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study a relaxed notion of lattice trapdoor called approximate trapdoor, which is defined to be able to invert Ajtai’s one-way function approximately instead of exactly. The primary motivation of our study is to improve the efficiency of the cryptosystems built from lattice trapdoors, including the hash-and-sign signatures.

## Key claims (as reported)
- Our main contribution is to construct an approximate trapdoor by modifying the gadget trapdoor proposed by Micciancio and Peikert [Eurocrypt 2012].
- In particular, we show how to use the approximate gadget trapdoor to sample short preimages from a distribution that is simulatable without knowing the trapdoor.
- The analysis of the distribution uses a theorem (implicitly used in past works) regarding linear transformations of discrete Gaussians on lattices.
- Our approximate gadget trapdoor can be used together with the existing optimization techniques to improve the concrete performance of the hashand-sign signature in the random oracle model under (Ring-)LWE and (Ring-)SIS assumptions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210158 (1).pdf`
- `downloads/119210158.pdf`
