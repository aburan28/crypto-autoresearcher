# Red-team report — BATCH-003 design and oracle

**Report id**: `RT-20260802-e5ebe9` · **Task**: `TASK-20260802-e5ebe9` (red-team)
**Batch**: `BATCH-003` · **Goal**: `GOAL-HQC-001` · **Question**: `RQ-HQC-001`
**Produced**: 2026-08-03 · **Branch**: `claude/goal-target-hqc-launch-vndegi`
**HEAD at review**: `e1b9388b5266240550f639683b592a5a1ea64646` (clean tree)

**Objects reviewed** (snapshot-committed, hashes recomputed by me from the
working tree and compared against both archive blocks — **all eight match**):

| commit | archive task | artifacts |
|---|---|---|
| `dcefbf6e` (parent `f73f290d`) | `TASK-20260803-d53ade` | `proposed_hypothesis.yaml`, `proposed_specification.yaml`, `feasibility_analysis.md`, `heuristics.md` |
| `47f7ad9b` (parent `6dc0040e`) | `TASK-20260803-2b5ab2` | `oracle.py`, `test_oracle.py`, `oracle_values.json`, `oracle_report.md` |

Both commits are reachable from `HEAD` with the declared parents; every
`path_sha256` in both `archive` blocks and both receipts reproduces. The
snapshot gate holds.

**Inference**: `requested_policy: review-adversarial`,
`resolved_model_id: claude-opus-5`, `fallback_used: true`,
`model_verified: false`, `independent_session: true`.
**This is an independent SESSION, not an independent MODEL.** No policy alias in
`orchestration/model-policies.yaml` resolves under this harness. **Nothing in
this report is admissible toward the `AGENTS.md` rule 13 closure quorum.**

**Scope**: I attack the DESIGN. **No security claim about HQC is made here in
either direction.** Claim tier: **toy**. `certificate.kind: none`.

---

## 0. Verdict, stated before the argument

> **FREEZE WITH REQUIRED AMENDMENTS. BATCH-004 may be authorised to spend
> compute once O1–O4 are addressed.**

I did not find a reason to refuse the contract, and I did find four things that
would make BATCH-004's number harder to interpret than it needs to be, two of
which can convert a *successful* run into an *uninterpretable* one through the
contract's own `ST-6` shutdown.

I tried hardest to break the arithmetic and **failed**. I independently
re-derived, from the primary transcription rather than from the producer's
numbers: `p̃` and `p*` from Props 6.1.1/6.1.2 at all four parameter sets
(`0.3397884 / 0.3479208 / 0.364929 / 0.376188` — exact agreement to every
printed digit); the closed-form relative variance `V(n_e,q,k)`; `T_prec`,
`s_90`, `T_stab` and `T_req` at thirteen cells; every quoted `SE`; the
Gaussian/orthogonality decoder model at five points; and the `dup = 2` cost of
`3.21e20` core-seconds from the producer's own cost model. **Every number
checked reproduced.** One objection I raised against the sizing was then
destroyed by my own computation and is **withdrawn** in §5.

The remaining objections are about **what the numbers mean and what the
protocol would and would not see** — which is where BATCH-002's A19 retarget
failed, and which is where this design fails too, in four places.

**Would a null result be interpretable?** **Partly, and less than the design
claims.** A null at PS-R1/R3/R5 is interpretable as the absence of a
*weight-mediated* dependence of the modeled size at those parameters. It is
**not** interpretable as the absence of dependence, because the design's only
wash-out guard (`γ̂ < 0.95`) monitors a quantity that is **constant in the
reduced knob by construction** and will pass at every reduced set regardless of
whether the reduction destroyed the effect. See O3 — this is the single most
important finding in this report.

---

## 1. Objections, ranked by severity

Each carries the cheapest control that resolves it. "Cheapest" means: the
control I would actually run, with its cost.

---

### O1 — HIGH. The "two-runged ladder" is an artifact of a self-imposed constraint. A walkable `dup = 2` rung exists at ~`2.0e4` core-seconds, and the design has foreclosed it.

