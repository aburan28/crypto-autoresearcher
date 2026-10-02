# Resume instructions — TASK-20261001-86f346 PFDR ideation wave

State as of 2026-10-01, after five failed dispatch attempts from one opencode
session (all `GPU not ready: AuthFailure DescribeInstances` — infrastructure
failures, not evidence, no research state changed).

## What is already done and durable

- Branch `ideas/pfdr-ic-20261001` (pushed; base merged to origin/main
  5599b0ce65, then packet commits f3fa2e06d9, dfc8112acf, plus the bus-record
  sync commit).
- Dispatch packet committed:
  - `ledger/handoffs/TASK-20261001-86f346.yaml` — the ideation card (to:
    idea-generator, policy research-deep, four assigned idea ids, completion
    gate, dispatch_preconditions all satisfied).
  - `ledger/handoffs/TASK-20261001-cf1045.yaml` — the snapshot-archive card
    (to: coordinator, written_not_dispatched, blocked_on the producer).
  - `coordination/tasks/TASK-20261001-86f346/context/` — rendered frontier
    maps (index-calculus + generic-rho, rendered at 0945f107be, verified
    unchanged at 5599b0ce65) and the dedup/lane-state list.
  - `coordination/tasks/TASK-20261001-86f346/dispatch-note.md` — the backend
    outage diagnosis, the user-approved zai/glm-5.2 reroute, and the revert
    checklist.
- Assigned, allocation-checked idea ids (free as of minting; re-run
  `python3 tools/allocate_id.py --check <ID>` before writing if time passed):
  IDEA-20261001-c41c07, IDEA-20261001-f484bd, IDEA-20261001-6a8720,
  IDEA-20261001-2d18c7.
- Bus notice MSG-20261001-f19772 published (vllm outage + temporary reroute).

## The blocker

- opencode project config pins `idea-generator` to `vllm/qwen3.8-27b`
  (L40S box behind `~/bin/vllm-lazy-proxy` -> ALB). The instance is down
  (ALB /health unreachable) and the proxy cannot relaunch it: this machine's
  AWS credentials are invalid (`aws sts get-caller-identity` ->
  `InvalidClientTokenId`).
- The user approved rerouting idea-generator to `zai/glm-5.2`; the edit is in
  the MAIN checkout's `opencode.json` (uncommitted, on the dirty
  exec/aes-14352a-stage1 tree — do not commit or merge it there).
- opencode resolves subagent models at session start: the running session
  kept dispatching to vllm despite the edit (verified twice). A NEW session
  picks the edit up.
- The `api_direct` runtime refuses the role by design
  (`REFUSED: this runtime cannot provide web_search`); do not bypass.

## To resume (either route)

Route A — fix AWS, stay on the configured model:
1. Refresh AWS credentials until `aws sts get-caller-identity` succeeds
   (proxy uses /opt/homebrew/bin/aws, region us-west-2). If credentials come
   from env vars, restart `~/bin/vllm-lazy-proxy` (it inherits its launch
   env); file-based creds need no restart.
2. Revert the main checkout's `opencode.json` idea-generator model to
   `vllm/qwen3.8-27b` (the reroute is then moot).
3. In any session: dispatch the idea-generator against the card, then run
   the completion flow below.

Route B — restart opencode, use the approved reroute:
1. Restart opencode in /Volumes/SSD990/crypto-autoresearcher with the same
   explicit session model as before (project primary is vllm and dead; the
   session model must be passed explicitly, as the previous session did).
2. Invoke /propose-ideas (or dispatch directly): the idea-generator agent
   now resolves zai/glm-5.2 (authorized research-deep binding,
   model_verified false until probed).
3. Dispatch against the committed card, then run the completion flow below.

## Completion flow (once a generator session exists)

1. Dispatch idea-generator with the card
   `ledger/handoffs/TASK-20261001-86f346.yaml` and the worktree discipline:
   all writes under the `ideas/pfdr-ic-20261001` worktree
   (/Volumes/SSD990/llm/tmp/opencode/wt-ideas-pfdr-20261001), never the main
   checkout. Deliverables: the four proposal files at their exact paths.
2. On return, verify the completion gate: strict parse, assigned ids, bound
   to RQ-PFDR-ae2fba, status proposed, full schema including prior_art,
   heuristic_assumptions with validation routes, target_complexity exponents
   vs rho, dominated_by + sota_delta, null controls. Incomplete ideas go BACK
   to the generator; nobody repairs them by hand.
3. Novelty check: `python3 tools/build_frontier_map.py --match "<claim +
   mechanism>"` per idea; send back any idea whose top hit is a row it did
   not cite.
4. `python3 tools/validate_ledger.py` — only the pre-existing
   DEC-20260930-{8af20f,ca32c7}/EXP-AUXIN-339fb0 errors may remain.
5. Execute TASK-20261001-cf1045 (snapshot archive): merge origin/main (never
   rebase), commit exactly the declared paths in one isolated commit, record
   the post-commit receipt with path_sha256 and the resolved model id of the
   generator run, push.
6. `gh pr create --base main --head ideas/pfdr-ic-20261001 --title "ideas:
   PFDR prime-field decomposition ideation wave" --body "RQ-PFDR-ae2fba;
   IDEA-20261001-c41c07, -f484bd, -6a8720, -2d18c7; TASK-20261001-86f346;
   TASK-20261001-cf1045"` (or `gh pr edit` if one exists).
7. Revert the main checkout's `opencode.json` reroute per the dispatch-note
   checklist and record the revert in the report.
