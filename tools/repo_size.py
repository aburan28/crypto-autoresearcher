#!/usr/bin/env python3
"""Keep what a pull request adds to the repository small, and say where the bytes are.

The tree grew past 9 GiB, most of it run outputs committed as written: text
that gzip shrinks about 5x, and byte-identical copies of run files kept again
under task directories (docs/artifact-storage.md). `check` refuses a PR that
adds more of either; `report` measures the whole tree.

    python3 tools/repo_size.py check --base BASE_SHA   # CI: what this PR adds
    python3 tools/repo_size.py report [--ref REF]      # where the tree's bytes are

`check` rules, on files the PR adds (A) or changes (M) relative to BASE:

  * too_large      -- A or M, 50 MiB or more as stored. GitHub warns at 50 MB and
                      refuses 100 MB. Offload it: CRYPTO_AR_BLOBSTORE=... python3
                      tools/artifact_store.py compact DIR NAME.
  * uncompressed   -- A, 1 MiB or more, not already a compressed format. Store it
                      compressed: python3 tools/artifact_store.py compact DIR NAME
                      (the executor already does this for trial artifacts).
  * duplicate      -- A, 1 MiB or more, byte-identical to a file BASE tracks or to
                      another file the PR adds. Reference the existing path.
  * pointer        -- A, a `*.blob.json` that is not a well-formed pointer into the
                      shared S3 store: a `file://` object exists only on its author's
                      machine, so nobody else could ever read the artifact.

A path matching a glob in .github/size-exemptions.txt (`<glob>  # <reason>`,
the reason required) is exempt; the exemption is a reviewed change like any
other. Existing files are never re-checked: records are immutable.
"""
from __future__ import annotations

import argparse
import collections
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_store  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
TOO_LARGE = 50 << 20
LARGE = artifact_store.COMPRESS_MIN
EXEMPTIONS = ".github/size-exemptions.txt"
FIX = {
    "too_large": "offload it: CRYPTO_AR_BLOBSTORE=s3://... python3 tools/artifact_store.py compact <dir> <name>",
    "uncompressed": "store it compressed: python3 tools/artifact_store.py compact <dir> <name>",
    "duplicate": "reference the existing path instead of committing a second copy",
    "pointer": "re-run the offload with CRYPTO_AR_BLOBSTORE=s3://crypto-autoresearcher/blobs/...",
}


def pointer_problem(data: bytes) -> str | None:
    """Why an added pointer cannot be committed, or None."""
    try:
        pointer = json.loads(data)
    except ValueError:
        return "not JSON"
    if not isinstance(pointer, dict) or pointer.get("schema") != artifact_store.POINTER_SCHEMA:
        return f"not a {artifact_store.POINTER_SCHEMA} pointer"
    missing = [f for f in ("sha256", "size", "encoding", "content_sha256", "content_size", "uri")
               if f not in pointer]
    if missing:
        return f"missing {', '.join(missing)}"
    sha, uri = str(pointer["sha256"]), str(pointer["uri"])
    if not uri.startswith("s3://"):
        return f"object {uri} is not in the shared S3 store"
    if not uri.endswith(f"/sha256/{sha[:2]}/{sha}"):
        return "object URI is not the content address of its sha256"
    return None


def git(*args: str, repo: Path = REPO) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          stdout=subprocess.PIPE).stdout


def tree(ref: str, repo: Path = REPO) -> dict[str, tuple[str, int]]:
    """path -> (blob sha, size) for every file blob in `ref`."""
    out: dict[str, tuple[str, int]] = {}
    for entry in git("ls-tree", "-r", "-l", "-z", "--full-tree", ref, repo=repo).split(b"\0"):
        if not entry:
            continue
        meta, path = entry.split(b"\t", 1)
        _mode, kind, sha, size = meta.split()
        if kind == b"blob" and size.isdigit():
            out[path.decode()] = (sha.decode(), int(size))
    return out


def changed(base: str, head: str, repo: Path = REPO) -> list[tuple[str, str]]:
    """(status, path) for files added or modified since the merge base."""
    raw = git("diff", "--name-status", "--no-renames", "-z", "--diff-filter=AM",
              f"{base}...{head}", repo=repo).split(b"\0")
    return [(raw[i].decode(), raw[i + 1].decode()) for i in range(0, len(raw) - 1, 2)]


