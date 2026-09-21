---
id: KN-LIT-1237
type: literature
title: "Faster algorithms for isogeny computations over extensions of finite fields"
authors:
  - "Shiping Cai"
  - "Mingjie Chen #"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1852"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1852"
tags: [elliptic-curve, extension-field, finite-field, isogeny, pqc, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Any isogeny between two supersingular elliptic curves can be defined over Fp2 , however, this does not imply that computing such isogenies can be done with field operations in Fp2 . In fact, the kernel generators of such isogenies are defined over extension fields of Fp2 , generically with extension degree linear to the isogeny degree.

## Key claims (as reported)
- Most algorithms related to isogeny computations are only efficient when the extension degree is small.
- This leads to efficient algorithms used in isogeny-based cryptographic constructions, but also limits their parameter choices at the same time.
- In this paper, we consider three computational subroutines regarding isogenies, focusing on cases with large extension degrees: computing a basis of l-torsion points, computing the kernel polynomial of an isogeny given a kernel generator, and computing the kernel generator of an isogeny given the corresponding quaternion ideal under the Deuring correspondence.
- We then apply our algorithms to the constructive Deuring correspondence algorithm from [EPSV23] in the case of a generic prime characteristic, achieving around 30% speedup over [EPSV23].

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1852.pdf`
