# Which isogeny-class structure is available at cryptographic scale?

Screening note for `GOAL-ENDO-001`, lanes **L2** (`RQ-VOLC-f6253b`, volcano level
and endomorphism-ring depth) and **L3** (`RQ-JINV-8fc13a`, special *j*-invariants
and CM discriminant size).

**Status: analysis note, not an evidence record.** Nothing here transitions a
hypothesis, closes a lane, or claims a speedup. `sota_delta`: zero. It reports
which structural axes are *available* for named cryptographic curves, which is a
precondition question those two lanes currently assume rather than check.

Instrument: [`tools/isogeny_class_screen.py`](../../tools/isogeny_class_screen.py).

---

## 0. The question

`DECOMPOSITION.md` L2 and L3 measure whether volcano depth, small CM
discriminant, or special *j* changes any attack-cost functional. Both lanes
presuppose the structure is *present in the class under test*. For a named curve
that presupposition is decidable in advance, cheaply, from Frobenius data alone —
before any experiment is contracted.

Three standard facts do the work:

1. `End^0(E) = Q(sqrt(D))`, `D = t^2 - 4p`, is an **isogeny-class invariant**
   (Tate). Small CM discriminant and extra automorphisms (`j = 0` requires
   `D_0 = -3`; `j = 1728` requires `D_0 = -4`) are properties of the **class**,
   not of a vertex. If the class lacks them, no walk within it finds them.
2. Writing `D = f^2 * D_0` with `D_0` fundamental, the `ell`-volcano has depth
   `v_ell(f)`. If `ell` does not divide `f`, every rational `ell`-isogeny is
   **horizontal** and preserves `End(E)` exactly — there is no vertical
   direction to take at that `ell`.
3. The minimal norm of a non-integer element of `Z[pi]` is `|D|/4`; the minimal
   norm in the **maximal** order `O_K` is governed by `|D_0|`, not `|D|`.

Fact 3 is the one that is easy to get wrong, and getting it wrong inverts the
answer. `|D|/4` bounds `Z[pi]`, but `End(E)` may be a strictly larger order.
Reporting `|D|/4` as if it bounded `End(E)` would declare secp256k1 —
the standard GLV curve — free of small endomorphisms. The screen uses `D_0`.

## 1. Result for P-256

All figures reproduced by:

```bash
python3 tools/isogeny_class_screen.py --curve p256 --neighbours --ell 2,3,5,7,11,13
```

Parameters self-check before use (`G` on curve, `[n]G = O`, `[n-1]G = -G`).

| quantity | value |
| --- | --- |
| `t = p + 1 - n` | `89188191154553853111372247798585809583` (odd) |
| `D = t^2 - 4p` | negative, 258 bits ⇒ **ordinary** |
| square part of `\|D\|` over primes `< 2e5` | **1** |
| fundamental `D_0` with `\|D_0\| <= 1e5` | **none** (exhaustive) |
| `j(E) == 0` or `1728` | no |
| class size `h ~ sqrt\|D\|` | `~2^129` curves |

Three consequences, each following from the table rather than from sampling:

- **No volcano depth anywhere in the small-`ell` range.** The conductor `f` has
  no prime factor below `2e5`, so for every such `ell` the `ell`-isogeny graph
  through P-256 is a crater with no descending direction. Every small-`ell`
  neighbour satisfies `End(E') = End(E)` **exactly**. Volcano position is not a
  free variable for this curve. This closes the L2 axis for P-256 specifically.
- **No small CM discriminant, and no `j = 0` / `j = 1728` in the class.** Since
  `D_0` is a class invariant and no fundamental `D_0` with `|D_0| <= 1e5`
  divides `D` with square quotient, `|D_0| > 1e5` is proven. This closes the L3
  axis for P-256 specifically.
- **No GLV-usable endomorphism on any curve in the class.** From `|D_0| > 1e5`,
  the minimal norm of a non-integer element of `End(E)` exceeds `25000` for
  **every** vertex. This bound is deliberately weak: it is what the exhaustive
  search proves without factoring `D`. A sharper bound needs `D` factored.

### Explicit neighbours

Computed as the Frobenius eigenspace on `E[ell]` (Elkies kernel polynomial
`h = gcd(psi_ell, x^p * psi_lambda^2 - phi_lambda)`), then Vélu for the codomain.

| `ell` | type | rational `ell`-isogenies |
| --- | --- | --- |
| 2 | inert (`t` odd ⇒ `D = 5 mod 8`) | 0 |
| 3 | ramified | 1 |
| 5 | ramified | 1 |
| 7, 19, 31 | inert | 0 |
| 11, 13, 17, 23, 29 | split | 2 each |

