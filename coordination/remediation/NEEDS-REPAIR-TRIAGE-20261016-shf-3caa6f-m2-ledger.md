# needs_repair triage: 2026-10-16, sheriff SHF-20261016-3caa6f finding M2 (ledger validator)

A control-plane note for the Coordinator. It diagnoses and proposes corrections.
It repairs no record, changes no status, and creates no superseding record:
records are immutable, and only the Coordinator changes research state
(AGENTS.md). Evidence:
`research/sheriff/SHF-20261016-3caa6f/checks/validate-ledger.txt`. Verified
against `origin/main` at `fdcdb905f`, where the validator reports the same 349
errors byte for byte.

## Result

| | New errors (beyond the 1,210 grandfathered) |
|---|---|
| `origin/main` at `fdcdb905f` | 349 |
| with branch `claude/ledger-validator-indexing` (validator indexing fix) | **287** |

All 62 removed errors were validator false positives. Each one cited an
artifact that exists, and that artifact's own schema defect is still reported
once, against itself. The fix adds no new errors, and nothing was added to the
baseline.

### Validator fixes (tooling, `tools/validate_ledger.py`, tests in `tests/test_validate_ledger_indexing.py`)

1. **Flat run manifests are now indexed.** `check_run` reported a manifest that
   has no `run:` envelope and then dropped its id, unless the manifest was in
   the legacy inventory. Every record citing the run was then reported again,
   as citing an "unknown run". The id is now registered as an alias, with the
   directory name as the run id. The alias is refused if the manifest records
   a different `run_id` or `experiment_id` from its location. **Removed 51
   `evidence references unknown run` and 4 `internal finding references
   unknown record 'RUN-*'`.**
2. **Wrong-shape specifications are indexed.** The id of
   `experiments/EXP-AUXIN-339fb0/specification.yaml` (a `successor_contract`
   document) was dropped in the same way. **Removed 5 `decision references
   unknown target 'EXP-AUXIN-339fb0'`.**
3. **Protocol amendments are indexed.** These are
   `experiments/<EXP>/amendments/AMD-*.yaml`, a documented part of the
   experiment package (`docs/evidence-and-reproducibility.md`). An amendment is
   indexed only when its `amendment.id` equals its filename stem. **Removed 2
   `internal finding references unknown record 'AMD-*'`.**
4. **Knowledge findings now consult `legacy_aliases`**, as the evidence
   `run_ids` check already does. Before this change, a finding citing a frozen
   run failed while an evidence record citing the same run passed.
5. **Runs with only `manifest.json` are indexed.** Non-legacy run directories
   whose only manifest is `manifest.json` were never scanned. They are now
   indexed, and the missing canonical `manifest.yaml` is reported as an
   **advisory** (`json-only run`, 75 directories; list them with
   `--advisories`). It is not reported as an error: none of these was
   schema-checked before, and the prune-only baseline cannot absorb them. This
   fix closes 4 citation errors (`RUN-ECDLP-502ae2-01`,
   `RUN-ECDLP-f49f75-01..03`). Promoting the advisory to an error is a separate
   decision, best taken after their supersessions land.

## Root-cause classification of all 349

| Original message | Count | Root cause | Remaining |
|---|---:|---|---:|
| `expected top-level key 'run'` | 65 | Genuine: a flat run manifest that is not in the run supersession registry (A) | 65 |
| `expected top-level key 'experiment'` | 1 | Genuine: `EXP-AUXIN-339fb0` spec is a generated `successor_contract` draft (B) | 1 |
| `missing required field` (spec) | 48 | Genuine: specs lack `budget`/`hypothesis_id`/`version`/`success_criterion` (C) | 48 |
| `missing required field 'knowledge_promotion'` | 6 | Genuine: decisions (D) | 6 |
| `evidence references unknown run` | 53 | **51 validator** (flat or JSON-only manifests not indexed); 2 genuine (K) | 2 |
| `decision references unknown target` | 10 | **5 validator** (EXP-AUXIN-339fb0); 5 genuine: drafts never filed under `experiments/` (J) | 5 |
| `internal finding references unknown record` | 7 | **6 validator** (4 flat runs, 2 amendments); 1 genuine (L) | 1 |
| citations provenance / verified_by / novelty | 28 | Genuine (E). Validator matches `templates/research-records.md` | 28 |
| `prior_art.*` | 66 | Genuine (F). Validator matches `templates/research-records.md` "Prior art on ideas" | 66 |
| `review_plan.*` | 37 | Genuine (G). Free text or incomplete plans on handoffs | 37 |
| `registered ... run manifest hash changed` | 4 | Genuine: immutability breach (H) | 4 |
| run manifest incomplete (`run missing required field`, `certificate.kind`, `code.*`, `missing artifact`) | 20 | Genuine (I). Validator matches `schemas/run-manifest.schema.json` | 20 |
| approved spec null criteria / missing `decision_impact` | 3 | Genuine (C) | 3 |
| `invalid YAML` | 1 | Genuine: `DEC-20261016-5d2fb8` is finding M1, handled by another session. Not touched here | 1 |
| **Total** | **349** | **62 validator, 287 records** | **287** |

