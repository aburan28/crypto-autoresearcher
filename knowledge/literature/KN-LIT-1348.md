---
id: KN-LIT-1348
type: literature
title: "Attacks on PRISM-id via Torsion over Small Extension Fields"
authors:
  - "Kohei Nakagawa"
  - "Hiroshi Onuki"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/1602"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/1602"
tags: [complexity-theory, elliptic-curve, endomorphism, extension-field, isogeny, mov-fr, pqc, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
PRISM is an isogeny-based cryptographic framework that relies on the hardness of computing a large prime-degree isogeny from a supersingular elliptic curve with an unknown endomorphism ring. It includes both an identification scheme PRISM-id and a signature scheme PRISM-sig.

## Key claims (as reported)
- In this work, we present two attacks on PRISM-id.
- First, we analyze the probability that a randomly sampled prime q in PRISM-id results in a q-torsion subgroup defined over a small extension field, and we show that this probability is higher than claimed in the original proposal.
- Exploiting this observation, we construct classical forgery attacks on PRISM-id.
- The first attack addresses the scenario in which the attacker cannot reject a challenge.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-1602.pdf`
