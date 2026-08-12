# OD-4: a lower bound on the branching factor B, and the exact step of PROP-701-I that breaks under B > 1

**Task** TASK-20260801-806 · **Goal** GOAL-AES-001 · **Batch** BATCH-004 · **Role** executor
**Artifact class** PROSE_REPORT

**Provenance pointer (protocol-amendment-GOAL-AES-001-004 Part B, class PROSE_REPORT).**
This report elects the POINTER form, which Part B declares equally compliant with the
in-text form. The covering manifest is `od4_results.json` in this same directory. Its
`artifact_provenance` list carries this file's path, kind `PROSE_REPORT`, its SHA-256,
`comment_block_inference_stanza: false` (not required of this class) and
`covered_by_this_manifest_inference_block: true`. The manifest's first-class `inference`
block records policy `executor-implementation`, requested policy `executor-implementation`,
resolved model `claude-opus-5`, `fallback_used: true`, `model_verified: false`
(`python3 -m orchestration.adapter doctor --probe` was not run), and standing basis
`0137a051eb5828789eb267fa83c8278086578d4c`.

---

## 0. What this is, and what it is not

This is a **derivation plus toy-scale exhaustive computation about the algebra of AES
components**. It is **not** a cryptanalytic result, **not** a distinguisher, **not** a key
recovery, and **not** a barrier statement about AES security. **Nothing here asserts
anything about AES at any round count**, including the 3–7 rounds RQ-AES-001 scopes in.
Every statement below is scoped to: the object class defined in §2, the number of
super-box interfaces explicitly counted, the field explicitly named, and the budget
actually spent (1600 s declared, ~67 s of compute consumed).

The report **proposes no closure, no `reject_scoped`, no evidence strength, no hypothesis
status and no promotion**. It requests no gate to be treated as satisfied. Gate (4) is
named as required and not performed here.

**Supersession.** Every file in this task directory is new. No BATCH-001, BATCH-002 or
BATCH-003 artifact is modified, re-run into, or deleted, and none is superseded: PROP-701-I
(BATCH-002 `candidate_report.yaml`, snapshot `ebac9ba8`) and Proposition 801-1 (BATCH-003
`od1_and_gate_redesign_report.md`) both **stand exactly as written**. Proposition 806-1
below does not correct either; it addresses a class neither of them covers.

**Literature.** No primary source is reachable in this environment. No literature
comparison, `sota_delta` or bit-margin is offered; DEC-20260731-011's strikes stand. One
recollection is used and is marked inline as `unverified-from-memory` with a recall
confidence. Nothing is compared against a recalled number.

**Instrument work.** None was performed. No mutation-control file was read for
modification, repaired, extended, re-run or probed; no escape was enumerated; no
GATE-601-A and no `reject_scoped`. DEC-20260731-014's stand-down was not touched.

---

## 1. The pre-screen, and what it killed

`prescreen_od4.json` was written **first**, before any derivation, any code and any
execution, and is frozen. Six candidate lines of argument were screened. **Two were killed
and neither was pursued**; the report states this per candidate, as the completion gate
requires.

| id | spreads through (λ,k) graph or G² | interface constant n | verdict | pursued |
|---|---|---|---|---|
| CAND-806-A — re-run Steps 1–3 with B-confinement, close under the group | **yes** | **30** (measured forward diameter; eccentricity distribution {30: 1020}; vertex-transitive, so no start node is cheaper. Via G² it is 2 + 2n\* = 32, worse) | **IN_SCOPE_VACUOUS**, margin 23 | **no** |
| CAND-806-B — type analysis of the Step 1 → Step 2 bootstrap under branching | no (routes through the two statements at one interface) | 1 | PURSUE | yes |
| CAND-806-C — exact one-interface branching for F-linear π by support/minor algebra | no (routes through the coordinate-support and minor structure of M) | 1 | PURSUE | yes |
| CAND-806-D — compose the one-interface bound into a cost table in n | no (routes through arithmetic on a cost model; n is a free parameter of the table, not a constant that must be reached) | 1 | PURSUE | yes |
| CAND-806-E — approximate-group / Freiman-type closure of the B-confinement | **yes** | **no upper bound exhibitable**; lower bound 30 | **IN_SCOPE_VACUOUS** on both grounds | **no** |
| CAND-806-F — fibre-counting bound for arbitrary π | no (routes through fibre cardinalities at one interface) | 1 | PURSUE | yes |

**CAND-806-A was not pursued.** No lemma, derivation or computation for it appears in any
artifact of this task. **CAND-806-E was not pursued.** Likewise.

The screen's own finding, worth stating: **every candidate that spreads a property through
the (λ,k) graph was killed, and every surviving candidate concludes from a single
interface.** The (λ,k) machine is not the machine that produced the bound in §4 — that is
the substantive content of the pre-screen, not a formality.

The screen was applied under **both** conversions (§`screen_definition.conversion_caveat`
of the frozen file). PROP-701-I's own one-interface-per-round convention gives at most 7
interfaces in scope; the alternative one-interface-per-super-box convention gives at most 3.
Every PURSUE has n = 1 and survives both; every kill fails both. **The one-interface-per-round
identification is PROP-701-I's modelling convention (residual R5) and is established by
nothing in this campaign.**

---

## 2. The object, restated so it is not drifted from

