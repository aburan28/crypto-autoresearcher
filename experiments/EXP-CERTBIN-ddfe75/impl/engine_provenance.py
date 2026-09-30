#!/usr/bin/env python3
"""C-ENGINE (phase 0, before any draw): pinned-engine provenance.

(a) tree rule and ancestry of engine_provenance; (b) sha256 of _kernels.c
against the pin and of every package file; (c) the FULL
tools/gf2_replay_rc1.py sweep (1062 records, 268 certificates, 0
mismatches); (d) tests/test_gf2_kernels.py with 0 failures and 0 skipped;
(e) kernels._native.build_info (backend native, source_sha256 = pin).
Outputs are kept verbatim under --out; summary.json carries the verdict.
Exit code 0 iff every item passes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
from common import ENGINE_COMMIT, KERNELS_C_PIN, ROOT, now, sha256_file, write_json  # noqa: E402

PKG = "src/crypto_autoresearcher/gf2"


def git(*a):
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    started = now()
    env_ok = os.environ.get("CRYPTO_AR_GF2_BACKEND") == "native"
    res = {"control": "C-ENGINE", "run_id": os.environ.get("RUN_ID"), "started": started,
           "env": {k: os.environ.get(k) for k in ["CRYPTO_AR_GF2_BACKEND", "PYTHONDONTWRITEBYTECODE",
                                                   "CRYPTO_AR_GF2_THREADS", "CRYPTO_AR_GF2_CACHE",
                                                   "RUN_ID", "OPENBLAS_NUM_THREADS"]},
           "env_backend_native": env_ok}

    # (a) tree rule and ancestry
    _, head, _ = git("rev-parse", "HEAD")
    _, tree_head, _ = git("rev-parse", f"HEAD:{PKG}")
    _, tree_pin, _ = git("rev-parse", f"{ENGINE_COMMIT}:{PKG}")
    rc_anc, _, _ = git("merge-base", "--is-ancestor", ENGINE_COMMIT, "HEAD")
    _, pin_full, _ = git("rev-parse", ENGINE_COMMIT)
    _, st_pkg, _ = git("status", "--porcelain", "--", PKG)
    _, st_ign, _ = git("status", "--porcelain", "--ignored", "--", PKG)
    res["a_tree_rule"] = {"head": head, "pinned_commit": ENGINE_COMMIT, "pinned_commit_full": pin_full,
                          "tree_head": tree_head, "tree_pin": tree_pin,
                          "tree_equal": bool(tree_head) and tree_head == tree_pin,
                          "pin_is_ancestor_of_head": rc_anc == 0,
                          "package_worktree_status": st_pkg.splitlines(),
                          "package_ignored_entries": [l for l in st_ign.splitlines() if l.startswith("!!")],
                          }
    res["a_tree_rule"]["pass"] = (res["a_tree_rule"]["tree_equal"] and res["a_tree_rule"]["pin_is_ancestor_of_head"]
                                  and not st_pkg)

    # (b) file hashes
    _, files, _ = git("ls-files", PKG)
    fh = {f: sha256_file(ROOT / f) for f in files.splitlines()}
    kc = fh.get(f"{PKG}/_kernels.c")
    res["b_hashes"] = {"package_files_sha256": fh, "kernels_c_sha256": kc, "pin": KERNELS_C_PIN,
                       "pass": kc == KERNELS_C_PIN}

    # (c) full RC-1 replay
    t = time.time()
    cmd = [sys.executable, "tools/gf2_replay_rc1.py", "--json", str(out / "replay-rc1.json")]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    (out / "replay-rc1.stdout.txt").write_text(r.stdout)
    (out / "replay-rc1.stderr.txt").write_text(r.stderr)
    m = re.search(r"records: (\d+)\s+certificates checked: (\d+)\s+mismatches: (\d+)", r.stdout)
    rec = {"command": " ".join(["python3"] + cmd[1:]), "exit_code": r.returncode,
           "seconds": round(time.time() - t, 1), "finished": now()}
    if m:
        rec.update(records=int(m.group(1)), certificates=int(m.group(2)), mismatches=int(m.group(3)))
    bm = re.search(r"backend: (\S+)\s+threads: (\d+)", r.stdout)
    if bm:
        rec.update(backend=bm.group(1), threads=int(bm.group(2)))
    rec["pass"] = (r.returncode == 0 and rec.get("records") == 1062 and rec.get("certificates") == 268
                   and rec.get("mismatches") == 0 and rec.get("backend") == "native")
    res["c_replay_rc1"] = rec
    print(f"[engine] replay: {rec}", flush=True)

    # (d) pytest
    t = time.time()
    cmd = [sys.executable, "-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider", "tests/test_gf2_kernels.py"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    (out / "pytest.stdout.txt").write_text(r.stdout)
    (out / "pytest.stderr.txt").write_text(r.stderr)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    counts = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|skipped|error|errors|xfailed|xpassed)", tail)}
    rec = {"command": " ".join(["python3"] + cmd[1:]), "exit_code": r.returncode, "summary_line": tail,
           "counts": counts, "seconds": round(time.time() - t, 1), "finished": now(),
           "note": "-p no:cacheprovider added so that no .pytest_cache is written into the shared worktree; it does not change test selection or outcome"}
    rec["pass"] = (r.returncode == 0 and counts.get("passed", 0) > 0 and not counts.get("failed")
                   and not counts.get("skipped") and not counts.get("error") and not counts.get("errors"))
    res["d_pytest"] = rec
    print(f"[engine] pytest: {tail}", flush=True)

    # (e) build_info (in this process, after the first native call)
    from crypto_autoresearcher.gf2 import closure, kernels
    from crypto_autoresearcher.gf2 import _native
    cl = closure.Closure(6, 3, 1)
    cl.macaulay_closure([[1, 2, 3]], want_cert=False)
    bi = dict(_native.build_info)
    res["e_build_info"] = {"build_info": bi, "kernels_backend": kernels.backend(),
                           "pass": bi.get("backend") == "native" and bi.get("source_sha256") == KERNELS_C_PIN
                           and kernels.backend() == "native"}
    res["finished"] = now()
    res["pass"] = all(res[k]["pass"] for k in ["a_tree_rule", "b_hashes", "c_replay_rc1", "d_pytest", "e_build_info"]) and env_ok
    write_json(out / "summary.json", res)
    print(f"[engine] C-ENGINE pass={res['pass']}", flush=True)
    return 0 if res["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
