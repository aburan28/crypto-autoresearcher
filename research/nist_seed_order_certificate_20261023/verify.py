"""Proof-enabled verification and fixed Pocklington proxy metrics."""
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import sys

from sage.all import ZZ

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run import ARCH, EXPECTED, curve_rows, sha

CONTROLS = {"control_15": (15, [(3, 1), (5, 1)]),
            "control_60": (60, [(2, 2), (3, 1), (5, 1)]),
            "control_101": (101, [(101, 1)])}
BOUNDS = (1000, 10000, 100000, 1000000)


def metrics(n, factors):
    data = {}
    for bound in BOUNDS:
        F = math.prod(q**e for q, e in factors if q <= bound)
        data[str(bound)] = {"F_B": str(F), "bits": F.bit_length(),
                            "pocklington_size_condition": F*F > n}
    components = sorted((q**e, q) for q, e in factors)
    components.reverse()
    product = 1
    used = []
    for component, q in components:
        product *= component
        used.append(q)
        if product*product > n:
            break
    if product*product <= n:
        raise ValueError("full factors fail size crossing")
    return {"bounded": data, "minimum_prime_power_components": len(used),
            "largest_prime_at_crossing": str(max(used)),
            "smallest_prime_at_crossing": str(min(used))}


def main(out):
    if (out / "verification.json").exists() or (out / "complete.ok").exists():
        raise ValueError("verification already exists")
    start = json.loads((out / "started.json").read_text())
    if start["source_sha256"] != EXPECTED:
        raise ValueError("source digest manifest changed")
    for name, digest in EXPECTED.items():
        if sha(ARCH / name) != digest:
            raise ValueError(f"source changed: {name}")
    expected = {}
    for base, label, row in curve_rows():
        n = int(row["n_hex"], 16)
        uid = row["identity"]["curve_uid"]
        for direction, number in (("minus", n-1), ("plus", n+1)):
            expected[f"{base}_{direction}"] = (label, n, number, uid, direction)
    rows = json.loads((out / "results.json").read_text())
    if len(rows) != 41 or {x["name"] for x in rows} != set(expected) | set(CONTROLS):
        raise ValueError("wrong case set")
    verified = []
    for x in rows:
        name, receipt = x["name"], x["receipt"]
        for suffix, key in (("gp", "script_sha256"), ("stdout", "stdout_sha256"), ("stderr", "stderr_sha256")):
            if sha(out / f"{name}.{suffix}") != receipt[key]:
                raise ValueError(f"raw hash mismatch: {name}.{suffix}")
        if name in CONTROLS:
            target, control_factors = CONTROLS[name]
            if x["label"] != "control" or x["n"] is not None or x["curve_uid"] is not None or int(x["number"]) != target:
                raise ValueError(f"control binding mismatch: {name}")
        else:
            label, n, number, uid, direction = expected[name]
            if x["label"] != label or x["curve_uid"] != uid or int(x["number"]) != number or int(x["n"]) != n:
                raise ValueError(f"curve binding mismatch: {name}")
            if not ZZ(n).is_prime(proof=True):
                raise ValueError(f"group order not prime: {name}")
        if x["factors"] is None:
            if name in CONTROLS or receipt["status"] == "completed" and receipt["exit_code"] == 0:
                raise ValueError(f"unexpected censored case: {name}")
            verified.append({"name": name, "label": x["label"], "curve_uid": x["curve_uid"],
                             "status": receipt["status"], "metrics": None})
            continue
        if receipt["status"] != "completed" or receipt["exit_code"] != 0:
            raise ValueError(f"invalid completed receipt: {name}")
        factors = [(int(q), int(e)) for q, e in x["factors"]]
        transcript = [line.strip() for line in (out / f"{name}.stdout").read_text().splitlines() if line.strip()]
        if transcript != [f"COUNT={len(factors)}"] + [f"{q},{e}" for q, e in factors] + ["DONE"]:
            raise ValueError(f"factor transcript mismatch: {name}")
        if any(e < 1 or not ZZ(q).is_prime(proof=True) for q, e in factors):
            raise ValueError(f"unproved factor: {name}")
        if math.prod(q**e for q, e in factors) != int(x["number"]):
            raise ValueError(f"incomplete product: {name}")
        if name in CONTROLS:
            if factors != control_factors:
                raise ValueError(f"control factors mismatch: {name}")
            value = None
        else:
            value = metrics(n, factors)
        verified.append({"name": name, "label": x["label"], "curve_uid": x["curve_uid"],
                         "status": "verified", "factor_count": len(factors), "metrics": value})
    (out / "verification.json").write_text(json.dumps({
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "results_sha256": sha(out / "results.json"),
        "verifier_sha256": sha(HERE / "verify.py"),
        "rows": verified,
    }, indent=2) + "\n")
    print(out / "verification.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: sage -python verify.py RUN_DIR")
    main(Path(sys.argv[1]))
