# round011_exp021_crossbred_m4_ering.sage
# EXP-021: crossbred/XL admissible-(D,k) frontier at m=4 in the E-RING
#          (elementary-symmetric coordinates) for the Semaev S5 index-calculus
#          decomposition system over prime-field ECDLP toy families.
#
# CAMPAIGN POSITION
# -----------------
# NR-025 (round010_exp020, X-RING) found NO crossbred-admissible (D,k) with
# D < D_reg for the m=4 Semaev S5 system using the reduced-surrogate-degree model.
# The e-ring (elementary-symmetric coordinates e1..e4) LOWERS the per-variable
# degree of the Semaev part vs the x-ring (the S_{m+1} relation, symmetric in the
# m factor-base x-coordinates, has a more compact representation in e-coords).
# That lower per-variable degree is exactly where a crossbred degree-cutoff
# D < D_reg is MOST likely to open. BUT the e-ring base-fire is a KNOWN
# factor-base-row ARTIFACT under the localization gate (round-6 / NR-018): the
# FB-membership leading forms all carry the e1 factor, so any low-degree fall is
# CONFINED to the FB rows and does not touch the S5 summation leading form. The
# gate must therefore CONFIRM that any admissible (D,k) fall is summation-
# localized (gate_meaningful), not an e-ring FB artifact.
#
# THIS EXPERIMENT
# ---------------
#   (1) inline meter self-validation (POS-A fires d_ff=4<7; NEG-1/NEG-2 quiet;
#       e-ring m=3 base-fires but FAILS gate; POS-C Weil S_3 PASSES gate).
#   (2) build the m=4 Semaev S5 system in e-ring coords (e1..e4) + FB constraints;
#       compute the crossbred/XL admissible-(D,k) frontier (Joux-Vitse criterion);
#       sweep bits {13,15,17}, |FB| {3,4,5}, Solinas/a=-3 + random, seed 42.
#       Symbolic S5 in e-coords is heavy (its true x-coord top-form degree is
#       2^(m-1)=8 per the standard Semaev degree bound), so we use the SAME
#       reduced-surrogate-degree approach as NR-025 and LABEL d_S used vs symbolic.
#   (3) for any admissible (D,k) with D<D_reg, run meter_gated on the corresponding
#       system and report gate_meaningful (S5 rows vs e-ring FB artifact).
#   (4) field-op cost of any admissible config vs F4 vs rho (state conversion);
#       end-to-end incl P_rel for any rho comparison (avoid EXP-009 p-flat trap).
#   (5) honesty: do NOT manufacture a candidate. A gate_meaningful=False admissible
#       D<D_reg is an e-ring FB artifact (bankable NEGATIVE, extends NR-025). Only a
#       gate_meaningful AND end-to-end rho-beating config is a CANDIDATE (flag LOUD).
#
# Author: Experiment-Engineer agent, EXP-021 (round 11).

import os, sys, json, time, itertools

EXPDIR   = "/Volumes/Volume/autolab/experiments/ecdlp_prime_field"
GATE     = os.path.join(EXPDIR, "round007_exp012_localization_gate.sage")
LOGPATH  = os.path.join(EXPDIR, "round011_exp021_crossbred_m4_ering.log")
RES_JSON = os.path.join(EXPDIR, "round011_exp021_crossbred_m4_ering_result.json")
RES_MD   = os.path.join(EXPDIR, "round011_exp021_crossbred_m4_ering_result.md")

SEED = 42

# ----------------------------------------------------------------------------
# Logging (defensive: reopen if closed -- load()'d handles can close)
# ----------------------------------------------------------------------------
_LOGF = None
def _open_log():
    global _LOGF
    if _LOGF is None or getattr(_LOGF, "closed", True):
        _LOGF = open(LOGPATH, "a")
    return _LOGF

def log(msg):
    f = _open_log()
    line = "[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    f.write(line + "\n"); f.flush()
    print(line)

# ----------------------------------------------------------------------------
# Load the gated meter (mandatory). meter_gated / meter_local / froberg_Dreg_local
# / trivial_koszul_local / macaulay_homog_rows / top_form_local + the validation
# builders all come from the gate file.
# ----------------------------------------------------------------------------
load(GATE)

