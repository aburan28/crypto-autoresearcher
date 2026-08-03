#!/usr/bin/env python3
"""Independent certificate verifier for EXP-DS-001 run artifacts.

Re-checks discrete-log and decomposition certificates without importing the
solver paths used to produce them (uses harness.toycurve arithmetic only).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from harness.toycurve import EllipticCurve, Point, generate_instance  # noqa: E402


def verify_discrete_log(curve: dict, P: list, Q: list, k: int) -> bool:
    E = EllipticCurve(curve["p"], curve["a"], curve["b"])
    Pt: Point = (int(P[0]), int(P[1]))
    Qt: Point = (int(Q[0]), int(Q[1]))
    if not E.is_on_curve(Pt) or not E.is_on_curve(Qt):
        return False
    return E.mul(int(k), Pt) == Qt


def verify_decomposition(cert: dict) -> bool:
    if cert.get("kind") != "decomposition":
        return False
    # Support both nested statement and flat driver form
    st = cert.get("statement") or cert
    curve = st.get("curve")
    target = st.get("target")
    summands = st.get("summands")
    if curve is None:
        # Driver-flat form without curve: cannot fully verify — return False
        # unless caller supplies instance context.
        return False
    E = EllipticCurve(curve["p"], curve["a"], curve["b"])
    acc: Point = None
    for s in summands:
        pt = (int(s[0]), int(s[1]))
        if not E.is_on_curve(pt):
            return False
        acc = E.add(acc, pt)
    return acc == (int(target[0]), int(target[1]))


def verify_decomposition_with_instance(cert: dict, seed: int, bits: int) -> bool:
    inst = generate_instance(seed, bits)
    E = inst.curve()
    st = cert.get("statement") or cert
    target = st.get("target")
    summands = st.get("summands")
    if not target or not summands:
        return False
    acc: Point = None
    for s in summands:
        pt = (int(s[0]), int(s[1]))
        if not E.is_on_curve(pt):
            return False
        acc = E.add(acc, pt)
    return acc == (int(target[0]), int(target[1]))


def verify_run_dir(run_dir: Path) -> dict:
    raw_path = run_dir / "raw-result.json"
    man_path = run_dir / "manifest.json"
    out = {"run_dir": str(run_dir), "ok": True, "checks": []}
    if not raw_path.exists():
        return {"run_dir": str(run_dir), "ok": False, "error": "missing raw-result.json"}
    raw = json.loads(raw_path.read_text())
    cert = None
    if man_path.exists():
        man = json.loads(man_path.read_text())
        cert = (man.get("result") or {}).get("certificate")
    cert = cert or raw.get("certificate") or {"kind": "none"}
    kind = cert.get("kind", "none")
    if kind == "none":
        out["checks"].append({"kind": "none", "verified": True})
        return out
    if kind == "discrete_log":
        # Recover instance from whatever cell layout this mode wrote.
        cell = raw.get("cell") or {}
        if not cell and raw.get("reported_cell"):
            cell = dict(raw["reported_cell"])
        if not cell and raw.get("selected_cell"):
            cell = dict(raw["selected_cell"])
        if not cell:
            records = raw.get("cell_records") or raw.get("cell_or_ladder_search_record") or []
            if records:
                first = records[0]
                cell = dict(first.get("cell_record") or first)
        seed = cell.get("seed", 101)
        bits = cell.get("bits", 16)
        inst = generate_instance(seed, bits)
        k = cert.get("k")
        if k is None and cell.get("rho"):
            k = cell["rho"].get("k")
        if k is None and isinstance(raw.get("selected_cell"), dict):
            rho = (raw["selected_cell"] or {}).get("rho") or {}
            k = rho.get("k")
        ok = False
        if k is not None:
            ok = inst.curve().mul(int(k), inst.P) == inst.Q
        out["checks"].append({
            "kind": "discrete_log",
            "verified": ok,
            "k": k,
            "bits": bits,
            "seed": seed,
        })
        out["ok"] = bool(ok)
        return out
    if kind == "decomposition":
        ok = verify_decomposition(cert)
        out["checks"].append({"kind": "decomposition", "verified": ok})
        out["ok"] = bool(ok)
        return out
    out["ok"] = False
    out["checks"].append({"kind": kind, "verified": False, "error": "unknown kind"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    result = verify_run_dir(Path(args.run_dir))
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
