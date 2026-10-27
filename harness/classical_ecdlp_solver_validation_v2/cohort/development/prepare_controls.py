#!/usr/bin/env python3
"""Generate known-label arithmetic controls, excluded from confirmation."""
from pathlib import Path
import importlib.util
import json

BASE = Path(__file__).resolve().parent.parent
DEV = BASE / "development"
spec = importlib.util.spec_from_file_location("cohort_prep", BASE / "prepare.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fixtures = [
    {"id": "dev-old-17", "stratum": "ordinary", "p": 37, "a": 29, "b": 3,
     "Px": 30, "Py": 30, "r": 17, "N": 34, "seed": 1},
    {"id": "dev-old-19", "stratum": "ordinary", "p": 61, "a": 1, "b": 4,
     "Px": 41, "Py": 55, "r": 19, "N": 57, "seed": 2},
    {"id": "dev-old-41", "stratum": "ordinary", "p": 127, "a": 13, "b": 45,
     "Px": 26, "Py": 68, "r": 41, "N": 123, "seed": 3},
    {"id": "dev-large-13121", "stratum": "ordinary", "p": 65537, "a": 1, "b": 7,
     "Px": 13979, "Py": 44364, "r": 13121, "N": 65605, "seed": 4},
]
mod.write_tsv(DEV / "fixtures.tsv", list(fixtures[0]), fixtures)
targets = []
truth = []
for fixture in fixtures:
    p, a, r = (fixture[key] for key in ("p", "a", "r"))
    point = fixture["Px"], fixture["Py"]
    assert mod.mul(p, a, point, r) is None
    for ordinal, k in enumerate([0, 1, r-1, 7]):
        q = mod.mul(p, a, point, k)
        target_id = fixture["id"] + "-edge" + str(ordinal)
        targets.append({"fixture_id": fixture["id"], "target_id": target_id,
                        "Qx": q[0] if q else 0, "Qy": q[1] if q else 0,
                        "Qinf": 0 if q else 1})
        truth.append({"fixture_id": fixture["id"], "target_id": target_id, "k": k,
                      "case": ["identity", "generator", "last_canonical", "ordinary_scalar"][ordinal]})
mod.write_tsv(DEV / "public-targets.tsv", list(targets[0]), targets)
mod.write_tsv(DEV / "known-scalars.tsv", list(truth[0]), truth)
(DEV / "scope.json").write_text(json.dumps({
    "kind": "fixed_development_edge_controls", "scientific_confirmation": False,
    "labels_intentionally_public": True, "fixtures": 4, "targets": 16,
    "cases": ["k0 identity", "k1 generator", "k=r-1", "k7 ordinary"],
    "source": "Three prior fixed toy controls and candidate-fixed larger arithmetic control; all excluded from confirmation.",
    "not_fresh_blinded_targets": True,
}, indent=2) + "\n")
print("Wrote16 forced edge development controls, separately from confirmation.")
