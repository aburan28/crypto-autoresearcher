# J1 — Predicate fidelity audit

**Task** TASK-20260907-b2a8ad (Validator, `review-breakthrough` requested at `max`)
**Joint** J1 only. J2 and J3 are reported in `j2_output.json` / `j3_replication_table.json`
and in `validation_report.yaml`. J4, J5 and J6 belong to TASK-20260907-ee1ca7 and are
not addressed here.
**Question** Does `experiments/EXP-ECDLP-612fb1/source_v3/g3_predicate.py` compute the
predicate that `experiments/EXP-ECDLP-612fb1/amendments/v2_to_v3.yaml` Section 3
(`g3_predicate`) defines, or a nearby one?
**Snapshot read** `fe6cdf59f`, verified an ancestor of session HEAD `72ad14bfd`.
**Verdict** **HOLDS**, with two findings recorded below. Finding **F2 is a defect in the
amendment's own text, not in the implementation**, and it is reported because Section 3
requires exactly that.
**Provenance of every reference below** `internal`, read directly by this validator at
the snapshot commit.

---

## 1. Clause-by-clause

Section 3 clause → implementation, in the amendment's own order.

### `parameters` and `exact_parameter_table_for_this_item` — HOLDS

`g3_predicate.make_params` returns `instrument.Params(n_bits, a, seed)`, whose
`__post_init__` (`source_v2/instrument.py:72-91`) sets `T = T_OF_NBITS[n_bits]`
(frozen: 64 at n=20, 256 at n=24 — not a recomputed rounding, as the clause requires),
`W = sqrt(a*N/T)` **real-valued and unrounded**, `theta = 1/W`, `cap = ceil(8*W)`.
`t_sel_of(T) = T // 2` gives `T_sel` = 32 at n=20 and 128 at n=24.

I recomputed the amendment's table from the formulas: at n=24, `a=1/16` → `W=64.000000`,
`theta=0.015625000`, `cap=512`; `a=1/8` → `W=90.509668`, `theta=0.011048544`, `cap=725`.
Both agree with the printed table at every quoted digit. The run records carry the same
values in `cells[a].modeled`.

### `reading_P1_frozen_instrument` — HOLDS

`Params.step` is `mix64(x ^ K) & (N-1)` and `Params.is_dp` is
`mix64(x ^ K_dp) < floor(2^64 / W)` (`instrument.py:114-119`), with
`K = mix64_int(0x9E3779B97F4A7C15 + s)` and `K_dp = mix64_int(K ^ 0xD1B54A32D192ED03)`
(`instrument.py:81-82`), and `mix64` the splitmix64 finaliser with the constants
`0xBF58476D1CE4E5B9` and `0x94D049BB133111EB` and shifts 30/27/31 (`instrument.py:43-61`).
This matches the amendment's verbatim restatement term for term, including the wrapping
mask and the `dp_threshold = floor(2^64 / W)` form.

### `basins` — HOLDS

`instrument.exact_basins` (`instrument.py:194-215`) computes the basin partition exactly by
pointer doubling: DPs are made self-absorbing (`nxt[dp] = flatnonzero(dp)`), `dist` starts at
0 on DPs and 1 elsewhere, and `n_bits` doubling rounds give `dist = min(2^n_bits, true dist)`.
Then `reach = dist < 2^n_bits` marks trajectories entering a DP-free cycle as
**UNREACHABLE**, `ok = reach & (dist <= cap)` additionally excludes **CAPPED** points, and
`size = bincount(searchsorted(dps, nxt[ok]))` counts only `ok` points. Points with
`dist > cap` and points on DP-free cycles therefore belong to no basin, and `dist(d) = 0`
for a DP puts every DP in its own basin — all exactly as the clause states.

This is the one clause I could check by an **independent route rather than by reading**.
My own implementation of the same clause (`j2_blind_rederivation.py:exact_basins`, written
pre-seal from this text alone) was verified against a naive per-point brute-force walk on
six randomized fixtures spanning `N = 2^9 .. 2^12` and `cap = 1, 3, 8, 16, 40, 200`: basin
dictionaries identical and capped/unreachable mass identical in all six, including the cap
boundary and DP-free cycles. The two implementations agree on the clause's semantics.

### `top_share` — HOLDS. This was the clause the review plan expected to break; it does not.

