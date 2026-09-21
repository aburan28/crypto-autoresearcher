# Validator Report: BATCH-d8bb19 Idea Generator Task

**Task ID:** TASK-20260807-d8bb19-idea
**Batch ID:** BATCH-d8bb19
**Validator:** TASK-20260807-d8bb19-validator
**Date:** 2026-08-07
**Verdict:** FAIL

---

## Per-Check Results

### 1. Artifact Completeness: PASS

All 6 required files are present:

| File | Present |
|------|---------|
| `ledger/proposals/IDEA-ISO-7f3e2d.yaml` | Yes |
| `ledger/proposals/IDEA-ISO-a4c8e1.yaml` | Yes |
| `ledger/proposals/IDEA-ISO-f9b2d3.yaml` | Yes |
| `.../tasks/TASK-20260807-d8bb19-idea/idea_report.md` | Yes |
| `.../batches/BATCH-d8bb19/batch.yaml` | Yes |
| `.../batches/BATCH-d8bb19/dispatch_queue.json` | Yes |

### 2. Schema Compliance: FAIL (minor defects)

All three YAML files contain the required fields from the idea template:
`id`, `question_id`, `added`, `title`, `class`, `claim`, `mechanism`,
`novelty_status`, `novelty_note`, `avoids_tate_obstruction`,
`avoids_tate_obstruction_reason`, `assumptions`, `heuristic_assumptions`,
`predictions`, `minimal_test`, `falsification_conditions`, `confounders`,
`interpretation_limits`, `dominated_by`, `sota_delta`, `target_complexity`,
`estimated_cost`, `recommended_priority`, `proof_search_map`, `scope`.

**Defects found:**
- **Duplicate `novelty_status` key** in all three files:
  - `IDEA-ISO-7f3e2d.yaml`: lines 49 and 166
  - `IDEA-ISO-a4c8e1.yaml`: lines 49 and 159
  - `IDEA-ISO-f9b2d3.yaml`: lines 53 and 174
  YAML spec: duplicate keys are undefined behavior; most parsers silently take the last value.

### 3. ID Allocation: FAIL (critical defect)

All three identifiers are **malformed** per `tools/allocate_id.py --check`:

```
IDEA-ISO-7f3e2d  -> REFUSE: malformed
IDEA-ISO-a4c8e1  -> REFUSE: malformed
IDEA-ISO-f9b2d3  -> REFUSE: malformed
```

The expected pattern is `^IDEA-\d{8}-(?:\d{3}|[0-9a-f]{6})$`. The area code
`ISO` contains no date component. Per AGENTS.md rule 14, identifiers must be
minted via `python3 tools/allocate_id.py --next <type> --area|--date <x>` and
confirmed with `--check` before use. These IDs were not properly allocated.

**Severity:** Critical. Per AGENTS.md rule 14: "REFUSE: malformed. Do not
author a record under this id." The ledger cannot validate or reference these
records.

### 4. Write Scope: PASS

Files written:
- `ledger/proposals/IDEA-ISO-*.yaml` — within `ledger/proposals/` scope
- `.../tasks/TASK-20260807-d8bb19-idea/idea_report.md` — within declared task scope

No writes outside the declared `write_scope`.

### 5. Completion Gates: PASS

All four gates from `batch.yaml` are met:

| Gate | Met? | Evidence |
|------|------|----------|
| At least one proposal with falsifiable experimental test | Yes | Three proposals, each with `minimal_test` and `falsification_conditions` |
| Explicit dominated_by / sota_delta vs Pollard rho | Yes | All three have `dominated_by: Pollard rho at exponent 1/2` and `sota_delta` blocks |
| Mechanism avoids Tate theorem obstruction | Yes | All three have `avoids_tate_obstruction: true` with reasoning |
| OR recommendation to close SG-ECDLP-002 with named obstruction | Yes | Report recommends closure with four named obstructions |

### 6. Procedural Compliance: FAIL

- **ID allocation violation:** The idea generator did not use `allocate_id.py` to mint IDs. The `IDEA-ISO-*` format does not conform to the required pattern. This violates AGENTS.md rule 14.
- **Duplicate YAML keys:** All three files contain duplicate `novelty_status` keys, indicating insufficient self-review.
- Otherwise, the handoff contract was followed: the task objective was addressed, the report references the parent decision (DEC-20260804-2fae6a), and the proposals address the required directions (DIR-2, DIR-3).

---

## Summary of Defects

| # | Severity | Defect | Affected Files |
|---|----------|--------|----------------|
| 1 | **Critical** | Malformed IDs: `IDEA-ISO-{7f3e2d,a4c8e1,f9b2d3}` do not match `^IDEA-\d{8}-(?:\d{3}|[0-9a-f]{6})$` | All three proposal YAMLs |
| 2 | Minor | Duplicate `novelty_status` key in YAML | All three proposal YAMLs |

---

## Required Remediation

1. **Re-allocate IDs** using `python3 tools/allocate_id.py --next idea --date 20260807` and confirm each with `--check`. Update the `id` field in each YAML and rename the files accordingly. Update all cross-references in `idea_report.md`.
2. **Remove duplicate `novelty_status` keys** from all three files (keep the second value, which is the intended one).

---

## Final Verdict

**FAIL** — Critical ID allocation defect. The proposals are substantively complete and meet all completion gates, but the malformed identifiers prevent ledger integration. Remediation is straightforward (re-allocate IDs, fix duplicate keys).