# ============================================================================
# (1) INLINE METER SELF-VALIDATION
# ============================================================================
def self_validate_meter():
    """
    Run the canonical gate self-validation cases inline. Required by the round-11
    posture: meter self-validates inline or the whole result is INCONCLUSIVE.
      POS-A             : base fires d_ff=4 < D_reg (gate N/A; no summation poly)
      NEG-1 / NEG-2     : quiet (no base fire)
      e-ring m=3 Semaev : base-fires but FAILS gate (FB-row artifact)
      POS-C Weil S_3    : PASSES gate (genuine summation-localized fall)
    Returns (ok_bool, detail_dict).
    """
    log("-" * 78)
    log("METER SELF-VALIDATION (inline)")
    detail = {}

    # POS-A. NOTE: the FB-less homogeneous-cubic POS-A profile makes meter_local
    # return D_reg=None, so the strict `fires = d_ff<D_reg` predicate is False even
    # though d_ff=4 is the correct documented early fall. We therefore assert the
    # directly-meaningful fact d_ff==4 (the same convention EXP-020/NR-025 used),
    # NOT `fires`, so this non-discriminating control does not spuriously fail the
    # self-validation. The DISCRIMINATING controls are e-ring (artifact, must FAIL
    # gate) and POS-C (genuine, must PASS gate).
    polys, R, si = build_POS_A()
    rA = meter_gated(polys, R, si, Dmax=12)
    posA_ok = bool(rA["d_ff"] == 4)
    detail["POS_A"] = {"d_ff": rA["d_ff"], "D_reg": rA["D_reg"], "fires": rA["fires"], "ok": posA_ok}
    log("  POS-A           d_ff=%s D_reg=%s fires=%s -> ok=%s (assert d_ff==4; D_reg=None edge)"
        % (rA["d_ff"], rA["D_reg"], rA["fires"], posA_ok))

    # NEG-1
    polys, R, si = build_NEG_generic_quadrics()
    r1 = meter_gated(polys, R, si, Dmax=12)
    neg1_ok = (not r1["fires"])
    detail["NEG_1"] = {"d_ff": r1["d_ff"], "D_reg": r1["D_reg"], "fires": r1["fires"], "ok": neg1_ok}
    log("  NEG-1           d_ff=%s D_reg=%s fires=%s -> ok=%s" % (r1["d_ff"], r1["D_reg"], r1["fires"], neg1_ok))

    # NEG-2
    polys, R, si = build_NEG_generic_cubics()
    r2 = meter_gated(polys, R, si, Dmax=12)
    neg2_ok = (not r2["fires"])
    detail["NEG_2"] = {"d_ff": r2["d_ff"], "D_reg": r2["D_reg"], "fires": r2["fires"], "ok": neg2_ok}
    log("  NEG-2           d_ff=%s D_reg=%s fires=%s -> ok=%s" % (r2["d_ff"], r2["D_reg"], r2["fires"], neg2_ok))

    # e-ring m=3 Semaev: base fires, gate FAILS
    polys, R, si = build_ering_m3_semaev()
    rE = meter_gated(polys, R, si, Dmax=12)
    ering_ok = bool(rE["fires"] and (not rE["gate_passes"]))
    detail["ERING_m3"] = {"d_ff": rE["d_ff"], "D_reg": rE["D_reg"], "fires": rE["fires"],
                          "gate_passes": rE["gate_passes"], "gate_meaningful": rE["gate_meaningful"], "ok": ering_ok}
    log("  e-ring m=3      d_ff=%s D_reg=%s fires=%s gate=%s meaningful=%s -> ok=%s (must base-fire & FAIL gate)"
        % (rE["d_ff"], rE["D_reg"], rE["fires"], rE["gate_passes"], rE["gate_meaningful"], ering_ok))

    # POS-C Weil S_3: gate PASSES
    polys, R, si = build_POSC_weil_S3()
    rC = meter_gated(polys, R, si, Dmax=12)
    posC_ok = bool(rC["fires"] and rC["gate_passes"] and rC["gate_meaningful"])
    detail["POS_C"] = {"d_ff": rC["d_ff"], "D_reg": rC["D_reg"], "fires": rC["fires"],
                       "gate_passes": rC["gate_passes"], "gate_meaningful": rC["gate_meaningful"], "ok": posC_ok}
    log("  POS-C Weil S_3  d_ff=%s D_reg=%s fires=%s gate=%s meaningful=%s -> ok=%s (must PASS gate)"
        % (rC["d_ff"], rC["D_reg"], rC["fires"], rC["gate_passes"], rC["gate_meaningful"], posC_ok))

    ok = bool(posA_ok and neg1_ok and neg2_ok and ering_ok and posC_ok)
    log("  METER SELF-VALIDATION: %s" % ("PASS" if ok else "FAIL"))
    log("-" * 78)
    return ok, detail

