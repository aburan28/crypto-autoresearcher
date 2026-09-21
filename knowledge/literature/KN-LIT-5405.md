---
id: KN-LIT-5405
type: literature
title: "On Strong Simulation and Composable Point Obfuscation"
authors:
  - "Nir Bitansky"
  - "Ran Canetti"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Virtual Black Box (VBB) property for program obfuscators provides a strong guarantee: Anything computable by an efficient adversary given the obfuscated program can also be computed by an efficient simulator with only oracle access to the program. However, we know how to achieve this notion only for very restricted classes of programs.

## Key claims (as reported)
- This work studies a simple relaxation of VBB: Allow the simulator unbounded computation time, while still allowing only polynomially many queries to the oracle.
- We then demonstrate the viability of this relaxed notion, which we call Virtual Grey Box (VGB), in the context of fully composable obfuscators for point programs: It is known that, w.r.t.
- VBB, if such obfuscators exist then there exist multi-bit point obfuscators (aka “digital lockers”) and subsequently also very strong variants of encryption that are resilient to various attacks, such as key leakage and keydependent-messages.
- However, no composable VBB-obfuscators for point programs have been shown.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230513 (1).pdf`
- `downloads/62230513 (2).pdf`
- `downloads/62230513 (3).pdf`
- `downloads/62230513.pdf`
