# Adjudication of Claim A, `ledger/proposals/IDEA-20260802-003.yaml`

Red Team, BATCH-028. Adjudicates **Claim A only**. Claim B is a measurement
proposal and is out of scope except for one note at the end.

This adjudication changes no research state. No ledger record, proposal,
hypothesis, experiment, or control was modified; no commit was made. It is an
argument review, and its status is a recommendation to the Coordinator.

**Independence caveat (mandatory disclosure).** This harness resolves author and
reviewer to the same backend (`claude-opus-5`). The independence of this review
is *procedural* — separate session, separate task, separate write scope — and
is **not** model-level independence. Correlated blind spots between
`IDEA-20260802-003`'s author and this adjudicator are not excluded by anything
in this document. Under `AGENTS.md` rule 12 a closure claim requires
`review-breakthrough` at `max` on an independently resolved model; this session
is not that, and this document may not be treated as satisfying it.

---

## VERDICT

**UNSOUND AS STATED.** Both load-bearing steps of Claim A fail:

- the premise `B >= (m! p)^(1/m)` is **not forced**, and the optimal member of
  the very class Claim A is closing sits strictly *below* it
  (`B = N^(1/(2m-1))`, which for `m = 5` is `N^0.111`, not `N^0.2`);
- the quantifier "**every** balanced meet-in-the-middle claw ... has a larger
  side of size at least `B^(m/2)`" is false in both directions — balanced is not
  optimal in this class, and when `B < p^(1/m)` the quantity `B^(m/2)` is
  *smaller* than `p^(1/2)`, so the chain `B^(m/2) >= p^(1/2)` breaks exactly
  where the interesting parameterizations live.

**The conclusion is nevertheless correct, and a stronger correct closure
exists.** I derived and numerically verified a replacement below. The corrected
statement is:

> For the exact-match enumerate-and-join class over `E(F_p)`, total time
> `T >= 2*sqrt(B*N)`, and the class optimum is `N^(m/(2m-1))` in time **and**
> memory — that is `1/2 + 1/(2(2m-1))`, **strictly above 1/2 at every finite
> `m`**, reaching `1/2` only in the limit `m -> infinity`. The class never
> attains `1/2` and never beats it.

So Claim A is *pessimistic about itself*: it asserts parity with rho when the
class is strictly worse than rho at every arity, on both cost axes. "The
exponent is 1/2 identically in `m`" is false as an equality — the floor depends
on `m` — while "never below 1/2" is true.

**Net disposition.** Do **not** record Claim A as written; it does not meet the
`docs/inventor-protocol.md` §4 closure standard, because §4 requires *a named
obstruction and an argument*, and the argument given is wrong. The replacement
in §7 does meet that standard and may be promoted in that form after
independent `review-breakthrough`.

---

## 1. What was actually checked, and how

All numbers below are from computations run in this session
(`scratchpad/{count,opt,sim,filter,multi}.py`). Nothing is quoted from memory
without being labelled as such.

External results relied on, each verified by web search in this session:

