"""Independent accounting checker (AMD-20260926-ced670 C-6 accounting_audit).

Uses only verify.py arithmetic, oracle.py and closed-form operation counts; it
never calls the charged code paths (arith, b0, la, pipeline). For a cell
receipt (the JSON a cell wrote) it:

  * rejects receipts that omit failed attempts (the columnar log must cover
    every attempt, its sums must equal the charged totals, and the replay of
    index-labelled attempts below detects a dropped or shifted entry), zero
    or omit the forward-table build or factor-base construction, or omit
    peak RSS;
  * replays 10% of stage-1 attempts (attempt j iff SHA256('<ns>|audit|<bits>|
    <seed>|<j>') % 10 == 0): regenerates R_j from the labels, recomputes its
    group-operation count (scalar multiplications and the B0 scan, counting
    every addition with two finite operands) and probe count independently,
    re-decides membership with the exact oracle, and compares units exactly;
  * recomputes the operation count of EVERY logged LA step from its logged
    dimensions and checks the stage totals;
  * replays EVERY descent attempt the same way and re-verifies k_t G = Q_t;
  * re-verifies every relation by point arithmetic and every recovered log;
  * recomputes the complete cost from its components.
"""

from __future__ import annotations

from math import comb

import common
from oracle import MembershipOracle
from verify import O, VCurve, verify_decomposition

U_ADD = common.UNIT_POINT_ADD


def _pt(v):
    return O if v is None else tuple(v)


def audit_selected(ns, fx, j) -> bool:
    return common.h(common.lab(ns, "audit", fx["bits"], fx["seed"], j)) % common.AUDIT_FRACTION_MOD == 0


def scalar_ops(vc, k, P):
    """(k P, #additions with two finite operands) for right-to-left double-and-add."""
    R, Qp, ops = O, P, 0
    while k:
        if k & 1:
            if R is O or Qp is O:
                R = Qp if R is O else R
            else:
                ops += 1
                R = vc.add(R, Qp)
        k >>= 1
        if k:
            if Qp is not O:
                ops += 1
            Qp = vc.add(Qp, Qp)
    return R, ops


def add_ops(vc, P, Q):
    return vc.add(P, Q), (0 if P is O or Q is O else 1)


def b0_expected(vc, pts, R, m):
    """Group-op and probe counts of the B0 prefix-shared scan (closed recursion)."""
    d = m - 2
    n = len(pts)
    ops = 0

    def rec(level, start, prefix):
        nonlocal ops
        for i in range(start, n):
            new = []
            for P in prefix:
                for s in (1, -1):
                    if P is not O:
                        ops += 1
                    new.append(vc.add(P, vc.neg(pts[i]) if s > 0 else pts[i]))
            if level < d:
                rec(level + 1, i, new)

    rec(1, 0, [R])
    probes = (2 ** d) * comb(n + d - 1, d) if n else 0
    return ops, probes


def la_step_expected(s) -> tuple[int, int]:
    k = s["step"]
    if k == "rank_reduce":
        mul = sum(u - 1 for u in s["basis_nnz_used"])
        if s["new_pivot"] is not None:
            return mul + s["new_row_nnz"] - 1, 1
        return mul, 0
    if k == "sge_singleton":
        return 0, 0
    if k == "sge_merge":
        return s["pivot_nnz"] + s["row_nnz"] + 2, 0
    if k == "lanczos_rhs":
        return s["nr"] + s["nnz"], 0
    if k == "lanczos_iter":
        base = 2 * s["nnz"] + s["nr"] + s["nc"]
        if s["breakdown"]:
            return base, 0
        return base + 4 * s["nc"] + 2 + (2 * s["nc"] + 1 if s["has_prev"] else 0), 1
    if k == "lanczos_check":
        return s["nnz"], 0
    if k == "backsub":
        return s["row_nnz"], 1
    raise ValueError(f"unknown LA step {k}")


def _check_la(log, total, name, fails):
    em = ei = 0
    for s in log:
        m_, i_ = la_step_expected(s)
        if (m_, i_) != (s["la_mul"], s["la_inv"]):
            fails.append(f"{name}: step {s['step']} logged ({s['la_mul']},{s['la_inv']}) expected ({m_},{i_})")
        em += m_
        ei += i_
    if (em, ei) != (total["la_mul"], total["la_inv"]):
        fails.append(f"{name}: step sum ({em},{ei}) != charged total ({total['la_mul']},{total['la_inv']})")
    return len(log)


