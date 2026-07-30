---
id: KN-LIT-4223
type: literature
title: "Highly-Efficient Universally-Composable Commitments based on the DDH Assumption"
authors:
  - "Yehuda Lindell"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Universal composability (a.k.a. UC security) provides very strong security guarantees for protocols that run in complex real-world environments.

## Key claims (as reported)
- In particular, security is guaranteed to hold when the protocol is run concurrently many times with other secure and possibly insecure protocols.
- Commitment schemes are a basic building block in many cryptographic constructions, and as such universally composable commitments are of great importance in constructing UC-secure protocols.
- In this paper, we construct highly efficient UC-secure commitments from the standard DDH assumption, in the common reference string model.
- Our commitment stage is non-interactive, has a common reference string with O(1) group elements, and has complexity of O(1) exponentiations for committing to a group element (to be more exact, the effective cost is that of 23 13 exponentiations overall, for both the commit and decommit stages).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320451 (1).pdf`
- `downloads/66320451 (2).pdf`
- `downloads/66320451 (3).pdf`
- `downloads/66320451.pdf`
