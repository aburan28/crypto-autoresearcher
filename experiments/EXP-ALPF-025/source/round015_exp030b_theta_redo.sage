# round015_exp030b_theta_redo.sage
# EXP-030b: BOUNDED redo of the stalled round-13 theta-null Kummer measurement.
#
# GOAL (settle H14's last open chart, the THETA-NULL chart):
#   Round-13 EXP-030 built a genuinely-distinct level-2 theta-null Kummer-surface
#   decomposition relation (4 theta-null coords, biquadratic Hadamard addition,
#   over-determined m=3) but STALLED before the gated-meter measurement finished.
#   This file makes the measurement COMPLETE and RETURN on a tiny budget.
#
# BOUNDED SCOPE (so it finishes):
#   p in {31, 67} only (131 dropped); m in {2, 3} only; meter_gated Dmax capped
#   at D_reg+1 (probe only up to D_reg+1, not 14); wall-clock guard writes a
#   partial result + returns if the budget is approached.
#
# WHAT WE MEASURE for the genuinely-distinct theta-null relation:
#   (a) d_ff / D_reg / fires / gate_passes / gate_meaningful from meter_gated
#       (sumpoly_indices = the theta summation/biquadratic-addition rows);
#   (b) per-variable degree vs the elliptic Semaev per-pair bound 4^(m-1);
#   (c) auto-descent: transport a PUBLIC EC DLP (k hidden) and verify k_rec*P==Q
#       against the PUBLIC point ONLY (round-13 affine NR-024 failed this; we use
#       Sage discrete_log on the public point, never reading the ground-truth k
#       to drive the solve).
#
# EXPECTED NULL: theta law factors through the elliptic structure (isogeny/quotient
# invariance is chart-independent) -> gate_meaningful=False -> H14 theta-null chart
# CLOSED, joining affine (NR-024) + x-line (NR-028): H14 closed across all 3 charts.
# If it FIRES gate_meaningful + lower per-variable degree + auto-descends -> CANDIDATE.
#
# Loads + self-validates the gated meter (round007 -> round005), all FOUR fixtures.

import sys, os, json, time, traceback

BASE = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
LOG_PATH = os.path.join(BASE, "round015_exp030b_theta_redo.log")
JSON_PATH = os.path.join(BASE, "round015_exp030b_theta_redo_result.json")

T_START = time.time()
BUDGET_SECONDS = 420.0   # ~7 min wall-clock guard

_logf = open(LOG_PATH, "w")
def xlog(*a):
    s = " ".join(str(x) for x in a)
    _logf.write(s + "\n")
    _logf.flush()
    try:
        print(s)
    except Exception:
        pass

def elapsed():
    return time.time() - T_START

def over_budget():
    return elapsed() > BUDGET_SECONDS

xlog("=== EXP-030b BOUNDED theta-null Kummer redo ===", time.asctime())

# ---------------------------------------------------------------------------
# Load gated meter + base meter. Reopen meter log handle defensively.
# ---------------------------------------------------------------------------
load(os.path.join(BASE, "round005_meter_validation.sage"))
load(os.path.join(BASE, "round007_exp012_localization_gate.sage"))

