# Development V3 Analysis

## Status

`NEGATIVE RESULT`, `TOY-EVIDENCE`, `MODEL-BOUND`,
`NOVELTY-UNVERIFIED`.

No frozen coordinate family crossed the Stage-A joint geometry gate on the
10, 12, and 14-bit development schedule. This narrows only the tested
factor-base constructors, sign policies, occupancy target, curve seed, and
`p mod 4 = 3` generator.

It is not a coordinate-factor-base barrier, an index-calculus negative
result, or an ECDLP exponent result.

## Integrity

- source commit: `fefe32f5e1fda87823c5ec1824ceb858bb616d9c`
- source SHA-256:
  `5af1bfcc3e777aa366b137ef34a893d7e0304aa0edc32a2b5684e5d206e5c45b`
- raw-result SHA-256:
  `48191b81e8a44a508f10a691c6dae7591d6a1262c58df5d16a587e2e1dbe26e2`
- exact configurations: 582
- wall time: 41.88 seconds
- maximum resident set: 125,435,904 bytes
- V2/V3 arithmetic projection: byte-value equal after removing timing and
  summary-only fields

Every candidate was built and hashed before target generation and before the
subgroup-log census. The online API received target points, factor-base
points, and point-keyed `D2`/`D3` advice only. Independent point replay
through depth five matched scalar support, `D2+D3` matched `D5`, runtime
assertions checked every transient returned witness, the one retained witness
per configuration was independently rechecked, and every factor-base digest
was unchanged after audit.

## Curves

| bits | p | q | trace | j | B canonical | B complete |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 971 | 953 | 19 | 832 | 8 | 10 |
| 12 | 3947 | 3919 | 29 | 2377 | 10 | 12 |
| 14 | 15667 | 15583 | 85 | 3394 | 14 | 16 |

All group orders are prime with cofactor one. The field primes were selected
without consulting the disclosed `p-1` factorizations. The schedule remains
restricted to `p mod 4 = 3`.

## Joint geometry

The table reports ranges over the three curves. Coverage is the minimum ratio
against the random-x and source-PRF-x medians. Compression and `Phi` use the
maximum ratio against those two nulls.

| family | sign policy | D2 ratio | D3 ratio | D5_new retention | Phi ratio | passes |
|---|---|---:|---:|---:|---:|---:|
| x interval | canonical | 0.990-1.000 | 0.980-1.017 | 0.973-1.047 | 0.853-1.048 | 0/3 |
| x interval | complete | 1.000-1.000 | 0.988-1.014 | 0.620-1.090 | 0.827-3.287 | 0/3 |
| square map | canonical | 1.000-1.000 | 0.974-1.005 | 0.953-1.039 | 0.949-1.244 | 0/3 |
| square map | complete | 1.000-1.000 | 1.014-1.027 | 0.998-1.044 | 0.914-1.011 | 0/3 |
| rational union | canonical | 1.000-1.000 | 1.000-1.017 | 0.958-1.047 | 0.863-1.110 | 0/3 |
| rational union | complete | 1.000-1.000 | 0.946-1.071 | 0.599-1.261 | 0.340-2.388 | 0/3 |
| scalar progression control | canonical | 0.467-0.694 | 0.143-0.362 | 0.008-0.063 | 3.756-5.665 | ineligible |
| scalar progression control | complete | 0.256-0.412 | 0.071-0.185 | 0.005-0.037 | 1.854-4.264 | ineligible |

The decisive failed condition is `D2 <= 0.8x`: every coordinate candidate is
between `0.990x` and `1.000x` of the worse matched coordinate null. `D3` is
also null-like. The progression control proves the profiler can detect strong
intermediate compression, while its collapse in `D5_new` shows why support
retention must remain in the joint gate.

Some rows have favorable `Phi`, including complete rational union at 10 bits.
They do not pass because support-mass compression is absent, the effect varies
or reverses across sizes, and scan-order spread can be material. These are
diagnostics, not candidate algorithms.

The preserved raw field named `empirical_joint_dominance_p` is a pooled
partial-order dominance score, not a calibrated p-value. Its minimum
`1/63 = 0.0159` may occur when all null rows are merely incomparable with the
candidate. It supplies no significance claim. The result instead follows
directly from the preregistered effect-size miss: candidate `D2` ratios are
`0.990-1.000`, not at most `0.8`.

## Baselines and limits

The measured rho median group-operation counts were 159, 456, and 444.5.
Their three-point fitted slope is dominated by toy variance and has no
asymptotic interpretation.

Audit structures and point-build costs are partially instrumented. Canonical
scalar enumeration time, split-census wall time, and temporary peak
allocations are not separately charged.

Stage A does not implement a packed recursive point DAG, genuine batch
inversion, relation collection, matrix rank, filtering, linear algebra, or
individual target descent. Since no family compressed `D2`, those successors
are not justified for these frozen constructors.

## Strongest valid conclusion

No useful intermediate point-support compression was found for x intervals,
square-map images, or the frozen square/Mobius union under this development
schedule. The experiment supplies a concrete falsifier for these
representations, not a no-go theorem for coordinate-specific index calculus.

## Next positive search direction

Search outside one-dimensional accepted-x enumerators. The next candidate
should have a structural reason for a small `D2`, such as a factor base drawn
from a low-complexity correspondence whose pair sums land in a separately
indexable image, while a transverse third-stage map restores five-term
coverage.

## Next negative/proof direction

Exhaustively enumerate small cyclic-group factor bases and construct the exact
Pareto frontier `(d2,d3,d5_new,T_perm,Phi)`. Compare unrestricted sets with
coordinate-generated sets. This can determine whether the joint thresholds
are combinatorially feasible at the selected occupancy before spending effort
on a richer coordinate compiler.
