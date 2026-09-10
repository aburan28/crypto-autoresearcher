# Defect localization — TASK-20260819-e076f1 (BATCH-f85613, GOAL-SSI-001)

Independent Executor session. I opened all three files batch.yaml names, myself,
before writing anything below, and re-derived the corrected law from the paper's
own stated interpolation law rather than copying CORR-20260808-c792f8's formula
on trust (it is also cross-checked, separately, below).

**No file under `experiments/EXP-WESOVOW-001/` was modified by this task.**
Check run: `git status --porcelain -- experiments/EXP-WESOVOW-001/` returned
empty both before and after this task's work (only files under this task's own
`coordination/goals/.../tasks/TASK-20260819-e076f1/` write scope were created).

## 1. What `batch.yaml`'s `coordinator_reading_to_be_independently_rechecked` claims, quoted verbatim

> "In experiments/EXP-WESOVOW-001/cost_model.py the documentation string at
> line 236 reads T_full / sqrt(min(w, M)) and the computation at line 270
> reads log2Tw = log2Tfull - 0.5 * min(lw, log2M) + overhead_bits, which
> decreases time as memory decreases. In
> experiments/EXP-WESOVOW-001/specification.yaml the declared crossover
> metric reads w* = (T_full * 2^{c*sqrt(log2 p)} / T_DG)^2 capped by M, and
> controls C3 and C4 require T(w) to equal T_full for w at or above M. In
> experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/execution_report.yaml the
> control block records C4_vow_asymptote as PASS by construction against a
> formula written there as T_full * min(1, sqrt(M/w)) ..."

## 2. My own independent read of each of the three files, today

### 2a. `experiments/EXP-WESOVOW-001/cost_model.py` — **DISAGREE. The Coordinator's reading is stale, not current.**

I read the file fresh (`sed -n '235,240p'` and `'268,290p'` on the working
tree, matching my full earlier `Read` of the file). What is actually there
today:

```
238:                "log2Tfull": "log2M - log2P0",
239:                "T_w_vOW": "T(w) = T_full * sqrt(M / min(w, M))",
240:                "T_DG_baseline": "p^{1/2} = 2^{log2p/2}",
```

```
268:        vow = {}
269:        for lw in MEMORY_BUDGETS:
270:            entry = {}
271:            for c in OVERHEAD_C:
272:                overhead_bits = c * math.sqrt(b2p)
273:                log2Tw = (log2Tfull
274:                          + 0.5 * max(0.0, log2M - lw)
275:                          + overhead_bits)
276:                log2speedup = log2TDG - log2Tw
```

```
286:        crossovers = {}
287:        for c in OVERHEAD_C:
288:            overhead_bits = c * math.sqrt(b2p)
289:            log2w_star = log2M + 2.0 * (log2Tfull + overhead_bits - log2TDG)
290:            feasible = bool(log2w_star <= log2M)
```

Line 236 is `"log2Tfull": "log2M - log2P0",` — a different formula entirely
(this is `log2Tfull`'s own documentation, one line before `T_w_vOW`, not
`T_w_vOW` itself). Line 270 is `entry = {}` — a dict literal, not the vOW
computation. Neither the doc string `"T_full / sqrt(min(w, M))"` nor the
computation `log2Tfull - 0.5 * min(lw, log2M) + overhead_bits` that
`batch.yaml` quotes is present anywhere in the file I read. **The file
currently commits the CORRECTED law** — `T(w) = T_full * sqrt(M / min(w,M))`,
i.e. `log2Tw = log2Tfull + 0.5*max(0, log2M - lw) + overhead_bits` — and its
crossover formula `log2w_star = log2M + 2*(log2Tfull + overhead_bits -
log2TDG)` **already includes the `log2M` term** that `specification.yaml`'s
own metric line omits (see 2b).

**This is not a disagreement about interpretation; it is a disagreement about
what the file contains.** I traced why with `git log -p -- experiments/EXP-WESOVOW-001/cost_model.py`:

