---
id: KN-LIT-7150
type: literature
title: "Tightly Secure IBE under Constant-size Master Public Key"
authors:
  - "Jie Chen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Chen and Wee [CRYPTO, 2013] proposed the first almost tightly and adaptively secure IBE in the standard model and left two open problems which called for a tightly secure IBE with (1) constantsize master public key and/or (2) constant security loss. In this paper, we propose an IBE scheme with constant-size master public key and tighter security reduction.

## Key claims (as reported)
- This (partially) solves Chen and Wee’s first open problem and makes progress on the second one.
- Technically, our IBE scheme is built based on Wee’s petit IBE scheme [TCC, 2016] in the composite-order bilinear group whose order is product of four primes.
- The sizes of master public key, ciphertexts, and secret keys are not only constant but also nearly optimal as Wee’s petit IBE.
- We can prove its adaptive security in the multi-instance, multi-ciphertext setting [PKC, 2015] based on the decisional subgroup assumption and a subgroup variant of DBDH assumption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/101740197 (1).pdf`
- `downloads/101740197 (2).pdf`
- `downloads/101740197 (3).pdf`
- `downloads/101740197 (4).pdf`
- `downloads/101740197.pdf`
