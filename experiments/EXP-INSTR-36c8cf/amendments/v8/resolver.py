#!/usr/bin/env python3
"""Deterministic resolver for the EXP-INSTR-36c8cf version-8 composition.

This program performs protocol conformance only.  It never runs the harness,
authorizes a run, changes research state, or interprets scientific evidence.
The two entry strategies deliberately resolve the same explicit manifest and
must produce byte-identical canonical JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml


EXPERIMENT_ID = "EXP-INSTR-36c8cf"
VERSION = 8
DEFAULT_INPUT = "experiments/EXP-INSTR-36c8cf/amendments/v8/resolution-input.json"
DEFAULT_RESOLVED = "experiments/EXP-INSTR-36c8cf/amendments/v8/resolved-contract.json"
DEFAULT_ORIGIN = "experiments/EXP-INSTR-36c8cf/amendments/v8/origin-trace.json"

EXPECTED_ARTIFACTS = {
    DEFAULT_INPUT: {
        "size_bytes": 379916,
        "sha256": "ae020d74ca2cc87599b72cdc386797fcecf0974898900892885da8f22ad14b0c",
    },
    DEFAULT_RESOLVED: {
        "size_bytes": 516821,
        "sha256": "018aa4f9b0420dd985911c3fd059bcf32362b96ca0ffeacfac6a8c51673edd22",
    },
    DEFAULT_ORIGIN: {
        "size_bytes": 1199973,
        "sha256": "75d9ad35de729fff95b9aaf80723c461150dc0511fb04592f9648023831719a4",
    },
}

EXPECTED_SOURCE_IDS = [
    "specification",
    "amendment_v1",
    "amendment_v4",
    "amendment_v5",
    "amendment_v6",
    "amendment_v7",
]

EXPECTED_VERSION_CHAIN = {
    "specification": ("experiment", 1),
    "amendment_v1": ("protocol_amendment", 1, 1, 2),
    "amendment_v4": ("protocol_amendment", 4, 3, 4),
    "amendment_v5": ("protocol_amendment", 5, 4, 5),
    "amendment_v6": ("protocol_amendment", 6, 5, 6),
    "amendment_v7": ("protocol_amendment", 7, 6, 7),
}

EXPECTED_ERROR_CODES = [
    "EXCLUDED_FINGERPRINT",
    "DUPLICATE_KEY",
    "MISSING_SOURCE",
    "UNEXPECTED_SOURCE",
    "SOURCE_ORDER",
    "SOURCE_SIZE",
    "SOURCE_SHA256",
    "VERSION_CHAIN",
    "CUSTODY_ABSENT",
    "CUSTODY_DISAGREEMENT",
    "PATH_DISPOSITION_MISSING",
    "PATH_DISPOSITION_DUPLICATE",
    "OWNERLESS_FIELD",
    "DUAL_OWNER_FIELD",
    "OVERRIDE_POINTER_MISSING",
    "OVERRIDE_OWNER_MISMATCH",
    "DUPLICATE_SEMANTIC_SUBJECT",
    "OVERRIDE_OUT_OF_SCOPE",
    "UNRESOLVED_CONTRADICTION",
    "TYPE_COERCION",
    "GENERIC_MERGE",
    "RNG_FIXTURE_DRIFT",
    "AUTHORITY_NONZERO",
    "ECOMP_LATEST_ONLY",
    "OUTPUT_MISMATCH",
]

EXPECTED_EDGE_IDS = (
    [f"OVR-V1-{i:03d}" for i in range(1, 13)]
    + [f"OVR-V5-{i:03d}" for i in range(1, 10)]
    + [f"OVR-V6-{i:03d}" for i in range(1, 21)]
    + [f"OVR-V8-{i:03d}" for i in range(1, 11)]
)

EXPECTED_V8_SUCCESSOR_POINTERS = {
    "OVR-V8-001": "/composition/ordered_sources",
    "OVR-V8-002": "/composition/source_leaf_disposition",
    "OVR-V8-003": "/composition/allowed_overrides",
    "OVR-V8-004": "/composition/resolver_contract",
    "OVR-V8-005": "/composition/static_conformance_fixtures",
    "OVR-V8-006": "/preservation/v6_RNG",
    "OVR-V8-007": "/composition/error_priority",
    "OVR-V8-008": "/authority",
    "OVR-V8-009": "/composition/quarantined_fingerprints",
    "OVR-V8-010": "/composition/controlling_v7_disposition",
}

# Historical non-executable fingerprints are frozen in v7.  The final two
# entries are the two distinct post-snapshot mutations added to v8's
# quarantine.  Fingerprint rejection precedes all ordinary manifest checks.
HISTORICAL_EXCLUDED_SHA256 = {
    "582f3638965b33f04751fc91577339fa97de2a010069c776e010d30f98d86be4",
    "0926a2f84d4959029a9ed61ad20e744d093b7664853cc628053449b22d03b876",
    "03b06727cf2c5db69b8068d796250026e8f36e97490a001c9d4454938591a560",
    "8d4fbc76d15040de9be73ce52a1d49d28380a443992768035da0843418d96353",
    "0b9ac9290c9d793d26383c7cf8fa857b8548abab7039f2e120c0bf872492747e",
    "44a217ffddfa4a7f60f377b54fcc3eb4043efef79c905cde8ac8755f5b17396f",
    "58e3c2b0d78bd95e4c7a76e67b0175aff70c651ccc523f7a2895bbbae93152cc",
}

EXPECTED_AUTHORITY = {
    "amendment_approved": False,
    "approved_by": None,
    "breakthrough_claim": False,
    "ecdlp_attack_or_speedup_claim": False,
    "evidence_status_transition": "none",
    "execution_authorized": False,
    "experiment_runs_authorized": 0,
    "experiment_status_transition": "none",
    "goal_status_transition": "none",
    "harness_work_authorized": False,
    "hypothesis_status_transition": "none",
    "jinv_work_authorized": False,
    "knowledge_status_transition": "none",
    "phase_b_authorized": False,
    "phase_b_defined": False,
    "rerun_authorized": False,
    "run_records_created": 0,
    "scientific_interpretation": "none",
    "source_status_transition": "none",
}

EXPECTED_RESOLVER_CONTRACT = {
    "all_conflicts_fail_before_measurement": True,
    "canonical_output_framing": "v8_owned_sorted_compact_UTF8_JSON_exactly_one_terminal_LF",
    "duplicate_semantic_subjects": "prohibited",
    "frozen_legacy_v7_null_key_normalization": "exact_null_tag_and_null_lexeme_to_string_null_only",
    "generic_deep_merge": "prohibited",
    "integer_float_coercion": "prohibited",
    "latest_entry_requires_manifest_resolution": True,
    "last_write_wins": "prohibited",
    "missing_or_dual_disposition": "prohibited",
    "prose_inheritance": "prohibited",
    "strategy_convergence": "byte_identical",
    "v7_no_trailing_line_feed_rule": "superseded_for_v8_artifacts",
}


class ResolverFailure(Exception):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def fail(code: str, detail: str) -> None:
    raise ResolverFailure(code, detail)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        fail("TYPE_COERCION", f"non-canonical JSON value: {exc}")
    return text.encode("utf-8") + b"\n"


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("DUPLICATE_KEY", f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def load_json_bytes(raw: bytes, label: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=strict_pairs)
    except ResolverFailure:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail("DUPLICATE_KEY", f"strict JSON parse failed for {label}: {exc}")


class StrictLoader(yaml.SafeLoader):
    pass


# Dates are contract strings.  Copy the resolver table before removing the
# timestamp resolver so the process-wide SafeLoader is not mutated.
StrictLoader.yaml_implicit_resolvers = {
    key: [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def construct_mapping(loader: StrictLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, Any]:
    loader.flatten_mapping(node)
    result: dict[str, Any] = {}
    for key_node, value_node in node.value:
        if (
            getattr(loader, "allow_frozen_v7_null_key", False)
            and isinstance(key_node, yaml.ScalarNode)
            and key_node.tag == "tag:yaml.org,2002:null"
            and key_node.value == "null"
        ):
            # Snapshot-bound v7 contains exactly one unquoted `null: null`
            # type-tag entry.  Its intended RFC6901 token is the string
            # `null`.  This one lexeme/tag/source exception is frozen; no
            # arbitrary non-string key is ever stringified.
            key = "null"
        else:
            key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            fail("TYPE_COERCION", f"non-string YAML mapping key {key!r}")
        if key in result:
            fail("DUPLICATE_KEY", f"duplicate YAML key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_mapping,
)


def load_yaml_bytes(raw: bytes, label: str) -> Any:
    try:
        loader = StrictLoader(raw.decode("utf-8"))
        loader.allow_frozen_v7_null_key = label.endswith(
            "experiments/EXP-INSTR-36c8cf/amendments/v7.yaml"
        )
        try:
            value = loader.get_single_data()
        finally:
            loader.dispose()
    except ResolverFailure:
        raise
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        fail("DUPLICATE_KEY", f"strict YAML parse failed for {label}: {exc}")
    if not isinstance(value, dict):
        fail("TYPE_COERCION", f"top-level YAML value for {label} is not a mapping")
    return value


def repository_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or relative.startswith("/"):
        fail("UNEXPECTED_SOURCE", f"invalid repository-relative path {relative!r}")
    target = (root / relative).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        fail("UNEXPECTED_SOURCE", f"path escapes repository root: {relative!r}")
    return target


def escape_pointer_token(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")


def unescape_pointer_token(token: str) -> str:
    result = token.replace("~1", "/").replace("~0", "~")
    if escape_pointer_token(result) != token:
        fail("OVERRIDE_POINTER_MISSING", f"non-canonical RFC6901 token {token!r}")
    return result


def iter_leaves(value: Any, pointer: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key in sorted(value, key=lambda item: item.encode("utf-8")):
            if not isinstance(key, str):
                fail("TYPE_COERCION", f"non-string mapping key at {pointer or '/'}")
            yield from iter_leaves(value[key], pointer + "/" + escape_pointer_token(key))
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            yield from iter_leaves(item, pointer + "/" + str(index))
        return
    if value is None or isinstance(value, (str, bool, int, float)):
        if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
            fail("TYPE_COERCION", f"non-finite scalar at {pointer}")
        yield pointer, value
        return
    fail("TYPE_COERCION", f"unsupported scalar type at {pointer}: {type(value).__name__}")


def pointer_get(value: Any, pointer: str) -> Any:
    if pointer == "":
        return value
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        fail("OVERRIDE_POINTER_MISSING", f"invalid RFC6901 pointer {pointer!r}")
    current = value
    for raw_token in pointer[1:].split("/"):
        token = unescape_pointer_token(raw_token)
        if isinstance(current, dict):
            if token not in current:
                raise KeyError(pointer)
            current = current[token]
        elif isinstance(current, list):
            if token == "-" or not token.isdigit() or (len(token) > 1 and token.startswith("0")):
                raise KeyError(pointer)
            index = int(token)
            if index >= len(current):
                raise KeyError(pointer)
            current = current[index]
        else:
            raise KeyError(pointer)
    return current


def pointer_covers(root_pointer: str, leaf_pointer: str) -> bool:
    return leaf_pointer == root_pointer or leaf_pointer.startswith(root_pointer + "/")


def value_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    fail("TYPE_COERCION", f"unsupported resolved value type {type(value).__name__}")
    raise AssertionError


def verify_version_chain(source_id: str, document: dict[str, Any]) -> None:
    expected = EXPECTED_VERSION_CHAIN[source_id]
    if source_id == "specification":
        section = document.get("experiment")
        observed = ("experiment", section.get("version") if isinstance(section, dict) else None)
    else:
        section = document.get("protocol_amendment")
        observed = (
            "protocol_amendment",
            section.get("amendment_ordinal") if isinstance(section, dict) else None,
            section.get("version_from") if isinstance(section, dict) else None,
            section.get("version_to") if isinstance(section, dict) else None,
        )
    if observed != expected:
        fail("VERSION_CHAIN", f"{source_id}: expected {expected!r}, observed {observed!r}")


def load_and_verify_sources(root: Path, composition: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    manifest = composition.get("ordered_sources")
    if not isinstance(manifest, list):
        fail("UNEXPECTED_SOURCE", "ordered_sources is not a sequence")

    exclusions = set(HISTORICAL_EXCLUDED_SHA256)
    quarantines = composition.get("quarantined_fingerprints")
    if not isinstance(quarantines, list):
        fail("UNEXPECTED_SOURCE", "quarantined_fingerprints is not a sequence")
    for item in quarantines:
        if isinstance(item, dict) and isinstance(item.get("sha256"), str):
            exclusions.add(item["sha256"])

    raw_by_index: list[bytes | None] = []
    path_by_index: list[Path | None] = []
    for index, item in enumerate(manifest):
        if not isinstance(item, dict):
            fail("UNEXPECTED_SOURCE", f"manifest entry {index} is not a mapping")
        path = repository_path(root, item.get("path"))
        path_by_index.append(path)
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            raw_by_index.append(None)
            continue
        digest = sha256(raw)
        if digest in exclusions:
            fail("EXCLUDED_FINGERPRINT", f"manifest entry {index} matches excluded sha256 {digest}")
        raw_by_index.append(raw)

    # Duplicate-key failures have priority over missing/order/hash failures for
    # every candidate byte stream that is present.
    parsed_by_index: list[dict[str, Any] | None] = []
    for index, raw in enumerate(raw_by_index):
        if raw is None:
            parsed_by_index.append(None)
        else:
            parsed_by_index.append(load_yaml_bytes(raw, str(path_by_index[index])))

    missing_expected = []
    manifest_ids = [item.get("source_id") if isinstance(item, dict) else None for item in manifest]
    for source_id in EXPECTED_SOURCE_IDS:
        if source_id not in manifest_ids:
            missing_expected.append(source_id)
    for index, raw in enumerate(raw_by_index):
        if raw is None and manifest_ids[index] in EXPECTED_SOURCE_IDS:
            missing_expected.append(str(manifest_ids[index]))
    if missing_expected:
        fail("MISSING_SOURCE", "missing required source(s): " + ",".join(sorted(set(missing_expected))))

    unexpected = [source_id for source_id in manifest_ids if source_id not in EXPECTED_SOURCE_IDS]
    if unexpected or len(manifest) != len(EXPECTED_SOURCE_IDS):
        fail("UNEXPECTED_SOURCE", f"unexpected manifest sources: {unexpected!r}")
    if manifest_ids != EXPECTED_SOURCE_IDS:
        fail("SOURCE_ORDER", f"expected {EXPECTED_SOURCE_IDS!r}, observed {manifest_ids!r}")
    if [item.get("order_index") for item in manifest] != list(range(len(EXPECTED_SOURCE_IDS))):
        fail("SOURCE_ORDER", "order_index does not match the explicit source order")

    documents: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(manifest):
        raw = raw_by_index[index]
        document = parsed_by_index[index]
        assert raw is not None and document is not None
        if len(raw) != item.get("size_bytes"):
            fail("SOURCE_SIZE", f"{item['source_id']}: expected {item.get('size_bytes')}, observed {len(raw)}")
        digest = sha256(raw)
        if digest != item.get("sha256"):
            fail("SOURCE_SHA256", f"{item['source_id']}: expected {item.get('sha256')}, observed {digest}")
        verify_version_chain(item["source_id"], document)
        documents[item["source_id"]] = document
    return manifest, documents


def verify_dispositions(
    composition: dict[str, Any],
    manifest: list[dict[str, Any]],
    documents: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[tuple[str, str], str], dict[str, list[tuple[str, Any]]]]:
    rows = composition.get("source_leaf_disposition")
    if not isinstance(rows, list):
        fail("PATH_DISPOSITION_MISSING", "source_leaf_disposition is not a sequence")

    leaves_by_source = {source_id: list(iter_leaves(documents[source_id])) for source_id in EXPECTED_SOURCE_IDS}
    observed: dict[tuple[str, str], str] = {}
    duplicate_keys: list[tuple[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            fail("OWNERLESS_FIELD", "disposition row is not a mapping")
        key = (row.get("source_id"), row.get("source_pointer"))
        if key in observed:
            duplicate_keys.append(key)
            continue
        disposition = row.get("disposition")
        if disposition not in {"executable-owned", "excluded-provenance", "common-metadata"}:
            fail("OWNERLESS_FIELD", f"invalid disposition {disposition!r} at {key!r}")
        observed[key] = disposition

    expected_keys = {
        (source_id, pointer)
        for source_id in EXPECTED_SOURCE_IDS
        for pointer, _value in leaves_by_source[source_id]
    }
    observed_keys = set(observed)
    missing = expected_keys - observed_keys
    if missing:
        fail("PATH_DISPOSITION_MISSING", f"first missing disposition {min(missing)!r}")
    if duplicate_keys:
        fail("PATH_DISPOSITION_DUPLICATE", f"first duplicate disposition row {min(duplicate_keys)!r}")
    extras = observed_keys - expected_keys
    if extras:
        fail("OWNERLESS_FIELD", f"first disposition without a source leaf {min(extras)!r}")

    expected_order = [
        (source_id, pointer)
        for source_id in EXPECTED_SOURCE_IDS
        for pointer, _value in sorted(leaves_by_source[source_id], key=lambda pair: pair[0].encode("utf-8"))
    ]
    row_order = [(row["source_id"], row["source_pointer"]) for row in rows]
    if row_order != expected_order:
        fail("PATH_DISPOSITION_DUPLICATE", "disposition rows are not in canonical source/pointer order")

    computed_by_source: dict[str, dict[str, int]] = {}
    totals = {
        "parsed_source_leaves": 0,
        "executable-owned": 0,
        "common-metadata": 0,
        "excluded-provenance": 0,
    }
    for item in manifest:
        source_id = item["source_id"]
        counts = {
            "total": len(leaves_by_source[source_id]),
            "executable-owned": 0,
            "common-metadata": 0,
            "excluded-provenance": 0,
        }
        for pointer, _value in leaves_by_source[source_id]:
            counts[observed[(source_id, pointer)]] += 1
        computed_by_source[source_id] = counts
        totals["parsed_source_leaves"] += counts["total"]
        for name in ("executable-owned", "common-metadata", "excluded-provenance"):
            totals[name] += counts[name]
    summary = composition.get("classification_summary")
    if summary != {"by_source": computed_by_source, "totals": totals}:
        fail("DUAL_OWNER_FIELD", "classification summary disagrees with exhaustive literal rows")
    return rows, observed, leaves_by_source


def verify_edges(
    composition: dict[str, Any],
    input_object: dict[str, Any],
    documents: dict[str, dict[str, Any]],
    dispositions: dict[tuple[str, str], str],
) -> list[dict[str, Any]]:
    edges = composition.get("allowed_overrides")
    if not isinstance(edges, list):
        fail("UNRESOLVED_CONTRADICTION", "allowed_overrides is not a sequence")
    edge_ids = [edge.get("edge_id") if isinstance(edge, dict) else None for edge in edges]
    if edge_ids != EXPECTED_EDGE_IDS:
        fail("UNRESOLVED_CONTRADICTION", f"expected exact 51-edge identifier sequence, observed {edge_ids!r}")

    owner_documents = dict(documents)
    owner_documents["amendment_v8"] = input_object

    # Pointer absence has priority over owner mismatch across the complete
    # graph, so collect both classes before failing.
    missing_pointers: list[str] = []
    owner_mismatches: list[str] = []
    for edge in edges:
        for side in ("predecessor", "successor"):
            owner = edge.get(f"{side}_owner")
            pointer = edge.get(f"{side}_pointer")
            if owner not in owner_documents:
                owner_mismatches.append(f"{edge.get('edge_id')}: unknown {side} owner {owner!r}")
                continue
            try:
                pointer_get(owner_documents[owner], pointer)
            except (KeyError, TypeError):
                exists_elsewhere = False
                for other_owner, other_document in owner_documents.items():
                    if other_owner == owner:
                        continue
                    try:
                        pointer_get(other_document, pointer)
                    except (KeyError, ResolverFailure, TypeError):
                        continue
                    exists_elsewhere = True
                    break
                if exists_elsewhere:
                    owner_mismatches.append(f"{edge.get('edge_id')}: {side} pointer belongs to another owner")
                else:
                    missing_pointers.append(f"{edge.get('edge_id')}: missing {side} pointer {pointer!r}")
    if missing_pointers:
        fail("OVERRIDE_POINTER_MISSING", sorted(missing_pointers)[0])
    if owner_mismatches:
        fail("OVERRIDE_OWNER_MISMATCH", sorted(owner_mismatches)[0])

    subjects = [edge.get("semantic_subject") for edge in edges]
    if len(set(subjects)) != len(subjects) or any(not isinstance(subject, str) or not subject for subject in subjects):
        fail("DUPLICATE_SEMANTIC_SUBJECT", "semantic subjects must be non-empty and unique")

    for edge in edges:
        for side in ("predecessor", "successor"):
            owner = edge[f"{side}_owner"]
            pointer = edge[f"{side}_pointer"]
            if owner == "amendment_v8":
                if (
                    side != "successor"
                    or EXPECTED_V8_SUCCESSOR_POINTERS.get(edge["edge_id"]) != pointer
                ):
                    fail("OVERRIDE_OUT_OF_SCOPE", f"{edge['edge_id']}: invalid v8 synthetic scope")
                continue
            covered = [
                disposition
                for (source_id, leaf_pointer), disposition in dispositions.items()
                if source_id == owner and pointer_covers(pointer, leaf_pointer)
            ]
            accepted = (
                {"executable-owned", "excluded-provenance"}
                if side == "predecessor"
                else {"executable-owned"}
            )
            if not covered or any(disposition not in accepted for disposition in covered):
                fail("OVERRIDE_OUT_OF_SCOPE", f"{edge['edge_id']}: {side} scope has a prohibited disposition")
    return edges


def verify_preservation(input_object: dict[str, Any], documents: dict[str, dict[str, Any]]) -> None:
    preservation = input_object.get("preservation")
    if not isinstance(preservation, dict):
        fail("RNG_FIXTURE_DRIFT", "preservation contract missing")
    v5 = documents["amendment_v5"]
    v6 = documents["amendment_v6"]

    for source_key, contract_key in (("amendment_v5", "v5"), ("amendment_v6", "v6_RNG")):
        document = documents[source_key]
        contract = preservation[contract_key]
        for subtree in contract["subtrees"]:
            try:
                value = pointer_get(document, subtree["pointer"])
            except KeyError:
                fail("RNG_FIXTURE_DRIFT", f"missing preserved subtree {subtree['pointer']}")
            count = sum(1 for _ in iter_leaves(value))
            if count != subtree["leaf_count"]:
                fail("RNG_FIXTURE_DRIFT", f"leaf count drift at {subtree['pointer']}: {count}")

    standing = preservation["standing_sampler"]
    scalar = pointer_get(v5, standing["source_pointer"])
    if not isinstance(scalar, str):
        fail("RNG_FIXTURE_DRIFT", "standing sampler custody value is not a string")
    scalar_bytes = scalar.encode("utf-8")
    if len(scalar_bytes) != standing["scalar_size_bytes"] or sha256(scalar_bytes) != standing["scalar_sha256"]:
        fail("RNG_FIXTURE_DRIFT", "standing sampler scalar digest/size drift")

    legacy = preservation["v5"]["legacy_seeded_fresh_null"]
    legacy_checks = {
        "/protocol_amendment/deterministic_conformance_fixture/seeded_fresh_null/seed_label_sha256": legacy["seed_label_sha256"],
        "/protocol_amendment/deterministic_conformance_fixture/seeded_fresh_null/raw_8_by_5_little_endian_binary64_SHA256": legacy["raw_buffer_sha256"],
    }
    if legacy.get("production_RNG_authority") is not False:
        fail("RNG_FIXTURE_DRIFT", "legacy v5 fixture gained production RNG authority")
    for pointer, expected in legacy_checks.items():
        if pointer_get(v5, pointer) != expected:
            fail("RNG_FIXTURE_DRIFT", f"legacy v5 fixture drift at {pointer}")

    rng = preservation["v6_RNG"]
    rng_checks = {
        "/protocol_amendment/seeded_conformance_fixtures/D2/label_sha256": rng["D2"]["label_sha256"],
        "/protocol_amendment/seeded_conformance_fixtures/D2/normalized_raw_buffer_sha256": rng["D2"]["normalized_raw_buffer_sha256"],
        "/protocol_amendment/seeded_conformance_fixtures/D2/canonical_output_sha256": rng["D2"]["canonical_output_sha256"],
        "/protocol_amendment/seeded_conformance_fixtures/D5/label_sha256": rng["D5"]["label_sha256"],
        "/protocol_amendment/seeded_conformance_fixtures/D5/normalized_raw_buffer_sha256": rng["D5"]["normalized_raw_buffer_sha256"],
        "/protocol_amendment/seeded_conformance_fixtures/D5/canonical_output_sha256": rng["D5"]["canonical_output_sha256"],
        "/protocol_amendment/seeded_conformance_fixtures/D6/input_matrix/normalized_raw_buffer_sha256": rng["D6"]["input_normalized_raw_buffer_sha256"],
        "/protocol_amendment/seeded_conformance_fixtures/D6/label_sha256": rng["D6"]["label_sha256"],
        "/protocol_amendment/seeded_conformance_fixtures/D6/normalized_raw_index_buffer_sha256": rng["D6"]["normalized_raw_index_buffer_sha256"],
        "/protocol_amendment/seeded_conformance_fixtures/D6/canonical_output_sha256": rng["D6"]["canonical_output_sha256"],
        "/protocol_amendment/seeded_conformance_fixtures/D6/forced_zero_scale_branch/canonical_output_sha256": rng["D6"]["forced_zero_scale_canonical_output_sha256"],
    }
    for pointer, expected in rng_checks.items():
        if pointer_get(v6, pointer) != expected:
            fail("RNG_FIXTURE_DRIFT", f"v6 RNG fixture drift at {pointer}")

    fixture = input_object["composition"]["five_prior_source_manifest_fixture"]
    preimage = fixture.get("exact_preimage")
    if not isinstance(preimage, str):
        fail("RNG_FIXTURE_DRIFT", "five-prior manifest exact preimage missing")
    preimage_bytes = preimage.encode("utf-8")
    if len(preimage_bytes) != fixture.get("byte_length") or sha256(preimage_bytes) != fixture.get("sha256"):
        fail("RNG_FIXTURE_DRIFT", "five-prior manifest exact preimage digest/size drift")


def role_for(pointer: str, predecessor_edges: list[dict[str, Any]], successor_edges: list[dict[str, Any]]) -> str:
    is_predecessor = bool(predecessor_edges)
    is_successor = bool(successor_edges)
    if is_predecessor and is_successor:
        return "override-successor-and-predecessor"
    if is_predecessor:
        return "override-predecessor"
    if is_successor:
        return "active-override-successor"
    return "active"


def derive(
    input_object: dict[str, Any],
    input_path: str,
    input_raw: bytes,
    manifest: list[dict[str, Any]],
    documents: dict[str, dict[str, Any]],
    disposition_rows: list[dict[str, Any]],
    dispositions: dict[tuple[str, str], str],
    leaves_by_source: dict[str, list[tuple[str, Any]]],
    edges: list[dict[str, Any]],
    strategy: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if strategy not in {"latest_entry", "ordered_entry"}:
        fail("ECOMP_LATEST_ONLY", f"unsupported entry strategy {strategy!r}")

    manifest_by_id = {item["source_id"]: item for item in manifest}
    source_fields: dict[str, Any] = {}
    origin_rows: list[dict[str, Any]] = []
    for source_id in EXPECTED_SOURCE_IDS:
        for pointer, value in leaves_by_source[source_id]:
            if dispositions[(source_id, pointer)] != "executable-owned":
                continue
            predecessor_edges = [
                edge
                for edge in edges
                if edge["predecessor_owner"] == source_id
                and pointer_covers(edge["predecessor_pointer"], pointer)
            ]
            successor_edges = [
                edge
                for edge in edges
                if edge["successor_owner"] == source_id
                and pointer_covers(edge["successor_pointer"], pointer)
            ]
            role = role_for(pointer, predecessor_edges, successor_edges)
            resolved_path = f"/sources/{source_id}{pointer}"
            scalar_type = value_type(value)
            source_fields[resolved_path] = {
                "authority_role": role,
                "source_id": source_id,
                "source_pointer": pointer,
                "value": value,
                "value_type": scalar_type,
            }
            origin_rows.append(
                {
                    "authority_role": role,
                    "disposition": "executable-owned",
                    "overridden_by": [
                        {
                            "edge_id": edge["edge_id"],
                            "semantic_subject": edge["semantic_subject"],
                            "successor_owner": edge["successor_owner"],
                            "successor_pointer": edge["successor_pointer"],
                        }
                        for edge in predecessor_edges
                    ],
                    "override_predecessors": [
                        {
                            "edge_id": edge["edge_id"],
                            "predecessor_owner": edge["predecessor_owner"],
                            "predecessor_pointer": edge["predecessor_pointer"],
                            "semantic_subject": edge["semantic_subject"],
                        }
                        for edge in successor_edges
                    ],
                    "owner_source_id": source_id,
                    "owner_source_sha256": manifest_by_id[source_id]["sha256"],
                    "resolved_field_path": resolved_path,
                    "source_pointer": pointer,
                    "value": value,
                    "value_type": scalar_type,
                }
            )

    origin_rows.sort(key=lambda row: row["resolved_field_path"].encode("utf-8"))
    input_binding = {
        "path": input_path,
        "sha256": sha256(input_raw),
        "size_bytes": len(input_raw),
    }
    composition = input_object["composition"]
    semantic_winners = [
        {
            "edge_id": edge["edge_id"],
            "semantic_subject": edge["semantic_subject"],
            "winner_owner": edge["successor_owner"],
            "winner_pointer": edge["successor_pointer"],
        }
        for edge in edges
    ]
    resolved = {
        "schema": "crypto.autoresearch.resolved_contract.v8",
        "experiment_id": EXPERIMENT_ID,
        "version": VERSION,
        "resolution_input": input_binding,
        "composition": {
            "allowed_overrides": composition["allowed_overrides"],
            "canonical_framing": composition["canonical_framing"],
            "classification_summary": composition["classification_summary"],
            "controlling_v7_disposition": composition["controlling_v7_disposition"],
            "error_priority": composition["error_priority"],
            "ordered_sources": composition["ordered_sources"],
            "quarantined_fingerprints": composition["quarantined_fingerprints"],
            "resolver_contract": composition["resolver_contract"],
            "snapshot_custody": composition["snapshot_custody"],
            "source_field_count": len(source_fields),
            "static_conformance_fixtures": composition["static_conformance_fixtures"],
            "semantic_winners": semantic_winners,
        },
        "preservation": input_object["preservation"],
        "authority": input_object["authority"],
        "source_fields": source_fields,
    }
    composition_origin_rows = [
        {
            "authority_role": "active-override-successor",
            "edge_id": edge["edge_id"],
            "owner_source_id": "amendment_v8",
            "override_predecessor_owner": edge["predecessor_owner"],
            "override_predecessor_pointer": edge["predecessor_pointer"],
            "resolved_field_path": edge["successor_pointer"],
            "semantic_subject": edge["semantic_subject"],
        }
        for edge in edges
        if edge["successor_owner"] == "amendment_v8"
    ]
    origin = {
        "schema": "crypto.autoresearch.origin_trace.v8",
        "experiment_id": EXPERIMENT_ID,
        "version": VERSION,
        "resolution_input": input_binding,
        "classification_summary": composition["classification_summary"],
        "source_leaf_disposition": disposition_rows,
        "exact_overrides": composition["allowed_overrides"],
        "composition_origin_rows": composition_origin_rows,
        "row_order": "ascending_UTF8_resolved_field_path",
        "rows": origin_rows,
    }
    return resolved, origin


def verify_static_contract(input_object: dict[str, Any], phase: str) -> None:
    composition = input_object.get("composition")
    if not isinstance(composition, dict):
        fail("UNRESOLVED_CONTRADICTION", "composition is not a mapping")
    if phase == "version":
        if input_object.get("experiment_id") == EXPERIMENT_ID and input_object.get("version") == VERSION:
            return
        fail("VERSION_CHAIN", "resolution input experiment/version mismatch")
    if phase == "conflict":
        error_priority = composition.get("error_priority")
        expected_priority = [
            {"code": code, "priority": index}
            for index, code in enumerate(EXPECTED_ERROR_CODES, start=1)
        ]
        if error_priority != expected_priority:
            fail("UNRESOLVED_CONTRADICTION", "error-priority table is not the frozen total order")
        fixtures = composition.get("static_conformance_fixtures")
        positive = fixtures.get("positive") if isinstance(fixtures, dict) else None
        if positive != {
            "expected_executable_leaf_count": 1363,
            "expected_origin_row_count": 1363,
            "expected_override_count": 51,
            "strategies": ["latest_entry", "ordered_entry"],
        }:
            fail("UNRESOLVED_CONTRADICTION", "positive conformance fixture counts drift")
        return
    if phase == "merge":
        if composition.get("resolver_contract") != EXPECTED_RESOLVER_CONTRACT:
            fail("GENERIC_MERGE", "resolver contract permits an inexact composition mechanism")
        return
    if phase == "authority":
        fixtures = composition.get("static_conformance_fixtures")
        if input_object.get("authority") != EXPECTED_AUTHORITY:
            fail("AUTHORITY_NONZERO", "v8 authority boundary is not exactly zero")
        if not isinstance(fixtures, dict) or fixtures.get("experiment_runs_consumed") != 0:
            fail("AUTHORITY_NONZERO", "protocol fixture consumed an experiment run")
        return
    if phase == "entry":
        fixtures = composition.get("static_conformance_fixtures")
        positive = fixtures.get("positive") if isinstance(fixtures, dict) else None
        if composition.get("entry_strategies") != ["latest_entry", "ordered_entry"]:
            fail("ECOMP_LATEST_ONLY", "both entry strategies are mandatory")
        if not isinstance(positive, dict) or positive.get("strategies") != ["latest_entry", "ordered_entry"]:
            fail("ECOMP_LATEST_ONLY", "positive fixture does not require both strategies")
        return
    if phase == "output":
        if input_object.get("schema") != "crypto.autoresearch.resolution_input.v8":
            fail("OUTPUT_MISMATCH", "unexpected resolution-input schema")
        canonical = composition.get("canonical_framing")
        if canonical != {
            "encoding": "UTF-8",
            "frozen_legacy_yaml_key_normalization": {
                "accepted_key_lexeme": "null",
                "accepted_key_tag": "tag:yaml.org,2002:null",
                "all_other_non_string_mapping_keys": "TYPE_COERCION",
                "normalized_key": "null",
                "scope": "snapshot_bound_amendment_v7_only",
            },
            "json": "sorted_keys_compact_ensure_ascii_false_allow_nan_false",
            "terminal_line_feed": "exactly_one",
        }:
            fail("OUTPUT_MISMATCH", "canonical framing contract drift")
        return
    raise AssertionError(f"unknown static verification phase: {phase}")


def find_task_record(value: Any, task_id: str) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if value.get("task_id") == task_id or value.get("id") == task_id:
            return value
        for child in value.values():
            found = find_task_record(child, task_id)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_task_record(child, task_id)
            if found is not None:
                return found
    return None


def find_plan_archive(value: Any, task_id: str) -> dict[str, Any] | None:
    if isinstance(value, dict):
        archives = value.get("content_only_archives")
        if isinstance(archives, dict):
            candidate = archives.get(task_id)
            if isinstance(candidate, dict):
                return candidate
        if isinstance(archives, list):
            for candidate in archives:
                if isinstance(candidate, dict) and (
                    candidate.get("task_id") == task_id
                    or candidate.get("id") == task_id
                    or candidate.get("archive_task_id") == task_id
                ):
                    return candidate
        for child in value.values():
            found = find_plan_archive(child, task_id)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_plan_archive(child, task_id)
            if found is not None:
                return found
    return None


def verify_snapshot_custody(root: Path, input_object: dict[str, Any], plan_argument: str | None) -> None:
    contract = input_object["composition"]["snapshot_custody"]
    task_id = contract["archive_task_id"]
    expected_paths = contract["expected_content_paths"]
    authorities = {item["authority_id"]: item for item in contract["authorities"]}

    receipt_path = repository_path(root, authorities["prepared_declarations"]["path"])
    queue_path = repository_path(root, authorities["completed_queue_archive"]["path"])
    if not receipt_path.exists() or not queue_path.exists() or not plan_argument:
        fail("CUSTODY_ABSENT", "receipt, completed queue archive, and --plan are all required")
    plan_path = repository_path(root, plan_argument)
    if not plan_path.exists():
        fail("CUSTODY_ABSENT", f"canonical rendered plan missing: {plan_argument}")

    receipt = load_json_bytes(receipt_path.read_bytes(), str(receipt_path))
    queue = load_json_bytes(queue_path.read_bytes(), str(queue_path))
    plan = load_json_bytes(plan_path.read_bytes(), str(plan_path))
    if receipt.get("task_id") != task_id or receipt.get("commit_sha") is not None:
        fail("CUSTODY_DISAGREEMENT", "self-neutral receipt task/commit declaration mismatch")
    if receipt.get("paths") != expected_paths:
        fail("CUSTODY_DISAGREEMENT", "receipt path list disagrees with frozen six-path list")
    receipt_hashes = receipt.get("path_sha256")
    receipt_sizes = receipt.get("path_size_bytes")
    if not isinstance(receipt_hashes, dict) or not isinstance(receipt_sizes, dict):
        fail("CUSTODY_DISAGREEMENT", "receipt path declarations missing")
    receipt_rel = authorities["prepared_declarations"]["path"]
    if receipt_hashes.get(receipt_rel) is not None or receipt_sizes.get(receipt_rel) is not None:
        fail("CUSTODY_DISAGREEMENT", "receipt illegally self-authenticates its own hash or size")

    queue_task = find_task_record(queue, task_id)
    if queue_task is None:
        fail("CUSTODY_ABSENT", f"archive task {task_id} absent from queue")
    if queue_task.get("state", queue_task.get("status")) != "completed":
        fail("CUSTODY_ABSENT", f"archive task {task_id} is not completed")
    archive = queue_task.get("archive")
    if not isinstance(archive, dict):
        fail("CUSTODY_ABSENT", "completed queue task lacks archive object")
    queue_hashes = archive.get("path_sha256")
    if not isinstance(queue_hashes, dict) or set(queue_hashes) != set(expected_paths):
        fail("CUSTODY_DISAGREEMENT", "queue archive does not bind exactly six path hashes")
    if not isinstance(archive.get("commit_sha"), str) or not isinstance(archive.get("parent_sha"), str):
        fail("CUSTODY_ABSENT", "queue archive commit/parent authority absent")

    for relative in expected_paths:
        path = repository_path(root, relative)
        if not path.exists():
            fail("CUSTODY_ABSENT", f"custody path absent: {relative}")
        raw = path.read_bytes()
        if queue_hashes.get(relative) != sha256(raw):
            fail("CUSTODY_DISAGREEMENT", f"queue hash disagrees with bytes: {relative}")
        if relative != receipt_rel:
            if receipt_hashes.get(relative) != queue_hashes.get(relative):
                fail("CUSTODY_DISAGREEMENT", f"receipt and queue hash disagree: {relative}")
            if receipt_sizes.get(relative) != len(raw):
                fail("CUSTODY_DISAGREEMENT", f"receipt size disagrees with bytes: {relative}")

    plan_archive = find_plan_archive(plan, task_id)
    if plan_archive is None:
        fail("CUSTODY_ABSENT", f"canonical plan has no content-only archive for {task_id}")
    if plan_archive.get("paths_verified") != contract["expected_content_path_count"]:
        fail("CUSTODY_DISAGREEMENT", "canonical plan paths_verified disagrees")
    if plan_archive.get("generated_paths_skipped") != []:
        fail("CUSTODY_DISAGREEMENT", "canonical plan reports generated paths skipped")


def compare_frozen(path: Path, relative: str, generated: bytes) -> None:
    expected = EXPECTED_ARTIFACTS[relative]
    if len(generated) != expected["size_bytes"] or sha256(generated) != expected["sha256"]:
        fail(
            "OUTPUT_MISMATCH",
            f"generated {relative}: size={len(generated)} sha256={sha256(generated)}",
        )
    try:
        actual = path.read_bytes()
    except FileNotFoundError:
        fail("OUTPUT_MISMATCH", f"materialized artifact missing: {relative}")
    if actual != generated:
        fail(
            "OUTPUT_MISMATCH",
            f"materialized {relative}: size={len(actual)} sha256={sha256(actual)}",
        )


def resolve_package(
    root: Path,
    input_relative: str,
    strategies: list[str],
    check_custody: bool = False,
    plan_argument: str | None = None,
) -> tuple[bytes, bytes]:
    input_path = repository_path(root, input_relative)
    try:
        input_raw = input_path.read_bytes()
    except FileNotFoundError:
        fail("MISSING_SOURCE", f"resolution input missing: {input_relative}")
    input_object = load_json_bytes(input_raw, input_relative)
    composition = input_object["composition"]
    manifest, documents = load_and_verify_sources(root, composition)
    verify_static_contract(input_object, "version")
    if check_custody:
        verify_snapshot_custody(root, input_object, plan_argument)
    disposition_rows, dispositions, leaves_by_source = verify_dispositions(composition, manifest, documents)
    edges = verify_edges(composition, input_object, documents, dispositions)
    verify_static_contract(input_object, "conflict")
    verify_static_contract(input_object, "merge")
    verify_preservation(input_object, documents)
    verify_static_contract(input_object, "authority")
    verify_static_contract(input_object, "entry")
    verify_static_contract(input_object, "output")
    if canonical_bytes(input_object) != input_raw:
        fail("OUTPUT_MISMATCH", "resolution input is not exact canonical compact JSON plus one LF")
    if input_relative == DEFAULT_INPUT:
        frozen = EXPECTED_ARTIFACTS[DEFAULT_INPUT]
        if len(input_raw) != frozen["size_bytes"] or sha256(input_raw) != frozen["sha256"]:
            fail("OUTPUT_MISMATCH", "resolution input differs from the frozen v8 preimage")

    results: list[tuple[bytes, bytes]] = []
    for strategy in strategies:
        resolved, origin = derive(
            input_object,
            input_relative,
            input_raw,
            manifest,
            documents,
            disposition_rows,
            dispositions,
            leaves_by_source,
            edges,
            strategy,
        )
        if resolved["composition"]["source_field_count"] != 1363 or len(origin["rows"]) != 1363:
            fail("OWNERLESS_FIELD", "resolved executable leaf/origin row count is not 1363")
        if len(origin["composition_origin_rows"]) != 10:
            fail("UNRESOLVED_CONTRADICTION", "v8 composition-origin row count is not 10")
        results.append((canonical_bytes(resolved), canonical_bytes(origin)))
    if any(result != results[0] for result in results[1:]):
        fail("ECOMP_LATEST_ONLY", "latest_entry and ordered_entry did not converge byte-identically")
    return results[0]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--resolved", default=DEFAULT_RESOLVED)
    parser.add_argument("--origin", default=DEFAULT_ORIGIN)
    parser.add_argument(
        "--strategy",
        choices=("latest_entry", "ordered_entry", "both"),
        default="both",
    )
    parser.add_argument(
        "--emit",
        choices=("summary", "resolved-contract", "origin-trace"),
        default="summary",
    )
    parser.add_argument("--check-custody", action="store_true")
    parser.add_argument("--plan", help="repository-relative canonical rendered plan path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = args.root.resolve()
    strategies = (
        ["latest_entry", "ordered_entry"]
        if args.strategy == "both"
        else [args.strategy]
    )
    resolved_bytes, origin_bytes = resolve_package(
        root,
        args.input,
        strategies,
        check_custody=args.check_custody,
        plan_argument=args.plan,
    )
    compare_frozen(repository_path(root, args.resolved), args.resolved, resolved_bytes)
    compare_frozen(repository_path(root, args.origin), args.origin, origin_bytes)

    if args.emit == "resolved-contract":
        sys.stdout.buffer.write(resolved_bytes)
    elif args.emit == "origin-trace":
        sys.stdout.buffer.write(origin_bytes)
    else:
        summary = {
            "authority": "zero",
            "custody_checked": bool(args.check_custody),
            "experiment_id": EXPERIMENT_ID,
            "origin_trace": {
                "sha256": sha256(origin_bytes),
                "size_bytes": len(origin_bytes),
            },
            "resolved_contract": {
                "sha256": sha256(resolved_bytes),
                "size_bytes": len(resolved_bytes),
            },
            "status": "PASS",
            "strategies": strategies,
            "version": VERSION,
        }
        sys.stdout.buffer.write(canonical_bytes(summary))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ResolverFailure as exc:
        sys.stderr.buffer.write(
            canonical_bytes(
                {
                    "code": exc.code,
                    "detail": exc.detail,
                    "status": "FAIL",
                }
            )
        )
        raise SystemExit(2)
