This operational inventory is bound to Git source commit
`3d69283a97f1cf418074da752384c9048df5a083` in
`/Volumes/SSD990/1083/pending-ideas-swarm-20260907`. It contains zero scientific
runs, experiment approvals, task admissions, and research status changes.
The parent Coordinator owns archival and the next research action. The exact
tool and policy hashes are recorded in `scan-receipt.json`, SHA256
`7509bac4ae6094db864b367e87ea3f4563f256282698263736b534a58424305f`.

The all-pending discovery universe contains **2,314 identifiers at 2,460 source
locations**, with every discovered source status retained. This consists of
1,879 identifiers from the primary proposal directories and 435 additional
identifiers discovered through legacy and archived layouts. It is not a verified
count of pending work. The latter remains null because lifecycle, effective
approval, semantic scope, claims, and completion authority were not adjudicated.
Both tools have discovery gaps, so this is not a claim that every possible
unminted or unrecognized idea layout has been counted.

Use `overview.json` for the compact totals, `summary.json` for the partition
counts and exact status vocabulary, and `worklist.json.gz` for all 2,314 rows.
Every worklist row retains its source locations, literal status presence,
classification evidence, the two tools' link paths, source-linked task ownership
candidates, and unresolved reconciliation signals. Historical status strings
containing rejection or closure language are copied observations; this report
does not adopt or independently validate those conclusions.

| Observation | Count | Meaning |
| --- | ---: | --- |
| Identifiers with literal `proposed` | 1,561 | Explicit recorded status, requiring lifecycle review |
| Identifiers with no explicit status | 331 | Missing status stays missing |
| Identifiers with other explicit status | 422 | Exact vocabulary retained in the detail |
| Policy-explicit ECC | 1,168 | Pinned canonical area policy supports classification |
| Explicitly excluded from ECC | 137 | Pinned policy explicitly excludes the area |
| Classification unresolved | 1,009 | Missing or unknown policy area remains unresolved |
| Source-backed experiment link candidates | 748 | Typed lineage exists; semantic coverage is unverified |
| No experiment link discovered | 1,566 | Requires source/lifecycle audit; no orphanhood finding |
| IDs with legacy contract candidates | 109 | Legacy preflight contracts, requiring separate scope/readiness review |
| IDs with task ownership candidates | 53 | Paths associate tasks to protocols; admission was not audited |

The unchanged tools were used for their separate purposes:

| Tool | Sources and joins | Limits |
| --- | --- | --- |
| `tools/pending_idea_coverage.py` | Reads immutable Git blobs at the selected commit; all structured documents under `ledger/proposals` and `ledger/ideas`; hypotheses, multiple experiment document versions, and committed protocol pointers; exact-schema queue candidates | 1,879 proposal documents, 1,230 protocol documents, 692 queue documents, 3,947 task entries; 231 diagnostics. It never selects effective approval, queue authority, or protocol readiness. Root legacy ledger, legacy Markdown, and archived proposal lists are outside its proposal denominator. |
| `tools/idea_experiment_coverage.py` | Current-tree scanner invoked on a temporary materialization of only committed inputs; adds root legacy ledger, recognized legacy Markdown, and top-level archived YAML proposal lists; scans `experiments/*/specification.yaml` and exact source fields | 2,314 IDs; 18 errors; 146 duplicate idea entries; 748 explicit experiment links. Its `ecc: false` and `classification_unresolved` fields do not safely identify non-ECC records. It inventories legacy contracts separately. |

The primary generator SHA256 is
`2acbcbac76d69e2fd79b7ece3bfea24ccbf3cf864745df1b6483d0280e5844ca`;
the broader generator SHA256 is
`132c1e63a888a7143c149e0dcf7abbd1ecf6c0571ea0d6c7142dddfe4b6c2c9e`.
The broader tool natively reports only 55 unresolved classifications. An
additional 954 IDs have discovered area values occurring in neither the ECC
inclusion set nor the explicit exclusion set. This projection therefore preserves all 1,009
as unresolved instead of turning the false boolean into a non-ECC finding.
No policy file or source record was edited. The compact overview's
`unknown_area_tokens_not_marked_unresolved_by_broader_tool` field counts these
954 affected IDs, not 954 distinct area names.

`refresh_inventory.py` packages the two existing tools; it implements no coverage
scanner. It copied 9,225 committed files, 161,346,532 bytes, into the owned
temporary `.committed-inputs` directory, including unchanged tool dependencies
and schema-supersession endpoints. The first tool still read Git objects. The
second tool read that copy with Git ancestor discovery disabled, so its original
`source_commit: null` is preserved inside `broader-lineage.json.gz`; the outer
capsule binds the independently verified commit and materialization hashes.
All copied inputs were hashed again after both traversals and the temporary copy
was removed. `materialized-inputs.json.gz` retains its exact manifest.

