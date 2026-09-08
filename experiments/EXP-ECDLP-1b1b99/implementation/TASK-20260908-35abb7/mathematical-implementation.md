# Executable conventions for the corrected finite CM contract

## Scope

The code implements the future finite calibration stated in `coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260907-fe3f53/EXP-ECDLP-1b1b99.yaml`, as prospectively approved by `DEC-20260908-166ad3`.  This file documents code paths; it reports no fixture, timing, ratio, or scientific observation.

For a candidate source `E_0: y^2=x^3-x` over `F_p`, `Curve` carries canonical affine integers and the point at infinity.  Candidate construction checks

\[
N=p+1-t,\qquad D_\pi=t^2-4p=-4f_\pi^2,\qquad v_3(f_\pi)=1,
\]

the largest-prime subgroup conditions, and full rational `E_0[3]`.  The fixture record retains every rejected prime candidate and its reason.  The implementation is called only by an admitted future runner; no current command invokes it.

`full_rational_three_torsion` enumerates all eight nonzero torsion points, pairs each point with its inverse, and rejects any result other than four distinct cyclic kernels.  `normalized_velu_map` applies the degree-three normalized Vélu formula.  `exact_dual` enumerates target kernels and finds the unique normalized dual together with the explicit short-Weierstrass normalization for which the composition is `[3]`.  The source and target composition predicates are separate.  Endpoint classes are made from actual Fp-isomorphisms and must partition `K0` through `K3` into two size-two classes.

For an endpoint `K`, the executable map names match the contract:

\[
\phi_K=\alpha_K\circ v_K,
\qquad
\psi_K=\widehat v_K\circ\alpha_K^{-1},
\qquad
\beta_K=\phi_K\circ\iota\circ\psi_K.
\]

`CoordinateEndpoint` uses `\phi_{K,u}=\rho_u\circ\phi_K` and `\psi_{K,u}=\psi_K\circ\rho_u^{-1}`.  The dual therefore always applies the inverse coordinate transport.  Controls check both compositions, `\iota^2=[-1]`, `\beta^2=[-9]`, `\beta=[m]`, and failure of the wrong `\lambda` and the negative-`m` alternatives on the canonical target sample.

## Deterministic data and custody boundary

`StreamState` implements the contract’s SHA-256 compact JSON stream over `[experiment_id, purpose, [p,A,B,r,k,u,arm], seed, counter]`.  Counters are preserved by stream key and every rejection consumes a digest.  A base query sequence is created once for an endpoint-coordinate-seed-q workload and is reused for every arm.  `PublicEvaluatorBatch` is a closed public schema; `PrivateVerifierBatch` alone has fixture/kernel/class labels, generators, scalars, expected points, certificates, and the opaque join.  Unknown or private fields in the public wire form are rejected.

`run_selection_matrix` constructs the six scalar-arm, seven-block q=256 selection panel.  It scores integer process-group CPU nanoseconds in each of the nine interval-by-coordinate strata and chooses the minimum with the lower numeric arm ID as the exact tie rule.  `run_timing_matrix` reuses those frozen winners, preserves all warmup and block records, alternates arm order using the fixed shuffle stream, and checks the required main, top-control, and identity-control cardinalities before reduction.

`BlockCost` is the typed raw cost tensor entry.  `Allocation` carries explicit rational weights and integer CPU/wall allocation; `allocate_equal` implements the specified canonical remainder distribution and `reconcile_allocations` rejects every missing weight or nanosecond mismatch.  The reduction reports opaque PARI operation counts as `null` with a reason, while CPU, wall, and RSS remain data fields.

## Authorization, resources, and artifacts

`verify_future_authorization` accepts only canonical detached payload bytes and a signature verified by the exact bound OpenSSL binary with the repository’s fixed public PEM.  It verifies runtime and source hashes, snapshot ancestry and byte equality, code and execution-plan hashes, output path, provider/model prohibition, and a one-run nonce claim.  It never accepts a caller-selected key or verifier, reads no private key, and returns typed refusal codes instead of treating an exception as authorization.

`Custody` writes atomically into `runs/<run-id>.partial`, fsyncs every item, records progressive receipts, never replaces an existing artifact, and atomically publishes only after all twelve required artifacts are nonempty.  Process-group metric records use monotonic nanoseconds, self plus waited-descendant CPU, platform-specific RSS units, live process-group RSS inspection, and group termination/wait receipts for child work.  Cancellation produces a preserved partial directory and has no scientific meaning.

The hard reducer treats empty, missing, or false stage/control/coverage conditions as invalid or partial.  It cannot promote a finite run into an asymptotic result, ECDLP-use result, novelty finding, lane closure, or breakthrough claim.
