---
id: KN-LIT-3875
type: literature
title: "Fiat-Shamir With Aborts:"
authors:
  - "Applications to Lattice"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We demonstrate how the framework that is used for creating efficient number-theoretic ID and signature schemes can be transferred into the setting of lattices. This results in constructions of the most efficient to-date identification and signature schemes with security based on the worst-case hardness of problems in ideal lattices.

## Key claims (as reported)
- In particular, our ID scheme has communication complexity of around 65, 000 bits and the length of the signatures produced by our signature scheme is about 50, 000 bits.
- All prior lattice-based identification schemes required on the order of millions of bits to be transferred, while all previous lattice-based signature schemes were either stateful, too inefficient, or produced signatures whose lengths were also on the order of millions of bits.
- The security of our identification scheme is based on the hardness of finding the approximate shortest vector to within a factor of Õ(n2 ) in the standard model, while the security of the signature scheme is based on the same assumption in the random oracle model.
- Our protocols are very efficient, with all operations requiring Õ(n) time.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59120596 (1).pdf`
- `downloads/59120596 (2).pdf`
- `downloads/59120596 (3).pdf`
- `downloads/59120596.pdf`