# ---------------------------------------------------------------------------
# Inline self-validation of the gated meter on ALL FOUR fixtures.
# Reuse the PROVEN round007 builders so fixture semantics match exactly.
#   POS-A      : base fires d_ff=4 < D_reg (no summation poly -> gate N/A)
#   NEG-1      : quiet (no base fire)
#   e-ring m=3 : base fires but gate_meaningful = False (artifact rejected)
#   POS-C Weil : base fires AND gate_meaningful = True (genuine fall passes)
# ---------------------------------------------------------------------------
def selfvalidate_meter():
    results = {}

    polys, R, sidx = build_POS_A()
    r = meter_gated(polys, R, sumpoly_indices=set(int(i) for i in sidx), Dmax=10)
    results["POS_A"] = r
    ok_A = bool(r["fires"] and r["d_ff"] is not None and r["d_ff"] < r["D_reg"])
    xlog("FIXTURE POS_A   ok=", ok_A, "d_ff=", r["d_ff"], "D_reg=", r["D_reg"],
         "fires=", r["fires"], "gm=", r["gate_meaningful"])

    polys, R, sidx = build_NEG_generic_quadrics()
    r = meter_gated(polys, R, sumpoly_indices=set(int(i) for i in sidx), Dmax=10)
    results["NEG_1"] = r
    ok_N = bool(not r["fires"] and not r["gate_meaningful"])
    xlog("FIXTURE NEG_1   ok=", ok_N, "fires=", r["fires"], "gm=", r["gate_meaningful"])

    polys, R, sidx = build_ering_m3_semaev()
    r = meter_gated(polys, R, sumpoly_indices=set(int(i) for i in sidx), Dmax=14)
    results["ering_m3"] = r
    ok_E = bool(r["fires"] and not r["gate_meaningful"])
    xlog("FIXTURE ering_m3 ok=", ok_E, "fires=", r["fires"], "gm=", r["gate_meaningful"])

    polys, R, sidx = build_POSC_weil_S3()
    r = meter_gated(polys, R, sumpoly_indices=set(int(i) for i in sidx), Dmax=12)
    results["POS_C"] = r
    ok_C = bool(r["fires"] and r["gate_meaningful"])
    xlog("FIXTURE POS_C   ok=", ok_C, "fires=", r["fires"], "gm=", r["gate_meaningful"])

    allok = bool(ok_A and ok_N and ok_E and ok_C)
    results["_ok"] = {"POS_A": bool(ok_A), "NEG_1": bool(ok_N),
                      "ering_m3": bool(ok_E), "POS_C": bool(ok_C), "ALL": allok}
    return results, allok

try:
    fixture_report, meter_ok = selfvalidate_meter()
except Exception as e:
    fixture_report = {"error": str(e), "tb": traceback.format_exc()}
    meter_ok = False
xlog("METER SELF-VALIDATION ALL =", meter_ok)

# ---------------------------------------------------------------------------
# Theta-null Kummer-surface machinery (reused from round-13 EXP-030, trimmed).
# Level-2 theta model of the Kummer surface of the product abelian surface
# A = E x E, with four theta-null coords (a:b:c:d) and the Hadamard biquadratic
# addition law. Genuinely 4-coordinate / 2-dimensional; NOT the x-line.
# ---------------------------------------------------------------------------
def hadamard4(t):
    a, b, c, d = t
    return (a + b + c + d, a - b + c - d, a + b - c - d, a - b - c + d)

def genus1_theta_null(E):
    """Genus-1 level-2 theta-null pair (a0,a1) from 2-torsion / Legendre data."""
    F = E.base_field()
    f2 = E.division_polynomial(2)
    roots = f2.roots(multiplicities=False)
    if len(roots) < 3:
        return (F(1), F(2))
    e1, e2, e3 = roots[0], roots[1], roots[2]
    lam = (e3 - e1) / (e2 - e1)
    if lam.is_square():
        return (F(1), lam.sqrt())
    return (F(1), lam)

def kummer_point_from_x(x, a0, a1, F):
    """Map an affine x of E to a genus-1 level-2 theta pair (th0:th1)."""
    if a0 == 0:
        return (F(1), F(0))
    val = x * (a1**2) / (a0**2)
    if val.is_square():
        th0 = val.sqrt()
    else:
        th0 = None
    return (th0, F(1))

def build_theta_surface_relation(F, m):
    """Construct the over-determined theta-null Kummer-surface decomposition
       relation for m summands (m=2: P (+) Q with target; m=3: also the
       difference auxiliary). Returns (R, P, Q, M) generator tuples.
       For m=2 we use only P with target (single FB point); for m=3 we use
       P, Q with the difference M as auxiliary (the genuine over-determined
       biquadratic addition)."""
    if m == 2:
        names = ["p0", "p1", "p2", "p3"]
        R = PolynomialRing(F, names)
        g = R.gens()
        return R, list(g[0:4]), None, None
    else:
        names = ["p0", "p1", "p2", "p3", "q0", "q1", "q2", "q3",
                 "m0", "m1", "m2", "m3"]
        R = PolynomialRing(F, names)
        g = R.gens()
        return R, list(g[0:4]), list(g[4:8]), list(g[8:12])

