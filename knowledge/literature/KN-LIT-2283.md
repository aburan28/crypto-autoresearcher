---
id: KN-LIT-2283
type: literature
title: "A Very Compact Hardware Implementation of the MISTY1 Block Cipher"
authors:
  - "Dai Yamamoto"
  - "Jun Yajima"
  - "Kouichi Itoh"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, provable-security, quantum, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper proposes compact hardware (H/W) implementation for the MISTY1 block cipher, which is an ISO/IEC18033 standard encryption algorithm. In designing the compact H/W, we focused on optimizing the implementation of FO/FI functions, which are the main components of MISTY1.

## Key claims (as reported)
- For this optimization, we propose two new methods; reducing temporary registers for the FO function, and shortening the critical path for the FI function.
- According to our logic synthesis on a 0.18-μm CMOS standard cell library based on our proposed method, the gate size is 3.95 Kgates, which is the smallest as far as we know.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/51540311 (1).pdf`
- `downloads/51540311 (2).pdf`
- `downloads/51540311 (3).pdf`
- `downloads/51540311.pdf`
