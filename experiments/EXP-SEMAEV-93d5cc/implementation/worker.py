"""One arm of one EXP-SEMAEV-93d5cc cell.

    python3 worker.py --arm legacy|repaired --cell <cell> --out <dir> [--dep <cell>=<run_dir> ...]

Runs the archived program of the cell, unmodified, with the arm's ``s4_expr``
installed (``arms.install``), writing everything under ``--out``.  Archived
inputs are read in place and never written; archived outputs that a cell
consumes are copied into ``--out/inputs`` with their sha256 recorded.  The
worker computes no comparison; ``launch.py`` and ``check.py`` do.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))

import arms  # noqa: E402

ICINV_RUN = REPO / "experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class"
FIB_EXP = REPO / "experiments/EXP-FIB-001"
MTIC_EXP = REPO / "experiments/EXP-MTIC-001"
ICINV_P = 4001
ICINV_M4_TIMEOUT = 180.0  # archived curve_full_invariants default m4_timeout
SINGULAR_CANDIDATES = ("/opt/conda-sage/envs/sage/bin/Singular",)
CELLS = ("icinv-m4", "fib-004", "fib-005", "fib-decision",
         "mtic-007", "mtic-008", "mtic-010b")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=1, sort_keys=True, default=str)
        stream.write("\n")


def copy_input(src: Path, dst: Path, ledger: dict) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    ledger[str(dst)] = {"source": str(src.relative_to(REPO)) if src.is_relative_to(REPO) else str(src),
                        "sha256": sha256(dst)}


# ----------------------------------------------------------------- ICINV m4
def cell_icinv(arm: str, out: Path) -> dict:
    import harness.exp_icinv_e0cd8f_m3class as M
    prov = arms.install(M, arm)
    for cand in SINGULAR_CANDIDATES:
        if Path(cand).exists():
            M.SINGULAR_BIN = cand
            break
    records = []
    t0 = time.time()
    for set_name, fname in (("control", "control-set-invariants.json"),
                            ("class", "per-curve-invariants.json")):
        doc = json.loads((ICINV_RUN / fname).read_text())
        if doc.get("p", ICINV_P) != ICINV_P:
            raise RuntimeError(f"{fname}: unexpected p")
        for i, c in enumerate(doc["curves"]):
            a, b = c["a"], c["b"]
            g = c["gauge"]
            a2, b2 = M.gauge_transform(a, b, g["u"], ICINV_P)
            if (a2, b2) != (g["a2"], g["b2"]):
                raise RuntimeError(f"gauge mismatch at {set_name}[{i}]")
            for role, (ca, cb) in (("base", (a, b)), ("gauge", (a2, b2))):
                try:
                    r = M.compute_curve_m4(ca, cb, ICINV_P, timeout=ICINV_M4_TIMEOUT)
                except subprocess.TimeoutExpired:
                    r = {"backend": "singular", "returncode": None, "timeout": True,
                         "wall_seconds": ICINV_M4_TIMEOUT}
                records.append({"set": set_name, "index": i, "role": role,
                                "a": ca, "b": cb, "m4": r})
            print(f"[{arm}] {set_name}[{i}] ({a},{b}) base={records[-2]['m4'].get('s4_support')} "
                  f"gauge={records[-1]['m4'].get('s4_support')} t={time.time()-t0:.1f}s", flush=True)
    probe = subprocess.run([M.SINGULAR_BIN, "--version"], stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=30)
    ver = ((probe.stdout or probe.stderr).strip().splitlines() or [None])[0]
    write_json(out / "m4-records.json", {"p": ICINV_P, "records": records})
    return {"provenance": prov, "singular_bin": M.SINGULAR_BIN, "singular_version": ver,
            "n_records": len(records), "wall_seconds": time.time() - t0,
            "outputs": ["m4-records.json"]}


# --------------------------------------------------------------------- FIB
def _fib_modules(out: Path):
    sys.path.insert(0, str(FIB_EXP))
    from driver import decompcost, orchestrate, runlib
    import fib_child
    runlib.RUNS_DIR = str(out / "runs")
    os.makedirs(runlib.RUNS_DIR, exist_ok=True)
    decompcost._worker = fib_child.solve  # child installs the arm itself
    return decompcost, orchestrate


def cell_fib_measure(arm: str, out: Path, run_id: str) -> dict:
    decompcost, orch = _fib_modules(out)
    os.environ["EXP_S4RR_ARM"] = arm
    prov = arms.s4_function(arm)[1]
    prov["installed_into"] = "driver.decompcost (spawn child, fib_child.solve)"
    if run_id == "RUN-FIB-004":
        curves, fn, label = ["C16-1", "C16-2"], orch.run_fib_004, "16-bit"
    else:
        curves, fn, label = ["C20-1", "C20-2"], orch.run_fib_005, "20-bit"
    r = orch._run(run_id,
                  f"python3 -m driver.orchestrate  # {run_id}: {label} decomposition cost "
                  f"(EXP-SEMAEV-93d5cc arm={arm})",
                  {"targets_per_curve": orch.TARGETS_PER_MAIN_CURVE, "curves": curves,
                   "per_solve_cap_s": orch.PER_SOLVE_CAP,
                   "per_curve_cumulative_cap_s": orch.PER_CURVE_DECOMP_WALL_CAP,
                   "s4_arm": arm},
                  {"instance_seeds": [1, 2]}, fn)
    return {"provenance": prov, "status": r["status"], "wall_seconds": r["wall_seconds"],
            "outputs": [f"runs/{run_id}"]}


def cell_fib_decision(arm: str, out: Path, deps: dict) -> dict:
    """RUN-FIB-006C correlation decision, RUN-FIB-007 ratio and the RUN-FIB-008
    gate, recomputed with this arm's RUN-FIB-004/005 and the archived
    (S4-independent) RUN-FIB-002/003/007, exactly as driver/resume2.py does."""
    _, orch = _fib_modules(out)
    ledger: dict = {}

    def load(run_id: str, src_root: Path) -> dict:
        dst = out / "inputs" / run_id / "raw.json"
        copy_input(src_root / run_id / "raw.json", dst, ledger)
        return json.loads(dst.read_text())

    r2 = load("RUN-FIB-002", FIB_EXP / "runs")
    r3 = load("RUN-FIB-003", FIB_EXP / "runs")
    r7 = load("RUN-FIB-007", FIB_EXP / "runs")
    r4 = load("RUN-FIB-004", Path(deps["fib-004"]) / "arms" / arm / "runs")
    r5 = load("RUN-FIB-005", Path(deps["fib-005"]) / "arms" / arm / "runs")
    r6c = orch._run("RUN-FIB-006C",
                    f"python3 -m driver.resume2  # RUN-FIB-006C recomputed (EXP-SEMAEV-93d5cc arm={arm})",
                    {"permutation_replicates": orch.statslib.PERMUTATION_REPLICATES,
                     "correlation_prefix_min": orch.CORRELATION_PREFIX_MIN, "s4_arm": arm},
                    {"permutation_seed": orch.PERM_SEED},
                    lambda: orch.run_fib_006(r2, r3, r4, r5))
    ratios = orch.compute_predictor_cost_ratio(r7, r4, r5)
    cost_gate_curves = [cid for cid, ratio in ratios.items() if ratio is not None and ratio <= 0.1]
    corr_pass = r6c["summary"].get("correlation_gate_pass_overall")
    cost_pass = len(cost_gate_curves) >= 3
    decision = {"correlation_gate_pass_overall": corr_pass,
                "correlation_gate_curves_passing": r6c["summary"].get("correlation_gate_curves_passing"),
                "predictor_cost_ratios": ratios, "cost_gate_curves": cost_gate_curves,
                "predictor_cost_gate_pass": cost_pass,
                "gate_pass": bool(corr_pass and cost_pass),
                "run_fib_008_outcome": "would_run" if (corr_pass and cost_pass) else "cancelled_by_gate",
                "rule": "driver/resume2.py: cost gate = ratio <= 0.1 on >= 3 curves; gate = correlation AND cost"}
    write_json(out / "decision.json", decision)
    write_json(out / "inputs.json", ledger)
    return {"provenance": {"arm": arm, "s4_used": False,
                           "note": "S4 is not called here; the arm selects which RUN-FIB-004/005 feed the decision"},
            "status": r6c["status"], "outputs": ["runs/RUN-FIB-006C", "decision.json", "inputs.json"]}


# -------------------------------------------------------------------- MTIC
def cell_mtic(arm: str, out: Path, run_id: str, deps: dict) -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_mtic", MTIC_EXP / "code" / "run_mtic.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["run_mtic"] = m
    spec.loader.exec_module(m)
    prov = arms.install(m, arm)
    root = out / "out-root"
    ledger: dict = {}
    copy_input(MTIC_EXP / "frozen-instances.yaml", root / "frozen-instances.yaml", ledger)
    if run_id == "RUN-MTIC-010b":
        for rid in ("RUN-MTIC-002", "RUN-MTIC-003", "RUN-MTIC-004", "RUN-MTIC-005",
                    "RUN-MTIC-006", "RUN-MTIC-009"):
            for name in ("raw.json", "relations.json"):
                src = MTIC_EXP / "runs" / rid / name
                if src.exists():
                    copy_input(src, root / "runs" / rid / name, ledger)
        for cell, rid in (("mtic-007", "RUN-MTIC-007"), ("mtic-008", "RUN-MTIC-008")):
            src = Path(deps[cell]) / "arms" / arm / "out-root" / "runs" / rid / "raw.json"
            copy_input(src, root / "runs" / rid / "raw.json", ledger)
    write_json(out / "inputs.json", ledger)
    sys.argv = ["run_mtic.py", "--run-id", run_id, "--out-root", str(root)]
    t0 = time.time()
    rc = m.main()
    return {"provenance": prov, "returncode": rc, "wall_seconds": time.time() - t0,
            "outputs": [f"out-root/runs/{run_id}", "inputs.json"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=arms.ARMS)
    ap.add_argument("--cell", required=True, choices=CELLS)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--dep", action="append", default=[], help="cell=run_dir")
    args = ap.parse_args()
    deps = dict(d.split("=", 1) for d in args.dep)
    out = args.out
    out.mkdir(parents=True, exist_ok=False)
    fn, _ = arms.s4_function(args.arm)
    started = time.time()
    fingerprint = arms.self_test(fn)
    if args.cell == "icinv-m4":
        res = cell_icinv(args.arm, out)
    elif args.cell == "fib-004":
        res = cell_fib_measure(args.arm, out, "RUN-FIB-004")
    elif args.cell == "fib-005":
        res = cell_fib_measure(args.arm, out, "RUN-FIB-005")
    elif args.cell == "fib-decision":
        res = cell_fib_decision(args.arm, out, deps)
    else:
        rid = {"mtic-007": "RUN-MTIC-007", "mtic-008": "RUN-MTIC-008",
               "mtic-010b": "RUN-MTIC-010b"}[args.cell]
        res = cell_mtic(args.arm, out, rid, deps)
    res.update({"cell": args.cell, "arm": args.arm, "s4_fingerprint": fingerprint,
                "started_unix": started, "finished_unix": time.time()})
    write_json(out / "arm-result.json", res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
