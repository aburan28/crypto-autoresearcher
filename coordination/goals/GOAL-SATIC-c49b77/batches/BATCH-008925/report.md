# BATCH-008925 — bounded independent integrity review of the GOAL-SATIC-c49b77 launch archives

Goal: `GOAL-SATIC-c49b77` · Question: `RQ-SATIC-1ae57a` · Authorized by `DEC-20260905-36847f`
Disposition: `DEC-20260905-6e8621` · Archive task: `TASK-20260905-e20317`

## Outcome in one line

The independent review delivered and discharges its own frozen contract; the nested
`IMP-1` is **cleared**, the top-level `IMP-1` is **partially cleared**, `IMP-3`
**stands** — and no completion criterion is met.

## What ran

| Task | Role | Outcome | Artifacts |
|---|---|---|---|
| `TASK-20260905-2c383f` | validator | completed (epoch 2, owner `validator-satic-008925-1`) | `tasks/TASK-20260905-2c383f/startup_receipt.json`, `tasks/TASK-20260905-2c383f/report.json` |
| `TASK-20260905-e20317` | coordinator | this ledger archive | `DEC-20260905-6e8621`, this report, `archives/TASK-20260905-e20317/ledger.md`, goal checkpoint |

Epoch 1 of `TASK-20260905-2c383f` was claimed by `coordinator-satic-recon-3` on
2026-09-05 and released `failed` seven minutes later with zero work, when
`review-adversarial` at `xhigh` proved unservable on every reachable backend
(`DEC-20260905-e140ee`). Epoch 2 ran on 2026-09-07 in a Cursor Cloud Agent
claude_code-family session and delivered.

## The review's own result — the Validator's, cited as such

Overall verdict `pass`; joints J1–J4 all `pass`; 14 findings, highest severity
medium. Its headline quantities: 58 of 58 bound path digests recompute exactly
at the commit each archive names, across 7 archive binding blocks; 53 of 58
against the working tree, the 5 exceptions being 5 bindings of only 2 shared
mutable files; 10 of 10 release-record digests exact; the reverse direction
finding 23 of 23, 7 of 10 and 10 of 13 files bound per batch, with the 6 unbound
paths all claim/release side files or dispatch queues that cannot bind
themselves.

The proves-too-much control was executed as this batch's contract words it: the
J1 method applied to the known-good `BATCH-cef2eb` set as well as the failed
sets. It reports 1 flag of 17 on the control set against 5 of 58 overall, of the
same kind and cause, and concludes the flags are **uncorrelated with batch
outcome** — so the quantity being measured is "a shared mutable record has moved
since it was bound", not "this batch failed". That is a real and well-argued
specificity result.

## What this Coordinator recomputed, rather than restated

- **Nine bound digests at their named commits, all exact.** A sample spanning
  all three batches, both archive kinds, and both shared mutable files:
  `79a686/snapshot.md` and the goal head and `research-priority.yaml` at
  `9a79547b6`; the goal head at `0136779b8`, `51e193bb1` and `b384ae3cb`;
  `15bed7/snapshot.md` at `1e88c6fea`; `cef2eb/probe.py` at `4a6ee8775`;
  `5dd82d/observer.json` at `b384ae3cb`. This corroborates the at-commit result
  on the entries checked and asserts nothing about the 49 not checked.
- **The release binding of the assessed artifacts.** `report.json` hashes
  `8763fa8e…9403` and `startup_receipt.json` hashes `23cf173e…25ed` in the
  working tree, both exactly equal to the `artifact_sha256` values in
  `claims/TASK-20260905-2c383f.2.release.json` and to the bytes at snapshot
  `acb081203`.
- **The reverse-direction file counts** — 23 / 10 / 13 at the reviewer's HEAD
  `6fe699ada`, reproduced independently and matching.
- **The findings severity tally** — medium 5, low 6, informational 3, total 14.
- **The policy environment** — `doctor --probe` re-run here reproduces the
  Validator's account exactly, including the configuration digest
  `sha256:5c8ecafafa75d5675d9166e9530b7365`.

## The report is the release-bound artifact

Two commits touched it after the snapshot. `dd8bb7d6f` edited `findings_summary`
inside the immutable report and broke its release binding
(`8763fa8e…` → `ad54f243…`); `4172dca7f` restored the archived bytes from
`acb081203`. All three revisions were recomputed here: snapshot `8763fa8e…`,
edit `ad54f243…`, restore `8763fa8e…`, working tree `8763fa8e…`. The restore was
the correct handling — corrections supersede, they do not rewrite — and its
consequence is that the severity-count nit survives in the bound bytes.

