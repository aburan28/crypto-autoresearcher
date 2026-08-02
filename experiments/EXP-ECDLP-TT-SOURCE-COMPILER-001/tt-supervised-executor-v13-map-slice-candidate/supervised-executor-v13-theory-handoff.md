## Handoff: V13 Typed Private-Map Slice

### Claim or task

Replace the action-authored E0 private-map result with a request-bound typed
observation while preserving the V12 checkpoint boundary.

### Status

`HYPOTHESIS` | `MODEL-BOUND` | `ZERO-RUN`

### Assumptions

- V12 root
  `98dba44fb4e79fd4d156a04ec6a528d2fa98d528d8e7c8fa16f18f58fa4c60da`
  remains authoritative.
- The descriptor token is a finite-model class, not proof of an OS descriptor.
- The gateway is a modeled evidence source and is not proven truthful.
- The selector bytes remain unchanged.

### Evidence so far

- V12 established request/observation and one-shot patterns for spawn and reap.
- P001 already creates the exact durable intent needed as an observation
  subject.
- P003 and P004 already separate failure-terminal and success-receipt paths.

### Failure modes

- A selector source asserts syscall success before observation.
- P002 continues to author the map result.
- A P001 request or intent is consumed twice or in E0 close mode.
- Observation value and descriptor bytes disagree.
- A failed observation produces an opened receipt.
- The map failure cannot be committed and finalized.
- Builder and verifier disagree on the first rejection.

### Next concrete action

Make P001 the observation request, add `WAIT(private_map_open)`, and construct
the typed E0 map-failure trace in both reducers.

### Artifact paths

- `V12-REAP-SLICE-CHECKPOINT.sha256`
- `V12-REAP-SLICE-PUBLICATION.json`
- `V12-REAP-SLICE-DECISION.json`
- `build_v13_closed_kernel.mjs`
- `verify_v13_closed_kernel.mjs`
- `supervised-executor-contract-v13.md`
- `supervised-executor-topology-decision-v13.md`

