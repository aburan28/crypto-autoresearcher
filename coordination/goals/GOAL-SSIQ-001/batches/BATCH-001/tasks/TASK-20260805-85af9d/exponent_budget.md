# Exponent budget of the p^{1/3+o(1)} algorithm — re-derived from primary text

**Task:** TASK-20260805-85af9d · **Goal:** GOAL-SSIQ-001 · **Batch:** BATCH-001
**Role:** executor · **Compute used:** none (reading task; `runs_authorized: 0`)
**Sole source:** `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`
(`SRC-P13-WESOLOWSKI-2026`, sha256 `ca34a0f784351992df72458b2410ed92a137a1811d5401a24810121116c7a9cf`, 351 lines)
**Companion:** `line_locators.yaml` — 45 verbatim quotations, each sliced from the
file by script at a declared line, never typed from memory.

---

## 0. What this document is, and the four qualifiers it carries throughout

This is a **bookkeeping** document. It decomposes the exponent `1/3` of the
archived result into separately-sourced factors, and it records where each
factor lives in the frozen text. It records **no** judgement about whether any
factor can move. Attainability is `TASK-20260805-87e568`'s question and the
campaign's.

Four qualifiers attach to every appearance of the `p^{1/3+o(1)}` tier below and
are never to be dropped when this document is quoted:

1. **Conditional.** The result holds *assuming Heuristic 1* (line 69). Nothing
   here is unconditional. Line 19: *"Assuming Heuristic 1, there is a Las Vegas
   algorithm which, given a supersingular elliptic curve E/F_{p^2}, finds a
   non-scalar endomorphism α ∈ End(E) \ Z in expected time and memory
   p^{1/3+o(1)}."*
2. **Memory equals time.** Line 39: *"its memory cost is essentially as high as
   the complexity p^{1/3+o(1)}, a serious obstacle for any deployment of the
   algorithm on instances of cryptographic size."*
3. **The o(1) is superpolynomial.** Line 39: *"the overhead hiding in the o(1)
   term is superpolynomial, much larger than the previous (log p)^{O(1)}
   cofactor."*
4. **Expected, not worst-case.** The algorithm is Las Vegas; the cost is an
   expectation over the re-randomisation (line 19, Algorithm 3).

**`0.25` is this program's search target, not a claim.** The string `1/4` does
not occur anywhere in the frozen text (`grep -n "1/4"` returns nothing). Every
"condition for 1/4" in this package is arithmetic on named quantities, and
arithmetic that identifies a condition says nothing about whether the condition
holds.

---

## 1. Audit of the opening reading (goal record `exponent_budget.factors`)

The `F1`–`F4` table in `ledger/goals/GOAL-SSIQ-001/goal.yaml` is a Coordinator
reading that had never been checked. Verdicts:

| row | verdict | what is wrong, if anything |
|---|---|---|
| **F1** | **CONFIRMED** (substance) / **locator corrected** | Statement is accurate. Its home is line **81** (Theorem 1.5), not the proof of Theorem 1.1; it *enters* the argument at line **177**, which opens the proof of **Lemma 3.4**. |
| **F2** | **CORRECTED** — attribution and characterisation | The split bound is **not in the statement of Lemma 3.4** (line 160 contains no `X`). It lives in Algorithm 2 step 1 (line 167) and the proof at lines 177–181. "1/2 of F1" is true of `X`'s exponent but understates the operative identity: **`X = (B·D)^{1/2}` exactly**, so `X² = B·D`. |
| **F3** | **CORRECTED** — attribution and one-sidedness | The cardinality bound is **Lemma 3.2** (line 133), not Lemma 3.3. Lemma 3.3 (line 154) is the *running-time* lemma. The paper states `≤`, not `=`; the matching lower bound appears only in **§4.1** (lines 226–230), i.e. outside the proof of Theorem 1.1. |
| **F4** | **CONFIRMED** and strengthened | Exponent 0 is correct and can be tightened to *provably* 0 (§4). One phrase in the batch opening needs narrowing — see §4.3. |

**A fifth, cross-cutting correction (locator).** Both the goal record
(`exponent_budget.note`) and `RQ-SSIQ-9702af` (`motivation`) say the
decomposition was read from *"the proof of Theorem 1.1, lines 177–218"*. That
range is wrong in both directions:

- The **proof of Theorem 1.1 is lines 193–220**. Lines 177–185 are the proof of
  **Lemma 3.4**; line 187 is Lemma 3.5; line 189 its proof; line 191 Remark 1.
  The cited range therefore spans three proofs and a remark, and it truncates
  the correctness half of the Theorem 1.1 proof (line 220).
