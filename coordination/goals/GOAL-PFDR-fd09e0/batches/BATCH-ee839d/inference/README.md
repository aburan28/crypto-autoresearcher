# Prospective native inference admission

The original unbound alias refusals are retained in admission-history.json.
They are not global runtime unavailability. No task was launched.

Executor may not use coordinator-orchestration-code: validate_inference rejects
that policy on a noncoordinator because may_change_official_state is true.
AGENTS core11 permits stronger requests but does not waive this explicit guard.
Instead the documented task-local overlay binds executor-implementation to the
same gpt-6.1-sol capabilities conservatively copied from its existing binding.
This preserves Executor authority and requests high prospectively on the card.

Reviewer uses existing openai/review-adversarial -> gpt-5.6-sol/xhigh. The
planned native call selects that exact model/effort with fork_turns:none.
Each Reviewer is independent of producer and sibling. This does not call the
OpenAI API, require its separate credential, or claim a new API model probe.
The actual native invocation/session identity is recorded only when dispatched.

The generic executor-resolution.json records the policy-default medium result;
TASK-20261026-589ad5-handoff-resolution.json is the authoritative actual-card
resolution and records high. Reviewer resolver inherited a historical probe
date from the committed binding; this session performed no catalog probe.

Use AUTORESEARCH_BINDINGS_OVERLAY pointed explicitly at the published
native-model-bindings.overlay.yaml for the Executor. Never install it as a
shared default. Publish its exact bytes/hash before implementation dispatch.
