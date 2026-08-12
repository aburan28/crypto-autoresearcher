---
id: KN-LIT-6671
type: literature
title: "Simplex Consensus: A Simple and Fast Consensus Protocol"
authors:
  - "Benjamin Y Chan"
  - "Rafael Pass"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, pairing, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a theoretical framework for analyzing the efficiency of consensus protocols, and apply it to analyze the optimistic and pessimistic confirmation times of state-of-the-art partially-synchronous protocols in the so-called “rotating leader/random leader” model of consensus (recently popularized in the blockchain setting). We next present a new and simple consensus protocol in the partially synchronous setting, tolerating f < n/3 byzantine faults; in our eyes, this protocol is essentially as simple to describe as the simplest known protocols, but it also enjoys an even simpler security proof, while matching and, even improving, the efficiency of the state-of-the-art (according to our theoretical framework).

## Key claims (as reported)
- As with the state-of-the-art protocols, our protocol assumes a (bare) PKI, a digital signature scheme, collision-resistant hash functions, and a random leader election oracle, which may be instantiated with a random oracle (or a CRS).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369120 (1).pdf`
- `downloads/14369120.pdf`
