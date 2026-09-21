# TASK-20260725-001 — Toy Validation Protocol Design Rationale

## Terminal verdict

`CONTRACT_COMPLETE_REVIEW_REQUIRED`

This protocol is a concrete instance of certificate contract
`crypto.autoresearch.rank_failure_conservation_certificate` version
`1.0.0-review` (TASK-20260722-012). It freezes the four residual gaps
flagged as non-blocking objections by the independent review
TASK-20260722-014 (verdict PASS, lines 217-226):

1. A concrete public toy fixture.
2. A sealed empty pre-execution schedule template.
3. An independent verifier identity, version, and artifact_sha256.
4. A frozen explicit finite group-operation type vocabulary.

No implementation or experiment was authorized or performed. The maximum
claim tier is toy. This is not an attack improvement, ECDLP lower bound,
cryptographic-scale conclusion, breakthrough, or universal impossibility
result. The P1553 R4 target-label common-factor operation is excluded.

## Runtime and authorization gate

- requested policy: `research-sol-max`
- resolved model: `fireworks-ai/accounts/fireworks/models/glm-5p2`
- reasoning effort: `high`
- available reasoning effort: `high`
- fallback used: `true`
- authorization: `DEC-20260722-005`
- adapter runtime: `opencode`
- equivalence to the unavailable requested policy: not claimed

The exact Sol-family policy `research-sol-max` could not be resolved in
this runtime. An auditable fallback was used. The inference receipt in the
protocol YAML records all metadata. No equivalence is claimed.

## Relied-upon repository input binding

Observed repository HEAD: `38a079c4887ac45e648a7574b20951311e995898`.

```
f21afaab25ac6f2c74a7a36cb67b76bde313be14ac78077e72abc76031dc493b  AGENTS.md
a3d710e1be2ee9b7c5404c41212a525d09cd6ca97182941a37102c6b7eeae7d7  agents/idea-generator.md
1ca204a0e16e88012892a0867aab5ea82d388fdfa1b0474938a0e2c8cffd8d9f  coordination/goals/GOAL-ECDLP-001/batches/BATCH-002/tasks/TASK-20260722-012/certificate_contract.yaml
bae09f93273152a4563177b9f19a696d78f1e7f5e43f71413e802b79b5dfe476  coordination/goals/GOAL-ECDLP-001/batches/BATCH-002/tasks/TASK-20260722-012/derivation_and_no_go.md
b9054734bc99bd73c64ad4703e14bfb0f7ccfeb66a990b6737fe43b89a4f14a0  coordination/goals/GOAL-ECDLP-001/batches/BATCH-002/reviews/TASK-20260722-014/review_report.yaml
764bc684d7b43711bcce4d03233a0f00c05bf4361fb49516f7b49e40d4b41f6e  ledger/evidence/EV-ECDLP-004.yaml
1a9d63c09d7d60aa116b70c5bbccd04f67699948d7b3596ddb4b548ba4ad5342  ledger/decisions/DEC-20260722-005.yaml
37fd8d21d97fdcb429c19b7d29c72dfca7d893f608a9f66f5cc0eb53d5c20d29  docs/claims-and-verification.md
a390605329527d92a3bc97d2cd9e73cd63a626fdb6d7a588df3d6c9e28a578dc  templates/research-records.md
4ccf43564d2a7fe34d04372aa1c745515c0a698b8529c9623f0b11f3396302b7  ledger/handoffs/TASK-20260725-001.yaml
```

## 1. Toy fixture selection and verification

### Curve choice

The fixture uses the elliptic curve E: y^2 = x^3 + x + 6 over F_11
(short Weierstrass, a=1, b=6, p=11). This is a genuinely small prime-field
curve with modulus p = 11 (between 2^3 and 2^4).

### Group order

Enumerating all (x, y) in {0,...,10}^2 satisfying y^2 = x^3 + x + 6
(mod 11) plus the identity gives exactly 13 points:

| x | y values | #points |
|---|----------|---------|
| 2 | 4, 7     | 2       |
| 3 | 5, 6     | 2       |
| 5 | 2, 9     | 2       |
| 7 | 2, 9     | 2       |
| 8 | 3, 8     | 2       |
| 10| 2, 9     | 2       |

Plus the identity O: total = 12 + 1 = 13. Since 13 is prime, #E(F_11) = 13
is prime, making the full group a cyclic group of prime order. Every
non-identity point is a generator.

### Primality method

13 is prime by trial division: 13 mod 2 = 1, 13 mod 3 = 1, and sqrt(13)
< 4, so testing divisibility by {2, 3} is exhaustive. No larger prime
divisor need be checked.

