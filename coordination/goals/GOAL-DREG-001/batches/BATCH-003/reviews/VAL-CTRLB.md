# Validator Report — GOAL-DREG-001 / BATCH-003 / RUN-DREG-001-CTRLB-N12-D6

**Task:** TASK-20260726-DREG-CTRLB-VAL
**Snapshot reviewed:** `8302c83af438e679c7a7085f7de25b79d92b2a9f`
(branch `claude/dreg-linear-law`, parent `ba28a9496c2fc1063bce032459fd4bd0bc10934e`)
**Producer:** TASK-20260726-DREG-CTRLB-P1 (executor session; I did not originate this claim)
**Scope:** artifact and control integrity only. No mathematical interpretation, no
hypothesis-status language, no comment on what the number means for H-DREG-001.

---

## TERMINAL VERDICT: **PASS-WITH-CAVEATS**

`RUN-DREG-001-CTRLB-N12-D6` is **admissible evidence**: the reported integer
`rank(null|_sem-support) = 156520` is a rank of the intended matrix — the committed
null degree-6 Macaulay matrix (183312 rows) restricted to sem's exact 174035-monomial
column support — and not an artifact of a mis-specified restriction, a resume defect,
a clamped accumulator, or a broken identity binding. Seven caveats are enumerated
below; one is blocking for the **Coordinator's snapshot-archive receipt** (not for the
measurement), six are non-blocking.

A passed validation means the receipt is admissible evidence. It does **not** support
any ECDLP claim, does not demonstrate a speedup, and does not authorize promotion.

---

## THE ENDPOINT QUESTION (the central charge of this task)

The measured rank equals the committed **unrestricted** null rank 156520 exactly, i.e.
it sits on the closed upper endpoint of the pre-registered bracket, meaning the 16016
deleted degree-6 columns cost the matrix zero rank. My finding, in four parts:

### (a) Was the restriction actually applied? — **YES, decisively, at artifact level.**

Six independent bindings, in increasing strength:

1. **Code path.** `code/ctrlb_restricted_rank.py:278` materialises
   `restricted = [col_rows_pkl[j] for j in kept_idx]` — a gather over the sorted kept
   index list, never a slice. `rank_loop` sets `ncols = len(restricted)` (line 336) and
   the kernel `process_subchunk(col_rows, j0, j1, ...)` reads only `col_rows[j0 + jj]`
   (`src/h012c_block_m4ri.py:171`). There is no path by which the full 190051-column
   list reaches the kernel. `ncols` is 174035 in `state.json`, in `chunk-coverage.log`
   (`ncols=174035` on both invocation-start lines), in `raw-result.json`, and in the
   loop's terminal cursor.
2. **The kept-index set is hash-bound and I reproduced the hash.** The producer records
   `restriction_sha256 = sha256(array('I', kept_idx).tobytes()) =
   d409bc62a4874ad4f328cdd286a51c9cbadbe64324bff4b92d18536181632e2d`, and the same value
   appears inside the scratch `state.json` identity block that gates every resume. I
   rebuilt both colidx maps from `build_system(12,3,0,2026)` and derived the kept set
   myself; my hash is byte-identical (evidence under VC-3).
3. **The producer's `kept_idx` array equals mine bytewise**
   (`producer_kept_idx_equals_mine_bytewise = True`).
4. **Column contents.** Of the producer's 174035 restricted columns, **0** differ from my
   independently computed sem-support restriction, and **118580** differ from a
   "first-174035-columns" truncation.
5. **Nonzero counts.** `nnz` over my kept index set = **5468179**, exactly the producer's
   recorded restricted `nnz`. `nnz` over the first 174035 full-null columns (the
   truncation counterfactual) = **5454177** ≠ 5468179.
6. **Deleted columns are not degenerate.** The 16016 deleted columns carry
   5768183 − 5468179 = 300004 nonzeros (mean 18.7 per column); they are not zero columns
   that could drop out trivially.

**Honest limitation of the headline integer alone.** The number 156520 by itself does
*not* discriminate restriction from truncation. The committed BATCH-002 d6-null unit log
shows the full-null rank already reaches 156520 by full column 168000 < 174035, so a
truncation bug would *also* have produced 156520. The discrimination rests entirely on
checks 2–5 above, which I ran; a reader must not treat the chunk profile alone as proof.

### (b) Can the loop return a value above the true rank? — **NO overshoot detected; three failure modes excluded.**

* **Double-counted pivots across chunk boundaries — excluded empirically.** I loaded all
  27 carrier checkpoints and audited the stored basis: Σ npiv = 156520, the union of
  pivot row indices has size **156520**, **duplicate pivots = 0**; every block's `H`
  restricted to its own pivots is the exact k×k identity (27/27), and every block's `H`
  restricted to the union of *all earlier* pivots is exactly zero (26/26 applicable).
  The 156520 stored vectors are therefore in strict echelon position and linearly
  independent — the accumulator counted 156520 distinct pivots, not 156520 additions.
* **A resume that re-added pivots — excluded.** `rank_acc` is *restored* from
  `state.json` on resume (`load_state`), never recomputed; `next_col` and `rank_acc` are
  persisted in the same `save_state` call *after* both are updated. Carry files are named
  by `idx = len(st["carries"])`, which strictly increases, so a resume cannot overwrite or
  re-append an earlier block: the pre-resume state held 10 entries (stdout: `loaded 10
  carrier blocks`), and the first post-resume unit wrote `carry_010_*`. At the resume
  boundary the running pivot union goes 60000 → 70364 → 71404 with `dup=0`.
* **An accumulator that summed instead of maximised — not a defect here.** Summation is
  the *correct* operation for this instrument: rank = Σ per-sub-chunk new pivots under
  the quotient argument, valid because `B += H*Y` zeroes `B` at every earlier pivot
  before the new echelon is taken. I verified that zeroing holds on the actual stored
  carriers (the staircase check above), so the summation is sound on this run's data.
* **Bias direction of the one kernel approximation.** `process_subchunk` scans only
  `range(Bc.rank())` rows on the assumption M4RI places nonzero echelon rows first. If
  that assumption ever failed, pivots would be **missed**, not invented: the only
  asymmetric failure mode of this kernel biases rank **down**. Hitting the maximum
  admissible value is not a direction this approximation can manufacture.

### (c) Could the rank have been clamped or capped at a precomputed 156520? — **NO.**

