"""Replay arithmetic/coverage independently of SAT; never invoke a search solver."""
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import engine


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    # Supports native artifact pointers once raw files are archived.
    sys.path.insert(0, str(ROOT / "tools"))
    import artifact_store
    return artifact_store.read_json(path)


def bound_artifact(root, metadata):
    require(isinstance(metadata, dict), "missing artifact")
    relative = Path(metadata["artifact"])
    require(not relative.is_absolute() and ".." not in relative.parts, "unsafe artifact path")
    path = root / relative
    sys.path.insert(0, str(ROOT / "tools"))
    import artifact_store
    require(artifact_store.content_digest(path) == metadata["sha256"], "artifact hash mismatch: " + str(relative))
    return read(path)


def arithmetic_check(job, answer):
    if job["encoding"] != "synthetic":
        return engine.adapter.verify_encoding_search(job["input"], job["encoding"], answer)
    inp = job["input"]
    polys = [{int(k): v for k, v in f.items()} for f in inp["polynomials"]]
    return engine.adapter.verify_transcript(inp["p"], inp["n"], inp["projected_bits"], polys,
                                           inp.get("domain", []), answer, aux_bound=inp.get("aux_bound"))


def mutation_controls():
    """Known-false supplied transcripts; no solver or curve fixture is called."""
    base = {"status": "complete", "models": [], "learned": [
        {"depth": 0, "prefix": 0, "clause": [], "certificate": [{0: 1}]}]}
    corrupt = copy.deepcopy(base)
    corrupt["learned"][0]["certificate"] = [{0: 2}]
    malformed = copy.deepcopy(base)
    malformed["learned"][0]["clause"] = [1]
    bad_model = {"status": "censored", "models": [0], "learned": []}
    cases = {"corrupted_multiplier": corrupt, "malformed_prefix": malformed, "invalid_model": bad_model}
    results = {}
    for name, answer in cases.items():
        try:
            engine.adapter.verify_transcript(5, 2, 2, [{0: 1}], [], answer)
        except ValueError as error:
            results[name] = {"rejected": True, "error": str(error)}
        else:
            results[name] = {"rejected": False}
    return results


def counters_check(answer, n, limits):
    costs, events, attempts = answer["costs"], answer["costs"]["search_events"], answer["attempts"]
    require(set(events) == set(engine.EVENTS), "missing or unknown declared event counter")
    require(all(type(v) is int and v >= 0 for v in events.values()), "noncanonical event counter")
    require(events["pc_calls"] == len(attempts) <= limits["pc_calls"], "PC attempt accounting")
    require(events["pc_attempted_rows"] == sum(a["attempted_rows"] for a in attempts), "PC row accounting")
    require(events["pc_field_inverse_calls"] == sum(a["rank"] for a in attempts), "PC inverse accounting")
    require(events["pc_unknown"] == sum(a["status"] == "unknown" for a in attempts), "UNKNOWN accounting")
    require(events["partial_attempts"] == sum(a["trigger"] == "partial" for a in attempts), "partial attempt accounting")
    require(events["model_attempts"] == sum(a["trigger"] == "model" for a in attempts), "model attempt accounting")
    require(events["pc_capped_calls"] == sum(a["resource_capped"] for a in attempts), "row cap accounting")
    require(events["accepted_models"] == len(answer["models"]), "model accounting")
    require(events["partial_refutations"] == sum(x["trigger"] == "partial" for x in answer["learned"]), "partial proof accounting")
    require(events["model_refutations"] == sum(x["trigger"] != "partial" for x in answer["learned"]), "model proof accounting")
    require(events["leaf_fallbacks"] == events["leaf_inverse_calls"] == sum(
        x["trigger"] == "leaf_fallback" for x in answer["learned"]), "fallback accounting")
    keys = [(a["depth"], a["prefix"]) for a in attempts]
    require(len(keys) == len(set(keys)), "repeated PC call violates fixed cache rule")
    for a in attempts:
        # The engine's resource marker is raised on the (rows+1)-th insertion.
        require(a["attempted_rows"] <= limits["rows"] + 1, "unbounded PC rows")
        require(a["max_accepted_row_degree"] <= limits["degree"], "PC degree bound exceeded")
    for a in attempts + answer["learned"]:
        if a["trigger"] == "partial":
            require(answer["strategy"] != "model_only", "baseline used partial proof work")
            require(0 <= a["depth"] <= a["contiguous_depth"] <= a["assigned_count"] < n,
                    "fully assigned work mislabeled as partial")
    require(answer["certificate_bytes"] == len(engine._compact(answer["learned"])), "certificate size accounting")
    require(answer["limits"]["degree"] == limits["degree"] and answer["limits"]["rows"] == limits["rows"] and
            answer["limits"]["pc_calls"] == limits["pc_calls"], "declared PC limits differ")
    require(events["sat_calls"] <= answer["limits"]["outer_calls"], "outer call bound exceeded")
    for name in ("native_conflicts_per_call", "native_decisions_per_call"):
        require(answer["limits"][name] == limits[name], "native budget mismatch")
    total = Counter()
    for phase in costs["arithmetic_breakdown"].values():
        total.update(phase)
    # Explicit event-counter convention: absent and zero arithmetic entries
    # are equivalent only for this additive Counter reconciliation.
    require(total == Counter(costs["search_arithmetic"]), "arithmetic phase sum mismatch")
    require(answer["selected_options"] == {"is_lazy": False, "seed": 0, "lucky": 0,
                                            "phase": "negative", "decision": "lowest_unassigned_negative",
                                            "clause_delivery": "external_callback"}, "backend configuration mismatch")


