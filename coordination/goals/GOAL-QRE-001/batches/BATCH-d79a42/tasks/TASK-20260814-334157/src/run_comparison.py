"""baseline_comparison.json -- one point addition counted with the derived
binary-EEA inverter substituted in, against the frozen Fermat-inversion
baseline of EV-QRE-45dfe1, on every axis at every declared width.

STRUCTURAL GUARD AGAINST THE OMISSION DEC-20260813-5cef9c RECORDS.  Every
comparison row is produced by one function that fills a FIXED column set --
toffoli, t_count, peak_qubits, ancilla_qubits, io_qubits, and the parameter
dependence -- for BOTH sides.  A row cannot be emitted with a column present on
one side and absent on the other, at any width, favourable or not.

Both sides are enumerated with the SAME instrument: BATCH-973b49's builder,
counter and Machine.  The Fermat side is a live enumeration of the inherited
circuits.mod_inv-based point_add, and EV-QRE-45dfe1's published closed form is
re-checked against that enumeration rather than assumed.
"""
import json
import os
import time
from fractions import Fraction

from common import (TASK, GOAL, BATCH, LANE, T_PER_TOFFOLI, EC_LADDER,
                    EC_HOLDOUT, CLOSED_FORM_ONLY_N, PROHIBITION,
                    BLIND_STATEMENT, CONVENTION_REF, prime_pair, bw,
                    any_point, is_prime, interp_exact, poly_eval, fmt_poly,
                    coeff_list, fermat_pointadd_closed_form)
from circuits import point_add as fermat_point_add
from euclid import Machine, point_add_euclid


def tally_pointadd(builder, n, p):
    x2, y2, A, B = any_point(p)
    m = Machine(run=False)
    X = m.alloc(n, io=True)
    Y = m.alloc(n, io=True)
    t0 = time.time()
    builder(m, X, Y, p, x2, y2)
    b, w = bw(p)
    return {"n": n, "prime_p": p, "b_bitlength_p_minus_2": b,
            "w_hamming_weight_p_minus_2": w, "curve_A": A, "curve_B": B,
            "constant_point_Q": [x2, y2],
            "toffoli": m.counts["ccx"], "cnot": m.counts["cnot"],
            "x": m.counts["x"], "t_count": T_PER_TOFFOLI * m.counts["ccx"],
            "peak_qubits": m.peak, "io_qubits": m.io,
            "ancilla_qubits": m.peak - m.io,
            "seconds": round(time.time() - t0, 3)}


def solve_exact(basis_rows, values):
    """Exact rational solve of a square system."""
    k = len(values)
    mtx = [[Fraction(v) for v in basis_rows[i]] + [Fraction(values[i])]
           for i in range(k)]
    for i in range(k):
        piv = next(r for r in range(i, k) if mtx[r][i] != 0)
        mtx[i], mtx[piv] = mtx[piv], mtx[i]
        mtx[i] = [v / mtx[i][i] for v in mtx[i]]
        for r in range(k):
            if r != i and mtx[r][i] != 0:
                f = mtx[r][i]
                mtx[r] = [a - f * b for a, b in zip(mtx[r], mtx[i])]
    return [row[k] for row in mtx]


