---
id: KN-LIT-2045
type: literature
title: "A Formal Treatment of Backdoored Pseudorandom Generators"
authors:
  - "Yevgeniy Dodis"
  - "Chaya Ganesh"
  - "Alexander Golovnev"
  - "Ari Juels"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, hash, pairing, protocol, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide a formal treatment of backdoored pseudorandom generators (PRGs). Here a saboteur chooses a PRG instance for which she knows a trapdoor that allows prediction of future (and possibly past) generator outputs.

## Key claims (as reported)
- This topic was formally studied by Vazirani and Vazirani, but only in a limited form and not in the context of subverting cryptographic protocols.
- The latter has become increasingly important due to revelations about NIST’s backdoored Dual EC PRG and new results about its practical exploitability using a trapdoor.
- We show that backdoored PRGs are equivalent to public-key encryption schemes with pseudorandom ciphertexts.
- We use this equivalence to build backdoored PRGs that avoid a well known drawback of the Dual EC PRG, namely biases in outputs that an attacker can exploit without the trapdoor.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560291 (1).pdf`
- `downloads/90560291.pdf`
