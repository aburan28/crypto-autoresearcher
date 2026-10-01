# J-1 validation report — RUN-SEMBIN-b6eb9f

- **Task**: `TASK-20260921-f2d82f` (validator, `review-adversarial`)
- **Round**: `REVIEW-SEMBIN-20260921-457504`, joint **J-1 only**
- **Run under review**: `experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f`
- **Authority checked against**: `experiments/EXP-SEMBIN-c2c312/specification.yaml` v1
  (`controls`, `invalidation_rules`, `stopping_rules`, `required_artifacts`)
- **Runs launched**: 0. Every number below is recomputed from committed records
  with exact integer / GF(2) arithmetic, or is a sha256 of a committed file.

## Verdicts

| | |
|---|---|
| **Run validity (this joint)** | **`incomplete`** |
| **J-1 joint verdict** | **`breaks`** — narrowly, and not where the run's numbers are |
| What breaks | The **byte-identity control was reframed**, from "both instruments' recorded input hashes compared, a mismatch invalidates that cell" to "equal by construction". As shipped the check has **zero detection power**. Separately, 4 of 11 declared `code_sha256` values do not match this snapshot, so the instrument bytes that produced the run are **not recoverable here** — and `dirty: true` made that hash block the only binding. |
| What holds | Every reported quantity reproduces **exactly** from the raw records. The duplicate audit finds **zero discordant pairs**. The structural-shape and known-false controls verify independently. No contract invalidation rule fires. I performed the missing byte-identity comparison myself and it **passes on all 139 retained instances**. |

`completed_valid` is not falsified, but it is **broader than what the package
established**. Its `validity.reason` asserts "byte identity holds on every
instance"; nothing in the run checked that, and the assertion is true only
because I checked it here. The same reason omits the matched null entirely.

## (a) The duplicate-record audit — the discordant list is EMPTY, and computed

Source: the five `*/cells/results.jsonl` files, grouped by `(instance_id, instrument)`.

```
raw records                                   314
distinct (instance_id, instrument) keys        270
keys with more than one record                 30
extra records over those keys                  44
distinct instance_ids                         126
```

**DISCORDANT PAIRS: 0.** No duplicated pair disagrees on `d_F4_semaev`,
`d_F4_naive`, `closure_D`, `D_macaulay_rank_statistic`, or any per-degree
profile (F4 `rounds` compared on `(deg, pairs, sel, rows, cols, new, zero)`;
closure `per_D` on `(D, rank, ncols, verdict, status, basis_lm_sha256,
max_rows_seen, iterations)`; Macaulay `per_D` on `(D, rank, cols, rows, status,
deficit_vs_semiregular, sr_pred_rank)`). This is a computed result, not an
assumption.

The 30 duplicated keys decompose as:

| class | keys | what it is |
|---|---|---|
| ≥2 records each carrying a measured value, **all agreeing** | 14 | genuine repeat measurements |
| at most one record carrying a value | 16 | a re-attempt after an `unreached_*` placeholder |

Of the 14 genuine repeats: 3 are the known-false control measured **five times**
(`workerA:1,4,7,10,19` F4; `:2,5,8,11,20` closure; `:3,6,9,12,21` Macaulay), and
11 are `macaulay_single_level_DREG` repeats — 10 at (19,3,3,7) in workerB and 1
at (17,3,3,7) in workerC. All 11 agree bit-for-bit including timing-independent
fields.

**The disclosed workerB double-run is real, and it is cleaner than the
disclosure implies.** `workerB/cells/progress.log` shows pid 9160 starting
08:08:21Z and pid 9336 at 08:30:38Z, both with
`--f4-skip-cells 19:3:3:7,21:3:3:7`. Their 19 duplicated keys split into 9 F4
keys where **both records are `unreached_declared` placeholders** — not
measurements at all — and 10 Macaulay keys which are real duplicated
measurements and agree exactly. So "first completed record wins" never had to
break a tie between two disagreeing measurements: on this data the rule is a
no-op with respect to every reported value.

Two things the disclosure does not say:

