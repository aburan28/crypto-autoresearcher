#!/usr/bin/env python3
"""Recompute the visually verified 1997/1998 X9.62 SHA-1 formula change."""

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P97 = Path("/private/tmp/x962-11-17-97.pdf")
P98 = Path("/private/tmp/x962-1998.pdf")
SOURCES = {
    "x962_1997_pdf": (P97, "0c231d5176fcf0b239b44732213d281b518a0e16cc6f13f7bd4039ec99807b6e"),
    "x962_1998_pdf": (P98, "6cb44495bf816008afc11cc6cf65124b484654b2d260559dab6dde55e2609da7"),
    "omitted": (ROOT / "research/nist_seed_skipped_curves_20261016/assessed.json",
                "370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841"),
    "published": (ROOT / "research/nist_seed_skipped_curves_20261016/traits.json",
                  "a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67"),
    "prior_implementation": (ROOT / "research/nist_seed_selection_20261016/generate_candidates.py",
                             "d7883ad23414edf15253fa8634fbad4390c0e9d6b1b3789bf928cca1ce16242c"),
}
SAMPLES97 = {"prime192v1", "prime192v2", "prime192v3", "prime239v1",
             "prime239v2", "prime239v3", "prime256v1"}
MASK160 = (1 << 160) - 1


def sha1_int(x: int) -> int:
    return int.from_bytes(hashlib.sha1(x.to_bytes(20, "big")).digest(), "big")


def x962_r(seed: int, p: int, date: str) -> int:
    t = p.bit_length() if date == "1997-11" else p.bit_length() - 1
    s = (t - 1) // 160
    h = t - 160 * s
    assert h >= 1
    w0 = sha1_int(seed) & ((1 << h) - 1)
    w0 &= (1 << (h - 1)) - 1
    value = w0
    for i in range(1, s + 1):
        value = (value << 160) | sha1_int((seed + i) & MASK160)
    return value


def load_old(path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("prior_nist_candidate_generator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.prime_c


def main() -> None:
    for name, (path, digest) in SOURCES.items():
        assert path.exists(), name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
    omitted = json.loads(SOURCES["omitted"][0].read_text())["candidate_rows"]
    published = json.loads(SOURCES["published"][0].read_text())["published_controls"]
    old_prime_c = load_old(SOURCES["prior_implementation"][0])
    assert len(omitted) == 11 and len(published) == 10
    rows = []
    for label, names_and_records in (
        ("omitted", [(f"omitted-{r['seed_ordinal_one_based']}", r) for r in omitted]),
        ("published", list(published.items())),
    ):
        for name, record in names_and_records:
            uid = record["identity"]["curve_uid"]
            p = int(record["p_hex"], 16)
            b = int(record["b_hex"], 16)
            c = int(record["ansi_c_hex"], 16)
            seed = int(record["seed_hex"], 16)
            r97 = x962_r(seed, p, "1997-11")
            r98 = x962_r(seed, p, "1998-09")
            changed = x962_r(seed ^ 1, p, "1997-11")
            assert r97 == c, name
            assert changed != r97, name
            assert (r97 * b * b + 27) % p == 0, name
            assert old_prime_c(seed, p, "nist_fips_186_2") == r97, name
            assert old_prime_c(seed, p, "ansi_x9_62_1998") == r98, name
            # For these six field sizes, both dated formulas hash the same
            # number of full 160-bit blocks. The later text drops one more bit.
            dropped_bit = 1 << (p.bit_length() - 2)
            assert r98 == (r97 & ~dropped_bit), name
            rows.append({
                "name": name, "label": label, "curve_uid": uid,
                "seed_ordinal_one_based": record["seed_ordinal_one_based"],
                "p_bits": p.bit_length(), "seed_hex": record["seed_hex"],
                "in_1997_draft_sample_table": name in SAMPLES97,
                "r1997_hex": hex(r97), "r1998_hex": hex(r98),
                "archived_c_hex": hex(c), "r1997_matches_archived_c": r97 == c,
                "r1998_matches_archived_c": r98 == c,
                "r1997_matches_curve_equation": (r97 * b * b + 27) % p == 0,
                "r1998_matches_curve_equation": (r98 * b * b + 27) % p == 0,
                "old_fips_equals_r1997": True, "old_strict_equals_r1998": True,
                "altered_seed_changes_r1997": changed != r97,
            })
    assert len(rows) == 21 and len({r["curve_uid"] for r in rows}) == 21
    sample = [r for r in rows if r["in_1997_draft_sample_table"]]
    assert len(sample) == 7 and all(r["label"] == "published" for r in sample)
    summary = {
        "all_rows": len(rows), "published": 10, "omitted": 11,
        "1997_sample_rows": len(sample),
        "published_r1997_matches": sum(r["label"] == "published" and r["r1997_matches_archived_c"] for r in rows),
        "omitted_r1997_matches": sum(r["label"] == "omitted" and r["r1997_matches_archived_c"] for r in rows),
        "1997_sample_r1998_matches": sum(r["in_1997_draft_sample_table"] and r["r1998_matches_archived_c"] for r in rows),
        "published_r1998_matches": sum(r["label"] == "published" and r["r1998_matches_archived_c"] for r in rows),
        "omitted_r1998_matches": sum(r["label"] == "omitted" and r["r1998_matches_archived_c"] for r in rows),
        "all_r1997_positive_controls": sum(r["r1997_matches_curve_equation"] for r in rows),
        "all_altered_seed_controls": sum(r["altered_seed_changes_r1997"] for r in rows),
    }
    output = {"protocol_sha256": hashlib.sha256((HERE / "PROTOCOL.md").read_bytes()).hexdigest(),
              "source_sha256": {name: digest for name, (_, digest) in SOURCES.items()},
              "source_pages_pdf_one_based": {"x962_1997_prime_generation": 65,
                                             "x962_1998_prime_generation": 41},
              "summary": summary, "rows": rows}
    text = json.dumps(output, indent=2, sort_keys=True) + "\n"
    target = HERE / "analysis.json"
    if target.exists():
        assert target.read_text() == text, "immutable analysis replay mismatch"
    else:
        target.write_text(text)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
