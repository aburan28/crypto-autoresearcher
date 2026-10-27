#!/usr/bin/env python3
"""Finite exact fixed-x check. Importing this module performs no I/O or arithmetic."""
import argparse
import contextlib
import copy
import datetime
import hashlib
import json
import platform
import subprocess
import sys
import traceback
from pathlib import Path

INPUT_COMMIT = "3d0cd8901492d83ab6aea327b967061c75f7550e"
PINS = {
    "research/nist_seed_skipped_curves_20261016/assessed.json": "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841",
    "research/nist_seed_skipped_curves_20261016/traits.json": "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67",
    "research/nist_seed_selection_deep_20261016/selection_matrix.json": "d93eabf58eecdb48cb74657d28e985c965bc6ca8a74ec02e468846e8c77329b6",
}
ARMS = ("fixed-x", "fixed-x-aa", "positive", "negative")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def dump(path, value):
    with path.open("x", encoding="utf8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def bound_json(data, expected):
    require(sha(data) == expected, "source SHA-256 mismatch")
    return json.loads(data)


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


def plan(assessed, traits, matrix):
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


def evaluate(p, a, b, x, y):
    require(p > 2 and p % 2 == 1 and 0 <= x < p and 0 <= y < p, "invalid arithmetic inputs")
    rhs = (x*x*x + a*x + b) % p
    euler = pow(rhs, (p-1)//2, p)
    require(euler in (0, 1, p-1), "Euler output outside odd-prime alphabet")
    symbol = -1 if euler == p-1 else euler
    other = jacobi(rhs, p)
    require(symbol == other, "Euler/Jacobi disagreement")
    return {"rhs_hex":hex(rhs), "euler_value_hex":hex(euler), "jacobi":other, "symbol":symbol, "lifts":symbol in (0,1), "full_point_member":(y*y-rhs) % p == 0, "b_determined_by_full_point_hex":hex((y*y-x*x*x-a*x) % p)}


def expect_rejected(fn):
    try:
        fn()
    except (ValueError, KeyError, TypeError, IndexError):
        return True
    return False


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def committed_bytes(root, commit, path):
    relative = Path(path).resolve().relative_to(root.resolve()).as_posix()
    return subprocess.run(["git", "-C", str(root), "show", commit+":"+relative], check=True, capture_output=True).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New directory; existing paths are refused")
    parser.add_argument("--protocol", type=Path, default=Path(__file__).with_name("protocol.json"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    require(not args.out.exists(), "refusing existing output directory")
    observed_commit = git(root, "rev-parse", "HEAD")
    observed_dirty = git(root, "status", "--porcelain", "--untracked-files=normal")
    args.out.mkdir(parents=True, exist_ok=False)
    started = {"schema":"nist.fixed-x.started/v1", "started_at":now(), "argv":sys.argv, "input_commit":INPUT_COMMIT, "observed_commit":observed_commit, "dirty_before_output_creation":observed_dirty, "python":sys.version, "executable":sys.executable, "platform":platform.platform(), "machine":platform.machine(), "processor":platform.processor(), "isolation":"none", "wall_valid":False, "threads":1, "source_pins":PINS}
    dump(args.out/"started.json", started)
    results, run_rows = {}, []
    with (args.out/"stdout.txt").open("x") as outlog, (args.out/"stderr.txt").open("x") as errlog, contextlib.redirect_stdout(outlog), contextlib.redirect_stderr(errlog):
        try:
            protocol_bytes = args.protocol.read_bytes()
            require(protocol_bytes == committed_bytes(root, observed_commit, args.protocol), "protocol differs from observed committed bytes")
            protocol = json.loads(protocol_bytes)
            freeze = protocol["freeze"]
            require(protocol["schema"] == "experiment.protocol/v1" and freeze["status"] == "frozen", "protocol must already be frozen")
            require(freeze["filed_before_affected_data"] is True, "protocol was not filed before affected data")
            require(freeze["protocol_sha256"] == sha(canonical({k:v for k,v in protocol.items() if k != "freeze"})), "frozen protocol hash mismatch")
            require(git(root, "merge-base", "--is-ancestor", INPUT_COMMIT, observed_commit) == "", "input commit is not ancestral")
            git(root, "merge-base", "--is-ancestor", freeze["commit"], observed_commit)
            code_bytes = Path(__file__).read_bytes()
            require(code_bytes == committed_bytes(root, observed_commit, Path(__file__)), "checker differs from observed committed bytes")
            code_sha = sha(code_bytes)
            require(protocol["analysis_plan"]["frozen_before_data"] is True and protocol["analysis_plan"]["script"]["sha256"] == code_sha, "analysis source is not pinned")
            require([a["id"] for a in protocol["arms"]] == list(ARMS), "unexpected arms/order")
            require(all(a["instrument"]["binary_sha256"] == code_sha for a in protocol["arms"]), "instrument source is not pinned")
            blobs = {p:(root/p).read_bytes() for p in PINS}
            for path, data in blobs.items():
                require(data == committed_bytes(root, observed_commit, root/path), "input differs from observed committed bytes: " + path)
            docs = [bound_json(blobs[p], digest) for p,digest in PINS.items()]
            workload = plan(*docs)
            dump(args.out/"workload.json", workload)
            for arm in ARMS:
                began = now()
                details = []
                status = "succeeded"
                try:
                    if arm in ("fixed-x", "fixed-x-aa"):
                        for item in workload:
                            record = dict(item)
                            try:
                                record.update(evaluate(*(int(item[k], 16) for k in ("p_hex", "a_hex", "b_hex", "fixed_x_hex", "fixed_y_hex"))))
                                record["status"] = "succeeded"
                            except Exception as exc:
                                record.update(status="invalid", error=repr(exc))
                                status = "invalid"
                            details.append(record)
                        if arm == "fixed-x-aa":
                            require(details == results["fixed-x"], "A/A exact equality failure")
                        require(all(r.get("lifts") and r.get("full_point_member") for r in details if r["kind"] == "published_self"), "published self control failure")
                    elif arm == "positive":
                        for name,b,y,expected in (("positive-square",1,1,1), ("zero-boundary",0,0,0)):
                            record = dict(name=name, p=101, a=-3, b=b, x=0, y=y, **evaluate(101,-3,b,0,y))
                            require(record["lifts"] and record["symbol"] == expected, "positive or zero-boundary failure")
                            details.append(record)
                    else:
                        record = dict(name="negative-nonresidue", p=101, a=-3, b=3, x=0, y=0, **evaluate(101,-3,3,0,0))
                        require(not record["lifts"] and record["symbol"] == -1, "negative detector failure")
                        details.append(record)
                        positive = evaluate(101,-3,1,0,1)
                        nearby = evaluate(101,-3,4,0,1)
                        require(positive["lifts"] and nearby["lifts"] and positive["full_point_member"] and not nearby["full_point_member"], "full-point circularity control failure")
                        details.append({"name":"proves-too-much-full-point", "positive":positive, "nearby_b4":nearby, "passed":True})
                        first = next(iter(PINS))
                        require(expect_rejected(lambda:bound_json(blobs[first]+b"\n", PINS[first])), "source corruption accepted")
                        broken = copy.deepcopy(docs)
                        del broken[0]["candidate_rows"][0]["p_hex"]
                        require(expect_rejected(lambda:plan(*broken)), "schema corruption accepted")
                        details.append({"name":"source-binding-and-schema-corruption", "passed":True})
                except Exception as exc:
                    status = "invalid"
                    details.append({"status":"invalid", "error":repr(exc), "traceback":traceback.format_exc()})
                results[arm] = details
                dump(args.out/(arm+".json"), {"arm":arm,"status":status,"rows":details})
                run_rows.append({"run_id":arm+"-batch-0", "arm":arm, "instance_id":"0", "replicate":0, "seed":0, "warmup":False, "status":status, "verification":"verified" if status == "succeeded" else "refuted", "tier":"none", "lift_count":sum(r.get("lifts") is True for r in details), "evaluated_count":sum("lifts" in r for r in details), "started_at":began, "finished_at":now(), "binary_sha256":code_sha, "source_commit":observed_commit})
            with (args.out/"rows.jsonl").open("x") as handle:
                for row in run_rows:
                    handle.write(json.dumps(row, sort_keys=True)+"\n")
            valid = all(row["status"] == "succeeded" for row in run_rows)
            canonical_rows = [r for r in results["fixed-x"] if r.get("kind") == "canonical_omission"]
            summary = {"schema":"nist.fixed-x.observation/v1", "valid":valid, "protocol_sha256":freeze["protocol_sha256"], "canonical_omission_rows":len(canonical_rows), "canonical_omission_lifts":sum(r.get("lifts") is True for r in canonical_rows), "canonical_witness_uids":[r["curve_uid"] for r in canonical_rows if r.get("lifts") is True], "alternate_sign_sensitivity":[r for r in results["fixed-x"] if r.get("kind") == "alternate_sign_sensitivity"], "historical_selector_established":False, "official_transition":False, "finished_at":now()}
            dump(args.out/"summary.json", summary)
            print(json.dumps({"valid":valid,"rows":len(workload),"arms":len(run_rows)}))
            return 0 if valid else 2
        except Exception as exc:
            traceback.print_exc()
            dump(args.out/"failure.json", {"status":"invalid", "error":repr(exc), "traceback":traceback.format_exc(), "finished_at":now(), "completed_arm_rows":run_rows})
            return 2


if __name__ == "__main__":
    raise SystemExit(main())
