"""EXP-FB3-001 battery driver: one run per size (2^14, 2^16, 2^18).

Executes the six pre-registered geometry cells, the shared permutation null,
the typed nulls, the greedy train/held-out arm, the asymmetric ladder, and the
exploratory (non-family) arms, with exact whole-target-space counting.

Usage:  python3 run_battery.py --bits 14 --out <raw-result.json>

Observations only.  Discrete logs are known by construction FOR MEASUREMENT
ONLY; nothing here is a step of an attack and no cost claim is derived.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import resource
import sys
import time
from datetime import datetime, timezone

import numpy as np

import fb3_core as C

GEOMETRIES = ["high_bit_interval", "small_height", "mixed_two_base",
              "coset_union", "greedy_optimized", "asymmetric_sizing"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def peak_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def jsonable(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"not JSON serialisable: {type(obj)}")


class Auditor:
    """Hard control: exact total must equal the closed form for the cell's typing.

    Also cross-checks the primary integer counter against the direct multiset
    enumeration and the FFT route on an audited subset.
    """

    def __init__(self, audit_limit: int = 5):
        self.total_checks = 0
        self.total_failures: list[dict] = []
        self.cross_checks = 0
        self.cross_failures: list[dict] = []
        self.fft_checks = 0
        self.fft_failures: list[dict] = []
        self.max_fft_round_err = 0.0
        self.audit_limit = audit_limit
        self._audited: dict[str, int] = {}

    def check_total(self, label: str, counts: np.ndarray, expected: int) -> bool:
        self.total_checks += 1
        got = int(counts.sum())
        ok = got == int(expected)
        if not ok:
            self.total_failures.append({"label": label, "got": got,
                                        "expected": int(expected)})
        return ok

    def cross_check(self, label: str, n_order: int, logs, counts: np.ndarray,
                    force: bool = False) -> None:
        """Independent recount of an untyped cell (direct enumeration + FFT)."""
        seen = self._audited.get(label, 0)
        if not force and seen >= self.audit_limit:
            return
        self._audited[label] = seen + 1
        direct = C.counts_untyped_m3_direct(n_order, logs)
        self.cross_checks += 1
        if not np.array_equal(direct, counts):
            self.cross_failures.append({"label": label,
                                        "n_disagree": int(np.count_nonzero(direct != counts))})
        fft, err = C.counts_untyped_m3_fft(n_order, logs)
        self.fft_checks += 1
        self.max_fft_round_err = max(self.max_fft_round_err, err)
        if not np.array_equal(fft, counts):
            self.fft_failures.append({"label": label, "round_err": err,
                                      "n_disagree": int(np.count_nonzero(fft != counts))})

    def report(self) -> dict:
        return {
            "closed_form_total_checks": self.total_checks,
            "closed_form_total_failures": self.total_failures,
            "closed_form_total_control": "pass" if not self.total_failures else "FAIL",
            "independent_recount_checks": self.cross_checks,
            "independent_recount_failures": self.cross_failures,
            "independent_recount_control": "pass" if not self.cross_failures else "FAIL",
            "fft_route_checks": self.fft_checks,
            "fft_route_failures": self.fft_failures,
            "fft_max_abs_rounding_deviation": self.max_fft_round_err,
            "fft_rounding_safe": self.max_fft_round_err < 0.25,
            "fft_route_control": "pass" if not self.fft_failures else "FAIL",
            "audit_note": ("every cell (structured, null, exploratory) is total-"
                           "checked; the independent recount and FFT route are "
                           "run on all structured cells and the first "
                           f"{self.audit_limit} null draws of each label"),
        }


def ratios(cell: dict, null_stats: list[dict]) -> dict:
    out = {}
    for key in C.STAT_KEYS:
        nulls = np.array([s[key] for s in null_stats], dtype=np.float64)
        nm = float(nulls.mean())
        out[key] = {
            "cell": cell[key],
            "null_mean": nm,
            "ratio": (cell[key] / nm) if nm != 0 else None,
            "null_ratio_band_95": [float(np.percentile(nulls / nm, 2.5)),
                                   float(np.percentile(nulls / nm, 97.5))] if nm else None,
        }
        two = C.empirical_p(cell[key], nulls, two_sided=True)
        one_lo = C.empirical_p(cell[key], nulls, two_sided=False, direction="less")
        one_hi = C.empirical_p(cell[key], nulls, two_sided=False, direction="greater")
        out[key]["p_two_sided"] = two["p"]
        out[key]["p_two_sided_h016_convention"] = C.empirical_p_h016(cell[key], nulls)
        out[key]["p_one_sided_null_below_cell"] = one_hi["p"]
        out[key]["p_one_sided_null_above_cell"] = one_lo["p"]
        out[key]["null_detail"] = two
        out[key]["direction"] = ("above_null" if cell[key] > nm else
                                 "below_null" if cell[key] < nm else "equal_to_null")
    return out


def build_curves(bits: int, n_targets: int, log, n_curves: int = 4) -> list[C.Curve]:
    curves = []
    for idx in range(1, n_curves + 1):
        t0 = time.time()
        cv = C.find_curve(bits, idx, n_targets)
        log(f"  curve {idx}: p={cv.p} a={cv.a} b={cv.b} N={cv.n_order} "
            f"tries={cv.tries} checks_ok={cv.checks['all_ok']} "
            f"({time.time() - t0:.1f}s)")
        if not cv.checks["all_ok"]:
            raise RuntimeError(f"curve verification failed for curve {idx}")
        curves.append(cv)
    return curves


def curve_record(cv: C.Curve) -> dict:
    ck = dict(cv.checks)
    return {
        "curve_index": cv.curve_index, "seed": cv.seed, "p": cv.p, "a": cv.a,
        "b": cv.b, "N": cv.n_order, "curve_tries": cv.tries,
        "rejects_non_prime_or_singular_order": cv.order_rejects,
        "rejects_outside_size_window": cv.window_rejects,
        "G": [cv.gx, cv.gy], "verification": ck,
        "order_method": "exact character sum #E = p+1+sum_x legendre(x^3+ax+b,p)",
        "order_independent_check": ("N prime, N in Hasse interval, N*G = O by "
                                    "double-and-add, multiple table closes at N, "
                                    "dlog table is a bijection onto the group"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bits", type=int, required=True, choices=[14, 16, 18])
    ap.add_argument("--out", required=True)
    ap.add_argument("--null-draws", type=int, default=C.FROZEN["null_draws"])
    ap.add_argument("--curves", type=int, default=4,
                    help="timing probe only; the recorded runs use 4")
    ap.add_argument("--seeds", type=int, default=4,
                    help="timing probe only; the recorded runs use 4")
    args = ap.parse_args()
    if args.null_draws < 100:
        print(f"WARNING: null_draws={args.null_draws} is below the frozen "
              f"minimum of 100 (timing probe only)", file=sys.stderr)

    started = now_iso()
    t_start = time.time()
    lines: list[str] = []

    def log(msg: str) -> None:
        print(msg, flush=True)
        lines.append(msg)

    bits = args.bits
    n_target = 1 << bits
    audit = Auditor()
    log(f"=== EXP-FB3-001 battery, size 2^{bits} (N_target={n_target}) ===")
    log(f"started_at {started}")
    log(f"frozen: m={C.FROZEN['m']} matched_size={C.FROZEN['matched_size_rule']} "
        f"null_draws={args.null_draws}")
    log("counting: exact integer counts over ALL N targets (no sampling); "
        "discrete logs known by construction FOR MEASUREMENT ONLY")

    log("curve generation:")
    curves = build_curves(bits, n_target, log, args.curves)

    cells: list[dict] = []
    exploratory: list[dict] = []
    null_shared_records: list[dict] = []
    geometry_infeasible: list[dict] = []

    for cv in curves:
        n_order = cv.n_order
        b = C.matched_size(n_order)
        expected_untyped = C.total_untyped_m3(b)
        log(f"curve {cv.curve_index}: N={n_order} B={b} "
            f"exact_total=C(B+2,3)={expected_untyped} "
            f"exact_mean={expected_untyped / n_order:.6f}")

        # ---- deterministic (seed-independent) geometries, built once ---------
        det: dict[str, dict] = {}
        for name, fn in (("high_bit_interval", C.geom_high_bit_interval),
                         ("small_height", C.geom_small_height),
                         ("coset_union", C.geom_coset_union)):
            try:
                det[name] = fn(cv, b)
            except C.Infeasible as exc:
                geometry_infeasible.append({"geometry": name,
                                            "curve_index": cv.curve_index,
                                            "reason": str(exc)})
                log(f"  {name}: INFEASIBLE ({exc})")
        try:
            det["mixed_two_base"] = C.geom_mixed_two_base(cv, b)
        except C.Infeasible as exc:
            geometry_infeasible.append({"geometry": "mixed_two_base",
                                        "curve_index": cv.curve_index,
                                        "reason": str(exc)})
        det_counts: dict[str, np.ndarray] = {}
        for name in ("high_bit_interval", "small_height", "coset_union"):
            if name in det:
                cnt = C.counts_untyped_m3(n_order, det[name]["logs"])
                audit.check_total(f"{name}/c{cv.curve_index}", cnt, expected_untyped)
                audit.cross_check(f"structured/{name}", n_order, det[name]["logs"],
                                  cnt, force=True)
                det_counts[name] = cnt

        # mixed_two_base: both typings, counted exactly
        mixed_typed: dict[str, dict] = {}
        if "mixed_two_base" in det:
            l1, l2 = det["mixed_two_base"]["sub_bases"]
            b1, b2 = det["mixed_two_base"]["sizes"]
            mixed_typed["two_from_interval_one_from_small_mult"] = {
                "counts": C.counts_typed_1_2(n_order, l2, l1),
                "expected_total": b2 * b1 * (b1 + 1) // 2,
                "sizes": [b1, b2], "pattern": "pair from sub-base 1, single from sub-base 2",
            }
            mixed_typed["one_from_interval_two_from_small_mult"] = {
                "counts": C.counts_typed_1_2(n_order, l1, l2),
                "expected_total": b1 * b2 * (b2 + 1) // 2,
                "sizes": [b1, b2], "pattern": "single from sub-base 1, pair from sub-base 2",
            }
            for key, rec in mixed_typed.items():
                audit.check_total(f"mixed/{key}/c{cv.curve_index}", rec["counts"],
                                  rec["expected_total"])

        # exploratory prior-cell geometries (outside the pre-registered family)
        expl_geoms: dict[str, dict] = {}
        try:
            expl_geoms["small_multiples_H017"] = C.geom_small_multiples(cv, b)
        except C.Infeasible as exc:
            expl_geoms["small_multiples_H017"] = {"infeasible": str(exc)}
        try:
            expl_geoms["qr_walk_H016"] = C.geom_qr_walk(cv, b, seed=cv.seed + 991)
        except C.Infeasible as exc:
            expl_geoms["qr_walk_H016"] = {"infeasible": str(exc)}

        for seed in range(1, args.seeds + 1):
            cell_seed = (C.FROZEN["cell_seed_base"] + bits * 100000
                         + cv.curve_index * 1000 + seed)
            rng = np.random.default_rng(cell_seed)
            t_rep = time.time()

            # ---- greedy train/held-out split (frozen deterministic rule) -----
            train_mask, held_mask = C.greedy_split(n_order, cell_seed + 500000)
            train_bits = C.bits_from_indices(np.flatnonzero(train_mask), n_order)

            # ---- shared untyped permutation null -----------------------------
            null_all, null_held, null_train = [], [], []
            for j in range(args.null_draws):
                rb = C.random_base(n_order, b, rng)
                cnt = C.counts_untyped_m3(n_order, rb)
                audit.check_total("null_untyped", cnt, expected_untyped)
                audit.cross_check("null_untyped", n_order, rb, cnt)
                null_all.append(C.cell_stats(cnt))
                null_held.append(C.cell_stats(cnt, held_mask))
                null_train.append(C.cell_stats(cnt, train_mask))
            null_shared_records.append({
                "curve_index": cv.curve_index, "rep_seed": seed,
                "cell_seed": cell_seed, "B": b, "draws": args.null_draws,
                "shared_by": ["high_bit_interval", "small_height", "coset_union",
                              "greedy_optimized (held-out restricted)",
                              "mixed_two_base (total-size control)",
                              "asymmetric_sizing (total-size control)",
                              "exploratory untyped arms"],
                "shared": True,
                "convention": "B distinct uniform logs in [0,N) (H016 record)",
                "whole_group_mean_is_constant": bool(
                    len({s["sum_counts"] for s in null_all}) == 1),
                "null_mean_whole_group": float(np.mean([s["mean"] for s in null_all])),
                "null_coverage_mean": float(np.mean([s["coverage"] for s in null_all])),
                "null_coverage_band_95": [
                    float(np.percentile([s["coverage"] for s in null_all], 2.5)),
                    float(np.percentile([s["coverage"] for s in null_all], 97.5))],
            })

            def add_cell(geometry: str, domain: str, stats: dict, nulls: list[dict],
                         extra: dict, total_ok: bool, expected_total: int,
                         actual_total: int) -> None:
                rec = {
                    "geometry": geometry, "bits_target": bits, "N": n_order, "B": b,
                    "curve_index": cv.curve_index, "rep_seed": seed,
                    "cell_seed": cell_seed, "evaluation_domain": domain,
                    "terminal_state": "measured",
                    "exact_total": actual_total,
                    "closed_form_total": expected_total,
                    "closed_form_total_ok": bool(total_ok),
                    "stats": stats,
                    "null_source": "shared untyped matched-random set"
                                   if extra.get("null_shared", True)
                                   else "cell-specific matched-random set",
                    "metrics": ratios(stats, nulls),
                    "extra": extra,
                }
                cells.append(rec)

            # ---- pre-registered cells 1, 2, 4 (untyped, whole group) ---------
            for name in ("high_bit_interval", "small_height", "coset_union"):
                if name not in det:
                    cells.append({"geometry": name, "bits_target": bits,
                                  "N": n_order, "B": b,
                                  "curve_index": cv.curve_index, "rep_seed": seed,
                                  "terminal_state": "infeasible",
                                  "reason": next(r["reason"] for r in geometry_infeasible
                                                 if r["geometry"] == name
                                                 and r["curve_index"] == cv.curve_index)})
                    continue
                cnt = det_counts[name]
                add_cell(name, "whole_group", C.cell_stats(cnt), null_all,
                         {k: v for k, v in det[name].items() if k != "logs"}
                         | {"logs_are_seed_independent": True, "null_shared": True},
                         True, expected_untyped, int(cnt.sum()))

            # ---- pre-registered cell 3: mixed_two_base (typed) ---------------
            if mixed_typed:
                primary_key = "two_from_interval_one_from_small_mult"
                typed_nulls: dict[str, list[dict]] = {}
                for key, rec in mixed_typed.items():
                    b1, b2 = rec["sizes"]
                    nulls_same = []
                    for _ in range(args.null_draws):
                        s1, s2 = C.random_disjoint_sub_bases(n_order, [b1, b2], rng)
                        if key == primary_key:
                            cnt_n = C.counts_typed_1_2(n_order, s2, s1)
                        else:
                            cnt_n = C.counts_typed_1_2(n_order, s1, s2)
                        audit.check_total(f"null_mixed/{key}", cnt_n,
                                          rec["expected_total"])
                        nulls_same.append(C.cell_stats(cnt_n))
                    typed_nulls[key] = nulls_same
                for key, rec in mixed_typed.items():
                    st = C.cell_stats(rec["counts"])
                    extra = {
                        "typing": key, "pattern": rec["pattern"],
                        "sub_base_sizes": rec["sizes"],
                        "sub_base_overlap": det["mixed_two_base"]["overlap"],
                        "sub_base_1": det["mixed_two_base"]["sub_base_1"],
                        "sub_base_2": det["mixed_two_base"]["sub_base_2"],
                        "is_primary_typing": key == primary_key,
                        "typed_total_vs_untyped_total": rec["expected_total"] / expected_untyped,
                        "same_typing_control": ratios(st, typed_nulls[key]),
                        "null_shared": True,
                        "family_control": C.FROZEN["typed_family_control"],
                        "logs_are_seed_independent": True,
                    }
                    name = ("mixed_two_base" if key == primary_key
                            else "mixed_two_base__secondary_typing")
                    add_cell(name, "whole_group", st, null_all, extra, True,
                             rec["expected_total"], int(rec["counts"].sum()))

            # ---- pre-registered cell 5: greedy_optimized --------------------
            pool = C.distinct_logs(rng, n_order, C.FROZEN["greedy_pool_factor"] * b)
            t_g = time.time()
            gsel = C.greedy_select(n_order, pool, train_bits, b)
            g_secs = time.time() - t_g
            gcnt = C.counts_untyped_m3(n_order, gsel["logs"])
            audit.check_total(f"greedy/c{cv.curve_index}s{seed}", gcnt, expected_untyped)
            audit.cross_check("structured/greedy", n_order, gsel["logs"], gcnt,
                              force=True)
            st_held = C.cell_stats(gcnt, held_mask)
            st_train = C.cell_stats(gcnt, train_mask)
            add_cell("greedy_optimized", "held_out_half", st_held, null_held, {
                "pool_size": gsel["pool_size"],
                "sigma3_size_at_stop": gsel["sigma3_size_at_stop"],
                "train_targets_covered_at_stop": gsel["train_targets_covered_at_stop"],
                "n_train_targets": int(train_mask.sum()),
                "n_held_out_targets": int(held_mask.sum()),
                "split_rule": C.FROZEN["greedy_split_rule"],
                "split_seed": cell_seed + 500000,
                "leakage_guard": ("greedy_select() receives only the training "
                                  "bitset; the held-out mask is not in scope "
                                  "during selection"),
                "train_stats": st_train,
                "train_metrics": ratios(st_train, null_train),
                "transfer_gap_coverage": st_train["coverage"] - st_held["coverage"],
                "transfer_gap_mean": st_train["mean"] - st_held["mean"],
                "selection_seconds": g_secs,
                "marginal_gain_first5": gsel["marginal_gains"][:5],
                "marginal_gain_last5": gsel["marginal_gains"][-5:],
                "null_shared": True,
                "honesty_note": ("base SELECTION consumes the full discrete-log "
                                 "table, so this construction is not available "
                                 "to an attacker; it is a measurement of what "
                                 "an oracle-aided base could achieve"),
            }, True, expected_untyped, int(gcnt.sum()))

            # ---- pre-registered cell 6: asymmetric_sizing (typed ladder) -----
            ladder = []
            primary_w = C.FROZEN["asym_primary_split_weights"]
            for w in C.FROZEN["asym_ladder_weights"]:
                b1, b2, b3 = C.asym_split_sizes(b, w)
                subs = C.random_disjoint_sub_bases(n_order, [b1, b2, b3], rng)
                cnt = C.counts_typed_111(n_order, *subs)
                exp_tot = b1 * b2 * b3
                ok = audit.check_total(f"asym/{w}/c{cv.curve_index}s{seed}", cnt, exp_tot)
                nulls_same = []
                for _ in range(args.null_draws):
                    s = C.random_disjoint_sub_bases(n_order, [b1, b2, b3], rng)
                    cn = C.counts_typed_111(n_order, *s)
                    audit.check_total(f"null_asym/{w}", cn, exp_tot)
                    nulls_same.append(C.cell_stats(cn))
                st = C.cell_stats(cnt)
                ladder.append({
                    "weights": w, "sizes": [b1, b2, b3], "expected_total": exp_tot,
                    "total_ok": ok, "stats": st,
                    "typed_total_vs_untyped_total": exp_tot / expected_untyped,
                    "decomposition_probability_exact": st["coverage"],
                    "mean_per_target_exact": st["mean"],
                    "same_split_control": ratios(st, nulls_same),
                    "is_primary_split": w == primary_w,
                })
            prim = next(item for item in ladder if item["is_primary_split"])
            add_cell("asymmetric_sizing", "whole_group", prim["stats"], null_all, {
                "primary_split_weights": primary_w,
                "primary_split_sizes": prim["sizes"],
                "ladder": ladder,
                "element_choice": C.FROZEN["asym_element_choice"],
                "family_control": C.FROZEN["typed_family_control"],
                "same_split_control": prim["same_split_control"],
                "typed_total_vs_untyped_total": prim["typed_total_vs_untyped_total"],
                "null_shared": True,
            }, prim["total_ok"], prim["expected_total"],
                int(prim["stats"]["sum_counts"]))

            # ---- exploratory arms (NOT in the pre-registered family) ---------
            for name, geo in expl_geoms.items():
                if "logs" not in geo:
                    exploratory.append({"arm": name, "curve_index": cv.curve_index,
                                        "rep_seed": seed, "state": "infeasible",
                                        "reason": geo["infeasible"]})
                    continue
                cnt = C.counts_untyped_m3(n_order, geo["logs"])
                audit.check_total(f"expl/{name}", cnt, expected_untyped)
                audit.cross_check(f"expl/{name}", n_order, geo["logs"], cnt)
                st = C.cell_stats(cnt)
                exploratory.append({
                    "arm": name, "kind": "exact recomputation of a prior-cell "
                                         "geometry (replication section only)",
                    "bits_target": bits, "N": n_order, "B": b,
                    "curve_index": cv.curve_index, "rep_seed": seed,
                    "state": "measured", "stats": st,
                    "exact_total": int(cnt.sum()),
                    "closed_form_total": expected_untyped,
                    "metrics": ratios(st, null_all),
                    "detail": {k: v for k, v in geo.items() if k != "logs"},
                })

            # symmetric-convention exploratory arm: D union -D at the same B
            for name in ("high_bit_interval", "small_height", "coset_union"):
                if name not in det:
                    continue
                logs = det[name]["logs"]
                sym = np.unique(np.concatenate([logs, (n_order - logs) % n_order]))
                cnt = C.counts_untyped_m3(n_order, sym)
                exp_tot = C.total_untyped_m3(int(sym.size))
                ok = audit.check_total(f"sym/{name}", cnt, exp_tot)
                exploratory.append({
                    "arm": f"symmetric_convention/{name}",
                    "kind": "secondary exploratory arm: convention D union -D",
                    "bits_target": bits, "N": n_order, "B": b,
                    "effective_base_size": int(sym.size),
                    "self_negation_collisions": int(2 * logs.size - sym.size),
                    "curve_index": cv.curve_index, "rep_seed": seed,
                    "state": "measured", "stats": C.cell_stats(cnt),
                    "exact_total": int(cnt.sum()), "closed_form_total": exp_tot,
                    "closed_form_total_ok": ok,
                    "identity_holds_with_effective_size": ok,
                })
            sym_rand_logs = C.random_base(n_order, b, rng)
            sym_rand = np.unique(np.concatenate([sym_rand_logs,
                                                 (n_order - sym_rand_logs) % n_order]))
            cnt = C.counts_untyped_m3(n_order, sym_rand)
            exp_tot = C.total_untyped_m3(int(sym_rand.size))
            ok = audit.check_total("sym/random", cnt, exp_tot)
            exploratory.append({
                "arm": "symmetric_convention/matched_random",
                "kind": "secondary exploratory arm: convention D union -D",
                "bits_target": bits, "N": n_order, "B": b,
                "effective_base_size": int(sym_rand.size),
                "curve_index": cv.curve_index, "rep_seed": seed,
                "state": "measured", "stats": C.cell_stats(cnt),
                "exact_total": int(cnt.sum()), "closed_form_total": exp_tot,
                "closed_form_total_ok": ok,
                "identity_holds_with_effective_size": ok,
            })

            log(f"  curve {cv.curve_index} seed {seed}: "
                f"{time.time() - t_rep:.1f}s (greedy {g_secs:.1f}s) "
                f"peak_rss={peak_mb():.0f}MB")

    # ------------------------------------------------------------------
    # Per-size summary (observations only).
    # ------------------------------------------------------------------
    summary: dict[str, dict] = {}
    for geometry in sorted({c["geometry"] for c in cells}):
        sub = [c for c in cells if c["geometry"] == geometry
               and c["terminal_state"] == "measured"]
        if not sub:
            summary[geometry] = {"terminal_state": "infeasible_or_absent",
                                 "n_cells": 0}
            continue
        entry = {"n_cells": len(sub), "terminal_state": "measured",
                 "evaluation_domain": sub[0]["evaluation_domain"]}
        for key in C.STAT_KEYS:
            vals = np.array([c["metrics"][key]["ratio"] for c in sub], dtype=np.float64)
            raw = np.array([c["stats"][key] for c in sub], dtype=np.float64)
            ps = np.array([c["metrics"][key]["p_two_sided"] for c in sub])
            entry[key] = {
                "exact_mean_over_replicates": float(raw.mean()),
                "ratio_mean": float(vals.mean()),
                "ratio_min": float(vals.min()), "ratio_max": float(vals.max()),
                "ratio_sd": float(vals.std(ddof=1)) if vals.size > 1 else 0.0,
                "p_two_sided_mean": float(ps.mean()),
                "p_two_sided_min": float(ps.min()),
            }
        summary[geometry] = entry
        log(f"  {geometry:36s} mean_ratio={entry['mean']['ratio_mean']:.6f} "
            f"cov_ratio={entry['coverage']['ratio_mean']:.6f} "
            f"conc_ratio={entry['concentration']['ratio_mean']:.6f} "
            f"min_p={entry['mean']['p_two_sided_min']:.3f}")

    wall = time.time() - t_start
    out = {
        "run_id": f"RUN-FB3-001-N{bits}",
        "experiment_id": "EXP-FB3-001",
        "amendment_id": "EXP-FB3-001-AMD-001",
        "purpose": f"exact factor-base geometry battery at N ~ 2^{bits}",
        "size": {"bits_target": bits, "N_target": n_target},
        "frozen_constants": C.FROZEN,
        "counting_convention": {
            "m": 3,
            "decomposition": "multiset {i<=j<=k} of base elements with sum = r",
            "target_space": "ALL N group elements (exact count, no sampling)",
            "matched_random": "B distinct uniform logs in [0,N) (H016 record)",
            "dlog_availability": "known by construction FOR MEASUREMENT ONLY; no "
                                 "cost, speedup, or attack claim is derived",
        },
        "curves": [curve_record(cv) for cv in curves],
        "cells": cells,
        "exploratory": exploratory,
        "shared_null_records": null_shared_records,
        "geometry_infeasible": geometry_infeasible,
        "controls": audit.report(),
        "summary_per_geometry": summary,
        "timing": {"started_at": started, "finished_at": now_iso(),
                   "wall_clock_seconds": wall},
        "peak_memory_mb": peak_mb(),
        "environment": {"python": platform.python_version(),
                        "numpy": np.__version__, "platform": platform.platform()},
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1, default=jsonable, sort_keys=False)
    log(f"wrote {args.out}")
    log(f"controls: {json.dumps({k: v for k, v in audit.report().items() if 'control' in k or 'fft_max' in k})}")
    log(f"wall_clock_seconds {wall:.1f} peak_memory_mb {peak_mb():.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
