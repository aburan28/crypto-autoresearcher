#!/usr/bin/env python3
"""Independent re-derivation for the Semaev Boolean-parity Lean modules.

Written blind to the producer's Python (replay_ffd_semaev_20261022.py and the
generate_* scripts were NOT read).  Inputs: the field modulus, basis, x_R, a6
stated in the Lean headers / target yamls, and the literal data in the Lean
files (parsed from text, to compare constants).

Usage: python3 -I semaev_recheck.py <repo-root>
"""
import hashlib, json, re, sys, itertools

ROOT = sys.argv[1]
FORMAL = ROOT + "/formal/CryptoResearch/Semaev/"
out = {}

# ---------- F16 = F2[X]/(X^4+X+1) ----------
MOD = 0b10011
def gm(a, b):
    r = 0
    for i in range(4):
        if (b >> i) & 1:
            r ^= a << i
    for i in (6, 5, 4):
        if (r >> i) & 1:
            r ^= MOD << (i - 4)
    return r
BASIS = [9, 3, 2, 12]
XR, A6 = 1, 1

def S3(x1, x2, x3):
    # binary-curve third summation polynomial y^2+xy=x^3+a2x^2+a6:
    # (x1x2+x1x3+x2x3)^2 + x1x2x3 + a6
    e2 = gm(x1, x2) ^ gm(x1, x3) ^ gm(x2, x3)
    return gm(e2, e2) ^ gm(gm(x1, x2), x3) ^ A6

def val(assign, off):
    v = 0
    for i in range(4):
        if (assign >> (off + i)) & 1:
            v ^= BASIS[i]
    return v

# truth table of each output bit, then ANF (Moebius transform) -> unique
# squarefree Boolean polynomial
anf_eqs = []
for bit in range(4):
    tt = [(S3(val(a, 0), val(a, 4), XR) >> bit) & 1 for a in range(256)]
    f = tt[:]
    for i in range(8):
        for a in range(256):
            if (a >> i) & 1:
                f[a] ^= f[a ^ (1 << i)]
    anf_eqs.append(sorted(m for m in range(256) if f[m]))

src = open(FORMAL + "BooleanParityFiniteCertificate.lean").read()
m = re.search(r"def equations : List \(List Nat\) :=\s*(\[\[.*?\]\])", src, re.S)
lean_eqs = json.loads(m.group(1).replace("\n", ""))
out["anf_derived_equations"] = anf_eqs
out["lean_equations_equal_anf_derivation"] = [sorted(e) for e in lean_eqs] == anf_eqs
# canonical JSON hash candidates
cands = {
    "compact": json.dumps(lean_eqs, separators=(",", ":")),
    "default": json.dumps(lean_eqs),
    "sorted_compact": json.dumps(lean_eqs, separators=(",", ":"), sort_keys=True),
}
out["equation_hash_candidates"] = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in cands.items()}
out["claimed_hash"] = "89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb"
out["claimed_hash_matched_by"] = [k for k, h in out["equation_hash_candidates"].items() if h == out["claimed_hash"]]

# ---------- Boolean ring rows ----------
def popc(x): return bin(x).count("1")
def mul_xor(f, mono):
    r = 0
    for t in f:
        r ^= 1 << (t | mono)
    return r
def mul_or(f, mono):
    r = 0
    for t in f:
        r |= 1 << (t | mono)
    return r
def deg_of_row(row):
    return max((popc(i) for i in range(256) if (row >> i) & 1), default=-1)
def rows_for(D, mult):
    rs = []
    for f in lean_eqs:
        for mono in range(256):
            p = mult(f, mono)
            if deg_of_row(p) <= D:
                rs.append(p)
    return rs
def gf2_rank(rows):
    basis = {}  # pivot (highest bit) -> row
    r = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                r += 1
                break
    return r
def mask_deg(pred):
    return sum(1 << i for i in range(256) if pred(popc(i)))
def proj(rows, D):
    msk = mask_deg(lambda d: d == D)
    return [r & msk for r in rows]

prof = {}
for sem, mult in (("xor", mul_xor), ("or", mul_or)):
    p = {}
    for D in range(0, 4):
        rs = rows_for(D, mult)
        p[D] = dict(rows=len(rs), rank=gf2_rank(rs), projected_rank=gf2_rank(proj(rs, D)))
    for D in range(1, 4):
        p[D]["new_falls_int"] = p[D]["rank"] - p[D]["projected_rank"] - p[D - 1]["rank"]
    prof[sem] = p
