---
id: KN-LIT-1856
type: literature
title: "Scalable High-Throughput FPGA Architecture for SMAC Message"
authors:
  - "Authentication Code"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1466"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1466"
tags: [implementation, protocol, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
SMAC is a recently proposed by Wang et al. stand-alone Message Authentication Code (MAC) constructed from repeated applications of the AES round function and featuring an aggregation mode, SMAC-1×n, for scalable parallel processing. Although originally designed for high-throughput CPU implementations leveraging AES-NI instructions, its structural properties suggest strong compatibility with hardware parallelism.

## Key claims (as reported)
- However, no systematic FPGA-oriented architectural study of SMAC has been reported.
- This paper presents a scalable FPGA architecture of SMAC implemented on a Xilinx Kintex UltraScale+ KCU116 platform.
- The Π transformation is evaluated in a single clock cycle using fully combinational AES rounds, and throughput scaling is achieved through physical replication of aggregation lanes.
- All SMAC-1×n configurations up to n = 16 are implemented and evaluated.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1466.pdf`
