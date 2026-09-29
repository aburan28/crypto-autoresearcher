# EXP-MONO-805a02 — Implementation notes

Single-file harness: `experiments/EXP-MONO-805a02/implementation/run_experiment.py`.
Invoked as `python3 run_experiment.py <seed> <outdir>`; writes `<outdir>/raw-result.json`.

Reuses `harness/semaev.py`'s `s2`, `s3_expr`, `s4_expr` and `harness/toycurve.py`'s
`EllipticCurve` directly (imported, not reimplemented). Pure Python 3 stdlib +
sympy (1.14.0), matching the frozen contract's dependency constraint.

## Fixture curve and second curve

- **Fixture curve** (Stage 0, Stage 1, and one arm of every other stage):
  `p=211, A=37, B=57`. This is the EXACT curve KN-FIND-c41ea9's own m=4
  census used (`red_team_report.md` line 409, TASK-20260802-1b4130 objection
  O-9: "the run's own first random-panel curve (`A=37, B=57`)").
- **Second curve** (the contract's second required `p`): `p=1009, A=17, B=19`,
  a freshly chosen non-singular curve at that prime (not otherwise pinned by
  any prior record).

## Stage-by-stage notes

**Stage 0** is deliberately seed-free: it uses the first two on-curve points
in ascending-x order on the fixture curve, per the "known-answer edge"
convention of a fixed, reproducible instance.

**Stage 1** reproduces KN-FIND-c41ea9's construction (same curve, same `p`,
same `s4_expr` resultant, same triple count 193) but NOT its literal 193
triples, because the underlying git history under
`coordination/goals/GOAL-MONO-001/` records only the prose census result (the
count and the aggregate outcome), not a machine-readable listing of the 193
specific `(x1,x2,x3)` triples used. This is disclosed as a protocol deviation
in the execution report: "cell-for-cell" reproduction of the identical
construction on a freshly, deterministically seeded sample of 193 triples,
which is the closest reproduction achievable from what is actually committed.

**A degree-computation bug was found and fixed during development, before any
official run.** `sympy.Poly(expr, var).degree()` (no `modulus=` argument)
reports the degree of the polynomial's INTEGER (over-Z) representation. For a
small fraction of Stage-1/Stage-2/Stage-5 specializations, the top integer
coefficient(s) happen to be divisible by `p`, so the polynomial's TRUE degree
mod `p` is smaller than the over-Z degree — this is KN-FIND-c41ea9's own
"degree drop" phenomenon (documented for `m=3`: "`x1=x2` is a degree drop"),
generalised here to `m=4`/`m=5`: one signed combination of the summed points
lands on the point at infinity, which has no finite `x`-coordinate and is
correctly excluded from both the polynomial's affine degree and the
group-law-predicted root set. `poly_roots_bruteforce()` was fixed to strip
leading-zero coefficients mod `p` before computing the degree, so
"splits completely" (`len(roots) == deg`) is evaluated against the correct
mod-`p` degree. Before the fix, this produced 3 spurious Stage-1
"non-split" cells (190/193) despite the root SET matching the group-law
prediction in all 193/193 cases; after the fix, both split count and match
count read 193/193 in both official runs. The pre-fix number appears nowhere
in any official artifact.

**Two distinct metrics are reported at every polynomial-construction stage**
and must not be conflated:
- `n_split_completely` / `split_rate`: does the mod-`p` polynomial factor into
  DISTINCT linear factors matching its own mod-`p` degree exactly (i.e. no
  repeated root)? This can occasionally read slightly below 100% even when
  the theorem holds, because two DIFFERENT sign combinations can coincide in
  their affine `x`-coordinate by a genuine (rare, ~`1/p`) coincidence — a
  repeated root is still "split" over `F_p` in the classical sense (product
  of linear factors), just not with distinct roots.
- `n_root_set_matches_group_law` / `n_match`: does the SET of roots found
  equal the group-law-predicted set exactly? This is the actual content of
  KN-FIND-c41ea9's theorem and is the authoritative pass/fail criterion for
  Stage 1's hard gate. Both official runs read 193/193 on this metric.

**Stage 2** builds `S_5` by one further resultant elimination following
`s4_expr`'s own pattern, done NUMERICALLY (all of `x1,x2,x3,x4` substituted to
concrete on-curve `x`-coordinates before the resultant is taken), which keeps
each cell's resultant computation to a fraction of a second — nowhere near
the 300s per-cell timeout in the frozen contract.

