#!/usr/bin/env python3
"""INVOCATION 1 of TASK-20260923-2d8db0 (validator, EXP-GFPN-726eb2 review round).

Independent re-verification of both GFPN run packages (J1), the embedding-degree /
CM-discriminant arithmetic (J2), and the lightweight J3 checks (SCURVE hashes and
l*B = O / Hasse regeneration; call graph; chronology), plus artifact hashes against
the snapshot receipt. Uses scratch/vlib.py (written in this session); imports nothing
from experiments/EXP-GFPN-726eb2/implementation/ and runs no PARI code.

Reads committed artifacts only. Writes only scratch/inv1/.
"""
import ast, hashlib, json, math, os, re, subprocess, sys, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib as V
from vlib import F, fe, Curve, is_sq, coeffs, P_GOLD as p, Q_GOLD as q
import mpmath
import yaml

T0 = time.time()
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
EXP = os.path.join(REPO, "experiments/EXP-GFPN-726eb2")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inv1")
os.makedirs(OUT, exist_ok=True)
assert p == 2**64 - 2**32 + 1 and "VLIB_P" not in os.environ
R = {"task": "TASK-20260923-2d8db0", "invocation": 1, "repo_head": subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()}
FAILS = []
def rec(section, key, value):
    R.setdefault(section, {})[key] = value
def must(cond, msg):
    if not cond: FAILS.append(msg); print("CHECK FAILED:", msg)
    return cond
def sha(path): return hashlib.sha256(open(path, "rb").read()).hexdigest()
def rel(pth): return os.path.relpath(pth, REPO)

# =============================================================================
# A. artifact hashes vs the snapshot receipt; frozen-input companions; trial plan
# =============================================================================
rcpt = json.load(open(os.path.join(REPO, "coordination/goals/GOAL-GFPN-380702/archives/TASK-20260921-b59aad/snapshot-receipt.json")))
mism = [k for k, v in rcpt["path_sha256"].items() if not os.path.exists(os.path.join(REPO, k)) or sha(os.path.join(REPO, k)) != v]
rec("A_artifacts", "snapshot_receipt_paths", len(rcpt["path_sha256"]))
rec("A_artifacts", "snapshot_receipt_mismatches", mism)
must(not mism, f"snapshot receipt hash mismatches: {mism}")
# every file under the three run dirs is covered by the receipt
uncovered = []
for run in ("RUN-GFPN-17ed52", "RUN-GFPN-b71f2f", "RUN-GFPN-3bbef2"):
    for dp, _dn, fn in os.walk(os.path.join(EXP, "runs", run)):
        for f in fn:
            if rel(os.path.join(dp, f)) not in rcpt["path_sha256"]: uncovered.append(rel(os.path.join(dp, f)))
rec("A_artifacts", "run_files_not_in_receipt", uncovered)
tp = json.load(open(os.path.join(EXP, "trial-plan.json")))
rec("A_artifacts", "trial_plan_source_sha256_match", {k: sha(os.path.join(REPO, k)) == v for k, v in tp["source_sha256"].items()})
rec("A_artifacts", "specification_sha256_match_trial_plan", sha(os.path.join(EXP, "specification.yaml")) == tp["specification_sha256"])
for d, f in (("inputs/PORNIN-2022-274-ECGFP5", "paper_fulltext.md"), ("inputs/ECMASFP5-HACKMD-2025", "note_fulltext.md")):
    comp = open(os.path.join(REPO, d, f + ".sha256")).read().split()[0]
    rec("A_artifacts", f"{f}_sha256_companion_match", sha(os.path.join(REPO, d, f)) == comp)
# the review plan + this card are bound by the phase-A archive receipt (DP-1)
rc3 = json.load(open(os.path.join(REPO, "coordination/goals/GOAL-GFPN-380702/archives/TASK-20260923-3b12c2/snapshot-receipt.json")))
for card in ("ledger/handoffs/TASK-20260923-cc166b.yaml", "ledger/handoffs/TASK-20260923-2d8db0.yaml"):
    v = rc3.get("path_sha256", {}).get(card)
    rec("A_artifacts", f"archived_{os.path.basename(card)}", {"in_receipt": v is not None, "sha256_match": v == sha(os.path.join(REPO, card)) if v else None})
# required artifacts present per contract
req = ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log", "raw-result.json", "audit-table.yaml", "figure-provenance.yaml", "certificates"]
rec("A_artifacts", "required_artifacts_missing", {run: [a for a in req if not os.path.exists(os.path.join(EXP, "runs", run, a))] for run in ("RUN-GFPN-17ed52", "RUN-GFPN-b71f2f", "RUN-GFPN-3bbef2")})
rec("A_artifacts", "implementation_md_present", os.path.exists(os.path.join(EXP, "implementation.md")))
rec("A_artifacts", "amendments_dir_listing", sorted(os.listdir(os.path.join(EXP, "amendments"))))

# =============================================================================
# helpers
# =============================================================================
def load_cert(path):
    txt = [l for l in open(path).read().splitlines() if l.strip()][-1]
    return json.loads(txt)

