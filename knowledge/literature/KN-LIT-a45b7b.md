---
id: KN-LIT-a45b7b
type: literature
title: "Index Calculus in Class Groups of Plane Curves of Small Degree"
authors:
  - "Claus Diem"
year: 2007
venue: "11th Workshop on Elliptic Curve Cryptography (ECC 2007), Dublin (talk slides)"
identifiers:
  doi: null
  arxiv: null
  url: null
tags: [index-calculus, plane-curve, model-degree, non-hyperelliptic, genus-3, double-large-prime, class-group, dlp, factor-base, ghs, ecc2007, slides]
confidence: reported
citation_verified: read
added: "2026-08-09"
superseded_by: null
---

## Contribution

Index calculus for class groups of arbitrary (not necessarily hyperelliptic)
curves, with the cost exponent driven by the **degree of a plane model** rather
than by the genus. Relations are cut by lines meeting the plane model in `d`
points; a smaller defining degree means shorter, more frequent relations.

Read from the local corpus copy `downloads/diem.pdf`.

## Key claims (as reported)

- Adapting hyperelliptic index calculus to arbitrary curves poses "no principal
  problem"; heuristically the running times are unchanged up to logarithmic
  factors.
- For a fixed genus `g` and a fixed plane-model degree `d >= 4`, heuristically:
  - Gaudry optimal factor base + double large prime: `Õ(q^{2 - 2/g})`
  - Diem's algorithm + double large prime: `Õ(q^{2 - 2/(d-2)})`
- Genus 3 over `F_q`: rho and Gaudry–Harley both `Õ(q^{3/2})`; Gaudry–Thériault–Thomé
  double-large-prime `Õ(q^{4/3})`; non-hyperelliptic genus 3, heuristically `Õ(q)`.
- The stated reason for the gain is purely the model degree: non-hyperelliptic
  genus-3 curves admit degree-4 (plane quartic) equations, while hyperelliptic
  genus-3 curves need degree 5 or higher.
- Motivating application: transfers of an elliptic or hyperelliptic DLP over
  `F_{q^n}` down to a higher-genus curve over `F_q` (GHS; Diem–Scholten) very often
  land on a non-hyperelliptic curve, so the transferred instance falls under this
  faster algorithm.

## Relevance and the boundary for prime fields

- The exponent `2 - 2/(d-2)` is **increasing** in `d`. Re-embedding a fixed curve
  at a *higher* plane-model degree therefore strictly worsens the index-calculus
  exponent; the gain in genus 3 comes from `d = 4 < 5`, i.e. from *lowering* `d`.
  This closes the natural-looking "re-embed `E` in a higher-degree plane model to
  get shorter relations" line by monotonicity alone.
- An elliptic curve already has minimal plane-model degree `d = 3`, one below the
  algorithm's stated applicability threshold `d >= 4`. The formal extrapolation of
  the exponent to `d = 3` is vacuous rather than favourable: for a plane cubic a
  line meets the curve in exactly the three points of a group-law relation, so the
  relation supply is trivial while the factor base and the group have the *same*
  order of magnitude, and no smoothness gain exists to be harvested. The parameter
  that produces Diem's gain is already at its floor for `E`.
- The applicability precondition throughout is a *proper subfield to descend to*
  (`F_{q^n} → F_q`). A prime field has none, which is the standing reason this
  family gives nothing over `F_p`. Recorded against `KN-OPEN-001` and `KN-OPEN-020`.
- `LITERATURE-DERIVED`; heuristic complexity claims as reported by the author. No
  prime-field consequence and no breakthrough content.