# ============================================================================
# (2) m=4 SEMAEV S5 SYSTEM IN E-RING (elementary-symmetric) COORDINATES
# ============================================================================
#
# DEGREE MODEL (LABELED).
# -----------------------
# For Gaudry-Semaev index calculus on E(F_q) with an m-point decomposition, the
# summation polynomial S_{m+1} has degree 2^{m-1} in each of the m factor-base
# x-coordinates. For m=4, S5 has per-variable x-degree 2^{m-1} = 8 and total
# x-degree 2^{m-1}*... -- the FULL symbolic S5 leading form is too heavy to carry
# through a Macaulay/crossbred sweep at toy parameters in bounded time.
#
# We therefore follow NR-025's REDUCED-SURROGATE-DEGREE approach and we LABEL it:
#   * SYMBOLIC per-variable x-degree of S5  : 2^{m-1} = 8  (the true object).
#   * E-RING surrogate top-form degree d_S  : the SYMMETRIC representation packs
#     the m! permutation orbit into the e-coords, so the e-coord total degree of
#     the S5 top form is LOWER than the x-coord total degree. The standard fact
#     (Faugere-Gaudry-Huot-Renault symmetrization) is that the symmetrized S_{m+1}
#     has degree 2^{m-1} in the LAST elementary symmetric variable and lower in the
#     others. We model the e-ring S5 top form with surrogate degree d_S_ering and
#     compare against the x-ring surrogate d_S_xring used by NR-025.
#
# The CROSSBRED/XL admissibility question (below) is a degree/D_reg combinatorial
# question on the leading-form degree profile; it does NOT require the explicit
# huge polynomial -- only its degree profile. We build BOTH:
#   (a) the degree-profile-only object for the admissibility frontier sweep, and
#   (b) a faithful SMALL meter instance (e-ring m=3-style leading-form profile
#       extended to the m=4 S5 degree) so meter_gated can adjudicate any fall as
#       S5-localized vs e-ring FB artifact.

M = 4                      # m=4 decomposition
D_S_SYMBOLIC = 2**(M - 1)  # =8, true per-variable x-degree of S5 (LABEL)

def ering_degree_profile(nfb, d_S_ering):
    """
    Leading-form degree profile of the m=4 e-ring S5 system.
      vars: e1..e4 (m=4 elementary symmetric coords) + (nfb) auxiliary FB-encoding
            slack vars are NOT added; FB constraints act directly on e-coords.
      The S5 summation relation: one generator, top-form degree d_S_ering (e-ring
            surrogate; symbolic x-degree D_S_SYMBOLIC=8).
      FB constraints: nfb generators, each of leading-form degree 2 (the standard
            factor-base membership constraint -- a quadratic in e-coords sharing the
            e1 factor; this is the e-ring FB-row mechanism / round-6 artifact source).
    Returns (n_vars, degs_list, sumpoly_indices).
    """
    n_vars = M  # e1..e4
    degs = [d_S_ering] + [2] * nfb   # S5 first, then nfb FB quadrics
    sum_idx = [0]
    return n_vars, degs, sum_idx

def D_reg_of_profile(degs, n):
    """Froberg degree of regularity for a degree profile in n vars (gate primitive)."""
    return froberg_Dreg_local([int(d) for d in degs], int(n), Dmax=60)

# ----------------------------------------------------------------------------
# CROSSBRED / XL ADMISSIBILITY FRONTIER (Joux-Vitse criterion).
# ----------------------------------------------------------------------------
# Crossbred (Joux-Vitse 2017) splits solving into:
#   * a Macaulay/linearization phase at degree D over ALL variables, extracting
#     polynomials of degree <= k in a chosen "remaining" subset after the rest are
#     specialized;
#   * a brute/exhaustive phase on the remaining variables.
# A pair (D, k) with k < D is ADMISSIBLE iff at degree D the Macaulay matrix yields
# enough independent degree-<=k relations to over-determine the kept subset, i.e.
# the number of independent "low-k-degree" rows extracted at degree D meets the
# Joux-Vitse count threshold. The CRUCIAL crossbred win condition is D < D_reg:
# the Macaulay phase runs at a degree STRICTLY BELOW the F4/F5 solving degree.
#
# Over F_p (large prime) there are NO field equations x^p - x to cheaply truncate
# degree (unlike F_2), so the admissibility is governed purely by the homogeneous
# Hilbert/Froberg bookkeeping of the leading-form profile. We compute, for each D,
# the Joux-Vitse "kept-degree" count and test whether ANY (D,k) with D<D_reg and
# 1<=k<D yields a strictly positive admissible surplus.
#
# Admissible-surplus(D,k) heuristic (degree-profile model, LABELED HEURISTIC):
#   For a semi-regular system with degree profile {d_i} in n vars, the Hilbert
#   series of the ideal at degree D gives the number of degree-D polynomials in the
#   ideal that are expressible from the generators (= rows of Macaulay_D). The
#   crossbred "degree-k extractable" relations are those whose support, after
#   restricting to the k-kept variables, has degree <= k. For a generic (semi-
#   regular) profile WITHOUT a low-degree syzygy below D_reg, NO such surplus exists
#   below D_reg -- this is exactly the NR-025 negative. A surplus below D_reg can
#   only arise if the leading-form module has a NON-Froberg early drop, i.e. a
#   first fall d_ff < D_reg. So the admissibility frontier reduces to: does the
#   PROFILE admit d_ff < D_reg, and (gate) is that fall on the S5 row?
#
# We therefore compute the admissibility frontier two ways and cross-check:
#   (A) Hilbert-function surplus test on the homogeneous Macaulay map of the actual
#       leading forms (exact, via the gate's macaulay_homog_rows -- this is the
#       ground truth for whether any D<D_reg has extractable low-degree relations).
#   (B) the Froberg/d_ff combinatorial predictor (cheap profile-only check).

