---
id: KN-LIT-7542
type: literature
title: "Zero Knowledge Protocols and Signatures from the Restricted Syndrome Decoding Problem Marco Baldi1[0000−0002−8754−5526] , Sebastian Bitzer2[0000−0002−5928−359X]"
authors:
  - "Alessio Pavoni"
  - "Paolo Santini"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, finite-field, hash, lattice, mov-fr, mpc, pqc, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Restricted Syndrome Decoding Problem (R-SDP) corresponds to the Syndrome Decoding Problem (SDP) with the additional constraint that all entries of the solution error vector must live in a fixed subset of the finite field. In this paper, we study how this problem can be applied to the construction of signatures derived from Zero-Knowledge (ZK) protocols.

## Key claims (as reported)
- First, we show that R-SDP appears to be well-suited for this type of application: ZK protocols relying on SDP can easily be modified to use R-SDP, resulting in significant reductions in the communication cost.
- We then introduce and analyze a variant of R-SDP, which we call R-SDP(G), with the property that solution vectors can be represented with a number of bits that is slightly larger than the security parameter (which clearly provides an ultimate lower bound).
- This enables the design of competitive ZK protocols.
- We show that existing ZK protocols can greatly benefit from the use of R-SDP, achieving signature sizes in the order of 7 kB, which are smaller than those of several other schemes submitted to NIST’s additional call for post-quantum digital signatures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602119 (1).pdf`
- `downloads/14602119.pdf`
