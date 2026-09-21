---
id: KN-LIT-3253
type: literature
title: "Cryptanalysis of Round-Reduced LED"
authors:
  - "Ivica Nikolić"
  - "Lei Wang"
  - "Shuang Wu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we present known-plaintext single-key and chosenkey attacks on round-reduced LED-64 and LED-128. We show that with an application of the recently proposed slidex attacks [5], one immediately improves the complexity of the previous single-key 4-step attack on LED-128.

## Key claims (as reported)
- Further, we explore the possibility of multicollisions and show single-key attacks on 6 steps of LED-128.
- A generalization of our multicollision attack leads to the statement that no 6-round cipher with two subkeys that alternate, or 2-round cipher with linearly dependent subkeys, is secure in the single-key model.
- Next, we exploit the possibility of finding pairs of inputs that follow a certain differential rather than a differential characteristic, and obtain chosen-key differential distinguishers for 5-step LED-64, as well as 8-step and 9-step LED-128.
- We provide examples of inputs that follow the 8-step differential, i.e. we are able to practically confirm our results on 2/3 of the steps of LED-128.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84240105 (1).pdf`
- `downloads/84240105 (2).pdf`
- `downloads/84240105 (3).pdf`
- `downloads/84240105.pdf`
