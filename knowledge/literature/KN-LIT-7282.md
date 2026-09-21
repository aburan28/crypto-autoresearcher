---
id: KN-LIT-7282
type: literature
title: "TweetNaCl: A crypto library in 100 tweets"
authors:
  - "Daniel J. Bernstein"
  - "Bernard van Gastel"
  - "Wesley Janssen"
  - "Tanja Lange"
  - "Peter Schwabe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, hyperelliptic, implementation, pairing, quantum, rsa, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper introduces TweetNaCl, a compact reimplementation of the NaCl library, including all 25 of the NaCl functions used by applications. TweetNaCl is published on Twitter and fits into just 100 tweets; the tweets are available from anywhere, any time, in an unsuspicious way.

## Key claims (as reported)
- Distribution via other social media, or even printed on a sheet of A4 paper, is also easily possible.
- TweetNaCl is human-readable C code; it is the smallest readable implementation of a high-security cryptographic library.
- TweetNaCl is the first cryptographic library that allows correct functionality to be verified by auditors with reasonable effort, making it suitable for inclusion into the trusted code base of a secure computer system.
- This paper uses two examples of formally verified correctness properties to illustrate the impact of TweetNaCl’s conciseness upon auditability.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/tweetnacl-20140917.pdf`
