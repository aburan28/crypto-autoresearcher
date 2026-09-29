#!/usr/bin/env python3
"""Symmetrised summation-polynomial construction, Weil descent and msolve
driver for EXP-GFPN-05ff43.

Arms (m factor-base points, target R, x_R = x(R)):
  raw   (i)   : S_{m+1}(x_1..x_m, x_R) in the x_i themselves (grid interpolation,
                per-variable degree 2^{m-1}).
  S5    (ii)  : same polynomial written in e_1..e_m = elementary symmetric
                polynomials of x_1..x_m (monomials e^a with |a| <= 2^{m-1}).
  torsion_S5 (iii): with T = (0,0), x(P+T) = b/x(P), t = x + b/x:
                Q(t_1..t_m; t_R) := s(x; X) * s(x^{(1)}; X) written in e(t_1..t_m)
                and t_R = X + b/X, where s(x; X) = S_{m+1}(x, X) / (prod x_i * X)^{2^{m-2}}
                and x^{(1)} = (b/x_1, x_2, ..).  Q vanishes iff t lifts to factor-base
                points (phi(P) = x + b/x in F_p) with +-P_1 .. +-P_m in {R, R+T}.
  identity    : control -- the arm-(ii)/(iii) interpolation machinery run with
                the trivial group (monomial basis = all x-monomials); must equal raw.

All polynomials are obtained by exact interpolation: evaluate the numeric
summation polynomial (gfpn5_core, product formula, cross-checked against the
resultant recursion) at random sample points, solve the dense linear system
over F_p (python-flint nmod_mat), and verify on held-out points.  The polynomial
is built once per (prime, curve, arm) with X symbolic (degree 2^{m-1} in X) and
specialised per target (charged as construction cost, C-5).
"""
import itertools, json, os, re, subprocess, time, resource, sys
import flint
import numpy as np
from gfpn5_core import Fq, Curve, S_poly_grp, S_num_grp, S_num_res, poly_eval

# ------------------------------------------------------------------ monomials
def monomials_total(nvars, maxdeg):
    """Exponent tuples a with sum(a) <= maxdeg (graded lex order)."""
    out = []
    for d in range(maxdeg + 1):
        for a in itertools.product(range(d + 1), repeat=nvars):
            if sum(a) == d:
                out.append(a)
    return out

def monomials_box(nvars, maxdeg):
    """Exponent tuples with each a_i <= maxdeg (full box; raw arm)."""
    return list(itertools.product(range(maxdeg + 1), repeat=nvars))

def elem_sym(vals, p):
    """e_1..e_n of integers mod p."""
    e = [1] + [0] * len(vals)
    for v in vals:
        for k in range(len(vals), 0, -1):
            e[k] = (e[k] + e[k - 1] * v) % p
    return e[1:]

def eval_monomials_rows(points, monos, p):
    """numpy int64 array rows = points (already the invariant coordinates), cols = monomials."""
    A = np.array(monos, dtype=np.int64)              # (N_mono, nvars)
    nvars = A.shape[1]
    maxd = int(A.max())
    out = np.empty((len(points), len(monos)), dtype=np.int64)
    for r, pt in enumerate(points):
        pw = np.empty((nvars, maxd + 1), dtype=np.int64)
        for j in range(nvars):
            v = int(pt[j]) % p
            row = [1]
            for _ in range(maxd):
                row.append(row[-1] * v % p)
            pw[j] = row
        acc = np.ones(len(monos), dtype=np.int64)
        for j in range(nvars):
            acc = acc * pw[j][A[:, j]] % p
        out[r] = acc
    return out

def nmod_from_numpy(M, p):
    R = flint.nmod_mat(M.shape[0], M.shape[1], p)
    for i in range(M.shape[0]):
        row = M[i].tolist()
        for j, v in enumerate(row):
            if v:
                R[i, j] = v
    return R

