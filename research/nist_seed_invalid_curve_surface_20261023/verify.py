"""Sage check of exact wrong-curve order-two witness and source bindings."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from sage.all import EllipticCurve, GF

HERE = Path(__file__).resolve().parent
RESULT = HERE / "results.json"
OUTPUT = HERE / "verification.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUTPUT.exists():
        raise ValueError("refuse verification overwrite")
    data = json.loads(RESULT.read_text())
    if len(data["rows"]) != 19:
        raise ValueError("wrong row count")
    checked = []
    for row in data["rows"]:
        p, a, b = (int(row[key]) for key in ("p", "a", "b"))
        F = GF(p)
        E0 = EllipticCurve(F, [F(a), F(0)])
        E = EllipticCurve(F, [F(a), F(b)])
        Q = E0(F(0), F(0))
        if Q.order() != 2 or E0.discriminant() == 0 or F(b) == 0:
            raise ValueError(f"wrong-curve witness failed: {row['curve_uid']}")
        if F(0)**2 == F(0)**3 + F(a)*F(0) + F(b):
            raise ValueError(f"Q lies on configured curve: {row['curve_uid']}")
        if int(E.a4()) != a or int(E.a6()) != b or int(E0.a4()) != a:
            raise ValueError(f"curve coefficient mismatch: {row['curve_uid']}")
        checked.append({"curve_uid": row["curve_uid"], "wrong_curve_Q_order": 2,
                        "configured_Q_rejected": True, "wrong_curve_discriminant_nonzero": True})
    OUTPUT.write_text(json.dumps({
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "results_sha256": sha(RESULT),
        "verifier_sha256": sha(HERE / "verify.py"),
        "rows": checked,
    }, indent=2) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