- The range **omits the sources of two of the four factors**: Theorem 1.5
  (line 81, all of F1) and Lemma 3.2 / Lemma 3.3 (lines 133 / 154, all of F3),
  as well as Theorem 1.4 (line 77).

The exponent-carrying material is spread over lines **77, 81, 131–135,
154–158, 160–189, 193–218, 226–230**. These are mutable fields of records
outside this task's write scope; the correction is recorded here for the
Coordinator, not applied.

---

## 2. The corrected factor table

`D` denotes the degree bound of Theorem 1.5, `X` the per-side degree bound, `B`
the smoothness bound, `P0` the per-attempt success probability, `#L` the table
cardinality. Exponents are base-`p`.

### 2.1 Factors carried over from the opening reading

| id | quantity | value in the source | p-exponent | provenance | locators |
|---|---|---|---|---|---|
| **F1** | degree bound `D` on the minimal isogeny `E → E^{(p)}` | `(p/2)^{1/3}` | **1/3** | **CITED-NOT-VERIFIED**, ref. [4] | 81, 177, 61, 266 |
| **F2** | per-side bound after the balanced 2-way split | `X = B^{1/2}(p/2)^{1/6} = (B·D)^{1/2}` | 1/6 (= d/k with k=2) | proved here (proof of Lemma 3.4) | 167, 160, 177, 181, 183, 87 |
| **F3** | cardinality of the searched list, as a power of `X` | `#L ≤ Ψ(X,B)·X^{1+o(1)} = X^{2+o(1)}` | q = **2** | upper: proved here (Lemma **3.2**) on the cited count [2, Lem. 5.7]; lower: §4.1 only | 131, 133, 135, 154, 156, 158, 216, 218, 226, 228, 230 |
| **F4** | inverse success probability `P0^{-1}` | `u^{u(1+o(1))} = p^{o(1)}` at `B = e^{(1/3)√log(p/2)}` | **0** | proved here *conditional on Heuristic 1*, on the cited Theorem 1.4 of [10] | 187, 189, 210, 212, 218, 191, 77 |

### 2.2 Factors the opening reading omitted (added by this task)

All four carry **exponent 0**, so §2.1's exponent accounting is unchanged by
them. They are added because **levers act on them**, and a factor absent from
the table is a factor no lever can be attributed to.

| id | quantity | value | p-exponent | why it must be in the table |
|---|---|---|---|---|
| **F5** | smoothness parameter `B` | `e^{(1/3)√log(p/2)}` | 0 | Not an independent factor: it is the **shared knob coupling F2/F3 to F4** (`X = (B·D)^{1/2}`; `u = log(p/2)/(3 log B)`). Any proposal that "tunes B" is moving two factors at once, in opposite directions. Locators 193, 200, 214. |
| **F6** | re-randomisation walk length `n` | `O(log p)` | 0 | Exponent-free but **correctness-load-bearing**: the walk exists so `E′` is indistinguishable from uniform, which is the *hypothesis* of Lemma 3.5 and Heuristic 1. A lever that changes the instance distribution invalidates F4's derivation. Locators 193, 202. |
| **F7** | collision / match mechanism | one linear scan of the single table, keyed by codomain | cost exponent **c = 1** in `#L` | This is the factor L3 and L5 act on, and it was unnamed. Note what the text actually does (line 171): it queries the **same** table at the Frobenius conjugate of each codomain. The "two lists" are one list plus an involution. Locators 171, 185, 39. |
| **F8** | per-step arithmetic (modular polynomial roots) | `(B + log p)^{O(1)}` | 0 | The source explicitly declines to optimise this `O(1)` and says it "will be absorbed in other asymptotics" while being "critical for a practical deployment" (line 156 footnote). Locators 156. |

---

## 3. The arithmetic: how the factors compose

### 3.1 The paper's own assembly (verbatim chain)

Per-attempt cost, Lemma 3.3 (line 154):

> **Lemma 3.3.** Algorithm 2 terminates in time Ψ(X, B)·X^{1+o(1)}·B^{O(1)}, where X = B^{1/2}·(p/2)^{1/6}.

Evaluation and assembly, proof of Theorem 1.1 (lines 216, 218):

> Ψ(X, B) = Xw^{−w(1+o(1))} = p^{1/6+o(1)}p^{o(1)} = p^{1/6+o(1)}.

> We deduce that each attempt costs Ψ(X, B)X^{1+o(1)}B^{O(1)} = p^{1/6+o(1)}p^{1/6+o(1)}p^{o(1)} = p^{1/3+o(1)}. The total expected cost of Algorithm 3 is therefore this latter quantity multiplied by P0^{−1}, which is p^{1/3+o(1)}, as claimed.

