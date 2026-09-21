# Feasibility of measuring the joint moment `mu_{delta_e+1}` on space (T)

**Task**: `TASK-20260803-c470c0` (executor) · **Batch**: `BATCH-003` ·
**Goal**: `GOAL-HQC-001` · **Question**: `RQ-HQC-001`
**Produced**: 2026-08-03 · **Branch**: `claude/goal-target-hqc-launch-vndegi`
**Repo commit at start**: `6dc0040e24a5180d69ac5bef48b60f4d7c012bcc`
(tree clean except the sibling task's own untracked directory
`…/tasks/TASK-20260803-6f50df/`, which this task did not create and did not read)

**Predecessor**: `TASK-20260802-853bad`, terminated by an API session limit — an
**infrastructure failure**, never evidence about the mathematics (AGENTS.md
rule 5). Its one surviving artifact (`heuristics.md`) was read. **Nothing in it
is carried forward unverified**; every number below is re-derived here, and
where this document disagrees with it the disagreement is recorded in §12.4.

**Inference**: `requested_policy: executor-implementation`,
`resolved_model_id: claude-opus-5`, `fallback_used: true`,
`model_verified: false`, `independent_session: true`.

**Claim tier: toy.** `certificate.kind: none`. **No security claim about HQC is
made here in either direction.** No HQC object was sampled, no decoding trial
was run, no confirmatory measurement was executed (`runs_authorized: 0`). Every
number below is one of: transcribed from a published table; recomputed by exact
arithmetic from a published formula; derived symbolically here; or a **machine
throughput measured by a generic non-HQC microbenchmark** (§9.1, labelled).

---

## 0. Verdict, stated before the argument so it cannot be mis-summarised

