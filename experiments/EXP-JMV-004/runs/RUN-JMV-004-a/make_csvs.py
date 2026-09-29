#!/usr/bin/env python3
"""Build crossover.csv and constants_table.csv from raw.json.

Not itself a required_artifact; a reproducibility helper archived alongside
compute_grid.py in this run directory.
"""
import csv
import json

with open("raw.json") as f:
    raw = json.load(f)

grid = raw["grid"]
flip_keys = {tuple(k) for k in raw["log_convention_flips"]}

VARIANT_KEYS = None
for row in grid:
    if row.get("costs"):
        VARIANT_KEYS = list(row["costs"].keys())
        break

fieldnames = [
    "bits", "delta", "log_convention", "C",
    "m", "k_half_split_primes_over_2", "k_full_split_primes_no_half",
    "c", "ratio_half", "ratio_full",
    "sign_log_kc_half_PRIMARY", "sign_log_kc_full_ALT",
    "degree_convention_flip", "log_convention_flip_bits_vs_natural",
    "r_half_walk_length", "rho_sqrt_n",
    "phi_l_storage_coeffs_order", "phi_l_full_set_storage_coeffs_order",
]
for vk in (VARIANT_KEYS or []):
    fieldnames += [f"cost__{vk}", f"cost_over_rho__{vk}", f"cheaper_than_rho__{vk}"]

