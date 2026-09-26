---
id: KN-LIT-6fb205
type: literature
title: "The Supersingular Isogeny Problem in Time and Memory p^{1/3+o(1)}, Unconditionally"
authors:
  - "José Luis Delgado"
year: 2026
venue: "arXiv preprint (v1), arXiv:2609.22018 [cs.CR]"
identifiers:
  eprint: null
  doi: null
  arxiv: "2609.22018"
  url: "https://arxiv.org/abs/2609.22018"
source:
  citation: >-
    José Luis Delgado (Independent Researcher). "The Supersingular Isogeny
    Problem in Time and Memory p^{1/3+o(1)}, Unconditionally."
    arXiv:2609.22018v1 [cs.CR], 18 Sep 2026. 24 pp.
  url: "https://arxiv.org/abs/2609.22018"
tags: [isogeny, supersingular, oneend, endomorphism-ring, unconditional, meet-in-the-middle, random-walk, chenu-smith, attack, heuristic-removal]
confidence: unverified
confidence_note: >-
  v1 preprint, single author, not refereed as far as this program knows. Read
  in full (PDF, all 24 pages) on 2026-09-26, but its claims have NOT been
  independently verified by this program: no proof has been checked, no
  implementation has been run, and no reviewer has checked it. Cite it only as
  a CLAIM. Upgrade only after an independent proof check or an external
  refereed version.
citation_verified: read
added: 2026-09-26
superseded_by: null
---

## Contribution (as claimed by the source)

