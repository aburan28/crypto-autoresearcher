#!/usr/bin/env python3
"""Synthetic engineering suite, lossless attempt recorder, and report renderer."""
import argparse
import base64
import contextlib
import copy
from datetime import datetime, timezone
import gzip
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import traceback
from types import SimpleNamespace
from unittest.mock import patch

import checker_v2 as checker
import native_bridge_v2 as bridge
import raw_capsule as capsule

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RECEIPTS = HERE / "test-receipts.json"
JSON_LIMIT = 1 << 20
PDF_LIMIT = 64 << 10
SOURCE_AMENDMENT = {'schema': 'nist.fixed-x.test-source-amendment/v1', 'task_id': 'TASK-20261027-3a4831', 'purpose': 'Measure native raw-schema, unsupported outer-promotion and output-directory alias behavior before any production correction.', 'previous_test_sha256': '4bc000d1f6251e4061b3edf9d09ca989b8f63c948baca360a674a487657bf2bd', 'previous_test_source': {'encoding': 'gzip+base64', 'length': 63301, 'sha256': '4bc000d1f6251e4061b3edf9d09ca989b8f63c948baca360a674a487657bf2bd', 'data': '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'}, 'production_bridge_sha256_unchanged': '3b75dfac014ed90e53128c7dd46c17346d00a23546163b1559f6c8bbfb33c0b4', 'prior_receipt_sha256': 'c1966929c771fc21630cafc48dffafc6523100b94d85d22a93b57c1fb373859a', 'added_test_outcomes': 'UNRUN'}
COUNTS = {
    "named_membership": 0,
    "scientific_runs": 0,
    "vm": 0,
    "legacy": 0,
    "storage": 0,
    "forbidden_process": 0,
    "synthetic_predicates": 0,
    "fake_cli_processes": 0,
    "child_calls": 0,
}
SAVED_RUN = subprocess.run
SAVED_POPEN = subprocess.Popen
EVALUATE = checker.evaluate
ARITHMETIC = bridge.arithmetic
CURRENT_RETAINED = []


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def write(path, value):
    path.write_bytes(capsule.canonical(value))


def encoded(data):
    return {
        "encoding": "gzip+base64",
        "sha256": capsule.sha(data),
        "length": len(data),
        "data": base64.b64encode(
            gzip.compress(data, compresslevel=9, mtime=0)
        ).decode(),
    }


def decoded(value):
    require(value["encoding"] == "gzip+base64", "receipt byte encoding")
    data = gzip.decompress(base64.b64decode(value["data"], validate=True))
    require(
        len(data) == value["length"]
        and capsule.sha(data) == value["sha256"],
        "receipt byte digest",
    )
    return data


def load_receipts():
    obj = json.loads(RECEIPTS.read_bytes())
    if "attempts_data" in obj:
        data = gzip.decompress(
            base64.b64decode(obj["attempts_data"], validate=True)
        )
        require(
            len(data) == obj["attempts_length"]
            and capsule.sha(data) == obj["attempts_sha256"],
            "receipt archive binding",
        )
        attempts = json.loads(data)
        require(len(attempts) == obj["attempt_count"], "receipt attempt count")
        return {"schema": obj["schema"], "attempts": attempts}
    require(isinstance(obj.get("attempts"), list), "receipt initialization")
    return obj


def append_receipt(attempt):
    records = load_receipts()
    attempt = {
        "sequence": len(records["attempts"]) + 1,
        **attempt,
    }
    records["attempts"].append(attempt)
    archive = capsule.canonical(records["attempts"])
    envelope = {
        "schema": records["schema"],
        "attempt_count": len(records["attempts"]),
        "attempts_encoding": "gzip+base64",
        "attempts_sha256": capsule.sha(archive),
        "attempts_length": len(archive),
        "attempts_data": base64.b64encode(
            gzip.compress(archive, compresslevel=9, mtime=0)
        ).decode(),
    }
    data = json.dumps(envelope, indent=2, sort_keys=True).encode() + b"\n"
    # Retention precedes size refusal. An oversized pending receipt is kept
    # task-local and must not be staged or represented as policy compliant.
    pending = HERE / ".test-receipts.pending"
    with pending.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(pending, RECEIPTS)
    if len(data) > JSON_LIMIT:
        raise RuntimeError(
            "Complete attempt retained in test-receipts.json, but its "
            "size exceeds 1MiB. Stop retries and do not stage it; return "
            "an additive artifact-route blocker. No storage call made."
        )
    return attempt["sequence"]


def retain_tree(base):
    retained = {}
    for path in sorted(base.rglob("*")):
        relative = path.relative_to(base).as_posix()
        if path.is_symlink():
            retained[relative] = {
                "type": "symlink", "target": os.readlink(path),
            }
        elif path.is_file():
            data = path.read_bytes()
            retained[relative] = {
                "type": "regular",
                "length": len(data),
                "sha256": capsule.sha(data),
                "base64": base64.b64encode(data).decode(),
            }
        elif path.is_dir():
            retained[relative] = {"type": "directory"}
        else:
            retained[relative] = {
                "type": "nonregular", "mode": path.lstat().st_mode,
            }
    return retained


@contextlib.contextmanager
def scratch(prefix="synthetic-"):
    with tempfile.TemporaryDirectory(prefix=prefix, dir=HERE) as name:
        base = Path(name)
        try:
            yield base
        finally:
            CURRENT_RETAINED.append({
                "temporary_path": str(base),
                "members": retain_tree(base),
            })


def guarded_evaluate(p, *args):
    if p != 101:
        COUNTS["named_membership"] += 1
        raise AssertionError("named membership forbidden")
    COUNTS["synthetic_predicates"] += 1
    return EVALUATE(p, *args)


def guarded_arithmetic(row):
    if int(row["p_hex"], 16) != 101:
        COUNTS["named_membership"] += 1
        raise AssertionError("named membership forbidden")
    return ARITHMETIC(row)


def forbidden(*args, **kwargs):
    COUNTS["forbidden_process"] += 1
    raise AssertionError("non-fixture process/network/storage forbidden")


def guarded(fn):
    with (
        patch.object(checker, "evaluate", side_effect=guarded_evaluate),
        patch.object(bridge, "arithmetic", side_effect=guarded_arithmetic),
        patch.object(subprocess, "run", side_effect=forbidden),
        patch.object(subprocess, "Popen", side_effect=forbidden),
        patch.object(os, "system", side_effect=forbidden),
        patch.object(socket, "socket", side_effect=forbidden),
    ):
        return fn()


def synthetic_workload():
    result = []
    for index in range(24):
        kind = (
            "published_self" if index < 10
            else "canonical_omission" if index < 21
            else "alternate_sign_sensitivity"
        )
        b = 1 if index < 10 else 3 if index < 21 else 4
        result.append({
            "row_id": "synthetic-" + str(index),
            "kind": kind,
            "name": "synthetic-" + str(index),
            "curve_uid": "synthetic:uid:" + str(index),
            "timestamp": 0,
            "ordinal": index,
            "previous_published_uid": None,
            "counterpart_name": "synthetic-control",
            "counterpart_uid": "synthetic:control",
            "counterpart_ordinal": 99,
            "p_hex": hex(101),
            "a_hex": hex(-3),
            "b_hex": hex(b),
            "n_hex": "0x1",
            "fixed_x_hex": "0x0",
            "fixed_y_hex": "0x1",
        })
    return result


