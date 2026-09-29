# Validation report — TASK-20260824-bc488d

Goal `GOAL-MLKEM-005` · batch `BATCH-f9780d` · role validator · fresh session, not a
continuation of the producer's or the archiver's.

Snapshot commit read: `e17d95cbfdfcdb047c682c89a626745fe53b72e2`
(parent `2fe7dfebb4e3697aca14753a10b3214de7c9eeee`). `git status --porcelain` was
empty for the whole review; every digest below was recomputed from the commit's own
blobs **and** from the working tree, and the two agree everywhere.

This report verifies. It does not interpret the result, move a hypothesis, or write
a ledger record. A passed or incomplete verdict here is a statement about
admissibility of a receipt and nothing else.

---

## 0. Summary of verdicts

| # | Item | Verdict |
| --- | --- | --- |
| 1 | `seed_used == 452658293` in every cell that has a record | **PASS** (1 of 2 cells has a record) |
| 2 | `strategies_sha256` identical across recorded cells and `== f516a0…` | **PASS** (1 of 2 cells has a record) |
| 3 | `gso_float_type_used == 'mpfr'` | **PASS** (1 of 2 cells has a record) |
| 4 | Receipt `path_sha256` matches the files on disk at this commit | **PASS**, 15/15, 0 mismatch, 0 missing |
| 5 | Could the runner as pinned have produced the records that exist? | **YES** — and the Coordinator's write-after-return claim is stated correctly |
| — | Is the matched pair genuinely MATCHED? | **MATCHED BY DESIGN, UNVERIFIABLE AS RUN** — see §4 |
| — | Producer completion gate, item 1 (`all_runs_terminal`) | **FAIL**, as the producer and the receipt both report |
| — | Terminal verdict | **`incomplete`** |

Three findings are load-bearing beyond the checklist and are set out in §5–§7:
the pinned runner could not have recorded `tours` or a root-Hermite factor even on
success (§5.3); the 75-bit "reference" cell was already known to ERROR before this
batch was dispatched, so the pair had no baseline even in principle (§4.6); and a
binding condition of the decision this batch descends from was not implemented, and
its absence cost this batch its only remaining result (§6.2).

---

## 1. Artifact and receipt integrity

### A-1 — every declared digest recomputed. PASS.

All 15 `archive_receipt.path_sha256` entries of
`archives/TASK-20260824-c7248f/receipt.yaml` were recomputed by me with
`hashlib.sha256`, once over `git show e17d95cb:<path>` and once over the file on
disk. **15/15 match the declared value in both directions. 0 mismatch, 0 missing,
0 non-hash sentinels.** The receipt was not trusted for any of them.

Two entries are worth stating explicitly because they are the ones the task card
forces:

- `…/inputs/fplll_strategies_default.json` →
  `f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18`, equal to the
  value pinned in `task_card.what_to_run.strategies_sha256`, in the handoff, and in
  `invalidation_triggers[0]`. The trigger does **not** fire.
- `…/rt_ctrl_1_matched_pair.py` →
  `bc0524ee432a2327bc4a5cfff5d8f5d79b590d37b2f38ea428c78af5abb25035`, equal to
  `task_card.what_to_run.script_sha256`.
- `stderr.log` and `stderr.attempt1_killed.log` both hash to
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, which is
  sha256 of the empty byte string. The execution report's "0 bytes. Empty, not
  omitted" is confirmed by digest, not by file size alone.

### A-2 — parent commit. PASS.

`git rev-parse e17d95cb^` = `2fe7dfebb4e3697aca14753a10b3214de7c9eeee` =
`archive_receipt.parent_sha`.

### A-3 — `commit_sha: null`. DISCLOSED GAP in the archiver's own gate, non-fatal.

`TASK-20260824-c7248f`'s completion gate item 2 reads "The receipt records
commit_sha and parent_sha of the snapshot commit." `parent_sha` is recorded and
correct; `commit_sha` is `null`, with `commit_sha_note` giving the self-reference
reason and pointing at CLAUDE.md's "Archive receipts bind to CONTENT first". I
record this as an unmet item of the **archiver's** gate rather than waving it
through, and I record that it is not load-bearing here because I verified the
content binding independently (A-1) and the commit is in any case reachable from
`HEAD`. This is a defect of the archive task, not of the producer.

### A-4 — the commit changed exactly what it should have. PASS.

`git diff --name-only 2fe7dfeb e17d95cb` returns exactly 13 paths: the receipt plus
the 12 producer artifacts the run created. The other three receipt-declared paths —
`rt_ctrl_1_matched_pair.py`, `task_card.yaml`, `inputs/fplll_strategies_default.json`
— have **byte-identical blob ids at both commits**. This is independent
corroboration, from git rather than from the executor's assertion, of the execution
report's "Runner sha256 verified before AND after both attempts, unchanged". The
prohibition "Do not modify the runner or the archived strategies file" holds.

### A-5 — receipt coverage. PASS.

The receipt's 15 declared paths are exactly the 15 files under
`tasks/TASK-20260824-b3e9da/` at this commit. No omission, no extra.

### A-6 — generated artifacts. PASS, note only.

`dispatch_plan.json` / `dispatch_plan.md` exist on disk under the batch directory and
are untracked and gitignored, per CLAUDE.md "Generated artifacts are never
committed". They are not in the receipt and should not be.

### A-7 — strategies-file provenance. GAP, recorded as a limitation, not a failure.

The file is bound by **content** and is archived inside the commit, so the run is
reproducible from this repository alone; that is what route (c) needed and it holds.
But **no artifact in this batch records where those bytes came from** — not an
upstream URL, not an fplll release or commit, not a generation command. I inspected
it: a 8 606 859-byte JSON list of 101 entries, `block_size` 0…100, each with
`preprocessing_block_sizes` and `pruning_parameters`; block 55 carries
`preprocessing_block_sizes: [36]` and 21 pruning parameters (first: radius factor
`0.8992271105826423`, probability `0.524873708375701`, 55 coefficients). So it is a
genuine tuned strategies file covering β=55, **not** the pruning-free
`[Strategy(b) for b in range(41)]` substitute that
`instrument_readiness_20260824.md` warned against — which is the right outcome. What
cannot be established from any committed record is *which* fplll strategies file it
is, and therefore nothing here re-establishes the cross-container byte-identity
`DEC-20260824-526f89` correctly calls unrecoverable.

---

## 2. The producer's completion gate, item by item

Gate text is from `dispatch_queue.json` → `tasks[0].handoff.completion_gate`. Values
below are quoted verbatim from `rt_ctrl_1_matched_pair_results.json` and
`rt_ctrl_1_matched_pair_results.attempt1_killed.json`; nothing is paraphrased and
nothing is inferred.

### G-1 "Both cells (mpfr_bits 75 and 100) attempted and recorded with status, wall clock, tours and root-Hermite factor." — **FAIL**

Cell `mpfr_bits: 75`, attempt 2 (the run of record):

```
"status": "ERROR"
"error": "ReductionError: b'infinite loop in babai'"
"cell_wall_clock_seconds": 3051.823137998581
"outer_lll_reduction_elapsed_seconds": 498.9597418308258
```

`tours` — **absent from the record.** `root_hermite_factor` — **absent.**
`b0_norm` — **absent.** `bkz_elapsed_seconds` — **absent.** Two of the four fields
the gate names are therefore missing even for the cell that terminated. See §5.3:
they are missing for a deeper reason than the exception.

Cell `mpfr_bits: 100`: **no entry of any kind.** `report["cells"]` has length 1 in
both results files. There is no `status`, no `seed_used`, no
`strategies_sha256`, no `gso_float_type_used`, no wall clock, no `tours`, no
`root_hermite_factor`, no `error`. I fill in none of them.

The gate's escape clause — "An ERROR status in either cell SATISFIES this gate
provided it is reported verbatim: the gate is about the completeness of the record,
not about the outcome" — rescues cell 75, whose ERROR is reported verbatim and
twice. It cannot rescue cell 100, which has no status at all rather than an ERROR
status. This matches the producer's own `all planned runs terminal | FAIL` and the
receipt's `all_runs_terminal: FAIL`.

### G-2 "`seed_used == 452658293` in BOTH cells." — **PASS on the one cell that has a record; unverifiable on the other**

- attempt 2, cell 75: `"seed_used": 452658293`
- attempt 1, cell 75: `"seed_used": 452658293`
- cell 100: no record.

I recomputed the value independently, in a fresh process at the declared interpreter
(`…/scratchpad/sagevenv/bin/python`, Python 3.11.15, numpy 2.4.6), from the formula
`numpy.random.default_rng([715923, 0, d, beta, 0, 0]).integers(0, 2**31 - 1)`:

```
(512, 40) -> 2074339090
(512, 55) -> 452658293
(512, 70) ->  915347894
```