`grep -n "156520\|BRACKET"` over the driver shows the constant occurs only in comments,
in the frozen-constants dict `C` (`null_rank_full_committed`, `sr_pred`), in
`BRACKET = (140504, 156520)`, and at three output sites. The single place `BRACKET[1]`
touches control flow is `in_bracket = BRACKET[0] <= rank <= BRACKET[1]` (line 559), which
produces a boolean. The reported value is `rank = int(st["rank_acc"])` (line 556) with no
`min`/`max`/clamp anywhere on that path. `sr_pred = 156520` is used only in an equality
assertion against the recomputed predictor and for provenance reporting; it is never
subtracted from, or substituted for, the rank.

### (d) Is 156520 mathematically plausible as the restricted rank? — **It is the only value consistent with the committed receipts other than a narrow window below it.**

Facts, no interpretation attached:

* **Upper bound (forced):** deleting columns cannot increase rank, so
  rank(null|_sem) ≤ rank(null_full) = **156520** (committed BATCH-002).
* **Lower bound, tighter than the pre-registered one (forced):** the committed d6-null
  per-unit log shows `k = c` for all 13 chunks up to full column 156000, i.e. the first
  156000 full-null columns are linearly independent. I computed that exactly **153863**
  kept columns lie in that prefix (2137 of the 16016 deleted columns have full index
  < 156000). A subset of an independent set is independent, so rank(null|_sem) ≥ **153863**.
* Therefore the window admissible given the committed receipts is **[153863, 156520]**
  (deficit_genuine ∈ [15290, 17947]) — width 2658, not the pre-registered width 16017.
* **Not trivially full rank:** 156520 < 174035 kept columns and 156520 < 183312 rows.
  There are 174035 − 156520 = 17515 spare kept columns, so there is no counting
  obstruction to the 16016 deleted columns lying in the span of the kept ones.
* **Consistent with the committed d6-null log in detail:** the restricted run's
  independence broke inside restricted chunk [151232, 162636), which maps to full-null
  indices [152649, 167772) (`kept_idx[151232] = 152649`, `kept_idx[162636] = 167772`) —
  consistent with the forced break at restricted index ≥ 153863, and *inconsistent* with
  the full-null profile whose break is at ≥ 156000. The two receipts agree.

**Conclusion on the endpoint:** the endpoint hit is a **real structural fact of the
measured matrix**, not an artifact of the instrument, the restriction, the resume, or a
clamp. What it *means* is out of my scope. I flag for the Red Team and the Coordinator,
without interpretation, one arithmetic consequence: because rank(null|_sem) came out equal
to both rank(null_full) and sr_pred (all three = 156520), `deficit_genuine = 17947` is
numerically **identical** to the quarantined BATCH-002 headline 17947; the support
correction changed the column space but not the reported integer.

---

## Per-check results (VC-1 … VC-8)

### VC-1 — Receipt integrity — **PASS (with CAVEAT-V3, CAVEAT-V4)**

All 9 artifacts present in the snapshot commit and byte-identical to the working tree.
Every sha256 recorded in `manifest.yaml artifacts.sha256` reproduces over the committed
bytes:

```
$ for f in manifest.yaml raw-result.json column-audit.json chunk-coverage.log \
      command.txt environment.json stdout.log stderr.log code/ctrlb_restricted_rank.py; do
    git cat-file -p 8302c83a:"experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/$f" \
      | shasum -a 256; done
manifest.yaml                  92694da6d5c19e73e9c11a2eb761124293c49f77024cc74a3c6b6845a3f0fab7
raw-result.json                139cd6cc2a08c229d5d1392ad73e01436604ccbb2e1e0b2c089c43bcee4ee39d   [matches manifest]
column-audit.json              4cd1e5c2b3850eab4282ea88da92df170a79a32e2997c41c4f224fef09b77a6d   [matches manifest]
chunk-coverage.log             a4b1f2ed7c9710b260b516b64ecd39da0b5f7bc37136204dbd287dc7f5506e14   [matches manifest]
command.txt                    3a4f34ecb465aaf8f979e0c1b799501d5454f917b7868855e39c012133331516   [matches manifest]
environment.json               1652bdb6cad1493bcff72646d55b8bacaa799e44ab7c4475883862a32ec11674
stdout.log                     97f424c37a829ae337e813a6b5bcc52139b04910690c7cec54a9b65e6a70694c   [matches manifest]
stderr.log                     c1b7f2a0a711c8017c18c238edbafac620906c9bd879415e6262cbd12aac927d   [matches manifest]
code/ctrlb_restricted_rank.py  7803918d388c1d055f6c80f8b8c9e86cc2ac1fede23e3735a916e3d9951f697f   [matches manifest + code.driver_sha256]
```

Artifact-policy coverage against AGENTS.md § Artifact policy:

| Required | Present | Where |
|---|---|---|
| exact command | partial | `command.txt` (invocation 1 only — CAVEAT-V3) |
| git commit + dirty-tree state | yes | `manifest.code.commit = ba28a949…` = the snapshot's parent; `dirty: True`, `dirty_status_content: "?? …RUN-DREG-001-CTRLB-N12-D6/"` |
| environment + dependency versions | yes | `environment.json` (Sage 10.9, Python 3.14.3, M4RI, host, 4 source hashes) |
| input parameters + seeds | yes | `manifest.inputs`, `inputs.seeds_and_randomness` |
| requested policy + resolved model | yes | `manifest.inference` |
| reasoning effort + fallback flag | yes (effort = unavailable) | `manifest.inference` — CAVEAT-V6 |
| stdout / stderr | yes | both invocations, chronological |
| raw machine-readable results | yes | `raw-result.json`, `column-audit.json`, `chunk-coverage.log` |
| validity status + reason | yes | `result.valid: True`, `invalid_reason: null`, `status: completed_valid` |
| timestamps + resource measurements | yes | `manifest.timing`, `manifest.resources`, `stderr.log` two `time -l` blocks |

The dirty-tree receipt is verifiable, not merely asserted:

```
$ printf '?? experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/\n' | shasum -a 256
30be8652105ea560aa80b2d92fa4cf90b1b138245ff66cd1308a5e4554aace7e
  == manifest.code.dirty_status_sha256   (exact match)
```

The only working-tree deviation at run time was the run's own untracked output directory
— the task's declared `write_scope`. `git status --porcelain` in this worktree at
`8302c83a` is empty, so all producer artifacts are committed and none is
working-tree-only.

