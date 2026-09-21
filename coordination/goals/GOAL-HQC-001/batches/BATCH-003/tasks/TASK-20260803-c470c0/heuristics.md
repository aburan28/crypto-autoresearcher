# Numbered heuristics for the joint-moment measurement (proposed `EXP-HQC-982268`)

**Task**: `TASK-20260803-c470c0` (executor) · **Batch**: `BATCH-003` ·
**Goal**: `GOAL-HQC-001` · **Question**: `RQ-HQC-001`
**Produced**: 2026-08-03 · **Repo commit at start**: `6dc0040e24a5180d69ac5bef48b60f4d7c012bcc`
**Companion**: `feasibility_analysis.md` (all numbers cited below are derived there)

**Inference**: `requested_policy: executor-implementation`,
`resolved_model_id: claude-opus-5`, `fallback_used: true`,
`model_verified: false`, `independent_session: true`.

**Claim tier: toy.** `certificate.kind: none`. **No security claim about HQC in
either direction.** These heuristics are **proposed**; only a Coordinator ledger
archive creates `H-HQC-18d1b4` and `EXP-HQC-982268`.

---

## 0. The rule these heuristics enforce, stated first

`docs/target-result-profile.md` and AGENTS.md "Explicit conditional rigor"
require that **every step from a reduced-parameter measurement to any statement
about HQC's parameters be a numbered heuristic**, each with a formal statement,
a justification (rigorous bound + classical distribution theorem where one
exists, and a declaration where one does not), known obstructions, a
falsification condition, and a validation plan.

Eight are numbered: **`HEUR-HQC-1` … `HEUR-HQC-8`**. Numbering is stable once
assigned. Three facts about them are stated up front so no reader has to
discover them:

1. **Only three of the eight have a "classical distribution theorem" half.** The
   others are declared as missing it. That is a weakness of the state of
   knowledge about concatenated decoding under a non-memoryless channel, not a
   bookkeeping omission.
2. **`HEUR-HQC-3` (rarity transfer) is the weakest link and it is load-bearing
   for every statement about HQC's own sets.** It is tested over `0.33` decades
   and applied over `2.9` (`feasibility_analysis.md` §12.1).
3. **The design deliberately eliminates the heuristic that `EV-HQC-6fd5b1` O-6
   names as structurally unsupportable.** By holding `n_e` and `m` at HQC's own
   values in the reduced arms, `mubar_m` is measured **at the load-bearing
   order itself**, so no order-extrapolation step is needed for those arms.
   `HEUR-HQC-7` survives only for the *anchor* arm at true HQC-1 parameters,
   where `k <= 3`, and it is declared **not validatable** there.

**Notation** is `feasibility_analysis.md` §1.1. The estimand is
`A_k = mubar_k / q^k` with `mubar_k = E[C(S,k)]/C(n_e,k)` the **average** `k`-way
joint failure probability (Lemma F1); `beta` is defined in `HEUR-HQC-2`;
`lambda = n_e q`; `eta = dlog q/dlog p`; `gamma = Var(w(ẽ))/(N p*(1-p*))`;
`tau = N/n`.

---

## `HEUR-HQC-1` — Construction-family membership

### Formal statement

> Let `P(n, omega, omega_r, omega_e, dup, n_e)` denote an instance of the HQC
> concatenated construction: `x, y` uniform of weight `omega`, `r_1, r_2` of
> weight `omega_r`, `e` of weight `omega_e`, all independent and uniform on
> their fixed-weight sets in `R = F_2[X]/(X^n - 1)` with `n` prime and 2
> primitive mod `n`; `e' = x·r_2 - r_1·y + e`; `ẽ = e'` truncated to
> `N = n_e * 128 * dup`; inner code the `[128,8,64]` Reed–Muller code duplicated
> `dup` times with maximum-likelihood decoding; outer code shortened
> Reed–Solomon over `F_256` of length `n_e`. Then for the instances
> `PS-A, PS-R1, PS-R3, PS-R5` of `EXP-HQC-982268` — which differ from HQC-1/3/5
> **only in `dup`**, with `n_e`, `m`, `p*`, `omega/sqrt(n)`, `tau` and the
> sampler held at each level's own values — the **mechanism** generating
> dependence among the `F_j` is the same mechanism as at HQC-1/3/5, differing
> only through the measured scalars `eta`, `gamma`, `Var(W_1)/E[W_1]^2` and
> `n_e`.

### Justification

