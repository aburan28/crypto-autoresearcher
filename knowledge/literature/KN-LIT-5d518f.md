---
id: KN-LIT-5d518f
type: literature
title: "The supersingular endomorphism ring problem given one endomorphism"
authors:
  - "Arthur Herlédan Le Merdy"
  - "Benjamin Wesolowski"
year: null
venue: "Cryptology ePrint Archive, Paper 2023/1448"
identifiers:
  eprint: iacr:2023/1448
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/1448"
source:
  citation: >-
    Arthur Herlédan Le Merdy and Benjamin Wesolowski. "The supersingular
    endomorphism ring problem given one endomorphism." Cryptology ePrint
    Archive, Paper 2023/1448. Version read: PDF footer "Date of this document:
    2025-07-03", 37 pp.
  url: "https://eprint.iacr.org/2023/1448.pdf"
tags: [isogeny, supersingular, endomorphism-ring, orientation, primitivisation, vectorisation, higher-dimensional-isogenies, grh, meet-in-the-middle, kuperberg]
confidence: reported
citation_verified: read
added: 2026-09-26
superseded_by: null
---

## Bibliographic notes

- Title, authors, ePrint number and document date were verified from the PDF.
- Venue is not verified. A web-search snippet states publication in IACR
  Communications in Cryptology vol. 2 no. 1 (April 2025), and a search result
  lists arXiv:2309.11912 under the same title. Neither page was opened, so
  both are left out of `identifiers` on purpose.
- `year` is null because the first ePrint posting year was not confirmed from
  the landing page (the ID suggests 2023).

## Contribution

Given a supersingular E and ANY non-scalar α ∈ End(E), the paper computes
End(E) classically in about |disc Z[α]|^{1/4}, and quantumly in
subexponential time. It is rigorous under GRH only. Ingredients:
- polynomial-time division of isogenies by integers using dimension-8
  isogenies (Kani / Robert embedding; Theorem 3, Theorem 4, Algorithm 1);
- a polynomial-time solution of Primitivisation, given the factorisation of
  disc (Theorem 5, Corollary 2);
- a polynomial-time action of smooth ideals (Corollary 3), and of any ideal
  via Clapoti (Corollary 4);
- rigorous meet-in-the-middle and Kuperberg algorithms for O-Vectorisation
  (Theorems 7 and 9).

## Main statements (verbatim, page numbers from the PDF)

- Theorem 1 (GRH), p.4: "There is a classical algorithm that given a
  supersingular curve E, and an endomorphism α ∈ End(E) \ Z, computes the
  endomorphism ring of E in expected time l^{O(1)}|disc(Z[α])|^{1/4} where l
  is the length of the input."
- Theorem 2 (GRH), p.4: the quantum analogue, "in expected time
  l^{O(1)} L_{|disc(Z[α])|}[1/2]".
- Corollary 2, p.24. Given θ ∈ End(E) \ Z "of degree N together with the
  factorisation of disc(Z[θ])", it returns an efficiently represented
  primitive orientation, "in time polynomial in log N and log p".
- Theorem 7 (GRH, Classical O-Vectorisation), p.28: expected time
  l^{O_ε(1)}|disc(O)|^{1/4}.
- Theorem 10 (GRH), p.32: "(Z+cO)-EndRing reduces to O-EndRing in
  probabilistic polynomial time in the length of the input and in the largest
  prime factor of c."
- Proof of Theorem 1, p.29, in order:
  1. factor disc(Z[α]) "in time subexponential in the length of disc(Z[α])"
     [Pom87];
  2. primitivise (Corollary 2);
  3. reduce to O-Vectorisation (Proposition 3 = [Wes22a, Prop. 7]);
  4. solve by Theorem 7, using |disc(O)| ≤ |disc(Z[α])|.

## Assumptions and cost

- Assumption: GRH only. p.4: "Unlike previous results, our proofs do not rely
  on heuristic assumptions."
- Classical: Theorem 1. Quantum: Theorem 2.
- α must be given in efficient representation (§2.3, Definition 7).
  Inseparable α is in scope: the introduction (p.1) names CSIDH's Frobenius as
  the motivating "one public endomorphism".
- No primitivity or conductor bound is required of α; primitivisation happens
  inside the algorithm.
- Factoring disc(Z[α]) is subexponential and added on top, not a factor.
- Memory is of the same order as time. Remark 6 (p.28): "Algorithm 3 needs
  space exponential in the length of the input"; a Pollard-ρ variant is not
  pursued.
