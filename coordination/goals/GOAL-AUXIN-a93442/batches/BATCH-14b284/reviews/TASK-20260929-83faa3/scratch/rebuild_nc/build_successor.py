#!/usr/bin/env python3
"""Build EXP-AUXIN-55c6c0 draft-contract.yaml: fresh meta + protocol_normative, zero transclusion.

Closes by construction the remaining EJ3/EJ6/EJ8 breaks named in
DEC-20260929-cfb294 (EJ3-CLOSURE, EJ6-B1 surfaces, EJ8-T0124,
EJ8-INCORP-HASH-VS-FPREC). Design-time only; zero runs.
"""

from __future__ import annotations

import copy
import hashlib
import re
from pathlib import Path

import yaml

ROOT = Path('/workspace')
DESIGN = Path(__file__).resolve().parent
TYPED = ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml"
NARROW = ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml"
GATED = ROOT / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml"
FRESH = Path('/workspace/coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-14b284/reviews/TASK-20260929-83faa3/scratch/rebuild_nc/fresh-text.yaml')
OUT = Path('/workspace/coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-14b284/reviews/TASK-20260929-83faa3/scratch/rebuild_nc/draft-contract.yaml')

EXP_ID = "EXP-AUXIN-55c6c0"
EXP_PATH = f"experiments/{EXP_ID}/"

