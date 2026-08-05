# Independent protocol design review — TASK-20260804-9514c9

## Scope and provenance

This is an independent-session, design-only review of `EXP-SMTH-92d322` at
its stated toy ceiling. It is not evidence; it does not approve or freeze a
contract, authorize execution, create an executor task, run, or data, update
the ledger, or make an ECDLP or mathematical claim.

Requested policy: `review-adversarial`. Reasoning effort: `xhigh`.
The exact resolved model identifier is not recorded in the task material and
is therefore not asserted here.

## Snapshot integrity

The reviewed snapshot is
`b9788929bfd9b21a0bbbeee82416f4084ba6be16`; its observed parent is exactly
`4e8e1afc3c9c43f5d3445a2b6a2982453d9dd5af`.

The three source hashes in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-c259e0/archives/TASK-20260804-05f9a8/snapshot_commit_receipt.json`
match their paths in the snapshot:

| Path | SHA-256 | Result |
|---|---|---|
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-c259e0/dispatch_queue.json` | `d63922b43536d6fedf5b4a0a5fd9bf7ef793c3a407506d91c1f1fe2005fbd9b3` | match |
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-c259e0/task-cards/TASK-20260804-1bdcf5.md` | `9ebc03ba56f1eaf037e6f9240f14309b0b822fffbac91c6e42f7f0e9ea50a5b3` | match |
| `coordination/goals/GOAL-ECDLP-001/batches/BATCH-c259e0/tasks/TASK-20260804-1bdcf5/snapshot_input_audit.md` | `8ed84b338fe939724ae473ff2fe9fc018ea33f66d3d955b83285de427f2402c2` | match |

The receipt's `commit_sha` is `null`, as its self-binding note explains; the
commit and parent above were independently checked. The committed draft is
`experiments/EXP-SMTH-92d322/specification.yaml`, SHA-256
`bdb6e96f9b7b8f1548912dfc163bf9b76a16c1c707a068d15019d02293c4d634`,
whose recorded source commit is `cbb93954f6c049e9a1906267c9a242b8da0a8232`.

## Gap dispositions

1. Curve and factor-base deterministic construction — `amendment_required`.
   The draft only says the curve and 512-coordinate base are deterministic
   (`specification.yaml` lines 66–78 and 159–167). Its own approval requirement
   says the selection algorithms are currently unspecified (lines 228–237);
   the committed audit agrees (`snapshot_input_audit.md` lines 25–31).
   A successor must specify one total seed/domain/bits-to-prime, curve, and
   ordered-base algorithm, including eligibility, rejection/retry, point/x
   enumeration, duplicate treatment, ordering, and terminal failure.

2. Exact `INT-1`/`ENC-B`/root-multiset and exceptions —
   `amendment_required`. The draft identifies an invariant and output range
   (`specification.yaml` lines 46–64), but not the arithmetic formula,
   root-multiset procedure, multiplicity/non-split/repeated-root treatment, or
   exceptions. Lines 228–237 and the audit at lines 27–29 explicitly preserve
   this absence. A successor must state the exact S3/invariant calculation,
   representative convention, INT-1 and ENC-B formulas, and deterministic
   handling of every listed exceptional or arithmetic/encoding failure.

3. Complete-factorization solver/configuration/output verification —
   `amendment_required`. “Complete” and a product-equality control occur at
   `specification.yaml` lines 61–64 and 101–113, but no solver/version/config,
   timeout/resume policy, raw record schema, factor encoding, or independently
   checkable verification format is committed. See also lines 221–237 and the
   audit at lines 29–30. A successor must commit those solver rules and a
   treatment/null record format containing each input, complete status,
   factors, verification, and defined incomplete/failure disposition.

4. Numerical RSS probe tolerance/margins and failure rule —
   `amendment_required`. The draft has only a ceiling and generic
   record-boundary stop (`specification.yaml` lines 176–198). It expressly
   requires later numerical probes near 5%, 10%, and 20% (lines 228–237).
   The predecessor requires values be predeclared
   (`EXP-SMTH-71b1b0/specification.yaml` lines 314–324), and the audit confirms
   none were supplied (lines 30–31). A successor must fix the RSS source and
   sampling method, exact probe positions, numerical tolerances/margins,
   acceptance calculation, and required halt/invalidation result.

5. Domain-separation comparability — `amendment_required`. The draft retains
   the numerical seed but changes the domain (`specification.yaml` lines
   159–167), and lines 228–237 require reconciliation. The committed audit
   identifies no valid cross-domain comparison rule (line 31). A successor
   must either forbid predecessor-comparability claims outright or specify the
   compared streams/outputs, expected relation, comparator, and failure
   interpretation. The shared numerical seed alone supplies no such rule.

## Verdict: REVISE

None of the five gaps is resolved from current committed material. The only
permitted recommendation is a future successor revision containing the
minimal rules above. This verdict is a design-boundary finding only and is not
approval, freezing, authorization, evidence, or any claim beyond the stated
toy design ceiling.