These reproduce `task_card.forced_values_declared_before_the_run.seed_verified`
exactly and match every seed the predecessor batch recorded. `invalidation_triggers[2]`
("seed_used is not 452658293 in both cells") does not fire on any recorded cell; it
is unevaluable for cell 100.

### G-3 "`strategies_sha256` identical across both cells and equal to `f516b0a6…b27a18`." — **PASS on the record that exists**

Recorded at the report level and in the cell-75 block of **both** results files:

```
"strategies_sha256": "f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18"
"strategies_file_used": "/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/inputs/fplll_strategies_default.json"
```

I recomputed the archived file's digest and it equals that value (A-1). One
qualification a reader should have: the runner computes the report-level hash and
every cell hash by calling the same `sha256()` on the same module constant
`STRATEGIES` (lines 31, 56, 98), so cross-cell identity is a **property of the
source**, not an independent observation. It is nonetheless true, and
`invalidation_triggers[0]` and `[1]` do not fire.

### G-4 "`gso_float_type_used == 'mpfr'` in both cells." — **PASS on the one cell that has a record**

`"gso_float_type_used": "mpfr"` in attempt 2 and in attempt 1. This is
`M.float_type` read back from the constructed `GSO.Mat`, i.e. the object's own
report, not an echo of the requested value — the right thing to record. Cell 100:
no record. `invalidation_triggers[3]` does not fire on any recorded cell.

### G-5 "`run_start_utc.txt` and `run_end_utc.txt` both written." — **PASS**

```
run_start_utc.txt                 2026-08-25T06:21:19Z
run_end_utc.txt                   2026-08-25T11:12:59Z
run_start_utc.attempt1_killed.txt 2026-08-25T05:13:39Z
killed_at_utc.attempt1.txt        2026-08-25T06:21:08Z
exit_rc.txt                       EXIT_RC=124
```

### G-6 "An ERROR status in either cell SATISFIES this gate provided it is reported verbatim." — **PASS for cell 75**

The error string is reported verbatim and is byte-identical across attempt 1,
attempt 2, and (on the committed predecessor record) the predecessor run:
`ReductionError: b'infinite loop in babai'`.

---

## 3. Metric recomputation from raw artifacts

### M-1 Raw-vs-summary agreement — PASS.

Every numeric and string value quoted in `execution_report.md` §"Cells, exactly as
recorded" appears character-for-character in the results JSONs. I checked each:
`452658293`, `f516b0a6…b27a18`, `mpfr`, `498.9597418308258`, `3051.823137998581`,
`508.58293199539185`, `2974.328118801117`, the error string, `EXIT_RC=124`, and the
stated absences of `tours` / `root_hermite_factor` / `b0_norm`. No hand-editing
signature. The stdout logs' per-cell lines agree with the JSON to sub-second
truncation (`3051.8s` vs `3051.823137998581`; `2974.3s` vs `2974.328118801117`).

### M-2 Timestamp arithmetic — THREE DISCREPANCIES, none load-bearing. Recorded, not smoothed.

Recomputed from the archived timestamp files and stdout lines:

| quantity | recomputed by me | as reported | Δ |
| --- | --- | --- | --- |
| attempt 1 elapsed (05:13:39Z → 06:21:08Z) | **4049 s** | `4030 s` (execution report; "~4030 s" in the snapshot commit message) | +19 s |
| attempt 2 elapsed (06:21:19Z → 11:12:59Z) | **17500 s** | `17508 s` | −8 s |
| cumulative task wall clock | **21549 s** | `21538 s` | +11 s |
| attempt 1, cell 100 unterminated span (06:03:13Z → 06:21:08Z) | **1075 s** | "~1050 s" | +25 s |
| attempt 2, cell 100 unterminated span (07:12:10Z → 11:12:59Z) | **14449 s** | `14 448 s` (report and commit message) | +1 s |

The 17500 s figure is exactly the `timeout 17500` value, which is what a SIGTERM at
the cap should produce; `17508 s` is not derivable from any archived artifact.
Nothing downstream breaks: the ceiling conclusion survives recomputation with
**21549 s against 21600 s**, i.e. 51 s of headroom rather than the 62 s implied, and
the executor's stated reason for reducing `timeout` from 21600 to 17500 ("solely so
that attempt 1 + attempt 2 stay under the task's 21600 s ceiling") is still
satisfied under the corrected figures. The reporting-mark numbers (`~626 s`,
`~10370 s`, `~7318 s`) are internally consistent with the report's own 4030 s; under
the recomputed 4049 s they become 626 s, 10351 s and 7299 s. The 1 s residual on
14 448 s is timestamp granularity and is not a defect.

### M-3 The ">= 4.7x" figure — PASS as stated, and correctly labelled.

`14449 / 3051.823137998581 = 4.735`. The execution report calls it "a lower bound on
an unfinished computation and NOT a cost measurement", and the snapshot commit
message repeats that before any reviewer read it. Both are correct and I endorse the
wording, not the inference anyone might draw from the number.

### M-4 This run's own noise floor — a new measurement, computed by me.

Cell 75 was run twice, same seed, same bytes, same container:

- cell wall clock `2974.328118801117` → `3051.823137998581` = **+2.61 %**
- outer LLL `508.58293199539185` → `498.9597418308258` = **−1.89 %**

So this instrument cannot resolve a wall-clock contrast smaller than roughly 3 %
between two cells. That is consistent with the 5–8 % environmental error bar
`DEC-20260815-3e8e9c` records for this goal. It bites on nothing in this record,
because no cross-cell contrast exists; it is recorded so a successor sizing a
tour-level precision comparison knows the floor.

### M-5 Cross-container consistency — computed by me, and it is NOT a contrast.

Against the predecessor's committed `main_grid[0]`:

- cell-75 total: `3051.823137998581 / 2502.7416553497314 = 1.219`
- outer LLL: `498.9597418308258 / 413.6276364326477 = 1.206`

The two ratios agree to 1.1 percentage points, which is what one expects if the same
deterministic computation ran on a host about 20 % slower. I record this as
**evidence that the same computation was performed**, and for nothing else. It is
not a precision comparison, it is not a cost comparison, and the producer was right
to draw none: the predecessor's strategies bytes are unrecoverable, so the two runs
differ in an input as well as in a host.

---

## 4. THE CENTRAL QUESTION: is the matched pair genuinely matched?

The batch exists to make two cells differ in mpfr precision **alone**. I split the
question, because the two halves have different answers.

### D-1 Same basis — HOLDS BY DESIGN, and I confirmed it by execution.

The runner re-seeds inside each cell (`FPLLL.set_random_seed(seed)`, line 53) before
generating (`IntegerMatrix.random(d, "qary", k=d//2, q=Q)`, line 58), so cell 2's
basis does not depend on anything cell 1 consumed. I tested this rather than
assuming it: in one process at the declared interpreter I ran the runner's own
preamble, consumed the global RNG in between, changed precision in between, and
re-seeded. All three generated bases are identical —

```
row-serialised sha256 = a5ec1e4d4713b7e23a6e91df7350a744a3dcb8d22cc05fcc702b505a4cd7df26
  (fresh seed) == (after intervening RNG consumption + set_precision(75)/(53))
              == (at set_precision(100))
```

Neither intervening randomness nor the mpfr precision setting perturbs basis
generation. (The digest is my own row serialisation, not a producer artifact; it is
offered as a fingerprint a successor can reuse.)

### D-2 Same pre-GSO stage — HOLDS, and it holds *because of* the `finally` block.

`FPLLL.set_precision(mpfr_bits)` (line 63) runs after the outer LLL, and the
`finally` block restores `set_precision(53)` (line 86) on both the success and the
exception path. I measured the process-start global precision in this container:
`FPLLL.set_precision(53)` returns `53`, so the default equals the restored value.
Therefore cell 2's `IntegerMatrix.random` and `LLL.reduction(A)` ran at exactly the
precision cell 1's did. Had the default not been 53, or had the reset been outside
`finally` (cell 1 raised), the outer LLL would have been silently unmatched. It was
not. This is the one place the design could have quietly failed and it does not.

### D-3 Same strategies bytes, same invocation, same container — HOLDS.

`STRATEGIES` is a module constant; both cells run in one `main()` in one process
under one `timeout` invocation. Verified by source and by the single stdout stream.

### D-4 …but the pair is UNVERIFIABLE AS RUN, because half of it produced nothing.

D-1 to D-3 are statements about the **program**, established from the pinned source
and from my re-execution of its preamble. They are not observations of the 100-bit
cell, because the 100-bit cell wrote no record. There is no recorded `seed_used`, no
`strategies_sha256`, no `gso_float_type_used`, no basis fingerprint and no status
for it. The correct statement is: **the pair is matched by construction and its
matchedness is unobserved on one side.** Under AGENTS.md rule 5 nothing about cell
100 is filled in here, and the batch's own `uncertainty_reduced` — "how its cost
compares to the SAME basis at `mpfr_bits=75`" — is not reduced at all.

