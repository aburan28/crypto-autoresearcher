---
id: KN-LIT-654
type: literature
title: "“S-Box” Implementation of AES is NOT side channel resistant"
authors:
  - "C Ashokkumar"
  - "Bholanath Roy"
  - "M Bhargav Sri Venkatesh"
  - "Bernard L"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/1002"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/1002"
tags: [implementation, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Several successful cache-based attacks have provided strong impetus for developing side channel resistant software implementations of AES. One of the best-known countermeasures - use of a “minimalist” 256-byte look-up table - has been employed in the latest (assembly language) versions.

## Key claims (as reported)
- Software and hardware prefetching and out-of-order execution in modern processors have served to further shrink the attack surface.
- Despite these odds, we devise and implement two strategies to retrieve the complete AES key.
- The first uses adaptively chosen plaintext and random plaintext in a 2-round attack.
- The second strategy employs only about 50 blocks of random plaintext in a novel single round attack.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2018-1002.pdf`
