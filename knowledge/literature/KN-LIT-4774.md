---
id: KN-LIT-4774
type: literature
title: "Lockable Obfuscation from Circularly Insecure"
authors:
  - "Fully Homomorphic Encryption"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In a lockable obfuscation scheme, a party called the obfuscator takes as input a circuit C, a lock value y, and a message m, and outputs an obfuscated circuit. Given the obfuscated circuit, an evaluator can run it on an input x and learn the message if C(x) = y.

## Key claims (as reported)
- For security, we require that the obfuscation reveals no information on the circuit as long as the lock y has high entropy even given the circuit C.
- The only known constructions of lockable obfuscation schemes require indistinguishability obfuscation (iO) or the learning with errors (LWE) assumption.
- Furthermore, in terms of technique, all known constructions, excluding iO-based, are build from provably secure variations of graphinduced multilinear maps.
- We show a generic construction of a lockable obfuscation scheme built from a (leveled) fully homomorphic encryption scheme that is circularly insecure.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/131770058 (1).pdf`
- `downloads/131770058.pdf`
