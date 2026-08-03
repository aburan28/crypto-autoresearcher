# S3 source store schema

Layout for `s3://crypto-autoresearcher`, the object store holding external
source documents (papers, preprints, specifications, reference code) that are
too large or too numerous to commit to git.

Implemented by `tools/s3_source_store.py`. This document is the specification;
where the two disagree, the tool is wrong.

## What this store is for, and what it is not

It holds **inputs**. A paper in this bucket is a source that was acquired, not
a result that was established, and nothing here is evidence for or against a
hypothesis on its own (AGENTS.md rules 4 and 6).

The ledger under `ledger/` and the corpus under `knowledge/` remain the source
of truth and stay in git. This store never becomes a second home for records:
no tool reads a research record back from S3, and a bucket outage must never be
able to change what the program believes. The direction of trust is one-way —
git cites S3 by digest, S3 knows nothing about git.

## Why content addressing

The harness's central rule is that records are immutable and corrections
supersede rather than overwrite (AGENTS.md rule 2). A key-per-filename layout
fights that rule: `papers/wesolowski.pdf` can be silently replaced, and every
citation that named it now points at different bytes with nothing in the record
showing it.

So the primary store is **content-addressed** — the key *is* the SHA-256 of the
bytes:

```
blobs/sha256/<aa>/<bb>/<64-hex-digest>
```

This gives four properties for free:

1. **Overwrite is impossible by construction.** Different bytes produce a
   different key. There is no operation that changes what a key means, so no
   audit is needed to prove none happened.
2. **Upload is idempotent.** Re-uploading the same paper is a no-op, so a
   re-run after a partial failure is safe.
3. **Deduplication.** The same paper arriving from arXiv and from a colleague
   is stored once and cited once.
4. **Verification needs no side channel.** The expected digest is the key, so
   a truncated or corrupted download is detectable from the key alone — which
   is exactly the check `tools/build_source_index.py` already performs on the
   copies that live in-repo.

`<aa>/<bb>` are the first two and next two hex characters of the digest. That
spreads writes across 65 536 prefixes so no single partition goes hot, and
keeps any one console listing browsable.

The cost, stated plainly: keys are unreadable to a human. That is what the two
layers below exist to fix.

## Layout

```
s3://crypto-autoresearcher/
├── blobs/sha256/<aa>/<bb>/<digest>      immutable, write-once, content-addressed
├── packages/<PACKAGE-ID>/manifest.json  immutable; what one ingest produced
├── index/by-src/<SRC-ID>.json           alias: source record  → digest
├── index/by-lit/<KN-LIT-ID>.json        alias: literature entry → digest
└── incoming/                            unmanaged drop zone (see below)
```

### `blobs/` — the bytes

Write-once. Every object carries user metadata:

| metadata key | meaning |
|---|---|
| `sha256` | the digest, duplicated out of the key for tooling that reads only metadata |
| `original-filename` | the name the file arrived with, which the key destroys |
| `package` | the ingest package that first introduced this blob |
| `ingested-at` | UTC timestamp of first upload |

A blob is never deleted while any manifest or alias references it.

### `packages/<PACKAGE-ID>/manifest.json` — what one ingest produced

Immutable, one per ingest, and the S3 twin of the `provenance.json` that
`tools/build_source_index.py` already reads. It maps human-meaningful names to
digests:

```json
{
  "schema": "crypto.autoresearch.s3_source_store.v1",
  "package_id": "INBOX-20260802",
  "created_at": "2026-08-02T23:30:00Z",
  "bucket": "crypto-autoresearcher",
  "files": [
    {
      "logical_name": "wesolowski-p13.pdf",
      "sha256": "ab12…",
      "blob_key": "blobs/sha256/ab/12/ab12…",
      "bytes": 812345,
      "content_type": "application/pdf",
      "origin_key": "incoming/wesolowski.pdf",
      "origin_version_id": "3HL4kqtJ…"
    }
  ]
}
```

A re-ingest never edits a manifest — it writes a new package. `origin_key` and
`origin_version_id` record where the bytes came from, so an adoption can be
retraced to the object it read.

### `index/` — resolving a ledger ID to bytes

Rule 6 requires every conclusion to cite record IDs, so a reader holding
`KN-LIT-0421` needs a path to the PDF. These are small JSON pointers:

```json
{"id": "KN-LIT-0421", "sha256": "ab12…", "blob_key": "blobs/sha256/ab/12/ab12…",
 "logical_name": "wesolowski-p13.pdf", "package_id": "INBOX-20260802",
 "recorded_at": "2026-08-02T23:31:00Z", "supersedes": null}
```

Aliases are the one mutable layer, because a correction may need to repoint an
ID at a better scan of the same paper. Repointing writes a new alias whose
`supersedes` names the previous digest, so the change is recorded rather than
silent — and this is why bucket **versioning must be enabled**: it is the
backstop that makes an alias overwrite recoverable.

### `incoming/` — the drop zone

Unmanaged. Files land here by any means (console upload, `aws s3 cp`, a sync
from a laptop) with no naming rules. `s3_source_store.py adopt` reads this
prefix, hashes each object, writes it to `blobs/`, and records a manifest —
after which the originals can be deleted or left alone. Nothing in the harness
cites `incoming/` directly.

## Required bucket configuration

| setting | value | why |
|---|---|---|
| Block Public Access | all four ON | these are third-party papers; several are not redistributable |
| Versioning | Enabled | backstop for the mutable `index/` layer |
| Default encryption | SSE-S3 minimum, SSE-KMS if the org requires it | at-rest baseline |
| Lifecycle | `blobs/` → Glacier Instant Retrieval after 90 days | papers are read rarely after ingestion; IR keeps them millisecond-accessible |
| Object Lock | governance mode on `blobs/` if available | makes write-once an enforced property rather than a convention |

Object Lock can only be enabled at bucket creation. If this bucket predates
that decision, content addressing still makes overwrite meaningless — a
misdirected `PUT` to a blob key can only write bytes that already hash to that
key, which is to say the same bytes.

## Licensing boundary

Papers are third-party copyrighted works. This bucket is private storage for a
research program's own reading, not redistribution. The reuse boundary already
recorded in `inputs/MLKEM-DUAL-SOURCES-20260802/README.md` applies here too:
what gets committed to the public repository is extracted text regions and
hashes, not whole PDFs.

## Relationship to `inputs/`

`tools/s3_source_store.py pull` materialises a package into the layout the
harness already reads:

```
inputs/<PACKAGE>/sources/<name>[.sha256]
inputs/<PACKAGE>/provenance.json
```

`tools/build_source_index.py` then indexes it and recomputes every hash, so a
pulled package is verified locally rather than trusted from S3.

Which files stay in git after that is a judgement call per source, and the
default is: **freeze extracted text, not the PDF.** `SRC-P13-WESOLOWSKI-2026`
is the model — its full text lives in the repository as markdown, so any
session can re-read what a finding rests on, forever, with no bucket access at
all. The PDF stays in S3. A citation backed only by an S3 object is one
bucket-deletion away from being unverifiable, which puts it in the same class
as `SRC-OAI-TEN-PROOFS-2026`: an assertion about a read that happened, not a
checkable receipt for it.
