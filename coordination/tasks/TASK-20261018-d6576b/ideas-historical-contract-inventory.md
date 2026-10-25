# Historical eighteen-contract investigation

Read-only inventory against `f279a4918cdc41885682b40de1b8e5150035242b`. No launch, source edit, approval change or Git history mutation.

**Result:** one reproducible native-readiness filter gives exactly18 candidate IDs, but the audit did not specify that filter or a revision; the identity is not uniquely established. A nearby native filter gives19, and the broad approved+frozen+no-run predicate gives152.

The18 are the native ready/implementation-gap ECDLP backlog plus the four original worksheets just reproduced. The sole excluded nearby row is `EXP-ECDLP-daee4d`, whose native queue is rejected because queue.goal_id is empty. All18 specifications were read from the pre-session base, are frozen/approved, are unchanged today, and have zero tracked run-content files at that base.

| Candidate | Base title | Current native status/blocker |
|---|---|---|
| EXP-ECDLP-080496 | Rational points and the coordinate cycle on the Hesse cubic over F_97 | needs_implementation_or_plan |
| EXP-ECDLP-20ac31 | Square bias of one four-term x-product on y^2 = x^3 + 6x + 2 | Scoped metadata-compatible successor output_validated; original invalid attempt retained |
| EXP-ECDLP-3c166b | Lower-half x-count gap of two curves over F_29 | Scoped metadata-compatible successor output_validated; original invalid attempt retained |
| EXP-ECDLP-4a3f03 | Orbit factors and the anomalous trace | needs_implementation_or_plan |
| EXP-ECDLP-5a293e | Negation invariance of two x-line maps over F_17 | needs_implementation_or_plan |
| EXP-ECDLP-5f4f14 | Chord-slope fibres under translation by one generator on one F_53 curve | Scoped metadata-compatible successor output_validated; original invalid attempt retained |
| EXP-ECDLP-6491b4 | Three cells of the query-bounded success bound | needs_implementation_or_plan |
| EXP-ECDLP-65f903 | The exponent band contains 1/5, and 64 squared is below 64 cubed | needs_implementation_or_plan |
| EXP-ECDLP-903c48 | Stage-0 instrument: rank-1 net zeros for (1, 5) on y^2 = x^3 + 2 over F_11 | ready |
| EXP-ECDLP-911c16 | Which theta coefficient leaves a positive cross-energy remainder | needs_implementation_or_plan |
| EXP-ECDLP-95f69f | Branching of 2-bit reduction after addition modulo 17 | needs_implementation_or_plan |
| EXP-ECDLP-bfbe6f | Twelve S_3 residues on y^2 = x^3 + x + 2 over F_41 | Scoped metadata-compatible successor output_validated; original invalid attempt retained |
| EXP-ECDLP-c9110e | Degree-2 translation count | needs_implementation_or_plan |
| EXP-ECDLP-c9c5a4 | Cover counts and band products | needs_implementation_or_plan |
| EXP-ECDLP-d68ac9 | Window pair-sum counts | needs_implementation_or_plan |
| EXP-ECDLP-efafc0 | Chord-and-tangent check of one triple over F_17 | needs_implementation_or_plan |
| EXP-ECDLP-f34097 | Stage-0 instrument: planted degree-0 section on y^2 = x^3 + x + 30 over F_31 | ready |
| EXP-ECDLP-f7310e | Trivial-direction cancellation on two points | needs_implementation_or_plan |

Two ordinary-ready packets have exact existing plans and no off-main runs: `f34097` (F31 Stage0,256MiB,120s watchdog) and `903c48` (F11 Stage0,256MiB,60s). Root separately authorized native execution if existing gates pass. This inventory itself launches nothing. Twelve rows still have no admitted native trial plan/launcher; their implementation/plan requirement remains open.

Historical limitations: the checkout is shallow at the base (one local commit). Read-only GitHub API identifies base parents and the latest default-branch checkpoint before 2026-10-13 as `387dd4aeba486c198913fbecc45661b6a26f8cb5` (2026-10-12T22:01:50Z). No historical snapshot was silently treated as the audit’s actual revision.

The341-record index, native selectors (including blocked rows), all tracked experiment paths at the base, original specifications, hold-aware source behavior, and exact-text references were inspected. See companion JSON for exact hashes, IDs, plans, argv, memory/watchdog limits, source evidence and excluded alternative.

Confirming the audit source revision/list would discriminate the18 from the152 broader frozen/unexecuted contracts. Current four accepted calibration scopes are explicitly a subset and do not stand in for18.

Additional native admission finding: both ordinary-ready packets have source/publication and dispatcher gates passing, but their executor/archive handoffs omit all eight native GENERATED provenance/log files. Each needs full eleven-path coverage (eight native plus three declared driver artifacts). No claim/run slot was consumed. Additive coordination coverage repair is required before the native supervisor can launch; see /tmp/ideas-two-ready-readiness.json.