### D-5 One confound is uncontrolled, and would have mattered had both cells returned.

Cell order is fixed (75 then 100), never counterbalanced and never repeated within
one process. A wall-clock difference between the cells would therefore confound
precision with position — allocator and page-cache warmth, machine load, thermal
state. M-4 bounds that at roughly 3 %. It costs nothing here because no contrast
exists; a successor that intends to *measure* a per-cell cost ratio should either
alternate the order across runs or run each cell in its own process.

### D-6 The pair had no baseline even in principle — and this was knowable before dispatch.

The 75-bit cell is labelled `"role": "REFERENCE (the contrast)"`. It produced no
cost. It produced a **time to failure** of `3051.823137998581` s. So even a
returning 100-bit cell could only have been compared against a failure time.

This is not hindsight. On the committed predecessor record,
`BATCH-0d5018/tasks/TASK-20260815-f14d3c/main_grid_d512_beta5570_reattempt_results.json`
records for the same cell, same seed, same construction:

```
"mpfr_bits": 75, "seed_used": 452658293,
"status": "ERROR",
"error": "ReductionError: b'infinite loop in babai'",
"subprocess_wall_clock_seconds": 2502.7416553497314
...
"n_cells_completed": 0
```

and `DEC-20260815-3e8e9c` states it in terms — "(d=512, beta=55) raised
ReductionError('infinite loop in babai') after 2502.74 s" and "The only two cost
figures in the record are a FAILURE cost (2502.74 s) and a LOWER BOUND". The same
decision records that the predecessor's Validator **reproduced that failure on a
second host, same error string character-for-character**.

Neither `task_card.yaml` nor `instrument_readiness_20260824.md` nor
`DEC-20260824-526f89` states that the 75-bit cell had already failed identically.
They describe 2502.74 s as what the cell "cost" and as the basis of a ~5000 s
expectation. The four pre-declared outcomes list `both_error` as a possibility
without noting that half of it was already observed twice. Recorded as a
**contract-fidelity finding against the dispatch**, not against the executor, who
ran the pinned card exactly and retuned nothing.

**Answer to the central question:** the two cells differ in `mpfr_bits` alone — that
is verifiable from the pinned source and I verified the two places it could have
silently broken. But only one cell was observed, that one is the reference rather
than the target, and it yielded a failure time rather than a baseline. There is no
precision attribution available from this batch in either direction, and none is
claimed anywhere in the package.

---

## 5. Could the runner as pinned have produced the records that exist?

Source read at `bc0524ee432a2327bc4a5cfff5d8f5d79b590d37b2f38ea428c78af5abb25035`,
byte-unchanged across both commits (A-4).

### R-1 Yes for cell 75; necessarily no for cell 100. The Coordinator's claim is CORRECT.

`main()` (lines 102–113) is:

```python
for c in cells:
    ...
    r = worker_main_cell(D, BETA, c["mpfr_bits"])      # line 106
    ...
    report["cells"].append(r)                          # line 109
    ...
    with open(out, "w") as fh:                         # line 112
        json.dump(report, fh, indent=2)                # line 113
```

The append and the write both follow the **return** of `worker_main_cell`. A cell
killed before that return contributes nothing — not a partial entry, none. The
snapshot commit's line reference ("line 112, inside the per-cell loop") is exact.

A killed *process* also cannot reach the `except`/`finally` recording path: `timeout`
delivers SIGTERM, for which CPython installs no handler, so the interpreter dies
without unwinding. The execution report's explanation of why cell 100 has no entry
is therefore correct on both counts.

So the file on disk — one cell, `mpfr_bits: 75`, terminal — is exactly what this
runner produces when cell 1 returns and cell 2 is signalled. **The records that
exist are consistent with the pinned source and could not have been produced any
other way by it.**

### R-2 Which commit is right: **both sentences are true of the source; they are about different cells.**

- Dispatch commit `2fe7dfeb`, and still verbatim at
  `dispatch_queue.json` → `tasks[0].artifact_paths_note`: *"Both cells write into
  one results JSON, rewritten after each cell so a kill mid-run still leaves the
  completed cell recorded."* Read literally, about a **completed** cell, this is
  **accurate**, and it was borne out twice: cell 75 returned, was written, and its
  record survived both kills — which is the only reason the 75-bit ERROR is known to
  reproduce at all.
- Snapshot commit `e17d95cb`: *"writes its results JSON only AFTER `worker_main_cell`
  RETURNS (line 112, inside the per-cell loop). A cell killed mid-computation
  therefore leaves NO RECORD AT ALL."* This is **accurate**, about the **killed**
  cell, and the line reference checks out.

They do not contradict each other. The earlier sentence is silent on the killed
cell while its phrasing — "a kill mid-run still leaves … recorded" — invites the
reading that a mid-run kill leaves a usable record of the run, which is not what
happened. The retraction's own qualifier, "That is true only of a cell that
RETURNS", states the position exactly. **Verdict: the snapshot commit's correction
is correctly stated and is, if anything, harder on the earlier wording than the
source requires; the retracted sentence was incomplete rather than false.** Owning
it before any reviewer read the artifacts is the right handling.

One consequence the correction does not reach: `dispatch_queue.json` is
**byte-identical between `2fe7dfeb` and `e17d95cb`**, so the un-retracted sentence
still stands in the coordination record at the snapshot commit. The correction lives
only in a commit message, and a later reader of the queue does not see it.

### R-3 THREE UNDECLARED DEPARTURES FROM THE PINNED PREDECESSOR

The runner's docstring says the construction is "reused VERBATIM" from
`58a1fdc21f45730789feeff69c6a6fd7c24bf4938be15d6e878afd246d0de485` and that "THE ONE
DELIBERATE DEPARTURE" is the strategies source. I recomputed that predecessor sha
from the tree (it matches) and diffed the two `worker_main_cell` bodies. The
construction, seed formula, precision-before-GSO ordering and ROW_EXPO-free GSO
*are* reproduced faithfully — that part of the claim holds. Three other things
changed, none of them declared:

**(a) `tours` is unrecordable by this runner, even on success.**
Predecessor: `bkz(par, tracer=True)` then
`n_tours = sum(1 for child in bkz.trace.children if child.label[0] == "tour")`.
This runner: `bkz(par)` (line 73, no tracer) then
`result["tours"] = getattr(bkz, "tours", None)` (line 75). Neither
`fpylll.algorithms.bkz` nor `fpylll.algorithms.bkz2` ever assigns a `tours`
attribute — the string occurs 0 times in either module. I ran a real small BKZ in
this container under the runner's exact calling convention:

```
getattr(bkz, 'tours', None) -> None
hasattr(bkz, 'tours')       -> False
```

So a **COMPLETED** cell would have recorded `"tours": null`. The completion-gate item
naming `tours` was unsatisfiable from the moment the runner was pinned, and the
execution report's explanation of the absence ("the field is only assigned after
`bkz(par)` returns") is true but incomplete: the field would have been `null` even
if it had returned.

**(b) `root_hermite_factor` is not a root-Hermite factor.**
Predecessor:
`delta_0 = (sqrt(M.get_r(0,0)) / exp(M.get_log_det(0,d)/d)) ** (1.0/d)` — the
standard definition, taken from the GSO's own log-determinant.
This runner, line 78:

```python
result["root_hermite_factor"] = float(b0) ** (1.0 / d) / (Q ** 0.5) ** (1.0 / 1)
```

The trailing `** (1.0 / 1)` is a no-op. For this q-ary construction
(`k = d//2`, so `vol^(1/d) = q^(1/2)`) the definition requires the `1/d` exponent to
apply to the *ratio*, i.e. `(Q ** 0.5) ** (1.0 / d)` in the denominator. As written,
the recorded quantity is smaller than δ₀ by a factor `q^(1/2 − 1/(2d))`, which is
**57.242 at d = 512**. Measured on a genuinely reduced basis at d = 80 in this
container: runner formula `0.018481105`, standard δ₀ `1.0136088`, ratio `54.8457` =
`3329^(1/2 − 1/160)`, as predicted. Consequence: had either cell completed, the field
named `root_hermite_factor` would not have held one, and would not have been
comparable with the predecessor's `delta_0_root_hermite_factor`. No value was
produced this run, so nothing recorded is wrong — this is a latent defect that a
successor must fix before any completed cell is believed.

**(c) No traceback is recorded.** The predecessor stored
`traceback.format_exc()`; this runner stores only
`f"{type(exc).__name__}: {exc}"` (line 82). What that costs, precisely: the field
assignment order brackets the exception to the interval between the
`LLL.Reduction(M, …)` construction and the return of `bkz(par)` — because
`gso_float_type_used` (line 65, before `BKZ.Param`) **is** present and
`bkz_elapsed_seconds` (line 74, after `bkz(par)` returns) is **absent**. That
interval still *includes* `BKZ.Param(...)` and includes `BKZReduction.__call__`'s
pre-tour `self.lll_obj()`.

