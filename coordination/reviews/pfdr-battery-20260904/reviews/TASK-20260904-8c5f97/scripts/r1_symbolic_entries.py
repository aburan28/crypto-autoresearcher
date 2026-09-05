"""R1(a): independent symbolic audit of the Stage 0 entry table.

Expands S_3(ell_1, ell_2, x_R) over Z[A, B, x_R] with sympy (own expression for
S_3, not harness.semaev), reduces a_i^2 -> a_i, and reports: entry count, the
maximum total degree of an entry in (A, B, x_R), the integer content of the row,
the content of the degree-4 (top) part, and whether the top part is
parameter-free and equal to 16 Q_1 Q_2.  Also prints the number of maximal
minors at D = 6, which is what the ledger record's "product of the nonzero
maximal minors" degree bound would have to multiply.
"""
import json, math, os
import sympy

a = sympy.symbols("a0:6")
A, Bc, XR = sympy.symbols("A B x_R")
ell1 = a[0] + 2 * a[1] + 4 * a[2]
ell2 = a[3] + 2 * a[4] + 4 * a[5]
S3 = ((ell1 - ell2) ** 2 * XR ** 2
      - 2 * ((ell1 + ell2) * (ell1 * ell2 + A) + 2 * Bc) * XR
      + (ell1 * ell2 - A) ** 2 - 4 * Bc * (ell1 + ell2))
poly = sympy.Poly(sympy.expand(S3), *a)
entries = {}
for monom, coeff in poly.terms():
    key = frozenset(i for i, e in enumerate(monom) if e > 0)      # a^2 -> a
    entries[key] = sympy.expand(entries.get(key, 0) + coeff)
entries = {k: v for k, v in entries.items() if v != 0}

degs, contents, all_coeffs = {}, {}, []
for k, v in entries.items():
    pv = sympy.Poly(v, A, Bc, XR)
    cs = [int(c) for c in pv.coeffs()]
    all_coeffs.extend(cs)
    degs[len(k)] = max(degs.get(len(k), 0), pv.total_degree())
    contents[len(k)] = math.gcd(contents.get(len(k), 0), math.gcd(*cs) if len(cs) > 1 else abs(cs[0]))

top = {k: v for k, v in entries.items() if len(k) == 4}
Q1 = {frozenset({0, 1}): 1, frozenset({0, 2}): 2, frozenset({1, 2}): 4}
Q2 = {frozenset({3, 4}): 1, frozenset({3, 5}): 2, frozenset({4, 5}): 4}
pred = {}
for m1, c1 in Q1.items():
    for m2, c2 in Q2.items():
        pred[m1 | m2] = 16 * c1 * c2
res = {
    "n_entries": len(entries),
    "max_total_degree_in_A_B_xR_per_entry_degree": {str(k): v for k, v in sorted(degs.items())},
    "integer_content_per_entry_degree": {str(k): v for k, v in sorted(contents.items())},
    "row_content_gcd": math.gcd(*all_coeffs),
    "top_degree4_entries_are_parameter_free": all(sympy.Poly(v, A, Bc, XR).total_degree() == 0 for v in top.values()),
    "top_degree4_equals_16_Q1_Q2": {("*".join(f"a{i}" for i in sorted(k))): int(v) for k, v in sorted(top.items(), key=lambda kv: sorted(kv[0]))} ==
                                   {("*".join(f"a{i}" for i in sorted(k))): int(v) for k, v in sorted(pred.items(), key=lambda kv: sorted(kv[0]))},
    "stage0_claimed": {"n_entries": 49, "max_param_degree": 2, "content_D4": 1},
    "maximal_minor_count_at_D6": math.comb(64, 15),
    "product_of_minors_degree_bound_at_D6": 30 * math.comb(64, 15),
    "single_minor_degree_bound_at_D6": 30,
}
print(json.dumps(res, indent=1))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out",
                       "r1_symbolic_entries.json"), "w") as fh:
    json.dump(res, fh, indent=1, sort_keys=True)
