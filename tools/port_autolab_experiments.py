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

Two modes need no Autolab checkout and work from a fresh clone:

  --verify     recompute every ported package's artifact list, artifact count
               and per-file sha256 from the files it actually ships, and check
               them against implementation.md, manifest.yaml, raw-result.json
               and the port manifest. Exits 1 on any mismatch.
  --reconcile  with --verify, first rewrite those derived fields (and any
               degenerate finding text) to match the archive. Never touches an
               archived source artifact.

Porting itself needs the source tree, via $AUTOLAB_ROOT or a local checkout;
it refuses to run against a partial one rather than emit a partial port.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
AUTOLAB_COMMIT = "dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95"
PORT_DATE = "2026-07-31"
PORT_TAG = "autolab-port-20260731"


AUTOLAB_CANDIDATES = (
    Path("/Volumes/SSD990/autolab"),
    Path("/Volumes/Volume/autolab"),
    Path("/Volumes/SSD990/Volume/autolab"),
)


def has_portable_content(root: Path) -> bool:
    """Does this root hold result artifacts, or only the docs mirror?

    `inputs/refs` satisfies a bare "does experiments/ecdlp_prime_field exist"
    probe while holding no `*_result.json` at all, so that probe silently
    selected an empty source and the port emitted records whose `source_repo`
    disagreed with the packages it had already written.
    """
    prime = root / "experiments" / "ecdlp_prime_field"
    return prime.is_dir() and any(prime.glob("*_result.json"))


def resolve_autolab() -> Path:
    """The Autolab checkout to port from. $AUTOLAB_ROOT wins when set."""
    env = os.environ.get("AUTOLAB_ROOT")
    if env:
        return Path(env)
    for candidate in (REPO / "inputs" / "refs", *AUTOLAB_CANDIDATES):
        if has_portable_content(candidate):
            return candidate
    return AUTOLAB_CANDIDATES[0]


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


# Fallback for the ignore test when git is unavailable. Kept deliberately
# narrow: it only has to cover patterns that can match a *copied artifact*,
# and tests/test_port_autolab_experiments.py asserts these stay a subset of
# the real .gitignore.
_FALLBACK_IGNORED = ("*.sage.py", "._*", ".DS_Store", "*.pyc", "*.pkl", "*.raw",
                     "*.so", "*.dylib")


def _git_ignores(paths: list[Path]) -> set[Path]:
    """Which of `paths` would .gitignore keep out of the repo?

    An artifact that git refuses to track cannot be archived, so it must not
    appear in any provenance record either. Asking git directly keeps this in
    sync with .gitignore instead of duplicating its rules here.
    """
    if not paths:
        return set()
    try:
        proc = subprocess.run(
            ["git", "check-ignore", "--stdin"],
            cwd=REPO,
            input="\n".join(str(p) for p in paths),
            capture_output=True,
            text=True,
        )
        # 0 = some ignored, 1 = none ignored; anything else means git could
        # not answer and we must not treat silence as "nothing is ignored".
        if proc.returncode in (0, 1):
            return {Path(line) for line in proc.stdout.splitlines() if line}
    except (OSError, subprocess.SubprocessError):
        pass
    return {p for p in paths if any(fnmatch(p.name, pat) for pat in _FALLBACK_IGNORED)}


def archivable(src_dir: Path, candidates: list[Path]) -> list[Path]:
    """Source files that will actually survive into the committed archive.

    Provenance records are written from this list, so a file dropped here is
    a file no record claims. The alternative -- recording what was copied on
    the porting machine -- produces manifests that cite artifacts a reader
    cannot find.
    """
    kept, dests = [], []
    for p in candidates:
        if p is None:
            continue
        p = Path(p)
        if not p.exists() or is_appledouble(p):
            continue
        kept.append(p)
        dests.append(src_dir / p.name)
    ignored = _git_ignores(dests)
    return [p for p, d in zip(kept, dests) if d not in ignored]


def sanitize_text(text: str, limit: int = 500) -> str:
    cleaned = "".join(
        ch if (ch in "\t\n\r" or 32 <= ord(ch) < 127 or ord(ch) >= 160) else " "
        for ch in text
    )
    cleaned = " ".join(cleaned.split())
    return cleaned[:limit]