The paper claims to remove the smoothness assumption (Heuristic 1) from
Wesolowski's p^{1/3+o(1)} OneEnd algorithm (ePrint 2026/1486; frozen copy at
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`). It keeps Wesolowski's outer
structure:
- a lazy 2-isogeny walk to a near-uniform curve;
- meet-in-the-middle for a separable isogeny φ: E → E^{(p)};
- composition with the relative Frobenius;
- a pull-back along the walk.

In place of "the least degree is smooth often enough", it uses a DETERMINISTIC
family D_p of squarefree smooth degrees, fixed before any curve is sampled:
- The Chenu–Smith count gives many (d,+1)-structures for each d ∈ D_p.
- Tatuzawa's theorem gives the class-number lower bound, with at most one
  exceptional degree (Prop. 4.2, p.13).
- A new collision bound (Theorem 3.5) shows these isogenies are spread over
  many distinct curves.
- List matching uses colour coding [AYZ95] (§5.4).

## Main statements (verbatim, page numbers from the arXiv v1 PDF)

- Theorem 1.1 (Main theorem), p.3: "Let p > 3 be prime. There is a classical
  Las Vegas algorithm which, given a supersingular elliptic curve E/F_{p^2},
  returns a non-scalar endomorphism α ∈ End(E) \ Z, in efficient
  representation, in expected time and memory p^{1/3} exp(O(√(log p log log p)))
  = p^{1/3+o(1)}. The returned endomorphism satisfies log deg α = O(log p),
  and the algorithm and its analysis are unconditional."
- Corollary 1.2, p.3: "The supersingular endomorphism ring problem and the
  supersingular isogeny problem admit classical probabilistic algorithms with
  expected time and memory p^{1/3+o(1)}."
- Theorem 3.5 (Finite collision bound), p.11. For squarefree d, e ≥ 2 coprime
  to p and X = 2⌈√(de)⌉:
  C^+_{d,e}(p) ≤ 78 X 𝔓(X) ∏_{ℓ | gcd(d,e)} (1 + 3/ℓ).
  Eq. (27) gives the asymptotic form ≪ √(de) log²(2de) ∏(1+3/ℓ).
- Theorem 4.4 (Density of smooth isogenies to conjugates), p.16. For bit
  length n ≥ 2^16, at least p/(2^80 n^4) generic supersingular maximal models
  admit (d,+1)-structures for at least two distinct degrees d ∈ D_p. Each such
  d ≤ p^{1/3} exp(O(√(log p log log p))), and every prime factor is
  exp(O(√(log p log log p))).
- Theorem 5.3 (Main algorithm), p.22. Same bound as Theorem 1.1. "The output
  satisfies log deg α_in = O(log p), and the analysis is unconditional and
  independent of smoothness or statistical independence heuristics."
- Eq. (62), p.21. For the pulled-back endomorphism α⋆ = ω̂ ∘ α_E ∘ ω:
  "deg α⋆ = 2^{2r} p deg φ ≤ 2^{2T} pB, log deg α⋆ = O(n)".
  Here T = ⌈((n/2+81) log 2 + 4 log n)/log(36/35)⌉ (Eq. 54, p.18).
- Corollary 5.4 proof, pp.22–23: "Equation (62) solves the bounded problem
  OneEnd_λ with λ(n) = O(n). The reduction from EndRing to bounded OneEnd of
  Page–Wesolowski and the unconditional equivalences of Herlédan
  Le Merdy–Wesolowski [PW24, Theorem 7.1][HLMW25, Theorem 1.1] have overhead
  polynomial in n and λ(n), which is absorbed by (64)."

## Assumptions and cost (as claimed)

- Assumptions: none claimed (no GRH, no smoothness heuristic).
- p ≥ 2^16 bits: finitely many smaller p are handled by exhaustive search,
  absorbed into the O(·) (proof of Thm 5.3, p.22).
- Time and memory are both p^{1/3} exp(O(√(log p log log p))).
- Expected number of trials is O(n^4) (§5.2, Eq. 55).
- §1.6, p.4: "with a large subexponential factor and memory of the same order
  as the running time; practical attack costs and concrete security levels lie
  outside its scope."
- The explicit constants are enormous: 2^80 n^4 in the density bound, 2^50 n^2
  in Cor. 3.6. The claim is purely asymptotic.
- Scope limit stated by the author (p.23): the corollary "concerns Isogeny with
  unrestricted output degree; a path whose prime degree is prescribed in
  advance lies outside its statement."

## Verified vs. not verified by this program

Verified:
- Title, author, arXiv id and date, from the arXiv abstract page and the PDF
  stamp "arXiv:2609.22018v1 [cs.CR] 18 Sep 2026".
- The verbatim statements above were read directly from the PDF (all pages).

NOT verified:
- Correctness of Theorem 3.5, Theorem 4.4 or the complexity analysis.
- That the cited reductions (PW24 Thm 7.1, HLMW25 Thm 1.1) have the claimed
  polynomial overhead and are unconditional. PW24 has not been read by this
  program. HLMW25 (arXiv 2502.17010, KN-LIT-1499) has been read at abstract
  level only; its abstract claims Isogeny/EndRing/MaxOrder equivalence
  "unconditionally".
- Refereed status and any later versions.
- An earlier WebFetch summary of the HTML version returned garbled reference
  entries. It was discarded; nothing in this note depends on it.

## Relevance to program records

- GOAL-P13-001 (status closed_at_budget).
  - Its recorded resume condition is NC-3/NC-6 (Heuristic 1 tail validation)
    reaching a determinate outcome, plus a fresh budget authorization.
  - This paper does not satisfy that condition literally.
  - If its claims hold, however, the p^{1/3+o(1)} exponent no longer depends
    on Heuristic 1 at all, and Heuristic-1 validation stops carrying the
    exponent claim.
  - FLAGGED as a CANDIDATE TRIGGER for a Coordinator revisit of GOAL-P13-001,
    PENDING VERIFICATION of this paper. This note moves no status and records
    no decision.
- IDEA-20260926-4a496f (Heuristic 1 validation). Its value as exponent
  support is contingent on this paper failing. If this paper holds, the idea
  reduces to an empirical study of Wesolowski's practical constant and
  heuristic. Route this to the Coordinator; no status moves here.
- GOAL-SSIQ-001 standing conditions (ledger/goals/GOAL-SSIQ-001/goal.yaml):
  - SC-1 (Isogeny statements conditional on Heuristic 1 AND GRH). This paper
    claims to remove both: Heuristic 1 at OneEnd, and GRH in the reductions
    via HLMW25. Unverified.
  - SC-2 (unstated λ). Addressed directly by the claim λ(n) = O(n), i.e.
    log deg α = O(log p) (Thm 1.1; Cor. 5.4). Discrepancy to reconcile: SC-2
    cites "Theorem 7.2" of Page–Wesolowski; this paper cites "Theorem 7.1".
  - SC-3 (concrete cost not inheritable). Unaffected. The paper disclaims
    concrete costs, and its constants (2^80 n^4, 2^50 n^2) make any concrete
    transfer meaningless.
- KN-LIT-678a43 (Udovenko, ePrint 2026/1575, unconditional p^{2/5+o(1)}). This
  paper cites it as the previous unconditional exponent and reuses its
  Chenu–Smith count "in the form developed there" (§1.6, p.4). If this paper
  holds, it supersedes 678a43's "current unconditional state of the art"
  statement at the exponent level. 678a43 is not edited here.
- IDEA-20260926-442b92, C3. Eq. (62) confirms that the pulled-back OneEnd
  output has degree 2^{2r}·p·deg φ. That is the walk-conjugation blow-up
  noted in KN-LIT-5d518f. log deg α = O(log p) still holds.

## Novelty cross-check

A grep of `knowledge/` and `ledger/` on 2026-09-26 found no prior entry for
arXiv 2609.22018 or for this author.
