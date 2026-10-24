"""Independent Sage checks of the archived singular-companion result."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

from sage.all import GF, ZZ, PolynomialRing
from sage.version import version as sage_version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/nist_seed_skipped_curves_20261016"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("refuse to overwrite verification directory")
    data = json.loads(args.input.read_text())
    if data["schema"] != "nist-singular-companion-surface/v1" or data["curve_count"] != 19:
        raise ValueError("input schema/count mismatch")
    if (args.input.parent / "complete.ok").read_text().strip() != sha(args.input):
        raise ValueError("primary completion digest mismatch")
    source = json.loads((SOURCE / "assessed.json").read_text())["candidate_rows"]
    pub = json.loads((SOURCE / "traits.json").read_text())["published_controls"]
    exact = {x["identity"]["curve_uid"]: x for x in source}
    exact.update({x["identity"]["curve_uid"]: x for x in pub.values()})
    if len(exact) != 21:
        raise ValueError("archived UID count mismatch")
    results = []
    for row in data["rows"]:
        item = exact[row["curve_uid"]]
        p = ZZ(int(item["p_hex"], 16))
        a = ZZ(int(item["a_hex"], 16))
        b = ZZ(int(item["b_hex"], 16))
        if not p.is_prime(proof=True) or a != p-3 or b in (2, p-2):
            raise ValueError("field/source assertion failed")
        F = GF(p)
        R = PolynomialRing(F, "x")
        x = R.gen()
        verified_orders = []
        for bp, c, node in ((2, 3, 1), (-2, -3, -1)):
            poly = x**3 - 3*x + bp
            if poly != (x-node)**2 * (x+2*node):
                raise ValueError("polynomial factorization failed")
            if F(c).is_square():
                order = p-1
            else:
                order = p+1
            verified_orders.append(str(order))
        if verified_orders != row["singular_form_orders"]:
            raise ValueError("order mismatch")
        results.append({"curve_uid": row["curve_uid"], "field_bits": int(p).bit_length(),
                        "smooth_locus_orders": verified_orders})
    if len(results) != 19:
        raise ValueError("verification coverage failure")
    small = []
    for p in (101, 103):
        F = GF(p)
        for bp, c, node in ((2, 3, 1), (-2, -3, -1)):
            count = 1
            for x in F:
                rhs = x**3-3*x+bp
                for y in F:
                    if y*y == rhs and not (x == F(node) and y == 0):
                        count += 1
            expected = p-1 if F(c).is_square() else p+1
            if count != expected:
                raise ValueError("small-field enumeration mismatch")
            small.append({"p": p, "b_prime": bp, "smooth_points": count})
    out = {"schema": "nist-singular-companion-verification/v1",
           "verified_at_utc": datetime.now(timezone.utc).isoformat(),
           "input_sha256": sha(args.input), "script_sha256": sha(HERE / "verify.py"),
           "sage_version": sage_version, "python": sys.version, "host": platform.platform(),
           "curve_count": len(results), "rows": results, "small_field_controls": small,
           "status": "pass"}
    args.out.mkdir(parents=True, exist_ok=False)
    path = args.out / "results.json"
    path.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    (args.out / "complete.ok").write_text(sha(path) + "\n")
    print(path)


if __name__ == "__main__":
    main()
