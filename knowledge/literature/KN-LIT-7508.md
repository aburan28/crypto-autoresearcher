---
id: KN-LIT-7508
type: literature
title: "When Messages are Keys: Is HMAC a dual-PRF? Matilda Backendal1[0000−0002−8677−8301] , Mihir Bellare2[0000−0002−8765−5573]"
authors:
  - "Felix Günther"
  - "Matteo Scarlata"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, protocol, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In Internet security protocols including TLS 1.3, KEMTLS, MLS and Noise, HMAC is being assumed to be a dual-PRF, meaning a PRF not only when keyed conventionally (through its first input), but also when “swapped” and keyed (unconventionally) through its second (message) input. We give the first in-depth analysis of the dual-PRF assumption on HMAC.

## Key claims (as reported)
- For the swap case, we note that security does not hold in general, but completely characterize when it does; we show that HMAC is swap-PRF secure if and only if keys are restricted to sets satisfying a condition called feasibility, that we give, and that holds in applications.
- The sufficiency is shown by proof and the necessity by attacks.
- For the conventional PRF case, we fill a gap in the literature by proving PRF security of HMAC for keys of arbitrary length.
- Our proofs are in the standard model, make assumptions only on the compression function underlying the hash function, and give good bounds in the multi-user setting.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/140850393 (1).pdf`
- `downloads/140850393.pdf`
