"""Independent exact checker for the three fixed prime63 m=2 positives.

No Sage import or Gröbner computation. Full points, signs, factor-base indices,
polynomial equations, trace and every raw archive member are checked anew.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import tarfile
from decimal import Decimal
from pathlib import Path

import execute


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def exact(value) -> int:
    if type(value) is int:
        return value
    if isinstance(value, str) and value and value.lstrip("-").isdigit():
        return int(value, 10)
    raise ValueError("nonintegral field or index value")


def prime64(n: int) -> bool:
    if n < 2 or n >= 2**64:
        return False
    for small in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % small == 0:
            return n == small
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        a = base % n
        if a == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n-1):
            continue
        for _ in range(s-1):
            x = x*x % n
            if x == n-1:
                break
        else:
            return False
    return True


def point(raw, p: int, a: int, b: int):
    if not isinstance(raw, (list, tuple)) or len(raw) != 2:
        raise ValueError("full point requires two coordinates")
    x, y = map(exact, raw)
    if not (0 <= x < p and 0 <= y < p) or (y*y-x*x*x-a*x-b) % p:
        raise ValueError("point is not on exact curve")
    return x, y


def add(P, Q, p: int, a: int):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1+y2) % p == 0:
        return None
    if P == Q:
        if y1 == 0:
            return None
        slope = (3*x1*x1+a)*pow(2*y1, -1, p) % p
    else:
        slope = (y2-y1)*pow((x2-x1) % p, -1, p) % p
    x3 = (slope*slope-x1-x2) % p
    return x3, (slope*(x1-x3)-y1) % p


def curve(system):
    c = system["curve"]
    p, a, b = (exact(c[k]) for k in ("p", "a", "b"))
    if not prime64(p) or p <= 3 or (4*a*a*a+27*b*b) % p == 0:
        raise ValueError("unsupported, composite or singular curve")
    return p, a, b


def equations(system, root: dict):
    p, a, b = curve(system)
    names = system["variables"]
    if (not isinstance(root, dict) or not isinstance(root.get("variables"), dict)
            or set(root["variables"]) != set(names)):
        raise ValueError("root variables mismatch")
    values = [exact(root["variables"][name]) for name in names]
    if any(not 0 <= v < p for v in values):
        raise ValueError("root outside field")
    for equation in system["equations"]:
        total = 0
        for term in equation:
            product = exact(term["coefficient"])
            for index, power in term["powers"]:
                index, power = exact(index), exact(power)
                if not 0 <= index < len(values) or power < 0:
                    raise ValueError("bad monomial")
                product = product*pow(values[index], power, p) % p
            total = (total+product) % p
        if total:
            raise ValueError("polynomial equation failed")
    return p, a, b


def verify_selected(system, root: dict, selected: list[dict]) -> dict:
    p, a, b = equations(system, root)
    m = exact(system["m"])
    if m != 2 or len(selected) != m:
        raise ValueError("selected signed arity mismatch")
    base = [point(P, p, a, b) for P in system["base_points"]]
    if len(set(base)) != len(base):
        raise ValueError("duplicate factor-base point")
    target = point(system["target_point"], p, a, b)
    base_index = {P: j for j, P in enumerate(base)}
    total = None
    normalized = []
    for i, row in enumerate(selected, 1):
        index, sign = exact(row["index"]), exact(row["sign"])
        if index != i - 1 or sign not in (-1, 1):
            raise ValueError("bad summand index or sign")
        P = point(row["point"], p, a, b)
        if P not in base_index:
            raise ValueError("selected point outside factor base")
        signed = (P[0], P[1] if sign == 1 else (-P[1]) % p)
        if point(row["signed_point"], p, a, b) != signed:
            raise ValueError("selected signed point mismatch")
        if exact(root["variables"][f"x{i}"]) != P[0]:
            raise ValueError("root x and selected full point mismatch")
        total = add(total, signed, p, a)
        normalized.append({"index": index, "factor_base_index": base_index[P],
                           "sign": sign, "point": P,
                           "signed_point": signed})
    if total != target:
        raise ValueError("signed full-point target sum mismatch")
    if system["arm"] == "coset":
        params = system["base_parameters"]
        d, c = exact(params["d"]), exact(params["coset"])
        if any(pow(row["point"][0], d, p) != pow(c, d, p) for row in normalized):
            raise ValueError("coset gate mismatch")
    return {"status": "checked_full_point_relation", "selected": normalized}


def reconstruct_selected(system, root: dict) -> dict:
    p, a, b = equations(system, root)
    base = [point(P, p, a, b) for P in system["base_points"]]
    if len(set(base)) != len(base):
        raise ValueError("duplicate factor-base point")
    by_x = {}
    for P in base:
        by_x.setdefault(P[0], []).append(P)
    xs = [exact(root["variables"][f"x{i}"]) for i in (1, 2)]
    if any(x not in by_x for x in xs):
        raise ValueError("root x outside factor base")
    target = point(system["target_point"], p, a, b)
    for pair in itertools.product(*(by_x[x] for x in xs)):
        for signs in itertools.product((-1, 1), repeat=2):
            selected = [{"index": i, "sign": sign, "point": list(P),
                         "signed_point": [P[0], P[1] if sign == 1 else (-P[1]) % p]}
                        for i, (P, sign) in enumerate(zip(pair, signs))]
            try:
                checked = verify_selected(system, root, selected)
            except ValueError:
                continue
            if target is not None:
                return checked
    raise ValueError("no signed full-point target lift")


def archived_witnesses() -> dict:
    return {w["cell"]: w for w in execute.exact_json(execute.WITNESSES)["witnesses"]}


def verify_archive(output: Path, receipt: dict) -> dict[str, bytes]:
    records = receipt["raw_files"]
    names = [r["path"] for r in records]
    if len(set(names)) != len(names) or any(not n or n.startswith("/") or ".." in Path(n).parts for n in names):
        raise ValueError("invalid raw member path")
    tar_path = output / "raw.tar.gz"
    if execute.sha(tar_path) != receipt["raw_tar_sha256"]:
        raise ValueError("raw tar digest mismatch")
    contents = {}
    with tarfile.open(tar_path, "r:gz") as archive:
        members = archive.getmembers()
        if len(members) != len(names) or set(m.name for m in members) != set(names) \
                or any(not m.isfile() for m in members):
            raise ValueError("raw archive coverage mismatch")
        for row in records:
            handle = archive.extractfile(row["path"])
            if handle is None:
                raise ValueError("missing raw member")
            data = handle.read()
            if len(data) != row["bytes"] or sha_bytes(data) != row["sha256"]:
                raise ValueError("raw member digest mismatch")
            disk = output / row["path"]
            cursor = output
            for part in Path(row["path"]).parts:
                cursor /= part
                if cursor.is_symlink():
                    raise ValueError("raw path symlink")
            if disk.is_file() and disk.read_bytes() != data:
                raise ValueError("disk/raw archive mismatch")
            contents[row["path"]] = data
    expected_disk = {str(p.relative_to(output)) for p in output.rglob("*")
                     if p.is_file() and p.relative_to(output).as_posix()
                     not in ("raw.tar.gz", "receipt.json")}
    if expected_disk != set(names):
        raise ValueError("partial or extra raw disk tree")
    return contents


def _json_bytes(raw: bytes):
    return json.loads(raw.decode(), parse_int=int, parse_float=Decimal)


def verify_trace(raw: bytes, expected_stop: str, source_hashes: dict[str, str],
                 *, require_sample: bool) -> dict:
    if not raw or not raw.endswith(b"\n"):
        raise ValueError("missing or truncated phase trace")
    rows = [_json_bytes(line) for line in raw.splitlines()]
    streams = {}
    for row in rows:
        if row.get("schema") != "icperf-prime63-phase-v1" or \
                row.get("source_sha256") != source_hashes.get(row.get("stream")):
            raise ValueError("phase source/schema mismatch")
        stream = row["stream"]
        prior = streams.get(stream)
        if prior is not None and (row["sequence"] != prior[0]+1 or row["monotonic_ns"] < prior[1]):
            raise ValueError("phase sequence or clock regression")
        if prior is None and row["sequence"] != 0:
            raise ValueError("phase sequence does not start at zero")
        streams[stream] = row["sequence"], row["monotonic_ns"]
    terminals = [r for r in rows if r["stream"] == "supervisor" and r["event"] == "terminal"]
    if len(terminals) != 1 or terminals[0]["fields"]["stop"] != expected_stop:
        raise ValueError("phase terminal/receipt mismatch")
    samples = [r for r in rows if r["stream"] == "supervisor" and r["event"] == "sample"]
    if require_sample and not samples:
        raise ValueError("missing resource samples")
    if any("rss_bytes" not in r["fields"] for r in samples):
        raise ValueError("resource sample missing RSS classification")
    solver_terminal = [r for r in rows if r["stream"] == "solver" and r["event"] == "terminal"]
    if len(solver_terminal) > 1:
        raise ValueError("duplicate solver terminal")
    return {"events": len(rows), "samples": len(samples), "streams": sorted(streams),
            "solver_status": solver_terminal[0]["fields"].get("status") if solver_terminal else None}


def verify_result(receipt: dict, archived: dict[str, bytes], manifest: dict,
                  fixed: list[dict], witness: dict) -> dict:
    if len(receipt["cells"]) != 4 or [r["cell"] for r in receipt["cells"]] != ["monitor-null", *execute.CELLS]:
        raise ValueError("four-cell sequence mismatch")
    source_hashes = {
        "supervisor": manifest["source_sha256"]["research/icperf_prime63_monitor_phase_20261018/monitor.py"],
        "solver": manifest["source_sha256"]["research/icperf_prime63_monitor_phase_20261018/instrumented_backend.py"]}
    verified = censored = unattempted = 0
    if receipt.get("schema") != "icperf-prime63-m2-diagnostic-raw-v1":
        raise ValueError("raw receipt schema mismatch")
    for row in receipt["cells"]:
        cell = row["cell"]
        if not row["attempted"]:
            if cell == "monitor-null":
                raise ValueError("null control unattempted")
            if row.get("reason") not in {"monitor_null_control_failed", "total_wall_censored",
                                         "instrumentation_or_resource_stop", "solver_or_worker_error"}:
                raise ValueError("unattempted reason missing")
            unattempted += 1
            continue
        base = f"{cell}/call/"
        for name in ("phase.jsonl", "stdout.raw", "stderr.raw"):
            if base+name not in archived:
                raise ValueError("missing required raw member")
        if row["trace"]["sha256"] != sha_bytes(archived[base+"phase.jsonl"]):
            raise ValueError("trace digest mismatch")
        if row["stdout_sha256"] != sha_bytes(archived[base+"stdout.raw"]) or \
                row["stderr_sha256"] != sha_bytes(archived[base+"stderr.raw"]):
            raise ValueError("stdout/stderr digest mismatch")
        stop = row["stop"]
        trace = verify_trace(archived[base+"phase.jsonl"], stop, source_hashes,
                             require_sample=cell != "monitor-null" and stop != "infrastructure_monitor_error")
        if cell == "monitor-null":
            if stop != "infrastructure_monitor_error" or (row["fault"] or {}).get("code") != "unreadable_live_root":
                raise ValueError("monitor null control failed")
            continue
        system = next(r for r in fixed if r["cell"] == cell)
        request_name = f"{cell}/request.json"
        if request_name not in archived or archived[request_name] != execute.canonical(system) \
                or row["request_sha256"] != sha_bytes(archived[request_name]):
            raise ValueError("fixed request/raw mismatch")
        response_name = base+"response.json"
        response = archived.get(response_name)
        if response is None:
            if row.get("response_sha256") is not None:
                raise ValueError("missing response digest mismatch")
            if stop not in {"timeout_censored", "memory_censored", "scratch_censored"}:
                raise ValueError("missing response without bounded censor")
            censored += 1
            continue
        if row.get("response_sha256") != sha_bytes(response):
            raise ValueError("response digest mismatch")
        parsed = _json_bytes(response)
        if stop != "exited":
            if stop not in {"timeout_censored", "memory_censored", "scratch_censored"}:
                raise ValueError("response under monitor fault is unqualified")
            censored += 1
            continue
        if row["exit_code"] != 0 and parsed.get("status") == "ok":
            raise ValueError("successful response with nonzero worker exit")
        status = parsed.get("status")
        if trace["solver_status"] != status:
            raise ValueError("solver phase terminal/response mismatch")
        if status == "certified_no_solution":
            verify_selected(system, {"variables": witness[cell]["root"]}, witness[cell]["selected"])
            raise ValueError("producer no-solution contradicted by archived full-point witness")
        if status == "model_cap_censored":
            if parsed.get("quotient_lower_bound") != execute.MODEL_CAP + 1 \
                    or parsed.get("roots") != [] or parsed.get("variety_called") is not False:
                raise ValueError("invalid model-cap censor")
            censored += 1
            continue
        if status != "ok" or type(parsed.get("root_count")) is not int \
                or parsed["root_count"] != len(parsed.get("roots", [])) \
                or type(parsed.get("quotient_dimension")) is not int \
                or not 1 <= parsed["quotient_dimension"] <= execute.MODEL_CAP \
                or parsed.get("variety_called") is not True:
            raise ValueError("invalid positive response")
        roots = parsed["roots"]
        checked = [reconstruct_selected(system, r) for r in roots]
        planted = witness[cell]["root"]
        if planted not in [r.get("variables") for r in roots]:
            raise ValueError("archived planted witness missing from roots")
        verify_selected(system, {"variables": planted}, witness[cell]["selected"])
        if not checked:
            raise ValueError("empty positive root list")
        verified += 1
    return {"status": "integrity_pass", "positive_verified": verified,
            "positive_censored": censored, "positive_unattempted": unattempted,
            "scientific_interpretation": None}


def verify(run_dir: Path, plan: Path, owner: str, epoch: int, trial_id: str) -> dict:
    authority = execute.admit(plan, owner, epoch, run_dir=run_dir, trial_id=trial_id)
    output = Path(run_dir) / "diagnostic"
    receipt = execute.exact_json(output / "receipt.json")
    manifest = execute.manifest_bindings()
    if (receipt["plan_sha256"] != authority["plan_sha256"]
            or receipt["launch_sha256"] != authority["launch_sha256"]
            or receipt["run_id"] != authority["run_id"]
            or receipt["trial_id"] != trial_id
            or receipt["source_manifest_sha256"] != execute.sha(execute.HERE / "input_manifest.json")
            or receipt["claim_owner"] != owner or receipt["claim_epoch"] != epoch):
        raise ValueError("plan/launch/source/claim receipt binding mismatch")
    archived = verify_archive(output, receipt)
    return verify_result(receipt, archived, manifest, execute.fixed_requests(), archived_witnesses())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--owner", required=True)
    p.add_argument("--epoch", required=True, type=int)
    p.add_argument("--run-dir", required=True, type=Path)
    p.add_argument("--trial-id", required=True)
    args = p.parse_args()
    print(json.dumps(verify(args.run_dir, args.plan, args.owner, args.epoch, args.trial_id), sort_keys=True))


if __name__ == "__main__":
    main()
