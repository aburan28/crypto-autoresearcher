#!/usr/bin/env python3
"""
certificate_checker.py -- INDEPENDENT certificate verification for
EXP-ISOU-2ac81f.

INDEPENDENCE STATEMENT (this is the point of the file, not decoration).

  * This module imports NOTHING from census.py and NOTHING from any other
    module of this experiment.  Its only imports are argparse, json, os, sys,
    yaml and datetime.
  * It shares NO in-process state with the solver: it is executed as a separate
    process, after the solver process has exited, and it reads only the run's
    written artifacts (dlp_instance.yaml, solve_records.jsonl,
    class_enumeration.yaml, manifest.yaml).
  * It re-implements its own modular inverse, its own affine short-Weierstrass
    point addition, doubling and scalar multiplication, in this file, using a
    different scalar-multiplication schedule (fixed left-to-right binary,
    most-significant bit first) from the right-to-left ladder the solver uses.
    Nothing is called back into the solver.
  * It re-derives, independently:
      (1) that the claimed k satisfies [k]P = Q on the BASE curve E_0
          (the pullback check -- the isogeny restricted to the F_p-rational
          points is a group isomorphism, so the discrete logarithm is the same
          number on every member, and this is what the certificate asserts);
      (2) that the claimed k satisfies [k]P' = Q' on the MEMBER E' itself;
      (3) that P' and Q' actually lie on E' and have order exactly N;
      (4) that every rho-recovered k for that member agrees with the value in
          the frozen instance.
    A member failing ANY of these is reported certificate_verified: false and
    contributes NO cost datum to summary.json.

Self-confirmation is not verification.  This file never writes to, reads from,
or reuses any object produced inside the solver's process.

Usage:  python3 certificate_checker.py --run-dir <run directory>
Writes: <run directory>/certificate_verification.yaml
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import yaml


# --- independent modular and elliptic-curve arithmetic ----------------------

def _inv(x, m):
    """Extended Euclid -- deliberately a different algorithm from the solver's
    Fermat exponentiation, so a fault in one cannot be reproduced by the other."""
    g, a, b = m, 0, 1
    x %= m
    r0, r1 = m, x
    s0, s1 = 0, 1
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    if r0 != 1:
        raise ZeroDivisionError("not invertible")
    return s0 % m


def _on(pt, A, B, P):
    if pt is None:
        return True
    x, y = pt
    return (y * y - x * x * x - A * x - B) % P == 0


def _neg(pt, P):
    return None if pt is None else (pt[0], (-pt[1]) % P)


def _add(p1, p2, A, P):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if (x1 - x2) % P == 0:
        if (y1 + y2) % P == 0:
            return None
        num = (3 * x1 * x1 + A) % P
        den = (2 * y1) % P
    else:
        num = (y2 - y1) % P
        den = (x2 - x1) % P
    lam = num * _inv(den, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def _mul(pt, n, A, P):
    """Left-to-right binary ladder, MSB first -- a different schedule from the
    solver's right-to-left ladder."""
    if pt is None or n % 1 != 0:
        return None
    if n < 0:
        return _mul(_neg(pt, P), -n, A, P)
    R = None
    for bit in bin(n)[2:]:
        R = _add(R, R, A, P)
        if bit == "1":
            R = _add(R, pt, A, P)
    return R


