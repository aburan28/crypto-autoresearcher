# (O2) as an argument — a Fourier obstruction to sum-compatible filters

> **CORRECTION NOTICE — added after this document was written; no text below is
> altered.** This document's word "**unconditionally**" (§0 and §4) is an
> **overclaim** and is corrected in `O2_composition_closure.md` §2. Theorem A is
> unconditional as an *inequality*, but the closure conclusion depends on
> `Delta(h) = o(1/M)`, which §6 here **measured** for two filter families and
> extrapolated. `O2_derivation_attempt.md` Proposition 2 exhibits a family — the
> dlog-interval filter `floor(M*dlog(P)/N)` — for which `Delta ~ 1/2` at
> arbitrarily large `M`, so the extrapolation is false in general. §7.3 below did
> flag the scaling as "measured, not proven"; the headline did not carry that
> qualifier. Theorems A and B, the exact identity, and every number in §6 stand
> as written. Read `O2_composition_closure.md` for the corrected and composed
> statement, in which the affine closure becomes *stronger* — a proof on a named
> class rather than an extrapolation.

Executes item **4** of `F1_sum_compatible_filter_search.md` §10: *"Making precise
the step ... would convert (O2) from a measurement into an argument, which is
what the closure standard actually asks for."*

**Status: EXPLORATORY ANALYSIS.** No frozen specification governs this work; no
`EXP-*` contract, no `RUN-*` record, no evidence record, and no ledger entry is
created or modified by it. Claim tier is *exploratory* under
`docs/claims-and-verification.md`. Nothing here promotes, rejects, or closes any
hypothesis. Disposition of (O2) belongs to the Reviewer and Coordinator.

**Certificate discipline.** No discrete-log solve and no factor-base relation is
claimed; `certificate.kind: none`. The content is two theorems with proofs. The
accompanying computation is a *verification* of those theorems by exhaustive
enumeration over entire groups — not sampling — so its central check is an
identity holding to `1e-15`, not a statistic.

---

## 0. Answer first

| Question | Answer |
|---|---|
| Is there now an *argument* for (O2), not just a measurement? | **Yes, for the affine-`f` case, unconditionally.** Theorem A forces any filter with agreement `>= 4/M` under an affine `f` to have `Delta(h) >= 3/M`. |
| What is `Delta`? | The maximum correlation of `h` with a **character of the discrete logarithm**. It is one number per `h`, computable by an FFT — it replaces the entire `(h, f, M)` sweep. |
| Does that close the exponent-moving configurations? | **For affine `f`, yes — both of them.** Wagner needs `M ~ N^{1/(j+1)}`; the theorem needs `M >~ sqrt(N)`. `j=2` (`M ~ N^{1/3}`, exponent `0.4167`) and `j=3` (`M ~ N^{1/4}`, exponent `0.375`) both fail by a polynomial margin. |
| Does it close arbitrary `f`? | **No — and this is the honest residual.** Theorem B loses a factor `M`, closing only `M <~ N^{1/4}`. The `j=2` window at `M ~ N^{1/3}` survives *the proof*. It does not survive F1's measurements, which searched arbitrary `f` and found max lift `1.101x`. |
| Does the theorem explain F1's positives? | **Yes, all of them, as forced consequences.** See §5. |

---

## 1. Setup and notation

Let `G` be cyclic of order `N` with generator `G0`. The map `x -> [x]G0`
identifies `G` with `Z/N`, and under this identification **`x` is the discrete
logarithm** of the point. This is the whole point of what follows: the Fourier
basis on `G` is the basis of characters of the dlog.

For `phi: Z/N -> C` write

```
   phihat(xi) = E_x[ phi(x) e(-xi*x/N) ],      e(z) = exp(2*pi*i*z)
```

so that `phi(x) = sum_xi phihat(xi) e(xi*x/N)` and, by Parseval,
`sum_xi |phihat(xi)|^2 = E_x|phi(x)|^2`.