The execution report's claim "`BKZ.Param(...)` did NOT raise" is nevertheless
**supported**, but by the error *type* rather than by a traceback: a failed
`BKZ.Param` raises `RuntimeError: Cannot open strategies file.` (reproduced twice in
`instrument_readiness_20260824.md` §2 and §3), and the recorded exception is
`ReductionError`. I accept it on that basis and record the basis. What is **not**
supported by this batch's artifacts is localisation to a *tour*. The predecessor's
record does localise it — a nine-frame traceback ending at
`bkz.py:186 self.lll_obj(lll_start, lll_start, kappa + block_size)` inside a
doubly-nested `svp_preprocessing` within `tour` — and `DEC-20260815-3e8e9c` already
carries that. That is corroborating context from a different run on a different
host, not this run's evidence, and it should not be reported as this run's.

### R-4 The unit under test is not "ONE FULL BKZ TOUR".

The task card title, the handoff objective and `uncertainty_reduced` all say "ONE
FULL BKZ TOUR at (d=512, beta=55)". The runner calls `bkz(par)` with
`flags=BKZ.AUTO_ABORT` and no loop bound. Measured in this container:
`BKZ.Param(block_size=55, flags=BKZ.AUTO_ABORT).max_loops == 0` and
`flags & BKZ.MAX_LOOPS` is false; `BKZReduction.__call__` runs `while True` over
tours and breaks only on `clean`, `block_size >= M.d`, auto-abort, `MAX_LOOPS` or
`MAX_TIME`. **The executed unit is a full BKZ reduction of unbounded tour count, not
one tour.** The wording is inherited from `GOAL-MLKEM-005.next_action` and
`DEC-20260815-3e8e9c`, so it is a standing description defect rather than an
executor deviation — but it is not cosmetic: any per-cell figure this batch had
produced would be a per-*reduction* cost, not a per-tour cost, and with `tours`
unrecordable (R-3a) the record could never have said how many tours were bought.

---

## 6. Control checks

### C-1 Positive/negative controls against the frozen contract — INCOMPLETE, not failed.

The batch declares no separate positive or negative control. Its control structure
**is** the matched pair, and half of it produced nothing (§4). Nothing is scored as a
failed control.

### C-2 A BINDING CONDITION OF THE PREDECESSOR DECISION WAS NOT IMPLEMENTED, AND ITS ABSENCE COST THIS BATCH ITS ONLY REMAINING RESULT.

`DEC-20260815-3e8e9c` — cited in `DEC-20260824-526f89.evidence_basis` — imposes five
binding conditions on the follow-up. Condition (i), verbatim:

