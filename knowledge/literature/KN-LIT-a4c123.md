---
id: KN-LIT-a4c123
type: literature
title: "Endomorphism rings of elliptic curves over finite fields"
authors:
  - "David Russell Kohel"
year: 1996
venue: "PhD thesis, University of California, Berkeley (advisor Hendrik W. Lenstra, Jr.), December 1996; ProQuest 9723065"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://www.i2m.univ-amu.fr/perso/david.kohel/pub/thesis.pdf"
tags: [endomorphism-ring, conductor, isogeny, volcano, ordinary, finite-field, GRH, kernel-polynomial, isogeny-computation]
confidence: reported
citation_verified: metadata
added: "2026-10-12"
superseded_by: null
---

## Contribution
The thesis that founded the computation of End(E) for ordinary curves over
finite fields. For an ordinary curve E/F_q with Frobenius π, End(E) is an
order O with Z[π] ⊆ O ⊆ O_K, so it is determined by its conductor f_E,
which divides the conductor f_π of Z[π]. Kohel shows that the ℓ-adic
valuation v_ℓ(f_E) is read off the structure of the rational ℓ-isogeny
graph around E (the "depth" that Fouquet–Morain later named the volcano
level, KN-LIT-96f1bb): descending ℓ-isogenies multiply the conductor by ℓ,
ascending ones divide it, and the lengths of non-backtracking walks to the
floor give the level. From this he derives a deterministic algorithm that
computes the isomorphism type of End(E), with running time O(q^{1/3+ε})
under a generalised Riemann hypothesis, the first such algorithm. The thesis
also gives the kernel-polynomial formulas for computing an isogeny from its
kernel ("Kohel's formulas", the odd and even cases) that implementations
use alongside Vélu's.

## Key claims (as reported)
- Theorem 1 (thesis): a deterministic algorithm computes End(E) for an
  elliptic curve over a field of q elements; under a generalised Riemann
  hypothesis it runs in time O(q^{1/3+ε}).
- The ℓ-isogeny graph of an ordinary class is the union of "ℓ-volcanoes"
  (Kohel's own term was different; the structure is his), with the level of
  a vertex equal to v_ℓ of the conductor of its endomorphism ring.
- Explicit formulas for the isogeny with a given kernel polynomial.

## Relevance to this program
Every per-prime level label in the isogeny-stratified lane
(RQ-VOLC-f6253b, RQ-ICINV-475b5e; `research/isogeny_stratified_ml_blueprint_triage_20261010/`)
is "Kohel's level"; `crypto/isogeny_algos/src/path/endo.rs` implements the
algorithm for F_p and `isogeny_algos/src/kernel/kohel.rs` the kernel
formulas; `ml-cryptanalysis/csd/endo.py` computes the same conductor by a
Frobenius-scalar test on E[ℓ^k]. Bisson–Sutherland (KN-LIT-251) replace the
O(q^{1/3}) bound by a subexponential one.

## Not verified here
Metadata (author, institution, year, advisor, hosted full text) verified on
2026-10-12 against the author's CV, the Mathematics Genealogy Project and
the ProQuest catalogue record; the thesis body was not read in full here.
Theorem statement relayed from the thesis title page and from
Bisson–Sutherland's summary.
