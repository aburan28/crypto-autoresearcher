---
id: KN-LIT-e3a95c
type: literature
title: "Frobenius characteristic relation on binary curves defined over F_2, and on Koblitz curves: pi^2 - t pi + 2 = 0 with t = 3 - #E(F_2) in {-2..2}; for E_a: y^2 + xy = x^3 + a x^2 + 1, tau^2 - mu tau + 2 = 0 with mu = (-1)^(1-a)"
authors:
  - "Jithra Adikari"
  - "Vassil S. Dimitrov"
  - "Renato J. Cintra"
year: 2018
venue: "arXiv:1801.08589 (A New Algorithm for Double Scalar Multiplication over Koblitz Curves); general form from Wikipedia 'Schoof's algorithm' and 'Counting points on elliptic curves' (SEA section)"
identifiers:
  eprint: null
  arxiv: "1801.08589"
  doi: null
  url: "https://ar5iv.arxiv.org/html/1801.08589"
tags: [koblitz, frobenius, characteristic-polynomial, trace, hasse, binary-field, tau-adic, subfield-curve, ecdlp]
confidence: established
citation_verified: read
provenance: retrieved
verified_by: "idea-generator, TASK-20260929-c05f6e, 2026-09-30 (HTML renderings fetched and read in session; PDFs of Solinas and Avanzi-Heuberger-Prodinger could not be decoded and were NOT read)"
added: "2026-09-30"
superseded_by: null
status_note: >-
  DRAFT under coordination/tasks/TASK-20260929-c05f6e/proposed-records/. Not in
  knowledge/ until a Coordinator archival task moves it. Identifier chosen
  without a shell (no allocate_id.py); committed-state collision check owed.
---

## Why this record exists

The corpus had no citable statement of the Frobenius characteristic relation on
Koblitz curves. DEC-20260929-3e8a1c had to move its pointer (FG-1) out of
`citations` because no agent had opened a source. This record is that opening.
It is cited by TASK-20260929-c05f6e's literature screen (§1) and DESIGN.md (§2).

## What the sources state (as read)

- **S1, Wikipedia "Schoof's algorithm" (fetched 2026-09-30):** "φ:(x,y)↦(x^q,y^q)";
  "φ²−tφ+q=0"; "t=q+1−#E(F_q)"; "|q+1−#E(F_q)|≤2√q".
- **S2, Wikipedia "Counting points on elliptic curves", SEA section:** "the
  characteristic equation of the Frobenius endomorphism" is "ϕ² − tϕ + q = 0".
- **S3, Adikari–Dimitrov–Cintra 2018 (ar5iv rendering):** "[τ]P = (x², y²)", where
  τ is "a complex number with value (μ + √−7)/2, where μ = (−1)^{1−a}". Koblitz
  curves are given as "E_a: y² + xy = x³ + ax + 1", a ∈ {0, 1}. **Recorded
  discrepancy:** the standard form has ax². Over F_2 the two forms agree
  pointwise, but they differ over F_{2^m}. This may be an extraction artifact
  and is unresolved. S3 cites Koblitz and Solinas for these facts; those were
  not read.

## Derived in the reading session (hand checks, not machine-verified)

1. **q = 2:** π² − tπ + 2 = 0 and t = 3 − #E(F_2). Hasse gives |t| ≤ 2√2, so
   t ∈ {−2, −1, 0, 1, 2}.
2. **Koblitz form:** ((μ+√−7)/2)² − μ(μ+√−7)/2 + 2 = 0, so τ² − μτ + 2 = 0, i.e.
   t = μ.
3. **Point counts over F_2:** E_0(F_2) = {O, (0,1), (1,0), (1,1)} gives
   t = −1 = μ(a=0). E_1(F_2) = {O, (0,1)} gives t = +1 = μ(a=1).
4. **Action on E(F_{2^n}):** π^n = 1 on E(F_{2^n}), and Fix(π) = E(F_2).
   #E_a(F_2) ∈ {4, 2} divides #E_a(F_{2^n}). On a cyclic subgroup of prime order
   ℓ ∤ #E(F_2), π acts as λ with λ² − μλ + 2 ≡ 0 (mod ℓ), and ord(λ) = n for
   prime n.

## What it does NOT say (so nobody cites it for these)

- Nothing about curves over F_{2^n} that are not defined over F_2. There the
  2-power Frobenius maps E to E^(2) and is not an endomorphism.
- Nothing about ordinary versus supersingular classification by the parity of
  t. That is recalled, not read here.
- Nothing about index calculus, factor bases, or rho speedups. For those see
  KR-IC-b0fcda and KR-RHO-037e22.
- Solinas (1997/2000) and Avanzi–Heuberger–Prodinger remain `recalled`.

## Relevance

Supplies FG-1 of DEC-20260929-3e8a1c with a `retrieved` basis, and corrects one
part of FG-1. ΣP_i = R ⇒ Σπ(P_i) = π(R) **transports** an m-SUM instance to the
instance with target π(R). It does not act on a single solution set, because
π(R) = R only for R ∈ E(F_2) (TASK-20260929-c05f6e DESIGN.md §2.1, L1).
