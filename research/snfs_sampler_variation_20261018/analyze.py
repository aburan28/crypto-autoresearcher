"""Saved-input support, multiplicities and within-input trajectories.

No number-field point-search program is launched. The cubic catalog is exact
bounded arithmetic on the sampler's eight possible coefficient patterns.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product
from math import comb, isqrt
from pathlib import Path
import csv
import hashlib
import json
import platform
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
RUN = "experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-e89532/"
MAIN = "experiments/EXP-ECDLP-4c6a09/implementation/src/main.rs"
LIB = "experiments/EXP-ECDLP-84af7b/implementation/nfield/src/"
INPUTS = [RUN + "raw-result.json", RUN + "execution-receipt.json", MAIN,
          LIB + "ecnf.rs", LIB + "rng.rs"]
SHAPES = [("P-192", 3, 3), ("P-224", 7, 3),
          ("P-256", 8, 5), ("P-384", 12, 5)]


def key(cell, with_seed=False):
    f = cell["field"]
    result = (tuple(f["g"]), f["p"], cell["root_mod_p"],
              cell["curve"]["A"], cell["curve"]["B"])
    return result + (cell["seed"],) if with_seed else result


def coefficient_support(d, w):
    for positions in combinations(range(1, d), w - 2):
        for signs in product((-1, 1), repeat=w - 1):
            g = [0] * (d + 1)
            g[0], g[d] = signs[0], 1
            for position, sign in zip(positions, signs[1:]):
                g[position] = sign
            yield tuple(g)


def eval_poly(g, t):
    value = 0
    for coefficient in reversed(g):
        value = value * t + coefficient
    return value


def primes_through(n):
    sieve = bytearray(b"\1") * (n + 1)
    sieve[:2] = b"\0\0"
    for p in range(2, isqrt(n) + 1):
        if sieve[p]:
            sieve[p*p::p] = b"\0" * ((n - p*p)//p + 1)
    return [p for p in range(2, n + 1) if sieve[p]]


def cubic_catalog():
    gs = list(coefficient_support(3, 3))
    bound = max(eval_poly(g, 1 << k) for g in gs for k in range(4, 13))
    divisors = primes_through(isqrt(bound))
    rows = []
    for g in gs:
        evaluations = []
        # A monic integral cubic is irreducible iff it has no rational root;
        # constant +-1 limits such roots to +-1.
        irreducible = all(eval_poly(g, r) != 0 for r in (-1, 1))
        for k in range(4, 13):
            p = eval_poly(g, 1 << k)
            factor = next((q for q in divisors if q*q <= p and p % q == 0), None)
            prime = p >= 2 and factor is None
            evaluations.append(dict(k=k, value=p, prime=prime,
                                    smallest_prime_factor=factor,
                                    meets_minimum=p >= (1 << 12),
                                    trial_divisor_bound=isqrt(p)))
        eligible = [r for r in evaluations if r["prime"] and r["meets_minimum"]]
        rows.append(dict(g=list(g), irreducible_by_rational_root_test=irreducible,
                         evaluations=evaluations,
                         first_eligible=eligible[0] if eligible and irreducible else None))
    return rows


def mean(values):
    present = [Fraction(v) for v in values if v is not None]
    return float(sum(present) / len(present)) if present else None


def dump(folder, name, value):
    with (folder / name).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def main(out):
    wall, cpu = time.monotonic(), time.process_time()
    out.mkdir()  # Refuse overwriting any earlier analysis/report directory.
    raw = json.loads((ROOT / INPUTS[0]).read_text())
    cells = raw["cells"]
    catalog = cubic_catalog()
    dump(out, "cubic-catalog.json", catalog)
    field_draws = []
    assert len(cells) % 5 == 0
    for start in range(0, len(cells), 5):
        block = cells[start:start+5]
        assert [c["curve_index"] for c in block] == list(range(5))
        assert all(c["field"] == block[0]["field"] and
                   c["seed"] == block[0]["seed"] for c in block)
        first = block[0]
        f = first["field"]
        field_draws.append(dict(start_row=start, seed=first["seed"],
                                shape=f["shape"], kind=f["kind"], g=f["g"],
                                k=f["k"], p=f["p"],
                                distinct_curve_pairs=len({(c["curve"]["A"], c["curve"]["B"]) for c in block})))
    dump(out, "accepted-field-draws.json", field_draws)
    support = []
    multiplicities = []
    for shape, d, w in SHAPES:
        universe = set(coefficient_support(d, w))
        formula = 2**(w-1) * comb(d-1, w-2)
        assert len(universe) == formula
        draws = [r for r in field_draws if r["shape"] == shape and r["kind"] == "random_g"]
        observed = {tuple(r["g"]) for r in draws}
        assert observed <= universe
        admissible = {tuple(r["g"]) for r in catalog if r["first_eligible"]} if d == 3 else None
        if d == 3:
            assert observed == admissible
            for row in draws:
                entry = next(c for c in catalog if c["g"] == row["g"])
                assert (row["k"], int(row["p"])) == (entry["first_eligible"]["k"], entry["first_eligible"]["value"])
        support.append(dict(shape=shape, d=d, weight=w, coefficient_patterns=formula,
                            enumerated_patterns=len(universe), accepted_draws=len(draws),
                            observed_distinct_g=len(observed),
                            admissible_support_count=len(admissible) if admissible is not None else None,
                            support_scope="exact cubic rational-root/prime catalog" if d == 3 else "pre-filter coefficient support only; admissible support not computed"))
        for seed in (1, 2, 3):
            counts = Counter(tuple(r["g"]) for r in draws if r["seed"] == seed)
            multiplicities.append(dict(shape=shape, seed=seed, accepted_draws=sum(counts.values()),
                                       distinct_g=len(counts),
                                       g_counts=[dict(g=list(g), draws=n) for g, n in sorted(counts.items())]))
    dump(out, "sampler-support.json", support)
    dump(out, "draw-multiplicities.json", multiplicities)

    all_groups = defaultdict(list)
    for index, cell in enumerate(cells):
        all_groups[key(cell)].append((index, cell))
    cross_seed, trajectories = [], []
    for input_key, rows in all_groups.items():
        seeds = sorted({c["seed"] for _, c in rows})
        if len(seeds) < 2:
            continue
        input_id = "input-" + hashlib.sha256(json.dumps(input_key).encode()).hexdigest()[:12]
        representatives = [next((i, c) for i, c in rows if c["seed"] == seed) for seed in seeds]
        profiles = {json.dumps(c["rungs"], sort_keys=True) for _, c in representatives}
        sample_lists = {json.dumps(c["sample_points"], sort_keys=True) for _, c in representatives}
        cross_seed.append(dict(input_id=input_id, g=list(input_key[0]), p=input_key[1],
                               root=input_key[2], A=input_key[3], B=input_key[4], seeds=seeds,
                               all_raw_row_indices=[i for i, _ in rows],
                               representative_raw_rows=[i for i, _ in representatives],
                               auxiliary_prime_lists_match=len({tuple(c["aux_primes"]) for _, c in representatives}) == 1,
                               torsion_bounds=sorted({c["torsion_bound_T"] for _, c in representatives}),
                               distinct_rung_profiles=len(profiles),
                               distinct_saved_sample_lists=len(sample_lists)))
        for index, cell in representatives:
            for rung in cell["rungs"]:
                trajectories.append(dict(input_id=input_id, raw_row=index, seed=cell["seed"], **rung))
    dump(out, "within-input-groups.json", cross_seed)
    with (out / "within-input-trajectories.csv").open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(trajectories[0]))
        writer.writeheader()
        writer.writerows(trajectories)

    weighted = []
    for shape, _, _ in SHAPES:
        rows = [c for c in cells if c["field"]["kind"] == "random_g" and c["field"]["shape"] == shape]
        by_seed_input, by_input = defaultdict(list), defaultdict(list)
        for cell in rows:
            by_seed_input[key(cell, True)].append(cell)
        for skey, repeats in by_seed_input.items():
            by_input[skey[:-1]].append(repeats)
        for metric in ("final_distinct_residues", "gamma"):
            value = lambda c: c["rungs"][-1]["distinct_residues"] if metric == "final_distinct_residues" else c["gamma"]
            row_values = [value(c) for c in rows]
            seed_values = [mean([value(c) for c in repeats]) for repeats in by_seed_input.values()]
            input_values = [mean([mean([value(c) for c in repeats]) for repeats in seeds]) for seeds in by_input.values()]
            weighted.append(dict(shape=shape, metric=metric,
                                 row_weighted_mean=mean(row_values),
                                 seed_input_grouped_mean=mean(seed_values),
                                 input_grouped_mean=mean(input_values),
                                 rows=len(rows), seed_inputs=len(by_seed_input), inputs=len(by_input),
                                 row_values_present=sum(v is not None for v in row_values),
                                 seed_input_values_present=sum(v is not None for v in seed_values),
                                 input_values_present=sum(v is not None for v in input_values)))
    dump(out, "weighting-views.json", weighted)
    receipt = json.loads((ROOT / INPUTS[1]).read_text())
    summary = dict(scope="Saved-input descriptive reanalysis; no field/curve search launched",
                   source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                   raw_rows=len(cells), accepted_field_blocks=len(field_draws),
                   seed_input_keys=len({key(c, True) for c in cells}), input_keys=len(all_groups),
                   cross_seed_inputs=len(cross_seed),
                   cross_seed_different_profiles=sum(r["distinct_rung_profiles"] > 1 for r in cross_seed),
                   cross_seed_different_sample_lists=sum(r["distinct_saved_sample_lists"] > 1 for r in cross_seed),
                   native_status=receipt["status"],
                   producer_returncode=receipt["returncode"], checker_returncode=receipt["check_returncode"],
                   sources=[dict(path=p, sha256=hashlib.sha256((ROOT / p).read_bytes()).hexdigest()) for p in INPUTS],
                   analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   wall_seconds=time.monotonic()-wall, cpu_seconds=time.process_time()-cpu,
                   python=platform.python_version(), platform=platform.platform())
    dump(out, "summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("raw_rows", "seed_input_keys", "input_keys", "cross_seed_inputs", "cross_seed_different_profiles", "wall_seconds")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    main(args.out)
