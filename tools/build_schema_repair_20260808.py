#!/usr/bin/env python3
"""Build hash-pinned schema corrections without modifying archived records.

This is intentionally a one-shot, deterministic migration.  It only accepts
the audited source paths below, preserves their substantive fields, and writes
complete replacement records outside every validator discovery glob.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ledger/corrections/schema-supersessions/20260808"
REGISTRY = ROOT / "tools/schema_supersession_registry.yaml"

REPLACEMENT_IDS = {
    "ledger/proposals/IDEA-ISO-7f3e2d.yaml": "IDEA-20260808-5e5bbf",
    "ledger/proposals/IDEA-ISO-a4c8e1.yaml": "IDEA-20260808-de0c11",
    "ledger/proposals/IDEA-ISO-f9b2d3.yaml": "IDEA-20260808-8a63b8",
    "experiments/EXP-P13-NC2b/specification.yaml": "EXP-PTH-9f1440",
    "experiments/EXP-P13-NC2d/specification.yaml": "EXP-PTH-9980dc",
    "experiments/EXP-P13-NC36/specification.yaml": "EXP-PTH-48eee1",
}

REDIRECTS = {
    "ledger/hypotheses/H-XOR-YIELD.yaml": (
        "ledger/hypotheses/H-XOR-d1a480.yaml", "H-XOR-d1a480"),
}

YAML_SCHEMA_PATHS = [
    "ledger/proposals/IDEA-ISO-7f3e2d.yaml",
    "ledger/proposals/IDEA-ISO-a4c8e1.yaml",
    "ledger/proposals/IDEA-ISO-f9b2d3.yaml",
    "ledger/hypotheses/H-MLDSA-c7b4e8.yaml",
    "ledger/hypotheses/H-MLDSA-d1e509.yaml",
    "ledger/hypotheses/H-MLDSA-f3a291.yaml",
    "ledger/evidence/EV-AES-a47618.yaml",
    "ledger/evidence/EV-AES-c66a80.yaml",
    "ledger/evidence/EV-ECDLP-1d522d.yaml",
    "ledger/evidence/EV-ECDLP-5500b5.yaml",
    "ledger/evidence/EV-ECDLP-a2d5a4.yaml",
    "ledger/evidence/EV-HAWK-21edba.yaml",
    "ledger/evidence/EV-HAWK-68b8b6.yaml",
    "ledger/evidence/EV-HAWK-af783e.yaml",
    "ledger/evidence/EV-HAWK-c99848.yaml",
    "ledger/evidence/EV-MLDSA-32d752.yaml",
    "ledger/evidence/EV-MLDSA-56e35b.yaml",
    "ledger/evidence/EV-MLDSA-faf2ec.yaml",
    "ledger/evidence/EV-MLKEM-4a9cfe.yaml",
    "ledger/evidence/EV-SSI-59f7a2.yaml",
    "ledger/evidence/EV-SSI-17c854.yaml",
    "ledger/evidence/EV-SSI-fcda7e.yaml",
    "ledger/evidence/EV-WESO-b6ceff.yaml",
    "ledger/decisions/DEC-20260804-e19a65.yaml",
    "ledger/decisions/DEC-20260804-a6bb36.yaml",
    "ledger/decisions/DEC-20260804-cfe4d0.yaml",
    "ledger/decisions/DEC-20260805-0d59ff.yaml",
    "ledger/decisions/DEC-20260805-364e9e.yaml",
    "ledger/decisions/DEC-20260805-4843d6.yaml",
    "ledger/decisions/DEC-20260805-48b52e.yaml",
    "ledger/decisions/DEC-20260805-64abe7.yaml",
    "ledger/decisions/DEC-20260805-661790.yaml",
    "ledger/decisions/DEC-20260805-70450a.yaml",
    "ledger/decisions/DEC-20260805-77a735.yaml",
    "ledger/decisions/DEC-20260805-79d745.yaml",
    "ledger/decisions/DEC-20260805-a62164.yaml",
    "ledger/decisions/DEC-20260805-ae4a96.yaml",
    "ledger/decisions/DEC-20260805-bdcb53.yaml",
    "ledger/decisions/DEC-20260805-d4b182.yaml",
    "ledger/decisions/DEC-20260805-ed4cd3.yaml",
    "ledger/decisions/DEC-20260806-c058ac.yaml",
    "ledger/decisions/DEC-20260807-b54f28.yaml",
    "ledger/decisions/DEC-20260807-fc6df4.yaml",
    "ledger/decisions/DEC-20260807-fd61e4.yaml",
    "ledger/decisions/DEC-20260807-faea68.yaml",
    "experiments/EXP-ECDLP-03a8c9/specification.yaml",
    "experiments/EXP-ECDLP-1ed445/specification.yaml",
    "experiments/EXP-P13-NC2b/specification.yaml",
    "experiments/EXP-P13-NC2d/specification.yaml",
    "experiments/EXP-P13-NC36/specification.yaml",
    "experiments/EXP-SMTH-e932e8/specification.yaml",
    "experiments/EXP-SSI-6a2619/specification.yaml",
    "experiments/EXP-SSI-eca132/specification.yaml",
    "experiments/EXP-YIELD-004/specification.yaml",
    "ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-a67152.yaml",
    "ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-b3f591.yaml",
    "ledger/goals/GOAL-ECDLP-001/checkpoints/BATCH-fd61e4.yaml",
]

KNOWLEDGE_PATHS = [
    "knowledge/findings/KN-FIND-194294.md",
    "knowledge/findings/KN-FIND-4e7a92.md",
    "knowledge/findings/KN-FIND-528ca0.md",
    "knowledge/findings/KN-FIND-720727.md",
    "knowledge/findings/KN-FIND-ac28ed.md",
    "knowledge/findings/KN-FIND-d1c853.md",
    "knowledge/findings/KN-FIND-ff4a46.md",
    "knowledge/literature/KN-LIT-180ad5.md",
    "knowledge/literature/KN-LIT-340675.md",
    "knowledge/literature/KN-LIT-4dadec.md",
    "knowledge/literature/KN-LIT-4f3b80.md",
    "knowledge/literature/KN-LIT-8ce0b5.md",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_archived_yaml(relative: str) -> dict:
    text = (ROOT / relative).read_text(encoding="utf-8")
    if relative == "ledger/evidence/EV-HAWK-af783e.yaml":
        text = text.replace(
            "    - Claim 2.1 uniqueness proof: circular norm argument; correct repair is\n"
            "      \"by minimality of exact denominator\"\n",
            "    - >-\n      Claim 2.1 uniqueness proof: circular norm argument; correct repair is\n"
            "      by minimality of exact denominator\n",
        ).replace(
            "    - Claim 2.2 local-global citation: Hasse-Minkowski quoted for an integral\n"
            "      result; correct citation is Eichler's theorem (strong approximation)\n",
            "    - >-\n      Claim 2.2 local-global citation: Hasse-Minkowski quoted for an integral\n"
            "      result; correct citation is Eichler's theorem (strong approximation)\n",
        )
    if relative in {
        "ledger/decisions/DEC-20260805-364e9e.yaml",
        "ledger/decisions/DEC-20260805-48b52e.yaml",
        "ledger/decisions/DEC-20260805-661790.yaml",
    }:
        start = text.index("  findings:\n")
        end = text.index("\n  decisions:", start)
        block = text[start + len("  findings:\n"):end]
        block = "\n".join("  " + line for line in block.splitlines())
        text = text[:start] + "  findings: |-\n" + block + text[end:]
    if relative == "experiments/EXP-P13-NC2b/specification.yaml":
        lines = []
        for line in text.splitlines():
            match = re.match(
                r'(\s*)- field: ("[^"]+");\s*log2p: ([^;]+);\s*log2_B_opt: (.+)',
                line)
            if match:
                indent, field, log2p, log2b = match.groups()
                lines.extend([
                    f"{indent}- field: {field}",
                    f"{indent}  log2p: {log2p.strip()}",
                    f"{indent}  log2_B_opt: {log2b.strip()}",
                ])
            else:
                lines.append(line)
        text = "\n".join(lines) + "\n"
    if relative == "experiments/EXP-P13-NC2d/specification.yaml":
        text = text.replace(
            "      - |alpha_hat(ell) - alpha_null(ell)| per ell",
            "      - \"|alpha_hat(ell) - alpha_null(ell)| per ell\"",
        ).replace(
            "      - |alpha_primary - alpha_null|",
            "      - \"|alpha_primary - alpha_null|\"",
        ).replace(
            '      - "FC-4 FIRED" or "FC-4 DID NOT FIRE" as a single line',
            "      - 'FC-4 FIRED or FC-4 DID NOT FIRE as a single line'",
        ).replace(
            '      - "RERANK TRIGGER FIRES" or "RERANK TRIGGER DOES NOT FIRE"',
            "      - 'RERANK TRIGGER FIRES or RERANK TRIGGER DOES NOT FIRE'",
        )
    doc = yaml.safe_load(text)
    if not isinstance(doc, dict):
        raise ValueError(f"{relative}: expected mapping")
    return doc


def repair_yaml(relative: str) -> dict:
    doc = parse_archived_yaml(relative)
    if relative.startswith("ledger/proposals/"):
        body = doc["idea"]
        body["id"] = REPLACEMENT_IDS[relative]
    elif relative.startswith("ledger/hypotheses/"):
        body = doc["hypothesis"]
        body.setdefault("statement", body.get("title"))
    elif relative.startswith("ledger/evidence/"):
        if "evidence" not in doc:
            flat = dict(doc)
            rec_id = flat.pop("evidence_id")
            doc = {"evidence": {"id": rec_id, **flat}}
        body = doc["evidence"]
        if "hypothesis_id" not in body or (
                body.get("hypothesis_id") is None
                and not (body.get("hypothesis_id_note") or body.get("hypothesis_note"))):
            body["hypothesis_id"] = None
            body["hypothesis_id_note"] = (
                "The archived record did not bind a hypothesis; this correction "
                "does not manufacture one.")
        body.setdefault("run_ids", [])
        body.setdefault("direction", "neutral")
        body.setdefault("strength", "inconclusive")
        body.setdefault("claim_tier", "toy")
        proof = body.get("proof_status")
        if proof not in {"certificate", "derivation", "empirical_only", "not_applicable"}:
            kind = str(body.get("type") or "").lower()
            body["proof_status"] = (
                "derivation" if any(x in kind for x in ("derivation", "mathematical"))
                else "empirical_only" if any(x in kind for x in ("measurement", "empirical", "experiment"))
                else "not_applicable")
        if not isinstance(body.get("proof_refs"), list):
            refs = body.get("certificate_refs")
            body["proof_refs"] = list(refs) if isinstance(refs, list) else []
        if relative in {
            "ledger/evidence/EV-SSI-17c854.yaml",
            "ledger/evidence/EV-SSI-fcda7e.yaml",
        }:
            body["experiment_ids"] = [
                "EXP-SSI-7c41d9" if value == "EXP-SSI-S1" else value
                for value in body.get("experiment_ids") or []
            ]
    elif relative.startswith("ledger/decisions/"):
        if "coordinator_decision" in doc:
            body = doc["coordinator_decision"]
        elif isinstance(doc.get("decision"), dict):
            body = dict(doc["decision"])
            doc = {"coordinator_decision": body}
        else:
            flat = dict(doc)
            rec_id = flat.pop("decision_id")
            body = {"id": rec_id, **flat}
            doc = {"coordinator_decision": body}
        if "decision" not in body:
            decisions = body.get("decisions")
            body["decision"] = (
                "compound_coordinator_decision" if decisions
                else body.get("decision_type") or body.get("type") or "record_outcome")
        if not body.get("target_ids"):
            targets = []
            for key in ("goal_id", "hypothesis_id", "experiment_id", "evidence_id"):
                value = body.get(key)
                if isinstance(value, str) and re.match(r"^(?:GOAL|H|EXP|EV)-", value):
                    targets.append(value)
            for value in body.get("evidence_ids") or body.get("evidence_refs") or []:
                if isinstance(value, str) and re.match(r"^EV-[A-Z]+-(?:\d{3}|[0-9a-f]{6})$", value):
                    targets.append(value)
            body["target_ids"] = list(dict.fromkeys(targets))
        body["target_ids"] = [
            "EXP-SSI-7c41d9" if value == "EXP-SSI-S1" else value
            for value in body.get("target_ids") or []
            if value != "EV-SEMAEV-7f7d22"
        ]
        promotion = body.get("knowledge_promotion")
        if isinstance(promotion, dict):
            promoted = promotion.get("promoted")
            if isinstance(promoted, list):
                valid = [value for value in promoted if isinstance(value, str)
                         and re.fullmatch(
                             r"KN-[A-Z]+-(?:\d{3}|[0-9a-f]{6})", value)]
                if valid != promoted:
                    promotion["promoted"] = valid
                    if not valid and not promotion.get("not_warranted"):
                        promotion["not_warranted"] = (
                            "The archived field contained a prose scheduling note, "
                            "not a canonical knowledge-entry identifier.")
        if not isinstance(promotion, dict):
            if (isinstance(promotion, str)
                    and re.fullmatch(r"KN-[A-Z]+-(?:\d{3}|[0-9a-f]{6})", promotion)):
                promotion = {"promoted": [promotion]}
            else:
                reason = str(promotion or "No promotion was recorded in the archived decision.")
                promotion = {"promoted": [], "not_warranted": reason}
            body["knowledge_promotion"] = promotion
        body.setdefault("decided_by", body.get("made_by") or body.get("created_by") or "coordinator")
    elif relative.startswith("experiments/"):
        body = doc["experiment"]
        if relative in REPLACEMENT_IDS:
            body["id"] = REPLACEMENT_IDS[relative]
        body.setdefault("version", 1)
        if relative in {
            "experiments/EXP-ECDLP-03a8c9/specification.yaml",
            "experiments/EXP-SSI-eca132/specification.yaml",
        }:
            body["status"] = "review_required"
            body["approval_correction_note"] = (
                "The archived contract had approved_by: null and therefore was "
                "not executable as approved; no approval is inferred.")
        elif relative in {
            "experiments/EXP-ECDLP-1ed445/specification.yaml",
            "experiments/EXP-SSI-6a2619/specification.yaml",
        }:
            body["status"] = "completed"
            body["approval_correction_note"] = (
                "A completed run exists, but the archived contract did not record "
                "an approver; this correction does not fabricate one.")
        body.setdefault("status", "draft")
        body.setdefault("metrics", body.get("metric") or body.get("measurements") or [])
        body.setdefault("budget", body.get("resource_budget") or {"maximum_runs": 0})
        if "success_criterion" not in body:
            body["success_criterion"] = None
            body["success_criterion_note"] = (
                "The archived record was observational and declared no success "
                "criterion; this correction preserves that absence explicitly.")
        if body.get("status") == "approved" and not body.get("falsification_criterion"):
            body["falsification_criterion"] = None
            body["falsification_criterion_note"] = (
                "The archived approved contract did not state a separate "
                "falsification criterion; this correction records that defect "
                "explicitly and does not invent one.")
    elif "/checkpoints/" in relative:
        if "batch_checkpoint" not in doc:
            body = doc.get("checkpoint") if isinstance(doc.get("checkpoint"), dict) else doc
            doc = {"batch_checkpoint": body}
    else:
        raise ValueError(relative)
    return doc


def repair_markdown(relative: str) -> str:
    text = (ROOT / relative).read_text(encoding="utf-8")
    stem = Path(relative).stem
    kind = "internal_finding" if "/findings/" in relative else "literature"
    if text.startswith("---"):
        _, raw, body = text.split("---", 2)
        fm = yaml.safe_load(raw) or {}
    else:
        body = "\n" + text
        title = text.splitlines()[0].lstrip("# ").strip()
        fm = {
            "id": stem,
            "type": kind,
            "title": title,
            "tags": ["schema-correction", "archived-finding"],
            "added": "2026-08-05",
        }
    fm.setdefault("confidence", "provisional")
    if kind == "internal_finding":
        refs = fm.get("internal_refs")
        if not isinstance(refs, list) or not refs:
            candidates = re.findall(
                r"\b(?:EV|DEC|H|EXP)-[A-Z0-9]+-(?:\d{3}|[0-9a-f]{6})\b", text)
            fm["internal_refs"] = list(dict.fromkeys(candidates))[:8]
            if not fm["internal_refs"]:
                raise ValueError(f"{relative}: no truthful internal reference found")
        proof = fm.get("proof_status")
        if proof not in {"certificate", "derivation", "empirical_only", "not_applicable"}:
            fm["proof_status"] = "derivation" if "deriv" in text.lower() else "empirical_only"
        if not isinstance(fm.get("proof_refs"), list):
            fm["proof_refs"] = []
        if relative == "knowledge/findings/KN-FIND-ac28ed.md":
            fm["internal_refs"] = [
                value for value in fm["internal_refs"]
                if value != "EV-SEMAEV-7f7d22"
            ]
    return "---\n" + yaml.safe_dump(fm, sort_keys=False).rstrip() + "\n---" + body


def replacement_path(relative: str) -> Path:
    safe = relative.replace("/", "__")
    suffix = ".md" if relative.endswith(".md") else ".yaml"
    safe = re.sub(r"\.(?:yaml|md)$", ".v2" + suffix, safe)
    return OUT / safe


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    for relative in YAML_SCHEMA_PATHS + KNOWLEDGE_PATHS:
        source = ROOT / relative
        target = replacement_path(relative)
        if relative.endswith(".md"):
            target.write_text(repair_markdown(relative), encoding="utf-8")
            kind = "knowledge"
        else:
            target.write_text(yaml.safe_dump(repair_yaml(relative), sort_keys=False),
                              encoding="utf-8")
            kind = ("goal_checkpoint" if "/checkpoints/" in relative else
                    "experiment" if relative.startswith("experiments/") else "ledger")
        entry = {
            "kind": kind,
            "superseded_path": relative,
            "superseded_sha256": sha(source),
            "superseding_path": str(target.relative_to(ROOT)),
            "superseding_sha256": sha(target),
            "defect": "archived record predates or violates the current schema",
            "registered": "2026-08-08",
        }
        if relative in REPLACEMENT_IDS:
            entry["replacement_id"] = REPLACEMENT_IDS[relative]
        records.append(entry)
    for relative, (target_relative, redirect_id) in REDIRECTS.items():
        records.append({
            "kind": "ledger",
            "superseded_path": relative,
            "superseded_sha256": sha(ROOT / relative),
            "superseding_path": target_relative,
            "superseding_sha256": sha(ROOT / target_relative),
            "redirect_id": redirect_id,
            "defect": "archived identifier is a noncanonical duplicate alias",
            "registered": "2026-08-08",
        })
    records.sort(key=lambda item: item["superseded_path"])
    REGISTRY.write_text(yaml.safe_dump({
        "schema": "schema-supersession-registry-v1",
        "records": records,
    }, sort_keys=False), encoding="utf-8")
    print(f"wrote {len(records)} hash-pinned schema supersessions")


if __name__ == "__main__":
    main()
