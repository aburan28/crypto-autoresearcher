#!/usr/bin/env python3
"""Validator spot-checks of the EXP-ECDLP-f49f75 launcher (pre-fix b9ddeef vs HEAD).

1. Capture the Singular scripts the launcher would emit (run_singular monkeypatched),
   for pre-fix and post-fix launcher versions, and compare the summation polynomial S
   as Singular evaluates it (prints S, greps for int-overflow warnings).
2. Independent fibre check: own EC arithmetic + own Velu chain from (R, K) given by
   build_chain, brute-force F_p fibre of the chain x-map over c, compare with V.
3. Elimination check: eliminate w-variables from arm A's per-point chain ideal and
   compare with arm B's dense polynomial (same instance).
4. Second-pass cost: time std(I) / slimgb(I) and the extra G = std(G) separately.
Usage: python3 -I launcher_checks.py <dir-with-launcher_prefix.py-and-launcher_head.py> <check...>
"""
import importlib.util, json, re, subprocess, sys, tempfile, os, hashlib, time

base = sys.argv[1]
checks = sys.argv[2:] or ["overflow", "fibre", "elim", "secondstd"]


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(base, f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pre, post = load("launcher_prefix"), load("launcher_head")
SEED = "EXP-ECDLP-f49f75/v1"


def seed_of(m, L, inst):
    return int(hashlib.sha256(f"{SEED}|{m}|{L}|{inst}".encode()).hexdigest()[:12], 16)


def capture(mod, m, L, inst, arms, solvers=("std",)):
    got = []
    orig = mod.run_singular
    mod.run_singular = lambda script, timeout: (got.append(script), {"status": "captured"})[1]
    try:
        kind = "planted" if inst < 4 else "random"
        out = mod.run_instance(dict(m=m, L=L, inst=inst, kind=kind, seed=seed_of(m, L, inst), timeout=600,
                                    arms=list(arms), solvers=list(solvers)))
    finally:
        mod.run_singular = orig
    return out, got


def singular(src):
    with tempfile.NamedTemporaryFile("w", suffix=".sing", delete=False) as f:
        f.write(src)
        path = f.name
    r = subprocess.run(["Singular", "-q", "--no-rc", path], capture_output=True, text=True, timeout=900)
    os.unlink(path)
    return r.stdout + r.stderr


def s_part(script):
    lines = script.splitlines()
    keep = [l for l in lines if l.startswith("ring r0") or l.startswith("poly S = ") and "imap" not in l]
    return "\n".join(keep) + "\nprint(S);\nquit;\n"


if "overflow" in checks:
    print("== overflow / fix-invariance of S (arm B std script)")
    for (m, L, inst) in [(2, 7, 0), (2, 8, 0), (2, 8, 1), (2, 9, 0), (2, 11, 2), (3, 3, 0), (3, 4, 0), (3, 5, 0), (3, 5, 4)]:
        o1, s1 = capture(pre, m, L, inst, ["B"])
        o2, s2 = capture(post, m, L, inst, ["B"])
        assert (o1["p"], o1["b"], o1["chain_c"]) == (o2["p"], o2["b"], o2["chain_c"])
        r1, r2 = singular(s_part(s1[0])), singular(s_part(s2[0]))
        xT = re.search(r"number\((\d+)\)\)\^2|\*number\((\d+)\)\^2", s2[0])
        print(f" m={m} L={L} inst={inst} p={o1['p']} S_prefix==S_fixed: {r1.strip() == r2.strip()}"
              f"  overflow-warning prefix:{'overflow' in r1.lower()} fixed:{'overflow' in r2.lower()}")

if "fibre" in checks:
    print("\n== independent fibre check: brute-force F_p fibre of chain x-map over c == x(R+<K>)")

    def add(P, Q, A, p):
        if P is None: return Q
        if Q is None: return P
        if P[0] == Q[0] and (P[1] + Q[1]) % p == 0: return None
        if P == Q:
            l = (3 * P[0] * P[0] + A) * pow(2 * P[1], p - 2, p) % p
        else:
            l = (Q[1] - P[1]) * pow(Q[0] - P[0], p - 2, p) % p
        x = (l * l - P[0] - Q[0]) % p
        return (x, (l * (P[0] - x) - P[1]) % p)

    def mul(k, P, A, p):
        R = None
        for bit in bin(k)[2:]:
            R = add(R, R, A, p)
            if bit == "1": R = add(R, P, A, p)
        return R

    for (m, L) in [(2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (3, 3), (3, 4), (3, 5)]:
        import random
        for inst in (0, 5):
            rng = random.Random(seed_of(m, L, inst))
            p = post.find_prime(m, L)
            a = p - 3
            while True:
                b = rng.randrange(1, p)
                if (4 * a ** 3 + 27 * b * b) % p: break
            ch = post.build_chain(p, L, rng)
            R, K = ch["R"], ch["K"]
            assert (R[1] ** 2 - R[0] ** 3 - R[0]) % p == 0
            assert K == mul((p + 1) // 2 ** L, R, 1, p)
            # own Velu chain from K
            def phi(P, x0, t):
                if P is None or P[0] == x0:
                    return None
                d = pow(P[0] - x0, p - 2, p)
                return ((P[0] + t * d) % p, P[1] * (1 - t * d * d) % p)

            A_, B_, Kc, steps = 1, 0, K, []
            for i in range(L):
                T2 = mul(2 ** (L - 1 - i), Kc, A_, p)
                assert T2 is not None and T2[1] == 0 and (T2[0] ** 3 + A_ * T2[0] + B_) % p == 0
                x0 = T2[0]; t = (3 * x0 * x0 + A_) % p
                steps.append((x0, t))
                A_, B_ = (A_ - 5 * t) % p, (B_ - 7 * x0 * t) % p
                Kc = phi(Kc, x0, t)
                assert Kc is None or (Kc[1] ** 2 - Kc[0] ** 3 - A_ * Kc[0] - B_) % p == 0
            assert Kc is None, "kernel not exhausted"
            same_steps = steps == [tuple(s) for s in ch["steps"]]
            # c = image of R
            img = R
            for (u0, tt) in steps:
                d = pow(img[0] - u0, p - 2, p)
                img = ((img[0] + tt * d) % p, img[1] * (1 - tt * d * d) % p)
            c = img[0]
            V = set()
            P = R
            for _ in range(2 ** L):
                V.add(P[0]); P = add(P, K, 1, p)
            # brute-force fibre over F_p
            fib = []
            if p < 2 ** 17:
                for x in range(p):
                    y = x
                    ok = True
                    for (u0, tt) in steps:
                        if y == u0: ok = False; break
                        y = (y + tt * pow(y - u0, p - 2, p)) % p
                    if ok and y == c: fib.append(x)
            print(f" m={m} L={L} inst={inst} p={p} steps==launcher:{same_steps} c==launcher:{c == ch['c']} "
                  f"|V|={len(V)} V==launcher:{sorted(V) == ch['V']} "
                  + (f"F_p-fibre==V:{set(fib) == V} (|fibre|={len(fib)})" if fib else "fibre brute force skipped (p>=2^17)"))

if "elim" in checks:
    print("\n== elimination: arm A per-point chain ideal, w's eliminated, vs arm B dense poly")
    for (m, L, inst) in [(2, 5, 0), (2, 7, 3), (3, 4, 1)]:
        _, sa = capture(post, m, L, inst, ["A"])
        _, sb = capture(post, m, L, inst, ["B"])
        ia = re.search(r"ideal I = (.*);", sa[0]).group(1).split(",")
        ib = re.search(r"ideal I = (.*);", sb[0]).group(1).split(",")
        chain1 = [e for e in ia if "x(1)" in e or "w(1)" in e][: L]
        chain1 = [e for e in ia[1:] if re.search(r"\b(x|w)\(1\)", e)]
        dense1 = [e for e in ib[1:] if "x(1)" in e][0]
        p = re.search(r"ring r0 = (\d+)", sa[0]).group(1)
        wv = ",".join(f"w(1)({j})" for j in range(1, L))
        prodw = "*".join(f"w(1)({j})" for j in range(1, L))
        src = (f"ring q = {p},(x(1),{wv}),dp;\nideal J = {','.join(chain1)};\n"
               f"ideal E = eliminate(J,{prodw});\npoly D = {dense1};\n"
               f"ideal Es = std(E); ideal Ds = std(ideal(D));\n"
               f'print("ELIM size " + string(size(Es)) + " deg " + string(deg(Es[1])) + " equal " + string(size(reduce(Ds,Es))==0 && size(reduce(Es,Ds))==0));\nquit;\n')
        out = singular(src)
        print(f" m={m} L={L} inst={inst} p={p} n_chain_eqs_for_point1={len(chain1)} -> {out.strip()}")

if "secondstd" in checks:
    print("\n== cost of the extra G = std(G) pass inside the timed region (ms, rtimer)")
    for (m, L, inst) in [(2, 6, 0), (2, 7, 0), (3, 3, 0)]:
        for arm in ("A", "B"):
            for solver in ("std", "slimgb"):
                _, s = capture(post, m, L, inst, [arm], solvers=[solver])
                src = s[0]
                src = src.replace(f"ideal G = {solver}(I);\nG = std(G);\nint tstd = rtimer - t0;",
                                  f"ideal G = {solver}(I);\nint tfirst = rtimer - t0; int t2 = rtimer;\nG = std(G);\nint tsecond = rtimer - t2;\nint tstd = rtimer - t0;\n"
                                  'print("SPLIT " + string(tfirst) + " " + string(tsecond));')
                assert "SPLIT" in src
                out = singular(src)
                sp = re.search(r"SPLIT (\d+) (\d+)", out)
                pl = re.search(r"PLANTED (\d)", out)
                print(f" m={m} L={L} inst={inst} arm={arm} {solver:6s} first={sp.group(1)} second_std={sp.group(2)} planted={pl.group(1) if pl else None}")