```
commit 7d188a7c38e1d44b46796fe97b34fe4118628216
Date:   Sat Aug 8 23:45:42 2026 -0700
    archive TASK-20260809-981821 EXP-WESOVOW-001 RUN-WESOVOW-201692-001 corrected run snapshot

 experiments/EXP-WESOVOW-001/cost_model.py          |   17 +-
 .../runs/RUN-WESOVOW-201692-001/...(9 new files)...
```//
The diff at that commit shows exactly:
```
-                "T_w_vOW": "T_full / sqrt(min(w, M))",
+                "T_w_vOW": "T(w) = T_full * sqrt(M / min(w, M))",
-                log2Tw = log2Tfull - 0.5 * min(lw, log2M) + overhead_bits
+                log2Tw = (log2Tfull
+                          + 0.5 * max(0.0, log2M - lw)
+                          + overhead_bits)
```

**The exact lines `batch.yaml` quotes are the PRE-fix lines that this commit
replaced ten days before `batch.yaml` was authored (2026-08-19).** I confirmed
this is not an in-place edit of a frozen artifact done carelessly: it is a
properly authorized amendment. `ledger/decisions/DEC-20260809-c1066f.yaml`
(`goal_id: GOAL-SSI-001`, `batch_id: BATCH-2e6130`) records
`protocol_amendment_task: TASK-20260809-ef3e58` and states it "Accept[s] the
corrected source and RUN-WESOVOW-201692-001 as a validated ... amendment,
snapshot-archived the corrected source, ran exactly one [invocation] ...
changes no hypothesis status, makes no cryptanalytic claim." A new run,
`RUN-WESOVOW-201692-001`, was archived under the same experiment id with its
own `execution_report.yaml` stating `protocol.amendment: TASK-20260809-ef3e58`,
`amendment_version: 2`, and the identical corrected formulas quoted above
(`log2_formula: "log2T(w) = log2Tfull + 0.5*max(0, log2M - log2w) +
overhead_bits"`, `crossover_formula: "log2(w_star) = log2(M) +
2*(log2(T_full) + overhead_bits - log2(T_DG))"`).

**Consequence for this task's premise.** `batch.yaml`'s own selection
rationale (rank 1) states the defect is "still uncorrected at its source" as
of 2026-08-19. That statement is **false as of today's tree**: the shared
`cost_model.py` source was corrected in place on 2026-08-08/09, ten days
earlier, under a recorded protocol amendment and a superseding run
(`RUN-WESOVOW-201692-001`), with a Coordinator decision (`DEC-20260809-c1066f`)
accepting it. I did not go further upstream than reading that one decision
record and the amendment task's directory listing (both cited above) — I did
not open the full amendment task, its review, or `EV-SSI-4b17e7` /
`EV-SSI-5d954c`, which are outside this task's read/write scope and are not
needed to establish the fact that the file changed and why. **This
discrepancy between `batch.yaml`'s premise and the current tree state is the
single most important finding of this task and should be reconciled by the
Coordinator before any further work is queued against "the uncorrected
`cost_model.py`."**

A second, independent consequence: **`experiments/EXP-WESOVOW-001/specification.yaml`
is still `version: 1` with no amendment reference and `required_artifacts`
naming only `runs/RUN-WESOVOW-001/*`.** `cost_model.py` is a single shared
file, not a per-run copy, and it was mutated after `RUN-WESOVOW-001` was
produced (`git log` timestamps: `RUN-WESOVOW-001` ran at commit `cf82d44f...`
on 2026-07-25 per its own `manifest.yaml`; the fix landed 2026-08-08/09).
**The `cost_model.py` file now in the tree cannot reproduce
`RUN-WESOVOW-001/raw-result.json`** (verified quantitatively in
`control_report.md` RG-1). `RUN-WESOVOW-001`'s own `required_artifacts` list
still asserts `cost_model.py` as its source, which is no longer true of the
working tree's `cost_model.py`, only of the historical commit `cf82d44f...`.
This is a reproducibility break independent of, and prior to, the anchor-math
question: **a required artifact of an immutable run was edited in place**, and
whether that was itself proper (it was authorized by `TASK-20260809-ef3e58`
for the *new* run `RUN-WESOVOW-201692-001`, per `DEC-20260809-c1066f`) does
not restore `RUN-WESOVOW-001`'s own reproducibility from the artifact its own
manifest still names.

