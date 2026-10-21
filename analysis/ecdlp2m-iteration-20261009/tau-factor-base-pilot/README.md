# tau factor-base pilot: what the Frobenius buys in relation collection on toy Koblitz curves

**Status: exploratory, hypothesis-generating pilot. NOT program evidence.** Produced in
one interactive session by the scripts in this directory. No `RUN-*` manifest exists and
none is invented (AGENTS.md rule 5). No ledger record was written or changed; nothing here
supports a hypothesis status change. Every number below is derived from
`results/cells.jsonl` by `aggregate.py`; `aggregate.md` is that output and carries the sha256
of every input. Nothing was run against ECC2K-130 or any deployed parameter.

## Question

On a Koblitz curve the Frobenius `tau: (x,y) -> (x^2,y^2)` acts on the prime-order subgroup
as multiplication by a scalar `mu`, so a factor base closed under `tau` and negation can be
reduced to `<tau,-1>`-orbit representatives: the literature (`KN-LIT-004`, Faugere-Gaudry-
Huot-Renault 2014; Galbraith-Gebregiyorgis 2014, `KN-LIT-439`/`KN-LIT-95d1e4`) prices this at
"about `2n`" on the factor base, provided the base is a union of orbits. The program's
default descent subspace `V_poly = {x : deg x < k}` is not `tau`-stable. Measured, not
estimated: how many bits of relation-collection cost does `tau` actually buy for each choice
of `V`, and does a `tau`-friendly `V` change the decomposition probability or the relation
yield?

## Object

Toy Koblitz curves `E_a: y^2 + xy = x^3 + a x^2 + 1 / F_{2^n}`, `n in {11,13,17,19,23}`,
with `a` chosen so that `#E = h * r` with `r` prime (`h = 2` for `a = 1`, `h = 4` for
`a = 0`). The order comes from the Koblitz trace recursion and is checked against an
exhaustive point count (`results/curves.jsonl`, both agree on every row). All factor-base
points and all targets lie in the order-`r` subgroup; `mu` is the root of
`X^2 - t_1 X + 2 = 0 mod r` verified by `tau(P) = mu*P` on random points.

| n | a | #E | h | r | mu |
|---|---|---|---|---|---|
| 11 | 1 | 1982 | 2 | 991 | 947 |
| 13 | 0 | 8012 | 4 | 2003 | 89 |
| 17 | 1 | 131174 | 2 | 65587 | 17184 |
| 19 | 0 | 523492 | 4 | 130873 | 41811 |
| 23 | 0 | 8383412 | 4 | 2095853 | 93194 |

Three factor-base families, each a set `V` of `x`-values with `FB = {P in <G> : x(P) in V}`:

- `V_poly`: `{x : deg x < k}` in the polynomial basis (program default).
- `V_nb`: span of `k` consecutive conjugates `beta, beta^2, ..., beta^(2^(k-1))` of a normal
  element `beta` (found by the rank test on its conjugates); `tau` maps it to the next window.
- `V_orb`: a union of random `tau`-orbits of `x`-values, chosen so that `|FB|` matches the
  `V_poly` cell as closely as whole orbits allow.

`k` ladder: `m = 2`: `k in {k0-1, k0, k0+1}`; `m = 3`: `k in {k0-1, k0, k0+1, k0+2}` with
`k0 = ceil(n/m)`. The ladder is shifted one step up from the brief's `{k0, k0-1}` because
subgroup membership costs a further `Tr(1/x)` (and, for `h = 4`, a halving) condition, so
`|FB| ~ |V|/2` or `|V|/4`, and the brief's `m = 3` cells had factor bases of 0 to 8 points.

## Method

`tau_fb_pilot.py` (pure Python 3 + numpy, log/antilog tables, deterministic seeds):

1. For each target `R` (4000 per cell at `m = 2`, 1500 at `m = 3`, times 3 independent
   replicates for `V_nb` and `V_orb` with a fresh normal element / fresh orbit draw), enumerate
   **all** decompositions `R = P_1 + ... + P_m`, `P_i in FB`, by meet-in-the-middle over
   `FB^(m-1)` with exact point arithmetic. Decompositions are multisets of factor-base points
   (both signs are in `FB`).
2. Record `p` = P(at least one decomposition), decompositions per attempt (`dpa`), and
   `rpa` = **distinct projected rows** per attempt: each decomposition is written over
   `<tau,-1>`-orbit representatives as `{rep : sum_i sign_i * mu^(j_i)} mod r`, and
   decompositions of one target that coincide after projection are counted once.
