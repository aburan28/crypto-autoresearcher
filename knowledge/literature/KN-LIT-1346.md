---
id: KN-LIT-1346
type: literature
title: "Analyzing the capabilities of HLS and RTL tools in the design of an FPGA Montgomery Multiplier"
authors:
  - "Rares Ifrim"
  - "Decebal Popescu"
year: 2025
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2509.08067"
  url: "https://arxiv.org/abs/2509.08067"
tags: [curve-arithmetic, ecdsa, elliptic-curve, finite-field, implementation, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the analysis of various FPGA design implementations of a Montgomery Modular Multiplier, compatible with the BLS12-381 elliptic curve, using the Coarsely Integrated Operand Scanning approach of working with complete partial products on different digit sizes. The scope of the implemented designs is to achieve a high-frequency, high-throughput solution capable of computing millions of operations per second, which can provide a strong foundation for different Elliptic Curve Cryptography operations such as point addition and point multiplication.

## Key claims (as reported)
- One important constraint for our designs was to only use FPGA DSP primitives for the arithmetic operations between digits employed in the CIOS algorithm as these primitives, when pipelined properly, can operate at a high frequency while also relaxing the resource consumption of FPGA LUTs and FFs.
- The target of the analysis is to see how different design choices and tool configurations influence the frequency, latency and resource consumption when working with the latest AMD-Xilinx tools and Alveo FPGA boards in an RTL-HLS hybrid approach.
- We compare three categories of designs: a Verilog naive approach where we rely on the Vivado synthesizer to automatically choose when and where to use DSPs, a Verilog optimized approach by manually instantiating the DSP primitives ourselves and a complete High-Level Synthesis approach.
- We also compare the FPGA implementations with an optimized software implementation of the same Montgomery multiplier written in Rust.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2509.08067v1.pdf`
