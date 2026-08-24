# Lever additions beyond L1–L5

**Task:** TASK-20260805-85af9d · **Goal:** GOAL-SSIQ-001 · **Batch:** BATCH-001
**Basis:** `exponent_budget.md` (corrected factor table) and
`target_conditions.md` (the arithmetic). **Compute used:** none.

`ledger/goals/GOAL-SSIQ-001/goal.yaml` carries `lever_completeness_disclaimer`:
`L1`–`L5` is an opening enumeration, not a proof of exhaustiveness, and
producers are explicitly asked to add. This file adds **five routes (A1–A5)**
and **one anti-lever register (A6)**, then records **what was looked for and not
found**.

Each addition follows the goal record's own shape: *the statement that would
have to be true*, and *the nearest obstruction to audit first*. Naming an
obstruction to audit first is not a verdict on the route — under
`docs/inventor-protocol.md` a failed audit is frequently the useful result, and
premature closure is a failure mode symmetric with overclaiming.

**None of the following states, implies, or is arranged to suggest that a
`p^{1/4}` algorithm exists, is likely, or is near.** They are routes to *a lower
exponent*, enumerated so that the map is honest about its own gaps.

---

## Coverage check: where L1–L5 act, and what is left uncovered

Using the symbols of `target_conditions.md` §1 (`T = c·q·d/k + r`):

| symbol | factor | covered by |
|---|---|---|
| `d` | F1 degree bound | L1, and L4 via a different object |
| `q` | F3 list cardinality | L2 |
| `c` | F7 collision cost | L3 |
| `r` | F4 success probability | — (excluded: `r ≥ 0`) |
| **`k`** | **F2 split arity** | **NOTHING** |
| memory at fixed `T` | — | L5 (recorded as not serving the time target) |

Two gaps fall out immediately: **`k` has no lever at all**, and **`c`'s lever
(L3) has an unstated prerequisite** that `target_conditions.md` §3.4 shows is
binding. Those are A1 and A3. A2, A4 and A5 come from requirements the existing
levers state incompletely or from a cost model none of them enters.

---

## A1 — Split arity: `k ≥ 3`

**Targets:** `k` (factor F2). **Not covered by L1–L5:** no lever targets the
arity. L3 is adjacent but different — L3 keeps the two-way split and asks for a
better search *within* it; A1 changes the arity and thereby the *list size*, and
only then asks about the search.

**Arithmetic payoff (from `target_conditions.md` §3.3, §5).** `T = c·q·d/k + r`.
At `c = 1` an integer `k = 3` gives `T = 2/9`, `k = 4` gives `T = 1/6`; exactly
`1/4` needs the non-integer `k = 8/3`. Rows 4–5 of `target_conditions.md` §5 show
the same arithmetic lets a *worse* degree bound (`d = 3/8` with `k = 3`, or
`d = 1/2` with `k = 4`) reach the same total — so `k` and `d` trade.

**The statement that would have to be true.** For some integer `k ≥ 3`:

- **(i)** every `B`-smooth integer `≤ D` admits a factorisation into `k` factors
  each `≤ (B·D)^{1/k}` — the `k`-fold analogue of the balance chain at line 181;
  **and**
- **(ii)** the resulting `k`-way collision problem is solvable in time
  `(per-list cardinality)^{1+o(1)}`, i.e. `c = 1` at arity `k`.

**Nearest obstruction to audit first: the anchor.** At `k = 2` the "second list"
is not a second list. Algorithm 2 stores **one** table and queries it at the
Frobenius conjugate of each codomain — line 171: *"if (E′)^{(p)} is the key of
an entry ((E′)^{(p)}, χ) ∈ L then"*, justified at line 183 by
`χ = η̂^{(p)}` having domain `E^{(p²)} = E`. The involution on codomains is what
anchors both halves to the same known object. **For `k ≥ 3` the `k − 1`
intermediate curves are unknown, and this text states no analogous anchor**
(`exponent_budget.md` §6.5: the frozen text contains no `k ≥ 3` split at all).
Audit (i) and (ii) **separately**: (i) is a cheap question about divisors of
smooth numbers and is likely the easy half; (ii) is where the whole route lives,
and assuming `c = 1` at `k ≥ 3` assumes the question.

