#!/usr/bin/env python3
"""EXP-BINSTD-178742 typed implementation entry point.

Launch:
  python3 -I experiments/EXP-BINSTD-178742/implementation/typed/run.py --packaging-check
  python3 -I experiments/EXP-BINSTD-178742/implementation/typed/run.py --run

Under python3 -I the directory of run.py is NOT on sys.path. This file therefore
inserts the absolute path of experiments/EXP-BINSTD-178742/implementation/typed/
at sys.path[0] BEFORE importing any typed module, importing only sys and os
before doing so (corrective.custody.run_entry_sys_path).

Authorization:
  Packaging: TASK-20260930-d007a4 / DEC-20260930-70bff3 (implementation_authorized).
  Wiring: TASK-20260930-606126 / DEC-20260930-8de5ba (scientific_execution_authorized).
  --run REFUSES while scientific_execution_authorized is false or packaging_only
  is true. When authorized, --run enters a dry contract-path check (custody +
  stopping-rule presence) and does NOT score Part 1/Part 2 and does NOT mint
  RUN-*. Opening/wiring is not a solve claim.
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
    "ffacf110b050a93f1ee7b8bee132591a14cb96cb280dbafda81bbef2877b234b"
)
EXPERIMENT_ID = "EXP-BINSTD-178742"
HYPOTHESIS_ID = "H-BINSTD-ce4f38"
GOAL_ID = "GOAL-ECDLP2M-001"
BATCH_ID = "BATCH-ccfdc6"
PACKAGING_TASK = "TASK-20260930-d007a4"
PACKAGING_BATCH = "BATCH-8c7af6"
WIRING_TASK = "TASK-20260930-606126"
AUTH_DECISION = "DEC-20260930-8de5ba"
IMPL_AUTH_DECISION = "DEC-20260930-70bff3"
APPROVAL_DECISION = "DEC-20260930-735b4d"
CONTRACT_MAXIMUM_RUNS = 4

# Contract stopping-rule ids that must remain present (never skipped).
REQUIRED_STOPPING_RULE_PREFIXES = (
    "SR-1.",
    "SR-2.",
    "SR-3.",
    "SR-3b.",
    "SR-4.",
    "SR-5.",
    "SR-5b.",
    "SR-5c.",
    "SR-6.",
    "SR-7.",
    "SR-8.",
    "SR-9.",
)


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


def _check_successor_hash(trial: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    root = _repo_root()
    contract = root / CONTRACT_REL
    trial = trial if trial is not None else _load_trial_plan()
    item: Dict[str, Any] = {
        "item": "successor_contract_sha256",
        "expected": EXPECTED_CONTRACT_SHA256,
        "ok": True,
        "problems": [],
    }
    if not contract.is_file():
        item["ok"] = False
        item["problems"].append(f"missing contract file {contract}")
        return item
    live = _sha256_file(contract)
    tp_hash = trial.get("successor_contract_sha256")
    item["live_contract"] = live
    item["trial_plan"] = tp_hash
    if live != EXPECTED_CONTRACT_SHA256:
        item["ok"] = False
        item["problems"].append(
            f"live contract sha256 {live} != expected {EXPECTED_CONTRACT_SHA256}"
        )
    if tp_hash != EXPECTED_CONTRACT_SHA256:
        item["ok"] = False
        item["problems"].append(
            f"trial-plan successor_contract_sha256 {tp_hash!r} mismatch"
        )
    if tp_hash != live:
        item["ok"] = False
        item["problems"].append(
            "trial-plan hash does not match live contract file bytes"
        )
    return item


def _check_stopping_rules_present() -> Dict[str, Any]:
    """Confirm frozen stopping_rules remain in the live contract text.

    Does not execute or skip them — presence-only custody check so --run cannot
    proceed while pretending the contract has no stopping rules.
    """
    root = _repo_root()
    contract = root / CONTRACT_REL
    item: Dict[str, Any] = {
        "item": "contract_stopping_rules_present",
        "ok": True,
        "problems": [],
        "required_prefixes": list(REQUIRED_STOPPING_RULE_PREFIXES),
        "found": [],
        "missing": [],
    }
    if not contract.is_file():
        item["ok"] = False
        item["problems"].append(f"missing contract file {contract}")
        return item
    text = contract.read_text(encoding="utf-8")
    if "stopping_rules:" not in text:
        item["ok"] = False
        item["problems"].append("stopping_rules: key absent from live contract")
        return item
    for prefix in REQUIRED_STOPPING_RULE_PREFIXES:
        if prefix in text:
            item["found"].append(prefix)
        else:
            item["missing"].append(prefix)
    if item["missing"]:
        item["ok"] = False
        item["problems"].append(
            f"missing stopping rule prefixes: {item['missing']!r}"
        )
    return item


def packaging_check() -> Dict[str, Any]:
    """Validate package integrity without scoring Part 1/Part 2."""
    root = _repo_root()
    trial = _load_trial_plan()
    report: Dict[str, Any] = {
        "mode": "packaging-check",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "goal_id": GOAL_ID,
        "batch_id": BATCH_ID,
        "packaging_task": PACKAGING_TASK,
        "wiring_task": WIRING_TASK,
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

    hash_item = _check_successor_hash(trial)
    report["contract_sha256"] = hash_item.get("live_contract")
    report["trial_plan_successor_contract_sha256"] = hash_item.get("trial_plan")
    if not hash_item["ok"]:
        report["ok"] = False
        report["problems"].extend(hash_item["problems"])

    # After wiring: expect authorized flags matching DEC-20260930-8de5ba.
    if trial.get("scientific_execution_authorized") is not True:
        report["ok"] = False
        report["problems"].append(
            "trial-plan scientific_execution_authorized must be true after wiring"
        )
    if trial.get("packaging_only") is not False:
        report["ok"] = False
        report["problems"].append(
            "trial-plan packaging_only must be false after wiring"
        )
    if trial.get("maximum_runs") != CONTRACT_MAXIMUM_RUNS:
        report["ok"] = False
        report["problems"].append(
            f"trial-plan maximum_runs must be {CONTRACT_MAXIMUM_RUNS} "
            f"(contract budget), got {trial.get('maximum_runs')!r}"
        )
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

    # Confirm no RUN-* under this experiment (wiring card: still zero).
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


def contract_path_check() -> Dict[str, Any]:
    """Dry contract-path check when scientific execution is authorized.

    Verifies custody hash, stopping-rule presence, and trial-plan auth flags.
    Does NOT score Part 1/Part 2. Does NOT mint RUN-*. Does NOT skip stopping
    rules — it only confirms they remain declared on the live contract.
    """
    trial = _load_trial_plan()
    report: Dict[str, Any] = {
        "mode": "contract_path_check",
        "stage": "authorized_dry_gate",
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "goal_id": GOAL_ID,
        "batch_id": BATCH_ID,
        "wiring_task": WIRING_TASK,
        "authorization_decision": AUTH_DECISION,
        "implementation_authorization_decision": IMPL_AUTH_DECISION,
        "approval_decision": APPROVAL_DECISION,
        "scientific_execution_authorized": bool(
            trial.get("scientific_execution_authorized")
        ),
        "packaging_only": bool(trial.get("packaging_only")),
        "maximum_runs": trial.get("maximum_runs"),
        "runs_launched": 0,
        "run_directory_minted": False,
        "part1_scored": False,
        "part2_scored": False,
        "amazon_bedrock": "not_used",
        "items": [],
        "ok": True,
        "problems": [],
        "classification_if_failed": "infrastructure_error",
        "note": (
            "Dry contract-path only. Does not write under experiments/.../runs/. "
            "Does not score Part 1/Part 2. Does not mint RUN-*. Stopping rules "
            "remain binding for any later scientific /run."
        ),
    }

    if not trial.get("scientific_execution_authorized"):
        report["ok"] = False
        report["problems"].append(
            "REFUSED_AUTH: scientific_execution_authorized is false in trial-plan"
        )
        report["classification_if_failed"] = "specification_error"
        return report
    if trial.get("packaging_only"):
        report["ok"] = False
        report["problems"].append(
            "REFUSED_AUTH: packaging_only is true in trial-plan; "
            "contract path is blocked until packaging_only=false"
        )
        report["classification_if_failed"] = "specification_error"
        return report
    if trial.get("maximum_runs", 0) == 0:
        report["ok"] = False
        report["problems"].append(
            "REFUSED_AUTH: maximum_runs is 0 in trial-plan"
        )
        report["classification_if_failed"] = "specification_error"
        return report
    if trial.get("maximum_runs") != CONTRACT_MAXIMUM_RUNS:
        report["ok"] = False
        report["problems"].append(
            f"maximum_runs {trial.get('maximum_runs')!r} != contract "
            f"{CONTRACT_MAXIMUM_RUNS}"
        )
        report["classification_if_failed"] = "specification_error"

    hash_item = _check_successor_hash(trial)
    report["items"].append(hash_item)
    if not hash_item["ok"]:
        report["ok"] = False
        report["problems"].extend(hash_item["problems"])
        report["classification_if_failed"] = "invalid_measurement"

    sr_item = _check_stopping_rules_present()
    report["items"].append(sr_item)
    if not sr_item["ok"]:
        report["ok"] = False
        report["problems"].extend(sr_item["problems"])
        report["classification_if_failed"] = "specification_error"

    audit = import_audit.audit_tree(Path(_TYPED_DIR))
    audit_item: Dict[str, Any] = {
        "item": "import_audit",
        "ok": bool(audit.get("ok")),
        "problems": [] if audit.get("ok") else ["AST import audit failed"],
        "files": [
            {
                "file": f["file"],
                "ok": f["ok"],
                "problems": f["problems"],
            }
            for f in audit.get("files", [])
        ],
    }
    report["items"].append(audit_item)
    if not audit_item["ok"]:
        report["ok"] = False
        report["problems"].extend(audit_item["problems"])

    # Surface probes only (toy packaging surfaces) — not Part 1/2 scoring.
    import gf2n  # noqa: WPS433
    import part1_surface  # noqa: WPS433
    import part2_surface  # noqa: WPS433

    surfaces = {
        "gf2n": gf2n.packaging_surface(),
        "part1_surface": part1_surface.packaging_surface(),
        "part2_surface": part2_surface.packaging_surface(),
    }
    surface_item: Dict[str, Any] = {
        "item": "typed_surface_probes",
        "ok": True,
        "problems": [],
        "probes": surfaces,
        "note": "packaging_surface only; Part 1/2 not scored",
    }
    for name, probe in surfaces.items():
        if not probe.get("ok"):
            surface_item["ok"] = False
            surface_item["problems"].append(f"{name} packaging_surface failed")
    report["items"].append(surface_item)
    if not surface_item["ok"]:
        report["ok"] = False
        report["problems"].extend(surface_item["problems"])

    root = _repo_root()
    runs_dir = root / "experiments" / EXPERIMENT_ID / "runs"
    runs_item: Dict[str, Any] = {
        "item": "no_run_star_minted",
        "ok": True,
        "problems": [],
        "entries": [],
    }
    if runs_dir.is_dir():
        kids = sorted(p.name for p in runs_dir.iterdir())
        runs_item["entries"] = kids
        if kids:
            runs_item["ok"] = False
            runs_item["problems"].append(
                f"unexpected runs/ entries on wiring dry gate: {kids!r}"
            )
    report["items"].append(runs_item)
    if not runs_item["ok"]:
        report["ok"] = False
        report["problems"].extend(runs_item["problems"])

    return report


def refuse_auth(reason: str, argv: List[str]) -> int:
    """Refuse scientific launch while auth / packaging flags block --run."""
    msg = (
        f"REFUSED_AUTH: {reason}\n"
        f"wiring_task={WIRING_TASK} authorization={AUTH_DECISION} "
        f"packaging_task={PACKAGING_TASK}\n"
        f"argv={argv!r}\n"
    )
    sys.stderr.write(msg)
    return 2


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="run.py",
        description=(
            "EXP-BINSTD-178742 typed entry "
            "(--packaging-check default; --run → contract_path_check when authorized)"
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
            "Enter dry contract_path_check when scientific_execution_authorized "
            "is true and packaging_only is false. Does not score Part 1/2; "
            "does not mint RUN-*. REFUSED while unauthorized or packaging_only."
        ),
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="",
        help="Optional path to write JSON packaging-check / contract-path report",
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
        report = contract_path_check()
        text = json.dumps(report, indent=2, sort_keys=True)
        if args.json_out:
            out = Path(args.json_out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text + "\n", encoding="utf-8")
        sys.stdout.write(text + "\n")
        return 0 if report.get("ok") else 1

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
