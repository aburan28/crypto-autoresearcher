---
id: KN-LIT-1e6270
type: literature
title: "On the discrete logarithm problem for prime-field elliptic curves (full text read): random known-log factor base, one relation, about m^m Groebner solves of a split system, no exponent claimed"
authors:
  - "Alessandro Amadori"
  - "Federico Pintore"
  - "Massimiliano Sala"
year: 2018
venue: "Finite Fields and Their Applications 51:168-182 (2018); IACR ePrint 2017/609; accepted manuscript dated 16 January 2018 on the University of Trento IRIS repository"
identifiers:
  eprint: "iacr:2017/609"
  arxiv: null
  doi: "10.1016/j.ffa.2018.01.009"
  url: "https://iris.unitn.it/handle/11572/202653"
tags: [index-calculus, prime-field, summation-polynomial, factor-base, groebner, known-log-factor-base, single-relation, ecdlp]
confidence: reported
citation_verified: read
added: "2026-10-25"
superseded_by: null
---

## Contribution

Variant of Semaev's prime-field index calculus in which the factor base is
not selected but generated: `s` random points `R_j = u_j P + v_j Q` are
appended to `F` until `|F| = s` with `s^m ≈ q`, every base point carries its
own log coordinates `(u_j, v_j)`, and the whole discrete logarithm reduces to
finding **one** vanishing signed sum of `m` base points. The authors state
explicitly that they do not claim to beat generic algorithms.

Supersedes the abstract-only stub KN-LIT-99dfe4. Equation and page numbers
below are those of the accepted manuscript (AM, 11 pp.); the publisher PDF was
access-restricted, so FFA page numbers could not be assigned. The paper is not
on arXiv.

## Key claims (verified from the full text)

- Setting (AM §3, p. 6): `|E(F_q)| = r` prime, `Q = wP`. Relation collection:
  "The factor base F is not fixed, rather it is initialized as the empty set
  ... As usual we take `s^m ≈ q`. For random integers u, v, the point
  R = uP + vQ is computed and added to the factor base F." (verbatim)
- Relation solving (AM §3, §3.1): partition `F = F_1 ⊔ … ⊔ F_m` into equal
  parts, `V_i = x(F_i)`, `f_i(X_i) = ∏_{v ∈ V_i}(X_i − v)` (eq. 10, degree
  ≈ `s/m`); solve system (11) `S_m(X_1,…,X_m) = 0, f_1(X_1) = 0, …, f_m(X_m)
  = 0` by a Magma Groebner basis in grevlex (no algorithm, version or
  extraction method stated). A solution gives `±P_i ∈ F_i` with
  `P_1 + ⋯ + P_m = ∞` (eq. 8), hence `λP + µQ = ∞` and `w = −λ/µ mod r`. If
  no solution, the whole base is redrawn. The partition "break[s] the
  symmetry and avoid[s] trivial solutions when m is even" (AM p. 7), credited
  to Galbraith–Gebregiyorgis.
- Index convention: APS's `m` counts all points of the relation (they solve
  `S_m`); APS "m = 3" is the degree analogue of the standard two-point
  decomposition `S_3(X_1, X_2, x(R))`.
- For `m = 4, 5` the systems actually solved replace `S_4`, `S_5` by
  `{S_3(X_1,X_2,Y), S_3(X_3,X_4,Y)}` and `{S_3(X_1,X_2,Y), S_4(X_3,X_4,X_5,Y)}`
  with an auxiliary `Y` (AM §3.4, p. 9), citing Huang et al., Karabina and
  Semaev 2015.
- Cost model (AM §3.2, pp. 7–8, HEURISTIC): expected number of m-sums
  `(s/m)^m`; success probability per system `s^m/(q·m^m)` (eq. 12); total cost
  `(q·m^m/s^m)·T(E,m,V)`. With `s^m ≈ q` this is about `m^m` Groebner
  computations per DLP. Verbatim: "In order to reach an improvement with
  respect to algorithms for generic cyclic groups, this complexity should be
  smaller than `r^{1/2}`. We do not claim this result. Indeed our complexity
  analysis is partial, since we are unable to estimate the complexity of
  solving our polynomial equation systems."
- Comparison with Petit–Kosters–Messeng (AM §3.3, Table 1): PKM's cost
  transcribed as `(p·m!/s^{m−1})·T' + s^ω`; under the explicitly unproven
  assumption (13) `T ≈ T'`, APS beats PKM when `s·m! > m^m`, i.e.
  `p^{1/m} > m^m/m!` (7, 14, 24, 37, 52, 70 bits for m = 3..8; thresholds
  reproduce). No degree of regularity, Macaulay bound or asymptotic exponent
  appears anywhere in the paper.
- Experiments (AM §3.4, Table 2, EXPERIMENTAL): p of 11–22 bits,
  m ∈ {3,4,5}, 100 curves × 10 instances, Magma on a Xeon 5460; at 22 bits
  267.7 s (m=3, s=146), 339.9 s (m=4, s=43), 388.0 s (m=5, s=21). The "Petit
  et al." column is PKM's per-system time for a two-point decomposition at
  |V| ≈ p^{1/2}, set against APS's per-DLP time at |F| ≈ p^{1/3}; the
  even/odd-bit attribution of PKM's rows is reversed relative to PKM's
  Tables 4 and 5. No success rates, memory, degrees of regularity or system
  counts are reported.
- Barrier remarks (AM §1): "the difficulty to endow F with an algebraic
  structure, and the impossibility to exploit the Weil descent in the PDP".
- Stated open items (AM §4): the complexity of system (11); whether
  non-Groebner solvers are better; the composite-field case.

## How the follow-ups settle it (as reported in those papers)

- McGuire–Mueller (KN-LIT-2d30ef): Groebner cost of the APS system is
  `O(p^{ω−ω/m})` by the Macaulay bound; the base must be regenerated
  `m^m/2^{m−1}` times, "not only one [Groebner basis] as is claimed".
- Kudo–Yokota–Takahashi–Yasuda (KN-LIT-c1e815): hybrid method, `(t_1, t_2)`
  symmetrisation and GCD solving accelerate the variant; cost "at least
  `p^{2/3}`" as restated by Dzierzkowski–Wroński (KN-LIT-44eaba).
- Yokoyama–Yasuda–Takahashi–Kogure (KN-LIT-8bf122): heuristic lower bound
  `≥ m·2^{m−1}·d^{m−1}` field operations per system for any split base.

## Relevance to this program

The known-log/random-base mechanism is the family behind `H-ICEX-6ca21f`'s
CRT argument. With the base random, the relation search is the k-sum problem
in `E(F_p)`; Wagner's Theorem 2 (KN-LIT-7a7034) bounds every generic solver
by `Ω(√p)`, and the Groebner route is bounded by KN-LIT-8bf122. See
`KR-IC-52ad34` and DEC-20261025-48232f.

## Not verified here

The ePrint-vs-journal diff (ePrint and publisher PDFs were bot-blocked), and
any solver detail the paper omits (Groebner algorithm, variable order,
solution extraction).

## Provenance

Full accepted-manuscript text read on 2026-10-24 by a delegated literature
lane of the session recorded in DEC-20261025-48232f (notes:
`docs/reports/aps-prime-field-review-20261025/lanes/aps2018_dissection.md`).
Bibliographic identifiers confirmed against the ePrint record, Crossref,
OpenAlex and zbMATH (Zbl 1421.11103).
