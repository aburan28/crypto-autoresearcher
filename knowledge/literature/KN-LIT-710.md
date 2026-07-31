---
id: KN-LIT-710
type: literature
title: "Spin Me Right Round Rotational Symmetry for FPGA-specific AES"
authors: []
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/349"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/349"
tags: [implementation, pairing, provable-security, side-channel, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The effort in reducing the area of AES implementations has largely been focused on Application-Specific Integrated Circuits (ASICs) in which a tower field construction leads to a small design of the AES S-box. In contrast, a naive implementation of the AES S-box has been the status-quo on Field-Programmable Gate Arrays (FPGAs).

## Key claims (as reported)
- A similar discrepancy holds for masking schemes – a wellknown side-channel analysis countermeasure – which are commonly optimized to achieve minimal area in ASICs.
- In this paper we demonstrate a representation of the AES S-box exploiting rotational symmetry which leads to a 50% reduction of the area footprint on FPGA devices.
- We present new AES implementations which improve on the state of the art and explore various trade-offs between area and latency.
- For instance, at the cost of increasing 4.5 times the latency, one of our design variants requires 25% less look-up tables (LUTs) than the smallest known AES on Xilinx FPGAs by Sasdrich and Güneysu at ASAP 2016.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2019-349.pdf`
