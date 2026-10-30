#!/usr/bin/env python3
"""Versioned native custody bridge; production CLI accepts frozen native plans."""
import argparse
import copy
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
import raw_capsule as capsule

ARMS = ("fixed-x", "fixed-x-aa", "positive", "negative")
TOP = (
    "manifest.yaml", "raw-result.json", "driver-exit.json",
    "driver.stdout.txt", "driver.stderr.txt", "fixed-x.raw.json.gz",
)
GENERATED = (
    "launch.json", "execution-receipt.json", "command.txt",
    "environment.json", "stdout.log", "stderr.log",
    "check.stdout.log", "check.stderr.log",
)
RAW_MEMBERS = capsule.RAW_MEMBERS
CHECKER_SHA256 = hashlib.sha256(
    Path(__file__).with_name("checker_v2.py").read_bytes()
).hexdigest()
canonical = capsule.canonical
sha = capsule.sha

def require(value, message):
    if not value:
        raise ValueError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    with path.open("x", encoding="utf8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")

def read(path):
    return capsule.strict_json(path.read_bytes())

def validate_identity(row):
    ident = row["identity"]
    field, curve = ident["field"], ident["curve"]
    p, a, b, n = (int(row[k], 16) for k in ("p_hex", "a_hex", "b_hex", "n_hex"))
    require(field["characteristic"] == p and field["degree"] == 1, "field identity mismatch")
    require(field["representation"] == "prime_field", "unsupported field")
    require(curve["model"] == "short_weierstrass", "unsupported curve model")
    require((curve["a4"], curve["a6"], curve["subgroup_order"], curve["cofactor"]) == (a, b, n, 1), "curve identity mismatch")
    digest = sha(canonical({"field": field, "curve": {k:v for k,v in curve.items() if k != "curve_id"}}))
    require(ident["curve_sha256"] == digest, "curve digest mismatch")
    require(ident["curve_uid"] == "urn:ec-record:1:sha256:" + digest, "curve UID mismatch")
    require(ident["field_sha256"] == sha(canonical(field)), "field digest mismatch")
    require(type(p) is int and p > 2 and p % 2 == 1, "odd-prime input required")
    require(a == p - 3 and 0 <= b < p, "unexpected coefficient encoding")
    require(all(type(v) is int and 0 <= v < p for v in curve["generator"]) and len(curve["generator"]) == 2, "invalid generator encoding")
    return p, a, b, n

