---
id: KN-LIT-2911
type: literature
title: "Circular Security Is Complete for KDM Security"
authors:
  - "Fuyuki Kitagawa"
  - "Takahiro Matsuda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mpc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Circular security is the most elementary form of key-dependent message (KDM) security, which allows us to securely encrypt only a copy of secret key bits. In this work, we show that circular security is complete for KDM security in the sense that an encryption scheme satisfying this security notion can be transformed into one satisfying KDM security with respect to all functions computable by a-priori bounded-size circuits (bounded-KDM security).

## Key claims (as reported)
- This result holds in the presence of any number of keys and in any of secret-key/public-key and CPA/CCA settings.
- Such a completeness result was previously shown by Applebaum (EUROCRYPT 2011) for KDM security with respect to projection functions (projection-KDM security) that allows us to securely encrypt both a copy and a negation of secret key bits.
- Besides amplifying the strength of KDM security, our transformation in fact can start from an encryption scheme satisfying circular security against CPA attacks and results in one satisfying bounded-KDM security against CCA attacks.
- This result improves the recent result by Kitagawa and Matsuda (TCC 2019) showing a CPA-to-CCA transformation for KDM secure public-key encryption schemes.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491365 (1).pdf`
- `downloads/12491365.pdf`
