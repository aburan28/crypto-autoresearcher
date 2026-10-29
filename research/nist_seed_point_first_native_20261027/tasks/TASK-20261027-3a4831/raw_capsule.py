"""Bounded deterministic lossless capsule. No extraction or execution."""
import base64
import gzip
import hashlib
import io
import json
import os
import stat
from pathlib import PurePosixPath

MAX_BYTES = 8 * 1024 * 1024
MAX_MEMBERS = 32
RAW_MEMBERS = frozenset((
    "started.json", "workload.json", "fixed-x.json", "fixed-x-aa.json",
    "positive.json", "negative.json", "rows.jsonl", "summary.json",
    "stdout.txt", "stderr.txt",
))
ALLOWED = RAW_MEMBERS | {"failure.json"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    def constant(value):
        raise ValueError("nonfinite JSON")

    require(len(data) <= MAX_BYTES, "JSON size bound")
    return json.loads(
        data, object_pairs_hook=pairs, parse_constant=constant
    )


def safe_name(name):
    require(
        isinstance(name, str) and name
        and "\\" not in name and "\x00" not in name,
        "unsafe member name",
    )
    path = PurePosixPath(name)
    require(
        not path.is_absolute()
        and name == path.as_posix()
        and all(part not in (".", "..", "") for part in name.split("/")),
        "unsafe member name",
    )
    require("/" not in name, "unexpected nested raw member")
    return name


def encode(members, errors=()):
    body = canonical({
        "schema": "nist.fixed-x.capsule/v2",
        "members": members,
        "capture_errors": list(errors),
    })
    require(len(body) <= MAX_BYTES, "capsule uncompressed size bound")
    result = bytearray(gzip.compress(body, compresslevel=9, mtime=0))
    result[9] = 255
    return bytes(result)


def pack(directory):
    """Capture regular bytes; retain unsafe-type metadata without following it."""
    members, errors = [], []
    if not directory.exists():
        errors.append({"kind": "missing_child_directory"})
    else:
        require(not directory.is_symlink(), "aliased child directory")
        paths = sorted(directory.rglob("*"))
        require(len(paths) <= MAX_MEMBERS, "raw member count bound")
        for path in paths:
            name = path.relative_to(directory).as_posix()
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                members.append({
                    "name": name,
                    "type": "symlink",
                    "link": os.readlink(path),
                })
                errors.append({"kind": "symlink", "name": name})
            elif stat.S_ISREG(mode):
                require(
                    path.stat().st_size <= MAX_BYTES,
                    "raw byte size bound",
                )
                fd = os.open(
                    path,
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                )
                with os.fdopen(fd, "rb") as stream:
                    data = stream.read(MAX_BYTES + 1)
                require(len(data) <= MAX_BYTES, "raw byte size bound")
                members.append({
                    "name": name,
                    "type": "regular",
                    "length": len(data),
                    "sha256": sha(data),
                    "base64": base64.b64encode(data).decode(),
                })
            else:
                members.append({
                    "name": name,
                    "type": "nonregular",
                    "mode": mode,
                })
                errors.append({"kind": "nonregular", "name": name})
    return encode(members, errors)


def unpack(data, complete=True):
    require(
        type(data) is bytes and len(data) <= MAX_BYTES,
        "capsule compressed size bound",
    )
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
            plain = stream.read(MAX_BYTES + 1)
            require(
                len(plain) <= MAX_BYTES,
                "capsule decompression bound",
            )
            require(
                stream.read(1) == b"",
                "capsule trailing decompressed bytes",
            )
    except (OSError, EOFError) as exc:
        raise ValueError("capsule gzip corruption") from exc
    obj = strict_json(plain)
    require(
        set(obj) == {"schema", "members", "capture_errors"}
        and obj["schema"] == "nist.fixed-x.capsule/v2",
        "capsule schema",
    )
    require(
        isinstance(obj["members"], list)
        and len(obj["members"]) <= MAX_MEMBERS,
        "capsule member count",
    )
    result = {}
    for member in obj["members"]:
        name = safe_name(member["name"])
        require(
            name in ALLOWED and name not in result,
            "unexpected or duplicate raw member",
        )
        require(
            set(member) == {
                "name", "type", "length", "sha256", "base64",
            }
            and member["type"] == "regular",
            "nonregular raw member",
        )
        value = base64.b64decode(member["base64"], validate=True)
        require(
            type(member["length"]) is int
            and len(value) == member["length"]
            and sha(value) == member["sha256"],
            "raw member length/digest",
        )
        result[name] = value
    require(
        isinstance(obj["capture_errors"], list)
        and not obj["capture_errors"],
        "raw capture incomplete",
    )
    if complete:
        require(set(result) == RAW_MEMBERS, "incomplete raw member set")
    return result