`j'` for `ell = 3`:
`60359795834994757875819835712620686501669024665003573244969414519504858434740`

`j'` for `ell = 5`:
`31171072990254877788373378282136735748432322289678398370500384426697561518746`

Full `(a', b', j')` for each neighbour is printed by the tool; they are not
transcribed here to keep this note from becoming the artifact of record.

Every neighbour passed three independent checks, and the tool aborts rather than
printing a number if any fails:

- kernel polynomial degree is exactly `(ell-1)/2`;
- `#E'(F_p) = n`, verified by `[n]P = O` on several points (`n` prime and in the
  Hasse interval makes this conclusive);
- `Phi_ell(j(E), j') = 0` for `ell in {2, 3}` against the hard-coded classical
  modular polynomial.

The `ell = 3` modular-polynomial check passing is the strongest single
validation of the pipeline, since it is fully independent of the eigenvalue
construction.

## 2. Positive control: secp256k1

A screen that reports "no structure" everywhere is worthless. secp256k1 is the
control, and it lights up correctly:

```bash
python3 tools/isogeny_class_screen.py --curve secp256k1 --ell 3,7
```

- `j(E) = 0`;
- `D_0 = -3` found exactly, with `f = 303414439467246543595250775667605759171`;
- `v_3(D) = 3`, so `ell = 3` **may** divide the conductor — volcano depth is
  possible here, unlike P-256;
- flagged: curves whose `End(E) = O_K` carry a norm-`~1` endomorphism. This is
  the classical GLV situation, and the L3 axis is **open** for this class.

P-384 screens like P-256: square part 1, no small `D_0`, `h ~ 2^193`, and `ell`
inert for every prime tested up to 13.

## 3. Transfer gap against the campaign's toy scale

`GOAL-ENDO-001` measurements to date run at `p <= 100057`. Census:

```bash
python3 tools/isogeny_class_screen.py --census 100057
```

| | `p = 100057` | P-256 |
| --- | --- | --- |
| classes with volcano depth (`f > 1`) | **62.8 %** (794/1264) | **0** at every `ell < 2e5` |
| classes with `\|D_0\| <= 100` | 3.2 % (40/1264) | 0 (checked to `1e5`) |
| mean class size `h ~ sqrt\|D\|` | ~496 curves, **enumerable** | `~2^129`, **not enumerable** |

At `p = 10007` the same census gives 53.0 % depth and 3.0 % small `D_0`.

The toy population over-represents precisely the structure a 256-bit class
lacks, and it is enumerable where the real one is not. This does not invalidate
any committed toy-scale measurement — every such record is already scoped to its
tested parameters under rule 4. It does mean a toy-scale result about volcano
level or special `j` carries a **transfer assumption that is currently
unstated**, and the numbers above suggest that assumption is false as stated for
these two axes.

This bears directly on open item **N8** of `DEC-20260807-41c173` (the cause of
the density-independent within-class over-dispersion, the campaign's
highest-priority open question). It suggests a cheap discriminating test:
stratify the existing ICINV toy classes by `(f > 1, |D_0|, t parity)` and re-run
the over-dispersion measurement restricted to the P-256-like stratum
(`f = 1`, large `|D_0|`, `t` odd). If the over-dispersion vanishes there, it is
structural rather than computational. That test is **not run here** and this
note asserts nothing about its outcome.

## 4. Scope and limitations

- **Screening only.** No attack, no speedup, no hardness claim. A curve passing
  this screen is not thereby "secure"; a curve failing it is not thereby broken.
  secp256k1's `D_0 = -3` is a published design feature, not a finding.
- `Phi_ell` cross-verification covers `ell in {2, 3}` only. Neighbours at
  `ell >= 5` rest on the eigenvalue construction plus the point-count check.
- "Conductor has no small prime factor" is verified below `2e5`. A conductor
  built entirely from larger primes is not excluded — it could not affect
  small-`ell` structure, but it is not ruled out either.
- `|D_0| > 1e5` is proven by exhaustive search; the resulting norm bound
  (`> 25000`) is weak by design. Sharpening it requires factoring a 258-bit `D`,
  which is not attempted.
- Point-search in the codomain check assumes `p = 3 mod 4`, which holds for
  every named curve in the tool.
- The census at `p in {10007, 100057}` is a full enumeration of ordinary classes
  at those two primes, not a sample, and not a claim about all toy primes.
