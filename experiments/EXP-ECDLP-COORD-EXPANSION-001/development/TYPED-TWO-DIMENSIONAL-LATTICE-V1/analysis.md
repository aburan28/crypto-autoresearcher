# Typed Two-Dimensional Target Lattice V1 Result

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, and a scoped
`NEGATIVE RESULT`. The second public target direction creates distinct
coefficient slots and improves rank, but the tested lattice never reaches full
quotient rank and its target-side state grows linearly in the second dimension.

## Exact Run

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves: `q=953,3919,15583`;
- coordinate families: `random_x`, `source_prf_x`, `x_interval`,
  `rational_union`;
- family rows: 12;
- `U=ceil(B^alpha)` with `alpha in {1,1.5}`;
- `V in {1,2,4,8,16}`;
- cells: 120;
- all witness replay and equation checks: valid;
- producer wall time: 3.3746 seconds;
- producer peak RSS: 73,662,464 bytes;
- normalized deterministic replay: exact and receipt-valid.

The key identity is exact. For `k=u-i`,

`r2+r3+r4 = (Q0-P0)+kD+vE-r1`.

Thus the key table contains `(U+|A|-1)V|R|` records before point
collisions, rather than `UV|A||R|` records for unrelated targets.

## Rank and Coverage

No cell reaches full quotient rank. The quotient width is `|R|+2`, with the
additional column representing the second public direction. Median diagnostics
by `V` are:

| `V` | median rank deficit | median coverage ratio vs unrelated control | median key records | median peak retained advice |
|---:|---:|---:|---:|---:|
| 1 | 8.0 | 0.557 | 152 | 78,527 bytes |
| 2 | 6.0 | 1.417 | 304 | 129,835 bytes |
| 4 | 4.0 | 0.980 | 608 | 269,261 bytes |
| 8 | 1.5 | 1.108 | 1,216 | 490,945 bytes |
| 16 | 1.0 | 1.012 | 2,432 | 920,993 bytes |

The rank trend is a real finite-size signal: more `v` slices supply more
distinct coefficient rows. It is not yet a usable relation compiler. Even at
`V=16`, the full-rank count is `0/24` for that slice size, and coverage gains
come with linear target-table growth.

## Cost Boundary

The diagonal compression remains useful: for fixed `U`, the key record ratio
against unrelated targets is the expected `(U+|A|-1)/(U|A|)` factor. However,
the second direction multiplies the aligned table, target schedule, and scan
state by `V`. The candidate therefore trades the original row collapse for a
larger target lattice rather than eliminating the central cost.

The experiment does not charge a breakthrough based on the favorable coverage
ratio. It reports target construction, key construction, query work, retained
advice, and the exact rank gate separately. A near-full rank at a larger `V`
would still need a full end-to-end comparison against rho and target descent.

## Scoped Negative and Next Question

`NEGATIVE RESULT`: on these three toy curves and four coordinate families, the
two-dimensional lattice does not produce full quotient rank before the tested
linear-in-`V` target specialization becomes the dominant state. This rules out
promotion of this exact lattice organization, not all multi-direction
representations.

The next positive question is whether a nonlinear or quotient representation
can reuse the `v` slices without materializing one key block per slice. Any
successor must reconstruct the missing row independently and charge the
transposed/indexed state, not just report the observed rank trend.