# ------------------------------------------------------------------ counters
class OpCount:
    """F_q / F_p operation counters for construction & lifting (C-5)."""
    def __init__(self):
        self.fq_mul = 0; self.fq_add = 0; self.fq_inv = 0; self.fp_mul = 0; self.fp_add = 0
    def fp_equiv_mults(self):
        # schoolbook F_q mult = 25 F_p mults (+ 20 adds + 4 reduction mults for z^5=c);
        # inversion via Itoh-Tsujii / exponentiation ~ 150 F_q mults (conservative)
        return self.fq_mul * 29 + self.fq_inv * 150 * 29 + self.fp_mul
    def as_dict(self):
        return {"fq_mul": self.fq_mul, "fq_add": self.fq_add, "fq_inv": self.fq_inv,
                "fp_mul": self.fp_mul, "fp_add": self.fp_add,
                "fp_mult_equivalents": self.fp_equiv_mults(),
                "conversion": "F_q mul := 29 F_p mul (25 schoolbook + 4 for z^5=c reduction); F_q inv := 150 F_q mul; adds not counted in the mult-equivalent total"}

# ------------------------------------------------------------------ construction
class ArmPolynomial:
    """Polynomial of the arm in invariant coordinates with X (resp. t_R) symbolic:
    coeff[k] = dict? -> stored as numpy int64 array C[k] of shape (N_mono, 5) (z-components)."""
    def __init__(self, arm, m, monos, p, C, meta):
        self.arm, self.m, self.monos, self.p, self.C, self.meta = arm, m, monos, p, C, meta
    def specialise(self, F, val, counter=None):
        """Return F_q coefficient vector (numpy (N_mono,5)) of the polynomial at X = val (F_q element)."""
        K = self.C.shape[0]
        vc = F.coeffs(val)
        # Horner in F_q on numpy component arrays: acc = acc*val + C[k]
        acc = self.C[K - 1].copy()
        for k in range(K - 2, -1, -1):
            acc = fq_mul_rows(acc, vc, self.p, F.cmod)
            acc = (acc + self.C[k]) % self.p
            if counter is not None:
                counter.fq_mul += acc.shape[0]; counter.fq_add += acc.shape[0]
        return acc

def fq_mul_rows(A, v, p, cmod):
    """Multiply each row (F_q element as 5 F_p coeffs) of A by the F_q element v (5 coeffs), z^5 = cmod."""
    prod = np.zeros((A.shape[0], 9), dtype=np.int64)
    for i in range(5):
        if v[i]:
            prod[:, i:i + 5] = (prod[:, i:i + 5] + A * int(v[i])) % p
    out = prod[:, :5].copy()
    out[:, :4] = (out[:, :4] + prod[:, 5:9] * cmod) % p
    return out

def _dedupe_ok(vals):
    return len(set(vals)) == len(vals)

def sample_points_x(E, m, npts, rng, pool):
    """Random m-tuples of distinct pool x-values (F_p ints) with lifts (points) on E."""
    pts = []
    while len(pts) < npts:
        xs = rng.sample(pool, m)
        pts.append(xs)
    return pts

def build_pool_x(E, rng, size_limit=None):
    """x in F_p whose f(x) is a square in F_q (so a point exists) -- pool for arm (ii)."""
    F = E.F
    pool = []
    for x in range(1, F.p):
        if E.f(F(x)).is_square():
            pool.append(x)
        if size_limit and len(pool) >= size_limit:
            break
    return pool

def build_pool_t(E, rng, size_limit=None):
    """t in F_p such that X^2 - tX + b splits in F_q with root x giving a point (arm iii).
    Returns dict t -> x (one root, as F_q element)."""
    F = E.F; b = E.a4
    assert E.a6 == 0
    pool = {}
    for t in range(1, F.p):
        tt = F(t)
        disc = tt * tt - 4 * b
        if not disc.is_square():
            continue
        x = (tt + disc.sqrt()) / 2
        if x == 0:
            continue
        if E.f(x).is_square():
            pool[t] = x
        if size_limit and len(pool) >= size_limit:
            break
    return pool

