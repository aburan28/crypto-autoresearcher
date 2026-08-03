# TASK-20260725-687 falsification review

## Verdict

**REVISE**

Reviewed only Coordinator snapshot `TASK-20260725-686` at commit
`87a4debcaced44daa3b840fcb05cb453d8f472f2` (parent
`feba448bf1292a63809aa9921fc0a538345a54e8`). The commit is reachable from
review `HEAD`, changes exactly the receipt plus the two producer artifacts, and
the producer SHA-256 digests match the receipt. The receipt still shows
`pending_post_commit` with null commit metadata; Git checks plus the
dispatcher’s archive-verification assertion bound the review. Working-tree-only
producer edits were not treated as durable evidence.

Inference for this review: requested `review-xhigh`, resolved
`cursor-grok-4.5-high-fast`, `fallback_used: true`, authorization
`AMEND-PATH-001-001`. Equivalence to `review-xhigh` is not claimed.

## What survives

- **No illicit scalarization.** `no_scalarization: true`, additive vs
  non-additive split, ownership invalidation on double-count/unowned work, and
  the rule that `R_gain=0` leaves resource-per-rank undefined are faithful to
  contract `1.0.0-review`.
- **Planted controls.** All nine contract controls are present with matching
  expected terminal codes.
- **Claim boundary.** Maximum claim stays toy-tier conservation; attack
  improvement, ECDLP lower bound, crypto-scale conclusion, breakthrough,
  solution, and universal impossibility are excluded. Superseding
  `TASK-20260725-611` is correctly non-mathematical.
- **Present-tense non-authorization.** The artifacts do not authorize an
  implementation or experiment now.
- **Group-op vocabulary (partial).** An explicit frozen type enum is named;
  see caveat below.
- **AMEND-PATH-001-001 recording.** Producer inference block records requested
  policy, resolved model, fallback, and authorization ref.

## Falsification of completeness vs DEC / 014 pins

DEC-20260722-005 and the TASK-20260722-014 residual required a review-only
protocol that **pins**:

1. a public fixture,
2. a sealed empty-or-pilot schedule template,
3. an independent verifier artifact hash,
4. the group-operation type vocabulary.

### 1–2. Fixture and schedule — incomplete (major)

The protocol names `FIXTURE-ECDLP-TOY-RANKFAIL-001` but sets
`template_pinned_bytes_deferred_to_execution_batch` with no parameters, points,
or `fixture_sha256`. Residual 014 said the protocol-design task must freeze a
concrete public fixture; deferring bytes to an “execution batch” fails that pin.

Likewise, `sealed_schedule_template` is a field checklist with
`schedule_sha256: null`. Empty-or-pilot allows empty attempt contents; it does
not allow omitting a hashable schedule document. Without a JCS-canonical
schedule instance, there is nothing to seal, echo, or bijection-check.

**Cheapest discriminating mutation:** treat the card as PASS-complete, then try
to build a campaign certificate from null fixture/schedule digests. The contract
fails at the first preexecution obligation—no sealed bytes, no independent
parameter checks, no schedule/receipt domain. That is design incompleteness, not
an ECDLP negative.

### 3. Verifier hash — obligation-only (nonblocking if hard-gated)

`independent_verifier_artifact_sha256` is null. Residual 014 deferred the
concrete hash until before an executable campaign, and the protocol blocks runs
until filled. That is acceptable as a blocking residual **only if** seal /
activation cannot proceed with a null hash. DEC’s wording still lists the hash
among protocol pins; revise by pinning a frozen verifier artifact hash or by
making `PRECOMMIT_VERIFIER_HASH_MISSING` an explicit first no-go.

### 4. Group-op vocabulary — adequate with caveat

The enum is listed under protocol pins. Residual 014 required it inside the
schedule object used for aggregation. Embed the same enum under the sealed
schedule’s `resource_schema` / `group_operations_by_declared_type`.

## Weak non-authorization / self-exculpation

The design note calls missing fixture, verifier, and schedule hashes “open
obligations (not defects)” and “post-PASS execution-prep.” For the fixture and
sealed schedule pins, that is false relative to DEC-20260722-005 and residual
014: those gaps **are** design defects and must block protocol PASS.

Also strengthen authorization language so that even after review PASS, no
implementation is admitted without a separate Coordinator ledger authorization
(review PASS alone must not be read as auto-execution license).

## Overclaim check

No breakthrough, attack improvement, lower-bound, or crypto-scale claim was
found. Schema PASS on EV-ECDLP-004 is correctly not treated as empirical
validation. Fallback model use is recorded without equivalence claims.

## Narrowest supported statement

At snapshot `87a4deb`, TASK-20260725-685 is a non-executing methodology sketch
that preserves full-cost honesty and the nine planted controls, but does not
yet complete the DEC/014 pins for a concrete public fixture and a sealed
empty-or-pilot schedule instance. No implementation or experiment is authorized.

## Next concrete action

REVISE: freeze one public ≤32-bit toy fixture with `fixture_sha256`; emit one
JCS-canonical empty-or-pilot schedule with `schedule_sha256` and embedded
group-op vocabulary; pin or hard-gate `independent_verifier_artifact_sha256`;
rewrite open-obligation language so missing pins block protocol PASS; authorize
no implementation until the revised package independently reviews PASS and the
Coordinator issues a separate ledger authorization.
