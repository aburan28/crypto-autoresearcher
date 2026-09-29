# TASK-20260822-a7a9e8 — Mestre-style high-rank curve construction

Executor run record for GOAL-ECRANK-002 / BATCH-e0caa5.
Observations only; no interpretation of significance, and no statement about
whether H-ECRANK-f2a2f7 is supported.

* Implementation commit: `f5fb41f53221807d74112f1493cb218a4b1756c8`
  (branch `claude/elliptic-curve-high-rank-h0y9j2`, working tree dirty — this
  task's own artifacts)
* Environment: Python 3.11.15, cypari 2.5.6 / PARI 2.15.4, numpy 2.4.6,
  Linux 6.18.44. No Sage, no sympy.
* Requested inference policy: `executor-implementation`; model that answered:
  `claude-opus-5` (Claude Code runtime, effort `medium`).
* Budget: 2400 s wall clock / 4 GB / 40 runs.
  **Used: 1218 s across 8 runs**, each capped with `ulimit -v 4194304` and
  `timeout`. No cap was hit.

---

## 1. Headline measurement

**Maximum certified rank actually reached: 13.**

Certified means: 13 exhibited rational points, each re-verified on the reported
minimal model in exact rational arithmetic by our own `fractions` code, whose
13x13 Néron–Tate height pairing matrix is non-singular. No analytic rank, no
`ellrank` `r_high`, and no point-free bound contributes anywhere in this task.

The two rank-13 curves (both from parameter sets under `|a_i| <= 20`):

| A (the 10 prescribed x-values) | minimal model `[a1,a2,a3,a4,a6]` | rank | regulator det | min. eigenvalue |
|---|---|---|---|---|
| `[-20,-16,-14,-13,-7,-6,2,3,14,19]` | `[1,0,0,-10735733389588488545, 13386166243940268673745678025]` | 13 | 8.17042e+10 | 0.5773 |
| `[-12,5,6,7,9,10,11,13,14,17]` | `[1,-1,1,-97623025006346669, 342379984015184906117269]` | 13 | 1.00069e+12 | 0.8414 |

Full point lists, per-curve regulator determinants and construction data for
1206 curves are in `highrank_pool.json`.

Rank distribution actually certified (see §4 for the volume each came from):

| certified rank | 13 | 12 | 11 | 10 | 9 | 8 | 7 | <= 6 |
|---|---|---|---|---|---|---|---|---|
| curves (M10 + extra-point scan, 34 740 scanned) | 2 | 29 | 425 | 3 445 | 29 392 | 1 447 | – | – |
| curves (M10 construction alone, 39 876 built) | – | – | – | – | 32 805 | 4 501 | 1 702 | 868 |
| curves (M8 control, 2 985 built) | – | – | – | – | – | – | 1 751 | 1 234 |

For contrast with the input the handoff supplied, the predecessor twist search
(GOAL-ECRANK-001) reported no twist of rank >= 5 in 364 756 candidates and 2
curves of rank 4 in 49 692 enumerated. Those are different searches over
different objects; this task did not re-run them.

---

## 2. The construction, precisely enough to re-run

All of the following is implemented in `src/construct_highrank.py`, whose module
docstring is the normative statement. Summary:

### 2.1 Mestre polynomial step (forces 2k simultaneous square conditions)

Choose 2k distinct rationals `A = {a_1, ..., a_{2k}}` (here: distinct integers).

```
p(x) = prod_{i=1..2k} (x - a_i)                    monic, degree 2k
g(x) = unique MONIC degree-k polynomial with deg(p - g^2) <= k-1
       (polynomial part of the Laurent expansion of sqrt(p) at infinity;
        computed by exact coefficient matching over Q, no floating point)
s(x) = g(x)^2 - p(x)                               degree <= k-1
```

Since `p(a_i) = 0`, we get **`s(a_i) = g(a_i)^2` for every i** — 2k simultaneous
square conditions, by construction rather than by search. So `y^2 = s(x)`
carries the 2k rational points `(a_i, g(a_i))`.

### 2.2 The two instantiations

**M8** (`2k = 8, k = 4`): `deg s = 3`, so `y^2 = s(x)` is already a cubic. The
8 points are scaled to `Y^2 = X^3 + a2 X^2 + a4 X + a6` by `X = c3 x, Y = c3 y`
where `c3 = lead(s)`.
*Structural ceiling 7*: `g(x) - y` has a pole of order 8 at infinity and
vanishes at all 8 points, so the 8 points sum to `O` — one relation, hence at
most 7 independent. The M8 control run hit exactly 7 and never 8.

**M10** (`2k = 10, k = 5`): `deg s = 4`, so `y^2 = s(x)` is a **quartic** model
with 10 rational points. Reduced to a cubic as follows. Pick base index `i0`,
put `e = g(a_{i0}) != 0`, shift `u = t + a_{i0}` so
`v^2 = s~(t) = a t^4 + b t^3 + c t^2 + d t + e^2`. Intersect with the osculating
parabola `v = e + (d/2e) t + m t^2`:

```
s~(t) - (e + (d/2e)t + m t^2)^2
      = t^2 * [ (a-m^2) t^2 + (b-(d/e)m) t + (c - d^2/(4e^2) - 2em) ]
```

so a rational point with `t != 0` exists iff the discriminant is a square:

```
w^2 = D(m) := (b-(d/e)m)^2 - 4 (a-m^2)(c - d^2/(4e^2) - 2 e m)   (cubic in m, lead -8e)
m = (v - e - (d/2e) t) / t^2 ,     w = 2(a-m^2) t + (b-(d/e) m)
```

`D(m)` is expanded in exact rational arithmetic at run time — no coefficient
formula is quoted from memory — and **every mapped point is re-checked to
satisfy `w^2 = D(m)` exactly** before it is used. The base point `t = 0` maps to
infinity, so 9 of the 10 survive.
*Structural ceiling 9*: `g(u) - v` has pole order 5 at each of the two points at
infinity and vanishes at all 10 quartic points, giving one relation. The M10
construction alone reached exactly 9 and never 10, on 39 876 curves.

Finally `w^2 = A3 m^3 + A2 m^2 + A1 m + A0` becomes `Y^2 = X^3 + A2 X^2 +
A1 A3 X + A0 A3^2` via `X = A3 m, Y = A3 w`; denominators are cleared by
`(X,Y) -> (u^2 X, u^3 Y)`; PARI `ellminimalmodel` + `ellchangepoint` move curve
and points to a minimal model, which is what the pool reports.

### 2.3 Extra-point augmentation (this is what exceeds 9)

On the **quartic** model `v^2 = s(u)`, scan `u = n/d` with `|n| <= 400`,
`1 <= d <= 12`, `gcd(n,d) = 1`, `u` not already an `a_i`, and test whether
`s(u)` is a rational square by an exact integer perfect-square test (`isqrt`,
no floating point). Each hit is pushed through the same reduction of §2.2 and
appended to the 9. Ranks 10–13 all come from here.

### 2.4 Reproduction

```sh
cd coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-a7a9e8
python3 src/construct_highrank.py m8  --trials 3000  --seed 20260822 --amax 14 --budget 240 --out m8.json
python3 src/construct_highrank.py m10 --trials 40000 --seed 20260822 --amax 20 --budget 600 --out m10.json
python3 src/construct_highrank.py augment --pool m10.json --top 40000 --nmax 400 --dmax 12 --budget 700 --out aug.json
python3 src/assemble_pool.py m8.json m10.json aug.json highrank_pool.json 150
python3 src/verify_pool.py  highrank_pool.json          # stdlib only, no PARI
python3 src/scrutinize.py   highrank_pool.json scrut.json 12
```

Sources of randomness: exactly one — `random.Random(seed).sample` choosing the
integer set `A`; `seed = 20260822` for both searches. Everything downstream is
deterministic. `--budget` is a wall-clock cut, so on a slower host the searches
cover fewer trials; the per-trial output is unaffected.

---

## 3. Certification and what was checked

| check | where | result |
|---|---|---|
| every exhibited point on its curve, exact `Fraction` arithmetic, our own code | `construct_highrank.verify_on_curve` during search | pass, all curves |
| the same, re-done by an **independent stdlib-only verifier** that never calls PARI, plus distinctness, nonsingularity, rank-equals-points, and reproducibility of `s` from `A` | `src/verify_pool.py`, RUN-007 | **1206 curves, 11 499 points, 0 failures, PASS** |
| height pairing matrix determinant (`ellheightmatrix` / `matdet`) per curve | search, at 60 and 120 digits | reported per curve in `highrank_pool.json` as `regulator_det`, `regulator_det_highprec`, `hadamard_ratio` |
| high-scrutiny re-verification of all 31 curves of rank >= 12: height matrix at **60 / 120 / 250** digits, determinant stability, smallest eigenvalue via `numpy.linalg.eigvalsh` | `src/scrutinize.py`, RUN-006 | **31/31 certified**; determinants agree across all three precisions; smallest eigenvalue in `[0.41, 4.42]`, i.e. bounded far from 0 (a genuine relation would force a 0 eigenvalue) |
| PARI `ellisoncurve` (redundant, not load-bearing) | RUN-006 | pass |

**Singular-determinant handling.** When the full point set's height matrix is
numerically degenerate (Hadamard ratio `|det| / prod(diagonal) <= 1e-9`), the
points are **not** treated as independent: a maximal independent subset is
extracted greedily and the rank claim drops to the size of that subset. This
fired often and is visible in the data — e.g. in RUN-004, 24 660 of the 34 740
augmented curves gained nothing from their extra points, and curves with 5, 9
or 15 extra points still certify only 9 because the extras were dependent. The
detector discriminates; it does not rubber-stamp.

**Falsification cross-check that returned nothing (RUN-008).** For all 31
curves of rank >= 12 we asked PARI `ellrank` for an *upper* bound purely to test
whether it ever falls **below** our certified count — which would mean our
independence claim was wrong. All 31 calls hit the 25 s `alarm` or errored
(2-descent is infeasible at these coefficient sizes, `a4 ~ 1e19`, `a6 ~ 1e28`).
**31/31 infrastructure timeouts, 0 informative results, 0 contradictions.** Per
the handoff this is an infrastructure outcome and decides nothing in either
direction; it is neither evidence for nor against the rank claims.

---

## 4. Search volume actually covered

| run | what | volume | wall clock | outcome |
|---|---|---|---|---|
| RUN-001 | M8 control | 3 000 integer sets `A` drawn from `[-14,14]`, 2 985 built, 14 degenerate | 33.0 s | max certified rank **7** (1 751 curves), never 8 |
| RUN-002 | M10 main search | 40 000 integer sets `A` drawn from `[-20,20]`, 39 876 built, 124 degenerate | 379.3 s | max certified rank **9** (32 805 curves), never 10 |
| RUN-003 | augmentation pilot, 40 curves | 40 x ~6 400 candidate `u` | 4.6 s | first rank **11** |
| RUN-004 | augmentation, full pool | **34 740 curves** x ~6 400 candidate `u` ~ **2.2e8** square tests; 30 831 extra points found on 9 885 curves | 703.5 s | max certified rank **13** (2 curves) |
| RUN-005 | pool assembly | 1 206 curves selected | 4.9 s | `highrank_pool.json` |
| RUN-006 | high-scrutiny verification, rank >= 12 | 31 curves x 3 precisions | 0.7 s | 31/31 certified |
| RUN-007 | independent stdlib verification | 1 206 curves / 11 499 points | 1.1 s | PASS, 0 failures |
| RUN-008 | upper-bound falsification cross-check | 31 curves, 25 s alarm each | 90.7 s | 31/31 timeout, 0 contradictions |

RUN-004 stopped on its own 700 s internal budget after 34 740 of the 39 876
curves, having covered every rank-9 curve (32 805) and 1 935 of the rank-8 ones.
The 5 136 curves not reached are all of base rank <= 8.

Cost per unit: M10 construction + 9x9 regulator ~ **9.4 ms/curve**;
augmentation scan + regulator ~ **20 ms/curve**.

Pool selection rule (declared, not outcome-tuned): **all** curves of certified
rank >= 11, plus the first 150 in search order at each of ranks 10, 9, 8 (M10)
and 7 (M8 control). Recorded verbatim in the `selection_rule` field of
`highrank_pool.json`.

---

## 5. Where the method stopped paying off

Stated as measurements, not as conclusions.

1. **Each construction saturates exactly at its function-theoretic ceiling, and
   the ceiling is not soft.** M8 produced rank 7 on 1 751 of 2 985 curves and 8
   on none; M10 produced rank 9 on 32 805 of 39 876 and 10 on none. Additional
   parameter volume against the *bare* construction buys nothing once the
   ceiling is reached — the last 30 000 M10 trials raised the maximum by 0.
2. **Above the ceiling, yield falls off fast.** Of 34 740 augmented curves:
   84.6% stay at 9, 9.9% reach 10, 1.22% reach 11, 0.083% reach 12, 0.0058%
   reach 13. Each further step costs roughly a 10x larger sample than the last.
3. **Extra points are usually dependent.** 9 885 curves yielded 30 831 extra
   points; 71% of curves with extras gained no rank at all from them.
4. **The scan box, not the curve supply, is the near-term limit.** Every rank-12
   and rank-13 hit came from `|n| <= 400, d <= 12`; the scan is `O(nmax * dmax)`
   per curve with a cheap integer test, so it is the obvious knob, and it was
   not widened within this budget.
5. **Verification cost is not the bottleneck** (9–20 ms/curve), but *independent
   upper-bound* verification is completely unavailable at these coefficient
   sizes (§3, RUN-008): 31/31 2-descents timed out. Any claim about these curves
   therefore rests on exhibited points plus height regulators, and nothing was
   obtained that would bound the rank from above.

---

## 6. Deviations, anomalies, and infrastructure events — all recorded

1. **Concurrent external write into this task's run directory.** While RUN-004
   was executing, a process outside this session (evidently the archiving task
   TASK-20260822-e7c486) wrote `runs/RUN-a7a9e8-002-m10-main/raw-result.json.gz`
   and `runs/RUN-a7a9e8-002-m10-main/RAW-RESULT-STORAGE.md` into this task's run
   directory, and added a `.git/info/exclude` entry for that run's uncompressed
   `raw-result.json`. Those two files were authored by that process, not by this
   executor, and have been left untouched. Reason given there: the file was
   112 301 654 bytes and exceeds GitHub's 100 MB limit.
2. **Storage trim of two large raw results, and a collision with (1).** Not
   knowing about (1), this executor trimmed
   `RUN-a7a9e8-002-m10-main/raw-result.json` (39 876 -> 300 curve records) and
   `RUN-a7a9e8-004-augment-full/raw-result.json` (34 740 -> 300 result records)
   with `src/trim_raw.py`, which preserves every aggregate statistic verbatim
   and embeds the exact regeneration command.
   * For RUN-002 the trim was **fully reversed**: the file was restored from the
     external `.gz` and its sha256 verified to equal the recorded original,
     `ff0935a0c68c58da7da3fdb861f36d80e33f72365fb2ecb57d8196b0af5ccb47`.
     RUN-002's `raw-result.json` is the complete original artifact again.
   * For RUN-004 the trim **stands and is a real reduction of that artifact**;
     it was applied before any copy existed. Nothing outcome-relevant was
     discarded: all aggregates are verbatim, all 456 curves of rank >= 11 are in
     `highrank_pool.json` in full, and the untrimmed `stdout.log` still carries
     one line per curve (`A`, base rank, extras found, augmented rank) for all
     34 740. The run is deterministic, so the full file is regenerable from the
     recorded command; it was not regenerated because that costs ~700 s of a
     2400 s budget for no new measurement. **Flagging for the Coordinator:**
     if the archive requires byte-verbatim raw results, RUN-004 must be re-run
     under a new run ID.
3. **PARI stack warning** (`ellrank: Warning: increasing stack size to 8003584`)
   in RUN-008 stderr. Benign; the run completed.
4. **31/31 `ellrank` timeouts** in RUN-008, recorded as infrastructure outcomes
   and used as evidence for nothing (§3).
5. **Degenerate parameter sets** were skipped, not silently retried, and are
   counted: 14 of 3 000 in RUN-001, 124 of 40 000 in RUN-002 (`s` failed to have
   full degree, or `e = 0`, or image points collided). 0 PARI errors during
   construction or scoring in RUN-001/002/004.
6. **No run was repeated to obtain a better outcome.** RUN-003 is a 40-curve
   pilot of the same code RUN-004 then ran at full scale; both are reported.
7. `src/trim_raw.py` appended one `raw_result_trimmed_for_storage:` line to each
   `manifest.yaml`. Manifests were otherwise not edited after their run.

---

## 7. Artifacts

```
coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-a7a9e8/
  highrank_pool.json                    1206 curves; a-invariants, all points,
                                        independent points, certified rank,
                                        regulator determinant, construction data
  report.md                             this file
  src/construct_highrank.py             the construction + search (normative docstring)
  src/verify_pool.py                    independent verifier, python stdlib only
  src/scrutinize.py                     3-precision regulator / eigenvalue scrutiny
  src/assemble_pool.py                  declared-rule pool assembly
  src/trim_raw.py                       storage trim (see section 6.2)
  src/crosscheck_upper.py               upper-bound falsification cross-check
  src/run.sh                            run-record harness (manifest/env/logs/caps)
  runs/RUN-a7a9e8-001-m8-control/       } each: manifest.yaml, command.txt,
  runs/RUN-a7a9e8-002-m10-main/         } environment.json, stdout.log,
  runs/RUN-a7a9e8-003-augment/          } stderr.log, raw-result.json
  runs/RUN-a7a9e8-004-augment-full/
  runs/RUN-a7a9e8-005-assemble/
  runs/RUN-a7a9e8-006-scrutiny/
  runs/RUN-a7a9e8-007-independent-verify/
  runs/RUN-a7a9e8-008-upper-crosscheck/
```

Nothing was written outside this directory. No git commit was made.
