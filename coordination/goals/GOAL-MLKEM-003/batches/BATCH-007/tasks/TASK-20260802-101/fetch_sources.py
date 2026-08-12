#!/usr/bin/env python3
"""Fetch the TASK-20260802-101 source set once, with immutable provenance."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent
REPO = TASK_DIR.parents[6]
OUT = REPO / "inputs" / "MLKEM-DUAL-SOURCES-20260802"
BASELINE_HAL = "experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf"
BASELINE_CODE = "experiments/EXP-MLKEM-013/vendor-lock/FFT_sample.py"
USER_AGENT = "crypto-autoresearcher/TASK-20260802-101 source retrieval"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def write_text_new(path: Path, text: str) -> None:
    write_new(path, text.encode("utf-8"))


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def fetch(url: str, timeout: int = 60) -> tuple[bytes | None, dict[str, object]]:
    started = utc_now()
    marker = b"\n__TASK_20260802_101_META__"
    command = [
        "curl",
        "-L",
        "--max-time",
        str(timeout),
        "-sS",
        "-A",
        USER_AGENT,
        "-w",
        "\\n__TASK_20260802_101_META__%{http_code}\\n%{content_type}\\n%{url_effective}",
        url,
    ]
    try:
        result = subprocess.run(command, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if marker not in result.stdout:
            raise RuntimeError(f"curl returned no metadata marker (exit {result.returncode}): {result.stderr.decode('utf-8', 'replace').strip()}")
        body, metadata = result.stdout.rsplit(marker, 1)
        lines = metadata.decode("utf-8", "replace").splitlines()
        status = int(lines[0]) if lines and lines[0].isdigit() else 0
        content_type = lines[1] if len(lines) > 1 else None
        final_url = lines[2] if len(lines) > 2 else url
        if status >= 400 or result.returncode != 0:
            error = f"HTTP {status}" if status >= 400 else f"curl exit {result.returncode}"
            stderr = result.stderr.decode("utf-8", "replace").strip()
            if stderr:
                error += f": {stderr}"
            return None, {
                "url": url,
                "final_url": final_url,
                "http_status": status or None,
                "retrieved_at": started,
                "sha256": None,
                "bytes": 0,
                "status": "unretrieved",
                "error": error,
            }
        return body, {
            "url": url,
            "final_url": final_url,
            "http_status": status,
            "retrieved_at": started,
            "sha256": sha256(body),
            "bytes": len(body),
            "status": "retrieved",
            "content_type": content_type,
        }
    except (RuntimeError, OSError) as exc:
        return None, {
            "url": url,
            "http_status": None,
            "retrieved_at": started,
            "sha256": None,
            "bytes": 0,
            "status": "unretrieved",
            "error": f"{type(exc).__name__}: {exc}",
        }


def pdf_text(body: bytes) -> str:
    result = subprocess.run(
        ["pdftotext", "-", "-"],
        input=body,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdftotext failed with exit {result.returncode}: {result.stderr.decode('utf-8', 'replace')}")
    return result.stdout.decode("utf-8", "replace")


def selected_locus(text: str, patterns: list[str], radius: int = 1800) -> str:
    chunks: list[str] = []
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            start = max(0, match.start() - radius)
            end = min(len(text), match.end() + radius)
            chunks.append(text[start:end].strip())
    return "\n\n--- selected locus ---\n\n".join(chunks)


def add_git_baseline(records: list[dict[str, object]], path: str, revision_id: str, label: str) -> bytes:
    body = subprocess.check_output(["git", "show", f"origin/main:{path}"], cwd=REPO)
    records.append(
        {
            "source_id": label,
            "url": f"git+origin/main://{path}",
            "http_status": None,
            "retrieved_at": utc_now(),
            "sha256": sha256(body),
            "bytes": len(body),
            "revision_id": revision_id,
            "status": "retrieved",
            "retrieval_method": "git show origin/main",
            "artifact_path": path,
        }
    )
    return body


def main() -> int:
    if OUT.exists() and any(OUT.iterdir()):
        raise SystemExit(f"refusing to overwrite non-empty output directory: {OUT}")
    if any(TASK_DIR.iterdir()):
        existing = [p.name for p in TASK_DIR.iterdir() if p.name != Path(__file__).name]
        if existing:
            raise SystemExit(f"refusing to overwrite existing task artifacts: {existing}")

    OUT.mkdir(parents=True, exist_ok=True)
    started = utc_now()
    records: list[dict[str, object]] = []
    fetched: dict[str, bytes] = {}

    definitions: list[dict[str, object]] = [
        {
            "source_id": "carrier_eprint_landing",
            "url": "https://eprint.iacr.org/2022/1750",
            "revision_id": "eprint-2022/1750-current-last-of-3-revisions-2025-06-11",
            "save": "carrier_eprint_landing.html",
        },
        {
            "source_id": "carrier_eprint_pdf",
            "url": "https://eprint.iacr.org/2022/1750.pdf",
            "revision_id": "eprint-2022/1750-current-last-of-3-revisions-2025-06-11",
        },
        {
            "source_id": "carrier_eprint_revision_archive",
            "url": "https://eprint.iacr.org/archive/versions/2022/1750",
            "revision_id": "eprint-2022/1750-version-history",
        },
        {
            "source_id": "carrier_hal_landing",
            "url": "https://hal.science/hal-05406481v1",
            "revision_id": "hal-05406481v1",
            "save": "carrier_hal_landing.html",
        },
        {
            "source_id": "carrier_hal_current_pdf",
            "url": "https://hal.science/hal-05406481/document",
            "revision_id": "hal-05406481v1",
        },
        {
            "source_id": "fips203_csrc_landing",
            "url": "https://csrc.nist.gov/pubs/fips/203/final",
            "revision_id": "FIPS-203-final-2024-08-13",
            "save": "fips203_csrc_landing.html",
        },
        {
            "source_id": "fips203_pdf",
            "url": "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf",
            "revision_id": "FIPS-203-final-2024-08-13",
        },
        {
            "source_id": "ducas_pulles_eprint_landing",
            "url": "https://eprint.iacr.org/2023/302",
            "revision_id": "eprint-2023/302-current-approved-2023-03-01",
            "save": "ducas_pulles_eprint_landing.html",
        },
        {
            "source_id": "ducas_pulles_eprint_pdf",
            "url": "https://eprint.iacr.org/2023/302.pdf",
            "revision_id": "eprint-2023/302-current-approved-2023-03-01",
        },
        {
            "source_id": "ducas_pulles_current_fulltext",
            "url": "https://ir.cwi.nl/pub/35843/35843.pdf",
            "revision_id": "journal-version-of-record-2025-11-20",
        },
        {
            "source_id": "matzov_zenodo_v1_metadata",
            "url": "https://zenodo.org/api/records/6412487",
            "revision_id": "Zenodo-6412487-v1-2022-04-04",
            "save": "matzov_v1_metadata.json",
        },
        {
            "source_id": "matzov_zenodo_v1_pdf",
            "url": "https://zenodo.org/api/records/6412487/files/Report%20on%20the%20Security%20of%20LWE.pdf/content",
            "revision_id": "Zenodo-6412487-v1-2022-04-04",
        },
        {
            "source_id": "matzov_zenodo_v2_metadata",
            "url": "https://zenodo.org/api/records/6493704",
            "revision_id": "Zenodo-6493704-v2-2022-04-04",
            "save": "matzov_v2_metadata.json",
        },
        {
            "source_id": "matzov_zenodo_v2_pdf",
            "url": "https://zenodo.org/api/records/6493704/files/Report%20on%20the%20Security%20of%20LWE%20updated.pdf/content",
            "revision_id": "Zenodo-6493704-v2-2022-04-04",
        },
        {
            "source_id": "guo_johansson_asiacrypt2021_pdf",
            "url": "https://www.iacr.org/archive/asiacrypt2021/130900114/130900114.pdf",
            "revision_id": "ASIACRYPT-2021-LNCS-13093-pp33-62",
            "save": "guo_johansson_asiacrypt2021.pdf",
        },
        {
            "source_id": "codedualattack_current_head_api",
            "url": "https://api.github.com/repos/kevin-carrier/CodedDualAttack/commits/main",
            "revision_id": "current-main-resolved-after-fetch",
            "save": "codedualattack_current_head.json",
        },
    ]

    for definition in definitions:
        body, record = fetch(str(definition["url"]))
        record["source_id"] = definition["source_id"]
        record["revision_id"] = definition["revision_id"]
        if body is not None:
            fetched[str(definition["source_id"])] = body
            if definition.get("save"):
                record["artifact_path"] = f"inputs/MLKEM-DUAL-SOURCES-20260802/{definition['save']}"
                write_new(OUT / str(definition["save"]), body)
        records.append(record)

    api_body = fetched.get("codedualattack_current_head_api")
    if api_body is None:
        raise RuntimeError("GitHub current-head API was not retrieved; cannot identify code revision")
    current_head = json.loads(api_body.decode("utf-8"))["sha"]
    for path, output_name in [
        ("verifyModel/ScoreExperimentalDistribution/FFT_sample.py", "codedualattack_current_FFT_sample.py"),
        ("verifyModel/ScoreExperimentalDistribution/Algorithm.py", "codedualattack_current_Algorithm.py"),
    ]:
        url = f"https://raw.githubusercontent.com/kevin-carrier/CodedDualAttack/{current_head}/{path}"
        body, record = fetch(url)
        record.update({"source_id": f"codedualattack_current_{Path(path).stem}", "revision_id": current_head})
        if body is not None:
            write_new(OUT / output_name, body)
            record["artifact_path"] = f"inputs/MLKEM-DUAL-SOURCES-20260802/{output_name}"
        records.append(record)

    baseline_hal = add_git_baseline(records, BASELINE_HAL, "origin/main-pinned-hal-05406481", "carrier_hal_baseline_artifact")
    baseline_code = add_git_baseline(records, BASELINE_CODE, "origin/main-pinned-code-9c1367f", "codedualattack_baseline_vendor_lock")

    hal_body = fetched.get("carrier_hal_current_pdf")
    if hal_body is not None:
        hal_text = pdf_text(hal_body)
        start_matches = list(re.finditer(r"Scheme\s+C0:", hal_text, flags=re.IGNORECASE))
        start = start_matches[-1].start() if start_matches else max(0, hal_text.find("Table C.2") - 2500)
        end_marker = hal_text.find("Table C.2", start)
        end = min(len(hal_text), end_marker + 350 if end_marker >= 0 else start + 6500)
        write_text_new(OUT / "carrier_hal_c2_region.txt", hal_text[start:end].strip())
        write_text_new(OUT / "carrier_hal_front_matter.txt", hal_text[:5000].strip())

    fips_body = fetched.get("fips203_pdf")
    if fips_body is not None:
        fips_text = pdf_text(fips_body)
        write_text_new(OUT / "fips203_selected_text.txt", selected_locus(fips_text, [r"FIPS 203", r"ML-KEM", r"security"], radius=1000))

    dp_body = fetched.get("ducas_pulles_current_fulltext")
    if dp_body is not None:
        dp_text = pdf_text(dp_body)
        write_text_new(
            OUT / "ducas_pulles_score_loci.txt",
            selected_locus(
                dp_text,
                [
                    r"Experimental invalidation of the Prior Model",
                    r"Validating the New Model",
                    r"false positives and false negatives",
                    r"future work",
                ],
                radius=1800,
            ),
        )

    for source_id, output_name in [("matzov_zenodo_v1_pdf", "matzov_v1_loci.txt"), ("matzov_zenodo_v2_pdf", "matzov_v2_loci.txt")]:
        body = fetched.get(source_id)
        if body is not None:
            text = pdf_text(body)
            write_text_new(OUT / output_name, selected_locus(text, [r"Table 1", r"Kyber", r"Pwrong", r"distinguisher"], radius=1600))

    guo_body = fetched.get("guo_johansson_asiacrypt2021_pdf")
    if guo_body is not None:
        write_text_new(OUT / "guo_johansson_selected_text.txt", selected_locus(pdf_text(guo_body), [r"Abstract", r"Kyber", r"distinguisher", r"experiments"], radius=1200))

    for record in records:
        if record.get("source_id") == "codedualattack_current_head_api":
            record["revision_id"] = current_head
        if record.get("source_id") in {"codedualattack_current_FFT_sample", "codedualattack_current_Algorithm"}:
            record["revision_id"] = current_head

    provenance = {
        "schema": "crypto.autoresearch.mlkem_dual_sources_provenance.v1",
        "task_id": "TASK-20260802-101",
        "started_at": started,
        "completed_at": utc_now(),
        "command": "python3 coordination/goals/GOAL-MLKEM-003/batches/BATCH-007/tasks/TASK-20260802-101/fetch_sources.py",
        "cwd": str(REPO),
        "origin_main_commit": git_output("rev-parse", "origin/main"),
        "working_head": git_output("rev-parse", "HEAD"),
        "working_tree_status": git_output("status", "--short", "--branch"),
        "current_codedualattack_head": current_head,
        "baseline_hashes": {
            BASELINE_HAL: {"sha256": sha256(baseline_hal), "bytes": len(baseline_hal)},
            BASELINE_CODE: {"sha256": sha256(baseline_code), "bytes": len(baseline_code)},
        },
        "sources": records,
    }
    write_text_new(OUT / "provenance.json", json.dumps(provenance, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"retrieved": sum(r.get("status") == "retrieved" for r in records), "unretrieved": sum(r.get("status") == "unretrieved" for r in records), "current_codedualattack_head": current_head}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
