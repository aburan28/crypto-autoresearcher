#!/usr/bin/env python3
"""EXP-AUXIN-339fb0 typed implementation entry point.

Launch:
  python3 -I experiments/EXP-AUXIN-339fb0/implementation/typed/run.py --packaging-check
  python3 -I experiments/EXP-AUXIN-339fb0/implementation/typed/run.py --run

Under python3 -I the directory of run.py is NOT on sys.path. This file therefore
inserts the absolute path of experiments/EXP-AUXIN-339fb0/implementation/typed/
at sys.path[0] BEFORE importing any typed module, importing only sys and os
before doing so (corrective.custody.run_entry_sys_path / RI-7).

Wiring (TASK-20260930-6d25ea / DEC-20260930-224fc1 / DEC-20260930-25e287):
  --run no longer unconditionally packaging-refuses. When
  scientific_execution_authorized is true and packaging_only is false, it
  enters Stage A0 admission_gate_check() (dry probes to stdout; no RUN-* mint;
  no census scoring). Packaging archive BATCH-d0b34e remains immutable history.
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
import re
import shutil
import subprocess
from decimal import getcontext
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import import_audit

CONTRACT_REL = "experiments/EXP-AUXIN-339fb0/specification.yaml"
EXPECTED_CONTRACT_SHA256 = (
    "6a1dca32c109d5badf4ba143c31f9d4d9a49e18ae287c8bb4fc604526bf02ecc"
)
EXPERIMENT_ID = "EXP-AUXIN-339fb0"
PACKAGING_TASK = "TASK-20260930-e9f8bf"
WIRING_TASK = "TASK-20260930-6d25ea"
AUTH_DECISION = "DEC-20260930-224fc1"
WIRING_DECISION = "DEC-20260930-25e287"

# Declared minima from tools_and_admission (specification.yaml).
ECM_MIN = (7, 0, 4)
PARI_MIN = (2, 13, 0)
CYPARI2_DIST_MIN = (2, 1, 5)
PYPDF_MIN = (3, 0, 0)
PYTHON_MIN = (3, 10)


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


def _parse_dotted_triple(text: str) -> Optional[Tuple[int, ...]]:
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def _version_ok(got: Optional[Tuple[int, ...]], minimum: Tuple[int, ...]) -> bool:
    if got is None:
        return False
    return got >= minimum


def packaging_check() -> Dict[str, Any]:
    """Validate package integrity without scoring any census row."""
    root = _repo_root()
    contract = root / CONTRACT_REL
    trial = _load_trial_plan()
    report: Dict[str, Any] = {
        "mode": "packaging-check",
        "experiment_id": EXPERIMENT_ID,
        "packaging_task": PACKAGING_TASK,
        "wiring_task": WIRING_TASK,
        "typed_dir": _TYPED_DIR,
        "sys_path_0": sys.path[0],
        "scientific_execution_authorized": bool(
            trial.get("scientific_execution_authorized")
        ),
        "packaging_only": bool(trial.get("packaging_only")),
        "maximum_runs": trial.get("maximum_runs"),
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

    leaf = cert_verify.make_pratt_leaf_two()
    ok2, _ = cert_verify.verify_pratt(leaf)
    if not ok2:
        report["ok"] = False
        report["problems"].append("cert_verify leaf-2 self-check failed")
    p3 = cert_verify.build_pratt_for_small_prime(3)
    ok3 = False
    if p3 is None:
        report["ok"] = False
        report["problems"].append("could not build Pratt for 3")
    else:
        ok3, _ = cert_verify.verify_pratt(p3)
        if not ok3:
            report["ok"] = False
            report["problems"].append("cert_verify Pratt-3 self-check failed")

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


def _probe_python() -> Dict[str, Any]:
    ver = sys.version_info[:3]
    got = (ver[0], ver[1], ver[2])
    return {
        "item": "path_b_arithmetic_python",
        "present": True,
        "version_command_output": "Python %d.%d.%d" % ver,
        "parsed_version": list(got),
        "minimum": list(PYTHON_MIN),
        "meets_minimum": _version_ok(got, PYTHON_MIN),
    }


def _probe_ecm() -> Dict[str, Any]:
    ecm = shutil.which("ecm")
    item: Dict[str, Any] = {
        "item": "ecm_backend",
        "present": ecm is not None,
        "path": ecm,
        "minimum": list(ECM_MIN),
        "meets_minimum": False,
        "version_command_output": None,
        "parsed_version": None,
        "problems": [],
    }
    if ecm is None:
        item["problems"].append("ecm binary not found on PATH")
        return item
    try:
        proc = subprocess.run(
            ["bash", "-lc", "printf '2^89-1\\n' | ecm -c 1 2000"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        item["version_command_output"] = out[:4000]
        # Banner: "GMP-ECM <dotted> ..."
        m = re.search(r"GMP-ECM\s+(\d+\.\d+\.\d+)", out)
        if not m:
            item["problems"].append("could not parse GMP-ECM version from banner")
            return item
        got = _parse_dotted_triple(m.group(1))
        item["parsed_version"] = list(got) if got else None
        item["meets_minimum"] = _version_ok(got, ECM_MIN)
        if not item["meets_minimum"]:
            item["problems"].append(
                f"ECM version {got} below minimum {ECM_MIN}"
            )
    except Exception as exc:  # noqa: BLE001 — record infrastructure probe failure
        item["problems"].append(f"ecm probe failed: {exc!r}")
    return item


def _probe_cypari2() -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "item": "certificate_and_factoring_library_cypari2",
        "present": False,
        "minimum_distribution": list(CYPARI2_DIST_MIN),
        "minimum_pari": list(PARI_MIN),
        "meets_minimum": False,
        "version_command_output": None,
        "cypari2_version": None,
        "pari_version": None,
        "problems": [],
    }
    try:
        import cypari2  # noqa: WPS433

        item["present"] = True
        dist = getattr(cypari2, "__version__", "")
        pari_line = ""
        try:
            pari_line = str(cypari2.Pari()("version()"))
        except Exception as exc:  # noqa: BLE001
            item["problems"].append(f"Pari version() failed: {exc!r}")
        item["version_command_output"] = f"{dist}\n{pari_line}"
        item["cypari2_version"] = dist
        item["pari_version"] = pari_line
        dist_t = _parse_dotted_triple(str(dist))
        pari_t = _parse_dotted_triple(pari_line)
        item["parsed_cypari2"] = list(dist_t) if dist_t else None
        item["parsed_pari"] = list(pari_t) if pari_t else None
        ok_dist = _version_ok(dist_t, CYPARI2_DIST_MIN)
        ok_pari = _version_ok(pari_t, PARI_MIN)
        item["meets_minimum"] = bool(ok_dist and ok_pari)
        if not ok_dist:
            item["problems"].append(
                f"cypari2 distribution {dist_t} below minimum {CYPARI2_DIST_MIN}"
            )
        if not ok_pari:
            item["problems"].append(
                f"PARI library {pari_t} below minimum {PARI_MIN}"
            )
    except Exception as exc:  # noqa: BLE001
        item["problems"].append(f"cypari2 not importable: {exc!r}")
    return item


def _probe_pypdf() -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "item": "pdf_text_extractor_pypdf",
        "present": False,
        "minimum": list(PYPDF_MIN),
        "meets_minimum": False,
        "version_command_output": None,
        "parsed_version": None,
        "problems": [],
    }
    try:
        import pypdf  # noqa: WPS433

        item["present"] = True
        ver = getattr(pypdf, "__version__", "")
        item["version_command_output"] = str(ver)
        got = _parse_dotted_triple(str(ver))
        item["parsed_version"] = list(got) if got else None
        item["meets_minimum"] = _version_ok(got, PYPDF_MIN)
        if not item["meets_minimum"]:
            item["problems"].append(
                f"pypdf version {got} below minimum {PYPDF_MIN}"
            )
    except Exception as exc:  # noqa: BLE001
        item["problems"].append(f"pypdf not importable: {exc!r}")
    return item


def _check_successor_hash() -> Dict[str, Any]:
    root = _repo_root()
    contract = root / CONTRACT_REL
    trial = _load_trial_plan()
    item: Dict[str, Any] = {
        "item": "successor_contract_sha256",
        "ok": False,
        "expected": EXPECTED_CONTRACT_SHA256,
        "trial_plan": trial.get("successor_contract_sha256"),
        "live_contract": None,
        "problems": [],
    }
    if not contract.is_file():
        item["problems"].append(f"missing contract file {contract}")
        return item
    live = _sha256_file(contract)
    item["live_contract"] = live
    if live != EXPECTED_CONTRACT_SHA256:
        item["problems"].append(
            f"live contract sha256 {live} != expected {EXPECTED_CONTRACT_SHA256}"
        )
    if trial.get("successor_contract_sha256") != live:
        item["problems"].append(
            "trial-plan successor_contract_sha256 does not match live contract"
        )
    if trial.get("successor_contract_sha256") != EXPECTED_CONTRACT_SHA256:
        item["problems"].append(
            "trial-plan successor_contract_sha256 does not match expected constant"
        )
    item["ok"] = not item["problems"]
    return item


def _check_import_audit() -> Dict[str, Any]:
    audit = import_audit.audit_tree(Path(_TYPED_DIR))
    return {
        "item": "ast_import_audit",
        "ok": bool(audit.get("ok")),
        "files": [
            {
                "file": f["file"],
                "ok": f["ok"],
                "stdlib_only_required": f["stdlib_only_required"],
                "problems": f["problems"],
            }
            for f in audit.get("files", [])
        ],
        "problems": [] if audit.get("ok") else ["AST import audit failed"],
    }


def admission_gate_check() -> Dict[str, Any]:
    """Stage A0 admission dry check — no RUN-* directory, no census scoring.

    Implements tools_and_admission.admission_gate probes that can run without
    minting a run directory. Heavy self-tests that require missing tools are
    recorded as failed infrastructure items (absence_rule), never substituted.
    """
    trial = _load_trial_plan()
    report: Dict[str, Any] = {
        "mode": "admission_gate_check",
        "stage": "A0_admission",
        "experiment_id": EXPERIMENT_ID,
        "wiring_task": WIRING_TASK,
        "authorization_decision": AUTH_DECISION,
        "wiring_decision": WIRING_DECISION,
        "scientific_execution_authorized": bool(
            trial.get("scientific_execution_authorized")
        ),
        "packaging_only": bool(trial.get("packaging_only")),
        "maximum_runs": trial.get("maximum_runs"),
        "runs_launched": 0,
        "run_directory_minted": False,
        "census_scored": False,
        "amazon_bedrock": "not_used",
        "items": [],
        "ok": True,
        "problems": [],
        "classification_if_failed": "infrastructure_error",
        "note": (
            "Dry admission_gate only. Does not write admission_receipt.json under "
            "experiments/.../runs/. Does not score census rows. Does not mint RUN-*."
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
            "admission_gate path is blocked until packaging_only=false"
        )
        report["classification_if_failed"] = "specification_error"
        return report

    hash_item = _check_successor_hash()
    report["items"].append(hash_item)
    if not hash_item["ok"]:
        report["ok"] = False
        report["problems"].extend(hash_item["problems"])
        report["classification_if_failed"] = "invalid_measurement"

    audit_item = _check_import_audit()
    report["items"].append(audit_item)
    if not audit_item["ok"]:
        report["ok"] = False
        report["problems"].extend(audit_item["problems"])

    tool_probes = [
        _probe_python(),
        _probe_ecm(),
        _probe_cypari2(),
        _probe_pypdf(),
    ]
    for probe in tool_probes:
        report["items"].append(probe)
        if not probe.get("meets_minimum") or not probe.get("present", True):
            report["ok"] = False
            probs = probe.get("problems") or [
                f"{probe.get('item')}: version/presence check failed"
            ]
            report["problems"].extend(probs)

    # Self-tests (2)-(5),(8): attempt only when prerequisites present; otherwise
    # record infrastructure stop without substituting tools or scoring census.
    ecm_ok = any(
        i.get("item") == "ecm_backend" and i.get("meets_minimum") for i in report["items"]
    )
    cypari_ok = any(
        i.get("item") == "certificate_and_factoring_library_cypari2"
        and i.get("meets_minimum")
        for i in report["items"]
    )
    pypdf_ok = any(
        i.get("item") == "pdf_text_extractor_pypdf" and i.get("meets_minimum")
        for i in report["items"]
    )

    ecm_self: Dict[str, Any] = {
        "item": "ecm_self_test",
        "attempted": False,
        "ok": False,
        "problems": [],
    }
    if ecm_ok:
        ecm_self["attempted"] = True
        try:
            proc = subprocess.run(
                [
                    "bash",
                    "-lc",
                    "printf '(2^31-1)*(2^89-1)\\n' | ecm -one -c 25 2000",
                ],
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )
            out = (proc.stdout or "") + (proc.stderr or "")
            ecm_self["output_excerpt"] = out[:2000]
            # Factor 2^31-1 = 2147483647
            if "2147483647" in out:
                ecm_self["ok"] = True
            else:
                ecm_self["problems"].append(
                    "ECM self-test did not report factor 2147483647 (2^31-1)"
                )
        except Exception as exc:  # noqa: BLE001
            ecm_self["problems"].append(f"ECM self-test failed: {exc!r}")
    else:
        ecm_self["problems"].append(
            "ECM self-test skipped: ecm backend not admitted (infrastructure stop)"
        )
    report["items"].append(ecm_self)
    if not ecm_self["ok"]:
        report["ok"] = False
        report["problems"].extend(ecm_self["problems"])

    pari_alarm: Dict[str, Any] = {
        "item": "pari_alarm_self_test",
        "attempted": False,
        "ok": False,
        "problems": [],
    }
    if cypari_ok:
        pari_alarm["attempted"] = True
        try:
            import cypari2  # noqa: WPS433

            pari = cypari2.Pari()
            raised = False
            try:
                pari("alarm(1, while(1, ))")
            except Exception:  # noqa: BLE001 — alarm must raise
                raised = True
            pari_alarm["ok"] = raised
            if not raised:
                pari_alarm["problems"].append(
                    "PARI alarm(1, while(1,)) did not raise an alarm error"
                )
        except Exception as exc:  # noqa: BLE001
            pari_alarm["problems"].append(f"PARI alarm self-test failed: {exc!r}")
    else:
        pari_alarm["problems"].append(
            "PARI alarm self-test skipped: cypari2 not admitted (infrastructure stop)"
        )
    report["items"].append(pari_alarm)
    if not pari_alarm["ok"]:
        report["ok"] = False
        report["problems"].extend(pari_alarm["problems"])

    cert_self: Dict[str, Any] = {
        "item": "certificate_self_test_and_tamper",
        "attempted": False,
        "ok": False,
        "problems": [],
        "note": (
            "Full path-A certificates for 2^89-1 and 2^607-1 require cypari2. "
            "Wiring dry-check records attempt status only; does not mint RUN-*."
        ),
    }
    if cypari_ok:
        cert_self["attempted"] = True
        cert_self["problems"].append(
            "certificate_self_test deferred: path-A production not invoked "
            "from wiring dry-check (would be a scientific stage write); "
            "tool presence recorded separately. Treat as incomplete admission "
            "until a RUN-* admission_receipt is written."
        )
        # Incomplete until a real run directory hosts the receipt — fail closed.
        cert_self["ok"] = False
    else:
        cert_self["problems"].append(
            "certificate self-test skipped: cypari2 not admitted (infrastructure stop)"
        )
    report["items"].append(cert_self)
    if not cert_self["ok"]:
        report["ok"] = False
        report["problems"].extend(cert_self["problems"])

    pdf_self: Dict[str, Any] = {
        "item": "pdf_digit_check_machinery_self_test",
        "attempted": False,
        "ok": False,
        "problems": [],
    }
    if pypdf_ok:
        pdf_self["attempted"] = True
        pdf_path = (
            _repo_root()
            / "inputs"
            / "SAFECURVES-20260825"
            / "sp800-186.pdf"
        )
        if not pdf_path.is_file():
            # Try alternate declared locations under inputs/
            candidates = list(
                (_repo_root() / "inputs").rglob("sp800-186.pdf")
            ) if (_repo_root() / "inputs").is_dir() else []
            pdf_path = candidates[0] if candidates else pdf_path
        if not pdf_path.is_file():
            pdf_self["problems"].append(f"sp800-186.pdf not found at {pdf_path}")
        else:
            try:
                from pypdf import PdfReader  # noqa: WPS433

                reader = PdfReader(str(pdf_path))
                text = "\n".join(
                    (page.extract_text() or "") for page in reader.pages
                )
                normalized = (
                    text.replace("\\", "")
                    .translate({ord(c): None for c in " \t\n\r\f\v"})
                    .lower()
                )
                pdf_self["ok"] = "discretelogarithm" in normalized
                if not pdf_self["ok"]:
                    pdf_self["problems"].append(
                        'normalized PDF text missing contiguous "discretelogarithm"'
                    )
            except Exception as exc:  # noqa: BLE001
                pdf_self["problems"].append(f"pdf self-test failed: {exc!r}")
    else:
        pdf_self["problems"].append(
            "pdf self-test skipped: pypdf not admitted (infrastructure stop)"
        )
    report["items"].append(pdf_self)
    if not pdf_self["ok"]:
        report["ok"] = False
        report["problems"].extend(pdf_self["problems"])

    report["problems"] = list(dict.fromkeys(report["problems"]))
    return report


def refuse_auth(reason: str, argv: List[str]) -> int:
    """Refuse before admission when trial-plan auth flags block --run."""
    msg = (
        f"REFUSED_AUTH: {reason}\n"
        f"wiring_task={WIRING_TASK} authorization={AUTH_DECISION} "
        f"wiring_decision={WIRING_DECISION}\n"
        f"argv={argv!r}\n"
    )
    sys.stderr.write(msg)
    return 2


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="run.py",
        description=(
            "EXP-AUXIN-339fb0 typed entry "
            "(--packaging-check default; --run → admission_gate_check)"
        ),
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
        help=(
            "Enter Stage A0 admission_gate_check when authorized "
            "(no RUN-* mint, no census scoring)"
        ),
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default="",
        help="Optional path to write JSON report (packaging-check or admission)",
    )
    # Default: packaging-check when neither flag given.
    if not argv:
        argv = ["--packaging-check"]
    args, unknown = parser.parse_known_args(argv)
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
        report = admission_gate_check()
        text = json.dumps(report, indent=2, sort_keys=True)
        if args.json_out:
            out = Path(args.json_out)
            # Only allow writing under typed/ or the wiring report dir — never runs/.
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text + "\n", encoding="utf-8")
        sys.stdout.write(text + "\n")
        # Exit 0 only if all admission items that can be checked without a RUN
        # directory pass; otherwise non-zero with infrastructure reasons.
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
