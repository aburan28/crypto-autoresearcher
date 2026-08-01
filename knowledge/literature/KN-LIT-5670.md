---
id: KN-LIT-5670
type: literature
title: "Optimising Linear Key Recovery Attacks with Affine Walsh Transform Pruning"
authors:
  - "Antonio Flórez-Gutiérrez"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Linear cryptanalysis [25] is one of the main families of keyrecovery attacks on block ciphers. Several publications [16, 19] have drawn attention towards the possibility of reducing their time complexity using the fast Walsh transform.

## Key claims (as reported)
- These previous contributions ignore the structure of the key recovery rounds, which are treated as arbitrary boolean functions.
- In this paper, we optimise the time and memory complexities of these algorithms by exploiting zeroes in the Walsh spectra of these functions using a novel affine pruning technique for the Walsh Transform.
- These new optimisation strategies are then showcased with two application examples: an improved attack on the DES [1] and the first known atttack on 29-round PRESENT-128 [9].

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910250 (1).pdf`
- `downloads/137910250.pdf`
