#!/usr/bin/env python3
"""Exact Atkin trace sets and a declared residue-density comparison."""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / "research/nist_seed_1997_selection_extension_20261023/sea_signature/runs/scan-20261023T1840Z/raw.json"
INPUT_SHA = "4a0df1de260e4533253ef591f7b084b73e86fac5e03558ec3609081c750f48fe"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primes(bound):
    return [n for n in range(3, bound+1, 2) if all(n % d for d in range(2, int(n**0.5)+1))]


def legendre(x, ell):
    x %= ell
    return 0 if x == 0 else (1 if pow(x, (ell-1)//2, ell) == 1 else -1)


def mul(a, b, ell):
    return tuple((a[i*2] * b[j] + a[i*2+1] * b[j+2]) % ell for i in range(2) for j in range(2))


def mpow(a, exponent, ell):
    result = (1, 0, 0, 1)
    while exponent:
        if exponent & 1:
            result = mul(result, a, ell)
        a = mul(a, a, ell)
        exponent //= 2
    return result


def scalar(a):
    return a[1] == a[2] == 0 and a[0] == a[3] != 0


def projective_order(trace, p, ell):
    assert legendre(trace*trace-4*p, ell) == -1
    a = (0, -p % ell, 1, trace % ell)
    order = ell+1
    assert scalar(mpow(a, order, ell))
    n = order
    factors = []
    for q in range(2, int(n**0.5)+1):
        if n % q == 0:
            factors.append(q)
            while n % q == 0:
                n //= q
    if n > 1:
        factors.append(n)
    for q in factors:
        while order % q == 0 and scalar(mpow(a, order//q, ell)):
            order //= q
    return order


def audit():
    assert digest(INPUT) == INPUT_SHA
    source = json.loads(INPUT.read_text())
    odd_primes = primes(997)
    assert len(odd_primes) == 167 and len(source["rows"]) == 19
    tables = {}
    rows = []
    for prior in source["rows"]:
        p, n = int(prior["p_hex"], 16), int(prior["n_hex"], 16)
        t = p+1-n
        assert t == int(prior["trace_hex_signed"], 16) and t*t <= 4*p
        cells, M, ambiguity, elkies_product = [], 1, 1, 1
        cutoff, old_cutoff = None, None
        for ell in odd_primes:
            chi = legendre(t*t-4*p, ell)
            r = None
            if chi == 1:
                allowed = [t % ell]
                kind = "elkies"
                elkies_product *= ell
            elif chi == 0:
                allowed = [u for u in range(ell) if (u*u-4*p) % ell == 0]
                kind = "ramified"
            else:
                key = (p % ell, ell)
                if key not in tables:
                    grouped = defaultdict(list)
                    for u in range(ell):
                        if legendre(u*u-4*p, ell) == -1:
                            grouped[projective_order(u, p, ell)].append(u)
                    tables[key] = grouped
                r = projective_order(t, p, ell)
                allowed = tables[key][r]
                assert allowed == tables[key][projective_order(-t, p, ell)]
                kind = "atkin"
            assert t % ell in allowed
            M *= ell
            ambiguity *= len(allowed)
            if cutoff is None and M*M > 16*p*ambiguity*ambiguity:
                cutoff = ell
            if old_cutoff is None and elkies_product*elkies_product > 16*p:
                old_cutoff = ell
            cells.append({"ell": ell, "type": kind, "r": r, "allowed": allowed, "size": len(allowed)})
        assert old_cutoff == prior["cutoff_ell"]
        rows.append({k: prior[k] for k in ("name", "curve_uid", "field_bits", "label", "p_hex", "n_hex", "trace_hex_signed") } | {"cells": cells, "residue_density_cutoff": cutoff, "elkies_only_cutoff": old_cutoff})
    comparisons = []
    for omit in rows:
        if omit["label"] != "omitted":
            continue
        for pub in rows:
            if pub["label"] == "published" and pub["p_hex"] == omit["p_hex"]:
                a, b = omit["residue_density_cutoff"], pub["residue_density_cutoff"]
                assert a is not None and b is not None
                comparisons.append({"omitted": omit["name"], "published": pub["name"], "omitted_cutoff": a, "published_cutoff": b, "omitted_lower": a < b, "published_lower": b < a, "tie": a == b})
    assert len(comparisons) == 25
    assert projective_order(0, 1, 3) == 2
    assert scalar(mpow((2, 0, 0, 2), 1, 5))
    assert not (4*4 > 16) and 5*5 > 16
    return {"odd_primes": odd_primes, "rows": rows, "comparisons": comparisons, "pair_summary": {k: sum(c[k] for c in comparisons) for k in ("omitted_lower", "published_lower", "tie")}, "real_cells": sum(len(r["cells"]) for r in rows), "synthetic_controls_passed": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    start = datetime.now(timezone.utc).isoformat()
    wall, cpu = time.monotonic(), time.process_time()
    receipt = {"command": sys.argv, "cwd": str(Path.cwd()), "python": sys.version, "platform": platform.platform(), "started_utc": start, "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(), "dirty": subprocess.check_output(["git", "status", "--porcelain"], text=True), "input_sha256": digest(INPUT), "protocol_sha256": digest(HERE/"PROTOCOL.md"), "code_sha256": digest(Path(__file__)), "source_pdf_sha256": digest(Path("/private/tmp/nist-seed-schoof1995.pdf"))}
    assert receipt["source_pdf_sha256"] == "9971fd4f8aae23fa9578967e20af5d27b7849e5f0d614b16cc5cb1346b095715"
    (args.out/"started.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    try:
        raw = audit()
        (args.out/"raw.json").write_text(json.dumps(raw, indent=2, sort_keys=True)+"\n")
        receipt["status"] = "completed"
        receipt["raw_sha256"] = digest(args.out/"raw.json")
        message = json.dumps({"cells": raw["real_cells"], "pairs": raw["pair_summary"]})
        (args.out/"stdout.log").write_text(message+"\n")
        (args.out/"stderr.log").write_text("")
        print(message)
    except BaseException:
        receipt["status"] = "failed"
        (args.out/"stderr.log").write_text(traceback.format_exc())
        raise
    finally:
        receipt.update({"finished_utc": datetime.now(timezone.utc).isoformat(), "wall_seconds": time.monotonic()-wall, "cpu_seconds": time.process_time()-cpu})
        (args.out/"receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")


if __name__ == "__main__":
    main()
