# Research KB

One research library for `crypto`, `crypto-autoresearcher`, `cryptanalysis`,
`crypto-lean`, `cryptologic-archives` and the original paper collection. Search it
from any repository using Claude Code, Codex, a terminal or a cloud session.

The standalone application reuses the existing `crypto-kb` parsing, mathematical
chunking and Qdrant integration. SQLite FTS5 supplies a usable local baseline and
fast exact IDs; optional Qdrant provides hybrid search. One authenticated HTTPS
endpoint makes the same corpus accessible to local and cloud clients.

## Install and search locally

Requires Python 3.11+, Linux or macOS. Install the package in a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.lock
python -m pip install --no-deps --no-build-isolation .
```

Copy `examples/sources.toml` to `~/.config/research-kb/sources.toml` and set the
checkout paths. Relative paths resolve against the configuration file, never the
caller’s working directory. Register only canonical checkouts, not every worktree.
The unmounted PDF directory is intentionally commented out in the example.

```sh
research-kb refresh
research-kb status
research-kb search "KN-LIT-001"
research-kb search "Semaev decomposition" --repo crypto-autoresearcher
research-kb theorems "CryptoLean.Semaev.S3_root_iff"
research-kb mcp
```

Default state is `~/.local/share/research-kb`. Override it with
`RESEARCH_KB_HOME` or `--home`. `RESEARCH_KB_CONFIG` or `--config` selects the
source registry. Both agent clients can launch the same installed `research-kb
mcp` command with the same shared home; no project checkout is needed to query it.

## Hosted architecture

```text
Repository snapshots + PDFs -> operator import -> SQLite catalog + immutable originals
                                                optional Qdrant hybrid index
                                                          |
                                    EC2: authenticated read-only API and MCP
                                                          |
                                          Caddy HTTPS on your hostname
                                                          |
                                     local agents and permitted cloud runtimes

Private versioned S3: source bundles and backups
Encrypted EBS: catalog, original object cache, Qdrant storage
```

Start with one EC2 instance, SQLite on EBS and a Qdrant container. RDS, Redis,
multi-node search and a load balancer are unnecessary for this first version.
Only HTTPS is public; Qdrant has no host ports and SSH ingress stays closed.
The EC2 deployment uses Systems Manager for administration and Caddy for TLS.
See [AWS deployment](docs/AWS.md) for the exact provisioning and cutover steps.

The HTTP server requires a token registry and will not start without one. Create
a separate credential for each client. The server stores hashes only:

```sh
research-kb token create --client codex-cloud --output /secure/codex-cloud.token
research-kb token create --client claude-cloud --output /secure/claude-cloud.token
export RESEARCH_KB_AUTH_FILE="$HOME/.local/share/research-kb/auth.json"
research-kb serve
```

Token output files are mode 0600 and are never printed by the command. Install
their values as client runtime secrets. `token revoke --client NAME` takes effect
on the next request. If all clients are revoked, HTTP fails closed.

For container operation, set an absolute `RESEARCH_KB_DATA_DIR`, ensure it is
writable by UID 10001, and set `RESEARCH_KB_AUTH_DIR` to a directory containing
the hash registry as `auth.json`. Mounting the directory keeps atomic token
rotations visible to the running container. Then:

```sh
docker build -t research-kb:local .
docker compose up -d
```

`compose.yaml` exposes the authenticated service only on `127.0.0.1:8080`.
`compose.aws.yaml` adds public HTTPS. Reading SQLite WAL requires local sidecar
access; the service has a writable data mount but exposes only retrieval routes.

## Local and cloud client setup

Configure one user-level MCP entry and reuse it from every repo. Templates:

- [Codex](clients/codex.toml): native HTTP using `bearer_token_env_var`.
- [Claude Code](clients/claude-code.json): HTTP with a runtime-secret header.
- [Local stdio](clients/local-stdio.json): direct access to the shared local data.
- `research-kb connect https://kb.example.com`: stdio-to-remote bridge.

Cloud products differ in custom MCP support. Where a runtime supports it, supply
the HTTP configuration and `RESEARCH_KB_TOKEN` to the **running session**, not only
the setup step. Allow outbound HTTPS to the KB hostname in the runtime network
policy. The service is reachable independently of any local laptop or VPN.

For cloud sessions that cannot register a custom MCP, use the read-only fallback:

```sh
export RESEARCH_KB_URL=https://kb.example.com
# RESEARCH_KB_TOKEN comes from the cloud session's secret settings.
sh clients/cloud-search.sh Semaev decomposition
# Or, with the package installed:
research-kb remote-search https://kb.example.com "Semaev decomposition"
```

No AWS credential is given to an agent. A per-client bearer token permits access
only to this retrieval service. Never commit the actual token or place it in a URL.
The client’s platform still needs to permit the endpoint at runtime; this repo
cannot configure a managed cloud product’s account settings automatically.

## Retrieval contract

| MCP tool | Purpose |
| --- | --- |
| `search_knowledge` | Lexical search, or `mode="hybrid"` with a current index; optional repo/source-type filters |
| `get_context` | Bounded nearby passages for a selected chunk |
| `get_source` | Metadata, versions, all contributing origins and sections |
| `find_related` | Other sources on a similar topic |
| `search_theorems` | Lean names or source statements, with repo/environment filters |
| `get_theorem` | Declaration statement, assumptions and any bound verification receipt |
| `kb_status` | Coverage counts, active revision and hybrid freshness |