def prove(nint, cert_path=None):
    """Independent primality proof: my ECPP chain checker on the committed PARI certificate
    (large primes) or a Pratt certificate built and re-checked here (small primes)."""
    if cert_path is not None:
        ok, log = V.ecpp_check(load_cert(cert_path), nint)
        return {"method": "ECPP chain re-verified by vlib.ecpp_check", "certificate": rel(cert_path), "ok": ok, "log_tail": log[-2:]}
    c = V.pratt(nint)
    ok = c is not None and V.pratt_check(c)
    return {"method": "Pratt certificate built and re-checked here", "ok": ok}

def check_factorization(run, name, target):
    fj = json.load(open(os.path.join(EXP, "runs", run, "certificates", f"factorization-{name}.json")))
    prod = 1
    for f_ in fj["prime_factors"]: prod *= int(f_["p"]) ** f_["e"]
    for c in fj["unfactored_composites"]: prod *= int(c["c"])
    out = {"committed_n_equals_target": int(fj["n"]) == target, "product_equals_target": prod == target,
           "unfactored": fj["unfactored_composites"], "factors": []}
    allok = out["committed_n_equals_target"] and out["product_equals_target"] and not fj["unfactored_composites"]
    for f_ in fj["prime_factors"]:
        pr = int(f_["p"])
        cp = fj["primality_proofs"][f_["p"]].get("certificate")
        res = prove(pr, os.path.join(EXP, "runs", run, cp) if cp else None)
        out["factors"].append({"p": f_["p"], "e": f_["e"], "bits": pr.bit_length(), "proof": res["method"], "proved": res["ok"]})
        allok = allok and res["ok"]
    out["complete_and_proved"] = allok
    return out, {int(f_["p"]): f_["e"] for f_ in fj["prime_factors"]}

def parse_count(run):
    kv = {}
    for line in open(os.path.join(EXP, "runs", run, "certificates/pari/count.out")):
        k, _, v = line.partition("=")
        kv[k.strip()] = v.strip()
    return int(kv["N"]), int(kv["NT"])

def hasse():
    s = math.isqrt(4 * q)           # floor(2 sqrt q); 4q = 4 p^5 is not a square (p^5 is not)
    assert s * s != 4 * q
    return q + 1 - s, q + 1 + s

