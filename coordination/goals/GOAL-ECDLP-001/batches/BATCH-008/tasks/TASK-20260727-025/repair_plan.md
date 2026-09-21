# BATCH-008 specification repair plan

- **Record id:** REPAIR-PLAN-BATCH008-001
- **Produced by:** TASK-20260727-025 (Coordinator, GOAL-ECDLP-001, BATCH-008)
- **Date:** 2026-07-27
- **Status:** frozen. It is the contract the repair task TASK-20260727-028 executes
  and the object the independent reviews TASK-20260727-030 and TASK-20260727-031
  check. It is not durable until TASK-20260727-027 commits it and the
  dispatcher's post-commit verifier accepts that commit.
- **Session capability disclosure:** the session that wrote this plan had **no
  shell and no Git access**. It ran no `git` command, no `tools/validate_ledger.py`
  and no `tools/research_dispatch.py`. Every commit identifier and blob hash below
  is **orchestrator-supplied and unverified in this session** and is labelled as
  such at each use. Every `commit_sha`, `parent_sha` and `path_sha256` in this
  batch is null or empty by construction. Nothing here is fabricated: what could
  not be checked is marked unchecked.

---

## 1. The defect

`python3 tools/validate_ledger.py` reports three cross-reference errors
(orchestrator-supplied, not re-run in this session):

```
ledger/evidence/EV-STR-003.yaml: evidence references unknown experiment 'EXP-STR-003'
ledger/decisions/DEC-20260727-009.yaml: decision references unknown target 'EXP-STR-003'
ledger/decisions/DEC-20260727-008.yaml: decision references unknown target 'EXP-IC-002'
```

### 1.1 Root cause, verified by reading `tools/validate_ledger.py` in this session

`main()` globs `experiments/*/specification.yaml` and calls `check_experiment`
(lines 461-463). `check_experiment` calls `load_yaml` (line 189); `load_yaml`
catches `yaml.YAMLError`, records an `invalid YAML: ...` error and returns
`None` (lines 130-135); `check_experiment` then returns immediately without
reaching `ctx.register` (line 209). **An experiment whose specification does not
parse is never registered as an id.** `check_cross_refs` (lines 266-307) then
finds `EXP-STR-003` and `EXP-IC-002` absent from `ctx.ids` and reports the three
errors above against the *referring* records, which are themselves well-formed
and correct.

The three reported errors are therefore symptoms. The defect is in the two
specification files, and it is the same bug class in both: an **unquoted `|`
opening a plain scalar, which YAML reads as the block-scalar indicator**.

### 1.2 Scope check performed in this session

- `tools/validate_ledger_baseline.txt` contains `invalid YAML` lines for eleven
  other specifications (EXP-DREG-001, EXP-DREG-002, EXP-EQJ-001, EXP-FB-001,
  EXP-FB3-001, EXP-ICI-001, EXP-REP-001, EXP-REP-002, EXP-SIG-001, EXP-SIG-004,
  EXP-SIG-005). It contains **no** line for `experiments/EXP-STR-003/specification.yaml`
  or `experiments/EXP-IC-002/specification.yaml`.
- **Consequence, routed rather than asserted:** on the reading of the validator
  code above, a run of `tools/validate_ledger.py` today should emit **five** new
  errors, not three — the three cross-reference errors plus two unbaselined
  `invalid YAML:` lines, one per file. The orchestrator reported three. This
  session cannot run the validator and does not claim the count. TASK-20260727-028
  must capture the **verbatim** validator output before and after the repair, and
  TASK-20260727-030 must report any disagreement with this paragraph. If only
  three errors appear, this paragraph is wrong and the reviews must say so.
- Both files were scanned in this session for every occurrence of `|`. In
  `EXP-STR-003/specification.yaml` there are two: line 407 (the defect) and
  line 496, which is a continuation line inside a block scalar and is literal
  text. In `EXP-IC-002/specification.yaml` there are twenty-three; twenty-two of
  them are continuation lines inside `>-` block scalars (mathematical notation
  such as `|S|`, `|S intersect <P>|`) and are literal text. Line 213 is the
  single occurrence that begins a plain scalar value.

