---
id: KN-LIT-3055
type: literature
title: "Computing Individual Discrete Logarithms Faster in GF(pn ) with the NFS-DL Algorithm ?"
authors:
  - "Aurore Guillevic"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, extension-field, factoring, finite-field, number-theory, pairing, prime-field, protocol]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Number Field Sieve (NFS) algorithm is the best known method to compute discrete logarithms (DL) in finite fields Fpn , with p medium to large and n ≥ 1 small. This algorithm comprises four steps: polynomial selection, relation collection, linear algebra and finally, individual logarithm computation.

## Key claims (as reported)
- The first step outputs two polynomials defining two number fields, and a map from the polynomial ring over the integers modulo each of these polynomials to Fpn .
- After the relation collection and linear algebra phases, the (virtual) logarithm of a subset of elements in each number field is known.
- Given the target element in Fpn , the fourth step computes a preimage in one number field.
- If one can write the target preimage as a product of elements of known (virtual) logarithm, then one can deduce the discrete logarithm of the target.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520141 (1).pdf`
- `downloads/94520141.pdf`