# Values that answer "did it pass?" but state no finding. Copying one into a
# hypothesis statement yields "Source finding: failed", which reads as a
# scientific result and is not one.
_STATUS_TOKENS = {
    "failed", "fail", "survived", "passed", "pass", "ok", "done", "error",
    "inconclusive", "unknown", "n/a", "none", "null", "true", "false",
    "complete", "completed", "success", "aborted", "skipped",
}

# Ordered by how much interpretation the source author put into the field:
# a written verdict beats a machine status flag.
# `hypothesis*` sits last on purpose: it states what was tested, not what was
# found, so it is only a fallback when the source recorded no verdict at all.
_NARRATIVE_KEYS = ("finding", "claim", "claim_status", "summary",
                   "interpretation", "verdict", "verdict_reason", "conclusion",
                   "category", "hypothesis_H1", "hypothesis")


# Run bookkeeping. A line made only of these answers "which run was it?", not
# "what was found?", and several result files open with exactly such a header.
_METADATA_KEYS = {
    "date", "seed", "seed base", "script", "scripts", "log", "logs", "solver",
    "time", "timestamp", "commit", "runtime", "host", "rc", "author", "m",
    "experiment", "round", "duration",
}


def _labelled_keys(text: str) -> list[str]:
    keys = re.findall(r"\*\*\s*([^:*]{1,20}?)\s*:\*\*", text)
    if not keys:
        keys = re.findall(r"(?:^|[.;]\s+)([A-Z][A-Za-z ]{0,18}?):\s", text)
    return [k.strip().lower() for k in keys]


def _is_metadata_line(text: str) -> bool:
    keys = _labelled_keys(text)
    return bool(keys) and all(k in _METADATA_KEYS for k in keys)


def _is_narrative(text: str) -> bool:
    """Does this read as a stated finding rather than a status flag?"""
    stripped = text.strip().strip(".").strip()
    if not stripped or stripped.lower() in _STATUS_TOKENS:
        return False
    # A serialized container is data, not prose: it must never be presented
    # as the source's finding.
    if stripped[0] in "{[" or stripped.startswith("OrderedDict"):
        return False
    if _is_metadata_line(stripped):
        return False
    return len(stripped.split()) >= 3


def extract_finding(result_obj, result_md: str) -> str:
    """A one-line finding for the derived records, or an honest statement that
    the source recorded none.

    Never dresses a status flag or a serialized dict up as a result: the text
    this returns is copied verbatim into a hypothesis statement, an experiment
    objective and the inventory table.
    """
    status_note = ""
    if isinstance(result_obj, dict):
        for key in _NARRATIVE_KEYS:
            value = result_obj.get(key)
            if isinstance(value, str) and _is_narrative(sanitize_text(value)):
                return sanitize_text(value)
        for key in ("status", "verdict", "outcome"):
            value = result_obj.get(key)
            if isinstance(value, (str, bool)):
                token = sanitize_text(str(value))
                if token:
                    status_note = (
                        f"Source recorded outcome flag `{token}` and no narrative "
                        f"finding; see source/ artifacts for the scoped reading."
                    )
                    break

    if result_md:
        for line in result_md.splitlines():
            if line.strip().startswith("#"):
                continue
            cleaned = sanitize_text(line)
            if cleaned and _is_narrative(cleaned):
                return cleaned

    if status_note:
        return status_note

    if isinstance(result_obj, dict):
        if isinstance(result_obj.get("results"), list):
            return (
                f"No narrative finding recorded; source result artifact banks "
                f"{len(result_obj['results'])} result rows."
            )
        keys = ", ".join(sorted(str(k) for k in result_obj)[:8])
        if keys:
            return (
                f"No narrative finding recorded; source result artifact carries "
                f"fields: {keys}."
            )
    return "No narrative finding recorded in the source result artifacts."


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
    if not root.is_dir():
        return items
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
No baseline was computed for this record. Whatever baseline Autolab used stays in the
`source/` artifacts under its own assumptions; this import neither recomputes it nor
restates it, so nothing here may be read as a measured margin over rho, VW, or a
Wesolowski-class isogeny cost.

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
    metrics = archive_metrics(copied_hashes)
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


