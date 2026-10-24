"""Freeze exact row identities and compare them to the external class list."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ASSESSED = ROOT / "research/nist_seed_skipped_curves_20261016/assessed.json"
TRAITS = ROOT / "research/nist_seed_skipped_curves_20261016/traits.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    assessed = json.loads(ASSESSED.read_text())
    traits = json.loads(TRAITS.read_text())
    rows = []
    for row in assessed["candidate_rows"]:
        label = f"skip-{row['timestamp']}-{row['seed_ordinal_one_based']}"
        rows.append((label, "omitted", row))
    for label, row in traits["published_controls"].items():
        rows.append((label, "published", row))
    assert len(rows) == 21
    assert len({r[2]["identity"]["curve_uid"] for r in rows}) == 21
    out = []
    for label, group, row in rows:
        p, n = int(row["p_hex"], 16), int(row["n_hex"], 16)
        t = p + 1 - n
        delta = t * t - 4 * p
        assert delta < 0 and t != 0
        assert int(row["delta_pi_hex_signed"], 16) == delta
        out.append({"label": label, "group": group, "curve_uid": row["identity"]["curve_uid"],
                    "timestamp": row["timestamp"], "seed_ordinal": row["seed_ordinal_one_based"],
                    "p_hex": hex(p), "n_hex": hex(n), "trace_hex_signed": hex(t),
                    "delta_hex_signed": hex(delta), "delta_bits": (-delta).bit_length()})
    (HERE / "curves.tsv").write_text("".join(f"{r['label']}\t{(-int(r['delta_hex_signed'],16)):x}\n" for r in out)
                                    + "control_d3\t" + format(3 * 17**2, "x") + "\n"
                                    + "control_d4\t" + format(4 * 19**2, "x") + "\n"
                                    + "control_nohit\t5\n")
    (HERE / "inputs.json").write_text(json.dumps({
        "assessed_sha256": digest(ASSESSED), "traits_sha256": digest(TRAITS),
        "curves_tsv_sha256": digest(HERE / "curves.tsv"), "rows": out,
        "python": sys.version, "platform": platform.platform(),
        "gmp_version": subprocess.check_output(["pkg-config", "--modversion", "gmp"], text=True).strip(),
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
