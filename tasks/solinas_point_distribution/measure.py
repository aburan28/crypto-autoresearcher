"""Exact whole-curve distributions; no scalar or discrete-log inputs."""
import hashlib
import json
import math
import random

import numpy as np


def seed_for(seed, *parts):
    blob = json.dumps([seed, *parts], separators=(",", ":")).encode()
    return int.from_bytes(hashlib.sha256(blob).digest()[:16], "big")


def identity(p, a, b):
    raw = {"p": int(p), "A": int(a), "B": int(b), "model": "short-Weierstrass"}
    digest = hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return "urn:ec-point-distribution:1:sha256:" + digest


def naf_weight(n):
    weight = 0
    while n:
        if n & 1:
            n -= 2 - (n & 3)
            weight += 1
        n //= 2
    return weight


def field_arrays(p):
    x = np.arange(p, dtype=np.int64)
    roots = np.full(p, -1, dtype=np.int32)
    y = np.arange((p + 1) // 2, dtype=np.int64)
    roots[y * y % p] = y
    return x, roots


def exact_weights(p, a, b, x, roots):
    if (4 * a**3 + 27 * b**2) % p == 0:
        raise ValueError("singular curve")
    rhs = ((x * x % p) * x + a * x + b) % p
    return np.where(roots[rhs] < 0, 0, np.where(rhs == 0, 1, 2)).astype(np.uint8)


def scalar_weight(p, a, b, x):
    rhs = (x * x % p * x + a * x + b) % p
    value = pow(rhs, (p - 1) // 2, p)
    return 1 if value == 0 else (2 if value == 1 else 0)


def make_probes(p, seed, uid, uniform_count, window_count):
    rng = random.Random(seed_for(seed, uid, "probes"))
    if p <= (1 << 63) - 1:
        probes = rng.sample(range(p), uniform_count)
    else:
        seen = set()
        probes = []
        while len(probes) < uniform_count:
            x = rng.randrange(p)
            if x not in seen:
                seen.add(x)
                probes.append(x)
    start = rng.randrange(p)
    return probes, start, [(start + i) % p for i in range(window_count)]


def correlation(indicators, lag):
    left = indicators[:-lag].astype(np.float64)
    right = indicators[lag:].astype(np.float64)
    left -= left.mean()
    right -= right.mean()
    denominator = math.sqrt(float(left @ left) * float(right @ right))
    return float(left @ right) / denominator if denominator else None


def circular_gaps(indicators):
    positions = np.flatnonzero(indicators)
    if not len(positions):
        return {"histogram_1_to_32_plus_overflow": [0] * 33, "max_empty_run": len(indicators)}
    gaps = np.diff(np.append(positions, positions[0] + len(indicators)))
    hist = np.bincount(np.minimum(gaps, 33), minlength=34)[1:34]
    return {"histogram_1_to_32_plus_overflow": hist.tolist(), "max_empty_run": int(gaps.max() - 1)}


def window_stats(weights, lags):
    lift = weights > 0
    padded = np.concatenate(([True], lift, [True]))
    empty_runs = np.diff(np.flatnonzero(padded)) - 1
    return {
        "coverage": float(lift.mean()), "point_density": float(weights.mean()),
        "lag_correlations": {str(lag): correlation(lift, lag) for lag in lags},
        "max_empty_run": int(empty_runs.max()),
    }


def probe_stats(p, xs, weights, bins):
    labels = np.fromiter((x * bins // p for x in xs), dtype=np.int64, count=len(xs))
    counts = np.bincount(labels, minlength=bins)
    mass = np.bincount(labels, weights=weights, minlength=bins)
    mean = float(weights.mean())
    expected = mean * counts
    keep = expected > 0
    dispersion = float(np.sum((mass[keep] - expected[keep]) ** 2 / expected[keep])) if mean else None
    return {"coverage": float((weights > 0).mean()), "point_density": mean,
            "proposal_counts": counts.tolist(), "point_mass": mass.astype(int).tolist(),
            "bin_dispersion": dispersion}


def describe_curve(p, a, b, n, uid, probes, probe_weights, start, window_weights, config, census=None):
    trace = p + 1 - n
    if trace * trace > 4 * p:
        raise ValueError("Hasse bound failed")
    normal = trace / (2 * math.sqrt(p))
    sample = probe_stats(p, probes, probe_weights, config["x_bins"])
    window = window_stats(window_weights, config["lags"])
    shuffled = window_weights.copy()
    np.random.default_rng(seed_for(config["seed"], uid, "shuffle")).shuffle(shuffled)
    result = {"curve_id": uid, "p": p, "A": a, "B": b, "N": n, "trace": trace,
              "normalized_trace": normal, "trace_square": trace * trace / (4 * p),
              "window_start": start, "uniform": sample, "window": window,
              "shuffled_window": window_stats(shuffled, config["lags"]),
              "window_lag_1": window["lag_correlations"]["1"],
              "probe_bin_dispersion": sample["bin_dispersion"]}
    if census is not None:
        zero_x = np.flatnonzero(census == 1)
        covered = int(np.count_nonzero(census))
        if 2 * covered != n - 1 + len(zero_x):
            raise ValueError("coverage identity failed")
        bin_labels = np.arange(p, dtype=np.int64) * config["x_bins"] // p
        mass = np.bincount(bin_labels, weights=census, minlength=config["x_bins"]).astype(np.int64)
        result["census"] = {"coverage_count": covered, "coverage": covered / p,
                            "affine_point_density": (n - 1) / p, "zero_x": zero_x.tolist(),
                            "x_bin_point_mass": mass.tolist(), **circular_gaps(census > 0)}
    return result


def encode_coordinates(xs, p):
    width = (p.bit_length() + 7) // 8
    return np.frombuffer(b"".join(x.to_bytes(width, "big") for x in xs), dtype=np.uint8).reshape(len(xs), width)


def decode_coordinates(encoded):
    return [int.from_bytes(row.tobytes(), "big") for row in encoded]