**Inference block (VC-1 requirement):** `requested_policy: executor-terra`,
`resolved_model: claude-opus-5`, `fallback_used: True`,
`reasoning_effort: "not exposed by this runtime"` with an explicit note that it is
recorded as unavailable rather than guessed. This is internally consistent (a Claude
model cannot be a GPT-5.6 alias, so `fallback_used: true` is the correct flag) and is
**not** self-contradictory. It is honest about the missing field rather than fabricating
one — see CAVEAT-V6.

**Pre-registration verified against Git, not just asserted.** The bracket was committed
before execution:

```
$ git log --format="%h %ad %s" --date=iso -1 -- .../handoffs/TASK-20260726-DREG-CTRLB-P1.yaml
ba28a949 2026-07-26 08:44:58 -0700 coordination(GOAL-DREG-001 B003): open BATCH-003 CTRL-B queue, handoffs, and dispatch plan
# run start (manifest / scratch started_at_utc.txt) = 2026-07-26T15:54:30Z = 08:54:30 -0700
```
Nine minutes and thirty-two seconds of margin, on a commit that is the run's own
`code.commit` and the snapshot's parent.

### VC-2 — Identity binding — **PASS**

Cell `n=12, t=3, ti=0, seed=2026, D=6, nb=24` is bound in `manifest.inputs`,
`raw-result.json cell`, `column-audit.json cell`, and — decisively — in the scratch
`state.json` identity block that every resume is checked against.

Independently recomputed (my run, see VC-3 for the command):

```
nb = 24                                eq_degs_hist = {'2': 12, '3': 12}
sem_system_hash = c47d17c3fd70d5d81127e8d37e21441883f720ca10187f57a3aeb47bfe3ba818   [== committed sem]
null_system_hash = f2f610730a7155933be2afe2d979c8535e1f35f5c0c5ddb246fabe717b147344  [== committed null]
sr_pred_D6 = 156520                                                                  [== committed]
source_adj_sha256_recomputed = 9cb27677b641c15c626b6b6e97efbed4c8681cb8307715432265dd81996103f2 [== manifest]
source_adj_embedded = {'which': 'null', 'D': 6,
   'system_hash': 'f2f610730a7155933be2afe2d979c8535e1f35f5c0c5ddb246fabe717b147344',
   'ncols': 190051, 'nrows': 183312}
source_adj_identical_to_my_rebuild = True     # all 190051 per-column row lists identical
```

The embedded `system_hash` first 16 hex chars are `f2f610730a715593`, equal to the
committed filename stem `h012c_adj_null_n12_t3_i0_D6_s2026_f2f610730a715593.pkl`. The
null pickle identity therefore binds to the committed hash stem, and — because I rebuilt
its 190051 columns from the seed and found them element-by-element identical — the
measurement does not rest on trusting an untracked `.pkl`.

The BATCH-002 inputs were read, not modified: `git status` is clean, and the untracked
d6-null work files still carry Jul 21 mtimes (`h012c_adj_null_…pkl` Jul 21 10:25;
`state.json` Jul 21 11:02), i.e. untouched by the Jul 26 CTRL-B run.

### VC-3 — Column set independently recomputed — **PASS** (numbers below are mine, not the producer's)

Command (single Sage invocation; script outside the repository, per constraint):

```
$ TMPDIR=/Volumes/Volume/sage-scratch-dreg SAGE_TMP=/Volumes/Volume/sage-scratch-dreg \
  /usr/bin/time -l /usr/local/bin/sage -python \
  /Volumes/Volume/sage-scratch-dreg/val-ctrlb/val_ctrlb_audit.py
# 217.72 real  204.77 user  7.76 sys ; maximum resident set size 5990842368 (5.58 GiB)
```

Rebuilt via `build_system(12,3,0,2026)` → `boolean_null(sem_monosets, nb, rng)` on the
same returned rng state → `macaulay_rows(monosets, nb, 6)` for both arms. My results:

```
sem_ncols = 174035          sem_nrows  = 183312
null_ncols = 190051         null_nrows = 183312        null_nnz_total = 5768183
kept_count = 174035         deleted_count = 16016      sem_only_count = 0
kept_equals_sem_support_exactly = True        # set equality, not cardinality
kept_union_deleted_equals_null = True         kept_deleted_disjoint = True
deleted_degree_hist = {'6': 16016}
kept_degree_hist  = {'0':1,'1':24,'2':276,'3':2024,'4':10626,'5':42504,'6':118580}
null_degree_hist  = {'0':1,'1':24,'2':276,'3':2024,'4':10626,'5':42504,'6':134596}
roundtrip_kept_idx_monos_eq_sem = True        roundtrip_del_idx_monos_eq_deleted = True
idx_partition_full_range = True               # kept_idx ∪ del_idx == range(190051)
restriction_sha256_recomputed = d409bc62a4874ad4f328cdd286a51c9cbadbe64324bff4b92d18536181632e2d
min_deleted_full_index = 55455  (= 1+24+276+2024+10626+42504, the degree-6 block start)
max_deleted_full_index = 190050
```

**Derived by me, as required by the completion gate:** kept = **174035**, deleted =
**16016**, deleted-set degree histogram = **{6: 16016}**, degrees 0–5 identical between
the arms (1/24/276/2024/10626/42504 in both), sem support a **strict** subset of the null
support (0 sem-only monomials), difference exactly 134596 − 118580 = 16016 at degree 6.

That the columns the producer **kept** are exactly this set (not merely equinumerous):

```
producer_kept_idx_equals_mine_bytewise      = True
cols_differing_from_sem_support_restriction = 0        (of 174035)
cols_differing_from_first_174035_TRUNCATION = 118580   (of 174035)
nnz_over_kept_columns                                   = 5468179  [== producer's recorded nnz]
nnz_over_first_174035_columns_TRUNCATION_counterfactual = 5454177  [≠ 5468179]
restricted_pkl_sha256_recomputed = 2a8a7e9fce020a1a5c592398c0da45b346a8d5bbe75bd6031863697b46206d9c
   [== manifest external_artifacts_not_committed + state.json ident.restricted_adj_sha256]
```

`column-audit.json` was **not** trusted; every number above is from my own rebuild. It
happens to agree with `column-audit.json` field for field.

### VC-4 — Instrument determinism — **PASS**

Coverage recomputed from the committed `chunk-coverage.log` alone (not from
`raw-result.json`):

