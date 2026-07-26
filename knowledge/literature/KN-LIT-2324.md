---
id: KN-LIT-2324
type: literature
title: "Adaptive Extractors and their Application to Leakage Resilient Secret Sharing"
authors:
  - "Nishanth Chandran"
  - "Bhavana Kanukurthi"
  - "Sai Lakshmi Bhavana Obbattu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce Adaptive Extractors, which unlike traditional randomness extractors, guarantee security even when an adversary obtains leakage on the source after observing the extractor output. We make a compelling case for the study of such extractors by demonstrating their use in obtaining adaptive leakage in secret sharing schemes.

## Key claims (as reported)
- Specifically, at FOCS 2020, Chattopadhyay, Goodman, Goyal, Kumar, Li, Meka, Zuckerman, built an adaptively secure leakage resilient secret sharing scheme (LRSS) with both rate and leakage rate being O(1/n), where n is the number of parties.
- In this work, we build an adaptively secure LRSS that offers an interesting trade-off between rate, leakage rate, and the total number of shares from which an adversary can obtain leakage.
- As a special case, when considering t-out-of-n secret sharing schemes for threshold t = αn (constant 0 < α < 1), we build a scheme with a constant rate, constant leakage rate, and allow the adversary leakage from all but t − 1 of the shares, while giving her the remaining t − 1 shares completely in the clear.
- (Prior to this, constant rate LRSS scheme tolerating adaptive leakage was unknown for any threshold.) Finally, we show applications of our techniques to both non-malleable secret sharing and secure message transmission.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12826279 (1).pdf`
- `downloads/12826279.pdf`
