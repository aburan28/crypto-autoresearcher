#!/usr/bin/env python3
"""Keep large run artifacts small on disk and out of git, without losing a digest.

A run declares its artifacts by name (`raw-result.json`, `stdout.log`, ...), and
receipts bind each one's content digest. Most of the repository's 9 GiB is such
artifacts, and most of that is text that gzip shrinks about 5x
(docs/artifact-storage.md). So a declared artifact may be *stored* in one of
three forms, always beside where its name says:

    raw-result.json                 as written
    raw-result.json.gz              deterministic gzip of the same bytes
    raw-result.json.gz.blob.json    pointer to that gzip in the blob store

A pointer records the stored object's sha256 and size, the content's sha256 and
size, and the object's URI under `<store>/sha256/<aa>/<sha256>`. The digest a
receipt binds is always the *content's*: how an artifact is stored is a
transport detail, checked by its own digest, never a new result.

Readers never care which form is on disk: `resolve()` finds it and
`open_artifact()`/`read_bytes()` return the content, fetching a pointer's object
into a local cache (verifying its digest) on first use.

    python3 tools/artifact_store.py compact DIR NAME...   # store large NAMEs compressed / offloaded
    python3 tools/artifact_store.py cat PATH              # content of a logical path, any form
    python3 tools/artifact_store.py hash PATH             # sha256 of the stored file (archive path_sha256)
    python3 tools/artifact_store.py fetch POINTER...      # download pointers' objects into the cache
    python3 tools/artifact_store.py verify PATH...        # every stored form matches its content digest

The store is CRYPTO_AR_BLOBSTORE: `s3://bucket/prefix` (boto3, the ambient AWS
credentials) or `file:///dir` (tests, offline mirrors). Unset, nothing is
offloaded; artifacts are only compressed. Objects are content-addressed and
written once: an existing object is never overwritten.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import IO, Any, Iterable
from urllib.parse import urlparse

COMPRESS_MIN = 1 << 20          # compress a declared artifact of 1 MiB or more
OFFLOAD_MIN = 10 << 20          # offload one still 10 MiB or more once compressed
GZ = ".gz"
POINTER = ".blob.json"
POINTER_SCHEMA = "crypto.autoresearch.blob_pointer.v1"
# Records a reviewer reads first stay as written, whatever their size.
KEEP_AS_WRITTEN = frozenset({"manifest.yaml", "launch.json", "execution-receipt.json",
                             "environment.json", "command.txt"})
# Leading bytes of formats that are already compressed; gzip would only add a header.
COMPRESSED_MAGIC = (b"\x1f\x8b", b"\x28\xb5\x2f\xfd", b"\xfd7zXZ\x00", b"BZh", b"PK\x03\x04",
                    b"\x89PNG", b"\xff\xd8\xff", b"%PDF")
CHUNK = 1 << 20


class StoreError(ValueError):
    """A stored form that does not match its digest, or a store that cannot serve it."""


def sha256_file(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def already_compressed(path: Path) -> bool:
    with path.open("rb") as stream:
        head = stream.read(8)
    return any(head.startswith(magic) for magic in COMPRESSED_MAGIC)


def gzip_deterministic(source: Path, target: Path) -> None:
    """The same bytes always give the same .gz: no name, no mtime, fixed level."""
    with source.open("rb") as raw, target.open("xb") as out:
        with gzip.GzipFile(filename="", mode="wb", compresslevel=6, fileobj=out, mtime=0) as gz:
            shutil.copyfileobj(raw, gz, CHUNK)


def gunzip_digest(path: Path) -> tuple[str, int]:
    digest, size = hashlib.sha256(), 0
    with gzip.open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


# ---------------------------------------------------------------- blob stores

class FileStore:
    """A directory laid out like the S3 store: for tests and offline mirrors."""

    def __init__(self, root: Path):
        self.root = root
        self.base = root.as_uri()

    def uri(self, sha: str) -> str:
        return f"{self.base}/sha256/{sha[:2]}/{sha}"

    def _path(self, uri: str) -> Path:
        if not uri.startswith(self.base + "/"):
            raise StoreError(f"{uri} is not in {self.base}")
        return self.root / uri[len(self.base) + 1:]

    def put(self, path: Path, sha: str) -> str:
        uri = self.uri(sha)
        target = self._path(uri)
        if target.exists():                      # content-addressed: same digest, same bytes
            return uri
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp:
            shutil.copyfile(path, tmp.name)
        os.replace(tmp.name, target)
        return uri

    def get(self, uri: str, dest: Path) -> None:
        shutil.copyfile(self._path(uri), dest)


class S3Store:
    """`s3://bucket/prefix`, through boto3 and the ambient AWS credentials."""

    def __init__(self, bucket: str, prefix: str, client: Any = None):
        self.bucket, self.prefix = bucket, prefix.strip("/")
        self._client = client

    @property
    def client(self) -> Any:
        if self._client is None:
            try:
                import boto3
            except ImportError as error:
                raise StoreError("the S3 blob store needs boto3 (pip install boto3)") from error
            self._client = boto3.client("s3")
        return self._client

    def key(self, sha: str) -> str:
        return "/".join(p for p in (self.prefix, "sha256", sha[:2], sha) if p)

    def uri(self, sha: str) -> str:
        return f"s3://{self.bucket}/{self.key(sha)}"

    def put(self, path: Path, sha: str) -> str:
        key = self.key(sha)
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return self.uri(sha)                 # written once, never overwritten
        except Exception as error:               # botocore's ClientError; absent is 404
            code = str(getattr(error, "response", {}).get("Error", {}).get("Code", ""))
            if code not in {"404", "NoSuchKey", "NotFound"}:
                raise StoreError(f"cannot check s3://{self.bucket}/{key}: {error}") from error
        self.client.upload_file(str(path), self.bucket, key,
                                ExtraArgs={"ChecksumAlgorithm": "SHA256",
                                           "Metadata": {"sha256": sha}})
        return self.uri(sha)

    def get(self, uri: str, dest: Path) -> None:
        self.client.download_file(self.bucket, self._key_of(uri), str(dest))

    def head(self, uri: str) -> int:
        """The stored object's size, without downloading it."""
        return int(self.client.head_object(Bucket=self.bucket, Key=self._key_of(uri))["ContentLength"])

    def _key_of(self, uri: str) -> str:
        parsed = urlparse(uri)
        if parsed.scheme != "s3" or parsed.netloc != self.bucket:
            raise StoreError(f"{uri} is not in s3://{self.bucket}")
        return parsed.path.lstrip("/")