So the source's bookkeeping is exactly **per-attempt cost × inverse success
probability**:

```
TOTAL = [ Ψ(X,B) · X^{1+o(1)} · B^{O(1)} ] · P0^{-1}
      = [ p^{1/6+o(1)} · p^{1/6+o(1)} · p^{o(1)} ] · p^{o(1)}
      = p^{1/3+o(1)}
```

### 3.2 Where `X` comes from (F2, re-derived)

The choice of `X` is not free. From line 181:

> deg(η) = deg(φ)/deg(ψ) ≤ ℓ_{k+1}(p/2)^{1/3}/X ≤ B(p/2)^{1/3}/(B^{1/2}(p/2)^{1/6}) = B^{1/2}(p/2)^{1/6} = X.

Read right to left, this is the design constraint. With `D = (p/2)^{1/3}` and
`ℓ_{k+1} ≤ B`, requiring the *second* half to also fit under `X` demands

```
B·D / X  ≤  X      ⟺      X ≥ (B·D)^{1/2}
```

and the paper takes the minimum, `X = (B·D)^{1/2} = B^{1/2}(p/2)^{1/6}`.
**`X` is the geometric mean of the smoothness bound and the degree bound.**
Hence `X² = B·D` **exactly**, not merely up to constants.

### 3.3 The master identity

Substituting `Ψ(X,B) = X·w^{-w(1+o(1))} = X·p^{-o(1)}` and `B^{O(1)} = p^{o(1)}`
into §3.1, and then §3.2:

```
per-attempt cost = X^{2+o(1)} = (B·D)^{1+o(1)} = D · p^{o(1)}      (since B = p^{o(1)})
TOTAL            = D · p^{o(1)} · P0^{-1} = D · p^{o(1)}            (since P0^{-1} = p^{o(1)})
MEMORY           = #L = X^{2+o(1)} = D · p^{o(1)}
```

> **Master identity.** The total time exponent of the archived algorithm equals
> the exponent of the Theorem 1.5 degree bound, and the memory exponent equals
> it too. `1/3` is `1/3` because `(p/2)^{1/3}` is `(p/2)^{1/3}`.

F2 and F3 exactly cancel: the meet-in-the-middle **halves** the degree exponent
(`X ~ D^{1/2}`) and the list is **quadratic** in `X`, returning `D`. This
vindicates the substance of the opening reading's `F1.moves_total_as` and gives
it a two-line derivation it did not have.

A corollary worth recording, because it disciplines every future proposal:
**the naive comparison is `D²`.** Enumerating cyclic smooth isogenies up to
degree `D` directly costs `D^{2+o(1)} = p^{2/3+o(1)}`. The split buys a genuine
square root, from `p^{2/3}` to `p^{1/3}`; it is not decorative. What it does not
do is buy anything *beyond* `D`.

### 3.4 The parameterised identity (the object the 1/4 conditions are solved on)

Introduce a symbol for each factor's exponent, so the target can be stated as an
equation rather than a wish. All are base-`p` exponents; the source's values are
in the last column.

| symbol | meaning | factor | source value |
|---|---|---|---|
| `d` | exponent of the degree bound `D` | F1 | **1/3** |
| `k` | arity of the split (number of pieces) | F2 | **2** |
| `q` | exponent of the searched-family cardinality, as a power of the per-side degree bound | F3 | **2** |
| `c` | exponent of the collision-finding cost, as a power of the per-side cardinality | F7 | **1** |
| `r` | exponent of `P0^{-1}` | F4 | **0** |

With `Y` the per-side degree bound, the same balance argument as §3.2 for a
`k`-way split gives `Y = (B·D)^{1/k}`, so `exponent(Y) = d/k` (as `B = p^{o(1)}`).
Then:

```
per-side cardinality exponent  =  q · d / k
collision cost exponent        =  c · q · d / k
TIME exponent    T  =  c · q · d / k  +  r
MEMORY exponent  M  =      q · d / k
```

Check against the source: `T = 1·2·(1/3)/2 + 0 = 1/3` ✓ and `M = 2·(1/3)/2 = 1/3` ✓,
matching lines 19 and 39.

**Two structural constraints on this identity, both read off the text:**

- **`r ≥ 0` always,** because `P0` is a probability and `P0^{-1} ≥ 1`. The source
  pins it at `≤ 0 + o(1)` (line 212). Hence `r = 0` exactly, and it is the one
  symbol in the table that **cannot be lowered**.
