"""Per-system closure computations on the pinned engine (imported).

M_D = closure.Closure(nv, D, 17).macaulay_closure, W_D = .w_closure. The
wdag-v1 extractor is wdag.WDagClosure. No closure with D >= 5 (SR-4).
"""
from __future__ import annotations

import time

from crypto_autoresearcher.gf2 import closure

import rcb
import wdag
from common import rows_to_eqs

C3 = closure.Closure(18, 3, 17)
C4 = closure.Closure(18, 4, 17)
R3 = closure.Closure(17, 3, 17)
R4 = closure.Closure(17, 4, 17)
X4 = wdag.WDagClosure(18, 4, 17)

FIX = {"M_3": (C3.R, C3.C), "M_4": (C4.R, C4.C), "R'_3": (R3.R, R3.C), "R'_4": (R4.R, R4.C)}
FIX_EXPECTED = {"M_3": (323, 988), "M_4": (2924, 4048), "R'_3": (306, 834), "R'_4": (2618, 3214)}
SUBST_REF = [0, 0, 16, 288, 2328]
UNSUBST_REF = [0, 0, 17, 323, 2771]


def run_m(Cl, eqs, want_cert):
    t = time.time()
    rec, cert = Cl.macaulay_closure(eqs, want_cert=want_cert)
    rec = dict(rec)
    rec["wall_seconds"] = round(time.time() - t, 4)
    if cert is not None:
        rec["engine_self_check_sum_is_1"] = closure.eval_cert(cert, eqs) == [0]
    return rec, cert


def run_w(Cl, eqs, want_cert):
    t = time.time()
    rec, cert = Cl.w_closure(eqs, want_cert=want_cert)
    rec = dict(rec)
    rec["wall_seconds"] = round(time.time() - t, 4)
    if cert is not None:
        rec["engine_self_check_sum_is_1"] = closure.eval_cert(cert, eqs) == [0]
    return rec, cert


def derived_m4(rec):
    d = rec["dims_by_deg"]
    return {"P": rec["rank"] - d[3], "fallen": d[3], "linear_forms": d[1] - d[0]}


def rcb_phase3(rows):
    """rc_b (1)-(5): ell info, and on substituted systems R'_3 and R'_4."""
    info = rcb.ell_info(rows)
    out = {"kernel_dim": info["kernel_dim"], "label": info["label"],
           "c": info["c"], "ell_linear_support": info["ell_linear_support"],
           "ell_const": info["ell_const"], "j_star": info["j_star"],
           "substituted": info["substituted"]}
    if info["substituted"]:
        eqs17, _ = rcb.substitute(rows, info)
        r3, _ = run_m(R3, eqs17, False)
        r4, _ = run_m(R4, eqs17, False)
        out["R3"] = r3
        out["R4"] = r4
        out["T5_applicable"] = r4["dims_by_deg"][3] == r3["rank"]
        if out["T5_applicable"]:
            out["T5_prediction"] = {"W4_refuted": bool(r4["one"]),
                                    "W4_final_dim": r4["rank"] + 834}
        out["subst_profile_is_semiregular"] = r4["dims_by_deg"] == SUBST_REF
    else:
        out["T5_applicable"] = None
    return out


def w4_prime(rows, rcbrec):
    info = rcb.ell_info(rows)
    eqs17, _ = rcb.substitute(rows, info)
    rec, _ = run_w(R4, eqs17, False)
    return rec


def extract_wdag(rows, engine_rec):
    """-> (wdag body or None, extractor record)."""
    eqs = rows_to_eqs(rows)
    t = time.time()
    try:
        dims, of, levels = X4.iterate(eqs)
        body = X4.extract(levels) if levels is not None else None
        err = None
    except Exception as exc:  # recorded as UNCERTIFIED, never hidden
        dims, of, body, err = None, None, None, repr(exc)
    xrec = {"extractor_dims": dims, "extractor_one_first_iteration": of,
            "dims_equal_engine": dims == engine_rec["dims"] if dims is not None else None,
            "depth_equal_engine": of == engine_rec["one_first_iteration"] if dims is not None else None,
            "error": err, "wall_seconds": round(time.time() - t, 4)}
    if body is not None:
        xrec["node_count"] = len(body["nodes"])
        xrec["rows_total"] = sum(len(n["rows"]) for n in body["nodes"])
    return body, xrec
