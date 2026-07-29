---
id: KN-LIT-6177
type: literature
title: "Recovering Secret Keys from Weak Side Channel Traces of Differing Lengths"
authors:
  - "Colin D. Walter"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Secret key recovery from weak side channel leakage is always a challenge in the presence of standard counter-measures. The use of randomised exponent recodings in RSA or ECC means that, over multiple re-uses of a key, operations which correspond to a given key bit are not aligned in the traces.

## Key claims (as reported)
- This enhances the difficulties because traces cannot be averaged to improve the signal-to-noise ratio.
- The situation can be described using a hidden Markov model (HMM) but the standard solution is computationally infeasible when many traces have to be processed.
- Previous work has not provided a satisfactory way out.
- Here, instead of ad hoc sequential processing of complete traces, trace prefixes are combined naturally in parallel.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/51540210 (1).pdf`
- `downloads/51540210 (2).pdf`
- `downloads/51540210 (3).pdf`
- `downloads/51540210.pdf`
