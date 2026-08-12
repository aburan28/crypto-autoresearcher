---
id: KN-LIT-5355
type: literature
title: "On Ideal Lattices and Learning with Errors Over Rings"
authors:
  - "Vadim Lyubashevsky"
  - "Chris Peikert"
  - "Oded Regev"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mpc, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The “learning with errors” (LWE) problem is to distinguish random linear equations, which have been perturbed by a small amount of noise, from truly uniform ones. The problem has been shown to be as hard as worst-case lattice problems, and in recent years it has served as the foundation for a plethora of cryptographic applications.

## Key claims (as reported)
- Unfortunately, these applications are rather inefficient due to an inherent quadratic overhead in the use of LWE.
- A main open question was whether LWE and its applications could be made truly efficient by exploiting extra algebraic structure, as was done for lattice-based hash functions (and related primitives).
- We resolve this question in the affirmative by introducing an algebraic variant of LWE called ring-LWE, and proving that it too enjoys very strong hardness guarantees.
- Specifically, we show that the ring-LWE distribution is pseudorandom, assuming that worst-case problems on ideal lattices are hard for polynomial-time quantum algorithms.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320288 (2).pdf`
- `downloads/66320288 (3).pdf`
- `downloads/66320288 (5).pdf`
- `downloads/66320288 (7).pdf`
