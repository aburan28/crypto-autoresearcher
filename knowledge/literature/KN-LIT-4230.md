---
id: KN-LIT-4230
type: literature
title: "Homomorphic Encryption for Finite Automata"
authors:
  - "Nicholas Genise"
  - "Craig Gentry"
  - "Shai Halevi"
  - "Baiyu Li"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a somewhat homomorphic GSW-like encryption scheme, natively encrypting matrices rather than just single elements. This scheme offers much better performance than existing homomorphic encryption schemes for evaluating encrypted (nondeterministic) finite automata (NFAs).

## Key claims (as reported)
- Differently from GSW, we do not know how to reduce the security of this scheme from LWE, instead we reduce it from a stronger assumption, that can be thought of as an inhomogeneous variant of the NTRU assumption.
- This assumption (that we term iNTRU) may be useful and interesting in its own right, and we examine a few of its properties.
- We also examine methods to encode regular expressions as NFAs, and in particular explore a new optimization problem, motivated by our application to encrypted NFA evaluation.
- In this problem, we seek to minimize the number of states in an NFA for a given expression, subject to the constraint on the ambiguity of the NFA.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210324 (1).pdf`
- `downloads/119210324.pdf`
