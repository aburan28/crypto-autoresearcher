#set page(paper: "a4", margin: 16mm)
#set text(size: 10pt)
= Prime-field factor-base continuation
29 October 2026 · implemented software and correctness checks

Zero new scientific trials and zero p=4099 natural targets generated. This is a
software delivery report, not an experiment result or independent claim review.
The source-linked worklist and launch boundaries are in README.md.

#image("diagram.svg", width: 100%)

== Target combinations without full base rank
The new augmented system keeps each target coefficient: vz − tk = offset.
Testing the unit vector on k produces weights on original base and target rows,
with an explicit affine certificate check and public verification [k]P=Q.
Several individually insufficient rows can identify k while base logs remain
unresolved. Exhaustive F5/F7 software controls check this property.

The target-aware Prym collector uses the existing cubic construction and x=0
completion, fixes preprocessing anchors from public multiples of P, and verifies
source labels against Q with the separate arithmetic checker. It retains all
branches, witnesses, useless rows, recovery prefixes and failures. The fixed
public hash recipe generates no scalar label. Tests at p=101 check projected
equations as point identities and reject corrupted target labels. The eight
proposed p=4099 public targets remain ungenerated. Complete independent target
branch replay is still required before scientific interpretation.

== Dickson stage accounting
Optional instrumentation exposes construction, kernel elimination, restriction,
character extraction, cubic factoring, curve lifting, signs, subgroup checks
and the finite oracle. Failure events are flushed. Software fixtures at p=127,
depths 2 and 4, return exactly the same states, signed solutions, certificates
and counters as the uninstrumented path. The 560-dimension guard precedes
allocation; the frozen core, exterior arithmetic and inputs are unchanged.

CPU/wall clocks are diagnostic and include instrumentation overhead. Process
RSS is a lifetime high-water mark, not a phase-local peak. Solver-total events
include inner stages and must not be added to them. FLINT internal elimination
operation counts remain absent. No calibrated profile, speedup or attack-cost
bound is claimed.

== Checks and remaining execution boundary
The regression log records 164 passing tests and nine existing optional-msolve
skips. It includes IC, partial cancellation, target recovery, complete signed
extraction, Prym replay, checkpoint and relay checks. Final focused checks and
source hashes are in validation.json. The oversized historical PNG preview is
regenerated at 90 dpi (51,905 bytes); SVG, raw data and historical PDF are intact.

All four leads remain active: natural partial-row cancellation against the dense
oracle; the fixed two-curve x=0 comparison (9,175,040 planned branches); the
fixed P-256 depth-four cases; and eight independent natural public targets.
These are proposed workloads, not completed counts. The managed executor still
has no supported checkpoint transport. No new gate attempt or scientific job
was started. New exact protocol/native release and ownership/supervision
bindings remain necessary in addition to the real S3 checkpoint.

Sources: October 28 PLAN.md and retained diagnostics; original F1 core/exterior;
Prym relations/independent/collect_width; prior PKM 2016 sections 2.4, 3.1–3.5
retrieval and digest in the October 28 validation record. No novelty, natural
recovery, performance or scientific-status claim is promoted.
