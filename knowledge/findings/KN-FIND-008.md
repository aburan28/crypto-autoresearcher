---
id: KN-FIND-008
type: internal_finding
title: Rare-event density gates are settled exactly by fibering over solutions — and exactness does not protect against formalisation error
tags: [methodology, lifting, xedni, function-field, elliptic-surface, rare-event, exact-enumeration, experiment-design, ecdlp, toy-scale]
confidence: established
proof_status: derivation
proof_refs:
  - experiments/EXP-XEDN-002/derivation.md
  - experiments/EXP-XEDN-002/analysis.md
  - coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-234/validation_notes.md
  - coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-235/objections.md
internal_refs: [EXP-XEDN-002, H-XEDN-001, RQ-XEDN-001, EV-XEDN-001, DEC-20260724-008, RUN-XEDN-002-B]
claim_tier: toy
added: 2026-07-24
superseded_by: null
---

## The methodological finding

A "density gate" of the form *estimate `P(p) ~ p^{-α}` by sampling objects and
testing a predicate, then promote iff `α` is small* is unrunnable whenever the
true `α` is large: the sample size needed to see a single hit grows like `p^{α}`.
`EXP-XEDN-001` phase 2 was contracted this way — fit `α` at `p ∈ {101, 211, 431,
809}` with 40 runs and 14400 seconds — against a rate near `p^{-3}`, i.e. about
`10^{-6}` at `p = 101` and `2·10^{-9}` at `p = 809`. Its `p = 101` smoke observed
0 hits in 5760 slots; the exact expected count for that smoke is **0.00274**, so
the observation was uninformative about `α` by construction, not by bad luck. The
route sat unresolved for that reason alone.

The repair is to stop sampling the *ambient* space and instead **enumerate the
incidence set by fibering over the solution parameter**. Here the predicate is
"`x(t)^3 + b(t)` is a square", so instead of drawing `b` and testing, one draws
the section `y` and *defines* `b := y^2 − x^3`. That is a bijection onto the same
hit set, so it answers the same question — but the rate becomes a count, and the
count has a closed form:

```
N_slots(p) = (p-1)·p^8
N_hit(p)   = p^2·(p^4 − 3p^3 + 2p^2 + p − 1)/2
P_lift(p)  = (1 − 2/p + p^-3) / (2p^3)      [exact identity, α = 3, constant 1/2]
```

Verified by full brute force over the complete slot space at `p = 5, 7`, and
independently re-derived symbol-for-symbol by a validator who wrote the formula
down before reading the executor's derivation. Runtime: seconds.

**Generalisable rule.** Before contracting a density gate, compute the codimension
of the predicate in the parameter space. If it is `c`, the rate is `Θ(p^{-c})` and
sampling needs `Ω(p^{c})` draws; if the incidence set is parametrisable, enumerate
it instead and the answer is exact. A gate whose promotion threshold sits below
the predicate's codimension cannot be reached by sampling at any budget the
contract can afford.

## The equally important negative lesson

An exact count removes **sampling** error. It removes no **model** error, and in
this case model error dominated the result:

- The frozen family had `a(t) = 0`, hence `j = 0` throughout, hence was
  **iso-trivial** in the standard sense — exactly the class the originating
  research direction (candidate B2) had explicitly excluded, and exactly the
  exclusion the hypothesis listed among its own assumptions. Applying the
  contract's "detect and exclude iso-trivial surfaces" constraint would have
  emptied the family.
- The multi-section clause counted **distinct** sections of one degree shape as a
  proxy for **independent** sections; on an in-family `p = 13` surface the counted
  sections form `μ_3` orbits whose specialised relation is a tautology.
- The measure was **uniform on the family**, while the attack being modelled
  *constructs* its surface through prescribed points: building an in-family
  surface with a prescribed target fibre and section succeeded 10201/10201 times
  at `p = 101`, against a uniform per-slot rate of `4.76·10^{-7}`.
- The exponent `α = 3` is the naive square-density codimension count and is **not**
  the classical Jacobson–Koblitz–Silverman–Stein–Teske prediction, which concerns
  relation-coefficient growth (`KN-LIT-021`). The counted sections turn out to be
  height-2 roots of the `E_8` Mordell–Weil lattice, so their relation coefficients
  are absolutely bounded — the census measured a different obstruction from the
  one the literature names as binding.

So the exact machinery answered its question perfectly and still did not close the
research direction. **Two cheap pre-freeze checks would have caught this:** (1)
check the candidate family against the classes the source direction excluded; (2)
check that the measured probability is taken under the measure the attack induces,
not under the uniform measure that is convenient to enumerate.

## Scope

Toy scale; one surface family (`y^2 = x^3 + b(t)` over `F_p`, `deg b = 6`), one
section shape (`x` monic of degree 2, `deg y ≤ 3`), one square predicate, `p ≤ 809`
by closed form and `p ≤ 13` by enumeration. The methodological rule is general; the
numbers are not. Nothing here closes function-field xedni, candidate B2, or lifting,
and nothing here supersedes the audited-route records `ECFG-P1543` or `ECFG-P1547`.
