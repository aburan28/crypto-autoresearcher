---
id: KN-LIT-2303
type: literature
title: "Accelerating the Delfs–Galbraith algorithm with fast subfield root detection"
authors:
  - "Maria Corte-Real Santos∗"
  - "Craig Costello"
  - "Jia Shi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [elliptic-curve, isogeny, pairing, provable-security, sidh-csidh, supersingular, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a new algorithm for finding an isogeny from a given supersingular elliptic curve E/Fp2 to a subfield elliptic curve E 0 /Fp , which is the bottleneck step of the Delfs–Galbraith algorithm for the general supersingular isogeny problem. Our core ingredient is a novel method of rapidly determining whether a polynomial f ∈ L[X] has any roots in a subfield K ⊂ L, while avoiding expensive root-finding algorithms.

## Key claims (as reported)
- In the special case when f = Φ`,p (X, j) ∈ Fp2 [X], i.e., when f is the `-th modular polynomial evaluated at a supersingular j-invariant, this provides a means of efficiently determining whether there is an `isogeny connecting the corresponding elliptic curve to a subfield curve.
- Together with the traditional Delfs–Galbraith walk, inspecting many `isogenous neighbours in this way allows us to search through a larger proportion of the supersingular set per unit of time.
- Though the asymptotic Õ(p1/2 ) complexity of our improved algorithm remains unchanged from that of the original Delfs–Galbraith algorithm, our theoretical analysis and practical implementation both show a significant reduction in the runtime of the subfield search.
- This sheds new light on the concrete hardness of the general supersingular isogeny problem (i.e. the foundational problem underlying isogeny-based cryptography), and has immediate implications on the bit-security of schemes like B-SIDH and SQISign for which Delfs–Galbraith is the best known classical attack.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/135070137 (1).pdf`
- `downloads/135070137.pdf`
