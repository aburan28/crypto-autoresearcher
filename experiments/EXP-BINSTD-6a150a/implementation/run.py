#!/usr/bin/env python3
"""EXP-BINSTD-6a150a Stages 0-2 launcher (frozen contract v1).

Stage 0: Freeze retrieval protocol allow-list + preregistered predictions
         BEFORE any download.
Stage 1: Attempt TIER-P retrieval under the freeze; write admission_receipt.
Stage 2: Score five c2pnb k|r-1 rows; write part1_rows + RESULTS.md with
         exactly one O-* label.

Observations only. No Magma/Sage/AUXIN/Bedrock. No Part-2. No ECDLP solve.
No invented r strings. Amazon Bedrock is not selected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_IMPL = Path(__file__).resolve().parent
if str(_IMPL) not in sys.path:
    sys.path.insert(0, str(_IMPL))

from kdiv import ROWS, score_row  # noqa: E402

EXPERIMENT_ID = "EXP-BINSTD-6a150a"
HYPOTHESIS_ID = "H-BINSTD-ceae35"
APPROVED_BY = "DEC-20261004-173be8"
EXP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]

# Allow-listed local roots / document classes (frozen at Stage 0).
# No secondary dumps. No recall.
ALLOWLISTED_LOCAL_GLOBS = [
    "inputs/ANSI-X9.62*/**",
    "inputs/X9.62*/**",
    "inputs/ANSI_X962*/**",
]
FORBIDDEN_AS_TIER_P = [
    "analysis/binstd-curve-audit/",
    "openssl ecparam",
    "recalled",
]


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"refusing overwrite: {path}")
    path.write_text(text, encoding="utf-8")


def write_yaml_manifest(path: Path, obj: dict) -> None:
    lines = []
    for k, v in obj.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            s = str(v).replace("\n", " ")
            lines.append(f'{k}: "{s}"')
    write_text(path, "\n".join(lines) + "\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stage0(run_dir: Path) -> Dict[str, Any]:
    freeze = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "stage": 0,
        "frozen_before_any_download": True,
        "document_classes": {
            "TIER-P": [
                "Published ANSI X9.62 edition/annex publishing the five c2pnb curves",
                "Primary standard that reproduces ANSI X9.62 c2pnb parameters verbatim and says so",
            ],
            "TIER-D": [
                "ANSI X9.62 committee working draft (information-only; never counted verdict)"
            ],
            "FORBIDDEN_AS_SOURCE_OF_R": FORBIDDEN_AS_TIER_P,
        },
        "allowlisted_local_globs": ALLOWLISTED_LOCAL_GLOBS,
        "rows": ROWS,
        "source_rules": [
            "SR-SRC-1",
            "SR-SRC-2",
            "SR-SRC-3",
            "SR-SRC-6",
            "SR-SRC-7",
            "SR-SRC-8",
            "IR-10",
        ],
        "certificate_kind": "none",
        "part1_instrument_pin": "EXP-BINSTD-178742 part1_surface.k_divides_r_minus_1",
        "amazon_bedrock": "NOT SELECTED",
    }
    preds = {
        "experiment_id": EXPERIMENT_ID,
        "heuristic": "HEUR-BINSTD-262544-H1",
        "quantity": (
            "Under TIER-P retrieval, verdict TRUE iff r≡1 (mod k), else FALSE; "
            "fabricated_true_count=0. Under failure, NOT COMPUTED with IMP-X962."
        ),
        "success_labels": [
            "O-CLEAR-X962",
            "O-ALL-DECIDED",
            "O-STILL-IMP-X962",
            "O-ARTIFACT",
            "O-IMPEDIMENT",
        ],
        "hard_gate": "fabricated_true_count == 0",
        "frozen_before_stage1": True,
    }
    freeze_path = EXP_ROOT / "stage0" / "retrieval-protocol-freeze.json"
    pred_path = EXP_ROOT / "stage0" / "preregistered-predictions.json"
    write_json(freeze_path, freeze)
    write_json(pred_path, preds)
    result = {
        "experiment_id": EXPERIMENT_ID,
        "stage": 0,
        "status": "completed",
        "freeze_path": str(freeze_path.relative_to(REPO_ROOT)),
        "predictions_path": str(pred_path.relative_to(REPO_ROOT)),
        "frozen_before_any_download": True,
        "certificate": {"kind": "none"},
    }
    write_json(run_dir / "raw-result.json", result)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "run_stage": 0,
            "status": "completed",
            "validity": "valid",
            "certificate_kind": "none",
            "approved_by": APPROVED_BY,
        },
    )
    return result


def _candidate_files() -> List[Path]:
    roots = [
        REPO_ROOT / "inputs",
    ]
    hits: List[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            pdir = Path(dirpath)
            name_l = pdir.name.lower()
            if not any(tok in name_l for tok in ("x9.62", "x962", "ansi-x9", "ansi_x9")):
                # Also accept files that look like X9.62 inside any inputs subtree
                # only when the parent path contains those tokens.
                parent_l = str(pdir).lower()
                if not any(tok in parent_l for tok in ("x9.62", "x962", "ansi-x9", "ansi_x9")):
                    continue
            for fn in filenames:
                if fn.startswith("."):
                    continue
                hits.append(pdir / fn)
    return sorted(hits)


def stage1(run_dir: Path) -> Dict[str, Any]:
    freeze_path = EXP_ROOT / "stage0" / "retrieval-protocol-freeze.json"
    if not freeze_path.is_file():
        raise FileNotFoundError("Stage 0 freeze missing; refuse Stage 1")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if not freeze.get("frozen_before_any_download"):
        raise RuntimeError("Stage 0 freeze invalid")

    candidates = _candidate_files()
    attempts: List[Dict[str, Any]] = []
    admitted: List[Dict[str, Any]] = []
    for path in candidates:
        rel = str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
        # Refuse forbidden secondary dumps even if path-matched.
        if any(rel.startswith(bad) for bad in ("analysis/binstd-curve-audit/",)):
            attempts.append(
                {
                    "path": rel,
                    "status": "rejected",
                    "reason": "IR-10_secondary_dump",
                }
            )
            continue
        digest = sha256_file(path)
        attempts.append(
            {
                "path": rel,
                "status": "found",
                "sha256": digest,
                "bytes": path.stat().st_size,
                "tier_candidate": "TIER-P_pending_parameter_extraction",
            }
        )
        admitted.append(
            {
                "path": rel,
                "sha256": digest,
                "bytes": path.stat().st_size,
                "tier": "TIER-P_pending_parameter_extraction",
                "note": (
                    "File present under allow-listed inputs tree. Parameter "
                    "extraction for (k,r) is Stage-2 responsibility and must "
                    "record per-row mapping under SR-SRC-7. This design runner "
                    "does not invent r strings from secondary dumps."
                ),
            }
        )

    # Optional env override for an explicitly provisioned TIER-P file outside
    # the default tree (executor may set EXP_BINSTD_6A150A_TIERP_PATH).
    env_path = os.environ.get("EXP_BINSTD_6A150A_TIERP_PATH")
    if env_path:
        p = Path(env_path)
        if p.is_file():
            digest = sha256_file(p)
            admitted.append(
                {
                    "path": str(p),
                    "sha256": digest,
                    "bytes": p.stat().st_size,
                    "tier": "TIER-P_pending_parameter_extraction",
                    "note": "Admitted via EXP_BINSTD_6A150A_TIERP_PATH",
                }
            )
            attempts.append(
                {
                    "path": str(p),
                    "status": "found_env",
                    "sha256": digest,
                }
            )
        else:
            attempts.append(
                {
                    "path": env_path,
                    "status": "missing_env",
                    "reason": "EXP_BINSTD_6A150A_TIERP_PATH not a file",
                }
            )

    impediment = None
    if not admitted:
        impediment = {
            "id": "IMP-X962",
            "condition": "ANSI X9.62 / TIER-P text unreachable under frozen allow-list",
            "what_is_blocked": "decidable k|r-1 for five c2pnb rows",
            "clears_when": "A TIER-P ANSI X9.62 text (or verbatim primary reproduction) is retrieved with sha256",
            "asserts_nothing_about": "the mathematics of k|r-1",
        }

    receipt = {
        "experiment_id": EXPERIMENT_ID,
        "stage": 1,
        "freeze_sha256": sha256_file(freeze_path),
        "attempts": attempts,
        "admitted_sources": admitted,
        "impediment": impediment,
        "rows_pending": [r["name"] for r in ROWS],
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
    }
    out_path = EXP_ROOT / "stage1" / "admission_receipt.json"
    write_json(out_path, receipt)
    result = {
        "experiment_id": EXPERIMENT_ID,
        "stage": 1,
        "status": "completed",
        "admission_receipt": str(out_path.relative_to(REPO_ROOT)),
        "admitted_count": len(admitted),
        "impediment": impediment["id"] if impediment else None,
        "certificate": {"kind": "none"},
    }
    write_json(run_dir / "raw-result.json", result)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "run_stage": 1,
            "status": "completed",
            "validity": "valid",
            "certificate_kind": "none",
            "approved_by": APPROVED_BY,
            "impediment": impediment["id"] if impediment else "none",
        },
    )
    return result


def _load_extracted_params() -> Dict[str, Dict[str, Any]]:
    """Optional executor-supplied TIER-P parameter table.

    Path: experiments/EXP-BINSTD-6a150a/stage1/tierp_params.json
    Schema per row name: {k: int, r: str|int, source_path, source_sha256, tier}.
    Absent or incomplete → NOT COMPUTED. Never invents values.
    """
    path = EXP_ROOT / "stage1" / "tierp_params.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("tierp_params.json must be an object keyed by row name")
    return data


def stage2(run_dir: Path) -> Dict[str, Any]:
    receipt_path = EXP_ROOT / "stage1" / "admission_receipt.json"
    freeze_path = EXP_ROOT / "stage0" / "retrieval-protocol-freeze.json"
    if not receipt_path.is_file() or not freeze_path.is_file():
        raise FileNotFoundError("Stage 0/1 artifacts missing; refuse Stage 2")

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    params = _load_extracted_params()
    scored: List[Dict[str, Any]] = []
    fabricated = 0
    twin_fail = 0

    for row in ROWS:
        name = row["name"]
        entry = params.get(name)
        if not entry:
            scored.append(
                score_row(
                    name,
                    row["m"],
                    None,
                    None,
                    primary_sourced=False,
                    source="SRC-X962",
                    source_sha256=None,
                    tier=None,
                    reason=receipt.get("impediment", {}).get("id")
                    if receipt.get("impediment")
                    else "IMP-X962",
                )
            )
            continue

        tier = entry.get("tier")
        digest = entry.get("source_sha256")
        source = entry.get("source_path") or entry.get("source") or "SRC-X962"
        k = entry.get("k")
        r_raw = entry.get("r")
        try:
            r = int(r_raw) if r_raw is not None else None
            k_i = int(k) if k is not None else None
        except (TypeError, ValueError) as exc:
            raise ValueError(f"bad k/r for {name}: {exc}") from exc

        primary = tier == "TIER-P" and bool(digest) and k_i is not None and r is not None
        s = score_row(
            name,
            row["m"],
            k_i,
            r,
            primary_sourced=primary,
            source=str(source),
            source_sha256=digest if primary else None,
            tier=tier if primary else None,
            reason=None if primary else "non_tier_p_or_incomplete",
        )
        if s["verdict"] == "TRUE" and not primary:
            fabricated += 1
            s["verdict"] = "ARTIFACT"
            s["reason"] = "fabricated_true"
            s["ok"] = False
        if s.get("twin_agree") is False:
            twin_fail += 1
        scored.append(s)

    true_c = sum(1 for s in scored if s["verdict"] == "TRUE")
    false_c = sum(1 for s in scored if s["verdict"] == "FALSE")
    nc_c = sum(1 for s in scored if s["verdict"] == "NOT COMPUTED")
    decidable = true_c + false_c

    if fabricated > 0 or twin_fail > 0:
        label = "O-ARTIFACT"
    elif decidable == 5:
        label = "O-ALL-DECIDED"
    elif decidable >= 1:
        label = "O-CLEAR-X962"
    else:
        label = "O-STILL-IMP-X962"

    control = {
        "fabricated_true_count": fabricated,
        "twin_failures": twin_fail,
        "decidable_count": decidable,
        "true_count": true_c,
        "false_count": false_c,
        "not_computed_count": nc_c,
        "ir10_secondary_used": False,
        "certificate_kind": "none",
    }
    part1 = {
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": HYPOTHESIS_ID,
        "approved_by": APPROVED_BY,
        "prior_instrument": "EXP-BINSTD-178742 Part-1",
        "prior_evidence": "EV-BINSTD-fba851",
        "rows": scored,
        "summary": control,
        "outcome_label": label,
        "certificate": {"kind": "none"},
        "amazon_bedrock": "NOT SELECTED",
    }
    write_json(EXP_ROOT / "stage2" / "part1_rows.json", part1)
    write_json(EXP_ROOT / "stage2" / "control-table.json", control)

    results = "\n".join(
        [
            f"# RESULTS — {EXPERIMENT_ID}",
            "",
            f"Hypothesis: {HYPOTHESIS_ID}",
            f"Approved by: {APPROVED_BY}",
            f"Outcome label: **{label}**",
            "",
            "## Summary",
            "",
            f"- decidable_count: {decidable}",
            f"- true_count: {true_c}",
            f"- false_count: {false_c}",
            f"- not_computed_count: {nc_c}",
            f"- fabricated_true_count: {fabricated}",
            f"- twin_failures: {twin_fail}",
            "",
            "## Scope",
            "",
            "- Provenance / Part-1 k|r-1 census only.",
            "- No Part-2 ranks. No break. No exponent.",
            "- certificate.kind=none.",
            "- Amazon Bedrock not selected.",
            "",
            "## Artifacts",
            "",
            "- stage0/retrieval-protocol-freeze.json",
            "- stage0/preregistered-predictions.json",
            "- stage1/admission_receipt.json",
            "- stage2/part1_rows.json",
            "- stage2/control-table.json",
            "",
        ]
    )
    write_text(EXP_ROOT / "RESULTS.md", results)

    result = {
        "experiment_id": EXPERIMENT_ID,
        "stage": 2,
        "status": "completed",
        "outcome_label": label,
        "summary": control,
        "certificate": {"kind": "none"},
    }
    write_json(run_dir / "raw-result.json", result)
    write_yaml_manifest(
        run_dir / "manifest.yaml",
        {
            "experiment_id": EXPERIMENT_ID,
            "run_stage": 2,
            "status": "completed",
            "validity": "valid",
            "certificate_kind": "none",
            "approved_by": APPROVED_BY,
            "outcome_label": label,
        },
    )
    return result


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", type=int, required=True, choices=[0, 1, 2])
    p.add_argument("--trial-plan", required=True)
    p.add_argument("--run-dir", required=True)
    args = p.parse_args(argv)

    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if args.stage == 0:
        stage0(run_dir)
    elif args.stage == 1:
        stage1(run_dir)
    else:
        stage2(run_dir)
    (run_dir / "stdout.log").write_text(
        f"stage {args.stage} completed in {time.time() - t0:.3f}s\n",
        encoding="utf-8",
    )
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
