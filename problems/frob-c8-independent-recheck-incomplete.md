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
Subsequent independent replays cover all three core object arms and the
archived first-curve C2 residue lists and C4 null-curve geometry. C3/C4
historical sample identities and complete C8 review remain open.

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
- **Observed, input inventory:** The [raw-curve inventory](../docs/reports/2026-10-22-frob-provenance-audit/audit.json)
  records two curves in each core cell (`N=1051/10061`, `30841/3701`,
  `206461/117991`). Object-arm partition entries store aggregate counts and
  ratios, not the residue lists needed for a direct tuple-by-tuple comparison.
  C2/C3 records exist only for curve index 0. An independent checker must
  reconstruct subgroup points and slot membership from the bound parameters.
- **Observed, partial arithmetic recheck:** The [audit receipt](../docs/reports/2026-10-22-frob-provenance-audit/audit.json)
  independently matches `p_m`, `U_neg`, tuple-count products, and exact cost
  ratios for extras 0, 8, and 32 in all 23 stored `ok` partition entries.
  A changed-ratio mutation is rejected. This checks arithmetic from aggregate
  counts, not the point-derived counts or C8's tuple and membership duties.
- **Observed, q11n5 object replay:** The [bounded independent receipt](../docs/reports/2026-10-22-frob-provenance-audit/split-object-replay.json)
  reclassifies all 11,110 nonidentity subgroup points on both eligible
  `FROB-SPLIT-q11n5` curves, matches every object-arm partition, and checks
  1,030 tuple identities, of which 100 are nontrivial two-slot point sums
  and 930 are singleton checks. It rejects changed
  target counts, slot sizes, and generator coordinates. The verifier reuses
  the frozen checker's field/curve primitives, not the Sage driver. No
  C2/C3/C4 arm or q13/q19 object arm is covered by this receipt.
- **Observed, all-core object replay:** The [generalized receipt](../docs/reports/2026-10-22-frob-provenance-audit/core-object-replay.json)
  constructs the frozen Frobenius-factor kernels for q11n5, q13n5 and q19n5,
  reclassifies all 370,100 nonidentity points on six eligible curves, and
  matches all 36 object partition records. It checks 20,960 tuple identities,
  including 400 nontrivial multi-slot sums. It imports only the archived
  checker's field/curve primitives and the local q11 helper, not the Sage
  driver. It has no separate q13/q19 mutation battery or C2/C3/C4 replay.
- **Observed, first-curve controls:** The [C2/C3 replay receipt](../docs/reports/2026-10-22-frob-provenance-audit/c2-c3-control-replay.json)
  reconstructs 238,350 nonidentity points on the three first eligible curves.
  It verifies the first nonstable dimension-four coordinate subspace, matches
  all three archived C2 residue lists exactly, and checks 13,242 C2 singleton
  tuple identities with signed point addition, exact counts and ratios. A
  changed archived residue is rejected. All six populated C3 records have one
  slot; a valid seeded sample reproduces their aggregate cardinalities and
  ratios and checks 26,620 generated singleton sums. The historical C3 sample
  lists are absent, so those generated sums cannot be attributed to the
  archived run. No C4 null-curve record is re-enumerated here.
- **Observed, C4 null geometry:** The [C4 replay receipt](../docs/reports/2026-10-22-frob-provenance-audit/c4-null-geometry-replay.json)
  verifies nonsingularity, the non-basefield `j` value, and the accepted
  lexicographic candidate in all three core cells. Exact point-order witnesses
  plus Hasse's interval certify the three accepted curve orders and both
  earlier rejected candidates' orders; the rejected orders have no eligible
  prime factor. All three accepted subgroup orders are exactly prime, and
  wrong-order mutations fail. The replay enumerates 143,568 null-subgroup
  points and checks six aggregate rows and 26,620 singleton sums on valid
  generated samples. The historical C4 sampled residue lists are absent, so
  those generated tuple identities cannot be attributed to the frozen run.
  The Hasse bound is used as a mathematical premise, not proved in Lean here.
- **Derived or proved:** Reading the checker's executable path against the
  [C8 design](../experiments/EXP-FROB-91ee9c/specification.yaml) shows that
  the archived checker covers a strict subset of the required independent
  checks. The run's own success rule requires all C1, C5, C6, C7 and C8 to
  pass, so it cannot be concluded from this package that the rule passed.
- **Suspected explanation:** The archived checker comments describe a fuller
  re-enumeration than its code implements. Why that gap remained in the
  archived run is unknown; the present finding rests on the code path, not
  an inferred intent.
- **Missing capability:** Bind the historical C3/C4 samples or run a fresh
  source-bound seeded control, complete remaining mutation controls and
  independent Validator review, and settle the separate source-custody gap.
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

- **Action or proof obligation:** Recover C3/C4 sample identities or perform
  a source-bound fresh seeded replay, then audit the remaining C8 items and
  the checker itself. Independently review the Hasse and point-order
  certificate logic before using it as an order verdict.
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
- 2026-10-22: A prospective, source-pinned q11n5 object-arm replay matched
  both eligible curves, 11,110 subgroup point classifications, all 30 object
  partition statuses, and 1,030 tuple identities (100 two-slot sums). Three mutation
  controls were rejected. This closes only that object-arm slice; C8 and the
  experiment success gate remain open.
- 2026-10-22: A generalized object-arm replay matched all three core cells:
  six eligible curves, 370,100 point classifications, 36 partition records,
  and 20,960 tuple identities (400 multi-slot sums). The C2/C3/C4 control
  arms and independent review remain open, so C8 and the success gate remain
  unestablished.
- 2026-10-22: A first-curve control replay matched all three archived C2
  residue lists and 13,242 singleton tuple identities. Six C3 aggregate rows
  match valid seeded samples, but the frozen sample lists were not retained;
  C4 and the C8 success gate remain open.
- 2026-10-22: The null-geometry replay certified three accepted and two
  rejected C4 curve orders using point orders plus Hasse, with exact prime
  subgroup witnesses and six aggregate rows. Frozen C4 sample lists remain
  absent; the C8 success gate is still open.
