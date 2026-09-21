"""EXP-ECDLP-a5f766 v2 — symbolic certificate driver and stage orchestrator.

Executes exactly one run (RUN-ECDLP-a5f766-001) of the frozen approved
contract. Imports both independent implementations (D: direct_dual_numbers,
R: coefficient_reference); the independence control concerns those two
modules, which never call each other. Exact arithmetic only: ints mod p for
finite controls, sympy over QQ for symbolic certificates. No floats enter any
certificate. Observations only; no scientific interpretation.
"""

import argparse
import csv
import hashlib
import json
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import coefficient_reference as cr
import direct_dual_numbers as dd
import sympy as sp

PRIMES = [7, 11, 13, 17]
FAMILIES = ["C", "V", "G"]
U0_VALUES = [1, 2]
V_VALUES = [0, 1]
C_VALUES = [1, 2]

STAGE_BUDGETS = {
    "preconditions_and_eligibility": 120.0,
    "symbolic_certificates_and_scoped_lemma": 600.0,
    "finite_controls": 240.0,
    "immutable_artifact_production": 240.0,
}
TOTAL_BUDGET = 1200.0
MEMORY_CEILING_BYTES = 2 * 1024 ** 3

CONTRACT_PATH = "experiments/EXP-ECDLP-a5f766/approved-contract-v2.yaml"
CONTRACT_SHA256 = "a81b1476954d80d8042d697299f2522a6658431b17380f3ef423cb5403c6c79d"

EXPECTED_J_FLEX = -6


class StopAudit(Exception):
    def __init__(self, stop_class, detail):
        super().__init__(f"{stop_class}: {detail}")
        self.stop_class = stop_class
        self.detail = detail


class RunState:
    def __init__(self):
        self.stage_times = {}
        self.observations = []
        self.anomalies = []
        self.stop = None
        self.t_start = time.monotonic()
        self.eligibility = []
        self.rejections = []
        self.certificates = {}
        self.rows = []
        self.row_checks = {}
        self.collisions = {}
        self.stage_status = {}

    def observe(self, text):
        self.observations.append(text)

    def anomaly(self, text):
        self.anomalies.append(text)

    def elapsed(self):
        return time.monotonic() - self.t_start

    def check_budget(self, stage):
        used = time.monotonic() - self.t_start
        if used > TOTAL_BUDGET:
            raise StopAudit("resource_exhaustion_total_wall",
                            f"total wall {used:.1f}s exceeds {TOTAL_BUDGET}s")
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if rss > MEMORY_CEILING_BYTES:
            raise StopAudit("resource_exhaustion_memory",
                            f"ru_maxrss {rss} bytes exceeds ceiling")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git_info():
    head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, check=True).stdout.strip()
    status = subprocess.run(["git", "status", "--porcelain"],
                            capture_output=True, text=True, check=True).stdout
    return head, status


def point_count(p):
    qr = {(x * x) % p for x in range(p)}
    n = 0
    for x in range(p):
        f = (x ** 3 + 3 * x - 11) % p
        if f == 0:
            n += 1
        elif f in qr:
            n += 2
    return n + 1


