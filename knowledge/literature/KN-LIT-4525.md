---
id: KN-LIT-4525
type: literature
title: "Insuperability of the Standard Versus Ideal Model Gap for Tweakable Blockcipher Security"
authors:
  - "Bart Mennink"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security, survey, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Two types of tweakable blockciphers based on classical blockciphers have been presented over the last years: non-tweak-rekeyable and tweak-rekeyable, depending on whether the tweak may influence the key input to the underlying blockcipher. In the former direction, the best possible security is conjectured to be 2σn/(σ+1) , where n is the size of the blockcipher and σ is the number of blockcipher calls.

## Key claims (as reported)
- In the latter direction, Mennink and Wang et al. presented optimally secure schemes, but only in the ideal cipher model.
- We investigate the possibility to construct a tweak-rekeyable cipher that achieves optimal security in the standard cipher model.
- As a first step, we note that all standard-model security results in literature implicitly rely on a generic standard-to-ideal transformation, that replaces all keyed blockcipher calls by random secret permutations, at the cost of the security of the blockcipher.
- Then, we prove that if this proof technique is adopted, tweak-rekeying will not help in achieving optimal security: if 2σn/(σ+1) is the best one can get without tweak-rekeying, optimal 2n provable security with tweak-rekeying is impossible.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401137 (1).pdf`
- `downloads/10401137.pdf`
