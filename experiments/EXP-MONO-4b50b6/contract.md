# EXP-MONO-4b50b6 — m=3 Semaev summation-cover cycle-type census (frozen contract)

- **Goal:** `GOAL-MONO-001` (Tier 2 / G5), parent `GOAL-PATH-001`
- **Question:** `RQ-MONO-001`, open problem `KN-OPEN-009`
- **Protocol:** `MONO-m3-census-1.1.0-repair-cm-gate`, frozen at
  `coordination/goals/GOAL-MONO-001/batches/BATCH-002/tasks/TASK-20260725-705/monodromy_protocol.yaml`
  (red-team PASS `RT-20260725-707`, evidence `EV-MONO-002`)
- **Execution authorized by:** `DEC-20260802-505759` (Coordinator, `GOAL-PATH-001`
  prioritization). The protocol card explicitly does not self-authorize; this
  contract exists only because that decision is committed.
- **Claim tier ceiling:** `toy`. Nothing here is a crypto-scale statement.

## 1. What is measured

For `E: y^2 = x^3 + A x + B` over `F_p` and each `(x1, x2) in F_p^2`, the third
Semaev summation polynomial specialises to the univariate

```
f_{x1,x2}(T) = S_3(x1, x2, T)
             = (x1 - x2)^2 * T^2
               - 2 * [ (x1 + x2)(x1 x2 + A) + 2B ] * T
               + [ (x1 x2 - A)^2 - 4B (x1 + x2) ]
```

and the measurement is its Frobenius cycle type over `F_p`:
`split_1_1`, `inert_2`, `ramified` (repeated root), `degree_drop` (leading
coefficient zero, i.e. `x1 == x2`).

`deg_T S_3 = 2 = 2^{m-2}` at `m = 3`, so the only transitive subgroup of the
fibre's symmetric group is `S_2` itself. "Full versus exceptional" therefore
discriminates *Chebotarev-consistent equidistribution* against *a positively
exhibited locus with systematically deviant densities*, exactly as the frozen
protocol states.

## 2. Derivation used by the harness (proved, then checked)

The harness reports the frozen sampled census as its primary deliverable and a
closed-form exact histogram alongside it. The closed form rests on one identity.

**Lemma.** As a polynomial identity in `Z[x1, x2, A, B]`, with
`f(x) = x^3 + A x + B`:

```
disc_T S_3(x1, x2, T) = 16 * f(x1) * f(x2)
```

*Proof.* Write `a = (x1-x2)^2`, `b = -2[(x1+x2)(x1x2+A)+2B]`,
`c = (x1x2-A)^2 - 4B(x1+x2)`; expand `b^2 - 4ac`. Equivalently and more
transparently: for points `P = (x1, y1)`, `Q = (x2, y2)` with `x1 != x2` the two
roots of `S_3(x1,x2,T)` are `x(P+Q)` and `x(P-Q)`, and the chord formula gives

```
x(P+Q) - x(P-Q) = [ (y2-y1)^2 - (y2+y1)^2 ] / (x2-x1)^2 = -4 y1 y2 / (x1-x2)^2,
```

so `disc / a^2 = (x(P+Q) - x(P-Q))^2 = 16 y1^2 y2^2 / (x1-x2)^4`, i.e.
`disc = 16 f(x1) f(x2)`. Verified symbolically (`sympy.expand`, difference
identically `0`) and numerically on every censused curve. **This is an elementary
consequence of the chord-and-tangent addition law and is not claimed as new
mathematics.**

**Corollary A (cycle type is a character product).** For `x1 != x2`, with `chi`
the quadratic character of `F_p`:

| condition | cycle type |
|---|---|
| `chi(f(x1)) = chi(f(x2)) != 0` | `split_1_1` |
| `chi(f(x1)) = -chi(f(x2))` | `inert_2` |
| `f(x1) f(x2) = 0` | `ramified` |
| `x1 = x2` | `degree_drop` |

**Corollary B (exact histogram).** Let `Z = #{x : f(x) = 0}`,
`S = #{x : chi(f(x)) = 1}`, `N = #{x : chi(f(x)) = -1}`, and
`#E(F_p) = 1 + Z + 2S = p + 1 - t`, so `S - N = -t` and `S + N = p - Z`. Over all
`p^2` pairs:

```
N_degdrop = p
N_ramified = p^2 - (p-Z)^2 - Z
N_split    = S^2 + N^2 - (p-Z)
N_inert    = 2 S N
```

(these sum to `p^2`), and therefore

```
freq_split - 1/2 = ( t^2 - 2pZ + Z^2 - 2p + 2Z ) / (2 p^2).
```

**Corollary C (an O(1/p) bound, not O(1/sqrt p)).** `Z in {0, 1, 3}` for a
squarefree cubic and `|t| <= 2 sqrt(p)` by Hasse, so

```
Z = 0:  |freq_split - 1/2| <= 1/p
Z = 1:  |freq_split - 1/2| <= 2/p          (approx)
Z = 3:  |freq_split - 1/2| <  4/p
```

uniformly over **every** `E/F_p` and every `p > 3`. The protocol's pinned
agreement envelope is `3 * (2/sqrt p)`; the true deviation is smaller by a factor
of order `sqrt(p)`.

