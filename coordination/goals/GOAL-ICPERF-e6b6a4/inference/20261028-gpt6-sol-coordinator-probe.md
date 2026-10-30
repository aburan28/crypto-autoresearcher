# GPT-6 Sol Coordinator runtime admission, 2026-10-28 UTC

This is an infrastructure diagnostic for `GOAL-ICPERF-e6b6a4`, not an experiment or a research-state decision. The immutable machine receipt is [`20261028-gpt6-sol-coordinator-probe.json`](20261028-gpt6-sol-coordinator-probe.json).

## Exact attempt

- Requested policy: `coordinator-orchestration-code`, effort `high`, model `gpt-6-sol`, backend `openai-gpt6`, runtime `codex_cli`, independent session.
- `python3 tools/check_runtime_bindings.py` passed with 12 role bindings consistent.
- `codex login status` reported `Logged in using ChatGPT`.
- `python3 -m orchestration.adapter doctor --backend openai-gpt6 --probe` reported `$OPENAI_API_KEY` unset and the two Coordinator policy model IDs unverified.
- The repository's `probe-codex-session` command used `/opt/homebrew/bin/codex`, `/Volumes/SSD990-2/.codex/state_5.sqlite`, this checkout, a read-only sandbox, and the fixed public `PROBE_OK` prompt. It exited with `launch_nonzero_exit`; no new session ID was recorded and `runtime_resolution_verified` is false. The exact arguments and output digests are in the JSON receipt. The failed receipt must not be reused as a serving attestation.
- A second direct invocation of the same public probe command exposed the CLI's terminal error: `exceeded retry limit, last status: 429 Too Many Requests`. That invocation did not create a verified Coordinator session. An unrelated MCP memory service also emitted an authentication warning; the 429 is the Codex turn's reported terminal error.

## Consequence and next check

The GPT-6 Sol binding exists, but neither the configured API route nor this exact CLI session is verified for a Coordinator act. Retry a **new, separately named** `probe-codex-session` receipt when the serving limit changes, or provision the API credential outside chat and run `doctor --backend openai-gpt6 --probe`. Only a passing route may carry a Coordinator decision or handoff. This diagnostic says nothing about index-calculus performance, factor-base quality, or the hypotheses.