**Nearby-object control (required before belief).** Run any proposed `k`-way
search against a structure-free surrogate of the same shape — `k` lists with no
conjugation relation. If it succeeds there, it is not using the structure, and
the observed speedup is an artifact.

---

## A2 — Relation family: enlarge the *target*, not the *degree*

**Targets:** `d` (factor F1), by changing the object rather than improving the
bound. **Coverage:** L1 mentions *"or to another cheaply-recognisable auxiliary
target"* in a parenthesis, but frames its requirement solely as a degree bound.
A2 names the **three** separate requirements — and supplies a free refutation of
the most likely failure mode, which L1 does not.

**The statement that would have to be true.** A family `R` of relations on pairs
of supersingular curves such that:

- **(i)** membership `(E′, E″) ∈ R` is testable in `p^{o(1)}` per codomain, so
  `R` can serve as the table key exactly as Frobenius conjugation does at line
  171;
- **(ii)** every supersingular `E` — or a `p^{-o(1)}` fraction of them, since
  Algorithm 3 re-randomises — admits an `R`-related target reachable by an
  isogeny of degree `≤ p^{d′}` with `d′ < 1/3`;
- **(iii)** the resulting composition still yields a **non-scalar** endomorphism.

**Nearest obstruction to audit first: does `R` lower `d′`, or only multiply
successes at the same `d′`?** Only the first moves the exponent, and **the source
has already answered the second case**. Remark 1, line 191: *"there are
generally multiple small (non-cyclic) isogenies E → E^{(p)}, and it is
sufficient for any one of them to be smooth ... While practically relevant, this
phenomenon is absorbed in the hidden term of the asymptotic complexity."*
Multiplicity at fixed degree scale is an `r`-effect, and `r` is exponent-free
(`target_conditions.md` §3.5). So the audit is one question, answerable before
any implementation: **is the proposed family a degree-bound improvement, or a
multiplicity improvement in disguise?**

**Second obstruction, easily forgotten: requirement (iii) is not automatic.** The
source's non-scalarity argument is specific. Line 220: *"ϕ ◦ φ ∈ End(E′), and it
has inseparable degree p (which is not a square), so it cannot be in the subring
Z."* A different relation `R` must supply its own reason that the composition
escapes `Z`; without it the algorithm can return a scalar and solve nothing.

---

## A3 — Non-materialised family representation (the unstated prerequisite of L3)

**Targets:** `c` (factor F7), and simultaneously the memory accounting.
**Coverage:** L3 asks for *"a sieve or index-calculus-style search below list
cardinality"*. `target_conditions.md` §3.4 shows that **within the algorithm as
written, `c < 1` has no admissible solution**: memory cannot exceed time, the
table is materialised before it is searched (line 158), so `T ≥ M = q·d/k`
regardless of `c`. And if `q·d/k` has already been lowered by a `d`/`q`/`k`
movement, `c = 1` already suffices and `c < 1` buys nothing. L3 therefore
carries a prerequisite it does not state.

**The statement that would have to be true.** A representation of `L(E,X,B)` — or
of a sub-family — supporting the query *"does this family contain an entry whose
codomain is the Frobenius conjugate of this codomain?"* in time sublinear in the
family cardinality, **without materialising the family**, so that both the build
cost of line 158 and the stored memory fall below `q·d/k`.

**Nearest obstruction to audit first: line 158 makes the build cost dominant by
construction** — *"The cost of computing the list is thus at most
#L · (B + log p)^{O(1)} ... The cost of the final loop through the table L is
dominated by that previous computation."* And the only structure the text exposes
on codomains is the modular-polynomial relation (line 156), which is a **local,
one-step** relation on `j`-invariants. The audit: name the query primitive
explicitly and show it does not reduce to walking the graph — a primitive that
must enumerate the walk to answer has not avoided materialisation, it has only
avoided storing.

