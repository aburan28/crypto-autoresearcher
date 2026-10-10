"""Checker for EXP-CZLIFT-bdae69: reproduces the first two primes, re-derives the summary, checks the log_p instrument."""
from __future__ import annotations
import json, os, sys, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run as driver  # noqa: E402


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: check.py RUN_DIR", file=sys.stderr); return 1
    rd = args[0]
    raw = json.load(open(os.path.join(rd, "raw-result.json"))); man = yaml.safe_load(open(os.path.join(rd, "manifest.yaml")))["run"]
    if man["experiment_id"] != driver.EXP_ID or man["status"] != "completed_valid":
        print("manifest mismatch", file=sys.stderr); return 1
    seed, params = man["inputs"]["seed"], man["inputs"]["parameters"]
    primes = raw["raw"]["primes"]
    for pr in primes[:2]:
        if driver.measure_prime(pr["p"], seed=seed, samples=params["samples"]) != pr:
            print(f"p={pr['p']} does not reproduce", file=sys.stderr); return 1
    fresh = driver.summarize(primes)
    if fresh["sections"] != raw["metrics"]["sections"]:
        print("summary does not re-derive", file=sys.stderr); return 1
    # instrument: log_p is a homomorphism on 1 + pZ_p and vanishes on Teichmuller representatives
    p, k = primes[0]["p"], driver.PRECISION; M = p ** k
    u, v = 1 + p * 3, 1 + p * 7
    if (driver.log1p_padic(u, p, k) + driver.log1p_padic(v, p, k) - driver.log1p_padic(u * v % M, p, k)) % M:
        print("log_p is not additive at the test precision", file=sys.stderr); return 1
    if driver.functional(driver.teichmuller(5, p, k), p, k) % M:
        print("functional does not vanish on a Teichmuller representative", file=sys.stderr); return 1
    print("check ok"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