Let F = GF(2⁸), q = |F| = 256, Φ = ARK ∘ MC ∘ SR the AES super-box interface, M the
MixColumns matrix with columns m₀…m₃.

A **per-word projection** is a map π : F⁴ → X applied to every super-box word at every
super-box layer, **round-independent** (the same π before and after the interface). Its
**entropy loss** is L = 32 − log₂|X|.

* PROP-701-I's hypothesis (**B = 1**): there exist functions F_j : X⁴ → X with
  π(word_j(Φ(s))) = F_j(π(word₀(s)),…,π(word₃(s))) for **every** state s.
* OD-4's hypothesis (**bounded branching**): there exist relations R_j ⊆ X⁴ × X with
  |R_j(x)| ≤ B for every x, such that π(word_j(Φ(s))) ∈ R_j(π(word₀(s)),…,π(word₃(s)))
  for **every** state s.

B = 1 recovers PROP-701-I exactly. PROP-701-I says nothing about B > 1.

Throughout, **B(π) denotes the least B for which such a relation system exists.** Any valid
system must contain the canonical relation
R_j^can(x) = { π(word_j(Φ(s))) : s with π-profile x }, so a lower bound on |R_j^can| is a
lower bound on **every** admissible system. That observation is used silently below.

---

## 3. Part I (CAND-806-B) — the exact step of PROP-701-I that breaks under B > 1

**The answer to OD-4's question as posed is NO: the Step-1/Step-2/Step-3 machinery does not
force an inequality relating B, L and n.** The break is precise and is not a matter of the
argument being merely harder.

### 3.1 What Step 1 still gives

Step 1 survives, in weakened form. Take a ≠ b in F⁴ with π(a) = π(b), Δ = a + b. Compare
states S, S′ identical except that input word 1 is a in S and b in S′. All four input
π-values agree, so **the two outputs' π-values lie in the same set R_j(x)**, of size ≤ B.
Writing v = Δ_i m_i, Step 1 therefore yields, for u in the affine hyperplane U_i,

> **B-CONFINEMENT.** π(u) and π(u + v) lie in a common subset of X of size at most B, and
> that subset is R_j(x), which **depends on u** through the input π-profile x.

At B = 1 this is exactly π(u) = π(u + v).

### 3.2 The exact breaking step

**The break is the first sentence of Step 2:** *"For each u in U_i, the pair (u, u+v)
satisfies π(u) = π(u+v), so Step 1 applies to it."*

Step 1 **consumes** a hypothesis of the form *equality of two π-values*. Under B > 1, Step 1
**emits** a conclusion of the form *B-confinement of two π-values*. B-confinement is
**strictly weaker than equality for every B ≥ 2**, so the emitted conclusion cannot be fed
back in as the hypothesis of the next application. PROP-701-I is an induction whose engine
is precisely that its conclusion type equals its hypothesis type; at B = 1 the two coincide
and the induction runs, and at B ≥ 2 they do not and **the induction fails at its first
step, inside interface 1.**

Two further, independent failures sit behind that one, and are recorded because a repair
would have to clear all three:

* **Step 2's union fails separately.** Step 2 removes the constraint y_k = u_k by taking a
  union over u ∈ U_i, using that the invariance translation v_k m_k is *the same
  translation* for every u. Under branching the confining set R_j(x) **varies with x**, so
  the union is a union of *different* confinements; there is no single object to union, and
  the constraint is not removed. The step needs a single-valued u_k sweep and does not have one.
* **Step 3's group closure fails separately.** Step 3 says "the translations leaving π
  invariant form a group, hence contain the GF(2)-span". B-confinement is reflexive and
  symmetric but **not transitive**: π(u), π(u+v) sharing a ≤B-set and π(u+v), π(u+2v)
  sharing a (different) ≤B-set implies nothing about π(u) and π(u+2v). With no transitivity
  there is no equivalence, no group, no span, and no "invariant under every translation".

### 3.3 What a replacement would need (forward guidance)

A repair must supply a **type-stable** invariant: a property P of a pair (u, u+v) that
(i) Step 1 emits under branching and (ii) Step 1 also consumes, so that the induction closes.
Concretely a replacement would need **at least one** of:

1. a *quantitative* confinement that composes — e.g. a metric d on X for which Step 1 emits
   d(π(u), π(u+v)) ≤ δ(B) and consumes the same, with δ subadditive along the iteration.
   Nothing in this campaign supplies such a metric, and the (λ,k) graph's diameter of 30
   means any such δ must survive 30 compositions without degrading, which is a strong demand;
2. a *bounded-index subgroup* statement replacing the group closure: that the relation
   "π(u), π(u+v) share a ≤B-set" contains a subgroup of translations of index bounded in B.
   That is a genuine open question and is **not** answered here;
3. abandoning the traversal entirely and arguing at one interface. **That is what §4 does**,
   and it is why §4's bound is not a repair of PROP-701-I's machinery but a different
   argument for a smaller class.

---

## 4. Part II (CAND-806-C) — Proposition 806-1: a lower bound on B for F-linear π

The bound below **does not come from the group-growth argument**. It comes from the
coordinate-support and minor structure of M at a single interface. It applies to a strictly
smaller object class than OD-4's, and that restriction is part of the statement, not a
footnote.

### 4.1 Statement