def independent_plan(assessed, traits, matrix):
    omissions = assessed["candidate_rows"]
    published = traits["published_controls"]
    require(len(omissions) == 11 and len(published) == 10 and len(matrix["rows"]) == 21, "unexpected named scope")
    sources = {}
    for label, name, row in [("passed_over", r["identity"]["curve_id"], r) for r in omissions] + [("published", name, r) for name,r in published.items()]:
        validate_identity(row)
        uid = row["identity"]["curve_uid"]
        require(uid not in sources, "duplicate source UID")
        sources[uid] = (label, name, row)
    matrix_by_slot, matrix_uids = {}, set()
    for row in matrix["rows"]:
        uid = row["curve_uid"]
        require(uid in sources and uid not in matrix_uids, "missing or duplicate matrix UID")
        matrix_uids.add(uid)
        label, name, source = sources[uid]
        require((row["label"], row["name"], row["timestamp"], row["ordinal"], row["seed_hex"]) == (label, name, source["timestamp"], source["seed_ordinal_one_based"], source["seed_hex"]), "matrix/source join mismatch")
        key = row["timestamp"], row["ordinal"]
        require(key not in matrix_by_slot, "duplicate timestamp/ordinal")
        matrix_by_slot[key] = row
    require(matrix_uids == set(sources), "incomplete exact-UID join")
    workload, seen_slots, timestamps = [], set(), set()
    for stream in sorted(matrix["streams"], key=lambda s:s["timestamp"]):
        timestamp = stream["timestamp"]
        require(timestamp not in timestamps, "duplicate stream")
        timestamps.add(timestamp)
        slots = stream["slots"]
        require([r["ordinal"] for r in slots] == sorted(set(r["ordinal"] for r in slots)), "unordered or duplicate stream slots")
        require(sum(r["label"] == "published" for r in slots) == stream["published_count"], "published stream count mismatch")
        require(sum(r["label"] == "passed_over" for r in slots) == stream["passed_over_count"], "omission stream count mismatch")
        previous = None
        for i, slot in enumerate(slots):
            key = timestamp, slot["ordinal"]
            require(key in matrix_by_slot and key not in seen_slots, "stream coverage mismatch")
            seen_slots.add(key)
            item = matrix_by_slot[key]
            require((slot["name"], slot["label"], slot["seed_prefix"]) == (item["name"], item["label"], item["seed_hex"][:8]), "stream/matrix mismatch")
            source = sources[item["curve_uid"]][2]
            if item["label"] == "published":
                counterpart = item
            else:
                counterpart = next((matrix_by_slot[(timestamp, s["ordinal"])] for s in slots[i+1:] if s["label"] == "published"), None)
                require(counterpart is not None, "omission has no next publication")
            control = sources[counterpart["curve_uid"]][2]
            p, a, b, n = validate_identity(source)
            cp, ca, cb, cn = validate_identity(control)
            require(p == cp and a == ca and p.bit_length() == stream["field_bits"], "counterpart field mismatch")
            x, y = control["identity"]["curve"]["generator"]
            entry = {"row_id": str(timestamp)+"-"+str(slot["ordinal"]), "kind": "published_self" if item["label"] == "published" else "canonical_omission", "name":item["name"], "curve_uid":item["curve_uid"], "timestamp":timestamp, "ordinal":slot["ordinal"], "previous_published_uid":previous, "counterpart_name":counterpart["name"], "counterpart_uid":counterpart["curve_uid"], "counterpart_ordinal":counterpart["ordinal"], "p_hex":hex(p), "a_hex":hex(a), "b_hex":hex(b), "n_hex":hex(n), "fixed_x_hex":hex(x), "fixed_y_hex":hex(y)}
            workload.append(entry)
            alternate = source.get("alternate_sign_model")
            if alternate is not None:
                require(p.bit_length() == 224 and slot["ordinal"] in (777, 1485, 5736), "unexpected alternate model")
                alt_b = int(alternate["b_hex"], 16)
                require(alt_b == (-b) % p and alternate["curve_uid"] != item["curve_uid"], "alternate binding mismatch")
                alt = dict(entry, row_id=entry["row_id"]+"-opposite-sign", kind="alternate_sign_sensitivity", curve_uid=alternate["curve_uid"], canonical_uid=item["curve_uid"], b_hex=hex(alt_b), isomorphism=alternate["isomorphism"], isomorphism_u_hex=alternate["isomorphism_u_hex"], x_transport="none: fixed x unchanged")
                workload.append(alt)
            if item["label"] == "published":
                previous = item["curve_uid"]
    require(seen_slots == set(matrix_by_slot), "stream omits a named position")
    require([sum(r["kind"] == kind for r in workload) for kind in ("canonical_omission", "published_self", "alternate_sign_sensitivity")] == [11, 10, 3], "unexpected workload partitions")
    require(len({r["curve_uid"] for r in workload}) == 24, "duplicate representation UID")
    return workload

