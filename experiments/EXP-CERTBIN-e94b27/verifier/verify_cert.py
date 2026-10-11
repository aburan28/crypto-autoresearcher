#!/usr/bin/env python3
"""Independent certificate verifier for EXP-CERTBIN-e94b27 (spec
object.verifier, controls C-CERT and C-VERIFIER).

INDEPENDENCE: this file imports nothing from experiments/EXP-CERTBIN-e94b27/impl/
or from experiments/EXP-CERTBIN-4e92d7/impl/ (only the standard library and
numpy). It rebuilds every system f_0..f_16 itself:
  * curve-algebra instances (family F-S3): from (B, x_R) read from the archived
    source run, by EVALUATING S_3(x_1, x_2, x_R) = (x_1x_2 + x_1x_R + x_2x_R)^2
    + x_1x_2x_R + B at all 2^18 Boolean assignments with its own schoolbook
    F_{2^17} arithmetic (vectorised), and recovering each coordinate's algebraic
    normal form with the Moebius transform (no symbolic expansion);
  * F-AFF-1 instances: A0 XOR (XOR_{j : bit j of r} Aj) from the archived hex
    rows (integer XOR), r = the archived x_R;
  * F-NULLF2 instances: the archived per-target E_hex.
Hex rows are decoded with this file's own monomial ordering (degree ascending,
then ascending sorted index tuple, 172 monomials of degree <= 2 in 18
variables; bit j of a row = coefficient of monomial j).

A certificate is a list of pairs (mu, k), mu a sorted list of distinct variable
indices in 0..17 and k in 0..16. It is ACCEPTED iff it is well formed, has no
repeated pair, and sum_{(mu,k)} mu * f_k (multilinear products in
B = F_2[v]/(v_i^2 + v_i)) is exactly the constant 1.

Usage:
  verify_cert.py --certs CERTS.jsonl.gz --source-run SRC --out OUT.json
                 [--instances instance-sets.json]  (default: next to --certs)
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import sys
import time
from itertools import combinations

import numpy as np

NVAR = 18
NEQ = 17
HALF = 9
POLY = (1 << 17) | (1 << 3) | 1     # t^17 + t^3 + 1


# ---------------------------------------------------------------------------
# F_{2^17}, vectorised schoolbook
# ---------------------------------------------------------------------------
def gf_mul(a, b):
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    a, b = np.broadcast_arrays(a, b)
    r = np.zeros(a.shape, dtype=np.int64)
    for i in range(17):
        r ^= np.where((b >> i) & 1, a << i, 0)
    for bit in range(32, 16, -1):
        r ^= ((r >> bit) & 1) * (POLY << (bit - 17))
    return r


def gf_mul_scalar(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    for bit in range(40, 16, -1):
        if (r >> bit) & 1:
            r ^= POLY << (bit - 17)
    return r


# ---------------------------------------------------------------------------
# systems
# ---------------------------------------------------------------------------
def eq_monomial_masks():
    out = []
    for d in range(3):
        for c in combinations(range(NVAR), d):
            m = 0
            for i in c:
                m |= 1 << i
            out.append(m)
    assert len(out) == 172
    return out


EQM = eq_monomial_masks()


def anf_from_truth(tt):
    """tt: (2^18,) uint8 truth table -> sorted monomial masks of its ANF."""
    a = tt.copy()
    for i in range(NVAR):
        v = a.reshape(-1, 2, 1 << i)
        v[:, 1, :] ^= v[:, 0, :]
    return [int(m) for m in np.flatnonzero(a)]


def system_curve(B, xR):
    u = np.arange(1 << NVAR, dtype=np.int64)
    x1 = u & ((1 << HALF) - 1)
    x2 = u >> HALF
    x3 = np.int64(xR)
    e = gf_mul(x1, x2) ^ gf_mul(x1, x3) ^ gf_mul(x2, x3)
    s = gf_mul(e, e) ^ gf_mul(gf_mul(x1, x2), x3) ^ np.int64(B)
    eqs = []
    for k in range(NEQ):
        tt = ((s >> k) & 1).astype(np.uint8)
        f = anf_from_truth(tt)
        if any(bin(m).count("1") > 2 for m in f):
            raise ValueError("descended equation of degree > 2")
        eqs.append(f)
    return eqs


def system_from_rows(rows):
    return [[EQM[j] for j in range(172) if (rows[k] >> j) & 1] for k in range(NEQ)]


def rows_from_hex(hx):
    return [int(h, 16) for h in hx]


def rows_to_hex(rows):
    return [format(r, "x") for r in rows]


def masks_to_rows(eqs):
    pos = {m: j for j, m in enumerate(EQM)}
    rows = []
    for f in eqs:
        r = 0
        for m in f:
            r |= 1 << pos[m]
        rows.append(r)
    return rows


# ---------------------------------------------------------------------------
# certificate check
# ---------------------------------------------------------------------------
def check_certificate(pairs, eqs):
    seen = set()
    by_k = {}
    maxdeg = 0
    for p in pairs:
        if not (isinstance(p, list) and len(p) == 2 and isinstance(p[0], list) and isinstance(p[1], int)):
            return False, "malformed pair", maxdeg
        mu, k = p
        if not (0 <= k < NEQ):
            return False, "k out of range", maxdeg
        if any((not isinstance(i, int)) or i < 0 or i >= NVAR for i in mu) or sorted(set(mu)) != mu:
            return False, "malformed mu", maxdeg
        m = 0
        for i in mu:
            m |= 1 << i
        if (m, k) in seen:
            return False, "repeated pair", maxdeg
        seen.add((m, k))
        by_k.setdefault(k, []).append(m)
        maxdeg = max(maxdeg, len(mu))
    parts = []
    for k, mus in by_k.items():
        fk = np.array(eqs[k], dtype=np.int64)
        if fk.size == 0:
            continue
        parts.append((np.array(mus, dtype=np.int64)[:, None] | fk[None, :]).ravel())
    if not parts:
        return False, "empty sum", maxdeg
    allm = np.concatenate(parts)
    vals, cnt = np.unique(allm, return_counts=True)
    odd = vals[(cnt & 1) == 1]
    if odd.size == 1 and int(odd[0]) == 0:
        return True, "sum equals 1", maxdeg
    return False, f"sum is not 1 ({odd.size} monomials survive)", maxdeg


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--certs", required=True)
    ap.add_argument("--source-run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--instances", default=None)
    a = ap.parse_args()
    t0 = time.time()
    src = a.source_run
    inst_path = a.instances or os.path.join(os.path.dirname(os.path.abspath(a.certs)), "instance-sets.json")
    curve = json.load(open(os.path.join(src, "curve.json")))
    B = int(curve["B"])
    xr = {}
    for fam in ("F-S3", "F-AFF-1"):
        with gzip.open(os.path.join(src, f"targets-{fam}.jsonl.gz"), "rt") as f:
            for line in f:
                r = json.loads(line)
                xr[(fam, r["idx"])] = r["x_R"]
    with gzip.open(os.path.join(src, "checkpoint", "p1-instances.json.gz"), "rt") as f:
        p1 = json.load(f)
    A0 = rows_from_hex(p1["F-AFF-1"]["A0_hex"])
    Aj = [rows_from_hex(h) for h in p1["F-AFF-1"]["Aj_hex"]]
    nf = {t["idx"]: rows_from_hex(t["E_hex"]) for t in p1["F-NULLF2"]["targets"]}

    cache = {}

    def system(fam, idx):
        key = (fam, idx)
        if key not in cache:
            if fam == "F-S3":
                cache[key] = system_curve(B, int(xr[key]))
            elif fam == "F-AFF-1":
                r = int(xr[key])
                rows = list(A0)
                for j in range(NEQ):
                    if (r >> j) & 1:
                        rows = [x ^ y for x, y in zip(rows, Aj[j])]
                cache[key] = system_from_rows(rows)
            elif fam == "F-NULLF2":
                cache[key] = system_from_rows(nf[idx])
            else:
                raise KeyError(fam)
        return cache[key]

    # ---- C-VERIFIER construction agreement on every curve-algebra instance
    construction = []
    if os.path.exists(inst_path):
        inst = json.load(open(inst_path))
        for sname, lst in inst["sets"].items():
            for it in lst:
                if it["family"] != "F-S3":
                    continue
                eqs = system("F-S3", it["idx"])
                own_hex = rows_to_hex(masks_to_rows(eqs))
                construction.append({"key": it["key"], "agree_with_engine_E": own_hex == it["E_hex"],
                                     "own_sha256": hashlib.sha256(json.dumps(own_hex).encode()).hexdigest()})
    results = []
    with gzip.open(a.certs, "rt") as f:
        for line in f:
            c = json.loads(line)
            try:
                eqs = system(c["family"], c["idx"])
                ok, why, md = check_certificate(c["C"], eqs)
            except Exception as e:  # noqa: BLE001
                ok, why, md = False, f"exception: {e!r}", None
            results.append({"key": c["key"], "closure": c["closure"], "verified": bool(ok), "reason": why,
                            "size": len(c["C"]), "max_deg_mu": md})
    out = {
        "verifier": "experiments/EXP-CERTBIN-e94b27/verifier/verify_cert.py",
        "verifier_sha256": hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
        "certs": a.certs, "certs_sha256": hashlib.sha256(open(a.certs, "rb").read()).hexdigest(),
        "source_run": src, "instances_file": inst_path if os.path.exists(inst_path) else None,
        "pid": os.getpid(), "separate_process": True,
        "imports": sorted(m for m in sys.modules if m.split(".")[0] in ("impl", "closure", "macaulay", "gf2n",
                                                                         "elim", "curve", "instances")),
        "submitted": len(results), "verified": sum(r["verified"] for r in results),
        "failed": sum(not r["verified"] for r in results),
        "construction_checked": len(construction),
        "construction_disagreements": [c["key"] for c in construction if not c["agree_with_engine_E"]],
        "certificates": results, "construction": construction,
        "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "wall_seconds": time.time() - t0,
    }
    tmp = a.out + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    os.replace(tmp, a.out)
    print(f"[verify_cert] submitted={out['submitted']} verified={out['verified']} failed={out['failed']} "
          f"construction_checked={len(construction)} disagreements={len(out['construction_disagreements'])} "
          f"({out['wall_seconds']:.1f}s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
