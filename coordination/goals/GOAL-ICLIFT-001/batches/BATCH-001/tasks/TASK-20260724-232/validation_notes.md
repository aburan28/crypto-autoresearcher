# TASK-20260724-232 — Validator notes on the EXP-FB3-001 run package

Independent integrity validation of the EXP-FB3-001 run package produced by
TASK-20260724-228 and committed by the Coordinator's snapshot archive
TASK-20260724-230. Terminal verdict is in `validation_report.yaml`
(`overall_verdict: valid_with_findings`, `verdict: passed`).

This document records exactly what was run so that another agent can redo every
check. Nothing under `experiments/` was modified; no git write command was run;
all scratch output went to `/tmp/val/`.

**Scope reminder.** A passed validation means the receipt is admissible
evidence. It does not support an ECDLP claim, does not demonstrate a speedup,
and does not authorize a status transition. Whether the frozen criteria are met
is the Reviewer's, Red Team's and Coordinator's business, not mine.

---

## 0. What was validated, and against what

| item | value |
|---|---|
| snapshot commit | `68e375f720123d4f46b1b5bc686920d77bf5ecf4` |
| recorded parent | `e18c9bc0b90e3031cfa28483fe5571c0fb548dfb` (verified as the actual first parent) |
| HEAD at validation | `ae5503dc288efe74f23a870c59d5870c5f779d72` |
| branch | `cursor/ic-lifting-exact-counting-4e70` |
| frozen contract | `experiments/EXP-FB3-001/specification.yaml` (committed `e111dd3`, DEC-20260717-002) |
| approved amendment | `experiments/EXP-FB3-001/amendment-001.yaml` (committed `81d9e9f`, an ancestor of the run-time revision) |
| runs | `RUN-FB3-001-N14`, `-N16`, `-N18`, `-CTRL`, `-FAMILY` |

The amendment being committed *before* the run-time revision matters: the
conservation identity, the six operational geometry definitions, the matched-size
rule and the analytic arm are verifiably pre-registered rather than
reconstructed after seeing the data. `git diff e18c9bc HEAD --
specification.yaml amendment-001.yaml` is empty, so the frozen contract was not
edited during execution.

---

## 1. Artifact completeness (`pass`)

Script: `/tmp/val/check1.py`.

Each of the five run directories contains exactly the six required files and no
others. Each `manifest.yaml` has a top-level `run` key with non-empty `id`,
`experiment_id`, `status`, `code` (`commit` + `command`), `environment`,
`inputs`, `timing`, `result`; `result.certificate.kind` is `none` everywhere;
`inputs.parameters.field_bits` is 14/16/18/18/18, all `<= 32`, so the claim tier
stays `toy`. `command.txt` equals `run.code.command` in all five. The 25
SHA-256 values the manifests record for their own companions all reproduce.

Ledger validation:

```bash
python3 tools/validate_ledger.py            # exit 1, 154 errors
grep -c "EXP-FB3-001" <output>              # 0
git archive 123fb746 | tar -x -C /tmp/mb    # merge-base tree
cd /tmp/mb && python3 tools/validate_ledger.py   # exit 1, 154 errors
diff <(sort head.txt) <(sort mb.txt)        # identical
```

The 154 errors are byte-for-byte the same at HEAD and at the merge-base, so all
are pre-existing and none are attributable to this package. Note that
`tools/validate_ledger.py` *does* walk `experiments/*/runs/*/manifest.yaml`
(lines 461-465), so the absence of FB3 lines is a positive result, not a gap in
coverage.

Schema-style variance worth knowing about (not a failure): the manifests use
`result.validity` / `result.validity_reason` and put `peak_memory_mb` inside
`timing`, where `docs/evidence-and-reproducibility.md` sketches `result.valid` /
`result.invalid_reason` and a separate `resources` block. The validator tool
does not require those names and all the information is present.

---

## 2. Snapshot receipt integrity (`pass`)

Script: `/tmp/val/check2.py`. Dispatcher check:
`python3 tools/research_dispatch.py .../BATCH-001/dispatch_queue.json` exits 0
with `completed_archive_commits_verified: true` and
`archive_artifact_coverage_complete: true`.

My own verification, independent of the dispatcher:

* all 39 `path_sha256` entries hash to the recorded value **in the working
  tree** (0 mismatches);
* all 39 hash to the recorded value **as blobs at `68e375f7`** (0 mismatches) —
  this is the check that binds the reviewed bytes to the commit, not just to the
  working tree;
