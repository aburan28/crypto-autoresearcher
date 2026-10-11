"""Auditable rank and paired cost gate for independently verified rows.

The caller must certify the prime modulus and verify the mathematical rows.
No solver status, duplicate count, or Macaulay rank is a relation certificate.
"""

import random


class RelationRank:
    def __init__(self, modulus, width):
        if type(modulus) is not int or modulus < 2 or width < 1:
            raise ValueError("invalid rank ring")
        self.modulus, self.width = modulus, width
        self.pivots, self.seen = {}, set()

    @property
    def rank(self):
        return len(self.pivots)

    def add(self, coefficients):
        if len(coefficients) != self.width or any(type(x) is not int for x in coefficients):
            raise ValueError("invalid relation vector")
        row = [x % self.modulus for x in coefficients]
        first = next((x for x in row if x), None)
        signature = tuple(x * pow(first, -1, self.modulus) % self.modulus
                          for x in row) if first else tuple(row)
        repeated = signature in self.seen
        self.seen.add(signature)
        for col in range(self.width):
            if not row[col]:
                continue
            if col in self.pivots:
                factor = row[col]
                row = [(x - factor * y) % self.modulus
                       for x, y in zip(row, self.pivots[col])]
            else:
                inverse = pow(row[col], -1, self.modulus)
                self.pivots[col] = [x * inverse % self.modulus for x in row]
                return "independent"
        return "duplicate" if repeated else "dependent"


def comparison_gate(runs, baseline_ids, candidate, *, min_seeds=5, min_rank=8):
    """Conservative paired gate. Unknown/zero-yield cells cannot become wins.

    Every named baseline must finish on every seed. Compare each candidate
    against the fastest baseline on that seed. Bootstrap entire seed pairs,
    never individual (correlated) rows. This is a stage gate, not a DLP claim.
    """
    answer = {"candidate": candidate, "status": "insufficient_evidence",
              "full_dlp_speedup": None, "min_seeds": min_seeds, "min_rank": min_rank,
              "ratio": None, "paired_bootstrap_95_interval": None}
    cells = {}
    for run in runs:
        key = (run["seed"], run["backend"])
        if key in cells:
            raise ValueError("duplicate seed/backend: repetitions need their own comparison")
        cells[key] = run
    seeds = sorted({seed for seed, backend in cells if backend == candidate})
    paired_costs = []
    for seed in seeds:
        wanted = [cells.get((seed, b)) for b in [candidate, *baseline_ids]]
        if any(r is None or r.get("status") != "complete" or r.get("rank", 0) < min_rank
               or not r.get("verification_replayed") for r in wanted):
            return {**answer, "reason": "missing, incomplete, unverified or low-rank cell"}
        if len({(r["workload_sha256"], r["base_sha256"], r["accounting"])
                for r in wanted}) != 1:
            raise ValueError("unpaired workload, base or accounting boundary")
        costs = [r["charged_wall_seconds"] / r["rank"] for r in wanted]
        paired_costs.append((costs[0], min(costs[1:])))
    if len(paired_costs) < min_seeds:
        return {**answer, "reason": "too few independent seeds"}
    def ratio(pairs):
        return sum(x for x, _ in pairs) / sum(y for _, y in pairs)
    rng = random.Random(20260928)
    draws = sorted(ratio(rng.choices(paired_costs, k=len(paired_costs))) for _ in range(10000))
    observed, interval = ratio(paired_costs), [draws[249], draws[9749]]
    stable = all(x <= 0.5 * y for x, y in paired_costs)
    return {**answer, "status": "pass" if stable and interval[1] <= 0.5 else "not_met",
            "ratio": observed, "paired_bootstrap_95_interval": interval,
            "all_seed_ratios_at_most_half": stable, "reason": None}