out["profiles"] = prof

# subspace inclusions behind the filtration reading (XOR semantics)
def in_span(basis_rows, v):
    return gf2_rank(basis_rows + [v]) == gf2_rank(basis_rows)
r1, r2, r3 = rows_for(1, mul_xor), rows_for(2, mul_xor), rows_for(3, mul_xor)
out["rows1_subset_rows2_as_list"] = all(r in r2 for r in r1)
out["rows2_subset_rows3_as_list"] = all(r in r3 for r in r2)
out["rows3_no_support_above_3"] = all(deg_of_row(r) <= 3 for r in r3)
# dim(V_D intersect R_{<=D-1}) by direct kernel computation (not rank difference):
def low_intersection_dim(rows, D):
    # vectors in span(rows) with zero degree-D (and higher) part
    hi = mask_deg(lambda d: d >= D)
    # Gaussian elimination prioritising high columns
    piv = []
    for v in rows:
        for (pc, pr) in piv:
            if (v >> pc) & 1:
                v ^= pr
        if v:
            hv = v & hi
            col = (hv.bit_length() - 1) if hv else (v.bit_length() - 1)
            # re-reduce existing pivots on col
            piv = [(pc, pr ^ v) if (pr >> col) & 1 else (pc, pr) for (pc, pr) in piv]
            piv.append((col, v))
    lows = [pr for (pc, pr) in piv if not ((pr & hi))]
    return gf2_rank(lows), lows
d2, low2 = low_intersection_dim(r2, 2)
d3, low3 = low_intersection_dim(r3, 3)
out["dim_V2_cap_R_le1"] = d2
out["dim_V3_cap_R_le2"] = d3
out["V1_subset_V2capRle1"] = all(in_span(low2, v) for v in r1)
out["V2_subset_V3capRle2"] = all(in_span(low3, v) for v in r2 if v)
new = [v for v in low3 if not in_span(r2, v)]
out["explicit_new_vector_in_V3capRle2_not_in_V2"] = (hex(new[0]) if new else None)
out["explicit_new_vector_monomials"] = ([i for i in range(256) if (new[0] >> i) & 1] if new else None)

# archived product witness
first = lean_eqs[0]
a, b = mul_or(first, 1), mul_xor(first, 1)
out["archived_extra_masks"] = [i for i in range(256) if ((a ^ b) >> i) & 1]
# truth-table disagreement of archived OR product with f*u0
def ev(row, x):
    return sum((row >> mono) & 1 for mono in range(256) if (mono & x) == mono) & 1
def evpoly(f, x):
    return sum(1 for t in f if (t & x) == t) & 1
dis_or = sum(1 for x in range(256) if ev(a, x) != (evpoly(first, x) & (x & 1)))
dis_xor = sum(1 for x in range(256) if ev(b, x) != (evpoly(first, x) & (x & 1)))
out["archived_truth_table_disagreements"] = dis_or
out["parity_truth_table_disagreements"] = dis_xor

# literal rows in the semantic certificates
def parse_list(text, ns, name):
    blk = text.split("namespace " + ns + "\n", 1)[1].split("end " + ns, 1)[0]
    mm = re.search(r"private def " + name + r" : List Nat := (\[[^\]]*\])", blk)
    return json.loads(mm.group(1))
sem2 = open(FORMAL + "BooleanParitySemanticRankCertificate.lean").read()
sem3 = open(FORMAL + "BooleanParityDegreeThreeRankCertificate.lean").read()
lit = {
    "one": parse_list(sem2, "one", "literalRows"),
    "two": parse_list(sem2, "two", "literalRows"),
    "twoProjected": parse_list(sem2, "twoProjected", "literalRows"),
    "three": parse_list(sem3, "three", "literalRows"),
    "threeProjected": parse_list(sem3, "threeProjected", "literalRows"),
}
expect = {
    "one": r1, "two": r2, "twoProjected": proj(r2, 2),
    "three": r3, "threeProjected": proj(r3, 3),
}
out["literal_rows_match"] = {k: lit[k] == expect[k] for k in lit}
out["literal_rows_ranks"] = {k: gf2_rank(v) for k, v in lit.items()}

