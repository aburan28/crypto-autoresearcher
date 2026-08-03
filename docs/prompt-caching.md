# Prompt caching and context reuse

The adapter now exposes provider-neutral cache controls in
`orchestration.adapter.prompt_cache`. The goal is to make the expensive prefix
of every agent request stable while keeping task-specific material at the end.

## Recommended prefix order

1. global research policy and role contract;
2. deterministic tool declarations;
3. project conventions and repository map;
4. content-addressed repository or knowledge snapshot;
5. retrieved task evidence;
6. current task, run id, timestamp, and other volatile state.

Never put timestamps, random identifiers, temporary paths, or unordered JSON
before reusable context. Tool schemas and structured prompt fragments should be
serialized with sorted keys.

## Usage

```python
from orchestration import adapter

policy = adapter.PromptCachePolicy(
    namespace=f"executor:{git_tree_sha}",
    anthropic_ttl="5m",
    openai_retention=None,
)

url, headers, body = adapter.build_cached_request(
    config,
    resolution,
    system=stable_role_and_repository_prefix,
    messages=[adapter.Message("user", task_specific_suffix)],
    tools=tools,
    cache_policy=policy,
    env=env,
)
```

For Anthropic Messages, the helper converts the stable system prompt into a
cacheable content block and places a cache breakpoint on the final tool
schema. Use `anthropic_ttl="1h"` only when the same large prefix will be reused
across a sustained session; the default is five minutes.

For OpenAI-compatible requests, the helper derives `prompt_cache_key` from the
namespace, model, stable system prompt, and deterministic tool schemas. The
messages are deliberately excluded so sibling tasks share the same key while
provider prefix matching still distinguishes their suffixes. Set
`openai_retention="24h"` only when the backend supports extended retention and
the data-retention implications are acceptable.

## Namespace design

A namespace should describe a reusable workload, for example:

```text
coordinator:<git-tree-sha>:agents-v4
executor:<git-tree-sha>:tools-v2
review:<evidence-bundle-sha>:review-v3
```

Do not include a run id, timestamp, task id, random seed, or current diff unless
that value is intentionally part of the stable prefix.

## Metrics

Normalize provider usage before recording a receipt:

```python
usage = adapter.normalize_usage(resolution.wire, response_payload)
ratio = adapter.cache_efficiency(usage)
if adapter.cache_write_without_read(usage):
    logger.warning("cache entry written but not reused")
```

The normalized counters are:

- Anthropic: `cache_read_input_tokens`, `cache_creation_input_tokens`;
- OpenAI: `cached_tokens`, and `cache_write_tokens` when reported;
- both: `input_tokens`, `output_tokens`.

Track cache efficiency alongside outcome metrics such as cost per accepted
experiment, verified finding, or merged change. A high hit rate on irrelevant
context is still waste.

## Fan-out

Warm a large stable prefix with one request before launching a parallel agent
fan-out. All sibling requests must use the same namespace, model, system text,
tool ordering, and schema serialization. Keep the current task and dynamic
state in the final message.

## Application-level caches

Provider caching reduces repeated prompt processing but does not eliminate the
need for local content-addressed caches. Store parsed papers, repository maps,
AST summaries, deterministic tool outputs, test results, and mathematical
computations by source hash plus parser/tool version. Prefer retrieving the
smallest exact evidence bundle over sending the full repository.
