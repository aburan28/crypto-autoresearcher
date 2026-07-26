---
id: KN-LIT-6708
type: literature
title: "Smaller Keys for Code-based Cryptography: QC-MDPC McEliece Implementations on Embedded Devices"
authors:
  - "Stefan Heyse"
  - "Ingo von Maurich"
  - "Tim Güneysu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, elliptic-curve, implementation, lattice, quantum, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the last years code-based cryptosystems were established as promising alternatives for asymmetric cryptography since they base their security on well-known NP-hard problems and still show decent performance on a wide range of computing platforms. The main drawback of code-based schemes, including the popular proposals by McEliece and Niederreiter, are the large keys whose size is inherently determined by the underlying code.

## Key claims (as reported)
- In a very recent approach, Misoczki et al. proposed to use quasi-cyclic MDPC (QC-MDPC) codes that allow for a very compact key representation.
- In this work, we investigate novel implementations of the McEliece scheme using such QC-MDPC codes tailored for embedded devices, namely a Xilinx Virtex-6 FPGA and an 8-bit AVR microcontroller.
- In particular, we evaluate and improve different approaches to decode QC-MDPC codes.
- Besides competitive performance for encryption and decryption on the FPGA, we achieved a very compact implementation on the microcontroller using only 4,800 and 9,600 bits for the public and secret key at 80 bits of equivalent symmetric security.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860189 (1).pdf`
- `downloads/80860189 (2).pdf`
- `downloads/80860189 (3).pdf`
- `downloads/80860189.pdf`
