---
id: KN-TECH-055
remapped_from: KN-TECH-031
remapping_note: >-
  Canonical copy of the frozen ML-KEM record after its ID collided with an
  independently archived canonical record on main. Body unchanged apart from
  remap metadata and cross-references retargeted to the remapped IDs (see
  CORR-20260724-004).
type: technique
title: Conditional exponent improvement via structural bound + smoothness/distribution heuristic + meet-in-the-middle + re-randomization
tags: [exemplar, exponent-improvement, smoothness, heuristic, dickman-de-bruijn, meet-in-the-middle, claw-finding, rerandomization, mixing-time, conditional-theorem, methodology, isogeny, adjacent]
confidence: reported
complexity: pattern shape — rigorous bound shrinks the search object to size X, smoothness splitting halves it to ~X^{1/2} per side, meet-in-the-middle collides the halves, re-randomization amortizes a per-attempt success probability P0; total cost ~ (table size) x P0^{-1} with memory ~ table size
applicability: >-
  Hard problems where (a) a new structural theorem bounds the size of a target
  object, (b) the object's arithmetic can plausibly be modeled by a classical
  distribution (smooth integers, Dickman-de Bruijn), (c) the object splits
  multiplicatively so a meet-in-the-middle/collision search applies, and (d)
  instances can be re-randomized with a provable mixing bound so a
  heuristic-average success probability suffices.
source_refs: [KN-LIT-7563, KN-LIT-078, KN-LIT-075, KN-LIT-012]
added: 2026-07-24
superseded_by: null
---

## The pattern

Abstracted from Wesolowski's p^{1/3+o(1)} supersingular-isogeny result
(KN-LIT-7563), the owner-designated canonical exemplar. Five components, each
independently checkable:

1. **Structural bound.** Import (or prove) a theorem bounding the size of the
   target object. In the exemplar: the smallest isogeny E → E^{(p)} has degree
   ≤ (p/2)^{1/3} (external 2026 result, the paper's Thm 1.5). The bound must
   be rigorous — it is the load-bearing wall; everything heuristic sits on top
   of it, never underneath it.
2. **Distribution heuristic, formally stated.** Assume the target object's
   arithmetic behaves like a classical random model of its size — in the
   exemplar, B-smooth with probability u^{−u(1+o(1))} per
   Canfield-Erdős-Pomerance (Heuristic 1). State it numbered, with quantifiers
   and uniformity range, so reviewers can attack exactly one sentence.
3. **Split + meet-in-the-middle.** Smoothness makes the object factor; choose
   the split point so both halves fit in one table of size ~X (in the
   exemplar, deg ψ, deg η ≤ X = B^{1/2}·(p/2)^{1/6}), then collide the halves
   (claw finding on conjugate-paired codomains). One lemma per job: table-size
   bound, construction runtime, correctness under the split condition, success
   probability under the heuristic.
4. **Re-randomization to average case.** Random-walk the instance (exemplar:
   length n = O(log p) in the 2-isogeny graph, mixing justified by citation),
   solve the rerandomized instance with heuristic probability P0, pull the
   solution back through the walk. Expected total cost = per-attempt cost ×
   P0^{−1}, with the bookkeeping done explicitly in the main theorem.
5. **Validation + honesty at scale.** Sample the heuristic's exact distribution
   at cryptographically sized parameters (exemplar: Deuring correspondence
   moves degree-of-smallest-conjugate-isogeny to shortest-vector norms in
   maximal orders; 10^5 samples at NIST-I p, 10^4 at NIST-V p) against the
   theoretical CDF (Dickman-de Bruijn ρ(u)) including tail checks; publish
   concrete-cost tables with optimistic assumptions flagged, disclose the
   superpolynomial overhead in o(1), name the memory bottleneck, and
   parameterize time-memory tradeoffs (van Oorschot-Wiener: time
   p^{1/2+o(1)}/w^{1/2} at memory w).

## Transfer notes toward ECDLP / index calculus

Speculative — recorded as leads for the Idea Generator, not as validated
methods:

- **The structural-bound slot is the scarce resource.** The exemplar's exponent
  moved because a *new external theorem* shrank the target object. The ECDLP
  analog would be a rigorous bound that shrinks a relation search — e.g. a
  bound on summation-polynomial solution structure, first-fall/solving degree
  (KN-OPEN-002), or BKK/mixed-volume saturation (KN-OPEN-004) — converting an
  asymptotic plateau into a smaller meet-in-the-middle. Without such a bound,
  components 2–5 have nothing to bite on.
- **Smoothness heuristics already exist in our setting.** Decomposition
  probability in point-decomposition index calculus is a smoothness-type
  assumption (a point's x-coordinate splits over the factor base). The
  exemplar's discipline — state it as a numbered heuristic with a uniformity
  range, then validate it at scale against the Dickman-de Bruijn prediction —
  applies directly to how this program should handle its own decomposition
  heuristics (KN-TECH-003, KN-OPEN-001).
- **The Deuring-correspondence validation move generalizes as a method:** when
  the target distribution is too costly to sample directly, find a
  mathematical correspondence that makes sampling cheap at full scale,
  validate the heuristic there, and say exactly which correspondence was used.
  Toy-scale validation presented as crypto-scale evidence violates this
  pattern and the repo's core rule 7.
- **Meet-in-the-middle/collision accounting is shared.** The exemplar's cost
  model (table size × inverse success probability, van Oorschot-Wiener
  interpolation to the polynomial-memory regime) is the same accounting as our
  rho/distinguished-points baseline (KN-TECH-006); comparisons of any
  transferred attack against that baseline must include the memory axis, not
  time alone.

## Known limits

- **Memory is the bottleneck.** Time AND memory are both p^{1/3+o(1)} in the
  exemplar; reducing memory via van Oorschot-Wiener pushes time back toward
  p^{1/2+o(1)}/w^{1/2}. At cryptographic sizes the high-memory regime may be
  infeasible, which the paper itself flags as a serious deployment obstacle.
- **The o(1) hides superpolynomial overhead.** The exemplar discloses that its
  hidden term is much larger than the previous (log p)^{O(1)} cofactor, so the
  asymptotic win need not translate to concrete wins at NIST parameters
  (NIST-I estimate ≥ 2^106.5 ops / 2^92.5 memory vs ≈ 2^128 previously —
  flagged by the author as optimistic).
- **The heuristic is unproven.** Heuristic 1 is of a class "ubiquitous in
  computational number theory, yet notoriously difficult to prove"; the
  theorem is exactly as strong as that assumption plus its experimental
  support. A counterexample or arithmetic bias in the degree distribution
  collapses the exponent claim to the tested scope only.
- **Pattern preconditions are strong.** All four applicability conditions
  (structural bound, distributional model, multiplicative split, mixable
  re-randomization) must hold simultaneously; most problems fail at least one.
