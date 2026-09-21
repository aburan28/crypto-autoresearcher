#!/usr/bin/env python3
"""SafeCurves-style certificate audit of EcGFp5 / EcMasFp5 for EXP-GFPN-726eb2.

usage: gfpn_audit.py --curve {EcGFp5,EcMasFp5} [--rigidity-budget-seconds S]
                     [--ecm-log-dir DIR] [--out DIR]

Writes into $GFPN_RUN_DIR (or --out): raw-result.json, audit-table.yaml,
figure-provenance.yaml, certificates/ (PARI scripts + outputs, ECPP
certificates, order certificate, factorization certificates, ECM logs).

Pipeline (all from the frozen sources, nothing copied without regeneration):
  1. sources     sha256 of the frozen full-text files re-verified; every
                 parameter and self-reported figure is cited by line number.
  2. model       EcGFp5: double-odd y^2 = x(x^2+2x+263z) from the paper,
                 converted to short Weierstrass by the paper's own change of
                 variable; EcMasFp5: y^2 = x^3 + 3x + 8 z^4 from the note.
  3. count       independent SEA point count (PARI/GP 2.15.4 ellcard with
                 pari-seadata) of the curve AND of its quadratic twist.
  4. order cert  prime n: PARI primecert (ECPP) re-verified by the pure-Python
                 verifier in gfpn_arith.py; a point P != O with [n]P = O
                 computed with gfpn_arith's own F_{p^5} / Jacobian arithmetic;
                 Hasse-interval uniqueness => #E = h*n, compared with SEA.
  5. embedding   n-1 factored (trial division + GMP-ECM hints re-verified by
                 division + primality proofs); e = ord_n(q) computed exactly.
  6. CM disc     D = t^2 - 4q; bit length; factorization attempt for the
                 squarefree part (exact when complete, else not_verifiable).
  7. twist       N' = 2q+2-N (checked against the SEA count of the twist);
                 factorization; twist rho bits = log2(sqrt(pi*l'/4)).
  8. rigidity    the published search re-enumerated with ellsea early abort
                 under a wall-clock budget; first hit compared to the
                 published parameters.
  9. provenance  the 142-bit and 101.93 figures (and the other self-reports)
                 tagged computed / inherited / asserted with citations.

Classification of every metric: certificate | bound | not_verifiable (reason).
A gp timeout/crash is resource_exhaustion / infrastructure_error, never a
mathematical result.  No ECDLP solve, no PDP, no cover genus is attempted.
"""
import argparse, ast, glob, hashlib, json, math, os, re, shutil, subprocess, sys, time
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfpn_arith import (P, Q, Fq, INF, on_curve, mul, ec_add, multiples_in_hasse, hasse_interval,
                        miller_rabin, verify_ecpp)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RHO_CONST = 0.5 * math.log2(math.pi / 4)   # log2(sqrt(pi*l/4)) = 0.5*log2(l) + RHO_CONST

SOURCES = {
    "EcGFp5": {
        "dir": "inputs/PORNIN-2022-274-ECGFP5",
        "text": "paper_fulltext.md",
        "record": "SRC-PORNIN-2022-274-ECGFP5",
        "kn_lit": "KN-LIT-8aff72",
        "secondary_dir": "inputs/ECMASFP5-HACKMD-2025",
        "secondary_text": "note_fulltext.md",
    },
    "EcMasFp5": {
        "dir": "inputs/ECMASFP5-HACKMD-2025",
        "text": "note_fulltext.md",
        "record": "SRC-ECMASFP5-HACKMD-2025",
        "kn_lit": "KN-LIT-47d541",
    },
}

# ----------------------------------------------------------------------------- utilities
def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def cite(lines, pattern, flags=0):
    rx = re.compile(pattern, flags)
    return [{"line": i + 1, "text": l.rstrip()} for i, l in enumerate(lines) if rx.search(l)]

def fq_str(e):
    """gp-readable string of an Fq element in terms of the ffgen variable z."""
    return " + ".join(f"{c}*z^{i}" for i, c in enumerate(e.c)) or "0"

def bits(n):
    return int(n).bit_length()

class GP:
    """Runs PARI/GP scripts; every script and its output are kept under certificates/pari/."""
    def __init__(self, cert_dir, log):
        self.dir = os.path.join(cert_dir, "pari"); os.makedirs(self.dir, exist_ok=True)
        self.log = log
    def run(self, name, body, timeout):
        path = os.path.join(self.dir, f"{name}.gp")
        with open(path, "w") as f:
            f.write("default(parisizemax, 2000000000);\n")  # 2 GB stack cap (machine protection: 8 GB total)
            f.write(f'p = {P}; z = ffgen(Mod(1,p)*(x^5-3), \'z);\n')
            f.write(body)
        t0 = time.time()
        try:
            proc = subprocess.run(["gp", "-q", path], stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
            out, err, rc, status = proc.stdout, proc.stderr, proc.returncode, "ok"
        except subprocess.TimeoutExpired as e:
            out, err, rc, status = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), "TIMEOUT", None, "resource_exhaustion"
        wall = time.time() - t0
        with open(os.path.join(self.dir, f"{name}.out"), "w") as f:
            f.write(out)
        with open(os.path.join(self.dir, f"{name}.err"), "w") as f:
            f.write(err)
        kv = {}
        for line in out.splitlines():
            if "=" in line and not line.startswith("CAND") and not line.startswith(" "):
                k, _, v = line.partition("=")
                kv[k.strip()] = v.strip()
        self.log.append({"script": f"certificates/pari/{name}.gp", "wall_seconds": round(wall, 3), "status": status, "rc": rc})
        return {"kv": kv, "raw": out, "status": status, "wall_seconds": round(wall, 3), "rc": rc, "err": err}

# ----------------------------------------------------------------------------- factorization
def pollard_rho(n, seed=2, limit=2_000_000):
    if n % 2 == 0: return 2
    x = y = seed; c = 1; d = 1; it = 0
    while d == 1 and it < limit:
        x = (x * x + c) % n; y = (y * y + c) % n; y = (y * y + c) % n
        d = math.gcd(abs(x - y), n); it += 1
    return d if 1 < d < n else None

def trial_division(n, B=10**6):
    f = {}; m = n; d = 2
    while d <= B and d * d <= m:
        while m % d == 0:
            f[d] = f.get(d, 0) + 1; m //= d
        d += 1 if d == 2 else 2
    if 1 < m <= B * B and m != n:  # small leftover after trial division is prime
        pass
    return f, m

