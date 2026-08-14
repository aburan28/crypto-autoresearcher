"""inverter_counts.json -- exact enumerated Toffoli / T / peak-width counts for
the derived binary-EEA (Kaliski-style) reversible modular inverter, with a
closed form fitted by exact rational interpolation and residual-checked at the
pre-registered holdout widths.  The inherited Fermat inverter is enumerated at
the same widths with the same instrument, so the two columns are comparable.

Every count is an exact gate-by-gate tally of the SAME circuit object that
run_validation_e.py simulates.  No constant is taken from any publication.
"""
import json
import os
import time
from fractions import Fraction

from common import (TASK, GOAL, BATCH, LANE, T_PER_TOFFOLI, INV_LADDER,
                    INV_HOLDOUT, CLOSED_FORM_ONLY_N, PROHIBITION,
                    BLIND_STATEMENT, CONVENTION_REF, prime_pair, bw,
                    interp_exact, poly_eval, fmt_poly, coeff_list, is_prime)
from euclid import Machine, mod_inv_euclid
from circuits import mod_inv as fermat_mod_inv


def tally_inverter(builder, n, p):
    m = Machine(run=False)
    X = m.alloc(n, io=True)
    T = m.alloc(n, io=True)
    t0 = time.time()
    builder(m, X, T, p)
    b, w = bw(p)
    return {"n": n, "prime_p": p, "b_bitlength_p_minus_2": b,
            "w_hamming_weight_p_minus_2": w,
            "toffoli": m.counts["ccx"], "cnot": m.counts["cnot"],
            "x": m.counts["x"], "t_count": T_PER_TOFFOLI * m.counts["ccx"],
            "peak_qubits": m.peak, "io_qubits": m.io,
            "ancilla_qubits": m.peak - m.io,
            "seconds": round(time.time() - t0, 3)}


def fit_block(rows, key, degree, label):
    fit = [r for r in rows if r["role"] == "fit"]
    pts = sorted({(r["n"], r[key]) for r in fit})
    c = interp_exact(pts, degree)
    res = [{"n": r["n"], "prime_p": r["prime_p"],
            "w_hamming_weight_p_minus_2": r["w_hamming_weight_p_minus_2"],
            "role": r["role"], "enumerated": r[key],
            "closed_form": int(poly_eval(c, r["n"])),
            "residual": r[key] - int(poly_eval(c, r["n"]))} for r in rows]
    return {"quantity": label, "form": fmt_poly(c),
            "coefficients_ascending": coeff_list(c),
            "degree_assumed": degree,
            "fit_method": "exact rational interpolation through the %d "
                          "smallest fitted widths, then residual-checked at "
                          "every fitted AND every pre-registered holdout "
                          "width, in exact integer arithmetic with no "
                          "tolerance" % (degree + 1),
            "fitted_widths": sorted({r["n"] for r in rows
                                     if r["role"] == "fit"}),
            "holdout_widths": sorted({r["n"] for r in rows
                                      if r["role"] == "holdout"}),
            "residuals": res,
            "all_residuals_zero": all(x["residual"] == 0 for x in res),
            "exact_per_preregistration_clause_4":
                all(x["residual"] == 0 for x in res)}


