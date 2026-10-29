#!/usr/bin/env python3
"""Prospective native-supervisor adapter. Importing performs no trial or I/O."""
import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

CHECKER_SHA256 = "7c70b0b9e4843efa19c7301cb1884229621a525812528ace70bf913eb4580de1"
RAW_MEMBERS = {"started.json", "workload.json", "fixed-x.json", "fixed-x-aa.json",
               "positive.json", "negative.json", "rows.jsonl", "summary.json",
               "stdout.txt", "stderr.txt"}
ARMS = ("fixed-x", "fixed-x-aa", "positive", "negative")


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def write(path, value):
    with path.open("x", encoding="utf8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def context(args, running):
    root = Path(__file__).resolve().parents[3]
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
    checker = Path(__file__).with_name("check_fixed_x.py")
    require(digest(checker) == CHECKER_SHA256, "fixed checker changed")
    require(plan["source_sha256"].get(checker.relative_to(root).as_posix()) == CHECKER_SHA256,
            "checker absent from native source closure")
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


def raw_inventory(directory):
    result = {}
    for path in sorted(directory.rglob("*")):
        require(not path.is_symlink(), "symlink in raw custody")
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = digest(path)
    return result


def produce(args):
    root, directory, plan, launch, protocol, protocol_path, checker, supervisor = context(args, True)
    for name in ("manifest.yaml", "raw-result.json", "driver-exit.json",
                 "driver.stdout.txt", "driver.stderr.txt", "fixed-x-raw"):
        require(not (directory / name).exists(), "refusing existing driver output: " + name)
    argv = [sys.executable, str(checker), "--protocol", str(protocol_path),
            "--out", str(directory / "fixed-x-raw")]
    began = datetime.now(timezone.utc).isoformat()
    child_rc, error, stdout, stderr = None, None, "", ""
    try:
        child = subprocess.run(argv, cwd=root, capture_output=True, text=True,
                               timeout=protocol["execution"]["timeout_seconds"])
        child_rc, stdout, stderr = child.returncode, child.stdout, child.stderr
    except subprocess.TimeoutExpired as exc:
        decode = lambda value: value.decode(errors="replace") if isinstance(value, bytes) else (value or "")
        stdout, stderr = decode(exc.stdout), decode(exc.stderr)
        error = {"kind": "child_timeout", "message": str(exc)}
    except OSError as exc:
        error = {"kind": "child_invocation_error", "message": str(exc)}
    for name, content in (("driver.stdout.txt", stdout), ("driver.stderr.txt", stderr)):
        with (directory / name).open("x", encoding="utf8") as stream:
            stream.write(content)
    write(directory / "driver-exit.json",
          {"argv": argv, "started_at": began, "finished_at": datetime.now(timezone.utc).isoformat(),
           "wrapper_pid": os.getpid(), "child_call_attempted": True,
           "child_returncode_observed": child_rc, "error": error})
    raw_directory = directory / "fixed-x-raw"
    summary, decode_error = None, None
    if (raw_directory / "summary.json").is_file():
        try:
            summary = read(raw_directory / "summary.json")
        except (ValueError, OSError) as exc:
            decode_error = str(exc)
    valid = child_rc == 0 and error is None and isinstance(summary, dict) and summary.get("valid") is True
    metrics = {}
    if valid:
        count = summary.get("canonical_omission_lifts")
        require(type(count) is int and 0 <= count <= 11, "bad observed canonical count")
        metrics = {"canonical_omission_lifts": count, "planned_main_rows": 24}
    native_names = ("driver.stdout.txt", "driver.stderr.txt", "driver-exit.json")
    raw = {"schema": "nist.fixed-x.native/v1", "attack_claimed": False,
           "experiment_id": plan["experiment_id"], "run_id": launch["run_id"],
           "plan_sha256": launch["plan_sha256"], "protocol_path": protocol_path.relative_to(root).as_posix(),
           "protocol_file_sha256": digest(protocol_path), "protocol_sha256": protocol["freeze"]["protocol_sha256"],
           "checker_sha256": CHECKER_SHA256, "valid": valid, "summary": summary,
           "summary_decode_error": decode_error,
           "raw_artifacts": raw_inventory(raw_directory) if raw_directory.is_dir() else {},
           "native_artifacts": {name: digest(directory / name) for name in native_names}}
    write(directory / "raw-result.json", raw)
    body = {"attack_claimed": False, "metrics": metrics,
            "result": {"certificate": {"kind": "none"}, "valid": valid}}
    if not valid:
        body["status"] = "completed_invalid"
        body["result"]["reason"] = "Retained child failure, incomplete output, or invalid controls; see driver-exit.json and raw artifacts."
    write(directory / "manifest.yaml", {"run": body})
    # Packaging completion is not validity. The separate checker must refuse every invalid child.
    print(json.dumps({"packaging_completed": True, "scientific_output_valid": valid}))
    return 0


def expected_rows(root, protocol):
    pins = protocol["extensions"]["source_pins"]
    require(len(pins) == 3 and {Path(name).name for name in pins} ==
            {"assessed.json", "traits.json", "selection_matrix.json"}, "unexpected input closure")
    documents = {}
    for name, expected in pins.items():
        path = root / name
        require(digest(path) == expected, "changed exact input: " + name)
        documents[Path(name).name] = read(path)
    assessed, traits, matrix = (documents[name] for name in ("assessed.json", "traits.json", "selection_matrix.json"))
    sources = {r["identity"]["curve_uid"]: r for r in assessed["candidate_rows"]}
    sources.update({r["identity"]["curve_uid"]: r for r in traits["published_controls"].values()})
    matrix_rows = {(r["timestamp"], r["ordinal"]): r for r in matrix["rows"]}
    require(len(sources) == len(matrix_rows) == 21, "unexpected canonical input scope")
    answer = []
    for stream in sorted(matrix["streams"], key=lambda r: r["timestamp"]):
        previous = None
        for index, slot in enumerate(stream["slots"]):
            item = matrix_rows[(stream["timestamp"], slot["ordinal"])]
            require(item["name"] == slot["name"] and item["label"] == slot["label"], "chronology mismatch")
            is_self = slot["label"] == "published"
            next_slot = slot if is_self else next(s for s in stream["slots"][index+1:] if s["label"] == "published")
            target = matrix_rows[(stream["timestamp"], next_slot["ordinal"])]
            source, control = sources[item["curve_uid"]], sources[target["curve_uid"]]
            x, y = control["identity"]["curve"]["generator"]
            require(source["p_hex"] == control["p_hex"], "wrong paired field")
            entry = {"row_id": str(stream["timestamp"])+"-"+str(slot["ordinal"]),
                     "kind": "published_self" if is_self else "canonical_omission",
                     "name": item["name"], "curve_uid": item["curve_uid"],
                     "timestamp": stream["timestamp"], "ordinal": slot["ordinal"],
                     "previous_published_uid": previous,
                     "counterpart_name": target["name"], "counterpart_uid": target["curve_uid"],
                     "counterpart_ordinal": target["ordinal"],
                     **{k: hex(int(source[k], 16)) for k in ("p_hex", "a_hex", "b_hex", "n_hex")},
                     "fixed_x_hex": hex(x), "fixed_y_hex": hex(y)}
            answer.append(entry)
            alternate = source.get("alternate_sign_model")
            if alternate is not None:
                answer.append(dict(entry, row_id=entry["row_id"]+"-opposite-sign",
                                   kind="alternate_sign_sensitivity", canonical_uid=entry["curve_uid"],
                                   curve_uid=alternate["curve_uid"], b_hex=hex(int(alternate["b_hex"], 16)),
                                   x_transport="none: fixed x unchanged"))
            if is_self:
                previous = item["curve_uid"]
    require(len(answer) == 24 and len({r["curve_uid"] for r in answer}) == 24, "wrong fixed representation coverage")
    return answer


def arithmetic(row):
    p, a, b, x, y = (int(row[k], 16) for k in ("p_hex", "a_hex", "b_hex", "fixed_x_hex", "fixed_y_hex"))
    value = (pow(x, 3, p) + (a*x) + b) % p
    residue = pow(value, (p-1)//2, p)
    require(residue in (0, 1, p-1), "unexpected residue on bound prime input")
    symbol = -1 if residue == p-1 else residue
    return {"rhs_hex": hex(value), "euler_value_hex": hex(residue), "symbol": symbol,
            "jacobi": symbol, "lifts": symbol >= 0,
            "full_point_member": pow(y, 2, p) == value,
            "b_determined_by_full_point_hex": hex((pow(y, 2, p)-pow(x, 3, p)-a*x) % p)}


def verify(args):
    root, directory, plan, launch, protocol, protocol_path, checker, supervisor = context(args, False)
    raw = read(directory / "raw-result.json")
    require(raw["schema"] == "nist.fixed-x.native/v1" and raw["valid"] is True, "invalid native observation")
    require(raw["experiment_id"] == plan["experiment_id"] and raw["run_id"] == launch["run_id"], "wrong native identities")
    require(raw["plan_sha256"] == launch["plan_sha256"], "changed plan binding")
    require(raw["protocol_file_sha256"] == digest(protocol_path) and
            raw["protocol_sha256"] == protocol["freeze"]["protocol_sha256"], "changed protocol binding")
    for name, expected in raw["native_artifacts"].items():
        require(name in ("driver.stdout.txt", "driver.stderr.txt", "driver-exit.json"), "unexpected native sidecar")
        require(digest(directory / name) == expected, "changed native sidecar")
    require(set(raw["native_artifacts"]) == {"driver.stdout.txt", "driver.stderr.txt", "driver-exit.json"}, "missing native sidecar")
    require(read(directory / "driver-exit.json")["child_returncode_observed"] == 0, "child did not complete successfully")
    require(raw["checker_sha256"] == CHECKER_SHA256 and raw["attack_claimed"] is False,
            "changed source or claim boundary")
    require(raw["protocol_path"] == protocol_path.relative_to(root).as_posix(), "wrong protocol path")
    inner = directory / "fixed-x-raw"
    require(set(raw["raw_artifacts"]) == RAW_MEMBERS, "incomplete or extra raw members")
    require(raw_inventory(inner) == raw["raw_artifacts"], "raw custody mismatch")
    started = read(inner / "started.json")
    require(started["source_pins"] == protocol["extensions"]["source_pins"] and
            started["observed_commit"] == launch["authority"]["commit"],
            "wrong raw input or observed-commit provenance")
    expected = expected_rows(root, protocol)
    workload = read(inner / "workload.json")
    require(len(workload) == 24, "wrong raw workload length")
    arms = {name: read(inner / (name+".json")) for name in ARMS}
    require(all(obj["arm"] == name and obj["status"] == "succeeded" for name,obj in arms.items()),
            "an arm is invalid or absent")
    main = arms["fixed-x"]["rows"]
    require(main == arms["fixed-x-aa"]["rows"] and len(main) == 24, "A/A or coverage mismatch")
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
        require(row["symbol"] == symbol and all(row.get(k) == v for k,v in arithmetic(expect).items()),
                "fixture arithmetic failed")
    require(negatives[1]["name"] == "proves-too-much-full-point" and negatives[1]["passed"] is True,
            "circularity control absent")
    for key, b in (("positive", 1), ("nearby_b4", 4)):
        expect = {"p_hex":hex(101),"a_hex":hex(-3),"b_hex":hex(b),"fixed_x_hex":"0x0","fixed_y_hex":"0x1"}
        require(all(negatives[1][key].get(k) == value for k,value in arithmetic(expect).items()),
                "circularity fixture changed")
    require(negatives[2] == {"name":"source-binding-and-schema-corruption","passed":True},
            "fail-closed control absent")
    batch_rows = [json.loads(line) for line in (inner / "rows.jsonl").read_text().splitlines() if line.strip()]
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
    summary = read(inner / "summary.json")
    require(summary == raw["summary"] and summary["valid"] is True and
            summary["protocol_sha256"] == protocol["freeze"]["protocol_sha256"],
            "summary changed or invalid")
    require(summary["canonical_omission_rows"] == 11 and
            summary["canonical_omission_lifts"] == sum(row["lifts"] for row in canonical) and
            summary["canonical_witness_uids"] == [row["curve_uid"] for row in canonical if row["lifts"]],
            "wrong canonical summary")
    require(summary["alternate_sign_sensitivity"] == alternate and
            summary["historical_selector_established"] is False and summary["official_transition"] is False,
            "wrong sensitivity or promoted conclusion")
    manifest = supervisor.fast_yaml.safe_load((directory / "manifest.yaml").read_text())["run"]
    metrics = {"canonical_omission_lifts": summary["canonical_omission_lifts"], "planned_main_rows":24}
    require(manifest["id"] == launch["run_id"] and manifest["experiment_id"] == plan["experiment_id"] and
            manifest["attack_claimed"] is False and manifest["result"]["valid"] is True and
            manifest["result"]["certificate"]["kind"] == "none" and
            manifest["metrics"] == metrics and manifest["result"]["metrics"] == metrics,
            "manifest changed identities, validity or metrics")
    print(json.dumps({"valid":True,"canonical_omission_lifts":summary["canonical_omission_lifts"],
                      "representations_checked":24,"independent_review":False}))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run","check"))
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
