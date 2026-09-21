---
id: KN-LIT-1480
type: literature
title: "SQIsign2DPush: Faster Signature Scheme Using 2-Dimensional Isogenies"
authors:
  - "Kohei Nakagawa"
  - "Hiroshi Onuki"
year: 2025
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2025/897"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/897"
tags: [elliptic-curve, isogeny, pairing, pqc, quantum, sidh-csidh, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Isogeny-based cryptography involves cryptographic schemes whose security is based on the hardness of a mathematical problem called the isogeny problem and is attracting attention as one of the candidates for post-quantum cryptography. A representative isogeny-based cryptography is the signature scheme called SQIsign, which was submitted to the NIST PQC standardization competition for additional signature.

## Key claims (as reported)
- SQIsign has attracted much attention because of its very short signature and key size among candidates for the NIST PQC standardization.
- Recently, many new signature schemes using high-dimensional isogenies have been proposed, such as SQIsignHD, SQIsign2D-West, SQIsgn2DEast, and SQIPrime.
- Last year, SQIsign advanced to Round 2 of the NIST competition and was updated to version 2.0 (we call it SQIsignv2.0), which is based on SQIsign2D-West.
- SQIsign-v2.0 achieves smaller signature sizes and faster verification.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2025-897.pdf`
