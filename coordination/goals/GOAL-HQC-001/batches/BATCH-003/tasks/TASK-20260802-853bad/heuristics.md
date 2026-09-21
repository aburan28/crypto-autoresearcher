# Numbered heuristics for the joint-moment measurement (proposed EXP-HQC-982268)

**Task**: `TASK-20260802-853bad` (executor) · **Batch**: `BATCH-003` ·
**Goal**: `GOAL-HQC-001` · **Question**: `RQ-HQC-001`
**Produced**: 2026-08-02 · **Repo commit at start**: `78dff1e4976655c0a46019b298bec13459ccd422`
(tree clean except this task's own untracked directory)

**Inference**: `requested_policy: executor-implementation`,
`resolved_model_id: claude-opus-5`, `fallback_used: true`, `model_verified: false`,
`independent_session: true`.

---

## 0. What this document is, and the rule it enforces

`docs/target-result-profile.md` and `docs/claims-and-verification.md`
("Heuristic-conditional claims") require that **every step from a
reduced-parameter measurement to any statement about HQC's parameters be a
numbered heuristic**, each with a formal statement, a justification
(rigorous bound + classical distribution law where one exists), known
obstructions, a falsification condition, and a validation plan.

Eight heuristics are numbered below: **HEUR-HQC-1 … HEUR-HQC-8**. Numbering is
stable once assigned.

**The rule they enforce.** The proposed experiment measures
`log2 A_k = log2( mu_k / q^k )` on the true space (T) at parameter sets it can
afford. Section 3 of `feasibility_analysis.md` derives that **no affordable
parameter set reaches `k = 16` at HQC-1's own `(n_e, q)`** — the shortfall is a
factor `~2e34` in samples. Therefore **every sentence in any downstream record
that mentions HQC's own parameters at order `delta_e + 1` is conditional on the
chain HEUR-HQC-1 → -2 → -3 → -5 → -6 → -7, and must carry that qualifier.**
Dropping the qualifier is a claim-tier violation under
`docs/claims-and-verification.md`.

**HEUR-HQC-7 is not validatable by this contract at `k = 16`.** That is stated
up front so no reader has to discover it.

**No security claim about HQC is made here in either direction.** Claim-tier
ceiling: **toy**. `certificate.kind: none`.

---

## 1. Notation used throughout

Taken from `…/BATCH-002/tasks/TASK-20260802-15971b/a17_characterization.md` §1
and extended only where marked.

| symbol | meaning |
|---|---|
| `(T)` | true space: `x, y, r_1, r_2, e` uniform fixed-weight; `e' = x·r_2 − r_1·y + e`; `ẽ` = truncation to `N = n_e·n_2` |
| `(M)` | model space: `ẽ ~ Bernoulli(p*)^{⊗N}` (SPEC A5) |
| `n_2, d_i` | inner (duplicated Reed–Muller) length and minimum distance, `n_2 = 2 d_i` |
| `n_e, delta_e` | outer shortened-RS length over `F_256` and correction capacity |
| `m = delta_e + 1` | smallest number of symbol errors that defeats the outer decoder |
| `F_j` | indicator that inner block `j` ML-decodes to a non-zero codeword |
| `q = P[F_j = 1]` | true per-block failure probability (`q <= p_i`, `q != p_i`) |
| `mu_k` | `P[F_{j_1} = … = F_{j_k} = 1]`, well defined by Lemma L1 (exchangeability) |
| `A_k := mu_k / q^k` | **the joint-moment excess.** `A_k = 1` for all `k` iff Theorem 6.1's transfer is exact |
| `lambda := n_e·q` | expected failing blocks per ciphertext |
| `m/lambda` | **rarity ratio** — how deep in `S`'s tail the load-bearing event sits |
| `W_j` | Hamming weight of `ẽ` restricted to block `j` |
| `eps_j := (W_j − E W)/E W` | relative block-weight deviation |
| `gamma` | `Var(w(ẽ)) / (N p*(1−p*))`, the global weight dispersion ratio |
| `eta := d log q / d log p` | **elasticity** of the inner-code failure probability in the channel parameter |
| `beta := eta^2 · Cov(eps_i, eps_j)` **[new here]** | the **bridge coefficient** (HEUR-HQC-2) |
| `tau := n_e n_2 / n` | truncation/dilution ratio; HQC uses `tau ≈ 1` |

---

## HEUR-HQC-1 — Construction-family membership

### Formal statement

> Let `P(n, omega, omega_r, omega_e, n_2, dup, n_e)` denote an instance of the
> HQC concatenated construction: `x, y` uniform of weight `omega` and
> `r_1, r_2` of weight `omega_r`, `e` of weight `omega_e`, all independent and
> uniform on their fixed-weight sets in `R = F_2[X]/(X^n − 1)` with `n` prime and
> 2 primitive mod `n`; `e' = x·r_2 − r_1·y + e`; `ẽ = e'` truncated to
> `N = n_e n_2`; inner code the `[128,8,64]` Reed–Muller code duplicated `dup`
> times; outer code a shortened Reed–Solomon `[n_e, k_e, n_e − k_e + 1]` over
> `F_256`. Then, for the family of instances used by
> proposed `EXP-HQC-982268` — `dup ∈ {1,3}`, `n ∈ [8·10^3, 4.7·10^4]`,
> `omega/omega_r` fixed at `0.88`, `omega_r = omega_e`, `omega = Theta(sqrt(n))`
> (SPEC A7) — the *mechanism* generating dependence among the `F_j` is the same
> mechanism as at HQC-1/3/5, differing only through the measured quantities
> `eta`, `Var(eps)`, `Corr(eps_i, eps_j)` and `n_e`.

### Justification

Rigorous half: the two structural facts alleged to generate the dependence are
**construction facts, not parameter facts**. (i) `e'` is a single random object
shared by all `n_e` blocks — true for every member of the family. (ii) `x, y, e`
have exactly fixed weights, so block weights compete for a global budget — true
for every member. Lemma L1 (cyclic exchangeability of the `F_j`) is proved for
every member (`a17_characterization.md` §3.2), and Lemma L2 (the block-failure
event is increasing in the block's error support) is proved for every binary
linear code with minimum-distance decoding (*ibid.* §7).

Classical half: none available. There is no distribution theorem for the joint
law of Reed–Muller ML-decoder outcomes across blocks of a quasi-cyclic ring
product. **This heuristic's "rigorous-plus-classical" justification is missing
its classical half, and that gap is recorded rather than papered over.**

### Obstructions

- `dup = 1` (`n_2 = 128`, `d_i = 64`) is **not a deployed HQC inner code**. HQC
  deploys `dup ∈ {3,5}`; RMRS used `dup = 2`. `dup = 1` is the undluplicated
  base code of the same family, chosen because it is the only multiplicity at
  which `q` is large enough for high-order moments to be estimable
  (`feasibility_analysis.md` §4).
- The reduced sets have `n` 1.5× to 2× smaller than HQC-1, hence a different
  `omega`, hence a different `p*`, hence a different `eta`.
- Two-primitivity of `n` is imposed to match SPEC §4.1 but is irrelevant to the
  DFR question; it is retained only so the family is not silently altered.

### Falsification condition

The `PS-A` arm (**true HQC-1 parameters**, `dup = 3`) and the reduced arms
disagree *qualitatively* on the measured marginal diagnostics: specifically, if
`sign(Corr(W_i, W_j))` differs between `PS-A` and a majority of the reduced
sets, **or** if `gamma_hat` at `PS-A` falls outside `[0.5, 0.9]` (the
published-derived value is `0.725–0.736`, `a17_sensitivity.yaml` step 7) while
the reduced sets fall inside, the family-membership assumption is refuted for
the purposes of this contract and no reduced-set number may be read as
informative about HQC's sets.

### Validation plan

- **Sampling method**: direct sampling on (T) at every set, including `PS-A` at
  HQC-1's own `(n, omega, omega_r, omega_e, n_2, dup, n_e)`.
- **Statistics**: `p_hat` vs the analytic `p*` (Prop 6.1.2); `gamma_hat` vs the
  published-derived `0.735` at `PS-A`; `Var(W_1)` vs the binomial value
  `n_2 p(1−p)` (RMRS Remark 4.2 reports "virtually identical" at length 256);
  `Corr(W_i, W_j)` vs the exact identity
  `Var(W_total) = n_e Var(W_1) + n_e(n_e−1) Cov(W_1, W_2)`.
- **Tail checks**: the upper-tail quantiles of `w(ẽ)` at `PS-A` against SPEC
  Table 10's four published quantiles (`6169 / 6203 / 6232 / 6257` at the
  `10^-3 … 10^-6` upper tails, `N = 17664`). This is a **direct comparison
  against a published measurement** and is the strongest available check that
  the (T) sampler is generating the object HQC's own simulations generated.
- **Budget**: no extra cost — all quantities are by-products of the main arms.
- **Validation experiment ids**: `EXP-HQC-982268` (proposed).

---

## HEUR-HQC-2 — Weight-mediated dependence (the bridge)

This is the load-bearing heuristic of the whole design.

### Formal statement

> Condition on the block-weight vector `(W_0, …, W_{n_e−1})`. Then
> (a) the `F_j` are conditionally independent given `(W_j)_j`, and
> (b) the conditional failure probability of block `j` depends on the block
> through its weight only, log-linearly to the order retained:
> `log P[F_j = 1 | W_j] = log q + eta · eps_j + O(eps_j^2)`, with
> `eta = d log q / d log p` evaluated at `p = p*`, and `eps_j = (W_j − E W)/E W`.
> If in addition `(eps_j)_j` is exchangeable and jointly log-normal to the order
> retained, then for every `k <= n_e`
>
> ```
>     log A_k  =  C(k,2) · beta ,        beta := eta^2 · Cov(eps_i, eps_j)
>                                             =  eta^2 · Corr(W_i,W_j) · Var(W_1)/E[W_1]^2 .
> ```
>
> In particular `log A_k` is **proportional to `C(k,2)`** with a
> **`k`-independent constant `beta`**, and `sign(log A_k) = sign(Corr(W_i,W_j))`.

### Justification

Rigorous half:

1. `eta` is computed by exact arithmetic from **Prop 6.1.4**, a published,
   image-verified formula, differentiated numerically at
   `h = 10^-3` in `log p`. The implementation reproduces SPEC Table 11's
   published `p_i` (`-10.795 / -14.137 / -11.324` versus SPEC's printed
   `-10.79 / -14.14 / -11.30`) and matches `BATCH-002`'s independent
   recomputation to four decimals (`feasibility_analysis.md` §1).
2. `Var(W_total) = n_e Var(W_1) + n_e(n_e−1) Cov(W_1,W_2)` is an **exact
   identity** under exchangeability (Lemma L1), used with no approximation.
3. Lemma L2 gives that the block-failure event is *increasing* in the block's
   error support, so the sign of the response to a block-weight perturbation is
   determined: `eta > 0` always. Hence `sign(log A_k) = sign(Corr(W_i,W_j))` is
   forced by the mechanism, not fitted.

Classical half: the exponential-tilt / log-normal moment identity
`E[exp(sum_{j∈J} Z_j)] = exp(m sigma^2/2 + C(m,2) c sigma^2)` for an
exchangeable Gaussian vector with `Var = sigma^2`, `Cov = c sigma^2` — textbook,
no citation invented. The first-order form `A_k ≈ 1 + C(k,2) beta` is recovered
for `|C(k,2) beta| << 1`, and agrees with `a17_sensitivity.yaml` step 5's
independently derived coefficient `K = C(m,2)(1−q)/q` under
`rho = beta·q/(1−q)`.

### Obstructions — stated, because they are the reason this must be tested

- **Conditional independence given weights (clause (a)) is not proved.** `e'` is
  a product in a cyclic ring; two blocks can share algebraic structure that
  survives conditioning on their weights. This is exactly the `M+`
  (common-mode) mechanism of `a17_sensitivity.yaml` step 4, and it is
  *positive*, i.e. opposite in sign to the weight-budget term.
- **The log-linear response (clause (b)) is a first-order expansion in `eps`.**
  `eta ≈ 45.65` at HQC-1 and `Var(eps)^{1/2} ≈ 0.071`, so `eta·eps` has standard
  deviation `≈ 3.2` — **the expansion parameter is not small at HQC-1**, and the
  log-normal closure is doing real work rather than being a formality.
- **The log-normal closure is a closure, not a theorem.** `eps` is a
  standardized binomial-like weight, close to Gaussian in the bulk and not in
  the tail; the deep-tail regime is precisely where `mu_m` lives at HQC's
  parameters.
- Evaluated at HQC-1 with the published-derived `gamma = 0.735` this model
  returns `|C(16,2)·beta| = 7.45`, i.e. **the linearization of its own output is
  invalid there** (`feasibility_analysis.md` §6). That is recorded as a property
  of the model, not suppressed.

### Falsification condition

Any one of the following, measured on space (T) with `NULL-A` passing:

- **F2a (shape).** `log A_hat_k / C(k,2)` varies by more than a factor 2 across
  `k ∈ [2, k_max]` at half or more of the parameter sets with `k_max >= 6`.
- **F2b (magnitude).** The fitted `beta_hat` (weighted least squares of
  `log A_hat_k` on `C(k,2)` through the origin) differs from the predicted
  `beta = eta^2 · Corr_hat(W_i,W_j) · Var_hat(W_1)/E_hat[W_1]^2` by more than a
  factor 2 at half or more of the sets.
- **F2c (mediation).** The `CTRL-WBP` arm — the identical measurement after an
  independent uniformly random permutation of the coordinates **inside each
  block**, which preserves every `W_j` exactly and destroys all within-block
  positional structure — changes `log2 A_hat_k` by more than
  `3·SE_combined` at any `k <= k_max` at half or more of the sets. Then the
  dependence is **not** weight-mediated and clause (a) is false.

**Any of F2a/F2b/F2c refutes HEUR-HQC-2, and a refuted HEUR-HQC-2 forbids every
downstream evaluation at HQC's parameters.** That prohibition is written into
proposed `EXP-HQC-982268` `stopping_rules` ST-6.

### Validation plan

- **Sampling**: `PS-A` (`k = 2`, and `k = 3` if `q_hat` permits), `PS-B`,
  `PS-C`, `PS-D` on (T); `CTRL-WBP` at `PS-C`.
- **Statistics**: `log2 A_hat_k` for `k = 2 … k_max` per set; the WLS fit of
  `beta_hat`; the ratio `beta_hat / beta_pred`.
- **Tail checks**: the largest `|log2 A_hat_k|` over all (set, `k`) against the
  Gumbel prediction for the maximum of that many standardized `NULL-A`
  deviations, using the *empirical* `NULL-A` standard deviations.
- **A-priori predicted effect sizes** (`feasibility_analysis.md` §6, evaluated at
  an assumed `gamma = 0.70` for the reduced sets — the run measures `gamma`):
  `log2 A_m = −0.42` (`PS-B`, `m=6`), `−1.02` (`PS-C`, `m=16`),
  `−0.61` (`PS-D`, `m=20`), `−0.090` (`PS-A`, `k=2`), against per-set
  `SE ≈ 0.002–0.045` bits. **The predicted effect is 5σ to 300σ**, so the test
  discriminates.
- **Budget**: this is the main experiment; see §7 of the specification.

---

## HEUR-HQC-3 — Rarity-regime transfer

**This is the weakest link in the chain and it is named as such.**

### Formal statement

> The bridge coefficient `beta` of HEUR-HQC-2 is a function of
> `(eta, Var(eps), Corr(eps_i, eps_j))` alone and **does not depend on the
> rarity ratio `m/lambda`**. Consequently a `beta_hat` measured at a set with
> `m/lambda ∈ [0.8, 15]` is the same `beta` that governs `log A_k` at a set with
> `m/lambda ∈ [600, 5500]`, which is where HQC-1/3/5 sit.

### Justification

Within the log-normal closure of HEUR-HQC-2 this is *exact*: `beta` is built
from second moments of the latent `eps` and from `eta`, none of which references
`m` or `lambda`. The rarity ratio enters `A_k` only through `C(k,2)`.

There is **no rigorous half and no classical half**. The statement is a property
of the closure, and the closure is what is in doubt.

### Obstructions

- The regime `m/lambda ≈ 1` (reachable) and `m/lambda ≈ 600` (HQC-1) are
  qualitatively different events: at the former, `{S >= m}` is a typical
  configuration; at the latter it is a `~10^-40` tail event. A closure fitted in
  the bulk is being asked to predict the far tail — the classic failure mode of
  moment closures.
- `a17_sensitivity.yaml` step 6 states the exact obstruction in its own terms:
  *"a joint law can have `rho ≈ 0` while `mu_m >> q^m`, if the dependence lives
  in a rare configuration in which many blocks fail together."* A rare
  many-blocks-fail configuration is by construction invisible at
  `m/lambda ≈ 1`, because there every configuration is common.

### Falsification condition

`beta_hat` varies systematically with `lambda`: specifically, across the sets
`PS-B` (`lambda ≈ 0.4–3.1`), `PS-C` (`2.7–19.6`) and `PS-D` (`7.7–49.1`), after
dividing out each set's own `eta^2 · Corr_hat(W_i,W_j) · Var_hat(eps)`, the
residual ratio `beta_hat / beta_pred` shows a monotone trend in `log lambda`
whose ordinary-least-squares slope has magnitude `>= 0.15` per e-fold with a
95% interval excluding zero.

### Validation plan

- **Sampling**: the `lambda` ladder is built into the set list — `PS-B`, `PS-C`,
  `PS-D` span `lambda` over roughly two orders of magnitude at fixed inner code
  (`dup = 1`) and near-fixed `tau`.
- **Statistics**: `beta_hat/beta_pred` versus `log lambda`, with jackknife
  errors.
- **Tail checks**: at the set with the largest reachable `k_max`, compare the
  measured `log A_hat_k` at the *largest* `k` against the extrapolation of the
  `C(k,2)` law fitted on `k <= k_max/2` only. A break at large `k` inside the
  measured range is the strongest available in-range warning that the closure
  fails deeper in the tail.
- **Budget**: no extra cost; it is a re-analysis across the existing arms.
- **HONEST LIMIT**: the ladder spans `m/lambda ∈ [0.8, 15]`. HQC-1 sits at
  `618`. **The ladder therefore tests HEUR-HQC-3 over 1.3 decades and applies it
  over 2.6 more.** Passing the test does not validate the extrapolation.

---

## HEUR-HQC-4 — Truncation/dilution scaling of the weight budget

### Formal statement

> The negative component of `Corr(W_i, W_j)` is generated by the exactly-fixed
> weights of `x, y, e` competing for a global budget, and dilutes as the
> retained window shrinks relative to the ambient ring: for the fixed-weight
> component alone, restricting a weight-`W` vector in `n` coordinates to a
> window of `N` coordinates gives a hypergeometric weight with dispersion factor
> `(n − N)/(n − 1) = 1 − tau + O(1/n)`. Hence `|Corr(W_i, W_j)|`, and therefore
> `|log A_k|` at fixed `k`, is **non-increasing in `tau`**, and HQC's own
> `tau ≈ 1` (`17664/17669 = 0.99972` at HQC-1) is the *maximally
> budget-constrained* member of the family.

### Justification

Rigorous half: the hypergeometric variance formula
`Var = N p (1−p)(n − N)/(n − 1)` is exact and classical, and applies verbatim to
the `e` summand of `e'`.

Classical half: none for the product terms `x·r_2` and `r_1·y`, whose window
restriction is **not** hypergeometric. Indeed the published `gamma ≈ 0.735` at
`tau ≈ 1` is far above the `1 − tau ≈ 0` the fixed-weight component alone would
give, so the products contribute over-dispersion and the net `tau`-dependence is
**not predicted quantitatively by this heuristic** — only its *direction* is.

### Obstructions

- Only the direction is predicted. A measured `gamma(tau)` curve is a new
  observation, not a check of a formula.
- Holding `p*` fixed while `tau` decreases forces `omega ∝ sqrt(n)` to grow,
  which changes `omega_e/n` slightly and changes nothing else materially; the
  contract recomputes `p*` exactly per set so the comparison is at matched `p*`
  to 3 decimals (`0.3373 / 0.3416 / 0.3407` across `tau = 1 / 1/2 / 1/4`).

### Falsification condition

`|log2 A_hat_k|` at fixed `k` fails to be non-increasing along
`PS-C (tau=0.9975) → PS-C2 (0.4997) → PS-C4 (0.2499)` by more than
`3·SE_combined` at any `k <= min(k_max)` across the three.

**Resolution of the ambiguous case, pre-registered** (this is the
`docs/inventor-protocol.md` §3 structural tell, and it has two readings that must
be separated *before* any number exists): non-decay is **either** an estimator
artifact **or** a dependence mechanism that is not weight-budget-mediated.
`CTRL-WBP` discriminates: if `CTRL-WBP` preserves the signal, the dependence is
weight-mediated and non-decay contradicts HEUR-HQC-4 itself; if `CTRL-WBP`
destroys the signal, the dependence is positional (the `M+` mechanism) and
HEUR-HQC-2 clause (a) is refuted instead. Either outcome is recorded as a
resolved finding with its mechanism, never as a bare flag.

### Validation plan

- **Sampling**: `PS-C`, `PS-C2`, `PS-C4` at matched `(n_e, n_2, p*)` and
  `tau = 0.9975 / 0.4997 / 0.2499`.
- **Statistics**: `gamma_hat(tau)`, `Corr_hat(W_i,W_j)(tau)`,
  `log2 A_hat_k(tau)` at fixed `k`.
- **Tail checks**: `gamma_hat` at `PS-C` against the published-derived
  `0.61–0.74` range (`a17_sensitivity.yaml` step 7).
- **Budget**: 700 core-seconds per rung (`feasibility_analysis.md` §7); these
  are the first arms cut if the cap binds.

---

## HEUR-HQC-5 — Elasticity validity

### Formal statement

> The elasticity of the **true** per-block failure probability,
> `eta_true = d log q / d log p`, is equal to the elasticity of the **published
> upper bound**, `eta = d log p_i / d log p` computed from Prop 6.1.4, to within
> a factor `1 ± 0.20`, uniformly over the parameter sets used.

### Justification

Rigorous half: `q <= p_i` is proved on space (M) by Prop 6.1.4 (SPEC pp.36–38).
The *level* gap is measured by the sources themselves: SPEC Table 11 gives
`0.17 / 0.25 / 0.18` bits at NIST-1/3/5, RMRS Table 4 gives `0.19 / 0.31 / 0.05`
bits between its improved bound and its observed DFR. A gap that is nearly
constant across `p` is a gap with **zero elasticity**, which is precisely the
condition under which `eta_true = eta`.

Classical half: none. The observation that the bound-to-truth gap is roughly
constant rests on six published points across two documents.

### Obstructions

- `eta` enters `beta` **squared**. A 20% error in `eta` is a 44% error in
  `beta`, which is within — but not comfortably within — the factor-2 tolerance
  of falsification condition F2b.
- The published gaps are measured at `dup ∈ {2,3,5}`; the reduced sets use
  `dup = 1`, where the bound is far looser (`feasibility_analysis.md` §2 gives a
  bracket width of `2.07–2.90` bits at `d_i = 64` versus `0.70–1.63` bits at
  `d_i = 320`).

### Falsification condition

The empirical elasticity, obtained by regressing `log q_hat` on `log p_hat`
across the parameter sets that share an inner code, differs from the analytic
`eta` by more than 20% at half or more of the inner codes tested.

### Validation plan

- **Sampling**: Stage A measures `q_hat` and `p_hat` at every set. `PS-B`
  (`p* = 0.3000`), `PS-C` (`0.3373`), `PS-D` (`0.3582`), `PS-C2` (`0.3416`),
  `PS-C4` (`0.3407`) share `dup = 1`, giving five points spanning
  `p* ∈ [0.30, 0.36]` — enough for a two-parameter fit with a residual check.
- **Statistics**: `d log q_hat / d log p_hat` by weighted least squares, versus
  `eta` at each `p*`.
- **Tail checks**: `q_hat` must lie inside the a-priori bracket
  `[q_deCaen, p_i(6.1.4)]` at **every** set. The bracket is validated in
  `feasibility_analysis.md` §2 against all three published observed inner DFRs
  (it contains `-10.96 / -14.39 / -11.48`); a `q_hat` outside it at any set is an
  implementation defect (invalidation rule INV-Q).
- **Budget**: Stage A, 240 core-seconds total.

---

## HEUR-HQC-6 — Inner-code multiplicity transfer

### Formal statement

> A bridge coefficient measured at duplication multiplicity `dup = 1`
> (`n_2 = 128`, `d_i = 64`) predicts the bridge coefficient at HQC's
> multiplicities `dup ∈ {3, 5}` (`n_2 ∈ {384, 640}`) through the substitution of
> that multiplicity's own `eta`, `Var(eps) = (1−p)/(n_2 p)` and
> `Corr(W_i,W_j)`, with no additional multiplicity-dependent term.

### Justification

Rigorous half: SPEC's own A11 transfers Prop 6.1.3/6.1.4 across multiplicities
by substituting `d_i` and `n = 2 d_i`, and the transfer reproduces Table 11's
values at `dup = 3` and `dup = 5`; so the *marginal* is known to transfer this
way. `Var(eps) = (1−p)/(n_2 p)` is the exact binomial value and is the only
place `n_2` enters `beta` besides `eta`.

Classical half: none for the joint law.

### Obstructions

Duplication changes the decoder's geometry, not just its length: the folded
statistic sums `dup` independent copies before the Hadamard transform, so a
block's failure depends on the *distribution of its errors across copies*, not
only on its total weight. That is a multiplicity-dependent departure from
clause (b) of HEUR-HQC-2 and it is not bounded here.

### Falsification condition

`beta_hat` at `PS-A` (`dup = 3`, true HQC-1 parameters, measured at `k = 2` and,
if `q_hat` permits, `k = 3`) differs by more than a factor 2 from
`eta^2 · Corr_hat(W_i,W_j) · Var_hat(eps)` computed from `PS-A`'s **own**
measured inputs.

Note this is a *within-`PS-A`* consistency test and therefore does **not**
require a matched `dup = 1` twin; it tests whether the bridge formula holds at
`dup = 3` at all. It is the only multiplicity check the budget affords.

### Validation plan

- **Sampling**: `PS-A`, 4000 core-seconds, `T ≈ 3.9·10^7`.
- **Statistics**: `log2 A_hat_2` against the prediction `C(2,2)·beta/ln2`.
  Derived `SE(log2 A_hat_2) = 0.016–0.045` bits versus a predicted
  `−0.090` bits — a 2σ to 5.6σ test at `k = 2` alone.
- **Tail checks**: `log2 A_hat_3` where reachable; the ratio
  `(log A_hat_3/3)/(log A_hat_2/1)` must be 1 under the bridge, and this is the
  **only shape test available at HQC's own parameters**.
- **Budget**: included in the main allocation.

---

## HEUR-HQC-7 — Order extrapolation (regularity in `k`)

**This heuristic is not validatable at `k = 16` by this contract, at HQC's
parameters, at any budget this campaign can command.**

### Formal statement

> There is no order threshold `k*` in `(k_max, m]` at which a new mechanism
> switches on: the law `log A_k = C(k,2)·beta` fitted on `k ∈ [2, k_max]`
> continues to hold for `k ∈ (k_max, m]`.

### Justification

Rigorous half: **none.** `docs/claims-and-verification.md` requires a rigorous
bound plus a classical distribution law; neither exists here, and the
requirement is recorded as unmet.

Classical half: within the log-normal closure the identity is exact in `k`, so
the heuristic is a restatement of the closure rather than an independent
assumption. That is a weakness, not a strength: it means HEUR-HQC-7 and
HEUR-HQC-2 fail together, and a test of HEUR-HQC-2 at low `k` cannot separate
them.

### Obstructions — this is the campaign's own headline obstruction

`EV-HQC-6fd5b1` **O-6** and `DEC-20260802-9664c6` **D-6** state exactly this
gap: *`mu_m` is not determined by `mu_2`*, so no finite set of low-order moments
determines `mu_16`. `a17_sensitivity.yaml` step 6 gives the counterexample
shape. **HEUR-HQC-7 is the assumption that O-6's counterexample shape does not
occur in this particular family** — and the proposed experiment measures more
orders than any published work but still stops far below 16 at HQC's own
parameters.

The `proof_search_map.observation_collision` audit of the proposed hypothesis
**fails** on exactly this point, and the failure is recorded there as the audit's
outcome rather than argued away.

### Falsification condition

Any departure from `C(k,2)` proportionality **within** the measured range —
i.e. falsification condition F2a — refutes HEUR-HQC-7 as well. There is **no
condition available that could confirm it beyond `k_max`.**

### Validation plan

- **What is possible**: push `k_max` as high as the budget allows at reduced
  parameters (`k_max` is projected at `9–21` at `PS-C` and `13–34` at `PS-D`,
  depending on where `q_hat` lands in its bracket), and test the law over that
  range. At `PS-D` with a favourable `q_hat`, `k_max` may exceed `20`, which
  would be the first test of the law past HQC-1's own `m = 16` **at any
  parameters**.
- **What is not possible**: testing it at `k = 16` at HQC-1's own `(n_e, q)`.
  The derived sample requirement is `T = 2.66·10^42`
  (`feasibility_analysis.md` §3), against an affordable `T ≈ 10^8`.
- **Named successor if this matters more than the budget allows**: an exact or
  importance-sampled computation of `mu_k` under a *tilted* (T) sampler that
  conditions on `S >= k`, which would trade unbiasedness for tail reach. That is
  a different instrument, it is not designed here, and it is named so the gap
  carries a successor rather than a shrug.

---

## HEUR-HQC-8 — Sampler equivalence

### Formal statement

> Results obtained with the **uniform** fixed-weight sampler
> `SampleFixedWeightVect$` transfer to HQC as deployed, which uses the **biased**
> `SampleFixedWeightVect`, up to the factor SPEC §6.2.3 already charges,
> `(tau_max^{omega_r})^3 <= 1.00045` at NIST-1.

### Justification

Rigorous half: SPEC A22 — the §6.1 analysis and the §6.2.1–6.2.2 proofs
*themselves* assume the uniform sampler, and §6.2.3 charges the deployed
sampler separately via Lemma 6.4 and Table 12. So using the uniform sampler
matches the object Theorem 6.1 is about, exactly.

Classical half: not applicable — this is a scope alignment, not a distributional
claim.

### Obstructions

SPEC's `(tau_max^{omega_r})^3` factor is charged against the **DFR**, a scalar.
Nothing in either source charges it against a **joint moment**, and a bias that
correlates coordinate positions across blocks would not be captured by a scalar
multiplier.

### Falsification condition

Out of scope for this contract; nothing measured here can falsify it.

### Validation plan

**None, and that is declared rather than left blank.** Named successor: a
paired arm running the deployed `SampleFixedWeightVect` at `PS-C` and comparing
`log2 A_hat_k`, which is a bounded, well-defined follow-on task requiring only
a second sampler implementation. This contract does **not** run it, and no
statement about deployed HQC may be made without it.

---

## 2. Dependency graph — what any given claim costs

| claim | heuristics it is conditional on |
|---|---|
| `log2 A_hat_k` at a reduced set, `k <= k_max` | **none** — a scoped measurement |
| `log2 A_hat_2` (and `_3`) at true HQC-1 parameters | **none** — a scoped measurement at HQC-1's own `(n, omega, omega_r, omega_e, n_2, dup, n_e)` |
| "the dependence is weight-mediated" | 2 |
| "`beta` measured at reduced rarity is HQC's `beta`" | 1, 2, 3, 5 |
| "`beta` at `dup = 1` predicts `dup = 3/5`" | 1, 2, 5, 6 |
| **anything at all about `A_16` at HQC-1/3/5** | **1, 2, 3, 5, 6, 7** |
| anything about HQC **as deployed** | 1, 2, 3, 5, 6, 7, **8** |

The last two rows are the ones that matter and they are the ones with the
longest conditions. A downstream record that states a number for `A_16` at
HQC-1 without rendering "conditional on HEUR-HQC-1, -2, -3, -5, -6, -7" is
asserting above its record.

---

## 3. Scope limits of this document

- These heuristics are **proposed**. Only a Coordinator ledger archive creates
  `H-HQC-18d1b4` and `EXP-HQC-982268`; nothing here is official.
- **No measurement was performed by this task.** Every number is either
  transcribed from a published table, recomputed by exact arithmetic from a
  published formula, derived symbolically here, or — for the two machine
  constants — obtained from `CALIB-M0`, a generic synthetic-kernel benchmark
  that touches no HQC object (`feasibility_analysis.md` §7.1).
- **No security claim about HQC in either direction.** Claim tier **toy**;
  `RQ-HQC-001.claim_tier_ceiling` makes that ceiling more binding for a
  standardized algorithm, not less.
- Not admissible toward the `AGENTS.md` rule 13 closure quorum.
