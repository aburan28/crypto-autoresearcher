---
id: KN-LIT-2814
type: literature
title: "Broadcast-Optimal Two-Round MPC?"
authors:
  - "Ran Cohen"
  - "Juan Garay"
  - "Vassilis Zikas"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mov-fr, mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
An intensive effort by the cryptographic community to minimize the round complexity of secure multi-party computation (MPC) has recently led to optimal two-round protocols from minimal assumptions. Most of the proposed solutions, however, make use of a broadcast channel in every round, and it is unclear if the broadcast channel can be replaced by standard point-to-point communication in a round-preserving manner, and if so, at what cost on the resulting security.

## Key claims (as reported)
- In this work, we provide a complete characterization of the trade-off between number of broadcast rounds and achievable security level for tworound MPC tolerating arbitrarily many active corruptions.
- Specifically, we consider all possible combinations of broadcast and point-to-point rounds against the three standard levels of security for maliciously secure MPC protocols, namely, security with identifiable, unanimous, and selective abort.
- For each of these notions and each combination of broadcast and point-to-point rounds, we provide either a tight feasibility or an infeasibility result of two-round MPC.
- Our feasibility results hold assuming two-round OT in the CRS model, whereas our impossibility results hold given any correlated randomness.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12105475 (1).pdf`
- `downloads/12105475.pdf`
