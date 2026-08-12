# Target Result Profile

This document is the canonical reference for what a *target-class result* looks
like in this repository. Every hypothesis, experiment proposal, review, and
Coordinator status decision that claims a major advance should be checked
against it. The exemplar is Benjamin Wesolowski, "The supersingular isogeny
problem in time and memory p^{1/3+o(1)}" (frozen full text:
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`). The exemplar is an
isogeny-based result; the profile it defines is domain-general and applies to
ECDLP and related directions in this repo.

The profile describes the *shape* of a result, not a guarantee of truth. A
direction can match the profile and still be wrong; a direction that does not
match the profile is not a target-class result regardless of its correctness.

## Part A — The exemplar pattern

The paper improves the asymptotic complexity of the supersingular isogeny
problem (and its polynomially equivalent siblings OneEnd and EndRing) from
p^{1/2}·(log p)^{O(1)} to p^{1/3+o(1)}, conditional on one explicitly stated
heuristic. Eight elements make up the pattern.

### A1. Exponent-first ambition

The claim targets the *exponent* of a central hard problem: the main theorem
(Theorem 1.1) moves the complexity class from p^{1/2}·(log p)^{O(1)} — stable
since [21] (Delfs–Galbraith), with later work improving only the logarithmic
cofactor [15, 24, 26, 40] — to p^{1/3+o(1)}. The paper explicitly frames prior
progress as cofactor polishing ("subsequent improvements only impacting the
logarithmic cofactor", §1) and positions itself against that class of result.

**Profile rule.** A target-class result changes the asymptotic exponent (or an
equally central structural barrier) of a named hard problem. Constant-factor
speedups, implementation tuning, and logarithmic-cofactor improvements are
valuable engineering but are not target-class, and must not be presented as if
they were.

### A2. Conditional theorems with explicit heuristics

The main theorem is conditional on a numbered, formally stated assumption:
**Heuristic 1** — for a uniformly random supersingular E/F_{p^2}, the degree of
the smallest isogeny E → E^{(p)} is B-smooth with probability at least
u^{−u(1+o(1))}, u = log(p/2)/(3 log B), uniformly in a stated range
((log p)^ε < u < (log p)^{1−ε}). The heuristic is not asserted raw; it is
*justified by composition* of two rigorous ingredients:

- a rigorous size bound, **Theorem 1.5** ([4], Aubry–Oyono–Vincent): an
  isogeny E → E^{(p)} of degree ≤ (p/2)^{1/3} always exists; and
- a classical distribution theorem, **Theorem 1.4** ([10],
  Canfield–Erdős–Pomerance): Ψ(X, B) = X·u^{−u(1+o(1))} uniformly in the same
  u-range.

Heuristic 1 then asks only that the specific integer (the minimal degree)
behaves like a uniformly random integer of its size with respect to
smoothness. The theorem statement names the heuristic it depends on
("Assuming Heuristic 1, ..."), and the dependency propagates into every
corollary.

**Profile rule.** Every heuristic a target-class result depends on is stated
as a numbered, standalone, falsifiable assertion with quantifiers and
uniformity ranges, and is justified by combining a rigorous bound with a
classical distribution theorem — not by intuition. Theorem statements carry
their heuristic dependencies by name.

### A3. Single-responsibility proof decomposition

Section 3 decomposes the result so that each lemma does exactly one job:

| Component | Sole responsibility |
|---|---|
| Definition 3.1 | Defines the search object L(E, X, B) (cyclic-kernel isogenies of B-smooth degree < X). |
| Lemma 3.2 | Table-size bound only: #L(E, X, B) ≤ Ψ(X, B)·X·(log X + 2). |
| Algorithm 1 | Lists L(E, X, B) (numbered, Require/Ensure). |
| Lemma 3.3 | Runtime only: Ψ(X, B)·X^{1+o(1)}·B^{O(1)}. |
| Algorithm 2 | Meet-in-the-middle claw finding over the keyed table. |
| Lemma 3.4 | Correctness only, *under the smoothness condition*: if the smallest E → E^{(p)} isogeny is B-smooth, Algorithm 2 returns it. Contains the degree-split argument: writing deg φ = Π ℓ_i and splitting at the largest prefix ≤ X = B^{1/2}·(p/2)^{1/6}, both halves satisfy deg ψ, deg η ≤ X, because deg η ≤ B·(p/2)^{1/3}/X = X. |
| Lemma 3.5 | Success probability only, under Heuristic 1: ≥ u^{−u(1+o(1))}. Remark 1 records why this bound is not expected to be tight. |

The main theorem's proof then *only assembles*: it sets
B = e^{(1/3)√log(p/2)} = p^{o(1)}, computes the per-attempt success
probability P0 = u^{−u(1+o(1))} = p^{−o(1)} with u = √log(p/2), so that
P0⁻¹ = p^{o(1)}, from Lemma 3.5, computes
the per-attempt cost p^{1/3+o(1)} from Lemmas 3.2–3.3 via Theorem 1.4, and
multiplies: **total expected cost = per-attempt cost × P0⁻¹ = p^{1/3+o(1)}**.
Correctness (non-scalarity via inseparable degree p, which is not a square) is
one short final paragraph. No lemma secretly does two jobs; no assembly step
hides a new mathematical claim.

**Profile rule.** Proofs in this repo are decomposed into single-responsibility
lemmas — size bounds, runtime, correctness (conditioned on the explicit
smoothness/structural condition), success probability (conditioned on the
named heuristic) — with the main theorem restricted to assembly and to
explicit bookkeeping of per-attempt cost × inverse success probability.

### A4. New structural ingredient converted into an algorithm

The enabling step is an *external, very recent* mathematical result — the
minimal-degree bound of [4] (Theorem 1.5) — converted into an attack through
two generic moves: smoothness splitting (a B-smooth degree factors as
φ = η ◦ ψ with both factors of degree ≈ (p/2)^{1/6}) and meet-in-the-middle
claw finding over the keyed table L. The prior art ([24, 26]) already used
Frobenius conjugates but treated finding E → E^{(p)} as the bottleneck; the
new structural fact is what breaks that bottleneck.

**Profile rule.** A target-class direction names its new structural ingredient
(an external theorem, a new invariant, a new correspondence) and states the
generic algorithmic conversion (splitting, meet-in-the-middle, reduction,
rerandomization) that turns it into a complexity gain. "We tried harder on the
old method" is not a structural ingredient.

### A5. Re-randomization to the average case

The smoothness condition holds only with probability P0 for a given curve, so
Algorithm 3 re-randomizes: a non-backtracking random walk ω : E → E′ of length
n in the 2-isogeny graph, with the mixing justification cited explicitly
(n = O(log p), following [37] or the more explicit [6, Lemma 14]) so that E′
is indistinguishable from uniform. On success, the solution is pulled back
through the walk: ω̂ ◦ ϕ ◦ φ ◦ ω ∈ End(E), with non-scalarity preserved.

**Profile rule.** Worst-case-to-average-case rerandomization is a first-class
proof component: the walk, its mixing-time bound with citation, and the
pullback map are all stated explicitly, not left as "repeat until success".

### A6. Reduction-network cascade

One core result is proved (OneEnd, Problem 2.2); the remaining impact is
obtained by *citing published polynomial-time reductions*: Corollary 1.2
covers EndRing (Problem 2.3) and Isogeny (Problem 2.4) via [35, Theorem 1] and
[35, Proposition 8.5], inside the reduction network built by [23, 45, 35, 33].
The paper proves one thing and routes the rest through the literature.

**Profile rule.** Prove the single hardest core statement; obtain adjacent
results by citing verified polynomial-time reductions. Do not re-prove what a
cited reduction already gives, and do not claim an adjacent problem without
naming the reduction that carries it.

### A7. Experimental heuristic validation and transfer assumptions

Section 4.2 validates Heuristic 1 empirically at large parameters and states
the transfer assumptions used by the sampling method:

- **Method.** Direct computation of the smallest isogeny E → E^{(p)} is
  infeasible at large p, so the Deuring correspondence is used as a sampling
  oracle: random maximal orders O in B_{p,∞} are sampled uniformly up to
  conjugation; the two-sided ideal P of reduced norm p is isometric to
  Hom(E, E^{(p)}) with quadratic form Nrd/p; the shortest vector's norm is the
  degree of the smallest isogeny. The norm is factored and its largest prime
  factor recorded.
- **Scale.** p = 5·2^248 − 1 (SQIsign NIST-I) with 100,000 samples;
  p = 27·2^500 − 1 (NIST-V) with 10,000 samples.
- **Comparison.** The empirical CDF of the log of the largest prime factor is
  plotted against the Dickman–de Bruijn prediction ρ(u) ∼ u^{−u(1+o(1))},
  u = log(p/2)/(3x) (Figures 1 and 2), including a zoom on the 500 smoothest
  samples.
- **Tail consistency checks.** For p = 5·2^248−1 the smoothest of 100,000
  samples is 12589-smooth; predicted probability ρ(u) ≈ 1/69232 — consistent.
  For p = 27·2^500−1 the smoothest of 10,000 is e^23-smooth; predicted
  ρ(u) ≈ 1/3312 — consistent.

**Profile rule.** Every heuristic a target-class result depends on gets a
dedicated validation experiment at a declared scale, with the sampling method
(including any correspondence used to reach that scale), the sample sizes,
the distributional prediction being compared against, explicit tail checks,
and all transfer assumptions recorded as artifacts.

### A8. Concrete-cost and scope honesty

The paper is explicit about what the asymptotic does and does not deliver:

- **Rough concrete-cost table** (§4.1) at standardized parameter sets, built
  from a stated cost model (M = Ψ(X, B)·X table entries, one F_{p^2}-operation
  per entry as a conservative underestimate, time ≈ M/P0, memory ≈ M, B
  optimized for time):

  | log2(p) | time (F_{p^2}-ops) | memory | previous methods |
  |---|---|---|---|
  | ≈ 256 (SQIsign NIST-I) | ≥ 2^106.5 | ≥ 2^92.5 | ≈ 2^128, negligible memory |
  | ≈ 384 (SQIsign NIST-III) | ≥ 2^157.5 | ≥ 2^138.6 | ≈ 2^192, negligible memory |
  | ≈ 512 (SQIsign NIST-V) | ≥ 2^204.2 | ≥ 2^181.3 | ≈ 2^256, negligible memory |
  | ≈ 576 | ≥ 2^230.9 | ≥ 2^206.0 | ≈ 2^288, negligible memory |
  | ≈ 768 | ≥ 2^302.4 | ≥ 2^272.2 | ≈ 2^384, negligible memory |

- **Flagged optimism.** The estimates "make optimistic assumptions on the
  actual cost of certain steps, hence should not be interpreted as accurate
  predictions" (§1.1); both directions of error are named (table cost
  underestimated; 1/P0 possibly overestimated per Remark 1).
- **Hidden-overhead disclosure.** The o(1) hides a *superpolynomial* overhead,
  "much larger than the previous (log p)^{O(1)} cofactor" (§1.1).
- **Memory honesty.** Memory is essentially as large as the time
  p^{1/3+o(1)}; the claw-finding structure of the problem is named as the
  obstruction.
- **Time–memory tradeoff and parallelization.** van Oorschot–Wiener [43]
  gives time √(N³/w) = p^{1/2+o(1)}/w^{1/2} with memory w, interpolating
  between the new algorithm and the classic p^{1/2+o(1)} polynomial-memory
  algorithms [21]; with n parallel processors the time is
  p^{1/2+o(1)}/(w^{1/2}·n). Quantum considerations are pointed to [29].
- **Scope statement.** Affected: CGL hash [14], the SQIsign family
  [7, 19, 20, 22, 34], GPS [28], PRISM [5], ⊗-MIKE [39]. Explicitly safe
  (other cryptanalytic algorithms dominate): CSIDH [13], (qt-)Pegasis
  [17, 18], M(D)-SIDH [25], FESTA [9], POKE [8]. The attack is stated as "not
  a complete break" warranting parameter reevaluation.
- **Referenced proof-of-concept implementation** [36] (SageMath, by Panny),
  with a public URL.

**Profile rule.** No asymptotic claim is promoted in this repo without a
concrete-cost table at standardized parameter sets, a stated cost model,
explicitly flagged optimistic assumptions, disclosure of overhead hidden in
o(1)/polylog terms, memory accounting, time–memory tradeoffs, and an explicit
affected-vs-safe scope statement.

## Part B — Proof architecture standard

Results produced inside this repository (theory notes, derivation artifacts,
and any internal theorem-level claims) must follow the exemplar's
decomposition. A result write-up at target class contains:

1. **Problem statement(s).** Named, numbered problems (cf. Problems
   2.2–2.4), with input encoding and what constitutes a solution.
2. **Heuristics, numbered and standalone.** Each heuristic states the
   probability distribution claimed, the uniformity range, and its
   justification as rigorous-bound × classical-distribution-theorem (cf.
   Heuristic 1 = Theorem 1.5 × Theorem 1.4). Heuristics are inputs to
   theorem statements, never smuggled into proofs.
3. **Single-responsibility lemmas.** Each lemma does exactly one of:
   - *size bound* — how large is the search structure (cf. Lemma 3.2);
   - *runtime* — what one execution costs (cf. Lemma 3.3);
   - *correctness* — the algorithm returns a correct object *under an
     explicitly stated condition* (cf. Lemma 3.4, conditioned on B-smoothness;
     the degree-split inequality is proved, not asserted);
   - *success probability* — how often the condition holds *under a named
     heuristic* (cf. Lemma 3.5), with remarks recording known slack (cf.
     Remark 1).
4. **Numbered algorithms with Require/Ensure** (cf. Algorithms 1–3), so that
   each lemma binds to a specific algorithm and the proof text can reference
   line-level behavior.
5. **Assembly-only main theorem.** The main theorem chooses parameters,
   computes per-attempt cost and per-attempt success probability from the
   lemmas, and writes the bookkeeping explicitly:
   `total expected cost = per-attempt cost × P0⁻¹`. Correctness of the
   assembly is one short argument citing the correctness lemma.
6. **Re-randomization, when used, is explicit.** Walk definition, mixing-time
   citation, and pullback map (cf. Algorithm 3).
7. **Cascade by citation.** Adjacent problems are covered by named published
   reductions (cf. Corollary 1.2), each with its heuristic dependencies
   restated.
8. **Cost and scope section.** Concrete-cost table, cost model, flagged
   optimism, memory, tradeoffs, scope, and — where feasible — a referenced
   proof-of-concept implementation.
9. **Heuristic-validation experiment.** Per A7, as a first-class evidence
   artifact (see Part D).

Within this repository's machinery, internal write-ups remain *derivation*
artifacts under the refutation-artifact discipline of
`docs/claims-and-verification.md` — checkable arguments, labeled
`derivation`, never "proved" — unless routed to an external proof assistant
or human referee. The architecture above is the standard those derivations
must meet; it does not change their epistemic label.

## Part C — Profile checklist

Apply this checklist to any proposed hypothesis, direction, or claimed result.
Roles: the Idea Generator self-checks before proposing; the Reviewer and Red
Team score against it; the Coordinator uses it when classifying a direction as
target-class. A "no" does not reject the work — it classifies it as
non-target-class (engineering, cofactor-level, or exploratory), which affects
how it may be presented and promoted.

**Ambition**

- C1. Does the result change the asymptotic exponent (or a comparably central
  structural barrier) of a named, central hard problem — with the previous
  best complexity stated and cited? (A1)
- C2. Is the improvement distinguished from constant-factor,
  implementation-level, and logarithmic-cofactor gains? (A1)

**Conditional rigor**

- C3. Is every heuristic numbered, standalone, formally quantified, and stated
  with its uniformity range? (A2)
- C4. Is each heuristic justified by a rigorous bound composed with a
  classical distribution theorem, both cited? (A2)
- C5. Do all theorem statements carry their heuristic dependencies by name,
  and do corollaries inherit them? (A2, A6)

**Architecture**

- C6. Is the proof decomposed into single-responsibility lemmas (size /
  runtime / correctness-under-condition / success-probability-under-heuristic)?
  (A3)
- C7. Are algorithms numbered with Require/Ensure, and does each lemma bind to
  a specific algorithm? (A3)
- C8. Does the main theorem merely assemble, with explicit
  per-attempt-cost × inverse-success-probability bookkeeping and no hidden new
  claims? (A3)
- C9. Is the new structural ingredient named, external or novel, with its
  algorithmic conversion stated? (A4)
- C10. If rerandomization is used, are the walk, mixing bound (with citation),
  and pullback explicit? (A5)
- C11. Are adjacent problems obtained by named polynomial-time reductions
  rather than re-proof or bare assertion? (A6)

**Evidence and honesty**

- C12. Is there a heuristic-validation experiment at the largest feasible
  scale, with sampling method, sample sizes, distributional prediction, and
  tail consistency checks recorded as artifacts? (A7)
- C13. Is there a concrete-cost table at standardized parameter sets with a
  stated cost model? (A8)
- C14. Are optimistic assumptions, o(1)/polylog-hidden overheads, and memory
  requirements explicitly disclosed? (A8)
- C15. Are time–memory tradeoffs and parallelization behavior stated? (A8)
- C16. Is there an explicit affected-vs-safe scope statement naming which
  systems or parameter regimes the result does and does not threaten? (A8)
- C17. Are the tested parameters, transfer assumptions, and extrapolations
  explicit in the evidence supporting the claim? (A7)
- C18. Is a proof-of-concept implementation referenced or planned, with its
  fidelity limits stated? (A8)

Scoring guidance: C1–C2 classify ambition; C3–C11 classify proof maturity;
C12–C18 classify evidence readiness. A direction may be *proposed* with gaps,
but a hypothesis may not be marked `approved` for target-class promotion with
C3–C5 unresolved, and may not reach `supported` without C12–C16.

## Part D — Mapping onto repository machinery

The profile is not a parallel process; it binds to the existing contract.

### Hypothesis states

Per AGENTS.md, hypotheses move
`proposed → specified → approved → running → analyzed → replicated → supported | weakened | rejected | inconclusive | superseded`.
The checklist attaches to transitions:

- `proposed → specified`: the specification names the target problem, the
  previous best complexity, the structural ingredient (C1, C9), and drafts
  the heuristic statements (C3, C4).
- `specified → approved`: heuristics are formally stated with justifications
  (C3–C5); the planned proof decomposition follows Part B (C6–C8); the
  validation experiment and the concrete-cost analysis are *planned with
  budgets* before execution (C12, C13), consistent with the experiment
  contract (controls, metrics, budgets, stopping rules, artifacts) required
  by AGENTS.md rule 3.
- `analyzed → replicated → supported`: requires completed heuristic-validation
  runs at the largest feasible scale (C12) and the concrete-cost table (C13),
  each independently verified per the verification rules in
  `docs/focused-autoresearch-loop.md` (a positive result cannot spawn
  expansion before an independent verifier passes).
- Adverse transitions (`weakened`, `rejected`) follow the refutation-artifact
  discipline of `docs/claims-and-verification.md`: a heuristic failure
  observed at scale is a *scoped* negative result (AGENTS.md rule 6) — it
  closes exactly the tested distribution, parameters, and sample sizes, and
  is recorded in the mandated negative-result phrasing of
  `docs/evidence-and-reproducibility.md`.

### Evidence classes and artifacts

The profile adds two first-class artifact classes to the reproduction package
of `docs/evidence-and-reproducibility.md`:

1. **Heuristic-validation experiment.** An experiment whose hypothesis is a
   named heuristic (not an algorithm). Required artifacts, beyond the standard
   package: the sampling method and any correspondence used to reach scale
   (cf. Deuring correspondence in A7); instance-generation and seed policy;
   sample sizes; the exact distributional prediction compared against (e.g.,
   Dickman–de Bruijn ρ(u) with the u-parameterization stated); CDF data in
   machine-readable form; and tail consistency checks on extreme samples.
   Claim-tier metadata and the record's tested parameters remain explicit, but
   a validation run is not automatically barred from supporting a broader
   conditional interpretation.
2. **Concrete-cost table.** A required artifact *before any asymptotic claim
   is promoted* past `analyzed`. It must state: the cost model (what is
   counted, at what unit cost); standardized parameter sets; time and memory
   for the new result *and* the previous best, under matched accounting;
   flagged optimistic assumptions; overhead hidden in o(1)/polylog terms;
   time–memory tradeoffs and parallelization; and the affected-vs-safe scope
   statement. An asymptotic claim without this artifact is incomplete
   evidence and blocks promotion — an evidence-integrity failure, not a
   mathematical result.

### Claim-tier reporting

The profile requires claim-tier metadata, tested parameters, and transfer
assumptions to be visible in every evidence record, synthesis, and ledger
entry. Empirical heuristic validation remains conditional on the heuristic;
records must keep the conditional phrasing ("Assuming Heuristic H, ...") in
every evidence record, synthesis, and ledger entry, exactly as Theorem 1.1 and
Corollary 1.2 carry "Assuming Heuristic 1".

### Review routing

Per AGENTS.md rule 12, any claim proposed as a breakthrough or contradiction
of established evidence requires independent `review-xhigh` review. A claim of
target-class form (C1 answered "yes") is automatically in that category: the
Reviewer checks the decomposition against Part B, the Red Team attacks the
heuristic justification (C3–C5), the cost model (C13–C15), and the scope
statement (C16), and the Validator checks the heuristic-validation experiment
    integrity (C12) and the claim-tier report and transfer assumptions.
