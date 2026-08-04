# BATCH-032 scope decision — barrier formalization and exponent-first escape

## Selected lane

BATCH-032 implements `DEC-20260802-203` and the previously approved
`TASK-20260802-206`.

The task must:

1. formalize the fixed-field/fixed-order isogeny obstruction;
2. formalize the information-loss and inverse-success obstruction exposed by
   the failed quotient proposal; and
3. search for one certificate-bearing exponent-first mechanism that violates a
   named premise and still beats matched Pollard rho after complete expected
   cost and Pareto accounting.

This is research and proof design only. No experiment or Executor is authorized.

## Durable basis

- TASK-201 producer snapshot:
  `801524409339d0b4a49faed09f6c5dd2e83e4769`.
- TASK-202 independent Red Team snapshot:
  `e4d7f710ea24570ac4e17193f95a9da32206d59a`.
- BATCH-031 synthesis:
  `bd9552672`, parent `e4d7f710e`.
- Binding decision: `DEC-20260802-202`.

The reviewed result is bounded, not a closure:

- over fixed `F_p` and fixed subgroup order `N`, prime-to-`N` isogenies preserve
  the relevant trace/order data;
- `k=ord_N(p)` is fixed by `p` and `N`;
- a prime field has no proper subfield for prime-field subfield descent.

The proposed successor `IDEA-20260802-201-01` is falsified as written:

- its quotient has cardinality `N`, not `N/M`;
- projected search at `sqrt(N/M)` work has success about `1/M`;
- inverse-success accounting removes the claimed exponent improvement;
- cost units, scalar orientation, and Pareto coverage require repair.

## Dispatch chain

1. `TASK-20260802-211` — completed Coordinator authorship of the decision,
   scope, input capsule, focus queue, and six task cards.
2. `TASK-20260802-212` — isolated snapshot of TASK-211.
3. `TASK-20260802-206` — Idea Generator after TASK-212 verifies.
4. `TASK-20260802-207` — isolated snapshot of TASK-206.
5. `TASK-20260802-208` — independent Red Team after TASK-207 verifies.
6. `TASK-20260802-209` — isolated snapshot of TASK-208.

Archives run alone. A failed, invalid, cancelled, stalled, or unverified
predecessor unblocks nothing.

## Tool-surface transport

The Idea Generator is assumed to have no compliant repository filesystem
interface. `INPUT-CAPSULE.md` is therefore supplied verbatim in-message.
TASK-206 returns five explicitly delimited payloads. The Coordinator
materializes them verbatim at the declared TASK-206 paths.

The same transport may be used for TASK-208 with the capsule, exact TASK-206
payloads, and verified TASK-207 hashes.

## Claim ceiling

Permitted:

- a scoped proof decomposition;
- corrected cardinality and inverse-success derivations;
- a Pareto-screened successor proposal;
- explicit open escape conditions.

Forbidden:

- experiment execution;
- implementation or Executor dispatch;
- status or goal changes;
- knowledge promotion;
- universal closure or lane death;
- crypto-scale validation;
- breakthrough or supported-complexity claims.

## Budget interpretation

Queue `maximum_runs: 1` means one bounded agent invocation, as required by the
dispatcher schema. Binding experiment-run budget: zero.

## Focus discipline

`focus_queue.json` admits exactly one active lane: TASK-20260802-206. It records
the decision-changing uncertainty, decisive positive/negative/inconclusive
evidence, deterministic next decisions, excluded peripheral work, and the
rerank trigger after TASK-20260802-208 is archived by verified
TASK-20260802-209.

Its four analytical stages total exactly 5,400 wall-clock seconds, use at most
4 GiB, and authorize zero experiment runs. No idle capacity admits another
lane.

## Exclusive write scopes

- TASK-211: exact decision, scope, capsule, focus queue, and six task-card files.
- TASK-212: `BATCH-032/archives/TASK-20260802-212/`.
- TASK-206: `BATCH-032/tasks/TASK-20260802-206/`.
- TASK-207: `BATCH-032/archives/TASK-20260802-207/`.
- TASK-208: `BATCH-032/tasks/TASK-20260802-208/`.
- TASK-209: `BATCH-032/archives/TASK-20260802-209/`.

No write scopes overlap.