**Verified defect in the bound artifact:** `findings_summary.by_severity` records
low 5 / informational 4 where the array holds low 6 / informational 3. The
total, `high`, `medium`, `highest_severity` and the medium ID list are all
correct, so this disturbs no verdict. The remedy is a superseding record, named
and not performed.

## A gap this Coordinator found

The report explains the working-tree goal-head divergence by two later commits
(`ac06af61a`, `72dbd15d5`). Both exist and do what it says. But a **third**
commit changed that file and is not named: the merge `725f084ca`, which changed
it by 105 insertions and 66 deletions against its first parent and produced the
current bytes. The goal head hashes `0cab79ce…` at `72dbd15d5` and `6623f321…`
in the working tree, so a further change necessarily occurred. `git log
--follow` — the report's instrument — lists exactly six commits and omits the
merge; the six were reproduced here, then the merge found with a plain per-path
`git log`. The sentence is literally accurate about its instrument and
materially incomplete about the file. J1's at-commit result is unaffected.

That merge also **explains FINDING-01**, which the report records as a state
without a cause. Its own message body carries
`# Conflicts:  ledger/goals/GOAL-SATIC-c49b77.yaml`. Traced here: `72dbd15d5`
introduced a top-level `impediments` block carrying a *second* `IMP-1` while the
nested list ended at `IMP-2`; merge parent `463a2ec1c` held only `research_goal`
with nested `IMP-1/2/3`; merge parent `d4592dc73` held the top-level `IMP-1` with
nested `IMP-1/2`; and the merge took the **union**. AGENTS.md says a sync
conflict inside a ledger record is resolved by a superseding record under a new
id "and never an edit that picks one side" — this merge kept both sides, which is
how one identifier came to name two different impediments. It is on `origin/main`.

## The policy question

**An unprobed authenticated direct session does not satisfy a recheck naming a
credentialed backend.** A direct Claude-Code-family session does not route
through the adapter and has no adapter-visible credential, so the instrument
`IMP-3`'s recheck names is structurally unsatisfiable by that runtime class.
`adapter resolve` reports a *configured* binding, and AGENTS.md is explicit that
a model identifier is unverified configuration until `doctor --probe` confirms
it. No backend is credentialed.

Two consequences that must not be collapsed:

1. **The review is neither invalid nor a degradation.** Rule 16 permits an
   authenticated direct Claude Code session whose provider is not Bedrock, and
   nothing conditions a review's validity on `model_verified: true`. What the
   policy forbids is *silent* substitution and *unrecorded* degradation:
   `fallback_used` false, `degraded_requirements` empty, `effort: xhigh` carried
   in `.claude/agents/validator.md` and confirmed by
   `check_runtime_bindings.py` (both verified here), and the unverified status
   disclosed in receipt and report.
2. **The policy is not verified served either.** The strongest evidence is a
   self-report agreeing with a config file, which the Validator itself correctly
   refuses to call a probe. The report's evident depth is behavioural evidence
   about the review, never a model-identity probe. The attestation remains
   unobtained, and none is recorded.

## Findings that bear on the impediment or the criteria

Three of the five medium findings converge on one thing: **telemetry capture is
this campaign's weak joint.**

- **FINDING-04** — per-task wall-clock compliance is unverifiable for three of
  four producer tasks, and the one measurable envelope (1228 s) exceeds the
  600 s cap and cannot be attributed. Neither compliance nor violation is
  established.
- **FINDING-08** — the resource-limit anomaly at the centre of the readiness
  record rests on Executor-*transcribed* rather than *captured* probe output,
  disclosed in `transcript.json` but not in `report.json`.
- **FINDING-09** — the transcript's `authority_validation` asserts a returncode
  it did not capture, its embedded plan is bound to a queue state matching no
  committed revision, and the `/tmp` plan file is not preserved.

None is fabrication and none is asserted as such — FINDING-08's substance is
independently corroborated by the separate isolated probe in
`BATCH-1a527c/archives/TASK-20260905-2b52a7/snapshot.md`. But a benchmark
package built on the same recorder pattern would inherit the gap, and criterion 1
requires results "within declared parameters", which needs *measured* parameters
this campaign does not yet have.

**FINDING-14** is the sharpest on the impediment itself. The delivery diagnostic
that justified re-opening the review had a 2208-byte payload and about 5.7
seconds of work, and neither `observer.json` nor `DEC-20260905-293536` records
that this is unrepresentative of a substantive review. The goal's own history
bears it out: the very next review attempt still failed. "Delivery works" never
transferred; what delivered this review was a different runtime.

