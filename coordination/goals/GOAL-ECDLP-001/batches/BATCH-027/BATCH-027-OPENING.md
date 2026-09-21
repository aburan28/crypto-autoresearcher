# BATCH-027 OPENING — RUN THE MEASUREMENT

**Goal:** GOAL-ECDLP-001 · **Sub-goal:** SG-ECDLP-001 · **Question:** RQ-ECDLP-002
**Opened by:** DEC-20260801-013 (2026-08-01), which in the same record **closes
BATCH-026 as a NON-EXECUTION** for the measurement arm.
**Queue:** `coordination/goals/GOAL-ECDLP-001/batches/BATCH-027/dispatch_queue.json`
**Tasks:** TASK-20260801-075 … TASK-20260801-083 (nine cards) · **max_concurrent:** 3
**Goal status:** `active`. BATCH-027 is the **twenty-seventh** batch against
`campaign_budget.maximum_batches = 50`, so **no pause condition fires** — stated
explicitly rather than left implicit.

---

## 1. BATCH-026 closes as a non-execution, and it was not a research failure

`RUN-LPF-001-measure` **was not executed**. TASK-20260801-069 recorded
**APPROVAL_DETERMINATION: NOT APPROVED**. TASK-20260801-070 through
TASK-20260801-074 stand terminal `blocked`. **No evidence record exists because
no measurement run exists** — EV-LPF-001 was never written and its id is still
free, and **H-LPF-001 remains `specified`**. The close is recorded by goal-record
amendment at this opening: the BATCH-014/015, BATCH-022/023, BATCH-024/025 and
BATCH-025/026 precedent.

**This is the third consecutive non-execution and the reason matters.** It was a
**record-integrity gate**, not a mathematical result about H-LPF-001 or HEUR-DS-1
in either direction, and not an infrastructure failure — nothing timed out,
nothing crashed, no budget was exhausted.

### RTB-068 PASSED on the substance, and none of it is rebuilt

| what was checked | outcome |
|---|---|
| four-change cap | **held** — 34 paths removed, 313 added, 49 changed, **no fifth change**; bands, spreads, all six branch conditions, cut 4, `[0.125, 8.0]`, `u_star_formula`, both ladders, both Bsm ladders, both strikes, the D9 strike, the decidability map and every prior ruling byte- or semantically identical |
| mechanical regeneration | **re-run, not re-read** — 210/210 flags regenerated, 28/28 `moving_rungs` lists reproduced |
| ROUGH `Z < 2` derivation | **verified from source AND by execution** — `build_rough_replacement` run on **10,664** fresh inputs including 2,672 at the edge of the admissible range, **zero violations**, max Z 1.9906 |
| dependence on an unstable maximum | **none** — mutation-tested clause by clause |
| attainability | **re-run from scratch** — 17 certified ladders, all with a true top-rung flag, **L-1's second leg FALSE**, L-2/L-3/L-4 demonstrated-reachable, every aggregating leg's false-fire ≤ 0.02 |
| anti-tuning direction tell | **favourable** — two of three corrections go **against** the experiment, and the third (DIFF-3, +1.5724157930250209) is *precisely the one a selective repairer would have omitted* |

**Net direction of the repair: against the experiment, four unfavourable deltas
to two.** That is the strongest good-faith evidence the batch produced and it is
preserved in `CORR-20260801-003` and `DEC-20260801-013`.

### What stopped it

RTB-068 attached two preconditions and said in terms: *if either cannot be
satisfied, 069 must not approve.* Precondition 2 was satisfied. **Precondition 1
was not satisfiable by any record** — it demanded a superseding plantz manifest
that *also* made `tools/validate_ledger.py` stop erroring, and the validator
discovered runs by path glob with **no notion of supersession**. Three shortcuts
that would have cleared it — editing the frozen manifest, adding baseline lines,
registering it as legacy debt — were each refused for a stated reason.
TASK-20260801-069 **could** have narrowed the precondition by amendment and
deliberately did not: the party a precondition constrains does not get to narrow
it.