I checked for schema drift where the validator lags the documented schema,
and found none that produces any of the 287. The `prior_art`, `citations` and
`review_plan` rules match `templates/research-records.md`. The spec required
fields match `schemas/experiment.schema.json`. The run fields match
`schemas/run-manifest.schema.json`. The `certificate.kind` message text omits
`key_recovery`, but the check itself accepts it, and none of the 4 errors uses
it.

## Proposed corrections, by category (Coordinator decides; nothing here is done)

- **A. Flat run manifests (65).** These 18 already have a nested, id-consistent
  `manifest_v2.yaml` beside them that was never registered. Registering each
  pair (both sha256 values) in `tools/run_supersession_registry.yaml` as
  `additive_schema_completion` would clear 18 errors without writing any new
  record:
- `experiments/EXP-BINSTD-27f623/runs/RUN-BINSTD-60aff6/`
- `experiments/EXP-BINSTD-27f623/runs/RUN-BINSTD-95fcfd/`
- `experiments/EXP-BINSTD-27f623/runs/RUN-BINSTD-d15ac1/`
- `experiments/EXP-BINSTD-4b846c/runs/RUN-BINSTD-2dc695/`
- `experiments/EXP-BINSTD-4b846c/runs/RUN-BINSTD-ae1529/`
- `experiments/EXP-BINSTD-4b846c/runs/RUN-BINSTD-b3d5d2/`
- `experiments/EXP-BINSTD-6cca48/runs/RUN-BINSTD-6dad8a/`
- `experiments/EXP-BINSTD-6cca48/runs/RUN-BINSTD-c2d2c4/`
- `experiments/EXP-BINSTD-6fd454/runs/RUN-BINSTD-590471/`
- `experiments/EXP-BINSTD-6fd454/runs/RUN-BINSTD-710bab/`
- `experiments/EXP-BINSTD-871156/runs/RUN-BINSTD-2fe6ed/`
- `experiments/EXP-BINSTD-871156/runs/RUN-BINSTD-e717e6/`
- `experiments/EXP-BINSTD-9b18fc/runs/RUN-BINSTD-54a677/`
- `experiments/EXP-BINSTD-9b18fc/runs/RUN-BINSTD-6e9fde/`
- `experiments/EXP-BINSTD-a8bfd8/runs/RUN-BINSTD-441e0e/`
- `experiments/EXP-BINSTD-a8bfd8/runs/RUN-BINSTD-b2d17e/`
- `experiments/EXP-BINSTD-eb9e5e/runs/RUN-BINSTD-b819fc/`
- `experiments/EXP-BINSTD-eb9e5e/runs/RUN-BINSTD-f0b4ee/`

  The other 47 need a new `manifest_v2.yaml` built only from archived
  companions, plus a registry row: EXP-ECTD-0cf008 (14), EXP-QSP-70b731 (14),
  EXP-BINSTD-591d28 (5), EXP-BINSTD-8bdf86 (4), EXP-AUXIN-fef6ac (2),
  EXP-BINSTD-6f3434 (2), EXP-BINSTD-9001b3 (2), EXP-CSIDH-999626 (2),
  EXP-BINSTD-a33de2 (1), EXP-SEMBIN-d830d5 (1). This follows the precedent of
  `d9ccb72fa` for EXP-ECDLP-7d2a86. Root cause upstream: experiment-specific
  drivers write flat manifests. `docs/experiment-execution.md` says "the driver
  writes the canonical manifest", so the run skill's preflight should refuse a
  flat one.
