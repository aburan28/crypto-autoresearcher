#!/usr/bin/env python3
"""EXP-ECDLP-f49f75 launcher: does a 2-isogeny-chain factor base (the
Petit-Kosters-Messeng auxiliary-isogeny construction proposed for P-256) make
Semaev m-decomposition cheaper than the same factor base encoded densely, a
random factor base of the same size, or plain enumeration?

Toy scale only. For each (m, L):
  * p: smallest prime > 2^(m*L) with p = 3 mod 4 and 2^L | p+1 (P-256 has 2^96 | p+1).
  * E0: y^2 = x^3 + x over F_p (supersingular, #E0 = p+1, cyclic 2-part).
  * R in E0 with full 2-part, K = [(p+1)/2^L] R of order 2^L, Phi = chain of L
    Velu 2-isogenies with kernel <K>.  V = Phi_x^{-1}(x(Phi(R))) = x(R + <K>), |V| = 2^L.
  * Target curve E: y^2 = x^3 - 3x + b (P-256 shape), b from the seed.
    Factor base FB = points of E(F_p) with x in V.
Arms (same solver, Singular std(dp) + fglm(lp), same targets where defined):
  A  chain   - V encoded by L chained quadratic Velu equations per point (PKM).
  B  dense   - the SAME V encoded by its degree-2^L minimal polynomial.
  C  random  - a uniformly random set of size 2^L, dense encoding (no structure).
  E  enum    - meet-in-the-middle enumeration over FB (generic baseline), group ops.
Targets: planted (T = sum of m FB points, a decomposition exists) and random.
Every planted decomposition is checked against the Groebner variety; every
enumeration decomposition is checked by recomputing the sum on E.
"""
import argparse, hashlib, json, os, platform, random, subprocess, sys, tempfile, time
from concurrent.futures import ProcessPoolExecutor, as_completed

from sympy import isprime

# ---------------------------------------------------------------- field / curves

def sqrt_mod(a, p):
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p + 1) // 4, p)
    return r if r * r % p == a else None


def ec_add(P, Q, A, p):
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def ec_mul(k, P, A, p):
    R = None
    while k:
        if k & 1:
            R = ec_add(R, P, A, p)
        P = ec_add(P, P, A, p)
        k >>= 1
    return R


def ec_neg(P, p):
    return None if P is None else (P[0], (-P[1]) % p)


def find_prime(m, L):
    bits = m * L
    k = (2 ** bits) // (2 ** L) + 1
    while True:
        p = k * 2 ** L - 1
        if p % 4 == 3 and p > 2 ** bits and isprime(p):
            return p
        k += 1