* `git diff-tree` reports the commit changed exactly 40 paths, equal as a set to
  `declared_paths`; `declared_paths \ {receipt}` equals the `path_sha256` key
  set, consistent with `receipt_self_hash_excluded: true`;
* `git merge-base --is-ancestor 68e375f7 HEAD` succeeds; the actual first parent
  is the recorded `e18c9bc0…`; the commit message names `TASK-20260724-230`,
  both `record_ids` and all five run ids;
* `git status --porcelain` over the declared paths is empty.

One thing a reader should not trip over: **the receipt file records
`commit_sha: null`.** That is structural — the receipt is committed inside the
commit it describes, so its own content cannot contain that commit's SHA. The
binding SHA lives in the `archive` block of `dispatch_queue.json` for
TASK-20260724-230 (`68e375f720123d4f46b1b5bc686920d77bf5ecf4`), which is what
the dispatcher's verifier reads, and I confirmed it from Git independently. The
receipt's `parent_sha` agrees with the queue's. No integrity problem, but any
downstream record should quote the commit from the queue or from Git, not from
the receipt.

`specification.yaml` and `amendment-001.yaml` are tracked under
`experiments/EXP-FB3-001/` but are not in this receipt; they belong to earlier
archives (see table in §0).

---

## 3. Protocol conformance (`pass`)

Script: `/tmp/val/check3.py`.

**Cell grid.** 6 pre-registered geometries × 3 sizes × 4 curves × replicate
seeds `[1,2,3,4]` = 288 records, every one `terminal_state: measured`, 0
infeasible, 0 invalid. `mixed_two_base__secondary_typing` is measured (16 per
size) but excluded from the Holm family, exactly as the amendment requires.

**Matched size.** I recomputed `B` as the exact integer ceiling of `(6N)^(1/3)`
by integer search (no floating-point cube root), from the recorded `N`:

| size | recorded N per curve | my B | recorded B |
|---|---|---|---|
| 2^14 | 16339, 16253, 16319, 16189 | 47, 47, 47, 46 | 47, 47, 47, 46 |
| 2^16 | 65579, 65213, 65027, 65651 | 74, 74, 74, 74 | 74, 74, 74, 74 |
| 2^18 | 261643, 263941, 262411, 261563 | 117, 117, 117, 117 | 117, 117, 117, 117 |

For 2^14 curve 4, `46^3 = 97336 >= 6N = 97134`, so 46 is correct and the
apparent inhomogeneity in `B` is the frozen rule behaving as written. Typed
sub-base sizes sum to `B` in every mixed cell and every asymmetric ladder rung.

