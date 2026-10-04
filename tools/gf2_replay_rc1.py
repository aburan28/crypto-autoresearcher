#!/usr/bin/env python3
"""Re-run the whole RC-1 closure workload on the fast GF(2) engine and compare.

Recomputes every closure record of RUN-CERTBIN-c417e0 (EXP-CERTBIN-e94b27:
M_3, M_4, W_4, M_5 on U62/S62/C20/N-AFF62/N-F262, W_5 on the 10 S62 cases)
and every certificate with ``crypto_autoresearcher.gf2.closure``, and checks
them field for field against the archived records. Also reports the new wall
time next to the archived ``wall_seconds``.

This reads the archived run package only; it writes nothing into it, launches
no trial and assigns no RUN id. It is an engine regression and benchmark, not
evidence about any hypothesis.

    python3 tools/gf2_replay_rc1.py [--threads N] [--limit K] [--json OUT]
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RUN = ROOT / "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
IMPL = ROOT / "experiments/EXP-CERTBIN-e94b27/impl"

from crypto_autoresearcher.gf2 import closure as fc  # noqa: E402
from crypto_autoresearcher.gf2 import kernels  # noqa: E402

# Fields the archived driver added around the engine's own record.
DRIVER_FIELDS = {"wall_seconds", "label", "role", "certificate", "key", "set", "idx", "closure",
                 "engine_self_check_sum_is_1", "ell_in_W4_le1"}
NV, NEQ = 18, 17


def load_eqs():
    """key -> list of 17 lists of monomial masks, decoded with the archived
    E_hex convention (EXP-CERTBIN-e94b27 impl/instances.py, read-only import)."""
    sys.path.insert(0, str(IMPL))
    sys.dont_write_bytecode = True
    try:
        from instances import E_from_hex
        from macaulay import EQ_MONS
    finally:
        sys.path.remove(str(IMPL))
    sets = json.loads((RUN / "instance-sets.json").read_text())["sets"]
    out = {}
    for recs in sets.values():
        for r in recs:
            E = E_from_hex(r["E_hex"])
            out[r["key"]] = [[fc.mono_mask(EQ_MONS[j]) for j in np.flatnonzero(E[k])] for k in range(NEQ)]
    return out


def run_one(job, eqs, closures):
    rec, cert_ref = job
    kind, D = rec["closure"][0], int(rec["closure"][2])
    cl = closures[D]
    t = time.perf_counter()
    if kind == "M":
        got, cert = cl.macaulay_closure(eqs[rec["key"]], want_cert=cert_ref is not None)
    else:
        got, cert = cl.w_closure(eqs[rec["key"]], want_cert=cert_ref is not None)
    wall = time.perf_counter() - t
    want = {k: v for k, v in rec.items() if k not in DRIVER_FIELDS}
    diffs = [k for k in want if got.get(k) != want[k]]
    cert_ok = None
    if cert_ref is not None:
        cert_ok = cert is not None and fc.cert_to_json(cert) == cert_ref["C"]
        if cert_ok and fc.eval_cert(cert, eqs[rec["key"]]) != [0]:
            cert_ok = False
    return {"key": rec["key"], "closure": rec["closure"], "field_diffs": diffs, "cert_ok": cert_ok,
            "wall_new": wall, "wall_archived": rec.get("wall_seconds")}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--limit", type=int, default=None, help="first K records only")
    ap.add_argument("--json", help="write the per-record results here")
    a = ap.parse_args()

    rows = [json.loads(line) for line in gzip.open(RUN / "closures.jsonl.gz", "rt")]
    certs = {(c["key"], c["closure"]): c for c in map(json.loads, gzip.open(RUN / "certificates.jsonl.gz", "rt"))}
    if a.limit:
        rows = rows[:a.limit]
    eqs = load_eqs()
    closures = {D: fc.Closure(NV, D, NEQ) for D in (3, 4, 5)}
    jobs = [(r, certs.get((r["key"], r["closure"]))) for r in rows]
    # big jobs first so the pool drains evenly
    jobs.sort(key=lambda j: -(j[0].get("wall_seconds") or 0))
    t0 = time.perf_counter()
    res = kernels.map_threads(lambda j: run_one(j, eqs, closures), jobs, a.threads)
    elapsed = time.perf_counter() - t0

    bad = [r for r in res if r["field_diffs"] or r["cert_ok"] is False]
    ncert = sum(r["cert_ok"] is not None for r in res)
    arch = sum(r["wall_archived"] or 0 for r in res)
    new = sum(r["wall_new"] for r in res)
    by = {}
    for r in res:
        b = by.setdefault(r["closure"], [0, 0.0, 0.0])
        b[0] += 1
        b[1] += r["wall_archived"] or 0
        b[2] += r["wall_new"]
    print(f"backend: {kernels.backend()}  threads: {a.threads or kernels.default_threads()}")
    print(f"records: {len(res)}  certificates checked: {ncert}  mismatches: {len(bad)}")
    print(f"{'closure':8} {'n':>4} {'archived s':>11} {'new s':>8} {'speedup':>8}")
    for k in sorted(by):
        n, sa, sn = by[k]
        print(f"{k:8} {n:4d} {sa:11.1f} {sn:8.1f} {sa / sn if sn else float('nan'):7.1f}x")
    print(f"{'total':8} {len(res):4d} {arch:11.1f} {new:8.1f} {arch / new if new else float('nan'):7.1f}x"
          f"   (wall clock with the pool: {elapsed:.1f} s, {arch / elapsed:.1f}x)")
    for r in bad[:20]:
        print("MISMATCH", r)
    if a.json:
        Path(a.json).write_text(json.dumps({"backend": kernels.backend(), "results": res,
                                            "elapsed": elapsed}, indent=1))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
