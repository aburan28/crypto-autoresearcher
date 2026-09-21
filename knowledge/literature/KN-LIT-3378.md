---
id: KN-LIT-3378
type: literature
title: "Delayed-Key Message Authentication for Streams"
authors:
  - "Marc Fischlin"
  - "Anja Lehmann"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, protocol, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider message authentication codes for streams where the key becomes known only at the end of the stream. This usually happens in key-exchange protocols like SSL and TLS where the exchange phase concludes by sending a MAC for the previous transcript and the newly derived key.

## Key claims (as reported)
- SSL and TLS provide tailor-made solutions for this problem (modifying HMAC to insert the key only at the end, as in SSL, or using upstream hashing as in TLS).
- Here we take a formal approach to this problem of delayed-key MACs and provide solutions which are “as secure as schemes where the key would be available right away” but still allow to compute the MACs online even if the key becomes known only later.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/59780288 (1).pdf`
- `downloads/59780288 (2).pdf`
- `downloads/59780288 (3).pdf`
- `downloads/59780288.pdf`