def candidate_sources(item: dict) -> list[Path]:
    return [
        Path(p)
        for p in (
            ([item["result_json"]] if item.get("result_json") else [])
            + ([item["result_md"]] if item.get("result_md") else [])
            + ([item["contract"]] if item.get("contract") else [])
            + list(item.get("code") or [])
            + list(item.get("logs") or [])
            + list(item.get("extras") or [])
        )
        if p is not None
    ]


def copy_sources(exp_dir: Path, item: dict) -> dict[str, str]:
    src_dir = exp_dir / "source"
    src_dir.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str] = {}
    for p in archivable(src_dir, candidate_sources(item)):
        dest = src_dir / p.name
        if not dest.exists():
            shutil.copy2(p, dest)
        hashes[f"source/{p.name}"] = sha256_file(dest)
    return hashes


def archive_metrics(hashes: dict[str, str]) -> dict[str, int]:
    """Derive the run metrics from the archive itself.

    These used to be computed from the porting machine's candidate list, so a
    package could report source_script_present: 1 while shipping no script.
    """
    names = [Path(k).name for k in hashes]
    return {
        "import_complete": 1 if names else 0,
        "source_result_present": int(any(
            "result" in n and n.endswith((".json", ".md")) for n in names)),
        "source_script_present": int(any(
            n.endswith((".sage", ".py", ".c")) for n in names)),
        "copied_artifact_count": len(hashes),
    }


def archived_artifacts(exp_dir: Path) -> dict[str, str]:
    """`source/<name> -> sha256` for the files this package actually ships.

    Reads the committed tree, not the porting machine, so `--verify` means the
    same thing for a reviewer with a fresh clone and no Autolab checkout.
    """
    src_dir = exp_dir / "source"
    if not src_dir.is_dir():
        return {}
    present = sorted(p for p in src_dir.iterdir() if p.is_file())
    kept = archivable(src_dir, present)
    return {f"source/{p.name}": sha256_file(p) for p in sorted(kept)}


def _replace_section(text: str, heading: str, body: list[str]) -> str:
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return text
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].startswith("## ")), len(lines))
    trailing = [""] if end < len(lines) else []
    return "\n".join(lines[:start + 1] + body + trailing + lines[end:]) + "\n"


def package_discrepancies(exp_dir: Path) -> list[str]:
    """Every provenance claim in the package that the archive does not back."""
    problems: list[str] = []
    truth = archived_artifacts(exp_dir)

    impl = exp_dir / "implementation.md"
    if impl.exists():
        listed = set(re.findall(r"^- `(source/[^`]+)`", impl.read_text(), re.M))
        for missing in sorted(listed - set(truth)):
            problems.append(f"implementation.md lists `{missing}`, which is not archived")
        for unlisted in sorted(set(truth) - listed):
            problems.append(f"implementation.md omits archived `{unlisted}`")

    for manifest in sorted((exp_dir / "runs").glob("*/manifest.yaml")):
        run = (yaml.safe_load(manifest.read_text()) or {}).get("run", {})
        metrics = run.get("result", {}).get("metrics", {})
        for key, want in archive_metrics(truth).items():
            got = metrics.get(key)
            if got is not None and got != want:
                problems.append(
                    f"{manifest.parent.name}/manifest.yaml {key}={got}, archive has {want}")
        raw_path = manifest.parent / "raw-result.json"
        if raw_path.exists():
            try:
                raw = json.loads(raw_path.read_text())
            except json.JSONDecodeError:
                problems.append(f"{manifest.parent.name}/raw-result.json is unparseable")
                continue
            recorded = raw.get("copied_artifact_sha256") or {}
            for rel, digest in sorted(recorded.items()):
                if rel not in truth:
                    problems.append(
                        f"{manifest.parent.name}/raw-result.json hashes unarchived `{rel}`")
                elif truth[rel] != digest:
                    problems.append(
                        f"{manifest.parent.name}/raw-result.json sha256 mismatch for `{rel}`")
            for rel in sorted(set(truth) - set(recorded)):
                problems.append(
                    f"{manifest.parent.name}/raw-result.json omits archived `{rel}`")
    return problems


