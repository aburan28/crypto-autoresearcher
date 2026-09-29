"""rc_b (object.ell_and_rc_b): kernel of the quadratic part, ell, the
substitution and the substituted closures R'_3 and R'_4; plus the C-ELL check
and the T5 prediction (C-PRED (a))."""
from __future__ import annotations

import numpy as np

import common as C
import closures as CL
from descent import combine_rows, kernel_basis, substitute

ELL_ARMS = ("S3-U400", "S3-SAT100", "F-RANDX19", "N-CONV19")
S3_ARMS = ("S3-U400", "S3-SAT100", "F-RANDX19")


def kernel_info(E, arm, F=None, xR=None, ell_lin=None):
    nv = C.NV
    Mq = E[:, 1 + nv:]
    ker = kernel_basis(Mq)
    dim = len(ker)
    out = {"kernel_dim": dim}
    cvec = None
    if arm == "N-ELL19":
        e18 = 1 << (C.NEQ - 1)
        in_ker = not combine_rows(Mq, e18).any()
        out["e18_in_kernel"] = bool(in_ker)
        if in_ker:
            cvec = ker[0] if dim == 1 else e18
            out["c_rule"] = "kernel vector (dim 1)" if dim == 1 else f"c = e_18 (kernel dim {dim})"
    elif dim == 1:
        cvec = ker[0]
    out["applicable"] = cvec is not None
    if cvec is None:
        out["label"] = f"not applicable (kernel dim {dim})"
        return out, None, None
    ell = combine_rows(E, cvec)
    assert not ell[1 + nv:].any()
    out["c"] = [(cvec >> k) & 1 for k in range(C.NEQ)]
    out["ell_support"] = [int(j) for j in np.flatnonzero(ell)]
    # C-ELL (S_3 and N-CONV19 systems)
    if arm in ELL_ARMS and F is not None:
        xr2i = F.inv(F.mul(xR, xR))
        want = [F.trace(F.mul(1 << k, xr2i)) for k in range(C.NEQ)]
        ok = dim == 1 and out["c"] == want
        if arm in S3_ARMS:
            e = ell_lin.copy()
            e[0] ^= F.trace(F.mul(C.B, xr2i))
            ok = ok and bool((ell == e).all())
        out["C-ELL_ok"] = bool(ok)
    return out, cvec, ell


def rc_b(E, arm, F=None, xR=None, ell_lin=None, want_eqs=False):
    info, cvec, ell = kernel_info(E, arm, F, xR, ell_lin)
    if cvec is None:
        return info, None
    nv = C.NV
    if not ell[1:1 + nv].any():
        info["label"] = "REFUTED-AT-DEGREE-2" if ell[0] else "ELL-TRIVIAL"
        info["substituted"] = False
        return info, None
    eqs2, jstar, aff = substitute(E, ell, C.EQ_MASKS, nv)
    info["substituted"] = True
    info["jstar"] = jstar
    info["substitution"] = {"v_jstar": jstar, "image_vars": aff[0], "image_const": aff[1]}
    r3, _ = CL.macaulay(nv - 1, 3, C.NEQ, eqs2, want_cert=False)
    r4, _ = CL.macaulay(nv - 1, 4, C.NEQ, eqs2, want_cert=False)
    info["R3_rank"] = r3["rank"]
    info["R3_one"] = r3["one"]
    info["R4"] = r4
    info["sigma"] = r4["dims_by_deg"][3] - 360
    info["full_B3"] = r4["dims_by_deg"][3] == C.DIM_BP_LE[3]
    info["T5_applicable"] = r4["dims_by_deg"][3] == r3["rank"]
    info["ref_profile"] = r4["dims_by_deg"] == C.REF_SUB
    info["label"] = "substituted"
    return info, (eqs2 if want_eqs else None)


def t5_prediction(info):
    """T5 prediction record for a T5-applicable system (phase 3)."""
    r4 = info["R4"]
    fd = r4["rank"] + C.T4_CONST
    pred = {"one": bool(r4["one"]), "final_dim": fd,
            "dims_by_deg": [r4["dims_by_deg"][d] + C.DIM_BP_LE[d - 1] for d in range(5)],
            "iterations_to_fixpoint": "1 if rank(M_4) < final_dim else 0 (T5: W^(1) = W_4)"}
    if r4["dims_by_deg"] == C.REF_SUB:
        pred["full_reference_record"] = dict(C.REF_T5_W4)
    return pred
