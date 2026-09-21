---
id: KN-LIT-6418
type: literature
title: "Secure Computation Against Adaptive Auxiliary Information"
authors:
  - "Elette Boyle"
  - "Sanjam Garg"
  - "Abhishek Jain"
  - "Yael Tauman Kalai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of secure two-party and multiparty computation (MPC) in a setting where a cheating polynomial-time adversary can corrupt an arbitrary subset of parties and, in addition, learn arbitrary auxiliary information on the entire states of all honest parties (including their inputs and random coins), in an adaptive manner, throughout the protocol execution. We formalize a definition of multiparty computation secure against adaptive auxiliary information (AAI-MPC), that intuitively guarantees that such an adversary learns no more than the function output and the adaptive auxiliary information.

## Key claims (as reported)
- In particular, if the auxiliary information contains only partial, “noisy,” or computationally invertible information on secret inputs, then only such information should be revealed.
- We construct a universally composable AAI two-party and multiparty computation protocol that realizes any (efficiently computable) functionality against malicious adversaries in the common reference string model, based on the linear assumption over bilinear groups and the n-th residuosity assumption.
- Apart from theoretical interest, our result has interesting applications to the regime of leakage-resilient cryptography.
- At the heart of our construction is a new two-round oblivious transfer protocol secure against malicious adversaries who may receive adaptive auxiliary information.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420242 (1).pdf`
- `downloads/80420242 (2).pdf`
- `downloads/80420242 (3).pdf`
- `downloads/80420242.pdf`
