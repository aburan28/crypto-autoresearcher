#!/usr/bin/env python3
"""EXP-BINSTD-178742 typed implementation entry point (packaging-only).

Launch:
  python3 -I experiments/EXP-BINSTD-178742/implementation/typed/run.py --packaging-check
  python3 -I experiments/EXP-BINSTD-178742/implementation/typed/run.py --run

Under python3 -I the directory of run.py is NOT on sys.path. This file therefore
inserts the absolute path of experiments/EXP-BINSTD-178742/implementation/typed/
at sys.path[0] BEFORE importing any typed module, importing only sys and os
before doing so (corrective.custody.run_entry_sys_path).

Authorization (TASK-20260930-d007a4 / DEC-20260930-70bff3):
  implementation_authorized true; scientific_execution_authorized false;
  packaging_only true; maximum_runs 0. --run REFUSES scientific launch while
  those flags block scoring. Opening/implementing is not a solve claim.
"""

import os
import sys

# ONLY sys and os may be imported before this path insertion.
_TYPED_DIR = os.path.dirname(os.path.abspath(__file__))
if sys.path[:1] != [_TYPED_DIR]:
    sys.path.insert(0, _TYPED_DIR)

# --- imports below this line may include typed/ locals and stdlib -------------

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import import_audit

CONTRACT_REL = "experiments/EXP-BINSTD-178742/specification.yaml"
EXPECTED_CONTRACT_SHA256 = (
    "e841c33a30a4c8eaf1dc80f2199ec8dc34343bdb5d5e4ce38f918f055485d19f"
)
EXPERIMENT_ID = "EXP-BINSTD-178742"
HYPOTHESIS_ID = "H-BINSTD-ce4f38"
GOAL_ID = "GOAL-ECDLP2M-001"
BATCH_ID = "BATCH-8c7af6"
PACKAGING_TASK = "TASK-20260930-d007a4"
AUTH_DECISION = "DEC-20260930-70bff3"
APPROVAL_DECISION = "DEC-20260930-735b4d"


def _repo_root() -> Path:
    # typed/ -> implementation/ -> EXP-BINSTD-178742/ -> experiments/ -> repo
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
    """Validate package integrity without scoring Part 1/Part 2."""
    root = _repo_root()
    contract = root / CONTRACT_REL
    trial = _load_trial_plan()
    report: Dict[str, Any] = {
        "mode": "packaging-check",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "goal_id": GOAL_ID,
        "batch_id": BATCH_ID,
        "packaging_task": PACKAGING_TASK,
        "authorization_decision": AUTH_DECISION,
        "approval_decision": APPROVAL_DECISION,
        "typed_dir": _TYPED_DIR,
        "sys_path_0": sys.path[0],
        "scientific_execution_authorized": bool(
            trial.get("scientific_execution_authorized")
        ),
        "packaging_only": bool(trial.get("packaging_only")),
        "maximum_runs": trial.get("maximum_runs"),
        "runs_launched": 0,
        "amazon_bedrock": "not_used",
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

    if trial.get("scientific_execution_authorized") is not False:
        report["ok"] = False
        report["problems"].append(
            "trial-plan scientific_execution_authorized must be false for packaging"
        )
    if not trial.get("packaging_only"):
        report["ok"] = False
        report["problems"].append("trial-plan packaging_only must be true")
    if trial.get("maximum_runs") != 0:
        report["ok"] = False
        report["problems"].append("trial-plan maximum_runs must be 0")
    if trial.get("authorization_decision") != AUTH_DECISION:
        report["ok"] = False
        report["problems"].append(
            f"trial-plan authorization_decision must be {AUTH_DECISION}"
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

    import gf2n  # noqa: WPS433
    import part1_surface  # noqa: WPS433
    import part2_surface  # noqa: WPS433

    gf2n_probe = gf2n.packaging_surface()
    p1_probe = part1_surface.packaging_surface()
    p2_probe = part2_surface.packaging_surface()
    report["surface_probes"] = {
        "gf2n": gf2n_probe,
        "part1_surface": p1_probe,
        "part2_surface": p2_probe,
    }
    for name, probe in (
        ("gf2n", gf2n_probe),
        ("part1_surface", p1_probe),
        ("part2_surface", p2_probe),
    ):
        if not probe.get("ok"):
            report["ok"] = False
            report["problems"].append(f"{name} packaging_surface failed")

    # Confirm no RUN-* under this experiment.
    runs_dir = root / "experiments" / EXPERIMENT_ID / "runs"
    if runs_dir.is_dir():
        run_kids = sorted(p.name for p in runs_dir.iterdir())
        report["runs_directory_entries"] = run_kids
        if run_kids:
            report["ok"] = False
            report["problems"].append(
                f"unexpected entries under runs/: {run_kids!r}"
            )
    else:
        report["runs_directory_entries"] = []

    report["modules_present"] = sorted(
        p.name for p in Path(_TYPED_DIR).iterdir() if p.is_file()
    )
    return report


def refuse_auth(reason: str, argv: List[str]) -> int:
    """Refuse scientific launch while packaging / auth flags block --run."""
    msg = (
        f"REFUSED_AUTH: {reason}\n"
        f"packaging_task={PACKAGING_TASK} authorization={AUTH_DECISION}\n"
        f"scientific_execution_authorized=false packaging_only=true "
        f"maximum_runs=0\n"
        f"argv={argv!r}\n"
        "Part 1/Part 2 scoring is not admitted by this packaging card.\n"
    )
    sys.stderr.write(msg)
    return 2


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="run.py",
        description=(
            "EXP-BINSTD-178742 typed entry "
            "(--packaging-check default; --run REFUSES while packaging_only)"
        ),
    )
    parser.add_argument(
        "--packaging-check",
        action="store_true",
        default=False,
        help="Validate AST imports and successor_contract_sha256; default mode",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help=(
            "Scientific launch path. REFUSED while "
            "scientific_execution_authorized is false or packaging_only is true."
        ),
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="",
        help="Optional path to write JSON packaging-check report",
    )
    if not argv:
        argv = ["--packaging-check"]
    args, _unknown = parser.parse_known_args(argv)
    if not args.run and not args.packaging_check:
        args.packaging_check = True

    if args.run:
        trial = _load_trial_plan()
        if not trial.get("scientific_execution_authorized"):
            return refuse_auth(
                "scientific_execution_authorized is false in trial-plan.json",
                argv,
            )
        if trial.get("packaging_only"):
            return refuse_auth(
                "packaging_only is true in trial-plan.json",
                argv,
            )
        if trial.get("maximum_runs", 0) == 0:
            return refuse_auth(
                "maximum_runs is 0 in trial-plan.json",
                argv,
            )
        # Unreachable under current packaging flags; keep fail-closed.
        return refuse_auth(
            "scientific path not implemented on this packaging card",
            argv,
        )

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
