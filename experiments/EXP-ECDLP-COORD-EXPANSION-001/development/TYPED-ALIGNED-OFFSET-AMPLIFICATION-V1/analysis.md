# Typed Aligned Offset Amplification V1 Result

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`, and a scoped
`NEGATIVE RESULT` for the one-instance route. The exact aligned key identity
survives multiple common offsets, and offset randomization sometimes restores
coverage relative to unrelated controls. It does not produce a generic
ECDLP improvement.

## Exact Run

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves: `q=953,3919,15583`;
- coordinate families: `random_x`, `source_prf_x`, `x_interval`,
  `rational_union`;
- family rows: 12;
- target exponents: `1, 1.5, 2`;
- offset counts: `K in {1,2,4,8}`;
- cells: 144;
- all witness replay and equation checks: valid;
- producer wall time: 5.4601 seconds;
- producer peak RSS: 84,099,072 bytes;
- normalized deterministic replay: exact, independently receipt-checked.

The raw-result input hash is
`c7476f8aeff640ea2690c70218252186a8c657bf1d6db76baa01c55e2289fa3c`.

## Coverage

The aligned construction preserves the exact record identity for every
offset: each offset has `(T+|A|-1)|R|` target-key records before point
collisions. Across the 144 cells, 108 meet the provisional coverage gate of
at least 80% of the matched unrelated-target control.

By offset count, the gate counts are:

| `K` | passing cells | total cells | median aligned/control coverage | median charged work ratio |
|---:|---:|---:|---:|---:|
| 1 | 24 | 36 | 1.264 | 0.304 |
| 2 | 29 | 36 | 1.000 | 0.321 |
| 4 | 27 | 36 | 1.025 | 0.330 |
| 8 | 28 | 36 | 1.000 | 0.335 |

The coverage effect is not monotone in `K`: individual offsets can be
unlucky, and adding offsets can lower the aggregate fraction on a particular
family. The result therefore supports a bounded coverage-amplification
observation, not a uniform target decomposition theorem.

## Cost and Memory

Each extra offset adds a target schedule, aligned key table, and complete
`D2+R` scan. The fixed `D2` table is shared, but transient key advice is
charged separately. Median charged fixed-plus-core online work per target was
`27.54, 26.77, 26.38, 26.18` group-operation proxies for `K=1,2,4,8`,
respectively; the small decrease is amortization from the fixed table, not a
sublinear scan. Median peak retained advice was approximately `103 KiB` in
all four `K` cohorts, while cumulative transient key bytes grow with `K`.

The unrelated control materializes all `K*T` target records. Its much larger
charged work is a valid control for target specialization, but it does not
make the aligned route a single-target attack. Communication, public-target
enumeration, memory bandwidth, and witness replay are not hidden inside the
coverage fraction.

## Rank Boundary

No offset in any cell reached full quotient rank. This is expected from the
prior diagonal identity: a hit indexed by `k=t-i` gives a row tied to its
offset's unknown `log(Q0)`, and covering more `t` values does not create new
rows. Independent offsets introduce independent target-offset variables; they
cannot be pooled into one relation system without another exact relation
between the offsets.

`NEGATIVE RESULT`: common-offset randomization does not repair the one-instance
relation bottleneck in this architecture. It remains a possible fixed-curve
many-target decomposition primitive only when the target cohort is genuinely
aligned and the extra scans are useful.

## Boundary and Next Action

This is a toy, model-bound, public-test-cohort result. It does not apply to
arbitrary unrelated public keys, does not beat Pollard rho for a single target,
and does not establish an ECDLP exponent improvement.

The next positive question is a two-dimensional public target lattice that
could preserve shared complement keys while producing independent coefficients.
It must be tested with full target-record, query, rank, and memory accounting;
if its second direction restores `B^3` target materialization, it should be
classified as another scoped negative.
