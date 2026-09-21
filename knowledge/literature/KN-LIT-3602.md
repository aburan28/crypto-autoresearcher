---
id: KN-LIT-3602
type: literature
title: "Efficient Oblivious Transfer in the Bounded-Storage Model"
authors:
  - "Dowon Hong"
  - "Ku-Young Chang"
  - "Heuisu Ryu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we propose an efficient OT1N scheme in the bounded storage model, which is provably secure without complexity assumptions. Under the assumption that a public random string of M bits is broadcasted, the protocol is secure against any computationally unbounded dishonest receiver who can store τ M bits, τ √ < 1.

## Key claims (as reported)
- The protocol requires the sender and the receiver to store N · O( kM ) bits, where k is a security parameter.
- When N = 2, our protocol is similar to that of Ding [10] but has more efficient round and communication complexities.
- Moreover, in case of N > 2, if the sender and receiver can store √ N · O( kM ) bits, we are able to construct a protocol for OT1N which has almost the same complexity as in OT12 scheme.
- Ding’s protocol was constructed by using the interactive hashing protocol which is introduced by Noar, Ostrovsky, Venkatesan and Yung [15] with very large roundcomplexity.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/25010142 (1).pdf`
- `downloads/25010142 (2).pdf`
- `downloads/25010142.pdf`