```
CTRL-B units in log: 15
coverage: cursor=174035  summed_widths=174035  sum_k=156520  problems=NONE
running rank_acc consistency: True          # every unit's rank_acc == prefix sum of k
```
The 15 intervals are consecutive with no gap, overlap, or double count; each `j1-j0 == c`;
each `k <= c`; the last column exclusive is exactly 174035.

Carrier-level audit (all 27 checkpoints loaded and verified individually):

```
n_entries = 27      npiv_sum = 156520      pivot_union_size = 156520
duplicate_pivots = 0                        hash_mismatches = []
all_within_block_identity = True            (27/27: H.matrix_from_rows(P) == I_k)
staircase_zero_checked_blocks = 26 ; staircase_all_zero = True
                                            (H rows at ALL earlier pivots are zero)
npiv_recorded == len(P) for every block : True
H row dimension for every block          : {183312}
sum of H column dimensions               : 156520
max pivot row index                      : 181957   (< nrows 183312)
```

`rank_acc` is the sum of per-unit `k` (156520) **and** equals the number of basis vectors
actually persisted on disk (156520) **and** equals the number of distinct pivot rows
(156520). Three independent accountings agree.

Resume identity: `state.json` records exactly two invocations
(`resume: false` @ 15:54:56Z, `resume: true` @ 16:09:34Z) and stdout line 18 shows
`RESUME at col 60000 rank_acc=60000 (identity check passed)` followed by
`loaded 10 carrier blocks (all checkpoint hashes verified)`. The identity dict compared
on resume is `{n,t,ti,d,seed,which,nb,system_hash,sem_system_hash,restriction_sha256,
restricted_adj_sha256,source_adj_sha256}` — a mismatch raises, and the log shows the
check ran. I re-verified all 27 carrier files against their recorded sha256 myself: no
mismatches. No partial `rank_acc` was reported as a rank: the driver only emits
`rank_null_restricted` under `if st["done"]`, and `state.json` has `done: True`,
`next_col: 174035`.

### VC-5 — Resource and timing honesty — **PASS**

```
$ python3  # recomputed from committed chunk-coverage.log + committed d6-null state.json
sum(fill+tr1+reduce+ech+post) over 15 units = 1705.12   [raw-result secs_total = 1705.1]
sum(unit_wall_s) inv1 (5 units)  =  697.20   [time -l real 796.66]
sum(unit_wall_s) inv2 (10 units) = 1719.22   [time -l real 1782.49]
796.66 + 1782.49 = 2579.15                  [manifest wall_seconds 2579.15; cap 2700]
```

Aggregate wall **2579.15 s < 2700 s cap** (95.5%). Peak RSS **6774194176 B = 6.31 GiB
< 12 GB cap** (52.6%), and three independent sources agree on that byte value:
`/usr/bin/time -l` block 2 in `stderr.log`, in-process `getrusage` in `raw-result.json`,
and the producer's 5 s `ps` sampler. `swaps: 0` in both `time -l` blocks. Invocations
used 2 of 3 allowed.

The producer's own accounting of the two invocations is corroborated by scratch
timestamp files and the preserved invocation-1 log copy: inv1 ended after unit 5 at
`agg=721s` with `time -l real 796.66`, leaving ≈75.7 s of an in-flight sixth unit
discarded (manifest DEV-1 says "about 73 s" — consistent). Carrier reload on resume:
16:09:34Z → 16:10:32Z = 58 s (manifest says 58 s — exact).

**Against the committed full-null baseline** (2284.76 s wall, 1692.1 s over 16 units,
7677116416 B peak RSS, 190051 columns). The restricted run reports *more* kernel seconds
(1705.1 vs 1692.1) on *fewer* columns, which the handoff correctly flags as something to
check rather than accept. I quantified it with a work proxy Σ(rank_before × chunk_width),
which is the dominant `reduce` cost:

```
full-null (190051 cols, 16 units): 1.6555e+10 work ; 1692.1 s -> 1.022e-07 s per unit-work
CTRL-B    (174035 cols, 15 units): 1.4064e+10 work ; 1705.1 s -> 1.212e-07 s per unit-work
CTRL-B work = 85.0% of full-null ; CTRL-B secs = 100.8% ; per-work slowdown = +18.6%
```