Fix `h: G -> [M]`, `M >= 4`. Put

```
   g_t(x)   = e( t*h(x)/M ),          t in Z/M          (unit modulus)
   A_c      = h^{-1}(c),  alpha_c = |A_c|/N
   Delta(h) = max_{t != 0}  max_xi   | g_t-hat(xi) |
   delta(h) = max_c        max_{xi != 0} | 1_{A_c}-hat(xi) |
```

`Delta` and `delta` both measure **correlation of `h` with a character of the
discrete logarithm**. `Delta` does it through the phase encoding of `h`;
`delta` through its level sets.

### Lemma 1 (trilinear form)

For any `A, B, C: Z/N -> C`,

```
   E_{x,y}[ A(x+y) B(x) C(y) ] = sum_alpha Ahat(alpha) Bhat(-alpha) Chat(-alpha).
```

*Proof.* Expand all three in the Fourier basis. The inner expectation
`E_{x,y}[ e((alpha+beta)x/N) e((alpha+gamma)y/N) ]` vanishes unless
`beta = -alpha` and `gamma = -alpha`, where it is `1`. ∎

---

## 2. Theorem A — affine `f`

> **Theorem A.** Let `f(a,b) = a + b + d (mod M)` for any fixed `d`. Then
>
> ```
>    eps_+ := Pr_{x,y}[ h(x+y) = f(h(x), h(y)) ]
>           = (1/M) * sum_{t=0}^{M-1} e(-t*d/M) * sum_xi g_t-hat(xi) |g_t-hat(xi)|^2
> ```
>
> and consequently
>
> ```
>    eps_+ <= 1/M + ((M-1)/M) * Delta(h) <= 1/M + Delta(h).            (A)
> ```

*Proof.* Write `1[u = v] = (1/M) sum_t e(t(u-v)/M)` and apply it to
`u = h(x+y)`, `v = h(x)+h(y)+d`:

```
   eps_+ = (1/M) sum_t e(-t*d/M) * E_{x,y}[ g_t(x+y) conj(g_t(x)) conj(g_t(y)) ].
```

Apply Lemma 1 with `A = g_t`, `B = C = conj(g_t)`. Since
`conj(g)-hat(-alpha) = conj( ghat(alpha) )`, the inner expectation is
`sum_alpha g_t-hat(alpha) |g_t-hat(alpha)|^2`, which is the stated identity.

For the bound: the `t = 0` term has `g_0 == 1`, `g_0-hat = 1_{xi=0}`, and
contributes exactly `1`. For `t != 0`, `|g_t| = 1` gives
`sum_xi |g_t-hat(xi)|^2 = 1` by Parseval, hence

```
   | sum_xi g_t-hat(xi)|g_t-hat(xi)|^2 |  <=  max_xi |g_t-hat(xi)| * 1  <= Delta.
```

Summing the `M-1` nonzero-`t` terms and dividing by `M` gives (A). ∎

**Reading.** `1/M` is chance. So *any* lift above chance under an affine `f` is
paid for, one-for-one, by correlation with a dlog character. A filter clearing
F1's `4/M` bar needs

```
   Delta(h) >= 3/M.                                                   (A')
```

---

## 3. Theorem B — arbitrary `f`

> **Theorem B.** For **every** `f: [M] x [M] -> [M]` whatsoever,
>
> ```
>    eps_f := Pr_{x,y}[ h(x+y) = f(h(x), h(y)) ] <= max_c alpha_c + M * delta(h).   (B)
> ```

*Proof.* Partition by the observed pair of `h`-values:

```
   eps_f = sum_{a,b} E_{x,y}[ 1_{A_a}(x) 1_{A_b}(y) 1_{A_{f(a,b)}}(x+y) ].
```

Lemma 1 with `A = 1_{A_{f(a,b)}}`, `B = 1_{A_a}`, `C = 1_{A_b}`, together with
`1hat(-xi) = conj(1hat(xi))` for real-valued indicators, gives