**PROTOCOL DEVIATION, disclosed:** `stage2()`'s internal RNG is seeded from
`(p, "stage2")` only, NOT from the run's own `seed` argument. As a result,
Stage 2's 30-trial sample is IDENTICAL in content between RUN-MONO-805a02-1
(seed 20260830) and RUN-MONO-805a02-2 (seed 20260831) — only wall-clock
timing differs between the two runs' Stage-2 blocks. This was not caught
before both official runs completed; re-running would discard two otherwise
valid, budget-compliant runs (which run records are immutable and must not
be), so it is disclosed here and in `execution_report.yaml` rather than
silently corrected. Every other stage (0, 1, 3, 4, 5) IS seeded from the
run's own `seed` argument and its two replication instances draw genuinely
different samples (verified: Stage 1/3/4/5 raw-result.json content differs
between the two runs beyond timing fields; Stage 2's does not).

**Stage 3** instruments `EllipticCurve.add` directly via a counting wrapper
(`AddCounter`), with a factor base of 64 on-curve points and a fixed target,
for `m` in `{3,...,8}` at both `p`, 100,000 attempts per cell (the
contract's own floor). Convention: to sum `k = m-1` factor-base points,
`acc = chosen[0]` (0 calls) then `k-1 = m-2` calls to `.add` to fold in the
rest, then `+1` call for the residual subtraction `target - acc` (via
`.add(target, .negate(acc))`), for `m-1` total calls per attempt.
`.negate()` is a sign flip on `y` (no field inversion, no curve-arithmetic
formula) and is never counted. Every cell reconciled EXACTLY:
`measured_add_calls == (m-1) * attempts`, and no Semaev-polynomial evaluation
function is imported or called anywhere in `stage3()`'s hot loop (verifiable
by inspection: `stage3()` never references `s3_expr`/`s4_expr`/`sympy`).

**Stage 4**'s negative-locus control draws `x1, x2` uniformly in `F_p` (via
`rng.randrange(p)`, not constrained to on-curve `x`-coordinates), classifies
the resulting quadratic's discriminant by Euler's criterion (Legendre
symbol), and reports the fraction with both roots in `F_p` (QR or ramified
discriminant). A small number of trials (`x1 == x2`) collapse `S_3`'s degree
in `T` to below 2 and are skipped (`trials_used` is reported alongside the
nominal 10,000, and is always >99.5% of nominal).

**Stage 5** measures the "partial locus" EXACTLY as the frozen contract
specifies it: `m-2` of the `m-1` summation coordinates fixed to on-curve
`x`-coordinates, the target `T` ALSO fixed to an on-curve `x`-coordinate, and
exactly ONE summation coordinate left symbolic. Before measuring, the harness
checks and reports whether `S_4(x1,x2,x3,x4)` is symmetric under permuting
its four arguments (it is, by direct symbolic computation: swapping `x3<->x4`
and `x1<->x4` both leave `S_4` unchanged). **This symmetry is the reason
Stage 5's measured near-complete splitting is not a surprise requiring new
theory**: fixing `m-2` summation coordinates AND the target `T` on-curve
fixes `m-1` of `S_4`'s `m=4` TOTAL symmetric arguments to rational
`x`-coordinates — exactly KN-FIND-c41ea9's own theorem precondition, applied
to a relabelled argument. See `execution_report.yaml`'s Stage 5 section for
the full framing of why this is reported as the record's headline structural
observation rather than a footnote.

**Stage 6** is a static, read-only table built from a documented manual
search over `git ls-files` (tracked, committed state of this branch only —
explicitly excluding untracked worktree copies under
`.claude/worktrees/*` and `kb/.kb-corpus*`, which are not committed on this
branch) plus direct reading of the located files. No file outside
`experiments/EXP-MONO-805a02/` was written by this stage or by this
Executor at any point. The exact files read and the one-line justification
per label are embedded in `stage6()`'s return value (and hence in
`raw-result.json` for both runs) and repeated in `execution_report.yaml`.

## Files

- `implementation/run_experiment.py` — the only source file.
- `runs/RUN-MONO-805a02-{1,2}/` — the two required replication runs (seeds
  20260830, 20260831), each containing `manifest.yaml` (nested schema, per
  `experiments/EXP-MONO-a20e48/runs/*/manifest.yaml`), `command.txt`,
  `environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`.