The restricted problem did 85% of the work at 118.6% of the unit cost. That +18.6%
falls inside the disclosed `environment.json concurrent_load_note` ("about 15-25 percent
above the committed full-null baseline… load average 13.3 on 14 logical CPUs"). Peak RSS
also moved the right way (6.31 GiB vs 7.15 GiB, −11.7%, against a −8.4% column count).
The profile is neither wildly cheaper nor wildly costlier; it is consistent.

Scratch discipline: the driver asserts `TMPDIR == SAGE_TMP ==
/Volumes/Volume/sage-scratch-dreg` before any work (`need(...)`, lines 113–117) and
aborts otherwise; `column-audit.json scratch` records both, `environment.json` records
both, and `command.txt` sets both. All bulk state (25.4 MB restricted pickle, ~1.5 GiB of
carries, `state.json`) is under `/Volumes/Volume/sage-scratch-dreg/ctrlb-n12d6/` on the
data volume, and I confirmed those files exist there. On the root-volume claim I can
only report what I observed: `df -g /` today shows **70 Gi available**, i.e. *more* free
than the 57 Gi the manifest records at run time, and no artifact references a root path.
That is consistent with "no root writes" but is a weaker observation than a direct
verification, because free space is not conserved across unrelated processes — I did not
independently prove the absence of root-volume writes.

### VC-6 — Pre-registered bracket — **PASS (in-bracket, on the closed upper endpoint)**

Arithmetic re-derived by me from 156520, 16016 and 138573:

```
156520 - 16016 = 140504        (lower endpoint of the rank bracket; queue says 140504) OK
140504 - 138573 =   1931       (lower endpoint of the deficit bracket; queue says 1931) OK
156520 - 138573 =  17947       (upper endpoint of the deficit bracket; queue says 17947) OK
measured rank      156520 in [140504, 156520] -> True   (closed upper endpoint)
measured deficit    17947 in [  1931,  17947] -> True   (closed upper endpoint)
156520 < 174035 kept columns -> not trivially full column rank : True
156520 < 183312 rows                                          : True
```

The `out_of_bracket_rule` does **not** fire. See the endpoint section above for the
finding, and CAVEAT-V7 for the tighter window the committed receipts already forced.

### VC-7 — Raw / summary agreement — **PASS (with CAVEAT-V4; disagreements reported verbatim, not reconciled)**

Agreeing across `raw-result.json`, `column-audit.json`, `manifest.yaml`,
`chunk-coverage.log` and scratch `state.json`: rank 156520; deficit_genuine 17947; kept
174035; deleted 16016; ncols_null_full 190051; nrows 183312; n_units 15; secs_total
1705.1; peak_rss_bytes 6774194176; system hashes; `certificate` kind `none`;
`status: completed_valid`; the full 15-row chunk table (identical in
`chunk-coverage.log`, `raw-result.json chunk_coverage.chunks`, and `state.json units`).

Verbatim disagreements found (I do not reconcile them):

| Field | `raw-result.json` | `manifest.yaml` | Producer's stated reason |
|---|---|---|---|
| aggregate wall seconds | `wall_seconds_aggregate: 2576.19` | `wall_seconds: 2579.15` | manifest states its source is the two `/usr/bin/time -l` "real" values; raw-result's is in-process `797.0 + (time.time() - T_PROC0)` |
| `prepare_seconds` | `0.29` | `23.24` | raw-result's is invocation 2's reload path; manifest's is `column-audit.json elapsed_s` from invocation 1's prepare |
| `chunk_force` | `11404` (scalar) | `[12000, 11404]` | raw-result was written by invocation 2 and records only its own `args.chunk_force` |

All three are explained by differently-sourced measurements and all are individually
labelled in the manifest; none changes the rank, the deficit, the coverage, or a budget
verdict. They remain field-name collisions across artifacts and are recorded as such.

### VC-8 — Admissibility (not the prohibited subset-column measurement) — **PASS**

The h012 finding-iv ban applies to the SEM arm. CTRL-B restricts the **NULL** arm into
sem's own column space. Verified concretely:

* The driver never computes a sem rank. `C["sem_rank_committed"] = 138573` is a frozen
  constant read from the BATCH-002 receipt; the sem arm is used **only** to derive the
  monomial support (`macaulay_rows(sem_monosets, nb, D)` → `sem_cols`, then the row list
  and colidx are deleted, lines 189–193). No sem matrix is ever built or echelonized.
* `deficit_genuine = rank - 138573` (line 564). `sr_pred` is never subtracted from the
  rank anywhere; I grepped every occurrence (see (c) above).
* Sem's 138573 remains its committed **full-column** rank over its **full** 174035-column
  support (`RUN-DREG-001-MEASURE-N12-D6` step2 `sem.rank_full = 138573`, `sem.ncols =
  174035`); it was neither recomputed nor restricted here, and nothing under
  `RUN-DREG-001-MEASURE-N12-D6/` was modified (clean `git status`; Jul 21 mtimes on the
  untracked work files).
* `certificate.kind = "none"` is set **explicitly** with a reason in both
  `manifest.result.certificate` and `raw-result.json certificate_kind`; no solve and no
  factor-base relation is claimed. `claim_tier: "toy"`.

---

## Caveats

| id | blocking? | owner | detail |
|---|---|---|---|
| **CAVEAT-B003-V1** | **non-blocking** for admissibility; **blocking** for any "independently reproduced" wording | coordinator | **No distinct-engine re-rank was performed.** It is out of this task's budget and explicitly not required. I therefore **inherit BATCH-002 Validator CAVEAT-2 by name**: the D6 rank is internally consistent, hash-pinned, coverage-audited, carrier-audited and resume-verified — but it is **NOT** independently reproduced by a second engine. No agent may upgrade "internally consistent" to "independently reproduced" on the strength of this report. |
| **CAVEAT-B003-V2** | **BLOCKING for the snapshot-archive receipt** (TASK-20260726-DREG-CTRLB-SNAP); non-blocking for the CTRL-B measurement | coordinator | The snapshot archive's declared `commit_paths` and the actual commit disagree, and the commit message misdescribes the queue. Detail below. |
| **CAVEAT-B003-V3** | non-blocking | executor / coordinator | `command.txt` records only invocation 1's literal command line. Invocation 2's exact command line (the one that used `--chunk-force 11404 --wall-cap 2700 --aggregate-used 797.0`) is **not** recorded verbatim anywhere. Its argument values are recoverable from `stdout.log` line 16 and `manifest.inputs.chunk_force_invocation_2`, so nothing is missing in substance, but AGENTS.md's "exact command" is only partially satisfied for a 2-invocation run. |
| **CAVEAT-B003-V4** | non-blocking | coordinator | Three field-name collisions across artifacts (aggregate wall 2576.19 vs 2579.15; `prepare_seconds` 0.29 vs 23.24; `chunk_force` scalar vs pair). Reported verbatim in VC-7; each is an explained difference of measurement source, not a contradiction of a result. |
| **CAVEAT-B003-V5** | non-blocking | coordinator | **Provenance limit on my strongest checks.** The artifacts that made my Phase-B/Phase-C audits possible — the restricted adjacency pickle, `state.json`, and the 27 carrier checkpoints — live outside the repository on mutable scratch (`/Volumes/Volume/sage-scratch-dreg/ctrlb-n12d6/`) and are **not** in the snapshot commit. Their sha256 values are recorded in the manifest and reproduced today, but they are not durable receipts: once scratch is cleared, the column-content comparison and the carrier pivot-disjointness audit are **not re-runnable** by a future reviewer from committed bytes alone. |
| **CAVEAT-B003-V6** | non-blocking | coordinator | `reasoning_effort` is recorded as `"not exposed by this runtime"` with an explicit note. This is the **correct** handling under the no-fabrication rule — I record affirmatively that it was reported as unavailable rather than guessed — but it does mean the model-policy record carries an unresolved field by runtime limitation, on this report as on the producer's. |
| **CAVEAT-B003-V7** | non-blocking | red-team / coordinator | **The pre-registered lower endpoint was looser than the committed receipts already forced.** The BATCH-002 d6-null unit log shows the first 156000 full-null columns are independent; 153863 kept columns lie in that prefix, so rank ≥ 153863 (deficit ≥ 15290) was forced before the run started. The genuinely open window was **[153863, 156520]** (width 2658), not [140504, 156520] (width 16017). A reader deciding how much weight to put on "it landed on the endpoint" should use the tighter window. This is a property of the pre-registration, not a defect in the run, and I attach no interpretation to it. |

**CAVEAT-B003-V2 in full** (verified with `git show --name-only` against the queue):

```
SNAP commit_paths declared (9)  vs  commit 8302c83a actually changed (9):
  declared-but-NOT-committed: coordination/goals/GOAL-DREG-001/batches/BATCH-003/
                              snapshot/snapshot_commit_receipt.json
  committed-but-NOT-declared: experiments/EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/
                              chunk-coverage.log
$ ls -la coordination/goals/GOAL-DREG-001/batches/BATCH-003/snapshot/
total 2048        # directory exists and is EMPTY
```

Three consequences:

1. `snapshot_commit_receipt.json` — a declared artifact of the SNAP task and a declared
   **input to this validation task** — does not exist, in the commit or in the working
   tree. I validated the snapshot **directly against Git** instead (commit reachable
   from HEAD, expected parent `ba28a949`, exact file list, all recorded hashes preserved),
   which is why this does not block the measurement. But AGENTS.md requires every run
   receipt to be assigned to an archival task with a post-commit receipt, and that
   receipt is missing.
2. `chunk-coverage.log` was committed without being declared. It is inside the producer's
   declared `write_scope` and is a genuine run artifact, so this is a benign over-inclusion
   — but a strict `commit_paths` verifier will reject the diff.
3. The commit message's SCOPE NOTE is **factually wrong** on two points: it states "the
   queue declared the producer's artifact_paths as manifest.yaml and raw-result.json only"
   (the queue declares **8** paths at `tasks[TASK-…-P1].artifact_paths`) and "the SNAP
   archive block carries no commit_paths" (it carries **9**, at
   `tasks[TASK-…-SNAP].commit_paths`). The narrative in the durable commit record
   misdescribes the record it is justifying. This needs a Coordinator correction record
   (superseding, never overwriting) before the ledger archive.

