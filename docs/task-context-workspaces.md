# Task context and sparse execution workspaces

The harness controls context by choosing which text an agent retrieves. A
shallow clone only shortens history; it still checks out the current files.
Sparse worktrees reduce the working files while sharing the full repository's
Git objects and history. The full checkout remains the place for archival,
repository-wide validation, and checks requiring complete evidence coverage.

## Default behavior in api_direct

Every task is projected into an in-memory context manifest. The original task,
frozen handoff, and historical records are not edited. The projection includes:

- Explicit `context_paths`, literal file paths in `handoff.inputs`, and
  structured inputs such as `{path: src/helper.py}`.
- The source handoff file when it is inside the repository, the compact runtime
  contract, and the selected role's contract.
- The declared `read_scope` and `write_scope`. If a read scope is absent or
  empty, it is derived from the context paths and output scope. An explicit
  `read_scope: ['.']` still permits repository-wide file access. Top-level task
  fields take precedence over nested handoff fields.

Derivation does not scan the ledger or guess paths from record identifiers.
Prose and citations stay in the task brief. List dependencies explicitly when
an input cannot be expressed as a literal repository-relative path.

Default file discovery starts in the task's context and output paths, even
when its declared read scope is wider. A specific repository-relative glob
can retrieve another part of the declared scope. Searches traverse the relevant
roots directly; they do not enumerate the entire repository before filtering.
Default traversal skips Git metadata, nested worktrees, temporary directories,
virtual environments, and dependency caches. A specifically named readable
cache directory can still be inspected; `.git` is not a file-search target.

| Per-call limit | Default |
|---|---:|
| File read | 400 lines and 20,000 UTF-8 bytes |
| File listing | 200 paths |
| Search results | 100 matching lines |
| Search input | 2,000 matching files, 1 MB per file, 8 MB total, plus byte lookahead |
| List, search, or command response | 20,000 UTF-8 bytes |

Larger model-supplied `limit` and `max_lines` values cannot raise these caps.
Administrators can configure them under `api_direct.retrieval_limits` in
`orchestration/roles.yaml`; `max_read_bytes` must be at least 256 so a page can
include text and a continuation cursor. Limits affect retrieval, not research
budgets, sample counts, or scientific stopping rules.

File reads return a `start_line` / `start_column` continuation cursor when
more text remains. Search output explicitly states when coverage is partial
because of limits or unreadable files. Zero matches in partial coverage is not
an exhaustive absence finding. The tool journal records returned byte counts,
search coverage, skipped files, and truncation; the inference receipt records
the effective context, scopes, limits, and optional workspace snapshot.

These file-tool scopes are not a process sandbox: an allow-listed command
has its existing operating-system access. Command outputs are bounded, but
native CLI file tools and their context windows are controlled by the host.
The sparse workspace helper below is available to those runtimes too.

Inspect a task's context and limits without calling a model:

```sh
python3 -m orchestration.agent plan --task /path/to/task.yaml
```

Add a known dependency to a launch projection with repeatable
`--context-path src/dependency.py`. This can extend a derived scope; it cannot
widen an explicitly declared read scope. Scope changes on a frozen task still
use the existing task/amendment process.

## Optional sparse execution

Existing run commands continue to work in their current checkout. Sparse
preparation is opt-in and is supported for executor tasks only. It does not
perform a portfolio audit, create a scientific protocol, grant ownership,
admit an experiment, or bypass a runner's checks.

To prepare a workspace for a native runtime or an existing command runner:

```sh
# Preview the selected paths and source commit; no workspace is created.
python3 -m orchestration.task_workspace plan \
  --repo /path/to/full-repository --task /path/to/task.yaml

# Create a new detached workspace at the chosen snapshot.
python3 -m orchestration.task_workspace prepare \
  --repo /path/to/full-repository --task /path/to/task.yaml \
  --destination /path/to/new-execution-workspace
```

Both commands accept `--revision` (default `HEAD`) and repeatable
`--context-path`. The helper needs Python, PyYAML, and Git, but no agent packages,
API credentials, or model resolution. Launch the existing admitted runner from
the prepared workspace using its existing command and checks.

For api_direct, workspace creation can be part of the launch:

```sh
python3 -m orchestration.agent run \
  --task /path/to/task.yaml \
  --repo /path/to/full-repository \
  --sparse-worktree /path/to/new-execution-workspace \
  --out /path/to/new-run-receipt-directory
```

Workspace selection includes context paths, output scopes, and shared runtime
code/configuration. Optional task or handoff `workspace_paths` lists additional
literal dependency paths, for example a fixture directory. This field controls
materialization only; it does not grant additional file-tool read authority.
Selection uses literal non-cone patterns to avoid loading thousands of sibling
records when only one handoff is needed.

Preparation refuses a shallow source repository, missing required snapshot
paths, existing destinations, repository-wide roles, a root-wide output scope,
or selected source paths with uncommitted changes. Unrelated dirty work is
preserved. It never copies dirty inputs into a supposedly clean snapshot or
changes the main checkout's sparse selection. Ordinary Git checkout filters,
including any configured LFS behavior, remain in effect.

The workspace retains full history for historical `git show` and provenance
checks. Global budget-policy lookups still use the full source repository.
The selected paths, source commit, and read/write scopes are saved in the
worktree's private Git metadata as `harness-context.json`, outside research
artifacts. A failure after worktree creation retains the worktree for diagnosis.

Retrieve a specific dependency already inside the declared read scope:

```sh
python3 -m orchestration.task_workspace expand \
  --workspace /path/to/execution-workspace \
  --path knowledge/techniques/needed-record.md
```

Expansion uses the original pinned commit, adds only the requested path, and
records the addition in workspace metadata. It refuses paths outside the read
scope or a workspace whose HEAD has changed. Use a new prepared workspace for
a new snapshot. Retain output files until the existing archive workflow has
handled them; workspace preparation and expansion do not archive results.

Resume an api_direct task in an existing workspace with `--repo` pointing to
that workspace and the existing checkpoint; do not pass `--sparse-worktree`
again, since that option always creates a new destination. Repository-wide
checks should continue to use the complete repository.