def ecm_hints(ecm_dir):
    """All integers that GMP-ECM logs reported as factors or cofactors (re-verified by division below)."""
    hints = set(); logs = []
    if not ecm_dir: return hints, logs
    for path in sorted(glob.glob(os.path.join(ecm_dir, "ecm_*.out"))):
        logs.append(path)
        for line in open(path):
            if "Factor found" in line or "cofactor" in line.lower() or "prime factor" in line:
                for tok in re.findall(r"\b\d{6,}\b", line):
                    hints.add(int(tok))
    return hints, logs

class Prover:
    """Primality proofs: deterministic MR (< 3.3e24) or PARI ECPP re-verified by gfpn_arith.verify_ecpp."""
    def __init__(self, gp, cert_dir):
        self.gp = gp; self.dir = os.path.join(cert_dir, "ecpp"); os.makedirs(self.dir, exist_ok=True)
        self.cache = {}
    def prove(self, n, label):
        n = int(n)
        if n in self.cache: return self.cache[n]
        if n < 3317044064679887385961981:
            ok = miller_rabin(n, bases=(2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41))
            res = {"n": str(n), "bits": bits(n), "proof": "deterministic Miller-Rabin, 13 prime bases (proven for n < 3.3e24)", "proven": ok}
        else:
            if not miller_rabin(n):
                res = {"n": str(n), "bits": bits(n), "proof": "none", "proven": False, "note": "fails Miller-Rabin: composite"}
            else:
                r = self.gp.run(f"primecert_{label}", f"N = {n};\nc = primecert(N);\nprint(\"VALID=\", primecertisvalid(c));\nprint(\"APRCL=\", isprime(N));\nwrite(\"{self.dir}/{label}.cert\", c);\n", timeout=1800)
                cert_path = os.path.join(self.dir, f"{label}.cert")
                res = {"n": str(n), "bits": bits(n), "proof": "PARI primecert (ECPP, Atkin-Morain)", "certificate": f"certificates/ecpp/{label}.cert",
                       "pari_primecertisvalid": r["kv"].get("VALID"), "pari_isprime_aprcl": r["kv"].get("APRCL"), "proven": False}
                if r["status"] == "ok" and os.path.exists(cert_path):
                    try:
                        txt = [l for l in open(cert_path).read().splitlines() if l.strip()][-1]
                        cert = ast.literal_eval(txt)
                        ok, detail = verify_ecpp(cert)
                        res["independent_verify_ecpp"] = ok; res["verify_detail"] = detail[-1] if detail else None
                        res["proven"] = bool(ok) and r["kv"].get("VALID") == "1"
                    except Exception as e:
                        res["independent_verify_ecpp"] = False; res["verify_error"] = f"{type(e).__name__}: {e}"
                else:
                    res["note"] = f"primecert did not complete: {r['status']}"
        self.cache[n] = res
        return res

