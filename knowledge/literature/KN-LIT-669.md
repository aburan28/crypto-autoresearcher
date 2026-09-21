---
id: KN-LIT-669
type: literature
title: "Ease of Side-Channel Attacks on AES-192/256 by Targeting Extreme Keys"
authors:
  - "Antoine Wurcker"
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/340"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/340"
tags: [cryptanalysis, pairing, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Concerning the side-channel attacks on Advanced Encryption Standard, it seems that majority of studies focus on the lowest size: AES-128. Even when adaptable to higher sizes (AES-192 and AES-256), lots of state-of-the-art attacks see their complexity substantially raised.

## Key claims (as reported)
- Indeed, it often requires to perform two consecutive dependent attacks.
- The first is similar to the one applied on AES-128, but a part of the key remains unknown and must be retrieved through a second attack directly dependent on the success of the first.
- This configuration may substantially raise the complexity for the attacker, especially if new signal acquisitions with specific input, built using the first key part recovered, must be performed.
- Any error/uncertainty in the first attack raise the key recovery complexity.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2019-340.pdf`