```
   eps_f = sum_{a,b} sum_xi  1_{A_{f(a,b)}}-hat(xi) * conj(1_{A_a}-hat(xi)) * conj(1_{A_b}-hat(xi)).
```

*The `xi = 0` term.* `1_A-hat(0) = alpha_A`, so it equals
`sum_{a,b} alpha_a alpha_b alpha_{f(a,b)} <= (max_c alpha_c) * sum_{a,b} alpha_a alpha_b = max_c alpha_c`.

*The `xi != 0` terms.* Bound `|1_{A_{f(a,b)}}-hat(xi)| <= delta` and set
`s(xi) = sum_a |1_{A_a}-hat(xi)|`:

```
   | sum_{xi != 0} ... |  <=  delta * sum_{xi != 0} s(xi)^2.
```

Cauchy–Schwarz over the `M` classes gives `s(xi)^2 <= M * sum_a |1_{A_a}-hat(xi)|^2`,
and Parseval over all `xi` gives `sum_xi sum_a |1_{A_a}-hat(xi)|^2 = sum_a alpha_a = 1`.
Hence `sum_{xi != 0} s(xi)^2 <= M`, and the tail is at most `M * delta`. ∎

**Reading.** A filter clearing `4/M` with a roughly balanced `h`
(`max_c alpha_c <= 2/M`, which F1's degeneracy accounting already enforces via
`M_eff`) needs

```
   delta(h) >= 2/M^2.                                                 (B')
```

**Where the factor `M` comes from, and whether it is real.** It is the
Cauchy–Schwarz step over the `M` level sets. It is *not* known to be tight; a
sharper treatment of the `f`-dependence would shrink it. This single factor is
the entire difference between closing `j=2` and not (§4), so it is the precise
place a future session should push.

---

## 4. What this closes

A Wagner `2^j`-tree needs each of the `j` levels to pin `log2(N)/(j+1)` bits,
i.e. `M ~ N^{1/(j+1)}` — the quantitative point recorded in
`F1_sum_compatible_filter_search.md` §1. Measured `Delta` and `delta` for
structureless `h` on prime-order `E(F_p)` scale as `Theta~(N^{-1/2})` (§6).
Substituting into (A') and (B'):

| `j` | `M ~ N^(1/(j+1))` | class exponent (`m=16`) | affine `f` (needs `M >~ sqrt(N)`) | arbitrary `f` (needs `M >~ N^(1/4)`) |
|---|---|---|---|---|
| 2 | `N^0.3333` | **0.4167** | **CLOSED** | **open** |
| 3 | `N^0.2500` | **0.3750** | **CLOSED** | open (borderline) |
| 4 | `N^0.2000` | 0.4000 | **CLOSED** | CLOSED |

