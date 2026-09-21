# RED TEAM REPORT — TASK-20260806-7e7ce3

**Report id:** `RT-20260806-7e7ce3` (derived from the task id; this mints no ledger
identifier — `tools/allocate_id.py` has no `red_team` type).
**Role:** red-team, independent session. I produced none of these artifacts and I
repair none of them. **I change no status, edit no raw artifact, and commit nothing.**
**Snapshot under review:** commit `f3d3b7e6`, receipt
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-9c41dd/archives/TASK-20260806-fb85f5/snapshot-receipt.json`.

## 0. Snapshot integrity — verified independently

I recomputed **all ten** declared `source_path_sha256` values rather than one, both
against the working tree and against `git show f3d3b7e6:<path>`. **All ten match on
both.** The receipt's `commit_sha` and `parent_sha` are `null` and
`verification.status` is `pending_post_commit`; content binding is therefore the
operative binding, and it holds (CLAUDE.md, "Archive receipts bind to CONTENT first").

`tools/allocate_id.py --check` on all seven record ids now returns `REFUSE: taken`,
which is the expected post-commit answer and is **not** an independent collision
check — the check was owed *before* the snapshot and the audit says so. I verified
by grep that each token occurs only in its own record; no cross-record collision.

## 1. Verdict summary by severity

| # | Severity | Finding |
|---|---|---|
| **F-1** | **CRITICAL — blocks execution** | GATE-A arm **A3 is false as written** at four of the five ω values on its own declared grid. `T*/(c_LA·B*²)` must be `T*/(c_LA·B*^ω)`. At m=5, ω=1.90 the arm computes **0.2050** against a target of **1.4750**; at m=8, ω=2.40, **247.38** against **1.3429**. A conforming Executor fires `INV-GATE`, the entire run set is `completed_invalid`, and **no window, no memory table, no multi-target crossover and no satellite table is emitted**. ST-2 forbids repairing it in flight. |
| **F-2** | **CRITICAL — the headline is wrong** | The trial-count admissibility clause `d ≤ ω/(m−1)` is derived at the **harvest-all** optimum `B*_HA` and then applied to the **one-relation-per-target** branch, whose operating point is the kink `B_k=(m!N)^{1/m}` where `μ=1` and the trial count is `B_k ≫ 1`, so the clause is inactive there. Applying it correctly changes `sup W(m,2)` at every `m ≥ 7` from `1/3, 2/7, 1/4, 2/9, 1/5, 2/11` to `5/14, 3/8, 7/18, 2/5, 9/22, 5/12` — **monotonically increasing**. The hypothesis title ("bounded and NOT monotone in m"), the "peak at m∈{6,7}", the "decays like 2/(m−1)" clause and the stated contrast with `IDEA-20260803-fa9839`'s monotone reading **all collapse**. |
| **F-3** | **CRITICAL — false novelty claim** | `IDEA-20260806-3b91c7`'s central framing — "the corpus holds the preprocessing **lower** bound and no **achievability** row" — is refuted by a committed corpus record the proposal names and declares unopened. **`knowledge/literature/KN-LIT-013.md`** (the source_ref of `KN-TECH-005`) states verbatim: *"shows the bound is essentially tight via a matching generic algorithm"* and *"tight (a construction achieves S\*T^2 ~ N), so with advice the online cost can beat the classic sqrt(N) generic bound."* I found it by re-running the producer's capped E10 uncapped (109 files, not 40). |
| **F-4** | **CRITICAL — self-refuting headline** | `IDEA-20260806-7ea402`'s headline jump factor is wrong and **its own `sota_delta` table proves it wrong**. Claim (A) defines cost via cumulative `ncols(D)=Σ_{i≤D}C(n,i)` but then computes the jump as `C(n,D+1)/C(n,D)=(n−D)/(D+1)`, concluding `(6/7)^ω < 1` at n=12,D=6 ("THE JUMP FACTOR ... IS BELOW 1"). The cumulative ratio is `3302/2510 = 1.3155`, so the jump is **1.731 at ω=2 — cost RISES**. The record's own `sota_delta` states `J(12,6)=1.731`. `ncols` is a cumulative sum, so the jump is `>1` at **every** D and the "not monotone / below 1" claim is void. |
| **F-5** | **MAJOR** | `IDEA-20260806-20f6ab` books its `C(m,m/2)` gain **on the wrong axis**. It concedes the half-lists "are still BUILT before filtering", then claims the gain is on time and not memory. Building is the time cost of MITM; filtering after building reduces *stored* size, not *generated* size. And at the record's own operating point (`B^m ≈ m!N`) the join output is `Θ(m!)`, already far below the build cost `B^{⌈m/2⌉}` — so reducing the join by `R_w` buys nothing. Without a-priori restriction (which the record correctly flags as `KN-OPEN-001` recursively) the time gain is **zero**, not `2^{Θ(m)}`. |
| **F-6** | **MAJOR** | `IDEA-20260806-c5d183`'s exhaustiveness claim ("A FOURTH CLASS CANNOT EXIST") enumerates violations of the three **named** hypotheses and silently treats the universally quantified `g` inside hypothesis (iii) as unrelaxable. **Approximate equivariance** — `π(g+h)=T_h(π(g))` for all `h` but only for most `g` — violates none of Classes I–III and breaks the transitivity argument. The theorem itself (§2 below) is correct; the *index set* claim is not. |
| **F-7** | **MAJOR** | `IDEA-20260806-7ea402`'s load-bearing percentage is wrong by a factor of 6.4 and in the self-serving direction. It says the 7,110 deficit is "4.5 per cent of a gap of 24,621". `7110/24621 = 28.9%`; 4.5% is `7110/156520`. Two denominators conflated in the one sentence that decides the lane. |
| **F-8** | **MAJOR** | **Omitted cost term with exponent consequences:** `D_trial` is treated as free and **independent of `B` and `m`**, while the optimizer is free to push `B` upward. Any coupling `D=N^d·B^e` moves the balance threshold to `(m−ω−1−e)/(2ω)`; even `e=1` (one charged operation per base element) moves the emptiness boundary from `m≤3` to `m≤4`. `CTRL-DEGENERATE` D2 names this defect and then repairs it with the trial-count bound instead of a coupling. |
| **F-9** | **MAJOR** | **Omitted baseline:** for the multi-target row `PM-5`, index calculus **is** a preprocessing algorithm (`C_pre+C_rel+C_LA` are target-independent), so the correct comparator is the preprocessing frontier `S·T²≈N` (`KN-LIT-013`, committed), not `√(kN)` or `k·√N`. The `dominated_by: NOT APPLICABLE` on `H-ICEX-9e54c2` is therefore **unchecked for PM-5**, which *is* a Pareto claim. This is `3b91c7`'s substantive point and it survives F-3. |
| **F-10** | **MODERATE** | **`CTRL-NULL` and `CTRL-DEGENERATE` D1 are identities, not controls.** `KN-FIND-007` is a one-line double count; enumerating it can catch a coding bug and can never return a mathematical negative. D1 reduces to `T_r·D = (B/μ)·(μN) = N·B` exactly. `F2`'s "Either `KN-FIND-007` or this instantiation is wrong" is not a live disjunction. |
| **F-11** | **MODERATE** | **`CTRL-CONVENTION` cannot fail under one of its two readings.** Its description says "the exact set of (m,d) at which the EXPONENTS differ" — globally that set is `{d>(ω−1)/m}`, non-empty by trivial algebra for **every** m≥2, so `INV-PREREG`'s "divergence set is empty" branch is unreachable. Only the *within-window* reading (which yields the pre-registered "non-empty for every m≥5") can fail. The two readings are not disambiguated. |
| **F-12** | **MODERATE** | **GATE-A performs no external calibration.** A1 and A2 are algebraic consequences of the model's own two formulas; A3/A4/A5 are internal identities. The only externally anchored quantity is GATE-B's `2−2/n`, pre-registered **UNRUN**. "Reproduce known extension-field index-calculus quantities" oversells what is an internal-consistency gate. This is the load-bearing premise of the 5.4 re-partition. |
| **F-13** | **MODERATE** | **The design-time dependency verification is factually wrong for this worktree.** numpy is **not installed** here; sympy is **not installed** here; `harness/runner.py` imports `sympy` at module scope (line 28) and cannot import. The spec inferred present-tense environment state from historical committed manifests produced on other machines. The *conclusion* (stdlib-only) is right and the contract **is** runnable (Python 3.11.15, `fractions`/`decimal`/`math`/`itertools`/`json`/`hashlib`/`argparse`/`platform` all present, `Decimal` at prec 50 verified). |
| **F-14** | **MODERATE** | **R-D is not satisfied.** R-D names five items; the contract charges four and declares the fifth (relation rank) omitted, and R-D's own second clause — "needs its own IDEA-\* record" — is unmet (`source_proposal_id` is still `IDEA-20260803-fa9839`). |
| **F-15** | **MODERATE** | **Circular intra-batch Pareto citation.** Four proposals (`9d47e2`, `7ea402`, `c5d183`, `20f6ab`) list "the memory-matched generic baseline `√(N/S)` derived in `IDEA-20260806-3b91c7`" as a frontier row in `dominated_by`. An unreviewed, `novelty_status: unverified` sibling in the same batch is load-bearing for four records' Pareto honesty. Two of them (`9d47e2`, `20f6ab`) evaluate it at `σ=1/2`, **outside `3b91c7`'s own declared cap `σ∈[0,1/3]`**. |
| **F-16** | **MINOR** | `IDEA-20260806-3b91c7` quotes `B* = N^{1/(m+1)}` as "the corpus's recorded two-term optimum" — the exact form `DEC-20260805-bb162b` §5.2 ruled false wherever `d>0`, and which this batch's own GATE-A arm A4 exists to fail. Its point prediction "the two columns must differ by **exactly** `1/(2(m+1))`" holds only on the `d=0` row; off it the difference is `(1+d)/(2(m+1))`. |
| **F-17** | **MINOR** | **Two committed records disagree by 3 on the same quantity.** `EV-SIG-008` GATE 2 FINAL: sem D6 rank `138,570`, deficit `17,950`. `EV-DREG-008`: `deficit_genuine=17947 (=156520−138573)`, i.e. rank `138,573`. Observed at source and recorded per AGENTS rule 8; I adjudicate neither. |
| **F-18** | **MINOR** | The contract's `objective` says "with exact arithmetic and **no measurement**", but `CTRL-NULL` enumerates up to 11.4M multisets over four `Z/N` families and emits `SM-1` measured means, across a five-run, 0.25-CPU-hour plan. It is not a zero-compute derivation. This matters because the P2 routing argument leans on that word. |

Nothing above is an impossibility claim, and nothing above rejects a conditional
theorem for being conditional. Where a candidate fails I state the narrowest
surviving statement in §7.

---

## 2. Item 1 — ROUTING (P2/P3): is this contract in the right home?

**Homing: unresolved, and it should not have been dispatched before it was resolved.**
`EXP-ICEX-146ff5` binds `question_id: RQ-ICEX-001` and `H-ICEX-9e54c2` (also
`RQ-ICEX-001`) but sits inside a `GOAL-ECDLP-001` batch. `DEC-20260805-bb162b`
(`BATCH-156658/SCOPE-DECISION.md`) *declined* the `GOAL-ECDLP-001` binding for
`IDEA-20260803-fa9839` and routed it to `GOAL-ICEX-001`. Nothing in this batch
supersedes that decision. The contract is **correct not to pre-empt it** (P2 is well
drafted), but a `GOAL-ECDLP-001` batch approving an `RQ-ICEX-001` contract over a
standing decline is a routing defect that must be closed by a Coordinator decision
**before** any ledger commit, not after.

**R-D: NOT satisfied (F-14).** R-D reads: *"charged descent, relation rank,
verification, multi-target accounting, and a BSGS row beside the rho row — at which
point it is a different and much larger proposal and needs its own IDEA-\* record."*
Score: descent ✔, verification ✔, multi-target ✔, BSGS row ✔, **relation rank ✘**
(declared omitted, direction stated), **own IDEA record ✘**. Two of R-D's clauses are
unmet and one of them is named explicitly in R-D's list. A declared omission with a
stated direction is good practice; it is not a charge.

**Cheap discharge, so this does not become a deadlock.** `IDEA-20260805-061f97`
(committed) gives the left-kernel threshold as the fixed point of `x = 1−e^{−mx}`.
Relations needed becomes `B/x*` rather than `B` (`x*≈0.797` at m=2), a **constant**
factor that moves **no exponent**. Charging rank that way is two lines, converts a
declared omission into a charged term, and makes the omission provably
exponent-neutral within the model. That is the repair I recommend over either
waiving R-D or blocking on it.

**Does the ICEX deferral bar this?** `GOAL-ICEX-001.next_action` bars *measurement*
("NO ICEX MEASUREMENT AUTHORIZED ... until charged SDEG/MONO/RELN measurement
packages exist"). A genuinely zero-compute derivation is **not** barred by that text.
**But this contract is not one (F-18)**: five runs, 0.25 CPU-hours, and `CTRL-NULL`
emits measured means. The honest framing to put to `GOAL-ICEX-001`'s Coordinator is
"no ICEX or ECDLP measurement is performed; `CTRL-NULL` is an internal arithmetic
self-test in `Z/N`" — **not** "zero compute". The contract's own `objective` line
should be corrected to say so.

**Adjudication of the 5.4 re-partition (the contract asks for this explicitly).**
**ACCEPT, with two mandatory amendments.** It is not a relaxation of the four
readings 5.4 protects — tightness, no-go phrasing, literature comparison and any
prime-field positive reading all remain structurally blocked, and I checked the text
for a back door and did not find one. Restoring 5.4's blanket block would reproduce
the indefinite cap the decision itself flagged, and premature closure is a failure
mode symmetric with overclaiming (`docs/inventor-protocol.md`). **However** the
re-partition's load-bearing premise is "GATE-A ... IS executable here and IS capable
of failing", and that premise is weaker than stated: A3 is broken (F-1), `CTRL-NULL`
and D1 are identities (F-10), `CTRL-CONVENTION` is ambiguous (F-11), and GATE-A
contains **zero external calibration** (F-12). Amendments required:
1. Repair A3 (see F-1) — otherwise the re-partition is moot because nothing is emitted.
2. Relabel GATE-A as an **internal-consistency gate** and carry "no external
   calibration was performed; the only externally anchored quantity is GATE-B, which
   is UNRUN" verbatim onto every emitted table, beside `calibration_state`.

---

## 3. Item 2 — THE CALIBRATION GATE: I re-derived all three counting-convention
## discriminations, and found a fourth arm that fails

### A1 — the three claimed failure modes are all correct

`C(q+n−1,n) = ∏_{j=0}^{n−1}(q+j)/n!`, so
`n!·C(q+n−1,n)/q^n = ∏_{j=0}^{n−1}(1+j/q)` **identically**. First-order correction
`+n(n−1)/(2q)`. Then:

| convention | value of `n!·(count)/q^n` | first-order | fails at tolerance zero for n≥2? |
|---|---|---|---|
| `C(B+m−1,m)` (multisets, the model) | `∏(1+j/q)` | `+n(n−1)/2q` | — (this is the target) |
| `C(B,m)` (distinct subsets) | `∏(1−j/q)` | `−n(n−1)/2q` | **YES**, wrong sign |
| `B^m/m!` | `1` | `0` | **YES** |
| `B^m` (ordered tuples) | `n!` | — | **YES**, constant `n!` too large |

**All three derivations in the specification are correct.** A1 is a real
discrimination among the three realistic implementation choices, and its tolerance
(exact `Fraction` equality) is genuinely zero. This is materially better than the
`KN-TECH-1a5b7e` failure mode.

### A2 — correct, and hand-recoverable

At `B=q, D=q^0, N=q^n, m=n`: `C_rel = m!ND/B^{m−1} = n!·q`, `C_LA = q^ω = q²`, total
`~q²`, exponent exactly **2** in `q`, `2/n` in `N`. Correct. A mis-powered `B`, `N` or
`m!` misses it.

### A3 — **FALSE AS WRITTEN. This is the finding that blocks the contract.**

From `B*^{m+ω−1} = (m−1)m!ND/(ω c_LA)`, the total at the optimum is
`T* = c_LA·B*^ω·(m+ω−1)/(m−1)`. So the correct identity is
**`T*/(c_LA·B*^ω) = (m+ω−1)/(m−1)`**. The specification writes `T*/(c_LA·B*²)`, which
coincides only at `ω=2`. Its own declared grid is `ω ∈ {1.90, 2.00, 2.10, 2.20, 2.40}`.
Computed here at 50-digit `Decimal`, `N=2^160`, `D=1`, `c_LA=1`:

| m | ω | `T*/(c_LA B*²)` (arm as written) | `T*/(c_LA B*^ω)` (correct) | target `(m+ω−1)/(m−1)` |
|---|---|---|---|---|
| 5 | 2.00 | 1.500000 | 1.500000 | 1.5 |
| 5 | 1.90 | **0.2049837** | 1.475000 | 1.475 |
| 8 | 2.40 | **247.3761** | 1.342857 | 1.342857… |
| 12 | 2.10 | **3.275675** | 1.190909 | 1.190909… |

`INV-GATE` fires at four of five ω values, the run set is `completed_invalid`, and
**nothing is emitted**. ST-2 forbids the Executor from repairing it in flight, and a
`completed` review carrying REVISE would unblock an Executor mechanically — which is
exactly the risk P1 anticipates.

**Second defect in A3, independent of the first.** Even repaired, the stated tolerance
("exact rational equality for the ratio") is unattainable at non-integer ω through
`decimal.Decimal`: my 50-digit evaluation returns `1.4749999…9989`, not `1.475`. The
identity must either be verified **symbolically** (never materializing `B*`) or the
tolerance restated as a relative bound below `1e-25`, consistent with the arm's own
first clause. As written the arm fails on tolerance as well as on algebra.

### A4, A5 — both correct and both capable of convicting their author

A4's `(1+d)/(m+ω−1)` is right (I re-derived it; see §4). A5 is the strongest arm in
the contract: it pre-registers point rationals derived without an interpreter and
declares the run invalid either way on mismatch. **I predict A5 will fire**, for the
reason in §4 — and that is the gate working, not failing.

### Capable-of-failing verdict, control by control

| control / arm | can it return a mathematical negative? |
|---|---|
| GATE-A A1 | **YES** — discriminates three real modelling choices |
| GATE-A A2 | **YES** (internal, but hand-recoverable and mis-powerable) |
| GATE-A A3 | **BROKEN** — fails for the wrong reason at 4/5 ω values (F-1) |
| GATE-A A4 | **YES** — catches the one error already on record (defect 5.2) |
| GATE-A A5 | **YES** — the only arm that can convict the design-time algebra |
| GATE-B | **UNRUN by pre-registration** — honest, and the only external anchor |
| CTRL-NULL | **NO** — `KN-FIND-007` is a proved double count; catches coding bugs only |
| CTRL-DEGENERATE D1 | **NO** — exact identity `T_r·D = N·B` by substitution |
| CTRL-DEGENERATE D2 | **YES** — pre-registered flip at `m=8`; I verified `4/(m+1)<1/2 ⟺ m>7` |
| CTRL-PARAM | **YES** — `B` vs `B_x` exponent invariance is a real claim |
| CTRL-SIGN | **YES** — an exponent boundary must be constant-free |
| CTRL-CONVENTION | **AMBIGUOUS** — cannot fail under the global reading (F-11) |
| CTRL-RANK-DIRECTION | **NO** — a stamp check; the spec says so ("Mechanically") |

So six of thirteen can return a mathematical negative, two are identities dressed as
controls, one is broken and one is ambiguous. That is a genuine gate — not 33/33 — but
it is weaker than advertised, and **none of it is external** (F-12).

### The null-object control the contract is missing, and what the quantity should have done

Ask what should destroy the signal. The `CTRL-NULL` mean is **theorem-fixed**: it
*cannot* vary across base families, so its constancy is not evidence of anything.
The quantities the cost model actually depends on and that **should** vary with base
geometry are:

- **coverage fraction** — the share of the `N` targets with ≥1 decomposition; and
- **rank of the first `B` successful relations.**

For family (iv) — small multiples of a single element — the mean is unchanged while
coverage collapses onto a subgroup and the relation matrix has rank ≈ 1. **Two extra
columns on an enumeration the contract already performs** convert `CTRL-NULL` from a
tautology into a control that can fail, and they measure the exact term
(`relation_rank`) that R-D names and the contract omits. This is the cheapest
discriminating control in the whole package.

---

## 4. Item 3 — DEFECT 5.2 AND THE WINDOW: I re-derived the table; it is
## internally consistent and externally wrong

**Optimizer (A4 / defect 5.2): CONFIRMED CORRECT.** Minimizing
`f(B)=m!ND·B^{−(m−1)} + c_LA·B^ω` gives `B*^{m+ω−1}=(m−1)m!ND/(ω c_LA)`, hence
`B* ~ N^{(1+d)/(m+ω−1)}` and total `~ N^{ω(1+d)/(m+ω−1)}`. Beating `√N` requires
`d < (m−ω−1)/(2ω)`, which at ω=2 is `(m−3)/4` — the proposal's own threshold. The
`N^{1/(m+ω−1)}` form is the `d=0` row only. **Defect 5.2 is correctly repaired and A4
correctly fails a run reporting otherwise.**

**Trial-count bound: correct at the branch it was derived on.** `T_r ≥ 1` at `B*_HA`
gives `(m−1)(1+d) ≤ m+ω−1`, i.e. `d ≤ ω/(m−1)`. Correct.

**Kink branch: correct.** `μ≥1 ⟺ B ≥ B_k=(m!N)^{1/m}`; above `B_k` the ORPT cost
`B·D + c_LA B^ω` is strictly increasing, so the ORPT optimum is `min(B*_HA, B_k)`, and
`B*_HA > B_k ⟺ d > (ω−1)/m`. At the kink the total is `max(N^{1/m+d}, c_LA N^{ω/m})`,
which beats rho iff `m > 2ω` and `d < (m−2)/(2m)`. **All correct.**

**Composite table: reproduces exactly.** Evaluating the stated `W(m,ω)` at ω=2 I get
EMPTY, EMPTY, 1/4, 3/10, 1/3, 1/3, 2/7, 1/4, 2/9, 1/5, 2/11 at m=2…12 — **identical**
to the pre-registration, with `sup = 2/(m−1)` exactly for `m ≥ 8`. The design-time
algebra reproduces its own formula.

**But the formula imports a constraint from the wrong operating point (F-2).**
`d ≤ ω/(m−1)` was derived at `B*_HA`. Branch 2 does not operate there: it operates at
`B_k`, where `μ = 1` **by construction** and `T_r = B_k ~ N^{1/m} ≫ 1`. The trial-count
constraint is **satisfied automatically and vacuously** on branch 2. Yet the composite
ANDs it globally, and from `m ≥ 7` onward it is **the binding constraint** — i.e. the
entire "peak then decay" structure:

| m | contract `sup W(m,2)` | admissibility applied only where derived |
|---|---|---|
| 2–6 | EMPTY, EMPTY, 1/4, 3/10, 1/3 | EMPTY, EMPTY, 1/4, 3/10, 1/3 |
| 7 | **1/3** | **5/14** |
| 8 | **2/7** | **3/8** |
| 9 | **1/4** | **7/18** |
| 10 | **2/9** | **2/5** |
| 11 | **1/5** | **9/22** |
| 12 | **2/11** | **5/12** |

Corrected, the window is **monotonically increasing** toward `1/2`, there is no peak at
`m∈{6,7}`, there is no `2/(m−1)` decay, and the stated contrast with
`IDEA-20260803-fa9839`'s "monotonically loosening" reading **disappears**. The
hypothesis title, the `winning_window_shape` prediction, `A5`, and the "materially
different instruction to the deferred measurement goals" in `constructive_transforms`
all rest on this.

Note further that where the contract's clause *is* binding (`m ≥ 7`) the supremum is
the point at which the continuous relaxation wants **fewer than one trial** — a
degeneracy of the model, not an algorithmic threshold. A headline number set by a
degeneracy should be labelled as such even if the clause is retained.

**HEUR-AT-1's "exponent identical under both conventions": the contract's
pre-registration that it is FALSE is CORRECT.** For `d > (ω−1)/m`, ORPT total exponent
is `1/m + d` (slope 1 in `d`) while harvest-all is `ω(1+d)/(m+ω−1)` (slope
`ω/(m+ω−1) < 1`); they agree exactly at `d=(ω−1)/m` and ORPT is strictly larger above
it. So `HEUR-AT-1`'s clause holds only for `d ≤ (ω−1)/m`. **But** the divergence set is
`{d > 1/m}` at ω=2, which is non-empty for **every** `m ≥ 2` on the declared grid
`d∈[0,2]` — so `INV-PREREG`'s empty-set branch is unreachable under the global reading
(F-11). The pre-registered "non-empty for every `m ≥ 5`" is the *within-window* count
(at m=4, `1/m = 1/4 = sup W`, so the within-window divergence set is empty). The two
readings must be disambiguated or the control cannot fail.

---

## 5. Item 4 — OMITTED COST TERMS, itemized

Charged: `C_pre`, `C_rel`, `C_LA`, `C_desc`, `C_ver`, `M_total`, `C_multi`. Omitted or
charged at zero:

1. **`D_trial`–`B` coupling — the one that moves an exponent (F-8).** `D_trial=N^d` is
   held fixed while the optimizer raises `B`. With `D=N^d·B^e` the threshold becomes
   `d < (m−ω−1−e)/(2ω)`; each unit of `e` costs `1/(2ω)` of window. `SM-3` even emits
   the Bezout-implied predicate degree `d_p ≥ B*/3` — evidence that the oracle's cost
   scales with `B` — and does not feed it back into the charge. Under `KN-LIT-7593`,
   an eliminated dimension is not a speedup until its own cost is in the total.
2. **Relation rank (F-14).** Declared, direction stated, not charged. Cheap discharge
   via `IDEA-20260805-061f97` above.
3. **Preprocessing-frontier baseline for `PM-5` (F-9).** `C_pre+C_rel+C_LA` are
   target-independent, so the amortized comparison must be against `S·T²≈N`
   (`KN-LIT-013`), not `√(kN)`/`k√N`. At m=6, ω=2, d=1/3 the contract's own row has
   `S=N^{4/21}`, `T=N^{1/3}`, hence `S·T² = N^{0.857} ≪ N` — the row asserts something
   strictly stronger than "beats rho" and does not say so.
4. **Memory of the multi-target rho bracket.** Batch rho with distinguished points is
   charged `c_rho√(kN)` **time** with no memory column, while index calculus is charged
   its memory. Not a matched frontier.
5. **No BSGS multi-target row at all**, though `BASE-BSGS` exists single-target.
6. **Descent recursion.** `C_desc` assumes one-level decomposition of a rerandomized
   target over the same base, with `κ_desc ∈ {1,m,m²}` as a stand-in for depth. A
   recursive/large-prime descent is not charged; the interpretation limit correctly
   flags large primes as outside the charge but the *descent* stage inherits a
   one-level assumption rather than a charge.
7. **Factor-base membership test during collection** (hash/sort lookup) charged at
   zero. Polylog, but nowhere is "all polylog factors dropped" declared.
8. **Bit-cost of arithmetic mod `N` in `C_LA`.** `c_field_to_group = 1` pins one field
   op = one group op; the true ratio is ≈1/10. Constant, swept, exponent-neutral — but
   `log N` per modular multiply is polylog, not constant, and is undeclared.
9. **`O(m)` nonzeros per row** in the sparse solve: `B^ω` drops the `m` factor.
   Constant at fixed `m`; at the coverage-optimal arity `m ~ log N/log log N` it is not.
10. **Second moment / tail of the yield.** `HEUR-AT-1` supplies the exact **mean** and
    explicitly does not prove independence or concentration. Branch 2 operates at
    `μ = 1` — precisely where the mean-vs-success-probability gap is widest and where
    the `1.582 = 1/(1−e^{−1})` bound is itself a Poisson **heuristic**, not a bound on
    the object. The cost bookkeeping (per-attempt × inverse success probability) is
    structurally correct; the probability it uses is heuristic at the operating point.

Items 1, 3 and 4 can change a reported verdict. Items 2 and 6 are declared. Items
5, 7–10 are disclosure gaps.

---

## 6. Item 5 — THE THREE STANDING SCREENS, my verdicts vs the producer's,
## plus duplication

I re-ran all three screens myself on all five proposals. **I agree with the producer's
screen verdict in 15/15 cells.** Disagreement is confined to the *reasoning* behind two
of them, and to matters outside the screens.

| proposal | Screen 1 (`KN-FIND-007`) | Screen 2 (`KN-FIND-c41ea9`) | Screen 3 (`KN-FIND-002`/`KN-TECH-005`) |
|---|---|---|---|
| `3b91c7` | producer PASS / **mine PASS** | PASS / **PASS** | PASS ("uses it") / **PASS — the use is legitimate, the calibration is not discriminating** |
| `9d47e2` | PASS / **PASS** | PASS "by using the theorem as a premise" / **PASS — but the theorem is not load-bearing for the headline** |PASS / **PASS** |
| `7ea402` | n/a PASS / **PASS** | n/a PASS / **PASS** | n/a PASS / **PASS** |
| `c5d183` | PASS / **PASS** | n/a PASS / **PASS** | PASS ("places the closed families") / **PASS** |
| `20f6ab` | PASS / **PASS** | n/a PASS / **PASS** | PASS ("the argument binds") / **PASS** |

**Screen 2 and `9d47e2` — the handoff's specific question.** Using a committed theorem
as a *premise* is legitimate; the screen forbids proposing a *measurement* of a
statistic that is constant on the factor-base sublocus, and `9d47e2`'s observable is a
charged operation count. **PASS is correct.** But the theorem does no work for the
headline: in formulation E as `9d47e2` itself defines it (*loop over tuples, compute
`Q = R − Σ`, test membership*) **no root-find was ever present**, so complete splitting
rules out an algorithm nobody proposed. `D_trial(E) = m−1` additions is the definition
of enumerate-and-test and needs no theorem. `KN-FIND-c41ea9` is load-bearing only for
the *weaker* alternative (full signed root set, `2^{m−2}−1` additions vs a degree-`2^{m−2}`
factorisation). The record's title — "a COST identity that nobody has cashed" — attributes
its number to a citation that does not carry it.

**Screen 3 and `3b91c7`/`20f6ab` — the handoff's specific question.** Both claim to
**use** the GGM argument rather than defeat it. I checked both and **both claims are
sound**: `3b91c7`'s chain construction is a plain generic algorithm (additions +
equality) sitting at `S·T² = Θ(N)`, exactly on the recorded bound, violating nothing;
`20f6ab` is a constant-factor claim on a generic search and says so in its title.
Neither reopens a simulable oracle family.

**But `3b91c7`'s σ=0 calibration is NOT a discriminating control (handoff item 6).**
It is a real known-answer edge — `T=N^{(1−0)/2}=√N` reproduces rho for free, and the
record is right that a sign error or off-by-one shows up there. It is **not**
two-sided against the rival hypothesis, because the competing law "generic time is
`√N` at *every* memory" (Shoup, no preprocessing) passes σ=0 identically. **Every
candidate law that reduces to rho at zero memory passes it.** The discriminating point
is **σ=1/3**, where the two laws read `N^{1/3}` vs `N^{1/2}` and where a committed
corpus record already supplies the answer (`KN-LIT-013`: `S=T=N^{1/3}`). Ranking the
proposal first *because of* the σ=0 edge is ranking it on a control that cannot fail
against its main rival.

### Duplication verdicts (per-proposal, each naming what I opened myself)

- **`3b91c7` — DUPLICATIVE OF A COMMITTED KNOWLEDGE RECORD ON ITS ACHIEVABILITY HALF.**
  Nearest-neighbour claim (`IDEA-20260805-c06631`) checked: I confirm c06631's rho rows
  give group-operation exponent 1/2 at every storage parameter with no offline/online
  split, so the discrimination against c06631 **holds**. I additionally opened
  `knowledge/techniques/KN-TECH-005.md` and `knowledge/literature/KN-LIT-013.md` (my
  choice, not the record's). **KN-LIT-013 states the achievability explicitly** (F-3).
  The record itself pre-declared this outcome and its consequence — *"this record's
  honest status becomes `known` and its VALUE IS UNCHANGED"* — and that is correct: what
  survives is the **comparator-convention audit**, which is real, material, and
  independently confirmed by my own §5 item 3. Required: `novelty_status: unverified →
  known (internal, KN-LIT-013)`; delete the "no achievability row in the corpus"
  sentence; recite the frontier row to `KN-LIT-013` rather than to a derivation.
- **`9d47e2` — NOT A DUPLICATE, BUT ITS ATTRIBUTION IS.** I opened
  `IDEA-20260803-fa9839`'s role via the contract, `KN-FIND-007`, and
  `IDEA-20260805-0d2a21`'s audit line (the "prime-field vs boolean Weil-descent"
  labelling gap). `0d2a21` already holds the labelling half for SIG; `9d47e2` generalizes
  it across SDEG/DREG/SIG, which is a genuine increment. The E-vs-S dichotomy and the
  `N^{1/2+1/m}` accounting are catalogue `A1-2`'s, cited as prior art. Contribution is
  the cross-goal labelling, not the cost identity.
- **`7ea402` — NOT A DUPLICATE.** Checked against `IDEA-20260805-2dc8de` (normalisation
  of the decision variable), `IDEA-20260803-202a15` (one closed form for both n=12
  deficits) and `IDEA-20260805-61f7f4` (zero-compute discriminating-power map). The
  "cost is a step function of an integer `d_solve`" framing is not held by any of them.
  Genuinely new; see F-4 and F-7 for what is wrong inside it.
- **`c5d183` — NOT A DUPLICATE.** Checked against `IDEA-20260802-002` (the `(L,b)`
  propagation meter it makes a point prediction about) and `IDEA-20260727-005` (the
  exit-map classification barrier, which classifies *homomorphisms*, not *projections*).
  The theorem is different from both. See F-6.
- **`20f6ab` — NOT A DUPLICATE.** Checked against `IDEA-20260731-012` (large-prime
  variation) and `IDEA-20260805-1f4a11` (BKK trichotomy + Amdahl ceiling, which it
  correctly imports). Nobody holds the `C(m,m/2)` price. See F-5.

**Duplication audit quality.** 262/262 and 64/64 are real: E1 and E2 used
`head_limit: 0` and report totals, so truncation is detectable. The depth caveat
(6 of 64 read in full) is disclosed honestly. **The E10 debt was real and I discharged
it: uncapped it returns 109 files, not 40, and the answer changes (F-3).** The audit's
own instruction — *"a red team should re-run E10 uncapped"* — was the right instruction
and produced the batch's most consequential correction.

---

## 7. Baseline comparison, scope check, and narrowest supported statements

**Against rho, BSGS, and the closest specialized baseline.** Single-target: rho
`0.886√N` at `O(1)` memory is the correct comparator and the contract uses it, pinned
against a certificate-verified committed run — good practice. BSGS is present with
memory. **The closest specialized baseline is missing**: extension-field index calculus
(Gaudry–Diem) enters only through GATE-B, which is pre-registered UNRUN, so the model
is never compared against the one algorithm in its own family that demonstrably works.
The contract's `observation_collision` block records this honestly as a declared
non-tightness. **Amortized/multi-target: the wrong frontier is used (F-9).**

**Memory-matched second column — computed here, since `3b91c7` asks for it and nobody
emitted it.** With `β = τ/ω` and a memory-matched bar `1/2 − β/2`, the balance-branch
condition becomes `τ < ω/(2ω+1)`, i.e. `d < (m−ω−2)/(2ω+1)` — **`(m−4)/5` at ω=2**,
versus the contract's `(m−3)/4`; the kink branch becomes `d < (m−3)/(2m)` versus
`(m−2)/(2m)`. Consequence: **the m=4 row (`sup = 1/4`) becomes EMPTY**, and the
emptiness boundary moves from `m ≤ 3` to `m ≤ 4`. This is a decision-relevant change,
it is two lines of algebra, and it is exactly the over-reading `3b91c7` predicts.
It is conditional on the amortization policy (`3b91c7`'s H3) and must be reported as a
second column, never as a replacement.

**Scope check against AGENTS rules 6 and 7 and `docs/claims-and-verification.md`.**
I searched the contract for anything licensing a prime-field weakening claim or
presenting a threshold as though an oracle meeting it exists. **I found none.** The
`admission_and_ceiling` block, `interpretation_limits`, the `toy` tier stamp, the
`model_evaluation: true` stamp on all `N ∈ {2^160…2^384}` rows, `certificate: kind:
none` with a justification, and `CTRL-RANK-DIRECTION`'s `LOWER-BOUND-MODEL, POSITIVE
READING NOT CONSERVATIVE` stamp are collectively **the strongest scope discipline I
have seen in this corpus**, and the `quantifier_order` block correctly refuses to
invert to "there exists an oracle". **Two residual scope defects:** (i) `objective`'s
"no measurement" is contradicted by `CTRL-NULL` (F-18); (ii) the satellite table's
`HEUR-AT-3` conditional is correctly required at every citation, but `HEUR-AT-3` has
`supporting_results: []` and is "NOT VERIFIED against any measured solver in this
corpus" — so `PM-2`, the **declared deliverable and declared deadlock exit**, is
entirely conditional on the single unvalidated heuristic in the record. That is
disclosed, but a deliverable resting wholly on an unsupported heuristic should be
labelled as a *conditional instrument*, not as an *exit*.

**Runnability verdict (completion gate item 5): RUNNABLE on the declared stdlib path,
with a corrected environment statement.** Verified in this worktree: Python 3.11.15
on Linux; `fractions`, `decimal`, `math`, `itertools`, `json`, `hashlib`, `argparse`,
`platform`, `sys`, `os`, `time` all import; `Decimal` at `prec=50` verified.
**numpy is NOT installed. sympy is NOT installed.** `harness/runner.py` imports `sympy`
at module scope (line 28) and therefore **cannot be imported here** — an Executor
routing this contract through the standard wrapper will fail before the driver runs.
The spec's `verification_performed_at_design_time` inferred both packages present from
historical manifests produced on other machines; both inferences are false here (F-13).
Consequences: the design decision (stdlib only) is **vindicated**; the numpy branch
permitted in `CTRL-NULL` is dead code that can never be exercised and `INV-DEP`'s
"must run with numpy uninstalled" is the only reachable path; the environment
statement must be corrected to a present-tense check. `experiments/EXP-ICEX-146ff5/`
currently contains only `specification.yaml` — correct, since no run is authorized.

**Narrowest supported statements if the candidates fail.**

- *`EXP-ICEX-146ff5`*: even with F-1 and F-2 unrepaired, what survives is that the
  charged comparison has been **written down** for the first time, that its optimizer
  and its two branch conditions are correct (§4), and that the harvest-all/ORPT
  exponent divergence above `d=(ω−1)/m` is real. The window's **shape** does not survive.
- *`3b91c7`*: the achievability derivation is redundant with `KN-LIT-013`; the
  **comparator-convention audit survives intact** and is independently confirmed here.
- *`7ea402`*: the jump factor and the 4.5% both fail, but the **structural claim
  survives and is strengthened**: cost is `C(d_solve)` with `d_solve` an integer, so the
  derivative w.r.t. a continuous deficit is 0 almost everywhere. Moreover, at source
  `EV-SIG-008` records rank `149,410` (null) and `138,570` (sem) against
  `ncols − |V| = 174,031` — **both far below saturation, so `d_solve > 6` in both arms**
  and the 7,110 deficit provably does not move `d_solve` at D=6. That is a **cleaner and
  stronger** version of the record's own conclusion, derivable at zero compute, and it
  does not need the false percentage.
- *`9d47e2`*: the cost identity is trivial and the citation is not load-bearing; the
  **cross-goal formulation labelling survives** and is the contribution.
- *`20f6ab`*: the `2^{Θ(m)}` factor does not exist on the time axis; the **closure it
  reports is stronger than it claims** — the price of the representation escape is
  **0 on time** absent a-priori restriction, which the record itself correctly names as
  `KN-OPEN-001` recursively. Forward guidance intact.
- *`c5d183`*: the theorem is correct (I verified the proof: `T_{h1+h2}=T_{h2}∘T_{h1}`
  on `π(G)`, the action is transitive, `|π(G)| | N`, `N` prime); the **exhaustiveness**
  claim is not.

---

## 8. Required output block

```yaml
red_team_report:
  id: RT-20260806-7e7ce3
  task_id: TASK-20260806-7e7ce3
  claim_under_review: >-
    Five proposals for RQ-ECDLP-002 and its satellites, plus the frozen arity-threshold
    contract EXP-ICEX-146ff5 / H-ICEX-9e54c2, at snapshot commit f3d3b7e6.
  snapshot_verification: >-
    All 10 declared path_sha256 recomputed independently and matched, both against the
    working tree and against `git show f3d3b7e6:<path>`. commit_sha/parent_sha are null
    in the receipt; content binding is operative and holds.
  objections:
    - id: F-1
      severity: critical
      target: EXP-ICEX-146ff5 GATE-A arm A3
      statement: >-
        `T*/(c_LA*B*^2) == (m+omega-1)/(m-1)` is false for every omega != 2 on the arm's
        own declared grid; the correct identity is `T*/(c_LA*B*^omega)`. Verified at
        50-digit Decimal: m=5,omega=1.90 gives 0.2049837 vs target 1.475; m=8,omega=2.40
        gives 247.3761 vs 1.342857; m=12,omega=2.10 gives 3.275675 vs 1.190909.
        INV-GATE fires, the run set is completed_invalid, and nothing is emitted.
        Secondary: "exact rational equality" is unattainable at non-integer omega via
        decimal.Decimal (50-digit evaluation returns 1.4749...9989); the identity must be
        checked symbolically or the tolerance restated as relative < 1e-25.
    - id: F-2
      severity: critical
      target: H-ICEX-9e54c2 winning_window_shape; EXP-ICEX-146ff5 GATE-A arm A5
      statement: >-
        The admissibility clause d <= omega/(m-1) is derived at the harvest-all optimum
        B*_HA and applied globally, including to the one-relation-per-target branch whose
        operating point is the kink B_k=(m!N)^(1/m), where mu=1 and T_r=B_k >> 1 so the
        clause is vacuous. Applied only where derived, sup W(m,2) at m=7..12 becomes
        5/14, 3/8, 7/18, 2/5, 9/22, 5/12 - monotonically increasing. The "bounded and NOT
        monotone in m" title, the peak at m in {6,7}, the 2/(m-1) decay and the stated
        contrast with IDEA-20260803-fa9839 all fail.
    - id: F-3
      severity: critical
      target: IDEA-20260806-3b91c7
      statement: >-
        The novelty framing ("the corpus records the preprocessing lower bound and no
        achievability row") is refuted by knowledge/literature/KN-LIT-013.md, the
        source_ref of KN-TECH-005, which the record declares it did not open:
        "shows the bound is essentially tight via a matching generic algorithm";
        "tight (a construction achieves S*T^2 ~ N), so with advice the online cost can
        beat the classic sqrt(N) generic bound." Found by re-running the audit's own
        capped E10 uncapped (109 files, not 40).
    - id: F-4
      severity: critical
      target: IDEA-20260806-7ea402 claim (A)
      statement: >-
        The jump factor is computed as C(n,D+1)/C(n,D)=(n-D)/(D+1) while the record's own
        cost function uses cumulative ncols(D)=sum_{i<=D}C(n,i). At n=12,D=6 the true
        ratio is 3302/2510=1.3155, so the jump is 1.731 at omega=2 - cost RISES. The
        record's own sota_delta states J(12,6)=1.731. ncols is cumulative and strictly
        increasing, so the jump exceeds 1 at every D; "NOT MONOTONE ... AND BELOW 1" is void.
    - id: F-5
      severity: major
      target: IDEA-20260806-20f6ab
      statement: >-
        The C(m,m/2) gain is booked on time while the record concedes the half-lists are
        still BUILT before filtering. Building is the time cost; filtering after building
        reduces stored size, not generated size. At the record's own operating point
        B^m ~ m!N the join output is Theta(m!), already far below the build cost
        B^{ceil(m/2)}. Absent a-priori restriction the time gain is zero, not 2^{Theta(m)}.
    - id: F-6
      severity: major
      target: IDEA-20260806-c5d183 claim (B)
      statement: >-
        The theorem is correct (verified: T_{h1+h2}=T_{h2} o T_{h1} on pi(G); transitive;
        |pi(G)| divides N; N prime). The exhaustiveness claim is not: it enumerates
        violations of the three named hypotheses and treats the universally quantified g
        inside hypothesis (iii) as unrelaxable. Approximate equivariance - pi(g+h)=T_h(pi(g))
        for all h but only for most g - violates none of Classes I-III and breaks the
        transitivity argument. Either add Class IV or prove approximate equivariance
        implies one of I-III.
    - id: F-7
      severity: major
      target: IDEA-20260806-7ea402 claim (B)
      statement: >-
        "the deficit of 7,110 is 4.5 per cent of a gap of 24,621" conflates two
        denominators. Verified at source in EV-SIG-008: 7110/24621 = 28.9%;
        7110/156520 = 4.5%. The error is in the direction that makes the deficit look
        more negligible, in the one sentence the record says decides the lane.
    - id: F-8
      severity: major
      target: EXP-ICEX-146ff5 cost_model
      statement: >-
        D_trial is held independent of B and m while the optimizer raises B. With
        D = N^d * B^e the balance threshold becomes (m-omega-1-e)/(2*omega); e=1 alone
        moves the emptiness boundary from m<=3 to m<=4. SM-3 emits the Bezout-implied
        predicate degree d_p >= B*/3 - direct evidence the oracle cost scales with B -
        and never feeds it back. KN-LIT-7593: an eliminated dimension is not a speedup
        until its own cost is charged.
    - id: F-9
      severity: major
      target: H-ICEX-9e54c2 dominated_by; EXP-ICEX-146ff5 PM-5
      statement: >-
        C_pre + C_rel + C_LA are target-independent, so index calculus IS a preprocessing
        algorithm and the amortized comparator is the S*T^2 ~ N frontier (KN-LIT-013),
        not sqrt(kN) or k*sqrt(N). PM-5 is a Pareto claim, so `dominated_by: NOT
        APPLICABLE` is unchecked for it. At m=6, omega=2, d=1/3 the contract's own row has
        S=N^(4/21), T=N^(1/3), S*T^2 = N^0.857 << N.
    - id: F-10
      severity: moderate
      target: EXP-ICEX-146ff5 CTRL-NULL, CTRL-DEGENERATE D1
      statement: >-
        Both are identities, not controls. KN-FIND-007 is a proved double count, so
        enumerating it catches coding bugs and can never return a mathematical negative;
        F2's "either KN-FIND-007 or this instantiation is wrong" is not a live disjunction.
        D1 reduces to T_r*D = (B/mu)*(mu*N) = N*B exactly by substitution.
    - id: F-11
      severity: moderate
      target: EXP-ICEX-146ff5 CTRL-CONVENTION, INV-PREREG
      statement: >-
        Under the description's global reading the divergence set is {d > (omega-1)/m},
        non-empty for every m>=2 on the declared grid, so INV-PREREG's empty-set branch is
        unreachable and the control cannot fail. Only the within-window reading (which
        yields the pre-registered "non-empty for every m>=5") can fail. Disambiguate.
    - id: F-12
      severity: moderate
      target: EXP-ICEX-146ff5 GATE-A naming; 5.4 re-partition premise
      statement: >-
        GATE-A performs no external calibration. A1 and A2 are algebraic consequences of
        the model's own two formulas; A3-A5 are internal identities. The only externally
        anchored quantity is GATE-B's 2-2/n, pre-registered UNRUN. Rename to
        internal-consistency gate and carry that statement onto every emitted table.
    - id: F-13
      severity: moderate
      target: EXP-ICEX-146ff5 dependency_contract.verification_performed_at_design_time
      statement: >-
        numpy is NOT installed in this worktree and sympy is NOT installed; harness/runner.py
        imports sympy at module scope (line 28) and cannot be imported here. The spec
        inferred present-tense environment state from historical manifests produced on other
        machines. The stdlib-only conclusion is vindicated and the contract IS runnable
        (Python 3.11.15, Decimal prec=50 verified); the environment statement is wrong.
    - id: F-14
      severity: moderate
      target: EXP-ICEX-146ff5 execution_authorization P3 / revisit condition R-D
      statement: >-
        R-D names five items; four are charged and relation rank is declared-omitted, and
        R-D's second clause ("needs its own IDEA-* record") is unmet - source_proposal_id
        is still IDEA-20260803-fa9839. R-D is NOT satisfied on its own text.
    - id: F-15
      severity: moderate
      target: IDEA-20260806-9d47e2, 7ea402, c5d183, 20f6ab dominated_by
      statement: >-
        All four cite "the memory-matched generic baseline sqrt(N/S) derived in
        IDEA-20260806-3b91c7" as a frontier row. An unreviewed novelty_status:unverified
        sibling in the same batch is load-bearing for four records' Pareto honesty; if it
        were withdrawn four dominated_by fields silently become wrong. Recite to KN-LIT-013.
        9d47e2 and 20f6ab additionally evaluate it at sigma=1/2, outside 3b91c7's own
        declared cap sigma in [0,1/3].
    - id: F-16
      severity: minor
      target: IDEA-20260806-3b91c7 (D) and prediction 3
      statement: >-
        Quotes B* = N^{1/(m+1)} as "the corpus's recorded two-term optimum" - the exact
        form DEC-20260805-bb162b section 5.2 ruled false wherever d>0 and that this batch's
        GATE-A arm A4 exists to fail. The point prediction "differ by exactly 1/(2(m+1))"
        holds only on the d=0 row; off it the difference is (1+d)/(2(m+1)). Direction is
        conservative (the correction is understated), but the quoted number is wrong.
    - id: F-17
      severity: minor
      target: EV-SIG-008 vs EV-DREG-008 (observed at source, not adjudicated)
      statement: >-
        EV-SIG-008 GATE 2 FINAL records sem D6 rank 138,570 and deficit 17,950;
        EV-DREG-008 records deficit_genuine=17947 (=156520-138573), i.e. rank 138,573.
        Two committed records differ by 3 on the same quantity. Recorded per AGENTS rule 8.
    - id: F-18
      severity: minor
      target: EXP-ICEX-146ff5 objective
      statement: >-
        "with exact arithmetic and no measurement" is contradicted by CTRL-NULL (up to
        11.4M enumerated multisets over four Z/N families, emitting SM-1 measured means)
        across a five-run 0.25-CPU-hour plan. This matters because the P2 routing argument
        leans on the deferral being on measurement.
  required_controls:
    - >-
      CTRL-NULL must emit two additional columns per family per cell: (i) coverage
      fraction - the share of the N targets with >= 1 decomposition; (ii) rank of the
      first B successful relations. The mean is theorem-fixed and CANNOT vary, so its
      constancy is not evidence; coverage and rank SHOULD vary with base geometry and
      collapse for family (iv). This converts a tautology into a control that can fail
      and simultaneously measures the omitted relation-rank term.
    - >-
      Repair GATE-A A3 to T*/(c_LA*B*^omega) and restate its tolerance as symbolic
      equality or relative < 1e-25. Without this nothing is emitted at all.
    - >-
      D_trial-B coupling sensitivity: recompute the window under D = N^d * B^e for
      e in {0, 1/2, 1, omega_GB*(m-1)/m} and report how the emptiness boundary and the
      supremum move. One extra loop over an existing table.
    - >-
      Emit the memory-matched second column beside every window row: balance branch
      d < (m-omega-2)/(2*omega) and kink branch d < (m-3)/(2m), with the amortization
      policy named on the row. Two lines of algebra; changes the m=4 verdict.
    - >-
      Compare PM-5 against the S*T^2 ~ N preprocessing frontier (KN-LIT-013) in addition
      to the two rho multi-target conventions, and report the memory column for the rho
      batch bracket so the frontier is matched.
    - >-
      Disambiguate CTRL-CONVENTION to the within-window divergence set, or INV-PREREG's
      empty-set branch is unreachable.
    - >-
      Charge relation rank via IDEA-20260805-061f97's left-kernel fixed point
      x = 1 - e^{-mx} (relations needed B/x*, x* ~ 0.797 at m=2). A constant factor that
      moves no exponent, so the omission becomes provably exponent-neutral within the model.
    - >-
      For IDEA-20260806-3b91c7: replace the sigma=0 calibration as the ranking control
      with a sigma=1/3 check, where the rival law (Shoup: T=sqrt(N) at every memory)
      predicts N^{1/2} and this record predicts N^{1/3}, and KN-LIT-013 supplies the answer.
  counterexample_or_mutation: >-
    THE SINGLE CHEAPEST OBSERVATION THAT INVALIDATES THE CONTRACT'S OUTPUT: evaluate
    GATE-A arm A3's second clause at ONE cell, m=5 omega=1.90. It returns 0.2049837
    against a target of 1.4750. INV-GATE fires; the run set is completed_invalid; no
    window, no memory table, no multi-target crossover and no satellite table is emitted.
    Cost: two lines of decimal.Decimal, under a minute, zero compute budget.
    THE SINGLE CHEAPEST OBSERVATION THAT FALSIFIES THE TOP-RANKED NEW PROPOSAL
    (IDEA-20260806-3b91c7, recommended_priority high, ranked first by its own author):
    open knowledge/literature/KN-LIT-013.md - the source_ref of the very technique entry
    the record quotes, and the one file the record states it did not open. Its
    "Key claims" section reads "tight (a construction achieves S*T^2 ~ N), so with advice
    the online cost *can* beat the classic sqrt(N) generic bound." That single file read
    falsifies the record's novelty framing at zero compute. It does NOT falsify the
    comparator-convention audit, which survives and which the record itself pre-declared
    would survive.
    THE CHEAPEST MUTATION THAT SEPARATES SIGNAL FROM ARTIFACT IN THE WINDOW: recompute
    the trial count T_r at the ACTUAL operating point of each branch instead of at
    B*_HA. On branch 2, mu=1 by construction and T_r=B_k ~ N^{1/m} >> 1, so the
    admissibility clause is inactive and sup W(m,2) rises monotonically from m=7 on.
    One boolean per branch in the window routine, and it fires A5.
  baseline_comparison: >-
    RHO: correctly used single-target, pinned at 0.886*sqrt(N) against a certificate-
    verified committed run (RUN-YIELD-001-BASELINE-RHO-BSGS) with a measured sweep band -
    good practice. BSGS: present with sqrt(N) memory single-target; ABSENT multi-target.
    CLOSEST SPECIALIZED BASELINE (Gaudry-Diem extension-field index calculus): reachable
    only through GATE-B, which is pre-registered UNRUN, so the model is never compared
    against the one algorithm in its own family that demonstrably works; the
    observation_collision block records this honestly as declared non-tightness.
    PREPROCESSING FRONTIER S*T^2 ~ N (KN-LIT-013): the correct comparator for the
    amortized PM-5 row and it is absent (F-9). MEMORY-MATCHED GENERIC BASELINE: absent;
    computed here - it moves the emptiness boundary from m<=3 to m<=4 and the balance
    threshold from (m-3)/4 to (m-4)/5 at omega=2, conditional on the amortization policy.
    VAN OORSCHOT-WIENER TIME-MEMORY INTERPOLATION: not charged anywhere; the contract
    compares a memory-N^beta algorithm against a memory-O(1) baseline on the time axis
    alone, which is the mismatch IDEA-20260806-3b91c7 names correctly.
  heuristic_challenges:
    - >-
      HEUR-AT-1: the MEAN is exact and geometry-independent, correctly. INDEPENDENCE AND
      CONCENTRATION ARE NOT PROVED and the record says so. But branch 2 - which supplies
      the window's supremum at every m >= 5 - operates at exactly mu = 1, the regime where
      the mean-vs-success-probability gap is widest, and the 1.582 = 1/(1-e^{-1}) bound is
      a POISSON HEURISTIC about the count distribution, not a bound on the object. The
      random-model transfer is asserted for the mean (where it is a theorem) and silently
      extended to the distribution (where it is not).
    - >-
      HEUR-AT-1's own validation clause ("the exponent is identical under both harvesting
      conventions") is FALSE above d = (omega-1)/m, and the contract is CORRECT to
      pre-register it as false - I re-derived it (ORPT slope 1 vs harvest-all slope
      omega/(m+omega-1) < 1, equal at the kink, strictly larger above). Credit where due.
    - >-
      HEUR-AT-2: omega=2 headline with EV-STR-002/EV-STR-003 cited as a contested pair
      rather than a verdict - honest. The B^omega charge drops the O(m) nonzeros per row,
      which is constant at fixed m but not at the coverage-optimal arity m ~ log N/log log N.
    - >-
      HEUR-AT-3 is the weakest link and carries the declared deliverable. supporting_results
      is EMPTY and the record states it is "NOT VERIFIED against any measured solver in
      this corpus". PM-2 - the declared exit from the deferral deadlock - is therefore
      wholly conditional on an unsupported heuristic. Disclosed, but a deliverable resting
      entirely on an unvalidated heuristic is a CONDITIONAL INSTRUMENT, not an EXIT, and
      should be labelled so on every row and in every summary.
    - >-
      HEUR-AT-4 is well handled: stated as a reviewable claim rather than an omission,
      with CTRL-PARAM as a control that can genuinely refute it, and with KN-FIND-c41ea9's
      untested compounding clause left open in both directions. This is the model for how
      the other three should be written.
    - >-
      IDEA-20260806-3b91c7 H1/H2: the r-adding-walk-as-random-function assumption is
      correctly numbered, correctly labelled imperfect for small r, and given a direct
      toy-scale sampling plan with a tail check - and the record states plainly that NO
      correspondence trick exists to reach crypto scale for this quantity rather than
      glossing it. That is the right disclosure. H3 (offline chargeable per curve) is
      correctly identified as a POLICY and discharged by reporting three policies rather
      than choosing one.
  cost_model_challenges:
    - "OMITTED, exponent-moving: D_trial-B coupling (F-8)."
    - "OMITTED, verdict-changing: preprocessing frontier as the amortized comparator (F-9)."
    - "OMITTED: memory column on the rho multi-target batch bracket; BSGS multi-target row entirely."
    - "OMITTED: van Oorschot-Wiener / memory-matched interpolation on the baseline side."
    - "DECLARED-OMITTED: relation rank (cheap discharge available, see required_controls)."
    - "ASSUMED, not charged: single-level descent; kappa_desc in {1,m,m^2} substitutes for depth."
    - "CHARGED AT ZERO: factor-base membership lookup during collection."
    - "UNDECLARED POLYLOG: log N bit-cost per modular multiply inside c_LA; no global 'polylog dropped' statement."
    - "DROPPED CONSTANT: O(m) nonzeros per row in B^omega - not constant at coverage-optimal arity."
    - >-
      BOOKKEEPING: total = per-attempt x inverse success probability is structurally
      correct (T_r = B/mu), but mu is a MEAN used as a success probability, and at the
      branch-2 operating point mu = 1 exactly, which is where that substitution is least safe.
  reduction_and_scope_challenges:
    - >-
      The satellite conversion (HEUR-AT-3, Macaulay charge inverted to D_reg_max) is
      correctly declared "NOT a published reduction - an internal conversion" and carries
      its conditional forward. Hypotheses checked: it requires the solve to be
      linear algebra on a Macaulay matrix at a single degree; it does not model
      degree-falls, F4/F5 rewriting, or the cumulative sum over degrees that
      IDEA-20260806-7ea402's own cost function uses. The two records in this batch use
      DIFFERENT cost functions for the same object and neither cites the other.
    - >-
      Affected-vs-safe scope: NOT INFLATED. admission_and_ceiling, interpretation_limits,
      the toy tier, the model_evaluation:true stamps, certificate:kind:none with a
      justification, and CTRL-RANK-DIRECTION's LOWER-BOUND-MODEL stamp collectively
      forbid every over-reading I tried to construct. quantifier_order correctly refuses
      to invert to "there exists an oracle". I found NOTHING licensing a prime-field
      weakening claim or presenting a threshold as though an oracle meeting it exists.
    - >-
      ROUTING: the contract is homed in a GOAL-ECDLP-001 batch while binding RQ-ICEX-001,
      over a standing decline (DEC-20260805-bb162b) that nothing in this batch supersedes.
      The contract is right not to pre-empt it; the batch was wrong to dispatch before it
      was resolved. The ICEX deferral is on MEASUREMENT and does not bar a zero-compute
      derivation - but this contract is not one (F-18).
    - >-
      5.4 RE-PARTITION: ACCEPT, with two mandatory amendments (repair A3; relabel GATE-A
      as internal-consistency with no external calibration performed, carried verbatim
      onto every emitted table). It is not a relaxation of the four protected readings.
      Restoring the blanket block would reproduce the indefinite cap the decision itself
      flagged, and premature closure is a failure mode symmetric with overclaiming.
  proof_architecture_challenges:
    - >-
      QUANTIFIER-ORDER (c5d183): the trichotomy quantifies over the three named hypotheses
      and treats the universally quantified g inside hypothesis (iii) as unrelaxable.
      Approximate equivariance is a fourth violation mode. Additionally, (C)'s point
      prediction carries an escape clause ("UNLESS the meter's step set is a proper subset
      of G, in which case its readings are Class I readings") that re-labels any refuting
      observation rather than counting it - a prediction that cannot fail.
    - >-
      BOUNDARY AND STRICTNESS (3b91c7): the record caps sigma at 1/3 with a hand-waving
      reason, then evaluates its BSGS domination verdict - which it calls "the cheapest
      single check in the record" - at sigma = 1/2, OUTSIDE its own declared valid range.
      Either the cap is wrong or the BSGS verdict is unlicensed. Two sibling records
      propagate the same out-of-range evaluation (F-15).
    - >-
      METHOD CEILING (EXP-ICEX-146ff5): correctly stated - "its ceiling as a positive
      instrument is zero by construction" - and I could not break that statement. The
      ceiling for the NEGATIVE direction is also correctly bounded by the observation
      collision. This block is well done.
    - >-
      NEARBY-OBJECT (EXP-ICEX-146ff5): the declared nearby-object control (replace the
      conservation mean by a naive estimate or an empirical mean) is real, but the nearest
      object for which the desired conclusion is FALSE is extension-field index calculus
      itself, and that comparison sits behind GATE-B, pre-registered UNRUN. The nearby
      object that could discriminate is the one the design cannot reach.
    - >-
      OBSERVATION-FIBRE (3b91c7): the record volunteers its own collision - the chain
      table at sigma=1/3 and a hypothetical index calculus at B=N^{1/3} share the triple
      (1/3,1/3,2/3) - and names the separator (source of the memory: known-log endpoints
      vs a factor base with unknown logs). Correctly done.
  narrowest_supported_statement: >-
    WITHIN THIS SNAPSHOT: (1) The arity-threshold contract's OPTIMIZER algebra is correct
    and defect 5.2 is correctly repaired; the harvest-all/one-relation-per-target exponent
    divergence above d=(omega-1)/m is real and correctly pre-registered as refuting
    HEUR-AT-1's own validation clause; the three counting-convention discriminations in
    GATE-A A1 are all correct. (2) The contract as frozen CANNOT EXECUTE TO AN OUTPUT:
    A3 is false at four of five declared omega values and INV-GATE fires. (3) The window's
    SHAPE - bounded, peaked at m in {6,7}, decaying like 2/(m-1) - is NOT supported, because
    it depends on a constraint applied at an operating point where it was not derived.
    (4) IDEA-20260806-3b91c7's achievability derivation is redundant with committed
    KN-LIT-013, but its comparator-convention audit is CORRECT, MATERIAL, and
    independently confirmed here: the amortized and multi-target rows of this corpus are
    compared against a memory-O(1) baseline while charging the candidate its memory.
    (5) IDEA-20260806-7ea402's structural claim (cost is C(d_solve), an integer, so a
    continuous deficit has zero cost derivative almost everywhere) SURVIVES and is
    strengthened by EV-SIG-008 read at source - rank 149,410 (null) and 138,570 (sem)
    against ncols-|V| = 174,031 puts d_solve > 6 in both arms - while its jump factor
    and its 4.5 per cent both fail. (6) c5d183's theorem is correct; its exhaustiveness
    is not. (7) 20f6ab's closure is stronger than it claims and its number is on the
    wrong axis. (8) 9d47e2's contribution is the cross-goal formulation labelling, not
    the cost identity. NOTHING HERE IS AN IMPOSSIBILITY CLAIM, NOTHING CLOSES A LANE,
    AND KN-OPEN-001 IS UNTOUCHED IN BOTH DIRECTIONS.
  next_concrete_action: >-
    ONE versioned protocol_amendment to EXP-ICEX-146ff5, snapshot-committed and
    independently re-reviewed before any execution, containing exactly four changes and
    no others: (i) GATE-A A3 second clause corrected to T*/(c_LA*B*^omega) with the
    tolerance restated as symbolic equality or relative < 1e-25; (ii) the trial-count
    admissibility clause restricted to the branch on which it is derived, with the
    branch-2 trial count computed at B_k and reported, and A5's pre-registered rationals
    RE-DERIVED and RE-FROZEN under the correction BEFORE any run (a pre-observation
    change, recorded as such); (iii) CTRL-NULL extended by the coverage-fraction and
    first-B-relation-rank columns; (iv) GATE-A relabelled as an internal-consistency gate
    with "no external calibration performed" carried verbatim onto every emitted table.
    P1 is thereby answered ADVERSELY on three grounds - a materially omitted cost term
    (F-8), a calibration gate that fails for the wrong reason (F-1), and two controls
    incapable of returning a mathematical negative (F-10) - so execution remains
    unauthorized until that amendment exists and is re-reviewed. P2 and P3 are separately
    unresolved and are Coordinator decisions, not mine: R-D is not satisfied on its own
    text (F-14) and the cheap discharge is named above.
  artifact_paths:
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-9c41dd/reviews/TASK-20260806-7e7ce3/red_team_report.md
  records_reviewed:
    - experiments/EXP-ICEX-146ff5/specification.yaml
    - ledger/hypotheses/H-ICEX-9e54c2.yaml
    - ledger/proposals/IDEA-20260806-3b91c7.yaml
    - ledger/proposals/IDEA-20260806-9d47e2.yaml
    - ledger/proposals/IDEA-20260806-7ea402.yaml
    - ledger/proposals/IDEA-20260806-c5d183.yaml
    - ledger/proposals/IDEA-20260806-20f6ab.yaml
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-9c41dd/tasks/TASK-20260806-10e97e/duplication_audit.md
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-9c41dd/tasks/TASK-20260806-10e97e/ideation_report.md
    - coordination/goals/GOAL-ECDLP-001/batches/BATCH-9c41dd/tasks/TASK-20260806-cd81c5/design_report.md
  records_opened_at_source_beyond_the_snapshot:
    - knowledge/literature/KN-LIT-013.md
    - knowledge/techniques/KN-TECH-005.md
    - ledger/evidence/EV-SIG-008.yaml
    - ledger/evidence/EV-DREG-008.yaml
    - ledger/goals/GOAL-ICEX-001.yaml
    - harness/runner.py
  status_changes_made: none
  raw_artifacts_edited: none
  commits_made: none
```
