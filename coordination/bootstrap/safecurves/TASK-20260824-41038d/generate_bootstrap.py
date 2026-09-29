#!/usr/bin/env python3
"""Generate the bounded SafeCurves campaign bootstrap.

This is a control-plane generator, not an experiment.  It allocates every
record identifier through the repository allocator, constructs all launch
records in memory, and then installs them atomically one file at a time.  It
does not dispatch any task, run any curve computation, or make any safety or
vulnerability conclusion.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable

import yaml


BOOTSTRAP_TASK_ID = "TASK-20260824-41038d"
EXPECTED_BRANCH = "research/safecurves-goals-20260824"
CREATED_AT = "2026-08-24T00:00:00-07:00"
GENERATOR_REL = Path(
    "coordination/bootstrap/safecurves/"
    f"{BOOTSTRAP_TASK_ID}/generate_bootstrap.py"
)
BOOTSTRAP_DIR_REL = GENERATOR_REL.parent
TOP_HANDOFF_REL = Path("ledger/handoffs") / f"{BOOTSTRAP_TASK_ID}.yaml"
MANIFEST_REL = BOOTSTRAP_DIR_REL / "manifest.yaml"
BOOTSTRAP_RECEIPT_REL = BOOTSTRAP_DIR_REL / "snapshot-receipt.json"

CRITERIA = (
    "field",
    "equation",
    "base",
    "rho",
    "transfer",
    "disc",
    "rigid",
    "ladder",
    "twist",
    "complete",
    "ind",
)

CATEGORIES = {
    "basic_parameter_requirements": ["field", "equation", "base"],
    "ecdlp_security_requirements": ["rho", "transfer", "disc"],
    "ecc_security_beyond_ecdlp": [
        "rigid",
        "ladder",
        "twist",
        "complete",
        "ind",
    ],
}

FIELD_BITS = {
    "Anomalous": 204,
    "M-221": 221,
    "E-222": 222,
    "NIST P-224": 224,
    "Curve1174": 251,
    "Curve25519": 255,
    "BN(2,254)": 254,
    "brainpoolP256t1": 256,
    "ANSSI FRP256v1": 256,
    "NIST P-256": 256,
    "secp256k1": 256,
    "E-382": 382,
    "M-383": 383,
    "Curve383187": 383,
    "brainpoolP384t1": 384,
    "NIST P-384": 384,
    "Curve41417": 414,
    "Ed448-Goldilocks": 448,
    "M-511": 511,
    "E-521": 521,
}

SOURCE_POINTERS = [
    "https://safecurves.cr.yp.to/",
    "https://safecurves.cr.yp.to/transfer.html",
    "https://safecurves.cr.yp.to/disc.html",
    "https://safecurves.cr.yp.to/rigid.html",
    "https://safecurves.cr.yp.to/ladder.html",
    "https://safecurves.cr.yp.to/twist.html",
    "https://safecurves.cr.yp.to/complete.html",
    "https://safecurves.cr.yp.to/ind.html",
    "https://safecurves.cr.yp.to/verify.html",
]

ADDITIONAL_DIAGNOSTICS = [
    "complete curve and twist order factorization with checkable certificates",
    "subgroup, cofactor, and invalid-curve confinement costs",
    "automorphism- and endomorphism-adjusted rho cost",
    "embedding-degree certificate or explicit search bound",
    "CM discriminant and conductor structure",
    "model-conversion exceptional sets",
    "scalar and multiscalar formula exceptional-case search",
    "deterministic parameter-generation transcript audit",
]

CLAIM_BOUNDARIES = [
    "Every SafeCurves True or False cell is user-supplied, unverified intake and a preregistered comparison target; it is not evidence.",
    "A failure of rigidity, ladder availability, completeness, or indistinguishability is not by itself an ECDLP break.",
    "The Anomalous and BN(2,254) rows are positive-control candidates for the described transfer or small-discriminant behavior, not newly discovered attacks; their parameters and behavior still require sourced reproduction.",
    "The declared diagnostic list is deliberately non-exhaustive; a sourced, measurable additional parameter-level weakness may be added through a later scoped handoff.",
    "Infrastructure errors, timeouts, unavailable dependencies, and budget stops are operational observations, never mathematical evidence.",
]

COMPLETION_CRITERIA = [
    "Reconcile the exact parameter tuple to retrieved primary or authoritative sources, record citation provenance, and adjudicate every conflict.",
    "Produce a fully sourced, certificate-bearing dossier for each of the eleven declared SafeCurves lanes, including method, controls, raw/checkable artifacts, tested boundary, falsifier, and limitations.",
    "Evaluate every declared additional diagnostic with checkable certificates or an explicit reproducible bound, and state any untested or only partially tested scope.",
    "Adjudicate every disagreement with the preregistered SafeCurves row without treating the intake row as ground truth.",
    "Obtain independent validation of artifacts and controls plus independent review of any proposed interpretation before a Coordinator synthesis or status transition.",
    "Archive producer, validation, review, decision, and synthesis records through the durable snapshot and ledger mechanisms required by the repository.",
]

PAUSE_CONDITIONS = [
    "Archive, queue, identifier, or ledger integrity cannot be established.",
    "A required non-degradable independent review policy cannot be honored by an allowed non-Bedrock backend.",
    "Primary or authoritative sources leave an unresolved conflict in the named curve's parameter tuple.",
    "The campaign reaches its declared batch or wall-clock budget before the evidentiary completion criteria are met.",
]

# Exact user-supplied intake.  The booleans are comparison targets only.
CURVES = [
    {
        "name": "Anomalous",
        "equation": "y^2 = x^3+15347898055371580590890576721314318823207531963035637503096292x+7444386449934505970367865204569124728350661870959593404279615",
        "modulus": "17676318486848893030961583018778670610489016512983351739677143",
        "safe": False,
        "cells": [True, True, True, True, False, False, True, False, False, False, False],
        "details": "Created as an illustration of additive transfer and small discriminant.",
    },
    {
        "name": "M-221",
        "equation": "y^2 = x^3+117050x^2+x",
        "modulus": "2^221 - 3",
        "safe": True,
        "cells": [True] * 11,
        "details": "2013 Aranha-Barreto-Pereira-Ricardini (formerly named Curve2213)",
    },
    {
        "name": "E-222",
        "equation": "x^2+y^2 = 1+160102x^2y^2",
        "modulus": "2^222 - 117",
        "safe": True,
        "cells": [True] * 11,
        "details": "2013 Aranha-Barreto-Pereira-Ricardini",
    },
    {
        "name": "NIST P-224",
        "equation": "y^2 = x^3-3x+18958286285566608000408668544493926415504680968679321075787234672564",
        "modulus": "2^224 - 2^96 + 1",
        "safe": False,
        "cells": [True, True, True, True, True, True, False, False, False, False, False],
        "details": "2000 NIST; also in SEC 2",
    },
    {
        "name": "Curve1174",
        "equation": "x^2+y^2 = 1-1174x^2y^2",
        "modulus": "2^251 - 9",
        "safe": True,
        "cells": [True] * 11,
        "details": "2013 Bernstein-Hamburg-Krasnova-Lange",
    },
    {
        "name": "Curve25519",
        "equation": "y^2 = x^3+486662x^2+x",
        "modulus": "2^255 - 19",
        "safe": True,
        "cells": [True] * 11,
        "details": "2006 Bernstein",
    },
    {
        "name": "BN(2,254)",
        "equation": "y^2 = x^3+0x+2",
        "modulus": "16798108731015832284940804142231733909889187121439069848933715426072753864723",
        "safe": False,
        "cells": [True, True, True, True, False, False, True, False, False, False, False],
        "details": "2011 Pereira-Simplicio-Naehrig-Barreto pairing-friendly curve. Included as an illustration of multiplicative transfer and small discriminant.",
    },
    {
        "name": "brainpoolP256t1",
        "equation": "y^2 = x^3-3x+46214326585032579593829631435610129746736367449296220983687490401182983727876",
        "modulus": "76884956397045344220809746629001649093037950200943055203735601445031516197751",
        "safe": False,
        "cells": [True, True, True, True, True, True, True, False, False, False, False],
        "details": "2005 Brainpool",
    },
    {
        "name": "ANSSI FRP256v1",
        "equation": "y^2 = x^3-3x+107744541122042688792155207242782455150382764043089114141096634497567301547839",
        "modulus": "109454571331697278617670725030735128145969349647868738157201323556196022393859",
        "safe": False,
        "cells": [True, True, True, True, True, True, False, False, False, False, False],
        "details": "2011 ANSSI",
    },
    {
        "name": "NIST P-256",
        "equation": "y^2 = x^3-3x+41058363725152142129326129780047268409114441015993725554835256314039467401291",
        "modulus": "2^256 - 2^224 + 2^192 + 2^96 - 1",
        "safe": False,
        "cells": [True, True, True, True, True, True, False, False, True, False, False],
        "details": "2000 NIST; also in SEC 2 and NSA Suite B",
    },
    {
        "name": "secp256k1",
        "equation": "y^2 = x^3+0x+7",
        "modulus": "2^256 - 2^32 - 977",
        "safe": False,
        "cells": [True, True, True, True, True, False, True, False, True, False, False],
        "details": "SEC2",
    },
    {
        "name": "E-382",
        "equation": "x^2+y^2 = 1-67254x^2y^2",
        "modulus": "2^382 - 105",
        "safe": True,
        "cells": [True] * 11,
        "details": "2013 Aranha-Barreto-Pereira-Ricardini",
    },
    {
        "name": "M-383",
        "equation": "y^2 = x^3+2065150x^2+x",
        "modulus": "2^383 - 187",
        "safe": True,
        "cells": [True] * 11,
        "details": "2013 Aranha-Barreto-Pereira-Ricardini",
    },
    {
        "name": "Curve383187",
        "equation": "y^2 = x^3+229969x^2+x",
        "modulus": "2^383 - 187",
        "safe": True,
        "cells": [True] * 11,
        "details": "2013 Aranha-Barreto-Pereira-Ricardini; authors subsequently recommended switching to M-383",
    },
    {
        "name": "brainpoolP384t1",
        "equation": "y^2 = x^3-3x+19596161053329239268181228455226581162286252326261019516900162717091837027531392576647644262320816848087868142547438",
        "modulus": "21659270770119316173069236842332604979796116387017648600081618503821089934025961822236561982844534088440708417973331",
        "safe": False,
        "cells": [True, True, True, True, True, True, True, False, True, False, False],
        "details": "2005 Brainpool",
    },
    {
        "name": "NIST P-384",
        "equation": "y^2 = x^3-3x+27580193559959705877849011840389048093056905856361568521428707301988689241309860865136260764883745107765439761230575",
        "modulus": "2^384 - 2^128 - 2^96 + 2^32 - 1",
        "safe": False,
        "cells": [True, True, True, True, True, True, False, False, True, False, False],
        "details": "2000 NIST; also in SEC 2 and NSA Suite B",
    },
    {
        "name": "Curve41417",
        "equation": "x^2+y^2 = 1+3617x^2y^2",
        "modulus": "2^414 - 17",
        "safe": True,
        "cells": [True] * 11,
        "details": "2013 Bernstein-Lange (formerly named Curve3617)",
    },
    {
        "name": "Ed448-Goldilocks",
        "equation": "x^2+y^2 = 1-39081x^2y^2",
        "modulus": "2^448 - 2^224 - 1",
        "safe": True,
        "cells": [True] * 11,
        "details": "2014 Hamburg",
    },
    {
        "name": "M-511",
        "equation": "y^2 = x^3+530438x^2+x",
        "modulus": "2^511 - 187",
        "safe": True,
        "cells": [True] * 11,
        "details": "2013 Aranha-Barreto-Pereira-Ricardini (formerly named Curve511187)",
    },
    {
        "name": "E-521",
        "equation": "x^2+y^2 = 1-376014x^2y^2",
        "modulus": "2^521 - 1",
        "safe": True,
        "cells": [True] * 11,
        "details": "2013 Bernstein-Lange; independently 2013 Hamburg; independently 2013 Aranha-Barreto-Pereira-Ricardini",
    },
]


class BootstrapError(RuntimeError):
    """A refusal that must occur before target research records are written."""


def run_checked(argv: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        argv,
        cwd=root,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise BootstrapError(
            f"command failed ({proc.returncode}): {argv!r}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def resolve_and_check_root() -> tuple[Path, str, str]:
    here = Path(__file__).resolve()
    root = next(
        (
            parent
            for parent in here.parents
            if (parent / "AGENTS.md").is_file()
            and (parent / "agents/coordinator.md").is_file()
            and (parent / "tools/allocate_id.py").is_file()
            and (parent / "tools/validate_ledger.py").is_file()
        ),
        None,
    )
    if root is None:
        raise BootstrapError("could not resolve the intended repository root")
    if here != (root / GENERATOR_REL).resolve():
        raise BootstrapError(
            f"generator must be located at {GENERATOR_REL.as_posix()}"
        )

    git_root = Path(
        run_checked(["git", "rev-parse", "--show-toplevel"], root).stdout.strip()
    ).resolve()
    if git_root != root:
        raise BootstrapError(f"Git root {git_root} does not match {root}")

    branch = run_checked(
        ["git", "symbolic-ref", "--quiet", "--short", "HEAD"], root
    ).stdout.strip()
    if branch != EXPECTED_BRANCH:
        raise BootstrapError(
            f"refusing branch {branch!r}; expected {EXPECTED_BRANCH!r}"
        )

    head = run_checked(["git", "rev-parse", "HEAD"], root).stdout.strip()
    origin_main = run_checked(
        ["git", "rev-parse", "--verify", "origin/main"], root
    ).stdout.strip()
    if head != origin_main:
        raise BootstrapError(
            "HEAD must equal the execution-time origin/main before bootstrap generation; "
            f"HEAD={head}, origin/main={origin_main}"
        )

    status_lines = [
        line
        for line in run_checked(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"], root
        ).stdout.splitlines()
        if line
    ]
    unexpected = []
    for line in status_lines:
        # The only permitted pre-generation worktree change is this generator.
        path_text = line[3:] if len(line) >= 4 else ""
        if " -> " in path_text or path_text != GENERATOR_REL.as_posix():
            unexpected.append(line)
    if unexpected:
        raise BootstrapError(
            "worktree contains changes other than the generator: "
            + json.dumps(unexpected)
        )
    return root, head, origin_main


FREE_ID_LINE = re.compile(r"^\s*free\s+[^:]+:\s*([A-Z0-9-]+)\s*$", re.I)


def allocate_id(
    root: Path,
    record_type: str,
    expected: re.Pattern[str],
    allocated: set[str],
    *,
    area: str | None = None,
    date: str | None = None,
) -> str:
    argv = ["python3", "tools/allocate_id.py", "--next", record_type]
    if area is not None:
        argv.extend(["--area", area])
    if date is not None:
        argv.extend(["--date", date])
    proc = run_checked(argv, root)
    matches = []
    for line in proc.stdout.splitlines():
        match = FREE_ID_LINE.fullmatch(line)
        if match:
            matches.append(match.group(1))
    if len(matches) != 1:
        raise BootstrapError(
            "allocator output must contain exactly one 'free <type>: <id>' line; "
            f"got {matches!r} from stdout {proc.stdout!r}"
        )
    record_id = matches[0]
    if not expected.fullmatch(record_id):
        raise BootstrapError(
            f"allocator returned malformed {record_type} id {record_id!r}"
        )
    run_checked(
        ["python3", "tools/allocate_id.py", "--check", record_id], root
    )
    if record_id in allocated:
        raise BootstrapError(f"duplicate allocated identifier {record_id}")
    allocated.add(record_id)
    return record_id


def matrix_row(curve: dict[str, Any]) -> dict[str, bool]:
    return dict(zip(CRITERIA, curve["cells"], strict=True))


def intake(curve: dict[str, Any]) -> dict[str, Any]:
    return {
        "provenance": "user_supplied_unverified",
        "verification_status": "unverified",
        "comparison_target_only": True,
        "curve": curve["name"],
        "equation": curve["equation"],
        "modulus": curve["modulus"],
        "details": curve["details"],
        "expected_safe": curve["safe"],
        "expected_criteria": matrix_row(curve),
        "criterion_order": list(CRITERIA),
    }


def task_handoff(
    *,
    task_id: str,
    to: str,
    objective: str,
    uncertainty_reduced: str,
    inputs: list[Any],
    constraints: list[str],
    deliverables: list[str],
    artifact_paths: list[str],
    read_scope: list[str],
    write_scope: list[str],
    archived_by: str,
    policy: str,
    budget: dict[str, int],
    completion_gate: list[str],
    independent: bool = False,
    archive: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": task_id,
        "from": "coordinator",
        "to": to,
        "objective": objective,
        "uncertainty_reduced": uncertainty_reduced,
        "inputs": inputs,
        "constraints": constraints,
        "deliverables": deliverables,
        "artifact_paths": artifact_paths,
        "read_scope": read_scope,
        "write_scope": write_scope,
        "archived_by": archived_by,
        "inference": {
            "policy": policy,
            "reasoning_effort": None,
            "fallback_allowed": False,
            "degraded_allowed": False,
            "independent_session_required": independent,
        },
        "budget": budget,
        "completion_gate": completion_gate,
        "review_plan": None,
    }
    if archive is not None:
        result["archive"] = archive
    return result


def goal_record(
    curve: dict[str, Any],
    ids: dict[str, str],
    paths: dict[str, str],
    base_commit: str,
) -> dict[str, Any]:
    return {
        "id": ids["goal"],
        "title": f"Certificate-bearing SafeCurves parameter audit: {curve['name']}",
        "status": "active",
        "owner": "coordinator",
        "created_at": CREATED_AT,
        "updated_at": CREATED_AT,
        "runtime": {"provider": "none", "goal_id": None},
        "question_ids": [ids["rq"]],
        "latest_verified_commit": base_commit,
        "latest_verified_commit_note": "This is the execution-time pre-bootstrap HEAD/origin-main commit; the containing snapshot commit is bound only by the post-commit receipt to avoid a fixed-point claim.",
        "objective": (
            f"Independently reproduce and source the eleven SafeCurves criteria for "
            f"{curve['name']} (field, equation, base, rho, transfer, discriminant, "
            "rigidity, ladder, twist, completeness, and indistinguishability), then "
            "measure prioritized additional parameter-level weakness diagnostics "
            "without treating the intake table as evidence."
        ),
        "intake": intake(curve),
        "criterion_categories": CATEGORIES,
        "additional_diagnostics": ADDITIONAL_DIAGNOSTICS,
        "claim_boundaries": CLAIM_BOUNDARIES,
        "completion_criteria": COMPLETION_CRITERIA,
        "pause_conditions": PAUSE_CONDITIONS,
        "campaign_budget": {
            "maximum_batches": 5,
            "total_wall_clock_seconds": 18000,
            "max_concurrent": 2,
        },
        "current_batch_id": ids["batch"],
        "dispatch_queue_path": paths["queue"],
        "next_action": (
            f"Dispatch only {ids['idea_task']} to produce the primary-source "
            "parameter capsule and falsifiable prioritized audit plan."
        ),
    }


def rq_record(
    curve: dict[str, Any], ids: dict[str, str], paths: dict[str, str]
) -> dict[str, Any]:
    return {
        "id": ids["rq"],
        "goal_id": ids["goal"],
        "title": f"SafeCurves parameter-safety audit question: {curve['name']}",
        "status": "active",
        "owner": "coordinator",
        "created_at": CREATED_AT,
        "updated_at": CREATED_AT,
        "question": (
            f"For the exact user-supplied {curve['name']} tuple, which of the eleven "
            "SafeCurves comparison targets can be independently reproduced with "
            "certificates, what measurable parameter-level weaknesses or cost changes "
            "appear under the declared additional diagnostics, and what remains untested?"
        ),
        "intake": intake(curve),
        "category_separation": CATEGORIES,
        "additional_diagnostics": ADDITIONAL_DIAGNOSTICS,
        "internal_dependency": {
            "id": "IDEA-20260807-98a970",
            "path": "ledger/proposals/IDEA-20260807-98a970.yaml",
            "reuse": "named-curve embedding-degree, anomalous, and full-torsion audit lane",
            "nonduplication_rule": "Reuse and specialize this internal lane; do not mint a duplicate mechanism proposal.",
        },
        "source_requirements": {
            "intake_pointers_only": SOURCE_POINTERS,
            "rule": "Each future task must retrieve and read its own primary or authoritative sources and record citation provenance; these pointers and the table are not evidence.",
            "curve25519_internal_baseline": (
                "knowledge/literature/KN-LIT-093.md"
                if curve["name"] == "Curve25519"
                else None
            ),
        },
        "controls": {
            "positive": "Reproduce the described Anomalous additive-transfer behavior and BN(2,254) multiplicative-transfer/small-discriminant behavior only after source and parameter verification.",
            "negative": "Use a sourced, parameter-matched curve or model for which the tested criterion is expected not to trigger; state all matching assumptions.",
            "null": "Run the identical measurement on a same-shape synthetic, randomized, or shuffled object whose tested structure has been deliberately removed.",
        },
        "falsification_rule": "Every lane must specify a quantitative prediction, test boundary, and observation that would falsify its proposed interpretation before any expensive work.",
        "scope": {
            "curve": curve["name"],
            "equation": curve["equation"],
            "field": {
                "type": "prime",
                "bits": FIELD_BITS[curve["name"]],
                "modulus": curve["modulus"],
            },
            "methods": {
                "safecurves_criteria": list(CRITERIA),
                "criterion_categories": CATEGORIES,
                "additional_diagnostics": ADDITIONAL_DIAGNOSTICS,
            },
            "purpose": "lawfully authorized defensive cryptographic research",
            "live_keys": "prohibited",
            "targets": "public named-curve parameters, generated controls, and public certificates only",
            "conclusions": "No safety or vulnerability conclusion is authorized by this planning record.",
        },
        "claim_boundaries": CLAIM_BOUNDARIES,
        "first_batch": {"id": ids["batch"], "path": paths["batch"]},
    }


def build_curve_records(
    curve: dict[str, Any],
    ids: dict[str, str],
    paths: dict[str, str],
    base_commit: str,
) -> dict[str, Any]:
    idea_artifacts = [
        paths["parameter_capsule"],
        paths["audit_plan"],
        paths["idea_report"],
    ]
    archive_artifacts = [paths["batch_snapshot_receipt"]]
    idea_read_scope = [
        paths["goal"],
        paths["rq"],
        "ledger/proposals/IDEA-20260807-98a970.yaml",
    ]
    if curve["name"] == "Curve25519":
        idea_read_scope.append("knowledge/literature/KN-LIT-093.md")
    idea_write_scope = [paths["idea_dir"]]
    archive_read_scope = [paths["idea_dir"], *idea_artifacts]
    archive_write_scope = [paths["archive_dir"]]
    idea_objective = (
        f"Retrieve primary or authoritative sources for {curve['name']}, reconcile "
        "the exact parameter tuple, and produce a falsifiable prioritized plan for "
        "certificate-bearing reproduction of all eleven comparison cells plus the "
        "declared additional diagnostics."
    )
    idea_constraints = [
        *CLAIM_BOUNDARIES,
        "Retrieve and read sources during this task; record provenance for every citation and do not promote recalled references to support.",
        "Define positive, parameter-matched negative, and same-shape null controls before interpreting any signal.",
        "For every planned lane state mechanism, quantitative prediction, certificate or bound, budget, stopping rule, falsifier, and honest limitation.",
        "Reuse IDEA-20260807-98a970 for embedding-degree, anomalous, and full-torsion coverage rather than duplicating that proposal.",
        "Use only public parameters and generated controls; never test, request, store, or derive a live private key.",
        "Do not run a curve attack, create an experiment result, or state that the curve is safe, unsafe, vulnerable, or free of vulnerabilities.",
        "Never select a provider, backend, endpoint, or model identifier containing Bedrock, case-insensitively.",
    ]
    idea_inputs = [
        paths["goal"],
        paths["rq"],
        "ledger/proposals/IDEA-20260807-98a970.yaml",
        MANIFEST_REL.as_posix(),
        *SOURCE_POINTERS,
    ]
    if curve["name"] == "Curve25519":
        idea_inputs.append("knowledge/literature/KN-LIT-093.md")
    idea_gate = [
        "The parameter capsule distinguishes user intake from retrieved primary or authoritative sources and records provenance and unresolved conflicts.",
        "The audit plan covers every one of the eleven criteria in the declared category, with a certificate or explicit bound, controls, falsifier, budget, and stopping rule.",
        "The plan covers every declared additional diagnostic, or records a concrete reason and successor condition for a deferred diagnostic.",
        "Positive, parameter-matched negative, and same-shape null controls are explicit and run before belief in any later task.",
        "The report states that no curve attack ran and makes no safety or vulnerability conclusion.",
    ]
    idea_handoff = task_handoff(
        task_id=ids["idea_task"],
        to="idea-generator",
        objective=idea_objective,
        uncertainty_reduced=(
            f"Whether the user-supplied {curve['name']} tuple agrees with retrieved "
            "primary or authoritative sources and which bounded, falsifiable audits "
            "can reproduce or challenge each preregistered comparison target."
        ),
        inputs=idea_inputs,
        constraints=idea_constraints,
        deliverables=[
            "Primary-source parameter capsule",
            "Falsifiable prioritized audit plan",
            "Task report with limitations and proposed successor handoffs",
        ],
        artifact_paths=idea_artifacts,
        read_scope=idea_read_scope,
        write_scope=idea_write_scope,
        archived_by=ids["archive_task"],
        policy="research-deep",
        budget={
            "wall_clock_seconds": 1800,
            "memory_gb": 4,
            "maximum_runs": 1,
        },
        completion_gate=idea_gate,
    )

    archive_block = {
        "kind": "snapshot",
        "source_task_ids": [ids["idea_task"]],
        "commit_sha": None,
        "parent_sha": None,
        "path_sha256": {},
        "record_ids": [],
    }
    archive_handoff = task_handoff(
        task_id=ids["archive_task"],
        to="coordinator",
        objective=(
            f"Create and verify the durable snapshot commit for the exact outputs of "
            f"{ids['idea_task']} after that planning task completes."
        ),
        uncertainty_reduced=(
            f"Whether the exact planning outputs of {ids['idea_task']} are durably "
            "bound to a reachable snapshot commit with verified parent, path set, and hashes."
        ),
        inputs=[
            ids["idea_task"],
            paths["idea_handoff"],
            paths["idea_card"],
            *idea_artifacts,
        ],
        constraints=[
            "Run only after the producer has a completed valid receipt and all declared artifacts exist.",
            "Fetch and inspect origin/main immediately before archival; merge rather than rebase if branch synchronization is required.",
            "Stage only the producer's exact declared artifact paths and verify the commit parent, changed-path set, and SHA-256 bindings.",
            "Do not edit or normalize producer artifacts; a correction requires a new record.",
            "This planning snapshot changes no hypothesis, experiment, goal, safety, or vulnerability status.",
            "Never select a provider, backend, endpoint, or model identifier containing Bedrock, case-insensitively.",
        ],
        deliverables=["Post-commit snapshot receipt"],
        artifact_paths=archive_artifacts,
        read_scope=archive_read_scope,
        write_scope=archive_write_scope,
        archived_by=ids["archive_task"],
        policy="coordinator-orchestration-code",
        budget={
            "wall_clock_seconds": 900,
            "memory_gb": 2,
            "maximum_runs": 1,
        },
        completion_gate=[
            "The snapshot commit is reachable from HEAD and has the recorded parent.",
            "The commit changes exactly the producer artifacts and preserves their recorded SHA-256 hashes.",
            "The receipt records the checked base, commit, parent, exact paths, hashes, and producer task ID without placing the containing commit hash inside that same commit.",
        ],
        archive=archive_block,
    )

    idea_card = {
        "task": {
            "id": ids["idea_task"],
            "title": f"Prepare sourced parameter capsule and audit plan for {curve['name']}",
            "role": "idea-generator",
            "state": "queued",
            "review_required": False,
            "priority": 100,
            "depends_on": [],
            "handoff_path": paths["idea_handoff"],
            "read_scope": idea_read_scope,
            "write_scope": idea_write_scope,
            "artifact_paths": idea_artifacts,
            "archived_by": ids["archive_task"],
            "budget": idea_handoff["budget"],
            "completion_gate": idea_gate,
            "claim_changing": False,
        }
    }
    archive_card = {
        "task": {
            "id": ids["archive_task"],
            "title": f"Snapshot planning outputs for {curve['name']}",
            "role": "coordinator",
            "state": "queued",
            "review_required": False,
            "priority": 90,
            "depends_on": [ids["idea_task"]],
            "handoff_path": paths["archive_handoff"],
            "read_scope": archive_read_scope,
            "write_scope": archive_write_scope,
            "artifact_paths": archive_artifacts,
            "archived_by": ids["archive_task"],
            "budget": archive_handoff["budget"],
            "completion_gate": archive_handoff["completion_gate"],
            "archive": archive_block,
            "claim_changing": False,
        }
    }

    def queue_entry(
        handoff: dict[str, Any],
        title: str,
        depends_on: list[str],
        priority: int,
        read_scope: list[str],
        write_scope: list[str],
        archive: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entry = {
            "id": handoff["id"],
            "title": title,
            "role": handoff["to"],
            "state": "queued",
            "review_required": False,
            "priority": priority,
            "depends_on": depends_on,
            "read_scope": read_scope,
            "write_scope": write_scope,
            "artifact_paths": handoff["artifact_paths"],
            "archived_by": handoff["archived_by"],
            "handoff": handoff,
        }
        if archive is not None:
            entry["archive"] = archive
        return entry

    queue = {
        "schema": "crypto.autoresearch.dispatch_queue.v1",
        "objective": f"Produce and durably snapshot a source-reconciled planning dossier for {curve['name']} without running a curve attack or making a scientific claim.",
        "goal_id": ids["goal"],
        "batch_id": ids["batch"],
        "created_at": CREATED_AT,
        "max_concurrent": 1,
        "tasks": [
            queue_entry(
                idea_handoff,
                f"Prepare sourced parameter capsule and audit plan for {curve['name']}",
                [],
                100,
                idea_read_scope,
                idea_write_scope,
            ),
            queue_entry(
                archive_handoff,
                f"Snapshot planning outputs for {curve['name']}",
                [ids["idea_task"]],
                90,
                archive_read_scope,
                archive_write_scope,
                archive_block,
            ),
        ],
    }
    batch = {
        "id": ids["batch"],
        "goal_id": ids["goal"],
        "question_ids": [ids["rq"]],
        "status": "active",
        "created_at": CREATED_AT,
        "updated_at": CREATED_AT,
        "purpose": (
            f"Planning and source-intake only for {curve['name']}; no curve attack, "
            "experiment, claim, or status transition is authorized."
        ),
        "dispatch_queue_path": paths["queue"],
        "max_concurrent": 1,
        "task_ids": [ids["idea_task"], ids["archive_task"]],
        "ready_tasks": [ids["idea_task"]],
        "deferred_tasks": [ids["archive_task"]],
        "review_required": False,
        "claim_changing": False,
        "archive_assignments": {
            ids["idea_task"]: ids["archive_task"],
        },
    }
    return {
        "goal": {"research_goal": goal_record(curve, ids, paths, base_commit)},
        "rq": {"research_question": rq_record(curve, ids, paths)},
        "batch": batch,
        "queue": queue,
        "idea_card": idea_card,
        "archive_card": archive_card,
        "idea_handoff": {"handoff": idea_handoff},
        "archive_handoff": {"handoff": archive_handoff},
        "idea_handoff_inner": idea_handoff,
        "archive_handoff_inner": archive_handoff,
    }


def relpaths(ids: dict[str, str]) -> dict[str, str]:
    ledger_goal_dir = Path("ledger/goals") / ids["goal"]
    coordination_goal_dir = Path("coordination/goals") / ids["goal"]
    batch_dir = coordination_goal_dir / "batches" / ids["batch"]
    idea_dir = batch_dir / "tasks" / ids["idea_task"]
    archive_dir = batch_dir / "tasks" / ids["archive_task"]
    return {
        "goal": (ledger_goal_dir / "goal.yaml").as_posix(),
        "rq": (
            Path("ledger/questions") / f"{ids['rq']}.yaml"
        ).as_posix(),
        "batch": (batch_dir / "batch.yaml").as_posix(),
        "queue": (batch_dir / "dispatch_queue.json").as_posix(),
        "idea_dir": idea_dir.as_posix(),
        "archive_dir": archive_dir.as_posix(),
        "idea_card": (idea_dir / "task.yaml").as_posix(),
        "archive_card": (archive_dir / "task.yaml").as_posix(),
        "idea_handoff": (
            Path("ledger/handoffs") / f"{ids['idea_task']}.yaml"
        ).as_posix(),
        "archive_handoff": (
            Path("ledger/handoffs") / f"{ids['archive_task']}.yaml"
        ).as_posix(),
        "parameter_capsule": (idea_dir / "parameter-capsule.yaml").as_posix(),
        "audit_plan": (idea_dir / "audit-plan.yaml").as_posix(),
        "idea_report": (idea_dir / "task-report.yaml").as_posix(),
        "batch_snapshot_receipt": (
            archive_dir / "snapshot-receipt.json"
        ).as_posix(),
    }


def allocate_all(root: Path) -> list[dict[str, Any]]:
    allocated = {BOOTSTRAP_TASK_ID}
    mappings = []
    for curve in CURVES:
        ids = {
            "goal": allocate_id(
                root,
                "goal",
                re.compile(r"GOAL-SCURVE-[0-9a-f]{6}"),
                allocated,
                area="SCURVE",
            ),
            "rq": allocate_id(
                root,
                "research_question",
                re.compile(r"RQ-SCURVE-[0-9a-f]{6}"),
                allocated,
                area="SCURVE",
            ),
            "batch": allocate_id(
                root,
                "batch",
                re.compile(r"BATCH-[0-9a-f]{6}"),
                allocated,
            ),
            "idea_task": allocate_id(
                root,
                "handoff",
                re.compile(r"TASK-20260824-[0-9a-f]{6}"),
                allocated,
                date="20260824",
            ),
            "archive_task": allocate_id(
                root,
                "handoff",
                re.compile(r"TASK-20260824-[0-9a-f]{6}"),
                allocated,
                date="20260824",
            ),
        }
        mappings.append({"curve": curve, "ids": ids, "paths": relpaths(ids)})
    if len(allocated) != 101:
        raise BootstrapError(
            f"expected fixed task plus 100 unique allocated ids, got {len(allocated)}"
        )
    return mappings


def bootstrap_handoff(artifact_paths: list[str]) -> dict[str, Any]:
    return {
        "handoff": {
            "id": BOOTSTRAP_TASK_ID,
            "from": "coordinator",
            "to": "coordinator",
            "objective": "Bootstrap one durable, bounded, non-duplicative planning goal for each of the twenty user-supplied SafeCurves rows.",
            "uncertainty_reduced": "Whether all twenty intake rows can be represented as schema-valid, independently auditable, bounded planning campaigns without duplicating an existing audit lane or treating the table as evidence.",
            "inputs": [
                "User-supplied twenty-row SafeCurves table and exact parameter tuples",
                "AGENTS.md",
                "CLAUDE.md",
                "agents/coordinator.md",
                "docs/task-lifecycle.md",
                "docs/dynamic-subagent-dispatch.md",
                "templates/research-records.md",
                ".claude/skills/coordinate-research-goal/SKILL.md",
                ".claude/skills/launch-research-harness/SKILL.md",
                "ledger/proposals/IDEA-20260807-98a970.yaml",
                "knowledge/literature/KN-LIT-093.md",
                *SOURCE_POINTERS,
            ],
            "constraints": [
                "Create exactly twenty goals and twenty bound research questions, one per intake row.",
                "The intake tuple and expected matrix are user-supplied and unverified until primary-source reconciliation.",
                "The first batch is planning and intake only and must not execute an attack or create evidence or conclusions.",
                "Do not execute any generated task as part of this bootstrap.",
                "Do not create hypotheses, experiments, findings, decisions, or safety or vulnerability conclusions.",
                "Do not push or create a pull request from this task.",
                "Never select a provider, backend, endpoint, or model identifier containing Bedrock, case-insensitively.",
                *CLAIM_BOUNDARIES,
            ],
            "deliverables": [
                "Twenty persistent goal records",
                "Twenty research-question records",
                "Twenty planning-only first batches and bounded dispatch queues",
                "Forty task cards and matching persisted handoffs",
                "Machine-readable bootstrap manifest",
                "Post-commit bootstrap snapshot receipt written by the control plane",
            ],
            "artifact_paths": artifact_paths,
            "write_scope": artifact_paths,
            "archived_by": BOOTSTRAP_TASK_ID,
            "inference": {
                "policy": "coordinator-orchestration-code",
                "reasoning_effort": "high",
                "fallback_allowed": False,
                "degraded_allowed": False,
                "independent_session_required": False,
                "resolved_model_id": None,
                "model_verified": False,
                "provenance_note": "The generator cannot observe the serving model; the control plane must bind actual runtime provenance without fabrication.",
            },
            "budget": {
                "wall_clock_seconds": 3600,
                "memory_gb": 4,
                "maximum_runs": 1,
            },
            "completion_gate": [
                "Exactly twenty names map bijectively to twenty goal IDs and twenty question IDs.",
                "All one hundred generated IDs were allocated with --next, immediately checked with --check, and are unique in memory.",
                "The repository ledger validator reports no new violation.",
                "Every dispatch queue renders with exactly its planning task ready and its snapshot task dependency-deferred.",
                "Merge hygiene against execution-time origin/main passes.",
                "The bootstrap snapshot and post-commit receipt bind only these exact paths and hashes.",
            ],
            "review_plan": None,
        }
    }


def manifest_record(
    mappings: list[dict[str, Any]],
    artifact_paths: list[str],
    head: str,
    origin_main: str,
) -> dict[str, Any]:
    rows = []
    for item in mappings:
        curve = item["curve"]
        ids = item["ids"]
        paths = item["paths"]
        rows.append(
            {
                "curve": curve["name"],
                "goal_id": ids["goal"],
                "research_question_id": ids["rq"],
                "batch_id": ids["batch"],
                "idea_generator_task_id": ids["idea_task"],
                "snapshot_archive_task_id": ids["archive_task"],
                "expected_safecurves": intake(curve),
                "paths": paths,
            }
        )
    return {
        "schema_version": "1.0",
        "bootstrap_task_id": BOOTSTRAP_TASK_ID,
        "created_at": CREATED_AT,
        "purpose": "Planning-only bootstrap for independent certificate-bearing SafeCurves parameter audits.",
        "claim_status": "No scientific, safety, or vulnerability claim is made by this manifest.",
        "control_plane": {
            "expected_base_ref_at_execution": "origin/main",
            "observed_head_at_generation": head,
            "observed_origin_main_at_generation": origin_main,
            "head_matched_origin_main": head == origin_main,
            "intended_branch": EXPECTED_BRANCH,
            "scientific_result": False,
        },
        "generator": GENERATOR_REL.as_posix(),
        "future_bootstrap_snapshot_receipt": BOOTSTRAP_RECEIPT_REL.as_posix(),
        "record_count": {
            "curves": 20,
            "goals": 20,
            "research_questions": 20,
            "batches": 20,
            "task_cards": 40,
            "task_handoffs": 40,
            "allocated_ids": 100,
        },
        "criterion_order": list(CRITERIA),
        "criterion_categories": CATEGORIES,
        "rows": rows,
        "bootstrap_artifact_paths": artifact_paths,
    }


def yaml_text(value: Any) -> str:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True)


def json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def validate_in_memory(
    mappings: list[dict[str, Any]],
    records: list[dict[str, Any]],
    artifact_paths: list[str],
    payloads: dict[str, str],
) -> None:
    names = [item["curve"]["name"] for item in mappings]
    if len(names) != 20 or len(set(names)) != 20:
        raise BootstrapError("curve names are not a twenty-row bijection")
    if tuple(names) != tuple(curve["name"] for curve in CURVES):
        raise BootstrapError("curve order changed")
    if set(FIELD_BITS) != set(names):
        raise BootstrapError("field-bit mapping is not a twenty-row bijection")
    for curve in CURVES:
        if len(curve["cells"]) != 11 or set(matrix_row(curve)) != set(CRITERIA):
            raise BootstrapError(f"malformed eleven-cell row for {curve['name']}")

    all_ids = [record_id for item in mappings for record_id in item["ids"].values()]
    if len(all_ids) != 100 or len(set(all_ids)) != 100:
        raise BootstrapError("allocated IDs are not a one-hundred-item bijection")

    if len(artifact_paths) != len(set(artifact_paths)):
        raise BootstrapError("bootstrap artifact path list contains duplicates")
    if any(any(char in path for char in "*?[") for path in artifact_paths):
        raise BootstrapError("wildcard found in frozen artifact path list")
    expected_fixed = {
        GENERATOR_REL.as_posix(),
        TOP_HANDOFF_REL.as_posix(),
        MANIFEST_REL.as_posix(),
        BOOTSTRAP_RECEIPT_REL.as_posix(),
    }
    if not expected_fixed.issubset(artifact_paths):
        raise BootstrapError("frozen artifact list lacks a required control path")

    nonarchive_scopes: set[str] = set()
    archive_ids = set()
    for record in records:
        if set(record["goal"]) != {"research_goal"}:
            raise BootstrapError("goal payload lacks the canonical research_goal wrapper")
        if set(record["rq"]) != {"research_question"}:
            raise BootstrapError("question payload lacks the canonical research_question wrapper")
        goal = record["goal"]["research_goal"]
        question = record["rq"]["research_question"]
        if goal["campaign_budget"]["maximum_batches"] > 5:
            raise BootstrapError("goal batch budget exceeds five")
        if goal["campaign_budget"]["total_wall_clock_seconds"] > 18000:
            raise BootstrapError("goal wall-clock budget exceeds eighteen thousand seconds")
        if goal["campaign_budget"]["max_concurrent"] > 2:
            raise BootstrapError("goal concurrency exceeds two")
        if not isinstance(goal["next_action"], str) or not goal["next_action"].strip():
            raise BootstrapError("goal must have exactly one concrete next_action string")
        if (
            goal["runtime"]["provider"] != "none"
            or not goal["latest_verified_commit"]
            or not goal["latest_verified_commit_note"]
            or len(goal["question_ids"]) != 1
            or not goal["current_batch_id"]
            or not goal["dispatch_queue_path"]
            or "research_question_ids" in goal
            or "current_batch" in goal
        ):
            raise BootstrapError("goal lacks canonical runtime, question, batch, queue, or commit fields")
        if (
            question["status"] != "active"
            or not question["title"]
            or question["scope"]["curve"] != question["intake"]["curve"]
            or question["scope"]["field"]["type"] != "prime"
            or question["scope"]["field"]["bits"] <= 0
            or not question["scope"]["field"]["modulus"]
            or not question["scope"]["methods"]
        ):
            raise BootstrapError("research question lacks canonical active title or exact scope")

        queue = record["queue"]
        if (
            queue.get("schema") != "crypto.autoresearch.dispatch_queue.v1"
            or not queue.get("objective")
            or not queue.get("goal_id")
        ):
            raise BootstrapError("queue lacks the canonical v1 schema, objective, or goal")
        tasks = queue["tasks"]
        ready = [task for task in tasks if task["state"] == "queued" and not task["depends_on"]]
        deferred = [task for task in tasks if task["state"] == "queued" and task["depends_on"]]
        if (
            queue["max_concurrent"] != 1
            or len(tasks) != 2
            or len(ready) != 1
            or ready[0]["role"] != "idea-generator"
            or len(deferred) != 1
            or deferred[0]["role"] != "coordinator"
            or deferred[0]["depends_on"] != [ready[0]["id"]]
        ):
            raise BootstrapError("queue does not expose one planning task and one deferred archive")
        required_task_fields = {
            "id",
            "title",
            "role",
            "state",
            "review_required",
            "priority",
            "depends_on",
            "read_scope",
            "write_scope",
            "artifact_paths",
            "handoff",
        }
        for task in tasks:
            if not required_task_fields.issubset(task):
                raise BootstrapError("queue task lacks a canonical dispatcher field")
            if (
                not task["title"]
                or task["state"] != "queued"
                or not isinstance(task["review_required"], bool)
                or not isinstance(task["priority"], int)
                or not 0 <= task["priority"] <= 100
                or not task["read_scope"]
                or len(task["write_scope"]) != 1
                or not task["artifact_paths"]
            ):
                raise BootstrapError("queue task violates a canonical dispatcher value constraint")
            handoff = task["handoff"]
            if (
                not handoff.get("objective")
                or not handoff.get("uncertainty_reduced")
                or not handoff.get("inputs")
                or not handoff.get("constraints")
                or not handoff.get("deliverables")
                or not handoff.get("completion_gate")
                or any(handoff["budget"].get(key, 0) <= 0 for key in ("wall_clock_seconds", "memory_gb", "maximum_runs"))
            ):
                raise BootstrapError("inline handoff is not schema-complete or positively budgeted")
            if (
                task["read_scope"] != handoff.get("read_scope")
                or task["write_scope"] != handoff.get("write_scope")
                or task["artifact_paths"] != handoff.get("artifact_paths")
            ):
                raise BootstrapError("queue task and inline handoff scopes or artifacts diverge")
            write_dir = Path(task["write_scope"][0])
            if any(write_dir not in Path(path).parents for path in task["artifact_paths"]):
                raise BootstrapError("task artifact escapes its exact task-directory write scope")
        if ready[0]["priority"] != 100 or deferred[0]["priority"] != 90:
            raise BootstrapError("queue priorities differ from the frozen planning order")
        if len(ready[0]["artifact_paths"]) != 3 or len(deferred[0]["artifact_paths"]) != 1:
            raise BootstrapError("queue artifact cardinality is malformed")
        expected_idea_read_scope = [
            f"ledger/goals/{goal['id']}/goal.yaml",
            f"ledger/questions/{question['id']}.yaml",
            "ledger/proposals/IDEA-20260807-98a970.yaml",
        ]
        if question["scope"]["curve"] == "Curve25519":
            expected_idea_read_scope.append("knowledge/literature/KN-LIT-093.md")
        expected_idea_dir = Path(ready[0]["artifact_paths"][0]).parent.as_posix()
        expected_archive_dir = Path(deferred[0]["artifact_paths"][0]).parent.as_posix()
        if (
            ready[0]["read_scope"] != expected_idea_read_scope
            or ready[0]["write_scope"] != [expected_idea_dir]
            or deferred[0]["read_scope"]
            != [expected_idea_dir, *ready[0]["artifact_paths"]]
            or deferred[0]["write_scope"] != [expected_archive_dir]
        ):
            raise BootstrapError("queue task read or write scopes differ from the canonical exact paths")
        for card_key, task in (("idea_card", ready[0]), ("archive_card", deferred[0])):
            card = record[card_key]["task"]
            for key in (
                "id",
                "title",
                "role",
                "state",
                "review_required",
                "priority",
                "depends_on",
                "read_scope",
                "write_scope",
                "artifact_paths",
            ):
                if card.get(key) != task.get(key):
                    raise BootstrapError(f"{card_key} canonical field {key} diverges from queue")
        archive_id = deferred[0]["id"]
        archive_ids.add(archive_id)
        if ready[0]["archived_by"] != archive_id:
            raise BootstrapError("nonarchive task lacks exactly one snapshot assignment")
        for path in ready[0]["write_scope"]:
            if path in nonarchive_scopes:
                raise BootstrapError(f"overlapping nonarchive write scope: {path}")
            nonarchive_scopes.add(path)
        if ready[0]["review_required"] is not False:
            raise BootstrapError("planning task must set review_required false")
        if ready[0]["handoff"]["inference"]["policy"] != "research-deep":
            raise BootstrapError("planning task must request research-deep")
        archive = deferred[0].get("archive", {})
        if archive != {
            "kind": "snapshot",
            "source_task_ids": [ready[0]["id"]],
            "commit_sha": None,
            "parent_sha": None,
            "path_sha256": {},
            "record_ids": [],
        }:
            raise BootstrapError("snapshot archive starts with a nonempty or malformed binding")
        if (
            record["archive_card"]["task"].get("archive") != archive
            or record["archive_handoff_inner"].get("archive") != archive
        ):
            raise BootstrapError("archive binding diverges across queue, card, and handoff")
    if len(archive_ids) != 20:
        raise BootstrapError("snapshot archive task IDs are not unique")

    expected_payload_count = 2 + 20 * 8
    if len(payloads) != expected_payload_count:
        raise BootstrapError(
            f"expected {expected_payload_count} generated payloads, got {len(payloads)}"
        )
    # Serialization round trips are part of the in-memory gate, not repository validation.
    for path, text in payloads.items():
        if path.endswith(".json"):
            json.loads(text)
        else:
            yaml.safe_load(text)


def ensure_no_targets(root: Path, payload_paths: Iterable[str], reserved: Iterable[str]) -> None:
    for relative in sorted(set(payload_paths) | set(reserved)):
        path = root / relative
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise BootstrapError(f"target escapes repository root: {relative}") from exc
        if path.exists() or path.is_symlink():
            raise BootstrapError(f"refusing existing target path {relative}")


def make_parent(path: Path, root: Path, created_dirs: list[Path]) -> None:
    missing = []
    parent = path.parent
    while parent != root and not parent.exists():
        missing.append(parent)
        parent = parent.parent
    if parent != root and not parent.exists():
        raise BootstrapError(f"cannot anchor parent directory for {path}")
    for directory in reversed(missing):
        directory.mkdir()
        created_dirs.append(directory)


def install_payloads(root: Path, ordered_paths: list[str], payloads: dict[str, str]) -> None:
    created_dirs: list[Path] = []
    temps: dict[str, Path] = {}
    installed: list[Path] = []
    try:
        for relative in ordered_paths:
            target = root / relative
            make_parent(target, root, created_dirs)
            fd, temp_name = tempfile.mkstemp(
                prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
            )
            temp_path = Path(temp_name)
            temps[relative] = temp_path
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payloads[relative])
                handle.flush()
                os.fsync(handle.fileno())
        # The frozen bootstrap handoff is deliberately installed first.
        if ordered_paths[0] != TOP_HANDOFF_REL.as_posix():
            raise BootstrapError("bootstrap handoff is not first in install order")
        for relative in ordered_paths:
            target = root / relative
            os.replace(temps[relative], target)
            installed.append(target)
            del temps[relative]
        for directory in sorted({path.parent for path in installed}):
            fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    except Exception:
        for temp_path in temps.values():
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass
        # No pre-existing target is ever overwritten, so rollback is safe.
        for target in reversed(installed):
            try:
                target.unlink()
            except FileNotFoundError:
                pass
        for directory in reversed(created_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass
        raise


def main() -> int:
    root, head, origin_main = resolve_and_check_root()
    mappings = allocate_all(root)

    generated_paths: list[str] = []
    for item in mappings:
        paths = item["paths"]
        generated_paths.extend(
            [
                paths["goal"],
                paths["rq"],
                paths["batch"],
                paths["queue"],
                paths["idea_card"],
                paths["archive_card"],
                paths["idea_handoff"],
                paths["archive_handoff"],
            ]
        )
    artifact_paths = [
        TOP_HANDOFF_REL.as_posix(),
        GENERATOR_REL.as_posix(),
        MANIFEST_REL.as_posix(),
        BOOTSTRAP_RECEIPT_REL.as_posix(),
        *generated_paths,
    ]

    payload_objects: dict[str, Any] = {}
    records = []
    for item in mappings:
        ids = item["ids"]
        paths = item["paths"]
        record = build_curve_records(item["curve"], ids, paths, head)
        records.append(record)
        payload_objects.update(
            {
                paths["goal"]: record["goal"],
                paths["rq"]: record["rq"],
                paths["batch"]: record["batch"],
                paths["queue"]: record["queue"],
                paths["idea_card"]: record["idea_card"],
                paths["archive_card"]: record["archive_card"],
                paths["idea_handoff"]: record["idea_handoff"],
                paths["archive_handoff"]: record["archive_handoff"],
            }
        )
    payload_objects[TOP_HANDOFF_REL.as_posix()] = bootstrap_handoff(artifact_paths)
    payload_objects[MANIFEST_REL.as_posix()] = manifest_record(
        mappings, artifact_paths, head, origin_main
    )
    payloads = {
        path: (json_text(value) if path.endswith(".json") else yaml_text(value))
        for path, value in payload_objects.items()
    }

    reserved_future = [BOOTSTRAP_RECEIPT_REL.as_posix()]
    for item in mappings:
        paths = item["paths"]
        reserved_future.extend(
            [
                paths["parameter_capsule"],
                paths["audit_plan"],
                paths["idea_report"],
                paths["batch_snapshot_receipt"],
            ]
        )
    ensure_no_targets(root, payloads, reserved_future)
    validate_in_memory(mappings, records, artifact_paths, payloads)

    remaining_paths = sorted(
        path for path in payloads if path != TOP_HANDOFF_REL.as_posix()
    )
    install_payloads(
        root,
        [TOP_HANDOFF_REL.as_posix(), *remaining_paths],
        payloads,
    )

    summary = {
        "bootstrap_task_id": BOOTSTRAP_TASK_ID,
        "claim_status": "planning records only; no task dispatched and no safety or vulnerability conclusion",
        "created_paths": [TOP_HANDOFF_REL.as_posix(), *remaining_paths],
        "future_snapshot_receipt": BOOTSTRAP_RECEIPT_REL.as_posix(),
        "mappings": [
            {
                "curve": item["curve"]["name"],
                **item["ids"],
            }
            for item in mappings
        ],
        "sha256": {
            path: hashlib.sha256(payloads[path].encode("utf-8")).hexdigest()
            for path in [TOP_HANDOFF_REL.as_posix(), *remaining_paths]
        },
    }
    print(json.dumps(summary, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BootstrapError as exc:
        print(f"SafeCurves bootstrap refused: {exc}", file=sys.stderr)
        raise SystemExit(2)
