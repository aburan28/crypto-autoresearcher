---
id: KN-LIT-5449
type: literature
title: "On the Concrete Security of Goldreich’s Pseudorandom Generator"
authors:
  - "Geoffroy Couteau"
  - "Aurélien Dupin"
  - "Pierrick Méaux"
  - "Mélissa Rossi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Local pseudorandom generators allow to expand a short random string into a long pseudo-random string, such that each output bit depends on a constant number d of input bits. Due to its extreme efficiency features, this intriguing primitive enjoys a wide variety of applications in cryptography and complexity.

## Key claims (as reported)
- In the polynomial regime, where the seed is of size n and the output of size ns for s > 1, the only known solution, commonly known as Goldreich’s PRG, proceeds by applying a simple d-ary predicate to public random size-d subsets of the bits of the seed.
- While the security of Goldreich’s PRG has been thoroughly investigated, with a variety of results deriving provable security guarantees against class of attacks in some parameter regimes and necessary criteria to be satisfied by the underlying predicate, little is known about its concrete security and efficiency.
- Motivated by its numerous theoretical applications and the hope of getting practical instantiations for some of them, we initiate a study of the concrete security of Goldreich’s PRG, and evaluate its resistance to cryptanalytic attacks.
- Along the way, we develop a new guess-and-determine-style attack, and identify new criteria which refine existing criteria and capture the security guarantees of candidate local PRGs in a more fine-grained way.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272273 (1).pdf`
- `downloads/11272273.pdf`
