#!/usr/bin/env python3
"""J4 rejection-witness sweep (TASK-20260923-2d8db0, invocations 2 and 3).

Re-enumerates the PUBLISHED parameter search in the published order (enumeration
written here from the frozen texts, not read from the producer's code), and for every
predecessor of the published curve produces a SELF-CERTIFYING rejection witness,
verified twice in code written in this session (vlib PRIMARY: FLINT field + affine
law on the published model; vlib SECONDARY: pure-Python field + projective law on the
short-Weierstrass model). Nothing is re-trusted from PARI's SEA:

  W4   (EcGFp5 pre-filter) a subgroup of order 4 in E(F_q): either a second rational
       2-torsion point (r, 0) (root of x^2 + 2x + b), or a point P with 2P = (0,0).
       => 4 | #E, so #E != 2 * (odd prime).
  Wl   a point Q != O with [l]Q = O, l a small prime (odd for EcGFp5) => l | #E,
       so #E is not prime (EcMasFp5) / not 2 * prime (EcGFp5).
  WN   an integer N in the Hasse interval, a point P with [h]P != O and [N]P = O, and a
       proof that N is not h * prime (a nontrivial factor of N/h, or a Fermat witness).
       If #E = h*r with r prime then every P with [h]P != O has r | ord(P) | N, and
       |N - h r| <= 4 sqrt(q) < r forces N = h r, contradiction. N may come from any
       source (here: the producer's own trace, or PARI ellcard as discovery only); the
       argument does not need N = #E.

PARI is used ONLY for discovery (ellcard, when no small-l witness is found by FLINT
division polynomials); it never verifies anything. The producer's trace
(certificates/pari/rigidity.out) is read as a hint and for cross-checking its
classification; it is never trusted.

Resumable: one JSON line per candidate in <out>/witnesses.jsonl; a chunk stops after
--chunk-seconds and the next invocation continues.
"""
import argparse, json, math, os, random, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib as V
from vlib import F, fe, Curve, is_sq, coeffs, P_GOLD as p, Q_GOLD as q

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 6))
S = math.isqrt(4 * q); HLO, HHI = q + 1 - S, q + 1 + S
ODD_L = [l for l in V.SMALL_PRIMES if 3 <= l <= 19]

# ----------------------------------------------------------------------------- enumeration (published order)
def enum_ecgfp5():
    """Pornin 2022/274 sec. 4: c <- 1; for i = 1..4: (a) +c z^i, (b) -c z^i; c <- c+1."""
    idx, c = 0, 1
    while True:
        for i in range(1, 5):
            for sgn in (1, -1):
                idx += 1
                yield idx, {"c": c, "i": i, "sign": "+" if sgn > 0 else "-"}, fe([0] * i + [sgn * c] + [0] * (4 - i))
        c += 1

def enum_ecmasfp5():
    """find_ec_over_gfp5(initial_a=0, initial_c=1, attempts=50): A from 0; c = 1..49; i = 1..4 (range(1, 5))."""
    idx, A = 0, 0
    while True:
        for c in range(1, 50):
            for i in range(1, 5):
                idx += 1
                yield idx, {"A": A, "c": c, "i": i}, (F(A), fe([0] * i + [c] + [0] * (4 - i)))
        A += 1

def load_trace(curve):
    run = "RUN-GFPN-b71f2f" if curve == "EcGFp5" else "RUN-GFPN-3bbef2"
    tr = {}
    for line in open(os.path.join(REPO, "experiments/EXP-GFPN-726eb2/runs", run, "certificates/pari/rigidity.out")):
        if not line.startswith("CAND"): continue
        kv = dict(re.findall(r"(\w+)=(\d+)", line))
        tr[int(kv["idx"])] = {k: int(v) for k, v in kv.items()}
    return tr

