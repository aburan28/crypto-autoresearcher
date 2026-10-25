# Artifact storage: keeping run outputs small

The tree passed 9 GiB (9.26 GiB on 2026-10-23, 139k files). 1,403 files of
1 MiB or more hold 7.0 GiB of it, nearly all run outputs committed as written:
`raw-result.json`, `stdout.log`, per-curve tables. Text of that kind shrinks
about 5x with gzip (measured on the 1,211 such files: 5.56 → 1.14 GiB), and
1.3 GiB more is byte-identical copies of run files kept again under task
directories. `python3 tools/repo_size.py report` measures the current tree.

Git already compresses what it stores and sends, so a clone downloads ~1.9 GiB,
not 9. The cost is on disk, in every checkout and CI job, and it grows with
every run. Existing records stay as they are (records are immutable, and archive
receipts bind their bytes). What changes is how **new** large artifacts are
stored.

## Stored forms

A run still declares its artifacts by name, and receipts still bind each one's
**content** digest. Beside the declared path, exactly one of these exists:

| form | when | what it is |
| --- | --- | --- |
| `raw-result.json` | under 1 MiB, already compressed, or `manifest.yaml`/`launch.json`/`environment.json`/`command.txt`/`execution-receipt.json` | as written |
| `raw-result.json.gz` | 1 MiB or more | deterministic gzip (no name, mtime 0, level 6) of the same bytes |
| `raw-result.json.gz.blob.json` | still 10 MiB or more compressed, and a blob store is configured | pointer to that gzip in S3 |

A pointer records the object's sha256 and size, the content's sha256 and size,
and its URI, `s3://<bucket>/<prefix>/sha256/<aa>/<sha256>`: content-addressed,
written once, never overwritten.

**Writers.** `tools/experiment_execution.py` compacts every declared artifact
after the frozen checker has read the outputs as written, and before it writes
the receipt. The receipt's `artifact_sha256` keeps binding content; its new
`artifact_storage` map records each artifact's stored form and that form's own
digest. Other producers (task outputs, ports) run the same step before
committing:

```sh
python3 tools/artifact_store.py compact <dir> <name>...
```

**Readers** never care which form is on disk:

```python
import artifact_store                    # tools/artifact_store.py
data = artifact_store.read_json(run_dir / "raw-result.json")   # any form
```

```sh
python3 tools/artifact_store.py cat experiments/<EXP>/runs/<RUN>/raw-result.json
python3 tools/artifact_store.py verify <path>...      # stored form matches its content digest
python3 tools/artifact_store.py hash <path>...        # stored file's sha256, for archive path_sha256
```

A pointer's object is downloaded on first read into
`~/.cache/crypto-autoresearcher/blobs` (or `CRYPTO_AR_BLOB_CACHE`) and checked
against its sha256 before use; a mismatch is an error, never served.

**Checkers.** `tools/validate_ledger.py` accepts any one stored form for a
required run artifact. `tools/research_dispatch.py` maps a stored form back to
its declared path, and an archive's `path_sha256` binds the stored bytes git
holds (`artifact_store.py hash` prints them). Two stored forms of one path are
an error: which one would a receipt mean?

## The PR gate

`tools/repo_size.py check --base <sha>` runs in `validate` / `static-checks`.
On files a PR adds it refuses:

- **uncompressed**: 1 MiB or more, not already a compressed format;
- **duplicate**: 1 MiB or more, byte-identical to a tracked file or to another
  file the PR adds; reference the existing path instead;
- **pointer**: a `*.blob.json` that is not a well-formed pointer into S3 (a
  `file://` object exists only on its author's machine);

and on files added or changed, anything 50 MiB or more (GitHub warns at 50 MB
and refuses 100 MB). Each error names the command that fixes it. An exemption is
a line `<glob>  # <reason>` in `.github/size-exemptions.txt`, reviewed like any
change. Replayed on the 80 PRs merged before it landed, the gate would have
failed 7, all for new uncompressed files, 38 MiB in all; most were run outputs
the executor now compresses itself.

## S3

The blob store uses the same bucket and prefix as the artifact store
(`docs/artifacts.md`): `s3://setec-astronomy-artifacts/store`, region
`us-east-2`. Reports live in the same bucket under `reports/<repository>/`
(`docs/reports-s3.md`); the two never share a prefix. Set it wherever large runs
are produced (EC2 and RunPod hosts, a workstation):

```sh
export CRYPTO_AR_BLOBSTORE=s3://setec-astronomy-artifacts/store
export ARTIFACTS_AWS_REGION=us-east-2
pip install boto3          # credentials: ARTIFACTS_AWS_ACCESS_KEY_ID/_SECRET, or the usual AWS chain
```

The bucket layout, the writer/reader rule and the legacy-bucket freeze are stated
once in [`docs/lab-contract.md`](lab-contract.md), section 4.

Unset, nothing is offloaded: artifacts are only compressed, and one still 50 MiB
or more after compression fails the gate until it is offloaded. If an upload
fails, the `.gz` stays and the receipt records `offload_error`.

Writers need `s3:PutObject`, `s3:GetObject` and `s3:ListBucket` (so a missing
object reads as 404); readers need `s3:GetObject`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {"Effect": "Allow", "Action": ["s3:PutObject", "s3:GetObject"],
     "Resource": "arn:aws:s3:::crypto-autoresearcher/blobs/crypto-autoresearcher/*"},
    {"Effect": "Allow", "Action": "s3:ListBucket",
     "Resource": "arn:aws:s3:::crypto-autoresearcher",
     "Condition": {"StringLike": {"s3:prefix": "blobs/crypto-autoresearcher/*"}}}
  ]
}
```

The [`blobstore` workflow](../.github/workflows/blobstore.yml) runs on each push
to `main` that adds pointers and confirms every object exists at its recorded
size (`artifact_store.py check-remote`). It assumes `vars.BLOBSTORE_S3_ROLE_ARN`
through GitHub OIDC (trust policy as in `docs/reports-s3.md`, read-only
`s3:GetObject` is enough), or uses the `AWS_ACCESS_KEY_ID` /
`AWS_SECRET_ACCESS_KEY` secrets. With neither it posts a notice and checks
nothing.

A session without read credentials can still run everything that does not read
an offloaded artifact; only artifacts 10 MiB or more after compression are
offloaded, and only where a producer configured the store.

## Not done, on purpose

- **Existing records are not recompressed.** Records are immutable and receipts
  bind their exact bytes. Sparse checkouts already leave 3.5 GiB of the large
  files off disk (`docs/sparse-checkout.md`).
- **History is not rewritten.** Rewriting would break every archive receipt that
  binds a commit; a full clone keeps carrying old objects.
- **No database for raw outputs.** A database helps query metrics (ecbench has
  one); it does not make a raw output smaller than gzip does.
- **Not Git LFS.** GitHub bills LFS storage and bandwidth on every clone and CI
  checkout; the S3 store fetches an object only when something reads it.