`Basins.top_share(t)` is `sort(size)[::-1][:t].sum() / self.N` (`instrument.py:184-186`).
The denominator is **`self.N`, the full space size** — not `N` minus capped mass, not the
basin mass total. `Basins.coverage` uses the same `self.N` (`instrument.py:177-182`).

The plan's attack (4) was that "a denominator convention that quietly drops capped mass
would inflate every share". It does not occur: capped and cycle mass are excluded from the
numerator (they are in no basin) and retained in the denominator, which is the only
convention consistent with `TopShare` being a single-walk hit probability. As a
cross-check, `basin_mass_total + cycle_mass + capped_mass = N` holds in the run records'
`basin_structure` block, and my own independent implementation used the same convention
from the same text.

### `pool` — HOLDS

`build_pool` delegates to `instrument.generate_pools(P, [r])[r*P.T]`
(`instrument.py:243-289`). Checked against each sentence of the clause:

| clause requirement | implementation |
| --- | --- |
| independent uniform starts from a deterministic stream seeded by `s` | `rng = default_rng(P.seed)`, `rng.integers(0, P.N, size=4*P.T)` |
| walk each start to its first DP or the cap | `walk_to_dp` (`instrument.py:126-151`) |
| a capped walk is a MISS, charged `cap`, contributing nothing | `length[active] = P.cap` on exit; `t < 0` branch increments `capped` only and credits no DP |
| a hit at `d` with length `L` credits `S_d += L`, `h_d += 1` | `S[j] += L; h[j] += 1`, with `L = 0` when the start is itself a DP |
| **every** generating walk, hit or miss, charged to P | `walks += 1` and `P_cost += L` before the hit/miss branch |
| generation stops at the first moment the pool holds exactly `r*T` **DISTINCT** DPs | snapshot taken inside the per-walk loop when `len(dps) == targets[want]`, where `dps` is the distinct-DP list — a count of DISTINCT DPs, not of walks |

The termination test is on distinct DPs and is evaluated after each walk, so the snapshot is
taken at the exact moment the clause names. `walk_to_dp` is called on a whole batch of
`4*T` starts, but `P_cost` and `walks` accumulate only up to the break, so the cost
accounting is not inflated by the unconsumed remainder of the batch.

### `selection` — HOLDS on the load-bearing question

`selection_weight(ev, W)` returns `ev.S + 4.0 * W * ev.h` — the published weight
`w(d) = S_d + 4*W*h_d` — and its only arguments are the `PoolEvidence` and the modeled
scalar `W`. `instrument.numpy_select` is `lexsort((keys, -weights))[:t]`, i.e. `w`
**descending** with the tie-break key **ASCENDING**, which is the clause's ordering.
`CountedSelector._less` implements the same order (root = smallest weight; among equal
weights the largest key) and the final `heap.sort(key=lambda e: (-e[0], e[1]))` agrees.
`tiebreak_keys` draws one `int64` per pool entry from `default_rng(400 + s)`, which is v2's
frozen `Params.seed_tiebreak`.

### `static_coverage` — HOLDS

`Basins.coverage(table)` sums `size` over the selected DPs and divides by `N`. It is called
in REGION D on a table already chosen in REGION C. Exact basin sizes therefore **score** a
selection that was made without them.

### `predicate_per_seed` and `predicate_per_cell` — HOLDS

`margin_of` is `TopShare(T_sel) - StaticCov`, `g3_seed_flag` is `margin >= 0`, and
`g3_cell_verdict` returns `PASS` iff `pass_count >= 4` over a 5-element margin list
(`G3_PASS_THRESHOLD = 4`). I recomputed `margin` and the `g3` flag from
`top_share_T_sel - static_cov` in **all 120 measured cells** of the ten measurement runs:
**0 mismatches**. I recomputed all **24** rows of `g3_verdict_table.json` (pass_count and
verdict) from the ten run records: **0 mismatches**.

The threshold is applied **per `(N, a, r)` cell and never pooled across `r`**: the verdict
table holds 24 rows, one per distinct `(N, a, r)` triple, each carrying its own
`pass_count` and its own `threshold: ">= 4 of 5"`. This was the plan's check (5) and it
passes.

### Same code path for every cell — HOLDS

`run_stage3.py:207-228` is a single uniform loop, `for a in a_grid: ... for r in r_grid:
cell["by_r"][str(r)] = G.measure_cell(P, basins, r)`. There is no per-`a` branch, no
hard-coded expectation, and no cell skipped; the known-false objects of Section 6 are
evaluated by the same call as the primary cells. (Whether they *return* FAIL is J4's, not
mine.)

