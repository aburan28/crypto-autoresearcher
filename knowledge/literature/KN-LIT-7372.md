---
id: KN-LIT-7372
type: literature
title: "Unifying Leakage Models on a Rényi Day"
authors:
  - "Thomas Prest"
  - "Dahmun Goudarzi"
  - "Ange Martinelli"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mpc, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the last decade, several works have focused on finding the best way to model the leakage in order to obtain provably secure implementations. One of the most realistic models is the noisy leakage model, introduced in [PR13,DDF14] together with secure constructions.

## Key claims (as reported)
- These works suffer from various limitations, in particular the use of ideal leakfree gates in [PR13] and an important loss (in the size of the field) in the reduction in [DDF14].
- In this work, we provide new strategies to prove the security of masked implementations and start by unifying the different noisiness metrics used in prior works by relating all of them to a standard notion in information theory: the pointwise mutual information.
- Based on this new interpretation, we define two new natural metrics and analyze the security of known compilers with respect to these metrics.
- In particular, we prove (1) a tighter bound for reducing the noisy leakage models to the probing model using our first new metric, (2) better bounds for amplificationbased security proofs using the second metric.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/116940277 (1).pdf`
- `downloads/116940277.pdf`
