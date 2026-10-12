"""One fixture in a fresh process: generator to A2 (A1 is its prefix), then per
budget: LP graph metrics, Horton basis (16/20-bit), nulls, planted-dense
known positive, sparse LP log recovery, scrambled known false, accounting
audit; plus the rho baseline. Writes <out>.json and <out>.attempts.jsonl.

  python3 celltask.py --bits 16 --seed 11 --ns <ns> --a1 N --a2 N \
      --replicates 32 --rho-targets 64 --out PATH

A namespace without 'smoke' (the frozen draws) is refused unless the process
was launched by driver.py for an admitted run (AMD-20260929-cc7226 FX-5, R-5):
the driver passes the decision id, repository root, run directory and a
per-run random token in the environment; this process re-checks the decision,
that the run manifest is running for that decision and namespace, that the
token hashes to the manifest's run_token_sha256, and that the manifest's
driver_pid is its live parent running driver.py.

Known positive (AMD-20260929-cc7226 F-4): below the smallest |V| at which a
planted graph of cycle rank ceil(|V|^1.5) can give delta_proof > 1/4 for the
fixture's L, the control is recorded not_exercised (neither pass nor defect).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import resource
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import audit as audit_mod  # noqa: E402
import fixtures  # noqa: E402
import labels  # noqa: E402
import lpgraph  # noqa: E402
import nulls  # noqa: E402
import recovery  # noqa: E402
import rho  # noqa: E402
from relgen import Generator, relations_of  # noqa: E402

HORTON_BITS = (16, 20)
OUTCOMES = ("miss", "full", "lp1", "lp2", "single_point_fb", "single_point_lp", "R_is_O")


def peak_rss_bytes() -> int:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r if sys.platform == "darwin" else r * 1024


def _summ(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0, "mean": None, "sd": None, "min": None, "max": None}
    return {"n": len(vals), "mean": statistics.fmean(vals),
            "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
            "min": min(vals), "max": max(vals)}


def _null_row(m):
    return {k: m[k] for k in ("V", "E", "components", "cycle_rank", "giant_component_fraction",
                              "components_with_cycle", "delta_proof", "delta_ratio",
                              "cycle_rank_identity_ok")}


def planted_gate_min_v(L: int):
    """Smallest |V| >= 2 whose planted cycle rank ceil(|V|^1.5) gives
    delta_proof > 1/4 at log base L; None if no |V| can (L < 2)."""
    if L < 2:
        return None
    n = 2
    while True:
        cr = math.ceil(n ** 1.5)
        if lpgraph.deltas(cr, cr + n - 1, L)["delta_proof"] > 0.25:
            return n
        n += 1


def known_positive(n, L, ns, ctx, name, defects) -> dict:
    vmin = planted_gate_min_v(L)
    base = {"gate": "delta_proof > 1/4", "V": n, "L": L, "gate_min_V": vmin,
            "exercised": False, "power_confirmed": False}
    gp = nulls.planted_dense(n, ns, ctx)
    if gp is None:
        return {**base, "status": "not_exercised", "reason": "|V| < 2"}
    mp = lpgraph.metrics(gp, L)
    if mp["cycle_rank"] != gp["planted_cycle_rank"]:
        defects.append(f"{name}: planted cycle rank {mp['cycle_rank']} != {gp['planted_cycle_rank']}")
    row = {**base, "planted_cycle_rank": gp["planted_cycle_rank"], "metrics": _null_row(mp)}
    if vmin is None or n < vmin:
        return {**row, "status": "not_exercised",
                "reason": f"AMD-20260929-cc7226 F-4: |V| = {n} is below the gate-reachable minimum "
                          f"{vmin} for L = {L}; neither a pass nor a procedure defect"}
    passed = mp["delta_proof"] is not None and mp["delta_proof"] > 0.25
    if not passed:
        defects.append(f"{name}: planted-dense known positive did not report delta_proof > 1/4")
    return {**row, "status": "pass" if passed else "FAIL", "exercised": True, "power_confirmed": passed}


def parent_is_driver(pid) -> tuple[bool, str]:
    """The manifest's driver pid must be this process's parent, alive, and
    running driver.py."""
    if not isinstance(pid, int) or pid != os.getppid():
        return False, f"manifest driver_pid {pid!r} is not this process's parent {os.getppid()}"
    try:
        import psutil
        cmd = psutil.Process(pid).cmdline()
    except Exception as e:  # fail closed
        return False, f"cannot inspect parent {pid}: {e}"
    if not any(Path(c).name == "driver.py" for c in cmd):
        return False, f"parent {pid} is not driver.py: {cmd[:3]}"
    return True, "parent is the live driver"


def watch_parent(expected_ppid: int, interval=1.0, exit_fn=None, getppid=os.getppid):
    """Exit (code 9) as soon as the launching driver is gone (re-parenting),
    e.g. after an uncatchable SIGKILL of the driver."""
    import threading
    exit_fn = exit_fn or (lambda: os._exit(9))

    def loop():
        while True:
            if getppid() != expected_ppid:
                exit_fn()
                return
            time.sleep(interval)
    t = threading.Thread(target=loop, daemon=True, name="parent-watch")
    t.start()
    return t


def admission_guard(ns: str) -> tuple[bool, str]:
    if labels.is_smoke_ns(ns):
        return True, "smoke namespace"
    import driver
    import yaml
    dec = os.environ.get(driver.ADMISSION_ENV)
    repo = os.environ.get(driver.REPO_ENV)
    run_dir = os.environ.get(driver.RUN_DIR_ENV)
    token = os.environ.get(driver.RUN_TOKEN_ENV)
    if not (dec and repo and run_dir and token):
        return False, "not launched by the admitted driver (admission environment absent)"
    ok, why = driver.check_decision(Path(repo), dec)
    if not ok:
        return False, f"admission decision refused: {why}"
    mp = Path(run_dir) / "manifest.yaml"
    try:
        run = yaml.safe_load(mp.read_text())["run"]
    except (OSError, yaml.YAMLError, KeyError, TypeError) as e:
        return False, f"run manifest {mp} unreadable: {e}"
    inp = run.get("inputs") or {}
    if run.get("status") != "running" or inp.get("admission_decision") != dec or inp.get("namespace") != ns:
        return False, f"run manifest {mp} is not a running admitted run for {dec} in namespace {ns}"
    if inp.get("run_token_sha256") != driver.token_sha256(token):
        return False, f"run token does not match run manifest {mp}"
    ok, why = parent_is_driver(inp.get("driver_pid"))
    if not ok:
        return False, why
    return True, f"admitted by {dec} for {run.get('id')} (driver pid {inp.get('driver_pid')})"


def budget_block(gen, records, A, name, ns, replicates, horton_on, defects):
    fx = gen.fx
    pre = records[:A]
    counts = {o: 0 for o in OUTCOMES}
    for r in pre:
        counts[r["outcome"]] += 1
    rels = relations_of(pre)
    attempts_ops = sum(r["group_ops"] for r in pre)
    total_ops = gen.setup_ops["group_ops"] + attempts_ops
    g = lpgraph.build(rels, gen.B)
    met = lpgraph.metrics(g, gen.L)
    if not met["cycle_rank_identity_ok"]:
        defects.append(f"{name}: cycle rank |E|-|V|+c != GF(2) cycle-space dimension")
    out = {"budget": name, "attempts": A, "outcome_counts": counts,
           "full_relation_count": counts["full"],
           "failed_attempt_count": counts["miss"] + counts["single_point_fb"]
           + counts["single_point_lp"] + counts["R_is_O"],
           "extra_decompositions": sum(max(0, r["n_decomp"] - 1) for r in pre),
           "charged": {"setup_group_ops": gen.setup_ops["group_ops"],
                       "attempt_group_ops": attempts_ops, "total_group_ops": total_ops,
                       "setup_W_field": gen.setup_ops["W_field"],
                       "attempt_W_field": sum(r["W_field"] for r in pre),
                       "charged_work_over_sqrt_q": total_ops / math.sqrt(gen.q)},
           "graph": met, "lp_x": g["lp_x"]}
    t0 = time.time()
    if horton_on:
        hb = lpgraph.horton_mcb(g)
        if not (hb["size_identity_ok"] and hb["all_even_degree"]):
            defects.append(f"{name}: Horton basis size/cycle identity failed")
        basis = hb.pop("basis")
        hb["basis_edge_ids"] = [[i for i in range(len(g["edges"])) if c >> i & 1] for c in basis]
        out["horton"] = hb
    else:
        out["horton"] = {"computed": False,
                         "reason": "C-4: minimum basis at 16- and 20-bit only; GF(2) cycle rank reported"}
    out["horton_seconds"] = time.time() - t0
    ctx = nulls.ctx(gen.bits, gen.seed, name)
    deg = nulls.degree_sequence(g)
    rew, er = [], []
    for i in range(replicates):
        gr = nulls.rewire(g, ns, i, ctx)
        if nulls.degree_sequence(gr) != deg or len(gr["edges"]) != len(g["edges"]):
            defects.append(f"{name}: rewire {i} did not preserve degrees")
        rew.append(_null_row(lpgraph.metrics(gr, gen.L)))
        ge = nulls.erdos_renyi(g["n"], len(g["edges"]), ns, i, ctx)
        er.append(None if ge is None else _null_row(lpgraph.metrics(ge, gen.L)))
    er_ok = [r for r in er if r is not None]
    out["null_rewire"] = {"replicates": rew, "summary": {
        k: _summ([r[k] for r in rew]) for k in ("cycle_rank", "components", "giant_component_fraction",
                                               "delta_proof")},
        "frac_delta_proof_gt_quarter": (sum(1 for r in rew if (r["delta_proof"] or -9) > 0.25) / len(rew))
        if rew else None}
    out["null_er"] = {"replicates": er, "feasible": len(er_ok), "summary": {
        k: _summ([r[k] for r in er_ok]) for k in ("cycle_rank", "components", "giant_component_fraction",
                                                 "delta_proof")},
        "frac_delta_proof_gt_quarter": (sum(1 for r in er_ok if (r["delta_proof"] or -9) > 0.25) / len(er_ok))
        if er_ok else None}
    out["known_positive"] = known_positive(g["n"], gen.L, ns, ctx, name, defects)
    rec = recovery.recover_and_verify(rels, gen.fb_x, gen.B, fx, gen.Q)
    out["recovery"] = rec
    if rec["verification_failures"] or rec["inconsistent_rows"]:
        defects.append(f"{name}: treatment LP log recovery failed verification")
    srels = recovery.scramble(rels, ns, ctx)
    srec = recovery.recover_and_verify(srels, gen.fb_x, gen.B, fx, gen.Q)
    kf = recovery.known_false_outcome(srec)
    out["known_false"] = {"status": kf, "recovery": srec}
    if kf == "passes_verification":
        defects.append(f"{name}: scrambled-coefficient known false passed verification")
    hdr = gen.header()
    au = audit_mod.audit(hdr, pre, A, total_ops, ns)
    out["accounting_audit"] = au
    if not au["accepted"]:
        defects.append(f"{name}: accounting audit rejected: {au['reasons']}")
    return out


def run(bits, seed, ns, a1, a2, replicates, rho_targets, out_path: Path, horton_24=False):
    ok, why = admission_guard(ns)
    if not ok:
        raise PermissionError(f"REFUSED: namespace {ns!r}: {why}")
    t0 = time.time()
    fx = fixtures.fixture(bits, seed)
    prm = fixtures.params(fx)
    gen = Generator(fx, prm, ns)
    records = []
    out_path.parent.mkdir(parents=True, exist_ok=True)
    att_path = out_path.with_suffix(".attempts.jsonl")
    with open(att_path, "x") as fh:
        for j in range(a2):
            r = gen.attempt(j)
            records.append(r)
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    t_gen = time.time() - t0
    defects = []
    horton_on = bits in HORTON_BITS or horton_24
    blocks = [budget_block(gen, records, A, name, ns, replicates, horton_on, defects)
              for name, A in (("A1", a1), ("A2", a2))]
    rres = [rho.solve(fx, t, ns) for t in range(rho_targets)]
    if any(not r.get("solved") for r in rres):
        defects.append("rho: unsolved or unverified target")
    result = {"fixture_id": fixtures.fixture_id(fx), "fixture": fx, "params": prm,
              "ns": ns, "header": gen.header(), "budgets": blocks,
              "rho": {"targets": rres, "summary": rho.summary(rres, fx["N"])},
              "blind_descent_success": None,
              "blind_descent_note": "no descent step is defined in protocol v4 (see open questions)",
              "procedure_defects": defects,
              "timing_seconds": {"generator": t_gen, "total": time.time() - t0},
              "peak_rss_bytes": peak_rss_bytes(),
              "attempts_file": att_path.name}
    with open(out_path, "x") as fh:
        json.dump(result, fh, indent=1, sort_keys=True)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bits", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--ns", required=True)
    ap.add_argument("--a1", type=int, required=True)
    ap.add_argument("--a2", type=int, required=True)
    ap.add_argument("--replicates", type=int, default=32)
    ap.add_argument("--rho-targets", type=int, default=64)
    ap.add_argument("--horton-24", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    import driver
    dpid = os.environ.get(driver.DRIVER_PID_ENV)
    if dpid:
        if int(dpid) != os.getppid():
            print(f"REFUSED: launching driver {dpid} is not this process's parent", file=sys.stderr)
            return 9
        watch_parent(int(dpid))
    if a.a1 > a.a2:
        print("a1 must be <= a2 (A2 is a prefix-continuation of A1)", file=sys.stderr)
        return 2
    ok, why = admission_guard(a.ns)
    if not ok:
        print(f"REFUSED: namespace {a.ns!r}: {why}", file=sys.stderr)
        return 3
    res = run(a.bits, a.seed, a.ns, a.a1, a.a2, a.replicates, a.rho_targets, Path(a.out), a.horton_24)
    print(json.dumps({"fixture": res["fixture_id"], "defects": res["procedure_defects"],
                      "peak_rss_bytes": res["peak_rss_bytes"]}))
    return 7 if res["procedure_defects"] else 0


if __name__ == "__main__":
    sys.exit(main())
