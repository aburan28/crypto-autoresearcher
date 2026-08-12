---
id: KN-LIT-1231
type: literature
title: "Erebor and Durian: Full Anonymous Ring Signatures from Quaternions and Isogenies"
authors:
  - "Giacomo Borin"
  - "Yi-Fu Lai"
  - "Antonin Leroux"
year: 2024
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2024/1185"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/1185"
tags: [elliptic-curve, endomorphism, isogeny, lattice, mov-fr, pairing, pqc, protocol, sidh-csidh, signature, supersingular, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct two efficient post-quantum ring signatures with anonymity against full key exposure from isogenies, addressing the limitations of existing isogeny-based ring signatures. First, we present an efficient concrete distinguisher for the SQIsign simulator when the signing key is provided using one transcript.

## Key claims (as reported)
- This shows that turning SQIsign into an efficient full anonymous ring signature requires some new ideas.
- Second, we propose a variant of SQIsign (Asiacrypt’20) that is resistant to the distinguisher attack with only a ˆ1.33 increase in size and we render it to a ring signature, that we refer as Erebor.
- This variant introduces a new zero-knowledge assumption that ensures full anonymity.
- The efficiency of Erebor remains comparable to that of SQIsign, with only a proportional increase due to the ring size.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2024-1185.pdf`