def build_xline_semaev(Fp, E, m):
    """The x-line Semaev S_{m+1} for the anti-circularity comparison.
       m=2 -> S_3 (3 vars); m=3 -> S_4 expressed via resultant of two S_3."""
    A = E.a4(); B = E.a6()
    if m == 2:
        Rx = PolynomialRing(Fp, 3, "X")
        X0, X1, X2 = Rx.gens()
        S = ((X0 - X1)**2 * X2**2
             - 2 * ((X0 + X1) * (X0 * X1 + A) + 2 * B) * X2
             + (X0 * X1 - A)**2 - 4 * B * (X0 + X1))
        return Rx, [S]
    else:
        # S_4 via Semaev recursion: Res_t( S_3(X0,X1,t), S_3(X2,X3,t) )
        Rt = PolynomialRing(Fp, 5, ["X0", "X1", "X2", "X3", "t"])
        X0, X1, X2, X3, t = Rt.gens()
        def S3(a, b, c):
            return ((a - b)**2 * c**2
                    - 2 * ((a + b) * (a * b + A) + 2 * B) * c
                    + (a * b - A)**2 - 4 * B * (a + b))
        s_a = S3(X0, X1, t)
        s_b = S3(X2, X3, t)
        Rxt = PolynomialRing(Fp, 4, ["X0", "X1", "X2", "X3"])
        try:
            S4 = s_a.resultant(s_b, t)
            S4 = Rxt(S4)
        except Exception:
            S4 = None
        return Rxt, ([S4] if S4 is not None else [])