def main():
    t_start = time.time()
    widths = EC_LADDER + EC_HOLDOUT

    print("== euclid-inverter point addition ==", flush=True)
    erows = []
    for n in widths:
        for p, kind in prime_pair(n):
            r = tally_pointadd(point_add_euclid, n, p)
            r["role"] = "fit" if n in EC_LADDER else "holdout"
            r["prime_kind"] = kind
            r["inverter"] = "euclid_binary_eea"
            erows.append(r)
            print(" E n=%-3d p=%-12d w=%-3d tof=%-12d peak=%-6d %.2fs"
                  % (n, p, r["w_hamming_weight_p_minus_2"], r["toffoli"],
                     r["peak_qubits"], r["seconds"]), flush=True)

    print("== fermat-inverter point addition (inherited baseline) ==",
          flush=True)
    frows = []
    for n in widths:
        for p, kind in prime_pair(n):
            r = tally_pointadd(fermat_point_add, n, p)
            r["role"] = "fit" if n in EC_LADDER else "holdout"
            r["prime_kind"] = kind
            r["inverter"] = "fermat_x_pow_p_minus_2"
            frows.append(r)
            print(" F n=%-3d p=%-12d w=%-3d tof=%-12d peak=%-6d %.2fs"
                  % (n, p, r["w_hamming_weight_p_minus_2"], r["toffoli"],
                     r["peak_qubits"], r["seconds"]), flush=True)

    # ---------------- closed forms, new side: functions of n alone? --------
    efit = [r for r in erows if r["role"] == "fit"]
    ct = interp_exact(sorted({(r["n"], r["toffoli"]) for r in efit}), 2)
    cq = interp_exact(sorted({(r["n"], r["peak_qubits"]) for r in efit}), 1)
    ca = interp_exact(sorted({(r["n"], r["ancilla_qubits"]) for r in efit}), 1)

    def resid(rows, key, coeffs):
        return [{"n": r["n"], "prime_p": r["prime_p"],
                 "w_hamming_weight_p_minus_2": r["w_hamming_weight_p_minus_2"],
                 "role": r["role"], "enumerated": r[key],
                 "closed_form": int(poly_eval(coeffs, r["n"])),
                 "residual": r[key] - int(poly_eval(coeffs, r["n"]))}
                for r in rows]

    e_tof_res = resid(erows, "toffoli", ct)
    e_pk_res = resid(erows, "peak_qubits", cq)
    e_an_res = resid(erows, "ancilla_qubits", ca)

    # ---------------- closed forms, baseline side: n, b, w -----------------
    f_tof_res = [{"n": r["n"], "prime_p": r["prime_p"],
                  "b": r["b_bitlength_p_minus_2"],
                  "w": r["w_hamming_weight_p_minus_2"], "role": r["role"],
                  "enumerated": r["toffoli"],
                  "closed_form": fermat_pointadd_closed_form(r["n"],
                                                             r["prime_p"]),
                  "residual": r["toffoli"] - fermat_pointadd_closed_form(
                      r["n"], r["prime_p"])} for r in frows]

    # peak width of the baseline: EV-QRE-45dfe1 gave only a fit in n alone,
    # which cannot be exact because the Fermat chain holds b+w-2 registers.
    # Derive an exact form in (n, b, w) here, in basis [n(b+w), n, 1].
    pick = frows[:3]
    sol = solve_exact([[r["n"] * (r["b_bitlength_p_minus_2"]
                                 + r["w_hamming_weight_p_minus_2"]),
                        r["n"], 1] for r in pick],
                      [r["peak_qubits"] for r in pick])

    def fpeak(n, b, w):
        v = sol[0] * n * (b + w) + sol[1] * n + sol[2]
        return int(v)

    f_pk_res = [{"n": r["n"], "prime_p": r["prime_p"],
                 "b": r["b_bitlength_p_minus_2"],
                 "w": r["w_hamming_weight_p_minus_2"], "role": r["role"],
                 "enumerated": r["peak_qubits"],
                 "closed_form": fpeak(r["n"], r["b_bitlength_p_minus_2"],
                                      r["w_hamming_weight_p_minus_2"]),
                 "residual": r["peak_qubits"] - fpeak(
                     r["n"], r["b_bitlength_p_minus_2"],
                     r["w_hamming_weight_p_minus_2"])} for r in frows]

    # ---------------- the comparison table --------------------------------
    def verdict(new, old):
        if new < old:
            return "new_better"
        if new > old:
            return "new_worse"
        return "equal"

    table = []
    for e, f in zip(erows, frows):
        assert (e["n"], e["prime_p"]) == (f["n"], f["prime_p"])
        row = {
            "n": e["n"], "prime_p": e["prime_p"], "prime_kind": e["prime_kind"],
            "role": e["role"],
            "b_bitlength_p_minus_2": e["b_bitlength_p_minus_2"],
            "w_hamming_weight_p_minus_2": e["w_hamming_weight_p_minus_2"],
            "status": "enumerated",
        }
        for axis in ("toffoli", "t_count", "peak_qubits", "ancilla_qubits",
                     "io_qubits"):
            row["euclid_" + axis] = e[axis]
            row["fermat_" + axis] = f[axis]
        for axis in ("toffoli", "t_count", "peak_qubits", "ancilla_qubits"):
            row["verdict_" + axis] = verdict(e[axis], f[axis])
            row["ratio_" + axis + "_fermat_over_euclid"] = (
                round(f[axis] / e[axis], 4) if e[axis] else None)
        row["euclid_parameter_dependence"] = "n alone"
        row["fermat_parameter_dependence"] = "n, b = bitlength(p-2), " \
                                             "w = weight(p-2)"
        table.append(row)

    # ---------------- closed-form-only point, n = 256 ---------------------
    p256 = next(p for p in [(1 << 256) - k for k in range(1, 4000, 2)]
                if is_prime(p))
    b256, w256 = bw(p256)
    N = CLOSED_FORM_ONLY_N
    e256 = {"toffoli": int(poly_eval(ct, N)),
            "peak_qubits": int(poly_eval(cq, N)),
            "ancilla_qubits": int(poly_eval(ca, N))}
    e256["t_count"] = T_PER_TOFFOLI * e256["toffoli"]
    f256 = {"toffoli": fermat_pointadd_closed_form(N, p256),
            "peak_qubits": fpeak(N, b256, w256)}
    f256["t_count"] = T_PER_TOFFOLI * f256["toffoli"]
    f256["ancilla_qubits"] = f256["peak_qubits"] - 2 * N
    row256 = {"n": N, "prime_p": p256, "prime_kind": "largest_prime_below_2^256",
              "role": "closed_form_only", "b_bitlength_p_minus_2": b256,
              "w_hamming_weight_p_minus_2": w256,
              "status": "evaluated_from_closed_form",
              "euclid_io_qubits": 2 * N, "fermat_io_qubits": 2 * N}
    for axis in ("toffoli", "t_count", "peak_qubits", "ancilla_qubits"):
        row256["euclid_" + axis] = e256[axis]
        row256["fermat_" + axis] = f256[axis]
        row256["verdict_" + axis] = verdict(e256[axis], f256[axis])
        row256["ratio_" + axis + "_fermat_over_euclid"] = round(
            f256[axis] / e256[axis], 4)
    row256["euclid_parameter_dependence"] = "n alone"
    row256["fermat_parameter_dependence"] = "n, b, w"
    table.append(row256)

    enum = [r for r in table if r["status"] == "enumerated"]

    def axis_summary(axis):
        v = [r["verdict_" + axis] for r in enum]
        worse = [{"n": r["n"], "prime_p": r["prime_p"],
                  "euclid": r["euclid_" + axis], "fermat": r["fermat_" + axis]}
                 for r in enum if r["verdict_" + axis] == "new_worse"]
        return {
            "axis": axis,
            "enumerated_pairs": len(enum),
            "new_better": v.count("new_better"),
            "new_worse": v.count("new_worse"),
            "equal": v.count("equal"),
            "widths_where_new_is_worse": sorted({r["n"] for r in worse}),
            "pairs_where_new_is_worse": worse,
            "closed_form_only_n256_verdict": row256["verdict_" + axis],
        }

    out = {
        "task": TASK, "goal": GOAL, "batch": BATCH, "lane": LANE,
        "artifact": "baseline_comparison.json",
        "convention_reference": CONVENTION_REF,
        "preregistration_clauses_discharged": ["1.6", "1.8", "3.1", "4", "6",
                                               "6.1", "6.2", "6.3", "6.4",
                                               "6.5"],
        "baseline_identity":
            "EV-QRE-45dfe1, produced by BATCH-973b49 / TASK-20260813-c99166. "
            "The baseline side of every row here is a LIVE re-enumeration of "
            "that batch's own point_add with its own Fermat mod_inv, run "
            "through its own Machine, so the two sides differ only in the "
            "inverter sub-circuit.",
        "same_instrument_statement":
            "src/euclid.py imports BATCH-973b49's circuits.py and rebinds only "
            "the name `mod_inv` for the duration of the call. The "
            "point-addition structure -- coordinate subtractions, slope "
            "multiplication, uncomputation of lambda, the surrounding "
            "capture/replay pattern -- is that module's own source, executed "
            "unmodified.",
        "column_set_guard":
            "Every row carries toffoli, t_count, peak_qubits, ancilla_qubits "
            "and io_qubits for BOTH sides, at every width including the "
            "closed-form-only n = 256 row. DEC-20260813-5cef9c records that "
            "the previous package omitted peak_qubits from the unfavourable "
            "256-bit block while reporting it for RSA; the rows here are "
            "emitted by one function with a fixed column set so that the "
            "omission cannot recur.",
        "axis_independence_statement":
            "PREREGISTRATION clauses 6.2 and 6.3: each axis is scored "
            "separately. A Toffoli result and a peak-width result are never "
            "netted into one verdict.",
        "blind_by_design": BLIND_STATEMENT,
        "prohibition_statement": PROHIBITION,
        "validation_gate":
            "Every enumerated width in EC_LADDER on the new side was "
            "simulated and passed with clean ancillas; see "
            "inverter_validation.json. The holdout widths 15, 16, 20, 24, 32 "
            "were enumerated and NOT simulated, exactly as BATCH-973b49's "
            "holdouts were not.",
        "euclid_closed_forms": {
            "toffoli": {"form": fmt_poly(ct),
                        "coefficients_ascending": coeff_list(ct),
                        "degree_assumed": 2, "residuals": e_tof_res,
                        "all_residuals_zero": all(x["residual"] == 0
                                                  for x in e_tof_res)},
            "peak_qubits": {"form": fmt_poly(cq),
                            "coefficients_ascending": coeff_list(cq),
                            "degree_assumed": 1, "residuals": e_pk_res,
                            "all_residuals_zero": all(x["residual"] == 0
                                                      for x in e_pk_res)},
            "ancilla_qubits": {"form": fmt_poly(ca),
                               "coefficients_ascending": coeff_list(ca),
                               "degree_assumed": 1, "residuals": e_an_res,
                               "all_residuals_zero": all(x["residual"] == 0
                                                         for x in e_an_res)},
            "derivation":
                "four replays of the inverter block (two inversion sites, each "
                "replayed forward and inverted by the inherited point_add) at "
                "192n^2 + 176n each, plus the five quantum-quantum modular "
                "multiplications at 20n^2 + 10n - 8, plus five constant "
                "modular additions at 10(n+1) and one modular negation at 2n: "
                "4(192n^2 + 176n) + 5(20n^2 + 10n - 8) + 50(n+1) + 2n "
                "= 868n^2 + 806n + 10.",
            "parameter_dependence": "n alone; see "
                                    "hamming_weight_question below",
        },
        "fermat_closed_forms": {
            "toffoli": {
                "form": "(8(b+w-2)+5)(20n^2+10n-8) + 50(n+1) + 2n",
                "source": "EV-QRE-45dfe1 / BATCH-973b49 counts.json, "
                          "RE-CHECKED here against a live enumeration",
                "residuals": f_tof_res,
                "all_residuals_zero": all(x["residual"] == 0
                                          for x in f_tof_res)},
            "peak_qubits": {
                "form": "%s*n*(b+w) + %s*n + %s" % (sol[0], sol[1], sol[2]),
                "basis": "[n(b+w), n, 1], solved exactly on the three smallest "
                         "enumerated baseline rows",
                "why_derived_here":
                    "EV-QRE-45dfe1 published only a fit in n alone for the "
                    "baseline peak width, which cannot be exact because the "
                    "Fermat chain holds b+w-2 registers of n qubits. An exact "
                    "form is derived here so that the n = 256 peak-width "
                    "comparison has a baseline value at all, rather than a "
                    "blank cell on the unfavourable axis.",
                "residuals": f_pk_res,
                "all_residuals_zero": all(x["residual"] == 0
                                          for x in f_pk_res)},
            "parameter_dependence": "n, b = bitlength(p-2), w = weight(p-2)",
        },
        "comparison_table": table,
        "per_axis_summary": {a: axis_summary(a) for a in
                             ("toffoli", "t_count", "peak_qubits",
                              "ancilla_qubits")},
        "hamming_weight_question": {
            "clause": "PREREGISTRATION 6.5",
            "baseline": "The Fermat point-addition count depends on the "
                        "Hamming weight w of p-2 and on b = bitlength(p-2): "
                        "no function of n alone is exact for it "
                        "(EV-QRE-45dfe1).",
            "new_side_toffoli_depends_on":
                "n alone. The circuit runs a fixed K = 2n iterations whose "
                "gate content does not branch on p; the only place p enters "
                "the construction is as a classical constant loaded by X and "
                "CNOT gates (into the u register, the s0 initialisation, and "
                "the conditional constant addends inside the inherited mod_add "
                "and mod_dbl), and those loads emit no Toffoli.",
            "measured_how":
                "two primes per bit length, chosen for the LOWEST and the "
                "HIGHEST weight(p-2) among the 40 largest primes of that "
                "length, enumerated separately at every width",
            "toffoli_identical_across_the_prime_pair":
                all(a["toffoli"] == b["toffoli"] for a, b in
                    zip(erows[0::2], erows[1::2])
                    if a["n"] == b["n"]),
            "peak_qubits_identical_across_the_prime_pair":
                all(a["peak_qubits"] == b["peak_qubits"] for a, b in
                    zip(erows[0::2], erows[1::2]) if a["n"] == b["n"]),
            "what_still_depends_on_p":
                "the CNOT and X counts, through the Hamming weights of the "
                "classical constants loaded. Those are reported per row in "
                "inverter_counts.json and are not fitted, exactly as the "
                "baseline's were.",
            "scope":
                "This is an observation about the enumerated counts of these "
                "two constructions at these widths and primes under the frozen "
                "convention. It is not a statement about modular inversion in "
                "general.",
        },
        "wall_clock_seconds": None,
    }
    out["wall_clock_seconds"] = round(time.time() - t_start, 2)
    dest = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "baseline_comparison.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=2)
    print("wrote", dest, "in %.1fs" % out["wall_clock_seconds"])


if __name__ == "__main__":
    main()