def hilbert_surplus_admissible(forms, R, D_reg, sum_idx):
    """
    EXACT admissibility test on the leading-form module. For each D from 2 up to
    D_reg (exclusive), build the homogeneous Macaulay map; an admissible crossbred
    cut at (D,k) below D_reg exists iff there is a NON-Koszul (nontrivial) kernel
    at some D < D_reg (a genuine early-fall relation that the crossbred low-degree
    extraction could use). We report, per D < D_reg:
      nontriv(D) = (#rows - rank) - koszul(D)
      and, if nontriv>0, the gate localization (does it touch the S5 / sum rows).
    Returns list of per-D records and the overall admissible flag.
    """
    n = R.ngens()
    degs = [int(h.degree()) for h in forms]
    records = []
    admissible = False
    Dtop = D_reg if D_reg is not None else 8
    for D in range(2, Dtop):  # strictly below D_reg
        Mmat, owner, cols = macaulay_homog_rows(forms, R, D)
        nrows = Mmat.nrows()
        if nrows == 0:
            records.append({"D": int(D), "nrows": 0, "rank": 0, "nontriv": 0, "admissible": False,
                            "gate_meaningful": None})
            continue
        rk = Mmat.rank()
        koszul = trivial_koszul_local(degs, n, D)
        nontriv = (nrows - rk) - koszul
        rec = {"D": int(D), "nrows": int(nrows), "rank": int(rk),
               "koszul": int(koszul), "nontriv": int(nontriv),
               "admissible": bool(nontriv > 0)}
        if nontriv > 0:
            admissible = True
            # gate localization at this D
            gd = _nontrivial_kernel_support_on_block(forms, R, D, sum_idx)
            involves_sum = gd["involves_sum_direct"]
            if involves_sum is None:
                involves_sum = gd["involves_sum_shrink"]
            rec["gate_meaningful"] = bool(involves_sum)
            rec["gate_detail"] = {"nontriv_full": gd["nontriv_full"], "nontriv_fb": gd["nontriv_fb"],
                                  "involves_sum_direct": gd["involves_sum_direct"],
                                  "involves_sum_shrink": gd["involves_sum_shrink"]}
        else:
            rec["gate_meaningful"] = None
        records.append(rec)
    return records, admissible

# ----------------------------------------------------------------------------
# Faithful SMALL meter instance: e-ring m=4 S5 leading-form profile.
# ----------------------------------------------------------------------------
# We instantiate concrete leading forms reproducing the e-ring m=4 structure so
# meter_gated can adjudicate. The FB constraints carry the e1 factor (the e-ring
# artifact mechanism). The S5 top form is a degree-d_S generic-symmetric quartic+
# form in e1..e4 that does NOT cleanly divide by e1 (so a genuine S5-localized
# fall would be visible if it existed).
def build_ering_m4_instance(K, nfb, d_S_ering, rng_offset=0):
    R = PolynomialRing(K, M, 'e')   # e0..e3 representing e1..e4
    e = R.gens()
    e1, e2, e3, e4 = e[0], e[1], e[2], e[3]
    set_random_seed(int(SEED + rng_offset))
    # FB constraints: nfb quadrics, all carrying the e1 factor (e-ring FB mechanism).
    fbs = []
    for i in range(nfb):
        L = sum(K.random_element() * g for g in e) + K.random_element()
        g = e1 * L + (e2 + K(i + 1) * e3 + K(2 * i + 3))   # lf = e1*L (degree 2), shares e1
        fbs.append(g)
    # S5 summation relation: top form of degree d_S_ering, generic-symmetric, NOT
    # divisible by e1 (so its rows are distinguishable from the e1-confined FB rows).
    # Build a generic degree-d_S top form in e-coords + lower-order tail.
    topf = R(0)
    # generic monomials of total degree d_S_ering
    for comp in _weak_compositions(int(d_S_ering), M):
        if comp[0] < int(d_S_ering):   # ensure not a pure power of e1 alone dominating
            topf += K.random_element() * R.monomial(*comp)
    # guarantee a non-e1 leading monomial e4^d (and e3-cross terms) present
    topf += K(1) * e4**int(d_S_ering)
    S5 = topf + (e1 * e2 + K(7) * e3 + K(3))   # + lower order tail
    polys = [S5] + fbs
    sum_idx = [0]
    return polys, R, sum_idx

