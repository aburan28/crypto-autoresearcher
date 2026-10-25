"""Exact singular-companion surface audit for the nineteen matched classes."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/nist_seed_skipped_curves_20261016"
EXPECTED = {
    "assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    "traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
}
PUBLISHED = ("prime192v1", "prime192v2", "prime192v3", "prime239v1",
             "prime239v2", "prime239v3", "secp224r1", "prime256v1")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quadratic_character(c, p):
    value = pow(c % p, (p - 1) // 2, p)
    if value == 1:
        return 1
    if value == p - 1:
        return -1
    raise ValueError("Euler test invalid for expected prime field")


def brute_smooth_count(p, b):
    node_x = 1 if b == 2 else p - 1
    count = 1  # point at infinity
    for x in range(p):
        rhs = (x*x*x - 3*x + b) % p
        for y in range(p):
            if (y*y-rhs) % p == 0 and not (x == node_x and y == 0):
                count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise ValueError("refuse to overwrite run directory")
    source_hashes = {name: digest(SOURCE / name) for name in EXPECTED}
    if source_hashes != EXPECTED:
        raise ValueError("source hash mismatch")
    omitted = json.loads((SOURCE / "assessed.json").read_text())["candidate_rows"]
    published = json.loads((SOURCE / "traits.json").read_text())["published_controls"]
    cases = [("omitted", item) for item in omitted]
    cases += [("published", published[name]) for name in PUBLISHED]
    if len(omitted) != 11 or len(cases) != 19:
        raise ValueError("wrong case count")
    rows = []
    fields = {}
    for label, item in cases:
        p, a, b = (int(item[key], 16) for key in ("p_hex", "a_hex", "b_hex"))
        if p <= 3 or a != p - 3 or b in (2, p - 2):
            raise ValueError("source precondition failed")
        if (4 * pow(a, 3, p) + 27 * b*b) % p == 0:
            raise ValueError("configured source is singular")
        bits = p.bit_length()
        if bits in fields and fields[bits]["p"] != str(p):
            raise ValueError("multiple fields at same bit size")
        if bits not in fields:
            forms = []
            for companion_b, c, node_x in ((2, 3, 1), (-2, -3, -1)):
                if (4 * (-3)**3 + 27 * companion_b**2) != 0:
                    raise ValueError("singular discriminant identity failed")
                for x in (-2, -1, 0, 1, 2, 4, 11):
                    lhs = x**3 - 3*x + companion_b
                    rhs = (x-node_x)**2 * (x+2*node_x)
                    if lhs != rhs:
                        raise ValueError("factorization identity failed")
                chi = quadratic_character(c, p)
                forms.append({"b_prime": str(companion_b % p), "signed_b_prime": companion_b,
                              "node_x": str(node_x % p), "tangent_square": c,
                              "quadratic_character": chi,
                              "smooth_locus_order": str(p - chi)})
            fields[bits] = {"p": str(p), "p_mod_12": p % 12, "forms": forms,
                            "omitted_count": 0, "published_count": 0}
        fields[bits][f"{label}_count"] += 1
        rows.append({"label": label, "curve_uid": item["identity"]["curve_uid"],
                     "field_bits": bits, "seed_ordinal_one_based": item["seed_ordinal_one_based"],
                     "p": str(p), "a": str(a), "configured_b": str(b),
                     "singular_form_orders": [form["smooth_locus_order"] for form in fields[bits]["forms"]]})
    if sorted(fields) != [192, 224, 239, 256]:
        raise ValueError("field set mismatch")
    if sorted(row["curve_uid"] for row in rows) != sorted(set(row["curve_uid"] for row in rows)):
        raise ValueError("duplicate UID")
    controls = []
    for p in (101, 103):
        for b, c in ((2, 3), (-2, -3)):
            actual = brute_smooth_count(p, b)
            expected = p - quadratic_character(c, p)
            if actual != expected:
                raise ValueError("small-field smooth-count control failed")
            controls.append({"p": p, "b_prime": b, "enumerated_smooth_points": actual,
                             "formula_order": expected})
    # Deliberately singular configured-source negative control.
    if (4 * (-3)**3 + 27 * 2**2) != 0:
        raise ValueError("negative control failed")
    result = {
        "schema": "nist-singular-companion-surface/v1",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "command": "python3 research/nist_seed_singular_companions_20261023/check.py --out " + str(args.out),
        "source_sha256": source_hashes, "script_sha256": digest(HERE / "check.py"),
        "protocol_sha256": digest(HERE / "PROTOCOL.md"),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_dirty_before_output": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()),
        "host": platform.platform(), "python": sys.version,
        "field_count": len(fields), "curve_count": len(rows), "omitted_count": len(omitted),
        "published_count": len(PUBLISHED), "fields": {str(k): v for k, v in sorted(fields.items())},
        "rows": rows, "small_field_controls": controls,
        "singular_source_negative_control": True,
    }
    out.mkdir(parents=True, exist_ok=False)
    path = out / "results.json"
    path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    (out / "complete.ok").write_text(digest(path) + "\n")
    print(path)


if __name__ == "__main__":
    main()