| question | verdict |
|---|---|
| Can `mu_{16}` be measured on (T) at **HQC-1's own parameters**? | **NO. `T_req = 3.4e41` trials (§5), against an affordable `~1e8` — a shortfall of 33 orders of magnitude.** This is not a budget complaint: the direct estimator of `mubar_m` costs `~1/DFR` samples, and the DFR is below `2^-128`. |
| Can `mu_2`, `mu_3` be measured on (T) at **HQC-1's own parameters**? | **YES.** `T = 1e8` gives `SE(log2 A_2) = 0.0092` bits and `SE(log2 A_3) = 0.108` bits, at `3.3e4` core-seconds (§8). No published work measures **any** joint block moment; this would be the first. |
| Can `mu_m` be measured at **`m = 16, 17, 30` — HQC's own orders — with one reduced knob**? | **YES.** Set the Reed–Muller duplication multiplicity to `dup = 1` and change **nothing else**: same `n_e`, same `m`, same `p*`, same `omega/sqrt(n)` regime, same construction. `T_req = 2.9e7 / 3.1e5 / 2.7e6` (§6, §8). |
| Is there a **ladder** between the two? | **NO, and this is the sharpest negative finding here.** The duplication ladder has exactly two rungs: `dup = 1` (feasible, `3.4e3` core-s) and `dup = 2` (`3.2e20` core-s). §6.3. There is no intermediate parameter at which the measurement is affordable. |
| Total cost of the recommended design | **`5.58e4` core-seconds modeled** (`6.25e4` with the optional dilution ladder): 8 mandatory runs, each capped at `3600 s` wall on `<= 4` cores, `< 1 GB` peak RSS. Inside "roughly 2 batches of compute". §9.3. |
| Biggest threat to validity | **The rarity gap.** The design matches the moment **order** `m` exactly and misses the **rarity ratio** `m/lambda` by a factor `~840` at HQC-1 (`1.5` measured vs `1264` at HQC-1's `dup = 3`). Every statement about HQC's own sets is conditional on `HEUR-HQC-3` (rarity transfer), which the design tests over **0.33 decades** (`m/lambda` from `0.70` to `1.51`) and applies over **2.9 more**. §12.1. |

**What this means operationally.** The A17 question is **decidable by a
measurement this program can afford — but not at HQC's own parameters, and not
without one named, tested-only-in-part heuristic.** That is a more useful answer
than either "feasible" or "infeasible" alone, and it is stated as such rather
than rounded to whichever is more convenient.

---

## 1. The estimand, stated exactly — and a correction to the inherited derivation

### 1.1 Notation (from `a17_characterization.md` §1)

`n_e` outer blocks; `n_2 = 128 * dup` bits per block; `d_i = 64 * dup`;
`N = n_e * n_2`; `n` = ambient ring length; `ẽ` = `e' = x·r_2 - r_1·y + e`
truncated to `N` coordinates (A23); `F_j = 1{D_i(ẽ^{(j)}) != 0}`;
`S = sum_j F_j`; `q = P[F_j = 1]`; `m = delta_e + 1`;
`lambda = n_e q`; `tau = N/n`.

### 1.2 The inherited derivation asserts more than it proves — and the fix

`a17_characterization.md` Lemma L1 concludes that the `F_j` are
**"exchangeable, hence identically distributed"**. The argument given is cyclic
shift invariance of the law of `e'`. **That argument yields identical
*marginals* and *translation* invariance of the joint law, not exchangeability.**

Concretely: let `sigma` be the cyclic shift on the ring of length `n`. Applying
`sigma^{s*n_2}` maps block `B_j` to `B_{j+s}` **only when `0 <= j+s <= n_e-1`**;
block `B_{n_e-1}` maps outside the retained window. So what is proved is

> for every `J subset {0..n_e-1}` and every shift `s` with `J+s subset {0..n_e-1}`,
> `P[AND_{j in J} F_j = 1] = P[AND_{j in J+s} F_j = 1]`.

This gives equality of marginals (singletons; used below, and correct), and it
makes `mu^{(J)}` a function of the **difference pattern** of `J` only. It does
**not** give `P[F_0 = F_1 = 1] = P[F_0 = F_5 = 1]`, which full exchangeability
would require and which is not proved anywhere.

**This discrepancy is resolved, not flagged** (`DEC-20260802-9664c6` D-7). The
resolution is that **exchangeability was never needed**, because the object that
enters the DFR is the *aggregate*, not any single `mu^{(J)}`:

> **Definition.** `M_k := sum_{|J|=k} P[AND_{j in J} F_j = 1] = E[C(S,k)]`, and
> `mubar_k := M_k / C(n_e,k)` — the **average `k`-way joint failure
> probability** over all `C(n_e,k)` index sets.

> **Lemma F1 (exact; no independence, no exchangeability).** Jordan's
> inclusion–exclusion inversion gives, exactly,
> `P[S >= m] = sum_{k=m}^{n_e} (-1)^{k-m} C(k-1,m-1) C(n_e,k) * mubar_k`.

*Proof.* Jordan's identity `P[S >= m] = sum_{k>=m} (-1)^{k-m} C(k-1,m-1) S_k`
with `S_k = sum_{|J|=k} P[AND_J]` is standard Bonferroni inversion and needs no
distributional assumption. Substituting `S_k = C(n_e,k) mubar_k` gives the
statement. ∎

Setting `mubar_k = q^k` for all `k` recovers Theorem 6.1's binomial tail
exactly. **Therefore the entire content of A17, for the DFR, is the family of
statements `mubar_k = q^k`, `k = m .. n_e`.** `mubar_k`, not any single
`mu^{(J)}`, is the quantity to estimate — and it is the quantity the estimator
below estimates without bias.

If one *does* assume exchangeability, `mubar_k = mu_k` and this reduces to
BATCH-002's step 1 verbatim. So the correction strictly generalises the
inherited derivation; it removes an unproved premise and changes no number.

**Primary estimand.**

```
A_k  :=  mubar_k / q^k ,      k = 2 .. m .        A_k = 1 for all k  <=>  A17 holds on (T).
```

To leading order (`a17_sensitivity.yaml` step 2: the `l = m` term carries
99.90 % / 99.99 % / 99.92 % of the Theorem 6.1 tail at HQC-1/3/5) the DFR
distortion is `A_m`, and `log2 A_m` is the bit movement of Theorem 6.1's number.

### 1.3 The estimator

```
qhat      = (1/T) sum_t S_t / n_e                        (unbiased for q)
mubarhat_k = (1/T) sum_t C(S_t, k) / C(n_e, k)           (unbiased for mubar_k)
Ahat_k     = mubarhat_k / qhat^k
```

`E[C(S,k)] = E[sum_{|J|=k} prod_{j in J} F_j] = sum_J mu^{(J)} = C(n_e,k) mubar_k`
by linearity alone. **The empirical distribution of `S` is a sufficient
statistic for every `mubar_k`.** Three consequences that matter:

1. **The outer Reed–Solomon code is never implemented.** It enters only as the
   label `m = delta_e + 1`. All `mubarhat_k` come from one histogram of `S`.
2. Every `k` from `2` to `n_e` is obtained from the same trials at zero extra
   cost. The experiment measures a *curve in `k`*, not a point.
3. `Ahat_k` is a ratio and therefore mildly biased; the contract uses a
   delta-method/jackknife correction and reports the jackknife SE, not the
   model SE (§3.4).

---

## 2. Variance of the estimator — derivation shown

Sizing is done under the **null being tested** (A17: `S ~ Binomial(n_e, q)`);
this is the correct convention for a pre-registered power calculation, and §3.4
requires the *empirical* variance to be used at analysis time.

Write `nu_k := C(n_e,k) q^k = E[C(S,k)]` under the null.

```
E[C(S,k)^2] = sum_{J,J'} P[all of J u J' fail]
            = sum_{i=0}^{k}  #{(J,J'): |J n J'| = i} * q^{2k-i}
            = C(n_e,k) * sum_{j=0}^{k} C(k,j) C(n_e-k, j) q^{k+j}          (j = k-i)
```

*(the count of ordered pairs with intersection `i` is
`C(n_e,k) C(k,i) C(n_e-k, k-i)`; re-index `j = k-i`).*

**Verification of this closed form (deterministic, no randomness):** evaluated
against the direct sum `sum_s P[S=s] C(s,k)^2` at `(n_e,q,k) =
(12,0.3,3), (20,0.15,5), (46,0.2,7)`; relative differences `3.2e-61`,
`1.5e-61`, `1.3e-60` at 60-digit precision. Identity confirmed.

Hence the **relative variance per trial**

```
V(n_e,q,k) := Var(C(S,k)) / E[C(S,k)]^2
            = [ sum_{j=0}^{k} C(k,j) C(n_e-k,j) q^{k+j} ] / (C(n_e,k) q^{2k}) - 1
```

and, since `Var(log Ahat_k) ≈ V/T` to first order (the `qhat^k` term contributes
`k^2 * V(n_e,q,1)/T`, which is smaller by a factor `>= 10^3` at every cell used
here and is carried in the contract but omitted from the sizing formula):

```
                       sqrt( V(n_e,q,k) / T )
SE( log2 Ahat_k )  =   ----------------------                                (*)
                              ln 2
```

**Sanity check of (*) in the deep tail.** For `k >> lambda` the `j=0` term
dominates, `V ≈ 1/nu_k ≈ 1/P[S >= k]`, so `T_prec ≈ 1/(P[S>=k] (eps ln2)^2)`:
**the number of trials needed to measure `mubar_m` to `eps` bits is of order
`1/DFR`.** That single sentence is the whole of §5.

---

## 3. Two feasibility criteria, both pre-registered

### 3.1 C1 — precision

```
T_prec(eps) = V(n_e,q,k) / (eps * ln 2)^2 ,      eps in bits.
```
Throughout, `eps = 0.5` bits unless stated.

### 3.2 C2 — anti-jackpot (variance completeness)

`C(S,k)` is a **heavily right-skewed** summand: a single trial with `S` well
above `k` contributes `C(S,k)` which can exceed the mean by many orders. A
Gaussian SE computed from `(*)` is **meaningless** unless the `S`-range that
carries the estimand's mass is actually sampled. So:

```
s_90   := smallest s with  sum_{s'<=s} P[S=s'] C(s',k)  >=  0.90 * E[C(S,k)]
T_stab := 30 / P[S >= s_90]                (at least 30 trials in the top decile
                                            of the estimand's mass)
T_req  := max(T_prec, T_stab)
```

**C2 is the binding criterion at every cell examined here.** Omitting it is the
single easiest way to produce an optimistic sample-size number, and the
predecessor's surviving artifact contains no such criterion. A red team asking
"is your feasibility arithmetic optimistic?" should check this line first: with
C1 alone, `mu_16` at `n_e=46, q=0.10` would be quoted at `1.9e9` trials; with C2
it is `5.3e10`, a factor **28** worse.

### 3.3 Why `T_stab` is not conservative theatre

At `n_e = 46, q = 0.20, k = 16`: `T_prec = 1.55e6` but `s_90 = 25`, and
`P[S >= 25] = 2.7e-7`. With `T = 1.55e6` trials the *expected number of trials
in the range carrying 90 % of the estimand* is `0.4`. The realised estimator
would be a coin flip on whether one jackpot trial appears, and its reported SE
would understate its error by orders of magnitude. `T_stab = 1.12e8` is the
honest number.

### 3.4 Analysis-time variance

`(*)` sizes the experiment; it does **not** report it. The contract requires the
reported SE to be a **jackknife over 200 contiguous trial batches**, and
requires the run to be flagged if the jackknife SE exceeds `2x` the model SE
(evidence of dependence-inflated variance, itself an observation worth
recording).

---

## 4. Verification legs — every published number this analysis touches, reproduced

All by exact/60-digit arithmetic on the **image-verified** transcriptions in
`dfr_model_transcription.md`. No value is taken on trust.

| leg | computed here | published / prior | agreement |
|---|---|---|---|
| `p*` (Prop 6.1.2) at HQC-1/3/5 | `0.339788 / 0.361804 / 0.372489` | SPEC Tables 9, 11: `0.3398 / 0.3618 / 0.3725` | exact to 4 dp |
| `log2 p_i` (Prop 6.1.4) | `-10.7950 / -14.1374 / -11.3240` | SPEC Table 11 prints `-10.79 / -14.14 / -11.30`; BATCH-002 recomputed `-10.795 / -14.137 / -11.324` | exact to BATCH-002's digits |
| `log2 p_i` (Prop 6.1.3) | `-10.1312 / -13.6690 / -10.7638` | — | — |
| **A19 gap** `m *` (6.1.4 − 6.1.3) | `16*0.664 = 10.62`, `17*0.468 = 7.96`, `30*0.560 = 16.79` bits | BATCH-002 / red team: `10.61 / 7.96 / 16.79` | **independent reproduction** |
| SPEC Table 10 **binomial** column, Gaussian interpolation | `6196.8 / 6236.3 / 6270.7 / 6301.5` | printed `6197 / 6237 / 6272 / 6301` | `<= 1.3` out of `~6250` |
| implied `gamma` from Table 10's **error-vector** column | `0.7350 / 0.7355 / 0.7325 / 0.7249` | BATCH-002 step 7: `0.735 / 0.736 / 0.733 / 0.725` | **independent reproduction** |
| Var-identity of §2 | rel. diff `<= 1.3e-60` | — | closed form confirmed |

The Table 10 leg is worth stating twice: the Gaussian interpolation reproduces
the **exactly-computable binomial column** to `+-1.3`, which validates the
*method*, and only then is it used on the error-vector column to extract
`gamma`. That is why `gamma = 0.735 +- 0.01` is usable as a **pre-registered
tail check on the (T) sampler** (§10.2, D4).

---

## 5. INFEASIBLE: `mubar_m` at HQC's own parameters

Take `q` at its published upper bound `p_i` (Prop 6.1.4); the true `q` is
smaller and every number below then gets **worse**, so this is the optimistic
end.

| set | `n_e` | `m` | `q = p_i` | `lambda = n_e q` | `m/lambda` | `P[S>=m]` (A17 model) | `T_req` |
|---|---|---|---|---|---|---|---|
| HQC-1 | 46 | 16 | `5.588e-4` | `0.0257` | **621** | `8.82e-41` | **`3.40e41`** |
| HQC-3 | 56 | 17 | `5.551e-5` | `0.00311` | **5470** | `4.41e-59` | **`10^59.8`** |
| HQC-5 | 90 | 30 | `3.901e-4` | `0.0351` | **854** | `3.57e-79` | **`10^79.9`** |

At `1e4` trials/second/core — about `3.3x` faster than the modeled PS-A cost of
§9 — `3.40e41` trials is `3.4e37` core-seconds, or `1.1e30` core-years. This is
not a budget statement; it is the identity `T_req ≈ 1/DFR` of §2 evaluated at a
DFR the specification designed to be below `2^-128`.

**Corollary, stated plainly.** *No* Monte-Carlo scheme that samples (T)
unconditionally and forms an unbiased estimate of `mubar_m` can measure A17's
failure at HQC's standardized parameters, at any budget any organisation
commands. The obstruction is the same one that makes the DFR unmeasurable, and
it is why the design below changes a parameter. Named successors that could
attack this directly are in §11.

---

## 6. The reduction family: one knob, and it has only two settings

### 6.1 Choice of knob, and why this one

The construction has four reducible knobs: the outer length `n_e`, the outer
correction capacity `delta_e` (hence `m`), the channel `p*` (via
`omega, omega_r, omega_e`), and the inner **duplication multiplicity `dup`**
(`n_2 = 128*dup`, `d_i = 64*dup`).

The design reduces **`dup` alone**, because:

- **`m` must not be reduced.** `EV-HQC-6fd5b1` O-6 states that `mu_m` is not
  determined by `mu_2`; a design that lowers `m` measures precisely the quantity
  O-6 says is uninformative. Holding `n_e` and `m` at HQC's own values removes
  the order-extrapolation step entirely from the chain for the reduced arms.
- **`p*` must not be raised.** Raising `omega, omega_r` to raise `p*` pushes the
  channel toward `p* = 1/2`, where `e'` approaches uniform, `gamma -> 1`, and
  **the dependence being measured vanishes by construction**. That would bias
  the result toward `A_k = 1` — toward *falsely confirming* A17. The design
  therefore holds `p*` at the level's own published value, and §10.2 makes
  `gammahat` a pre-registered guard against this failure mode anyway.
- **`dup` is a parameter the sources themselves vary.** SPEC §3.4.1 duplicates
  "3 or 5 times"; RMRS's published instantiation used 2. `dup = 1` is the
  undluplicated base code `[128,8,64]` of the same family, i.e. one rung below
  the smallest deployed setting. This is a *smaller* departure than any
  alternative and it is a departure along an axis the specification itself
  parameterises.

At each `dup`, `N = n_e * 128 * dup`, `n` is the smallest prime `> N` with 2
primitive (SPEC §4.1's own rule), and `omega, omega_r = omega_e` are re-solved
to reproduce the level's own `p*` at the level's own `omega/omega_r` ratio.

### 6.2 `q` at `dup = 1`: rigorous bracket, plus a model validated on published data

`q` cannot be computed in closed form (A12/H4: ML decoding, "no exact formula").
Two independent handles, both derived here:

**(a) Rigorous bracket.**
- *Upper*: `q <= p_i` (Prop 6.1.4, proved on (M)).
- *Lower*: failure occurs whenever **one fixed** weight-`d_i` codeword is at
  least as close as `0`, so
  `q >= P[Bin(d_i,p) > d_i/2] + (1/2) P[Bin(d_i,p) = d_i/2]`.

  The bracket is `~8` bits wide (it is essentially `log2 255`), and it
  **contains all three of SPEC Table 11's published observed inner DFRs**
  (`-10.96 in [-18.54,-10.795]`, `-14.39 in [-22.03,-14.137]`,
  `-11.48 in [-19.10,-11.324]`). It is used as an **invalidation rule**
  (`INV-Q`), not as a design input.

**(b) A Gaussian/orthogonality model of the ML decoder — MODELED, validated.**
Fold the `dup` copies: `u_i = sum_{copies} (-1)^{e}`, `i = 1..128`. The 256
codewords of `RM(1,7)` are `+-H_i` for the 128 Hadamard rows, so the decoder
compares `V_0 = <u,H_0>` against `max_{i!=0} |V_i|`. By orthogonality the `V_i`
are uncorrelated with mean `0` (`i != 0`) and `128*dup*(1-2p)` (`i = 0`), each of
variance `512*dup*p(1-p)`. Hence

```
q  ≈  1 - E_{Z~N(0,1)} [ (2*Phi(rho + Z) - 1)^127 ],     rho = 128 dup (1-2p) / sqrt(512 dup p(1-p)).
```

Validated against the sources' **own measurements** (SPEC Table 11 "Observed
DFR", which are (M)-space simulations of exactly this decoder):

| set | `dup` | `p*` | model `log2 q` | **published observed** | Prop 6.1.4 bound |
|---|---|---|---|---|---|
| NIST-1 | 3 | 0.3398 | `-11.83` | **`-10.96`** | `-10.795` |
| NIST-3 | 5 | 0.3618 | `-15.03` | **`-14.39`** | `-14.137` |
| NIST-5 | 5 | 0.3725 | `-12.03` | **`-11.48`** | `-11.324` |

The model is **low by 0.55–0.87 bits, consistently** — expected, since it
neglects the discreteness of `u` and the correlation between `V_0` and the
maximum, both of which raise `q`. It is therefore used only to *rank* candidate
sets, with the bias direction stated; the contract **measures** `qhat` in
Stage A and re-derives every downstream number from `qhat` (§8.3).

### 6.3 The duplication ladder — the sharpest negative finding

`p*`, `n_e`, `m` and the `omega/omega_r` ratio held at each level's own values;
`T_req` from §3; `core-s` from the cost model of §9.

**HQC-1 shape (`n_e = 46`, `m = 16`, `p* = 0.339788`)**

| `dup` | `n` | `omega` | `omega_r` | `N` | `q` (model) | `lambda` | `m/lambda` | `T_req` | **core-s** |
|---|---|---|---|---|---|---|---|---|---|
| **1** | 5923 | 39 | 44 | 5888 | `0.2306` | 10.61 | **1.51** | `2.91e7` | **`3.4e3`** |
| 2 | 11779 | 54 | 61 | 11776 | `8.94e-3` | 0.411 | 38.9 | `1.47e24` | `3.2e20` |
| 3 *(= HQC-1)* | 17669 | 66 | 75 | 17664 | `2.75e-4` | 0.0127 | 1264 | `2.82e46` | `9.4e42` |
| 4 | 23563 | 77 | 88 | 23552 | `1.74e-5` | `8e-4` | 19946 | `4.14e65` | `2.0e62` |
| 5 | 29443 | 86 | 98 | 29440 | `4.11e-7` | `2e-5` | 847320 | `4.65e91` | `2.9e88` |

**HQC-3 shape (`n_e = 56`, `m = 17`)**: `dup=1` → `q=0.370`, `T_req=3.09e5`,
**`45` core-s**; `dup=2` → `5.8e10` core-s; `dup=5` (= HQC-3) → `2.2e61` core-s.

**HQC-5 shape (`n_e = 90`, `m = 30`)**: `dup=1` → `q=0.473`, `T_req=2.72e6`,
**`673` core-s**; `dup=2` → `3.4e13` core-s; `dup=5` (= HQC-5) → `3.3e83` core-s.

> **There is no ladder.** The transition from affordable to impossible happens
> **entirely between `dup = 1` and `dup = 2`**, a factor `10^17` in cost at the
> HQC-1 shape. Any design that promises to "walk the multiplicity down from
> HQC's setting" is promising something the arithmetic forbids. The reduced arms
> stand alone at `dup = 1`, and the bridge to `dup in {3,5}` is a **heuristic**
> (`HEUR-HQC-6`), never an interpolation.

---

## 7. What the reduced arms sacrifice, quantified

| quantity | HQC-1 (`dup=3`) | PS-R1 (`dup=1`) | matched? |
|---|---|---|---|
| outer code `[n_e,k_e,d_e]`, `m = delta_e+1` | `[46,16,31]`, `m=16` | identical | **YES, exactly** |
| channel `p*` | `0.339788` | `0.347921` (integer-weight rounding; §8.1) | **YES, to 0.008** |
| `omega/sqrt(n)`, `omega_r/sqrt(n)` (A7 regime) | `0.4966 / 0.5643` | `0.5068 / 0.5717` | **YES, to 2 %** |
| dilution `tau = N/n` | `0.99972` | `0.99409` | **YES, to 0.6 %** |
| sampler | uniform `SampleFixedWeightVect$` | identical | **YES** |
| inner code | `[384,8,192]` (`dup=3`) | `[128,8,64]` (`dup=1`) | **NO — the one knob** |
| `q` | `~5e-4` | `~0.23` | NO (consequence of `dup`) |
| **rarity `m/lambda`** | **1264** | **1.51** | **NO — factor 840** |
| elasticity `eta = dlog q/dlog p` | `45.6` (Prop 6.1.4) / `50.7` (model) | `10.3` / `12.3` | NO (factor 4.4) |

**The rarity gap is the design's central liability and it is irreducible**: §5
and §6.3 together show that *every* affordable cell sits at `m/lambda ~ 1`, and
that `T_req` grows roughly `10^{2.5}` per doubling of `m/lambda`. Closing the
remaining `2.9` decades would cost `~10^{29}` trials. It is carried as
`HEUR-HQC-3` with an explicit falsification test and an explicit statement that
passing that test does not validate the extrapolation.

---

## 8. The recommended design and its power

### 8.1 Parameter sets

`n` = smallest prime `> N` with 2 primitive (SPEC §4.1); `omega, omega_r = omega_e`
= smallest integers at the level's own ratio whose exact `p*` (Prop 6.1.2)
reaches the level's own `p*` — hence the small upward rounding in `p*`.

| set | role | `n` | `n_e` | `n_2` | `dup` | `omega` | `omega_r=omega_e` | `p*` (exact) | `m` | `q` |
|---|---|---|---|---|---|---|---|---|---|---|
| **PS-A** | anchor, **true HQC-1** | 17669 | 46 | 384 | 3 | 66 | 75 | `0.339788` | 16 | `~5e-4` |
| **PS-R1** | order-matched, HQC-1 shape | 5923 | 46 | 128 | 1 | 39 | 44 | `0.347921` | 16 | `~0.23` |
| **PS-R3** | order-matched, HQC-3 shape | 7187 | 56 | 128 | 1 | 45 | 51 | `0.364929` | 17 | `~0.37` |
| **PS-R5** | order-matched, HQC-5 shape | 11549 | 90 | 128 | 1 | 59 | 67 | `0.376188` | 30 | `~0.47` |

`PS-A` uses HQC-1's parameters **verbatim**; its `q` is taken from SPEC Table
11's own observed inner DFR `2^-10.96 = 4.993e-4` for sizing, and is
**measured** at run time.

### 8.2 Power: `SE(log2 Ahat_k)` from `(*)`, per set

| set | `T` | reachable `k` (C1 ∧ C2) | `SE` at `k=2` | `SE` at `k=m` |
|---|---|---|---|---|
| PS-A | `1.0e8` | `2, 3` (`k=4` needs `T_req = 3.01e9`) | `0.0092` | *k=16 unreachable* — `SE(k=3) = 0.108` |
| PS-R1 | `1.0e8` | `2 … 16` | `0.00007` | **`0.0321` at `k=16`** |
| PS-R3 | `2.0e7` | `2 … 22` | `0.00014` | **`0.0080` at `k=17`** |
| PS-R5 | `2.0e7` | `2 … 32` | `0.00007` | **`0.0259` at `k=30`** |

**PS-R1 reaches `k = m = 16` exactly, and only just**: `T_req(k=16) = 2.91e7`
against an allocated `T = 1e8`, a margin of `3.4x`; `k = 17` is already out of
reach. That tightness is stated rather than smoothed — if the Stage-A `qhat`
lands below the modeled `0.2306`, `k = 16` can fall out of range at PS-R1, and
`ST-4` is the pre-registered response (report `k = 16` as *not reached*; do
**not** raise `p*` to force it).

### 8.3 Effect size the design is powered against — MODELED, not predicted as fact

The frozen **primary** pre-registered prediction is A17 itself, `log2 A_k = 0`
for all `k` (§ `proposed_specification.yaml`). The following is a **secondary**,
model-derived effect size used only to demonstrate that the design
discriminates. It is `HEUR-HQC-2`'s prediction, evaluated with the
published-derived `gamma = 0.735` and each set's own `eta` and `n_2`:

```
beta = eta^2 * Corr(W_i,W_j) * Var(W_1)/E[W_1]^2 ,
Corr(W_i,W_j) = (gamma - 1)/(n_e - 1)  [exact under equal marginals],
Var(W_1)/E[W_1]^2 = (1-p)/(n_2 p)      [binomial within a block, per RMRS Rem. 4.2],
log A_k = C(k,2) * beta .
```

| set | `eta` | `Corr(W_i,W_j)` | `beta` | modeled `log2 A_2` | modeled `log2 A_m` | `SE` at `k=m` | discrimination |
|---|---|---|---|---|---|---|---|
| PS-A | 50.7 | `-0.00589` | `-0.0765` | `-0.110` | *(-13.2 at k=16, unreachable)* | `0.0092` at `k=2` | **12σ at `k=2`**, 3.1σ at `k=3` |
| PS-R1 | 12.3 | `-0.00589` | `-0.0135` | `-0.0195` | `-2.34` | `0.0321` | **73σ** |
| PS-R3 | 9.2 | `-0.00482` | `-0.0056` | `-0.0081` | `-1.10` | `0.0080` | **137σ** |
| PS-R5 | 7.8 | `-0.00298` | `-0.0024` | `-0.0034` | `-1.50` | `0.0259` | **58σ** |

Two honest riders. (i) The sign is **negative** (conservative direction: the
published bound would be *pessimistic*) only because `gamma < 1`; the competing
common-mode mechanism (`a17_sensitivity.yaml` step 4, `M+`) is positive and
`EV-HQC-6fd5b1` O-6 records the net sign as **undetermined**. The design is
two-sided and does not assume this sign. (ii) At these SEs the experiment is
**over-powered for the modeled effect and correspondingly sensitive to
systematic error** — which is why three null arms and five drift detectors are
mandatory (§10), not decorative.

---

## 9. Cost model — measured machine constants, modeled composition

### 9.1 CALIB-M0 / M0b — measured, generic, **no HQC object**

Command: `python3 calib_m0.py` and `python3 calib_m0b.py` (scratchpad; the
scripts construct only `numpy` arrays of arbitrary size and Python integers of
arbitrary size — no fixed-weight vector, no ring product, no code, no decoder,
no failure indicator). `Linux-6.18.5-x86_64-glibc2.39`, Python 3.11.15, numpy
2.4.6, 4 cores. Single-core results:

| primitive | measured |
|---|---|
| `int16` elementwise add/sub, cache-resident (`N = 4096 … 65536`) | `4.3e9 … 9.8e9` elem/s → **`R_add = 4.0e9`** used (conservative end) |
| `int16` add, memory-bound (`N = 2^24`) | `1.8e9` elem/s |
| `uint64` XOR, cache-resident | `1.8e9` word/s |
| **Python big-int `shift + xor`** | `5.12e-7 s` at 5888 bits; `5.67e-7` at 7168; `7.47e-7` at 11520; **`9.76e-7` at 17669**; `1.75e-6` at 35851 |
| PCG64 `uint64` generation | **`R_rng = 5.1e7`** word/s |

Linear fit in limbs `W = ceil(n/64)`: `t_sx(W) = 2.685e-7 + 2.646e-9 * W`
seconds; predicts `1.002e-6` at `W = 277` against `9.76e-7` measured (2.6 %
high). Used for interpolation only.

### 9.2 Modeled per-trial cost

```
C_prod = (omega + omega_r) * t_sx(n)                      two sparse cyclic ring products
C_dec  = ( N + [N if dup>1 else 0] + 896*n_e ) / R_add    unpack + fold + FWHT-128 per block
C_samp = ( 2*omega + 2*omega_r + omega_e ) / R_rng        fixed-weight index draws
C_trial = 2 * (C_prod + C_dec + C_samp)                   2x IMPLEMENTATION CONTINGENCY
```

`896 = 7 * 128` butterflies per Hadamard transform. The `2x` factor is a
**declared contingency**: the component throughputs are measured, their
composition is not, and no composed HQC pipeline was run by this task.

| set | `C_prod` | `C_dec` | `C_samp` | `C_trial` (with 2x) | trials/s/core |
|---|---|---|---|---|---|
| PS-A | `1.376e-4` | `1.91e-5` | `7.0e-6` | **`3.35e-4`** | 2 990 |
| PS-R1 | `4.25e-5` | `1.18e-5` | `3.3e-6` | **`1.17e-4`** | 8 540 |
| PS-R3 | `5.50e-5` | `1.44e-5` | `3.8e-6` | **`1.47e-4`** | 6 790 |
| PS-R5 | `9.20e-5` | `2.30e-5` | `4.9e-6` | **`2.47e-4`** | 4 050 |

### 9.3 Stage-by-stage budget

| stage | what | trials | core-s (modeled) | wall @4 cores | peak RSS |
|---|---|---|---|---|---|
| **A — calibration** | `qhat, phat, gammahat, Corr(W_i,W_j), eta_emp`, all 4 sets + `INV-Q` bracket check | `4 x 2e6` | `1.69e3` | `~423 s` | `< 0.2 GB` |
| **B1 — PS-A** | confirmatory, `k <= 3` | `1.0e8` | `3.35e4` | `~8 375 s`… *see note* | `< 0.5 GB` |
| **B2 — PS-R1** | confirmatory, `k <= 16` | `1.0e8` | `1.17e4` | `~2 925 s` | `< 0.5 GB` |
| **B3 — PS-R3** | confirmatory, `k <= 22` | `2.0e7` | `2.94e3` | `~735 s` | `< 0.5 GB` |
| **B4 — PS-R5** | confirmatory, `k <= 32` | `2.0e7` | `4.94e3` | `~1 235 s` | `< 0.5 GB` |
| **C — nulls** | `CTRL-BS` (re-indexing, no sampling), `NULL-P` (parametric), `NULL-M` (BSC arm, decode-only), `CTRL-DEC`, `CTRL-REPLAY` | — | `~1.01e3` | `~253 s` | `< 0.5 GB` |
| | **TOTAL (mandatory)** | | **`5.58e4` core-s** | **`~13 950 s`** | `< 1 GB` |
| **D — dilution** *(optional)* | `PS-D2`, `PS-D4` destroy-parameter rungs | `2 x 1e7` | `6.74e3` | `~1 686 s` | `< 0.5 GB` |
| | **TOTAL (with D)** | | **`6.25e4` core-s** | **`~15 640 s`** | `< 1 GB` |

*Note on B1 and B2*: `3.35e4` core-s on 4 cores is `8 375 s` wall, over a single
3 600 s task. The contract therefore **shards PS-A into 3 runs of `3.34e7`
trials each** (independent seeds, disjoint trial-index ranges, results pooled),
each `~2 792 s` wall on 4 cores. Every other stage fits inside one 3 600 s run.
A **run** is one invocation under the 3 600 s cap; inside it, work is split
across 4 worker processes and 3 **seed-disjoint shards** (the replication unit,
gated by `INV-SHARD`). Mandatory runs:
`1 (A) + 3 (B1) + 1 (B2) + 1 (B3) + 1 (B4) + 1 (C) = 8`; optional `D` adds 2.
The contract declares `maximum_runs: 12`, leaving two spare for infrastructure
re-runs — and a re-run is always a **new** run ID, never an overwrite.

Memory is trivially bounded: the working set is one ring buffer
(`n/8 <= 4.4 kB`), one block array (`N <= 17 664` int8), and one histogram of
`S` over `n_e+1` bins. `2 GB` is a 2 000-fold over-provision and is declared as
the cap.

### 9.4 Optimistic assumptions in this cost model — every one flagged

1. **The `2x` contingency may be insufficient.** Component throughputs were
   measured; the composed pipeline was not (`runs_authorized: 0`). If the real
   factor is `5x`, the total becomes `1.4e5` core-s and the contract's stopping
   rule `ST-1` truncates `T` per set rather than overrunning.
2. **Perfect 4-core scaling** is assumed. Trials are embarrassingly parallel and
   memory-trivial, so this is mild, but it is assumed and not measured.
3. **`q` is modeled, not measured.** If `qhat` at PS-R1 lands at the low end of
   its rigorous bracket, `k = 16` may become unreachable; `ST-4` handles this
   with a pre-registered fallback (§ specification `stopping_rules`).
4. **`T_stab`'s threshold of 30** is a judgement, not a theorem. At 100 the
   PS-R1 requirement rises to `9.7e7` — still inside budget, which is why 30 was
   not chosen to make the number work.
5. **Sizing uses the null variance.** Under strong positive dependence the true
   variance is larger; §3.4's jackknife is the guard, and `ST-2` stops and
   reports rather than quoting a model SE.
6. **`gamma = 0.735` is used only for the *modeled effect size* in §8.3**, never
   for sizing. If `gammahat` differs, §8.3's numbers move and the design's power
   moves with them; the frozen prediction (`A_k = 1`) does not move.

---

## 10. What makes a null result interpretable — and what makes it not

A red team will ask this directly, so it is answered directly.

### 10.1 The three null arms, and what each rules out

| arm | construction | what `A_k = 1` on it establishes | cost |
|---|---|---|---|
| **CTRL-BS** (primary) | pseudo-trial `t` takes block `j`'s indicator from **true trial `(t + j*o_j) mod T`**, offsets `o_j` distinct and coprime-spaced. Blocks within a pseudo-trial come from **distinct independent trials**, so they are exactly independent, with **exactly the true marginal block law** — not a modelled one. | `E[Ahat_k] = 1` **exactly**, by construction, for every `k`. Any deviation is estimator or pipeline artifact. | **zero extra sampling** |
| **NULL-M** | `ẽ ~ Bernoulli(phat)^{⊗N}`, identical decoder, identical estimator. This is space (M) — `n_e`, `n_2`, `p*` matched. | the decode-and-estimate pipeline is unbiased on i.i.d.-by-construction input | decode-only, `~2e-5 s`/trial |
| **NULL-P** | `S ~ Binomial(n_e, qhat)` drawn directly; only the estimator arithmetic runs | the `C(S,k)/C(n_e,k)` arithmetic and the jackknife are unbiased at the measured `q` | negligible |

**Pre-registered invalidation rule, stated before any number exists:**

> **INV-NULL.** For each set and each `k <= k_max`, let `SE_null(k)` be the
> jackknife SE of `log2 Ahat_k` on **CTRL-BS**. The (T) result at `(set, k)` is
> **`invalid_measurement`** — never a negative observation — if
> **(a)** `|log2 Ahat_k^{CTRL-BS}| > 3 * SE_null(k)`, **or**
> **(b)** `|log2 Ahat_k^{NULL-M}| > 3 * SE_null(k)`, **or**
> **(c)** `|log2 Ahat_k^{NULL-P}| > 3 * SE_null(k)`, **or**
> **(d)** `|log2 Ahat_k^{CTRL-BS}| > 0.25 * |log2 Ahat_k^{(T)}|` — the null
> excess is not separable from the (T) excess, and the (T) value at that `k`
> is reported as **not resolved**, with the number printed and marked.

### 10.2 Drift to space (M) — five detectors, because D-5 says (M) is where the
argument becomes vacuous

| id | observable | value on (M) | value on (T) | pre-registered rule |
|---|---|---|---|---|
| **D1** | `gammahat = Var(w(ẽ)) / (N phat(1-phat))` | **exactly 1** | `0.61 … 0.74` published-derived (§4) | `gammahat in [0.95,1.05]` at any (T) arm ⇒ **drift alarm, arm invalid**. At PS-A additionally require `gammahat in [0.55,0.85]`. |
| **D2** | exact weights of `x,y,r_1,r_2,e` on every trial | n/a | `omega,omega,omega_r,omega_r,omega_e` exactly | any violation ⇒ `failed_implementation` |
| **D3** | `w(ẽ) <= 2*omega*omega_r + omega_e` | violated w.p. ~1 | never violated | any violation ⇒ `failed_implementation` |
| **D4** | upper-tail quantiles of `w(ẽ)` at PS-A vs **SPEC Table 10** (`6169/6203/6232/6257` at `1e-3…1e-6`, `N=17664`) | `6197/6237/6272/6301` | Table 10's error-vector column | deviation `> 3` weight units at `>= 2` of 4 tails ⇒ sampler not reproducing the sources' own (T) object; arm invalid |
| **D5** | bit-identity re-derivation of `ẽ` from the recorded seed by an independent code path, on 10^4 sampled trials | — | — | any mismatch ⇒ `failed_implementation` |

D4 is the strongest of the five: it compares against a **published measurement
of the same object on the same space at the same parameters**, and §4 shows the
comparison method reproduces Table 10's exactly-computable column to `+-1.3`.

### 10.3 Would a null result be interpretable? — the honest answer

**Partly, and the boundary is stated in advance.**

- **A null at PS-R1/R3/R5 (`|log2 Ahat_m|` within `3 SE` of 0) IS
  interpretable** as: *at these parameters, on space (T), the `m`-way average
  joint failure moment is consistent with A17 to within `+-0.10 / 0.024 / 0.078`
  bits* — provided `gammahat` is in its (T) band (D1), because a set whose
  `gammahat` has drifted to 1 has destroyed the very dependence it is testing
  and **a null there is uninformative by construction, not evidence for A17**.
  That guard is why `p*` is held at HQC's own value (§6.1).
- **A null at PS-A at `k = 2, 3` IS interpretable** at HQC-1's own parameters,
  for `k = 2, 3` only. `EV-HQC-6fd5b1` O-6 forbids reading it as evidence about
  `k = 16`, and no record produced from this contract may do so.
- **A null anywhere is NOT evidence that HQC's published DFR is correct.** The
  reduced arms differ from HQC in `dup` and in rarity by a factor 840; the
  anchor arm differs in order by a factor 5.3. Both gaps are named heuristics.
- **A null with a *failing* null arm is `invalid_measurement`,** per INV-NULL.

**The single most likely way this design produces a misleading null** is
`gammahat -> 1` at the reduced sets — the dependence washing out for a reason
that has nothing to do with A17. D1 is the guard, `HEUR-HQC-1`'s falsification
condition is the test, and the honest statement is that the guard is a
*necessary* condition, not a sufficient one.

---

## 11. What remains infeasible, and the named successors

`docs/inventor-protocol.md` requires a negative to name what stays open. Three
items, each with a concrete successor rather than a shrug.

1. **`mubar_16` at HQC-1's own `(n_e, q)` — infeasible by `10^41`** (§5).
   *Successor*: an **importance-sampled (T) estimator** that samples `e'`
   conditioned on a large block-weight profile and reweights by the exact
   likelihood ratio of the conditioning event. The conditioning must be on a
   statistic whose (T) law is computable — the *global* weight `w(e')`
   (computable by convolution over the fixed-weight sampler's own law) is the
   only obvious candidate, and it is not obviously sufficient. **Not designed
   here. Not claimed to work.** It trades unbiasedness for tail reach and would
   need its own contract and its own null.
2. **The `dup = 1 -> dup in {3,5}` step has no intermediate rung** (§6.3).
   *Successor*: `HEUR-HQC-6`'s within-PS-A consistency test is the only check
   this budget affords. A genuine test needs `dup = 2` at a **much smaller
   `n_e`** (breaking order-matching to buy rarity), which is a different
   contract with a different estimand.
3. **The deployed biased sampler `SampleFixedWeightVect` is never exercised**
   (A22). *Successor*: a paired arm at PS-R1 running the deployed sampler and
   comparing `log2 Ahat_k`. Bounded, well-defined, and **out of scope here**;
   `HEUR-HQC-8` records that no statement about deployed HQC is licensed
   without it.

**Cross-check dependency, declared.** The sibling task `TASK-20260803-6f50df`
(exact oracle) is building an exact small-case joint-moment computation. If it
delivers, `CTRL-ORACLE` in the contract cross-checks `mubarhat_k` against an
exact value at an enumerable parameter. **This contract does not assume it
succeeds**: `CTRL-ORACLE` is marked optional, `NULL-P` carries the estimator
check unconditionally, and no success criterion depends on the sibling.

---

## 12. Threats to validity, ranked

### 12.1 Rank 1 — the rarity gap (`HEUR-HQC-3`)
Factor `840` at HQC-1. The `lambda`-ladder inside the design spans
`m/lambda in [0.70, 1.51]` across PS-R5/R3/R1 — **0.33 decades tested, 2.9
decades applied**. `a17_sensitivity.yaml` step 6 names the exact failure mode: a
joint law can have `rho ≈ 0` and `mu_m >> q^m` if the dependence lives in a rare
many-blocks-fail configuration, and such a configuration is *invisible* at
`m/lambda ≈ 1` because there every configuration is common. **This is the same
obstruction O-6 identifies, relocated from the order axis to the rarity axis.
It is not removed by this design; it is moved to an axis where at least part of
it is testable.**

### 12.2 Rank 2 — wash-out toward `A_k = 1`
Any reduction that pushes `p* -> 1/2` or `q -> 1/2` weakens the dependence and
biases toward confirming A17. PS-R5 sits at `q ≈ 0.47`. Guards: `p*` held at
each level's own value; `gammahat` band (D1); `eta` consistency
(`HEUR-HQC-5`); and the pre-registered statement in §10.3 that a null at a
washed-out set is **not** evidence for A17.

### 12.3 Rank 3 — heavy-tailed estimator
`C(S,k)` is right-skewed; a Gaussian SE without C2 is misleading (§3.3). Guards:
C2 in sizing, jackknife at analysis, `ST-2`.

### 12.4 Disagreements with the predecessor's surviving artifact — resolved

`TASK-20260802-853bad/heuristics.md` is unreviewed and unfrozen. Three of its
statements are **not** reproduced here, each resolved rather than left hanging:

| its statement | disposition here |
|---|---|
| `T = 2.66e42` for `k=16` at HQC-1 (cited to a `feasibility_analysis.md` §3 **that was never written**) | **Unverifiable as cited.** Re-derived independently: `T_req = 3.40e41` at `q = p_i`, `2.82e46` at the model `q`. Same order of magnitude, same verdict; the predecessor's figure is **not** carried forward and **not** cited. |
| a `k_max` of `9–21` at PS-C and `13–34` at PS-D, and predicted effects `-0.42/-1.02/-0.61` bits at those sets | **Not reproducible**: those sets are defined only in a file that does not exist. Superseded by §8's four sets, whose every input is stated here. |
| `CALIB-M0` machine constants | **Not carried forward.** Re-measured here as CALIB-M0/M0b with the exact commands and outputs in §9.1. |
| its Lemma L1 usage ("exchangeable") | **Corrected** in §1.2: the estimand is `mubar_k`, the average, and Lemma F1 needs no exchangeability. |

**No other discrepancy is flagged-and-left.** Where this document notes a gap
(§11), it names a successor.

---

## 13. Scope limits

- Everything is scoped to SPEC `sha256 174186cb…` and RMRS `sha256 cbb7dbd6…`
  as transcribed in BATCH-001 and re-checked in BATCH-002.
- **No HQC object was sampled by this task**; `runs_authorized: 0` was honoured.
  The only executions were (i) deterministic exact-arithmetic evaluations of
  published formulas, (ii) one deterministic identity check, and (iii) two
  generic machine microbenchmarks that construct no HQC object (§9.1).
- **No security claim about HQC in either direction.** Nothing here says HQC's
  DFR is wrong, optimistic, or unsafe; `EV-HQC-6fd5b1` records the direction as
  undetermined and this document does not move it.
- **Claim tier: toy.** `RQ-HQC-001.claim_tier_ceiling` makes that ceiling *more*
  binding for a standardized algorithm, not less.
- Not admissible toward the `AGENTS.md` rule 13 closure quorum: independent
  session, same backend.
- These are **proposed** records. Only a Coordinator ledger archive creates
  `H-HQC-18d1b4` and `EXP-HQC-982268`.
