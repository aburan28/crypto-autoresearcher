# BATCH-033 scope decision — ordinary-input nonlinear acquisition

## Selected lane

BATCH-033 implements DEC-20260802-205: one proof-only lane asking whether
ordinary ECDLP input G, alpha*G can produce alpha^d*G or an equivalent
certified nonlinear scalar generator below rho-scale expected cost.

The alternative deliverable is a scoped generic-group acquisition barrier with
an exact model, proof, and explicit non-generic escape interfaces.

## Known baseline

Cheon's DLP-with-auxiliary-input algorithm is prior art:

- input: G, alpha*G, alpha^d*G, with d dividing r-1;
- time: O(sqrt((r-1)/d) + sqrt(d));
- balanced time: N^{1/4+o(1)};
- rho/distinguished-point low-memory implementation.

Primary source:
https://www.iacr.org/archive/pkc2012/72930594/72930594.pdf

APR-206 and its augmented-input variants are known rediscoveries. BATCH-033
must not polish, re-propose, implement, or claim novelty for that route. It may
state the baseline only to compose acquisition and downstream costs.

## Durable basis

- BATCH-032 synthesis:
  1cf6ad5e115728416e977e56d715511490ef3700.
- Producer snapshot:
  dbd03c4b26e48a5a093e6740588044c4f666aa4a.
- Independent review snapshot:
  636f3975e3a66c4d76c5e2115ac0f835069a7459.
- Binding decisions: DEC-20260802-204 and DEC-20260802-205.

## Dispatch order

1. TASK-20260802-218 — completed Coordinator control-plane authorship.
2. TASK-20260802-219 — isolated snapshot of the ten TASK-218 artifacts.
3. TASK-20260802-213 — Idea Generator after verified TASK-219.
4. TASK-20260802-214 — isolated snapshot of TASK-213.
5. TASK-20260802-215 — independent Red Team after verified TASK-214.
6. TASK-20260802-216 — isolated snapshot of TASK-215.

An archive runs alone. A failed, invalid, cancelled, stalled, or unverified
predecessor unblocks nothing.

## Tool-surface transport

The Idea Generator is assumed to lack a repository filesystem interface.
INPUT-CAPSULE.md is sent verbatim in-message. TASK-213 returns five delimited
payloads, which the Coordinator materializes verbatim at the declared paths.
TASK-215 may use the same transport with the exact TASK-213 payloads and
verified TASK-214 hashes.

## Focus and budget

focus_queue.json admits exactly one active lane. Its four stages total 7,200
wall-clock seconds, at most 4 GiB, and one agent invocation. Experiment-run
budget is zero. Idle capacity admits no second lane.

Reranking occurs only after TASK-215 is archived by verified TASK-216.

## Claim ceiling

Permitted:

- a typed sub-rho acquisition construction;
- a scoped generic-group acquisition barrier;
- explicit escape interfaces and proof obligations;
- a composed ordinary-input Pareto row using Cheon as known baseline.

Forbidden:

- experiment execution or Executor dispatch;
- augmented-route rediscovery or polishing;
- novelty, first, best-known, SOTA, support, or breakthrough claims;
- hypothesis, goal, or direction status changes;
- knowledge promotion, lane death, or closure.

## Exclusive write scopes

- TASK-218: exact decision, scope, capsule, focus queue, and six task cards.
- TASK-219: BATCH-033/archives/TASK-20260802-219/.
- TASK-213: BATCH-033/tasks/TASK-20260802-213/.
- TASK-214: BATCH-033/archives/TASK-20260802-214/.
- TASK-215: BATCH-033/tasks/TASK-20260802-215/.
- TASK-216: BATCH-033/archives/TASK-20260802-216/.

The scopes are pairwise non-overlapping.