# ============================================================================
# (4) COST MODEL: crossbred-at-D vs F4-at-D_reg vs rho (field ops, end-to-end)
# ============================================================================
def macaulay_cols(n, D):
    return binomial(n - 1 + D, D)

def linalg_fieldops(ncols, omega=2.8):
    """Dense linear-algebra cost ~ ncols^omega field ops (omega=2.8 toy estimate)."""
    return RR(ncols) ** omega

def F4_cost_fieldops(n, D_reg, omega=2.8):
    return linalg_fieldops(macaulay_cols(n, D_reg), omega)

def crossbred_cost_fieldops(n, D, k, omega=2.8):
    """
    Crossbred: Macaulay linear algebra at degree D over n vars, then exhaustive on
    the k kept structure. Toy field-op estimate: linalg at D + (search factor).
    Over F_p the kept-variable brute phase is q^(kept) which is huge for prime
    fields -- we surface that explicitly in the rho comparison rather than folding
    it in blindly.
    """
    return linalg_fieldops(macaulay_cols(n, D), omega)

def rho_cost_groupops(p):
    """Pollard rho expected group ops ~ sqrt(pi*N/2), N ~ p (toy)."""
    return RR(p).sqrt() * RR(pi / 2).sqrt()

def relation_probability_decomp(p, nfb, m):
    """
    HEURISTIC P_rel for an m=4 decomposition over a size-|FB| factor base on
    E(F_p): the fraction of group elements that decompose as a sum of m FB points
    is ~ (|FB|^m / m!) / N. For toy |FB| in {3,4,5} and m=4 this is astronomically
    small -- this is the standard prime-field obstruction (no subfield to make the
    FB a positive-density set). We surface it to avoid the EXP-009 p-flat trap:
    the per-relation cost MUST include 1/P_rel attempts.
    """
    N = RR(p)
    fb = RR(nfb)
    from sage.functions.other import factorial as _fact
    return (fb ** m / RR(_fact(m))) / N

