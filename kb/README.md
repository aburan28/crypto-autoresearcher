# crypto-kb — S3 → Docling → Qdrant → MCP

A shared, auditable retrieval layer over this program's research corpus.
Agents ask a precise question through MCP and get 4–8 bounded passages, each
carrying its source, section, evidence status, and experiment or commit
provenance — instead of loading the corpus into context.

Object storage is the source of truth. Everything here — normalized markdown,
chunks, vectors, the Qdrant collection — is derived and can be deleted and
rebuilt without loss. That is the same rule `knowledge/README.md` already
states for the knowledge corpus: "any future search index must be generated
from these files, never replace them as the source of truth."

```text
corpus (S3 or filesystem)
    │  initial backfill / S3 events → EventBridge → SQS
    ▼
ingestion worker
    ├── parse (Docling for PDF/DOCX/HTML, native for markdown/YAML/text)
    ├── validate the conversion (equations, columns, tables, headers)
    ├── chunk (hierarchy first; theorems, proofs, tables never split)
    ├── embed (dense + BM25 sparse)
    └── upsert (deterministic point ids)
    ▼
Qdrant  ──►  retrieval service  ──►  FastMCP
                                      ├── search_knowledge
                                      ├── get_context
                                      ├── get_source
                                      └── find_related
                                      ▼
                        Claude Code · Codex · OpenCode
```

## Quick start

```bash
cd kb
make install-all                  # core + qdrant + mcp + aws + dev
make qdrant-up                    # docker: qdrant on :6333
export CRYPTO_KB_QDRANT_URL=http://localhost:6333

make slice                        # stage this repo's records → ingest → status
make search Q="negative results for Semaev decomposition over prime fields"
make eval-slice && make evaluate  # hybrid vs dense vs sparse, against the gates
```

Without Docker, point `CRYPTO_KB_QDRANT_URL` at a directory instead
(`export CRYPTO_KB_QDRANT_URL=./.kb-index`). That runs Qdrant embedded but
file-backed, so `ingest` in one command and `search` in the next work with no
server — single-writer, and no payload indexes, but correct at this corpus
size. The default `:memory:` is embedded *and* in-process: it is right for
tests and wrong for the CLI, where each command would get a fresh empty index.
`crypto-kb status` says so when it is configured that way.

## What it does

### The retrieval contract comes first

`src/crypto_kb/models.py` defines the agent-facing types before any ingestion
code, and the MCP server adds nothing of its own — it serialises them. Every
result carries what is needed to cite it: `source_id`, `section_path`,
`page_start`/`page_end` (when the parser could establish them), `claim_status`,
`evidence_level`, `authority`, `superseded`, `experiment_id`, `run_ids`,
`git_commit`, `content_hash`, `source_uri`.

### Chunking respects the mathematics

Hierarchy is consulted before token limits, never the other way round. A
theorem and its proof, a definition, an algorithm, an assumptions list, an
experiment result table, an equation and the sentence explaining it — none of
these is ever cut open. When an atomic unit exceeds the maximum chunk size it
is emitted oversized on purpose, and the chunk records which unit forced it.

Child chunks (~640 tokens) are what search scores against; parent sections
(~3,000 tokens) live in the same collection behind an `is_parent` flag and are
what `get_context` expands into.

### Ingestion is idempotent and fails closed

`DISCOVERED → DOWNLOADED → PARSED → NORMALIZED → CHUNKED → EMBEDDED → INDEXED`,
with the manifest updated at each step. A document is skipped when its
fingerprint — source bytes + metadata + parser version + chunker version +
embedding model version — is unchanged, so re-running a backfill is a no-op and
at-least-once queue delivery is safe. Point ids are `UUIDv5(namespace,
source_id + chunk_index + content_hash)`, so an update overwrites its own rows
and any point the new version no longer produces is deleted.

