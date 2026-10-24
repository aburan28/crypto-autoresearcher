# Measuring what instructions cost per call

Claude Code sends every skill's and agent's description, and `CLAUDE.md`, on
every model call of every session. `AGENTS.md` is read once per session; its
size is checked in words by `tools/check_instruction_budget.py`. The per-call
part is measured in tokens by `tools/measure_context.py`:

```sh
python3 tools/measure_context.py context HEAD --against origin/main
python3 tools/measure_context.py routing HEAD --against origin/main --runs 2
```

`context` builds a config-only copy of each ref per file group, runs one
headless turn that answers "OK", and reads the input tokens the runtime counted.
Each group's cost is its variant minus the empty floor. Counts are
deterministic, so one run per ref is enough; it costs 5 short calls per ref.

`routing` sends plain-language requests (`ROUTING_REQUESTS` in the tool, each
naming the skill or subagent it should reach, never in the request itself) to
both refs and prints the requests whose route differs. With two runs per
request a single `none` is noise; re-run a differing request before concluding
that a description lost its trigger.

Run both before merging a change to any skill or agent description or to
`CLAUDE.md`, and put the numbers in the PR. On 2026-10-22, before and after
`add05c5` (shorter descriptions):

| tokens per call | before | after |
| --- | --- | --- |
| Claude Code itself | 14,233 | 14,231 |
| `CLAUDE.md` | 1,287 | 1,286 |
| skill descriptions | 2,974 | 2,603 |
| agent descriptions and tools | 2,216 | 2,174 |
| this repository, total | 6,471 | 6,057 |

Both commands call the `claude` CLI (`MEASURE_CONTEXT_MODEL`, default
`claude-opus-5-5`) and spend real tokens. They drop the parent session's
environment variables so a nested run does not attach to the session it was
started from.
