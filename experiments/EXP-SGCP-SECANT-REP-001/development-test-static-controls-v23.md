# Development-Test Static Controls V23

## Handoff: V23 direct-pipeline repair controls

### Claim or task

Falsify the V22 outer-positional expansion defect and verify the proposed V23
three-stage pipeline semantics without invoking Docker, protected source,
protected test, or any repository runner.

### Status

OBSERVATION

### Assumptions

- Controls execute only shell text copied from or structurally equivalent to
  the uncommitted V23 host candidate.
- Shell functions stand in for archive, tee, and Docker only to observe
  argument routing, stderr routing, stage status, and wrapper classification.
- These controls do not authorize P, A, C, R, Docker create/start, protected
  parsing, protected import, protected runtime, tests, or experiments.

### Evidence so far

- `jq empty` accepted the V23 protocol candidate.
- `zsh -n` accepted the V23 host candidate.
- Constructing the exact V23 `pipeline_script` assignment in a no-argument
  function under `set -u` returned
  `assignment_without_outer_positionals=GO`.
- The retained script contains direct
  `docker start -a -i "$cid" 2>"$container_stderr"` and no nested
  `/bin/zsh -f -c` stage.
- A synthetic direct-command pipeline routed exactly
  `start`, `-a`, `-i`, and `cid-v23-control` to the third stage and routed its
  stderr marker to the designated file.
- Success recorded statuses `0,0,0` and wrapper status 0.
- First-stage failure recorded statuses `7,0,0` and wrapper status 74.
- Second-stage failure recorded statuses `0,8,0` and wrapper status 74.
- Third-stage failure recorded statuses `0,0,9` and wrapper status 9.
- Every synthetic status file contained exactly three LF-terminated records.
- After normalizing version, path, parent, and tree identities, the V22/V23
  host diff contains exactly the direct-Docker pipeline-stage replacement.
- The inherited authorization and result validators are byte-identical to
  V22.

### Failure modes

- The controls do not prove Docker behavior or protected execution.
- The controls do not replace exact-commit theory, accounting, or red-team
  review.
- Any later byte change to the host invalidates the observed host digest and
  requires rerunning these controls.

### Next concrete action

Bind this record as an immutable parent input, update the V23 parent
commit/tree, freeze the exact four-file P delta, rerun syntax and hash checks,
and obtain three fresh exact-commit reviews.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-static-controls-v23.md`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v23.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-host-runner-v23.zsh`
