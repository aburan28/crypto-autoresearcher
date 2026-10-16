#!/usr/bin/env python3
"""Freeze article run coordinates against independently shipped OpenSSL parameters."""

import hashlib
import json
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ARTICLE = Path(
    "/Volumes/SSD990/.codex/attachments/16b85e2b-3750-4f47-bd74-eff47ef2a250/Pasted text.txt"
)

# The article's published run coordinates, transcribed without arithmetic.
# Each tuple is name, OpenSSL name, UTC time, one-based candidate index, seed.
PRIME = [
    ("prime239v1", "prime239v1", "1997-05-15 15:49:03", 2185, "E43BB460F0B80CC0C0B075798E948060F8321B7D"),
    ("prime239v2", "prime239v2", "1997-05-15 15:49:03", 2320, "E8B4011604095303CA3B8099982BE09FCB9AE616"),
    ("prime239v3", "prime239v3", "1997-05-15 15:49:03", 3048, "7D7374168FFE3471B60A857686A19475D3BFA2FF"),
    ("P-192", "prime192v1", "1997-05-18 14:45:34", 139, "3045AE6FC8422F64ED579528D38120EAE12196D5"),
    ("prime192v3", "prime192v3", "1997-05-18 14:45:34", 5228, "C469684435DEB378C4B65CA9591E2A5763059A2E"),
    ("prime192v2", "prime192v2", "1997-05-18 14:45:34", 6013, "31A92EE2029FD10D901B113E990710F0D21AC6B6"),
    ("P-521", "secp521r1", "1997-08-08 01:12:04", 1136, "D09E8800291CB85396CC6717393284AAA0DA64BA"),
    ("P-256", "prime256v1", "1997-08-16 01:52:34", 1842, "C49D360886E704936A6678E1139D26B7819F7E90"),
    ("P-384", "secp384r1", "1997-08-30 14:50:08", 2688, "A335926AA319A27A1D00896A6773A4827ACDAC73"),
    ("P-224", "secp224r1", "1998-04-03 12:52:07", 7026, "BD71344799D5C7FCDC45B59FA3B9AB8F6A948BC5"),
]
BINARY = [
    ("B-233", "sect233r1", "1998-04-17 15:24:18", 155, "74D59FF07F6B413D0EA14B344B20A2DB049B50C3"),
    ("B-283", "sect283r1", "1998-04-17 15:27:44", 32, "77E2B07370EB0F832A6DD5B62DFC88CD06BB84BE"),
    ("B-409", "sect409r1", "1998-04-17 15:30:18", 60, "4099B5A457F9D69F79213D094C4BCD4D4262210B"),
    ("B-571", "sect571r1", "1998-04-17 15:32:08", 73, "2AA058F73A0E33AB486B0F610410C53A7F132310"),
]


def sections(raw: str) -> dict[str, str]:
    keys = ("Prime", "Polynomial", "A", "B", "Generator (uncompressed)", "Order", "Cofactor", "Seed")
    result = {}
    current = None
    for line in raw.splitlines():
        match = re.match(r"^([^:]+):\s*(.*)$", line)
        if match and match.group(1) in keys:
            current = match.group(1)
            result[current] = match.group(2) + "\n"
        elif current is not None:
            result[current] += line + "\n"
    return result


def hex_section(section: str) -> int:
    groups = re.findall(r"(?:[0-9a-fA-F]{2}:)+[0-9a-fA-F]{2}|\b[0-9a-fA-F]{2}\b", section)
    if groups:
        return int("".join(group.replace(":", "") for group in groups), 16)
    match = re.search(r"0x([0-9a-fA-F]+)", section)
    if match:
        return int(match.group(1), 16)
    raise ValueError(f"no hexadecimal parameter in {section!r}")


def build_record(kind: str, row: tuple) -> dict:
    name, openssl_name, when, index, expected_seed = row
    raw = subprocess.check_output(
        ["openssl", "ecparam", "-name", openssl_name, "-param_enc", "explicit", "-text", "-noout"],
        text=True,
        stderr=subprocess.STDOUT,
    )
    part = sections(raw)
    seed = f"{hex_section(part['Seed']):040X}"
    if seed != expected_seed:
        raise ValueError(f"{name}: article seed {expected_seed} != OpenSSL {seed}")
    q_param = hex_section(part["Prime" if kind == "prime" else "Polynomial"])
    cofactor = int(re.search(r"Cofactor:\s+(\d+)", raw).group(1))
    timestamp = int(datetime.fromisoformat(when).replace(tzinfo=timezone.utc).timestamp())
    result = {
        "name": name,
        "openssl_name": openssl_name,
        "kind": kind,
        "utc_time": when,
        "unix_time": timestamp,
        "candidate_index": index,
        "published_seed": seed,
        "published_a": hex_section(part["A"]),
        "published_b": str(hex_section(part["B"])),
        "published_subgroup_order": str(hex_section(part["Order"])),
        "published_cofactor": cofactor,
    }
    if kind == "prime":
        result["p"] = str(q_param)
        if result["published_a"] != q_param - 3 or cofactor != 1:
            raise ValueError(f"{name}: unexpected prime family parameters")
    else:
        result["m"] = q_param.bit_length() - 1
        result["polynomial"] = hex(q_param)
        if result["published_a"] != 1 or cofactor != 2:
            raise ValueError(f"{name}: unexpected binary family parameters")
    return result


def main() -> None:
    records = [build_record("prime", row) for row in PRIME]
    records += [build_record("binary", row) for row in BINARY]
    if sum(record["candidate_index"] for record in records) != 31945:
        raise ValueError("candidate cardinality changed")
    source = {
        "article_path_at_intake": str(ARTICLE),
        "article_sha256": hashlib.sha256(ARTICLE.read_bytes()).hexdigest(),
        "source_types": {"article": "user supplied", "parameters": "OpenSSL named curves"},
        "openssl_version": subprocess.check_output(["openssl", "version"], text=True).strip(),
        "python_version": platform.python_version(),
        "target_count": len(records),
        "candidate_pairs_including_anchors": sum(record["candidate_index"] for record in records),
    }
    (ROOT / "targets.json").write_text(json.dumps(records, indent=2) + "\n")
    (ROOT / "SOURCE.json").write_text(json.dumps(source, indent=2) + "\n")
    print(json.dumps(source, sort_keys=True))


if __name__ == "__main__":
    main()
