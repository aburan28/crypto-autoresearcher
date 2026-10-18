# Lean theorem and workflow evidence review

[Independent synthesis](synthesis.md) · [Per-claim outcomes](claim-verdicts.json) · [Report PDF](report.pdf)

This technical packet adapts `review-evidence` to Lean theorems and Lean-related
skills, with separate kernel, claim-fidelity and review-outcome records. It does
not change official scientific status or certify all historical research.

The independent mathematical reviews support the 19 explicitly scoped new
claims: five transport statements in `crypto`, four rho-collision statements in
`cryptanalysis`, and ten certificate/NCP statements in `crypto-autoresearcher`.
All 19 source bodies still match their reviewed hashes. The broader historical
claims and concrete implementation/model bridges remain open.

The 65 available targets among 66 frozen autoresearcher specifications were
freshly checked and retain their actual verifier revision `2951f9b...`. That
count overlaps the 19 new declarations. It is not 84 independent results, and
kernel checks do not establish claim fidelity for every historical target.

## Review record

- [Initial precommitted plan](review-plan.yaml), [source bindings](inputs.json)
  and [workflow bindings](workflow-inputs.json).
- [Transport/rho fidelity](reports/TASK-20261018-63a7cc/report.md) and
  [certificate/NCP fidelity](reports/TASK-20261018-a5dcec/report.md).
- [Blind statement-only mathematical controls](reports/TASK-20261018-29a8c7/report.md)
  and [versioned attestation correction](reports/TASK-20261018-29a8c7/review_attestation-v2.yaml).
- [Initial workflow failures](reports/TASK-20261018-dae80c/report.md),
  [first repair review](reports/TASK-20261018-695548/report.md), and
  [reduced second-repair findings](reports/TASK-20261018-1cab3a/publication-summary.md).
- [Independent closure:44 checks pass within the exercised contract](reports/TASK-20261018-2ea34a/publication/report.md), with [reviewer attestation](reports/TASK-20261018-2ea34a/publication/review_attestation.yaml) and [compact PDF](reports/TASK-20261018-2ea34a/publication/report.pdf).
- [Closure controls committed before dispatch](closure-repair-plan.yaml) and
  [scoped public input bindings](closure-repair-inputs.json).
- [Current proof identity](machine/final-proof-identity.json),
  [229 passing formal tests](machine/final-consistency-tests.log), and
  [11 gate controls](machine/gate-aux-selftest.log).

The full second-repair report and full closure control bundle are retained
unchanged in local committed archives. Automatic approval review blocked disclosure of its extensive
internal inventory and absolute paths; the published summary is explicitly
root-authored and identifies the original hashes. It is not a substitute for a
published independent attestation. The closure reviewer directly tested the corrected published candidate and
authored the compact publication of those same44 checks. It discloses a prior
workflow-attestation excerpt read outside the named allowlist, all trust limits,
and the unavailable public raw reproduction. No controls were rerun for the
compact publication. All 57 scoped closure inputs were independently
retrieved without credentials from already-public immutable GitHub URLs and
matched their declared hashes before the scoped manifest was published.

## Reproduction and boundaries

Use the exact revisions and commands in the independent reports, with fresh
output paths. The verifier binds ordinary and hidden local proof/configuration
inputs before and after execution; the summary requires exact task/theorem
identity and consistent nonempty audit evidence. For archived receipts select
`--verifier-revision 2951f9b77d96606820be80bf61ee0d539cfbb4dd` explicitly.
A hash/log check does not authenticate execution. Fresh Lean checks and semantic
review are still required, and dependency binaries retain Lean/Lake's trust
boundary. Use isolated immutable source trees; pre/post hashes do not detect a
transient edit that is restored.

The gate compiles unregistered auxiliary modules without editing frozen study
Lakefiles. The failed historical-configuration migration is retained in the
producer history, and all ten configurations were restored. A stale consumer
auditor/fixture bundle and standalone toolchain-directory handling were also
corrected; their earlier failures remain evidence.

The canonical unresolved coverage record is
[lean-retrospective-historical-coverage](https://github.com/aburan28/crypto-autoresearcher/blob/codex/lean-retrospective-20261018/problems/lean-retrospective-historical-coverage.md).
It includes the missing `ncp-reachability` proof, concrete geometry/duality,
C refinement, arbitrary-point action, parser integration and broader kernel
presentation obligations. No performance or security conclusion follows from
these workflow checks.

The original producer PDFs predate independent review. The synthesis and current report PDF are linked above. Current-head GitHub CI
remains queued/pending/running in the [recorded snapshot](machine/ci-current-code-heads.json); these are local and independent review results, not an assertion of green CI or merge readiness.