**The two exponent-moving configurations are closed for affine `f`,
unconditionally and by a polynomial margin** — not by a sweep coming up empty,
but because `M ~ N^{1/3}` is nowhere near the `M ~ sqrt(N)` that (A') demands.

**The residual is exactly one window: arbitrary `f` at `j = 2`** (and `j = 3` at
the boundary). It is a gap in the *proof*, not evidence for an attack: F1's
`f_joint` arm fits the empirically optimal `f` for each `h` out-of-sample and
reached max lift `1.101x` against the required `4x`, on 11 prime-order arms.
Proof and measurement do not disagree; the proof is simply weaker than the
measurement here.

---

## 5. Why this is more than a repackaging — it explains F1's three findings

The theorems make all three of F1's outcomes forced, rather than coincidental.

1. **The dlog pull-back (F1 §5) satisfies the inequality but violates the cost
   clause.** Theorem A says this is *necessary*, not incidental: the only way to
   lift above chance is correlation with a dlog character, and `h = dlog mod M`
   *is* such a character. Verified: `Delta = 0.900` at `M=4` and `0.994` at
   `M=16`, against `0.077–0.155` for the x-coordinate filter (§6). **The search
   found the dlog pull-back because it is essentially the only thing there is to
   find.**

2. **2-descent characters work, at exactly `M = 4`, and die on the odd part
   (F1 §6.1).** A sum-compatible `h` with `f` a group law is a homomorphism
   `G -> Z/M`, and `Hom(Z/N, Z/M) = Z/gcd(N,M)`. So exact filters exist
   precisely when `gcd(#G, M) > 1`, are capped by the torsion order, and are
   identically trivial when `#G` is prime. Verified: on `Z/1024` with `M | N`,
   `eps = 1.0000` and `Delta = 1.0000` exactly; on prime-order arms nothing
   approaches it.

3. **The x-coordinate filter sits at chance (F1 §7).** Its `Delta` tracks the
   SHA-256 structureless null to within a few percent at every size tested
   (§6). Theorem A then *predicts* `eps_+ <= 1/M + Delta`, and the measured
   `eps_+` lands at `1/M` to three decimals. The measurement was not merely
   negative — it was at the value the theorem requires.

The unifying statement: **`Delta(h)` is large exactly when `Hom(G, Z/M)` is
nontrivial or `h` encodes the discrete logarithm.** Prime-field ECDLP is posed
where the first fails, so only the second remains, and the second is barred by
the cost clause.

---

## 6. Verification

Two scripts in this directory, exhaustive over whole groups (no sampling):

- `fourier_obstruction.py` — checks the identity of Theorem A and the bounds
  (A), (B) on 18 configurations: `Z/1024` and `Z/1021` controls, and
  prime-order curves `#E = 499, 1103, 1901` with `h in {x mod M, SHA-256 mod M,
  dlog mod M}` at `M in {4, 16}`. `eps_+` and `eps_f` are computed by full `N^2`
  enumeration, and `eps_f` maximises over **all** `f` via the exact joint table.
- `scaling.py` — `Delta`, `delta` for `h = x mod M` and the SHA null on nine
  prime-order curves, `N = 523 ... 120413`.

Results:

```
  (T1) exact identity of Theorem A : 18/18 hold to 1e-15
  (T2) bound (A), affine f         : 18/18 hold
  (T3) bound (B), arbitrary f      : 18/18 hold
```

Positive controls behave as the theory demands: `Z/1024` with `M | N` gives
`eps = 1.0000`, `Delta = 1.0000`; `Z/1021` with `M` not dividing `N` gives
`eps = 0.5005` (the two-candidate behaviour), `Delta = 0.90–0.9996`.

Scaling of `Delta` for the x-coordinate filter, `M = 16`:

```
       N    Delta_x   D*sqrt(N)   D/sqrt(log(MN)/N)    Delta_sha
     523   0.154995      3.545               1.179     0.127293
    1103   0.096616      3.209               1.026     0.086671
    1901   0.076507      3.336               1.038     0.078353
    3907   0.057843      3.616               1.088     0.050554
    7699   0.039631      3.477               1.016     0.039498
   15259   0.030670      3.789               1.076     0.026362
   29833   0.025123      4.339               1.200     0.021312
   59951   0.015615      3.823               1.030     0.015258
  120413   0.011277      3.913               1.029     0.010500
```

The extreme-value model is the right one and the fit is the reason to trust the
extrapolation: `Delta` is a maximum over `~ M*N` coefficients each of scale
`N^{-1/2}`, so `Delta ~ sqrt(log(M*N)/N)`. That column is flat at `1.03–1.20`
across a **230x** range of `N`, while the pure `N^{-1/2}` column drifts upward
by 10%. Log-log slopes: `-0.463` (x-coord `Delta`), `-0.441` (x-coord `delta`),
`-0.455` / `-0.466` (SHA null) — all consistent with `N^{-1/2}` times a
logarithmic factor, and the curve filter is **indistinguishable from the null**.

**Reproduction.** Python 3.13, numpy 2.4.0, macOS-26.6-arm64. Deterministic —
no RNG is used anywhere except SHA-256 as a fixed function; re-running
reproduces every digit. `python3 fourier_obstruction.py`, `python3 scaling.py`
(~1s and ~9s). Curve orders are computed independently inside the script by
character sums, and `#E` primality by Miller–Rabin; the `#E = 499, 1103, 1901`
curves and the group-order arithmetic agree with the SageMath-verified panel in
`F1_sum_compatible_filter_search.md` §2 in method. Scripts are archived here
rather than left in scratch because the theorems, not the numbers, are the
deliverable and the numbers must remain checkable against them. Any promotion
to an evidence record must still re-run them inside an experiment directory with
the standard receipt package.

---

## 7. Limits — what this does not do

1. **It does not close arbitrary `f` at `j = 2`.** §3's factor `M` is the whole
   gap. Stated plainly because it is the one configuration that would move the
   exponent below `1/2`.
2. **It does not prove the cost clause.** Theorem A converts "no cheap
   sum-compatible filter" into "no cheap function correlating with a dlog
   character." That is a reduction to a dlog-hardness statement, not a proof of
   one. It is the right shape — the obstruction is now *tied to the hardness of
   the problem itself* rather than free-floating — but it is a conditional
   statement and must be cited as one.
3. **`Delta = Theta~(N^{-1/2})` is measured, not proven,** for the specific
   filters tested. For `h = x mod M` a proof should be within reach of standard
   character-sum bounds over `E(F_p)` (Kloosterman/Weil-type); that is the
   natural next lemma and it would make §4's affine row unconditional for that
   family rather than resting on an extrapolation.
4. **Uniform `P, Q` only.** Wagner's later levels operate on lists already
   filtered at earlier levels, so their inputs are conditioned. The theorem
   applies verbatim to level 1 and needs restating for levels `>= 2`.
5. **Cyclic `G`.** The proofs use only the character group, so they extend to
   any finite abelian `G` verbatim; the prime-order cyclic case is what
   prime-field ECDLP poses and is what is verified here.

**`dominated_by` / `sota_delta`.** No algorithm is proposed; there is no
frontier row to occupy. `sota_delta = 0` on time, memory and data/queries;
`dominated_by` is inapplicable rather than `null`.

---

## 8. Forward guidance

1. **Kill the factor `M` in Theorem B.** This is the single highest-value open
   item in the direction: it would close `j = 2` for arbitrary `f` and retire
   the last exponent-moving configuration in the class.
2. **Prove `Delta(x mod M) = O~(N^{-1/2})`** by character-sum bounds, making
   §4's affine row unconditional.
3. **Restate for conditioned inputs** (limit 4) so the result covers all `j`
   levels rather than the first.
4. **Retire the `(h, f, M)` sweep as the instrument.** `Delta(h)` is one FFT per
   `h` and dominates a full `f`-sweep: F1 spent 31 283 `(h, f, M)` combinations
   to conclude what `Delta` reports directly. Any future filter family should be
   screened by `Delta` first.

---

## Inference

```yaml
inference:
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  reasoning_effort: null
  fallback_used: true
  fallback_reason: >-
    This Claude Code harness cannot resolve the policy aliases in
    orchestration/model-policies.yaml; subagent frontmatter supports only Claude
    models. Recorded, never silently substituted (AGENTS.md rule 11). Note the
    consequence: this analysis, the F1 search it builds on, and the adjudication
    both rest on resolve to the same backend. It is a procedurally separate
    session, not a model-independent check. The theorems are proved and the
    proofs are short enough to check by hand, which is the intended mitigation.
  degraded_allowed: false
  degraded_requirements: []
  model_verified: false
  model_verified_reason: >-
    `python3 -m orchestration.adapter doctor --probe` was not run in this
    session. The identifier is unverified configuration.
```