---

## 2. EXP-STR-003 — repair in place, with re-attestation

### 2.1 Current state

| Field | Value | Verification status in this session |
|---|---|---|
| Path | `experiments/EXP-STR-003/specification.yaml` | read directly |
| Contract blob (HEAD) | `1c6f10b7ba4db293126504c19b4fe9c931b257f3` | **orchestrator-supplied, unverified** |
| Blob identical at | `92268c9e72dd9d49de410f4a535e64af5aa5d9a9` (pre-execution freeze, TASK-20260727-020), `c79e3a8d6cb429c7a9c876b5e0272f46145ab919` (run-package snapshot, TASK-20260727-022), and HEAD | **orchestrator-supplied, unverified**; independently reported by TASK-20260727-023 and TASK-20260727-024 |
| Committed runs | 20, each recording `code.commit: 92268c9e72dd9d49de410f4a535e64af5aa5d9a9`, `dirty: false` | **orchestrator-supplied, unverified**; reported by TASK-20260727-023 |
| Downstream ledger | `EV-STR-003`, `DEC-20260727-009`, `CORR-20260727-007`, `H-STR-002` (`supported -> weakened`) | read in this session |

### 2.2 The exact line

**Before (line 407, 4-space indent):**

```yaml
    - branch: "square" | "rectangular" - which limb of lines 220-234 executed (RT-OBJ-4).
```

**After (line 407, 4-space indent, single-quoted):**

```yaml
    - branch: '"square" | "rectangular" - which limb of lines 220-234 executed (RT-OBJ-4).'
```

**Why it fails now:** the value token begins with the double-quoted scalar
`"square"`, after which YAML expects the end of the node; the trailing
` | "rectangular" - ...` is unparseable in that position.

**What the repair changes:** two characters are added, one at the start of the
value and one at the end of the line. The parsed value becomes the string

```
"square" | "rectangular" - which limb of lines 220-234 executed (RT-OBJ-4).
```

which is character-for-character the text a human reads on line 407 today. The
line contains no single-quote character, so no escaping is needed and none is
introduced. **No key, no number, no criterion, no control, no budget, no
`version`, no `status` and no `approved_by` is touched.**

### 2.3 Mechanism decision: repair in place, and it is not free

**Chosen: repair in place + re-attest.** Recorded plainly: **this changes the
blob.** After the repair, `experiments/EXP-STR-003/specification.yaml` at HEAD is
a new blob, and the statement "the spec blob is byte-identical at `92268c9e`,
`c79e3a8d` and HEAD" stops being true at HEAD. That is a real cost and this plan
does not pretend otherwise.

What the repair **preserves**:

- The frozen blob `1c6f10b7...` is not destroyed. Git keeps it permanently and it
  stays independently retrievable by `git cat-file blob 1c6f10b7...` and by
  `git show 92268c9e:experiments/EXP-STR-003/specification.yaml`.
- The 20 run manifests attest `code.commit: 92268c9e`, a **commit**, not HEAD's
  working file. That attestation is untouched: it still resolves to the original
  blob. No run record is edited, and no run record needs to be.
- The pre-registration property that makes the ablation evidential — that the
  criteria F1-F4 and S1-S4 were frozen at `92268c9e` *before* `c79e3a8d`
  executed them — is a property of commit order, which the repair cannot alter.
- Every number in `EV-STR-003`, `DEC-20260727-009` and `CORR-20260727-007`, and
  the `H-STR-002` `supported -> weakened` transition they carry.

What the repair **does not preserve**:

- Byte-identity of HEAD's file with the attested freeze. A reader who checks
  HEAD against the runs' attested commit will now find a one-line difference and
  must consult `CORR-20260727-004` to learn why. That is exactly why the
  correction record is mandatory and must name **both** blob hashes.
