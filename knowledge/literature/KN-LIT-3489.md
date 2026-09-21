---
id: KN-LIT-3489
type: literature
title: "Dummy Shuffling against Algebraic Attacks in White-box Implementations?"
authors:
  - "Alex Biryukov"
  - "Aleksei Udovenko"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, provable-security, quantum, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At CHES 2016, Bos et al. showed that most of existing whitebox implementations are easily broken by standard side-channel attacks. A natural idea to apply the well-developed side-channel countermeasure - linear masking schemes - leaves implementations vulnerable to linear algebraic attacks which exploit absence of noise in the white-box setting and are applicable for any order of linear masking.

## Key claims (as reported)
- At ASIACRYPT 2018, Biryukov and Udovenko proposed a security model (BU-model for short) for protection against linear algebraic attacks and a new quadratic masking scheme which is provably secure in this model.
- However, countermeasures against higher-degree attacks were left as an open problem.
- In this work, we study the effectiveness of another well-known sidechannel countermeasure - shuffling - against linear and higher-degree algebraic attacks in the white-box setting.
- First, we extend the classic shuffling to include dummy computation slots and show that this is a crucial component for protecting against the algebraic attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/126960215 (1).pdf`
- `downloads/126960215.pdf`