# ----------------------------------------------------------------------------- secondary verification helpers
def to_short(curve_kind, a2, a4, a6, P_):
    """Map a point of y^2 = x^3 + a2 x^2 + a4 x (+a6) to the short model (X = x + a2/3)."""
    if P_ is None: return None
    return (P_[0] + a2 / 3, P_[1])

def sec_curve(A, B):
    return V.ProjCurve(V.pf_from(A), V.pf_from(B))

def sec_point(Pa):
    return (V.pf_from(Pa[0]), V.pf_from(Pa[1]), V.PF(1))

def sec_order_divides(Ep, Pa, k):
    """SECONDARY: Pa (short model, affine) on curve, and [k]Pa = O."""
    Pp = sec_point(Pa)
    return Ep.on(Pp), Ep.is_O(Ep.mul(k, Pp))

# ----------------------------------------------------------------------------- compositeness of N/h
def not_h_prime_proof(N, h):
    """Proof that N != h * prime: returns dict. Order: N mod h; factor via gcd with small primes,
    Pollard-Brent, GMP-ECM (discovery; factor re-checked by division); else Fermat witness."""
    if N % h: return {"kind": "N not divisible by h", "ok": True}
    M = N // h
    for sp in V.SMALL_PRIMES:
        if M % sp == 0 and M != sp: return {"kind": "factor", "factor": str(sp), "method": "trial division", "ok": M % sp == 0 and 1 < sp < M}
    g = V.pollard_brent(M, max_iter=200000, seed=3)
    if g and 1 < g < M: return {"kind": "factor", "factor": str(g), "method": "Pollard-Brent rho", "ok": M % g == 0}
    for B1, curves in ((11000, 30), (50000, 40)):
        try:
            r = subprocess.run(["ecm", "-q", "-c", str(curves), str(B1)], input=str(M) + "\n", capture_output=True, text=True, timeout=120)
            for tok in re.findall(r"\d+", r.stdout):
                f_ = int(tok)
                if 1 < f_ < M and M % f_ == 0:
                    return {"kind": "factor", "factor": str(f_), "method": f"GMP-ECM B1={B1} (discovery; checked by division)", "ok": True}
        except subprocess.TimeoutExpired:
            pass
    for a in (2, 3, 5, 7):
        if pow(a, M - 1, M) != 1:
            return {"kind": "fermat_witness", "base": a, "method": "a^(M-1) mod M != 1 proves M composite (no factor found within budget)", "ok": True}
    return {"kind": "NONE", "ok": False, "note": "M passes Fermat for bases 2,3,5,7: POSSIBLE PRIME -- flagged"}

# ----------------------------------------------------------------------------- witnesses
def w4_witness(b):
    """EcGFp5 pre-filter: y^2 = x(x^2 + 2x + b). Returns witness dict with both verifications."""
    E = Curve(2, b, 0)
    A_s, B_s = b - F(4) / 3, F(16) / 27 - 2 * b / 3
    Ep = sec_curve(A_s, B_s)
    two3 = F(2) / 3
    T0 = (F(0), F(0))
    if is_sq(4 - 4 * b):
        r = (-2 + (4 - 4 * b).sqrt()) / 2
        T = (r, F(0))
        prim = r * r + 2 * r + b == 0 and r != 0 and E.on(T) and E.add(T, T) is None and E.add(T, T0) is not None and E.add(E.add(T, T0), E.add(T, T0)) is None
        on2, o2 = sec_order_divides(Ep, to_short(0, F(2), b, 0, T), 2)
        sec = on2 and o2 and V.pf_from(r + two3) != V.pf_from(two3)
        return {"type": "W4_full_2torsion", "point": V.pt_json(T), "primary_ok": prim, "secondary_ok": sec}
    if is_sq(b):
        s = b.sqrt()
        for x0 in (s, -s):
            v = 2 + 2 * x0
            if is_sq(v):
                m = v.sqrt(); P_ = (x0, m * x0)
                prim = E.on(P_) and E.add(P_, P_) == T0 and E.mul(4, P_) is None
                Ps = to_short(0, F(2), b, 0, P_)
                on4, o4 = sec_order_divides(Ep, Ps, 4)
                _, o2 = sec_order_divides(Ep, Ps, 2)
                sec = on4 and o4 and not o2
                return {"type": "W4_order4_point", "point": V.pt_json(P_), "primary_ok": prim, "secondary_ok": sec}
    return {"type": "NONE", "primary_ok": False, "secondary_ok": False}

