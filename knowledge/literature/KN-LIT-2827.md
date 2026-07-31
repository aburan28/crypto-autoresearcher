---
id: KN-LIT-2827
type: literature
title: "CAIRN 2: An FPGA Implementation of the Sieving Step in the Number Field Sieve Method"
authors:
  - "Tetsuya Izu"
  - "Jun Kogure"
  - "Takeshi Shimoyama"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, hash, implementation, lattice, number-theory, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The hardness of the integer factorization problem assures the security of some public-key cryptosystems including RSA, and the number field sieve method (NFS), the most efficient algorithm for factoring large integers currently, is a threat for such cryptosystems. Recently, dedicated factoring devices attract much attention since it might reduce the computing cost of the number field sieve method.

## Key claims (as reported)
- In this paper, we report implementational and experimental results of a dedicated sieving device “CAIRN 2” with Xilinx’s FPGA which is designed to handle up to 768-bit integers.
- Used algorithm is based on the line sieving, however, in order to optimize the efficiency, we adapted a new implementational method (the pipelined sieving).
- In addition, we actually factored a 423bit integer in about 30 days with the developed device CAIRN 2 for the sieving step and usual PCs for other steps.
- As far as the authors know, this is the first FPGA implementation and experiment of the sieving step in NFS.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/47270364 (1).pdf`
- `downloads/47270364 (2).pdf`
- `downloads/47270364 (3).pdf`
- `downloads/47270364.pdf`
