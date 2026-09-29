#!/usr/bin/env python3
"""K1 first pass: independent N1 from RUN-SEMBIN-1b9afe per-R-counts.

SEQUENCING: this script reads ONLY
  experiments/EXP-SEMBIN-354a75/code/binary_field.py (modulus_for)
  experiments/EXP-SEMBIN-354a75/runs/RUN-SEMBIN-1b9afe/per-R-counts.json
It does not import or open anything under experiments/EXP-SEMBIN-911efe/.

Trace is this file's own loop. Squaring/reduction copies the source field
arithmetic so the identification of integers with field elements is the
run's modulus_for(n). Twist a' is the source construction: smallest delta
with Tr(delta)=1, a_E = 0, a_T = 0 xor delta.

pi(R) = Tr(x_R) + Tr(a)  (mod 2)
empty class: pi != m * Tr(a)  (mod 2)

(i)  nonzero in single_x_multiset or chained_x_multiset
(ii) usable_point_multiset only
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

REPO = os.environ.get("REPO", "/workspace")
sys.path.insert(0, os.path.join(REPO, "experiments/EXP-SEMBIN-354a75/code"))

from binary_field import modulus_for  # SOURCE run's field polynomial search

LABEL_RE = re.compile(
    r"^n(\d+)-m(\d+)-t(\d+)-k(\d+)"
    r"-(low_degree_polynomial|random_k_dimensional)"
    r"-(B_eq_1|random_B)-s(\d+)$"
)

PER_R = os.path.join(
    REPO, "experiments/EXP-SEMBIN-354a75/runs/RUN-SEMBIN-1b9afe/per-R-counts.json"
)
OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "k1_n1_pass1.json"
)


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
    """Absolute trace F_{2^n} -> F_2: sum_{i=0}^{n-1} a^{2^i}."""
    t, x = 0, a
    for _ in range(n):
        t ^= x
        x = reduce_poly(clmul(x, x), modulus, n)
    if t not in (0, 1):
        raise ArithmeticError(f"trace left F_2: {t} for a={a} n={n}")
    return t


def parse_label(label: str) -> dict:
    m = LABEL_RE.match(label)
    if not m:
        raise ValueError(f"unparseable label: {label}")
    n, mm, t, k, subspace, b_mode, seed = m.groups()
    return {
        "label": label,
        "n": int(n),
        "m": int(mm),
        "t": int(t),
        "k": int(k),
        "subspace": subspace,
        "b_mode": b_mode,
        "seed": int(seed),
    }


def twist_delta(n: int, modulus: int) -> int:
    """Smallest d >= 1 with Tr(d)=1; source twist_a / QuadraticExtension.delta."""
    q = 1 << n
    for d in range(1, q):
        if my_trace(d, n, modulus) == 1:
            return d
    raise ArithmeticError(f"no trace-1 element in F_{{2^{n}}}")


def main() -> int:
    started = time.time()
    with open(PER_R) as fh:
        data = json.load(fh)
    if data.get("run_id") != "RUN-SEMBIN-1b9afe":
        raise SystemExit(f"unexpected run_id {data.get('run_id')}")
    configs = data["configurations"]
    if len(configs) != 180:
        raise SystemExit(f"expected 180 configurations, got {len(configs)}")

    field_cache: dict[int, dict] = {}

    def field_of(n: int) -> dict:
        if n not in field_cache:
            modulus = modulus_for(n)
            delta = twist_delta(n, modulus)
            tr1 = my_trace(1, n, modulus)
            tr_delta = my_trace(delta, n, modulus)
            a_E, a_T = 0, delta  # a_E = 0; a_T = 0 xor delta
            field_cache[n] = {
                "n": n,
                "modulus": modulus,
                "modulus_hex": hex(modulus),
                "delta": delta,
                "Tr(1)": tr1,
                "Tr(1)_equals_n_mod_2": tr1 == (n % 2),
                "a_E": a_E,
                "Tr(a_E)": my_trace(a_E, n, modulus),
                "a_T": a_T,
                "Tr(a_T)": tr_delta,
                "Tr(a_T)_equals_Tr(a_E)_plus_1": tr_delta == (my_trace(a_E, n, modulus) ^ 1),
            }
        return field_cache[n]

    trace_cache: dict[tuple[int, int], int] = {}

    def tr_x(n: int, x: int, modulus: int) -> int:
        key = (n, x)
        if key not in trace_cache:
            trace_cache[key] = my_trace(x, n, modulus)
        return trace_cache[key]

    offenders_i = []
    offenders_ii = []
    n_even_lowdeg_configs = 0
    n_targets_scanned = 0
    n_empty_class_targets = 0
    n_reachable_class_targets = 0
    skipped_sides = []
    per_cfg_summary = []

    for cfg in configs:
        meta = parse_label(cfg["label"])
        if meta["subspace"] != "low_degree_polynomial":
            continue
        if meta["n"] % 2 != 0:
            continue
        n_even_lowdeg_configs += 1
        n = meta["n"]
        m_rel = meta["m"]
        fld = field_of(n)
        modulus = fld["modulus"]
        sides = cfg.get("columns") or {}
        cfg_row = {
            "label": meta["label"],
            "n": n, "m": m_rel, "t": meta["t"], "k": meta["k"],
            "b_mode": meta["b_mode"], "seed": meta["seed"],
            "sides": {},
        }
        for side in ("E", "T"):
            if side not in sides:
                skipped_sides.append({"label": meta["label"], "side": side})
                continue
            cols = sides[side]
            xs = cols["R_x"]
            ys = cols["R_y"]
            single = cols["single_x_multiset"]
            chained = cols["chained_x_multiset"]
            usable = cols["usable_point_multiset"]
            outside = cols["outside_fq_point_multiset"]
            total = cols["point_multiset_total"]
            n_t = len(xs)
            if not (len(ys) == len(single) == len(chained) == len(usable) == n_t):
                raise SystemExit(f"column length mismatch {meta['label']} {side}")
            a = fld["a_E"] if side == "E" else fld["a_T"]
            tr_a = fld["Tr(a_E)"] if side == "E" else fld["Tr(a_T)"]
            confined_parity = (m_rel * tr_a) % 2  # m * Tr(a) mod 2
            n_empty = n_reach = n_i = n_ii = 0
            for i in range(n_t):
                n_targets_scanned += 1
                trx = tr_x(n, int(xs[i]), modulus)
                pi = (trx + tr_a) % 2
                predicted_empty = pi != confined_parity
                if predicted_empty:
                    n_empty += 1
                    n_empty_class_targets += 1
                    nz_i = (int(single[i]) != 0) or (int(chained[i]) != 0)
                    nz_ii = int(usable[i]) != 0
                    rec = {
                        "label": meta["label"],
                        "n": n, "m": m_rel, "t": meta["t"], "k": meta["k"],
                        "subspace": meta["subspace"],
                        "b_mode": meta["b_mode"],
                        "seed": meta["seed"],
                        "side": side,
                        "target_index": i,
                        "R_x": int(xs[i]),
                        "R_y": int(ys[i]),
                        "Tr(x_R)": trx,
                        "a": a,
                        "Tr(a)": tr_a,
                        "pi": pi,
                        "m_Tr_a_mod2": confined_parity,
                        "single_x_multiset": int(single[i]),
                        "chained_x_multiset": int(chained[i]),
                        "usable_point_multiset": int(usable[i]),
                        "outside_fq_point_multiset": int(outside[i]),
                        "point_multiset_total": int(total[i]),
                    }
                    if nz_i:
                        n_i += 1
                        offenders_i.append(rec)
                    if nz_ii:
                        n_ii += 1
                        offenders_ii.append(rec)
                else:
                    n_reach += 1
                    n_reachable_class_targets += 1
            cfg_row["sides"][side] = {
                "a": a,
                "Tr(a)": tr_a,
                "m_Tr_a_mod2": confined_parity,
                "n_targets": n_t,
                "n_predicted_empty": n_empty,
                "n_reachable": n_reach,
                "N1_i_this_side": n_i,
                "N1_ii_this_side": n_ii,
            }
        per_cfg_summary.append(cfg_row)

    # Cross-check my_trace against GF2m.trace on a handful of values.
    from binary_field import GF2m
    cross = []
    for n, fld in sorted(field_cache.items()):
        f = GF2m(n)  # uses modulus_for
        if f.modulus != fld["modulus"]:
            raise SystemExit(f"GF2m modulus mismatch at n={n}")
        for x in (0, 1, 2, 3, fld["delta"], fld["a_T"], (1 << n) - 1):
            mine = my_trace(x, n, fld["modulus"])
            theirs = f.trace(x)
            cross.append({"n": n, "x": x, "mine": mine, "GF2m.trace": theirs,
                          "agree": mine == theirs})
            if mine != theirs:
                raise SystemExit(f"trace disagreement n={n} x={x}")

    out = {
        "pass": "K1_first_pass_BEFORE_producer",
        "source_per_R": PER_R,
        "source_run_id": data.get("run_id"),
        "source_n_configurations_in_file": len(configs),
        "n_even_n_low_degree_polynomial_configurations": n_even_lowdeg_configs,
        "n_targets_scanned": n_targets_scanned,
        "n_predicted_empty_class_targets": n_empty_class_targets,
        "n_reachable_class_targets": n_reachable_class_targets,
        "skipped_sides": skipped_sides,
        "fields": {str(n): v for n, v in sorted(field_cache.items())},
        "trace_crosscheck_vs_GF2m": {
            "n_checked": len(cross),
            "all_agree": all(r["agree"] for r in cross),
            "rows": cross,
        },
        "N1_i_contract_literal_nonzero_single_or_chained": len(offenders_i),
        "N1_ii_usable_point_multiset_only": len(offenders_ii),
        "offenders_i": offenders_i,
        "offenders_ii": offenders_ii,
        "per_configuration": per_cfg_summary,
        "elapsed_seconds": time.time() - started,
        "definitions": {
            "pi": "Tr(x_R) + Tr(a) mod 2, a = 0 on E, a = twist_delta on T",
            "empty_class": "pi != m * Tr(a) mod 2",
            "i": "nonzero in single_x_multiset or chained_x_multiset",
            "ii": "nonzero usable_point_multiset",
        },
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("N1_i", len(offenders_i))
    print("N1_ii", len(offenders_ii))
    print("even_n_lowdeg_configs", n_even_lowdeg_configs)
    print("empty_class_targets", n_empty_class_targets)
    print("reachable_class_targets", n_reachable_class_targets)
    print("fields", {n: {"mod": v["modulus_hex"], "delta": v["delta"],
                          "Tr_a_E": v["Tr(a_E)"], "Tr_a_T": v["Tr(a_T)"],
                          "a_T": v["a_T"]}
                     for n, v in sorted(field_cache.items())})
    print("wrote", OUT)
    if offenders_i:
        from collections import Counter
        print("i_by_label_side",
              Counter((r["label"], r["side"]) for r in offenders_i))
        print("i_usable_values", Counter(r["usable_point_multiset"] for r in offenders_i))
        print("i_single_values", Counter(r["single_x_multiset"] for r in offenders_i))
        print("i_pi", Counter(r["pi"] for r in offenders_i))
        print("i_Tr_x", Counter(r["Tr(x_R)"] for r in offenders_i))
        print("i_sides", Counter(r["side"] for r in offenders_i))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
