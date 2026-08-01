---
id: KN-LIT-6320
type: literature
title: "Round-optimal Black-box Commit-and-prove with Succinct Communication"
authors:
  - "Susumu Kiyoshima"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, hash, pairing, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a four-round black-box construction of a commitand-prove protocol with succinct communication. Our construction is WI and has constant soundness error, and it can be upgraded into a one that is ZK and has negligible soundness error by relying on a roundpreserving transformation of Khurana et al.

## Key claims (as reported)
- Our construction is obtained by combining the MPC-in-the-head technique of Ishai et al.
- (SICOMP 2009) with the two-round succinct argument of Kalai et al.
- (STOC 2014), and the main technical novelty lies in the analysis of the soundness—we show that, although the succinct argument of Kalai et al. does not necessarily provide soundness for N P statements, it can be used in the MPC-in-the-head technique for proving the consistency of committed MPC views.
- Our construction is based on sub-exponentially hard collision-resistant hash functions, two-round PIRs, and two-round OTs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171049 (1).pdf`
- `downloads/12171049.pdf`