def store_for(url: str | None, client: Any = None) -> FileStore | S3Store | None:
    if not url:
        return None
    parsed = urlparse(url)
    if parsed.scheme == "s3" and parsed.netloc:
        return S3Store(parsed.netloc, parsed.path, client)
    if parsed.scheme == "file":
        return FileStore(Path(parsed.path))
    raise StoreError(f"unsupported blob store {url!r}: use s3://bucket/prefix or file:///dir")


def store_from_env() -> FileStore | S3Store | None:
    return store_for(os.environ.get("CRYPTO_AR_BLOBSTORE"))


def store_for_uri(uri: str) -> FileStore | S3Store:
    """The store that can serve a pointer's URI, whatever the current default is."""
    parsed = urlparse(uri)
    if parsed.scheme == "s3":
        configured = store_from_env()
        if isinstance(configured, S3Store) and configured.bucket == parsed.netloc:
            return configured
        return S3Store(parsed.netloc, "")
    if parsed.scheme == "file":
        sha_dir = Path(parsed.path).parents[2]    # <root>/sha256/<aa>/<sha>
        return FileStore(sha_dir)
    raise StoreError(f"unsupported blob URI {uri!r}")


def cache_dir() -> Path:
    root = os.environ.get("CRYPTO_AR_BLOB_CACHE")
    return Path(root) if root else Path.home() / ".cache" / "crypto-autoresearcher" / "blobs"


# ---------------------------------------------------------------- stored forms

def candidates(path: Path) -> list[Path]:
    """Every stored form of a logical path, most direct first."""
    return [path, path.with_name(path.name + GZ), path.with_name(path.name + POINTER),
            path.with_name(path.name + GZ + POINTER)]


def resolve(path: str | os.PathLike[str]) -> Path | None:
    """The one stored form of a logical artifact path that exists, or None.

    Two forms at once is ambiguous -- which one did a receipt bind? -- and an error.
    """
    found = [p for p in candidates(Path(path)) if p.is_file()]
    if len(found) > 1:
        raise StoreError(f"{path} is stored more than once: {', '.join(p.name for p in found)}")
    return found[0] if found else None


def logical_candidates(path: str) -> list[str]:
    """Every declared path this stored path could be a form of, itself first.

    `x.gz.blob.json` is the offloaded gzip of `x` or the offloaded `x.gz`, so
    the caller picks the one that was declared.
    """
    out = [path]
    for suffix in (GZ, POINTER, GZ + POINTER):
        if path.endswith(suffix) and len(path) > len(suffix):
            out.append(path[: -len(suffix)])
    return out


def logical(path: str, declared: Iterable[str]) -> str | None:
    """The one declared path `path` stores, or None."""
    declared = set(declared)
    hits = [c for c in logical_candidates(path) if c in declared]
    return hits[0] if len(hits) == 1 else None


