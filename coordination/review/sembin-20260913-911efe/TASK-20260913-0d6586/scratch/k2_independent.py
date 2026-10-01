#!/usr/bin/env python3
"""K2: per-configuration shape, known-false splits, random-V null, odd-n.

Trace, second-irreducible search, LSB split and statistics are this file's.
modulus_for / _is_irreducible come from EXP-SEMBIN-354a75 (source field),
not from EXP-SEMBIN-911efe/code.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import time

import numpy as np

REPO = os.environ.get("REPO", "/workspace")
sys.path.insert(0, os.path.join(REPO, "experiments/EXP-SEMBIN-354a75/code"))

from binary_field import modulus_for, _is_irreducible  # SOURCE, not producer

LABEL_RE = re.compile(
    r"^n(\d+)-m(\d+)-t(\d+)-k(\d+)"
    r"-(low_degree_polynomial|random_k_dimensional)"
    r"-(B_eq_1|random_B)-s(\d+)$"
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "k2_out.json")
PER_R = os.path.join(
    REPO, "experiments/EXP-SEMBIN-354a75/runs/RUN-SEMBIN-1b9afe/per-R-counts.json"
)
ODD = os.path.join(
    REPO,
    "experiments/EXP-SEMBIN-911efe/runs/RUN-SEMBIN-8be036/odd-n-per-R-counts.json",
)
PARITY = os.path.join(
    REPO, "experiments/EXP-SEMBIN-911efe/runs/RUN-SEMBIN-8be036/parity-split.json",
)
N1_PASS1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "k1_n1_pass1.json")
BOOT = 2500
BOOT_SEED = 20260913
Z95 = 1.959963984540054

PRINTED = {
    # E usable, 10000 draws. From TASK-20260913-31d530/report.md table.
    ("n20-m2-t2-k10", "low_degree_polynomial", "B_eq_1"): {
        "mean": 0.45090, "hit_fraction": 0.29840, "P_ratio": 0.7584,
        "f_dispersion": 0.8222},
    ("n20-m2-t2-k10", "low_degree_polynomial", "random_B"): {
        "mean": 0.50030, "hit_fraction": 0.31620, "P_ratio": 0.8036,
        "f_dispersion": 0.8032},
    ("n20-m2-t2-k10", "random_k_dimensional", "B_eq_1"): {
        "mean": 0.51350, "hit_fraction": 0.40450, "P_ratio": 1.0280,
        "f_dispersion": 1.0072},
    ("n20-m2-t2-k10", "random_k_dimensional", "random_B"): {
        "mean": 0.51630, "hit_fraction": 0.40120, "P_ratio": 1.0196,
        "f_dispersion": 0.9949},
    ("n22-m2-t2-k11", "low_degree_polynomial", "B_eq_1"): {
        "mean": 0.50550, "hit_fraction": 0.31360, "P_ratio": 0.7970,
        "f_dispersion": 0.7903},
    ("n22-m2-t2-k11", "low_degree_polynomial", "random_B"): {
        "mean": 0.51630, "hit_fraction": 0.32840, "P_ratio": 0.8346,
        "f_dispersion": 0.8143},
    ("n22-m2-t2-k11", "random_k_dimensional", "B_eq_1"): {
        "mean": 0.49280, "hit_fraction": 0.39100, "P_ratio": 0.9937,
        "f_dispersion": 1.0049},
    ("n22-m2-t2-k11", "random_k_dimensional", "random_B"): {
        "mean": 0.49940, "hit_fraction": 0.39430, "P_ratio": 1.0021,
        "f_dispersion": 1.0030},
    ("n24-m2-t2-k12", "low_degree_polynomial", "B_eq_1"): {
        "mean": 0.48870, "hit_fraction": 0.31320, "P_ratio": 0.7960,
        "f_dispersion": 0.8102},
    ("n24-m2-t2-k12", "low_degree_polynomial", "random_B"): {
        "mean": 0.49540, "hit_fraction": 0.31080, "P_ratio": 0.7899,
        "f_dispersion": 0.7956},
    ("n24-m2-t2-k12", "random_k_dimensional", "B_eq_1"): {
        "mean": 0.51630, "hit_fraction": 0.40370, "P_ratio": 1.0260,
        "f_dispersion": 1.0011},
    ("n24-m2-t2-k12", "random_k_dimensional", "random_B"): {
        "mean": 0.51320, "hit_fraction": 0.40030, "P_ratio": 1.0174,
        "f_dispersion": 0.9972},
}


def clmul(a: int, b: int) -> int:
    out = 0
    while b:
        low = b & -b
        out ^= a * low
        b ^= low
    return out


def reduce_poly(v: int, modulus: int, m: int) -> int:
    while v.bit_length() > m:
        v ^= modulus << (v.bit_length() - m - 1)
    return v


def my_trace(a: int, n: int, modulus: int) -> int:
    t, x = 0, a
    for _ in range(n):
        t ^= x
        x = reduce_poly(clmul(x, x), modulus, n)
    if t not in (0, 1):
        raise ArithmeticError(f"trace left F_2: {t}")
    return t


def second_modulus(n: int) -> int:
    """Next irreducible after modulus_for(n), same search order as binary_field."""
    primary = modulus_for(n)
    head = 1 << n
    for k in range(1, n):
        cand = head | (1 << k) | 1
        if cand != primary and _is_irreducible(n, cand):
            return cand
    for k3 in range(3, n):
        for k2 in range(2, k3):
            for k1 in range(1, k2):
                cand = head | (1 << k3) | (1 << k2) | (1 << k1) | 1
                if cand != primary and _is_irreducible(n, cand):
                    return cand
    raise ArithmeticError(f"no second irreducible of degree {n}")


def parse_label(label: str) -> dict:
    m = LABEL_RE.match(label)
    if not m:
        raise ValueError(label)
    n, mm, t, k, subspace, b_mode, seed = m.groups()
    return {
        "label": label, "n": int(n), "m": int(mm), "t": int(t), "k": int(k),
        "subspace": subspace, "b_mode": b_mode, "seed": int(seed),
    }


def twist_delta(n: int, modulus: int) -> int:
    for d in range(1, 1 << n):
        if my_trace(d, n, modulus) == 1:
            return d
    raise ArithmeticError("no delta")


def f_disp(arr: np.ndarray) -> float | None:
    mean = float(arr.mean())
    if mean <= 0:
        return None
    p = float(np.count_nonzero(arr) / arr.size)
    denom = 1.0 - math.exp(-mean)
    if denom == 0:
        return None
    return p / denom


def summary(arr: np.ndarray) -> dict:
    n = int(arr.size)
    if n == 0:
        return {"n": 0, "mean": None, "var_ddof1": None, "var_over_mean": None,
                "n_nonzero": 0, "hit_fraction": None, "f_dispersion": None}
    mean = float(arr.mean())
    var1 = float(arr.var(ddof=1)) if n > 1 else 0.0
    nz = int(np.count_nonzero(arr))
    return {
        "n": n,
        "mean": mean,
        "var_ddof1": var1,
        "var_over_mean": (var1 / mean) if mean else None,
        "n_nonzero": nz,
        "hit_fraction": nz / n,
        "f_dispersion": f_disp(arr),
        "empty": nz == 0,
    }


def bootstrap_D_and_diff(arr: np.ndarray, rng: np.random.Generator,
                         n_boot: int = BOOT) -> dict:
    """Percentile CI for D=var/mean and for D-(1+mean)."""
    n = int(arr.size)
    if n < 2:
        return {"ok": False}
    idx = rng.integers(0, n, size=(n_boot, n), dtype=np.int32)
    samp = arr[idx]
    means = samp.mean(axis=1)
    vars_ = samp.var(axis=1, ddof=1)
    ok = means > 1e-15
    if not np.any(ok):
        return {"ok": False}
    D = vars_[ok] / means[ok]
    diff = D - (1.0 + means[ok])
    mean_boot = means[ok]
    return {
        "ok": True,
        "n_boot_kept": int(ok.sum()),
        "D_ci95": [float(np.percentile(D, 2.5)), float(np.percentile(D, 97.5))],
        "D_boot_mean": float(D.mean()),
        "mean_ci95": [float(np.percentile(mean_boot, 2.5)),
                       float(np.percentile(mean_boot, 97.5))],
        "D_minus_1_plus_mean_ci95": [
            float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))],
        "D_minus_1_plus_mean_contains_0": bool(
            np.percentile(diff, 2.5) <= 0 <= np.percentile(diff, 97.5)),
        "D_ci_contains_1": bool(
            np.percentile(D, 2.5) <= 1.0 <= np.percentile(D, 97.5)),
    }


def bootstrap_mean(arr: np.ndarray, rng: np.random.Generator,
                    n_boot: int = BOOT) -> list[float] | None:
    n = int(arr.size)
    if n == 0:
        return None
    idx = rng.integers(0, n, size=(n_boot, n), dtype=np.int32)
    means = arr[idx].mean(axis=1)
    return [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]


def bootstrap_ratio(a: np.ndarray, b: np.ndarray, rng: np.random.Generator,
                    n_boot: int = BOOT) -> dict:
    """CI for mean(a) / (2 * mean(concat(a,b))) i.e. class mean / (2 pooled).

    Here `a` is the reachable class, `pooled` is concatenation of a and the
    empty class (or all counts). We pass pooled as `all_counts`.
    """
    return {}  # filled by caller with all-counts bootstrap


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Field:
    def __init__(self):
        self.mod: dict[int, int] = {}
        self.delta: dict[int, int] = {}
        self.alt: dict[int, int] = {}
        self.trc: dict[tuple[int, int, int], int] = {}  # (n, modulus, x)

    def primary(self, n: int) -> int:
        if n not in self.mod:
            self.mod[n] = modulus_for(n)
            self.delta[n] = twist_delta(n, self.mod[n])
            self.alt[n] = second_modulus(n)
        return self.mod[n]

    def tr(self, n: int, x: int, modulus: int | None = None) -> int:
        if modulus is None:
            modulus = self.primary(n)
        key = (n, modulus, int(x))
        if key not in self.trc:
            self.trc[key] = my_trace(int(x), n, modulus)
        return self.trc[key]

    def a_of(self, n: int, side: str) -> int:
        self.primary(n)
        return 0 if side == "E" else self.delta[n]


def split_counts(xs, counts, pis) -> dict[int, np.ndarray]:
    by = {0: [], 1: []}
    for pi, c in zip(pis, counts):
        by[int(pi)].append(c)
    return {k: np.array(v, dtype=np.int64) for k, v in by.items()}


def main() -> int:
    t0 = time.time()
    rng = np.random.default_rng(BOOT_SEED)
    F = Field()

    with open(PER_R) as fh:
        data = json.load(fh)
    n1 = json.load(open(N1_PASS1))
    producer_parity = json.load(open(PARITY))
    odd = json.load(open(ODD))

    # ---- K1 pair-for-pair vs producer (after independent N1 was written) ----
    mine = {(r["label"], r["side"], r["target_index"]): r
            for r in n1["offenders_i"]}
    prod = producer_parity.get("offending_pairs") or []
    prod_keys = {(p["label"], p["side"], p["target_index"]) for p in prod}
    pair_cmp = {
        "N1_i_independent": n1["N1_i_contract_literal_nonzero_single_or_chained"],
        "N1_ii_independent": n1["N1_ii_usable_point_multiset_only"],
        "producer_N1": producer_parity.get("N1"),
        "producer_n_offending_pairs": len(prod),
        "independent_keys": sorted(list(mine.keys())),
        "producer_keys": sorted(list(prod_keys)),
        "keys_equal": mine.keys() == prod_keys,
        "only_in_independent": sorted(list(mine.keys() - prod_keys)),
        "only_in_producer": sorted(list(prod_keys - mine.keys())),
        "field_pair_agreements": [],
    }
    for p in prod:
        key = (p["label"], p["side"], p["target_index"])
        r = mine.get(key)
        if r is None:
            continue
        pair_cmp["field_pair_agreements"].append({
            "key": list(key),
            "R_x": r["R_x"] == p["R_x"],
            "pi": r["pi"] == p["pi"],
            "a": r["a"] == p["a"],
            "Tr_a": r["Tr(a)"] == p["Tr_a"],
            "Tr_x": r["Tr(x_R)"] == p["Tr_x_R"],
            "m_Tr_a": r["m_Tr_a_mod2"] == p["m_Tr_a"],
            "count_vs_single": r["single_x_multiset"] == p["count"],
            "usable_is_zero": r["usable_point_multiset"] == 0,
        })
    pair_cmp["all_fields_agree"] = all(
        all(v is True for k, v in rec.items() if k != "key")
        for rec in pair_cmp["field_pair_agreements"]
    ) and pair_cmp["keys_equal"]

    # ---- reconstruction 12 boxes from source ----
    recon_rows = []
    boxes: dict[tuple, list] = {}
    for cfg in data["configurations"]:
        meta = parse_label(cfg["label"])
        if meta["n"] not in (20, 22, 24) or meta["t"] != 2:
            continue
        cell = f"n{meta['n']}-m{meta['m']}-t{meta['t']}-k{meta['k']}"
        key = (cell, meta["subspace"], meta["b_mode"])
        arr = np.array(cfg["columns"]["E"]["usable_point_multiset"], dtype=np.int64)
        boxes.setdefault(key, []).append(arr)
    for key, parts in sorted(boxes.items()):
        arr = np.concatenate(parts)
        s = summary(arr)
        printed = PRINTED.get(key)
        lam = (1 << (2 * int(key[0].split("k")[1]) - int(key[0][1:3]))) / 2.0
        # P_ratio = hit / eq11 P; t=2 so t! = 2, lambda_eq11 = 2^{2k-n}/2
        n = int(key[0][1:3]); k = int(key[0].split("k")[1])
        lam_eq11 = (1 << (2 * k - n)) / 2.0
        P_eq11 = 1.0 - math.exp(-lam_eq11)
        P_ratio = s["hit_fraction"] / P_eq11
        row = {
            "key": list(key),
            "n_targets": s["n"],
            "mean": s["mean"],
            "hit_fraction": s["hit_fraction"],
            "P_ratio": P_ratio,
            "f_dispersion": s["f_dispersion"],
            "var_over_mean": s["var_over_mean"],
            "printed": printed,
            "mean_match": printed and abs(s["mean"] - printed["mean"]) < 5.5e-5,
            "hit_match": printed and abs(s["hit_fraction"] - printed["hit_fraction"]) < 5.5e-5,
            "fdisp_match_4dp": printed and abs(round(s["f_dispersion"], 4)
                                               - printed["f_dispersion"]) < 5e-5,
        }
        recon_rows.append(row)

    # ---- per-configuration t=2 even-n, both subspaces ----
    per_cfg = []
    kf_events = []
    random_v_depleted = []
    # pool buckets for cells: (n, subspace, b_mode, side)
    pools: dict[tuple, dict] = {}

    t2_cfgs = []
    for cfg in data["configurations"]:
        meta = parse_label(cfg["label"])
        if meta["t"] != 2 or meta["n"] not in (20, 22, 24):
            continue
        t2_cfgs.append((meta, cfg))

    for meta, cfg in t2_cfgs:
        n, m_rel = meta["n"], meta["m"]
        mod = F.primary(n)
        altm = F.alt[n]
        for side in ("E", "T"):
            cols = cfg["columns"][side]
            xs = cols["R_x"]
            usable = np.array(cols["usable_point_multiset"], dtype=np.int64)
            a = F.a_of(n, side)
            tra = F.tr(n, a, mod)
            confined = (m_rel * tra) % 2
            traces = [F.tr(n, int(x), mod) for x in xs]
            pis = [(tr + tra) % 2 for tr in traces]
            by = split_counts(xs, usable, pis)
            reachable = by[confined]
            empty_cls = by[1 - confined]
            pooled_s = summary(usable)
            reach_s = summary(reachable)
            empty_s = summary(empty_cls)
            boot_reach = bootstrap_D_and_diff(reachable, rng)
            boot_pool = bootstrap_D_and_diff(usable, rng)
            mean0_ci = bootstrap_mean(reachable, rng)
            two_pool = (2.0 * pooled_s["mean"]) if pooled_s["mean"] is not None else None
            # bootstrap mean_reach / (2 * mean_pooled) from joint resample of all
            nobs = usable.size
            idx = rng.integers(0, nobs, size=(BOOT, nobs), dtype=np.int32)
            samp = usable[idx]
            pi_arr = np.array(pis, dtype=np.int8)
            pi_s = pi_arr[idx]
            reach_mask = pi_s == confined
            # mean of reachable entries per replicate
            reach_means = []
            ratios = []
            for b in range(BOOT):
                rmask = reach_mask[b]
                if not rmask.any():
                    continue
                rm = samp[b][rmask].mean()
                pm = samp[b].mean()
                reach_means.append(rm)
                if pm > 0:
                    ratios.append(rm / (2.0 * pm))
            ratio_ci = [float(np.percentile(ratios, 2.5)),
                        float(np.percentile(ratios, 97.5))] if ratios else None

            rec = {
                "label": meta["label"], "n": n, "m": m_rel, "t": 2, "k": meta["k"],
                "subspace": meta["subspace"], "b_mode": meta["b_mode"],
                "seed": meta["seed"], "side": side,
                "a": a, "Tr_a": tra, "m_Tr_a": confined,
                "reachable_pi": confined,
                "pooled": pooled_s,
                "reachable_class": reach_s,
                "empty_predicted_class": empty_s,
                "bootstrap_reachable_D": boot_reach,
                "bootstrap_pooled": boot_pool,
                "reachable_mean_ci95": mean0_ci,
                "two_times_pooled_mean": two_pool,
                "reachable_mean_over_2_pooled_ci95": ratio_ci,
                "ratio_ci_contains_1": bool(
                    ratio_ci and ratio_ci[0] <= 1.0 <= ratio_ci[1]),
                "reachable_D_ci_contains_1": boot_reach.get("D_ci_contains_1"),
                "pooled_D_minus_1plus_mean_contains_0":
                    boot_pool.get("D_minus_1_plus_mean_contains_0"),
            }
            per_cfg.append(rec)

            pk = (n, meta["subspace"], meta["b_mode"], side)
            bucket = pools.setdefault(pk, {
                "usable": [], "reach": [], "empty": [], "meta": {
                    "n": n, "subspace": meta["subspace"], "b_mode": meta["b_mode"],
                    "side": side, "reachable_pi": confined, "a": a, "Tr_a": tra,
                }})
            bucket["usable"].append(usable)
            bucket["reach"].append(reachable)
            bucket["empty"].append(empty_cls)

            # known-false: LSB and alt-mod, usable column
            bit = [int(x) & 1 for x in xs]
            bit_by = {0: [], 1: []}
            for b, c in zip(bit, usable.tolist()):
                bit_by[b].append(c)
            alt_tr = [F.tr(n, int(x), altm) for x in xs]
            alt_by = {0: [], 1: []}
            for tr, c in zip(alt_tr, usable.tolist()):
                alt_by[tr].append(c)
            kf = {
                "label": meta["label"], "side": side, "subspace": meta["subspace"],
                "lsb": {str(k): summary(np.array(v, dtype=np.int64))
                        for k, v in bit_by.items()},
                "lsb_empty": (len(bit_by[0]) == 0 or len(bit_by[1]) == 0
                              or summary(np.array(bit_by[0], dtype=np.int64))["empty"]
                              or summary(np.array(bit_by[1], dtype=np.int64))["empty"]),
                "lsb_class_empty_population": len(bit_by[0]) == 0 or len(bit_by[1]) == 0,
                "alt_modulus": altm,
                "primary_modulus": mod,
                "alt": {str(k): summary(np.array(v, dtype=np.int64))
                        for k, v in alt_by.items()},
                "alt_class_empty_population": len(alt_by[0]) == 0 or len(alt_by[1]) == 0,
            }
            # "empty class" for known-false: a split class with zero TARGETS
            # (the invalidation rule) OR with zero hits while the other is populated.
            # Contract: "An empty class under either split means the analysis code
            # is producing the effect". Producer used len(class)==0.
            kf["lsb_empty_class_as_producer"] = kf["lsb_class_empty_population"]
            kf["alt_empty_class_as_producer"] = kf["alt_class_empty_population"]
            kf["lsb_zero_hits_in_a_populated_class"] = any(
                summary(np.array(v, dtype=np.int64))["empty"] and len(v) > 0
                for v in bit_by.values())
            kf["alt_zero_hits_in_a_populated_class"] = any(
                summary(np.array(v, dtype=np.int64))["empty"] and len(v) > 0
                for v in alt_by.values())
            kf_events.append(kf)

            if meta["subspace"] == "random_k_dimensional":
                # proves-too-much: no empty or depleted pi class
                m0, m1 = by[0], by[1]
                s0, s1 = summary(m0), summary(m1)
                depleted = False
                reason = None
                if s0["n"] == 0 or s1["n"] == 0:
                    depleted = True
                    reason = "empty_population"
                elif s0["empty"] or s1["empty"]:
                    depleted = True
                    reason = "zero_hits_in_a_class"
                elif s0["mean"] and s1["mean"]:
                    ratio = min(s0["mean"], s1["mean"]) / max(s0["mean"], s1["mean"])
                    # "depleted" if one class mean is < 1/4 of the other (far from equal)
                    if ratio < 0.25:
                        depleted = True
                        reason = f"mean_ratio {ratio}"
                if depleted:
                    random_v_depleted.append({
                        "label": meta["label"], "side": side, "reason": reason,
                        "pi0": s0, "pi1": s1,
                    })

    # ---- cell-level pools (5 seeds concatenated) ----
    cell_rows = []
    for pk, bucket in sorted(pools.items()):
        usable = np.concatenate(bucket["usable"])
        reach = np.concatenate(bucket["reach"])
        empty = np.concatenate(bucket["empty"])
        pooled_s = summary(usable)
        reach_s = summary(reach)
        empty_s = summary(empty)
        boot_reach = bootstrap_D_and_diff(reach, rng)
        boot_pool = bootstrap_D_and_diff(usable, rng)
        nobs = usable.size
        # reachable / (2 pooled)
        # rebuild pi via lengths of concatenated pieces is messy; bootstrap
        # from the concatenated reachable vs pooled means using a two-sample
        # resample of the already-split arrays.
        idx_r = rng.integers(0, reach.size, size=(BOOT, reach.size), dtype=np.int32)
        idx_p = rng.integers(0, nobs, size=(BOOT, nobs), dtype=np.int32)
        rm = reach[idx_r].mean(axis=1)
        pm = usable[idx_p].mean(axis=1)
        ratios = rm / (2.0 * pm) if False else (rm / (2.0 * pm))
        # pm from pooled resample independent of reach is conservative
        ratios = rm / (2.0 * pm)
        ratio_ci = [float(np.percentile(ratios, 2.5)),
                    float(np.percentile(ratios, 97.5))]
        two_pool = 2.0 * pooled_s["mean"]
        cell_rows.append({
            "n": bucket["meta"]["n"],
            "subspace": bucket["meta"]["subspace"],
            "b_mode": bucket["meta"]["b_mode"],
            "side": bucket["meta"]["side"],
            "a": bucket["meta"]["a"],
            "Tr_a": bucket["meta"]["Tr_a"],
            "reachable_pi": bucket["meta"]["reachable_pi"],
            "pooled": pooled_s,
            "reachable": reach_s,
            "empty_predicted": empty_s,
            "two_times_pooled_mean": two_pool,
            "reachable_minus_2pooled": reach_s["mean"] - two_pool,
            "bootstrap_reachable_D": boot_reach,
            "bootstrap_pooled": boot_pool,
            "reachable_mean_over_2_pooled_ci95": ratio_ci,
            "ratio_ci_contains_1": bool(ratio_ci[0] <= 1.0 <= ratio_ci[1]),
            "reachable_D_ci_contains_1": boot_reach.get("D_ci_contains_1"),
            "pooled_D_minus_1plus_mean_contains_0":
                boot_pool.get("D_minus_1_plus_mean_contains_0"),
            "one_plus_lambda": 1.0 + pooled_s["mean"],
            "pooled_D": pooled_s["var_over_mean"],
        })

    # ---- odd-n ----
    odd_rows = []
    odd_enum = {
        "n_configurations": len(odd.get("configurations") or []),
        "kind": odd.get("kind"),
        "run_id": odd.get("run_id"),
        "expected_labels": [],
        "V_to_the_t_from_k": {},
        "targets_per_side": {},
        "sampled_inside_V_evidence": "absent: no sample-size field; 2000 R draws as declared; t=2 lookup enumerates all factor-base pairs",
    }
    for cfg in odd["configurations"]:
        meta = parse_label(cfg["label"])
        n, k, t = meta["n"], meta["k"], meta["t"]
        needed = (1 << k) ** t
        odd_enum["V_to_the_t_from_k"][cfg["label"]] = needed
        odd_enum["targets_per_side"][cfg["label"]] = {
            side: len(cols["R_x"]) for side, cols in cfg["columns"].items()
        }
        mod = F.primary(n)
        for side in ("E", "T"):
            cols = cfg["columns"][side]
            usable = np.array(cols["usable_point_multiset"], dtype=np.int64)
            xs = cols["R_x"]
            a = F.a_of(n, side)
            tra = F.tr(n, a, mod)
            traces = [F.tr(n, int(x), mod) for x in xs]
            pis = [(tr + tra) % 2 for tr in traces]
            by = split_counts(xs, usable, pis)
            odd_rows.append({
                "label": cfg["label"], "side": side, "n": n, "k": k,
                "a": a, "Tr_a": tra, "Tr(1)": F.tr(n, 1, mod),
                "pooled": summary(usable),
                "pi0": summary(by[0]),
                "pi1": summary(by[1]),
                "needed_V_to_the_t": needed,
                "n_targets": len(xs),
            })

    # ---- artifact hashes ----
    digest_path = os.path.join(
        REPO,
        "experiments/EXP-SEMBIN-911efe/runs/RUN-SEMBIN-8be036/artifact-digests.json",
    )
    declared = json.load(open(digest_path))
    run_dir = os.path.join(
        REPO, "experiments/EXP-SEMBIN-911efe/runs/RUN-SEMBIN-8be036"
    )
    hash_checks = []
    for rel, spec in declared["outputs"].items():
        path = os.path.join(run_dir, rel)
        if not os.path.isfile(path):
            hash_checks.append({"path": rel, "present": False})
            continue
        got = sha256_file(path)
        hash_checks.append({
            "path": rel, "present": True,
            "declared": spec["sha256"], "got": got,
            "match": got == spec["sha256"],
            "bytes": os.path.getsize(path),
        })

    # summary flags for K2
    t2_low_E = [r for r in cell_rows
                if r["subspace"] == "low_degree_polynomial"
                and r["side"] == "E"]
    t2_rand_E = [r for r in cell_rows
                 if r["subspace"] == "random_k_dimensional"
                 and r["side"] == "E"]

    reach_D_excl_1 = [r for r in t2_low_E if r["reachable_D_ci_contains_1"] is False]
    pool_diff_excl_0 = [r for r in t2_low_E
                        if r["pooled_D_minus_1plus_mean_contains_0"] is False]
    # same direction: all D > 1+lambda or all below
    signs = []
    for r in t2_low_E:
        if r["pooled_D"] is not None:
            signs.append(1 if r["pooled_D"] > r["one_plus_lambda"] else -1)
    all_same_dir_and_outside = (
        len(pool_diff_excl_0) == len(t2_low_E) and len(set(signs)) == 1
        if t2_low_E else False
    )

    per_cfg_low_E = [r for r in per_cfg
                      if r["subspace"] == "low_degree_polynomial"
                      and r["side"] == "E"]
    per_cfg_D_excl = [r["label"] for r in per_cfg_low_E
                       if r["reachable_D_ci_contains_1"] is False]

    kf_lsb_empty = [e["label"] for e in kf_events if e["lsb_empty_class_as_producer"]]
    kf_alt_empty = [e["label"] for e in kf_events if e["alt_empty_class_as_producer"]]

    odd_E = [r for r in odd_rows if r["side"] == "E"]
    odd_fdisp = [(r["label"], r["pooled"]["f_dispersion"]) for r in odd_E]
    odd_both_pi_hit = all(
        (not r["pi0"]["empty"]) and (not r["pi1"]["empty"]) for r in odd_E
    )

    out = {
        "elapsed_seconds": time.time() - t0,
        "bootstrap_replicates": BOOT,
        "bootstrap_seed": BOOT_SEED,
        "K1_pair_comparison": pair_cmp,
        "fields": {
            str(n): {
                "modulus": F.mod[n], "modulus_hex": hex(F.mod[n]),
                "delta": F.delta[n], "alt_modulus": F.alt[n],
                "Tr_a_E": F.tr(n, 0), "Tr_a_T": F.tr(n, F.delta[n]),
            } for n in sorted(F.mod)
        },
        "reconstruction_12_boxes": recon_rows,
        "reconstruction_all_printed_match": all(
            r["mean_match"] and r["hit_match"] and r["fdisp_match_4dp"]
            for r in recon_rows if r["printed"]
        ),
        "per_configuration": per_cfg,
        "cell_pooled_5_seeds": cell_rows,
        "known_false_events": [
            {k: v for k, v in e.items() if k in (
                "label", "side", "subspace", "lsb_empty_class_as_producer",
                "alt_empty_class_as_producer", "alt_modulus", "primary_modulus",
                "lsb_zero_hits_in_a_populated_class",
                "alt_zero_hits_in_a_populated_class",
                "lsb", "alt",
            )} for e in kf_events
        ],
        "known_false_lsb_empty_class_any": kf_lsb_empty,
        "known_false_alt_empty_class_any": kf_alt_empty,
        "random_V_depleted": random_v_depleted,
        "odd_n_enum": odd_enum,
        "odd_n_rows": odd_rows,
        "k2_flags": {
            "t2_low_E_n_cells": len(t2_low_E),
            "reachable_D_ci_excludes_1_at_cell": [
                {"n": r["n"], "b_mode": r["b_mode"],
                 "D": r["reachable"]["var_over_mean"],
                 "ci": r["bootstrap_reachable_D"].get("D_ci95")}
                for r in reach_D_excl_1
            ],
            "pooled_D_minus_1plus_lambda_excludes_0_at_cell": [
                {"n": r["n"], "b_mode": r["b_mode"],
                 "D": r["pooled_D"], "one_plus_lambda": r["one_plus_lambda"],
                 "ci_diff": r["bootstrap_pooled"].get("D_minus_1_plus_mean_ci95")}
                for r in pool_diff_excl_0
            ],
            "all_three_n_same_direction_outside": all_same_dir_and_outside,
            "per_config_reachable_D_ci_excludes_1": per_cfg_D_excl,
            "random_V_depleted_count": len(random_v_depleted),
            "kf_lsb_empty": kf_lsb_empty,
            "kf_alt_empty": kf_alt_empty,
            "odd_n_both_pi_hit_on_E": odd_both_pi_hit,
            "odd_n_f_dispersion_E": odd_fdisp,
            "odd_n_n_targets_all_2000": all(
                v.get("E") == 2000 and v.get("T") == 2000
                for v in odd_enum["targets_per_side"].values()
            ),
            "odd_n_V2": odd_enum["V_to_the_t_from_k"],
        },
        "producer_known_false_empty_class": producer_parity.get("known_false_empty_class"),
        "hash_checks": hash_checks,
        "hash_all_match": all(h.get("match") for h in hash_checks if h.get("present")),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True, default=str)
        fh.write("\n")
    print("wrote", OUT)
    print("keys_equal", pair_cmp["keys_equal"], "fields", pair_cmp["all_fields_agree"])
    print("recon", out["reconstruction_all_printed_match"])
    print("reach_D_excl_1", out["k2_flags"]["reachable_D_ci_excludes_1_at_cell"])
    print("pool_diff", out["k2_flags"]["pooled_D_minus_1plus_lambda_excludes_0_at_cell"])
    print("per_cfg_D_excl", per_cfg_D_excl)
    print("random_V_depleted", len(random_v_depleted))
    print("kf_lsb_empty", kf_lsb_empty, "kf_alt_empty", kf_alt_empty)
    print("odd_both_hit", odd_both_pi_hit, "odd_fdisp", odd_fdisp)
    print("hashes", out["hash_all_match"], "elapsed", out["elapsed_seconds"])
    # compact cell table
    print("\nCELL TABLE E usable")
    print(f"{'n':>3} {'sub':<22} {'B':<10} {'D_reach':>8} {'ciL':>8} {'ciH':>8} "
          f"{'D_pool':>8} {'1+l':>8} {'ratio':>8} {'pi1_nz':>8}")
    for r in cell_rows:
        if r["side"] != "E":
            continue
        ci = r["bootstrap_reachable_D"].get("D_ci95") or [None, None]
        print(f"{r['n']:3d} {r['subspace']:<22} {r['b_mode']:<10} "
              f"{r['reachable']['var_over_mean']:8.4f} {ci[0]:8.4f} {ci[1]:8.4f} "
              f"{r['pooled_D']:8.4f} {r['one_plus_lambda']:8.4f} "
              f"{(r['reachable']['mean']/r['two_times_pooled_mean'] if r['two_times_pooled_mean'] else float('nan')):8.4f} "
              f"{r['empty_predicted']['n_nonzero']:8d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