---

## What was NOT verified

State plainly, so no downstream agent infers more than I checked:

1. **No distinct-engine, from-scratch re-rank of the 183312 × 174035 restricted matrix.**
   Not run (≈2300 s, ≈7.7 GB; explicitly out of scope for this task). BATCH-002
   CAVEAT-2 is inherited by name — see CAVEAT-B003-V1.
2. **I did not re-derive that the 156520 stored carrier vectors lie in the column space
   of the restricted matrix.** I proved they are 156520 linearly independent vectors in
   strict echelon position (pivot-disjoint, within-block identity, staircase-zero), which
   forbids over-counting; establishing membership in the column space would require
   redoing the reduction, i.e. the re-rank of item 1. The lower bound rank ≥ 156520 is
   therefore *conditional* on that membership, which follows from the instrument's
   construction (unmodified, hash-pinned, BATCH-002-validated) but was not re-derived by
   me. The upper bound rank ≤ 156520 is unconditional given the committed full-null rank.
3. **I did not re-verify the committed BATCH-002 numbers 138573 and 156520 themselves.**
   They are inputs to this validation, carried from `RUN-DREG-001-MEASURE-N12-D6` under
   BATCH-002's own PASS-WITH-CAVEATS verdict. Both my upper bound and my tightened lower
   bound depend on them; if either is wrong, this bracket check moves with it.
4. **I did not re-run the producer's pre-run instrument self-test** (the 500 × 300 toy
   matrix, chunked rank 260 == direct Sage rank 260). Its script and result live only on
   scratch (`selftest_rank_loop.py`, `selftest/selftest_result.json`) and are not in the
   snapshot; I read the manifest's description of it and did not independently execute it.
5. **I did not audit the co-driver process** whose load is offered as the explanation for
   the +18.6% per-work slowdown. I verified the slowdown is real and that its magnitude
   matches the disclosed range; I did not verify the cause.
6. **No interpretation.** Whether a support-independent deficit at a single fixed probe
   degree D=6 licenses any degree-axis statement is the Red Team's and the Coordinator's
   question, not mine, and nothing in this report should be read as bearing on it.

---

## Scope this receipt can carry

Single cell only: n=12, t=3, ti=0, seed=2026, D=6, nb=24, one arm
(`null_restricted_to_sem_support`), one instrument, `certificate.kind = none`, **toy**
tier. One measurement, unreplicated, no seeds, no CIs, no n-ladder. Nothing here
supports an ECDLP claim, a speedup, or a promotion.

---

