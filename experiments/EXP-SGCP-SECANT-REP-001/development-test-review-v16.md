# Development-Test Execution Review V16

## Handoff: recovery custody and derived-evidence gaps

### Claim or task

Determine whether V16 safely constructs and authorizes exactly one isolated
five-test development run.

### Status

NEGATIVE RESULT

### Evidence so far

- Static review at commit
  `dba478b2a70f2444e1c9b6251de79674dd6219cb`, tree
  `2f966a315e349a4a2a136de0ae2c10a8f2328cf8`.
- Sole parent:
  `0942a6ed8f391b138080289207238e63e13f98d4`.
- Protocol SHA-256:
  `ab2fbbc6c07d408294cf2ddfed8a09e093ecbc598253cd9fc304f7e3274dcc1a`.
- Host SHA-256:
  `8e0e4cf17d7b3ff5a37d66b256b7862523c6e3221a238cbc8ccf9003f07bdea0`.
- Authorization-validator SHA-256:
  `e1b028e166fd5ca729c516fa12fe1dd934817d88eec63db4d8d655eea2b5cbe4`.
- Result-validator SHA-256:
  `845129536b531fe9bc8384005ba2168180e2027ce5e56bf804a14c74e60d01c0`.
- Theory principal `019fae49-8906-74e2-b8e7-c24445ac1b30` and
  accounting principal `019fae49-c360-7192-89a0-6ac3a054f6c4` returned
  scoped `GO`.
- Red-team principal `019fae49-f051-7a22-900b-283f897281aa` returned
  `REVISE`.
- Inert controls confirmed exact outer timeout mapping, child-output
  separation, strict three-record parsing, raw/receipt mismatch rejection,
  and false-OOM rejection. No protected source/test parser, import, compile,
  test, runner, bootstrap, or experiment execution occurred.

### Positive controls that survived

1. Outer TERM preserves create-pending and active-container states as exits
   178 and 180; forced outer KILL maps to 124.
2. Host output cannot spoof the aggregate timeout diagnostic channel.
3. Pipeline status accepts exactly three LF-terminated integer records and no
   fourth record.
4. Receipt hashes and the seven-field causal tuple reject direct raw/receipt
   contradictions.
5. C/R parentage, exact trees, all-zero CAS, create/signal windows, and
   development-only claim boundaries survived review.

### Failure modes

1. `MANIFEST_NOT_REPLAYED_ON_RECOVERY`: R recovery validates the committed
   manifest hash but does not re-enumerate current artifacts or compare every
   path and digest. A manifest-only artifact can disappear or an extra artifact
   can appear while selected receipt checks still return validated R.
2. `CLEANUP_PROOF_NOT_REDERIVED`: recovery trusts the receipt cleanup boolean
   and exit zero rather than reconstructing exact ID/name absence from cleanup
   status, stdout, and stderr artifacts.
3. `TIMEOUT_GRAMMAR_IS_PREFIX_ONLY`: any line beginning
   `gtimeout: sending signal ` is accepted, including an unknown signal token.
4. `OOM_HELPER_NOT_CROSS_CHECKED`: `oom-killed.txt` is not independently
   compared with `.State.OOMKilled` in the bound post-run Docker inspection;
   container exit has the same transcription boundary.
5. `FAILURE_STAGE_IS_UNDERCONSTRAINED`: non-valid R can use broadly nullable
   causal fields and `ABSENT` hashes without a stage-specific mandatory
   artifact set, making early failure and later artifact loss indistinguishable.
6. `OUTER_FD3_REMAINS_INHERITED`: the monitored host inherits the saved output
   descriptor even though it does not need to retain it.
7. `EXCLUSION_COUNT_IS_STALE`: protocol prose says 78 exclusions while the
   exact array contains 81 distinct principals.

### Strongest valid statement

V16 closes V15's protected-timeout prefix, outer ownership-state, pipeline
wire-format, selected raw-hash, and basic causal-tuple defects. It remains
unauthorized because full current artifact custody, cleanup absence, timeout
grammar, and Docker-state causality are not independently reconstructed during
R recovery.

### Next concrete action

Create V17 with exact manifest replay, derived cleanup and Docker-state tuples,
strict pinned timeout grammar, a closed post-run evidence stage, closed FD 3,
and the corrected exclusion count.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v16.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-host-runner-v16.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-authorization-validator-v16.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-result-validator-v16.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-review-v16.md`

No development-test or experiment-execution authority is granted.
