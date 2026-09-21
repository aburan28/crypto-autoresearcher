---
id: KN-LIT-2894
type: literature
title: "Chosen-prefix Collisions for MD5 and Colliding X.509 Certificates for Different Identities"
authors:
  - "Marc Stevens"
  - "Arjen Lenstra"
  - "Benne de Weger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, hash, mov-fr, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a novel, automated way to find differential paths for MD5. As an application we have shown how, at an approximate expected cost of 250 calls to the MD5 compression function, for any two chosen message prefixes P and P 0 , suffixes S and S 0 can be constructed such that the concatenated values P kS and P 0 kS 0 collide under MD5.

## Key claims (as reported)
- Although the practical attack potential of this construction of chosen-prefix collisions is limited, it is of greater concern than random collisions for MD5.
- To illustrate the practicality of our method, we constructed two MD5 based X.509 certificates with identical signatures but different public keys and different Distinguished Name fields, whereas our previous construction of colliding X.509 certificates required identical name fields.
- We speculate on other possibilities for abusing chosen-prefix collisions.
- More details than can be included here can be found on www.win.tue.nl/hashclash/ChosenPrefixCollisions/.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45150001 (1).pdf`
- `downloads/45150001 (2).pdf`
- `downloads/45150001 (3).pdf`
- `downloads/45150001.pdf`