- The property that the frozen contract has never been edited after freezing.
  It has been, once, on the record, for quoting only.

**Rejected: reissue under a new EXP id.** It does not fix the reported defect,
and saying otherwise would be false. `EV-STR-003.yaml` and `DEC-20260727-009.yaml`
are immutable and name `EXP-STR-003`; a new id leaves both references
unresolvable, so errors 1 and 2 persist verbatim. The unparseable file would also
remain in the glob, so its own unbaselined `invalid YAML:` error persists. It
would additionally strand 20 run manifests whose `experiment_id` is `EXP-STR-003`
on a contract that no tool can read, and create a second contract for one
executed protocol. It buys blob preservation by leaving the defect in place.

**Rejected: parseable sidecar.** It preserves the blob perfectly; that is its only
merit. The validator globs `experiments/*/specification.yaml` **only**, so a
sidecar under any other filename registers no id and clears no error. A sidecar
placed at some other `experiments/<dir>/specification.yaml` carrying
`id: EXP-STR-003` would register the id, but it manufactures a directory whose
name contradicts its id, creates **two sources of truth for one frozen
contract**, and is unstable by construction: the moment the original is ever
repaired the validator reports `duplicate ID EXP-STR-003`. Two contracts for one
experiment is the failure mode the immutability rule exists to prevent.

**Why the two alternatives are not close.** Repair-in-place is the only mechanism
of the three that actually clears the reported defect under the id that the 20
runs and `EV-STR-003` already reference. The cost is a documented, reviewed,
one-line quoting change to an attested file whose original remains permanently
retrievable; the alternatives cost either the defect itself or a permanent
duplicate contract.

### 2.4 Required accompanying record

Because the file is frozen and attested, the repair is **not** authorized as a
silent edit. `AGENTS.md` core rule 4 is discharged by a superseding correction,
`CORR-20260727-004`, written by the ledger archive TASK-20260727-032, which must
state: both blob hashes (before and after), the three commits at which the
original blob is retrievable, the exact line changed, that the runs' attestation
points at `92268c9e`'s blob and continues to resolve, and that no protocol field
changed. This is deliberately the opposite of the `5de2db97` defect that
`CORR-20260727-007` corrects: that was an in-place rewrite of archived *claims*
with no superseding record; this is a quoting change declared in advance in a
snapshot-committed plan, independently reviewed, and recorded in a superseding
correction.

**This is not a `protocol_amendment`.** No input instance, control, independent
variable, metric, seed strategy, budget, stopping rule, success criterion or
falsification criterion changes. `version` stays `1` and `confirmatory_status` is
untouched. TASK-20260727-028 must not bump `version`: doing so would falsely
signal a protocol change and would itself alter a parsed field.

---

## 3. EXP-IC-002 — repair in place, no attestation to preserve

### 3.1 Current state

| Field | Value | Verification status in this session |
|---|---|---|
| Path | `experiments/EXP-IC-002/specification.yaml` | read directly |
| Contract blob (HEAD) | `8987eb01978ab82538b17e35358c389c23a9b7f1` | **orchestrator-supplied, unverified** |
| Committed runs | **zero** — the experiment was reviewed `REVISE` twice (TASK-20260727-004, TASK-20260727-012) and **never executed** | consistent with the committed BATCH-006 checkpoint read in this session |
| Downstream ledger | `DEC-20260727-008` names it as a target; `EV-IC-002` is a derivational re-analysis of the 748 committed **EXP-IC-001** runs and does not rest on any EXP-IC-002 execution | read in this session |

### 3.2 The exact line

**Before (line 213, 6-space indent):**

```yaml
      - p_dec_counting_bound: |S| / N.
```

**After (line 213, 6-space indent, single-quoted):**

```yaml
      - p_dec_counting_bound: '|S| / N.'
```

