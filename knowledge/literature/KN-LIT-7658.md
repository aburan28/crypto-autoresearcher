---
id: KN-LIT-7658
type: literature
title: "The Cokernel Pairing"
authors:
  - "Krijn Reijnders"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/001"
identifiers:
  eprint: "iacr:2026/001"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/001"
tags: [pairing, weil-pairing, tate-pairing, elliptic-curve, torsion-subgroup, cokernel, isogeny, curve-arithmetic, number-theory, sylow, foundational]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: null
---

## Contribution
Defines a **new pairing beyond the Weil and Tate pairings**, filling a structural gap
between them.

- The **Weil** pairing acts on the kernel of `[m]`: `E[m] × E[m] → μ_m`.
- The **Tate** pairing (when `μ_m ⊆ F_q^*`) connects kernel and rational cokernel:
  `E[m](F_q) × E(F_q)/[m]E(F_q) → μ_m`.
- This paper's **cokernel pairing** acts on **both** rational cokernels:
  `E(F_q)/[m]E(F_q) × E(F_q)/[m]E(F_q) → μ_m`.

When `E[m] ⊆ E(F_q)` the pairing is **non-degenerate**, and can be computed from three
Tate pairings plus two discrete logarithms in `μ_m`, given a basis for `E[m]`.

## Key claims (as reported)
- Non-degeneracy under `E[m] ⊆ E(F_q)`.
- Computable via three Tate pairings and two DLs in `μ_m` — note the **DLs are in the
  multiplicative group `μ_m`**, which is easy for smooth `m`; this is a computation
  recipe, not a hardness claim.
- For `m = ℓ` prime, allows direct study of `E(F_q)/[ℓ]E(F_q)` and **simplifies
  computing a basis of `E[ℓ^k]`**, and more generally the Sylow `ℓ`-torsion.
- Stated natural application: computing `ℓ^k`-isogenies in isogeny-based cryptography.

## Relevance to this program
A **structural** elliptic-curve result of the kind the corpus is comparatively thin on:
most of its 3945 `pairing`-tagged entries concern pairing *constructions*, *inversion*,
or *protocol use*, not new bilinear structure on the curve group itself.

Two bearings:

- **Torsion-basis computation is an inner loop.** Computing a basis of `E[ℓ^k]` is a
  real cost inside `ℓ^k`-isogeny evaluation, hence inside SQIsign-family routines and
  the Deuring machinery this program prices ([[KN-LIT-7642]], `KN-TECH-050`,
  `KN-TECH-057`). A simplification there is a constant-factor cost-model input.
- **The cokernel `E(F_q)/[m]E(F_q)` is an under-examined object.** The program's
  object-first protocol ([[KN-TECH-056]]) asks what objects an attack could track;
  the rational cokernel is one that classical ECDLP attack families do not track, and
  this paper gives it a non-degenerate bilinear form. **That is an observation, not a
  lead** — no attack follows, and none is proposed here. Compare [[KN-LIT-7644]],
  where a cokernel presentation turned out to *leak*, though of a module over `O_K`
  rather than of an elliptic curve.

**Does not bear on the ECDLP.** A pairing computable from Tate pairings inherits the
Tate pairing's reductions and adds no new one; pairing-based reduction of the ECDLP
remains the MOV/Frey–Rück situation the corpus already records.

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/001,
retrieved 2026-08-01 (hence `confidence: reported`). Citation checked against the
ePrint record: title, sole author Krijn Reijnders, report number, year 2026.

NOT verified here: the pairing's definition, bilinearity, or non-degeneracy; the
three-Tate-pairing computation; the claimed simplification for `E[ℓ^k]` bases; and any
cost consequence for isogeny computation. The remark that the rational cokernel is an
object classical ECDLP families do not track is **this program's own observation** and
appears nowhere in the source.
