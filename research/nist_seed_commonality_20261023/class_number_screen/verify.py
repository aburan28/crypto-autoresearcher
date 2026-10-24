"""Independent Sage exact-integer check of archived curves and scan hits."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sage.all import Integer, fundamental_discriminant, version

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSESSED = ROOT / "research/nist_seed_skipped_curves_20261016/assessed.json"
TRAITS = ROOT / "research/nist_seed_skipped_curves_20261016/traits.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    target = HERE / "sage_verification.json"
    if target.exists():
        raise SystemExit("refusing to overwrite Sage verification")
    inputs = json.loads((HERE / "inputs.json").read_text())
    analysis = json.loads((HERE / "analysis.json").read_text())
    assert digest(ASSESSED) == inputs["assessed_sha256"]
    assert digest(TRAITS) == inputs["traits_sha256"]
    source = json.loads(ASSESSED.read_text())
    controls = json.loads(TRAITS.read_text())["published_controls"]
    lookup = {f"skip-{r['timestamp']}-{r['seed_ordinal_one_based']}": r
              for r in source["candidate_rows"]}
    lookup.update(controls)
    assert len(lookup) == 21
    for row in analysis["curves"]:
        original = lookup[row["label"]]
        assert row["curve_uid"] == original["identity"]["curve_uid"]
        p, n = Integer(original["p_hex"]), Integer(original["n_hex"])
        delta = (p + 1 - n) ** 2 - 4 * p
        assert delta < 0 and delta == Integer(row["delta_hex_signed"])
        assert delta == Integer(original["delta_pi_hex_signed"])
        assert int((-delta).nbits()) == row["delta_bits"]
    for hit in analysis["hit_rows"]:
        label = hit["label"]
        if label.startswith("control_"):
            values = {"control_d3": -3 * 17**2,
                      "control_d4": -4 * 19**2}
            delta = Integer(values[label])
        else:
            delta = Integer(next(r["delta_hex_signed"] for r in analysis["curves"]
                                 if r["label"] == label))
        d, conductor = Integer(hit["D"]), Integer(hit["conductor"])
        assert fundamental_discriminant(-d) == -d
        assert delta == -d * conductor**2
    assert analysis["synthetic_controls"] == {"control_d3": 1,
                                                "control_d4": 1,
                                                "control_nohit": 0}
    result = {"status": "PASS", "sage_version": version(),
              "analysis_sha256": digest(HERE / "analysis.json"),
              "source_assessed_sha256": digest(ASSESSED),
              "source_traits_sha256": digest(TRAITS),
              "curves_recomputed": 21, "hits_checked": len(analysis["hit_rows"]),
              "scope": "source deltas, exact hit equations, and synthetic controls; external list completeness not reproduced"}
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
