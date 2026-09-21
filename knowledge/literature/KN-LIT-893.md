---
id: KN-LIT-893
type: literature
title: "New First-Order Secure AES Performance Records"
authors:
  - "Aein Rezaei Shahmirzadi"
  - "Dušan Božilov"
  - "Amir Moradi"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/037"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/037"
tags: [implementation, pairing, provable-security, quantum, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Being based on a sound theoretical basis, masking schemes are commonly applied to protect cryptographic implementations against Side-Channel Analysis (SCA) attacks. Constructing SCA-protected AES, as the most widely deployed block cipher, has been naturally the focus of several research projects, with a direct application in industry.

## Key claims (as reported)
- The majority of SCA-secure AES implementations introduced to the community opted for low area and latency overheads considering ApplicationSpecific Integrated Circuit (ASIC) platforms.
- Albeit a few, those which particularly targeted Field Programmable Gate Arrays (FPGAs) as the implementation platform yield either a low throughput or a not-highly secure design.
- In this work, we fill this gap by introducing first-order glitch-extended probing secure masked AES implementations highly optimized for FPGAs, which support both encryption and decryption.
- Compared to the state of the art, our designs efficiently map the critical non-linear parts of the masked S-box into the built-in Block RAMs (BRAMs).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-037.pdf`
