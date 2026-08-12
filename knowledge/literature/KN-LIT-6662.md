---
id: KN-LIT-6662
type: literature
title: "Simple Refreshing in the Noisy Leakage Model"
authors:
  - "Stefan Dziembowski"
  - "Sebastian Faust"
  - "Karol Żebrowski"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [binary-field, finite-field, mpc, pairing, provable-security, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Masking schemes are a prominent countermeasure against power analysis and work by concealing the values that are produced during the computation through randomness. The randomness is typically injected into the masked algorithm using a so-called refreshing scheme, which is placed after each masked operation, and hence is one of the main bottlenecks for designing efficient masking schemes.

## Key claims (as reported)
- The main contribution of our work is to investigate the security of a very simple and efficient refreshing scheme and prove its security in the noisy leakage model (EUROCRYPT’13).
- Compared to earlier constructions our refreshing is significantly more efficient and uses only n random values and < 2n operations, where n is the security parameter.
- In addition we show how our refreshing can be used in more complex masked computation in the presence of noisy leakage.
- Our results are established using a new methodology for analyzing masking schemes in the noisy leakage model, which may be of independent interest.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210289 (1).pdf`
- `downloads/119210289.pdf`
