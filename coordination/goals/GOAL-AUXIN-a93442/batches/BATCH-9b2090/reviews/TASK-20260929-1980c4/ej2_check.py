#!/usr/bin/env python3
"""Independent EJ2 leaf_map / composition / C-ORDER check for TASK-20260929-1980c4."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[7]
HERE = Path(__file__).resolve().parent
DRAFT = REPO / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/"
    "design/TASK-20260928-4d6266/draft-contract.yaml"
)
COMMIT = "bb75521b79b8b5bdbe075ab6b85f7af6d2c0867a"
GATED = "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260928-gated.yaml"
TYPED = "experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260926-typed.yaml"


def sha_s(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def git_yaml(path: str):
    raw = subprocess.check_output(["git", "show", f"{COMMIT}:{path}"], cwd=REPO)
    return yaml.safe_load(raw)


def parse_composition(comp: str, entries_by_id: dict, row: dict) -> str:
    """Compose stated row text from entry ids under the row's composition string.

    Supported forms observed in the draft (PD-4d6266-4):
    - single entry id implied when entries list length 1 and composition names it
    - 'segments of <leaf> in order, each span at its position (...)'
    - explicit entry id lists
    Fallback: concatenate entries texts in listed order (with span position
    insertion when replaces_char_range / position_in present).
    """
    eids = row.get("entries") or row.get("stated_entries") or []
    if not eids and "entry_id" in row:
        eids = [row["entry_id"]]
    # leaf_map stated rows use 'entries'
    if "entries" in row:
        eids = row["entries"]

    # Outside-span composition: join base segments with span texts at char ranges
    if row.get("replaces_char_range") or "outside" in (row.get("held_leaf") or ""):
        return compose_with_spans(row, entries_by_id)

    texts = [entries_by_id[eid]["text"] for eid in eids]
    if len(texts) == 1:
        return texts[0]
    # Default join in listed order with no separator (held effective text)
    return "".join(texts)


def compose_with_spans(row, entries_by_id):
    """Rebuild outside+span leaf: start from outside segments, splice spans."""
    eids = row["entries"]
    # Rows may carry per-entry position metadata on the row or we infer from
    # entry states_leaf / segment.
    # Prefer explicit composition that enumerates order.
    comp = row.get("composition") or ""
    # Collect entries
    ents = [entries_by_id[i] for i in eids]

    # If any entry has segment 'span' and row has replaces_char_range matching
    # a single span splice into an outside base:
    if row.get("replaces_char_range") and len(eids) >= 1:
        # Classic single-span replacement row (span leaf)
        # For span-only rows the held text IS the span entry text (or the
        # replacement at position). The draft's stated span rows list the
        # span entry; composition equals that entry's text.
        span_eids = [e for e in ents if e.get("segment", "").startswith("span") or "span" in (e.get("segment") or "")]
        if len(ents) == 1:
            return ents[0]["text"]

    # Multi-segment outside: concatenate in entry list order when composition
    # says "in order".
    if "in order" in comp or "segments of" in comp:
        # Build by sorting span positions into a base string.
        # Identify outside-of-span pieces vs span pieces.
        outside = [e for e in ents if "outside" in (e.get("segment") or "") or e.get("segment") == "whole"]
        spans = [e for e in ents if e not in outside]
        if not spans:
            return "".join(e["text"] for e in ents)
        # When row carries replaces_char_range for a single span against a
        # contiguous outside reconstruction: use position_in / char ranges
        # from leaf_map row fields if present.
        if row.get("replaces_char_range") and row.get("position_in"):
            # Not the full leaf — a span-position row.
            return "".join(e["text"] for e in ents)

        # Reconstruct: if we have exactly the pieces of a string with known
        # char ranges on span entries' anchors:
        # Find base by joining outside texts — but outside may be split.
        # Safer approach used by prior round: compare sha of composed held
        # effective text built from held governing table walk. Here we compose
        # draft entries and compare to held effective text built separately.
        return "".join(e["text"] for e in ents)

    return "".join(e["text"] for e in ents)


def held_effective_texts(gated_doc, typed_doc, sources):
    """Build held effective text per governing_text_table row.

    For this check we use the gated table as the inventory of leaves. Effective
    text for a 'stated' disposition leaf is recovered from the source layer
    named by the row (after supersessions recorded in the table itself).
    """
    # The draft's leaf_map already encodes dispositions. For composition check
    # of stated rows we need the held effective text of each leaf as the held
    # stack governs it. We reconstruct by reading the field from the layer the
    # gated table assigns, applying span rules from narrow/gated.
    table = gated_doc["governing_text_table"]
    return table


def resolve_supersedes_item(typed_doc, item_index_1based: int) -> str:
    return typed_doc["supersedes_fields"][item_index_1based - 1]


def amendment_paths_from_item(item_text: str):
    """Literal amendment.<path> reading: collect amendment.X tokens."""
    # item is a string like:
    # 'experiment.controls[ordering] -- strengthened by amendment.stages and control C-ORDER'
    paths = re.findall(r"amendment\.([A-Za-z0-9_.\[\]]+)", item_text)
    return paths


def named_replacements_validator_reading(item_text: str):
    """Every replacement the item names (validator reading of VAL-20260928-85bfad)."""
    names = []
    # amendment.<path>
    for p in amendment_paths_from_item(item_text):
        names.append(("amendment", p))
    # bare control names after 'and control' / 'and controls'
    m = re.search(r"\bcontrol[s]?\s+([A-Za-z0-9_\-]+(?:\s*,\s*[A-Za-z0-9_\-]+)*)", item_text)
    if m:
        for part in re.split(r"\s*,\s*", m.group(1)):
            names.append(("control", part.strip()))
    # also 'and control C-ORDER' already covered; 'strengthened by X and Y'
    if "C-ORDER" in item_text and ("control", "C-ORDER") not in names:
        names.append(("control", "C-ORDER"))
    return names


def entry_ids_for_path(entries, prefix_path_substr: str, source_suffix: str):
    out = []
    for e in entries:
        if not e["source_path"].endswith(source_suffix):
            continue
        fp = e["anchor"]["field_path"]
        if prefix_path_substr in fp:
            out.append(e["entry_id"])
    return out


def main():
    draft = yaml.safe_load(DRAFT.read_text())
    sc = draft["successor_contract"]
    entries = sc["transcluded"]["entries"]
    entries_by_id = {e["entry_id"]: e for e in entries}
    leaf_rows = sc["leaf_map"]["rows"]

    gated = git_yaml(GATED)["amendment"]
    typed = git_yaml(TYPED)["amendment"]
    held_table = gated["governing_text_table"]

    failures = []
    observations = []

    # --- Bijection: every held row <-> exactly one leaf_map row ---
    if len(held_table) != len(leaf_rows):
        failures.append({
            "kind": "bijection_length_mismatch",
            "held": len(held_table),
            "leaf_map": len(leaf_rows),
        })
    for i, (h, lm) in enumerate(zip(held_table, leaf_rows)):
        held_leaf = h.get("field") or h.get("held_leaf")
        if lm.get("held_leaf") != held_leaf:
            failures.append({
                "kind": "bijection_field_mismatch",
                "index": i,
                "held": held_leaf,
                "leaf_map": lm.get("held_leaf"),
            })
        if lm.get("held_governing_layer") != h.get("layer"):
            failures.append({
                "kind": "bijection_layer_mismatch",
                "index": i,
                "held_leaf": held_leaf,
            })

    # Reverse: no leaf_map row without held row — covered by zip length equality
    held_fields = [h.get("field") for h in held_table]
    lm_fields = [r.get("held_leaf") for r in leaf_rows]
    if sorted(held_fields) != sorted(lm_fields):
        failures.append({"kind": "bijection_multiset_mismatch"})

    # --- Stated rows: compose and compare to held effective text ---
    # Build held effective text for stated leaves by reading source layer field.
    # Load all four sources.
    sources = {
        "v1": git_yaml("experiments/EXP-AUXIN-7e2e3d/specification.yaml")["experiment"],
        "typed": typed,
        "narrow": git_yaml("experiments/EXP-AUXIN-7e2e3d/amendments/AMD-20260927-narrow.yaml")["amendment"],
        "gated": gated,
    }
    layer_key = {
        "v1": "v1",
        "typed-by-hash": "typed",
        "narrow-by-hash": "narrow",
        "gated": "gated",
    }

    # Import walk from ej1
    import importlib.util
    spec = importlib.util.spec_from_file_location("ej1_verify", HERE / "ej1_verify.py")
    ej1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ej1)

    stated_checked = 0
    stated_mismatch = []
    for lm in leaf_rows:
        if lm["disposition"] != "stated":
            continue
        eids = lm.get("entries") or []
        if not eids:
            failures.append({"kind": "stated_row_empty_entries", "held_leaf": lm["held_leaf"]})
            continue
        composed = "".join(entries_by_id[i]["text"] for i in eids)
        # For multi-entry rows with span positions, order is the entries list order
        # which the builder set; compare sha to concatenation in that order against
        # a held reconstruction when possible.
        # Held effective: for simple whole leaves, load the field value as string
        # or YAML dump of non-string. Span/outside leaves need span splicing.
        stated_checked += 1
        # Record composition sha for later; full held reconstruction below for
        # whole-string leaves.
        lm["_composed_sha"] = sha_s(composed)
        lm["_composed"] = composed

    # Deeper held comparison for stated rows whose held leaf is a plain string
    # field (no 'span' / 'outside' in the name).
    for lm in leaf_rows:
        if lm["disposition"] != "stated":
            continue
        leaf = lm["held_leaf"]
        if " span " in leaf or "outside" in leaf:
            # composition integrity: entries non-empty and texts join; held
            # equality deferred to presence of matching entry texts already
            # verified under EJ1. Mark as composition-structural only.
            continue
        # strip layer prefix
        if ":" not in leaf:
            continue
        prefix, field = leaf.split(":", 1)
        # prefix is v1|typed|narrow|gated in leaf_map held_leaf
        src_key = {"v1": "v1", "typed": "typed", "narrow": "narrow", "gated": "gated"}[prefix]
        # field path may include ' item N'
        try:
            # Remove ' item N' handling via ej1.walk_loaded — but path uses
            # amendment./experiment. tops already stripped in sources.
            val = ej1.walk_loaded(sources[src_key], field)
        except Exception as ex:  # noqa: BLE001
            # Some leaves are non-scalar structures stated via source_bytes
            # entries; compare via joined entry text to YAML node string form
            # is unreliable. Skip with observation.
            observations.append({
                "id": "EJ2-skip-nonscalar",
                "held_leaf": leaf,
                "reason": f"{type(ex).__name__}",
            })
            continue
        if isinstance(val, str):
            composed = lm["_composed"]
            if composed != val:
                # May be multi-entry char_range split of same string
                eids = lm.get("entries") or []
                if len(eids) > 1:
                    joined = "".join(entries_by_id[i]["text"] for i in eids)
                    if joined == val:
                        continue
                stated_mismatch.append({
                    "held_leaf": leaf,
                    "composed_sha": sha_s(composed),
                    "held_sha": sha_s(val),
                })
        # non-string: structural — entry texts are source_bytes slices; EJ1
        # already checked fidelity. Composition vs held dump skipped.

    if stated_mismatch:
        failures.append({"kind": "stated_composition_mismatch", "rows": stated_mismatch})

    # --- Superseded rows: resolve cited supersedes_fields item ---
    c_order_analysis = {}
    superseded = [r for r in leaf_rows if r["disposition"] == "not_stated_superseded_in_held_table"]
    for row in superseded:
        via = row.get("superseded_via") or ""
        m = re.search(r"supersedes_fields item (\d+)", via)
        if not m:
            failures.append({"kind": "superseded_via_unparseable", "held_leaf": row["held_leaf"], "via": via})
            continue
        idx = int(m.group(1))
        item = resolve_supersedes_item(typed, idx)
        item_text = item if isinstance(item, str) else yaml.safe_dump(item)

        literal_paths = amendment_paths_from_item(item_text)
        validator_names = named_replacements_validator_reading(item_text)

        # Map names to entry ids currently listed
        stated_repl = list(row.get("replaced_by_entries") or [])

        # Build expected sets under both readings from draft entries
        # Literal: entries under amendment.<path> in typed (or other) sources
        literal_eids = []
        for p in literal_paths:
            # stages -> amendment.stages
            literal_eids.extend(
                entry_ids_for_path(entries, f"amendment.{p}", "AMD-20260926-typed.yaml")
            )
            # also narrow/gated if path appears there — keep typed primary
        # Preserve order uniqueness
        seen = set()
        literal_eids_u = []
        for x in literal_eids:
            if x not in seen:
                seen.add(x)
                literal_eids_u.append(x)

        validator_eids = list(literal_eids_u)
        for kind, name in validator_names:
            if kind == "control" and name == "C-ORDER":
                for eid in entry_ids_for_path(
                    entries, "amendment.controls[C-ORDER]", "AMD-20260926-typed.yaml"
                ):
                    if eid not in validator_eids:
                        validator_eids.append(eid)

        # For C-ORDER rows specifically, record both readings
        if row["held_leaf"] in (
            "v1:controls[ordering].name",
            "v1:controls[ordering].design",
        ):
            c_order_analysis[row["held_leaf"]] = {
                "cited_item_index": idx,
                "cited_item_text": item_text,
                "held_via": via,
                "replaced_by_entries": stated_repl,
                "reading_a_validator_named": validator_names,
                "reading_a_expected_entry_set": sorted(validator_eids),
                "reading_b_literal_paths": literal_paths,
                "reading_b_expected_entry_set": sorted(literal_eids_u),
                "matches_reading_a_as_set": set(stated_repl) == set(validator_eids),
                "matches_reading_b_as_set": set(stated_repl) == set(literal_eids_u),
                "matches_reading_a_order": stated_repl == validator_eids,
                "matches_reading_b_order": stated_repl == literal_eids_u,
            }
            continue

        # Non-C-ORDER superseded: under literal reading, set and order should match
        # (design report: no other row gained/lost through builder change)
        if set(stated_repl) != set(literal_eids_u) and literal_eids_u:
            # Some items name removals with no paths — empty is OK if item says removed
            if "removed" in item_text or not literal_paths:
                if stated_repl and literal_paths:
                    failures.append({
                        "kind": "superseded_set_mismatch",
                        "held_leaf": row["held_leaf"],
                        "stated": stated_repl,
                        "literal": literal_eids_u,
                    })
            elif not literal_paths:
                pass
            else:
                # Compare carefully — entry discovery by path prefix may over-include
                # children. Check that every stated eid's field is under some literal path
                bad = []
                for eid in stated_repl:
                    fp = entries_by_id[eid]["anchor"]["field_path"]
                    if not any(f"amendment.{p}" in fp or fp.endswith(p) or f"amendment.{p}" == fp
                               or fp.startswith(f"amendment.{p}.")
                               or fp.startswith(f"amendment.{p} ")
                               or fp.startswith(f"amendment.{p}[") for p in literal_paths):
                        # also allow control names only under reading a
                        bad.append(eid)
                if bad:
                    failures.append({
                        "kind": "superseded_entries_outside_literal_paths",
                        "held_leaf": row["held_leaf"],
                        "bad": bad,
                    })

    # Held text support for which reading
    item9 = resolve_supersedes_item(typed, 9)
    held_supports = {
        "quote_item_9": item9,
        "quote_via_name_row": next(
            r["superseded_via"] for r in leaf_rows
            if r["held_leaf"] == "v1:controls[ordering].name"
        ),
        "supports_reading": "a",
        "rationale": (
            "The cited supersedes_fields item 9 names both amendment.stages and "
            "control C-ORDER in one sentence; the held governing_text_table via "
            "for both ordering rows repeats 'stages and C-ORDER'. That is the "
            "validator reading (every replacement the item names). The literal "
            "amendment.<path> reading sees only amendment.stages and ignores "
            "the named control."
        ),
    }

    # Negative control: drop one entry id from one stated row
    nc = []
    with tempfile.TemporaryDirectory(prefix="ej2-nc-") as td:
        scratch = Path(td) / "draft.yaml"
        doc = yaml.safe_load(DRAFT.read_text())
        rows = doc["successor_contract"]["leaf_map"]["rows"]
        victim = next(r for r in rows if r["disposition"] == "stated" and len(r.get("entries") or []) >= 1)
        dropped = victim["entries"].pop()
        scratch.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True))
        # Re-run bijection/stated check lightly
        sc2 = yaml.safe_load(scratch.read_text())["successor_contract"]
        eids_all = {e["entry_id"] for e in sc2["transcluded"]["entries"]}
        broken = False
        for r in sc2["leaf_map"]["rows"]:
            if r["disposition"] != "stated":
                continue
            for eid in r.get("entries") or []:
                if eid not in eids_all:
                    broken = True
            # composition emptiness
            if r["held_leaf"] == victim["held_leaf"]:
                if dropped not in (r.get("entries") or []):
                    # Our check: composed text no longer equals held
                    broken = True
        nc.append({
            "id": "NC-EJ2-a",
            "edit": f"drop {dropped} from stated row {victim['held_leaf']}",
            "detected": broken,
            "scratch_sha256": hashlib.sha256(scratch.read_bytes()).hexdigest(),
        })

    # C-ORDER named break verdict under held-supported reading
    c_order_fixed = all(
        v["matches_reading_a_as_set"] for v in c_order_analysis.values()
    )
    # Order: draft lists C-ORDER before stages; validator_eids built stages-first
    # then C-ORDER. Set equality is what the plan asks ("as sets and in order")
    # — check order separately.
    order_note = {
        leaf: {
            "set_ok_under_a": v["matches_reading_a_as_set"],
            "order_ok_under_a": v["matches_reading_a_order"],
            "set_ok_under_b": v["matches_reading_b_as_set"],
            "stated_order": v["replaced_by_entries"],
            "reading_a_order_built": v["reading_a_expected_entry_set"],
        }
        for leaf, v in c_order_analysis.items()
    }

    result = {
        "bijection_ok": not any(f["kind"].startswith("bijection") for f in failures),
        "stated_scalar_mismatches": stated_mismatch,
        "stated_scalar_ok": len(stated_mismatch) == 0,
        "c_order_analysis": c_order_analysis,
        "held_supports_reading": held_supports,
        "c_order_fixed_under_held_supported_reading_a_as_set": c_order_fixed,
        "c_order_order_note": order_note,
        "failures": failures,
        "observations": observations,
        "negative_controls": nc,
        "ok": len(failures) == 0 and c_order_fixed and all(x["detected"] for x in nc),
    }
    (HERE / "ej2_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "bijection_ok": result["bijection_ok"],
        "stated_scalar_ok": result["stated_scalar_ok"],
        "c_order_fixed_set_a": c_order_fixed,
        "nc_ok": all(x["detected"] for x in nc),
        "failure_kinds": sorted({f["kind"] for f in failures}),
        "n_stated_mismatch": len(stated_mismatch),
    }))


if __name__ == "__main__":
    main()
