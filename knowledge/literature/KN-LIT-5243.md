---
id: KN-LIT-5243
type: literature
title: "Nostradamus goes Quantum"
authors:
  - "Barbara Jiabao Benedikt ( )"
  - "Marc Fischlin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In the Nostradamus attack, introduced by Kelsey and Kohno (Eurocrypt 2006), the adversary has to commit to a hash value y of an iterated hash function H such that, when later given a message prefix P , the adversary is able to find a suitable “suffix explanation” S with H(P kS) = y. Kelsey and Kohno show a herding attack with 22n/3 evaluations of the compression function of H (with n bits output and state), locating the attack between preimage attacks and collision search in terms of complexity.

## Key claims (as reported)
- Here we investigate the security of Nostradamus attacks for quantum adversaries.
- We present a quantum herding algo√ rithm for the Nostradamus problem making approximately 3 n · 23n/7 compression function evaluations, significantly improving over the classical bound.
- We also prove that quantum herding attacks cannot do better than 23n/7 evaluations for random compression functions, showing that our algorithm is (essentially) optimal.
- We also discuss a slightly less tight bound of roughly 23n/7−s for general Nostradamus attacks against random compression functions, where s is the maximal block length of the adversarially chosen suffix S.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910157 (1).pdf`
- `downloads/137910157.pdf`
