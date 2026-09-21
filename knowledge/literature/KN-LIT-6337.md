---
id: KN-LIT-6337
type: literature
title: "Round-Optimal Secure Multiparty Computation with Honest Majority"
authors:
  - "Prabhanjan Ananth"
  - "Arka Rai Choudhuri"
  - "Aarushi Goel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the exact round complexity of secure multiparty computation (MPC) in the honest majority setting. We construct several round-optimal n-party protocols, tolerating any t < n2 corruptions.

## Key claims (as reported)
- Security with abort: We give the first construction of two round MPC for general functions that achieves security with abort against malicious adversaries in the plain model.
- The security of our protocol only relies on one-way functions.
- Guaranteed output delivery: We also construct protocols that achieve security with guaranteed output delivery: (i) Against failstop adversaries, we construct two round MPC either in the (bare) public-key infrastructure model with no additional assumptions, or in the plain model assuming two-round semi-honest oblivious transfer.
- In three rounds, however, we can achieve security assuming only one-way functions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993430 (1).pdf`
- `downloads/10993430.pdf`
