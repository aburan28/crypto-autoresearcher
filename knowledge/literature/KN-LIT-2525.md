---
id: KN-LIT-2525
type: literature
title: "Analysis of RMAC"
authors:
  - "Lars R. Knudsen"
  - "Tadayoshi Kohno"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper the newly proposed RMAC system is analysed. The scheme allows a (traditional MAC) attack some control over one of two keys of the underlying block cipher and makes it possible to mount several related-key attacks on RMAC.

## Key claims (as reported)
- First, an efficient attack on RMAC when used with triple-DES is presented, which rely also on other findings in the proposed draft standard.
- Second, a generic attack on RMAC is presented which can be used to find one of the two keys in the system faster than by an exhaustive search.
- Third, related-key attacks on RMAC in a multi-user setting are presented.
- In addition to beating the claimed security bounds in NIST’s RMAC proposal, this work suggests that, as a general principle, one may wish to avoid designing modes of operation that use related keys.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/28870190 (1).pdf`
- `downloads/28870190 (2).pdf`
- `downloads/28870190.pdf`
