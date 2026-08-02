# RED TEAM — TASK-20260801-810 — GOAL-AES-001 BATCH-004

**Role** red-team (adversarial, independent session) · **Snapshot under review** `cc660597e3bcc616521bce443b9a17eafa4393c2` · **Binding receipt** `db4b321a`

**Timing.** Start `2026-08-01T16:04:49Z` (measured, `date -u`). Budget 1000 s, binding stop at `2026-08-01T16:21:29Z`. Section stamps recorded in §9. This task has NO measured comparable in this campaign; the elapsed figure in §9 is the campaign's first red-team datum and is reported as measured whichever way it falls.

**Independence statement (mandatory, standing basis `0137a051eb5828789eb267fa83c8278086578d4c`).** This session supplies independence in **SESSION** and **NOT in MODEL**. It resolves to `claude-opus-5`, the same model as both producers (TASK-20260801-806, -807), the TASK-20260801-809 validator, and the Coordinator. Agreement between this report and the validator is **CORRELATED, not independent, confirmation**. Nothing here may be treated as a closure attestation under CLAUDE.md rule 8. `model_verified: false` — `python3 -m orchestration.adapter doctor --probe` was not run.

**State assertions.** None. No hypothesis status, no evidence strength, no promotion recommendation, no ledger record, no knowledge promotion. Nothing here asserts anything about AES security at any round count. No producer artifact was modified; all writes are under this task's own directory.

**Literature.** Zero literature comparisons are made. No primary source is reachable in this environment; every literature statement anywhere in this campaign is `unverified-from-memory` and novelty is unresolvable here. I neither smuggle in a recalled citation nor rebut one with another recollection.

---

## 0. Evidence integrity — CONFIRMED

All eight declared source paths were re-hashed from the committed tree with
`git show cc660597:<path> | sha256sum`. **All eight digests match `source_path_sha256` in the receipt exactly.** Parent `3e6b8b73` and commit subject confirmed via `git log`. No integrity failure. I read only committed bytes.

## 1. Branch determination — **BRANCH A**, and Branch B also run

**BRANCH A.** The committed package contains cost and asymptotic statements at more than one strength: Proposition 806-1 (`B >= q = 256`, unconditional, F-linear class), Corollary 806-2 (`L + Y <= 24`), and §5.3's cost table in `n` with an explicit per-attempt-cost × inverse-success-probability product, memory column, MITM column and parallelization claim. Under the handoff constraint ("BRANCH A if any cost or asymptotic statement exists at any strength"), this is unambiguously Branch A.

The dispatching card additionally directs Branch B (pre-screen attack) as live. **Both were run.** Branch A findings are §§2–4; Branch B is §§5–6.

---

## 2. BRANCH A — the cost model attacked

### 2.1 RT-1 (MAJOR, **DEMONSTRATED**) — a GF(2^8) witness BELOW the central column's J, found in seconds

The cost table's central column uses `J = 2^32`, "MEASURED at six GF(2^8) witness kernels", and the producer correctly flags (§5.4 item 5) that this is *not* established as the GF(2^8) minimum. I attacked it and **found a witness below it.**

**Derivation.** For `dim K = 1`, `K = span(v)`, `joint_branching` returns `q^rank` of the four generators `g_t`, whose block `j` is `v_{(t-j) mod 4} · m_{(t-j) mod 4}` reduced mod `K`. Writing `c_i = v_i m_i mod K` and identifying the four generators with the ring `R = F[x]/(x^4+1) = F[x]/(x+1)^4` (char 2), rank `< 4` holds iff a nonzero `a ∈ R` annihilates `c`, iff every component of `c` is a non-unit in the local ring `R`, iff `sum_i c_i = 0` in `F^4/K`, i.e.

> **`rank <= 3`  ⟺  `M v ∈ span(v)`  ⟺  `v` is an eigenvector of MixColumns over `F`.**

`M` is the circulant with symbol `c(x) = 02 + 03x + 01x^2 + 01x^3`; over `GF(2)`, `x^4+1 = (x+1)^4`, so `M`'s only eigenvalue is `c(1) = 0x01`, and `(c+1)(1) = 0`, so `M + I` is singular. **`ker(M+I)` is nonzero.**

**Measurement, using the producer's own unmodified `joint_branching` and `branching_closed_form` from `od4_branching.py` at snapshot `cc660597`:**

```
rank(M+I) = 3;  nullspace basis of M+I = [ (0x1, 0x1, 0x1, 0x1) ]
K = span(1,1,1,1)  [= ker(M+I)]   dim K = 1   J = 2^24   per-word B = 2^24
K = span(e0)       [806 witness]  dim K = 1   J = 2^32   per-word B = 2^8
K = span(m0)       [806 witness]  dim K = 1   J = 2^32   per-word B = 2^24
```

Reproduction: extract `od4_branching.py` from `cc660597`, `exec` everything above `def main()`, call `joint_branching(GF256, [[2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]], [[1,1,1,1]])`. Runs in well under a second.

