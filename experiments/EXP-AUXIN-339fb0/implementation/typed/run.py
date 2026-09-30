#!/usr/bin/env python3
"""EXP-AUXIN-339fb0 typed implementation entry point.

Launch (later, after scientific_execution_authorized + admission):
  python3 -I experiments/EXP-AUXIN-339fb0/implementation/typed/run.py ...

Under python3 -I the directory of run.py is NOT on sys.path. This file therefore
inserts the absolute path of experiments/EXP-AUXIN-339fb0/implementation/typed/
at sys.path[0] BEFORE importing any typed module, importing only sys and os
before doing so (corrective.custody.run_entry_sys_path / RI-7).

This packaging task (TASK-20260930-e9f8bf) must NOT execute the census protocol.
Default mode is --packaging-check: validate imports/AST and successor hash, exit 0.
"""

import os
import sys

# ONLY sys and os may be imported before this path insertion (F-J1-7 / RI-7).
_TYPED_DIR = os.path.dirname(os.path.abspath(__file__))
if sys.path[:1] != [_TYPED_DIR]:
    sys.path.insert(0, _TYPED_DIR)

# --- imports below this line may include typed/ locals and allowed deps --------

import argparse
import hashlib
import json
from decimal import getcontext
from pathlib import Path
from typing import Any, Dict, List, Optional

import import_audit

CONTRACT_REL = "experiments/EXP-AUXIN-339fb0/specification.yaml"
EXPECTED_CONTRACT_SHA256 = (
    "6a1dca32c109d5badf4ba143c31f9d4d9a49e18ae287c8bb4fc604526bf02ecc"
)
EXPERIMENT_ID = "EXP-AUXIN-339fb0"
PACKAGING_TASK = "TASK-20260930-e9f8bf"


def _repo_root() -> Path:
    # typed/ -> implementation/ -> EXP-AUXIN-339fb0/ -> experiments/ -> repo
    return Path(_TYPED_DIR).resolve().parents[3]


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_trial_plan() -> Dict[str, Any]:
    path = Path(_TYPED_DIR) / "trial-plan.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def packaging_check() -> Dict[str, Any]:
    """Validate package integrity without scoring any census row."""
    root = _repo_root()
    contract = root / CONTRACT_REL
    report: Dict[str, Any] = {
        "mode": "packaging-check",
        "experiment_id": EXPERIMENT_ID,
        "packaging_task": PACKAGING_TASK,
        "typed_dir": _TYPED_DIR,
        "sys_path_0": sys.path[0],
        "scientific_execution_authorized": False,
        "runs_launched": 0,
        "ok": True,
        "problems": [],
    }

    if sys.path[0] != _TYPED_DIR:
        report["ok"] = False
        report["problems"].append(
            f"sys.path[0]={sys.path[0]!r} != typed dir {_TYPED_DIR!r}"
        )

    if not contract.is_file():
        report["ok"] = False
        report["problems"].append(f"missing contract file {contract}")
        return report

    contract_sha = _sha256_file(contract)
    report["contract_sha256"] = contract_sha
    if contract_sha != EXPECTED_CONTRACT_SHA256:
        report["ok"] = False
        report["problems"].append(
            f"contract sha256 {contract_sha} != expected {EXPECTED_CONTRACT_SHA256}"
        )

    trial = _load_trial_plan()
    tp_hash = trial.get("successor_contract_sha256")
    report["trial_plan_successor_contract_sha256"] = tp_hash
    if tp_hash != EXPECTED_CONTRACT_SHA256:
        report["ok"] = False
        report["problems"].append(
            f"trial-plan successor_contract_sha256 {tp_hash!r} mismatch"
        )
    if tp_hash != contract_sha:
        report["ok"] = False
        report["problems"].append(
            "trial-plan hash does not match live contract file bytes"
        )

    audit = import_audit.audit_tree(Path(_TYPED_DIR))
    report["import_audit"] = {
        "ok": audit["ok"],
        "files": [
            {
                "file": f["file"],
                "path": f["path"],
                "ok": f["ok"],
                "stdlib_only_required": f["stdlib_only_required"],
                "problems": f["problems"],
                "import_count": len(f["imports"]),
            }
            for f in audit["files"]
        ],
    }
    if not audit["ok"]:
        report["ok"] = False
        report["problems"].append("AST import audit failed")

    # Import typed surfaces (stdlib / local only path) without launching stages.
    import cert_verify  # noqa: WPS433
    import e_eval  # noqa: WPS433
    import factor_path_b  # noqa: WPS433
    import factor_path_a  # noqa: WPS433

    # Smoke: Pratt leaf 2 and a tiny prime.
    leaf = cert_verify.make_pratt_leaf_two()
    ok2, _ = cert_verify.verify_pratt(leaf)
    if not ok2:
        report["ok"] = False
        report["problems"].append("cert_verify leaf-2 self-check failed")
    p3 = cert_verify.build_pratt_for_small_prime(3)
    if p3 is None:
        report["ok"] = False
        report["problems"].append("could not build Pratt for 3")
    else:
        ok3, _ = cert_verify.verify_pratt(p3)
        if not ok3:
            report["ok"] = False
            report["problems"].append("cert_verify Pratt-3 self-check failed")

    # Even compositeness witness.
    ok_even, _ = cert_verify.verify_compositeness_witness(15, 2)  # 15 fails at a=2? 
    # 15 fails strong PRP at a=2: pow checks — actually strong_prp(15,2) is False.
    # Smallest a>=2 failing: a=2 works. Good.
    if not ok_even:
        # 15 is odd; witness should be smallest failing base.
        # Re-check with correct expectation.
        pass
    ok15, det15 = cert_verify.verify_compositeness_witness(15, 2)
    report["cert_smoke"] = {
        "pratt_2": ok2,
        "pratt_3": bool(p3) and ok3,
        "compositeness_15_a2": ok15,
        "compositeness_detail": det15,
        "factor_path_a_surface": factor_path_a.packaging_surface(),
        "factor_path_b_surface": factor_path_b.packaging_surface(),
        "e_eval_prec": int(getcontext().prec),
    }
    if not ok15:
        report["ok"] = False
        report["problems"].append("compositeness witness smoke failed for 15")

    report["modules_present"] = sorted(
        p.name for p in Path(_TYPED_DIR).iterdir() if p.is_file()
    )
    return report


def refuse_scientific_run(argv: List[str]) -> int:
    msg = (
        "REFUSED: scientific protocol launch is not authorized in this package "
        "state (scientific_execution_authorized not set; TASK-20260930-e9f8bf "
        "is packaging-only, maximum_runs=0). Use --packaging-check.\n"
        f"argv={argv!r}\n"
    )
    sys.stderr.write(msg)
    return 2


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="EXP-AUXIN-339fb0 typed entry (packaging-check default)",
    )
    parser.add_argument(
        "--packaging-check",
        action="store_true",
        default=False,
        help="Validate AST imports and successor_contract_sha256; exit 0 (default if no --run)",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Attempt scientific protocol (refused unless separately authorized)",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="",
        help="Optional path to write packaging-check JSON report",
    )
    # Default: packaging-check when neither flag given.
    if not argv:
        argv = ["--packaging-check"]
    args, unknown = parser.parse_known_args(argv)
    if not args.run and not args.packaging_check:
        args.packaging_check = True

    if args.run:
        return refuse_scientific_run(argv)

    report = packaging_check()
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    sys.stdout.write(text + "\n")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
