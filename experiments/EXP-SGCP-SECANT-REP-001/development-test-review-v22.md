# Development-Test Review V22

## Handoff: V22 stopped before protected execution

### Claim or task

Record the exact V22 authorization consumption and host-shell failure without
interpreting it as source, test, or ECDLP evidence.

### Status

NEGATIVE RESULT

### Assumptions

- Protocol P is commit `33373f3f85051d3bedc1de1523c218eefe1306e4`,
  tree `5590c05fe345a6567eba6a1332dd2d9d93bf204d`, with sole parent
  `f321e059987755c979291612d244ccee1f1de046`.
- Authorization A is commit
  `295ca78938d1fabee2a796e55f1a6c08aee62742`, tree
  `b254750448afba5539d91e055c2ddce23d7aec7b`, with sole parent P.
- Consumption C is commit
  `a704527f4a100323dd7ef15003e27edff9327ceb`, tree
  `1747e48834d687f1f4feaed619dc9d76c00af304`, with sole parent A.
- The V22 authorization is consumed and must never be retried.
- The created V22 container and untracked V22 run directory are preserved as
  evidence and are not modified by this result record.

### Evidence so far

- Theory reviewer `019faec2-88a5-7091-b144-73fd8e7f1ba1`,
  accounting reviewer `019faec2-c9cd-7052-a486-1a0482e3ca30`, and red-team
  reviewer `019faec3-0a76-78f3-87c3-71bf9db9b02d` each returned `GO` for P.
- The canonical authorization validator accepted A before execution.
- The one-shot bootstrap was invoked exactly once and exited 1 with
  `run_container:5: 1: parameter not set`.
- C records
  `authorization_consumed_before_protected_execution` and
  `maximum_runs_remaining: 0`.
- Result ref
  `refs/crypto-autoresearcher/results/EXP-SGCP-SECANT-REP-001-development-test-v22`
  is absent.
- Container
  `b8657c024ac2c9bdcfd78379ae588d83e154bd750f27ac1f686706715e3bbef4`
  exists with status `created`, `Running=false`, PID 0, zero start and finish
  timestamps, `OOMKilled=false`, and exit code 0.
- No `input.tar`, protected stdout, protected stderr, resource receipt,
  pipeline-status receipt, post-run inspect, cleanup receipt, run receipt,
  manifest, or result seal exists.
- Sourcing only the frozen V22 `run_container` function and invoking it without
  arguments reproduces the same error before an external command is reached.
- The failure is caused by the nested single-quote splice in the ANSI-C-quoted
  `pipeline_script`: inner `$1` and `$2` are exposed to the outer function
  under `set -u`.
- No protected parse, import, compile, test, or runtime execution began.

### Failure modes

- The V22 host constructed a nested `zsh -c` script using a quote splice that
  terminated the intended ANSI-C quote early.
- Shell nounset converted the exposed inner positional parameter into a fatal
  function error before `/usr/bin/time`, the pipeline, or Docker start.
- The fatal function exit bypassed the planned post-run cleanup path, leaving
  an owned container in the created state.
- Manual deletion would mutate preserved failure evidence and is outside this
  result record.

### Next concrete action

Create V23 with a fresh run, authorization, consumption, result, and container
identity. Replace the nested shell with a direct Docker start pipeline stage,
prove the three-stage status and argument routing in an inert synthetic
control, and obtain three fresh exact-commit reviews before any authorization
is constructed.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v22.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-host-runner-v22.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-authorization-validator-v22.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-result-validator-v22.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/DEV-SGCP-SECANT-PURE-CORE-V22/`
