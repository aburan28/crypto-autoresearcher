# Degree-five closure through a checked degree-four quotient

Status (2026-10-30 23:13 UTC): the D4 panel has 26 terminal inputs of 32,
including 19 certified LFD-at-least-five results. The newly completed
n45 polynomial03 input has independently accepted codimension 12,742 and
fresh exact count 6. All 46 variable-closure checks and 47 worker artifact
hashes passed. Its 288,550,808-byte certificate is public; anonymous download,
decompression and object-store readback verified. See its
[report](reports/panel-local-n45-poly03-001/report.md),
[publication receipt](panel-local-archive-001/fresh-n45-poly-03-rref-local01.publication.json),
and [corrected inventory](runtime/panel-remaining-after-local006.json).
Six original panel inputs remain. Inventory 006 corrects copied descriptive
metadata in 005; its terminal bindings and counts are unchanged.

The n47 random02 degree-five job was submitted at 21:15:56 UTC and is
running with the qualified blocked implementation. Actual memory/disk
admission passed, and the retained seed bytes verified. A fresh original
checker accepted the D4 seed with codimension 61,196 after all 48 variable
checks; fresh enumeration confirmed four solutions. The D5 producer started
at 21:30:33 UTC. [Closed stage receipts](validation/rand02-blocked-frontier-progress-002/manifest.json)
retain these results. Only an independently accepted D5 codimension greater
than four establishes LFD at least six for this input.

The producer has published four verified durable checkpoint manifests.
The [latest observation](validation/rand02-blocked-frontier-progress-004/observation.json)
records completion of phase-zero variable 0 and entry into variable 1;
the latest snapshot is 1,826,505,616 bytes, with S3 object size checked.
This is resumable computation state, not an accepted D5 certificate.

A separate [RREF exporter](RREF-EXPORT.md) for later D4 inputs passed all
14 fixed equivalence controls. Its 12 completed certificates match the
reference bytes and pass independent checks; both constant-one cases emit
no certificate. The [report](reports/rref-export-001/report.md) and validated
export retain all 81 files. The separately packaged worker completed the
n45 polynomial03 scientific input with all per-worker controls and the
original checker. No runtime comparison is claimed.

The n47 random00 degree-five attempt freshly counted zero solutions and
verified byte identity and historical acceptance of its D4 seed. Its pod
was terminated in response to imminent node shutdown at 20:43:47 UTC,
with exit code 137 and zero restarts. Ten durable objects remain, but no
native checkpoint, D5 certificate, or final result. The
[interruption report](reports/seed-reuse-frontier-interruption-001/report.md)
retains the exact job, pod, and object hashes. This is a terminal interruption;
no replacement frontier job or restore has launched. An accepted positive
D5 codimension on this zero-solution input would establish LFD at least six.

The blocked rewrite with bounded export and native checkpoints has passed
28 native configurations and nine actual local-worker controls; see the
[native](reports/blocked-checkpoint-001/report.md) and
[local worker](reports/blocked-checkpoint-worker-001/report.md) reports.
Its first cloud source job reached its scheduling deadline without executing
controls. The second cloud qualification completed all nine controls: three fresh
certificates, three deliberate checkpoint stops, and three restored certificates
in a distinct pod. All six completed certificates match their references and
pass the original checker; all 556 archived file hashes verify. The
[report and export](reports/blocked-checkpoint-worker-cloud-002/report.md)
retain the results; export validation returned zero findings and the PDF was
inspected. The next large input is n47 random02, with a
[frozen blocked protocol](rand02-blocked-frontier-protocol-001.json) pinning
that qualification. Its actual memory/disk admission and fresh exact count
remain part of the worker execution. Candidate checkpoints remain bound
to the candidate binary; they cannot restore the original binary's state.

Seven of 47 original high-memory inputs have terminal records; 40 remain
unfinished. The next original input, n47 random02, has a published accepted
D4 seed and a [dimension profile](reports/rand02-envelope-001/report.md).
Its D5 cascade remains unfinished. The calculated blocked allocation envelope
is recorded in runtime/rand02-blocked-envelope-arithmetic-001.json. The
additional-workspace term in that record omitted the native stride padding;
the write-once [correction](runtime/blocked-envelope-correction-001.json)
gives 94,262,240,264 bytes for both random02 and random03, with
8,816,974,840 bytes below the 96 GiB child limit. These are source-derived
allocation bounds, not observed memory use. The random03
[dimension profile](validation/rand03-envelope-001/result.json) independently
agrees with the random02 counts: 126,387 border coordinates and 187,583
working coordinates. No independently checked
LFD-at-least-six result has yet been obtained.