1. **11 of the 30 duplicated keys are outside workerB.** `workerA` contributes 3
   (the known-false triple, from its 7 invocations), `workerC` 1, and 7 span
   workers (the heavy / heavy_closure re-attempts, which are by design —
   `--remeasure-unreached`, `--closure-only-missing`).
2. **One key looks like nondeterminism and is not.**
   `sem_n19_m3_t3_k7_low_B_equ_s20260913001_d0` / `f4_trace_msolve` has
   `heavy:1` = `unreached_memory_cap` (16 rounds, peak RSS 6.80 GB) and
   `heavy:3` = `completed` (20 rounds, 6.03→7.08 GB, `d_F4_semaev = 4`), same
   `system_sha256 9ab973072786…`. `heavy/cells/progress.log` resolves it: pid
   962 ran that cell at `--mem-cap 8.0`, pid 5726 at `--mem-cap 13.0`. The
   instrument's **value** is deterministic; only its **completion** is
   cap-dependent. This belongs in the resource record, not in the
   nondeterminism column.

I independently re-implemented the resolution rule ("first record per key;
replace if the old is not completed and the new is; for closure, replace if the
old `closure_D` is null and the new is not") and it reproduces the manifest
exactly — see (e).

**Instrument identity.** The contract's own control is separate from the above,
because the repeats carry a different `instance_id` (`…_repeat`) and so were not
grouped by the audit. Compared field by field, excluding `wall_s`, `cpu_s`,
`real_s`, `peak_rss_bytes`, `stdout_sha256`, `command`:

- `sem_n17_m3_t3_k6_low_B_equ_s20260913001_d0` vs `…_repeat`: all three
  instruments identical in **every** remaining field except the `group` label.
  The F4 15-round per-degree profile is exactly equal (`workerA:22` vs `:25`).
  **Control passes, verified directly rather than from the `f4_rounds_equal`
  flag.**
- `sem_n13_m4_t4_k4_low_B_equ_s20260913001_d0` vs `…_repeat`: closure and
  Macaulay identical; the **F4 half is not a comparison** — the base's completed
  record is `heavy:2` and the "repeat" is `workerA:16 unreached_declared`. This
  matches `NOTES` deviation 7 and the manifest lists only the (17,3,3,6) entry,
  so it is accurately reported. But `result.identity_repeat_instances: 2`
  standing beside a single `controls.instrument_identity` entry reads as two
  comparisons when there is one.

So **F4 instrument identity rests on one instance** as a declared control — and
on 14 more (instance, instrument) keys once the concurrency accident is counted,
all concordant. The accident supplied free replication and it is clean.

## (b) Byte identity — ASSERTED, not compared; I performed the comparison

**No per-record comparison exists in the raw data, and none can.** Every one of
the 314 records has `input_sha256 == system_sha256`, with 0 exceptions and 0
records missing either field. That is not a passing check; it is one value
written into two field names. `run_cells.py:92` computes
`sha = sha256(boolsys.canonical_bytes(system))`, line 97 puts it in `base` as
`system_sha256`, and lines 120 / 146 / 161 pass **the same variable** as
`input_sha256` into the F4, closure and Macaulay records. The fields cannot
differ, so the contract's "a mismatch invalidates that cell" can never fire.

A comparison of the two instruments' hashes does exist in code, at
`summarize.py:68` (`cl["input_sha256"] != f4["input_sha256"]`), but it guards
the *post-hoc* closure re-evaluation rather than cell validity, it runs after
both instruments, and it compares the same two provably-equal fields. It is
vacuous for the same reason.

**How it could fail silently.** The two instruments do not in fact consume the
same bytes, and the recorded hash cannot see the difference:

- the closure and Macaulay instruments receive `eqs = system["equations"]`, the
  in-memory list of monomial masks (`run_cells.py:138, 159`) — identity by
  reference, which is *stronger* than hash equality;
- msolve receives `instances/<id>.ms`, a **text translation** produced by
  `boolsys.write_msolve` (`run_cells.py:96`), with **N extra generators
  `v^2+v` appended**. Its hash is recorded separately as
  `msolve_input_sha256`, and nothing compares it to `system_sha256`.

So any defect in that translation layer changes what msolve solves while
`system_sha256` stays fixed on both records. Three concrete paths:
`write_msolve` **silently drops identically-zero equations** (`boolsys.py:346`
`if not e: continue`) while the closure still receives them, so the two
instruments would solve systems with different equation counts; `mono_str`
indexes `names[j]` over `range(mask.bit_length())`, so a mis-shifted mask names
wrong variables; and the field-equation block itself is an asymmetry that the
hash is blind to by construction.

**I ran the missing check.** With an independent parser (my own, importing no
producer code) over all 139 retained `<id>.ms` files, reconstructing each
polynomial as a set of monomial masks from the variable line and comparing
against the canonical `system.equations` in the sibling `<id>.json`:

```
.ms files parsed and compared                                      139
core polynomial systems agreeing EXACTLY with the canonical system 139
field-equation block != exactly one v^2+v per variable               0
characteristic line != 2                                             0
disagreements or parse failures                                      0
```

I also re-derived `boolsys.canonical_bytes` from the retained
`<id>.json`'s `system` field and re-hashed: **136 of 136** files hash to the
`system_sha256` their records carry (139 of 139 against the hash embedded in the
file). Note that the retained file is *not* the canonical bytes — it wraps them
in `{"meta", "system", "system_sha256"}` (`run_cells.py:93-94`), so hashing the
file directly mismatches every record. A later reader must re-canonicalise, and
nothing in the package says so.

No instance in this run has an identically-zero equation, so the
`write_msolve` drop path was never exercised here.

**Verdict:** `satisfied_differently`. Byte identity holds and I verified it on
every retained artifact; the run's own evidence for it was an assertion with no
detection power, and the substantive comparison was performed for the first time
in this validation.

## (c) How much rests on one instance at (13,4,4,4)

The baseline is the control the contract says "gives any later disagreement
meaning". At (13,4,4,4) it rests on **one instance**:

- `sem_n13_m4_t4_k4_low_B_equ_s20260913001_d0` — subspace
  `low_degree_polynomial`, `B_equals_1`, seed `20260913001`, draw 0. Nothing else.
- `d_F4_semaev = 4` from a **single record**, `heavy:2` (pid 5556,
  `--mem-cap 13`, 684.9 s, peak RSS 6.03 GB, 20 rounds, quotient dimension 36).
  `workerA:13` and `workerA:16` are both `unreached_declared`.
- `closure_D = 4` from a **single record**, `workerA:14`
  (`per_D = [(3, 1796, 12384, undetermined), (4, 124278, 124314, sufficient)]`),
  plus `workerA:17`, its byte-identical identity repeat.

Weight, stated plainly. The contract asks 20 draws per cell across 2 subspace
variants and 2 B modes; the executor's disclosed reduction is 5 draws per
(cell, subspace, B), i.e. 20 instances per cell. (13,4,4,4) has **1**. Both
`random_k_dimensional` and `B_random` are **entirely absent** at that cell, so
the calibration there is a single draw of a single variant. The second
reproduction cell is materially stronger — (17,3,3,6) has 6 instances, 6 of 6
F4 completions all reporting 4, and 2 closures both 4 — but
`random_k_dimensional` is absent there too. `stopping_rules[0]` (both
instruments must return 4 at both reproduction cells, else every later cell is
invalidated) is **satisfied**; it is satisfied at (13,4,4,4) on n = 1, and n = 1
admits no variance estimate whatever. I record the fact and its weight and do
not decide what it invalidates.

## (d) The other three invalidation rules

**Structural shape — `satisfied_as_specified`, verified independently.** I did
not read `structure.valid`; I recomputed from the retained canonical systems
(`n`, `m`, `t`, `k` taken from the instance id, everything else from the masks).
All **125** chained instance files pass: equation count `= n(t-1)`, variable
count `= n(t-2) + kt` and `= len(var_names)`, maximum algebraic degree `= 3`, no
identically-zero equation, no monomial mask referencing a bit ≥ N. **0
failures.**

```
(12,6,6,2) 16 files  N=60 (exp 60)  eqs=60 (exp 60)  maxdeg=3
(13,4,4,4)  2 files  N=42 (exp 42)  eqs=39 (exp 39)  maxdeg=3
(15,5,3,3) 20 files  N=24 (exp 24)  eqs=30 (exp 30)  maxdeg=3
(17,3,3,6)  7 files  N=35 (exp 35)  eqs=34 (exp 34)  maxdeg=3
(17,3,3,7) 20 files  N=38 (exp 38)  eqs=34 (exp 34)  maxdeg=3
(17,3,3,8) 20 files  N=41 (exp 41)  eqs=34 (exp 34)  maxdeg=3
(19,3,3,7) 20 files  N=40 (exp 40)  eqs=38 (exp 38)  maxdeg=3
(21,3,3,7) 20 files  N=42 (exp 42)  eqs=42 (exp 42)  maxdeg=3
```

Gap worth naming: 24 records carry no `structure` block — 15 known-false, 3
matched-null (the rule is about the chained family, so this is proper) and **6
chained records**, which are exactly the three instruments × two `…_repeat`
instances. The run's own structural check therefore never ran on the
identity-repeat copies. My recomputation above covers them, and they pass.

**Known-false returning 2 from both instruments — `satisfied_as_specified`, and
I verified the object itself.** From
`workerA/cells/instances/ctrl_known_false_N35.json`: 69 equations in 35
variables, maximum algebraic degree 2, of which **35 are of degree exactly 1**.
Evaluating the retained `meta.planted_point` over GF(2) against every equation:
**0 equations fail to vanish** — the planted point is an exact common root. Both
instruments return 2, five times each, identically: F4
`d_F4_semaev = d_F4_naive = 2` (`f4_step_count = 1`); closure `closure_D = 2`,
`D_macaulay_rank_statistic = 2`, `per_D = [(2, 630, 631, sufficient)]` with
`verdict_basis = "standard monomials = |V(I)| = 1"` and
`solutions_source = "brute force over 0 free variables"` — self-contained, not
taken from F4. Contract invalidation rule 2 does **not** fire.

Limitation on the control's strength: 35 degree-1 generators in 35 variables
pin the point by the linear part alone, so a verdict of 2 is reachable without
any quadratic reasoning. The control does establish what the contract wanted —
that neither instrument mechanically reports 4 from the Macaulay construction's
shape — but it is an easy known-false object, and it is the only one.

**Invalid inputs rejected before measurement — `satisfied_as_specified`.**
`boolsys.py` matches its declared `code_sha256` (`55d0063a0bb6`), so this is the
code that ran. Lines 172 and 174 raise inside `generate()`'s validation, before
any system is constructed:
`invalid input: t=1; t = 1 has no equation (rejected by design)` and
`invalid input: k=0; empty subspace (rejected by design)`.
`run_cells.py:225-231` calls `generate` on (17,3,1,6) and (17,3,3,0), recording
`"rejected: {exc}"` or the literal string `"NOT REJECTED"`.
`workerA/cells/controls.json` holds both rejection strings, matching the source
f-strings **character for character**. No measurement record exists for either.

**Matched null — `unevaluable`, and not mine.** One line as instructed: the
null's F4 hit the 3600 s wall cap (`workerA:28`, 3600.2 s) and its closure
returned `undetermined` at D = 3 and 4 with D = 5 above the column cap, so no
null separation exists and contract invalidation rule 3 cannot be evaluated from
the records. Referred to the composition.

## (e) The arithmetic — 126 / 314 / 44 are mutually consistent

`314 − 44 = 270`, which is exactly the number of distinct
`(instance_id, instrument)` keys I counted. All three numbers reproduce, and
`summary.json` records the same three (`n_instances 126`, `n_records_raw 314`,
`duplicate_records_resolved 44`).

The 126 decompose exactly:

```
122  chained instances          (15 + 1 + 20 + 6 + 20 + 20 + 20 + 20 by cell,
                                 matching the task-report's table row for row)
  2  chained "_repeat" copies   (instrument-identity control)
  1  known-false control        ctrl_known_false_N35
  1  matched null               null_n17_m3_t3_k6_low_B_equ_s20260913001_d0
---
126
```

Every headline number recomputes from the raw records under my own
reimplementation of the resolution rule:

| quantity | manifest / report | recomputed |
|---|---|---|
| structured instances | 122 | **122** |
| F4 completed | 43 | **43** |
| F4 unreached | 79 | **79** |
| closure measured | 14 | **14** |
| closure decided | 12 | **12** |
| instances with both | 9 | **9** |
| `closure_D − d_F4` | 0 on 9 | **{0: 9}** |

`results-table.json` agrees with the raw records on `d_F4_semaev`,
`d_F4_naive` and `closure_D` for **all 126** instances — 0 discrepancies. Only
`quotient_dimension` differs, on 7 instances, always `null → value`, which is
the disclosed `summarize.py` post-hoc re-read of the retained `.gb`
(`quotient_dimension_source: "reduced basis file (re-read)"`). No value is
overwritten with a different value anywhere.

## Infrastructure outcomes are recorded as resource facts, not measurements

Checked, because the run leans on it. **0** F4 records with a status other than
`completed` carry a non-null `d_F4_semaev` or `d_F4_naive`. Five carry only
`d_F4_partial_max_deg_seen = 4` alongside the round count reached before the cap
— `workerA:28` (null, wall cap, 3 rounds), `workerB:158` (memory cap, 29),
`workerC:1` (12), `heavy:1` (16), `heavy:5` (19). That field is the maximal step
degree observed before the cap, a resource fact, and the manifest reports it
under `partial_max_step_degree_seen_over_unreached` rather than as a degree. The
handling is correct. The only risk is the field's name, which a hurried reader
could mistake for a d_F4; I draw no inference from any of these records and
nothing downstream should.

## Defects found and not fixed

Nothing was repaired. In descending order of consequence:

1. **Declared code identity is broken for 4 of 11 modules, and `dirty: true`
   made it load-bearing.** Hashing `experiments/EXP-SEMBIN-c2c312/code/` against
   `manifest.code_sha256`: `boolsys.py`, `closure_cert.py`, `closure.c`,
   `gf2_echelon.c`, `run_wrapper.py` **match**; `f4_trace.py` (declared
   `0aea327a6a4b`, actual `dd92f466c5f4`), `run_cells.py` (`9431c6318f32` →
   `efc97bd2c327`), `summarize.py` (`06d7f30cd903` → `1941923c9e5a`) and
   `make_manifest.py` (`c66eaad2bc59` → `f7472df8f85b`) **do not**;
   `libclosure.so` and `libgf2ech.so` are absent (build products, so expected —
   but the compiled instrument is then unhashable). The run records
   `commit f2a88e4e…` with `dirty: true` on branch
   `claude/ecdlp-index-calculus-grobner-xwr62t`, so the commit never held the
   code that ran either and `code_sha256` was the only binding. **Consequence
   for this report**: my reading of the byte-identity mechanism and the
   duplicate-resolution rule describes the *current* `run_cells.py` /
   `summarize.py`, not necessarily the bytes that produced the run. Both
   conclusions survive that, because they also follow from the data alone — the
   hash equality holds on 314/314 records and the manifest itself says "equal by
   construction", and my independent resolution reproduces every manifest count.
   The generator and the closure instrument *are* byte-verified, which is why
   the known-false and closure-verdict findings above do not carry this caveat.
   Remedy is cheap and is not mine: recover the four blobs from the run's own
   branch history (I was instructed to run no `git` command, so I did not
   attempt it) or retain a copy of the code inside the run package.
2. **The manifest's commands and timings cover only the last invocation per
   directory.** The progress logs record **22 invocations** — workerA 7,
   workerB 4, workerC 2, heavy 6, heavy_closure 3 — with materially different
   arguments: `--mem-cap` 3 / 5 / 7 / 8 / 13, `--wall-cap` 3600 / 5400, varying
   `--cells`, `--f4-skip-cells`, `--no-closure`, `--closure-mem-cap`. The
   manifest lists **5** commands and each worker's `command.txt` holds one. The
   `unreached_memory_cap` record at `heavy:1` was produced under `--mem-cap 8`,
   a value appearing nowhere in the manifest or any `command.txt`. Likewise
   `timing.workers.heavy` (14:22:05 → 14:53:45, 1900.0 s) is pid 6431 alone; the
   heavy pass began at **10:49:23**. All of it is recoverable from
   `*/cells/progress.log`, so this is incompleteness in the manifest, not loss —
   but `required_artifacts` asks for "the exact command", and the exact commands
   are 22.
3. **`protocol_deviations: []` and `unexpected_observations: []` in the
   manifest**, while `NOTES-deviations-and-limitations.md` documents seven
   deviations and three unexpected events (the workerA OOM kill at 9.7 GB, the
   double-pid append, the deliberate stop at 1 GB free). A tool or reader
   consuming `manifest.yaml` alone concludes there were none. The prose
   satisfies rule 8's substance; the structured fields contradict it.
4. **A quantity used in the run's control narrative has no record.** Both
   `NOTES` and `task-report.md` state that at (13,4,4,4) "the null reached
   12779". That figure exists only in
   `workerA/cells/progress.log` @ `2026-09-17T10:07:57Z`
   (`null_n13_m4_t4_k4_low_B_equ_s20260913001_d0 closure D=4: completed
   verdict=undetermined rank=12779 ncols=124314`). The instance has retained
   `.json` and `.ms` and **no record in any `results.jsonl`**, so it appears in
   neither `results-table.json` nor `summary.json`, and
   `result.matched_null_instances: 1` does not count it. It is traceable, not
   fabricated — but a control figure carried only by a human-readable log is not
   machine-checkable evidence.
5. **Three generated systems have retained artifacts and no record**:
   `null_n13_m4_t4_k4_low_B_equ_s20260913001_d0`,
   `null_n17_m3_t3_k6_low_B_ran_s20260913001_d0` (both matched nulls, so the run
   generated three nulls and recorded one) and
   `sem_n12_m6_t6_k2_ran_B_ran_s20260913001_d0`. The last has a **zero-byte
   `.gb`**, so msolve was launched and killed before writing anything; no
   completed measurement was discarded. It is the draw in flight when workerB
   was stopped, and it is why (12,6,6,2) has 15 instances rather than 20 — its
   whole `random_k_dimensional` / `B_random` variant group is absent. That
   missing variant group is not listed among the seven deviations.
6. **`summary.json` mixes control instances and identity repeats into the
   per-cell group table.** Its per-group `instances` counts sum to **126, not
   122**: the known-false control appears as a group with
   `(n,m,t,k) = (None,None,None,None)`, the matched null appears as a
   **(17,3,3,6)** group row, and each `…_repeat` appears as its own (13,4,4,4)
   and (17,3,3,6) row carrying `closure_D=[4]`. Any consumer aggregating
   `summary.json` by cell double-counts the two repeats' closure values and
   folds the null into a structured cell. `results-table.json` is correctly
   per-instance and `task-report.md`'s table is right (122), so nothing reported
   is wrong — the artifact invites the error rather than committing it. Also
   `f4_completed` is `null` on all 31 group rows.
7. **The resources record is contradicted by a record.**
   `resources.within_budget` reads "memory cap per process 7 GB msolve / 3-7 GB
   closure estimate"; `heavy:5` records `peak_rss_bytes` = 11.86 GB, above the
   contract's declared `maximum_memory_gb: 8`. Enforcement is `advisory` in the
   contract, so this is not an invalidation — but the statement is false, and
   the run that exceeded the ceiling is the (17,3,3,8) attempt that then failed
   at the cap.
8. **Known-false control provenance.** The first of the five known-false F4
   records (`workerA:1`) carries a `command` pointing into
   `runs/RUN-SEMBIN-595308/...ctrl_known_false_N35.ms` — the **superseded**
   run's tree. It is admissible only because its `msolve_input_sha256`
   (`49b57dd6dca6…`) and `system_sha256` (`d6add8026fa5…`) are identical to the
   four later records produced in this run's own tree, and I confirmed the
   `.ms` file present here hashes to that value. Worth stating because a record
   whose command names a superseded directory is otherwise unresolvable.

## Observations referred elsewhere, not resolved here

- **A definition question, for J-2 / the composition.** The known-false F4
  record has `f4_step_count: 1` and its single step, at degree 2, is listed in
  `f4_empty_step_degrees: [2]` (the round shows `pairs 69, sel 69, zero 69,
  new 0`), yet `d_F4_semaev = 2`. Whether the Semaev reading should report a
  degree whose only step is empty is a question about the statistic's
  definition, not about run integrity. I record it and take no position.
- **Instrument coupling exists and did not fire.** `run_cells.py:123, 138` hand
  the F4 trace's quotient dimension to the closure instrument as `s_known`, and
  `closure_cert.py:246` can decide `sufficient` from it. Checked on all 9
  both-measured instances against hash-verified `closure_cert.py`: 5 decided by
  `verdict_basis = "standard monomials = |V(I)| = s"` with
  `solutions_source = "brute force over k free variables"` (the closure's own
  count), 4 by `verdict_basis = "1 in W_D"`, which `closure_cert.py:225-227`
  sets from the closure's own `contains_one` before `s` is consulted. **No
  closure_D among the 9 was decided by an F4-supplied quantity.** The channel is
  real, is disclosed per record in `solutions_source`, and a later cell could
  use it. `summarize.py`'s post-hoc path writes `closure_D_posthoc`, a separate
  field, and never overwrites `closure_D`.
- **Scope.** I offer no reading of what the measured degrees mean, whether the
  stated map is right, or whether anything here bears on Assumption 1 or on
  `EV-DREG-008`. Those are other joints and the Coordinator's composition.

## Why `incomplete` rather than `passed`, `failed`, or `invalid`

Not `failed` or `invalid`: no contract invalidation rule fires. Rule 1 (input
hashes differ) is not triggered on any cell and its substance holds on all 139
retained instances; rule 2 (known-false ≠ 2) is not triggered; rule 4
(structural shape) is not triggered on any of 125 files; rule 3 (matched null)
is unevaluable and is another reviewer's. `stopping_rules[0]` is met at both
reproduction cells and `stopping_rules[2]` is met — 0 discordant pairs, no
nondeterminism to pin. Every reported number reproduces exactly from raw
records that are themselves digest-verified (`artifact-digests.json`: 483 of 483
files match, none missing; the only unlisted files are that file and
`manifest.yaml`).

Not `passed`: two things the contract required as **checks** are absent or
unverifiable here. The byte-identity control was reframed into an assertion with
no detection power, so the run shipped no artifact that would have failed had the
translation layer diverged — the property is true, but the run did not establish
it. And the `code_sha256` block, which `dirty: true` made the sole binding
between this snapshot and the instruments that ran, does not resolve for
`f4_trace.py`, `run_cells.py`, `summarize.py` or `make_manifest.py`. A receipt
whose instrument bytes cannot be located is admissible for its recorded data and
short of reproducible.

Both gaps are repairable without re-running anything: recover the four code
blobs and record the per-record hash comparison (or, better, compare
`msolve_input_sha256` against an independent re-translation of the canonical
bytes, which is what actually has detection power). The comparison itself is
already done and passing, above.

## review_attestation

```yaml
review_attestation:
  joints_owned: [J-1]
  verdict: breaks          # the byte-identity control, as specified; see above
  run_validity_verdict: incomplete
  read_sibling_reports: false
  blind_from_respected: true
```

Full source list, blind-from set and independence qualifications:
`attestation.yaml` in this directory. Machine-readable verdicts, the explicit
(empty) discordant list and the count reconciliation: `findings.json`.
