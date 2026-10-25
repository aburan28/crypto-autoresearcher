# Prospective zero-run Coordinator packet

Prepared by native managed collaboration session
`/root/coordinate_portfolio_20261025`, following the user's explicit `/coordinate`
invocation. This is a scratch preview, not a published task, experiment approval,
scientific decision, opened lane, archive receipt, or run authorization.

IDs were minted with `tools/allocate_id.py`; root reports all four verified free
and well-formed: BATCH-3cfef2, TASK-20261025-b7e32e (design),
TASK-20261025-f950af (snapshot archive), DEC-20261025-fe4f22 (scope decision).

## Recommended next coordinated act

Publish a bounded zero-run joint-system applicability/design lane, after the
current ownership, native policy binding, and source-publication checks. Its
deliverable is the exact next experiment contract and implementation obligations,
not a new numerical bound. The target is the existing IDEA-20260904-39336c and
LEAD-ICP-coppersmith-smallroot-semaev; no new goal or scientific status is needed.

The first decision-changing uncertainty is whether the pinned external
optimal-shift construction accepts the actual weighted joint system, and what
precise coefficient, monomial-domain, preprocessing and extraction assumptions
must be frozen before its first joint call. A documented univariate calibration
already exists. Repeating it or preparing another generic literature summary is
not the task. In particular, the task must bind an initial nontrivial joint
workload and its controls prospectively, while leaving execution to `/run` after
the separate experiment approval and readiness gates.

## Operational corrections

1. WORKFLOW.md section 1 explicitly allows an authenticated native Codex or
   Claude Code session when the only API-direct failure is credential/model
   configuration. It permits a documented runtime probe **or login-status
   check**, with actual model provenance recorded. This native collaboration
   session is operating. The failed nested CLI initialization does not prove
   every native runtime unavailable. No API catalog verification or exact CLI
   SQLite receipt was obtained for this session, and none is asserted.
2. An open lane record is not a live task claim. At the read-only check,
   TASK-20261017-2755a2 and TASK-20261022-32fe8b had completed releases. Two open
   lanes did not demonstrate that two live workers occupied the goal's resource
   capacity. Existing lanes remain owned and are not ours to close. Root reports
   the named sibling branch no longer exists; use the claim feed and preserved
   artifacts, not that stale branch name, to assess any overlap.
3. The earlier `--no-deepen` health result carried a shallow-clone warning.
   Root has now deepened history and independently found the declared queue in
   commit 8941259ce5121f5e3d0acac036cb7fbf80b6fd25. Do not carry forward the
   shallow-history absence observation as proved queue corruption.
4. The real publication gate is shared-code ownership. The artifact checker
   copy in PR 2547 differs from crypto's canonical main source and the pinned
   digest. docs/lab-contract.md section 7 requires owner-first implementation,
   byte-identical mirrors and consistent locks. Root is preparing the narrow
   infrastructure fix in crypto; do not weaken parity or update a mirror lock
   alone. This is not a scientific experiment or mathematical observation.

## Before publication and dispatch

- Resolve and record the actual native Coordinator model and effort under
  `coordinator-orchestration-code` (high). A supported explicit native binding
  may be chosen and recorded; the default unverified Anthropic catalog entry
  must not be relabeled verified. Do not fabricate CLI receipt fields. If this
  host cannot expose the requested/actual provenance required by the policy,
  record that precise gap and do not approve a scientific contract.
- Finish the owner-first artifact fix and parity synchronization before merging
  PR 2547. A pending owner PR is not an owner-first change that has landed.
- Refresh the full-history goal health and current claims across available refs.
  Register the new disjoint lane through `goal_lanes.py open-lane`; do not edit,
  release, close, or reuse either older lane. Existing open records alone are
  not a capacity refusal. The new queue permits one zero-run task at a time.
- On `lane/smallroot-3cfef2`, based on current merged main/audit inputs,
  publish the prospective handoffs, queue, and bounded scope decision under
  the repository paths given in `publication-map.json`. Read and apply the
  parent repository's normal schema and merge gates. The decision authorizes
  only zero-run design; it approves no hypothesis, launcher, runbook or trial.
- Run `research_dispatch.py <queue> --claims refs --ready-only`. Only after
  inputs are committed and pushed, the lane is registered, the task is ready
  and unclaimed, and its actual native role binding is recorded, claim
  TASK-20261025-b7e32e with a bounded lease and `--publish`. Then dispatch the
  Coordinator role in a fresh native session with the exact envelope.
- The root control plane performs helper commands, PDF rendering and the
  isolated archive. The Coordinator authors the design, does not run trials,
  and does not use its exposed command tool to execute programs.
- Release the claim with its actual outcome; archive only declared paths
  through TASK-20261025-f950af, verify the exact path/hash receipt and publish
  the lane PR. Keep any later scientific specification `review_required`
  until its exact prospective packet reports `approvable: true` and its
  published approved selector state is `ready`. `/coordinate` then names
  the `/run` handoff and stops before execution.

## Exact control-plane commands after applying the map

The source records and lane must be published first; these commands are not
asserted to have been run by this scratch preparation.

```bash
python3 tools/goal_lanes.py open-lane GOAL-PFDR-fd09e0 BATCH-3cfef2 \
  --queue coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-3cfef2/dispatch_queue.json \
  --decision DEC-20261025-fe4f22 \
  --objective 'Weighted joint-system applicability and prospective design; zero runs' \
  --as coordinator-smallroot-3cfef2 --publish
python3 tools/research_dispatch.py \
  coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-3cfef2/dispatch_queue.json \
  --claims refs --ready-only
python3 tools/goal_lanes.py claim \
  coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-3cfef2/dispatch_queue.json \
  TASK-20261025-b7e32e --as coordinator-smallroot-3cfef2 \
  --ttl-minutes 120 --publish
```

The lease is an ownership timeout, not a campaign budget. Re-render and preserve
any refusal rather than forcing a claim. Publication must use a new lane branch
and PR, not rewrite the existing owner branches or immutable archive inputs.

## Source and command record

Read locally: AGENTS.md, agents/coordinator.md, coordinate and design-experiment
skills, docs/agent-contract-extended.md observation rule,
docs/concurrent-goal-lanes.md, docs/task-lifecycle.md,
docs/dynamic-subagent-dispatch.md, docs/isolated-task-recovery.md,
WORKFLOW.md and references/lifecycle.md, docs/inference-backends.md native-session
section, the PFDR goal head, the small-root lead, and generated Codex Coordinator
binding. Read through GitHub at ab0609ebee: docs/lab-contract.md,
docs/shared-code.lock.json, tools/check_lab_parity.py, templates/research-records.md,
and the existing BATCH-8d6d84 queue. Read canonical crypto:main artifacts.py/test
and the audit copy at 067db015e7d61ebc1d72eab831e7be22f736be44.

Read-only helper commands: goal_lanes lanes/claims; targeted
goal_portfolio_health --no-deepen --json; ECC classification and PFDR open-idea
list; check_runtime_bindings --list; adapter resolve --backend openai-gpt61;
allocate_id mint commands above. Root supplies post-deepen health, merges,
schema checks, ID verification, current claims, owner-source repair and publication.
No scientific program, experiment implementation, git mutation, lane mutation,
approval, external message, or official record was produced by this preparation.
