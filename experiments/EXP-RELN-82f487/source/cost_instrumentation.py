"""Predictor evaluation cost c_f, measured in-process in point-addition
equivalents, against the Theta(B) lookup cost, per specification.yaml's
secondary metrics and H3. Measured on THIS machine, THIS implementation --
labelled as such, never transferred."""
from __future__ import annotations

import time

import numpy as np


def measure_point_addition_time(curve, n_reps=20000) -> float:
    import hashlib
    P = None
    for x in range(1, curve.p):
        P = curve.lift_x(x)
        if P is not None:
            break
    Q = curve.mul(2, P)
    t0 = time.perf_counter()
    R = P
    for _ in range(n_reps):
        R = curve.add(R, Q)
    t1 = time.perf_counter()
    return (t1 - t0) / n_reps


def measure_feature_and_gnn_inference_time(feature_fn, model_predict_fn, targets, n_sample=200):
    t0 = time.perf_counter()
    feats = feature_fn(targets[:n_sample])
    t1 = time.perf_counter()
    _ = model_predict_fn(feats)
    t2 = time.perf_counter()
    n = len(targets[:n_sample])
    return {
        "feature_time_per_target": (t1 - t0) / n,
        "inference_time_per_target": (t2 - t1) / n,
        "total_c_f_time_per_target": (t2 - t0) / n,
        "n_sample": n,
    }


def measure_theta_b_lookup_time(lookup_fn, targets, n_sample=50):
    sample = targets[:n_sample]
    t0 = time.perf_counter()
    for tgt in sample:
        lookup_fn(tgt)
    t1 = time.perf_counter()
    return (t1 - t0) / max(1, len(sample))


def cost_ratio_report(point_add_time, c_f_time, lookup_time, B):
    c_f_in_point_adds = c_f_time / point_add_time if point_add_time > 0 else float("nan")
    lookup_in_point_adds = lookup_time / point_add_time if point_add_time > 0 else float("nan")
    ratio_cf_to_B_lookups = c_f_time / (B * point_add_time) if point_add_time > 0 else float("nan")
    return {
        "point_addition_time_seconds": point_add_time,
        "c_f_time_seconds": c_f_time,
        "c_f_point_addition_equivalents": c_f_in_point_adds,
        "theta_b_lookup_time_seconds": lookup_time,
        "theta_b_lookup_point_addition_equivalents": lookup_in_point_adds,
        "c_f_over_B_lookups_ratio": ratio_cf_to_B_lookups,
        "B": B,
    }
