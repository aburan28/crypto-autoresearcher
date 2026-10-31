"""Read and slice only hash-pinned public inputs. No private-seed imports."""
from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re

FIXTURE_COLUMNS = ("fixture_id","stratum","p","a","b","gx","gy","r","N","seed")
TARGET_COLUMNS = ("fixture_id","replicate","target_id","target_ordinal","qx","qy","infinity")
SETTING_COLUMNS = ("cell_id","fixture_id","replicate","dp_bits","initial_chains","endpoint_cap",
                   "max_precomp_ops","max_online_ops","seed")
HEX64 = re.compile(r"[0-9a-f]{64}")


class Refused(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Refused(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_read(path: Path) -> dict:
    def unique(items):
        out = {}
        for k,v in items:
            require(k not in out, f"duplicate JSON key in {path}")
            out[k] = v
        return out
    value = json.loads(path.read_text(),object_pairs_hook=unique)
    require(isinstance(value,dict),f"not JSON metadata: {path}")
    return value


def public_path(root: Path, relative: str) -> Path:
    require(isinstance(relative,str) and relative, "missing public relative path")
    p = PurePosixPath(relative)
    require(not p.is_absolute() and ".." not in p.parts and str(p) == relative,
            "unsafe public relative path")
    out = root/p
    require(not out.is_symlink() and out.resolve().is_relative_to(root.resolve()),
            "public path escapes root or is a symlink")
    return out


def read_table(path: Path, header: tuple[str,...]) -> list[dict]:
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream,delimiter="\t")
        require(tuple(reader.fieldnames or ()) == header, f"wrong columns: {path}")
        rows = list(reader)
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows),
            f"malformed TSV row: {path}")
    return rows


