---
id: KN-LIT-3c87b9
type: literature
title: "RACE: a Rapid ARM Cryptographic Engine for code-based Classic McEliece PQC scheme"
authors:
  - "Wen Wu"
  - "Jiankuo Dong"
  - "Xuecheng Liu"
  - "Shuzhou Sun"
  - "Zhenjiang Dong"
  - "Jingqiang Lin"
  - "Fu Xiao"
year: 2025
venue: null
identifiers:
  eprint: "iacr:2025/2310"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2025/2310"
tags: [classic-mceliece, code-based, implementation, arm, engine, acceleration]
confidence: reported
citation_verified: web
added: "2026-08-03"
superseded_by: null
---

## Contribution
**RACE**, a rapid ARM cryptographic engine for Classic McEliece — an
ARM-targeted acceleration engine for the scheme's operations.

## Key claims (as reported)
- An ARM-based acceleration engine for Classic McEliece.

## Relevance to this program
Held with the ARM cluster ([[KN-LIT-1359cc]], [[KN-LIT-a740ab]]). Classic
McEliece's very large public key makes platform-level implementation work
unusually consequential — the constraint is memory and bandwidth, not
arithmetic, which is an unusual profile for a cryptosystem and a reminder that
**the binding resource is not always the one the algorithm description
emphasises.**

**Does not bear on the ECDLP.**

## Not verified here
Citation verified against the IACR ePrint record for report 2025/2310 (title and author list checked) on 2026-08-03.

Bibliographic line transcribed from the Classic McEliece project's "Papers" page (https://classic.mceliece.org/papers.html, page version 2026.06.13), retrieved 2026-08-03; see `knowledge/gathers/GATHER-20260803.md` for the sweep record.

Performance figures and the target ARM platform are NOT recorded here.

The full text was **not read** for this entry. Everything under "Key claims" is relayed, not re-derived, and no complexity figure, benchmark, or security estimate in this entry has been reproduced by this program.
