"""EXP-ENDO-001 shared implementation (frozen protocol, TASK-20260727-002).

Endomorphism-invariant factor base on GLV toy prime-field curves:
  - j=0     (a=0, p = 1 mod 3):  phi(x,y) = (zeta3*x, y),   x-orbits {x,zx,z^2x}, r=3
  - j=1728  (b=0, p = 1 mod 4):  phi(x,y) = (-x, i*y),      x-orbits {x,-x},      r=2
  - generic (j not in {0,1728}): negation orbits {(x,y),(x,-y)} on signed points, r=2

Displacement measurement (frozen): generator pair (Z_phi, Z_phi^T), Z_phi the
cyclic phi-shift on orbit blocks; alpha = rank(M - Z_phi*M*Z_phi^T) over F_n.
Commutation residual ||M*Phi - Phi*M||_0 with orbit/sign bookkeeping.

Design decisions disclosed in experiments/EXP-ENDO-001/implementation.md.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
import sympy
import yaml

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    os.pardir, os.pardir, os.pardir))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness.toycurve import EllipticCurve, ECDLPInstance, generate_instance, _seed_int  # noqa: E402
from harness import rho as rho_mod  # noqa: E402

EXP_ID = "EXP-ENDO-001"
EXP_DIR = os.path.join(REPO, "experiments", EXP_ID)
READ_EXP_DIR = EXP_DIR  # run outputs are read from here (monkeypatched in smoke tests)
FROZEN_INSTANCES = os.path.join(EXP_DIR, "frozen-instances.yaml")
FROZEN_FACTORBASES = os.path.join(EXP_DIR, "frozen-factorbases.yaml")

# ---- frozen protocol constants (specification.yaml) ----
BITS_LIST = [16, 20, 24]
SEEDS = [1, 2, 3]
SEED_TO_BITS = {1: 16, 2: 20, 3: 24}          # one-to-one mapping (MTIC precedent)
FAMILIES = ["j0", "j1728", "generic"]
M_ARITY = 3                                    # S_4 systems
N_HIT_TARGETS = 200                            # decomposition tests per arm per cell
N_HARVEST_POOL = 2000                          # harvesting pool per cell (MTIC protocol)
EVAL_CAP_PER_CELL = 50_000_000                 # tuple evaluations cap per cell
CELL_TIME_CAP_S = 1500.0                       # per-cell cumulative cap
RUN_SELF_CAP_S = 1700.0                        # internal self-cap (hard limit 1800)
RUN_HARD_TIMEOUT_S = 1800                      # spec budget per run
RSS_LIMIT_BYTES = 4 * 1024 ** 3                # 4 GB hard cap (post-hoc enforced)
RSS_ABORT_BYTES = int(3.75 * 1024 ** 3)        # proactive abort threshold
AP_D_MAX = 64                                  # EV-STR-001 D = {1..64}
MULS_PER_EC_ADD = 4 + 15                       # EV-STR-001 charging rule (4 mul + inv@15)
FN_OP_TO_FP_MUL = 1                            # F_n and F_p ops comparable at toy (EV-STR-001)


# ---------------------------------------------------------------- utilities
def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def sha256_obj(obj) -> str:
    return hashlib.sha256(canon(obj).encode()).hexdigest()


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def git_state() -> tuple[str, bool, str]:
    """commit, dirty over non-._ tracked paths, basis string (disclosed)."""
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                            capture_output=True, text=True).stdout.strip() or "unknown"
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                         cwd=REPO, capture_output=True, text=True).stdout
    dirty_lines = []
    for line in out.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 else line
        # exclude AppleDouble ._ paths anywhere in the path
        parts = path.replace(" -> ", "/").split("/")
        if any(p.startswith("._") for p in parts):
            continue
        dirty_lines.append(line)
    basis = ("git status --porcelain --untracked-files=no; lines whose path "
             "contains an AppleDouble '._' component are excluded (exFAT volume "
             "artifact, no tracked content); untracked files (incl. this "
             "experiment's outputs being written) are not part of the dirty flag")
    return commit, bool(dirty_lines), basis


def environment() -> dict:
    import numpy
    import yaml as _yaml
    return {
        "operating_system": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "sage_version": None,
        "dependencies": {"sympy": sympy.__version__,
                         "numpy": numpy.__version__,
                         "pyyaml": _yaml.__version__},
    }


def curve_id(p: int, a: int, b: int, field_bits: int) -> str:
    h = hashlib.sha256(f"{p}:{a}:{b}".encode()).hexdigest()[:8]
    return f"TOY-P{field_bits}-{h}"


def peak_rss_bytes() -> int:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is bytes on macOS, KB on Linux
    return ru.ru_maxrss if platform.system() != "Linux" else ru.ru_maxrss * 1024


def cpu_seconds() -> float:
    ru = resource.getrusage(resource.RUSAGE_SELF)
    return round(ru.ru_utime + ru.ru_stime, 6)


class BudgetGuard:
    """Wall-clock self-cap + proactive RSS abort (darwin rejects RLIMIT_AS;
    the 4 GB cap is enforced post-hoc against measured peak RSS, mechanism
    recorded in every manifest)."""
    def __init__(self, t0: float, self_cap: float = RUN_SELF_CAP_S):
        self.t0 = t0
        self.self_cap = self_cap

    def check(self, where: str = ""):
        if time.time() - self.t0 > self.self_cap:
            raise ResourceExhaustion(f"wall-clock self-cap {self.self_cap}s exceeded at {where}")
        if peak_rss_bytes() > RSS_ABORT_BYTES:
            raise ResourceExhaustion(f"peak RSS exceeded abort threshold at {where}")


class ResourceExhaustion(Exception):
    pass


# ------------------------------------------------------- instance generation
def find_zeta3(p: int) -> int | None:
    if p % 3 != 1:
        return None
    for g in range(2, min(p, 1000)):
        z = pow(g, (p - 1) // 3, p)
        if z != 1 and pow(z, 3, p) == 1:
            return z
    return None


def j_invariant(p: int, a: int, b: int) -> int:
    den = (4 * a * a * a + 27 * b * b) % p
    return (1728 * (4 * a * a * a % p) * pow(den, -1, p)) % p


def _subgroup_from_curve(E: EllipticCurve, seed: int, tag: str, bits: int):
    """Largest-prime-factor subgroup; returns (n, cofactor, P, k, Q, order) or None.

    order_bsgs can return a small common annihilator of its two probe points
    (observed on j=0 curves: smooth junk orders caused 400 consecutive
    rejections in the first smoke test). The order candidate is therefore
    verified as an annihilator of three independently seeded points; on
    failure the exact naive count is used. The resulting subgroup is in any
    case certified independently of the order computation: n prime, P != O,
    n*P = O proves ord(P) = n divides #E.
    """
    order = E.order_bsgs()
    verified = True
    for j in range(3):
        x = _seed_int(seed, f"{tag}v{j}") % E.p
        R = E.lift_x(x)
        if R is None:
            continue
        if E.mul(order, R) is not None:
            verified = False
            break
    if not verified:
        order = E.order()  # exact fallback
    factors = sympy.factorint(order)
    n = int(max(factors))
    if n.bit_length() < bits - 2 or n < 5:
        return None
    cofactor = order // n
    for j in range(1, 4000):
        x = _seed_int(seed, f"{tag}x.{j}") % E.p
        R = E.lift_x(x)
        if R is None:
            continue
        P = E.mul(cofactor, R)
        if P is not None and E.mul(n, P) is None:
            k = _seed_int(seed, f"{tag}k") % (n - 2) + 2
            Q = E.mul(k, P)
            return n, cofactor, P, k, Q, order
    return None


def gen_j0(seed: int, bits: int) -> dict:
    """j=0 curve y^2 = x^3 + b, p = 1 mod 3. Deterministic.

    Regeneration (frozen stop rule): j=0 has only 6 sextic twist orders per p;
    if none carries a prime factor >= 2^(bits-2), advance p along the
    nextprime chain to the next p = 1 mod 3 and retry (observed: the seed-3
    24-bit first p gave all 6 twist orders with largest factor <= 2^15.3).
    """
    p = int(sympy.nextprime(_seed_int(seed, "p") % (2 ** bits) | (1 << (bits - 1))))
    while p % 3 != 1:
        p = int(sympy.nextprime(p))
    for regen in range(50):
        for t in range(1, 25):
            b = _seed_int(seed, f"j0b{t}") % p
            if b == 0:
                continue
            E = EllipticCurve(p, 0, b)
            sub = _subgroup_from_curve(E, seed, f"j0.{t}", bits)
            if sub is None:
                continue
            n, cofactor, P, k, Q, order = sub
            zeta3 = find_zeta3(p)
            assert zeta3 is not None
            return {"family": "j0", "field_bits": bits, "seed": seed, "p": p, "a": 0,
                    "b": b, "order_E": order, "n": n, "cofactor": cofactor,
                    "P": list(P), "Q": list(Q), "k": k, "zeta3": zeta3, "i_sqrt": None,
                    "n_p_regenerations": regen,
                    "derivation": ("p: generate_instance seed formula (tag 'p') advanced by "
                                   "nextprime to p=1 mod 3, plus deterministic nextprime-chain "
                                   f"regeneration x{regen} (sextic-twist orders all smooth on "
                                   "skipped primes); b: seeded stream j0b{t}; subgroup: largest "
                                   "prime factor of #E (annihilator-verified order_bsgs, naive "
                                   "fallback), n.bit_length>=bits-2; P: cofactor clearing; k: seeded")}
        p = int(sympy.nextprime(p))
        while p % 3 != 1:
            p = int(sympy.nextprime(p))
    raise RuntimeError(f"no j0 curve for seed={seed} bits={bits} after 50 regenerations")


def gen_j1728(seed: int, bits: int) -> dict:
    """j=1728 curve y^2 = x^3 + a*x, p = 1 mod 4. Deterministic; same
    nextprime-chain regeneration as gen_j0 (4 quartic twist orders per p)."""
    p = int(sympy.nextprime(_seed_int(seed, "p") % (2 ** bits) | (1 << (bits - 1))))
    while p % 4 != 1:
        p = int(sympy.nextprime(p))
    for regen in range(50):
        i_sqrt = int(sympy.ntheory.residue_ntheory.sqrt_mod(p - 1, p))
        for t in range(1, 25):
            a = _seed_int(seed, f"j1728a{t}") % p
            if a == 0:
                continue
            E = EllipticCurve(p, a, 0)
            sub = _subgroup_from_curve(E, seed, f"j1728.{t}", bits)
            if sub is None:
                continue
            n, cofactor, P, k, Q, order = sub
            return {"family": "j1728", "field_bits": bits, "seed": seed, "p": p, "a": a,
                    "b": 0, "order_E": order, "n": n, "cofactor": cofactor,
                    "P": list(P), "Q": list(Q), "k": k, "zeta3": None, "i_sqrt": i_sqrt,
                    "n_p_regenerations": regen,
                    "derivation": ("p: generate_instance seed formula (tag 'p') advanced by "
                                   "nextprime to p=1 mod 4, plus deterministic nextprime-chain "
                                   f"regeneration x{regen} (quartic-twist orders all smooth on "
                                   "skipped primes); a: seeded stream j1728a{t}; subgroup largest "
                                   "prime factor of #E (annihilator-verified order_bsgs, naive "
                                   "fallback), n.bit_length>=bits-2; P: cofactor clearing; "
                                   "k: seeded; i = sqrt(-1) mod p")}
        p = int(sympy.nextprime(p))
        while p % 4 != 1:
            p = int(sympy.nextprime(p))
    raise RuntimeError(f"no j1728 curve for seed={seed} bits={bits} after 50 regenerations")


def gen_generic(seed: int, bits: int) -> dict:
    """Generic non-GLV curve via harness/toycurve.py generate_instance; j not in {0,1728}."""
    for off in range(200):
        s = seed if off == 0 else seed * 1000 + off
        inst = generate_instance(seed=s, field_bits=bits, min_prime_order_bits=bits - 2)
        j = j_invariant(inst.p, inst.a, inst.b)
        if j in (0, 1728):
            continue
        return {"family": "generic", "field_bits": bits, "seed": seed, "p": inst.p,
                "a": inst.a, "b": inst.b, "order_E": None, "n": inst.n,
                "cofactor": None, "P": list(inst.P), "Q": list(inst.Q), "k": inst.k,
                "zeta3": None, "i_sqrt": None,
                "derivation": ("harness/toycurve.py generate_instance(seed, bits, "
                               f"min_prime_order_bits=bits-2) with generator seed {s}; "
                               "j-invariant computed and required not in {{0,1728}} "
                               f"(j={j}); random-curve CM by a small discriminant is "
                               "exponentially unlikely (disclosed assumption)")}
    raise RuntimeError(f"no generic curve for seed={seed} bits={bits}")


def instance_checks(rec: dict) -> dict:
    p, a, b, n = rec["p"], rec["a"], rec["b"], rec["n"]
    E = EllipticCurve(p, a, b)
    P, Q = tuple(rec["P"]), tuple(rec["Q"])
    checks = {
        "p_prime": bool(sympy.isprime(p)),
        "n_prime": bool(sympy.isprime(n)),
        "P_on_curve": E.is_on_curve(P),
        "Q_on_curve": E.is_on_curve(Q),
        "Q_eq_kP": E.mul(rec["k"], P) == Q,
        "nP_eq_O": E.mul(n, P) is None,
        "j_invariant": j_invariant(p, a, b),
    }
    if rec["family"] == "j0":
        z = rec["zeta3"]
        checks["congruence"] = (p % 3 == 1)
        checks["zeta3_cube_root"] = (pow(z, 3, p) == 1 and z != 1)
        checks["phi_order"] = 3
        # x-orbit automatic on-curve for j=0: (zx)^3+b = x^3+b
        checks["orbit_x_auto_oncurve"] = all(
            E.lift_x((z * P[0]) % p) is not None for _ in range(1))
    elif rec["family"] == "j1728":
        i = rec["i_sqrt"]
        checks["congruence"] = (p % 4 == 1)
        checks["i_sqrt_check"] = (i * i % p) == (p - 1)
        # phi^2 = negation on points: phi(phi(x,y)) = (x,-y)
        checks["phi_squared_is_negation"] = True  # (-(-x), i*(i*y)) = (x, -y) since i^2=-1
        checks["phi_order_on_x"] = 2
    else:
        checks["congruence"] = True
        checks["j_not_in_0_1728"] = checks["j_invariant"] not in (0, 1728)
    return checks


# --------------------------------------------------------- factor base build
def ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def fb_phi_j0(inst: dict) -> dict:
    """Union of complete phi-orbits {x, zeta3*x, zeta3^2*x}; FB_size = 3*ceil(B/3)."""
    E = EllipticCurve(inst["p"], inst["a"], inst["b"])
    p, zeta3, seed = inst["p"], inst["zeta3"], inst["seed"]
    B = math.isqrt(inst["n"]) + (1 if math.isqrt(inst["n"]) ** 2 < inst["n"] else 0)
    n_orbits = ceil_div(B, 3)
    xs: list[int] = []
    used: set[int] = set()
    j = 0
    while len(xs) < 3 * n_orbits and j < 200 * n_orbits + 1000:
        x = _seed_int(seed, f"phifb{j}") % p
        j += 1
        orbit = [x, (zeta3 * x) % p, (zeta3 * zeta3 * x) % p]
        if len(set(orbit)) < 3 or any(o in used for o in orbit):
            continue
        if any(E.lift_x(o) is None for o in orbit):
            continue  # never happens for j=0 (x^3+b preserved); audited below
        xs.extend(orbit)
        used.update(orbit)
    return {"arm": "phi_invariant", "family": "j0", "B": B, "r": 3,
            "column_kind": "x", "n_orbits": n_orbits,
            "elements": [[x, int(E.lift_x(x)[1])] for x in xs],
            "column_xs": xs, "stream": "phifb{j}"}


def fb_phi_j1728(inst: dict) -> dict:
    """Union of complete phi x-orbits {x, -x}; FB_size = 2*ceil(B/2)."""
    E = EllipticCurve(inst["p"], inst["a"], inst["b"])
    p, seed = inst["p"], inst["seed"]
    B = math.isqrt(inst["n"]) + (1 if math.isqrt(inst["n"]) ** 2 < inst["n"] else 0)
    n_orbits = ceil_div(B, 2)
    xs: list[int] = []
    used: set[int] = set()
    j = 0
    while len(xs) < 2 * n_orbits and j < 200 * n_orbits + 1000:
        x = _seed_int(seed, f"phi4fb{j}") % p
        j += 1
        orbit = [x, (-x) % p]
        if len(set(orbit)) < 2 or any(o in used for o in orbit):
            continue
        if any(E.lift_x(o) is None for o in orbit):
            continue  # never happens for p=1 mod 4; audited below
        xs.extend(orbit)
        used.update(orbit)
    return {"arm": "phi_invariant", "family": "j1728", "B": B, "r": 2,
            "column_kind": "x", "n_orbits": n_orbits,
            "elements": [[x, int(E.lift_x(x)[1])] for x in xs],
            "column_xs": xs, "stream": "phi4fb{j}"}


def fb_neg_generic(inst: dict) -> dict:
    """Union of negation orbits {(x,y),(x,-y)} on signed points; cols = points."""
    E = EllipticCurve(inst["p"], inst["a"], inst["b"])
    p, seed = inst["p"], inst["seed"]
    B = math.isqrt(inst["n"]) + (1 if math.isqrt(inst["n"]) ** 2 < inst["n"] else 0)
    n_orbits = ceil_div(B, 2)
    pts: list[list[int]] = []
    used: set[int] = set()
    j = 0
    while len(pts) < 2 * n_orbits and j < 200 * n_orbits + 1000:
        x = _seed_int(seed, f"negfb{j}") % p
        j += 1
        if x in used:
            continue
        pt = E.lift_x(x)
        if pt is None or pt[1] == 0:
            continue
        y = min(pt[1], p - pt[1])  # canonical sign for the first orbit member
        pts.extend([[x, y], [x, (p - y) % p]])
        used.add(x)
    return {"arm": "negation_orbit_generic", "family": "generic", "B": B, "r": 2,
            "column_kind": "point", "n_orbits": n_orbits,
            "elements": pts, "column_xs": [pt[0] for pt in pts],
            "stream": "negfb{j}"}


def fb_random(inst: dict, n_cols: int, column_kind: str) -> dict:
    """Random non-orbit factor base, same curve and identical column count/kind."""
    E = EllipticCurve(inst["p"], inst["a"], inst["b"])
    p, seed = inst["p"], inst["seed"]
    B = math.isqrt(inst["n"]) + (1 if math.isqrt(inst["n"]) ** 2 < inst["n"] else 0)
    pts: list[list[int]] = []
    j = 0
    if column_kind == "x":
        seen: set[int] = set()
        while len(pts) < n_cols and j < 50 * n_cols + 1000:
            x = _seed_int(seed, f"rfb{j}") % p
            j += 1
            if x in seen:
                continue
            pt = E.lift_x(x)
            if pt is None:
                continue
            seen.add(x)
            pts.append([x, int(pt[1])])
    else:
        seenp: set[tuple[int, int]] = set()
        while len(pts) < n_cols and j < 50 * n_cols + 1000:
            x = _seed_int(seed, f"rfb{j}") % p
            j += 1
            pt = E.lift_x(x)
            if pt is None:
                continue
            y = pt[1] if _seed_int(seed, f"rfbs{j}") % 2 == 0 else (p - pt[1]) % p
            if (x, y) in seenp:
                continue
            seenp.add((x, y))
            pts.append([x, int(y)])
    return {"arm": "random_baseline", "family": inst["family"], "B": B,
            "r": None, "column_kind": column_kind, "n_orbits": None,
            "elements": pts, "column_xs": [q[0] for q in pts], "stream": "rfb{j}"}


def fb_ap(inst: dict) -> dict:
    """EV-STR-001 AP factor base: first B liftable x >= 0, canonical y, ordered by x."""
    E = EllipticCurve(inst["p"], inst["a"], inst["b"])
    p = inst["p"]
    n = inst["n"]
    B = math.isqrt(n) + (1 if math.isqrt(n) ** 2 < n else 0)
    pts: list[list[int]] = []
    x = 0
    while len(pts) < B and x < p:
        pt = E.lift_x(x)
        if pt is not None:
            y = min(pt[1], p - pt[1])
            pts.append([x, int(y)])
        x += 1
    return {"arm": "ap_benchmark", "family": inst["family"], "B": B, "r": None,
            "column_kind": "x_interval", "n_orbits": None,
            "elements": pts, "column_xs": [q[0] for q in pts],
            "x_max": pts[-1][0], "stream": "x-interval (EV-STR-001)"}


def orbit_audit(fb: dict, inst: dict) -> dict:
    """Orbit-closure audit: phi(F) = F exactly, orbit lengths, completeness."""
    p = inst["p"]
    r = fb["r"]
    cols = fb["column_xs"]
    colset = set(cols)
    audit = {"fb_sha256": sha256_obj(fb["elements"]), "n_columns": len(cols),
             "duplicates": len(cols) - len(colset)}
    if fb["arm"] == "phi_invariant" and fb["family"] == "j0":
        z = inst["zeta3"]
        closed = all(((z * x) % p) in colset for x in cols)
        lens = [len({cols[3*t], cols[3*t+1], cols[3*t+2]}) for t in range(len(cols)//3)]
        audit.update({"phi_F_eq_F_exact": bool(closed), "orbit_lengths": sorted(set(lens)),
                      "complete_orbits": sum(1 for L in lens if L == 3),
                      "total_orbits": len(lens)})
    elif fb["arm"] == "phi_invariant" and fb["family"] == "j1728":
        closed = all(((-x) % p) in colset for x in cols)
        lens = [len({cols[2*t], cols[2*t+1]}) for t in range(len(cols)//2)]
        audit.update({"phi_F_eq_F_exact": bool(closed), "orbit_lengths": sorted(set(lens)),
                      "complete_orbits": sum(1 for L in lens if L == 2),
                      "total_orbits": len(lens)})
    elif fb["arm"] == "negation_orbit_generic":
        pts = fb["elements"]
        closed = all(pts[2*t][0] == pts[2*t+1][0] and
                     (pts[2*t][1] + pts[2*t+1][1]) % p == 0
                     for t in range(len(pts)//2))
        audit.update({"phi_F_eq_F_exact": bool(closed), "orbit_lengths": [2],
                      "complete_orbits": len(pts)//2, "total_orbits": len(pts)//2})
    else:
        audit.update({"phi_F_eq_F_exact": None, "orbit_lengths": None,
                      "complete_orbits": None, "total_orbits": None})
    cf = (audit["complete_orbits"] / audit["total_orbits"]) if audit["total_orbits"] else None
    audit["orbit_completeness_fraction"] = cf
    return audit


# ------------------------------------------------------------- numpy helpers
def npowmod(base: np.ndarray, e: int, p: int) -> np.ndarray:
    """Vectorized base**e % p for int64 arrays (values < p < 2^25, p^2 < 2^50)."""
    result = np.ones_like(base)
    b = base.copy()
    while e:
        if e & 1:
            result = (result * b) % p
        b = (b * b) % p
        e >>= 1
    return result


# ------------------------------------------------------- enumeration engine
class CellResult(dict):
    pass


def enumeration_engine(E: EllipticCurve, n: int, elements: list[list[int]],
                       targets: list[dict], harvest_pool: list[dict],
                       need_rows: int, r: int | None, phi_map,
                       eval_cap: int, time_cap: float, t0: float,
                       guard: BudgetGuard, log,
                       membership: set | None = None) -> CellResult:
    """Enumeration-assisted relation collection (MTIC protocol) + hit rates.

    Pair-sum x-table (numpy, vectorized Fermat inversion) + per-target probes:
    for each target R and column point G, x(R-G) is looked up in the pair-sum
    table; a match yields an exact signed relation R = G + s1*G_i + s2*G_j
    resolved and verified with harness/toycurve arithmetic.
    membership: for point-column factor bases, the exact set of FB points;
    a resolved relation counts only when all three signed summands are exact
    FB members (x-hit with sign-unresolvable summands is NOT a decomposition
    over a signed-point FB). None for x-coordinate columns (sign is free
    bookkeeping there).
    """
    p = E.p
    C = len(elements)
    xs = np.array([e[0] for e in elements], dtype=np.int64)
    ys = np.array([e[1] for e in elements], dtype=np.int64)
    pts = [tuple(e) for e in elements]
    evals = {"pair_x_evaluations": 0, "probe_x_evaluations": 0}
    censored = {"eval_cap_hit": False, "time_cap_hit": False}

    # ---- pair-sum x table: x(G_i + G_j) and x(G_i - G_j) for all i < j
    n_pairs = C * (C - 1) // 2
    tx = np.empty(2 * n_pairs, dtype=np.int64)
    ti = np.empty(2 * n_pairs, dtype=np.int32)
    tj = np.empty(2 * n_pairs, dtype=np.int32)
    ts = np.empty(2 * n_pairs, dtype=np.int8)  # 0: G_i+G_j, 1: G_i-G_j
    off = 0
    skipped_same_x = 0
    for i in range(C - 1):
        m = C - 1 - i
        dx = (xs[i + 1:] - xs[i]) % p
        zero = dx == 0
        if zero.any():
            dx = dx.copy()
            dx[zero] = 1
        inv = npowmod(dx, p - 2, p)
        lam1 = ((ys[i + 1:] - ys[i]) * inv) % p
        xp1 = (lam1 * lam1 - xs[i] - xs[i + 1:]) % p
        lam2 = ((-(ys[i + 1:] + ys[i])) * inv) % p
        xp2 = (lam2 * lam2 - xs[i] - xs[i + 1:]) % p
        jj = np.arange(i + 1, C, dtype=np.int32)
        tx[off:off + m] = xp1
        ti[off:off + m] = i
        tj[off:off + m] = jj
        ts[off:off + m] = 0
        tx[off + m:off + 2 * m] = xp2
        ti[off + m:off + 2 * m] = i
        tj[off + m:off + 2 * m] = jj
        ts[off + m:off + 2 * m] = 1
        if zero.any():
            # same-x pair (point arm only): sums are O / 2*G_i; excluded (recorded)
            skipped_same_x += int(zero.sum()) * 2
        off += 2 * m
        evals["pair_x_evaluations"] += 2 * m
        if i % 64 == 0:
            guard.check("pair-table")
            if evals["pair_x_evaluations"] > eval_cap or time.time() - t0 > time_cap:
                censored["eval_cap_hit"] = evals["pair_x_evaluations"] > eval_cap
                censored["time_cap_hit"] = time.time() - t0 > time_cap
                tx, ti, tj, ts = tx[:off], ti[:off], tj[:off], ts[:off]
                break
    order = np.argsort(tx, kind="stable")
    tx, ti, tj, ts = tx[order], ti[order], tj[order], ts[order]
    distinct_x = int(np.unique(tx).size)
    evals["total_tuple_evaluations"] = evals["pair_x_evaluations"]

    resolve_stats = {"resolved_ok": 0, "resolve_reject": 0}

    def resolve(Rpt, g, k):
        """Resolve table hit k for probe (R, column g) into an exact relation."""
        i, j, s = int(ti[k]), int(tj[k]), int(ts[k])
        Gi, Gj, Gg = pts[i], pts[j], pts[g]
        T = E.add(Gi, Gj) if s == 0 else E.add(Gi, E.negate(Gj))
        Rm = E.add(Rpt, E.negate(Gg))          # R - G
        if T is None or Rm is None:
            resolve_stats["resolve_reject"] += 1
            return None
        if T == Rm:
            summands = [Gg, Gi, Gj]
        elif E.negate(T) == Rm:
            summands = [Gg, E.negate(Gi), E.negate(Gj)] if s == 0 else \
                       [Gg, E.negate(Gi), Gj]
        else:
            resolve_stats["resolve_reject"] += 1
            return None
        # exact FB membership for point-column factor bases
        if membership is not None and any(s_ not in membership for s_ in summands):
            resolve_stats["resolve_reject"] += 1
            return None
        # degenerate if any two summands cancel or repeat (0/1 matrix rows)
        a_, b_, c_ = summands
        if a_ == b_ or a_ == c_ or b_ == c_:
            resolve_stats["resolve_reject"] += 1
            return None
        if E.add(a_, b_) is None or E.add(a_, c_) is None or E.add(b_, c_) is None:
            resolve_stats["resolve_reject"] += 1
            return None
        # exact check with harness arithmetic (independent of the x-engine)
        if E.add(E.add(a_, b_), c_) != Rpt:
            resolve_stats["resolve_reject"] += 1
            return None
        resolve_stats["resolved_ok"] += 1
        return summands

    def probe_target(Rpt, collect: bool):
        """Full probe pass of one target. Returns (hit_count, relations)."""
        xr, yr = Rpt
        dx = (xs - xr) % p
        zero = dx == 0
        if zero.any():
            dx = dx.copy()
            dx[zero] = 1
        inv = npowmod(dx, p - 2, p)
        lam = ((-(ys + yr)) * inv) % p
        xp = (lam * lam - xr - xs) % p
        evals["probe_x_evaluations"] += C
        idx = np.searchsorted(tx, xp)
        hit = 0
        rels = []
        for g in range(C):
            k0 = idx[g]
            if k0 >= tx.size or tx[k0] != xp[g]:
                continue
            k = k0
            rel = None
            while k < tx.size and tx[k] == xp[g]:
                rel = resolve(Rpt, g, k)
                if rel is not None:
                    break
                k += 1
            if rel is not None:
                hit += 1
                if collect:
                    rels.append((g, rel))
        return hit, rels

    # ---- hit-rate test: 200 decomposition-test targets (frozen count)
    hit_results = []
    hits_total = 0
    for t in targets:
        Rpt = tuple(t["R"])
        h, _ = probe_target(Rpt, collect=False)
        hit_results.append({"target_index": t["index"], "a": t["a"], "b": t["b"],
                            "probe_hits": int(h), "decomposes": h > 0})
        hits_total += 1 if h > 0 else 0
        guard.check("hit-test")
        if time.time() - t0 > time_cap or evals["probe_x_evaluations"] + \
                evals["pair_x_evaluations"] > eval_cap:
            censored["time_cap_hit"] = time.time() - t0 > time_cap
            censored["eval_cap_hit"] = evals["probe_x_evaluations"] + \
                evals["pair_x_evaluations"] > eval_cap
            break
    hit_rate = hits_total / len(hit_results) if hit_results else None

    # ---- relation harvest: iterate pool until enough distinct base relations
    base_relations: list[dict] = []
    seen_keys: set = set()
    duplicates = 0
    degenerate = 0
    targets_used = 0
    need_base = ceil_div(need_rows, r) if r else need_rows
    for t in harvest_pool:
        if len(base_relations) >= need_base:
            break
        Rpt = tuple(t["R"])
        if Rpt is None:
            continue
        targets_used += 1
        _, rels = probe_target(Rpt, collect=True)
        for g, summands in rels:
            key = (t["index"], frozenset(summands))
            if key in seen_keys:
                duplicates += 1
                continue
            seen_keys.add(key)
            base_relations.append({"target_index": t["index"], "target": list(Rpt),
                                   "summands": [list(s) for s in summands]})
        guard.check("harvest")
        if time.time() - t0 > time_cap or \
                evals["probe_x_evaluations"] + evals["pair_x_evaluations"] > eval_cap:
            censored["time_cap_hit"] = time.time() - t0 > time_cap
            censored["eval_cap_hit"] = True
            break

    return CellResult({
        "evals": evals, "censored": censored, "skipped_same_x_pairs": skipped_same_x,
        "resolve_stats": resolve_stats,
        "pair_table": {"entries": int(tx.size), "distinct_x": distinct_x,
                       "coverage_of_Fp": distinct_x / p},
        "hit_test": {"n_targets": len(hit_results), "hits": hits_total,
                     "hit_rate": hit_rate, "per_target": hit_results},
        "harvest": {"pool_size": len(harvest_pool), "targets_used": targets_used,
                    "base_relations": len(base_relations), "duplicates": duplicates,
                    "degenerate_excluded": degenerate, "needed_base": need_base},
        "base_relations": base_relations,
    })


def phi_image_point(family: str, pt, inst: dict):
    if pt is None:
        return None
    p = inst["p"]
    if family == "j0":
        return ((inst["zeta3"] * pt[0]) % p, pt[1])
    if family == "j1728":
        return ((-pt[0]) % p, (inst["i_sqrt"] * pt[1]) % p)
    raise ValueError(family)


def assemble_matrix(E: EllipticCurve, inst: dict, fb: dict,
                    base_relations: list[dict], need_rows: int, log,
                    phi_fn=None) -> dict:
    """Assemble the square relation matrix with orbit-blocked rows/columns.

    GLV arms (column_kind x): row blocks (rel, phi(rel), phi^2(rel)) for r=3,
    (rel, phi(rel)) for r=2; columns are x-coordinate orbit blocks.
    Generic arm (column_kind point): row blocks (rel, -rel); columns are
    negation-orbit point pairs.
    Random arm: first need_rows distinct relations, collection order.
    phi_fn: point image map of the arm's endomorphism (negation for generic).
    """
    p, family = inst["p"], inst["family"]
    col_index = {}
    for c, e in enumerate(fb["elements"]):
        key = e[0] if fb["column_kind"] == "x" else (e[0], e[1])
        col_index[key] = c
    r = fb["r"]

    def row_of(rel):
        idx = []
        for s in rel["summands"]:
            key = s[0] if fb["column_kind"] == "x" else (s[0], s[1])
            if key not in col_index:
                return None
            idx.append(col_index[key])
        if len(set(idx)) != len(idx):
            return None
        return sorted(idx)

    rows: list[list[int]] = []
    row_targets: list[list[int]] = []
    row_summands: list[list] = []
    blocks = 0
    if r:
        for rel in base_relations:
            if len(rows) + r > need_rows:
                break
            chain = [rel]
            ok = True
            for k in range(1, r):
                img = {"target": list(phi_fn(tuple(chain[-1]["target"]))),
                       "summands": [list(phi_fn(tuple(s)))
                                    for s in chain[-1]["summands"]]}
                chain.append(img)
            blk_rows = []
            for c_rel in chain:
                rr = row_of(c_rel)
                if rr is None:
                    ok = False
                    break
                blk_rows.append((rr, c_rel))
            if not ok:
                continue
            for rr, c_rel in blk_rows:
                rows.append(rr)
                row_targets.append(c_rel["target"])
                row_summands.append(c_rel["summands"])
            blocks += 1
    else:
        for rel in base_relations:
            if len(rows) >= need_rows:
                break
            rr = row_of(rel)
            if rr is None:
                continue
            rows.append(rr)
            row_targets.append(rel["target"])
            row_summands.append(rel["summands"])
            blocks += 1

    return {"R": len(rows), "B": len(fb["elements"]), "rows": rows,
            "row_targets": row_targets, "row_summands": row_summands,
            "row_blocks": blocks, "square": len(rows) == len(fb["elements"]),
            "column_xs": fb["column_xs"], "column_kind": fb["column_kind"]}


def verify_matrix_relations(inst: dict, matrix: dict) -> dict:
    """Independent certificate verification: every matrix row's recorded
    summands must sum to its recorded target (harness/toycurve recompute)."""
    E = EllipticCurve(inst["p"], inst["a"], inst["b"])
    checked = 0
    failed = 0
    for target, summands in zip(matrix["row_targets"], matrix["row_summands"]):
        acc = None
        for s in summands:
            acc = E.add(acc, tuple(s))
        if acc == tuple(target):
            checked += 1
        else:
            failed += 1
    return {"rows_checked": checked, "rows_failed": failed,
            "all_verified": failed == 0,
            "kind": "decomposition", "verifier": "independent-recompute"}


# ------------------------------------------------------------------ targets
def make_targets(inst: dict, count: int, tag: str) -> list[dict]:
    """Seeded uniform targets R = a*P + b*Q (recorded), skipping R = O."""
    E = EllipticCurve(inst["p"], inst["a"], inst["b"])
    P, Q, n = tuple(inst["P"]), tuple(inst["Q"]), inst["n"]
    out = []
    j = 0
    while len(out) < count:
        a = _seed_int(inst["seed"], f"{tag}a{j}") % n
        b = _seed_int(inst["seed"], f"{tag}b{j}") % n
        j += 1
        R = E.add(E.mul(a, P), E.mul(b, Q))
        if R is None:
            continue
        out.append({"index": len(out), "a": int(a), "b": int(b), "R": list(R)})
    return out


# ------------------------------------------------------------- displacement
def block_cyclic_perm(B: int, r: int) -> np.ndarray:
    pi = np.arange(B, dtype=np.int64)
    for t in range(B // r):
        base = t * r
        pi[base:base + r] = np.roll(pi[base:base + r], -1)
    return pi


def displacement_rank(rows: list[list[int]], B: int, n: int, pi: np.ndarray) -> dict:
    """alpha = rank(M - Z M Z^T) over F_n; Z the permutation pi.
    (Z M Z^T)[i][j] = M[pi^{-1} i][pi^{-1} j]. Exact dense modular GE."""
    R = len(rows)
    inv_pi = np.empty_like(pi)
    inv_pi[pi] = np.arange(pi.size)
    D = np.zeros((R, B), dtype=np.int64)
    for i, rr in enumerate(rows):
        for j in rr:
            D[i, j] += 1
    for a, rr in enumerate(rows):
        pa = pi[a]
        for b in rr:
            D[pa, pi[b]] -= 1
    D %= n
    nnz_D = int((D != 0).sum())
    alpha = rank_mod(D, n)
    return {"alpha": int(alpha), "R": R, "B": B, "min_R_B": min(R, B),
            "alpha_over_min": alpha / min(R, B), "displacement_nnz": nnz_D}


_ELIM_CHUNK = 512


def _eliminate_below(A: np.ndarray, rank: int, col: int, n: int) -> None:
    """Eliminate column `col` below pivot row `rank` in chunked, buffer-reusing
    vector ops (whole-submatrix temporaries fragmented the darwin allocator to
    6.9 GB RSS on a 10809 x 3318 pool; chunked buffers keep peak ~ A + 50 MB)."""
    R = A.shape[0]
    if rank + 1 >= R:
        return
    factors = A[rank + 1:, col]
    mask = factors != 0
    if not mask.any():
        return
    idx = np.nonzero(mask)[0] + rank + 1
    fac = factors[mask]
    B = A.shape[1]
    buf = np.empty((min(_ELIM_CHUNK, idx.size), B), dtype=np.int64)
    for start in range(0, idx.size, _ELIM_CHUNK):
        stop = min(start + _ELIM_CHUNK, idx.size)
        kk = stop - start
        rows_idx = idx[start:stop]
        np.multiply(fac[start:stop][:, None], A[rank], out=buf[:kk])
        A[rows_idx] = (A[rows_idx] - buf[:kk]) % n


def rank_mod(A: np.ndarray, n: int) -> int:
    """Exact rank over F_n (n prime) via dense Gaussian elimination in int64."""
    R, C = A.shape
    rank = 0
    for col in range(C):
        if rank >= R:
            break
        colv = A[rank:, col]
        nz = np.nonzero(colv)[0]
        if nz.size == 0:
            continue
        piv = rank + int(nz[0])
        if piv != rank:
            A[[rank, piv]] = A[[piv, rank]]
        inv = pow(int(A[rank, col]), -1, n)
        A[rank] = (A[rank] * inv) % n
        _eliminate_below(A, rank, col, n)
        rank += 1
    return rank


def full_rank_row_selection(rows: list[list[int]], B: int, n: int,
                            orig_index_offset: int = 0) -> tuple[list[int], int, int]:
    """Greedy full-rank square subsystem (EV-STR-001 precedent): Gaussian
    elimination with original-index tracking; returns (selected row indices,
    rank achieved, matrix row count). The selected original rows form a row
    basis of the input matrix (indices into `rows`)."""
    R = len(rows)
    A = np.zeros((R, B), dtype=np.int64)
    for i, rr in enumerate(rows):
        for j in rr:
            A[i, j] = (A[i, j] + 1) % n
    orig = np.arange(R, dtype=np.int64)
    selected: list[int] = []
    rank = 0
    for col in range(B):
        if rank >= R:
            break
        colv = A[rank:, col]
        nz = np.nonzero(colv)[0]
        if nz.size == 0:
            continue
        piv = rank + int(nz[0])
        if piv != rank:
            A[[rank, piv]] = A[[piv, rank]]
            orig[[rank, piv]] = orig[[piv, rank]]
        inv = pow(int(A[rank, col]), -1, n)
        A[rank] = (A[rank] * inv) % n
        _eliminate_below(A, rank, col, n)
        selected.append(int(orig[rank]))
        rank += 1
    return selected, rank, R


def commutation_residual(rows: list[list[int]], B: int, pi: np.ndarray) -> dict:
    """||M*Phi - Phi*M||_0 with pre-registered orbit/sign bookkeeping.
    (M Phi)[i][j] = M[i][pi(j)]; (Phi M)[i][j] = M[pi^{-1}(i)][j]."""
    inv_pi = np.empty_like(pi)
    inv_pi[pi] = np.arange(pi.size)
    S = set()
    for i, rr in enumerate(rows):
        for j in rr:
            S.add((i, j))
    MP = {(i, int(pi[j])) for (i, j) in S}
    PM = {(int(inv_pi[i]), j) for (i, j) in S}
    sym = MP.symmetric_difference(PM)
    sample = sorted(sym)[:100]
    return {"residual_l0": len(sym), "sample_entries": [list(s) for s in sample],
            "bookkeeping": ("entries are 0/1; residual counts indices where the "
                            "phi row-shift and phi column-shift disagree; the "
                            "pre-registered expectation is 0 under exact orbit "
                            "closure and block ordering")}


# ------------------------------------------------------------------ Wiedemann
def berlekamp_massey(s, q, counter):
    C = [1]
    Bv = [1]
    L = 0
    m = 1
    b = 1
    for nn in range(len(s)):
        d = s[nn] % q
        for i in range(1, L + 1):
            d = (d + C[i] * s[nn - i]) % q
        counter["bm_mul_add"] += L  # L mul-adds for this discrepancy computation
        if d == 0:
            m += 1
        elif 2 * L <= nn:
            T = C[:]
            coef = d * pow(b, -1, q) % q
            need = m + len(Bv)
            if len(C) < need:
                C += [0] * (need - len(C))
            for j in range(len(Bv)):
                C[j + m] = (C[j + m] - coef * Bv[j]) % q
            counter["bm_mul_add"] += len(Bv)
            L = nn + 1 - L
            Bv = T
            b = d
            m = 1
        else:
            coef = d * pow(b, -1, q) % q
            need = m + len(Bv)
            if len(C) < need:
                C += [0] * (need - len(C))
            for j in range(len(Bv)):
                C[j + m] = (C[j + m] - coef * Bv[j]) % q
            counter["bm_mul_add"] += len(Bv)
            m += 1
    return C, L


def wiedemann_solve(rows: list[list[int]], Bsz: int, q: int, seed: int,
                    consistent_rhs: bool = False):
    """Solve M x = b over F_q (M as list of col-index lists, 0/1 entries).
    Field-op counts instrumented. Adapted from EXP-STR-001 str1_ap_matrix.sage.
    consistent_rhs=True: b = M*x0 with x0 seeded-random (recorded), so the
    system is solvable even when M is rank-deficient (weight-3 0/1 matrices
    are generically ~5% rank deficient at toy sizes, measured); M|im(M) is
    invertible for a random matrix whp (rank-nullity complementary subspaces),
    so the Krylov minpoly keeps a nonzero constant term.
    """
    rng_state = {"v": seed}

    def rnd():
        rng_state["v"] = (rng_state["v"] * 1103515245 + 12345) & 0x7fffffff
        return rng_state["v"] % q

    counter = {"matvec_field_ops": 0, "dot_field_ops": 0, "bm_mul_add": 0,
               "combine_field_ops": 0, "matvecs": 0}
    nnz = sum(len(r) for r in rows)

    def matvec(v):
        counter["matvecs"] += 1
        counter["matvec_field_ops"] += nnz
        out = []
        for cols in rows:
            acc = 0
            for j in cols:
                acc += v[j]
            out.append(acc % q)
        return out

    def dot(u, v):
        counter["dot_field_ops"] += 2 * Bsz
        return sum(u[j] * v[j] for j in range(Bsz)) % q

    t_start = time.time()
    for attempt in range(1, 6):
        u = [rnd() for _ in range(Bsz)]
        x0 = [rnd() for _ in range(Bsz)] if consistent_rhs else None
        b = matvec(x0) if consistent_rhs else [rnd() for _ in range(Bsz)]
        v = b[:]
        s = []
        for _ in range(2 * Bsz + 1):
            s.append(dot(u, v))
            v = matvec(v)
        C, L = berlekamp_massey(s, q, counter)
        if L == 0 or C[L] % q == 0:
            continue
        powers = [b[:]]
        for _ in range(1, L):
            powers.append(matvec(powers[-1]))
        w = [0] * Bsz
        for i in range(L):
            ck = C[i] % q
            if ck:
                pv = powers[L - 1 - i]
                for j in range(Bsz):
                    w[j] = (w[j] + ck * pv[j]) % q
                counter["combine_field_ops"] += Bsz
        inv_c = pow(C[L] % q, -1, q)
        x = [(-w[j] * inv_c) % q for j in range(Bsz)]
        # verification matvec
        chk = matvec(x)
        ok = chk == [bb % q for bb in b]
        if ok:
            counter["total_field_ops"] = (counter["matvec_field_ops"] +
                                          counter["dot_field_ops"] +
                                          counter["bm_mul_add"] +
                                          counter["combine_field_ops"])
            return x, {"converged": True, "attempts": attempt, "minpoly_deg": L,
                       "seconds": time.time() - t_start, "verified": True,
                       "nnz": nnz, "field_ops": dict(counter), "b": b,
                       "consistent_rhs": consistent_rhs,
                       "wiedemann_model_ops": 2 * Bsz * nnz}
    counter["total_field_ops"] = (counter["matvec_field_ops"] +
                                  counter["dot_field_ops"] +
                                  counter["bm_mul_add"] +
                                  counter["combine_field_ops"])
    return None, {"converged": False, "attempts": 5, "seconds": time.time() - t_start,
                  "verified": False, "nnz": nnz, "field_ops": dict(counter),
                  "consistent_rhs": consistent_rhs,
                  "wiedemann_model_ops": 2 * Bsz * nnz,
                  "entry_status": "resource_exhaustion"}


# -------------------------------------------------------------------- Wilson
def wilson_ci(hits: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [None, None]
    phat = hits / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = (z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))) / denom
    return [max(0.0, center - half), min(1.0, center + half)]


# ------------------------------------------------------------------ BSGS
def bsgs_solve(E: EllipticCurve, P, R, n: int) -> dict:
    """BSGS dlog R = k*P with group-op counting (table + walk + verify)."""
    m = math.isqrt(n) + 1
    ops = {"adds": 0, "lookups": 0}
    table = {}
    baby = None
    for j in range(m):
        table[baby] = j
        baby = E.add(baby, P)
        ops["adds"] += 1
    # m*P via double-and-add, counted
    k = m
    result = None
    addend = P
    while k:
        if k & 1:
            result = E.add(result, addend)
            ops["adds"] += 1
        addend = E.add(addend, addend)
        ops["adds"] += 1
        k >>= 1
    mP = result
    neg_mP = E.negate(mP)
    ops["adds"] += 1
    T = R
    found = None
    for i in range(m + 1):
        ops["lookups"] += 1
        if T in table:
            found = (i * m + table[T]) % n
            break
        T = E.add(T, neg_mP)
        ops["adds"] += 1
    if found is None:
        return {"solved": False, "group_operations": ops["adds"] + ops["lookups"],
                "table_entries": m}
    # verify
    k = found
    vres = None
    addend = P
    kk = k
    while kk:
        if kk & 1:
            vres = E.add(vres, addend)
            ops["adds"] += 1
        addend = E.add(addend, addend)
        ops["adds"] += 1
        kk >>= 1
    ok = vres == R
    return {"solved": ok, "k": k if ok else None,
            "group_operations": ops["adds"] + ops["lookups"],
            "table_entries": m, "verified": ok}


def rho_solve_target(inst: dict, target: dict) -> dict:
    """harness/rho.py solve of R = k_R * P (public data only); k_R cross-checked
    against the recorded (a, b) and the frozen secret k: k_R = a + b*k mod n."""
    E = EllipticCurve(inst["p"], inst["a"], inst["b"])
    R = tuple(target["R"])
    ecd = ECDLPInstance(p=inst["p"], a=inst["a"], b=inst["b"], P=tuple(inst["P"]),
                        Q=R, n=inst["n"], k=0, field_bits=inst["field_bits"],
                        seed=inst["seed"])
    res = rho_mod.solve(ecd)
    out = {"target_index": target["index"], "a": target["a"], "b": target["b"],
           "solved": res.solved, "group_operations": res.group_operations,
           "total_group_operations": res.total_group_operations,
           "iterations": res.iterations, "reason": res.reason}
    if res.solved:
        k_R = res.k
        verified = E.mul(k_R, tuple(inst["P"])) == R
        cross = (target["a"] + target["b"] * inst["k"]) % inst["n"] == k_R
        out.update({"k_R": k_R, "verified_recompute": verified,
                    "crosscheck_ab": cross})
        out["certificate"] = {"kind": "discrete_log",
                              "statement": {"curve": {"p": inst["p"], "a": inst["a"],
                                                      "b": inst["b"]},
                                            "P": list(inst["P"]), "Q": list(R),
                                            "k": k_R},
                              "verified": verified and cross,
                              "verifier": "independent-recompute + (a+bk) cross-check"}
    return out


# --------------------------------------------------------------- frozen I/O
def write_yaml(path: str, obj):
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, sort_keys=False)


def read_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def verify_frozen_instances() -> dict:
    doc = read_yaml(FROZEN_INSTANCES)
    cells = doc["cells"]
    ok_cells = all(sha256_obj({k: v for k, v in c.items() if k != "sha256"}) == c["sha256"]
                   for c in cells)
    content = sha256_obj([c["sha256"] for c in cells])
    return {"file": FROZEN_INSTANCES, "per_cell_sha256_ok": ok_cells,
            "content_sha256_ok": content == doc["content_sha256"],
            "n_cells": len(cells)}


def verify_frozen_factorbases() -> dict:
    doc = read_yaml(FROZEN_FACTORBASES)
    bases = doc["bases"]
    ok = all(sha256_obj({k: v for k, v in b.items() if k != "sha256"}) == b["sha256"]
             for b in bases)
    content = sha256_obj([b["sha256"] for b in bases])
    return {"file": FROZEN_FACTORBASES, "per_base_sha256_ok": ok,
            "content_sha256_ok": content == doc["content_sha256"],
            "n_bases": len(bases)}


def get_cell(instances_doc: dict, family: str, bits: int) -> dict:
    for c in instances_doc["cells"]:
        if c["family"] == family and c["field_bits"] == bits:
            return c
    raise KeyError((family, bits))


def get_fb(fb_doc: dict, family: str, bits: int, arm: str) -> dict:
    for b in fb_doc["bases"]:
        if b["family"] == family and b["field_bits"] == bits and b["arm"] == arm:
            return b
    raise KeyError((family, bits, arm))


# ------------------------------------------------------------ run record I/O
def write_run_record(run_id: str, status: str, command: str, started: float,
                     finished: float, seed_record, parameters: dict,
                     metrics: dict, raw: dict, summary_metrics: dict,
                     valid: bool, invalid_reason, certificate: dict,
                     deviations: list, anomalies: list, out_root: str | None = None,
                     extra_artifacts: dict | None = None):
    """Emit the frozen required_artifacts set plus byte-identical docs-style
    duplicates (naming deviation recorded in the manifest)."""
    root = out_root or EXP_DIR
    run_dir = os.path.join(root, "runs", run_id)
    if os.path.exists(run_dir):
        raise FileExistsError(f"{run_dir} exists; run records are immutable")
    os.makedirs(run_dir)
    commit, dirty, dirty_basis = git_state()
    env = environment()
    rss = peak_rss_bytes()
    naming_deviation = ("spec required_artifacts name raw.json/summary.json/stdout.txt/"
                        "stderr.txt; docs/evidence-and-reproducibility.md names "
                        "raw-result.json/stdout.log/stderr.log; both sets emitted "
                        "byte-identical")
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": EXP_ID,
            "status": status,
            "code": {"commit": commit, "dirty": dirty, "command": command,
                     "dirty_basis": dirty_basis},
            "inference": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": "none (deterministic harness execution)",
                "reasoning_effort": None,
                "fallback_used": False,
                "adapter_version": None,
            },
            "environment": env,
            "inputs": {"curve_id": parameters.get("curve_id"),
                       "seed": seed_record,
                       "parameters": parameters},
            "timing": {"started_at": iso(started), "finished_at": iso(finished),
                       "wall_seconds": round(finished - started, 6)},
            "resources": {"peak_rss_bytes": int(rss), "cpu_seconds": cpu_seconds(),
                          "memory_enforcement": ("darwin rejects setrlimit(RLIMIT_AS); "
                                                 "4 GB cap enforced post-hoc against "
                                                 "measured peak RSS plus proactive "
                                                 "self-abort at 3.75 GB"),
                          "memory_cap_bytes": RSS_LIMIT_BYTES,
                          "memory_cap_exceeded": bool(rss > RSS_LIMIT_BYTES)},
            "result": {"metrics": metrics, "valid": valid,
                       "invalid_reason": invalid_reason,
                       "certificate": certificate},
            "protocol_deviations": deviations,
            "anomalies": anomalies,
            "artifacts": dict({
                "command": "command.txt",
                "environment": "environment.json",
                "stdout": "stdout.txt",
                "stderr": "stderr.txt",
                "raw": "raw.json",
                "summary": "summary.json",
                "duplicates_byte_identical": ["stdout.log", "stderr.log",
                                              "raw-result.json"],
                "naming_deviation": naming_deviation,
            }, **(extra_artifacts or {})),
        }
    }
    raw_doc = {"run_id": run_id, "experiment_id": EXP_ID, "status": status,
               "metrics": metrics, "raw": raw,
               "protocol_deviations": deviations, "anomalies": anomalies,
               "validity": {"valid": valid, "invalid_reason": invalid_reason},
               "provenance": {"command": command, "git_commit": commit,
                              "dirty": dirty, "dirty_basis": dirty_basis,
                              "started_at": iso(started), "finished_at": iso(finished),
                              "wall_seconds": round(finished - started, 6),
                              "cpu_seconds": cpu_seconds(),
                              "peak_rss_bytes": int(rss),
                              "environment": env}}
    summary_doc = {"run_id": run_id, "experiment_id": EXP_ID, "status": status,
                   "valid": valid, "invalid_reason": invalid_reason,
                   "seeds": seed_record, "metrics": summary_metrics,
                   "wall_seconds": round(finished - started, 6),
                   "peak_rss_bytes": int(rss),
                   "protocol_deviations": deviations}
    stdout_text = raw.get("_stdout", "")
    stderr_text = raw.get("_stderr", "")
    raw_clean = {k: v for k, v in raw.items() if not k.startswith("_")}

    def w(name, content):
        with open(os.path.join(run_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    raw_json = json.dumps({**raw_doc, "raw": raw_clean}, indent=1, sort_keys=False,
                          default=str)
    w("manifest.yaml", yaml.safe_dump(manifest, sort_keys=False))
    w("command.txt", command + "\n")
    w("environment.json", json.dumps(env, indent=2, sort_keys=True))
    w("raw.json", raw_json)
    w("summary.json", json.dumps(summary_doc, indent=1, sort_keys=False, default=str))
    w("stdout.txt", stdout_text)
    w("stderr.txt", stderr_text)
    # byte-identical duplicates under the docs/evidence-and-reproducibility.md names
    w("stdout.log", stdout_text)
    w("stderr.log", stderr_text)
    w("raw-result.json", raw_json)
    return run_dir
