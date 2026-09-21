# EXP-SIG-001 instrument (H-SIG-001 / H013; absorbs AUTOLAB_TASKS T3+T5).
#
# Signature-tracked syzygy classification of the boolean chained Semaev ideal
# (the T2 family: deficit 1 at D3, 8n/3 at D4) + the recovered Yokoyama object
# (D5_YOKOYAMA_OBJECT.md): #G* on the non-reduced GB vs m*d^{m-1}, #NS(Syz),
# Betti tables vs the T11-certified null, across the CM panel.
#
# Method (boolean arm), exact kernel algebra at Macaulay degree D:
#   * tagged Macaulay rows (generator index i, multiplier mu), boolean monomials
#     as frozensets (x^2 = x baked in); construction replicates macaulay_export.
#     macaulay_rows row-for-row (vanishing multiples kept as tagged zero rows).
#   * streaming GF(2) echelon WITH transformation tracking -> full row-kernel
#     basis = all syzygies of the generator set at degree <= D.
#   * model-syzygy family K_D = { monomial multiples of pairwise Koszul
#     f_j*e_i + f_i*e_j }  U  { monomial multiples of the boolean principal
#     (Frobenius/annihilator) family (1+f_i)*mu*e_i }  U  { unit vectors of
#     vanishing multiples }. This is exactly the family the boolean Bardet-
#     Froberg semi-regular prediction accounts for (verified: the t2 prediction
#     reproduces h012 anchors 69,073 / 143,882 / sr_pred 70,935 / 145,881).
#   * extra(D) = dim ker(M_D) - rank(K_D): syzygies beyond Koszul/Frobenius.
#   * quotient reps (kernel basis reduced mod K_D) carry: support structure,
#     block histogram (which S_3 of the chain), multiplier degrees, and the
#     POT/F5-style signature (max generator index, then max multiplier monomial
#     in degrevlex). F5 reading: Koszul = F5-criterion syzygies; monomial
#     multiples of a lower-degree syzygy = rewritten-rule syzygies; the rest =
#     non-rewritable.
#
# Gate (runs first, per spec): (V1) a support-matched random null must classify
#   as fully rewritable (extra = 0, rank == semi-regular prediction); (V2) a
#   system with an INJECTED known non-Koszul linear syzygy must be detected
#   with the correct support. No panel number is recorded unless the gate
#   passes.
#
# Yokoyama arm (#G*): instrumented grevlex Buchberger (normal strategy,
#   product criterion) counting every nonzero S-remainder appended = the
#   paper's #(G* \ F); ideal I = <F(x_1..x_m), S_{m+1}(x_1..x_m, xR)> over F_p,
#   attack-realistic factor base (curve-point x-coords), decomposable targets.
#   #NS(modified) = d^m - #V - (d - 2^{m-1})^m. Scale m*d^{m-1}.
#
# All RNG seeded (set_random_seed + random.Random + md5-derived stable ints).

import sys, os, time, json, itertools, hashlib, random
from pathlib import Path

# The driver (SIG_run.sage) inserts this file's directory into sys.path BEFORE
# load()ing this instrument, so the sibling .py modules import cleanly.
if str(Path.cwd()) not in sys.path:
    sys.path.insert(0, str(Path.cwd()))

from sage.all import GF, PolynomialRing, EllipticCurve, EllipticCurve_from_j, set_random_seed
from semaev_tree import (build_field_and_curve, build_chained_system_symbolic,
                         weil_descend_to_F2, gen_decomposable_R, make_V_subspace)
from ic_first_fall_fast import poly_to_monoset, mono_deg, multiply


def stable_seed(*parts):
    """Deterministic seed int from arbitrary parts (stable across processes)."""
    s = "|".join(str(p) for p in parts)
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:4], "little")


def jsonsafe(o):
    if isinstance(o, dict):
        return {str(k): jsonsafe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsonsafe(v) for v in o]
    if isinstance(o, (int, float, str, bool)) or o is None:
        return o
    try:
        return int(o)
    except Exception:
        return str(o)


# --------------------------------------------------------------------------
# boolean arm: tagged Macaulay + kernel + model-syzygy family
# --------------------------------------------------------------------------

