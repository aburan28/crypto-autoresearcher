# Additive decision metadata completion

Commit `190af45671dd7763cfdae2502bc89b320b0713a5` supplied the missing `knowledge_promotion` fields for two published decisions. This correction retains that metadata through the established schema-supersession registry and restores the historical decision paths to their bytes at parent `b6975c7382`.

Each replacement keeps the original decision ID and all original fields, and adds only the absent metadata. The validator discovers the original path and validates its exact SHA-bound replacement; `replacement_id: null` keeps the historical ID. The first added explanation uses precise finite-grid wording. No scientific status, measured value, evidence strength, hypothesis disposition, or approval is changed. These metadata completions do not independently validate those historical claims.

The author's metadata commit remains in Git history. Original, author-repair and final replacement digests are listed below so both versions are auditable. The original pilot, helper, evidence-qualification and review bytes elsewhere in this PR are unchanged.

| Decision | Original SHA-256 | Author metadata SHA-256 | Additive replacement SHA-256 |
| --- | --- | --- | --- |
| DEC-20261019-b01514 | `335d6ef1b0834a519d70116b7244a44db5caf0d2fda88ef5208fe68c8364c1db` | `cf848bf889d948ffdd057dacf912caa49f13d5557de270bc5eadadcb42853f9b` | `0b6cc82fc3b1e6c9715ec9cc932286ca7aa445980c0acc457ad39617447ed187` |
| DEC-20261019-624f64 | `41419c35f8b9c4960041a707d7cd444c3d9a65948f066427dc6be4f1e2f52a42` | `f21b31456efed127052c60f1af80ba0fd9025d0a119239996bbccbdf37473cd9` | `f21b31456efed127052c60f1af80ba0fd9025d0a119239996bbccbdf37473cd9` |


Validation must verify both registry bindings and validate both original paths through the replacements. The existing schema-routing regressions retain failure on changed hashes and defective replacements. Fresh current-head CI is required before merge.
