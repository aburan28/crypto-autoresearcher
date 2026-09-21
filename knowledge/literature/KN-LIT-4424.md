---
id: KN-LIT-4424
type: literature
title: "Improved OT Extension for Transferring Short Secrets"
authors:
  - "Vladimir Kolesnikov"
  - "Ranjit Kumaresan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, mov-fr, mpc, pairing, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose an optimization and generalization of OT extension of Ishai et al. of Crypto 2003. For computational security parameter k, our OT extension for short secrets offers O(log k) factor performance improvement in communication and computation, compared to prior work.

## Key claims (as reported)
- In concrete terms, for today’s security parameters, this means approx. factor 2-3 improvement.
- This results in corresponding improvements in applications relying on such OT.
- In particular, for two-party semi-honest SFE, this results in O(log k) factor improvement in communication over state of the art Yao Garbled Circuit, and has the same asymptotic complexity as the recent multi-round construction of Kolesnikov and Kumaresan of SCN 2012.
- For multi-party semi-honest SFE, where their construction is inapplicable, our construction implies O(log k) factor communication and computation improvement over best previous constructions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420329 (1).pdf`
- `downloads/80420329 (2).pdf`
- `downloads/80420329 (3).pdf`
- `downloads/80420329.pdf`
