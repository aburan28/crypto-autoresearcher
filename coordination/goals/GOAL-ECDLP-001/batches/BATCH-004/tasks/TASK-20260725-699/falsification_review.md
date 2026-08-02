# TASK-20260725-699 falsification review

## Verdict

**PASS**

Reviewed only Coordinator snapshot `TASK-20260725-698` at commit
`9b17754e23a1d8856e2762c517d99aa35588b260` (parent
`c9d160f532d4ddc4e2ea8873cac0fb287f5b303a`). The commit is reachable from
review `HEAD`, changes exactly the receipt plus the four producer artifacts,
and producer SHA-256 digests match the receipt `source_path_sha256` map.
The receipt still shows `pending_post_commit` with null commit metadata; Git
checks bind the review. Working-tree-only producer edits were not treated as
durable evidence.

Inference for this review: requested `review-xhigh`, resolved
`cursor-grok-4.5-high-fast`, `fallback_used: true`, authorization
`AMEND-PATH-001-001`, independent session. Equivalence to `review-xhigh` is
not claimed.

## What was attacked

Attempt to falsify that the BATCH-004 repair seals `fixture_sha256` and
`schedule_sha256` completely enough to discharge DEC-20260722-005 /
RT-20260725-687 without reopening honesty, control, claim-boundary, or
present-tense non-authorization failures.

## Snapshot hash verification

| Path | Receipt / pin digest | Git blob at `9b17754e23a1` |
| --- | --- | --- |
| `toy_validation_protocol.yaml` | `9fb4376cb30ef367300fd7d0f094ddd17dae3ae39f2020c797a64201fcb5d00f` | match |
| `protocol_design_note.md` | `fca316d03a46d40993a99471736f38cc3e1190a12127215ffa1dacc0f39df804` | match |
| `public_fixture.json` | `4c82f5e43efce185a2ecbf2cbcc24b6da7a1bddadd1176007427be350494c4a8` | match |
| `empty_or_pilot_schedule.json` | `be41eb8d016f049d31a3f2ce5bdeda94fb60548b9108311bddca5ede9f9f2279` | match |

Both JSON documents are already JCS-canonical: `sha256(raw file) == sha256(JCS)`.
Neither self-includes its own digest field. Protocol pins echo those digests.
The YAML `sealed_schedule_instance` echo matches the schedule JSON structurally.

## RT-687 major pins — discharged

### Fixture (RT687-O1)

`FIXTURE-ECDLP-TOY-RANKFAIL-001` is no longer a deferred template label. Concrete
public parameters are frozen (short-Weierstrass over \(\mathbb{F}_{19}\),
\(a=0\), \(b=2\), order \(13\), \(G=(4,3)\), factor base \(\{G,2G,3G\}\)) with
`fixture_sha256` bound. Independent checks: points lie on the curve; order of
\(G\) is \(13\); discriminant nonzero mod \(19\). Field size is toy and ≤32-bit.

### Schedule (RT687-O2)

`empty_or_pilot_schedule.json` is a hashable empty/pilot instance
(`attempts: []`) materializing all `required_root_fields`, including
`probability_plan`, `resource_schema`, `initial_matrix`, and `precommit`.
`schedule_sha256` is recorded. Empty-or-pilot correctly means empty attempts,
not absence of a schedule document. The RT-687 null-digest certificate-collapse
mutation no longer applies to the design pins.

### Self-exculpation (RT687-O3)

The design note no longer calls missing fixture/schedule hashes “non-defects.”
It states those were design defects and are closed here. Remaining null verifier
/ snapshot precommit fields are framed as **activation** blockers, which is the
correct scope for residuals that are not the DEC fixture/schedule pins.

## Honesty / controls / authorization — not reopened

- `no_scalarization: true` with additive/non-additive split and ownership rules
  preserved; `R_gain=0` still leaves resource-per-rank undefined.
- All nine planted controls present with prior expected terminal codes.
- Claim boundary remains toy-tier conservation; attack improvement, ECDLP lower
  bound, crypto-scale conclusion, breakthrough, solution, and universal
  impossibility stay excluded.
- Present-tense non-authorization holds and is strengthened: review PASS is not
  auto-execution license; separate Coordinator ledger authorization is required.

## Nonblocking residuals (do not flip PASS)

1. **Verifier hash (RT687-O4 accepted).**
   `independent_verifier_artifact_sha256` is still null, with first no-go
   `PRECOMMIT_VERIFIER_HASH_MISSING`. This blocks activation, not the
   fixture/schedule design pins under review.
2. **`precommit.schedule_sha256` omitted from the JSON instance.**
   Contract lists that field under `precommit.required`; the seal pattern records
   the digest at protocol-pin level and excludes a self-included digest from the
   hashed document. Acceptable for this empty/pilot card; freeze the binding
   rule at later activation sealing.
3. **`point_sha256` preimage convention.**
   Values match `sha256(UTF-8 hex string)` rather than raw SEC1 bytes. Internally
   consistent with `column_schema_sha256`; freeze the preimage rule before any
   executable campaign.

## Overclaim check

No breakthrough, attack improvement, lower-bound, or crypto-scale claim was
found. Schema/methodology PASS is not treated as empirical validation.
Fallback model use is recorded without equivalence claims.

## Narrowest supported statement

At snapshot `9b17754e23a1`, TASK-20260725-697 discharges the DEC-20260722-005 /
RT-20260725-687 pins for a concrete public fixture and a sealable empty-or-pilot
schedule, embeds group-operation vocabulary in the schedule, hard-gates the
still-null verifier artifact hash, and preserves full-cost honesty plus the nine
planted controls. No implementation or experiment is authorized.

## Next concrete action

Coordinator may ledger-archive this PASS. Do not admit implementation until a
separate ledger authorization exists; keep activation failing closed while
verifier artifact hash and snapshot precommit fields remain unset.
