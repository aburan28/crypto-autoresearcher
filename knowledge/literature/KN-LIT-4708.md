---
id: KN-LIT-4708
type: literature
title: "Learning with Rounding, Revisited"
authors:
  - "New Reduction"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, lattice, mpc, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The learning with rounding (LWR) problem, introduced by Banerjee, Peikert and Rosen at EUROCRYPT ’12, is a variant of learning with errors (LWE), where one replaces random errors with deterministic rounding. The LWR problem was shown to be as hard as LWE for a setting of parameters where the modulus and modulus-to-error ratio are super-polynomial.

## Key claims (as reported)
- In this work we resolve the main open problem and give a new reduction that works for a larger range of parameters, allowing for a polynomial modulus and modulus-to-error ratio.
- In particular, a smaller modulus gives us greater efficiency, and a smaller modulus-to-error ratio gives us greater security, which now follows from the worst-case hardness of GapSVP with polynomial (rather than superpolynomial) approximation factors.
- As a tool in the reduction, we show that there is a “lossy mode” for the LWR problem, in which LWR samples only reveal partial information about the secret.
- This property gives us several interesting new applications, including a proof that LWR remains secure with weakly random secrets of sufficient min-entropy, and very simple constructions of deterministic encryption, lossy trapdoor functions and reusable extractors.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/80420212 (1).pdf`
- `downloads/80420212 (2).pdf`
- `downloads/80420212 (3).pdf`
- `downloads/80420212.pdf`
