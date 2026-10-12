# Batch inference: the Message Batches API as a delivery lane

The Anthropic Message Batches API takes ordinary Messages requests, processes
them asynchronously, and returns results keyed by a `custom_id`. Most batches
finish within an hour; every request is served within 24 hours or expires
unbilled; results stay downloadable for 29 days; and all token usage is
charged at half the synchronous price. For this program that is a second
**delivery lane**, not a second kind of inference: a batched request is
resolved by the same resolver, built by the same request builder, guarded by
the same cost policy, and recorded with the same receipt fields as a
synchronous call, plus the batch it travelled in.

`orchestration/adapter/batch.py` is the implementation; this page is how to
use it and what it records. It is standard library only, like the rest of the
adapter — no vendor SDK is a dependency of the research program.

## When a batch is the right lane

Single-turn completions whose result nobody is waiting on at the keyboard:

* ideation sweeps — one prompt per research question, open idea, or
  literature source;
* evidence summaries, literature triage, knowledge-curation drafts;
* review *drafts* that a human or an independent session will read later
  (independence is a property of who built the prompt and who reads the
  answer, not of the transport);
* eval suites and any other many-prompt, same-shape workload.

Not a batch: the `api_direct` tool loop and any other multi-turn agent
session. Each turn depends on the previous result, so there is nothing to
submit together; the router refuses `delivery: batch` for multi-turn work and
`auto` routes it interactively.

The Message Batches API is a first-party capability. Only the `anthropic`
backend declares `supports_message_batches: true` in `providers.yaml`; the
gateways that re-serve open-weight models over the Anthropic wire format
(`zai-anthropic`, `fireworks-anthropic`, `abliteration-anthropic`) do not
batch, and asking them to is an error rather than a silent synchronous call.

## Routing: `delivery` and `deadline_seconds`

A handoff's `inference` block may state how the result should travel:

```yaml
inference:
  policy: research-deep
  delivery: auto            # interactive | batch | auto   (default: interactive)
  deadline_seconds: 14400   # when the result is needed; drives `auto`
```

* `interactive` — the synchronous Messages API, now. The default, and what
  every handoff written before this field existed means.
* `batch` — submit to a Message Batch. Refused on a backend without the API.
* `auto` — the router decides, and records why:

| condition | lane |
|---|---|
| backend has no batch API, or the work is a multi-turn tool loop | interactive |
| dispatch `priority` ≥ `urgent_priority` (90) | interactive — the queue already says it is wanted now |
| no deadline stated | **batch** — nobody is waiting, so it takes the half-price lane |
| deadline < `expected_latency_seconds` + `deadline_slack_seconds` (3600 + 1800) | interactive |
| otherwise | **batch**; if the deadline is inside the 24 h maximum the decision notes that `batch escalate` exists |

The figures live under `defaults.batch` in `providers.yaml`. They are the
provider's published envelope, not a guarantee: a batch *may* take the full
24 hours, and that is what escalation is for.

```sh
# decide without sending anything
python3 -m orchestration.adapter batch plan --delivery auto --deadline-seconds 7200
python3 -m orchestration.adapter batch plan --task ledger/handoffs/TASK-....yaml --priority 40
```

`tools/research_dispatch.py` validates both fields on every queued handoff
(`delivery` must be one of the three modes, `deadline_seconds` a non-negative
number) so a typo stops at dispatch, not after a day's wait.

## Submitting

```sh
# one request per prompt file, resolved through a role's default policy
python3 -m orchestration.adapter batch submit --role idea-generator \
    --prompt-file q1.md --prompt-file q2.md --task-id TASK-20261005-ab12cd

# from a handoff: policy, permissions, delivery, deadline, and task id all
# come from the record; the role contract is the system prompt
python3 -m orchestration.adapter batch submit --task ledger/handoffs/TASK-20261005-ab12cd.yaml \
    --prompts-jsonl prompts.jsonl

# many prompts: one JSON object per line
# {"custom_id": "TASK-20261005-ab12cd-rq1", "prompt": "...", "system": "...optional..."}
```

What `submit` does, in order:

