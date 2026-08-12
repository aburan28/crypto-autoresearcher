---
id: KN-LIT-3168
type: literature
title: "Correcting Errors in RSA Private Keys"
authors:
  - "Wilko Henecka"
  - "Alexander May"
  - "Alexander Meurer"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, factoring, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Let pk = (N , e) be an RSA public key with corresponding secret key sk = (p, q, d , dp , dq , qp−1 ). Assume that we obtain partial error-free information of sk, e.g., assume that we obtain half of the most significant bits of p.

## Key claims (as reported)
- Then there are well-known algorithms to recover the full secret key.
- As opposed to these algorithms that allow for correcting erasures of the key sk, we present for the first time a heuristic probabilistic algorithm that is capable of correcting errors in sk provided that e we e is small.
- That is, on input of a full but error-prone secret key sk reconstruct the original sk by correcting the faults.
- More precisely, consider an error rate of δ ∈ [0, 12 ), where we flip each bit e Our Las-Vegas in sk with probability δ resulting in an erroneous key sk. e type algorithm allows to recover sk from sk in expected time polynomial in log N with success probability close to 1, provided that δ < 0.237.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/62230350 (1).pdf`
- `downloads/62230350 (2).pdf`
- `downloads/62230350 (3).pdf`
- `downloads/62230350.pdf`