- **B. `EXP-AUXIN-339fb0` spec (1).** A generated draft
  (`build_successor.py`, `approved_by: null`). Proposed fix: a schema
  supersession (`tools/schema_supersession_registry.yaml`) to a canonical
  `experiment:` rendering, or a redirect if the experiment is retired.
- **C. Spec required fields (51).** EXP-PRECOMP-001..013 lack `version`,
  `hypothesis_id` and `budget`. EXP-GLV{CAN,F,FB,FF,INV,LP,PRE,SAT} lack
  `budget`. Budgets are advisory and may be null, but the key must be present,
  with a note when null. EXP-ECDLP-daee4d uses `success_criteria` and
  `falsification_criteria` (plural), lacks `decision_impact`, and is `approved`
  with null singular fields. Proposed fix: schema supersession per spec
  (`budget: null` + `budget_note`, `hypothesis_id: null` + note, `version: 1`).
  For daee4d, Coordinator review is needed, because it is approved.
- **D. `knowledge_promotion` missing on 6 decisions** (DEC-20261003-054ae8,
  -efb053, DEC-20261011-10f209, -5d5428, DEC-20261015-a08389, -ab6f23).
  Proposed fix: superseding decision records that state `knowledge_promotion`
  (usually `none`).
- **E. Citation provenance (28, 6 proposals).** An `internal` citation needs
  `verified_by`, and a `recalled` citation is incompatible with `adaptation`.
  Proposed fix: superseding proposals with `verified_by` named, or
  `novelty_status: unverified`.
- **F. `prior_art` blocks (66, 12 proposals).** The blocks use free-text
  `relation`, have no `provenance`, cite `IDEA-*` or `EXP-* arm D` refs
  instead of KR-*/KN-* entries, and give `frontier_map` as prose (e.g.
  `knowledge/frontiers/ecdlp/index-calculus (24 rows, pasted verbatim ...)`).
  IDEA-20261003-94078e and -c9c6c3 have no block. Proposed fix: superseding
  proposals with a conforming block. An internal predecessor idea belongs in
  `searched`, or should be promoted to a KN-FIND entry first. Agent
  contract: `agents/idea-generator.md` already requires the template.
