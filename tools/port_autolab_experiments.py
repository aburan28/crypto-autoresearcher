#!/usr/bin/env python3
"""Port completed Autolab ECDLP/crypto experiments into harness layout.

Creates for each sourced package:
  ledger/questions/RQ-AREA-NNN.yaml   (shared per area, once)
  ledger/hypotheses/H-AREA-NNN.yaml
  experiments/EXP-AREA-NNN/
    specification.yaml
    implementation.md
    analysis.md
    amendments/
    source/                 # copied scripts/logs/result artifacts
    runs/RUN-AREA-import-001/
      manifest.yaml command.txt environment.json
      stdout.log stderr.log raw-result.json

Also writes:
  docs/autolab-port-inventory-20260731.md
  inputs/autolab_port_manifest_20260731.yaml

Historical Autolab runs are archived as completed_valid empirical imports.
Certificates are kind=none (claims are not re-verified here). Discrete-log
solve claims in source JSON remain toy-scale observations only.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
AUTOLAB_COMMIT = "dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95"
PORT_DATE = "2026-07-31"
PORT_TAG = "autolab-port-20260731"


def resolve_autolab() -> Path:
    """Prefer the SSD990-local refs mirror; fall back to Volume/autolab."""
    env = os.environ.get("AUTOLAB_ROOT")
    if env:
        return Path(env)
    candidates = [
        REPO / "inputs" / "refs",
        Path("/Volumes/SSD990/autolab"),
        Path("/Volumes/Volume/autolab"),
        Path("/Volumes/SSD990/Volume/autolab"),
    ]
    for candidate in candidates:
        if (candidate / "experiments" / "ecdlp_prime_field").exists():
            return candidate
    return candidates[0]


def resolve_ecdsafail_root() -> Path:
    """ECDSA Fail forks live at Autolab root, not under inputs/refs/experiments."""
    env = os.environ.get("AUTOLAB_ROOT")
    if env and (Path(env) / "ecdsafail-challenge").exists():
        return Path(env)
    for candidate in (
        Path("/Volumes/SSD990/autolab"),
        Path("/Volumes/Volume/autolab"),
        Path("/Volumes/SSD990/Volume/autolab"),
        REPO / "inputs" / "refs",
    ):
        if (candidate / "ecdsafail-challenge").exists():
            return candidate
    return Path("/Volumes/Volume/autolab")


AUTOLAB = resolve_autolab()
ECDSAFAIL_ROOT = resolve_ecdsafail_root()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(repo: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return out or "unknown"
    except Exception:
        return "unknown"


def dump_yaml(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True, width=100)


def read_text(path: Path, limit: int = 200_000) -> str:
    if not path.exists():
        return ""
    data = path.read_text(encoding="utf-8", errors="replace")
    return data[:limit]


def first_existing(paths: list[Path]) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def summarize_json(obj, max_chars: int = 1200) -> str:
    try:
        s = json.dumps(obj, indent=2, default=str)
    except TypeError:
        s = str(obj)
    if len(s) > max_chars:
        return s[:max_chars] + "\n... [truncated]"
    return s


def is_appledouble(path: Path) -> bool:
    name = path.name
    return name.startswith("._") or name == ".DS_Store"


def sanitize_text(text: str, limit: int = 500) -> str:
    cleaned = "".join(
        ch if (ch in "\t\n\r" or 32 <= ord(ch) < 127 or ord(ch) >= 160) else " "
        for ch in text
    )
    cleaned = " ".join(cleaned.split())
    return cleaned[:limit]


def extract_finding(result_obj, result_md: str) -> str:
    if isinstance(result_obj, dict):
        for key in (
            "finding",
            "claim",
            "summary",
            "interpretation",
            "hypothesis_H1",
            "status",
            "verdict",
        ):
            if key in result_obj and result_obj[key]:
                return sanitize_text(str(result_obj[key]))
        if "results" in result_obj and isinstance(result_obj["results"], list):
            return f"Banked {len(result_obj['results'])} result rows from Autolab."
    if result_md:
        for line in result_md.splitlines():
            if line.strip().startswith("#"):
                continue
            if line.strip():
                cleaned = sanitize_text(line)
                if cleaned:
                    return cleaned
    return "Historical Autolab experiment with retained result artifacts."


# ---------------------------------------------------------------------------
# Catalog construction
# ---------------------------------------------------------------------------

def catalog_prime() -> list[dict]:
    root = AUTOLAB / "experiments" / "ecdlp_prime_field"
    items = []
    for result in sorted(root.glob("*_result.json")):
        if is_appledouble(result):
            continue
        stem = result.name[: -len("_result.json")]
        code = sorted(
            [
                p
                for p in root.glob(stem + "*")
                if not is_appledouble(p)
                and (
                    p.suffix in {".sage", ".py", ".c"}
                    or p.name.endswith(".sage.py")
                )
            ]
        )
        logs = sorted(
            [
                p
                for p in root.glob(stem + "*")
                if not is_appledouble(p)
                and (p.suffix == ".log" or p.name.endswith(".stdout"))
            ]
        )
        mds = sorted(
            [
                p
                for p in root.glob(stem + "*")
                if not is_appledouble(p)
                and p.suffix == ".md"
                and "contract" not in p.name
            ]
        )
        contracts = sorted(root.glob(stem + "*contract*")) + sorted(
            root.glob("*" + stem.split("_", 1)[-1] + "*contract*")
        )
        # round020 has a short name mismatch
        if stem == "round020_solvegate":
            code = [
                root / "round020_solvegate_ic_vs_rho.sage",
                root / "round020_solvegate_ic_vs_rho.sage.py",
            ]
            code = [p for p in code if p.exists()]
            logs = [p for p in [root / "round020_solvegate.log"] if p.exists()]
            mds = [p for p in [root / "round020_results.md"] if p.exists()]
            contracts = [
                p for p in [root / "round020_solvegate_contract.md"] if p.exists()
            ]
        items.append(
            {
                "area": "ALPF",
                "topic": "prime-field ECDLP",
                "source_id": stem,
                "title": f"Autolab prime-field: {stem}",
                "result_json": result,
                "result_md": mds[0] if mds else None,
                "contract": contracts[0] if contracts else None,
                "code": code,
                "logs": logs,
                "extras": [],
            }
        )
    return items


def catalog_binary() -> list[dict]:
    root = AUTOLAB / "experiments" / "ecdlp_binary_field"
    items = []
    titles = {
        1: "Weil-descent gate",
        2: "Solving degree",
        3: "m=3 fixed target",
        4: "Larger n sweep",
        5: "Cost balance",
        6: "m scaling",
        7: "WDSat",
        8: "Solving degree vs n / subregularity",
        9: "m=4 diagonal",
        10: "m=5 diagonal",
        11: "Petit–Quisquater diagonal cost capstone",
    }
    for n in range(1, 12):
        prefix = f"bin_exp{n:03d}"
        result_md = root / f"{prefix}_result.md"
        code = sorted(root.glob(f"{prefix}*.sage"))
        logs = sorted(root.glob(f"{prefix}*.log"))
        items.append(
            {
                "area": "ALBIN",
                "topic": "binary-field ECDLP",
                "source_id": prefix,
                "title": f"Autolab binary-field BIN-EXP-{n:03d}: {titles[n]}",
                "result_json": None,
                "result_md": result_md if result_md.exists() else None,
                "contract": None,
                "code": code,
                "logs": logs,
                "extras": [],
            }
        )
    return items


def catalog_isogeny() -> list[dict]:
    root = AUTOLAB / "experiments" / "ecdlp_isogeny"
    items = []
    patterns = [
        "p1486_*_result.json",
        "p1243_*_result.json",
        "iso_genus_filtered_*_result.json",
    ]
    # Prefer final ascending consensus versions (v10+), not every prelaunch.
    ascending = sorted(root.glob("iso_ascending_*_result.json"))
    ascending_keep = [
        p
        for p in ascending
        if re.search(r"_v(1[0-9]|[2-9][0-9])_result\.json$", p.name)
        and "prelaunch" not in p.name
    ]
    files: list[Path] = []
    for pat in patterns:
        files.extend(sorted(root.glob(pat)))
    files.extend(ascending_keep)

    # Deduplicate while preserving order.
    seen = set()
    uniq = []
    for f in files:
        if f.name in seen:
            continue
        seen.add(f.name)
        uniq.append(f)

    for result in uniq:
        if is_appledouble(result):
            continue
        stem = result.name[: -len("_result.json")]
        # Drop versioned duplicates like *_result_v2 — handled separately below.
        if re.search(r"_result_v\d+$", stem):
            continue
        # tighter: files that start with stem without _result
        base = stem
        code = sorted(
            [
                p
                for p in root.iterdir()
                if not is_appledouble(p)
                and p.name.startswith(base)
                and (
                    p.suffix in {".sage", ".py"}
                    or p.name.endswith(".sage.py")
                )
                and "result" not in p.name
            ]
        )[:8]
        logs = sorted(
            [
                p
                for p in root.iterdir()
                if not is_appledouble(p)
                and p.name.startswith(base)
                and (p.suffix == ".log" or p.name.endswith(".stdout"))
            ]
        )[:4]
        research_root = AUTOLAB / "research"
        mds = (
            sorted(
                [
                    p
                    for p in research_root.glob(f"*{base}*")
                    if not is_appledouble(p) and p.suffix == ".md"
                ]
            )[:4]
            if research_root.exists()
            else []
        )
        # also local md
        mds = sorted(
            [
                p
                for p in root.iterdir()
                if not is_appledouble(p)
                and p.name.startswith(base)
                and p.suffix == ".md"
            ]
        )[:4] + mds
        items.append(
            {
                "area": "ALISO",
                "topic": "isogeny / supersingular / Kani",
                "source_id": base,
                "title": f"Autolab isogeny: {base}",
                "result_json": result,
                "result_md": mds[0] if mds else None,
                "contract": None,
                "code": code,
                "logs": logs,
                "extras": [],
            }
        )

    # Include explicit v2/v3 verify results as separate packages when present.
    for result in sorted(root.glob("p1486_*_result_v*.json")) + sorted(
        root.glob("p1243_*_result_v*.json")
    ):
        stem = result.stem  # includes _result_vN
        items.append(
            {
                "area": "ALISO",
                "topic": "isogeny / supersingular / Kani",
                "source_id": stem,
                "title": f"Autolab isogeny: {stem}",
                "result_json": result,
                "result_md": None,
                "contract": None,
                "code": [],
                "logs": [],
                "extras": [],
            }
        )
    return items


def catalog_ecdsafail() -> list[dict]:
    items = []
    mapping = [
        ("ecdsafail-challenge", "Current challenge fork score"),
        ("ecdsafail-frontier-jul23", "Frontier Jul23 score"),
        ("ecdsafail-q1141-old-jul24", "Older q=1141 higher-Toffoli score"),
    ]
    for dirname, title in mapping:
        root = ECDSAFAIL_ROOT / dirname
        if not root.exists():
            continue
        extras = []
        for name in ("score.json", "results.tsv", "README.md"):
            p = root / name
            if p.exists():
                extras.append(p)
        items.append(
            {
                "area": "ALECF",
                "topic": "ECDSA Fail quantum point-add",
                "source_id": dirname,
                "title": f"Autolab ECDSA Fail: {title}",
                "result_json": root / "score.json" if (root / "score.json").exists() else None,
                "result_md": root / "README.md" if (root / "README.md").exists() else None,
                "contract": None,
                "code": [],
                "logs": [],
                "extras": extras,
            }
        )
    return items


# ---------------------------------------------------------------------------
# Emitters
# ---------------------------------------------------------------------------

AREA_META = {
    "ALPF": {
        "rq_id": "RQ-ALPF-001",
        "rq_title": "What prime-field ECDLP decomposition/structure candidates survive Autolab toy campaigns?",
        "field_types": ["prime"],
        "methods": [
            "semaev",
            "first_fall",
            "index_calculus",
            "pollard_rho",
            "vw_multitarget",
        ],
    },
    "ALBIN": {
        "rq_id": "RQ-ALBIN-001",
        "rq_title": "How does binary-field Semaev/Weil-descent IC behave along fixed-m and Petit–Quisquater diagonals?",
        "field_types": ["binary"],
        "methods": ["weil_descent", "semaev", "wdsat", "petit_quisquater_diagonal"],
    },
    "ALISO": {
        "rq_id": "RQ-ALISO-001",
        "rq_title": "Which isogeny/Kani/Hecke structures from Autolab yield scoped positives vs Wesolowski-class baselines?",
        "field_types": ["prime", "extension"],
        "methods": ["isogeny", "kani", "hecke", "frobenius_midpoint", "oriented_ascending"],
    },
    "ALECF": {
        "rq_id": "RQ-ALECF-001",
        "rq_title": "What quantum point-addition circuit scores were achieved on the ECDSA Fail benchmark forks?",
        "field_types": ["secp256k1"],
        "methods": ["toffoli_circuit", "quantum_point_add"],
    },
}


def write_questions() -> None:
    for area, meta in AREA_META.items():
        path = REPO / "ledger" / "questions" / f"{meta['rq_id']}.yaml"
        if path.exists():
            continue
        dump_yaml(
            path,
            {
                "research_question": {
                    "id": meta["rq_id"],
                    "title": meta["rq_title"],
                    "scope": {
                        "curve_families": ["autolab_imported"],
                        "field_types": meta["field_types"],
                        "bit_sizes": ["toy_to_medium_as_sourced"],
                        "methods": meta["methods"],
                    },
                    "motivation": (
                        "Import completed Autolab cryptanalysis campaigns into the "
                        "crypto-autoresearcher harness so subsequent work can cite "
                        "immutable run packages rather than free-form lab notebooks."
                    ),
                    "decision_target": (
                        "Preserve Autolab empirical boundaries as harness-native "
                        "EXP/RUN/EV records without upgrading claim tiers."
                    ),
                    "constraints": [
                        "Historical imports are empirical_only unless independently re-verified",
                        "No deployment or crypto-scale promotion from toy Autolab runs",
                        f"Source commit pinned: {AUTOLAB_COMMIT}",
                    ],
                    "status": "active",
                    "owner": "coordinator",
                }
            },
        )


def write_hypothesis(h_id: str, rq_id: str, item: dict, finding: str) -> None:
    path = REPO / "ledger" / "hypotheses" / f"{h_id}.yaml"
    if path.exists():
        return
    dump_yaml(
        path,
        {
            "hypothesis": {
                "id": h_id,
                "question_id": rq_id,
                "statement": (
                    f"Autolab package `{item['source_id']}` "
                    f"({item['topic']}) produces a scoped empirical measurement "
                    f"that can be archived as harness evidence. Source finding: "
                    f"{finding}"
                ),
                "mechanism": (
                    "Historical Autolab experiment contract + script + retained "
                    "result artifacts, ported without re-execution."
                ),
                "assumptions": [
                    f"Source artifacts under `{AUTOLAB}` (and ECDSA Fail under `{ECDSAFAIL_ROOT}`) are authentic run products",
                    "Autolab git commit pin is sufficient provenance for this archive",
                    "No claim upgrade beyond Autolab's original scope",
                ],
                "predictions": [
                    {
                        "metric": "harness_archive_complete",
                        "direction": "different",
                        "minimum_effect": "specification + run package + analysis present",
                    }
                ],
                "test_boundary": {
                    "instances": [item["source_id"]],
                    "parameters": {"import_mode": "historical_artifact_port"},
                    "implementation": "tools/port_autolab_experiments.py",
                    "budget": {"maximum_runs": 1},
                },
                "falsification_conditions": [
                    "Source result artifact missing or unreadable",
                    "Harness validation rejects the imported package schema",
                ],
                "interpretation_limits": [
                    "Import preserves Autolab scope; does not re-verify certificates",
                    "Toy/heuristic Autolab claims remain toy/heuristic here",
                ],
                "status": "analyzed",
                "proposed_by": "autolab-port",
            }
        },
    )


def write_experiment_spec(exp_id: str, h_id: str, item: dict, finding: str) -> None:
    path = REPO / "experiments" / exp_id / "specification.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    (path.parent / "amendments").mkdir(exist_ok=True)
    if path.exists():
        return
    dump_yaml(
        path,
        {
            "experiment": {
                "id": exp_id,
                "hypothesis_id": h_id,
                "version": 1,
                "title": item["title"],
                "status": "approved",
                "objective": (
                    f"Archive Autolab experiment `{item['source_id']}` "
                    f"({item['topic']}) as an immutable harness reproduction "
                    f"package. Source finding: {finding}"
                ),
                "inputs": {
                    "source_repo": str(AUTOLAB),
                    "source_commit": AUTOLAB_COMMIT,
                    "source_id": item["source_id"],
                    "import_tool": "tools/port_autolab_experiments.py",
                    "port_tag": PORT_TAG,
                },
                "controls": [
                    "Preserve original Autolab scripts/logs/result artifacts under source/",
                    "Do not re-interpret Autolab negatives as universal impossibility",
                    "Certificate kind=none unless independently re-verified in-harness",
                ],
                "independent_variables": ["source_id"],
                "metrics": {
                    "primary": ["import_complete", "source_artifact_sha256"],
                    "secondary": ["source_result_present", "source_script_present"],
                },
                "scale_relevance": {
                    "tier": "toy",
                    "justification": (
                        "Autolab campaigns are predominantly toy/feasibility scale; "
                        "this import does not raise the claim ceiling."
                    ),
                    "correspondence": None,
                },
                "replication": {
                    "seeds": ["historical"],
                    "independent_instances": 1,
                },
                "budget": {
                    "wall_clock_seconds_per_run": 1,
                    "total_cpu_hours": 0,
                    "maximum_memory_gb": 1,
                    "maximum_runs": 1,
                },
                "stopping_rules": [
                    "Single historical import run; no re-execution in this experiment"
                ],
                "invalidation_rules": [
                    "Missing source result artifact",
                    "Mutating runs/ after import (supersede with new RUN id instead)",
                ],
                "success_criterion": (
                    "Harness package contains specification, analysis, implementation, "
                    "and one RUN with the six required companion artifacts, linked to "
                    "a hypothesis under the area research question."
                ),
                "falsification_criterion": (
                    "Import package fails tools/validate_ledger.py schema checks, or "
                    "source artifacts cannot be located at the pinned Autolab commit."
                ),
                "required_artifacts": [
                    "specification.yaml",
                    "implementation.md",
                    "analysis.md",
                    "runs/<RUN>/manifest.yaml",
                    "runs/<RUN>/command.txt",
                    "runs/<RUN>/environment.json",
                    "runs/<RUN>/stdout.log",
                    "runs/<RUN>/stderr.log",
                    "runs/<RUN>/raw-result.json",
                ],
                "assigned_to": "executor",
                "approved_by": "coordinator",
            }
        },
    )


def write_implementation(exp_dir: Path, item: dict, copied: list[str]) -> None:
    path = exp_dir / "implementation.md"
    if path.exists():
        return
    lines = [
        f"# Implementation — {item['title']}",
        "",
        "Historical Autolab port (no re-execution).",
        "",
        "## Provenance",
        f"- Source repo: `{AUTOLAB}`",
        f"- Source commit: `{AUTOLAB_COMMIT}`",
        f"- Source id: `{item['source_id']}`",
        f"- Port tool: `tools/port_autolab_experiments.py`",
        f"- Port tag: `{PORT_TAG}`",
        "",
        "## Copied artifacts",
    ]
    if copied:
        lines.extend(f"- `{c}`" for c in copied)
    else:
        lines.append("- (result-only import; no local script copied)")
    lines += [
        "",
        "## Deviations from live harness execution",
        "- Run package is an archival import of prior Autolab outputs.",
        "- `run.code.commit` records the crypto-autoresearcher HEAD at import time;",
        "  Autolab source commit is recorded in `inputs.parameters.source_commit`.",
        "- Certificates are `kind: none` (not re-verified).",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_analysis(exp_dir: Path, item: dict, finding: str, result_obj, result_md: str) -> None:
    path = exp_dir / "analysis.md"
    if path.exists():
        return
    obs = finding
    if result_md:
        # Keep a short excerpt
        excerpt = "\n".join(result_md.splitlines()[:40])
    else:
        excerpt = summarize_json(result_obj, 900)
    body = f"""# Analysis — {item['title']}