3. Record `orbits` = number of `tau`-orbits meeting `FB_x` (the orbit-reduced factor-base
   size; `<tau,-1>`-orbits of points correspond one-to-one to `tau`-orbits of `x` since
   `tau^j P = -P` forces `x in F_2`), `g = FB_x/orbits`, and for every decomposition the
   number of shifts `j` for which the conjugate relation `tau^j(R) = sum tau^j(P_i)` lies
   entirely inside `FB` again.
4. Compare `dpa` with `lambda = C(|FB|, m)/r`.

Gain accounting (derived). In the orbit-reduced matrix the unknowns are the `orbits`
logarithms of representatives and each distinct projected row is one equation; the conjugate
row `tau^j(rel)` is `mu^j` times the same equation and adds no rank. So relations needed =
`orbits`, attempts needed = `orbits / rpa`, and relative to `V_poly` with negation only
(unknowns `FB_x`, rows `rpa_poly`):

```
raw     = log2( (rpa_V / orbits_V) / (rpa_poly / FB_x_poly) )      at realised sizes
struct  = log2( g_V )                                               pure counting
dec     = log2( eff_V / eff_poly ),  eff = rpa / lambda             matched-size yield
matched = struct + dec                                              size-normalised gain
```

The same number computed in the *unreduced* matrix (rows = all usable conjugates, unknowns =
all points) is tabulated as a check; it equals `raw` whenever the base is an orbit union.
Multiplying rows by conjugates *and* dividing unknowns by orbits would double count. The
bound for `tau` alone is `log2(n)` (negation is shared by all three `V` and is not counted
in the comparison); the literature's `log2(2n)` includes negation.

## Result

Per-cell table, gain table, duplicate-row table and `V_nb` window table: `aggregate.md`.
The headline cells are `n = 23`, `m = 2` (the best populated, 12000 targets per `V`).

| n=23, m=2 | k | \|FB\| | orbits | g | p | rpa | lambda | eff | usable shifts of 23 | struct | dec | matched |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V_poly | 11 | 502 | 234 | 1.07 | 0.056 | 0.058 | 0.060 | 0.97 | 1.0 | 0.10 | 0 | 0.10 |
| V_nb | 11 | 551 | 136 | 2.02 | 0.072 | 0.074 | 0.074 | 1.01 | 1.7 | 1.02 | +0.07 | 1.08 |
| V_orb | 11 | 506 | 11 | 23.0 | 0.057 | 0.059 | 0.061 | 0.97 | 23 | 4.52 | +0.01 | 4.54 |
| V_poly | 12 | 1000 | 481 | 1.04 | 0.222 | 0.254 | 0.238 | 1.07 | 1.0 | 0.06 | 0 | 0.06 |
| V_nb | 12 | 1003 | 252 | 1.99 | 0.214 | 0.242 | 0.240 | 1.01 | 1.7 | 0.99 | -0.08 | 0.91 |
| V_orb | 12 | 1012 | 22 | 23.0 | 0.217 | 0.243 | 0.244 | 1.00 | 23 | 4.52 | -0.09 | 4.43 |
| V_poly | 13 | 2080 | 977 | 1.06 | 0.656 | 1.043 | 1.032 | 1.01 | 1.0 | 0.09 | 0 | 0.09 |
| V_nb | 13 | 1977 | 513 | 1.93 | 0.615 | 0.948 | 0.933 | 1.02 | 1.6 | 0.95 | +0.01 | 0.95 |
| V_orb | 13 | 2070 | 45 | 23.0 | 0.646 | 1.032 | 1.022 | 1.01 | 23 | 4.52 | 0.00 | 4.53 |

Summary over all cells with at least 300 projected rows in both the cell and its `V_poly`
baseline (`aggregate.md`, "Summary by V family"), bits:

