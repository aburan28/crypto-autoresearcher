---
id: KN-LIT-5932
type: literature
title: "Programmable Hash Functions from Lattices: Short Signatures and IBEs with Small Key Sizes"
authors:
  - "Jiang Zhang"
  - "Yu Chen"
  - "Zhenfeng Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, lattice, pairing, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Driven by the open problem raised by Hofheinz and Kiltz (Journal of Cryptology, 2012), we study the formalization of lattice-based programmable hash function (PHF), and give two types of constructions by using several techniques such as a novel combination of cover-free sets and lattice trapdoors. Under the Inhomogeneous Small Integer Solution (ISIS) assumption, we show that any (non-trivial) lattice-based PHF is collision-resistant, which gives a direct application of this new primitive.

## Key claims (as reported)
- We further demonstrate the power of lattice-based PHF by giving generic constructions of signature and identity-based encryption (IBE) in the standard model, which not only provide a way to unify several previous lattice-based schemes using the partitioning proof techniques, but also allow us to obtain a new short signature scheme and a new fully secure IBE scheme with keys consisting of a logarithmic number of matrices/vectors in the security parameter κ.
- Besides, we also give a refined way of combining two concrete PHFs to construct an improved short signature scheme with short verification keys from weaker assumptions.
- In particular, our methods depart from the confined guessing technique of Böhl et al.
- (Eurocrypt’13) that was used to construct previous standard model short signature schemes with short verification keys by Ducas and Micciancio (Crypto’14) and by Alperin-Sheriff (PKC’15), and allow us to achieve existential unforgeability against chosen message attacks (EUF-CMA) without resorting to chameleon hash functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98160292 (1).pdf`
- `downloads/98160292.pdf`