> **PROPOSITION 806-1.** Let F = GF(2⁸), q = 256. Let π : F⁴ → F⁴/K be **F-linear** with
> kernel K, applied round-independently to every super-box word, and suppose π is **neither
> injective (K = 0) nor constant (K = F⁴)**. Then every bounded-branching relation system
> for π across Φ = ARK ∘ MC ∘ SR satisfies
>
> **B ≥ q = 2⁸ = 256,**
>
> **independently of the entropy loss L = 8·dim K.** The bound is **tight**: it is attained
> at dim K = 1, 2 and 3, i.e. at L = 8, 16 and 24.
>
> Exactly: with S = { i : proj_i(K) ≠ 0 }, s = |S|, and W_S the F-span of { m_i : i ∈ S },
> **B = q^( s − dim(W_S ∩ K) )**, and the exponent is ≥ 1 for every K ∉ {0, F⁴}.

**Epistemic label: DERIVATION** (complete argument, checkable by recomputation), not
machine-checked, not empirical. Its finite ingredients are recomputed exhaustively by
`od4_branching.py` phases P1–P3 over GF(2⁸).

> **COROLLARY 806-2 (the cost inequality, in the form OD-4 asked for).** Write the **yield**
> Y = log₂|X| − log₂B, the number of bits of predictive information the branching relation
> retains per word per interface. For F-linear round-independent π across one AES super-box
> interface,
>
> **L + Y ≤ 24 bits,**
>
> tight at L = 8 (Y ≤ 16), L = 16 (Y ≤ 8) and L = 24 (Y ≤ 0). At L = 24 the relation is
> **total** — R_j(x) = X — so an F-linear per-word projection losing 24 bits carries no
> information across the interface at all.

Corollary 806-2 is the trade-off form; it follows from B ≥ q together with the trivial
ceiling B ≤ |X| = 2^(32−L), which also shows that **no lower bound of the shape B ≥ f(L,n)
with f increasing in L can exist for any object class**: f is capped by 2^(32−L). That
ceiling is the structural reason OD-4's hoped-for shape cannot be attained in the direction
hoped for, and it is stated here rather than left for the red team.

### 4.2 Proof, decomposed into single-responsibility lemmas (promotion gate 1)

Each lemma does one job. The Assembly is a counting argument over a **measured** table, in
the structural pattern DEC-20260731-014 records for Proposition 801-1.

**LEM-806-1 (ShiftRows index bookkeeping — one job: the four coordinates come from four
different words).** For each fixed output word index j, i ↦ (j+i) mod 4 is a bijection of
{0,1,2,3}. Hence the pre-MixColumns vector y^(j) of output word j takes its coordinate i
from input word (j+i) mod 4, and the four coordinates are taken from four **distinct** input
words. *Verified exhaustively over all 16 (j,i) pairs: P1, PRED-4, holds.*

**LEM-806-2 (perturbation set — one job: identify the reachable set).** Fix the input
π-profile x. Input word t may vary over the coset w_t + K, so coordinate i of y^(j) varies
over proj_i(K), the image of K under the i-th coordinate map — a F-subspace of F, hence 0 or
all of F. By LEM-806-1 the four coordinates are perturbed by **four independent elements of
K**, so the reachable perturbation set of y^(j) is exactly the product
∏_i proj_i(K) = F^S with S = { i : proj_i(K) ≠ 0 }. ARK contributes a fixed translation and
does not change any cardinality.

**LEM-806-3 (image size — one job: turn the set into a count).** The reachable set of output
words is M·F^S + const = W_S + const with W_S = span{ m_i : i ∈ S }, and dim W_S = s since M
is invertible. Every admissible relation must contain the π-image of that set, so
B ≥ |π(W_S)| = q^( s − dim(W_S ∩ K) ), and the canonical relation attains it. Hence
**B = q^( s − dim(W_S ∩ K) )** exactly.

**LEM-806-4 (support and intersection bookkeeping — one job: bound the exponent's negative
term).** K ⊆ F^S by construction, so dim K ≤ s; and dim(W_S ∩ K) ≤ dim(W_S ∩ F^S). The
sixteen values of dim(W_S ∩ F^S) over GF(2⁸) are **measured, not asserted**:

| s = \|S\| | dim(W_S ∩ F^S) | number of such S |
|---|---|---|
| 0 | 0 | 1 |
| 1 | **0** | 4 |
| 2 | **0** | 6 |
| 3 | **2** | 4 |
| 4 | **4** | 1 |

matching max(0, 2s − 4) in every row. *P1, PRED-3, holds; computed over GF(2⁸) for all 16
subsets.* The s = 1 and s = 2 rows are exactly the fact that every entry of M is nonzero and
that every 2×2 minor of M is nonzero; the s = 3 row is the 3×3 minor condition. *P1 records
all entries nonzero (PRED-1, holds — this recomputes `verify_derivation.py` claim C9
independently) and all 69 proper minors plus the determinant nonzero, i.e. M is MDS
(PRED-2, holds).*

**ASSEMBLY (counting over the measured table).** Minimise the exponent s − dim(W_S ∩ K) over
the 15 nonempty S and over 1 ≤ dim K ≤ min(s, 3) — dim K ≤ 3 because dim K = 4 is the
excluded constant π:

| s | dim(W_S ∩ K) ≤ | admissible dim K | min exponent | min B |
|---|---|---|---|---|
| 1 | 0 | 1 | 1 − 0 = **1** | q |
| 2 | 0 | 1, 2 | 2 − 0 = **2** | q² |
| 3 | min(2, dim K) | 1, 2, 3 | 3 − 2 = **1** | q |
| 4 | min(4, dim K) = dim K ≤ 3 | 1, 2, 3 | 4 − 3 = **1** | q |

The minimum over all rows is exponent 1, so **B ≥ q**. ∎

*(Caveat recorded for the reader of the machine output: P3's field `min_over_all_S` reads 1
rather than 256, because that phase allows dim K = 4 in the s = 4 row. dim K = 4 is π
constant and is excluded by hypothesis. The table above is the corrected minimisation and
the discrepancy is flagged here rather than left to be discovered.)*

**Tightness.** Three explicit witnesses over GF(2⁸), each with B recomputed independently
(P2):

| witness K | dim K | L | S | dim(W_S∩K) | B | independent enumeration |
|---|---|---|---|---|---|---|
| span(e₀) | 1 | 8 | {0} | 0 | **256** | 256, agrees |
| W_S ∩ F^S for S={0,1,2} | 2 | 16 | {0,1,2} | 2 | **256** | skipped (q^\|S\| > 2²⁰ limit) |
| span(e₀,e₁,e₂) | 3 | 24 | {0,1,2} | 2 | **256** | skipped (same reason) |

### 4.3 Independent recomputation of the closed form

The closed form of LEM-806-3 is checked against brute force by two routes that do not reuse
it:

* **`branching_by_enumeration`** explicitly enumerates M·(∏_i proj_i(K)) and counts distinct
  π-images. Over GF(2⁸): 3 of the 6 witness kernels within the 2²⁰ enumeration limit, **all
  agree**. Over the GF(2⁴) analogue: 101 cross-checks, **0 discrepancies**. Over the GF(2²)
  analogue: every subspace cross-checked, **0 discrepancies**.
* **`branching_from_definition`** uses **no structural shortcut at all**: it ranges the
  perturbation tuple over K⁴ (all four input words perturbed independently by arbitrary
  elements of K), applies the actual ShiftRows index map and the actual MixColumns, and
  counts distinct π-images per output word and jointly. Run **exhaustively over all 442
  kernels of dimension 1 and 2 in the GF(2²) analogue** (85 + 357, complete, not capped):
  **0 discrepancies**, per-word and joint.

*PRED-5 holds with zero discrepancies at every scale run.*

### 4.4 Exhaustive minimisation in the analogues

**These are ANALOGUES. Their readings are NOT evidence about GF(2⁸) and are certainly not
evidence about AES.** They are reported because they are exhaustive where GF(2⁸) is not.

| analogue | subspaces enumerated | min B over lossy non-constant K | per-dim minima (d=1,2,3) |
|---|---|---|---|
| GF(2⁴), M circulant (02,03,01,01), MDS = **true** | **78 901** (all of them) | **16 = q** | 16, 16, 16 |
| GF(2²), same symbols, MDS = **false** (16 vanishing 2×2 and 8 vanishing 3×3 minors) | **529** (all of them) | **4 = q** | 4, 4, 4 |

Both analogues read min B = q, independently of dim K, matching PRED-6 and matching the
GF(2⁸) derivation. The GF(2²) analogue is **not MDS**, which is recorded as a limitation of
that analogue and simultaneously as a data point for §7: losing MDS did not move the minimum.

---

## 5. Part III (CAND-806-D) — cost accounting over n interfaces (promotion gate 3)

**Every number in this section is labelled MEASURED, DERIVED or MODELLED. Modelled numbers
are not measurements.** The parameter sets are **toy / reduced-round** and are named as such.

### 5.1 The attempt, its cost, and its success probability (gate 1 bookkeeping)

* **Attempt.** Follow one π-trajectory of the object across n consecutive super-box
  interfaces, expanding the branching relation at each word of each interface.
* **Per-attempt cost.** C_node × N(n), where N(n) is the number of nodes expanded and C_node
  is the cost of evaluating one R_j. For F-linear π, C_node is O(1) field operations
  (the relation is a linear map, evaluated on the fly).
* **Success probability.** For the **frontier** version, p = 1 exactly: the true trajectory
  is contained in the relation by the definition of the object, so no attempt is lost. For
  the **single-guess** version, p = 1/J^n where J is the per-interface joint branching, and
  the per-attempt cost is C_node·n.
* **Product.** Frontier: cost × 1/p = C_node·N(n) × 1. Single guess:
  C_node·n × J^n. Both are shown; they agree up to the C_node·n factor, and the frontier
  form is used in the table.

### 5.2 The per-interface joint branching J (four words, one 128-bit state)

Three separate rows, because they have three different epistemic statuses and conflating
them is the D-705-9…12 failure this repairs:

| basis | J per interface | status |
|---|---|---|
| provable from Proposition 806-1 | **≥ 2⁸** | **DERIVED**, unconditional (the joint is at least the per-word branching) |
| the six GF(2⁸) witness kernels of P2 | **2³²**, exactly, = B⁴ at the three minimising witnesses | **MEASURED** at those kernels only; **not** an exhaustive minimum over GF(2⁸) |
| GF(2⁴) analogue, exhaustive over all 78 901 subspaces | min J = q³ (= 2¹² there) | **MEASURED IN AN ANALOGUE**; transfer to GF(2⁸) is **HEUR-806-1**, not a fact |

