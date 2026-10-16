#!/usr/bin/env python3
"""Reproducible, bounded extension of the six recovered seed streams."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MASK48 = (1 << 48) - 1
MULT48 = 0x5DEECE66D
MASK160 = (1 << 160) - 1


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ansi_c(seed: bytes, bits: int) -> int:
    x = int.from_bytes(seed, "big")
    v = (bits - 1) // 160
    w = bits - 160 * v - 1
    hashes = [int.from_bytes(hashlib.sha1(((x + i) & MASK160).to_bytes(20, "big")).digest(), "big") for i in range(v + 1)]
    c = hashes[0] & ((1 << w) - 1)
    for h in hashes[1:]:
        c = (c << 160) | h
    return c


def blocks(timestamp: int, last: int):
    state = ((timestamp & 0xffffffff) << 16) | 0x330e
    for ordinal in range(1, last + 1):
        seed = bytearray()
        for _ in range(20):
            state = (MULT48 * state + 0xb) & MASK48
            seed.append(state >> 40)
        yield ordinal, bytes(seed)


def prepare(out: Path, protocol: dict, traits: dict) -> dict:
    out.mkdir(parents=True, exist_ok=False)
    rows = []
    controls = []
    for stream in protocol["streams"]:
        t = stream["timestamp"]
        published = traits["published_controls"][stream["field_control"]]
        p = int(published["p_hex"], 16)
        assert t == published["timestamp"]
        assert stream["control_ordinal"] == published["seed_ordinal_one_based"]
        assert stream["first_new_ordinal"] == stream["control_ordinal"] + 1
        assert stream["last_new_ordinal"] - stream["first_new_ordinal"] + 1 == 1024
        candidate_lines = []
        metadata = []
        valid_control = False
        for ordinal, seed in blocks(t, stream["last_new_ordinal"]):
            if ordinal == stream["control_ordinal"]:
                c = ansi_c(seed, p.bit_length())
                b = int(published["b_hex"], 16)
                assert seed.hex() == published["seed_hex"].removeprefix("0x")
                assert (c * b * b + 27) % p == 0
                valid_control = True
                controls.append({"timestamp": t, "ordinal": ordinal, "name": stream["field_control"], "seed": seed.hex(), "ok": True})
            if ordinal < stream["first_new_ordinal"]:
                continue
            c = ansi_c(seed, p.bit_length())
            row = {"timestamp": t, "ordinal": ordinal, "seed": seed.hex(), "c": hex(c)}
            if c == 0 or (4 * c + 27) % p == 0:
                row["precheck"] = "forbidden_coefficient"
            else:
                b2 = (-27 * pow(c, -1, p)) % p
                if pow(b2, (p - 1) // 2, p) != 1:
                    row["precheck"] = "no_square_root"
                else:
                    b0 = pow(b2, (p + 1) // 4, p) if p % 4 == 3 else 0
                    row.update(precheck="point_count_candidate", b2=hex(b2), b0=hex(b0))
                    candidate_lines.append(f"{ordinal} {int.from_bytes(seed, 'big')} {c} {b2} {b0}\n")
            metadata.append(row)
        assert valid_control and len(metadata) == 1024
        prefix = str(t)
        (out / f"candidates_{prefix}.txt").write_text("".join(candidate_lines))
        (out / f"metadata_{prefix}.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in metadata))
        rows.append({"timestamp": t, "field": stream["field_control"], "p": hex(p), "first": stream["first_new_ordinal"], "last": stream["last_new_ordinal"], "total_blocks": 1024, "point_count_candidates": len(candidate_lines), "candidate_sha256": digest(out / f"candidates_{prefix}.txt"), "metadata_sha256": digest(out / f"metadata_{prefix}.jsonl")})
    gp_version = subprocess.run(["gp", "--version"], capture_output=True, text=True, check=True).stdout.strip()
    seadata_path = Path("/opt/homebrew/share/pari/seadata")
    manifest = {"protocol_sha256": digest(HERE / "protocol.json"), "scanner_sha256": digest(Path(__file__)), "traits_sha256": digest(ROOT / protocol["source"]), "sea_census_sha256": digest(ROOT / protocol["point_counter"]), "python": sys.version, "gp_version": gp_version, "seadata_path": str(seadata_path.resolve()) if seadata_path.exists() else None, "platform": platform.platform(), "generated_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "controls": controls, "streams": rows}
    (out / "prepare_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def count(out: Path, protocol: dict, manifest: dict) -> None:
    gp_source = ROOT / protocol["point_counter"]
    for row in manifest["streams"]:
        t = row["timestamp"]
        p = int(row["p"], 16)
        source = out / f"candidates_{t}.txt"
        assert digest(source) == row["candidate_sha256"]
        if row["point_count_candidates"] == 0:
            (out / f"orders_{t}.txt").write_text("")
            continue
        driver = out / f"driver_{t}.gp"
        driver.write_text(f'P={p}; CAND="{source}";\n' + gp_source.read_text())
        start = time.monotonic()
        with (out / f"orders_{t}.txt").open("w") as stdout, (out / f"gp_{t}.stderr").open("w") as stderr:
            proc = subprocess.run(["gp", "-q", "-f", str(driver)], stdout=stdout, stderr=stderr, check=False)
        receipt = {"timestamp": t, "command": ["gp", "-q", "-f", str(driver)], "exit_code": proc.returncode, "wall_seconds": time.monotonic() - start, "orders_sha256": digest(out / f"orders_{t}.txt"), "stderr_sha256": digest(out / f"gp_{t}.stderr"), "driver_sha256": digest(driver)}
        receipt["output_rows"] = len((out / f"orders_{t}.txt").read_text().splitlines())
        receipt["valid_output_count"] = receipt["output_rows"] == row["point_count_candidates"]
        (out / f"count_receipt_{t}.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt), flush=True)
        if proc.returncode != 0 or not receipt["valid_output_count"]:
            raise RuntimeError(f"GP failed or returned incomplete output for {t}; retained stderr and partial output")


def summarize(out: Path, protocol: dict, manifest: dict) -> dict:
    result = {"protocol_sha256": manifest["protocol_sha256"], "streams": []}
    classifier = ROOT / "research/nist_seed_provenance_20261016/classify.gp"
    for row in manifest["streams"]:
        t = row["timestamp"]
        p = int(row["p"], 16)
        meta = {r["ordinal"]: r for r in (json.loads(s) for s in (out / f"metadata_{t}.jsonl").read_text().splitlines())}
        orders = {}
        for line in (out / f"orders_{t}.txt").read_text().splitlines():
            i, n, nt = map(int, line.split())
            assert i not in orders and i in meta and meta[i]["precheck"] == "point_count_candidate"
            orders[i] = (n, nt)
        assert len(orders) == row["point_count_candidates"]
        driver = out / f"classify_driver_{t}.gp"
        driver.write_text(f'P={p}; ORDERS="{out / f"orders_{t}.txt"}"; RUN="srand48({t})";\n' + classifier.read_text())
        classified = subprocess.run(["gp", "-q", "-f", str(driver)], capture_output=True, text=True, check=True)
        (out / f"classification_{t}.txt").write_text(classified.stdout)
        (out / f"classification_{t}.stderr").write_text(classified.stderr)
        line = next(s[5:] for s in classified.stdout.splitlines() if s.startswith("JSON "))
        classes = json.loads(line)
        assert classes["candidates"] == len(orders)
        accepted_ordinals = set(classes["accepted"])
        early_abort = 0
        for i, (n, nt) in sorted(orders.items()):
            if n == 0:
                early_abort += 1
                continue
            assert nt == 2 * p + 2 - n
            candidate = meta[i]
            candidate.update(n=hex(n), twist_n=hex(nt), trace=p + 1 - n)
            if i in accepted_ordinals:
                b = int(candidate["b0"], 16)
                if b == 0:
                    b = int(subprocess.check_output(["gp", "-q", "-f"], input=f'print(lift(sqrt(Mod({int(candidate["b2"], 16)},{p}))))\nquit;\n'.encode()).strip())
                candidate["b"] = hex(b)
                candidate["j"] = hex((1728 * 4 * (-3) ** 3 * pow((4 * (-3) ** 3 + 27 * b * b) % p, -1, p)) % p)
                candidate["twist_small_factor_le_10000"] = next((q for q in range(2, 10001) if nt % q == 0), None)
        output = {"timestamp": t, "field": row["field"], "p": row["p"], "total_blocks": 1024, "point_count_candidates": len(orders), "early_abort": early_abort, "accepted": [meta[i] for i in sorted(accepted_ordinals)], "accepted_ordinals": sorted(accepted_ordinals), "n_longer_than_p": classes["n_longer_than_p"], "only_twist_prime": classes["only_twist_prime"], "classification_sha256": digest(out / f"classification_{t}.txt")}
        result["streams"].append(output)
    (out / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["prepare", "count", "summarize"])
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    protocol = json.loads((HERE / "protocol.json").read_text())
    if args.stage == "prepare":
        traits = json.loads((ROOT / protocol["source"]).read_text())
        print(json.dumps(prepare(args.out, protocol, traits), indent=2))
    else:
        manifest = json.loads((args.out / "prepare_manifest.json").read_text())
        assert manifest["protocol_sha256"] == digest(HERE / "protocol.json")
        assert manifest["scanner_sha256"] == digest(Path(__file__))
        if args.stage == "count":
            count(args.out, protocol, manifest)
        else:
            print(json.dumps(summarize(args.out, protocol, manifest), indent=2))


if __name__ == "__main__":
    main()