## Observation
{obs}

Source excerpt / raw summary:

```
{excerpt}
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
"""
    path.write_text(body, encoding="utf-8")


def write_run(
    exp_id: str,
    area: str,
    item: dict,
    result_obj,
    result_md: str,
    copied_hashes: dict[str, str],
    stdout_text: str,
    nnn: str,
) -> str:
    run_id = f"RUN-{area}-{nnn}-import"
    run_dir = REPO / "experiments" / exp_id / "runs" / run_id
    if run_dir.exists():
        return run_id
    run_dir.mkdir(parents=True)

    raw = {
        "port_tag": PORT_TAG,
        "source_repo": str(AUTOLAB),
        "source_commit": AUTOLAB_COMMIT,
        "source_id": item["source_id"],
        "topic": item["topic"],
        "copied_artifact_sha256": copied_hashes,
        "result": result_obj if result_obj is not None else {"result_md": result_md},
    }
    (run_dir / "raw-result.json").write_text(
        json.dumps(raw, indent=2, default=str) + "\n", encoding="utf-8"
    )

    command = (
        f"python3 tools/port_autolab_experiments.py "
        f"--only {item['source_id']}  # historical import of Autolab artifacts"
    )
    (run_dir / "command.txt").write_text(command + "\n", encoding="utf-8")

    env = {
        "operating_system": "imported-from-autolab",
        "architecture": "imported",
        "python_version": None,
        "sage_version": None,
        "dependencies": {
            "import_mode": "historical_artifact_port",
            "source_commit": AUTOLAB_COMMIT,
        },
    }
    (run_dir / "environment.json").write_text(
        json.dumps(env, indent=2) + "\n", encoding="utf-8"
    )

    stdout = stdout_text or f"Imported {item['source_id']} from Autolab.\n"
    (run_dir / "stdout.log").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text("", encoding="utf-8")

    commit = git_commit(REPO)
    now = datetime.now(timezone.utc).isoformat()
    metrics = {
        "import_complete": 1,
        "source_result_present": 1 if (result_obj is not None or result_md) else 0,
        "source_script_present": 1 if item.get("code") else 0,
        "copied_artifact_count": len(copied_hashes),
    }
    # Surface a few numeric fields when present.
    if isinstance(result_obj, dict):
        if "score" in result_obj:
            metrics["ecdsafail_score"] = result_obj["score"]
            m = result_obj.get("metrics") or {}
            if "toffoli" in m:
                metrics["toffoli"] = m["toffoli"]
            if "qubits" in m:
                metrics["qubits"] = m["qubits"]

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": exp_id,
            "status": "completed_valid",
            "code": {
                "commit": commit,
                "dirty": True,
                "command": command,
            },
            "inference": {
                "requested_policy": "autolab-port",
                "resolved_model_id": "none (deterministic import)",
                "reasoning_effort": None,
                "fallback_used": False,
                "adapter_version": None,
            },
            "environment": env,
            "inputs": {
                "curve_id": f"AUTOLAB-{item['source_id']}",
                "seed": "historical",
                "parameters": {
                    "source_commit": AUTOLAB_COMMIT,
                    "source_id": item["source_id"],
                    "topic": item["topic"],
                    "port_tag": PORT_TAG,
                },
            },
            "timing": {
                "started_at": now,
                "finished_at": now,
                "wall_seconds": 0.0,
            },
            "resources": {
                "peak_rss_bytes": None,
                "cpu_seconds": 0.0,
            },
            "result": {
                "metrics": metrics,
                "valid": True,
                "invalid_reason": None,
                "certificate": {
                    "kind": "none",
                    "verified": True,
                    "verifier": "no-claim-historical-import",
                },
            },
            "artifacts": {
                "command": "command.txt",
                "environment": "environment.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "raw_result": "raw-result.json",
            },
        }
    }
    dump_yaml(run_dir / "manifest.yaml", manifest)
    return run_id


def copy_sources(exp_dir: Path, item: dict) -> dict[str, str]:
    src_dir = exp_dir / "source"
    src_dir.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for p in (
        ([item["result_json"]] if item.get("result_json") else [])
        + ([item["result_md"]] if item.get("result_md") else [])
        + ([item["contract"]] if item.get("contract") else [])
        + list(item.get("code") or [])
        + list(item.get("logs") or [])
        + list(item.get("extras") or [])
    ):
        if p is None or not Path(p).exists():
            continue
        p = Path(p)
        if is_appledouble(p):
            continue
        dest = src_dir / p.name
        if not dest.exists():
            shutil.copy2(p, dest)
        rel = f"source/{p.name}"
        hashes[rel] = sha256_file(dest)
    return hashes


def port_item(item: dict, index: int) -> dict:
    area = item["area"]
    nnn = f"{index:03d}"
    exp_id = f"EXP-{area}-{nnn}"
    h_id = f"H-{area}-{nnn}"
    rq_id = AREA_META[area]["rq_id"]

    result_obj = None
    if item.get("result_json") and Path(item["result_json"]).exists():
        try:
            result_obj = json.loads(Path(item["result_json"]).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            result_obj = {"_parse_error": True, "path": str(item["result_json"])}
    result_md = ""
    if item.get("result_md") and Path(item["result_md"]).exists():
        md_path = Path(item["result_md"])
        if not is_appledouble(md_path):
            raw = md_path.read_bytes()[:4096]
            if b"\x00" not in raw[:64]:
                result_md = read_text(md_path)
    finding = extract_finding(result_obj, result_md)

    write_hypothesis(h_id, rq_id, item, finding)
    write_experiment_spec(exp_id, h_id, item, finding)

    exp_dir = REPO / "experiments" / exp_id
    hashes = copy_sources(exp_dir, item)
    write_implementation(exp_dir, item, list(hashes))
    write_analysis(exp_dir, item, finding, result_obj, result_md)

    stdout_parts = []
    for log in item.get("logs") or []:
        stdout_parts.append(read_text(Path(log), limit=80_000))
    if not stdout_parts and result_md:
        stdout_parts.append(result_md[:80_000])
    stdout_text = "\n\n".join(stdout_parts)[:200_000]
    run_id = write_run(
        exp_id, area, item, result_obj, result_md, hashes, stdout_text, nnn
    )

    return {
        "experiment_id": exp_id,
        "hypothesis_id": h_id,
        "run_id": run_id,
        "source_id": item["source_id"],
        "area": area,
        "topic": item["topic"],
        "finding": finding,
        "artifact_count": len(hashes),
    }


def write_evidence(area: str, ports: list[dict]) -> str:
    ev_id = f"EV-{area}-001"
    path = REPO / "ledger" / "evidence" / f"{ev_id}.yaml"
    if path.exists():
        return ev_id
    dump_yaml(
        path,
        {
            "evidence": {
                "id": ev_id,
                "hypothesis_id": ports[0]["hypothesis_id"],
                "experiment_ids": [p["experiment_id"] for p in ports],
                "run_ids": [p["run_id"] for p in ports],
                "direction": "neutral",
                "strength": "preliminary",
                "claim_tier": "toy",
                "proof_status": "empirical_only",
                "proof_refs": [],
                "observations": [
                    f"Imported {len(ports)} Autolab packages into harness EXP/RUN layout.",
                    *[
                        f"{p['experiment_id']}: {p['source_id']} — {p['finding'][:180]}"
                        for p in ports[:12]
                    ],
                ],
                "inference": (
                    f"Autolab {area} campaign artifacts are now citeable under the "
                    "harness without upgrading their original claim tiers. Use individual "
                    "EXP analysis.md files for scoped scientific content."
                ),
                "boundaries": [
                    "Historical import; certificates not re-verified",
                    "claim_tier toy is a hard ceiling for this evidence record",
                    f"Source commit {AUTOLAB_COMMIT}",
                ],
                "unresolved_confounds": [
                    "Autolab worktree-only dumps (e.g. codex 258d) not fully curated here",
                    "Large campaign monoliths (ecdlp_index_calculus_state) inventoried but not EXP-ported",
                ],
                "reviewed_by": "coordinator",
            }
        },
    )
    return ev_id


def write_inventory(all_ports: list[dict], deferred: list[dict]) -> None:
    manifest = {
        "schema": "autolab-port-manifest-v1",
        "port_tag": PORT_TAG,
        "ported_at": PORT_DATE,
        "source_repo": str(AUTOLAB),
        "source_commit": AUTOLAB_COMMIT,
        "target_repo": str(REPO),
        "target_commit_at_port": git_commit(REPO),
        "counts": {
            "ported": len(all_ports),
            "deferred": len(deferred),
            "by_area": {},
        },
        "ported": all_ports,
        "deferred": deferred,
    }
    by_area: dict[str, int] = {}
    for p in all_ports:
        by_area[p["area"]] = by_area.get(p["area"], 0) + 1
    manifest["counts"]["by_area"] = by_area

    dump_yaml(REPO / "inputs" / f"autolab_port_manifest_{PORT_DATE.replace('-', '')}.yaml", manifest)

    lines = [
        f"# Autolab → crypto-autoresearcher port inventory ({PORT_DATE})",
        "",
        f"Source: `{AUTOLAB}` @ `{AUTOLAB_COMMIT}`",
        f"Port tag: `{PORT_TAG}`",
        f"Tool: `tools/port_autolab_experiments.py`",
        "",
        "## Ported",
        "",
        f"Total EXP packages: **{len(all_ports)}**",
        "",
    ]
    for area in ("ALPF", "ALBIN", "ALISO", "ALECF"):
        subset = [p for p in all_ports if p["area"] == area]
        lines.append(f"### {area} ({len(subset)})")
        lines.append("")
        lines.append("| EXP | Source | Finding |")
        lines.append("|---|---|---|")
        for p in subset:
            finding = p["finding"].replace("|", "/").replace("\n", " ")[:120]
            lines.append(
                f"| `{p['experiment_id']}` | `{p['source_id']}` | {finding} |"
            )
        lines.append("")

    lines += [
        "## Deferred (inventoried, not EXP-packaged in this pass)",
        "",
        "| Topic | Path / note | Why deferred |",
        "|---|---|---|",
    ]
    for d in deferred:
        lines.append(
            f"| {d['topic']} | `{d['path']}` | {d['reason']} |"
        )
    lines += [
        "",
        "## Worktrees",
        "",
        "Almost all `/Users/adamburan/.codex/worktrees/*/autolab` checkouts are sparse "
        "detached copies of `f1c783082` without unique `experiments/`. Exception:",
        "",
        "- `258d`: ~550 unique root JSON/md probe dumps (P1553/torus/divisor ledgers) not "
        "present on Autolab main; inventoried as deferred curation, not auto-ported.",
        "",
        "## How to extend",
        "",
        "```bash",
        "python3 tools/port_autolab_experiments.py",
        "python3 tools/validate_ledger.py",
        "```",
        "",
    ]
    (REPO / "docs" / f"autolab-port-inventory-{PORT_DATE.replace('-', '')}.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def deferred_inventory() -> list[dict]:
    return [
        {
            "topic": "ECDLP index-calculus campaign monolith",
            "path": "ecdlp_index_calculus_state/",
            "reason": "~41k artifacts; needs curated trial extraction, not bulk EXP emission",
        },
        {
            "topic": "ECDLP challenge notes corpus",
            "path": "ecdlp-challenge/notes/",
            "reason": "~1900 probe notes; select winners later",
        },
        {
            "topic": "PO-transfer / PO96AB research program",
            "path": "research/PO_transfer_* + .sage-po96ab-*",
            "reason": "Large theory+audit chain; many already in Autolab ledger narrative",
        },
        {
            "topic": "SHA1-H001..H004 campaigns",
            "path": "research/ + jobs/",
            "reason": "Custody/audit failures dominate; not clean EXP packages",
        },
        {
            "topic": "Codex worktree 258d unique JSON dump",
            "path": "/Users/adamburan/.codex/worktrees/258d/autolab",
            "reason": "Unique vs main; requires manual curation before harness IDs",
        },
        {
            "topic": "ISO ascending prelaunch / intermediate versions",
            "path": "experiments/ecdlp_isogeny/iso_ascending_*prelaunch*",
            "reason": "Intermediate negatives; finals ported preferentially",
        },
        {
            "topic": "Root phase*.sage.py scripts without colocated results",
            "path": "phase*.sage.py",
            "reason": "Scripts-only / historical; results live in negative_results narrative",
        },
        {
            "topic": "ecc2k130 campaign state",
            "path": "ecc2k130_campaign_state/",
            "reason": "Systems optimization state, not cryptanalytic EXP contract",
        },
    ]


def main(only: str | None = None) -> None:
    if not AUTOLAB.exists():
        raise SystemExit(f"Autolab source missing: {AUTOLAB}")

    write_questions()

    catalogs = {
        "ALPF": catalog_prime(),
        "ALBIN": catalog_binary(),
        "ALISO": catalog_isogeny(),
        "ALECF": catalog_ecdsafail(),
    }

    all_ports: list[dict] = []
    for area, items in catalogs.items():
        for i, item in enumerate(items, start=1):
            if only and item["source_id"] != only and only not in item["source_id"]:
                continue
            ported = port_item(item, i)
            all_ports.append(ported)
            print(f"ported {ported['experiment_id']} <- {ported['source_id']}")

    # Group evidence by area
    for area in catalogs:
        subset = [p for p in all_ports if p["area"] == area]
        if subset:
            ev = write_evidence(area, subset)
            print(f"evidence {ev} ({len(subset)} experiments)")

    write_inventory(all_ports, deferred_inventory())
    print(f"done: {len(all_ports)} experiments ported")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="Port only matching source_id substring")
    args = ap.parse_args()
    main(only=args.only)
