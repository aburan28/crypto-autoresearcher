---
id: KN-LIT-5516
type: literature
title: "On the Local Leakage Resilience of Linear Secret Sharing Schemes"
authors:
  - "Fabrice Benhamouda"
  - "Akshay Degwekar"
  - "Yuval Ishai"
  - "Tal Rabin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the following basic question: to what extent are standard secret sharing schemes and protocols for secure multiparty computation that build on them resilient to leakage? We focus on a simple local leakage model, where the adversary can apply an arbitrary function of a bounded output length to the secret state of each party, but cannot otherwise learn joint information about the states.

## Key claims (as reported)
- We show that additive secret sharing schemes and high-threshold instances of Shamir’s secret sharing scheme are secure under local leakage attacks when the underlying field is of a large prime order and the number of parties is sufficiently large.
- This should be contrasted with the fact that any linear secret sharing scheme over a small characteristic field is clearly insecure under local leakage attacks, regardless of the number of parties.
- Our results are obtained via tools from Fourier analysis and additive combinatorics.
- We present two types of applications of the above results and techniques.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993361 (1).pdf`
- `downloads/10993361.pdf`
