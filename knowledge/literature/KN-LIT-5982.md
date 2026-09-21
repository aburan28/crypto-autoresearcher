---
id: KN-LIT-5982
type: literature
title: "Provably Weak Instances of Ring-LWE Revisited"
authors:
  - "Wouter Castryck"
  - "Ilia Iliashenko"
  - "Frederik Vercauteren"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, number-theory, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In CRYPTO 2015, Elias, Lauter, Ozman and Stange described an attack on the non-dual decision version of the ring learning with errors problem (RLWE) for two special families of defining polynomials, whose construction depends on the modulus q that is being used. For particularly chosen error parameters, they managed to solve nondual decision RLWE given 20 samples, with a success rate ranging from 10% to 80%.

## Key claims (as reported)
- In this paper we show how to solve the search version for the same families and error parameters, using only 7 samples with a success rate of 100%.
- Moreover our attack works for every modulus q 0 instead of the q that was used to construct the defining polynomial.
- The attack is based on the observation that the RLWE error distribution for these families of polynomials is very skewed in the directions of the polynomial basis.
- For the parameters chosen by Elias et al. the smallest errors are negligible and simple linear algebra suffices to recover the secret.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96650208 (1).pdf`
- `downloads/96650208.pdf`