## Checks nobody has run

`IMP-3`'s `clears_when` names **BATCH-2cca27's** frozen contract, which is a
different document — digested here as `8589f128…` against BATCH-008925's
`b5c558c6…`, a different schema with a different check list. Three of its checks
have no counterpart and were not performed, and one of them matters:

**No session has run a planted-defect sensitivity control on this verification
procedure.** BATCH-2cca27 mandates one before any verdict — corrupt a copied
receipt in scratch space, confirm the procedure flags it, and "if it does not,
the procedure is broken and the verdict must be invalid, not passed."
BATCH-008925's control is the opposite kind: a *specificity* check on a
known-good set. Neither substitutes for the other. AGENTS.md's own
"proves-too-much" obligation is the *known-false* form, which matches
BATCH-2cca27's control and not BATCH-008925's — a defect in BATCH-008925's
contract as frozen, not in the Validator's execution of it.

The report's mitigation is partial and honestly labelled: its method emitted two
false positives from its own instrument, both run down rather than accepted,
which shows the instrument emits flags at all. That is strictly weaker than a
planted-defect control and is not presented as equivalent.

## Impediment disposition

| Impediment | Verdict | Deciding fact |
|---|---|---|
| `IMP-1` nested | **cleared** | Every conjunct of its `clears_when` holds: newly approved, bounded, independent, durable, archived at `acb081203`, content-verified here, published to `origin/main`, disposed by this decision. |
| `IMP-1` top-level | **partially cleared** | What it blocked is no longer blocked, but none of its four credential/transport disjuncts is satisfied — the blockage lifted by a fifth route its author did not enumerate. |
| `IMP-3` | **stands** | It names a different frozen contract and a credentialed-backend recheck; neither is satisfied. Its `what_is_blocked` is narrowed to the policy attestation and the known-bad control. |
| `IMP-2` | **stands, out of scope** | Deferred behind this disposition by the goal's own ordering; not examined. |

One shortfall inside the clearance, recorded rather than absorbed: the snapshot
archive task `DEC-20260905-36847f` authorized (`TASK-20260905-de286c`) **was
never created**. There is no `archives/` directory for it and no receipt;
`acb081203` is a bare snapshot commit. "Verified" therefore rests on content
verification — recomputed here — plus the dispatcher spot-check in the release
note, which under CLAUDE.md's content-first rule is sufficient for durability.
The missing archive *task* is a process defect, routed rather than repaired.

## Completion criteria — neither met

**Criterion 1** is not met: no benchmark package exists, zero solver invocations
occurred in any reviewed batch and zero in the review, and the only reproduced
computations are truth-table enumerations over three 1- and 2-variable fixtures.
Every substantive obligation in `benchmark-obligations.json` is `pending`.

**Criterion 2** is not met, and this decision must not be misread as satisfying
it. It answers a records-integrity and inference-policy question, not an
attribution question about `RQ-SATIC-1ae57a`, which both the review and this
disposition leave untouched. The criterion's own text forecloses the nearest
temptation — "tooling readiness or design intake alone never satisfies this
criterion" — and an integrity review of archive bindings is further from an
attribution answer than design intake is.

## Ranked next action for this lane

**Rank 1 — execute BATCH-2cca27's frozen known-bad control, alone.** It converts
a one-sided specificity result into a two-sided calibration result; it is cheap
and needs no solver, benchmark, or network; the contract is already frozen and
approved; it is the AGENTS.md known-false pattern BATCH-008925's control did not
implement; and `DEC-20260905-29416d` records it as still unperformed. It ranks
ahead of doing nothing because a `pass` on a procedure never shown to flag a
planted corruption is weaker than it reads.

Ranked below: reconciling FINDING-01/02 by a superseding goal record (real, but
reduces no research uncertainty); designing the criterion-1 package (gated on a
capture discipline that yields measured parameters, per FINDING-04/08/09); and
IMP-2 (out of scope by the goal's own ordering).

## What this batch does not establish

Nothing mathematical. No hypothesis status changes and
`active_hypothesis_ids` stays empty. `RQ-SATIC-1ae57a` is untouched. No solver
readiness. No cause for the two reportless attempts or the later refusal — this
review examined records, not runtimes, and an infrastructure failure remains
categorically not negative mathematical evidence. The blocked ledger stages
`TASK-20260905-e2c12f` and `TASK-20260905-86ea49` **remain blocked**; clearing
the missing-review impediment removes the obstacle to deciding them and is not
that decision. `BATCH-2cca27`'s own bindings were never assessed by any
completed review.
