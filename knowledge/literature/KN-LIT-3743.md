---
id: KN-LIT-3743
type: literature
title: "Extended Tower Number Field Sieve: A New Complexity for the Medium Prime Case?"
authors:
  - "Taechan Kim"
  - "Razvan Barbulescu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, dlp, factoring, finite-field, number-theory, pairing, prime-field, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new variant of the number field sieve algorithm for discrete logarithms in Fpn called exTNFS. The most important modification is done in the polynomial selection step, which determines the cost of the whole algorithm: if one knows how to select good polynomials to tackle discrete logarithms in Fpκ , exTNFS allows to use this method when tackling Fpηκ whenever gcd(η, κ) = 1.

## Key claims (as reported)
- This simple fact has consequences on the asymptotic complexity of NFSp in the medium prime pcase, where the complexity is reduced from LQ (1/3, 3 96/9) to LQ (1/3, 3 48/9), Q = pn , respectively from LQ (1/3, 2.15) to LQ (1/3, 1.71) if multiple number fields are used.
- On the practical side, exTNFS can be used when n = 6 and n = 12 and this requires to updating the keysizes used for the associated pairing-based cryptosystems.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98140523 (1).pdf`
- `downloads/98140523.pdf`