**A pre-registered prediction was falsified here and is reported as such.** PRED-11 predicted
J < B⁴ at the minimising kernels. **Measured: J = B⁴ = 2³² exactly at all three GF(2⁸)
minimising witnesses**, while J < B⁴ elsewhere (e.g. K = span(m₀): J = 2³² against
B⁴ = 2⁹⁶). The prediction is recorded as **partially falsified** and was not adjusted.

### 5.3 Concrete cost table, toy / reduced-round parameter sets

Standardized parameter sets, all **toy**: F-linear round-independent per-word π over
GF(2⁸), state = four 32-bit super-box words = 128 bits, L ∈ {8, 16, 24}, n = 1…7 interfaces.
Baseline for comparison = exhaustive enumeration of the 128-bit state = 2¹²⁸.

| n | frontier cost, J = 2⁸ (DERIVED floor) | frontier cost, J = 2³² (MEASURED at witnesses) | with de-duplication, L = 16 (frontier ≤ \|X\|⁴ = 2⁶⁴) | meet-in-the-middle, J = 2³² |
|---|---|---|---|---|
| 1 | 2⁸ | 2³² | 2³² | 2¹⁶ |
| 2 | 2¹⁶ | 2⁶⁴ | 2⁶⁴ | 2³² |
| 3 | 2²⁴ | 2⁹⁶ | 2⁶⁴ | 2⁴⁸ |
| 4 | 2³² | **2¹²⁸ (= baseline)** | 2⁶⁴ | 2⁶⁴ |
| 5 | 2⁴⁰ | 2¹⁶⁰ | 2⁶⁴ | 2⁸⁰ |
| 6 | 2⁴⁸ | 2¹⁹² | 2⁶⁴ | 2⁹⁶ |
| 7 | 2⁵⁶ | 2²²⁴ | 2⁶⁴ | 2¹¹² |

Column 2 is **DERIVED and unconditional**; columns 3–5 are **MODELLED** on top of measured
inputs and rest on HEUR-806-2 and HEUR-806-3 below.

**Memory.** The frontier method's memory equals its frontier size: 2³²ⁿ un-deduplicated, or
|X|⁴ = 2^(4(32−L)) with de-duplication (2⁶⁴ at L = 16, 2⁹⁶ at L = 8). Depth-first traversal
trades this to O(n) memory at the same time cost. **The 15 GB available here holds ≈ 2³⁴
bytes**, so every table entry above 2³⁴ is beyond this machine and is **modelled, not
measured** — stated explicitly because BATCH-002's untabulated 46× memory ratio is the
precedent being repaired.

**Time–memory trade-off.** Meet-in-the-middle across the n interfaces halves the exponent
(column 5), at memory 2^(16n). This **materially weakens** any barrier reading of column 3:
at n = 7, MITM gives 2¹¹² < 2¹²⁸.

**Parallelization.** Frontier expansion is embarrassingly parallel; P cores divide wall-clock
time by P and leave memory unchanged in the depth-first form. On this machine P = 4, a
factor 2².

**Hidden overhead (the o(1) disclosure).** For F-linear π the relation is a linear map, so
C_node is a handful of field operations and nothing large hides in it. **For a general π the
relation would have to be stored or recomputed**: a table for R_j has |X|⁴ · B entries,
which at L = 16 is 2⁶⁴ · 2⁸ = 2⁷² entries — a **superpolynomial overhead entirely absent
from the table above**, which is legitimate only because the table is restricted to the
F-linear class. Carrying this table to a general π **without** re-deriving C_node would be a
cost-model error.

### 5.4 Optimistic assumptions, flagged individually

1. **OPTIMISTIC (favours the object):** the baseline is taken as 2¹²⁸ full state enumeration.
   Any cheaper alternative attack makes the object look worse, and at 3–7 rounds cheaper
   alternatives certainly exist. No such alternative is named or costed here, and none may
   be inferred.
2. **OPTIMISTIC (favours the object):** C_node is taken as O(1) with unit constant. Real
   per-node cost includes memory traffic that dominates at frontier sizes above cache.
3. **OPTIMISTIC (favours the object):** de-duplication is assumed free (column 4). Real
   de-duplication needs a 2^(4(32−L))-entry structure and its own memory traffic.
4. **OPTIMISTIC (favours the object):** meet-in-the-middle (column 5) is assumed to have a
   free matching step. It does not; matching costs at least the smaller list.
5. **PESSIMISTIC (favours the barrier reading), and therefore the one to attack:** column 3
   uses J = 2³², the value **measured at six witness kernels**, as if it were the minimum
   over all F-linear π. **It is not established to be the minimum** — see HEUR-806-1. The
   analogue's exhaustive minimum is q³, one factor of q lower; if the same holds over GF(2⁸)
   then J = 2²⁴ and column 3 crosses the baseline at n ≈ 5.3, not n = 4.
6. **OPTIMISTIC (favours the object):** the four words are assumed to need independent
   tracking. If an attacker only needs one word's trajectory, J = B = 2⁸ and column 2 applies,
   in which case **no barrier follows at any n ≤ 7**.

### 5.5 Affected-vs-safe scope statement

* **Pressured** by this accounting: F-linear, round-independent, single-word, single-state,
  deterministic-up-to-bounded-branching projections with L = 24, where Corollary 806-2 gives
  yield Y ≤ 0 — such an object carries **no information at all** across one interface, and
  that is unconditional, not modelled.
