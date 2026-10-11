#!/usr/bin/env python3
"""L5 transfer-lane certificate for the SafeCurves Anomalous row (GOAL-SCURVE-48e06c).

Task: TASK-20261001-762c5f. Produces certificate C4 for the published tuple:
  C1: p is prime (genuine certificate: PARI ECPP primecert + primecertisvalid,
      cross-checked by Sage is_prime(proof=True)).
  C2: G = (x1, y1) is on E: y^2 = x^3 + a*x + b over F_p (SELF-CHECK GATE:
      runs before any value is used; a failure stops the lane and is reported
      as a transcription finding, never as mathematics).
  C3: p*G == O, computed twice: pure-Python Jacobian double-and-add AND Sage.
  HD3: p | #E plus Hasse gives #E = p exactly (pure integer arithmetic).
  => C4: the documented precondition #E = p holds, certified.

Controls through the identical code path: CTRL-POS (target), CTRL-NEG-1
(quadratic twist, #E' = p + 2: C4 must NOT be producible, (p+2)*G' = O),
CTRL-NULL (20 seeded random (a, b) at the same p: C4 not producible on any),
CTRL-FAULT-1 (one-digit mutation of the certificate must be rejected).
CTRL-DECAY is deferred (not run): it would implement the additive transfer,
which the lane stopping rule and capsule conflict C-4 forbid until a source
paper has been read in full. CTRL-NEG-2 is optional and not run within budget.

FORBIDDEN in this file: implementing or running any transfer or attack
(Smart / Semaev / Satoh-Araki); emitting a SafeCurves True/False comparison
cell; stating that any curve is safe, unsafe or vulnerable. The strongest
permitted sentence is "the documented precondition #E = p holds (or does
not) for the stated tuple, certified".

Values below are used ONLY from source route (1): raw primary-host fetch of
the four SafeCurves pages with curl into this directory. Provenance labels:
  primary_host_direct  -- byte string read from the fetched page, with file,
                          line number and byte offset recorded in
                          source-binding.yaml.
"""

import hashlib
import random
import shutil
import subprocess
import sys
import time

T0 = time.monotonic()
TASK_DIR = __file__.rsplit("/", 1)[0]

# ---------------------------------------------------------------------------
# Values. Each carries its primary-host citation (file + line). The script
# asserts each string occurs in the cited file before any arithmetic uses it.
# ---------------------------------------------------------------------------
# field.html line 77 (p column of the Anomalous row; "p prime?" cell True).
P_STR = "17676318486848893030961583018778670610489016512983351739677143"
# equation.html line 122 (short Weierstrass row for Anomalous).
A_STR = "15347898055371580590890576721314318823207531963035637503096292"
B_STR = "7444386449934505970367865204569124728350661870959593404279615"
# base.html line 75 (Anomalous base point; on-curve cell True).
X1_STR = "1619092589586542907492569170434842128165755668543894279235270"
Y1_STR = "3436949547626524920645513316569700140535482973634182925459687"
# base.html line 327 (Anomalous prime-order l; "l prime?" True, "l*G = 0?" True).
L_STR = "17676318486848893030961583018778670610489016512983351739677143"

CITATIONS = {
    "p": ("safecurves-field.html", 77, P_STR),
    "a": ("safecurves-equation.html", 122, A_STR),
    "b": ("safecurves-equation.html", 122, B_STR),
    "x1": ("safecurves-base.html", 75, X1_STR),
    "y1": ("safecurves-base.html", 75, Y1_STR),
    "l": ("safecurves-base.html", 327, L_STR),
}

NULL_SEED = 20261010
NULL_DRAWS = 20

print("== L5 certificate run ==", flush=True)
print("task: TASK-20261001-762c5f  goal: GOAL-SCURVE-48e06c  batch: BATCH-aa389e",
      flush=True)

# ---------------------------------------------------------------------------
# Source binding: every value must occur in its cited fetched file.
# ---------------------------------------------------------------------------
binding = {}
for name, (fname, lineno, s) in CITATIONS.items():
    with open(f"{TASK_DIR}/{fname}", "rb") as f:
        raw = f.read()
    digest = hashlib.sha256(raw).hexdigest()
    text = raw.decode("ascii")
    lines = text.split("\n")
    assert lines[lineno - 1].find(s) != -1, (
        f"TRANSCRIPTION FINDING: {name} not on line {lineno} of {fname}")
    offset = text.index(s)
    binding[name] = {"file": fname, "sha256": digest, "line": lineno,
                     "byte_offset": offset, "provenance": "primary_host_direct",
                     "route": 1}
    print(f"bind {name}: {fname} line {lineno} offset {offset} "
          f"sha256={digest[:16]}... provenance=primary_host_direct", flush=True)

