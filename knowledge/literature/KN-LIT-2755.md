---
id: KN-LIT-2755
type: literature
title: "Blockcipher-based MACs: Beyond the Birthday Bound without Message Length Yusuke Naito"
authors:
  - "Mitsubishi Electric Corporation"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present blockcipher-based MACs (Message Authentication Codes) that have beyond the birthday bound security without message length in the sense of PRF (Pseudo-Random Function) security. Achieving such security is important in constructing MACs using blockciphers with short block sizes (e.g., 64 bit).

## Key claims (as reported)
- (FSE 2016) proposed LightMAC, the first blockcipher-based MAC with such security and a variant of PMAC, where for each n-bit blockcipher call, an m-bit counter and an (n − m)-bit message block are input.
- By the presence of counters, LightMAC becomes a secure PRF up to O(2n/2 ) tagging queries.
- Iwata and Minematsu (TOSC 2016, Issue 1) proposed Ft , a keyed hash function-based MAC, where a message is input to t keyed hash functions (the hash function is performed t times) and the t outputs are input to the xor of t keyed blockciphers.
- Using the LightMAC’s hash function, Ft becomes a secure PRF up to O(2tn/(t+1) ) tagging queries.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/106240326 (1).pdf`
- `downloads/106240326.pdf`