_OLD_FALLBACK = "Historical Autolab experiment with retained result artifacts."


def finding_is_degenerate(text: str) -> bool:
    """Is this 'finding' a status flag, a serialized dict, or a placeholder?

    Such text was copied verbatim into hypothesis statements and experiment
    objectives, where "Source finding: failed" reads as a scientific result.
    """
    stripped = (text or "").strip().rstrip(".").strip()
    return (not stripped
            or stripped == _OLD_FALLBACK.rstrip(".")
            or stripped.lower() in _STATUS_TOKENS
            or stripped[0] in "{["
            or _is_metadata_line(stripped))


def archived_result(exp_dir: Path) -> tuple[object, str]:
    """The result artifacts this package ships, for recomputing derived text."""
    src_dir = exp_dir / "source"
    if not src_dir.is_dir():
        return None, ""
    files = sorted(p for p in src_dir.iterdir() if p.is_file())
    obj = None
    for p in files:
        if p.name.endswith("_result.json") or p.name == "score.json":
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                obj = None
            break
    md = ""
    for p in files:
        if p.suffix == ".md" and ("result" in p.name.lower() or p.name == "README.md"):
            md = read_text(p)
            break
    return obj, md


def _rewrite_finding(path: Path, old: str, new: str) -> bool:
    """Replace a finding inside a YAML scalar without reflowing the document."""
    if not path.exists():
        return False
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    body = next(iter(doc.values()))
    changed = False
    for key in ("statement", "objective"):
        value = body.get(key)
        if isinstance(value, str) and old in value:
            body[key] = value.replace(old, new)
            changed = True
    if changed:
        dump_yaml(path, doc)
    return changed


def reconcile_findings(exp_dir: Path) -> str | None:
    """Refresh a package's derived finding text when the recorded one is
    degenerate. Returns the replacement, or None if nothing needed changing."""
    spec_path = exp_dir / "specification.yaml"
    if not spec_path.exists():
        return None
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))["experiment"]
    objective = spec.get("objective") or ""
    marker = "Source finding: "
    if marker not in objective:
        return None
    old = objective.split(marker, 1)[1].strip()
    if not finding_is_degenerate(old):
        return None

    new = extract_finding(*archived_result(exp_dir))
    if new.strip().rstrip(".") == old.strip().rstrip("."):
        return None

    _rewrite_finding(spec_path, old, new)
    h_id = spec.get("hypothesis_id")
    if h_id:
        _rewrite_finding(REPO / "ledger" / "hypotheses" / f"{h_id}.yaml", old, new)

    # Only the observation line is derived from the finding; the source excerpt
    # below it is archived content and must survive untouched.
    analysis = exp_dir / "analysis.md"
    if analysis.exists():
        lines = analysis.read_text(encoding="utf-8").splitlines()
        if "## Observation" in lines:
            i = lines.index("## Observation") + 1
            if i < len(lines) and lines[i].strip() == old:
                lines[i] = new
                analysis.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return new


def reconcile_package(exp_dir: Path) -> bool:
    """Rewrite the derived provenance fields to match the archive.

    Only touches values that are a *function of* the archived files. Source
    artifacts, findings, and every hand-written field are left alone.
    """
    truth = archived_artifacts(exp_dir)
    metrics = archive_metrics(truth)
    changed = False

    impl = exp_dir / "implementation.md"
    if impl.exists():
        before = impl.read_text()
        body = [f"- `{rel}`" for rel in sorted(truth)] or [
            "- (no archivable source artifact)"]
        after = _replace_section(before, "## Copied artifacts", body)
        if after != before:
            impl.write_text(after, encoding="utf-8")
            changed = True

    for manifest in sorted((exp_dir / "runs").glob("*/manifest.yaml")):
        doc = yaml.safe_load(manifest.read_text())
        recorded = doc["run"]["result"]["metrics"]
        for key, want in metrics.items():
            if key in recorded and recorded[key] != want:
                recorded[key] = want
                changed = True
        raw_path = manifest.parent / "raw-result.json"
        if raw_path.exists():
            raw = json.loads(raw_path.read_text())
            if raw.get("copied_artifact_sha256") != truth:
                raw["copied_artifact_sha256"] = truth
                raw_path.write_text(
                    json.dumps(raw, indent=2, default=str) + "\n", encoding="utf-8")
                changed = True
        dump_yaml(manifest, doc)
    return changed