---

## 2. The named invalidation rule: does any exact-basin array reach the selection?

The amendment's last `invalidation_rules` entry is: *"Reading TRUE BASIN SIZE anywhere in
the SELECTION path (as opposed to the SCORING path): invalid."* The task card puts it
structurally: *no exact-basin array may be in scope at the point the weight is computed.*

**Answer: no true basin size is read in the selection path. The invariant holds.** I
establish it two independent ways, because reading alone cannot distinguish "does not read
it" from "reads it somewhere I did not look".

### (a) By data flow — every input to `w` traced to its origin

`selection_weight` reads exactly `ev.S`, `ev.h` and the scalar `P.W`. `ev` is the
`PoolEvidence` built in `build_pool` from `PoolSnapshot.S` and `.h`, which
`generate_pools` accumulates from `walk_to_dp`'s `(term, length)` — and `walk_to_dp`
iterates the map directly and constructs no `Basins` object and no length-`N` array.
`PoolEvidence` has no basin field. The three REGION C functions take only
`(ev, W)`, `(weights, keys, T)` and `(ev, indices)`; none can reach a basin size.
`P.W` is a modeled scalar from `sqrt(a*N/T)`, not a measurement.

### (b) Empirically — the plan's attack (2), run

I replaced the weight vector with **true exact basin sizes** for the same pool, same keys,
same `T`, and re-scored (`/tmp/val_b2a8ad/j1_probe.py`, post-seal, using the producer's own
code):

| cell (N=2^24, r=2) | pass by `w(d)` | pass by TRUE basin size | verdict changes |
| --- | --- | --- | --- |
| a = 1/16 | 5/5 | 5/5 | no |
| a = 1/8 | 5/5 | **0/5** | **yes — all five seeds flip sign** |

At `a = 1/8` the substitution flips every seed: `+0.009002 → −0.007454`,
`+0.005128 → −0.008888`, `+0.003084 → −0.016441`, `+0.005594 → −0.007711`,
`+0.011855 → −0.000449`. **If the selection were already reading basin sizes, this
substitution would have been a no-op.** It is the opposite of a no-op, so the selection
demonstrably is not reading them, and the selection rule is load-bearing exactly where the
amendment says it is.

