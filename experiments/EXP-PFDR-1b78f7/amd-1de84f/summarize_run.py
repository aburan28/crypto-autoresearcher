"""raw-result.json summariser for TASK-20260929-f90fed runs (EXP-PFDR-1b78f7, protocol v2).

    summarize_run.py tests  --run-dir D --run-id ID
    summarize_run.py census --run-dir D --run-id ID --panel {main,rho,j0} [--m M]

Counts only: instance statuses against the `cells` enumeration (no silently
missing instance), per-instance gate checks G4-G7, certificate counts, every
failed_infrastructure / invalid instance with its reason, and for the j0 panel
every cell's p, b, N, prime draws and skipped primes (C-1 generation log); for
the main panel any prime coincidence within a rung.  Nothing here computes a
kappa, a rank ratio, a harvest ratio, an exponent or a floor ratio, and nothing
is interpreted.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import xml.etree.ElementTree as ET
from collections import Counter

MAIN_ARMS = ("subgroup", "dickson", "small_x", "random_sub_r0", "random_sub_r1",
             "random_sub_r2", "random_dick_r0", "random_dick_r1", "random_dick_r2")
J0_ARMS = ("j0_coset", "j0_random_r0", "j0_random_r1", "j0_random_r2")
MODES = ("census", "on")
MAIN_BITS = tuple(range(12, 33, 2))
J0_BITS = tuple(range(12, 25, 2))


def rows_of(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def lines_of(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return None
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as fh:
        return sum(1 for l in fh if l.strip())


def expected(panel, m, known_log_max_bits, curves=5, offset=0, rho_curves=10):
    exp = []
    if panel == "main":
        for b in MAIN_BITS:
            for c in range(offset, offset + curves):
                for arm in MAIN_ARMS + ("known_log",):
                    if arm == "known_log" and not (m == 3 and b <= known_log_max_bits):
                        continue
                    for mode in MODES:
                        exp.append(("main", b, c, m, arm, mode))
    elif panel == "j0":
        for b in J0_BITS:
            for c in range(offset, offset + curves):
                for arm in J0_ARMS:
                    for mode in MODES:
                        exp.append(("j0", b, c, 3, arm, mode))
                exp.append(("j0", b, c, None, "rho", None))
    else:
        for b in MAIN_BITS:
            for c in range(offset, offset + rho_curves):
                exp.append(("rho", b, c, None, "rho", None))
    return exp


def key_of(r):
    if r.get("method") == "rho":
        return (r.get("panel"), r["bits"], r["curve"], None, "rho", None)
    m = int(r["method"][4:]) if str(r.get("method", "")).startswith("ic_m") else r.get("m")
    return (r.get("panel"), r["bits"], r["curve"], m, r.get("arm"), r.get("mode"))


def gate_checks(r):
    """Per-instance G4-G7 as visible in the row."""
    out = {}
    h = r.get("harvest")
    if h:
        cls = {}
        for c in ("TT", "TB", "SS"):
            st = h[c]["at_stop"]
            cls[c] = {"cert_pass": st["cert_pass"], "cert_fail": st["cert_fail"],
                      "rows_emitted": st["rows_emitted"],
                      "ok": st["cert_fail"] == 0 and st["cert_pass"] == st["rows_emitted"]}
        out["G4_rows"] = cls
        out["G5_identity_ok"] = bool(h["ss_store"]["identity_ok"])
    if r.get("k_found"):
        out["G4_kP_eq_Q"] = bool(r.get("k_verified"))
    for k, v in (r.get("checks") or {}).items():
        out[k] = v
    return out


def cmd_tests(a):
    rd = a.run_dir
    ex = json.load(open(os.path.join(rd, "execution.json")))
    root = ET.parse(os.path.join(rd, "junit.xml")).getroot()
    suites = [root] if root.tag == "testsuite" else list(root)
    tot = Counter()
    skipped, failed = [], []
    for s in suites:
        for k in ("tests", "failures", "errors", "skipped"):
            tot[k] += int(s.get(k, 0))
        for tc in s.iter("testcase"):
            name = f"{tc.get('classname')}::{tc.get('name')}"
            sk = tc.find("skipped")
            if sk is not None:
                skipped.append({"test": name, "reason": sk.get("message")})
            if tc.find("failure") is not None or tc.find("error") is not None:
                failed.append(name)
    passed = tot["tests"] - tot["failures"] - tot["errors"] - tot["skipped"]
    g3 = ex["exit_code"] == 0 and tot["failures"] == 0 and tot["errors"] == 0 and not ex["watchdog_expired"]
    raw = {"run_id": a.run_id, "experiment_id": "EXP-PFDR-1b78f7", "exit_code": ex["exit_code"],
           "watchdog_expired": ex["watchdog_expired"], "junit_totals": dict(tot), "passed": passed,
           "failed_tests": failed, "skipped_tests": skipped,
           "G3_pass": g3, "E-5_pass": g3,
           "certificate": {"kind": "none", "note": "unit tests; no solve or relation claimed"}}
    json.dump(raw, open(os.path.join(rd, "raw-result.json"), "w"), indent=2, sort_keys=True)
    print(json.dumps({k: raw[k] for k in ("G3_pass", "passed", "junit_totals")}, indent=2))
    return 0


def cmd_census(a):
    rd = a.run_dir
    ex = json.load(open(os.path.join(rd, "execution.json")))
    rows = rows_of(os.path.join(rd, "rows.jsonl"))
    exp = expected(a.panel, a.m, a.known_log_max_bits, a.curves, a.curve_offset, a.rho_curves)
    got = Counter(key_of(r) for r in rows)
    missing = [list(k) for k in exp if got[k] == 0]
    dup = [list(k) for k, n in got.items() if n > 1]
    extra = [list(k) for k in got if k not in set(exp)]
    by_status = Counter()
    for r in rows:
        k = key_of(r)
        by_status[f"{k[0]}|{k[4]}|{k[5] or '-'}|{r.get('status')}"] += 1
    status_tot = Counter(r.get("status") for r in rows)
    failed = [{"key": list(key_of(r)), "status_reason": r.get("status_reason"),
               "ru_maxrss_bytes": r.get("ru_maxrss_bytes"), "seconds": r.get("seconds")}
              for r in rows if r.get("status") == "failed_infrastructure"]
    invalid = [{"key": list(key_of(r)), "status_reason": r.get("status_reason")}
               for r in rows if r.get("status") == "invalid"]
    # gates per harvest instance
    g4_rows_bad, g4_k_bad, g5_bad, g67 = [], [], [], Counter()
    cert = Counter()
    harvest_instances = solved = verified = 0
    per_instance = []
    for r in rows:
        gc = gate_checks(r)
        if r.get("harvest"):
            harvest_instances += 1
            for c, v in gc["G4_rows"].items():
                cert[f"{c}_cert_pass"] += v["cert_pass"]
                cert[f"{c}_cert_fail"] += v["cert_fail"]
                cert[f"{c}_rows_emitted"] += v["rows_emitted"]
                if not v["ok"]:
                    g4_rows_bad.append(list(key_of(r)) + [c])
            if not gc["G5_identity_ok"]:
                g5_bad.append(list(key_of(r)))
        if r.get("k_found") or (r.get("method") == "rho" and r.get("status") != "failed_infrastructure"):
            solved += 1
            ok = gc.get("G4_kP_eq_Q", r.get("ok")) if r.get("method") != "rho" else bool(r.get("ok"))
            verified += bool(ok)
            if not ok:
                g4_k_bad.append(list(key_of(r)))
        for k, v in gc.items():
            if k.startswith(("G6", "G7")):
                g67[f"{k}|{'pass' if v else 'fail'}"] += 1
        if r.get("harvest") or r.get("checks"):
            per_instance.append({"key": list(key_of(r)), "status": r.get("status"),
                                 "G4": (all(v["ok"] for v in gc["G4_rows"].values()) if "G4_rows" in gc else None),
                                 "G4_kP_eq_Q": gc.get("G4_kP_eq_Q"),
                                 "G5": gc.get("G5_identity_ok"),
                                 "G6_G7": {k: v for k, v in gc.items() if k.startswith(("G6", "G7"))}})
    raw = {"run_id": a.run_id, "experiment_id": "EXP-PFDR-1b78f7", "panel": a.panel, "m": a.m,
           "exit_code": ex["exit_code"], "watchdog_expired": ex["watchdog_expired"],
           "instances": {"expected": len(exp), "present": len(rows), "missing": missing,
                         "duplicates": dup, "unexpected": extra},
           "status_totals": dict(status_tot), "by_panel_arm_mode_status": dict(sorted(by_status.items())),
           "failed_infrastructure": failed, "invalid": invalid,
           "gates": {"harvest_instances": harvest_instances,
                     "G4": {"pass": not g4_rows_bad and not g4_k_bad,
                            "row_certificate_failures": g4_rows_bad, "k_not_verified": g4_k_bad,
                            "solved_instances": solved, "solved_verified": verified},
                     "G5": {"pass": not g5_bad, "identity_failures": g5_bad},
                     "G6_G7_check_counts": dict(sorted(g67.items())),
                     "G6_G7_pass": not any(k.endswith("|fail") for k in g67)},
           "gates_per_instance": per_instance,
           "harvest_rows_lines": lines_of(os.path.join(rd, "harvest-rows.jsonl")),
           "staircase_lines": lines_of(os.path.join(rd, "staircase.jsonl")),
           "certificate": {"kind": "discrete_log" if solved else "none",
                           "verifier": "kP == Q by curve.py scalar multiplication (solver `verified`; rho `verified`)",
                           "solved_instances": solved, "verified": verified,
                           "harvested_row_check": dict(cert),
                           "harvested_row_check_note": ("each harvested row re-verified as sum c_i F_i + kcoef Q == rhs P "
                                                        "on an independent Curve instance before any elimination")}}
    if a.panel == "j0":
        cells = {}
        for r in rows:
            k = (r["bits"], r["curve"])
            if k in cells or "j0_generation" not in r:
                continue
            log = r["j0_generation"]
            fin = log[-1] if log and "prime_draws" in log[-1] else {}
            cells[k] = {"bits": r["bits"], "curve": r["curve"], "p": r.get("p"), "b": r.get("b"),
                        "N": r.get("N"), "prime_draws": fin.get("prime_draws"),
                        "skipped_primes": [e for e in log if "reason" in e]}
        raw["j0_cells"] = [cells[k] for k in sorted(cells)]
        raw["j0_cells_count"] = len(cells)
        per_rung = {}
        for (b, c), v in sorted(cells.items()):
            per_rung.setdefault(b, []).append(v["p"])
        raw["j0_distinct_primes_per_rung"] = {str(b): len(set(ps)) == len(ps) for b, ps in per_rung.items()}
    if a.panel in ("main", "rho"):
        seen = {}
        for r in rows:
            if r.get("p") is not None:  # job-crash rows carry no curve fields
                seen.setdefault(r["bits"], {})[r["curve"]] = r["p"]
        coinc = []
        for b, cp in sorted(seen.items()):
            inv = {}
            for c, p in cp.items():
                inv.setdefault(p, []).append(c)
            coinc += [{"bits": b, "p": p, "curves": sorted(cs)} for p, cs in inv.items() if len(cs) > 1]
        raw["prime_coincidences_within_rung"] = coinc
    json.dump(raw, open(os.path.join(rd, "raw-result.json"), "w"), indent=2, sort_keys=True)
    print(json.dumps({"instances": {k: (v if isinstance(v, int) else len(v)) for k, v in raw["instances"].items()},
                      "status_totals": raw["status_totals"],
                      "G4": raw["gates"]["G4"]["pass"], "G5": raw["gates"]["G5"]["pass"],
                      "G6_G7": raw["gates"]["G6_G7_pass"],
                      "failed_infrastructure": len(failed), "invalid": len(invalid)}, indent=2))
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tests")
    t.add_argument("--run-dir", required=True)
    t.add_argument("--run-id", required=True)
    c = sub.add_parser("census")
    c.add_argument("--run-dir", required=True)
    c.add_argument("--run-id", required=True)
    c.add_argument("--panel", required=True, choices=("main", "rho", "j0"))
    c.add_argument("--m", type=int, default=None)
    c.add_argument("--known-log-max-bits", type=int, default=0)
    c.add_argument("--curves", type=int, default=5)
    c.add_argument("--curve-offset", type=int, default=0)
    c.add_argument("--rho-curves", type=int, default=10)
    a = ap.parse_args()
    return {"tests": cmd_tests, "census": cmd_census}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