def describe_package(exp_dir: Path) -> dict | None:
    """Reconstruct a manifest row from the committed package alone."""
    spec_path = exp_dir / "specification.yaml"
    if not spec_path.exists():
        return None
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))["experiment"]
    inputs = spec.get("inputs") or {}
    objective = spec.get("objective") or ""
    finding = (objective.split("Source finding: ", 1)[1].strip()
               if "Source finding: " in objective else "")
    runs = sorted(d.name for d in (exp_dir / "runs").glob("*") if d.is_dir())
    topic = ""
    for manifest in sorted((exp_dir / "runs").glob("*/manifest.yaml")):
        run = (yaml.safe_load(manifest.read_text()) or {}).get("run", {})
        topic = (run.get("inputs", {}).get("parameters", {}) or {}).get("topic", "")
        break
    return {
        "experiment_id": spec["id"],
        "hypothesis_id": spec.get("hypothesis_id"),
        "run_id": runs[0] if runs else None,
        "source_id": inputs.get("source_id"),
        "area": spec["id"].split("-")[1],
        "topic": topic,
        "finding": finding,
        "artifact_count": len(archived_artifacts(exp_dir)),
    }


def reconcile_inventory() -> bool:
    """Rebuild the port manifest and inventory doc from the committed packages.

    Both were regenerated after the packages were written, against a different
    resolved source root, so they disagreed with all 84 specifications about
    where the artifacts came from and how many there were.
    """
    ports = [row for row in (describe_package(d) for d in package_dirs()) if row]
    if not ports:
        return False
    manifest_path = REPO / "inputs" / f"autolab_port_manifest_{PORT_DATE.replace('-', '')}.yaml"
    doc_path = REPO / "docs" / f"autolab-port-inventory-{PORT_DATE.replace('-', '')}.md"
    before = (manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else "",
              doc_path.read_text(encoding="utf-8") if doc_path.exists() else "")
    existing = yaml.safe_load(before[0]) if before[0] else {}
    write_inventory(ports, existing.get("deferred") or deferred_inventory(),
                    target_commit=existing.get("target_commit_at_port"),
                    target_repo=existing.get("target_repo"))
    return before != (manifest_path.read_text(encoding="utf-8"),
                      doc_path.read_text(encoding="utf-8"))


VERIFY_BASELINE = REPO / "tools" / "autolab_port_verify_baseline.yaml"


def discrepancy_fingerprint(problems: list[str]) -> str:
    return hashlib.sha256("\n".join(problems).encode("utf-8")).hexdigest()


def load_verify_baseline() -> dict:
    """Load exact legacy discrepancies without weakening new mismatch checks."""
    if not VERIFY_BASELINE.exists():
        return {}
    document = yaml.safe_load(VERIFY_BASELINE.read_text(encoding="utf-8")) or {}
    if document.get("schema") != "autolab-port-verify-baseline-v1":
        raise ValueError(f"{VERIFY_BASELINE} has an unknown schema")
    return document


def package_dirs() -> list[Path]:
    root = REPO / "experiments"
    return sorted(
        d for area in AREA_META for d in root.glob(f"EXP-{area}-*") if d.is_dir())