> "(i) RT-CTRL-2's ZERO-COMPUTE INSTRUMENT FIXES LAND FIRST, BEFORE ANY FURTHER
> CAPPED RUN: call `.cpu_times()` on the psutil handle the polling loop already
> holds; persist tour progress on SIGTERM (a signal handler or per-tour flush of
> `bkz.trace`'s tour count) and retain `stdout_tail` for a timed-out cell; capture
> load average into environment.json. This batch spent 14400.08 s -- 63.9% of its
> compute -- to learn one bit ("> 14400 s"), and these fixes convert the next
> timeout into a tours-per-hour cost curve, which is exactly the quantity a Stage-1
> sizing decision needs and does not have. They cost no lattice compute."

Checked against the pinned runner, line by line: **no signal handler, no per-tour
flush, no use of `bkz.trace` at all, no psutil, no `cpu_times()`, no
`environment.json`, no load average.** `DEC-20260824-526f89` does not mention
condition (i), does not implement it, and records no deviation from it.

The measured consequence: the 100-bit cell ran **14449 s** and the machine-readable
record learned exactly one bit — "> 14449 s". That is the identical loss condition
(i) was written to prevent, at essentially the identical magnitude, one batch later.

The snapshot commit independently identifies the same defect and prescribes "a
successor runner must write a STARTED stub before each cell so a capped cell is
still evidence of something". I confirm the stub is necessary, and record that it is
**weaker** than condition (i), which asked for per-tour progress — a stub yields
"started and did not finish", whereas a per-tour flush would have yielded the
tours-per-hour curve the goal has been trying to obtain for four batches.

This is a finding against the dispatch, not against the executor.

### C-3 Condition (ii), dual-mark reporting at 3600 s and 14400 s — DISCHARGED.

Both marks are reported with the cell state at each. The arithmetic behind them
inherits the 4030 s figure corrected in M-2; the marks themselves were reported.

### C-4 Condition (v), preserve every artifact of every execution including an infrastructure-killed one — DISCHARGED IN SUBSTANCE.

Attempt 1's results JSON, stdout, stderr, start timestamp and kill timestamp are all
archived (`*.attempt1_killed.*`, `killed_at_utc.attempt1.txt`) and bound by the
receipt. The condition's literal `failed_infrastructure` **label** is not used; the
naming convention plus `execution_report.md` "Deviations" §1 and §3 carry the same
information and the deviation is disclosed rather than hidden. This is the condition
whose violation in the predecessor batch produced an unverifiable corroboration
claim; it was not repeated. Recorded as satisfied, with the label deviation noted.

### C-5 Condition (iii), the near-free rider of two further draws — NOT TAKEN.

Explicitly "strongly recommended and not mandatory". No finding.

### C-6 Condition (iv), scope — RESPECTED.

No (d=512, β=40) re-attempt, no d=256, no CTRL-3 full-tour precision search, no
Stage 1, no ≥8-draw grid, no Branch-B substitute.

### C-7 Null-object control (`docs/inventor-protocol.md` §3) — NOT APPLICABLE to this batch's output, with two facts recorded rather than skipped.

This batch reports no correlation, bias or excess. It reports one exception and one
non-measurement, so there is no statistical signal for a null object to falsify, and
the absence of a null-object control here is not a defect. Two related facts belong
in the record anyway:

1. **The object under test already *is* the null object.**
   `IntegerMatrix.random(d, "qary", k=d//2, q=3329)` is a structureless random q-ary
   lattice; `DEC-20260815-3e8e9c` records the predecessor Red Team's RT-CTRL-3(i) to
   exactly this effect. Everything measured here is a property of fpylll 0.6.4's mpfr
   path on generic bases. The ML-KEM-shaped **nearby-object** control (RT-CTRL-3(ii))
   has never been run in this goal, and `DEC-20260815-3e8e9c` names it as REQUIRED
   before any escalation branch is called ripe.
2. **The decay question is the one this batch was built to answer, and it returned no
   data.** The parameter meant to destroy the failure is mpfr precision; whether the
   failure decays in it *at tour level* is precisely what the 100-bit cell was for.
   It remains open. The only decay evidence in the goal is at the isolated-step /
   partial-progress level, and `KN-FIND-f54a82` — already promoted — holds that an
   isolated-step probe is not evidence about the full tour it stands in for. No
   tour-level decay claim is available from this record and none is made in the
   package.

---

## 7. Cost-model and validation-ladder checks

### CM-1 The batch's only cost statement is built on a failure time.

`dispatch_queue.json` → `tasks[0].budget_justification` and
`task_card.budget.justification`: *"The predecessor's 75-bit cell at this basis cost
2502.74 s. Two cells put the expectation near 5000 s."* Verified against the source:
2502.74 s is `subprocess_wall_clock_seconds` for a cell whose `status` is `"ERROR"`,
in a run with `n_cells_completed: 0`, and `DEC-20260815-3e8e9c` §6(1) says so
explicitly. **It is a time-to-failure, not a cost.** Using it to forecast a batch
whose second cell had never terminated at any precision undersized the run: the
100-bit cell alone ran 14449 s without terminating, against a ~5000 s expectation for
both cells. The 21600 s ceiling was correctly described as "a hard ceiling, not a
forecast", and it is what ended the task.

### CM-2 No expected-cost figure may be computed, and none is. CORRECT.

Per-attempt cost × inverse success probability needs a success probability. The
completed-cell count at (d=512, β=55) is **0** across the predecessor run, the
predecessor's independent re-execution on a second host, and both attempts here.
The producer computes no expected cost, the receipt asserts none, and I compute
none.

### CM-3 Memory beside time — PRESENT IN PROSE ONLY.

`execution_report.md` records "Peak observed RSS of the solver process: ~175 MB
(single-threaded, ~100% of one core)" and "PID 24314". No machine-readable resource
record exists in any artifact: no `peak_rss_mb` field (the predecessor's results JSON
had one), no CPU time, no load average, no `environment.json`. AGENTS.md "Artifact
policy" lists "timestamps and resource measurements" among what each run must retain.
Recorded as a partial gap, and it is the same gap as C-2.

### CM-4 Cost-unit declaration — N/A. No concrete cost table exists in this batch.

### L — validation ladder (`docs/inventor-protocol.md` §6)

**No speedup, ratio, or complexity improvement is claimed anywhere in this batch**,
so the ladder's step-2 requirement does not fire and its absence is not a `failed`
here. Recorded for completeness:

- **Step 1 (isolate each assumption, measure separately).** Exercised by the goal,
  not by this batch — the isolated-step bisection is the predecessor's, and
  `KN-FIND-f54a82` states in terms that it does not transfer to the full tour.
- **Step 2 (whole pipeline on a scaled-down instance, measured ratio, negative cases
  checked).** N/A: there is no baseline and no improvement to ratio against.
- **Step 3 (real object with named cheats).** N/A.
- **Step 4 (reproducibility pointer exercised, not asserted).** PARTIALLY EXERCISED
  BY ME, and listed rather than asserted. Rebuilt from scratch at the declared
  interpreter: the seed (452658293, plus 2074339090 and 915347894 as cross-checks),
  the container's process-start FPLLL precision (53), the generated basis
  fingerprint, the absence of a `tours` attribute after a real BKZ call, the
  `BKZ.Param` loop defaults, and the root-Hermite-factor arithmetic. **Not** rebuilt:
  either lattice cell — cell 75 costs ~3050 s and cell 100 is unbounded, and
  re-running the producer's experiment is not a validator act.

### H — heuristic-validation checks

NOT APPLICABLE. This batch validates no numbered heuristic, pre-registers no
theoretical distribution, reports no empirical CDF or tail statistic, and uses no
substitute-sampling correspondence.

---

## 8. Scope and rule-3 discipline

**S-1 Toy scale, stated correctly everywhere. PASS.** The execution report, the
receipt (`no_interpretation`), and both commit messages state the boundary and make
no ML-KEM or FIPS 203 statement. The tested scope is: `d=512`, `beta=55`, `q=3329`,
`IntegerMatrix.random(d,"qary",k=d//2,q=3329)`, single seed 452658293, fpylll 0.6.4,
Python 3.11.15, one container, one host, 4 CPUs / 16075 MiB. **Nothing in this
report is a statement about ML-KEM at any standardized parameter set**, and no
transfer is asserted.

**S-2 Rule 3 honoured throughout, in both directions. PASS.**

- Attempt 1's runtime kill at **4049 s** — far inside the 21600 s ceiling — is an
  infrastructure event. Attempt 2's `EXIT_RC=124` at the `timeout 17500` cap is a
  resource event. Neither is negative mathematical evidence, neither is treated as
  such by the producer, the receipt, either commit message, or this report.
- The converse is equally important and is also honoured: the 75-bit **ERROR** is
  *not* an infrastructure event. It is an exception raised by a run that terminated
  on its own more than 18 000 s inside its cap, reproduced across two independent
  attempts here with a matching seed and a character-identical error string, and on
  the committed record reproduced by a different session on a different host in the
  predecessor batch. Classifying it as an instrument failure would be as wrong as
  classifying the timeout as a result.
- The producer retuned nothing in response to the ERROR: construction, seed, both
  precisions and the strategies source are byte-identical across attempts, and the
  runner blob is unchanged in git (A-4).

---

## 9. Terminal verdict and why it is not one of the other three

**`incomplete`.**

- Not **`passed`**: the producer's own completion-gate item 1 fails on its face; three
  of the six gate items are checkable on only one of two cells; two metrics the gate
  names (`tours`, root-Hermite factor) were unrecordable by the pinned runner even on
  success (R-3a, R-3b); and the designed contrast has no data on one side and no
  baseline on the other (§4.6).
- Not **`failed`**: the reason cell 100 has no record is a wall-clock cap plus a
  runner recording defect — an infrastructure and instrument outcome, which under
  AGENTS.md core rule 5 / CLAUDE.md rule 3 is never negative evidence and must not be
  scored as one.
- Not **`invalid`**: nothing in the record is unsound, fabricated, hand-edited, or
  out of declared scope. The receipt is exact, the raw and summary agree, the seed
  and strategies bytes verify independently, the scope statements are correct, and
  the one cell that terminated is admissible evidence of exactly what it says.

What this verdict does **not** do: it does not support any ECDLP or ML-KEM claim, does
not demonstrate or refute a precision effect at tour level, does not authorize any
promotion, and does not license reading the 100-bit cell's 14449 s as a cost.

---

## 10. Required output record

```yaml
validation_report:
  id: VAL-20260824-bc488d
  task_id: TASK-20260824-bc488d
  goal_id: GOAL-MLKEM-005
  batch_id: BATCH-f9780d
  snapshot_commit_read: e17d95cbfdfcdb047c682c89a626745fe53b72e2
  snapshot_parent: 2fe7dfebb4e3697aca14753a10b3214de7c9eeee
  working_tree_state_at_review: clean (git status --porcelain empty)
  run_ids:
    - TASK-20260824-b3e9da attempt 2 (run of record, EXIT_RC=124)
    - TASK-20260824-b3e9da attempt 1 (runtime-killed, artifacts preserved)

  artifact_checks:
    - id: A-1
      check: recompute all 15 receipt path_sha256 from the commit blobs and from disk
      result: PASS - 15/15 match in both directions; 0 mismatch, 0 missing, 0 sentinels
    - id: A-2
      check: receipt parent_sha equals git rev-parse e17d95cb^
      result: PASS - 2fe7dfebb4e3697aca14753a10b3214de7c9eeee
    - id: A-3
      check: archiver gate item 2 "receipt records commit_sha and parent_sha"
      result: PARTIAL - commit_sha is null with a disclosed self-reference reason;
        parent_sha correct; non-fatal because content binding was verified
        independently. An unmet item of TASK-20260824-c7248f's gate, not the
        producer's.
    - id: A-4
      check: commit changed set, and whether the pinned inputs were modified
      result: PASS - exactly 13 paths changed (receipt + 12 new producer artifacts);
        rt_ctrl_1_matched_pair.py, task_card.yaml and inputs/fplll_strategies_default.json
        have identical blob ids at 2fe7dfeb and e17d95cb. Independent git
        corroboration of "runner unchanged before and after both attempts".
    - id: A-5
      check: receipt coverage of the producer write_scope
      result: PASS - the 15 declared paths are exactly the 15 files present
    - id: A-6
      check: generated artifacts not committed
      result: PASS - dispatch_plan.{json,md} untracked and gitignored, absent from
        the receipt
    - id: A-7
      check: provenance of the content-pinned strategies file
      result: GAP (limitation, not failure) - bytes archived in the commit and hashed,
        so the run is reproducible from this repository; but no artifact records the
        file's origin (no upstream URL, release, commit or generation command).
        Content inspected - 8606859 bytes, 101 entries block_size 0..100 with
        pruning_parameters; block 55 carries preprocessing_block_sizes [36] and 21
        pruning parameters, so it is a genuine tuned strategies file and NOT the
        pruning-free substitute instrument_readiness_20260824.md warned against.
    - id: A-8
      check: stderr logs empty rather than omitted
      result: PASS - both hash to e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        (sha256 of the empty string)

  completion_gate_checks:
    - item: "Both cells (mpfr_bits 75 and 100) attempted and recorded with status,
        wall clock, tours and root-Hermite factor."
      verdict: FAIL
      recorded_values: >-
        cell 75 (attempt 2): status "ERROR"; error "ReductionError: b'infinite loop
        in babai'"; cell_wall_clock_seconds 3051.823137998581;
        outer_lll_reduction_elapsed_seconds 498.9597418308258; tours ABSENT;
        root_hermite_factor ABSENT; b0_norm ABSENT; bkz_elapsed_seconds ABSENT.
        cell 100: NO ENTRY AT ALL - report["cells"] has length 1 in both results
        files. No status, no seed_used, no strategies_sha256, no
        gso_float_type_used, no wall clock, no tours, no root_hermite_factor, no
        error. Nothing is inferred or estimated for it.
      note: the gate's ERROR escape clause rescues cell 75 but cannot rescue cell
        100, which has no status at all rather than an ERROR status.
    - item: "seed_used == 452658293 in BOTH cells."
      verdict: PASS on the one cell that has a record; UNVERIFIABLE on the other
      recorded_values: 'attempt 2 cell 75: seed_used 452658293; attempt 1 cell 75:
        seed_used 452658293; cell 100: no record'
      independent_recomputation: >-
        numpy.random.default_rng([715923,0,d,beta,0,0]).integers(0,2**31-1) in a
        fresh process at the declared interpreter (Python 3.11.15, numpy 2.4.6):
        (512,40) -> 2074339090, (512,55) -> 452658293, (512,70) -> 915347894.
        Reproduces task_card.forced_values_declared_before_the_run.seed_verified
        exactly.
    - item: "strategies_sha256 identical across both cells and equal to
        f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18."
      verdict: PASS on the record that exists
      recorded_values: >-
        report-level and cell-75 strategies_sha256 =
        f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18 in BOTH
        results files; recomputed from the archived file and equal. cell 100: no
        record.
      qualification: the runner hashes the same module constant with the same
        function for every cell (lines 31, 56, 98), so cross-cell identity is a
        property of the source rather than an independent observation.
    - item: "gso_float_type_used == 'mpfr' in both cells."
      verdict: PASS on the one cell that has a record
      recorded_values: '"mpfr" in attempt 2 and attempt 1 (read back from
        M.float_type, not echoed from the request); cell 100: no record'
    - item: "run_start_utc.txt and run_end_utc.txt both written."
      verdict: PASS
      recorded_values: 'run_start_utc.txt 2026-08-25T06:21:19Z; run_end_utc.txt
        2026-08-25T11:12:59Z; run_start_utc.attempt1_killed.txt 2026-08-25T05:13:39Z;
        killed_at_utc.attempt1.txt 2026-08-25T06:21:08Z; exit_rc.txt EXIT_RC=124'
    - item: "An ERROR status in either cell SATISFIES this gate provided it is
        reported verbatim."
      verdict: PASS for cell 75
      recorded_values: "ReductionError: b'infinite loop in babai' - byte-identical
        across attempt 1, attempt 2, and the committed predecessor record"
    - item: 'invalidation_triggers (all four)'
      verdict: NONE FIRE on any recorded cell; two are unevaluable for cell 100

  metric_recomputations:
    - id: M-1
      metric: raw-vs-summary agreement
      result: PASS - every figure quoted in execution_report.md appears
        character-for-character in the results JSONs; stdout per-cell lines agree
        with the JSON to sub-second truncation
    - id: M-2
      metric: wall-clock arithmetic from the archived timestamps
      result: THREE DISCREPANCIES, none load-bearing
      detail: >-
        attempt 1 elapsed recomputed 4049 s (05:13:39Z -> 06:21:08Z) vs 4030 s
        reported (delta +19 s); attempt 2 elapsed recomputed 17500 s
        (06:21:19Z -> 11:12:59Z, exactly the `timeout 17500` value) vs 17508 s
        reported (delta -8 s); cumulative recomputed 21549 s vs 21538 s reported,
        against a 21600 s ceiling - the "within budget, the ceiling ended it"
        conclusion survives with 51 s of headroom. attempt-1 cell-100 span
        recomputed 1075 s vs "~1050 s"; attempt-2 cell-100 span recomputed 14449 s
        vs 14448 s (1 s, timestamp granularity). The reporting-mark figures
        (~626 s, ~10370 s, ~7318 s) inherit the 4030 s basis; under 4049 s they
        become 626 s, 10351 s, 7299 s.
    - id: M-3
      metric: '">= 4.7x" cell-100 vs cell-75 ratio'
      result: PASS - 14449 / 3051.823137998581 = 4.735, and it is correctly labelled
        a lower bound on an unfinished computation rather than a cost
    - id: M-4
      metric: this run's own wall-clock noise floor (new measurement by me)
      result: cell 75 repeated - cell_wall_clock 2974.328118801117 -> 3051.823137998581
        = +2.61%; outer LLL 508.58293199539185 -> 498.9597418308258 = -1.89%. The
        instrument cannot resolve a cross-cell wall-clock contrast below about 3%.
    - id: M-5
      metric: cross-container consistency (new computation by me; NOT a contrast)
      result: cell-75 total 3051.823137998581/2502.7416553497314 = 1.219; outer LLL
        498.9597418308258/413.6276364326477 = 1.206. The two agree to 1.1 points,
        consistent with the same deterministic computation on a ~20% slower host.
        Evidence that the same computation ran; evidence of nothing else. The
        predecessor's strategies bytes are unrecoverable, so the runs differ in an
        input as well as a host.
    - id: M-6
      metric: root-Hermite-factor formula in the pinned runner (line 78)
      result: DEFECT (latent; no value was produced this run). Recorded quantity is
        b0^(1/d) / q^(1/2); the definition requires (b0 / q^(1/2))^(1/d). Distortion
        factor q^(1/2 - 1/(2d)) = 57.242 at d=512. Measured at d=80 on a reduced
        basis - runner formula 0.018481105, standard delta_0 1.0136088, ratio
        54.8457 = 3329^(1/2 - 1/160), as predicted.

  runner_fidelity_checks:
    - id: R-1
      check: could the pinned runner (sha bc0524ee...) have produced these records
      result: YES - and only these. main() appends and writes only AFTER
        worker_main_cell returns (line 106 call, line 109 append, lines 112-113
        write, all inside the per-cell loop). A cell killed before that return
        contributes nothing. A SIGTERM-killed process additionally never reaches the
        except/finally path, since CPython installs no SIGTERM handler.
    - id: R-2
      check: which commit is right about the results-JSON write behaviour
      result: >-
        BOTH SENTENCES ARE TRUE OF THE SOURCE; THEY ARE ABOUT DIFFERENT CELLS. The
        dispatch commit's "rewritten after each cell so a kill mid-run still leaves
        the completed cell recorded" is literally accurate about a cell that RETURNS,
        and was borne out twice - cell 75's record survived both kills, which is the
        only reason the ERROR is known to reproduce. The snapshot commit's "writes
        its results JSON only AFTER worker_main_cell RETURNS (line 112, inside the
        per-cell loop) ... a killed cell leaves NO RECORD AT ALL" is literally
        accurate about the KILLED cell, and its line reference is exact. They do not
        contradict. The earlier sentence was INCOMPLETE rather than false - silent on
        the killed cell while phrased so as to invite the reading that a mid-run kill
        leaves a usable record. THE RETRACTION IS CORRECTLY STATED and is if anything
        harder on the earlier wording than the source requires.
      residual: dispatch_queue.json is byte-identical between 2fe7dfeb and e17d95cb,
        so the un-retracted sentence still stands verbatim at
        tasks[0].artifact_paths_note at the snapshot commit. The correction lives
        only in a commit message.
    - id: R-3a
      check: '"reused VERBATIM ... THE ONE DELIBERATE DEPARTURE" - tours'
      result: >-
        UNDECLARED DEPARTURE. Predecessor - bkz(par, tracer=True) plus a count of
        bkz.trace children labelled "tour". This runner - bkz(par) with no tracer
        (line 73) and getattr(bkz, "tours", None) (line 75). Neither
        fpylll.algorithms.bkz nor bkz2 ever assigns a `tours` attribute (0
        occurrences of the string in either module). Measured after a real BKZ call
        in this container - hasattr(bkz,'tours') False, getattr(...) None. A
        COMPLETED cell would have recorded the JSON field `tours` as null. The gate
        item naming `tours` was unsatisfiable from the moment the runner was pinned.
    - id: R-3b
      check: '"reused VERBATIM" - root-Hermite factor'
      result: UNDECLARED DEPARTURE. Predecessor computed the standard delta_0 from
        the GSO log-determinant; this runner computes a different, dimensionally
        incorrect quantity (see M-6) under the same field name, which would also not
        be comparable with the predecessor's delta_0_root_hermite_factor.
    - id: R-3c
      check: '"reused VERBATIM" - traceback'
      result: >-
        UNDECLARED DEPARTURE. Predecessor stored traceback.format_exc(); this
        runner stores only the exception type and message (line 82,
        f-string "{type(exc).__name__}" followed by the message). Consequence - the archived
        artifacts bracket the exception only to the interval between the
        LLL.Reduction(M,...) construction and the return of bkz(par), because
        gso_float_type_used (line 65) is present and bkz_elapsed_seconds (line 74) is
        absent. That interval still includes BKZ.Param(...) and the pre-tour
        self.lll_obj(). The report's "BKZ.Param did NOT raise" is SUPPORTED, but by
        the error TYPE (ReductionError, not the RuntimeError "Cannot open strategies
        file." reproduced twice in instrument_readiness_20260824.md), not by a
        traceback. Localisation to a TOUR is NOT supported by this batch's artifacts;
        the predecessor's nine-frame traceback (ending at bkz.py:186
        self.lll_obj(lll_start, lll_start, kappa + block_size) inside a doubly-nested
        svp_preprocessing within tour) does localise it, and is corroborating context
        from another run on another host, not this run's evidence.
    - id: R-4
      check: is the executed unit "ONE FULL BKZ TOUR" as the card, objective and
        uncertainty_reduced all state
      result: NO. Measured in this container - BKZ.Param(block_size=55,
        flags=BKZ.AUTO_ABORT).max_loops == 0 and flags & BKZ.MAX_LOOPS is false;
        BKZReduction.__call__ loops `while True` over tours, breaking only on clean,
        block_size >= M.d, auto-abort, MAX_LOOPS or MAX_TIME. The executed unit is a
        full BKZ reduction of unbounded tour count. The wording is inherited from
        GOAL-MLKEM-005.next_action and DEC-20260815-3e8e9c, so it is a standing
        description defect rather than an executor deviation; it matters because any
        per-cell figure would be a per-reduction cost, and with tours unrecordable
        (R-3a) the record could never say how many tours were bought.

  matched_pair_determination:
    verdict: MATCHED BY DESIGN; UNVERIFIABLE AS RUN; AND WITHOUT A BASELINE EVEN IN
      PRINCIPLE
    holds:
      - id: D-1
        property: same basis in both cells
        basis: verified by execution, not assumed. The runner re-seeds inside each
          cell (line 53) before generating (line 58). In one process at the declared
          interpreter, with intervening RNG consumption and precision changes, all
          generated d=512 qary bases were identical - row-serialised sha256
          a5ec1e4d4713b7e23a6e91df7350a744a3dcb8d22cc05fcc702b505a4cd7df26, including
          at set_precision(100). (My own serialisation, offered as a fingerprint the
          runner should have recorded; not a producer artifact.)
      - id: D-2
        property: same pre-GSO stage precision in both cells
        basis: measured - this container's process-start FPLLL precision is 53
          (set_precision(53) returns 53), and the runner's finally block (line 86)
          restores 53 on both the success and the exception path. So cell 2's
          IntegerMatrix.random and outer LLL ran at exactly cell 1's precision. This
          is the one place the design could have silently broken and it does not.
      - id: D-3
        property: same strategies bytes, one invocation, one container
        basis: STRATEGIES is a module constant; both cells run in one main() in one
          process under one timeout invocation; the file hashes to the pinned value.
    does_not_hold:
      - id: D-4
        finding: THE PAIR IS UNOBSERVED ON ONE SIDE. D-1..D-3 are properties of the
          PROGRAM, established from the pinned source and my re-execution of its
          preamble. The 100-bit cell wrote no record, so its seed, strategies hash,
          GSO float type, basis and status are unobserved. Nothing is filled in. The
          batch's uncertainty_reduced ("how its cost compares to the SAME basis at
          mpfr_bits=75") is not reduced at all.
      - id: D-5
        finding: cell ORDER is an uncontrolled confound. 75 always runs first, never
          counterbalanced, never repeated within a process, so any cross-cell
          wall-clock difference would confound precision with position (allocator and
          page-cache warmth, load, thermal state). Bounded at about 3% by M-4. Costs
          nothing here; a successor measuring a cost ratio should alternate order
          across runs or run each cell in its own process.
      - id: D-6
        finding: NO BASELINE EVEN IN PRINCIPLE, AND THIS WAS KNOWABLE BEFORE
          DISPATCH. The 75-bit cell is labelled "REFERENCE (the contrast)" and
          produced a time-to-failure (3051.823137998581 s), not a cost. On the
          committed predecessor record the same cell with the same seed already had
          status "ERROR" with the identical error string at 2502.7416553497314 s,
          n_cells_completed 0, and DEC-20260815-3e8e9c states it in terms and records
          that the predecessor's Validator reproduced that failure on a second host.
          Neither task_card.yaml nor instrument_readiness_20260824.md nor
          DEC-20260824-526f89 states that the 75-bit cell had already failed
          identically; all describe 2502.74 s as what the cell "cost". A
          contract-fidelity finding against the DISPATCH, not against the executor,
          who ran the pinned card exactly and retuned nothing.

  control_checks:
    - id: C-1
      control: positive/negative controls against the frozen contract
      result: INCOMPLETE, not failed - the batch declares no separate control; its
        control structure IS the pair, and half of it produced nothing
    - id: C-2
      control: DEC-20260815-3e8e9c binding condition (i), RT-CTRL-2 zero-compute
        instrument fixes "BEFORE ANY FURTHER CAPPED RUN"
      result: NOT IMPLEMENTED, AND ITS ABSENCE COST THIS BATCH ITS ONLY REMAINING
        RESULT. Checked against the pinned runner - no signal handler, no per-tour
        flush, no use of bkz.trace at all, no psutil, no cpu_times(), no
        environment.json, no load average. DEC-20260824-526f89 does not mention the
        condition, does not implement it, and records no deviation. Measured
        consequence - the 100-bit cell ran 14449 s and the machine-readable record
        learned one bit ("> 14449 s"), the identical loss the condition was written
        to prevent, at essentially the identical magnitude, one batch later. The
        snapshot commit independently identifies the defect and prescribes a STARTED
        stub; the stub is necessary but WEAKER than condition (i), which asked for
        per-tour progress. A finding against the dispatch, not the executor.
    - id: C-3
      control: condition (ii), dual-mark reporting at 3600 s and 14400 s
      result: DISCHARGED - both marks reported with cell state at each (arithmetic
        inherits the 4030 s figure corrected in M-2)
    - id: C-4
      control: condition (v), preserve every artifact of every execution including an
        infrastructure-killed one
      result: DISCHARGED IN SUBSTANCE - attempt 1's results JSON, stdout, stderr,
        start and kill timestamps are all archived and receipt-bound. The literal
        `failed_infrastructure` LABEL is not used; the *.attempt1_killed.* convention
        plus execution_report.md Deviations 1 and 3 carry the same information and
        the deviation is disclosed. This is the condition whose violation in the
        predecessor batch produced an unverifiable corroboration claim; it was not
        repeated.
    - id: C-5
      control: condition (iii), near-free rider of two further draws
      result: NOT TAKEN - explicitly non-mandatory. No finding.
    - id: C-6
      control: condition (iv), scope
      result: RESPECTED - no (512,40) re-attempt, no d=256, no CTRL-3 full-tour
        precision search, no Stage 1, no >=8-draw grid, no Branch-B substitute
    - id: C-7
      control: null-object control (docs/inventor-protocol.md section 3)
      result: NOT APPLICABLE to this batch's output - it reports one exception and
        one non-measurement, no correlation, bias or excess, so there is no
        statistical signal for a null object to falsify and its absence is not a
        defect. Two related facts recorded rather than skipped - (1) THE OBJECT UNDER
        TEST ALREADY IS THE NULL OBJECT (a structureless random q-ary lattice; see
        DEC-20260815-3e8e9c on RT-CTRL-3(i)), so everything measured is a property of
        fpylll 0.6.4's mpfr path on generic bases, and the ML-KEM-shaped nearby-object
        control RT-CTRL-3(ii) has never been run in this goal; (2) THE DECAY QUESTION
        - does the failure decay as mpfr precision, the parameter meant to destroy
        it, increases - is exactly what the 100-bit cell was for, and it RETURNED NO
        DATA, so it remains open at tour level. The only decay evidence in the goal
        is at the isolated-step level, which KN-FIND-f54a82 holds is not evidence
        about the full tour.

  cost_model_checks:
    - id: CM-1
      check: the batch's only cost statement
      result: BUILT ON A FAILURE TIME. budget_justification reads "The predecessor's
        75-bit cell at this basis cost 2502.74 s. Two cells put the expectation near
        5000 s." Verified against the source - 2502.7416553497314 s is
        subprocess_wall_clock_seconds for a cell whose status is "ERROR", in a run
        with n_cells_completed 0; DEC-20260815-3e8e9c calls it "a FAILURE cost".
        Using it to forecast a batch whose second cell had never terminated at any
        precision undersized the run - the 100-bit cell alone ran 14449 s. The
        21600 s ceiling was correctly described as a hard ceiling, not a forecast,
        and it is what ended the task.
    - id: CM-2
      check: total expected cost as per-attempt cost x inverse success probability
      result: CORRECTLY ABSENT. No success probability exists - the completed-cell
        count at (d=512, beta=55) is 0 across the predecessor run, its independent
        re-execution on a second host, and both attempts here. The producer computes
        none, the receipt asserts none, and I compute none.
    - id: CM-3
      check: memory reported alongside time
      result: PROSE ONLY - "Peak observed RSS ~175 MB (single-threaded, ~100% of one
        core)", PID 24314. No machine-readable resource record anywhere - no
        peak_rss_mb field (the predecessor's results JSON had one), no CPU time, no
        load average, no environment.json. AGENTS.md "Artifact policy" lists resource
        measurements among required retained artifacts. Same gap as C-2.
    - id: CM-4
      check: cost-table unit declaration
      result: NOT APPLICABLE - no concrete cost table exists in this batch

  heuristic_validation_checks:
    - result: NOT APPLICABLE - this batch validates no numbered heuristic,
        pre-registers no theoretical distribution, reports no empirical CDF or tail
        statistic, and uses no substitute-sampling correspondence

  validation_ladder_checks:
    - id: L-0
      result: NO speedup, ratio or complexity improvement is claimed anywhere in this
        batch, so section 6 step 2 does not fire and its absence is not a `failed`
    - id: L-1
      step: isolate each assumption and measure it separately
      result: exercised by the goal, not by this batch - the isolated-step bisection
        is the predecessor's, and KN-FIND-f54a82 states it does not transfer to the
        full tour
    - id: L-2
      step: whole pipeline on a scaled-down instance, measured ratio, negative cases
      result: NOT APPLICABLE - no baseline and no improvement to ratio against
    - id: L-3
      step: real object with named cheats
      result: NOT APPLICABLE
    - id: L-4
      step: reproducibility pointer exercised rather than asserted
      result: PARTIALLY EXERCISED BY ME, listed not asserted. Rebuilt from scratch at
        the declared interpreter - the seed (452658293, plus 2074339090 and
        915347894), the container's process-start FPLLL precision (53), the generated
        basis fingerprint, the absence of a `tours` attribute after a real BKZ call,
        the BKZ.Param loop defaults, and the root-Hermite-factor arithmetic. NOT
        rebuilt - either lattice cell (cell 75 costs ~3050 s, cell 100 is unbounded);
        re-running the producer's experiment is not a validator act.

  proof_architecture_checks:
    - result: NOT APPLICABLE - this is an instrument control run, not a
        proof-oriented task; no proof_search_map is carried and none is due

  scope_checks:
    - id: S-1
      result: PASS - toy scale stated correctly in the execution report, the receipt
        and both commit messages. Tested scope - d=512, beta=55, q=3329,
        IntegerMatrix.random(d,"qary",k=d//2,q=3329), seed 452658293, fpylll 0.6.4,
        Python 3.11.15, one container, one host, 4 CPUs / 16075 MiB. NOTHING HERE IS
        A STATEMENT ABOUT ML-KEM AT ANY FIPS 203 PARAMETER SET and no transfer is
        asserted.
    - id: S-2
      result: PASS in both directions. Attempt 1's runtime kill at 4049 s (far inside
        the 21600 s ceiling) and attempt 2's EXIT_RC=124 at the timeout cap are
        infrastructure and resource events, are not negative mathematical evidence,
        and are treated as such by the producer, the receipt, both commit messages
        and this report. Conversely the 75-bit ERROR is NOT an infrastructure event -
        it is an exception raised by a run that terminated on its own more than
        18000 s inside its cap, reproduced across two independent attempts here and,
        on the committed record, on a different host in the predecessor batch.
        Nothing was retuned in response to it and the runner blob is unchanged in git.

  verdict: incomplete

  verdict_reasoning: >-
    Not `passed` - the producer's own completion-gate item 1 fails on its face,
    three of six gate items are checkable on only one of two cells, two metrics the
    gate names were unrecordable by the pinned runner even on success, and the
    designed contrast has no data on one side and no baseline on the other. Not
    `failed` - the reason cell 100 has no record is a wall-clock cap plus a runner
    recording defect, an infrastructure and instrument outcome, which under AGENTS.md
    core rule 5 / CLAUDE.md rule 3 is never negative evidence. Not `invalid` -
    nothing in the record is unsound, fabricated, hand-edited or out of declared
    scope; the receipt is exact, raw and summary agree, seed and strategies bytes
    verify independently, and the one cell that terminated is admissible evidence of
    exactly what it says.

  what_this_verdict_does_not_do: >-
    It supports no ECDLP or ML-KEM claim, demonstrates and refutes no precision
    effect at tour level, authorizes no promotion, and does not license reading the
    100-bit cell's 14449 s as a cost.

  limitations:
    - I re-ran neither lattice cell. Cell 75 costs ~3050 s and cell 100 is unbounded,
      and re-running the producer's experiment is not a validator act.
    - The matched-pair property for the 100-bit cell is established from the pinned
      source plus my re-execution of its preamble. It is NOT an observation of the
      run, because the run produced no record for that cell.
    - My basis fingerprint
      (a5ec1e4d4713b7e23a6e91df7350a744a3dcb8d22cc05fcc702b505a4cd7df26) is my own
      row serialisation of a freshly generated basis, not a producer artifact and not
      an fplll-canonical digest.
    - The predecessor's traceback localising the failure inside a tour is context
      from a different run on a different host. It is not this run's evidence and
      must not be reported as such.
    - I read four paths outside my declared read_scope, all committed and all
      read-only, and they are listed in sources_read. No sibling review report exists
      at this commit (the batch's reviews/ directory did not exist before I created
      my own), so read_sibling_reports is false as a matter of fact and not only of
      intent.
    - INDEPENDENCE IS PROCEDURAL AND NOT MODEL-LEVEL. Fresh session; I did not
      produce, run, or archive any of the work reviewed. But the producer, the
      Coordinator and I are recorded as the same model family (claude-opus-5).
      AGENTS.md rule 12 is UNMET AND UNWAIVED for this batch. Any agreement between
      this report and the snapshot commit's own self-assessment is correlated
      same-model judgement and must not be counted as corroboration.
    - model_verified is FALSE. No adapter probe receipt exists for this session and
      AUTORESEARCH_POLICY and AUTORESEARCH_BACKEND are both unset (checked, not
      assumed).

  inference_provenance:
    requested_policy: review-adversarial
    serving_model_as_reported_by_the_runtime: claude-opus-5
    runtime: claude_code, subagent `validator`
    reasoning_effort: xhigh
    reasoning_effort_basis: >-
      the `effort` key of .claude/agents/validator.md, whose value is xhigh, derived
      from orchestration/roles.yaml role validator -> default_policy
      review-adversarial -> reasoning_effort in orchestration/model-policies.yaml.
      Honoured by the runtime binding rather than asserted by me.
    fallback_used: false
    fallback_allowed: false
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: no `orchestration.adapter doctor --probe` receipt exists
      for this session; AUTORESEARCH_POLICY and AUTORESEARCH_BACKEND are unset
    independent_session: true
    attestations_recorded: NONE. I obtained no attestation from any model or session
      and I record none.

  review_attestation:
    joints_owned:
      - receipt and artifact integrity at the snapshot commit
      - the producer's completion gate, item by item
      - seed, strategies-bytes, and GSO float-type fidelity
      - whether the pinned runner could have produced the extant records
      - whether the matched pair is genuinely matched
      - the Coordinator's write-after-return claim across the two commits
    read_sibling_reports: false
    sibling_reports_note: no sibling review exists at e17d95cb; the batch's reviews/
      directory did not exist until I created my own task directory under it. The
      Red Team task TASK-20260824-6fc282 had produced nothing readable.
    blind_from_respected: not applicable - this task carries no
      blind_rederivation.blind_from
    sources_read:
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/dispatch_queue.json
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/archives/TASK-20260824-c7248f/receipt.yaml
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/task_card.yaml
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/execution_report.md
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair.py
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair_results.json
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/rt_ctrl_1_matched_pair_results.attempt1_killed.json
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/inputs/fplll_strategies_default.json
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stdout.log
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stdout.attempt1_killed.log
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stderr.log
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/stderr.attempt1_killed.log
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/run_start_utc.txt
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/run_end_utc.txt
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/run_start_utc.attempt1_killed.txt
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/killed_at_utc.attempt1.txt
      - coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/TASK-20260824-b3e9da/exit_rc.txt
      - coordination/goals/GOAL-MLKEM-005/instrument_readiness_20260824.md
      - ledger/decisions/DEC-20260824-526f89.yaml
      - ledger/decisions/DEC-20260815-3e8e9c.yaml
      - knowledge/findings/KN-FIND-f54a82.md
      - AGENTS.md
      - agents/validator.md
      - docs/inventor-protocol.md (section 6 only)
      - 'git commit messages of e17d95cb and 2fe7dfeb'
      - 'OUTSIDE DECLARED read_scope, disclosed - coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/tasks/TASK-20260815-f14d3c/stage0_d512_beta5570_precision_bisection_and_reattempt.py'
      - 'OUTSIDE DECLARED read_scope, disclosed - coordination/goals/GOAL-MLKEM-005/batches/BATCH-0d5018/tasks/TASK-20260815-f14d3c/main_grid_d512_beta5570_reattempt_results.json'
      - 'OUTSIDE DECLARED read_scope, disclosed - installed fpylll 0.6.4 sources (fpylll/algorithms/bkz.py, bkz2.py) at the declared interpreter'
    code_executed_by_me:
      - sha256 recomputation of all 15 receipt-declared paths from git blobs and disk
      - seed re-derivation from numpy default_rng at the declared interpreter
      - basis-identity test across re-seeding, RNG consumption and precision changes
      - process-start FPLLL precision measurement
      - a real small BKZ run to test getattr(bkz,'tours',None) and BKZ.Param defaults
      - root-Hermite-factor formula comparison at d=80 on a reduced basis
      - timestamp and ratio arithmetic
    no_producer_artifact_or_ledger_record_was_changed: true
    committed_anything: false
    verdict: incomplete

  artifact_paths:
    - /home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/reviews/TASK-20260824-bc488d/review.md
```
