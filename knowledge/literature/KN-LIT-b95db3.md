---
id: KN-LIT-b95db3
type: literature
title: "Elliptic Curve Paillier Schemes"
authors:
  - "Steven D. Galbraith"
year: 2002
venue: "Journal of Cryptology 15, pp. 129-138 (2002)"
identifiers:
  eprint: null
  doi: "10.1007/s00145-001-0015-6"
  arxiv: null
  url: "https://link.springer.com/article/10.1007/s00145-001-0015-6"
tags: [paillier, ring-curve, composite-modulus, kernel-of-reduction, anomalous, homomorphic-encryption, factoring, ecdlp]
confidence: reported
citation_verified: web
added: "2026-10-01"
superseded_by: null
---

## Contribution

Abstract (verbatim from the publisher page): "This paper is concerned with
generalisations of Paillier's probabilistic encryption scheme from the
integers modulo a square to elliptic curves over rings. Paillier himself
described two public key encryption schemes based on anomalous elliptic
curves over rings. It is argued that these schemes are not secure. A more
natural generalisation of Paillier's scheme to elliptic curves is given."

The mechanism (as understood from the abstract and from the program's own
reading of the anomalous-curve attack, `KN-LIT-088`): over `Z/N^2 Z` the
kernel of reduction `E(Z/N^2 Z) -> E(Z/N Z)` is isomorphic, via the formal
group, to the additive group `Z/N Z`, so a discrete logarithm whose base and
target lie in that kernel is a division. The holder of the factorization of
`N` can move into and out of the kernel; the public cannot. This is the
constructive use of the Smart / Satoh-Araki / Semaev lift.

## Key claims (as reported)

- Paillier's own two anomalous-elliptic-curve variants are argued to be
  insecure (the specific break was not read here; cite only the claim).
- The "natural generalisation" is a homomorphic encryption scheme over an
  elliptic curve over `Z/N^2 Z` with security tied to factoring-type
  assumptions, by analogy with Paillier's composite-residuosity assumption.

Not verified here: the precise assumption named in the body and the exact
parameter choices. Read the full text before relying on those.

## Relevance to this program

Primary source for the elliptic-curve Paillier / Okamoto-Uchiyama line in
`KN-TECH-906e14` and for the "additive kernel of reduction modulo p^2" row
of the hiding-criterion table in `KN-TECH-6ead00`. The expected-negative
open problem `KN-OPEN-b9907c` (partially anomalous ring curves) is the
question of whether this mechanism can be turned from an encryption trapdoor
into a full ECDLP trapdoor; this paper is the constructive baseline it must
be compared against.