- **`T ≥ M` always,** and in the algorithm *as written* `c` cannot be taken below
  1, because the list must be **built** before it can be searched. Line 158:
  *"The cost of computing the list is thus at most #L · (B + log p)^{O(1)} ...
  The cost of the final loop through the table L is dominated by that previous
  computation."* A lever that only searches faster (`c < 1`) buys nothing unless
  it also avoids materialising the list.

---

## 4. Which factors are exponent-free, and what that refutes for free

**Exponent-free set: `{F4, F5, F6, F8}` — the inverse success probability, the
smoothness parameter, the walk length, and the per-step arithmetic. Each is
`p^{o(1)}`.**

### 4.1 The class of proposals refuted at zero cost

> Any proposal whose entire saving lands in the retry loop — a better success
> probability, fewer attempts, a smarter `B`, a shorter walk, faster modular
> polynomial arithmetic — moves the **disclosed `o(1)`**, not the exponent.

For F4 this is not merely observed but forced: `r ≥ 0` because `P0 ≤ 1`. To take
`T` from `1/3` to `1/4` through F4 alone would require `r = −1/12`, i.e.
`P0 = p^{+1/12} > 1`. **There is no such probability.** F4 is therefore the
unique factor in §3.4 on which the required movement cannot be placed — a hard
arithmetic fact, not a judgement. This **confirms** the goal record's F4 row and
supplies the one-line argument the row asserted without.

### 4.2 F5 is a coupling, not a free lunch