def wl_search(model, A_s, B_s, ls, memo):
    """FLINT division-polynomial search for a rational point of prime order l on the short model."""
    for l in ls:
        if l == 2:
            rts = V.cubic_roots(A_s, B_s)
            if rts: return 2, (rts[0], F(0))
            continue
        xs = V.rational_l_torsion_x(A_s, B_s, l, memo)
        if xs:
            X0 = xs[0]; Y0 = (X0**3 + A_s * X0 + B_s).sqrt()
            return l, (X0, Y0)
    return None, None

def verify_wl(Emodel, a2, Ep, l, Qs):
    """Qs on the short model; check on the published model (primary) and short model (secondary)."""
    Qm = (Qs[0] - a2 / 3, Qs[1])
    prim = Qm is not None and Emodel.on(Qm) and Emodel.mul(l, Qm) is None
    on_, ol = sec_order_divides(Ep, Qs, l)
    return Qm, prim, on_ and ol and not Ep.is_O(sec_point(Qs))

def wn_witness(Emodel, a2, Ep, N, h, rng):
    """(N, P, proof N != h*prime) with [h]P != O and [N]P = O, both implementations."""
    in_hasse = HLO <= N <= HHI
    for _ in range(4):
        P_ = Emodel.random_point(rng)
        if Emodel.mul(h, P_) is not None: break
    hP_ok = Emodel.mul(h, P_) is not None
    prim = Emodel.mul(N, P_) is None
    Ps = (P_[0] + a2 / 3, P_[1])
    on_, oN = sec_order_divides(Ep, Ps, N)
    _, oh = sec_order_divides(Ep, Ps, h)
    comp = not_h_prime_proof(N, h)
    return {"type": "WN_full_count", "N": str(N), "N_in_hasse": in_hasse, "point": V.pt_json(P_), "hP_not_O": hP_ok,
            "not_h_prime": comp, "primary_ok": in_hasse and hP_ok and prim and comp["ok"],
            "secondary_ok": in_hasse and on_ and oN and not oh and comp["ok"]}

def pari_ellcard(A_s, B_s):
    """DISCOVERY ONLY: PARI ellcard of the short model (never used to verify)."""
    cs = lambda a: " + ".join(f"{c}*z^{i}" for i, c in enumerate(coeffs(a)))
    script = (f"default(parisizemax, 2000000000);\np = {p}; z = ffgen(Mod(1,p)*(x^5-3), 'z);\n"
              f"E = ellinit([{cs(A_s)}, {cs(B_s)}]);\nprint(\"N=\", ellcard(E));\n")
    t0 = time.time()
    r = subprocess.run(["gp", "-q", "-f"], input=script, capture_output=True, text=True, timeout=1200)
    m = re.search(r"N=(\d+)", r.stdout)
    return (int(m.group(1)) if m else None), round(time.time() - t0, 2), r.stderr[-300:]

