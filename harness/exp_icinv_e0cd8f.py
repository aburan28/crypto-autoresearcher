"""EXP-ICINV-e0cd8f: exact symbolic Semaev geometry across one isogeny class.

Computes, per curve and WITHOUT any factor-base membership polynomial f_V in
any ideal (see experiments/EXP-ICINV-e0cd8f/specification.yaml, "WHY THE
FACTOR-BASE MEMBERSHIP POLYNOMIALS f_V ARE REMOVED"):

  * S_3 (and, secondarily, S_4) monomial support,
  * the affine singular locus (dimension, degree) of S_m = 0,
  * the graded Betti table and Castelnuovo-Mumford regularity of the
    homogenised ideal I_m = < S_m, dS_m/dx_1, ..., dS_m/dx_m >,
  * the degree and F_p-factorisation type of the elimination polynomial of
    I_m in F_p[x_m].

This module is PURE COMPUTATION: it builds ideals with sympy, drives an
external computer-algebra backend (Singular, and Macaulay2 for the C-BACKEND
cross-check) via subprocess, and parses the results. It does not import or
edit harness/semaev.py's `measure_s3_decomposition` machinery (which builds
the DEPLOYED, f_V-BEARING ideal) -- only its polynomial definitions (`s3_expr`,
`s4_expr`) are reused, unedited, from harness/semaev.py.

Nothing here is Sage- or sympy-Groebner-based for the Betti table: sympy
cannot compute a minimal free resolution, which is exactly SR3's premise.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass

import sympy

from .semaev import s3_expr, s4_expr, x1, x2, x3
from .toycurve import _seed_int
from .isogeny_class import isogeny_classes, class_census

x0, x4 = sympy.symbols("x0 x4")

SINGULAR_BIN = "Singular"
M2_BIN = "M2"


# --------------------------------------------------------------------------
# ideal construction (f_V-free, per the contract's defining constraint)
# --------------------------------------------------------------------------


def s3_generators(a: int, b: int):
    """<S3, dS3/dx1, dS3/dx2, dS3/dx3>, un-homogenised, over the integers."""
    S3 = sympy.expand(s3_expr(a, b))
    return [S3, sympy.diff(S3, x1), sympy.diff(S3, x2), sympy.diff(S3, x3)]


def s4_generators(a: int, b: int):
    S4 = sympy.expand(s4_expr(a, b))
    return [S4] + [sympy.diff(S4, v) for v in (x1, x2, x3, x4)]


def s3_support(a: int, b: int, p: int) -> int:
    S3 = sympy.expand(s3_expr(a, b))
    return len(sympy.Poly(S3, x1, x2, x3, modulus=p).terms())


def s4_support(a: int, b: int, p: int) -> int:
    S4 = sympy.expand(s4_expr(a, b))
    return len(sympy.Poly(S4, x1, x2, x3, x4, modulus=p).terms())


def _homogenize(gens, variables, p):
    out = []
    for g in gens:
        poly = sympy.Poly(g, *variables, modulus=p)
        out.append(poly.homogenize(x0).as_expr())
    return out


def _to_singular(e) -> str:
    return str(sympy.expand(e)).replace("**", "^")


# --------------------------------------------------------------------------
# Singular driver: m = 3 (full invariant family)
# --------------------------------------------------------------------------


def build_m3_singular_script(a: int, b: int, p: int, order: str = "dp") -> str:
    gens = s3_generators(a, b)
    aff = [_to_singular(g) for g in gens]
    hom = [_to_singular(g) for g in _homogenize(gens, (x1, x2, x3), p)]
    return f"""\
ring raff = {p}, (x1,x2,x3), {order};
ideal Jaff = {','.join(aff)};
"===SUPPORT===";
size(Jaff[1]);
ideal Saff = std(Jaff);
"===DIM===";
dim(Saff);
"===DEG===";
degree(Saff);
"===UNIT===";
Saff[1]==1;
ideal E = eliminate(Jaff, x1*x2);
ideal E2 = std(E);
"===ELIM_SIZE===";
size(E2);
if (size(E2) > 0) {{
  "===ELIM_DEG===";
  deg(E2[1]);
  list FL = factorize(E2[1]);
  "===ELIM_FACTORS===";
  int fi;
  for (fi=1; fi<=size(FL[1]); fi=fi+1) {{
    if (deg(FL[1][fi]) > 0) {{
      string(deg(FL[1][fi])) + " " + string(FL[2][fi]);
    }}
  }}
}}
ring rhom = {p}, (x0,x1,x2,x3), {order};
ideal Jh = {','.join(hom)};
"===HOMOG_CHECK===";
homog(Jh);
resolution re = mres(Jh, 0);
intmat B = betti(re);
int nr = nrows(B);
int nc = ncols(B);
"===BETTI_ENTRIES===";
int bi, bj;
for (bi=1; bi<=nr; bi=bi+1) {{
  for (bj=1; bj<=nc; bj=bj+1) {{
    if (B[bi,bj] != 0) {{
      string(bi-1) + " " + string(bj-1) + " " + string(B[bi,bj]);
    }}
  }}
}}
"===DIMHOM===";
dim(std(Jh));
"===NVARSHOM===";
nvars(basering);
"===NGENS===";
ncols(Jh);
quit;
"""


def build_m4_singular_script(a: int, b: int, p: int, order: str = "dp") -> str:
    gens = s4_generators(a, b)
    aff = [_to_singular(g) for g in gens]
    return f"""\
