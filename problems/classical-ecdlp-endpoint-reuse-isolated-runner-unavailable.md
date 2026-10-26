# Endpoint reuse has no source-bound isolated execution route

- **Status:** `open`
- **Kind:** access/tool limit; implementation/deployment gap
- **Affected work:** [EXP-ECDLP-2b4ff1](../experiments/EXP-ECDLP-2b4ff1/specification.yaml), [GOAL-ECDLP-e70832](../ledger/goals/GOAL-ECDLP-e70832/goal.yaml), [TASK-20261026-76aa84](../ledger/handoffs/TASK-20261026-76aa84.yaml)
- **Next action owner:** Coordinator, TASK-20261026-76aa84
- **Last updated:** 2026-10-26

## Problem

We cannot yet dispatch the new source-pinned classical endpoint-reuse measurement because this session has no demonstrated generic isolated runner that executes the new code and returns verifiable host and artifact receipts.

The planned study has 64 fresh ordinary, non-anomalous prime-field curves with j distinct from 0 and 1728, 16 each at 12/14/16/18 subgroup bits. Two independent target/setup replicates and 64 targets per cell give 8,192 public target IDs, tested by six complete solver arms. The method retains failed Bernstein–Lange endpoints only after a scalar passes its public point equation, under one fixed known-plus-pending endpoint arena. The original acceptance criterion remains complete source/input-bound execution, all outcomes and independent public witness/trace checks, followed by the registered full setup-plus-solve counter comparison. A draft or a problem record does not satisfy it.

## Evidence and uncertainty

- **Observed:** [capacity observations](../harness/classical_ecdlp_endpoint_reuse/execution/evidence/observations.json) at crypto source commit `ac14190f1ab825f0ab1760a093c43bdac8be5e61` report no generic isolab/taskq/spotlab tool exposed in this session and no configured AWS outbound identity. Normal `aws`, `kubectl` and `boto3` entry points were absent. This is session evidence, not a statement that the owner has no such capacity elsewhere.
- **Observed:** the [main Actions bridge](../harness/classical_ecdlp_endpoint_reuse/execution/evidence/main-workflow.yml) accepts a main-branch ecbench specification and uses a fixed deployed image. [HARNESS.md](../harness/classical_ecdlp_endpoint_reuse/execution/evidence/HARNESS.md) says caller `source_revision` is provenance; it does not cause arbitrary new candidate source or shell code to execute.
- **Observed:** the feature bridge at `fae82d3325e05d0a608b4ea47712cd38cec90c10` is not on the inspected main. [Run 40118925100 job data](../harness/classical_ecdlp_endpoint_reuse/execution/evidence/run-40118925100-jobs.json) shows contracts succeeded while build and experiment jobs were skipped. That run is not evidence of a successful custom-image measurement.
- **Observed:** the ordinary GitHub Actions variables read returned HTTP 403, `Resource not accessible by integration`; configuration values were not obtained. The denied read was neither retried nor bypassed.
- **Derived or proved:** a fixed-image specification runner cannot supply a measurement of this new source merely because the request names its commit. A generic node label or CPU request alone does not establish observed L2/tier-B isolation.
- **Suspected explanation:** the remaining gap is connection/deployment access or an undeployed generic worker. Which authorized path is available is not yet established.
- **Missing capability:** a working authorized generic isolated submission route, a real code-only worker image/binary identity, normal authorized public-input/output transport and readback, and observed execution/isolation receipts. Source and protocol fields that depend on those observations remain unbound.
- **What this evidence does not establish:** no scientific batch was attempted; there are no endpoint-reuse measurements, speedups or algorithm failures. It does not refute endpoint reuse, establish runtime isolation, prove the absence of all remote resources, or justify changing the scientific sample or success criterion.

## What would unblock it

- [ ] Identify an authorized exposed generic isolab connection or normal AWS/Kubernetes submission identity; a non-scientific readiness check must establish the actual supported request/worker contract.
- [ ] Build and publish the code-only worker image from an exact source commit, record its actual OCI digest and native binary SHA-256, and verify the measured worker reports those identities. Protocol/public-input data are supplied later by hash, avoiding an image/protocol/input hash cycle.
- [ ] Demonstrate authorized durable public-input transport and output retrieval with actual length/SHA-256 readback; retain all raw streams, the unified export and failures under the repository's canonical artifact policy.
- [ ] Record actual isolated allocation/host facts and per-child isolation blockers. A timed secondary comparison remains invalid without observed L2/tier-B or better; choosing counted metrics does not waive the isolated-placement rule in `docs/experiment-protocol.md` section 4.
- [ ] Complete the source/runtime/preflight bindings and honest inference provenance, freeze and publish the protocol before affected draws, then obtain genuine exact-byte preapproval, committed Coordinator approval, ordinary selector readiness and a real published executor claim. Warnings about unconfigured external API backends do not establish failure of the current interactive Codex session.

These conditions are necessary for this planned measurement route, not proof of a gain. Public witness checks, full counter/memory accounting, the A/A control, complete sampling and later independent scientific interpretation remain obligations.

## Next discriminating step

- **Action or proof obligation:** TASK-20261026-76aa84 binds one source-capable isolated worker and demonstrates its non-scientific readiness and artifact readback with the actual image/identity; it does not launch this study.
- **Inputs and controls:** the pinned workflow/HARNESS/job evidence above, the prospective source/protocol package, and a readiness control that distinguishes the deployed fixed image from the new candidate worker. Keep API authorization failures distinct from backend process failures.
- **Execution limits and stop condition:** read/configuration checks and a fixed software readiness control only. No scientific target draw or solver cohort, no credential substitution, no changed infrastructure permissions and no campaign spending cap. Stop on a concrete unsupported/unauthorized route and retain its exact result.
- **Outcomes and next actions:** demonstrated source-bound execution and readback allow final admission work; a fixed-image-only or denied route keeps this task impeded and motivates another already-authorized route; ambiguous metadata requires a more discriminating readiness receipt. None of these outcomes changes a mathematical hypothesis.
- **Recheck trigger:** an authorized generic runner/identity becomes available, the owner identifies its existing endpoint, a real image build is available, or the connector/runtime capability set changes.

## Resolution and history

Unresolved. On 2026-10-26 the exact capacity observations and source hashes were retained while implementation, independent public verification and prospective design continued. No source-isolation certificate, experiment approval, run, archive completion or scientific verdict is manufactured by this record. Future updates append actual evidence and preserve this original acceptance criterion.