---

## 2. That blocker is gone

A **separate session** — not the one whose record failed the gate, exactly as
`CORR-20260801-003` and `DEC-20260801-012` require — implemented a run-supersession
registry:

- `tools/run_supersession_registry.yaml` — explicit, auditable entries; no
  globbing, pattern matching or inference
- `tools/validate_ledger.py` — `load_run_supersessions`, `check_run_supersessions`,
  exact-path routing in `check_run`, and the `tier_of_run` repair
- `tools/test_run_supersession.py` — the regression suite

Verified by the dispatching session: **1171 → 1169** errors with a diff showing
**exactly the two `RUN-LPF-001-plantz` lines removed** and nothing else moving;
both lines were in the **new** set, not the baseline, so nothing was laundered;
the frozen manifest is **unedited** and **no baseline line was added**;
supersession errors at `force=True` on either hash mismatch so it **cannot hide
drift**; and `tier_of_run`'s latent `TypeError` on list-valued `field_bits` is
fixed with the tier **governed by the largest cell**.

**DEF-065-1 is therefore recorded as DISCHARGED BY SUPERSESSION**, with the
registry entry as the evidence — *conditional on the review below*. On a REVISE it
reverts to half-discharged and is recorded that way.

---

## 3. The one open item, and it is the head of the batch

**Verification by the dispatching session is not independent review, and this
opening does not pretend otherwise.** The tool change alters **a gate**, and both
`CORR-20260801-003` and `DEC-20260801-012` require it to be reviewed before the
gate is relied on. **TASK-20260801-077** does exactly that, in a session that
neither wrote nor verified it, against seven named checks:

1. **Registry format** — schema pin, required fields, relative-path and no-`..`
   rules, 64-hex digests, duplicate-path rejection, and a malformed registry
   making the tool *refuse to run* rather than half-apply.
2. **Routing is exact-path only** — keyed on the absolute superseded path, with no
   glob, prefix or inference. A path is superseded only because it is named.
3. **Hash mismatches cannot be hidden** — either file drifting by one byte errors
   at `force=True`, undowngradable and unsuppressable; a missing file also errors.
4. **The duplicate-ID check is unweakened** — a superseding record may not itself
   match the run glob, both records must declare the same run id, and the run is
   registered exactly once.
5. **Nothing was laundered** — verified against Git: no line added to
   `validate_ledger_baseline.txt`, no entry in `legacy_run_inventory.yaml`, and the
   frozen manifest byte-unedited at `c8812fb4`.
6. **The error-set diff is exactly two lines** — the tool run at *both* commits,
   both error sets captured and diffed, counts reported **as measured**, and both
   removed lines confirmed to be in the new set rather than the baseline.
7. **`tier_of_run` semantics** — no `TypeError`, tier governed by the **largest**
   cell, non-numeric cells yielding `None`, missing-`field_bits` behaviour unchanged.

Plus: the change must be **committed and reachable from HEAD**, with the reviewed
commit sha recorded. An unarchived gate change is not reviewable evidence.

> **If TASK-20260801-077 returns REVISE at any severity, the measurement does not
> run**, TASK-20260801-079 through TASK-20260801-083 stand terminal `blocked`, and
> BATCH-027 records a **non-execution**. That is written into the contract, not
> left to judgement at the time.

---

## 4. The chain, in the order the queue fixes

| task | role | what it does |
|---|---|---|
| **075** | coordinator | opens the batch, authors `DEC-20260801-013` |
| **076** | coordinator | snapshot archive of that decision (2 paths) |
| **077** | reviewer | **independent review of the tool change** — the gate |
| **078** | coordinator | snapshot archive of the review **+ APPROVAL_DETERMINATION** (2 paths) |
| **079** | executor | **runs `RUN-LPF-001-measure` once**, only if APPROVED |
| **080** | coordinator | snapshot of the run package, **before any review reads it** (14 paths) |
| **081** | validator | independent validation — admissibility |
| **082** | red-team | independent red team — interpretation, scope, alternative classes |
| **083** | coordinator | ledger archive — EV-LPF-001, DEC-20260801-014, H-LPF-001, GOAL checkpoint (7 paths) |