### Subgroup-order binding

The contract requires `modulus_decimal` (the rank-computation field
modulus) to equal the fixture's `subgroup_order` and every named point to
satisfy ell * P = O. Here ell = 13, and the group order is 13, so every
point on the curve satisfies 13 * P = O by Lagrange's theorem. This was
verified computationally for all four factor-base points:
- 13 * (2, 4) = O
- 13 * (5, 9) = O
- 13 * (8, 8) = O
- 13 * (3, 5) = O

### Factor-base points

Four factor-base points are chosen as the ordered columns:

| Column | Label | Point (x, y) | k = dlog_wrt_G | Encoding hex |
|--------|-------|--------------|-----------------|--------------|
| col-1  | G     | (2, 4)       | 1               | 040204       |
| col-2  | 2G    | (5, 9)       | 2               | 040509       |
| col-3  | 3G    | (8, 8)       | 3               | 040808       |
| col-4  | 5G    | (3, 5)       | 5               | 040305       |

The discrete logs {1, 2, 3, 5} are chosen to be distinct and non-trivial
(generators of small multiplicative structure but not a simple arithmetic
progression).

### Canonical point encoding

Each finite point is encoded as:
`0x04 || byte(x) || byte(y)`

where byte(v) is a single unsigned 8-bit big-endian byte. Since p = 11 <
256, each coordinate fits in one byte. The identity O is encoded as the
single byte `0x00`.

Point SHA-256 hashes are computed over the raw encoding bytes:
- col-1: sha256(0x04 0x02 0x04) = 14c0e459b7a8ff79f3d4867c8455d6bc0f963a20d7ff4940ba8ebac31cc7af14
- col-2: sha256(0x04 0x05 0x09) = 6188b0fcb2b58cf35fca4c5e9292e903bfb19babc58b4e1bb416ae453e35c95a
- col-3: sha256(0x04 0x08 0x08) = f9c2ecc090c3efefaae83e5a0b7d1dfd76498b803cbcb0d890fac25b1917bee6
- col-4: sha256(0x04 0x03 0x05) = 40d8597ea9a489ae7d1e43e93de718c7c5ccdf3299fd58493b2f6f777d51550d

### Fixture SHA-256 computation

The fixture_sha256 is computed as:
`sha256(JCS(fixture_object_without_fixture_sha256_field))`

