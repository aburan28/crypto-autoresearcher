Adds five proposed mathematical and defensive-assessment diagnostics under `RQ-EQIC-8cb959` and `GOAL-ENDO-001` for interpreting CM endomorphism and summation-polynomial claims.

| Proposal | Question | Proposed bounded test |
| --- | --- | --- |
| `IDEA-20260905-c0001f` | Which subgroup, field, kernel and action premises justify a scope transfer? | 12 paper cases |
| `IDEA-20260905-6685a0` | Which geometric, rational, subgroup or prescribed-point witness follows from a polynomial zero? | 8 finite-fiber cases |
| `IDEA-20260905-a648c0` | Does specialization change solution support, multiplicity or the exceptional domain? | 6 elementary cases |
| `IDEA-20260905-e8cf55` | Does using orbit representatives change the sampling measure? | 3 finite partitions |
| `IDEA-20260905-d76525` | Which dependencies and transport witnesses justify reusing precomputation? | 8 synthetic record pairs |

All five remain `proposed`, `approved_by: null`, and `novelty_status: unverified`. Each records controls, falsification conditions, assumptions, source limits, proof-search obligations, costs, and its difference from nearby proposals. No experiments were run and no algorithmic improvement is demonstrated. Existing hypothesis, question and goal states remain unchanged.

The exact ten-file proposal snapshot is `0b304e2cf8f196833bffe08ac05f3c687e1469f3`. Supporting intake records preserve the unsuccessful bounded first attempt and the separately authorized completion task. The completed producer bytes are immutable; three EOF-only blank-line warnings are documented and preserved.

Validation after merging main `84fbc464cdf1918f6a45544d04143b527ad1f926`:

- All five canonical bodies exactly match the producer objects; all 15 ledger records added by this PR pass the canonical per-record validator.
- Strict Git archive verification passes for all ten snapshot paths. Branch-scoped merge hygiene passes for the 38 changed files.
- Full ledger validation currently fails on four unrelated records whose bytes are identical to the merged main revision: `DEC-20260905-01a1b4` (invalid YAML), `DEC-20260905-36847f` and `DEC-20260905-e140ee` (wrong top-level record keys), and `TASK-20260905-2c383f` (wrong top-level handoff key). This PR does not modify those records. The earlier pre-refresh full-ledger pass is retained in the immutable intake history; it is not presented as a pass for current main.
- GitHub checks remain pending until their runs finish.

The recommended first separate design is the 12-case typed-scope diagnostic. This PR grants no experiment approval and makes no scientific status transition.