* **Weakly pressured:** the same class at L = 16 tracked across n ≥ 4 interfaces **under**
  HEUR-806-1 and HEUR-806-2, and only in the un-deduplicated, non-MITM cost model. With
  de-duplication or MITM the pressure **disappears** within n ≤ 7 (columns 4 and 5).
* **Not reached at all, and why:** (i) **arbitrary non-linear π** — Proposition 806-1's proof
  uses linearity in LEM-806-2 and LEM-806-3 and says nothing outside it (§6);
  (ii) **GF(2)-linear but not F-linear π** — an explicit counterexample is in §6.2;
  (iii) **layer-dependent π^(0), π^(1), …** — OD-1, out of scope for this task; the bound uses
  round-independence at the point where the same K appears on input and output, and with a
  constant π_out the branching collapses to 1 trivially; (iv) **multi-word and set-valued
  objects** — OD-2, OD-3, untouched; (v) **AES at any round count** — nothing here reaches it.

---

## 6. Part IV (CAND-806-F) — arbitrary π: no bound follows

**Result: NO lower bound on B in terms of L alone is derived for arbitrary π, and the
counting route is shown to be blocked rather than merely unattempted.**

### 6.1 Where the counting fails

The natural argument: fix an input π-profile x; the reachable output set is M·(Y₀×Y₁×Y₂×Y₃)
where Y_i is the byte-i image of the fibre π⁻¹(x_{(j+i) mod 4}); then bound
|π(M·∏Y_i)| ≥ ∏|Y_i| / max_fibre. **It fails at the first factor.** A fibre of size 2^L may
lie entirely inside a single fixed-byte coset { v : v_i = c } whenever 2^L ≤ 2²⁴, driving
|Y_i| to 1. Not all four coordinates can collapse for all profiles at once — if π refined the
byte-i partition for every i it would be injective — but B is a **maximum over profiles**, and
the argument needs a **lower** bound on that maximum, which the collapse argument cannot supply.
Nothing weaker than a balancedness hypothesis on π rescues the divisor either, and adding one
would be weakening a definition until something falls out. **It was not added.**

### 6.2 A concrete obstruction

Take π a single GF(2)-linear functional of the 32-bit word, so |X| = 2 and L = 31. Its kernel
K is a GF(2)-hyperplane; for any functional depending on more than one byte, proj_i(K) = F for
all four i, so by the same LEM-806-2 mechanism the reachable perturbation set is F⁴, its image
under M is F⁴, and π(F⁴) = X. Hence **B = 2 = |X| with L = 31**: a lossy π with **tiny B**.
Its yield is Y = log₂|X| − log₂B = **0** — the relation is total and carries nothing. This is
a derivation, not a measurement (no code was run for it), and it establishes two things:

1. **No f(L,n) increasing in L can be a valid lower bound on B**, since B ≤ |X| = 2^(32−L)
   always. OD-4's hoped-for inequality cannot have the hoped-for shape.
2. **B alone is the wrong cost parameter.** The informative quantity is the yield
   Y = log₂|X| − log₂B, which is what Corollary 806-2 bounds. A future statement of OD-4
   should be posed in Y, not in B.

That reframing is the main forward guidance this task produces for OD-4.

---

## 7. Controls, and what they actually isolate (inventor-protocol §3)

A control that discriminates without isolating is this campaign's own demonstrated failure
mode (V-804-1). Each control below negates a **named ingredient** of Proposition 806-1, and a
**sibling null negating the same named ingredient differently** was built before belief. All
are exhaustive over every subspace of the stated analogue.

| control | negates | GF(2⁴) min B | GF(2²) min B | reading |
|---|---|---|---|---|
| **CTRL-NULL-1** block-diagonal, a 2×2 **zero block** | "every entry of M is nonzero", strongest form | **1** | not invertible over GF(2²); skipped | **bound FAILS** — an F-linear lossy π with B = 1 exists (witness K = span(e₀,e₁), S = {0,1}, dim(W_S∩K) = 2) |
| **CTRL-NULL-2** (SIBLING) exactly **one zero entry** | "every entry of M is nonzero", weakest form | **16 = q** | **4 = q** | **bound HOLDS** |
| **CTRL-NULL-3** all entries nonzero, invertible, **not MDS** | "M is MDS" | **16 = q** | **4 = q** | **bound HOLDS** |
| **CTRL-POS** seeded random invertible (seed 20260801806) | nothing (positive control) | **16 = q** | **4 = q** | **bound HOLDS** |

**What this isolates, stated plainly and against my own convenience.** PRED-8 was written
before measurement and **held**: the sibling null did *not* void the bound. Therefore
**CTRL-NULL-1 does NOT isolate "every entry of M is nonzero"** — it isolates the strictly
stronger property **"M has no zero block"**, i.e. that M does not decompose the four
coordinates into non-interacting groups. A report claiming the bound rests on "all entries
nonzero" would be over-attributing exactly as V-804-1 warned. PRED-9 also held: **the MDS
property is not load bearing for the minimum**, only for the per-case value at s = 2 (it
controls whether the s = 2 row reads q² or less). The GF(2²) analogue independently confirms
this: it is **not MDS** and still reads min B = q.

