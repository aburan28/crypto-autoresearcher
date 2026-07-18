# EXP-STR-001 / STR-H-001: Displacement-rank relation matrices from AP supports (candidate A3)
# Minimal falsifying experiment. See experiments/EXP-STR-001/specification.yaml (frozen protocol).
# Run: sage experiments/EXP-STR-001/str1_ap_matrix.sage
# Deterministic: all RNG streams derive arithmetically from the frozen seeds.

import json, math, os, platform, random, resource, subprocess, sys, time
from datetime import datetime, timezone
from itertools import combinations

# ---------------- frozen parameters (specification.yaml) ----------------
PRIMES = [int(x) for x in [211, 1009, 4099]]
D_MAX = int(64)                      # D = {1..64}
MS = [int(x) for x in [3, 4]]
SEEDS = [int(x) for x in [20260717, 20260718, 20260719, 20260720, 20260721, 20260722]]
N_TARGETS = int(16)
ENUM_CAP = int(120000)
NEG_SAMPLES = int(20000)
SELF_CAP_SECONDS = 480               # stop launching new instances past this; write partial json
WALL_LIMIT_SECONDS = 600             # coordinator kill rule (external)
INV_CHARGE = int(15)                 # F_p mul-equivalents per inversion (frozen charging rule)
MULS_PER_EC_ADD = int(4) + INV_CHARGE

RUN_DIR = "experiments/EXP-STR-001/runs/RUN-STR-001-a"
RAW_PATH = os.path.join(RUN_DIR, "raw.json")

T0 = time.time()
T_START_ISO = datetime.now(timezone.utc).isoformat()

def log(msg):
    print("[str1 %8.2fs] %s" % (time.time() - T0, msg), flush=True)

def sub_seed(seed, p, m, code):
    # deterministic integer combination; no str hashing anywhere
    return int(int(seed) + int(p) * 10000019 + int(m) * 100003 + int(code))

# ---------------- curve generation (Sage) ----------------
def gen_curve(p, seed):
    rng = random.Random(sub_seed(seed, p, 0, 1))
    F = GF(p)
    attempts = 0
    while attempts < 500:
        attempts += 1
        a = F(rng.randrange(p)); b = F(rng.randrange(p))
        if (4 * a**3 + 27 * b**2) == 0:
            continue
        E = EllipticCurve(F, [a, b])
        n = int(E.order())
        if n == p:            # exclude anomalous (standard exclusions)
            continue
        if not is_prime(n):
            continue
        return E, n, attempts
    raise RuntimeError("no prime-order curve found after 500 attempts")

def build_fb(E, p, B):
    fb = []
    x = 0
    while len(fb) < B and x < p:
        if E.is_x_coord(x):
            P = E.lift_x(x)
            y = int(P[1])
            if y > p - y:
                P = -P
                y = int(P[1])
            fb.append((int(x), int(y)))
        x += 1
    if len(fb) < B:
        raise RuntimeError("x-interval exhausted before B points")
    return fb  # ordered by x; entries (x, y) python ints, canonical y