1. **Resolve** the policy exactly as a synchronous call would —
   `fallback_allowed`, `degraded_allowed`, independent-session gates,
   per-task `reasoning_effort` — and print the resolution summary.
2. **Route.** With `--task` the handoff's `delivery` and `deadline_seconds`
   decide; `--delivery`, `--deadline-seconds`, and `--priority` override. If
   the router picks interactive, the prompts run **now** through the same
   request builder, the outputs are printed, and `--receipt-dir` writes one
   receipt per prompt carrying the decision. Nothing is batched behind your
   back, and nothing waits behind your back either.
3. **Build** each request with `build_request` and attach prompt caching at
   the one-hour TTL (a batch routinely outlives a five-minute cache entry).
   The body is byte-for-byte what the synchronous lane would send, apart
   from that TTL.
4. **Preflight** the first request through `count_tokens`. The batch
   endpoint validates its requests asynchronously and reports a malformed
   one only when the whole batch has ended; counting tokens costs nothing
   and catches a bad model id, thinking configuration, or message shape
   immediately. `--no-preflight` skips it; `--dry-run` stops after it and
   prints the body.
5. **Submit**, then record the submission write-once (below).

`custom_id`s default to `<task-id>-<prompt stem>` (or `-0000`, `-0001`, …),
which already satisfies the API's `^[a-zA-Z0-9_-]{1,64}$` and is the join
key back to the ledger. Results come back in any order: everything here
keys by `custom_id`, never by position.

## The registry: collect from any session

Sessions are ephemeral and a batch is not, so everything about a batch is
recorded under `coordination/inference-batches/<msgbatch id>/`
(`AUTORESEARCH_BATCH_DIR` or `--registry` to relocate), **one file per
event, write-once**, keyed by the provider's globally unique batch id so
concurrent worktrees never touch the same path:

| file | written by | contents |
|---|---|---|
| `submission.json` | `submit` | batch state at creation, backend, task id, the routing decision, the preflight result, and per-request metadata: `custom_id`, task, role, policy, resolved model, effort, fallback, `body_sha256` |
| `requests.jsonl` | `submit` | the exact request bodies, so an escalation re-runs one verbatim |
| `results.jsonl` | `collect` | the results file as downloaded |
| `collected.json` | `collect` | batch state at collection, result type per `custom_id`, missing/unknown ids, and one inference receipt per result |
| `escalations/<custom_id>.json` | `escalate` | the synchronous answer, its receipt, and the reason |
| `cancel.json` | `cancel` / `escalate` | when and why |

```sh
python3 -m orchestration.adapter batch list                   # local registry, offline
python3 -m orchestration.adapter batch list --remote          # plus the workspace's batches
python3 -m orchestration.adapter batch status --all           # every open local batch
python3 -m orchestration.adapter batch wait msgbatch_... --timeout-seconds 3600
python3 -m orchestration.adapter batch collect msgbatch_... [--print | --json]
```

The directory is commit-safe (write-once files, globally unique ids), and
whether a batch's records are archived with a task is the Coordinator's
call, as for any other task artifact; note that `requests.jsonl` repeats
the system prompt per request, so a large sweep is a large file.

`collect` downloads once and answers from disk ever after — in this session
or any other, before or after the provider's 29-day retention. `wait` stops
on its wall-clock budget without raising (exit 1, batch still collectable);
a budget stop is infrastructure signal, not a result. `list --remote` shows
batches submitted from other checkouts and marks the ones this registry
does not know; `collect` still records those, with the `custom_id`s listed
under `unknown` because there is no local submission to join them to.

Per-result receipts have the same `response` block as a synchronous receipt
(`reported_model`, `stop_reason`, `usage` with cache counters,
`model_matches_resolution`) plus a `delivery` block naming the batch,
`custom_id`, result type, and `body_sha256`. `latency_seconds` is `null` on
a batch result: an asynchronous turnaround is not a latency.

Result types, and what to do with each:

| type | meaning | action |
|---|---|---|
| `succeeded` | a message was produced | use it; cite the batch id and `custom_id` |
| `errored` / `invalid_request_error` | the request itself was rejected | fix the request; a resubmission of the same body fails the same way |
| `errored` / other | server-side error, unbilled | resubmit |
| `expired` | not served within 24 h, unbilled | resubmit, or escalate if it is now urgent |
| `canceled` | cancelled before it was sent, unbilled | nothing |

