# Remote access: authorization, audit, and limits

Status: **design note.** Audit is implemented. Authorization is not, and this
document exists so that when it is, the decisions are made once and on the
record rather than during an incident.

The server today is stdio-only. Do not expose it over a network as it stands —
`kb/README.md` says the same, and this note is the plan for changing that.

---

## What is implemented

**Audit, on every tool and every outcome.** `search_knowledge`, `get_context`,
`get_source`, and `find_related` each write one JSONL record per invocation to
`CRYPTO_KB_QUERY_LOG_PATH`:

```json
{
  "type": "tool_invocation",
  "query_id": "…",
  "tool": "search_knowledge",
  "caller": {"client": "claude-code", "agent": "idea-generator",
             "task_id": "TASK-…", "transport": "stdio", "authenticated": false},
  "arguments": {"query": "…", "top_k": 6, "source_type": "paper"},
  "outcome": "ok",
  "result_count": 6,
  "flagged_count": 1,
  "error": null,
  "latency_ms": 83,
  "recorded_at": "2026-08-03T04:12:00Z"
}
```

Three properties worth stating, because each is a decision:

- **Refusals are recorded.** `outcome` is one of `ok`, `rejected` (a filter
  value outside the closed vocabulary), `not_found`, or `error`. A log that
  records only successes cannot answer what an audit is for.
- **Response bodies are not recorded.** Arguments are; passages are not. A log
  holding retrieved text is a second, uncontrolled copy of the corpus.
- **`authenticated` is `false`, always, today.** Over stdio the caller is
  whoever launched the process, and `CRYPTO_KB_CLIENT` / `CRYPTO_KB_AGENT` are
  self-asserted. They are good enough to attribute a query across the three
  runtimes and worth nothing as an authorization input. The field is written
  explicitly so no later reader mistakes attribution for authentication.

**Passage screening.** See `retrieval/screening.py`. Returned passages are
checked for text shaped like instructions to the reading agent, and flagged
rather than removed.

---

## What is not implemented

Authorization. There is no identity, no policy, and no per-tool permission
check, because a stdio server launched by the user already runs with exactly
the user's authority — adding a policy layer under it would be theatre.

That changes the moment the transport does.

---

## Threat model

The read path exposes a research corpus, not secrets. The realistic harms are
in this order:

1. **Corpus poisoning via retrieval.** A vendored external paper contains text
   directing an agent to abandon a lead or misreport a result. This is the one
   attack the corpus's own content makes possible, and the one that maps
   directly onto `AGENTS.md`'s rule against deliberately abandoning a
   promising path. *Partly addressed:* screening flags it; the agent still has
   to read the flag.
2. **Unbounded cost.** An agent loop issuing thousands of queries, or one
   query that returns megabytes. *Addressed for size* (top-k clamped to 10,
   4,000 characters per passage, context expansion capped at 3 either side),
   *not addressed for rate*.
3. **Index tampering.** Ruled out by construction rather than by policy: the
   MCP server exposes no ingestion or deletion tool, and the retrieval task
   role in `infra/terraform/` has no S3 write access and no queue access. An
   agent that can change what every other agent believes the corpus says makes
   every downstream conclusion unauditable. Do not add a write tool.
4. **Exfiltration of the corpus.** Low: the corpus is this program's own
   research, and the deployment is internal. Worth revisiting if the index
   ever holds embargoed or third-party-confidential material.

Note the ordering. For most retrieval services the top risk is data exposure;
here it is content that lies to the reader.

---

## Design: authorization, when the transport carries identity

Three requirements, in order of how much they matter here.

### 1. Verifiable caller identity

The transport must carry it; the process environment cannot. For HTTP, a
bearer token (OIDC/JWT) validated per request, with the claims — subject,
agent role, task id — replacing the self-asserted environment values in the
`caller` block, and `authenticated: true` set only when a signature actually
verified.

Under this harness, the natural subject is the *role*, not the person: the
five roles in `orchestration/roles.yaml` (coordinator, idea-generator,
executor, validator, red-team) are the identities whose retrieval behaviour is
worth distinguishing.

### 2. Per-tool permission, evaluated before the tool runs

A static map from tool to required permission, checked against the caller's
claims, denying by default:

| tool | permission | notes |
| --- | --- | --- |
| `search_knowledge` | `kb:search` | every role |
| `get_context` | `kb:read-context` | every role |
| `get_source` | `kb:read-source` | every role |
| `find_related` | `kb:search` | every role |
| *(any future write tool)* | — | there is no such tool; see threat 3 |

Every role holding every permission is the correct starting state, and the map
is still worth having: it makes "which callers can do what" a table someone
can read, and it makes a denial a logged event rather than a missing feature.
The case that will eventually justify it is narrower — for example restricting
`include_superseded` to the coordinator, since retracted conclusions are
exactly what a role without the context to interpret them should not be
retrieving by default.

AWS's Context Ontology Accelerator does this with Cedar policies mapped per
tool (`TOOL_CEDAR_ACTION`); the shape is right and worth copying. Its
implementation is not portable here — it is bound to Cognito and Lambda — and
a dict plus a claims check is proportionate to five roles and four tools.

### 3. Rate and size limits

- Per-caller request rate, enforced at the edge (ALB/API Gateway), not in the
  server.
- Response size is already bounded in the server, and must stay bounded there:
  the edge cannot enforce a limit that depends on `max_chars_per_result`.
- Query length capped, so a pathological query cannot cost an embedding pass
  over a megabyte of text.

---

## Deployment requirements

When the MCP service is put behind a network:

- **TLS terminated at the load balancer**, with the service reachable only
  from it (the security group in `infra/terraform/` is where this lands).
- **Bearer or workload identity per client**, validated in the service, not
  only at the edge — an edge-only check is bypassed by anything that reaches
  the service directly.
- **Audit shipped off the instance.** The JSONL log is local; in production it
  belongs in CloudWatch Logs with a retention policy, because an audit trail on
  an ephemeral task is not an audit trail.
- **The Qdrant credential from Secrets Manager**, which the `mcp` task role
  already grants and nothing else does.
- **No S3 write access on the retrieval role.** Already true; keep it true.

---

## Open questions

- **Do superseded results need a permission, or is the default exclusion
  enough?** Currently any caller can pass `include_superseded`. The argument
  for restricting it is that a retracted conclusion is the most misusable
  content in the corpus; the argument against is that the red-team role exists
  precisely to go looking at those.
- **Should a flagged passage ever be withheld from a non-coordinator role?**
  This trades the injection risk against the false-negative risk, and the
  measured false-positive rate (0 of 1,518 chunks on the evaluation corpus)
  suggests withholding would be cheap. It is still a decision to make
  deliberately, not a default to drift into.
- **Where does per-agent query budgeting belong** — the harness's dispatch
  layer, which already meters agent work, or the retrieval service? Probably
  the former; the service should still refuse to be the unbounded one.
