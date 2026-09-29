"""V1 steps (1)-(4) + proves-too-much object 1, on the validator's own
arithmetic (val_gf2n.py). Written before opening code/binec.py,
code/convert.py or Weil_descent.sage.

Outputs v1_certificates.json and v1_certificates.md next to this file.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from val_gf2n import (GF2n, BinaryCurve, decode_le, decode_be, summation_poly_f3,
                      GF2n_ext2, BinaryCurveExt2)

BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
HERE = os.path.dirname(os.path.abspath(__file__))


def read_info(name):
    lines = open(os.path.join(BENCH, f"INFO{name}.dimacs")).read().split("\n")
    n, l = (int(t) for t in lines[0].split())
    return {"n": n, "l": l, "modulus": lines[1].strip(), "xR": lines[2].strip(),
            "label": lines[3].strip(), "res": lines[4].strip()}


def instance_names():
    names = []
    for f in sorted(os.listdir(BENCH)):
        m = re.match(r"INFO(n\d+l\d+-\d+-[SU])\.dimacs$", f)
        if m:
            names.append(m.group(1))
    def key(s):
        m = re.match(r"n(\d+)l(\d+)-(\d+)-([SU])", s)
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return sorted(names, key=key)


FIELDS = {}
def field(n, modstr):
    if n not in FIELDS:
        FIELDS[n] = GF2n.from_info_modulus(n, modstr)
    assert FIELDS[n].mod == GF2n.from_info_modulus(n, modstr).mod
    return FIELDS[n]


def sum_x_matches(E, xs, xR):
    """Try every choice of y for each x (2 per x, 1 for x = 0); return the
    number of sign choices with x(P1+P2+P3) = xR and the number tried."""
    ys = [E.ys(x) for x in xs]
    if any(len(y) == 0 for y in ys):
        return 0, 0, "some x_i is not an x-coordinate of E(F_{2^n})"
    tried = 0
    hits = 0
    import itertools
    for choice in itertools.product(*ys):
        tried += 1
        P = None
        for x, y in zip(xs, choice):
            P = E.add(P, (x, y))
        if P is not None and P[0] == xR:
            hits += 1
    return hits, tried, None


def check_certificate(info, xs_str, xR_str, decode):
    n = info["n"]
    F = field(n, info["modulus"])
    E = BinaryCurve(F, a2=1, a6=1)
    xs = [decode(s) for s in xs_str]
    xR = decode(xR_str)
    hits, tried, why = sum_x_matches(E, xs, xR)
    f3 = summation_poly_f3(F, xs[0], xs[1], xs[2], xR)
    return {"x_hex": [hex(x) for x in xs], "xR_hex": hex(xR),
            "x_on_E": [E.ys(x) != [] for x in xs], "xR_on_E": E.ys(xR) != [],
            "x_crit": [E.x_criterion(x) for x in xs], "xR_crit": E.x_criterion(xR),
            "sign_choices_tried": tried, "sign_choices_matching": hits,
            "verified": hits > 0, "why": why, "f3": hex(f3), "f3_zero": f3 == 0}


results = {"certificates": [], "perturbed": [], "n19l6_19_U": {}}
names = instance_names()
assert len(names) == 60

# ---------------------------------------------------------------- step (1)
n_ok = 0
for name in names:
    info = read_info(name)
    if info["label"] != "S":
        continue
    xs_str = info["res"].split("-")
    assert len(xs_str) == 3 and all(len(s) == info["l"] for s in xs_str)
    assert len(info["xR"]) == info["n"]
    le = check_certificate(info, xs_str, info["xR"], decode_le)
    be = check_certificate(info, xs_str, info["xR"], decode_be)
    row = {"instance": name, "n": info["n"], "l": info["l"], "certificate": xs_str,
           "xR_bits": info["xR"], "LE": le, "BE": be}
    results["certificates"].append(row)
    n_ok += le["verified"]
    # --------------------------------------------------- proves-too-much (1)
    F = field(info["n"], info["modulus"])
    E = BinaryCurve(F, a2=1, a6=1)
    xs = [decode_le(s) for s in xs_str]
    xR = decode_le(info["xR"])
    for bit in range(info["l"]):
        pxs = [xs[0] ^ (1 << bit), xs[1], xs[2]]
        hits, tried, why = sum_x_matches(E, pxs, xR)
        f3 = summation_poly_f3(F, pxs[0], pxs[1], pxs[2], xR)
        results["perturbed"].append({"instance": name, "flipped_bit_of_x1": bit,
                                     "x1_perturbed_hex": hex(pxs[0]),
                                     "checker_accepts": hits > 0, "why_rejected": why or "no sign choice sums to x_R",
                                     "f3_zero": f3 == 0})
print("certificates verified (LE):", n_ok, "/ 30")
print("certificates verified (BE):", sum(r["BE"]["verified"] for r in results["certificates"]), "/ 30")
print("f3 = 0 on shipped (LE):", sum(r["LE"]["f3_zero"] for r in results["certificates"]), "/ 30")
pert = results["perturbed"]
print("perturbed objects:", len(pert), "accepted:", sum(p["checker_accepts"] for p in pert),
      "f3 zero:", sum(p["f3_zero"] for p in pert))
bit0 = [p for p in pert if p["flipped_bit_of_x1"] == 0]
print("  bit-0 flips (the plan's 30 objects): accepted", sum(p["checker_accepts"] for p in bit0),
      "f3 zero", sum(p["f3_zero"] for p in bit0))

# ---------------------------------------------------------------- step (2)
def parse_anf(path):
    lines = open(path).read().split("\n")
    hdr = lines[0].split()
    assert hdr[0] == "p" and hdr[1] == "cnf"
    nvars, neqs = int(hdr[2]), int(hdr[3])
    eqs = []
    for ln in lines[1:]:
        ln = ln.strip()
        if not ln:
            continue
        toks = ln.split()
        assert toks[0] == "x" and toks[-1] == "0", ln
        toks = toks[1:-1]
        terms = []
        const = 0
        i = 0
        while i < len(toks):
            t = toks[i]
            if t == "T":
                const ^= 1
                i += 1
            elif t.startswith("."):
                d = int(t[1:])
                terms.append(tuple(int(v) for v in toks[i + 1:i + 1 + d]))
                i += 1 + d
            else:
                terms.append((int(t),))
                i += 1
        eqs.append((terms, const))
    assert len(eqs) == neqs, (len(eqs), neqs)
    return nvars, eqs


def eval_anf(eqs, assign):
    """assign: dict var -> 0/1. Returns (count of lines whose XOR of all
    terms incl. T evaluates to 1, count evaluating to 0)."""
    ones = zeros = 0
    for terms, const in eqs:
        v = const
        for mono in terms:
            p = 1
            for var in mono:
                p &= assign[var]
            v ^= p
        if v:
            ones += 1
        else:
            zeros += 1
    return ones, zeros


anf_path = os.path.join(BENCH, "Xn19l6-19-U.anf")
nvars, eqs = parse_anf(anf_path)
rows = [json.loads(l) for l in open(os.path.join(RUN, "results.jsonl"))]
wd = [r for r in rows if r["instance"] == "n19l6-19-U" and r["engine"] == "wdsat"
      and r["config"] in ("default", "core_order", "symmetry", "gauss_elim")]
assert len(wd) == 4
assignments = {r["config"]: r["assignment"] for r in wd}
assert len(set(assignments.values())) == 1
A = assignments["default"]
assert len(A) == nvars == 51
assign = {i + 1: int(ch) for i, ch in enumerate(A)}
ones, zeros = eval_anf(eqs, assign)
degprof = {}
for terms, const in eqs:
    for mono in terms:
        degprof[len(mono)] = degprof.get(len(mono), 0) + 1
step2 = {"anf": "inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks/Xn19l6-19-U.anf",
         "n_vars": nvars, "n_equations": len(eqs), "monomials_by_degree": degprof,
         "wdsat_assignment": A, "assignment_identical_across_4_wdsat_configs": True,
         "lines_evaluating_to_1_(clause_true)": ones, "lines_evaluating_to_0": zeros,
         "reading": "WDSat ANF line = XOR clause that must be TRUE (README CNF-XOR semantics); "
                    "all lines evaluate to 1 under the assignment => every equation satisfied"
                    if zeros == 0 else "MIXED: assignment does not satisfy every line under either reading"}
# a random assignment as a control on the evaluator (must NOT satisfy all lines)
import random
rng = random.Random(7)
ctrl = []
for _ in range(5):
    ra = {i + 1: rng.getrandbits(1) for i in range(nvars)}
    ctrl.append(eval_anf(eqs, ra))
step2["random_assignment_control_(ones,zeros)x5"] = ctrl

# CMS model on the upstream CNF-XOR file
cms = [r for r in rows if r["instance"] == "n19l6-19-U" and r["engine"] == "cryptominisat5"][0]
assert cms["argv"][-1].endswith("upstream/benchmarks/Xn19l6-19-U.dimacs")
model = {}
for ln in open(os.path.join(RUN, cms["stdout"])):
    if ln.startswith("v "):
        for t in ln.split()[1:]:
            v = int(t)
            if v != 0:
                model[abs(v)] = 1 if v > 0 else 0
cnfx = open(os.path.join(BENCH, "Xn19l6-19-U.dimacs")).read().split("\n")
hdr = cnfx[0].split()
assert hdr[:2] == ["p", "cnf"]
nv_c, ncl = int(hdr[2]), int(hdr[3])
assert len(model) == nv_c, (len(model), nv_c)
sat_or = unsat_or = sat_x = unsat_x = 0
for ln in cnfx[1:]:
    ln = ln.strip()
    if not ln:
        continue
    toks = ln.split()
    is_x = toks[0] == "x"
    if is_x:
        toks = toks[1:]
    assert toks[-1] == "0"
    lits = [int(t) for t in toks[:-1]]
    vals = [(model[abs(v)] if v > 0 else 1 - model[abs(v)]) for v in lits]
    if is_x:
        ok = sum(vals) & 1
        sat_x += ok; unsat_x += 1 - ok
    else:
        ok = 1 if any(vals) else 0
        sat_or += ok; unsat_or += 1 - ok
core_bits_cms = "".join(str(model[i]) for i in range(1, 19))
assert core_bits_cms == cms["assignment_core_bits"]
step2["cms_model_on_upstream_cnf_xor"] = {
    "file": "inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks/Xn19l6-19-U.dimacs (UPSTREAM file per argv; not a local conversion)",
    "n_vars": nv_c, "n_clauses_declared": ncl, "or_clauses_satisfied": sat_or, "or_clauses_unsatisfied": unsat_or,
    "xor_clauses_satisfied": sat_x, "xor_clauses_unsatisfied": unsat_x,
    "core_bits_from_model_vars_1_18": core_bits_cms, "row_assignment_core_bits": cms["assignment_core_bits"]}
# CMS core bits are a permutation of the WDSat x-set; evaluate the ANF at the
# permuted core with WDSat's e-bits (e-variables are symmetric functions of x).
perm_assign = dict(assign)
for i in range(18):
    perm_assign[i + 1] = int(core_bits_cms[i])
ones_p, zeros_p = eval_anf(eqs, perm_assign)
step2["anf_at_cms_core_permutation_with_wdsat_e_bits_(ones,zeros)"] = (ones_p, zeros_p)
results["n19l6_19_U"]["step2_anf_evaluation"] = step2
print("step2:", json.dumps(step2, indent=1))

# ---------------------------------------------------------------- step (3)
info19 = read_info("n19l6-19-U")
F19 = field(19, info19["modulus"])
E19 = BinaryCurve(F19, a2=1, a6=1)
xbits = [A[0:6], A[6:12], A[12:18]]
assert xbits == wd[0]["verification"]["x_bits"]
step3 = {"x_bits_first_18_of_assignment": xbits, "xR_bits_INFO": info19["xR"]}
tab = {}
for cx, dx in (("LE", decode_le), ("BE", decode_be)):
    for cr, dr in (("LE", decode_le), ("BE", decode_be)):
        xs = [dx(b) for b in xbits]
        xR = dr(info19["xR"])
        f3 = summation_poly_f3(F19, xs[0], xs[1], xs[2], xR)
        tab[f"x:{cx} xR:{cr}"] = {"x_hex": [hex(x) for x in xs], "xR_hex": hex(xR), "f3": hex(f3), "f3_zero": f3 == 0}
step3["f3_table"] = tab
results["n19l6_19_U"]["step3_two_conventions"] = step3
print("step3:", json.dumps(step3, indent=1))

# ---------------------------------------------------------------- step (4)
conv_zero = [k for k, v in tab.items() if v["f3_zero"]]
step4 = {}
for k in ("x:LE xR:LE", "x:BE xR:BE"):
    xs = [int(h, 16) for h in tab[k]["x_hex"]]
    xR = int(tab[k]["xR_hex"], 16)
    step4[k] = {"Tr(x+1+1/x^2) for x1,x2,x3": [E19.x_criterion(x) for x in xs],
                "Tr(x+1+1/x^2) for xR": E19.x_criterion(xR),
                "x_i on E(F_2^19)": [E19.ys(x) != [] for x in xs], "xR on E(F_2^19)": E19.ys(xR) != []}
results["n19l6_19_U"]["step4_traces"] = step4
print("step4:", json.dumps(step4, indent=1))

# -------- explicit construction over F_{2^38} (beyond the plan's step list;
# used in step (6) classification): if all four x's are twist x-coordinates,
# build the points on E over F_{2^38} and check x(P1 +/- P2 +/- P3) = xR.
K = GF2n_ext2(F19)
EK = BinaryCurveExt2(K, a2=1, a6=1)
def ext_decomp(xs, xR):
    import itertools
    pts = [EK.ys_for_base_x(x) if x != 0 else [K.embed(1)] for x in xs]
    xRK = K.embed(xR)
    hits = 0; tried = 0
    for ch in itertools.product(*pts):
        tried += 1
        P = None
        for x, y in zip(xs, ch):
            P = EK.add(P, (K.embed(x), y))
        if P is not None and P[0] == xRK:
            hits += 1
    return hits, tried
ext = {}
for k in conv_zero or ["x:LE xR:LE"]:
    xs = [int(h, 16) for h in tab[k]["x_hex"]]
    xR = int(tab[k]["xR_hex"], 16)
    hits, tried = ext_decomp(xs, xR)
    ext[k] = {"sign_choices_tried": tried, "sign_choices_with_x(P1+P2+P3)=xR": hits,
              "all_points_lie_in_E(F_2^38)\\E(F_2^19)": all(E19.x_criterion(x) == 1 for x in xs + [xR])}
results["n19l6_19_U"]["explicit_F_2^38_decomposition"] = ext
print("ext:", json.dumps(ext, indent=1))

# -------- proves-too-much: the five x-sets with xR replaced by xR of n19l6-1-S
info1S = read_info("n19l6-1-S")
xR_1S = decode_le(info1S["xR"])
swap = []
for r in wd + [cms]:
    xb = r["verification"]["x_bits"]
    xs = [decode_le(b) for b in xb]
    hits, tried, why = sum_x_matches(E19, xs, xR_1S)
    ehits, etried = ext_decomp(xs, xR_1S)
    f3 = summation_poly_f3(F19, xs[0], xs[1], xs[2], xR_1S)
    swap.append({"row": (r["engine"], r["config"]), "x_bits": xb, "xR_swapped_to": info1S["xR"],
                 "E_checker_accepts": hits > 0, "F_2^38_checker_accepts": ehits > 0,
                 "f3_zero": f3 == 0})
results["n19l6_19_U"]["proves_too_much_xR_swap"] = swap
print("swap:", json.dumps(swap, indent=1))

json.dump(results, open(os.path.join(HERE, "v1_certificates.json"), "w"), indent=1)

# markdown table of the 30 certificates
with open(os.path.join(HERE, "v1_certificates.md"), "w") as f:
    f.write("| instance | x1,x2,x3 (INFO strings) | LE hex x1,x2,x3 | LE xR hex | on E | sign choices matching/tried | f3(LE) | verified | BE verified |\n")
    f.write("|---|---|---|---|---|---|---|---|---|\n")
    for r in results["certificates"]:
        le = r["LE"]
        f.write(f"| {r['instance']} | {'-'.join(r['certificate'])} | {','.join(le['x_hex'])} | {le['xR_hex']} | "
                f"{le['x_on_E']} | {le['sign_choices_matching']}/{le['sign_choices_tried']} | {le['f3']} | "
                f"{le['verified']} | {r['BE']['verified']} |\n")
print("V1_DONE")
