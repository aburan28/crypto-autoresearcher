"""Independent exact polynomial, lift, full-point and raw-archive checker."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import tarfile
from decimal import Decimal
from pathlib import Path

import execute


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(value):
    if type(value) is int:
        return value
    if isinstance(value, str) and value and value.lstrip("-").isdigit():
        return int(value, 10)
    raise ValueError("nonintegral integer or coordinate")


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
        if not a:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def sqrt_mod(value: int, p: int) -> int | None:
    value %= p
    if value == 0:
        return 0
    if pow(value, (p - 1)//2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(value, (p + 1)//4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1)//2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(value, q, p), pow(value, (q + 1)//2, p)
    while t != 1:
        i, v = 1, t*t % p
        while i < m and v != 1:
            v = v*v % p
            i += 1
        if i == m:
            raise ValueError("Tonelli-Shanks invariant failed")
        b = pow(c, 1 << (m - i - 1), p)
        r, t, c, m = r*b % p, t*b*b % p, b*b % p, i
    return r


def add(P, Q, p: int, a: int):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        slope = (3*x1*x1 + a) * pow(2*y1, -1, p) % p
    else:
        slope = (y2-y1) * pow((x2-x1) % p, -1, p) % p
    x3 = (slope*slope-x1-x2) % p
    return x3, (slope*(x1-x3)-y1) % p


def point(value, p: int, a: int, b: int):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("point must have x,y")
    x, y = map(exact, value)
    if not 0 <= x < p or not 0 <= y < p or (y*y-x*x*x-a*x-b) % p:
        raise ValueError("invalid curve point")
    return x, y


def verify_root(system: dict, root: dict) -> None:
    curve = system["curve"]
    p, a, b = (exact(curve[key]) for key in ("p", "a", "b"))
    if not prime64(p) or p <= 3 or (4*a**3+27*b**2) % p == 0:
        raise ValueError("unsupported or singular prime curve")
    names = system["variables"]
    if not isinstance(root, dict) or set(root.get("variables", {})) != set(names):
        raise ValueError("root variables mismatch")
    values = [exact(root["variables"][name]) for name in names]
    if any(not 0 <= value < p for value in values):
        raise ValueError("root coordinate out of field")
    for equation in system["equations"]:
        total = 0
        for term in equation:
            product = exact(term["coefficient"]) % p
            for index, power in term["powers"]:
                index, power = exact(index), exact(power)
                if not 0 <= index < len(values) or power < 0:
                    raise ValueError("bad monomial")
                product = product*pow(values[index], power, p) % p
            total = (total+product) % p
        if total:
            raise ValueError("polynomial is nonzero")
    m = exact(system["m"])
    xs = values[:m]
    base = [point(row, p, a, b) for row in system["base_points"]]
    allowed = {row[0] for row in base}
    if len(allowed) != len(base) or any(x not in allowed for x in xs):
        raise ValueError("base membership failed")
    if system["arm"] == "coset":
        params = system["base_parameters"]
        d, c = exact(params["d"]), exact(params["coset"])
        if any(pow(x, d, p) != pow(c, d, p) for x in xs):
            raise ValueError("coset gate failed")
    target = point(system["target_point"], p, a, b)
    lifts = []
    for x in xs:
        y = sqrt_mod((x*x*x+a*x+b) % p, p)
        if y is None:
            raise ValueError("x does not lift")
        lifts.append(sorted({(x, y), (x, -y % p)}))
    if "ys" in root:
        ys = root["ys"]
        if not isinstance(ys, list) or len(ys) != m:
            raise ValueError("signed lift arity")
        lifts = [[Q for Q in options if Q[1] == exact(ys[i])]
                 for i, options in enumerate(lifts)]
        if any(not options for options in lifts):
            raise ValueError("wrong signed lift")
    for options in itertools.product(*lifts):
        total = None
        for Q in options:
            total = add(total, Q, p, a)
        if total == target:
            return
    raise ValueError("full target point mismatch")


def verify_archive(panel_dir: Path, receipt: dict) -> dict[str, bytes]:
    rows = receipt["raw_files"]
    names = [row["path"] for row in rows]
    if len(set(names)) != len(names) or any(not name or name.startswith("/")
                                         or ".." in Path(name).parts for name in names):
        raise ValueError("invalid raw archive manifest")
    actual = {str(p.relative_to(panel_dir)) for p in panel_dir.rglob("*")
              if p.is_file() and p.name not in ("receipt.json", "raw.tar.gz")}
    # The tar and receipt are canonical custody. Discarded scratch cell files
    # are allowed after archive; a partially present disk tree is not.
    if actual and actual != set(names):
        raise ValueError("partial or extra disk raw file tree")
    archive = panel_dir / "raw.tar.gz"
    if sha(archive) != receipt["raw_tar_sha256"]:
        raise ValueError("archive hash mismatch")
    contents = {}
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        if (len(members) != len(names) or {member.name for member in members} != set(names)
                or any(not member.isfile() for member in members)):
            raise ValueError("archive coverage mismatch")
        for row in rows:
            member = tar.extractfile(row["path"])
            if member is None:
                raise ValueError("missing archived raw member")
            data = member.read()
            if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise ValueError("raw file hash mismatch")
            disk = panel_dir / row["path"]
            if disk.is_symlink():
                raise ValueError("symlink raw file")
            if disk.is_file() and disk.read_bytes() != data:
                raise ValueError("disk and archived raw bytes mismatch")
            contents[row["path"]] = data
    return contents


def verify(run_dir: Path, plan: Path, owner: str, epoch: int, trial_id: str,
           *, root: Path = execute.ROOT, rows: list[dict] | None = None) -> dict:
    authority = execute.admit(plan, owner, epoch, root=root,
                              run_dir=run_dir, trial_id=trial_id)
    panel_dir = run_dir / "panel"
    receipt = execute.read(panel_dir / "receipt.json")
    raw = execute.read(run_dir / "raw-result.json")
    manifest = execute.read(run_dir / "manifest.yaml")
    if rows is None:
        rows = execute.schedule()
    if len(rows) != 27 or [r["id"] for r in rows] != [c["cell"] for c in receipt["cells"]]:
        raise ValueError("27-cell schedule mismatch")
    if (receipt["attempted"] + receipt["unattempted"] != 27
            or receipt["attempted"] != sum(c["attempted"] for c in receipt["cells"])):
        raise ValueError("attempt accounting mismatch")
    if (receipt["plan_sha256"] != authority["plan_sha256"]
            or receipt["launch_sha256"] != authority["launch_sha256"]
            or receipt["run_id"] != authority["run_id"]
            or receipt["trial_id"] != trial_id
            or raw["plan_sha256"] != authority["plan_sha256"]
            or raw["launch_sha256"] != authority["launch_sha256"]
            or raw["run_id"] != authority["run_id"]
            or raw["trial_id"] != trial_id
            or raw["attempted"] != receipt["attempted"]
            or raw["unattempted"] != receipt["unattempted"]
            or raw["cells"] != receipt["cells"]
            or raw["panel_receipt_sha256"] != sha(panel_dir / "receipt.json")
            or raw["raw_archive_sha256"] != sha(run_dir / "raw.tar.gz")
            or (run_dir / "raw.tar.gz").read_bytes() != (panel_dir / "raw.tar.gz").read_bytes()
            or manifest["run"]["id"] != authority["run_id"]):
        raise ValueError("run/plan/launch/raw binding mismatch")
    archived = verify_archive(panel_dir, receipt)
    checked = controls_verified = controls_censored = 0
    no_response_censored = {"timeout_censored", "memory_censored",
                            "scratch_censored", "panel_wall_censored"}
    for record, row in zip(receipt["cells"], rows):
        if not record["attempted"]:
            if row["kind"] == "positive":
                controls_censored += 1
            continue
        if not record.get("response_sha256"):
            if record.get("status") not in no_response_censored:
                raise ValueError("missing response without bounded censoring")
            if row["kind"] == "positive":
                controls_censored += 1
            continue
        response_name = record["cell"] + "/response.json"
        response_bytes = archived.get(response_name)
        if response_bytes is None or hashlib.sha256(response_bytes).hexdigest() != record["response_sha256"]:
            raise ValueError("response hash mismatch")
        response = json.loads(response_bytes.decode("utf-8"), parse_int=int,
                              parse_float=Decimal)
        status = response.get("status")
        if status not in {"ok", "certified_no_solution", "model_cap_censored",
                          "unsupported", "timeout", "memory"}:
            raise ValueError("missing or unknown response status")
        if record.get("status") != status:
            raise ValueError("receipt/response status mismatch")
        if status != "ok":
            if row["kind"] == "positive":
                controls_censored += 1
            continue
        roots = response.get("roots")
        if not isinstance(roots, list) or type(response.get("root_count")) is not int \
                or response["root_count"] != len(roots):
            raise ValueError("root count mismatch")
        for candidate in roots:
            verify_root(row["request"], candidate)
            checked += 1
        if row["kind"] == "positive":
            witness = next(w["root"] for w in execute.read(execute.OLD / "planted_witnesses.json")["witnesses"]
                           if w["cell"] == row["id"])
            if witness not in [candidate.get("variables") for candidate in roots]:
                raise ValueError("planted control witness missing")
            controls_verified += 1
    return {"status": "integrity_pass", "cells": 27, "roots_checked": checked,
            "positive_controls_verified": controls_verified,
            "positive_controls_censored": controls_censored,
            "positive_control_status": "verified" if controls_verified == 6 else "censored"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--owner", required=True)
    p.add_argument("--epoch", required=True, type=int)
    p.add_argument("--trial-id", required=True)
    p.add_argument("--run-dir", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(verify(a.run_dir, a.plan, a.owner, a.epoch, a.trial_id),
                     sort_keys=True))


if __name__ == "__main__":
    main()
