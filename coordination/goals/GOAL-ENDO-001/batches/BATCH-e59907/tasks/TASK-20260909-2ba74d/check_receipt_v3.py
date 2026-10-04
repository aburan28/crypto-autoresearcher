"""Finite presence checks and byte custody only; no receipt authentication."""
import hashlib
import json
from pathlib import Path

RULES = json.loads(Path(__file__).with_name("receipt-rules-v3.json").read_text())
FIELDS = tuple(RULES["normalization"]["fields"])
TRIM = "".join(chr(int(x[2:], 16)) for x in RULES["normalization"]["trim_codepoints"])


def presence(field, value=None, *, present=True):
    if field not in FIELDS:
        raise ValueError("Unknown field")
    if not present or not isinstance(value, str):
        return {"normalized": None, "outcome": "STOP"}
    normalized = value.strip(TRIM)
    if field == "filesystem_id":
        normalized = normalized.lower().rstrip("/")
    elif field == "filesystem_mount":
        normalized = normalized.rstrip("/") or ("/" if normalized.startswith("/") else "")
    return {"normalized": normalized,
            "outcome": "STOP" if not normalized or normalized.lower() == "null" else "PASS"}


def check_presence(binding):
    if not isinstance(binding, dict):
        return {field: presence(field, present=False) for field in FIELDS}
    return {field: presence(field, binding.get(field), present=field in binding) for field in FIELDS}


def custody(blob, expected_sha256):
    actual = hashlib.sha256(blob).hexdigest()
    return {"actual_sha256": actual, "expected_sha256": expected_sha256,
            "accepted": actual == expected_sha256}
