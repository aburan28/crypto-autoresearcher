"""Independent Sage multiplicative-order verification for all exact rows."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from sage.all import Mod, ZZ, prod

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from compute import ARCH, FACT, EXPECTED, BOUNDS, curves, sha


def verify(root):
    dest = root / "verification.json"
    if dest.exists():
        raise ValueError("refuse verification overwrite")
    if not (root / "complete.ok").exists() or not (root / "exact/complete.ok").exists():
        raise ValueError("missing completion marker")
    for path, digest in EXPECTED.items():
        if sha(path) != digest:
            raise ValueError(f"changed source: {path}")
    data = json.loads((root / "exact/results.json").read_text())
    if len(data["rows"]) != 19 or len({r["curve_uid"] for r in data["rows"]}) != 19:
        raise ValueError("wrong or duplicate row set")
    row_by_uid = {r["curve_uid"]: r for r in data["rows"]}
    factor_by_name = {r["name"]: r for r in json.loads((FACT / "results.json").read_text())}
    verified = []
    for name, label, archived in curves():
        uid = archived["identity"]["curve_uid"]
        row = row_by_uid[uid]
        p, n = int(archived["p_hex"], 16), int(archived["n_hex"], 16)
        k = int(row["k"])
        if row["name"] != name or row["label"] != label or int(row["p"]) != p or int(row["n"]) != n:
            raise ValueError(f"curve identity mismatch: {name}")
        if not ZZ(n).is_prime(proof=True):
            raise ValueError(f"nonprime subgroup order: {name}")
        fact = factor_by_name[name + "_minus"]["factors"]
        if fact is None or ZZ(n-1) != prod(ZZ(q)**int(e) for q, e in fact):
            raise ValueError(f"bad factor product: {name}")
        if any(not ZZ(q).is_prime(proof=True) for q, _ in fact):
            raise ValueError(f"unproved factor: {name}")
        sage_k = int(Mod(p, n).multiplicative_order())
        if sage_k != k:
            raise ValueError(f"Sage order mismatch: {name}")
        if pow(p, k, n) != 1 or any(pow(p, k//int(q), n) == 1 for q, _ in row["k_factors"]):
            raise ValueError(f"missing minimality witness: {name}")
        if row["k_bits"] != k.bit_length() or row["k_decimal_digits"] != len(str(k)):
            raise ValueError(f"order size mismatch: {name}")
        if row["below_or_equal_bounds"] != {str(B): k <= B for B in BOUNDS}:
            raise ValueError(f"threshold mismatch: {name}")
        verified.append({"name": name, "curve_uid": uid, "label": label, "k": str(k),
                         "Sage_exact_order_match": True})
    dest.write_text(json.dumps({"verified_at_utc": datetime.now(timezone.utc).isoformat(),
                                "results_sha256": sha(root / "exact/results.json"),
                                "verifier_sha256": sha(HERE / "verify.py"),
                                "rows": verified}, indent=2) + "\n")
    print(dest)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: sage -python verify.py RUN_DIR")
    verify(Path(sys.argv[1]))
