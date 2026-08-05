# GOAL-SSIQ-001 BATCH-002 — opening

**Goal:** GOAL-SSIQ-001 · **Question:** RQ-SSIQ-9702af · **Opened:** 2026-08-05
**Opened by:** `DEC-20260805-2be965` `next_action` · **Authority:** user direction
this session (`run BATCH-002`).

BATCH-001 closed on a **CLOSED-IN-SCOPE** verdict for lever L1 that rests on a
single derivation-tier pillar, checked four times by **one model**. BATCH-002
exists to attack that from outside.

---

## 1. The one confound BATCH-001 could not touch

Every session in BATCH-001 — both producers, the Validator, the Red Team —
resolved to `claude-opus-5`. Policy aliases do not bind under this harness, so
`review-adversarial`'s `xhigh` floor was never applied and never verifiable.
The Red Team said it plainly: *its own concurrence on D1 is not independent
corroboration of D1*. A shared systematic error would have passed all four
gates.

A fifth re-derivation in the same model cannot fix that. **Measuring the
exponent D1 predicts, against data this program did not generate, can** — it
fails *differently*. That is the whole design rationale for this batch, and it
is why REC-1 was chosen over REC-1b and REC-2, both of which are live and
scheduled behind it.

## 2. What is being measured

`EXP-SSIQ-4de240`, frozen **before** the dataset was fetched, tests
`H-SSIQ-6e0748` on the exhaustive `δ_E` data released with `arXiv:2607.14624`:

| model | `α` in `N(T,p) = c·T^α·p^β` | consequence |
|---|---|---|
| **D1** (ingredient (c) contributes `(np)^{o(1)}`) | **3/2** | L1 stays `CLOSED-IN-SCOPE` |
| **failure mode** (ingredient (c) contributes `n^{1/2}`) | **2** | **reversion fires** — L1 disjunct 2 → `UNRESOLVED`, the `p^{1/4}` degree-bound route reopens |

The gap is an **exponent**, not a constant, which is the only reason a sub-toy
measurement (`log₂ p ≤ 18`, below this question's own toy band) can discriminate
at all. Whether it actually can is itself reported, as `M-RANGE`.

**Success is not agreement.** A run returning `REFUTES-D1-AT-SCALE` with all
controls passing is a fully successful run and the more valuable outcome — it
reopens a lever at exactly the target exponent. The contract says so in its own
`success_criterion` so that no one has to infer it later.

## 3. The control most likely to void this batch

`C-NULL`. The Red Team observed in BATCH-001 that **D1's shape *is* the Gaussian
heuristic for a random ternary lattice**. If a structure-free surrogate — random
positive-definite ternary forms of discriminant `p/4` — reproduces the full fit
including `β` and `c`, then the measurement does not distinguish supersingular
arithmetic from generic lattice geometry, and `M-ALPHA` may not be cited as
evidence about D1 at all. The run is then **void for the primary metric**, and
is not repaired by adjusting the surrogate.

This control exists *because* of that objection. It is expected to be the
hardest one to pass, and it was written into the frozen contract rather than
discovered afterwards.

## 4. The second producer, and why it is in this batch

`REC-2` — cost the `[35]` reduction cascade. `GOAL-SSIQ-001`'s own recorded
defect `GD-1` is that it states its target on the supersingular **isogeny**
problem, reachable only through reductions `[35, Theorem 1]` and
`[35, Proposition 8.5]` that are **not in this repository and have never been
checked here**, while every condition BATCH-001 derived is about **OneEnd**. No
exponent is assigned to those reductions anywhere.

It is blocked on a trivial thing: no PDF text extractor works in this
environment (`pypdf` dies with a `pyo3_runtime` panic). Unblocking it is the
cheapest useful action available, and it runs disjoint from the fit.

## 5. What this batch may not do

- It may not present agreement with D1 as proof of D1. An asymptotic prediction
  agreeing at `log₂ p ≤ 18` is **consistent with**, not evidence for, the
  asymptotic claim — and the contract's own decision rule says "weak
  confirmation, reported as such".
- It may not compute `δ_E` itself if the dataset cannot be fetched. That would
  reintroduce exactly the shared-model dependence this batch exists to escape;
  such a run is worth **less than no run**. Acquisition failure is
  `failed_infrastructure` (AGENTS.md rule 5) and produces no evidence in either
  direction.
- It may not tune the estimator, the windows, or the decision rule to the data.
  All were frozen at `experiments/EXP-SSIQ-4de240/specification.yaml` before a
  single byte was fetched.
- It may not treat `A1`'s (`k ≥ 3`) payoff table as live: the naive `k`-way
  collision costs `c = k−1`, giving `T = 4/9` at `k = 3`, **worse than the
  incumbent**. The requirement reads "beat `c = k−1`".
- It may not move a claim tier, mint a hypothesis beyond `H-SSIQ-6e0748`, or
  assert anything about whether a `p^{1/4}` algorithm exists.

## 6. Evidence-strength cap — unchanged, and unfixed by this batch

Independence is still session-level; the model is still one model. REC-1
substitutes *external data* for model independence on one specific question. It
does not lift the `preliminary` ceiling on this campaign, and no record from
this batch may claim it does.

---

**Batch closes** on: one run package snapshot, one REC-2 snapshot, independent
Validator and Red Team passes, and a Coordinator ledger archive writing
`EV-SSIQ-29fcbb`, `DEC-20260805-be2f87` and the write-once
`checkpoints/BATCH-002.yaml`.
