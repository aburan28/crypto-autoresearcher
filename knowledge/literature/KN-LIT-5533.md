---
id: KN-LIT-5533
type: literature
title: "On the Possibility of a"
authors:
  - "Keegan Ryan"
  - "Adam Suhl"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, finite-field, lattice, pairing, protocol, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study both the implications and potential impact of backdoored parameters for two RSA-based pseudorandom number generators: the ISO-standardized Micali-Schnorr generator and a closely related design, the RSA PRG. We observe, contrary to common understanding, that the security of the Micali-Schnorr PRG is not tightly bound to the difficulty of inverting RSA.

## Key claims (as reported)
- We show that the MicaliSchnorr construction remains secure even if one replaces RSA with a publicly evaluatable PRG, or a function modeled as an efficiently invertible random permutation.
- This implies that any cryptographic backdoor must somehow exploit the algebraic structure of RSA, rather than an attacker’s ability to invert RSA or the presence of secret keys.
- We exhibit two such backdoors in related constructions: a family of exploitable parameters for the RSA PRG, and a second vulnerable construction for a finite-field variant of Micali-Schnorr.
- We also observe that the parameters allowed by the ISO standard are incompletely specified, and allow insecure choices of exponent.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602062 (1).pdf`
- `downloads/14602062.pdf`
