# EXP-FB3-001 implementation note

Executor record for TASK-20260724-228. Frozen contract:
`experiments/EXP-FB3-001/specification.yaml` (version 1, approved, DEC-20260717-002).
Frozen operational definitions: `experiments/EXP-FB3-001/amendment-001.yaml`
(EXP-FB3-001-AMD-001, approved). Neither file was modified.

## Files

| file | role |
|---|---|
| `fb3_core.py` | curve generation and verification, dlog tables, the six geometries, three independent exact counters, statistics (empirical p-values, Holm, bootstrap, growth slope) |
| `run_battery.py` | one size run (2^14 / 2^16 / 2^18): all pre-registered cells, shared null, typed nulls, exploratory arms |
| `run_controls.py` | controls run: brute-force counter verification, conservation/closed-form controls, auxiliary-machinery controls, H016/H017 port fidelity |
| `run_family.py` | family run: Holm across the 8-cell family per size, bootstrap CIs, growth slopes, prior-cell accounting, analytic-arm consequence checks |
| `make_run.py` | run wrapper: creates the immutable run directory, captures the real stdout/stderr streams, records git commit + dirty tree, writes `manifest.yaml` |

Environment: Python 3.12.3, numpy 2.4.4, sympy 1.14.0, pure Python + numpy
(no SageMath, Singular, or PARI in this environment). 4 CPUs, single process.

## Counting convention (inherited, not invented)

A factor base is a set `D` of `B` distinct nonzero group elements identified with
their discrete logs; a decomposition of target `r` is a **multiset**
`{i <= j <= k}` of base elements with `d_i + d_j + d_k = r`; `m = 3`; no signs;
targets range over the whole group. This is the H016 convention recorded
verbatim in `inputs/h100_session/h016_base_yield.json` and is used so the new
cells are comparable with the two prior cells.

**Discrete logs are known by construction FOR MEASUREMENT ONLY.** They are used
to count decompositions. No cost, speedup, or attack claim is derived from their
availability, and nothing in this experiment is a step of an attack.

## Exact counting: three independent implementations

1. `counts_untyped_m3` (primary) — Burnside orbit count over `S_3` acting on
   ordered triples, `c = (T + 3U + 2V)/6` with `T` the ordered-triple sum
   histogram, `U` the `2d_i + d_j` histogram, `V` the `3d_i` histogram. All
   integer arithmetic (`numpy.bincount`), no floating point, so there is no
   rounding step to audit. 12 ms per base at `N ~ 2^18`.
2. `counts_untyped_m3_direct` — direct enumeration of the multisets
   `i <= j <= k`. Independent code path.
3. `counts_untyped_m3_fft` — the cyclic-convolution route named in the
   amendment: `c = (irfft(F(A)^3 + 3 F(A) F(A2)) + 2 A3)/6`, with the rounding
   deviation `max |value - round(value)|` measured on every call.

Typed counters: `counts_typed_111` (one element from each of three sub-bases)
and `counts_typed_1_2` (one element from one sub-base, a 2-multiset from
another). Brute-force references: `brute_force_counts`,
`brute_force_typed_111`, `brute_force_typed_1_2`.

Agreement is checked on the **full per-target count vector over all N targets**,
not only on the total (RUN-FB3-001-CTRL block A: 46 cases, 148 assertions, all
true). Every cell in every run is additionally checked against its closed-form
total (67 784 checks across the three size runs, all pass), and 43 cells per
size run are recounted by both independent routes.

The prime-length FFT was measured at 25 ms per transform at `N ~ 2^18` versus
12 ms for the whole integer count, so the integer counter is the primary route
and the FFT is retained as an audit route only. Its worst rounding deviation
over the whole campaign was 5.5e-12, i.e. 4.6e10 times below the 0.25 margin
that would threaten integer recovery.

## Operational pinnings (fixed before execution, recorded in `FROZEN`)

The frozen contract specifies these in prose; the executor pinned them before
any measurement and did not adjust them afterwards. They are recorded in
`frozen_constants` inside every size run's `raw-result.json`.

| quantity | pinning |
|---|---|
| size window | `p` drawn within +-0.5% of `N_target`; accepted `N` within +-2% of `N_target` |
| curve seed | `20260724*1000 + bits*10 + curve_index` |
| cell seed | `70160724 + bits*100000 + curve_index*1000 + replicate_seed` |
| null draws | 200 per (curve, N, seed) per typing pattern (frozen minimum is 100; see deviation D1) |
| concentration statistic | `sum_r c(r)(c(r)-1) / n_targets` |
| p-value convention | `(r+1)/(n+1)`; the recorded H016 convention `2*min(tail)/n` is reported alongside |
| bootstrap | 2000 resamples, seed 4242 + bits; percentile CIs at 95% and 99.375% (= 1 - 0.05/8, the family-wise level) |
| height schedule | enumerate coprime `(u,v)` with `max(\|u\|,v) <= H` for `H = 16, 32, ...` until `B` point-x are available |
| coset ordering | ascending `x` within each coset, cosets in order `i = 0, 1, 2, ...` |
| greedy split | seeded permutation of `[0,N)`; first `floor(N/2)` indices are TRAINING |
| mixed sub-bases | `ceil(B/2)` x-interval, `floor(B/2)` small multiples |
| mixed primary typing | two from sub-base 1, one from sub-base 2 — pre-declared by the size-only rule "the typing with the larger closed-form total when `B1 >= B2`"; both typings are measured and reported |
| asym ladder | weights `(1,1,1), (2,1,1), (4,1,1), (8,1,1)`; `B2 = floor(w2/W * B)`, `B3 = floor(w3/W * B)`, `B1` takes the remainder |
| asym primary split | `(8,1,1)`, the most unbalanced rung, pre-declared |
| asym element choice | disjoint uniform random logs from the cell seed — the frozen definition pins only the SIZES, so the elements are left unstructured to isolate the sizing effect H004 claims |
| typed-cell family control | untyped matched-random base of the same **total** size `B` (the frozen control "matched random base, same size"); the same-typing matched-random control is also reported for every typed cell |

