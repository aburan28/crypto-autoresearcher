#!/usr/bin/env python3
"""C-ENGINE (phase 0, before any draw): tree rule and ancestry, package file
hashes and the _kernels.c pin, the full RC-1 replay, the kernel test suite and
build_info. Outputs are kept verbatim under --out with UTC timestamps.

    python3 engine_provenance.py --out RUN_DIR/engine-provenance
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import common as C


def sh(cmd, **kw):
    p = subprocess.run(cmd, cwd=C.ROOT, capture_output=True, text=True, **kw)
    return p.returncode, p.stdout, p.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists() and any(out.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty {out}")
    out.mkdir(parents=True, exist_ok=True)
    run_id = args.run_id or out.parent.name
    rec = {"run_id": run_id, "experiment_id": C.EXPERIMENT_ID, "started_utc": C.utc_now(), "items": {}}
    env = dict(os.environ)
    if env.get("CRYPTO_AR_GF2_BACKEND") != "native":
        rec["items"]["env"] = {"pass": False, "reason": "CRYPTO_AR_GF2_BACKEND must be native"}
    env["CRYPTO_AR_GF2_BACKEND"] = "native"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    # (a) tree rule and ancestry
    _, head, _ = sh(["git", "rev-parse", "HEAD"])
    _, t_head, _ = sh(["git", "rev-parse", "HEAD:src/crypto_autoresearcher/gf2"])
    _, t_pin, _ = sh(["git", "rev-parse", f"{C.PINNED_COMMIT}:src/crypto_autoresearcher/gf2"])
    anc, _, _ = sh(["git", "merge-base", "--is-ancestor", C.PINNED_COMMIT, "HEAD"])
    dq, dstat, _ = sh(["git", "status", "--porcelain", "--", "src/crypto_autoresearcher/gf2"])
    rec["items"]["a_tree_rule"] = {
        "head": head.strip(), "tree_head": t_head.strip(), "tree_pinned": t_pin.strip(),
        "is_ancestor_exit": anc, "package_worktree_status": dstat.strip(),
        "pass": bool(t_head.strip()) and t_head.strip() == t_pin.strip() and anc == 0 and dstat.strip() == ""}

    # (b) hashes
    pkg = C.SRC / "crypto_autoresearcher" / "gf2"
    _, tracked, _ = sh(["git", "ls-files", "src/crypto_autoresearcher/gf2"])
    hashes = {f: C.sha256_file(C.ROOT / f) for f in tracked.split()}
    kc = C.sha256_file(pkg / "_kernels.c")
    rec["items"]["b_hashes"] = {"package_files_sha256": hashes, "kernels_c_sha256": kc,
                                "pin": C.KERNELS_C_SHA256, "pass": kc == C.KERNELS_C_SHA256}

    # (c) RC-1 replay
    t0 = time.time()
    rc_json = out / "replay-rc1.json"
    cmd = [sys.executable, "tools/gf2_replay_rc1.py", "--limit", "1062", "--json", str(rc_json)]
    thr = env.get("CRYPTO_AR_GF2_THREADS")
    p = subprocess.run(cmd, cwd=C.ROOT, capture_output=True, text=True, env=env)
    (out / "replay-rc1.stdout.log").write_text(p.stdout)
    (out / "replay-rc1.stderr.log").write_text(p.stderr)
    item = {"command": " ".join(cmd), "CRYPTO_AR_GF2_THREADS": thr, "exit": p.returncode,
            "wall_seconds_measured": round(time.time() - t0, 1), "end_utc": C.utc_now()}
    try:
        rj = json.loads(rc_json.read_text())
        res = rj["results"]
        mism = [r for r in res if r["field_diffs"] or r["cert_ok"] is False]
        item.update(records=len(res), certificates=sum(r["cert_ok"] is not None for r in res),
                    mismatches=len(mism), backend=rj.get("backend"))
        item["pass"] = (p.returncode == 0 and len(res) == 1062 and item["certificates"] == 268
                        and not mism and rj.get("backend") == "native")
    except Exception as exc:
        item.update(error=repr(exc), **{"pass": False})
    rec["items"]["c_replay_rc1"] = item

    # (d) kernel tests
    t0 = time.time()
    cmd = [sys.executable, "-m", "pytest", "-q", "-rs", "-p", "no:cacheprovider", "tests/test_gf2_kernels.py"]
    p = subprocess.run(cmd, cwd=C.ROOT, capture_output=True, text=True, env=env)
    (out / "pytest.stdout.log").write_text(p.stdout)
    (out / "pytest.stderr.log").write_text(p.stderr)
    last = [ln for ln in p.stdout.strip().splitlines() if ln.strip()][-1:] or [""]
    summary = last[0]
    rec["items"]["d_pytest"] = {
        "command": " ".join(cmd), "exit": p.returncode, "summary": summary,
        "deviation_note": "-p no:cacheprovider added so pytest writes no .pytest_cache outside the write scope",
        "wall_seconds_measured": round(time.time() - t0, 1), "end_utc": C.utc_now(),
        "pass": p.returncode == 0 and "failed" not in summary and "skipped" not in summary and "passed" in summary}

    # (e) build_info in this process
    os.environ["CRYPTO_AR_GF2_BACKEND"] = "native"
    from crypto_autoresearcher.gf2 import _native, kernels  # noqa: E402
    backend = kernels.backend()
    bi = dict(_native.build_info)
    rec["items"]["e_build_info"] = {"backend": backend, "build_info": bi,
                                    "pass": backend == "native" and bi.get("backend") == "native"
                                    and bi.get("source_sha256") == C.KERNELS_C_SHA256}
    rec["git"] = {"head": head.strip()}
    rec["finished_utc"] = C.utc_now()
    rec["pass"] = all(v.get("pass") for v in rec["items"].values())
    C.write_json(out / "engine-provenance.json", rec)
    print(json.dumps({k: v.get("pass") for k, v in rec["items"].items()}), "PASS" if rec["pass"] else "FAIL")
    return 0 if rec["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
