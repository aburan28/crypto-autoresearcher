---
id: KN-LIT-2094
type: literature
title: "A Lightweight Concurrent Fault Detection Scheme for the AES S-boxes Using Normal Basis"
authors:
  - "Mehran Mozaffari-Kermani"
  - "Arash Reyhani-Masoleh"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The use of an appropriate fault detection scheme for hardware implementation of the Advanced Encryption Standard (AES) makes the standard robust to the internal defects and fault attacks. To minimize the overhead cost of the fault detection AES structure, we present a lightweight concurrent fault detection scheme for the composite field realization of the S-box using normal basis.

## Key claims (as reported)
- The structure of the S-box is divided into blocks and the predicted parities of these blocks are obtained.
- Through an exhaustive search among all available composite fields and transformation matrices that map the polynomial basis representation in binary field to the normal basis representation in composite field, we have found the optimum solution for the least overhead S-box and its parity predictions.
- Finally, using FPGA implementations, the complexities of the proposed schemes are compared to those of the previously reported ones.
- It is shown that the FPGA implementations of the S-box using normal basis representation in composite fields outperform the traditional ones using polynomial basis for both with and without fault detection capability.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/51540111 (1).pdf`
- `downloads/51540111 (2).pdf`
- `downloads/51540111 (3).pdf`
- `downloads/51540111.pdf`