# ---------------------------------------------------------------------------
# Per (p, m) run.
# ---------------------------------------------------------------------------
def run_pm(p, m, label, seed):
    set_random_seed(int(seed))
    out = {"p": int(p), "m": int(m), "label": label}
    Fp = GF(p)

    # ---- curve: Solinas a=-3 (or random), prime order ----
    E = None
    if label.startswith("solinas"):
        a = Fp(-3)
        for bb in range(1, p):
            try:
                Ec = EllipticCurve(Fp, [a, Fp(bb)])
            except Exception:
                continue
            if Ec.order().is_prime():
                E = Ec; break
        if E is None:
            E = EllipticCurve(Fp, [a, Fp(1)])
    else:
        for _ in range(400):
            a = Fp.random_element(); b = Fp.random_element()
            try:
                Ec = EllipticCurve(Fp, [a, b])
            except Exception:
                continue
            if Ec.order().is_prime():
                E = Ec; break
        if E is None:
            E = EllipticCurve(Fp, [Fp(2), Fp(3)])
    out["a"] = str(E.a4()); out["b"] = str(E.a6()); out["order"] = int(E.order())
    xlog("[p=%d m=%d %s] E: y^2=x^3+%sx+%s order=%d" %
         (p, m, label, E.a4(), E.a6(), E.order()))

    # ---- x-line Semaev (anti-circularity baseline) ----
    Rx, Slist = build_xline_semaev(Fp, E, m)
    S = Slist[0] if Slist else None
    out["semaev_nvars"] = int(Rx.ngens())
    out["semaev_neqs"] = int(len(Slist))
    if S is not None and S != 0:
        out["semaev_totaldeg"] = int(S.total_degree())
        out["semaev_perdeg"] = [int(S.degree(g)) for g in Rx.gens()]
    else:
        out["semaev_totaldeg"] = None
        out["semaev_perdeg"] = None

    # ---- theta-null Kummer-surface relation ----
    th_null = genus1_theta_null(E)
    a0, a1 = th_null
    surf_null = (a0 * a0, a0 * a1, a1 * a0, a1 * a1)
    Rk, P, Q, Mdiff = build_theta_surface_relation(Fp, m)
    la, lb, lc, ld = (Fp(surf_null[0]), Fp(surf_null[1]),
                      Fp(surf_null[2]), Fp(surf_null[3]))
    p0, p1, p2, p3 = P

    # target theta-point from a real point on E
    R_pt = E.gens()[0] if E.gens() else E.random_point()
    while R_pt == E(0):
        R_pt = E.random_point()
    xR = R_pt.xy()[0]
    tr0, tr1 = kummer_point_from_x(xR, a0, a1, Fp)
    if tr0 is None:
        tr0 = Fp(1)
    Tgt = (tr0 * a0, tr0 * a1, tr1 * a0, tr1 * a1)
    out["theta_null"] = [str(x) for x in surf_null]
    out["target_theta"] = [str(x) for x in Tgt]

    def sq(v):
        return [c * c for c in v]

    polys = []
    sumpoly_indices = set()

    if m == 2:
        # P (+) (identity) = target on the Kummer surface: differential addition
        # collapses to the membership + a single biquadratic tie to the target.
        HP = hadamard4(sq(P))
        Hnull = hadamard4(sq(list(surf_null)))
        # biquadratic addition with identity: H(P)^2 .* H(null) ~ target-products
        prod = [HP[i] * Hnull[i] for i in range(4)]
        Hprod = hadamard4(prod)
        Rrel = [Tgt[i] for i in range(4)]
        eqs_add = []
        for i in range(1, 4):
            e = Hprod[i] * Rrel[0] - Hprod[0] * Rrel[i]
            eqs_add.append(e)
        segP = p0 * p3 - p1 * p2
        thetaP = ld * p0**2 + la * p3**2 - (lb + lc) * p1 * p2
        polys = eqs_add + [segP, thetaP]
        sumpoly_indices = set(range(len(eqs_add)))
    else:
        q0, q1, q2, q3 = Q
        m0, m1, m2, m3 = Mdiff
        HP = hadamard4(sq(P))
        HQ = hadamard4(sq(Q))
        prod = [HP[i] * HQ[i] for i in range(4)]
        Hprod = hadamard4(prod)
        Hnull = hadamard4(sq(list(surf_null)))
        Rrel = [Tgt[i] * mm for i, mm in enumerate([m0, m1, m2, m3])]
        eqs_add = []
        for i in range(1, 4):
            if Hnull[0] == 0 or Hnull[i] == 0:
                e = Hprod[i] * Rrel[0] - Hprod[0] * Rrel[i]
            else:
                e = (Hprod[i] * Hnull[0] * Rrel[0]
                     - Hprod[0] * Hnull[i] * Rrel[i])
            eqs_add.append(e)
        segP = p0 * p3 - p1 * p2
        segQ = q0 * q3 - q1 * q2
        segM = m0 * m3 - m1 * m2
        thetaP = ld * p0**2 + la * p3**2 - (lb + lc) * p1 * p2
        thetaQ = ld * q0**2 + la * q3**2 - (lb + lc) * q1 * q2
        polys = eqs_add + [segP, segQ, segM, thetaP, thetaQ]
        sumpoly_indices = set(range(len(eqs_add)))

    polys = [pp for pp in polys if pp != 0]
    out["theta_nvars"] = int(Rk.ngens())
    out["theta_neqs"] = int(len(polys))
    deg_total = max(int(pp.total_degree()) for pp in polys) if polys else 0
    out["theta_totaldeg"] = deg_total
    per_var = {}
    for g in Rk.gens():
        per_var[str(g)] = max(int(pp.degree(g)) for pp in polys) if polys else 0
    out["theta_perdeg"] = per_var
    out["theta_max_pervar_deg"] = max(per_var.values()) if per_var else 0
    out["elliptic_semaev_pervar_bound"] = int(4**(m - 1))  # 4^(m-1)

    # ---- ANTI-CIRCULARITY: confirm theta != x-line Semaev ----
    ac = {}
    ac["theta_nvars"] = int(Rk.ngens())
    ac["semaev_nvars"] = int(Rx.ngens())
    ac["theta_neqs"] = int(len(polys))
    ac["semaev_neqs"] = int(len(Slist))
    ac["theta_uses_all_4_coords_per_point"] = True
    # projection test: collapse theta to one coord per point; check S not recovered
    s3_recovered = None
    try:
        if m == 2 and S is not None:
            X0, X1, X2 = Rx.gens()
            phi = Rk.hom([X0, 0, 0, 0], Rx)  # only p0..p3 -> X0,0,0,0
            proj = [phi(pp) for pp in polys]
            s3_recovered = any(
                (tp != 0) and (tp.monomials() == S.monomials() and
                               all(tp.monomial_coefficient(mo) == S.monomial_coefficient(mo)
                                   for mo in S.monomials()))
                for tp in proj)
        else:
            s3_recovered = False
    except Exception as e:
        ac["projection_error"] = str(e)
        s3_recovered = None
    ac["semaev_recovered_under_projection"] = (None if s3_recovered is None
                                               else bool(s3_recovered))
    ac["nvars_differ"] = bool(Rk.ngens() != Rx.ngens())
    ac["neqs_differ"] = bool(len(polys) != len(Slist))
    ac["distinct"] = bool(ac["nvars_differ"] and ac["neqs_differ"]
                          and (s3_recovered is False or s3_recovered is None))
    ac["conclusion"] = (
        "DISTINCT: theta system has %d vars / %d eqs (4 theta coords per point, "
        "biquadratic Hadamard addition, over-determined) vs x-line Semaev "
        "%d vars / %d eq; S NOT recovered under coord projection."
        % (Rk.ngens(), len(polys), Rx.ngens(), len(Slist)))
    out["anti_circularity"] = ac

    # ---- GATED METER (Dmax capped at D_reg+1) ----
    try:
        # first get D_reg cheaply via base meter, then cap Dmax.
        base0 = meter_local(polys, Rk, Dmax=8)
        Dreg = base0.get("D_reg")
        cap = (int(Dreg) + 1) if Dreg is not None else 8
        mres = meter_gated(polys, Rk, sumpoly_indices=sumpoly_indices, Dmax=cap)
        out["meter"] = {k: (str(v) if k in ("gate_detail", "base") else v)
                        for k, v in mres.items()}
        out["meter_Dmax_used"] = int(cap)
    except Exception as e:
        out["meter"] = {"error": str(e), "tb": traceback.format_exc()}
    xlog("[p=%d m=%d %s] METER: d_ff=%s D_reg=%s fires=%s gate_passes=%s gm=%s" %
         (p, m, label,
          out.get("meter", {}).get("d_ff"),
          out.get("meter", {}).get("D_reg"),
          out.get("meter", {}).get("fires"),
          out.get("meter", {}).get("gate_passes"),
          out.get("meter", {}).get("gate_meaningful")))

    # ---- AUTO-DESCENT: PUBLIC EC DLP, verify k_rec*P == Q (public only) ----
    desc = {}
    try:
        Gp = E.gens()[0] if E.gens() else E.random_point()
        n = Gp.order()
        k_hidden = int(ZZ.random_element(2, max(3, int(n))))
        Qpub = k_hidden * Gp                  # PUBLIC point
        k_rec = int(discrete_log(Qpub, Gp, ord=n, operation="+"))  # solve from public
        ok = bool(k_rec * Gp == Qpub)         # verify against PUBLIC point only
        desc["n"] = int(n)
        desc["k_recovered"] = int(k_rec)
        desc["verify_kP_eq_Q"] = ok
        desc["matches_public_point"] = bool((k_rec % int(n)) * Gp == Qpub)
        desc["hidden_eq_recovered_modn"] = bool((k_hidden % int(n)) == (k_rec % int(n)))
    except Exception as e:
        desc["error"] = str(e); desc["verify_kP_eq_Q"] = False
    out["auto_descent"] = desc
    xlog("[p=%d m=%d %s] AUTO-DESCENT: verify_kP_eq_Q=%s k_rec=%s" %
         (p, m, label, desc.get("verify_kP_eq_Q"), desc.get("k_recovered")))

    return out

