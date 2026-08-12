---
id: KN-LIT-6521
type: literature
title: "Security of Symmetric Encryption against Mass Surveillance"
authors:
  - "Mihir Bellare"
  - "Kenneth G. Paterson"
  - "Phillip Rogaway"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Motivated by revelations concerning population-wide surveillance of encrypted communications, we formalize and investigate the resistance of symmetric encryption schemes to mass surveillance. The focus is on algorithm-substitution attacks (ASAs), where a subverted encryption algorithm replaces the real one.

## Key claims (as reported)
- We assume that the goal of “big brother” is undetectable subversion, meaning that ciphertexts produced by the subverted encryption algorithm should reveal plaintexts to big brother yet be indistinguishable to users from those produced by the real encryption scheme.
- We formalize security notions to capture this goal and then offer both attacks and defenses.
- In the first category we show that successful (from the point of view of big brother) ASAs may be mounted on a large class of common symmetric encryption schemes.
- In the second category we show how to design symmetric encryption schemes that avoid such attacks and meet our notion of security.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160245 (1).pdf`
- `downloads/86160245 (2).pdf`
- `downloads/86160245 (3).pdf`
- `downloads/86160245 (4).pdf`
- `downloads/86160245 (5).pdf`
- `downloads/86160245.pdf`