def table_bytes(header: tuple[str,...], rows: list[dict]) -> bytes:
    text = io.StringIO(newline="")
    writer = csv.DictWriter(text,fieldnames=header,delimiter="\t",lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return text.getvalue().encode()


def _prime(n: int) -> bool:
    return n>1 and all(n%d for d in range(2,math.isqrt(n)+1))


def _add(p: int,a: int,left,right):
    if left is None:
        return right
    if right is None:
        return left
    x,y = left
    u,v = right
    if x == u and (y+v)%p == 0:
        return None
    slope = ((3*x*x+a)*pow(2*y,-1,p) if left == right else (v-y)*pow(u-x,-1,p))%p
    xx = (slope*slope-x-u)%p
    return xx,(slope*(x-xx)-y)%p


def _mul(p: int,a: int,point,n: int):
    result = None
    while n:
        if n&1:
            result = _add(p,a,result,point)
        point = _add(p,a,point,point)
        n >>= 1
    return result


def _seed(protocol: str,nonce: str,fixture: str,replicate: int,purpose: str) -> int:
    payload = b"classical.ecdlp.endpoint-reuse.v1\0"+b"\0".join(
        str(x).encode("ascii") for x in (protocol,nonce,fixture,replicate,purpose))
    return int.from_bytes(hashlib.sha256(payload).digest()[:8],"big")


@dataclass(frozen=True)
class PublicInputs:
    root: Path
    manifest_sha256: str
    protocol_sha256: str
    nonce_hex: str
    fixtures: dict[str,dict]
    settings: dict[str,dict]
    targets: dict[str,list[dict]]


def load_inputs(root: Path, expected_manifest_sha256: str) -> PublicInputs:
    """Verify every declared public byte and every requested execution cell."""
    root = Path(root).resolve()
    require(HEX64.fullmatch(expected_manifest_sha256) is not None, "expected manifest SHA required")
    manifest_path = root/"inputs-manifest.json"
    require(sha(manifest_path.read_bytes()) == expected_manifest_sha256, "public manifest hash mismatch")
    manifest = json_read(manifest_path)
    require(manifest.get("schema") == "classical.ecdlp.endpoint-public-inputs/v1",
            "wrong public manifest schema")
    require((manifest.get("fixture_count"),manifest.get("cell_count"),manifest.get("target_count")) ==
            (64,128,8192), "wrong fixed cohort dimensions")
    declared = set()
    for item in manifest["files"]:
        name = item["path"]
        require(name not in declared and name != "inputs-manifest.json", "duplicate/self public manifest entry")
        declared.add(name)
        path = public_path(root,name)
        raw = path.read_bytes()
        require(len(raw) == item["bytes"] and sha(raw) == item["sha256"], f"public bytes changed: {name}")
        require(len(raw) < 1048576, f"oversized public file: {name}")
        if path.suffix in (".tsv",".jsonl"):
            require(len(raw) <= 61440, f"unpartitioned public data file: {name}")
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    require(actual == declared|{"inputs-manifest.json"}, "public tree has missing or undeclared files")
    fixture_path = public_path(root,manifest["fixture_path"])
    settings_path = public_path(root,manifest["settings_path"])
    target_manifest_path = public_path(root,manifest["targets_manifest_path"])
    require({manifest["fixture_path"],manifest["settings_path"],manifest["targets_manifest_path"],
             "target-custody.json","external-nonce.json","fixture-certificates.json"} <= declared,
            "required public metadata not declared")
    custody,nonce = json_read(root/"target-custody.json"),json_read(root/"external-nonce.json")
    protocol_hash = custody["protocol_sha256"]
    nonce_hex = nonce["nonce_hex"]
    require(HEX64.fullmatch(protocol_hash) is not None and HEX64.fullmatch(nonce_hex) is not None,
            "invalid public seed provenance")
    require(manifest.get("protocol_sha256") == protocol_hash, "public manifest protocol binding differs")
    require(nonce["protocol_sha256"] == protocol_hash and
            sha((root/"external-nonce.json").read_bytes()) == custody["nonce_file_sha256"],
            "public nonce binding differs")
    fixtures = {}
    for row in read_table(fixture_path,FIXTURE_COLUMNS):
        name = row["fixture_id"]
        require(name not in fixtures and re.fullmatch(r"er-r(12|14|16|18)-([0-9]|1[0-5])",name) is not None,
                "wrong/duplicate fixture identity")
        p,a,b,x,y,r,n = (int(row[k]) for k in ("p","a","b","gx","gy","r","N"))
        require(row["stratum"] == "ordinary" and 3<p<=1048575 and 2<r<=524287 and
                _prime(p) and _prime(r), "invalid ordinary prime-field fixture")
        require(0<a<p and 0<b<p and (4*a*a*a+27*b*b)%p and
                n%r == 0 and 1<=n//r<=3 and math.gcd(n//r,r) == 1 and
                n not in (p,p+1) and r != p and (p+1-n)**2<=4*p, "bad curve/order metadata")
        require(0<=x<p and 0<=y<p and (y*y-x*x*x-a*x-b)%p == 0 and
                _mul(p,a,(x,y),r) is None, "invalid generator/order witness")
        require(str(r.bit_length()) == name.split("-")[1][1:], "fixture bit-size identity")
        fixtures[name] = row
    require(len(fixtures) == 64 and
            all(sum(int(f["r"]).bit_length() == b for f in fixtures.values()) == 16
                for b in (12,14,16,18)), "wrong fixture panel")
    require(len({tuple(f[k] for k in ("p","a","b")) for f in fixtures.values()}) == 64,
            "duplicate curve model in public cohort")
    settings = {}
    for row in read_table(settings_path,SETTING_COLUMNS):
        name,fid,rep = row["cell_id"],row["fixture_id"],int(row["replicate"])
        require(fid in fixtures and rep in (0,1) and name == f"{fid}-rep{rep}" and name not in settings,
                "wrong/duplicate settings cell")
        r = int(fixtures[fid]["r"])
        t = r.bit_length()//3
        c0 = (r+(1<<(2*t))//2)//(1<<(2*t))
        cap = 4*c0
        rr = math.isqrt(r)
        expected = (t,c0,cap,256*cap*(1<<t)+8192,256*(rr+(rr*rr<r))+8192,
                    _seed(protocol_hash,nonce_hex,fid,rep,"solver_cell"))
        observed = tuple(int(row[k]) for k in
                         ("dp_bits","initial_chains","endpoint_cap","max_precomp_ops","max_online_ops","seed"))
        require(observed == expected, "settings differ from frozen law")
        settings[name] = row
    require(set(settings) == {f"{fid}-rep{rep}" for fid in fixtures for rep in (0,1)},
            "incomplete settings cells")
    target_manifest = json_read(target_manifest_path)
    require(target_manifest.get("schema") == "classical.ecdlp.endpoint-target-parts/v1" and
            target_manifest.get("columns") == list(TARGET_COLUMNS) and target_manifest.get("rows") == 8192,
            "wrong target-part manifest")
    require(sha(target_manifest_path.read_bytes()) == custody["public_target_manifest_sha256"],
            "target manifest custody mismatch")
    targets = {name:[] for name in settings}
    logical = bytearray(table_bytes(TARGET_COLUMNS,[]))
    part_fixtures,target_ids = set(),set()
    for item in target_manifest["parts"]:
        name,fid = item["path"],item["fixture_id"]
        require(name in declared and fid in fixtures and fid not in part_fixtures, "wrong target part set")
        part_fixtures.add(fid)
        path = public_path(root,name)
        data = path.read_bytes()
        require(sha(data) == item["sha256"] and len(data) == item["bytes"], "target-part bytes changed")
        rows = read_table(path,TARGET_COLUMNS)
        require(len(rows) == item["rows"] == 128, "wrong per-curve target-part length")
        f = fixtures[fid]
        p,a,b,r = (int(f[k]) for k in ("p","a","b","r"))
        for row in rows:
            rep,ordinal = int(row["replicate"]),int(row["target_ordinal"])
            tid = row["target_id"]
            require(row["fixture_id"] == fid and rep in (0,1) and 0<=ordinal<64 and
                    tid == f"{fid}-rep{rep}-t{ordinal:02d}" and tid not in target_ids,
                    "wrong/duplicate target identity")
            target_ids.add(tid)
            x,y,infinity = (int(row[k]) for k in ("qx","qy","infinity"))
            require(infinity in (0,1), "invalid infinity flag")
            if infinity:
                require((x,y) == (0,0), "noncanonical infinity")
                point = None
            else:
                require(0<=x<p and 0<=y<p and (y*y-x*x*x-a*x-b)%p == 0, "target not on curve")
                point = (x,y)
            require(_mul(p,a,point,r) is None, "target not in prime subgroup")
            targets[f"{fid}-rep{rep}"].append(row)
        logical.extend(data.split(b"\n",1)[1])
    require(part_fixtures == set(fixtures) and len(target_ids) == 8192, "incomplete target parts")
    require(len(logical) == target_manifest["logical_bytes"] and
            sha(logical) == target_manifest["logical_sha256"], "merged target hash mismatch")
    for rows in targets.values():
        require([int(r["target_ordinal"]) for r in rows] == list(range(64)),
                "target order must be contiguous and fixed within each cell")
    return PublicInputs(root,expected_manifest_sha256,protocol_hash,nonce_hex,fixtures,settings,targets)


def write_cell(cohort: PublicInputs, cell_id: str, out: Path) -> dict:
    """Create public-only exact one-cell TSVs in a fresh runtime directory."""
    require(cell_id in cohort.settings, "unknown execution cell")
    out = Path(out)
    require(not out.exists(), "cell slice output already exists")
    out.mkdir(parents=True)
    setting = cohort.settings[cell_id]
    fixture = cohort.fixtures[setting["fixture_id"]]
    result = {}
    for name,columns,rows in (("fixtures.tsv",FIXTURE_COLUMNS,[fixture]),
                              ("targets.tsv",TARGET_COLUMNS,cohort.targets[cell_id]),
                              ("settings.tsv",SETTING_COLUMNS,[setting])):
        data = table_bytes(columns,rows)
        fd = os.open(out/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644)
        with os.fdopen(fd,"wb") as stream:
            stream.write(data)
        result[name] = {"path":str(out/name),"bytes":len(data),"sha256":sha(data),"rows":len(rows)}
    return result
