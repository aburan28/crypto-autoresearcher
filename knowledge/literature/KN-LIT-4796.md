---
id: KN-LIT-4796
type: literature
title: "Low-communication parallel quantum multi-target preimage search"
authors:
  - "Gustavo Banegas"
  - "Daniel J. Bernstein"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, pollard-rho, pqc, quantum, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The most important pre-quantum threat to AES-128 is the 1994 van Oorschot–Wiener “parallel rho method”, a low-communication parallel pre-quantum multi-target preimage-search algorithm. This algorithm uses a mesh of p small processors, each running for approximately 2128/pt fast steps, to find one of t independent AES keys k1 , . . . , kt , given the ciphertexts AESk1 (0), . . . , AESkt (0) for a shared plaintext 0.

## Key claims (as reported)
- NIST has claimed a high post-quantum security level for AES-128, starting from the following rationale: “Grover’s algorithm requires a longrunning serial computation, which is difficult to implement in practice.
- In a realistic attack, one has to run many smaller instances of the algorithm in parallel, which makes the quantum speedup less dramatic.” NIST has also stated that resistance to multi-key attacks is desirable; but, in a realistic parallel setting, a straightforward multi-key application of Grover’s algorithm costs more than targeting one key at a time.
- This paper introduces a different quantum algorithm for multi-target preimage search.
- This algorithm shows, in the same realistic parallel setting, that quantum preimage search benefits asymptotically from having multiple targets.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/groverrho-20170818.pdf`
