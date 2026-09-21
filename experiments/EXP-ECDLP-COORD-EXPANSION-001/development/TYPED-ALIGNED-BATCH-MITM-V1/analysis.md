# Typed Aligned Batch MITM V1 Result

## Status

`RESTRICTED THEOREM`, `OBSERVATION`, `TOY-EVIDENCE`, and scoped
`NEGATIVE RESULT`.

The diagonal key-compression identity is exact. The preregistered uniform
many-target coverage gate and one-instance relation gate both fail.

## Exact Run

- pinned source commit: `0a5bd4ab18b0380b3e41439a151f4889c915e8b9`;
- curves: prime orders `q=953,3919,15583`;
- coordinate `R` families: random-x, source-PRF-x, x-interval,
  rational-union;
- cohort exponents: `alpha=0.5,1,1.5,2`;
- family rows: 12;
- aligned/random cohort pairs: 48;
- all canonical `D2` pair witnesses retained;
- all reported point witnesses replayed exactly;
- wall time: 0.38 seconds;
- maximum RSS: 41,484,288 bytes.

The exact rerun verifier reproduced every cohort. Raw and rerun normalized
SHA-256 values both equal
`3c2807ac308c7c11518c12be8b232181a0e0942136dedcdbb9b52ab88e2473ef`.

## Exact Compression Theorem

For

`A_i=P0+iD` and `Q_t=Q0+tD`,

the witness equation depends on `t` and `i` only through `k=t-i`:

`r2+r3+r4 = (Q0-P0)+kD-r1`.

Therefore the aligned target map contains exactly

`(T+|A|-1)|R|`

records before point collisions, versus `T|A||R|` for matched unrelated
targets. Every one of the 48 cohorts meets this exact bound.

Observed aligned/random record ratios are:

| alpha | ratio range | deep-byte ratio range |
|---:|---:|---:|
| 0.5 | `0.318-0.444` | `0.314-0.459` |
| 1.0 | `0.182-0.314` | `0.191-0.347` |
| 1.5 | `0.119-0.214` | `0.126-0.236` |
| 2.0 | `0.100-0.180` | `0.116-0.217` |

This is a real storage and target-specialization reduction for aligned
cohorts.

## Coverage Result

Aggregate aligned coverage is comparable to the random-target control:

| alpha | aligned covered | random covered |
|---:|---:|---:|
| 0.5 | 15 | 15 |
| 1.0 | 36 | 36 |
| 1.5 | 111 | 108 |
| 2.0 | 341 | 304 |

However, coverage is strongly clustered by diagonal `k`. At `alpha=1`, four
of twelve aligned cells cover no targets. On the largest curve, several
families have no aligned hit through `alpha=1.5`, even when matched random
targets have ordinary support.

The preregistered many-target gate requires per-cell coverage, not an
aggregate average, and is therefore false.

An exploratory, non-promotable check at `alpha=1.25` and `1.4` shows the same
pattern: aggregate aligned/random coverage is `59/65` and `84/87`, but several
individual cohorts still have zero aligned coverage.

`OBSERVATION`: randomizing the common offset `Q0` may amplify aligned-cohort
coverage with a constant number of scans. This remains untested as a
deployment-relevant many-target algorithm, and naturally occurring public
keys are not generally aligned along one public `D`.

## Exact Rank Obstruction

All targets associated with one hit `(k,r1,r2,r3,r4)` give the same quotient
equation:

`p0' - k*d + sum_{j>0} c_j*rj' = log(Q0)`.

Thus covering many `t` values with one diagonal hit creates no new row. This
is a restricted theorem, not merely a toy observation.

The experiment measures the consequence:

- zero aligned cohort reaches full quotient rank at any schedule;
- even at `T=B^2`, aligned ranks are:
  - `1-3 / 6` at `q=953`;
  - `3-8 / 9` at `q=3919`;
  - `4-8 / 11` at `q=15583`;
- every matched random-target cohort reaches full rank at `T=B^2`.

At `T=B^2`, 341 aligned covered targets collapse to 62 distinct equations
across all cells. The relation gain is therefore much smaller than the target
coverage gain.

`NEGATIVE RESULT`: diagonal target compression does not produce a
one-instance relation collector in this exact architecture. Reaching
`Theta(B)` distinct diagonal equations requires roughly `T=Theta(B^2)`
targets under random-incidence heuristics, at which point target records and
workspace are `Theta(B^3)=q^(3/5)`, above rho.

## Cost Boundary

The useful symbolic batch identity remains:

- fixed `D2`: `Theta(B^2)`;
- aligned target records: `Theta(B(T+B))`;
- one `D2+R` scan: at most `Theta(B^3)`.

For genuinely aligned independent targets this can reduce amortized
decomposition work. It does not improve:

- a single target, which still pays the `B^3` scan;
- relation collection, because repeated target coverage repeats rows;
- arbitrary unrelated public keys, which do not share the diagonal collapse.

No ECDLP exponent improvement is claimed.

## Next Positive Questions

1. Test common-offset randomization for a genuinely aligned many-target
   application, with success amplification and communication charged.
2. Ask whether a two-dimensional target lattice can preserve key sharing
   while producing independent `D` coefficients; this must avoid restoring
   `B^3` target records.
3. Continue the single-target route through direct coordinate-ring prefix
   factors or an implicit resultant circuit, where row diversity is not
   identified with target-shift diversity.