def head_bytes(path: str, sha: str, repo: Path = REPO) -> bytes:
    """The first bytes of a blob: from the work tree when it holds that blob, else git."""
    local = repo / path
    if local.is_file():
        with local.open("rb") as stream:
            return stream.read(8)
    return git("cat-file", "blob", sha, repo=repo)[:8]


def exemptions(repo: Path = REPO) -> list[str]:
    path = repo / EXEMPTIONS
    if not path.is_file():
        return []
    globs = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        glob, _, reason = line.partition("#")
        if not reason.strip():
            raise SystemExit(f"{EXEMPTIONS}:{number}: an exemption needs '# <reason>'")
        globs.append(glob.strip())
    return globs


def check(base: str, head: str = "HEAD", repo: Path = REPO) -> list[tuple[str, str, int, str]]:
    """Violations as (rule, path, size, detail)."""
    head_tree, base_tree = tree(head, repo), tree(base, repo)
    by_sha = collections.defaultdict(list)
    for path, (sha, _size) in base_tree.items():
        by_sha[sha].append(path)
    exempt = exemptions(repo)
    diff = changed(base, head, repo)
    added_sha = collections.Counter(head_tree[p][0] for s, p in diff if s == "A" and p in head_tree)
    out = []
    for status, path in diff:
        if path not in head_tree or any(fnmatch.fnmatchcase(path, g) for g in exempt):
            continue
        sha, size = head_tree[path]
        if status == "A" and path.endswith(artifact_store.POINTER):
            problem = pointer_problem(git("cat-file", "blob", sha, repo=repo))
            if problem:
                out.append(("pointer", path, size, problem))
            continue
        if size >= TOO_LARGE:
            out.append(("too_large", path, size, f"{size / 2**20:.1f} MiB"))
        if status != "A" or size < LARGE:
            continue
        magic = head_bytes(path, sha, repo)
        if not any(magic.startswith(m) for m in artifact_store.COMPRESSED_MAGIC):
            out.append(("uncompressed", path, size, f"{size / 2**20:.1f} MiB of uncompressed data"))
        if by_sha.get(sha):
            out.append(("duplicate", path, size, f"same bytes as {by_sha[sha][0]}"))
        elif added_sha[sha] > 1:
            out.append(("duplicate", path, size, "same bytes as another file this PR adds"))
    return out


def report(ref: str, repo: Path = REPO) -> str:
    files = tree(ref, repo)
    total = sum(size for _sha, size in files.values())
    by_top = collections.Counter()
    for path, (_sha, size) in files.items():
        by_top[path.split("/", 1)[0]] += size
    counts = collections.Counter(sha for sha, _size in files.values())
    sizes = {sha: size for sha, size in files.values()}
    duplicate = sum((n - 1) * sizes[sha] for sha, n in counts.items() if n > 1 and sizes[sha] >= LARGE)
    large = [(size, path) for path, (_sha, size) in files.items() if size >= LARGE]
    lines = [f"{ref}: {len(files):,} files, {total / 2**30:.2f} GiB as committed",
             f"  files of 1 MiB or more: {len(large):,}, {sum(s for s, _ in large) / 2**30:.2f} GiB",
             f"  extra copies of identical files of 1 MiB or more: {duplicate / 2**20:,.1f} MiB",
             "  by top-level directory:"]
    lines += [f"    {size / 2**30:6.2f} GiB  {top}" for top, size in by_top.most_common(8)]
    lines.append("  largest files:")
    lines += [f"    {size / 2**20:7.1f} MiB  {path}" for size, path in sorted(large, reverse=True)[:10]]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check", help="refuse large, uncompressed or duplicate files a PR adds")
    p.add_argument("--base", required=True)
    p.add_argument("--head", default="HEAD")
    p = sub.add_parser("report", help="where the tree's bytes are")
    p.add_argument("--ref", default="HEAD")
    args = parser.parse_args(argv)
    if args.command == "report":
        print(report(args.ref))
        return 0
    violations = check(args.base, args.head)
    head_tree = tree(args.head)
    added = sum(head_tree.get(path, ("", 0))[1] for status, path in changed(args.base, args.head)
                if status == "A")
    summary = [f"repo_size: this PR adds {added / 2**20:.1f} MiB in new files; "
               f"{len(violations)} size violation(s)"]
    for rule, path, _size, detail in violations:
        print(f"::error file={path}::{rule}: {detail}; {FIX[rule]}")
        summary.append(f"  {rule:12} {path}: {detail}")
    print("\n".join(summary))
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write("### Repository size\n\n```\n" + "\n".join(summary) + "\n```\n")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
