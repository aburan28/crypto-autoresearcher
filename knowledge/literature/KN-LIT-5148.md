---
id: KN-LIT-5148
type: literature
title: "New Security Proofs for the 3GPP"
authors:
  - "Integrity Algorithms"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper analyses the 3GPP confidentiality and integrity schemes adopted by Universal Mobile Telecommunication System, an emerging standard for third generation wireless communications. The schemes, known as f 8 and f 9, are based on the block cipher KASUMI.

## Key claims (as reported)
- Although previous works claim security proofs for f 8 and f 90 , where f 90 is a generalized versions of f 9, it was recently shown that these proofs are incorrect.
- Moreover, Iwata and Kurosawa (2003) showed that it is impossible to prove f 8 and f 90 secure under the standard PRP assumption on the underlying block cipher.
- We address this issue here, showing that it is possible to prove f 80 and f 90 secure if we make the assumption that the underlying block cipher is a secure PRP-RKA against a certain class of related-key attacks; here f 80 is a generalized version of f 8.
- Our results clarify the assumptions necessary in order for f 8 and f 9 to be secure and, since no related-key attacks are known against the full eight rounds of KASUMI, lead us to believe that the confidentiality and integrity mechanisms used in real 3GPP applications are secure.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/30170427 (1).pdf`
- `downloads/30170427 (2).pdf`
- `downloads/30170427.pdf`