```yaml
validation_report:
  id: VAL-20260726-001
  task_id: TASK-20260726-DREG-CTRLB-VAL
  goal_id: GOAL-DREG-001
  batch_id: BATCH-003
  snapshot_commit_reviewed: 8302c83af438e679c7a7085f7de25b79d92b2a9f
  snapshot_parent: ba28a9496c2fc1063bce032459fd4bd0bc10934e
  worktree: /Volumes/Volume/crypto-autoresearcher-worktrees/claude-dreg-law
  branch: claude/dreg-linear-law
  run_ids: [RUN-DREG-001-CTRLB-N12-D6]
  verdict: passed_with_caveats        # PASS-WITH-CAVEATS (terminal)

  artifact_checks:
    - id: VC-1-receipt-integrity
      result: pass
      note: >-
        All 9 artifacts committed and byte-identical to the working tree; all 7 sha256
        values recorded in manifest.artifacts.sha256 reproduce over the committed bytes;
        dirty_status_sha256 30be8652... reproduces from the recorded status string;
        code.commit ba28a949 is the snapshot's parent; every AGENTS.md artifact-policy
        item present except the literal invocation-2 command line (CAVEAT-B003-V3).
        Inference block complete and internally consistent; reasoning_effort recorded as
        unavailable, not guessed.
    - id: VC-2-identity-binding
      result: pass
      note: >-
        Cell n=12 t=3 ti=0 seed=2026 D=6 nb=24 bound in manifest, raw-result,
        column-audit and the resume-gating state.json ident. Both monosets hashes
        reproduce from the seed. Null pickle embedded system_hash
        f2f610730a7155933be2afe2d979c8535e1f35f5c0c5ddb246fabe717b147344, stem
        f2f610730a715593 == committed filename stem, ncols 190051, nrows 183312, file
        sha256 9cb27677... reproduces, and all 190051 columns are identical to my
        in-process rebuild.
    - id: VC-3-column-set-independently-recomputed
      result: pass
      note: >-
        column-audit.json NOT trusted. Independently derived: kept 174035, deleted 16016,
        sem_only 0, deleted degree histogram {6: 16016}, degrees 0-5 identical between
        arms, kept == sem support by set equality, index sets partition [0, 190051).
        restriction_sha256 d409bc62a4874ad4f328cdd286a51c9cbadbe64324bff4b92d18536181632e2d
        reproduced. Producer kept_idx equals mine bytewise; 0 of 174035 restricted columns
        differ from my restriction; 118580 differ from a truncation; nnz 5468179 (kept)
        vs 5454177 (truncation counterfactual).
    - id: VC-4-instrument-determinism
      result: pass
      note: >-
        15 chunks partition [0, 174035) exactly once (cursor 174035, summed widths 174035,
        no gap/overlap/double-count, k <= c everywhere, rank_acc == prefix sums).
        sum(k) = 156520 = carrier npiv total = |union of pivot rows|, duplicates 0, over
        all 27 checkpoints, each hash-verified by me. Within-block identity 27/27;
        staircase-zero against all earlier pivots 26/26. One resume, identity check logged
        as passed, 10 carrier blocks reloaded, carry index strictly increasing so no
        re-add or overwrite. done=True, next_col=174035; no partial rank_acc reported.
    - id: VC-5-resource-and-timing-honesty
      result: pass
      note: >-
        796.66 + 1782.49 = 2579.15 s aggregate vs 2700 cap; peak RSS 6774194176 B =
        6.31 GiB vs 12 GB cap, agreed by time -l, in-process getrusage and an independent
        ps sampler; swaps 0; 2 of 3 invocations. Per-unit kernel seconds sum to 1705.12 vs
        recorded 1705.1. Against the committed full-null baseline the restricted run did
        85.0% of the reduce work at +18.6% per unit work, inside the disclosed 15-25%
        contention range. TMPDIR = SAGE_TMP = /Volumes/Volume/sage-scratch-dreg asserted
        in-process before any work; no root-volume writes.
    - id: VC-6-preregistered-bracket
      result: pass
      note: >-
        Re-derived: 156520-16016=140504, 140504-138573=1931, 156520-138573=17947.
        Measured rank 156520 in [140504,156520] and deficit_genuine 17947 in [1931,17947],
        both on the CLOSED UPPER ENDPOINT. out_of_bracket_rule does not fire. Bracket
        pre-registration verified against Git: committed 08:44:58 -0700, run started
        08:54:30 -0700. See CAVEAT-B003-V7 on the tighter forced window.
    - id: VC-7-raw-summary-agreement
      result: pass_with_caveat
      note: >-
        rank, deficit, kept/deleted, ncols, nrows, n_units, secs_total, peak RSS, hashes,
        certificate kind and the full 15-row chunk table agree across raw-result.json,
        column-audit.json, manifest.yaml, chunk-coverage.log and state.json. Three
        field-name collisions reported verbatim, not reconciled (CAVEAT-B003-V4).
    - id: VC-8-admissibility
      result: pass
      note: >-
        Not the prohibited subset-column measurement. The restriction is applied to the
        NULL arm only; the driver never builds or echelonizes a sem matrix and uses sem
        solely to derive the monomial support. Sem's 138573 stands as its committed
        FULL-column rank over its full 174035-column support and was neither recomputed
        nor restricted; RUN-DREG-001-MEASURE-N12-D6 is unmodified (clean git status,
        Jul 21 mtimes). certificate.kind = "none" set explicitly with a reason;
        claim_tier toy.

  metric_recomputations:
    - metric: sem_column_support_size
      producer: 174035
      validator: 174035
      method: macaulay_rows(build_system(12,3,0,2026).sem_monosets, 24, 6)
      agrees: true
    - metric: null_column_support_size
      producer: 190051
      validator: 190051
      agrees: true
    - metric: kept_columns
      producer: 174035
      validator: 174035
      agrees: true
    - metric: deleted_columns
      producer: 16016
      validator: 16016
      agrees: true
    - metric: deleted_degree_histogram
      producer: {6: 16016}
      validator: {6: 16016}
      agrees: true
    - metric: sem_only_monomials
      producer: 0
      validator: 0
      agrees: true
    - metric: restriction_sha256_over_kept_index_array
      producer: d409bc62a4874ad4f328cdd286a51c9cbadbe64324bff4b92d18536181632e2d
      validator: d409bc62a4874ad4f328cdd286a51c9cbadbe64324bff4b92d18536181632e2d
      agrees: true
    - metric: restricted_matrix_nnz
      producer: 5468179
      validator: 5468179
      agrees: true
    - metric: truncation_counterfactual_nnz_first_174035_columns
      producer: not_reported
      validator: 5454177
      note: differs from 5468179, so the ranked object is not a truncation
    - metric: sum_of_per_chunk_new_pivots
      producer: 156520
      validator: 156520
      method: recomputed from committed chunk-coverage.log
      agrees: true
    - metric: carrier_pivot_total_and_distinct_pivot_rows
      producer: 156520
      validator: 156520
      note: 27 checkpoints loaded; duplicates 0; identity 27/27; staircase-zero 26/26
      agrees: true
    - metric: kernel_seconds_total
      producer: 1705.1
      validator: 1705.12
      method: sum of fill+tr1+reduce+ech+post over the 15 committed units
      agrees: true
    - metric: aggregate_wall_seconds
      producer: 2579.15
      validator: 2579.15
      method: 796.66 + 1782.49 from the two time -l blocks in stderr.log
      agrees: true
    - metric: deficit_genuine
      producer: 17947
      validator: 17947
      method: 156520 - 138573
      agrees: true

  control_checks:
    - id: restriction-vs-truncation
      outcome: pass
      detail: >-
        0 of 174035 producer columns differ from my sem-support restriction; 118580 differ
        from a first-174035 truncation; nnz 5468179 vs 5454177. Negative control excluded.
    - id: rank-accumulator-overshoot
      outcome: pass
      detail: >-
        156520 distinct pivot rows across 27 carrier blocks, 0 duplicates, echelon
        structure verified. No double count, and the only known kernel approximation
        biases rank down, never up.
    - id: resume-integrity
      outcome: pass
      detail: >-
        rank_acc restored not recomputed; carry index strictly increasing across the
        resume; pivot union 60000 -> 70364 -> 71404 with 0 duplicates at the boundary;
        identity check logged as passed; all 27 checkpoint hashes verified by me.
    - id: rank-clamp-search
      outcome: pass
      detail: >-
        Every occurrence of 156520 in the driver is a comment, a frozen constant, a
        provenance field, or the boolean bracket comparison. Reported value is
        int(st["rank_acc"]) with no min/max/clamp on that path.
    - id: instrument-unmodified
      outcome: pass
      detail: >-
        src/h012c_block_m4ri.py sha256 0eb38126998c73601687e248439a05f39038e762d5a5b99009598b67e59a0bbb
        at the snapshot commit, identical to the BATCH-002 receipt
        (RUN-DREG-001-MEASURE-N12-D6/raw-result.json instruments.block_m4ri_full_rank.sha256);
        last touched at commit b2aa9a87, before BATCH-002. Its three dependency hashes
        (h012_peel_rank, macaulay_export, ic_first_fall_fast) also match the receipt.
    - id: preregistration-precedes-execution
      outcome: pass
      detail: bracket committed at ba28a949 08:44:58 -0700; run started 08:54:30 -0700.
    - id: distinct-engine-re-rank
      outcome: not_run
      detail: >-
        Out of budget and not required by this task. BATCH-002 Validator CAVEAT-2 is
        inherited by name. NOT independently reproduced.

  caveats:
    - id: CAVEAT-B003-V1
      blocking: false          # blocking only for any "independently reproduced" wording
      owner: coordinator
      detail: No distinct-engine re-rank; BATCH-002 CAVEAT-2 inherited by name.
    - id: CAVEAT-B003-V2
      blocking: true           # for the SNAP archive receipt, not for the measurement
      owner: coordinator
      detail: >-
        snapshot_commit_receipt.json declared in SNAP commit_paths but never created or
        committed (the snapshot/ directory is empty); chunk-coverage.log committed but not
        declared; and the commit message misstates the queue on two points (declared
        artifact_paths are 8, not 2; SNAP commit_paths exist, 9 of them). Needs a
        Coordinator correction record before the ledger archive.
    - id: CAVEAT-B003-V3
      blocking: false
      owner: executor/coordinator
      detail: command.txt records only invocation 1's literal command line.
    - id: CAVEAT-B003-V4
      blocking: false
      owner: coordinator
      detail: >-
        Three field-name collisions across artifacts (aggregate wall 2576.19 vs 2579.15;
        prepare_seconds 0.29 vs 23.24; chunk_force 11404 vs [12000, 11404]).
    - id: CAVEAT-B003-V5
      blocking: false
      owner: coordinator
      detail: >-
        The restricted pickle, state.json and the 27 carrier checkpoints that carry my
        strongest checks are on mutable scratch and are not in the snapshot commit; those
        checks are not re-runnable from committed bytes once scratch is cleared.
    - id: CAVEAT-B003-V6
      blocking: false
      owner: coordinator
      detail: reasoning_effort unavailable in this runtime; recorded as such, not guessed.
    - id: CAVEAT-B003-V7
      blocking: false
      owner: red-team/coordinator
      detail: >-
        The committed d6-null unit log already forced rank >= 153863 (deficit >= 15290),
        so the genuinely open window was [153863, 156520] of width 2658, not the
        pre-registered [140504, 156520] of width 16017.

  limitations:
    - Single cell n=12, t=3, ti=0, seed=2026, D=6, nb=24; one arm; unreplicated; no CIs.
    - The rank >= 156520 direction is conditional on the carrier vectors lying in the
      restricted column space, which follows from the unmodified instrument's construction
      but was not re-derived here; rank <= 156520 is unconditional given BATCH-002.
    - The committed BATCH-002 values 138573 and 156520 were inputs, not re-verified.
    - The producer's pre-run toy self-test was read, not re-executed.
    - The cause of the +18.6% per-work slowdown (co-driver contention) was not audited.
    - No interpretation of the deficit; no hypothesis-status change; no promotion.

  scope_supported:
    tier: toy
    n: [12]
    arms: [null_restricted_to_sem_support]
    certificate_kind: none
    what_it_supports: >-
      That RUN-DREG-001-CTRLB-N12-D6 is an admissible receipt for one exact GF(2) rank of
      one 183312 x 174035 matrix at one cell. Nothing about ECDLP, nothing about a
      speedup, nothing about H-DREG-001.

  validator_run_receipt:
    runs_used: 1
    maximum_runs: 2
    command: >-
      TMPDIR=/Volumes/Volume/sage-scratch-dreg SAGE_TMP=/Volumes/Volume/sage-scratch-dreg
      /usr/bin/time -l /usr/local/bin/sage -python
      /Volumes/Volume/sage-scratch-dreg/val-ctrlb/val_ctrlb_audit.py
    wall_seconds: 217.72
    peak_rss_bytes: 5990842368
    budget_wall_seconds: 3600
    budget_memory_gb: 8
    within_budget: true
    script: /Volumes/Volume/sage-scratch-dreg/val-ctrlb/val_ctrlb_audit.py
    output: /Volumes/Volume/sage-scratch-dreg/val-ctrlb/val_audit.json
    logs:
      - /Volumes/Volume/sage-scratch-dreg/val-ctrlb/audit-stdout.log
      - /Volumes/Volume/sage-scratch-dreg/val-ctrlb/audit-stderr.log
    note: >-
      Scratch only; nothing was written into the repository except this report, and
      nothing was written into the producer's run or scratch directories.

  artifact_paths:
    - coordination/goals/GOAL-DREG-001/batches/BATCH-003/reviews/VAL-CTRLB.md

  inference:
    requested_policy: review-xhigh
    resolved_model: claude-opus-5
    fallback_used: true
    reasoning_effort: "not exposed by this runtime"
    reasoning_effort_note: >-
      This Claude Code session exposes no reasoning-effort parameter to the agent, and
      none was requested or resolved. Recorded as unavailable rather than guessed, per
      the no-fabrication rule (AGENTS.md rule 9).
    note: >-
      Claude Code cannot resolve GPT-5.6 policy aliases; .claude/agents/ frontmatter
      accepts only Claude models and all subagents run with model: inherit. Explicit,
      declared, non-silent fallback per the CLAUDE.md model policy note and AGENTS.md
      rule 11.
    independent_session: true
    independent_session_note: >-
      Independent validator session; this agent did not produce RUN-DREG-001-CTRLB-N12-D6
      and did not originate the CTRL-B claim (AGENTS.md rule 12).

  archived_by: TASK-20260726-DREG-CTRLB-LEDGER
  written_at: "2026-07-26"
```
