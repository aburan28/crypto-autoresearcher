# TASK-20260725-707 falsification review

## Verdict

**PASS**

Reviewed only Coordinator snapshot `TASK-20260725-706` at commit
`ac09260135c23f1838e54d9fd42eb23460bc6046` (parent
`518fa95595823e01b696b38e1d47b6b7bccf4191`). The commit is reachable from
review `HEAD`, changes exactly the receipt plus the two producer artifacts, and
producer SHA-256 digests match the receipt:

| Artifact | SHA-256 |
| --- | --- |
| `monodromy_protocol.yaml` | `19f81d50dacf5049f03188e7e02c20711b361c8b8bb60b89e9437533fb9f0eb9` |
| `protocol_design_note.md` | `41b9f6d7f6f254210e9de6b87924295f51b97c7c3efed3e2af81dd15941a42a2` |

Receipt still shows `pending_post_commit` with null commit metadata; Git
reachability plus exact path/hash binding is the durable evidence used.
Working-tree-only producer edits were not treated as durable evidence.

Inference for this review: requested `review-xhigh`, resolved
`cursor-grok-4.5-high-fast`, `fallback_used: true`, authorization
`AMEND-PATH-001-001`, independent session. Equivalence to `review-xhigh` is
not claimed.

Prior REVISE context: `RT-20260725-653` / `DEC-20260725-016` / `EV-MONO-001` /
`KN-OPEN-009`.

## Disposition of OBJ-653-1 / 2 (/ 3)

| Objection / control | Status | Notes |
| --- | --- | --- |
| OBJ-653-1 / CTRL-CM-GATE-FULL | **Discharged** | FULL and exceptional-rate ICEX closure hard-require ≥8 scored CM curves under override with no CM exceptions; unavailable CM → `SCOPED_PROTOCOL_NO_GO` or `RANDOM_PANEL_CALIBRATION_TOY` (`not_closed_for_unscored_cm_families`). |
| OBJ-653-2 / CTRL-CM-ADMISSION | **Discharged** | CM panel `require_prime_order_group: false`, `allow_composite_order: true`; random controls stay prime-order; override flags logged; mis-applying prime-order to CM while allowing FULL is protocol-invalid. |
| OBJ-653-3 / CTRL-CLAIM-WORDING | **Discharged** | “Forces” / `theorem-backed-at-toy-scope` removed; envelope is protocol pin; ICEX label `chebotarev_prediction_plus_toy_census_envelope`. |

## Falsification axes (repair)

### 1. CM gate for FULL — not falsified

Re-attempted the RT-653 cheapest mutation: pass random-panel barrier checks on
≥3 primes, leave `cm_screen_unavailable_at_prime` everywhere, mint
`FULL_MONODROMY_BARRIER_TOY` with ICEX
`closed_at_toy_scope_for_exceptional_rate_sieves`.

Blocked by `barrier_aggregate_rule` clause (v), `CTRL-CM-GATE-FULL`,
`qualified_non_closure_when_cm_unavailable`, claim-boundary forbids, and ICEX
FULL preconditions. KN-OPEN-009’s primary exceptional candidate cannot be
skipped while closing exceptional-rate content.

### 2. CM panel prime-order conflict — not falsified

The shared default `require_prime_order_group: true` no longer empties the CM
panel under a written rule that still allows FULL: the CM panel carries an
explicit admission override, and even post-override incompleteness never
unlocks unqualified FULL.

### 3. Envelope wording — not falsified

Theorem-backed language is reserved for Chebotarev(S₂) split/inert = 1/2.
The multiplier/floor `3·(2/√p)` is labeled a protocol pin / toy calibration.

### 4. Present-tense non-authorization — not falsified (not reopened)

`status: review_only_freeze`, authorization text, design-note section, and
`executor_gate_when_authorized` still forbid census execution now. Review PASS
only unlocks later scheduling under a fresh write_scope plus separate
Coordinator ledger authorization. PASS is not a barrier theorem or
exceptional-locus discovery. No measurement commands are authorized by this
freeze.

### 5. Automorphism quarantine — not falsified (not reopened)

`j ∈ {0,1728}` remain excluded from random controls, quarantined, audited by
`CTRL-J-EXCLUSION`, and forbidden as sole exceptional-locus evidence.

## What this PASS does *not* authorize

- No Frobenius / cycle-type census in BATCH-002.
- No monodromy mathematical result, barrier theorem, or exceptional locus.
- No crypto-scale conclusions; no H-/GOAL status change.
- No Pollard-rho / BSGS / index-calculus path.

## Residual non-blocking

1. **RES-707-1** — Prefer non-`j=0/1728` CM labels for the ≥8 CM-gate score;
   keep automorphism curves in the artifact panel only.
2. **RES-707-2** — Do not re-interpret top-level `cofactor: 1` as emptying the
   CM panel against the explicit composite-order override.
3. **RES-707-3..5** — Inherited loose Weil at `p=211`, window smoke-check
   vacuity, and executor pin of monic `S_3` helper hash.
4. **RES-707-6** — Receipt metadata still `pending_post_commit`; Git binding
   `ac09260135c2` used.

## Baseline comparison

No Pollard-rho, BSGS, or index-calculus path was run or authorized. Closest
baselines remain Chebotarev(S₂) split rate 1/2, the quasirandom window proxy
for ICEX planning, and Pollard-rho as the ECDLP cost the exceptional reading
correctly refuses to claim to beat. This PASS mints no ECDLP advantage and no
barrier theorem.

## Narrowest supported statement

At `ac09260135c2`, the TASK-20260725-705 repair freeze discharges OBJ-653-1/2
(and OBJ-653-3): FULL / exceptional-rate ICEX closure is CM-hard-gated under an
explicit composite-order CM admission override, while present-tense
non-authorization and `j=0/1728` quarantine survive. Coordinator may schedule
measurement only under a later admitted executor task.

## Next concrete action

Hand off to Coordinator ledger archive task `TASK-20260725-708`. Do not
schedule census execution from this PASS alone.
