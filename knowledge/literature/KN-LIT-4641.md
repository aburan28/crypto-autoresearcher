---
id: KN-LIT-4641
type: literature
title: "Lattice Signatures and Bimodal Gaussians"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [ecdsa, fhe, lattice, mpc, prime-field, quantum, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Our main result is a construction of a lattice-based digital signature scheme that represents an improvement, both in theory and in practice, over today’s most efficient lattice schemes. The novel scheme is obtained as a result of a modification of the rejection sampling algorithm that is at the heart of Lyubashevsky’s signature scheme (Eurocrypt, 2012) and several other lattice primitives.

## Key claims (as reported)
- Our new rejection sampling algorithm which samples from a bimodal Gaussian distribution, combined with a modified scheme instantiation, ends up reducing the standard deviation of the resulting signatures by a factor that is asymptotically square root in the security parameter.
- The implementations of our signature scheme for security levels of 128, 160, and 192 bits compare very favorably to existing schemes such as RSA and ECDSA in terms of efficiency.
- In addition, the new scheme has shorter signature and public key sizes than all previously proposed lattice signature schemes.
- As part of our implementation, we also designed several novel algorithms which could be of independent interest.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420210 (1).pdf`
- `downloads/80420210 (2).pdf`
- `downloads/80420210 (3).pdf`
- `downloads/80420210.pdf`