where JCS is RFC 8785 JSON Canonicalization Scheme: keys sorted by UTF-16
code unit order, no whitespace, all integer values serialized as base-10
strings (per the contract's integer_rule). The computation was performed
in Python using `json.dumps(obj, sort_keys=True, separators=(',', ':'),
ensure_ascii=False)` which produces JCS-compliant output for objects with
only ASCII keys and string values.

Result: `fixture_sha256 = 1b5478a65d39461b6730089dae403c0d57b98c03f39b522a76cf55b28fd0b4cb`

### Sample relation verification

To demonstrate the relation-to-row binding is well-defined, consider:
- target_column_id = "col-1" (P_target = G = 1G)
- summand_column_ids = ["col-3", "col-3", "col-3", "col-4"]

Group check: 3 * P_col-3 + P_col-4 = 3 * (3G) + 5G = 9G + 5G = 14G = G
(since 14 mod 13 = 1) = P_col-1. Verified.

Derived coefficients (mod 13):
- a_col-1 = 0 (count in summands) - 1 (target) = -1 = 12 mod 13
- a_col-2 = 0
- a_col-3 = 3
- a_col-4 = 1

Canonical row bytes: [12, 0, 3, 1] (4 bytes, 1 per coefficient).

Linear dependence check: 12*1 + 0*2 + 3*3 + 1*5 = 12 + 0 + 9 + 5 = 26 =
2*13 = 0 mod 13. The row lies in the kernel of the discrete-log map,
confirming it represents a valid group relation.

## 2. Empty sealed schedule template

### Choice: empty (zero attempts)

An empty sealed template is the safest review-only choice. It:
- trivially satisfies the schedule/receipt bijection (empty set = empty
  set, 0 = 0, no multiplicity violations);
- has a trivially acyclic retry forest (zero nodes);
- has no activation predicates to recompute;
- trivially satisfies the probability gate (r=0 implies n_star=0 per the
  contract edge case);
- pins the fixture, field, column schema, row format, terminal vocabulary,
  resource schema, and group-operation type vocabulary without authorizing
  any execution.

### Precommit seal structure

The precommit seal is present with all required fields:
- `schedule_sha256`: computed as sha256(JCS(schedule_object_without_schedule_sha256)).
  Result: `6566e8bab496e9c8cc60a4754c3e95e9056d8dcac5ff155e4409064c2e1ab270`
- `schedule_path`: the protocol YAML file path
- `coordinator_snapshot_receipt_path`: placeholder (to-be-filled-by-TASK-20260725-002)
- `snapshot_commit_sha`: placeholder (to-be-filled-by-TASK-20260725-002)
- `snapshot_parent_sha`: placeholder (to-be-filled-by-TASK-20260725-002)
- `verified_before_execution`: placeholder (to-be-filled-by-TASK-20260725-002)

The snapshot commit references are placeholders because no snapshot commit
exists at review-only time. The task assignment explicitly allows this:
"snapshot commit refs may be placeholders marked to-be-filled-by-
TASK-20260725-002 since no snapshot exists yet." The seal structure is
present and structurally valid; the placeholders will be replaced with
actual Git commit references when the Coordinator creates the snapshot
archival commit (TASK-20260725-002).

### Schedule root fields

All 13 required root fields from the contract are present:
contract_schema, contract_version, campaign_id, public_fixture, field,
column_schema, canonical_row_format, terminal_vocabulary, resource_schema,
probability_plan, attempts (empty), initial_matrix, precommit.

### Initial matrix

The initial matrix is empty:
- row_count: 0
- rank: 0
- canonical_rows_sha256: sha256("rank-row-v1\0" || column_schema_sha256_bytes || b"")
  = 6a34d0c8f94d22958b0317877dce11d2b96f461fa9ad2835b51f3475662790f3
- field_schema_sha256: e3788b29abdddc770b33cede330ad60361c94d5394e3e8acb800d2645e176af7
- column_schema_sha256: 7b348668293595206ffdc2f4593e44fcac78e5a850b4254a28c57029f0652175

The canonical_rows_sha256 for zero rows uses the row domain separator and
column schema hash as binding prefixes, following the contract's row_hash
formula pattern, with an empty canonical-row-bytes suffix.

## 3. Independent verifier specification

### Identity and version

- verifier_id: `independent-gaussian-rank-verifier-toy-v1`
- verifier_version: `0.1.0-spec`
- implementation_status: `specification_only_not_yet_implemented_review_only`

This is a hash-bound verifier **specification artifact**, not an
implemented verifier. The specification is self-contained and defines
exactly what the verifier will do when implemented. Its artifact_sha256
binds the specification content.

### Independence

The verifier is independent of the producer solver path. It:
- reparses the public fixture without using producer solver state;
- recomputes group sums from scratch using affine curve arithmetic;
- derives coefficients independently from target and summand column IDs;
- computes canonical row bytes in frozen column order;
- performs exact Gaussian elimination over F_13 using its own
  implementation, not the producer's rank path.

### Artifact SHA-256

The verifier specification is a JCS-canonicalized JSON object. Its SHA-256
is:
`d0ccd87df0f9718dc0edb7d28115b41a0833a63e2a968b8af19824acd66a54e8`

This hash binds the verifier's declared algorithm, all 13 checks, the rank
computation method, field arithmetic, insertion order, rank increment
domain, row dispositions, and resource counting convention.

### Rank computation

The verifier performs exact Gaussian elimination with partial pivoting
over F_13. All arithmetic is modulo 13, with modular inverses computed via
Fermat's little theorem (a^{-1} = a^{11} mod 13 for a in {1,...,12}).
Rows are processed in ascending schedule ordinal order. Each row's rank
increment is in {0, 1}.

## 4. Group-operation type vocabulary

### Frozen vocabulary: `rank-failure-group-ops-v1`

Six operation types are defined:

| Type | Description | Counts as |
|------|-------------|-----------|
| POINT_ADD | Affine addition P+Q, P and Q finite, distinct, P != +-Q | 1 per invocation |
| POINT_DOUBLE | Affine doubling 2*P, P finite, not identity | 1 per invocation |
| POINT_NEGATE | Affine negation -P = (x, p-y mod p) | 1 per invocation |
| POINT_IDENTITY_TEST | Test whether a point is O | 1 per test |
| POINT_MEMBERSHIP_TEST | Check y^2 = x^3+ax+b mod p | 1 per check |
| SCALAR_MULT_ORDER_CHECK | Full ell*P order verification | 1 per check (composite, no sub-counting) |

### Counting conventions

- Each type counts as exactly one unit per invocation.
- SCALAR_MULT_ORDER_CHECK is a composite operation (internally uses doublings
  and additions). Its internal operations are NOT additionally counted under
  POINT_DOUBLE or POINT_ADD to prevent double-counting. It is reported as a
  single indivisible unit.
- Point subtraction P - Q decomposes into POINT_NEGATE + POINT_ADD, each
  counted under its respective type.
- General scalar multiplication k*P (not the order check) decomposes into a
  sequence of POINT_DOUBLE and POINT_ADD operations, each counted
  individually.
- The vocabulary is exhaustive: no operation type outside these six may be
  charged to the group_operations_by_declared_type resource coordinate.
- The zero vector for an attempt with no group operations is
  {POINT_ADD: 0, POINT_DOUBLE: 0, POINT_NEGATE: 0, POINT_IDENTITY_TEST: 0,
  POINT_MEMBERSHIP_TEST: 0, SCALAR_MULT_ORDER_CHECK: 0}.

### Aggregation

group_operations_by_declared_type is a map from type name to nonnegative
integer count. It is an additive coordinate: the campaign total is the
coordinatewise sum of per-attempt vectors plus the verification-stage
vector. No scalarization is permitted.

## 5. Obligation satisfaction audit

Every scoped no-go trigger from the contract is satisfied:

1. **runtime_metadata_matches_authorization**: inference_receipt records
   requested_policy `research-sol-max`, resolved model
   `fireworks-ai/accounts/fireworks/models/glm-5p2`, fallback_used true,
   authorization_ref `DEC-20260722-005`. SATISFIED.

2. **preexecution_schedule_can_be_sealed**: empty schedule with precommit
   seal structure present; schedule_sha256 computed. SATISFIED.

3. **schedule_and_retry_graph_are_finite_and_acyclic**: zero nodes; empty
   forest is trivially finite and acyclic. SATISFIED.

4. **terminal_vocabulary_is_exhaustive**: 9 codes carried forward from
   contract v1.0.0-review; exhaustive=true. SATISFIED.

5. **field_column_and_row_schema_are_exact**: F_13 prime field, 4 ordered
   columns, 1-byte coefficients, all schema hashes computed. SATISFIED.

6. **schedule_receipt_bijection_is_reconstructible**: empty set = empty
   set, 0 = 0; trivially reconstructible. SATISFIED.

7. **relation_and_row_are_independently_verifiable**: verifier spec pinned
   with artifact_sha256; independence statement recorded. SATISFIED.

8. **incremental_rank_is_exactly_reconstructible**: exact Gaussian
   elimination over F_13 specified; initial rank 0 with 0 rows. SATISFIED.

9. **resource_ownership_is_complete_without_scalarization**: resource
   vector schema with 6-type group-operation vocabulary; no scalarization.
   SATISFIED.

10. **probability_assumptions_and_tail_gate_are_declared**: r=0, n=0,
    alpha_campaign=0, no strata; trivially satisfied gate. SATISFIED.

11. **all_planted_controls_are_decisive**: 9 controls carried forward from
    contract with expected verdicts. SATISFIED.

No obligation failed. The protocol is CONTRACT_COMPLETE_REVIEW_REQUIRED.

## 6. Fields not frozen and why

The only fields not frozen with concrete values are the four precommit
snapshot-commit references:
- `coordinator_snapshot_receipt_path`
- `snapshot_commit_sha`
- `snapshot_parent_sha`
- `verified_before_execution`

These are marked `to-be-filled-by-TASK-20260725-002` because no snapshot
commit exists at review-only time. The task assignment explicitly permits
this: "snapshot commit refs may be placeholders marked to-be-filled-by-
TASK-20260725-002 since no snapshot exists yet." The seal structure is
present and structurally valid. These placeholders do not constitute a
failed obligation — they are deferred to the Coordinator's archival task,
which creates the Git commit and fills in the references.

All other fixture, schedule, verifier, type-vocabulary, field, row, rank,
resource, probability, and control fields are frozen with concrete values.

## 7. Claim boundary

This protocol makes no claim beyond:

> A later independent verifier may conclude only that one sealed toy/public
> campaign conserves its precommitted attempt identities, declared terminal
> receipts, independently verified relation rows, exact incremental rank,
> and declared resource counters under this frozen schema and its
> explicitly accepted probability assumptions.

The toy curve E: y^2 = x^3 + x + 6 over F_11 with subgroup order 13 is
genuinely small (modulus ~2^3.5). Toy-curve evidence must never be
presented as crypto-scale validation. No ECDLP attack improvement, lower
bound, cryptographic-scale conclusion, breakthrough, or universal
impossibility is claimed or implied.

## Exactly one recommended next action

Archive these two TASK-20260725-001 artifacts through TASK-20260725-002
and submit only that immutable snapshot to independent review; authorize
no implementation or experiment until the protocol passes independent
review and the Coordinator approves a separately scoped executable
campaign.