| V | m | cells | struct mean [min,max] | dec mean [min,max] | matched mean [min,max] | log2(n) |
|---|---|---|---|---|---|---|
| V_poly (tau-aware) | 2 | 12 | 0.22 [0.03, 0.51] | 0 | 0.22 | 3.46-4.52 |
| V_nb | 2 | 12 | 1.01 [0.50, 1.32] | -0.03 [-0.10, 0.03] | 0.98 [0.45, 1.28] | 3.46-4.52 |
| V_orb | 2 | 12 | 3.97 [3.46, 4.52] | -0.15 [-0.57, 0.01] | 3.81 [2.89, 4.52] | 3.46-4.52 |
| V_poly (tau-aware) | 3 | 9 | 0.18 [0.00, 0.49] | 0 | 0.18 | 3.46-4.52 |
| V_nb | 3 | 9 | 0.95 [0.75, 1.19] | -0.14 [-0.41, -0.01] | 0.81 [0.45, 1.05] | 3.46-4.52 |
| V_orb | 3 | 8 | 3.91 [3.46, 4.52] | -0.82 [-1.57, -0.14] | 3.08 [1.89, 4.38] | 3.46-4.52 |

Measured facts:

1. **`V_orb` buys exactly `log2(n)` bits of structure** (`g = n` in every cell: 11, 13, 17,
   19, 23) and nothing beyond it. The decomposition yield at matched `|FB|` is unchanged:
   `dec` is within `+-0.1` bit in every `m = 2` cell with at least 11 orbits (all `n = 23`
   cells: +0.01, -0.09, 0.00).
2. **`V_nb` buys about 1 bit, not `log2(n)`.** `g = 1.93-2.02` at `n = 23` and `0.95-1.32`
   bits across all cells. Reason (derived, confirmed by the counts): `V_nb` and `tau(V_nb)`
   share a `(k-1)`-dimensional subspace, so an element whose normal-basis support spans `L`
   consecutive positions sits in `k-L+1` of the windows, and summing `1/(k-L+1)` over the
   window gives about `|V_nb|/2` orbits. Inside the window only 1.55-1.89 of the `n` conjugates
   of a relation are usable at `m = 2` for `n >= 17` (8-10 % of the orbit; up to 2.2 of 11
   at `n = 11`) and 1.1-1.5 at `m = 3` (5-14 %). The union of all `n` windows is itself an orbit union (`|FB_U|/orbits = 2n`
   exactly in every row), i.e. a `V_orb` of a different size, not a free gain.
3. **`V_poly` already contains a small free `tau` coincidence**: `g = 1.02-1.43`, 0.03-0.5
   bit, because squaring maps `deg < k/2` into `deg < k`; it shrinks with `n`
   (0.06-0.10 bit at `n = 23`). Usable conjugates per relation: 1.00-1.28.
4. **Heuristic check (d).** For `V_poly`, `m = 2`: `dpa / lambda_r = 0.97-1.07` for
   `n >= 17` (1.13-1.21 only in the two smallest cells with `|FB| = 14`), and `p` matches
   `1 - exp(-lambda_r)` to within 0.01. The brief's formula with `#E` in place of `r` is off
   by exactly the cofactor (`dpa/lambda_E = 2.0-2.3` for `h = 2`, `3.9-4.8` for `h = 4`):
   with factor base and targets in the prime subgroup the correct denominator is `r`.
