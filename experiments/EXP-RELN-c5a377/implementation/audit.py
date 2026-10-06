"""Independent accounting audit and relation certificates (C-6 accounting_audit).

Uses only ``vcurve`` arithmetic and its own charging formula; imports nothing
from the charged path. Rejects a receipt that:
  * omits any attempt index in 0..A-1 (failed attempts included) or repeats one;
  * charges an attempt anything other than the formula (scalar multiplications
    (bitlen-1)+(popcount-1) each, one addition, plus |S| scan operations when
    R_j != O), which catches zeroed failed attempts;
  * declares totals that are not the sum of setup and per-attempt charges;
  * disagrees with an independent replay on any SHA256-selected attempt (10%);
  * carries any two-point relation whose certificate a G + b Q = s1 V1 + s2 V2
    fails under independent arithmetic.
"""

from __future__ import annotations

import labels
from vcurve import VCurve


def _smul_charge(k: int) -> int:
    return 0 if k <= 0 else (len(bin(k)) - 3) + (bin(k).count("1") - 1)


def scan_set(vc: VCurve, B2: int) -> list:
    S = []
    for x in range(B2):
        P = vc.lift_canonical(x)
        if P is None:
            continue
        if P[1] == 0:
            S.append(P)
        else:
            S.extend(sorted([P, (x, vc.p - P[1])]))
    return S


def replay(vc, S, B, B2, G, Q, a, b) -> dict:
    p = vc.p
    R = vc.add(vc.mul(a, G), vc.mul(b, Q))
    if R is None:
        return {"outcome": "R_is_O", "rel": None, "n_decomp": 0, "single_point": False}
    found, seen, single = [], set(), False
    for P1 in S:
        T = vc.add(R, vc.neg(P1))
        if T is None:
            single = True
        elif T[0] < B2:
            key = tuple(sorted([P1, T]))
            if key not in seen:
                seen.add(key)
                found.append(key)
    if found:
        (x1, y1), (x2, y2) = found[0]
        sg = lambda y: 1 if y <= (p - 1) // 2 else -1  # noqa: E731
        rel = [x1, sg(y1), x2, sg(y2)]
        nlp = (x1 >= B) + (x2 >= B)
        outcome = ("full", "lp1", "lp2")[nlp]
    else:
        rel = None
        outcome = ("single_point_fb" if R[0] < B else "single_point_lp") if single else "miss"
    return {"outcome": outcome, "rel": rel, "n_decomp": len(found), "single_point": single}


def audit(header: dict, records: list[dict], n_attempts: int, declared_total_group_ops: int,
          ns: str, replay_all: bool = False) -> dict:
    p, q, B, B2 = header["p"], header["q"], header["B"], header["B2"]
    vc = VCurve(p, header["a"], header["b"])
    G = tuple(header["G"])
    Q = tuple(header["Q"]) if header["Q"] is not None else None
    bits, seed = header["bits"], header["seed"]
    reasons = []
    S = scan_set(vc, B2)
    if len(S) != header["scan_size"]:
        reasons.append(f"scan size {header['scan_size']} != independent {len(S)}")
    js = [r["j"] for r in records]
    if js != list(range(n_attempts)):
        missing = sorted(set(range(n_attempts)) - set(js))
        reasons.append(f"attempt indices not exactly 0..{n_attempts - 1}: "
                       f"{len(records)} records, {len(missing)} missing (first {missing[:5]})")
    total = header["setup_ops"]["group_ops"]
    bad_charge = 0
    for r in records:
        exp = _smul_charge(r["a"]) + _smul_charge(r["b"]) + 1
        if r["outcome"] != "R_is_O":
            exp += len(S)
        if r["group_ops"] != exp:
            bad_charge += 1
        total += r["group_ops"]
    if bad_charge:
        reasons.append(f"{bad_charge} attempts charged differently from the formula")
    if total != declared_total_group_ops:
        reasons.append(f"declared total {declared_total_group_ops} != setup + attempts {total}")
    selected = [r for r in records if replay_all or labels.audit_selected(ns, bits, seed, r["j"])]
    mismatches = 0
    for r in selected:
        lbl = labels.attempt_label(ns, bits, seed, r["j"])
        a, b = labels.uniform(lbl + "|a", q), labels.uniform(lbl + "|b", q)
        if (a, b) != (r["a"], r["b"]):
            mismatches += 1
            continue
        rp = replay(vc, S, B, B2, G, Q, a, b)
        if any(rp[k] != r[k] for k in ("outcome", "rel", "n_decomp", "single_point")):
            mismatches += 1
    if mismatches:
        reasons.append(f"{mismatches} of {len(selected)} replayed attempts disagree")
    cert_fail = 0
    n_rel = 0
    for r in records:
        if r["outcome"] not in ("full", "lp1", "lp2"):
            continue
        n_rel += 1
        x1, s1, x2, s2 = r["rel"]
        V1, V2 = vc.lift_canonical(x1), vc.lift_canonical(x2)
        if V1 is None or V2 is None:
            cert_fail += 1
            continue
        lhs = vc.add(vc.mul(r["a"], G), vc.mul(r["b"], Q))
        rhs = vc.add(V1 if s1 > 0 else vc.neg(V1), V2 if s2 > 0 else vc.neg(V2))
        if lhs != rhs:
            cert_fail += 1
    if cert_fail:
        reasons.append(f"{cert_fail} relation certificates fail")
    return {"accepted": not reasons, "reasons": reasons, "n_attempts": len(records),
            "n_replayed": len(selected), "replay_fraction": len(selected) / max(1, len(records)),
            "replay_mismatches": mismatches, "relations_certified": n_rel - cert_fail,
            "certificate_failures": cert_fail, "recomputed_total_group_ops": total}
