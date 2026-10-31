# Continuing the four prime-field leads

2026-10-28. The user requested a continuing plan and experiments. This is an
active research worklist, not a claim that a new experiment is admitted or
running. All four directions remain open. Reuse the merged implementation
`0bf1fd1434d9c62916737124a749084dde579f13` (PR #2664), preserving frozen records.

## Immediate observations from retained data

`analyze_retained.py` reads the archived EXP-ECDLP-a9b6a5 matrices and the
October 25 F4 constructed fixtures. It generates no target or collector draw.
`retained-diagnostics.json` records input hashes and exact row certificates.

| p=4099 curve | Witnesses | Unique affine equations | Rank / columns | Nullity | Identifiable single columns | Two-column combinations |
|---|---:|---:|---:|---:|---:|---:|
| a=2,b=13,r=4021 | 97 | 13 | 13/15 | 2 | 0 | 1 |
| a=2,b=16,r=4111 | 67 | 9 | 9/15 | 6 | 0 | 1 |

Both fixtures already contain `P=(0,y)` as the first factor-base atom:
`(0,264)` and `(0,4)`. It is public and already present, so the zero-completion
test changes no base cardinality and introduces no additional unknown column.
This is read directly from the retained fixtures, not a new curve search.

On the retained F4 combined constructed fixture, full-base rows already supply
rank 5. Eliminating outside columns adds **4** further ranks to reach 9. Reporting
9 as the gain from partial rows would overstate the increment. The separate
one-outside and two-outside fixtures add 4 and 1 ranks. The unsigned-looking
triangle adds 0: its signed outside matrix has rank 3. These are exact
recomputations of constructed fixtures, not natural collision-rate evidence.

The two-column Prym combinations are selected after observing the matrices.
They are correctness/control candidates, not natural unknown-scalar targets.

## Execution order

The first new scientific wave should contain **B1 (isolated x=0)** and **C1
(fixed Dickson depth 4)**. They answer different questions and have independent
inputs. Begin with one process per track on a suitably provisioned executor;
parallel execution is optional, not a reason to omit either lane. A0, the
retained-data accounting below, is already complete. Design A1 from actual
partial witnesses and D1 from independently generated public targets; neither
requires B1 to achieve full rank. Keep at most three scientific contracts active
at once, with D1 prepared while the first wave runs.

The current workspace lacks checkpoint transport. The actual canonical gate
attempt and readiness observation are retained under `admission/`; the
[execution problem record](../../problems/prime-field-lead-checkpoint-transport.md)
preserves the exact failure and exit conditions. No alternate
upload mechanism or runner bypass is permitted. This is a runtime impediment,
not a mathematical null result or a user-approval request. Existing source
entry points still require their new protocol/release, complete source/input
locks and normal native supervisor/ownership/export bindings before execution.

## A — Useful information from partial relations

**Question.** Does a proposed partial-relation law produce independent
information on an existing base at lower charged cost?

**A0, completed retained-data check.** Partition stored rows into full-base M
and partial `[B U]` rows; compute
`Delta=rank([[M,0],[B,U]])-rank(U)-rank(M)`. Retain cancellation weights,
rank histories and zero/duplicate combinations. Verify against the archived
separate checker. No cost rate is available for these historical fixtures.

**A1, next prospective test.** Use the prepared F4 all-draw anchored-divisor
program and its frozen inputs as a source, through its own existing admission
route. Preserve every draw, rejected pole, irreducible factor, inverse-pair
aggregation and outside coefficient. Keep curve, subgroup, canonical signed
base, anchor law and function space fixed within each comparison. Compare the
new cancellation scorer with the existing dense kernel oracle on precisely
the same accepted raw rows; this is an exact accounting comparison before a
new collector law is introduced. Constructed shared endpoints are controls
only. Do not assume a random-graph model for naturally sampled endpoints.

**Primary records.** Number of draws, rational divisors, retained signed partial
rows, repeated outside vertices, outside rank, cancellation dimension, zero
mapped combinations, useful base-rank gain, new columns, witness-storage bytes,
and operation vectors for construction/factorization/hashing/elimination.
Measure `Delta / charged cost` only after a common unit and complete boundary
are fixed. Do not sum unlike counters or assign infinite rate to zero cost.

**Controls.** Same-row dense oracle; duplicate and inverse-pair rows; balanced
and unbalanced signed cycles; deliberately corrupted cancellation weights;
matched cardinality and the same subgroup/orbit conventions for base families.

**Successor for each result.** Positive gain: test a sparse signed reducer
against the oracle, then repeat on held-out instances. Zero gain with scarce
edges: change the sampling law in a separate contract. Many edges but no
cancellation: inspect signed incidence rank and endpoint overlap. Many
cancellations mapping to zero: inspect source coefficients and dependencies.
Same informative space produced more cheaply remains worth measuring even
without additional rank. None of these results closes partial relations.

## B — Isolated x=0 completion

**Question.** Do the previously excluded source/constraint points contribute
distinct equations or new syndromes on the fixed 16-atom Prym bases?

**B1, first new collector test.** Two p=4099 fixtures above; exact retained
generator, 16 atoms/lifts, 64-source order and cubic law. Run two fresh arms:
the historical nonzero rule and the completed-zero rule, using the same source
schedule. Each arm has 2,293,760 attempted branches per curve, hence **9,175,040
total scheduled attempts** for both curves and arms. This number is a derived
workload size, not completed execution. No sample, base expansion or rank stop.
Archived observations remain separate from these fresh arms.

**Primary records.** All branch statuses and digests; accepted witnesses;
distinct normalized affine equations; source-zero versus constraint-zero
provenance; rank after every distinct equation; each new row's syndrome against
the old right kernel. Keep exact lift/sign/subgroup verification and all three
pole/residual guards. Report operator counters, failures and storage separately.

**Controls.** New-wrapper nonzero arm versus frozen historical rule on the same
ordered witness stream; marked p=101 software positive already exercises zero;
duplicate x and singular interpolation refusal; corrupted source/sign/status/
rank/digest rejection by `check_prym.py`. Both x=0 deck choices coincide and
must be deduplicated rather than counted as separate geometry.

**Successors.** New syndromes/rank: carry both old and new spaces into D1.
More witnesses but no new equations: canonicalize principal divisors before
repeat interpolation, in a separate charged comparison. New equations but no
new span: retain them and test cheaper production of the same span. No change:
keep the finite result and move to the already proposed common-atom translated
covers or pole-complete spaces, one change per contract. Do not enlarge the
base and change the function law simultaneously.

## C — Complete and price the Dickson extractor

**Question.** Does the exact exterior/cubic-divisor extractor complete the
fixed depth-four P-256 queries, and which stage sets its cost?

**C1, first new algebraic test.** Use the exact existing F1 `inputs.json`:
depth-3 constructed positive and public generator; depth-4 constructed positive
and public generator; enumerative arity-four depth-2 controls; nonseparable and
corrupted-certificate controls. No replacement of a hard target with a planted
one. `max_dimension=560`: the distinct space at depth 4 is C(16,3)=560;
two-equal and all-equal spaces are separately included. Record status per case,
including unknown, memory/resource stop and implementation failure.

**Instrumentation required before a cost claim.** Separate scalar-chain
construction, tensor/operator formation, rank/kernel elimination, restricted
operator construction, character extraction, cubic factoring, curve lifting,
sign enumeration, subgroup verification and the finite oracle. Count what the
implementation actually exposes. FLINT's internal elimination operations are
currently absent: do not rename tensor term accumulations as total field work.
Process CPU/RSS and diagnostic wall time must cover all phases and failed cases.
The oracle is charged validation work, not hidden inside the alleged solver.

**Controls and comparisons.** Complete geometric-state equality using the
separate resultant oracle; complete signed-point-set equality; all three
multiplicity partitions; a missing state/solution, changed root/sign and
nonseparable fibre must be rejected. Price actual signed decomposition against
the best available direct/MITM engine on the identical realized base. Polynomial
state extraction and point decomposition are different workloads; compare
their like-for-like outputs. Historical timeouts on another host are not a
matched timing baseline. A 2 GiB process limit and a declared per-case watchdog
are proposed machine guards, not permission to censor slow cells silently.

**Successors.** Correct completed cases: measure costs at depths 2,3,4 and
choose the next depth from explicit memory estimates. Dominant dense matrix
cost: prototype matrix-free action with exact rank/extraction certificates.
Dominant extraction: compare certified separating-element policies. Any stopped
case remains unresolved; a cubic representation size is not a lower bound on
all possible decomposition algorithms. No exponent claim follows from C1.

## D — Natural target recovery without full base rank

**Question.** Do independently chosen public targets produce useful natural
relations while individual factor-base logs remain unidentified?

**D1, separate frozen target study.** Freeze both original preprocessing spaces
now; if B1 completes, its space is an additional declared arm, not a retroactive
replacement. Freeze a public hash-to-curve rule and domain before generating
targets: `prime-field-leads/20261028/target/v1|curve_uid|j`, j=0,1,2,3 per curve.
Hash to x, try counters in order, take the first rational point with canonical
y and verified r-subgroup membership. Generate no scalar label or scalar
sidecar. Retain all counters/rejections and every resulting target, including
a coincidental base hit. These **eight proposed targets have not been generated**.

Apply the unchanged public multiplier schedule 1..64 to Q. A verified natural
row is `sum(c_i log(F_i))=t*k`; set `source_scalar=0` and
`target_coefficient=t` and call the target-aware independent verifier. Fold
known anchors with the correct sign. Test `v*N=0`, emit original-row weights,
and verify every recovered k through `[k]P=Q`. No requirement that M have full
rank. After a predeclared successful recovery, either stop with its actual
charged prefix or complete the fixed census; the protocol must choose one
before data. Maximum full census is 18,350,080 scheduled attempts across the
eight targets; this is a workload calculation, not an observation.

**D2, if single rows are insufficient.** Stack target equations with M,
retaining the target coefficient as a separate unknown column. Test whether
the unit vector on k lies in this augmented row space. This permits useful
combinations of individually nonidentifiable rows. Reject all zero-target-
coefficient/circular known-witness controls; keep generated but useless rows.

**Controls and costs.** Known-witness recovery is a software positive, never a
natural-target success. Use the post-data two-column combinations only as
explicit constructed controls. Separate no target rows, wrong subgroup/sign,
nonzero kernel syndrome, dependent target rows, zero-Q information and failed
final verification. Include source/base setup, collection misses, linear
algebra, target attachment and final verification. Match the same public
targets to optimized rho and existing IC before any comparative attack claim;
report cold single-target and reusable many-target costs separately.

**Successors.** Natural recoveries: independent replay, then predeclared fresh
curves/targets and calibrated complete-cost comparison. No natural rows:
investigate density/function spaces. Rows exist but k is not identifiable even
in D2: diagnose the target-coordinate kernel before requiring all base logs.
A finite failure does not establish a general rank obstruction.

## Evidence and operating discipline

No per-idea user confirmation is needed. Before a new scientific trial, make
the exact source, frozen protocol, workload, source/input/interpreter locks,
supervisor, ownership and release prospectively runnable through the normal
lab route; preserve the real checkpoint gate. This document is a plan, not that
release. In particular the old F1 preparation and the full-rank E-stage
`blind_recovery.py` gates are not silently modified to admit D1.

Every trial leaves raw outputs, failures and checked certificates; each wave
gets a source-linked report, diagram/PDF and unified export. Distinguish
software tests, constructed controls, retained-data deductions and new natural
observations. An independent claim review is separate from a second code path.
Keep official goals open and avoid status promotion from a successful merge.

Sources reviewed: the merged continuation README and code; original F1
derivation/inputs; `blind_recovery.py` and `independent.verify_row` target
semantics; F4 `report.md`, `receipts/independent-04.json` and signed graph
certificates; the immutable Prym matrices and fixtures named in the analysis.
The PKM 2016 primary sections and cost caveats were read in the implementation
session and remain linked in its source notes. The unavailable KB connector
and issue-only October 27 source boundary remain explicit; no novelty is claimed.

Concrete next operation: restore supported checkpoint transport and finish
B1/C1 protocol/supervisor binding, then execute their frozen workloads. Continue
A1/D1 preparation and retained-source diagnostics while that runtime is absent.
There is no unattended or scheduled experiment running after this session.
