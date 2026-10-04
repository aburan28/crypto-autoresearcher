#!/usr/bin/env python3
"""Blind re-derivation of BQ0–BQ3 for TASK-20260929-7109a0 (joint EJ7).

Libraries: PyYAML 6.0.1 (yaml.safe_load), Python 3.12.3 stdlib
(hashlib, json, re, pathlib). No experiment runs.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path("/workspace")
OUT = ROOT / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/"
    "reviews/TASK-20260929-7109a0"
)

HELD = {
    "v1": ROOT / "experiments/EXP-AUXIN-7e2e3d/specification.yaml",
    "typed": ROOT
    / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
    "narrow": ROOT
    / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
    "gated": ROOT
    / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
    "bands": ROOT
    / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260916-bands.yaml",
    "d1d10": ROOT
    / "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260923-d1d10.yaml",
}

EXPECTED_SHA = {
    "experiments/EXP-AUXIN-7e2e3d/specification.yaml": (
        "1f803aa0a535e4c0a321dfcb3851b89cbd4cae23596ad70e1aa1fd1b06639fbc"
    ),
    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml": (
        "3c57978c91b632226c0e0543913f8a122bb16d121b0a308254b1c99cedeeaad6"
    ),
    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml": (
        "ccd11216c3250d9ab69fafa7f4252a872704772a2091fc70989a198d1ca11dcd"
    ),
    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml": (
        "77d1d5bfd8bf9d1c164903742c501f7161cc1b47814420d1957d6e39da9a8f3f"
    ),
    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260916-bands.yaml": (
        "8dcd725a316ab61c216dacba3b2575c86fb7830a0941316f74e7bb3b9f339372"
    ),
    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260923-d1d10.yaml": (
        "dfda903076ba6976ae0812d1f25f1e7a44fe3a026862ffabc2a633a37e6ae5e5"
    ),
}

LAYER_TO_FILE = {
    "v1": "experiments/EXP-AUXIN-7e2e3d/specification.yaml",
    "typed-by-hash": (
        "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml"
    ),
    "narrow-by-hash": (
        "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml"
    ),
    "gated": (
        "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml"
    ),
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    """Hash per blind-inputs.yaml canonical_form."""
    if isinstance(value, str):
        data = value.encode("utf-8")
    else:
        data = json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def canonical_bytes_repr(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )


# ---------------------------------------------------------------------------
# Path / leaf accessors
# ---------------------------------------------------------------------------

_INDEX_RE = re.compile(r"^(?P<name>[^\[\]]+)(?:\[(?P<key>[^\]]+)\])?$")
# '… item N' or '… item N.rest.of.path'
_ITEM_SPLIT_RE = re.compile(
    r"^(?P<head>.*?)\s+item\s+(?P<item>\d+)(?:\.(?P<rest>.+))?$"
)


def _split_segments(path: str) -> list[str]:
    """Split dotted path respecting bracket keys that may contain dots."""
    parts: list[str] = []
    buf = ""
    depth = 0
    for ch in path:
        if ch == "[":
            depth += 1
            buf += ch
        elif ch == "]":
            depth -= 1
            buf += ch
        elif ch == "." and depth == 0:
            if buf:
                parts.append(buf)
                buf = ""
        else:
            buf += ch
    if buf:
        parts.append(buf)
    return parts


def get_by_path(root: Any, path: str) -> Any:
    """Resolve a field path against a YAML tree.

    Supports: a.b.c, list[key] where key matches id/kind/name or mapping key,
    'item N' (1-based) on lists, 'item N.subpath', and 'span_rules[ID]' style.
    """
    path = path.strip()
    m = _ITEM_SPLIT_RE.match(path)
    if m:
        head = m.group("head")
        item_n = m.group("item")
        rest = m.group("rest")
    else:
        head = path
        item_n = None
        rest = None
    cur: Any = root
    for seg in _split_segments(head):
        sm = _INDEX_RE.match(seg)
        if sm is None:
            raise KeyError(f"bad segment {seg!r} in {path!r}")
        name, key = sm.group("name"), sm.group("key")
        if isinstance(cur, dict):
            if name not in cur:
                raise KeyError(f"missing {name!r} under path {path!r}")
            cur = cur[name]
        else:
            raise KeyError(f"cannot descend {name!r} into non-dict at {path!r}")
        if key is not None:
            cur = _index_into(cur, key, path)
    if item_n is not None:
        idx = int(item_n) - 1
        if not isinstance(cur, list):
            raise KeyError(f"item on non-list at {path!r}")
        if idx < 0 or idx >= len(cur):
            raise KeyError(
                f"item {item_n} out of range (len={len(cur)}) at {path!r}"
            )
        cur = cur[idx]
    if rest:
        if isinstance(cur, (dict, list)):
            cur = get_by_path(cur, rest)
        else:
            raise KeyError(f"cannot apply rest .{rest} at {path!r}")
    return cur


def _index_into(cur: Any, key: str, path: str) -> Any:
    if isinstance(cur, dict):
        if key in cur:
            return cur[key]
        raise KeyError(f"dict key {key!r} missing at {path!r}")
    if isinstance(cur, list):
        # Match by id / kind / name / field / role fields, or exact string.
        for el in cur:
            if isinstance(el, dict):
                for k in ("id", "kind", "name", "field", "role"):
                    if el.get(k) == key:
                        return el
            elif el == key:
                return el
        # Also allow numeric index (0-based or 1-based ambiguous — prefer 0-based
        # only if key is digits and in range).
        if key.isdigit():
            i = int(key)
            if 0 <= i < len(cur):
                return cur[i]
        raise KeyError(f"list key {key!r} missing at {path!r}")
    raise KeyError(f"cannot index into {type(cur)} at {path!r}")


def parse_field_name(field: str) -> dict[str, Any]:
    """Parse a governing_text_table field name into structured parts."""
    info: dict[str, Any] = {
        "raw": field,
        "prefix": None,
        "path": None,
        "span_ids": [],
        "outside_spans": [],
        "except_suffix": None,
        "file_row": None,
        "special": None,
    }
    if field.startswith("file:"):
        info["prefix"] = "file"
        info["file_row"] = field[len("file:") :]
        return info

    # Patterns:
    #   typed:path
    #   typed:path span ID
    #   typed:path outside span ID
    #   typed:path outside spans ID, ID
    #   typed:path span ID1  (and separate outside)
    #   narrow:span_rules[INV-CLAIM] except .replacement
    #   narrow:span_rules[INV-CLAIM].replacement
    m = re.match(
        r"^(typed|narrow|gated|v1):(.+)$", field
    )
    if not m:
        info["special"] = "unparsed"
        return info
    info["prefix"] = m.group(1)
    rest = m.group(2)

    m_out_multi = re.match(
        r"^(?P<path>.+?)\s+outside spans?\s+(?P<spans>.+)$", rest
    )
    m_span = re.match(
        r"^(?P<path>.+?)\s+span\s+(?P<span>\S+)$", rest
    )
    m_except = re.match(
        r"^(?P<path>.+?)\s+except\s+(?P<ex>.+)$", rest
    )
    if m_out_multi:
        info["path"] = m_out_multi.group("path")
        spans = [s.strip() for s in m_out_multi.group("spans").split(",")]
        info["outside_spans"] = spans
    elif m_span and " outside " not in rest:
        info["path"] = m_span.group("path")
        info["span_ids"] = [m_span.group("span")]
    elif m_except:
        info["path"] = m_except.group("path")
        info["except_suffix"] = m_except.group("ex")
    else:
        info["path"] = rest
    return info


def apply_span_excision(text: str, from_s: str, through_s: str) -> str:
    """Remove the span [first from .. end of first through at/after from]."""
    i = text.find(from_s)
    if i < 0:
        raise ValueError(f"from not found: {from_s!r}")
    j = text.find(through_s, i)
    if j < 0:
        raise ValueError(f"through not found: {through_s!r}")
    j_end = j + len(through_s)
    return text[:i] + text[j_end:]


def apply_span_extract(text: str, from_s: str, through_s: str) -> str:
    i = text.find(from_s)
    if i < 0:
        raise ValueError(f"from not found: {from_s!r}")
    j = text.find(through_s, i)
    if j < 0:
        raise ValueError(f"through not found: {through_s!r}")
    j_end = j + len(through_s)
    return text[i:j_end]


# ---------------------------------------------------------------------------
# Load held texts
# ---------------------------------------------------------------------------

def load_all():
    docs = {}
    raw = {}
    sha = {}
    for key, path in HELD.items():
        raw[key] = path.read_bytes()
        sha[key] = hashlib.sha256(raw[key]).hexdigest()
        docs[key] = yaml.safe_load(raw[key].decode("utf-8"))
    return docs, sha


def root_for_prefix(docs, prefix: str):
    if prefix == "v1":
        return docs["v1"]["experiment"]
    if prefix == "typed":
        return docs["typed"]["amendment"]
    if prefix == "narrow":
        return docs["narrow"]["amendment"]
    if prefix == "gated":
        return docs["gated"]["amendment"]
    raise KeyError(prefix)


def envelope_role_map(field_path: str) -> str | None:
    """Map typed:X envelope field to gated field of same role."""
    # typed:approval.status -> approval.status on gated
    if field_path.startswith("approval."):
        return field_path
    simple = {
        "id",
        "experiment_id",
        "hypothesis_id",
        "predecessor_amendment",
        "predecessor_status",
        "question_id",
        "goal_id",
        "batch_id",
        "producer_task",
        "producer_snapshot",
        "review_plan_id",
        "decision_id",
        "decision_id_note",
        "recorded_at",
        "kind",
        "status",
        "cites",
        "design_record",
        "authorization",
        "defect",
    }
    if field_path in simple:
        return field_path
    return None


def build_span_rule_index(docs):
    """Map span id -> {from, through, replacement, file, field, layer}."""
    idx = {}
    narrow = docs["narrow"]["amendment"]
    for rule in narrow.get("span_rules", []):
        idx[rule["id"]] = {
            "from": rule["from"],
            "through": rule["through"],
            "replacement": rule["replacement"],
            "field": rule["field"],
            "source": "narrow",
        }
    # custody span rules may be under custody_consequences? No - they're in span_rules
    gated = docs["gated"]["amendment"]
    for rule in gated.get("gated_span_rules", []):
        idx[rule["id"]] = {
            "from": rule["from"],
            "through": rule["through"],
            "replacement": rule["replacement"],
            "field": rule["field"],
            "source": "gated",
            "file": rule.get("file"),
            "layer": rule.get("layer"),
        }
    return idx


def resolve_replacement_via(via: str, docs, span_idx) -> Any:
    """Resolve effective text when via names a replacement source."""
    m = re.match(
        r"AMD-20260927-narrow\.yaml span_rules\[(?P<id>[^\]]+)\]\.replacement$",
        via,
    )
    if m:
        return span_idx[m.group("id")]["replacement"]
    m = re.match(r"gated_span_rules\[(?P<id>[^\]]+)\]\.replacement$", via)
    if m:
        return span_idx[m.group("id")]["replacement"]
    if via.startswith(
        "corrective.threshold_index.text of this file"
    ) or via == "supersedes_fields -> corrective.threshold_index.text":
        return docs["gated"]["amendment"]["corrective"]["threshold_index"][
            "text"
        ]
    if via == (
        "supersedes_fields -> corrective.falsification_condition_mapping_fc6.outcome"
    ):
        return docs["gated"]["amendment"]["corrective"][
            "falsification_condition_mapping_fc6"
        ]["outcome"]
    if via == (
        "supersedes_fields -> incorporates_by_hash.status_of_the_incorporated_files of this file"
    ):
        return docs["gated"]["amendment"]["incorporates_by_hash"][
            "status_of_the_incorporated_files"
        ]
    if via == "supersedes_fields -> reading_of_self_references of this file":
        return docs["gated"]["amendment"]["reading_of_self_references"]
    if via == "supersedes_fields -> precedence of this file":
        return docs["gated"]["amendment"]["precedence"]
    if via == "supersedes_fields -> governing_text_table of this file":
        return docs["gated"]["amendment"]["governing_text_table"]
    if via == "AMD-20260927-narrow.yaml corrective.bin_by_status":
        return docs["narrow"]["amendment"]["corrective"]["bin_by_status"]
    if via == "AMD-20260927-narrow.yaml corrective.interpretation_limits_item_6":
        return docs["narrow"]["amendment"]["corrective"][
            "interpretation_limits_item_6"
        ]
    if via == (
        "AMD-20260927-narrow.yaml corrective.tools."
        "certificate_and_factoring_library.minimum_version"
    ):
        return docs["narrow"]["amendment"]["corrective"]["tools"][
            "certificate_and_factoring_library"
        ]["minimum_version"]
    if via == (
        "AMD-20260927-narrow.yaml corrective.tools."
        "certificate_and_factoring_library.version_command"
    ):
        return docs["narrow"]["amendment"]["corrective"]["tools"][
            "certificate_and_factoring_library"
        ]["version_command"]
    return None


def typed_supersedes_effective(field: str, via: str, docs) -> Any:
    """Effective text for a v1 leaf superseded by typed-by-hash.

    Reading chosen (BQ0): for 'replaced by PATH', use that typed value;
    for multi-path replacements, use a mapping of named paths to values;
    for retired/removed, use the supersedes_fields clause string itself;
    for 'strengthened by', use the strengthening typed field value alone
    (not a union with the v1 original);
    for 'meaning fixed by', keep the original v1 leaf string and note that
    meaning comes from named typed fields (effective text = v1 leaf).
    """
    items = docs["typed"]["amendment"]["supersedes_fields"]
    # Parse item number(s) from via
    item_nums = [int(x) for x in re.findall(r"item(?:s)?\s+(\d+)", via)]
    if "last item" in via:
        return items[-1]

    # Map field path to replacement content
    parsed = parse_field_name(field)
    path = parsed["path"] or ""

    # Special cases by via content
    if "retired" in via or "removed" in via:
        # Use the supersedes clause
        n = item_nums[0]
        return items[n - 1]

    if "meaning fixed" in via:
        # Keep v1 text; meaning fixed elsewhere
        return get_by_path(docs["v1"]["experiment"], path)

    if "no field governs" in via or field.startswith("file:"):
        n = item_nums[0] if item_nums else len(items)
        return items[n - 1] if "last" not in via else items[-1]

    # Replacement mappings inferred from supersedes clauses + field path
    stages = docs["typed"]["amendment"]["stages"]
    d1_rows = docs["typed"]["amendment"]["change"]["D1_pins"]["rows"]
    controls = docs["typed"]["amendment"]["controls"]

    if path == "hypothesis_id":
        return "H-AUXIN-6db354"
    if path == "inputs.procedure":
        return stages
    if path.startswith("stages[") and path.endswith("].purpose"):
        return stages
    if path == "inputs.instrument":
        return {
            "change.D6_factoring": docs["typed"]["amendment"]["change"][
                "D6_factoring"
            ],
            "change.D7_certificates": docs["typed"]["amendment"]["change"][
                "D7_certificates"
            ],
            "tools_and_admission": docs["typed"]["amendment"][
                "tools_and_admission"
            ],
        }
    if path.endswith(".r_pin_source") or "frozen_curve_list" in path:
        # Find matching row id
        m = re.search(r"frozen_curve_list\[([^\]]+)\]", path)
        if m:
            rid = m.group(1)
            for row in d1_rows:
                if row.get("id") == rid:
                    return row
        return d1_rows
    if path == "inputs.parameters.confounder_field_vs_order":
        return docs["typed"]["amendment"]["change"]["D1_pins"][
            "confounder_check"
        ]
    if path in (
        "inputs.parameters.cost_expression",
        "inputs.parameters.E_r",
    ):
        return docs["typed"]["amendment"]["definitions"]["typed_costs"]
    if "positive_planted" in path or "null_safeprime" in path:
        # replaced by C-PLANT-M, C-PLANT-P, C-PLANT-PL, C-INERT
        wanted = ["C-PLANT-M", "C-PLANT-P", "C-PLANT-PL", "C-INERT"]
        out = []
        for c in controls:
            if c.get("id") in wanted:
                out.append(c)
        return out
    if "controls[ordering]" in path:
        c_order = next(c for c in controls if c.get("id") == "C-ORDER")
        return {"stages": stages, "C-ORDER": c_order}
    if "independent_variables" in path:
        return {
            "note": "PLANTED and SAFEPRIME replaced by control ids and null arm",
            "null_arm": docs["typed"]["amendment"]["null_arm"],
            "control_ids": [c.get("id") for c in controls],
        }
    if path.startswith("metrics."):
        return docs["typed"]["amendment"]["metrics"]
    if path.startswith("preregistered_prediction"):
        return docs["typed"]["amendment"]["preregistered_prediction"]
    if path.startswith("replication.seeds"):
        return docs["typed"]["amendment"]["null_arm"]
    if path.startswith("cost_model_disclosure"):
        return {
            "definitions.typed_costs": docs["typed"]["amendment"][
                "definitions"
            ]["typed_costs"],
            "change.D9_labelling": docs["typed"]["amendment"]["change"][
                "D9_labelling"
            ],
        }
    if path.startswith("stopping_rules"):
        return docs["typed"]["amendment"]["stopping_rules"]
    if path == "success_criterion" or path.startswith("falsification_criterion"):
        return {
            "success_criterion": docs["typed"]["amendment"][
                "success_criterion"
            ],
            "falsification_criterion": docs["typed"]["amendment"][
                "falsification_criterion"
            ],
        }
    if path.startswith("required_artifacts"):
        return docs["typed"]["amendment"]["required_artifacts"]
    if path.startswith("launch_gate"):
        return get_by_path(docs["v1"]["experiment"], path)

    # Fallback: supersedes clause text
    if item_nums:
        return items[item_nums[0] - 1]
    return None


def resolve_row(row: dict, docs, span_idx, bq0: list) -> dict:
    field = row["field"]
    layer = row["layer"]
    via = row["via"]
    parsed = parse_field_name(field)
    governing_file = LAYER_TO_FILE.get(layer)
    clauses = [f"layer={layer}", f"via={via}"]
    effective: Any = None
    errors: list[str] = []

    # --- file: rows (bands / d1d10 govern nothing) ---
    if parsed["prefix"] == "file":
        governing_file = None
        if "bands" in field:
            effective = docs["typed"]["amendment"]["supersedes_fields"][-1]
            clauses.append(
                "typed supersedes_fields last item: no field of bands governs"
            )
        elif "d1d10" in field:
            effective = docs["gated"]["amendment"]["governs_nothing"][1]
            clauses.append("governs_nothing item 2 of gated / narrow via")
        else:
            bq0.append(
                {
                    "quote": field,
                    "admissible_readings": ["unknown file-row"],
                    "depends": "BQ2 effective text",
                    "implication_only": True,
                }
            )
            effective = ""
        return _pack(
            field, governing_file, layer, via, effective, clauses, errors
        )

    # --- via names a concrete replacement ---
    rep = resolve_replacement_via(via, docs, span_idx)
    if rep is not None and (
        parsed["span_ids"]
        or via.startswith("supersedes_fields")
        or via.startswith("AMD-20260927-narrow.yaml corrective")
        or via.startswith("corrective.threshold")
    ):
        effective = rep
        clauses.append("resolved via named replacement/corrective source")
        # For span rows, governing file is the layer's file (replacement lives
        # in narrow or gated). Prefer LAYER_TO_FILE.
        return _pack(
            field, governing_file, layer, via, effective, clauses, errors
        )

    # --- gated span replacement via ---
    if via.startswith("gated_span_rules["):
        effective = resolve_replacement_via(via, docs, span_idx)
        return _pack(
            field, governing_file, layer, via, effective, clauses, errors
        )

    # --- envelope: gated field of same role ---
    if "envelope_not_incorporated" in via or "narrow_envelope_not_incorporated" in via:
        # Field like typed:id or typed:approval.status or narrow:id
        # Same-role field on gated
        path = parsed["path"]
        # For narrow envelope fields the path may be like 'id'
        try:
            if path and path.startswith("approval"):
                effective = get_by_path(docs["gated"]["amendment"], path)
            elif path:
                # narrow:batch_id -> gated batch_id; typed:predecessor_* may be absent on gated
                try:
                    effective = get_by_path(docs["gated"]["amendment"], path)
                except KeyError:
                    # predecessor_amendment / predecessor_status / defect not on gated
                    # Reading: gated has no field of that role; effective text is null
                    # with note that envelope rule still assigns governance to gated.
                    bq0.append(
                        {
                            "quote": (
                                f"{field}: envelope says gated field of same "
                                f"role governs, but gated has no '{path}'"
                            ),
                            "admissible_readings": [
                                "effective text is null (no same-role field)",
                                "fall back to narrow/typed envelope value (excluded by envelope rule)",
                            ],
                            "depends": "BQ2 effective text and sha256",
                            "implication_only": False,
                            "chosen": "null",
                        }
                    )
                    effective = None
            else:
                errors.append("envelope without path")
        except Exception as e:
            errors.append(f"envelope resolve: {e}")
            effective = None
        return _pack(
            field, governing_file, layer, via, effective, clauses, errors
        )

    if via == "identity field; this file states the same value":
        path = parsed["path"]
        effective = get_by_path(docs["gated"]["amendment"], path)
        return _pack(
            field, governing_file, layer, via, effective, clauses, errors
        )

    # --- typed supersedes of v1 leaves ---
    if via.startswith("typed-by-hash supersedes") or via.startswith(
        "narrow-by-hash governs_nothing"
    ):
        try:
            effective = typed_supersedes_effective(field, via, docs)
            if via.startswith("narrow-by-hash governs"):
                effective = docs["gated"]["amendment"]["governs_nothing"][1]
                governing_file = None
        except Exception as e:
            errors.append(f"supersedes resolve: {e}")
            bq0.append(
                {
                    "quote": f"{field} / {via}",
                    "admissible_readings": [
                        "use supersedes clause string",
                        "use named typed replacement object",
                        "leave undetermined",
                    ],
                    "depends": "BQ2 effective text",
                    "implication_only": False,
                    "error": str(e),
                }
            )
            effective = via
        return _pack(
            field, governing_file, layer, via, effective, clauses, errors
        )

    # --- incorporated leaf (typed or narrow) possibly with outside-span excision ---
    if (
        via.startswith("incorporates.sha256")
        or via.startswith("incorporates_by_hash.sha256")
        or via == "this file"
        or via.startswith("not superseded")
    ):
        prefix = parsed["prefix"]
        path = parsed["path"]
        try:
            if via.startswith("not superseded") or (
                prefix == "v1" and layer == "v1"
            ):
                effective = get_by_path(docs["v1"]["experiment"], path)
            elif prefix == "typed":
                effective = get_by_path(docs["typed"]["amendment"], path)
            elif prefix == "narrow":
                effective = get_by_path(docs["narrow"]["amendment"], path)
            elif prefix == "gated":
                effective = get_by_path(docs["gated"]["amendment"], path)
            else:
                raise KeyError(f"prefix {prefix}")
        except Exception as e:
            errors.append(f"leaf get: {e}")
            # Try except .replacement case: path is span_rules[INV-CLAIM]
            if parsed["except_suffix"]:
                try:
                    base = get_by_path(
                        docs["narrow"]["amendment"], parsed["path"]
                    )
                    if isinstance(base, dict) and parsed[
                        "except_suffix"
                    ].startswith("."):
                        key = parsed["except_suffix"][1:]
                        effective = {k: v for k, v in base.items() if k != key}
                    else:
                        effective = base
                        errors.append("except_suffix handling fallback")
                except Exception as e2:
                    errors.append(f"except fallback: {e2}")
                    effective = None
            else:
                effective = None

        # outside span excision
        if parsed["outside_spans"] and isinstance(effective, str):
            for sid in parsed["outside_spans"]:
                if sid not in span_idx:
                    errors.append(f"unknown span {sid}")
                    continue
                rule = span_idx[sid]
                try:
                    # Verify span hash if we can
                    extracted = apply_span_extract(
                        effective, rule["from"], rule["through"]
                    )
                    got = hashlib.sha256(extracted.encode("utf-8")).hexdigest()
                    # Look up expected hash from rule source file
                    expected = None
                    if rule["source"] == "narrow":
                        for r in docs["narrow"]["amendment"]["span_rules"]:
                            if r["id"] == sid:
                                expected = r.get("replaced_span_sha256")
                    else:
                        for r in docs["gated"]["amendment"][
                            "gated_span_rules"
                        ]:
                            if r["id"] == sid:
                                expected = r.get("replaced_span_sha256")
                    if expected and got != expected:
                        bq0.append(
                            {
                                "quote": (
                                    f"span {sid} hash mismatch: got {got} "
                                    f"expected {expected}"
                                ),
                                "admissible_readings": [
                                    "still excise by from/through",
                                    "stop as undetermined",
                                ],
                                "depends": f"BQ2 outside-span for {field}",
                                "implication_only": False,
                                "chosen": "still excise by from/through",
                            }
                        )
                    effective = apply_span_excision(
                        effective, rule["from"], rule["through"]
                    )
                except Exception as e:
                    errors.append(f"excise {sid}: {e}")
                    bq0.append(
                        {
                            "quote": f"cannot excise span {sid} from {field}: {e}",
                            "admissible_readings": [
                                "leave full text",
                                "mark undetermined",
                            ],
                            "depends": "BQ2 effective text",
                            "implication_only": False,
                            "chosen": "leave full text with error noted",
                        }
                    )
        elif parsed["outside_spans"] and not isinstance(effective, str):
            bq0.append(
                {
                    "quote": (
                        f"{field}: outside-span on non-string leaf "
                        f"type={type(effective).__name__}"
                    ),
                    "admissible_readings": [
                        "stringify then excise",
                        "refuse excision; hash whole value",
                        "undetermined",
                    ],
                    "depends": "BQ2 effective text and sha256",
                    "implication_only": False,
                    "chosen": "hash whole value without excision",
                }
            )

        # except .replacement on mapping
        if parsed["except_suffix"] and effective is not None:
            if isinstance(effective, dict) and parsed[
                "except_suffix"
            ].startswith("."):
                key = parsed["except_suffix"][1:]
                effective = {k: v for k, v in effective.items() if k != key}
                clauses.append(f"removed key {key}")

        return _pack(
            field, governing_file, layer, via, effective, clauses, errors
        )

    # Fallback
    bq0.append(
        {
            "quote": f"unhandled via for {field}: {via}",
            "admissible_readings": [
                "treat as undetermined",
                "attempt layer-default leaf fetch",
            ],
            "depends": "BQ2 row",
            "implication_only": False,
            "chosen": "attempt layer-default leaf fetch",
        }
    )
    try:
        prefix = parsed["prefix"]
        path = parsed["path"]
        if prefix == "gated":
            effective = get_by_path(docs["gated"]["amendment"], path)
        elif prefix == "narrow":
            effective = get_by_path(docs["narrow"]["amendment"], path)
        elif prefix == "typed":
            effective = get_by_path(docs["typed"]["amendment"], path)
        elif prefix == "v1":
            effective = get_by_path(docs["v1"]["experiment"], path)
    except Exception as e:
        errors.append(str(e))
        effective = None
    return _pack(
        field, governing_file, layer, via, effective, clauses, errors
    )


def _pack(field, governing_file, layer, via, effective, clauses, errors):
    text_for_hash = effective
    # None -> JSON null
    sha = canonical_hash(text_for_hash)
    eff_repr = canonical_bytes_repr(text_for_hash)
    return {
        "field": field,
        "governing_file": governing_file,
        "layer": layer,
        "via": via,
        "effective_text": eff_repr,
        "sha256": sha,
        "clauses": clauses,
        "errors": errors,
        "effective_is_string": isinstance(text_for_hash, str),
        "effective_python_type": type(text_for_hash).__name__,
    }


# ---------------------------------------------------------------------------
# BQ1: self-referential phrase inventory
# ---------------------------------------------------------------------------

DOC_NOUN = (
    r"(?:file|files|layer|layers|contract|contracts|specification|"
    r"specifications|amendment|amendments|protocol|protocols|text|texts|"
    r"experiment|experiments|record|records|table|tables|convention|"
    r"conventions|document|documents|report|reports|decision|decisions|"
    r"hypothesis|yaml|stack|receipt|manifest|artifact|artifacts|"
    r"design|transcript|transcripts|source|sources)"
)

DEICTIC = re.compile(
    rf"(?P<phrase>"
    rf"\b(?:this|these|the|that|those)\s+(?:combined\s+)?{DOC_NOUN}\b|"
    rf"\b(?:the\s+)?(?:held|combined)\s+{DOC_NOUN}\b|"
    rf"\b(?:above|below|following)\b|"
    rf"\bthe\s+following\b|"
    rf"\bthis\s+file(?:'?s)?\b|"
    rf"\bthese\s+files\b|"
    rf"\bthis\s+(?:text|amendment|protocol|experiment|contract|specification|"
    rf"layer|table|record|decision|hypothesis)\b|"
    rf"\bthe\s+(?:held|combined|governing)\s+(?:text|texts|stack|file|files|"
    rf"fields?|layers?)\b"
    rf")",
    re.IGNORECASE,
)

PATH_PHRASE = re.compile(
    r"(?P<phrase>"
    r"(?:experiments|ledger|coordination|inputs|research|tools|docs|"
    r"templates|agents|knowledge|orchestration)/"
    r"[A-Za-z0-9_./\-]+\.(?:yaml|yml|md|json|py|txt|pdf)"
    r"|"
    r"AMD-20[0-9]{6}-[A-Za-z0-9_\-]+\.yaml"
    r"|"
    r"AMD-EXP-AUXIN-7e2e3d-20[0-9]{6}-[A-Za-z0-9_\-]+"
    r"|"
    r"specification\.yaml"
    r"|"
    r"EXP-AUXIN-7e2e3d"
    r")"
)

AMEND_EXP_FORM = re.compile(
    r"(?P<phrase>\b(?:amendment|experiment)\.[A-Za-z_][A-Za-z0-9_\.\[\]\-]*)"
)


def iter_string_leaves(obj: Any, prefix: str = ""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            yield from iter_string_leaves(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{prefix}[{i}]"
            yield from iter_string_leaves(v, p)
    elif isinstance(obj, str):
        yield prefix, obj


def referent_for_phrase(phrase: str, file_key: str, leaf_path: str, docs) -> dict:
    """Fix referent using reading_of_self_references / governs_nothing."""
    pl = phrase.lower().strip()
    gated_ros = docs["gated"]["amendment"]["reading_of_self_references"]
    result = {
        "referent": None,
        "fixing_clause": None,
        "unfixed": False,
    }
    if pl in ("this file", "this file's"):
        # Depends which file the text is written in
        fmap = {
            "v1": (
                "experiments/EXP-AUXIN-7e2e3d/specification.yaml",
                "reading_of_self_references: 'This file' means the file in which the text is written",
            ),
            "typed": (
                "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml "
                "(sha256 3c57978c...)",
                "gated reading_of_self_references / narrow incorporates.reading_of_self_references",
            ),
            "narrow": (
                "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml "
                "(sha256 ccd11216...)",
                "gated reading_of_self_references",
            ),
            "gated": (
                "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
                "gated reading_of_self_references",
            ),
            "bands": (
                "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260916-bands.yaml",
                "local deictic in bands file (governs_nothing says it governs no run leaf)",
            ),
            "d1d10": (
                "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260923-d1d10.yaml",
                "local deictic in d1d10 file (governs_nothing)",
            ),
        }
        ref, clause = fmap.get(file_key, (None, None))
        result["referent"] = ref
        result["fixing_clause"] = clause
        return result
    if "combined governing text" in pl or pl in (
        "this text",
        "this amendment",
        "this protocol",
        "the combined text",
        "the combined governing text",
        "the governing text",
        "held text",
        "the held text",
        "the held texts",
        "held texts",
    ):
        result["referent"] = (
            "combined governing text: each leaf resolved through "
            "governing_text_table of AMD-20260928-gated.yaml "
            "(v1 + typed-by-hash + narrow-by-hash + gated)"
        )
        result["fixing_clause"] = (
            "AMD-20260928-gated.yaml reading_of_self_references / precedence"
        )
        return result
    if phrase.startswith("amendment.") or phrase.startswith("experiment."):
        result["referent"] = (
            f"path {phrase} in the combined governing text "
            f"(reading_of_self_references)"
        )
        result["fixing_clause"] = (
            "gated reading_of_self_references: amendment.<path> means "
            "combined governing text leaf"
        )
        return result
    if "/" in phrase or phrase.endswith(".yaml") or phrase.startswith("AMD-"):
        result["referent"] = f"named path/id {phrase}"
        result["fixing_clause"] = (
            "verbatim file name or path in held text; "
            "if not in the six held files, BQ0 records do-not-open"
        )
        return result
    if pl in ("above", "below", "following", "the following"):
        result["referent"] = None
        result["unfixed"] = True
        result["fixing_clause"] = (
            "deictic without explicit antecedent in matching rule"
        )
        return result
    # Generic "the file" / "this layer" etc.
    result["referent"] = f"context-dependent ({phrase!r} in {file_key}:{leaf_path})"
    result["unfixed"] = True
    result["fixing_clause"] = None
    return result


def collect_bq1(docs) -> tuple[list, list, str]:
    matching_rule = (
        "Scan every string leaf returned by yaml.safe_load over the six held "
        "files. An occurrence is recorded when a regex match captures (a) a "
        "deictic/definite description whose head noun is a document-ish word "
        "(file, layer, contract, specification, amendment, protocol, text, "
        "experiment, record, table, convention, document, report, decision, "
        "hypothesis, yaml, stack, receipt, manifest, artifact, design, "
        "transcript, source) optionally qualified by held/combined/governing, "
        "or the bare deictics above/below/following/the following; (b) a "
        "repository-relative path or AMD-*/specification.yaml/EXP-AUXIN-7e2e3d "
        "token; or (c) an amendment.<path> or experiment.<path> form. Matching "
        "is case-insensitive for (a). Overlapping matches: prefer the longest "
        "match at each start offset; do not double-count nested captures of the "
        "same span. Character offset is 0-based within the leaf string as the "
        "YAML safe loader returned it."
    )
    occurrences = []
    unfixed = []
    file_keys = [
        ("v1", "experiments/EXP-AUXIN-7e2e3d/specification.yaml", docs["v1"]),
        (
            "typed",
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
            docs["typed"],
        ),
        (
            "narrow",
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
            docs["narrow"],
        ),
        (
            "gated",
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
            docs["gated"],
        ),
        (
            "bands",
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260916-bands.yaml",
            docs["bands"],
        ),
        (
            "d1d10",
            "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260923-d1d10.yaml",
            docs["d1d10"],
        ),
    ]
    for fkey, fpath, doc in file_keys:
        for leaf_path, text in iter_string_leaves(doc):
            spans: list[tuple[int, int, str, str]] = []  # start,end,phrase,kind
            for rx, kind in (
                (DEICTIC, "deictic"),
                (PATH_PHRASE, "path"),
                (AMEND_EXP_FORM, "amendment_or_experiment_form"),
            ):
                for m in rx.finditer(text):
                    spans.append(
                        (m.start("phrase"), m.end("phrase"), m.group("phrase"), kind)
                    )
            # longest-first non-overlapping
            spans.sort(key=lambda t: (-(t[1] - t[0]), t[0]))
            taken: list[tuple[int, int]] = []
            selected = []
            for s, e, phrase, kind in spans:
                if any(not (e <= a or s >= b) for a, b in taken):
                    continue
                taken.append((s, e))
                selected.append((s, e, phrase, kind))
            selected.sort(key=lambda t: t[0])
            for s, e, phrase, kind in selected:
                ref = referent_for_phrase(phrase, fkey, leaf_path, docs)
                rec = {
                    "file": fpath,
                    "field_path": leaf_path,
                    "char_offset": s,
                    "phrase": phrase,
                    "match_kind": kind,
                    "referent": ref["referent"],
                    "fixing_clause": ref["fixing_clause"],
                }
                occurrences.append(rec)
                if ref["unfixed"]:
                    unfixed.append(rec)
    return occurrences, unfixed, matching_rule


# ---------------------------------------------------------------------------
# BQ2 dependence + BQ3 topics
# ---------------------------------------------------------------------------

DEPENDENCE_PATTERNS = [
    (
        "sha256",
        re.compile(
            r"sha256|content hash|path_sha256|hash-commit|hash.commit|"
            r"computes the sha256|compares (?:it|each) with the value|"
            r"mismatch|digest",
            re.I,
        ),
    ),
    (
        "bytes_or_cleanliness",
        re.compile(
            r"\bdirty\b|\bclean\b|byte-for-byte|bytes of|working.tree|"
            r"dirty-path|git status|cleanliness",
            re.I,
        ),
    ),
    (
        "presence_or_archive",
        re.compile(
            r"archived|archive|presence of|must (?:exist|be present)|"
            r"snapshot|path_sha256|verified against Git",
            re.I,
        ),
    ),
    (
        "named_file_gate",
        re.compile(
            r"(?:hash_check|admission_gate|launch_gate|custody|"
            r"evidence-integrity stop|blocks_scientific_run|"
            r"before any use).*?(?:file|yaml|path|record)",
            re.I | re.S,
        ),
    ),
]

RUNTIME_DECISION = re.compile(
    r"\b(?:gate|stop|refuse|refusal|admit|admission|invalid(?:ation)?|"
    r"validity|outcome|custody|launch|authorized|before (?:any|Stage)|"
    r"hash_check|mismatch means|reader stops|evidence-integrity)\b",
    re.I,
)


def find_dependences(effective_text: str) -> list:
    if not isinstance(effective_text, str):
        text = effective_text
    else:
        text = effective_text
    if not isinstance(text, str):
        text = canonical_bytes_repr(text)
    deps = []
    # Only flag if the text also looks like a run-time decision
    if not RUNTIME_DECISION.search(text):
        # Still check explicit hash_check / dirty clauses
        if not re.search(
            r"hash_check|dirty|sha256 of|path_sha256|admission_gate", text, re.I
        ):
            return []
    # Named file/path mentions near dependence language
    for kind, rx in DEPENDENCE_PATTERNS:
        for m in rx.finditer(text):
            # Extract a short clause window
            a = max(0, m.start() - 80)
            b = min(len(text), m.end() + 120)
            clause = text[a:b].replace("\n", " ")
            # Try to name a file/path in the window
            paths = PATH_PHRASE.findall(clause)
            target = paths[0] if paths else "(clause-local; see quote)"
            deps.append(
                {
                    "kind": kind,
                    "file_path_or_record": target,
                    "clause_quote": clause.strip(),
                }
            )
    # Dedup by quote
    seen = set()
    out = []
    for d in deps:
        k = (d["kind"], d["clause_quote"][:120])
        if k in seen:
            continue
        seen.add(k)
        out.append(d)
    return out


TOPIC_RULES = [
    (
        "revision",
        re.compile(
            r"\b(?:supersede|amendment|new file under a new id|revis(?:e|ion)|"
            r"additive|span_rules|replaced_by|does_not_rewrite|"
            r"immutability|any later change)\b",
            re.I,
        ),
    ),
    (
        "approval",
        re.compile(
            r"\b(?:approv(?:e|ed|al)|approved_if_and_only_if|review_required|"
            r"authorized|authorization|until_approved)\b",
            re.I,
        ),
    ),
    (
        "custody",
        re.compile(
            r"\b(?:sha256|hash_check|path_sha256|dirty|clean|archiv(?:e|ed|ing)|"
            r"custody|hash-commit|content hash|snapshot)\b",
            re.I,
        ),
    ),
    (
        "write_scope",
        re.compile(
            r"\bwrite_scope\b|paths? may be written|new modules go under|"
            r"implementation/typed/",
            re.I,
        ),
    ),
    (
        "reading_of_references",
        re.compile(
            r"\breading_of_self_references\b|conventions\.Q0-11|"
            r"Every reference|provenance only|means the combined|"
            r"\"This file\" means|self-referen",
            re.I,
        ),
    ),
]

PROTOCOL_CONTENT = re.compile(
    r"\b(?:gate|stop|validity|invalidation|outcome|control|definition|"
    r"custody|pin|parameter|must |shall |refuse|admission|threshold|"
    r"recipe|timeout|factoring|certificate|bins?|stage[s ]|"
    r"success_criterion|falsification|stopping_rules|required_artifacts|"
    r"hash_check|launch)\b",
    re.I,
)
MACHINERY_ONLY = re.compile(
    r"^(?:AMD-EXP-AUXIN|EXP-AUXIN|H-AUXIN|RQ-AUXIN|GOAL-AUXIN|BATCH-|"
    r"TASK-202|DEC-202|REVIEW-AUXIN|RUN-AUXIN|"
    r"additive_|review_required|approved|"
    r"[0-9a-f]{64}|"
    r"\d{4}-\d{2}-\d{2})",
    re.I,
)


def classify_bq3(effective_text: Any) -> dict:
    text = (
        effective_text
        if isinstance(effective_text, str)
        else canonical_bytes_repr(effective_text)
    )
    topics = []
    for name, rx in TOPIC_RULES:
        m = rx.search(text)
        if m:
            a = max(0, m.start() - 40)
            b = min(len(text), m.end() + 80)
            topics.append(
                {
                    "topic": name,
                    "clause_quote": text[a:b].replace("\n", " ").strip(),
                }
            )
    classifying_rules = (
        "A row is protocol content if its effective text states a gate, stop, "
        "validity/invalidation rule, outcome, control, definition, custody "
        "check, pin, parameter, stage rule, success/falsification criterion, "
        "stopping rule, required artifact, admission/launch rule, or any other "
        "rule a run must obey (matched by keyword). Otherwise, if it only "
        "states identity, approval status, provenance, citation, or how held "
        "files govern one another without a run-time obedience rule beyond "
        "layer machinery, it is machinery only. Mixed rows are protocol "
        "content. Envelope identity fields (id, batch_id, recorded_at, pure "
        "citation lists without gates) are machinery only unless they embed a "
        "protocol rule."
    )
    if topics or PROTOCOL_CONTENT.search(text):
        # Envelope-ish short identity?
        stripped = text.strip()
        if (
            len(stripped) < 80
            and not PROTOCOL_CONTENT.search(stripped)
            and not topics
        ):
            content_class = "machinery_only"
            class_clause = stripped
        elif (
            not topics
            and not PROTOCOL_CONTENT.search(text)
        ):
            content_class = "machinery_only"
            class_clause = text[:200]
        else:
            content_class = "protocol_content"
            m = PROTOCOL_CONTENT.search(text)
            if m:
                a = max(0, m.start() - 20)
                b = min(len(text), m.end() + 60)
                class_clause = text[a:b].replace("\n", " ").strip()
            elif topics:
                class_clause = topics[0]["clause_quote"]
            else:
                class_clause = text[:200]
    else:
        content_class = "machinery_only"
        class_clause = text[:200] if text else "(empty)"
    # Override: if only revision/approval/custody/write_scope/reading topics
    # about how files govern each other without run gates — still protocol
    # if custody/approval create run-time stops.
    if any(t["topic"] in ("custody", "approval", "write_scope") for t in topics):
        if re.search(
            r"stop|refuse|mismatch|before any|not approved|authorizes nothing|"
            r"write_scope|hash_check",
            text,
            re.I,
        ):
            content_class = "protocol_content"
    return {
        "topics": topics,
        "content_class": content_class,
        "class_clause": class_clause,
        "classifying_rules": classifying_rules,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    docs, sha = load_all()
    bq0: list = []

    # BQ0: hash verification
    hash_report = []
    mismatch = False
    for rel, expected in EXPECTED_SHA.items():
        got = file_sha256(ROOT / rel)
        ok = got == expected
        hash_report.append(
            {"file": rel, "expected": expected, "got": got, "match": ok}
        )
        if not ok:
            mismatch = True
            bq0.append(
                {
                    "quote": f"sha256 mismatch for {rel}",
                    "admissible_readings": ["stop per blind-inputs"],
                    "depends": "all of BQ1–BQ3",
                    "implication_only": False,
                }
            )
    if mismatch:
        print("HASH MISMATCH — stopping", file=sys.stderr)
        (OUT / "computations.json").write_text(
            json.dumps({"bq0_hash": hash_report, "stopped": True}, indent=2)
        )
        return 2

    # Whether bands/d1d10 govern any leaf
    gn = docs["gated"]["amendment"]["governs_nothing"]
    bq0.append(
        {
            "quote": (
                "governs_nothing lists AMD-20260916-bands.yaml and "
                "AMD-20260923-d1d10.yaml; typed supersedes_fields last item "
                "also retires bands"
            ),
            "admissible_readings": [
                "neither file governs any leaf of the combined text (chosen)",
                "bands/d1d10 still supply provenance phrases for BQ1 only",
            ],
            "depends": (
                "BQ2 rows file:AMD-20260916-bands.yaml and "
                "file:AMD-20260923-d1d10.yaml; BQ1 still scans their strings"
            ),
            "implication_only": False,
            "chosen": (
                "they govern no run leaf; BQ1 still inventories phrases inside them"
            ),
        }
    )

    # External references pointed at by held texts (do not open)
    external_refs = []
    for fkey, fpath, doc in [
        ("typed", str(HELD["typed"]), docs["typed"]),
        ("narrow", str(HELD["narrow"]), docs["narrow"]),
        ("gated", str(HELD["gated"]), docs["gated"]),
        ("v1", str(HELD["v1"]), docs["v1"]),
    ]:
        for leaf_path, text in iter_string_leaves(doc):
            for m in PATH_PHRASE.finditer(text):
                p = m.group("phrase")
                held_names = {str(x).replace(str(ROOT) + "/", "") for x in HELD.values()}
                # normalize
                rel_held = {
                    "experiments/EXP-AUXIN-7e2e3d/specification.yaml",
                    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml",
                    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml",
                    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml",
                    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260916-bands.yaml",
                    "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260923-d1d10.yaml",
                }
                if p not in rel_held and not p.startswith("AMD-202609"):
                    # AMD-* without path may still be ids
                    if p.startswith("experiments/") or p.startswith("ledger/") or p.startswith("coordination/") or p.startswith("inputs/"):
                        external_refs.append(
                            {"from_file": fpath, "leaf": leaf_path, "ref": p}
                        )
    # Dedupe external refs
    seen_ext = set()
    ext_unique = []
    for e in external_refs:
        if e["ref"] in seen_ext:
            continue
        seen_ext.add(e["ref"])
        ext_unique.append(e)
    if ext_unique:
        bq0.append(
            {
                "quote": (
                    "held texts name paths outside the six held files; "
                    "per blind-inputs sources.note, do not open them"
                ),
                "admissible_readings": [
                    "record under BQ0 and continue with held files only (chosen)"
                ],
                "depends": "BQ1 referents for those path phrases",
                "implication_only": False,
                "chosen": "do not open; list refs",
                "external_refs_sample": ext_unique[:40],
                "external_refs_count": len(ext_unique),
            }
        )

    span_idx = build_span_rule_index(docs)
    table = docs["gated"]["amendment"]["governing_text_table"]

    # Choice: how additions combine — path_additions says UNION; table rows
    # remain separate leaves (addition rows are separate gated/narrow fields).
    bq0.append(
        {
            "quote": (
                "precedence: An ADDITION (an entry with adds_to) supersedes "
                "nothing: ... the text read at the path it names is the UNION "
                "of the held field's governing text and every addition"
            ),
            "admissible_readings": [
                (
                    "BQ2 hashes each table row's leaf separately; the union is "
                    "how a reader combines them at the named path, not a single "
                    "row effective text (chosen)"
                ),
                "concatenate union members into one effective text per path_additions path",
            ],
            "depends": "BQ2 sha256 for paths listed in path_additions",
            "implication_only": False,
            "chosen": "per-row leaf hash; union noted in clauses where relevant",
        }
    )

    bq0.append(
        {
            "quote": (
                "For v1 leaves with via 'typed-by-hash supersedes_fields … "
                "replaced by …': what is the effective text?"
            ),
            "admissible_readings": [
                "the named typed replacement object/value (chosen)",
                "the supersedes_fields clause string only",
                "empty / does-not-govern marker",
            ],
            "depends": "BQ2 effective text and sha256 for superseded v1 rows",
            "implication_only": False,
            "chosen": (
                "named typed replacement; retired/removed use clause string; "
                "meaning-fixed keeps v1 leaf"
            ),
        }
    )

    # Resolve all rows
    bq2_rows = []
    for i, row in enumerate(table):
        resolved = resolve_row(row, docs, span_idx, bq0)
        deps = find_dependences(resolved["effective_text"])
        resolved["held_file_dependence"] = deps
        # Note table layer vs determination
        if resolved["governing_file"] != LAYER_TO_FILE.get(row["layer"]):
            resolved["differs_from_table_layer_column"] = True
        else:
            resolved["differs_from_table_layer_column"] = False
        # For file: rows governing_file is None by design
        if row["field"].startswith("file:"):
            resolved["differs_from_table_layer_column"] = (
                "table layer names a layer but file governs nothing; "
                "reported governing_file=null"
            )
        bq2_rows.append(resolved)
        if (i + 1) % 200 == 0:
            print(f"resolved {i+1}/{len(table)}", file=sys.stderr)

    # BQ1
    bq1_occ, bq1_unfixed, bq1_rule = collect_bq1(docs)
    for u in bq1_unfixed:
        bq0.append(
            {
                "quote": (
                    f"BQ1 unfixed referent: {u['phrase']!r} in "
                    f"{u['file']} {u['field_path']} @{u['char_offset']}"
                ),
                "admissible_readings": [
                    "leave unfixed (chosen)",
                    "bind to nearest prior noun in the same leaf",
                ],
                "depends": "BQ1 referent field",
                "implication_only": True,
                "chosen": "leave unfixed",
            }
        )

    # BQ3
    bq3_rows = []
    classifying_rules = None
    for r in bq2_rows:
        c = classify_bq3(r["effective_text"])
        classifying_rules = c["classifying_rules"]
        bq3_rows.append(
            {
                "field": r["field"],
                "topics": c["topics"],
                "content_class": c["content_class"],
                "class_clause": c["class_clause"],
            }
        )

    # Leak check: allowed files should not contain precomputed BQ answers
    leak = False
    leak_notes = []
    for label, doc in docs.items():
        blob = json.dumps(doc)
        for token in (
            "BQ1",
            "BQ2",
            "BQ3",
            "self-referential phrase inventory",
            "held-file dependence per table row",
        ):
            # BQ0 is defined in blind-inputs which we must read; skip blind-inputs
            pass
    # Check gated/typed/narrow for keys that look like answers
    for label in ("typed", "narrow", "gated", "v1", "bands", "d1d10"):
        text = HELD[label].read_text()
        if "char_offset" in text and "self-referential" in text.lower():
            leak = True
            leak_notes.append(label)

    computations = {
        "task_id": "TASK-20260929-7109a0",
        "libraries": {
            "python": sys.version,
            "PyYAML": yaml.__version__,
            "hashlib": "stdlib sha256",
            "json": "stdlib (sort_keys, ensure_ascii=False, separators=(',',':'))",
        },
        "commands": [
            "python3 derive_bq.py  # this script, from write_scope",
        ],
        "bq0_hash_verification": hash_report,
        "bq0_undetermined_choices": bq0,
        "leak_check": {"leak_detected": leak, "notes": leak_notes},
        "bq1": {
            "matching_rule": bq1_rule,
            "occurrence_count": len(bq1_occ),
            "occurrences": bq1_occ,
            "unfixed_referents": bq1_unfixed,
        },
        "bq2": {
            "row_count": len(bq2_rows),
            "rows": bq2_rows,
        },
        "bq3": {
            "classifying_rules": classifying_rules,
            "row_count": len(bq3_rows),
            "rows": bq3_rows,
        },
    }

    out_json = OUT / "computations.json"
    out_json.write_text(
        json.dumps(computations, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {out_json} "
        f"BQ1={len(bq1_occ)} BQ2={len(bq2_rows)} BQ0={len(bq0)}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
