# RT-EXP-1 — the bucket-gain ladder, run

Executes the experiment `RT-20260803-be45a8` §6 specified as the cheapest
decisive test of the hole it found, and which `KN-FIND-ffe1df` recorded as the
correct unrun next action.

**Status: EXPLORATORY MEASUREMENT.** No `EXP-*`/`RUN-*`/`EV-*`/`DEC-*` record;
claim tier *exploratory*; `certificate.kind: none`. This is **measurement, not
proof** — see §4.

---

## 0. Answer first

| Question | Answer |
|---|---|
| Does the bucket-max quantity show an attack signal for any **cheap** filter? | **No.** Every cheap family decays indistinguishably from the SHA null. |
| Including the families that were *uncovered*? | **Yes, including them** — target-dependent `h_Q` and `x([2]P)` both decay like the null. |
| Did anything trip the refutation criterion? | **Yes — `popcount` and `digitsum`.** Both are **false positives**, killed by the matched-marginal control. §2 |
| Can the instrument actually see a signal at the decisive boundary? | **Yes.** The planted `θ = p^{-1/9}` mixture separates cleanly; the `P2` shuffle collapses `20.01 → 1.0030`. §3 |
| Does this close the Lemma 5 hole? | **No.** The hole is a *proof* hole and remains open. This is evidence it does not conceal an attack. §4 |

---

## 1. What is measured

The red team's point: every theorem in this line bounds
`δ = Pr[h(P+Q) = f(h(P),h(Q))]`, the `q_c`-weighted **average** over target
buckets, while a Wagner level fixes **one** bucket `c` and offset `d` *after
seeing `h`* and is paid at `max_{c,d} π_c(d) >= δ`. So this measures the
quantity the attacker is actually paid at:

```
   G  =  M_eff · max_{c,d} π_c(d),      π_c(d) = Pr[h(P+Q)=c | h(P)+h(Q)+d=c]
```

`G ≈ 1` means no exploitable bucket gain. **Exact, no sampling**: all `N²` pairs,
via `W_s[k] = Σ_a (1_a ⋆ 1_{s-a})[k]`, which is a convolution in the *alphabet*
index too — so all `M` of them come from one `M`-axis FFT of the `N`-axis FFTs
(`M` length-`N` transforms, not `M²`). `M = round(N^{1/3})`, 3 curves per prime,
8 primes, `p = 523 … 65539`.

**Run at `M_eff`, the number of non-empty level sets.** This is [D]'s (H6)
non-redundancy hypothesis, which the additive completion dropped and the red team
named as missing. It is not cosmetic: at full `M = 40`, popcount (whose image is
only `0…16`) has empty buckets, `den(s) = 0`, and `G` blows up to **157348** — a
value exceeding `M`, hence impossible by construction. **The first run of this
experiment produced exactly that artifact.** A filter earns no credit for buckets
it never populates.

## 2. Results

```
                  filter       523     1033     2063     4111     8219    16417    32779    65539   alpha(G-1)             95% CI
                 x mod M    1.3069   1.2150   1.2461   1.2160   1.1374   1.1413   1.0982   1.0859       -0.258      [-0.32,-0.20]  Meff=40
             floor(Mx/p)    1.3029   1.3325   1.2615   1.2118   1.1444   1.1586   1.1077   1.0823       -0.287      [-0.34,-0.23]  Meff=40
                popcount    2.0699   2.5702   2.7742   2.8895   2.9226   3.1282   3.0443   3.3045       +0.125      [+0.07,+0.18]  Meff=16
           popcount SHUF    2.0381   2.4457   2.7080   2.8404   2.8774   3.0796   3.0271   3.2819       +0.135      [+0.09,+0.18]  Meff=16
                digitsum    1.2193   1.1662   1.2057   1.3177   1.5296   1.8069   2.2063   2.6656       +0.495      [+0.39,+0.61]  Meff=40
           digitsum SHUF    1.1726   1.1434   1.1737   1.2728   1.4780   1.7572   2.1636   2.6267       +0.537      [+0.43,+0.64]  Meff=40
                 x([2]P)    1.3069   1.2150   1.2461   1.2160   1.1374   1.1413   1.0982   1.0859       -0.258      [-0.32,-0.20]  Meff=40
          h_Q target-dep    1.1886   1.1831   1.1583   1.1299   1.0858   1.0722   1.0656   1.0527       -0.290      [-0.33,-0.25]  Meff=40
              sha [null]    1.3271   1.2723   1.1921   1.1438   1.1186   1.1181   1.1133   1.0742       -0.283      [-0.34,-0.22]  Meff=40
  P2 dlog-int [old ctrl]    4.0620   5.0466   6.5399   8.0308  10.0245  12.5190  16.0156  20.0122       +0.375      [+0.36,+0.39]  Meff=40
P2 dlog-int [old ctrl] SHUF 1.0640   1.0414   1.0265   1.0161   1.0102   1.0064   1.0049   1.0030       -0.634      [-0.66,-0.61]  Meff=40
    PLANTED theta=p^-1/9    1.6642   1.5823   1.6270   1.6146   1.5645   1.5717   1.5983   1.5725       -0.022      [-0.04,-0.00]  Meff=40
```

