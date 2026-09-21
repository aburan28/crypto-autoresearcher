---
id: KN-LIT-7563
remapped_from: KN-LIT-082
remapping_note: >-
  Canonical copy of the frozen ML-KEM record after its ID collided with an
  independently archived canonical record on main. Body unchanged apart from
  remap metadata and cross-references retargeted to the remapped IDs (see
  CORR-20260724-004).
type: literature
title: The supersingular isogeny problem in time and memory p^{1/3+o(1)}
authors: [Wesolowski Benjamin]
year: 2026
venue: preprint; full text frozen in-repo at inputs/P13-WESOLOWSKI-2026/paper_fulltext.md (SRC-P13-WESOLOWSKI-2026)
identifiers:
  eprint: null
  doi: null
  url: null
tags: [supersingular, isogeny-problem, oneend, endomorphism-ring, smoothness, heuristic, dickman-de-bruijn, meet-in-the-middle, claw-finding, rerandomization, deuring, exponent-improvement, exemplar, isogeny, adjacent]
confidence: reported
citation_verified: full_text
added: 2026-07-24
superseded_by: null
---

## Contribution

Proves, conditionally on an explicitly stated smoothness heuristic (Heuristic 1),
that the supersingular isogeny problem — via the OneEnd problem (find a
non-scalar endomorphism of a supersingular E/F_{p^2}) — admits a Las Vegas
algorithm with expected time AND memory p^{1/3+o(1)}, improving the long-stable
p^{1/2}·(log p)^{O(1)} barrier (Delfs-Galbraith and successors, KN-LIT-078).
The new structural ingredient is an external 2026 result (Aubry-Oyono-Vincent,
arXiv:2607.14624, the paper's ref [4]; its Thm 1.5): every supersingular E has
an isogeny to its Frobenius conjugate E^{(p)} of degree ≤ (p/2)^{1/3}. If that
degree is B-smooth, the isogeny splits as η ◦ ψ with both factors of degree
≤ X = B^{1/2}·(p/2)^{1/6}, findable by listing smooth isogenies from E and
meet-in-the-middle on conjugate-paired codomains.

This entry is filed not only as prior art but as the CANONICAL EXEMPLAR of the
result profile this program biases toward; see `docs/target-result-profile.md`
and KN-TECH-055 for the abstracted pattern.

## Key claims (as reported)

- **Theorem 1.1 (heuristic-conditional).** Assuming Heuristic 1, OneEnd is
  solvable in expected time and memory p^{1/3+o(1)}. The paper frames the
  conditioning explicitly; it is not presented as unconditional.
- **Heuristic 1 (formally stated, numbered).** For uniformly random
  supersingular E/F_{p^2}, the degree of the smallest isogeny E → E^{(p)} is
  B-smooth with probability ≥ u^{−u(1+o(1))}, u = log(p/2)/(3 log B), uniformly
  for (log p)^ε < u < (log p)^{1−ε}. Justification architecture: a rigorous
  bound (Thm 1.5: degree ≤ (p/2)^{1/3}) combined with a classical distribution
  theorem (Canfield-Erdős-Pomerance, Thm 1.4: Ψ(X,B) = X·u^{−u(1+o(1))}) — the
  heuristic asks only that the degree behaves like a random integer of its size.
- **Corollary 1.2 (reduction cascade).** Same complexity for EndRing and
  Isogeny, by citing published polynomial-time reductions (Page-Wesolowski,
  the paper's ref [35]). One core result, immediate corollaries — no re-proof.
- **Single-responsibility proof decomposition.** Lemma 3.2 bounds the table
  size (#L(E,X,B) ≤ Ψ(X,B)·X(log X + 2)); Lemma 3.3 bounds the listing runtime
  (Ψ(X,B)·X^{1+o(1)}·B^{O(1)}, via modular-polynomial root finding); Lemma 3.4
  proves correctness under the smoothness condition, including the degree-split
  argument deg ψ, deg η ≤ X = B^{1/2}·(p/2)^{1/6}; Lemma 3.5 gives the success
  probability under Heuristic 1. Theorem 1.1 merely assembles them, with
  explicit bookkeeping: per-attempt cost p^{1/3+o(1)} × inverse success
  probability P0^{−1} = p^{o(1)}-ish, total p^{1/3+o(1)}.
- **Re-randomization to average case.** Algorithm 3 conjugates the instance by
  a non-backtracking random walk E → E′ of length n = O(log p) in the
  2-isogeny graph, with explicit mixing-time justification (Pizer; Basso et
  al.'s Lemma 14), pulls the solution back through the walk, and converts
  φ : E′ → E′^{(p)} into the non-scalar endomorphism ω̂ ◦ ϕ ◦ φ ◦ ω
  (inseparable degree p, not a square, hence ∉ Z).
- **Experimental heuristic validation at cryptographic scale.** Using the
  Deuring correspondence to move the problem to quaternion maximal orders
  (the ideal P of reduced norm p, shortest vector ⇒ degree of the smallest
  conjugate isogeny), the paper samples at cryptographically sized p:
  100,000 curves at p = 5·2^248 − 1 (SQIsign NIST-I) and 10,000 at
  p = 27·2^500 − 1 (NIST-V), comparing the empirical CDF of the largest prime
  factor against the Dickman-de Bruijn prediction ρ(u), including tail
  consistency checks on the smoothest observed samples (12589-smooth in 10^5,
  predicted ρ ≈ 1/69232; e^23-smooth in 10^4, predicted ρ ≈ 1/3312).
- **Concrete-cost and scope honesty.** Rough cost tables at standardized
  parameter sets with optimistic assumptions explicitly flagged: NIST-I
  ≥ 2^106.5 F_{p^2}-ops and ≥ 2^92.5 memory (vs ≈ 2^128, negligible memory,
  previously); NIST-III ≥ 2^157.5 / 2^138.6; NIST-V ≥ 2^204.2 / 2^181.3.
  The paper discloses the superpolynomial overhead hiding in o(1), the high
  memory cost, the van Oorschot-Wiener time-memory tradeoff
  (time p^{1/2+o(1)}/w^{1/2} with memory w) and parallelization, gives an
  explicit affected-vs-safe scope statement (CGL, SQIsign family, GPS, PRISM,
  ⊗-MIKE affected; CSIDH, (qt-)Pegasis, M(D)-SIDH, FESTA, POKE out of range),
  and references a proof-of-concept implementation (Panny, ref [36]).

## Proof architecture (why this is the model to imitate)

The paper exhibits the full target profile in one artifact:

1. **Exponent-first ambition** — it moves the asymptotic exponent of a central
   hard problem (1/2 → 1/3), rather than polishing logarithmic cofactors, and
   says so plainly while noting the prior literature only improved the
   cofactor.
2. **Conditional theorems with explicit heuristics** — the main theorem names
   its dependency (Heuristic 1), states it formally with quantifiers and
   uniformity range, and justifies it by a rigorous bound × a classical
   distribution theorem rather than by assertion.
3. **Single-responsibility lemmas** — each lemma does exactly one job; the main
   theorem is bookkeeping over their outputs.
4. **New external structure converted into an algorithm** — a very recent
   mathematical result (minimal conjugate-isogeny degree) is weaponized via
   smoothness splitting + meet-in-the-middle claw finding.
5. **Re-randomization to the average case** with a cited mixing bound.
6. **Reduction-network cascade** — OneEnd ⇒ EndRing, Isogeny by citation.
7. **Heuristic validation at scale** — the exact distribution the heuristic
   claims is sampled at crypto-sized parameters via a mathematical
   correspondence (Deuring), not extrapolated from toy instances.
8. **Cost/scope honesty** — optimistic assumptions flagged, hidden overhead
   disclosed, memory bottleneck named, tradeoffs parameterized, affected and
   safe systems listed separately, implementation referenced.

Any result this program promotes toward `supported` at a comparable ambition
level should be reviewable against these eight components.

## Relevance to this program

Adjacent to the ECDLP mission (isogeny track; updates the baselines in
KN-TECH-029 and bears on KN-OPEN-013): the p^{1/2} classical reference point
for the pure supersingular problem is now conditionally p^{1/3+o(1)}, so
novelty checks and hardness-foundation claims must cite the new conditional
bound. Its primary function here is methodological: it is the owner-designated
exemplar for what counts as an ambitious, honestly-conditional,
experimentally-validated result (see `docs/target-result-profile.md`), and its
technique pattern is abstracted in KN-TECH-055 for transfer attempts toward
ECDLP/index-calculus directions (KN-OPEN-001 and related).

## Not verified here

The proofs of Lemmas 3.2–3.5 and Theorem 1.1 were read in the frozen full text
but not independently re-derived in this entry; the SageMath experiments and
Panny's implementation were not re-run. The external ingredient (ref [4],
arXiv:2607.14624) is corroborated to exist per SRC-P13-WESOLOWSKI-2026 but its
proof was not read. No ePrint/DOI identifier for the paper itself is recorded
in the frozen text; bibliographic identifiers beyond the in-repo freeze are
unconfirmed. Independent review of the proofs and cost model is scoped to
GOAL-P13-001 tasks (TASK-20260724-P13-HEUR, -COST, -REV, -RT, -VAL); this
entry's claims remain `reported` until those reviews land.
