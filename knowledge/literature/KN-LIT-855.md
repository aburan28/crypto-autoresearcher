---
id: KN-LIT-855
type: literature
title: "DeCSIDH: Delegating isogeny computations in the CSIDH setting"
authors:
  - "Robi Pedersen"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/700"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/700"
tags: [class-group, elliptic-curve, endomorphism, finite-field, hash, isogeny, number-theory, pairing, pqc, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Delegating heavy computations to auxiliary servers, while keeping the inputs secret, presents a practical solution for computationally limited devices to use resource-intense cryptographic protocols, such as those based on isogenies, and thus allows the deployment of post-quantum security on mobile devices and in the internet of things. We propose two algorithms for the secure and verifiable delegation of isogeny computations in the CSIDH setting.

## Key claims (as reported)
- We then apply these algorithms to different instances of CSIDH and to the signing algorithms SeaSign and CSI-FiSh.
- Our algorithms present a communication-cost trade-off.
- Asymptotically (for high communication), the cost for the delegator is reduced by a factor 9 for the original CSIDH-512 parameter set and a factor 30 for SQALE’d CSIDH-4096, while the relative cost of SeaSign vanishes.
- Even for much lower communication cost, we come close to these asymptotic results.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-700.pdf`