def rhs_arm_S(E, xs_int, m):
    """Arm (ii)/(identity): S_{m+1}(x_1..x_m, X) coefficients in X (list of F_q, len 2^{m-1}+1)."""
    F = E.F
    pts = [E.lift_x(F(x)) for x in xs_int]
    assert all(P is not None for P in pts)
    return S_poly_grp(E, pts)

def laurent_to_tR(F, cs, b):
    """cs: coefficients c_{-K}..c_{K} (index k+K) of a Laurent polynomial in X invariant
    under X -> b/X (c_{-k} = b^k c_k).  Returns polynomial in t = X + b/X of degree K."""
    K = (len(cs) - 1) // 2
    # check invariance
    bk = F.one
    for k in range(1, K + 1):
        bk = bk * b
        assert cs[K - k] == bk * cs[K + k], f"Laurent coefficients not X->b/X invariant at k={k}"
    # u_k(t) with X^k + (b/X)^k = u_k(t): u_0 = 2, u_1 = t, u_{k+1} = t u_k - b u_{k-1}
    u_prev = [2 * F.one]; u_cur = [F.zero, F.one]
    out = [F.zero] * (K + 1)
    out[0] += cs[K]
    for k in range(1, K + 1):
        for i, c in enumerate(u_cur):
            out[i] += cs[K + k] * c
        # next
        nxt = [F.zero] * (len(u_cur) + 1)
        for i, c in enumerate(u_cur):
            nxt[i + 1] += c
        for i, c in enumerate(u_prev):
            nxt[i] -= b * c
        u_prev, u_cur = u_cur, nxt
    return out

def rhs_arm_T(E, ts_int, m, pool_t, T):
    """Arm (iii): Q(t_1..t_m; t_R) coefficients in t_R (list of F_q, len 2^{m-1}+1)."""
    F = E.F; b = E.a4
    xs = [pool_t[t] for t in ts_int]
    pts = [E.lift_x(x) for x in xs]
    assert all(P is not None for P in pts)
    K = 2 ** (m - 1)                       # degree of S_{m+1} in X
    h = K // 2
    s1 = S_poly_grp(E, pts)                # S_{m+1}(x; X)
    pts2 = [E.add(pts[0], T)] + pts[1:]    # x_1 -> b/x_1
    assert pts2[0][0] == b / pts[0][0]
    s2 = S_poly_grp(E, pts2)
    # product polynomial degree 2K in X
    prod = [F.zero] * (2 * K + 1)
    for i, a in enumerate(s1):
        if a == 0: continue
        for j, c in enumerate(s2):
            prod[i + j] += a * c
    # Laurent normalisation: divide by (prod x_i)^h (b/x_1 prod_{i>=2} x_i)^h X^{K}
    px = F.one
    for P in pts: px = px * P[0]
    px2 = b / pts[0][0]
    for P in pts[1:]: px2 = px2 * P[0]
    norm = (px * px2) ** h
    cs = [c / norm for c in prod]          # index k + K  <->  X^{k}
    return laurent_to_tR(F, cs, b)