**The property actually doing the work is: no proper nonempty S ⊆ {0,1,2,3} has
W_S ⊆ F^S** — no set of columns of M is supported on its own index set. That is what the
measured max(0, 2s−4) table encodes, and it is the ingredient a future attacker of this
proposition should target.

---

## 8. Numbered heuristics (promotion gate 2)

Proposition 806-1 and Corollary 806-2 are **unconditional** — they rest on no heuristic. The
heuristics below are load bearing **only** for §5's n-interface cost table, and each is
stated formally with a paired validation experiment. Gate (2) is addressed for every
conditional dependence I could identify; TASK-20260801-810 Branch A is invited to hunt for an
unnumbered one, and if it finds one that is a real finding against this package.

**HEUR-806-1 (joint-branching minimum over GF(2⁸)).**
*Formal statement.* Let 𝒦 = { K ≤ F⁴ : 0 < dim K < 4 } and let J(K) = q^rank(Γ_K) where Γ_K
is the F-linear map K⁴ → (F⁴/K)⁴ of `joint_branching`. Then min_{K ∈ 𝒦} J(K) = q³ = 2²⁴, and
the distribution of J over 𝒦 is supported on { q³, q⁴ }.
*Status.* **Unvalidated over GF(2⁸).** Measured exhaustively over GF(2⁴) (min = q³, support
{q³, q⁴}); measured at six GF(2⁸) witnesses, all reading q⁴ = 2³².
*Validation experiment (schedulable).* Distribution: J(K) over all K ≤ GF(2⁸)⁴. Scale:
exhaustive over the 16 843 009 kernels of dim 1 and, by duality, of dim 3; for dim 2, exhaustive
over the 15 support classes S with the intersection dimension enumerated within each class
(the closed form makes this finite and small). Predicted distribution: supported on
{2²⁴, 2³²} with minimum 2²⁴. Tail check: the count of kernels attaining the minimum should
match the GF(2⁴) proportion to within the class-size scaling. **Falsifying outcome: any kernel
with J(K) < 2²⁴, or any kernel with J(K) ∉ {2²⁴, 2³²}.** Needs numpy or C; ~minutes.

**HEUR-806-2 (multiplicativity of branching across interfaces).**
*Formal statement.* For round-independent F-linear π with kernel K, the number of π-trajectories
over n consecutive interfaces consistent with a fixed starting π-state is J(K)^n, i.e. the
composed relation does not collapse.
*Status.* **Unvalidated at every n ≥ 2, and believed FALSE for large n**: the frontier is
bounded by |X|⁴ = 2^(4(32−L)), so J^n must saturate. It is used in §5 column 3 only, and
column 4 shows the saturated alternative beside it.
*Validation experiment (schedulable).* Distribution: |R^(n)(x)| over uniformly chosen starting
π-states x, for n = 1…4, in the GF(2⁴) analogue, exhaustively over all K of dim 1. Predicted:
min(J^n, |X|⁴). Tail check: the fraction of x attaining the maximum should be 1 for the linear
class (the count is x-independent for linear π — itself a prediction). **Falsifying outcome:
any x with |R^(n)(x)| ≠ min(J^n, |X|⁴), or any x-dependence of the count.**

**HEUR-806-3 (cost-model baseline).**
*Formal statement.* The cheapest alternative to tracking the object across n interfaces costs
2¹²⁸ (full 128-bit state enumeration).
*Status.* **A modelling choice, not a fact, and almost certainly generous to the object.**
It is numbered because §5's "beats/does not beat" reading depends entirely on it.
*Validation experiment.* Not a distributional heuristic; it is discharged by **naming and
costing an actual alternative**, which this task does not do and which is **out of scope**
under DEC-20260731-011's strikes (no literature comparison is reachable). Recorded as
**open**, and any conclusion drawn from a comparison against it is conditional on it.

