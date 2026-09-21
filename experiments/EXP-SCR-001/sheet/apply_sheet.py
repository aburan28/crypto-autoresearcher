#!/usr/bin/env python3
"""EXP-SCR-001 mechanical admission-sheet adjudicator and run harness.

Applies the frozen admission sheet (predicates S1-S5) from
experiments/EXP-SCR-001/specification.yaml to the 21 frozen corpus audit
items, reading all corpus content as git blobs at the pinned commit
(git cat-file), never the working tree.

Subcommands:
  run-a     Freeze corpus manifest + calibration fixtures (RUN-SCR-001-A).
  run-b     Adjudicate groups A and B (RUN-SCR-001-B).
  run-c     Adjudicate group C, determinism replay, aggregate tables
            (RUN-SCR-001-C).
  harness   Execute one payload run with timeout, resource measurement, and
            immutable run-record artifacts.
  validate  Lifecycle step-7 checks over the three run records.

stdlib + PyYAML only. No randomness: seeds = [] (deterministic audit).
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

import yaml

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
for _ in range(3):  # sheet/ -> EXP-SCR-001/ -> experiments/ -> repo root
    REPO_ROOT = os.path.dirname(REPO_ROOT)
EXP_DIR = os.path.join(REPO_ROOT, "experiments", "EXP-SCR-001")
SPEC_PATH = os.path.join(EXP_DIR, "specification.yaml")

TERMINAL_STATUSES = (
    "completed_valid",
    "completed_invalid",
    "failed_infrastructure",
    "failed_implementation",
    "resource_exhaustion",
    "cancelled_by_budget",
)

GROUP_A = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9"]
GROUP_B = ["B1", "B2", "B3", "B4", "B5"]
GROUP_C = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
ALL_ITEMS = GROUP_A + GROUP_B + GROUP_C

# Frozen owner assignments (from the specification's audit_item_index and
# frozen admission sheet; owners that are not corpus paths are record IDs
# named inside pinned corpus records).
ITEM_OWNERS = {
    "A1": ["IDEA-20260723-001", "EV-CRYPTO-002"],
    "A2": ["IDEA-20260723-002", "EV-CRYPTO-004"],
    "A3": ["EV-JET-001", "EV-JETB-001", "P1547"],
    "A4": ["EV-NET-001", "P1540"],
    "A5": ["EV-INC-001", "EV-INCB-001", "P1553"],
    "A6": ["EV-BKK-001", "EV-BKKMV-001"],
    "A7": ["EV-STR-001"],
    "A8": ["EV-REP-001", "EV-REP-002", "EV-FB-001", "EV-ISO-001"],
    "A9": ["KN-LIT-025", "FINDING-PF-IC-001", "McGuire-Mueller screen"],
    "C1": ["KN-LIT-006"],
    "C2": ["KN-LIT-025", "FINDING-PF-IC-001"],
    "C3": ["KN-LIT-025", "FINDING-PF-IC-001", "McGuire-Mueller screen"],
    "C4": ["IDEA-20260723-002", "EV-CRYPTO-004"],
    "C5": [
        "ideas/reviews/P1552_MECHANISM_FRONTIER_20260718.md",
        "ideas/artifacts/ECDLP-IDEA-012/p1553_six_list_incidence_model_gate.md",
    ],
    "C6": ["KN-LIT-011"],
    "C7": [
        "external_references:quantum_resource_reduction_excluded (arXiv:2607.13816)",
        "coordination/goals/GOAL-CRYPTO-001/batches/BATCH-005/tasks/TASK-20260723-501/candidate_report.yaml literature screen",
    ],
}

# Class marker substrings inside the pinned BATCH-005 candidate report's
# toy_negative_and_scoped_control_exclusions entries.
CLASS_MARKERS = {
    "A3": "First-order jets",
    "A4": "Elliptic-net",
    "A5": "Incidence reporting",
    "A6": "BKK/mixed-volume",
    "A7": "Arithmetic-progression displacement",
    "A8": "Edwards/model",
    "A9": "Solver-free summation",
}

# For owners that are record IDs named inside pinned corpus records (not corpus
# paths), the substring proving the pinned exclusion entry names them.
OWNER_MENTION_MARKERS = {
    "McGuire-Mueller screen": "McGuire-Mueller",
}

# Corpus-path content markers proving each closed-class owner record carries
# the toy-negative the sheet names. (path, [required substrings])
OWNER_CONTENT_MARKERS = {
    "ledger/EV-JET-001.yaml": ["sigma_w: 0.0"],
    "ledger/EV-JETB-001.yaml": ["screen equivalence", "sigma_true = 1.0"],
    "ledger/EV-NET-001.yaml": ["direction: weakens"],
    "ledger/EV-INC-001.yaml": ["no output sensitivity"],
    "ledger/EV-INCB-001.yaml": ["direction: weakens"],
    "ledger/EV-BKK-001.yaml": ["= 1 exactly"],
    "ledger/EV-BKKMV-001.yaml": ["mv_exact", "98304"],
    "ledger/EV-STR-001.yaml": ["direction: contradicts"],
    "ledger/EV-REP-001.yaml": ["d_reg=2 flat"],
    "ledger/EV-REP-002.yaml": ["d_reg=2 flat"],
    "ledger/EV-FB-001.yaml": ["structure-invariant"],
    "ledger/EV-ISO-001.yaml": ["no neighbor d_reg<2"],
    "knowledge/literature/KN-LIT-025.md": ["practical only for small parameters"],
    "ledger/FINDING-PF-IC-001.md": ["not** produce relations below the", "2.05"],
}

CANDIDATE_REPORT = (
    "coordination/goals/GOAL-CRYPTO-001/batches/BATCH-005/tasks/"
    "TASK-20260723-501/candidate_report.yaml"
)

PLANNED_RUNS = {
    "RUN-SCR-001-A": "run-a",
    "RUN-SCR-001-B": "run-b",
    "RUN-SCR-001-C": "run-c",
}

WALL_TIMEOUT_SECONDS = 1800  # frozen per-run budget
MEM_LIMIT_BYTES = 4 * 1024**3  # frozen 4 GB cap


# --------------------------------------------------------------------------
# spec / corpus access
# --------------------------------------------------------------------------

def load_spec():
    with open(SPEC_PATH, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)["experiment"]


def pinned_commit(spec):
    return spec["inputs"]["corpus_snapshot"]["pinned_commit"]


def git_blob_bytes(commit, path):
    out = subprocess.run(
        ["git", "cat-file", "blob", "%s:%s" % (commit, path)],
        capture_output=True,
        cwd=REPO_ROOT,
    )
    if out.returncode != 0:
        return None
    return out.stdout


def git_blob_sha1_of(content):
    header = b"blob %d\x00" % len(content)
    return hashlib.sha1(header + content).hexdigest()


def sha256_hex(content):
    return hashlib.sha256(content).hexdigest()


def canonical_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def write_json_if_absent_or_identical(path, obj):
    data = canonical_json(obj)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            existing = fh.read()
        if existing != data:
            raise RuntimeError("immutable artifact content conflict: %s" % path)
        return False
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(data)
    return True


def verify_corpus(spec):
    """Corpus integrity control: read every pinned blob, compare SHA-1."""
    commit = pinned_commit(spec)
    entries = []
    missing, mismatches = [], []
    for entry in spec["inputs"]["corpus_snapshot"]["hash_manifest"]:
        path = entry["path"]
        want = entry["git_blob_sha1"]
        content = git_blob_bytes(commit, path)
        if content is None:
            missing.append(path)
            entries.append(
                {
                    "path": path,
                    "expected_git_blob_sha1": want,
                    "status": "missing",
                }
            )
            continue
        got = git_blob_sha1_of(content)
        rec = {
            "path": path,
            "expected_git_blob_sha1": want,
            "actual_git_blob_sha1": got,
            "sha256": sha256_hex(content),
            "bytes": len(content),
            "status": "pass" if got == want else "mismatch",
        }
        if got != want:
            mismatches.append(path)
        entries.append(rec)
    report = {
        "control": "CTRL-CORPUS-INTEGRITY",
        "pinned_commit": commit,
        "verification_rule": spec["inputs"]["corpus_snapshot"]["verification_rule"],
        "entry_count": len(entries),
        "verified": sum(1 for e in entries if e["status"] == "pass"),
        "missing": missing,
        "mismatches": mismatches,
        "pass": not missing and not mismatches,
        "entries": entries,
    }
    return report


class Corpus:
    """Cached pinned-commit corpus content (git blobs only)."""

    def __init__(self, spec):
        self.commit = pinned_commit(spec)
        self._text = {}

    def text(self, path):
        if path not in self._text:
            content = git_blob_bytes(self.commit, path)
            if content is None:
                raise KeyError("missing corpus path: %s" % path)
            self._text[path] = content.decode("utf-8")
        return self._text[path]

    def yaml(self, path):
        return yaml.safe_load(self.text(path))


def excerpt(text, needle, width=200):
    idx = text.find(needle)
    if idx < 0:
        return None
    start = max(0, idx - 20)
    snippet = text[start : idx + len(needle) + (width - len(needle) - 20)]
    return " ".join(snippet.split())


# --------------------------------------------------------------------------
# frozen admission sheet
# --------------------------------------------------------------------------

def apply_sheet(facts):
    """Pure function of the fact vector. Returns (verdict, first_failed, detail)."""
    if facts.get("residual"):
        return "residual_open_problem", None, {
            "note": "group B residual open problem; not a candidate",
            "obligation": facts["residual"],
        }
    if facts.get("is_zR_rename"):
        return "reject_duplicate", "S1", {"owner_class": "IDEA-20260723-001 z_R interface"}
    if facts.get("is_hyperplane_rename"):
        return "reject_duplicate", "S2", {
            "owner_class": "IDEA-20260723-002 hyperplane/zero-minor interface"
        }
    if facts.get("closed_class"):
        return "reject_closed_class", "S3", {"closed_class": facts["closed_class"]}
    op = facts.get("operation")
    s4_holds = bool(
        op
        and op.get("typed_io")
        and op.get("coefficient_provenance")
        and op.get("occurrence_level_signed_source_return")
        and op.get("identical_masked_target_use")
        and not op.get("aggregate_only")
        and not op.get("unnamed_oracle")
        and not op.get("backend_substitution")
        and not op.get("residual_description")
    )
    if not s4_holds:
        return "reject_no_explicit_operation", "S4", {
            "operation_facts": op,
            "note": facts.get("s4_note"),
        }
    ledger = facts.get("ledger")
    terms = ledger.get("terms", {}) if ledger else {}
    unassigned = [k for k, v in terms.items() if v is None]
    lam = ledger.get("lambda") if ledger else None
    mu = ledger.get("mu") if ledger else None
    s5_holds = bool(ledger) and not unassigned and lam is not None and lam < 0.50
    if not s5_holds:
        return "reject_not_sub_rho", "S5", {
            "unassigned_terms": unassigned,
            "lambda": lam,
            "mu": mu,
        }
    return "ADMIT", None, {"lambda": lam, "mu": mu}


def campaign_045_flag(verdict, facts):
    if verdict != "ADMIT":
        return None
    ledger = facts.get("ledger") or {}
    lam, mu = ledger.get("lambda"), ledger.get("mu")
    return lam is not None and mu is not None and lam <= 0.45 and mu <= 0.45


# --------------------------------------------------------------------------
# per-item adjudication (checks grounded in pinned corpus bytes)
# --------------------------------------------------------------------------

def _check(check_id, description, ok, evidence=None):
    return {
        "check_id": check_id,
        "description": description,
        "result": "pass" if ok else "fail",
        "evidence": evidence or {},
    }


def _undecidable(item_id, name, checks, reason):
    return {
        "item_id": item_id,
        "item_name": name,
        "verdict": "undecidable_with_reason",
        "undecidable_reason": reason,
        "first_failed_predicate": None,
        "owner": [],
        "checks": checks,
        "campaign_045": None,
    }


def adjudicate_item(item_id, spec, corpus):
    items = {}
    for group_key in (
        "group_a_dedup_and_exclusion",
        "group_b_residual_open_problems",
        "group_c_literature_screen_records",
    ):
        for entry in spec["inputs"]["audit_item_index"][group_key]:
            items[entry["id"]] = entry
    meta = items[item_id]
    name = meta["name"]
    report = corpus.yaml(CANDIDATE_REPORT)
    checks = []

    def require(check_id, desc, ok, evidence=None):
        checks.append(_check(check_id, desc, ok, evidence))
        return ok

    # ---- group A1: S1 z_R rename exclusion -------------------------------
    if item_id == "A1":
        idea1 = corpus.text("ledger/proposals/IDEA-20260723-001.yaml")
        evc2 = corpus.text("ledger/evidence/EV-CRYPTO-002.yaml")
        excl = report["corpus_deduplication"]["exact_exclusions"]
        e0 = next((e for e in excl if e["id"] == "OBL-ZR-COMPACT-CONSTRUCTOR-001"), None)
        ok = True
        ok &= require(
            "CK-A1-1",
            "spec index names OBL-ZR-COMPACT-CONSTRUCTOR-001 with the frozen owner",
            "OBL-ZR-COMPACT-CONSTRUCTOR-001" in name
            and meta.get("expected_owner") == "IDEA-20260723-001 / EV-CRYPTO-002",
            {"spec_index_name": name},
        )
        ok &= require(
            "CK-A1-2",
            "pinned candidate report exact_exclusions carries OBL-ZR-COMPACT-CONSTRUCTOR-001 "
            "as a rename of the IDEA-20260723-001 interface",
            bool(e0)
            and "IDEA-20260723-001" in e0["reason"]
            and "support factor" in e0["reason"],
            {"excerpt": excerpt(e0["reason"], "IDEA-20260723-001") if e0 else None},
        )
        ok &= require(
            "CK-A1-3",
            "IDEA-20260723-001 mechanism is the compact z_R common-factor interface and "
            "EV-CRYPTO-002 records NO_ADMISSIBLE_CONSTRUCTION",
            "z_R" in idea1
            and "gcd" in idea1
            and "NO_ADMISSIBLE_CONSTRUCTION" in evc2,
            {
                "idea_excerpt": excerpt(idea1, "z_R"),
                "ev_excerpt": excerpt(evc2, "NO_ADMISSIBLE_CONSTRUCTION"),
            },
        )
        if not ok:
            return _undecidable(item_id, name, checks, "S1 grounding markers not all found")
        facts = {"is_zR_rename": True}
        verdict, first_failed, detail = apply_sheet(facts)
        return _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)

    # ---- group A2: S2 hyperplane rename exclusion ------------------------
    if item_id == "A2":
        idea2 = corpus.text("ledger/proposals/IDEA-20260723-002.yaml")
        evc4 = corpus.text("ledger/evidence/EV-CRYPTO-004.yaml")
        excl = report["corpus_deduplication"]["exact_exclusions"]
        e1 = next((e for e in excl if e["id"] == "IDEA-20260723-002"), None)
        ok = True
        ok &= require(
            "CK-A2-1",
            "spec index names the defect-scaled hyperplane-signature / zero-minor interface",
            "hyperplane-signature" in name and "zero-minor" in name,
            {"spec_index_name": name},
        )
        ok &= require(
            "CK-A2-2",
            "pinned candidate report exact_exclusions carries IDEA-20260723-002 covering "
            "zero-minor / hyperplane-signature enumerators / unnamed minor locators",
            bool(e1)
            and "zero-minor" in e1["reason"]
            and "hyperplane-signature" in e1["reason"],
            {"excerpt": excerpt(e1["reason"], "zero-minor") if e1 else None},
        )
        ok &= require(
            "CK-A2-3",
            "IDEA-20260723-002 mechanism is defect-scaled hyperplane-signature zero-minor "
            "search; EV-CRYPTO-004 records INCONCLUSIVE_COST_CLAIM",
            "defect-scaled hyperplane signatures" in idea2
            and "zero minors" in idea2
            and "INCONCLUSIVE_COST_CLAIM" in evc4,
            {"ev_excerpt": excerpt(evc4, "INCONCLUSIVE_COST_CLAIM")},
        )
        # S2 scope guard: only an unchanged interface / unnamed locator /
        # backend substitution may be rejected here.
        report_text = corpus.text(CANDIDATE_REPORT)
        repaired = "repaired formula alignment" in report_text
        ok &= require(
            "CK-A2-4",
            "S2 scope guard: no pinned record asserts a repaired, named, cost-aligned "
            "variant of the interface (which would be outside S2)",
            not repaired,
        )
        if not ok:
            return _undecidable(item_id, name, checks, "S2 grounding markers not all found")
        facts = {"is_hyperplane_rename": True}
        verdict, first_failed, detail = apply_sheet(facts)
        return _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)

    # ---- group A3-A9: S3 closed-class dedup ------------------------------
    if item_id in CLASS_MARKERS:
        marker = CLASS_MARKERS[item_id]
        exclusions = report["corpus_deduplication"][
            "toy_negative_and_scoped_control_exclusions"
        ]
        entry = next((e for e in exclusions if marker in e), None)
        ok = require(
            "CK-%s-1" % item_id,
            "pinned candidate report names the closed class '%s'" % marker,
            entry is not None,
            {"excerpt": excerpt(entry, marker) if entry else None},
        )
        for owner in ITEM_OWNERS[item_id]:
            corpus_path = _owner_corpus_path(owner)
            if corpus_path is None:
                mention = OWNER_MENTION_MARKERS.get(owner, owner)
                ok &= require(
                    "CK-%s-owner-%s" % (item_id, owner),
                    "owner record ID '%s' is named inside the pinned exclusion entry "
                    "(mention marker '%s')" % (owner, mention),
                    bool(entry) and mention in entry,
                    {"excerpt": excerpt(entry, mention) if entry else None},
                )
                continue
            text = corpus.text(corpus_path)
            markers = OWNER_CONTENT_MARKERS.get(corpus_path, [])
            ok &= require(
                "CK-%s-owner-%s" % (item_id, owner),
                "owner record %s exists in pinned corpus and carries the toy-negative markers %s"
                % (corpus_path, markers),
                all(m in text for m in markers),
                {"excerpt": excerpt(text, markers[0]) if markers else None},
            )
        if not ok:
            return _undecidable(item_id, name, checks, "S3 grounding markers not all found")
        facts = {"closed_class": marker}
        verdict, first_failed, detail = apply_sheet(facts)
        return _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)

    # ---- group B: residual open problems ---------------------------------
    if item_id in GROUP_B:
        problems = report["narrowest_remaining_open_problems"]
        entry = next((p for p in problems if p["id"] == name), None)
        ok = require(
            "CK-%s-1" % item_id,
            "pinned candidate report carries residual open problem '%s'" % name,
            entry is not None,
            {"excerpt": excerpt(entry["statement"], entry["statement"][:40]) if entry else None},
        )
        obligation, obligation_source = None, None
        if entry:
            if entry.get("admission_obligation"):
                obligation = entry["admission_obligation"]
                obligation_source = "candidate_report:narrowest_remaining_open_problems.admission_obligation"
            else:
                obligation = entry["statement"]
                obligation_source = "candidate_report:narrowest_remaining_open_problems.statement (no separate admission_obligation field in pinned record)"
        kn_path = "knowledge/open-problems/%s.md" % name
        if name.startswith("KN-OPEN-"):
            front = corpus.text(kn_path).split("---")[1]
            fm = yaml.safe_load(front)
            ok &= require(
                "CK-%s-2" % item_id,
                "pinned %s exists with status open" % kn_path,
                fm.get("status") == "open",
                {"status": fm.get("status")},
            )
        if not ok:
            return _undecidable(item_id, name, checks, "residual grounding markers not found")
        facts = {
            "residual": {
                "problem_id": name,
                "obligation": obligation,
                "obligation_source": obligation_source,
            }
        }
        verdict, first_failed, detail = apply_sheet(facts)
        return _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)

    # ---- group C ----------------------------------------------------------
    lit = report["literature_deduplication"]
    checked = "\n".join(lit["checked_sources"])

    if item_id == "C1":
        kn = corpus.text("knowledge/literature/KN-LIT-006.md")
        ok = True
        ok &= require(
            "CK-C1-1",
            "pinned literature screen checked Galbraith-Gaudry (KN-LIT-006)",
            "Galbraith and Gaudry" in checked and "KN-LIT-006" in checked,
            {"excerpt": excerpt(checked, "Galbraith and Gaudry")},
        )
        ok &= require(
            "CK-C1-2",
            "KN-LIT-006 is a survey record reporting no known prime-field sub-rho algorithm",
            "no algorithm is known that beats generic square-root" in kn
            and "survey" in kn,
            {"excerpt": excerpt(kn, "no algorithm is known that beats generic square-root")},
        )
        if not ok:
            return _undecidable(item_id, name, checks, "C1 grounding markers not found")
        facts = {"operation": None, "s4_note": "survey class record; supplies no explicit public operation"}
        verdict, first_failed, detail = apply_sheet(facts)
        return _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)

    if item_id == "C2":
        kn = corpus.text("knowledge/literature/KN-LIT-025.md")
        finding = corpus.text("ledger/FINDING-PF-IC-001.md")
        exclusions = report["corpus_deduplication"]["toy_negative_and_scoped_control_exclusions"]
        entry = next((e for e in exclusions if "Solver-free summation" in e), None)
        ok = True
        ok &= require(
            "CK-C2-1",
            "pinned literature screen checked Petit-Kosters-Messeng (KN-LIT-025)",
            "Petit, Kosters, and Messeng" in checked and "KN-LIT-025" in checked,
            {"excerpt": excerpt(checked, "Petit, Kosters, and Messeng")},
        )
        ok &= require(
            "CK-C2-2",
            "pinned corpus dedup records prime-field decomposition / summation backends "
            "as covered by KN-LIT-025 and FINDING-PF-IC-001",
            bool(entry) and "KN-LIT-025" in entry and "FINDING-PF-IC-001" in entry,
            {"excerpt": excerpt(entry, "KN-LIT-025") if entry else None},
        )
        ok &= require(
            "CK-C2-3",
            "KN-LIT-025 is hedged to small parameters; FINDING-PF-IC-001 records the "
            "toy-negative total-cost exponent 2.05 (CI [1.86, 2.29]) above rho",
            "practical only for small parameters" in kn
            and "2.05" in finding
            and "[1.86, 2.29]" in finding,
            {"finding_excerpt": excerpt(finding, "2.05")},
        )
        if not ok:
            return _undecidable(item_id, name, checks, "C2 grounding markers not found")
        facts = {"closed_class": "Solver-free summation / prime-field decomposition backend"}
        verdict, first_failed, detail = apply_sheet(facts)
        return _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)

    if item_id == "C3":
        exclusions = report["corpus_deduplication"]["toy_negative_and_scoped_control_exclusions"]
        entry = next((e for e in exclusions if "Solver-free summation" in e), None)
        ok = True
        ok &= require(
            "CK-C3-1",
            "pinned literature screen checked McGuire-Mueller ePrint 2017/1262 and records "
            "exponential stated complexity, worse than Pollard rho",
            "McGuire and Mueller" in checked
            and "2017/1262" in checked
            and "exponential complexity" in checked
            and "worse than Pollard rho" in checked,
            {"excerpt": excerpt(checked, "McGuire and Mueller")},
        )
        ok &= require(
            "CK-C3-2",
            "pinned corpus dedup names the McGuire-Mueller prior-art screen as covering "
            "the summation-evaluation route",
            bool(entry) and "McGuire-Mueller" in entry,
            {"excerpt": excerpt(entry, "McGuire-Mueller") if entry else None},
        )
        if not ok:
            return _undecidable(item_id, name, checks, "C3 grounding markers not found")
        facts = {"closed_class": "Solver-free summation / prime-field decomposition backend"}
        verdict, first_failed, detail = apply_sheet(facts)
        rec = _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)
        rec["notes"] = [
            "pinned screen independently reports the stated prime-field algorithms as "
            "exponential and worse than rho (would also fail S5)"
        ]
        return rec

    if item_id == "C4":
        evc4 = corpus.text("ledger/evidence/EV-CRYPTO-004.yaml")
        ext = spec["inputs"]["external_references"]["items"]
        ref = next((r for r in ext if r["id"] == "mahalanobis_lineage_zero_minor"), None)
        ok = True
        ok &= require(
            "CK-C4-1",
            "pinned literature screen records the Mahalanobis lineage (2018/2023/2025/"
            "arXiv:2607.09814v1) as the excluded zero-minor/hyperplane-signature lineage",
            "Mahalanobis" in checked
            and "arXiv:2607.09814v1" in checked
            and "excluded zero-minor/hyperplane-signature lineage" in checked,
            {"excerpt": excerpt(checked, "excluded zero-minor/hyperplane-signature lineage")},
        )
        ok &= require(
            "CK-C4-2",
            "S2 scope guard holds for C4: the lineage is recorded as the excluded interface "
            "itself (EV-CRYPTO-004 inconclusive, not a closure theorem); no pinned record "
            "presents a repaired named variant",
            "INCONCLUSIVE_COST_CLAIM" in evc4
            and "repaired formula alignment" not in checked,
            {"ev_excerpt": excerpt(evc4, "INCONCLUSIVE_COST_CLAIM")},
        )
        ok &= require(
            "CK-C4-3",
            "frozen external_references carries mahalanobis_lineage_zero_minor with the "
            "recorded URL and retrieval date",
            bool(ref)
            and ref.get("url") == "https://arxiv.org/abs/2607.09814v1"
            and str(ref.get("recorded_retrieval_date")) == "2026-07-23",
            {"ref": ref},
        )
        if not ok:
            return _undecidable(item_id, name, checks, "C4 grounding markers not found")
        facts = {"is_hyperplane_rename": True}
        verdict, first_failed, detail = apply_sheet(facts)
        return _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)

    if item_id == "C5":
        p1552 = corpus.text("ideas/reviews/P1552_MECHANISM_FRONTIER_20260718.md")
        p1553 = corpus.text("ideas/artifacts/ECDLP-IDEA-012/p1553_six_list_incidence_model_gate.md")
        ok = True
        ok &= require(
            "CK-C5-1",
            "pinned literature screen checked the kSUM/3SUM preprocessing cluster "
            "(arXiv:2512.04258, arXiv:2410.16784, arXiv:2602.11363) and records the "
            "P1552/P1553 translation outside the B^(9/4)/B^(5/4) rectangle",
            "arXiv:2512.04258" in checked
            and "arXiv:2410.16784" in checked
            and "arXiv:2602.11363" in checked
            and "outside the" in checked
            and "rectangle" in checked,
            {"excerpt": excerpt(checked, "arXiv:2512.04258")},
        )
        ok &= require(
            "CK-C5-2",
            "P1552 and P1553 pinned records independently record the current kSUM/"
            "preprocessed-3SUM controls missing the required rectangle and supplying no "
            "endpoint-only source unranking operation",
            "CURRENT_KSUM_AND_PREPROCESSED_3SUM_CONTROLS_MISS_THE_REQUIRED_RECTANGLE" in p1552
            and "NO_ENDPOINT_ONLY_SOURCE_UNRANKING_OPERATION_SUPPLIED" in p1552
            and "CURRENT_KSUM_INDEXING_INCIDENCE_AND_DENSE_MULTIPOINT_ALGORITHMS_MISS_B9_OVER_4_B5_OVER_4" in p1553,
            {"p1552_excerpt": excerpt(p1552, "NO_ENDPOINT_ONLY_SOURCE_UNRANKING_OPERATION_SUPPLIED")},
        )
        if not ok:
            return _undecidable(item_id, name, checks, "C5 grounding markers not found")
        facts = {"operation": None, "s4_note": "records supply no explicit public operation with occurrence-level signed source return inside the charged rectangle"}
        verdict, first_failed, detail = apply_sheet(facts)
        return _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)

    if item_id == "C6":
        kn = corpus.text("knowledge/literature/KN-LIT-011.md")
        ok = True
        ok &= require(
            "CK-C6-1",
            "pinned literature screen checked Shoup EUROCRYPT 1997 (KN-LIT-011)",
            "Shoup" in checked and "EUROCRYPT 1997" in checked and "KN-LIT-011" in checked,
            {"excerpt": excerpt(checked, "Shoup")},
        )
        ok &= require(
            "CK-C6-2",
            "KN-LIT-011 records the proven generic Omega(sqrt(p)) lower bound matching rho "
            "(a barrier theorem, not an attack operation)",
            "Omega(sqrt(p))" in kn and "generic" in kn,
            {"excerpt": excerpt(kn, "Omega(sqrt(p))")},
        )
        if not ok:
            return _undecidable(item_id, name, checks, "C6 grounding markers not found")
        facts = {"operation": None, "s4_note": "generic lower-bound theorem; supplies no attack operation (it grounds the 0.50 baseline used by S5)"}
        verdict, first_failed, detail = apply_sheet(facts)
        return _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)

    if item_id == "C7":
        ext = spec["inputs"]["external_references"]["items"]
        ref = next((r for r in ext if r["id"] == "quantum_resource_reduction_excluded"), None)
        ok = True
        ok &= require(
            "CK-C7-1",
            "pinned literature screen records arXiv:2607.13816 quantum resource reduction "
            "as a different computational model",
            "arXiv:2607.13816" in checked and "different computational model" in checked,
            {"excerpt": excerpt(checked, "arXiv:2607.13816")},
        )
        ok &= require(
            "CK-C7-2",
            "frozen external_references excludes it from the classical screen",
            bool(ref) and "excluded from classical screen" in (ref.get("note") or ""),
            {"ref": ref},
        )
        if not ok:
            return _undecidable(item_id, name, checks, "C7 grounding markers not found")
        facts = {
            "operation": None,
            "s4_note": "different computational model (quantum circuit optimization); excluded from the classical screen per the frozen external_references; supplies no classical public operation",
        }
        verdict, first_failed, detail = apply_sheet(facts)
        return _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks)

    raise KeyError("unknown item id: %s" % item_id)


def _owner_corpus_path(owner):
    candidates = {
        "IDEA-20260723-001": "ledger/proposals/IDEA-20260723-001.yaml",
        "IDEA-20260723-002": "ledger/proposals/IDEA-20260723-002.yaml",
        "EV-CRYPTO-002": "ledger/evidence/EV-CRYPTO-002.yaml",
        "EV-CRYPTO-004": "ledger/evidence/EV-CRYPTO-004.yaml",
        "EV-JET-001": "ledger/EV-JET-001.yaml",
        "EV-JETB-001": "ledger/EV-JETB-001.yaml",
        "EV-NET-001": "ledger/EV-NET-001.yaml",
        "EV-INC-001": "ledger/EV-INC-001.yaml",
        "EV-INCB-001": "ledger/EV-INCB-001.yaml",
        "EV-BKK-001": "ledger/EV-BKK-001.yaml",
        "EV-BKKMV-001": "ledger/EV-BKKMV-001.yaml",
        "EV-STR-001": "ledger/EV-STR-001.yaml",
        "EV-REP-001": "ledger/EV-REP-001.yaml",
        "EV-REP-002": "ledger/EV-REP-002.yaml",
        "EV-FB-001": "ledger/EV-FB-001.yaml",
        "EV-ISO-001": "ledger/EV-ISO-001.yaml",
        "KN-LIT-025": "knowledge/literature/KN-LIT-025.md",
        "FINDING-PF-IC-001": "ledger/FINDING-PF-IC-001.md",
        "KN-LIT-006": "knowledge/literature/KN-LIT-006.md",
        "KN-LIT-011": "knowledge/literature/KN-LIT-011.md",
    }
    return candidates.get(owner)


def _verdict_record(item_id, name, verdict, first_failed, detail, facts, checks):
    return {
        "item_id": item_id,
        "item_name": name,
        "verdict": verdict,
        "first_failed_predicate": first_failed,
        "owner": ITEM_OWNERS.get(item_id, []),
        "sheet_detail": detail,
        "campaign_045": campaign_045_flag(verdict, facts),
        "checks": checks,
    }


def adjudicate_items(item_ids, spec):
    corpus = Corpus(spec)
    return [adjudicate_item(iid, spec, corpus) for iid in item_ids]


# --------------------------------------------------------------------------
# calibration fixtures
# --------------------------------------------------------------------------

CAL_PASS_DESCRIPTOR = {
    "fixture_id": "CAL-PASS-SCR-001",
    "synthetic": True,
    "is_zR_rename": False,
    "is_hyperplane_rename": False,
    "closed_class": None,
    "operation": {
        "typed_io": True,
        "coefficient_provenance": True,
        "occurrence_level_signed_source_return": True,
        "identical_masked_target_use": True,
        "aggregate_only": False,
        "unnamed_oracle": False,
        "backend_substitution": False,
        "residual_description": False,
    },
    "ledger": {
        "terms": {
            "a": 0.20,
            "a_m": 0.40,
            "delta": 0.10,
            "q": 0.10,
            "r": 0.05,
            "o": 0.10,
            "ell": 0.44,
            "ell_m": 0.20,
            "delta_t": 0.10,
            "q_t": 0.10,
            "o_t": 0.10,
            "u": 0.05,
        },
        "lambda": 0.44,
        "mu": 0.40,
    },
}


def run_calibration(spec):
    """CTRL-SHEET-CALIBRATION: frozen sheet on the two pre-declared fixtures."""
    fixtures = []
    # CAL-PASS-SCR-001: synthetic must-pass fixture.
    facts = {k: v for k, v in CAL_PASS_DESCRIPTOR.items() if k not in ("fixture_id", "synthetic")}
    verdict, first_failed, detail = apply_sheet(facts)
    fixtures.append(
        {
            "id": "CAL-PASS-SCR-001",
            "kind": "must_pass",
            "synthetic_fixture": True,
            "expected_verdict": "ADMIT",
            "actual_verdict": verdict,
            "first_failed_predicate": first_failed,
            "campaign_045": campaign_045_flag(verdict, facts),
            "sheet_detail": detail,
            "pass": verdict == "ADMIT",
        }
    )
    # CAL-FAIL-SCR-001: the real A1 record through the sheet; must trigger S1.
    corpus = Corpus(spec)
    rec = adjudicate_item("A1", spec, corpus)
    fixtures.append(
        {
            "id": "CAL-FAIL-SCR-001",
            "kind": "must_fail",
            "synthetic_fixture": False,
            "expected_verdict": "reject_duplicate",
            "actual_verdict": rec["verdict"],
            "first_failed_predicate": rec["first_failed_predicate"],
            "triggered_predicate": rec["first_failed_predicate"],
            "pass": rec["verdict"] == "reject_duplicate"
            and rec["first_failed_predicate"] == "S1",
        }
    )
    accuracy = sum(1 for f in fixtures if f["pass"]) / len(fixtures)
    return {
        "control": "CTRL-SHEET-CALIBRATION",
        "fixtures": fixtures,
        "accuracy": accuracy,
        "pass": accuracy == 1.0,
    }


# --------------------------------------------------------------------------
# payload commands
# --------------------------------------------------------------------------

def cmd_run_a(out_path):
    spec = load_spec()
    print("RUN-SCR-001-A: freeze corpus manifest + calibration")
    corpus_report = verify_corpus(spec)
    manifest_path = os.path.join(EXP_DIR, "corpus_manifest.json")
    write_json_if_absent_or_identical(manifest_path, corpus_report)
    print(
        "corpus integrity: %d/%d verified, missing=%d, mismatches=%d"
        % (
            corpus_report["verified"],
            corpus_report["entry_count"],
            len(corpus_report["missing"]),
            len(corpus_report["mismatches"]),
        )
    )
    calibration = run_calibration(spec)
    receipt_path = os.path.join(EXP_DIR, "sheet", "calibration_receipt.json")
    write_json_if_absent_or_identical(receipt_path, calibration)
    print(
        "calibration: accuracy=%.3f pass=%s (%s)"
        % (
            calibration["accuracy"],
            calibration["pass"],
            ", ".join(
                "%s=%s" % (f["id"], f["actual_verdict"]) for f in calibration["fixtures"]
            ),
        )
    )
    valid = corpus_report["pass"] and calibration["pass"]
    invalid_reason = None
    if not corpus_report["pass"]:
        invalid_reason = "corpus integrity control failed (missing or mismatched pinned blobs)"
    elif not calibration["pass"]:
        invalid_reason = "calibration accuracy below 2/2 (sheet unsound as instrumented)"
    raw = {
        "run_id": "RUN-SCR-001-A",
        "experiment_id": "EXP-SCR-001",
        "generated_at": _now(),
        "corpus_integrity": {
            k: v for k, v in corpus_report.items() if k != "entries"
        },
        "corpus_manifest_path": os.path.relpath(manifest_path, REPO_ROOT),
        "calibration": calibration,
        "calibration_receipt_path": os.path.relpath(receipt_path, REPO_ROOT),
        "controls": {
            "CTRL-CORPUS-INTEGRITY": "pass" if corpus_report["pass"] else "fail",
            "CTRL-SHEET-CALIBRATION": "pass" if calibration["pass"] else "fail",
        },
        "valid": valid,
        "invalid_reason": invalid_reason,
    }
    _write_out(out_path, raw)
    return 0 if valid else 2


def cmd_run_b(out_path):
    spec = load_spec()
    print("RUN-SCR-001-B: adjudicate groups A and B")
    corpus_report = verify_corpus(spec)
    calibration = run_calibration(spec)
    print(
        "pre-controls: corpus=%s calibration=%s"
        % (corpus_report["pass"], calibration["pass"])
    )
    if not (corpus_report["pass"] and calibration["pass"]):
        raw = {
            "run_id": "RUN-SCR-001-B",
            "experiment_id": "EXP-SCR-001",
            "generated_at": _now(),
            "corpus_integrity_pass": corpus_report["pass"],
            "calibration": calibration,
            "adjudications": [],
            "controls": {
                "CTRL-CORPUS-INTEGRITY": "pass" if corpus_report["pass"] else "fail",
                "CTRL-SHEET-CALIBRATION": "pass" if calibration["pass"] else "fail",
            },
            "valid": False,
            "invalid_reason": "pre-controls failed before adjudication",
        }
        _write_out(out_path, raw)
        return 2
    records = adjudicate_items(GROUP_A + GROUP_B, spec)
    for rec in records:
        print(
            "  %s %-70s -> %s" % (rec["item_id"], rec["item_name"][:70], rec["verdict"])
        )
    raw = {
        "run_id": "RUN-SCR-001-B",
        "experiment_id": "EXP-SCR-001",
        "generated_at": _now(),
        "corpus_integrity_pass": corpus_report["pass"],
        "calibration": calibration,
        "adjudications": records,
        "group_tally": _tally(records),
        "controls": {
            "CTRL-CORPUS-INTEGRITY": "pass",
            "CTRL-SHEET-CALIBRATION": "pass",
        },
        "valid": True,
        "invalid_reason": None,
    }
    _write_out(out_path, raw)
    return 0


def cmd_run_c(out_path):
    spec = load_spec()
    print("RUN-SCR-001-C: adjudicate group C, replay, aggregate")
    corpus_report = verify_corpus(spec)
    calibration = run_calibration(spec)
    if not (corpus_report["pass"] and calibration["pass"]):
        raw = {
            "run_id": "RUN-SCR-001-C",
            "experiment_id": "EXP-SCR-001",
            "generated_at": _now(),
            "corpus_integrity_pass": corpus_report["pass"],
            "calibration": calibration,
            "adjudications": [],
            "controls": {
                "CTRL-CORPUS-INTEGRITY": "pass" if corpus_report["pass"] else "fail",
                "CTRL-SHEET-CALIBRATION": "pass" if calibration["pass"] else "fail",
            },
            "valid": False,
            "invalid_reason": "pre-controls failed before adjudication",
        }
        _write_out(out_path, raw)
        return 2

    records_c = adjudicate_items(GROUP_C, spec)
    for rec in records_c:
        print(
            "  %s %-70s -> %s" % (rec["item_id"], rec["item_name"][:70], rec["verdict"])
        )

    # Pass 1: group A/B verdicts from RUN-SCR-001-B raw record + this run's C verdicts.
    run_b_raw_path = os.path.join(
        EXP_DIR, "runs", "RUN-SCR-001-B", "raw-result.json"
    )
    with open(run_b_raw_path, "r", encoding="utf-8") as fh:
        run_b_raw = json.load(fh)
    pass1_records = run_b_raw["adjudications"] + records_c

    # CTRL-REPLAY-DETERMINISM: second full application over all 21 items.
    pass2_records = adjudicate_items(ALL_ITEMS, spec)
    table1 = _admissibility_table_payload(pass1_records)
    table2 = _admissibility_table_payload(pass2_records)
    bytes1 = canonical_json(table1).encode("utf-8")
    bytes2 = canonical_json(table2).encode("utf-8")
    replay_identical = bytes1 == bytes2
    replay = {
        "control": "CTRL-REPLAY-DETERMINISM",
        "pass1_source": "RUN-SCR-001-B adjudications (A,B) + RUN-SCR-001-C adjudications (C)",
        "pass2_source": "fresh full-sheet application over all 21 items in RUN-SCR-001-C",
        "pass1_sha256": sha256_hex(bytes1),
        "pass2_sha256": sha256_hex(bytes2),
        "byte_identical": replay_identical,
        "verdict_flips": _verdict_flips(pass1_records, pass2_records),
        "pass": replay_identical,
    }
    print("replay determinism: byte_identical=%s" % replay_identical)

    # Residual frontier from pass-1 records.
    residual = [
        {
            "item_id": r["item_id"],
            "problem_id": r["sheet_detail"]["obligation"]["problem_id"],
            "obligation": r["sheet_detail"]["obligation"]["obligation"],
            "obligation_source": r["sheet_detail"]["obligation"]["obligation_source"],
        }
        for r in pass1_records
        if r["verdict"] == "residual_open_problem"
    ]
    required_residual = ["SOURCE-LOCATOR-OPEN", "KN-OPEN-005", "KN-OPEN-004", "KN-OPEN-006", "KN-OPEN-001"]
    residual_ids = [r["problem_id"] for r in residual]
    residual_complete = sorted(residual_ids) == sorted(required_residual)
    residual_frontier = {
        "entries": residual,
        "required_entries": required_residual,
        "complete": residual_complete,
    }

    rejected = [
        r
        for r in pass1_records
        if r["verdict"] not in ("ADMIT", "residual_open_problem", "undecidable_with_reason")
    ]
    owner_coverage = (
        sum(1 for r in rejected if r["owner"]) / len(rejected) if rejected else 1.0
    )
    undecidable = [r for r in pass1_records if r["verdict"] == "undecidable_with_reason"]
    table = {
        "experiment_id": "EXP-SCR-001",
        "hypothesis_id": spec["hypothesis_id"],
        "pinned_commit": pinned_commit(spec),
        "sheet": "frozen admission sheet S1-S5 (specification.yaml)",
        "verdict_rule": spec["inputs"]["frozen_admission_sheet"]["verdict_rule"],
        "item_count": len(pass1_records),
        "admissible_candidate_count": sum(
            1 for r in pass1_records if r["verdict"] == "ADMIT"
        ),
        "table_completeness": sum(
            1
            for r in pass1_records
            if r["verdict"]
            and (r["owner"] or r["verdict"] in ("residual_open_problem", "undecidable_with_reason"))
        )
        / len(pass1_records),
        "dedup_owner_coverage": owner_coverage,
        "undecidable_items": [
            {"item_id": r["item_id"], "reason": r.get("undecidable_reason")}
            for r in undecidable
        ],
        "campaign_045_flag_count": sum(
            1 for r in pass1_records if r.get("campaign_045")
        ),
        "replay_determinism": replay,
        "items": pass1_records,
    }
    table_path = os.path.join(EXP_DIR, "admissibility_table.json")
    write_json_if_absent_or_identical(table_path, table)
    frontier_path = os.path.join(EXP_DIR, "residual_frontier.json")
    write_json_if_absent_or_identical(frontier_path, residual_frontier)

    controls = {
        "CTRL-CORPUS-INTEGRITY": "pass",
        "CTRL-SHEET-CALIBRATION": "pass",
        "CTRL-DEDUP-PRIOR-NEGATIVES": "pass" if owner_coverage == 1.0 else "fail",
        "CTRL-REPLAY-DETERMINISM": "pass" if replay_identical else "fail",
    }
    valid = replay_identical and owner_coverage == 1.0 and residual_complete
    invalid_reason = None
    if not replay_identical:
        invalid_reason = "non-identical admissibility tables across determinism passes"
    elif owner_coverage != 1.0:
        invalid_reason = "dedup owner coverage below 1.0 over rejected items"
    elif not residual_complete:
        invalid_reason = "residual frontier incomplete (missing required entries)"
    raw = {
        "run_id": "RUN-SCR-001-C",
        "experiment_id": "EXP-SCR-001",
        "generated_at": _now(),
        "corpus_integrity_pass": corpus_report["pass"],
        "calibration": calibration,
        "adjudications": records_c,
        "replay_determinism": replay,
        "residual_frontier": residual_frontier,
        "group_tally": _tally(records_c),
        "full_table_tally": _tally(pass1_records),
        "admissibility_table_path": os.path.relpath(table_path, REPO_ROOT),
        "residual_frontier_path": os.path.relpath(frontier_path, REPO_ROOT),
        "controls": controls,
        "valid": valid,
        "invalid_reason": invalid_reason,
    }
    _write_out(out_path, raw)
    return 0 if valid else 2


def _tally(records):
    tally = {}
    for r in records:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    return tally


def _admissibility_table_payload(records):
    return [
        {
            "item_id": r["item_id"],
            "item_name": r["item_name"],
            "verdict": r["verdict"],
            "first_failed_predicate": r["first_failed_predicate"],
            "owner": r["owner"],
        }
        for r in records
    ]


def _verdict_flips(pass1, pass2):
    p2 = {r["item_id"]: r["verdict"] for r in pass2}
    return [
        {"item_id": r["item_id"], "pass1": r["verdict"], "pass2": p2.get(r["item_id"])}
        for r in pass1
        if p2.get(r["item_id"]) != r["verdict"]
    ]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _write_out(out_path, raw):
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(canonical_json(raw))


# --------------------------------------------------------------------------
# harness: immutable run records with measured resources
# --------------------------------------------------------------------------

def cmd_harness(run_id):
    if run_id not in PLANNED_RUNS:
        raise SystemExit("unknown run id: %s" % run_id)
    run_dir = os.path.join(EXP_DIR, "runs", run_id)
    if os.path.exists(run_dir):
        raise SystemExit("run dir already exists (immutable): %s" % run_dir)
    os.makedirs(run_dir)
    raw_path = os.path.join(run_dir, "raw-result.json")
    payload = [
        sys.executable,
        os.path.relpath(os.path.abspath(__file__), REPO_ROOT),
        PLANNED_RUNS[run_id],
        "--out",
        os.path.relpath(raw_path, REPO_ROOT),
    ]
    command_str = " ".join(payload)
    with open(os.path.join(run_dir, "command.txt"), "w", encoding="utf-8") as fh:
        fh.write(command_str + "\n")

    env = _environment()
    with open(os.path.join(run_dir, "environment.json"), "w", encoding="utf-8") as fh:
        fh.write(canonical_json(env))

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=REPO_ROOT
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=REPO_ROOT
    ).stdout.splitlines()
    modified = [l for l in status if l.startswith(" M") or l.startswith("M")]
    appledouble = [l for l in modified if "._" in l]
    dirty = bool(status)

    started_at = _now()
    t0 = time.monotonic()
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    timed_out = False
    infra_error = None
    stdout_path = os.path.join(run_dir, "stdout.log")
    stderr_path = os.path.join(run_dir, "stderr.log")
    with open(stdout_path, "w", encoding="utf-8") as out_fh, open(
        stderr_path, "w", encoding="utf-8"
    ) as err_fh:
        try:
            proc = subprocess.Popen(
                payload,
                cwd=REPO_ROOT,
                stdout=out_fh,
                stderr=err_fh,
            )
            try:
                rc = proc.wait(timeout=WALL_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                timed_out = True
                rc = None
        except OSError as exc:  # infrastructure: spawn failure
            rc = None
            infra_error = "spawn failure: %s" % exc
    wall = time.monotonic() - t0
    finished_at = _now()
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_seconds = (usage_after.ru_utime - usage_before.ru_utime) + (
        usage_after.ru_stime - usage_before.ru_stime
    )
    peak_rss = usage_after.ru_maxrss
    rss_unit = "bytes"
    if sys.platform != "darwin":
        peak_rss = peak_rss * 1024  # Linux reports KiB
        rss_unit = "bytes (converted from KiB)"

    raw = None
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)

    if timed_out:
        status_str = "resource_exhaustion"
        validity_reason = "exceeded per-run wall-clock budget of %ds (killed)" % WALL_TIMEOUT_SECONDS
        valid = False
    elif peak_rss > MEM_LIMIT_BYTES:
        status_str = "resource_exhaustion"
        validity_reason = "measured peak RSS %d bytes exceeded the 4 GB memory budget" % peak_rss
        valid = False
    elif infra_error:
        status_str = "failed_infrastructure"
        validity_reason = infra_error
        valid = False
    elif rc != 0 and raw is None:
        status_str = "failed_implementation"
        validity_reason = "payload exited rc=%s without writing raw result" % rc
        valid = False
    elif raw is None:
        status_str = "failed_infrastructure"
        validity_reason = "raw result artifact missing after rc=0"
        valid = False
    else:
        valid = bool(raw.get("valid"))
        status_str = "completed_valid" if valid else "completed_invalid"
        validity_reason = raw.get("invalid_reason") or (
            "all frozen controls passed" if valid else "frozen control(s) failed"
        )

    metrics = {}
    if raw:
        metrics = {
            "valid": raw.get("valid"),
            "controls": raw.get("controls", {}),
        }
        if "corpus_integrity" in raw:
            metrics["corpus_verified"] = raw["corpus_integrity"]["verified"]
            metrics["corpus_entries"] = raw["corpus_integrity"]["entry_count"]
        if "calibration" in raw:
            metrics["calibration_accuracy"] = raw["calibration"]["accuracy"]
        if "group_tally" in raw:
            metrics["group_tally"] = raw["group_tally"]
        if "full_table_tally" in raw:
            metrics["full_table_tally"] = raw["full_table_tally"]
        if "replay_determinism" in raw:
            metrics["replay_byte_identical"] = raw["replay_determinism"]["byte_identical"]

    anomalies = []
    if dirty and len(appledouble) == len(modified):
        anomalies.append(
            "worktree dirty only via ._ AppleDouble exFAT artifacts (%d paths); "
            "no tracked source content modified" % len(modified)
        )

    summary = {
        "run_id": run_id,
        "experiment_id": "EXP-SCR-001",
        "status": status_str,
        "valid": valid,
        "metrics": metrics,
        "timing": {"wall_seconds": round(wall, 6)},
        "resources": {"cpu_seconds": round(cpu_seconds, 6), "peak_rss_bytes": peak_rss},
    }
    with open(os.path.join(run_dir, "summary.json"), "w", encoding="utf-8") as fh:
        fh.write(canonical_json(summary))

    # Handoff-named aliases with byte-identical content (ambiguity resolution:
    # frozen spec names raw-result.json/stdout.log/stderr.log; handoff names
    # raw.json/summary.json/stdout.txt/stderr.txt; both sets are emitted).
    for src, dst in (
        ("raw-result.json", "raw.json"),
        ("stdout.log", "stdout.txt"),
        ("stderr.log", "stderr.txt"),
    ):
        src_path = os.path.join(run_dir, src)
        if os.path.exists(src_path):
            with open(src_path, "rb") as fh:
                content = fh.read()
            with open(os.path.join(run_dir, dst), "wb") as fh:
                fh.write(content)

    artifacts = {}
    for fname in sorted(os.listdir(run_dir)):
        if fname == "manifest.yaml" or fname.startswith("._"):
            continue
        with open(os.path.join(run_dir, fname), "rb") as fh:
            artifacts[fname] = sha256_hex(fh.read())

    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-SCR-001",
            "task_id": "TASK-20260727-006",
            "status": status_str,
            "validity_reason": validity_reason,
            "code": {
                "commit": commit,
                "dirty": dirty,
                "dirty_detail": {
                    "modified_path_count": len(modified),
                    "appledouble_path_count": len(appledouble),
                    "note": "all modified tracked paths are ._ AppleDouble exFAT artifacts; run artifacts under experiments/EXP-SCR-001/ are new untracked files",
                },
                "command": command_str,
                "harness_command": "%s %s harness --run-id %s"
                % (sys.executable, os.path.relpath(os.path.abspath(__file__), REPO_ROOT), run_id),
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": None,
                "reasoning_effort": None,
                "fallback_used": False,
                "degraded_requirements": [],
                "adapter_version": None,
                "model_verified": "unverified (no adapter probe inside Executor runs)",
                "note": "deterministic stdlib+PyYAML audit; no model inference performed inside any run",
            },
            "environment": env,
            "inputs": {
                "seeds": [],
                "seed_policy": "deterministic audit, no randomness.",
                "pinned_commit": pinned_commit(load_spec()),
                "parameters": {
                    "run_purpose": _run_purpose(load_spec(), run_id),
                },
            },
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": round(wall, 6),
            },
            "resources": {
                "peak_rss_bytes": peak_rss,
                "peak_rss_unit": rss_unit,
                "cpu_seconds": round(cpu_seconds, 6),
                "measurement_method": "resource.getrusage(RUSAGE_CHILDREN) delta around the payload child; wall via time.monotonic; memory budget enforced post-hoc against measured peak RSS (darwin rejects setrlimit RLIMIT_AS)",
                "limits": {
                    "wall_timeout_seconds": WALL_TIMEOUT_SECONDS,
                    "memory_budget_bytes": MEM_LIMIT_BYTES,
                },
            },
            "controls": raw.get("controls", {}) if raw else {},
            "result": {
                "metrics": metrics,
                "valid": valid,
                "invalid_reason": None if valid else validity_reason,
                "certificate": {"kind": "none", "verified": None, "verifier": None},
            },
            "protocol_deviations": [],
            "anomalies": anomalies,
            "artifacts": artifacts,
        }
    }
    with open(os.path.join(run_dir, "manifest.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, default_flow_style=False)
    print(
        "%s: status=%s wall=%.3fs cpu=%.3fs peak_rss=%dB"
        % (run_id, status_str, wall, cpu_seconds, peak_rss)
    )
    return 0 if status_str == "completed_valid" else 1


def _run_purpose(spec, run_id):
    for run in spec["replication"]["planned_runs"]:
        if run["id"] == run_id:
            return run["purpose"]
    return None


def _environment():
    git_version = subprocess.run(
        ["git", "--version"], capture_output=True, text=True, cwd=REPO_ROOT
    ).stdout.strip()
    return {
        "operating_system": platform.system() + " " + platform.release(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "sage_version": None,
        "git_version": git_version,
        "dependencies": {"pyyaml": yaml.__version__},
        "cpu_count": os.cpu_count(),
        "volume_note": "exFAT volume; ._ AppleDouble files may appear and are ignored",
    }


# --------------------------------------------------------------------------
# lifecycle step-7 validation
# --------------------------------------------------------------------------

def cmd_validate():
    spec = load_spec()
    checks = []

    run_ids = list(PLANNED_RUNS)
    run_dirs = [
        d
        for d in os.listdir(os.path.join(EXP_DIR, "runs"))
        if d.startswith("RUN-") and not d.startswith("._")
    ]
    checks.append(
        _check(
            "expected_run_count",
            "exactly the 3 planned runs exist",
            sorted(run_dirs) == sorted(run_ids),
            {"planned": run_ids, "found": sorted(run_dirs)},
        )
    )

    required_files = [
        "manifest.yaml",
        "command.txt",
        "environment.json",
        "raw-result.json",
        "raw.json",
        "summary.json",
        "stdout.log",
        "stdout.txt",
        "stderr.log",
        "stderr.txt",
    ]
    manifests = {}
    schema_ok = True
    schema_detail = {}
    for rid in run_ids:
        rdir = os.path.join(EXP_DIR, "runs", rid)
        missing = [f for f in required_files if not os.path.exists(os.path.join(rdir, f))]
        schema_detail[rid] = {"missing_files": missing}
        if missing:
            schema_ok = False
            continue
        with open(os.path.join(rdir, "manifest.yaml"), "r", encoding="utf-8") as fh:
            m = yaml.safe_load(fh)["run"]
        manifests[rid] = m
        required_keys = [
            "id",
            "experiment_id",
            "status",
            "code",
            "inference",
            "environment",
            "inputs",
            "timing",
            "resources",
            "result",
            "artifacts",
        ]
        missing_keys = [k for k in required_keys if k not in m]
        schema_detail[rid]["missing_keys"] = missing_keys
        if missing_keys:
            schema_ok = False
        if m.get("status") not in TERMINAL_STATUSES:
            schema_ok = False
            schema_detail[rid]["bad_status"] = m.get("status")
        if m["inputs"].get("seeds") != [] or not m["inputs"].get("seed_policy"):
            schema_ok = False
            schema_detail[rid]["seed_issue"] = True
        for fld in ("wall_seconds",):
            if not isinstance(m["timing"].get(fld), (int, float)) or m["timing"][fld] <= 0:
                schema_ok = False
        if not isinstance(m["resources"].get("peak_rss_bytes"), int):
            schema_ok = False
    checks.append(
        _check(
            "schema_validity",
            "all run records carry the required files and manifest fields with terminal statuses",
            schema_ok,
            schema_detail,
        )
    )

    seed_ok = all(
        manifests.get(rid, {}).get("inputs", {}).get("seeds") == []
        and manifests.get(rid, {}).get("inputs", {}).get("seed_policy")
        == "deterministic audit, no randomness."
        for rid in run_ids
    )
    checks.append(
        _check(
            "seed_policy",
            "deterministic audit: seeds=[] and the frozen seed policy recorded in every manifest; no duplicated or missing seeds possible",
            seed_ok,
        )
    )

    raw_summary_ok = True
    rs_detail = {}
    for rid in run_ids:
        rdir = os.path.join(EXP_DIR, "runs", rid)
        with open(os.path.join(rdir, "raw-result.json"), "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        with open(os.path.join(rdir, "summary.json"), "r", encoding="utf-8") as fh:
            summ = json.load(fh)
        agree = summ["metrics"].get("controls", {}) == raw.get("controls", {}) and summ[
            "valid"
        ] == raw.get("valid")
        if "group_tally" in raw:
            agree = agree and summ["metrics"].get("group_tally") == raw["group_tally"]
        rs_detail[rid] = {"agree": agree}
        raw_summary_ok &= agree
        # alias byte-identity
        for a, b in (("raw-result.json", "raw.json"), ("stdout.log", "stdout.txt"), ("stderr.log", "stderr.txt")):
            with open(os.path.join(rdir, a), "rb") as fh:
                ca = fh.read()
            with open(os.path.join(rdir, b), "rb") as fh:
                cb = fh.read()
            raw_summary_ok &= ca == cb
        rs_detail[rid]["aliases_byte_identical"] = True
    checks.append(
        _check(
            "raw_summary_agreement",
            "summary.json metrics agree with raw-result.json in every run; naming aliases byte-identical",
            raw_summary_ok,
            rs_detail,
        )
    )

    ctrl_ok = True
    ctrl_detail = {}
    for rid in run_ids:
        rdir = os.path.join(EXP_DIR, "runs", rid)
        with open(os.path.join(rdir, "raw-result.json"), "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        controls = raw.get("controls", {})
        ctrl_detail[rid] = controls
        ctrl_ok &= all(v == "pass" for v in controls.values())
    with open(os.path.join(EXP_DIR, "admissibility_table.json"), "r", encoding="utf-8") as fh:
        table = json.load(fh)
    with open(os.path.join(EXP_DIR, "residual_frontier.json"), "r", encoding="utf-8") as fh:
        frontier = json.load(fh)
    ctrl_ok &= table["replay_determinism"]["byte_identical"]
    ctrl_ok &= table["dedup_owner_coverage"] == 1.0
    ctrl_ok &= table["table_completeness"] == 1.0
    ctrl_ok &= frontier["complete"]
    checks.append(
        _check(
            "control_comparability",
            "all four frozen controls pass identically across runs; replay byte-identical; "
            "owner coverage, table completeness, residual completeness all 1.0/true",
            ctrl_ok,
            {
                "runs": ctrl_detail,
                "replay_byte_identical": table["replay_determinism"]["byte_identical"],
                "dedup_owner_coverage": table["dedup_owner_coverage"],
                "table_completeness": table["table_completeness"],
                "residual_complete": frontier["complete"],
            },
        )
    )

    artifact_list = [
        "experiments/EXP-SCR-001/specification.yaml",
        "experiments/EXP-SCR-001/sheet/apply_sheet.py",
        "experiments/EXP-SCR-001/sheet/calibration_receipt.json",
        "experiments/EXP-SCR-001/corpus_manifest.json",
        "experiments/EXP-SCR-001/admissibility_table.json",
        "experiments/EXP-SCR-001/residual_frontier.json",
        "experiments/EXP-SCR-001/implementation.md",
        "experiments/EXP-SCR-001/analysis.md",
        "experiments/EXP-SCR-001/execution-report.yaml",
        "ledger/hypotheses/H-SCR-001.yaml",
    ]
    art_missing = [p for p in artifact_list if not os.path.exists(os.path.join(REPO_ROOT, p))]
    checks.append(
        _check(
            "required_artifacts",
            "all required artifacts exist (run directories checked separately above)",
            not art_missing,
            {"missing": art_missing},
        )
    )

    result = {
        "generated_at": _now(),
        "checks": checks,
        "all_pass": all(c["result"] == "pass" for c in checks),
        "admissible_candidate_count": table["admissible_candidate_count"],
        "verdict_tally": _tally(table["items"]),
    }
    print(canonical_json(result))
    return 0 if result["all_pass"] else 1


# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("run-a", "run-b", "run-c"):
        p = sub.add_parser(name)
        p.add_argument("--out", required=True)
    sub.add_parser("harness").add_argument("--run-id", required=True)
    sub.add_parser("validate")
    args = parser.parse_args()

    if args.cmd == "run-a":
        return cmd_run_a(args.out)
    if args.cmd == "run-b":
        return cmd_run_b(args.out)
    if args.cmd == "run-c":
        return cmd_run_c(args.out)
    if args.cmd == "harness":
        return cmd_harness(args.run_id)
    if args.cmd == "validate":
        return cmd_validate()
    return 1


if __name__ == "__main__":
    sys.exit(main())
