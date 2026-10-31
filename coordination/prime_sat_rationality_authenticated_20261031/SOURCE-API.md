# Corrected authenticated rationality interface — prospective draft

Status: prospective fixed implementation contract; execution requires published admission and native ownership.
Prerequisite: published DEC-20261031-cd6460 and exact review/ledger archive.
The frozen source at 48dfd36341d00beaf0b0ed803411dae68d522fdf and independent R1 failure remain unchanged.

## Interfaces and trust

Add a new module, importing the reviewed builders and generic evaluator without modifying them. The public descriptor contains trusted p, a, b, block kind, nilpotent degree when applicable, and projection. Prime p>3 is an explicit caller premise; nonsingularity and canonical coefficients must still be checked. Metadata provided by an untrusted circuit is never the source of the public descriptor.

1. `canonical_circuit(public_descriptor)` reconstructs symbolic IR with default witness assignments. Return only the circuit, never use a default assignment as a supplied witness. Nilpotent blocks use `nilpotent_square_block`; guard/slack use `linear_B_square_block`; constant uses `constant_B_block(curve, [1])`. The nonzero dummy B=1 populates the discarded assignment; b0 remains symbolic in the circuit. Preserve symbolic input coefficients and deterministic ordering. Exact JSON type comparisons must distinguish bool from int.
2. `check_authenticated_assignment(circuit, assignment, expected)` validates the public descriptor, compares the complete supplied circuit with the canonical reconstruction, then calls the existing generic evaluator. Require exact equation coefficients, monomials, labels, names, projection, metadata and schema. A fixture-specialized equation system must fail authentication even if all its residuals vanish.
3. `check_authenticated_chart(w, candidate)` checks the exact integer outer k, 0<=k<=5, and k=len(U.coeffs)-1 before stratum selection. Validate monic canonical U and the existing shape obligations. Derive the expected block descriptor from this validated chart and the selected arm, authenticate the candidate circuit, then invoke existing membership and signed reconstruction checks. Do not replace the independent frozen reference check with candidate acceptance.

Default builder assignments do not authenticate the mathematics of the builder. That dependency is the independent coefficient audit retained in TASK-20261031-60575a. The wrapper provides content binding to that reviewed source; this scope must be explicit.

## Fixed regression obligations

Retain all original 15 chart fixtures and the F1 two-beta signed regression. For every applicable arm, report candidate and independent reference acceptance separately. Add R1 exactly: F5, y²=x³+1, target(0,1), interval t=0,s=1, A=-X, B=X, U=X^4; change both chart degree tags from4 to3. The frozen checker acceptance is historical evidence; the corrected interface must reject before branch selection.

Exercise outer k bool, float, negative, above5 and degree mismatch; exercise zero, constant and linear B branches. Reject mutations of a coefficient, equation omission, equation replacement by zero, fixture specialization, altered projection, reordered names, unexpected metadata, wrong field/curve/kind/degree, missing and noncanonical assignment values. Separate parser rejection from authentication rejection and arithmetic residual failure. Valid circuits with invalid assignments must not be reported as authentication failures.

Fresh reviewer independently authors expectations and malformed inputs; producer tests/results/README remain hidden. Prospective maximum four suite invocations per producer/reviewer, each240seconds and2GiB; all attempts retained. No census, parameter search, SAT instance or timing comparison belongs to this correction contract.

## Accounting and exit

Record canonical-builder invocations, equation/term comparisons and evaluator events separately; do not label operation counters elapsed-time results. Never discard authentication, reconstruction or certificate-checking work from later SAT totals. Completion requires an independent scoped review, frozen source hashes, exact output archive and inspected report. Only then admit the bit compiler and complete projected SAT comparison; preserve all chart strata and canonical range constraints.
