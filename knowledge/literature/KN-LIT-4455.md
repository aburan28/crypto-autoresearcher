---
id: KN-LIT-4455
type: literature
title: "Improving Modular Inversion in RNS using the Plus-Minus Method"
authors:
  - "Karim Bigou"
  - "Arnaud Tisserand"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, implementation, pairing, provable-security, rsa, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The paper describes a new RNS modular inversion algorithm based on the extended Euclidean algorithm and the plus-minus trick. In our algorithm, comparisons over large RNS values are replaced by cheap computations modulo 4.

## Key claims (as reported)
- Comparisons to an RNS version based on Fermat’s little theorem were carried out.
- The number of elementary modular operations is significantly reduced: a factor 12 to 26 for multiplications and 6 to 21 for additions.
- Virtex 5 FPGAs implementations show that for a similar area, our plus-minus RNS modular inversion is 6 to 10 times faster.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80860177 (1).pdf`
- `downloads/80860177 (2).pdf`
- `downloads/80860177 (3).pdf`
- `downloads/80860177.pdf`
