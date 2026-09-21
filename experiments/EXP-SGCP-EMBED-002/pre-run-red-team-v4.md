## Handoff: SGCP V4 independent red-team review

### Claim or task

Assess exact commit `188b6f12cd50fb18a4304c126c23c27d99c56738` for
readiness to authorize a separate hash-complete canonical launch-plan design.

### Status

`OBSERVATION`; the underlying claim remains `HYPOTHESIS`, `TOY-EVIDENCE`,
`MODEL-BOUND`, and `NOVELTY-UNVERIFIED`.

Recommendation: `REVISE`.

### Assumptions

- Only committed blobs at the exact hash were reviewed.
- Only in-memory unit, abstract, synthetic-envelope, and frozen p=19 controls
  were run.
- A verifier exception is an `INCONCLUSIVE` implementation failure, not
  mathematical falsification or false acceptance.
- The recommendation concerns launch-plan design only; execution remains
  unauthorized.

### Evidence so far

- The focused suite passed 25/25 and all nine V4 development-log hashes matched
  the committed blobs.
- A broader frozen-row sweep made 1,374 wrong-type scalar substitutions; none
  escaped `v4_row_type_errors`.
- Duplicate-plus-mathematical reasons, ordering, source encodings,
  digest-refreshed semantic mutations, exhausted fields, and registered
  canonical-grid mutations passed their committed controls.
- `maximum_runs=0`, `runs: []`, and both disabled CLI modes remain correctly
  enforced. This is a policy boundary, not a capability sandbox.

### Failure modes

1. Blocking: the V4 verifier is not total on exact-type malformed envelopes.
   Four bounded, digest-refreshed mutations raised uncaught exceptions:
   truncated `constrained_budget_caps`, selected formal `[999]`, duplicate
   selected formals, and a negative exact-integer cap with refreshed
   associations.
2. Blocking: legacy routing can crash or emit misleading receipts. A valid V4
   body relabeled as V3 raised `KeyError: 'selected_maxima'`; an empty
   noncanonical V3 document returned `valid=true`; and legacy receipts claimed
   V4 checks that did not execute.
3. Medium: the third exhaustive oracle independently enumerates masks and
   objective ties but reuses verifier graph, model, and support helpers. It is
   not a third end-to-end semantic implementation.
4. Medium: the family-gate differential lacks hand-derived boundary fixtures
   for 17/18 versus 18/24 positives, two versus three passing strata, median
   ties, duplicate nulls, fixed-family/cap enforcement, all-fail, and collapse
   cases.
5. Interpretation: even a complete PASS is a finite comparison against four
   deterministic controls on toy curves, not general coordinate-structure or
   ECDLP evidence.

### Required controls

- Make every bounded verifier entrypoint return deterministic `valid=false`
  receipts for malformed or out-of-range JSON.
- Validate lengths, cap associations and positivity, selected-formal
  uniqueness/eligibility/order, and node budgets before replay or indexing.
- Reject V1-V3 documents explicitly or route each through version-specific
  checks; report only checks actually executed.
- Add regressions for truncated caps, invalid and duplicate formals, negative
  caps, and a V4-body/V3-schema downgrade.
- Add a genuinely separate frozen-B4 semantic oracle that does not call
  producer or verifier graph/model helpers.
- Add hand-derived family-gate threshold and cross-cap-splicing fixtures.

### Next concrete action

Create a no-run V5 verifier-totality and routing repair, keep every budget at
zero, and request fresh exact-hash review.

### Artifact paths

- `experiments/EXP-SGCP-EMBED-002/contract.md`
- `experiments/EXP-SGCP-EMBED-002/specification.json`
- `experiments/EXP-SGCP-EMBED-002/src/sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/src/verify_sgcp_embed_family.py`
- `tests/test_sgcp_embed_family.py`
- `experiments/EXP-SGCP-EMBED-002/development-test-log-v4.md`

Final recommendation: **REVISE. Do not authorize launch-plan design.
Execution remains unauthorized and `maximum_runs=0`.**
