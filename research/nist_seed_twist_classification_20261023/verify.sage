#!/usr/bin/env sage -python
"""Independent Sage enumeration of finite-field twists for 21 exact curves."""
import argparse
import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

from sage.all import EllipticCurve, GF, ZZ, is_prime
from sage.version import version as sage_version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE / "runs/20261023T2102Z/results.json"
SOURCE_SHA = "55dcc0d49b8616c4a85698173761fd743fb43e1495d174e4a1b10540483b00d1"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def save(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    begin = time.monotonic()
    record = {
        "schema": "nist-seed-twist-sage-verification/v1", "started_at_utc": utc(),
        "command": sys.argv, "git_head": head, "git_status_before_run": status,
        "host": platform.platform(), "python": sys.version, "sage": sage_version,
        "source_sha256_expected": SOURCE_SHA,
        "verification_protocol_sha256": sha((HERE / "VERIFICATION_PROTOCOL.md").read_bytes()),
        "verifier_sha256": sha(Path(__file__).read_bytes()), "rows": [],
    }
    save(out / "started.json", record)
    try:
        if sha(SOURCE.read_bytes()) != SOURCE_SHA:
            raise ValueError("primary result digest mismatch")
        source = json.loads(SOURCE.read_text())["rows"]
        if len(source) != 21:
            raise ValueError("primary result cardinality mismatch")
        for row in source:
            p, a, b, n = (ZZ(row[k]) for k in ("p_decimal", "a_decimal", "b_decimal", "n_decimal"))
            if not is_prime(p, proof=True):
                raise ValueError(f"nonprime field: {row['name']}")
            E = EllipticCurve(GF(p), [a, b])
            j = E.j_invariant()
            if int(j) != int(row["j_decimal"]) or j in (0, 1728):
                raise ValueError(f"Sage j mismatch: {row['name']}")
            forms = E.twists()
            quad = E.quadratic_twist()
            original_matches = sum(bool(T.is_isomorphic(E)) for T in forms)
            quadratic_matches = sum(bool(T.is_isomorphic(quad)) for T in forms)
            if len(forms) != 2 or original_matches != 1 or quadratic_matches != 1:
                raise ValueError(f"twist-class mismatch: {row['name']}")
            if 2 * p + 2 - n != ZZ(row["quadratic_twist_order_decimal"]):
                raise ValueError(f"twist order identity mismatch: {row['name']}")
            output = {"curve_uid": row["curve_uid"], "name": row["name"],
                      "field_prime_proved": True, "sage_j_decimal": str(j),
                      "rational_twist_forms": len(forms),
                      "original_isomorphism_matches": original_matches,
                      "quadratic_isomorphism_matches": quadratic_matches,
                      "twist_order_identity_matches": True}
            record["rows"].append(output)
            save(out / f"case_{len(record['rows'])-1:02d}.json", output)
        record["summary"] = {"passed": 21, "forms_per_curve": 2}
        record["finished_at_utc"] = utc()
        record["elapsed_seconds"] = time.monotonic() - begin
        save(out / "results.json", record)
        (out / "complete.ok").write_text(sha((out / "results.json").read_bytes()) + "\n")
        return 0
    except Exception as exc:
        record["failure"] = f"{type(exc).__name__}: {exc}"
        record["failed_at_utc"] = utc()
        record["elapsed_seconds"] = time.monotonic() - begin
        save(out / "failure.json", record)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
