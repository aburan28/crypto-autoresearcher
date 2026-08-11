#!/usr/bin/env python3
"""Validate the ECDLP idea corpus without third-party dependencies."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


IDEAS = Path(__file__).resolve().parent
REPO = IDEAS.parent
LEDGER = REPO / "ledger"
LEDGER_INVENTORY = REPO / "inputs" / "ledger_inventory.json"
ID_RE = re.compile(r"ECDLP-IDEA-(\d{3})")
FILE_RE = re.compile(r"ECDLP-IDEA-(\d{3})_[a-z0-9_]+_hypothesis\.md$")
REQUIRED_HEADINGS = [
    "## Status and claim labels",
    "## Falsifiable hypothesis",
    "## Mechanism-new operation",
    "## Assumptions",
    "## Semantic fingerprint",
    "## Five closest ledger entries",
    "## Closest primary literature",
    "## Complete factor-base-to-target-descent path",
    "## Full rho/BSGS cost model",
    "## Likely fatal obstruction",
    "## Proof track",
    "## Disproof track",
    "## Positive and negative controls",
    "## Quantitative promotion and falsification gates",
    "## Artifact plan",
    "## Interpretation boundary",
    "## Exactly one next executable action",
]
EXPECTED_HYPOTHESIS_COUNT = 20
EXPECTED_CONTRACT_COUNT = 12
REQUIRED_DEDUP_REPORT = "DEDUP-20260718T132546-0700.md"
REQUIRED_REDTEAM_REPORT = "REDTEAM-20260718T134111-0700.md"
P1514_V2_ARTIFACT_HASHES = {
    "ECDLP-IDEA-133/nonlinear_apolar_operation_theorem.md": (
        "4093e48132d96706db1155c44a8ab0f82de5ae997885df56b6ba1074022f297e"
    ),
    "ECDLP-IDEA-133/nonlinear_apolar_operation_theorem_v2.md": (
        "b97666d65119c90eb7c63ac9df3be650af1b1e42854f613d1b39dc1eb68c50b2"
    ),
    "ECDLP-IDEA-133/nonlinear_apolar_operation_theorem_audit_v2.md": (
        "d718a341153f1ea805c59fe1f45511712fda1805fbcc61103bbe9f1f4159866f"
    ),
    "ECDLP-IDEA-133/verify_nonlinear_apolar_theorem.py": (
        "cafef7ab468f11d3c68d58ab3105c3c76ebc33a7ffcdd3ec519c6a6cdbc43ec4"
    ),
    "ECDLP-IDEA-133/verify_nonlinear_apolar_theorem_v2.py": (
        "de07cdefea70091f193a0bb6b28e5dc38d0fc29fcf809295a0a30f29561b9ef9"
    ),
    "ECDLP-IDEA-133/verify_nonlinear_apolar_theorem_v3.py": (
        "8d17e1339c98d586a3d1bb67032ba30fe364b9b76d9171f6cb88bebcc0c9293b"
    ),
}
EXPECTED_IDS = {
    *(f"ECDLP-IDEA-{i:03d}" for i in range(2, 13)),
    "ECDLP-IDEA-050",
    "ECDLP-IDEA-056",
    "ECDLP-IDEA-059",
    "ECDLP-IDEA-158",
    "ECDLP-IDEA-159",
    "ECDLP-IDEA-160",
    "ECDLP-IDEA-434",
    "ECDLP-IDEA-435",
    "ECDLP-IDEA-436",
}
EXPECTED_REJECTED_IDS = {
    "ECDLP-IDEA-001",
    *(f"ECDLP-IDEA-{i:03d}" for i in range(13, 49)),
    "ECDLP-IDEA-051",
    "ECDLP-IDEA-054",
    "ECDLP-IDEA-055",
    "ECDLP-IDEA-057",
    "ECDLP-IDEA-060",
    "ECDLP-IDEA-061",
    "ECDLP-IDEA-062",
    "ECDLP-IDEA-063",
    "ECDLP-IDEA-065",
    "ECDLP-IDEA-066",
    "ECDLP-IDEA-067",
    "ECDLP-IDEA-070",
    "ECDLP-IDEA-071",
    "ECDLP-IDEA-072",
    "ECDLP-IDEA-074",
    "ECDLP-IDEA-077",
    "ECDLP-IDEA-078",
    "ECDLP-IDEA-079",
    "ECDLP-IDEA-080",
    "ECDLP-IDEA-081",
    "ECDLP-IDEA-082",
    "ECDLP-IDEA-083",
    "ECDLP-IDEA-084",
    "ECDLP-IDEA-085",
    *(f"ECDLP-IDEA-{i:03d}" for i in range(88, 97)),
    "ECDLP-IDEA-097",
    "ECDLP-IDEA-099",
    "ECDLP-IDEA-100",
    "ECDLP-IDEA-101",
    *(f"ECDLP-IDEA-{i:03d}" for i in range(104, 109)),
    "ECDLP-IDEA-109",
    "ECDLP-IDEA-110",
    "ECDLP-IDEA-112",
    "ECDLP-IDEA-113",
    "ECDLP-IDEA-114",
    "ECDLP-IDEA-115",
    "ECDLP-IDEA-116",
    "ECDLP-IDEA-117",
    "ECDLP-IDEA-118",
    "ECDLP-IDEA-120",
    *(f"ECDLP-IDEA-{i:03d}" for i in range(122, 133)),
    *(f"ECDLP-IDEA-{i:03d}" for i in range(134, 146)),
    "ECDLP-IDEA-146",
    "ECDLP-IDEA-147",
    "ECDLP-IDEA-148",
    "ECDLP-IDEA-149",
    "ECDLP-IDEA-150",
    "ECDLP-IDEA-151",
    *(f"ECDLP-IDEA-{i:03d}" for i in range(153, 158)),
    "ECDLP-IDEA-162",
    "ECDLP-IDEA-166",
    "ECDLP-IDEA-168",
    "ECDLP-IDEA-169",
    "ECDLP-IDEA-170",
    "ECDLP-IDEA-171",
    "ECDLP-IDEA-172",
    "ECDLP-IDEA-174",
    "ECDLP-IDEA-175",
    "ECDLP-IDEA-176",
    "ECDLP-IDEA-177",
    "ECDLP-IDEA-178",
    "ECDLP-IDEA-179",
    "ECDLP-IDEA-180",
    "ECDLP-IDEA-181",
    *(f"ECDLP-IDEA-{i:03d}" for i in range(182, 194)),
    "ECDLP-IDEA-194",
    *(f"ECDLP-IDEA-{i:03d}" for i in range(196, 411)),
}
EXPECTED_DEFERRED_IDS = {
    "ECDLP-IDEA-049",
    "ECDLP-IDEA-052",
    "ECDLP-IDEA-053",
    "ECDLP-IDEA-058",
    "ECDLP-IDEA-064",
    "ECDLP-IDEA-068",
    "ECDLP-IDEA-069",
    "ECDLP-IDEA-073",
    "ECDLP-IDEA-075",
    "ECDLP-IDEA-076",
    "ECDLP-IDEA-086",
    "ECDLP-IDEA-087",
    "ECDLP-IDEA-098",
    "ECDLP-IDEA-102",
    "ECDLP-IDEA-103",
    "ECDLP-IDEA-111",
    "ECDLP-IDEA-119",
    "ECDLP-IDEA-121",
    "ECDLP-IDEA-133",
    "ECDLP-IDEA-152",
    "ECDLP-IDEA-161",
    "ECDLP-IDEA-163",
    "ECDLP-IDEA-164",
    "ECDLP-IDEA-165",
    "ECDLP-IDEA-167",
    "ECDLP-IDEA-173",
    "ECDLP-IDEA-195",
}
EXPECTED_COHORT_SIZES = {
    "20260717-a": 11,
    "20260717-b": 3,
    "20260718-b": 3,
    "20260809-a": 3,
}
NEW_COHORT_IDS = {f"ECDLP-IDEA-{i:03d}" for i in range(61, 411)}
EXPECTED_RETIRED_CONTRACT_COUNT = 97
EXPECTED_NEW_RETIRED_CONTRACT_IDS = {
    "ECDLP-IDEA-063",
    "ECDLP-IDEA-066",
    "ECDLP-IDEA-069",
    "ECDLP-IDEA-073",
    "ECDLP-IDEA-075",
    "ECDLP-IDEA-076",
    "ECDLP-IDEA-080",
    "ECDLP-IDEA-085",
    "ECDLP-IDEA-086",
    "ECDLP-IDEA-087",
    "ECDLP-IDEA-098",
    "ECDLP-IDEA-102",
    "ECDLP-IDEA-103",
    "ECDLP-IDEA-115",
    "ECDLP-IDEA-117",
    "ECDLP-IDEA-119",
    "ECDLP-IDEA-128",
    "ECDLP-IDEA-129",
    "ECDLP-IDEA-133",
    "ECDLP-IDEA-134",
    "ECDLP-IDEA-135",
    "ECDLP-IDEA-145",
    "ECDLP-IDEA-146",
    "ECDLP-IDEA-149",
    "ECDLP-IDEA-150",
    "ECDLP-IDEA-170",
    "ECDLP-IDEA-174",
    "ECDLP-IDEA-180",
    "ECDLP-IDEA-182",
    "ECDLP-IDEA-183",
    "ECDLP-IDEA-192",
    "ECDLP-IDEA-194",
    "ECDLP-IDEA-195",
    "ECDLP-IDEA-202",
    "ECDLP-IDEA-209",
    "ECDLP-IDEA-211",
    "ECDLP-IDEA-212",
    "ECDLP-IDEA-218",
    "ECDLP-IDEA-219",
    "ECDLP-IDEA-220",
    "ECDLP-IDEA-230",
    "ECDLP-IDEA-231",
    "ECDLP-IDEA-233",
    "ECDLP-IDEA-242",
    "ECDLP-IDEA-244",
    "ECDLP-IDEA-250",
    "ECDLP-IDEA-254",
    "ECDLP-IDEA-255",
    "ECDLP-IDEA-263",
    "ECDLP-IDEA-266",
    "ECDLP-IDEA-270",
    "ECDLP-IDEA-276",
    "ECDLP-IDEA-278",
    "ECDLP-IDEA-279",
    "ECDLP-IDEA-287",
    "ECDLP-IDEA-290",
    "ECDLP-IDEA-296",
    "ECDLP-IDEA-300",
    "ECDLP-IDEA-304",
    "ECDLP-IDEA-309",
    "ECDLP-IDEA-313",
    "ECDLP-IDEA-320",
    "ECDLP-IDEA-322",
    "ECDLP-IDEA-323",
    "ECDLP-IDEA-324",
    "ECDLP-IDEA-326",
    "ECDLP-IDEA-327",
    "ECDLP-IDEA-333",
    "ECDLP-IDEA-338",
    "ECDLP-IDEA-341",
    "ECDLP-IDEA-349",
    "ECDLP-IDEA-350",
    "ECDLP-IDEA-354",
    "ECDLP-IDEA-360",
    "ECDLP-IDEA-362",
    "ECDLP-IDEA-367",
    "ECDLP-IDEA-373",
    "ECDLP-IDEA-374",
    "ECDLP-IDEA-378",
    "ECDLP-IDEA-379",
    "ECDLP-IDEA-386",
    "ECDLP-IDEA-388",
    "ECDLP-IDEA-391",
    "ECDLP-IDEA-398",
    "ECDLP-IDEA-399",
    "ECDLP-IDEA-400",
    "ECDLP-IDEA-410",
}
EXPECTED_CURRENT_RETIRED_FORMULAS = {
    "ECDLP-IDEA-134": (
        "lambda=max(s*beta,(1+alpha+delta+o)*beta,ell*beta,(alpha+delta_t+o+u)*beta,beta)",
        "mu=max(s_m*beta,m_q*beta,(1+o)*beta,ell_m*beta,u*beta)",
    ),
    "ECDLP-IDEA-135": (
        "lambda=max(a,c,beta+delta+q+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,c,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-098": (
        "lambda=max(g,f,beta+delta+k+o,ell,delta_t+k+o+u,beta)",
        "mu=max(gm,f,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-102": (
        "lambda=max(a,v,s,h,beta+delta+k+o,ell,delta_t+k+o+u,beta)",
        "mu=max(am,v,s,h,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-103": (
        "lambda=max(a,g+h,beta+delta+q+o+v,ell,delta_t+q+o+u+v)",
        "mu=max(a_m,g+h,q_m,ell_m,beta+o,o+u,v_m)",
    ),
    "ECDLP-IDEA-115": (
        "lambda=max(a,c,beta+delta+k+o,ell,delta_t+k+o+u,beta)",
        "mu=max(a_m,c_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-117": (
        "lambda=max(s*ell,1+(alpha-4)*ell,2*ell,1+(alpha-5)*ell)",
        "mu=max(s_m*ell,m_q*ell,ell)",
    ),
    "ECDLP-IDEA-119": (
        "lambda=max(a,beta+delta+q+o+v,ell_LA,delta_t+q+o+u+v)",
        "mu=max(a_m,q_m,m_LA,beta+o,o+u,v_m)",
    ),
    "ECDLP-IDEA-128": (
        "lambda=max(s*ell,1+(alpha-4)*ell,2*ell,1+(alpha-5)*ell)",
        "mu=max(s_m*ell,m_q*ell,ell)",
    ),
    "ECDLP-IDEA-129": (
        "lambda=max(s*ell,1+(alpha-4)*ell,2*ell,1+(alpha-5)*ell)",
        "mu=max(s_m*ell,m_q*ell,ell)",
    ),
    "ECDLP-IDEA-133": (
        "lambda=max(a,c,beta+delta+k+o,ell,delta_t+k+o+u,beta)",
        "mu=max(a_m,c_m,k_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-145": (
        "lambda=max(a,q+delta,chi+u,ell,beta)",
        "mu=max(a_m,q_m,chi_m,ell_m,u)",
    ),
    "ECDLP-IDEA-146": (
        "lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-149": (
        "lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-150": (
        "lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-170": (
        "lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-174": (
        "lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-180": (
        "lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-182": (
        "lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-183": (
        "lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-192": (
        "lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-194": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-195": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-202": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-209": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-211": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-212": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-218": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-219": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-220": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-230": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-231": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-233": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-242": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-244": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-250": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-254": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-255": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-263": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-266": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-270": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-276": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-278": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-279": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-287": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-290": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-296": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
    "ECDLP-IDEA-300": (
        "lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)",
        "mu=max(a_m,q_m,beta+o,ell_m,u)",
    ),
}


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    start += len(heading)
    match = re.search(r"^## ", text[start:], flags=re.MULTILINE)
    return text[start:] if match is None else text[start : start + match.start()]


def within_repo(path_text: str) -> bool:
    candidate = (REPO / path_text).resolve()
    try:
        candidate.relative_to(REPO.resolve())
    except ValueError:
        return False
    return ".." not in Path(path_text).parts


def validate_exact_inventory_neighbors(
    *,
    idea_id: str,
    closest: str,
    path: Path,
    inventory_ids: set[str],
    errors: list[str],
) -> None:
    """Require the new cohort to name five exact imported ledger IDs."""
    if idea_id not in NEW_COHORT_IDS:
        return
    imported = re.findall(
        r"(?m)^[1-5]\.\s+`(?:ledger|inputs)/[^`]+`\s+—\s+imported\s+`([^`]+)`",
        closest,
    )
    if len(imported) != 5 or len(set(imported)) != 5:
        errors.append(
            f"{path.name}: new-cohort closest section must name five unique exact "
            "imported ledger IDs"
        )
        return
    unknown = sorted(set(imported) - inventory_ids)
    if unknown:
        errors.append(f"{path.name}: unknown imported ledger IDs: {unknown}")


def main() -> int:
    errors: list[str] = []
    inventory_ids: set[str] = set()
    try:
        inventory = json.loads(LEDGER_INVENTORY.read_text(encoding="utf-8"))
        inventory_ids = {row["id"] for row in inventory}
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        errors.append(f"cannot load exact ledger inventory IDs: {exc}")
    idea_files = sorted(IDEAS.glob("ECDLP-IDEA-*_hypothesis.md"))
    expected_ids = EXPECTED_IDS
    seen_ids: set[str] = set()
    file_by_id: dict[str, Path] = {}
    title_by_id: dict[str, str] = {}

    if len(idea_files) != EXPECTED_HYPOTHESIS_COUNT:
        errors.append(
            f"expected {EXPECTED_HYPOTHESIS_COUNT} hypothesis files, "
            f"found {len(idea_files)}"
        )

    for path in idea_files:
        if not FILE_RE.fullmatch(path.name):
            errors.append(f"invalid hypothesis filename: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        id_match = ID_RE.search(path.name)
        assert id_match is not None
        idea_id = f"ECDLP-IDEA-{id_match.group(1)}"
        if idea_id in seen_ids:
            errors.append(f"duplicate idea ID: {idea_id}")
        seen_ids.add(idea_id)
        file_by_id[idea_id] = path
        title_match = re.match(rf"^# {re.escape(idea_id)} — (.+)$", text, flags=re.MULTILINE)
        if title_match is None:
            errors.append(f"{path.name}: title/ID mismatch")
        else:
            title_by_id[idea_id] = title_match.group(1).strip()

        positions = []
        for heading in REQUIRED_HEADINGS:
            count = text.count(heading)
            if count != 1:
                errors.append(f"{path.name}: heading {heading!r} occurs {count} times")
            positions.append(text.find(heading))
        if all(pos >= 0 for pos in positions) and positions != sorted(positions):
            errors.append(f"{path.name}: required headings are out of order")

        for label in ("toy", "heuristic", "model-bound", "novelty-unverified"):
            if label not in text:
                errors.append(f"{path.name}: missing explicit label {label}")
        if "Breakthrough claim:" not in text or "none" not in section(text, REQUIRED_HEADINGS[0]).lower():
            errors.append(f"{path.name}: missing explicit no-breakthrough boundary")

        closest = section(text, "## Five closest ledger entries")
        entries = re.findall(
            r"(?m)^([1-9]\d*)\.\s+`((?:ledger|inputs)/[^`]+)`", closest
        )
        if len(entries) != 5 or [n for n, _ in entries] != [str(i) for i in range(1, 6)]:
            errors.append(f"{path.name}: closest-ledger section must contain exactly items 1..5")
        for _, ledger_path in entries:
            if not (REPO / ledger_path).is_file():
                errors.append(f"{path.name}: missing ledger reference {ledger_path}")
        validate_exact_inventory_neighbors(
            idea_id=idea_id,
            closest=closest,
            path=path,
            inventory_ids=inventory_ids,
            errors=errors,
        )

        literature = section(text, "## Closest primary literature")
        if len(re.findall(r"https?://", literature)) < 2:
            errors.append(f"{path.name}: fewer than two primary-literature links")

        cost = section(text, "## Full rho/BSGS cost model")
        for token in ("rho", "BSGS", "exponent", "memory"):
            if token.lower() not in cost.lower():
                errors.append(f"{path.name}: cost model missing {token!r}")

        action = section(text, "## Exactly one next executable action")
        action_items = re.findall(r"(?m)^\s*\d+\.\s+\S", action)
        if len(action_items) != 1:
            errors.append(f"{path.name}: expected exactly one numbered executable action")

        artifacts = section(text, "## Artifact plan")
        artifact_paths = re.findall(r"`(ideas/artifacts/[^`]+)`", artifacts)
        if not artifact_paths:
            errors.append(f"{path.name}: artifact plan has no ideas/artifacts path")
        for artifact in artifact_paths:
            if not artifact.startswith(f"ideas/artifacts/{idea_id}/"):
                errors.append(f"{path.name}: artifact path belongs to wrong ID: {artifact}")
            if not within_repo(artifact):
                errors.append(f"{path.name}: artifact path escapes repository: {artifact}")

    if seen_ids != expected_ids:
        errors.append(f"idea ID set mismatch: expected {sorted(expected_ids)}, got {sorted(seen_ids)}")

    registry_path = IDEAS / "idea_registry.tsv"
    registry_rows: list[dict[str, str]] = []
    if not registry_path.is_file():
        errors.append("missing ideas/idea_registry.tsv")
    else:
        with registry_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            registry_rows = list(reader)
            required_columns = {
                "idea_id", "title", "filename", "class", "risk_band", "status",
                "novelty_status", "top_lane", "semantic_fingerprint", "contract_path",
                "cohort",
            }
            if set(reader.fieldnames or []) != required_columns:
                errors.append(f"registry columns mismatch: {reader.fieldnames}")
        if len(registry_rows) != EXPECTED_HYPOTHESIS_COUNT:
            errors.append(
                f"registry must have {EXPECTED_HYPOTHESIS_COUNT} rows, "
                f"found {len(registry_rows)}"
            )
        row_ids = [row["idea_id"] for row in registry_rows]
        if set(row_ids) != expected_ids or len(row_ids) != len(set(row_ids)):
            errors.append("registry IDs are missing, duplicated, or unexpected")
        fingerprints = [row["semantic_fingerprint"] for row in registry_rows]
        if len(fingerprints) != len(set(fingerprints)):
            errors.append("registry semantic fingerprints are not unique")
        for row in registry_rows:
            idea_id = row["idea_id"]
            registered = IDEAS / row["filename"]
            if file_by_id.get(idea_id) != registered:
                errors.append(f"registry filename mismatch for {idea_id}: {row['filename']}")
            if title_by_id.get(idea_id) != row["title"]:
                errors.append(
                    f"registry title mismatch for {idea_id}: "
                    f"{row['title']!r} != {title_by_id.get(idea_id)!r}"
                )
            if row["status"] != "proposed_unapproved":
                errors.append(f"registry status is not proposed_unapproved for {idea_id}")
            if row["novelty_status"] != "novelty_unverified":
                errors.append(f"registry novelty status mismatch for {idea_id}")
            hypothesis = file_by_id.get(idea_id)
            if hypothesis is not None:
                status_text = section(hypothesis.read_text(encoding="utf-8"), REQUIRED_HEADINGS[0])
                class_match = re.search(r"(?m)^- Class: `([^`]+)`$", status_text)
                risk_match = re.search(r"(?m)^- Risk band: `([^`]+)`$", status_text)
                if class_match is None or class_match.group(1).replace("-", "_") != row["class"]:
                    errors.append(f"registry class mismatch for {idea_id}")
                if risk_match is None or risk_match.group(1).replace("-", "_") != row["risk_band"]:
                    errors.append(f"registry risk-band mismatch for {idea_id}")
            contract = row["contract_path"]
            if contract != "-":
                if not within_repo(f"ideas/{contract}") or not (IDEAS / contract).is_file():
                    errors.append(f"missing or unsafe contract path for {idea_id}: {contract}")
                else:
                    contract_text = (IDEAS / contract).read_text(encoding="utf-8")
                    contract_hypothesis = re.search(
                        r"(?m)^\s*hypothesis_id:\s*(ECDLP-IDEA-\d{3})\s*$",
                        contract_text,
                    )
                    if contract_hypothesis is None or contract_hypothesis.group(1) != idea_id:
                        errors.append(f"registry contract/hypothesis mismatch for {idea_id}")

        expected_top_lanes = {"conservative", "representation_changing", "high_risk"}
        cohorts = sorted({row["cohort"] for row in registry_rows})
        if cohorts != sorted(EXPECTED_COHORT_SIZES):
            errors.append(f"unexpected registry cohorts: {cohorts}")
        for cohort in cohorts:
            cohort_rows = [row for row in registry_rows if row["cohort"] == cohort]
            expected_size = EXPECTED_COHORT_SIZES[cohort]
            if len(cohort_rows) != expected_size:
                errors.append(
                    f"cohort {cohort} must have {expected_size} active ideas, "
                    f"found {len(cohort_rows)}"
                )
            top_rows = [
                row for row in cohort_rows if row["top_lane"] != "-"
            ]
            top_counts = Counter(row["top_lane"] for row in top_rows)
            if set(top_counts) != expected_top_lanes or any(
                count != 1 for count in top_counts.values()
            ):
                errors.append(
                    f"cohort {cohort} must select "
                    f"exactly one of each top lane: {dict(top_counts)}"
                )
            for row in top_rows:
                if row["contract_path"] == "-":
                    errors.append(f"top-lane idea has no contract: {row['idea_id']}")

    readme_path = IDEAS / "README.md"
    if not readme_path.is_file():
        errors.append("missing ideas/README.md")
    else:
        readme = readme_path.read_text(encoding="utf-8")
        for idea_id, path in file_by_id.items():
            if idea_id not in readme or path.name not in readme:
                errors.append(f"README missing {idea_id} or its filename")
                continue
            readme_row = re.search(
                rf"(?m)^\| \[{re.escape(idea_id)}\]\({re.escape(path.name)}\) "
                rf"\| ([^|]+) \|",
                readme,
            )
            if readme_row is None:
                errors.append(f"README has no parseable table row for {idea_id}")
            elif readme_row.group(1).strip() != title_by_id.get(idea_id):
                errors.append(
                    f"README title mismatch for {idea_id}: "
                    f"{readme_row.group(1).strip()!r} != {title_by_id.get(idea_id)!r}"
                )

    contract_ids: set[str] = set()
    handoff_ids: set[str] = set()
    contract_hypotheses: set[str] = set()
    for path in sorted((IDEAS / "contracts").glob("*.yaml")):
        if path.name.startswith("._"):
            continue
        text = path.read_text(encoding="utf-8")
        exp = re.search(r"(?m)^\s*id:\s*(EXP-ECDLP-IDEA-\d{3}-PREFLIGHT)\s*$", text)
        hyp = re.search(r"(?m)^\s*hypothesis_id:\s*(ECDLP-IDEA-\d{3})\s*$", text)
        if exp is None or hyp is None:
            errors.append(f"{path.name}: missing experiment or hypothesis ID")
            continue
        if exp.group(1) in contract_ids:
            errors.append(f"duplicate experiment contract ID: {exp.group(1)}")
        contract_ids.add(exp.group(1))
        if hyp.group(1) in contract_hypotheses:
            errors.append(f"duplicate contracted hypothesis ID: {hyp.group(1)}")
        contract_hypotheses.add(hyp.group(1))
        if "status: review_required" not in text or "approved_by: null" not in text:
            errors.append(f"{path.name}: contract must remain review_required/unapproved")
        for field in (
            "inputs:",
            "controls:",
            "independent_variables:",
            "metrics:",
            "replication:",
            "budget:",
            "stopping_rules:",
            "invalidation_rules:",
            "success_criterion:",
            "falsification_criterion:",
            "required_artifacts:",
        ):
            if field not in text:
                errors.append(f"{path.name}: lifecycle field missing: {field}")
        handoff = re.search(r"(?m)^\s*id:\s*(TASK-\d{8}-\d{3})\s*$", text)
        if handoff is None:
            errors.append(f"{path.name}: missing handoff ID")
        elif handoff.group(1) in handoff_ids:
            errors.append(f"duplicate handoff ID: {handoff.group(1)}")
        else:
            handoff_ids.add(handoff.group(1))
        artifacts = re.findall(r"(?m)^\s*-\s+(ideas/artifacts/\S+)\s*$", text)
        if not artifacts:
            errors.append(f"{path.name}: no required artifact paths")
        for artifact in artifacts:
            if not within_repo(artifact):
                errors.append(f"{path.name}: unsafe required artifact path {artifact}")
            if not artifact.startswith(f"ideas/artifacts/{hyp.group(1)}/"):
                errors.append(f"{path.name}: artifact path belongs to wrong hypothesis: {artifact}")
        if "All required artifact paths exist and are checksummed." not in text:
            errors.append(f"{path.name}: completion gate does not require artifact checksums")

    if len(contract_ids) != EXPECTED_CONTRACT_COUNT:
        errors.append(
            f"expected exactly {EXPECTED_CONTRACT_COUNT} top-lane contracts, "
            f"found {len(contract_ids)}"
        )

    registered_top_ids = {
        row["idea_id"] for row in registry_rows if row["top_lane"] != "-"
    }
    if contract_hypotheses != registered_top_ids:
        errors.append(
            "contracted hypotheses do not match registered top-lane ideas: "
            f"contracts={sorted(contract_hypotheses)}, top={sorted(registered_top_ids)}"
        )

    reviews = IDEAS / "reviews"
    if not (reviews / REQUIRED_DEDUP_REPORT).is_file():
        errors.append(f"missing current deduplication report {REQUIRED_DEDUP_REPORT}")
    if not (reviews / REQUIRED_REDTEAM_REPORT).is_file():
        errors.append(f"missing current independent review {REQUIRED_REDTEAM_REPORT}")
    if not list(reviews.glob("DEDUP-????????T??????-????.md")):
        errors.append("missing timestamped deduplication report")
    if not list(reviews.glob("REDTEAM-????????T??????-????.md")):
        errors.append("missing timestamped independent red-team report")

    artifact_readme = IDEAS / "artifacts" / "README.md"
    if not artifact_readme.is_file():
        errors.append("missing ideas/artifacts/README.md")
    else:
        artifact_index_text = artifact_readme.read_text(encoding="utf-8")
        indexed_artifacts = re.findall(
            r"(?m)^\| `ECDLP-IDEA-\d{3}` \| \[`[^`]+`\]\(([^)]+)\) "
            r"\| `([0-9a-f]{64})` \|",
            artifact_index_text,
        )
        indexed_paths = [relative for relative, _ in indexed_artifacts]
        duplicates = sorted(
            relative
            for relative, count in Counter(indexed_paths).items()
            if count > 1
        )
        if duplicates:
            errors.append(f"duplicate artifact index paths: {duplicates}")
        for relative, expected_sha in indexed_artifacts:
            artifact_path = IDEAS / "artifacts" / relative
            if not artifact_path.is_file():
                errors.append(f"indexed artifact is missing: {relative}")
                continue
            actual_sha = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            if actual_sha != expected_sha:
                errors.append(
                    f"indexed artifact hash mismatch for {relative}: "
                    f"expected {expected_sha}, got {actual_sha}"
                )
        actual_artifacts = {
            path.relative_to(IDEAS / "artifacts").as_posix()
            for path in (IDEAS / "artifacts").rglob("*")
            if path.is_file()
            and path.name != "README.md"
            and not path.name.startswith("._")
        }
        if set(indexed_paths) != actual_artifacts:
            errors.append(
                "artifact index coverage mismatch: "
                f"unindexed={sorted(actual_artifacts - set(indexed_paths))}, "
                f"missing={sorted(set(indexed_paths) - actual_artifacts)}"
            )

    for relative, expected_sha in P1514_V2_ARTIFACT_HASHES.items():
        path = IDEAS / "artifacts" / relative
        if not path.is_file():
            errors.append(f"missing P1514 V2 evidence: {relative}")
            continue
        actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            errors.append(
                f"P1514 V2 evidence hash mismatch for {relative}: "
                f"expected {expected_sha}, got {actual_sha}"
            )

    p1514_verifier = (
        IDEAS / "artifacts/ECDLP-IDEA-133/verify_nonlinear_apolar_theorem.py"
    )
    if p1514_verifier.is_file():
        verifier_text = p1514_verifier.read_text(encoding="utf-8")
        if "/Volumes/Volume/autolab" in verifier_text:
            errors.append("P1514 verifier escaped the crypto-autoresearcher boundary")
        for token in (
            "require_inside_repository",
            'theorem_ws = " ".join(theorem.split())',
            'correction_ws = " ".join(correction.split())',
            "does not make `5B-3` a compulsory minimum",
            "reusable_mitm_charged_as_streamed_campaign",
            "streamed_mitm_charged_as_reusable_campaign",
            "sufficient_cutoff_is_compulsory_minimum",
            "joint_eigenvalues_recover_nonreduced_multiplicity",
        ):
            if token not in verifier_text:
                errors.append(f"P1514 verifier is missing scope mutation {token}")

    p1514_ledger = LEDGER / "FINDING-PF-IC-001.md"
    if p1514_ledger.is_file() and "### ECFG-P1514-V2" not in p1514_ledger.read_text(
        encoding="utf-8"
    ):
        errors.append("ledger is missing append-only ECFG-P1514-V2 correction")

    focus_queue_path = REPO / "focus/focus_queue_20260717.json"
    focus_plan_path = REPO / "focus/current_plan.json"
    if not focus_queue_path.is_file() or not focus_plan_path.is_file():
        errors.append("missing live focus queue or generated plan")
    else:
        focus_queue = json.loads(focus_queue_path.read_text(encoding="utf-8"))
        focus_plan = json.loads(focus_plan_path.read_text(encoding="utf-8"))
        p1514_claims = [
            claim
            for claim in focus_queue.get("claims", [])
            if claim.get("id") == "CLM-P1514-NONLINEAR-APOLAR-FLAT-EXTENSION"
        ]
        p1514_candidates = [
            candidate
            for candidate in focus_queue.get("candidates", [])
            if candidate.get("id") == "P1514"
        ]
        p1514_runs = [
            run
            for run in focus_queue.get("runs", [])
            if run.get("experiment_id") == "P1514"
        ]
        if len(p1514_claims) != 1:
            errors.append("live focus queue has an inconsistent P1514 claim count")
        else:
            claim = p1514_claims[0]
            if claim.get("verdict") != "open" or claim.get("independently_verified"):
                errors.append("live P1514 claim is not open and unverified")
            if claim.get("evidence_runs"):
                errors.append("live P1514 open claim improperly cites completed runs")
        if len(p1514_candidates) != 1:
            errors.append("live focus queue has an inconsistent P1514 candidate count")
        else:
            candidate = p1514_candidates[0]
            if candidate.get("outcome", {}).get("independently_verified"):
                errors.append("live P1514 candidate is incorrectly independently verified")
            if candidate.get("resource_estimate", {}).get("maximum_runs") != 0:
                errors.append("live P1514 candidate does not preserve the zero-run gate")
        external_p1514_artifacts = [
            artifact
            for run in p1514_runs
            for artifact in run.get("artifacts", [])
            if artifact.startswith("/Volumes/Volume/autolab")
        ]
        if external_p1514_artifacts:
            errors.append(
                f"live P1514 runs cite external artifacts: {external_p1514_artifacts}"
            )
        planned_ids = {
            run.get("id") for run in p1514_runs if run.get("status") == "planned"
        }
        if "RUN-P1514-APOLAR-SCOPE-CORRECTION-AUDIT-V4-INREPO" not in planned_ids:
            errors.append("live P1514 repository-confined audit is not planned/unrun")
        queue_digest = hashlib.sha256(
            json.dumps(
                focus_queue,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("ascii")
        ).hexdigest()
        if focus_plan.get("source_queue_sha256") != queue_digest:
            errors.append("generated focus plan is stale relative to the live queue")

    rejected_dir = IDEAS / "rejected"
    rejected_ids: set[str] = set()
    rejected_id_list: list[str] = []
    for path in sorted(rejected_dir.glob("ECDLP-IDEA-*_hypothesis.md")):
        if not FILE_RE.fullmatch(path.name):
            errors.append(f"invalid rejected hypothesis filename: {path.name}")
            continue
        match = ID_RE.search(path.name)
        if match is not None:
            idea_id = f"ECDLP-IDEA-{match.group(1)}"
            rejected_ids.add(idea_id)
            rejected_id_list.append(idea_id)
            text = path.read_text(encoding="utf-8")
            title_match = re.match(
                rf"^# {re.escape(idea_id)} — (.+)$", text, flags=re.MULTILINE
            )
            if title_match is None:
                errors.append(f"{path.name}: rejected title/ID mismatch")
            positions = []
            for heading in REQUIRED_HEADINGS:
                count = text.count(heading)
                if count != 1:
                    errors.append(
                        f"{path.name}: rejected heading {heading!r} occurs {count} times"
                    )
                positions.append(text.find(heading))
            if all(pos >= 0 for pos in positions) and positions != sorted(positions):
                errors.append(f"{path.name}: rejected required headings are out of order")
            for label in ("toy", "heuristic", "model-bound", "novelty-unverified"):
                if label not in text:
                    errors.append(f"{path.name}: rejected record missing label {label}")
            if (
                "Breakthrough claim:" not in text
                or "none" not in section(text, REQUIRED_HEADINGS[0]).lower()
            ):
                errors.append(f"{path.name}: rejected record missing no-breakthrough boundary")
            closest = section(text, "## Five closest ledger entries")
            entries = re.findall(
                r"(?m)^([1-9]\d*)\.\s+`((?:ledger|inputs)/[^`]+)`", closest
            )
            if len(entries) != 5 or [n for n, _ in entries] != [
                str(i) for i in range(1, 6)
            ]:
                errors.append(
                    f"{path.name}: rejected closest-ledger section must contain exactly items 1..5"
                )
            for _, ledger_path in entries:
                if not (REPO / ledger_path).is_file():
                    errors.append(
                        f"{path.name}: rejected missing ledger reference {ledger_path}"
                    )
            validate_exact_inventory_neighbors(
                idea_id=idea_id,
                closest=closest,
                path=path,
                inventory_ids=inventory_ids,
                errors=errors,
            )
            if len(re.findall(r"https?://", section(text, "## Closest primary literature"))) < 2:
                errors.append(f"{path.name}: rejected record has fewer than two literature links")
            cost = section(text, "## Full rho/BSGS cost model")
            for token in ("rho", "BSGS", "exponent", "memory"):
                if token.lower() not in cost.lower():
                    errors.append(
                        f"{path.name}: rejected cost model missing {token!r}"
                    )
            action = section(text, "## Exactly one next executable action")
            if len(re.findall(r"(?m)^\s*\d+\.\s+\S", action)) != 1:
                errors.append(
                    f"{path.name}: rejected record must retain exactly one numbered action"
                )
            artifacts = section(text, "## Artifact plan")
            artifact_paths = re.findall(r"`(ideas/artifacts/[^`]+)`", artifacts)
            if not artifact_paths:
                errors.append(f"{path.name}: rejected artifact plan has no path")
            for artifact in artifact_paths:
                if not artifact.startswith(f"ideas/artifacts/{idea_id}/"):
                    errors.append(
                        f"{path.name}: rejected artifact path belongs to wrong ID: {artifact}"
                    )
                if not within_repo(artifact):
                    errors.append(
                        f"{path.name}: rejected artifact path escapes repository: {artifact}"
                    )
    duplicate_rejected_ids = [
        idea_id for idea_id, count in Counter(rejected_id_list).items() if count > 1
    ]
    if duplicate_rejected_ids:
        errors.append(f"duplicate rejected idea IDs: {sorted(duplicate_rejected_ids)}")
    if rejected_ids != EXPECTED_REJECTED_IDS:
        errors.append(
            f"rejected evidence ID mismatch: expected {sorted(EXPECTED_REJECTED_IDS)}, "
            f"got {sorted(rejected_ids)}"
        )
    if rejected_ids & seen_ids:
        errors.append(f"active/rejected ID overlap: {sorted(rejected_ids & seen_ids)}")
    if not (rejected_dir / "README.md").is_file():
        errors.append("missing ideas/rejected/README.md")

    deferred_dir = IDEAS / "deferred"
    deferred_ids: set[str] = set()
    deferred_id_list: list[str] = []
    for path in sorted(deferred_dir.glob("ECDLP-IDEA-*_hypothesis.md")):
        if not FILE_RE.fullmatch(path.name):
            errors.append(f"invalid deferred hypothesis filename: {path.name}")
            continue
        match = ID_RE.search(path.name)
        if match is None:
            continue
        idea_id = f"ECDLP-IDEA-{match.group(1)}"
        deferred_ids.add(idea_id)
        deferred_id_list.append(idea_id)
        text = path.read_text(encoding="utf-8")
        title_match = re.match(
            rf"^# {re.escape(idea_id)} — (.+)$", text, flags=re.MULTILINE
        )
        if title_match is None:
            errors.append(f"{path.name}: deferred title/ID mismatch")
        positions = []
        for heading in REQUIRED_HEADINGS:
            count = text.count(heading)
            if count != 1:
                errors.append(
                    f"{path.name}: deferred heading {heading!r} occurs {count} times"
                )
            positions.append(text.find(heading))
        if all(pos >= 0 for pos in positions) and positions != sorted(positions):
            errors.append(f"{path.name}: deferred required headings are out of order")
        for label in ("toy", "heuristic", "model-bound", "novelty-unverified"):
            if label not in text:
                errors.append(f"{path.name}: deferred record missing label {label}")
        if (
            "Breakthrough claim:" not in text
            or "none" not in section(text, REQUIRED_HEADINGS[0]).lower()
        ):
            errors.append(f"{path.name}: deferred record missing no-breakthrough boundary")
        closest = section(text, "## Five closest ledger entries")
        entries = re.findall(
            r"(?m)^([1-9]\d*)\.\s+`((?:ledger|inputs)/[^`]+)`", closest
        )
        if len(entries) != 5 or [n for n, _ in entries] != [
            str(i) for i in range(1, 6)
        ]:
            errors.append(
                f"{path.name}: deferred closest-ledger section must contain exactly items 1..5"
            )
        for _, ledger_path in entries:
            if not (REPO / ledger_path).is_file():
                errors.append(
                    f"{path.name}: deferred missing ledger reference {ledger_path}"
                )
        validate_exact_inventory_neighbors(
            idea_id=idea_id,
            closest=closest,
            path=path,
            inventory_ids=inventory_ids,
            errors=errors,
        )
        if len(re.findall(r"https?://", section(text, "## Closest primary literature"))) < 2:
            errors.append(f"{path.name}: deferred record has fewer than two literature links")
        cost = section(text, "## Full rho/BSGS cost model")
        for token in ("rho", "BSGS", "exponent", "memory"):
            if token.lower() not in cost.lower():
                errors.append(f"{path.name}: deferred cost model missing {token!r}")
        action = section(text, "## Exactly one next executable action")
        if len(re.findall(r"(?m)^\s*\d+\.\s+\S", action)) != 1:
            errors.append(
                f"{path.name}: deferred record must retain exactly one numbered action"
            )
        artifacts = section(text, "## Artifact plan")
        artifact_paths = re.findall(r"`(ideas/artifacts/[^`]+)`", artifacts)
        if not artifact_paths:
            errors.append(f"{path.name}: deferred artifact plan has no path")
        for artifact in artifact_paths:
            if not artifact.startswith(f"ideas/artifacts/{idea_id}/"):
                errors.append(
                    f"{path.name}: deferred artifact path belongs to wrong ID: {artifact}"
                )
            if not within_repo(artifact):
                errors.append(
                    f"{path.name}: deferred artifact path escapes repository: {artifact}"
                )
    duplicate_deferred_ids = [
        idea_id for idea_id, count in Counter(deferred_id_list).items() if count > 1
    ]
    if duplicate_deferred_ids:
        errors.append(f"duplicate deferred idea IDs: {sorted(duplicate_deferred_ids)}")
    if deferred_ids != EXPECTED_DEFERRED_IDS:
        errors.append(
            f"deferred evidence ID mismatch: expected {sorted(EXPECTED_DEFERRED_IDS)}, "
            f"got {sorted(deferred_ids)}"
        )
    if deferred_ids & (seen_ids | rejected_ids):
        errors.append(
            "active/rejected/deferred ID overlap: "
            f"{sorted(deferred_ids & (seen_ids | rejected_ids))}"
        )
    if not (deferred_dir / "README.md").is_file():
        errors.append("missing ideas/deferred/README.md")
    complete_ids = seen_ids | rejected_ids | deferred_ids
    expected_complete_ids = {
        *(f"ECDLP-IDEA-{i:03d}" for i in range(1, 411)),
        # cohort 20260809-a, minted above the retired preallocation ceiling (433)
        "ECDLP-IDEA-434",
        "ECDLP-IDEA-435",
        "ECDLP-IDEA-436",
    }
    if complete_ids != expected_complete_ids:
        errors.append(
            "complete active/rejected/deferred ID coverage is not exactly "
            "001..410 plus cohort 20260809-a"
        )

    retired_contracts = sorted(
        path
        for path in (rejected_dir / "contracts").glob("*.yaml")
        if not path.name.startswith("._")
    )
    if len(retired_contracts) != EXPECTED_RETIRED_CONTRACT_COUNT:
        errors.append(
            f"expected {EXPECTED_RETIRED_CONTRACT_COUNT} retired contracts, "
            f"found {len(retired_contracts)}"
        )
    new_retired_ids: set[str] = set()
    for path in retired_contracts:
        text = path.read_text(encoding="utf-8")
        hyp = re.search(r"(?m)^\s*hypothesis_id:\s*(ECDLP-IDEA-\d{3})\s*$", text)
        if hyp is None or hyp.group(1) not in EXPECTED_NEW_RETIRED_CONTRACT_IDS:
            continue
        idea_id = hyp.group(1)
        new_retired_ids.add(idea_id)
        if "retired_from_dispatch: true" not in text:
            errors.append(f"{path.name}: new retired contract lacks dispatch retirement")
        if "status: review_required" not in text or "approved_by: null" not in text:
            errors.append(f"{path.name}: retired draft lost review_required/unapproved state")
        if idea_id in EXPECTED_CURRENT_RETIRED_FORMULAS and text.count("maximum_runs: 0") < 2:
            errors.append(f"{path.name}: retired draft must permit zero experiment and handoff runs")
        artifacts = re.findall(r"(?m)^\s*-\s+(ideas/artifacts/\S+)\s*$", text)
        if not artifacts:
            errors.append(f"{path.name}: retired draft has no planned artifact paths")
        for artifact in artifacts:
            if not within_repo(artifact):
                errors.append(f"{path.name}: unsafe retired artifact path {artifact}")
            if not artifact.startswith(f"ideas/artifacts/{idea_id}/"):
                errors.append(
                    f"{path.name}: retired artifact path belongs to wrong hypothesis: "
                    f"{artifact}"
                )
        prospective_gate = (
            "Any artifact actually produced is ID-scoped and checksummed; "
            "prospective paths need not exist under this retired draft."
        )
        if idea_id in {
            "ECDLP-IDEA-115",
            "ECDLP-IDEA-117",
            "ECDLP-IDEA-119",
            "ECDLP-IDEA-128",
            "ECDLP-IDEA-129",
            "ECDLP-IDEA-133",
            "ECDLP-IDEA-134",
            "ECDLP-IDEA-135",
            "ECDLP-IDEA-145",
            "ECDLP-IDEA-146",
            "ECDLP-IDEA-149",
            "ECDLP-IDEA-150",
            "ECDLP-IDEA-170",
            "ECDLP-IDEA-174",
            "ECDLP-IDEA-180",
            "ECDLP-IDEA-182",
            "ECDLP-IDEA-183",
            "ECDLP-IDEA-192",
            "ECDLP-IDEA-194",
            "ECDLP-IDEA-195",
            "ECDLP-IDEA-202",
            "ECDLP-IDEA-209",
            "ECDLP-IDEA-211",
            "ECDLP-IDEA-212",
            "ECDLP-IDEA-218",
            "ECDLP-IDEA-219",
            "ECDLP-IDEA-220",
            "ECDLP-IDEA-230",
            "ECDLP-IDEA-231",
            "ECDLP-IDEA-233",
            "ECDLP-IDEA-242",
            "ECDLP-IDEA-244",
            "ECDLP-IDEA-250",
            "ECDLP-IDEA-254",
            "ECDLP-IDEA-255",
            "ECDLP-IDEA-263",
            "ECDLP-IDEA-266",
            "ECDLP-IDEA-270",
            "ECDLP-IDEA-276",
            "ECDLP-IDEA-278",
            "ECDLP-IDEA-279",
            "ECDLP-IDEA-287",
            "ECDLP-IDEA-290",
            "ECDLP-IDEA-296",
            "ECDLP-IDEA-300",
            "ECDLP-IDEA-304",
            "ECDLP-IDEA-309",
            "ECDLP-IDEA-313",
            "ECDLP-IDEA-320",
            "ECDLP-IDEA-322",
            "ECDLP-IDEA-323",
            "ECDLP-IDEA-324",
            "ECDLP-IDEA-326",
            "ECDLP-IDEA-327",
            "ECDLP-IDEA-333",
            "ECDLP-IDEA-338",
            "ECDLP-IDEA-341",
            "ECDLP-IDEA-349",
            "ECDLP-IDEA-350",
            "ECDLP-IDEA-354",
            "ECDLP-IDEA-360",
            "ECDLP-IDEA-362",
            "ECDLP-IDEA-367",
            "ECDLP-IDEA-373",
            "ECDLP-IDEA-374",
            "ECDLP-IDEA-378",
            "ECDLP-IDEA-379",
            "ECDLP-IDEA-386",
            "ECDLP-IDEA-388",
            "ECDLP-IDEA-391",
            "ECDLP-IDEA-398",
            "ECDLP-IDEA-399",
            "ECDLP-IDEA-400",
            "ECDLP-IDEA-410",
        }:
            if prospective_gate not in text:
                errors.append(
                    f"{path.name}: retired completion gate mishandles prospective artifacts"
                )
        elif "All required artifact paths exist and are checksummed." not in text:
            errors.append(
                f"{path.name}: retired completion gate lacks artifact checksums"
            )
        evidence_inputs = re.findall(
            r"(?m)^\s*-\s+(ideas/(?:rejected|deferred)/ECDLP-IDEA-\S+\.md)\s*$",
            text,
        )
        contract_inputs = re.findall(
            r"(?m)^\s*-\s+(ideas/rejected/contracts/ECDLP-EXP-CONTRACT-\S+\.yaml)\s*$",
            text,
        )
        if len(evidence_inputs) != 1 or not (REPO / evidence_inputs[0]).is_file():
            errors.append(f"{path.name}: retired hypothesis evidence path is inconsistent")
        elif idea_id in EXPECTED_CURRENT_RETIRED_FORMULAS:
            hypothesis_text = (REPO / evidence_inputs[0]).read_text(encoding="utf-8")
            for formula in EXPECTED_CURRENT_RETIRED_FORMULAS[idea_id]:
                if text.count(formula) != 1 or hypothesis_text.count(formula) != 1:
                    errors.append(
                        f"{path.name}: cost equation is not verbatim-identical to {idea_id}"
                    )
            for replication_token in (
                "future_field_bit_sizes: [14, 16, 18, 20]",
                'future_curve_indices_per_size: "0..19"',
                "future_independent_curves_per_size: 20",
                "future_total_curve_size_cells: 80",
                "future_prng: ChaCha20-IETF",
                'future_prng_nonce_hex: "000000000000000000000000"',
                "future_prng_initial_counter: 0",
                "future_byte_mapping: unsigned_big_endian_rejection_sampling",
                "future_independently_verified_accepted_rows_at_each_of_two_largest_sizes: 1000",
                "future_relation_attempt_ceiling_at_each_of_two_largest_sizes: 1000000",
                "future_target_descents_at_each_of_two_largest_sizes: 100",
            ):
                if replication_token not in text:
                    errors.append(
                        f"{path.name}: missing frozen replication token {replication_token!r}"
                    )
            hypothesis_artifacts = set(
                re.findall(r"`(ideas/artifacts/[^`]+)`", section(hypothesis_text, "## Artifact plan"))
            )
            if not set(artifacts).issubset(hypothesis_artifacts):
                errors.append(f"{path.name}: contract artifacts are not a subset of its hypothesis plan")
            next_action = section(hypothesis_text, "## Exactly one next executable action")
            if not set(re.findall(r"`(ideas/artifacts/[^`]+)`", next_action)) <= set(artifacts):
                errors.append(f"{path.name}: next-action artifact is absent from the contract")
        if len(contract_inputs) != 1 or (REPO / contract_inputs[0]) != path:
            errors.append(f"{path.name}: retired contract self-path is inconsistent")
    if new_retired_ids != EXPECTED_NEW_RETIRED_CONTRACT_IDS:
        errors.append(
            "new retired-contract ID mismatch: "
            f"expected {sorted(EXPECTED_NEW_RETIRED_CONTRACT_IDS)}, "
            f"got {sorted(new_retired_ids)}"
        )

    appledouble = sorted(path.relative_to(IDEAS) for path in IDEAS.rglob("._*"))
    if appledouble:
        errors.append(f"AppleDouble sidecars remain under ideas/: {appledouble}")

    if errors:
        print("idea corpus validation FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"idea corpus validation OK: {len(idea_files)} hypotheses, "
        f"{len(registry_rows)} registry rows, {len(contract_ids)} contracts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
