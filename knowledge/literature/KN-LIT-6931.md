---
id: KN-LIT-6931
type: literature
title: "tardigrade: An Atomic Broadcast Protocol for Arbitrary Network Conditions"
authors:
  - "Erica Blum"
  - "Jonathan Katz"
  - "Julian Loss"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We study the problem of atomic broadcast—the underlying problem addressed by blockchain protocols—in the presence of a malicious adversary who corrupts some fraction of the n parties running the protocol. Existing protocols are either robust for any number of corruptions in a synchronous network (where messages are delivered within some known time ∆) but fail if the synchrony assumption is violated, or tolerate fewer than n/3 corrupted parties in an asynchronous network (where messages can be delayed arbitrarily) and cannot tolerate more corruptions even if the network happens to be well behaved.

## Key claims (as reported)
- We design an atomic broadcast protocol (tardigrade) that, for any ts ≥ ta with 2ts + ta < n, provides security against ts corrupted parties if the network is synchronous, while remaining secure when ta parties are corrupted even in an asynchronous network.
- We show that tardigrade achieves optimal tradeoffs between ts and ta .
- Finally, we show a second protocol (upgrade) with similar (but slightly weaker) guarantees that achieves per-transaction communication complexity linear in n.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900042 (1).pdf`
- `downloads/130900042.pdf`
