# Handoff: Minimal V11 Stateful-Topology Repair

## Claim or task

Repair the finite closed model so externally determined outcomes are journaled
before selection, recovery derives from replayed evidence, every terminal is
committable, and recoverable and infrastructure finalization have reachable
paths.

## Status

`HYPOTHESIS` | `MODEL-BOUND` | `ZERO-RUN`

## Assumptions

- This is an independent design handoff, not runtime or cryptanalytic evidence.
- The observation gateway may author typed observations only; reducers still
  verify request, subject, attempt, phase, and predecessor bindings.
- OS truthfulness, crash atomicity, PID reuse, filesystem durability, and live
  Git atomicity remain outside the finite model.
- No source snapshot or phase-state snapshot may be accepted.

## Evidence so far

Use one ordering for every external event:

```text
deterministic pending action receipt
-> exactly one typed observation
-> deterministic source derivation
-> selector action
-> exact publication
```

The smallest reusable vocabulary is:

- request-bound map, spawn, and reap observations;
- a restart observation bound to the preceding journal head and lock epoch;
- indexed recovery/finalization process probes;
- a replay-checked prior-journal anchor rather than hand-built recovery state;
- cause-bound closure requests.

Source construction must assign every selector field explicitly. Schema-domain
first values cannot be defaults. Recovery state must be reconstructed from exact
records, with conflicts rejected, in the order committed, ref applied, commit
object, commit intent, terminal, content, result, reap, spawn, launch,
reservation, unseen.

Every failure or quarantine terminal needs a canonical Git encoding. Do not
synthesize fake success result/content records. Commit a failure envelope bound
to the terminal and require nullable intent links on that path.

Infrastructure finalization must route to meter finalization. Recoverable M004
needs a distinct no-closure trigger; meter observation cannot require a closure
request unconditionally.

Likely removal candidates, subject to machine-checked certificates, include
late duplicate live rules, invalid-universe meter rows, and G002 if malformed Git
evidence remains a pre-source rejection. Do not remove map, spawn, reap, restart,
recovery, M001, M004, or M006 merely because V10 could not select them.

## Failure modes

- An action authors an external outcome.
- One request has two observations or one observation crosses request identity.
- Source construction silently uses a domain default.
- Recovery accepts a hand-built state snapshot or unreplayed anchor.
- A failure terminal cannot reach a committed phase.
- Infrastructure closure remains in its originating context.
- A dead-rule claim omits a legal observation value.
- Builder and verifier accept different bytes for one transition.

## Next concrete action

Implement only the P0 spawn-failure vertical slice: AN002 as a no-domain pending
request, a request-bound `spawn_failed` observation, AN003 without source
injection, the canonical failure Git envelope, and replay through committed P0
failure to C004 in both validators.

## Artifact paths

- `V10-REACHABILITY-DECISION.md`
- `build_v11_closed_kernel.mjs`
- `verify_v11_closed_kernel.mjs`
- `supervised-executor-contract-v11.md`
- `supervised-executor-topology-decision-v11.md`
