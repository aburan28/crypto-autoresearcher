# TASK-20260725-003 — Adversarial Notes

## Session identity

TASK-20260725-003-independent-review-20260725

## Independence attestation

This reviewer did NOT produce any TASK-20260725-001 artifacts. This is a fresh,
non-originating review session. The reviewer originated none of the protocol
YAML, the design rationale, the snapshot receipt, or the producer authorization
DEC-20260722-005.

## Adversarial reconstruction

The task required me to falsify the frozen toy validation protocol. I attempted
multiple falsification routes. Below are the strongest routes I tried and what
I found.

### Route 1: Mathematical fixture falsification

**Hypothesis to falsify**: the declared fixture (E: y²=x³+x+6 over F₁₁, group
order 13, 4 factor-base points) is mathematically wrong.

**Method**: Independent Python brute-force enumeration of all (x,y) in
{0,...,10}² satisfying y² = x³ + x + 6 mod 11, plus independent affine point
addition/doubling to verify group order and discrete logs.

**Result**: FALSIFICATION FAILED. The fixture is mathematically correct.
- p=11 is prime.
- 4a³+27b² = 976 mod 11 = 8 ≠ 0, so the curve is nonsingular.
- Enumeration found exactly 12 affine points plus the identity = 13 total.
  The 12 affine points are: (2,4), (2,7), (3,5), (3,6), (5,2), (5,9),
  (7,2), (7,9), (8,3), (8,8), (10,2), (10,9). This matches the rationale's
  table.
- 13 is prime (no divisor in {2,3}; sqrt(13) < 4).
- All 4 factor-base points (2,4), (5,9), (8,8), (3,5) satisfy the curve
  equation.
- 13*P = O for all 4 points (verified by repeated affine addition).
- Discrete logs are correct: 2G=(5,9), 3G=(8,8), 5G=(3,5).
- Sample relation: 9G + 5G = 14G = 1G = G = (2,4). Verified.
- All 4 point_sha256 values match (sha256 of 0x04 || byte(x) || byte(y)).

The mathematical fixture is sound. No falsification possible here.

### Route 2: Hash binding falsification

**Hypothesis to falsify**: the binding hashes (fixture_sha256,
field_schema_sha256, schedule_sha256, verifier artifact_sha256,
column_schema_sha256, canonical_rows_sha256) are either wrong or not
independently reproducible.

