---
id: KN-LIT-2873
type: literature
title: "Characterization of Secure Multiparty Computation Without Broadcast"
authors:
  - "Ran Cohen"
  - "Iftach Haitner"
  - "Eran Omri"
  - "Lior Rotem"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A major challenge in the study of cryptography is characterizing the necessary and sufficient assumptions required to carry out a given cryptographic task. The focus of this work is the necessity of a broadcast channel for securely computing symmetric functionalities (where all the parties receive the same output) when one third of the parties, or more, might be corrupted.

## Key claims (as reported)
- Assuming all parties are connected via a peer-to-peer network, but no broadcast channel (nor a secure setup phase) is available, we prove the following characterization: – A symmetric n-party functionality can be securely computed facing n/3 ≤ t < n/2 corruptions (i.e., honest majority), if and only if it is (n − 2t)-dominated ; a functionality is k-dominated, if any k-size subset of its input variables can be set to determine its output. – Assuming the existence of one-way functions, a symmetric n-party functionality can be securely computed facing t ≥ n/2 corruptions (i.e., no honest majority), if and only if it is 1-dominated and can be securely computed with broadcast.
- It follows that, in case a third of the parties might be corrupted, broadcast is necessary for securely computing non-dominated functionalities (in which “small” subsets of the inputs cannot determine the output), including, as interesting special cases, the Boolean XOR and coin-flipping functionalities.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/95620587 (1).pdf`
- `downloads/95620587.pdf`
