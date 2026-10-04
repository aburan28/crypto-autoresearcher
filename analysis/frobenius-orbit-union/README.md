# Shift-encoded Frobenius orbit-union point decomposition, `m = 2`

Instruments and raw results behind `EV-FROB-b6e1e9` and `KN-FIND-47da4e`.

**These are not harness runs.** They were produced by the scripts in this
directory inside one interactive session, not by `harness/runner.py`, so no
`RUN-*` manifest exists for them and none is invented (AGENTS.md rule 5). The
scripts and their outputs are committed here so the finding binds to content
rather than to a container that no longer exists.

## The question

`RQ-FROB-7d8dd4` asks whether Frobenius structure reaches the *expensive* stage
of subfield-curve index calculus — point decomposition — rather than only the
factor-base and linear-algebra constants that Galbraith–Granger–Merz–Petit
already claim (`KN-LIT-796`).

At `n = 131` no Frobenius-stable `F_2`-*subspace* of index-calculus dimension
exists: `ord_131(2) = 130`, so the stable subspaces are exactly the four of
dimension `0, 1, 130, 131` (`IDEA-20260918-9abf42`). Frobenius-stable *sets*
are still free, because every `x` outside `F_2` has an orbit of size exactly
`131`, so a union of orbits is stable at any size. The open question is whether
such a union can be given a cheap algebraic description that the decomposition
solver can exploit — the `REP+INDEX` arm of `EXP-FROB-ORBIT-1` in
`research/ideas/frobenius_orbit_experiment_matrix.md`, which had never been run.

## What is measured

Fix a random `F_2`-subspace `V'` of dimension `l'` and let
`S = ∪_j σ^j(V')` be its orbit union. For a target abscissa `x_R`, the
`m = 2` decomposition question over `S` is asked three ways:

- **baseline** — `n` separate Semaev systems, `x_1 ∈ V'`, `x_2 ∈ σ^j(V')`,
  `j = 0 … n-1`. The global Frobenius gauge fixes the first summand, so these
  `n` systems cover the target's whole Frobenius orbit, and one relation for any
  conjugate is as good as one for `x_R` (its logarithm differs by a known
  `λ^{-i}`). This is the `n^{m-1}` system count the encoding must beat.
- **one-hot** — a single system with `n` shift bits, `x_2 = Σ_j s_j σ^j(u)`,
  exactly one `s_j` true.
- **binary** — a single system with `⌈log₂ n⌉ shift bits, `σ^j` expanded as a
  product of selectors. Degree 7 at `n = 19`.

`l'` is chosen so that `|S| ≈ 2^{n/2}`, which is the balanced factor-base size
for `m = 2`.

Ground truth per target is an exhaustive solve of the quadratic
`S_3(x_1, x_2, x_R) = 0` over every `x_1 ∈ V'`, independent of any solver.
Every model returned is re-checked against `S_3` and against membership in `V'`
and `S` before it counts.

## Reproducing

```sh
# CaDiCaL arm (conflicts, decisions, propagations, seconds)
python3 frob_union_m2.py --n 19 --targets 16 --seed 7 --no-linear --out union_n19.json

# WDSat arm: export the same instances as ANF, then build and solve
python3 emit_anf.py  --n 19 --targets 16 --seed 7 --out anf19
python3 run_wdsat.py --anf anf19 --source <WDSat checkout> --work build --out wdsat19.json --skip binary
```

`emit_anf.py` reproduces `frob_union_m2.py`'s random stream exactly, so both
arms see the same subspace, the same generator and the same targets; the
exported manifest carries each target's abscissa and verdict for cross-checking.
The ANF row format follows
`crypto/src/cryptanalysis/wdsat_oracle.rs::format_anf`. `run_wdsat.py` sizes
`config.h` from the instances and grows the static capacity until the instance
loads, because WDSat allocates statically and aborts on an assertion when
`__MAX_ID__` is short.

WDSat source: `github.com/aburan28/WDSat`, commit
`55d55b2620d768d9f7c78dcd8990a0689533c1d0` — the same commit
`.github/workflows/koblitz-stage32-wdsat-capacity.yml` in the sibling
`crypto` repository pins. Solver modes: default (`cnf` + `xorset`
propagation) and `-x` (`XORGAUSS`, the XG-ext search). `-g` supplies a
branching-priority prefix.

## Results

`union_n{13,17,19,23}.json` — CaDiCaL 1.5.3 via `python-sat`.
`wdsat{19,23}.json` — WDSat, both modes, default and shift-first branching.

Headline, on refuted targets, one-hot against the summed baseline:

| n | CaDiCaL conflicts | WDSat plain | WDSat XG |
|---|---|---|---|
| 13 | 1.017 | — | — |
| 17 | 1.017 | — | — |
| 19 | 1.467 | 1.017 | 1.212 |
| 23 | 1.150 | 1.000 | 1.033 |

## Known limits of these instruments

- `m = 2` only. The chained system at `m ≥ 3` is not built here.
- The binary arm is **not measurable on WDSat**: on `binary/t014.anf` at
  `n = 19` the default search returns a model that violates 11 of the
  instance's 32 rows, and the two search modes disagree on satisfiability.
  Degree 7 is outside the degree 3–4 envelope every shipped `config.h`
  profile targets. The arm is excluded rather than reported.
- Wall time is not comparable between arms: the baseline pays `n` process
  launches against the one-hot arm's one. Conflicts is the unit.
- `frob_union_m2.py` is pure Python field arithmetic and does not scale past
  roughly `n = 23` at these subspace sizes.