**Rigorous half.** The two structural facts alleged to generate inter-block
dependence are **construction facts, not parameter facts**, and hold verbatim
for every member: (i) `ẽ` is one random object shared by all `n_e` blocks;
(ii) `x, y, e` have exactly fixed weights, so block weights compete for a global
budget. Two supporting lemmas hold for every member:

- **Lemma L1' (re-verified here, weaker than the inherited claim).** Because the
  fixed-weight sets are cyclic-shift invariant and `(x,y,r_1,r_2,e) ↦ x·r_2 -
  r_1·y + e` commutes with cyclic shift, the law of `e'` is shift invariant.
  Block `B_j` is the translate of `B_0` by `j*n_2`, and for `0 <= j <= n_e-1`
  that translate lies inside the retained window, so `F_j ~ F_0` for every `j`
  and the joint law is **translation** invariant within the window. It is
  **not** exchangeable, and `feasibility_analysis.md` §1.2 shows the estimand
  `mubar_k` never needed exchangeability.
- **Lemma L2 (re-verified here).** For a binary linear code with
  minimum-distance decoding, the event bounded by Props 6.1.3/6.1.4 —
  "some non-zero codeword is at least as close as the transmitted one" — is an
  **increasing** event in `supp(e)`: it equals `{g(e) <= 0}` with
  `g(e) = min_{c!=0}(|c| - 2|e ∧ c|)`, and adding a coordinate to `supp(e)` can
  only increase each `|e ∧ c|`, hence only decrease `g`. Consequently `eta > 0`
  for either deterministic tie convention, and `q(p)` is non-decreasing in `p`.

**Classical half: none.** There is no distribution theorem for the joint law of
Reed–Muller ML-decoder outcomes across blocks of a quasi-cyclic ring product.
**Recorded as missing, not papered over.**

### Obstructions

- `dup = 1` is **not a deployed HQC inner code** (SPEC deploys 3 and 5; RMRS's
  published instantiation used 2). It is the undluplicated base code of the same
  family, one rung below the smallest published setting.
- Reducing `dup` reduces `n` by the same factor, so `omega, omega_r` shrink as
  `sqrt(n)`. The A7 regime `omega = alpha*sqrt(n)` is preserved to 2 %
  (`alpha_omega = 0.4966 -> 0.5068`), but `omega` itself is 39 rather than 66,
  and small-`omega` effects are not excluded.
- Integer rounding of `omega, omega_r` moves the exact `p*` upward by
  `<= 0.008` (`0.339788 -> 0.347921` at PS-R1). Recorded, not hidden.

### Falsification condition

**F1a.** `sign(Corrhat(W_i,W_j))` differs between `PS-A` and a majority of the
reduced sets. **F1b.** `gammahat` at `PS-A` falls outside `[0.55, 0.85]` while
the reduced sets fall inside, or vice versa. **F1c.** `gammahat` at any reduced
set exceeds `0.95` (dependence washed out; that set is uninformative and a null
there is **not** evidence for A17 — `feasibility_analysis.md` §10.3).

Any of F1a/F1b/F1c refutes family membership for the purposes of this contract,
and **no reduced-set number may then be read as informative about HQC's sets.**

### Validation plan

- **Sampling**: direct (T) sampling at all four sets including `PS-A` at HQC-1's
  own `(n, omega, omega_r, omega_e, n_2, dup, n_e) = (17669, 66, 75, 75, 384, 3, 46)`.
