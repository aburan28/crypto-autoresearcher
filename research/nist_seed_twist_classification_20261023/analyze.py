#!/usr/bin/env python3
"""Exact generic-j and quadratic-twist binding audit for archived seed curves."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / "research/nist_seed_skipped_curves_20261016"
TWISTS = ROOT / "research/nist_seed_twist_embedding_20261023/analysis.json"
EXPECTED = {
    "assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    "traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    # Record the tree before creating a new untracked run directory.
    head, status = git("rev-parse", "HEAD"), git("status", "--short")
    out.mkdir(parents=True, exist_ok=False)
    begin = time.monotonic()
    record = {
        "schema": "nist-seed-rational-twist-classification/v1",
        "started_at_utc": utc(), "git_head": head, "git_status_before_run": status,
        "python": sys.version, "host": platform.platform(),
        "protocol_sha256": sha((HERE / "PROTOCOL.md").read_bytes()),
        "launcher_sha256": sha(Path(__file__).read_bytes()),
        "source_sha256": {}, "rows": [],
    }
    save(out / "started.json", record)
    try:
        for name, expected in EXPECTED.items():
            actual = sha((INPUT / name).read_bytes())
            if actual != expected:
                raise ValueError(f"input hash mismatch: {name}")
            record["source_sha256"][name] = actual
        record["source_sha256"]["twist_analysis.json"] = sha(TWISTS.read_bytes())
        skipped = json.loads((INPUT / "assessed.json").read_text())["candidate_rows"]
        published = json.loads((INPUT / "traits.json").read_text())["published_controls"]
        twist_rows = json.loads(TWISTS.read_text())["rows"]
        if len(skipped) != 11 or len(published) != 10 or len(twist_rows) != 21:
            raise ValueError("input cardinality mismatch")
        twists_by_uid = {r["curve_uid"]: r for r in twist_rows}
        if len(twists_by_uid) != 21:
            raise ValueError("duplicate twist UID")
        items = [("omitted", row["identity"]["curve_id"], row) for row in skipped]
        items += [("published", name, row) for name, row in published.items()]
        for kind, name, source in items:
            ident = source["identity"]
            curve = ident["curve"]
            uid = ident["curve_uid"]
            p = int(ident["field"]["characteristic"])
            a = int(curve["a4"]) % p
            b = int(curve["a6"]) % p
            n = int(curve["subgroup_order"])
            if n != int(source["n_hex"], 16) or p <= 3 or a != p - 3 or b == 0:
                raise ValueError(f"field, coefficient, or order mismatch: {name}")
            den = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
            if den == 0:
                raise ValueError(f"singular curve: {name}")
            j = (1728 * 4 * pow(a, 3, p) * pow(den, -1, p)) % p
            if j in (0, 1728):
                raise ValueError(f"exceptional j invariant: {name}")
            twist = twists_by_uid.pop(uid)
            twist_order = 2 * p + 2 - n
            if p != int(twist["p_hex"], 16) or twist_order != int(twist["twist_order_hex"], 16):
                raise ValueError(f"twist archive mismatch: {name}")
            row = {
                "kind": kind, "name": name, "curve_uid": uid,
                "p_decimal": str(p), "a_decimal": str(a), "b_decimal": str(b),
                "n_decimal": str(n), "discriminant_denominator_mod_p": str(den),
                "j_decimal": str(j), "j_is_generic": True,
                "quadratic_twist_order_decimal": str(twist_order),
                "twist_archive_factor_source": twist["factor_source"],
                "twist_archive_factor_count": twist["factor_count"],
            }
            record["rows"].append(row)
            save(out / f"case_{len(record['rows'])-1:02d}.json", row)
        if twists_by_uid or len({r["curve_uid"] for r in record["rows"]}) != 21:
            raise ValueError("curve UID coverage mismatch")
        record["summary"] = {"omitted": 11, "published": 10, "generic_j": 21,
                             "twist_archive_matches": 21}
        record["finished_at_utc"] = utc()
        record["elapsed_seconds"] = time.monotonic() - begin
        save(out / "results.json", record)
        (out / "complete.ok").write_text(sha((out / "results.json").read_bytes()) + "\n")
        return 0
    except Exception as exc:
        record["failed_at_utc"] = utc()
        record["failure"] = f"{type(exc).__name__}: {exc}"
        record["elapsed_seconds"] = time.monotonic() - begin
        save(out / "failure.json", record)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
