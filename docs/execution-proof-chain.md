# Execution proofs in the research proof chain

**Required integration design, 2026-10-16. Implementation open.** The owner
requires prescribed-computation proofs to be integral to the proof chain,
not an optional attachment to run records. This document makes that an
acceptance condition for the Cairn integration. It does not claim the current
runner, evidence validator or settlement bridge already verifies such proofs.
It changes no experiment approval, historical run, scientific status or payout.

The protocol-side contract is
[Cairn's execution-proof design](https://github.com/aburan28/cairn/blob/main/docs/design/execution-proof-chain.md).
This document owns the research-side bindings and promotion gates. Wire schemas
must be frozen together during implementation; the illustrative fields below
are requirements, not fields supported by today's schemas.

## Required dependency graph

```text
EXP specification + approved, complete trial plan
                    |
                    v
reviewed guest executable + committed inputs + prescribed seed derivation
                    |
                    v
RUN execution proof + complete workload coverage + raw-output commitment
                    |
                    v
independent arithmetic / certificate / metric / control checks
                    |
                    +--> EV -> independent scientific review -> Coordinator DEC
                    |
                    +--> Cairn claim -> verified settlement -> offline audit
                                    |
                                    v
                       additive external_verification receipt
```

The same result commitment must survive every edge. Evidence cannot cite a
proved summary while its substantive measurements come from different,
unproved raw bytes. A settlement receipt is evidence about a settled claim;
it does not promote a hypothesis. A mathematical theorem's kernel proof and
its assumptions remain separate obligations from computation integrity.

Existing cheap certificates remain appropriate for claims such as `[k]P = Q`.
Such a certificate verifies that solution, not the search procedure, operation
count, distribution or claimed absence of solutions. Use the execution chain
when the claim depends on those properties. Do not relabel an endpoint check,
replay, signed process receipt or hardware attestation as an execution proof.

## What is bound before execution

The approved protocol and frozen plan declare whether the experiment requires
prescribed execution and the exact scope that must be proved. For covered
work, the requirement belongs upstream in the protocol and Cairn objective;
an executor cannot remove it by omitting a manifest field.

Required statement components:

- Protocol/specification digest, trial-plan digest, EXP/RUN/trial identifiers,
  and the declared hypothesis/claim scope.
- Reviewed guest source/dependency closure, compiled image identity and a
  reproducible build recipe. Pin compiler and dependency versions. A commit
  or a source hash alone is not the executable identity.
- Complete input commitment, curve/field identity and parameters, preprocessing,
  paired baseline/candidate identity, and the versioned operation-cost model.
- Prescribed seed derivation, all required sample/trial indices, controls,
  stopping rules, and the required completion condition.
- Proof-system release, receipt mode, verification parameters and explicit
  security/trust assumptions.

There must be no hash cycle: the plan does not contain its own digest, and a
result commitment excludes the proof generated about it. Compute source and
input commitments over exact, defined bytes. Use separate domains for plan,
input, result and semantic work identity.

For fresh challenges, commit the implementation and plan before a specified
future beacon round and derive seeds deterministically from that round and
trial indices. Prevent a contributor from selecting favorable replacement
draws. The historical fixed-seed experiments keep their original scope. If
operator honesty is excluded, a backdated local timestamp cannot establish
pre-registration: require a previously witnessed checkpoint or external anchor.
Missing required randomness leaves the proof incomplete, not silently weaker.

## What the proof must establish

The guest computes or constrains the arithmetic that creates the observations.
Host hints, external solver outputs and GPU returns are untrusted unless their
relationship is verified within the proved computation. Proving that a JSON
summary was computed from arbitrary input proves only that postprocessing.

Public outputs bind the expected task and program to exact raw-result bytes
or their digest, canonical integer/boolean metrics, completion status and the
required trial coverage. Byte commitments can cover an archived file with
decimal data, but consensus metrics must have explicitly deterministic
semantics; merely rounding host-dependent arithmetic to an integer is not a
determinism proof.

For chunks, prove each state transition and aggregate all required chunks in
order. Include failed controls, misses, capped trials and zero-hit cells.
Retain interruptions as operational observations; do not invent proof of
completion for a run that stopped. Proving completion of an exact finite
search is compatible with a scoped negative result; it establishes no general
hardness or absence outside that domain.

An operation count is proved only if the guest enforces the declared count
semantics. VM cycles are not native CPU/GPU cycles. Proving an arithmetic
result does not prove the runtime, energy, memory usage or count of a different
optimized implementation. Those retain their own measurement and review
requirements under [progress fidelity](progress-fidelity.md).

## Enforcement points and implementation work

The existing implementation provides useful seams, but none is an execution
proof verifier today. Each row is required work, not an assertion of coverage.

| Boundary | Current seam | Required implementation |
| --- | --- | --- |
| Protocol to plan | Frozen `specification.yaml`, `trial-plan.json`, handoff hashes | Inherit the execution-proof requirement and full trial/control coverage; reject a weaker plan |
| Plan to run | `tools/experiment_execution.py` | Dispatch the approved proof-producing workload; capture proof, journal and result artifacts; reverify on completion and reconciliation |
| Existing harness paths | `harness/runner.py`, native/legacy experiment drivers | Audit and route every covered path; an alternate launcher must not bypass the requirement |
| Run to objective | `tools/exp_to_objective.py` | Render an execution objective from the frozen policy; refuse certificate/replay downgrade; preserve identities and scope |
| Local verification | `tools/cairn_bridge.py` | Verify the real receipt against the expected statement; absence is explicit and cannot be called execution verified |
| Claim to settlement | Cairn primary and reference verifiers | Require valid proof and complete binding during admission/settlement and imported-log audit |
| Settlement to receipt | `tools/cairn_settlement_receipt.py` | Bind the archived run/result/proof to the actual settled claim; independent audit/checkpoint evidence must distinguish verification from node-reported JSON |
| Run to evidence | Run/evidence schemas and `tools/validate_ledger.py` | Derive requirements from protocol and referenced runs; reverify bindings rather than trusting a recorded boolean; refuse promotion with missing/mismatched proof |
| Evidence to claim/DEC | `tools/progress_fidelity`, review and archival paths | Carry proof scope and independent validity checks; scientific interpretation and Coordinator authority remain mandatory |

Persist an additive `execution-proof` record alongside a new run: task/policy
commitment, image identity, backend/profile, journal/result commitment,
coverage, receipt artifact and its digest, and verification provenance. These
are conceptual requirements; freezing the concrete schema is milestone 1.
The record must be included in declared artifacts, archive coverage and
immutability checks. A historical landed run is never rewritten to add a
proof, and a later proof must describe its actual relationship to that run.

Record three independent facts: execution validity, metric/control validity,
and inferential validity. A correctly executed failed A/A gate does not
release its dependent inference. An unproved observation can be retained with
its limits, but cannot be promoted as execution verified or satisfy an
objective that requires the proof. No missing verifier or resource failure
is negative mathematical evidence.

## Backend and release sequence

Start with RISC Zero STARK receipts on bounded deterministic arithmetic. The
research baseline is `v3.0.6`; pin and recheck the complete guest/verifier
closure at implementation time. Record its actual security assumptions and
parameters, including the documented approximate 96-bit target. Do not claim
128-bit, end-to-end post-quantum or confidential execution by implication.
Compare patched SP1 on identical work only if needed; its native-verifier
fix in `v6.8.1` is a minimum advisory constraint, not a general security audit.
See the protocol-side design for primary references and proof-mode details.

| Milestone | Required deliverable | Completion evidence |
| --- | --- | --- |
| 1 | Shared versioned statement, journal, run/evidence record and downgrade rules | Cross-language conformance and substitution tests; no commitment cycles |
| 2 | Real small `ecc2k-23` prescribed-walk guest plus a complete seeded count batch | Real non-development proofs, independent arithmetic agreement; an endpoint-valid alternative walk fails |
| 3 | Cairn primary/reference verification and bounded proof availability | Same settled log independently audited offline; existing frozen IDs unchanged |
| 4 | All research execution, reconciliation, evidence, progress-fidelity and archive consumers wired | Removing/replacing a proof, result, task or required trial blocks covered promotion and settlement |
| 5 | Cost/adversarial report and shadow verification | Native/proving/verification/storage costs separate; duplicate proof encodings cannot duplicate rewards; failed attempts retained |
| 6 | Enforced newly funded execution objectives | Reviewed exact release passes all links; historical objective and record semantics preserved |

Every milestone is open. No shadow result may silently satisfy a mandatory
proof gate. A schema, mock proof, signature or hash check cannot close one.
Benchmark geometric workload sizes and freeze resource/correctness targets
before measuring. The pilot supplies engineering evidence only at its actual
parameters; it does not assert production-scale proving economics.

The first implementation handoff must name all paths in the table and include
these adversarial controls: fake/dev receipt under a dev-enabled environment;
wrong program, protocol, inputs, seed or result; invented count; missing,
duplicated or reordered trial/chunk; omitted failed control; unresolved
assumption; old proof replayed under a new task; different proof encoding for
one paid unit; missing blob; unsupported backend; verifier crash/timeout; and
correct execution with failed scientific controls.

Use the existing Executor/Validator/Reviewer/Coordinator contracts for the
handoff, archive and independent review. Passing cryptographic verification
does not remove any scientific responsibility or authorize a state transition.

## Related contracts and open work

- [Cairn integration plan](cairn-integration-plan.md) includes this as a required
  cross-cutting workstream, not a later optional verifier experiment.
- [Evidence and reproducibility](evidence-and-reproducibility.md) preserves the
  distinction between execution, controls and interpretation.
- [Claim verification](claims-and-verification.md) defines existing certificate
  scope; [subversion resistance](subversion-resistance-20261010.md) names the
  fabricated-measurement threat this implementation must address.
- [Tracked implementation obstruction](../problems/execution-proof-chain-not-enforced.md)
  stays open until the end-to-end release gates pass.
