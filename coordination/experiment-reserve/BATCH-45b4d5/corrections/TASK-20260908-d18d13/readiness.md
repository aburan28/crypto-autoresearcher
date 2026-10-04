# Complete CM pre-run outcome definition

TASK-20260908-d18d13 adds a closed pre_run_outcome carrier for the15existing early refusal/infrastructure reasons at authorize_and_claim_nonce. It requires independently trusted task/handoff identity, UTC time and an available/unavailable authorization-input observation. It forbids RUN, code, scientific input, resource, directory and admission facts in the minimal carrier. A policy-resolution failure preserves the governing writer block; other reasons cannot smuggle it.

The contract requires constructor and receiving verifier to compare trusted_handoff exactly against independently established invoking context, never against the receipt itself. Before moving beyond authorization, the launcher must establish the factual context required by the normal manifest. Refusals are delivered to the trusted invoking control plane without creating a RUN directory or deriving paths from untrusted input. This defines an interface; no actual authorization/refusal or scientific runtime was executed here.

All24other effective-contract sections are unchanged, including the cost relations and23scientific sections. The prior raw_cost, allocation_edge and manifest schema definitions are unchanged. Their prior cost-schema binding is retained explicitly; the new artifact schema extends the top-level carrier only.

Two complete suites passed294/294each, for588/640fixed executions and0failures. The second suite followed an explicit trusted-context validation clause. Both source states, reservations, UTC command/case boundaries, output hashes, exits and telemetry are retained. Aggregate external wall time19.76s andCPU17.25s; maximum observedRSS75,317,248bytes. The actual memory-enforcement results are in the receipt and no hard-limit success is inferred from RSS.

All67source bindings were rechecked. No curves, fixtures, CM computation, allocator, scientific panel, Sage/PARI process, private key, signature, nonce, lock or RUN allocation occurred. Approved_by remains null and execution/evidence flags remain false.

Next action: snapshot the exact five files underTASK-20260908-e5fdfd, then independently review the new carrier, trusted-context semantics and preservation of the three prior carriers before any protocol approval.
