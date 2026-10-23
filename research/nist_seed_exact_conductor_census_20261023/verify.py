"""Separate proof-enabled arithmetic check for all new conductor census rows."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

from sage.all import ZZ

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run import ARCH, FIRST, FIRST_VERIFICATION_SHA, GP_SOURCE, cases, sha

CONTROLS = {"control_neg75": (-75, -3, 5), "control_neg7": (-7, -7, 1),
            "control_neg12": (-12, -3, 2)}


def main(out):
    if (out / "verification.json").exists() or (out / "complete.ok").exists():
        raise ValueError("verification output already exists")
    start = json.loads((out / "started.json").read_text())
    if start["gp_launcher_sha256"] != sha(GP_SOURCE):
        raise ValueError("GP launcher hash mismatch")
    if start["first_verification_sha256"] != FIRST_VERIFICATION_SHA or sha(FIRST / "runs/first-stage-20261023T1720Z/verification.json") != FIRST_VERIFICATION_SHA:
        raise ValueError("first stage changed")
    for name, digest in start["source_sha256"].items():
        if sha(ARCH / name) != digest:
            raise ValueError("source changed")
    expected = {name: (label, row) for name, label, row in cases()}
    rows = json.loads((out / "results.json").read_text())
    if len(rows) != 20 or {r["name"] for r in rows} != set(CONTROLS) | set(expected):
        raise ValueError("wrong case set")
    verified = []
    for rec in rows:
        name, label, value, receipt = rec["name"], rec["label"], rec["value"], rec["receipt"]
        if value is None or receipt["status"] != "completed" or receipt["exit_code"] != 0:
            raise ValueError(f"incomplete result: {name}")
        for suffix, key in (("gp", "script_sha256"), ("stdout", "stdout_sha256"), ("stderr", "stderr_sha256")):
            if sha(out / f"{name}.{suffix}") != receipt[key]:
                raise ValueError(f"transcript hash mismatch: {name}.{suffix}")
        factors = [(int(q), int(e)) for q, e in value["factors"]]
        transcript = [x.strip() for x in (out / f"{name}.stdout").read_text().splitlines() if x.strip()]
        if transcript != [f"COUNT={len(factors)}"] + [f"{q},{e}" for q, e in factors] + ["DONE"]:
            raise ValueError(f"factor transcript mismatch: {name}")
        if any(e < 1 or not ZZ(q).is_prime(proof=True) for q, e in factors):
            raise ValueError(f"unproved prime factor: {name}")
        delta = int(value["delta"])
        if math.prod(q**e for q, e in factors) != abs(delta):
            raise ValueError(f"factor product mismatch: {name}")
        s = -math.prod(q for q, e in factors if e % 2)
        D = s if s % 4 == 1 else 4*s
        if D != int(value["D_K"]):
            raise ValueError(f"fundamental discriminant mismatch: {name}")
        f = int(value["f_pi"])
        if f <= 0 or f*f*D != delta:
            raise ValueError(f"conductor identity mismatch: {name}")
        if name in CONTROLS:
            if label != "control" or (delta, D, f) != CONTROLS[name] or rec["curve_uid"] is not None:
                raise ValueError(f"synthetic control mismatch: {name}")
        else:
            expected_label, source = expected[name]
            p, n = int(source["p_hex"], 16), int(source["n_hex"], 16)
            if label != expected_label or rec["curve_uid"] != source["identity"]["curve_uid"] or delta != (p+1-n)**2-4*p:
                raise ValueError(f"curve binding mismatch: {name}")
        verified.append({"name": name, "label": label, "curve_uid": rec["curve_uid"],
                         "delta": str(delta), "D_K": str(D), "f_pi": str(f),
                         "prime_factors_proved": len(factors)})
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
