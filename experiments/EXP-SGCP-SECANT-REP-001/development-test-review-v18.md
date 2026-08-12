# Development-Test Execution Review V18

## Handoff: aggregate timeout diagnostics bypass their filter

### Claim or task

Determine whether V18 safely constructs and authorizes exactly one isolated
five-test development run.

### Status

NEGATIVE RESULT

### Evidence so far

- Static review at commit
  `a286f9c553248d6771740c77ec106ff2cd123d12`, tree
  `9d18661da61209887992bbcdf6b1e5b151a6cdd7`.
- Sole parent:
  `edb224bafaf5cf7c8214d3d95a387fe2e6361ebd`.
- Protocol SHA-256:
  `5166f9c0dbed1acfb135a28799cd01c1014955d105f062eb39e89c859efcdb60`.
- Host SHA-256:
  `ffaa642273ce2965aca50794ab7e3d72c6dc759a97d02ad03c602564ddc4c169`.
- Authorization-validator SHA-256:
  `e1b028e166fd5ca729c516fa12fe1dd934817d88eec63db4d8d655eea2b5cbe4`.
- Result-validator SHA-256:
  `4005f772e585e971ebdf089608f3e10189acf146a08682437519d24813540a22`.
- Theory principal `019fae7a-6aba-73f0-9656-7b6b2deb4a68` returned
  scoped `GO`.
- Accounting principal `019fae7a-6a2d-7cf1-9eb3-5eb597db186f` and
  red-team principal `019fae7a-6b21-7b92-86f9-fc24ff2dd4cc` returned
  `REVISE`.
- Exact-commit inert checks proved successful complete host retention:
  producer status zero, 89668 bytes, terminal LF, and the bound SHA-256.
  Mismatched protected TERM/KILL targets were rejected. No protected
  source/test parser, import, compile, test, runner, bootstrap, validator, or
  experiment execution occurred.

### Positive controls that survived

1. The host is completely retained before execution, with producer status,
   exact length, terminal LF, and SHA-256 all checked.
2. Failed producer output cannot reach host execution.
3. Protected timeout reconstruction accepts only exact C-locale TERM/KILL
   lines naming `'/bin/zsh'`.
4. V17's manifest, cleanup, Docker-state, closed-stage, FD, and shell-variable
   repairs remain intact.
5. Exact five-test and development-only theorem boundaries survived theory
   review.

### Failure mode

`AGGREGATE_TIMEOUT_STDERR_BYPASSES_FILTER`: the canonical bootstrap applies
`1>&3 3>&- 2>&1` to the aggregate `gtimeout` command. Redirections are
left-to-right, so stdout is first sent to saved descriptor 3 and stderr is
then duplicated to that same destination. The downstream diagnostic filter
receives EOF. Aggregate TERM cannot map host exit 78 or 80 to 178 or 180, and
TERM-then-KILL can escape as 137 rather than the claimed outer 124.

### Strongest valid statement

V18 closes V17's unverified-prefix execution and mismatched timeout-target
defects. It remains unauthorized because aggregate timeout diagnostics do not
reach their exact-line filter.

### Next concrete action

Create V19 with `2>&1 1>&3 3>&-` on the monitored aggregate command, then prove
in a synthetic non-repository harness that TERM plus child 78 maps to 178,
TERM plus child 80 maps to 180, TERM-then-KILL maps to 124, wrong targets map
to rejection 72, and ordinary host output bypasses the diagnostic filter.

### Artifact paths

- `experiments/EXP-SGCP-SECANT-REP-001/development-test-execution-protocol-v18.json`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-host-runner-v18.zsh`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-authorization-validator-v18.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-result-validator-v18.jq`
- `experiments/EXP-SGCP-SECANT-REP-001/development-test-review-v18.md`

No development-test or experiment-execution authority is granted.