def build_arm_polynomial(E, arm, m, rng, pool, T=None, extra_rows=64, holdout=32, log=print):
    """Interpolate the arm polynomial with X (t_R) symbolic.  Returns ArmPolynomial."""
    F = E.F; p = F.p
    K = 2 ** (m - 1)
    if arm == "identity":
        monos = monomials_box(m, K)
    elif arm.startswith("torsion_S") or (arm.startswith("S") and arm[1:].isdigit()):
        monos = monomials_total(m, K)
    else:
        raise ValueError(arm)
    N = len(monos)
    npts = N + extra_rows + holdout
    log(f"[build] arm={arm} m={m} p={p} N_mono={N} sampling {npts} points")
    t0 = time.time()
    pool_list = sorted(pool) if isinstance(pool, dict) else list(pool)
    pts = [rng.sample(pool_list, m) for _ in range(npts)]
    if arm.startswith("torsion"):
        rhs = [rhs_arm_T(E, xs, m, pool, T) for xs in pts]
        inv = [elem_sym(xs, p) for xs in pts]
    elif arm == "identity":
        rhs = [rhs_arm_S(E, xs, m) for xs in pts]
        inv = [list(xs) for xs in pts]
    else:
        rhs = [rhs_arm_S(E, xs, m) for xs in pts]
        inv = [elem_sym(xs, p) for xs in pts]
    t_eval = time.time() - t0
    log(f"[build] evaluated {npts} RHS in {t_eval:.1f}s")
    # square interpolation matrix on the first N rows; RHS matrix with (K+1)*5 columns
    t1 = time.time()
    Msq = flint.nmod_mat(N, N, p)
    for r0 in range(0, N, 256):                      # block-wise: never hold a second full matrix
        blk = eval_monomials_rows(inv[r0:min(N, r0 + 256)], monos, p)
        for i in range(blk.shape[0]):
            row = blk[i].tolist()
            for j, v in enumerate(row):
                if v: Msq[r0 + i, j] = v
        del blk
    Bsq = flint.nmod_mat(N, (K + 1) * 5, p)
    for r in range(N):
        for k in range(K + 1):
            cs = F.coeffs(rhs[r][k])
            for j in range(5):
                if cs[j]:
                    Bsq[r, k * 5 + j] = cs[j]
    log(f"[build] matrices built in {time.time()-t1:.1f}s; solving {N}x{N} with {(K+1)*5} right-hand sides")
    t2 = time.time()
    try:
        Xs = Msq.solve(Bsq)
    except Exception as e:
        raise RuntimeError(f"interpolation matrix singular: {e}")
    del Msq, Bsq
    t_solve = time.time() - t2
    log(f"[build] solved in {t_solve:.1f}s")
    C = np.zeros((K + 1, N, 5), dtype=np.int64)
    for i in range(N):
        for c in range((K + 1) * 5):
            v = int(Xs[i, c])
            if v: C[c // 5, i, c % 5] = v
    del Xs
    # verify on the extra + holdout rows (all rows beyond N)
    bad = 0
    Mrest = eval_monomials_rows(inv[N:], monos, p)
    for r in range(N, npts):
        row = Mrest[r - N]
        for k in range(K + 1):
            for j in range(5):
                val = int((row * C[k, :, j] % p).sum() % p)
                if val != F.coeffs(rhs[r][k])[j]:
                    bad += 1
    log(f"[build] held-out check: {npts-N} rows x {(K+1)*5} components, mismatches={bad}")
    assert bad == 0, "held-out verification failed"
    support = int(np.count_nonzero(C.any(axis=2).any(axis=0)))
    meta = {"arm": arm, "m": m, "p": p, "N_monomials": N, "support_nonzero_monomials": support,
            "sample_points": npts, "holdout_rows": npts - N, "held_out_mismatches": bad,
            "seconds_eval": round(t_eval, 2), "seconds_solve": round(t_solve, 2), "deg_in_X": K,
            "pool_size": len(pool_list)}
    return ArmPolynomial(arm, m, monos, p, C, meta)

# ------------------------------------------------------------------ raw arm (grid)
def build_raw_polynomial_at_target(E, m, xR, nodes=None, log=print, evaluator="grp", pool=None, rng=None):
    """S_{m+1}(x_1..x_m, x_R) in x-monomials via tensor-product grid interpolation.
    Grid nodes: K+1 distinct F_p values per axis, taken from `pool` (so the product
    formula applies) -- the interpolated polynomial is the unique one of the box
    degree agreeing on the grid.  Returns numpy (K+1)^m x 5 array indexed by exponents."""
    F = E.F; p = F.p; K = 2 ** (m - 1)
    if nodes is None:
        nodes = sorted(rng.sample(sorted(pool), K + 1))
    nn = K + 1
    vals = np.zeros([nn] * m + [5], dtype=np.int64)
    t0 = time.time()
    cnt = 0
    for idx in itertools.product(range(nn), repeat=m):
        xs = [nodes[i] for i in idx]
        if len(set(xs)) < m:
            # coincident coordinates: use resultant evaluator (product formula degenerate)
            v = S_num_res(E, [F(x) for x in xs] + [xR])
        else:
            pts = [E.lift_x(F(x)) for x in xs]
            v = poly_eval(S_poly_grp(E, pts), xR)
        vals[idx] = F.coeffs(v)
        cnt += 1
    log(f"[raw] evaluated {cnt} grid points in {time.time()-t0:.1f}s")
    # inverse Vandermonde along each axis
    V = np.array([[pow(x, k, p) for k in range(nn)] for x in nodes], dtype=np.int64)
    Vinv = np.array(flint.nmod_mat(nn, nn, V.ravel().tolist(), p).inv().tolist(), dtype=object).astype(np.int64)
    # Vinv shape (k, node): coeff_k = sum_node Vinv[k,node] * val[node]
    C = vals
    for axis in range(m):
        C = np.moveaxis(C, axis, 0)
        shp = C.shape
        flat = C.reshape(nn, -1)
        new = np.zeros_like(flat)
        for k in range(nn):
            acc = np.zeros(flat.shape[1], dtype=np.int64)
            for nd in range(nn):
                if Vinv[k, nd]:
                    acc = (acc + flat[nd] * int(Vinv[k, nd])) % p
            new[k] = acc
        C = np.moveaxis(new.reshape(shp), 0, axis)
    return C, nodes

# ------------------------------------------------------------------ descent & msolve I/O
def descend_and_write(coeffs, monos, varnames, p, path, F=None):
    """coeffs: numpy (N_mono, 5) F_q coefficients; write msolve input with 5 F_p equations."""
    lines = [",".join(varnames), str(p)]
    eqs = []
    nterms = 0
    for j in range(5):
        terms = []
        for i, a in enumerate(monos):
            c = int(coeffs[i, j])
            if c == 0: continue
            mono = "*".join(f"{v}^{e}" if e > 1 else v for v, e in zip(varnames, a) if e > 0)
            terms.append(f"{c}*{mono}" if mono else f"{c}")
        if not terms:
            terms = ["0"]
        nterms += len(terms)
        eqs.append("+".join(terms))
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n" + ",\n".join(eqs) + "\n")
    return nterms

def descend_raw_and_write(C, varnames, p, path):
    nn = C.shape[0]; m = C.ndim - 1
    monos = list(itertools.product(range(nn), repeat=m))
    flat = C.reshape(-1, 5)
    return descend_and_write(flat, monos, varnames, p, path)

MSOLVE = "/usr/bin/msolve"

def run_msolve(inpath, outpath, timeout_s, mem_gb, threads=1, logpath=None, extra=("-P", "1")):
    """Run msolve under a hard wall-clock timeout and a hard address-space cap.

    The cap is set with setrlimit(RLIMIT_AS) in the child itself, so the kernel
    refuses the allocation instead of the host OOM-killer choosing a victim.
    msolve 0.6.5 does not check every malloc, so an allocation refused by the cap
    surfaces as SIGSEGV; the peak RSS of THIS child is therefore measured directly
    from /proc/<pid>/status (VmHWM), not from RUSAGE_CHILDREN, which is a maximum
    over all children ever reaped by this process and would silently attribute an
    earlier target's peak to this one.

    Returns the parsed log plus `outcome` in {ok, timeout, memory_exhausted, crashed}.
    `memory_exhausted` and `timeout` are resource_exhaustion for the caller;
    neither is ever evidence about the ideal degree.
    """
    import threading
    cmd = [MSOLVE, "-v", "2", "-t", str(threads), "-f", inpath, "-o", outpath] + list(extra)
    cap_bytes = int(mem_gb * (1 << 30))

    def _limit():
        resource.setrlimit(resource.RLIMIT_AS, (cap_bytes, cap_bytes))

    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, preexec_fn=_limit)
    peak = {"vmhwm_bytes": 0, "vmpeak_bytes": 0}

    def _watch(pid):
        path = f"/proc/{pid}/status"
        while True:
            try:
                with open(path) as fh:
                    for line in fh:
                        if line.startswith("VmHWM:"):
                            peak["vmhwm_bytes"] = max(peak["vmhwm_bytes"], int(line.split()[1]) * 1024)
                        elif line.startswith("VmPeak:"):
                            peak["vmpeak_bytes"] = max(peak["vmpeak_bytes"], int(line.split()[1]) * 1024)
            except (FileNotFoundError, ProcessLookupError, ValueError):
                return
            if proc.poll() is not None:
                return
            time.sleep(0.2)

    watcher = threading.Thread(target=_watch, args=(proc.pid,), daemon=True)
    watcher.start()
    timed_out = False
    try:
        out, err = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        timed_out = True
        proc.kill()
        out, err = proc.communicate()
    wall = time.time() - t0
    watcher.join(timeout=2)
    rc = proc.returncode
    if logpath:
        with open(logpath, "w") as fh:
            fh.write("# " + " ".join(cmd) + f"\n# RLIMIT_AS = {cap_bytes} bytes ({mem_gb} GB)\n"
                     + out + "\n#STDERR\n" + err)
    stats = parse_msolve_log(out + "\n" + err)
    # An allocation refused by RLIMIT_AS is memory exhaustion however the process dies.
    near_cap = peak["vmpeak_bytes"] >= 0.80 * cap_bytes or peak["vmhwm_bytes"] >= 0.60 * cap_bytes
    if timed_out:
        outcome = "timeout"
    elif rc == 0:
        outcome = "ok"
    elif rc in (-9, -11, -6, 137, 134, 139) and near_cap:
        outcome = "memory_exhausted"
    elif rc != 0:
        outcome = "crashed"
    else:
        outcome = "ok"
    stats.update({"returncode": rc, "timed_out": timed_out, "outcome": outcome,
                  "wall_seconds": round(wall, 3),
                  "peak_rss_bytes": peak["vmhwm_bytes"], "peak_vm_bytes": peak["vmpeak_bytes"],
                  "maxrss_children_bytes": peak["vmhwm_bytes"],
                  "mem_cap_bytes": cap_bytes,
                  "command": " ".join(cmd), "mem_cap_gb": mem_gb, "timeout_s": timeout_s,
                  "signal_note": ("msolve 0.6.5 does not check every allocation, so a request refused by "
                                  "RLIMIT_AS surfaces as a fatal signal; peak VM against the cap is recorded "
                                  "so the outcome can be told apart from a genuine crash."
                                  if outcome in ("memory_exhausted", "crashed") else None)})
    return stats

