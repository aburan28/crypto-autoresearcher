---
id: KN-LIT-5937
type: literature
title: "Projective Coordinates Leak"
authors:
  - "David Naccache"
  - "Nigel P. Smart"
  - "Jacques Stern"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, ecdsa, elliptic-curve, implementation, jacobian, protocol, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Denoting by P = [k]G the elliptic-curve double-and-add multiplication of a public base point G by a secret k, we show that allowing an adversary access to the projective representation of P , obtained using a particular double and add method, may result in information being revealed about k. Such access might be granted to an adversary by a poor software implementation that does not erase the Z coordinate of P from the computer's memory or by a computationally-constrained secure token that sub-contracts the ane conversion of P to the external world.

## Key claims (as reported)
- From a wider perspective, our result proves that the choice of representation of elliptic curve points can reveal information about their underlying discrete logarithms, hence casting potential doubt on the appropriateness of blindly modelling elliptic-curves as generic groups.
- As a conclusion, our result underlines the necessity to sanitize Z after the ane conversion or, alternatively, randomize P before releasing it out.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/projective (1).pdf`
- `downloads/projective (2).pdf`
- `downloads/projective.pdf`
