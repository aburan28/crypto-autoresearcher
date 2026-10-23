"""The CI size gate refuses large uncompressed or duplicate files a PR adds, never old ones."""
from __future__ import annotations

import gzip
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import repo_size  # noqa: E402

MIB = 1 << 20


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def repo(tmp_path: Path) -> Path:
    root = tmp_path / "r"
    root.mkdir()
    git(root, "init", "-q")
    git(root, "config", "user.email", "t@example.invalid")
    git(root, "config", "user.name", "t")
    return root


def commit(root: Path, files: dict[str, bytes]) -> str:
    for path, data in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(data)
    git(root, "add", "-A")
    git(root, "commit", "-qm", "c")
    return git(root, "rev-parse", "HEAD")


def text(n: int, seed: str = "x") -> bytes:
    return (seed * 64 + "\n").encode() * (n // 65 + 1)


def rules(violations):
    return sorted((rule, path) for rule, path, _size, _detail in violations)


def test_flags_new_uncompressed_and_duplicate_files_only(tmp_path):
    root = repo(tmp_path)
    old = text(2 * MIB, "o")
    base = commit(root, {"experiments/E/runs/R/raw-result.json": old, "small.txt": b"hi"})
    commit(root, {
        "experiments/E/runs/S/raw-result.json": text(2 * MIB, "n"),               # uncompressed
        "experiments/E/runs/S/roots.jsonl.gz": gzip.compress(text(4 * MIB, "g")),  # fine
        "coordination/goals/G/runs/R/raw-result.json": old,                         # copy of a tracked file
        "experiments/E/runs/S/notes.md": b"small and new",                          # fine
    })
    found = rules(repo_size.check(base, "HEAD", root))
    assert found == [("duplicate", "coordination/goals/G/runs/R/raw-result.json"),
                     ("uncompressed", "coordination/goals/G/runs/R/raw-result.json"),
                     ("uncompressed", "experiments/E/runs/S/raw-result.json")]


def test_existing_files_are_never_rechecked(tmp_path):
    root = repo(tmp_path)
    base = commit(root, {"big.json": text(3 * MIB)})
    commit(root, {"other.txt": b"unrelated change"})
    assert repo_size.check(base, "HEAD", root) == []


def test_too_large_applies_to_changes_as_well(tmp_path, monkeypatch):
    monkeypatch.setattr(repo_size, "TOO_LARGE", 3 * MIB)
    root = repo(tmp_path)
    base = commit(root, {"index.json": b"{}"})
    commit(root, {"index.json": gzip.compress(os.urandom(4 * MIB))})   # modified, compressed, still too large
    assert rules(repo_size.check(base, "HEAD", root)) == [("too_large", "index.json")]


def test_exemptions_need_a_reason(tmp_path):
    root = repo(tmp_path)
    base = commit(root, {"a.txt": b"a"})
    commit(root, {"vendor/table.csv": text(2 * MIB),
                  ".github/size-exemptions.txt": b"vendor/*.csv  # vendored test vector, read by path\n"})
    assert repo_size.check(base, "HEAD", root) == []
    (root / ".github/size-exemptions.txt").write_bytes(b"vendor/*.csv\n")
    try:
        repo_size.check(base, "HEAD", root)
    except SystemExit as error:
        assert "needs '# <reason>'" in str(error)
    else:
        raise AssertionError("an exemption without a reason was accepted")


def test_report_counts_duplicates(tmp_path):
    root = repo(tmp_path)
    blob = text(2 * MIB)
    commit(root, {"a/x.json": blob, "b/x.json": blob, "c.txt": b"c"})
    out = repo_size.report("HEAD", root)
    assert "3 files" in out
    assert f"extra copies of identical files of 1 MiB or more: {len(blob) / MIB:,.1f} MiB" in out


def test_added_pointers_must_address_the_shared_store(tmp_path):
    import json
    root = repo(tmp_path)
    base = commit(root, {"a.txt": b"a"})
    sha = "ab" * 32
    good = {"schema": "crypto.autoresearch.blob_pointer.v1", "sha256": sha, "size": 9, "encoding": "gzip",
            "content_sha256": "cd" * 32, "content_size": 99,
            "uri": f"s3://crypto-autoresearcher/blobs/sha256/ab/{sha}"}
    local = dict(good, uri=f"file:///home/me/blobs/sha256/ab/{sha}")
    wrong = dict(good, uri="s3://crypto-autoresearcher/blobs/sha256/ab/" + "ef" * 32)
    commit(root, {"r/raw-result.json.gz.blob.json": json.dumps(good).encode(),
                  "r/stdout.log.gz.blob.json": json.dumps(local).encode(),
                  "r/stderr.log.gz.blob.json": json.dumps(wrong).encode()})
    assert rules(repo_size.check(base, "HEAD", root)) == [("pointer", "r/stderr.log.gz.blob.json"),
                                                          ("pointer", "r/stdout.log.gz.blob.json")]