with open("crossover.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for row in grid:
        if "not_computable" in row:
            continue
        key = (row["bits"], row["delta"], row["C"])
        out = {
            "bits": row["bits"], "delta": row["delta"],
            "log_convention": row["log_convention"], "C": row["C"],
            "m": row["m"],
            "k_half_split_primes_over_2": row["k_half"],
            "k_full_split_primes_no_half": row["k_full"],
            "c": row["c"],
            "ratio_half": row["ratio_half"], "ratio_full": row["ratio_full"],
            "sign_log_kc_half_PRIMARY": row["sign_half"],
            "sign_log_kc_full_ALT": row["sign_full"],
            "degree_convention_flip": row["degree_convention_flip"],
            "log_convention_flip_bits_vs_natural": (key in flip_keys),
            "r_half_walk_length": row.get("r_half"),
            "rho_sqrt_n": row.get("rho"),
            "phi_l_storage_coeffs_order": row.get("phi_l_storage_coeffs_order"),
            "phi_l_full_set_storage_coeffs_order": row.get("phi_l_full_set_storage_coeffs_order"),
        }
        costs = row.get("costs") or {}
        for vk in (VARIANT_KEYS or []):
            c = costs.get(vk)
            if c:
                out[f"cost__{vk}"] = c["total_cost"]
                out[f"cost_over_rho__{vk}"] = c["cost_over_rho"]
                out[f"cheaper_than_rho__{vk}"] = c["cheaper_than_rho"]
            else:
                out[f"cost__{vk}"] = "NA_ratio_not_positive"
                out[f"cost_over_rho__{vk}"] = "NA"
                out[f"cheaper_than_rho__{vk}"] = "NA"
        w.writerow(out)

print(f"crossover.csv written: {len(grid)} source rows -> see file for count actually written")

# constants_table.csv
constants = [
    dict(constant="delta", value="swept: 0.25, 0.5, 1.0, 2.0",
         role="free polynomial-degree parameter of m=(log q)^(2+delta)",
         source="Theorem 1.1 (transcribed, as held; asserts existence of SOME polynomial p(log q), not this specific family)",
         statement_no="Thm 1.1",
         hypotheses="Held transcription only; NOT checked against arXiv:math/0411378v3 (C1 pending)."),
    dict(constant="log-convention for 'log q' in m's formula", value="swept: bits (log2 q), natural (ln q)",
         role="resolves an explicit ambiguity flagged in the held transcription's own honesty notes",
         source="cost_model.py module docstring, CRITICAL HONESTY NOTE 2 (held transcription)",
         statement_no="n/a (implementation note, not a paper equation)",
         hypotheses="Ambiguity is in OUR reading of 'log q', not asserted to be in the paper itself; both computed, no single value chosen as ground truth."),
    dict(constant="degree convention for k (split-prime generator count)",
         value="PRIMARY: k=Li(m)/2 (split primes as pairs); ALT: k=Li(m) (each split prime, 2 generators)",
         role="fixes whether a split prime contributes one generator or two (condition E2)",
         source="cost_model.py docstring 'k = lambda_triv ~ #{split p <= m} ~ pi(m)/2 [Sec 4.3]' (held transcription)",
         statement_no="Sec 4.3",
         hypotheses="PRIMARY convention adopted per the held transcription's own stated formula (with the /2 factor); ALT computed for E2 sensitivity only, not adopted. NOT checked against source (C1 pending)."),
    dict(constant="pi(m) estimator", value="Li(m) = li(m) - li(2), offset logarithmic integral, evaluated at 60 decimal digits (mpmath)",
         role="standard analytic-number-theory estimator for the count of primes <= m",
         source="Standard number theory (not paper-specific); used by the held scouting script via numerical integration of the same closed form",
         statement_no="n/a",
         hypotheses="Order-of-magnitude / standard asymptotic estimator, not an exact count; disclosed as an approximation layered on top of Sec 4.3's own lambda_triv ~ pi(m)/2 approximation."),
    dict(constant="C (Lemma 4.1 implied constant)", value="NOT PINNED. Swept: 0.5, 1, 2, 4, 8",
         role="multiplicative constant in the explicit GRH-conditional eigenvalue bound c = C*sqrt(m)*log|mD|",
         source="cost_model.py docstring 'c = C * m^(1/2) * log|mD| [Lemma 4.1]' (held transcription); paper states only that C is absolute, per CRITICAL HONESTY NOTE 1",
         statement_no="Lemma 4.1",
         hypotheses="GRH-conditional (CTRL-GRH). Single value NOT_COMPUTABLE_WITHOUT_CITATION: needs Bach-Sorenson explicit constants (JMV ref [2]), not held in this repository's corpus. Swept, not invented."),
    dict(constant="|D| <= 4q bound", value="used as equality |D|=4q for ln|mD| (worst case, largest discriminant)",
         role="bounds the fundamental discriminant magnitude entering Lemma 4.1's log|mD| term",
         source="cost_model.py docstring 'c = ... log|mD|, |D| <= 4q [Lemma 4.1]' (held transcription)",
         statement_no="Lemma 4.1",
         hypotheses="Held transcription's own stated bound; using the bound as equality is conservative (largest log|mD|, so largest c, so most conservative/smallest ratio -- biases AGAINST finding a positive sign, i.e. this choice cannot manufacture a false positive-sign result)."),
    dict(constant="h ~ sqrt(q) (class number order of magnitude)",
         value="ln_h = 0.5*ln(q)", role="approximate class number entering Prop 3.1's walk-length bound",
         source="cost_model.py docstring 'h ~ sqrt(|D|) ~ sqrt(q) [class number, order of magnitude]' (held transcription; NOT tied to a specific theorem/equation number in the held material)",
         statement_no="n/a (order-of-magnitude note only, not a numbered statement)",
         hypotheses="Order-of-magnitude approximation, disclosed as such; affects r (walk length / total cost) but NOT the sign of log(k/c), which depends only on k and c."),
    dict(constant="eps (target-set-size parameter in Prop 3.1's r formula, |S|=eps*h)",
         value="declared assumption: 0.5 (sensitivity checked at 0.1, 0.5, 0.9)",
         role="statistical parameter in the walk-length lower bound r >= log(2h/|S|^(1/2))/log(k/c)",
         source="cost_model.py's implementation choice (model() function default eps=0.5); NOT traceable to a specific numeric value in the held transcription",
         statement_no="n/a -- NOT_COMPUTABLE_WITHOUT_CITATION for a specific value; DECLARED by choice",
         hypotheses="Declared assumption, not invented silently. Effect on the sign of log(k/c): NONE (eps does not appear in k or c). Effect on r: enters only inside a logarithm (ln_S term), so r changes only weakly with eps; verified numerically across {0.1,0.5,0.9} in this run."),
    dict(constant="Per-step cost exponent for Phi_l root-finding: O(l^3)",
         value="PRIMARY / APPLICABLE per the frozen specification's own method",
         role="cost of root-finding on Phi_l(j(E),X) for one walk step",
         source="cost_model.py docstring 'phi_l O(l^3) JMV Sec 4.1, via modular polynomials (Galbraith)' (held transcription)",
         statement_no="JMV Sec 4.1",
         hypotheses="This is the cost model the frozen specification.yaml's own method (item 4) requires: 'Per-step cost: root-finding on Phi_l(j(E), X)'."),
    dict(constant="Per-step cost O(l) (plain Velu) and O(sqrt(l)) (BDLS 2020)",
         value="OPTIMISTIC / CAVEATED, reported in addition to the primary O(l^3) row",
         role="alternative per-step cost models, IF a kernel point is already in hand",
         source="cost_model.py docstring items 2-3 under 'Three per-step cost models are reported' (held transcription)",
         statement_no="n/a (algorithmic literature, not the JMV paper)",
         hypotheses="APPLICABILITY CAVEAT (from the held scouting note, research/JMV004_branch_a_scouting_20260726.md, 'The load-bearing caveat'): a random split prime l<=m generally does NOT have rational l-torsion over the base field, so a kernel generator is not cheaply sampleable; these two rows are optimistic lower bounds, not established costs for this setting, and are reported for transparency only, never as the applicable figure."),
    dict(constant="Phi_l storage: O(l^2) coefficients",
         value="order-of-magnitude coefficient count, evaluated at typical l ~ m per cell",
         role="precomputation / storage term for the modular polynomial (condition E4)",
         source="specification.yaml method item 5 (frozen contract's own text): 'Phi_l has on the order of l^2 coefficients and is not storable' at the m the theorem's generator set forces at cryptographic q",
         statement_no="specification.yaml method item 5",
         hypotheses="Coefficient-COUNT order of magnitude only. A bit-size / field-operation conversion for this storage (e.g. per-coefficient bit length) is NOT_COMPUTABLE_WITHOUT_CITATION: no numeric coefficient-bit-size formula is held in this repository's corpus, so none is asserted here."),
]
with open("constants_table.csv", "w", newline="") as f:
    fieldnames = ["constant", "value", "role", "source", "statement_no", "hypotheses"]
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for row in constants:
        w.writerow(row)

print("constants_table.csv written:", len(constants), "rows")