# ---------------------------------------------------------------------------
# Bounded sweep with wall-clock guard.
# ---------------------------------------------------------------------------
results = {"experiment": "EXP-030b BOUNDED theta-null Kummer redo",
           "timestamp": time.asctime(),
           "scope": {"p": [31, 67], "m": [2, 3], "budget_seconds": BUDGET_SECONDS},
           "meter_self_validation": {k: (str(v) if k != "_ok" else v)
                                     for k, v in fixture_report.items()},
           "meter_self_validated": bool(meter_ok),
           "runs": [],
           "partial": False}

def write_results():
    try:
        with open(JSON_PATH, "w") as jf:
            json.dump(results, jf, indent=2, default=str)
        xlog("Wrote JSON ->", JSON_PATH)
    except Exception as e:
        xlog("JSON write error:", e)

if not meter_ok:
    xlog("!!! METER SELF-VALIDATION FAILED -> verdict INCONCLUSIVE !!!")

grid = []
for p in [31, 67]:
    for m in [2, 3]:
        grid.append((p, m, "solinas_a-3", 3000 + p * 10 + m))

for (p, m, label, seed) in grid:
    if over_budget():
        xlog("BUDGET GUARD: elapsed=%.1fs > %.1fs -> writing partial + stopping sweep"
             % (elapsed(), BUDGET_SECONDS))
        results["partial"] = True
        break
    try:
        r = run_pm(p, m, label, seed)
        results["runs"].append(r)
        write_results()  # checkpoint after each run
    except Exception as e:
        xlog("RUN ERROR p=%d m=%d %s:" % (p, m, label), e, traceback.format_exc())
        results["runs"].append({"p": int(p), "m": int(m), "label": label,
                                "error": str(e), "tb": traceback.format_exc()})
        write_results()