**Method**: For each hash, I attempted to recompute it from the protocol
document using the stated canonicalization method (JCS via
json.dumps(sort_keys=True, separators=(',',':'), ensure_ascii=False),
matching the rationale's stated Python approach). I tested multiple field-set
interpretations for each hash.

**Result**: PARTIAL FALSIFICATION SUCCEEDED.
- column_schema_sha256: MATCHES when excluding both column_schema_sha256 and
  column_schema_sha256_computation. This confirms the JCS method is sound.
- canonical_rows_sha256: MATCHES (sha256 of row domain separator || column
  schema hash bytes || empty bytes).
- fixture_sha256: DOES NOT MATCH under any of 5 interpretations. The protocol
  says sha256(JCS(fixture_object_without_fixture_sha256_field)) but never
  defines which fields constitute "fixture_object."
- field_schema_sha256: DOES NOT MATCH under any of 3 interpretations. There
  is NO computation method specified at all — the hash is opaque.
- schedule_sha256: DOES NOT MATCH under any of 4 interpretations, including
  the exact 13 root fields specified in the schedule_sha256_computation.
- verifier artifact_sha256: DOES NOT MATCH under 2 interpretations. The scope
  of "verifier_specification_object" is ambiguous.

**Assessment**: 4 of 6 binding hashes cannot be independently reproduced. This
is a significant gap because the contract's canonicalization rule
(sha256(JCS(document_without_its_own_digest_field))) implies that an independent
verifier should be able to recompute every digest. If the verifier cannot
recompute the fixture_sha256, it cannot verify that the schedule references
the correct fixture. The hash-binding discipline is weakened.

**Why this is blocking**: The column_schema_sha256 demonstrates that the JCS
methodology works when the field set is unambiguous. The 4 non-reproducible
hashes are not reproducible because the protocol does not specify their field
sets with the same precision. This is an insufficiency of concreteness, not a
mathematical error. An independent verifier for a future executable campaign
would be unable to verify 4 of the 6 hash bindings.

### Route 3: Schedule seal falsification

**Hypothesis to falsify**: the empty schedule's precommit seal is structurally
invalid or the placeholders are improperly handled.

**Method**: Check that all 6 required precommit fields are present, that
ordinals are contiguous from zero, that the retry forest is acyclic, and that
the 4 snapshot-commit placeholders are explicitly marked as to-be-filled.

**Result**: FALSIFICATION FAILED. The seal structure is valid.
- All 6 required precommit fields are present.
- Zero attempts means ordinals are trivially contiguous and the retry forest
  is trivially acyclic.
- The 4 snapshot-commit reference placeholders are explicitly marked
  "to-be-filled-by-TASK-20260725-002" with a placeholder_explanation field.
- This is acceptable for review-only (no snapshot existed when the producer
  wrote them).

However, the schedule_sha256 itself is not reproducible (see Route 2), which
undermines the seal's verifiability even though its structure is valid.

### Route 4: Claim boundary falsification

**Hypothesis to falsify**: the protocol makes an unauthorized claim (attack
improvement, ECDLP lower bound, cryptographic scale, breakthrough, universal
impossibility).

**Method**: Read every claim, passing_claim, prohibited_claims, exclusions,
and scoped_no_go_triggers field. Check for any statement that exceeds the toy
tier.

**Result**: FALSIFICATION FAILED. The claim boundary is clean.
- maximum_tier is "toy".
- The passing_claim is scoped to toy/public campaign conservation only.
- All 7 prohibited claims are listed.
- All 4 exclusions are listed.
- No statement in the protocol makes or implies an attack improvement, ECDLP
  lower bound, cryptographic-scale conclusion, breakthrough, or universal
  impossibility.
- The scoped_no_go_triggers rule explicitly says "Do not infer universal
  impossibility, ECDLP hardness, or an attack lower bound."

### Route 5: Contract conformance falsification

**Hypothesis to falsify**: the protocol is missing or diluting an obligation
from certificate contract v1.0.0-review.

**Method**: Map every section of the contract to the corresponding section in
the protocol. Check that all conservation, bijection, rank, resource-vector,
probability-gate, and planted-control obligations are carried forward as
concrete instances.

**Result**: FALSIFICATION FAILED on obligation completeness. All 11
scoped_no_go_triggers, all 9 terminal codes, all 9 planted controls, the
schedule_receipt_bijection, independent_rank_verification, resource_schema,
probability_plan, campaign_certificate, terminal_receipt, relation_certificate,
and canonicalization sections are all present and concrete.

However, the hash-binding insufficiency (Route 2) means that while the
obligations are present, the hash bindings that make them verifiable are not
all independently reproducible. This is a concreteness gap, not a missing
obligation.

### Route 6: Runtime receipt falsification

**Hypothesis to falsify**: the protocol's inference_receipt misrepresents the
runtime, claims equivalence, or has inconsistent metadata.

**Method**: Check requested_policy, resolved_model_id, fallback_used,
equivalence_to_requested_policy_claimed, and cross-check consistency between
the protocol YAML and the design rationale.

**Result**: FALSIFICATION FAILED. The runtime receipt is honest.
- requested_policy: "research-sol-max" (correct for a research/idea-generator
  task).
- resolved_model_id: "fireworks-ai/accounts/fireworks/models/glm-5p2" (an
  auditable fallback).
- fallback_used: true.
- equivalence_to_requested_policy_claimed: false.
- Metadata is consistent across the protocol YAML and the rationale.

### Route 7: Group-operation double-counting falsification

**Hypothesis to falsify**: the group-operation type vocabulary allows
double-counting or has an operation type gap.

**Method**: Check that SCALAR_MULT_ORDER_CHECK's internal operations are NOT
additionally counted, that point subtraction decomposes correctly, that general
scalar multiplication decomposes correctly, and that the vocabulary is
exhaustive.

**Result**: FALSIFICATION FAILED. The vocabulary is well-designed.
- SCALAR_MULT_ORDER_CHECK is explicitly a composite unit; its internal
  doublings and additions are NOT additionally counted.
- Point subtraction P - Q = POINT_NEGATE(P) + POINT_ADD.
- General scalar multiplication k*P = sequence of POINT_DOUBLE and POINT_ADD.
- exhaustive: true, no_open_ended_types: true.
- The zero vector is explicitly specified.
- The aggregation rule is additive and coordinatewise.

### Route 8: Verifier independence falsification

**Hypothesis to falsify**: the independent verifier is not actually
independent of the producer solver path.

**Method**: Check the verifier specification's checks_performed list and
independence statement.

**Result**: FALSIFICATION FAILED. The verifier is specified as independent.
- It reparses the public fixture without using producer solver state.
- It recomputes group sums from scratch.
- It derives coefficients independently.
- It performs Gaussian elimination with its own implementation.
- It is declared as specification_only, which is acceptable for review-only.

However, the verifier's artifact_sha256 is not reproducible (Route 2), which
means the specification binding cannot be independently verified.

## Summary of adversarial findings

| Route | Target | Result |
|-------|--------|--------|
| 1 | Mathematical fixture | FALSIFICATION FAILED — fixture is correct |
| 2 | Hash bindings | PARTIAL FALSIFICATION — 4 of 6 hashes not reproducible |
| 3 | Schedule seal structure | FALSIFICATION FAILED — structure valid |
| 4 | Claim boundary | FALSIFICATION FAILED — no unauthorized claims |
| 5 | Contract conformance | FALSIFICATION FAILED — all obligations present |
| 6 | Runtime receipt | FALSIFICATION FAILED — honest metadata |
| 7 | Type vocabulary | FALSIFICATION FAILED — no double-counting |
| 8 | Verifier independence | FALSIFICATION FAILED — independent by spec |

## Verdict rationale

The mathematical content, structure, claim boundary, contract conformance,
runtime receipt, type vocabulary, and verifier independence are all correct.
The single falsification route that succeeded is Route 2: 4 of 6 binding
hashes cannot be independently reproduced because the protocol does not
unambiguously specify their field sets.

This is a REVISE verdict, not FAIL, because:
- The fixture is not "fundamentally broken" — it is mathematically correct.
- The protocol does not violate the contract schema — all obligations are
  present.
- The protocol makes no unauthorized claim.

And not PASS, because:
- 4 binding hashes are "insufficiently concrete" — the
  field_schema_sha256 has no computation method at all, and the other 3 have
  ambiguous or non-matching computations.
- An independent verifier for a future executable campaign cannot verify these
  hash bindings, which is a core requirement of the certificate discipline.

The repairs are specific and bounded: enumerate the exact field sets for each
hash computation, following the pattern of column_schema_sha256_computation
(which IS reproducible). This is a documentation/specification gap, not a
mathematical or structural error.