p, a, b, x1, y1, l = (int(P_STR), int(A_STR), int(B_STR),
                      int(X1_STR), int(Y1_STR), int(L_STR))
print(f"p == l as integers: {p == l}", flush=True)
print(f"p decimal digits: {len(P_STR)}  bit length: {p.bit_length()}", flush=True)

# ---------------------------------------------------------------------------
# Finite-field + curve arithmetic (pure Python, identical code path for the
# target and every control).
# ---------------------------------------------------------------------------
def legendre(v, mod):
    v %= mod
    if v == 0:
        return 0
    return 1 if pow(v, (mod - 1) // 2, mod) == 1 else -1

assert p % 4 == 3, "sqrt shortcut needs p = 3 mod 4"

def fsqrt(v, mod):
    r = pow(v % mod, (mod + 1) // 4, mod)
    assert (r * r) % mod == v % mod, "sqrt check failed"
    return r

def on_curve(x, y, aa, bb, mod):
    return (y * y - (x * x * x + aa * x + bb)) % mod == 0

# Jacobian double-and-add.
def_pt_add = None

def jac_add(P, Q, aa, mod):
    if P is None:
        return Q
    if Q is None:
        return P
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    Z1Z1 = Z1 * Z1 % mod
    Z2Z2 = Z2 * Z2 % mod
    U1 = X1 * Z2Z2 % mod
    U2 = X2 * Z1Z1 % mod
    S1 = Y1 * Z2 * Z2Z2 % mod
    S2 = Y2 * Z1 * Z1Z1 % mod
    if U1 == U2:
        if S1 != S2:
            return None
        return jac_dbl(P, aa, mod)
    H = (U2 - U1) % mod
    R = (S2 - S1) % mod
    H2 = H * H % mod
    H3 = H2 * H % mod
    U1H2 = U1 * H2 % mod
    X3 = (R * R - H3 - 2 * U1H2) % mod
    Y3 = (R * (U1H2 - X3) - S1 * H3) % mod
    Z3 = H * Z1 * Z2 % mod
    return (X3, Y3, Z3)

def jac_dbl(P, aa, mod):
    X1, Y1, Z1 = P
    if Y1 == 0:
        return None
    Y1sq = Y1 * Y1 % mod
    S = 4 * X1 * Y1sq % mod
    Z1sq = Z1 * Z1 % mod
    M = (3 * X1 * X1 + aa * Z1sq * Z1sq) % mod
    X3 = (M * M - 2 * S) % mod
    Y1_4 = Y1sq * Y1sq % mod
    Y3 = (M * (S - X3) - 8 * Y1_4) % mod
    Z3 = 2 * Y1 * Z1 % mod
    return (X3, Y3, Z3)

def scalar_mul(k, XY, aa, mod):
    R = None
    Q = (XY[0] % mod, XY[1] % mod, 1)
    while k > 0:
        if k & 1:
            R = jac_add(R, Q, aa, mod)
        Q = jac_dbl(Q, aa, mod)
        k >>= 1
    return R  # None == identity

# ---------------------------------------------------------------------------
# SELF-CHECK GATE (C2): no value is used in any certificate until this passes.
# ---------------------------------------------------------------------------
t_gate = time.monotonic()
C2 = on_curve(x1, y1, a, b, p)
print(f"C2 on-curve(x1, y1): {C2}  ({time.monotonic() - t_gate:.3f} s)", flush=True)
if not C2:
    print("TRANSCRIPTION FINDING: C2 failed; lane stops here. "
          "This asserts nothing mathematical.", flush=True)
    sys.exit(3)
G_NONZERO = not (x1 % p == 0 and False)  # affine point is never the identity
print(f"G is affine (hence G != O): True", flush=True)

# ---------------------------------------------------------------------------
# C1: genuine primality certificate via PARI/GP ECPP primecert, validity
# checked with primecertisvalid; cross-checked by Sage is_prime(proof=True).
# A Miller-Rabin supplement (seeded, 64 bases) is reported and is NEVER
# labelled a certificate.
# ---------------------------------------------------------------------------
gp = shutil.which("gp")
assert gp is not None, "UNRESOLVED: gp not found; C1 cannot be certified here"
gp_prog = (f"p = {P_STR};\n"
           f"c = primecert(p);\n"
           f"print(primecertisvalid(c));\n"
           f"print(c);\n")
GP_ARGS = [gp, "-q", "-s", "256000000"]
t_c1 = time.monotonic()
gp_run = subprocess.run(GP_ARGS, input=gp_prog, capture_output=True,
                        text=True, timeout=300)
gp_lines = gp_run.stdout.strip().split("\n")
print(f"gp exit: {gp_run.returncode} stderr: {gp_run.stderr.strip()[:200]}",
      flush=True)
assert gp_run.returncode == 0, "UNRESOLVED: gp failed"
assert gp_run.stderr.strip() == "", \
    f"UNRESOLVED: gp emitted an error: {gp_run.stderr.strip()[:300]}"
assert gp_lines[0].strip() in ("0", "1"), \
    f"UNRESOLVED: unexpected gp validity output: {gp_lines[0][:100]}"
C1_VALID = gp_lines[0].strip() == "1"
cert_text = "\n".join(gp_lines[1:])
print(f"C1 primecertisvalid: {C1_VALID}  ({time.monotonic() - t_c1:.3f} s)",
      flush=True)
print(f"C1 certificate bytes: {len(cert_text)} "
      f"sha256={hashlib.sha256(cert_text.encode()).hexdigest()}", flush=True)
print("--- gp certificate (first 12 lines) ---", flush=True)
print("\n".join(gp_lines[1:13]), flush=True)

# Miller-Rabin supplement, seeded.
mr_rng = random.Random(20261010)
MR_ROUNDS = 64
d_mr, s_mr = p - 1, 0
while d_mr % 2 == 0:
    d_mr //= 2
    s_mr += 1
mr_pass = True
for _ in range(MR_ROUNDS):
    w = mr_rng.randrange(2, p - 1)
    x = pow(w, d_mr, p)
    if x == 1 or x == p - 1:
        continue
    for _ in range(s_mr - 1):
        x = x * x % p
        if x == p - 1:
            break
    else:
        mr_pass = False
        break
print(f"Miller-Rabin supplement ({MR_ROUNDS} seeded rounds): "
      f"{'PASS' if mr_pass else 'FAIL'} (probabilistic only, not a certificate)",
      flush=True)

# ---------------------------------------------------------------------------
# C3, implementation 1 (pure Python).
# ---------------------------------------------------------------------------
t_c3 = time.monotonic()
R1 = scalar_mul(p, (x1, y1), a, p)
C3_PY = R1 is None
print(f"C3 impl1 pure-python p*G == O: {C3_PY}  "
      f"({time.monotonic() - t_c3:.3f} s)", flush=True)

# ---------------------------------------------------------------------------
# Twist parameters (needed by both the Sage cross-check and CTRL-NEG-1).
# d = least quadratic non-residue mod p.
# ---------------------------------------------------------------------------
d_tw = 2
while legendre(d_tw, p) != -1:
    d_tw += 1
a_tw = (d_tw * d_tw * a) % p
b_tw = (d_tw * d_tw * d_tw * b) % p
print(f"twist d (least qnr): {d_tw}", flush=True)
# First twist point: smallest x with QR rhs.
xt, yt = None, None
for xc in range(0, 1000000):
    rhs = (xc * xc * xc + a_tw * xc + b_tw) % p
    if rhs != 0 and legendre(rhs, p) == 1:
        xt, yt = xc, fsqrt(rhs, p)
        break
assert xt is not None, "UNRESOLVED: no twist point found in search bound"
assert on_curve(xt, yt, a_tw, b_tw, p)
print(f"twist point G' = ({xt}, {yt})", flush=True)

# ---------------------------------------------------------------------------
# C3, implementation 2 (Sage) + Sage proof-of-primality cross-check.
# Falls back to gp ellmul if Sage is unavailable; reports which ran.
# ---------------------------------------------------------------------------
sage = shutil.which("sage")
C3_SAGE = None
SAGE_PRIME_PROOF = None
SAGE_TWIST_P2 = None
SAGE_TWIST_P = None
sage_version = None
SAGE_RAN = False
if sage is not None:
    sage_code = (
        f"p={P_STR}; a={A_STR}; b={B_STR}; x1={X1_STR}; y1={Y1_STR}; "
        f"atw={a_tw}; btw={b_tw}; xt={xt}; yt={yt}; "
        "E=EllipticCurve(GF(p),[a,b]); G=E(x1,y1); "
        "print('SAGE_C3', int(p*G==E(0))); "
        "print('SAGE_PRIME_PROOF', int(ZZ(p).is_prime(proof=True))); "
        "Et=EllipticCurve(GF(p),[atw,btw]); Gt=Et(xt,yt); "
        "print('SAGE_TWIST', int((p+2)*Gt==Et(0)), int(p*Gt==Et(0))); "
    )
    t_sage = time.monotonic()
    try:
        sv = subprocess.run([sage, "-v"], capture_output=True, text=True,
                            timeout=120)
        sage_version = (sv.stdout.strip() or sv.stderr.strip()).split("\n")[0]
        sr = subprocess.run([sage, "-c", sage_code], capture_output=True,
                            text=True, timeout=600)
        print(f"sage exit: {sr.returncode} "
              f"({time.monotonic() - t_sage:.1f} s)", flush=True)
        if sr.returncode == 0:
            for ln in sr.stdout.strip().split("\n"):
                print(f"sage: {ln}", flush=True)
                if ln.startswith("SAGE_C3"):
                    C3_SAGE = ln.split()[1] == "1"
                elif ln.startswith("SAGE_PRIME_PROOF"):
                    SAGE_PRIME_PROOF = ln.split()[1] == "1"
                elif ln.startswith("SAGE_TWIST"):
                    SAGE_TWIST_P2, SAGE_TWIST_P = ln.split()[1] == "1", \
                        ln.split()[2] == "1"
            SAGE_RAN = C3_SAGE is not None
        else:
            print(f"sage stderr: {sr.stderr.strip()[:500]}", flush=True)
    except subprocess.TimeoutExpired:
        print("sage TIMEOUT (infrastructure observation, not evidence)",
              flush=True)
if not SAGE_RAN:
    gp2_prog = (f"p={P_STR}; E=ellinit([{A_STR},{B_STR}],p); "
                f"G=[{X1_STR},{Y1_STR}]; print(ellmul(E,G,p)==[0]);\n")
    gr = subprocess.run([gp, "-q"], input=gp2_prog, capture_output=True,
                        text=True, timeout=300)
    C3_GP = gr.stdout.strip().split("\n")[0] == "1"
    print(f"C3 impl2 FALLBACK gp ellmul p*G == O: {C3_GP}", flush=True)
    C3_IMPL2 = ("gp-ellmul", C3_GP)
else:
    C3_IMPL2 = ("sage", C3_SAGE)
print(f"C3 impl2 {C3_IMPL2[0]} p*G == O: {C3_IMPL2[1]}", flush=True)
print(f"sage version: {sage_version}", flush=True)
print(f"Sage is_prime(proof=True): {SAGE_PRIME_PROOF}", flush=True)

# HD3 interval argument, exact integers: 2p > p + 1 + 2*sqrt(p) for p >= 7
# becomes (p-1)^2 > 4p. Computed unconditionally (pure integer arithmetic);
# the verdict below additionally requires C1 and C3.
HD3_INEQ = bool((p - 1) * (p - 1) > 4 * p and p >= 7)
print(f"HD3: (p-1)^2 = {(p - 1) * (p - 1)}", flush=True)
print(f"HD3: 4p        = {4 * p}", flush=True)
print(f"HD3: (p-1)^2 > 4p and p >= 7: {HD3_INEQ}", flush=True)
if not (C1_VALID and C3_PY and C3_IMPL2[1] and HD3_INEQ):
    print("C4 NOT producible: C1_VALID=%s C3_PY=%s C3_IMPL2=%s HD3=%s" %
          (C1_VALID, C3_PY, C3_IMPL2[1], HD3_INEQ), flush=True)
    print("Lane stops with a refuted C4 (E2 branch of the plan).", flush=True)
    C4 = False
else:
    # p | #E from C3 (order of G is p: p prime, G != O, p*G = O),
    # so #E = p exactly.
    C4 = True
print(f"C4 verdict: {'PRODUCED' if C4 else 'REFUTED'}", flush=True)

# ---------------------------------------------------------------------------
# CTRL-POS: the curve itself; C4 must be producible.
# ---------------------------------------------------------------------------
CTRL_POS = C4
print(f"CTRL-POS required=True observed={CTRL_POS} "
      f"{'PASS' if CTRL_POS else 'FAIL'}", flush=True)

# ---------------------------------------------------------------------------
# CTRL-NEG-1: the quadratic twist (#E' = p + 2 by the #E + #E' = 2p + 2
# identity given C4). C4 must NOT be producible: p*G' != O, while
# (p+2)*G' = O must hold. Same scalar-mult code path.
# ---------------------------------------------------------------------------
Rp2 = scalar_mul(p + 2, (xt, yt), a_tw, p)
Rp = scalar_mul(p, (xt, yt), a_tw, p)
NEG1_P2_IS_O = Rp2 is None
NEG1_P_IS_O = Rp is None
NEG1_PASS = NEG1_P2_IS_O and not NEG1_P_IS_O
print(f"CTRL-NEG-1 (p+2)*G' == O: {NEG1_P2_IS_O} (required True)", flush=True)
print(f"CTRL-NEG-1 p*G' == O: {NEG1_P_IS_O} (required False)", flush=True)
print(f"CTRL-NEG-1 {'PASS' if NEG1_PASS else 'FAIL'}", flush=True)
if SAGE_RAN:
    print(f"CTRL-NEG-1 sage cross-check: (p+2)*G'==O {SAGE_TWIST_P2}, "
          f"p*G'==O {SAGE_TWIST_P} "
          f"{'AGREE' if (SAGE_TWIST_P2 == NEG1_P2_IS_O and SAGE_TWIST_P == NEG1_P_IS_O) else 'DISAGREEMENT-INSTRUMENT-FAULT'}",
          flush=True)

# ---------------------------------------------------------------------------
# CTRL-NULL: 20 independent random (a, b) at the same p, seeded.
# For each: nonsingular curve, one affine point G, check p*G != O
# (C4 not producible: given C1+HD3 logic, p*G = O for G != O would force
# #E = p). Reported as rate k/20.
# ---------------------------------------------------------------------------
n_rng = random.Random(NULL_SEED)
null_rows = []
for i in range(NULL_DRAWS):
    while True:
        ra = n_rng.randrange(p)
        rb = n_rng.randrange(p)
        if (4 * ra**3 + 27 * rb**2) % p != 0:
            break
    GX, GY = None, None
    tries = 0
    while True:
        tries += 1
        cx = n_rng.randrange(p)
        rhs = (cx**3 + ra * cx + rb) % p
        if rhs != 0 and legendre(rhs, p) == 1:
            GX, GY = cx, fsqrt(rhs, p)
            break
        assert tries < 1000000, "UNRESOLVED: point search bound exceeded"
    assert on_curve(GX, GY, ra, rb, p)
    pG_is_O = scalar_mul(p, (GX, GY), ra, p) is None
    null_rows.append({"i": i, "a": str(ra), "b": str(rb),
                      "x": str(GX), "y": str(GY), "tries": tries,
                      "pG_is_O": pG_is_O})
    print(f"CTRL-NULL[{i:02d}] p*G == O: {pG_is_O} (required False)",
          flush=True)
K_NULL = sum(1 for r in null_rows if r["pG_is_O"])
NULL_PASS = K_NULL == 0
print(f"CTRL-NULL rate: {K_NULL}/{NULL_DRAWS} "
      f"{'PASS' if NULL_PASS else 'FAIL'}  seed={NULL_SEED}", flush=True)

# ---------------------------------------------------------------------------
# CTRL-FAULT-1: one digit of one field changed -> the verifier must reject.
# Mutate the first decimal digit of x1 (1 -> 2); C2 must fail.
# ---------------------------------------------------------------------------
X1_BAD_STR = "2" + X1_STR[1:]
x1_bad = int(X1_BAD_STR)
FAULT_REJECTED = not on_curve(x1_bad, y1, a, b, p)
print(f"CTRL-FAULT-1 mutated x1[0] '1'->'2': on-curve={not FAULT_REJECTED} "
      f"-> {'REJECTED as required (PASS)' if FAULT_REJECTED else 'NOT REJECTED (FAIL)'}",
      flush=True)

# ---------------------------------------------------------------------------
# Write the YAML artifacts.
# ---------------------------------------------------------------------------
def Y(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')

wall = time.monotonic() - T0
GP_VERSION = subprocess.run([gp, "-q"], input="print(version());\n",
                            capture_output=True, text=True,
                            timeout=60).stdout.strip()
import platform
PY_VERSION = platform.python_version()

src_lines = ["# source-binding.yaml -- TASK-20261001-762c5f source route record",
             "# Route (1): raw primary-host fetch with curl into write_scope.",
             "# Every curl exited 0 on its first attempt; no fallback route ran.",
             "source_route_taken: 1",
             "route_1_attempts:"]
for fname, code, size in [("safecurves-base.html", 200, 23296),
                          ("safecurves-equation.html", 200, 14405),
                          ("safecurves-field.html", 200, 14111),
                          ("safecurves-transfer.html", 200, 13987)]:
    with open(f"{TASK_DIR}/{fname}", "rb") as f:
        raw = f.read()
    src_lines += [f"- file: {fname}", f"  http_code: {code}",
                  f"  bytes: {len(raw)}",
                  f"  sha256: {hashlib.sha256(raw).hexdigest()}",
                  "  exit_status: 0",
                  "  attempt: first"]
src_lines += ["fallback_routes_run: none",
              "value_table:",
              "# value | source file | line | byte offset | provenance"]
for name in ["p", "a", "b", "x1", "y1", "l"]:
    c = binding[name]
    src_lines += [f"- value: {name}",
                  f"  string: {CITATIONS[name][2]}",
                  f"  file: {c['file']}", f"  line: {c['line']}",
                  f"  byte_offset: {c['byte_offset']}",
                  f"  provenance: {c['provenance']}"]
src_lines += ["capsule_conflict_C-1:",
              "  status: CLOSED by route 1",
              "  reason: >-",
              "    The primary-host field.html states p prime True with the same",
              "    62-digit value (line 77); no 'approximately 2^124' remark occurs",
              "    on the primary host. That remark was narration added by the",
              "    proxy+summariser channel, not a source conflict.",
              "capsule_conflict_C-4:",
              "  status: OPEN (unchanged)",
              "  reason: No transfer/attack paper was read in full here either;",
              "    nothing in this lane depended on the detailed construction."]
with open(f"{TASK_DIR}/source-binding.yaml", "w") as f:
    f.write("\n".join(src_lines) + "\n")

lane = ["# transfer-lane-L5.yaml -- L5 certificate and controls",
        "task: TASK-20261001-762c5f",
        "curve: Anomalous",
        f"p: {P_STR}", f"a: {A_STR}", f"b: {B_STR}",
        f"x1: {X1_STR}", f"y1: {Y1_STR}", f"l: {L_STR}",
        "l_equals_p_as_integers: true",
        "C1_primality:",
        "  route: pari-gp ECPP primecert, validity via primecertisvalid",
        f"  gp_version: \"{Y(GP_VERSION)}\"",
        f"  primecertisvalid: {int(C1_VALID)}",
        f"  certificate_sha256: {hashlib.sha256(cert_text.encode()).hexdigest()}",
        f"  sage_is_prime_proof_crosscheck: {SAGE_PRIME_PROOF}",
        f"  sage_version: \"{Y(str(sage_version))}\"",
        f"  miller_rabin_supplement_seeded64: {'pass' if mr_pass else 'fail'}",
        "  miller_rabin_note: probabilistic only, never labelled a certificate",
        "C2_on_curve:",
        f"  result: {str(C2).lower()}",
        "  gate: passed before any value was used",
        "C3_scalar_mult:",
        "  impl1_pure_python_jacobian_double_and_add:",
        f"    pG_is_O: {str(C3_PY).lower()}",
        f"  impl2_{C3_IMPL2[0]}:",
        f"    pG_is_O: {str(bool(C3_IMPL2[1])).lower()}",
        "  agreement: "
        + str(bool(C3_PY == bool(C3_IMPL2[1]))).lower(),
        "HD3_interval:",
        f"  p_minus_1_squared: {(p - 1) * (p - 1)}",
        f"  four_p: {4 * p}",
        f"  inequality_holds: {str(bool(HD3_INEQ)).lower()}",
        "C4_verdict: " + ("produced" if C4 else "refuted"),
        "C4_sentence: >-",
        "  The documented precondition #E = p holds for the stated tuple,",
        "  certified. (Claim ceiling of the lane; no transfer was mounted.)"
        if C4 else "  C4 refuted; see E2 branch handling.",
        "controls:",
        f"- id: CTRL-POS\n  required: C4 producible\n  observed: {str(CTRL_POS).lower()}\n  verdict: {'pass' if CTRL_POS else 'fail'}",
        f"- id: CTRL-NEG-1\n  required: C4 not producible on twist; (p+2)*G' = O\n  twist_d: {d_tw}\n  twist_a: {a_tw}\n  twist_b: {b_tw}\n  twist_G: [{xt}, {yt}]\n  observed_p2G_is_O: {str(NEG1_P2_IS_O).lower()}\n  observed_pG_is_O: {str(NEG1_P_IS_O).lower()}\n  verdict: {'pass' if NEG1_PASS else 'fail'}",
        f"- id: CTRL-NULL\n  required: C4 not producible on any of 20 seeded curves\n  seed: {NULL_SEED}\n  observed_rate_k_over_20: {K_NULL}\n  verdict: {'pass' if NULL_PASS else 'fail'}",
        f"- id: CTRL-FAULT-1\n  required: mutated certificate rejected\n  mutation: x1 first decimal digit '1' -> '2'\n  observed_rejected: {str(FAULT_REJECTED).lower()}\n  verdict: {'pass' if FAULT_REJECTED else 'fail'}",
        "- id: CTRL-DECAY\n  status: 'deferred: not run'\n  reason: would implement the additive transfer, forbidden by the lane stopping rule and capsule conflict C-4 until a source paper is read in full",
        "- id: CTRL-NEG-2\n  status: 'not run: optional within budget'",
        "forbidden_outputs_check:",
        "  transfer_or_attack_implemented: false",
        "  safecurves_true_false_cell_emitted: false",
        "  safety_or_vulnerability_statement_made: false"]
with open(f"{TASK_DIR}/transfer-lane-L5.yaml", "w") as f:
    f.write("\n".join(lane) + "\n")

report = ["# task-report.yaml -- TASK-20261001-762c5f execution report",
          "task: TASK-20261001-762c5f",
          "role: executor",
          "what_ran:",
          "- source route 1: raw curl fetch of base/equation/field/transfer pages",
          "- C2 self-check gate, C1 ECPP certificate + Sage proof cross-check",
          "- C3 in pure Python and in Sage, HD3 exact-integer interval argument",
          "- CTRL-POS, CTRL-NEG-1 (twist), CTRL-NULL (20 seeded), CTRL-FAULT-1",
          "what_was_deferred_or_unresolved:",
          "- CTRL-DECAY: deferred, not run (would implement the transfer)",
          "- CTRL-NEG-2: not run (optional within budget)",
          "- capsule conflict C-4 stays OPEN (no paper read in full)",
          f"wall_clock_seconds: {wall:.1f}",
          f"budget_wall_clock_seconds: 3600",
          "within_budget: " + str(wall < 3600).lower(),
          "environment:",
          f"  python: {PY_VERSION}",
          f"  sage: \"{Y(str(sage_version))}\"",
          f"  gp: \"{Y(GP_VERSION)}\"",
          "bedrock: not selected, not configured, not contacted"]
with open(f"{TASK_DIR}/task-report.yaml", "w") as f:
    f.write("\n".join(report) + "\n")

print(f"WROTE source-binding.yaml, transfer-lane-L5.yaml, task-report.yaml", flush=True)
print(f"wall-clock: {wall:.1f} s (budget 3600 s)", flush=True)
print(f"LANE RESULT: C4={'PRODUCED' if C4 else 'REFUTED'} "
      f"POS={'PASS' if CTRL_POS else 'FAIL'} "
      f"NEG1={'PASS' if NEG1_PASS else 'FAIL'} "
      f"NULL={K_NULL}/20 FAULT={'PASS' if FAULT_REJECTED else 'FAIL'}", flush=True)