`collect` prints the resubmittable ids. Expiry and errors are never
negative evidence about anything (AGENTS.md rule 3).

## Urgency after submission: `escalate`

A result that was cheap to wait for an hour ago can become the thing a
review is blocked on. Results are released only when the **whole** batch
ends, so there is no way to pull one finished answer out early; the right
move is to run the request synchronously now:

```sh
python3 -m orchestration.adapter batch escalate msgbatch_... --custom-id TASK-...-rq3 \
    --reason "validator waiting on this"
python3 -m orchestration.adapter batch escalate msgbatch_...            # everything still pending
python3 -m orchestration.adapter batch escalate msgbatch_... --custom-id X --cancel-remaining
```

What it guarantees:

* the stored body from `requests.jsonl` is sent **verbatim** to the
  synchronous endpoint — same model, effort, system prompt, cache markers —
  so the answer is comparable to what the batch would have produced;
* the answer and its receipt are written write-once under `escalations/`,
  with `escalated_from_batch`, `custom_id`, `body_sha256`, and the reason;
* escalating the same `custom_id` twice is a no-op, not a second payment;
* once every request in the batch has been escalated (or with
  `--cancel-remaining`) the batch is **cancelled**, so the double payment
  is bounded to the requests actually needed now, and `cancel.json` says
  why;
* when the batch later ends anyway and is collected, the batch copy of an
  escalated request is marked `superseded_by_escalation: true` in its
  receipt and in `collect`'s summary. Two answers to one question are never
  left looking independent.

`escalate` refuses a batch that has already ended (collect it instead) and
`custom_id`s the batch does not contain.

## What every record carries

The manifest `inference` block written by `orchestration/adapter/manifest.py`
now names the lane:

```yaml
inference:
  requested_policy: research-deep
  ...
  delivery: batch                 # interactive | batch | null (no model in the loop)
  batch_id: msgbatch_01Hk...      # null unless delivery is batch
```

A manifest that did not say which lane it used could explain neither its
cost (half) nor its timing (up to a day). Every batch receipt also carries
`body_sha256`, which ties the result to the exact request body in
`requests.jsonl` — the same discipline as `path_sha256` on an archive.

## Limits worth knowing

* 100,000 requests or 256 MB per batch, whichever first; `check_entries`
  refuses a larger submission before any byte leaves the machine.
* `stream`, `speed` (fast mode), and `max_tokens: 0` are rejected by the
  batch endpoint; the request builder never emits them, and `submit` checks.
* Rate limits apply to the number of requests queued across batches as well
  as to the HTTP calls; a busy workspace sees more `expired` results.
* Cache hits inside a batch are best-effort (the provider quotes 30–98 %);
  the one-hour TTL and a shared system prompt per batch are what move that
  number.
* `batch delete` removes the provider's copy of the results. The local
  registry is kept: it is the record of what was asked and answered.

## Programmatic use

```python
from orchestration import adapter
from orchestration.adapter import batch

cfg = adapter.load()
resolution = adapter.resolve(cfg, "research-deep", backend="anthropic")
decision = adapter.choose_delivery(cfg, backend="anthropic", requested="auto",
                                   deadline_seconds=14400, priority=40)
if decision.delivery == "batch":
    entries = [adapter.build_batch_entry(
        cfg, resolution, custom_id=batch.custom_id_for(task_id, i, label),
        system=role_contract, messages=[adapter.Message("user", prompt)],
        task_id=task_id, role="idea-generator")
        for i, (label, prompt) in enumerate(prompts)]
    handle = batch.submit(cfg, "anthropic", entries, task_id=task_id, decision=decision)
    ...                                   # any later session:
    collected = batch.collect(cfg, "anthropic", handle.id)
    for custom_id, result in collected.results.items():
        if result.type == "succeeded":
            text, usage = result.completion.text, result.completion.usage
```

Every function takes `env=` and `opener=` for the same reason the transport
does: tests run against an in-memory endpoint and never touch the network
(`tests/test_batch_inference.py`).
