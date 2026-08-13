---
id: KN-LIT-a4d0f1
type: literature
title: "Elliptic and hyperelliptic curves with weak coverings against Weil descent attack"
authors:
  - "Jinhui Chao"
  - "Fumiyuki Momose"
year: 2007
venue: "11th Workshop on Elliptic Curve Cryptography (ECC 2007), Dublin (talk slides)"
identifiers:
  doi: null
  arxiv: null
  url: null
tags: [weil-descent, ghs, weak-covering, index-calculus, extension-field, cover-attack, curve-selection, defensive, ecc2007, slides]
confidence: reported
citation_verified: read
added: "2026-08-09"
superseded_by: null
---

## Contribution

Characterisation of elliptic and hyperelliptic curves over extension fields that
admit a **weak covering** — a cover by a curve whose class-group DLP is cheaper
than the square-root bound — extending the GHS/Weil-descent attack surface beyond
the original Artin–Schreier construction, and thereby specifying which curves to
avoid when selecting parameters over `F_{q^d}`.

Read from the local corpus copy `downloads/chao.pdf`.

## Key claims (as reported)

- Attack cost table used as the frame:
  - square-root attacks (BSGS, rho, lambda) on a group of size `l`: `Õ(l^{1/2})`;
  - double-large-prime index calculus on a hyperelliptic `H/F_q` of genus `g`
    (Gaudry–Thériault–Thomé–Diem, Nagao): `Õ(q^{2 - 2/g})`, so `Õ(q^{4/3})` at
    `g = 3`, "a little faster than square-root attacks";
  - Diem's double-large-prime variation on a non-hyperelliptic `C/F_q` of genus
    `g >= 3` and degree `d`: `Õ(q^{2 - 2/(d-2)})`, i.e. `Õ(q^{2 - 2/(g-1)})` when
    `g = d - 1`; `C_{34}` genus-3 curves fall to `Õ(q)`.
- Weil descent (Frey, ECC 1998) realised as the GHS attack (Gaudry–Hess–Smart 2000)
  moves the DLP from `E/K = F_{q^d}` to a class group over `k = F_q` via the
  function-field tower.
- The practical driver for extension fields is implementation, not security:
  normal bases and small-characteristic Frobenius expansions speed arithmetic,
  and those same structures supply the descent.

## Relevance

- Reinforces the same boundary as `KN-LIT-a45b7b`: every member of this family is
  *conditioned on a proper subfield* `F_q ⊂ F_{q^d}`. A prime field admits no such
  subfield, so the weak-covering classification has no prime-field instance —
  neither as an attack nor as a curve-selection criterion. Any prime-field
  "covering defect" invariant is identically trivial, which removes that as a
  candidate measurement axis.
- Useful as the defensive/curve-selection counterpart when this program states
  deployment relevance: the attack surface it maps is extension-field only.
- `LITERATURE-DERIVED`; heuristic complexity claims as reported. No prime-field
  consequence and no breakthrough content.