081 and 082 are **siblings with no edge between them**: neither reads the other's
report.

**Exactly one run is authorizable in this batch, and it has exactly one gate.**

---

## 5. What is reused without rebuilding

| artifact | binding | status |
|---|---|---|
| `specification.yaml` | sha256 `0d6c946f…`, frozen at `ba1567ee` | **UNFAULTED by any review** |
| `reading_rule_v2.yaml` (RR-LPF-2) | sha256 `b633eaf1…`, frozen at `9515f6a1` | **PASSED on substance at TASK-20260801-068** — the reading rule of record |
| `reading_rule.yaml` (RR-LPF-1) | sha256 `8bcb196f…`, commit `1026150f` | **IMMUTABLE**, in no write scope |
| `RUN-LPF-001-calib` | snapshot `104d32fa` | **ADMISSIBLE**, 68,950,136 verified factorizations |
| `RUN-LPF-001-plantz` | snapshot `aaf7672c` | **ADMISSIBLE**; manifest defect superseded and registered |
| `lpf001_driver.py` | sha256 `786aeb05…` | **UNMODIFIED**, hash-bound across the calibration boundary |

**Nothing above is rebuilt, re-frozen or re-reviewed.** No new experiment id, no
new hypothesis, no new contract, no new calibration, no new reading rule, no new
driver.

---

## 6. Proportion — the ruling this opening owes

**Three consecutive batches have closed without running, each for a correct
reason.** The gates are working: BATCH-024 on a contract review, BATCH-025 on
RTB-054-1 (a rule certifying two rungs with no recorded movement), BATCH-026 on an
unsatisfiable precondition. Two of the three were caught **only** by recomputation
or execution — reading would have missed them.

**And the ceremony is now costing more than the science it protects.** BATCH-026
spent fourteen declared cards, five review duties and four executed archives
(TASK-20260801-062, -064, -067, -069) to produce a PASS on a file that then could
not be used.

Under `docs/inventor-protocol.md` §4, **premature closure is a failure mode
symmetric with overclaiming**. A campaign that never runs because a procedural
item is always outstanding has not been rigorous; it has stopped doing science
while continuing to look rigorous.

### The five disciplines are kept. No sixth is filed.

- **Attainability** — kept as a *binding property*, not re-run. Re-run from
  scratch at 068 with L-1's second leg FALSE; RR-LPF-2 is byte-frozen and the
  calibration is unchanged. Re-enters at 083: the branch fired must be one
  RR-LPF-2 certifies.
- **Movement at every rung** — **re-run in full** at 081. This is the check that
  caught RTB-054-1 and it is cheap.
- **Anti-tuning** — kept in its mechanical form and **structurally stronger here
  than in any prior batch**: the reading rule was frozen, hash-bound and
  independently reviewed *before the measurement exists*.
- **Decision-variable variation** — kept at 081: every threshold traced to the
  named order statistic of the named archived array by an independent sort, and
  every branch leg attributed to the arm that produces it.
- **No sentence on an unarchived array** (PERTURB-TAIL-1) — kept, applied to
  EV-LPF-001 and the close decision.

### Gates judged redundant **for this batch**, and why

| gate | judgement |
|---|---|
| four-change-cap diff | **retired — it has no object.** No reading rule is authored; RR-LPF-2 was machine-diffed at 068 with no fifth change found. Replaced by a one-line hash check at every archive. |
| attainability re-run | **retired as a re-run.** It was run from scratch at 068 and none of its inputs has moved. |
| alternative-class source re-derivation | **retired as a derivation.** Re-derived from driver source and recomputed against the archived arrays at 068, incl. 10,664 executions. Replaced by a **restatement** duty checked by 082. |
| plant-Z regeneration arm | **absent, not waived** — nothing is regenerated. |
| one-cycle amendment cap | **not applicable** — no rule is authored, so there is no cycle to cap. |

