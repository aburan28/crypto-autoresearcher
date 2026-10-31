# Data files in the artifact store

Run output, relation tables, raw logs and archives live in object storage
under their SHA-256. Git keeps a small manifest next to them. A checkout only
carries the bytes it asks for, so `actions/checkout` stays small and CI stops
failing with "unable to write file".

Owner decision (2026-10-24): data moves out of Git to
`s3://setec-astronomy-artifacts`. History is not rewritten; CI fetches with
`filter: blob:none`, so old blobs cost nothing.

## What lives where

| piece | where |
|:--|:--|
| data bytes | `s3://setec-astronomy-artifacts/store/sha256/ab/<hex>`, write-once, same layout as `crypto store` |
| manifest | `.artifacts.json` in the data's directory, tracked: name -> `sha256`, `bytes` |
| ignore rule | a managed block in that directory's `.gitignore`, so a hydrated file is never committed again |
| policy and remote | `.artifacts/config.json` |
| tool | `tools/artifacts/artifacts.py` (stdlib only; transport is the `aws` CLI) |
| cache | `~/.cache/crypto-store`, shared with `crypto store` (`ARTIFACTS_CACHE` or `CRYPTO_STORE_CACHE` override it) |

`tools/artifacts/` is a copy of the tool in the `crypto` repository; change it
there and copy it, never fork it. It is separate from `tools/artifact_store.py`
(gzip form and `.blob.json` pointers for new run artifacts,
[artifact-storage.md](artifact-storage.md)); the two coexist, and receipts keep
binding content digests either way.

## Quick start

```bash
python3 tools/artifacts/artifacts.py status                 # config, cache, remote, counts
python3 tools/artifacts/artifacts.py pull research/x        # hydrate what you read (default: everything)
python3 tools/artifacts/artifacts.py push research/x/out    # instead of git add for data
git add research/x/out/.artifacts.json research/x/out/.gitignore
python3 tools/artifacts/artifacts.py verify [PATH] [--remote]
python3 tools/artifacts/artifacts.py ls [PATH]
```

Pull before you read data; every download is hashed against the manifest
before it is placed. `push PATH --dry-run` shows what would move; `push` on a
directory moves the files under it that the policy selects.

Policy (`.artifacts/config.json`, `policy`): a tracked non-code file larger
than 1 MiB goes to the store; a data-suffixed file (`.jsonl`, `.gz`, `.npy`,
`.csv`, `.log`, `.part-NNNN`, and the rest of `DATA_EXT`) larger than 64 KiB
does too. Source, build and config text (`CODE_EXT`) never moves, and PDFs
(`GIT_EXT`) stay in Git at any size. `policy.keep` lists globs that stay in Git whatever their size: data files that code or CI
outside the data trees name by path (inputs PDFs, `knowledge/sources.json`,
`knowledge/leads/ecdlp/coverage.tsv` (read by `tools/lead_atlas.py --check`),
`research_digest/manifest.jsonl`, two experiment summaries) and the generated
`ledger/.index/*.jsonl`.

`artifacts.py plan [PATH ...]` lists the tracked files the policy would move;
`artifacts.py check BASE [HEAD]` is the PR gate: it fails on added or modified
tracked files that belong in the store.

## CI

- `.github/workflows/artifacts.yml` runs the tool's tests, `check HEAD^1 HEAD`
  and `wire_workflows.py --check` on every pull request. The `large-file-ok`
  label turns the check into a warning.
- A workflow that reads moved data needs a pull step after its
  `actions/checkout`. `python3 tools/artifacts/wire_workflows.py` inserts it
  (and adds `tools/artifacts` to a sparse checkout); `--check` fails when one
  is missing.
- Secrets `ARTIFACTS_AWS_ACCESS_KEY_ID` and `ARTIFACTS_AWS_SECRET_ACCESS_KEY`,
  variable `ARTIFACTS_AWS_REGION` (default `us-west-2`). The IAM principal
  needs `s3:GetObject`, `s3:PutObject` and `s3:ListBucket` on
  `setec-astronomy-artifacts/store/*`; read-only jobs need only get and list.
- Checkouts with `fetch-depth: 0` also set `filter: blob:none`.

Never delete remote objects from an agent session. The remote is write-once;
removing an object is a decision for the bucket's owner.

## Migrating existing data

One PR, in this order:

1. `artifacts.py plan` for the summary; `artifacts.py push <dir>` per top-level
   data directory (`experiments/`, `coordination/`, `research/`, `inputs/`,
   `knowledge/`, ...).
2. `artifacts.py verify --remote` over what moved.
3. `wire_workflows.py` to add the pull steps.
4. Commit the manifests, `.gitignore` blocks, deleted data files and workflow
   edits together.

Against `origin/main` with the current keep list, `plan` selects 2982 files,
7,132.9 MB of 8,957.4 MB tracked; the tip tree drops to about 1,824 MB.
Because history is kept, existing clones do not shrink; only checkouts of the
new tip and `blob:none` fetches do.