**Why the producer's six witnesses missed it.** I additionally scanned, with the same code, **1 534 dim-1 kernels of support ≤ 2** (all of them) and **3 000 random full-support dim-1 kernels**: *every single one reads `J = 2^32`.* The low-`J` kernel is the unique (up to scalar) eigenvector — a measure-zero, highly structured object. The producer's witnesses (`e_i`, `m_0`, …) were structured, but structured along **support**, which is the wrong axis; the discriminating axis is **eigenvector-ness**. This is precisely the role-contract failure mode: a quantity validated on instances that are structured in a way that is not the way that matters.

**Consequences, all inside the producer's own model.** With `J = 2^24`: column 3 crosses the `2^128` baseline at `n ≈ 5.33` rather than `n = 4`; the `n = 7` MITM entry becomes `2^84`, not `2^112`. **The central column is not merely unestablished — a cheap counter-witness exists, and it moves every barrier-relevant number in the table.**

**Scope honesty against myself.** This does *not* falsify HEUR-806-1; it **confirms** HEUR-806-1's predicted minimum `q^3 = 2^24` over `GF(2^8)`, which the producer listed as unvalidated there. I did **not** establish that `2^24` is the global minimum over all `K` (I searched dim-1 exhaustively-by-criterion and dim-2 only in the 1 020 kernels containing `(1,1,1,1)`, all of which read `2^56`). A kernel with `J < 2^24` is **UNRESOLVED**.

### 2.2 RT-2 (MAJOR, **DEMONSTRATED**) — column 3 exceeds its own object's frontier ceiling; the barrier reading and the producer's own MITM weakening are both computed above the ceiling

The frontier of the `n`-interface traversal lives in `X^4 = (F^4/K)^4`, which has `F`-dimension `4(4 − dim K)`. Hence the frontier size is capped at `q^{4(4−dim K)}`, **unconditionally**, at every `n`:

| dim K | L | frontier ceiling | column-3 value `2^{32n}` first exceeds ceiling at |
|---|---|---|---|
| 1 | 8 | `q^12 = 2^96` | `n = 4` (`2^128 > 2^96`) |
| 2 | 16 | `q^8 = 2^64` | `n = 3` (`2^96 > 2^64`) |
| 3 | 24 | `q^4 = 2^32` | `n = 2` (`2^64 > 2^32`) |