A document whose sidecar is missing, invalid, or model-generated is recorded
`REJECTED` with the reason and left out of the index. It is never indexed with
guessed metadata: a paper filed under the wrong claim status is worse than one
that is absent, because absence is visible and a wrong filter result is not.

### Provenance is enforced, not documented

`AUTHORITY_ORDER` ranks machine-checked proof > reproduced experiment >
single-run experiment > peer-reviewed > preprint > internal analysis > agent
hypothesis. Where a sidecar's stated authority disagrees with its recorded
evidence level, the evidence level wins and the disagreement is reported.
Superseded material is excluded from retrieval by default and never deleted.
A sidecar marked `provenance_class: model-suggested` has its authoritative
fields dropped with a warning; only `topics` survives.

### Retrieved passages are screened, and flagged rather than dropped

`inputs/` holds vendored external papers and `knowledge/literature/` holds
notes on other people's work; both reach an agent's context through
`search_knowledge`. Returned passages are checked for text shaped like
instructions to the reading agent — instruction overrides, role reassignment,
forged prompt boundaries, exfiltration, tool directives, and conclusion
steering — and flagged with a verdict the agent can see.

**Flagged passages are still returned.** That is the design decision, and it
goes the other way from most guardrail layers for a reason specific to this
corpus: mathematical prose is full of imperatives. "Ignore the lower-order
terms", "disregard the degenerate case", "assume the curve is generic" — a
screener aggressive enough to catch a real injection catches those too, and
silently dropping them removes exactly the assumption and boundary statements
a conclusion must be scoped by. A false positive that deletes a theorem's
hypothesis is worse than a flagged passage the reader was warned about.

Measured on the 1,518-chunk evaluation corpus: **0 false positives.** The
first version flagged 5, all `conclusion-steering`, and all 5 were this
program's own governance prose ("never by editing a committed record", "Never
record an attestation you did not obtain"). That category is now scoped to
external sources — the risk is a vendored paper steering our conclusions, not
our ledger doing its job. The generic injection categories still fire
everywhere. `screening_action = "drop"` is available and off by default; even
then it filters at read time and never touches the index.

It is a heuristic, not a security boundary. The boundary is that agents cannot
write to the index at all.

### Hybrid retrieval, and why

Half the queries this corpus must answer are exact lookups — `EXP-GGM-001`,
`P-256`, `ePrint 2026/1486`, `Theorem 4.3`. Dense and sparse results are fused
with reciprocal rank fusion rather than a weighted score blend, because BM25
scores and cosine similarities are not on a comparable scale and any fixed
weighting between them is a parameter that rots as the corpus changes.

Three findings from building the evaluation set, each measured:

1. **Chunks had no lexical trace of their own document.** Identifiers live in
   YAML frontmatter, which the parser strips as non-prose, so the query
   `KN-LIT-001` could not retrieve KN-LIT-001. Vectors are now built over the
   chunk text prefixed with its identity; payloads keep the text alone.
   Exact-identifier recall@5: 0.44 → 0.89.
2. **Decomposed identifier parts drowned the whole form.** Every open-problem
   note contains `kn`, `open` and some `001`. Parts now carry 0.3 of a term's
   weight. Sparse-mode general recall@5: 0.71 → 0.86.
3. **Lexical scoring cannot express identity at all.** `kn-open-001` appears in
   26 documents that *cite* KN-OPEN-001 — more text than the one that is it.
   Identifiers in a query are now resolved by an exact payload lookup on an
   indexed `identity_tokens` field and placed first. Exact-identifier recall@5:
   0.89 → 1.00.

## Measured results

Against the evaluation corpus slice (415 documents, 1,518 chunks) and the
32-question set in `tests/retrieval_eval/questions.jsonl`:

