# Ancillary files

Verification code and data for section 8 of the paper.

- `semaev_cover.py` — arithmetic of the Semaev summation cover, written from
  scratch: `F_{p^2}`, elliptic-curve group law, summation polynomials via the
  resultant recursion (Sylvester determinant recovered by interpolation),
  distinct-degree factorization over `F_p`, and exact multivariate polynomials
  over `Z` for the `m = 3` discriminant identity. **Depends on nothing outside
  the Python standard library** — no Sage, no SymPy.
- `verify.py` — the falsification battery. Every check is written so that it can
  fail; the file computes and does not interpret.
- `raw-result.json` — its output.

```sh
python3 verify.py --out raw-result.json      # ~70 seconds
python3 verify.py --quick --out quick.json   # ~15 seconds, smaller battery
```

Deterministic at seed 20260807. The output is byte-reproducible: nothing
environment-dependent is written into it (timing, interpreter version and
platform are printed to stderr instead). The shipped file has

```
sha256  a7f3cb1265cf110291e8169bcea184374c807372fb7ca3ad841f29eed4b57974
```

## What each key of `raw-result.json` holds

| key | check |
|---|---|
| `C1_discriminant_identity` | `disc_T S_3 = 16 f(x1) f(x2)` in `Z[x1,x2,A,B]`, exact integers |
| `C2_C4_generic_fibre` | root identification, factorization law, Frobenius classes, discriminant square class, at `m = 3,4,5` |
| `C5_factor_base_locus` | complete splitting when every coordinate is a rational point's `x` |
| `C6_exhaustive` | all `p^{m-1}` specializations in 5 cells, with the exact per-class count |
| `C7_null_controls` | the same instrument on two degree-4 families that are not summation polynomials |

`C7` is the one to look at first if you doubt the rest: a law obeyed by 100% of
241 643 genuine specializations is only meaningful because the matched controls
obey it 13.7% and 48.9% of the time.
