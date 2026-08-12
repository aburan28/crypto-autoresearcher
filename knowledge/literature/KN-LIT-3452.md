---
id: KN-LIT-3452
type: literature
title: "Distributed Differential Privacy via Shuffling Albert Cheu1(B)"
authors:
  - "David Zeber"
  - "Maxim Zhilyaev"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the problem of designing scalable, robust protocols for computing statistics about sensitive data. Specifically, we look at how best to design differentially private protocols in a distributed setting, where each user holds a private datum.

## Key claims (as reported)
- The literature has mostly considered two models: the “central” model, in which a trusted server collects users’ data in the clear, which allows greater accuracy; and the “local” model, in which users individually randomize their data, and need not trust the server, but accuracy is limited.
- Attempts to achieve the accuracy of the central model without a trusted server have so far focused on variants of cryptographic multiparty computation (MPC), which limits scalability.
- In this paper, we initiate the analytic study of a shuffled model for distributed differentially private algorithms, which lies between the local and central models.
- This simple-to-implement model, a special case of the ESA framework of [5], augments the local model with an anonymous channel that randomly permutes a set of user-supplied messages.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760269 (1).pdf`
- `downloads/114760269.pdf`