| metric | hybrid | dense only | sparse only |
| --- | ---: | ---: | ---: |
| recall@5 | **0.870** | 0.826 | 0.913 |
| recall@10 | 0.913 | 0.870 | 0.913 |
| MRR | **0.764** | 0.673 | 0.748 |
| nDCG@10 | **0.797** | 0.718 | 0.783 |
| exact-identifier recall@5 | 1.000 | 1.000 | 1.000 |
| general recall@5 | 0.786 | 0.714 | 0.857 |
| filter correctness | 1.000 | 1.000 | 1.000 |
| source attribution | 1.000 | 1.000 | 1.000 |
| duplicate rate | 0.000 | 0.000 | 0.000 |
| median context tokens | 1,832 | 1,724 | 2,059 |

Against the plan's gates, **five of six pass and one does not**:

```text
exact identifiers recall@5     1.000   ≥ 0.95    pass
general questions recall@5     0.786   ≥ 0.80    FAIL
filter correctness             1.000   = 1.00    pass
source attribution             1.000   ≥ 0.95    pass
duplicate result rate          0.000   < 0.15    pass
median retrieved context       1,832   < 5,000   pass
```

The miss is three questions out of fourteen, and they are the same kind:
vocabulary the pinned dependency-free embedder has no way to bridge. The
clearest is a query asking about a *"generic-group simulable"* representation
against a document that says *"GGM-simulable"* — no lexical overlap and no
learned synonym. That is the concrete argument for spending a real sentence
encoder, and it is now measurable rather than assumed: set
`CRYPTO_KB_DENSE_BACKEND=sentence-transformers`, bump the collection, and
re-run `make evaluate`.

Two other honest readings of that table:

- **Sparse alone beats hybrid on raw recall@5** on this corpus (0.913 vs
  0.870), while hybrid wins on ranking quality (MRR, nDCG@10). This corpus is
  unusually identifier-dense, which favours lexical matching. Hybrid is kept
  because ranking quality is what a top-6 budget actually spends, but the
  claim is checked by a test rather than asserted.
- **Unsupported-answer rate is not measured.** It is a property of an answer,
  and this harness retrieves without answering. What is measured is the
  precondition: whether the passages needed to support an answer came back.
  Recall is likewise a floor — it counts only hand-labelled sources.

## Commands

```bash
crypto-kb stage-repo ..          # repository records → corpus layout + sidecars
crypto-kb stage-repo .. --eval-slice   # just the fixed evaluation corpus
crypto-kb ingest [KEY|PREFIX]    # idempotent; --force to re-ingest
crypto-kb search "query" [--json] [--source-type paper] [--mode dense|sparse]
crypto-kb context <chunk_id> [--before 2 --after 2]
crypto-kb source <source_id>
crypto-kb related <source_id>
crypto-kb delete <source_id>     # removes points, tombstones the manifest
crypto-kb reindex --yes          # drop and rebuild; recomputes sparse statistics
crypto-kb status                 # corpus, manifests, index
crypto-kb doctor                 # reachability, FAILED documents, parse warnings
crypto-kb evaluate               # metrics and gates; exits non-zero on a failure
crypto-kb worker                 # consume S3 events from SQS
crypto-kb mcp                    # FastMCP server on stdio
```

`crypto-kb doctor` lists documents whose conversion raised a warning —
truncated equations, replacement characters, out-of-order sections, ragged
tables, unstripped running headers. Those are the ones to inspect by hand
before trusting a high-value paper's chunks.

## Deviations from the plan

- **`kb/`, not `knowledge/`.** The plan puts the package at `knowledge/`; that
  directory is this program's curated corpus and is referenced throughout
  `AGENTS.md`, the skills, and the tooling. Taking the name would have
  displaced the source of truth for its own index.
- **Heavy dependencies are extras, imported lazily.** Docling, qdrant-client,
  fastmcp, and boto3 are optional. The core pipeline — parse, chunk, hash,
  embed, fingerprint, manifest — installs and tests with no Qdrant, no AWS
  credentials, and no torch, which matches this repository's stated preference
  for a small, slow-moving dependency set that a run record can still be
  reproduced against years from now.