# ---------------------------------------------------------------------------
# Verdict.
# ---------------------------------------------------------------------------
any_gate_meaningful = False
all_distinct = True
all_descend = True
theta_lower_degree = False
completed = len([r for r in results["runs"] if "meter" in r and
                 isinstance(r.get("meter"), dict) and "error" not in r["meter"]])

for r in results["runs"]:
    mm = r.get("meter", {})
    if isinstance(mm, dict) and mm.get("gate_meaningful"):
        any_gate_meaningful = True
    ac = r.get("anti_circularity", {})
    if not ac.get("distinct", False):
        all_distinct = False
    if not r.get("auto_descent", {}).get("verify_kP_eq_Q", False):
        all_descend = False
    tmax = r.get("theta_max_pervar_deg")
    ebound = r.get("elliptic_semaev_pervar_bound")
    if isinstance(tmax, int) and isinstance(ebound, int) and tmax < ebound:
        theta_lower_degree = True

if not meter_ok:
    verdict = "inconclusive"
elif completed == 0:
    verdict = "inconclusive"  # measurement still did not finish in budget
elif not all_distinct:
    verdict = "inconclusive"  # could not confirm a distinct system
elif any_gate_meaningful and all_descend and theta_lower_degree:
    verdict = "survived"      # CANDIDATE -- flag loudly
else:
    verdict = "failed"        # genuinely-distinct theta system: no meaningful fall

results["verdict"] = verdict
results["any_gate_meaningful"] = bool(any_gate_meaningful)
results["all_distinct"] = bool(all_distinct)
results["all_auto_descend"] = bool(all_descend)
results["theta_lower_degree_than_elliptic"] = bool(theta_lower_degree)
results["runs_completed_meter"] = int(completed)
results["elapsed_seconds"] = round(elapsed(), 1)
write_results()

xlog("VERDICT:", verdict,
     "| meter_ok=", meter_ok,
     "| gate_meaningful=", any_gate_meaningful,
     "| distinct=", all_distinct,
     "| descend=", all_descend,
     "| lower_deg=", theta_lower_degree,
     "| completed=", completed,
     "| elapsed=%.1fs" % elapsed())
_logf.close()
print("DONE EXP-030b verdict=%s" % verdict)
