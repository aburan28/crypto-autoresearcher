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
cp .env.example .env              # already points at :6333

make slice                        # stage this repo's records → ingest → status
make search Q="negative results for Semaev decomposition over prime fields"
make eval-slice && make evaluate  # hybrid vs dense vs sparse, against the gates
```

Agents reach it through MCP, and **Claude Code needs no setup beyond the two
commands above**: `.mcp.json` at the repository root is this server, committed,
with a relative `--directory` so every worktree resolves it, and `uv run`
builds `kb/.venv` on first launch. Codex and OpenCode snippets are in
`clients/`. Put machine-specific settings in `kb/.env`, never in a client
config — a value set there overrides `.env` and has to be maintained per
client.

The index is derived and starts empty; `make slice` is what fills it. Skip it
and every tool returns nothing, correctly and unhelpfully.

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
`git_commit`, `content_hash`, `source_uri`, plus immutable replacement lineage
in `supersedes` and `verification_artifacts`. The same lineage is present in
`search_knowledge`, every chunk returned by `get_context`, and the bounded
metadata returned by `get_source`.

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

### Schema-supersession lineage and the fresh-collection boundary

Repository staging hash-verifies every source and replacement named in
`tools/schema_supersession_registry.yaml`. A replacement document carries its
legacy identifier in `supersedes` and both pinned `path@sha256:` bindings in
`verification_artifacts`. Redirect aliases are not indexed as duplicate
documents: their aliases and hash bindings are propagated to the terminal
corrected target. Exact-ID search accepts both the canonical ID and those
legacy aliases; `get_source` remains canonical-ID-only by design.

The staging rules cover modern typed hypotheses, questions, proposals, flat
and sharded goals, goal checkpoint shards, and subgoals. Checkpoint source IDs
use both the goal directory and immutable shard filename, for example
`goal-checkpoint:GOAL-ECDLP-001:BATCH-ef31ab-close-20260808`; the body batch ID
is not unique enough to address a shard.

For an auditable dry run, pass a `StagingDiagnostics` instance to
`stage_repository`. It reports registry-path coverage, unregistered
unparseable legacy records, different-byte duplicate source IDs, and
intentional redirect suppressions separately. These diagnostics are debt
records, not permission to repair or hide immutable sources.

`tests/unit/test_repo_corpus.py` asserts that dry stage against **floors and
per-destination coverage, not an exact document count**. The corpus is a
different size in every concurrent worktree and grows with every research
batch, so an exact pin fails on branches that changed nothing about staging.
Destinations are read back off `RULES`, so a new staging rule must declare its
own floor rather than staging an unwatched family; the floors are sized to
catch a family collapsing to zero, not to track a few percent of drift. The
debt sets above stay exact, because disclosed debt is closed and never grown.
Because that test measures the repository rather than `kb/`, `kb.yml` runs it
on every corpus-touching PR with a five-wheel install, outside the gate that
skips the full retrieval suite. Note its unparseable set is a strict subset of
`tools/merge_hygiene_baseline.txt` and not a duplicate of it: the baseline
lists everything that fails to parse on disk anywhere in the repository, while
this set lists only what a staging rule matched and no registered supersession
routes around.

**Do not reuse an existing collection after changing payload projection.** A
change to `payload_fields()` need not change an already-ingested document's
fingerprint, so an idempotent ingest can correctly skip the document while its
old Qdrant payload still lacks lineage. After code snapshot and independent
validation, an operator must select a fresh collection name and build it from
the source corpus. Never update an existing shared collection in place. Tests
use `qdrant_url=:memory:` and temporary object storage only; they neither
authorize nor perform that operator-owned rebuild.

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

Measured 2026-08-08 against the **frozen** evaluation slice
(`crypto_kb/eval/corpus_manifest.txt`: 625 paths, 610 of which carry the
frontmatter needed to stage) and the 32-question set in
`tests/retrieval_eval/questions.jsonl`:

| metric | hybrid | dense only | sparse only |
| --- | ---: | ---: | ---: |
| recall@5 | 0.826 | 0.826 | **0.870** |
| recall@10 | **0.913** | 0.870 | **0.913** |
| MRR | **0.759** | 0.673 | 0.732 |
| nDCG@10 | **0.792** | 0.718 | 0.772 |
| exact-identifier recall@5 | **1.000** | **1.000** | 0.889 |
| general recall@5 | 0.714 | 0.714 | **0.857** |
| filter correctness | 1.000 | 1.000 | 1.000 |
| source attribution | 1.000 | 1.000 | 1.000 |
| duplicate rate | 0.000 | 0.000 | 0.000 |
| median context tokens | 1,822 | 1,756 | 2,007 |

Against the plan's gates, **five of six pass and one does not**:

```text
exact identifiers recall@5     1.000   ≥ 0.95    pass
general questions recall@5     0.714   ≥ 0.80    FAIL
filter correctness             1.000   = 1.00    pass
source attribution             1.000   ≥ 0.95    pass
duplicate result rate          0.000   < 0.15    pass
median retrieved context       1,822   < 5,000   pass
```

The miss is four questions out of thirty-two, and they are the same kind:
vocabulary the pinned dependency-free embedder has no way to bridge. The
clearest is a query asking about a *"generic-group simulable"* representation
against a document that says *"GGM-simulable"* — no lexical overlap and no
learned synonym. That is the concrete argument for spending a real sentence
encoder, and it is now measurable rather than assumed: set
`CRYPTO_KB_DENSE_BACKEND=sentence-transformers`, bump the collection, and
re-run `make evaluate`.

### Why the slice is frozen

These numbers are lower than the ones first recorded here (recall@5 0.870,
general 0.786), and **no retrieval code changed between the two runs**. The
slice was defined by globs, and six of the eight were open-ended:
`ledger/evidence/EV-*.yaml` matched 137 files when the baseline was set and
299 five days later, `knowledge/findings/KN-FIND-*.md` 31 and then 57. The
corpus grew 430 → 625 documents, more documents competed for the same top-5,
and recall fell. A measured baseline that any unrelated commit can move is not
measuring retrieval.

So the slice is now an explicit manifest of repository-relative paths and the
globs are only the recipe used to regenerate it. `crypto-kb eval-manifest`
reports drift; `--write` freezes it deliberately, after which the labels are
re-checked and the baseline re-measured with the run that justifies it. A
manifest path that has been deleted is an error, not a silent shrink.

Two other honest readings of that table:

- **Sparse alone beats hybrid on general recall@5** on this corpus (0.857 vs
  0.714), while hybrid wins on ranking quality (MRR, nDCG@10) and on exact
  identifiers (1.000 vs 0.889). This corpus is unusually identifier-dense,
  which favours lexical matching. Hybrid is kept because ranking quality is
  what a top-6 budget actually spends, and because dropping the dense side
  would cost the exact-identifier gate; the claim is checked by a test rather
  than asserted.
- **Unsupported-answer rate is not measured.** It is a property of an answer,
  and this harness retrieves without answering. What is measured is the
  precondition: whether the passages needed to support an answer came back.
  Recall is likewise a floor — it counts only hand-labelled sources.

## Commands

```bash
crypto-kb stage-repo ..          # repository records → corpus layout + sidecars
crypto-kb stage-repo .. --eval-slice   # just the frozen evaluation corpus
crypto-kb eval-manifest ..       # how the frozen slice differs from the globs today
crypto-kb eval-manifest .. --write     # freeze it again, deliberately
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
├── infra/            Dockerfile (two targets), terraform (S3→EventBridge→SQS→ECS)
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
make test        # full suite: builds a 610-document corpus and queries it (~60s)
```

209 tests. The integration and evaluation tests run against real repository
documents through the real pipeline and a real (embedded) Qdrant — nothing is
mocked between "a file on disk" and "a search result", because a retrieval test
against fakes tests the fakes.

## Not built

Deliberately postponed, per the plan: GraphRAG, automatic ontology
construction, embedding fine-tuning, multi-hop agentic retrieval,
model-generated authoritative metadata, automatic paper summarization,
distributed ingestion, and a web UI.

Also not built: the remote MCP deployment. The Terraform describes the
production topology and the IAM boundaries; the TLS termination, bearer
authentication, per-client identity, and rate limiting the plan calls for are
specified there but not implemented, and the server today is stdio-only. Do
not expose it over a network as it stands.
