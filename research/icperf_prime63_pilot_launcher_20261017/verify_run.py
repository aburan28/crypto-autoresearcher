"""Independent polynomial/full-point and raw-archive checker for a later panel."""
from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import tarfile
from decimal import Decimal
from pathlib import Path

from sage.all import EllipticCurve, GF


def read(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as stream:
        return json.load(stream, parse_int=int, parse_float=Decimal)


def evaluate(eq, values, p):
    total = 0
    for term in eq:
        product = int(term["coefficient"])
        for index, power in term["powers"]:
            product = product * pow(values[index], int(power), p) % p
        total = (total + product) % p
    return total


def exact_integer(value):
    if type(value) is int:
        return value
    if isinstance(value, str) and value and value.lstrip("-").isdigit():
        return int(value, 10)
    raise ValueError("nonintegral or rounded coordinate")


def verify_explicit(system, root, ys):
    """Demand a polynomial root and a signed lift to the *full* target point."""
    if not isinstance(root, dict) or "variables" not in root or not isinstance(root["variables"], dict):
        return {"accepted": False, "reason": "missing_polynomial_root"}
    c = system["curve"]
    p = int(c["p"])
    names = system["variables"]
    if set(root["variables"]) != set(names):
        return {"accepted": False, "reason": "root_variables"}
    try:
        values = [exact_integer(root["variables"][name]) for name in names]
    except (TypeError, ValueError):
        return {"accepted": False, "reason": "root_coordinate"}
    if any(not 0 <= value < p for value in values):
        return {"accepted": False, "reason": "root_range"}
    if any(evaluate(eq, values, p) for eq in system["equations"]):
        return {"accepted": False, "reason": "polynomial_nonzero"}
    m = int(system["m"])
    xs = values[:m]
    allowed = {int(point[0]) for point in system["base_points"]}
    if len(allowed) != len(system["base_points"]) or any(x not in allowed for x in xs):
        return {"accepted": False, "reason": "base_membership"}
    if system["arm"] == "coset":
        params = system["base_parameters"]
        constant = pow(int(params["coset"]), int(params["d"]), p)
        if any(pow(x, int(params["d"]), p) != constant for x in xs):
            return {"accepted": False, "reason": "coset_gate"}
    E = EllipticCurve(GF(p), [int(c["a"]), int(c["b"])])
    lifts = []
    for x in xs:
        points = sorted(E.lift_x(GF(p)(x), all=True), key=lambda q: int(q[1]))
        if not points:
            return {"accepted": False, "reason": "nonlifting_x"}
        lifts.append(points)
    if ys is not None:
        if len(ys) != m:
            return {"accepted": False, "reason": "sign_arity"}
        lifts = [[q for q in row if int(q[1]) == int(ys[i])] for i, row in enumerate(lifts)]
        if any(not row for row in lifts):
            return {"accepted": False, "reason": "wrong_sign"}
    target = E([int(v) for v in system["target_point"]])
    for points in itertools.product(*lifts):
        total = E(0)
        for point in points:
            total += point
        if total == target:
            return {"accepted": True, "reason": "exact_polynomial_and_full_point",
                    "ys": [str(int(q[1])) for q in points]}
    return {"accepted": False, "reason": "full_target_mismatch"}


def verify_root(system, root):
    return verify_explicit(system, root, None)


def verify_raw_archive(output_dir):
    """Check listed raw bytes against disk and tar, with no extra tar members."""
    output_dir = Path(output_dir)
    receipt = read(output_dir / "receipt.json")
    manifest = receipt["raw_files"]
    listed = {row["path"] for row in manifest}
    if len(listed) != len(manifest):
        raise ValueError("duplicate raw manifest path")
    actual = {str(p.relative_to(output_dir)) for p in output_dir.rglob("*")
              if p.is_file() and p.name not in ("receipt.json", "raw.tar.gz")}
    if actual != listed:
        raise ValueError("missing or extra raw file")
    tar_path = output_dir / "raw.tar.gz"
    if hashlib.sha256(tar_path.read_bytes()).hexdigest() != receipt["raw_tar_sha256"]:
        raise ValueError("altered tar digest")
    with tarfile.open(tar_path, "r:gz") as tar:
        members = tar.getmembers()
        if {m.name for m in members} != listed or len(members) != len(listed):
            raise ValueError("tar manifest coverage")
        for row in manifest:
            path = output_dir / row["path"]
            data = path.read_bytes()
            if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise ValueError("raw digest mismatch")
            archived = tar.extractfile(row["path"])
            if archived is None or archived.read() != data:
                raise ValueError("tar byte mismatch")
    return {"status": "pass", "raw_files": len(manifest)}


def verify_panel(output_dir, schedule):
    receipt = read(Path(output_dir) / "receipt.json")
    if [r["cell"] for r in receipt["cells"]] != [r["id"] for r in schedule]:
        raise ValueError("schedule changed or cell omitted")
    if len(schedule) != 27 or receipt["attempted"] + receipt["unattempted"] != 27:
        raise ValueError("attempt accounting")
    verify_raw_archive(output_dir)
    checked = 0
    for record, spec in zip(receipt["cells"], schedule):
        if not record["attempted"] or not record.get("response_sha256"):
            continue
        response_path = Path(output_dir) / record["cell"] / "response.json"
        if hashlib.sha256(response_path.read_bytes()).hexdigest() != record["response_sha256"]:
            raise ValueError(f"response digest mismatch: {record['cell']}")
        response = read(response_path)
        status = response.get("status")
        if status not in {"ok", "certified_no_solution", "model_cap_censored",
                          "unsupported", "timeout", "memory"}:
            raise ValueError(f"missing or invalid response status: {record['cell']}")
        if status != "ok":
            continue
        roots = response.get("roots")
        if not isinstance(roots, list) or type(response.get("root_count")) is not int \
                or response["root_count"] != len(roots):
            raise ValueError(f"root_count or roots missing/mismatch: {record['cell']}")
        for root in roots:
            verdict = verify_root(spec["request"], root)
            if not verdict["accepted"]:
                raise ValueError(f"false root: {record['cell']}: {verdict['reason']}")
            checked += 1
    return {"status": "pass", "roots_checked": checked, "cells": 27}
