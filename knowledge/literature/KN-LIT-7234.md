---
id: KN-LIT-7234
type: literature
title: "Towards Tight Security Bounds for OMAC, XCBC and TMAC"
authors:
  - "Soumya Chattopadhyay"
  - "Ashwin Jha"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
OMAC — a single-keyed variant of CBC-MAC by Iwata and Kurosawa — is a widely used and standardized (NIST FIPS 800-38B, ISO/IEC 29167-10:2017) message authentication code (MAC) algorithm. The best security bound for OMAC is due to Nandi who proved that OMAC’s pseudorandom function (PRF) advantage is upper bounded by O(q 2 `/2n ), where n, q, and `, denote the block size of the underlying block cipher, the number of queries, and the maximum permissible query length (in terms of n-bit blocks), respectively.

## Key claims (as reported)
- In contrast, there is no attack with matching lower bound.
- Indeed, the best known attack on OMAC is the folklore birthday attack achieving a lower bound of Ω(q 2 /2n ).
- In this work, we close this gap for a large range of message lengths.
- Specifically, we show that OMAC’s PRF security is upper bounded by O(q 2 /2n + q`2 /2n ).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910185 (1).pdf`
- `downloads/137910185.pdf`