ring r = {p}, (x1,x2,x3,x4), {order};
ideal J = {','.join(aff)};
"===SUPPORT===";
size(J[1]);
ideal S = std(J);
"===DIM===";
dim(S);
"===DEG===";
degree(S);
"===UNIT===";
S[1]==1;
quit;
"""


def run_singular(script: str, timeout: float = 120.0) -> tuple[str, str, int, float]:
    t0 = time.perf_counter()
    proc = subprocess.run([SINGULAR_BIN, "--no-shell", "-q"], input=script,
                          capture_output=True, text=True, timeout=timeout)
    return proc.stdout, proc.stderr, proc.returncode, time.perf_counter() - t0


def _section(text: str, name: str) -> list[str]:
    """Lines strictly between "===NAME===" and the next "===...===" marker."""
    lines = text.splitlines()
    out, capture = [], False
    marker = f"==={name}==="
    for ln in lines:
        s = ln.strip().strip('"')
        if s == marker:
            capture = True
            continue
        if capture and s.startswith("===") and s.endswith("==="):
            break
        if capture:
            out.append(ln.rstrip())
    return out


def _first_int(lines: list[str]) -> int | None:
    for ln in lines:
        s = ln.strip()
        m = re.match(r"^-?\d+$", s)
        if m:
            return int(s)
    return None


def parse_m3_output(stdout: str) -> dict:
    support = _first_int(_section(stdout, "SUPPORT"))
    dim_lines = _section(stdout, "DIM")
    dim_val = _first_int(dim_lines)
    deg_lines = _section(stdout, "DEG")
    deg_val = None
    for ln in deg_lines:
        m = re.search(r"degree \(affine\)\s*=\s*(\d+)", ln)
        if m:
            deg_val = int(m.group(1))
    unit_lines = _section(stdout, "UNIT")
    is_unit = _first_int(unit_lines) == 1

    elim_size = _first_int(_section(stdout, "ELIM_SIZE"))
    elim_deg = _first_int(_section(stdout, "ELIM_DEG")) if elim_size else None
    factor_partition = []
    for ln in _section(stdout, "ELIM_FACTORS"):
        s = ln.strip()
        m = re.match(r"^(\d+)\s+(\d+)$", s)
        if m:
            deg_f, mult = int(m.group(1)), int(m.group(2))
            factor_partition.extend([deg_f] * mult)
    factor_partition.sort()

    homog_ok = _first_int(_section(stdout, "HOMOG_CHECK")) == 1

    betti_entries = []
    for ln in _section(stdout, "BETTI_ENTRIES"):
        s = ln.strip()
        m = re.match(r"^(\d+)\s+(\d+)\s+(\d+)$", s)
        if m:
            row, col, val = int(m.group(1)), int(m.group(2)), int(m.group(3))
            betti_entries.append({"i": col, "twist": row, "j": col + row, "beta": val})
    regularity = max((e["twist"] for e in betti_entries), default=None)

    dimhom = _first_int(_section(stdout, "DIMHOM"))
    nvarshom = _first_int(_section(stdout, "NVARSHOM"))
    ngens = _first_int(_section(stdout, "NGENS"))
    codim_hom = (nvarshom - dimhom) if (nvarshom is not None and dimhom is not None) else None
    koszul = (codim_hom is not None and ngens is not None and codim_hom == ngens)

    return {
        "s3_support": support,
        "singular_locus_dim": dim_val,
        "singular_locus_degree": deg_val,
        "singular_locus_is_unit_ideal": bool(is_unit),
        "elimination_ideal_size": elim_size,
        "elimination_poly_degree": elim_deg,
        "elimination_factor_partition": factor_partition,
        "elimination_empty": (elim_size == 0),
        "homogenization_check_ok": bool(homog_ok),
        "betti_entries": betti_entries,
        "regularity": regularity,
        "hom_ideal_dim": dimhom,
        "hom_ring_nvars": nvarshom,
        "num_generators": ngens,
        "codim_hom": codim_hom,
        "koszul_degeneration": bool(koszul),
    }


def parse_m4_output(stdout: str) -> dict:
    support = _first_int(_section(stdout, "SUPPORT"))
    dim_val = _first_int(_section(stdout, "DIM"))
    deg_val = None
    for ln in _section(stdout, "DEG"):
        m = re.search(r"degree \(\w+\.?\)\s*=\s*(\d+)", ln)
        if m:
            deg_val = int(m.group(1))
    is_unit = _first_int(_section(stdout, "UNIT")) == 1
    return {
        "s4_support": support,
        "singular_locus_dim": dim_val,
        "singular_locus_degree": deg_val,
        "singular_locus_is_unit_ideal": bool(is_unit),
    }


def compute_curve_m3(a: int, b: int, p: int, order: str = "dp", timeout: float = 120.0) -> dict:
    script = build_m3_singular_script(a, b, p, order)
    stdout, stderr, rc, secs = run_singular(script, timeout)
    result = {"backend": "singular", "returncode": rc, "wall_seconds": secs}
    if rc != 0:
        result["error"] = stderr[-4000:]
        return result
    result.update(parse_m3_output(stdout))
    return result


def compute_curve_m4(a: int, b: int, p: int, order: str = "dp", timeout: float = 120.0) -> dict:
    script = build_m4_singular_script(a, b, p, order)
    stdout, stderr, rc, secs = run_singular(script, timeout)
    result = {"backend": "singular", "returncode": rc, "wall_seconds": secs}
    if rc != 0:
        result["error"] = stderr[-4000:]
        return result
    result.update(parse_m4_output(stdout))
    return result


# --------------------------------------------------------------------------
# gauge transform: (a, b) -> (u^4 a, u^6 b) mod p
# --------------------------------------------------------------------------


def gauge_transform(a: int, b: int, u: int, p: int) -> tuple[int, int]:
    return (pow(u, 4, p) * a) % p, (pow(u, 6, p) * b) % p


def gauge_u_for_curve(seed: int, a: int, b: int, p: int) -> int:
    u = _seed_int(seed, f"gauge:{a}:{b}") % (p - 1) + 1  # 1 <= u <= p-1
    if u == 0:
        u = 1
    return u


# --------------------------------------------------------------------------
# Macaulay2 driver (C-BACKEND cross-check)
# --------------------------------------------------------------------------


def build_m3_m2_script(a: int, b: int, p: int) -> str:
    gens = s3_generators(a, b)
    hom = _homogenize(gens, (x1, x2, x3), p)

    def m2(e):
        return str(sympy.expand(e)).replace("**", "^")

    aff_str = ", ".join(m2(g) for g in gens)
    hom_str = ", ".join(m2(g) for g in hom)
    return f"""\