- **G. `review_plan` (37, 19 handoffs).** Seven handoffs carry prose ("Not this
  card. A later independent review reads the manifest after the run.") where
  the field expects null or a path. Others have incomplete plans
  (TASK-20261003-308fcf alone has 14 errors). Proposed fix: superseding
  handoffs. Set `review_plan: null` on non-opening handoffs, and complete the
  plan on the round-opening one.
- **H. Hash-pinned run manifests changed after registration (4). This is an
  immutability breach, and the highest priority.**
  `RUN-ECDLP-02af0e` and `RUN-ECDLP-fc4eff` `manifest_v2.yaml` were registered
  at 286df4b2/9fdb3725 in `d9ccb72fa`. The concurrent snapshot commit
  `6ddbeab1b` ("Stages 0-1 run artifacts + schema repair") committed different
  bytes. `RUN-SEMBIN-9000a8` and `RUN-SEMBIN-bd538f` `manifest.yaml` were
  registered at 57b51317/fd62bd3f in `170cbce82`. The merge `792f5b718`
  (conflict resolution) replaced them. Proposed fix: determine which bytes are
  authoritative, then write a CORR-* reconciliation. Either restore the
  registered bytes, or register a new supersession that pins the current bytes
  and keeps the old ones. These same 4 cause the 3 failing
  `tools/test_run_supersession.py::CommittedRegistryTests` tests on main.
- **I. Nested run manifests incomplete (20, 6 runs).** RUN-AES-0739d9 and
  RUN-AES-a36d0b have no `environment`, `inputs`, `timing` or `result`
  (`certificate` sits at `run.certificate`). RUN-BINSTD-51ad99 and -e55dcf v2
  have `certificate.kind: integer_catalog_check`. TASK-20260914-7119f2 under
  EXP-FROB-91ee9c has no `environment` or `code.commit`/`command`, and its
  directory is named for a task, not a run. RUN-QSP-33b442-S0 has no
  companions (`command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
  `raw-result.json`). Proposed fix: `additive_schema_completion` supersessions
  where archived companions hold the data. Where they don't, record a
  provenance gap.
- **J. Decisions targeting never-filed drafts (5).** DEC-20260929-21bb51 and
  -7efa82 target EXP-AUXIN-bafa2e. DEC-20260929-4eade7 targets -369078,
  -93fc4d targets -55c6c0, and -cfb294 targets -92dccc. These were refused
  drafts that exist only as design packages under
  `coordination/goals/GOAL-AUXIN-a93442/batches/*/design/`. Proposed fix: a
  Coordinator ruling. Either superseding decisions move the draft ids from
  `target_ids` to a non-target field, or the Coordinator rules that the
  validator should index design-package draft ids. That would be a tooling
  change, and I have not made it.
- **K. Evidence citing a run with no record (2).** EV-QSP-2c78d3 cites
  RUN-QSP-715b58, whose directory has companions but no manifest. EV-SEMBIN-3e91a7
  cites RUN-SEMBIN-9ecb77, which has no run directory. This one is tied to
  finding M1, DEC-20261016-5d2fb8, and is left to that session. Proposed fix:
  build a manifest from the RUN-QSP-715b58 companions, and supersede or retract
  the citation to 9ecb77.
- **L. Finding citing an unrecorded task (1).** KN-FIND-0e3ed0 cites
  TASK-20261003-6e0c8a. A decision names it as `review_task`, but no handoff
  record exists. Proposed fix: file the handoff, or supersede the finding's
  `internal_refs`.

## Absolute gate: evaluated, not implemented

The push-to-`main` step in `.github/workflows/validate.yml` already runs
`python3 tools/validate_ledger.py` absolutely, failing on any error beyond the
baseline, so `main` is red today. The pull-request step is differential
(`tools/ci_ledger_gate.py`). It fails a PR only for errors the PR introduces,
which is how 349 accumulated on `main` unnoticed. An absolute PR gate ("new
errors must not exceed 0") cannot pass now, because 287 remain. It cannot be
made to pass by refreshing the baseline either: that would silently
grandfather the 287, and the baseline is prune-only by design. A count
ratchet, failing a PR when head's count exceeds base's, would be about 5 lines
in the workflow. It adds little over the existing identity-based differential
gate, so I have not implemented it. Recommended order: land corrections A
through L, and the absolute PR gate then becomes a one-line change
(`python3 tools/validate_ledger.py` in both branches).

## Per-record defect list (287 errors, 148 records)

| Record | Defect(s) |
|---|---|
| `ledger/proposals/IDEA-20260920-b9f0c5.yaml` | citations[i].provenance is 'internal' and requires verified_by naming the agent that read the source (x5) |
| `ledger/proposals/IDEA-20261003-43f871.yaml` | prior_art.nearest[i].ref 'IDEA-20261003-f20e41' must resolve to a KR-* row or a knowledge/ entry |
| `ledger/proposals/IDEA-20261003-4f41d0.yaml` | prior_art.nearest[i].ref 'IDEA-20261003-43f871' must resolve to a KR-* row or a knowledge/ entry |
| `ledger/proposals/IDEA-20261003-94078e.yaml` | citations[i] is provenance 'recalled' but novelty_status is 'adaptation'; use 'unverified' until the source is read; prior_art is required for ideas from IDEA-20261001 on: name the known-result rows checked and the nearest prior work (knowledge/frontiers/ecdlp/README.md) |
| `ledger/proposals/IDEA-20261003-c9c6c3.yaml` | citations[i] is provenance 'recalled' but novelty_status is 'adaptation'; use 'unverified' until the source is read; prior_art is required for ideas from IDEA-20261001 on: name the known-result rows checked and the nearest prior work (knowledge/frontiers/ecdlp/README.md) |
| `ledger/proposals/IDEA-20261006-486aa2.yaml` | prior_art.frontier_map 'knowledge/frontiers/ecdlp/index-calculus (24 rows, pasted verbatim 2026-10-06)' is not a directory; prior_art.nearest[i].provenance must be recalled\|retrieved\|kb\|internal (x3); prior_art.nearest[i].relation must be one of ['adjacent', 'generalizes', 'orthogonal', 'same', 'special_case'] (x3) |
| `ledger/proposals/IDEA-20261006-839ced.yaml` | prior_art.frontier_map 'knowledge/frontiers/ecdlp/index-calculus (24 rows, pasted verbatim 2026-10-06)' is not a directory; prior_art.nearest[i].provenance must be recalled\|retrieved\|kb\|internal (x3); prior_art.nearest[i].relation must be one of ['adjacent', 'generalizes', 'orthogonal', 'same', 'special_case'] (x3) |
| `ledger/proposals/IDEA-20261006-8f4f02.yaml` | prior_art.frontier_map 'knowledge/frontiers/ecdlp/index-calculus (24 rows, pasted verbatim 2026-10-06)' is not a directory; prior_art.nearest[i].provenance must be recalled\|retrieved\|kb\|internal (x3); prior_art.nearest[i].relation must be one of ['adjacent', 'generalizes', 'orthogonal', 'same', 'special_case'] (x3) |
| `ledger/proposals/IDEA-20261006-ef3939.yaml` | prior_art.frontier_map 'knowledge/frontiers/ecdlp/index-calculus (24 rows, pasted verbatim 2026-10-06)' is not a directory; prior_art.nearest[i].provenance must be recalled\|retrieved\|kb\|internal (x4); prior_art.nearest[i].relation must be one of ['adjacent', 'generalizes', 'orthogonal', 'same', 'special_case'] (x4) |
| `ledger/proposals/IDEA-20261016-7a138a.yaml` | prior_art.frontier_map must be a knowledge/frontiers/... path or 'not_applicable'; prior_art.nearest[i].ref 'EXP-SEMBIN-92724f arm D' must resolve to a KR-* row or a knowledge/ entry; prior_art.nearest[i].provenance must be recalled\|retrieved\|kb\|internal (x2); prior_art.nearest[i].relation must be one of ['adjacent', 'generalizes', 'orthogonal', 'same', 'special_case'] (x2); prior_art.nearest[i].ref 'KR-IC-e847d1 crossbred' must resolve to a KR-* row or a knowledge/ entry |
| `ledger/proposals/IDEA-20261016-bb92bd.yaml` | prior_art.frontier_map must be a knowledge/frontiers/... path or 'not_applicable'; prior_art.nearest[i].ref 'IDEA-20261006-839ced' must resolve to a KR-* row or a knowledge/ entry; prior_art.nearest[i].provenance must be recalled\|retrieved\|kb\|internal (x2); prior_art.nearest[i].relation must be one of ['adjacent', 'generalizes', 'orthogonal', 'same', 'special_case'] (x2); prior_art.nearest[i].ref 'IDEA-20261006-8f4f02' must resolve to a KR-* row or a knowledge/ entry |
| `ledger/proposals/IDEA-20261016-d0335b.yaml` | prior_art.frontier_map must be a knowledge/frontiers/... path or 'not_applicable'; prior_art.nearest[i].ref 'EXP-SEMBIN-7e1371 / c2c312' must resolve to a KR-* row or a knowledge/ entry; prior_art.nearest[i].provenance must be recalled\|retrieved\|kb\|internal (x4); prior_art.nearest[i].relation must be one of ['adjacent', 'generalizes', 'orthogonal', 'same', 'special_case'] (x4); prior_art.nearest[i].ref 'IDEA-20260918-c05e71 / EXP-SEMBIN-d830d5' must resolve to a KR-* row or a knowledge/ entry |
| `ledger/proposals/IDEA-20261016-e191a8.yaml` | prior_art.frontier_map must be a knowledge/frontiers/... path or 'not_applicable'; prior_art.nearest[i].ref 'Semaev Sec 4.5 / KR-IC-889857' must resolve to a KR-* row or a knowledge/ entry; prior_art.nearest[i].provenance must be recalled\|retrieved\|kb\|internal (x2); prior_art.nearest[i].relation must be one of ['adjacent', 'generalizes', 'orthogonal', 'same', 'special_case'] (x2); prior_art.nearest[i].ref 'IDEA-20260913-352163' must resolve to a KR-* row or a knowledge/ entry |
| `ledger/evidence/EV-BINSTD-030b4e.yaml` | citations[i].provenance is 'internal' and requires verified_by naming the agent that read the source (x5) |
| `ledger/evidence/EV-BINSTD-0db227.yaml` | citations[i].provenance is 'internal' and requires verified_by naming the agent that read the source (x7) |
| `ledger/evidence/EV-BINSTD-9ac9c5.yaml` | citations[i].provenance is 'internal' and requires verified_by naming the agent that read the source (x9) |
| `ledger/decisions/DEC-20261003-054ae8.yaml` | missing required field 'knowledge_promotion' |
| `ledger/decisions/DEC-20261003-efb053.yaml` | missing required field 'knowledge_promotion' |
| `ledger/decisions/DEC-20261011-10f209.yaml` | missing required field 'knowledge_promotion' |
| `ledger/decisions/DEC-20261011-5d5428.yaml` | missing required field 'knowledge_promotion' |
| `ledger/decisions/DEC-20261015-a08389.yaml` | missing required field 'knowledge_promotion' |
| `ledger/decisions/DEC-20261015-ab6f23.yaml` | missing required field 'knowledge_promotion' |
| `ledger/decisions/DEC-20261016-5d2fb8.yaml` | invalid YAML: while scanning a simple key |
| `ledger/handoffs/TASK-20260910-19bd7b.yaml` | review_plan.blind_rederivation.assigned_to is required when required is true |
| `ledger/handoffs/TASK-20260910-2c0931.yaml` | review_plan.proves_too_much.objects is required; the argument is run against objects where its conclusion is known false, as controls-before-belief for an argument |
| `ledger/handoffs/TASK-20260910-4abecd.yaml` | review_plan.blind_rederivation.assigned_to is required when required is true |
| `ledger/handoffs/TASK-20260910-59d885.yaml` | review_plan.blind_rederivation.assigned_to is required when required is true |
| `ledger/handoffs/TASK-20260910-6d6bd3.yaml` | review_plan.claim_under_review is required; the prior is recorded before the round so concurrence can be told apart from agreement with the Coordinator; review_plan.coordinator_prior is required; the prior is recorded before the round so concurrence can be told apart from agreement with the Coordinator; review_plan.joints must be a nonempty list; a review with no named load-bearing step cannot show coverage; review_plan.proves_too_much.objects is required; the argument is run against objects where its conclusion is known false, as controls-before-belief for an argument |
| `ledger/handoffs/TASK-20260910-c8cb36.yaml` | review_plan.blind_rederivation.assigned_to is required when required is true |
| `ledger/handoffs/TASK-20260913-9863af.yaml` | review_plan.blind_rederivation.assigned_to is required when required is true |
| `ledger/handoffs/TASK-20261003-308fcf.yaml` | review_plan.claim_under_review is required; the prior is recorded before the round so concurrence can be told apart from agreement with the Coordinator; review_plan.joints[i].joint is empty (x4); review_plan.joints[i] has no assigned_to; an unowned joint is the coverage gap this plan exists to make visible (x4); review_plan.joints[i] has no attack_plan; a worked attack returns a result either way, 'review this' returns an opinion (x4); review_plan.proves_too_much.objects is required; the argument is run against objects where its conclusion is known false, as controls-before-belief for an argument |
| `ledger/handoffs/TASK-20261003-46fb77.yaml` | review_plan.proves_too_much.objects is required; the argument is run against objects where its conclusion is known false, as controls-before-belief for an argument |
| `ledger/handoffs/TASK-20261003-478a3c.yaml` | review_plan.proves_too_much.objects is required; the argument is run against objects where its conclusion is known false, as controls-before-belief for an argument |
| `ledger/handoffs/TASK-20261003-68bcf5.yaml` | review_plan.blind_rederivation.quantity is required when required is true; review_plan.blind_rederivation.assigned_to is required when required is true; review_plan.blind_rederivation.blind_from is required; name the producer's implementation, notes and report, or the independence is not checkable |
| `ledger/handoffs/TASK-20261003-6edf51.yaml` | review_plan.proves_too_much.failure_signature is required; state what the argument must do on a known-false object or the control cannot fail |
| `ledger/handoffs/TASK-20261012-4cebfe.yaml` | review_plan path does not exist: Not this card. A later independent review reads the manifest after the run. |
| `ledger/handoffs/TASK-20261012-739d5b.yaml` | review_plan path does not exist: Not this card. A later independent review reads the manifest after the run. |
| `ledger/handoffs/TASK-20261012-9e8997.yaml` | review_plan path does not exist: Not this card. A later independent review reads the manifest after the run. |
| `ledger/handoffs/TASK-20261012-a25520.yaml` | review_plan path does not exist: Not this card. A later independent review reads the manifest after the run. |
| `ledger/handoffs/TASK-20261012-e42be3.yaml` | review_plan path does not exist: Not this card. A later independent review reads the manifest after the run. |
| `ledger/handoffs/TASK-20261012-eb1dae.yaml` | review_plan path does not exist: Not this card. A later independent review reads the manifest after the run. |
| `ledger/handoffs/TASK-20261012-f63559.yaml` | review_plan path does not exist: Not this card. A later independent review reads the manifest after the run. |
| `experiments/EXP-AUXIN-339fb0/specification.yaml` | expected top-level key 'experiment' |
| `experiments/EXP-ECDLP-daee4d/specification.yaml` | missing required field 'success_criterion'; approved experiment has null 'success_criterion'; approved experiment has null 'falsification_criterion'; missing 'decision_impact' (on_positive/on_negative): say before the run what each outcome changes |
| `experiments/EXP-GLVCAN-468fb2/specification.yaml` | missing required field 'budget' |
| `experiments/EXP-GLVF-8dee36/specification.yaml` | missing required field 'budget' |
| `experiments/EXP-GLVFB-5f287d/specification.yaml` | missing required field 'budget' |
| `experiments/EXP-GLVFF-3b7a1c/specification.yaml` | missing required field 'budget' |
| `experiments/EXP-GLVINV-94a550/specification.yaml` | missing required field 'budget' |
| `experiments/EXP-GLVLP-8a5d31/specification.yaml` | missing required field 'budget' |
| `experiments/EXP-GLVPRE-4c9f62/specification.yaml` | missing required field 'budget' |
| `experiments/EXP-GLVSAT-71d2e8/specification.yaml` | missing required field 'budget' |
| `experiments/EXP-PRECOMP-001/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-002/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-003/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-004/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-005/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-006/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-007/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-008/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-009/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-010/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-011/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-012/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-PRECOMP-013/specification.yaml` | missing required field 'hypothesis_id'; missing required field 'version'; missing required field 'budget' |
| `experiments/EXP-ECDLP-7d2a86/runs/RUN-ECDLP-02af0e/manifest_v2.yaml` | registered superseding run manifest hash changed (registry pins 286df4b2, found b3217b78); supersede it instead of editing it |
| `experiments/EXP-ECDLP-7d2a86/runs/RUN-ECDLP-fc4eff/manifest_v2.yaml` | registered superseding run manifest hash changed (registry pins 9fdb3725, found c3b0c99a); supersede it instead of editing it |
| `experiments/EXP-SEMBIN-509d41/runs/RUN-SEMBIN-9000a8/manifest.yaml` | registered superseded run manifest hash changed (registry pins 57b51317, found ff89e695); supersede it instead of editing it |
| `experiments/EXP-SEMBIN-509d41/runs/RUN-SEMBIN-bd538f/manifest.yaml` | registered superseded run manifest hash changed (registry pins fd62bd3f, found efd7cb68); supersede it instead of editing it |
| `experiments/EXP-AES-14352a/runs/RUN-AES-0739d9/manifest.yaml` | run missing required field 'environment'; run missing required field 'inputs'; run missing required field 'timing'; run missing required field 'result'; run.result.certificate.kind must be one of discrete_log\|decomposition\|none |
| `experiments/EXP-AES-14352a/runs/RUN-AES-a36d0b/manifest.yaml` | run missing required field 'environment'; run missing required field 'inputs'; run missing required field 'timing'; run missing required field 'result'; run.result.certificate.kind must be one of discrete_log\|decomposition\|none |
| `experiments/EXP-AUXIN-fef6ac/runs/RUN-AUXIN-69eec8/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-AUXIN-fef6ac/runs/RUN-AUXIN-aa27b4/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-27f623/runs/RUN-BINSTD-60aff6/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-27f623/runs/RUN-BINSTD-95fcfd/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-27f623/runs/RUN-BINSTD-d15ac1/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-4b846c/runs/RUN-BINSTD-2dc695/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-4b846c/runs/RUN-BINSTD-ae1529/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-4b846c/runs/RUN-BINSTD-b3d5d2/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-591d28/runs/RUN-BINSTD-2b5b2c/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-591d28/runs/RUN-BINSTD-3849a9/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-591d28/runs/RUN-BINSTD-453b8d/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-591d28/runs/RUN-BINSTD-d4a2b8/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-591d28/runs/RUN-BINSTD-f7ca97/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-6cca48/runs/RUN-BINSTD-6dad8a/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-6cca48/runs/RUN-BINSTD-c2d2c4/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-6f3434/runs/RUN-BINSTD-95b5eb/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-6f3434/runs/RUN-BINSTD-970fc9/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-6fd454/runs/RUN-BINSTD-590471/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-6fd454/runs/RUN-BINSTD-710bab/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-871156/runs/RUN-BINSTD-2fe6ed/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-871156/runs/RUN-BINSTD-e717e6/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-8bdf86/runs/RUN-BINSTD-43abd4/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-8bdf86/runs/RUN-BINSTD-6f1bcc/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-8bdf86/runs/RUN-BINSTD-a2a24c/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-8bdf86/runs/RUN-BINSTD-f4d6e3/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-9001b3/runs/RUN-BINSTD-31cc54/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-9001b3/runs/RUN-BINSTD-aead63/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-9b18fc/runs/RUN-BINSTD-54a677/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-9b18fc/runs/RUN-BINSTD-6e9fde/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-a33de2/runs/RUN-BINSTD-113958/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-a8bfd8/runs/RUN-BINSTD-441e0e/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-a8bfd8/runs/RUN-BINSTD-b2d17e/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-eb9e5e/runs/RUN-BINSTD-b819fc/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-eb9e5e/runs/RUN-BINSTD-f0b4ee/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-BINSTD-fdd2d9/runs/RUN-BINSTD-51ad99/manifest_v2.yaml` | run.result.certificate.kind must be one of discrete_log\|decomposition\|none |
| `experiments/EXP-BINSTD-fdd2d9/runs/RUN-BINSTD-e55dcf/manifest_v2.yaml` | run.result.certificate.kind must be one of discrete_log\|decomposition\|none |
| `experiments/EXP-CSIDH-999626/runs/RUN-CSIDH-2ea205/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-CSIDH-999626/runs/RUN-CSIDH-8701fb/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-26c17c/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-26d06d/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-375652/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-426674/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-4cdc0a/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-509251/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-5a22e4/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-69b263/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-8231ef/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-84a499/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-bf5901/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-c769f1/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-f395a9/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-ECTD-0cf008/runs/RUN-ECTD-fd922d/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2/manifest.yaml` | run missing required field 'environment'; run.code.commit missing (not reproducible); run.code.command missing (not reproducible) |
| `experiments/EXP-QSP-33b442/runs/RUN-QSP-33b442-S0/manifest_v2.yaml` | run directory missing artifact 'command.txt'; run directory missing artifact 'environment.json'; run directory missing artifact 'stdout.log'; run directory missing artifact 'stderr.log'; run directory missing artifact 'raw-result.json' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-097ecd/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-10586d/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-1df59e/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-26c91a/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-2e1ff8/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-327529/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-383952/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-5a4afd/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-7dd37b/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-86e0d2/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-9312f7/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-a6dab8/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-a96be8/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-QSP-70b731/runs/RUN-QSP-ffed3c/manifest.yaml` | expected top-level key 'run' |
| `experiments/EXP-SEMBIN-d830d5/runs/RUN-SEMBIN-a1bd6e/manifest.yaml` | expected top-level key 'run' |
| `knowledge/findings/KN-FIND-0e3ed0.md` | internal finding references unknown record 'TASK-20261003-6e0c8a' |
| `ledger/evidence/EV-QSP-2c78d3.yaml` | evidence references unknown run 'RUN-QSP-715b58' |
| `ledger/evidence/EV-SEMBIN-3e91a7.yaml` | evidence references unknown run 'RUN-SEMBIN-9ecb77' |
| `ledger/decisions/DEC-20260929-21bb51.yaml` | decision references unknown target 'EXP-AUXIN-bafa2e' |
| `ledger/decisions/DEC-20260929-4eade7.yaml` | decision references unknown target 'EXP-AUXIN-369078' |
| `ledger/decisions/DEC-20260929-7efa82.yaml` | decision references unknown target 'EXP-AUXIN-bafa2e' |
| `ledger/decisions/DEC-20260929-93fc4d.yaml` | decision references unknown target 'EXP-AUXIN-55c6c0' |
| `ledger/decisions/DEC-20260929-cfb294.yaml` | decision references unknown target 'EXP-AUXIN-92dccc' |
