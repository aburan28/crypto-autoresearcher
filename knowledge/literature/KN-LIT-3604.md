---
id: KN-LIT-3604
type: literature
title: "Efficient Pairings and ECC for Embedded Systems"
authors:
  - "Thomas Unterluggauer"
  - "Erich Wenger"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, elliptic-curve, implementation, pairing, prime-field, provable-security, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The research on pairing-based cryptography brought forth a wide range of protocols interesting for future embedded applications. One significant obstacle for the widespread deployment of pairing-based cryptography are its tremendous hardware and software requirements.

## Key claims (as reported)
- In this paper we present three side-channel protected hardware/software designs for pairing-based cryptography yet small and practically fast: our plain ARM Cortex-M0+-based design computes a pairing in less than one second.
- The utilization of a multiply-accumulate instructionset extension or a light-weight drop-in hardware accelerator that is placed between CPU and data memory improves runtime up to six times.
- With a 10.1 kGE large drop-in module and a 49 kGE large platform, our design is one of the smallest pairing designs available.
- Its very practical runtime of 162 ms for one pairing on a 254-bit BN curve and its reusability for other elliptic-curve based crypto systems offer a great solution for every microprocessor-based embedded application.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310164 (1).pdf`
- `downloads/87310164 (2).pdf`
- `downloads/87310164 (3).pdf`
- `downloads/87310164.pdf`
