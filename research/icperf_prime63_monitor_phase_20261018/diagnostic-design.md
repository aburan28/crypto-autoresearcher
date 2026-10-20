# Proposed prime63 m=2 positive-control diagnostic

**Status: unapproved design proposal.** This document defines a possible fresh-ID experiment for Coordinator specification and preapproval. It contains no run ID, result, or execution authority. The engineering handoff TASK-20261018-3b41b1 authorizes zero scientific solver calls.

## Fixed inputs and question

Use the exact 63-bit prime-field B=475 archived systems in `research/icperf_prime63_pilot_launcher_20261017/planted_public.json.gz`, witnesses in `planted_witnesses.json`, and the pinned 475-point natural-system archive. Prelist exactly these three m=2 positives: `coset-m2` with `quadratic_lift`, `random-m2` with `direct`, and `small_x-m2` with `direct`. Their `p` is 9223372021248595841. The later protocol must bind the file SHA-256 values from `source_manifest.json`, extract requests byte for byte or publish their exact serialized digests, and use the same public curve and point sets. The original six 300-second time censors from RUN-ICPERF-7ed866 remain historical evidence and are not retried under that run ID.

Question: under a bounded, instrumented call, which phase consumes time and memory in each positive control, and does any return a root that an independent checker can lift to a full-point relation? The serialized m=2 supports (coset 25 variables/26 equations/60 monomial occurrences/maximum input degree 4; random 3/4/964/475; small-x 3/4/962/475) describe inputs only. They do not measure degree of regularity, Gröbner complexity, or relative runtime.

## Proposed protocol boundaries

- One fixed call for each of the three named positive cells, in the order coset, random, small-x. One synthetic monitor fault-injection null control runs first and must end `infrastructure_monitor_error`, retain raw trace and logs, and never report zero RSS for the unreadable live child. The null uses no Sage algebra.
- Proposed per scientific call: 600 seconds wall, 8 GiB sampled process-tree RSS, 8 GiB scratch, model-count cap 64, one worker. Require at least 16 GiB scratch free at start and stop below 8 GiB free. The three scientific calls plus null and cleanup have a proposed 2,100-second total watchdog. These are prospective limits, not edits to EXP-ICPERF-891f7f.
- Record `input_load`, `polynomial_ring` including ideal construction, `groebner`, `model_count`, `root_enumeration`, and `response_write` start/end/error events with monotonic nanoseconds, source SHA-256, sampled tree RSS, scratch/free bytes, and a null marker when telemetry is unavailable. Fsync each event to an external append-only trace. The supervisor owns timeout/kill and hashes partial trace, request, response when present, stdout and stderr into raw custody. Missing response after timeout is a censor; missing response after an unclassifiable monitor fault is infrastructure/invalid, never zero roots.
- Each control has exactly one scheduled attempt. Continue after an independently checked certificate, a bounded timeout, or a model-cap censor. Stop the scientific sequence immediately after a monitor fault, lost raw custody, source/input hash mismatch, checker disagreement, or resource cap; record remaining cells as unattempted. Never extend a call cap inside the same protocol. Retain all attempts and their first-attempt receipts.
- An independent checker separately evaluates every encoded polynomial at each returned root modulo `p`; verifies each selected point lies on the archived full curve; checks signed full-point addition equals the archived target point; checks factor-base membership and the chosen signs/indices; and rejects a root with one changed coordinate. The checker cannot use the producer's `variety()` result as its own proof and must bind its source hash. A root is not a useful relation merely because x-coordinate equations vanish.

## Prospective inference table

| Bounded observation | Allowed inference | Next decision |
| --- | --- | --- |
| Root plus independently checked polynomial and full-point certificate | This exact positive system has a valid witness under the tested source and limits; report its phase cost and resource samples. | Consider a separately frozen m=2 natural-yield and rank protocol. Do not select a factor base from a positive control alone. |
| Timeout or model-cap censor with valid partial trace | Only the exact stage reached and elapsed wall/RSS bounds are observed; no root count or Gröbner degree is inferred. | Change solver/formulation design prospectively; keep unattempted work missing. |
| Returned root contradicts independent equation or point check | The backend/encoding/checker pipeline is inconsistent for that cell. | Preserve both artifacts and seek independent backend review before any cost comparison. |
| Monitor fault, lost trace, or unreadable live child | Infrastructure classification; scientific result unavailable. | Repair and retest instrumentation before a fresh scientific contract. |
| Null fault injection fails to produce its expected fail-closed state | Monitor control failure. | Do not admit scientific calls under this monitor. |

A separate future non-Gröbner m=2 arithmetic control could enumerate the same 475-point pair space (225,625 ordered pairs before any symmetry reduction) and check full-point sums against the fixed targets. Its base setup, enumeration, memory and verification must be charged separately; it is a proposed correctness/time reference, not a measured result or part of this handoff.

## What remains after this diagnostic

Even a checked m=2 positive certificate does not measure natural relation yield, useful rank, linear algebra, target descent, complete cold/online index-calculus cost, or matched rho. It does not rank the three bases at m=2..8 or address Koblitz and ordinary-binary curves. Direct S8 at m=7 and direct S9 versus chained S3 at m=8 remain separate formulation obligations.
