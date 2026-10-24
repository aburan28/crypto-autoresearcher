"""Independent Sage/Kronecker verification of the full 21 x 1228 matrix."""

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

from sage.all import ZZ, kronecker
from sage.version import version as sage_version

here = Path(__file__).resolve().parent
study = here.parent.parent / "nist_seed_skipped_curves_20261016"
analysis = json.loads((here / "analysis.json").read_text())
assessed_path = study / "assessed.json"
traits_path = study / "traits.json"
assert analysis["inputs_sha256"] == {
    "assessed.json": hashlib.sha256(assessed_path.read_bytes()).hexdigest(),
    "traits.json": hashlib.sha256(traits_path.read_bytes()).hexdigest(),
}
assessed = json.loads(assessed_path.read_text())
traits = json.loads(traits_path.read_text())
originals = {x["identity"]["curve_uid"]: x for x in assessed["candidate_rows"]}
originals.update({x["identity"]["curve_uid"]: x for x in traits["published_controls"].values()})
assert len(originals) == 21

primes = analysis["odd_prime_degrees"]
assert len(primes) == 1228
assert primes[0] == 3 and primes[-1] == 9973
checked = 0
for row in analysis["rows"]:
    source = originals[row["curve_uid"]]
    assert row["p_hex"] == source["p_hex"] and row["n_hex"] == source["n_hex"]
    p, n = ZZ(source["p_hex"]), ZZ(source["n_hex"])
    delta = (p + 1 - n)**2 - 4*p
    assert row["delta_hex_signed"] == hex(int(delta))
    for ell, got in zip(primes, row["signature"], strict=True):
        sign = kronecker(delta, ZZ(ell))
        expected = {1: "E", 0: "R", -1: "A"}[sign]
        assert got == expected, (row["curve_uid"], ell, got, expected)
        checked += 1
assert checked == 21 * 1228

# Recompute the finite label-allocation diagnostic using sets instead of the
# generator's integer bit masks. This is still a descriptive comparison, not
# a sampling model for 1997 decisions.
rows = analysis["rows"]
choices = []
for bits in (192, 224, 239, 256):
    indices = [i for i, row in enumerate(rows) if row["field_bits"] == bits]
    count = sum(rows[i]["label"] == "omitted" for i in indices)
    choices.append(list(itertools.combinations(indices, count)))
inert_sets = [
    frozenset(i for i, row in enumerate(rows) if row["signature"][j] == "A")
    for j in range(len(primes))
]
all_indices = frozenset(range(len(rows)))
hist_all_inert = Counter()
hist_perfect = Counter()
hist_pair_score = Counter()
for allocation in itertools.product(*choices):
    omitted = frozenset(itertools.chain.from_iterable(allocation))
    hist_all_inert[sum(omitted.issubset(inert) for inert in inert_sets)] += 1
    hist_perfect[sum(inert == omitted or inert == all_indices - omitted for inert in inert_sets)] += 1
    score = 0
    for bits in (192, 224, 239, 256):
        group = [i for i, row in enumerate(rows) if row["field_bits"] == bits]
        for i in group:
            if i not in omitted:
                continue
            for j in group:
                if j in omitted:
                    continue
                a, b = rows[i]["isogeny_count"], rows[j]["isogeny_count"]
                score += 2 if a > b else 1 if a == b else 0
    hist_pair_score[score] += 1
diagnostic = analysis["comparison"]["conditional_allocation_diagnostic"]
assert sum(hist_all_inert.values()) == diagnostic["allocation_count"] == 4480
assert dict(sorted(hist_all_inert.items())) == {
    int(k): v for k, v in diagnostic["all_inert_prime_count_histogram"].items()
}
assert dict(sorted(hist_perfect.items())) == {
    int(k): v for k, v in diagnostic["perfect_separator_count_histogram"].items()
}
observed = diagnostic["observed_all_omitted_inert_prime_count"]
tail = sum(v for k, v in hist_all_inert.items() if k >= observed)
assert tail == diagnostic["tail_at_least_observed_numerator"] == 853
assert hist_perfect[0] == 4475
pairwise = diagnostic["availability_pairwise"]
assert dict(sorted(hist_pair_score.items())) == {
    int(k): v for k, v in pairwise["score_histogram"].items()
}
pair_tail = sum(v for k, v in hist_pair_score.items() if k >= pairwise["score_twice_wins_plus_ties"])
assert pairwise["omitted_higher_pairs"] == 20
assert pairwise["equal_pairs"] == 1
assert pairwise["omitted_lower_pairs"] == 4
assert pair_tail == pairwise["one_sided_tail_numerator"] == 100
summary = {
    "schema": "nist-seed-rational-isogeny-verification/v1",
    "sage_version": sage_version,
    "analysis_sha256": hashlib.sha256((here / "analysis.json").read_bytes()).hexdigest(),
    "checked_cells": checked,
    "rows": len(analysis["rows"]),
    "allocation_count": 4480,
    "all_inert_tail_at_least_observed_numerator": tail,
    "no_perfect_separator_allocation_count": hist_perfect[0],
    "availability_pairwise_tail_numerator": pair_tail,
    "status": "PASS",
}
(here / "sage_verification.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
print(json.dumps(summary, sort_keys=True))
