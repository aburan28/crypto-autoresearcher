#!/usr/bin/env python3
"""Source-locked synthetic input custodian; never runs an ECDLP solver.

The public generate entry point refuses to compile, write cohort outputs,
or draw private entropy until committed source/protocol/lock bindings and an
external post-freeze nonce pass. The C++ helper only searches public fixtures.
Public Q files and private scalar/seed records are written to separate trees.
This is an interface separation, not a claim of OS-enforced confidentiality.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import subprocess
import sys
from datetime import datetime, timezone

from curve_identity import curve_identity

HERE = Path(__file__).resolve().parent
BITS = (12, 14, 16, 18)
CURVES_PER_SIZE = 16
REPLICATES = 2
TARGETS_PER_CELL = 64
PART_LIMIT = 60 * 1024
FIXTURE_COLUMNS = ("fixture_id", "stratum", "p", "a", "b", "gx", "gy", "r", "N", "seed")
TARGET_COLUMNS = ("fixture_id", "replicate", "target_id", "target_ordinal", "qx", "qy", "infinity")
SETTING_COLUMNS = ("cell_id", "fixture_id", "replicate", "dp_bits", "initial_chains",
                   "endpoint_cap", "max_precomp_ops", "max_online_ops", "seed")
TRUTH_COLUMNS = ("fixture_id", "replicate", "target_id", "target_ordinal", "k")
PUBLIC_SEED_DOMAIN = b"classical.ecdlp.endpoint-reuse.v1\0"
PRIVATE_SEED_DOMAIN = b"classical.ecdlp.endpoint-target-sampling.v1\0"
HEX64 = re.compile(r"[0-9a-f]{64}")
HEX40 = re.compile(r"[0-9a-f]{40}")


class Refused(ValueError):
    pass


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Refused(reason)


def canonical(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return digest(path.read_bytes())


def read_json(path: Path) -> dict:
    def unique(items):
        out = {}
        for key, value in items:
            require(key not in out, f"duplicate JSON key in {path}: {key}")
            out[key] = value
        return out
    try:
        value = json.loads(path.read_text(), object_pairs_hook=unique,
                           parse_constant=lambda x: (_ for _ in ()).throw(Refused(x)))
    except (OSError, ValueError) as exc:
        raise Refused(f"cannot read JSON {path}: {exc}") from exc
    require(isinstance(value, dict), f"not a JSON object: {path}")
    return value


def safe_relative(value: str) -> str:
    require(isinstance(value, str), "relative path must be a string")
    p = PurePosixPath(value)
    require(bool(value) and not p.is_absolute() and ".." not in p.parts and
            "." not in p.parts and str(p) == value, f"unsafe relative path: {value}")
    return value


def inside(root: Path, relative: str) -> Path:
    relative = safe_relative(relative)
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()), f"path escapes root: {relative}")
    return path


def utc(value: str) -> datetime:
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise Refused(f"invalid timestamp: {value}") from exc
    require(t.tzinfo is not None, "timestamps must state timezone")
    return t.astimezone(timezone.utc)


def git(repo: Path, *args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True)
    require(result.returncode == 0, f"git {' '.join(args)} failed: " +
            result.stderr.decode(errors="replace")[:500])
    return result.stdout


def check_commit(repo: Path, value: str) -> None:
    require(isinstance(value, str) and HEX40.fullmatch(value) is not None,
            "commit must be a full lowercase object ID")
    require(git(repo, "cat-file", "-t", value).strip() == b"commit", "object is not a commit")


def required_source_paths(prefix: str) -> set[str]:
    paths = {"prepare.py", "public_inputs.py", "curve_identity.py", "src/common.hpp", "src/prepare_cohort.cpp",
             "exclusions/manifest.json"}
    provenance = read_json(HERE / "exclusions/manifest.json")
    paths.update(item["path"] for item in provenance["sources"])
    return {f"{prefix}/{safe_relative(p)}" for p in paths}


def verify_bindings(repo: Path, lock_path: Path, lock_commit: str,
                    protocol_sha256: str, nonce_path: Path) -> dict:
    """Verify immutable byte/chronology bindings; schema validation is separate."""
    repo = repo.resolve()
    lock_path = lock_path.resolve()
    require(lock_path.is_relative_to(repo), "source lock must be inside checkout")
    lock_rel = lock_path.relative_to(repo).as_posix()
    lock_bytes = lock_path.read_bytes()
    lock = read_json(lock_path)
    require(lock.get("schema") == "classical.ecdlp.endpoint-cohort-lock/v1",
            "unsupported source-lock schema")
    check_commit(repo, lock_commit)
    require(git(repo, "show", f"{lock_commit}:{lock_rel}") == lock_bytes,
            "lock bytes are not committed at --lock-commit")
    source_commit = lock.get("source_commit")
    protocol_commit = lock.get("protocol_commit")
    check_commit(repo, source_commit)
    check_commit(repo, protocol_commit)
    git(repo, "merge-base", "--is-ancestor", source_commit, protocol_commit)
    git(repo, "merge-base", "--is-ancestor", protocol_commit, lock_commit)
    prefix = safe_relative(lock.get("source_prefix", ""))
    require(inside(repo, prefix) == HERE, "source prefix is not this generator")
    require(lock.get("design") == {"subgroup_bits": list(BITS), "curves_per_size": 16,
                                  "replicates": 2, "targets_per_cell": 64,
                                  "endpoint_cap_multiplier": 4},
            "source lock design differs from fixed generator design")
    files = lock.get("files")
    require(isinstance(files, dict), "source lock lacks files")
    require(required_source_paths(prefix) <= set(files), "source lock omits a generator dependency")
    for relative, expected in files.items():
        require(isinstance(expected, str) and HEX64.fullmatch(expected) is not None,
                "invalid source SHA-256")
        path = inside(repo, relative)
        raw = path.read_bytes()
        require(digest(raw) == expected, f"source differs from lock: {relative}")
        require(git(repo, "show", f"{source_commit}:{relative}") == raw,
                f"source differs from committed bytes: {relative}")
    require(HEX64.fullmatch(protocol_sha256) is not None, "invalid protocol hash")
    require(lock.get("protocol_sha256") == protocol_sha256, "protocol hash differs from lock")
    protocol_rel = safe_relative(lock.get("protocol_path", ""))
    protocol_path = inside(repo, protocol_rel)
    protocol_bytes = protocol_path.read_bytes()
    require(git(repo, "show", f"{protocol_commit}:{protocol_rel}") == protocol_bytes,
            "frozen protocol bytes are not committed")
    require(digest(protocol_bytes) == lock.get("protocol_file_sha256"),
            "protocol file hash differs from source lock")
    protocol = read_json(protocol_path)
    require(protocol.get("schema") == "experiment.protocol/v1", "not the current protocol schema")
    freeze = protocol.get("freeze", {})
    require(isinstance(freeze,dict), "protocol freeze block is not an object")
    require(freeze.get("status") == "frozen" and freeze.get("filed_before_affected_data") is True,
            "protocol is not prospectively frozen")
    require(freeze.get("protocol_sha256") == protocol_sha256 and
            digest(canonical({k: v for k, v in protocol.items() if k != "freeze"})) ==
            protocol_sha256, "frozen protocol hash mismatch")
    frozen_at = utc(freeze.get("frozen_at", ""))
    nonce = read_json(nonce_path)
    require(nonce.get("schema") == "classical.ecdlp.endpoint-cohort-nonce/v1",
            "unsupported external nonce schema")
    require(nonce.get("protocol_sha256") == protocol_sha256 and
            nonce.get("source_lock_sha256") == digest(lock_bytes),
            "nonce is not bound to this protocol/source lock")
    nonce_hex = nonce.get("nonce_hex", "")
    require(isinstance(nonce_hex, str) and HEX64.fullmatch(nonce_hex) is not None,
            "external nonce must be 32 lowercase-hex bytes")
    drawn_at = utc(nonce.get("drawn_at", ""))
    require(frozen_at <= drawn_at <= datetime.now(timezone.utc),
            "nonce must be drawn after freeze and not in the future")
    for commit in (source_commit,protocol_commit,lock_commit):
        committed_at = utc(git(repo,"show","-s","--format=%cI",commit).decode().strip())
        require(committed_at <= drawn_at, "nonce predates a required source/protocol/lock commit")
    return {"lock": lock, "protocol_path": protocol_path, "nonce": nonce,
            "lock_sha256": digest(lock_bytes), "nonce_file_sha256": sha(nonce_path),
            "lock_commit": lock_commit, "protocol_sha256": protocol_sha256}


def verify_official_protocol(repo: Path, protocol_path: Path, source_commit: str) -> str:
    tool = repo / "tools/experiment_protocol.py"
    require(tool.is_file(), "official protocol validator is not materialized")
    for relative in ("tools/experiment_protocol.py","schemas/experiment-protocol.v1.json"):
        path = inside(repo,relative)
        require(git(repo,"show",f"{source_commit}:{relative}") == path.read_bytes(),
                "official protocol validator/schema differs from source commit")
    result = subprocess.run([sys.executable, str(tool), "validate", str(protocol_path)],
                            cwd=repo, text=True, capture_output=True)
    require(result.returncode == 0, "official protocol validator refused:\n" +
            result.stdout + result.stderr)
    return result.stdout + result.stderr


def public_seed(protocol_sha256: str, nonce_hex: str, fixture_id: str,
                replicate: int, purpose: str) -> int:
    payload = PUBLIC_SEED_DOMAIN + b"\0".join(
        str(x).encode("ascii") for x in
        (protocol_sha256, nonce_hex, fixture_id, replicate, purpose))
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


class TargetStream:
    def __init__(self, private_root: bytes, protocol_hash: str, nonce: str,
                 fixture_id: str, replicate: int):
        require(len(private_root) == 32, "private target root must have 32 bytes")
        self.root = private_root
        self.domain = PRIVATE_SEED_DOMAIN + b"\0".join(
            str(x).encode("ascii") for x in (protocol_hash, nonce, fixture_id, replicate))
        self.counter = 0

    def bounded(self, n: int) -> int:
        require(n > 0, "invalid scalar range")
        limit = (1 << 256) - ((1 << 256) % n)
        while True:
            message = self.domain + b"\0" + self.counter.to_bytes(8, "big")
            self.counter += 1
            x = int.from_bytes(hmac.new(self.root, message, hashlib.sha256).digest(), "big")
            if x < limit:
                return x % n


def prime(n: int) -> bool:
    return n > 1 and all(n % d for d in range(2, math.isqrt(n)+1))


def add(p: int, a: int, left, right):
    if left is None:
        return right
    if right is None:
        return left
    x, y = left
    u, v = right
    if x == u and (y+v) % p == 0:
        return None
    slope = ((3*x*x+a)*pow(2*y, -1, p) if left == right
             else (v-y)*pow(u-x, -1, p)) % p
    xx = (slope*slope-x-u) % p
    return xx, (slope*(x-xx)-y) % p


def mul_affine(p: int, a: int, point, scalar: int):
    require(scalar >= 0, "negative scalar")
    result = None
    while scalar:
        if scalar & 1:
            result = add(p, a, result, point)
        point = add(p, a, point, point)
        scalar >>= 1
    return result


def mul_jacobian(p: int, a: int, point, scalar: int):
    """Separate projective implementation used for generating Q, not checking it."""
    require(scalar >= 0, "negative scalar")
    if point is None or scalar == 0:
        return None
    px, py = point
    x, y, z = 0, 1, 0
    for bit in bin(scalar)[2:]:
        if z and y:
            aa, bb = x*x % p, y*y % p
            cc = bb*bb % p
            dd = 2*((x+bb)*(x+bb)-aa-cc) % p
            zz = z*z % p
            ee = (3*aa+a*zz*zz) % p
            ff = ee*ee % p
            x, y, z = (ff-2*dd) % p, (ee*(dd-(ff-2*dd))-8*cc) % p, 2*y*z % p
        else:
            x, y, z = 0, 1, 0
        if bit == "1":
            if not z:
                x, y, z = px, py, 1
            else:
                zz = z*z % p
                uu = px*zz % p
                ss = py*z*zz % p
                hh, rr = (uu-x) % p, (ss-y) % p
                if hh == 0:
                    if rr:
                        x, y, z = 0, 1, 0
                    else:
                        aa, bb = x*x % p, y*y % p
                        cc = bb*bb % p
                        dd = 2*((x+bb)*(x+bb)-aa-cc) % p
                        ee = (3*aa+a*zz*zz) % p
                        ff = ee*ee % p
                        x, y, z = (ff-2*dd) % p, (ee*(dd-(ff-2*dd))-8*cc) % p, 2*y*z % p
                else:
                    h2 = hh*hh % p
                    ii = 4*h2 % p
                    jj = hh*ii % p
                    r2 = 2*rr % p
                    vv = x*ii % p
                    nx = (r2*r2-jj-2*vv) % p
                    x, y, z = nx, (r2*(vv-nx)-2*y*jj) % p, ((z+hh)*(z+hh)-zz-h2) % p
    if not z:
        return None
    inv = pow(z, -1, p)
    return x*inv*inv % p, y*inv*inv*inv % p


def read_tsv(path: Path, expected: tuple[str, ...] | None = None) -> list[dict]:
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if expected is not None:
            require(tuple(reader.fieldnames or ()) == expected, f"wrong TSV header: {path}")
        return list(reader)


def tsv_bytes(columns: tuple[str, ...], rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def write_once(path: Path, data: bytes, private: bool = False, bounded: bool = True) -> None:
    if bounded:
        require(len(data) <= PART_LIMIT, f"output exceeds part limit: {path}")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600 if private else 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)


def write_json(path: Path, value: object, private: bool = False) -> None:
    write_once(path, json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False).encode()+b"\n",
               private, bounded=False)
    require(path.stat().st_size < 1024*1024, "metadata exceeds repository limit")


def exclusion_union() -> tuple[set[tuple[int, int, int]], dict]:
    manifest = read_json(HERE / "exclusions/manifest.json")
    require(manifest.get("schema") == "classical.ecdlp.endpoint-cohort-exclusions/v1",
            "invalid exclusion manifest")
    union = set()
    for item in manifest["sources"]:
        path = inside(HERE, item["path"])
        require(sha(path) == item["sha256"], f"exclusion source changed: {path}")
        rows = read_tsv(path)
        require(len(rows) == item["rows"], "exclusion row count changed")
        union.update(tuple(int(row[k]) for k in ("p", "a", "b")) for row in rows)
    require(len(union) == manifest["unique_curve_models"] == 114, "exclusion union changed")
    require(union == {(int(x["p"]), int(x["a"]), int(x["b"])) for x in manifest["union"]},
            "exclusion union metadata differs from source rows")
    return union, manifest


def fixture_identity(row: dict) -> dict:
    p, a, b, x, y, r, n = (int(row[k]) for k in ("p", "a", "b", "gx", "gy", "r", "N"))
    field = {"characteristic": p, "degree": 1, "representation": "prime-field",
             "modulus": p, "element_encoding": "canonical_integer"}
    curve = {"model": "short_weierstrass", "a": a, "b": b, "subgroup_order": r,
             "cofactor": n//r, "generator": {"x": x, "y": y},
             "target_group": "prime-order subgroup generated by generator"}
    return {"fixture_id": row["fixture_id"], "field": field, "curve": curve,
            **curve_identity(field, curve, "er")}


def certify_fixture(row: dict, full_census: bool = True) -> dict:
    p, a, b, x, y, r, n = (int(row[k]) for k in ("p", "a", "b", "gx", "gy", "r", "N"))
    require(3 < p <= 1048575 and prime(p) and 2 < r <= 524287 and prime(r),
            "field/subgroup bounds or primality")
    require(0 < a < p and 0 < b < p and (4*a*a*a+27*b*b) % p != 0,
            "special-j, noncanonical or singular curve")
    require(n % r == 0 and 1 <= n//r <= 3 and math.gcd(n//r, r) == 1,
            "cofactor certificate")
    require(n not in (p, p+1) and r != p and (p+1-n)**2 <= 4*p,
            "ordinary non-anomalous/Hasse certificate")
    require(0 <= x < p and 0 <= y < p and (y*y-x*x*x-a*x-b) % p == 0 and
            mul_affine(p, a, (x,y), r) is None, "base point order certificate")
    exact_n = None
    if full_census:
        exact_n = 1
        for xx in range(p):
            rhs = (xx*xx*xx+a*xx+b) % p
            symbol = pow(rhs, (p-1)//2, p)
            require(symbol in (0,1,p-1), "invalid Legendre symbol")
            exact_n += 1 if rhs == 0 else (2 if symbol == 1 else 0)
        require(exact_n == n, "independent Python Euler census differs")
    return {"fixture_id": row["fixture_id"], "p": p, "r": r, "N": n, "cofactor": n//r,
            "python_euler_count": exact_n, "prime_order_witness_checked": True,
            "identity": fixture_identity(row)}


def settings_for(fixtures: list[dict], protocol_hash: str, nonce: str) -> list[dict]:
    rows = []
    for f in fixtures:
        r = int(f["r"])
        t = r.bit_length()//3
        denominator = 1 << (2*t)
        c0 = (r+denominator//2)//denominator
        require(c0 > 0, "verified-only growth cannot bootstrap from zero advice")
        cap = 4*c0
        root = math.isqrt(r)
        ceil_sqrt = root if root*root == r else root+1
        for rep in range(REPLICATES):
            rows.append({"cell_id": f"{f['fixture_id']}-rep{rep}", "fixture_id": f["fixture_id"],
                         "replicate": rep, "dp_bits": t, "initial_chains": c0, "endpoint_cap": cap,
                         "max_precomp_ops": 256*cap*(1 << t)+8192,
                         "max_online_ops": 256*ceil_sqrt+8192,
                         "seed": public_seed(protocol_hash, nonce, f["fixture_id"], rep, "solver_cell")})
    return rows


def split_history(source: Path, public: Path) -> dict:
    parts, block, rows = [], bytearray(), 0
    full_hash = hashlib.sha256()
    total_rows = 0
    def flush():
        nonlocal block, rows
        if not block:
            return
        name = f"fixture-history-{len(parts):04d}.jsonl"
        data = bytes(block)
        write_once(public/name, data)
        parts.append({"path": name, "bytes": len(data), "rows": rows, "sha256": digest(data)})
        block, rows = bytearray(), 0
    with source.open("rb") as stream:
        for line in stream:
            require(len(line) <= PART_LIMIT, "overlong input-history row")
            if len(block)+len(line) > PART_LIMIT:
                flush()
            block.extend(line)
            rows += 1
            total_rows += 1
            full_hash.update(line)
    flush()
    manifest = {"schema": "classical.ecdlp.lossless-parts/v1", "logical_stream": "fixture-history.jsonl",
                "sha256": full_hash.hexdigest(), "rows": total_rows, "parts": parts,
                "scope": "input candidate accept/reject history; not a solver measurement"}
    write_json(public/"fixture-history-manifest.json", manifest)
    return manifest


def generate(args) -> dict:
    repo = args.repo_root.resolve()
    binding = verify_bindings(repo, args.source_lock, args.lock_commit,
                              args.protocol_sha256, args.nonce)
    official_log = verify_official_protocol(repo, binding["protocol_path"],binding["lock"]["source_commit"])
    excluded, exclusion_manifest = exclusion_union()
    out = args.out.resolve()
    require(not out.exists(), "refuse existing preparation tree; retain every attempt")
    out.mkdir(parents=True)
    public, private, work = out/"public", out/"private", out/"work"
    public.mkdir()
    private.mkdir(mode=0o700)
    work.mkdir()
    write_once(public/"external-nonce.json",args.nonce.read_bytes())
    write_once(work/"protocol-validation.txt", official_log.encode())
    compiler = ["g++", "-std=c++20", "-O2", "-Wall", "-Wextra", "-Wconversion",
                "-Wshadow", "-Wpedantic", "-Werror", str(HERE/"src/prepare_cohort.cpp"),
                "-o", str(work/"prepare-cohort")]
    built = subprocess.run(compiler, text=True, capture_output=True)
    write_once(work/"compile.txt", (built.stdout+built.stderr).encode())
    require(built.returncode == 0, "input generator build failed")
    union_data = tsv_bytes(("p","a","b"), [{"p":p,"a":a,"b":b} for p,a,b in sorted(excluded)])
    write_once(work/"excluded-union.tsv", union_data)
    nonce = binding["nonce"]["nonce_hex"]
    seed = public_seed(args.protocol_sha256, nonce, "cohort", 0, "curve_generation")
    command = [str(work/"prepare-cohort"), "--curves", str(public/"fixtures.tsv"),
               str(work/"fixture-history.jsonl"), str(work/"excluded-union.tsv"), str(seed)]
    made = subprocess.run(command, text=True, capture_output=True)
    write_once(work/"curve-generation.txt", (made.stdout+made.stderr).encode())
    require(made.returncode == 0, "fixture search failed; preserve output and retry as a new attempt")
    fixtures = read_tsv(public/"fixtures.tsv", FIXTURE_COLUMNS)
    require(len(fixtures) == 64, "incomplete fixture cohort")
    require(len({f["fixture_id"] for f in fixtures}) == 64, "duplicate fixture ID")
    seen = set()
    certificates = []
    for f in fixtures:
        key = tuple(int(f[k]) for k in ("p","a","b"))
        require(key not in excluded | seen and f["stratum"] == "ordinary", "fixture reuse/stratum")
        seen.add(key)
        certificates.append(certify_fixture(f))
    require(all(sum(int(f["r"]).bit_length() == bits for f in fixtures) == 16 for bits in BITS),
            "wrong per-size fixture count")
    history = split_history(work/"fixture-history.jsonl", public)
    write_json(public/"fixture-certificates.json",
               {"schema": "classical.ecdlp.endpoint-fixture-certificates/v1", "fixtures": certificates,
                "excluded_unique_models": 114, "exclusion_manifest_sha256": sha(HERE/"exclusions/manifest.json"),
                "history_sha256": history["sha256"], "new_identity_scope": "exact representation, not isomorphism class"})
    write_json(public/"fixture-seal-before-targets.json",
               {"schema": "classical.ecdlp.endpoint-fixture-seal/v1",
                "fixtures_sha256": sha(public/"fixtures.tsv"),
                "certificates_sha256": sha(public/"fixture-certificates.json"),
                "source_lock_sha256": binding["lock_sha256"], "lock_commit": args.lock_commit,
                "protocol_sha256": args.protocol_sha256, "nonce_file_sha256": binding["nonce_file_sha256"],
                "private_target_entropy_not_yet_drawn": True})
    # No private root exists before every preceding check/seal has succeeded.
    private_root = secrets.token_bytes(32)
    generated_at = datetime.now(timezone.utc).isoformat()
    root_record = {"schema": "classical.ecdlp.endpoint-private-target-root/v1",
                   "private_root_hex": private_root.hex(), "generated_at": generated_at,
                   "protocol_sha256": args.protocol_sha256, "external_nonce": nonce,
                   "source_lock_sha256": binding["lock_sha256"],
                   "derivation": "HMAC-SHA256, endpoint-target-sampling.v1 NUL domain, per fixture/replicate, uint64BE counter; 256-bit rejection then mod r"}
    write_json(private/"target-root.json", root_record, private=True)
    write_json(public/"private-root-commitment-before-targets.json",
               {"schema":"classical.ecdlp.endpoint-private-root-commitment/v1",
                "withheld_root_record_sha256":sha(private/"target-root.json"),
                "protocol_sha256":args.protocol_sha256,
                "source_lock_sha256":binding["lock_sha256"],
                "fixture_seal_sha256":sha(public/"fixture-seal-before-targets.json"),
                "target_coordinates_not_yet_generated":True,
                "external_timestamp_attestation":False})
    public_parts, truth_parts = [], []
    logical_targets = bytearray(tsv_bytes(TARGET_COLUMNS, []))
    logical_truth = bytearray(tsv_bytes(TRUTH_COLUMNS, []))
    for f in fixtures:
        targets, truth = [], []
        p,a,r,gx,gy = (int(f[k]) for k in ("p","a","r","gx","gy"))
        for rep in range(REPLICATES):
            stream = TargetStream(private_root, args.protocol_sha256, nonce, f["fixture_id"], rep)
            for ordinal in range(TARGETS_PER_CELL):
                k = stream.bounded(r)
                q = mul_jacobian(p,a,(gx,gy),k)
                require(q == mul_affine(p,a,(gx,gy),k), "independent affine target equation check")
                require(mul_affine(p,a,q,r) is None, "public target membership check")
                qx,qy = q if q is not None else (0,0)
                target_id = f"{f['fixture_id']}-rep{rep}-t{ordinal:02d}"
                targets.append({"fixture_id":f["fixture_id"],"replicate":rep,"target_id":target_id,
                                "target_ordinal":ordinal,"qx":qx,"qy":qy,"infinity":int(q is None)})
                truth.append({"fixture_id":f["fixture_id"],"replicate":rep,"target_id":target_id,
                              "target_ordinal":ordinal,"k":k})
        name = f"targets-{f['fixture_id']}.tsv"
        target_data, truth_data = tsv_bytes(TARGET_COLUMNS,targets), tsv_bytes(TRUTH_COLUMNS,truth)
        write_once(public/name,target_data)
        write_once(private/name,truth_data,private=True)
        public_parts.append({"path":name,"fixture_id":f["fixture_id"],"rows":len(targets),
                             "bytes":len(target_data),"sha256":digest(target_data)})
        truth_parts.append({"path":name,"fixture_id":f["fixture_id"],"rows":len(truth),
                            "bytes":len(truth_data),"sha256":digest(truth_data)})
        logical_targets.extend(target_data.split(b"\n",1)[1])
        logical_truth.extend(truth_data.split(b"\n",1)[1])
    target_manifest = {"schema":"classical.ecdlp.endpoint-target-parts/v1","columns":list(TARGET_COLUMNS),
                       "rows":8192,"parts":public_parts,"logical_stream":"public-targets.tsv",
                       "logical_sha256":digest(logical_targets),"logical_bytes":len(logical_targets),
                       "combination":"one TSV header, parts in manifest order with each part header removed"}
    write_json(public/"public-targets-manifest.json",target_manifest)
    write_json(private/"target-truth-manifest.json",
               {"schema":"classical.ecdlp.endpoint-truth-parts/v1","columns":list(TRUTH_COLUMNS),
                "rows":8192,"parts":truth_parts,"logical_sha256":digest(logical_truth),
                "logical_bytes":len(logical_truth)})
    write_once(public/"settings.tsv",
               tsv_bytes(SETTING_COLUMNS,settings_for(fixtures,args.protocol_sha256,nonce)))
    write_json(public/"target-custody.json",
               {"schema":"classical.ecdlp.endpoint-target-custody/v1","fixtures":64,"replicates":2,
                "targets_per_cell":64,"target_ids":8192,"sampling":"uniform k in [0,r) independently with replacement",
                "public_target_manifest_sha256":sha(public/"public-targets-manifest.json"),
                "withheld_root_record_sha256":sha(private/"target-root.json"),
                "withheld_truth_manifest_sha256":sha(private/"target-truth-manifest.json"),
                "pre_target_root_commitment_sha256":sha(public/"private-root-commitment-before-targets.json"),
                "fixture_seal_sha256":sha(public/"fixture-seal-before-targets.json"),
                "source_lock_sha256":binding["lock_sha256"],"protocol_sha256":args.protocol_sha256,
                "nonce_file_sha256":binding["nonce_file_sha256"],"generated_at":generated_at,
                "private_root":"32 OS-random bytes drawn only after source/protocol checks and fixture seal",
                "private_labels_are_solver_inputs":False,
                "separation":"public/private process-interface convention; no OS-isolated blindness claim",
                "reveal_policy":"reveal roots and scalar parts only after all candidate outputs are sealed; compare prior commitments",
                "scalar_duplicates":"permitted by uniform sampling with replacement; target IDs remain distinct",
                "scientific_solver_measurement_performed":False})
    summary = {"schema":"classical.ecdlp.endpoint-cohort-preparation/v1","scope":"input_preparation_only",
               "fixtures":64,"target_ids":8192,"cells":128,"target_parts":len(public_parts),
               "fixture_manifest_sha256":sha(public/"fixtures.tsv"),
               "target_manifest_sha256":sha(public/"public-targets-manifest.json"),
               "logical_target_sha256":target_manifest["logical_sha256"],
               "settings_sha256":sha(public/"settings.tsv"),
               "solver_measurements_performed":False}
    write_json(public/"preparation-summary.json",summary)
    input_manifest = {
        "schema":"classical.ecdlp.endpoint-public-inputs/v1",
        "fixture_count":64,"cell_count":128,"target_count":8192,
        "fixture_path":"fixtures.tsv","settings_path":"settings.tsv",
        "targets_manifest_path":"public-targets-manifest.json",
        "protocol_sha256":args.protocol_sha256,
        "files":[{"path":p.relative_to(public).as_posix(),"bytes":p.stat().st_size,"sha256":sha(p)}
                 for p in sorted(public.rglob("*")) if p.is_file()]}
    write_json(public/"inputs-manifest.json",input_manifest)
    # The manifest is self-excluding; its digest is supplied to the public reader
    # from the frozen execution plan rather than trusted from its own contents.
    return {**summary,"inputs_manifest_sha256":sha(public/"inputs-manifest.json")}


def assemble(manifest_path: Path, out: Path) -> dict:
    manifest = read_json(manifest_path)
    require(manifest.get("schema") == "classical.ecdlp.endpoint-target-parts/v1",
            "not a public target manifest")
    require(manifest.get("columns") == list(TARGET_COLUMNS), "wrong target columns")
    content = bytearray(tsv_bytes(TARGET_COLUMNS, []))
    count = 0
    for item in manifest["parts"]:
        path = inside(manifest_path.parent,item["path"])
        data = path.read_bytes()
        require(digest(data) == item["sha256"] and len(data) == item["bytes"], "target part hash/size")
        require(len(data) <= PART_LIMIT, "oversized target part")
        rows = read_tsv(path,TARGET_COLUMNS)
        require(len(rows) == item["rows"], "target part rows")
        require(all(r["fixture_id"] == item["fixture_id"] for r in rows), "cross-fixture target part")
        count += len(rows)
        content.extend(data.split(b"\n",1)[1])
    require(count == manifest["rows"] and len(content) == manifest["logical_bytes"] and
            digest(content) == manifest["logical_sha256"], "logical target stream mismatch")
    write_once(out,bytes(content),bounded=False)
    return {"rows":count,"bytes":len(content),"sha256":digest(content),
            "scope":"lossless input reconstruction; runtime temporary file, not an unpartitioned Git artifact"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="mode", required=True)
    gen = commands.add_parser("generate")
    gen.add_argument("--repo-root",type=Path,required=True)
    gen.add_argument("--source-lock",type=Path,required=True)
    gen.add_argument("--lock-commit",required=True)
    gen.add_argument("--protocol-sha256",required=True)
    gen.add_argument("--nonce",type=Path,required=True)
    gen.add_argument("--out",type=Path,required=True)
    check = commands.add_parser("check-lock")
    check.add_argument("--repo-root",type=Path,required=True)
    check.add_argument("--source-lock",type=Path,required=True)
    check.add_argument("--lock-commit",required=True)
    check.add_argument("--protocol-sha256",required=True)
    check.add_argument("--nonce",type=Path,required=True)
    assembly = commands.add_parser("assemble-targets")
    assembly.add_argument("--manifest",type=Path,required=True)
    assembly.add_argument("--out",type=Path,required=True)
    args = parser.parse_args()
    try:
        if args.mode == "generate":
            result = generate(args)
        elif args.mode == "check-lock":
            binding = verify_bindings(args.repo_root,args.source_lock,args.lock_commit,
                                      args.protocol_sha256,args.nonce)
            text = verify_official_protocol(args.repo_root,binding["protocol_path"],binding["lock"]["source_commit"])
            result = {"bindings_valid":True,"official_protocol_validator":text,
                      "private_entropy_drawn":False,"cohort_generated":False}
        else:
            result = assemble(args.manifest,args.out)
        print(json.dumps(result,indent=2))
        return 0
    except (OSError, Refused, subprocess.SubprocessError) as exc:
        print(json.dumps({"error":str(exc),"scope":"input_preparation_only"}),file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