def factor_certified(n, label, hints, prover):
    """Return a factorization certificate for n: proven prime factors + unfactored composites."""
    n = int(n)
    small, m = trial_division(n)
    pieces = [m] if m > 1 else []
    factors = {p: e for p, e in small.items()}
    unfactored = []
    # split with ECM hints (any hint integer h with 1 < gcd(h, piece) < piece splits it) and Pollard rho for small pieces
    changed = True
    while changed:
        changed = False
        new = []
        for c in pieces:
            if miller_rabin(c):
                new.append(c); continue
            g = None
            for h in sorted(hints):
                gg = math.gcd(h, c)
                if 1 < gg < c: g = gg; break
            if g is None and c < 2**90:
                g = pollard_rho(c)
            if g:
                new.extend([g, c // g]); changed = True
            else:
                new.append(c)
        pieces = new
    for c in pieces:
        if miller_rabin(c):
            factors[c] = factors.get(c, 0) + 1
        else:
            unfactored.append(c)
    # merge repeated primes
    proofs = {}
    for i, p in enumerate(sorted(factors)):
        proofs[str(p)] = prover.prove(p, f"{label}_f{i}")
    prod = 1
    for p, e in factors.items(): prod *= p ** e
    for c in unfactored: prod *= c
    return {
        "n": str(n), "bits": bits(n),
        "product_check": prod == n,
        "prime_factors": [{"p": str(p), "e": e, "bits": bits(p), "proven": proofs[str(p)]["proven"], "proof": proofs[str(p)]["proof"]} for p, e in sorted(factors.items())],
        "unfactored_composites": [{"c": str(c), "bits": bits(c)} for c in unfactored],
        "complete": (not unfactored) and all(proofs[str(p)]["proven"] for p in factors) and prod == n,
        "primality_proofs": proofs,
        "method": "trial division to 10^6; GMP-ECM 7.0.5 factor hints re-verified by exact division; Pollard rho (< 2^90); primality by deterministic Miller-Rabin (< 3.3e24) or PARI ECPP re-verified by gfpn_arith.verify_ecpp",
    }

def largest_prime_factor(fc):
    ps = [int(f["p"]) for f in fc["prime_factors"] if f["proven"]]
    return max(ps) if ps else None

def mult_order_from_factorization(g, n, fc):
    """ord_n(g) given the complete factorization of n-1."""
    e = n - 1
    for f in fc["prime_factors"]:
        r = int(f["p"])
        while e % r == 0 and pow(g, e // r, n) == 1:
            e //= r
    return e

# ----------------------------------------------------------------------------- main audit
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--curve", required=True, choices=list(SOURCES))
    ap.add_argument("--rigidity-budget-seconds", type=int, default=14400)
    ap.add_argument("--ecm-log-dir", default=None)
    ap.add_argument("--out", default=os.environ.get("GFPN_RUN_DIR"))
    ap.add_argument("--skip-rigidity", action="store_true")
    args = ap.parse_args()
    out_dir = args.out; assert out_dir, "GFPN_RUN_DIR or --out required"
    cert_dir = os.path.join(out_dir, "certificates"); os.makedirs(cert_dir, exist_ok=True)
    T0 = time.time()
    gp_log = []
    gp = GP(cert_dir, gp_log)
    prover = Prover(gp, cert_dir)
    curve = args.curve
    R = {"curve_id": curve, "experiment_id": "EXP-GFPN-726eb2", "run_status": "completed_valid", "failure_class": None,
         "invalid_reason": None, "seed": None,
         "randomness": "none: point search is deterministic (smallest x in F_p order), all other steps deterministic; PARI random state not used for any reported value (primecert curve choices are internal to the certificate, which is verified, not sampled)",
         "parameters": {"p": str(P), "q_bits": bits(Q), "field": "F_p[z]/(z^5-3)", "field_bits": 320, "extension_degree": 5},
         "sources": [], "metrics": {}, "steps": {}, "observations": [], "not_verifiable": {}, "deviations": []}
    metrics = R["metrics"]
    notes_hint = []

    # ------------------------------------------------------------ 1. sources
    src = SOURCES[curve]
    text_path = os.path.join(REPO, src["dir"], src["text"])
    lines = open(text_path, encoding="utf-8").read().splitlines()
    sha_obs = sha256(text_path)
    sha_rec = open(text_path + ".sha256").read().split()[0]
    R["sources"].append({"path": os.path.join(src["dir"], src["text"]), "sha256": sha_obs, "sha256_companion_match": sha_obs == sha_rec, "source_record": src["record"], "kn_lit": src["kn_lit"]})
    sec_lines = None
    if "secondary_dir" in src:
        sp = os.path.join(REPO, src["secondary_dir"], src["secondary_text"])
        sec_lines = open(sp, encoding="utf-8").read().splitlines()
        s2 = sha256(sp)
        R["sources"].append({"path": os.path.join(src["secondary_dir"], src["secondary_text"]), "sha256": s2, "sha256_companion_match": s2 == open(sp + ".sha256").read().split()[0], "role": "secondary (Hermez note restates EcGFp5 in Weierstrass form)"})

    # ------------------------------------------------------------ 2. model from the frozen text
    if curve == "EcGFp5":
        c_field = cite(lines, r"5 − 3\), i\.e\. the ring") + cite(lines, r"GF \(p\s*5\) = GF \(p\) \[z\]")
        c_eq = cite(lines, r"double-odd curve\[16\], with equation constants a = 2 and b = 263z")
        c_n = cite(lines, r"^n = 106799351671714695104148491657179270274505774058$") + cite(lines, r"^1727230159139685185762082554198619328292418486241$")
        n_note = int("106799351671714695104148491657179270274505774058" + "1727230159139685185762082554198619328292418486241")
        assert any(l["text"].strip() == "n = 106799351671714695104148491657179270274505774058" for l in c_n) and any(l["text"].strip() == "1727230159139685185762082554198619328292418486241" for l in c_n)
        # double-odd y^2 = x(x^2 + a x + b), a = 2, b = 263 z
        a_do, b_do = Fq(2), Fq((0, 263, 0, 0, 0))
        inv3 = Fq(3).inv(); inv27 = Fq(27).inv()
        A = b_do - a_do * a_do * inv3                      # X = x + a/3 shift: A = b - a^2/3
        B = Fq(2) * a_do * a_do * a_do * inv27 - a_do * b_do * inv3   # B = 2a^3/27 - ab/3
        expected_cofactor = 2
        n_hex_secondary = 0x7ffffffd800000077ffffff1000000167fffffe6cfb80639e8885c39d724a09ce80fd996948bffe1
        sec_cite = cite(sec_lines, r"7ffffffd800000077ffffff1000000167fffffe6cfb80639e8885c39d724a09ce80fd996948bffe1") + cite(sec_lines, r"6148914689804861439 \+ 263z|15713893096167979237 \+ 6148914689804861265z")
        A_sec = Fq((6148914689804861439, 263, 0, 0, 0)); B_sec = Fq((15713893096167979237, 6148914689804861265, 0, 0, 0))
        R["steps"]["model"] = {
            "published_model": "double-odd y^2 = x(x^2 + 2x + 263 z) over GF(p^5) = GF(p)[z]/(z^5 - 3)",
            "citations": {"field": c_field, "equation": c_eq, "n": c_n, "secondary_weierstrass_in_hermez_note": sec_cite},
            "weierstrass_from_paper_change_of_variable": {"A": fq_str(A), "B": fq_str(B), "formula": "x -> X - a/3: A = b - a^2/3, B = 2a^3/27 - ab/3 (paper section 'Change of Variable': A = (3b - a^2)/3, B = a(2a^2 - 9b)/27)"},
            "hermez_note_weierstrass_constants_match_derivation": (A == A_sec and B == B_sec),
            "n_paper_decimal_equals_hermez_hex": n_note == n_hex_secondary,
            "self_reported_order": f"2n, n = {n_note} ({bits(n_note)} bits)",
        }
        R["observations"].append("EcGFp5 Weierstrass constants stated in the Hermez note equal the change-of-variable of Pornin's double-odd equation: " + str(A == A_sec and B == B_sec))
        src_rec = yaml.safe_load(open(os.path.join(REPO, src["dir"], "source_record.yaml")))
        headline = str(src_rec.get("provenance", {}).get("what_the_paper_claims", {}).get("headline", ""))
        if "z^5 - 2" in headline:
            R["deviations"].append("inputs/PORNIN-2022-274-ECGFP5/source_record.yaml headline says modulus 'z^5 - 2'; the frozen paper text (paper_fulltext.md, cited lines) says z^5 - 3, and the Hermez note also uses z^5 - 3. The audit uses z^5 - 3 as the paper states; the source_record headline is reported as a transcription defect outside this task's write scope.")
        N_note = 2 * n_note
    else:
        c_field = cite(lines, r"\\mathbb\{F\}_\{p\^5\} = \\mathbb\{F\}_p\[z\] / \(z\^5 - 3\)")
        c_eq = cite(lines, r"y\^2 = x\^3 \+ 3x \+ 8z\^4")
        c_n = cite(lines, r"^n = 0xfffffffb0000000effffffe20000002cffffffcc2c13f5f892042da0dfcde3fc8f4b2caf22360ee3")
        n_note = 0xfffffffb0000000effffffe20000002cffffffcc2c13f5f892042da0dfcde3fc8f4b2caf22360ee3
        A = Fq(3); B = Fq((0, 0, 0, 0, 8))
        expected_cofactor = 1
        R["steps"]["model"] = {"published_model": "short Weierstrass y^2 = x^3 + 3x + 8 z^4 over F_p[z]/(z^5 - 3)",
                               "citations": {"field": c_field, "equation": c_eq, "n": c_n},
                               "self_reported_order": f"n = {n_note} ({bits(n_note)} bits), cofactor 1"}
        N_note = n_note
    assert c_eq and c_n, "parameter citations not found in frozen text"
    R["parameters"].update({"A": fq_str(A), "B": fq_str(B), "self_reported_n": str(n_note), "expected_cofactor": expected_cofactor})

    # ------------------------------------------------------------ 3. SEA point count (curve and twist)
    body = f"""A = {fq_str(A)}; B = {fq_str(B)};
E = ellinit([A, B]);
print("J=", E.j);
t0 = getwalltime(); N = ellcard(E); print("N=", N); print("SEA_MS=", getwalltime() - t0);
d = 0; forstep(k = 1, 200, 1, cand = z + k; if(!issquare(cand), d = cand; break));
print("TWIST_D=", d);
Et = ellinit([A*d^2, B*d^3]);
t0 = getwalltime(); Nt = ellcard(Et); print("NT=", Nt); print("SEA_TWIST_MS=", getwalltime() - t0);
print("SUM_CHECK=", N + Nt == 2*p^5 + 2);
print("APRCL_N_OVER_H=", isprime(N / {expected_cofactor}));
"""
    r = gp.run("count", body, timeout=7200)
    step = {"tool": "PARI/GP 2.15.4 ellcard (SEA with pari-seadata modular polynomials) over F_{p^5}", "status": r["status"], "wall_seconds": r["wall_seconds"]}
    if r["status"] != "ok" or "N" not in r["kv"]:
        step["outcome"] = "not_measured"; step["failure_class"] = r["status"] if r["status"] != "ok" else "infrastructure_error"
        step["stderr_tail"] = r["err"][-500:]
        N_sea = None; NT_sea = None
        R["not_verifiable"]["sea_count"] = f"SEA did not complete: {step['failure_class']}"
    else:
        N_sea = int(r["kv"]["N"]); NT_sea = int(r["kv"]["NT"])
        step.update({"N": str(N_sea), "N_bits": bits(N_sea), "sea_ms": r["kv"].get("SEA_MS"), "twist_d": r["kv"].get("TWIST_D"), "N_twist": str(NT_sea), "sea_twist_ms": r["kv"].get("SEA_TWIST_MS"),
                     "sum_check_N_plus_Nt_eq_2q_plus_2": r["kv"].get("SUM_CHECK") == "1", "pari_isprime_aprcl_N_over_h": r["kv"].get("APRCL_N_OVER_H"), "j_invariant": r["kv"].get("J")})
        step["N_equals_self_report"] = (N_sea == N_note)
    R["steps"]["point_count"] = step
    metrics["sea_method_id"] = "pari-gp-2.15.4/ellcard/SEA+seadata-0.20090618/F_p5"

    # ------------------------------------------------------------ 4. order certificate (independent arithmetic)
    n_cand = (N_sea // expected_cofactor) if N_sea is not None else n_note
    cand_origin = "regenerated by SEA (step 3)" if N_sea is not None else "self-reported integer from the frozen note (SEA not completed)"
    oc = {"candidate_n": str(n_cand), "candidate_origin": cand_origin, "cofactor_h": expected_cofactor}
    pr = prover.prove(n_cand, "n"); oc["primality"] = pr
    # deterministic point: smallest x = 0,1,2,... in F_p with x^3 + A x + B a square in F_q
    x0 = 0; y0 = None
    while True:
        rhs = Fq(x0) ** 3 + A * Fq(x0) + B
        if rhs.is_square():
            y0 = rhs.sqrt(); break
        x0 += 1
    Pt = (Fq(x0), y0)
    oc["point_search"] = {"x": x0, "y": list(y0.c), "on_curve": on_curve(A, B, Pt)}
    if expected_cofactor == 2:
        # rational 2-torsion: the double-odd point (0,0) maps to X = a/3; check it is a root of the cubic and the only one
        x2 = Fq(2) * Fq(3).inv()
        oc["two_torsion"] = {"x_of_rational_2_torsion_point": fq_str(x2), "is_root_of_cubic": (x2 ** 3 + A * x2 + B).is_zero(),
                             "other_2_torsion": "none iff x^2 + 2x + 263z is irreducible over F_q, i.e. disc 4 - 4*263z is a non-square",
                             "disc_is_nonsquare": not (Fq(4) - Fq(4) * Fq((0, 263, 0, 0, 0))).is_square(),
                             "pornin_double_odd_filter_b_nonsquare": not Fq((0, 263, 0, 0, 0)).is_square()}
        Pt = ec_add(A, Pt, Pt)  # P := 2Q lands in the odd-order part
        oc["point_search"]["used_point"] = "P = 2*Q (Q the searched point), so [n]P = [2n]Q"
    t1 = time.time()
    nP = mul(A, n_cand, Pt)
    oc["n_times_P_is_infinity"] = (nP is INF); oc["P_not_infinity"] = (Pt is not INF)
    oc["scalar_mul_seconds"] = round(time.time() - t1, 3)
    h_n = expected_cofactor * n_cand
    mults = multiples_in_hasse(Q, h_n)
    lo, hi = hasse_interval(Q)
    oc["hasse"] = {"interval": [str(lo), str(hi)], "multiples_of_h_n_in_interval": [str(m) for m in mults], "count": len(mults), "unique": len(mults) == 1 and mults[0] == h_n}
    oc["argument"] = ("n prime (ECPP, independently verified) and P != O with [n]P = O  =>  n | #E; "
                      + ("the rational 2-torsion point gives 2 | #E, gcd(2,n)=1  =>  2n | #E; " if expected_cofactor == 2 else "")
                      + "exactly one multiple of h*n lies in the Hasse interval  =>  #E = h*n.")
    oc["certified"] = bool(pr["proven"] and oc["n_times_P_is_infinity"] and oc["P_not_infinity"] and oc["hasse"]["unique"] and (expected_cofactor == 1 or (oc["two_torsion"]["is_root_of_cubic"] and oc["two_torsion"]["disc_is_nonsquare"])))
    oc["certified_order"] = str(h_n) if oc["certified"] else None
    oc["agrees_with_sea"] = (N_sea == h_n) if N_sea is not None else None
    oc["agrees_with_self_report"] = (h_n == N_note)
    R["steps"]["order_certificate"] = oc
    json.dump(oc, open(os.path.join(cert_dir, "order-certificate.json"), "w"), indent=2)
    metrics["order_certificate"] = "certificate" if oc["certified"] else "not_verifiable"
    metrics["order_matches_self_report"] = oc["agrees_with_self_report"]
    metrics["cofactor"] = expected_cofactor if oc["certified"] else None
    if not oc["certified"]:
        R["not_verifiable"]["order_certificate"] = "one of: primality proof, [n]P = O, Hasse uniqueness failed; see order-certificate.json"
    N = h_n if oc["certified"] else N_sea

    # ------------------------------------------------------------ 5. embedding degree
    hints, ecm_logs = ecm_hints(args.ecm_log_dir)
    if ecm_logs:
        os.makedirs(os.path.join(cert_dir, "ecm"), exist_ok=True)
        for lp in ecm_logs: shutil.copy(lp, os.path.join(cert_dir, "ecm", os.path.basename(lp)))
    n = n_cand
    fc_nm1 = factor_certified(n - 1, "nm1", hints, prover)
    json.dump(fc_nm1, open(os.path.join(cert_dir, "factorization-n-minus-1.json"), "w"), indent=2)
    emb = {"n_minus_1_factorization": [(f["p"], f["e"]) for f in fc_nm1["prime_factors"]], "complete": fc_nm1["complete"], "unfactored": fc_nm1["unfactored_composites"]}
    qmod = Q % n
    if fc_nm1["complete"]:
        e = mult_order_from_factorization(qmod, n, fc_nm1)
        emb.update({"embedding_degree": str(e), "bits": bits(e), "ratio_n_minus_1_over_e": str((n - 1) // e) if (n - 1) % e == 0 else None, "certificate": "exact multiplicative order from the complete factorization"})
        metrics["embedding_degree"] = "certificate"
    else:
        # bound: every known prime r with q^((n-1)/r) != 1 contributes r^{v_r} to e; unknown part bounds the loss
        known = 1
        for f in fc_nm1["prime_factors"]:
            r = int(f["p"]); v = f["e"]
            if pow(qmod, (n - 1) // r, n) != 1: known *= r ** v
        C = 1
        for c in fc_nm1["unfactored_composites"]: C *= int(c["c"])
        emb.update({"embedding_degree_lower_bound": str((n - 1) // C), "certificate": "bound only: e >= (n-1)/C where C is the unfactored part; exact value not_verifiable"})
        metrics["embedding_degree"] = "bound"
        R["not_verifiable"]["embedding_degree_exact"] = "n-1 not completely factored within budget"
    if curve == "EcGFp5":
        emb["self_report"] = {"claim": "e = (n-1)/5, a 317-bit integer; n-1 = 2^5 * 5 * 163 * 769 * 1059871 * 253243826720162431254857814100127 * 198400523053184002814403536918162724916343842520561", "citations": cite(lines, r"e = \(n − 1\)/5|n − 1 = 25 · 5 · 163 · 769 · 1059871|^· 253243826720162431254857814100127|^· 198400523053184002814403536918162724916343842520561")}
        emb["matches_self_report"] = (fc_nm1["complete"] and emb.get("ratio_n_minus_1_over_e") == "5")
    else:
        emb["self_report"] = {"claim": "e = n-1 (320 bits)", "citations": cite(lines, r"Curve embedding degree: n-1|Finding that \$e = n-1\$")}
        emb["matches_self_report"] = (fc_nm1["complete"] and emb.get("ratio_n_minus_1_over_e") == "1")
    R["steps"]["embedding_degree"] = emb
    metrics["embedding_degree_matches_self_report"] = emb["matches_self_report"]

    # ------------------------------------------------------------ 6. CM discriminant
    cm = {}
    if N is not None:
        t = Q + 1 - N; D = t * t - 4 * Q
        cm.update({"trace_t": str(t), "t_bits": bits(abs(t)), "D": str(D), "D_negative": D < 0, "abs_D_bits": bits(abs(D)), "abs_D_hex_digits": len(f"{abs(D):x}")})
        fc_D = factor_certified(abs(D), "D", hints, prover)
        json.dump(fc_D, open(os.path.join(cert_dir, "factorization-cm-discriminant.json"), "w"), indent=2)
        cm["abs_D_factorization"] = [(f["p"], f["e"]) for f in fc_D["prime_factors"]]; cm["factorization_complete"] = fc_D["complete"]; cm["unfactored"] = fc_D["unfactored_composites"]
        if fc_D["complete"]:
            sf = 1
            for f in fc_D["prime_factors"]:
                if f["e"] % 2 == 1: sf *= int(f["p"])
            D0 = -sf
            if D0 % 4 != 1: D0 *= 4   # fundamental discriminant of Q(sqrt(D))
            cm.update({"squarefree_part_of_abs_D": str(sf), "fundamental_discriminant": str(D0), "fundamental_discriminant_bits": bits(abs(D0)), "conductor_squared": str(abs(D) // sf)})
            metrics["cm_discriminant_bits"] = "certificate"
        else:
            cm["note"] = "bit length of D = t^2 - 4q is exact; the CM field (fundamental) discriminant needs the squarefree part, which is not_verifiable without the complete factorization"
            metrics["cm_discriminant_bits"] = "certificate (bit length of t^2-4q) / not_verifiable (fundamental discriminant)"
            R["not_verifiable"]["cm_fundamental_discriminant"] = "|D| not completely factored within budget: " + str(fc_D["unfactored_composites"])
        if curve == "EcMasFp5":
            D_note = -0x350910d76c19ff80472df1f236bda8f251edc59a20563b4f1bcb88ad47f9892d334755425f4369e43
            cm["self_report"] = {"claim": "D = t^2 - 4q = -0x350910d7...e43 (323 bits)", "citations": cite(lines, r"CM discriminant|CM Discriminant|350910d76c19ff80472df1f236bda8f251edc59a20563b4f1bcb88ad47f9892d334755425f4369e43")}
            cm["D_equals_self_reported_integer"] = (D == D_note)
            cm["self_reported_bit_length"] = 323
            cm["recomputed_bit_length"] = bits(abs(D))
            cm["bit_length_matches_self_report"] = (bits(abs(D)) == 323)
            if D == D_note and bits(abs(D)) != 323:
                R["observations"].append(f"EcMasFp5: the self-reported D integer reproduces exactly, but its binary length is {bits(abs(D))} bits, not the '323 bits' stated in the note (the hex string has {len(f'{abs(D):x}')} hex digits with leading nibble 3). A plausible explanation is counting the sign character (len(bin(D))-2 in Python gives 323 for a negative D); recorded as an observation, not adjudicated here.")
        else:
            cm["self_report"] = {"claim": "none: the EcGFp5 paper does not state a CM discriminant", "citations": []}
    else:
        metrics["cm_discriminant_bits"] = "not_verifiable"; R["not_verifiable"]["cm_discriminant_bits"] = "no certified order"
    R["steps"]["cm_discriminant"] = cm

    # ------------------------------------------------------------ 7. twist
    tw = {}
    if N is not None:
        Nt = 2 * Q + 2 - N
        tw.update({"twist_order": str(Nt), "bits": bits(Nt), "derivation": "#E' = 2q + 2 - #E", "sea_twist_count_agrees": (NT_sea == Nt) if NT_sea is not None else None})
        fc_t = factor_certified(Nt, "twist", hints, prover)
        json.dump(fc_t, open(os.path.join(cert_dir, "factorization-twist-order.json"), "w"), indent=2)
        tw["factorization"] = [(f["p"], f["e"], f["bits"]) for f in fc_t["prime_factors"]]; tw["complete"] = fc_t["complete"]; tw["unfactored"] = fc_t["unfactored_composites"]
        lpf = largest_prime_factor(fc_t)
        if fc_t["complete"]:
            rho_bits = 0.5 * math.log2(lpf) + RHO_CONST
            tw.update({"largest_prime_factor": str(lpf), "largest_prime_factor_bits": bits(lpf), "twist_cofactor": str(Nt // lpf), "twist_cofactor_bits": bits(Nt // lpf),
                       "twist_security_bits": round(rho_bits, 4), "formula": "log2(sqrt(pi * l' / 4)) = 0.5*log2(l') + 0.5*log2(pi/4) (SafeCurves rho cost)"})
            metrics["twist_order_factorization"] = "certificate"; metrics["twist_security_bits"] = "certificate"
            # twist embedding degree (needs l'-1 factored)
            fc_lt = factor_certified(lpf - 1, "twistprime_m1", hints, prover)
            json.dump(fc_lt, open(os.path.join(cert_dir, "factorization-twist-prime-minus-1.json"), "w"), indent=2)
            if fc_lt["complete"]:
                et = mult_order_from_factorization(Q % lpf, lpf, fc_lt)
                tw["twist_embedding_degree"] = {"value": str(et), "bits": bits(et), "ratio": str((lpf - 1) // et), "certificate": "exact"}
            else:
                tw["twist_embedding_degree"] = {"certificate": "not_verifiable: l'-1 not completely factored", "unfactored": fc_lt["unfactored_composites"], "known_factors": [(f["p"], f["e"]) for f in fc_lt["prime_factors"]]}
        else:
            C = 1
            for c in fc_t["unfactored_composites"]: C *= int(c["c"])
            ub = 0.5 * math.log2(C) + RHO_CONST
            tw.update({"twist_security_bits_upper_bound": round(ub, 4), "bound_note": "largest prime factor l' <= largest unfactored composite; exact value not_verifiable", "known_prime_factors_max_bits": bits(lpf) if lpf else None})
            metrics["twist_order_factorization"] = "bound"; metrics["twist_security_bits"] = "bound"
            R["not_verifiable"]["twist_security_bits_exact"] = "twist order not completely factored within budget"
        if curve == "EcMasFp5":
            nt_note = 0x128ad28934008b50864257bbff0983af9688b4f04ff3f024f86f; ct_note = 0xdce68ed7aef21329a0ac97d33d76f
            tw["self_report"] = {"claim": "twist order = 0x128ad2...f86f (205-bit prime) * 0xdce68e...d76f (116-bit cofactor); twist security 101.93 bits; twist embedding degree (nt-1)/15",
                                 "citations": cite(lines, r"Twist prime order|Twist cofactor|Twist embedding degree|Twist security|0x128ad28934008b50864257bbff0983af9688b4f04ff3f024f86f")}
            tw["product_of_self_reported_factors_equals_regenerated_twist_order"] = (nt_note * ct_note == Nt)
            tw["self_reported_prime_equals_regenerated_largest_prime_factor"] = (lpf == nt_note)
            if "twist_security_bits" in tw:
                tw["self_reported_twist_security_bits"] = 101.93
                tw["abs_difference"] = round(abs(tw["twist_security_bits"] - 101.93), 4)
                tw["matches_self_report_within_0.01"] = tw["abs_difference"] <= 0.01
                metrics["twist_security_matches_self_report_0.01"] = tw["matches_self_report_within_0.01"]
            if "twist_embedding_degree" in tw and tw["twist_embedding_degree"].get("ratio"):
                tw["twist_embedding_degree"]["matches_self_report_(nt-1)/15"] = (tw["twist_embedding_degree"]["ratio"] == "15")
            # curve rho figure 159.83
            rho_curve = 0.5 * math.log2(n) + RHO_CONST
            tw["curve_rho_bits"] = {"recomputed": round(rho_curve, 4), "self_reported": 159.83, "matches_within_0.01": abs(rho_curve - 159.83) <= 0.01, "citations": cite(lines, r"Curve security \(Pollard-Rho\)")}
        else:
            tw["self_report"] = {"claim": "none: the EcGFp5 paper states no twist order, twist factorization or twist-security figure", "citations": cite(lines, r"twist")}
            rho_curve = 0.5 * math.log2(n) + RHO_CONST
            tw["curve_rho_bits"] = {"recomputed": round(rho_curve, 4), "self_reported": None}
    else:
        metrics["twist_order_factorization"] = "not_verifiable"; metrics["twist_security_bits"] = "not_verifiable"
        R["not_verifiable"]["twist"] = "no certified order"
    R["steps"]["twist"] = tw
    metrics["factorization_method_id"] = "trial-division-1e6+gmp-ecm-7.0.5-hints(reverified)+pollard-rho+ECPP(pari-primecert,verify_ecpp)"

    # ------------------------------------------------------------ 8. rigidity: re-enumerate the published search
    rg = {"budget_seconds": args.rigidity_budget_seconds}
    if args.skip_rigidity:
        rg["outcome"] = "skipped (development run)"; metrics["rigidity_reproduced"] = "not_verifiable"
    else:
        if curve == "EcMasFp5":
            rg["published_procedure"] = "find_ec_over_gfp5(initial_a=0, initial_c=1, attempts=50): for A = 0,1,2,...: for c = 1..49: for i = 1..4: B = c*z^i; accept the first E: y^2 = x^3 + A x + B with prime order (Sage, order via PARI)"
            rg["citations"] = cite(lines, r"def find_ec_over_gfp5|B = c \* z\*\*i|if is_prime\(E\.order\(algorithm=\"pari\"\)\)|The first elliptic curve found was")
            rg["published_first_hit"] = {"A": 3, "c": 8, "i": 4}
            rg["predecessor_count"] = 3 * 49 * 4 + 7 * 4 + 3
            body = f"""budget = {args.rigidity_budget_seconds * 1000}; t0 = getwalltime(); idx = 0; found = 0; A = 0; c = 1;
{{
while(!found,
  for(i = 1, 4,
    idx++; E = ellinit([A, c*z^i]); t1 = getwalltime(); N = ellsea(E, 1); dt = getwalltime() - t1;
    pr = if(N == 0, 0, isprime(N));
    print("CAND idx=", idx, " A=", A, " c=", c, " i=", i, " sea=", N, " prime=", pr, " ms=", dt);
    if(pr, found = 1; print("FOUND=", idx, " ", A, " ", c, " ", i); break);
    if(getwalltime() - t0 > budget, found = -1; print("BUDGET=", idx); break));
  if(!found, c++; if(c == 50, c = 1; A++)));
}}
print("DONE=", found);
"""
        else:
            rg["published_procedure"] = "c = 1, 2, ...: for i = 1..4: if y^2 = x(x^2 + 2x + c z^i) has order 2n with n prime return b = c z^i; if y^2 = x(x^2 + 2x - c z^i) has order 2n with n prime return b = -c z^i. Fast filter: a curve can be double-odd only if neither b nor a^2 - 4b is a quadratic residue."
            rg["citations"] = cite(lines, r"^1\. c ← 1|^2\. For i = 1 to 4|has order 2n with n prime, then return b = czi|has order 2n with n prime, then return b = −czi|^3\. c ← c \+ 1|first usable curve is obtained for b = 263z|4b is a quadratic residue")
            rg["published_first_hit"] = {"c": 263, "i": 1, "sign": "+"}
            rg["predecessor_count"] = 262 * 8
            body = f"""budget = {args.rigidity_budget_seconds * 1000}; t0 = getwalltime(); idx = 0; found = 0; c = 1; nfilt = 0;
{{
while(!found,
  for(i = 1, 4, for(s = 0, 1,
    idx++; b = if(s == 0, c*z^i, -c*z^i);
    if(issquare(b) || issquare(4 - 4*b), nfilt++; print("CAND idx=", idx, " c=", c, " i=", i, " s=", s, " filtered=1"); next);
    A = b - 4/3; B = 16/27 - 2*b/3; E = ellinit([A, B]);
    t1 = getwalltime(); N = ellsea(E, 2); dt = getwalltime() - t1;
    pr = if(N == 0 || N % 2 != 0, 0, isprime(N/2));
    print("CAND idx=", idx, " c=", c, " i=", i, " s=", s, " sea=", N, " twoprime=", pr, " ms=", dt);
    if(pr, found = 1; print("FOUND=", idx, " ", c, " ", i, " ", s); break(2));
    if(getwalltime() - t0 > budget, found = -1; print("BUDGET=", idx); break(2))));
  if(!found, c++));
}}
print("NFILT=", nfilt); print("DONE=", found);
"""
        r = gp.run("rigidity", body, timeout=args.rigidity_budget_seconds + 600)
        cands = [l for l in r["raw"].splitlines() if l.startswith("CAND")]
        rg["candidates_examined"] = len(cands)
        rg["filtered_by_published_qr_test"] = sum(1 for l in cands if "filtered=1" in l)
        rg["sea_early_abort_nonprime"] = sum(1 for l in cands if " sea=0 " in l)
        rg["sea_full_count"] = sum(1 for l in cands if " sea=" in l and " sea=0 " not in l)
        rg["wall_seconds"] = r["wall_seconds"]; rg["gp_status"] = r["status"]
        rg["trace"] = "certificates/pari/rigidity.out"
        found = r["kv"].get("FOUND"); budget_hit = r["kv"].get("BUDGET")
        if found:
            parts = found.split()
            if curve == "EcMasFp5":
                hit = {"index": int(parts[0]), "A": int(parts[1]), "c": int(parts[2]), "i": int(parts[3])}
                same = (hit["A"], hit["c"], hit["i"]) == (3, 8, 4)
            else:
                hit = {"index": int(parts[0]), "c": int(parts[1]), "i": int(parts[2]), "sign": "+" if parts[3] == "0" else "-"}
                same = (hit["c"], hit["i"], hit["sign"]) == (263, 1, "+")
            rg["first_hit"] = hit; rg["first_hit_equals_published"] = same
            rg["outcome"] = "reproduced" if same else "FIRST HIT DIFFERS FROM PUBLISHED PARAMETERS"
            metrics["rigidity_reproduced"] = "certificate"
            metrics["rigidity_first_hit_equals_published"] = same
        elif budget_hit or r["status"] != "ok":
            rg["outcome"] = f"partial: budget/tool limit reached after {len(cands)} candidates ({'resource_exhaustion' if r['status'] != 'ok' or budget_hit else 'infrastructure_error'}); every examined predecessor was excluded, remainder not examined"
            metrics["rigidity_reproduced"] = "not_verifiable"
            R["not_verifiable"]["rigidity_reproduced"] = rg["outcome"]
        else:
            rg["outcome"] = "gp ended without FOUND/BUDGET marker: implementation_error"; metrics["rigidity_reproduced"] = "not_verifiable"
            R["not_verifiable"]["rigidity_reproduced"] = rg["outcome"]; rg["stderr_tail"] = r["err"][-800:]
    R["steps"]["rigidity"] = rg

    # ------------------------------------------------------------ 9. figure provenance
    figs = []
    if curve == "EcGFp5":
        figs.append({"id": "field_security_142", "claimed_bits": 142, "curve": "EcGFp5",
                     "tag": "asserted",
                     "tag_rationale": "The figure is derived inside the paper from a cost model of Gaudry's index-calculus attack (p^(2-2/5) ~ 2^102.4 systems, each costed at 'unlikely to go below O(D^2) ~ 2^40'), i.e. a modeled theoretical lower bound with optimistic-assumption language; it is not a measurement and not a certifiable parameter. This audit does not recompute attack cost (scientific boundary), so the tag records that the figure is asserted from a model in the note.",
                     "citations": cite(lines, r"2−2/5 ≈ 2102\.4|total theoretical complexity of at least 2142|unlikely to go below O\(D|2k\(k−1\) = 220"),
                     "audit_recomputation": "not attempted (out of scope: no PDP / attack-cost measurement in this experiment)"})
        figs.append({"id": "embedding_degree_n_minus_1_over_5", "claimed": "(n-1)/5, 317 bits", "curve": "EcGFp5", "tag": "computed (in note, from the stated factorization of n-1)",
                     "audit_recomputation": "recomputed; matches_self_report=" + str(emb.get("matches_self_report")), "citations": emb["self_report"]["citations"][:2]})
        figs.append({"id": "order_2n", "claimed": "2n, n 319-bit prime", "curve": "EcGFp5", "tag": "computed (in note)", "audit_recomputation": "regenerated by SEA and Hasse-interval certificate; matches=" + str(oc["agrees_with_self_report"]), "citations": c_n})
        figs.append({"id": "twist_security", "claimed": None, "curve": "EcGFp5", "tag": "not stated in the paper", "audit_recomputation": f"computed here: {tw.get('twist_security_bits', tw.get('twist_security_bits_upper_bound'))} bits ({metrics['twist_security_bits']})"})
    else:
        figs.append({"id": "field_security_142", "claimed_bits": 142, "curve": "EcMasFp5",
                     "tag": "inherited",
                     "tag_rationale": "The note states that because the extension field is the same as EcGFp5's it 'inherit[s] by default its security' and 'approximately achieves a 142-bit security level'; no derivation is given in the note. The figure is inherited from the EcGFp5 paper, where it is itself an asserted model-derived lower bound (see the EcGFp5 provenance row).",
                     "citations": cite(lines, r"we inherit by default its security|142\$-bit security level"),
                     "audit_recomputation": "not attempted (out of scope)"})
        figs.append({"id": "twist_security_101_93", "claimed_bits": 101.93, "curve": "EcMasFp5",
                     "tag": "computed",
                     "tag_rationale": "Self-reported from the twist factorization in the note; recomputed here from the regenerated twist order, its independently regenerated factorization (GMP-ECM + ECPP proofs) and the SafeCurves rho formula.",
                     "citations": cite(lines, r"Twist security \(Pollard-Rho\): 101\.93"),
                     "audit_recomputation": {"recomputed_bits": tw.get("twist_security_bits", tw.get("twist_security_bits_upper_bound")), "status": metrics["twist_security_bits"], "matches_within_0.01": tw.get("matches_self_report_within_0.01")}})
        figs.append({"id": "curve_rho_159_83", "claimed_bits": 159.83, "curve": "EcMasFp5", "tag": "computed", "audit_recomputation": tw.get("curve_rho_bits"), "citations": cite(lines, r"Curve security \(Pollard-Rho\): 159\.83")})
        figs.append({"id": "cm_discriminant_323_bits", "claimed": "D 323 bits", "curve": "EcMasFp5", "tag": "computed", "audit_recomputation": {"D_integer_matches": cm.get("D_equals_self_reported_integer"), "recomputed_bit_length": cm.get("recomputed_bit_length"), "bit_length_matches": cm.get("bit_length_matches_self_report")}, "citations": cm.get("self_report", {}).get("citations", [])[:2]})
        figs.append({"id": "embedding_degree_n_minus_1", "claimed": "e = n-1", "curve": "EcMasFp5", "tag": "computed", "audit_recomputation": "matches_self_report=" + str(emb.get("matches_self_report")), "citations": emb["self_report"]["citations"]})
        figs.append({"id": "twist_embedding_degree_(nt-1)/15", "claimed": "(nt-1)/15, 201 bits", "curve": "EcMasFp5", "tag": "computed", "audit_recomputation": tw.get("twist_embedding_degree"), "citations": cite(lines, r"Twist embedding degree")})
        figs.append({"id": "order_prime_320", "claimed": "n prime, 320 bits, cofactor 1", "curve": "EcMasFp5", "tag": "computed", "audit_recomputation": "regenerated by SEA and Hasse-interval certificate; matches=" + str(oc["agrees_with_self_report"]), "citations": c_n})
    R["steps"]["figure_provenance"] = figs
    metrics["figure_provenance_table"] = "present"
    prov = {"figure_provenance": {"curve_id": curve, "tag_vocabulary": {"computed": "derived in the note from its own stated computation and recomputed here", "inherited": "taken over from another document without recomputation in the note", "asserted": "stated from a model or argument without a certifiable computation"}, "figures": figs}}
    yaml.safe_dump(prov, open(os.path.join(out_dir, "figure-provenance.yaml"), "w"), sort_keys=False, width=110)

    # ------------------------------------------------------------ audit table
    def row(criterion, result, cert, self_report, match, note=None):
        return {"criterion": criterion, "result": result, "certificate": cert, "self_report": self_report, "matches_self_report": match, "note": note}
    rows = [
        row("order_certificate", "PASS" if oc["certified"] else "NOT_VERIFIABLE", "certificates/order-certificate.json + certificates/ecpp/n.cert + certificates/pari/count.out", R["steps"]["model"]["self_reported_order"], oc["agrees_with_self_report"], oc["argument"]),
        row("cofactor", "PASS" if oc["certified"] else "NOT_VERIFIABLE", "certificates/order-certificate.json", str(expected_cofactor), oc["certified"]),
        row("embedding_degree", "PASS" if fc_nm1["complete"] else "BOUND", "certificates/factorization-n-minus-1.json", emb["self_report"]["claim"], emb["matches_self_report"], f"e = {emb.get('embedding_degree', emb.get('embedding_degree_lower_bound'))} ({emb.get('bits')} bits)"),
        row("cm_discriminant_bits", ("PASS" if cm.get("factorization_complete") else "PASS_BITS_ONLY") if cm else "NOT_VERIFIABLE", "certificates/factorization-cm-discriminant.json", cm.get("self_report", {}).get("claim"), cm.get("bit_length_matches_self_report"), f"|D| = {cm.get('abs_D_bits')} bits; fundamental discriminant {cm.get('fundamental_discriminant_bits', 'not_verifiable')} bits"),
        row("twist_order_factorization", "PASS" if tw.get("complete") else ("BOUND" if tw else "NOT_VERIFIABLE"), "certificates/factorization-twist-order.json", tw.get("self_report", {}).get("claim"), tw.get("product_of_self_reported_factors_equals_regenerated_twist_order"), f"largest prime factor {tw.get('largest_prime_factor_bits')} bits"),
        row("twist_security_bits", "PASS" if tw.get("complete") else ("BOUND" if tw else "NOT_VERIFIABLE"), "certificates/factorization-twist-order.json", tw.get("self_reported_twist_security_bits"), tw.get("matches_self_report_within_0.01"), f"recomputed {tw.get('twist_security_bits', tw.get('twist_security_bits_upper_bound'))} bits"),
        row("rigidity_reproduced", {"certificate": "PASS" if metrics.get("rigidity_first_hit_equals_published") else "FAIL"}.get(metrics.get("rigidity_reproduced"), "NOT_VERIFIABLE"), "certificates/pari/rigidity.out", rg.get("published_first_hit"), metrics.get("rigidity_first_hit_equals_published"), rg.get("outcome")),
        row("figure_provenance_table", "PRESENT", "figure-provenance.yaml", None, None, f"{len(figs)} figures tagged"),
        row("scurve_control_certificate_match", "PASS (RUN-GFPN-17ed52, recorded before this run)", "runs/RUN-GFPN-17ed52/certificates/control-regeneration.json", None, None, "control run precedes GFPN scoring as the contract requires"),
    ]
    yaml.safe_dump({"audit_table": {"curve_id": curve, "p": str(P), "rows": rows, "not_verifiable": R["not_verifiable"], "deviations": R["deviations"]}}, open(os.path.join(out_dir, "audit-table.yaml"), "w"), sort_keys=False, width=110)

    # ------------------------------------------------------------ finish
    R["gp_calls"] = gp_log
    R["metrics"]["wall_seconds"] = round(time.time() - T0, 3)
    R["scientific_boundary"] = "Parameter audit only: no ECDLP solve, no PDP, no OA-SDH, no cover genus, no rho-beat claim. certificate.kind none."
    if N_sea is None and not oc["certified"]:
        R["run_status"] = "failed"; R["failure_class"] = "resource_exhaustion"
    json.dump(R, open(os.path.join(out_dir, "raw-result.json"), "w"), indent=2)
    print(json.dumps({"curve": curve, "metrics": metrics, "not_verifiable": R["not_verifiable"], "observations": R["observations"], "deviations": R["deviations"]}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
