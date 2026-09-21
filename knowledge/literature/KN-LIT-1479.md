---
id: KN-LIT-1479
type: literature
title: "SQIsign2D2 : New SQIsign2D Variant by Leveraging Power Smooth Isogenies in Dimension One"
authors:
  - "Zheng Xu"
  - "Kaizhan LinB"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/920"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/920"
tags: [isogeny, pqc, sidh-csidh, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we propose SQIsign2D2 , a novel digital signature scheme within the SQIsign2D family. Unlike other SQIsign2D variants, SQIsign2D2 employs the prime p = CD − 1 as the field char√ acteristic, where D = 2e2 , C = 3e3 and C ≈ D ≈ p.

## Key claims (as reported)
- By leveraging 2 accessible C-isogenies, SQIsign2D significantly reduces the degree requirements for two-dimensional isogeny computations, thereby lowering the overall computational overhead compared to other SQIsign2D variants.
- We also provide a proof-of-concept implementation of SQIsign2D2 , and give an efficiency comparison between SQIsign2D2 and other SQIsign2D variants.
- In particular, the experimental results demonstrate that the key generation and signing phases of SQIsign2D2 are more than twice as fast as those of SQIsign2D-East at the NIST-I security level, respectively.
- Additionally, the verification performance in SQIsign2D2 exhibits marginally improved efficiency.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-920.pdf`
