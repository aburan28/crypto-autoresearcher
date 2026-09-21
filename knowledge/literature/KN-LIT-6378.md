---
id: KN-LIT-6378
type: literature
title: "Scale-Invariant Fully Homomorphic Encryption over the Integers"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At Crypto 2012, Brakerski constructed a scale-invariant fully homomorphic encryption scheme based on the LWE problem, in which the same modulus is used throughout the evaluation process, instead of a ladder of moduli when doing “modulus switching”. In this paper we describe a variant of the van Dijk et al.

## Key claims (as reported)
- FHE scheme over the integers with the same scale-invariant property.
- Our scheme has a single secret modulus whose size is linear in the multiplicative depth of the circuit to be homomorphically evaluated, instead of exponential; we therefore construct a leveled fully homomorphic encryption scheme.
- This scheme can be transformed into a pure fully homomorphic encryption scheme using bootstrapping, and its security is still based on the ApproximateGCD problem.
- We also describe an implementation of the homomorphic evaluation of the full AES encryption circuit, and obtain significantly improved performance compared to previous implementations: about 23 seconds (resp.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/83830119 (1).pdf`
- `downloads/83830119 (2).pdf`
- `downloads/83830119 (3).pdf`
- `downloads/83830119 (4).pdf`
- `downloads/83830119 (5).pdf`
- `downloads/83830119.pdf`