def emit_child(path, protocol, launch, mode="valid"):
    path.mkdir()
    workload = synthetic_workload()
    write(path / "started.json", {
        "source_pins": protocol["extensions"]["source_pins"],
        "observed_commit": launch["authority"]["commit"],
    })
    write(path / "workload.json", workload)
    results = {}
    for arm in bridge.ARMS:
        if arm in ("fixed-x", "fixed-x-aa"):
            rows = []
            for item in workload:
                row = dict(item)
                row.update(checker.evaluate(*(
                    int(item[key], 16)
                    for key in (
                        "p_hex", "a_hex", "b_hex",
                        "fixed_x_hex", "fixed_y_hex",
                    )
                )))
                row["status"] = "succeeded"
                rows.append(row)
        elif arm == "positive":
            rows = [
                dict(
                    name=name, p=101, a=-3, b=b, x=0, y=y,
                    **checker.evaluate(101, -3, b, 0, y),
                )
                for name, b, y in (
                    ("positive-square", 1, 1),
                    ("zero-boundary", 0, 0),
                )
            ]
        else:
            rows = [
                dict(
                    name="negative-nonresidue",
                    p=101, a=-3, b=3, x=0, y=0,
                    **checker.evaluate(101, -3, 3, 0, 0),
                ),
                {
                    "name": "proves-too-much-full-point",
                    "positive": checker.evaluate(101, -3, 1, 0, 1),
                    "nearby_b4": checker.evaluate(101, -3, 4, 0, 1),
                    "passed": True,
                },
                {
                    "name": "source-binding-and-schema-corruption",
                    "passed": True,
                },
            ]
        results[arm] = rows
        write(path / (arm + ".json"), {
            "arm": arm, "status": "succeeded", "rows": rows,
        })
    exports = [{
        "run_id": arm + "-batch-0",
        "arm": arm,
        "instance_id": "0",
        "replicate": 0,
        "seed": 0,
        "warmup": False,
        "status": "succeeded",
        "verification": "verified",
        "tier": "none",
        "lift_count": sum(
            row.get("lifts") is True for row in results[arm]
        ),
        "evaluated_count": sum(
            "lifts" in row for row in results[arm]
        ),
        "binary_sha256": bridge.CHECKER_SHA256,
        "source_commit": launch["authority"]["commit"],
    } for arm in bridge.ARMS]
    (path / "rows.jsonl").write_bytes(
        b"\n".join(capsule.canonical(row) for row in exports) + b"\n"
    )
    write(path / "summary.json", {
        "schema": "nist.fixed-x.observation/v1",
        "valid": True,
        "protocol_sha256": protocol["freeze"]["protocol_sha256"],
        "canonical_omission_rows": 11,
        "canonical_omission_lifts": 0,
        "main_lift_count": 13,
        "canonical_witness_uids": [],
        "alternate_sign_sensitivity": [
            row for row in results["fixed-x"]
            if row["kind"] == "alternate_sign_sensitivity"
        ],
        "historical_selector_established": False,
        "official_transition": False,
    })
    (path / "stdout.txt").write_bytes(b"inner\x00stdout\xff\n")
    (path / "stderr.txt").write_bytes(b"inner\r\nstderr\xfe")
    if mode == "malformed":
        (path / "summary.json").write_bytes(b"{malformed\xff")
    if mode == "partial":
        (path / "fixed-x-aa.json").unlink()


class Fixture:
    def __init__(self, base):
        self.root = base
        self.directory = base / "out"
        self.directory.mkdir()
        self.protocol_path = base / "protocol.json"
        self.protocol = {
            "execution": {"timeout_seconds": 1},
            "extensions": {"source_pins": {"synthetic": "0" * 64}},
            "freeze": {"protocol_sha256": "1" * 64},
        }
        write(self.protocol_path, self.protocol)
        self.plan = {"experiment_id": "EXP-SYNTHETIC-000000"}
        self.launch = {
            "run_id": "RUN-SYNTHETIC-000000",
            "plan_sha256": "2" * 64,
            "authority": {"commit": "3" * 40},
        }
        self.args = SimpleNamespace(
            out=self.directory,
            plan=base / "plan.json",
            protocol=self.protocol_path,
        )
        self.supervisor = SimpleNamespace(
            fast_yaml=SimpleNamespace(safe_load=json.loads),
        )
        self.calls = 0

    def context(self, args, running):
        return (
            self.root, self.directory, self.plan, self.launch,
            self.protocol, self.protocol_path,
            HERE / "checker_v2.py", self.supervisor,
        )

    def child(self, argv, **kwargs):
        COUNTS["child_calls"] += 1
        self.calls += 1
        emit_child(
            Path(argv[argv.index("--out") + 1]),
            self.protocol,
            self.launch,
        )
        return subprocess.CompletedProcess(
            argv, 0, b"driver\xff\x00\r\n", b"driver\xfe\x00",
        )

    def produce(self, child=None):
        with patch.object(
            bridge, "expected_rows", return_value=synthetic_workload(),
        ):
            return bridge.produce(
                self.args,
                context_call=self.context,
                child_call=child or self.child,
            )

    def check(self):
        with patch.object(
            bridge, "expected_rows", return_value=synthetic_workload(),
        ):
            return bridge.verify(self.args, context_call=self.context)

    def resign(self, members):
        records = [{
            "name": name,
            "type": "regular",
            "length": len(data),
            "sha256": capsule.sha(data),
            "base64": base64.b64encode(data).decode(),
        } for name, data in sorted(members.items())]
        data = capsule.encode(records)
        path = self.directory / "fixed-x.raw.json.gz"
        path.write_bytes(data)
        raw = bridge.read(self.directory / "raw-result.json")
        raw["native_artifacts"][path.name] = capsule.sha(data)
        if "summary.json" in members:
            try:
                raw["summary"] = capsule.strict_json(
                    members["summary.json"]
                )
            except ValueError:
                pass
        write(self.directory / "raw-result.json", raw)


def expect_gate(fn, text):
    try:
        fn()
    except (ValueError, AssertionError, KeyError, TypeError) as exc:
        require(
            text in str(exc),
            "wrong gate expected " + text + " got " + repr(exc),
        )
        return {"refusal": str(exc), "intended_gate": text}
    raise AssertionError("invalid fixture accepted: " + text)


def ordinary(fixture):
    require(fixture.produce() == 0, "ordinary production control")
    require(fixture.check() == 0, "ordinary checking control")
    return {"ordinary_producer_and_checker_passed": True}


def fixture_case(fn):
    with scratch() as base:
        fixture = Fixture(base)
        ordinary(fixture)
        return fn(fixture)


def mutate_json(members, name, fn):
    value = capsule.strict_json(members[name])
    fn(value)
    members[name] = capsule.canonical(value)


