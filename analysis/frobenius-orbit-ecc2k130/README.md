# A Frobenius orbit-union factor base at ECC2K-130: a pre-compute audit

**Status: analysis note, not evidence.** Every number here is computed by
`orbit_fb_ecc2k130.py` in this directory. **Nothing was run against the
challenge**: there is no relation search, no decomposition solve, no attack on
any instance. It is a section-8 audit in the sense of
`docs/inventor-protocol.md` — exact baseline embedding and method ceiling at
one parameter point. No `RUN-*` manifest exists for it and none is invented
(AGENTS.md rule 5); it changes no hypothesis status and supports no claim.

Target: ECC2K-130, the **public Certicom challenge curve** `y^2 + xy = x^3 + 1`
over `F_{2^131}` (`KN-LIT-096`, `KN-LIT-661e97`). The audit/instance
distinction this note relies on is the one `RQ-ICPERF-94c86e` states for the
FIPS labels: parameters appear in a cost table, never as a target.

## Ownership is unresolved, deliberately

This note is **not filed under a goal**, and that is a finding in itself:

- `GOAL-FROB-6333a9` owns the Frobenius-stable-factor-base work but excludes
  "Deployed Koblitz / ECC2K-130 as attack instances" (`scope_exclusions[0]`);
  `RQ-FROB-7d8dd4` likewise bars deployed Koblitz parameters as instances.
- `RQ-QSP-f9bbdb` is the question that *does* permit ECC2K-130 ("Lawful
  defensive cryptanalysis on the public Certicom challenge curve and toy
  curves only"), but its ideation card `TASK-20260916-a93a2a` bars the
  Frobenius-orbit lens as *the idea* there: "use it as a component (the orbit
  column of the table), never as the idea."
- `GOAL-ECDLP2M-001` names "Frobenius-orbit and subfield-orbit relation
  generation" among its mechanism families and is the natural adopter, but
  today owns only `RQ-QSP-f9bbdb`.

Adoption is a Coordinator decision and is **not** taken here.

## The question

Can a Frobenius-stable factor base be used for index calculus at the real
ECC2K-130 parameters, and does the resulting pipeline beat Pollard rho with
the Frobenius and negation classes?

## What was computed

**A — field, curve, exact order.** `F_2[z]/(z^131 + z^13 + z^2 + z + 1)`
(irreducibility checked, not assumed). The order is derived from the Koblitz
trace recursion `t_m = t_1 t_{m-1} - 2 t_{m-2}` seeded by `#E(F_2) = 4`,
`t_1 = -1` — no SEA and no recall — giving

```
#E = 2722258935367507707729280517973639940516 = 2^2 * r
r  = 680564733841876926932320129493409985129   (prime, log2 r = 129.0)
```

`r` reproduces the literal committed in `EV-ICPERF-10c5fc` exactly, the Hasse
bound holds, and the computed order annihilates random curve points.

**B — the linear stable factor base does not exist.** `F_2^131` under `sigma`
is the `F_2[X]`-module `F_2[X]/(X^131 - 1)`, so its Frobenius-stable subspaces
correspond to the monic divisors of `X^131 - 1`. Since `ord_131(2) = 130`,
that polynomial splits as `(X+1) * Phi_131` with `Phi_131` irreducible, giving
**exactly four** stable subspaces, of dimensions

```
{0, 1, 130, 131}
```

Nothing in the index-calculus band `[2, 129]`. This independently re-derives
`IDEA-20260918-9abf42` at the target parameters.

**C — the orbit union exists and was built at real scale.** With `V'` a random
`F_2`-subspace of dimension 36 and `S = union_j sigma^j(V')`: `sigma^131` is
the identity, `sigma(V')` equals the shift-1 subspace, `sigma^131(V') = V'`,
every sampled orbit has size exactly 131 (131 is prime), and the shifted
copies meet in dimension 0 — so `|S| = 2^43.03` and `pi(S) = S` genuinely
holds. The object is real and constructible at `n = 131`.

**D — the gain it earns, verified on the curve.** On a real point of exact
order `r`, the Frobenius orbit has exactly 131 points and `sigma` acts as
multiplication by

```
mu = 196511074115861092422032515080945363956,  a root of mu^2 + mu + 2 = 0 mod r
ord_r(mu) = 131,  and all 131 powers are distinct
```

So one relation yields exactly 131, and the linear algebra runs at the
orbit-reduced dimension. The gain is `2^7.03` — **exactly `n`, and no more.**

## The cost, charged against rho