def context(args, running):
    root = Path(__file__).resolve().parents[4]
    require(not args.out.is_symlink(), "aliased native output")
    directory = args.out.resolve()
    directory.relative_to(root / "experiments")
    require(directory.is_dir(), "supervisor must create run directory")
    plan_path = args.plan.resolve()
    protocol_path = args.protocol.resolve()
    plan_path.relative_to(root)
    protocol_relative = protocol_path.relative_to(root).as_posix()
    launch = read(directory / "launch.json")
    require(digest(plan_path) == launch["plan_sha256"], "launch/plan mismatch")
    sys.path.insert(0, str(root / "tools"))
    supervisor = importlib.import_module("experiment_execution")
    plan = supervisor.load_plan(root, plan_path)
    trial = next(t for t in plan["trials"] if t["id"] == launch["trial_id"])
    require(supervisor.run_root(root, plan, trial).resolve() == directory,
            "wrong native run directory")
    require(trial["run_id"] == launch["run_id"], "run identity mismatch")
    require(plan["input_sha256"].get(protocol_relative) == digest(protocol_path),
            "protocol is not exact bound plan input")
    checker = Path(__file__).with_name("checker_v2.py")
    require(digest(checker) == CHECKER_SHA256, "fixed checker changed")
    require(plan["source_sha256"].get(checker.relative_to(root).as_posix()) == CHECKER_SHA256,
            "checker absent from native source closure")
    require(
        tuple(trial["artifacts"]) == TOP,
        "wrong top-level artifact closure",
    )
    for source in (
        "checker_v2.py", "native_bridge_v2.py",
        "raw_capsule.py", "native_schema.json",
    ):
        path = Path(__file__).with_name(source)
        relative = path.relative_to(root).as_posix()
        require(
            plan["source_sha256"].get(relative) == digest(path),
            "source absent or changed: " + source,
        )
        committed = subprocess.run(
            ["git", "-C", str(root), "show", "HEAD:" + relative],
            check=True,
            capture_output=True,
        ).stdout
        require(
            committed == path.read_bytes(),
            "source differs from committed HEAD",
        )
    protocol = read(protocol_path)
    require(protocol["freeze"]["status"] == "frozen", "unfrozen protocol")
    core = {key:value for key,value in protocol.items() if key != "freeze"}
    core_sha = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":"),
                                        ensure_ascii=False).encode()).hexdigest()
    require(core_sha == protocol["freeze"]["protocol_sha256"], "protocol core hash mismatch")
    if running:
        authority = launch["authority"]
        fresh = supervisor.authorize(root, plan_path, plan,
                                     authority["owner"], authority["epoch"])
        require(all(fresh[k] == authority[k] for k in ("owner", "epoch", "commit")),
                "native authority changed before driver call")
    return root, directory, plan, launch, protocol, protocol_path, checker, supervisor


def expected_rows(root, protocol):
    expected_pins = {
        "research/nist_seed_skipped_curves_20261016/assessed.json":
            "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
        "research/nist_seed_skipped_curves_20261016/traits.json":
            "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
        "research/nist_seed_selection_deep_20261016/selection_matrix.json":
            "d93eabf58eecdb48cb74657d28e985c965bc6ca8a74ec02e468846e8c77329b6",
    }
    require(
        protocol["extensions"]["source_pins"] == expected_pins,
        "wrong fixed input closure",
    )
    documents = []
    for name, expected in expected_pins.items():
        data = (root / name).read_bytes()
        require(sha(data) == expected, "changed exact input")
        committed = subprocess.run(
            ["git", "-C", str(root), "show", "HEAD:" + name],
            check=True,
            capture_output=True,
        ).stdout
        require(data == committed, "input differs from committed HEAD")
        documents.append(capsule.strict_json(data))
    return independent_plan(*documents)

def jacobi(value, modulus):
    require(modulus > 0 and modulus % 2 == 1, "Jacobi needs positive odd modulus")
    value %= modulus
    sign = 1
    while value:
        while value % 2 == 0:
            value //= 2
            if modulus % 8 in (3, 5):
                sign = -sign
        value, modulus = modulus, value
        if value % 4 == modulus % 4 == 3:
            sign = -sign
        value %= modulus
    return sign if modulus == 1 else 0

