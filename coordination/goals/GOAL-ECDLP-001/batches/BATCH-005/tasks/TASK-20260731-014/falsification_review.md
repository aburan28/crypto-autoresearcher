# TASK-20260731-014 falsification review

## Verdict

**PASS**

Reviewed only Coordinator snapshot `TASK-20260731-013` at commit
`d371bc81057a2a295420282871bd54d13e4074cc` (parent
`9e6bbbbe3639d02ed0387d8e2c46d288e30b34c4`). The commit is reachable from
review `HEAD`, changes exactly the receipt plus the three producer artifacts,
and producer SHA-256 digests match the receipt `source_path_sha256` map.
The receipt still shows `pending_post_commit` with null commit metadata; Git
checks bind the review. Working-tree-only producer edits were not treated as
durable evidence.

Inference for this review: requested `review-xhigh`, resolved
`cursor-grok-4.5-high-fast`, `fallback_used: true`, authorization
`AMEND-PATH-001-001`, independent session. Equivalence to `review-xhigh` is
not claimed.

## What was attacked

Attempt to falsify that the ECDLP activation pin is concrete, hash-honest, and
still present-tense non-authorizing for full experiments — specifically that
`PRECOMMIT_VERIFIER_HASH_MISSING` is discharged without illicitly licensing
implementation, solvers, or relation campaigns (BATCH-004 residual under
DEC-20260725-025 / RT-20260725-699).

## Snapshot hash verification

| Path | Receipt / pin digest | Git blob at `d371bc81057a2a` |
| --- | --- | --- |
| `activation_package.yaml` | `7db58872f62e09f9a585583bd02fddf49606c40fa86bb2aacaf661131def03f4` | match |
| `independent_verifier.py` | `3b7d932b7cfb41dbdbfa5fd91dc802765a8000a440e71603ab75152393e668ef` | match |
| `protocol_design_note.md` | `e20836bc3c2d9ded4cb151fb6e31ebfc554feb964580f4b743d4ea21030aa7be` | match |

Recomputed `sha256(independent_verifier.py)` equals package field
`independent_verifier_artifact_sha256` and verifier `--print-self-sha256`.

## BATCH-004 pin continuity

| Pin | Expected (BATCH-004) | Observed in activation package / on disk |
| --- | --- | --- |
| `fixture_sha256` | `4c82f5e43efce185a2ecbf2cbcc24b6da7a1bddadd1176007427be350494c4a8` | unchanged; file digest matches |
| `schedule_sha256` | `be41eb8d016f049d31a3f2ce5bdeda94fb60548b9108311bddca5ede9f9f2279` | unchanged; file digest matches |
| reopen | — | `not_reopened` |

No defect justifying reopen of fixture/schedule pins was found. The sealed
schedule JSON still embeds `precommit.independent_verifier_artifact_sha256: null`
by immutability; the authoritative activation pin is this package (documented).

## Gate interaction (checklist)

| Gate | After this package | Evidence |
| --- | --- | --- |
| `PRECOMMIT_VERIFIER_HASH_MISSING` | Discharged | Non-null pin; null/empty CLI hard-fail exit 2 |
| `PRECOMMIT_SNAPSHOT_UNVERIFIED` | Still blocking | `verified_before_execution: false`; design snapshot ≠ execution seal |
| `PRECOMMIT_SCHEDULE_UNSEALED` | Still blocking | Package `activation_blocked_until`; verifier leaves gate without seal flags |
| Separate Coordinator ledger authorization | Still required | Package text / `authorization_note`; not experiment license |

Correct pin without seal flags yields `STRUCTURAL_OK`,
`activation_executable: false`, remaining
`[PRECOMMIT_SNAPSHOT_UNVERIFIED, PRECOMMIT_SCHEDULE_UNSEALED]`.

## Non-authorization / claim boundary

- Package `status: activation_pin_review_only`
- Explicit denial of implementation, solver, relation campaign, live attack,
  and auto-execution from review PASS
- `claim_tier: toy`; `field_bit_size_max: 32`
- `not_claimed` includes breakthrough, crypto-scale, attack improvement,
  ECDLP lower bound, solution, and `experiment_authorization`
- No crypto-scale or breakthrough affirmative language found

## Verifier behavior

Digest checks are real for the pin obligation: fixture/schedule JCS + raw
sha256 against BATCH-004 seals; `empty_or_pilot` mode; frozen group-op
vocabulary; RT699-O2 point preimage `sha256(UTF-8 hex string)`. Wrong pin →
`VERIFIER_HASH_MISMATCH`.

## Objections (nonblocking)

1. **RT003-O1** — Snapshot receipt inside the producer commit still has null
   commit/parent and `pending_post_commit` (same pattern as RT-699; Git binds).
2. **RT003-O2** — CLI can report `activation_executable:true` if seal flags are
   asserted, without encoding ledger authorization in `remaining_activation_gates`.
   Package/process gates remain binding; Coordinator admission stays authoritative.

Neither reopens pin honesty or illicit authorization of experiments.

## Narrowest supported statement

At `d371bc81057a2a295420282871bd54d13e4074cc`, TASK-20260731-012 discharges
`PRECOMMIT_VERIFIER_HASH_MISSING` with a concrete hash-bound verifier artifact,
reuses BATCH-004 fixture/schedule digests unchanged, keeps execution seals and
separate ledger authorization blocking, and authorizes no experiment.

## Next concrete action

Coordinator may ledger-archive this PASS via `TASK-20260731-015`. Do not admit
implementation or experiment from this pin alone.