- **Statistics**: `phat` vs analytic `p*` (Prop 6.1.2); `gammahat`;
  `Var(W_1)` vs the binomial `n_2 p(1-p)` (RMRS Remark 4.2 reports "virtually
  identical" at support length 256); `Corrhat(W_i,W_j)` against the exact
  identity `Var(W) = n_e Var(W_1) + n_e(n_e-1) Cov(W_1,W_2)`.
- **Tail check**: upper-tail quantiles of `w(ẽ)` at `PS-A` against **SPEC Table
  10's published `6169 / 6203 / 6232 / 6257`** at the `1e-3 … 1e-6` upper tails,
  `N = 17664`. The comparison method reproduces Table 10's exactly-computable
  binomial column to `+-1.3` (`feasibility_analysis.md` §4), so a `> 3`-unit
  deviation at `>= 2` of 4 tails is a real failure.
- **Budget**: zero extra — all quantities are by-products of Stage A.
- **Validation experiment**: `EXP-HQC-982268` (proposed), arms `PS-A`, `PS-R1`,
  `PS-R3`, `PS-R5`, controls `D1`–`D5`.

---

## `HEUR-HQC-2` — Weight-mediated dependence (the bridge)

### Formal statement

> Condition on the block-weight vector `(W_0, …, W_{n_e-1})`. Then
> **(a)** the `F_j` are conditionally independent given `(W_j)_j`; and
> **(b)** the conditional failure probability depends on the block only through
> its weight, log-linearly to the order retained:
> `log P[F_j = 1 | W_j] = log q + eta * eps_j + O(eps_j^2)` with
> `eps_j = (W_j - E W_1)/E W_1` and `eta = dlog q/dlog p` at `p = p*`.
> If in addition `(eps_j)_j` is exchangeable and jointly log-normal to the order
> retained, then for every `k <= n_e`
>
> ```
> log A_k = C(k,2) * beta ,   beta := eta^2 * Cov(eps_i, eps_j)
>                                   = eta^2 * Corr(W_i,W_j) * Var(W_1)/E[W_1]^2 ,
> ```
>
> so `log A_k` is **proportional to `C(k,2)`** with a **`k`-independent**
> constant, and `sign(log A_k) = sign(Corr(W_i,W_j))`.

### Justification

**Rigorous half.**
1. `Var(W) = n_e Var(W_1) + n_e(n_e-1) Cov(W_1,W_2)` is an **exact identity**
   under equal marginals (Lemma L1'), used with no approximation; it yields
   `Corr(W_i,W_j) = (gamma - 1)/(n_e - 1)` when `Var(W_1)` takes its binomial
   value.
2. `eta > 0` is forced by Lemma L2 (the block-failure event is increasing in the
   block's error support), so the **sign** of the response to a weight
   perturbation is determined by the mechanism and is not fitted.
3. `eta` is computed by exact arithmetic from Prop 6.1.4 — an image-verified
   published formula — whose implementation here reproduces SPEC Table 11's
   `p_i` (`-10.795 / -14.137 / -11.324` against printed
   `-10.79 / -14.14 / -11.30`) and BATCH-002's independent A19 gaps
   (`10.62 / 7.96 / 16.79` bits) exactly.

**Classical half.** The exponential-tilt / log-normal moment identity
`E[exp(sum_{j in J} Z_j)] = exp(k sigma^2/2 + C(k,2) c sigma^2)` for an
exchangeable Gaussian vector with variance `sigma^2` and covariance
`c sigma^2` — textbook; no citation invented. Its first-order form
`A_k ≈ 1 + C(k,2) beta` agrees with `a17_sensitivity.yaml` step 5's
independently derived `K = C(m,2)(1-q)/q` under `rho = beta*q/(1-q)`.

### Obstructions — the reason this must be tested rather than assumed

- **Clause (a) is not proved.** `ẽ` is a product in a cyclic ring; two blocks can
  share algebraic structure that survives conditioning on their weights. That is
  exactly the common-mode mechanism `M+` of `a17_sensitivity.yaml` step 4, whose
  sign is **positive** — opposite to the weight-budget term.
- **Clause (b) is a first-order expansion.** At `PS-A`, `eta ≈ 50.7` and
  `sd(eps) = sqrt((1-p)/(n_2 p)) = 0.0711`, so `eta*eps` has standard deviation
  `3.6` — **the expansion parameter is not small at HQC's own parameters**, and
  the log-normal closure is doing real work. At `PS-R1` (`eta ≈ 12.3`,
  `sd(eps) = 0.123`) it is `1.5` — better, but not small either.
- **The closure is a closure.** `eps` is a standardized weight, near-Gaussian in
  the bulk and not in the tail, and the far tail is precisely where `mubar_m`
  lives at HQC's parameters.
- Evaluated at `PS-A` with the published-derived `gamma = 0.735`, the model
  returns `|C(16,2) beta| = 13.2` bits — i.e. **the linearization of its own
  output is invalid there.** Recorded as a property of the model.

### Falsification condition

Any one of the following, with the null arms passing (`INV-NULL`):

- **F2a (shape).** `log Ahat_k / C(k,2)` varies by more than a factor 2 across
  `k in [2, k_max]` at half or more of the sets with `k_max >= 8`.
- **F2b (magnitude).** The weighted-least-squares `betahat` (regression of
  `log Ahat_k` on `C(k,2)` through the origin) differs by more than a factor 2
  from `eta^2 * Corrhat(W_i,W_j) * Varhat(W_1)/Ehat[W_1]^2` computed from that
  set's **own** measured inputs, at half or more of the sets.
- **F2c (mediation).** The `CTRL-WBP` arm — the identical measurement after an
  independent uniformly random permutation of the coordinates **inside each
  block**, which preserves every `W_j` exactly and destroys all within-block
  positional structure — moves `log2 Ahat_k` by more than `3*SE_combined` at any
  `k <= k_max` at half or more of the sets. Then the dependence is **not**
  weight-mediated and clause (a) is false.

**A refuted `HEUR-HQC-2` forbids every downstream evaluation at HQC's
parameters**; this prohibition is written into `EXP-HQC-982268` `ST-6`.

### Validation plan

- **Sampling**: all four sets; `CTRL-WBP` at `PS-R1` (a coordinate permutation,
  no extra sampling).
- **Statistics**: `log2 Ahat_k`, `k = 2..k_max`, per set; the WLS `betahat`; the
  ratio `betahat/beta_pred`.
- **Tail check**: the largest `|log2 Ahat_k|` over all `(set, k)` against the
  Gumbel prediction for the maximum of that many standardized `CTRL-BS`
  deviations, using **empirical** null SEs.
- **A-priori discrimination** (`feasibility_analysis.md` §8.3, `gamma = 0.735`
  assumed, MODELED): predicted `log2 A_m` of `-2.34 / -1.10 / -1.50` bits at
  `PS-R1/R3/R5` against SEs of `0.032 / 0.008 / 0.026` bits — **73σ / 137σ /
  58σ**; and `-0.110` bits at `PS-A`, `k=2`, against `SE = 0.0092` — **12σ**.
- **Budget**: this is the main experiment.

---

## `HEUR-HQC-3` — Rarity-regime transfer  *(WEAKEST LINK; named as such)*

### Formal statement

> The bridge coefficient `beta` is a function of `(eta, Var(eps),
> Corr(eps_i,eps_j))` alone and **does not depend on the rarity ratio
> `m/lambda`**. Consequently a `betahat` measured at a set with
> `m/lambda in [0.70, 1.51]` is the same `beta` that governs `log A_k` at a set
> with `m/lambda in [621, 5470]`, which is where HQC-1/3/5 sit.

### Justification

Within `HEUR-HQC-2`'s log-normal closure this is **exact**: `beta` is built from
second moments of the latent `eps` and from `eta`, none of which references `m`
or `lambda`; rarity enters `A_k` only through `C(k,2)`.

**There is no rigorous half and no classical half.** The statement is a property
of the closure, and the closure is what is in doubt. Declared, not disguised.

### Obstructions — this is the campaign's own headline obstruction, relocated

- `m/lambda ≈ 1` and `m/lambda ≈ 621` are qualitatively different events: at the
  former `{S >= m}` is a typical configuration, at the latter it is a `~10^-40`
  tail event. A closure fitted in the bulk is being asked to predict the far
  tail — the classic failure mode of moment closures.
- `a17_sensitivity.yaml` step 6 states the exact failure shape: *"a joint law can
  have `rho ≈ 0` while `mu_m >> q^m`, if the dependence lives in a rare
  configuration in which many blocks fail together."* **Such a configuration is
  invisible at `m/lambda ≈ 1`, because there every configuration is common.**
  This is `EV-HQC-6fd5b1` O-6's obstruction moved from the *order* axis (where
  this design removes it) to the *rarity* axis (where it remains).
- `feasibility_analysis.md` §5–§6.3 shows the gap cannot be narrowed by budget:
  every affordable cell sits at `m/lambda ~ 1`, and `T_req` grows by `~10^{2.5}`
  per doubling of `m/lambda`.

### Falsification condition

**F3.** After dividing out each set's own
`eta^2 * Corrhat(W_i,W_j) * Varhat(eps)`, the residual `betahat/beta_pred` shows
a monotone trend in `log lambda` across `PS-R5 (lambda ≈ 42.6)`,
`PS-R3 (20.7)`, `PS-R1 (10.6)` and `PS-A (0.023)` whose ordinary-least-squares
slope has magnitude `>= 0.15` per e-fold with a 95 % interval excluding zero.

*(Note the ladder deliberately includes `PS-A`, whose `lambda` is `10^3` below
the reduced sets. `PS-A` contributes only `k = 2, 3`, so this is a test of
`beta`'s `lambda`-dependence at low `k` — the only such test the budget affords,
and it is stated as partial.)*

### Validation plan

- **Sampling**: the `lambda` ladder is built into the set list; no extra arms.
- **Statistics**: `betahat/beta_pred` vs `log lambda`, jackknife errors.
- **Tail check**: at the set with the largest `k_max` (`PS-R5`, `k_max = 32`),
  compare the measured `log Ahat_k` at the **largest** `k` against the
  extrapolation of the `C(k,2)` law fitted on `k <= k_max/2` only. A break at
  large `k` inside the measured range is the strongest in-range warning that the
  closure fails deeper in the tail.
- **Budget**: zero extra; re-analysis across existing arms.
- **HONEST LIMIT, restated because it is the design's central liability**: the
  ladder spans `m/lambda in [0.70, 1.51]` — **0.33 decades** — at the orders
  where `k = m` is reachable. HQC-1 sits at `621`. **Passing F3 does not
  validate the extrapolation**, and no record produced from this contract may
  say that it does.

---

## `HEUR-HQC-4` — Dilution scaling of the weight budget  *(the destroy parameter)*

### Formal statement

> The **negative** component of `Corr(W_i,W_j)` is generated by the exactly-fixed
> weights of `x, y, e` competing for a global budget, and **dilutes as the
> retained window shrinks relative to the ambient ring**: for the fixed-weight
> component alone, restricting a weight-`W` vector on `n` coordinates to a window
> of `N` gives a hypergeometric weight with dispersion factor
> `(n-N)/(n-1) = 1 - tau + O(1/n)`. Hence `|Corr(W_i,W_j)|`, and therefore
> `|log A_k|` at fixed `k`, is **non-increasing in `tau = N/n`**; HQC's own
> `tau ≈ 1` (`17664/17669 = 0.99972`) is the **maximally budget-constrained**
> member of the family.

### Justification

**Rigorous half.** The hypergeometric variance `Var = N p(1-p)(n-N)/(n-1)` is
exact and classical, and applies verbatim to the `e` summand of `e'`.

**Classical half: none for the product terms** `x·r_2` and `r_1·y`, whose window
restriction is not hypergeometric. Indeed the published-derived `gamma ≈ 0.735`
at `tau ≈ 1` is far above the `1 - tau ≈ 0` the fixed-weight component alone
would give, so the products contribute over-dispersion and the net
`tau`-dependence is **not predicted quantitatively** — only its **direction**.

### Obstructions

- Only the direction is predicted. A measured `gammahat(tau)` curve is a new
  observation, not a check of a formula.
- Holding `p*` fixed while `tau` falls forces `omega ∝ sqrt(n)` to grow; the
  contract re-solves `omega, omega_r` per rung so the comparison is at matched
  `p*` to 3 decimals (`0.3479 / 0.3525 / 0.3509` at `tau = 0.994 / 0.500 /
  0.250`). The residual `p*` mismatch of `0.005` is recorded.
- These rungs are the **first arms cut** if the budget binds (`ST-3`).

### Falsification condition — with its ambiguity resolved **in advance**

**F4.** `|log2 Ahat_k|` at fixed `k` fails to be non-increasing along
`PS-R1 (tau = 0.994) -> PS-D2 (0.500) -> PS-D4 (0.250)` by more than
`3*SE_combined` at any `k <= min(k_max)` across the three.

`docs/inventor-protocol.md` names non-decay under an increasing destroy
parameter as the **canonical artifact tell**, and it has two readings that must
be separated *before* any number exists. **Pre-registered resolution:**

- If `CTRL-WBP` (within-block coordinate permutation) **preserves** the signal,
  the dependence is weight-mediated, and non-decay contradicts `HEUR-HQC-4`
  itself — the dilution model of the negative component is wrong.
- If `CTRL-WBP` **destroys** the signal, the dependence is positional (the `M+`
  common-mode mechanism) and `HEUR-HQC-2` clause (a) is refuted instead.
- If `CTRL-BS` also fails to vanish, the whole observation is an **estimator
  artifact** and is `invalid_measurement` (`INV-NULL`).

Each branch is a recorded finding with a named mechanism — **never a bare flag**
(`DEC-20260802-9664c6` D-7).

### Validation plan

- **Sampling**: `PS-R1` plus two optional rungs at matched `n_e = 46`,
  `n_2 = 128`, `p* ≈ 0.35`:
  `PS-D2` (`n = 11779`, `omega = 56`, `omega_r = omega_e = 63`, `tau = 0.4999`) and
  `PS-D4` (`n = 23563`, `omega = 79`, `omega_r = omega_e = 89`, `tau = 0.2499`).
- **Statistics**: `gammahat(tau)`, `Corrhat(W_i,W_j)(tau)`, `log2 Ahat_k(tau)`
  at fixed `k`.
- **Tail check**: `gammahat` at `PS-R1` against the published-derived
  `0.61–0.74` band.
- **Budget**: `2 158 + 4 585 = 6 743` core-seconds at `T = 1e7` per rung
  (`feasibility_analysis.md` §9.2 cost model). Optional; cut first.

---

## `HEUR-HQC-5` — Elasticity validity

### Formal statement

> The elasticity of the **true** per-block failure probability,
> `eta_true = dlog q/dlog p`, equals the elasticity of the **published upper
> bound**, `eta = dlog p_i/dlog p` from Prop 6.1.4, to within a factor
> `1 +- 0.20`, uniformly over the parameter sets used.

### Justification

**Rigorous half.** `q <= p_i` is proved on space (M) by Prop 6.1.4. The *level*
gap is measured by the sources themselves: SPEC Table 11 gives
`0.17 / 0.25 / 0.18` bits at NIST-1/3/5; RMRS Table 4 gives `0.19 / 0.31 / 0.05`
bits between its improved bound and its observed DFR. **A gap that is nearly
constant across `p` is a gap with zero elasticity**, which is exactly the
condition under which `eta_true = eta`. Independently, the Gaussian/orthogonality
model of `feasibility_analysis.md` §6.2(b) — validated against all three of
Table 11's observed DFRs to `0.55–0.87` bits — gives
`eta_model = 50.7 / 74.9 / 68.0` against `eta_{6.1.4} = 45.6 / 69.7 / 64.1`,
i.e. agreement to `6–11 %`, well inside the claimed `+-20 %`.

**Classical half: none.** The constancy of the bound-to-truth gap rests on six
published points across two documents plus one model.

### Obstructions

- `eta` enters `beta` **squared**: a 20 % error in `eta` is a 44 % error in
  `beta`, inside but not comfortably inside `F2b`'s factor-2 tolerance.
- The published gaps are measured at `dup in {2,3,5}`; the reduced sets use
  `dup = 1`, where the union bound is far looser (the rigorous `q` bracket is
  `~8` bits wide at `d_i = 64`).

### Falsification condition

**F5.** The empirical elasticity, obtained by regressing `log qhat` on
`log phat` across the sets sharing an inner code (`PS-R1, PS-R3, PS-R5, PS-D2,
PS-D4` all have `dup = 1`, spanning `p* in [0.348, 0.376]`), differs from the
analytic `eta` by more than 20 %.

**`INV-Q` (invalidation, not falsification).** `qhat` must lie inside the
rigorous bracket `[P[Bin(d_i,p)>d_i/2] + ½P[=d_i/2], p_i(6.1.4)]` at **every**
set. The bracket is validated: it contains all three of SPEC Table 11's
published observed inner DFRs. A `qhat` outside it is an **implementation
defect**, and the run is `failed_implementation`.

### Validation plan

- **Sampling**: Stage A measures `qhat, phat` at every set (`4 x 2e6` trials).
- **Statistics**: `dlog qhat/dlog phat` by WLS, against `eta` at each `p*`.
- **Tail check**: `INV-Q` bracket membership at every set.
- **Budget**: Stage A, `2 900` core-seconds total.

---

## `HEUR-HQC-6` — Inner-multiplicity transfer

### Formal statement

> A bridge coefficient measured at duplication multiplicity `dup = 1`
> (`n_2 = 128`, `d_i = 64`) predicts the bridge coefficient at HQC's
> multiplicities `dup in {3,5}` (`n_2 in {384,640}`) through substitution of that
> multiplicity's own `eta`, `Var(eps) = (1-p)/(n_2 p)` and `Corr(W_i,W_j)`, with
> **no additional multiplicity-dependent term**.

### Justification

**Rigorous half.** SPEC's own A11 transfers Props 6.1.3/6.1.4 across
multiplicities by substituting `d_i` and `n = 2 d_i`, and that transfer
reproduces Table 11's tabulated values at `dup = 3` and `dup = 5`; so the
**marginal** is known to transfer this way. `Var(eps) = (1-p)/(n_2 p)` is the
exact binomial value and is the only place `n_2` enters `beta` besides `eta`.

**Classical half: none for the joint law.**

### Obstructions

- Duplication changes the decoder's **geometry**, not just its length: the
  folded statistic sums `dup` copies before the Hadamard transform, so a block's
  failure depends on the *distribution of its errors across copies*, not only on
  its total weight. That is a multiplicity-dependent departure from
  `HEUR-HQC-2` clause (b), and it is **not bounded here**.
- **There is no intermediate rung.** `feasibility_analysis.md` §6.3 shows the
  cost jumps by `10^17` between `dup = 1` and `dup = 2`. This heuristic bridges
  a gap that cannot be walked, only jumped.

### Falsification condition

**F6.** `betahat` at `PS-A` (`dup = 3`, true HQC-1 parameters, from `k = 2` and
`k = 3`) differs by more than a factor 2 from
`eta^2 * Corrhat(W_i,W_j) * Varhat(eps)` computed from `PS-A`'s **own** measured
inputs.

This is a **within-`PS-A` consistency test** and therefore needs no matched
`dup = 1` twin; it tests whether the bridge formula holds at `dup = 3` at all.
It is the only multiplicity check this budget affords, and that is stated rather
than dressed up.

### Validation plan

- **Sampling**: `PS-A`, `T = 1e8` (3 shards of `3.4e7`), `3.35e4` core-seconds.
- **Statistics**: `log2 Ahat_2` against `C(2,2)*beta/ln2`. Derived
  `SE(log2 Ahat_2) = 0.0092` bits against a modeled `-0.110` bits — a **12σ**
  test at `k = 2` alone.
- **Tail check**: `log2 Ahat_3`, where the ratio
  `(log Ahat_3 / C(3,2)) / (log Ahat_2 / C(2,2))` must be `1` under the bridge.
  `SE(log2 Ahat_3) = 0.108` bits against a modeled `-0.331`: a **3.1σ** shape
  test, and **the only shape test available at HQC's own parameters**.
- **Budget**: included in the main allocation.

---

## `HEUR-HQC-7` — Order regularity  *(NOT validatable at `k = 16` for `PS-A`)*

### Formal statement

> There is no order threshold `k*` in `(k_max, m]` at which a new mechanism
> switches on: the law `log A_k = C(k,2)*beta` fitted on `k in [2, k_max]`
> continues to hold for `k in (k_max, m]`.

### Scope — read this before the rest

**This heuristic is needed only for the anchor arm `PS-A`**, where `k_max = 3`
and `m = 16`. **It is NOT needed for `PS-R1/R3/R5`, which measure `k = m`
directly** (`k_max = 16 / 22 / 32` against `m = 16 / 17 / 30`). Removing this
heuristic from the reduced arms is the principal design gain over any scheme
that reduces `m`, and it is the direct operational consequence of
`EV-HQC-6fd5b1` O-6.

### Justification

**Rigorous half: none.** `docs/claims-and-verification.md` asks for a rigorous
bound plus a classical distribution law; neither exists, and the requirement is
recorded as **unmet**.

**Classical half:** within the log-normal closure the identity is exact in `k`,
so this is a restatement of `HEUR-HQC-2` rather than an independent assumption.
That is a weakness, not a strength: `HEUR-HQC-7` and `HEUR-HQC-2` fail together,
and a test of `HEUR-HQC-2` at low `k` cannot separate them.

### Obstructions

`EV-HQC-6fd5b1` **O-6** and `DEC-20260802-9664c6` **D-6** state exactly this gap:
`mu_m` is not determined by `mu_2`, so no finite set of low-order moments
determines `mu_16`. `HEUR-HQC-7` is the assumption that O-6's counterexample
shape does not occur in this family at `PS-A`.

### Falsification condition

**F7.** Any departure from `C(k,2)` proportionality **within** the measured
range — i.e. `F2a` — refutes `HEUR-HQC-7` as well. At `PS-A` the only in-range
test is the `k=3`/`k=2` ratio (3.1σ). **There is no condition available that
could confirm it beyond `k_max`,** and none is claimed.

### Validation plan

- **What is possible**: (i) the `k=3/k=2` ratio at `PS-A`; (ii) testing the
  `C(k,2)` law over `k = 2 … 32` at `PS-R5`, `2 … 22` at `PS-R3` and `2 … 16` at
  `PS-R1` — i.e. **past HQC-3's own `m = 17` and past HQC-5's own `m = 30`**, and
  **exactly to** HQC-1's own `m = 16` at `PS-R1`, where `k = 17` is already out
  of reach. To this program's knowledge no published work measures the law at any
  `k >= 2` at all.
- **What is not possible**: testing it at `k = 16` at `PS-A`'s own `(n_e, q)`.
  Derived requirement `T = 3.4e41` (`feasibility_analysis.md` §5) against an
  affordable `T ≈ 1e8`.
- **Named successor**: the importance-sampled (T) estimator of
  `feasibility_analysis.md` §11 item 1. Not designed here, not claimed to work,
  named so the gap carries a successor rather than a shrug.

---

## `HEUR-HQC-8` — Sampler equivalence

### Formal statement

> Results obtained with the **uniform** fixed-weight sampler
> `SampleFixedWeightVect$` transfer to HQC as deployed, which uses the **biased**
> `SampleFixedWeightVect`, up to the factor SPEC §6.2.3 already charges,
> `(tau_max^{omega_r})^3 <= 1.00045` at NIST-1.

### Justification

**Rigorous half.** SPEC A22: the §6.1 analysis and the §6.2.1–6.2.2 proofs
*themselves* assume the uniform sampler, and §6.2.3 charges the deployed sampler
separately via Lemma 6.4 and Table 12. Using the uniform sampler therefore
matches **exactly** the object Theorem 6.1 is about.

**Classical half: not applicable** — this is a scope alignment, not a
distributional claim.

### Obstructions

SPEC's `(tau_max^{omega_r})^3` factor is charged against the **DFR**, a scalar.
Nothing in either source charges it against a **joint moment**, and a bias that
correlates coordinate positions across blocks would not be captured by a scalar
multiplier.

### Falsification condition

**Out of scope for this contract; nothing measured here can falsify it.**
Declared rather than left blank.

### Validation plan

**None, and that is declared.** Named successor: a paired arm running the
deployed `SampleFixedWeightVect` at `PS-R1` and comparing `log2 Ahat_k`, needing
only a second sampler implementation. **This contract does not run it, and no
statement about deployed HQC may be made without it.**

---

## 9. Dependency graph — what any given claim costs

| claim | heuristics it is conditional on |
|---|---|
| `log2 Ahat_k` at a reduced set, `k <= k_max` | **none** — a scoped measurement at stated parameters |
| `log2 Ahat_2`, `log2 Ahat_3` at **true HQC-1 parameters** | **none** — a scoped measurement at HQC-1's own `(n, omega, omega_r, omega_e, n_2, dup, n_e)` |
| "the dependence is weight-mediated" | 2 |
| "`beta` measured at `dup=1` rarity is HQC's `beta`" | 1, 2, 3, 5 |
| "`beta` at `dup=1` predicts `dup in {3,5}`" | 1, 2, 5, 6 |
| **any statement about `A_16` at HQC-1, `A_17` at HQC-3, `A_30` at HQC-5** | **1, 2, 3, 5, 6** *(and **7** if routed through `PS-A` rather than through the reduced arms)* |
| any statement about HQC **as deployed** | 1, 2, 3, 5, 6, (7), **8** |
| "the destroy parameter behaves as predicted" | 4 |

The last two rows are the ones that matter and they carry the longest
conditions. **A downstream record that states a number for `A_m` at HQC-1/3/5
without rendering "conditional on `HEUR-HQC-1, -2, -3, -5, -6`" is asserting
above its record**, and that is a claim-tier violation under
`docs/claims-and-verification.md`.

---

## 10. Scope limits of this document

- These heuristics are **proposed**. Only a Coordinator ledger archive creates
  `H-HQC-18d1b4` and `EXP-HQC-982268`; nothing here is official.
- **No measurement of HQC was performed by this task.** Every number is
  transcribed from a published table, recomputed by exact arithmetic from a
  published formula, derived symbolically in `feasibility_analysis.md`, or — for
  the machine constants — obtained from `CALIB-M0`/`CALIB-M0b`, generic numpy
  and big-integer microbenchmarks that construct no HQC object.
- **No security claim about HQC in either direction.** Claim tier **toy**;
  `RQ-HQC-001.claim_tier_ceiling` makes that ceiling *more* binding for a
  standardized algorithm, not less.
- Not admissible toward the `AGENTS.md` rule 13 closure quorum.
- The predecessor task's `heuristics.md` numbered eight heuristics under the same
  identifiers. **The statements here are re-derived and differ**: `HEUR-HQC-1`
  now names a one-knob family; `HEUR-HQC-3`'s ladder is `0.33` decades, not the
  `1.3` claimed there; `HEUR-HQC-7` is no longer load-bearing for the reduced
  arms; and every effect size and sample count is recomputed
  (`feasibility_analysis.md` §12.4). Where the two disagree, **this document
  governs**, and the disagreement is recorded rather than silently overwritten.