def arithmetic(row):
    p, a, b, x, y = (int(row[k], 16) for k in ("p_hex", "a_hex", "b_hex", "fixed_x_hex", "fixed_y_hex"))
    value = (pow(x, 3, p) + (a*x) + b) % p
    residue = pow(value, (p-1)//2, p)
    require(residue in (0, 1, p-1), "unexpected residue on bound prime input")
    symbol = -1 if residue == p-1 else residue
    require(jacobi(value, p) == symbol, "independent Euler/Jacobi disagreement")
    return {"rhs_hex": hex(value), "euler_value_hex": hex(residue), "symbol": symbol,
            "jacobi": symbol, "lifts": symbol >= 0,
            "full_point_member": pow(y, 2, p) == value,
            "b_determined_by_full_point_hex": hex((pow(y, 2, p)-pow(x, 3, p)-a*x) % p)}


def produce(args, *, child_call=None, context_call=None):
    # Injection is a Python engineering seam, never a production CLI option.
    (
        root, directory, plan, launch, protocol,
        protocol_path, checker, supervisor,
    ) = (context_call or context)(args, True)
    require(not directory.is_symlink(), "aliased native output")
    child_directory = directory / ".fixed-x-child"
    for name in (*TOP, ".fixed-x-child"):
        path = directory / name
        require(
            not path.exists() and not path.is_symlink(),
            "refusing existing driver output: " + name,
        )
    argv = [
        sys.executable, str(checker),
        "--protocol", str(protocol_path),
        "--out", str(child_directory),
        "--native-plan", str(args.plan),
        "--native-out", str(directory),
    ]
    began = datetime.now(timezone.utc).isoformat()
    child_rc, error, stdout, stderr = None, None, b"", b""

    def exact_bytes(value):
        require(
            value is None or type(value) is bytes,
            "child capture must be binary",
        )
        return value or b""

    try:
        child = (child_call or subprocess.run)(
            argv,
            cwd=root,
            capture_output=True,
            timeout=protocol["execution"]["timeout_seconds"],
        )
        child_rc = child.returncode
        stdout, stderr = exact_bytes(child.stdout), exact_bytes(child.stderr)
    except subprocess.TimeoutExpired as exc:
        stdout = exact_bytes(exc.stdout)
        stderr = exact_bytes(exc.stderr)
        error = {"kind": "child_timeout", "message": str(exc)}
    except OSError as exc:
        error = {"kind": "child_invocation_error", "message": str(exc)}

    for name, data in (
        ("driver.stdout.txt", stdout), ("driver.stderr.txt", stderr),
    ):
        with (directory / name).open("xb") as stream:
            stream.write(data)
    write(directory / "driver-exit.json", {
        "argv": argv,
        "started_at": began,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "wrapper_pid": os.getpid(),
        "child_call_attempted": True,
        "child_returncode_observed": child_rc,
        "error": error,
    })

    packaging_error, capsule_bytes = None, None
    summary, semantic_error = None, None
    try:
        capsule_bytes = capsule.pack(child_directory)
        with (directory / "fixed-x.raw.json.gz").open("xb") as stream:
            stream.write(capsule_bytes)
    except Exception as exc:
        packaging_error = {
            "kind": "capsule_packaging_error", "message": repr(exc),
        }
    if capsule_bytes is not None:
        try:
            members = capsule.unpack(capsule_bytes)
            expected = expected_rows(root, protocol)
            summary = verify_inner(members, expected, protocol, launch)
        except Exception as exc:
            semantic_error = {
                "kind": "raw_invalid_or_incomplete", "message": repr(exc),
            }

    valid = (
        child_rc == 0 and error is None
        and packaging_error is None and semantic_error is None
        and summary is not None
    )
    metrics = ({
        "canonical_omission_lifts": summary["canonical_omission_lifts"],
        "main_lift_count": summary["main_lift_count"],
        "planned_main_rows": 24,
    } if valid else {})
    manifest = {"run": {
        "attack_claimed": False,
        "metrics": metrics,
        "result": {"certificate": {"kind": "none"}, "valid": valid},
    }}
    if not valid:
        manifest["run"]["status"] = "completed_invalid"
        manifest["run"]["result"]["reason"] = (
            "Retained child failure, raw incompleteness, "
            "packaging or semantic error."
        )
    manifest_data = (
        json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n"
    )
    native_names = [
        "driver.stdout.txt", "driver.stderr.txt", "driver-exit.json",
    ] + (["fixed-x.raw.json.gz"] if capsule_bytes is not None else [])
    raw = {
        "schema": "nist.fixed-x.native/v2",
        "attack_claimed": False,
        "experiment_id": plan["experiment_id"],
        "run_id": launch["run_id"],
        "plan_sha256": launch["plan_sha256"],
        "protocol_path": protocol_path.relative_to(root).as_posix(),
        "protocol_file_sha256": digest(protocol_path),
        "protocol_sha256": protocol["freeze"]["protocol_sha256"],
        "checker_sha256": CHECKER_SHA256,
        "valid": valid,
        "summary": summary,
        "packaging_completed": packaging_error is None,
        "packaging_error": packaging_error,
        "semantic_error": semantic_error,
        "native_artifacts": {
            name: digest(directory / name) for name in native_names
        },
        "driver_manifest_sha256": sha(manifest_data),
    }
    write(directory / "raw-result.json", raw)
    with (directory / "manifest.yaml").open("xb") as stream:
        stream.write(manifest_data)

    # Deletion requires a completed lossless capsule. A packaging failure
    # keeps the child tree intact, records the error, and returns failure.
    if (
        capsule_bytes is not None
        and child_directory.exists()
        and not child_directory.is_symlink()
    ):
        shutil.rmtree(child_directory)
    print(json.dumps({
        "packaging_completed": packaging_error is None,
        "scientific_output_valid": valid,
    }))
    return 0 if valid else 2

def verify_inner(members, expected, protocol, launch):
    started = capsule.strict_json(members["started.json"])
    require(started["source_pins"] == protocol["extensions"]["source_pins"] and
            started["observed_commit"] == launch["authority"]["commit"],
            "wrong raw input or observed-commit provenance")
    workload = capsule.strict_json(members["workload.json"])
    require(len(workload) == 24, "wrong raw workload length")
    arms = {name: capsule.strict_json(members[name+".json"]) for name in ARMS}
    require(all(obj["arm"] == name and obj["status"] == "succeeded" for name,obj in arms.items()),
            "an arm is invalid or absent")
    main = arms["fixed-x"]["rows"]
    # Individual validity is established before A/A equality.
    for arm_name in ("fixed-x", "fixed-x-aa"):
        rows = arms[arm_name]["rows"]
        require(len(rows) == 24, "arm coverage")
        for expect, observed in zip(expected, rows):
            require(
                all(observed.get(key) == value
                    for key, value in expect.items()),
                "individual identity/chronology",
            )
            require(
                observed.get("status") == "succeeded",
                "individual row invalid",
            )
            require(
                type(observed.get("symbol")) is int
                and type(observed.get("jacobi")) is int
                and type(observed.get("lifts")) is bool
                and type(observed.get("full_point_member")) is bool,
                "individual metric type",
            )
            require(
                all(observed.get(key) == value
                    for key, value in arithmetic(expect).items()),
                "individual semantic arithmetic",
            )
        require(
            all(row["lifts"] and row["full_point_member"]
                for row in rows if row["kind"] == "published_self"),
            "individual self control",
        )
    for expect, planned, observed in zip(expected, workload, main):
        require(all(planned.get(k) == value and observed.get(k) == value for k,value in expect.items()),
                "wrong independent pairing, UID, parameters or point")
        require(observed["status"] == "succeeded", "invalid raw membership")
        require(type(observed["symbol"]) is int and type(observed["lifts"]) is bool and
                type(observed["full_point_member"]) is bool, "wrong metric type")
        require(all(observed.get(k) == value for k,value in arithmetic(expect).items()), "arithmetic disagreement")
    self_rows = [row for row in main if row["kind"] == "published_self"]
    canonical = [row for row in main if row["kind"] == "canonical_omission"]
    alternate = [row for row in main if row["kind"] == "alternate_sign_sensitivity"]
    require((len(self_rows), len(canonical), len(alternate)) == (10,11,3), "wrong partitions")
    require(all(row["lifts"] and row["full_point_member"] for row in self_rows), "self control failure")
    positives, negatives = arms["positive"]["rows"], arms["negative"]["rows"]
    require(len(positives) == 2 and len(negatives) == 3, "wrong fixture coverage")
    for row, b, y, symbol in ((positives[0],1,1,1), (positives[1],0,0,0), (negatives[0],3,0,-1)):
        expect = {"p_hex":hex(101),"a_hex":hex(-3),"b_hex":hex(b),"fixed_x_hex":"0x0","fixed_y_hex":hex(y)}
        require((row["p"],row["a"],row["b"],row["x"],row["y"]) == (101,-3,b,0,y), "changed fixture")
        require(
            type(row.get("symbol")) is int
            and type(row.get("jacobi")) is int
            and type(row.get("lifts")) is bool
            and type(row.get("full_point_member")) is bool,
            "fixture metric type",
        )
        require(row["symbol"] == symbol and all(
            row.get(k) == v for k,v in arithmetic(expect).items()),
                "fixture arithmetic failed")
    require(negatives[1]["name"] == "proves-too-much-full-point" and negatives[1]["passed"] is True,
            "circularity control absent")
    for key, b in (("positive", 1), ("nearby_b4", 4)):
        expect = {"p_hex":hex(101),"a_hex":hex(-3),"b_hex":hex(b),"fixed_x_hex":"0x0","fixed_y_hex":"0x1"}
        require(all(negatives[1][key].get(k) == value for k,value in arithmetic(expect).items()),
                "circularity fixture changed")
    require(negatives[2] == {"name":"source-binding-and-schema-corruption","passed":True},
            "fail-closed control absent")
    require(main == arms["fixed-x-aa"]["rows"], "A/A equality")
    batch_rows = [
        capsule.strict_json(line)
        for line in members["rows.jsonl"].splitlines() if line.strip()
    ]
    require(len(batch_rows) == 4 and [row["arm"] for row in batch_rows] == list(ARMS),
            "wrong export batch rows")
    for name, row in zip(ARMS, batch_rows):
        details = arms[name]["rows"]
        require(row["status"] == "succeeded" and row["verification"] == "verified" and
                row["instance_id"] == "0" and row["replicate"] == 0 and row["seed"] == 0 and
                row["warmup"] is False and row["binary_sha256"] == CHECKER_SHA256 and
                row["source_commit"] == started["observed_commit"], "wrong export provenance or status")
        require(type(row["lift_count"]) is int and type(row["evaluated_count"]) is int and
                row["lift_count"] == sum(item.get("lifts") is True for item in details) and
                row["evaluated_count"] == sum("lifts" in item for item in details),
                "export batch metric differs from raw rows")
    summary = capsule.strict_json(members["summary.json"])
    require(summary["valid"] is True and
            summary["protocol_sha256"] == protocol["freeze"]["protocol_sha256"],
            "summary changed or invalid")
    require(summary["canonical_omission_rows"] == 11 and
            summary["canonical_omission_lifts"] == sum(row["lifts"] for row in canonical) and
            summary["canonical_witness_uids"] == [row["curve_uid"] for row in canonical if row["lifts"]],
            "wrong canonical summary")
    require(summary["alternate_sign_sensitivity"] == alternate and
            summary["historical_selector_established"] is False and summary["official_transition"] is False,
            "wrong sensitivity or promoted conclusion")
    require(
        type(summary.get("main_lift_count")) is int
        and summary["main_lift_count"] == sum(row["lifts"] for row in main),
        "whole-arm count domain",
    )
    require(
        type(summary.get("canonical_omission_lifts")) is int
        and 0 <= summary["canonical_omission_lifts"] <= 11,
        "canonical count domain",
    )
    return summary


def _native_schema(value, *, structural_only=False):
    """Enforce exactly the supported keywords of the source-bound local schema.

    Structural validation precedes required-field access. Full validation
    follows explicit source/plan/protocol bindings so their established
    diagnostics remain stable. Neither phase establishes semantic validity.
    """
    try:
        document = capsule.strict_json(
            Path(__file__).with_name("native_schema.json").read_bytes()
        )
        allowed = {
            "$schema", "$id", "$defs", "$ref", "title", "type",
            "required", "properties", "additionalProperties",
            "propertyNames", "const", "enum", "pattern", "minimum",
        }

        def check(item, specification, location="$", depth=0):
            require(depth <= 64, "schema recursion bound at " + location)
            if specification is True:
                return
            require(specification is not False, "disallowed value at " + location)
            require(type(specification) is dict, "invalid schema object")
            require(
                all(key in allowed or key.startswith("x-")
                    for key in specification),
                "unsupported local schema keyword at " + location,
            )
            if "$ref" in specification:
                reference = specification["$ref"]
                require(
                    type(reference) is str
                    and reference.startswith("#/$defs/")
                    and reference.count("/") == 2,
                    "only local definition references are allowed",
                )
                name = reference[len("#/$defs/"):]
                require(name in document["$defs"], "unknown local definition")
                check(item, document["$defs"][name], location, depth + 1)
            if "type" in specification:
                names = specification["type"]
                names = [names] if type(names) is str else names
                require(type(names) is list and names, "invalid schema type")
                predicates = {
                    "object": type(item) is dict,
                    "array": type(item) is list,
                    "string": type(item) is str,
                    "integer": type(item) is int,
                    "boolean": type(item) is bool,
                    "null": item is None,
                    "number": type(item) in (int, float),
                }
                require(
                    all(name in predicates for name in names),
                    "unsupported schema type",
                )
                require(
                    any(predicates[name] for name in names),
                    "wrong JSON type at " + location,
                )
            if not structural_only:
                if "const" in specification:
                    require(
                        canonical(item) == canonical(specification["const"]),
                        "constant mismatch at " + location,
                    )
                if "enum" in specification:
                    require(
                        any(canonical(item) == canonical(option)
                            for option in specification["enum"]),
                        "enum mismatch at " + location,
                    )
                if "pattern" in specification and type(item) is str:
                    require(
                        re.search(specification["pattern"], item) is not None,
                        "pattern mismatch at " + location,
                    )
                if "minimum" in specification:
                    require(
                        type(item) in (int, float)
                        and item >= specification["minimum"],
                        "minimum mismatch at " + location,
                    )
            if type(item) is dict:
                required = specification.get("required", [])
                require(
                    all(name in item for name in required),
                    "missing required key at " + location,
                )
                properties = specification.get("properties", {})
                additional = specification.get("additionalProperties", True)
                for name, member in item.items():
                    require(type(name) is str, "non-string JSON key")
                    if "propertyNames" in specification:
                        check(
                            name, specification["propertyNames"],
                            location + ".<key>", depth + 1,
                        )
                    if name in properties:
                        check(
                            member, properties[name],
                            location + "." + name, depth + 1,
                        )
                    else:
                        require(
                            additional is not False,
                            "unexpected key at " + location + "." + name,
                        )
                        if type(additional) is dict:
                            check(
                                member, additional,
                                location + "." + name, depth + 1,
                            )

        check(value, document)
    except Exception as exc:
        raise ValueError("native raw schema: " + str(exc)) from exc


def verify(args, *, context_call=None):
    (
        root, directory, plan, launch, protocol,
        protocol_path, checker, supervisor,
    ) = (context_call or context)(args, False)
    allowed = set(TOP) | set(GENERATED)
    for path in directory.iterdir():
        require(
            path.name in allowed and path.is_file()
            and not path.is_symlink(),
            "unexpected or aliased native artifact",
        )
    require(
        all(
            (directory / name).is_file()
            and not (directory / name).is_symlink()
            for name in TOP
        ),
        "missing top-level artifact",
    )
    raw = read(directory / "raw-result.json")
    if type(raw) is dict:
        for forbidden_field in (
            "historical_selector_established", "official_transition",
        ):
            require(
                forbidden_field not in raw,
                "forbidden outcome promotion: unsupported outer "
                + forbidden_field,
            )
        if "attack_claimed" in raw:
            require(
                raw["attack_claimed"] is False,
                "forbidden outcome promotion",
            )
    _native_schema(raw, structural_only=True)
    require(
        raw["schema"] == "nist.fixed-x.native/v2"
        and raw["valid"] is True
        and raw["packaging_completed"] is True
        and raw["packaging_error"] is None
        and raw["semantic_error"] is None,
        "invalid native observation",
    )
    require(raw["attack_claimed"] is False, "forbidden outcome promotion")
    require(
        raw["experiment_id"] == plan["experiment_id"]
        and raw["run_id"] == launch["run_id"]
        and raw["plan_sha256"] == launch["plan_sha256"],
        "native identity/plan binding",
    )
    require(
        raw["protocol_path"] == protocol_path.relative_to(root).as_posix()
        and raw["protocol_file_sha256"] == digest(protocol_path)
        and raw["protocol_sha256"] == protocol["freeze"]["protocol_sha256"],
        "protocol binding",
    )
    require(raw["checker_sha256"] == CHECKER_SHA256, "source binding")
    _native_schema(raw)
    expected_names = {
        "driver.stdout.txt", "driver.stderr.txt",
        "driver-exit.json", "fixed-x.raw.json.gz",
    }
    require(
        set(raw["native_artifacts"]) == expected_names,
        "native sidecar closure",
    )
    require(
        all(
            digest(directory / name) == expected
            for name, expected in raw["native_artifacts"].items()
        ),
        "native sidecar digest",
    )
    exit_record = read(directory / "driver-exit.json")
    require(
        exit_record["child_call_attempted"] is True
        and exit_record["child_returncode_observed"] == 0
        and exit_record["error"] is None,
        "child failure",
    )
    expected_argv = [
        sys.executable, str(checker),
        "--protocol", str(protocol_path),
        "--out", str(directory / ".fixed-x-child"),
        "--native-plan", str(args.plan),
        "--native-out", str(directory),
    ]
    require(exit_record["argv"] == expected_argv, "child command binding")
    members = capsule.unpack(
        (directory / "fixed-x.raw.json.gz").read_bytes()
    )
    summary = verify_inner(
        members, expected_rows(root, protocol), protocol, launch,
    )
    require(summary == raw["summary"], "outer/raw summary disagreement")
    body = supervisor.fast_yaml.safe_load(
        (directory / "manifest.yaml").read_text()
    )["run"]
    metrics = {
        "canonical_omission_lifts": summary["canonical_omission_lifts"],
        "main_lift_count": summary["main_lift_count"],
        "planned_main_rows": 24,
    }
    require(
        body["attack_claimed"] is False
        and body["result"]["valid"] is True
        and body["result"]["certificate"]["kind"] == "none"
        and body["metrics"] == metrics,
        "manifest semantic disagreement",
    )
    if "envelope_completion" in body:
        completion = body["envelope_completion"]
        require(
            completion["completed_by"] == "tools/experiment_execution.py"
            and completion["driver_manifest_sha256"]
                == raw["driver_manifest_sha256"],
            "supervisor manifest provenance",
        )
        require(
            body["id"] == launch["run_id"]
            and body["experiment_id"] == plan["experiment_id"]
            and body["result"]["metrics"] == metrics,
            "completed manifest identity",
        )
    else:
        require(
            digest(directory / "manifest.yaml")
                == raw["driver_manifest_sha256"],
            "driver manifest digest",
        )
        if "id" in body:
            require(
                body["id"] == launch["run_id"]
                and body["experiment_id"] == plan["experiment_id"],
                "manifest identity",
            )
    print(json.dumps({
        "valid": True,
        "canonical_omission_lifts": summary["canonical_omission_lifts"],
        "main_lift_count": summary["main_lift_count"],
        "representations_checked": 24,
        "independent_review": False,
    }))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    args = parser.parse_args()
    try:
        return produce(args) if args.command == "run" else verify(args)
    except Exception:
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