Two of these deserve emphasis because they shape how a typed cell reads:

* The **typed-cell family control** is the untyped base of the same total size.
  That is the comparison consequence (iv) of the amendment's analytic arm is
  about, and it is the frozen wording ("same size"). It makes a typed cell's
  primary ratio a *typing* effect rather than an element-geometry effect, so the
  same-typing control is reported for every typed cell as well; against it both
  typed geometries have a mean ratio of exactly 1.
* `asym_element_choice` had to be pinned because the frozen definition of
  H004 names sizes only. Random elements isolate the sizing question.

## Verification of the group order and the dlog table

For every generated curve (12 of 12 verified, `all_ok: true`):

* order from the exact character sum `#E = p + 1 + sum_x legendre(x^3+ax+b, p)`;
* `N` prime (sympy) and inside the Hasse interval;
* `N*G = O` by double-and-add, a code path independent of the table build;
* the multiple enumeration closes exactly at `N` (`(N-1)G = -G`);
* the table has exactly `(N-1)/2` distinct x-coordinates, `x(kG) = x((N-k)G)`,
  `y(kG) + y((N-k)G) = 0`, and the log table is a bijection;
* 20 seeded random multiples re-checked by double-and-add.

Together these give an independent proof of the order: `ord(G) = N` divides
`#E`, `N` is prime, and `#E <= p + 1 + 2 sqrt(p) < 2N`, so `#E = N`.

## Deviations from the approved protocol

* **D1 — null draws raised from the frozen minimum 100 to 200 (strengthening).**
  With 100 draws the smallest attainable permutation p-value under the
  `(r+1)/(n+1)` convention is `1/101 = 0.0099`, and `8 x 0.0099 = 0.079 > 0.05`,
  so *no* cell could have been Holm-rejected at `alpha = 0.05` regardless of the
  data — the family test would have been structurally unable to reject. 200
  draws give a floor of `1/201 = 0.00498` and `8 x 0.00498 = 0.0398 < 0.05`.
  The amendment specifies ">= 100", so 200 is inside the contract; it is
  recorded here because it is a deliberate choice, not a default.
* **D2 — closed-form total control generalised to every typing pattern.** The
  handoff names `binomial(B+2,3)` for untyped bases and `B1*B2*B3` for typed
  bases. `mixed_two_base` has two sub-bases and a (1,2) type pattern, whose
  closed form is `B1 * C(B2+1,2)`. The control was applied with the closed form
  of each cell's own pattern; the (1,2) forms are checked against brute force in
  RUN-FB3-001-CTRL block A.
* **D3 — prior cells censored at 2^16 and 2^18.** The recorded H016/H017 cells
  exist at 2^14 and 2^17 only. Their recorded statistics enter the 2^14 family;
  at 2^16 and 2^18 their family slots are retained (so the Holm family size
  stays 8, which is conservative) and marked
  `censored_not_recorded_at_this_size`. No prior-cell statistic was extrapolated
  to a size at which it was not recorded.
* **D4 — the QR walk is a same-family reconstruction, not a replay.** The
  recorded conventions do not pin the r-adding walk's RNG stream, index
  function, or start point, so the H016 QR *geometry* cannot be replayed
  bit-exactly. It is reported only in the exploratory replication section, never
  as a pre-registered cell, and the port-fidelity control compares it
  distributionally. The H017 small-multiples geometry, by contrast, IS exactly
  determined by the recorded convention (dedup-by-x of `x(jG)`, `j = 1..2B`, is a
  no-op in log space for `2B < N/2`, so the base is `{1,...,B}` whatever `G`
  is), and it is reproduced exactly.
* **D5 — one added derived run.** `RUN-FB3-001-FAMILY` performs no measurement;
  it aggregates the immutable size runs so that the family table, Holm
  correction, growth slopes, and analytic-arm checks are machine-generated
  rather than hand-copied. 5 runs total against a budget of 12.

No pre-registered cell was dropped, reordered, or added; no geometry variant
outside the frozen list was introduced into the family; no stopping rule was
triggered by an outcome.

## Reproduction

Each run directory records the exact command. Re-running the recorded command
for `RUN-FB3-001-N14` and `RUN-FB3-001-N18` at the same revision reproduced the
raw result **bit-for-bit** except for 17 wall-clock fields per run (16 greedy
`selection_seconds` plus the run timing block); every measured statistic,
including all 200-draw null sets, was identical.
