---
id: KN-LIT-4642
type: literature
title: "Lattice Signatures Without Trapdoors"
authors:
  - "Vadim Lyubashevsky"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mov-fr, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide an alternative method for constructing latticebased digital signatures which does not use the “hash-and-sign” methodology of Gentry, Peikert, and Vaikuntanathan (STOC 2008). Our resulting signature scheme is secure, in the random oracle model, based on the worst-case hardness of the Õ(n1.5 )-SIVP problem in general lattices.

## Key claims (as reported)
- The secret key, public key, and the signature size of our scheme are smaller than in all previous instantiations of the hash-and-sign signature, and our signing algorithm is also quite simple, requiring just a few matrixvector multiplications and rejection samplings.
- We then also show that by slightly changing the parameters, one can get even more efficient signatures that are based on the hardness of the Learning With Errors problem.
- Our construction naturally transfers to the ring setting, where the size of the public and secret keys can be significantly shrunk, which results in the most practical to-date provably secure signature scheme based on lattices.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72370731 (1).pdf`
- `downloads/72370731 (2).pdf`
- `downloads/72370731 (3).pdf`
- `downloads/72370731.pdf`
