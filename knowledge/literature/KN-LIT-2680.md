---
id: KN-LIT-2680
type: literature
title: "Better Concrete Security for Half-Gates Garbling (in the Multi-Instance Setting)"
authors:
  - "Chun Guo"
  - "Jonathan Katz"
  - "Xiao Wang"
  - "Chenkai Weng"
  - "Yu Yu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, pairing, provable-security, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the concrete security of high-performance implementations of half-gates garbling, which all rely on (hardware-accelerated) AES. We find that current instantiations using k-bit wire labels can be completely broken—in the sense that the circuit evaluator learns all the inputs of the circuit garbler—in time O(2k /C), where C is the total number of (non-free) gates that are garbled, possibly across multiple independent executions.

## Key claims (as reported)
- The attack can be applied to existing circuitgarbling libraries using k = 80 when C ≈ 109 , and would require 267 machine-months and cost about $3500 to implement on the Google Cloud Platform.
- Since the attack can be fully parallelized, it could be carried out in about a month using ≈ 250 machines.
- With this as our motivation, we seek a way to instantiate the hash function in the half-gates scheme so as to achieve better concrete security.
- We present a construction based on AES that achieves optimal security in the single-instance setting (when only a single circuit is garbled).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171199 (1).pdf`
- `downloads/12171199.pdf`
