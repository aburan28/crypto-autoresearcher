---
id: KN-LIT-7596
type: literature
title: "Advanced cryptography from lattice isomorphism — new constructions of IBE and FHE"
authors:
  - "Huck Bennett"
  - "Zhengnan Lai"
  - "Noah Stephens-Davidowitz"
year: 2026
venue: 'IACR ePrint 2026/465 (PUBLIC-KEY CRYPTOGRAPHY)'
identifiers:
  eprint: iacr:2026/465
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/465
tags: [lattice-isomorphism-problem, lip, ibe, fhe, gpv, gsw, assumption-load, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

## Contribution
Translates the standard LWE-based construction machinery — Gentry–Peikert–Vaikuntanathan
(STOC 2008) for IBE and Gentry–Sahai–Waters (CRYPTO 2013) for leveled FHE — into the
lattice-isomorphism setting of Ducas–van Woerden (Eurocrypt 2022), with security under a
suitable version of the Lattice Isomorphism Problem.

## Key claims (as reported)
- Constructions of **identity-based encryption** and **leveled fully homomorphic
  encryption** whose security reduces to a version of LIP.
- The techniques are described as "quite general and modular," working with any
  sufficiently "nice" lattice; the authors expect further applications.

## Relevance to this program
Adjacent, and recorded chiefly for the timing. LIP is the hardness assumption underneath
HAWK, and this entry lands in the same window as [[KN-LIT-7592]], which halves HAWK's
effective key strength by exploiting a Galois involution specific to power-of-two
cyclotomic fields. The two together sharpen a question this program cares about
generically: **how much weight a single structured hardness assumption is carrying**.
[[KN-LIT-7592]] is explicit that its attack does not generalize to LIP as such — it
attacks the *module*-LIP instance HAWK chose, and conductors with cyclic `(Z/m)^×` evade
it — so this paper's constructions are not implicated by it. But the pairing is a clean
illustration of assumption load growing faster than assumption scrutiny, which is the
generic pattern behind `KN-TECH-035`-style full-cost honesty.

**No ECDLP bearing.** Recorded as adjacent literature only; no technique here has a known
route to elliptic-curve discrete logarithms.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved on
2026-07-28 (hence `confidence: reported`). ePrint metadata: last updated 2026-07-28,
category PUBLIC-KEY CRYPTOGRAPHY.

NOT verified here: the IBE and FHE constructions, the precise LIP variant assumed and how
it relates to the variants underpinning HAWK, the security proofs, and the claimed
modularity. Whether the assumption used here is affected in any way by [[KN-LIT-7592]] has
**not** been checked and is not claimed either way.