- **The default dense embedder has no learned weights.** A hashed-feature model
  is deterministic across machines and years, needs no download, and made the
  architecture testable end to end before committing to a particular neural
  model. It is weaker on paraphrase, the evaluation says by how much, and
  swapping it is a config change plus a new collection.
- **A local object store sits behind the same interface as S3.** Not a test
  double: it is how the vertical slice runs against this repository's own
  corpus without an AWS account, and it gives the evaluation a real, stable
  fixture set.
- **A YAML/JSON record parser was added.** Much of this corpus is ledger
  records — evidence, hypotheses, decisions. Indexed as a raw code block they
  are close to unretrievable, since the text agents search for is inside the
  values. They are rendered into headed markdown so section paths mirror the
  record structure.
- **A `stage-repo` command was added.** The plan assumes documents arrive in S3
  with hand-written sidecars. These records already exist here with provenance
  in their frontmatter, so the sidecars are *derived* from them —
  `provenance_class: deterministic` — rather than authored again.

## Layout

```text
kb/
├── config/           metadata-schema.json, retrieval.yaml (documented defaults)
├── clients/          MCP configuration for Claude Code, Codex, OpenCode
├── infra/
│   ├── docker/       Dockerfile, two targets (mcp, worker)
│   └── terraform/    AWS (S3→EventBridge→SQS→IAM) on HCP Terraform, plus
│                     bootstrap/ which creates the workspaces themselves
├── src/crypto_kb/
│   ├── models.py     the retrieval contract
│   ├── config.py     settings, corpus prefixes
│   ├── hashing.py    content hash, fingerprint, deterministic point ids
│   ├── metadata.py   sidecar validation, provenance rules, authority resolution
│   ├── text.py       tokenization (identifier-aware)
│   ├── storage/      ObjectStore protocol, local + S3, manifests
│   ├── parsing/      docling, markdown, records, plaintext, math validation
│   ├── chunking/     hierarchical, atomic units, references
│   ├── embeddings/   dense, sparse (BM25), reranker
│   ├── index/        collection schema, Qdrant wrapper
│   ├── ingest/       pipeline, backfill, SQS worker, repo staging
│   ├── retrieval/    hybrid, filters, diversify, formatting
│   ├── eval/         harness, gates, corpus slice
│   ├── mcp/          FastMCP server (read-only)
│   └── cli.py
└── tests/            unit · integration · retrieval_eval
```

## Testing

```bash
make test-fast   # unit tests, no corpus build (~0.3s)
make test        # full suite: builds a 415-document corpus and queries it (~60s)
```

186 tests. The integration and evaluation tests run against real repository
documents through the real pipeline and a real (embedded) Qdrant — nothing is
mocked between "a file on disk" and "a search result", because a retrieval test
against fakes tests the fakes.

## Not built

Deliberately postponed, per the plan: GraphRAG, automatic ontology
construction, embedding fine-tuning, multi-hop agentic retrieval,
model-generated authoritative metadata, automatic paper summarization,
distributed ingestion, and a web UI.

Also not built: the remote MCP deployment. `infra/terraform/` manages the
corpus notifications, the queue, and the two asymmetric IAM roles, and runs on
HCP Terraform (`infra/terraform/README.md` is the runbook — organization,
workspaces, dynamic credentials). What is *not* written is the ECS cluster and
task definitions, and the TLS termination, bearer authentication, and rate
limiting the plan calls for. The server today is stdio-only. Do not expose it
over a network as it stands.

Audit *is* implemented — every tool, every outcome including refusals, with
caller attribution and without response bodies. Authorization is not, because
over stdio the caller already runs with the user's authority and a policy
layer under that would be theatre. `docs/remote-access.md` is the design note:
threat model, the per-tool permission table, and what has to be true before
the transport changes.

Nothing has been applied: the Terraform is validated, not deployed.