5. **Projected-row duplication is a real mechanism and the only place `tau`-friendliness
   changes the yield.** Two decompositions of one target that differ by a kernel identity of
   the `tau`-module (`tau^2 - t_1 tau + 2 = 0`, e.g. `2 tau^i Q = -(tau^(i+1) Q + tau^(i+2) Q)`
   up to the sign of `t_1`) are one row. With a single orbit every successful target yields
   exactly one row (`rpa = p`, 65 % of `m = 3` decompositions duplicate); the fraction falls
   with the orbit count: 1 orbit 0.26 (`m=2`) / 0.65 (`m=3`); 3 orbits 0.08 / 0.17; 5 orbits
   -- / 0.07; 11 orbits 0.011; 22-45 orbits 0.002 (`aggregate.md`, "Duplicate projected
   rows"). This is what drives the negative `dec` of `V_orb` at `m = 3`, where no toy cell
   has more than 5 orbits; it is a finite-size artefact of toy orbit counts, not a property
   that survives at `2^36` orbits, but it is also a warning for any toy-scale certified
   pipeline that counts decompositions as relations (compare the kernel identities the
   CERTBIN k = 2 audit found, `../certbin-k2-collision-audit/`).
6. **Unreduced check**: for `V_orb` the unreduced-matrix number equals `raw` in every cell;
   for `V_poly`/`V_nb` it is lower by exactly the unusable part of the orbit, as it must be.

## Reading (derived; not a decision)

- The bits `tau` buys in relation collection on a Koblitz curve are **`log2(n)` for an
  orbit-union factor base, about 1 for a normal-basis window, and 0.03-0.5 (vanishing with
  `n`) for the program's polynomial-basis subspace** -- and in all three cases the
  decomposition probability per attempt at matched `|FB|` is the birthday heuristic, within
  `+-0.1` bit once the base holds more than a handful of orbits. There is no second gain in the
  decomposition step: a `tau`-friendly `V` does not make a random target decompose more
  often.
- Against the literature bound: the measured `V_orb` gain is `log2(n)` exactly, which is the
  `tau` part of the `~2n` of `KN-LIT-004`; the negation factor 2 is available to every `V`
  and is not a `tau` effect. At `n = 131` this is 7.03 bits on the number of relations
  (and the same factor on the matrix dimension, so about 14 bits on dense linear algebra).
- Against what the program already measured: this reproduces, by exhaustive enumeration on
  five curves, the structural claims of `analysis/frobenius-orbit-ecc2k130/` (gain exactly
  `n = 131`, `2^7.03`, "and no more") and `KN-FIND-b9a41d` (the Frobenius quotient gains the
  mean orbit size `g <= n`, a constant factor), and it adds the two numbers neither had: a
  normal-basis window realises `g ~ 2`, and the polynomial-basis default realises
  `g ~ 1.05`. The per-solve cost side is unchanged from `KN-FIND-47da4e` / `EV-FROB-b6e1e9`
  (orbit-union encoding is cost-neutral at `m = 2`); the cost model of
  `frobenius-orbit-ecc2k130/README.md` already grants the full factor `n` and still finds
  `m = 2, 3` dead on linear algebra alone, so nothing here moves an exponent.
- A possible follow-up, not proposed as an experiment here: since `V_nb` costs the same
  Weil descent as `V_poly` (both are `F_2`-subspaces of dimension `k`) and buys about 1 bit
  on the orbit count for free, it is the only `tau`-friendly choice that does not change the
  solver's object; whether the descended system over a normal-basis window solves at the
  same cost as over the polynomial-basis window is the unmeasured half.

## Limitations

- Toy sizes `n <= 23`; orbit counts 1-45 (`m = 2`) and 1-5 (`m = 3`). The duplicate-row
  effect (fact 5) is therefore large at `m = 3` and the `m = 3` `V_orb` gain is reported as
  measured (`3.1` bits mean) rather than extrapolated; at the `2^36` orbits of a real
  `m = 3` base it would be `log2(n)`.
- `m = 2, 3` only, exhaustive enumeration; no Weil-descent solving cost measured. The gain
  is per *attempt*, and an attempt over `V_orb` is not a subspace system
  (`KN-FIND-47da4e`: `n` gauge-fixed systems or a one-hot encoding at the same cost).
- `|FB|` is matched between `V` families only up to whole orbits (`V_orb`) and up to the
  random `Tr(1/x)` / halving split (`V_nb`); `matched` normalises with the `|FB|^m` and `|FB|`
  scaling of the heuristic, which the `V_poly` check supports but which is a model.
- One normal element and one orbit draw per replicate, three replicates; `V_poly` has no
  randomness. Error bars on `eff` are Poisson on the row count.
- No linear algebra was run; `rpa` counts distinct projected rows, not rank.
- Single author, single session, no validator or red team; see the status line.

## Regenerate

```sh
cd analysis/ecdlp2m-iteration-20261009/tau-factor-base-pilot
python3 tau_fb_pilot.py            # ~25 min, 1 CPU, < 200 MB; writes results/*.jsonl, results/run.log
python3 aggregate.py > /dev/null   # writes aggregate.md
sha256sum -c SHA256SUMS
```

Defaults: `--ns 11,13,17,19,23 --targets2 4000 --targets3 1500 --reps 3 --seed 20261017`.
The run is deterministic given the seed (numpy `default_rng` seeded per cell by
`[seed, n, m, k, V, rep]`; `mu` search seeded by `[seed, n, 99]`).

## Files

- `tau_fb_pilot.py` -- field, curve, factor bases, exhaustive decomposition, projection.
- `aggregate.py` -- pools replicates, computes gains, writes `aggregate.md`.
- `results/cells.jsonl` -- one row per (n, m, k, V, rep) cell, 245 rows, 0 censored.
- `results/curves.jsonl` -- both `a` per `n`: order by recursion and by point count, primality of `r`.
- `results/run.log` -- console log of the run.
- `aggregate.md` -- all tables and the sha256 of every input.
