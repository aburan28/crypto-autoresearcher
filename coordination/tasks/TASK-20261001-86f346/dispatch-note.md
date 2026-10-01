# Dispatch note — TASK-20261001-86f346 backend reroute (2026-10-01)

Recorded before dispatch, per the model-policy requirement that every
substitution is disclosed, and per the standing dispatch preconditions.

## What happened

- The configured model for the opencode runtime's `idea-generator` agent is
  `vllm/qwen3.8-27b` (project `opencode.json`), served by the L40S vLLM box on
  AWS behind `~/bin/vllm-lazy-proxy` (127.0.0.1:8787 -> vllm-alb -> instance).
- Three dispatch attempts (2026-10-01) failed identically before any agent ran:
  `GPU not ready: An error occurred (AuthFailure) when calling the
  DescribeInstances operation: AWS was not able to validate the provided
  access credentials`.
- Diagnosis: the ALB is unreachable (`curl .../health` -> HTTP 000), so the
  proxy takes its launch path, and this machine's AWS credentials are invalid
  (`aws sts get-caller-identity` -> `InvalidClientTokenId`). The proxy's
  `/v1/models` deliberately does not launch and returned a static list, which
  initially masked the outage.
- The `api_direct` runtime (`orchestration/agent/`) REFUSED the role outright:
  `REFUSED: this runtime cannot provide web_search` (idea-generator requires
  `web_search` per `orchestration/roles.yaml`; the refusal is by design and was
  not bypassed).
- These are infrastructure failures. They are not evidence about any
  hypothesis, and no research state changed because of them.

## User-approved reroute

- On 2026-10-01 the user was presented with the outage and three options
  (fix AWS credentials and retry; reroute; terminal stop) and selected:
  **reroute idea-generator to `zai/glm-5.2`**.
- `zai` backend, `research-deep` -> `glm-5.2` is an authorized binding in
  `orchestration/model-bindings.yaml` (provenance: operator-supplied,
  last_probed: null -> `model_verified: false` is carried into the receipt).
  `ZAI_API_KEY` is present per `orchestration.adapter doctor`. No Bedrock
  provider is selected; project config keeps `amazon-bedrock` disabled.
- This is a backend reroute within the same requested policy
  (`research-deep`), not a policy degradation: `fallback_allowed: false` and
  `degraded_allowed: false` on the card remain untouched, and no requirement
  of the policy is being accepted unmet.

## Mechanical state of the reroute

- The effective edit is in the dispatching session's project config:
  `/Volumes/SSD990/crypto-autoresearcher/opencode.json`,
  `agent.idea-generator.model: vllm/qwen3.8-27b -> zai/glm-5.2`.
  That checkout is on an unrelated dirty branch (`exec/aes-14352a-stage1`),
  so the edit is left UNCOMMITTED there and is to be REVERTED after the wave
  completes. It is not committed to that branch and must not be merged.
- The worktree copy of `opencode.json` on this branch is NOT edited; the
  branch carries this note instead, so the merged tree keeps the configured
  `vllm/qwen3.8-27b` routing.
- The resolved model identifier for the run is to be recorded in the
  archival receipt of TASK-20261001-cf1045 together with this note's id.

## Revert checklist (after the wave)

1. Restore `/Volumes/SSD990/crypto-autoresearcher/opencode.json`
   `agent.idea-generator.model` to `vllm/qwen3.8-27b`.
2. Confirm `git -C /Volumes/SSD990/crypto-autoresearcher diff -- opencode.json`
   is empty.
3. Record the revert in the wave's final report.
