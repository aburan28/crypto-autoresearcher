# BATCH-034 scope decision — B033-S1 producer-bound repair

## Selected lane

BATCH-034 implements DEC-20260802-208 as exactly one bounded proof-only lane.
It asks whether the narrow producer-output route surviving BATCH-033 can be
made rigorous in the ordinary generic-group model. It does not restore or
polish the false certificate lemma.

The first proof action is mandatory: apply RT-215-C1 with producer output
`R=G` and a perfectly sound generic-DLP verifier. This separates correctness
of the producer's output from work done by a verifier or certificate system.
Any argument that again charges verifier-created labels or collisions to the
producer is out of scope.

## Durable basis

- TASK-213 producer snapshot:
  `7516d91c156a662aed73c4acc6bb17a088c70370`, parent
  `59b50c5c2594b7b9ab7343feef9a8c23416f68d5`.
- RT-215 review snapshot:
  `6cd133ee45e1bf8793a87be84eefa7c5f131e0dd`, parent
  `7516d91c156a662aed73c4acc6bb17a088c70370`.
- BATCH-033 synthesis snapshot:
  `590032bbc8cfc022b949bf44023ca2bf992744e0`, parent
  `6cd133ee45e1bf8793a87be84eefa7c5f131e0dd`.
- Schema-corrected DEC-20260802-206 and CORR-20260802-001:
  `482b2e9ba342a5f8c4b5c38e2c42e87fa6fd7db5`, parent
  `590032bbc8cfc022b949bf44023ca2bf992744e0`.

## Proof boundary

TASK-224 must formalize all of the following or mark the exact item open:

- a fixed symbolic transcript whose choices are independent of `alpha`;
- raw-encoding-dependent branches, not merely equality branches;
- the exact root union for collisions and producer-output agreement;
- an oracle-issued output handle, or an explicit encoding-guess term;
- preprocessing cross terms using the `q_g+1` online-label boundary;
- preprocessing construction, accesses, comparisons, amortization, and peak
  memory;
- per-attempt cost multiplied by inverse success for expected work;
- separate time, memory, and data/query axes;
- piecewise `dominated_by` and quantitative `sota_delta` fields, using
  `not_applicable` for ordinary-inadmissible rows.

Cheon auxiliary-input DLP and generalized nonlinear-target generic hardness
are prior art. A repaired proof is neither novel nor a breakthrough. Ordinary
time, memory, and data/query SOTA deltas remain zero.

## Dispatch order

1. TASK-222 — completed Coordinator authorship of ten immutable controls.
2. TASK-223 — isolated snapshot of exactly those ten sources plus its receipt.
3. TASK-224 — one filesystem-free Idea Generator invocation after verified
   TASK-223.
4. TASK-225 — isolated snapshot of exactly four TASK-224 artifacts plus its
   receipt.
5. TASK-226 — one new independent Red Team after TASK-224 and verified
   TASK-225.
6. TASK-227 — isolated snapshot of exactly three TASK-226 artifacts plus its
   receipt.

An archive runs alone. Failed, invalid, cancelled, stalled, or unverified
predecessors unblock nothing. `max_concurrent` is two, but the dependency graph
admits only one task at a time.

## Transport and artifacts

The producer is assumed to have no repository filesystem. Send
INPUT-CAPSULE.md verbatim. TASK-224 returns exactly four delimited payloads for
verbatim materialization under `tasks/TASK-20260802-224/`:

- `repaired-producer-bound.md`
- `proof-obligations.yaml`
- `pareto-frontier.yaml`
- `provenance.yaml`

TASK-226 owns exactly `red-team-report.md`, `verdict.yaml`, and
`provenance.yaml` under `tasks/TASK-20260802-226/`.

Every immutable source artifact is assigned exactly once. The mutable
`dispatch_queue.json` is not evidence and is excluded from TASK-223, TASK-225,
and TASK-227 snapshots.

## Budget and stopping rule

The focus queue has one stage: 1,800 wall-clock seconds, at most 2 GiB, one
research-deep invocation, and zero experiment runs. The independent Red Team
has at most 3,600 seconds, 4 GiB, and one invocation.

Stop the producer after one complete repaired theorem candidate or one exact
unresolved proof obstruction. Stop the batch after the independent review is
snapshotted. Later Coordinator synthesis is a separate decision path.

## Claim ceiling

Permitted: a scoped, prior-art-correct producer-output theorem candidate or a
named obstruction to that exact proof route.

Forbidden: experiment, Executor, implementation, certificate-lemma revival,
status transition, knowledge promotion, closure, support, rejection, novelty,
SOTA, or breakthrough.
