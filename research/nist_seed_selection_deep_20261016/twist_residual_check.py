"""Check primality of each source audit's post-trial-division twist residual.

This does not factor a composite residual. PARI/GP isprime is run once on each
of the 21 original field curves; P-224 alternate-sign duplicates are excluded.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "nist_seed_skipped_curves_20261016"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    traits_path = SOURCE / "traits.json"
    assessed_path = SOURCE / "assessed.json"
    traits = json.loads(traits_path.read_text())
    assessed = json.loads(assessed_path.read_text())
    rows = [(name, row, "published") for name, row in traits["published_controls"].items()]
    rows += [(f"{row['timestamp']}:{row['seed_ordinal_one_based']}", row, "passed_over")
             for row in assessed["candidate_rows"]]
    assert len(rows) == 21
    commands = [f"isprime({int(row['twist_unfactored_rest_hex'], 16)})"
                for _, row, _ in rows]
    process = subprocess.run(["gp", "-q"], input="\n".join(commands) + "\n",
                             text=True, capture_output=True, timeout=120, check=True)
    lines = process.stdout.splitlines()
    if len(lines) != len(rows) or any(line not in ("0", "1") for line in lines):
        raise RuntimeError(f"unexpected GP output: {process.stdout[:1000]!r} {process.stderr[:1000]!r}")
    version = subprocess.run(["gp", "--version"], text=True,
                             capture_output=True, check=True).stdout.strip()
    output = {
        "command": "gp -q, one isprime(post-10000-trial-division twist residual) per row",
        "gp_version": version,
        "source_sha256": {"traits.json": digest(traits_path),
                          "assessed.json": digest(assessed_path)},
        "rows": [
            {"name": name, "label": label,
             "field_bits": int(row["p_hex"], 16).bit_length(),
             "residual_bits": int(row["twist_unfactored_rest_hex"], 16).bit_length(),
             "residual_is_prime": line == "1",
             "small_twist_factors_to_10000": row["twist_small_factors_to_10000"]}
            for (name, row, label), line in zip(rows, lines, strict=True)
        ],
    }
    (HERE / "twist_residual_primality.json").write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n")
    for r in output["rows"]:
        print(f"{r['name']:20s} {r['label']:11s} {r['residual_bits']:3} bits "
              f"prime={r['residual_is_prime']}")


if __name__ == "__main__":
    main()