The primary report was produced successfully with diagnostics disclosed. The
broader CLI exited 1 because its 18 discovery errors remain unresolved; no PASS
or completeness assertion is substituted for that exit. The primary report's
231 diagnostics include 115 parse errors, 22 documents beyond the unchanged
16 MiB per-document discovery limit, 3 ownership-shape errors, 30 unresolved
record-shape/identity entries, 11 unresolved source references, and 50 unresolved
hypothesis references. These are discovery observations, not mathematical
findings. Detailed affected paths are retained in the original tool outputs.

`summarize_inventory.py` projects those outputs into a union by exact identifier.
It does not semantically merge duplicates. It reads pinned source bytes to
distinguish an actual status field from an absent field, including explicit
legacy Markdown State/Status lines and separately labeled registry fallbacks.
`projection-inputs.json.gz` records those reads. The six disagreements about
experiment-link presence arise under different tool source-field/discovery
rules and remain explicit. The 146 identifiers found in multiple source
locations and 27 identifiers associated with several queue candidates require
identity/history and authority reconciliation; multiplicity alone does not
establish an ownership conflict. No contradictory literal statuses or mixed
explicit inclusion/exclusion areas were found in these discovered rows.

The parent agreed the source pin before traversal. At traversal start and end,
local HEAD was `3faef27d7fa04fdaa5a342d2f2b48d01b3db2369`, differing from the
pin only in an additive models-snapshot release receipt. The shared local
`origin/main` ref was `df9386f79e3cc74d828c839ffc84944df9462caa`, which had
advanced from the earlier observed `a5a9e3b930fbc606715a92186bc48157c4f2ba19`.
This agent performed no fetch. Those live ref observations are disclosed;
neither ref changed the agreed Git-object source. Later admission drafts and
later upstream work are outside this report and require a subsequent refresh.

`baseline-delta.json` compares the unchanged primary tool to the historical
`c9200088566443294d4678f38808d349cb590cea` diagnostic. The proposal denominator
and literal-status counts are unchanged. Eleven additional IDs now have declared
source candidates, seven moved from no source found to lexical mentions only,
and 18 rows changed in total. Declared-source rows increased from 725 to 736;
no-source-discovered rows decreased from 890 to 872; lexical-only rows increased
from 264 to 271. These changes establish discovery bookkeeping only.

Both newly produced source-bound designs are included:
`IDEA-20260905-4dff7b` links to `EXP-ECDLP-abf981`, and
`IDEA-20260905-bf8898` links to `EXP-ECDLP-2cb7f8`. At the pin both specification
records have `status: review_required` and `approved_by: null`. Their queue
ownership candidates are Coordinator design tasks, not verified Executor
admissions. Later additive approval work by the parent is outside this pin.

The practical next worklist preserves the existing ECC policy and recorded
recommended priorities. Its grouping is operational and does not change
scientific rankings or confer task authority:

1. The parent retains its six active candidate reviews. Five have no discovered
   experiment link; `IDEA-20260906-0c1bbd` already has a typed link to
   `EXP-PFDR-59409e`, which the parent was told to reconcile. This inventory did
   not repeat the six semantic reviews.
2. Audit existing experiment scope and authority for the other 202 ECC IDs with
   links, prioritizing current parent-owned designs and recorded justified work.
   Resolve effective versions, approval decisions, archive bindings, claims,
   and dependencies before any Executor dispatch. The global admitted-task
   count remains null because that audit was not performed here.
3. The remaining 452 explicit-proposed ECC IDs without discovered experiment
   links form a source/lifecycle audit partition for potential design work.
   Search and reconcile existing ownership first; missing links alone do not
   authorize duplicate designs. Within the full worklist, the original
   `recommended_priority` is preserved without inventing a research ranking.
4. Reconcile 92 other ECC IDs missing status and 416 with other recorded
   lifecycle states; legacy contracts and archived duplicate sources must stay
   visible. Historical rejection prose does not satisfy a present closure audit.
5. Resolve source-area bindings for 1,009 unclassified IDs, including 492 with
   experiment links, 392 explicitly proposed without links, 124 missing status
   without links, and one with another lifecycle state. The 137 explicitly
   non-ECC IDs remain in the denominator and are considered under existing
   policy when no ECC route offers ranked justified work.

The next operational refresh should follow the parent's committed admission
and source integration checkpoint. Preserve these files and create a new output
directory for that successor; do not overwrite this pinned diagnostic.
`runtime-provenance.json` records directly observed native Codex session metadata:
worker `/root/ultra_pending_inventory_refresh`, `gpt-6-astra`, `ultra`, provider
`openai`, and `model_verified: false`. Its metadata cwd is distinguished from
the explicit workdir used by every source command. No backend probe or scientific
validation was performed. The final `artifact-manifest.json` hashes the complete
delivered bundle, excluding its own self-hash by design.