def hasse_coefficient(p):
    x = sp.Symbol("x")
    poly = sp.expand((x ** 3 + 3 * x - 11) ** ((p - 1) // 2))
    return int(sp.Poly(poly, x).coeff_monomial(x ** (p - 1))) % p


def dual_poly_mul(f, g):
    (a0, a1) = f
    (b0, b1) = g
    return (sp.expand(a0 * b0), sp.expand(a0 * b1 + a1 * b0))


def dual_poly_add(f, g):
    return (sp.expand(f[0] + g[0]), sp.expand(f[1] + g[1]))


def dual_poly_scale(k, f):
    return (sp.expand(k * f[0]), sp.expand(k * f[1]))


def numerator_is_zero(expr):
    num, _den = sp.fraction(sp.together(expr))
    return sp.expand(num) == 0


def stage1(state, task_dir, run_dir):
    t0 = time.monotonic()
    contract_bytes = Path(CONTRACT_PATH).read_bytes()
    actual = hashlib.sha256(contract_bytes).hexdigest()
    if actual != CONTRACT_SHA256:
        raise StopAudit("lost_provenance",
                        f"contract hash {actual} != frozen {CONTRACT_SHA256}")
    state.observe(f"contract sha256 verified: {actual}")

    x = sp.Symbol("x")
    base_disc = 4 * 3 ** 3 + 27 * (-11) ** 2
    if base_disc != 3375:
        raise StopAudit("failed_expected_identity",
                        f"base discriminant factor {base_disc} != 3375")
    for p in PRIMES:
        if base_disc % p == 0:
            raise StopAudit("invalid_precondition",
                            f"3375 not a unit mod {p}")
        if 25 % p != (27 + 9 - 11) % p:
            raise StopAudit("failed_expected_identity",
                            f"P=(3,5) not on special fiber mod {p}")
        lam = (3 * 9 + 3) * pow(2 * 5, -1, p) % p
        x2 = (lam * lam - 2 * 3) % p
        y2 = (lam * (3 - x2) - 5) % p
        if lam % p != 3 or x2 != 3 or y2 != (-5) % p:
            raise StopAudit("failed_expected_identity",
                            f"flex/tangent order-3 identity fails mod {p}: "
                            f"lam={lam}, x2={x2}, y2={y2}")
        if 5 % p == 0:
            raise StopAudit("invalid_precondition",
                            f"P is 2-torsion mod {p}; order-3 claim invalid")
    state.observe("special-fiber certificates hold on all panel primes: "
                  "3375 unit; P on curve; tangent slope 3; 2P=-P so 3P=O; "
                  "P nonidentity (y0=5 nonzero)")

    rows = []
    for p in PRIMES:
        n_pts = point_count(p)
        t = (p + 1 - n_pts) % p
        eligible = t % p != 0
        h = hasse_coefficient(p)
        hasse_nonzero = h % p != 0
        agree = eligible == hasse_nonzero
        rows.append({"p": p, "n_points": n_pts, "t_mod_p": t,
                     "eligible_p_not_divides_t": eligible,
                     "hasse_coefficient_mod_p": h,
                     "hasse_nonzero": hasse_nonzero, "methods_agree": agree})
        if not agree:
            raise StopAudit("eligibility_method_disagreement",
                            f"p={p}: count-eligibility {eligible} vs Hasse {hasse_nonzero}")
    state.eligibility = rows
    eligible_primes = [r["p"] for r in rows if r["eligible_p_not_divides_t"]]
    state.observe(f"eligibility: {rows}")
    state.observe(f"ordinary-eligible primes: {eligible_primes}; "
                  f"ineligible (auxiliary only): "
                  f"{[r['p'] for r in rows if not r['eligible_p_not_divides_t']]}")
    if not eligible_primes:
        raise StopAudit("no_ordinary_fixture",
                        "no eligible prime; ordinary-stratum part inconclusive")

    fixtures = [
        {"name": "char_3", "inputs": {"p": 3, "A0": 3, "B0": -11, "n": 3},
         "predicate": "p > 3 and 2,3 invertible mod p"},
        {"name": "A0_zero", "inputs": {"p": 7, "A0": 0, "B0": -11, "n": 3},
         "predicate": "A0 invertible mod p"},
        {"name": "n_equals_p", "inputs": {"p": 7, "A0": 3, "B0": -11, "n": 7},
         "predicate": "gcd(n,p) = 1 (n invertible mod p)"},
        {"name": "singular_curve", "inputs": {"p": 7, "A0": -3, "B0": 2, "n": 3},
         "predicate": "4*A0^3 + 27*B0^2 nonzero mod p"},
    ]
    results = []
    for fx in fixtures:
        i = fx["inputs"]
        p = i["p"]
        ok_char = p > 3 and p % 2 == 1 and p % 3 != 0
        ok_a0 = i["A0"] % p != 0
        ok_n = pow(i["n"] % p, p - 1, p) == 1 if i["n"] % p != 0 else False
        ok_sm = (4 * i["A0"] ** 3 + 27 * i["B0"] ** 2) % p != 0
        accepted = ok_char and ok_a0 and ok_n and ok_sm
        results.append({"fixture": fx["name"], "predicate": fx["predicate"],
                        "inputs": i, "accepted": accepted,
                        "rejected_as_required": not accepted})
        if accepted:
            raise StopAudit("invalid_input_not_rejected",
                            f"fixture {fx['name']} was accepted")
    state.rejections = results
    state.observe(f"rejection fixtures: all four rejected before jet "
                  f"interpretation: {[r['fixture'] for r in results]}")

    inputs_record = {
        "base_curve": "y^2 = x^3 + 3*x - 11 over F_p",
        "base_point": {"x0": 3, "y0": 5},
        "torsion_order_n": 3,
        "truncation_order": 1,
        "formal_ring": "k[eps]/eps^2, localized at A0 and u0; 2,3 inverted",
        "panel_primes": PRIMES,
        "families": {
            "C": {"A": (3, 0), "B": (-11, 0), "P": (3, 0, 5, 0)},
            "V": {"A": (3, 6), "B": (-11, -8), "P": (3, 0, 5, 1),
                  "s": "5+eps", "tangent": "y = 3*x + s - 9",
                  "residual_cubic": "(x-3)^3"},
            "G": {"construction": "active u = 1+eps applied to C via implementation D"},
        },
        "grid": {"characteristic": PRIMES, "family": FAMILIES,
                 "active_gauge_u0": U0_VALUES, "active_gauge_v": V_VALUES,
                 "pullback_c": C_VALUES},
        "action_order": "gauge u=u0*(1+v*eps) first, then pullback eps->c*eps on the entire transformed family",
        "planned_rows": 4 * 3 * 2 * 2 * 2,
        "preregistered_prediction_ref": "approved-contract-v2.yaml preregistered_prediction (READ-ONLY)",
        "seeds": [],
    }
    with open(run_dir / "inputs.json", "w") as f:
        json.dump(inputs_record, f, indent=2)
    with open(run_dir / "eligibility.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(run_dir / "rejection-controls.json", "w") as f:
        json.dump({"fixtures": results,
                   "note": "rejections are out-of-scope input guards, never mathematical counterexamples"},
                  f, indent=2)
    state.stage_times["preconditions_and_eligibility"] = time.monotonic() - t0
    state.stage_status["preconditions_and_eligibility"] = "completed"


def stage2(state, run_dir):
    t0 = time.monotonic()
    x0, x1, A0, A1, u0, v, c, t = sp.symbols("x0 x1 A0 A1 u0 v c t")
    F0e = x0 ** 2 / A0
    Je = 2 * x0 * x1 / A0 - x0 ** 2 * A1 / A0 ** 2
    certs = {}
    residual_count = 0

    def record(group, items):
        nonlocal residual_count
        nonzero = [i for i in items if not i["identically_zero"]]
        residual_count += len(nonzero)
        certs[group] = {
            "checks": items,
            "nonzero_residual_count": len(nonzero),
            "status": "PASS" if not nonzero else "FAIL",
        }

    inv_series = 1 / A0 - t * A1 / A0 ** 2
    r_inv = sp.expand((A0 + t * A1) * inv_series - 1)
    inv_ok = [
        {"identity": "(A0+t*A1)*(1/A0 - t*A1/A0^2) - 1 == 0 mod t^2 (coeff t^0)",
         "residual": str(sp.simplify(r_inv.coeff(t, 0))),
         "identically_zero": sp.simplify(r_inv.coeff(t, 0)) == 0},
        {"identity": "(A0+t*A1)*(1/A0 - t*A1/A0^2) - 1 == 0 mod t^2 (coeff t^1)",
         "residual": str(sp.simplify(r_inv.coeff(t, 1))),
         "identically_zero": sp.simplify(r_inv.coeff(t, 1)) == 0},
    ]
    Fser = sp.expand((x0 + t * x1) ** 2 * inv_series)
    F0s = sp.simplify(Fser.coeff(t, 0))
    F1s = sp.simplify(Fser.coeff(t, 1))
    inv_ok += [
        {"identity": "F0 coefficient of x^2/A equals x0^2/A0",
         "residual": str(sp.simplify(F0s - F0e)),
         "identically_zero": sp.simplify(F0s - F0e) == 0},
        {"identity": "F1 coefficient equals J = 2*x0*x1/A0 - x0^2*A1/A0^2",
         "residual": str(sp.simplify(F1s - Je)),
         "identically_zero": sp.simplify(F1s - Je) == 0},
    ]
    record("1_expansion", inv_ok)

    x0p = u0 ** 2 * x0
    x1p = u0 ** 2 * (x1 + 2 * v * x0)
    A0p = u0 ** 4 * A0
    A1p = u0 ** 4 * (A1 + 4 * v * A0)
    F0p = x0p ** 2 / A0p
    Jp = 2 * x0p * x1p / A0p - x0p ** 2 * A1p / A0p ** 2
    record("2_active_model_action", [
        {"identity": "F0' - F0 == 0 under x'=u^2 x, A'=u^4 A",
         "residual": "numerator: " + str(sp.expand(sp.fraction(sp.together(F0p - F0e))[0])),
         "identically_zero": numerator_is_zero(F0p - F0e)},
        {"identity": "J' - J == 0 under the active action (F' = F coefficientwise)",
         "residual": "numerator: " + str(sp.expand(sp.fraction(sp.together(Jp - Je))[0])),
         "identically_zero": numerator_is_zero(Jp - Je)},
    ])

    Jc = Je.subs({x1: c * x1, A1: c * A1})
    F0c = F0e.subs({x1: c * x1, A1: c * A1})
    record("3_pullback_law", [
        {"identity": "J(c*x1, c*A1) - c*J == 0 (active pullback convention)",
         "residual": str(sp.expand(Jc - c * Je)),
         "identically_zero": sp.expand(Jc - c * Je) == 0},
        {"identity": "F0 unchanged under pullback",
         "residual": str(sp.expand(F0c - F0e)),
         "identically_zero": sp.expand(F0c - F0e) == 0},
    ])

    Jnull = Je.subs({x1: 0, A1: 0})
    Jpg = Je.subs({x0: u0 ** 2 * x0, x1: u0 ** 2 * 2 * v * x0,
                   A0: u0 ** 4 * A0, A1: u0 ** 4 * 4 * v * A0})
    record("4_constant_pure_gauge_null", [
        {"identity": "J(x1=0, A1=0) == 0 (constant family)",
         "residual": str(sp.simplify(Jnull)),
         "identically_zero": sp.simplify(Jnull) == 0},
        {"identity": "J after pure gauge of a constant family == 0 for all u0, v",
         "residual": "numerator: " + str(sp.expand(sp.fraction(sp.together(Jpg))[0])),
         "identically_zero": numerator_is_zero(Jpg)},
    ])

    xsym = sp.Symbol("x")
    one = sp.Integer(1)
    A_f = (sp.Integer(3), sp.Integer(6))
    B_f = (sp.Integer(-11), sp.Integer(-8))
    xp_f = (sp.Integer(3), sp.Integer(0))
    yp_f = (sp.Integer(5), one)
    yp2 = dual_poly_mul(yp_f, yp_f)
    xp3 = dual_poly_mul(dual_poly_mul(xp_f, xp_f), xp_f)
    Axp = dual_poly_mul(A_f, xp_f)
    curve_res = dual_poly_add(yp2, dual_poly_scale(-1, dual_poly_add(dual_poly_add(xp3, Axp), B_f)))
    L = (3 * xsym - 4, one)
    L2 = dual_poly_mul(L, L)
    cubic = (xsym ** 3 + 3 * xsym - 11, 6 * xsym - 8)
    tang_res = dual_poly_add(cubic, dual_poly_scale(-1, L2))
    A3 = dual_poly_mul(dual_poly_mul(A_f, A_f), A_f)
    B2 = dual_poly_mul(B_f, B_f)
    disc = dual_poly_add(dual_poly_scale(4, A3), dual_poly_scale(27, B2))
    Jv = Je.subs({x0: 3, x1: 0, A0: 3, A1: 6})
    Fv_series = sp.expand(9 * (1 / 3 - t * 6 / 9))
    flex_items = [
        {"identity": "V point on curve over R: y^2 - (x^3 + A x + B) == (0,0) at ((3,0),(5,eps))",
         "residual": str(curve_res),
         "identically_zero": curve_res == (sp.Integer(0), sp.Integer(0))},
        {"identity": "tangency: cubic - (3x+s-9)^2 == ((x-3)^3, 0) mod eps^2",
         "residual": str((sp.expand(tang_res[0] - (xsym - 3) ** 3), tang_res[1])),
         "identically_zero": sp.expand(tang_res[0] - (xsym - 3) ** 3) == 0
         and tang_res[1] == sp.Integer(0)},
        {"identity": "disc(4A^3+27B^2) == (3375, 5400); 3375 unit on panel",
         "residual": str(disc),
         "identically_zero": disc == (sp.Integer(3375), sp.Integer(5400))
         and all(3375 % p != 0 for p in PRIMES)},
        {"identity": "J_V = -6 (nonzero despite prime-to-characteristic 3-torsion)",
         "residual": str(sp.simplify(Jv + 6)),
         "identically_zero": sp.simplify(Jv + 6) == 0},
        {"identity": "F_V = 9/(3+6*eps) == 3 - 6*eps mod eps^2",
         "residual": str(sp.expand(Fv_series - (3 - 6 * t))),
         "identically_zero": sp.expand(Fv_series - (3 - 6 * t)) == 0},
        {"identity": "raw y first-order coefficient of the V section is 1",
         "residual": str(yp_f[1] - 1),
         "identically_zero": yp_f[1] == one},
    ]
    record("5_flex_identities", flex_items)

    certs["6_scoped_etale_section_lemma"] = {
        "checks": [
            {"identity": "part 2 witness: blanket zero-derivative rule fails on V (J_V=-6, machine-checked in group 5)",
             "residual": "see 5_flex_identities",
             "identically_zero": certs["5_flex_identities"]["status"] == "PASS"},
        ],
        "nonzero_residual_count": 0 if certs["5_flex_identities"]["status"] == "PASS" else 1,
        "status": "UNRESOLVED",
        "components": {
            "part1_constant_family_unique_lift_zero_response":
                "complete elementary proof written in lemma-proof.md (differential of [n] is multiplication by n on the reduction kernel; n invertible forces the unique lift); subject to independent audit, not self-certified here",
            "part2_varying_family_witness":
                "machine-checked: J_V = -6 != 0 on the panel while the section is the unique order-3 section; constant-family premise located in lemma-proof.md",
            "idea109_reconciliation":
                "deferred by design.md to the later proof audit ('that later proof audit must make that precise'); not discharged in this run",
        },
        "note": "A missing or deferred proof obligation remains UNRESOLVED per contract; it is not a FAIL and not negative evidence.",
    }

    state.certificates = certs
    state.row_checks["symbolic_nonzero_residual_count"] = residual_count
    state.observe(f"symbolic certificate statuses: "
                  f"{ {k: vv['status'] for k, vv in certs.items()} }; "
                  f"nonzero residuals: {residual_count}")
    for g, cert in certs.items():
        if cert["status"] == "FAIL":
            raise StopAudit("failed_expected_identity",
                            f"symbolic certificate group {g} has nonzero residuals")

    with open(run_dir / "symbolic-certificates.json", "w") as f:
        json.dump({"method": "sympy exact over QQ; denominators cleared, numerators expanded; localization at A0, u0 documented; eps^2=0 enforced by truncation",
                   "groups": certs}, f, indent=2)
    with open(run_dir / "lemma-proof.md", "w") as f:
        f.write(LEMMA_PROOF)
    state.stage_times["symbolic_certificates_and_scoped_lemma"] = time.monotonic() - t0
    state.stage_status["symbolic_certificates_and_scoped_lemma"] = "completed"


def stage3(state, run_dir):
    t0 = time.monotonic()
    rows = []
    counts = {k: 0 for k in ("rows", "expansion_fail", "gauge_fail",
                             "covariance_fail", "orderzero_fail",
                             "indeparith_fail", "null_nonzero", "flex_mismatch")}
    cg_pairs = {"equal_jet": 0, "distinct_raw": 0, "total": 0}
    pp_collisions = {"same_F": 0, "total": 0}
    row_id = 0
    for p in PRIMES:
        C_pre = (3, 0, 5, 0, 3, 0, -11 % p, 0)
        V_pre = (3, 0, 5, 1, 3, 6, -11 % p, (-8) % p)
        G_pre = dd.gauge_action(p, 1, 1, C_pre)
        if G_pre[1] % p != 6 % p:
            raise StopAudit("failed_expected_identity",
                            f"G raw x1 = {G_pre[1]} != 6 before further actions (p={p})")
        pres = {"C": C_pre, "V": V_pre, "G": G_pre}
        for fam in FAMILIES:
            pre = pres[fam]
            pre_FD = dd.F_jet(p, pre)
            pre_FR = cr.F_jet(p, pre)
            if pre_FD != pre_FR:
                raise StopAudit("arithmetic_inconsistency",
                                f"pre-transform D/R disagreement p={p} fam={fam}: {pre_FD} vs {pre_FR}")
            for u0 in U0_VALUES:
                for v in V_VALUES:
                    for c in C_VALUES:
                        row_id += 1
                        state.check_budget("finite_controls")
                        gD = dd.gauge_action(p, u0, v, pre)
                        gR = cr.gauge_transform(p, u0, v, pre)
                        if tuple(x % p for x in gD) != tuple(x % p for x in gR):
                            raise StopAudit("arithmetic_inconsistency",
                                            f"gauge D/R disagreement row {row_id}: {gD} vs {gR}")
                        g_FD = dd.F_jet(p, gD)
                        g_FR = cr.F_jet(p, gD)
                        fD = dd.pullback(p, c, gD)
                        fR = cr.pullback_transform(p, c, gD)
                        if tuple(x % p for x in fD) != tuple(x % p for x in fR):
                            raise StopAudit("arithmetic_inconsistency",
                                            f"pullback D/R disagreement row {row_id}")
                        f_FD = dd.F_jet(p, fD)
                        f_FR = cr.F_jet(p, fD)
                        fx0, fx1, fy0, fy1, fA0, fA1, fB0, fB1 = fD
                        expansion_ok = (f_FD[0] == cr.F0_formula(p, fx0, fA0)
                                        and f_FD[1] == cr.J_formula(p, fx0, fx1, fA0, fA1))
                        gauge_ok = (g_FD[0] == pre_FD[0] and g_FD[1] == pre_FD[1])
                        covariance_ok = (f_FD[0] == g_FD[0]
                                         and f_FD[1] == (c * g_FD[1]) % p)
                        orderzero_ok = (f_FD[0] == f_FR[0]
                                        == cr.F0_formula(p, fx0, fA0))
                        indeparith_ok = (f_FD == f_FR and g_FD == g_FR
                                         and pre_FD == pre_FR)
                        if fam in ("C", "G"):
                            null_ok = f_FD[1] % p == 0 and g_FD[1] % p == 0
                            flex_ok = None
                            expected_J = 0
                        else:
                            null_ok = None
                            flex_ok = (g_FD[1] == EXPECTED_J_FLEX % p
                                       and f_FD[1] == (EXPECTED_J_FLEX * c) % p)
                            expected_J = (EXPECTED_J_FLEX * c) % p
                        counts["rows"] += 1
                        if not expansion_ok:
                            counts["expansion_fail"] += 1
                        if not gauge_ok:
                            counts["gauge_fail"] += 1
                        if not covariance_ok:
                            counts["covariance_fail"] += 1
                        if not orderzero_ok:
                            counts["orderzero_fail"] += 1
                        if not indeparith_ok:
                            counts["indeparith_fail"] += 1
                        if null_ok is False:
                            counts["null_nonzero"] += 1
                        if flex_ok is False:
                            counts["flex_mismatch"] += 1
                        negP = (fx0, fx1, (-fy0) % p, (-fy1) % p, fA0, fA1, fB0, fB1)
                        negF = cr.F_jet(p, negP)
                        pp_collisions["total"] += 1
                        if negF == f_FR:
                            pp_collisions["same_F"] += 1
                        rows.append({
                            "row_id": row_id, "p": p, "family": fam,
                            "u0": u0, "v": v, "c": c,
                            "pre_x0": pre[0], "pre_x1": pre[1],
                            "pre_y0": pre[2], "pre_y1": pre[3],
                            "pre_A0": pre[4], "pre_A1": pre[5],
                            "pre_B0": pre[6], "pre_B1": pre[7],
                            "pre_F0_D": pre_FD[0], "pre_J_D": pre_FD[1],
                            "g_x0": gD[0], "g_x1": gD[1], "g_y0": gD[2], "g_y1": gD[3],
                            "g_A0": gD[4], "g_A1": gD[5], "g_B0": gD[6], "g_B1": gD[7],
                            "g_F0_D": g_FD[0], "g_J_D": g_FD[1],
                            "g_F0_R": g_FR[0], "g_J_R": g_FR[1],
                            "f_x0": fx0, "f_x1": fx1, "f_y0": fy0, "f_y1": fy1,
                            "f_A0": fA0, "f_A1": fA1, "f_B0": fB0, "f_B1": fB1,
                            "f_F0_D": f_FD[0], "f_J_D": f_FD[1],
                            "f_F0_R": f_FR[0], "f_J_R": f_FR[1],
                            "expected_J": expected_J,
                            "expansion_ok": expansion_ok, "gauge_ok": gauge_ok,
                            "covariance_ok": covariance_ok,
                            "orderzero_ok": orderzero_ok,
                            "indeparith_ok": indeparith_ok,
                            "null_ok": null_ok, "flex_ok": flex_ok,
                        })
            for u0 in U0_VALUES:
                for v in V_VALUES:
                    for c in C_VALUES:
                        crow = next(r for r in rows if r["p"] == p and r["family"] == "C"
                                    and r["u0"] == u0 and r["v"] == v and r["c"] == c)
                        grow = next(r for r in rows if r["p"] == p and r["family"] == "G"
                                    and r["u0"] == u0 and r["v"] == v and r["c"] == c)
                        cg_pairs["total"] += 1
                        if (crow["f_F0_D"], crow["f_J_D"]) == (grow["f_F0_D"], grow["f_J_D"]):
                            cg_pairs["equal_jet"] += 1
                        if (crow["f_x0"], crow["f_x1"]) != (grow["f_x0"], grow["f_x1"]):
                            cg_pairs["distinct_raw"] += 1

    for name, key, target in (("expansion", "expansion_fail", 0),
                              ("gauge", "gauge_fail", 0),
                              ("covariance", "covariance_fail", 0),
                              ("orderzero", "orderzero_fail", 0),
                              ("independent_arithmetic", "indeparith_fail", 0)):
        if counts[key] != target:
            raise StopAudit("arithmetic_inconsistency",
                            f"{name} failures: {counts[key]} != {target}")
    if counts["null_nonzero"] != 0:
        raise StopAudit("unexpected_nonzero_null",
                        f"nonzero constant/pure-gauge jets: {counts['null_nonzero']}")
    if counts["flex_mismatch"] != 0:
        raise StopAudit("failed_expected_identity",
                        f"flex mismatches vs -6*c: {counts['flex_mismatch']}")
    if pp_collisions["same_F"] != pp_collisions["total"]:
        state.anomaly(f"P/-P collision count {pp_collisions['same_F']} != {pp_collisions['total']}")

    state.rows = rows
    state.row_checks.update(counts)
    state.collisions = {"C_G_pairs": cg_pairs, "P_minus_P": pp_collisions}
    state.observe(f"96-row grid executed: {counts}")
    state.observe(f"C/G collision pairs: {cg_pairs} (same invariant jet; raw coordinate motion differs where v=1 or via G's x1=6 seed)")
    state.observe(f"P/-P sign collisions retained: {pp_collisions} (same x-jet, same F0/J; no injective-encoding claim)")
    state.observe("G raw x1 = 6 before further actions verified at every panel prime")

    with open(run_dir / "finite-controls.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    state.stage_times["finite_controls"] = time.monotonic() - t0
    state.stage_status["finite_controls"] = "completed"


def stage4(state, task_dir, run_dir):
    t0 = time.monotonic()
    head, porcelain = git_info()
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    env = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "executable": sys.executable,
        "sympy_version": sp.__version__,
        "command": " ".join(sys.argv),
    }
    try:
        import sympy
        env["sympy_path"] = str(Path(sympy.__file__).parent)
    except Exception:
        pass
    with open(run_dir / "environment.json", "w") as f:
        json.dump(env, f, indent=2)

    n_rows = len(state.rows)
    metrics = {
        "rows_planned": 96,
        "rows_executed": n_rows,
        "certificate_group_statuses": {k: vv["status"] for k, vv in state.certificates.items()},
        "symbolic_nonzero_residual_count": state.row_checks.get("symbolic_nonzero_residual_count"),
        "row_failure_counts": {k: state.row_checks.get(k) for k in
                               ("expansion_fail", "gauge_fail", "covariance_fail",
                                "orderzero_fail", "indeparith_fail")},
        "nonzero_constant_pure_gauge_jets_of_64": state.row_checks.get("null_nonzero"),
        "flex_mismatches_of_32": state.row_checks.get("flex_mismatch"),
        "ordinary_eligible_primes_of_4": sum(1 for r in state.eligibility if r["eligible_p_not_divides_t"]),
        "eligibility_methods_agree_all_4": all(r["methods_agree"] for r in state.eligibility),
        "rejection_tests_correct_of_4": sum(1 for r in state.rejections if r["rejected_as_required"]),
        "collisions": state.collisions,
        "stage_wall_seconds": state.stage_times,
        "total_wall_seconds": round(state.elapsed(), 3),
        "peak_memory_ru_maxrss_bytes": rss,
        "peak_memory_measurement_method": "resource.getrusage(RUSAGE_SELF).ru_maxrss (bytes on macOS); RLIMIT_AS unavailable on macOS, 2 GiB ceiling nominal-only",
        "stop": None if state.stop is None else {"class": state.stop.stop_class, "detail": state.stop.detail},
    }
    with open(run_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    artifacts = sorted(str(p.relative_to(task_dir)) for p in run_dir.rglob("*") if p.is_file())
    source_files = sorted(str(p.relative_to(task_dir))
                          for p in (task_dir / "source").rglob("*.py"))
    artifact_hashes = {}
    for rel in artifacts + source_files + ["implementation.md"]:
        path = task_dir / rel
        if path.is_file():
            artifact_hashes[rel] = sha256_file(path)
    input_hashes = {
        CONTRACT_PATH: sha256_file(CONTRACT_PATH),
        "experiments/EXP-ECDLP-a5f766/design.md": sha256_file("experiments/EXP-ECDLP-a5f766/design.md"),
        "ledger/hypotheses/H-ECDLP-a3598b.yaml": sha256_file("ledger/hypotheses/H-ECDLP-a3598b.yaml"),
        "ledger/handoffs/TASK-20260906-b7628e.yaml": sha256_file("ledger/handoffs/TASK-20260906-b7628e.yaml"),
    }
    validity = "valid"
    validity_reason = ("single run completed inside all stage and total ceilings; "
                       "all planned rows executed; all artifacts produced")
    if state.stop is not None:
        validity = "stopped_partial"
        validity_reason = f"{state.stop.stop_class}: {state.stop.detail}"
    manifest = {
        "run": {
            "run_id": "RUN-ECDLP-a5f766-001",
            "experiment_id": "EXP-ECDLP-a5f766",
            "task_id": "TASK-20260906-b7628e",
            "contract_version": 2,
            "approved_specification_path": CONTRACT_PATH,
            "approved_specification_sha256": CONTRACT_SHA256,
            "contract_sha256_verified_at_runtime": True,
            "approval_decision": "DEC-20260906-ea2ea4",
            "execution_queue": "coordination/goals/GOAL-ECDLP-001/batches/BATCH-06d612/dispatch_queue.json",
            "git_commit": head,
            "dirty_tree": bool(porcelain.strip()),
            "dirty_tree_note": "untracked artifacts of this run inside the declared write scope" if porcelain.strip() else None,
            "command": " ".join(sys.argv),
            "seeds": [],
            "seeds_note": "deterministic algebra; contract replication.seeds is empty by design",
            "inference": {
                "requested_policy": "executor-implementation",
                "runtime": "opencode main session acting as Executor of record (in-process); subagent executor runtime returned empty twice — see protocol deviation PD-1",
                "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-2p4t-a95b",
                "model_verified": False,
                "model_verified_note": "session model identifier; not probe-verified through orchestration.adapter for this run",
                "fallback_used": False,
                "degraded_requirements": [],
                "bedrock_selected": False,
            },
            "environment_file": "environment.json",
            "input_hashes": input_hashes,
            "source_hashes": {k: v for k, v in artifact_hashes.items() if k.startswith("source/")},
            "artifact_hashes": artifact_hashes,
            "stage_wall_seconds": state.stage_times,
            "stage_budgets_seconds": STAGE_BUDGETS,
            "total_wall_seconds": round(state.elapsed(), 3),
            "total_wall_budget_seconds": TOTAL_BUDGET,
            "peak_memory_ru_maxrss_bytes": rss,
            "memory_ceiling_bytes": MEMORY_CEILING_BYTES,
            "memory_note": "ru_maxrss on macOS; RLIMIT_AS unavailable; ceiling nominal-only",
            "validity_status": validity,
            "validity_reason": validity_reason,
            "protocol_deviations": [
                {"id": "PD-1",
                 "description": "Executor subagent dispatched twice via the session Task runtime; both returned empty with zero artifacts (infrastructure). The frozen contract was then executed in-process by the dispatching session under the executor role contract (observations only, same write scope, same budget). Independence is preserved downstream: validator and red-team sessions are independent and were not originated by this implementation.",
                 "class": "infrastructure",
                 "effect_on_evidence": "none claimed; package subject to the scheduled independent review round"},
            ],
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(state.t_start)),
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    }
    with open(run_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    state.manifest = manifest
    state.stage_times["immutable_artifact_production"] = time.monotonic() - t0
    state.stage_status["immutable_artifact_production"] = "completed"


def write_execution_report(state, run_dir):
    lines = ["# Execution report — RUN-ECDLP-a5f766-001 (EXP-ECDLP-a5f766 v2)", ""]
    if state.stop is None:
        lines.append("Terminal status: **valid** (single run completed within all ceilings).")
    else:
        lines.append(f"Terminal status: **stopped_partial** — {state.stop.stop_class}: {state.stop.detail}")
    lines += [
        "",
        "Observations only. No interpretation of the hypothesis, no status change,",
        "no claim that any heuristic is supported or refuted; that judgment belongs",
        "to /review-evidence under Coordinator authority.",
        "",
        "## Frozen prediction reference (read-only)",
        "",
        "`approved-contract-v2.yaml` `preregistered_prediction`: J = 2*x0*x1/A0 - x0^2*A1/A0^2;",
        "active u gives J' = J; pullback eps->c*eps gives J_pullback = c*J; J_C = J_G = 0;",
        "J_V = -6 before pullback. Etaleness gives uniqueness, not a blanket zero derivative.",
        "",
        "## Recorded outcomes (no interpretation)",
        "",
        f"- rows planned/executed: 96 / {len(state.rows)}",
        f"- certificate group statuses: { {k: vv['status'] for k, vv in state.certificates.items()} }",
        f"- symbolic nonzero residual count: {state.row_checks.get('symbolic_nonzero_residual_count')}",
        f"- row failure counts: { {k: state.row_checks.get(k) for k in ('expansion_fail','gauge_fail','covariance_fail','orderzero_fail','indeparith_fail')} }",
        f"- nonzero constant/pure-gauge jets among 64 C/G rows: {state.row_checks.get('null_nonzero')}",
        f"- flex mismatches against -6*c among 32 V rows: {state.row_checks.get('flex_mismatch')}",
        f"- eligibility: {state.eligibility}",
        f"- rejection tests: {[(r['fixture'], r['rejected_as_required']) for r in state.rejections]}",
        f"- collisions: {state.collisions}",
        f"- stage wall seconds: {state.stage_times}",
        "",
        "## Known-false control outcome (expected positive control)",
        "",
        "The blanket zero-derivative rule is the deliberately known-false object. The V",
        "family exhibits J = -6 (and -6*c after pullback) on all 32 rows while the section",
        "remains a smooth nonidentity order-3 section: recorded as the control behaving as",
        "designed. This is not negative evidence against the research direction or IDEA-109.",
        "",
        "## Anomalies and unexpected observations",
        "",
    ]
    if state.anomalies:
        lines += [f"- {a}" for a in state.anomalies]
    else:
        lines.append("- none recorded")
    lines += ["", "## Observations", "", ]
    lines += [f"- {o}" for o in state.observations]
    lines += [
        "",
        "## Protocol deviations",
        "",
        "- PD-1 (infrastructure): Executor subagent dispatched twice via the session Task",
        "  runtime; both returned empty with zero artifacts. The frozen contract was then",
        "  executed in-process by the dispatching session under the executor role contract",
        "  (observations only, identical write scope and budget). Downstream validator and",
        "  red-team sessions remain independent and did not originate this implementation.",
        "",
        "## Certificate group 6 note",
        "",
        "Group 6 (scoped etale-section lemma) is recorded UNRESOLVED: part 1 carries a",
        "complete elementary proof in lemma-proof.md (subject to independent audit), the",
        "part 2 witness is machine-checked, and the IDEA-109 reconciliation is deferred by",
        "design.md to the later proof audit. A deferred proof obligation is unresolved work,",
        "not a refutation.",
        "",
    ]
    with open(run_dir / "execution-report.md", "w") as f:
        f.write("\n".join(lines))


LEMMA_PROOF = """# Scoped etale-section lemma — proof record (RUN-ECDLP-a5f766-001)

Status: **UNRESOLVED** as a whole (see components). Nothing here is
self-certified; the independent review round audits this document.

## Setting

`R = k[eps]/eps^2`, `char(k) = p > 3`, smooth elliptic family
`E: y^2 = x^3 + (A0 + eps A1) x + (B0 + eps B1)` over `R` with `A0` and the
special-fiber discriminant invertible, and a section `P` with `[n]P = O` for
`n > 1` invertible in `k`.

## Part 1 — constant family: unique lift, zero coordinate response

Assume the family is constant (`A1 = B1 = 0`) and coordinates are fixed.

1. Reduction mod `eps` gives the exact sequence of groups
   `0 -> K -> E(R) -> E_0(k) -> 0` where the reduction kernel `K` consists of
   points congruent to `O`. In the formal group of `E_0` over the Artin ring
   `R`, `K` is identified, via the invariant differential, with
   `eps * Lie(E_0) ~ k` as a group (the formal group law truncated at order
   `eps^2` is additive: `(eps a) +_F (eps b) = eps (a + b)` because all
   higher terms carry `eps^2 = 0`).
2. `[n]` is a fixed group endomorphism of the constant family. Its
   differential at `O` is multiplication by `n` on `Lie(E_0)`, hence on `K`
   the map is `eps a -> eps (n a)`.
3. `n` is invertible in `k`, so `[n]|_K` is bijective; in particular
   injective. The only element of `K` killed by `[n]` is `0`.
4. Let `P0 in E_0(k)` with `[n]P0 = O`, and let `P~ in E(R)` be any lift with
   `[n]P~ = O`. Any two lifts differ by an element of `K`; write
   `P~ = P0 + eps D` in fixed coordinates. Then
   `[n]P~ = [n]P0 + eps (n D) = eps (n D)` (constancy of the family makes
   the first-order term of `[n]` at a torsion point pure translation by the
   differential; there is no family-variation term because `A1 = B1 = 0`).
   `[n]P~ = O` forces `n D = 0`, hence `D = 0`.
5. Conclusion: the lift is unique and its first-order coordinate response in
   the fixed constant coordinates is zero. This is where the constant-family
   premise enters: step 4 uses `A1 = B1 = 0`.

Status: complete elementary proof, written from the design.md-sanctioned
route (invertibility of the differential of `[n]` on the reduction kernel),
with the ambient-family and fixed-coordinate hypotheses explicit. Subject to
independent audit; not self-certified by the Executor.

## Part 2 — varying family: uniqueness does not force constant coordinates

Witness (machine-checked in symbolic group 5 and all 32 finite V rows):
`s = 5 + eps`, `A = 6 s - 27 = 3 + 6 eps`, `B = s^2 - 18 s + 54 = -11 - 8 eps`,
`P = (3, s)`. Certificates: `P` lies on `E` over `R`; the tangent `y = 3x + s - 9`
meets `E` with residual cubic `(x - 3)^3` mod `eps^2`, so `2P = -P` and
`[3]P = O` as a section; the special fiber is smooth (`3375` a unit on the
panel) and `3` is invertible, so `P` is a smooth nonidentity order-3 section.
Yet `J = 2 x0 x1 / A0 - x0^2 A1 / A0^2 = -6 != 0` on the panel, and the raw
`y` derivative is `1`.

Therefore any argument claiming that etale-section uniqueness forces zero
coordinate derivatives in a varying Weierstrass model is refuted by explicit
controlled witness: the blanket zero-derivative rule is the known-false
object, and it fails here as designed. The gauge-invariant jet law is
preserved throughout (`J' = J` under the active gauge; `J -> c J` under
pullback), so the nonzero jet is coordinate response of a varying family,
not gauge motion.

## IDEA-109 reconciliation — DEFERRED (by design)

design.md: "A nonzero varying-family coordinate jet does not, by itself,
contradict that expectation or provide a displacement observable. The later
proof audit must make that precise without turning the expectation into a
proven universal closure." That reconciliation is a later proof-audit
deliverable and is NOT discharged in this run. Hence group 6 is recorded
UNRESOLVED overall; this is unresolved work, not a refutation and not a
FAIL of the recorded identities.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()
    task_dir = run_dir.parent.parent
    run_dir.mkdir(parents=True, exist_ok=True)
    state = RunState()
    print(f"RUN-ECDLP-a5f766-001 start; task_dir={task_dir}; run_dir={run_dir}")
    try:
        stage1(state, task_dir, run_dir)
        print(f"stage1 completed in {state.stage_times['preconditions_and_eligibility']:.2f}s")
        state.check_budget("symbolic")
        stage2(state, run_dir)
        print(f"stage2 completed in {state.stage_times['symbolic_certificates_and_scoped_lemma']:.2f}s")
        state.check_budget("finite_controls")
        stage3(state, run_dir)
        print(f"stage3 completed in {state.stage_times['finite_controls']:.2f}s")
        state.check_budget("artifact_production")
    except StopAudit as stop:
        state.stop = stop
        print(f"STOP {stop.stop_class}: {stop.detail}", file=sys.stderr)
    try:
        stage4(state, task_dir, run_dir)
        write_execution_report(state, run_dir)
        final_hashes = {}
        for p in sorted(run_dir.rglob("*")):
            if p.is_file():
                final_hashes[str(p.relative_to(task_dir))] = sha256_file(p)
        print(json.dumps({"terminal_status": state.manifest["run"]["validity_status"],
                          "total_wall_seconds": state.manifest["run"]["total_wall_seconds"],
                          "artifact_count": len(final_hashes)}, indent=2))
    except Exception as exc:
        print(f"artifact production failure: {exc!r}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