def verify(raw_path):
    import driver
    raw_path = Path(raw_path)
    root = raw_path.parent
    findings, checks = [], []
    try:
        raw = read(raw_path)
        config = raw["config"]
        require(raw["schema"] == "prime-prefix-search-result/v1", "wrong raw schema")
        canonical = ROOT / "experiments" / config["experiment_id"] / "config.json"
        require(hashlib.sha256(canonical.read_bytes()).hexdigest() == raw["config_sha256"] and
                json.loads(canonical.read_text()) == config, "frozen config mismatch")
        require(raw["status"] == "completed", "incomplete run payload")
        cells, selection_costs = driver.select_cells(config)
        require(raw["input_selection"] == {"cells": cells, "costs": selection_costs}, "input selection mismatch")
        search = bound_artifact(root, raw["packages"]["search"])
        controls = bound_artifact(root, raw["packages"]["controls"])
        references = bound_artifact(root, raw["packages"]["reference"])
        ref_check = engine.load("research/prime_sat_costbridge_20261029/check_reference.py", "psearch_independent_reference")
        require(references["config"] == config and len(references["rows"]) == len(cells), "reference inventory")
        refs = {}
        for cell, row in zip(cells, references["rows"]):
            expected_input = {k: cell[k] for k in ("p", "a", "b", "target")}
            domain = {"kind": "interval", "offset": 0, "size": 1 << cell["s"]}
            expected_input.update(D1=domain, D2=domain)
            require(row["cell_id"] == cell["id"] and row["input"] == expected_input, "reference input mismatch")
            result = ref_check.verify(row["input"], row["answer"])
            require(result["valid"] and result == row["check"], "reference certificate failed")
            refs[cell["id"]] = {x | (z << cell["s"]) for x, z in row["answer"]["projected_pairs"]}
        answers = {}
        for category, payload, inventory in (("search", search, list(driver.jobs(config, cells))),
                                               ("controls", controls, list(driver.control_jobs(config)))):
            require(payload["config"] == config, category + " config mismatch")
            rows = payload["rows"]
            require(len(rows) == len(inventory), category + " incomplete inventory")
            require(raw["planned_" + ("search" if category == "search" else "control") + "_ids"] ==
                    [job["id"] for job in inventory], "planned inventory mismatch")
            sys.path.insert(0, str(ROOT / "tools"))
            import artifact_store
            journal = [json.loads(line) for line in artifact_store.read_text(root / (category + "-rows.jsonl")).splitlines()]
            require(journal == rows, category + " journal mismatch")
            states = Counter(row["result"]["declared_status"] for row in rows)
            expected_flow = {"planned": len(inventory), "attempted": len(rows), "complete": states["complete"],
                             "censored": states["censored"], "failed": states["failed"],
                             "interrupted": sum(row["censoring"]["watchdog"] for row in rows)}
            require(raw["flow"][category] == expected_flow, category + " flow mismatch")
            for row, job in zip(rows, inventory):
                for name in ("id", "cell_id", "input", "encoding", "strategy"):
                    require(row[name] == job[name], "row identity mismatch: " + name)
                require(row["result"]["declared_status"] in ("complete", "censored"), "failed worker")
                answer = bound_artifact(root, row["transcript"])
                checked = arithmetic_check(job, answer)
                require(checked["declared_status"] == row["result"]["declared_status"], "censoring changed")
                projected = set(checked["projected_models"])
                expected = refs[row["cell_id"]] if category == "search" else set(job["input"]["expected_models"])
                require(projected <= expected, "spurious projected model")
                if checked["projected_model_set_complete"]:
                    require(projected == expected, "complete projected set differs from reference")
                if not row["censoring"]["watchdog"]:
                    require(row["environment"] == answer["environment"] == raw["environment"], "environment mismatch")
                    n = job["input"]["n"] if category == "controls" else 2 * job["input"]["s"] + (
                        job["input"]["p"].bit_length() if job["encoding"] in ("quadratic", "quadratic_aa") else 0)
                    counters_check(answer, n, config["limits"])
                    for phase in ("search_arithmetic", "search_events", "online_certificate_check", "sat_native"):
                        require(row["phases"][phase] == answer["costs"][phase], "phase provenance mismatch")
                    require(Counter(answer["costs"]["online_certificate_check"]) == Counter(checked["costs"]["identity_check"]),
                            "online identity work differs from independent term-pair count")
                    for field in ("declared_status", "projected_models", "cover_complete", "projected_model_set_complete"):
                        require(row["result"][field] == checked[field], "reported result differs from checker")
                    require(row["result"]["stop_reason"] == answer["stop_reason"], "stop reason mismatch")
                    if category == "search":
                        require(row["phases"]["construction"] == checked["costs"]["construction"], "construction cost mismatch")
                        require(row["phases"]["reconstruction"] == checked["costs"]["witness_reconstruction_and_check"], "reconstruction cost mismatch")
                        expected_offline = {k: v for k, v in checked["costs"].items() if k != "witness_reconstruction_and_check"}
                    else:
                        expected_offline = checked["costs"]
                    require(row["phases"]["offline_verification"] == expected_offline, "offline verification cost mismatch")
                if category == "controls":
                    require(checked["projected_model_set_complete"], "censored control is inconclusive")
                    early = [x for x in answer["learned"] if x["trigger"] == "partial" and x["depth"] < job["input"]["n"]]
                    if row["cell_id"] == "control-positive" and row["strategy"] != "model_only":
                        require(any(x["depth"] == 1 and x["prefix"] == 0 for x in early), "positive pruning control failed")
                    if row["cell_id"] == "control-negative":
                        require(not any(x["depth"] < job["input"]["n"] for x in answer["learned"]), "negative control refuted viable prefix")
                answers[(row["cell_id"], row["encoding"], row["strategy"])] = answer
                checks.append({"id": row["id"], "valid": True, "status": checked["declared_status"],
                               "projected_count": len(projected), "cover_complete": checked["cover_complete"]})
        aa_pairs, aa_censored = 0, []
        for (cell, encoding, strategy), answer in answers.items():
            if strategy == "partial_prefix":
                repeat = answers[(cell, encoding, "partial_prefix_aa")]
                if answer["status"] != "complete" or repeat["status"] != "complete":
                    aa_censored.append({"cell_id": cell, "encoding": encoding, "decision": "inconclusive"})
                    continue
                # Same source and native seed: exact deterministic work identity.
                for field in ("status", "models", "learned", "attempts", "costs", "certificate_bytes", "stop_reason"):
                    require(answer[field] == repeat[field], "A/A mismatch: " + cell + "/" + encoding + "/" + field)
                aa_pairs += 1
        expected_mutations = mutation_controls()
        require(controls["mutations"] == expected_mutations and all(x["rejected"] for x in expected_mutations.values()),
                "mutation controls failed")
        return {"valid": True, "findings": [], "rows": checks, "aa_pairs": aa_pairs, "aa_censored": aa_censored,
                "reference_cells": len(refs), "execution_counters_independently_replayed": False,
                "scope": "checked identities, projected completeness, references and counter consistency; no speedup claim"}
    except (ValueError, KeyError, TypeError, OSError, AssertionError) as error:
        findings.append(str(error))
        return {"valid": False, "findings": findings, "rows": checks}