def read_pointer(path: Path) -> dict[str, Any]:
    pointer = json.loads(path.read_text(encoding="utf-8"))
    if pointer.get("schema") != POINTER_SCHEMA:
        raise StoreError(f"{path}: not a {POINTER_SCHEMA} pointer")
    for field in ("sha256", "size", "encoding", "content_sha256", "content_size", "uri"):
        if field not in pointer:
            raise StoreError(f"{path}: pointer lacks {field}")
    return pointer


def fetch(pointer_path: Path) -> Path:
    """The pointer's object in the local cache, downloaded and verified on first use."""
    pointer = read_pointer(pointer_path)
    target = cache_dir() / "sha256" / pointer["sha256"][:2] / pointer["sha256"]
    if target.is_file() and sha256_file(target) == pointer["sha256"]:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp:
        partial = Path(tmp.name)
    try:
        store_for_uri(pointer["uri"]).get(pointer["uri"], partial)
        if sha256_file(partial) != pointer["sha256"]:
            raise StoreError(f"{pointer['uri']} does not match {pointer_path}'s sha256")
        os.replace(partial, target)
    finally:
        partial.unlink(missing_ok=True)
    return target


def open_artifact(path: str | os.PathLike[str]) -> IO[bytes]:
    """The content of a logical artifact path, whichever stored form is on disk."""
    stored = resolve(path)
    if stored is None:
        raise FileNotFoundError(str(path))
    if stored.name.endswith(POINTER):
        pointer = read_pointer(stored)
        blob = fetch(stored)
        return gzip.open(blob, "rb") if pointer["encoding"] == "gzip" else blob.open("rb")
    if stored.name.endswith(GZ) and stored != Path(path):
        return gzip.open(stored, "rb")
    return stored.open("rb")


def read_bytes(path: str | os.PathLike[str]) -> bytes:
    with open_artifact(path) as stream:
        return stream.read()


def read_text(path: str | os.PathLike[str], encoding: str = "utf-8") -> str:
    return read_bytes(path).decode(encoding)


def read_json(path: str | os.PathLike[str]) -> Any:
    return json.loads(read_bytes(path))


def exists(path: str | os.PathLike[str]) -> bool:
    return resolve(path) is not None


def content_digest(path: str | os.PathLike[str]) -> str:
    """sha256 of the content of a logical path; for a pointer, its recorded digest."""
    stored = resolve(path)
    if stored is None:
        raise FileNotFoundError(str(path))
    if stored.name.endswith(POINTER):
        return read_pointer(stored)["content_sha256"]
    if stored.name.endswith(GZ) and stored != Path(path):
        return gunzip_digest(stored)[0]
    return sha256_file(stored)


# ---------------------------------------------------------------- compaction

def _offload(store: FileStore | S3Store, stored: Path, encoding: str,
             content_sha: str, content_size: int) -> Path:
    sha = sha256_file(stored)
    uri = store.put(stored, sha)
    pointer = stored.with_name(stored.name + POINTER)
    with pointer.open("x", encoding="utf-8") as stream:
        json.dump({"schema": POINTER_SCHEMA, "sha256": sha, "size": stored.stat().st_size,
                   "encoding": encoding, "content_sha256": content_sha,
                   "content_size": content_size, "uri": uri}, stream, indent=1, sort_keys=True)
        stream.write("\n")
    stored.unlink()
    return pointer


def compact(directory: Path, names: Iterable[str], store: FileStore | S3Store | None = None, *,
            compress_min: int | None = None, offload_min: int | None = None) -> dict[str, dict]:
    """Store each large named artifact compressed, and offload the largest.

    Returns {name: entry} for every artifact whose stored form changed; an entry
    gives the stored path (relative to `directory`), its encoding, the stored
    file's sha256 and size, and the content's sha256 and size. A name not
    returned is stored as written. Each step is checked before the original is
    removed: the gzip must decompress to the original's digest.
    """
    compress_min = COMPRESS_MIN if compress_min is None else compress_min
    offload_min = OFFLOAD_MIN if offload_min is None else offload_min
    entries: dict[str, dict] = {}
    for name in names:
        source = directory / name
        if name in KEEP_AS_WRITTEN or not source.is_file() or source.is_symlink():
            continue
        size = source.stat().st_size
        if size < compress_min:
            continue
        content_sha = sha256_file(source)
        if already_compressed(source):
            stored, encoding = source, "identity"
        else:
            stored, encoding = source.with_name(source.name + GZ), "gzip"
            if stored.exists():
                raise StoreError(f"{stored} exists; refusing to overwrite a stored form")
            gzip_deterministic(source, stored)
            if gunzip_digest(stored) != (content_sha, size):
                stored.unlink()
                raise StoreError(f"{stored} does not round-trip to {source}")
            source.unlink()
        entry = {"path": stored.relative_to(directory).as_posix(), "encoding": encoding,
                 "sha256": sha256_file(stored), "size": stored.stat().st_size,
                 "content_sha256": content_sha, "content_size": size}
        if store is not None and entry["size"] >= offload_min:
            try:
                pointer = _offload(store, stored, encoding, content_sha, size)
            except Exception as error:      # no credentials, no network: keep the local form
                entry["offload_error"] = f"{type(error).__name__}: {error}"
            else:
                entry["path"] = pointer.relative_to(directory).as_posix()
                entry["uri"] = read_pointer(pointer)["uri"]
        if entry["path"] != name:
            entries[name] = entry
    return entries


