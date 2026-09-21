# Full SDEG counter-protocol readiness

**Disposition: revise the protocol; retain the proposed mechanism.**
EXP-ECDLP-9cd134 is not ready for implementation or measurement. The governing
RQ-SDEG-001 explicitly requires independent protocol review before either.
Standing user authorization is already satisfied; the remaining work is
technical completion and genuine independent review, not another approval
question to the user.

This is a readiness review only. DEC-20260908-2b80aa changes no hypothesis,
experiment or goal status, and the original records remain immutable. The
companion repair contract defines twelve concrete completion requirements;
it does not pretend those requirements are already an executable frozen
scientific specification.

| Source-backed issue | Required full-scope repair |
| --- | --- |
| Original counter proposal | Preserve at least four prime sizes and twenty instances per size, separate paired timing/counting processes, multipliers 1/2/4/8/16, same-core load 0/1/2/4, all four M/S/I/A event types, exact counts under load and all finite timing/ratio targets. |
| Governing SDEG scope | Bind the complete ten-cell ladder: S3 at 8/10/12/16/20/24 bits with caps 16/24/32/48/64/80, and S4 at 8/10/12/16 bits with caps 12/16/20/24; each factor-base size is min(cap,floor(p/4)). Preserve rho/BSGS, independent decomposition certificates and nine conservation controls. |
| Authority | Design-only conversion and preliminary theoretical design PASS do not discharge independent-protocol-review-first. Reassess current verifier/fixture/sealed-schedule and other activation residuals from contemporary evidence; historical notes do not establish present global state. |
| Existing S3 timer | `measure_s3_decomposition` times only `sympy.groebner(..., order='grevlex')`. Basis analysis and `_find_decomposition` enumeration, lifts/signs and sums happen afterwards. Do not label that timer full decomposition cost. |
| Existing S4 support | The inspected file defines S4 by resultant with simultaneous substitution but contains no S4 measurement function. Preserve S4 implementation/certificate requirements instead of reducing the panel to S3. |
| Solver/backend pins | The harness leaves method/version/domain backend unspecified. Repository dependency is `sympy>=1.12`; inspected installation is 1.14.0. `groebner(method=None)` consults mutable configuration. Freeze the actual algorithm/backend and verify identical timing/counting paths. |
| Hook bypasses | Parent-read `modularinteger.__truediv__` multiplies directly after inversion, `__pow__` delegates to modular `pow`, and `__rtruediv__` can combine inversion with `__mul__`. A multiplication wrapper can omit or double-count work. First establish the actual active backend and complete event boundary. |
| Backend selection | Parent-read `finitefield._modular_int_factory` can select flint nmod/fmpz_mod for prime moduli, with ModularIntegerFactory as fallback. Python wrapper inspection is not proof that those hooks lie on the actual solver path; pin and inspect the chosen backend before relying on them. |
| Calibration | Freeze independently predicted programs for M, S, I and A across the whole multiplier range, including nonzero inversion and fault controls. Schoolbook multiplication alone may only exercise M/A. No observed counter total may serve as its own expected answer. |
| Fixture generation | The inspected generator hashes requested bits then calls nextprime without an explicit resulting bit-length assertion. Freeze exact admissibility, requested/actual bits, order/target/factor-base/lift certificates, rejection accounting and fixture costs; do not silently resample favorable systems. |
| Curve-free control | Specify actual matched variables/degrees/support/sparsity/coefficient construction under the same solver. A coarse match does not prove equal complexity or uniquely isolate elliptic structure. |
| Seeds and counts | Reconcile five declared seed labels with twenty instances/seeds per cell, modes, multipliers, loads and baselines. Pin master mapping and hash tuple byte encoding. The old 240-run estimate is not a scientific count. The ten-cell minimum alone is 200 EC system instances before other factors. |
| Load and profile | Freeze burner programs, topology, affinity, pairing, order, timers and boundary fraction. Keep monotone load time and factor>=1.5 as targets, and monotone wall/weightedops with factor>2 across size as a separate target. They are not guaranteed laws. |
| Size exclusions | Retain the original boundary-time fraction>0.5 exclusion for specified slope summaries, while publishing excluded measurements and reasons. It does not bound uncounted arithmetic. Fewer than four eligible sizes leaves that family's scaling claim inconclusive. |
| Statistics | Use shared-instance 2000-bootstrap paired deltas and fixed local-slope/median definitions. Original practical agreement and disjoint marginal intervals can overlap; resolve them prospectively with mutually exclusive paired-delta categories. |
| Full resource vector | Charge setup, relation collection, linear algebra, descent, verification and shared overhead, with exact workflow mapping and justified NAs. Weightedops is supplementary; it cannot replace the governing lawful ICEX numerator or omit search, enumeration, certificates and checking. |
| Independent verification | Existing certificate checking shares the producer's EllipticCurve implementation. Its name does not establish independent authorship/runtime. Require the actual governing certificate interface, independent verifier/review/hash and controls. |
| Protection/artifacts | Freeze the real runner/solver/burner process tree, aggregate 8 GiB limit and readback, CPU affinity, exclusive launch/receipt/checkpoint files and complete tables/certificates/hashes. Four burners plus runner already require five processes; extra supervisors must be counted. |

