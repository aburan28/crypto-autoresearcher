---
id: KN-LIT-6950
type: literature
title: "The Bitcoin Backbone Protocol: Analysis and Applications?"
authors:
  - "Juan Garay"
  - "Aggelos Kiayias"
  - "Nikos Leonardos"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Bitcoin is the first and most popular decentralized cryptocurrency to date. In this work, we extract and analyze the core of the Bitcoin protocol, which we term the Bitcoin backbone, and prove two of its fundamental properties which we call common prefix and chain quality in the static setting where the number of players remains fixed.

## Key claims (as reported)
- Our proofs hinge on appropriate and novel assumptions on the “hashing power” of the adversary relative to network synchronicity; we show our results to be tight under high synchronization.
- Next, we propose and analyze applications that can be built “on top” of the backbone protocol, specifically focusing on Byzantine agreement (BA) and on the notion of a public transaction ledger.
- Regarding BA, we observe that Nakamoto’s suggestion falls short of solving it, and present a simple alternative which works assuming that the adversary’s hashing power is bounded by 1/3.
- The public transaction ledger captures the essence of Bitcoin’s operation as a cryptocurrency, in the sense that it guarantees the liveness and persistence of committed transactions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560288 (1).pdf`
- `downloads/90560288.pdf`