Balanced factor base `|S| = 2^(131/m)`, the full factor-`n` collapse granted on
relations and `n^2` on linear algebra, and — absurdly generously — **one
operation charged per decomposition solve**. Baseline: `2^60.9` expected rho
iterations with the Frobenius and negation classes (`KN-LIT-096`; that figure
is the authors' *estimate*, and the real public effort reached about `2^58.3`
iterations, ~17%, over 22 months, per `KN-LIT-661e97`).

| m | Semaev | \|FB\| | descended `F_2` vars | solves | linear algebra | floor | budget per solve for rho parity |
|---|---|---|---|---|---|---|---|
| 2 | `S_3` | `2^65.5` | 117 | `2^59.5` | **`2^116.9`** | `2^116.9` | `2^1.4` |
| 3 | `S_4` | `2^43.7` | 110 | `2^39.2` | **`2^73.3`** | `2^73.3` | `2^21.7` |
| 4 | `S_5` | `2^32.8` | 103 | `2^30.3` | `2^51.4` | `2^51.4` | `2^30.6` |
| 5 | `S_6` | `2^26.2` | 96 | `2^26.1` | `2^38.3` | `2^38.3` | `2^34.8` |
| 6 | `S_7` | `2^21.8` | 89 | `2^24.3` | `2^29.6` | `2^29.6` | `2^36.6` |

`m = 2` and `m = 3` are dead on **linear algebra alone**, before a single
solve is charged: `2^116.9` and `2^73.3` against rho's `2^60.9`. The orbit
collapse is already included in those numbers; it is what brings them down to
there.

For `m >= 4` the bookkeeping fits under rho, and the entire question collapses
to one quantity: **a single decomposition solve must cost under about `2^31`**
(at `m = 4`; `2^30.6`). That solve is a Weil-descended Semaev system in ~103
`F_2` unknowns. The rows that look roomier are worse, not better: `m = 5` and
`m = 6` need `S_6` and `S_7`, which are not constructible at this size.

## The finding

The orbit-union factor base is the **only** Frobenius-stable factor base
available at ECC2K-130 — part B rules out every linear one — and it is
constructible (part C). What it buys is exactly the factor `n = 131` on
relations and `n^2` on linear algebra (part D): the known constant-factor
lever, which rho already answers with its own `sqrt(2n)`. No exponent moves.

Whether the pipeline is viable therefore rests entirely on the per-solve cost
of decomposition — and that is precisely the quantity this program has already
measured, at toy sizes, and found **unmoved by the orbit structure**:
`EV-FROB-b6e1e9` / `KN-FIND-47da4e` report a one-hot-over-baseline conflict
ratio of 1.02, 1.02, 1.47, 1.15 on CaDiCaL at `n = 13, 17, 19, 23` and 1.00 to
1.21 on WDSat in both search modes — never below 1, approaching 1 from above.
The orbit parameterisation relabels the work rather than removing it.

That combination lands on `RQ-FROB-7d8dd4`'s decision target (a): a gain
confined to the constant factor `n` on the factor base and `n^2` on linear
algebra, with no change in decomposition cost per attempt.

## What this does NOT claim

- **No attack, no run, no instance.** Nothing was executed against the
  challenge. There is no relation search and no solve here at any `m`.
- **The toy ratio is not a proof.** A conflict count is a property of a
  search, not of the algebra — it is not a solving degree and not a lower
  bound. A better encoding or solver could move any row of
  `KN-FIND-47da4e`, and the per-solve cost at `n = 131` has **never been
  measured**; the `2^31` budget above is the target such a measurement would
  have to beat, not a demonstration that it cannot.
- **The cost model is a model.** It grants the attack every gain and charges
  one operation per solve; it is a *floor* for this pipeline shape, not an
  achievable cost, and not a security statement about ECC2K-130.
- **`m >= 4` is not evaluated on its own terms.** Those cells are dismissed on
  summation-polynomial constructibility, which is a literature judgement
  recorded here, not something this note measured.
- **Nothing about the linear stable factor bases at rich `n`.**
  `H-FROB-a5bf86` / `EXP-FROB-30006a` test `n = 41, 43`; different object,
  different cells. This note scores none of that hypothesis's predictions.

## Reproducing

```sh
/opt/conda-sage/bin/sage -python orbit_fb_ecc2k130.py --json results.json
```

Runs in under a minute. `results.json` in this directory is that command's
output. Part C draws a random `V'`, so its subspace-level facts (all booleans
and the orbit sizes) reproduce while the particular `V'` does not; parts A, B
and D's cost sweep are fully deterministic, and part D's `mu` is determined by
the curve, not the draw.
