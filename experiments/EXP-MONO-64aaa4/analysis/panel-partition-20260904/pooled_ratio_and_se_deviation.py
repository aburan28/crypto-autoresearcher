#!/usr/bin/env python3
"""
Read-only re-analysis: exact conditional-binomial pooled CM/ordinary
transversal collision-rate ratio (matching the archive's existing FB4/
EV-MONO-9c760b convention), and se_deviation mean comparison against
H-MONO-45183a Part B's closed form 6*(tau-1)/N, both computed on:
  (a) the full 100-cell panel (reproduction/sanity check), and
  (b) the CLEAN 36-cell subset produced by partition_panel.py, and
  (c) the CONTAMINATED 64-cell subset (for comparison).

Requires partition_panel.py to have been run first (produces
clean_cells.json / contaminated_cells.json in this directory).

Method for the pooled ratio: every cell draws NTUPLES=20000 transversal
tuples for both its ordinary and CM curve, so the pair-count denominators
are equal across arms and the rate ratio r = (X_cm/n_cm)/(X_ord/n_ord)
reduces to r = X_cm/X_ord. Conditional on the pooled total T = X_cm+X_ord,
X_cm ~ Binomial(T, p) under a fixed true ratio r, with p = r/(r+1). An
exact Clopper-Pearson 95% CI for p on (X_cm, T) transforms via r=p/(1-p)
to an exact 95% CI for the ratio. This is EXACT, not an approximation.

Method for se_deviation: reuses the archived per-cell se_deviation field
verbatim (computed by the original run as
  predicted = 6*(tau-1)/N
  se = binomial_se_pairs(tau, N, ntuples)  # Poisson/binomial approx SE
  se_deviation = (observed_total_pairs_colliding - predicted*ntuples) / se
), which already matches H-MONO-45183a Part B's closed form and a simple
Poisson-based SE approximation -- explicitly an APPROXIMATION, not exact.
"""
import json
import statistics
from pathlib import Path
from scipy import stats

OUT_DIR = Path("/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-64aaa4/analysis/panel-partition-20260904")
RAW_RESULT_PATH = Path("/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-cb905d/runs/RUN-MONO-cb905d-1/raw-result.json")


def pooled_ratio(cells):
    X_cm = sum(c["cm"]["observed_total_pairs_colliding"] for c in cells)
    X_ord = sum(c["ord"]["observed_total_pairs_colliding"] for c in cells)
    T = X_cm + X_ord
    p_hat = X_cm / T
    r_hat = p_hat / (1 - p_hat)
    lo, hi = stats.binomtest(X_cm, T).proportion_ci(confidence_level=0.95, method="exact")
    r_lo = lo / (1 - lo)
    r_hi = hi / (1 - hi)
    return {"n_cells": len(cells), "X_cm": X_cm, "X_ord": X_ord, "T": T,
            "ratio": r_hat, "ci_lo": r_lo, "ci_hi": r_hi}


def se_dev_means(cells):
    return {
        "n": len(cells),
        "ordinary_mean": statistics.mean(c["ord"]["se_deviation"] for c in cells),
        "cm_mean": statistics.mean(c["cm"]["se_deviation"] for c in cells),
    }


def main():
    with open(RAW_RESULT_PATH) as f:
        all_cells = json.load(f)["part_b"]["cells"]
    with open(OUT_DIR / "clean_cells.json") as f:
        clean = json.load(f)
    with open(OUT_DIR / "contaminated_cells.json") as f:
        contaminated = json.load(f)

    assert len(all_cells) == 100
    assert len(clean) + len(contaminated) == 100

    results = {
        "pooled_ratio": {
            "full_100_reproduction": pooled_ratio(all_cells),
            "clean_36": pooled_ratio(clean),
            "contaminated_64": pooled_ratio(contaminated),
        },
        "se_deviation_means": {
            "full_100_all_cells": se_dev_means(all_cells),
            "full_100_tau_ne_1_84_cells": se_dev_means([c for c in all_cells if c["tau"] != 1]),
            "clean_36_all_cells": se_dev_means(clean),
            "clean_20_tau_ne_1_cells": se_dev_means([c for c in clean if c["tau"] != 1]),
        },
    }

    with open(OUT_DIR / "pooled_ratio_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