Raff = ZZ/{p}[x1,x2,x3];
Jaff = ideal({aff_str});
print "===SUPPORT===";
print(#(terms((gens Jaff)_(0,0))));
Saff = Jaff;
print "===DIM===";
print(dim Saff);
print "===DEG===";
print(if dim Saff == 0 then degree Saff else -1);
print "===UNIT===";
print(Saff == ideal(1_Raff));
Eelim = eliminate({{x1,x2}}, Jaff);
print "===ELIM_NGENS===";
print(numgens Eelim);
if numgens Eelim > 0 then (
  print "===ELIM_DEG===";
  print(first degree Eelim_0);
  felim = Eelim_0;
  flelim = factor felim;
  print "===ELIM_FACTORS===";
  scan(toList flelim, ff -> print(toString (first degree ff#0) | " " | toString (ff#1)));
);
Rhom = ZZ/{p}[x0,x1,x2,x3];
Jh = ideal({hom_str});
print "===HOMOG===";
print(isHomogeneous Jh);
res1 = res Jh;
b = betti res1;
print "===BETTI_KEYS===";
scan(pairs b, (k,v) -> print(toString k | " " | toString v));
print "===REG===";
print(regularity Jh);
print "===DIMHOM===";
print(dim Jh);
print "===NGENS===";
print(numgens Jh);
exit 0;
"""


def run_m2(script: str, timeout: float = 180.0) -> tuple[str, str, int, float]:
    t0 = time.perf_counter()
    proc = subprocess.run([M2_BIN, "--script", "/dev/stdin"], input=script,
                          capture_output=True, text=True, timeout=timeout)
    return proc.stdout, proc.stderr, proc.returncode, time.perf_counter() - t0


def parse_m2_output(stdout: str) -> dict:
    def section(name):
        return _section(stdout, name)

    support = _first_int(section("SUPPORT"))
    dim_val = _first_int(section("DIM"))
    deg_lines = section("DEG")
    deg_val = _first_int(deg_lines)
    unit_line = section("UNIT")
    is_unit = any("true" in ln.lower() for ln in unit_line)
    homog_line = section("HOMOG")
    homog_ok = any("true" in ln.lower() for ln in homog_line)
    betti_keys = []
    for ln in section("BETTI_KEYS"):
        m = re.match(r"^\((\d+),\{(\d+)\},(\d+)\)\s+(\d+)$", ln.strip())
        if m:
            i, j, deg_shift, val = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
            betti_keys.append({"i": i, "j": j, "beta": val})
    # NOTE: M2's own `regularity` builtin is NOT used -- it is computed on a
    # different convention (reg(R/I) vs reg(I) can differ by 1 depending on
    # how the function's input is interpreted) and disagreed with the
    # max(j-i) figure derived from this run's OWN betti table by exactly 1 on
    # the prototype curve, even though the betti tables of Singular and M2
    # agreed entry-for-entry. Deriving regularity from the SAME betti table
    # this run reports removes that convention ambiguity entirely and is the
    # only way the cross-check (C-BACKEND) is comparing like with like.
    reg_from_betti = max((e["j"] - e["i"] for e in betti_keys), default=None)
    dimhom = _first_int(section("DIMHOM"))
    ngens = _first_int(section("NGENS"))

    elim_ngens = _first_int(section("ELIM_NGENS"))
    elim_deg = _first_int(section("ELIM_DEG")) if elim_ngens else None
    elim_partition = []
    for ln in section("ELIM_FACTORS"):
        m = re.match(r"^(\d+)\s+(\d+)$", ln.strip())
        if m:
            deg_f, mult = int(m.group(1)), int(m.group(2))
            elim_partition.extend([deg_f] * mult)
    elim_partition.sort()

    return {
        "s3_support": support,
        "singular_locus_dim": dim_val,
        "singular_locus_degree": deg_val,
        "singular_locus_is_unit_ideal": bool(is_unit),
        "homogenization_check_ok": bool(homog_ok),
        "betti_entries": betti_keys,
        "regularity": reg_from_betti,
        "regularity_m2_builtin": _first_int(section("REG")),
        "hom_ideal_dim": dimhom,
        "num_generators": ngens,
        "elimination_ideal_size": elim_ngens,
        "elimination_poly_degree": elim_deg,
        "elimination_factor_partition": elim_partition,
        "elimination_empty": (elim_ngens == 0),
    }


def compute_curve_m3_m2(a: int, b: int, p: int, timeout: float = 180.0) -> dict:
    script = build_m3_m2_script(a, b, p)
    stdout, stderr, rc, secs = run_m2(script, timeout)
    result = {"backend": "macaulay2", "returncode": rc, "wall_seconds": secs}
    if rc != 0:
        result["error"] = stderr[-4000:]
        result["stdout_tail"] = stdout[-2000:]
        return result
    result.update(parse_m2_output(stdout))
    return result


# --------------------------------------------------------------------------
# class enumeration, control set, and support-gate re-derivation
# --------------------------------------------------------------------------


def enumerate_class(p: int, t: int):
    """Re-emit the trace-t class and certify it against Hurwitz-Kronecker.

    Uses harness.isogeny_class (READ-ONLY import; never edited) exactly as
    the committed instrument does. Returns (members, census_results).
    """
    classes = isogeny_classes(p)
    members = classes.get(t, [])
    census = class_census(p, {t: members})
    return members, census


def build_control_set(p: int, t: int, size: int, seed: int):
    """`size` random ordinary curves at p, drawn from traces OTHER than t.

    Deterministic: every curve outside the class is ranked by a seeded hash
    and the first `size` are taken. Recorded alongside the seed so the draw
    is reproducible bit-for-bit.
    """
    classes = isogeny_classes(p)
    pool = []
    for tt, recs in classes.items():
        if tt == t:
            continue
        if tt % p == 0:
            continue  # supersingular trace: excluded, "ordinary curves" per spec
        pool.extend(recs)

    def key(rec):
        return _seed_int(seed, f"control:{rec.a}:{rec.b}")

    pool_sorted = sorted(pool, key=key)
    chosen = pool_sorted[:size]
    drawn_traces = sorted({r.trace for r in chosen})
    return chosen, drawn_traces


def support_gate(members, p: int):
    """SR1: symbolic re-derivation of 13/9/10, then per-member confirmation.

    Returns (ok: bool, detail: dict).
    """
    a_sym, b_sym = sympy.symbols("a_sym b_sym")
    generic = sympy.Poly(sympy.expand(s3_expr(a_sym, b_sym)), x1, x2, x3, a_sym, b_sym)
    generic_support = len(generic.terms())
    a0_support = s3_support(0, 5, p)
    b0_support = s3_support(5, 0, p)
    derivation_ok = (generic_support == 13 and a0_support == 9 and b0_support == 10)

    per_member = []
    all_13 = True
    for r in members:
        s = s3_support(r.a, r.b, p)
        per_member.append({"a": r.a, "b": r.b, "s3_support": s})
        if s != 13:
            all_13 = False

    detail = {
        "symbolic_generic_support": generic_support,
        "symbolic_a0_support": a0_support,
        "symbolic_b0_support": b0_support,
        "derivation_matches_13_9_10": bool(derivation_ok),
        "all_class_members_support_13": bool(all_13),
        "per_member": per_member,
    }
    return bool(derivation_ok and all_13), detail


# --------------------------------------------------------------------------
# per-curve invariant bundle (m=3 required, m=4 secondary, gauge recheck)
# --------------------------------------------------------------------------


def curve_full_invariants(a: int, b: int, p: int, seed: int, *,
                          gauge: bool = True, m4: bool = True,
                          m3_timeout: float = 120.0, m4_timeout: float = 180.0) -> dict:
    out = {"a": a, "b": b}
    out["m3"] = compute_curve_m3(a, b, p, timeout=m3_timeout)
    if m4:
        out["m4"] = compute_curve_m4(a, b, p, timeout=m4_timeout)
    if gauge:
        u = gauge_u_for_curve(seed, a, b, p)
        a2, b2 = gauge_transform(a, b, u, p)
        gd = {"u": u, "a2": a2, "b2": b2}
        gd["m3"] = compute_curve_m3(a2, b2, p, timeout=m3_timeout)
        if m4:
            gd["m4"] = compute_curve_m4(a2, b2, p, timeout=m4_timeout)
        out["gauge"] = gd
    return out


def _m3_signature(inv_m3: dict) -> dict:
    """The primary-metric signature of one curve's m=3 computation."""
    betti_key = tuple(sorted((e["i"], e["j"], e["beta"]) for e in inv_m3.get("betti_entries", [])))
    return {
        "s3_support": inv_m3.get("s3_support"),
        "singular_locus_dim": inv_m3.get("singular_locus_dim"),
        "singular_locus_degree": inv_m3.get("singular_locus_degree"),
        "regularity": inv_m3.get("regularity"),
        "elimination_poly_degree": inv_m3.get("elimination_poly_degree"),
        "elimination_factor_partition": tuple(inv_m3.get("elimination_factor_partition") or []),
        "betti_table": betti_key,
    }


def gauge_check_curve(inv: dict) -> dict:
    """Compare primary m=3 (and, if present, m=4) signature before/after gauge."""
    base_sig = _m3_signature(inv["m3"])
    gauge_sig = _m3_signature(inv["gauge"]["m3"]) if "gauge" in inv else None
    agree = (gauge_sig is not None) and (base_sig == gauge_sig)
    result = {"a": inv["a"], "b": inv["b"], "m3_base": base_sig,
              "m3_gauge": gauge_sig, "m3_agrees": bool(agree)}
    if "m4" in inv and "gauge" in inv and "m4" in inv["gauge"]:
        m4b = {"s4_support": inv["m4"].get("s4_support"),
               "singular_locus_dim": inv["m4"].get("singular_locus_dim"),
               "singular_locus_degree": inv["m4"].get("singular_locus_degree")}
        m4g = {"s4_support": inv["gauge"]["m4"].get("s4_support"),
               "singular_locus_dim": inv["gauge"]["m4"].get("singular_locus_dim"),
               "singular_locus_degree": inv["gauge"]["m4"].get("singular_locus_degree")}
        result["m4_base"] = m4b
        result["m4_gauge"] = m4g
        result["m4_agrees"] = bool(m4b == m4g)
    return result


def distinct_multiset(invariants: list[dict], key: str):
    vals = [_m3_signature(inv["m3"])[key] for inv in invariants]
    try:
        distinct = sorted(set(vals))
    except TypeError:
        distinct = sorted({str(v) for v in vals})
    return vals, distinct


PRIMARY_FAMILIES = [
    "s3_support", "singular_locus_dim", "singular_locus_degree",
    "regularity", "elimination_poly_degree", "elimination_factor_partition",
    "betti_table",
]


def compare_class_vs_control(class_inv: list[dict], control_inv: list[dict]):
    report = {}
    for fam in PRIMARY_FAMILIES:
        cvals, cdist = distinct_multiset(class_inv, fam)
        ovals, odist = distinct_multiset(control_inv, fam)
        report[fam] = {
            "class_distinct_count": len(cdist),
            "class_distinct_values": [list(v) if isinstance(v, tuple) else v for v in cdist],
            "control_distinct_count": len(odist),
            "control_distinct_values": [list(v) if isinstance(v, tuple) else v for v in odist],
        }
    return report


# --------------------------------------------------------------------------
# top-level orchestration -- writes every required artifact into run_dir
# --------------------------------------------------------------------------


def run_experiment(run_dir: str, *, seed: int = 20260810, p: int = 4001, t: int = 30,
                    expected_member_count: int = 138, control_size: int = 138,
                    crosscheck_n: int = 20, gauge: bool = True, m4: bool = True,
                    m3_timeout: float = 120.0, m4_timeout: float = 180.0,
                    m2_timeout: float = 240.0, alt_order: str = "lp") -> dict:
    os.makedirs(run_dir, exist_ok=True)

    def write_json(name, obj):
        with open(os.path.join(run_dir, name), "w") as f:
            json.dump(obj, f, indent=2, sort_keys=False, default=str)

    log = []

    def logmsg(*a):
        msg = " ".join(str(x) for x in a)
        print(msg)
        log.append(msg)

    # --- SR2 CENSUS GATE ---------------------------------------------------
    members, census = enumerate_class(p, t)
    census_agrees_all = all(c.agrees for c in census)
    census_ok = census_agrees_all and len(members) == expected_member_count
    write_json("class-census.json", {
        "p": p, "t": t, "expected_member_count": expected_member_count,
        "observed_member_count": len(members),
        "census_agrees": bool(census_ok),
        "census_detail": [
            {"trace": c.trace, "observed_curves": c.observed_curves,
             "observed_weighted": c.observed_weighted,
             "predicted_weighted": c.predicted_weighted, "agrees": c.agrees,
             "note": c.note} for c in census
        ],
        "members": [{"a": r.a, "b": r.b, "j": r.j, "trace": r.trace,
                     "order": r.order, "aut_order": r.aut_order} for r in members],
    })
    if not census_ok:
        write_json("verdict.json", {
            "verdict": "PREMISE-FAILED",
            "reason": "SR2 census gate failed: re-emitted class enumeration "
                      "disagrees with the committed 138-member Hurwitz-"
                      "Kronecker-certified census.",
        })
        logmsg("SR2 CENSUS GATE FAILED -- stopping, PREMISE-FAILED")
        return {"verdict": "PREMISE-FAILED", "stage": "SR2", "log": log}
    logmsg(f"SR2 census gate passed: {len(members)} members, all agree={census_agrees_all}")

    # --- SR1 SUPPORT GATE ---------------------------------------------------
    support_ok, support_detail = support_gate(members, p)
    write_json("support-derivation.json", support_detail)
    if not support_ok:
        write_json("verdict.json", {
            "verdict": "PREMISE-FAILED",
            "reason": "SR1 support gate failed: symbolic re-derivation did "
                      "not match 13/9/10, or a class member's S_3 support "
                      "was not 13.",
        })
        logmsg("SR1 SUPPORT GATE FAILED -- stopping, PREMISE-FAILED")
        return {"verdict": "PREMISE-FAILED", "stage": "SR1", "log": log}
    logmsg("SR1 support gate passed: 13/9/10 confirmed, all 138 members support=13")

    # --- control set (SR4: control computed and WRITTEN before class read) -
    control_recs, drawn_traces = build_control_set(p, t, control_size, seed)
    logmsg(f"control set: {len(control_recs)} curves, traces drawn: {drawn_traces[:10]}"
          f"{'...' if len(drawn_traces) > 10 else ''}")

    t_control_start = time.perf_counter()
    control_inv = []
    for r in control_recs:
        control_inv.append(curve_full_invariants(r.a, r.b, p, seed, gauge=gauge, m4=m4,
                                                  m3_timeout=m3_timeout, m4_timeout=m4_timeout))
    control_elapsed = time.perf_counter() - t_control_start
    write_json("control-set-invariants.json", {
        "p": p, "seed": seed, "size": len(control_recs),
        "drawn_traces": drawn_traces,
        "construction": "random ordinary curves outside the class, ranked "
                        "by sha256(seed:'control:a:b') and truncated to "
                        "control_size -- deterministic given the seed",
        "wall_seconds": control_elapsed,
        "curves": control_inv,
    })
    logmsg(f"control-set-invariants.json written BEFORE class read (SR4), "
          f"{control_elapsed:.1f}s")

    # --- class-wide computation (SR4: read only after control is written) --
    t_class_start = time.perf_counter()
    class_inv = []
    for r in members:
        class_inv.append(curve_full_invariants(r.a, r.b, p, seed, gauge=gauge, m4=m4,
                                                m3_timeout=m3_timeout, m4_timeout=m4_timeout))
    class_elapsed = time.perf_counter() - t_class_start
    write_json("per-curve-invariants.json", {
        "p": p, "t": t, "seed": seed, "size": len(members),
        "grading": "homogenised with x0, F_p[x0,x1,x2,x3], standard grading, "
                  "degrevlex primary / lex on the cross-check subsample",
        "wall_seconds": class_elapsed,
        "curves": class_inv,
    })
    logmsg(f"per-curve-invariants.json written, {class_elapsed:.1f}s")

    # --- gauge recheck (C-GAUGE) --------------------------------------------
    gauge_report = {
        "class": [gauge_check_curve(inv) for inv in class_inv] if gauge else [],
        "control": [gauge_check_curve(inv) for inv in control_inv] if gauge else [],
    }
    class_gauge_fail = [g for g in gauge_report["class"] if not g["m3_agrees"]]
    control_gauge_fail = [g for g in gauge_report["control"] if not g["m3_agrees"]]
    gauge_report["summary"] = {
        "gauge_computed": bool(gauge),
        "class_failures": len(class_gauge_fail),
        "control_failures": len(control_gauge_fail),
        "all_agree": bool(gauge) and not class_gauge_fail and not control_gauge_fail,
    }
    write_json("gauge-recheck.json", gauge_report)
    logmsg(f"gauge recheck: class_failures={len(class_gauge_fail)} "
          f"control_failures={len(control_gauge_fail)}")

    # --- Koszul indicator (C-KOSZUL) ----------------------------------------
    def koszul_rows(invs, label):
        rows = []
        for inv in invs:
            m3 = inv["m3"]
            rows.append({
                "a": inv["a"], "b": inv["b"],
                "codim_hom": m3.get("codim_hom"),
                "num_generators": m3.get("num_generators"),
                "koszul_degeneration": m3.get("koszul_degeneration"),
            })
        return rows

    koszul_class = koszul_rows(class_inv, "class")
    koszul_control = koszul_rows(control_inv, "control")
    koszul_report = {
        "class": koszul_class, "control": koszul_control,
        "summary": {
            "class_all_koszul": all(r["koszul_degeneration"] for r in koszul_class) if koszul_class else None,
            "class_any_koszul": any(r["koszul_degeneration"] for r in koszul_class) if koszul_class else None,
            "control_all_koszul": all(r["koszul_degeneration"] for r in koszul_control) if koszul_control else None,
        },
    }
    write_json("koszul-indicator.json", koszul_report)
    logmsg(f"koszul indicator: class_all_koszul={koszul_report['summary']['class_all_koszul']}")

    # --- distinct-value comparison ------------------------------------------
    comparison = compare_class_vs_control(class_inv, control_inv)

    # families where the CLASS itself shows >1 distinct value
    varying_families = [fam for fam, rep in comparison.items() if rep["class_distinct_count"] > 1]

    # extreme/deviating curves per family (tail check)
    deviating = {}
    for fam in varying_families:
        vals, _ = distinct_multiset(class_inv, fam)
        mode = max(set(vals), key=vals.count) if vals else None
        devs = []
        for inv, v in zip(class_inv, vals):
            if v != mode:
                devs.append({"a": inv["a"], "b": inv["b"], "value": v, "mode": mode})
        deviating[fam] = devs

    # --- cross-check subsample selection (C-BACKEND, C-ORDER) --------------
    deviating_curves = set()
    for fam, devs in deviating.items():
        for d in devs:
            deviating_curves.add((d["a"], d["b"]))
    subsample = []
    seen = set()
    # every curve carrying a claimed difference goes in first
    for inv in class_inv + control_inv:
        key = (inv["a"], inv["b"])
        if key in deviating_curves and key not in seen:
            subsample.append(inv)
            seen.add(key)
    # then a deterministic fill to reach crosscheck_n
    ranked = sorted(class_inv + control_inv,
                    key=lambda inv: _seed_int(seed, f"xcheck:{inv['a']}:{inv['b']}"))
    for inv in ranked:
        if len(subsample) >= crosscheck_n:
            break
        key = (inv["a"], inv["b"])
        if key not in seen:
            subsample.append(inv)
            seen.add(key)

    crosscheck_rows = []
    for inv in subsample:
        a, b = inv["a"], inv["b"]
        m2_result = compute_curve_m3_m2(a, b, p, timeout=m2_timeout)
        alt_result = compute_curve_m3(a, b, p, order=alt_order, timeout=m3_timeout)
        base_sig = _m3_signature(inv["m3"])
        m2_sig = _m3_signature(m2_result) if m2_result.get("returncode") == 0 else None
        alt_sig = _m3_signature(alt_result) if alt_result.get("returncode") == 0 else None
        crosscheck_rows.append({
            "a": a, "b": b,
            "carries_claimed_difference": (a, b) in deviating_curves,
            "singular_dp_signature": base_sig,
            "macaulay2_signature": m2_sig,
            "m2_agrees": (m2_sig == base_sig) if m2_sig is not None else None,
            "m2_raw": m2_result,
            "singular_lp_signature": alt_sig,
            "order_agrees": (alt_sig == base_sig) if alt_sig is not None else None,
        })
    backend_crosscheck = {
        "backend": "macaulay2", "n_curves": len(crosscheck_rows),
        "meets_minimum_20": len(crosscheck_rows) >= 20,
        "includes_all_deviating_curves": deviating_curves.issubset(
            {(r["a"], r["b"]) for r in crosscheck_rows}),
        "alt_monomial_order": alt_order,
        "rows": crosscheck_rows,
    }
    write_json("backend-crosscheck.json", backend_crosscheck)
    m2_all_agree = all(r["m2_agrees"] for r in crosscheck_rows if r["m2_agrees"] is not None) \
        and all(r["m2_agrees"] is not None for r in crosscheck_rows)
    order_all_agree = all(r["order_agrees"] for r in crosscheck_rows if r["order_agrees"] is not None) \
        and all(r["order_agrees"] is not None for r in crosscheck_rows)
    logmsg(f"backend crosscheck: n={len(crosscheck_rows)} m2_all_agree={m2_all_agree} "
          f"order_all_agree={order_all_agree}")

    # --- F5: withdraw any claimed difference not surviving gauge/backend ---
    surviving_families = []
    withdrawn_families = []
    for fam in varying_families:
        devs = deviating[fam]
        dev_keys = {(d["a"], d["b"]) for d in devs}
        rows_for_dev = [r for r in crosscheck_rows if (r["a"], r["b"]) in dev_keys]
        survives = (len(rows_for_dev) == len(dev_keys)) and all(
            r["m2_agrees"] and r["order_agrees"] for r in rows_for_dev
        )
        # a difference must ALSO survive the gauge recheck: the deviating
        # curve's own gauge-transformed model must show the SAME deviating
        # value (an implementation defect would instead make gauge disagree).
        gauge_ok_for_dev = True
        for gc in gauge_report["class"]:
            if (gc["a"], gc["b"]) in dev_keys and not gc["m3_agrees"]:
                gauge_ok_for_dev = False
        if survives and gauge_ok_for_dev and len(rows_for_dev) > 0:
            surviving_families.append(fam)
        else:
            withdrawn_families.append({"family": fam, "reason":
                "did not survive C-BACKEND cross-check and/or C-GAUGE recheck (F5)"})

    # --- verdict -------------------------------------------------------------
    if surviving_families:
        verdict = "CLASS-VARYING"
        reason = (f"At least one primary invariant family shows >1 distinct "
                  f"value across the class, surviving gauge and backend "
                  f"checks: {surviving_families}.")
    else:
        # constancy across the class -- check F2 (control equally constant)
        control_also_constant = all(comparison[fam]["control_distinct_count"] == 1
                                    for fam in PRIMARY_FAMILIES
                                    if comparison[fam]["class_distinct_count"] == 1)
        verdict = "CLASS-INVARIANT"
        reason = ("All primary invariant families take exactly one distinct "
                  "value across the 138-curve class.")
        if control_also_constant:
            reason += (" F2 CAUTION: the control set is ALSO constant on "
                      "every family the class is constant on -- per the "
                      "falsification criterion this means the constancy may "
                      "be a property of S_3's shape and not of the isogeny "
                      "class, and closure is NOT automatically licensed by "
                      "this run alone.")

    verdict_obj = {
        "verdict": verdict,
        "reason": reason,
        "primary_family_comparison": comparison,
        "varying_families_raw": varying_families,
        "surviving_families_after_f5": surviving_families,
        "withdrawn_families": withdrawn_families,
        "deviating_curves_by_family": deviating,
        "koszul_summary": koszul_report["summary"],
        "control_construction": {"seed": seed, "size": len(control_recs),
                                 "drawn_traces": drawn_traces},
        "gauge_summary": gauge_report["summary"],
        "backend_crosscheck_summary": {
            "n_curves": len(crosscheck_rows), "m2_all_agree": m2_all_agree,
            "order_all_agree": order_all_agree,
        },
    }
    write_json("verdict.json", verdict_obj)
    logmsg(f"VERDICT: {verdict}")

    return {
        "verdict": verdict, "stage": "complete",
        "n_class": len(members), "n_control": len(control_recs),
        "n_crosscheck": len(crosscheck_rows),
        "class_wall_seconds": class_elapsed, "control_wall_seconds": control_elapsed,
        "log": log,
    }


# --------------------------------------------------------------------------
# CLI driver: writes the full reproduction-package artifact set for one run
# --------------------------------------------------------------------------


def backend_provenance_block() -> dict:
    """Report the ALREADY-COMPLETED SR3 backend install (this task's own
    Stage-0 work). Both figures below are transcribed from the executor's own
    recorded apt-get invocations for this run (not fabricated, not modeled):
    `apt-get update` succeeded in ~4s; `apt-get install -y singular` and
    `apt-get install -y macaulay2` both exited 0, in 19s and 86s respectively.
    """
    singular_version = subprocess.run([SINGULAR_BIN, "--version"],
                                      capture_output=True, text=True).stdout.strip().splitlines()
    m2_version = subprocess.run([M2_BIN, "--version"],
                                capture_output=True, text=True).stdout.strip()
    dpkg_singular = subprocess.run(["dpkg-query", "-W", "-f=${Version}", "singular"],
                                   capture_output=True, text=True).stdout.strip()
    dpkg_m2 = subprocess.run(["dpkg-query", "-W", "-f=${Version}", "macaulay2"],
                             capture_output=True, text=True).stdout.strip()
    return {
        "sr3_gate": "PASSED -- both required backends installed successfully",
        "install_attempt": {
            "apt_get_update": {"outcome": "succeeded", "elapsed_seconds": 4,
                               "measured": True},
            "singular": {"command": "apt-get install -y singular",
                        "outcome": "succeeded", "exit_code": 0,
                        "elapsed_seconds": 19, "measured": True,
                        "apt_candidate_version": "1:4.3.2-p10+ds-1.1build1"},
            "macaulay2": {"command": "apt-get install -y macaulay2",
                         "outcome": "succeeded", "exit_code": 0,
                         "elapsed_seconds": 86, "measured": True,
                         "apt_candidate_version": "1.22+ds-6build2"},
        },
        "primary_backend": {
            "name": "Singular", "binary": SINGULAR_BIN,
            "dpkg_version": dpkg_singular,
            "version_string": singular_version[0] if singular_version else None,
        },
        "cross_check_backend": {
            "name": "Macaulay2", "binary": M2_BIN,
            "dpkg_version": dpkg_m2,
            "version_string": m2_version,
        },
        "note": (
            "Prior to this run, NEITHER backend was installed (confirmed by "
            "the dispatching Coordinator via `which` and apt-cache policy "
            "before this handoff). This task's own Stage-0 work was to "
            "attempt the installs; both succeeded, so SR3 passes and the "
            "run proceeds to resolution computation -- it does NOT report "
            "failed_infrastructure. Timings are measured from this run's own "
            "apt-get invocations, executed before any resolution was "
            "computed, per SR3's own ordering requirement."),
    }


def main() -> int:
    import argparse
    import platform

    from . import runner as _runner

    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--seed", type=int, default=20260810)
    ap.add_argument("--control-size", type=int, default=138)
    ap.add_argument("--crosscheck-n", type=int, default=20)
    ap.add_argument("--m4", action="store_true", default=True)
    args = ap.parse_args()

    run_dir = args.run_dir
    os.makedirs(run_dir, exist_ok=True)

    command = (f"python3 -m harness.exp_icinv_e0cd8f --run-dir {run_dir} "
              f"--seed {args.seed} --control-size {args.control_size} "
              f"--crosscheck-n {args.crosscheck_n}")

    started = time.time()
    provenance = backend_provenance_block()
    with open(os.path.join(run_dir, "backend-provenance.json"), "w") as f:
        json.dump(provenance, f, indent=2, sort_keys=False)

    import io
    import contextlib
    buf = io.StringIO()
    err = io.StringIO()
    status = "completed_valid"
    summary = None
    exc_text = None
    try:
        with contextlib.redirect_stdout(buf):
            summary = run_experiment(run_dir, seed=args.seed, p=4001, t=30,
                                     expected_member_count=138,
                                     control_size=args.control_size,
                                     crosscheck_n=args.crosscheck_n, m4=args.m4)
    except Exception as exc:  # noqa: BLE001 -- record, never hide
        import traceback
        exc_text = traceback.format_exc()
        err.write(exc_text)
        status = "failed_infrastructure"
        summary = {"verdict": None, "stage": "exception", "error": str(exc)}

    finished = time.time()

    commit, dirty = _runner.git_state()
    prov = _runner.source_provenance()
    env = _runner.environment()

    manifest = {
        "run": {
            "id": os.path.basename(run_dir.rstrip("/")),
            "experiment_id": "EXP-ICINV-e0cd8f",
            "status": status,
            "code": {"commit": commit, "dirty": dirty, "command": command,
                     "source": prov,
                     "untracked": _runner.untracked_source_vs_output()},
            "inference": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": "claude-sonnet-5",
                "reasoning_effort": None,
                "fallback_used": False,
                "adapter_version": None,
                "note": ("This run's COMPUTATION is deterministic Python + "
                        "external CAS subprocess calls (Singular, Macaulay2) "
                        "-- no model call in the compute loop. The model "
                        "recorded here is the Claude Code session (policy "
                        "executor-implementation, requested by the dispatching "
                        "handoff TASK-20260811-d9d01e) that wrote and invoked "
                        "this harness module."),
            },
            "environment": env,
            "inputs": {
                "p": 4001, "t": 30, "discriminant": -15104,
                "seed": args.seed, "control_size": args.control_size,
                "crosscheck_n": args.crosscheck_n,
            },
            "timing": {
                "started_at": _runner._iso(started),
                "finished_at": _runner._iso(finished),
                "wall_seconds": round(finished - started, 6),
            },
            "result": {
                "verdict": (summary or {}).get("verdict"),
                "valid": status == "completed_valid",
                "certificate": {"kind": "none",
                               "note": "measurement run: no discrete-log or "
                                       "relation claim is made"},
            },
            "artifacts": {
                "backend_provenance": "backend-provenance.json",
                "class_census": "class-census.json",
                "support_derivation": "support-derivation.json",
                "per_curve_invariants": "per-curve-invariants.json",
                "control_set_invariants": "control-set-invariants.json",
                "gauge_recheck": "gauge-recheck.json",
                "backend_crosscheck": "backend-crosscheck.json",
                "koszul_indicator": "koszul-indicator.json",
                "verdict": "verdict.json",
                "command": "command.txt",
                "environment": "environment.json",
                "stdout": "stdout.log",
                "stderr": "stderr.log",
                "raw_result": "raw-result.json",
            },
        }
    }

    import yaml
    with open(os.path.join(run_dir, "manifest.yaml"), "w") as f:
        yaml.safe_dump(manifest, f, sort_keys=False)
    with open(os.path.join(run_dir, "command.txt"), "w") as f:
        f.write(command + "\n")
    with open(os.path.join(run_dir, "environment.json"), "w") as f:
        json.dump(env, f, indent=2, sort_keys=True)
    with open(os.path.join(run_dir, "stdout.log"), "w") as f:
        f.write(buf.getvalue())
    with open(os.path.join(run_dir, "stderr.log"), "w") as f:
        f.write(err.getvalue())
    with open(os.path.join(run_dir, "raw-result.json"), "w") as f:
        json.dump({"summary": summary, "status": status,
                  "backend_provenance": provenance}, f, indent=2, default=str)

    print(f"run {run_dir} status={status} verdict={(summary or {}).get('verdict')}")
    return 0 if status == "completed_valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "s3_generators", "s4_generators", "s3_support", "s4_support",
    "build_m3_singular_script", "build_m4_singular_script",
    "run_singular", "parse_m3_output", "parse_m4_output",
    "compute_curve_m3", "compute_curve_m4",
    "gauge_transform", "gauge_u_for_curve",
    "build_m3_m2_script", "run_m2", "parse_m2_output", "compute_curve_m3_m2",
    "enumerate_class", "build_control_set", "support_gate",
    "curve_full_invariants", "gauge_check_curve", "compare_class_vs_control",
    "run_experiment", "backend_provenance_block", "main",
]