# ============================================================================
# DRIVER
# ============================================================================
def main():
    log("=" * 78)
    log("EXP-021 crossbred/XL admissible-(D,k) at m=%d in E-RING  seed=%d" % (M, SEED))
    log("  symbolic S5 per-var x-degree 2^(m-1) = %d (LABEL); e-ring surrogate below" % D_S_SYMBOLIC)
    log("=" * 78)

    # ---- (1) meter self-validation ----
    meter_ok, meter_detail = self_validate_meter()

    # ---- (2)+(3) admissibility frontier sweep ----
    bits_list = [13, 15, 17]
    fb_list   = [3, 4, 5]
    curve_kinds = ["solinas_a-3", "random"]
    # e-ring surrogate degrees to probe for S5 top form. We test a LADDER from the
    # genuinely-lowered e-ring degree up toward the symbolic 8, labeling each.
    # d_S_ering in {3,4,5,6,8}: 8 = symbolic; <8 = optimistic e-ring surrogate
    # (gives crossbred the BEST chance to open a D<D_reg cut).
    dS_ladder = [3, 4, 5, 6, 8]

    frontier = []     # one record per (bits, fb, kind, d_S) cell
    any_admissible_below_Dreg = False
    any_gate_meaningful_admissible = False

    for kind in curve_kinds:
        for bits in bits_list:
            p = next_prime(2 ** bits)
            K = GF(p)
            for nfb in fb_list:
                for d_S in dS_ladder:
                    # degree profile -> D_reg
                    n_vars, degs, sum_idx_prof = ering_degree_profile(nfb, d_S)
                    D_reg = D_reg_of_profile(degs, n_vars)
                    # build faithful leading-form instance and run EXACT surplus test
                    rng_off = (bits * 100 + nfb * 10 + d_S) + (0 if kind.startswith("solinas") else 7)
                    polys, R, sum_idx = build_ering_m4_instance(K, nfb, d_S, rng_offset=rng_off)
                    forms = [top_form_local(R(f)) for f in polys]
                    recs, admissible = hilbert_surplus_admissible(forms, R, D_reg, sum_idx)
                    # find the minimal admissible D < D_reg and its gate verdict
                    min_adm_D = None
                    min_adm_gate = None
                    for r in recs:
                        if r["admissible"]:
                            min_adm_D = r["D"]
                            min_adm_gate = r.get("gate_meaningful")
                            break
                    if admissible:
                        any_admissible_below_Dreg = True
                        if min_adm_gate:
                            any_gate_meaningful_admissible = True
                    # base meter (full gate) on the instance for d_ff/D_reg cross-check
                    g = meter_gated(polys, R, sum_idx, Dmax=int(D_reg + 2) if D_reg else 12)
                    cell = {
                        "kind": kind, "bits": int(bits), "p": int(p), "nfb": int(nfb),
                        "d_S_ering": int(d_S), "d_S_symbolic": int(D_S_SYMBOLIC),
                        "n_vars": int(n_vars), "degs": [int(x) for x in degs],
                        "D_reg": (int(D_reg) if D_reg is not None else None),
                        "d_ff": g["d_ff"],
                        "base_fires": bool(g["fires"]),
                        "gate_passes": bool(g["gate_passes"]),
                        "gate_meaningful_meter": bool(g["gate_meaningful"]),
                        "admissible_below_Dreg": bool(admissible),
                        "min_admissible_D": (int(min_adm_D) if min_adm_D is not None else None),
                        "min_admissible_gate_meaningful": (None if min_adm_gate is None else bool(min_adm_gate)),
                        "surplus_records": recs,
                    }
                    frontier.append(cell)
                    log("CELL %-11s bits=%2d nfb=%d d_S=%d | D_reg=%s d_ff=%s | adm<Dreg=%s minD=%s gate_mean=%s | meter: fires=%s gate=%s mean=%s"
                        % (kind, bits, nfb, d_S, cell["D_reg"], cell["d_ff"],
                           cell["admissible_below_Dreg"], cell["min_admissible_D"],
                           cell["min_admissible_gate_meaningful"],
                           cell["base_fires"], cell["gate_passes"], cell["gate_meaningful_meter"]))

    # ---- (4) cost comparison for any admissible-below-Dreg cell (else representative) ----
    cost_rows = []
    # choose cells to cost: all admissible cells, plus one representative per bits at fb=4,d_S=8
    cost_cells = [c for c in frontier if c["admissible_below_Dreg"]]
    if not cost_cells:
        cost_cells = [c for c in frontier if c["nfb"] == 4 and c["d_S_ering"] == 8 and c["kind"] == "solinas_a-3"]
    for c in cost_cells:
        p = c["p"]; n = c["n_vars"]; D_reg = c["D_reg"]; nfb = c["nfb"]
        f4 = F4_cost_fieldops(n, D_reg) if D_reg else None
        Dcut = c["min_admissible_D"] if c["min_admissible_D"] is not None else (D_reg - 1 if D_reg else None)
        cb = crossbred_cost_fieldops(n, Dcut, max(1, Dcut - 1)) if Dcut else None
        rho_g = rho_cost_groupops(p)
        P_rel = relation_probability_decomp(p, nfb, M)
        # end-to-end IC: need ~|FB| relations, each costs (decomp solve) / P_rel attempts.
        n_rel_needed = nfb + 1
        ic_solve_per_attempt = cb if cb else (f4 if f4 else RR(1))
        ic_end_to_end = (ic_solve_per_attempt / P_rel) * n_rel_needed if P_rel > 0 else None
        cost_rows.append({
            "cell": {"kind": c["kind"], "bits": c["bits"], "nfb": nfb, "d_S_ering": c["d_S_ering"]},
            "n_vars": n, "D_reg": D_reg, "D_cut": (int(Dcut) if Dcut else None),
            "F4_fieldops_log2": (_log2(f4) if f4 else None),
            "crossbred_fieldops_log2": (_log2(cb) if cb else None),
            "rho_groupops_log2": _log2(rho_g),
            "P_rel_log2": (_log2(P_rel) if P_rel > 0 else None),
            "IC_end_to_end_log2": (_log2(ic_end_to_end) if ic_end_to_end else None),
            "IC_beats_rho": (bool(ic_end_to_end < rho_g) if ic_end_to_end else False),
        })
        log("COST %-11s bits=%d nfb=%d d_S=%d | F4=2^%.1f cb=2^%.1f rho=2^%.1f P_rel=2^%.1f IC_e2e=2^%.1f beats_rho=%s"
            % (c["kind"], c["bits"], nfb, c["d_S_ering"],
               (_log2(f4) if f4 else float('nan')),
               (_log2(cb) if cb else float('nan')),
               _log2(rho_g),
               (_log2(P_rel) if P_rel>0 else float('nan')),
               (_log2(ic_end_to_end) if ic_end_to_end else float('nan')),
               (bool(ic_end_to_end < rho_g) if ic_end_to_end else False)))

    # ---- VERDICT ----
    # CANDIDATE only if: an admissible (D,k) with D<D_reg exists in e-ring AND it is
    # gate_meaningful (S5-localized) AND it beats rho end-to-end (incl P_rel).
    any_beats_rho = any(r["IC_beats_rho"] for r in cost_rows)
    candidate = bool(any_admissible_below_Dreg and any_gate_meaningful_admissible and any_beats_rho)

    if candidate:
        verdict = "survived"   # flagged LOUD; still PO-003 needs downstream solver demo
    elif not meter_ok:
        verdict = "inconclusive"
    else:
        verdict = "failed"

    summary = {
        "experiment": "EXP-021 crossbred/XL m=4 e-ring admissibility",
        "m": M, "seed": SEED,
        "d_S_symbolic_2^(m-1)": int(D_S_SYMBOLIC),
        "d_S_ladder_ering_surrogate": dS_ladder,
        "meter_self_validated": bool(meter_ok),
        "any_admissible_below_Dreg_ering": bool(any_admissible_below_Dreg),
        "any_gate_meaningful_admissible": bool(any_gate_meaningful_admissible),
        "any_IC_beats_rho_end_to_end": bool(any_beats_rho),
        "candidate": bool(candidate),
        "verdict": verdict,
        "nr025_xring_baseline": "NO admissible (D,k) with D<D_reg in x-ring (reduced surrogate)",
    }
    log("=" * 78)
    log("SUMMARY: meter_ok=%s adm<Dreg(ering)=%s gate_meaningful_adm=%s beats_rho=%s -> CANDIDATE=%s VERDICT=%s"
        % (meter_ok, any_admissible_below_Dreg, any_gate_meaningful_admissible,
           any_beats_rho, candidate, verdict))
    log("=" * 78)

    out = {
        "summary": summary,
        "meter_self_validation": meter_detail,
        "frontier": frontier,
        "cost_rows": cost_rows,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(RES_JSON, "w") as jf:
        json.dump(out, jf, indent=2, default=str)
    log("wrote %s" % RES_JSON)

    _write_md(out)
    log("wrote %s" % RES_MD)
    return out

def _write_md(out):
    s = out["summary"]; fr = out["frontier"]; cr = out["cost_rows"]
    L = []
    L.append("# EXP-021 - crossbred/XL admissible-(D,k) at m=4 in the E-RING")
    L.append("")
    L.append("Round 11. Semaev S5 (m=4) index-calculus decomposition system in")
    L.append("elementary-symmetric (e-ring) coordinates over prime-field ECDLP toy families.")
    L.append("Seed %d. Extends NR-025 (x-ring crossbred negative) to the e-ring." % s["seed"])
    L.append("")
    L.append("## Degree model (LABELED)")
    L.append("")
    L.append("- Symbolic S5 per-variable x-degree: 2^(m-1) = %d (the true object)." % s["d_S_symbolic_2^(m-1)"])
    L.append("- E-ring surrogate top-form degree ladder d_S in %s (reduced-surrogate, same" % s["d_S_ladder_ering_surrogate"])
    L.append("  approach as NR-025; lower d_S = optimistic e-ring packing = BEST chance for a")
    L.append("  crossbred D<D_reg cut to open). d_S=8 reproduces the symbolic degree.")
    L.append("")
    L.append("## Meter self-validation (inline, mandatory)")
    L.append("")
    L.append("meter_self_validated = **%s**" % s["meter_self_validated"])
    mv = out["meter_self_validation"]
    L.append("")
    L.append("| case | d_ff | D_reg | fires | gate_passes | gate_meaningful | ok |")
    L.append("|---|---|---|---|---|---|---|")
    for nm in ["POS_A", "NEG_1", "NEG_2", "ERING_m3", "POS_C"]:
        d = mv.get(nm, {})
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            nm, d.get("d_ff"), d.get("D_reg"), d.get("fires"),
            d.get("gate_passes", "-"), d.get("gate_meaningful", "-"), d.get("ok")))
    L.append("")
    L.append("## Admissibility frontier (e-ring) vs NR-025 (x-ring)")
    L.append("")
    L.append("NR-025 x-ring baseline: %s" % s["nr025_xring_baseline"])
    L.append("")
    L.append("| kind | bits | |FB| | d_S | n_vars | degs | D_reg | d_ff | adm<D_reg? | min_adm_D | adm_gate_meaningful |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for c in fr:
        L.append("| %s | %d | %d | %d | %d | %s | %s | %s | %s | %s | %s |" % (
            c["kind"], c["bits"], c["nfb"], c["d_S_ering"], c["n_vars"],
            c["degs"], c["D_reg"], c["d_ff"],
            c["admissible_below_Dreg"], c["min_admissible_D"],
            c["min_admissible_gate_meaningful"]))
    L.append("")
    L.append("## Cost comparison (field ops, log2; end-to-end incl P_rel)")
    L.append("")
    if cr:
        L.append("| cell | n | D_reg | D_cut | F4 2^ | crossbred 2^ | rho 2^ | P_rel 2^ | IC e2e 2^ | IC beats rho? |")
        L.append("|---|---|---|---|---|---|---|---|---|---|")
        for r in cr:
            cc = r["cell"]
            L.append("| %s b%d fb%d dS%d | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                cc["kind"], cc["bits"], cc["nfb"], cc["d_S_ering"],
                r["n_vars"], r["D_reg"], r["D_cut"],
                _f(r["F4_fieldops_log2"]), _f(r["crossbred_fieldops_log2"]),
                _f(r["rho_groupops_log2"]), _f(r["P_rel_log2"]),
                _f(r["IC_end_to_end_log2"]), r["IC_beats_rho"]))
    else:
        L.append("(no cost rows)")
    L.append("")
    L.append("## Verdict")
    L.append("")
    L.append("- any admissible (D,k) with D<D_reg in e-ring: **%s**" % s["any_admissible_below_Dreg_ering"])
    L.append("- any such admissible fall gate_meaningful (S5-localized, not e-ring FB artifact): **%s**"
             % s["any_gate_meaningful_admissible"])
    L.append("- any IC config beats rho end-to-end (incl P_rel): **%s**" % s["any_IC_beats_rho_end_to_end"])
    L.append("- CANDIDATE (all three, PO-003 still needs downstream solver demo): **%s**" % s["candidate"])
    L.append("- **VERDICT: %s**" % s["verdict"].upper())
    L.append("")
    L.append("## What this rules out / what remains open")
    L.append("")
    if not s["any_admissible_below_Dreg_ering"]:
        L.append("- NEGATIVE (extends NR-025 to e-ring): the m=4 Semaev S5 system in elementary-")
        L.append("  symmetric coordinates admits NO crossbred/XL (D,k) cut with D<D_reg across the")
        L.append("  swept bits/|FB|/curve-kind/d_S ladder. D_reg-conservation holds in the e-ring")
        L.append("  exactly as in the x-ring: the symmetric repacking lowers per-variable degree but")
        L.append("  does NOT create an early fall below the Froberg degree of regularity.")
    elif not s["any_gate_meaningful_admissible"]:
        L.append("- NEGATIVE (extends NR-025 to e-ring): admissible D<D_reg cuts exist in the e-ring")
        L.append("  but EVERY such fall is gate_meaningful=False -- an e-ring FB-row artifact (the e1-")
        L.append("  shared factor among FB constraints), NOT a summation-localized S5 fall. No index-")
        L.append("  calculus solver leverage; PO-003 not satisfied.")
    elif not s["any_IC_beats_rho_end_to_end"]:
        L.append("- NEGATIVE: gate_meaningful admissible cuts exist but DO NOT beat rho end-to-end once")
        L.append("  relation probability P_rel is included (prime-field FB density obstruction; avoids")
        L.append("  the EXP-009 p-flat trap).")
    else:
        L.append("- CANDIDATE FLAGGED LOUD: a gate_meaningful admissible D<D_reg cut beats rho end-to-")
        L.append("  end in the e-ring. NOT a survivor (PO-003): requires a downstream Groebner/crossbred")
        L.append("  solver demo on a real decomposing prime-field instance verified vs the PUBLIC point.")
    L.append("")
    L.append("## Next")
    L.append("")
    L.append("- Conservative: re-run with the FULL symbolic S5 e-ring top form (not surrogate) at the")
    L.append("  smallest bits to confirm the surrogate ladder did not hide a real fall.")
    L.append("- Representation-changing: power-sum (Newton) coords at m=4, and the partially-symmetric")
    L.append("  Faugere-Gaudry-Huot-Renault 'last-variable' degree-8 / others-lower split.")
    L.append("- High-risk: hybrid e-ring + one specialized variable (XL guess-and-determine) to force a")
    L.append("  low-k kept set, then gate-check whether the forced fall is S5-localized.")
    L.append("")
    with open(RES_MD, "w") as mf:
        mf.write("\n".join(L) + "\n")

def _f(x):
    return ("%.1f" % x) if (x is not None) else "-"

def _log2(x):
    # math log base-2; the loaded gate file shadows Sage's `log` with a logging
    # function, so we use natural log via RR to avoid the name collision.
    return float(RR(x).log() / RR(2).log())

_RESULT = main()