# check the elimination certificates numerically: V*U = I, U*A rows, pivots
def check_cert(text, ns, nrows):
    U = parse_list(text, ns, "Urows"); V = parse_list(text, ns, "Vrows")
    A = parse_list(text, ns, "literalRows")
    blk = text.split("namespace " + ns + "\n", 1)[1].split("end " + ns, 1)[0]
    pv = re.search(r"private def pivots : List \(WithTop \(Fin 256\)\) := \[(.*?)\]\n", blk).group(1)
    piv = [None if t.strip() == "⊤" else int(re.search(r"\(\((\d+) :", t).group(1))
           for t in re.split(r",\s*(?=\(\(|⊤)", pv)]
    def mat_mul_rows(Lrows, Rrows):  # L (n x n) bit-rows times R rows
        res = []
        for lr in Lrows:
            acc = 0
            for k in range(len(Rrows)):
                if (lr >> k) & 1:
                    acc ^= Rrows[k]
            res.append(acc)
        return res
    VU = mat_mul_rows(V, U)
    ident = VU == [1 << i for i in range(nrows)]
    E = mat_mul_rows(U, A)
    # pivot semantics assumed: pivot i = least column with nonzero entry, None for zero row;
    # pivot columns strictly increasing over nonzero rows; zero rows after nonzero rows
    ok = True
    lowbit = [((r & -r).bit_length() - 1) if r else None for r in E]
    ok &= lowbit == piv
    nz = [p for p in piv if p is not None]
    ok &= nz == sorted(set(nz))
    first_none = piv.index(None) if None in piv else len(piv)
    ok &= all(p is None for p in piv[first_none:])
    # reduced? pivot columns zero in other rows
    red = all(((E[j] >> p) & 1) == 0 for i, p in enumerate(piv) if p is not None for j in range(len(E)) if j != i)
    return dict(n=nrows, VU_identity=ident, pivots_are_lowest_set_bits_increasing=bool(ok),
                reduced_echelon=red, pivot_count=len(nz), rank_E=gf2_rank(E))
out["elimination_certificates"] = {
    "one": check_cert(sem2, "one", 17), "two": check_cert(sem2, "two", 28),
    "twoProjected": check_cert(sem2, "twoProjected", 28),
    "three": check_cert(sem3, "three", 80), "threeProjected": check_cert(sem3, "threeProjected", 80),
}
# Erows for degree three
for ns in ("three", "threeProjected"):
    U = parse_list(sem3, ns, "Urows"); A = parse_list(sem3, ns, "literalRows"); E = parse_list(sem3, ns, "Erows")
    calc = []
    for lr in U:
        acc = 0
        for k in range(80):
            if (lr >> k) & 1:
                acc ^= A[k]
        calc.append(acc)
    out["elimination_certificates"][ns]["Erows_equal_U_times_A"] = calc == E

# FiniteEquationSemantics: direct S3 vs packed component values
def descended(x):
    v = 0
    for bit, f in enumerate(lean_eqs):
        v ^= evpoly(f, x) << bit
    return v
out["finite_equation_semantics_all_256"] = all(descended(x) == S3(val(x, 0), val(x, 4), XR) for x in range(256))
# negative control: wrong a6 or wrong x_R must break it
A6 = 0
out["neg_control_a6_0_breaks"] = not all(descended(x) == S3(val(x, 0), val(x, 4), XR) for x in range(256))
A6 = 1
out["neg_control_xR_2_breaks"] = not all(descended(x) == S3(val(x, 0), val(x, 4), 2) for x in range(256))

# draws.json data binding
d = json.load(open(ROOT + "/docs/reports/2026-10-22-semaev-first-fall-replay/evidence/draws.json"))
rec = [r for r in d["draws"] if r["n"] == 4 and r["nprime"] == 4 and r["draw"] == 1][0]
out["draws_json_record"] = {k: rec[k] for k in ("seed", "xR", "basis", "equations_sha256", "first_fall", "degree_3", "boolean_parity_profile")}
out["draws_json_equations_equal_lean"] = rec["equations"] == lean_eqs
out["curve_model"] = d["curve_model"]
print(json.dumps(out, indent=1, default=str))
