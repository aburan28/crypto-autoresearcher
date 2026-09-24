# Index calculus for the ECDLP over prime fields

`crypto_autoresearcher.index_calculus` is a self-contained implementation of
the Semaev point-decomposition route to index calculus on prime-order
elliptic curves `E(F_p)`, with Pollard rho on the same curves as the baseline.
It solves toy instances end to end, verifies every logarithm by scalar
multiplication, and counts the cost of every stage.

Nothing here threatens a deployed curve. The point is to measure, honestly,
how the classical prime-field index calculus scales.

## Layout

| module | what it does |
|---|---|
| `curve.py` | curves `y^2 = x^3 + ax + b` over `F_p`; deterministic prime-order curves with a certified order (BSGS in the Hasse interval), optionally restricted by a filter on `p` |
| `semaev.py` | the summation polynomial `S_3` and its roots |
| `factor_base.py` | factor bases: `small_x` (smallest x-coordinates), `subgroup` (x in a coset `g·mu_d` of `F_p^*`), `random` (control); their membership polynomials; the prime filter that makes the subgroup base fair |
| `decompose.py` | exhaustive decomposition of a point into `m` signed factor-base points (fix `m-2`, solve the last two with `S_3`) |
| `_accel.py` | optional numpy scan that locates the useful `S_3` roots; relations and every counter are identical to the pure-Python path |
| `msolve.py` | algebraic decomposition: the Semaev system solved by the msolve Gröbner-basis engine |
| `linalg.py` | incremental sparse elimination mod `N`, stopping at the first relation that fixes the target log |
| `rho.py` | Pollard rho with distinguished points and a Teske 20-adding walk |
| `solver.py` | the end-to-end solver and its cost columns |
| `stats.py` | exponent fits with a stratified bootstrap confidence interval |

## Running it

```sh
pip install -e ".[index-calculus]"      # numpy for the fast path (optional)
apt install msolve                       # only for the msolve engine (optional)

# one instance, index calculus and rho, JSON out
python -m crypto_autoresearcher.index_calculus solve --bits 20 --m 3 --fb small_x --rho

# index calculus vs rho over field sizes, 4 processes, rows appended to a JSONL file
python -m crypto_autoresearcher.index_calculus sweep --bits 12 14 16 18 20 \
    --m 2 3 --fb small_x random subgroup --curves 5 --rho-curves 10 \
    --workers 4 --out sweep.jsonl

# per-target cost: msolve vs exhaustive enumeration on a ladder of |F|
python -m crypto_autoresearcher.index_calculus engines --bits 16 --m 2 3 \
    --targets 12 --workers 3 --out engines.jsonl

# refit and tabulate saved rows
python -m crypto_autoresearcher.index_calculus analyze sweep.jsonl engines.jsonl
```

Everything is deterministic in the seeds, so operation counts reproduce
exactly on any machine. Wall times do not reproduce.

## How cost is counted

Costs are counts in separate columns, and columns are never summed.

- **Index calculus.** The primary unit is one `S_3` root solve, i.e. one
  candidate factor-base element tried against a target (one modular square
  root). The other columns are membership tests, group operations, and
  modular multiply-adds in the linear algebra. Group operations are split
  into target generation (`aP + bQ`) and decomposition.
- **Rho.** The primary unit is one group addition of the walk (`walk_ops`).
  The fixed scalar multiplications for the step table and the walk starts
  are reported separately as `setup_ops`. At toy sizes that setup term rivals
  the walk, and mixing the two flattens a fitted slope toward 0.3.
- **Exponents.** An exponent is the least-squares slope of `log2(cost)`
  against `log2(N)`. The 95% interval comes from a bootstrap that resamples
  instances within each size.
- **Factor-base size.** `|F|` defaults to `((m! N)/2)^(1/m) / 2`, which gives
  about one decomposition per two attempts.
- **Fair subgroup comparison.** When the subgroup base is in a sweep, `p` is
  drawn so that `p - 1` has a divisor `d` within 15% of `2|F|` for every arity
  in the sweep. Every base in a cell then uses the subgroup base's actual
  size.

## Results

The 12–32-bit sweep and the msolve comparison are running; their numbers
land here when they finish.