def wl_from_N(Emodel, a2, A_s, B_s, Ep, N, h, rng):
    """Discovery via a count N: smallest prime l | N with l not dividing h, Q = [N/l]R."""
    Es = Curve(0, A_s, B_s)
    for l in V.SMALL_PRIMES:
        if N % l or (l == 2 and h == 2): continue       # EcGFp5: odd l only
        for _ in range(40):
            R_ = Es.random_point(rng)
            Qs = Es.mul(N // l, R_)
            if Qs is not None:
                Qm, prim, sec = verify_wl(Emodel, a2, Ep, l, Qs)
                return {"type": "Wl_small_order_point", "l": l, "point_published_model": V.pt_json(Qm), "discovery": "PARI ellcard count (discovery only)", "primary_ok": prim, "secondary_ok": sec}
    return None

# ----------------------------------------------------------------------------- CM re-count for j = 0 (EcMasFp5, A = 0)
def cm_j0_orders():
    """The six possible #E(F_q) of y^2 = x^3 + B over F_q, q = p^5, p = 1 mod 3: q + 1 - Tr(u pi^5),
    u in Z[w]^*, pi of norm p (p = r^2 + 3 s^2 by Cornacchia). Independent of SEA."""
    def sqrt_mod(a, pr):
        # Tonelli-Shanks
        Qv, Sv = pr - 1, 0
        while Qv % 2 == 0: Qv //= 2; Sv += 1
        zn = 2
        while pow(zn, (pr - 1) // 2, pr) != pr - 1: zn += 1
        M, c, t, Rv = Sv, pow(zn, Qv, pr), pow(a, Qv, pr), pow(a, (Qv + 1) // 2, pr)
        while t != 1:
            i, tt = 0, t
            while tt != 1: tt = tt * tt % pr; i += 1
            b_ = pow(c, 1 << (M - i - 1), pr); M, c, t, Rv = i, b_ * b_ % pr, t * b_ * b_ % pr, Rv * b_ % pr
        return Rv
    x0 = sqrt_mod((-3) % p, p)
    if x0 < p // 2: x0 = p - x0
    a_, b_ = p, x0
    lim = math.isqrt(p)
    while b_ > lim: a_, b_ = b_, a_ % b_
    r = b_; s2, rem = divmod(p - r * r, 3)
    s = math.isqrt(s2)
    assert rem == 0 and s * s == s2 and r * r + 3 * s * s == p
    Rr, Ss = 1, 0
    for _ in range(5): Rr, Ss = Rr * r - 3 * Ss * s, Rr * s + Ss * r
    assert Rr * Rr + 3 * Ss * Ss == q
    traces = [2 * Rr, -2 * Rr, Rr + 3 * Ss, -(Rr + 3 * Ss), Rr - 3 * Ss, -(Rr - 3 * Ss)]
    return {"p=r^2+3s^2": [r, s], "orders": sorted(q + 1 - T for T in traces)}

# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--curve", required=True, choices=["EcGFp5", "EcMasFp5"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--chunk-seconds", type=float, default=1500)
    args = ap.parse_args()
    t_start = time.time()
    os.makedirs(args.out, exist_ok=True)
    wpath = os.path.join(args.out, "witnesses.jsonl")
    done = set()
    if os.path.exists(wpath):
        for line in open(wpath):
            done.add(json.loads(line)["idx"])
    trace = load_trace(args.curve)
    pub = {"EcGFp5": {"c": 263, "i": 1, "sign": "+"}, "EcMasFp5": {"A": 3, "c": 8, "i": 4}}[args.curve]
    h = 2 if args.curve == "EcGFp5" else 1
    cm = cm_j0_orders() if args.curve == "EcMasFp5" else None
    if cm: json.dump(cm, open(os.path.join(args.out, "cm_j0_orders.json"), "w"), indent=1)
    gen = enum_ecgfp5() if args.curve == "EcGFp5" else enum_ecmasfp5()
    n_new = 0
    with open(wpath, "a") as wf:
        for idx, params, coef in gen:
            if idx in done:
                if params == pub: break
                continue
            if time.time() - t_start > args.chunk_seconds:
                print(f"CHUNK_STOP at idx {idx} after {time.time() - t_start:.0f}s"); break
            t0 = time.time()
            rng = random.Random(f"{args.curve}-{idx}")
            rec = {"idx": idx, "params": params, "is_published": params == pub, "trace": trace.get(idx)}
            # cross-check enumeration against the producer's trace parameters
            tr = trace.get(idx)
            if tr is not None:
                rec["trace_params_agree"] = all(tr.get(k) == (v if k != "sign" else None) for k, v in params.items() if k != "sign") and (args.curve != "EcGFp5" or tr["s"] == (0 if params["sign"] == "+" else 1))
            if args.curve == "EcGFp5":
                b = coef
                a2 = F(2); Emodel = Curve(2, b, 0)
                A_s, B_s = b - F(4) / 3, F(16) / 27 - 2 * b / 3
                qb, qd = is_sq(b), is_sq(4 - 4 * b)
                rec["euler"] = {"b_is_QR": qb, "a2-4b_is_QR": qd, "flint_is_square_agrees": (qb == b.is_square()) and (qd == (4 - 4 * b).is_square())}
                rec["published_prefilter_rejects"] = qb or qd
                if tr is not None: rec["trace_filtered"] = tr.get("filtered") == 1
            else:
                A_, B_ = coef
                a2 = F(0); Emodel = Curve(0, A_, B_); A_s, B_s = A_, B_
            Ep = sec_curve(A_s, B_s)
            if rec["is_published"]:
                rec["witness"] = {"type": "ACCEPTED_published_curve", "note": "acceptance is the J1 certificate (#E = h*n, n ECPP-proved), re-verified in invocation 1"}
                wf.write(json.dumps(rec) + "\n"); wf.flush(); n_new += 1
                print(f"idx {idx} PUBLISHED {params}"); break
            w = None
            if args.curve == "EcGFp5" and rec["published_prefilter_rejects"]:
                w = w4_witness(b)
            else:
                memo = {}
                ls = ODD_L if h == 2 else [2] + ODD_L
                trace_full = tr is not None and tr.get("sea", 0) != 0
                if trace_full:
                    w = wn_witness(Emodel, a2, Ep, tr["sea"], h, rng)
                    if args.curve == "EcMasFp5" and params["A"] == 0:
                        hits = []
                        for Nk in cm["orders"]:
                            P_ = Emodel.random_point(random.Random(f"cm-{idx}"))
                            if Emodel.mul(Nk, P_) is None: hits.append(Nk)
                        w["cm_j0_recount"] = {"orders_killing_random_point": [str(x) for x in hits], "unique": len(hits) == 1,
                                              "equals_trace_N": hits == [tr["sea"]]}
                    if not (w["primary_ok"] and w["secondary_ok"]): w = None
                if w is None:
                    l, Qs = wl_search(args.curve, A_s, B_s, ls, memo)
                    if l is not None:
                        Qm, prim, sec = verify_wl(Emodel, a2, Ep, l, Qs)
                        w = {"type": "Wl_small_order_point", "l": l, "point_published_model": V.pt_json(Qm), "discovery": "FLINT division polynomial / cubic roots", "primary_ok": prim, "secondary_ok": sec}
                if w is None:
                    N, dt, err = pari_ellcard(A_s, B_s)
                    rec["pari_discovery"] = {"N": str(N) if N else None, "seconds": dt, "stderr_tail": err if N is None else None}
                    if N is None:
                        w = {"type": "INFRA_pari_failed", "primary_ok": False, "secondary_ok": False}
                    else:
                        w = wl_from_N(Emodel, a2, A_s, B_s, Ep, N, h, rng) or wn_witness(Emodel, a2, Ep, N, h, rng)
            rec["witness"] = w
            rec["rejection_certified"] = bool(w and w.get("primary_ok") and w.get("secondary_ok"))
            rec["seconds"] = round(time.time() - t0, 3)
            wf.write(json.dumps(rec) + "\n"); wf.flush(); n_new += 1
            if idx % 50 == 0: print(f"idx {idx} {w['type'] if w else None} {rec['rejection_certified']} {rec['seconds']}s elapsed {time.time() - t_start:.0f}s", flush=True)
    print(f"CHUNK_DONE new_records={n_new} elapsed={time.time() - t_start:.1f}s")

if __name__ == "__main__":
    main()
