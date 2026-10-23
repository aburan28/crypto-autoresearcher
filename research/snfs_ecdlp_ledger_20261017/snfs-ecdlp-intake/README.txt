Special-structure prime-field ECDLP ledger — staging bundle

State: locally staged and validated; NOT imported into an existing harness.
The workspace contains no harness, intake schema, campaign registry, or reused
rank-campaign certificates. No remote registry was identified or queried.

Contents

source.yaml
  The supplied 23-record ledger, retaining its comments and original prose.
normalized-ledger.json
  All batch/record fields, including optional assumptions, reuse, claim boundaries,
  sources, stopping rules, costs and provisional novelty. Ten colon-bearing
  experiment entries are strings here; YAML otherwise parses them as mappings.
  No hypotheses or statuses were silently corrected.
intake-manifest.json
  Separate local metadata: original IDs and statuses, source/record hashes,
  lineage, status classes, priorities, dependencies, and distinct 128-bit seed
  candidates. This is a staging format, not a discovered harness schema.
audit-findings.json
  Proposed mathematical and measurement corrections. Primary-source links are
  included where checked; elementary deductions are identified separately.
  This is a preflight review, not an exhaustive bibliography or novelty audit.
validation.json
  Structural checks, normalization log and arithmetic preflight calculations.
stage_intake.py
  Reproducible staging/verification helper; requires Python 3 and PyYAML.
  It performs no network calls and executes no scientific experiments.

Validation

  python stage_intake.py --verify

All 23 provisional IDs are distinct within this batch. All listed priorities
resolve. Recorded dependency edges resolve and are acyclic. Original fields and
status qualifiers are retained. Metadata maps statuses to 10 theorem-closed
controls, 9 negative controls and 4 open records. This mapping does not certify
that the claimed theorems or novelty assertions are correct.

Declared estimates sum to 1,463–5,143 CPU-hours. These are supplied planning
estimates, not measured execution costs or an accepted scheduling allocation.

Preflight issues to resolve first

E1: a nonconstant bounded-degree j-map does not have the stated O(chi/p) image
density. A twist with a simple zero at the prescribed good fibre creates bad
reduction. Rank certification must cite a valid Tate theorem for the family and
distinguish arithmetic from geometric rank.

E3: completed-operation timing must include MW-coordinate recovery, independent
relations, lattice index/saturation, subgroup coverage and final matrix solving.
The section encoding must include rational coordinates and specialization to O.

A4: no listed (n,d) pair satisfies d | n, so none instantiates the proposed digit
ring map as written.

D4: at subgroup order about 2^32, the box has expected nonzero kernel-hit counts
far below one at all three ranks. The proposed HNF and independence tests need
a powered sampling design.

Additional notes address B1's identically zero statistic, theorem scope versus
algorithmic upper bounds, specialization rank jumps, and height normalization.

Integration handoff

1. Supply the existing harness path/URL and campaign identity, then read its
   schema, intake, execution and evidence rules.
2. Map normalized fields without dropping data; use an extension/provenance
   field for any information the target schema cannot represent directly.
3. Resolve provisional IDs against the canonical registry. On collision, merge
   lineage into the existing canonical record. Do not rename to evade collision.
   Immutable IDs in this bundle are deliberately null.
4. Check and reserve seed candidates atomically against the campaign registry.
   Candidates are unique locally only; no campaign-wide uniqueness or reservation
   is claimed. Preserve the harness's per-instance/replicate seed rules.
5. Reconcile the separate audit notes and validate prerequisites before scheduling.
   Keep the supplied priority order distinct from dependency ordering.

The user's standing approval is retained. No additional approval is requested.
Scientific experiments have NOT run. There are no benchmark outcomes, recovered
logs, theorem receipts, or promoted results in this bundle. Claimed theorem-closed
items retain receipt-only eligibility even where the audit questions their scope.
The synthetic/known-answer boundary, finite-control claim limits, and B4's
explicit prohibition on sieving are preserved.
