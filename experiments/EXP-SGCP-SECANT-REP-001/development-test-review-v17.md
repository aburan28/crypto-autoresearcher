# Development-Test Execution Review V17

## Handoff: bootstrap prefix execution and timeout-target ambiguity

### Claim or task

Determine whether V17 safely constructs and authorizes exactly one isolated
five-test development run.

### Status

NEGATIVE RESULT

### Evidence so far

- Static review at commit
  `86949f81808d73f976cdae33f48013f5d2345ab3`, tree
  `5cedb9144a026c6876f7d40c776a1495f717327e`.
- Sole parent:
  `43457546abc899d1dedf5c9fde11272657b41564`.
- Protocol SHA-256:
  `7f46182cfcec726f555f36f15ef28fb824058d83ea5ab572963724d04d23e641`.
- Host SHA-256:
  `0d894b388cf309dded36f81a8e45d31c5c74ccc29954635dddeec7c43f72b259`.
- Authorization-validator SHA-256:
  `e1b028e166fd5ca729c516fa12fe1dd934817d88eec63db4d8d655eea2b5cbe4`.
- Result-validator SHA-256:
  `4005f772e585e971ebdf089608f3e10189acf146a08682437519d24813540a22`.
- Theory principal `019fae67-7991-7a50-8bdf-ac1fcde6ad0d` and
  accounting principal `019fae67-a857-7cc1-b690-545e69b635c8` returned
  scoped `GO`.
- Red-team principal `019fae67-db89-7b90-b07d-67cd137b79c5` returned
  `REVISE`.
- Inert controls confirmed exact object identity, manifest replay, closed
  post-run stages, Docker-state derivation, cleanup derivation, and zsh
  variable safety. No protected source/test parser, import, compile, test,
  runner, bootstrap, or experiment execution occurred.

### Positive controls that survived

1. Current-tree manifest replay rejects missing, extra, changed, symlink,
   nonregular, newline-named, ambiguous, and duplicate paths.
2. Cleanup proof is reconstructed from exact exit, stdout, and stderr
   artifacts for both container ID and name.
3. Container exit and OOM helper values are cross-checked against validated
   post-run Docker inspection.
4. Only the complete and incomplete closed post-run evidence stages can seal.
5. C/R parentage, exact trees, all-zero CAS, direct nonsymbolic refs, and
   development-only claim boundaries survived review.
6. The monitored host closes inherited FD 3, and no zsh special-parameter
   collision remains.

### Failure modes

1. `STREAMED_HOST_PREFIX_CAN_EXECUTE`: the canonical bootstrap pipes
   `git show` directly into `zsh -s` and checks the producer status only after
   the pipeline. A late producer timeout or truncation can therefore execute a
   syntactically complete host prefix before EOF, including the host `main`
   call, without proving complete host bytes or retaining the intended suffix.
2. `TIMEOUT_TARGET_NOT_BOUND`: `derive_timeout_observed` accepts arbitrary
   nonempty suffixes after the TERM and KILL prefixes. A two-line log naming
   different command targets, such as `alpha` then `beta`, is accepted as a
   valid wrapper-137 timeout observation.

### Strongest valid statement

V17 closes V16's artifact-custody, cleanup, Docker-state, evidence-stage, FD,
and shell-variable defects. It remains unauthorized because the bootstrap can
execute an unverified host prefix and timeout evidence does not bind TERM and
KILL to the same exact command representation.

### Next concrete action

Create V18 that fully materializes the host in a private pre-execution
directory, proves producer success, exact length, terminal LF, and SHA-256
before execution, and requires an exact identical command target in TERM/KILL
diagnostics.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v17.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-host-runner-v17.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-authorization-validator-v17.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-result-validator-v17.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-review-v17.md`

No development-test or experiment-execution authority is granted.