The dense producer works in every monomial of degree at most five. This
prototype first rewrites degree-five monomials using a triangular, checked
degree-four quotient map, then imposes multiplication consistency on a smaller
coordinate space. The numerical size of that space is not assumed in advance.
This is not a claim that all frontier instances fit the present host.

## Next original frontier seed

The next original input after active n47 random02 is n47 random03. Its saved
D3 certificate and system hashes were verified against the recovery plan;
the previous D4 lift was resource-capped. The separately frozen
`rand03-d4-local-protocol-001.json` prepares direct D4 closure using the
qualified RREF exporter, fresh exact counting, and the original checker.
Its calculated admission envelope is 21,372,163,527 bytes under the unchanged
40 GiB child limit; this is allocation arithmetic, not measured RSS.

The request launched locally at 23:12:36 UTC after polynomial03 terminated.
Both campaign locks and unchanged memory admission passed; all three worker
controls passed, and fresh counting returned 2 solutions. The original
independent checker accepted the completed D4 certificate with codimension
at least 61,196, so this exact input has LFD at least 5. The collector
verified all 47 worker artifacts and the successful terminal record in
`validation/rand03-d4-local-final-001`. The [report](reports/rand03-d4-local-001/report.md)
records the exact evidence and public readback. This accepted seed prepares
the original D5 continuation; it neither completes that frontier input nor
adds an input to the separate 32-input D4 panel. No field, target, subspace,
or sample was redrawn.

Its [next D5 request](runtime/rand03-blocked-frontier-request-001.json) and
[frozen protocol](rand03-blocked-frontier-protocol-001.json) pin the published
seed, fresh count target two, corrected memory envelope, and qualified blocked
worker. The [prepared job](runtime/rand03-blocked-frontier-job-001.json) has
not been submitted; the protocol requires the active random02 frontier job
to become terminal and capacity to be reconciled first.

The next original D4 panel input, n45 polynomial04, passed bounded memory
admission after 535.5 seconds at 00:35:53 UTC on October 31. Its three
worker controls passed, fresh exact counting found zero solutions, and D4
production is active. The five remaining n45 random-subspace input systems,
plans, and protocols are committed and frozen in inventory order behind it.
After a local D4 attempt is terminal, `collect_panel_result.py` verifies its
pinned artifacts, controls, exact count, and original checker transcript.
`normalize_local_certificate.py` then creates a write-once publication view
from that verified collection without changing the raw attempt. The normalizer
was exercised against the completed n45 polynomial03 result, including its
certificate hardlink, and rejects the active n47 random03 attempt before a
terminal record exists.

## Soundness argument to review

Write B for the Boolean polynomial ring and B_d for its degree-at-most-d
subspace. Suppose the checked map pi_d has kernel U containing the input
polynomials F, all of degree at most d, and U is closed under multiplication
on U intersect B_(d-1). Do not assume U = W_d.

Choose monomials Q mapping to the coordinate unit vectors, and require that
h_m = m + pi_d(m), written using Q, is triangular in the producer's declared
monomial order. Then the nonzero h_m form a basis of U. The implementation
checks triangularity rather than inferring it from checker acceptance.

For each degree-(d+1) monomial divisible by the leading monomial of a degree-d
h_m, use one relation x*h_m to rewrite it recursively. Retain the remaining
high monomials together with Q as coordinates. Every rewrite lowers the
order: a same-degree term stays later when multiplied by the missing variable,
unless Boolean reduction lowers its degree. This gives a surjective linear
map rho: B_(d+1) -> E. Its kernel is generated by U and the chosen triangular
rewrite relations. Representatives of every coordinate are monomials.

Insert rho(x*h_m) for every seed relation and variable into a row space R in E.
Order high coordinates before the Q coordinates. The echelon rows whose pivot
is in Q span R intersect span(Q). For each newly inserted such row r, insert
rho(x*r) for every variable x, and continue to a fixed point. Finite dimension
bounds the number of independent insertions; all generated rows are retained.

Let pi be rho followed by the quotient E -> E/R and let K = ker(pi). Every
low-degree element of K decomposes as a seed-kernel element plus a combination
of the low-coordinate rows of R. Their variable products have all been
annihilated by construction. Thus K contains F and is closed under variable
multiplication on K intersect B_d. It follows directly from the definition
that W_(d+1)(F) is contained in K. Surjectivity yields the codimension lower
bound. If pi(1) is nonzero, this is a candidate certificate of nonmembership;
only independent checker acceptance permits that claim in reported data.

If pi(1) is zero, the result is `projection_kills_one`. It is inconclusive for
membership in the true closure unless equality of the seed kernel with W_d
is separately established. The reference tests may establish equality for
their small fixtures; that must not be transferred to arbitrary input maps.

For an LFD lower bound of d+2, the accepted codimension bound must additionally
exceed an independently justified solution count. Nonmembership alone does
not give that bound on a satisfiable instance.