def parse_msolve_log(out):
    """Extract ideal degree, per-round F4 matrix statistics and FGLM statistics from
    msolve -v 2 output (stdout+stderr).  The F_p operation proxy for F4 is
    sum over rounds of rows * cols * density (an upper bound on the number of
    field multiply-accumulates in the dense-row reductions actually performed on
    those matrices); for FGLM it is 2 * D * nnz(multiplication matrix) for the
    sequence generation plus the reported sequence Gops.  Both are derived from
    msolve's own printed matrix dimensions -- measured shapes, modeled op count."""
    st = {"dimension_of_quotient": None, "f4_rounds": [], "fglm": {}, "no_solution": False,
          "timings": {}, "f4_summary": {}}
    m = re.search(r"Dimension of quotient:\s*(\d+)", out)
    if m: st["dimension_of_quotient"] = int(m.group(1))
    if "Grobner basis has a single element" in out or "No solution" in out:
        st["no_solution"] = True
    f4_ops = 0.0; f4_ops_red = 0.0; f4_rows = 0; f4_maxcols = 0
    for line in out.splitlines():
        mm = re.match(r"\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+) x (\d+)\s+([\d.]+)%\s+(\d+) new\s+(\d+) zero\s+([\d.]+) \| ([\d.]+)", line)
        if mm:
            deg, sel, pairs, rows, cols, dens, new, zero, treal, tcpu = mm.groups()
            rows, cols, dens = int(rows), int(cols), float(dens)
            ops = rows * cols * dens / 100.0
            k = int(new) + int(zero)                 # rows reduced this round
            piv = max(rows - k, 1)                   # pivot rows they are reduced against
            ops_red = k * piv * cols * dens / 100.0  # Gaussian-elimination estimate: each reduced row against each pivot row over the nonzero columns
            f4_ops += ops; f4_ops_red += ops_red; f4_rows += rows; f4_maxcols = max(f4_maxcols, cols)
            st["f4_rounds"].append({"deg": int(deg), "sel": int(sel), "pairs": int(pairs), "rows": rows, "cols": cols,
                                    "density_pct": dens, "new": int(new), "zero": int(zero), "sec_real": float(treal), "sec_cpu": float(tcpu),
                                    "ops_proxy_nnz": ops, "ops_proxy_reduction": ops_red})
    st["f4_summary"]["ops_proxy_rows_cols_density"] = f4_ops
    st["f4_summary"]["ops_proxy_reduction_total"] = f4_ops_red
    st["f4_summary"]["ops_proxy_note"] = ("both derived from msolve -v 2 matrix dimensions per F4 round: nnz = sum rows*cols*density (lower bound: every nonzero touched once); "
                                          "reduction = sum (rows reduced)*(pivot rows)*cols*density (dense Gaussian-elimination estimate). MEASURED shapes, MODELED op counts.")
    st["f4_summary"]["total_rows"] = f4_rows
    st["f4_summary"]["max_cols"] = f4_maxcols
    st["f4_summary"]["max_degree"] = max([r["deg"] for r in st["f4_rounds"]], default=None)
    for key, pat in {"max_matrix": r"max\. matrix data\s+(\d+) x (\d+) \(([\d.]+)%\)",
                     "rows_reduced": r"#rows reduced\s+(\d+)", "pairs_reduced": r"#pairs reduced\s+(\d+)",
                     "zero_reductions": r"#zero reductions\s+(\d+)",
                     "size_of_basis": r"size of basis\s+(\d+)", "terms_in_basis": r"#terms in basis\s+(\d+)"}.items():
        mm = re.search(pat, out)
        if mm:
            g = mm.groups()
            st["f4_summary"][key] = [float(x) if "." in x else int(x) for x in g] if len(g) > 1 else int(g[0])
    for key, pat in {"overall_cpu": r"overall\(cpu\)\s+([\d.]+) sec", "overall_elapsed": r"overall\(elapsed\)\s+([\d.]+) sec",
                     "linear_algebra_sec": r"linear algebra\s+([\d.]+) sec"}.items():
        mm = re.search(pat, out)
        if mm: st["timings"][key] = float(mm.group(1))
    mm = re.search(r"\[(\d+), (\d+)\], Non trivial / Trivial = ([\d.]+)%", out)
    if mm:
        st["fglm"] = {"dim": int(mm.group(1)), "nontrivial_cols": int(mm.group(2)), "nontrivial_pct": float(mm.group(3))}
        mm2 = re.search(r"Density of non-trivial part ([\d.]+)%", out)
        if mm2: st["fglm"]["density_pct"] = float(mm2.group(1))
        D = st["fglm"]["dim"]; nt = st["fglm"]["nontrivial_cols"]; dens = st["fglm"].get("density_pct", 100.0) / 100.0
        nnz = nt * D * dens + (D - nt)          # non-trivial columns dense-ish, trivial columns 1 entry
        st["fglm"]["nnz_multiplication_matrix_est"] = nnz
        st["fglm"]["ops_proxy_sequence"] = 2.0 * D * nnz
    mm = re.search(r"Time spent to generate sequence \(elapsed\): ([\d.]+) sec \(([\d.]+) Gops/sec\)", out)
    if mm:
        st["fglm"]["sequence_seconds"] = float(mm.group(1)); st["fglm"]["gops_per_sec_reported"] = float(mm.group(2))
        st["fglm"]["ops_from_reported_gops"] = float(mm.group(1)) * float(mm.group(2)) * 1e9
    mm = re.search(r"Degree of the square-free part:\s*(\d+)", out)
    if mm: st["fglm"]["squarefree_degree"] = int(mm.group(1))
    mm = re.search(r"Time for rational param:\s*([\d.]+) \(elapsed\) sec /\s*([\d.]+) sec \(cpu\)", out)
    if mm: st["timings"]["rational_param_elapsed"] = float(mm.group(1)); st["timings"]["rational_param_cpu"] = float(mm.group(2))
    return st