### What is **not** reduced

Both the Validator and the Red Team run, independently of each other. The 100%
factorization verification and the independent-refactoring duty are unchanged. The
snapshot-before-review order is unchanged. The pilot budget gate is unchanged, and
an abort at it is an L-0 instrument signal reported as a budget event.

### The reduction is conditional and self-voiding

It rests entirely on hash equality of six named artifacts. **If any of the
specification, either reading rule, the driver, the calibration package or the
plantz manifest fails to match its declared sha256 at any archive, the reduction
is void, the batch stops, and the full duty set returns.**

---

## 7. Carried forward, each with its status

`DEF-065-1` **discharged by supersession** (registry entry as evidence,
conditional on 077) · `DEF-065-2/3/4/5` present and acted on, carried ·
`DEF-068-A` open (register incompleteness) · `DEF-068-B` open (undeclared
normalisation, and the clarification is *correct*) · `DEF-068-C` discharged by
record at CORR-20260801-003 Part B as RTB-068-1 · `DEF-068-D` no repair required ·
`NINTH-BULLET` **unverifiable**, cited only as such · `D2`–`D6` carried as
observations, D5's completeness hoist still refused as a new-driver change ·
`OPEN-RR066-A` ruled Reading 1, **bound condition in force** (empty list = absence
of *certified power*, never of *measured movement*) · `OPEN-LPF049-A` ruled
non-decisional, **zero margin** carried · `OPEN-RR052-B/C/D` ruled, D with its
extension · `ANOM-LPF052-1` confirmed, signed-(D+, D−) reporting **ranked, not
done** · `OPEN-BATCH022-A` mitigated not repaired — **the registry does not repair
it** · `OPEN-BATCH022-B` mitigated, mandatory freshness re-check at 083 ·
`OPEN-BATCH023-B` second half repaired, first half mitigated only ·
`OPEN-BATCH024-A` **open, with its first partial machine-readable mitigation and
the limit of that mitigation recorded** (run manifests only) · `OPEN-BATCH026-A/B`
instances repaired, general cases open · `RT049-B6` open, carried sharpened ·
`KN-CAND-BATCH023-A` withheld, route (b) cheaper · `KN-CAND-BATCH024-A` withheld,
**trigger (b) now arguably met and deliberately not exercised** ·
`PATTERN-INSTR-5` **four instruments, five batches, five defect classes — not
incremented by BATCH-026**, honest status `unverified`.

**Standing model-independence caveat, in force and unchanged.** Every session
resolves to `claude-opus-5`. Independence is **procedural**, not model-level.
`model_verified` is false everywhere. Nothing produced in BATCH-026 or BATCH-027
is admissible toward the AGENTS.md rule 13 three-model closure quorum.

---

## 8. Forbidden at this batch

`S1_met`, `F1_met`, `F2_met`, `structure_gate_passed`; `support` for H-LPF-001,
H-SMTH-001, H-DS-001, H-EQD-001 or H-DEP-001; HEUR-DS-1 validation or refutation
above the toy tier in either direction; any asymptotic, crypto-scale,
medium-scale or affected-scheme claim; movement of promotion gates **G1–G4, all
of which remain OPEN**; `reject_scoped` and in particular
reject_scoped-as-impossibility on a single unreplicated run; `dominated_by: null`;
and equally any characterization of BATCH-021 through BATCH-026 as vacuous, which
would be premature closure.

Do not edit `reading_rule.yaml`, `reading_rule_v2.yaml`, `specification.yaml`,
`lpf001_driver.py`, any run package, any review file, any prior ledger record, or
any file under `tools/`. Do not edit anything under `experiments/EXP-SMTH-001/`,
`experiments/EXP-DS-001/`, `experiments/EXP-EQD-001/` or
`experiments/EXP-DEP-001/`. Leave FAEST and XEDN alone. **Toy ceiling throughout.**