**Permutation null.** 200 draws per `(curve, N, seed)`, i.e. above the frozen
`>= 100`, in all 48 shared-null records and in all 336 per-cell `null_detail`
blocks per size run. Sharing is recorded explicitly (`shared: true` plus a
`shared_by` list naming each consuming label and the greedy's mask restriction).
Each typed pattern draws its own 200-draw same-typing null, so the amendment's
"per typing pattern" clause is met.

**Prior cells.** `prior_H016_qr_base` and `prior_H017_small_multiples` occupy
family slots supplied from `inputs/h100_session/h016_base_yield.json` through
the CTRL port-fidelity block. Neither appears in `cells[]` at any size, so
neither was re-run as a family cell. Their exact recomputations appear only
under `exploratory` / `exploratory_arms`, in a clearly separated section
(analysis.md §6). This is the amendment's rule, satisfied.

**Greedy train/held-out separation — the frozen invalidation rule.** Enforced
structurally, which is the strongest available form:

```677:683:experiments/EXP-FB3-001/implementation/fb3_core.py
def greedy_select(n_order: int, pool: np.ndarray, train_bits: int, b: int) -> dict:
    """H022 exact submodular-style greedy on TRAINING targets only.

    The held-out mask is not an argument of this function, which is the
    structural enforcement of the frozen stopping rule "any use of held-out
    targets during selection invalidates this arm".
    """
```

The selection loop's only target-space input is `avail = train_bits & ~r_bits`.
The candidate pool is drawn from the cell RNG and is independent of the split.
`held_mask` is first touched after selection returns, to compute `st_held`. I
found no path by which a held-out target influences a selection decision.

---

## 4. Independent recomputation (`pass`, exact agreement)

Script: `/tmp/val/independent.py`. It deliberately does **not** import
`fb3_core.py`. Everything is rewritten from the amendment prose:

* group order by `#E = p + 1 + sum_x legendre(x^3+ax+b, p)` with the Legendre
  symbol from Euler's criterion (`pow(v,(p-1)//2,p)`), not from a numpy QR table;
* point addition, double-and-add and the multiples table written from scratch;
* geometry constructors written from the frozen definitions;
* counting by **literal triple-nested enumeration of multisets `i <= j <= k`**
  in pure Python `Counter`, with no numpy, no Burnside identity and no FFT.

### Side-by-side, 2^14 curve 1 (`p=16381, a=4099, b=15559, N=16339, B=47`), seed 1

| cell | stat | validator | executor | agree |
|---|---|---|---|---|
| `high_bit_interval` | sum_counts | 18424 | 18424 | yes |
| | mean | 1.1276087887875634 | 1.1276087887875634 | yes |
| | coverage | 0.6801517840749128 | 0.6801517840749128 | yes |
| | concentration | 1.254666748271008 | 1.254666748271008 | yes |
| | max_count | 7 | 7 | yes |
| `small_height` | sum_counts | 18424 | 18424 | yes |
| | mean | 1.1276087887875634 | 1.1276087887875634 | yes |
| | coverage | 0.6806414101230186 | 0.6806414101230186 | yes |
| | concentration | 1.2524634310545322 | 1.2524634310545322 | yes |
| | max_count | 8 | 8 | yes |
| `coset_union` | sum_counts | 18424 | 18424 | yes |
| | mean | 1.1276087887875634 | 1.1276087887875634 | yes |
| | coverage | 0.6683395556643613 | 0.6683395556643613 | yes |
| | concentration | 1.3233368015178408 | 1.3233368015178408 | yes |
| | max_count | 9 | 9 | yes |
| `mixed_two_base` (primary) | sum_counts | 6900 | 6900 | yes |
| | mean | 0.42230246649121733 | 0.42230246649121733 | yes |
| | coverage | 0.33563865597649795 | 0.33563865597649795 | yes |
| | concentration | 0.196217638778383 | 0.196217638778383 | yes |
| | max_count | 4 | 4 | yes |
| `mixed_two_base__secondary_typing` | sum_counts | 6624 | 6624 | yes |
| | mean | 0.40541036783156864 | 0.40541036783156864 | yes |
| | coverage | 0.06218250810943142 | 0.06218250810943142 | yes |
| | concentration | 3.1233245608666382 | 3.1233245608666382 | yes |
| | max_count | 20 | 20 | yes |
| `small_multiples_H017` (exploratory) | sum_counts | 18424 | 18424 | yes |
| | mean | 1.1276087887875634 | 1.1276087887875634 | yes |
| | coverage | 0.008507252585837566 | 0.008507252585837566 | yes |
| | concentration | 237.09602790868473 | 237.09602790868473 | yes |
| | max_count | 288 | 288 | yes |

Plus, at the largest size and the most additively concentrated base — the
adversarial case — 2^18 curve 1 (`p=262253, N=261643, B=117`),
`small_multiples_H017`: sum_counts 273819 (= `C(119,3)`), mean
`1.0465366931276587`, coverage `0.001333878605580887`, concentration
`1334.7849703603765`, max_count 1741 — identical to the record.

Agreement is to the last float bit, not to a tolerance.

### Hard control `sum_r count(r)`

* untyped, on my own recomputations: `18424 = 47·48·49/6 = C(49,3)` and
  `273819 = C(119,3)`;
* typed, on my own recomputations: `6900 = B2·C(B1+1,2)` and
  `6624 = B1·C(B2+1,2)` for `(B1,B2) = (24,23)`;
* across the whole package: I recomputed the closed form from `B` and the typing
  sizes for **812** recorded totals (all cells, all asymmetric ladder rungs, all
  exploratory and symmetric-convention arms across the three size runs) and
  compared to the recorded `exact_total`. **0 mismatches.** For
  `asymmetric_sizing` this is literally the `B1*B2*B3` control the task names;
  for the mixed `(1,2)` pattern `B1*B2*B3` is undefined and the correct closed
  form is `B1*C(B2+1,2)`, which is what the executor's declared deviation D2
  says and what I verified.

### Two controls on my own method

* **Exact integer convolution.** I recomputed `high_bit_interval` a third way,
  by exact big-integer polynomial multiplication mod `x^N - 1` (Kronecker
  substitution with a `2^64` slot width), so there is no floating point
  anywhere. Identical count vector on all 16339 targets, and every Burnside
  numerator divisible by 6.
* **Generator invariance.** Rebuilding the curve with `G' = 3G` and redoing
  `high_bit_interval` gave bit-identical statistics. This matters: it shows the
  agreement is a property of the geometry and not an artifact of my having
  happened to pick the same generator the executor did. (It also confirms my
  smallest-x canonical generator `(1, 2554)` equals the recorded `G`.)

---

## 5. Curve validity (`pass`)

For 2^14 curve 1, all computed by my own code:

* `#E = 16339` by character sum — equal to the recorded `N`;
* `sympy.isprime(16339) = True`;
* Hasse interval `[16126.023, 16637.977]` contains it;
* `N·G = O` and `(N-1)·G = -G` by my own double-and-add;
* my table has exactly `(N-1)/2 = 8169` canonical x-coordinates;
* uniqueness: `N` prime, `ord(G) = N | #E`, and `#E <= p+1+2√p < 2N`, so
  `#E = N` is forced — the executor's recorded argument, which I checked
  numerically (`16339 > 16637.977/2`).

I also independently recomputed the group orders of all four recorded H016/H017
curves: `8329, 14143, 128857, 113621`, all matching the record, all prime, all
inside their Hasse intervals.

The other 11 generated curves rest on the executor's per-curve `verification`
block (`all_ok: true`, 12/12, including `x_pairing_ok`, `y_pairing_ok`,
`dlog_table_bijection` and 20 seeded double-and-add spot checks) plus the exact
reproduction of the run that builds them.

---

## 6. Port fidelity (`pass`)

Script: `/tmp/val/check6.py`, plus a re-run of `RUN-FB3-001-CTRL`.

Independently reproduced for all four recorded cells, not merely read:

| check | outcome |
|---|---|
| group order from recorded `(p,a,b)` by my character sum | `8329 / 14143 / 128857 / 113621` — exact match, all prime, all in Hasse |
| recorded `theory_mean_triples_per_target` vs my `C(B+2,3)/N` | absolute difference `0.0` on all four |
| recorded `qr_vs_random.ratio`, `sm_vs_random.ratio` | re-derived from recorded base means, difference `0.0` |
| recorded `counts` sum to recorded `total` and to `mean·800` | consistent, all four cells, all three bases |
| recorded `perm_null.mean_band_95` | equals my 2.5/97.5 percentiles of the recorded `null_means` |
| recorded `qr_emp_p_two_sided` = `0.40, 0.90, 0.44, 0.76` | exactly reproduced by `2·min(#{null≥obs}, #{null≤obs})/n` |
| H017 base `{1..B}` recomputed exactly by my own enumerator | agrees with the executor bit-for-bit on all four cells |

The executor's two fidelity findings hold up. The prior harness's own "theory
mean" *is* the conservation constant `C(B+2,3)/N` — I confirmed a `0.0`
difference in all four cells, so the identity was already implicit in the H016
record. And the prior sampled estimator really was unstable for concentrated
bases: the H017 geometry has an exact mean-yield ratio of exactly `1` (forced,
since it is a base of size `B`), while its recorded 800-target sampled ratio
ranges from `0.0000` to `1.7895` across the four recorded curves.

**Ordering.** Port fidelity is analysis.md §1; the family table is §3; the
verdict is §7. The handoff's "report the comparison before any family verdict"
constraint is met.

**Acknowledged limitations are in the artifacts, not only in a message.** All
three:

1. QR walk not bit-exactly replayable — analysis.md §1, execution-report
   deviation D4, implementation.md D4, and the machine-readable
   `qr_walk_reconstruction.bit_exact_replay_possible: false` with the reason
   ("the recorded conventions do not pin the walk's RNG stream, index function,
   or start point") in `RUN-FB3-001-CTRL/raw-result.json`;
2. prior cells recorded only at 2^14 and 2^17 — analysis.md §3 and §8,
   execution-report D3 and `censoring`, `cell_terminal_states.prior_cells`;
3. prior statistics sampled at 800 targets rather than exact — analysis.md §3
   ("recorded protocol: 800 sampled targets, not exact counting") and §8,
   execution-report `boundaries`, and `prior_cells.*.measurement_basis` in the
   family raw JSON.

---

## 7. Numerical safety (`pass`)

Script: `/tmp/val/check7.py`.

The important structural fact first: **no reported statistic depends on the
FFT.** `counts_untyped_m3_fft` is called at exactly one place in the battery
driver, inside `Auditor.cross_check`. Every published count comes from
`counts_untyped_m3` (integer `numpy.bincount` on integer modular sums) or the
integer typed counters. Rounding therefore cannot have flipped a reported count,
by construction rather than by margin.

The margin is nonetheless measured and recorded:

| where | max abs(value − round(value)) |
|---|---|
| 2^14 size run | `1.364e-12` (43 FFT checks, 0 failures) |
| 2^16 size run | `5.457e-12` (43 checks, 0 failures) |
| 2^18 size run | `3.638e-12` (43 checks, 0 failures) |
| CTRL block B | `5.457e-12` |
| CTRL block A | `3.411e-13` |
| campaign worst | `5.4569682106375694e-12` — matches the execution report exactly |

A single count flip needs an error `>= 0.5` in the Burnside numerator, so the
observed worst case is `9.16e10` times too small; the code aborts above `0.25`.

My own spot check at the adversarial worst case (2^18, `N = 261643`, base
`{1..117}` — the maximally concentrated base in the battery, `max_count = 1741`,
largest Burnside numerator `10446`): my own FFT route reproduced my own exact
enumeration on all 261643 targets, max deviation `3.638e-12`, all numerators
divisible by 6, i.e. `1.37e11` times below a flip.

---

## 8. Budget and honesty compliance (`pass`)

Budget against the handoff (`7200 s`, `6 GB`, `12 runs`), summed from the
manifests by me:

| run | wall (s) | peak (MB) |
|---|---|---|
| `RUN-FB3-001-CTRL` | 1.990 | 139.0 |
| `RUN-FB3-001-FAMILY` | 2.081 | 74.7 |
| `RUN-FB3-001-N14` | 6.629 | 87.8 |
| `RUN-FB3-001-N16` | 24.600 | 137.4 |
| `RUN-FB3-001-N18` | 140.110 | 230.6 |
| **total / max** | **175.41** | **230.6** |

Matches the reported `175.4 s` and `230.6 MB` / `0.23 GB` over 5 runs. Adding
the executor's declared `242.7 s` of auxiliary probes and reproduction checks
gives `418.1 s`, still 2.4% of the limit. The largest single run (140 s) is well
inside the frozen specification's `1800 s` per-run cap, and 5 runs is inside
both the handoff's 12 and the specification's 96. No run was truncated by a
limit; the only censoring is inherited (prior cells at 2^16/2^18).

`result.certificate.kind: none` in all five manifests, each with an explicit
reason rather than a blank.

Honesty scan over `experiments/EXP-FB3-001/**` for speedup / attack / break /
cryptanalytic-improvement language returns **only negations** — the sentence "no
cost, speedup, or attack claim is derived from their availability" appears in
the amendment, `implementation.md`, `conservation.md`, `analysis.md` and all
five manifests. Specifically present:

* the "discrete logs known by construction, **for measurement only**" caveat —
  analysis.md, conservation.md §4, implementation.md, execution-report
  `boundaries`, and every manifest's `honesty_notes`;
* the yield-versus-solving-cost boundary — analysis.md ("What was not
  measured", §8), conservation.md §4, execution-report `boundaries`, and every
  manifest;
* the extra caveat that the greedy base is *selected* with the full discrete-log
  table and so is unavailable to an attacker, making that arm an oracle-aided
  upper bound rather than an attack ingredient;
* claim tier `toy` with its field-size basis, and the negative-result phrasing
  from `docs/evidence-and-reproducibility.md` verbatim.

No artifact asserts a status transition. analysis.md §7 and
`execution_report.verdict_against_frozen_criteria.executor_position` both defer
to the Coordinator.

---

## 9. Reproducibility (`pass`) — exactly what I observed

I re-ran two recorded commands verbatim, redirecting `--out` to `/tmp` so no
committed artifact could be touched.

**(1) `RUN-FB3-001-N14`.**

```bash
cd experiments/EXP-FB3-001/implementation
python3 run_battery.py --bits 14 --out /tmp/val/repro/N14-revalidate.json --null-draws 200
```

Exit 0 in 6.3 s. A full recursive JSON leaf diff against the recorded
`raw-result.json` gives **20 differing leaves and 0 substantive differences**:

* 16 × `cells[i].extra.selection_seconds` (greedy selection wall clock);
* `peak_memory_mb` (`87.83984375` → `87.89453125`);
* `timing.started_at`, `timing.finished_at`, `timing.wall_clock_seconds`
  (`6.325408220291138` → `6.252686023712158`).

Every measured statistic is identical, including all 200 null draws in each of
the 16 shared-null records, every curve block and every control counter. The
recorded `stdout.log` differs from mine in 8 lines: the start timestamp, one
per-replicate elapsed-time line, the output path, and the final wall/peak line.

**(2) `RUN-FB3-001-CTRL`.**

```bash
cd experiments/EXP-FB3-001/implementation
python3 run_controls.py --out /tmp/val/repro/CTRL-revalidate.json
```

Exit 0 in 1.7 s. **4 differing leaves**, all timing/memory
(`peak_memory_mb`, two timestamps, `wall_clock_seconds`). All four control
blocks return `pass` and all four port-fidelity cells return 17/17.

I did **not** re-run N16, N18 or FAMILY. The executor's N18 reproduction claim
is therefore unverified by me; N14 and CTRL are verified.

**What "at the recorded revision" can mean here (finding F3).** Every manifest
records `code.commit = e18c9bc` with `dirty_tree: true`, and
`environment.json` shows the dirty tree was exactly four **untracked** new
directories:

```text
?? experiments/EXP-FB3-001/implementation/
?? experiments/EXP-FB3-001/runs/
?? experiments/EXP-XEDN-002/implementation/
?? experiments/EXP-XEDN-002/runs/
```

So no *tracked* file differed from `e18c9bc`, but the implementation did not
exist at `e18c9bc` either — you cannot check it out and re-run. The chain still
closes, and this is why my hash check in §2 matters: the untracked
implementation became durable at `68e375f`, and the working-tree files I actually
ran hash to the receipt's recorded values, so the code I ran is byte-identical to
the code that produced the records. The executor discloses this in
`execution_report.implementation_commit_note`. **Downstream records should cite
`68e375f` as the reproducible revision, not `e18c9bc`.**

---

## 10. Self-consistency (`pass`) — 93 published values, 1 labelling mismatch

Script: `/tmp/val/check10.py`. Well above the 10 required spot checks.

Verified exactly against `RUN-FB3-001-FAMILY/raw-result.json` and the size runs:

* all 18 primary mean-yield ratios of analysis.md §3 (e.g. `mixed_two_base`
  `0.372639 / 0.370000 / 0.374919` vs raw `0.372638949 / 0.370000000 /
  0.374919198`; `greedy_optimized` `0.955409 / 0.971719 / 0.980631` vs raw
  `0.955408892 / 0.971719077 / 0.980630978`; the three untyped geometries
  exactly `1.000000` at all sizes);
* all six `p_holm` values, at all three sizes (`1.000` ×3 and `0.0398` ×3);
* all six family-wise (99.375%) CIs at 2^18, including
  `greedy_optimized [0.979477, 0.981536]` and the three zero-width `[1, 1]`;
* all six growth slopes (`0.0`, `0.0`, `0.0`, `+0.000570062`, `+0.001947619`,
  `+0.006305522`);
* the absolute-scale line — exact mean `1.1146 / 1.0755 / 1.0436` and
  matched-random coverage `0.6734 / 0.6594 / 0.6480`;
* all 18 coverage ratios of §4, including the two above-1 entries
  `coset_union 1.00121` and `greedy_optimized 1.00299` at 2^18;
* all 18 exploratory values of §6 and conservation.md §2 (mean, coverage and
  concentration ratios for `qr_walk_H016` and `small_multiples_H017` at three
  sizes) plus the `n = 12 / 16 / 16` record counts;
* control counts: `67784 = 22592 + 22596 + 22596` closed-form checks, 46
  brute-force cases, 148 assertions, 43 recounts per size run, 288
  pre-registered measured records, `144 / 336 / 144` cells for consequences
  (i)/(iii)/(iv), consequence (i) max deviation exactly `0.0`;
* resources `175.4 s / 230.6 MB / 5 runs`.

I also **re-derived the Holm-Bonferroni arithmetic myself** from the raw per-cell
p-values:

| size | family size | my rejections | executor's rejections |
|---|---|---|---|
| 2^14 | 8 | `asymmetric_sizing, greedy_optimized, mixed_two_base, prior_H017_small_multiples` | identical |
| 2^16 | 8 | `asymmetric_sizing, greedy_optimized, mixed_two_base` | identical |
| 2^18 | 8 | `asymmetric_sizing, greedy_optimized, mixed_two_base` | identical |

My adjusted p-values match the executor's to within `1e-15`. The censored prior
slots carry `p_raw: null` and still occupy a slot, so the family size is 8 at
every size as frozen.

**The one mismatch (finding F1).** conservation.md §2(i) reports the "observed
exact mean" series as `1.1276 -> 1.0755 -> 1.0436`. The 2^16 and 2^18 values are
the 16-replicate means, but `1.1276` is the single **curve-1** value at 2^14; the
2^14 replicate mean is `1.1146`, which is what analysis.md §3 publishes.

| size | conservation.md | 16-replicate mean | curve-1 value |
|---|---|---|---|
| 2^14 | `1.1276` | `1.114639` | `1.127609` |
| 2^16 | `1.0755` | `1.075475` | `1.071990` |
| 2^18 | `1.0436` | `1.043573` | `1.046537` |

Both numbers are in the raw data, so nothing is fabricated; the same labelled
quantity simply has two values across two artifacts. It has no effect on any
verdict, because consequence (i) is checked **per cell**, where the maximum
deviation of the exact mean from `C(B+2,3)/N` is exactly `0.0` over 144 untyped
cells. The 2^14 spread (`1.0684` to `1.1336`) is entirely the integer ceiling in
`B = ceil((6N)^(1/3))` across four curves with different `N`, which
conservation.md itself explains in the following sentence. Per AGENTS.md rule 4
this should be corrected by a superseding record if the Coordinator cites the
series, not by editing conservation.md.

---

## 11. Deviations and findings not declared by the executor

### V1 — matched-random draws exclude the identity (`minor`)

The frozen amendment (AMD-1) and every run's
`counting_convention.matched_random` string say the matched-random base is
"B distinct uniform logs in **[0, N)**". The implementation draws from
`[1, N)`:

```739:753:experiments/EXP-FB3-001/implementation/fb3_core.py
def distinct_logs(rng, n_order: int, k: int) -> np.ndarray:
    """k distinct uniform logs in [1, N) -- the frozen matched-random convention.
```

Excluding `0` (the identity) is the mathematically correct reading — a factor
base is a set of distinct *nonzero* elements, which is exactly how
conservation.md §1 states it, and structured bases never contain `0` either, so
the comparison is like-for-like. But the frozen text and the machine-readable
convention string are not literally what was executed, and the docstring
contradicts the JSON.

Bounded impact: the conservation identity and the exact mean depend only on
`|D|` and `N`, so they are untouched. The probability that a genuine `[0, N)`
draw of `B` distinct logs would have contained `0` is `B/N = 0.0029` at 2^14 and
`0.00045` at 2^18, so at most the null *coverage* estimate moves at `O(1/N)`.
No conclusion can turn on it. Recorded so the Coordinator can decide whether to
correct the convention string in a superseding record.

### F2 — the family p-value aggregation rule is not in FROZEN (`minor`)

The per-cell p-value fed to Holm is the **mean over the 16 replicates** of the
two-sided permutation p-value. That choice lives only in a comment in
`run_family.py` (asserted as "declared before execution") and is not in the
amendment, not in the `FROZEN` block, and not among the D6 pinnings the executor
lists — even though D6 does list "p-value convention", which covers only the
per-cell `(r+1)/(n+1)` rule.

Impact is negligible and the direction is conservative: averaging p-values is
not a valid combining function in general, but under the null the mean of 16
independent uniforms concentrates near `0.5`, which makes rejection *harder*.
In this data the per-replicate p-values are degenerate — exactly `1.0` for the
three untyped cells (point-mass null) and exactly the `1/201 = 0.004975` floor
for the three rejected cells — so the mean equals each individual value and the
aggregation has no effect on the reported family. The executor also reports the
per-cell min and max, so the choice is auditable. A Reviewer citing
Holm-adjusted significance should name the aggregation rule explicitly.

### F4 — framing correction in the executor's favour (`none`)

A reader of implementation.md item 3, or of the task framing, might conclude the
reported counts come from a rounded FFT. They do not (see §7). The
numerical-safety question is answered structurally, not statistically.

### F5 — accounting nit (`none`)

implementation.md and the execution report say the reproduction differed in "17
wall-clock fields per run". A full leaf diff gives 20 leaves (16
`selection_seconds`, three timing fields, `peak_memory_mb`). All 20 are
wall-clock, timestamp or peak-RSS fields, so the substantive claim (0
measurement differences) stands.

### F6 — a defect in *my* control, recorded for completeness (`none`)

Cross-checking the two height routines, I found one `x` where my
continued-fraction implementation disagreed with brute enumeration: `x = 0`,
where `h(0) = 1` legitimately (`0 = 0/1`) but my guard returned `p`. The
executor's `height_cf` handles `x = 0` correctly, which is why its control
reports 0 disagreements over all 16381 values. The defect was mine.

---

## 12. Failure-mode discipline

No crash, timeout, or memory problem occurred in any Validator check. Every
check reached a terminal verdict from data. Had one failed on infrastructure I
would have marked that check `failed_infrastructure` and said so explicitly; per
AGENTS.md rule 5 such a failure is never evidence about the mathematics.

My own budget: `~95 s` of compute, `~88 MB` peak, **2** reproduction runs
(N14 battery, CTRL controls) against a limit of `3600 s / 4 GB / 3 runs`. My
recomputation and audit scripts are Validator computations, not experiment runs.

---

## 13. What I did not check

* N16, N18 and FAMILY were not re-run; the executor's N18 reproduction claim is
  unverified by me.
* 1 of 12 generated curves was fully verified by hand (plus all 4 recorded prior
  curves); the other 11 rest on the executor's recorded verification block and on
  exact reproduction.
* 7 cells were recomputed from first principles. Cells whose construction depends
  on the numpy RNG stream — the 9600 matched-random null bases, the greedy pools
  and selections, the asymmetric sub-base elements — were **not** rebuilt by an
  independent method. They were checked by exact reproduction of the recorded
  command and by the closed-form total control, which is weaker than a
  from-scratch recount.
* I did not audit the bootstrap CIs or the growth-slope resampling beyond
  confirming that published values match the raw JSON and that the reported
  zero-width CIs are consistent with degenerate inputs.
* I read conservation.md §1 as a correct elementary proof and checked that its
  four consequences are labelled consistently with the data, but a
  derivation-level argument is not machine-checked and I did not formalise it.
* **Interpretation is out of scope.** Whether the frozen success or
  falsification criteria are met, whether the "alive direction" operationalisation
  in analysis.md §7 is the right reading of the frozen text, whether a primary
  metric that the pre-registered analytic arm proves *cannot* show a matched-size
  geometry effect can support a scoped KILL, and what any of this means for
  H-FB3-001 or the F3 family — all belong to the Reviewer, the Red Team and the
  Coordinator. I take no position.
* I validated only the committed snapshot `68e375f` as it appears at HEAD
  `ae5503d`. I made no commit, staged nothing, and wrote only the two files in my
  assigned write scope.

---

## 14. How to redo these checks

```bash
# 1. artifact completeness + schema
python3 /tmp/val/check1.py
python3 tools/validate_ledger.py                       # 154 pre-existing errors, 0 FB3
git archive 123fb746 | tar -x -C /tmp/mb && (cd /tmp/mb && python3 tools/validate_ledger.py)

# 2. snapshot receipt integrity
python3 /tmp/val/check2.py
python3 tools/research_dispatch.py \
  coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/dispatch_queue.json \
  --output /tmp/plan.json --report /tmp/plan.md

# 3. protocol conformance
python3 /tmp/val/check3.py

# 4/5. independent recomputation + curve validity   (~77 s)
python3 /tmp/val/independent.py

# 6. port fidelity, recomputed
python3 /tmp/val/check6.py

# 7. numerical safety
python3 /tmp/val/check7.py

# 9. reproduction (writes only to /tmp)
cd experiments/EXP-FB3-001/implementation
python3 run_battery.py --bits 14 --out /tmp/val/repro/N14-revalidate.json --null-draws 200
python3 run_controls.py --out /tmp/val/repro/CTRL-revalidate.json
python3 /tmp/val/check9.py

# 10 + extras: self-consistency, 812 closed-form totals, Holm re-derivation
python3 /tmp/val/check10.py
python3 /tmp/val/check_extra.py
```

The scripts live in `/tmp/val/` and are self-contained (Python 3.12.3, numpy
2.4.4, sympy 1.14.0); `check6.py` and `check7.py` import `independent.py` for my
own curve and counting layer, never `fb3_core.py`.
