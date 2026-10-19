#!/usr/bin/env python3
"""Native G trial producer. --self-test checks software fixtures only.

The original pilot's square-multiplicity arithmetic is extended to both frozen
panels and reverse enumeration. Only the native supervisor may launch a census.
No Jacobian evaluator or independently verified genus-three polynomial is supplied.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import threading
import time

import sympy as sp
import yaml

EXP = "EXP-ECDLP-da4ba3"
ROOT = Path(__file__).resolve().parents[2]
CONFIG = "research/prym_experiment_design_20261019/geometry_inputs.json"
T = sp.Symbol("T")
LIMITS = [
    "Exact Fp/Fp2 point counts and rational polynomial screens only.",
    "D has genus three: two counted traces do not independently verify its full Frobenius polynomial.",
    "F_D_candidate is inferred from the geometric decomposition E x J(H).",
    "No Jacobian map, subgroup action, ECDLP recovery, speedup or security claim.",
    "F43 (a,b)=(0,1) is previously seen calibration; synthetic inputs are screen controls only.",
]


class GroupMemory:
    """Sample Linux process-group RSS; retain sampling interval and monitor loss."""
    def __init__(self):
        self.peak = 0
        self.errors = []
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.monitor, daemon=True)

    def sample(self):
        total, members = 0, 0
        for proc in Path("/proc").iterdir():
            if not proc.name.isdecimal():
                continue
            try:
                fields = (proc/"stat").read_text().rsplit(")", 1)[1].split()
                if int(fields[2]) != os.getpgrp():
                    continue
                total += int(fields[21])*os.sysconf("SC_PAGE_SIZE")
                members += 1
            except FileNotFoundError:
                continue  # exited while being sampled
            except PermissionError:
                continue  # another uid's process, outside this trial group
        if not members:
            raise RuntimeError("cannot sample trial process group")
        self.peak = max(self.peak, total)

    def monitor(self):
        while not self.stop.wait(0.05):
            try:
                self.sample()
            except Exception as exc:
                self.errors.append(f"{type(exc).__name__}: {exc}")
                return

    def __enter__(self):
        self.sample()
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.stop.set()
        self.thread.join()
        self.sample()


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def config(path):
    cfg = json.loads(Path(path).read_text())
    expected = {"schema": "prym-geometry-input/v1", "experiment_id": EXP,
                "primes": [11, 13, 17, 19, 23, 31, 43, 59],
                "f_coefficients_descending": [1, 0, 0, 7], "covers_per_prime": 8,
                "extension_degrees": [1, 2]}
    if any(cfg.get(k) != v for k, v in expected.items()):
        raise ValueError("unsupported frozen configuration")
    return cfg


def catalogue(p):
    selected, inspected = [], []
    for rank, (a, b) in enumerate(combinations(range(p), 2)):
        roots = [x for x in (a, b) if (x**3 + 7) % p == 0]
        event = {"event": "candidate_pair", "p": p, "a": a, "b": b,
                 "lexicographic_rank": rank, "accepted": not roots,
                 "reason": "f_root_at_cover_branch" if roots else "eligible",
                 "f_root_branches": roots}
        if not roots:
            event.update(panel="primary" if len(selected) < 8 else "companion",
                         eligible_index=len(selected))
            selected.append((a, b))
        inspected.append(event)
        if len(selected) == 16:
            break
    if len(selected) != 16:
        raise ValueError("insufficient fixed eligible pairs")
    return selected, inspected


def count(p, a, b, degree, reverse=False):
    """Independent D affine count: multiply numbers of y and z roots at x."""
    ops = Counter()
    d = None if degree == 1 else next(x for x in range(1, p)
                                    if pow(x, (p-1)//2, p) == p-1)
    if degree not in (1, 2):
        raise ValueError("extension degree must be 1 or 2")
    elems = list(range(p)) if degree == 1 else [(u, v) for u in range(p) for v in range(p)]
    if reverse:
        elems.reverse()
    def const(z):
        return z % p if degree == 1 else (z % p, 0)
    def add(x, y):
        ops["field_additions"] += 1
        return (x+y) % p if degree == 1 else ((x[0]+y[0]) % p, (x[1]+y[1]) % p)
    def mul(x, y):
        ops["field_multiplications"] += 1
        return x*y % p if degree == 1 else ((x[0]*y[0]+d*x[1]*y[1]) % p,
                                           (x[0]*y[1]+x[1]*y[0]) % p)
    squares = Counter(mul(y, y) for y in elems)
    ne, nh, nd = 1, 1, 2
    for x in elems:
        fx = add(mul(mul(x, x), x), const(7))
        hx = mul(add(x, const(-a)), add(x, const(-b)))
        ne += squares[fx]
        nh += squares[mul(fx, hx)]
        nd += squares[fx] * squares[hx]
        ops["square_table_lookups"] += 4
        ops["affine_x_visits"] += 1
    return {"degree": degree, "q": p**degree, "nonresidue": d,
            "field_polynomial": [1, 0, -d] if d is not None else None,
            "N_E": ne, "N_H": nh, "N_D": nd,
            "infinity_points": {"E": 1, "H": 1, "D": 2},
            "operation_vector": dict(ops), "square_table_entries": len(squares),
            "peak_live_field_words_upper_bound": (degree*(len(elems)+len(squares)+12))}


def reciprocal(coeff, p):
    n = len(coeff)-1
    return (n > 0 and n % 2 == 0 and coeff[0] == 1
            and all(coeff[n-i] == coeff[i]*p**(n//2-i) for i in range(n//2+1)))


def polynomial_screen(p, fe, fh):
    e, h = (sp.Poly.from_list(c, T, domain=sp.QQ) for c in (fe, fh))
    factors = [{"coefficients": [int(c) for c in f.all_coeffs()], "multiplicity": int(m)}
               for f, m in sp.factor_list(h)[1]]
    return {"F_E": fe, "F_H": fh, "F_H_irreducible_factors": factors,
            "gcd_over_Q": [int(c) for c in sp.gcd(e, h).monic().all_coeffs()],
            "gcd_over_Q_degree": int(sp.gcd(e, h).degree()),
            "F_D_candidate": [int(c) for c in (e*h).all_coeffs()],
            "reciprocal_valid": reciprocal(fe, p) and reciprocal(fh, p),
            "classification": ("malformed" if not (reciprocal(fe, p) and reciprocal(fh, p))
                               else "shared" if sp.gcd(e, h).degree() else "coprime")}


def screen(p, counts):
    c1, c2 = counts
    te, th = p+1-c1["N_E"], p+1-c1["N_H"]
    s2 = p*p+1-c2["N_H"]
    if (th*th-s2) % 2:
        raise ValueError("nonintegral genus-two coefficient")
    result = polynomial_screen(p, [1, -te, p], [1, -th, (th*th-s2)//2, -p*th, p*p])
    result.update(t_E=te, s_E2=p*p+1-c2["N_E"], t_H=th, s_H2=s2,
                  E_order=c1["N_E"], H_order=int(sp.Poly.from_list(result["F_H"], T).eval(1)),
                  source_type="supersingular_control" if te % p == 0 else "ordinary_toy",
                  full_genus3_frobenius_independent_check=False)
    return result


def synthetic_inputs(p):
    # Explicit formulas, independent of counted geometry. Both valid quartics are p-reciprocal.
    e = [1, -1, p]
    shared = [1, -2, 2*p+1, -2*p, p*p]  # (T^2-T+p)^2
    coprime = [1, 0, 2*p, 0, p*p]       # (T^2+p)^2
    malformed = [1, -2, 2*p+1, 2*p, p*p]  # deliberately reversed reciprocal sign
    return [{"id": label, "p": p, "F_E": e, "F_H": h, "expected": expected}
            for label, h, expected in (("shared", shared, "shared"),
                                       ("coprime", coprime, "coprime"),
                                       ("sign_malformed_reciprocal", malformed, "malformed"))]


def row(p, a, b, panel):
    forward = [count(p, a, b, degree) for degree in (1, 2)]
    reverse = [count(p, a, b, degree, True) for degree in (1, 2)]
    sf, sr = screen(p, forward), screen(p, reverse)
    return {"p": p, "a": a, "b": b, "panel": panel,
            "sample_role": "calibration" if (p, a, b) == (43, 0, 1) else "holdout",
            "curve_uid": f"prym-toy:p={p}:E=y2-x3-7:D:z2-(x-{a})(x-{b})",
            "subgroup_uid": None, "factor_base_uid": None,
            "counts": forward, "reverse_counts": reverse, "screen": sf,
            "reverse_screen": sr, "aa_exact": forward == reverse and sf == sr}


def native_context(directory):
    launch = json.loads((directory/"launch.json").read_text())
    plan_path = ROOT/f"experiments/{EXP}/trial-plan.json"
    plan = json.loads(plan_path.read_text())
    spec = yaml.safe_load((ROOT/plan["specification"]).read_text())["experiment"]
    if (launch.get("plan_sha256") != digest(plan_path) or plan.get("experiment_id") != EXP
            or spec.get("status") not in ("approved", "running") or spec.get("frozen") is not True
            or spec.get("execution_authorized") is not True or spec.get("approved_by") != plan.get("approved_by")
            or digest(ROOT/plan["specification"]) != plan.get("specification_sha256")):
        raise ValueError("native supervisor / approved protocol binding mismatch")
    authority = launch.get("authority", {})
    if not authority.get("owner") or not authority.get("epoch") or not authority.get("commit"):
        raise ValueError("native live-claim authority missing")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True)
    if commit != authority["commit"] or dirty:
        raise ValueError("source revision mismatch or tracked dirty tree")
    for kind in ("source_sha256", "input_sha256"):
        for path, expected in plan[kind].items():
            if digest(ROOT/path) != expected:
                raise ValueError(f"changed {kind}: {path}")
    trial = next(t for t in plan["trials"] if t["id"] == launch["trial_id"])
    if directory.resolve() != (ROOT/f"experiments/{EXP}/runs/{trial['run_id']}").resolve():
        raise ValueError("native run-directory mismatch")
    return launch, plan, commit, dirty


def run(args):
    directory = args.run_dir.resolve()
    launch, plan, commit, dirty = native_context(directory)
    cfg = config(args.config)
    started = datetime.now(timezone.utc).isoformat()
    wall, cpu = time.perf_counter(), time.process_time()
    result = {"schema": "prym-geometry-result/v2", "experiment_id": EXP,
              "config_sha256": digest(args.config), "measurement_scope": "point_counts_Fp_Fp2_only",
              "primary_rows": [], "companion_rows": [], "synthetic_controls": [],
              "candidate_pairs": [], "errors": [], "complete": False,
              "jacobian_maps_checked": False, "full_genus3_frobenius_independent_check": False,
              "limits": LIMITS, "execution_authority_granted": False}
    status, error = "completed", None
    memory = GroupMemory()
    with memory, (directory/"events.jsonl").open("x") as events:
        def event(value):
            events.write(json.dumps(value, sort_keys=True)+"\n")
            events.flush()
        try:
            for p in cfg["primes"]:
                pairs, inspected = catalogue(p)
                result["candidate_pairs"].extend(inspected)
                for candidate in inspected:
                    event(candidate)
                for index, (a, b) in enumerate(pairs):
                    panel = "primary" if index < 8 else "companion"
                    cell = row(p, a, b, panel)
                    result[f"{panel}_rows"].append(cell)
                    event({"event": "cell_complete", "p": p, "a": a, "b": b,
                           "panel": panel, "aa_exact": cell["aa_exact"]})
                    identities = all(c["N_D"] == c["N_E"]+c["N_H"]-c["q"]-1 for c in cell["counts"])
                    if not identities or not cell["aa_exact"] or cell["screen"]["s_E2"] != cell["screen"]["t_E"]**2-2*p:
                        raise ValueError(f"arithmetic/control mismatch: {(p,a,b,panel)}")
                for supplied in synthetic_inputs(p):
                    observed = polynomial_screen(p, supplied["F_E"], supplied["F_H"])
                    result["synthetic_controls"].append({**supplied, "observed": observed})
                    event({"event": "synthetic_control", "p": p, "id": supplied["id"],
                           "classification": observed["classification"]})
                    if observed["classification"] != supplied["expected"]:
                        raise ValueError("synthetic instrument mismatch")
            result["complete"] = True
        except Exception as exc:
            status, error = "invalid", f"{type(exc).__name__}: {exc}"
            result["errors"].append(error)
            event({"event": "implementation_error", "detail": error})
        memory.sample()
        if memory.errors:
            status, error = "invalid", "process-group memory monitor loss"
            result["complete"] = False
            result["errors"].extend(memory.errors)
        result.update(wall_seconds=time.perf_counter()-wall, cpu_seconds=time.process_time()-cpu,
                      sampled_process_group_peak_rss_bytes=memory.peak,
                      process_group_rss_sampling_interval_seconds=0.05,
                      peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform == "darwin" else 1024))
        event({"event": "producer_terminal", "status": status, "complete": result["complete"]})
    write_json(directory/"raw-result.json", result)
    sources = plan["source_sha256"]
    manifest = {"run": {"id": directory.name, "experiment_id": EXP, "status": status,
        "code": {"commit": commit, "dirty_tree": dirty, "command": launch["argv"], "source_sha256": sources},
        "environment": {"python": platform.python_version(), "sympy": sp.__version__, "pyyaml": yaml.__version__,
                        "platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor(),
                        "native_environment": "environment.json"},
        "inputs": {"parameters": cfg, "input_sha256": plan["input_sha256"],
                   "specification_sha256": plan["specification_sha256"], "seeds": [0]},
        "inference": {"policy": "executor-implementation", "backend": None, "resolved_model_id": None,
                      "model_verified": False, "provenance": "Python trial makes no model call; executor session identity is not supplied by supervisor",
                      "fallback_used": False, "degraded_requirements": [], "reasoning_effort": None},
        "timing": {"started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
                   "wall_seconds": result["wall_seconds"], "cpu_seconds": result["cpu_seconds"],
                   "producer_peak_rss_bytes": result["peak_rss_bytes"], "process_group_guard_bytes": 2*1024**3,
                   "process_group_peak_rss_bytes": result["sampled_process_group_peak_rss_bytes"],
                   "process_group_peak_note": "Linux /proc group sum sampled every 0.05s; subinterval peaks can be missed; native adapter enforces RLIMIT_AS"},
        "result": {"raw_result": "raw-result.json", "outcome": None, "outcome_note": error or "Observations only; independent recount is in verification.json.",
                   "certificate": {"kind": "none"}, "limitations": LIMITS}}}
    with (directory/"manifest.yaml").open("x") as stream:
        yaml.safe_dump(manifest, stream, sort_keys=False)
    print(json.dumps({"primary_rows": len(result["primary_rows"]), "companion_rows": len(result["companion_rows"]),
                      "status": status, "raw_result": str(directory/"raw-result.json")}))
    return 0 if result["complete"] else 2


def self_test():
    # Small software fixtures only, outside the frozen prime panel.
    n = [count(5, 0, 1, d) for d in (1, 2)]
    assert n == [count(5, 0, 1, d, True) for d in (1, 2)]
    for d in (1, 2):
        c = count(5, 0, 1, d)
        assert c["N_D"] == c["N_E"]+c["N_H"]-c["q"]-1
    controls = synthetic_inputs(5)
    assert [polynomial_screen(5, c["F_E"], c["F_H"])["classification"] for c in controls] == ["shared", "coprime", "malformed"]
    pairs, events = catalogue(29)
    assert len(pairs) == 16 and len(set(pairs)) == 16
    assert all(e["accepted"] == bool(((e["a"]**3+7)*(e["b"]**3+7)) % 29) for e in events)
    return {"software_checks": "passed", "scientific_panel_executed": False,
            "fixtures": "Fp/Fp2 at p=5; synthetic p=5; lexicographic selection p=29"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT/CONFIG)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return 0
    if args.run_dir is None:
        parser.error("--run-dir is required for a native supervised trial")
    try:
        return run(args)
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        print(f"G producer impediment: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
