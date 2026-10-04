# IMPLEMENTATION.md — EXP-ECDLP-56117b

Independent G3 implementation for TASK-20260907-b407d8 / EXP-ECDLP-56117b.
Authored from the frozen formal statement in
`experiments/EXP-ECDLP-56117b/specification.yaml` (`g3_predicate`), which
copies `experiments/EXP-ECDLP-612fb1/amendments/v2_to_v3.yaml` Section 3.
This file discloses the three choices the predicate text leaves open, and
attests independence.

## Independence attestation

The author of this implementation did **not** read, import, copy, or
`sys.path`-insert any of:

- `experiments/EXP-ECDLP-612fb1/source_v2/`
- `experiments/EXP-ECDLP-612fb1/source_v3/`
- `experiments/EXP-ECDLP-6ac801/source/`
- any existing `instrument.py` in this lineage

`sys.path` is inserted only for `experiments/EXP-ECDLP-56117b/source/`
(this directory). Reading P2 is a uniformly random function on `Z_N` plus
an independent Bernoulli(theta) DP marking. mix64 / hash64 was not
reproduced.

## Files

Exactly the five named implementation files:

- `__init__.py`
- `g3_predicate.py` — instance, pool, weight selection, exact basins, scoring
- `run_cell.py` — one measurement run → nine artifacts
- `analyze.py` — analysis run → eight base files plus `g3_verdict_table.json`
- `IMPLEMENTATION.md` — this file

No sixth Python module. A C resolver is compiled at runtime from a string
embedded in `g3_predicate.py` into `/tmp/g3_56117b_basins_<digest>.so`
(scratch, not an artifact). If `gcc` fails, a numpy layer-pull fallback
runs.

## The three unspecified PRNGs

`g3_predicate.what_this_section_does_not_specify` names three open choices.
All use `numpy.random.Generator(numpy.random.PCG64(SeedSequence(...)))`.
`EXPERIMENT_SALT = 0x56117B`.

| stream | SeedSequence entropy | draws |
| --- | --- | --- |
| (iii) map `f` | `[SALT, 1, s]` | `f[x] ~ Unif{0,...,N-1}` independently, `dtype=uint32` |
| (iii) DP marking `D` | `[SALT, 2, s]` | `D[x] = 1` iff `U[x] < theta`, independent of `f` |
| (i) pool starts | `[SALT, 3, s]` | uniform starts in `Z_N`, consumed sequentially; prefetch batch 65536 (order-preserving) |
| (ii) tie-break | `[SALT, 400 + s]` | one `uint64` key per pool DP; **ascending** on ties of `w(d)` |
| NULL_A | `[SALT, 300 + s]` | a uniform permutation of the pool's own `(S_d, h_d)` multiset; tie-break keys stay with DP identity |

These are disclosed, not copied from any prior instrument.

## Selection vs scoring

Order of operations in `run_cell()`:

1. Generate `(f, D)`.
2. Build the precomputation pool (starts → first DP or cap) until exactly
   `r * T` distinct DPs. Charge every walk to `P`. A miss is charged `cap`
   and contributes nothing. A hit of length `L` credits `(S_d += L, h_d += 1)`;
   `L = 0` if the start is itself a DP.
3. **Select** `STATIC(T)_r` by `w(d) = S_d + 4 * W * h_d`, taking the `T`
   largest `w`; ties broken by the declared key ascending.
   `select_static_by_weight` accepts only `(dps, S, h, W, T, tie_keys)`.
   It has no basin argument. At this point the basin array has not been
   allocated.
4. If the cell is `a16r2`, relabel `(S, h)` (NULL_A) and select again with
   the same `w` and the same tie-break keys.
5. **Then** compute exact basins and **score** the already-chosen tables.

Selecting by true basin size is a named invalidation and is not implemented.

Frozen table (not recomputed): `N = 16777216`, `T = 256`, `T_sel = 128`.

| a | W | theta | cap |
| --- | --- | --- | --- |
| 1/16 | 64.000000 | 0.015625000 | 512 |
| 1/8 | 90.509668 | 0.011048544 | 725 |
| 1/4 | 128.000000 | 0.007812500 | 1024 |

## Basins

`dist(x)` = least `m >= 0` with `D(f^m(x)) = 1`; `first_dp(x)` is that
iterate. DP-free cycles are UNREACHABLE. `dist(x) > cap` is CAPPED.
`basin(d) = #{ x : first_dp(x) = d AND dist(x) <= cap }`. Every DP is in
its own basin (`dist(d) = 0`). Exact, not sampled.

`TopShare(t)` = (sum of the `t` largest `basin(d)` over all DPs) / `N`.
`StaticCov(T, r)` = (sum of `basin(d)` over the `T` selected pool entries) / `N`.
`margin = TopShare(T_sel) - StaticCov(T, r)`.
`g3_s = [margin >= 0]`.

Exact-coverage non-exceedance: `StaticCov` count never exceeds `TopShare(T)`
count (integer comparison). An exceedance marks the run `completed_invalid`.

## BCa

`analyze.py` implements BCa 95% on the **seed** as the resampling unit,
10 000 resamples, generator seed 20260907, stated as fields on every CI.
The inverse-normal uses Acklam's rational approximation (no scipy).

## a = 1/8 (20 seeds)

Reported as a margin **distribution**. No binary 4/5 threshold is applied
as a cell verdict. `pass_count/20` is the count of non-negative margins, a
descriptive statistic. Strictly-positive / negative / zero counts are also
written. A C(20,5) subset fraction may appear as a non-criterion descriptive
statistic only.

## Determinism

`RUN-ECDLP-56117b-a16r2-s1` is executed with `--determinism-repeat`: the
cell is computed twice in one process and the scored quantities are compared.
The check is stored in that run's `raw-result.json` under `determinism_check`
and copied into `g3_verdict_table.json`. No second run directory is written.

## Resources

Machine protection: 3600 s wall and 8 GiB peak RSS per run. Excess is
`failed_infrastructure` / `resource_exhaustion`, never a mathematical
negative. Serial, `maximum_workers: 1`.

## Certificate

`certificate.kind: none`. This is a pure measurement of coverages.

## Inference record

Requested policy: `executor-implementation`. This session is served by
Cursor Grok 4.6. Adapter resolve for that policy is `anthropic:claude-sonnet-5`.
Handoff `fallback_allowed: false`. The identifier substitution is recorded
in every manifest (`fallback_used: true` with reason) and as a protocol
deviation; it is not silent. Numeric results are deterministic code.
