#!/usr/bin/env python3
"""TASK-20260928-3f90b8 -- UNASSIGNED-JOINT finding (overlaps J1), surfaced while
building J2's "tabulate more summands" mutant: the contract's MITM relation
phase omits the one-time construction of the oracle's table.

Every entry of an MITM table is a group element that must be computed, so a
store of 2^S entries costs at least ~2^S group operations to fill. Under the
contract's per-call MITM accounting that cost is dominated by any single oracle
call -- IF at least one call is made. This audit checks, on the COMMITTED
raw-result of RUN-SEMBIN-c68773, whether the reported sub-rho cells live in the
regime where that holds.

For every non-degenerate cell reported as beating the vOW baseline, in
mitm_store_free, mitm_capped and min_store_for_subrho, it computes:

  log2_total_calls = log2(|F| / p) = d + log2 m! + log2 N - m d
                     (total oracle calls the model charges, over all relations)
  log2_table_build = s * d                   (entries tabulated, each computed)
  corrected_total  = log2(2^total + 2^build)  (table construction counted once)

and reports whether any sub-rho cell survives the corrected total. It also
records the generic-group reading (KN-LIT-011): with the table built,
table x probes >= |F| * m! * N, so time >= 2*sqrt(m! N |F|) > sqrt(N).

Usage: python3 build_term_audit.py [--out build_term_audit.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
RAW = os.path.join(REPO, "experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773/raw-result.json")
RAW_SHA256 = "9569c9c099172ea9f6367b79a3f0cce7cfa1b781f0650a56f48cfae54e8e5126"
HERE = os.path.dirname(os.path.abspath(__file__))
ECC2K130_R = 680564733841876926932320129493409985129


def log2_fact(m: int) -> float:
    return math.lgamma(m + 1) / math.log(2.0)


def log2N(n: int) -> float:
    return math.log2(ECC2K130_R) if n == 131 else float(n)


def lse2(a: float, b: float) -> float:
    hi, lo = max(a, b), min(a, b)
    return hi + math.log2(1.0 + 2.0 ** (lo - hi))


def audit_cell(n, m, d, s, total, rho):
    calls = d + log2_fact(m) + log2N(n) - m * d
    build = s * d
    corrected = lse2(total, build)
    return {"n": n, "m": m, "d": d, "s": s, "log2_total_reported": total,
            "log2_rho_vow": rho, "log2_total_oracle_calls": round(calls, 4),
            "log2_table_build": round(build, 4),
            "build_exceeds_reported_total_by_bits": round(build - total, 4),
            "build_exceeds_rho_by_bits": round(build - rho, 4),
            "corrected_total": round(corrected, 4),
            "corrected_beats_rho": corrected < rho}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "build_term_audit.json"))
    args = ap.parse_args()
    blob = open(RAW, "rb").read()
    got = hashlib.sha256(blob).hexdigest()
    if got != RAW_SHA256:
        raise SystemExit(f"raw-result sha256 {got} != committed {RAW_SHA256}; refusing")
    raw = json.loads(blob)

    out = {"task_id": "TASK-20260928-3f90b8", "raw_result_sha256": got, "families": {}}
    for fam in ("mitm_store_free", "mitm_capped"):
        cells = [c for c in raw[fam] if c["beats_vow"] and not c["degenerate"]]
        audited = [audit_cell(c["n"], c["m"], c["d"], c["s_tabulated"],
                              c["log2_total"], c["log2_rho_vow"]) for c in cells]
        uniq = {(a["n"], a["m"], a["d"], a["s"]) for a in audited}
        out["families"][fam] = {
            "subrho_cells_reported": len(cells),
            "distinct_(n,m,d,s)": len(uniq),
            "all_have_fewer_than_one_total_oracle_call":
                all(a["log2_total_oracle_calls"] < 0 for a in audited),
            "max_log2_total_oracle_calls": max((a["log2_total_oracle_calls"] for a in audited), default=None),
            "all_table_builds_exceed_reported_total":
                all(a["build_exceeds_reported_total_by_bits"] > 0 for a in audited),
            "all_table_builds_exceed_rho":
                all(a["build_exceeds_rho_by_bits"] > 0 for a in audited),
            "min_build_excess_over_rho_bits": min((a["build_exceeds_rho_by_bits"] for a in audited), default=None),
            "subrho_cells_after_charging_build": sum(a["corrected_beats_rho"] for a in audited),
            "examples": sorted(audited, key=lambda a: (a["n"], a["m"]))[:3],
        }
    ms = [r for r in raw["min_store_for_subrho"] if r.get("reachable")]
    aud = []
    for r in ms:
        s = r["m"] // 2
        rho = r["target"]
        aud.append(audit_cell(r["n"], r["m"], r["d"], s, r["log2_total"], rho))
    out["families"]["min_store_for_subrho"] = {
        "reachable_rows": len(aud),
        "all_have_fewer_than_one_total_oracle_call": all(a["log2_total_oracle_calls"] < 0 for a in aud),
        "all_table_builds_exceed_rho": all(a["build_exceeds_rho_by_bits"] > 0 for a in aud),
        "subrho_rows_after_charging_build": sum(a["corrected_beats_rho"] for a in aud),
        "ecc2k130_m8": next((a for a in aud if a["n"] == 131 and a["m"] == 8), None),
    }
    # The generic-group reading: with a table of T entries (built) and Q probes,
    # expected relations = T*Q*|F|^... ; the contract's own formulas give
    # T*Q = |F|^s * (|F| * m! N / |F|^m) * |F|^(m-s) = m! * N * |F|.  So
    # T + Q >= 2*sqrt(m! N |F|), which exceeds the vOW baseline 0.886*sqrt(N)
    # by 1.175 + (log2 m! + d)/2 bits -- positive for every m >= 2, d >= 0.
    worst = min(1 + (log2_fact(m) + d + log2N(n)) / 2 - (log2N(n) / 2 + math.log2(0.886))
                for n in (97, 109, 131, 163, 571) for m in range(2, 17) for d in (1.0, 5.0, 10.0))
    out["generic_group_reading"] = {
        "statement": "with the table's construction counted, T*Q = m! N |F|, so the "
                     "relation phase alone is >= 2*sqrt(m! N |F|) > 0.886*sqrt(N) at "
                     "every (n, m, d): no MITM cell can beat the vOW baseline at ANY store",
        "min_excess_over_vow_bits_on_grid": round(worst, 4),
        "consistent_with": "KN-LIT-011 (Shoup 1997): generic algorithms need Omega(sqrt p)",
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    for k, v in out["families"].items():
        print(k, {kk: vv for kk, vv in v.items() if kk not in ("examples", "ecc2k130_m8")})
    print("ecc2k130 m=8:", out["families"]["min_store_for_subrho"]["ecc2k130_m8"])
    print(out["generic_group_reading"])


if __name__ == "__main__":
    main()