def port_item(item: dict, index: int) -> dict | None:
    area = item["area"]
    nnn = f"{index:03d}"
    exp_id = f"EXP-{area}-{nnn}"
    h_id = f"H-{area}-{nnn}"
    rq_id = AREA_META[area]["rq_id"]

    # Fail closed BEFORE anything is written. An import that archives no source
    # artifact has nothing to archive, and emitting it anyway produced runs
    # marked completed_valid / import_complete: 1 over an empty source/ dir --
    # a receipt for work that did not happen.
    exp_dir = REPO / "experiments" / exp_id
    if not archivable(exp_dir / "source", candidate_sources(item)):
        return None

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
                # The schema carries one hypothesis_id, but this record spans
                # every hypothesis in the area. The scalar names the first and
                # `hypothesis_ids` carries the real, complete linkage.
                "hypothesis_id": ports[0]["hypothesis_id"],
                "hypothesis_ids": [p["hypothesis_id"] for p in ports],
                "hypothesis_id_note": (
                    f"Scalar `hypothesis_id` is a schema artifact: this record "
                    f"covers all {len(ports)} {area} import hypotheses listed in "
                    f"`hypothesis_ids`, one per experiment."
                ),
                "experiment_ids": [p["experiment_id"] for p in ports],
                "run_ids": [p["run_id"] for p in ports],
                "type": "empirical",
                "direction": "neutral",
                "strength": "preliminary",
                "claim_tier": "toy",
                "certificate_refs": [],
                "certificate_refs_note": (
                    "Empty by construction: every imported run carries "
                    "`certificate.kind: none`, so there is no verified solve or "
                    "relation for this record to cite."
                ),
                "proof_status": "empirical_only",
                "proof_refs": [],
                "observations": [
                    f"Imported {len(ports)} Autolab packages into harness EXP/RUN layout.",
                    *[
                        f"{p['experiment_id']}: {p['source_id']} — {p['finding'][:180]}"
                        for p in ports
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


def write_inventory(all_ports: list[dict], deferred: list[dict],
                    target_commit: str | None = None,
                    target_repo: str | None = None) -> None:
    manifest = {
        "schema": "autolab-port-manifest-v1",
        "port_tag": PORT_TAG,
        "ported_at": PORT_DATE,
        "source_repo": str(AUTOLAB),
        "source_commit": AUTOLAB_COMMIT,
        # Both record where and when the port ran, so a later rebuild of this
        # index must not overwrite them with today's checkout and HEAD.
        "target_repo": target_repo or str(REPO),
        "target_commit_at_port": target_commit or git_commit(REPO),
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
        "## Verifying this port",
        "",
        "Needs no Autolab checkout. Recomputes each package's artifact list, count",
        "and per-file sha256 from the files it ships, and compares them against",
        "`implementation.md`, `manifest.yaml`, `raw-result.json` and this manifest:",
        "",
        "```bash",
        "python3 tools/port_autolab_experiments.py --verify",
        "```",
        "",
        "`--verify --reconcile` rewrites those derived fields from the archive.",
        "It never edits an archived source artifact.",
        "",
        "## How to extend",
        "",
        "Porting needs the source tree. `inputs/refs` is a documentation mirror and",
        "holds no result artifacts, so point `AUTOLAB_ROOT` at a full checkout at the",
        "pinned commit; the tool refuses to run against a partial source.",
        "",
        "```bash",
        "AUTOLAB_ROOT=/path/to/autolab python3 tools/port_autolab_experiments.py",
        "python3 tools/port_autolab_experiments.py --verify",
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
    # A partial source produces a partial port that still looks complete, so
    # refuse rather than emit one. `--verify` is the mode that needs no
    # Autolab checkout; porting genuinely does.
    if not has_portable_content(AUTOLAB):
        raise SystemExit(
            f"Autolab source has no portable content: {AUTOLAB}\n"
            f"Expected {AUTOLAB}/experiments/ecdlp_prime_field/*_result.json.\n"
            f"Set AUTOLAB_ROOT to a full Autolab checkout at {AUTOLAB_COMMIT}, "
            f"or use --verify to check the already-ported packages."
        )

    write_questions()

    catalogs = {
        "ALPF": catalog_prime(),
        "ALBIN": catalog_binary(),
        "ALISO": catalog_isogeny(),
        "ALECF": catalog_ecdsafail(),
    }

    all_ports: list[dict] = []
    skipped: list[dict] = []
    for area, items in catalogs.items():
        for i, item in enumerate(items, start=1):
            if only and item["source_id"] != only and only not in item["source_id"]:
                continue
            ported = port_item(item, i)
            if ported is None:
                skipped.append({"area": area, "source_id": item["source_id"]})
                print(f"skipped {area}-{i:03d} <- {item['source_id']} "
                      f"(no archivable source artifact)")
                continue
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


def verify(fix: bool = False) -> int:
    """Re-check every ported package's provenance against what it ships."""
    dirs = package_dirs()
    if not dirs:
        print("no EXP-AL* packages found")
        return 0
    if fix:
        touched = [d.name for d in dirs if reconcile_package(d)]
        print(f"reconciled provenance for {len(touched)} of {len(dirs)} package(s)")
        refreshed = [d.name for d in dirs if reconcile_findings(d)]
        print(f"refreshed degenerate findings for {len(refreshed)} package(s)")
        for name in refreshed:
            print(f"  {name}")
        if reconcile_inventory():
            print("rebuilt the port manifest and inventory doc")

    baseline = load_verify_baseline()
    baseline_packages = baseline.get("packages") or {}
    suppressed = 0
    failures = 0
    for exp_dir in dirs:
        problems = package_discrepancies(exp_dir)
        if problems:
            if baseline_packages.get(exp_dir.name) == discrepancy_fingerprint(problems):
                suppressed += 1
                print(f"KNOWN LEGACY {exp_dir.name}: exact mismatch fingerprint suppressed")
            else:
                failures += 1
                print(f"FAIL {exp_dir.name}")
                for problem in problems:
                    print(f"  - {problem}")
    manifest_path = REPO / "inputs" / f"autolab_port_manifest_{PORT_DATE.replace('-', '')}.yaml"
    if manifest_path.exists():
        recorded = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
        rows = {r.get("experiment_id"): r for r in recorded.get("ported") or []}
        truth = {r["experiment_id"]: r for r in
                 (describe_package(d) for d in dirs) if r}
        # Compared against the specifications, not against whatever root this
        # machine resolves, so the check means the same thing in CI as it does
        # on the porting machine.
        declared = {
            (yaml.safe_load(d.joinpath("specification.yaml").read_text())
             ["experiment"].get("inputs") or {}).get("source_repo")
            for d in dirs if d.joinpath("specification.yaml").exists()
        }
        inventory_problems = []
        if len(declared) > 1:
            inventory_problems.append(
                f"experiment specifications disagree on source_repo: "
                f"{sorted(map(str, declared))}")
        elif declared and recorded.get("source_repo") != next(iter(declared)):
            inventory_problems.append(
                f"{manifest_path.name}: source_repo {recorded.get('source_repo')!r} != "
                f"{next(iter(declared))!r} recorded in every specification")
        for exp_id in sorted(set(rows) | set(truth)):
            if rows.get(exp_id) != truth.get(exp_id):
                inventory_problems.append(f"{manifest_path.name}: {exp_id} row is stale")
        if inventory_problems:
            if baseline.get("inventory") == discrepancy_fingerprint(inventory_problems):
                suppressed += 1
                print("KNOWN LEGACY inventory: exact mismatch fingerprint suppressed")
            else:
                failures += len(inventory_problems)
                for problem in inventory_problems:
                    print(f"FAIL {problem}")

    if failures:
        print(f"\nFAIL: {failures} provenance mismatch(es); "
              f"rerun with --reconcile to rebuild from the archive")
        return 1
    suffix = f"; {suppressed} known legacy mismatch set(s) suppressed" if suppressed else ""
    print(f"PASS: {len(dirs)} package(s) match their archived source artifacts{suffix}")
    return 0


if __name__ == "__main__":
    import argparse
    import sys

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", default=None, help="Port only matching source_id substring")
    ap.add_argument("--verify", action="store_true",
                    help="Check committed packages against their archived source/ "
                         "files instead of porting; exits 1 on any mismatch")
    ap.add_argument("--reconcile", action="store_true",
                    help="With --verify: first rewrite derived provenance fields "
                         "(artifact lists, counts, hashes) to match the archive")
    args = ap.parse_args()
    if args.verify or args.reconcile:
        sys.exit(verify(fix=args.reconcile))
    main(only=args.only)