def _replay_attempt(vc, pts, oracle, R, pre_ops, m, logged_member, logged_ops, probes_each, fails, tag):
    ops, probes = b0_expected(vc, pts, R, m)
    member = oracle.member(R)
    ops_total = pre_ops + ops + (1 if member else 0)
    if member != logged_member:
        fails.append(f"{tag}: membership {logged_member} but oracle says {member}")
    if ops_total != logged_ops or probes != probes_each:
        fails.append(f"{tag}: ops/probes logged ({logged_ops},{probes_each}) expected ({ops_total},{probes})")


def _check_columns(log, n_pts, m, fails, tag):
    """Columnar attempt log: lengths, probe constant vs closed form. Returns (bits, ops, pe)."""
    bits, ops, pe = log["member_bits"], log["pt_ops"], log["probes_each"]
    if len(ops) != len(bits) or set(bits) - {"0", "1"}:
        fails.append(f"{tag}: malformed attempt columns")
    d = m - 2
    exp = (2 ** d) * comb(n_pts + d - 1, d) if n_pts else 0
    if pe != exp:
        fails.append(f"{tag}: probes per attempt {pe} != closed form {exp} (zeroed or partial scan)")
    if [h[0] for h in log["hits"]] != [j for j, c in enumerate(bits) if c == "1"]:
        fails.append(f"{tag}: hit list does not match member attempts")
    return bits, ops, pe


