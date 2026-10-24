"""Independent exact verification of first-stage conductor factors with Sage."""
import hashlib
import json
import math
from pathlib import Path
import sys
from datetime import datetime, timezone

from sage.all import ZZ

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCH = ROOT / "research/nist_seed_skipped_curves_20261016"
EXPECTED = {
    "control_neg75": (-75, -3, 5),
    "control_neg7": (-7, -7, 1),
    "control_neg12": (-12, -3, 2),
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(out):
    if (out / "verification.json").exists() or (out / "complete.ok").exists():
        raise ValueError("verification output already exists")
    started = json.loads((out / "started.json").read_text())
    rows = json.loads((out / "results.json").read_text())
    if len(rows) != 5 or {r["name"] for r in rows} != set(EXPECTED) | {"omitted_p256_876", "published_p256_1842"}:
        raise ValueError("wrong case set")
    for name, digest in started["source_sha256"].items():
        if sha(ARCH / name) != digest:
            raise ValueError("source hash mismatch")
    assessed = json.loads((ARCH / "assessed.json").read_text())["candidate_rows"]
    controls = json.loads((ARCH / "traits.json").read_text())["published_controls"]
    omitted = next(x for x in assessed if x["timestamp"] == 871696354 and x["seed_ordinal_one_based"] == 876)
    pub = controls["prime256v1"]
    real = {"omitted_p256_876": omitted, "published_p256_1842": pub}
    verified = []
    for rec in rows:
        name, value, receipt = rec["name"], rec["value"], rec["receipt"]
        if receipt["status"] != "completed" or receipt["exit_code"] != 0 or value is None:
            raise ValueError(f"incomplete factorization: {name}")
        for suffix, key in [("gp", "script_sha256"), ("stdout", "stdout_sha256"), ("stderr", "stderr_sha256")]:
            if sha(out / f"{name}.{suffix}") != receipt[key]:
                raise ValueError(f"raw hash mismatch: {name}.{suffix}")
        lines = [s.strip() for s in (out / f"{name}.stdout").read_text().splitlines() if s.strip()]
        factors = [(int(q), int(e)) for q, e in value["factors"]]
        if lines[0] != f"COUNT={len(factors)}" or lines[-1] != "DONE":
            raise ValueError(f"framing mismatch: {name}")
        if [f"{q},{e}" for q, e in factors] != lines[1:-1]:
            raise ValueError(f"factor transcript mismatch: {name}")
        if any(e < 1 or not ZZ(q).is_prime(proof=True) for q, e in factors):
            raise ValueError(f"unproved prime factor: {name}")
        delta = int(value["delta"])
        if math.prod(q**e for q, e in factors) != abs(delta):
            raise ValueError(f"incomplete factor product: {name}")
        s = -math.prod(q for q, e in factors if e % 2)
        if s % 4 == 1:
            D = s
        else:
            D = 4*s
            if s % 4 not in (2, 3):
                raise ValueError(f"invalid fundamental part: {name}")
        f = int(value["f_pi"])
        if D != int(value["D_K"]) or f <= 0 or f*f*D != delta:
            raise ValueError(f"discriminant identity mismatch: {name}")
        if name in EXPECTED:
            if (delta, D, f) != EXPECTED[name] or rec["curve_uid"] is not None:
                raise ValueError(f"synthetic control failed: {name}")
        else:
            source = real[name]
            p, n = int(source["p_hex"], 16), int(source["n_hex"], 16)
            if rec["curve_uid"] != source["identity"]["curve_uid"]:
                raise ValueError(f"curve identity mismatch: {name}")
            if delta != (p + 1 - n)**2 - 4*p:
                raise ValueError(f"source discriminant mismatch: {name}")
        verified.append({"name": name, "curve_uid": rec["curve_uid"],
                         "delta": str(delta), "D_K": str(D), "f_pi": str(f),
                         "prime_factors_proved": len(factors)})
    (out / "verification.json").write_text(json.dumps({
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "verifier_sha256": sha(HERE / "verify.py"),
        "results_sha256": sha(out / "results.json"), "rows": verified,
    }, indent=2) + "\n")
    print(out / "verification.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: sage -python verify.py RUN_DIR")
    main(Path(sys.argv[1]))