### 2b. `experiments/EXP-WESOVOW-001/specification.yaml` — **AGREE, verified myself.**

Lines 39-41, read directly:

```
39:  - crossover memory log2(w*) per (p, overhead c), analytic: w* = (T_full * 2^{c*sqrt(log2
40:      p)} / T_DG)^2, capped by M
```

This literal formula (in linear, non-log form) omits the memory-anchor factor
entirely: solving it for `log2(w*)` gives `2*(log2Tfull + overhead_bits -
log2TDG)` with **no `log2M` term** — which is exactly the (wrong) `as_run`
crossover this task's `corrected_charging.py` reproduces bit-for-bit against
`RUN-WESOVOW-001/raw-result.json` (see `control_report.md` RG-1). The frozen
specification's own declared crossover metric is the buggy one; the currently
corrected `cost_model.py` code (2a) has since diverged from its own frozen
specification's stated metric without a recorded `protocol_amendment` to
`specification.yaml` itself. `batch.yaml`'s quotation of this line is
accurate.

Controls C3 (line 145-147) and C4 (line 148-149), read directly:

```
145:  - id: C3-monotonicity
146:    description: T(w) must be non-increasing in memory budget w for every (p, overhead) scenario;
147:      T(w) must equal T_full for w >= M.
148:  - id: C4-vow-asymptote
149:    description: At w = M, vOW time must equal T_full exactly (cap check).
```

`batch.yaml`'s paraphrase ("controls C3 and C4 require T(w) to equal T_full
for w at or above M") is accurate.

### 2c. `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/execution_report.yaml` — **AGREE, verified myself.**

Line 33 and line 53, read directly:

```
33:  model: "T(w) = T_full / sqrt(min(w, M)) F_{p^2}-ops; baseline T_DG = p^{1/2}"
...
53:  C4_vow_asymptote: "PASS (by construction) - T(w) = T_full * min(1, sqrt(M/w)); cap formula verified; note all tested budgets 2^30..2^80 are below M (>= 2^93.3), so the cap branch is not exercised by the tested grid"
```

Both quotations in `batch.yaml` are accurate. Note the internal inconsistency
this exposes, independent of anything `batch.yaml` says: **line 33's `model`
field states the law as `T_full / sqrt(min(w, M))`** (the buggy, as-run law,
matching `raw-result.json`'s own `model.formulas.T_w_vOW` field and the actual
numbers in the `van_oorschot_wiener` block) **while line 53's C4 justification
states a different formula, `T_full * min(1, sqrt(M/w))`** (algebraically
equal to the *corrected* law, `T_full*sqrt(M/min(w,M))`, not the one that
actually ran). **The run's own execution report describes two different,
inconsistent charging laws for the same run**, and the one used to justify a
PASS verdict on C4 is not the one that actually executed. See
`control_report.md` for whether that PASS is capable of failing.

## 3. Verdict: where and how the law is mis-anchored

The defect that produced `RUN-WESOVOW-001` (frozen, immutable, still the
object of the citation prohibitions this batch restates) is:

```
as_run (buggy):    log2T(w) = log2Tfull - 0.5*min(log2w, log2M) + overhead_bits
as_run crossover:  log2w*   = 2*(log2Tfull + overhead_bits - log2TDG)
```

