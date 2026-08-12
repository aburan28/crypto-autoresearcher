---
id: KN-LIT-5342
type: literature
title: "On Error Correction in the Exponent Chris Peikert"
authors:
  - "MIT CSAIL"
  - "Vassar St"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, mpc]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Given a corrupted word w = (w1 , . . . , wn ) from a ReedSolomon code of distance d, there are many ways to efficiently find and correct its errors. But what if we are instead given (g w1 , . . . , g wn ) where g generates some large cyclic group — can the errors still be corrected efficiently?

## Key claims (as reported)
- This problem is called error correction in the exponent, and though it arises naturally in many areas of cryptography, it has received little attention.
- We first show that unique decoding and list decoding in the exponent are no harder than the computational Diffie-Hellman (CDH) problem in the same group.
- The remainder of our results are negative: – Under mild assumptions on the parameters, we show that boundeddistance decoding in the exponent, under e = d − k1− errors for any  > 0, is as hard as the discrete logarithm problem in the same group. – For generic algorithms (as defined by Shoup, Eurocrypt 1997) that treat the group as a “black-box,” we show lower bounds for decoding that exactly match known algorithms.
- Our generic lower bounds also extend to decisional variants of the decoding problem, and to groups in which the decisional Diffie-Hellman (DDH) problem is easy.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/38760167 (1).pdf`
- `downloads/38760167 (2).pdf`
- `downloads/38760167 (3).pdf`
- `downloads/38760167.pdf`