**Two obligations if the audit passes.** (a) L3's own nearby-object control
applies: the same primitive on a structure-free surrogate must **fail**.
(b) The memory accounting of `exponent_budget.md` §3.4 no longer holds — `M` is
no longer `q·d/k` — so any such result must state its own memory from scratch,
per `docs/claims-and-verification.md` ("memory complexity stated beside time,
always").

---

## A4 — The correlation condition for restricted families (sharpening L2's instrument)

**Targets:** `q` (factor F3). **Coverage:** L2 owns this lever. What A4 adds is
**the null outcome of L2's own proposed measurement**, which L2 does not name —
and an unnamed null is how a break-even measurement gets read as a signal.

**The statement that would have to be true** (from `target_conditions.md` §4): a
restriction `F ⊆ L(E,X,B)` with `|F| = X^{2−δ}` whose hit-probability loss
exponent `e` satisfies

```
e = δ − 1/2
```

i.e. `F` must be **positively correlated with the sought `ψ`**, containing it
with probability `X^{1/2}` times `F`'s own density in the list.

**Nearest obstruction to audit first: the two natural nulls are already
computed, and both are non-results.** Because *both* `ψ` and the conjugated `χ`
must be table entries (line 185), membership is a two-event conjunction:

| model | `e` | resulting `T` |
|---|---|---|
| independent membership | `2δ` | `(2+δ)/6` — **strictly worse than 1/3** for every `δ > 0` |
| aligned (`ψ ∈ F ⟹ χ ∈ F`) | `δ` | `1/3` — **exact break-even, for every `δ`** |

L2 currently proposes *"a toy measurement of that exchange rate"*. The equation
says a measured rate of `e ≈ δ` or `e ≈ 2δ` **is the null**, not a finding.
**Pre-register both nulls before the measurement** — otherwise the alignment
outcome, which returns exactly the baseline `1/3`, is indistinguishable from a
success at the level of the raw exchange rate.

*(The two-event model here is this task's bookkeeping device. The frozen text
says nothing about restricted families; see `exponent_budget.md` §6.)*

---

## A5 — Amortised / multi-instance cost model

**Targets:** none of `c, q, d, k, r`. It changes the **cost model** rather than
the exponent inside it. **Not covered by L1–L5:** all five are single-instance
exponent levers.

**The statement that would have to be true.** A precomputation depending on `p`
alone, of size `p^{e}`, after which each subsequent OneEnd instance over the same
`p` costs `p^{T′+o(1)}` with `T′ < 1/3`.

**Nearest obstruction to audit first: instance-dependence of both the table and
the target.** The list is rooted at the instance — Definition 3.1, line 131:
*"L(E, X, B) = {ψ : E → E′ | ψ has cyclic kernel and deg(ψ) ∈ S(X, B)}"* — and
the match target `E^{(p)}` is likewise instance-dependent (line 171). A
precomputation must be indexed by something that does not depend on `E`, and the
audit is to name that index before anything else.

**Second obstruction, of record-keeping rather than mathematics.** This is a
**different cost model from the source's**, which is single-instance *expected*
time (line 19). `exponent_budget.md` §6.7 records that the frozen text contains
no amortised precomputation — the sole occurrence of "precompute" (line 200)
concerns the parameter `B`. Any result in the amortised model must state the
model change explicitly and **may not be compared to `p^{1/3+o(1)}` without it**.
Stated plainly: **A5 does not lower the single-instance exponent, and nothing
here suggests it does.**

---

## A6 — The exponent-free register (an ANTI-lever, recorded so it is not re-proposed)

**This is not a route.** It is the complementary set, recorded because the goal
record's disclaimer cuts both ways: as no later record may read *"not in L1–L5"*
as *"not a route"*, no later proposal should have to rediscover that these are
not routes.

**Exponent-free set:** `F4` (inverse success probability), `F5` (smoothness
parameter `B`), `F6` (walk length `n`), `F8` (per-step modular-polynomial
arithmetic), and the retry count. Each is `p^{o(1)}`
(`exponent_budget.md` §2.2, §4).

> Any proposal whose **entire** saving lands in this set moves the disclosed
> `o(1)`, not the exponent. For `F4` this is forced rather than observed:
> `r ≥ 0` because `P0` is a probability, so `T = 1/4` would need
> `P0 = p^{1/12} > 1` (`target_conditions.md` §3.5).

**The mandatory caveat.** "Not an exponent lever" is not "worthless". The source
says the opposite about the practical dimension — Remark 1, line 191: *"While
practically relevant, this phenomenon is absorbed in the hidden term of the
asymptotic complexity"* — and line 156's footnote says the unoptimised `O(1)` is
*"of course critical for a practical deployment of the algorithm."* Concrete-cost
consequences belong to GOAL-P13-001 (`EV-PEC-2e67ff`, `EV-PEC-857664`), cited
here and not re-derived.

---

## What was looked for and NOT found

Recorded per the handoff's requirement that an empty or partial finding name its
search. Each entry states where it was looked for.

1. **A lever on the reductions behind Corollary 1.2.** Line 21 calls
   `[35, Theorem 1]` and `[35, Proposition 8.5]` *"the computational
   reductions"*. If they are polynomial-time they carry exponent 0 and offer no
   lever; this task has **not verified their cost** and they are
   CITED-NOT-VERIFIED (`exponent_budget.md` §5). **No lever found**, and no
   exponent assigned to them anywhere in this package.

2. **A lever exploiting a special form of `p`.** Looked for in the statements of
   Theorem 1.1, Lemma 3.3, Lemma 3.5 and Heuristic 1 — all uniform in `p`. The
   specific primes `p = 5·2^248 − 1` and `p = 27·2^500 − 1` appear only at line
   248 as sample points for the Heuristic 1 experiments, not as algorithmic
   assumptions. **Nothing in the text suggests special primes change the
   exponent, in either direction.**

3. **A lever on Heuristic 1 itself.** Looked for, and the arithmetic rules it
   out as a *lever* while confirming it as a *floor-holder*: strengthening
   Heuristic 1 cannot push `r` below 0, so it cannot lower `T`; a failure of
   Heuristic 1 in the adverse direction gives `r > 0` and **raises** `T`.
   Heuristic 1 can only cost, never gain, in exponent terms. (This is
   bookkeeping about the exponent only. Whether Heuristic 1 holds is
   GOAL-P13-001's question, and by `docs/claims-and-verification.md` no
   experiment at any scale discharges it.)

4. **A quantum time-exponent lever.** Line 41 relays the opposite suggestion for
   the vOW setting: *"suggesting that quantum computation may only be
   advantageous to reduce the amount of memory, with the same time complexity"*.
   **Not found**, and out of this goal's classical `F_{p^2}` framing in any case.

5. **A lever in the correctness argument.** Lines 57 and 220 (the
   inseparable-degree-`p` argument) are exponent-free; they constrain what a
   replacement relation must supply (see A2 requirement (iii)) but offer no
   saving. **No lever found.**

6. **A source-side statement that memory can be reduced without increasing
   time.** Line 39 states the open problem rather than a route: *"It is
   currently unclear how to reduce the memory cost without increasing the
   time"*. That is L5's territory, and L5 is honestly recorded in the goal record
   as not serving this goal's time target. **No addition made.**

7. **A higher-dimensional (Kani-style) enumeration lever.** `exponent_budget.md`
   §6.6: the word "Kani" does not occur and `[11, 31, 38]` are cited at line 111
   for isogeny *interpolation*, not enumeration. A lever of this kind would be
   this program's addition, not a reading of the source — and by the two-sided
   pinning of `q = 2` (Lemma 3.2 above, §4.1 below) a change of *representation*
   alone does not change the *count* of objects to be searched. **Not added as a
   route**, because on the corrected table it has no symbol to move; recorded
   here so the reasoning is on file rather than repeated.