def tagged_macaulay(monosets, nb, D):
    """Rows as (tag=(i, mu), prod); vanishing products kept as empty prods.
    Row enumeration identical to macaulay_export.macaulay_rows."""
    rows = []
    for i, f in enumerate(monosets):
        fdeg = max((mono_deg(m) for m in f), default=0)
        if fdeg > D:
            continue
        for md in range(0, D - fdeg + 1):
            for combo in itertools.combinations(range(nb), md):
                mu = frozenset(combo)
                prod = multiply(f, mu)
                if prod and max(mono_deg(m) for m in prod) > D:
                    continue  # unreachable (union bound), kept for safety
                rows.append(((i, mu), prod))
    cols = sorted(set().union(*[p for _, p in rows if p]) if rows else set(),
                  key=lambda m: (mono_deg(m), tuple(sorted(m))))
    colidx = {m: c for c, m in enumerate(cols)}
    return rows, colidx


def echelon_kernel(rows, colidx, track=True):
    """Streaming GF(2) echelon. Returns (rank, kernel_bitmasks, n_dropped_zero_rows).
    kernel bitmask e: set bits = original row indices of a dependency."""
    piv = {}
    kernel = []
    dropped = 0
    for idx, (tag, prod) in enumerate(rows):
        bb = 0
        for m in prod:
            bb |= 1 << colidx[m]
        bb = int(bb)
        ee = int(1 << idx)
        while bb:
            lead = bb.bit_length() - 1
            if lead in piv:
                pr, pe = piv[lead]
                bb = bb ^^ pr
                if track:
                    ee = ee ^^ pe
            else:
                piv[lead] = (bb, ee)
                break
        if bb == 0:
            kernel.append(ee)
            if not prod:
                dropped += 1
    return len(piv), kernel, dropped


def vec_echelon(vecs):
    """Rank + pivot dict for a list of GF(2) bitmasks."""
    piv = {}
    for v in vecs:
        bb = int(v)
        while bb:
            lead = bb.bit_length() - 1
            if lead in piv:
                bb = bb ^^ piv[lead]
            else:
                piv[lead] = bb
                break
    return len(piv), piv


def reduce_against(v, piv):
    bb = int(v)
    while bb:
        lead = bb.bit_length() - 1
        if lead in piv:
            bb = bb ^^ piv[lead]
        else:
            break
    return bb


def bits_to_positions(e):
    out = []
    e = int(e)
    while e:
        low = e & (-e)
        out.append(low.bit_length() - 1)
        e = e ^^ low
    return out


def koszul_principal_vectors(monosets, nb, D, tag2idx):
    """Model syzygy family K_D as bitmasks over row indices (see header)."""
    vecs = []
    degs = [max((mono_deg(m) for m in f), default=0) for f in monosets]
    m = len(monosets)
    # pairwise Koszul f_j e_i + f_i e_j, monomial multiples
    for i in range(m):
        for j in range(i + 1, m):
            di, dj = degs[i], degs[j]
            for md in range(0, D - di - dj + 1):
                for combo in itertools.combinations(range(nb), md):
                    mu = frozenset(combo)
                    v = 0
                    for c in monosets[j]:
                        ix = tag2idx.get((i, mu | c))
                        if ix is not None:
                            v = v ^^ (1 << ix)   # XOR: repeated tags cancel (GF(2) symmetric difference)
                    for c in monosets[i]:
                        ix = tag2idx.get((j, mu | c))
                        if ix is not None:
                            v = v ^^ (1 << ix)
                    if v:
                        vecs.append(int(v))
    # principal Frobenius/annihilator (1+f_i) mu e_i
    for i in range(m):
        di = degs[i]
        for md in range(0, D - 2 * di + 1):
            for combo in itertools.combinations(range(nb), md):
                mu = frozenset(combo)
                v = 0
                ix = tag2idx.get((i, mu))
                if ix is not None:
                    v = v ^^ (1 << ix)
                for c in monosets[i]:
                    ix = tag2idx.get((i, mu | c))
                    if ix is not None:
                        v = v ^^ (1 << ix)   # constant monomial c=mu cancels the (i,mu) tag
                if v:
                    vecs.append(int(v))
    # vanishing multiples: unit vectors appended by caller (zero-row detection)
    return vecs


def semireg_rank_pred(eq_degs, nb, Dmax):
    """Boolean semi-regular prediction (verbatim semantics of t2_streaming_dreg)."""
    from math import comb
    a = [comb(nb, j) if j <= nb else 0 for j in range(Dmax + 2)]
    for d in eq_degs:
        for j in range(d, Dmax + 2):
            a[j] -= a[j - d]
    HF = []
    ok = True
    for d in range(Dmax + 2):
        if not ok or a[d] <= 0:
            HF.append(0)
            if a[d] <= 0:
                ok = False
        else:
            HF.append(a[d])
    pred = {}
    tot = 0
    for D in range(0, Dmax + 1):
        tot += comb(nb, D) - HF[D]
        pred[D] = tot
    return pred, HF


