"""Mechanical replay of saved-data arithmetic; not independent scientific review."""
from collections import Counter, defaultdict
from itertools import product
from math import isclose, isqrt
from pathlib import Path
from statistics import fmean
import argparse
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]


def verify(data):
    read = lambda name: json.loads((data / name).read_text())
    summary = read("summary.json")
    for binding in summary["sources"]:
        assert hashlib.sha256((ROOT / binding["path"]).read_bytes()).hexdigest() == binding["sha256"]
    assert hashlib.sha256((Path(__file__).parent / "analyze.py").read_bytes()).hexdigest() == summary["analysis_sha256"]
    raw = json.loads((ROOT / summary["sources"][0]["path"]).read_text())["cells"]
    catalog = read("cubic-catalog.json")
    for entry in catalog:
        g = entry["g"]
        assert len(g) == 4 and g[-1] == 1 and sum(c != 0 for c in g) == 3
        assert entry["irreducible_by_rational_root_test"] == all(sum(c*r**i for i,c in enumerate(g)) != 0 for r in (-1, 1))
        for row in entry["evaluations"]:
            p = sum(c*(1 << row["k"])**i for i,c in enumerate(g))
            assert p == row["value"]
            divisor = next((q for q in range(2, isqrt(p)+1) if p % q == 0), None)
            assert row["prime"] == (p >= 2 and divisor is None)
            assert row["smallest_prime_factor"] == divisor
            assert row["meets_minimum"] == (p >= 4096)
        eligible = [r for r in entry["evaluations"] if r["prime"] and r["meets_minimum"]]
        assert entry["first_eligible"] == (eligible[0] if eligible else None)
    assert len({tuple(r["g"]) for r in catalog}) == 8
    for row in read("sampler-support.json"):
        # Independent ternary enumeration instead of positions/sign subsets.
        count = sum(1 for interior in product((-1, 0, 1), repeat=row["d"]-1)
                    if sum(v != 0 for v in interior) == row["weight"]-2) * 2
        assert count == row["coefficient_patterns"] == row["enumerated_patterns"]
        actual = {tuple(c["field"]["g"]) for c in raw if c["field"]["shape"] == row["shape"] and c["field"]["kind"] == "random_g"}
        assert len(actual) == row["observed_distinct_g"]
        if row["d"] == 3:
            assert actual == {tuple(c["g"]) for c in catalog if c["first_eligible"]}
    for row in read("draw-multiplicities.json"):
        indices = [i for i, c in enumerate(raw) if c["curve_index"] == 0 and
                   c["field"]["kind"] == "random_g" and c["field"]["shape"] == row["shape"] and c["seed"] == row["seed"]]
        counts = Counter(tuple(raw[i]["field"]["g"]) for i in indices)
        assert counts == {tuple(r["g"]): r["draws"] for r in row["g_counts"]}
        assert sum(counts.values()) == row["accepted_draws"] == 20
        assert len(counts) == row["distinct_g"]
    for group in read("within-input-groups.json"):
        rows = [raw[i] for i in group["representative_raw_rows"]]
        for c in rows:
            assert (c["field"]["g"],c["field"]["p"],c["root_mod_p"],c["curve"]["A"],c["curve"]["B"]) == (group["g"],group["p"],group["root"],group["A"],group["B"])
        assert sorted(c["seed"] for c in rows) == group["seeds"]
        assert len({json.dumps(c["rungs"],sort_keys=True) for c in rows}) == group["distinct_rung_profiles"]
        assert len({json.dumps(c["sample_points"],sort_keys=True) for c in rows}) == group["distinct_saved_sample_lists"]
    trajectories = list(csv.DictReader((data / "within-input-trajectories.csv").open()))
    for row in trajectories:
        cell = raw[int(row["raw_row"])]
        assert cell["seed"] == int(row["seed"])
        rung = next(r for r in cell["rungs"] if r["work"] == int(row["work"]))
        assert all(int(row[k]) == v for k,v in rung.items())
    def avg(xs):
        present = [v for v in xs if v is not None]
        return fmean(present) if present else None
    for row in read("weighting-views.json"):
        rows = [c for c in raw if c["field"]["shape"] == row["shape"] and c["field"]["kind"] == "random_g"]
        value = lambda c: c["gamma"] if row["metric"] == "gamma" else c["rungs"][-1]["distinct_residues"]
        seed_groups, input_groups = defaultdict(list), defaultdict(list)
        for c in rows:
            k = (tuple(c["field"]["g"]), c["field"]["p"], c["root_mod_p"], c["curve"]["A"], c["curve"]["B"])
            seed_groups[(k,c["seed"])].append(value(c))
        for (k,seed), values in seed_groups.items():
            input_groups[k].append(avg(values))
        views = ([value(c) for c in rows], [avg(v) for v in seed_groups.values()],
                 [avg(v) for v in input_groups.values()])
        for values, field, count_field in zip(views,
                ("row_weighted_mean", "seed_input_grouped_mean", "input_grouped_mean"),
                ("row_values_present", "seed_input_values_present", "input_values_present")):
            assert isclose(avg(values), row[field], rel_tol=1e-12, abs_tol=1e-12)
            assert sum(v is not None for v in values) == row[count_field]
        assert (len(rows),len(seed_groups),len(input_groups)) == (row["rows"],row["seed_inputs"],row["inputs"])
    return dict(scope="Mechanical arithmetic replay by the authoring session, not independent review",
                source_rows=len(raw), cubic_evaluations=sum(len(r["evaluations"]) for r in catalog),
                support_strata=4, draw_strata=12, within_input_trajectory_rows=len(trajectories),
                weighting_rows=8, passed=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", type=Path)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.data)
    with args.receipt.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result))
