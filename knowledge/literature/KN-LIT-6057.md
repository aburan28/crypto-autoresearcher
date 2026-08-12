---
id: KN-LIT-6057
type: literature
title: "QCCA-Secure Generic Key Encapsulation Mechanism with Tighter Security in the Quantum Random Oracle Model"
authors:
  - "Xu Liu"
  - "Mingqiang Wang"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Xagawa and Yamakawa (PQCrypto 2019) proved the transformation SXY can tightly turn DS secure PKEs into IND-qCCA secure KEMs in the quantum random oracle model (QROM). But transformations such as KC, TPunc that turn PKEs with standard security (OW-CPA or IND-CPA) into DS secure PKEs still suffer from quadratic security loss in the QROM.

## Key claims (as reported)
- In this paper, we give a tighter security reduction for the transformation KC that turns OW-CPA secure deterministic PKEs into modified DS secure PKEs in the QROM.
- We use the Measure-Rewind-Measure One-Way to Hiding Lemma recently introduced by Kuchta et al.
- (EUROCRYPT 2020) to avoid the square-root advantage loss.
- Moreover, we extend it to the case that underlying PKEs are not perfectly correct.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110107 (1).pdf`
- `downloads/127110107.pdf`