def run_suite():
    results = []

    def case(name, fn):
        CURRENT_RETAINED.clear()
        stdout, stderr = io.StringIO(), io.StringIO()
        try:
            with (
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                value = fn()
            result = {
                "name": name, "outcome": "PASS", "detail": value,
            }
        except Exception as exc:
            result = {
                "name": name,
                "outcome": "FAIL",
                "error": repr(exc),
                "traceback": traceback.format_exc(),
            }
        result.update(
            stdout=stdout.getvalue(),
            stderr=stderr.getvalue(),
            retained_fixtures=copy.deepcopy(CURRENT_RETAINED),
        )
        results.append(result)

    def good(fixture):
        require(
            {path.name for path in fixture.directory.iterdir()}
            == set(bridge.TOP),
            "top-level inventory",
        )
        members = capsule.unpack(
            (fixture.directory / "fixed-x.raw.json.gz").read_bytes()
        )
        require(
            members["stdout.txt"] == b"inner\x00stdout\xff\n",
            "lossless raw stdout",
        )
        require(
            members["stderr.txt"] == b"inner\r\nstderr\xfe",
            "lossless raw stderr",
        )
        require(
            (fixture.directory / "driver.stdout.txt").read_bytes()
            == b"driver\xff\x00\r\n",
            "lossless driver stdout",
        )
        require(
            (fixture.directory / "driver.stderr.txt").read_bytes()
            == b"driver\xfe\x00",
            "lossless driver stderr",
        )
        summary = bridge.read(
            fixture.directory / "raw-result.json"
        )["summary"]
        require(
            summary["main_lift_count"] == 13
            and summary["canonical_omission_lifts"] == 0,
            "distinct count domains",
        )
        return {
            "ordinary_valid": True,
            "all_arithmetic_domain": "explicit synthetic p101",
            "main_fixture_count": 13,
            "canonical_fixture_count": 0,
        }

    case(
        "ordinary_lossless_wrapper_to_checker",
        lambda: fixture_case(good),
    )

    def refusal():
        fixture_case(good)
        with scratch() as base:
            fixture = Fixture(base)

            def denied(*args):
                raise ValueError("authorization refused")

            result = expect_gate(
                lambda: bridge.produce(
                    fixture.args,
                    context_call=denied,
                    child_call=fixture.child,
                ),
                "authorization refused",
            )
            require(
                fixture.calls == 0
                and not list(fixture.directory.iterdir()),
                "child invoked after refusal",
            )
            return result

    case("authorization_before_child", refusal)

    def member_case(name, mutator, gate):
        def action(fixture):
            members = capsule.unpack(
                (fixture.directory / "fixed-x.raw.json.gz").read_bytes()
            )
            mutator(members)
            fixture.resign(members)
            return expect_gate(fixture.check, gate)
        case(name, lambda: fixture_case(action))

    member_case(
        "missing_raw",
        lambda members: members.pop("workload.json"),
        "incomplete raw member set",
    )
    member_case(
        "extra_raw",
        lambda members: members.update({"unexpected.json": b"{}"}),
        "unexpected or duplicate raw member",
    )
    member_case(
        "changed_raw_json",
        lambda members: members.update({"fixed-x.json": b"{"}),
        "Expecting",
    )

    def identical_semantic(members):
        for arm in ("fixed-x", "fixed-x-aa"):
            mutate_json(
                members, arm + ".json",
                lambda obj: obj["rows"][0].update(symbol=-1),
            )

    member_case(
        "identical_resigned_invalid_aa_before_equality",
        identical_semantic,
        "individual semantic arithmetic",
    )
    member_case(
        "aa_semantically_valid_extra_field_requires_equality",
        lambda members: mutate_json(
            members, "fixed-x-aa.json",
            lambda obj: obj["rows"][0].update(
                synthetic_extra_annotation="different"
            ),
        ),
        "A/A equality",
    )
    for arm, index, field, value in (
        ("positive", 0, "symbol", -1),
        ("positive", 1, "lifts", False),
        ("negative", 0, "symbol", 1),
    ):
        member_case(
            "individual_control_" + arm + "_" + str(index),
            lambda members, a=arm, i=index, k=field, v=value:
                mutate_json(
                    members, a + ".json",
                    lambda obj: obj["rows"][i].update({k: v}),
                ),
            "fixture arithmetic failed",
        )
    member_case(
        "circularity_semantic_failure",
        lambda members: mutate_json(
            members, "negative.json",
            lambda obj: obj["rows"][1]["nearby_b4"].update(
                full_point_member=True
            ),
        ),
        "circularity fixture changed",
    )
    member_case(
        "source_schema_control_flag_failure",
        lambda members: mutate_json(
            members, "negative.json",
            lambda obj: obj["rows"][2].update(passed=False),
        ),
        "fail-closed control absent",
    )
    member_case(
        "canonical_count_conflation",
        lambda members: mutate_json(
            members, "summary.json",
            lambda obj: obj.update(
                canonical_omission_lifts=obj["main_lift_count"]
            ),
        ),
        "wrong canonical summary",
    )
    member_case(
        "whole_arm_count_conflation",
        lambda members: mutate_json(
            members, "summary.json",
            lambda obj: obj.update(
                main_lift_count=obj["canonical_omission_lifts"]
            ),
        ),
        "whole-arm count domain",
    )
    for field in ("historical_selector_established", "official_transition"):
        member_case(
            "promotion_" + field,
            lambda members, key=field: mutate_json(
                members, "summary.json",
                lambda obj: obj.update({key: True}),
            ),
            "wrong sensitivity or promoted conclusion",
        )
    for field in ("curve_uid", "ordinal", "counterpart_uid"):
        def mutation(members, key=field):
            for arm in ("fixed-x", "fixed-x-aa"):
                mutate_json(
                    members, arm + ".json",
                    lambda obj: obj["rows"][0].update({key: "wrong"}),
                )
        member_case(
            "identity_chronology_" + field,
            mutation,
            "individual identity/chronology",
        )
    member_case(
        "input_binding",
        lambda members: mutate_json(
            members, "started.json",
            lambda obj: obj.update(source_pins={}),
        ),
        "wrong raw input",
    )
    member_case(
        "observed_commit_binding",
        lambda members: mutate_json(
            members, "started.json",
            lambda obj: obj.update(observed_commit="wrong"),
        ),
        "wrong raw input",
    )

    def export_mutation(members):
        rows = [
            capsule.strict_json(line)
            for line in members["rows.jsonl"].splitlines()
        ]
        rows[0]["lift_count"] = 0
        members["rows.jsonl"] = (
            b"\n".join(capsule.canonical(row) for row in rows) + b"\n"
        )

    member_case(
        "export_summary_domain_disagreement",
        export_mutation,
        "export batch metric differs",
    )
    for key in (
        "run_id", "plan_sha256", "experiment_id", "checker_sha256",
        "protocol_file_sha256", "protocol_sha256",
    ):
        def outer(fixture, field=key):
            path = fixture.directory / "raw-result.json"
            value = bridge.read(path)
            value[field] = "wrong"
            write(path, value)
            gate = (
                "source binding" if field == "checker_sha256"
                else "protocol binding" if field.startswith("protocol")
                else "native identity/plan binding"
            )
            return expect_gate(fixture.check, gate)
        case(
            "outer_binding_" + key,
            lambda action=outer: fixture_case(action),
        )

    def raw_schema_case(mode):
        def action(fixture):
            path = fixture.directory / "raw-result.json"
            value = bridge.read(path)
            if mode == "extra_key":
                value["unexpected_native_field"] = True
            elif mode == "missing_required":
                del value["driver_manifest_sha256"]
            elif mode == "wrong_type":
                value["summary"] = []
            else:
                raise AssertionError("unknown raw-schema mutation")
            write(path, value)
            return expect_gate(fixture.check, "native raw schema")
        return fixture_case(action)

    for schema_mode in ("extra_key", "missing_required", "wrong_type"):
        case(
            "native_raw_schema_" + schema_mode,
            lambda selected=schema_mode: raw_schema_case(selected),
        )

    def unsupported_outer_promotion(field):
        def action(fixture):
            path = fixture.directory / "raw-result.json"
            value = bridge.read(path)
            value[field] = True
            write(path, value)
            return expect_gate(fixture.check, "forbidden outcome promotion")
        return fixture_case(action)

    for promotion_field in (
        "historical_selector_established", "official_transition",
    ):
        case(
            "outer_promotion_" + promotion_field,
            lambda selected=promotion_field:
                unsupported_outer_promotion(selected),
        )

    def outer_promotion(fixture):
        path = fixture.directory / "raw-result.json"
        value = bridge.read(path)
        value["attack_claimed"] = True
        write(path, value)
        return expect_gate(fixture.check, "forbidden outcome promotion")

    case(
        "outer_attack_claim_promotion",
        lambda: fixture_case(outer_promotion),
    )

    def sidecar(fixture):
        (fixture.directory / "driver.stdout.txt").write_bytes(b"changed")
        return expect_gate(fixture.check, "native sidecar digest")

    case("outer_sidecar_corruption", lambda: fixture_case(sidecar))

    def outer_summary(fixture):
        path = fixture.directory / "raw-result.json"
        value = bridge.read(path)
        value["summary"]["canonical_omission_lifts"] = 1
        write(path, value)
        return expect_gate(fixture.check, "outer/raw summary disagreement")

    case(
        "outer_summary_disagreement",
        lambda: fixture_case(outer_summary),
    )

    def capsule_case(transform, gate):
        def action(fixture):
            path = fixture.directory / "fixed-x.raw.json.gz"
            path.write_bytes(transform(path.read_bytes()))
            raw_path = fixture.directory / "raw-result.json"
            value = bridge.read(raw_path)
            value["native_artifacts"][path.name] = capsule.sha(
                path.read_bytes()
            )
            write(raw_path, value)
            return expect_gate(fixture.check, gate)
        return fixture_case(action)

    case(
        "truncated_capsule",
        lambda: capsule_case(
            lambda data: data[:-7], "capsule gzip corruption",
        ),
    )
    case(
        "corrupt_capsule",
        lambda: capsule_case(
            lambda data: b"bad-gzip", "capsule gzip corruption",
        ),
    )
    case(
        "oversized_capsule",
        lambda: capsule_case(
            lambda data: gzip.compress(
                b"x" * (capsule.MAX_BYTES + 1), mtime=0
            ),
            "capsule decompression bound",
        ),
    )

    def modify_capsule(data, fn):
        obj = capsule.strict_json(gzip.decompress(data))
        fn(obj["members"])
        return capsule.encode(obj["members"], obj["capture_errors"])

    case(
        "duplicate_member",
        lambda: capsule_case(
            lambda data: modify_capsule(
                data, lambda rows: rows.append(copy.deepcopy(rows[0])),
            ),
            "unexpected or duplicate raw member",
        ),
    )
    for name in ("../escape", "/absolute", "a/../escape", "a\\escape"):
        case(
            "unsafe_member_" + name,
            lambda member_name=name: capsule_case(
                lambda data: modify_capsule(
                    data,
                    lambda rows: rows[0].update(name=member_name),
                ),
                "unsafe member name",
            ),
        )
    case(
        "capsule_symlink",
        lambda: capsule_case(
            lambda data: modify_capsule(
                data, lambda rows: rows[0].update(type="symlink"),
            ),
            "nonregular raw member",
        ),
    )
    case(
        "capsule_member_digest",
        lambda: capsule_case(
            lambda data: modify_capsule(
                data, lambda rows: rows[0].update(sha256="0" * 64),
            ),
            "raw member length/digest",
        ),
    )

    def raw_symlink_capture():
        fixture_case(good)
        with scratch() as base:
            raw = base / "raw"
            raw.mkdir()
            (raw / "stdout.txt").write_bytes(b"safe")
            (raw / "stderr.txt").symlink_to(raw / "stdout.txt")
            data = capsule.pack(raw)
            require(b"safe" not in data, "unexpected uncompressed capsule")
            require(
                capsule.strict_json(gzip.decompress(data))[
                    "capture_errors"
                ][0]["kind"] == "symlink",
                "symlink capture not recorded",
            )
            return expect_gate(
                lambda: capsule.unpack(data), "nonregular raw member",
            )

    case("actual_pack_symlink_refusal", raw_symlink_capture)

    def aliased(fixture):
        path = fixture.directory / "driver.stderr.txt"
        path.unlink()
        path.symlink_to(fixture.directory / "driver.stdout.txt")
        return expect_gate(
            fixture.check, "unexpected or aliased native artifact",
        )

    case("aliased_sidecar", lambda: fixture_case(aliased))
    case(
        "reused_output",
        lambda: fixture_case(
            lambda fixture: expect_gate(
                fixture.produce, "refusing existing driver output",
            )
        ),
    )

    def failed_child(mode):
        fixture_case(good)
        with scratch() as base:
            fixture = Fixture(base)

            def child(argv, **kwargs):
                COUNTS["child_calls"] += 1
                path = Path(argv[argv.index("--out") + 1])
                if mode == "oserror":
                    raise OSError("synthetic invocation error")
                emit_child(
                    path, fixture.protocol, fixture.launch,
                    mode if mode in ("malformed", "partial") else "valid",
                )
                if mode == "timeout":
                    raise subprocess.TimeoutExpired(
                        argv, 1,
                        output=b"partial\xff\x00", stderr=b"partial\xfe",
                    )
                return subprocess.CompletedProcess(
                    argv, 7 if mode == "nonzero" else 0,
                    b"observed\xff", b"error\xfe",
                )

            require(fixture.produce(child) == 2, "failed child promoted")
            raw = bridge.read(fixture.directory / "raw-result.json")
            require(raw["valid"] is False, "invalid child valid flag")
            require(
                (fixture.directory / "fixed-x.raw.json.gz").is_file(),
                "partial capsule lost",
            )
            detail = expect_gate(
                fixture.check, "invalid native observation",
            )
            if mode == "timeout":
                require(
                    (fixture.directory / "driver.stdout.txt").read_bytes()
                    == b"partial\xff\x00",
                    "timeout partial bytes lost",
                )
            detail["exit_record"] = bridge.read(
                fixture.directory / "driver-exit.json"
            )
            return detail

    for mode in ("nonzero", "timeout", "oserror", "malformed", "partial"):
        case("child_" + mode, lambda selected=mode: failed_child(selected))

    def secondary_failure():
        fixture_case(good)
        with scratch() as base:
            fixture = Fixture(base)
            with patch.object(
                capsule, "pack",
                side_effect=OSError("injected packaging failure"),
            ):
                require(
                    fixture.produce() == 2, "packaging error promoted",
                )
            require(
                (
                    fixture.directory / ".fixed-x-child" / "stdout.txt"
                ).read_bytes() == b"inner\x00stdout\xff\n",
                "secondary recovery lost raw bytes",
            )
            raw = bridge.read(fixture.directory / "raw-result.json")
            require(
                raw["packaging_error"] is not None
                and raw["valid"] is False,
                "secondary failure absent",
            )
            return {"native_returncode": 2, "raw_tree_retained": True}

    case("secondary_packaging_failure_retained", secondary_failure)

    def native_context_checks():
        with scratch("synthetic-context-") as root:
            src = root / "research" / "study" / "tasks" / "id"
            src.mkdir(parents=True)
            for name in (
                "checker_v2.py", "native_bridge_v2.py",
                "raw_capsule.py", "native_schema.json",
            ):
                shutil.copyfile(HERE / name, src / name)
            directory = (
                root / "experiments" / "synthetic" / "runs" / "synthetic"
            )
            directory.mkdir(parents=True)
            protocol = {
                "freeze": {"status": "frozen"},
                "extensions": {"source_pins": {}},
            }
            protocol["freeze"]["protocol_sha256"] = capsule.sha(
                capsule.canonical({
                    key: value for key, value in protocol.items()
                    if key != "freeze"
                })
            )
            protocol_path = root / "protocol.json"
            write(protocol_path, protocol)
            authority = {
                "owner": "synthetic-owner", "epoch": 1, "commit": "a" * 40,
            }
            trial = {
                "id": "synthetic", "run_id": "synthetic",
                "artifacts": list(bridge.TOP),
            }
            plan = {
                "trials": [trial],
                "input_sha256": {
                    "protocol.json": bridge.digest(protocol_path),
                },
                "source_sha256": {
                    path.relative_to(root).as_posix(): bridge.digest(path)
                    for path in src.iterdir()
                },
            }
            plan_path = root / "plan.json"
            write(plan_path, plan)
            launch = {
                "plan_sha256": bridge.digest(plan_path),
                "trial_id": "synthetic",
                "run_id": "synthetic",
                "authority": authority,
            }
            write(directory / "launch.json", launch)
            supervisor = SimpleNamespace(
                load_plan=lambda *args: plan,
                run_root=lambda *args: directory,
                authorize=lambda *args: dict(authority),
            )
            args = SimpleNamespace(
                out=directory, plan=plan_path, protocol=protocol_path,
            )

            def fake_git(argv, **kwargs):
                require(
                    argv[:3] == ["git", "-C", str(root)]
                    and argv[3] == "show",
                    "unexpected synthetic Git seam",
                )
                return subprocess.CompletedProcess(
                    argv, 0,
                    (root / argv[4].split(":", 1)[1]).read_bytes(), b"",
                )

            with (
                patch.object(
                    bridge, "__file__", str(src / "native_bridge_v2.py"),
                ),
                patch.object(
                    bridge.importlib, "import_module",
                    return_value=supervisor,
                ),
                patch.object(subprocess, "run", side_effect=fake_git),
            ):
                bridge.context(args, True)
                alias_directory = directory.with_name("synthetic-output-alias")
                alias_directory.symlink_to(directory, target_is_directory=True)
                alias_args = SimpleNamespace(
                    out=alias_directory,
                    plan=plan_path,
                    protocol=protocol_path,
                )
                alias_refusal = expect_gate(
                    lambda: bridge.context(alias_args, True),
                    "aliased native output",
                )
                require(
                    directory.is_dir() and not directory.is_symlink(),
                    "ordinary native output changed by alias control",
                )
                bridge.context(args, True)
                relative = (src / "native_bridge_v2.py").relative_to(
                    root
                ).as_posix()
                original_source = plan["source_sha256"][relative]
                plan["source_sha256"][relative] = "0" * 64
                source_refusal = expect_gate(
                    lambda: bridge.context(args, True),
                    "source absent or changed",
                )
                plan["source_sha256"][relative] = original_source
                bridge.context(args, True)
                original_plan_hash = launch["plan_sha256"]
                launch["plan_sha256"] = "wrong"
                write(directory / "launch.json", launch)
                plan_refusal = expect_gate(
                    lambda: bridge.context(args, True),
                    "launch/plan mismatch",
                )
                launch["plan_sha256"] = original_plan_hash
                write(directory / "launch.json", launch)
                bridge.context(args, True)
                launch["run_id"] = "wrong"
                write(directory / "launch.json", launch)
                run_refusal = expect_gate(
                    lambda: bridge.context(args, True),
                    "run identity mismatch",
                )
                launch["run_id"] = "synthetic"
                write(directory / "launch.json", launch)
                bridge.context(args, True)
                with patch.object(
                    supervisor, "authorize",
                    return_value={**authority, "epoch": 2},
                ):
                    auth_refusal = expect_gate(
                        lambda: bridge.context(args, True),
                        "native authority changed",
                    )
                bridge.context(args, True)
                plan["input_sha256"]["protocol.json"] = "wrong"
                protocol_refusal = expect_gate(
                    lambda: bridge.context(args, True),
                    "protocol is not exact bound plan input",
                )
            return {
                "ordinary_context_passed": True,
                "output_directory_alias": alias_refusal,
                "source": source_refusal,
                "plan": plan_refusal,
                "run": run_refusal,
                "authorization": auth_refusal,
                "protocol": protocol_refusal,
                "seams": (
                    "Explicit synthetic load_plan, run_root, authorize "
                    "and Git committed-byte source. Production scientific "
                    "admission is UNRUN."
                ),
            }

    case("actual_context_identity_guards", native_context_checks)

    def metadata_only():
        source_inputs = json.loads((
            ROOT / "coordination/goals/GOAL-NISTSEED-ab8949/"
            "batches/BATCH-05b760/source-inputs.json"
        ).read_bytes())
        pins = source_inputs["input_sha256"]
        protocol = {"extensions": {"source_pins": pins}}

        def fake_git(argv, **kwargs):
            require(
                argv[:3] == ["git", "-C", str(ROOT)]
                and argv[3] == "show",
                "unexpected metadata Git seam",
            )
            return subprocess.CompletedProcess(
                argv, 0,
                (ROOT / argv[4].split(":", 1)[1]).read_bytes(), b"",
            )

        before = COUNTS["synthetic_predicates"]
        with patch.object(subprocess, "run", side_effect=fake_git):
            rows = bridge.expected_rows(ROOT, protocol)
        require(
            len(rows) == 24
            and len({row["curve_uid"] for row in rows}) == 24,
            "metadata scope",
        )
        require(
            COUNTS["synthetic_predicates"] == before,
            "metadata invoked arithmetic",
        )
        broken = copy.deepcopy(protocol)
        broken["extensions"]["source_pins"][next(iter(pins))] = "wrong"
        pin_refusal = expect_gate(
            lambda: bridge.expected_rows(ROOT, broken),
            "wrong fixed input closure",
        )
        require(
            checker.bound_json(b"{}", capsule.sha(b"{}")) == {},
            "ordinary binding fixture",
        )
        source_refusal = expect_gate(
            lambda: checker.bound_json(b"{}\n", capsule.sha(b"{}")),
            "source SHA-256 mismatch",
        )
        documents = [
            json.loads((ROOT / name).read_bytes()) for name in pins
        ]
        checker.plan(*documents)
        missing = copy.deepcopy(documents)
        del missing[0]["candidate_rows"][0]["p_hex"]
        schema_refusal = expect_gate(
            lambda: checker.plan(*missing), "p_hex",
        )
        return {
            "metadata_rows": len(rows),
            "named_memberships_evaluated": 0,
            "pin_refusal": pin_refusal,
            "source_refusal": source_refusal,
            "schema_refusal": schema_refusal,
            "Git_seam_is_synthetic": True,
        }

    case("full_named_identity_metadata_without_predicates", metadata_only)

    def complete(fixture):
        sys.path.insert(0, str(ROOT / "tools"))
        native = importlib.import_module("experiment_execution")
        for name in bridge.GENERATED:
            if name != "execution-receipt.json":
                (fixture.directory / name).write_bytes(
                    b"{}" if name == "environment.json"
                    else b"synthetic capture\n"
                )
        plan = {
            **fixture.plan,
            "task_id": "TASK-SYNTHETIC-000000",
            "approved_by": "DEC-SYNTHETIC-000000",
        }
        trial = {
            "id": "synthetic",
            "run_id": fixture.launch["run_id"],
            "parameters": {"synthetic": True},
            "seed": 0,
        }
        before = {
            name: (fixture.directory / name).read_bytes()
            for name in bridge.GENERATED
            if (fixture.directory / name).exists()
        }
        original = (fixture.directory / "manifest.yaml").read_bytes()
        result = native.complete_manifest(
            fixture.directory,
            plan,
            "synthetic-plan.json",
            fixture.launch["plan_sha256"],
            trial,
            fixture.launch["authority"],
            ["synthetic-driver"],
            ["synthetic-checker"],
            "2026-10-27T00:00:00+00:00",
            "2026-10-27T00:00:01+00:00",
        )
        require(
            result["action"] == "completed"
            and result["driver_manifest_text"].encode() == original,
            "manifest completion provenance",
        )
        require(
            all(
                (fixture.directory / name).read_bytes() == data
                for name, data in before.items()
            ),
            "supervisor companion mutated",
        )
        require(
            native.manifest_schema_errors(
                fixture.directory / "manifest.yaml"
            ) == [],
            "completed schema invalid",
        )
        fixture.supervisor = native
        require(
            fixture.check() == 0,
            "checker rejected documented completion",
        )
        return {
            "actual_complete_manifest": result,
            "supervisor_companions_unchanged": True,
        }

    case(
        "actual_complete_manifest_compatibility",
        lambda: fixture_case(complete),
    )

    def explicit_fake_cli():
        fixture_case(good)
        with scratch("synthetic-cli-") as base:
            argv = [
                sys.executable, "-B", str(Path(__file__).resolve()),
                "--fake-driver", str(base),
            ]
            COUNTS["fake_cli_processes"] += 1
            with patch.object(subprocess, "Popen", SAVED_POPEN):
                process = SAVED_RUN(
                    argv, capture_output=True, timeout=30, cwd=ROOT,
                    env={
                        **os.environ, "PYTHONDONTWRITEBYTECODE": "1",
                    },
                )
            require(
                process.returncode == 0,
                "explicit fake CLI failed: " + repr(process.stderr),
            )
            lines = process.stdout.splitlines()
            report = json.loads(lines[-1])
            require(report["explicit_fake"] is True, "fake CLI marker")
            for key in (
                "named_membership", "scientific_runs", "vm", "legacy",
                "storage", "forbidden_process",
            ):
                require(
                    report["guard_totals"][key] == 0,
                    "fake CLI forbidden guard: " + key,
                )
            inventory = sorted(
                path.name for path in (base / "out").iterdir()
            )
            require(
                inventory == sorted(bridge.TOP),
                "post-exit CLI inventory",
            )
            return {
                "argv": argv,
                "returncode": process.returncode,
                "stdout": encoded(process.stdout),
                "stderr": encoded(process.stderr),
                "post_exit_inventory": inventory,
                "child_report": report,
            }

    case("explicit_fake_cli_after_process_exit", explicit_fake_cli)

    def zero_forbidden():
        for key in (
            "named_membership", "scientific_runs", "vm",
            "legacy", "storage", "forbidden_process",
        ):
            require(COUNTS[key] == 0, "forbidden guard total: " + key)
        return dict(COUNTS)

    case("zero_forbidden_guard_totals", zero_forbidden)
    return {
        "schema": "nist.fixed-x.synthetic-suite/v2",
        "source_amendment": SOURCE_AMENDMENT,
        "results": results,
        "passed": sum(row["outcome"] == "PASS" for row in results),
        "failed": sum(row["outcome"] == "FAIL" for row in results),
        "guard_totals": COUNTS,
        "scientific_execution": False,
        "scope": (
            "Guarded source engineering. Only explicit p101 arithmetic; "
            "named-domain work is metadata reconstruction only."
        ),
    }


def record_suite():
    argv = [sys.executable, "-B", str(Path(__file__).resolve())]
    started = now()
    try:
        process = SAVED_RUN(
            argv, capture_output=True, timeout=120, cwd=ROOT,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        stdout, stderr = process.stdout, process.stderr
        returncode, error = process.returncode, None
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b"", exc.stderr or b""
        returncode, error = None, "suite_watchdog"
    except OSError as exc:
        stdout, stderr = b"", b""
        returncode, error = None, repr(exc)
    git_records = []
    for git_args in (
        ["rev-parse", "HEAD"],
        ["status", "--porcelain", "--untracked-files=normal"],
    ):
        command = ["git", "-C", str(ROOT), *git_args]
        try:
            result = SAVED_RUN(
                command, capture_output=True, timeout=15, cwd=ROOT,
            )
            git_records.append({
                "argv": command,
                "returncode": result.returncode,
                "stdout": encoded(result.stdout),
                "stderr": encoded(result.stderr),
            })
        except Exception as exc:
            git_records.append({"argv": command, "error": repr(exc)})
    source_hashes = {
        path.name: capsule.sha(path.read_bytes())
        for path in HERE.iterdir()
        if path.suffix == ".py" or path.name == "native_schema.json"
    }
    sequence = append_receipt({
        "kind": "synthetic_suite",
        "argv": argv,
        "started_at": started,
        "finished_at": now(),
        "returncode": returncode,
        "error": error,
        "stdout": encoded(stdout),
        "stderr": encoded(stderr),
        "source_sha256": source_hashes,
        "git_records": git_records,
        "python": sys.version,
        "platform": platform.platform(),
        "execution_owner": (
            "Parent executing executor-authored guarded engineering suite."
        ),
        "watchdog_seconds": 120,
    })
    print(json.dumps({
        "recorded_sequence": sequence,
        "returncode": returncode,
        "stdout_sha256": capsule.sha(stdout),
        "stderr_sha256": capsule.sha(stderr),
        "receipt_bytes": RECEIPTS.stat().st_size,
    }))
    return 0 if returncode == 0 else 1


def parsed_suite(attempt):
    try:
        stdout = decoded(attempt["stdout"])
        obj = json.loads(stdout.splitlines()[-1])
        require(
            obj["schema"] == "nist.fixed-x.synthetic-suite/v2",
            "suite schema",
        )
        return obj
    except Exception as exc:
        return {
            "parse_error": repr(exc),
            "passed": None,
            "failed": None,
            "results": [],
            "guard_totals": None,
        }


def render_report():
    started = now()
    records = load_receipts()
    suites = [
        row for row in records["attempts"]
        if row.get("kind") == "synthetic_suite"
    ]
    latest = parsed_suite(suites[-1]) if suites else None
    source_inputs = json.loads((
        ROOT / "coordination/goals/GOAL-NISTSEED-ab8949/"
        "batches/BATCH-05b760/source-inputs.json"
    ).read_bytes())
    hashes = {
        name: capsule.sha((HERE / name).read_bytes())
        for name in (
            "checker_v2.py", "native_bridge_v2.py", "raw_capsule.py",
            "native_schema.json", "test_native_bridge.py",
            "source-lineage.json", "protocol-amendment-draft.json",
        )
    }
    history = []
    for attempt in suites:
        parsed = parsed_suite(attempt)
        history.append(
            "Sequence {seq}: exit {rc}; passed {passed}; failed {failed}; "
            "stdout {digest}.".format(
                seq=attempt["sequence"],
                rc=attempt["returncode"],
                passed=parsed["passed"],
                failed=parsed["failed"],
                digest=attempt["stdout"]["sha256"],
            )
        )
    failures = []
    if latest:
        failures = [
            row["name"] + ": " + row.get("error", "failure")
            for row in latest["results"] if row["outcome"] != "PASS"
        ]
    outcome = (
        "UNRUN: no retained synthetic-suite invocation exists."
        if not suites else
        "Latest retained invocation: exit {}; passed {}; failed {}.".format(
            suites[-1]["returncode"],
            latest["passed"], latest["failed"],
        )
    )
    guards = (
        json.dumps(latest["guard_totals"], sort_keys=True)
        if latest else "UNRUN"
    )
    report = (
        "# Fixed-x native source engineering\n\n"
        "TASK-20261027-3a4831. Observations below describe guarded "
        "synthetic engineering only. Scientific execution, scientific "
        "readiness and official state transitions are not established.\n\n"
        + outcome + "\n\n"
        "The fixture has 24 explicit p101 representation rows: ten self "
        "rows, eleven canonical-domain rows and three sensitivity rows. "
        "Its constructed main count is 13 and canonical count is 0; "
        "these fixture values exercise distinct count domains. Named "
        "inputs are inspected only for identity and chronology metadata. "
        "The scientific contract remains 21 canonical identities, "
        "24 representation rows, four correlated whole-batch export "
        "rows, and the original broader 69-position limitation.\n\n"
        "Actual guard totals from the latest complete suite JSON: "
        + guards + "\n\n"
        "Retained invocation history:\n\n"
        + ("\n".join("- " + line for line in history) or "- UNRUN")
        + "\n\nLatest failing checks:\n\n"
        + ("\n".join("- " + line for line in failures) or
           ("- None reported by the parsed latest suite."
            if latest and not latest.get("parse_error")
            else "- Outcome unavailable; inspect raw receipts."))
        + "\n\n"
        "Source changes: v2 provenance binds exact unchanged inputs to "
        "main27256e880ee2f7838b5aba2eaf193826148d2934; root resolution "
        "reflects the task directory; current committed-byte checks "
        "remain. The wrapper retains binary captures, actual exit or "
        "invocation error, and packaging status separately. A normalized "
        "bounded gzip/JSON capsule stores exact raw bytes; its checker "
        "does no extraction. The local checking path reconstructs "
        "identity/chronology and semantics without importing the "
        "producer. Individual validity precedes A/A equality. "
        "Whole-arm lift_count/main_lift_count and canonical_omission_lifts "
        "remain distinct.\n\n"
        "Test seams and limits: production load_plan/authorize and Git "
        "committed-byte calls are replaced only inside explicit "
        "synthetic context tests. The actual complete_manifest function "
        "and guarded wrapper/checker functions are invoked by the "
        "suite; their actual outcomes are in the retained check rows. "
        "The explicit-fake CLI is a local isolated process using the "
        "same synthetic seams. Guards reject other process/network "
        "operations. No production scientific supervisor launch is "
        "covered by those seams.\n\n"
        "Source review: AGENTS.md, agents/executor.md, complete literature/"
        "observation rules, historical checker/bridge/protocol and prior "
        "engineering review, source-inputs.json, native supervisor and "
        "ledger run-schema source (provenance internal, verified_by "
        "TASK-20261027-3a4831). Official Python subprocess, gzip and JSON "
        "documentation was retrieved during authorship. External-source "
        "review followed the first proposed snippet; repository review "
        "preceded design. This ordering deviation is retained. "
        "URLs: https://docs.python.org/3/library/subprocess.html ; "
        "https://docs.python.org/3/library/gzip.html ; "
        "https://docs.python.org/3/library/json.html .\n\n"
        "Original frozen core: "
        + source_inputs["original_protocol_core_sha256"] + ". "
        "All three exact input pins remain in source-lineage.json. "
        "Original exhibits and protocol bytes are unchanged. The "
        "successor protocol amendment remains draft.\n\n"
        "Remaining gates: assess all actual failures; parent snapshot/"
        "publication; independent engineering invocation review and "
        "archive; exact successor scientific protocol/freeze and full "
        "archive coverage; actual preapproval true; committed/pushed "
        "approval; selector ready; lawful scientific lane/claim; "
        "separate independent scientific review. Historical visitation, "
        "initialization and selection across all69 positions remain "
        "unestablished. Full goal criteria are unchanged.\n\n"
        "Canonical graphs checked by scope: the historical ECPP runtime/"
        "admission graphs and frozen scientific records are outside "
        "this task's write scope. No mathematical edge changes; this "
        "task adds the engineering custody diagram only. PDF generation "
        "does not constitute visual inspection: the hash-bound "
        "pdf_inspection receipt records the later actual inspection.\n\n"
        "Artifact hashes:\n\n"
        + "\n".join("- " + name + ": " + value
                    for name, value in hashes.items())
        + "\n\n![Engineering custody](custody.svg)\n"
    )
    version_attempts = [
        row for row in records["attempts"]
        if row.get("kind") == "tool_versions"
    ]
    report += "\nActual tool-version invocations:\n\n"
    if version_attempts:
        for observation in version_attempts[-1]["commands"]:
            output = (
                decoded(observation["stdout"])
                + decoded(observation["stderr"])
            ).decode("utf-8", errors="backslashreplace").strip()
            report += (
                "- " + json.dumps(observation["argv"])
                + "; exit " + str(observation.get("returncode"))
                + "; retained output: " + output + "\n"
            )
    else:
        report += "- UNRUN; no tool-version observation exists.\n"
    report += "\nRetained earlier failing checks:\n\n"
    historical_failures = []
    for attempt in suites:
        for check in parsed_suite(attempt)["results"]:
            if check["outcome"] != "PASS":
                historical_failures.append(
                    "Sequence " + str(attempt["sequence"]) + ": "
                    + check["name"] + ": " + check.get("error", "failure")
                )
    report += (
        "\n".join("- " + item for item in historical_failures)
        if historical_failures else "- None recorded."
    ) + "\n"
    dot = r'''
digraph custody {
  rankdir=TB;
  ranksep=0.28;
  nodesep=0.30;
  graph [fontname="Helvetica", fontsize=12,
         label="TASK-20261027-3a4831\nProspective custody\nSynthetic engineering only",
         labelloc=t, bgcolor="white"];
  node [shape=box, style="rounded,filled", fillcolor="#edf4fb",
        fontname="Helvetica", fontsize=12];
  edge [fontname="Helvetica", fontsize=11, color="#365269"];
  authority [label="Frozen native plan\nsource/input closure\nfresh authority"];
  child [label="Fixed 24-row checker\nbinary stdout/stderr\nactual exit/error"];
  capsule [label="Top-level raw capsule\nnames, exact bytes\nlengths and digests"];
  check [label="Retained-byte checker\nidentity + semantics\nvalidity before A/A"];
  report [label="Separate observations\nwhole-arm count\ncanonical 11 count"];
  authority -> child [label="prospective production"];
  child -> capsule [label="lossless custody"];
  capsule -> check [label="bounded in-memory parse"];
  check -> report [label="no state transition"];
  failure [label="Invalid/incomplete child\npartial bytes retained\npackaging failure distinct",
           fillcolor="#fff0df"];
  child -> failure;
  failure -> capsule [style=dashed, label="when packaging succeeds"];
  failure -> report [style=dashed, label="failure observation only"];
}
'''
    previous = {}
    for name in (
        "IMPLEMENTATION_REPORT.md", "custody.dot", "custody.svg", "report.pdf",
    ):
        path = HERE / name
        if path.exists():
            previous[name] = encoded(path.read_bytes())
    commands = []
    error = None
    temp = Path(tempfile.mkdtemp(prefix="render-", dir=HERE))
    preview = HERE / ".report-preview.png"

    def command(argv):
        began = now()
        try:
            result = SAVED_RUN(
                argv, capture_output=True, timeout=45, cwd=HERE,
            )
            record = {
                "argv": argv, "started_at": began, "finished_at": now(),
                "returncode": result.returncode,
                "stdout": encoded(result.stdout),
                "stderr": encoded(result.stderr),
            }
            commands.append(record)
            require(
                result.returncode == 0,
                "render command failed: " + repr(argv),
            )
            return result
        except Exception as exc:
            if not commands or commands[-1].get("argv") != argv:
                commands.append({
                    "argv": argv, "started_at": began,
                    "finished_at": now(), "error": repr(exc),
                    "stdout": encoded(
                        getattr(exc, "stdout", None) or b""
                    ),
                    "stderr": encoded(
                        getattr(exc, "stderr", None) or b""
                    ),
                })
            raise

    typst_source = ""
    failed_outputs = {}
    try:
        (HERE / "IMPLEMENTATION_REPORT.md").write_text(report)
        (HERE / "custody.dot").write_text(dot)
        command([
            "/opt/homebrew/bin/dot", "-Tsvg",
            str(HERE / "custody.dot"), "-o", str(HERE / "custody.svg"),
        ])
        compact = (
            "TASK-20261027-3a4831 - fixed-x native source engineering\n\n"
            + outcome + "\n\n"
            "Synthetic p101 engineering only. Latest guard totals:\n"
            + guards + "\n\n"
            "Preserved scientific scope: 21 identities, 24 representation "
            "rows (11 canonical omissions, 10 self controls, 3 sign "
            "sensitivities), and four correlated batch rows. The "
            "broader 69-position limitation remains. Whole-arm counts and "
            "the canonical 11 subset count are distinct.\n\n"
            "Custody: frozen native authority -> fixed checker -> "
            "binary captures and bounded lossless capsule -> local "
            "identity/semantic checks -> individual validity before A/A. "
            "Packaging success does not establish validity.\n\n"
            "Failures and all raw attempts are retained in "
            "test-receipts.json. Latest failing checks: "
            + (", ".join(failures) if failures else
               "see retained suite; no failure is suppressed") + ".\n\n"
            "Remaining: producer assessment, pushed snapshot, independent "
            "engineering invocation review, successor scientific protocol, "
            "actual preapproval/approval/ready and lawful scientific "
            "claim. No official transition. Full goal criteria unchanged.\n\n"
            "Sources: immutable BATCH-05b760 exhibits, source-inputs.json, "
            "native supervisor source; Python subprocess/gzip/json docs. "
            "External documentation was retrieved during authorship. "
            "Full source hashes and test seams: IMPLEMENTATION_REPORT.md.\n"
        )
        history_parts = []
        for attempt in suites:
            observed = parsed_suite(attempt)
            if observed.get("parse_error"):
                history_parts.append(
                    "sequence " + str(attempt["sequence"])
                    + ": result unavailable; raw receipt retained"
                )
                continue
            description = (
                "sequence " + str(attempt["sequence"])
                + ": " + str(observed["passed"]) + " pass/"
                + str(observed["failed"]) + " fail"
            )
            accepted_invalid = sum(
                check["outcome"] == "FAIL"
                and "invalid fixture accepted:" in check.get("error", "")
                for check in observed["results"]
            )
            later_gate_mismatches = sum(
                check["outcome"] == "FAIL"
                and "wrong gate expected" in check.get("error", "")
                for check in observed["results"]
            )
            if accepted_invalid or later_gate_mismatches:
                description += (
                    " (" + str(accepted_invalid)
                    + " accepted invalid synthetic packages; "
                    + str(later_gate_mismatches)
                    + " later-gate mismatches)"
                )
            history_parts.append(description)
        intended_corrective_gates = {
            "native_raw_schema_extra_key": "native raw schema",
            "native_raw_schema_missing_required": "native raw schema",
            "native_raw_schema_wrong_type": "native raw schema",
            "outer_promotion_historical_selector_established":
                "forbidden outcome promotion",
            "outer_promotion_official_transition":
                "forbidden outcome promotion",
        }
        if suites and latest and not latest.get("parse_error"):
            intended_gate_passes = sum(
                check["name"] in intended_corrective_gates
                and check["outcome"] == "PASS"
                and check.get("detail", {}).get("intended_gate")
                    == intended_corrective_gates[check["name"]]
                for check in latest["results"]
            )
            corrective_history = (
                "Latest raw extra/missing/type and unsupported outer "
                "historical-selector/official-transition controls: "
                + str(intended_gate_passes) + "/"
                + str(len(intended_corrective_gates))
                + " PASS at their intended gates."
            )
        else:
            corrective_history = (
                "Corrective intended-gate outcomes unavailable or UNRUN."
            )
        compact += (
            "\nEngineering-only retained invocation history: "
            + ("; ".join(history_parts) if history_parts else "UNRUN")
            + ". " + corrective_history + "\n"
        )
        typst_source = (
            '#set page(paper: "a4", margin: 1.25cm)\n'
            '#set text(size: 9pt)\n'
            '#text(' + json.dumps(compact, ensure_ascii=False) + ')\n'
            '#v(0.3cm)\n'
            '#image("/custody.svg", width: 100%, height: 13cm, fit: "contain")\n'
        )
        typst_path = temp / "report.typ"
        typst_path.write_text(typst_source)
        command([
            "/opt/homebrew/bin/typst", "compile", "--root", str(HERE),
            str(typst_path), str(HERE / "report.pdf"),
        ])
        require(
            (HERE / "report.pdf").stat().st_size <= PDF_LIMIT,
            "PDF exceeds65536 bytes; no storage route authorized",
        )
        info = command([
            "/opt/homebrew/bin/pdfinfo", str(HERE / "report.pdf"),
        ])
        match = re.search(rb"^Pages:\s+(\d+)\s*$", info.stdout, re.M)
        require(
            match and int(match.group(1)) == 1,
            "PDF must be one page for complete declared preview inspection",
        )
        text = command([
            "/opt/homebrew/bin/pdftotext",
            str(HERE / "report.pdf"), "-",
        ])
        require(
            b"TASK-20261027-3a4831" in text.stdout,
            "PDF task citation absent",
        )
        command([
            "/opt/homebrew/bin/pdftoppm",
            "-f", "1", "-singlefile", "-scale-to", "1400", "-png",
            str(HERE / "report.pdf"),
            str(HERE / ".report-preview"),
        ])
    except Exception as exc:
        error = repr(exc)
        for name in (
            "IMPLEMENTATION_REPORT.md", "custody.dot",
            "custody.svg", "report.pdf",
        ):
            path = HERE / name
            if path.exists():
                failed_outputs[name] = encoded(path.read_bytes())
    finally:
        sequence = append_receipt({
            "kind": "report_render",
            "started_at": started,
            "finished_at": now(),
            "returncode": 0 if error is None else 1,
            "error": error,
            "commands": commands,
            "typst_source": typst_source,
            "previous_artifacts": previous,
            "failed_outputs": failed_outputs,
            "pdf_sha256": (
                capsule.sha((HERE / "report.pdf").read_bytes())
                if (HERE / "report.pdf").is_file() else None
            ),
            "preview_path": str(preview) if preview.exists() else None,
            "visual_inspection": "PENDING; generation is not inspection",
        })
        shutil.rmtree(temp)
    print(json.dumps({
        "recorded_sequence": sequence,
        "render_error": error,
        "preview_path": str(preview) if preview.exists() else None,
        "pdf_sha256": (
            capsule.sha((HERE / "report.pdf").read_bytes())
            if (HERE / "report.pdf").is_file() else None
        ),
    }))
    return 0 if error is None else 1


def record_inspection(expected_sha256, note):
    path = HERE / "report.pdf"
    require(path.is_file(), "PDF absent")
    actual = capsule.sha(path.read_bytes())
    require(actual == expected_sha256, "PDF changed before inspection record")
    require(note.strip(), "inspection note empty")
    sequence = append_receipt({
        "kind": "pdf_inspection",
        "recorded_at": now(),
        "pdf_sha256": actual,
        "note": note,
        "source": "Parent-reported actual visual and extracted-text inspection",
        "scope": "All pages of the one-page current PDF",
    })
    preview = HERE / ".report-preview.png"
    if preview.exists():
        preview.unlink()
    print(json.dumps({
        "recorded_sequence": sequence, "pdf_sha256": actual,
    }))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--fake-driver", type=Path)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--inspect-sha256")
    parser.add_argument("--inspection-note")
    args = parser.parse_args()
    modes = sum((
        args.record, args.fake_driver is not None,
        args.render, args.inspect_sha256 is not None,
    ))
    require(modes <= 1, "choose one tooling mode")
    if args.fake_driver:
        def fake():
            fixture = Fixture(args.fake_driver)
            ordinary(fixture)
            print(json.dumps({
                "explicit_fake": True, "guard_totals": COUNTS,
            }))
            return 0
        return guarded(fake)
    if args.record:
        return record_suite()
    if args.render:
        return render_report()
    if args.inspect_sha256:
        return record_inspection(
            args.inspect_sha256, args.inspection_note or "",
        )

    def alarm(signum, frame):
        raise TimeoutError("synthetic-suite watchdog")

    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(110)
    try:
        result = guarded(run_suite)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["failed"] == 0 else 1
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    raise SystemExit(main())