DEPLOYED_ROSTER = [
    {"id": "NIST-P-224", "role": "deployed"},
    {"id": "NIST-P-256", "role": "deployed"},
    {"id": "NIST-P-384", "role": "deployed"},
    {"id": "NIST-P-521", "role": "deployed"},
    {"id": "secp256k1", "role": "deployed"},
    {"id": "brainpoolP256r1", "role": "deployed"},
    {"id": "brainpoolP384r1", "role": "deployed"},
    {"id": "Ed25519-L", "role": "deployed"},
    {"id": "BN254-r", "role": "deployed_pairing"},
    {"id": "BLS12-381-r", "role": "deployed_pairing"},
]


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def deep_merge(base: dict, overlay: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in overlay.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def walk_strings(obj, fn):
    if isinstance(obj, dict):
        return {k: walk_strings(v, fn) for k, v in obj.items()}
    if isinstance(obj, list):
        return [walk_strings(x, fn) for x in obj]
    if isinstance(obj, str):
        return fn(obj)
    return obj


def rewrite_protocol_text(s: str) -> str:
    s = s.replace(
        "experiments/EXP-AUXIN-7e2e3d/implementation/",
        f"{EXP_PATH}implementation/",
    )
    s = s.replace("experiments/EXP-AUXIN-92dccc/", EXP_PATH)
    s = re.sub(
        r"(?<![\w/])implementation/typed/",
        f"{EXP_PATH}implementation/typed/",
        s,
    )
    s = re.sub(rf"({re.escape(EXP_PATH)})+", EXP_PATH, s)
    s = re.sub(
        r"Launch with a dirty implementation/typed/ or dirty amendment path, or on implementation bytes",
        f"Launch with a dirty implementation tree under {EXP_PATH}implementation/typed/, or on implementation bytes that differ from the implementation snapshot",
        s,
    )
    s = re.sub(
        rf"Launch with a dirty {re.escape(EXP_PATH)}implementation/typed/ or dirty amendment path, or on implementation bytes",
        f"Launch with a dirty implementation tree under {EXP_PATH}implementation/typed/, or on implementation bytes that differ from the implementation snapshot",
        s,
    )
    s = re.sub(
        r"Any edit of this file, of specification\.yaml, of AMD-20260916-bands\.yaml or of AMD-20260923-d1d10\.yaml after approval",
        "Any edit of this contract file after approval",
        s,
    )
    s = re.sub(r"[Gg]overning-text hash(?:es)? mismatch", "successor_contract_sha256 mismatch", s)
    s = re.sub(r"successor_contract_sha256(?:es)?", "successor_contract_sha256", s)
    s = re.sub(r"governing_text_table", "protocol_normative section index", s)
    s = re.sub(r"four governing layers?", "this contract file alone", s)
    s = re.sub(r"four-layer stack", "single-contract custody model", s)
    s = re.sub(r"all four governing layers?", "this contract file", s)
    s = re.sub(
        r"Pre-registration of every cut-off rests on the sha256 binding of all four governing layers before any value is seen \(change\.D8_custody and custody_additions below\), not on the index\.",
        "Pre-registration of every cut-off rests on successor_contract_sha256 binding at launch, not on the index.",
        s,
    )
    s = re.sub(r"the held text", "this contract's stated rule", s)
    s = re.sub(r"\bheld text\b", "prior-record wording", s, flags=re.I)
    s = re.sub(r"amendment\.<path>", "successor contract path (provenance only)", s)
    s = re.sub(
        r"licenses a later amendment revision route",
        "does not apply; F-REV is the only revision route",
        s,
    )
    # EJ8-T0124: remove later-amendment licensing sentence patterns
    s = re.sub(
        r"A later amendment may pre-register a rule on the basis of this arm; this run's deployed rows are never re-scored by such a rule\.",
        "No later amendment and no successor layer may pre-register a rule on the basis of this arm for this contract; F-REV is the only revision route. This run's deployed rows are never re-scored by any rule derived from the null arm.",
        s,
    )
    s = re.sub(
        r"Revisit when any later amendment edits C-PLANT-PL for another reason\.",
        "Revisit only under F-REV in a new successor contract if C-PLANT-PL is redesigned.",
        s,
    )
    s = re.sub(
        r"the amendment returns to review",
        "this contract returns to review under F-REV",
        s,
    )
    # EJ6/EJ8 incorporated-by-hash surfaces
    s = re.sub(
        r"rows 1 to 5 \(FC1 to FC5\) of AMD-20260927-narrow\.yaml stay incorporated by hash",
        "rows 1 to 5 (FC1 to FC5) are restated as fresh text in protocol_normative.falsification_condition_mapping of this contract; no held record is bound by content-digest",
        s,
    )
    s = re.sub(r"\bstay incorporated by hash\b", "are restated as fresh text in this contract", s)
    s = re.sub(r"\bincorporated by hash\b", "restated as fresh text in this contract (no content-digest binding)", s)
    # EJ6-READ / INV-SPEC stand language on specification.yaml as governing
    s = re.sub(
        r"All experiment\.invalidation_rules of specification\.yaml stand\.",
        "The invalidation rules of this contract are exactly the list in protocol_normative.invalidation_rules; no held specification.yaml rule stands by reference.",
        s,
    )
    s = re.sub(
        r"Nothing here concerns any claim outside experiment\.claim_ceiling of specification\.yaml, which stands unchanged, and the DEC-20260802-204 acquisition gate stands\.",
        "Nothing here concerns any claim outside the claim ceiling restated in protocol_normative.claim_ceiling_restated of this contract. The DEC-20260802-204 acquisition gate is cited for provenance only and is not opened at run time.",
        s,
    )
    # FC6 / missing-branch: restate without specification.yaml governing
    s = re.sub(
        r'specification\.yaml tail_checks item 1 governs \(layer v1\), quoted verbatim: "Report r-1 and r\+1 separately; a missing branch voids the row\." \(sha256 of its UTF-8 bytes 26b53f8995afb04335a24612dcf48e736a2dd0e3d72d5f9b6b440b1a13cc5e52\)\.',
        'This contract restates the missing-branch rule as fresh text: "Report r-1 and r+1 separately; a missing branch voids the row." No held specification.yaml clause governs.',
        s,
    )
    s = re.sub(
        r'specification\.yaml tail_checks item 1 \(v1, "a missing branch voids the row"\) makes each omitted branch VOID',
        'this contract\'s missing-branch rule ("Report r-1 and r+1 separately; a missing branch voids the row.") makes each omitted branch VOID',
        s,
    )
    # Neutralize internal_consistency run-time reads of held specification.yaml
    s = re.sub(
        r"specification\.yaml frozen_curve_list\[NIST-P-256\]\.r_hex_pinned_internal is compared and the result recorded; it cannot pin",
        "No held specification.yaml field is compared at run time. The primary-source pin alone governs; any design-time internal hex note is provenance only and cannot pin",
        s,
    )
    s = re.sub(
        r"specification\.yaml frozen_curve_list\[secp256k1\]\.r_hex_pinned_internal is compared and the result recorded; it cannot pin",
        "No held specification.yaml field is compared at run time. The primary-source pin alone governs; any design-time internal hex note is provenance only and cannot pin",
        s,
    )
    # amendment.X → this contract wording where it implies held governing text
    s = re.sub(r"\bamendment\.controls\b", "protocol_normative.controls", s)
    s = re.sub(r"\bamendment\.null_arm\b", "protocol_normative.null_arm", s)
    s = re.sub(r"\bamendment\.what_the_controls_exercise\b", "protocol_normative.what_the_controls_exercise", s)
    return s


def extract_protocol(amendment: dict) -> dict:
    a = amendment.get("amendment", amendment)
    keys = [
        "definitions",
        "change",
        "conventions",
        "tools_and_admission",
        "stages",
        "controls",
        "controls_distinctness",
        "what_the_controls_exercise",
        "null_arm",
        "preregistered_prediction",
        "metrics",
        "budget",
        "stopping_rules",
        "invalidation_rules",
        "required_artifacts",
        "success_criterion",
        "falsification_criterion",
        "interpretation_limits",
        "proof_search_map",
    ]
    return {k: a[k] for k in keys if k in a}


def patch_deployed_roster(protocol: dict) -> None:
    """EJ6-READ: roles/order live only in this contract; no READ FROM held paths."""
    defs = protocol.setdefault("definitions", {})
    defs["deployed_row"] = (
        "A row whose role in change.D1_pins.deployed_row_roster of THIS contract "
        "is deployed or deployed_pairing. The label is that roster's role name only. "
        "No held specification.yaml list is read at run time."
    )
    defs["deployed_row_roster_note"] = (
        "Ids, roles and order of deployed rows are exactly change.D1_pins.deployed_row_roster "
        "in this contract file. That roster is the sole authority."
    )
    d1 = (protocol.get("change") or {}).setdefault("D1_pins", {})
    d1["deployed_row_roster"] = copy.deepcopy(DEPLOYED_ROSTER)
    rows = d1.get("rows")
    if isinstance(rows, list):
        role_by_id = {r["id"]: r["role"] for r in DEPLOYED_ROSTER}
        for row in rows:
            if isinstance(row, dict) and row.get("id") in role_by_id:
                row["role"] = role_by_id[row["id"]]


def patch_corrective_overlays(protocol: dict) -> None:
    """Rewrite EJ6-READ surface in corrective overlays; drop hash-incorporation."""
    for overlay in protocol.get("corrective_overlays") or []:
        if not isinstance(overlay, dict):
            continue
        pins = overlay.get("pins") or {}
        dro = pins.get("deployed_rows_roles_and_order")
        if isinstance(dro, dict):
            dro["rule"] = (
                "Deployed-row ids, roles and order are exactly "
                "change.D1_pins.deployed_row_roster of THIS contract, in that order. "
                "change.D1_pins.rows lists the same ten ids in the same order and "
                "carries each row's source, parse rule and cross-checks. No held "
                "specification.yaml frozen_curve_list is opened, hashed or compared "
                "at run time. A run that finds D1_pins.rows ids/order disagreeing "
                "with deployed_row_roster stops in Stage P with outcome I_TEXT."
            )
            dro["item"] = "RI-5"
            dro["adds_to"] = "definitions.deployed_row"
        # threshold / FC surfaces already rewritten via walk_strings
        fcm = overlay.get("falsification_condition_mapping_fc6")
        if isinstance(fcm, dict) and "unchanged_rows" in fcm:
            fcm["unchanged_rows"] = (
                "rows 1 to 5 (FC1 to FC5) are restated as fresh text in "
                "protocol_normative.falsification_condition_mapping of this contract; "
                "no held record is bound by content-digest"
            )


def patch_d4_and_invalidation(protocol: dict) -> None:
    """EJ8-T0124 and EJ6-INV-SPEC-STANDS."""
    d4 = (protocol.get("change") or {}).get("D4_calibration")
    if isinstance(d4, dict):
        d4["what_the_null_arm_is_for"] = (
            "Context only. It shows how often random primes of the same bit length "
            "receive each status and bin under the identical pipeline and budget. "
            "It licenses no curve-specific reading of any deployed row. No later "
            "amendment and no successor layer may pre-register a rule on the basis "
            "of this arm for this contract; F-REV is the only revision route. This "
            "run's deployed rows are never re-scored by any rule derived from the "
            "null arm."
        )
    inv = protocol.get("invalidation_rules")
    if isinstance(inv, list) and inv:
        # Replace any residual "stand" pointer as first item
        if isinstance(inv[0], str) and (
            "specification.yaml" in inv[0] or "stand" in inv[0].lower()
        ):
            inv[0] = (
                "The invalidation rules of this contract are exactly this list; "
                "no held specification.yaml rule stands by reference."
            )
        # Ensure held-path independence sentence present
        independence = (
            "Any rule that would open, hash, compare or stand on a path under "
            f"experiments/EXP-AUXIN-7e2e3d/ is void; F-CUSTODY.independence governs."
        )
        if not any(isinstance(x, str) and "F-CUSTODY.independence" in x for x in inv):
            inv.append(independence)


def patch_protocol(protocol: dict) -> None:
    """Surgical fixes for EJ3/EJ6/EJ8 surfaces after bulk rewrite."""
    d8 = (protocol.get("change") or {}).get("D8_custody")
    if isinstance(d8, dict):
        d8["trial_plan"] = (
            f"trial-plan.json under {EXP_PATH}implementation/typed/ "
            "records successor_contract_sha256 only. The run recomputes it at launch "
            "and at every stage boundary; mismatch is evidence-integrity failure."
        )
        d8["manifest"] = (
            "manifest.yaml records dirty_summary, launch commit, implementation snapshot "
            "task and commit, successor_contract_sha256, tool versions, third-party "
            "distributions and the inference block. Launch is refused if dirty_summary "
            f"lists this contract file or any path under {EXP_PATH}implementation/typed/."
        )
        for key in ("import_rule", "implementation_snapshot_and_launch_comparison", "snapshot"):
            if key in d8 and isinstance(d8[key], str):
                d8[key] = rewrite_protocol_text(d8[key])
    d10 = (protocol.get("change") or {}).get("D10_additivity")
    if isinstance(d10, dict) and "rule" in d10:
        d10["rule"] = (
            "This contract is never rewritten in place. Any change is a new successor "
            f"contract under a new EXP id per F-REV. The run uses NEW modules under "
            f"{EXP_PATH}implementation/typed/ and edits no "
            "implementation file of any other experiment. No amendment layers this contract."
        )
    ta = protocol.get("tools_and_admission") or {}
    gate = ta.get("admission_gate")
    if isinstance(gate, str):
        gate = rewrite_protocol_text(gate)
        gate = gate.replace(
            "(7) The four successor_contract_sha256 match trial-plan.json.",
            "(7) successor_contract_sha256 in trial-plan.json matches this contract file at launch.",
        )
        gate = gate.replace(
            "(7) The four governing-text hashes match trial-plan.json.",
            "(7) successor_contract_sha256 in trial-plan.json matches this contract file at launch.",
        )
        ta["admission_gate"] = gate
    if isinstance(protocol.get("required_artifacts"), list):
        protocol["required_artifacts"] = [
            rewrite_protocol_text(x)
            .replace("governing-text hashes", "successor_contract_sha256")
            .replace("four governing-text hashes", "successor_contract_sha256")
            if isinstance(x, str)
            else x
            for x in protocol["required_artifacts"]
        ]
    for overlay in protocol.get("corrective_overlays") or []:
        if not isinstance(overlay, dict):
            continue
        ti = overlay.get("threshold_index") or {}
        if "completeness_claims_over_four_layers" in ti:
            ti["completeness_claims_over_four_layers"] = (
                "No governing field of this contract claims a complete threshold index; "
                "F-INDEX makes the index non-normative."
            )
        if "status_of_the_index" in ti and isinstance(ti["status_of_the_index"], str):
            ti["status_of_the_index"] = rewrite_protocol_text(ti["status_of_the_index"])
    fcm = protocol.get("falsification_condition_mapping") or {}
    if fcm:
        protocol["falsification_condition_mapping"] = walk_strings(
            fcm,
            lambda t: rewrite_protocol_text(t) if isinstance(t, str) else t,
        )
    ta = protocol.get("tools_and_admission") or {}
    if isinstance(ta.get("absence_rule"), str):
        ta["provisioning_precondition"] = ta["absence_rule"]

    patch_deployed_roster(protocol)
    patch_corrective_overlays(protocol)
    patch_d4_and_invalidation(protocol)

    # Restate claim ceiling as fresh text (no held stand)
    protocol["claim_ceiling_restated"] = {
        "text_kind": "fresh",
        "tier": "crypto",
        "exact_scope_a_run_could_support": (
            "On the deployed_row_roster of this contract, with the pinned r integers, "
            "certified factorizations (or stated unfactored-cofactor bounds), and two "
            "independent evaluators agreeing: the typed table of branch exponents or "
            "bounds. WHAT DOES NOT FOLLOW: any ordinary-ECDLP claim; any statement that "
            "a deployed system is weak or safe; any claim about curves not on the roster; "
            "any claim about protocols."
        ),
        "explicitly_not_supportable_under_any_outcome": (
            "Ordinary ECDLP below rho; a vulnerability in ECDSA/Ed25519/P-256/etc.; "
            "novelty of Cheon's algorithm; closure of IDEA-20260831-ccb587."
        ),
    }


def build_execution_admission() -> dict:
    return {
        "currently_admitted": False,
        "requirements": [
            f"Verified snapshot archive of {EXP_ID} contract file and H-AUXIN-6db354 binding on a published branch or PR; archive names this experiment id only.",
            f"Implementation under {EXP_PATH}implementation/typed/ with two independent arithmetic paths that do not share factorization code.",
            "trial-plan.json naming successor_contract_sha256 and Stage artifact paths.",
            "Fresh Executor claim via tools/goal_lanes.py before launch.",
        ],
        "explicitly_not_required": [
            "Verified snapshot archive of EXP-AUXIN-7e2e3d approval chain.",
            "Clean or dirty status of any EXP-AUXIN-7e2e3d amendment file.",
            "Predecessor governing-text hashes of the held four-layer stack.",
            "Any bytes, hash or status of refused drafts EXP-AUXIN-92dccc, EXP-AUXIN-bafa2e or EXP-AUXIN-edd104.",
        ],
    }


def build_falsification_mapping(narrow: dict, gated: dict) -> dict:
    n = narrow.get("amendment", narrow)
    g = gated.get("amendment", gated)
    mapping = n.get("corrective", {}).get("falsification_condition_mapping", {})
    fc6 = n.get("corrective", {}).get("falsification_condition_mapping_fc6")
    if fc6 is None:
        fc6 = g.get("corrective", {}).get("falsification_condition_mapping_fc6")
    return {"FC1_to_FC5": mapping, "FC6": fc6}


def collect_self_reference_phrases(text: str) -> set[str]:
    patterns = [
        r"\bthis contract\b",
        r"\bthis file\b",
        r"\bthis experiment\b",
        r"\bthis specification\b",
        r"\bthis protocol\b",
        r"\bthis frozen contract\b",
        r"\bthe frozen contract\b",
        r"\bthis amendment\b",
        r"\bthese controls\b",
        r"\bthis text\b",
        rf"\b{re.escape(EXP_ID)}\b",
    ]
    found = set()
    for p in patterns:
        m = re.search(p, text, re.I)
        if m:
            found.add(m.group(0))
    # Normalize case for table: keep EXP id exact; others lower
    normalized = set()
    for ph in found:
        if ph.upper().startswith("EXP-"):
            normalized.add(EXP_ID)
        else:
            normalized.add(ph.lower())
    return normalized


def build_self_reference_table(contract_yaml: str) -> list[dict]:
    phrases = sorted(collect_self_reference_phrases(contract_yaml))
    # Ensure every F-READ R1 phrase is present even if a dump quirk missed one
    required = [
        "this contract",
        "this file",
        "this experiment",
        "this specification",
        "this protocol",
        "this frozen contract",
        "the frozen contract",
        "this text",
        "this amendment",
        EXP_ID,
    ]
    for ph in required:
        if ph not in phrases and ph.lower() not in {p.lower() for p in phrases}:
            phrases.append(ph)
    phrases = sorted(set(phrases), key=lambda x: (0 if x == EXP_ID else 1, x.lower()))
    table = []
    for ph in phrases:
        table.append({"phrase": ph, "rule_id": "R1", "closed": True})
    table.append(
        {
            "phrase": "_closure_",
            "rule_id": "R4",
            "text": (
                "Every self-referential phrase in protocol_normative and fresh fields "
                "appears above with exactly one rule, including the experiment id "
                f"{EXP_ID} listed by F-READ R1. Unlisted phrase is a draft defect."
            ),
        }
    )
    return table


def assert_no_forbidden_surfaces(body: str) -> None:
    """Stop-rule helpers: fail the build if named break surfaces remain."""
    failures = []
    if re.search(r"READ FROM specification\.yaml", body):
        failures.append("residual READ FROM specification.yaml")
    if re.search(r"All experiment\.invalidation_rules of specification\.yaml stand", body):
        failures.append("residual invalidation stand on specification.yaml")
    if re.search(r"\bstay incorporated by hash\b", body, re.I):
        failures.append("residual stay-incorporated-by-hash")
    if re.search(r"(?<!not )(?<!no )(?<!never )\bincorporated by hash\b", body, re.I):
        # Allow explicit negations in F-PREC; forbid affirmative incorporation claims.
        for m in re.finditer(r".{0,40}incorporated by hash.{0,40}", body, re.I):
            snippet = m.group(0)
            if not re.search(r"\b(no|not|never|without)\b.{0,30}incorporated by hash", snippet, re.I):
                if not re.search(r"incorporated by hash.{0,20}\b(forbidden|void|absent)\b", snippet, re.I):
                    failures.append(f"residual incorporated by hash near: {snippet!r}")
                    break
    if re.search(
        r"A later amendment may pre-register a rule",
        body,
    ):
        failures.append("residual D4 later-amendment license")
    if EXP_ID not in body:
        failures.append("EXP id missing from body")
    # self_reference_table must list EXP id (checked after table is built by caller)
    if failures:
        raise SystemExit("STOP: construction failed: " + "; ".join(failures))


def main() -> None:
    fresh = load_yaml(FRESH)["fresh"]
    typed = load_yaml(TYPED)
    narrow = load_yaml(NARROW)
    gated = load_yaml(GATED)

    protocol = extract_protocol(typed)
    protocol = walk_strings(protocol, rewrite_protocol_text)
    patch_protocol(protocol)

    for src in (narrow, gated):
        a = src.get("amendment", src)
        corr = a.get("corrective")
        if corr:
            protocol.setdefault("corrective_overlays", []).append(
                walk_strings(corr, rewrite_protocol_text)
            )
    patch_protocol(protocol)

    protocol["execution_admission"] = build_execution_admission()
    protocol["falsification_condition_mapping"] = walk_strings(
        build_falsification_mapping(narrow, gated),
        lambda t: rewrite_protocol_text(t) if isinstance(t, str) else t,
    )
    patch_protocol(protocol)
    ch = protocol.get("change") or {}
    if isinstance(ch.get("D8_custody"), dict):
        ch["D8_custody"]["trial_plan"] = (
            f"trial-plan.json under {EXP_PATH}implementation/typed/ "
            "records successor_contract_sha256 only. The run recomputes it at launch "
            "and at every stage boundary; mismatch is evidence-integrity failure."
        )
    protocol["text_kind"] = "fresh"
    protocol["semantic_lineage"] = {
        "note": (
            "Normative content restated from held amendments as fresh text in this "
            "file only. Not transcluded. Not read from held paths at run time. No "
            "content-digest binding of held records."
        ),
        "provenance_only_sources": [
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
        ],
    }

    if isinstance(protocol.get("stopping_rules"), list):
        protocol["stopping_rules"] = [
            rewrite_protocol_text(x) if isinstance(x, str) else x
            for x in protocol["stopping_rules"]
        ]
        protocol["stopping_rules"].append(
            "Outcome hierarchy: evidence-integrity stops and admission failures precede "
            "instrument falsification outcomes (N1, N2, N3, N4). There is no "
            "stop-and-escalate on deployed-row exponents. After Stage C passes, "
            "null-arm and deployed rows run to completion unless a validity rule fires."
        )

    successor = {
        "successor_contract": {
            "fresh": fresh,
            "protocol_normative": protocol,
            "transcluded": {"entries": []},
            "additions_read_together": {"text_kind": "fresh", "groups": []},
            "leaf_map": {
                "text_kind": "fresh",
                "note": "Empty. No transcluded leaves.",
                "rows": [],
            },
        }
    }

    body = yaml.dump(successor, sort_keys=False, allow_unicode=True, width=1000)
    phrases_table = build_self_reference_table(body)
    successor["successor_contract"]["self_reference_table"] = {
        "text_kind": "fresh",
        "order_matches_F_READ": True,
        "rows": phrases_table,
    }
    body = yaml.dump(successor, sort_keys=False, allow_unicode=True, width=1000)
    assert_no_forbidden_surfaces(body)
    # EJ3 closure: EXP id must appear in self_reference_table
    table_phrases = {
        r["phrase"] for r in phrases_table if isinstance(r, dict) and "phrase" in r
    }
    if EXP_ID not in table_phrases:
        raise SystemExit(f"STOP: {EXP_ID} missing from self_reference_table")

    OUT.write_text(
        "# GENERATED by build_successor.py — status draft, approved_by null.\n"
        "# Zero transclusion. Do not edit by hand; edit fresh-text.yaml or builder.\n"
        + body
    )
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print("wrote", OUT, "sha256", digest)
    print("self_reference_phrases", sorted(table_phrases))


if __name__ == "__main__":
    main()
