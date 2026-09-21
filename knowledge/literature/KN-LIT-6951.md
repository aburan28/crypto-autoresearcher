---
id: KN-LIT-6951
type: literature
title: "The Broadcast Message Complexity of Secure Multiparty Computation"
authors:
  - "Sanjam Garg"
  - "Aarushi Goel"
  - "Abhishek Jain"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the broadcast message complexity of secure multiparty computation (MPC), namely, the total number of messages that are required for securely computing any functionality in the broadcast model of communication. MPC protocols are traditionally designed in the simultaneous broadcast model, where each round consists of every party broadcasting a message to the other parties.

## Key claims (as reported)
- We show that this method of communication is suboptimal; specifically, by eliminating simultaneity, it is, in fact, possible to reduce the broadcast message complexity of MPC.
- More specifically, we establish tight lower and upper bounds on the broadcast message complexity of n-party MPC for every t < n corruption threshold, both in the plain model as well as common setup models.
- For example, our results show that the optimal broadcast message complexity of semi-honest MPC can be much lower than 2n, but necessarily requires at least three rounds of communication.
- We also extend our results to the malicious setting in setup models.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210362 (1).pdf`
- `downloads/119210362.pdf`
