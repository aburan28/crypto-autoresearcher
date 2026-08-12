---
id: KN-LIT-6700
type: literature
title: "Sleuth: Automated Verification of Software Power Analysis Countermeasures"
authors:
  - "Ali Galip Bayrak"
  - "Francesco Regazzoni"
  - "David Novo"
  - "Paolo Ienne"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, mov-fr, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Security analysis is a crucial concern in the design of hardware and software systems, yet there is a distinct lack of automated methodologies. In this paper, we remedy this situation for the verification of software countermeasure implementations.

## Key claims (as reported)
- In this context, verifying the security of a protected implementation against side-channel attacks corresponds to assessing whether any particular leakage in any particular computational phase is statistically dependent on the secret data and statistically independent of any random information used to protect the implementation.
- We present a novel methodology to reduce this verification problem into a set of Boolean satisfiability problems, which can be efficiently solved by leveraging recent advances in SAT solving.
- To show the effectiveness of our methodology, we have implemented an automatic verification tool, named Sleuth, as an advanced analysis pass in the back-end of the LLVM compiler.
- Our results show that one can automatically detect several examples of classic pitfalls in the implementation of countermeasures with reasonable runtimes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860192 (1).pdf`
- `downloads/80860192 (2).pdf`
- `downloads/80860192 (3).pdf`
- `downloads/80860192.pdf`