def parse_msolve_param(path, p):
    """Parse msolve rational parametrization output.  Returns None if no solutions
    ([-1]) or dict with elim poly, denominator, params, varnames."""
    txt = open(path).read().strip()
    if txt.endswith(":"): txt = txt[:-1]
    txt = txt.replace("\n", "")
    import ast
    data = ast.literal_eval(txt)
    if data == [-1] or data == -1:
        return None
    if data[0] != 0:
        return {"error": f"positive dimension or unexpected header {data[0]}"}
    body = data[1]
    char, nvars, deg, varnames, linform, param = body[0], body[1], body[2], body[3], body[4], body[5]
    nb = param[0]
    inner = param[1]
    elim, den, plist = inner[0], inner[1], inner[2]
    return {"char": char, "nvars": nvars, "degree": deg, "varnames": varnames, "linform": linform,
            "elim": elim, "den": den, "params": plist, "nb": nb}

def rational_solutions(par, p, nvars_orig=None):
    """All F_p-rational solutions from msolve's rational parametrization.
    Convention (verified empirically in the validation run on a planted m=3 system):
    for each F_p-root r of the eliminating polynomial w, x_i = -v_i(r) / (c_i * den(r)).
    If msolve did not add a linear form, the last original variable is the eliminating
    variable itself (params has nvars-1 entries) and equals r."""
    w = flint.nmod_poly(par["elim"][1], p)
    den = flint.nmod_poly(par["den"][1], p)
    roots = [int(r) for r, mult in w.roots()]
    nv = nvars_orig if nvars_orig is not None else par["nvars"]
    sols = []
    for r in roots:
        dn = int(den(r))
        if dn == 0:
            continue
        vals = []
        for entry in par["params"]:
            polyc = entry[0]; cst = int(entry[1]) if len(entry) > 1 else 1
            v = flint.nmod_poly(polyc[1], p)
            vals.append((-int(v(r)) * pow(cst * dn, -1, p)) % p)
        if len(vals) == nv - 1:
            vals.append(r % p)
        assert len(vals) == nv, (len(vals), nv)
        sols.append(vals)
    return sols, roots