The witnesses that generate `J = 2^32` are the three minimising witnesses at `dim K = 1, 2, 3`. **For every one of them, the `n = 7` entry `2^224` is impossible**, and so is the MITM entry `2^112` (both exceed the largest ceiling, `2^96`). The two numbers on which the whole §5 reading turns — the `n = 4` crossing of `2^128` (the barrier reading) and the `n = 7` MITM value `2^112` (the producer's own honest weakening of the barrier reading) — are **both above the ceiling of the object being counted, and are therefore not attainable frontier sizes.**

The producer *is* aware of saturation: HEUR-806-2's status says "believed FALSE for large n: the frontier is bounded by `|X|^4`, so `J^n` must saturate", and column 4 shows a saturated alternative. **But the saturation flag was not carried into the numbers it invalidates.** Column 4's cap is computed at `L = 16`, while column 3's `J = 2^32` is generated at witnesses spanning `dim K = 1,2,3`; the table therefore places a cap for one kernel dimension beside an uncapped count for another, and the affected-scope statement §5.5 then says "weakly pressured: the same class at `L = 16` tracked across `n ≥ 4`" — at `L = 16` the ceiling is `2^64`, already reached at `n = 2`, so the entire `n ≥ 4` window named as "weakly pressured" is past saturation.

**Narrowest valid conclusion.** No entry of column 3 with `n ≥ 2` survives its own object's ceiling except where it coincides with it. Nothing in the table supports a statement of the form "the cost crosses `2^128` at `n = 4`".

### 2.3 RT-3 (MAJOR, **DEMONSTRATED omission**) — UNNUMBERED CONDITIONAL DEPENDENCE #1: the nonlinear layer between consecutive interfaces

This is the highest-value class of finding available on Branch A and I report it as MAJOR as the card requires.

`Φ = ARK ∘ MC ∘ SR` is **purely affine**. Proposition 806-1, LEM-806-2 and LEM-806-3 are proved for **one** such `Φ`. §5 then multiplies the per-interface factor across **`n` consecutive super-box interfaces**. The word "SubBytes" appears **zero times** in `od4_branching_bound_report.md` (verified by grep over the committed bytes; "S-box", "sbox", "nonlinear" also zero). The composition model is therefore silently in one of two states, and neither is stated:

* **(a) No nonlinear layer between interfaces.** Then `Φ^n` is a *single affine map*, and the `n`-interface branching is `q^{rank}` of the composed generator system, which saturates at `4(4−dim K)` — exactly RT-2's ceiling — and is emphatically not `J^n`. The "n consecutive interfaces" framing then has no cipher content: it counts compositions of an affine map with itself.
* **(b) A nonlinear layer is present** (as it is between AES super-box interfaces). Then `π ∘ SB` is **not `F`-linear** at interfaces 2…n, so Proposition 806-1 — whose proof uses `F`-linearity twice, at LEM-806-2 and LEM-806-3 — **does not govern any interface after the first**, and the per-interface factor `J` has no derived status there at all.

HEUR-806-2 numbers only *multiplicativity/saturation*. It does **not** state the class assumption that the object remains `F`-linear across the composition, which is what alternative (b) destroys. **This is an unnumbered conditional dependence on which the entire `n`-dependence of §5 rests.** Under alternative (b), §5.3 is not a cost table for a chain of AES interfaces; it is a cost table for `n` independent copies of one affine interface.

I record, against my own convenience, that the producer's §0 disclaimer ("not a barrier statement, nothing asserts anything about AES") and residual R806-2 ("every multi-interface number in §5 is a cost model, not a derivation") absorb some of this. They do not absorb the specific defect: the missing dependence is not "this is a model", it is "the model's per-step factor is derived in a class the model's own composition leaves".

### 2.4 RT-4 (MODERATE, **DEMONSTRATED omission**) — UNNUMBERED CONDITIONAL DEPENDENCE #2: round-key obliviousness is never charged

LEM-806-2 disposes of ARK with "ARK contributes a fixed translation and does not change any cardinality." That is correct **for cardinality at one interface with a fixed key**. §5 then costs an *attacker-style* traversal — "attempt", "per-attempt cost", "success probability", against a `2^128` enumeration baseline — in which the traversal must evaluate `R_j` at each node. The **set** `R_j(x) = π(W_S + const)` is a coset whose *representative* depends on the round key; only its size is key-independent. A traversal across `n` interfaces therefore requires either (i) knowledge of `n` round-key contributions, which is not charged anywhere and which the `2^128` state-enumeration baseline does not assume, or (ii) a union over key hypotheses at each interface, which multiplies the frontier. **Neither is stated, numbered, or costed.** The words "round key" and "key schedule" appear nowhere in the report outside the LEM-806-2 sentence.

This is a per-attempt-cost × inverse-success-probability defect of the type the card names: the success probability is asserted as `p = 1` "by the definition of the object", which is true only if the relation is known, and knowing it is not free.

### 2.5 RT-5 (MODERATE, **UNRESOLVED**) — UNNUMBERED CONDITIONAL DEPENDENCE #3: intermediate-profile reachability

`J^n` counts paths in a product structure and thereby assumes every profile in the frontier at interface `i` is a **realizable input profile** at interface `i+1`. Consistency/reachability of intermediate profiles is nowhere asserted. HEUR-806-2's tail check touches the neighbouring question (x-independence of the count for linear `π`) but not this one. I could not settle whether it fails within budget; recorded UNRESOLVED, not refuted.

### 2.6 The mandated cost-model checks, each attempted, each reported — **including the ones that found nothing**

| check | outcome |
|---|---|
| omitted / absorbed costs | **FOUND**: round-key knowledge (RT-4); de-duplication structure (producer flags as §5.4-3 but does not cost); MITM matching step (producer flags as §5.4-4 but does not cost). The producer's `o(1)` disclosure for general `π` (a `2^72`-entry table) is honest and correctly excluded from the F-linear table. |
| per-attempt × 1/p product | **FOUND (RT-4)**: `p = 1` is asserted from the object's definition, valid only under relation-knowledge. No double-counting found; the frontier/single-guess forms are correctly reconciled up to `C_node·n`. |
| memory accounting | **PARTLY SOUND.** Memory is stated (`2^{32n}` un-deduplicated, `2^{4(32−L)}` deduplicated) and the 15 GB / `2^34`-byte machine limit is disclosed. But by RT-2 the un-deduplicated figure is above the ceiling for `n ≥ 2–4`, so the memory column inherits the same defect. Depth-first `O(n)` memory at equal time is correctly noted. |
| time–memory tradeoff | **PRODUCER-DISCLOSED AND I CONCUR IT WEAKENS THE BARRIER.** The MITM row (`2^112` at `n = 7`) is recorded by the producer itself as materially weakening any barrier reading. By RT-1 it is `2^84` and by RT-2 it is above the ceiling anyway. The producer disclosing a number that hurts its own reading is creditable and I say so. |
| parallelization | **NOTHING FOUND BEYOND WHAT IS STATED.** "Embarrassingly parallel, P cores divide wall clock, memory unchanged in depth-first form" is correct for frontier expansion. What does *not* parallelize — de-duplication (a global structure) and the MITM matching step — is not named; minor, and only because those steps are not costed at all (RT-4 covers it). |
| regime where the advantage disappears, inside claimed scope | **FOUND, and the producer names one of them itself.** (i) `L = 24`: `Y ≤ 0`, no information crosses — the producer states this as *pressure*, and it is equally a statement that the object is uninteresting there. (ii) HEUR-806-4 false (single word suffices) ⇒ column 2, `J = 2^8`, **no barrier at any `n ≤ 7`**. (iii) RT-1's kernel: `J = 2^24`. (iv) RT-2: saturation, at `n = 2` for `L = 24`. |
| affected-vs-safe honesty, both directions | **MOSTLY HONEST, ONE INFLATION.** The "not reached at all" list (arbitrary nonlinear `π`, GF(2)-linear-not-F-linear `π`, layer-dependent `π`, multi-word/set-valued, AES at any round count) is accurate and unusually complete; nothing is claimed *safe* that is merely untested, because nothing is claimed safe. The inflation is on the *pressured* side: "weakly pressured … at `L = 16` across `n ≥ 4`" is void by RT-2 (saturated at `n = 2`). |

---

## 3. BRANCH A — every numbered heuristic attacked

**HEUR-806-1 (joint-branching minimum over GF(2^8)).** *Is the formal statement the assumption the proof uses?* No — the **table uses the opposite direction.** HEUR-806-1 asserts `min J = q^3 = 2^24`; column 3 uses `2^32`. So the table is not conditional on HEUR-806-1 being **true**, it is conditional on HEUR-806-1 being **false at the witnesses**, which is a different and unstated proposition. That mismatch is itself a defect (**RT-6, MODERATE, DEMONSTRATED**): a heuristic is numbered in the direction that is not the direction the cost model needs. *Structured/degenerate instance?* **Yes, exhibited** — RT-1's `ker(M+I)`. *Can the validation experiment falsify?* **Yes**, genuinely: "any kernel with `J(K) < 2^24`, or `J(K) ∉ {2^24, 2^32}`" is a real falsifier, and the experiment is well-specified. It is not a confirmation exercise. Credit where due. My RT-1 is a partial early execution of it and it came out on the heuristic's side.

**HEUR-806-2 (multiplicativity across interfaces).** *Is it the assumption used?* **No — it is weaker than what §5 needs.** §5 needs (a) multiplicativity, (b) `F`-linearity preserved across the composition (RT-3), and (c) intermediate-profile reachability (RT-5). Only (a) is numbered. *Degenerate instance?* Trivially yes — the producer says so itself ("believed FALSE for large n"). *Can the experiment falsify?* Yes, and it is well designed (`|R^(n)(x)| ≠ min(J^n,|X|^4)` or any x-dependence). But it is scheduled **in the GF(2^4) analogue only**, and its falsifier is stated against `min(J^n, |X|^4)` — i.e. it tests the *saturated* form, which is not the form column 3 uses. **The experiment cannot falsify the use column 3 actually makes of the heuristic.** (**RT-7, MODERATE, DEMONSTRATED.**)

**HEUR-806-3 (baseline `2^128`).** OPEN, by the producer's own admission, with no validation experiment and none possible under the literature strikes. *Attack:* it is not merely open, it is **known-generous in a named direction** — the producer says "at 3–7 rounds cheaper alternatives certainly exist". A baseline that is known to be too high, by an unquantified margin, cannot support any "beats/does not beat" statement in either direction.

**HEUR-806-4 (four-word independence).** OPEN, untestable in isolation by the producer's own statement, and **blocking**: its failure puts column 2 in force and, in the producer's own words, "no barrier follows at any `n ≤ 7`".

### R-2 ruling — does the table support ANY barrier reading while HEUR-806-3 and -4 are open?

**NO. Not any reading, at any strength, in either direction.** The reasoning is short and does not depend on any of my findings:

1. HEUR-806-4 open ⇒ the correct column may be column 2 (`J = 2^8`), where the maximum entry at `n = 7` is `2^56` — six orders of magnitude of exponent below the baseline. **A cost model that cannot distinguish `2^56` from `2^224` at its own headline parameter is not a cost model, it is a range.**
2. HEUR-806-3 open ⇒ there is no baseline to be above or below, and the one named is known-generous.
3. Independently of both, RT-2 shows the `n ≥ 2` entries of the column that would carry a barrier are above the object's own ceiling, and RT-1 shows the column's per-interface factor is beaten by an exhibitable kernel.

The producer states conclusion 1–2 itself ("Until those exist, §5's cost table may not be read as a barrier") and gate (3) is self-marked `partially_addressed`. **I concur with the producer's self-assessment and go further: with RT-1 and RT-2, the table does not support a barrier reading even if HEUR-806-3 and -4 were closed tomorrow.** The MITM row the producer volunteered is not the only thing weakening the barrier; it is the mildest.

---

## 4. Analogue-to-cipher transfer (both branches)

* `GF(2^4)` and `GF(2^2)` are analogues; the producer labels them so, in bold, repeatedly, and explicitly says their readings are not evidence about `GF(2^8)`. The `GF(2^2)` analogue is disclosed as **not MDS**. This is done to a standard I could not fault, and I attempted to.
* One transfer *is* load bearing and is correctly numbered rather than smuggled: the `GF(2^4)` exhaustive minimum `q^3` → `GF(2^8)` is HEUR-806-1, not a fact. Correct handling.
* **The transfer that is NOT argued** is the one in RT-3: from a single affine interface to `n` chained interfaces. That is not an analogue-to-cipher transfer of fields; it is a transfer of *class* along the composition, and it is unargued.
* My RT-1 witness is in `GF(2^8)`, not an analogue, and is therefore not exposed to this objection.

## 5. BRANCH B — the pre-screen attacked

### 5.1 RT-8 (MAJOR, **DEMONSTRATED**) — the two sibling screens assign `n = 30` and `n = 1` to the same structural object, and the inconsistency killed the one candidate that attacked OD-4's actual question

Both screens declare "language and threshold deliberately identical". They are not applied identically.

* `prescreen_od3.json` freezes, **before any work**: for a **round-independent** `π`, every `(λ,k)`-graph traversal step "happens AT THE SAME SINGLE INTERFACE with the SAME `pi` … Its interface constant is therefore `n = 1`, not 32." Proposition 801-1's 32 is attributed **specifically to layer-dependence**.
* `prescreen_od4.json` kills **CAND-806-A** ("re-run Steps 1–3 with B-confinement, close under the group") at **`n = 30`**, reading the graph's forward diameter as an interface count.

But OD-4's object is **explicitly round-independent** — §2 of the 806 report: "*round-independent (the same `π` before and after the interface)*". By 807's own frozen rule, **CAND-806-A's interface constant is 1, not 30, and it should have been PURSUED.** The same applies to CAND-806-E.

This is exactly the R-4(ii) target: *a candidate discarded on a constant that a better argument would have reduced below 7.* I did not have to invent the better argument — **the campaign's own sibling screen, frozen the same day, supplies it.**

Which screen is right? **807's is.** The screen's own `question_c` defines `n` as "the number of consecutive **super-box interfaces** over which the tracked object must survive". For a round-independent `π`, Steps 1–3 iterate over the **invariance group of translations**, not over successive applications of `Φ`; the states differ but the interface does not. 806's `n = 30` reads a *graph diameter* as an *interface count*, which is a category error, and it is the same category error DEC-20260731-014 was right to make for Proposition 801-1 **only because that `π` was layer-dependent**.

**Materiality.** CAND-806-A is the route to OD-4's hoped-for inequality. Its content was partly recovered anyway (806 §3 shows the induction breaks under `B > 1`), so the kill was *partly* moot — but not wholly: 806 §3.3 route 2, "a bounded-index subgroup statement replacing the group closure", is precisely CAND-806-A's remaining content, is explicitly left as "a genuine open question … not answered here", and was screened out at a constant its sibling says is 1.

### 5.2 RT-9 (MAJOR) — the "no upper bound exhibited" kill rule is NOT defensible as a vacuity verdict

Two candidates were killed on this rule: **CAND-806-E** ("no upper bound exhibitable") and **CAND-B4** ("no upper bound exhibited").

The card asks whether the rule is defensible. **As a budget-triage rule inside a bounded batch, yes** — you cannot schedule work whose size you cannot state, and saying so is honest. **As an `IN_SCOPE_VACUOUS` verdict, no.** `IN_SCOPE_VACUOUS` is a predicate on the *candidate*: it asserts the argument needs more interfaces than the scope affords. "No upper bound exhibited" asserts only that *the producer, in the time it had, could not bound it*. Those are different propositions and the screen records the second under the label of the first.

Per `docs/inventor-protocol.md` §4 a closure needs a **named obstruction**, an argument, and forward guidance. "I could not bound `n`" names no obstruction. It is, in the language of the protocol, a **fatigue report about the search, not a statement about the problem** — and the campaign should say so in those terms. Note that CAND-806-E's entry hedges toward the defensible form ("`IN_SCOPE_VACUOUS` on **both** grounds", the other ground being a lower bound of 30) whereas **CAND-B4 was killed on the unbounded ground alone**, with the mitigation that 807 carries it forward as a named residual (§4.4) rather than as a closure. That mitigation is real and I credit it; the label is still wrong.

**Recommended (not enacted; I change nothing): a distinct verdict value, e.g. `DEFERRED_UNBOUNDED`, kept out of any count of candidates the screen has *ruled* vacuous.** As things stand, "3 of 7 killed" and "2 of 6 killed" are counts that mix a ruling with an abstention.

### 5.3 RT-10 (MODERATE) — the ~7 threshold is a bound on the wrong quantity, and RT-8 shows it

The threshold basis is: RQ-AES-001 scopes 3–7 rounds; PROP-701-I's one-interface-per-round convention ⇒ at most 7 interfaces. Residual R5 records that this convention is **established by nothing in this campaign**, and both screens say so.

* **Direction of error under the alternative conversion.** The screens check the tighter conversion (1 interface = 2 rounds ⇒ at most 3) and every PURSUE survives it. That check is sound and I credit it.
* **The unchecked direction.** `prescreen_od4.json` asserts "*No conversion known to this task makes MORE than 7 interfaces available inside RQ-AES-001's round scope*". That is a claim about *available cipher interfaces*. The screen applies the number to a different quantity: *the argument's iteration count*. **RT-8 / 807's own `n = 1` rule proves these are not the same quantity** — an argument can iterate arbitrarily many times at one interface, and (symmetrically) an argument could in principle consume interface-visits that are not in bijection with distinct rounds. A bound on the first is not a bound on the second. So the threshold is unsound not because 7 is the wrong number but because it bounds a resource the screen is not measuring.
* **Knowable direction of the error, as the card asks:** if R5's convention is wrong in the direction that a super-box spans two rounds, the true in-scope budget is **3**, and the screen is **too permissive**, not too strict. Every PURSUE at `n = 1` survives that, so no current verdict flips — but the margin the screen advertises (e.g. "margin 23" for CAND-806-A) is computed against 7 and is overstated by more than a factor of two under the tighter conversion.

### 5.4 RT-11 (MODERATE) — the screen is dodgeable in principle, and its real discriminating variable is layer-dependence, not iteration count

By 807's rule, **any** candidate can be re-posed with a round-independent `π` and thereby obtain `n = 1`, however many graph steps it takes. The screen therefore does not filter on iteration count, which is what its `anti_relabelling_clause` advertises; **it filters on layer-dependence.** Every `IN_SCOPE_VACUOUS` verdict across both tasks (CAND-806-A/E under 806's reading, CAND-B3/B4/A3 under 807's) tracks layer-dependence or unboundedness, and no candidate was ever killed for taking many steps at one interface.

**Did either producer dodge?** *Not culpably, and I say so explicitly.* 807 froze the `n = 1` distinction in `prescreen_od3.json` **before any derivation and before any code**, with the written justification "*stated here, before any work, so that it cannot be constructed afterwards to dodge the screen*", and the freeze is anchored by a committed SHA-256 rather than an mtime (the V-804-2 response). I verified the ordering claim is anchored in committed bytes. **The pre-registration holds.** The defect is in the rule, not in its author's conduct — and the fact that the rule's author anticipated exactly this charge is evidence for good faith and against the rule's clarity simultaneously.

### 5.5 RT-12 (MINOR) — the "routes through a different machine" escape

Used for every PURSUE in 806 (CAND-806-B/C/D/F: "routes through the coordinate-support and minor structure of `M`", "arithmetic on a cost model", "fibre cardinalities at one interface"). **Substantive, not a label, for B/C/F**: §4's proof demonstrably uses support/minor algebra and never the `(λ,k)` graph, and §7's controls target the support property, not the graph. **Weakest for CAND-806-D** ("routes through arithmetic on a cost model; `n` is a free parameter of the table, not a constant that must be reached") — that is close to circular, since a cost table in `n` is precisely an object whose content is `n`-many interfaces. Given RT-2 and RT-3, CAND-806-D is the candidate whose escape deserved scrutiny and got the least.

### 5.6 R-5 RULING — is 807's `n = 1` the relabelling the anti-relabelling clause forbids?

**RULING: NO — the `n = 1` claim is CORRECT, and the asymmetry with 806 is real but resolves in 807's favour, not 806's.**

*Why it is not a relabelling.* The anti-relabelling clause forbids repackaging `n` steps as one lemma. 807 does not repackage steps; it observes that the steps were never interface-steps. The screen's own `question_c` measures "consecutive **super-box interfaces** over which the tracked object must survive". For a round-independent `π`, Steps 1/2/3 quantify over translations `t ∈ F^4` and states `s`, all evaluated against **one** map `Φ` with **one** `π`. The `(λ,k)` graph is a graph on the invariance group, not a time axis. No sequence of distinct cipher interfaces is consumed. `n = 1` is the correct reading of the screen's own definition.

*Why Proposition 801-1's 32 is nevertheless legitimate.* There `π` is **layer-dependent**: `π^(l)` and `π^(l+1)` are different maps, so relating them across a graph step genuinely requires traversing fresh cipher interfaces, and `2 + 2n* = 32` is a count of real interfaces. The asymmetry between `n = 1` and `n = 32` is **not** an asymmetry between two treatments of the same object; it is the difference between an index over a group and an index over time. **The legitimising feature is layer-dependence, and it is the right feature.**

*The three qualifications I attach, none of which overturn the ruling.*

1. **The asymmetry that is NOT legitimate is 806-vs-807, not 807-vs-801.** By this ruling, 806's `n = 30` for round-independent CAND-806-A is **wrong** (RT-8). 807 is right and 806 is wrong, on the same day, under screens declared identical.
2. **The screen's advertised variable and its operative variable have come apart** (RT-11). If `n = 1` is right, then interface count is nearly always 1 for this campaign's round-independent objects, and the screen decides almost nothing for them. It should be renamed for what it does: a **layer-dependence screen**.
3. **`n = 1` is not a licence.** An argument that takes 30 group-traversal steps at one interface is not thereby cheap, tractable, or in scope — it is merely not *interface*-vacuous. The screen was never a proxy for tractability and must not be read as one now that its threshold binds on almost nothing.

### 5.7 Attempt to construct the bound 806 says does not exist — **I COULD NOT WALK PAST IT**

806 §6.2 derives: a single `GF(2)`-linear functional gives `|X| = 2`, `L = 31`, `B = 2`; hence `B ≤ |X| = 2^{32−L}` always; hence no `f(L,n)` increasing in `L` can lower-bound `B`.

**I attacked this and it holds.** The core inequality `B ≤ |X|` is not a modelling step — `B` is a cardinality of a subset of `X`, so it is an identity of the definition, and no choice of object class can evade it. The derivation is **sound and correctly scoped**, and it is a genuine named obstruction, not a fatigue report. It meets the inventor-protocol §4 closure standard: named obstruction (the trivial ceiling), argument (one line, checkable), forward guidance (re-pose in the yield `Y`). **This is the one closure in the package I attempted to break and could not.** Reported as such, not as agreement I did not test.

Two boundary remarks, both narrow: (i) §6.2's witness has `L + Y = 31 > 24`, so it is simultaneously a witness that **Corollary 806-2 does not extend past the `F`-linear class** — the producer says this in §5.5(ii), and the two statements should be read together; (ii) the closure rules out `f` increasing in `L` **globally**; it does not rule out a bound increasing in `L` on a restricted range, nor any bound in `Y`, and 806 does not claim otherwise.

## 6. Honest-accounting fields

* **`dominated_by` / `sota_delta`:** neither field is filled anywhere in the package, and the producer states why: no literature is reachable, DEC-20260731-011's strikes stand, "no literature comparison, `sota_delta` or bit-margin is offered". Under AGENTS rule 5 an unchecked `null` in `dominated_by` is a fabrication — **here it is not `null`, it is declared unavailable with a reason, which is the correct handling.** I find no smuggled comparison. **One exposure remains:** the `2^128` baseline (HEUR-806-3) *functions* as a Pareto comparator while being explicitly a modelling choice known to be generous. It is not a recalled literature number, so it is not the fabrication error — it is the weaker error of comparing against a self-chosen baseline. Correctly numbered by the producer.
* **Recalled numbers used as read:** I found exactly one recollection (R806-7, "MDS matrices are standard in wide-trail designs"), marked `unverified-from-memory`, recall confidence LOW, explicitly non-load-bearing, with `M`'s MDS property **recomputed rather than recalled**. Correct handling. **I make no literature comparison of my own and offer no counter-recollection.**
* **Charged-cost check on the eliminated dimension (KN-LIT-7593 pattern):** §4's `B = q^{s − dim(W_S∩K)}` closed form eliminates a search dimension via the measured `max(0, 2s−4)` table. **The cost of computing that invariant is charged** — the table is computed exhaustively over all 16 subsets, the minors are recomputed, and the runtime (67 s total) is reported. No uncharged elimination found.

## 7. R-3 VERDICT — is gate (4) satisfiable at all under this harness?

**Verdict: gate (4) is SATISFIABLE ONLY IN ITS MECHANICAL AND SESSION HALVES. Its independent-confirmation half is UNSATISFIABLE under this harness as currently configured, and no combination of validator and red-team CONCUR can repair that.**

Under standing basis `0137a051`, the producers, the validator (TASK-20260801-809), this red team, and the Coordinator all resolve to `claude-opus-5`. Stated plainly:

**What gate (4) CAN certify here.**
1. **Evidence integrity** — that the reviewed bytes are the committed bytes. I verified eight digests; that check is model-free.
2. **Mechanical reproducibility** — that the numbers recompute. This is the strongest thing available, and it is not vacuous: RT-1 was obtained by re-executing the producer's own code on an input the producer did not try, and it returned a number that contradicts the producer's table. A re-execution that *changes a headline number* is real evidence regardless of who ran it.
3. **Session independence** — that a reviewer without the producer's reasoning trace still reaches the artifacts' defects. Weaker than model independence but not nothing: it excludes carry-over of a specific chain of thought.
4. **Adversarial coverage** — that a named list of attacks was actually attempted, with outcomes recorded for the ones that found nothing (§2.6, §5.7).

**What gate (4) CANNOT certify here.**
5. **Absence of correlated blind spots.** This is the decisive one. Producer, validator and red team share a model prior. A defect all three miss because of that shared prior is invisible to the gate *by construction*. RT-3 (SubBytes never mentioned in a report about `n` chained AES super-box interfaces) is exactly the shape of defect a shared prior produces. That I caught it is weak counter-evidence at best — a single instance does not measure the correlation, and I cannot rule out that I share other blind spots with the producer that neither of us will ever surface.
6. **Independent confirmation.** A validator CONCUR plus a red-team CONCUR is **one draw from a correlated pair, not two draws.** Any promotion argument of the form "two reviewers agreed" is invalid here.
7. **Any closure quorum.** CLAUDE.md rule 8 forbids it outright; distinctness is on the resolved model, and there is one.

**Consequence for DEC-20260731-014.** Gate (4) as written ("independent review + red team") cannot be marked satisfied by 809 + 810. The Coordinator has three honest options and I name them without choosing: **(a)** re-scope gate (4) to what is achievable — "session-independent adversarial recomputation with named attack coverage" — and record explicitly that model independence is *not* obtained, so no asymptotic promotion rests on reviewer agreement; **(b)** hold any asymptotic promotion until a genuinely different backend is routed for at least one reviewer; **(c)** leave the gate `not_addressed` and say why. What the Coordinator may **not** do is treat this report plus the validator's as two independent confirmations. **I therefore recommend AGAINST any promotion that rests on gate (4) being satisfied by this pair** — and note that on the merits (RT-1, RT-2, RT-3) there is nothing here to promote in any case.

## 8. Strongest objection and its settling control

**Strongest objection: RT-2 + RT-1 jointly** — the central column of the cost table both exceeds the frontier ceiling of its own object at `n ≥ 2` and uses a per-interface factor beaten by an exhibitable `GF(2^8)` kernel. **Severity MAJOR. DEMONSTRATED** (RT-1 by reproduction above; RT-2 by dimension count against the table's own entries). RT-3 (unnumbered nonlinear-layer dependence) is MAJOR and DEMONSTRATED-as-an-omission and is the finding the card values most; I rank RT-2+RT-1 first only because they are settled by arithmetic rather than by interpretation.

**Settling control — CTRL-810-A, "the saturating frontier census".** Bounded, schedulable in BATCH-005.

* **What to compute.** For the `GF(2^4)` analogue (exhaustive) and for a named `GF(2^8)` list (the six producer witnesses **plus `ker(M+I) = span(1,1,1,1)`** plus a seeded sample of 10^3 kernels per dimension), compute the **actual** composed relation size `|R^{(n)}(x)|` for `n = 1…5` by direct composition, under **two** explicitly separated composition models: **(M-affine)** `Φ` composed with itself, no nonlinear layer; **(M-nonlinear)** `Φ ∘ SB` composed, with the real AES S-box. Report `|R^{(n)}|` against both `J^n` and the ceiling `q^{4(4−dim K)}`.
* **Scale and cost.** `GF(2^4)` exhaustive is the same 78 901-subspace enumeration the producer already ran, times 5 values of `n`; `GF(2^8)` is a rank computation per kernel. Pure Python is adequate for `GF(2^4)`; `GF(2^8)` needs numpy or a small C program (**not installed here** — that is the binding constraint, and it is infrastructure, not mathematics). Estimated well inside one producer slot.
* **Outcome (i) — `|R^{(n)}| = min(J^n, ceiling)` in M-affine, and M-nonlinear differs.** Then RT-2 is confirmed (column 3 must be replaced by the capped column throughout) **and** RT-3 is confirmed as material (the two composition models are not interchangeable, so §5's `n`-axis needs an explicit class statement before it means anything).
* **Outcome (ii) — `|R^{(n)}|` agrees with the uncapped `J^n` anywhere with `n ≥ 2`.** Then my dimension count is wrong somewhere and **RT-2 is falsified**; I would withdraw it. That is the outcome that falsifies my own objection, and I name it deliberately.
* **Outcome (iii) — M-nonlinear tracks M-affine closely.** Then RT-3 is materially weakened (though still an unstated dependence that should be numbered), and the `n`-axis survives with a stated class caveat.
* **Secondary, near-free:** run HEUR-806-1's own already-specified `GF(2^8)` census. RT-1 predicts the minimum is `2^24`, attained exactly on `ker(M+I)` in dimension 1. If the census finds any kernel with `J < 2^24`, HEUR-806-1 is falsified and RT-1's "confirms the heuristic" framing is wrong.

## 9. Timing, and attacks I did NOT run

**Stamps (all measured `date -u`).** Start `16:04:49Z`. Post-verification / branch determination `~16:05:16Z`. Post-computation (RT-1 confirmed) `~16:07:41Z`, elapsed 172 s. Section boundary before writing `16:09:20Z`, elapsed 271 s. Final stamp recorded in `redteam_findings.yaml`. **Budget 1000 s; the task halted on completion, not on the budget.** As the campaign's first red-team datum: the measured cost was **well under** the declared allowance and under the measured validator range (1071/1375/1046 s). One task is not a distribution and this figure should be treated as a single observation, not a norm — a run that found a live counter-witness early is not evidence that the next red-team pass will be cheap.

**Attacks NOT run — each named, so that an unrun attack is never mistaken for an attack that found nothing.**

1. **Exhaustive `GF(2^8)` `J`-census.** Not run — 16 843 009 dim-1 kernels in pure Python (no numpy) exceeds budget. I ran a **criterion-based** dim-1 argument plus 4 534 explicit kernels. **A kernel with `J < 2^24` is UNRESOLVED.**
2. **`dim K = 2` and `3` `J`-minimisation over `GF(2^8)`.** Only the 1 020 dim-2 kernels containing `(1,1,1,1)` were run (all read `2^56`). The rest is unexamined.
3. **Direct composition of `R^{(n)}` for `n ≥ 2` at any scale.** Not run. RT-2 is a dimension count, not a measurement; it is DEMONSTRATED as arithmetic against the table's own entries, not as an experiment. CTRL-810-A is exactly this gap.
4. **Re-execution of `od3_quantifier.py`.** Not run at all. **Every group-(b) and group-(a) measurement of TASK-20260801-807 in §2.2–§2.5 of its report is UNCHECKED BY ME**, including the `{1,16}` dichotomy, the count 57, the `P_b7` double disagreement, and the null_1/2/3 isolation claim. My 807 findings are confined to its pre-screen.
5. **Re-execution of the `GF(2^4)`/`GF(2^2)` exhaustive minimisations and the four controls (CTRL-NULL-1/2/3, CTRL-POS).** Not run. `PRED-1…PRED-10` are unverified by me.
6. **Attack on Proposition 806-1's proof itself** (LEM-806-1…4 and the Assembly). Not attempted beyond reading. I re-derived and re-ran only the *joint* branching. **The per-word bound `B ≥ q` is UNCHALLENGED BY ME** — that is an absence of attack, not a clearance.
7. **The `branching_from_definition` cross-check and the `min_over_all_S = 1` caveat in P3.** Not independently re-run.
8. **Any attack on `prescreen_od3.json`'s group-(a) candidates (CAND-A1, A2, A3) on their merits.** Only their interface constants were examined.
9. **DEC-20260731-016, KN-FIND-018 and EV-AES-003** were not read in full within budget; my ruling on the pre-screen rests on `prescreen_od4.json`, `prescreen_od3.json`, DEC-20260731-014's basis as quoted inside them, and `docs/inventor-protocol.md` §4. **If those records contain a basis for the `n = 30` reading of a round-independent traversal that the screens do not quote, RT-8 would need revisiting**, and I flag that dependency rather than conceal it.
