# Token efficiency

The harness optimizes for evidence-producing work per token, not for minimizing
reasoning or weakening review. Token controls must preserve the immutable audit
trail, role authority, evidence scope, and independent review requirements in
`AGENTS.md`.

## What is implemented

### Provider-side prompt caching in `api_direct`

`ResolvedChatModel` applies explicit prompt-cache controls only for first-party
`anthropic` and `openai` backends. OpenAI-compatible and Anthropic-compatible
gateways are deliberately not treated as cache-capable solely because they
share a wire protocol; a backend must be explicitly added once its cache
contract is verified.

The stable cache identity is content-addressed over the model, system prompt,
tool declarations, and cache namespace. Task-specific message history is not
part of the key. This prevents unrelated task suffixes from invalidating a
stable role/tool prefix while still changing the key whenever the actual
shared prefix changes.

### Usage accounting

Receipts retain provider cache counters when they are reported. Missing
counters remain absent rather than being inferred from totals.

Cache-read efficiency follows each provider's accounting semantics:

- Anthropic reports uncached input, cache reads, and cache creation separately,
  so the denominator is their sum.
- OpenAI reports total input with cache reads as a detail counter, so the
  denominator is total input directly.

Do not compare cache percentages across providers without preserving these
semantics.

## Next optimization: bounded working context

The complete transcript is an audit artifact; it does not need to be identical
to the model-visible working set on every turn. A future context compactor should
maintain two representations:

1. the complete immutable transcript/tool journal;
2. a bounded working context containing the applicable policy, task envelope,
   unresolved questions, relevant evidence excerpts, and recent complete tool
   exchanges.

Older tool output should be replaced in the working context only by a durable
artifact reference plus a faithful excerpt and integrity metadata. Research
claims, assumptions, contradictory evidence, source IDs, and unresolved
uncertainty must never be dropped merely to save tokens.

Before enabling compaction by default, add replay tests proving that:

- recent tool-call/result pairs remain structurally valid;
- required role and evidence rules remain present;
- referenced artifacts can be re-read exactly;
- a compacted run and an uncompacted control reach equivalent task-state
  transitions on deterministic fixtures;
- compaction changes no immutable run record.

## Metrics to track

Per role, backend, model policy, and task class, record:

- requests;
- input tokens;
- output tokens;
- cache-read tokens when reported;
- cache-write/creation tokens when reported;
- cache-read efficiency using provider-correct accounting;
- task completion/stop reason;
- files written and denied tool calls;
- validated evidence or review outcome where applicable.

Optimization decisions should use token cost per validated task outcome rather
than raw token volume or cache-hit rate alone.