def mult_order(g, n, fac_nm1):
    e = n - 1
    for r in fac_nm1:
        while e % r == 0 and pow(g, e // r, n) == 1: e //= r
    return e

paper = open(os.path.join(REPO, "inputs/PORNIN-2022-274-ECGFP5/paper_fulltext.md"), encoding="utf-8").read().splitlines()
note = open(os.path.join(REPO, "inputs/ECMASFP5-HACKMD-2025/note_fulltext.md"), encoding="utf-8").read().splitlines()
def find(lines, pat):
    return [(i + 1, l) for i, l in enumerate(lines) if re.search(pat, l)]

# =============================================================================
# B. per-curve certificate re-verification (J1) and arithmetic (J2)
# =============================================================================
lo, hi = hasse()
rec("B_common", "hasse_interval", [str(lo), str(hi)])
CURVES = {}
for curve, run, h in (("EcGFp5", "RUN-GFPN-b71f2f", 2), ("EcMasFp5", "RUN-GFPN-3bbef2", 1)):
    S = {}
    rd = os.path.join(EXP, "runs", run)
    raw = json.load(open(os.path.join(rd, "raw-result.json")))
    oc = json.load(open(os.path.join(rd, "certificates/order-certificate.json")))
    N_sea, NT_sea = parse_count(run)
    # ---------- B1 model: the certified curve is the published curve
    if curve == "EcGFp5":
        a_do, b_do = F(2), fe([0, 263, 0, 0, 0])
        A = (3 * b_do - a_do * a_do) / 3                      # paper: A = (3b - a^2)/3
        B = a_do * (2 * a_do * a_do - 9 * b_do) / 27          # paper: B = a(2a^2 - 9b)/27
        Edo = Curve(2, b_do, 0)                                # y^2 = x(x^2 + 2x + 263z)
        herm_a = find(note, r"a &= (\d+) \+ (\d+)z"); herm_b = find(note, r"b &= (\d+) \+ (\d+)z")
        ha = re.search(r"a &= (\d+) \+ (\d+)z", herm_a[0][1]); hb = re.search(r"b &= (\d+) \+ (\d+)z", herm_b[0][1])
        A_h = fe([int(ha.group(1)), int(ha.group(2)), 0, 0, 0]); B_h = fe([int(hb.group(1)), int(hb.group(2)), 0, 0, 0])
        eq_line = find(paper, r"with equation constants a = 2 and b = 263z")
        nl = find(paper, r"^n = 106799351671714695104148491657179270274505774058$")
        tail = next(l.strip() for l in paper[nl[0][0]:] if l.strip())                 # next non-empty line holds the tail
        n_paper = int(nl[0][1].split("=")[1].strip() + tail)
        n_herm = int(re.search(r"0x([0-9a-f]+)", find(note, r"^n = 0x7ffffffd")[0][1]).group(1), 16)
        S["model"] = {"published": "y^2 = x(x^2 + 2x + 263z) over F_p[z]/(z^5-3)", "paper_line": eq_line[0][0],
                      "A_from_paper_formula": coeffs(A), "B_from_paper_formula": coeffs(B),
                      "hermez_note_lines": [herm_a[0][0], herm_b[0][0]],
                      "hermez_constants_equal_derivation": A == A_h and B == B_h,
                      "raw_result_A_B_equal_derivation": raw["parameters"]["A"] == " + ".join(f"{c}*z^{i}" for i, c in enumerate(coeffs(A))) and raw["parameters"]["B"] == " + ".join(f"{c}*z^{i}" for i, c in enumerate(coeffs(B))),
                      "count_gp_A_B_equal_derivation": None,
                      "paper_n_decimal": str(n_paper), "hermez_n_hex_equals_paper_n": n_herm == n_paper}
        # the model used by the SEA count script is the same A, B
        cg = open(os.path.join(rd, "certificates/pari/count.gp")).read()
        mA = re.search(r"A = ([^;]+);", cg).group(1); mB = re.search(r"B = ([^;]+);", cg).group(1)
        parse = lambda s: fe([int(t.split("*z^")[0]) for t in s.split(" + ")])
        S["model"]["count_gp_A_B_equal_derivation"] = parse(mA) == A and parse(mB) == B
        # isomorphism check: X = x + 2/3 maps double-odd points onto the short model
        rng = random.Random(1)
        Esw = Curve(0, A, B)
        ok_iso = True
        for _ in range(5):
            Pd = Edo.random_point(rng); Qd = Edo.random_point(rng)
            m = lambda P_: None if P_ is None else (P_[0] + F(2) / 3, P_[1])
            ok_iso &= Esw.on(m(Pd)) and m(Edo.add(Pd, Qd)) == Esw.add(m(Pd), m(Qd))
        S["model"]["double_odd_to_short_weierstrass_isomorphism_checked"] = ok_iso
        n_pub = n_paper; N_pub = 2 * n_paper
        must(S["model"]["hermez_constants_equal_derivation"] and S["model"]["raw_result_A_B_equal_derivation"] and S["model"]["count_gp_A_B_equal_derivation"] and ok_iso and S["model"]["hermez_n_hex_equals_paper_n"], f"{curve} model")
    else:
        A, B = F(3), fe([0, 0, 0, 0, 8])
        Esw = Curve(0, A, B)
        eq_line = find(note, r"y\^2 = x\^3 \+ 3x \+ 8z\^4")
        n_note = int(re.search(r"0x([0-9a-f]+)", find(note, r"^n = 0xfffffffb")[0][1]).group(1), 16)
        cg = open(os.path.join(rd, "certificates/pari/count.gp")).read()
        mA = re.search(r"A = ([^;]+);", cg).group(1); mB = re.search(r"B = ([^;]+);", cg).group(1)
        parse = lambda s: fe([int(t.split("*z^")[0]) for t in s.split(" + ")])
        S["model"] = {"published": "y^2 = x^3 + 3x + 8z^4 over F_p[z]/(z^5-3)", "note_line": eq_line[0][0],
                      "count_gp_A_B_equal_published": parse(mA) == A and parse(mB) == B, "note_n_hex": hex(n_note)}
        n_pub = n_note; N_pub = n_note
        must(S["model"]["count_gp_A_B_equal_published"], f"{curve} model")
    # ---------- B2 SEA integer (regenerated) and ECPP proof of n
    n = N_sea // h
    S["sea_count"] = {"N": str(N_sea), "N_mod_h": N_sea % h, "n": str(n), "n_bits": n.bit_length()}
    pr_n = prove(n, os.path.join(rd, "certificates/ecpp/n.cert"))
    S["n_prime"] = pr_n
    must(N_sea % h == 0 and pr_n["ok"], f"{curve} ECPP n")
    # ---------- B3 point of order n (producer's recorded point, and a fresh one of mine)
    xq = oc["point_search"]["x"]; yq = oc["point_search"]["y"]
    Qpt = (F(xq), fe(yq))
    pts = {"recorded_point_on_curve": Esw.on(Qpt)}
    Ppt = Esw.add(Qpt, Qpt) if h == 2 else Qpt
    pts["P_not_O"] = Ppt is not None
    pts["nP_is_O_primary"] = Esw.mul(n, Ppt) is None
    Ep = V.ProjCurve(V.pf_from(A), V.pf_from(B))
    PP = (V.pf_from(Ppt[0]), V.pf_from(Ppt[1]), V.PF(1))
    pts["nP_is_O_secondary_projective"] = Ep.is_O(Ep.mul(n, PP))
    pts["neg_control_(n+2)P_is_O"] = Esw.mul(n + 2, Ppt) is None
    rng = random.Random(20260923)
    Rpt = Esw.random_point(rng); P2 = Esw.add(Rpt, Rpt) if h == 2 else Rpt
    pts["fresh_point_seed"] = 20260923
    pts["fresh_point"] = V.pt_json(P2)
    pts["fresh_point_nP_is_O"] = P2 is not None and Esw.mul(n, P2) is None
    S["order_point"] = pts
    must(pts["recorded_point_on_curve"] and pts["P_not_O"] and pts["nP_is_O_primary"] and pts["nP_is_O_secondary_projective"] and not pts["neg_control_(n+2)P_is_O"] and pts["fresh_point_nP_is_O"], f"{curve} [n]P = O")
    # ---------- B4 2-torsion (EcGFp5)
    if h == 2:
        x2 = F(2) / 3
        roots = V.cubic_roots(A, B)
        tt = {"X=2/3_is_root_of_cubic": x2**3 + A * x2 + B == 0,
              "cubic_roots_in_Fq_count": len(roots), "the_root_is_2/3": len(roots) == 1 and roots[0] == x2,
              "disc_4-4b_is_square_euler": is_sq(F(4) - 4 * b_do), "b=263z_is_square_euler": is_sq(b_do),
              "argument": "one rational 2-torsion point (2 | #E); 4 - 4b non-square => no other rational 2-torsion; b non-square => (0,0) is not in 2E(F_q) (a halving P of (0,0) has x(P)^2 = b), so the 2-Sylow subgroup has order exactly 2"}
        S["two_torsion"] = tt
        must(tt["X=2/3_is_root_of_cubic"] and tt["the_root_is_2/3"] and not tt["disc_4-4b_is_square_euler"] and not tt["b=263z_is_square_euler"], f"{curve} 2-torsion")
    # ---------- B5 Hasse uniqueness
    hn = h * n
    mults = [k * hn for k in range(lo // hn, hi // hn + 2) if lo <= k * hn <= hi]
    S["hasse"] = {"multiples_of_hn": [str(m) for m in mults], "unique": len(mults) == 1, "equals_sea_N": mults == [N_sea],
                  "certified_order": str(hn), "equals_published": hn == N_pub}
    must(len(mults) == 1 and mults[0] == N_sea, f"{curve} Hasse")
    # ---------- B6 twist
    Nt = 2 * q + 2 - N_sea
    tw, twfac = check_factorization(run, "twist-order", Nt)
    lpr = max(twfac)
    mpmath.mp.dps = 60
    sec = 0.5 * mpmath.log(mpmath.pi * lpr / 4, 2)
    tw.update({"N_twist": str(Nt), "equals_sea_twist_count": Nt == NT_sea, "N_plus_Nt_eq_2q_plus_2": N_sea + Nt == 2 * q + 2,
               "largest_prime": str(lpr), "largest_prime_bits": lpr.bit_length(),
               "twist_security_bits_60digits": mpmath.nstr(sec, 12), "twist_security_bits_4dp": f"{float(sec):.4f}",
               "committed_value": raw["steps"]["twist"]["twist_security_bits"]})
    tw["committed_value_matches_4dp"] = f"{float(sec):.4f}" == f"{tw['committed_value']:.4f}"
    if curve == "EcMasFp5":
        nt_h = int(re.search(r"0x([0-9a-f]+)", find(note, r"Twist prime order")[0][1]).group(1), 16)
        ct_h = int(re.search(r"0x([0-9a-f]+)", find(note, r"Twist cofactor")[0][1]).group(1), 16)
        tw["note_twist_prime_equals_largest"] = nt_h == lpr
        tw["note_factors_product_equals_Nt"] = nt_h * ct_h == Nt
        tw["self_report_101.93_abs_diff"] = f"{abs(float(sec) - 101.93):.4f}"
        tw["within_0.01"] = abs(float(sec) - 101.93) <= 0.01
        rho = 0.5 * mpmath.log(mpmath.pi * n / 4, 2)
        tw["curve_rho_bits"] = mpmath.nstr(rho, 10); tw["curve_rho_vs_159.83_within_0.01"] = abs(float(rho) - 159.83) <= 0.01
    # twist embedding degree from the committed factorization of l'-1
    tlm, tlmfac = check_factorization(run, "twist-prime-minus-1", lpr - 1)
    et = mult_order(q % lpr, lpr, tlmfac)
    tw["twist_embedding_degree"] = {"factorization_l_minus_1": tlm["complete_and_proved"], "e_twist_bits": et.bit_length(), "(l-1)/e": (lpr - 1) // et}
    S["twist"] = tw
    must(tw["complete_and_proved"] and tw["equals_sea_twist_count"] and tw["committed_value_matches_4dp"] and tlm["complete_and_proved"], f"{curve} twist")
    # ---------- B7 embedding degree (J2 a)
    em, nfac = check_factorization(run, "n-minus-1", n - 1)
    e = mult_order(q % n, n, nfac)
    em.update({"e": str(e), "e_bits": e.bit_length(), "(n-1)/e": (n - 1) // e, "e_divides_n-1": (n - 1) % e == 0,
               "q^e=1": pow(q, e, n) == 1,
               "q^(e/l)!=1_for_all_primes_l|e": all(pow(q, e // r, n) != 1 for r in nfac if e % r == 0),
               "committed_e_equal": raw["steps"]["embedding_degree"]["embedding_degree"] == str(e)})
    S["embedding_degree"] = em
    must(em["complete_and_proved"] and em["q^e=1"] and em["q^(e/l)!=1_for_all_primes_l|e"] and em["committed_e_equal"], f"{curve} embedding")
    # ---------- B8 CM discriminant (J2 b)
    t = q + 1 - N_sea
    D = t * t - 4 * q
    cmf, Dfac = check_factorization(run, "cm-discriminant", abs(D))
    sf = 1
    for r, ex in Dfac.items():
        if ex % 2: sf *= r
    d = -sf
    DK = d if d % 4 == 1 else 4 * d
    f2, rem = divmod(D, DK)
    cond = math.isqrt(f2)
    cm_raw = raw["steps"]["cm_discriminant"]
    cm = {"t": str(t), "t_bits": abs(t).bit_length(), "D": str(D), "D_negative": D < 0, "abs_D_bits": abs(D).bit_length(),
          "abs_D_hex_digits": len(f"{abs(D):x}"), "abs_D_leading_hex_nibble": f"{abs(D):x}"[0],
          "factorization": cmf, "squarefree_part_of_abs_D": str(sf), "d=-sf_mod_4": d % 4,
          "fundamental_discriminant_DK": str(DK), "DK_bits": abs(DK).bit_length(),
          "conductor_f_with_D=f^2*DK": cond if (rem == 0 and cond * cond == f2) else None,
          "committed": {"squarefree_part_of_abs_D": cm_raw.get("squarefree_part_of_abs_D"), "fundamental_discriminant": cm_raw.get("fundamental_discriminant"),
                        "conductor_squared": cm_raw.get("conductor_squared")}}
    cm["committed_squarefree_equal"] = cm_raw.get("squarefree_part_of_abs_D") == str(sf)
    cm["committed_fundamental_discriminant_equal"] = cm_raw.get("fundamental_discriminant") == str(DK)
    cm["committed_conductor_squared_equal_recomputed_f^2"] = cm_raw.get("conductor_squared") == str(f2)
    cm["committed_raw_internally_consistent_D_eq_cond2_times_fundamental"] = int(cm_raw["D"]) == int(cm_raw["conductor_squared"]) * int(cm_raw["fundamental_discriminant"])
    if curve == "EcMasFp5":
        hits = find(note, r"350910d76c19ff80472df1f236bda8f251edc59a20563b4f1bcb88ad47f9892d334755425f4369e43")
        bitsays = find(note, r"323")
        Dn = -int("350910d76c19ff80472df1f236bda8f251edc59a20563b4f1bcb88ad47f9892d334755425f4369e43", 16)
        cm["note_D_lines"] = [ln for ln, _ in hits]
        cm["note_323_lines"] = [[ln, tx.strip()] for ln, tx in bitsays]
        cm["note_D_integer_equals_recomputed_D"] = Dn == D
        cm["note_D_hex_digits"] = 81
        cm["binary_length_of_note_integer"] = abs(Dn).bit_length()
        cm["observation_only_len(bin(D))-2_for_negative_D"] = len(bin(Dn)) - 2
    S["cm"] = cm
    must(cmf["complete_and_proved"], f"{curve} |D| factorization")
    # ---------- B9 negative controls of my verifier
    nc = {}
    cert = load_cert(os.path.join(rd, "certificates/ecpp/n.cert"))
    bad = json.loads(json.dumps(cert)); s0 = str(bad[0][4][0]); bad[0][4][0] = int(s0[:-1] + str((int(s0[-1]) + 1) % 10))
    nc["n.cert_one_digit_flipped_in_row0_point_x_rejected"] = not V.ecpp_check(bad, n)[0]
    bad = json.loads(json.dumps(cert)); s0 = str(bad[1][2]); bad[1][2] = int(s0[:-1] + str((int(s0[-1]) + 1) % 10))
    nc["n.cert_one_digit_flipped_in_row1_s_rejected"] = not V.ecpp_check(bad, n)[0]
    nc["n.cert_against_n+2_rejected"] = not V.ecpp_check(cert, n + 2)[0]
    # swap one twist factor: (i) l' -> l'+2 ; (ii) l' -> n (a genuine prime of similar size)
    def prod_of(fd):
        pr_ = 1
        for r, ex in fd.items(): pr_ *= r**ex
        return pr_
    sw = dict(twfac); del sw[lpr]; sw[lpr + 2] = 1
    nc["twist_factor_l'_swapped_for_l'+2_product_check_rejects"] = prod_of(sw) != Nt
    nc["twist_factor_l'+2_is_composite_(MR_witness)"] = not V.is_probable_prime(lpr + 2)
    sw = dict(twfac); del sw[lpr]; sw[n] = 1
    nc["twist_factor_l'_swapped_for_n_product_check_rejects"] = prod_of(sw) != Nt
    ecpp_tw = [f_ for f_ in sorted(os.listdir(os.path.join(rd, "certificates/ecpp"))) if f_.startswith("twist_f")]
    lp_cert = [f_ for f_ in ecpp_tw if load_cert(os.path.join(rd, "certificates/ecpp", f_))[0][0] == lpr]
    nc["twist_l'_certificate_against_l'+2_rejected"] = bool(lp_cert) and not V.ecpp_check(load_cert(os.path.join(rd, "certificates/ecpp", lp_cert[0])), lpr + 2)[0]
    S["verifier_negative_controls"] = nc
    must(all(v for v in nc.values()), f"{curve} verifier negative controls")
    CURVES[curve] = {"A": coeffs(A), "B": coeffs(B), "n": n, "N": N_sea, "P": V.pt_json(Ppt), "h": h, "D": D, "Nt": Nt}
    R[f"B_{curve}"] = S

# ---------- B10 ECM inputs: which certified integer each hint log was run on
ecm_dir = os.path.join(EXP, "runs/RUN-GFPN-b71f2f/certificates/ecm")
targets = {}
for c, v in CURVES.items():
    n = v["n"]
    targets[f"{c}:n-1"] = n - 1; targets[f"{c}:|D|"] = abs(v["D"]); targets[f"{c}:twist"] = v["Nt"]
    raw = json.load(open(os.path.join(EXP, "runs", "RUN-GFPN-b71f2f" if c == "EcGFp5" else "RUN-GFPN-3bbef2", "raw-result.json")))
    targets[f"{c}:l'-1"] = int(raw["steps"]["twist"]["largest_prime_factor"]) - 1
ecm = {}
for fn in sorted(os.listdir(ecm_dir)):
    txt = open(os.path.join(ecm_dir, fn)).read()
    m = re.search(r"Input number is (\d+)", txt)
    X = int(m.group(1))
    hit = [k for k, v in targets.items() if v % X == 0]
    ecm[fn] = {"input_digits": len(str(X)), "divides": hit, "has_timestamp_or_commandline": bool(re.search(r"\d{4}-\d{2}-\d{2}|ecm -", txt))}
R["B_ecm_inputs"] = ecm

# =============================================================================
# C. J3(b): SCURVE prior package: hashes, and my own regeneration of l*B = O and Hasse
# =============================================================================
PKG = os.path.join(REPO, "coordination/goals/GOAL-SCURVE-15e805/batches/BATCH-0aef14/tasks/TASK-20260908-42e809")
ctrl = json.load(open(os.path.join(EXP, "runs/RUN-GFPN-17ed52/certificates/control-regeneration.json")))
C = {"hashes": {fn: {"observed_now": sha(os.path.join(PKG, fn)), "recorded_in_control_run": ctrl["hashes"][fn]["expected"],
                     "match": sha(os.path.join(PKG, fn)) == ctrl["hashes"][fn]["expected"]} for fn in ("base-point-audit.yaml", "raw-transcription.yaml")}}
C["git_commits_touching_package"] = subprocess.run(["git", "-C", REPO, "log", "--format=%h %ad %s", "--date=iso", "--", rel(os.path.join(PKG, "base-point-audit.yaml")), rel(os.path.join(PKG, "raw-transcription.yaml"))], capture_output=True, text=True).stdout.strip().splitlines()
tr = yaml.safe_load(open(os.path.join(PKG, "raw-transcription.yaml")))["raw_transcription"]["transcribed_values"]
au = {c_["id"]: c_ for c_ in yaml.safe_load(open(os.path.join(PKG, "base-point-audit.yaml")))["base_point_audit"]["candidates"]}
pp = 2**448 - 2**224 - 1
m1 = tr["M1_curve448_montgomery"]; m3 = tr["M3_edwards448_goldilocks"]
Am = int(m1["A"]["value"]); hh = int(m1["cofactor"]["value"]); l = 2**446 - int(m1["order_hex_subtrahend"]["value"], 16)
u, v = int(m1["U_P"]["value"]), int(m1["V_P"]["value"])
# M1: Montgomery v^2 = u^3 + A u^2 + u is general Weierstrass (a2 = A, a4 = 1, a6 = 0); my own affine law over F_pp
def wadd(P1, P2, a2, a4):
    if P1 is None: return P2
    if P2 is None: return P1
    (x1, y1), (x2, y2) = P1, P2
    if x1 == x2:
        if (y1 + y2) % pp == 0: return None
        lam = (3 * x1 * x1 + 2 * a2 * x1 + a4) * pow(2 * y1, -1, pp) % pp
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, pp) % pp
    x3 = (lam * lam - a2 - x1 - x2) % pp
    return (x3, (lam * (x1 - x3) - y1) % pp)
def wmul(k, P_, a2, a4):
    Rr = None
    for bit in bin(k)[2:]:
        Rr = wadd(Rr, Rr, a2, a4)
        if bit == "1": Rr = wadd(Rr, P_, a2, a4)
    return Rr
C["M1_on_curve"] = (v * v - (u**3 + Am * u * u + u)) % pp == 0
C["M1_lB_is_O_my_weierstrass_law"] = wmul(l, (u, v), Am, 1) is None
C["M1_neg_control_(l-1)B_is_O"] = wmul(l - 1, (u, v), Am, 1) is None
# M3: edwards448 x^2 + y^2 = 1 + d x^2 y^2 (a = 1, d = -39081): my own unified addition
d3 = int(m3["d"]["value"]) % pp; x3, y3 = int(m3["X_P_RFC7748"]["value"]), int(m3["Y_P_RFC7748"]["value"])
def eadd(P1, P2):
    (a1, b1), (a2_, b2) = P1, P2
    k = d3 * a1 * a2_ * b1 * b2 % pp
    return ((a1 * b2 + b1 * a2_) * pow(1 + k, -1, pp) % pp, (b1 * b2 - a1 * a2_) * pow(1 - k, -1, pp) % pp)
def emul(k, P_):
    Rr = (0, 1)
    for bit in bin(k)[2:]:
        Rr = eadd(Rr, Rr)
        if bit == "1": Rr = eadd(Rr, P_)
    return Rr
C["M3_on_curve"] = (x3 * x3 + y3 * y3 - 1 - d3 * x3 * x3 * y3 * y3) % pp == 0
C["M3_lB_is_identity_my_edwards_law"] = emul(l, (x3, y3)) == (0, 1)
C["M3_neg_control_(l+1)B_is_identity"] = emul(l + 1, (x3, y3)) == (0, 1)
s2 = math.isqrt(4 * pp); assert s2 * s2 != 4 * pp
hlo, hhi = pp + 1 - s2, pp + 1 + s2
C["hasse_lo"] = str(hlo); C["hasse_hi"] = str(hhi)
prior_int = au["M1_curve448_montgomery"]["hasse_interval_uniqueness"]["interval"].strip("[]").split(",")
C["hasse_endpoints_equal_prior"] = [str(hlo) == prior_int[0].strip(), str(hhi) == prior_int[1].strip()]
C["multiples_of_l_in_interval"] = sum(1 for k in range(hlo // l, hhi // l + 2) if hlo <= k * l <= hhi)
C["multiples_of_h*l_in_interval"] = sum(1 for k in range(hlo // (hh * l), hhi // (hh * l) + 2) if hlo <= k * hh * l <= hhi)
C["h*l_equals_prior"] = str(hh * l) == str(au["M1_curve448_montgomery"]["hasse_interval_uniqueness"]["h_times_l"])
R["C_J3b_scurve"] = C
must(all(x["match"] for x in C["hashes"].values()) and C["M1_lB_is_O_my_weierstrass_law"] and C["M3_lB_is_identity_my_edwards_law"] and not C["M1_neg_control_(l-1)B_is_O"] and not C["M3_neg_control_(l+1)B_is_identity"] and all(C["hasse_endpoints_equal_prior"]), "J3b regeneration")

# =============================================================================
# D. J3(a): static call graph of the control vs the GFPN scoring path
# =============================================================================
IMPL = os.path.join(EXP, "implementation")
def summarize(fn):
    tree = ast.parse(open(os.path.join(IMPL, fn)).read())
    imports, local_from, defs, calls, subprocs = set(), {}, set(), set(), []
    for nd in ast.walk(tree):
        if isinstance(nd, ast.Import):
            for a in nd.names: imports.add(a.name)
        elif isinstance(nd, ast.ImportFrom):
            imports.add(nd.module)
            for a in nd.names: local_from.setdefault(nd.module, []).append(a.name)
        elif isinstance(nd, (ast.FunctionDef, ast.ClassDef)):
            defs.add(nd.name)
        elif isinstance(nd, ast.Call):
            fnode = nd.func
            name = fnode.attr if isinstance(fnode, ast.Attribute) else (fnode.id if isinstance(fnode, ast.Name) else None)
            if name: calls.add(name)
            if isinstance(fnode, ast.Attribute) and isinstance(fnode.value, ast.Name) and fnode.value.id == "subprocess":
                subprocs.append(ast.unparse(nd)[:120])
    return {"imports": sorted(imports), "from_imports": {k: sorted(v) for k, v in local_from.items()}, "defs": sorted(defs), "calls": sorted(calls), "subprocess_calls": subprocs}
cg = {fn: summarize(fn) for fn in ("scurve_control.py", "gfpn_audit.py", "gfpn_arith.py", "check_run.py", "run_wrapper.py")}
project_modules = {"gfpn_arith", "gfpn_audit", "scurve_control", "check_run", "run_wrapper"}
ctrl_code = set(cg["scurve_control.py"]["defs"])
gfpn_code = set(cg["gfpn_audit.py"]["defs"]) | set(cg["gfpn_arith.py"]["defs"])
D_ = {"per_file": cg,
      "control_imports_project_modules": sorted(set(cg["scurve_control.py"]["imports"]) & project_modules),
      "gfpn_audit_imports_project_modules": sorted(set(cg["gfpn_audit.py"]["imports"]) & project_modules),
      "project_functions_defined_by_control": sorted(ctrl_code),
      "project_functions_on_gfpn_scoring_path": sorted(gfpn_code),
      "shared_project_functions": sorted(ctrl_code & gfpn_code),
      "shared_names_defined_in_both_files_but_distinct_code": sorted(set(cg["scurve_control.py"]["defs"]) & (set(cg["gfpn_audit.py"]["defs"]) | set(cg["gfpn_arith.py"]["defs"]))),
      "shared_third_party_or_stdlib_modules": sorted((set(cg["scurve_control.py"]["imports"]) & (set(cg["gfpn_audit.py"]["imports"]) | set(cg["gfpn_arith.py"]["imports"]))) - project_modules),
      "control_invokes_PARI_gp": any("gp" in s for s in cg["scurve_control.py"]["subprocess_calls"]),
      "gfpn_audit_invokes_PARI_gp": any("gp" in s for s in cg["gfpn_audit.py"]["subprocess_calls"])}
src = open(os.path.join(IMPL, "gfpn_audit.py")).read().splitlines()
D_["gfpn_audit_lines_referring_to_control"] = [[i + 1, l.strip()[:220]] for i, l in enumerate(src) if re.search(r"17ed52|scurve|control-regeneration", l)]
D_["gfpn_audit_reads_control_artifacts"] = any(re.search(r"open\([^)]*(17ed52|control-regeneration)", l) for l in src)
R["D_J3a_callgraph"] = D_

# =============================================================================
# E. J3(c): chronology from manifests / environment
# =============================================================================
E_ = {}
for run in ("RUN-GFPN-17ed52", "RUN-GFPN-b71f2f", "RUN-GFPN-3bbef2"):
    man = yaml.safe_load(open(os.path.join(EXP, "runs", run, "manifest.yaml")))["run"]
    env = json.load(open(os.path.join(EXP, "runs", run, "environment.json")))
    E_[run] = {"started_at": man["timing"]["started_at"], "finished_at": man["timing"]["finished_at"], "status": man["status"], "dirty_paths": env["git"]["dirty_paths"], "commit": man["code"]["commit"]}
import datetime as _dt
iso = lambda s: _dt.datetime.fromisoformat(s)
E_["control_finished_before_both_gfpn_started"] = iso(E_["RUN-GFPN-17ed52"]["finished_at"]) < min(iso(E_["RUN-GFPN-b71f2f"]["started_at"]), iso(E_["RUN-GFPN-3bbef2"]["started_at"]))
E_["gap_seconds"] = (min(iso(E_["RUN-GFPN-b71f2f"]["started_at"]), iso(E_["RUN-GFPN-3bbef2"]["started_at"])) - iso(E_["RUN-GFPN-17ed52"]["finished_at"])).total_seconds()
E_["gfpn_runs_overlap_each_other"] = iso(E_["RUN-GFPN-3bbef2"]["started_at"]) < iso(E_["RUN-GFPN-b71f2f"]["finished_at"])
R["E_J3c_chronology"] = E_

# =============================================================================
# F. J1(d): where a published integer enters gfpn_audit.py, in execution order
# =============================================================================
F_ = {"lines_using_published_integers": [[i + 1, l.strip()[:200]] for i, l in enumerate(src) if re.search(r"\bn_note\b|\bN_note\b|n_hex_secondary|D_note|nt_note", l)]}
for curve, run in (("EcGFp5", "RUN-GFPN-b71f2f"), ("EcMasFp5", "RUN-GFPN-3bbef2")):
    raw = json.load(open(os.path.join(EXP, "runs", run, "raw-result.json")))
    ocj = raw["steps"]["order_certificate"]
    F_[curve] = {"candidate_origin": ocj["candidate_origin"], "gp_call_order": [g["script"] for g in raw["gp_calls"]],
                 "sea_status": raw["steps"]["point_count"]["status"], "candidate_equals_sea_over_h": int(ocj["candidate_n"]) * ocj["cofactor_h"] == int(raw["steps"]["point_count"]["N"])}
R["F_J1d_regenerated_not_copied"] = F_

R["FAILED_CHECKS"] = FAILS
R["wall_seconds"] = round(time.time() - T0, 2)
json.dump(CURVES and {k: {kk: (str(vv) if isinstance(vv, int) else vv) for kk, vv in v.items()} for k, v in CURVES.items()}, open(os.path.join(OUT, "curves.json"), "w"), indent=1)
json.dump(R, open(os.path.join(OUT, "result.json"), "w"), indent=1, default=str)
print(json.dumps({"failed_checks": FAILS, "wall_seconds": R["wall_seconds"]}, indent=1))