| Result | Where | Verified |
|---|---|---|
| Wagner, *A Generalized Birthday Problem*, CRYPTO 2002 — k-tree in time/memory `N^(1/(floor(log2 k)+1))`; for `k=4`, `alpha^3` solutions at `alpha x` the work of one | [iacr.org/archive/crypto2002/24420288/24420288.pdf](https://www.iacr.org/archive/crypto2002/24420288/24420288.pdf) | yes, 2026-08-01 |
| Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*, EUROCRYPT '97, LNCS 1233, 256–266 | [link.springer.com/chapter/10.1007/3-540-69053-0_18](https://link.springer.com/chapter/10.1007/3-540-69053-0_18), [shoup.net/papers/dlbounds1.pdf](https://www.shoup.net/papers/dlbounds1.pdf) | yes, 2026-08-01 |
| Kuhn & Struik, *Random Walks Revisited: Extensions of Pollard's Rho Algorithm for Computing Multiple Discrete Logarithms*, SAC 2001, LNCS 2259 | [link.springer.com/chapter/10.1007/3-540-45537-X_17](https://link.springer.com/chapter/10.1007/3-540-45537-X_17) | yes, 2026-08-01 |

Not re-verified this session and therefore **not** relied on for any load-bearing
step, listed only as forward pointers: Semaev (eprint 2004/031), Gaudry
(J. Symbolic Comput. 44, 2009), Diem (Compositio Math. 147, 2011),
Minder–Sinclair (*The extended k-tree algorithm*, SODA 2009), van Oorschot–Wiener
(J. Cryptology 12, 1999), Corrigan-Gibbs–Kogan (EUROCRYPT 2018). A KN-LIT entry
is owed for any of these that a promoted record cites.

---

## 2. Step 1 — is `B >= (m! p)^(1/m)` forced? **No.**

### 2a. The counting itself is fine, and is better than heuristic

Let `F` be any set of `B` points in a group of prime order `N`, and let `R` be a
uniform random target independent of `F`. The number of `m`-subsets of `F` is
exactly `C(B,m)`, and by linearity of expectation

```
E[ #{ S subset F, |S| = m, sum(S) = R } ]  =  C(B,m)/N     (exact, any F)
```

and by Markov

```
Pr[ R decomposes ]  <=  C(B,m)/N  <=  B^m/(m! N)           (rigorous, any F)
```

I verified the equality exactly on a real curve `y^2 = x^3 + 11` over `F_1009`,
prime order `N = 967`, by full enumeration of every `m`-subset over the whole
group:

```
 B   m   C(B,m)   C(B,m)/N   empirical mean   Pr[>=1 decomp]   Markov UB
 8   4       70     0.0724          0.0724           0.0724       0.0724
10   4      210     0.2172          0.2172           0.2006       0.2172
12   4      495     0.5119          0.5119           0.4240       0.5119
14   4     1001     1.0352          1.0352           0.6112       1.0000
20   4     4845     5.0103          5.0103           0.9938       1.0000
```

The empirical mean matches `C(B,m)/N` to the last digit in every cell, as it
must, and `Pr[>=1]` sits below the Markov bound in every cell. **This is a
strengthening the program should take:** the `m!` counting relation is not a
heuristic at the level of the *expectation* — it is exact — and the "in the
choice of `F`" leg of Claim A is *rigorously* true for the mean, for every `F`,
because the mean incidence count `C(B,m)` is spread over `N` targets no matter
how `F` is structured. Only the *concentration* (that a typical target attains
the mean) is heuristic, and Markov gives the inequality in the direction a
closure needs. `IDEA-20260727-006`'s `beta_cert` worry is about the wrong
direction: for a lower bound on cost you want an upper bound on yield, and
Markov supplies it unconditionally.

### 2b. But "non-vanishing yield" is the wrong threshold, and the claim's own class prefers to violate it

`(m! N)^(1/m)` at `m = 4, N = 967` is `12.34`. At `B = 10` — comfortably below
the "forced" threshold — 20.06% of all targets still decompose. Yield is not
vanishing; it is *low*, and low yield is paid for, not prohibited. The correct
bookkeeping is the one the target profile mandates and Claim A omits:

```
total cost = per-attempt cost x (inverse success probability)
```

Claim A charges **per-attempt cost alone** (the table `B^(m/2)`). That is
precisely the failure mode `docs/target-result-profile.md` A3 and the Red Team
contract name explicitly, and here it is not a presentational slip: it is what
produces the wrong premise. Once the inverse-success factor is charged, `B` well
*below* `(m! p)^(1/m)` becomes optimal, because the extra targets are cheap and
the table is not.

Numerically, over the full class model (see §3), optimising `beta` and the split:

```
   m    optimal beta      1/m      class exponent
   4        0.148        0.250        0.578
   5        0.117        0.200        0.563
   6        0.098        0.167        0.553
  10        0.062        0.100        0.535
```

The optimum is roughly **half** the "forced" `1/m` at `m = 5`. So the premise is
not merely unproven — the class's own best member violates it.

### 2c. The `m!`, and ordered vs unordered

The `m!` is correct for unordered decompositions and is the right normalisation:
the exact count is `C(B,m)`, and `B^m/m!` overstates it by `1 + O(m^2/B)`. The
`m!` therefore *helps* the closure (fewer distinct subsets than `B^m`), and the
penalty is visible at finite `N`: at `N = 2^256, m = 4` the numerical optimum is
`0.5779` against the asymptotic `4/7 = 0.5714`, closing to `0.5731` at
`N = 2^1024`. Nothing here is a problem for Claim A.

---

## 3. Step 2 — is `B^(m/2)` a lower bound on the larger side? **No.** Here is every attack I ran on the quantifier.

Model, uniform across all attacks. A member of the class stores the sums of
`m1`-subsets of `F` (`W1 = B^m1/m1!` entries, built once, target-independent) and
probes with `W2` entries assembled from the remaining `m2 = m - m1` summands and
a stream of `tau` targets. One hash lookup adjudicates a whole table, so the
number of (candidate `m`-subset, target) pairs adjudicated is `W1 * W2`; each
pair is a relation with probability `1/N`; `~B` relations are needed to solve for
`B` factor-base logs. Time `T = W1 + W2`, memory `>= max(W1, W2)`.

I verified the "one lookup adjudicates a whole table at rate `1/N`" accounting
directly, on a real prime-order curve (`y^2 = x^3 + 2` over `F_100003`,
`N = 99667`) **and** against the null object (`Z/N`, same order, no curve):

```
mode   B  m   W1=C(B,m)   tau    pairs=W1*tau   predicted W1*tau/N   observed rels
EC    24  4       10626   4000       42504000              426.46             418
NULL  24  4       10626   4000       42504000              426.46             461
EC    20  5       15504   4000       62016000              622.23             612
NULL  20  5       15504   4000       62016000              622.23             623
EC    24  5       42504   4000      170016000             1705.84            1772
NULL  24  5       42504   4000      170016000             1705.84            1691
```

Predicted and observed agree within noise, and **the curve and the structureless
null agree with each other** — the counting has no elliptic-curve content, which
is the object-level control `DEC-20260801-003` taught this campaign to demand and
which Claim A's counting step passes cleanly.

### Attack 1 — unbalanced splits. **Succeeds against Claim A; conclusion survives.**

Minimising `max(W1, W2)` subject to `W1*W2 >= B*N` gives `W1 = W2 = sqrt(B*N)`,
so the optimum is set by the *product*, not by balance across the `m` summands.
The best split is the **maximally unbalanced** one — store all `m`-subset sums,
join against the target table — because that is the largest store the class
admits and therefore the one that lets `B` drop furthest.

The numerical optimiser picks `m1 = m` at every `m` and every `N` tested. So
"every balanced meet-in-the-middle claw" does not quantify over the class's best
member, and the "larger side" of that member is `B^m/m!`, not `B^(m/2)`.

### Attack 2 — accepting lower success probability per attempt. **Succeeds against Claim A; conclusion survives.**

This is §2b. It is not a separate attack so much as the same one: subsetting one
side and paying more attempts is exactly what moves the optimum below `p^(1/m)`,
and at `B < p^(1/m)` the quantity `B^(m/2)` is **below** `p^(1/2)`. The stated
inequality chain fails at its last link precisely in the regime that matters.

### Attack 3 — closed form for the class, and the matching lower bound. **Fails to break 1/2.**

Adjudicated pairs across the whole run are bounded by `T^2/4` (a hash join of two
tables of sizes `W1, W2` costs `W1 + W2` and adjudicates `W1*W2`; by AM-GM the
sum of such products at total work `T` is maximised by one join, at `T^2/4`).
Needing `B*N` pairs gives

```
   T >= 2*sqrt(B*N)                                   (LB-1)
```

which already yields `T >= 2*sqrt(N)`, and is strict for any `B > 1`. The store
is capped at `B^m/m!`, so `W1 = sqrt(B*N)` is reachable only when
`B^(2m-1) >= (m!)^2 * N`; balancing at the cap gives

```
   optimal beta = 1/(2m-1),   T = N^(m/(2m-1)) = N^(1/2 + 1/(2(2m-1)))
```

The numerical optimiser reproduces this closed form, approaching it from above as
`N` grows (the gap is the `m!`):

```
   m    N=2^256      N=2^1024     closed form m/(2m-1)
   3     0.6060       0.6015            0.6000
   4     0.5779       0.5731            0.5714
   5     0.5625       0.5573            0.5556
   6     0.5527       0.5473            0.5455
  10     0.5347       0.5284            0.5263
  32     0.5192       0.5108            0.5079
```

Memory equals time in this class. **Rho is `N^(1/2)` with `O(1)` memory, so the
class is dominated on both axes at every arity, strictly.**

If one insists the class only covers joins between two *factor-base* sides
(`m1 <= m-1`, no target table), the floor is `(m-1)/(2m-3)`: `0.600` at `m = 4`,
`0.571` at `m = 5`. Same conclusion.

### Attack 4 — multi-level / recursive joins (the serious one). **Fails on `E(F_p)` — and this is the actual obstruction.**

Wagner's k-tree is a multi-level join and is squarely inside "enumerate sums of
subsets and join them." It defeats (LB-1), because its intermediate filters raise
the per-adjudicated-pair hit rate from `1/N` to `2^ell/N`. Taking `k = 2^j` leaf
lists, each the set of `(m/k)`-subset sums, the counterfactual exponent is
`(2^j + m)/(m(j+1))`:

```
   j  k     m     beta      exponent
   2  4     8    0.167       0.5000
   2  4    16    0.083       0.4167     <-- below 1/2
   3  8    16    0.125       0.3750     <-- below 1/2
   3  8    32    0.063       0.3125
```

(The cost-per-solution scaling I used matches Wagner's own statement for `k = 4`:
`alpha^3` solutions at `alpha x` the work of one.)

**So if a k-tree were available, this class would break 1/2 — and Claim A's
counting argument does nothing to prevent it.** Claim A's obstruction is
therefore not the real obstruction. The real one is structural, and I measured
it. Wagner needs a cheap map `h` with `h(P+Q)` predictable from `h(P), h(Q)`
*without forming `P+Q`*. Predictability of `h(sum)` from the pair of `h`-values,
20000 samples per cell, `h` = low `ell` bits:

```
 ell   M     Z/N (low bits)    E(F_p) (low bits of x)    pure chance 1/M
   1   2           0.4997                     0.4991             0.5000
   2   4           0.4985                     0.2542             0.2500
   3   8           0.5032                     0.1296             0.1250
   4  16           0.5006                     0.0635             0.0625
```

In `Z/N` the sum's low bits are pinned to **two** candidates regardless of `ell`
(the single mod-`N` reduction ambiguity) — the filter works, and this is why
Wagner works over the integers. On the curve the predictability is
**indistinguishable from chance at every `ell`** — `x(P+Q)` carries no usable
partial information from `x(P), x(Q)`. This is the null-object control the
inventor protocol asks for, and it is decisive: **on `E(F_p)` every join in the
class must be an exact-equality join, so (LB-1) applies and the k-tree escape is
closed.**

This is also exactly the shadow one expects from Shoup's generic lower bound:
index calculus escapes `sqrt(N)` only through non-generic structure, and prime-field
`E(F_p)` supplies none *at the group level*. The only candidate non-generic
structure is algebraic (summation polynomials) — which is outside the class.

### Attack 5 — sharing work across many targets (`IDEA-20260731-010`). **Fails to break 1/2, but Claim A does not cover it and must not be read as closing it.**

(LB-1) already permits unlimited sharing: the store is built once, the target
stream is in the pair count. Extending the model to `T = N^t` targets with
per-target descent cost `N/W1`:

```
 t        class total    Kuhn-Struik sqrt(T*N)    class - KS    class memory exp
 0.000       0.5625                   0.5000        +0.0625              0.5585
 0.100       0.5625                   0.5500        +0.0125              0.5585
 0.111       0.5625                   0.5556        +0.0069              0.5585
 0.200       0.6020                   0.6000        +0.0020              0.5980
 0.500       0.8019                   0.7500        +0.0519              0.6981
```

Analytically the optimum is `W1 = sqrt(B*N)` and per-target descent
`sqrt(N/B)`, balancing at `B = T` for a total of `2*sqrt(T*N)` — **exactly
Kuhn–Struik, never better**, with `N^(0.56)` memory against Kuhn–Struik's
negligible memory. The residual `+0.0069` at the crossover is the `m!` at
`N = 2^256`.

The consequence for `IDEA-20260731-010`: its headline prediction ("amortised
per-target exponent falls below 1/2 for `T >= N^0.1`") is **true and
uninteresting** — matched *multi-target* rho does the same thing for free. Its
baseline must be Kuhn–Struik, not `0.886*sqrt(N)` single-target rho. That is a
correction to that record's comparison, not a closure of it, and Claim A as
written provides neither.

### Attack 6 — a factor base that is not a coordinate box. **Fails to break 1/2.**

The mean-yield identity `C(B,m)/N` holds for *every* `F`, so a structured `F`
cannot raise average yield; it can only concentrate decompositions onto fewer
targets, which is strictly bad when targets are uniform (and `R_j = a_j P + b_j Q`
with random `a_j, b_j` is uniform). A factor base with internal known relations
reduces the unknown count, but then `B` should be read as the number of unknowns.
Keying on `x`-coordinates rather than points costs a factor `2^m` — a constant.
Claim A's "identically ... in the choice of `F`" leg survives, and is in fact the
strongest part of the claim.

### Summary of the quantifier attacks

| Attack | Breaks Claim A's stated bound? | Breaks the 1/2 floor? |
|---|---|---|
| 1. unbalanced splits | **yes** | no |
| 2. low yield / more attempts | **yes** | no |
| 3. full class optimisation | **yes** (floor is `m/(2m-1)`, not `1/2`) | no |
| 4. k-tree / multi-level joins | **yes** (uncovered by the argument) | **would**, but no sum-compatible filter exists on `E(F_p)` — measured |
| 5. multi-target sharing | n/a (outside the stated argument) | no; ties Kuhn–Struik at best |
| 6. non-box factor base | no | no |

---

## 4. Step 3 — does `B^(m/2) >= p^(1/2)` follow from `B >= (m! p)^(1/m)`?

**Yes, the inequality direction is fine.** `(m! p)^(1/m) = (m!)^(1/m) * p^(1/m)
>= p^(1/m)` since `m! >= 1`, so the hypothesis is *stronger* than `B >= p^(1/m)`
and implies it; then `B^(m/2) >= p^(1/2)`. The `m!` helps and does not hurt.

This step is the one part of the chain that is valid. It is also the part that
does not matter, because the hypothesis it consumes is false (§2).

**On the asymptotic regime.** Claim A does not say whether `m` is fixed or
growing, and it must. With `m` fixed the floor is `m/(2m-1) > 1/2` strictly.
`1/2` is reached only as `m -> infinity`, which requires `m! <= N^o(1)`, i.e.
`m log m = o(log N)`. So the honest asymptotic statement is
`1/2 + Theta(1/m)` for fixed `m`, and `1/2 + o(1)` for slowly growing `m` —
never `1/2` and never below.

---

## 5. Step 4 — is the scope stated correctly? What sits OUTSIDE the closure.

`interpretation_limits` in the record does scope Claim A honestly ("it says
nothing about procedures that do not [enumerate and join]"). But the headline —
"the class is CLOSED at exponent 1/2 with that mechanism named" — reads far
broader than what is closed, and a later session skimming the claim field will
over-read it. **The closed class is a small corner of prime-field ECDLP index
calculus, not its mainline.** Explicitly outside:

1. **Every algebraic decomposition oracle.** Semaev summation polynomials solved
   by Gröbner or resultant methods — i.e. essentially the entire published
   prime-field index-calculus literature — is *not* an enumerate-and-join
   procedure. It does not enumerate the box; it solves a variety. This is the
   single most important exclusion and it means the closure does **not**
   retrospectively explain the literature; it explains this program's own
   degree-split lane.
2. **Lattice small-root / box-constrained solving** — Claim B's own subject.
   Claim A explicitly leaves it open, correctly.
3. **Any procedure with a sum-compatible filter** on `E(F_p)`. Measured absent
   (§3, Attack 4), not proven absent. This is where the falsifier lives.
4. **Preprocessing / non-uniform models.** Corrigan-Gibbs–Kogan give online
   `N^(1/3)` after `N^(2/3)` advice. Already below `1/2` and untouched here. The
   closure must never be phrased as "nothing beats `1/2` on prime-field ECDLP."
5. **Multi-target amortisation** as an accounting regime (§3, Attack 5). The
   class ties Kuhn–Struik; the closure statement must name Kuhn–Struik as the
   baseline or it will be mis-scored.
6. **Extension fields.** Gaudry/Diem-style Weil-restriction index calculus over
   `F_(q^n)` is a different class with genuinely better exponents. Nothing here
   applies.
7. **Non-uniform targets** (small-interval / structured `x`), quantum, descent
   with a specially structured target, and factor bases whose points have partly
   known logarithms.

---

## 6. Step 5 — the retrospective attribution. **Partly right, and it must not be recorded as written.**

Claim A says the degree-split lane's "assembled figure of about 1/2, recorded at
RT047-H3 inside `DEC-20260801-003`, is therefore not a parameter accident but an
instance of this identity."

I checked the record rather than assuming. Three findings.

**(a) The arithmetic identity is real.** RT047-H3 evaluates
`IDEA-20260731-007`'s own formula `E = max(beta*m/2, omega_LA*beta)` at
`m = 5, beta = 1/5, omega_LA = 2`, giving `max(0.5, 0.4, 0.2) ~ 1/2`. The `0.5`
is literally `beta*m/2` at `beta = 1/m`, which is `B^(m/2) = p^(1/2)`. So the
number is not a coincidence of parameters; it is that identity. **That much of
the attribution is correct.**

**(b) It is not a measurement, and the task framing "measured ~1/2" is wrong.**
RT047-H3 is a red-team *calculation from the proposal's own formula*. The record
is explicit that no exponent was measured: `DEC-20260801-003`
`asymptotic_promotion_gates.note` and `EV-DS-003` N-6 both record
`assembled_E_proxy = null`, status `"not_computed (out of control scope)"`. The
nearest actual measurement is `EV-DS-002` O-7: *"assembled_E_proxy never <0.45 on
completed cells (min ~0.65)"* — i.e. the measured proxy never came near `0.5`; it
sat around `0.65`. Any promoted text saying the lane "measured ~1/2" would be a
fabrication under `AGENTS.md` rule 5.

**(c) The `1/2` is itself an undercount, produced by the same error as Claim A.**
`IDEA-20260731-007`'s formula charges the claw table and the linear algebra and
omits the inverse-success-probability factor. Charged in full, the class cost at
that exact parameter point (`m = 5`, balanced split, `beta = 1/m = 0.2`) is
**`0.60`**, not `0.50`:

```
   m   beta=1/m   Claim A quotes B^(m/2)   full class cost at that point   class optimum
   4     0.250              0.500                          0.750               0.571
   5     0.200              0.500                          0.600               0.556
   6     0.167              0.500                          0.667               0.545
```

**Ruling.** The retrospective attribution is a *post-hoc fit of one error to
another*. The `1/2` at RT047-H3 and the `1/2` in Claim A are the same
quantity — `beta*m/2` at `beta = 1/m` — because both records commit the same
omission (per-attempt cost charged without the inverse-success factor). Calling
the agreement a structural identity dresses a shared mistake as a discovery. The
true class exponent at that parameter point is `0.60` and the class optimum is
`0.556`; neither is `1/2`. Record the agreement as *"both records used the same
incomplete cost model"*, not as *"the lane's exponent was pinned by an
identity."*

The weaker claim that survives, and is worth recording: **the degree-split lane
could never have moved an exponent**, because its entire class floors at
`m/(2m-1) > 1/2` with `N^(m/(2m-1))` memory. Five batches of instrument repair
were spent on a construction that a two-line cost balance excludes. That
retrospective judgement is correct and is the durable content — reached by the
corrected argument, not by Claim A's.

---

## 7. The statement I would be willing to see promoted

Phrased so a later session can falsify it. Conditional dependencies named.
Requires independent `review-breakthrough` at `max` on a distinct resolved model
before promotion (`AGENTS.md` rule 12); this session cannot supply that.

> **KN-FIND candidate — the exact-match join floor for prime-field ECDLP relation search.**
>
> *Scope.* Prime-field ECDLP, `E(F_p)` with prime-order subgroup of order `N`,
> factor base `F` of size `B`, arity `m` fixed or growing with `m log m = o(log N)`,
> targets `R_j = a_j P + b_j Q` uniform and independent of `F`. Class: procedures
> that (i) form group elements only as sums of subsets of `F` and of targets, and
> (ii) locate relations only by exact-equality lookups/joins between stored lists
> of such elements. Cost unit: group operations; memory: stored group elements.
>
> *Statement.* Let `T` be total time and `W` the largest stored list. A hash join
> of lists of sizes `W1, W2` costs `W1+W2` and adjudicates `W1*W2` candidate
> (subset, target) pairs, each a relation with probability `1/N` (exact in
> expectation, by linearity, for uniform targets independent of `F`). Collecting
> the `~B` relations needed to determine `B` factor-base logarithms therefore
> requires `>= B*N` adjudicated pairs, whence
>
>     T >= 2*sqrt(B*N),  and memory >= sqrt(B*N) at the optimum.
>
> With the store capped at `C(B,m) <= B^m/m!`, the class optimum is
>
>     beta = 1/(2m-1),  time = memory = N^(m/(2m-1)) = N^(1/2 + 1/(2(2m-1))).
>
> Restricted to joins between two factor-base sides, the floor is
> `N^((m-1)/(2m-3))`. Both are **strictly above** `N^(1/2)` at every finite `m`
> and tend to `N^(1/2)` from above. With `T = N^t` targets and one shared matrix,
> the class total is `max(N^(m/(2m-1)), 2*sqrt(T*N))`, which **ties and never
> beats** Kuhn–Struik multi-target rho while using `N^(m/(2m-1))` memory against
> its negligible memory.
>
> *`dominated_by`.* Pollard rho (time `0.886*sqrt(N)`, `O(1)` memory) on time and
> on memory at every `m`; BSGS on time–memory product; Kuhn–Struik `sqrt(T*N)` in
> the multi-target regime, at equality on time and dominating on memory;
> Corrigan-Gibbs–Kogan `ST^2 = Omega(eps*N)` preprocessing frontier
> (`N^(1/3)` online after `N^(2/3)` advice) in the preprocessing model. All four
> rows checked across time, memory, and data/queries. `null` is inadmissible.
>
> *`sota_delta`.* Zero on every axis; the deliverable is a named obstruction plus
> an exact class floor.
>
> *Named obstruction (§4 of the inventor protocol).* Two conjuncts.
> **(O1) Adjudication bound.** Exact-equality joins adjudicate at most `T^2/4`
> pairs at hit rate `1/N`, giving `T >= 2*sqrt(B*N)`.
> **(O2) No sum-compatible filter on `E(F_p)`.** Multi-level (Wagner k-tree)
> joins would defeat (O1) by raising the hit rate to `2^ell/N`, and would put the
> class at `(2^j+m)/(m(j+1))` — `0.4167` at `j=2, m=16`; `0.375` at `j=3, m=16` —
> i.e. **below `1/2`**. They are unavailable because no cheap map `h` is known
> with `h(P+Q)` predictable from `h(P), h(Q)` without forming `P+Q`. Measured:
> low-bit predictability is `~1/M` (pure chance) on `E(F_p)` at
> `M = 2,4,8,16` against `~1/2` (two candidates, independent of `M`) on `Z/N`,
> 20000 samples per cell.
>
> *Forward guidance — what remains open.* Algebraic decomposition oracles
> (Gröbner/resultant on `S_(m+1)`, symmetry-reduced formulations, box-aware term
> orders); lattice small-root solving (`IDEA-20260802-003` Claim B); hybrid
> partial-enumeration/solve splits whose exponent interpolates; preprocessing and
> non-uniform models; extension fields; non-uniform targets; and **the search for
> a sum-compatible filter on `E(F_p)`, which (O2) identifies as the single
> highest-value object in this direction.**
>
> *Falsification — this closure is false if any of the following is exhibited.*
> **F1.** A map `h: E(F_p) -> [M]`, `M >= 4`, computable in `o(1)` group
> operations, with `Pr[h(P+Q) = f(h(P),h(Q))] >= 4/M` for some `f` over uniform
> `P, Q`. The measurement in (O2) is the test; it currently returns `1/M` to
> within sampling noise. Such an `h` puts the class below `1/2` by the k-tree
> arithmetic above.
> **F2.** A join primitive that adjudicates `omega(W1*W2)` pairs at cost
> `W1+W2`, or an adaptive procedure whose adjudicated pairs hit at rate
> `omega(1/N)` without such a filter — either breaks (O1).
> **F3.** A relation-search procedure needing `o(B)` relations for `B` unknowns,
> or a factor base whose logarithms are partly known at no cost.
> **F4.** A target distribution in the intended attack that is not uniform and
> independent of `F`, which invalidates the `1/N` hit rate.
> **F5.** Empirically: a measured relation-collection cost below `2*sqrt(B*N)`
> group operations, with certificates, on any instance in the class. This is
> directly measurable at toy scale today and no run in the `EXP-DS-001` series
> has ever reported it.

Note that F1–F5 are all *cheap* and F1/F5 are runnable this week. That is what
makes this a closure rather than a fatigue report.

---

## 8. Required controls, if any of this is taken further

1. **Null-object control, already run here and reusable.** Every counting claim in
   this lane must be re-run on `Z/N` of the same order. The `EC ~ NULL` agreement
   in §3 is the controlled null for the yield counting; treat any future measured
   "structure" in yield as an artifact until it separates from that null.
2. **The artifact tell for this class.** The quantity that must decay is the
   relation-collection cost as `B` grows past `N^(1/(2m-1))`: it should *rise*
   like `B^m`, and the per-target probe count should *fall* like `N/W1`. A cost
   flat in `B` means the harness is not exercising the store. `UC-2` in
   `EV-DS-003` records that nobody has run this `B`-sweep. It is still the right
   next measurement for `EXP-DS-001`.
3. **F1 as a standing control.** Re-run the low-bit predictability measurement at
   larger `p`, at more `ell`, and with non-trivial `h` candidates (`x mod q` for
   small primes `q`, Legendre symbols, short Weierstrass invariants). Cost:
   minutes. This is the cheapest possible test of the one conjunct on which the
   whole closure rests.

## 9. One next concrete action

**Do not admit Claim A to the ledger as written.** Instead, open a scoped
derivation task that re-derives the closure in the §7 form — `T >= 2*sqrt(B*N)`,
class optimum `N^(m/(2m-1))`, obstruction (O1)+(O2), falsifiers F1–F5 — as a
single-responsibility derivation artifact under
`docs/claims-and-verification.md` (`derivation`, never "proved"), with the F1
predictability control re-run at `p ~ 2^32` and `ell` up to 8 as its one
attached measurement. Route the resulting record to independent
`review-breakthrough` at `max` on a resolved model distinct from
`claude-opus-5` before any promotion, since it is a closure claim
(`AGENTS.md` rule 12). If three distinct models cannot be resolved, record the
derivation and leave the closure `unverified` — an unattested closure is worse
than an open lane.

## 10. Note on Claim B (out of scope, one line as permitted)

Claim A's unsoundness does **not** reduce Claim B's value, and the corrected
closure slightly *raises* it. The corrected floor `m/(2m-1)` is strictly worse
than rho at every `m`, so the enumerate-and-join lane is deader than Claim A
said, which makes the algebraic-oracle escape the only live route and Claim B's
`X_max(m, p, t)` curve the right thing to measure. But Claim B's positive branch
inherits `IDEA-20260727-003`'s exponent arithmetic, which rests on the same
`beta >= 1/m` premise refuted in §2 — the free-oracle floor should be
re-derived without that constraint before the `omega_LA/m` figure is quoted
again.

---

## Inference

```yaml
inference:
  requested_policy: review-xhigh
  resolved_model_id: claude-opus-5
  reasoning_effort: null
  fallback_used: true
  fallback_reason: >-
    This Claude Code harness cannot resolve the policy aliases in
    orchestration/model-policies.yaml; subagent frontmatter supports only Claude
    models. Recorded, never silently substituted (AGENTS.md rule 11).
    Consequence disclosed at the head of this document: author and reviewer
    resolve to the same model, so independence here is procedural, not
    model-level.
  degraded_allowed: false
  degraded_requirements: []
  model_verified: false
  model_verified_reason: >-
    `python3 -m orchestration.adapter doctor --probe` was not run in this
    session. The identifier is unverified configuration.
```

Computations backing every table above were run in this session under
`scratchpad/{count,opt,sim,filter,multi}.py`. They are scratch, not archived
artifacts; any promotion must re-run them inside an experiment directory with
the standard receipt package.
