---
id: KN-LIT-3858
type: literature
title: "Fault Template Attacks on Block Ciphers"
authors:
  - "Exploiting Fault Propagation"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, mov-fr, mpc, pairing, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Fault attacks (FA) are one of the potent practical threats to modern cryptographic implementations. Over the years the FA techniques have evolved, gradually moving towards the exploitation of devicecentric properties of the faults.

## Key claims (as reported)
- In this paper, we exploit the fact that activation and propagation of a fault through a given combinational circuit (i.e., observability of a fault) is data-dependent.
- Next, we show that this property of combinational circuits leads to powerful Fault Template Attacks (FTA), even for implementations having dedicated protections against both power and fault-based vulnerabilities.
- The attacks found in this work are applicable even if the fault injection is made at the middle rounds of a block cipher, which are out of reach for most of the other existing fault analysis strategies.
- Quite evidently, they also work for a known-plaintext scenario.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105206 (1).pdf`
- `downloads/12105206.pdf`
