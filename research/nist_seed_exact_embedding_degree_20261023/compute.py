"""Compute exact prime-subgroup embedding degrees from a pinned factor archive."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCH = ROOT / "research/nist_seed_skipped_curves_20261016"
FACT = ROOT / "research/nist_seed_order_certificate_20261023/runs/certificate-20261023T1747Z"
EXPECTED = {
    ARCH / "assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    ARCH / "traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
    FACT / "results.json": "59dae2376fcc477fcfcf69b8a3d5b592b81c15726d33ca61e2ee7e4bc6c9ec32",
    FACT / "verification.json": "c1375cf10666797817794b46af39c88123b7de9080c02ef75041a6d90afea756",
}
PUB_NAMES = ("prime192v1", "prime192v2", "prime192v3", "prime239v1",
             "prime239v2", "prime239v3", "secp224r1", "prime256v1")
BOUNDS = (100, 1000, 10000, 1000000)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_order(p, n, factors):
    if n < 3 or p % n == 0 or math.prod(q**e for q, e in factors) != n-1:
        raise ValueError("invalid multiplicative-order inputs")
    if n < 1000 and any(n % d == 0 for d in range(2, math.isqrt(n)+1)):
        raise ValueError("nonprime modulus control")
    if pow(p, n-1, n) != 1:
        raise ValueError("Fermat check failed")
    k = n-1
    for q, _ in factors:
        while k % q == 0 and pow(p, k//q, n) == 1:
            k //= q
    if pow(p, k, n) != 1:
        raise ValueError("order upper witness failed")
    k_factors = []
    remainder = k
    for q, _ in factors:
        e = 0
        while remainder % q == 0:
            remainder //= q
            e += 1
        if e:
            if pow(p, k//q, n) == 1:
                raise ValueError("minimality witness failed")
            k_factors.append([str(q), e])
    if remainder != 1:
        raise ValueError("incomplete order factorization")
    return k, k_factors


def curves():
    omitted = json.loads((ARCH / "assessed.json").read_text())["candidate_rows"]
    published = json.loads((ARCH / "traits.json").read_text())["published_controls"]
    cases = []
    for x in omitted:
        p = int(x["p_hex"], 16)
        cases.append((f"omitted_{p.bit_length()}_{x['seed_ordinal_one_based']}", "omitted", x))
    cases.extend((f"published_{name}", "published", published[name]) for name in PUB_NAMES)
    if len(cases) != 19 or len({name for name, _, _ in cases}) != 19:
        raise ValueError("wrong exact curve set")
    return cases


def compute(out, mode):
    if out.exists():
        raise ValueError("output path already exists")
    out.mkdir(parents=True)
    if mode == "exception":
        raise RuntimeError("injected unexpected exception")
    if mode == "early_return":
        return
    for path, digest in EXPECTED.items():
        if sha(path) != digest:
            raise ValueError(f"source digest mismatch: {path}")
    raw = json.loads((FACT / "results.json").read_text())
    checked = json.loads((FACT / "verification.json").read_text())
    if checked["results_sha256"] != EXPECTED[FACT / "results.json"]:
        raise ValueError("factor verification binding mismatch")
    fact_rows = {x["name"]: x for x in raw}
    verified_rows = {x["name"]: x for x in checked["rows"]}
    if len(fact_rows) != len(raw) or len(verified_rows) != len(checked["rows"]):
        raise ValueError("duplicate factor record")
    tests = [(11, 2, [(2, 1), (5, 1)], 10),
             (13, 3, [(2, 2), (3, 1)], 3),
             (17, 4, [(2, 4)], 4)]
    controls = []
    for n, p, factors, expected in tests:
        actual, _ = exact_order(p, n, factors)
        if actual != expected:
            raise ValueError("positive control failed")
        controls.append({"n": n, "p": p, "expected": expected, "actual": actual})
    try:
        exact_order(2, 15, [(2, 1), (7, 1)])
        raise ValueError("negative composite-order control accepted")
    except ValueError as exc:
        if str(exc) != "nonprime modulus control":
            raise
    rows = []
    for name, label, x in curves():
        key = name + "_minus"
        if key not in fact_rows or key not in verified_rows:
            raise ValueError(f"missing factor row: {key}")
        f, v = fact_rows[key], verified_rows[key]
        p, n = int(x["p_hex"], 16), int(x["n_hex"], 16)
        uid = x["identity"]["curve_uid"]
        if (f["label"], f["curve_uid"], int(f["n"]), int(f["number"])) != (label, uid, n, n-1):
            raise ValueError(f"factor identity mismatch: {key}")
        if v["status"] != "verified" or v["curve_uid"] != uid or f["factors"] is None:
            raise ValueError(f"unverified factor row: {key}")
        factors = [(int(q), int(e)) for q, e in f["factors"]]
        k, k_factors = exact_order(p, n, factors)
        rows.append({"name": name, "label": label, "curve_uid": uid,
                     "field_bits": p.bit_length(), "seed_ordinal_one_based": x["seed_ordinal_one_based"],
                     "p": str(p), "n": str(n), "k": str(k), "k_bits": k.bit_length(),
                     "k_decimal_digits": len(str(k)), "k_factors": k_factors,
                     "below_or_equal_bounds": {str(B): k <= B for B in BOUNDS}})
    output = {"schema": "nist-seed-exact-embedding-degree/v1",
              "computed_at_utc": datetime.now(timezone.utc).isoformat(),
              "source_sha256": {str(p.relative_to(ROOT)): h for p, h in EXPECTED.items()},
              "script_sha256": sha(HERE / "compute.py"),
              "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "git_status_during_run": subprocess.check_output(["git", "status", "--porcelain"], text=True).splitlines(),
              "host": platform.platform(), "python": sys.version,
              "controls": controls, "composite_modulus_control_rejected": True,
              "rows": rows}
    (out / "results.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    (out / "complete.ok").write_text("completed after exact certificates\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--mode", choices=("normal", "exception", "early_return"), default="normal")
    args = parser.parse_args()
    compute(args.out, args.mode)
