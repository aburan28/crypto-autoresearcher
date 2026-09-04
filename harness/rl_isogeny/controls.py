"""Controls and evaluation for the search (harness.rl_isogeny).

exhaustive_oracle   enumerate the certified isogeny class (tools.isogeny_dreg_search)
                    and score EVERY (member, presentation) state with the same
                    meter and cache the agents use.  At toy scale this is the
                    ground truth a learned policy is judged against: regret,
                    hit rate on the optimum, and -- the pre-registered reading --
                    whether the score is constant across the class per
                    presentation.
summarize           per-run statistics of episode records.
compare             paired comparison of an agent against the random baseline.
"""
from __future__ import annotations

import math
import random
import time
from typing import Dict, List, Optional, Sequence

from tools.isogeny_dreg_search import DEFAULT_PRIMES, enumerate_isogeny_class, iso_key

from .env import IsogenyPDPEnv


def _band(vals: Sequence[float]) -> Optional[dict]:
    vals = [v for v in vals if v is not None and not (isinstance(v, float) and math.isinf(v))]
    if not vals:
        return None
    mu = sum(vals) / len(vals)
    sd = (sum((v - mu) ** 2 for v in vals) / max(1, len(vals) - 1)) ** 0.5
    return {"min": min(vals), "max": max(vals), "mean": mu, "sd": sd, "n": len(vals)}


def exhaustive_oracle(env: IsogenyPDPEnv, max_members: Optional[int] = None,
                      primes: Sequence[int] = DEFAULT_PRIMES, verbose: bool = False,
                      keep_rows: int = 5000) -> dict:
    t0 = time.time()
    rng = random.Random(env.seed + 7919)
    enum = enumerate_isogeny_class(env.a0, env.b0, env.p, rng, primes=tuple(primes),
                                   max_members=max_members, exact_trace_limit=env.exact_trace_limit,
                                   verbose=verbose)
    specs = env.spec_list()
    rows = []
    best = None
    per_spec: Dict[str, List[float]] = {s.label(): [] for s in specs}
    per_spec_rel: Dict[str, List[tuple]] = {s.label(): [] for s in specs}
    excess_states = []
    for m in enum.members:
        curve = env._curve_for(m.a, m.b)
        for spec in specs:
            meas = env.measure(curve, spec)
            row = {"j": m.j, "a": m.a, "b": m.b, "depth": m.depth, "spec": spec.label(),
                   "score": meas.score, "excess_fall": meas.excess_fall, "deficit_excess": meas.deficit_excess,
                   "d_ff_real": meas.d_ff_real, "d_ff_null": meas.d_ff_null, "log2_nnz": meas.log2_nnz,
                   "coverage": meas.coverage, "feasible": meas.feasible}
            rows.append(row)
            per_spec[spec.label()].append(meas.score)
            per_spec_rel[spec.label()].append((meas.excess_fall, meas.deficit_excess))
            if meas.excess_fall > 0 or meas.deficit_excess > 0:
                excess_states.append(row)
            if meas.feasible and (best is None or meas.score > best["score"]):
                best = dict(row)
    spec_stats = {}
    for label, vals in per_spec.items():
        b = _band(vals)
        rel = per_spec_rel[label]
        spec_stats[label] = {
            **(b or {}),
            # exact constancy of the NULL-RELATIVE terms (the pre-registered reading)
            "excess_constant": len(set(rel)) == 1,
            "excess_values": sorted(set(rel)),
            # spread of the shape term across the class, in bits (coefficient
            # coincidences at random x_R move nnz by a few entries)
            "shape_spread_bits": (max(vals) - min(vals)) if vals else None,
            "class_constant": bool(b and b["max"] - b["min"] < 1e-9),
        }
    class_constant_all = all(v["class_constant"] for v in spec_stats.values()) if spec_stats else None
    excess_constant_all = all(v["excess_constant"] for v in spec_stats.values()) if spec_stats else None
    return {
        "certified": enum.certified,
        "coverage_fraction": enum.coverage_fraction,
        "class_size": len(enum.members),
        "predicted_weighted": enum.predicted_weighted,
        "observed_weighted": enum.observed_weighted,
        "primes_used": enum.primes_used,
        "order_checks_passed": enum.order_checks_passed,
        "modular_checks_passed": enum.modular_checks_passed,
        "n_states": len(rows),
        "best": best,
        "per_spec": spec_stats,
        "class_constant_per_spec": class_constant_all,
        "excess_constant_per_spec": excess_constant_all,
        "max_shape_spread_bits": max((v["shape_spread_bits"] or 0.0) for v in spec_stats.values()) if spec_stats else None,
        "states_with_excess": excess_states,
        "rows": rows[:keep_rows],
        "rows_truncated": len(rows) > keep_rows,
        "seconds": time.time() - t0,
    }


def summarize(records: Sequence[dict], oracle_best: Optional[float] = None, tol: float = 1e-9) -> dict:
    best = [r["best_score"] for r in records]
    final = [r["final_score"] for r in records]
    out = {
        "episodes": len(records),
        "best_score": _band(best),
        "final_score": _band(final),
        "true_return": _band([r["true_return"] for r in records]),
        "planted_hit_rate": sum(1 for r in records if r["planted_hit"]) / max(1, len(records)),
        "seconds": sum(r["seconds"] for r in records),
    }
    if oracle_best is not None:
        out["regret_best"] = _band([oracle_best - b for b in best])
        out["fraction_best_optimal"] = sum(1 for b in best if b >= oracle_best - tol) / max(1, len(best))
        out["fraction_final_optimal"] = sum(1 for f in final if f >= oracle_best - tol) / max(1, len(final))
    return out


def compare(agent_records: Sequence[dict], random_records: Sequence[dict]) -> dict:
    """Paired comparison on best-in-episode score (same env, same episode budget)."""
    a = [r["best_score"] for r in agent_records]
    b = [r["best_score"] for r in random_records]
    n = min(len(a), len(b))
    if n == 0:
        return {}
    diffs = [a[i] - b[i] for i in range(n)]
    mu = sum(diffs) / n
    sd = (sum((d - mu) ** 2 for d in diffs) / max(1, n - 1)) ** 0.5
    se = sd / math.sqrt(n) if n > 1 else float("inf")
    return {"n": n, "mean_diff_best_score": mu, "sd": sd, "se": se,
            "z": (mu / se) if se > 0 else 0.0,
            "agent_planted_hit_rate": sum(1 for r in agent_records[:n] if r["planted_hit"]) / n,
            "random_planted_hit_rate": sum(1 for r in random_records[:n] if r["planted_hit"]) / n}