### The two false positives, and the control that caught them

The red team's refutation criterion is *"refuted if any cheap family's 95% CI on
`α(G−1)` excludes `<= 0` while nulls decay."* **`popcount` and `digitsum` both
trip it.** Taken at face value that is an attack signal on two cheap families.

It is not. The **matched-marginal shuffle** — identical level-set sizes, all
structure destroyed — reproduces both effects exactly:

| filter | `α` | matched-marginal `SHUF` | verdict |
|---|---|---|---|
| `popcount` | +0.125 [+0.07,+0.18] | **+0.135 [+0.09,+0.18]** | imbalance |
| `digitsum` | +0.495 [+0.39,+0.61] | **+0.537 [+0.43,+0.64]** | imbalance |

The shuffled versions are, if anything, *slightly higher*. Both signals are
entirely the **free marginal-bias floor** — [D] §8.3's `f_const` effect — and
carry no sum-compatibility content. Popcount is binomial over bits and digit sums
are non-uniform, so their level sets are wildly unequal and `max_c π_c` is
dominated by small buckets.

**Recorded because it nearly went the other way:** without this control the
honest reading of the table would have been "two cheap families refute the
barrier."

## 3. The instrument passes its own test

The red team's objection to the old `P2` control was that it is flat *by
algebraic identity*, calibrating only the maximal-signal end and never showing
the instrument resolves the `M·T ≈ 1` boundary where closure is decided. Two
controls answer that:

- **`P2` vs `P2 SHUF`: `G = 20.0122` → `1.0030`**, `α` from `+0.375` to
  `−0.634`. A genuine sum-compatible structure is annihilated by the shuffle
  while its marginals are preserved. The statistic separates structure from
  imbalance by a factor of ~20.
- **Planted `θ = p^{-1/9}`**: sits at `G ≈ 1.57–1.66`, essentially flat
  (`α = −0.022`), clearly above the SHA null's `1.07–1.33` decaying at `−0.283`.
  **`Λ` could not distinguish these** (`Λ_x = 0.01622` vs `Λ_sha = 0.01619`);
  `G` does.

## 4. What this does and does not establish

**Does.** For every cheap filter tested — including the two the coverage table
listed as *uncovered*, target-dependent `h_Q` and `x([2]P)` — the quantity a
Wagner level is actually paid at decays indistinguishably from a SHA null, over a
125× range in `p`, at `M = N^{1/3}` which is the `j = 2` operating point. The
instrument demonstrably resolves signals at that boundary.

**Does not.**

1. **The Lemma 5 hole is a PROOF hole and is untouched.** No theorem here bounds
   `max_c π_c`. Measurement at eight toy primes is not a bound.
2. **`j = 2` remains UNPROVED**, exactly as `KN-FIND-ffe1df` states. This
   experiment lowers the probability that the hole conceals an attack; it does
   not close it.
3. **Toy scale.** `p <= 65539` against a target of 256-bit `p`. Under
   `AGENTS.md` rule 4 this is not crypto-scale validation.
4. **Filter list is not exhaustive.** Nine families; the space of cheap `h` is
   not enumerable, and Proposition 2 proves no group-theoretic argument can cover
   it.
5. **One `M` per prime** (`M = round(N^{1/3})`), 3 curves each. Per-curve spread
   was not separated from the `p`-trend, which the red team flagged as a real
   confound in fits of this kind.

**`sota_delta = 0`** on all axes; `dominated_by` inapplicable. No attack, no
speedup, no solve.

## 5. Next

The open item is unchanged and is **mathematical, not empirical**: prove or
replace Lemma 5's equal-`π_c` hypothesis, or bound `max_{c,d} π_c(d)` directly.
Until then the (O2) line remains a conditional, class-restricted, level-1,
bucket-averaged barrier.

```yaml
inference:
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    Policy aliases in orchestration/model-policies.yaml are unresolvable in this
    harness (AGENTS.md rule 11). This experiment was specified by an independent
    red-team session and executed here, so specification and execution are
    procedurally separated but share a backend.
  model_verified: false
  model_verified_reason: >-
    `python3 -m orchestration.adapter doctor --probe` not run this session.
```
