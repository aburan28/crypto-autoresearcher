# Adversarial re-screen — slice5 (18 records)

Reviewer: red-team. Repo read-only at `/tmp/wt-ideas-100` (main, HEAD `9b49a54f0`).
Web search unavailable — **all external-novelty verdicts below are UNADJUDICATED**;
every verdict is an internal-corpus / internal-soundness verdict.

## Verdict table

| ID | Verdict | One-line reason |
|---|---|---|
| `IDEA-20260808-46d7ef` | NOVEL (2 corrections) | Mechanism sound; pre-registered "≥5 bits" WHT gain assumes exactly ONE length-256 transform (3 transforms ⇒ 3.42 bits), and the nearest technique records were invisible to its screen. |
| `IDEA-20260808-6a2b50` | NOVEL | Change-of-frame diagnostic is genuinely absent from the corpus; honest that its load-bearing theorem is unread. |
| `IDEA-20260808-90c7ab` | **REFUTED** (prediction 2 / falsification cond. 2) | Computed: the ONLY named matched null (`EV-ECDLP-65b004`'s documented reshape) **fires** S1 — its scalar multiset gains ~15 values in the reshape commit. |
| `IDEA-20260808-fa1d80` | **REFUTED** | The graph of `[k]` is a Lagrangian of `(E×E)[N]` iff `k²≡−1 mod N`. Enumerated N=5,7,11,13,17: at N=11 (inside its own test range) **no k at all** works. |
| `IDEA-20260808-5ee6b4` | **REFUTED** (part C) + PARTIAL-OVERLAP | BSGS/kangaroo on a group action needs a *known target*; a predicate supplies none, so the "p^{1/2}→p^{1/4} coset collapse" — the record's self-declared "actual content" — does not follow. Sibling `28361d` states the contradiction explicitly. |
| `IDEA-20260808-45af43` | NOVEL (2 corrections) | Closure is sound, but its only PLANTED positive control (`a = 3b`) is **provably impossible** for prime `p≡1 mod 3`; 0/1124 primes tested, and the six traces are always distinct. |
| `IDEA-20260808-8e13ff` | NOVEL (process) | Gate is real and absent from the corpus; count is wrong (58 KN-FIND, not 57) and it needs a `discriminated_from` line against sibling `ea3b4f`. |
| `IDEA-20260808-dd4d30` | NOVEL | FrodoKEM params verified exactly (n̄=8, n=640/976/1344, q=2^15/2^16); rank-n̄ embedding is legitimate; predicts Δ≈0 honestly. |
| `IDEA-20260808-2ef5c8` | PARTIAL-OVERLAP | Algebra fully verified, but it is the **same cost model** as sibling `812554` under `θ=(m−1)σ`; title's "misses by exactly 1/2 in theta at every arity" is false for odd m (miss = 1), contradicting its own prediction table. |
| `IDEA-20260808-b6ba7a` | NOVEL (low ceiling) | All five Classic McEliece redundancy rationals verified exactly; claim (A) is the standard sub-linear-weight fact it itself cites; claim (B)'s "exactly three parameterizations" is contradicted by its own confounder 3. |
| `IDEA-20260808-c1abd1` | **REFUTED** | Its defining falsifiable quantity `g = log₂min(C_lattice,\|B_τ\|) − log₂max(C_reduce,\|B_τ\|)` is **≤ 0 identically**, for all inputs, because `max(x,\|B\|) ≥ \|B\| ≥ min(y,\|B\|)`. Verified over a grid: max g = 0.0. |
| `IDEA-20260808-51e40f` | **SCOPE-INFLATED** | Headline "up to 1.22N" delta for MAYO/SNOVA is measured against Groebner-over-F₁₆; the record's own descent + the corpus's own BooleanSolve (KN-TECH-053) already gets 0.83N of it. Marginal contribution is 0.39N — a 3.1× overstatement. |
| `IDEA-20260808-812554` | **REFUTED** + substantive duplicate of `2ef5c8` | Its "admission gate" `σ < 1−2/(m−1)` is derived from an interior optimum that is **infeasible** for every `σ > 2/(m−1)`: `trials = m!N/B^{m−1} < 1` there. MITM at m=8 (σ=4/7) passes its gate at N^{2/5} but truly costs N^{4/7} > rho. |
| `IDEA-20260808-589c19` | NOVEL | Every number verified against `KN-TECH-057` and `H-RSA-68884a` (1.949616, 2.2435, 0.961500, 0.835550, 0.0266, 11.1×). One overread of KN-TECH-057 noted. |
| `IDEA-20260808-02a046` | **REFUTED** | Under its own HA-1 the per-tree counts `C_j` are **independent**, so the product factors exactly: measured ratio 1.0000±MC noise in 5/5 cells, matching `(1−(1−2^{−a})^q)^k`. The correlation it exists to capture is identically zero. |
| `IDEA-20260808-ee5d81` | PARTIAL-OVERLAP (`dominated_by` incomplete) | Steps (1)–(3) are correct, but the row that dominates it on **both** axes in exactly the binding regime — MITM/vOW on the commitment walk from the known E₀, 2^{e/2} time and **one** signature — is not in its frontier check. |
| `IDEA-20260808-71c2b2` | NOVEL (3 required additions) | All arithmetic independently reproduced (0.8165 → 0.6667, 2^{6.55}, 2^{9.87}, both stationarity conditions). Needs a numbered heuristic for E[N]=1 ⇒ P>0, and the "per-entry correction cancels in the ratio" claim is false. |
| `IDEA-20260808-4f3ef4` | **REFUTED** / not decision-relevant | No `goal_id`. Its Arm D is informationally the same null as the existing Arm C (identical E[hits] = \|F\|·pairs/p at all four frozen cells), and its motivating contrast was already adjudicated by `DEC-20260808-6a7ac4` (Y_A = Y_B exactly, 40/40). |

---

## Non-`NOVEL` verdicts, in detail

### `IDEA-20260808-90c7ab` — REFUTED at its own named null

**The claim.** Prediction 2: *"S1 firings on legitimate reshapes — predicted: **Zero, by construction** of the value-multiset projection. `EV-ECDLP-65b004`'s documented reshape is the specific null and **must not fire**."* Falsification condition 2: *"The documented reshape fires — over-strict, unusable, must be fixed before deployment."* HA-16 asserts the projection is invariant under reshaping.

**The check.** The record's motivating facts verify exactly: `a325d824` at 19:07:05 archives 13 runs + EV-STR-002 + DEC-20260726-006; `5de2db97` at 20:40:10 (93 min later) touches 6 files, **694 insertions, 213 deletions**, and adds **zero** paths under `runs/`. So S2's known positive holds.

The named null does not. `EV-ECDLP-65b004` is born in `b34e6c76d` and reshaped in `287f8eb7c`. I computed the leaf-scalar multiset of both versions (recursive leaf walk, `Counter` over `repr`). The multiset **changes**: ~15 new scalars appear (`'H-XOR-d1a480'`, `'contradicts'`, `'empirical_only'`, `'preliminary'`, `'toy'`, four `sha256:...` values, three long disclosure strings) and `'RUN-SEMAEV-f48dd1-grid'` goes from multiplicity 1 to 2. S1 as written ("a ledger record's SCALAR VALUE SET changes in a commit later than its birth commit") therefore **fires on the null**.

Two consequences the record does not survive as written: (a) prediction 2 and falsification condition 2 are decided against it before any implementation; (b) worse, **the null is not realizable at all** — there exists no commit in the history in which a *pure* reshape of this record occurred, because the reshape and the disclosure additions were committed together. Phase 1's "known null" cannot be run as specified.

**Narrowest valid conclusion / exact repair.** No pre-existing value was deleted or altered — every diff line except one multiplicity bump is an addition. So the correct predicate is monotone, not equality:

> S1′: fire iff the record's scalar multiset **loses** an element or has an element's multiplicity **decrease** after its birth commit; additions alone do not fire. S2′ additionally requires that the added scalars lie outside declared `disclosure` blocks.

That repair passes the real null and still fires on `5de2db97` (whose rewrite of EV-STR-002/DEC-20260726-006 replaced conclusions). It also makes the record's own confounder 1 ("legitimate additions do add numeric fields without new runs — `EV-ECDLP-65b004` does exactly this") consistent with its predictions, which it currently is not.

**Also:** `goal_id: GOAL-ECDLP-001` with `question_id: RQ-INSTR-f8faa0`; `ledger/goals/GOAL-ECDLP-001.yaml` does not exist at that path, so the goal binding could not be verified.

---

### `IDEA-20260808-fa1d80` — REFUTED: the object it wants to detect is not in the pencil

**The claim.** *"Lagrangian subgroups K of (E×E)[N] containing v are in bijection with the N+1 isotropic lines… **Exactly one of them is the graph K_k = {(R,[k]R)}**, and its quotient (E×E)/K_k … is REDUCIBLE."* Prediction 1: *"exactly zero for K_k and nonzero for all others, at every tested instance."* Test range: `N ∈ {11,13,…,101}`.

**The computation.** Under the product principal polarisation the pairing is `e((R₁,R₂),(S₁,S₂)) = e(R₁,S₁)·e(R₂,S₂)`, i.e. the symplectic form `J ⊕ J` on `(Z/N)^4`. For `u=(x,kx)`, `w=(y,ky)`: `⟨u,w⟩ = (1+k²)·x^T J y`. So `K_k` is isotropic — hence Lagrangian, hence in the pencil — **iff `1 + k² ≡ 0 mod N`**.

Direct enumeration (all `N+1` Lagrangians through `v=(P,[k]P)`, all `k`):

```
N=5  (N+1=6):  graph[k] in pencil for k=2,3 only        (2 of 4 values of k)
N=7  (N+1=8):  graph[k] in pencil for NO k              (0 of 6)
N=11 (N+1=12): graph[k] in pencil for NO k              (0 of 10)
N=13 (N+1=14): graph[k] in pencil for k=5,8 only        (2 of 12)
N=17 (N+1=18): graph[k] in pencil for k=4,13 only       (2 of 16)
```

The `N+1` count is correct; the identification of the graph as one of them is not. For `N ≡ 3 mod 4` — including `N = 11`, the **first** prime in the record's own stated test range — the construction is empty for every `k`. For `N ≡ 1 mod 4` it exists for exactly 2 of the `N−1` secrets. So prediction 1 fails at toy scale before any Igusa invariant is computed, and the "certificate" cannot certify a random ECDLP instance.

**No standard convention repairs it.** The graph of an isogeny `φ` is isotropic only when `deg φ ≡ −1 mod N` (product polarisation) or `deg φ ≡ +1` (anti-isometry convention). `[k]` has degree `k²`; neither condition is generic. This is exactly the constraint that forces Kani's lemma to use an isogeny **diamond** with `deg φ + deg ψ = N`.

The record's own `why_not_a_renamed_known_approach` states the killing fact and then proceeds past it: *"here the relevant endomorphism [k] has degree k² far above N, so the Kani hypothesis fails and the construction is used only as a classifier."* The degree condition is not a Kani-specific convenience — it is the isotropy condition, and failing it means there is no quotient ppav to take Igusa invariants of.

**Cheapest discriminating control (already run above):** the `(1+k²) mod N` column. Any future version must state which endomorphism (not `[k]`) supplies a Lagrangian and how it is obtained without `k`.

---

### `IDEA-20260808-5ee6b4` — REFUTED in part (C); PARTIAL-OVERLAP with `28361d`

**The claim (the record's own "ACTUAL CONTENT").** *"if the weak set W is a UNION OF COSETS of a subgroup H ≤ Cl(O) of index m, … locating a coset of H is a vectorization-type problem on the quotient torsor Cl(O)/H of size m, solvable by meet-in-the-middle / kangaroo in O(√m) class-group action evaluations. Taking m = h … gives √h = p^{1/4} — HALF THE EXPONENT of rho."*

**The objection.** Baby-step/giant-step and kangaroo on a free abelian group action require **two known endpoints**: baby steps `a_i·E_pub`, giant steps `b_j·E_target`, join on curve equality. Here `E_target` is precisely what is unknown; the attacker holds only a predicate `W`. Coset structure changes nothing about that:

- If the attacker knows both `H` **and** the coset representative `g₀H`, he computes `g₀·E_pub` in **O(1)** actions — not `√m`.
- If he knows `H` but not the coset, the only operation available is: choose a coset representative `g`, form `g·E_pub`, test `W`. That is a linear scan over `m` cosets. There is no second list to giant-step from, so no meet-in-the-middle exists.
- At `m = h` (H trivial) the "coset" is a single unknown curve and the coset structure conveys literally zero information beyond "W is a singleton".

So the dichotomy is not `linear scan` vs `√m`; it is `O(1)` (representative derivable from the public description of W) vs `linear` (not derivable). The claimed factor-two exponent move does not exist.

The record states the principle that refutes it one paragraph earlier: *"the CSIDH vectorization cost √h … applied to the case where **BOTH endpoints are known**. That is not this: here one endpoint is unknown and only a predicate on it is known, **which is why the generic case is a linear scan and not √h**."* It then asserts `√m` for the coset case without saying what plays the role of the second endpoint.

**Independent corroboration inside the same batch.** `IDEA-20260808-28361d` (C1): *"g = 1 (a single exceptional curve) NEVER helps, at any c, not even c = 0, because the search alone costs √N · polylog."* That is a direct contradiction of 5ee6b4's `m = h` collapse, filed the same day, and neither record cites the other.

**Cheapest discriminating control.** The record's own PLANTED-COSET arm, run with the coset representative **withheld from the attacker**. Predicted under my objection: linear in `m`, not `√m`. As currently specified the planted arm hands the attacker the representative, so it would "confirm" a speedup that is really `O(1)` bookkeeping.

**PARTIAL-OVERLAP, exact text to add.** Parts (A) and (B) are re-derived independently in `IDEA-20260808-28361d`, including the identical walk-and-test cost `(h/g)·τ` with the same symbols `h, g, τ`. 5ee6b4's `discriminated_from` says *"Slice record E3-02 states the density criterion for ATTACKS; … the two share only the class-size input"* — that is inaccurate. Required addition:

> `IDEA-20260808-28361d` independently derives the same entropy identity (h(O) = |D|^{1/2+o(1)} ≍ √N) and the same walk-and-test cost (h/g)·τ + c. This record is not novel with respect to parts (A) and (B); its only distinct content is the coset criterion in part (C), which `28361d`'s corollary (C1) contradicts at m = h.

**Minor.** The headline `(1/2)log₂p + O(log log p)` is one-sided without GRH: the upper bound `h ≪ √|D| log|D|` is unconditional, but the matching lower bound needs Littlewood/GRH — Siegel's is ineffective, as the record's own `interpretation_limits` concedes while the title does not.

---

### `IDEA-20260808-c1abd1` — REFUTED: the defined gap can never be positive

**The claim.** *"the resulting cost is C_reduce + L·C_decode + |B_τ| hash calls, whose minimum over L is approximately **max(C_reduce, |B_τ|)** — strictly below the published **min(C_lattice, |B_τ|)** whenever the lattice arm's cost is dominated by reduction rather than decoding."* Falsifiable form: `g = log₂[min(C_lattice,|B_τ|)] − log₂[max(C_reduce,|B_τ|)]`, either `> 0` or `= 0`.

**The check.** For any reals, `max(C_reduce, |B_τ|) ≥ |B_τ| ≥ min(C_lattice, |B_τ|)`. Therefore **`g ≤ 0` identically**, for every cost model, every parameter set, and every value of `C_reduce` and `C_lattice`. Confirmed numerically over a 4×4×3 grid of plausible values: max `g` = 0.0. The record's `g > 0` branch — the entire reason it is filed at `recommended_priority: high` with `P(g > 3 bits) ~ 0.3` — is arithmetically impossible. What the record has constructed is the **sum** of the two arms, not an interpolation between them; adding a lattice reduction to a hash search cannot reduce the hash count below the `|B_τ|` it charges itself.

**And the obvious repair is also blocked.** A genuine claw would charge `L + Q_H ≥ 2√|B_τ|`, not the product. That is unavailable here: `H` is evaluated on `μ ‖ w` where `w = [A|I]r + t·c` is the vector produced by the *specific* decoding. Hash outputs computed for one `w` cannot be matched against a decoding that produced a different `w`, so the two lists are not cross-joinable and total hash work is `Σ_w Q_H(w) = |B_τ|`. The record's own mechanism paragraph assumes this away ("two lists, one lattice-side, one hash-side").

**Separately**, the pinned cost model forecloses `g > 0` a second time: core-SVP hardness `2^{0.292β}` is *by definition* the cost of one SVP-oracle call, so the published `C_lattice` already equals (indeed undercharges) one reduction. `C_reduce < C_lattice` is not attainable in the model the record itself pins.

Verified challenge-space sizes for the record: `log₂|B_τ|` = 192.76 / 225.35 / 257.01 at τ = 39/49/60. The τ recall is correct.

---

### `IDEA-20260808-812554` — REFUTED: the admission gate admits infeasible operating points

**The claim.** *"beating rho requires β(m−1)(1−σ) > 1/2 together with 2β < 1/2, hence β < 1/4 and **σ < 1 − 2/(m−1)** … this three-line table is the admission gate every future proposal must clear."*

**What is right.** The identity is correct: `C_rel = B·P_dec^{−1}·T_solve = m!·N·B^{(m−1)(σ−1)}`, the σ=1 cancellation is exact, the balance exponent `2/(2+(m−1)(1−σ))` is right, and the `σ=0, m` free limit really does give `L_N(1/2, 2+o(1))` once `m!` is charged. I re-derived all of these.

**What is wrong.** The derivation never checks that the balance point is *reachable*. The interior optimum `β* = 1/(2+(m−1)(1−σ))` satisfies the feasibility constraint `trials = m!N/B^{m−1} ≥ 1` (i.e. `β ≤ 1/(m−1)`) **iff `σ ≤ 2/(m−1)`**. For every `m ≥ 6` the record's gate is strictly looser than feasibility, by a band of width `1 − 4/(m−1)`:

```
 m   interior feasible iff σ ≤   gate admits σ <   permissive band
  6            2/5                     3/5              1/5
  8            2/7                     5/7              3/7
 10            2/9                     7/9              5/9
 12           2/11                    9/11             7/11
```

Concrete counterexample, the record's own kind of oracle: target-keyed meet-in-the-middle at `m = 8` has `T_solve = B^4`, i.e. `σ = 4/7 ≈ 0.571`. The gate says PASS (`0.571 < 5/7`) and prices it at `2β* = 2/5 = 0.4 < 1/2` — *beats rho*. But `β* = 1/5` means `B = N^{1/5}` and `B^{m−1} = N^{7/5} > N`, so fewer than one target is needed to collect `B` relations. Once the cap binds the achieved exponent is exactly `σ = 4/7 > 1/2` and MITM does **not** beat rho.

**This is refuted by its own sibling.** `IDEA-20260808-2ef5c8`, same batch, adds precisely the `trials ≥ 1` cap and derives `α_MITM = ceil(m/2)/(m−1) = 4/7` at `m = 8`. The two records give opposite verdicts on the same oracle. `2ef5c8` is the correct one.

**Substantive duplication.** Under `θ = (m−1)σ` the two cost models are *identical* (verified symbolically for all m ∈ [3,10), σ ∈ {0,0.1,…,1}: `θ−m+1 = (m−1)(σ−1)` in every cell). And 812554's admission inequality `σ < 1 − 2/(m−1)` is literally 2ef5c8's regime-(i) threshold `θ < m−3` (verified m = 4..12, exact match in every row), which 2ef5c8 in turn proves identical to `IDEA-20260803-fa9839`'s `d < (m−3)/4`. So this is one inequality in three parameterizations, filed three times. 812554's `novelty_screen` is marked `screened` and names `fa9839` as "nearest neighbour" without noticing that its "new" gate *is* fa9839's threshold.

**Also vacuous.** Prediction 3 — *"count of ECDLP proposals that name a sigma and clear σ < 1−2/(m−1); predicted: zero"* — is guaranteed by the novelty of the notation the record just introduced. It is not a check.

---

### `IDEA-20260808-02a046` — REFUTED: the correlation it targets is identically zero

**The claim.** *"the exact expression is the expectation of the product over j from 1 to k of (C_j / 2^a), where C_j is the number of distinct indices revealed in tree j — a quantity whose k-fold product **does NOT factor** because the C_j share the same q signatures."* Prediction 1's deliverable is the *sign of the cross-tree correlation*; the whole record's value is the gap `d` between the "union/independence step" and the exact value.

**The check.** HA-1 states the model the record adopts: *"the digest-to-index map is modelled as a random oracle, so the q revealed index sets are q independent uniform draws of k indices."* Under exactly that model the index matrix `(I_{i,j})_{i≤q, j≤k}` has i.i.d. uniform entries, so its **columns are independent**, so `C_1,…,C_k` are i.i.d., so

`E[∏_j C_j/2^a] = ∏_j E[C_j]/2^a = (1 − (1−2^{−a})^q)^k` exactly.

Sharing the same `q` signatures induces no dependence, because `q` is a fixed budget, not a random resource: each tree receives exactly `q` balls deterministically.

Monte Carlo, 200 000 trials per cell (the record's own toy control, run for it):

```
k=4  a=4  q=6 :  E[∏]=0.01062785  ∏E=0.01062744  ratio=1.000039  closed form=0.01062616
k=6  a=5  q=10:  E[∏]=0.00040465  ∏E=0.00040461  ratio=1.000090  closed form=0.00040517
k=8  a=4  q=12:  E[∏]=0.00713908  ∏E=0.00713582  ratio=1.000457  closed form=0.00712889
k=3  a=6  q=20:  E[∏]=0.01973312  ∏E=0.01973350  ratio=0.999981  closed form=0.01972396
k=10 a=3  q=5 :  E[∏]=0.00075237  ∏E=0.00075266  ratio=0.999613  closed form=0.00075180
```

Ratio 1.0000 in 5/5 cells within Monte Carlo error, and both agree with the closed form. `d = 0` by construction, and the record's `honest_prior_of_survival` of 0.4 for "d ≥ 1 bit at some parameter set" is unwarranted.

**Why its own controls miss it.** `nearby_object_control: "A parameter set with k = 1 has no cross-tree correlation at all, so the exact value must coincide with the independent product there."* That control passes for **every** k, so it cannot detect the error.

**Where the genuine slack actually lives.** In SLH-DSA the `q` signatures are spread over `2^h` FORS instances by the hypertree index, so the per-instance signature count `q_idx` is *random* (multinomial). Conditional on `q_idx` the `C_j` are still independent, but `E_{q_idx}[(1−(1−2^{−a})^{q_idx})^k] ≠ (1−(1−2^{−a})^{q/2^h})^k` by Jensen. That is a real, computable correlation — and `h` appears nowhere in the record, whose model has only `(k, a, q)`. A repaired record should track `(k, a, h, q)` and state the Jensen gap, not a within-instance cross-tree correlation that does not exist.

---

### `IDEA-20260808-51e40f` — SCOPE-INFLATED: the delta is measured against a baseline its own transform already beats

**The claim.** `sota_delta`: *"Against MAYO and SNOVA determined solves at q=16, ω=2: **up to 1.22N** bit-operation exponents versus semi-regular Groebner."* `dominated_by`: *"not dominated on TIME by any row I checked — the spec Groebner rows, exhaustive search, Crossbred and **BooleanSolve as recorded in KN-TECH-053**."*

**The arithmetic.** At `q = 16` (e = 4), with `N` the determined-system size:

| row | cost |
|---|---|
| Groebner over F₁₆ at ω=2, `binom(2N,N)^ω` | `2^{4N}` |
| exhaustive `q^N` | `2^{4N}` |
| **Weil descent + BooleanSolve (KN-TECH-053, `2^{0.792n}`, n = 4N)** | `2^{3.168N}` |
| Weil descent + polynomial method (`c = 0.6943`) | `2^{2.777N}` |

The record's 1.22N is `4 − 2.777`. But BooleanSolve is a **GF(2)** algorithm: applying it to a `q = 16` scheme requires exactly the Weil descent this record proposes, and once you do that it already delivers `4 − 3.168 = 0.83N`. The polynomial method's marginal contribution over a row the corpus already carries is `3.168 − 2.777 = **0.39N**`. The headline overstates the record's own contribution by a factor 3.1, and it does so by choosing the weaker baseline exactly where the number is biggest. The record is internally inconsistent about this: for MQOM's GF(2) rows it *correctly* benchmarks against BooleanSolve (`(0.792 − c)·N₂`), then switches baselines for MAYO/SNOVA.

**Two further corrections.**
1. The claim text writes *"At ω=2 that is e < 2/c; at ω=2.81 it is e < 2.81/c"*, but the stated crossover is `c·e < 2ω`, giving `e < 4/c` and `e < 5.62/c`. Both intermediate expressions are off by a factor 2. The *numbers* quoted (5.76 and 8.09) use the correct `2ω/c`, so this is a transcription slip, not a numerical error — but a reader who checks the intermediate step will conclude the record is wrong.
2. Prediction 2 asserts *"MQOM GF(2) WIN at both omega"*, i.e. a Groebner comparison at `e = 1`, while the record's own confounder forbids exactly that: *"over F₂ the field equations change d_reg substantially, and the record must not apply the large-field convention to a GF(2) row."*

---

### `IDEA-20260808-4f3ef4` — REFUTED / not decision-relevant, and unbound

**Structural.** No `goal_id`. It also carries none of `estimated_cost`, `recommended_priority`, `honest_prior_of_survival`, `interpretation_limits`, `heuristic_assumptions`, `discriminated_from`, `source_refs`, `why_not_a_renamed_known_approach`, or `target_complexity`, and its `dominated_by` names only rho on time+memory — no data/query axis, no BSGS row, no van Oorschot–Wiener interpolation.

**The claim.** *"replacing the right-half x(P₂+P₃) keys with deterministic independent uniform F_p keys … should remove the relation-finding correlation attributed to the x-oracle. This isolates the oracle/table-key association from the generic cost of building and probing a MITM table."* `sota_delta`: *"The only decision-changing quantity is whether the observed B-vs-C contrast survives a right-table null control."*

**(a) The motivating contrast is already adjudicated.** `DEC-20260808-6a7ac4` (`reject_scoped`): *"Y_A (exhaustive) and Y_B (x-oracle MITM) are EQUAL, EXACTLY, in every one of the 40 measured configurations … any significant delta against the random-predictor arm C measures only that 'structured search beats an uninformative null'."* `EV-ECDLP-65b004` records `Y_A_mean = Y_B_mean = 0.01212636`, `Y_C_mean = 0.00010671`. Since the oracle arm finds *exactly* the relations exhaustive search finds and no more, there is no "correlation attributed to the x-oracle" left to isolate, and no Arm D result can change that.

**(b) Arm D is the existing Arm C with the randomisation moved to the other side of an already-independent product.** I read `experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py`. Arm C builds the *true* right table `H[x(P₂+P₃)] = [(P₂,P₃)]` and replaces the left probe with a PRNG value in `F_p`. Arm D keeps the true probe `x(P₁)` and randomises the table keys. In both, probe ⟂ keys with one side uniform on `F_p`, so the expected hit count is the same in both arms:

```
p=101 b=0.4 (B=6) : E[hits] = 6·36/101  =  2.139   (C and D identical)
p=101 b=0.5 (B=10): E[hits] = 10·100/101=  9.901
p=103 b=0.4 (B=6) : E[hits] = 6·36/103  =  2.097
p=211 b=0.5 (B=14): E[hits] = 14·196/211= 13.005
```

and true relations ≈ 0 in both (Y_C = 1.07e-4). The forced value of the contrast is derivable before measuring it, which is the definition of an uninformative control.

**(c) It names the correct null and does not adopt it.** Confounder 1: *"Random-from-F_p keys have a different support distribution from x-coordinates of curve points … a future permutation-preserving control remains admissible."* Only about half of `F_p` are x-coordinates of points on E, so Arm D changes the key *support* by a factor ≈2 independent of any association. The matched null is a random **permutation of the true keys** among the right-half pairs: it preserves support, multiset and occupancy exactly and destroys only the association. That control is strictly cheaper and strictly better, and it is in the record's own confounder list.

**(d) The oracle does not escape the standing GGM closure, and the screen never checks it.** The `novelty_screen` lists the ECDLP ledger, BATCH-b3f591 red-team reports and EXP-SEMAEV artifacts — not `KN-FIND-002`, `KN-FIND-b7e091` or `KN-FIND-982fdf`. As implemented, the "x-oracle" is the test `x(P₁) ∈ {x(P₂+P₃)}`, i.e. `P₁ = ±(P₂+P₃)`: a group equality test up to sign, simulable with O(1) group operations. That is the same object as `KN-FIND-b7e091`'s incidence oracle ("which factor-base subsets sum to the target … simulable in O(m) group operations"), closed at exponent 1/2 by Shoup. This independently *explains* the exact equality `Y_A = Y_B`, and it means the arm-design question is downstream of a settled closure.

**(e) Intra-batch collision.** `IDEA-20260808-7c4e9d` (also no `goal_id`, also RQ-ECDLP-002, same session) opens: *"The true-null control experiment suggested by the red team ('Arm D: Random-from-F_p MITM') **has already been performed**: Arm C in EXP-SEMAEV-f48dd1 uses random x-coordinates from F_p in the MITM framework."* Neither record cites the other. On the arm's *side* 4f3ef4 is right and 7c4e9d is loose; on the *conclusion* 7c4e9d is right.

---

### `IDEA-20260808-2ef5c8` — PARTIAL-OVERLAP; text supplied

All of its algebra verified independently: `C_rel = m!c_D N B^{θ−m+1}`; interior optimum `B* = Θ(N^{1/(m+1−θ)})`, `T* = Θ(N^{2/(m+1−θ)})`, beats rho iff `θ < m−3`; the identity `θ < m−3 ⟺ θ/(m+1−θ) < (m−3)/4` is exact; the cap binds iff `θ > 2`; regime (ii) gives `α = θ/(m−1)`; `α_MITM = 2/3, 3/5, 4/7` at `m = 4, 6, 8`; the exhibited collision `(θ=2,m=6) = (θ=4,m=11) = 2/5` is real.

**Required `discriminated_from` addition** (against a sibling filed the same day):

> `IDEA-20260808-812554` states the identical cost model under the substitution `θ = (m−1)σ` (`C_rel = m!N B^{θ−m+1} = m!N B^{(m−1)(σ−1)}`), and its admission inequality `σ < 1 − 2/(m−1)` is exactly this record's regime-(i) threshold `θ < m−3`. The distinct content of the present record is the `trials ≥ 1` feasibility cap and the second regime `θ > 2`, which `812554` omits and which reverses `812554`'s verdict on meet-in-the-middle for every `m ≥ 6`.

**Title correction.** *"meet-in-the-middle misses it by exactly 1/2 in theta **at every arity**"* is false for odd `m`, where `θ_MITM = (m+1)/2` and the threshold is `(m−1)/2`, a miss of **1**:

```
m= 5: miss 1     m= 6: miss 1/2    m= 7: miss 1     m= 8: miss 1/2
m= 9: miss 1     m=10: miss 1/2    m=11: miss 1     m=12: miss 1/2
```

The record's own prediction table (`1/(m−1)` for odd m) is correct and contradicts its title.

**Cost-model honesty objection.** Confounder 2: *"one-relation-per-target costs a bounded factor ≤ 1.582, disclosed, **does not move theta**."* False in regime (ii). Under harvest-all the cap is `B ≤ (m!N)^{1/(m−1)}`; under one-relation-per-target the yield saturates at 1 and the cap is `B ≤ (m!N)^{1/m}`, giving `α = (θ+1)/m` instead of `θ/(m−1)` — at `m=8, θ=4` that is `5/8` versus `4/7`, an exponent change, not a factor 1.582. The two conventions diverge by `B^m/(m!N)`, a power of `N`, precisely in the region the record's headline occupies. (It happens not to bite for MITM specifically, whose enumeration produces all decompositions anyway, but the confounder is stated as a general disclaimer and is not one.)

---

### `IDEA-20260808-ee5d81` — PARTIAL-OVERLAP: the dominating row is missing from `dominated_by`

Steps (1)–(3) are correct: `σ̂_j ∘ σ_i ∈ End(E_com)` of degree `deg σ_i · deg σ_j`; it is scalar only if `σ_i, σ_j` are proportional (so, at equal response degree, only if `σ_i = σ_j` up to automorphism); OneEnd → EndRing → pushforward to `End(E_pk)`. `N_com ≤ 3·2^{e−1}` for a non-backtracking 2-isogeny walk of length `e` is right.

**The missing row.** The record's `dominated_by` says *"on the DATA axis the incumbent p^{1/3+o(1)} attack dominates completely, because it needs zero signatures. ROWS CHECKED: … KN-TECH-057's four full-cost rows."* Those are MITM/DG/vOW on the **whole** graph. The relevant row is MITM (or vOW) on the **commitment walk**: `E_0` is public, the commitment is a walk of length `e` from it, and `E_com` is published in every signature. Meeting in the middle at distance `e/2` recovers the commitment path in `~2^{e/2}` time from **one** signature, hence `End(E_com)` (from `End(E_0)` and the recovered path), hence `End(E_pk)` by the record's own step (3).

So in the *only* regime where the record's inequality binds — `2^{e/2}` below the `p^{1/3}` baseline — there is a same-cost attack that needs **zero** extra signatures, and it dominates the proposed attack on time (equal or better under full cost), memory (equal), and data (strictly). The birthday bound on signatures is therefore never the binding constraint.

**Exact text to add to `discriminated_from` / `dominated_by`:**

> DOMINATING ROW, previously unchecked: meet-in-the-middle (or vOW distinguished-point search) on the commitment walk itself. Since E_0 is public and the walk has length e, the commitment path is recoverable in ~2^{e/2} time from a SINGLE signature, yielding End(E_com) and hence End(E_pk) by step (3). Whenever 2^{e/2} is below the p^{1/3+o(1)} bare-curve baseline, this dominates the collision attack on the data axis at equal time. The correct deliverable is therefore the comparison 2^{e/2} versus the security level λ, not 2^{e/2} versus the claimed signing bound; a short commitment walk is a key-recovery weakness independent of signing volume.

Minor: the claim text quotes `q_max ~ p^{1/2}/3.5` (= `√(p/12)`) while prediction 1 uses the birthday constant `1.177·√N_com` (= `p^{1/2}/2.94`). Pick one.

---

## Required corrections on `NOVEL` records

**`46d7ef`.** (i) The pre-registered effect size is wrong. `2^8/8 = 32` = 5 bits is the saving for **one** length-256 Walsh–Hadamard transform; a convolution over `(GF(2)^8, XOR)` needs 2 or 3 transforms unless one operand is pre-stored in the transform domain: 2 transforms → 4.00 bits, 3 transforms → 3.42 bits. Prediction 3 (`≤ −5.0 bits if at least one key-addition step survives`) and the ≥5-bit falsification threshold are therefore unachievable under a standard accounting, and the record would record a *false negative* on a real gain. State the transform count. (ii) Held–Karp bound checks: `2^20·20 = 2^{24.32} < 2^25` ✓. (iii) Its `novelty_screen` names `KN-TECH-013` as the nearest technique entry; the actually-nearest entries — `KN-TECH-074` (division property / monomial prediction), `KN-TECH-076` (automated trail search, MILP/SAT/CP, "the reporting gap between an optimal trail and a real advantage"), `KN-TECH-079` (structural MITM, Demirci–Şelçuk tables) — are **absent from the dedup corpus** (see below) and must be screened before dispatch.

**`45af43`.** (i) Its only PLANTED positive control is *"a = 3b can occur"*. It cannot: `a = 3b ⇒ 4p = 12b² ⇒ p = 3b²`, contradicting `p ≡ 1 mod 3` prime. Likewise `b = 0 ⇒ p` square, `a = 0 ⇒ 3|p`, `a = ±b ⇒ p = a²`. Enumerated all 1124 primes `p ≡ 1 mod 3` below 20 000 and every representation `4p = a²+3b²`: **0** degenerate cases, **0** cells with fewer than six distinct traces. So the two-directional instrument check has no positive arm, and prediction 3's hedge ("except on an explicitly computable thin set … those degenerate cases must be reported separately") is vacuous. The honest statement is: *for every prime `p > 3` with `p ≡ 1 mod 3` the six traces are automatically distinct*, which strengthens the closure. (ii) The product identity `∏ N_i = #E(F_{p^6})` is exact (I re-derived it from `∏(1−ζ₆^i α)(1−ζ₆^{−i}ᾱ) = (1−α⁶)(1−ᾱ⁶)`), but it tests **one** point count. Tate's theorem for abelian varieties needs equal characteristic polynomials, i.e. matching counts over all extensions; matching `#(F_p)` is necessary, not sufficient, for the `n = 6` Weil-restriction decomposition the record labels `recall-uncertain`. Say so, or add `#(F_{p^k})` for `k = 2,3`.

**`8e13ff`.** The corpus has **58** `KN-FIND` records, not 57 (`ls knowledge/findings | wc -l` = 58; the dedup corpus exposes 57 — see below). Also needs a `discriminated_from` line against `IDEA-20260808-ea3b4f` ("The three GGM-simulability closures are being cited as if they closed RESOURCES"), which is its test T5 as a standalone record, filed the same day under the same goal.

**`b6ba7a`.** Claim (B)'s *"there are **exactly three** parameterizations a code-based complexity claim can live in"* is a closure with no argument, and its own confounder 3 concedes it ("If the 2026 line's complexity is stated in a parameter this analysis does not anticipate (for instance q, or the extension degree m alone)…"). Restate as "three that matter here". Claim (A) is the standard Canto Torres–Sendrier sub-linear-weight fact the record itself cites as `KN-LIT-fa9bc8`; the marginal content is the decision rule, and the priority should reflect that. Parameters verified exactly: `mt/n` = 24/109 (3488), 13/48 (4608), 52/209 (6688), 1547/6960 (6960), 13/64 (8192) — all five correct.

**`589c19`.** All figures verified against source records: `KN-TECH-057` does say *"the table is accessed only at distinguished points (amortized cost O(p^{−1/6}) per step, subconstant)"*, and `H-RSA-68884a` carries `c(1/3) = (2401/324)^{1/3} = 1.949616`, `β(1/3) = (7/12)^{1/3} = 0.835550`, `(2+θ)(8/9)^{1/3} = 2.2435`, `(8/9)^{1/3} = 0.961500`, and `c(1/3) − c(0) = 0.0266`; the 11.1× ratio is right. One overread: HA-7's `rigorous_ingredient` says *"KN-TECH-057 states exactly this"*. It does not — KN-TECH-057 applies the exemption to vOW in one instance; it never states the general two-sided criterion (fraction bounded below ⇒ charge `S^{1/3}`, fraction → 0 ⇒ `O(1)`), and it says nothing about the intermediate band. HA-7 is a *generalisation* of the source, correctly labelled heuristic elsewhere in the record but mis-attributed here.

**`71c2b2`** (exemplar-profile record — held to the `docs/target-result-profile.md` standard). Every number reproduced: the count law `c·T^{3/2}/√p` follows from a ternary form of determinant `p/4` with `c = 8π/3`; the stationarity conditions `u²(log u+1) = L/3` and `= L/2` are correct for `α = 1` and `α = 2/3`; the overhead coefficients `2√(α/6)` give `2/√6 = 0.8165` and `2/3 = 0.6667`; and `exp(0.1498·√(L log L))` = `2^{6.55}` at `L = 177.45` and `2^{9.87}` at `L = 354.89`. Three required additions:

1. **A missing numbered heuristic.** The step *"setting this to 1 gives … a per-attempt success probability Θ(1)"* is a first-moment-to-positive-probability inference: `E[N] = 1` does not give `P[N ≥ 1] = Θ(1)` without a concentration statement. This is distinct from HA-1 (a *mean over random E*, while the algorithm faces one fixed E) and from HA-2 (independence of *smoothness*, not of the *count*). Per the profile standard ("every heuristic explicit and numbered"), it needs to be HA-3, with the second moment as its rigorous ingredient.
2. **The random-model transfer does not obviously survive the successive-minima skew — and the batch already contains the counterexample.** `IDEA-20260808-f313da`, same goal, same question, same day, gives a *determinant identity* (not a heuristic): `p/4 ≤ N₁N₂N₃ ≤ p/2`, hence `u₁+u₂+u₃ = 3u + O(1/log B)`, so the smoothness parameters lie on a simplex; and by convexity of `u ↦ u log u` the multiplicity gain is **smaller** than naive on typical curves. That is the cheapest experiment that would expose the deviation from HA-2, it is rigorous where 71c2b2's HA-2 is not, and 71c2b2 does not cite it. These two must be adjudicated together before either is dispatched.
3. **"Cancels in the ratio" is false.** Confounder 1 says the `EV-PEC-857664` per-entry cost correction *"is common to both branches and cancels in the ratio"*; falsification condition 4 says a per-entry cost growing superlinearly in `B` invalidates the comparison. Both cannot hold: the two branches sit at **different** optima, `b_overshoot = √(2/3)·b_incumbent = 0.8165·b_incumbent`, so a `B`-dependent correction cannot cancel. Either establish that the correction is `B`-independent or drop the cancellation claim.

Everything else in this record meets the profile: memory inflation `K^{3/2}` charged, the van Oorschot–Wiener middle-memory interpolation named as the place it most likely loses, crypto-scale validation route (100 000 samples at `p = 5·2^248−1`), and the exponent explicitly not claimed to move.

**`dd4d30`.** Verified: FrodoKEM `n̄ = 8`, `n ∈ {640,976,1344}`, `q ∈ {2^15, 2^16}` — the recall is right. The rank-`n̄` embedding is legitimate (the vectors `(e_j, s_j, u_j)` for `j = 1..n̄` are `n̄` independent short vectors in the single lattice `{(x,y,z) : x ≡ Bz − Ay mod q}`). Its "dense sublattice condition" is the Kirchner–Fouque / Ducas–van Woerden DSD event; name it, and note that this is where the external-novelty risk sits.

**`6a2b50`.** Sound. One note it should carry: over `GF(2)` the "generic coordinates" argument has essentially no force — the Zariski-open set may have no `F_2`-rational points at all, so `≥8` random frames does not approximate genericity, it samples `GL_n(F_2)`. The record acknowledges the weakness; it should state that the negative outcome over `GF(2)` is therefore uninformative about genericity and only informative about `GL_n(F_2)`-frame sensitivity.

---

## Corpus defect: the dedup corpus is missing 29 of 89 `KN-TECH` records

The brief flags five *blanked titles*. The larger defect is that `KNOWLEDGE_BARRIERS.txt` contains **60** of the repo's **89** `KN-TECH` records, **57** of **58** `KN-FIND`, and **28** of **29** `KN-OPEN`. Twenty-nine technique records — 33% of the technique base — were entirely invisible to every generator in this round. Missing:

`KN-TECH-061..082` and `KN-TECH-14efa5, -1a5b7e, -276d30, -6c0e15, -797223, -9d21c4, -d1bc4f`; plus `KN-FIND-ff4a46` and `KN-OPEN-2c095b`.

Three of them bear directly on this slice:

- **`KN-TECH-1a5b7e` / `-6c0e15` / `-9d21c4` — three near-identical copies of *"Null sufficiency — deriving a contrast's forced value before measuring it, the three ways a control passes without being informative."*** That is precisely the technique that disposes of `4f3ef4` (and would have caught `02a046` and `90c7ab`). All three copies were invisible. The knowledge base also carries `KN-TECH-062` and `KN-TECH-080` with identical titles — the technique base has undeduplicated entries of its own.
- **`KN-TECH-074` / `-076` / `-079`** (division property & monomial prediction; automated MILP/SAT/CP trail search and its reporting gap; structural MITM / Demirci–Şelçuk) — the three nearest neighbours of `46d7ef`, whose entire selling point is "no MILP or CP solver anywhere in the loop".
- **`KN-TECH-082`** (hybrid attacks on LWE: guessing/MITM over sparse secrets, ring-structure acceleration) — the nearest neighbour of `dd4d30`.

Several records in this slice quote corpus sizes from the defective file ("57 KN-FIND, 61 KN-TECH, 28 KN-OPEN" in `5ee6b4`; "57 committed KN-FIND entries" in `8e13ff`). Those counts are wrong, and any `novelty_status: screened` asserted on the strength of `KNOWLEDGE_BARRIERS.txt` should be downgraded to `unverified` for the technique axis until the corpus is regenerated.

---

## What I actually checked

**Corpus files read:** `RESCREEN_BRIEF.md`; `KNOWLEDGE_BARRIERS.txt` (counted and diffed against the repo); `knowledge/techniques/KN-TECH-057.md` (full); `knowledge/findings/KN-FIND-002.md`, `-b7e091.md`, `-982fdf.md` (full); `KN-FIND-ff4a46.md` (head); `ledger/decisions/DEC-20260808-6a7ac4.yaml`; `ledger/evidence/EV-ECDLP-65b004.yaml` (both committed versions); `ledger/hypotheses/H-RSA-68884a.yaml` (targeted greps); `ledger/questions/RQ-INSTR-f8faa0.yaml`; `experiments/EXP-SEMAEV-f48dd1/specification.yaml` and `implementation/full_grid.py` (Arm B and Arm C bodies); `ledger/goals/GOAL-FIND-001.yaml` (status). All 18 slice records read in full; plus `IDEA-20260808-7c4e9d`, `-28361d`, `-f313da` read for intra-batch collision; all 126 `IDEA-20260808-*` titles + goal/question bindings enumerated.

**Computations run (outputs shown above, all reproducible):**
1. `git show --stat` on `a325d824` and `5de2db97` — 93-minute gap, 694/213, zero `runs/` paths, confirmed.
2. Leaf-scalar-multiset diff of `EV-ECDLP-65b004` across `b34e6c76d → 287f8eb7c` — the named matched null fires.
3. Enumeration of all Lagrangians of `(E×E)[N]` through `v = (P,[k]P)` for `N = 5,7,11,13,17`, all `k`, under the product polarisation `J⊕J` — `graph[k]` in pencil iff `1+k² ≡ 0`.
4. All `4p = a²+3b²` representations for the 1124 primes `p ≡ 1 mod 3` below 20 000 — zero degenerate cases, zero non-distinct trace sets.
5. `min/max` grid for `c1abd1`'s gap `g` — max over grid = 0.0.
6. Symbolic identity `θ−m+1 = (m−1)(σ−1)` (all `m ∈ [3,10)`, `σ` on a 0.1 grid) and `(m−1)(1−2/(m−1)) = m−3` (m = 4..12) — `2ef5c8` and `812554` are one model.
7. Feasibility table `β* ≤ 1/(m−1) ⟺ σ ≤ 2/(m−1)` with the m = 8, σ = 4/7 counterexample.
8. `θ_MITM − (m−1)/2` for m = 3..12 — miss is 1 for odd m, not 1/2.
9. Monte Carlo (200 000 trials × 5 cells) of `E[∏_j C_j/2^a]` vs `∏_j E[C_j/2^a]` and vs `(1−(1−2^{−a})^q)^k` — ratio 1.0000 throughout.
10. `log₂|B_τ|` at τ = 39/49/60; WHT bit-savings at 1/2/3 transforms; Held–Karp `2^20·20`.
11. `E[hits]` for Arm C and Arm D at all four frozen `(p,b)` cells.
12. Independent re-derivation of `71c2b2`'s two stationarity conditions, the coefficients `2√(α/6)`, and the `2^{6.55}` / `2^{9.87}` figures.
13. Knowledge-record inventory diff (repo vs dedup corpus).

**What I could NOT verify, and what would settle it.**
- **All external novelty.** Web unavailable. The most exposed: `46d7ef`'s recalled 2024 FFT/Walsh reorganisation of 6-round AES partial sums (if it exists, the marginal contribution shrinks to the schedule search); `51e40f`'s recalled Dinur constant `c = 0.6943` and its unread `c_mem` (the record correctly refuses to proceed without them); `6a2b50`'s Caminata–Gorla solving-degree ≤ regularity bound; `02a046`'s ITSR literature (my refutation is model-internal and does not depend on it); `dd4d30`'s DSD calibration range.
- **`589c19`'s `(O-A)` value β = 0.835550** is quoted from `H-RSA-68884a`'s closed forms, which I confirmed contain that exact figure but did not re-derive.
- **`ee5d81`'s deciding parameter `e`** (SQIsign commitment walk length) is not in the repo; the record correctly declines to assert it.
- **`b6ba7a`'s `C*`** cannot be computed without a stated `(α, β)` from an unread paper; the record's pre-registration is the right shape.
- **`71c2b2` vs `f313da`** should be adjudicated by a single session with both in front of it; I have not decided which survives, only that they conflict on the load-bearing heuristic and neither cites the other.

**Intra-batch overlaps found (none of these pairs cite each other):**
`5ee6b4 ↔ 28361d` (same entropy identity, same `(h/g)·τ` formula, contradictory corollaries) · `812554 ↔ 2ef5c8` (same cost model, contradictory verdicts on MITM) · `4f3ef4 ↔ 7c4e9d` (one proposes the arm the other says already exists) · `71c2b2 ↔ f313da` (one assumes short-vector independence, the other refutes it by a determinant identity) · `8e13ff ↔ ea3b4f` (T5 is ea3b4f's whole subject).