def boolean_null(monosets, nb, rng):
    """T11-boolean null (verbatim semantics of t2_streaming_dreg)."""
    null = []
    for f in monosets:
        by_deg = {}
        for mm in f:
            by_deg.setdefault(len(mm), 0)
            by_deg[len(mm)] += 1
        nf = set()
        for d, cnt in by_deg.items():
            seen = set()
            while len(seen) < cnt:
                mm = frozenset(rng.sample(range(nb), d))
                if mm not in nf:
                    seen.add(mm)
                    nf.add(mm)
        null.append(nf)
    return null


def monoset_degrevlex_key(mu, nb):
    """degrevlex key on a boolean monomial (frozenset), vars ordered by index."""
    return (len(mu), tuple(sorted(mu, reverse=True)))


def analyze_syzygy_space(monosets, nb, D, extract=True, block_size=None):
    """Full classification at one degree D. Returns dict with ranks, counts,
    and (if extract) quotient-rep structural details."""
    t0 = time.time()
    rows, colidx = tagged_macaulay(monosets, nb, D)
    tag2idx = {tag: ix for ix, (tag, _) in enumerate(rows)}
    nrows = len(rows)
    rank, kernel, dropped = echelon_kernel(rows, colidx, track=extract)
    eq_degs = [max((mono_deg(m) for m in f), default=0) for f in monosets]
    pred, HF = semireg_rank_pred(eq_degs, nb, D)
    kvecs = koszul_principal_vectors(monosets, nb, D, tag2idx)
    # vanishing multiples: add their unit vectors to the model family
    for ix, (tag, prod) in enumerate(rows):
        if not prod:
            kvecs.append(int(1 << ix))
    rankK, kpiv = vec_echelon(kvecs)
    kernel_dim = nrows - rank
    extra = kernel_dim - rankK
    rec = {
        "D": D, "nb": nb, "nrows": nrows, "ncols": len(colidx),
        "rank": rank, "sr_pred": pred[D], "deficit": int(pred[D] - rank),
        "kernel_dim": kernel_dim, "rankK": rankK, "extra": int(extra),
        "dropped_multiples": dropped,
        "sec": round(time.time() - t0, 2),
    }
    if extract and extra > 0:
        reps = []
        for kv in kernel:
            r = reduce_against(kv, kpiv)
            if r:
                reps.append(r)
        # structural description of quotient representatives
        rep_desc = []
        for r in reps:
            pos = bits_to_positions(r)
            tags = [rows[p][0] for p in pos]
            gens_used = sorted({t[0] for t in tags})
            mult_degs = sorted({len(t[1]) for t in tags})
            # POT/F5 signature: max generator index, then max multiplier (degrevlex)
            imax = max(gens_used)
            mu_max = max((t[1] for t in tags if t[0] == imax),
                         key=lambda mu: monoset_degrevlex_key(mu, nb))
            rep_desc.append({
                "support_rows": len(pos),
                "n_generators": len(gens_used),
                "gen_index_max": imax,
                "gen_index_min": min(gens_used),
                "mult_degrees": mult_degs,
                "sig": [imax, sorted(mu_max), len(mu_max)],
                "blocks": (sorted({t[0] // block_size for t in tags})
                           if block_size else []),
            })
        rec["extra_reps"] = rep_desc
        rec["kernel_vectors"] = [bits_to_positions(kv) for kv in kernel
                                 if reduce_against(kv, kpiv)]
    elif extract:
        rec["extra_reps"] = []
    return rec, rows, kernel, kpiv


def build_boolean_semaev(n, t, seed):
    """Build the boolean chained Semaev system (semaev_tree builder), decomposable R.
    Returns (monosets, nb, meta)."""
    k = (n + t - 1) // t
    Fq, E, alpha, A, B = build_field_and_curve(n)
    V = make_V_subspace(Fq, alpha, k)
    rng = random.Random(stable_seed("semaev", n, t, seed))
    R = None
    for _ in range(400):
        try:
            R, pts = gen_decomposable_R(E, t, V, rng=rng)
            break
        except Exception:
            continue
    if R is None:
        return None, None, {"error": "no decomposable R"}
    Rh, polys, _ = build_chained_system_symbolic(t, Fq, B, R[0])
    Bring, dpolys = weil_descend_to_F2(polys, n, k, alpha, Rh)
    nb = int(Bring.ngens())
    monosets = [mm for mm in (poly_to_monoset(p) for p in dpolys) if mm]
    meta = {"n": n, "t": t, "k": k, "nb": nb, "n_eqs": len(monosets),
            "eq_degs_hist": {str(d): sum(1 for f in monosets
                                         if max(mono_deg(m) for m in f) == d)
                             for d in (1, 2, 3, 4)},
            "curve_A": str(A), "curve_B": str(B),
            "R_x": str(R[0]), "seed": seed}
    return monosets, nb, meta


def classify_cell(n, t, seed, Ds, d5_count_only=False):
    """One boolean cell: Semaev + matched null, per-D classification, plus the
    D3-syzygy-multiples (F5 rewritten-rule) analysis at D4."""
    monosets, nb, meta = build_boolean_semaev(n, t, seed)
    if monosets is None:
        return {"meta": meta, "skipped": True}
    cell = {"meta": meta, "sem": {}, "null": {}}
    rng = random.Random(stable_seed("null", n, t, seed))
    null_ms = boolean_null(monosets, nb, rng)
    sem_aux = {}
    for D in Ds:
        rec_s, rows_s, kernel_s, kpiv_s = analyze_syzygy_space(
            monosets, nb, D, extract=True, block_size=n)
        cell["sem"][str(D)] = rec_s
        sem_aux[D] = (rows_s, kernel_s, kpiv_s)
        rec_n, _, _, _ = analyze_syzygy_space(null_ms, nb, D, extract=False,
                                              block_size=n)
        rec_n.pop("extra_reps", None)
        cell["null"][str(D)] = rec_n
    # ---- F5 rewritten-rule analysis: multiples of the D3 syzygies inside D4
    if 3 in sem_aux and 4 in sem_aux:
        rows3, kernel3, _ = sem_aux[3]
        rows4, kernel4, kpiv4 = sem_aux[4]
        tag2idx4 = {tag: ix for ix, (tag, _) in enumerate(rows4)}
        v3_mults = []
        for kv in kernel3:
            pos3 = bits_to_positions(kv)
            tags3 = [rows3[p][0] for p in pos3]
            for j in range(nb):
                img = 0
                for (i, mu) in tags3:
                    ix = tag2idx4.get((i, mu | {j}))
                    if ix is not None:
                        img = img ^^ (1 << ix)
                if img:
                    v3_mults.append(int(img))
        red = [reduce_against(v, kpiv4) for v in v3_mults]
        red = [r for r in red if r]
        rank_v3mod, _ = vec_echelon(red)
        cell["v3_multiples_at_D4"] = {
            "n_d3_syzygies": len(kernel3),
            "n_mult_images": len(v3_mults),
            "rank_mod_K4": rank_v3mod,
            "residual_new_at_D4": int(cell["sem"]["4"]["extra"] - rank_v3mod),
        }
    if d5_count_only:
        D = 5
        rec_s5, _, _, _ = analyze_syzygy_space(monosets, nb, D, extract=False,
                                               block_size=n)
        rec_s5.pop("extra_reps", None)
        cell["sem"][str(D)] = rec_s5
    return cell


# --------------------------------------------------------------------------
# Yokoyama arm: instrumented Buchberger #G* (verbatim semantics of
# t3_gstar_buchberger.sage) + S4 for m=3 + CM/isogenous panel
# --------------------------------------------------------------------------

def S3_odd(X1, X2, X3, a, b):
    return ((X1 - X2) ** 2 * X3 ** 2
            - 2 * ((X1 + X2) * (X1 * X2 + a) + 2 * b) * X3
            + ((X1 * X2 - a) ** 2 - 4 * b * (X1 + X2)))


def S4_odd_factory(F, a, b):
    """S4(x1,x2,x3,x4) = Res_X(S3(x1,x2,X), S3(x3,x4,X)) over F_p."""
    R4 = PolynomialRing(F, ['x1', 'x2', 'x3', 'x4', 'X'], order='degrevlex')
    x1, x2, x3, x4, X = R4.gens()
    S3a = S3_odd(x1, x2, X, a, b)
    S3b = S3_odd(x3, x4, X, a, b)
    S4 = S3a.resultant(S3b, X)
    return S4, R4


def full_reduce(h, G, LG):
    R = h.parent()
    r = R(0)
    h = h - R(0)
    while h != 0:
        hm = h.lm()
        red = False
        for i in range(len(G)):
            if LG[i].divides(hm):
                h = h - (h.lc() / G[i].lc()) * (hm // LG[i]) * G[i]
                red = True
                break
        if not red:
            r += h.lt()
            h -= h.lt()
    return r


def buchberger_instrumented(gens, strategy="normal", time_limit=55):
    """#G* = number of nonzero S-remainders appended (paper's #(G* \\ F)).
    Time-boxed: returns {'censored': 'time'} if the box expires (recorded as
    censored, NOT evidence, per AGENTS rule 5)."""
    import signal
    class _TO(Exception):
        pass
    def _h(s, f):
        raise _TO()
    signal.signal(signal.SIGALRM, _h)
    signal.setitimer(signal.ITIMER_REAL, time_limit)
    try:
        R = gens[0].parent()
        G = [g - R(0) for g in gens if g != 0]
        for i in range(len(G)):
            G[i] = G[i] / G[i].lc()
        LG = [g.lm() for g in G]
        pairs = [(i, j) for i in range(len(G)) for j in range(i + 1, len(G))]
        gstar = 0
        zero_red = 0
        npairs = 0
        max_deg = max(g.degree() for g in G)
        while pairs:
            k = min(range(len(pairs)),
                    key=lambda k: (LG[pairs[k][0]].lcm(LG[pairs[k][1]]),
                                   pairs[k]))
            (i, j) = pairs.pop(k)
            if LG[i].lcm(LG[j]) == LG[i] * LG[j]:
                continue
            npairs += 1
            L = LG[i].lcm(LG[j])
            S = (L // G[i].lt()) * G[i] - (L // G[j].lt()) * G[j]
            r = full_reduce(S, G, LG)
            if r == 0:
                zero_red += 1
            else:
                r = r / r.lc()
                G.append(r)
                LG.append(r.lm())
                gstar += 1
                max_deg = max(max_deg, r.degree())
                pairs.extend((i2, len(G) - 1) for i2 in range(len(G) - 1))
        unit = any(g.degree() == 0 for g in G)
        return {"gstar": gstar, "zero_red": zero_red, "pairs": npairs,
                "max_deg": max_deg, "gb_size": len(G), "unit": unit}
    except _TO:
        return {"censored": "time>%ds" % time_limit}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def build_panel(p):
    """CM panel: generic, j=0, 1728, -3375, 8000, -32768 + isogenous partners
    (same order verified). Deterministic per-curve parameters."""
    F = GF(p)
    panel = []
    set_random_seed(stable_seed("panel", p))
    a0 = F.random_element()
    b0 = F.random_element()
    while (4 * a0 ** 3 + 27 * b0 ** 2) == 0:
        b0 = F.random_element()
    panel.append((a0, b0, "generic"))
    panel.append((F(0), F(stable_seed("j0b", p) % (p - 1) + 1), "CM j=0"))
    panel.append((F(stable_seed("j1728a", p) % (p - 1) + 1), F(0), "CM j=1728"))
    for jv, lab in [(-3375, "CM j=-3375"), (8000, "CM j=8000"), (-32768, "CM j=-32768")]:
        E = EllipticCurve_from_j(F(jv))
        panel.append((E.a4(), E.a6(), lab))
    out = []
    for (a, b, lab) in panel:
        E = EllipticCurve(F, [a, b])
        out.append((a, b, lab, E))
    # isogenous partners (control): first small-degree isogeny codomain,
    # same-order verified
    iso = []
    for (a, b, lab, E) in out:
        found = None
        for ell in (2, 3, 5, 7):
            try:
                isogs = E.isogenies_prime_degree(ell)
            except Exception:
                isogs = []
            if isogs:
                cod = isogs[0].codomain()
                try:
                    if cod.cardinality() == E.cardinality():
                        found = (cod.a4(), cod.a6(), "iso(%s)" % lab, cod)
                        break
                except Exception:
                    pass
        if found is not None:
            iso.append(found)
        else:
            iso.append((a, b, "iso(%s) NONE-FOUND" % lab, E))
    return out, iso


def gstar_cell(E, m, d, seed, xR_kind="decomp", time_limit=55):
    """One Yokoyama cell: I = <F(x_1..x_m), S_{m+1}(x_1..x_m,xR)>."""
    F = E.base_field()
    p = F.order()
    set_random_seed(stable_seed("gstar", str(E.a4()), str(E.a6()), m, d, seed))
    base, pts = [], []
    while len(base) < d:
        Pt = E.random_point()
        if Pt[0] not in base:
            base.append(Pt[0])
            pts.append(Pt)
    if xR_kind == "decomp":
        xR = (sum(pts[:m], E(0, 1, 0)))[0]
    else:
        xR = F.random_element()
    names = ['x%d' % (i + 1) for i in range(m)]
    R = PolynomialRing(F, names, order='degrevlex')
    xs = R.gens()
    if m == 2:
        a, b = E.a4(), E.a6()
        Sm1 = S3_odd(xs[0], xs[1], F(xR), a, b)
    else:
        S4, R4 = S4_odd_factory(F, E.a4(), E.a6())
        x4 = R4.gens()[3]
        Sm1 = S4.subs({x4: F(xR)})
        Sm1 = R(Sm1)
    gens = []
    for i in range(m):
        Fi = prod(xs[i] - r for r in base)
        gens.append(Fi)
    gens.append(Sm1)
    # #V enumeration
    nV = 0
    if m == 2:
        a, b = E.a4(), E.a6()
        for u in base:
            for v in base:
                if S3_odd(u, v, F(xR), a, b) == 0:
                    nV += 1
    else:
        for u in base:
            for v in base:
                for w in base:
                    if Sm1(u, v, w) == 0:
                        nV += 1
    delta = 2 ** (m - 1)
    nNS = d ** m - nV - (d - delta) ** m
    t0 = time.time()
    res = buchberger_instrumented(gens, strategy="normal", time_limit=time_limit)
    res["sec"] = round(time.time() - t0, 2)
    res.update({"m": m, "d": d, "seed": seed, "target": xR_kind,
                "nV": int(nV), "nNS": int(nNS),
                "scale_mdm1": int(m * d ** (m - 1))})
    if "gstar" in res:
        res["ratio_scale"] = res["gstar"] / float(m * d ** (m - 1))
        res["ratio_ns"] = (res["gstar"] / float(nNS)) if nNS else None
    return res


# --------------------------------------------------------------------------
# Betti arm (verbatim semantics of t11_null_harness / t5_betti_redux)
# --------------------------------------------------------------------------

def parse_resolution_string(s):
    B = {}
    for i, chunk in enumerate(s.split(" <-- ")):
        chunk = chunk.strip()
        if chunk == "0" or not chunk:
            continue
        for term in chunk.split("⊕"):
            term = term.strip()
            if term.startswith("S(-"):
                j = int(term[3:-1])
            elif term.startswith("S("):
                j = -int(term[2:-1])
            else:
                continue
            B[(i, j)] = B.get((i, j), 0) + 1
    return B


def betti_table_homog(polys, Rng):
    F = Rng.base_ring()
    Rh = PolynomialRing(F, [str(v) for v in Rng.gens()] + ['h'], order='degrevlex')
    h = Rh.gens()[-1]
    hom = [Rh(f).homogenize(h) for f in polys]
    I = Rh.ideal(hom)
    try:
        Braw = parse_resolution_string(str(I.graded_free_resolution()))
        B = {"(%d, %d)" % kk: int(v) for kk, v in Braw.items()}
        pdim = max((kk[0] for kk in Braw.keys()), default=0)
        reg = max((kk[1] - kk[0] for kk in Braw.keys()), default=0)
    except Exception as e:
        B = {"error": str(type(e).__name__) + ": " + str(e)[:100]}
        reg = None
        pdim = None
    return B, reg, pdim


def betti_l1(B1, B2):
    keys = (set(B1.keys()) | set(B2.keys())) - {"error", "unparsed"}
    return int(sum(abs(B1.get(k, 0) - B2.get(k, 0)) for k in keys))


def randomize_on_support(Rng, f, rng):
    """Support-matched null generator (t11 semantics), deterministic via rng."""
    F = Rng.base_ring()
    p = F.order()
    g = Rng(0)
    for mm in f.monomials():
        g += F(rng.randint(1, p - 1)) * mm
    return g


def chained_gens_prime(Rng, t, a, b, xR):
    vs = list(Rng.gens())
    xs = vs[:t]
    us = vs[t:]
    apex = list(us) + [xR]
    polys = [S3_odd(xs[0], xs[1], apex[0], a, b)]
    for i in range(2, t):
        polys.append(S3_odd(apex[i - 2], xs[i], apex[i - 1], a, b))
    return polys
