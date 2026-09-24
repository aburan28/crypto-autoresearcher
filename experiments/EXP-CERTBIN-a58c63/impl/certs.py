"""PS0' certificates (new; C-PROPS, F-J2-1): for an unsatisfiable instance
with 1 in R_D, an explicit combination of ORIGINAL rows equal to the constant 1.

Regime A (GF(2)): the declared column pass is re-run on M_D augmented with the
identity (R extra bit columns); the pivot row of the constant column then
carries the set of original rows whose XOR is 1.
Regime B (F_{2^n}): the same with an F_{2^n} identity tracked by the same row
operations; the pivot row p* of the constant column equals gamma * e_const,
so the coefficients are track[p*] / gamma.
Both are self-checked here; verifier/verify_cert.py re-verifies them in a
separate process with its own arithmetic."""
import numpy as np

from elim import column_pass as column_pass_A
from regimeB import column_pass as column_pass_B


def cert_A(S, E):
    Md = S.build_dense(E)
    R, C = Md.shape
    aug = np.concatenate([Md, np.eye(R, dtype=np.uint8)], axis=1)
    Wt = (C + R + 63) // 64
    pad = np.zeros((R, Wt * 64 - C - R), dtype=np.uint8)
    Mp = np.packbits(np.concatenate([aug, pad], axis=1), axis=1, bitorder="little").view(np.uint64).reshape(R, Wt).copy()
    ps, cs, Xs = column_pass_A(Mp, C, keep_ops=False)
    if S.const_col not in cs:
        return None
    pstar = ps[cs.index(S.const_col)]
    row = np.unpackbits(Mp[pstar].view(np.uint8), bitorder="little")[:C + R]
    body, comb = row[:C], row[C:]
    rows = np.flatnonzero(comb).tolist()
    # self-check: XOR of the original rows is e_const
    acc = np.bitwise_xor.reduce(Md[rows], axis=0) if rows else np.zeros(C, dtype=np.uint8)
    want = np.zeros(C, dtype=np.uint8)
    want[S.const_col] = 1
    ok = bool(np.array_equal(acc, want)) and bool(np.array_equal(body, want))
    ro = S.row_order()
    return {"rows": rows, "row_labels": [[ro[i]["mu"], ro[i]["k"]] for i in rows], "self_check": ok}


def cert_B(S, T, coeffs):
    M = S.build(coeffs)
    R, C = M.shape
    track = np.zeros((R, R), dtype=np.uint32)
    track[np.arange(R), np.arange(R)] = 1
    ps, cs, Xs, pv, fnp, cl, unused = column_pass_B(M, T, keep_ops=False, track=track)
    if S.const_col not in cs:
        return None
    k = cs.index(S.const_col)
    pstar = ps[k]
    gamma = int(M[pstar, S.const_col])
    t = track[pstar].astype(np.int64)
    nz = np.flatnonzero(t)
    coef = T.exp[(T.log[t[nz]] - T.log[gamma]) % T.q1]
    # self-check with the impl's arithmetic
    M0 = S.build(coeffs).astype(np.int64)
    acc = np.zeros(C, dtype=np.int64)
    for i, cf in zip(nz, coef):
        row = M0[i]
        j = np.flatnonzero(row)
        acc[j] ^= T.exp[T.log[row[j]] + T.log[int(cf)]]
    want = np.zeros(C, dtype=np.int64)
    want[S.const_col] = 1
    ro = S.row_order()
    return {"rows": nz.tolist(), "coeffs": [int(x) for x in coef],
            "row_labels": [[ro[i]["block"], ro[i]["mult"]] for i in nz],
            "self_check": bool(np.array_equal(acc, want))}
