---
id: KN-LIT-5685
type: literature
title: "Order-C Secure Multiparty Computation for Highly Repetitive Circuits"
authors:
  - "Gabrielle Beck"
  - "Aarushi Goel"
  - "Abhishek Jain"
  - "Gabriel Kaptchuk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, mpc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Running secure multiparty computation (MPC) protocols with hundreds or thousands of players would allow leveraging large volunteer networks (such as blockchains and Tor) and help justify honest majority assumptions. However, most existing protocols have at least a linear (multiplicative) dependence on the number of players, making scaling difficult.

## Key claims (as reported)
- Known protocols with asymptotic efficiency independent of the number of parties (excluding additive factors) require expensive circuit transformations that induce large overheads.
- We observe that the circuits used in many important applications of MPC such as training algorithms used to create machine learning models have a highly repetitive structure.
- We formalize this class of circuits and propose an MPC protocol that achieves O(|C|) total complexity for this class.
- We implement our protocol and show that it is practical and outperforms O(n|C|) protocols for modest numbers of players.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960050 (1).pdf`
- `downloads/126960050.pdf`
