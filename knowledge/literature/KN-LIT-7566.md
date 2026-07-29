---
id: KN-LIT-7566
type: literature
title: Provable Recovery of RSA Private Exponents below N^{11/42-epsilon}
authors: [Gao Yiming, Hu Honggang]
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1478'
identifiers:
  eprint: iacr:2026/1478
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1478
tags: [rsa, small-private-exponent, wiener, boneh-durfee, coppersmith, small-roots, lattice, provable, heuristic-removal, cryptanalysis, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
Gives the first **fully provable** improvement past Wiener's classical `d < N^{1/4}`
bound for small-private-exponent RSA: for every fixed `epsilon > 0`, balanced RSA with
`e = Theta(N)` can be factored deterministically in polynomial time whenever
`d <= N^{11/42 - epsilon}`. Note `11/42 ~ 0.2619 > 1/4 = 0.25`.

## Key claims (as reported)
- Wiener's continued-fraction attack gives the classical **provable** bound
  `d < N^{1/4}`.
- Boneh-Durfee reached exponent `1 - sqrt(2)/2 ~ 0.2929`, but that argument **relies on
  a heuristic independence assumption** (the standard Coppersmith-style assumption that
  the polynomials extracted from the reduced lattice basis are algebraically
  independent).
- This paper proves recovery for `d <= N^{11/42 - epsilon}`, deterministically, in
  polynomial time, for balanced RSA with `e = Theta(N)`.
- The result is therefore *below* Boneh-Durfee's heuristic `0.2929` but *above*
  Wiener's provable `0.25` — it narrows the provable/heuristic gap rather than closing
  it.

## Relevance to this program
`adjacent` — RSA, not ECDLP — but recorded for one specific methodological reason the
program cares about: **it is a case study in converting a heuristic lattice bound into
a provable one, and in how much exponent that conversion costs.**

`KN-TECH-015` (Coppersmith small-root lattice methods) is in the corpus because the
program has considered windowed / small-root attacks on summation-polynomial systems,
and `KN-OPEN-011` / `KN-OPEN-018` ask whether lattice machinery bears on the plain
ECDLP at all. The relevant transferable observation is not the RSA bound itself but
the **gap structure**: the heuristic-independence assumption that Coppersmith-style
attacks routinely invoke is worth `0.2929 - 0.2619 ~ 0.031` of exponent here, and
removing it took a dedicated paper. Any program proposal that reaches for a
Coppersmith construction should expect to inherit that same assumption and should
state whether its claim is provable or heuristic — the program's claim-tier discipline
(`docs/claims-and-verification.md`) makes exactly this distinction.

Forecloses nothing on the ECDLP line and supplies no relation-harvesting mechanism.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved
from eprint.iacr.org on 2026-07-26 (hence `confidence: reported`). ePrint history:
received 2026-07-20, approved 2026-07-23. Not peer-reviewed as of this entry; no DOI.

NOT verified here: the proof, the exact restriction `e = Theta(N)` and how much of the
balanced-RSA parameter space it covers, whether `11/42` is tight for the technique,
and the claim that this is the *first* fully provable improvement beyond `1/4` (a
priority claim, not independently checked). Wiener and Boneh-Durfee are cited from
this paper's abstract, not from their own sources; neither is currently in this
corpus.