`B` appears in F2/F3 through `X = (B·D)^{1/2}` (larger `B` ⇒ larger list) and in
F4 through `u = log(p/2)/(3 log B)` (larger `B` ⇒ better success probability).
The source's `B = e^{(1/3)√log(p/2)}` is the balance point, and both sides are
`p^{o(1)}` there. A "tune B" proposal is moving F3 and F4 against each other
inside the `o(1)`; the source itself flags this as a *practical* optimisation
(line 200: *"in practice, one may instead precompute an optimal choice of B
minimizing the total expected cost"*).

### 4.3 One narrowing of the batch opening's phrasing

BATCH-001-OPENING §2 says of F4: *"That class of idea is refuted at the
whiteboard, for free, before it is ever dispatched."* That is **correct as
stated about the exponent** and this task confirms it. It would be an
overstatement if carried across to practical impact, and the source is explicit
on the point. Remark 1 (line 191):

> **Remark 1.** Lemma 3.5 is a simple lower bound on the probability, and is not expected to be optimal. Indeed, it considers the single smallest isogeny E → E^{(p)}, and estimates its smoothness probability; but there are generally multiple small (non-cyclic) isogenies E → E^{(p)}, and it is sufficient for any one of them to be smooth. This has already been observed experimentally by Panny through his proof-of-concept implementation [36]. While practically relevant, this phenomenon is absorbed in the hidden term of the asymptotic complexity.

So: success-probability work is **refuted as an exponent lever and endorsed by
the source as practically relevant**. Both halves belong in the record. (The
concrete-cost consequences of the disclosed `o(1)` are GOAL-P13-001's —
`EV-PEC-2e67ff`, `EV-PEC-857664` — cited here, not re-derived.)

---

## 5. Proved here vs cited: the external dependency ledger

Full detail in `line_locators.yaml → cited_not_verified`. Summary:

| result | used for | status |
|---|---|---|
| **Theorem 1.5** — *Yves Aubry, Roger Oyono, and Christelle Vincent. Minimal degree of an isogeny between a supersingular elliptic curve and its conjugate. 2026. arXiv: 2607.14624 [math.NT].* | **F1 — the entire exponent 1/3** | **CITED-NOT-VERIFIED.** Not in this repository. By the master identity (§3.3), the whole headline exponent is this bound's exponent, and this program has not checked it. |
| **Theorem 1.4** — *E Rodney Canfield, Paul Erdős, and Carl Pomerance. "On a problem of Oppenheim concerning "factorisatio numerorum"". Journal of number theory 17.1 (1983), pp. 1–28.* | F3 (`Ψ` evaluation) and F4 (Heuristic 1's random model) | CITED-NOT-VERIFIED |
| **[2, Lemma 5.7]** — *Aardal, Basso, De Feo, Patranabis, Wesolowski. "A Complete Security Proof of SQIsign". CRYPTO 2025.* | F3 — the per-degree count `I(x) ≤ x(log x + 2)`, i.e. the "`~d` isogenies of degree `d`" half of the quadratic factor | CITED-NOT-VERIFIED |
| **[35, Theorem 1]** and **[35, Proposition 8.5]** — *Aurel Page and Benjamin Wesolowski. "The Supersingular Endomorphism Ring and One Endomorphism Problems are Equivalent". EUROCRYPT 2024, Part VI.* | **Corollary 1.2** — transport of the result from OneEnd to EndRing and Isogeny | **CITED-NOT-VERIFIED.** Two distinct results, neither in this repository. Line 21 calls them *"the computational reductions"*; this task has **not** verified their cost, so **no exponent is assigned to them** in §3.4. Any statement that this goal's target applies to EndRing or Isogeny inherits this unchecked dependency. |
| **[37]** Pizer, and **[6, Lemma 14]** Basso et al. | F6 — uniformity of the re-randomised `E′`, hence the hypothesis of Lemma 3.5 | CITED-NOT-VERIFIED |
| **[27, Section 25.2]** Galbraith | F8 — modular polynomial root finding | CITED-NOT-VERIFIED |
| **[43]** van Oorschot–Wiener | F7 — the tradeoff curve `√(N³/w)` | CITED-NOT-VERIFIED |

**Heuristic 1 is a different category:** an explicitly stated assumption, not a
cited theorem. It is not "unverified" — it is *assumed*, and per
`docs/claims-and-verification.md` no amount of experiment discharges it.

---

## 6. What the frozen text does not say

Recorded so that no later record attributes these to this source. Search method
for each is in `line_locators.yaml → checked_and_absent`.

1. **No occurrence of `1/4` anywhere.** The target exponent is this program's.
2. **No lower bound on the minimal degree of `E → E^{(p)}`, and no Minkowski-type
   argument.** The word "Minkowski" does not occur. The obstruction named in
   lever **L1** of the goal record is therefore **not sourced from this text**;
   establishing it is TASK-20260805-87e568's job, and until then L1's ceiling is
   asserted, not shown.
3. **No claim of optimality** for `(p/2)^{1/3}` or for `p^{1/3+o(1)}`.
4. **No `Õ(p^{1/4})` figure for the F_p-restricted problem.** The only complexity
   this text attaches to Delfs–Galbraith [21] is `p^{1/2}·(log p)^{O(1)}`
   (line 51: *"A memory-free algorithm with the same complexity"*). This frozen
   text can neither establish nor contest the contested figure at KN-TECH-058
   RC4; it is silent. Lever **L4**'s baseline gets no support from here.
5. **No discussion of splits into three or more pieces.** The `k ≥ 3` arithmetic
   in `target_conditions.md` is this task's own bookkeeping on the paper's
   formulas, labelled as such.
6. **No higher-dimensional / Kani-style isogeny machinery** in the enumeration.
7. **No precomputation amortised across instances.** The cost model is
   single-instance expected time.
8. **No quantum time-exponent improvement.** Line 41 relays the opposite
   suggestion, for the vOW setting.

---

## 7. Where each existing lever acts, on the corrected table

Bookkeeping only — no verdict on any lever. `L1`–`L5` are from
`ledger/goals/GOAL-SSIQ-001/goal.yaml`; additions are in `lever_additions.md`,
and `L1`–`L5` is explicitly **not** exhaustive.

| lever | symbol in §3.4 | note after this audit |
|---|---|---|
| L1 | `d` | Acts on the one factor that is CITED-NOT-VERIFIED. Its named obstruction is not in this text (§6.2). |
| L2 | `q` | Must restrict to a **sub-family**: `q = 2` is pinned *two-sidedly* for the full list (Lemma 3.2 above, §4.1 below), so no better *counting* is available. See `target_conditions.md` §4 for the sharpened condition. |
| L3 | `c` | Blocked by the build-cost dominance of line 158 unless the list is also not materialised — see addition A3. |
| L4 | `d` (via a different object) | Its baseline is unsupported by this text (§6.4). |
| L5 | `M` at fixed `T` | Moves along the vOW curve (line 39), which trades memory for **more** time. It does not appear in the `T` equation except through `c ≥ 3/2` in the polynomial-memory regime. |
| — | `k` | **No existing lever targets the split arity.** See addition A1. |
| — | `r` | **Cannot be targeted.** §4.1. |

---

## 8. Completion-gate self-check for this file

- Every factor F1–F8 has ≥ 1 verbatim locator in `line_locators.yaml`: **yes**
  (45 locators; none of the eight factors is unestablished).
- Each opening row marked confirmed or corrected with the correction given:
  **yes** (§1).
- Arithmetic shown for the composition: **yes** (§3.1–§3.4).
- Exponent-free factors identified and the refuted class named: **yes** (§4).
- Proved vs cited separated: **yes** (§5).
- No statement, implication, or arrangement suggesting a `p^{1/4}` algorithm
  exists, is likely, or is near: **asserted**; §0 and §6.1 state the opposite
  explicitly.
