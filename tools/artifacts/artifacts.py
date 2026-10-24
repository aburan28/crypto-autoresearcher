#!/usr/bin/env python3
"""Keep data files out of Git: bytes in S3, a small manifest in the repository.

A data file (run output, relation table, raw log, compressed archive, ...)
lives in object storage under its SHA-256. The directory that holds it keeps
a tracked `.artifacts.json` naming the file, its digest and its size, and a
managed block in its `.gitignore` so the hydrated copy is never committed
again. A checkout, CI job or worker that needs the bytes runs `pull` for the
paths it reads; every download is hashed against the manifest before it is
placed.

The object layout is the one `crypto store` uses (`<prefix>/sha256/ab/<hex>`,
write-once, checksum-verified), in the same bucket, so the three research
repositories and `crypto store` share objects and a local cache.

    artifacts.py status
    artifacts.py plan [PATH ...]            tracked files the policy would move
    artifacts.py push PATH ... [--dry-run]  move files (or matching files under dirs) to the store
    artifacts.py pull [PATH ...]            hydrate files listed under PATH (default: everything)
    artifacts.py verify [PATH ...] [--remote]
    artifacts.py ls [PATH ...]
    artifacts.py check BASE [HEAD]          PR gate: added/modified tracked files that belong in the store

Stdlib only; transport is the `aws` CLI (credentials, SSO, retries are the
CLI's), a `file://` directory, or a read-only `https://` base URL. See
docs/artifacts.md.
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import fnmatch
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

MANIFEST = ".artifacts.json"
MANIFEST_SCHEMA = "artifacts.manifest/v1"
CONFIG = ".artifacts/config.json"
BEGIN = "# >>> artifacts: managed by tools/artifacts; bytes live in the store (see .artifacts.json)"
END = "# <<< artifacts"
SINGLE_PUT_MAX = 4 << 30

# Files the policy never moves: source, build and config text. A data file
# with one of these suffixes is rare and is better split or renamed.
CODE_EXT = {
    ".rs", ".py", ".pyi", ".toml", ".lock", ".yml", ".yaml", ".sh", ".bash", ".md",
    ".rst", ".lean", ".sage", ".spyx", ".c", ".h", ".cc", ".cpp", ".hpp", ".cu",
    ".cuh", ".metal", ".js", ".mjs", ".ts", ".tsx", ".css", ".html", ".tex",
    ".bib", ".cfg", ".ini", ".mk", ".cmake", ".go", ".swift", ".m", ".gp",
    ".mag", ".sql", ".nix", ".ipynb", ".v", ".sv", ".tcl", ".xdc", ".json5",
}
DATA_EXT = {
    ".jsonl", ".ndjson", ".gz", ".zst", ".xz", ".bz2", ".lz4", ".tar", ".zip", ".7z",
    ".npy", ".npz", ".pkl", ".pickle", ".h5", ".hdf5", ".parquet", ".arrow",
    ".feather", ".bin", ".dat", ".raw", ".rsp", ".csv", ".tsv", ".log", ".out",
    ".stdout", ".stderr", ".trace", ".prof", ".perf", ".png", ".jpg", ".jpeg",
    ".gif", ".webp", ".pdf", ".svgz", ".sqlite", ".db", ".dylib", ".so", ".a",
    ".o", ".exe", ".wasm", ".safetensors", ".pt", ".onnx", ".ckpt",
}

DEFAULT_POLICY = {
    # Any non-code file larger than this goes to the store.
    "max_bytes": 1 << 20,
    # A data-suffixed file (DATA_EXT, `.part-NNNN`) larger than this does too.
    "data_min_bytes": 64 << 10,
    # Glob patterns (repository-relative) that stay in Git whatever their size.
    "keep": [],
}


def die(msg: str, code: int = 2) -> None:
    print(f"artifacts: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------------------
# Repository, configuration, policy


def git(root: Path, *args: str, input: bytes | None = None) -> bytes:
    p = subprocess.run(["git", "-C", str(root), *args], input=input, capture_output=True)
    if p.returncode != 0:
        die(f"git {' '.join(args[:3])}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout


def repo_root() -> Path:
    p = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if p.returncode != 0:
        die("not inside a git repository")
    return Path(p.stdout.strip())


@dataclass
class Config:
    root: Path
    remote: str
    endpoint: str | None
    read_url: str | None
    cache: Path
    aws: str
    policy: dict = field(default_factory=dict)

    @classmethod
    def load(cls, root: Path) -> "Config":
        raw: dict = {}
        cfg_path = root / CONFIG
        if cfg_path.exists():
            raw = json.loads(cfg_path.read_text())
        policy = dict(DEFAULT_POLICY)
        policy.update(raw.get("policy", {}))
        env = os.environ
        cache = env.get("ARTIFACTS_CACHE") or env.get("CRYPTO_STORE_CACHE")
        if not cache:
            xdg = env.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
            cache = str(Path(xdg) / "crypto-store")
        return cls(
            root=root,
            remote=env.get("ARTIFACTS_REMOTE") or raw.get("remote", ""),
            endpoint=env.get("ARTIFACTS_ENDPOINT") or raw.get("endpoint"),
            read_url=env.get("ARTIFACTS_READ_URL") or raw.get("read_url"),
            cache=Path(cache),
            aws=env.get("ARTIFACTS_AWS", "aws"),
            policy=policy,
        )


def suffix(path: str) -> str:
    name = path.rsplit("/", 1)[-1].lower()
    if ".part-" in name:
        return ".part"
    return os.path.splitext(name)[1]


def belongs_in_store(path: str, size: int, policy: dict) -> bool:
    """The policy: does a tracked file of this path and size belong in the store?"""
    name = path.rsplit("/", 1)[-1]
    if name in (MANIFEST, ".gitignore", ".gitattributes") or path.startswith(".artifacts/"):
        return False
    if any(fnmatch.fnmatchcase(path, pat) for pat in policy.get("keep", [])):
        return False
    ext = suffix(path)
    if ext in CODE_EXT:
        return False
    if size > policy["max_bytes"]:
        return True
    return (ext in DATA_EXT or ext == ".part") and size > policy["data_min_bytes"]


# ---------------------------------------------------------------------------
# Manifests and the managed .gitignore block


def read_text_or_index(p: Path) -> str | None:
    """A file's text, or its staged copy when a sparse checkout left it off disk."""
    if p.exists():
        return p.read_text()
    r = subprocess.run(["git", "-C", str(p.parent if p.parent.exists() else repo_root()), "show",
                        f":{rel(repo_root(), p)}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def read_manifest(d: Path) -> dict[str, dict]:
    p = d / MANIFEST
    text = read_text_or_index(p)
    if text is None:
        return {}
    data = json.loads(text)
    if data.get("schema") != MANIFEST_SCHEMA:
        die(f"{p}: unknown schema {data.get('schema')!r}")
    return data["files"]


def write_manifest(d: Path, files: dict[str, dict]) -> None:
    # One entry per line, sorted: concurrent PRs adding files in one
    # directory merge cleanly, and a diff shows exactly which file changed.
    lines = [f'{{\n "schema": "{MANIFEST_SCHEMA}",\n "files": {{']
    items = sorted(files.items())
    for i, (name, e) in enumerate(items):
        comma = "," if i + 1 < len(items) else ""
        entry = json.dumps({"sha256": e["sha256"], "bytes": e["bytes"]})
        lines.append(f"  {json.dumps(name)}: {entry}{comma}")
    lines.append(" }\n}\n")
    (d / MANIFEST).write_text("\n".join(lines))


def gitignore_escape(name: str) -> str:
    out = "".join("\\" + c if c in "*?[]!#\\" else c for c in name)
    if out.endswith(" "):
        out = out[:-1] + "\\ "
    return "/" + out


def write_gitignore(d: Path, names: list[str]) -> None:
    p = d / ".gitignore"
    text = read_text_or_index(p) or ""
    if BEGIN in text:
        head, rest = text.split(BEGIN, 1)
        tail = rest.split(END, 1)[1] if END in rest else ""
        text = head.rstrip("\n") + ("\n" if head.strip() else "") + tail.lstrip("\n")
    block = [BEGIN, *[gitignore_escape(n) for n in sorted(names)], END]
    text = (text.rstrip("\n") + "\n" if text.strip() else "") + "\n".join(block) + "\n"
    p.write_text(text)


def rel(root: Path, p: Path) -> str:
    a = os.path.abspath(p)
    a = os.path.join(os.path.realpath(os.path.dirname(a)), os.path.basename(a))
    r = os.path.relpath(a, os.path.realpath(root))
    return "" if r == "." else r


def all_manifests(root: Path) -> list[Path]:
    """Directories holding a manifest that is tracked or staged."""
    out = git(root, "ls-files", "-z", "--", MANIFEST, f":(glob)**/{MANIFEST}")
    return sorted({(root / f).parent for f in out.decode().split("\0") if f})


def under(path: str, prefix: str) -> bool:
    return not prefix or path == prefix or path.startswith(prefix + "/")


def selected(root: Path, paths: list[Path]) -> list[tuple[Path, str, dict]]:
    """(directory, name, entry) for manifest entries at or below the given paths (all when none)."""
    prefixes = [rel(root, p) for p in paths]
    for raw, pre in zip(paths, prefixes):
        if pre.startswith(".."):
            die(f"{raw}: outside the repository")
    out = []
    for d in all_manifests(root):
        drel = rel(root, d)
        # A manifest can only hold entries for a path at or below its directory,
        # or for a directory below a requested prefix.
        if prefixes and not any(under(drel, p) or under(p, drel) for p in prefixes):
            continue
        for name, e in read_manifest(d).items():
            frel = f"{drel}/{name}" if drel else name
            if not prefixes or any(under(frel, p) for p in prefixes):
                out.append((d, name, e))
    return out


# ---------------------------------------------------------------------------
# Remote: s3:// via the aws CLI, file:// directory, read-only https://


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def object_key(digest: str) -> str:
    if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        die(f"not a sha256 digest: {digest!r}")
    return f"sha256/{digest[:2]}/{digest}"


class Remote:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        r = cfg.remote
        if r.startswith("s3://"):
            self.kind = "s3"
            bucket, _, prefix = r[5:].partition("/")
            self.bucket, self.prefix = bucket, prefix.strip("/")
        elif r.startswith("file://"):
            self.kind = "file"
            self.dir = Path(r[7:])
        elif not r and cfg.read_url:
            self.kind = "http"
        else:
            die(f"no usable remote (set `remote` in {CONFIG} or ARTIFACTS_REMOTE); got {r!r}")

    def key(self, digest: str) -> str:
        k = object_key(digest)
        return f"{self.prefix}/{k}" if self.kind == "s3" and self.prefix else k

    def describe(self) -> str:
        return self.cfg.remote or f"{self.cfg.read_url} (read-only)"

    # aws CLI argument vectors, kept separate so tests can check them.
    def _aws(self, *args: str) -> list[str]:
        extra = ["--endpoint-url", self.cfg.endpoint] if self.cfg.endpoint else []
        return [self.cfg.aws, *args, *extra]

    def head_args(self, digest: str) -> list[str]:
        return self._aws("s3api", "head-object", "--bucket", self.bucket, "--key", self.key(digest),
                         "--checksum-mode", "ENABLED", "--output", "json")

    def put_args(self, digest: str, src: Path) -> list[str]:
        b64 = base64.b64encode(bytes.fromhex(digest)).decode()
        return self._aws("s3api", "put-object", "--bucket", self.bucket, "--key", self.key(digest),
                         "--body", str(src), "--if-none-match", "*", "--checksum-algorithm", "SHA256",
                         "--checksum-sha256", b64, "--output", "json")

    def put_multipart_args(self, digest: str, src: Path) -> list[str]:
        return self._aws("s3", "cp", str(src), f"s3://{self.bucket}/{self.key(digest)}",
                         "--metadata", f"sha256={digest}", "--no-progress", "--only-show-errors")

    def get_args(self, digest: str, dest: Path) -> list[str]:
        return self._aws("s3", "cp", f"s3://{self.bucket}/{self.key(digest)}", str(dest),
                         "--no-progress", "--only-show-errors")

    def _run(self, argv: list[str]) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(argv, capture_output=True, text=True)
        except FileNotFoundError:
            die(f"`{argv[0]}` not found; install the AWS CLI or set ARTIFACTS_AWS")

    def head(self, digest: str) -> int | None:
        """Size of the stored object, or None when absent."""
        if self.kind == "file":
            p = self.dir / object_key(digest)
            return p.stat().st_size if p.exists() else None
        if self.kind == "http":
            req = urllib.request.Request(self._url(digest), method="HEAD")
            try:
                with urllib.request.urlopen(req) as r:
                    return int(r.headers["Content-Length"])
            except urllib.error.HTTPError as e:
                if e.code in (403, 404):
                    return None
                raise
        p = self._run(self.head_args(digest))
        if p.returncode == 0:
            meta = json.loads(p.stdout)
            got = meta.get("ChecksumSHA256")
            if got and "-" not in got and got != base64.b64encode(bytes.fromhex(digest)).decode():
                die(f"{self.key(digest)}: stored checksum {got} does not match its key")
            return int(meta["ContentLength"])
        if "Not Found" in p.stderr or "(404)" in p.stderr or "NoSuchKey" in p.stderr:
            return None
        hint = " (S3 answers 403 for an absent key without s3:ListBucket)" if "403" in p.stderr else ""
        die(f"head-object {self.key(digest)}: {p.stderr.strip()}{hint}")

    def put(self, digest: str, src: Path, size: int) -> bool:
        """Store the object unless present. Returns True when bytes were sent."""
        have = self.head(digest)
        if have is not None:
            if have != size:
                die(f"{self.key(digest)}: remote holds {have} bytes, expected {size}")
            return False
        if self.kind == "http":
            die("the https remote is read-only; pushing needs s3:// or file://")
        if self.kind == "file":
            dest = self.dir / object_key(digest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_name(dest.name + f".tmp{os.getpid()}")
            shutil.copyfile(src, tmp)
            os.replace(tmp, dest)
            return True
        argv = self.put_multipart_args(digest, src) if size > SINGLE_PUT_MAX else self.put_args(digest, src)
        p = self._run(argv)
        if p.returncode != 0:
            if "PreconditionFailed" in p.stderr or "ConditionalRequestConflict" in p.stderr:
                if self.head(digest) == size:  # a concurrent writer stored the same bytes
                    return False
            die(f"upload {self.key(digest)}: {p.stderr.strip()}")
        if size <= SINGLE_PUT_MAX:
            want = base64.b64encode(bytes.fromhex(digest)).decode()
            got = json.loads(p.stdout or "{}").get("ChecksumSHA256")
            if got != want:
                die(f"{self.key(digest)}: S3 reports checksum {got}, expected {want}")
        return True

    def _url(self, digest: str) -> str:
        return self.cfg.read_url.rstrip("/") + "/" + object_key(digest)

    def get(self, digest: str, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if self.kind == "file":
            shutil.copyfile(self.dir / object_key(digest), dest)
            return
        if self.kind == "http" or (self.cfg.read_url and not os.environ.get("ARTIFACTS_NO_READ_URL")):
            try:
                with urllib.request.urlopen(self._url(digest)) as r, open(dest, "wb") as f:
                    shutil.copyfileobj(r, f, 1 << 20)
                return
            except urllib.error.URLError:
                if self.kind == "http":
                    raise
        p = self._run(self.get_args(digest, dest))
        if p.returncode != 0:
            dest.unlink(missing_ok=True)
            die(f"download {self.key(digest)}: {p.stderr.strip()}")


# ---------------------------------------------------------------------------
# Cache: verified, read-only objects shared with `crypto store`


def cache_path(cfg: Config, digest: str) -> Path:
    return cfg.cache / object_key(digest)


def ensure_cached(cfg: Config, remote: Remote, digest: str, size: int) -> Path:
    c = cache_path(cfg, digest)
    if c.exists() and c.stat().st_size == size:
        return c
    (cfg.cache / "tmp").mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=cfg.cache / "tmp")
    os.close(fd)
    tmp = Path(tmp)
    try:
        remote.get(digest, tmp)
        got = sha256_file(tmp)
        if got != digest or tmp.stat().st_size != size:
            die(f"downloaded object {digest[:12]} hashes to {got[:12]} ({tmp.stat().st_size} bytes); refused")
        tmp.chmod(0o444)
        c.parent.mkdir(parents=True, exist_ok=True)
        os.replace(tmp, c)
    finally:
        tmp.unlink(missing_ok=True)
    return c


def cache_insert(cfg: Config, src: Path, digest: str) -> None:
    c = cache_path(cfg, digest)
    if c.exists():
        return
    c.parent.mkdir(parents=True, exist_ok=True)
    (cfg.cache / "tmp").mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=cfg.cache / "tmp")
    os.close(fd)
    place_copy(src, Path(tmp))
    Path(tmp).chmod(0o444)
    os.replace(tmp, c)


def place_copy(src: Path, dest: Path) -> None:
    """Copy-on-write clone where the filesystem has it (APFS, btrfs, XFS), else a copy."""
    dest.unlink(missing_ok=True)
    flag = "-c" if sys.platform == "darwin" else "--reflink=auto"
    p = subprocess.run(["cp", flag, str(src), str(dest)], capture_output=True)
    if p.returncode != 0:
        shutil.copyfile(src, dest)
    dest.chmod(0o644)


# ---------------------------------------------------------------------------
# Commands


def tracked_sizes(root: Path, paths: list[str]) -> list[tuple[str, int]]:
    """(path, size) for tracked blobs at or below the given paths, from HEAD's index."""
    out = git(root, "ls-files", "-s", "-z", "--", *(paths or ["."]))
    entries = []
    for rec in out.decode(errors="surrogateescape").split("\0"):
        if not rec:
            continue
        meta, path = rec.split("\t", 1)
        mode, blob, _ = meta.split()
        if mode == "160000":
            continue
        entries.append((path, blob))
    sizes = git(root, "cat-file", "--batch-check=%(objectsize)", input="\n".join(b for _, b in entries).encode() + b"\n")
    return [(p, int(s)) for (p, _), s in zip(entries, sizes.decode().split())]


def cmd_plan(cfg: Config, args) -> int:
    rels = [rel(cfg.root, Path(p)) or "." for p in args.paths]
    moved = [(p, s) for p, s in tracked_sizes(cfg.root, rels) if belongs_in_store(p, s, cfg.policy)]
    total = sum(s for _, s in tracked_sizes(cfg.root, rels))
    for p, s in sorted(moved, key=lambda x: -x[1])[: args.limit]:
        print(f"{s:>14,}  {p}")
    mb = sum(s for _, s in moved)
    print(f"\n{len(moved)} files, {mb / 1e6:,.1f} MB of {total / 1e6:,.1f} MB tracked would move to the store", file=sys.stderr)
    return 0


def cmd_push(cfg: Config, args) -> int:
    remote = None if args.dry_run else Remote(cfg)
    targets: list[tuple[str, int]] = []
    for raw in args.paths:
        p = Path(raw)
        r = rel(cfg.root, p)
        if p.is_file():
            targets.append((r, p.stat().st_size))  # an explicit file moves regardless of policy
            continue
        tracked = tracked_sizes(cfg.root, [r or "."])
        if not tracked:
            die(f"{raw}: no such file or directory")
        if len(tracked) == 1 and tracked[0][0] == r:
            targets += tracked  # an explicit file outside the sparse checkout
        else:
            targets += [(f, s) for f, s in tracked if belongs_in_store(f, s, cfg.policy)]
    targets = sorted(set(targets))
    if not targets:
        print("nothing to move", file=sys.stderr)
        return 0
    if args.dry_run:
        for f, s in targets:
            print(f"{s:>14,}  {f}")
        print(f"\n{len(targets)} files, {sum(s for _, s in targets) / 1e6:,.1f} MB (dry run)", file=sys.stderr)
        return 0

    def one(item: tuple[str, int]) -> tuple[str, str, int, bool]:
        f, size = item
        path = cfg.root / f
        tmp = None
        if not path.exists():
            # Tracked but not on disk (a sparse checkout): read the committed blob.
            (cfg.cache / "tmp").mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=cfg.cache / "tmp")
            with os.fdopen(fd, "wb") as out:
                subprocess.run(["git", "-C", str(cfg.root), "cat-file", "blob", f":{f}"], stdout=out, check=True)
            path = Path(tmp)
        try:
            digest = sha256_file(path)
            sent = remote.put(digest, path, size)
            cache_insert(cfg, path, digest)
        finally:
            if tmp:
                os.unlink(tmp)
        return f, digest, size, sent

    done: list[tuple[str, str, int, bool]] = []
    with cf.ThreadPoolExecutor(args.jobs) as ex:
        for i, res in enumerate(ex.map(one, targets), 1):
            done.append(res)
            if i % 100 == 0 or i == len(targets):
                print(f"  {i}/{len(targets)} stored", file=sys.stderr)

    by_dir: dict[Path, dict[str, dict]] = {}
    for f, digest, size, _ in done:
        d = (cfg.root / f).parent
        by_dir.setdefault(d, read_manifest(d))[Path(f).name] = {"sha256": digest, "bytes": size}
    for d, files in by_dir.items():
        d.mkdir(parents=True, exist_ok=True)
        write_manifest(d, files)
        write_gitignore(d, list(files))
    tracked = [f for f, *_ in done]
    for i in range(0, len(tracked), 500):
        git(cfg.root, "rm", "--cached", "--sparse", "-q", "--ignore-unmatch", "--", *tracked[i:i + 500])
    git(cfg.root, "add", "--sparse", "--", *[rel(cfg.root, d / n) for d in by_dir for n in (MANIFEST, ".gitignore")])
    sent = sum(1 for *_, s in done if s)
    print(f"moved {len(done)} files ({sum(s for _, _, s, _ in done) / 1e6:,.1f} MB; {sent} uploaded, "
          f"{len(done) - sent} already stored) into {len(by_dir)} manifests; review with `git status` and commit",
          file=sys.stderr)
    return 0


def cmd_pull(cfg: Config, args) -> int:
    items = selected(cfg.root, [Path(p) for p in args.paths])
    todo = []
    for d, name, e in items:
        f = d / name
        if f.exists() and f.stat().st_size == e["bytes"] and (args.fast or sha256_file(f) == e["sha256"]):
            continue
        todo.append((f, e))
    if not todo:
        print(f"{len(items)} files already present", file=sys.stderr)
        return 0
    remote = Remote(cfg)

    def one(item):
        f, e = item
        c = ensure_cached(cfg, remote, e["sha256"], e["bytes"])
        place_copy(c, f)

    with cf.ThreadPoolExecutor(args.jobs) as ex:
        list(ex.map(one, todo))
    print(f"hydrated {len(todo)} files ({sum(e['bytes'] for _, e in todo) / 1e6:,.1f} MB); "
          f"{len(items) - len(todo)} already present", file=sys.stderr)
    return 0


def cmd_verify(cfg: Config, args) -> int:
    items = selected(cfg.root, [Path(p) for p in args.paths])
    remote = Remote(cfg) if args.remote else None
    bad = missing = 0
    for d, name, e in items:
        f = d / name
        if remote is not None:
            have = remote.head(e["sha256"])
            if have != e["bytes"]:
                print(f"REMOTE {'absent' if have is None else f'{have} bytes'}  {rel(cfg.root, f)}")
                bad += 1
        if not f.exists():
            missing += 1
        elif f.stat().st_size != e["bytes"] or sha256_file(f) != e["sha256"]:
            print(f"CHANGED  {rel(cfg.root, f)}")
            bad += 1
    print(f"{len(items)} entries: {len(items) - missing} hydrated, {missing} not pulled, {bad} problems", file=sys.stderr)
    return 1 if bad else 0


def cmd_ls(cfg: Config, args) -> int:
    for d, name, e in selected(cfg.root, [Path(p) for p in args.paths]):
        f = d / name
        state = "present" if f.exists() else "-"
        print(f"{e['bytes']:>14,}  {e['sha256'][:12]}  {state:<7}  {rel(cfg.root, f)}")
    return 0


def cmd_status(cfg: Config, args) -> int:
    items = selected(cfg.root, [])
    present = sum(1 for d, n, _ in items if (d / n).exists())
    print(f"remote   {cfg.remote or '(none)'}{' via ' + cfg.endpoint if cfg.endpoint else ''}")
    if cfg.read_url:
        print(f"read_url {cfg.read_url}")
    print(f"cache    {cfg.cache}")
    print(f"entries  {len(items)} ({sum(e['bytes'] for *_, e in items) / 1e9:,.2f} GB), {present} hydrated")
    return 0


def cmd_check(cfg: Config, args) -> int:
    """Fail when BASE..HEAD adds or grows a tracked file the policy assigns to the store."""
    out = git(cfg.root, "diff", "--raw", "--no-abbrev", "-z", "--no-renames", "--diff-filter=AM", args.base, args.head)
    fields = out.decode(errors="surrogateescape").split("\0")
    offenders = []
    for meta, path in zip(fields[0::2], fields[1::2]):
        if not meta:
            continue
        _, mode, _, blob, _ = meta.lstrip(":").split()
        if mode == "160000":
            continue
        size = int(git(cfg.root, "cat-file", "-s", blob))
        if belongs_in_store(path, size, cfg.policy):
            offenders.append((path, size))
    if not offenders:
        print("artifacts check: no data files committed", file=sys.stderr)
        return 0
    for p, s in offenders:
        print(f"{s:>14,}  {p}")
    print(f"\n{len(offenders)} data file(s) belong in the store, not Git. Move them with\n"
          f"  python3 tools/artifacts/artifacts.py push <file-or-dir>...\n"
          f"and commit the .artifacts.json / .gitignore it writes (docs/artifacts.md).", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="artifacts", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    s = sub.add_parser("plan", help="tracked files the policy would move")
    s.add_argument("paths", nargs="*")
    s.add_argument("--limit", type=int, default=50)
    s = sub.add_parser("push", help="move files to the store")
    s.add_argument("paths", nargs="+")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--jobs", type=int, default=16)
    s = sub.add_parser("pull", help="hydrate files from the store")
    s.add_argument("paths", nargs="*")
    s.add_argument("--jobs", type=int, default=16)
    s.add_argument("--fast", action="store_true", help="trust a present file of the right size")
    s = sub.add_parser("verify")
    s.add_argument("paths", nargs="*")
    s.add_argument("--remote", action="store_true")
    s = sub.add_parser("ls")
    s.add_argument("paths", nargs="*")
    s = sub.add_parser("check", help="PR gate")
    s.add_argument("base")
    s.add_argument("head", nargs="?", default="HEAD")
    args = ap.parse_args(argv)
    cfg = Config.load(repo_root())
    return {
        "status": cmd_status, "plan": cmd_plan, "push": cmd_push, "pull": cmd_pull,
        "verify": cmd_verify, "ls": cmd_ls, "check": cmd_check,
    }[args.cmd](cfg, args)


if __name__ == "__main__":
    sys.exit(main())