# ------------------------------------------------------------------ D from leading ideal
def count_standard_monomials(lead_monos, nvars, cap=10**7):
    """Count monomials not divisible by any leading monomial (ideal degree) -- independent
    recount of msolve's 'Dimension of quotient' from its printed leading ideal."""
    leads = [tuple(l) for l in lead_monos]
    # bounding box: pure powers must exist for zero-dim ideal
    box = [None] * nvars
    for l in leads:
        nz = [i for i, e in enumerate(l) if e > 0]
        if len(nz) == 1:
            i = nz[0]
            if box[i] is None or l[i] < box[i]: box[i] = l[i]
    if any(b is None for b in box):
        return None
    count = 0
    for a in itertools.product(*[range(b) for b in box]):
        if not any(all(a[i] >= l[i] for i in range(nvars)) for l in leads):
            count += 1
        if count > cap: return None
    return count

def parse_leading_ideal(path, varnames):
    txt = open(path).read()
    body = txt.split("[", 1)[1].rsplit("]", 1)[0]
    monos = []
    for term in body.replace("\n", "").split(","):
        term = term.strip()
        if not term: continue
        e = [0] * len(varnames)
        if term != "1":
            for fac in term.split("*"):
                if "^" in fac:
                    v, k = fac.split("^"); e[varnames.index(v)] = int(k)
                else:
                    e[varnames.index(fac)] = 1
        monos.append(tuple(e))
    return monos
