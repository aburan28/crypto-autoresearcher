#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2-a1 -- PARI/gp parameter verification in a CAPPED CHILD.

Used by stage-1b development check A1-7 (c), by controls_a1 check (b) (A1-2 (b)), and by the FB-1 curve
search (A1-9; AA-3 (d)) if that branch is ever taken. /usr/bin/gp runs as a separate process under
v2_solver.run_child: RLIMIT_AS set IN THE CHILD and read back with getrlimit before exec (a child that
cannot set it refuses to start), one memory-heavy child at a time, no other solver process (AC-1; AA-6).

For each curve y^2 = x^3 + a2 x^2 + a4 x + a6 over F_q = F_p[w]/(M) it reports:
  N = ellcard(E) (PARI SEA / point counting over the finite field),
  N mod 4, the number of F_q-rational roots of x^3 + a2 x^2 + a4 x + a6 (rational 2-torsion points),
  for a declared cofactor h: whether h | N and isprime(N / h) (PARI isprime: a PROOF of primality),
  for a6 = 0: the NORM CRITERION class of b = a4: kronecker(N_{F_q/F_p}(b), p) (b is a square in F_q iff
  its norm is a square in F_p, for odd q).
The norm is ALSO recomputed here in pure Python, independently of PARI, as b^((q-1)/(p-1)) (which lies in
F_p), with v2_verify_independent.FqP arithmetic; the two must agree.
"""
import os
import sys

sys.dont_write_bytecode = True
import a1_common as AC                                   # noqa: E402

import v2_solver as V                                    # noqa: E402
import v2_verify_independent as VI                       # noqa: E402

GP = "/usr/bin/gp"
PARI_TIMEOUT_S = 7200      # builder m4 value of trial-plan-v2.json; PARI point counts are not solver cells


def _poly_w(cs):
    s = " + ".join("%d*w^%d" % (int(c), i) for i, c in enumerate(cs) if int(c))
    return s or "0"


def gp_script(p, modulus, curves):
    """curves: list of dicts {label, a2, a4, a6, cofactor}. Returns the gp program text."""
    lines = ["default(parisize, 256000000);", "default(parisizemax, 4000000000);",
             "M = Mod(1, %d) * (%s);" % (p, _poly_w(modulus)),
             "g = ffgen(M, 'w);"]
    for c in curves:
        L = c["label"]
        lines += [
            "a2 = subst(%s, 'w, g); a4 = subst(%s, 'w, g); a6 = subst(%s, 'w, g);" % (_poly_w(c["a2"]), _poly_w(c["a4"]), _poly_w(c["a6"])),
            "E = ellinit([0, a2, 0, a4, a6]);",
            "N = ellcard(E);",
            "f = 'x^3 + a2*'x^2 + a4*'x + a6; fa = factor(f); r = 0; for(i = 1, #fa[,1], if(poldegree(fa[i,1]) == 1, r += fa[i,2]));",
            "h = %d; hd = (N %% h == 0); q = if(hd, N / h, 0); qp = if(hd, isprime(q), 0);" % int(c.get("cofactor") or 1),
            "nb = if(a6 == 0, lift(norm(Mod(Mod(1, %d) * (%s), M))), -1); kb = if(nb >= 0, kronecker(nb, %d), 0);" % (p, _poly_w(c["a4"]), p),
            'print("A1PARI ", "%s", " N=", N, " N_mod_4=", N %% 4, " rational_2torsion_roots=", r, " cofactor_divides=", hd, " N_over_h_isprime=", qp, " norm_b=", nb, " kronecker_norm_b=", kb);' % L,
        ]
    lines.append("quit;")
    return "\n".join(lines) + "\n"


def _parse(stdout_text):
    out = {}
    for line in stdout_text.splitlines():
        if not line.startswith("A1PARI "):
            continue
        toks = line.split()
        lab = toks[1]
        rec = {}
        for t in toks[2:]:
            k, v = t.split("=", 1)
            rec[k] = int(v)
        out[lab] = rec
    return out


def norm_pure_python(p, modulus, b):
    """N_{F_q/F_p}(b) = b^((q-1)/(p-1)) by v2_verify_independent.FqP (pure Python, no PARI, no flint)."""
    F = VI.FqP(p, modulus)
    n = F.n
    e = (p ** n - 1) // (p - 1)
    v = F.pow(F.norm(b), e)
    if not F.in_Fp(v):
        raise ArithmeticError("norm not in F_p")
    return v[0]


def legendre(a, p):
    a %= p
    return 0 if a == 0 else (1 if pow(a, (p - 1) // 2, p) == 1 else -1)


def curve_facts(p, modulus, curves, out_dir, tag, cap=AC.CAP_BYTES, timeout_s=PARI_TIMEOUT_S):
    """Run the gp program in a capped child. Returns a record with per-curve facts, the child record
    (including the getrlimit read-back) and the pure-Python norm cross-check."""
    os.makedirs(out_dir, exist_ok=True)
    gpf = os.path.join(out_dir, tag + ".gp")
    with open(gpf, "w") as fh:
        fh.write(gp_script(p, modulus, curves))
    argv = [GP, "-q", "-f", "--default", "nbthreads=1", gpf]
    so, se = os.path.join(out_dir, tag + ".gp.stdout"), os.path.join(out_dir, tag + ".gp.stderr")
    rec = V.run_child(argv, so, se, cap_bytes=cap, timeout_s=timeout_s, count_instructions=False)
    res = {"tag": tag, "p": p, "modulus": list(modulus), "script": gpf, "script_sha256": AC.sha256_file(gpf), "command": " ".join(argv),
           "child": {k: rec.get(k) for k in ("outcome", "returncode", "timed_out", "wall_seconds", "rlimit_as_child_getrlimit",
                                              "rlimit_as_proc_limits_after_exec", "peak_rss_bytes", "peak_vm_bytes", "refusal_reason")}}
    try:
        txt = open(so, errors="replace").read()
    except OSError:
        txt = ""
    facts = _parse(txt)
    res["curves"] = {}
    for c in curves:
        f = dict(facts.get(c["label"], {}))
        if c.get("a6") is not None and all(int(x) == 0 for x in c["a6"]) and f:
            nb_py = norm_pure_python(p, modulus, c["a4"])
            f["norm_b_pure_python"] = nb_py
            f["norm_b_agrees_pari_vs_pure_python"] = (nb_py == f.get("norm_b"))
            f["b_is_square_in_Fq_by_norm_criterion"] = legendre(nb_py, p) == 1
        res["curves"][c["label"]] = f
    res["complete"] = rec.get("outcome") == "ok" and all(c["label"] in facts for c in curves)
    return res


def gp_version():
    try:
        import subprocess
        return subprocess.run([GP, "--version-short"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:                               # noqa: BLE001
        return "ERROR %r" % (e,)


def fb1_curve_search(out_dir, cap=AC.CAP_BYTES, c_max=5000, log_path=None):
    """A1-9 / AA-3 (d): smallest c >= 1 with y^2 = x(x^2 + 2x + c z) over F_16777291[z]/(z^5 - 2) of order N = 2q,
    q proved prime by PARI isprime, and b = c z a non-square by the norm criterion. Every c tried is logged.
    Only executed if FB-1 fires; it did not fire in stage 1b (see implementation-v2-a1.md)."""
    p = AC.P_FB1
    modulus = [(-2) % p, 0, 0, 0, 0, 1]
    tried, chosen = [], None
    for c in range(1, c_max + 1):
        cv = {"label": "c%d" % c, "a2": [2], "a4": [0, c], "a6": [0], "cofactor": 2}
        r = curve_facts(p, modulus, [cv], out_dir, "fb1_c%d" % c, cap=cap)
        f = r["curves"].get(cv["label"], {})
        ok = (r["complete"] and f.get("cofactor_divides") == 1 and f.get("N_over_h_isprime") == 1
              and f.get("b_is_square_in_Fq_by_norm_criterion") is False and f.get("norm_b_agrees_pari_vs_pure_python") is True)
        tried.append({"c": c, "facts": f, "child_outcome": r["child"]["outcome"], "qualifies": ok})
        if ok:
            chosen = c
            break
    return {"tried": tried, "chosen_c": chosen, "c_max": c_max}


if __name__ == "__main__":
    print(gp_version())
    sys.exit(0)
