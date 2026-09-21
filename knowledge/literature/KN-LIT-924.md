---
id: KN-LIT-924
type: literature
title: "Secure Linear Aggregation Using Decentralized"
authors:
  - "Threshold Additive Homomorphic Encryption"
year: 2021
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2111.10753"
  url: "https://arxiv.org/abs/2111.10753"
tags: [elliptic-curve, fhe, lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Secure linear aggregation is to linearly aggregate private inputs of different users with privacy protection. The server in a federated learning (FL) environment can fulfill any linear computation on private inputs of users through the secure linear aggregation.

## Key claims (as reported)
- At present, based on pseudo-random number generator and one-time padding technique, one can efficiently compute the sum of user inputs in FL, but linear calculations of user inputs are not well supported.
- Based on decentralized threshold additive homomorphic encryption (DTAHE) schemes, this paper provides a secure linear aggregation protocol, which allows the server to multiply the user inputs by any coefficients and to sum them together, so that the server can build a full connected layer or a convolution layer on top of user inputs.
- The protocol adopts the framework of Bonawitz et al. to provide fault tolerance for user dropping out, and exploits a blockchain smart contract to encourage the server honest.
- The paper gives a security model, security proofs and a concrete lattice based DTAHE scheme for the protocol.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2111.10753v1.pdf`
