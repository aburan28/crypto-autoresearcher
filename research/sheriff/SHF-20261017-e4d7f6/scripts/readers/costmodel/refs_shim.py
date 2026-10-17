#!/usr/bin/env python3
"""Run cryptanalysis experiments/fb-archive/refs.py `check` unchanged, except that a tracked file absent from the
sparse worktree is read from the local object store (git cat-file, GIT_NO_LAZY_FETCH=1: never fetches).
Reports how many files came from the object store and how many were unavailable. Writes nothing.
Usage: python3 -B refs_shim.py <cryptanalysis-root>"""
import importlib.util, os, subprocess, sys, gzip, lzma
from pathlib import Path
root = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("refs", root / "experiments/fb-archive/refs.py")
refs = importlib.util.module_from_spec(spec); spec.loader.exec_module(refs)
env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_OPTIONAL_LOCKS="0")
stats = {"worktree": 0, "object_store": 0, "unavailable": []}
orig = refs.read_text
def read_text(path: Path) -> str:
    if path.exists():
        stats["worktree"] += 1
        return orig(path)
    rel = path.resolve().relative_to(root).as_posix()
    p = subprocess.run(["git", "-c", "gc.auto=0", "cat-file", "blob", f"HEAD:{rel}"], cwd=root, env=env, capture_output=True)
    if p.returncode != 0:
        stats["unavailable"].append(rel)
        return ""
    stats["object_store"] += 1
    data = p.stdout
    if path.name.endswith(".gz"): data = gzip.decompress(data)
    elif path.name.endswith(".xz"): data = lzma.decompress(data)
    return data.decode("utf-8", errors="replace")
refs.read_text = read_text
sys.argv = ["refs.py", "check"]
rc = refs.main()
print(f"[shim] files read from worktree {stats['worktree']}, from local object store {stats['object_store']}, unavailable {len(stats['unavailable'])}")
for u in stats["unavailable"][:20]: print("[shim] unavailable:", u)
print(f"[shim] refs.py check exit {rc}")
sys.exit(rc)