def audit_cell(receipt: dict, full_replay: bool = False) -> dict:
    fails = []
    if receipt.get("status") != "ok":
        return {"accepted": False, "failures": [f"cell status {receipt.get('status')}"]}
    res = receipt["result"]
    kind = res["kind"]
    if not receipt.get("peak_rss_bytes") or not res.get("peak_rss_bytes"):
        fails.append("peak RSS missing or zero")
    fx = res["fixture"]
    ns = res["namespace"]
    vc = VCurve(fx["p"], fx["a"], fx["b"])
    G = tuple(fx["G"])
    q = fx["N"]
    stats = {"kind": kind, "fixture_id": res["fixture_id"]}
    if kind == "rho":
        for t in res["targets"]:
            k = common.uniform(common.lab(ns, "rho", fx["bits"], fx["seed"], t["t"]), q)
            if not t.get("solved") or t.get("k") != k or vc.mul(t["k"], G) != vc.mul(k, G):
                fails.append(f"rho target {t['t']} not certified")
            if not t.get("units"):
                fails.append(f"rho target {t['t']} zero units")
        stats["rho_targets_checked"] = len(res["targets"])
        return {"accepted": not fails, "failures": fails, "stats": stats}

    fb = res["factor_base"]
    pts = [tuple(P) for P in _fb_points(vc, fb)]
    n = fb["L"]
    m = res["m"]
    s1 = res["stage1"]
    for key in ("peak_rss_bytes",):
        if not s1.get(key) or not res["stage3"].get(key):
            fails.append(f"stage {key} missing")
    if fb["construction_cost"]["units"] <= 0:
        fails.append("factor-base construction cost zero/omitted")
    ft = res["forward_table"]["cost"]
    if ft["pt_add"] + ft["pt_dbl"] != n * (n + 1) or ft["probes"] != n * (n + 1) or ft["units"] != (U_ADD + 1) * n * (n + 1):
        fails.append(f"forward table cost {ft} != expected n(n+1)={n * (n + 1)} ops and probes")
    bits, ops, pe = _check_columns(s1["attempt_log"], n, m, fails, "stage1")
    n_att = len(bits)
    if s1["n_attempts"] != n_att or s1["n_failed_attempts"] != bits.count("0"):
        fails.append("attempt/failed-attempt counts disagree with the attempt log")
    ac = s1["cost"]["attempts"]
    if ac["probes"] != n_att * pe or ac["pt_add"] + ac["pt_dbl"] != sum(ops) or ac["mul"] or ac["inv"] \
            or ac["units"] != U_ADD * sum(ops) + n_att * pe:
        fails.append("attempt log does not sum to the charged stage-1 attempt cost")
    if s1["units"] != fb["construction_cost"]["units"] + ft["units"] + ac["units"]:
        fails.append("stage-1 units != fb construction + table + attempts")
    members = [j for j, c in enumerate(bits) if c == "1"]
    rels = s1["relations"]
    if [r["j"] for r in rels] != members:
        fails.append("relations do not correspond one-to-one to member attempts")
    k_true = common.uniform(common.lab(ns, "target", fx["bits"], fx["seed"]), q)
    Q = vc.mul(k_true, G)
    for r in rels:
        R = _pt(r["R"])
        if not verify_decomposition(vc, R, pts, [tuple(t) for t in r["terms"]], m=m):
            fails.append(f"relation {r['j']} fails point-arithmetic verification")
        if vc.add(vc.mul(r["a"], G), vc.mul(r["b"], Q)) != R:
            fails.append(f"relation {r['j']} R != a G + b Q")
    oracle = MembershipOracle(fx, pts, m)
    replayed = 0
    for j in range(n_att):
        if not (full_replay or audit_selected(ns, fx, j)):
            continue
        aj, bj = common.uniform_pair(common.lab(ns, "attempt", fx["bits"], fx["seed"], j), q)
        A, o1 = scalar_ops(vc, aj, G)
        Bq, o2 = scalar_ops(vc, bj, Q)
        R, o3 = add_ops(vc, A, Bq)
        _replay_attempt(vc, pts, oracle, R, o1 + o2 + o3, m, bits[j] == "1", ops[j] if j < len(ops) else None,
                        pe, fails, f"attempt {j}")
        replayed += 1
    stats["attempts_replayed"] = replayed
    stats["attempts_total"] = n_att
    s3 = res["stage3"]
    stats["la_steps_checked"] = (_check_la(s3["rank_log"], s3["rank_tracking_cost"], "rank", fails)
                                 + _check_la(s3["la_log"], s3["la_cost"], "la", fails))
    if s3["units"] != s3["rank_tracking_cost"]["units"] + s3["la_cost"]["units"]:
        fails.append("stage-3 units != rank tracking + LA")
    x = s3.get("logs")
    if kind == "primary":
        if x is None or any(vc.mul(x[i], G) != pts[i] for i in range(n)) or vc.mul(x[n], G) != Q:
            fails.append("recovered logs fail verification")
        d = res["descents"]
        if len(d["targets"]) != d["n_descents"]:
            fails.append("descent count mismatch")
        dunits = 0
        for t in d["targets"]:
            kt = common.uniform(common.lab(ns, "descent", fx["bits"], fx["seed"], t["t"]), q)
            Qt = vc.mul(kt, G)
            dbits, dops, dpe = _check_columns(t["attempt_log"], n, m, fails, f"descent {t['t']}")
            if not dbits or dbits != "0" * (len(dbits) - 1) + "1" or t["attempts"] != len(dbits) \
                    or t["i"] != len(dbits) - 1:
                fails.append(f"descent {t['t']}: attempt log not contiguous/terminal")
            for i in range(len(dbits)):
                r = common.uniform(common.lab(ns, "descent_r", fx["bits"], fx["seed"], t["t"], i), q)
                rG, o1 = scalar_ops(vc, r, G)
                R, o2 = add_ops(vc, Qt, rG)
                _replay_attempt(vc, pts, oracle, R, o1 + o2, m, dbits[i] == "1", dops[i] if i < len(dops) else None,
                                dpe, fails, f"descent {t['t']}.{i}")
            if U_ADD * sum(dops) + len(dbits) * dpe != t["units"]:
                fails.append(f"descent {t['t']}: attempt units do not sum")
            R_found = vc.add(Qt, vc.mul(t["r"], G))
            if not verify_decomposition(vc, R_found, pts, [tuple(x) for x in t["terms"]], m=m):
                fails.append(f"descent {t['t']}: decomposition fails verification")
            dunits += t["units"]
            if vc.mul(t["k_hat"], G) != Qt:
                fails.append(f"descent {t['t']}: k_t G != Q_t")
        if dunits != d["units"] or d["cost"]["units"] != dunits:
            fails.append("descent units do not sum to the charged descent cost")
        comp = res["complete_units_components"]
        if (comp["stage1"], comp["stage3"], comp["descents"]) != (s1["units"], s3["units"], d["units"]) \
                or res["complete_units"] != s1["units"] + s3["units"] + d["units"]:
            fails.append("complete cost != stage1 + stage3 + descents")
        if not res["descents"].get("peak_rss_bytes"):
            fails.append("descent peak RSS missing")
        kf = res["known_false"]
        if kf["log_verification_all_ok"] or not kf["control_passed"] or kf["rows_changed"] == 0:
            fails.append("known-false control not behaving as specified")
        stats["descent_attempts_replayed"] = sum(len(t["attempt_log"]["member_bits"]) for t in d["targets"])
    return {"accepted": not fails, "failures": fails, "stats": stats}


def _fb_points(vc, fb):
    return [vc.lift(x) for x in fb["V"]]


def audit_run(receipts: list[dict]) -> dict:
    per = [audit_cell(r) for r in receipts]
    return {"accepted": all(p["accepted"] for p in per), "cells": per,
            "rule": "10% of stage-1 attempts by SHA256 audit label; all LA steps; every descent"}
