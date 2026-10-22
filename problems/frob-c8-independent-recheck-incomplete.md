# FROB C8 independent recheck is incomplete

- **Status:** `open`
- **Kind:** independent-validation implementation gap; execution-source custody is tracked separately in [full ledger integrity](full-ledger-validation-errors.md)
- **Affected work:** [EXP-FROB-91ee9c frozen specification](../experiments/EXP-FROB-91ee9c/specification.yaml), [RUN-FROB-91ee9c-7119f2](../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/manifest.yaml), and its [scoped checker audit](../docs/reports/2026-10-22-frob-provenance-audit/REPORT.md)
- **Next action owner:** Coordinator for a prospective source-bound recheck plan; independent Validator for implementation and review
- **Last updated:** 2026-10-22

## Problem

The run cannot satisfy its frozen C8 independent-correctness control because
the archived checker does not recheck every tuple sum, slot membership,
Frobenius order, or rational identity required by the specification. Thus the
frozen success criterion for the three core cells
`FROB-SPLIT-q11n5`, `FROB-NOLATTICE-q13n5`, and `FROB-EQDEG-q19n5` is not
established, even though the original cells are recorded as completed.

The claimed scope is a toy combinatorial design axis under a frozen cost
model, with C1–C8 controls; it is not an ECDLP solve or performance claim.
The success criterion explicitly requires C8 to pass. A failed or incomplete
instrument control invalidates the instrument under the frozen decision rule;
it does not falsify the mathematical hypothesis.

## Evidence and uncertainty

- **Observed:** The [archived checker](../experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/checker.py)
  writes six `tuple_sum_reverifications` entries, but its three `ok` entries
  only find a curve point and check `[N]G=O`, a probable-prime test, and the
  Frobenius action. It skips the other three for size. It does not recompute
  tuple sumsets, `p_m`, C2/C3/C4 arms, slot membership, or rational identities.
  The [audit receipt](../docs/reports/2026-10-22-frob-provenance-audit/audit.json)
  reproduces the checker output byte for byte and verifies the three checked
  `N` values prime by exact trial division.
- **Derived or proved:** Reading the checker's executable path against the
  [C8 design](../experiments/EXP-FROB-91ee9c/specification.yaml) shows that
  the archived checker covers a strict subset of the required independent
  checks. The run's own success rule requires all C1, C5, C6, C7 and C8 to
  pass, so it cannot be concluded from this package that the rule passed.
- **Suspected explanation:** The archived checker comments describe a fuller
  re-enumeration than its code implements. Why that gap remained in the
  archived run is unknown; the present finding rests on the code path, not
  an inferred intent.
- **Missing capability:** A checker independent of the driver that can
  reconstruct and verify every required C8 item for each accepted core-cell
  tuple, including the larger subgroups and all exact rational arithmetic.
- **What this evidence does not establish:** It does not show that the
  recorded sumsets or ratios are wrong, that C8 would fail on a complete
  implementation, or that the mathematical hypothesis is false. The
  extension cell's `not_run_resource` status is separately permitted by SR-4.

## What would unblock it

- [ ] Build a separately source-bound checker or fresh replay that verifies,
  for every accepted tuple on each frozen core cell, signed point sums,
  exact slot membership, `ord(G)=N`, `ord_N(mu)=n`, every reported rational
  identity, and orbit divisibility. It must not import the driver's
  enumeration code and must emit per-item pass/fail evidence.
- [ ] Compare its output against the frozen manifest, raw and metric records,
  preserve the originals, and obtain independent Validator review of the
  checker source, limits and outputs. Resolve the execution-source custody
  gap separately before using the original driver as a bound replay source.

Meeting these conditions would decide the specified C8 control on the tested
cells. It would still leave the other success gates, control interpretation,
independent red-team review, and any downstream cost or attack claim to their
own evidence.

## Next discriminating step

- **Action or proof obligation:** Inventory the exact per-tuple and per-arm
  data needed by C8 against the frozen raw files, then implement the smallest
  independent checker that covers one complete core cell before scaling to
  all three.
- **Inputs and controls:** Use the frozen specification and hash-pinned run
  artifacts. Include deliberately altered point, slot, `N`, Frobenius
  eigenvalue, and rational fields as negative controls, plus the existing
  checker as a baseline for what it actually checks.
- **Execution limits and stop condition:** Keep the original run immutable;
  follow its fixed cell parameters, resource protection and new-run admission
  rules. Stop a replay if required source or per-tuple data cannot be bound,
  and record that missing item rather than declaring C8 passed.
- **Outcomes and next actions:** Full agreement advances to independent
  interpretation review; a reproducible mismatch requires a source-bound
  correction and scoped scientific reassessment; incomplete data or resource
  exhaustion remains inconclusive.
- **Recheck trigger:** A new independent checker/replay receipt or recovered
  contemporaneous source snapshot.

A planned check is not a completed experiment. Existing execution, review,
budget, and archival rules still govern the follow-up.

## Resolution and history

- 2026-10-22: Opened after source review of the frozen checker and exact
  byte-for-byte replay. The archived code verifies three curve witnesses,
  skips three, and recomputes no tuple sumsets or C2/C3/C4 arms. The original
  run, metrics, cost model and numerical graphs remain unchanged. Unresolved.
