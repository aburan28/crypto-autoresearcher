"""Exact b-independence and order-two wrong-curve witness check."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCH = ROOT / "research/nist_seed_skipped_curves_20261016"
EXPECTED = {
    "assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    "traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
}
PUB_NAMES = ("prime192v1", "prime192v2", "prime192v3", "prime239v1",
             "prime239v2", "prime239v3", "secp224r1", "prime256v1")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def on_curve(point, p, a, b):
    if point is None:
        return True
    x, y = point
    return (y*y - x*x*x - a*x - b) % p == 0


def add(P, Q, p, a):
    """Affine group law with exceptional cases; intentionally has no b argument."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1+y2) % p == 0:
        return None
    if P == Q:
        lam = ((3*x1*x1+a) * pow(2*y1, -1, p)) % p
    else:
        lam = ((y2-y1) * pow(x2-x1, -1, p)) % p
    x3 = (lam*lam-x1-x2) % p
    y3 = (lam*(x1-x3)-y1) % p
    return x3, y3


def main():
    output = HERE / "results.json"
    if output.exists():
        raise ValueError("refuse to overwrite results")
    source_hashes = {name: sha(ARCH / name) for name in EXPECTED}
    if source_hashes != EXPECTED:
        raise ValueError("source hash mismatch")
    omitted = json.loads((ARCH / "assessed.json").read_text())["candidate_rows"]
    published = json.loads((ARCH / "traits.json").read_text())["published_controls"]
    cases = [("omitted", x) for x in omitted]
    cases += [("published", published[name]) for name in PUB_NAMES]
    if len(cases) != 19:
        raise ValueError("wrong case count")
    rows = []
    fields = {}
    for label, x in cases:
        p, a, b = (int(x[key], 16) for key in ("p_hex", "a_hex", "b_hex"))
        bits = p.bit_length()
        fields.setdefault(bits, set()).add(p)
        Q = (0, 0)
        discriminant_nonzero = (-16*(4*pow(a, 3, p))) % p != 0
        row = {
            "label": label,
            "curve_uid": x["identity"]["curve_uid"],
            "field_bits": bits,
            "seed_ordinal_one_based": x["seed_ordinal_one_based"],
            "p": str(p), "a": str(a), "b": str(b),
            "a_equals_minus_three": (a-p) == -3,
            "b_nonzero": b % p != 0,
            "wrong_curve_b_prime": "0",
            "wrong_curve_nonsingular": discriminant_nonzero,
            "Q_on_wrong_curve": on_curve(Q, p, a, 0),
            "Q_off_configured_curve": not on_curve(Q, p, a, b),
            "two_Q_is_identity": add(Q, Q, p, a) is None,
        }
        if not all(row[key] for key in ("a_equals_minus_three", "b_nonzero", "wrong_curve_nonsingular",
                                        "Q_on_wrong_curve", "Q_off_configured_curve", "two_Q_is_identity")):
            raise ValueError(f"real-curve check failed: {row['curve_uid']}")
        rows.append(row)
    if set(fields) != {192, 224, 239, 256} or any(len(values) != 1 for values in fields.values()):
        raise ValueError("field identity mismatch")

    p, a, b1, b2, other_b = 101, -3 % 101, 1, 2, 3
    Q = (0, 0)
    order_two = [Q, add(Q, Q, p, a), add(add(Q, Q, p, a), Q, p, a)]
    if order_two != [Q, None, Q] or on_curve(Q, p, a, b1) or on_curve(Q, p, a, b2):
        raise ValueError("small-field order-two control failed")
    R = None
    for x in range(p):
        for y in range(1, p):
            candidate = (x, y)
            if on_curve(candidate, p, a, other_b):
                R = candidate
                break
        if R is not None:
            break
    if R is None or on_curve(R, p, a, b1) or on_curve(R, p, a, b2):
        raise ValueError("small-field nonzero-y control setup failed")
    two_R = add(R, R, p, a)
    if two_R is None or not on_curve(two_R, p, a, other_b):
        raise ValueError("small-field doubling control failed")
    data = {
        "schema": "nist-invalid-curve-surface/v1",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": source_hashes,
        "script_sha256": sha(HERE / "check.py"),
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_dirty_before_output": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()),
        "host": platform.platform(), "python": sys.version,
        "field_prime_count": {str(k): len(v) for k, v in fields.items()},
        "rows": rows,
        "small_field_controls": {"p": p, "a": a, "configured_b": [b1, b2],
                                 "wrong_curve_b_prime": other_b, "order_two_Q": Q,
                                 "Q_multiples_1_2_3": order_two,
                                 "nonzero_y_R": R, "two_R": two_R,
                                 "R_off_b1": not on_curve(R, p, a, b1),
                                 "R_off_b2": not on_curve(R, p, a, b2),
                                 "two_R_on_b_prime": on_curve(two_R, p, a, other_b)},
    }
    output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