**Why it fails now:** `|` in the value position is the block-scalar indicator, so
YAML expects a header and an indented block, and `S| / N.` on the same line is
unparseable.

**What the repair changes:** two characters. The parsed value becomes the string
`|S| / N.`, character-for-character the text a human reads today. The line
contains no single-quote character. **No key, no number, no criterion, no
control, no budget, no `version`, no `status` and no `approved_by` is touched.**

### 3.3 Mechanism decision: same mechanism, materially weaker constraint

**Chosen: repair in place.** The two files get the same mechanism but they are
**not** the same case, and this plan records the difference rather than applying
one rule to both:

- **No run binds to this blob.** There are zero runs, so there is no
  `code.commit` attestation whose byte-identity with HEAD anyone will ever check.
- **No evidence record rests on its execution.** `EV-IC-002` is derived from
  EXP-IC-001 run records; `DEC-20260727-008` weakened `H-IC-001` on that
  derivation, explicitly noting the control experiment was never executed.
- The versions that the two `REVISE` reviews actually read remain retrievable in
  Git history exactly as before, alongside `experiments/EXP-IC-002/amendments/v1_to_v2.yaml`.

The consequence is a difference in **obligation**, not in mechanism:
`CORR-20260727-004` must carry the full two-blob re-attestation apparatus for
EXP-STR-003, and for EXP-IC-002 need only record the before/after blobs, the line,
and the fact that no run, evidence record or attestation depends on the prior
blob. The reviews must confirm that the second case is not silently given the
first's weight, and equally that the first is not silently given the second's
lightness.

Reissue-under-a-new-id and sidecar are rejected here for the same reasons as in
2.3, with one addition that makes rejection easier: reissuing an experiment that
was **never executed** would create a second unexecuted contract for the same
never-run protocol, which is pure ledger noise.

---

## 4. What the repair task must and must not do

**Must:**

1. Capture the verbatim output of `python3 tools/validate_ledger.py` **before**
   any edit, into `validator_output_before.txt`.
2. Apply exactly the two line changes in sections 2.2 and 3.2.
3. Confirm with `python3 -c "import yaml; yaml.safe_load(open(<path>))"` that each
   file now parses, and record the top-level `experiment.id`, `version`, `status`,
   `hypothesis_id` and `approved_by` read back from the parsed document.
4. Confirm that the parsed value of `experiment.metrics.secondary` contains, for
   EXP-STR-003, the exact string
   `"square" | "rectangular" - which limb of lines 220-234 executed (RT-OBJ-4).`
   and, for EXP-IC-002, the exact string `|S| / N.`.
5. Capture the verbatim output of `python3 tools/validate_ledger.py` **after** the
   edit, into `validator_output_after.txt`, and state explicitly whether the three
   reported errors cleared, whether the two `invalid YAML` lines cleared, and
   whether **any new error appeared**. A newly surfaced error is a finding to
   report, never a thing to suppress.
6. Record `git diff --stat` and the full `git diff` for both files, and the
   post-repair blob hash of each file, in `repair_report.yaml`.
7. Re-confirm that all 20 `experiments/EXP-STR-003/runs/*/manifest.yaml` still
   record `code.commit: 92268c9e72dd9d49de410f4a535e64af5aa5d9a9` and are
   unmodified.

**Must not:**

8. Change any byte of either file other than the declared lines. If
   `yaml.safe_load` still fails after the declared change, apply the **same**
   minimal-quoting discipline to the newly reported line, record it as an
   additional declared change with its own before/after, and repeat. If any
   remaining parse failure cannot be repaired by quoting alone — that is, if it
   would require changing content, structure, or a key — **STOP and report**. The
   repair task is not authorized to change content under any circumstances.
9. Add any line to `tools/validate_ledger_baseline.txt`. That file is outside the
   write scope. The baseline may only ever shrink; growing it to absorb this
   violation would defeat the check and is forbidden.
10. Touch any run record, any file under `harness/`, any ledger record, or any
    other experiment.