# ---------------- pure-python EC arithmetic (speed; cross-checked vs Sage) ----------------
def ec_add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        s = (3 * x1 * x1 + a) * pow((2 * y1) % p, -1, p) % p
    else:
        s = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (s * s - x1 - x2) % p
    y3 = (s * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(P, k, a, p):
    R = None
    Q = P
    while k:
        if k & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_add(Q, Q, a, p)
        k >>= 1
    return R

def tuple_sum(fb, idxs, a, p):
    S = None
    for j in idxs:
        S = ec_add(S, fb[j], a, p)
    return S

# ---------------- AP + baseline support enumeration ----------------
def enum_ap_tuples(fb_xs, x_to_idx, x_max, m):
    out = set()
    for d in range(1, D_MAX + 1):
        span = (m - 1) * d
        if span > x_max:
            break
        for x in fb_xs:
            if x + span > x_max:
                break
            idxs = []
            ok = True
            for k in range(m):
                j = x_to_idx.get(x + k * d)
                if j is None:
                    ok = False
                    break
                idxs.append(j)
            if ok:
                out.add(tuple(sorted(idxs)))
    return sorted(out)

def baseline_tuples(B, m, rng):
    total = math.comb(B, m)
    if total <= ENUM_CAP:
        return list(combinations(range(B), m)), total, False
    keep = set(rng.sample(range(total), ENUM_CAP))
    out = []
    for i, t in enumerate(combinations(range(B), m)):
        if i in keep:
            out.append(t)
    return out, total, True

def sum_multiset(fb, tuples, a, p):
    d = {}
    for t in tuples:
        S = tuple_sum(fb, t, a, p)
        key = S if S is not None else ("O",)
        d[key] = d.get(key, 0) + 1
    return d

# ---------------- Berlekamp-Massey + Wiedemann over F_n (pure python ints) ----------------
def berlekamp_massey(s, q):
    C = [1]; Bv = [1]; L = 0; m = 1; b = 1
    for n in range(len(s)):
        d = s[n] % q
        for i in range(1, L + 1):
            d = (d + C[i] * s[n - i]) % q
        if d == 0:
            m += 1
        elif 2 * L <= n:
            T = C[:]
            coef = d * pow(b, -1, q) % q
            need = m + len(Bv)
            if len(C) < need:
                C += [0] * (need - len(C))
            for j in range(len(Bv)):
                C[j + m] = (C[j + m] - coef * Bv[j]) % q
            L = n + 1 - L
            Bv = T; b = d; m = 1
        else:
            coef = d * pow(b, -1, q) % q
            need = m + len(Bv)
            if len(C) < need:
                C += [0] * (need - len(C))
            for j in range(len(Bv)):
                C[j + m] = (C[j + m] - coef * Bv[j]) % q
            m += 1
    return C, L  # sum_{i=0..L} C[i] * s_{n-i} = 0 for n >= L

def matvec_sparse(rows, v, q):
    out = []
    for cols in rows:
        acc = 0
        for j in cols:
            acc += v[j]
        out.append(acc % q)
    return out

def wiedemann_solve(rows, Bsz, q, rng):
    """Solve M x = b over F_q; M given as list of sorted col-index lists (0/1 matrix).
       Returns (x, info) or (None, info)."""
    attempts = 0
    t_start = time.time()
    matvecs = 0
    while attempts < 5:
        attempts += 1
        u = [rng.randrange(q) for _ in range(Bsz)]
        b = [rng.randrange(q) for _ in range(Bsz)]
        v = b[:]
        s = []
        for i in range(2 * Bsz + 1):
            s.append(sum(u[j] * v[j] for j in range(Bsz)) % q)
            v = matvec_sparse(rows, v, q)
            matvecs += 1
        C, L = berlekamp_massey(s, q)
        if L == 0 or C[L] % q == 0:
            continue
        # g(X) = sum_i C[i] X^{L-i} annihilates b; constant term C[L]
        w = [0] * Bsz
        vk = b[:]
        # x = -(1/C[L]) * sum_{i=0}^{L-1} C[i] * M^{L-1-i} b
        powers = [b[:]]
        for k in range(1, L):
            powers.append(matvec_sparse(rows, powers[-1], q))
            matvecs += 1
        for i in range(L):
            ck = C[i] % q
            if ck:
                pv = powers[L - 1 - i]
                for j in range(Bsz):
                    w[j] = (w[j] + ck * pv[j]) % q
        inv_c = pow(C[L] % q, -1, q)
        x = [(-w[j] * inv_c) % q for j in range(Bsz)]
        ok = (matvec_sparse(rows, x, q) == [bb % q for bb in b])
        matvecs += 1
        if ok:
            return x, {"attempts": attempts, "minpoly_deg": L, "matvecs": matvecs,
                       "seconds": time.time() - t_start, "verified": True}
    return None, {"attempts": attempts, "matvecs": matvecs,
                  "seconds": time.time() - t_start, "verified": False}

# ---------------- displacement rank ----------------
def displacement_rank(ap_row_keys, row_count, fb_xs, x_to_idx, Bsz, q, m, rng, randomized_baseline):
    """alpha = rank over F_q of (Z_r M - M Z_c), x-space translation by +1 on both sides.
       ap_row_keys: list of (x_start, d) for AP rows; for the random baseline, rows are
       random m-subsets and the row-shift map matches elementwise x+1 shifted sets."""
    F = GF(q)
    if randomized_baseline:
        total_comb = math.comb(Bsz, m)
        if row_count * 2 <= total_comb:
            rows = set()
            while len(rows) < row_count:
                rows.add(tuple(sorted(rng.sample(range(Bsz), m))))
            rows = sorted(rows)
        else:  # avoid coupon-collector blowup; exact sample without replacement
            rows = sorted(tuple(sorted(t)) for t in
                          rng.sample(list(combinations(range(Bsz), m)), min(row_count, total_comb)))
        row_set = {r: i for i, r in enumerate(rows)}
        # row shift: elementwise FB-index translation is meaningless for random rows;
        # use x-space shift on the actual support x's, matched if the shifted set is a row.
        row_shift = {}
        for i, r in enumerate(rows):
            shifted = []
            ok = True
            for j in r:
                x1 = fb_xs[j] + 1
                j1 = x_to_idx.get(x1)
                if j1 is None:
                    ok = False
                    break
                shifted.append(j1)
            if ok:
                tgt = row_set.get(tuple(sorted(shifted)))
                if tgt is not None:
                    row_shift[i] = tgt
        row_list = rows
    else:
        row_list = ap_row_keys  # (x_start, d)
        row_set = {rk: i for i, rk in enumerate(row_list)}
        row_shift = {}
        for i, (xs, d) in enumerate(row_list):
            tgt = row_set.get((xs + 1, d))
            if tgt is not None:
                row_shift[i] = tgt
    R = len(row_list)
    # support of each row
    if randomized_baseline:
        supports = [set(r) for r in row_list]
    else:
        supports = []
        for (xs, d) in row_list:
            supports.append(set(x_to_idx[xs + k * d] for k in range(m)))
    # column shift: col j -> col of x_j + 1 (if in FB)
    col_shift = {}
    for j in range(Bsz):
        j1 = x_to_idx.get(fb_xs[j] + 1)
        if j1 is not None:
            col_shift[j] = j1
    # Delta = Z_r M - M Z_c  (R x Bsz over F_q), sparse assembly
    entries = {}
    for i in range(R):
        si = supports[i]
        r_tgt = row_shift.get(i)
        if r_tgt is not None:
            for j in si:
                entries[(r_tgt, j)] = entries.get((r_tgt, j), 0) + 1   # (Z_r M)[r_tgt][j] += 1
        for j in si:
            c_tgt = col_shift.get(j)
            if c_tgt is not None:
                entries[(i, c_tgt)] = entries.get((i, c_tgt), 0) - 1   # (M Z_c)[i][c_tgt] += 1
    Mdelta = matrix(F, R, Bsz, sparse=True)
    for (i, j), v in entries.items():
        Mdelta[i, j] = v
    return int(Mdelta.rank()), R

def classic_displacement_rank(supports_ordered, Bsz, q):
    """Standard (Z, Z^T) displacement rank: alpha = rank(M - Z_R M Z_B^T) over F_q,
       Z = nilpotent lower shift. Toeplitz matrices give rank <= 2; generic matrices
       give ~ min(R, Bsz). Rows of M must be supplied in the claimed structured order."""
    if len(supports_ordered) < 2:
        return None
    F = GF(q)
    R = len(supports_ordered)
    M = matrix(F, R, Bsz)
    for i, s in enumerate(supports_ordered):
        for j in s:
            M[i, j] = 1
    Delta = M.__copy__()
    Delta[1:, 1:] -= M[: R - 1, : Bsz - 1]   # (Z_R M Z_B^T)[i][j] = M[i-1][j-1]
    return int(Delta.rank())

# ---------------- negative control: AP enrichment among random x-sets ----------------
def negative_control(p, m, seed):
    """Random x-sets must show AP-pattern frequency at exactly the combinatorial rate.
       (a) machinery cross-check: direct enumeration of AP sets == closed form
           sum_{d in D} max(0, p-(m-1)d);
       (b) sampling check: adaptive N targeting >=25 expected hits (cap 3e6);
           pass if observed hits within 4 binomial sigma of expectation; if even the
           cap gives <5 expected hits, mark low_power and rely on (a)."""
    rng = random.Random(sub_seed(seed, p, m, 7))
    closed_form = sum(max(0, p - (m - 1) * d) for d in range(1, D_MAX + 1))
    direct = set()
    for d in range(1, D_MAX + 1):
        span = (m - 1) * d
        if span > p - 1:
            break
        for x in range(0, p - span):
            direct.add(tuple(x + k * d for k in range(m)))
    direct_count = len(direct)
    direct_ok = (direct_count == closed_form)
    total_sets = math.comb(p, m)
    expected = closed_form / total_sets
    N = max(NEG_SAMPLES, int(math.ceil(25.0 / expected))) if expected > 0 else NEG_SAMPLES
    N = int(min(N, 3000000))
    hits = 0
    for _ in range(N):
        s = sorted(rng.sample(range(p), m))
        diffs = [s[i + 1] - s[i] for i in range(m - 1)]
        if 1 <= diffs[0] <= D_MAX and all(dd == diffs[0] for dd in diffs):
            hits += 1
    measured = hits / N
    expected_hits = N * expected
    low_power = expected_hits < 5
    if low_power:
        sample_ok = None
    else:
        sigma = math.sqrt(expected_hits * (1 - expected))
        sample_ok = abs(hits - expected_hits) <= 4 * sigma
    ratio = (measured / expected) if expected > 0 else None
    return {"p": p, "m": m, "expected_frac": expected, "measured_frac": measured,
            "ratio": ratio, "samples": N, "expected_hits": expected_hits,
            "hits": hits, "low_power": low_power, "sample_ok": sample_ok,
            "direct_count": direct_count, "closed_form": closed_form,
            "direct_enumeration_ok": direct_ok,
            "pass": bool(direct_ok and (sample_ok is not False))}

# ---------------- calibration: seconds per F_p mul ----------------
def calibrate():
    q = 2**255 - 19
    x = 123456789; y = 987654321; acc = 0
    t = time.time()
    for _ in range(200000):
        acc = (acc + x * y) % q
    dt = (time.time() - t) / 200000.0
    return {"sec_per_python_bigint_mul_mod": dt, "acc_guard": int(acc % 97)}

# ---------------- main ----------------
def main():
    os.makedirs(RUN_DIR, exist_ok=True)
    log("EXP-STR-001 starting; primes=%s m=%s seeds=%s" % (PRIMES, MS, SEEDS))

    cal = calibrate()
    log("calibration: %s" % cal)

    neg_controls = []
    for p in PRIMES:
        for m in MS:
            nc = negative_control(p, m, SEEDS[0])
            neg_controls.append(nc)
            log("neg-control p=%d m=%d ratio=%.4f pass=%s" % (p, m, nc["ratio"], nc["pass"]))

    rows_out = []
    truncated = False
    spot_global_fail = []

    for p in PRIMES:
        for seed in SEEDS:
            if time.time() - T0 > SELF_CAP_SECONDS:
                truncated = True
                log("SELF-CAP hit; truncating remaining instances")
                break
            E, n, attempts = gen_curve(p, seed)
            a_int = int(E.a4())  # short Weierstrass: y^2 = x^3 + a4*x + a6
            B = int(math.isqrt(n) + (1 if math.isqrt(n) ** 2 < n else 0))  # ceil(sqrt(n))
            fb = build_fb(E, p, B)
            fb_xs = [pt[0] for pt in fb]
            x_to_idx = {x: i for i, x in enumerate(fb_xs)}
            x_max = fb_xs[-1]
            G = fb[0]

            for m in MS:
                if time.time() - T0 > SELF_CAP_SECONDS:
                    truncated = True
                    break
                t_inst = time.time()
                rng_enum = random.Random(sub_seed(seed, p, m, 2))
                rng_tgt = random.Random(sub_seed(seed, p, m, 3))
                rng_mat = random.Random(sub_seed(seed, p, m, 4))
                rng_wie = random.Random(sub_seed(seed, p, m, 5))

                ap_tuples = enum_ap_tuples(fb_xs, x_to_idx, x_max, m)
                ap_supply = len(ap_tuples)
                base_tuples, base_total, base_sampled = baseline_tuples(B, m, rng_enum)

                base_sums = sum_multiset(fb, base_tuples, a_int, p)
                ap_sums = sum_multiset(fb, ap_tuples, a_int, p)

                # integrity: multiset counts sum to tuple counts
                integrity_count = (sum(base_sums.values()) == len(base_tuples)) and \
                                  (sum(ap_sums.values()) == ap_supply)

                # spot-check pure-python arithmetic vs Sage EC arithmetic (8 seeded tuples)
                spot_ok = True
                spot_pool = (base_tuples if base_tuples else ap_tuples)
                for t in rng_enum.sample(spot_pool, min(8, len(spot_pool))):
                    S_py = tuple_sum(fb, t, a_int, p)
                    S_sage = None
                    for j in t:
                        Pj = E(fb[j][0], fb[j][1])
                        S_sage = Pj if S_sage is None else S_sage + Pj
                    if S_py is None:
                        match = (S_sage is None) or (S_sage == E(0))
                    else:
                        match = (S_sage is not None) and (int(S_sage[0]) == S_py[0]) and (int(S_sage[1]) == S_py[1])
                    if not match:
                        spot_ok = False
                        spot_global_fail.append({"p": p, "seed": seed, "m": m, "tuple": list(t)})

                # targets: 16 seeded multiples of G; hit counts are EXACT from multisets
                targets = []
                base_hits_total = 0
                ap_hits_total = 0
                for _ in range(N_TARGETS):
                    r = rng_tgt.randrange(1, n)
                    R = ec_mul(G, r, a_int, p)
                    key = R if R is not None else ("O",)
                    bh = base_sums.get(key, 0)
                    ah = ap_sums.get(key, 0)
                    base_hits_total += bh
                    ap_hits_total += ah
                    targets.append({"r": r, "base_hits": bh, "ap_hits": ah})

                random_hit_rate = base_hits_total / (N_TARGETS * len(base_tuples)) if base_tuples else None
                ap_hit_rate = (ap_hits_total / (N_TARGETS * ap_supply)) if ap_supply else None
                penalty = (random_hit_rate / ap_hit_rate) if (random_hit_rate and ap_hit_rate) else None

                # expected hits per target under equidistribution
                exp_hits_base = len(base_tuples) / n
                exp_hits_ap = ap_supply / n
                hit_sanity = None
                if base_tuples:
                    measured_mean = base_hits_total / N_TARGETS
                    hit_sanity = (exp_hits_base > 0) and (0.5 <= measured_mean / exp_hits_base <= 2.0)

                # exact sum-distribution stats from the full multisets (no sampling)
                distinct_base = len(base_sums)
                distinct_ap = len(ap_sums)
                max_mult_base = max(base_sums.values()) if base_sums else 0
                max_mult_ap = max(ap_sums.values()) if ap_sums else 0
                coverage_base = distinct_base / n
                coverage_ap = distinct_ap / n
                yield_per_enum_base = base_total / n          # expected relations at ONE target, full enumeration
                yield_per_enum_ap = ap_supply / n
                yield_penalty = (base_total / ap_supply) if ap_supply else None

                # displacement ranks (exact over F_n)
                alpha_ap, R_ap = None, ap_supply
                alpha_rand, rank_M_ap = None, None
                alpha_ap_classic, alpha_rand_classic = None, None
                M_full_rank_square = False
                wie = None
                dense_sec = None
                if ap_supply >= m:
                    row_keys = []
                    # reconstruct (x_start, d) keys from support tuples
                    sup_to_key = {}
                    for t in ap_tuples:
                        xs = [fb_xs[j] for j in t]
                        dd = (xs[-1] - xs[0]) // (m - 1)
                        sup_to_key[t] = (xs[0], dd)
                        row_keys.append((xs[0], dd))
                    alpha_ap, R_ap = displacement_rank(row_keys, ap_supply, fb_xs, x_to_idx, B, n, m, rng_mat, False)
                    alpha_rand, _ = displacement_rank(None, ap_supply, fb_xs, x_to_idx, B, n, m, rng_mat, True)

                    # classic (Z, Z^T) displacement rank, AP rows in (d, x_start) harvest order
                    if R_ap >= 2:
                        order = sorted(range(len(row_keys)), key=lambda i: (row_keys[i][1], row_keys[i][0]))
                        sup_ap_ordered = [[x_to_idx[row_keys[i][0] + k * row_keys[i][1]] for k in range(m)] for i in order]
                        alpha_ap_classic = classic_displacement_rank(sup_ap_ordered, B, n)
                        rng_cls = random.Random(sub_seed(seed, p, m, 6))
                        total_comb = math.comb(B, m)
                        if R_ap * 2 <= total_comb:
                            rs = set()
                            while len(rs) < R_ap:
                                rs.add(tuple(sorted(rng_cls.sample(range(B), m))))
                            sup_rand_ordered = sorted(rs)
                        else:
                            sup_rand_ordered = sorted(tuple(sorted(t)) for t in
                                rng_cls.sample(list(combinations(range(B), m)), min(R_ap, total_comb)))
                        alpha_rand_classic = classic_displacement_rank([list(t) for t in sup_rand_ordered], B, n)

                    # greedy full-rank square subsystem from AP rows over F_n
                    F = GF(n)
                    Mrows = []
                    sel = []
                    cur = matrix(F, 0, B)
                    cur_rank = 0
                    for i, t in enumerate(ap_tuples):
                        if cur_rank == B:
                            break
                        v = vector(F, B)
                        for j in t:
                            v[j] = 1
                        M2 = cur.stack(v)
                        r2 = M2.rank()
                        if r2 > cur_rank:
                            cur = M2
                            cur_rank = r2
                            sel.append(t)
                    rank_M_ap = int(cur_rank)
                    M_full_rank_square = (cur_rank == B)
                    if M_full_rank_square:
                        sparse_rows = [sorted(t) for t in sel]
                        nnz = sum(len(t) for t in sel)
                        x_sol, wie = wiedemann_solve(sparse_rows, B, n, rng_wie)
                        # dense reference
                        t_dense = time.time()
                        bv = vector(F, [rng_wie.randrange(n) for _ in range(B)])
                        try:
                            _ = cur.solve_right(bv)
                            dense_sec = time.time() - t_dense
                        except Exception:
                            dense_sec = None
                        wie["nnz"] = nnz
                        wie["wiedemann_model_ops"] = 2 * B * nnz  # ~2B matvecs x nnz

                # structured (MODEL ONLY, from measured alpha)
                structured_model_ops = None
                if alpha_ap is not None and alpha_ap > 0:
                    structured_model_ops = (alpha_ap ** 2) * B * max(1, math.ceil(math.log2(B)))

                # gate arithmetic (fully charged, F_p-mul-equivalent units)
                gate = None
                if random_hit_rate and ap_hit_rate and ap_hit_rate > 0:
                    tests_rand = B / random_hit_rate
                    tests_ap = B / ap_hit_rate
                    rel_cost_ap = tests_ap * (m - 1) * MULS_PER_EC_ADD
                    rel_cost_rand = tests_rand * (m - 1) * MULS_PER_EC_ADD
                    la_wie_ops = 2 * (B ** 2) * m
                    la_str_ops = structured_model_ops if structured_model_ops else la_wie_ops
                    la_best = min(la_wie_ops, la_str_ops)
                    gate = {
                        "relation_tests_random": tests_rand,
                        "relation_tests_ap": tests_ap,
                        "penalty_factor": penalty,
                        "supply_ratio": ap_supply / B,
                        "la_wiedemann_ops": la_wie_ops,
                        "la_structured_model_ops": la_str_ops,
                        "la_share_with_wiedemann": la_wie_ops / (la_wie_ops + rel_cost_ap),
                        "la_share_with_structured_model": la_str_ops / (la_str_ops + rel_cost_ap),
                        "n_over_B": n / B,
                    }

                positive_control_pass = bool(integrity_count and spot_ok and (hit_sanity is True))

                rec = {
                    "p": p, "seed": seed, "m": m,
                    "curve": {"a": a_int, "b": int(E.a6()), "order_n": n, "gen_attempts": attempts},
                    "B": B, "x_max": x_max,
                    "ap_supply": ap_supply,
                    "supply_ratio": ap_supply / B,
                    "baseline_tuples_enumerated": len(base_tuples),
                    "baseline_tuples_total": base_total,
                    "baseline_sampled": base_sampled,
                    "targets": targets,
                    "base_hits_total": base_hits_total,
                    "ap_hits_total": ap_hits_total,
                    "random_hit_rate_per_tuple": random_hit_rate,
                    "ap_hit_rate_per_tuple": ap_hit_rate,
                    "expected_hits_per_target_base": exp_hits_base,
                    "expected_hits_per_target_ap": exp_hits_ap,
                    "relation_penalty_factor": penalty,
                    "distinct_sums_base": distinct_base,
                    "distinct_sums_ap": distinct_ap,
                    "max_multiplicity_base": max_mult_base,
                    "max_multiplicity_ap": max_mult_ap,
                    "coverage_base": coverage_base,
                    "coverage_ap": coverage_ap,
                    "yield_per_enum_base": yield_per_enum_base,
                    "yield_per_enum_ap": yield_per_enum_ap,
                    "yield_penalty": yield_penalty,
                    "hit_rate_sanity_pass": hit_sanity,
                    "integrity_count_pass": bool(integrity_count),
                    "spot_check_pass": bool(spot_ok),
                    "positive_control_pass": positive_control_pass,
                    "alpha_ap": alpha_ap,
                    "alpha_rand_baseline": alpha_rand,
                    "alpha_ap_classic": alpha_ap_classic,
                    "alpha_rand_classic": alpha_rand_classic,
                    "ap_matrix_rows": R_ap,
                    "ap_matrix_rank": rank_M_ap,
                    "full_rank_square_from_ap": M_full_rank_square,
                    "wiedemann": wie,
                    "dense_solve_seconds": dense_sec,
                    "structured_model_ops": structured_model_ops,
                    "gate": gate,
                    "instance_seconds": time.time() - t_inst,
                }
                rows_out.append(rec)
                log("p=%d seed=%d m=%d n=%d B=%d ap_supply=%d pen=%s alpha=%s alpha_rand=%s sq=%s" % (
                    p, seed, m, n, B, ap_supply,
                    ("%.3g" % penalty) if penalty else "None",
                    alpha_ap, alpha_rand, M_full_rank_square))
            if truncated:
                break
        if truncated:
            break

    # aggregate per size
    agg = []
    for p in PRIMES:
        for m in MS:
            sub = [r for r in rows_out if r["p"] == p and r["m"] == m]
            if not sub:
                continue
            def med(key):
                vals = sorted(r[key] for r in sub if r.get(key) is not None)
                if not vals:
                    return None
                k = len(vals) // 2
                return vals[k] if len(vals) % 2 else (vals[k - 1] + vals[k]) / 2
            gates = [r["gate"] for r in sub if r.get("gate")]
            ns_ = sorted(r["curve"]["order_n"] for r in sub)
            agg.append({
                "p": p, "m": m, "instances": len(sub),
                "B_median": med("B"),
                "n_median": (ns_[len(ns_)//2] if len(ns_) % 2 else (ns_[len(ns_)//2 - 1] + ns_[len(ns_)//2]) / 2),
                "ap_supply_median": med("ap_supply"),
                "supply_ratio_median": med("supply_ratio"),
                "penalty_median": med("relation_penalty_factor"),
                "yield_penalty_median": med("yield_penalty"),
                "coverage_ap_median": med("coverage_ap"),
                "coverage_base_median": med("coverage_base"),
                "max_multiplicity_ap_median": med("max_multiplicity_ap"),
                "alpha_ap_median": med("alpha_ap"),
                "alpha_rand_median": med("alpha_rand_baseline"),
                "alpha_ap_classic_median": med("alpha_ap_classic"),
                "alpha_rand_classic_median": med("alpha_rand_classic"),
                "full_rank_square_fraction": sum(1 for r in sub if r["full_rank_square_from_ap"]) / len(sub),
                "la_share_wiedemann_median": (sorted(g["la_share_with_wiedemann"] for g in gates)[len(gates)//2] if gates else None),
                "la_share_structured_median": (sorted(g["la_share_with_structured_model"] for g in gates)[len(gates)//2] if gates else None),
                "positive_control_pass_fraction": sum(1 for r in sub if r["positive_control_pass"]) / len(sub),
            })

    # environment + provenance
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip())
    except Exception:
        commit, dirty = None, None

    out = {
        "experiment_id": "EXP-STR-001",
        "hypothesis_id": "STR-H-001",
        "run_id": "RUN-STR-001-a",
        "parameters": {"primes": PRIMES, "D": [1, D_MAX], "m": MS, "seeds": SEEDS,
                       "B_rule": "ceil(sqrt(n))", "targets_per_instance": N_TARGETS,
                       "enumeration_cap": ENUM_CAP, "negative_control_samples": NEG_SAMPLES,
                       "inv_charge_muls": INV_CHARGE},
        "calibration": cal,
        "negative_controls": neg_controls,
        "negative_control_all_pass": all(c["pass"] for c in neg_controls),
        "spot_check_failures": spot_global_fail,
        "instances": rows_out,
        "aggregate_by_size": agg,
        "truncated": truncated,
        "planned_instances": len(PRIMES) * len(SEEDS) * len(MS),
        "completed_instances": len(rows_out),
        "provenance": {
            "command": "sage experiments/EXP-STR-001/str1_ap_matrix.sage",
            "git_commit": commit, "dirty_tree": dirty,
            "sage_version": str(sage.version.version),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "started_at": T_START_ISO,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "wall_seconds": time.time() - T0,
            "cpu_seconds": time.process_time(),
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
    }
    with open(RAW_PATH, "w") as f:
        def _json_default(o):
            # sage preparser turns numeric literals into sage Integer/Rational/RealNumber;
            # coerce faithfully: integral values stay ints, everything else floats
            try:
                fv = float(o)
                iv = int(o)
                return iv if fv == iv else fv
            except (TypeError, ValueError):
                return str(o)
        json.dump(out, f, indent=1, default=_json_default)
    log("wrote %s; completed %d/%d instances; truncated=%s" % (
        RAW_PATH, len(rows_out), out["planned_instances"], truncated))

main()