At `a = 1/16` the cell verdict does *not* change, which the plan flagged as ambiguous
("either the cell is insensitive or the selection is already reading basin sizes — both are
findings"). Here it is demonstrably the former: every per-seed margin moves materially in
the expected direction (e.g. seed 3: `+0.013719 → +0.003265`, a drop of 0.0105), so the
weight is not the true size; `a = 1/16` simply has enough headroom to survive the stronger
comparator. The direction is correct in all ten cells — selection by true size is a
strictly stronger rule, so it raises `StaticCov` and lowers the margin, never the reverse.

For the record, the amendment quotes EV-ECDLP-2e9680's diagnostic as giving `a = 1/8`:
`5 → 1`. On *this* lane's instrument I measure `5 → 0`. That is a different diagnostic on a
different pool draw, not a discrepancy in this batch; noted so a later reader does not read
`0` and `1` as a contradiction.

### FINDING F1 — the invariant holds as information flow; the run-time guard does not prove it, and one enclosing scope is wider than the task card's wording

Two scope observations, neither a break:

1. `measure_cell(P, basins, r)` carries `basins` in its **enclosing lexical scope** at
   line 392, where `selection_weight(ev, P.W)` is called. Nothing reads it there, and the
   amendment's rule is about *reading*, which does not occur — so the invalidation rule is
   not triggered. But the task card's stricter structural phrasing ("no exact-basin array
   in scope at the point the weight is computed") is satisfied only at the granularity of
   the REGION C functions, not at the granularity of their caller. A successor amendment
   wanting the structural guarantee would have to pass the pool to a selector that returns a
   table, and score in a separate function that never sees the pool.
2. `_assert_evidence_only` is advertised in the module docstring as making the invariant
   "mechanically checkable". It is a **length tripwire, not an information-flow proof**: it
   checks `isinstance(ev, PoolEvidence)` and that `len(dps) == r*T == len(S) == len(h)`. A
   `PoolEvidence` whose `S` had been *derived from* basin sizes would pass it unchanged, as
   long as its length were `r*T`. It catches the crudest error (smuggling a length-`N`
   array) and is worth having; it should not be cited as establishing the invariant. The
   evidence for the invariant is (a) and (b) above.

---

## 3. FINDING F2 — the amendment's justification for leaving the tie-break unfixed is factually wrong; its conclusion survives at these cells, with limited headroom

Section 3 `selection` says ties are broken by a seeded ascending key, and adds:

> *"any deterministic tie-break is acceptable for the P2 reading, since ties in a
> real-valued `w` are measure-zero and the choice cannot change a verdict."*

And `what_a_reviewer_needs_and_this_section_does_not_give` requires: *"If a reviewer
believes either DOES change a verdict, that is itself a finding and must be reported, not
absorbed."* So this is reported.

**The premise is false.** `w(d) = S_d + 4*W*h_d` with `S_d` and `h_d` non-negative
**integers** is supported on a countable set, not on a continuum; and at `a = 1/16`,
`W = 64` exactly, so `4W = 256` and `w` is an **integer**. Ties are structural, not
incidental. Measured on the producer's own ten primary cells:

| cell | pool entries in some tie (of 512) | tie straddles the T=256 cut | margin spread over 64 alternative tie-break streams |
| --- | --- | --- | --- |
| a=1/16 s1 | 430 | no | 0 |
| a=1/16 s2 | 434 | **yes** | 1.90e-04 |
| a=1/16 s3 | 414 | **yes** | 6.58e-04 |
| a=1/16 s4 | 426 | no | 0 |
| a=1/16 s5 | 412 | no | 0 |
| a=1/8 s1 | 399 | **yes** | 8.89e-05 |
| a=1/8 s2 | 401 | no | 0 |
| a=1/8 s3 | 383 | **yes** | 1.16e-03 |
| a=1/8 s4 | 401 | **yes** | 3.35e-04 |
| a=1/8 s5 | 385 | **yes** | 2.22e-05 |

75–85 % of pool entries lie in some tie at every cell, and the tie **straddles the
selection cut in 6 of the 10 cells** — so the tie-break stream really does decide which
entries enter `STATIC(T)_r`, and it really does move `StaticCov`.

**The conclusion nonetheless holds at the tested cells.** Across all 640 (cell × stream)
combinations I measured, **no per-seed sign flipped**. At the tightest cell — `a = 1/8`
seed 3, whose margin is `+0.003084` — the minimum over 64 streams was `+0.002003`, still
positive; the margin is about 2.7× the tie-break-induced spread there.

So the correct statement is: *the tie-break choice does not change a verdict at these
cells, as measured, with roughly 2.7× headroom at the tightest seed* — not *ties are
measure-zero so it cannot*. The amendment reached a right answer by a wrong argument. This
matters beyond pedantry for two reasons: the wrong argument would license ignoring the
tie-break at cells with less headroom, and `a = 1/8` is already the cell whose PASS is
least robust (J2). Any successor amendment should restate this clause as a measurement with
its headroom, and should fix the tie-break stream rather than declaring it irrelevant.

The producer is not at fault here and did the right thing: `IMPLEMENTATION.md` §3 discloses
both open choices explicitly (the pool-start PRNG as `default_rng(s)` in batches of `4*T`,
and a fresh `default_rng(400+s)` per selection), which is what the clause asks of an
implementer.

---

## 4. Summary

| clause | verdict |
| --- | --- |
| `parameters`, exact parameter table | holds |
| `reading_P1_frozen_instrument` | holds |
| `basins` (cap, cycle, DP self-basin) | holds — independently cross-checked |
| `top_share` (numerator and denominator) | holds — the flagged inflation does not occur |
| `pool` (distinct-DP stop, every walk charged, misses credit nothing) | holds |
| `selection` (`w(d)`, pool evidence only, ascending tie-break) | holds |
| basin sizes SCORE, never MAKE | holds — proved by data flow **and** by substitution test |
| `static_coverage` | holds |
| `predicate_per_seed`, `predicate_per_cell` (≥4 of 5, per cell) | holds — 120 cells and 24 rows recomputed, 0 mismatches |
| same code path for all cells | holds |

**J1 verdict: HOLDS.** The implementation computes the predicate Section 3 defines, not a
nearby one. Finding F1 is a scope-of-guarantee observation about how the invariant is
established (it is established, just not by the guard that claims to). Finding F2 is a
defect in the amendment's text that the amendment's own clause required a reviewer to
report; it does not change any verdict in this batch, and it is a caveat on `a = 1/8`
rather than on `a = 1/16`.