11. Bump `version`, alter `status`, `approved_by`, `frozen`, `frozen_on`, or any
    criterion.
12. Create, edit or delete any evidence, decision or correction record. Those
    belong to the ledger archive TASK-20260727-032.

---

## 5. Why semantic equivalence cannot be proved mechanically, and what replaces it

The originals do not parse, so there is no parsed structure to diff the repaired
files against. No tool can certify "same semantics" here, and no record in this
batch may claim one did. What **is** mechanically checkable, and is what the
reviews must check instead:

- **Exactness of the diff.** `git diff` must show exactly the declared changed
  lines and nothing else — no reflow, no whitespace change, no reordering, no
  line-ending change. Everything outside those lines is byte-identical.
- **Character-level identity of the changed value.** The repaired value string,
  read back from `yaml.safe_load`, must equal the original line's text after the
  `<key>: ` prefix, character for character. Both changes are pure delimiter
  additions, so this is decidable by eye and by string comparison.
- **Validator transition.** Errors present before and absent after, with no new
  error introduced.
- **Attestation continuity.** The original blobs still resolve at their recorded
  commits; the 20 run manifests are unmodified.

This is the strongest available basis and it is `derivation`, not `certificate`.
`EV-SPEC-001` must set `proof_status: derivation` and must not claim a
certificate. If the reviews cannot establish the diff is exactly the declared
lines, the correct outcome is that the repair is returned to the repair task as
defective — not that a weaker claim is written.

---

## 6. Reserved record identifiers (named here, created by TASK-20260727-032)

| Id | Type | Purpose | Status |
|---|---|---|---|
| `EV-SPEC-001` | evidence | The repair is minimal, semantics-preserving on the stated basis, and clears the reported validator errors. `hypothesis_id: H-STR-002`, `direction: neutral`, `claim_tier: toy`, `run_ids: []`, `proof_status: derivation`. Its boundaries must state that it bears on `H-IC-001`'s contract artifact too and that it moves **neither** hypothesis's status. | reserved, unwritten |
| `DEC-20260727-003` | coordinator_decision | The official disposition of the repair. Must fill `knowledge_promotion` (a `not_warranted` reason is expected: a YAML quoting repair is not a research finding). | reserved, unwritten |
| `CORR-20260727-004` | correction | The superseding record for the in-place edit of two frozen contracts, carrying both blob-hash pairs and the re-attestation statement of section 2.3. | reserved, unwritten |

No evidence, decision or correction record is created by TASK-20260727-025.
No hypothesis status is changed by this plan or by the repair.

---

## 7. What this batch is not

- Not a research result of any kind. It produces no measurement, no run, no
  attack, no cryptanalytic claim, no closure, no impossibility claim, and no
  result at any tier. It moves no asymptotic exponent in either direction.
- Not a completion criterion of `GOAL-ECDLP-001`. A repaired ledger is not a
  candidate attack improvement and is not an independently validated novel
  technique.
- Not a re-opening of `H-STR-002` or `H-IC-001`. Both remain `weakened`, per
  `DEC-20260727-009` and `DEC-20260727-008` respectively.
- Not a closure of anything, so **no closure quorum arises and none is claimed**.
  Recorded for the record: `AGENTS.md` in this tree has **no rule 13 and no
  closure-quorum clause** — that text is an `origin/main` skew — and every review
  in this session's lineage resolved to `claude-opus-5` with `fallback_used: true`,
  so three pairwise-distinct `resolved_model_id` attestations are **not available
  here**. Nothing in BATCH-008 closes a goal, so nothing in BATCH-008 needs one;
  no record may claim such a quorum is satisfiable in this tree.
- Not an occasion to mark the outstanding archive-receipt defect `INT-BATCH007-T`
  repaired. It is carried forward unrepaired, so BATCH-008's archive tasks stay
  `queued` with null `commit_sha`, and no session may fabricate a receipt hash to
  route around it.