## Validation and resource boundaries

`quotient_lift.py` is a small-instance reference implementation, capped at
12 variables by default. It emits the unchanged certificate format expected
by the independent checker in the original dossier. Frontier use needs a
native implementation, a prospective allocation model, a frozen protocol,
and independent acceptance of its actual certificate. The original dense
producer remains a small-fixture correctness reference.

## Sources checked

- Internal: `../semaev-m2-last-fall-degree/verify/cert_check.py`, including C0–C3,
  and `../semaev-d5-closure-feasibility/review-correction-20261019.md`.
  These fix the containment semantics and forbid claiming kernel equality.
- Retrieved: [Sage's official Boolean-polynomial documentation](https://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/pbori/pbori.html),
  Boolean quotient representation and bounded Gröbner-basis options. A solver's
  degree cutoff is not substituted for the explicit closure condition here.
- HKY's official CRYPTO 2015 PDF was attempted again on 2026-10-29 and returned
  HTTP 403. The 2017 JSC DOI landing page was also inaccessible through the web
  tool. No claim to a full new reading or algorithmic novelty is made.

The argument above is a written construction rationale, not a Lean theorem
or an external expert review.

## Native candidate

`quotient_lift.cpp` implements the same construction using M4RI multiplication
and elimination in the provisional coordinate space. It has an explicit
allocation envelope and emits `projection_kills_one` rather than claiming a
refutation when the constant vanishes. Its output uses the unchanged original
certificate format. Small fixtures compare it with the reference implementation
at three chunk sizes, including multiword coordinates. Four native Semaev
outputs also passed the original independent checker; transcripts and certificate
bytes are retained in `validation/native-checker-20261029/`.

The structural profile completed on all 13 historical seeds under frozen
`profile-protocol-v2.json`: both enumeration directions agree. The validated
unified export and graph/PDF are in `reports/profile-001/`. These profiles are
not degree-five closure runs. A separately frozen and checkpointed execution
is still required before using the native candidate on historical/frontier inputs.

## Completed historical trial

The frozen historical lift trial completed all thirteen inputs and all thirteen fresh exact counts. Q35a and Q35b yielded maps accepted by the original independent checker, with checked codimensions6 and2 equal to their exact solution counts. The other eleven constructed quotients killed the constant; these outcomes remain inconclusive for the true W5 closure. No degree-six lower bound or new upper bound follows from this batch.

The [complete report](reports/native-lift-historical-001/report.md), graph, PDF, immutable raw records and validated unified export are retained. Both accepted certificates have public download and object-store readback receipts in `archive/`. The native implementation PR2696 merged.

The n47–51 frontier requirement remains open. One prospective alternative is a checked D3 seed followed by successive D4 and D5 lifts, avoiding a prerequisite dense D4 seed calculation. The native primitive supports these degrees and has single-stage software comparisons; a complete two-stage control and new frozen protocol are required before scientific execution. No frontier feasibility or scientific outcome is inferred from this proposal.

## Frontier successive-lift execution

The consecutive D3-to-D4-to-D5 controls now pass: all nine maps from three fixtures are independently accepted and match direct dense codimensions. The complete driver also passes its count/checker control; see [control notes](validation/CASCADE.md).

`cascade-plan.json` retains all fifty n47–51 inputs from the original panel. `cascade-protocol.json` was frozen and checkpointed before launching `run_cascade.py`, one worker with a16 GiB cap. Outputs live at `/home/ec2-user/fall-degree-data-20261029/frontier-cascade-001`; each input keeps all accepted intermediate maps and logs. Original dense-panel attempts remain unchanged.

At initial observation, the first n47 input has an accepted D3 certificate with codimension10093 and fresh exact count0; this supports only LFD>=4. Its D4 lift was admitted under the allocation envelope and is running. No completed frontier D5 map or LFD>=6 is claimed. Resource refusal and quotients killing the constant remain explicit unknown outcomes for later stages.

## Retained frontier bounds and separate continuation

At reconciliation on2026-10-29 15:00 UTC, the original frontier owner was absent and its lock was free. Twenty attempts were terminal:17 resource-capped and3 without a degree-three certificate. Seven accepted degree-four maps support LFD>=5: n47 polynomial-basis indices00–04 and n48 polynomial-basis indices00 and04. The n47 checked codimensions are21428 (indices00–03) and21430 (04); their exact solution counts are0,2,2,0,2. The two n48 checked codimensions are26570, against counts2 and0. No degree-six bound follows from a memory refusal.

The completed n49 degree-four candidate was retained without claiming acceptance. The original expanded panel also stopped after108 outcomes. Cause of owner loss is unknown; missing processes are not mathematical evidence.

The separate `highmem-protocol.json` continues47 inputs: all17 capped cases plus30 unfinished/unattempted cases. It pins18 retained seeds, always rechecks them against the original independent checker, and uses the separately validated blockwise exporter under a standalone64 GiB cap. Its detached owner and exact command are recorded in `runs/frontier-highmem-001.launch.json`; outputs are `/home/ec2-user/fall-degree-data-20261029/frontier-highmem-001`. The old two40 GiB workers remain stopped during this placement.

The original50 records remain authoritative for their attempts. Continuation outputs must be joined by `prior_id`, preserving old outcomes and taking only justified lower bounds. They are not47 additional independent inputs, and20+47 must not be reported as67 distinct instances. The three original no-certificate outcomes remain visible. The rest of the original expanded campaign is still outstanding.

## High-memory continuation: two terminal results

The immutable [third progress snapshot](reports/highmem-progress-003/report.md) records two terminal inputs out of47. The first n47 polynomial-basis input retained its accepted D4 map (codimension21428, exact count0, LFD>=5). Its D5 construction killed the constant and produced no usable D5 certificate. This gives neither an upper bound nor a conclusion about membership in the true W5 closure. The second input has accepted D4 codimension21428 and D5 codimension2, with exact count2. It retains LFD>=5; equality at D5 gives no stronger lower bound or upper bound. Both accepted stages are publicly archived with anonymous and canonical-store GET/hash verification. The remaining45 inputs include the live third input; no degree-six bound is recorded.

The continuation-specific [publication linkage](highmem-archive/fresh-n47-poly-00-D5-cascade01-highmem01-D4.publication.json) binds the retained certificate and fresh checker/count evidence to the already-public original certificate. A fresh anonymous GET verified all three original assets, and gzip decompression reproduced the continuation certificate hash. The original public receipt still describes the original attempt; the linkage records the continuation provenance separately. The new snapshot has no missing publication acknowledgement for its completed stage. This changes evidence availability, not the mathematical bound or sample count.

## High-memory continuation: five terminal results

The [fourth immutable snapshot](reports/highmem-progress-004/report.md) adds polynomial-basis inputs02–04 at n47. All retained D4 certificates and fresh checker/count transcripts were verified. Inputs02 and04 have accepted D5 codimension2 equal to their exact count2; input03 killed the constant at D5. All retain LFD>=5, with no degree-six or upper bound. Five newly archived stages passed anonymous public and canonical-store readback verification. The continuation now has five terminal and42 unfinished inputs; the live random input00 remains unfinished. These are continuations of original named inputs, not additional independent draws.

## n47 random input 00: accepted D4, capped D5

The [fifth immutable snapshot](reports/highmem-progress-005/report.md) records six terminal inputs and no degree-six bound. The original independent checker accepts the D4 certificate with codimension lower bound 61,196 and exact solution count 0, establishing LFD >= 5. The following D5 lift was refused by the frozen 64 GiB allocation gate. This leaves degree six and upper bounds unknown. The [resource obstruction record](../../problems/semaev-degree-five-lift-exceeds-64gib.md) preserves the next capacity and qualification requirements; the active driver continues the remaining frozen inputs unchanged.

The [retained-seed capacity calculation](reports/native-envelope-001/report.md) reproduces a 152,976,386,232-byte native envelope for this D5 lift. Both border enumerations agree. Even chunk 1 exceeds this host total memory, so reducing the batch alone cannot admit the existing representation. A separately qualified larger-memory instrument/host or reduced representation remains necessary. No new LFD bound follows.

The separate [bounded-export allocation candidate](BOUNDED-EXPORT-MEMORY.md) passed generic byte-equivalence and nine independently checked Semaev stages. It removes a full-output-map reservation left over after blockwise export, giving a calculated 85.791 GiB envelope for this seed. Runtime placement and a frozen frontier continuation are still required; no large input has run on it.

The [n44 random03 report](reports/panel-v3-n44-rand03/report.md) retains an accepted D4 codimension 31,780 against exact count zero, establishing LFD >= 5; all 47 artifact hashes and public archive readback verified.

The [n44 random02 report](reports/panel-v3-n44-rand02/report.md) adds accepted D4 codimension 31,780 against exact count 2, establishing LFD >= 5. The separate bounded-export D5 job was submitted after both panel jobs finished; see [submission receipt](runs/bounded-lift-submission-001.json). Submission alone establishes no new mathematical result.

The blocked candidate's small cloud source job
`semaev-blocked-worker-source-20261030-1700` was submitted at 18:58:52 UTC.
It is Pending with scheduler-reported affinity/selector/taint constraints;
no controls have run and no dependent restore has launched. See the
[scheduling problem record](../../problems/semaev-blocked-worker-cloud-scheduling.md).
The original large n47 job is still active and has not been replaced.