This takes `0.5 * min(log2w, log2M)` — a bare memory-COUNT term — and
*subtracts* it from `log2Tfull`, so **T(w) decreases as memory shrinks below
M**, the opposite of every time-memory tradeoff sense, and does not reduce to
`T_full` at `w = M` in general (it reduces to `log2Tfull - 0.5*log2M`). This
is exactly the defect class `CORR-20260808-c792f8` and the red-team report at
`coordination/goals/GOAL-SSI-001/batches/BATCH-b3c87f/reviews/
TASK-20260806-9536f4/red_team_report.md` §4 attribute to `cost_model.py` line
236 (in the commit that produced `RUN-WESOVOW-001`, before the 2026-08-08/09
fix) — I independently confirm it reproduces `RUN-WESOVOW-001`'s committed
`van_oorschot_wiener` numbers to **exact bit-for-bit agreement (max abs diff =
0.0)**, see `control_report.md` RG-1/RG-3.

The corrected law — independently re-derived here from the paper's own stated
interpolation law (`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` l.39, as
quoted in the red-team report: *"time essentially sqrt(N^3/w) =
p^{1/2+o(1)}/w^{1/2}"*, i.e. `T(w) = T_full * sqrt(M/w)` for `w <= M` and
`T(w) = T_full` for `w >= M`) — is:

```
corrected:            log2T(w) = log2Tfull + 0.5*max(0, log2M - log2w) + overhead_bits
corrected crossover:  log2w*   = log2M + 2*(log2Tfull + overhead_bits - log2TDG)
```

**This is, independently, exactly the formula already sitting in the current
`cost_model.py` source (2a)** and exactly the formula `CORR-20260808-c792f8`
uses. Three independent derivations (this task's from the paper's stated law;
`CORR-20260808-c792f8`'s; and the already-committed `RUN-WESOVOW-201692-001`
amendment's) agree to machine precision — see `control_report.md` and
`anchor_sensitivity.md` for the numeric cross-checks.

## 4. Is a control that reports PASS even capable of failing?

**Yes for C4, and the run's own record is wrong about which formula it
verified.** Evaluated at `w` exactly equal to `M` (all five field sizes, both
anchors, `c=0`):

- Under the **as-run law that actually produced `RUN-WESOVOW-001`**, `T(w=M) =
  T_full - 0.5*log2M ≠ T_full` at **every one of the five field sizes**
  (`log2M` ranges ≈93 to ≈269 bits, so the discrepancy at the cap is 46 to 135
  bits, not the promised exact equality). **C4 would FAIL if evaluated at
  `w=M` under the law that actually ran.** It did not fail only because, as
  the run's own note says, "the cap branch is not exercised by the tested
  grid" (max tested `w = 2^80 < M` at every field size) — i.e. **C4's PASS
  verdict is vacuous, not a verification of the cap property**, exactly the
  `KN-TECH-1a5b7e` control-cannot-fail pattern the cited red-team report names
  for the sibling contract `EXP-SSI-697354`.
- Under the **corrected law**, `T(w=M) = T_full` exactly (`max(0, log2M -
  log2M) = 0`) at all five field sizes, by construction — this direction is
  correct but is now an algebraic identity of the formula, not a
  discriminating check either.
- Full numeric evidence: `control_report.md` §RG-2.

C3 (monotonicity) is similarly incapable of failing under either law: `min(lw,
log2M)` is non-decreasing in `lw`, so the as-run law's `T(w)` is non-increasing
in `w` by construction regardless of whether the anchor is right — C3 checks
slope, not level, and cannot see this defect, matching the red-team report's
general finding for the sibling contract's `MONO-*` controls.

## 5. Absence-claim discipline

I claim above that the exact strings `batch.yaml` quotes from `cost_model.py`
("`T_full / sqrt(min(w, M))`" as the current doc string at "line 236", and
"`log2Tw = log2Tfull - 0.5 * min(lw, log2M) + overhead_bits`" as the current
computation at "line 270") are **not present in the file as it stands today**.
Search performed: (1) `sed -n` printing the literal lines 235-240 and 268-290
of the working-tree file (shown in §2a above — line 236 and line 270 contain
different text); (2) `grep -n` for the literal substring `T_full / sqrt(min`
and for `- 0.5 \* min(lw` across
`experiments/EXP-WESOVOW-001/cost_model.py` returned zero matches in the
working tree (both patterns match only inside
`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json` and
`.../execution_report.yaml`, which are the frozen, historical run records, not
the current source file).