def main():
    t_start = time.time()
    out = {
        "task": TASK, "goal": GOAL, "batch": BATCH, "lane": LANE,
        "artifact": "inverter_counts.json",
        "convention_reference": CONVENTION_REF,
        "preregistration_clauses_discharged": ["1.1", "1.2", "1.7", "1.8",
                                               "3.1", "3.2", "4"],
        "gate_set": ["X", "CNOT", "CCX"],
        "t_count_rule": {
            "rule": "T = 7 * Toffoli",
            "status": "REUSED, not re-derived",
            "reuse_basis":
                "PREREGISTRATION clause 1.2 explicitly permits reuse of "
                "BATCH-973b49's already-derived, already-verified constant "
                "(src/derive_identities.py of TASK-20260813-c99166, which "
                "exhibits an explicit 7-T Clifford+T circuit and compares its "
                "8x8 unitary with the Toffoli permutation matrix; the "
                "Validator of that batch re-derived it exactly over "
                "Z[zeta_8]). It was derived inside this program under this "
                "same convention and is therefore not a cited constant. It "
                "was NOT re-derived by this task.",
            "not_claimed": "optimality; no smaller-T construction is used, "
                           "and none is cited",
        },
        "blind_by_design": BLIND_STATEMENT,
        "prohibition_statement": PROHIBITION,
        "construction": {
            "family": "binary extended Euclidean algorithm (binary GCD) in "
                      "Kaliski/Montgomery form, phase 1 only",
            "why_this_family": "see execution_report.yaml; phase 2 of the "
                               "classical two-phase algorithm is absorbed into "
                               "a classical initialisation constant and costs "
                               "no gates here (derivation D4 in src/euclid.py)",
            "fixed_step_count_K": "2n",
            "fixed_step_count_justification":
                "derivation D2 in src/euclid.py: Phi = bitlength(u) + "
                "bitlength(v) starts at most 2n, drops by at least 1 per "
                "iteration and is 1 in the terminal state (u,v) = (1,0), so "
                "v = 0 is reached within 2n-1 iterations. The circuit runs a "
                "FIXED 2n iterations on every input, which is "
                "PREREGISTRATION clause 1.4's pre-registered resolution of "
                "the data-dependent-iteration tension. The bound is also "
                "confirmed exhaustively for n = 3..16 in "
                "inverter_validation.json.",
            "structure": "phase 1 built once, result copied out with n CNOTs, "
                         "phase 1 replayed inverted -- identical in shape to "
                         "BATCH-973b49's Fermat mod_inv, so the substitution "
                         "into point_add is like for like",
            "per_iteration_toffoli_derived":
                "1 (both-odd flag) + 4(n+1) (comparison u > v by an inherited "
                "ripple subtraction, its sign bit copied out, then added back) "
                "+ 1 (branch-3 flag) + 4(n+1) (controlled u <- u-v) + 4(n+1) "
                "(controlled v <- v-u) + n (controlled cyclic right rotation "
                "of u) + n (same for v) + 2*(12n+10) (two controlled modular "
                "additions, each a controlled copy in and out at 2n plus the "
                "inherited mod_add at 10(n+1)) + 2*(5n+5) (two controlled "
                "modular doublings) = 48n + 44",
            "inverter_toffoli_derived":
                "2 * K * (48n + 44) = 2 * 2n * (48n + 44) = 192n^2 + 176n, "
                "the factor 2 being the forward phase-1 circuit and its "
                "inverse",
        },
        "measurement_status": {
            "enumerated": "exact gate-by-gate tally of the built circuit",
            "closed_form": "exact rational interpolation on the fitted widths, "
                           "residual-checked at every fitted and held-out "
                           "width",
            "evaluated_from_closed_form":
                "closed form evaluated at a width not enumerated here; "
                "arithmetic, not a measurement",
        },
    }

    print("== euclid inverter ==", flush=True)
    rows = []
    for n in INV_LADDER + INV_HOLDOUT:
        for p, kind in prime_pair(n):
            r = tally_inverter(mod_inv_euclid, n, p)
            r["role"] = "fit" if n in INV_LADDER else "holdout"
            r["prime_kind"] = kind
            rows.append(r)
            print(" n=%-3d p=%-12d w=%-3d toffoli=%-10d peak=%-6d %.2fs"
                  % (n, p, r["w_hamming_weight_p_minus_2"], r["toffoli"],
                     r["peak_qubits"], r["seconds"]), flush=True)

    print("== fermat inverter (inherited, same instrument) ==", flush=True)
    frows = []
    for n in INV_LADDER + INV_HOLDOUT:
        for p, kind in prime_pair(n):
            r = tally_inverter(fermat_mod_inv, n, p)
            r["role"] = "fit" if n in INV_LADDER else "holdout"
            r["prime_kind"] = kind
            frows.append(r)
            print(" n=%-3d p=%-12d w=%-3d toffoli=%-12d peak=%-8d %.2fs"
                  % (n, p, r["w_hamming_weight_p_minus_2"], r["toffoli"],
                     r["peak_qubits"], r["seconds"]), flush=True)

    # ---- structure-dependence check: same n, two primes, same Toffoli? ----
    dep = []
    for n in sorted({r["n"] for r in rows}):
        grp = [r for r in rows if r["n"] == n]
        fgrp = [r for r in frows if r["n"] == n]
        if len(grp) < 2:
            continue
        dep.append({
            "n": n,
            "primes": [g["prime_p"] for g in grp],
            "w_of_p_minus_2": [g["w_hamming_weight_p_minus_2"] for g in grp],
            "euclid_toffoli": [g["toffoli"] for g in grp],
            "euclid_toffoli_identical":
                len({g["toffoli"] for g in grp}) == 1,
            "euclid_peak_qubits": [g["peak_qubits"] for g in grp],
            "euclid_peak_identical":
                len({g["peak_qubits"] for g in grp}) == 1,
            "euclid_cnot": [g["cnot"] for g in grp],
            "euclid_cnot_identical": len({g["cnot"] for g in grp}) == 1,
            "euclid_x": [g["x"] for g in grp],
            "fermat_toffoli": [g["toffoli"] for g in fgrp],
            "fermat_toffoli_identical":
                len({g["toffoli"] for g in fgrp}) == 1,
            "fermat_peak_qubits": [g["peak_qubits"] for g in fgrp],
        })

    out["euclid_inverter"] = {
        "rows": rows,
        "toffoli_closed_form": fit_block(rows, "toffoli", 2, "toffoli"),
        "peak_qubits_closed_form": fit_block(rows, "peak_qubits", 1,
                                             "peak_qubits"),
        "ancilla_qubits_closed_form": fit_block(rows, "ancilla_qubits", 1,
                                                "ancilla_qubits"),
        "io_qubits": "2n (the n-bit input register X, preserved, and the "
                     "n-bit output register T)",
        "cnot_and_x_note":
            "CNOT and X counts DO depend on the classical constants loaded "
            "into the u and s registers (p and -2^{-2n} mod p) and on the "
            "Hamming weight of p inside the inherited mod_add / mod_dbl "
            "conditional constant loads. They are reported per row and are "
            "not fitted. Toffoli, T, peak_qubits and ancilla_qubits are "
            "prime-independent -- see structure_dependence_check.",
    }
    out["fermat_inverter_inherited"] = {
        "note": "The inherited Fermat inverter (circuits.mod_inv) enumerated "
                "at the same widths with the same instrument. Its Toffoli "
                "count is NOT a function of n alone: it depends on b and w of "
                "p-2, which is why no closed form in n is fitted for it here. "
                "Its exact form is EV-QRE-45dfe1's "
                "2(b+w-2)(20n^2+10n-8).",
        "rows": frows,
        "exact_form_check": [
            {"n": r["n"], "prime_p": r["prime_p"],
             "b": r["b_bitlength_p_minus_2"],
             "w": r["w_hamming_weight_p_minus_2"],
             "enumerated": r["toffoli"],
             "closed_form": 2 * (r["b_bitlength_p_minus_2"]
                                 + r["w_hamming_weight_p_minus_2"] - 2)
                            * (20 * r["n"] ** 2 + 10 * r["n"] - 8),
             "residual": r["toffoli"] - 2 * (r["b_bitlength_p_minus_2"]
                                             + r["w_hamming_weight_p_minus_2"]
                                             - 2)
                         * (20 * r["n"] ** 2 + 10 * r["n"] - 8)}
            for r in frows],
    }
    out["fermat_inverter_inherited"]["exact_form_all_residuals_zero"] = all(
        x["residual"] == 0
        for x in out["fermat_inverter_inherited"]["exact_form_check"])

    out["structure_dependence_check"] = {
        "question": "Does the new inverter's cost depend on any property of p, "
                    "or on n alone? PREREGISTRATION clause 4 (ii) and 6.5.",
        "method": "two primes per bit length, chosen for the LOWEST and the "
                  "HIGHEST Hamming weight of p-2 among the 40 largest primes "
                  "of that length, enumerated separately",
        "rows": dep,
        "euclid_toffoli_is_function_of_n_alone":
            all(d["euclid_toffoli_identical"] for d in dep),
        "euclid_peak_is_function_of_n_alone":
            all(d["euclid_peak_identical"] for d in dep),
        "euclid_cnot_is_function_of_n_alone":
            all(d["euclid_cnot_identical"] for d in dep),
        "fermat_toffoli_is_function_of_n_alone":
            all(d["fermat_toffoli_identical"] for d in dep),
    }

    ct = out["euclid_inverter"]["toffoli_closed_form"]["coefficients_ascending"]
    cq = out["euclid_inverter"]["peak_qubits_closed_form"][
        "coefficients_ascending"]
    ctf = [Fraction(x) for x in ct]
    cqf = [Fraction(x) for x in cq]
    p256 = next(p for p in [(1 << 256) - k for k in range(1, 4000, 2)]
                if is_prime(p))
    b256, w256 = bw(p256)
    out["evaluated_at_256_bit_shape"] = {
        "n": CLOSED_FORM_ONLY_N,
        "prime_p": p256, "b": b256, "w": w256,
        "prime_selection": "largest prime below 2^256, computed here; it is "
                           "the SAME prime BATCH-973b49 used, so the "
                           "comparison is at one (n, p) pair",
        "status": "evaluated_from_closed_form",
        "euclid_inverter_toffoli": int(poly_eval(ctf, CLOSED_FORM_ONLY_N)),
        "euclid_inverter_t_count":
            T_PER_TOFFOLI * int(poly_eval(ctf, CLOSED_FORM_ONLY_N)),
        "euclid_inverter_peak_qubits": int(poly_eval(cqf, CLOSED_FORM_ONLY_N)),
        "fermat_inverter_toffoli":
            2 * (b256 + w256 - 2) * (20 * 256 ** 2 + 10 * 256 - 8),
        "fermat_inverter_peak_qubits": "not evaluated here from a closed form; "
                                       "the enumerated Fermat peak widths are "
                                       "in fermat_inverter_inherited.rows and "
                                       "the point-addition peak comparison at "
                                       "n = 256 is in baseline_comparison.json",
        "caveat":
            "Arithmetic on a closed form that reproduces every enumerated "
            "width with zero residual, not a measurement, and not a claim "
            "that either construction is the cheapest one. Both sides are "
            "the cost of THESE constructions under the frozen convention.",
    }

    out["wall_clock_seconds"] = round(time.time() - t_start, 2)
    dest = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "inverter_counts.json")
    with open(dest, "w") as fh:
        json.dump(out, fh, indent=2)
    print("wrote", dest, "in %.2fs" % out["wall_clock_seconds"])


if __name__ == "__main__":
    main()