# --- verification -----------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    d = args.run_dir

    with open(os.path.join(d, "dlp_instance.yaml")) as fh:
        inst = yaml.safe_load(fh)
    with open(os.path.join(d, "class_enumeration.yaml")) as fh:
        cls = yaml.safe_load(fh)

    P = inst["base_curve"]["p"]
    A0 = inst["base_curve"]["a"]
    B0 = inst["base_curve"]["b"]
    N = inst["base_curve"]["N"]
    P0 = tuple(inst["P"])
    Q0 = tuple(inst["Q"])
    k_frozen = inst["k"]

    coeffs = {v["index"]: (v["a"], v["b"], v["j"]) for v in cls["vertices"]}
    transfers = {tr["vertex"]: tr for tr in inst["transfers"]}

    # rho-claimed k per vertex, read from the raw solve records
    claimed = {}
    solved_counts = {}
    with open(os.path.join(d, "solve_records.jsonl")) as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("curve_role") not in ("class_member", "base_curve",
                                           "class_member_fresh_seed_tail_check"):
                continue
            vi = r.get("vertex")
            if vi is None:
                continue
            solved_counts[vi] = solved_counts.get(vi, 0) + (1 if r.get("status") == "solved" else 0)
            if r.get("k") is not None:
                claimed.setdefault(vi, set()).add(r["k"])

    # --- the base-curve instance itself, checked first ---------------------
    base_ok = (_on(P0, A0, B0, P) and _on(Q0, A0, B0, P)
               and _mul(P0, N, A0, P) is None
               and _mul(P0, k_frozen, A0, P) == Q0)

    members = []
    n_ok = 0
    for vi in sorted(set(list(claimed.keys()) + list(transfers.keys()))):
        if vi not in coeffs:
            members.append({"vertex": vi, "certificate_verified": False,
                            "reason": "vertex absent from class_enumeration.yaml"})
            continue
        a, b, j = coeffs[vi]
        tr = transfers.get(vi)
        ks = sorted(claimed.get(vi, []))
        entry = {
            "vertex": vi, "j_invariant": j,
            "curve_a": a, "curve_b": b,
            "rho_recovered_k_values": ks,
            "frozen_k": k_frozen,
        }
        if tr is None or tr.get("P_image") is None or tr.get("Q_image") is None:
            entry.update({"certificate_verified": False,
                          "reason": "no transferred instance recorded for this vertex"})
            members.append(entry)
            continue
        Pm = tuple(tr["P_image"])
        Qm = tuple(tr["Q_image"])
        c1 = _on(Pm, a, b, P) and _on(Qm, a, b, P)
        c2 = _mul(Pm, N, a, P) is None and Pm is not None
        c3 = _mul(Qm, N, a, P) is None
        # (1) member check : [k]P' = Q'
        c4 = all(_mul(Pm, kk, a, P) == Qm for kk in ks) if ks else False
        # (2) pullback check : the same k on the BASE curve
        c5 = all(_mul(P0, kk, A0, P) == Q0 for kk in ks) if ks else False
        # (3) agreement with the frozen instance
        c6 = bool(ks) and all(kk == k_frozen for kk in ks)
        # (4) exactly one k was recovered across all seeds
        c7 = len(ks) == 1
        ok = bool(c1 and c2 and c3 and c4 and c5 and c6 and c7)
        entry.update({
            "points_on_codomain": bool(c1),
            "P_image_has_order_N": bool(c2),
            "Q_image_has_order_N": bool(c3),
            "member_check_k_P_equals_Q_on_member": bool(c4),
            "pullback_check_k_P_equals_Q_on_base_curve": bool(c5),
            "agrees_with_frozen_instance_k": bool(c6),
            "single_k_across_all_seeds": bool(c7),
            "seeds_solved": solved_counts.get(vi, 0),
            "certificate_verified": ok,
        })
        if not ok:
            entry["reason"] = "one or more independent checks failed; this member contributes NO cost datum"
        else:
            n_ok += 1
        members.append(entry)

    # --- null objects: their own planted k, checked the same way -----------
    null_path = os.path.join(d, "null_objects.yaml")
    nulls = []
    if os.path.exists(null_path):
        with open(null_path) as fh:
            nb = yaml.safe_load(fh)
        null_claimed = {}
        with open(os.path.join(d, "solve_records.jsonl")) as fh:
            for line in fh:
                r = json.loads(line)
                if r.get("curve_role") != "null_object_different_order":
                    continue
                if r.get("k") is not None:
                    null_claimed.setdefault(r["null_index"], set()).add(r["k"])
        for i, nu in enumerate(nb.get("curves", [])):
            ks = sorted(null_claimed.get(i, []))
            pp, aa = nu["p"], nu["a"]
            Pn = tuple(nu["P"])
            Qn = tuple(nu["Q"])
            ok = bool(ks) and len(ks) == 1 and all(_mul(Pn, kk, aa, pp) == Qn for kk in ks) \
                and all(kk == nu["k"] for kk in ks) and _mul(Pn, nu["N"], aa, pp) is None
            nulls.append({"null_index": i, "N": nu["N"], "rho_recovered_k_values": ks,
                          "planted_k": nu["k"], "certificate_verified": bool(ok)})

    out = {
        "schema": "crypto.autoresearch.exp_isou_2ac81f.certificate_verification.v1",
        "run_dir": d,
        "experiment_id": "EXP-ISOU-2ac81f",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checker": "experiments/EXP-ISOU-2ac81f/implementation/certificate_checker.py",
        "independence_statement": (
            "This checker imports nothing from census.py, shares no in-process "
            "state with the solver, runs as a separate process after the solver "
            "has exited, and re-implements modular inversion (extended Euclid, "
            "not Fermat) and scalar multiplication (left-to-right MSB-first, not "
            "the solver's right-to-left ladder) in its own file. It reads only "
            "written artifacts. Self-confirmation is not verification."),
        "checks_performed": [
            "P and Q lie on the member curve",
            "P and Q have order exactly N on the member curve",
            "[k]P' = Q' on the member (member check)",
            "[k]P = Q on the base curve E_0 (pullback check)",
            "the recovered k equals the frozen instance k",
            "exactly one k was recovered across all seeds for that member",
        ],
        "base_curve_instance_verified": bool(base_ok),
        "members_checked": len(members),
        "members_verified": n_ok,
        "members_failed": [m["vertex"] for m in members if not m["certificate_verified"]],
        "all_members_verified": bool(members) and all(m["certificate_verified"] for m in members),
        "null_objects": nulls,
        "null_objects_all_verified": bool(nulls) and all(n["certificate_verified"] for n in nulls),
        "members": members,
    }
    with open(os.path.join(d, "certificate_verification.yaml"), "w") as fh:
        yaml.safe_dump(out, fh, sort_keys=False, default_flow_style=False, width=100)
    print("certificate verification: %d/%d members verified, base instance verified: %s"
          % (n_ok, len(members), base_ok))
    return 0 if out["all_members_verified"] and base_ok else 1


if __name__ == "__main__":
    sys.exit(main())