The statistical repair preserves the original practical tolerance without
contradictory labels. Define paired delta as timing slope minus supplementary
weighted-operation slope on the same retained panel. Agreement requires both
the estimate and its paired interval within [-0.05,0.05]. Disagreement requires
both entirely above 0.05 or entirely below -0.05. Other valid configurations
are inconclusive. Marginal-interval disjointness remains visible as a
diagnostic. A precise difference of 0.01 can therefore be practically agreed
without being assigned a competing primary disagreement label.

The proof-search audits target the actual uncertainty. Known-count calibrators
for all four types, certified baselines and conservation controls provide the
exact baseline checks. Equal weighted totals can hide different typed counts;
small profiler fractions can hide arithmetic omissions; matched coarse null
features can hide algebraic differences. The full panel, algorithms, events,
seeds, weights, statistics and resource interfaces must precede measurement.
A counter that passes M/A schoolbook checks while omitting S/I is the nearby
false object that the complete protocol must reject.

The smallest future formal obligation is a finite typed-event trace count
recurrence for the actual calibration programs, then a separate source-hook
refinement binding. Calibration degrees/programs, active backend and complete
hook semantics are not yet fixed. An abstract event-count identity would not
prove SymPy coverage, decomposition correctness or full costs. Revisit exact
formal statements during protocol completion and independent review; no
general Lean or Mathlib absence is claimed.

Sources and supplemental installed-code findings were actually read by
`parent_control_plane/01a07d9c-ceb4-7892-ae01-260e4b5f0374` and transmitted with
hash receipts. The parent read the full question, goal, cited preliminary
evidence and `harness/semaev.py`, the specified scaling-protocol blocks, and
the named generator/SymPy segments. It did not represent those excerpts as
every line of the scaling protocol or as an executed SDEG package. This
Coordinator performed no commands, experiments, calibrations, proofs or tests.

The unavailable process-local knowledge collection is not evidence that no
prior counter record exists. Instrumentation overhead remains unmeasured.
One-host observations cannot prove machine dependence; matching curve-free
behavior cannot identify a unique cause; no blanket assertion about all
reachable or cryptographic scales follows. The reviewed sources support
specific readiness defects and a full repair path, not scientific rejection.

Design readiness requires concrete choices and procedures for every R1–R12
item, including the exact solver/backend, calibrator formulas, scientific
controls, verifier interface and runtime acceptance tests. It does **not**
require a newly implemented verifier or observed runtime receipts before the
independent protocol review. Those actual code/verifier hashes, realized
fixtures and admission receipts are implementation/activation outputs after
the governing review permits implementation. Their future hashes bind bytes
generated under fixed choices; they cannot stand in for algorithm choices
left undecided at design time. The repair contract's `stage_gate_mapping`
makes these separate gates explicit and removes the circular dependency.

**Next action:** archive these three files, then immediately trace the selected
SymPy FiniteField and polynomial-ring coefficient callgraph, including backend
delegation, to fix method/backend and M/S/I/A hook semantics and source-backed
coverage. Complete the paired statistical decision schema alongside it. The repair contract
assigns this first phase to the responsible Coordinator, then full R1–R12
completion, genuine independent protocol review, and only afterwards
implementation and activation. Future runtime, realized fixture and verifier
values do not block the source/design work now; do not substitute repeated
gate audits for it. Keep the full pending approval/design objective active and
complete this scope rather than choosing a synthetic-only task or easier candidate.
