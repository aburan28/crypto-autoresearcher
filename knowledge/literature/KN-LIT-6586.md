---
id: KN-LIT-6586
type: literature
title: "Short Leakage Resilient and Non-malleable"
authors:
  - "Secret Sharing Schemes"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, quantum, side-channel, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Leakage resilient secret sharing (LRSS) allows a dealer to share a secret amongst n parties such that any authorized subset of the parties can recover the secret from their shares, while an adversary that obtains shares of any unauthorized subset of parties along with bounded leakage from the other shares learns no information about the secret. Non-malleable secret sharing (NMSS) provides a guarantee that even shares that are tampered by an adversary will reconstruct to either the original message or something independent of it.

## Key claims (as reported)
- The most important parameter of LRSS and NMSS schemes is the size of each share.
- For LRSS, in the local leakage model (i.e., when the leakage functions on each share are independent of each other and bounded), Srinivasan and Vasudevan (CRYPTO 2019), gave a scheme for threshold access structures with share size of approximately (3 · message length + μ), where μ is the number of bits of leakage tolerated from every share.
- For the case of NMSS, the best known result (again due to the above work) has share size of (11·message length).
- In this work, we build LRSS and NMSS schemes with much improved share size.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070331 (1).pdf`
- `downloads/135070331.pdf`
