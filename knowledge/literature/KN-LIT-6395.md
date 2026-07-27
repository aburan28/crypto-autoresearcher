---
id: KN-LIT-6395
type: literature
title: "Second Preimages on n-bit Hash Functions for Much Less than 2n Work"
authors:
  - "John Kelsey"
  - "Bruce Schneier"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We expand a previous result of Dean [Dea99] to provide a second preimage attack on all n-bit iterated hash functions with DamgårdMerkle strengthening and n-bit intermediate states, allowing a second preimage to be found for a 2k -message-block message with about k × 2n/2+1 +2n−k+1 work. Using RIPEMD-160 as an example, our attack can find a second preimage for a 260 byte message in about 2106 work, rather than the previously expected 2160 work.

## Key claims (as reported)
- We also provide slightly cheaper ways to find multicollisions than the method of Joux [Jou04].
- Both of these results are based on expandable messages–patterns for producing messages of varying length, which all collide on the intermediate hash result immediately after processing the message.
- We provide an algorithm for finding expandable messages for any n-bit hash function built using the Damgård-Merkle construction, which requires only a small multiple of the work done to find a single collision in the hash function.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/34940474 (1).pdf`
- `downloads/34940474 (2).pdf`
- `downloads/34940474 (3).pdf`
- `downloads/34940474.pdf`