def stored_matches(directory: Path, name: str, entry: dict[str, Any], content_sha: str) -> bool:
    """A receipt's storage entry still describes what is on disk, without downloading."""
    if entry.get("content_sha256") != content_sha:
        return False
    stored = directory / entry["path"]
    if not stored.is_file() or entry["path"] not in {c.as_posix() for c in candidates(Path(name))}:
        return False
    if stored.name.endswith(POINTER):
        pointer = read_pointer(stored)
        return pointer["sha256"] == entry["sha256"] and pointer["content_sha256"] == content_sha
    return sha256_file(stored) == entry["sha256"]


def verify(path: Path) -> str:
    """Check one stored form end to end; returns the content digest."""
    stored = path if path.is_file() else resolve(path)
    if stored is None:
        raise FileNotFoundError(str(path))
    if stored.name.endswith(POINTER):
        pointer = read_pointer(stored)
        blob = fetch(stored)
        content = (gunzip_digest(blob) if pointer["encoding"] == "gzip"
                   else (sha256_file(blob), blob.stat().st_size))
        if content != (pointer["content_sha256"], pointer["content_size"]):
            raise StoreError(f"{stored}: object content does not match its content digest")
        return content[0]
    if stored.name.endswith(GZ):
        return gunzip_digest(stored)[0]
    return sha256_file(stored)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("compact", help="store large named artifacts compressed / offloaded")
    p.add_argument("directory", type=Path)
    p.add_argument("names", nargs="+")
    p.add_argument("--no-offload", action="store_true", help="compress only, even with a store set")
    p = sub.add_parser("cat", help="write a logical path's content to stdout")
    p.add_argument("path", type=Path)
    p = sub.add_parser("hash", help="sha256 of the stored file a logical path resolves to")
    p.add_argument("paths", type=Path, nargs="+")
    p = sub.add_parser("fetch", help="download pointers' objects into the cache")
    p.add_argument("pointers", type=Path, nargs="+")
    p = sub.add_parser("verify", help="check stored forms against their content digests")
    p.add_argument("paths", type=Path, nargs="+")
    p = sub.add_parser("check-remote", help="each pointer's object exists in S3 at its recorded size")
    p.add_argument("pointers", type=Path, nargs="+")
    args = parser.parse_args(argv)
    try:
        if args.command == "compact":
            store = None if args.no_offload else store_from_env()
            print(json.dumps(compact(args.directory, args.names, store), indent=1, sort_keys=True))
        elif args.command == "cat":
            with open_artifact(args.path) as stream:
                shutil.copyfileobj(stream, sys.stdout.buffer, CHUNK)
        elif args.command == "hash":
            for path in args.paths:
                stored = resolve(path)
                if stored is None:
                    raise FileNotFoundError(str(path))
                print(f"{sha256_file(stored)}  {stored}")
        elif args.command == "fetch":
            for pointer in args.pointers:
                print(fetch(pointer))
        elif args.command == "check-remote":
            bad = 0
            for path in args.pointers:
                pointer = read_pointer(path)
                remote = store_for_uri(pointer["uri"])
                if not isinstance(remote, S3Store):
                    print(f"::error file={path}::object {pointer['uri']} is not in S3")
                    bad += 1
                    continue
                try:
                    size = remote.head(pointer["uri"])
                except Exception as error:      # absent, or unreadable with these credentials
                    print(f"::error file={path}::{pointer['uri']}: {type(error).__name__}: {error}")
                    bad += 1
                    continue
                if size != pointer["size"]:
                    print(f"::error file={path}::{pointer['uri']} is {size} bytes, pointer says {pointer['size']}")
                    bad += 1
                else:
                    print(f"ok  {path}")
            return 1 if bad else 0
        else:
            for path in args.paths:
                print(f"{verify(path)}  {path}")
    except (OSError, StoreError, ValueError) as error:
        print(f"artifact_store: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
