---
id: KN-LIT-4828
type: literature
title: "LWE Without Modular Reduction and"
authors:
  - "Pierre-Alain Fouque"
  - "Mehdi Tibouchi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, provable-security, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper is devoted to analyzing the variant of Regev’s learning with errors (LWE) problem in which modular reduction is omitted: namely, the problem (ILWE) of recovering a vector s ∈ Zn given polynomially many samples of the form (a, ha, si + e) ∈ Zn+1 where a and e follow fixed distributions. Unsurprisingly, this problem is much easier than LWE: under mild conditions on the distributions, we show that the problem can be solved efficiently as long as the variance of e is not superpolynomially larger than that of a.

## Key claims (as reported)
- We also provide almost tight bounds on the number of samples needed to recover s.
- Our interest in studying this problem stems from the side-channel attack against the BLISS lattice-based signature scheme described by Espitau et al. at CCS 2017.
- The attack targets a quadratic function of the secret that leaks in the rejection sampling step of BLISS.
- The same part of the algorithm also suffers from a linear leakage, but the authors claimed that this leakage could not be exploited due to signature compression: the linear system arising from it turns out to be noisy, and hence key recovery amounts to solving a high-dimensional problem analogous to LWE, which seemed infeasible.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272231 (1).pdf`
- `downloads/11272231.pdf`