- Hidden overhead:
  - The exponent in l^{O(1)} is never stated.
  - Division uses dimension-8 isogenies with B^8 factors (Theorem 4, Lemma 5).
  - Theorem 3 (p.11) states evaluation in Õ(log^11 deg φ).
  - The symplectic-group search Sp_16(Z/4Z) has a "very large" constant
    (footnote 1, p.21).

## Verified vs. not verified by this program

Verified: the statements above, read directly from the full PDF on
2026-09-26.

NOT verified:
- the proofs themselves;
- the venue and arXiv identifiers (see above);
- whether versions other than the 2025-07-03 one differ in theorem numbering.

## Program-side derivation, NOT in source (IDEA-20260926-442b92, claim C3)

The following is this program's own reasoning. It is not stated in this paper,
in Wesolowski ePrint 2026/1486, or in Delgado arXiv 2609.22018. It has not
been reviewed.

1. Walk-conjugation blow-up. Wesolowski's OneEnd output (Algorithm 3, line 7
   of the frozen copy) is α = ω̂∘ϕ∘φ∘ω, where ω is a 2-isogeny walk of length
   n = O(log p). For β = ϕ∘φ ∈ End(E′):
   - tr(ω̂βω) = deg(ω)·tr(β) and deg(ω̂βω) = deg(ω)²·deg(β), hence
     disc(Z[α]) = deg(ω)²·disc(Z[β]);
   - |disc Z[α]|^{1/4} therefore gains a factor 2^{n/2} = p^{Θ(1)}.
   - Delgado's Eq. (62) (KN-LIT-6fb205) states the same degree growth for his
     construction.
   So applying Theorem 1 to the RETURNED α does NOT give p^{1/3}. The C3
   statement "deg alpha = p*delta(E)" is incorrect for the returned
   endomorphism.
2. Corrected route.
   - Apply Theorem 1 at the walk endpoint E′ to β = ϕ∘φ. There
     deg φ ≤ B(p/2)^{1/3} (proof of Algorithm 2 in the frozen copy).
   - Tr(β) = 0: p | Trd and |Trd| ≤ 2√(p deg φ) < p. The argument is as in
     Delgado Prop. 2.7.
   - So |disc Z[β]| = 4p·deg φ = p^{4/3+o(1)}, giving End(E′) in time and
     memory l^{O(1)} p^{1/3+o(1)} under GRH.
   - Transport End(E′) to End(E) along the known walk in probabilistic
     polynomial time under GRH. This is the [Wes22a, Lemma 12] step this
     paper itself uses in the proof of Theorem 10 (p.33).
3. Pareto position.
   - The composed route matches the exponent of the Page–Wesolowski /
     HLMW25 cascade.
   - It is dominated by that cascade: it adds a p^{1/3+o(1)} time AND memory
     term and requires GRH, whereas the cascade has polynomial overhead per
     Delgado Cor. 5.4 (unverified).
   - Its only distinguishing property is independence from PW24's internal
     constants.

## Relevance to program records

- IDEA-20260926-442b92. Resolves its minimal-test read (1):
  - conditions on α: none that the corrected route fails;
  - GRH: required;
  - overhead: unstated polynomial, plus a p^{1/3} memory term.
  C3 as written is defective (item 1 above). The corrected form is a
  dominated alternative, not a new cascade.
- GOAL-SSIQ-001 SC-2 (unstated λ). This route needs no λ, but pays GRH and
  p^{1/3} extra time and memory. SC-2 is more directly addressed by the
  unverified λ(n) = O(n) claim in KN-LIT-6fb205.
- GOAL-SSIQ-001 SC-3 (concrete cost not inheritable). NOT discharged by this
  paper. Its l^{O(1)} exponent is unstated and it carries dimension-8 costs,
  so no concrete figure can be carried through this route either.
- GOAL-SSIQ-001 SC-1. This route keeps GRH. It gives no help in removing GRH
  (contrast HLMW25 / KN-LIT-1499, which claims unconditional equivalences).
- Oriented constructions (442b92 C4). Theorem 1 with α = ι(ω) prices EndRing
  for a published O-orientation at about |disc O|^{1/4}, under GRH.

## Novelty cross-check

A grep of `knowledge/` on 2026-09-26 found no prior KN-LIT entry for ePrint
2023/1448. Before this note it was cited only in ledger/proposals/
IDEA-20260926-442b92.yaml, and only at abstract level.
