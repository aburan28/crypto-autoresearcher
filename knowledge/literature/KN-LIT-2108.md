---
id: KN-LIT-2108
type: literature
title: "A masked ring-LWE implementation"
authors:
  - "Oscar Reparaz"
  - "Sujoy Sinha Roy"
  - "Frederik Vercauteren"
  - "Ingrid Verbauwhede"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, factoring, fhe, finite-field, implementation, lattice, pqc, quantum, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Lattice-based cryptography has been proposed as a postquantum public-key cryptosystem. In this paper, we present a masked ringLWE decryption implementation resistant to first-order side-channel attacks.

## Key claims (as reported)
- Our solution has the peculiarity that the entire computation is performed in the masked domain.
- This is achieved thanks to a new, bespoke masked decoder implementation.
- The output of the ring-LWE decryption are Boolean shares suitable for derivation of a symmetric key.
- We have implemented a hardware architecture of the masked ring-LWE processor on a Virtex-II FPGA, and have performed side channel analysis to confirm the soundness of our approach.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930660 (1).pdf`
- `downloads/92930660.pdf`