**The claim under attack.** `feasibility_analysis.md` §6.3: *"There is no
ladder. … Any design that promises to 'walk the multiplicity down from HQC's
setting' is promising something the arithmetic forbids."* Restated in the frozen
contract (`independent_variables.duplication_multiplicity_dup`: *"the ladder has
NO intermediate rung: dup = 2 costs 3.2e20 core-seconds"*), in `OPEN-2`, in
`HEUR-HQC-6`'s obstructions (*"bridges a gap that cannot be walked, only
jumped"*), and — **without its qualifier** — in the Coordinator's receipt
(*"CRITICALLY, THE LADDER HAS EXACTLY TWO RUNGS … there is NO WALKABLE PATH from
dup=1 to HQC's dup in {3,5}"*).

**What is actually true.** §6.3's own header states the constraint: *"`p*`,
`n_e`, `m` and the `omega/omega_r` ratio held at each level's own values"*.
Under that constraint the arithmetic is correct and I reproduce it exactly
(`T_req = 1.473e24`, `C_trial = 2.18e-4 s`, cost `3.21e20` core-s). **The claim
is a statement about the constraint, not about the arithmetic.**

**The counter-design.** Relax `p*` alone — the design already spans
`p* ∈ [0.3398, 0.3762]` across its own levels — and hold everything the campaign
actually cares about:

| | PS-R1 (design) | **PS-R2 (proposed)** | PS-A (design) |
|---|---|---|---|
| `dup` | 1 | **2** | 3 |
| `n` | 5923 | **11779** | 17669 |
| `n_e` | 46 | **46** | 46 |
| `m = δ_e+1` | **16** | **16** | 16 |
| `ω, ω_r = ω_e` | 39, 44 | **62, 70** | 66, 75 |
| `p*` exact (Prop 6.1.2) | 0.347921 | **0.388705** | 0.339788 |
| `q` (producer's own model) | 0.2306 | **0.21932** | ~5e-4 |
| `m/λ` | 1.508 | **1.586** | 621–1264 |
| `T_req` at `k = m = 16` | 2.915e7 | **8.164e7** | 3.4e41 |
| `C_trial` (producer's cost model) | 1.17e-4 s | **2.456e-4 s** | 3.35e-4 s |
| **cost at `T_req`** | 3.4e3 core-s | **2.005e4 core-s** | — |
| `SE(log2 Â_16)` at `T = 1e8` | 0.0321 | **0.0404** | *k=16 unreachable* |

Derivations: `p* = 0.388705` from Props 6.1.1/6.1.2 with `n = 11779` (verified
prime with 2 primitive, and it is the design's own `dup=2` ring), `ω = 62`,
`ω_r = ω_e = 70` at HQC-1's own `ω_r/ω` ratio. `q = 0.21932` from the producer's
own Gaussian/orthogonality model at `dup = 2`. `T_req` from the producer's own
`max(T_prec, T_stab)` with `s_90 = 26`. `C_trial` from the producer's own §9.2
formula with `W = ceil(11779/64) = 185`.

**Cost: `2.0e4` core-seconds — 36 % of the mandatory `5.58e4` budget**, fundable
from the optional Stage D (`6.7e3`, already first-to-cut under `ST-3`) plus a
modest trim, or simply added (the campaign's stated envelope is "roughly 2
batches").

**Why this matters more than the cost.** `HEUR-HQC-6` (inner-multiplicity
transfer) is the heuristic the design says can only be *jumped*, and its only
test (`F6`) is a **within-`PS-A` consistency check at `k ≤ 3`** — i.e. a test of
the bridge *formula* at `dup = 3`, not a test of *transfer across `dup`* at all.
PS-R2 gives a **matched-`n_e`, matched-`m = 16`, matched-rarity
(`1.586` vs `1.508`), two-point contrast on the one axis the design reduces, at
the load-bearing order.** That is the difference between a heuristic with no
matched test and a heuristic with a direct one.

**Against the design's own stated objection.** §6.1 refuses to raise `p*`
because it *"pushes the channel toward `p* = 1/2`, where `e'` approaches
uniform, `γ → 1`, and the dependence being measured vanishes by
construction."* Applied to PS-R2 that objection does not survive its own
metrics: PS-R2's `q = 0.219` is **lower** than PS-R1's `0.231` and far below
`PS-R5`'s **accepted** `q = 0.473`; `p* = 0.3887` is `0.016` above HQC-5's own
`0.3725`, a 4.3 % relative move inside a family the design already spans by
9.6 %; and `γ` is a function of the fixed-weight structure and `τ`, not of `p*`
directly, so `D1` remains a live check rather than a foregone one. The honest
cost of PS-R2 is that `ω/√n = 0.571` against HQC-1's `0.497` — the A7 regime is
preserved to 15 % rather than PS-R1's 2 %, and that should be stated, not hidden.

**Also wrong in the forward guidance.** `OPEN-2`'s successor says a genuine test
*"needs `dup = 2` at a much smaller `n_e`, breaking order-matching to buy
rarity"*. At fixed `q`, **smaller `n_e` raises `m/λ` and makes it more
expensive**, not less; the coherent reading (shrink `m` too) is exactly the move
`EV-HQC-6fd5b1` O-6 forbids. The cheap rung is in the opposite direction from
the one the design points at.

> **Cheapest resolving control.** Add PS-R2 as specified above (or, at minimum,
> restate the two-rung claim with its constraint attached wherever it appears —
> `feasibility_analysis.md` §6.3, `OPEN-2`, `HEUR-HQC-6`, the frozen contract's
> `independent_variables`, and the `d53ade` receipt). **Cost of the restatement:
> zero. Cost of the rung: `2.0e4` core-seconds.** I recommend the rung: it
> converts the design's own declared unwalkable gap into a measured two-point
> contrast for 36 % of the budget.

---

### O2 — HIGH. Exchangeability is removed from the estimand and silently re-enters in the falsification conditions, where it can trigger `ST-6` and forbid all downstream evaluation.

The design's central repair (`§1.2`, `estimated_statistic.correction_to_the_inherited_derivation`,
`OPEN-4`) is correct and I verified it: Lemma F1 (Jordan/Bonferroni) is
distribution-free, `E[C(S,k)] = Σ_{|J|=k} μ^{(J)}` holds by linearity alone, and
`mubarhat_k` is unbiased for `mubar_k` with no exchangeability. **That part
survives.**

It does not survive downstream. Two places:

**(a) The variance identity is mislabelled.** `HEUR-HQC-2` "Rigorous half" item 1
asserts that `Var(W) = n_e Var(W_1) + n_e(n_e−1) Cov(W_1,W_2)` is *"an exact
identity under equal marginals (Lemma L1')"*. It is not. Under equal marginals
the identity is

```
Var(ΣW_j) = n_e Var(W_1) + n_e(n_e−1) · C̄ ,   C̄ = mean of Cov(W_i,W_j) over ordered pairs i≠j
```

Writing `Cov(W_1,W_2)` in place of `C̄` requires **all pairwise covariances to be
equal** — pair-exchangeability, precisely what §1.2 proved is *not* established.
The estimate itself is fine (`γ̂` is built from `Var(w(ẽ))`, so it measures `C̄`),
but the frozen contract's secondary metric `corr_W_hat` is *defined* as
`Cov(W_1,W_2)`, and `F2b` compares `β̂` against a prediction built from it. An
analyst who reads the label and estimates the adjacent pair — the natural
reading, and the one with the largest deviation under a translation-invariant
law — is comparing a different object.

**(b) The closure explicitly requires exchangeability, and `F2a`/`F2b` inherit
it.** `HEUR-HQC-2`'s formal statement: *"If in addition `(eps_j)_j` is
**exchangeable** and jointly log-normal to the order retained, then …
`log A_k = C(k,2)·β`."* Under only translation invariance,
`Cov(eps_i,eps_j) = c(|i−j|)` and

```
log A_k = log( (1/C(n_e,k)) Σ_J exp( Σ_{pairs in J} c ) )  ≥  C(k,2)·c̄     (Jensen)
```

so covariance heterogeneity biases `log A_k` **upward** relative to the
homogeneous prediction, and the excess **grows with `k`** because larger subsets
sample more distant pairs. Therefore:

- **`F2a`** (*"`log Âhat_k / C(k,2)` varies by more than a factor 2 across
  `k`"*) can fire from heterogeneity alone;
- **`F2b`** (factor-2 magnitude test against the homogeneous prediction) can
  fire from heterogeneity alone;
- **either firing triggers `ST-6`**, which *"FORBIDS every downstream evaluation
  at HQC's parameters"*.

**This is not hypothetical.** The sibling oracle *demonstrates* the
heterogeneity in an HQC-shaped ring: `μ_2({0,1}) = 1482597/3920000` against
`μ_2({0,2}) = 100175981/264600000` at `n_e = 4`, with the count of distinct
`μ_2` values equal to the cyclic-orbit count exactly. The design has a route to
a **spurious self-shutdown** on structure it has itself proved is present.

> **Cheapest resolving control.** The ingredients are already budgeted. The
> contract already measures `mu2_by_block_distance` (`muhat_2^(d)`, `d = 1…n_e−1`)
> as a required per-run artifact. Amend the analysis to (i) rename
> `corr_W_hat` to the **average** covariance/correlation with the definition
> written out, (ii) compute the heterogeneity-corrected prediction
> `log A_k = log( avg_J exp(Σ_{pairs∈J} ĉ(d)) )` from the measured `ĉ(d)` by
> dynamic programming over gap multisets (`n_e ≤ 90`, `k ≤ 32`: milliseconds),
> and (iii) gate `F2a`/`F2b`/`ST-6` on the **corrected** prediction, reporting
> both. **Cost: analysis only, zero compute.**

---

### O3 — HIGH. The wash-out hole is named, not closed. `γ̂` is not the destroy parameter for the quantity under test, and under a null the mechanism discriminator is inoperative.

This is the duty I was told is the single most valuable thing to check, so I
state the answer without hedging: **the three guards close the hole for the
weight-mediated mechanism and leave it open for the other one.**

**Guard-by-guard.**

1. **"Hold `p*` at each level's published value."** Real, and it does prevent the
   crude `p* → 1/2` failure. But the design's own `§12.2` concedes *"`p* → 1/2`
   **or** `q → 1/2`"* is the hazard, and PS-R5 sits at `q ≈ 0.473` — inside the
   hazard by the design's own criterion, guarded only by (2).

2. **The `γ̂ < 0.95` gate. This is the hole.** `γ̂ = Var(w(ẽ))/(N p̂(1−p̂))` is a
   property of **`ẽ` alone**. `ẽ`'s law is fixed by `(n, ω, ω_r, ω_e, N)`; it
   **does not depend on `dup` at all** — `dup` changes only the block partition
   and the decoder. So `γ̂` at the reduced sets measures whether the *ring-level*
   under-dispersion survived, which it trivially does, and it will report
   `0.61–0.74` and pass. **`γ̂` cannot detect whether the reduction destroyed the
   propagation of that structure into the `F_j`, which is the entire question.**
   The design's own numbers say the propagation *is* attenuated by construction:
   `η` falls from `50.7` at `dup = 3` to `12.3` at `dup = 1` (its §7 table,
   "factor 4.4"), and `β ∝ η²`, so the induced effect drops ~19×. A `γ̂` in band
   certifies nothing about that.

3. **"A null at a washed-out set is uninformative, not evidence for A17."**
   Correct as a rule and correctly pre-registered — but it is **keyed to
   `uninformative_null_condition: γ̂ > 0.95`**, which by (2) will never fire.
   A pre-registered rule whose trigger cannot fire is a rule that names the
   hazard without guarding it.

**The mechanism that is actually at risk.** `EV-HQC-6fd5b1` O-6 names two
mechanisms of opposite sign. The design models the **negative, weight-mediated**
one and is over-powered for it (73σ at PS-R1). The **positive common-mode `M+`**
one is positional — it is `HEUR-HQC-2` clause (a), which the design states is
*"not proved"* — and it is exactly the mechanism a `dup 3 → 1` reduction most
plausibly destroys, because folding `dup` copies before the Hadamard transform
is where cross-copy positional structure enters. `CTRL-WBP` is the pre-registered
discriminator for it, **and `CTRL-WBP` is inoperative under a null**: permuting
within blocks when there is no signal returns no signal, whichever mechanism was
absent. So a null carries no information about whether `M+` was destroyed.

**The inventor-protocol inversion.** §3 of `docs/inventor-protocol.md` asks what
the measured quantity *should do* as the parameter meant to destroy it
increases. The design **has** such a parameter — dilution `τ`, arms PS-D2/PS-D4
— and it is **optional and first to be cut** (`ST-3`, `HEUR-HQC-4` validation
plan: *"Optional; cut first"*). The only decay check in the design is the one it
plans to drop.

> **Cheapest resolving control — the most valuable missing arm in this design.**
> Add a **pre-registered injected-dependence recovery control** (`CTRL-INJ`) at
> PS-R1 and PS-R5: draw `ẽ` from a *known* dependent ensemble of matched shape —
> the simplest is a two-component mixture over `p* ± δ` chosen so that the
> analytic `log2 A_16` equals the modeled `−2.34` bits — push it through the
> **identical** decoder and estimator, and require the measured `log2 Â_16` to
> recover the injected value within `3 SE`. If the pipeline cannot recover a
> **known** dependence of the modeled size at `k = m`, the null is uninformative
> **by measurement** rather than by an untriggerable `γ̂` rule. This is
> decode-only, the same cost class as `NULL-M` (~`1e3` core-s). **Additionally:
> promote `stage_D_dilution` out of `ST-3`'s first-cut slot** — the destroy
> parameter is not the arm to cut.

---

### O4 — MEDIUM-HIGH. `HEUR-HQC-4`'s formal statement has the destroy-parameter direction backwards, and the error can trigger the wrong `F4` branch and hence `ST-6`.

`HEUR-HQC-4` formal statement: *"`|Corr(W_i,W_j)|`, and therefore `|log A_k|` at
fixed `k`, is **non-increasing in `tau = N/n`**; HQC's own `tau ≈ 1` … is the
**maximally budget-constrained** member of the family."*

Those two clauses contradict each other, and the first is wrong. For the
fixed-weight component, with two disjoint blocks of size `n_2` in a
weight-`W`-on-`n` vector,

```
Cov(W_i,W_j) = −n_2² p(1−p)/(n−1) ,  Var(W_i) = n_2 p(1−p)(n−n_2)/(n−1)
⇒ Corr = −n_2/(n−n_2) = −τ/(n_e−1) + O(1/n)
```

which is consistent with the design's own `Corr = (γ−1)/(n_e−1)` and
`γ ≈ 1−τ` (I checked both reduce to `−1/(n_e−1)` at `τ → 1`), and which is
manifestly **increasing** in magnitude with `τ`. The statement should read
**non-decreasing in `τ`**.

The rest of the package has it right: `F4` tests non-increase *along decreasing
`τ`*, and the frozen contract's `independent_variables.dilution_tau` says
*"`|log2 A_k|` must be non-increasing as `tau` falls"* — the opposite of the
heuristic's formal statement. So the **frozen contract and the heuristic
document contradict each other on the direction of the design's only destroy
parameter**, and the heuristic is the falsifiable object.

Consequence if unfixed: an analysis run against the formal statement as written
reads a **correct** result as an `F4` firing, enters `F4`'s pre-registered
branch structure, and — down one branch — refutes `HEUR-HQC-2` clause (a),
which triggers `ST-6` and forbids all downstream evaluation. A wording error
that can shut down a successfully executed batch.

> **Cheapest resolving control.** One-line correction to `HEUR-HQC-4`'s formal
> statement (`non-increasing` → `non-decreasing` in `τ`), pinned by writing the
> exact identity `Corr_fixed-weight = −τ/(n_e−1)` into the heuristic and adding
> it to the frozen regression fixture. **Cost: zero.**

---

### O5 — MEDIUM. The "3.4× margin" at PS-R1 is a **13 % margin in `q̂`**, and `T_req` is discontinuous in `q̂`.

`T_req(46, q, 16)` is an extremely steep and **non-monotone** function of `q`,
because `s_90` is an integer that steps. My independent grid at `T = 1e8`:

| `q̂` | 0.190 | 0.198 | 0.202 | 0.210 | 0.218 | **0.222** | 0.2306 | 0.246 |
|---|---|---|---|---|---|---|---|---|
| `s_90` | 25 | 25 | 25 | 25 | 25 | **26** | 26 | 26 |
| `T_req` | 3.16e8 | 1.37e8 | 9.18e7 | 4.24e7 | 2.04e7 | **6.35e7** | 2.92e7 | 7.94e6 |
| reachable | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

So: `k = 16` at PS-R1 is reachable iff `q̂ ≳ 0.200`, a **13 % margin in `q̂`**,
not a 3.4× margin in anything robust; and inside the reachable region the
"margin" swings between 1.57× and 3.4× across the `s_90 = 25 → 26` step at
`q̂ ≈ 0.220`. The design states the 3.4× figure four times and never states the
`q̂` threshold.

This matters because `q` at PS-R1 is **modeled, not measured**, and the model's
validation points are all at `dup ∈ {3,5}` (SPEC Table 11); PS-R1 is at
`dup = 1`, where the model is extrapolated and the rigorous bracket is ~8 bits
wide. The known bias direction (model low, true `q` higher) is favourable, but
it is validated only where the design does not sit.

`ST-4` handles the failure gracefully (report `k = 16` NOT REACHED, do not raise
`p*`) — which is the right rule and I am not attacking it. I am attacking the
absence of a **budgeted escalation** before that fallback fires: at `q̂ = 0.198`,
`T = 3.2e8` would still reach `k = 16` for `3.7e4` core-s, an affordable
addition, and the difference between "the campaign's one order-matched
measurement happened" and "it did not".

> **Cheapest resolving control.** Restate PS-R1 reachability as a **`q̂`
> threshold** (`q̂ ≥ 0.202` at `T = 1e8`) rather than a `T` margin, and
> pre-register an escalation: if `q̂ ∈ [0.190, 0.207]`, raise PS-R1's `T` to
> `T_req(q̂)` capped at `3.2e8` (`3.7e4` core-s) before invoking `ST-4`'s NOT
> REACHED. Stage A already measures `q̂` to `±0.0002`. **Cost: zero unless
> triggered.**

---

### O6 — MEDIUM. `CTRL-ORACLE` should be mandatory, and its tie convention is unpinned. The oracle certifies the same object; three tie policies are in play and none is named in the cross-check.

**On the "same object" question, I found nothing wrong, and I checked hard.**
The oracle's C2 is `μ_k := (1/C(n_e,k)) Σ_{|J|=k} μ_k(J) = E[C(S,k)]/C(n_e,k)`;
the design's estimand is `mubar_k = E[C(S,k)]/C(n_e,k)`. **Identical.** Both use
distinct indices (the oracle *raises* on a repeat, and quantifies the bug: mutant
M1 returns ×2.898 on a perfectly independent ensemble and ×9.561 on a negatively
dependent one, reading as positive dependence in both). Both are unconditional
(oracle C3; the design conditions on nothing). The identity
`Σ_J μ_k(J) = E[C(S,k)]` is verified from two code paths for every
configuration. **No index-set, conditioning, or distinct-vs-repeated gap
exists.** This duty found a clean instrument.

**Two riders.**

*(a) Tie convention.* Three conventions are in play: the oracle's default is
A13's **randomised split** (`φ` rational, C4); the oracle also implements
**ties-count-as-failure** (deterministic, pessimistic); the frozen contract
specifies **"take the maximum, broken by lowest index"** — and since index 0 is
the zero codeword, that breaks ties toward **success** (deterministic,
optimistic). All three differ on any configuration with a non-zero tie rate.
`CTRL-ORACLE` names none of them.

*(b) Scale.* On the faithful ring the oracle reaches `N = 18`, `n_e = 4`,
`m ≤ 4` against HQC-1's `17 664 / 46 / 16` — it does **not** validate the
estimator on the faithful ensemble at the protocol's order. **But this is less
damaging than it sounds, and the design deserves the credit**: the estimator
factors entirely through the histogram of `S`, so what needs validating at
`k = 16…30` is the `C(S,k)/C(n_e,k)` arithmetic, and Route B validates that at
`n_e = 46, m = 16` (3 ms) and `n_e = 100, m = 30`. What the ring reach is needed
for is the **sampler + decoder** chain, and that is covered by `CTRL-DEC`,
`CTRL-REPLAY`, `D2`, `D3` and — **only at PS-A** — `D4`.

That last clause is the real gap: **`D4`, the strongest sampler check, compares
against a published (T) measurement that exists only at PS-A — the one arm that
cannot reach `k = m`.** At PS-R1/R3/R5, where `k = m` is measured, the sampler
has only invariant checks (weights, support cap, replay), none of which is
distributional. The one available end-to-end distributional check at the reduced
arms is the oracle itself, and the contract marks it **optional**.

The reason for optionality has expired: the sibling was written concurrently and
has now delivered, and it demonstrably computes the ring exactly at `n = 17, 19`
and has already shown a direct ring sampler converging to the exact value
(`z = +0.358` at 200 000 samples).

> **Cheapest resolving control.** Promote `CTRL-ORACLE` from optional to
> **mandatory on the ring configuration** (`R1`/`R4`, `n = 17`/`19`), require the
> experiment's own driver — not the oracle's sampler — to reproduce the oracle's
> exact `μ_k` within its stated tolerance, and **pin the tie policy** in both:
> either implement the contract's lowest-index rule in the oracle's `BlockModel`
> (it is a function of content, hence `φ ∈ {0,1}` — trivial), or require the
> cross-check on a configuration whose exact tie rate the oracle reports as
> zero. **Cost: seconds of compute plus one `BlockModel` variant.**

---

### O7 — MEDIUM. `A1` — the independence of the five fixed-weight vectors — is guaranteed "by construction" and never measured, and no detector can catch its failure.

The five drift detectors are genuinely strong against drift to (M): `D2` (exact
weights every trial), `D3` (support cap `2ωω_r + ω_e`, violated w.p. ~1 on (M)),
`D5` (bit-identity replay through an independent dense-multiplication code
path), `D1` (`γ̂` band) and `D4` (Table 10 tails at PS-A). **I looked for a
Bernoulli-ization or a coordinate-independent path into a (T) arm and found
none**: the sampler is Floyd/partial-Fisher-Yates fixed-weight index sampling
with no Bernoulli step, and the (M) generator lives in a separate module used
only by `NULL-M`.

What none of them tests is `A1`. The contract derives all five vectors from
*"five disjoint counter subspaces of the same key"*. If those subspaces overlap
— a one-line indexing bug — then e.g. `x` and `r_2` are correlated,
`e' = x·r_2 − r_1·y + e` acquires structure that is **not** the structure under
test, and every one of `D2`, `D3`, `D5` still passes (weights are exact, the
support cap holds, replay is bit-identical because the bug is deterministic and
reproduced by both paths). `D1` might or might not catch it. The result would be
a genuine `(T)`-versus-`CTRL-BS` excess — **an artifact wearing exactly the
shape of the finding the campaign is looking for.**

> **Cheapest resolving control.** Add a Stage-A `A1` check with an exact
> reference: the overlap `|supp(x) ∩ supp(r_2)|` is **hypergeometric** under
> `A1`, with mean `ωω_r/n` and an exactly computable law; test the empirical
> overlap distribution for all five pairs against it, and separately assert in
> code that the five counter ranges are provably disjoint and record the ranges
> in the manifest. **Cost: a by-product of Stage A, zero extra sampling.**

---

### O8 — MEDIUM. `CTRL-BS`'s offset condition is stated on the wrong quantity, and its "`E[Â_k] = 1` EXACTLY" is an overstatement (though a harmless one — I checked the size).

*(a) The offset condition is wrong as written.* `CTRL-BS` takes block `j`'s
indicator from true trial `(t + j·o_j) mod T` with *"offsets `o_j` pairwise
distinct and coprime to `T`"*. The property the null needs is that for every
`J`, the `|J|` trial indices are **distinct**, which requires the **products
`j·o_j` to be pairwise distinct mod `T`** — not the `o_j`. Distinct `o_j` does
not give it (`j=1, o=6` and `j=2, o=3` both give shift 6). If two blocks share a
shift they are **perfectly coupled** in the null, `CTRL-BS` shows an excess,
`INV-NULL(a)` fires, and the cell is (correctly, but expensively) discarded as
`invalid_measurement`. A wasted batch, not a false positive — still worth
one line.

*(b) The exactness claim.* `Â_k = mubarhat_k / q̂^k` is a **ratio**; only the
numerator is unbiased. The contract itself says so elsewhere (*"`Ahat_k` is a
ratio and therefore mildly biased"*), then asserts in the `CTRL-BS` row that
*"`E[Ahat_k] = 1` **EXACTLY**, for every `k`, by construction"*. **I quantified
it rather than just objecting**: at PS-R1, `k = 16`, `T = 1e8`, the numerator's
log-bias is `V/(2T) = 2.5e-4` nats `= 3.6e-4` bits and the denominator's is
`≈ 6e-9` bits, against `3 SE_null = 0.096` bits. **The bias is 270× below the
`INV-NULL` threshold and is not load-bearing.** This half is a wording
correction, not a defect, and I say so rather than inflating it.

> **Cheapest resolving control.** Restate the offset condition as *"shifts `c_j`,
> `j = 0…n_e−1`, pairwise distinct mod `T`"* and assert it in code; replace
> *"`E[Â_k] = 1` exactly"* with *"`E[mubarhat_k^{BS}] = q^k` exactly; the ratio
> bias is `O(V/T)` and is `3.6e-4` bits at the PS-R1 design point". **Cost: zero.**

---

### O9 — LOW-MEDIUM. The `proof_search_map`'s headline variance gain is overstated by a factor `3.1e6`.

`proposed_hypothesis.yaml`, `constructive_transforms[0].predicted_gain`:
*"A factor `C(n_e,k)` in variance relative to any single-index-set estimator
(about `1e12` at `n_e = 46, k = 16`)."*

`C(46,16) = 9.91e11`, so the arithmetic of the binomial is right — but the
variance gain is **not** `C(n_e,k)`, because the `C(n_e,k)` subset indicators are
massively overlapping and positively correlated, so `Var(ΣX_J) ≠ C(n_e,k)Var(X_J)`.
Computed at the PS-R1 design point:

```
single-subset relative variance  (1−μ_16)/μ_16 = 1.564e10      (μ_16 = q^16 = 6.39e-11)
mubar_16 estimator               V             = 4.944e4
ACTUAL gain                                    = 3.164e5       (claimed ~1e12; overstated 3.13e6×)
```

Not load-bearing — every `T_req` in the package was computed from `V`, correctly
— but it is the stated justification for the design's principal representation
transform, it sits in a record about to be frozen as `H-HQC-18d1b4`, and it is
exactly the kind of number that becomes a citation. `3.2e5` is still a large and
genuine gain and should simply replace it.

> **Cheapest resolving control.** Replace `~1e12` with the computed `3.16e5` at
> the stated design point, with the one-line reason (`overlapping subsets`).
> **Cost: zero.**

---

### O10 — LOW-MEDIUM. The rarity gap is quoted with five different values across the package, and one of them (`3900`) is not derivable from any stated convention.

| where | figure | `q` convention |
|---|---|---|
| `feasibility` §5 table | `m/λ = 621` (HQC-1) | `q = p_i` (Prop 6.1.4 bound) |
| implied by contract's `PS-A.q_for_sizing` | `696` | Table 11 observed |
| `feasibility` §7, §12.1; `heuristics` `HEUR-HQC-3`; `d53ade` receipt | `1264`, "factor ~840", "2.9 decades" | Gaussian model `q` |
| frozen contract `scale_relevance` | *"rarity ratio up to **3900** times smaller"* | **none I can reconstruct** |

I recomputed all three conventions (`HQC-1`: model `1263.9`, bound `622.5`,
observed `696.6`; `HQC-3`: `10184 / 5469 / 6557`; `HQC-5`: `1396 / 854 / 966`)
and could not produce `3900` from any pairing with any reduced set. It is not a
fabrication — the number is small relative to defensible alternatives and the
package's own headline (`840`) is the *more* pessimistic model-`q` figure, which
is the conservative direction for a threat statement. But `3900` appears in the
document that is about to become the **frozen contract**, unsourced.

> **Cheapest resolving control.** Fix one `q` convention for rarity (I recommend
> the model `q`, since it is the one the `840`/`2.9-decade` headline uses),
> state it at every point of use, and derive or strike `3900`. **Cost: zero.**

---

### O11 — LOW-MEDIUM. `TASK-20260802-1758c3` (the ledger archive of this batch) depends on a permanently-blocked task and, by the queue's own eligibility rule, can never run.

`TASK-20260802-1758c3.depends_on = ["TASK-20260802-506c73", "TASK-20260802-addcdd",
"TASK-20260802-e5ebe9"]`. `TASK-20260802-506c73` carries the amendment *"Retained,
claiming the two FAILED producers. **It can never complete and is expected to
stay blocked.**"* `AGENTS.md` dynamic dispatch: *"A task becomes eligible only
after every dependency has a `completed` receipt."*

The two **review** cards (`addcdd`, `e5ebe9`) were correctly amended to repoint
at `TASK-20260803-2b5ab2` and `TASK-20260803-d53ade`. The **ledger archive** card
was not. Retaining `506c73` as a historical record is right; naming it as a
dependency of a task that must run is not.

> **Cheapest resolving control.** One amendment to `TASK-20260802-1758c3`,
> mirroring the two already made: `depends_on` → `["TASK-20260803-2b5ab2",
> "TASK-20260803-d53ade", "TASK-20260802-addcdd", "TASK-20260802-e5ebe9"]`, with
> the reason recorded. `506c73` keeps its terminal state. **Cost: zero.**

---

### O12 — LOW. The Coordinator's independence hedge is correct and **under-reports** what the oracle established; and one supporting sentence omits that the clean case is a ring HQC's own rule forbids.

The hedge under review (`d53ade` receipt): *"THE COORDINATOR IS NOT CLAIMING
INDEPENDENT CONVERGENCE — both tasks read the same characterization document, so
this is corroboration from two directions, not two independent discoveries."*

**Correct on independence.** Both producers' `read_scope` includes
`BATCH-002/tasks/TASK-20260802-15971b`; Lemma L1 lives only there; the inputs are
common. Refusing an independence claim is right, and it is the correction the
BATCH-002 red team's O9 asked for.

**Too weak on content.** The two artifacts are not the same kind of object:

- the **design** shows L1's *argument does not reach its conclusion* — a proof
  gap, whose repair could in principle be a better proof;
- the **oracle** *exhibits a counterexample*: in an HQC-shaped ring it computes
  `μ_2({0,1}) ≠ μ_2({0,2})` exactly, and matches the distinct-value count to the
  cyclic-orbit count. That is not corroboration of a reading; it is a
  demonstration, at toy scope, that the conclusion is **false**, not merely
  unproved.

The distinction is operational, not rhetorical: under "unproved" the design's
`mu2_by_block_distance` is a curiosity; under "false in the ring" it is
**load-bearing**, and O2 above becomes a real bias source rather than a
hypothetical one. Flattening the two into "corroboration" understates the
evidence, which is the mirror image of overclaiming and is governed by the same
rules.

**And the two are not even about the same reason.** The design's stated mechanism
is *truncation* (block `n_e−1` shifts outside the retained window). The primary
reason is group-theoretic and holds with **no** truncation: cyclic shifts
generate `C_{n_e}` on block indices, not `S_{n_e}`, so even a perfectly aligned
ring gives orbit-constancy, not exchangeability. The design's diagnosis is
correct but its mechanism is the weaker half; the oracle supplies the stronger
half. Reported together they are a complete statement; neither alone is.

**One supporting sentence overreaches.** The `2b5ab2` receipt: *"Verified: in the
aligned case the count of distinct `mu_2` values equals the number of cyclic
orbits exactly."* True, and the oracle's own §8.5.1 discloses what the receipt
does not: the aligned case is `n = 16 = n_e·n_2`, which is **not prime**, makes
`X^16−1 = (X+1)^16` a degenerate ring, and violates HQC's own
smallest-primitive-prime rule. In the **faithful** truncated configurations
(`n = 17, 19`) the oracle observes heterogeneity **without** the orbit
explanation (3 and 2 distinct values, "n/a (truncated)"). The artifact is honest;
the receipt's summary is not complete.

> **Cheapest resolving control.** In the ledger decision, record the finding as
> *"one proof-gap identification (design) plus one computed counterexample at toy
> scope (oracle), from a shared input, therefore not independent discoveries but
> not equivalent in strength either"*, and attach the aligned-vs-truncated
> caveat. **Cost: zero.**

---

### O13 — LOW. The novelty claim is hedged in two places and unhedged in the verdict table.

`feasibility` §0: *"No published work measures **any** joint block moment; this
would be the first."* `HEUR-HQC-7`'s validation plan hedges the same claim
correctly (*"To this program's knowledge …"*), and `a17_characterization.md` §8
names what the source search does **not** cover (the reference implementation,
NIST archives, earlier revisions, `[1]` Aguilar-Melchor et al. 2018, and the
general concatenated-coding literature). This is a `dominated_by: null`-shaped
assertion in a headline verdict table without the qualifier or the uncovered set
that the rest of the package supplies.

> **Cheapest resolving control.** Restore the *"to this program's knowledge"*
> qualifier in §0 and cross-reference the uncovered set, **or** spend one
> literature pass on the concatenated-code DFR simulation literature and record
> the result. **Cost: zero for the qualifier.**

---

### O14 — LOW. The immutable ledger records inherit the L1 overreach and are owed a superseding note.

`EV-HQC-6fd5b1` O-6 and `DEC-20260802-9664c6` D-6 both read *"the distortion
reduces to **the** joint moment `mu_{delta_e+1}`"* — a single scalar. Its
well-definedness is exactly what `a17_characterization.md` §1 attributes to
Lemma L1 (*"`μ_k = P[F_{j1} = ⋯ = F_{jk} = 1]` … well defined by Lemma L1"*),
and that attribution is the overreach the design has now identified. The design
repairs it forward (`mubar_m`, the average), and the records are immutable and
must not be edited — but they are the records BATCH-004 and everything after will
cite.

> **Cheapest resolving control.** The `BATCH-003` decision records, in one
> sentence, that O-6/D-6 are to be read with `mu_{delta_e+1}` replaced by
> `mubar_{delta_e+1} = E[C(S,m)]/C(n_e,m)`, and that the substitution changes no
> number and removes an unproved premise. **Cost: zero.**

---

## 2. Objection raised and WITHDRAWN

I record this in full because the instruction is that an objection I cannot
support is withdrawn, not softened, and because the withdrawal is itself
information the Coordinator should have.

**The objection I intended to make.** `T_prec` and `T_stab` are both sized under
the **null being tested** (`S ~ Binomial(n_e, q)`). `C2` — which the design calls
*"the binding criterion at every cell examined"* and *"the single easiest way to
produce an optimistic sample-size number"* — requires ~30 trials in the top
decile of the estimand's mass. If the design's own modeled alternative holds
(`β = −0.0135` at PS-R1, `log2 A_16 = −2.34`), the upper tail of `S` is
compressed: `log2 A_26 = −6.33`, so the leading Bonferroni proxy for
`P[S ≥ 26]` falls ~80×, which would put `T_stab` at `~2.3e9` against an
allocated `1e8` — the 3.4× margin eaten 23× over by the very effect the design
is powered to detect.

**Why it is withdrawn.** I reconstructed the alternative's full law of `S` by
Jordan inversion of the modeled moment sequence `mubar_k = q^k exp(C(k,2)β)`.
The inversion yields a **valid** pmf (all masses non-negative, summing to 1 at
80 digits), and:

| | null | modeled alternative |
|---|---|---|
| `s_90` at `k = 16` | 26 | **24** |
| `P[S ≥ s_90]` | 1.03e-6 | **1.89e-6** |
| `T_stab` | 2.92e7 | **1.59e7** |
| `V` | 4.944e4 | **4.722e4** |
| `SE(log2 Â_16)` at `T = 1e8` | 0.0321 | **0.0314** |

`s_90` moves **down** under the alternative by more than the tail thins, so the
requirement **falls**. **Sizing under the null is conservative for the design's
own modeled alternative, in both criteria.** The objection is wrong and is
withdrawn without qualification. The design's §9.4 item 5 (*"Sizing uses the
null variance. Under strong positive dependence the true variance is larger"*)
remains the correct residual caveat for the opposite sign, and the jackknife plus
`ST-2` are an adequate guard for it.

---

## 3. Where each named duty found nothing

Stated plainly, per the constraint.

**Duty 4, first half — does the oracle certify the same object?** **Nothing
found.** Index set, conditioning, and distinct-vs-repeated convention all
coincide exactly (§O6). The oracle refuses repeated indices by assertion and
quantifies the bug it prevents; the subset-average identity is verified from two
code paths on every configuration; the i.i.d. null equals `p_i^k` by **exact
rational equality** across three structurally different constructions. This is
the strongest artifact in the batch.

**Space (T) integrity.** **Nothing found** in the sampler path. Fixed-weight
index sampling with no Bernoulli step; the (M) generator isolated in a separate
module reachable only from `NULL-M`; `D2`/`D3`/`D5` are hard invariants an (M)
sampler cannot satisfy. The residual risk I did find (O7) is a violation of `A1`,
not a drift to (M).

**Null-object matching.** **Nothing found** on the matching itself. `CTRL-BS`
carries the *exact* true marginal block law rather than a modeled one, which is a
strictly stronger match than the handoff required (`same n_e`, same block length,
same marginal `p_i`). `INV-NULL` is genuinely pre-registered, has four falsifiable
triggers including a magnitude clause (25 % of the (T) excess), and `ST-5`'s
null-first ordering removes the opportunity for motivated interpretation. My
objections against it (O8) are a construction-condition wording error and an
exactness overstatement I measured and found harmless.

**Premature closure and scope.** **Nothing found.** No artifact treats A17 as
settled in either direction; `EV-HQC-6fd5b1`'s "undetermined" is preserved
verbatim; the prediction is two-sided with no one-sided test anywhere; claim tier
`toy` and `certificate.kind: none` are stated in all four design artifacts, both
oracle artifacts and both receipts; `admission_and_ceiling` explicitly says the
experiment *"CANNOT MEET ANY COMPLETION CRITERION of GOAL-HQC-001 under any
outcome"*; the falsification criterion nets the optimistic direction against the
`2.72/4.25/5.40` bits of published conservatism before permitting any statement.
Every extrapolation to HQC's parameters is a numbered heuristic with a
falsification condition, and three heuristics **declare** a missing classical
half while `HEUR-HQC-7` declares a missing rigorous half with the requirement
recorded as **unmet**. That is the standard `docs/claims-and-verification.md`
asks for, met.

**Flag-without-resolution (`DEC-20260802-9664c6` D-7).** **Nothing found** in
either producer. `OPEN-1`, `-2`, `-3`, `-5` are open **with named successors**;
`OPEN-4` is `RESOLVED` with the resolution stated; the oracle's §7 is a textbook
flag-**with**-resolution. The one flag-without-resolution I did find is in the
**Coordinator's** layer, not the producers': `TASK-20260802-506c73` is amended to
say it "can never complete" and the archive card that depends on it was not
amended (O11).

**Arithmetic.** **Nothing found.** Thirteen `T_req` cells, four `p*` values from
the primary formulas, the variance closed form, seven `SE` values, five decoder-
model points and the `dup = 2` cost all reproduced. The producer's arithmetic is
correct throughout, including the two places it is deliberately unflattering to
itself (the `T_stab` factor-28 example and the `10^41` infeasibility).

---

## 4. The rarity gap — direct answer

**Asked**: is O-6's obstruction genuinely relocated from the order axis to the
rarity axis, or is it the same obstruction wearing a different name?

**Answer: RELOCATED — genuinely, and the design deserves credit for it — but the
relocation is narrower than the design's framing suggests in one direction and
wider in another, and neither correction changes the batch decision.**

**Relocated, not renamed.** O-6 is a **non-identifiability** statement about one
law: `μ_m` is not determined by `μ_2`, so no amount of second-moment data at
HQC-1 constrains `μ_16` there. At PS-R1/R3/R5 the design **measures `k = m`
directly** — 16, 17, 30, at HQC's own `n_e` and `m`. A direct measurement of
`mubar_16` cannot be evaded by dependence hiding in a high-order configuration,
because the high-order configuration is what is being measured. **At those
parameter sets O-6's obstruction is dead, not renamed.** This is a real and, so
far as this program's records show, unprecedented thing to measure.

**What replaces it is a different species.** The rarity gap is an
**extrapolation** obstruction across a family of laws, not a non-identifiability
obstruction within one. The difference is evidential and it matters: O-6's
obstruction admits **no** in-range test at HQC's parameters, while the rarity
gap admits several — `F2a` (shape of `log A_k` against `C(k,2)` over
`k = 2…32`), `F2b` (magnitude against each set's own measured inputs), `F2c`
(mediation, via `CTRL-WBP`), `TC-4` (a large-`k` break inside the measured
range), and `F3` (a `λ`-trend). A conclusion drawn through these is conditional
and weak, but it is not vacuous, whereas a conclusion about `μ_16` drawn from
`μ_2` at PS-A would be.

**Where the design's framing understates itself.** The "0.33 decades" figure is
the span of `m/λ` at the sets where `k = m` is reachable. `F3`'s `λ`-lever is
much longer: `λ = 0.023` (PS-A) to `42.6` (PS-R5) is **3.3 decades**, restricted
to `k ≤ 3` at the low-`λ` end. The rarity gap is therefore tested on a 2-D grid
that is thin only in the corner that matters (high `k` **and** high `m/λ`), not
confined to a 0.33-decade line. The design states this in `F3`'s note and then
does not carry it into its own headline.

**Where the design's framing overstates itself.** `HEUR-HQC-3`'s obstruction
paragraph asserts that the O-6 counterexample shape *"is invisible at
`m/λ ≈ 1`, because there every configuration is common."* That sentence is doing
more work than it can bear: at `m/λ ≈ 1` the configuration is not invisible, it
is **absent** — a rare many-blocks-fail mode is a feature of the far-tail regime
and simply does not exist in the bulk one. So the correct statement is not "the
test cannot see it" but "the object being tested does not contain it", which is
a **stronger** limitation, not a weaker one: passing `F3` cannot even in
principle constrain a mechanism that only exists at `m/λ ≫ 1`. `HEUR-HQC-3`'s
own honest limit (*"passing F3 does not validate the extrapolation"*) is
therefore right, and its stated reason is not.

**Consequence for the batch decision: BATCH-004 should run.** The design
delivers a scoped measurement no one has made — `mubar_m` at `m = 16/17/30` on
space (T), with a null object, at HQC's own `n_e` and `m` — for 15.5 CPU-hours,
plus first-ever joint block moments at HQC-1's **verbatim** parameters for
`k = 2, 3`. It does not deliver a statement about HQC-1/3/5, and it says so in
every artifact. The alternative to running it is that the campaign has no
measurement at all, which is the premature-closure failure mode
`docs/inventor-protocol.md` treats as symmetric with overclaiming.

---

## 5. Baseline comparison and Pareto position

Not an attack, so `Pollard-rho` / `BSGS` are not the frontier; the relevant
frontier is *what is already known about the object*.

| baseline | what it measures | order reached | space |
|---|---|---|---|
| SPEC Table 10, RMRS Tables 2–3, Figs. 2–3 | upper tail of the **scalar** `ω(e')` | 1st moment | (T) |
| SPEC Table 11, RMRS Table 4 | **single-block** inner DFR | `k = 1` | (M) simulation |
| RMRS Remark 4.2 / Fig. 4 | weight in **one** RM support | `k = 1` | (T), length 256 |
| **this contract, PS-A** | `mubar_k` at HQC-1's verbatim parameters | `k = 2, 3` | **(T)** |
| **this contract, PS-R1/R3/R5** | `mubar_k` at `k = m = 16/17/30` | **`k = m`** | **(T)** |

`dominated_by`: **not dominated on the order axis** — no row above reaches
`k ≥ 2`. **Dominated on the parameter axis** by the published rows at
`k = 1`, which are at deployed `dup ∈ {3,5}` where PS-R1/R3/R5 are not.
`sota_delta`: first measurement of any joint inter-block failure moment on
space (T); `+15` orders in `k` at PS-R1 relative to every published row;
`−1` rung in `dup` and `−2.9` decades in `m/λ` relative to HQC-1. This is
checked against the two primary sources only; the uncovered literature set is
`a17_characterization.md` §8 (see O13).

---

## 6. Legitimacy of the per-producer snapshot split

**Legitimate on its stated grounds, with one channel opened that rests on a
self-report.**

For: both commits verify (reachable, declared parents `f73f290d` and `6dc0040e`,
all eight `path_sha256` recomputed and matching); the narrowing amendment on
`2b5ab2` updates the `handoff.objective`/`inputs` prose in the *same* amendment,
explicitly naming and repairing the BATCH-002 defect (red-team O7) where prose
was left describing a joint snapshot after the archive block had been narrowed;
the stated reason — a finished, independently verified artifact (43/43 tests
re-run by the Coordinator) should not sit uncommitted in a shared worktree while
a sibling writes — is a real evidence-integrity argument, not convenience.

Against: the split necessarily creates a one-directional channel. The oracle was
frozen at `47f7ad9b` (parent `6dc0040e`) while the design task, whose own header
records starting at `6dc0040e`, was still writing. A joint snapshot would have
made the channel impossible; the split makes it merely unused.

**Is it unused?** I checked the design's four artifacts for content derivable
only from the oracle: no mention of Lemma R, cyclic orbits, orbit counts,
mutants M1–M4, Route A/B, the `p_i^k` exact-equality check, or any oracle
number. The design's L1 correction uses a **different** (truncation) argument
from the oracle's (group-theoretic) one — a similarity too weak to indicate
copying and a difference too large to be a paraphrase — and `CTRL-ORACLE` is
written conditionally (*"If the sibling task … delivers"*), which is what a task
that had not read the sibling would write. The design also asserts
`sibling_task_directory_touched: false`. **The channel appears unused, and the
only formal guarantee is the producer's own attestation.**

> **Cheapest resolving control for future batches.** When a snapshot is split
> mid-batch, record in the receipt the sibling's `HEAD` at the second producer's
> completion and require the second producer to state the commits it read.
> **Cost: one field.**

---

## 7. Required controls, consolidated

Ranked by what they buy per unit cost.

| # | control | cost | closes |
|---|---|---|---|
| C1 | `CTRL-INJ`: injected-dependence recovery arm at PS-R1 and PS-R5, decode-only, analytic `log2 A_16` target | ~1e3 core-s | **O3** — makes a null interpretable by measurement |
| C2 | Heterogeneity-corrected `F2a`/`F2b` prediction from the already-required `ĉ(d)`; gate `ST-6` on it | 0 (analysis) | **O2** — removes the spurious-shutdown route |
| C3 | `HEUR-HQC-4` direction fix + `Corr = −τ/(n_e−1)` in the fixture | 0 | **O4** |
| C4 | PS-R2 (`dup = 2`, `n = 11779`, `ω = 62`, `ω_r = ω_e = 70`, `p* = 0.3887`) | 2.0e4 core-s | **O1** — the only matched test of `HEUR-HQC-6` |
| C5 | PS-R1 reachability restated as `q̂ ≥ 0.202`, with a pre-registered escalation to `T = 3.2e8` | 0 unless triggered | **O5** |
| C6 | `CTRL-ORACLE` mandatory on the ring at `n = 17/19`, tie policy pinned | seconds | **O6** |
| C7 | Hypergeometric `\|supp(x) ∩ supp(r_2)\|` check + asserted counter-range disjointness | 0 (Stage A by-product) | **O7** |
| C8 | `CTRL-BS` shifts `c_j` pairwise distinct mod `T`, asserted in code | 0 | **O8** |
| C9 | Move `stage_D_dilution` out of `ST-3`'s first-cut slot | 6.7e3 core-s (already budgeted) | **O3** |
| C10 | Numeric/editorial: `3.16e5` for `1e12`; one `q` convention for rarity; derive-or-strike `3900`; novelty qualifier; `1758c3` `depends_on`; O12/O14 wording in the decision | 0 | O9–O14 |

**Budget impact if all are adopted**: `5.58e4 → 7.7e4` core-seconds mandatory
(`+38 %`), or `5.58e4 → 5.7e4` if C4 is deferred. Both are inside "roughly 2
batches of compute" as the campaign has used the phrase.

---

## 8. Narrowest supported statement

> BATCH-003 produced a fully specified, internally consistent, arithmetically
> correct experiment design and an exact correctness oracle that computes the
> same estimand the design estimates. The design would, if executed, produce the
> first measurement of an inter-block joint failure moment for the HQC
> concatenated decoder on the true space (T) — at `k = 2, 3` at HQC-1's verbatim
> parameters, and at `k = m ∈ {16, 17, 30}` at three order-matched sets with the
> Reed–Muller duplication multiplicity reduced to 1. **A positive result would be
> well controlled against estimator, decoder and pipeline artifacts. A null
> result is interpretable only as the absence of a *weight-mediated* dependence
> of the modeled size at the tested parameters**, because the design's only
> wash-out guard monitors a quantity that is invariant under the reduced knob.
> Nothing in the batch bears on whether A17 holds at HQC-1/3/5, and nothing in it
> is a security claim in either direction. Claim tier **toy**.

---

## 9. Structured record

```yaml
red_team_report:
  id: RT-20260802-e5ebe9
  task_id: TASK-20260802-e5ebe9
  goal_id: GOAL-HQC-001
  batch_id: BATCH-003
  reviewed_snapshots:
    - {archive_task: TASK-20260803-d53ade, commit: dcefbf6e7fd9bddeab31a9a7257289e5ea02027c, parent: f73f290dd050cfbdecbeec86835dfe16aaa26446, hashes_recomputed: 4, hashes_matched: 4}
    - {archive_task: TASK-20260803-2b5ab2, commit: 47f7ad9b4cb49e2e52a70ffc8089ab3961858f33, parent: 6dc0040e24a5180d69ac5bef48b60f4d7c012bcc, hashes_recomputed: 4, hashes_matched: 4}
  claim_under_review: >-
    That the proposed EXP-HQC-982268 contract, if frozen and executed in
    BATCH-004, would produce an interpretable measurement of mubar_m on space
    (T) under both outcomes; that the feasibility arithmetic is honest in both
    directions; that the duplication ladder has exactly two rungs; that the
    oracle certifies the same object the protocol estimates; and that the
    exchangeability defect in the inherited Lemma L1 is resolved without
    exchangeability re-entering downstream.
  verdict: FREEZE_WITH_REQUIRED_AMENDMENTS
  verdict_detail: >-
    The contract may be frozen and BATCH-004 authorised to spend compute once
    O1-O4 are addressed. O2 and O4 can convert a successfully executed run into
    an uninterpretable one via a spurious ST-6 shutdown; O3 determines whether a
    null is interpretable at all; O1 shows a budgeted rung exists that the
    design has foreclosed. None of the four requires re-designing the contract.
  null_result_interpretable: PARTIALLY
  null_result_detail: >-
    Interpretable as the absence of a weight-mediated dependence of the modeled
    size at the tested parameters. NOT interpretable as the absence of
    dependence: the gammahat < 0.95 guard monitors Var(w(e-tilde)), which is
    independent of dup by construction and will pass at every reduced set, and
    CTRL-WBP - the discriminator for the positional M+ mechanism - is
    inoperative under a null. CTRL-INJ (control C1) converts this to
    interpretable-by-measurement for ~1e3 core-seconds.
  objections:
    - {id: O1, severity: high, summary: "Two-runged-ladder claim is scoped to holding p*, n_e and m fixed; a dup=2 rung at n=11779, omega=62, omega_r=70, p*=0.3887, m=16, n_e=46 costs 2.0e4 core-s at m/lambda=1.586. Coordinator receipt drops the qualifier. OPEN-2's successor guidance points the wrong way in n_e.", control: C4}
    - {id: O2, severity: high, summary: "Exchangeability removed from the estimand (correctly) re-enters in HEUR-HQC-2's log-normal closure and in the Var identity's Cov(W_1,W_2) label; F2a/F2b can fire from covariance heterogeneity alone, triggering ST-6. The oracle demonstrates the heterogeneity is real.", control: C2}
    - {id: O3, severity: high, summary: "Wash-out hole named, not closed: gammahat is invariant under the reduced knob and cannot detect destruction of the F-level dependence; the uninformative-null trigger cannot fire; CTRL-WBP is inoperative under a null; the only destroy-parameter ladder is optional and first-to-cut.", control: "C1, C9"}
    - {id: O4, severity: medium_high, summary: "HEUR-HQC-4's formal statement says |log A_k| is non-increasing in tau; its own justification, its own F4, the frozen contract's independent_variables entry, and the exact identity Corr = -tau/(n_e-1) all say non-DEcreasing. Can trigger the wrong F4 branch and hence ST-6.", control: C3}
    - {id: O5, severity: medium, summary: "PS-R1's '3.4x margin' is a 13% margin in qhat (reachability boundary qhat ~ 0.200), and T_req steps by 3.1x across the integer s_90 jump at qhat ~ 0.220. The q model is validated only at dup in {3,5}.", control: C5}
    - {id: O6, severity: medium, summary: "CTRL-ORACLE is optional though the sibling delivered and reaches the ring at n=17/19; it is the only end-to-end distributional check at the arms that reach k=m (D4 exists only at PS-A). Three tie conventions are in play and none is pinned in the cross-check.", control: C6}
    - {id: O7, severity: medium, summary: "A1 (independence of the five fixed-weight vectors) is by-construction and unmeasured; a PRNG substream collision passes D2/D3/D5 and manufactures exactly the (T)-vs-CTRL-BS excess the campaign seeks.", control: C7}
    - {id: O8, severity: medium, summary: "CTRL-BS's offset condition is stated on o_j but must be on the products j*o_j; and 'E[Ahat_k]=1 EXACTLY' overstates a ratio estimator - measured bias 3.6e-4 bits against 3SE=0.096 bits, harmless.", control: C8}
    - {id: O9, severity: low_medium, summary: "proof_search_map's predicted variance gain 'about 1e12' (= C(46,16)) overstates the true gain of 3.16e5 by 3.13e6x; the subsets overlap.", control: C10}
    - {id: O10, severity: low_medium, summary: "Five rarity figures across the package (621/696/1264/840x/3900x) under three unnamed q conventions; the frozen contract's 3900 is not derivable from any of them.", control: C10}
    - {id: O11, severity: low_medium, summary: "TASK-20260802-1758c3 still depends on TASK-20260802-506c73, which its own amendment says can never complete; by the queue's eligibility rule this batch's ledger archive can never run.", control: C10}
    - {id: O12, severity: low, summary: "Coordinator's 'corroboration from two directions, NOT two independent discoveries' is correct on independence and under-reports content (proof gap vs computed counterexample); and the 'aligned case' verification is on n=16, a non-prime degenerate ring HQC's own rule forbids - disclosed in the artifact, omitted from the receipt.", control: C10}
    - {id: O13, severity: low, summary: "'No published work measures any joint block moment' appears unhedged in the feasibility verdict table while hedged elsewhere; the uncovered literature set is named only in a17_characterization.md section 8.", control: C10}
    - {id: O14, severity: low, summary: "EV-HQC-6fd5b1 O-6 and DEC-20260802-9664c6 D-6 say 'the joint moment mu_{delta_e+1}', whose well-definedness rests on the L1 overreach; a superseding note is owed since the records are immutable.", control: C10}
  objections_withdrawn:
    - id: W1
      summary: >-
        That sizing under the null (A17) is optimistic because the modeled
        alternative compresses the upper tail of S and inflates T_stab.
      why_withdrawn: >-
        REFUTED BY MY OWN COMPUTATION. Reconstructing the alternative's law of S
        by Jordan inversion of mubar_k = q^k exp(C(k,2)*beta) (valid pmf, sums
        to 1 at 80 digits) gives s_90 = 24 (null 26), P[S >= s_90] = 1.886e-6
        (null 1.029e-6), T_stab = 1.59e7 (null 2.92e7), V = 4.722e4 (null
        4.944e4), SE = 0.0314 (null 0.0321). Null-based sizing is CONSERVATIVE
        for the design's own modeled alternative in both criteria.
  duties_that_found_nothing:
    - 'Oracle-vs-protocol object identity: C2 == mubar_k exactly; distinct indices; unconditional; two-code-path identity check. No gap.'
    - 'Space (T) sampler integrity: no Bernoulli step, (M) isolated to NULL-M, D2/D3/D5 unsatisfiable by an (M) sampler. No drift path found.'
    - 'Null-object matching: CTRL-BS carries the EXACT true marginal, a stronger match than required; INV-NULL is genuinely pre-registered with four falsifiable triggers and ST-5 null-first ordering.'
    - 'Premature closure and claim tier: nothing treats A17 as settled in either direction; toy tier and certificate.kind none stated in all eight artifacts and both receipts; two-sided prediction throughout; missing heuristic halves declared rather than papered over.'
    - 'Flag-without-resolution in the producers: none. OPEN-1/-2/-3/-5 carry named successors; OPEN-4 is RESOLVED; oracle section 7 is flag-with-resolution. The one instance found is in the Coordinator layer (O11).'
    - 'Feasibility arithmetic: 13 T_req cells, 4 p* values re-derived from Props 6.1.1/6.1.2, the variance closed form, 7 SEs, 5 decoder-model points and the dup=2 cost of 3.21e20 all reproduced. Zero errors.'
  required_controls: [C1, C2, C3, C4, C5, C6, C7, C8, C9, C10]
  counterexample_or_mutation: >-
    PS-R2: dup=2, n=11779 (prime, 2 primitive), n_e=46, n_2=256, m=16,
    omega=62, omega_r=omega_e=70, p*(Prop 6.1.2)=0.388705, q(model)=0.21932,
    lambda=10.09, m/lambda=1.586, T_req=8.164e7, C_trial=2.456e-4 s,
    cost=2.005e4 core-seconds, SE(log2 A_16) at T=1e8 = 0.0404. Refutes
    "the ladder has exactly two rungs" as stated without its constraint.
  baseline_comparison:
    dominated_by: >-
      NOT dominated on the moment-order axis - no published row in either
      primary source reaches k >= 2. DOMINATED on the parameter axis by SPEC
      Table 11 / RMRS Table 4 / RMRS Remark 4.2, which are at deployed
      dup in {3,5} where PS-R1/R3/R5 are not. Checked against the two primary
      sources only; the uncovered set is a17_characterization.md section 8.
    sota_delta: >-
      First measurement of any joint inter-block failure moment on space (T);
      +15 orders in k at PS-R1 relative to every published row; -1 rung in dup
      and -2.9 decades in m/lambda relative to HQC-1; -13 orders in k at PS-A
      relative to HQC-1's own m.
  heuristic_challenges:
    - 'HEUR-HQC-3 is correctly named the weakest link and correctly declares both justification halves missing. Its obstruction paragraph mis-states its own reason (see section 4): the rare many-blocks-fail mode is ABSENT at m/lambda ~ 1, not merely invisible, which is a stronger limitation.'
    - 'HEUR-HQC-2 requires (eps_j) exchangeable, which section 1.2 of the same package proves is not established (O2).'
    - 'HEUR-HQC-4s formal statement inverts its own destroy-parameter direction (O4).'
    - 'HEUR-HQC-6 has no matched test at all; F6 is a within-PS-A consistency check at k <= 3 of the bridge FORMULA, not of transfer across dup. PS-R2 (C4) supplies the missing test.'
    - 'HEUR-HQC-7 correctly declares the rigorous half unmet and correctly scopes itself out of the reduced arms - this is the designs principal gain over any scheme reducing m.'
    - 'HEUR-HQC-8 declares no validation plan and names a successor. Correct.'
  cost_model_challenges:
    - 'Cost model verified internally consistent: dup=2 cost 3.21e20 reproduced from the packages own C_trial formula and T_req.'
    - 'Memory (< 1 GB against a 2 GB cap) is stated beside time throughout; the 2x implementation contingency, perfect 4-core scaling, modeled q, the T_stab threshold of 30, null-variance sizing and gamma=0.735 are all flagged as optimistic. Six flags, all real.'
    - 'Total expected cost is per-cell T_req, not per-attempt cost with success probability silently 1: T_req = max(T_prec, T_stab) and T_stab is 1/P[jackpot], which IS the inverse-success-probability factor. Correct.'
    - 'PS-R3 and PS-R5 are allocated T = 2e7 against T_req at k=m of 3.09e5 and 2.72e6; the surplus buys k up to 22 and 32 for F2a/TC-4 and is justified, not slack.'
  proof_architecture_challenges:
    - 'Baseline reproduction: performed, not promised - Props 6.1.1-6.1.4, Table 10s binomial column and Table 11s p_i all reproduced and frozen as a regression fixture with INV-REPRO. I re-derived all four p* independently and they match to every printed digit.'
    - 'Observation collision: the audit outcome is stated honestly - the collision is real at PS-A and is broken at PS-R1/R3/R5 by measuring k = m directly, leaving the rarity-axis collision, which is HEUR-HQC-3.'
    - 'Quantifier order: the estimand is defined for every k and every set before any data exist, T is fixed before Stage B (ST-7), and INV-NULL thresholds are frozen. No witness is chosen after seeing an outcome.'
    - 'Method ceiling: derived and stated as the headline negative - T_req ~ 1/DFR, so no unconditional (T) Monte-Carlo can reach mubar_m at HQC parameters at any budget. I reproduce 3.401e41 / 6.8e59 / 8.387e79.'
    - 'Nearby-object control: NULL-M is the closest object where the conclusion is FALSE by theorem (A17 holds on (M)); running the identical estimator on it is the right control and it is mandatory.'
  reduction_and_scope_challenges:
    - 'No corollary is claimed via any cited reduction; the transitive path A17 -> Thm 6.1 -> Table 5 DFR -> Thm 6.3 is inherited from EV-HQC-6fd5b1 O-5 and is not re-asserted or extended.'
    - 'Affected-vs-safe scope is not inflated: the contract states it cannot meet any GOAL-HQC-001 completion criterion under any outcome, does not adjudicate X9/A20, does not reopen A19, and makes no statement about deployed HQC without HEUR-HQC-8.'
  premature_closure_check: >-
    PASS. Nothing treats A17 as settled in either direction. The infeasibility
    result at HQC parameters is a closure at the docs/inventor-protocol.md
    section 4 standard - named obstruction (T_req ~ 1/DFR), argument (derived
    and independently reproduced here), and forward guidance (three OPEN items
    each with a named successor). The design does NOT decline to search: it
    finds the affordable corner and states what that corner cannot answer.
  narrowest_supported_statement: >-
    BATCH-003 produced a fully specified, arithmetically correct experiment
    design and an exact correctness oracle computing the same estimand. If
    executed, the design would produce the first measurement of an inter-block
    joint failure moment for the HQC concatenated decoder on space (T), at
    k = 2,3 at HQC-1's verbatim parameters and at k = m in {16,17,30} at three
    order-matched sets with dup reduced to 1. A positive result would be well
    controlled against estimator, decoder and pipeline artifacts. A NULL RESULT
    IS INTERPRETABLE ONLY AS THE ABSENCE OF A WEIGHT-MEDIATED DEPENDENCE OF THE
    MODELED SIZE AT THE TESTED PARAMETERS. Nothing bears on whether A17 holds at
    HQC-1/3/5 and nothing is a security claim in either direction. Claim tier
    toy.
  next_concrete_action: >-
    Adopt C1 (CTRL-INJ injected-dependence recovery arm, ~1e3 core-seconds) and
    C2 (heterogeneity-corrected F2a/F2b gating ST-6, zero compute) as binding
    amendments before the contract is frozen. They are the two that decide
    whether BATCH-004's number can be read under a null and whether a correct
    run can shut itself down; C3-C10 are cheap and should follow, and C4 (PS-R2)
    is the Coordinator's call on 2.0e4 core-seconds.
  inference:
    requested_policy: review-adversarial
    resolved_model_id: claude-opus-5
    fallback_used: true
    fallback_reason: >-
      No policy alias in orchestration/model-policies.yaml resolves under this
      Claude Code harness; subagents run model: inherit and execute on the
      session model. Recorded, never silently substituted.
    model_verified: false
    reasoning_effort: null
    independent_session: true
    independent_model: false
    quorum_admissible: false
    quorum_note: >-
      INDEPENDENT SESSION, NOT INDEPENDENT MODEL. Nothing in this report is
      admissible toward the AGENTS.md rule 13 closure quorum.
  claim_tier: toy
  certificate: {kind: none, why: 'a review report claims no solve and no relation'}
  proof_status: derivation
  security_claim_about_hqc: none_in_either_direction
  prohibitions_observed:
    modified_producer_artifacts: false
    modified_ledger_records: false
    modified_research_status: false
    state_mutating_git_command_run: false
    wrote_outside_write_scope: false
    executed_the_confirmatory_measurement: false
    sampled_any_hqc_object: false
  computations_performed: >-
    All deterministic, none an HQC measurement: exact/high-precision arithmetic
    in mpmath reproducing (i) V(n_e,q,k), T_prec, s_90, T_stab and T_req at 13
    cells; (ii) p-tilde and p* from Props 6.1.1/6.1.2 at 5 parameter sets;
    (iii) the Gaussian/orthogonality decoder model at 7 points; (iv) the
    producer's C_trial cost model at 13 configurations; (v) a Jordan inversion
    of the modeled alternative's moment sequence to the law of S; (vi) the
    single-subset-versus-mubar variance ratio. No fixed-weight vector, no ring
    product, no decoder, no failure indicator, no HQC object was constructed.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/reviews/TASK-20260802-e5ebe9/red_team_report.md
  reviewed_artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/tasks/TASK-20260803-c470c0/proposed_hypothesis.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/tasks/TASK-20260803-c470c0/proposed_specification.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/tasks/TASK-20260803-c470c0/feasibility_analysis.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/tasks/TASK-20260803-c470c0/heuristics.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/tasks/TASK-20260803-6f50df/oracle.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/tasks/TASK-20260803-6f50df/test_oracle.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/tasks/TASK-20260803-6f50df/oracle_values.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/tasks/TASK-20260803-6f50df/oracle_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/archives/TASK-20260803-d53ade/snapshot-receipt.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/archives/TASK-20260803-2b5ab2/snapshot-receipt.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/BATCH-003-OPENING.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-003/dispatch_queue.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-002/tasks/TASK-20260802-15971b/a17_characterization.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-001/tasks/TASK-20260802-6344ed/dfr_model_transcription.md
    - ledger/evidence/EV-HQC-6fd5b1.yaml
    - ledger/decisions/DEC-20260802-9664c6.yaml
    - ledger/questions/RQ-HQC-001.yaml
    - ledger/goals/GOAL-HQC-001.yaml
```