**HEUR-806-4 (independence of the four words' tracking).**
*Formal statement.* Tracking the state requires all four super-box words, so the per-interface
cost is J and not B.
*Status.* **Unvalidated.** If a single word suffices, §5 column 2 applies and no barrier
follows at any n ≤ 7. This is the assumption whose failure most cheaply destroys §5's
reading, and it is stated here rather than left implicit.
*Validation experiment.* Specify the downstream use of the object first; the heuristic is not
testable in isolation. Recorded as **open and blocking** for any barrier reading of §5.

---

## 9. Pre-registration: predictions written first, measurements beside them

The prediction block is in `od4_branching.py` above the imports and was authored before any
phase was executed. **No prediction was adjusted after a reading was seen.**

| id | prediction | measured | outcome |
|---|---|---|---|
| PRED-1 | every entry of M nonzero | true | **held** |
| PRED-2 | M is MDS (all 69 proper minors + det nonzero) | true, 0 zero minors | **held** |
| PRED-3 | dim(W_S ∩ F^S) = max(0, 2s−4) for all 16 S | true for all 16 | **held** |
| PRED-4 | i ↦ (j+i) mod 4 bijective for each j | true for all 4 | **held** |
| PRED-5 | closed form agrees with brute force everywhere | 0 discrepancies over 442 from-definition kernels + 101 + all-GF(2²) enumerations + 3 GF(2⁸) witnesses | **held** |
| PRED-6 | min B = q, independent of dim K | GF(2⁴): 16 = q at d = 1,2,3 over all 78 901 subspaces; GF(2²): 4 = q over all 529 | **held** |
| PRED-7 | CTRL-NULL-1 admits B = 1 | min B = 1 | **held** |
| PRED-8 | sibling CTRL-NULL-2 still reads min B = q | 16 and 4 = q | **held** (and it is the inconvenient outcome — see §7) |
| PRED-9 | CTRL-NULL-3 still reads min B = q | 16 and 4 = q | **held** |
| PRED-10 | CTRL-POS reads min B = q | 16 and 4 = q | **held** |
| PRED-11 | joint < B⁴ at minimising kernels | joint **= B⁴ = 2³²** at all three GF(2⁸) minimising witnesses; joint < B⁴ elsewhere | **PARTIALLY FALSIFIED**, not adjusted |

---

## 10. Promotion gates: status, honestly

**No promotion is requested. No gate is asserted satisfied.** Promotion is the Coordinator's
transition in TASK-20260801-811 and rests on independent review and the red team.

* **Gate (1) proof decomposition — `addressed_in_this_package`** (§4.2: four
  single-responsibility lemmas LEM-806-1…4, an Assembly counting over a **measured** table,
  and §5.1's explicit attempt / per-attempt-cost / success-probability product).
* **Gate (2) numbered heuristics — `partially_addressed`.** Proposition 806-1 and Corollary
  806-2 need **no** heuristic. §5's cost table rests on HEUR-806-1…4, each formally stated;
  **HEUR-806-1 and HEUR-806-2 carry concrete schedulable validation experiments, but
  HEUR-806-3 and HEUR-806-4 do not and are recorded as open.** **What is missing:** a costed
  alternative baseline (HEUR-806-3) and a specified downstream use (HEUR-806-4). Until those
  exist, §5's cost table may not be read as a barrier.
* **Gate (3) concrete cost table — `partially_addressed`** (§5.3–§5.5: table at named toy
  parameter sets, memory, time–memory trade-off, parallelization, hidden-overhead
  disclosure, six individually flagged assumptions with their direction, affected-vs-safe
  statement). **What is missing:** the table's central column uses J = 2³² measured at six
  witness kernels rather than an established GF(2⁸) minimum (HEUR-806-1), and no alternative
  baseline is costed (HEUR-806-3).
* **Gate (4) independent review + red team — `not_addressed`. REQUIRED AND NOT PERFORMED BY
  THIS TASK.** It is scheduled as TASK-20260801-809 and TASK-20260801-810.

**Three gates are cleared or partly cleared and the fourth is named.** Gate (2) is the one
that bites, exactly as the task card predicted, and it bites on the **cost table**, not on
the proposition.

---

## 11. Limitations and residuals

* **R806-1.** Proposition 806-1 covers **F-linear** π only. OD-4's class is arbitrary π. The
  bound is therefore a result about a **strictly smaller** class than the one OD-4 names, and
  must never be quoted as a bound for OD-4's class.
* **R806-2.** The bound is at **one interface**. Every multi-interface number in §5 is a cost
  model, not a derivation.
* **R806-3.** The GF(2⁸) minimum of the **joint** branching is not established (HEUR-806-1).
  Only per-word B ≥ 2⁸ is derived.
* **R806-4.** GF(2⁴) and GF(2²) are **analogues**. The GF(2²) analogue is additionally **not
  MDS**, so it is a weaker analogue than GF(2⁴); this is recorded, not smoothed over.
* **R806-5.** The from-definition brute force did **not** run at dim K = 3 in GF(2²), nor at
  any dimension in GF(2⁴) or GF(2⁸): the perturbation space is q^(4·dim K) and pure Python —
  **numpy is not installed in this environment** — puts all three outside the 1600 s budget.
  Recorded in `od4_results.json` under `checks_not_run`.
* **R806-6.** PROP-701-I's one-interface-per-round identification (its residual R5) is
  unestablished; §5's n is counted in **interfaces**, and the round column is deliberately
  absent.
* **R806-7.** One recollection is used, nowhere load bearing: *`unverified-from-memory`,
  recall confidence LOW* — that MDS matrices are standard in wide-trail designs. Nothing in
  §4 depends on it; M's MDS property is **recomputed here**, not recalled. No other
  literature statement is made and no novelty is claimed or claimable in this environment.

## 12. Forward guidance

1. **Re-pose OD-4 in the yield Y = log₂|X| − log₂B, not in B.** §6.2 shows B alone admits a
   trivial small value at large L with zero information. Corollary 806-2's L + Y ≤ 24 is the
   statement that has content.
2. **The next open question is the non-linear one**, and it is finite and sharp: *does there
   exist a non-F-linear π : GF(2⁸)⁴ → X with L = 8 and B < 2⁸?* LEM-806-2 and LEM-806-3 both
   use linearity; §6.1 shows the counting route to "no" is blocked. Neither a construction nor
   an obstruction is known to this task.
3. **Do not attempt CAND-806-A or CAND-806-E.** They were screened out at 30 interfaces
   against 7 available, and the screen is what saved this task's budget for §4.
4. **HEUR-806-1's validation is cheap and would upgrade gate (3)'s central column** from six
   witnesses to an exhaustive minimum. It needs numpy or a small C program, neither present here.

---

*Artifacts: `prescreen_od4.json` (frozen first), `od4_branching.py`, `od4_results.json`,
`od4_branching_bound_report.md`. Budget declared 1600 s; compute consumed 67 s in a single
run; the task halted on completion, not on the budget.*
