---
id: KN-LIT-1027
type: literature
title: "Protecting the most significant bits in scalar multiplication algorithms"
authors:
  - "Estuardo Alpirez Bock"
  - "Lukasz Chmielewski"
  - "Konstantina Miteloudi"
year: 2022
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2022/1254"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2022/1254"
tags: [cryptanalysis, curve-arithmetic, ecdsa, elliptic-curve, implementation, isogeny, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Montgomery Ladder is widely used for implementing the scalar multiplication in elliptic curve cryptographic designs. This algorithm is efficient and provides a natural robustness against (simple) sidechannel attacks.

## Key claims (as reported)
- Previous works however showed that implementations of the Montgomery Ladder using Lopez-Dahab projective coordinates easily leak the value of the most significant bits of the secret scalar, which led to a full key recovery in an attack known as LadderLeak [3].
- In light of such leakage, we analyse further popular methods for implementing the Montgomery Ladder.
- We first consider open source software implementations of the X25519 protocol which implement the Montgomery Ladder based on the ladderstep algorithm from Düll et al.
- We confirm via power measurements that these implementations also easily leak the most significant scalar bits, even when implementing Z-coordinate randomisations.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2022-1254.pdf`
