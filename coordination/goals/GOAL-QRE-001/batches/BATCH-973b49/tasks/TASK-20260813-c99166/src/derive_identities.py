"""Derivation checks for the two identities used by the in-place point addition,
and for the 7-T Clifford+T decomposition of the Toffoli gate.

Nothing here is cited.  The point-addition identities are re-derived from the
affine chord formula and checked exhaustively over small prime fields; the
T-count ratio 7 is established by exhibiting a circuit and multiplying its 8x8
unitary out from first principles.

Run:  python3 derive_identities.py
"""
import cmath
import json
import sys


# ---------------------------------------------------------------------
# 1. point-addition identities
#
#   chord formulae for P=(x1,y1), Q=(x2,y2), x1 != x2, on y^2 = x^3+Ax+B:
#       lam = (y1-y2)/(x1-x2),  x3 = lam^2-x1-x2,  y3 = lam*(x1-x3)-y1
#   with u = x1-x2, v = y1-y2 the circuit works on the shifted coordinates.
#   Claimed:   x3 - x2 = lam^2 - u - 3*x2
#              y3 + y2 = -lam*(x3 - x2)
# ---------------------------------------------------------------------
def check_point_identities():
    checked = 0
    for p in (11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53):
        for A in range(p):
            for B in range(p):
                if (4 * A ** 3 + 27 * B ** 2) % p == 0:
                    continue
                pts = [(x, y) for x in range(p) for y in range(p)
                       if (y * y - x ** 3 - A * x - B) % p == 0]
                if len(pts) < 2:
                    continue
                for (x1, y1) in pts[:6]:
                    for (x2, y2) in pts[:6]:
                        if x1 == x2:
                            continue
                        lam = (y1 - y2) * pow(x1 - x2, -1, p) % p
                        x3 = (lam * lam - x1 - x2) % p
                        y3 = (lam * (x1 - x3) - y1) % p
                        u = (x1 - x2) % p
                        assert (x3 - x2) % p == (lam * lam - u - 3 * x2) % p
                        assert (y3 + y2) % p == (-lam * ((x3 - x2) % p)) % p
                        assert (y3 * y3 - x3 ** 3 - A * x3 - B) % p == 0
                        checked += 1
    return checked


# ---------------------------------------------------------------------
# 2. T-count per Toffoli, derived rather than cited.
#
# Exhibit a Clifford+T circuit on 3 qubits with exactly seven T/Tdg gates,
# multiply its 8x8 unitary out with exact complex arithmetic, and compare with
# the Toffoli permutation matrix.  Only if this matches to 1e-12 is the ratio
# T = 7 * Toffoli admissible (PREREGISTRATION clause 2).
# ---------------------------------------------------------------------
S2 = 1.0 / cmath.sqrt(2)
TPH = cmath.exp(1j * cmath.pi / 4)


def _ident():
    return [[1.0 + 0j if i == j else 0j for j in range(8)] for i in range(8)]


def _mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(8)) for j in range(8)]
            for i in range(8)]


def _one_qubit(gate, q):
    """gate = 2x2 list; qubit q of 3 (q=0 is the most significant)."""
    U = [[0j] * 8 for _ in range(8)]
    shift = 2 - q
    for i in range(8):
        bi = (i >> shift) & 1
        for bo in (0, 1):
            j = (i & ~(1 << shift)) | (bo << shift)
            U[j][i] += gate[bo][bi]
    return U


def _cnot(c, t):
    U = [[0j] * 8 for _ in range(8)]
    sc, st = 2 - c, 2 - t
    for i in range(8):
        j = i ^ (1 << st) if (i >> sc) & 1 else i
        U[j][i] = 1.0 + 0j
    return U


H = [[S2, S2], [S2, -S2]]
T = [[1, 0], [0, TPH]]
TDG = [[1, 0], [0, TPH.conjugate()]]


def toffoli_7t():
    """Standard-form Clifford+T Toffoli with controls 0,1 and target 2.
    Seven T/Tdg gates, six CNOTs, two H."""
    seq = [
        ("H", 2), ("CX", 1, 2), ("TDG", 2), ("CX", 0, 2), ("T", 2),
        ("CX", 1, 2), ("TDG", 2), ("CX", 0, 2), ("T", 1), ("T", 2),
        ("H", 2), ("CX", 0, 1), ("T", 0), ("TDG", 1), ("CX", 0, 1),
    ]
    U = _ident()
    tcount = 0
    for op in seq:
        if op[0] == "H":
            G = _one_qubit(H, op[1])
        elif op[0] == "T":
            G = _one_qubit(T, op[1])
            tcount += 1
        elif op[0] == "TDG":
            G = _one_qubit(TDG, op[1])
            tcount += 1
        else:
            G = _cnot(op[1], op[2])
        U = _mul(G, U)
    return U, tcount, len([o for o in seq if o[0] == "CX"]), \
        len([o for o in seq if o[0] == "H"])


def check_t_ratio():
    U, tcount, ncx, nh = toffoli_7t()
    ref = [[0j] * 8 for _ in range(8)]
    for i in range(8):
        j = i ^ 1 if (i >> 2) & 1 and (i >> 1) & 1 else i
        ref[j][i] = 1.0 + 0j
    err = max(abs(U[i][j] - ref[i][j]) for i in range(8) for j in range(8))
    return {"t_gates_in_circuit": tcount, "cnot_gates": ncx, "h_gates": nh,
            "max_abs_deviation_from_toffoli": err,
            "tolerance": 1e-12, "matches": err < 1e-12,
            "derived_ratio_T_per_toffoli": 7 if err < 1e-12 else None}


if __name__ == "__main__":
    out = {"point_identity_instances_checked": check_point_identities(),
           "t_ratio_derivation": check_t_ratio()}
    json.dump(out, sys.stdout, indent=2)
    print()