def build_chain(p, L, rng):
    """Velu 2-isogeny chain on E0: y^2=x^3+x with kernel <K>, |K| = 2^L."""
    A, B = 1, 0
    while True:
        x = rng.randrange(1, p)
        y = sqrt_mod(x ** 3 + x, p)
        if y is None:
            continue
        R = (x, y)
        if ec_mul((p + 1) // 2, R, A, p) is None:  # need full 2-part (2-part is cyclic)
            continue
        # need 2R outside <K>, else x(R + jK) repeats (-(R+jK) in R + <K>)
        if ec_mul(2 ** (L + 1), R, A, p) is not None:
            break
    K = ec_mul((p + 1) // 2 ** L, R, A, p)
    assert ec_mul(2 ** (L - 1), K, A, p) is not None and ec_mul(2 ** L, K, A, p) is None
    steps = []
    Kc, Rc = K, R
    for i in range(L):
        k2 = ec_mul(2 ** (L - 1 - i), Kc, A, p)
        x0 = k2[0]
        assert k2[1] == 0
        t = (3 * x0 * x0 + A) % p
        w = x0 * t % p
        steps.append((x0, t))

        def phi(P, x0=x0, t=t):
            if P is None or P[0] == x0:
                return None
            d = pow(P[0] - x0, -1, p)
            return ((P[0] + t * d) % p, P[1] * (1 - t * d * d) % p)

        A, B = (A - 5 * t) % p, (B - 7 * w) % p
        Kc, Rc = phi(Kc), phi(Rc)
        for P in (Kc, Rc):  # curve-equation check on every step
            assert P is None or (P[1] ** 2 - P[0] ** 3 - A * P[0] - B) % p == 0
    assert Kc is None
    c = Rc[0]
    # fibre = x(R + jK), j < 2^L ; check every element maps to c through the chain
    V, P = [], R
    for j in range(2 ** L):
        V.append(P[0])
        P = ec_add(P, K, 1, p)
    assert len(set(V)) == 2 ** L
    for v in V:
        assert chain_eval(v, steps, p) == c
    return dict(steps=steps, c=c, V=sorted(V), R=R, K=K)


def chain_eval(x, steps, p, trace=False):
    out = [x]
    for x0, t in steps:
        x = (x + t * pow(x - x0, -1, p)) % p
        out.append(x)
    return out if trace else x


def factor_base(Vset, a, b, p):
    fb = []
    for x in Vset:
        y = sqrt_mod(x ** 3 + a * x + b, p)
        if y is not None:
            fb.append((x, y))
    return fb


# ---------------------------------------------------------------- Singular systems

def poly_from_roots(roots, p):
    c = [1]
    for r in roots:
        n = [0] * (len(c) + 1)
        for i, ci in enumerate(c):
            n[i] = (n[i] - r * ci) % p
            n[i + 1] = (n[i + 1] + ci) % p
        c = n
    return c  # c[i] = coeff of x^i


def dense_str(coeffs, var):
    return "+".join(f"{ci}*{var}^{i}" for i, ci in enumerate(coeffs) if ci)


S3 = ("({x1}-{x2})^2*{x3}^2-2*(({x1}+{x2})*({x1}*{x2}+({a}))+2*({b}))*{x3}"
      "+({x1}*{x2}-({a}))^2-4*({b})*({x1}+{x2})")


def singular_script(arm, p, m, a, b, xT, enc, planted_pt, solver="std"):
    xs = [f"x({i})" for i in range(1, m + 1)]
    lines = ["option(redSB);", 'system("--ticks-per-sec",1000);']
    # summation polynomial in a small ring, imapped into the system ring
    lines.append(f"ring r0 = {p},(x(1..{m}),X),dp;")
    if m == 2:
        lines.append("poly S = " + S3.format(x1="x(1)", x2="x(2)", x3=str(xT), a=a, b=b) + ";")
    else:
        lines.append("poly S = resultant(" + S3.format(x1="x(1)", x2="x(2)", x3="X", a=a, b=b)
                     + "," + S3.format(x1="x(3)", x2=str(xT), x3="X", a=a, b=b) + ",X);")
    L = len(enc["steps"]) if arm == "A" else 0
    if arm == "A":
        ring_vars = f"x(1..{m})" + (f",w(1..{m})(1..{L-1})" if L > 1 else "")
    else:
        ring_vars = f"x(1..{m})"
    lines.append(f"ring r = {p},({ring_vars}),dp;")
    lines.append("poly S = imap(r0,S);")
    eqs = ["S"]
    for i in range(1, m + 1):
        if arm == "A":
            chain = [f"x({i})"] + [f"w({i})({j})" for j in range(1, L)] + [str(enc["c"])]
            for j, (x0, t) in enumerate(enc["steps"]):
                u, v = chain[j], chain[j + 1]
                eqs.append(f"{v}*({u}-{x0})-{u}*({u}-{x0})-{t}")
        else:
            eqs.append(dense_str(enc["coeffs"], f"x({i})"))
    lines.append("ideal I = " + ",".join(eqs) + ";")
    lines += [
        "int t0 = rtimer;",
        f"ideal G = {solver}(I);", "G = std(G);",
        "int tstd = rtimer - t0;",
        "int dg = 0; int k; for (k=1;k<=size(G);k++){ if (deg(G[k])>dg) {dg=deg(G[k]);} }",
        'print("STD " + string(tstd) + " " + string(vdim(G)) + " " + string(size(G)) + " " + string(dg));',
    ]
    if planted_pt is not None:
        subs = ",".join(f"{name},{val}" for name, val in planted_pt)
        lines.append(f"ideal Z = subst(G,{subs});")
        lines.append('print("PLANTED " + string(size(Z)==0));')
    lines += [
        "if (vdim(G) >= 0) {",
        f"ring s = {p},({ring_vars}),lp;",
        "int t1 = rtimer; ideal F = fglm(r,G); int tf = rtimer - t1;",
        'print("FGLM " + string(tf));',
        "}",
        'print("MEM " + string(memory(2)));',
        "quit;",
    ]
    return "\n".join(lines) + "\n"


def run_singular(script, timeout):
    with tempfile.NamedTemporaryFile("w", suffix=".sing", delete=False) as f:
        f.write(script)
        path = f.name
    t0 = time.monotonic()
    try:
        out = subprocess.run(["Singular", "-q", "--no-rc", path], capture_output=True,
                             text=True, timeout=timeout)
        stdout, status = out.stdout, ("ok" if out.returncode == 0 else f"rc{out.returncode}")
    except subprocess.TimeoutExpired as e:
        stdout, status = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "timeout"
    wall = time.monotonic() - t0
    os.unlink(path)
    res = dict(status=status, wall_s=round(wall, 4))
    for line in stdout.splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "STD":
            res.update(std_ms=int(parts[1]), vdim=int(parts[2]), gb_size=int(parts[3]), gb_maxdeg=int(parts[4]))
        elif parts[0] == "PLANTED":
            res["planted_in_variety"] = parts[1] == "1"
        elif parts[0] == "FGLM":
            res["fglm_ms"] = int(parts[1])
        elif parts[0] == "MEM":
            res["mem_bytes"] = int(parts[1])
    if status == "ok" and "fglm_ms" not in res:
        res["status"] = "incomplete"
        res["stdout_tail"] = stdout[-400:]
    return res


# ---------------------------------------------------------------- enumeration baseline

def enumerate_decomp(T, fb, m, a, p):
    """Meet-in-the-middle over +-FB; returns (#group ops, #decompositions)."""
    pts = fb + [ec_neg(P, p) for P in fb if P[1] != 0]
    ops, found = 0, set()
    fbx = {P[0] for P in fb}
    if m == 2:
        for P1 in pts:
            Q = ec_add(T, ec_neg(P1, p), a, p); ops += 1
            if Q is not None and Q[0] in fbx:
                found.add(tuple(sorted((P1[0], Q[0]))))
    else:
        table = {}
        for P1 in pts:
            Q = ec_add(T, ec_neg(P1, p), a, p); ops += 1
            if Q is not None:
                table.setdefault(Q, []).append(P1)
        for i, P2 in enumerate(pts):
            for P3 in pts[i:]:
                S = ec_add(P2, P3, a, p); ops += 1
                for P1 in table.get(S, ()):
                    assert ec_add(ec_add(P1, P2, a, p), P3, a, p) == T
                    found.add(tuple(sorted((P1[0], P2[0], P3[0]))))
    return ops, len(found)


# ---------------------------------------------------------------- one cell

def run_instance(job):
    m, L, inst, kind, seed, timeout, arms = (job[k] for k in
                                            ("m", "L", "inst", "kind", "seed", "timeout", "arms"))
    rng = random.Random(seed)
    p = find_prime(m, L)
    a = p - 3
    while True:
        b = rng.randrange(1, p)
        if (4 * a ** 3 + 27 * b * b) % p:
            break
    chain = build_chain(p, L, rng)
    randV = sorted(rng.sample(range(p), 2 ** L))
    out = dict(job, p=p, p_bits=p.bit_length(), b=b, chain_c=chain["c"], results={})
    for arm in arms:
        Vset = randV if arm == "C" else chain["V"]
        fb = factor_base(Vset, a, b, p)
        trng = random.Random(f"{seed}-{arm in 'C'}-target")
        if kind == "planted":
            picks = [trng.choice(fb) for _ in range(m)]
            picks = [P if trng.random() < .5 else ec_neg(P, p) for P in picks]
            T = None
            for P in picks:
                T = ec_add(T, P, a, p)
            if T is None:
                out["results"][arm] = dict(status="degenerate_target")
                continue
        else:
            while True:
                x = trng.randrange(p)
                y = sqrt_mod(x ** 3 + a * x + b, p)
                if y is not None:
                    T, picks = (x, y), None
                    break
        if arm == "E":
            t0 = time.monotonic()
            ops, nfound = enumerate_decomp(T, fb, m, a, p)
            out["results"][arm] = dict(status="ok", group_ops=ops, decompositions=nfound,
                                       wall_s=round(time.monotonic() - t0, 4), fb_size=len(fb))
            continue
        planted_pt = None
        if picks is not None:
            planted_pt = []
            for i, P in enumerate(picks, 1):
                planted_pt.append((f"x({i})", P[0]))
                if arm == "A":
                    tr = chain_eval(P[0], chain["steps"], p, trace=True)
                    planted_pt += [(f"w({i})({j})", tr[j]) for j in range(1, L)]
        enc = chain if arm == "A" else dict(coeffs=poly_from_roots(Vset, p))
        for solver in job["solvers"]:
            res = run_singular(singular_script(arm, p, m, a, b, T[0], enc, planted_pt, solver), timeout)
            res["fb_size"] = len(fb)
            out["results"][arm if solver == "std" else f"{arm}:{solver}"] = res
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()
    plan = json.load(open(args.plan))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    t0 = time.time()
    n = 0
    with open(args.out, "w") as fh, ProcessPoolExecutor(args.workers) as ex:
        for m, Ls in sorted(plan["L_by_m"].items()):
            m = int(m)
            arms = list(plan["arms"])
            for L in Ls:
                if not [x for x in arms if x != "E"]:
                    break
                jobs = []
                for inst in range(plan["planted_per_cell"] + plan["random_per_cell"]):
                    kind = "planted" if inst < plan["planted_per_cell"] else "random"
                    seed = int(hashlib.sha256(f"{plan['seed']}|{m}|{L}|{inst}".encode()).hexdigest()[:12], 16)
                    jobs.append(dict(m=m, L=L, inst=inst, kind=kind, seed=seed, timeout=plan["timeout_s"],
                                     arms=arms, solvers=plan["solvers"]))
                rows = [f.result() for f in as_completed([ex.submit(run_instance, j) for j in jobs])]
                for r in sorted(rows, key=lambda r: r["inst"]):
                    fh.write(json.dumps(r) + "\n")
                    print(f"m={m} L={L} inst={r['inst']} " + " ".join(
                        f"{k}:{v.get('status')}/{v.get('std_ms', v.get('group_ops'))}" for k, v in r["results"].items()), flush=True)
                fh.flush(); n += len(rows)
                # stopping rule (frozen in specification): an arm whose every solver timed
                # out on every instance of a cell is not run at larger L for this m.
                for arm in [x for x in arms if x != "E"]:
                    keys = [k for k in rows[0]["results"] if k.split(":")[0] == arm]
                    if all(r["results"][k]["status"] == "timeout" for r in rows for k in keys):
                        arms.remove(arm)
                        print(f"stop: arm {arm} retired at m={m} L={L}", flush=True)
    print(json.dumps(dict(jobs=n, elapsed_s=round(time.time() - t0, 1), python=platform.python_version())))


if __name__ == "__main__":
    main()
