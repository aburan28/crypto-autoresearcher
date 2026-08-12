---
id: KN-LIT-4245
type: literature
title: "Horizontal Side-Channel Attacks and Countermeasures on the ISW Masking Scheme"
authors:
  - "Alberto Battistello"
  - "Jean-Sébastien Coron"
  - "Emmanuel Prouff"
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
A common countermeasure against side-channel attacks consists in using the masking scheme originally introduced by Ishai, Sahai and Wagner (ISW) at Crypto 2003, and further generalized by Rivain and Prouff at CHES 2010. The countermeasure is provably secure in the probing model, and it was showed by Duc, Dziembowski and Faust at Eurocrypt 2014 that the proof can be extended to the more realistic noisy leakage model.

## Key claims (as reported)
- However the extension only applies if the leakage noise σ increases at least linearly with the masking order n, which is not necessarily possible in practice.
- In this paper we investigate the security of an implementation when the previous condition is not satisfied, for example when the masking order n increases for a constant noise σ.
- We exhibit two (template) horizontal side-channel attacks against the Rivain-Prouff’s secure multiplication scheme and we analyze their efficiency thanks to several simulations and experiments.
- Eventually, we describe a variant of Rivain-Prouff’s multiplication that is still provably secure in the original ISW model, and also heuristically secure against our new attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130173 (1).pdf`
- `downloads/98130173.pdf`
