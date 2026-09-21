---
id: KN-LIT-4367
type: literature
title: "Impossibility of Order-Revealing Encryption in Idealized Models"
authors:
  - "Mark Zhandry"
  - "Cong Zhang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An Order-Revealing Encryption (ORE) scheme gives a public procedure by which two ciphertexts can be compared to reveal the order of their underlying plaintexts. The ideal security notion for ORE is that only the order is revealed — anything else, such as the distance between plaintexts, is hidden.

## Key claims (as reported)
- The only known constructions of ORE achieving such ideal security are based on cryptographic multilinear maps and are currently too impractical for real-world applications.
- In this work, we give evidence that building ORE from weaker tools may be hard.
- Indeed, we show black-box separations between ORE and most symmetric-key primitives, as well as public key encryption and anything else implied by generic groups in a black-box way.
- Thus, any construction of ORE must either (1) achieve weaker notions of security, (2) be based on more complicated cryptographic tools, or (3) require non-black-box techniques.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11239143 (1).pdf`
- `downloads/11239143.pdf`
