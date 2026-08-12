---
id: KN-LIT-922
type: literature
title: "Round-Efficient Byzantine Agreement and Multi-Party Computation with Asynchronous Fallback"
authors:
  - "Giovanni Deligios"
  - "Martin Hirt"
  - "Chen-Da Liu-Zhang⋆"
year: 2021
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2021/1141"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2021/1141"
tags: [mpc, pairing, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Protocols for Byzantine agreement (BA) and secure multi-party computation (MPC) can be classified according to the underlying communication model. The two most commonly considered models are the synchronous one and the asynchronous one.

## Key claims (as reported)
- Synchronous protocols typically lose their security guarantees as soon as the network violates the synchrony assumptions.
- Asynchronous protocols remain secure regardless of the network conditions, but achieve weaker security guarantees even when the network is synchronous.
- Recent works by Blum, Katz and Loss [TCC’19], and Blum, Liu-Zhang and Loss [CRYPTO’20] introduced BA and MPC protocols achieving security guarantees in both settings: security up to ts corruptions in a synchronous network, and up to ta corruptions in an asynchronous network, under the provably optimal threshold trade-offs ta ≤ ts and ta + 2ts < n.
- However, current solutions incur a high synchronous round complexity when compared to state-of-the-art purely synchronous protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2021-1141.pdf`