**Corollary D (no exceptional locus at m = 3).** The identity is universal in
`(A, B)`. No curve — CM, `j = 0`, `j = 1728`, small discriminant, or otherwise —
can have `|freq_split - 1/2| >= 4/p`. Hypothesis B of the protocol's
`discrimination` block is therefore **empty at m = 3**, and this does not depend
on the census.

**Corollary E (the relation-rate independence assumption is false).** Every
element of a factor base `FB = {x(rG)}` is the x-coordinate of an `F_p`-rational
point, so `chi(f(x)) = +1` on `FB` (no `2`-torsion when the subgroup order is
odd). By Corollary A the fibre over `(x1, x2) in FB^2`, `x1 != x2`, **always
splits**. Hence

```
P(split | x1, x2 in FB, x1 != x2) = 1,     not  freq_split ~ 1/2,
```

and the protocol's `quasirandom_relation_prediction`
`freq_split * (W_eff/p)^2` understates the measured
`joint_relation_proxy_rate` by the factor `1/freq_split ~ 2` on the off-diagonal
(`~ 1.5` including the `x1 = x2` degree-drop diagonal at `W_eff = 4`).
**This is a constant factor. It moves no exponent.**

## 3. Frozen execution parameters (from the protocol, unchanged)

| parameter | value |
|---|---|
| primes | 211, 431, 809, 1601 |
| master seed | 20260725 |
| per-prime stream | `SHA-256("GOAL-MONO-001\|m3\|p=<p>\|seed=20260725")[:8]` big-endian |
| samples per curve | 30000, uniform `(x1,x2) in F_p^2` |
| random controls per prime | >= 20, ordinary, prime order, `j not in {0, 1728}` |
| curve search box | `A in [0, min(p-1,64)]`, `B in [1, min(p-1,64)]`, `4A^3+27B^2 != 0` |
| CM screen | >= 8 ordinary CM curves total, prime order **not** required (CTRL-CM-ADMISSION) |
| automorphism panel | `j in {0, 1728}`, quarantined, never in random aggregates |
| factor-base window | `W = 4`, `FB_W = {x(rG) : 1 <= r <= W}` |
| agreement envelope | `3 * (2 / sqrt p)` — **protocol pin, not a theorem** |

## 4. Instrument design

- **Two independent classifiers.** `classify_primary` uses discriminant +
  Legendre symbol (the protocol's `toy_allowed` route). `classify_secondary`
  scans `F_p` for roots and uses no discriminant formula. They are cross-checked
  on a deterministic 1-in-50 subsample of every curve's census, and any curve
  outside the envelope is fully re-censused on the secondary path before it may
  be called an exception (`reverification_rule`). Mismatch is
  `failed_infrastructure`, never exceptional evidence — confounder `CF-IMPL-FACTOR`.
- **Sampled vs exact.** Every curve's sampled `freq_split` is checked against
  Corollary B's exact value at 4 binomial sigma. This is an instrument check on
  the sampler and the closed form simultaneously.
- **`j` comparison is done in `F_p`.** `j = 1728` reduces to `127` at `p = 1601`,
  `110` at `p = 809`, `4` at `p = 431` and `40` at `p = 211`; comparing a reduced
  `j` against the integer `1728` would silently admit extra-automorphism curves
  into the random panel at every pinned prime. `is_extra_automorphism_j` compares
  `j mod p` against `0` and `1728 mod p`.
- **Degree-5 instrument controls** (`CTRL-IMON-*`, borrowed from `EXP-IMON-001`)
  use distinct-degree factorization, so the harness is shown able to *detect* a
  non-full group before any `S_2` agreement is trusted.

## 5. Outcome vocabulary (protocol `barrier_aggregate_rule`)

Exactly one of `FULL_MONODROMY_BARRIER_TOY`, `RANDOM_PANEL_CALIBRATION_TOY`,
`EXCEPTIONAL_LOCUS_TOY`, `SCOPED_PROTOCOL_NO_GO`, computed mechanically by
`aggregate_outcome`. `FULL_MONODROMY_BARRIER_TOY` requires the CM hard gate
(`>= 8` scored ordinary CM curves under the admission override, zero reverified
CM exceptions) in addition to the random-panel tests.

## 6. Claim boundaries

- Toy primes only. **No extrapolation to 256-bit ECDLP.**
- Corollaries A–E are stated for **`m = 3` only**. At `m >= 4`,
  `deg_T S_m = 2^{m-2} >= 4`, the discriminant has no such factorization, and
  `KN-OPEN-009` remains **fully open**. Nothing here closes it for `m >= 4`.
- `joint_relation_proxy_rate` is the protocol's window proxy, not an
  index-calculus campaign. Corollary E corrects a *model* used for planning; it
  is not an attack improvement and confers no advantage over Pollard rho.
- The `3 * (2/sqrt p)` envelope is a protocol pin. Only the Chebotarev `1/2`
  prediction is theorem-backed by `KN-LIT-039` — and at `m = 3` Corollary B
  supersedes both with an exact equality.
- Timeouts, crashes and control failures are `failed_infrastructure`, never
  negative mathematical evidence.

## 7. Reproduction

```sh
python3 experiments/EXP-MONO-4b50b6/mono3_census.py \
  --primes 211 431 809 1601 --seed 20260725 --samples 30000 --window 4 --m 3 \
  --curves-per-prime 20 \
  --protocol-version MONO-m3-census-1.1.0-repair-cm-gate \
  --out experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-001/results.json
```

Deterministic given the pinned seeds; exit status `0` iff every declared control
passes.
