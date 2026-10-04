# Domination screen — IDEA-20260915-5c407a / H-ICPERF-5f038b / EXP-ICPERF-025a52 v2

**Task:** TASK-20260915-532164 · **Role:** red-team, independent session · **Date:** 2026-09-15
**Goal:** GOAL-ICPERF-e6b6a4 · **Decision ref:** DEC-20260915-674299
**Runs executed:** 0. Nothing was created under `experiments/EXP-ICPERF-025a52/runs/`.
**Write scope:** `coordination/goals/GOAL-ICPERF-e6b6a4/tasks/TASK-20260915-532164/` only.

**Snapshot reviewed:** branch `claude/index-calculus-graph-dag-3linyk`, HEAD
`1852537c02a0f936eb16b61d5e4b7df84eca9742` (*"amend: EXP-ICPERF-025a52 v1->v2 +
CORR-20260915-3965c1 disclosing the in-place edit"*). All four input records are
clean at that commit and the commit is contained in
`origin/claude/index-calculus-graph-dag-3linyk`, so this screen read a committed,
pushed snapshot, not a working tree. `TASK-20260915-60dc73`'s snapshot commit is
`7c3d47ed7`; that dispatch precondition is satisfied.

Companion file: **`sources.yaml`** — every source with `provenance`, `verified_by`,
and the verbatim quote each conclusion rests on. This report cites source IDs;
the quotes live there.

---

## VERDICT

> ### `partially_dominated`

Split by question, because the three questions have genuinely different answers
and collapsing them would misreport all three.

| | Question | Finding | Basis |
|---|---|---|---|
| **Q1** | Has `rho_j` been **measured and reported vs. depth**? | **not found** in covered scope | absence of a search result, *not* novelty |
| **Q2a** | Are the published analyses on the **tree** or the **DAG**? | **on the TREE**, verbatim | `BGJT-Q1` (retrieved) |
| **Q2b** | Does that leave regime **R3** with exponent content? | **NO — dominated by argument, three independent published routes** | `BGJT-Q2`, `GUI-Q1/Q2/Q3` + `CS-Q1`, `F2-Q2/Q3` |
| **Q3** | Is descent memoisation **standard practice**? | **YES, in CADO-NFS**, verbatim source; saving **not quantified** anywhere found | `CADO-Q1/Q2/Q3` (retrieved) |

**What this means for the approval decision.** The half of the line the task card
identified as load-bearing — *"if the analyses are already on the DAG, R3 has no
exponent content and the whole line collapses by argument"* — **resolves in the
card's favour, but by a route the idea's own `dominated_by` field did not
enumerate.** The published analyses are *not* on the DAG; they are on the tree,
exactly as the idea claims. But R3's **exponent content is foreclosed anyway**,
and the foreclosure is in the literature, in one case in the very paper that
writes the tree bound. The implementation budget that this screen was created to
protect **can be protected**: not by abandoning the measurement, but by removing
the only reason given for calling it exponent-relevant.

`partially_dominated` rather than `dominated` because Q1 is genuinely not
answered by anything I could reach, and Q3's *quantification* is not published
as far as I could see. A scoped measurement of `rho_j` for a declared toy rule
remains an un-dominated, if much less interesting, thing to do.

---

## Q1 — Has the distinct-node vs tree-node sharing ratio been measured and reported as a function of depth?

**Answer: not found in the scope I could cover. This is an absence of a search
result and is reported as such, never as novelty (AGENTS.md retrieval policy).**

What I searched and read:

* **kb index (live, 6 sequential queries).** The index answered — IMP-DESIGN-2 is
  cleared for this screen. Configuration `kb/.env → CRYPTO_KB_QDRANT_URL=./.kb-index`.
  Queries: *quasi-polynomial descent / node counts*; *Granger–Kleinjung–Zumbrägel
  fixed characteristic descent*; *CADO-NFS descent memoisation/cache*; *Diem
  recursive decomposition descent depth*; *FFS descent tree cost analysis*;
  *memoisation / caching / shared subproblem / dynamic programming / recursion
  reuse*. The corpus returned the right papers as **abstract-level literature
  notes** (`KN-LIT-2078` = BGJT, `KN-LIT-2804` = GKZ-128, `KN-LIT-3055` =
  Guillevic, `KN-LIT-2459` = Commeine–Semaev, `KN-LIT-3440` = FFS GF(2^809)) and
  **nothing at all** on memoisation/dynamic programming in recursion — that last
  query's top hits were an FHEW/TFHE paper and a `doc:prompt-caching` entry, i.e.
  a genuine corpus gap rather than a near-miss.
* **Full texts read** (`retrieved`): BGJT (arXiv:1306.4244), Guillevic
  (arXiv:1505.07553), the 30750-bit binary record (arXiv:2008.02717), GKZ-128
  (arXiv:1402.3668), GKZ "powers of two descent" (arXiv:1805.00093), CADO-NFS
  `scripts/descent.py` and `sieve/las-descent-trees.hpp`.
* In none of these is a *distinct-vs-occurrence* node ratio reported. The
  quantity that IS reported, in the one place per-level counts appear at all, is
  the **number of polynomials eliminated at each degree** (`F2-Q3`): 1, 1, 1, 1,
  1, 1, 1, 1, 1, 1, 3, 3, 3, 2, 4, 3, 2, 4, 8, 5, 9, 12, 12, 19, 43, 39, 116,
  209, 592 for degrees 1024 down to 13. The paper charges cost **per eliminated
  polynomial**. It does not say whether duplicates were removed before counting,
  and I do not assert that it does.

**The closer finding, which matters more than the absence.** Those reported
counts are the strongest available *indirect* measurement, and they point the
wrong way for the idea. At degree 13 over `F_{2^30}` the descent handled **592**
polynomials; the level pool — monic irreducibles of degree 13 over `F_{2^30}` —
is of order `2^390/13`. The occupancy ratio is ~`10^{-115}`. **`rho_j = 1` to
within any measurable precision, throughout the entire costed region of the
largest published binary-field DL computation.** And the region where the ratio
*could* differ from 1 (degrees ≤ 8) is assigned **cost 0** in that paper's own
cost table (`F2-Q2`), because those logarithms come from precomputation and
non-classical elimination rather than from descent.

**Uncovered for Q1** — named so the Coordinator can scope around it: the FFS
GF(2^809) record (`KN-LIT-3440`, corpus note only — I did not read the paper);
Joux's L(1/4) paper; Adj–Menezes–Oliveira–Rodríguez-Henríquez's characteristic-3
analyses; Diem's Compositio papers; any implementation log or artefact repository
attached to a record computation, where a per-level de-duplication count would
most plausibly live and would most plausibly never be written up.

---

## Q2 — THE LOAD-BEARING ONE. Tree or DAG?

### Q2a — The analyses are on the TREE. The idea's premise is correct.

Verbatim, from the canonical quasi-polynomial paper (`BGJT-Q1`, retrieved, full
text):

> "Each internal node of the descent tree corresponds to one application of the
> algorithm of Proposition 2, therefore each internal node has a cost which is
> bounded by a polynomial in *q* and *k*. **The total cost of the descent is
> therefore bounded by the number of nodes in the descent tree** times a
> polynomial in *q* and *k*. The depth of the descent tree is in *O*(log *k*).
> **The number of nodes of the tree is then less than or equal to its arity
> raised to the power of its depth**, which is (*q*²*k*)^{*O*(log *k*)}."

That is `arity^depth`. It is a tree count, it is an upper bound, and it is the
bound that produces the headline quasi-polynomial complexity. `GKZ-Q1` confirms
the vocabulary is standard ("building up a descent tree, which has the target
element as its root and factor base elements as its leaves").

**So the collapse the task card hoped for does not happen.** The idea is not
wrong about what the literature says. A screen that stopped here would have
reported `not_found` and cleared the contract.

### Q2b — R3 has no exponent content anyway. Three independent published routes.

I did not stop there, and this is the finding.

**Route 1 — BGJT already identified the pigeonhole crossover, prescribed the
remedy, and stated the remedy is complexity-neutral.** Section 6.2, "Practical
improvements" (`BGJT-Q2`, retrieved, verbatim):

> "**Because of the arity of the descent tree, the breadth eventually exceeds the
> number of polynomials below some degree bound.** It makes no sense, therefore,
> to use the descent procedure beyond this point, as the recovery of discrete
> logarithms of all these polynomials is better achieved as a pre-computation.
> Note that this corresponds to the computations of the L(1/4+ε) algorithm which
> starts by pre-computing the logarithms of polynomials up to degree 2. In our
> case, **we could in principle go up to degree O(log q) without changing the
> complexity.**"

Read that against mechanism **M1** of `IDEA-20260915-5c407a`:

> "the level-j node set is drawn from a pool of elements of bounded size … and
> once B^j EXCEEDS that pool size, REPETITION IS FORCED BY PIGEONHOLE."

These are the same sentence. *"the breadth eventually exceeds the number of
polynomials below some degree bound"* **is** the pigeonhole crossover `j*` that
`H-ICPERF-5f038b` freezes in Stage A and pre-registers as prediction P3. It was
published in 2013, in the paper whose tree bound the idea questions, by the
authors of that bound.

And the consequence is drawn there too, in two moves that between them close R3:

1. The **remedy** is to stop descending at the crossover and precompute the whole
   pool. Precomputing the pool costs at most `|pool|`, which upper-bounds the
   *distinct*-node count at those levels. So the algorithm **as prescribed**
   already pays at most the DAG cost in exactly the saturated region — the
   `arity^depth` figure is a loose bound in a theorem, not a cost the prescribed
   algorithm incurs.
2. The remedy is **complexity-neutral**: *"without changing the complexity."*

Therefore: the region where sharing is *forced* is the region the standard
algorithm design already removes from the descent, and removing it is published
as costing nothing in the exponent. Above that region sharing is not forced, and
neither `IDEA-20260915-5c407a` nor `H-ICPERF-5f038b` offers any mechanism by
which it would occur. **R3's exponent claim has no room left to live in.**

`GKZ-Q2` is this prescription in operation: where the level pool was small enough,
*"This automatically provided the logarithms of **all** degree 2 elements over
F_{2^12}"*; where the pool was too large to precompute, degree-2 elements over
`F_{2^24}` were *"eliminate[d] … on the fly"* — i.e. precisely where pigeonhole
does not bite.

**Route 2 — for NFS/FFS special-q descent the phase is already subdominant, so
no saving in it can move the exponent.** From Guillevic (`GUI-Q1`, `GUI-Q2`,
retrieved, verbatim):

> "The NFS algorithm for DL in prime and large characteristic fields has a
> dominating complexity of L_Q[1/3,(64/9)^{1/3} ≃ 1.923]. … This bound gives the
> running time of this fourth step (**much smaller than relation collection and
> linear algebra**)."

> "Barbulescu … gave a tight analysis of the individual DL computation …
> decomposed in three steps: booting (also called smoothing), **descent**, and
> final combination of logarithms. The booting step has an asymptotic complexity
> of L_p[1/3,**1.23**] and the **descent step of L_p[1/3,1.21]**."

The descent step is `L_p[1/3, 1.21]`. It is beaten by the booting step
(`1.23`) *within its own phase*, and the whole phase is beaten by
`L_Q[1/3, 1.923]`. Corroborated independently by the corpus record for
Commeine–Semaev (`CS-Q1`, `kb`, `KN-LIT-2459` — the very reference the idea cites
as `recalled`): individual logarithms in `L_p[1/3, 3^{1/3} ≈ 1.44]` after an
`L_p[1/3, 1.9018]` precomputation. **Two stages bound the descent from above.
Dividing the descent's node count by any factor — constant, or growing with
depth — leaves the NFS-DL exponent exactly where it was.** This route does not
depend on whether the analysis was written on the tree; it depends only on the
descent not being the bottleneck.

**Route 3 — in practice, at record scale, the cost is where there is no sharing
and the sharing is where there is no cost.** From `F2-Q3` and `F2-Q2`
(30750-bit binary record, retrieved): the expensive *classical* descent
processed **exactly one polynomial per degree** at degrees 1024, 672, 466, 130,
106, 64, 45, 40, 38, 35 — the descent at the top is a **path**, and a path has
`rho_j ≡ 1` by definition. The counts only rise below degree 34, and by degree 8
the cost table assigns **0**. The paper's own accounting is bottom-up dynamic
programming over degrees (`F2-Q1`, `F2-Q4`), which already prices a shared
sub-problem once per degree rather than once per occurrence.

### Q2b, stated as the narrowest thing I actually established

> For BGJT-style quasi-polynomial descent, the published complexity bound is
> charged on the descent tree as `arity^depth`, **and** the same paper identifies
> the pigeonhole saturation of the lower levels, prescribes replacing those
> levels by precomputation, and states that doing so does not change the
> complexity. For NFS/FFS special-q descent, the descent step is asymptotically
> subdominant to both the booting step and relation collection + linear algebra.
> In the largest published binary-field record, the costed part of the descent is
> a path and the shareable part is charged zero. On those three grounds, regime
> R3 — `rho_j` growing with depth — carries **no exponent content for any
> published descent family that this screen was able to check**.

I did **not** verify this for Kleinjung–Wesolowski (I read only the abstract),
for Joux's L(1/4) descent, or for Diem's elliptic-curve recursion. See
*Uncovered scope*.

---

## Q3 — Is descent memoisation already standard, and does that make the measurement redundant?

**Answer: the practice is standard and is in the source of a serious
implementation. The *quantification* is not — I found no number anywhere.**

CADO-NFS `scripts/descent.py` (`CADO-Q3`, retrieved) maintains

```python
class LogBase(object):
    def __init__(self, general):
        self.known={}
    def has(self,p,r,side):     return (p,r,side) in self.known
    def get_log(self, p,r,side): ...
    def add_log(self,p,r,side,log):
        self.known[(p,r,side)] = log
```

— a global table keyed on the canonical ideal `(p, r, side)` — and consults it
before an ideal is ever put on the descent todo list (`CADO-Q1`, `CADO-Q2`):

```python
if self.logDB.has(q,-1,0):
    continue
...
ideal = ideals_above_p(p, 1, a, b, side, general)
if ideal.get_log() != None:
    continue
```

with `logDB.add_log(...)` writing logarithms deduced *during* the descent back
into the same table. **That is the memo table of mechanism M3, keyed on a
canonical form, in production.** M3's framing ("common-subexpression elimination,
textbook") is right, and its `dominated_by` paragraph's admission ("serious FFS
and quasi-polynomial-descent implementations cache intermediate logarithms as a
matter of course") is now a verified fact rather than an honest guess.

**Two qualifications I will not smooth over**, both of which leave a sliver of
room:

1. The `visited` set in `sieve/las-descent-trees.hpp` (`CADO-Q4`) is a
   duplicate-**relation** guard, not node memoisation, and is self-described in
   the source as *"an ugly temporary hack"*. CADO's own descent instrumentation
   is a `descent_tree` holding a `forest` of `tree` nodes with `tree_depth` and
   `tree_weight` — i.e. **CADO measures its descent as a tree**, which is a small
   point in the idea's favour on the *instrumentation* side even though the
   *scheduling* side memoises.
2. The todo-file writer in `CADO-Q1`/`CADO-Q2` has no within-file de-duplication
   that I could see: the same `(p, r)` reached from two relations in one level
   may be written twice. So CADO memoises against the **known** set, not
   necessarily against within-level duplicates.

**Does this make the proposed measurement redundant?** For the *engineering*
claim, largely yes — "you should memoise descent" is settled practice and
`EXP-ICPERF-025a52` would be re-deriving it on a toy rule. For the *quantitative*
claim — how much it saves, as a function of depth — I found no published number,
so the measurement is not redundant, merely much less valuable than the idea
presents it, because Q2b has removed the reason to care about the answer.

**Provenance limitation, stated plainly:** I read CADO-NFS from the GitHub mirror
`sethtroisi/cado-nfs@master`. The canonical `gitlab.inria.fr/cado-nfs/cado-nfs`
raw paths 404'd and `api.github.com` returned 403 from this session, so **the
exact upstream revision is not pinned**. Anyone relying on this for a supersession
decision should re-fetch from canonical and pin a commit.

---

## Objections

### OBJ-1 (severity: high) — The idea's `dominated_by` disjunction is not exhaustive, and the missing branch is the one that holds

`IDEA-20260915-5c407a.dominated_by` offers the reviewer exactly two exits: *rho_j
measured and published*, or *analyses already on the DAG*. The actual state of the
literature is a third branch it did not enumerate: **the analyses are on the tree,
the tree bound is known to its authors to be loose in exactly the saturated
region, and closing that looseness is published as complexity-neutral.** A
`dominated_by` field that enumerates the ways a record could die is only as good
as its enumeration; this one would have let a reviewer who checked both named
branches clear the record. Per the instructions binding this role, an unchecked
Pareto exit is a defect — and here the unchecked exit is the live one.

### OBJ-2 (severity: high) — `sota_delta`'s internal target does not exist

The idea's stated honest ceiling is:

> "if regime R3 holds, every internal model charging descent by tree size
> over-charges the attacker by a factor that grows with depth"

I could not find such a model. `GOAL-ICPERF-e6b6a4`'s own record says the descent
column is unmeasured and unclaimed (`ICPERF-Q1`: *"Each is its own batch with its
own frozen contract; none is claimed here"*). The one descent cost model I did
find in the ledger, `IDEA-20260727-002`, charges descent **by yield** —
`T_desc_charged = T_attempt / P_dec(N)` (`YIELD-Q1`) — which is the correct
total-expected-cost form and contains no `B^d` term for memoisation to attack.
**The value proposition of the whole record points at an object that is not in
this ledger.** This does not make the measurement wrong; it removes the stated
reason to rank it.

### OBJ-3 (severity: high) — `C-MEMO-OFF`, the proves-too-much guard, cannot do what the record says it does, and as frozen it will fire on a *correct* instrument

`C-MEMO-OFF` requires `rho_j == 1.0` **exactly**, at every level of every cell,
with the memo table disabled; failure is `F0` and an invalidation rule.

But the frozen metric definitions say `T_j` = level-*j* occurrences **by path
counting**, `U_j` = distinct level-*j* nodes **by canonical form**, and the
descent rule is **deterministic per node** (`H(global_seed ‖ canonical_bytes(t))`).
Under those three frozen facts, `U_j` is a property of the **set of elements
reached** and does not depend on whether a cache is switched on. Turning the memo
off changes how many times each element is *re-solved*; it does not change how
many *distinct* elements exist. So on a correct instrument, memo-off returns the
same `rho_j > 1`, `C-MEMO-OFF` fails, `F0` fires, and the run is declared invalid.

The only reading under which the control passes is that with the memo off the
instrument *also* stops de-duplicating and reports `U_j := T_j` — in which case
the control is **true by construction** and tests nothing about sharing; it tests
only that a flag is wired to two counters.

Either way the control is not the proves-too-much guard the record claims. The
idea's own justification — *"An instrument that reports sharing with its cache off
is measuring itself"* — is the mis-step: under deterministic relation choice,
sharing is a fact about the DAG, not an artefact of the cache. **This is the
cheapest thing in the contract to get wrong and the most expensive to discover
after Stage B, because it is wired to a hard stop.**

### OBJ-4 (severity: high) — the deciding control `C-NULL` is not matched on censoring, and the matching it *does* do is fitted to the run

`C-NULL` is prediction P4's comparator and the record calls it "THE DECIDING
CONTROL". Two problems:

* **Censoring mismatch.** A real node that exhausts `K_try` is a descent failure:
  it is excluded from `rho_j`, and its entire sub-tree never exists. The null is a
  pure branching process with **no failure mode at all**. Failures concentrate at
  the deepest levels — exactly where P4 is evaluated ("at the deepest level common
  to both"). So real and null are compared under different censoring, in the one
  place the comparison decides anything. *Required:* apply the measured per-level
  failure rate to the null, or report both censored and uncensored nulls.
* **Fitted comparator.** The null takes "the per-level branching-factor
  distribution **measured from the real run**". That is the right instinct for a
  matched null, but it means the null inherits any structure in the branching and
  can only ever test *residual* concentration. Worth stating in the contract, not
  as a defect but as the precise thing P4 can and cannot see.

Also: **P4 and F3 leave an outcome unassigned.** `HEUR-1.falsification_condition`
says departure from occupancy "in EITHER direction" falsifies, but P4 scores only
`real > null` (success) and `indistinguishable` (F3). `real < null` — the descent
*anti*-concentrating — has no assigned verdict. A pre-registered prediction set
with an unassigned outcome is not fully pre-registered.

### OBJ-5 (severity: high) — method ceiling on the instrument: the frozen grid very likely cannot reach its own pre-registered crossover `j*`, so P3 is probably unevaluable

This is a consequence of the v1→v2 fix disclosed in `CORR-20260915-3965c1`, and
it is not visible in that correction's reasoning.

The fix forces `deg(a) ≥ n − d_t` so that `w = (a·t) mod f` genuinely reduces.
Correct — and the correction is right that the interval is non-empty for
`d_t ≥ b+1`. **But non-emptiness is not feasibility.** Forcing `deg(a·t) ≥ n`
pins `deg w ≈ n−1` at *every* level, while the acceptance bound
`max(b, ⌈α·d_t⌉)` shrinks with the target degree. The smoothness parameter
`u = deg(w)/L ≈ (n−1)/(α·d_t)` therefore **grows** as the descent goes deeper, and
`ρ(u)` falls by roughly two orders of magnitude per unit of `u`.

Back-of-envelope (Dickman `ρ` by numerical integration; polynomial `L`-smoothness
approximated by `ρ(deg w / L)`; `b = 5`, the most favourable value; `K_try = 10^5`;
Stage A feasibility floor = 10 expected acceptances). **This is a red-team
estimate, not a Stage A computation and not a run** (`SRC-SCREEN-RT-CEILING`):

| n | α | last level with E[acc] ≥ 10 | node degree there | level pool `M_j` there | `T_j` there (B ≈ (n−1)/L) |
|---|---|---|---|---|---|
| 61 | 0.6 | 2 | 22 | 1.4·10³ | ~4 |
| 61 | 0.7 | 3 | 21 | 4.7·10³ | ~8 |
| 61 | 0.8 | 6 | 16 | 1.4·10³ | ~10² |
| 89 | 0.6 | 2 | 32 | 1.1·10⁵ | ~4 |
| 89 | 0.7 | 3 | 31 | 4.0·10⁵ | ~8 |
| 89 | 0.8 | 6 | 19 | 5.9·10⁴ | ~10² |
| 127 | 0.6 | 2 | 46 | 2.0·10⁷ | ~4 |
| 127 | 0.7 | 3 | 44 | 1.4·10⁸ | ~8 |
| 127 | 0.8 | 6 | 27 | 1.0·10⁷ | ~10² |

In every cell the descent hits the feasibility floor while `T_j` is still **two to
six orders of magnitude below** `M_j`. The pigeonhole condition `T_j ≥ M_j` that
defines `j*` is not met at the last reachable level anywhere on the grid.
`b = 3` and `b = 4` are strictly worse (they widen the pool window and deepen the
nominal descent without changing `u` at mid-tree degrees).

Consequences, in order of how much they cost:

* **P3 — the pre-registered mechanism test, and the entire reason Stage A and
  Stage B are one contract — is probably unevaluable.** `j*` sits below the
  deepest reachable level.
* **P2 (`depth ≥ 4`) is only reachable in the α = 0.8 cells**; α = 0.6 dies at
  depth ~3.
* Any `rho_j > 1` that *is* observed will sit above the crossover, where
  pigeonhole does **not** force it. The record supplies no mechanism for sharing
  there, so such a reading would be unexplained by its own hypothesis — and
  F2 would fire ("rho_j rises at a level unrelated to `j*`").
* The most likely actual outcome of running the contract as frozen is **F4**
  (descent failures dominate) — which, correctly and per AGENTS.md rule 5, is an
  *infrastructure/parameter* outcome and **not evidence about descent**. That is
  a full implementation budget spent for a result that says nothing.

**The feasibility rule itself is the defect that lets this through.** Stage A
declares infeasibility **per cell** — *"A cell whose predicted acceptance
probability implies fewer than 10 expected acceptances in K_try draws"* — but
acceptance probability is a function of **node degree**, not of the cell. Every
cell is comfortably feasible at its root (`E[acc] ≈ 10⁴–10⁵`) and hopeless four
to six levels down. As frozen, Stage A will pass the whole grid and Stage B will
die mid-descent.

I am not redesigning the contract; supersession is a Coordinator act. I am naming
the one comparison Stage A does not currently require and that decides everything:
**per cell, the deepest level whose predicted acceptance probability clears the
floor, set beside `j*`.**

### OBJ-6 (severity: medium) — the quantity has no stated parameter that should destroy it

Per `docs/inventor-protocol.md` §3, name the parameter that should kill the signal
and say what the measurement must do as it increases. For `rho_j` under pigeonhole
that parameter is the **level pool size `M_j`**, and the grid varies it: at a fixed
level index `j`, `M_j` grows steeply with `n` (61 → 89 → 127) and with `α`.

**So the contract's own pigeonhole mechanism predicts: `rho_j` at fixed `j` must
DECREASE as `n` increases, and must decrease as `α` increases.** This prediction
is nowhere in `H-ICPERF-5f038b`. It is free — the grid already contains the
variation — and it is the single cheapest discriminator between "we are measuring
pigeonhole" and "we are measuring the relation-finder". **A `rho_j` that stays
flat in `n` at fixed `j` is the artefact tell**, and as frozen the contract would
report it without noticing.

### OBJ-7 (severity: medium) — the memory axis is charged as a footnote, not as a frontier

The record flags, correctly, that a memoised descent trades time for memory and
that `Σ_j U_j` is the memo table size. But the contract measures only the two
endpoints — cache off (`w = 0`) and cache unbounded (`w = ∞`). The honest object
is the **interpolation**: with a memo table bounded to `w` entries, what fraction
of the sharing survives? This is the same time–memory interpolation this program
is required to charge against a van Oorschot–Wiener-style baseline, and it is the
axis on which "an eliminated dimension is not a speedup until the invariant's own
cost is in the total" (`KN-LIT-7593`) bites. `Σ_j U_j` **relation-finding calls**
saved is not a cost statement until it is set against `Σ_j U_j` **entries held**.
As frozen, no row of the deliverable carries both.

### OBJ-8 (severity: medium) — censoring is disclosed but its direction is not pre-registered

`node_failure` excludes `K_try`-exhausted nodes from `rho_j` and reports the
count; `interpretation_limits` calls them censored observations. Neither says
**which way the censoring biases `rho_j`**. It is not neutral: failures
concentrate at the deepest levels, which are exactly the levels where the record
expects the signal, and a failed node removes its whole sub-tree — i.e. removes
occurrences (`T`) and distinct nodes (`U`) in a ratio nobody has predicted. The
direction must be pre-registered before Stage B or the exclusion rate is
uninterpretable after it.

### OBJ-9 (severity: medium) — prior internal work on the same object is not cited

`IDEA-20260726-005` / `H-DTREE-001` / `EXP-DTREE-001` / `EV-DTREE-2e8f6a` /
`EV-DTREE-b47c19` is this program's own **multi-level descent tree for
prime-field ECDLP index calculus**, already designed, run and reviewed (verdict:
`inconclusive`, `claim_tier: toy`). `KN-OPEN-5b3a08` records the open
`harness/semaev.py` `s4_expr` defect that measurement surfaced. Arm 2 of
`IDEA-20260915-5c407a` is the same object on the same harness. Neither the idea
nor the hypothesis cites any of it. A novelty/domination screen that only looks
outward misses the nearest neighbour, and here the nearest neighbour is in this
repository and carries a live open defect that would land on arm 2.

### OBJ-10 (severity: low, governance) — the card was dispatched with `archived_by: null`, which its own preconditions forbid

`TASK-20260915-532164` carries `status: written_not_dispatched` and
`dispatch_preconditions[0]`: *"archived_by is bound to a freshly minted archival
task … Dispatch with archived_by still null is forbidden."* It is still `null` at
the reviewed commit, and this screen was dispatched and executed anyway. The other
two preconditions **are** satisfied (`TASK-20260915-60dc73` committed and pushed at
`7c3d47ed7`; inputs clean at HEAD). No lane-claim state was checked by me — that is
the Coordinator's to verify. This does not invalidate the findings, but this report
is a working-tree artefact under my write scope and is **not durable evidence until
a Coordinator archival task commits it**; the ownership rule the null was protecting
is currently unenforced.

---

## Required controls (before Stage B is approved, in order of cost)

| id | control | cost | what it decides |
|---|---|---|---|
| **RC-1** | **Run Stage A alone** (analytic, zero descent, 600 s as budgeted) and report, per cell, **both** `j*` **and** the deepest level whose predicted acceptance probability clears the feasibility floor. Approve Stage B only for cells where `j* ≤` that level. | ~600 s, already in the contract | Whether the grid can test P3 at all. Settles OBJ-5 for the price of the cheapest stage. |
| **RC-2** | Resolve `C-MEMO-OFF` to **one** of the two readings in OBJ-3, in writing, before implementation. | zero | Whether the proves-too-much guard is informative or tautological — and whether it will spuriously invalidate a correct run. |
| **RC-3** | Add the **null-censoring match**: apply the measured per-level descent-failure rate to `C-NULL`, or report censored and uncensored nulls side by side. | small | Whether P4, the deciding control, is a valid comparison at the deepest level. |
| **RC-4** | Pre-register the **`n`- and `α`-dependence of `rho_j` at fixed `j`** (it must *fall* as `n` or `α` rises). | zero | Separates pigeonhole from a relation-finder artefact. The null-object test applied to the parameter rather than to the object. |
| **RC-5** | Assign a verdict to **`real < null`** in P4/F3. | zero | Completes the pre-registration. |
| **RC-6** | Report the **bounded-memory interpolation**: sharing retained as a function of memo-table size `w`, not only `w = ∞`. | small | Makes any time saving a cost statement rather than half of one. |
| **RC-7** | Pre-register the **direction** of the censoring bias from `K_try` exhaustion. | zero | Makes the exclusion rate interpretable. |

---

## Baseline comparison

* **Pollard rho / BSGS.** *Not comparable, and the contract is right about why.*
  `H-ICPERF-5f038b.assumptions` states plainly that *"No discrete logarithm is
  computed anywhere in this design"*; correctness rests on per-relation algebraic
  identities. There is therefore no group, no solved instance and no quantity that
  can be placed beside a matched rho or BSGS run. This must not be read as the
  contract evading the baseline — it is an honest scope statement — but it does
  mean **nothing this contract produces can enter a boundary-table row**, which is
  the deliverable `RQ-ICPERF-94c86e` exists to produce.
* **Closest specialized baseline — published descent cost accounting.** Against
  BGJT §6.2 (`BGJT-Q2`), the Barbulescu/Guillevic individual-logarithm constants
  (`GUI-Q2`, `GUI-Q3`, `CS-Q1`) and the 30750-bit record's dynamic-programming
  cost model (`F2-Q1`, `F2-Q2`, `F2-Q4`): **`sota_delta = 0` at the exponent, on
  every family checked.** The idea's own `sota_delta` already claims no delta
  against SOTA — that part is honest and survives the screen. What does not
  survive is the fallback claim of a delta against this program's internal descent
  cost model, which OBJ-2 shows has no target.
* **Against the engineering baseline (CADO-NFS).** Memoisation of descent
  logarithms against a canonical-form-keyed known-log table is already implemented
  (`CADO-Q1`–`CADO-Q3`). The delta available is the *quantification*, not the
  technique.

---

## Narrowest supported statement

> The published descent complexity analyses this screen could read are charged on
> the descent **tree**, as `arity^depth`, so `IDEA-20260915-5c407a`'s framing
> premise is correct and is **not** dominated on that point. However, the
> pigeonhole saturation of the lower levels that mechanism M1 proposes as new was
> published by Barbulescu–Gaudry–Joux–Thomé in 2013, together with the prescribed
> remedy (replace those levels by precomputation) and the statement that the
> remedy does not change the complexity; and for NFS/FFS special-q descent the
> descent step is asymptotically subdominant to both the booting step and relation
> collection + linear algebra. **Regime R3 therefore has no exponent content for
> any published descent family checked here**, and memoisation of descent
> logarithms is already implemented in CADO-NFS. What remains un-dominated is the
> narrow measurement itself: a `rho_j`-vs-depth curve for a declared toy rule,
> which no source found here reports — subject to the uncovered scope below, and
> subject to OBJ-5, which suggests the frozen grid cannot reach the level where
> that curve would be interesting.

What this screen does **not** establish: that no descent anywhere admits an
exponent-relevant sharing effect; that `rho_j` has never been measured (Q1 is an
absence, not a negative); that the toy measurement is worthless (it is scoped and
honest, merely much less valuable than presented); or that the contract is
unimplementable (OBJ-5 is an order-of-magnitude estimate, and Stage A is the
instrument that settles it). **None of these is an impossibility result and none
may be reported as one.**

---

## Uncovered scope

Named explicitly so the Coordinator can scope the approval or supersession
decision to it.

1. **Sources not read.** Joux, *"A new index calculus algorithm with complexity
   L(1/4+o(1))"* (SAC 2013) — cited `recalled` by the idea, **still `recalled`
   after this screen**; Granger–Kleinjung–Zumbrägel, Trans. AMS 370 (2018) — I
   read two other GKZ papers, not this one; Diem, Compositio Math. 147 (2011) —
   **still `recalled`**; Kleinjung–Wesolowski J. AMS 2022 — **abstract only**, the
   descent accounting inside is unverified; the FFS GF(2^809) record
   (`KN-LIT-3440`) — corpus note only; Adj–Menezes–Oliveira–Rodríguez-Henríquez's
   characteristic-3 analyses; Barbulescu's thesis, which is the primary source for
   the `L_p[1/3,1.21]` descent constant I quote via Guillevic.
2. **Corpus depth.** The kb corpus holds **abstract-level literature notes**, not
   full texts. Every literature conclusion above rests on the full texts I fetched
   myself (`retrieved`), not on the index; the index's contribution was to
   *locate* the right papers and to resolve `KN-LIT-2459` (Commeine–Semaev) from
   `recalled` to `kb`. Six queries is a floor on recall, not an estimate.
3. **CADO-NFS revision not pinned.** Read from a GitHub mirror; canonical
   `gitlab.inria.fr` unreachable from this session. Q3's conclusion should be
   re-confirmed against a pinned canonical commit before it is used to supersede
   anything.
4. **Implementation artefacts.** Per-level de-duplication counts, if they exist
   anywhere, most plausibly live in record-computation logs and auxiliary
   repositories rather than in papers. Not searched.
5. **ECDLP / Diem descent (arm 2).** Not screened at all. The idea predicts
   `rho ≈ 1` there and the contract excludes it; that prediction is untested by
   this screen.
6. **OBJ-5's arithmetic is mine and is coarse.** Dickman `ρ` as a proxy for
   `F_2[x]` smoothness density is least accurate at `q = 2`; my branching estimate
   `B_j ≈ (n−1)/L_j` is a lower bound on the child count. The conclusion (the
   floor is hit several orders of magnitude before `j*`) is robust to one or two
   orders of magnitude in `ρ`, because `ρ(u)` falls ~100× per unit `u` while `u`
   rises ~`1/α` per level — but **Stage A, not this table, is the instrument that
   settles it.** One cell, `(n = 61, b = 5, α = 0.8)`, sits close enough to the
   boundary that my estimate cannot call it.
7. **Lane/claim state.** I did not check `tools/goal_lanes.py` state for
   `GOAL-ICPERF-e6b6a4` or `BATCH-51e2aa`. That precondition is unverified here.

---

## Next concrete action (one)

**Approve Stage A only, as an analytic zero-descent task, and gate Stage B on a
new criterion Stage A must report: per cell, `j*` beside the deepest level whose
predicted per-node acceptance probability clears the feasibility floor. Stage B is
approved only for cells where `j* ≤` that level; if no cell qualifies, the grid is
superseded rather than run.**

This costs the 600 s already budgeted for Stage A, requires no implementation of
the descent itself, and settles OBJ-5 — the difference between a contract that can
test its own pre-registered prediction and one that will return F4 after a full
implementation budget. Whatever the Coordinator concludes about Q2b, this gate is
worth passing first, because a contract that cannot reach `j*` produces nothing
either way.

---

```yaml
red_team_report:
  id: RT-20260915-532164
  task_id: TASK-20260915-532164
  claim_under_review: >-
    IDEA-20260915-5c407a / H-ICPERF-5f038b / EXP-ICPERF-025a52 v2 -- that
    recursive index-calculus descent is universally analysed as a TREE while the
    object is a DAG, that the true cost is the distinct-node count, and that if
    the sharing ratio rho_j = T_j/U_j grows with depth (regime R3) the descent
    phase's charged exponent is an over-estimate.
  verdict: partially_dominated
  objections:
    - OBJ-1 (high): the idea's dominated_by enumerates two exits and the live one
      is a third it did not name -- analyses on the TREE, but the tree bound
      known-loose in the saturated region and closing it published as
      complexity-neutral (BGJT-Q2).
    - OBJ-2 (high): sota_delta's internal target does not exist. GOAL-ICPERF-e6b6a4
      declares the descent column unmeasured and unclaimed (ICPERF-Q1); the one
      descent model in the ledger charges by YIELD, not tree size (YIELD-Q1).
    - OBJ-3 (high): C-MEMO-OFF is not the proves-too-much guard it claims. Under
      the frozen metric definitions plus deterministic per-node relation choice it
      FAILS on a correct instrument and fires F0; under the only reading that
      passes, it is true by construction.
    - OBJ-4 (high): C-NULL, the deciding control, is unmatched on censoring at
      exactly the level where P4 is evaluated; and P4/F3 leave `real < null`
      unassigned.
    - OBJ-5 (high): method ceiling on the instrument. The v2 fix pins deg w ~ n-1
      at every level while the acceptance bound shrinks, so u = (n-1)/(alpha*d_t)
      grows with depth and the K_try floor is hit 2-6 orders of magnitude before
      T_j reaches M_j, in every grid cell. P3 is probably unevaluable and the
      likely outcome is F4 -- an infrastructure result, never evidence.
    - OBJ-6 (medium): no parameter is named that should destroy rho_j. Pigeonhole
      predicts rho_j at fixed j must FALL as n or alpha rises; the grid already
      varies both and the contract makes no such prediction.
    - OBJ-7 (medium): memory is charged as a footnote. Only w=0 and w=infinity are
      measured; the bounded-memo-table interpolation is absent (KN-LIT-7593).
    - OBJ-8 (medium): censoring from K_try exhaustion is disclosed but its
      direction is not pre-registered, and it concentrates at the signal levels.
    - OBJ-9 (medium): prior internal work on the same object (IDEA-20260726-005,
      H-DTREE-001, EXP-DTREE-001, EV-DTREE-2e8f6a, KN-OPEN-5b3a08) is uncited.
    - OBJ-10 (low, governance): the card was dispatched with archived_by null,
      which its own dispatch_preconditions forbid. This report is not durable
      evidence until a Coordinator archival task commits it.
  required_controls:
    - RC-1 run Stage A alone and report j* beside the deepest feasible level, per cell
    - RC-2 resolve the C-MEMO-OFF ambiguity in writing before implementation
    - RC-3 match C-NULL on censoring, or report censored and uncensored nulls
    - RC-4 pre-register that rho_j at fixed j must fall as n and as alpha rise
    - RC-5 assign a verdict to `real < null` in P4/F3
    - RC-6 report sharing retained as a function of bounded memo size w
    - RC-7 pre-register the direction of the K_try censoring bias
  counterexample_or_mutation: >-
    The cheapest discriminating mutation is RC-4, and it needs no new run: the
    grid already varies the level pool size M_j by many orders of magnitude across
    n in {61,89,127} and alpha in {0.6,0.7,0.8}. Pigeonhole -- the record's own
    mechanism -- requires rho_j at fixed level index j to DECREASE as M_j grows.
    If the measured rho_j is flat in n at fixed j, the quantity is not tracking
    occupancy and P3's explanation is dead whatever the number says. The nearest
    published counterexample to the cost premise is the 30750-bit record (F2-Q3):
    the expensive classical descent processed exactly ONE polynomial per degree
    down to degree 35 -- a path, rho_j identically 1 -- while every degree <= 8,
    where sharing is forced, is charged cost 0 (F2-Q2).
  baseline_comparison: >-
    Pollard-rho and BSGS are not comparable: the contract computes no discrete
    logarithm (H-ICPERF-5f038b.assumptions), so it yields no quantity that can
    enter a boundary-table row or a rho ratio. Against the closest specialized
    baseline -- published descent cost accounting -- sota_delta is 0 at the
    exponent on every family checked: BGJT states the pigeonhole-saturated region
    is better handled by precomputation and that doing so does not change the
    complexity (BGJT-Q2); NFS-DL charges the descent step at L_p[1/3,1.21] under a
    booting step of L_p[1/3,1.23] and a dominating L_Q[1/3,1.923] (GUI-Q1, GUI-Q2,
    corroborated by CS-Q1). Against the engineering baseline, CADO-NFS already
    memoises descent logarithms against a canonical-form-keyed known-log table
    (CADO-Q1, CADO-Q2, CADO-Q3); the unpublished delta is the quantification, not
    the technique.
  heuristic_challenges:
    - HEUR-1 (the occupancy model) is explicit, numbered and given a random-model
      justification, and the record tests rather than assumes it. That is correct
      practice and is not an objection.
    - The transfer is the objection. The level-j nodes of a descent are not
      uniform draws from the level pool: they are the irreducible factors of an
      ACCEPTED, smoothness-conditioned w. Conditioning on L-smoothness biases the
      factor-degree distribution toward the top of the allowed window, which is
      exactly the sub-pool with the largest M_d. Cheapest exposure, zero runs:
      compare the measured child-degree histogram against the Stage A branching
      model's C(d,r) -- the contract already computes both and does not compare
      them.
    - supporting_results is empty by design and the record says why. Correct. The
      screen converts one recalled pointer (Commeine-Semaev) to `kb`
      (KN-LIT-2459) and leaves Joux SAC 2013, GKZ Trans. AMS 2018 and Diem 2011
      still `recalled`; they may not discharge supporting_results.
  cost_model_challenges:
    - Total expected cost is handled correctly in the ledger's other descent
      record (IDEA-20260727-002 charges T_attempt / P_dec). This contract reports
      T_j and U_j as call COUNTS and never multiplies by the per-node inverse
      success probability, which is the quantity that actually dominates: at the
      last feasible level the per-node acceptance probability is ~1e-4, so a node
      costs ~1e4 draws. A saving of rho_j calls is worth rho_j * (1/P_acc) draws,
      and P_acc varies by four orders of magnitude ACROSS levels. Counting calls
      per level and never weighting them by per-level cost is the same error the
      idea accuses the literature of, one level up.
    - Memory: sum_j U_j is named as the memo size but never converted to bytes,
      never compared against maximum_memory_gb: 2, and never interpolated over a
      bounded cache (OBJ-7).
    - o(1)/overhead: the memo key is the monic canonical byte form; hashing and
      lookup cost per node is not charged anywhere against the relation-finding
      call it replaces.
  reduction_and_scope_challenges:
    - Scope is stated unusually well: the contract repeatedly and correctly says it
      is NOT FFS, NOT Joux, NOT GKZ, NOT Diem, NOT any elliptic curve. No scope
      inflation found in the contract.
    - Scope inflation IS present one level up, in the idea's claim sentence:
      "Every recursive descent in index calculus ... is universally described in
      the literature as a DESCENT TREE, but the object is actually a DIRECTED
      ACYCLIC GRAPH ... The cost of descent is therefore NOT the node count of the
      tree but the count of DISTINCT nodes." The first clause is verified
      (BGJT-Q1, GKZ-Q1). The last is not: for BGJT the prescribed algorithm
      already avoids the saturated region (BGJT-Q2), and for NFS the phase is
      subdominant (GUI-Q2), so "the cost of descent" is neither quantity in the
      place it matters.
    - No reduction chain is claimed (reduction_chain.core_problem: null,
      corollaries: []). Correct, and nothing to instantiate.
  proof_architecture_challenges:
    - method_ceiling: the record's own method_ceiling block is honest ("Nothing
      asymptotic, nothing about ECDLP, nothing about any published descent"). The
      ceiling this screen adds is on the INSTRUMENT, not the claim: OBJ-5 shows the
      frozen grid probably cannot reach j*, so the strongest certifiable claim is
      narrower still -- rho_j for levels ABOVE the crossover, where the record's
      own mechanism predicts nothing.
    - nearby_object: C-NULL is the right nearby object and is well chosen. The
      defect is the censoring mismatch (OBJ-4), not the choice.
    - quantifier_order: sound. j* is a function of (n,b,alpha) fixed in Stage A
      before any Stage B quantity exists, and the Stage-A hash is bound into the
      Stage-B manifest as an invalidation rule. This is the best-constructed part
      of the contract and it should be preserved through any supersession.
    - boundary_embedding: the baseline is the same instrument with one flag, which
      is the right embedding -- but see OBJ-3: that flag does not mean what the
      record says it means.
  narrowest_supported_statement: >-
    The published descent analyses read here are charged on the TREE as
    arity^depth, so the idea's framing premise is correct and is not dominated on
    that point; but the pigeonhole saturation it proposes as new was published by
    BGJT in 2013 together with the prescribed remedy and the statement that the
    remedy does not change the complexity, and for NFS/FFS the descent step is
    asymptotically subdominant to both the booting step and relation collection +
    linear algebra. Regime R3 therefore has no exponent content for any published
    descent family checked here. Memoisation is already implemented in CADO-NFS.
    What remains un-dominated is the narrow toy measurement itself, subject to the
    uncovered scope and to OBJ-5.
  next_concrete_action: >-
    Approve Stage A ONLY, as an analytic zero-descent task within its existing
    600 s budget, and gate Stage B on a criterion Stage A must newly report: per
    cell, j* beside the deepest level whose predicted per-node acceptance
    probability clears the feasibility floor. Approve Stage B only for cells where
    j* <= that level; if no cell qualifies, supersede the grid rather than run it.
  artifact_paths:
    - coordination/goals/GOAL-ICPERF-e6b6a4/tasks/TASK-20260915-532164/screen-report.md
    - coordination/goals/GOAL-ICPERF-e6b6a4/tasks/TASK-20260915-532164/sources.yaml
  asserts_no_research_status: true
```