REST provides `/v1/search?q=...`, `/v1/theorems?q=...`, `/v1/status`,
`/v1/sources/{id}` and authenticated original downloads. `/healthz` exposes only
liveness without authentication; `/readyz` is authenticated and returns 503 for
an empty corpus. `/mcp` implements stateless Streamable HTTP MCP.

Results include canonical IDs, content hashes, source versions, origin repositories,
paths and commits, extraction coverage, supersession state and PDF page spans.
Versioned download URLs retain the original bytes behind an old citation.
Known-ID ambiguity is returned explicitly. Notes about a paper remain distinct
from the original full text; original PDF bytes are deduplicated across repos.
Extraction is unreviewed until separately checked; scanned PDFs without a usable
text layer report failure and need OCR. Printed page labels are not inferred.

## Ingestion and migration

Register source roots once, then run `refresh`. A single writer lock prevents
competing imports. Unchanged source versions reuse their chunks; missing files
stop appearing in current search, and historical versions remain readable.
The CLI reports failed inputs rather than silently claiming complete coverage.

For a hosted instance, package selected source files locally and transfer through
the private S3 inbox. The service never clones repositories on an agent request:

```sh
research-kb bundle /tmp/research-sources.tar.gz
aws s3 cp /tmp/research-sources.tar.gz s3://YOUR-BUCKET/inbox/sources-UNIQUE.tar.gz
```

The EC2 operator job downloads new bundles, verifies every hash, imports them and
builds a new index. Archive extraction never trusts file paths or symlinks.
Different bundles are additive: importing a partial bundle does not remove sources
from other bundles. To reconcile deletions, run `refresh` with a full registered
source snapshot on the operator host. Source-only Lean bundles do not transfer a
claim of compiled verification.

During cutover, point both clients at the shared endpoint and remove only old KB
launch entries. Leave other MCP services, source repositories and immutable
research records intact. Canonical source IDs derive from repository/path, while
legacy KN and experiment identifiers remain aliases with repository scope.

## Hybrid retrieval

SQLite lexical lookup works immediately with no model downloads. For hybrid:

```sh
export RESEARCH_KB_QDRANT_URL=http://127.0.0.1:6333
research-kb index
research-kb search "summation polynomials" --mode hybrid
```

The database must already be running; Compose's operator container uses the
private `http://qdrant:6333` address. Each build publishes its collection, BM25
statistics and model configuration together. A stale hybrid index returns an
operational error until rebuilt. Lexical search continues to work during rebuilds.
The old collection stays available for investigation; automatic index pruning is
not enabled. `:memory:` is rejected for persistent hybrid builds.

The default dense backend is the original deterministic hashing model. To use a
learned encoder, install the `transformers` extra, explicitly cache a model into
a local directory and set `RESEARCH_KB_DENSE_BACKEND=sentence-transformers`,
`RESEARCH_KB_DENSE_MODEL`, and its matching `RESEARCH_KB_DENSE_DIMENSION` before
rebuilding. Normal searches use local-only model loading and never fetch weights.

## Lean verification

Source discovery preserves scoped variable declarations and explicit hypotheses,
but is labelled `source-only`; it is not an elaborated proof. To compile and audit
a registered Lake project with its own installed toolchain:

```sh
# Freeze/update the project's manifest before refreshing its source inventory.
research-kb refresh
research-kb audit-lean /absolute/path/to/project Module.Name
```

The operator command runs `lake build`, reads the compiled environment and its
transitive axiom dependencies, and attaches receipts only when indexed source
hashes and environment pins still match. Standard foundations are `propext`,
`Classical.choice` and `Quot.sound`. User axioms, `sorry` and compiler-trusting
native proofs produce `nonstandard-axioms`, rather than a standard proof claim.
The receipt includes the exported kernel type, module, source hash and environment.

`export-lean PROJECT MODULE... --output FILE` also exports the compiled catalog
without modifying verification state. The exporter is tested on Lean 4.19.0;
each actual consumer toolchain still needs its own compatibility check. This does
not change a consumer’s pinned dependencies or certify that a report describes
the same mathematical statement.

## Validation and current scope

```sh
python -m pip install -e '.[dev,index,pdf]'
pytest -q
ruff check src/research_kb tests
```

The suite covers cross-repo identity, PDF deduplication/page provenance, immutable
context, supersession, bundle tampering/path traversal, hybrid publication and
staleness, authentication/revocation/rate limits, in-process MCP and real HTTP MCP
with two clients. The Lean compilation test runs when `lake` is installed.

The AWS configuration is validated Terraform and includes a tested container
build. An AWS apply, live DNS/TLS validation and the original local PDF-library
backfill require the operator's actual account, hostname and source files.
The shared service is a single host; high availability is not part of this release.

See [shared agent instructions](docs/AGENT_USAGE.md), [upstream extraction](UPSTREAM.md)
and [AWS deployment](docs/AWS.md).
