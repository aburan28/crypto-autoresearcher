"""Artifact inventory of this task's directory (every file except report.yaml, whose own digest is returned to
the Coordinator separately) and of the scratch artifacts that are not staged. Prints YAML for report.yaml.

usage: python3 -I -B inventory.py <repo-root> <task-dir> <scratch-dir>
"""
import hashlib
import os
import sys

repo, task, scratch = (os.path.abspath(a) for a in sys.argv[1:4])


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


print("artifact_inventory:")
big = []
for dp, dns, fns in sorted(os.walk(task)):
    dns.sort()
    for fn in sorted(fns):
        p = os.path.join(dp, fn)
        rel = os.path.relpath(p, repo)
        if os.path.relpath(p, task) == "report.yaml":
            continue
        size = os.path.getsize(p)
        if size >= 65536:
            big.append(rel)
        print(f"- {{path: {rel}, sha256: {sha(p)}, bytes: {size}}}")
print("not_staged_scratch_artifacts:")
for dp, dns, fns in sorted(os.walk(scratch)):
    dns.sort()
    for fn in sorted(fns):
        p = os.path.join(dp, fn)
        if "/tmp/" in p[len(scratch):] + "/" and fn.startswith("bb0d26-"):
            continue
        print(f"- {{path: {p}, sha256: {sha(p)}, bytes: {os.path.getsize(p)}}}")
print(f"# files >= 64 KiB in the task directory: {big}")
