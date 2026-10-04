#!/usr/bin/env python3
"""Independent verifier for EXP-CERTBIN-ddfe75 (N-CONV).

Imports NOTHING from experiments/EXP-CERTBIN-ddfe75/impl/, from
crypto_autoresearcher (any module), from any archived impl/ or from any
review directory. Only the standard library and numpy (for the PCG64 draw
streams and vectorised evaluation).

Own components (all written here):
  * F_{2^17} = F_2[t]/(t^17 + t^3 + 1) by exp/log tables with base t
    (2^17 - 1 is prime, so every element other than 0, 1 generates F*);
  * S_3 descent by GENERIC symbolic expansion of
    (x1 x2 + x1 x3 + x2 x3)^2 + x1 x2 x3 + B as polynomials in v with
    F_{2^17} coefficients and multilinear reduction (v^2 = v);
  * the union support U and S_L, the N-CONV17 forms Q_k, every draw rule and
    the keep rule (numpy PCG64, one generator per arm);
  * exhaustive satisfiability over 2^18 assignments by a half split
    (x = v_0..v_8, y = v_9..v_17; a 512 x 512 value table per equation);
  * multilinear arithmetic for certificates (monomials as bit masks).

(V1) rebuild every system; (V2) s and solution lists; (V3) draw-stream
replay; (V4) certificates (flat-v1, wdag-v1 rules (a)-(e)); (V5) negative
controls. Outputs certificate-verification.json,
construction-verification.json, draw-replay-verification.json and
negative-controls-verification.json in --out.
"""
from __future__ import annotations

import argparse
import datetime
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# F_{2^17} by tables
# ---------------------------------------------------------------------------
FN = 17
FPOLY = (1 << 17) | (1 << 3) | 1
FORD = (1 << FN) - 1
EXP = [0] * (2 * FORD)
LOG = [0] * (1 << FN)
_x = 1
for _i in range(FORD):
    EXP[_i] = _x
    LOG[_x] = _i
    _x <<= 1
    if _x >> FN:
        _x ^= FPOLY
for _i in range(FORD, 2 * FORD):
    EXP[_i] = EXP[_i - FORD]
assert _x == 1, "t does not have order 2^17 - 1"


def fmul(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP[LOG[a] + LOG[b]]


def finv(a):
    return EXP[(FORD - LOG[a]) % FORD]


def ftr(a):
    s = 0
    x = a
    for _ in range(FN):
        s ^= x
        x = fmul(x, x)
    return s


def tp(j):
    return EXP[j % FORD]


# ---------------------------------------------------------------------------
# monomials and the 172-column layout (deg ascending, then sorted tuple)
# ---------------------------------------------------------------------------
NVAR = 18
NE = 17
_mons = [0] + [1 << i for i in range(NVAR)]
for a in range(NVAR):
    for b in range(a + 1, NVAR):
        _mons.append((1 << a) | (1 << b))
MON = _mons
COLIDX = {m: i for i, m in enumerate(MON)}
assert len(MON) == 172


def pmul(p, q):
    out = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = m1 | m2
            v = out.get(m, 0) ^ fmul(c1, c2)
            if v:
                out[m] = v
            elif m in out:
                del out[m]
    return out


def padd(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            v = out.get(m, 0) ^ c
            if v:
                out[m] = v
            elif m in out:
                del out[m]
    return out


X1 = {1 << i: tp(i) for i in range(9)}
X2 = {1 << (9 + j): tp(j) for j in range(9)}
X12 = pmul(X1, X2)


def s3_poly(xR, B):
    X3 = {0: xR} if xR else {}
    e1 = padd(X12, pmul(X1, X3), pmul(X2, X3))
    return padd(pmul(e1, e1), pmul(X12, X3), {0: B} if B else {})


def poly_to_rows(p):
    rows = [0] * NE
    for m, c in p.items():
        col = COLIDX[m]
        for k in range(NE):
            if (c >> k) & 1:
                rows[k] |= 1 << col
    return rows


def s3_rows(xR, B):
    return poly_to_rows(s3_poly(xR, B))


def to_hex(rows):
    return [format(r, "x") for r in rows]


def hsha(E_hex):
    return hashlib.sha256(json.dumps(E_hex).encode()).hexdigest()


def rows_masks(rows):
    """rows -> list of numpy int64 arrays of monomial masks."""
    out = []
    for r in rows:
        out.append(np.array([MON[c] for c in range(172) if (r >> c) & 1], dtype=np.int64))
    return out


# ---------------------------------------------------------------------------
# exhaustive satisfiability: half split
# ---------------------------------------------------------------------------
_XS = np.arange(512, dtype=np.int64)


def solutions(rows):
    """-> sorted list of u (bit i = v_i) with every equation = 0."""
    good = np.ones((512, 512), dtype=bool)  # [y, x]
    for r in rows:
        c = 0
        tx = np.zeros(512, dtype=np.int64)
        ty = np.zeros(512, dtype=np.int64)
        colmask = [0] * 9  # for b in 0..8 (var 9+b): mask of x-vars a with v_a v_{9+b}
        for ci in range(172):
            if not (r >> ci) & 1:
                continue
            m = MON[ci]
            lo, hi = m & 511, m >> 9
            if m == 0:
                c ^= 1
            elif hi == 0:
                tx ^= ((_XS & lo) == lo).astype(np.int64)
            elif lo == 0:
                ty ^= ((_XS & hi) == hi).astype(np.int64)
            else:
                # one x var and one y var
                assert bin(lo).count("1") == 1 and bin(hi).count("1") == 1
                colmask[hi.bit_length() - 1] |= lo
        Ry = np.zeros(512, dtype=np.int64)
        for b in range(9):
            if colmask[b]:
                Ry ^= np.where((_XS >> b) & 1, colmask[b], 0)
        bil = np.bitwise_count(_XS[None, :] & Ry[:, None]) & 1
        val = (c ^ tx[None, :] ^ ty[:, None] ^ bil) & 1
        good &= (val == 0)
    ys, xs = np.nonzero(good)
    return sorted((ys.astype(np.int64) << 9 | xs).tolist())


# ---------------------------------------------------------------------------
# certificate checks
# ---------------------------------------------------------------------------
def _parity(arr):
    if arr.size == 0:
        return arr
    u, cnt = np.unique(arr, return_counts=True)
    return u[(cnt & 1) == 1]


def _deg(p):
    return int(np.bitwise_count(p).max()) if p.size else -1


def _mu_mask(mu, nv=NVAR):
    if not isinstance(mu, list):
        raise ValueError("mu not a list")
    s = 0
    prev = -1
    for i in mu:
        if not isinstance(i, int) or i <= prev or i < 0 or i >= nv:
            raise ValueError(f"bad mu {mu}")
        s |= 1 << i
        prev = i
    return s


def check_flat(body, F, closure):
    """flat-v1: sum mu*f_k == 1. For closure M_4 also max|mu| <= 2."""
    res = {"format": "flat-v1", "size": None, "max_mu": None}
    try:
        parts = []
        mx = 0
        for mu, k in body:
            if not isinstance(k, int) or not 0 <= k < NE:
                raise ValueError(f"bad k {k}")
            mm = _mu_mask(mu)
            mx = max(mx, len(mu))
            parts.append(F[k] | mm)
        res["size"] = len(body)
        res["max_mu"] = mx
        s = _parity(np.concatenate(parts)) if parts else np.zeros(0, dtype=np.int64)
        sum_is_1 = bool(s.size == 1 and int(s[0]) == 0)
        res["sum_is_1"] = sum_is_1
        if not sum_is_1:
            res.update(verified=False, reason="sum is not 1")
        elif closure == "M_4" and mx > 2:
            res.update(verified=False, reason="max |mu| > 2 for an M_4 certificate")
        else:
            res.update(verified=True, reason=None)
        res["counts_for_M4"] = bool(sum_is_1 and mx <= 2)
        res["counts_for_W4"] = bool(sum_is_1 and mx <= 2)
    except Exception as exc:  # format error
        res.update(verified=False, reason=f"format: {exc}", sum_is_1=False,
                   counts_for_M4=False, counts_for_W4=False)
    return res


def check_wdag(body, F, D=4, nv=NVAR):
    """wdag-v1 rules (a)-(e). F[k] = numpy array of monomial masks of f_k.
    D and nv are parameters only so that the self-test can apply the same
    rules to small systems; the run uses D = 4, nv = 18."""
    res = {"format": "wdag-v1", "node_count": None, "size": None, "max_mu": None,
           "max_child_degree": None}
    try:
        if body.get("D") != D or body.get("nv") != nv:
            raise ValueError("D/nv")
        nodes = body["nodes"]
        out = body["output"]
        if not isinstance(out, int) or not 0 <= out < len(nodes):
            raise ValueError("output id")
        polys = []
        mx = 0
        mcd = -1
        nrows = 0
        viol = []
        for i, nd in enumerate(nodes):
            if nd.get("id") != i:
                raise ValueError(f"node {i} id")
            parts = []
            for mu, k in nd["rows"]:
                if not isinstance(k, int) or not 0 <= k < len(F):
                    viol.append(f"(b) node {i} k={k}")
                    continue
                mm = _mu_mask(mu, nv)
                mx = max(mx, len(mu))
                if len(mu) > D - 2:
                    viol.append(f"(b) node {i} |mu|={len(mu)}")
                parts.append(F[k] | mm)
                nrows += 1
            for j, c in nd["prods"]:
                if not isinstance(j, int) or not 0 <= j < nv:
                    raise ValueError(f"node {i} j={j}")
                if not isinstance(c, int) or c < 0 or c >= i:
                    viol.append(f"(a) node {i} child {c}")
                    continue
                dc = _deg(polys[c])
                mcd = max(mcd, dc)
                if dc > D - 1:
                    viol.append(f"(c) node {i} child {c} degree {dc}")
                parts.append(polys[c] | (1 << j))
            p = _parity(np.concatenate(parts)) if parts else np.zeros(0, dtype=np.int64)
            if _deg(p) > D:
                viol.append(f"(d) node {i} degree {_deg(p)}")
            polys.append(p)
            if len(viol) > 50:
                break
        po = polys[out] if out < len(polys) else np.zeros(0, dtype=np.int64)
        is1 = bool(po.size == 1 and int(po[0]) == 0)
        if not is1:
            viol.append("(e) poly(output) != 1")
        res.update(node_count=len(nodes), size=nrows, max_mu=mx, max_child_degree=mcd,
                   output_is_1=is1, violations=viol[:20], verified=not viol,
                   reason=None if not viol else "; ".join(viol[:5]))
    except Exception as exc:
        res.update(verified=False, reason=f"format: {exc}", output_is_1=False, violations=[])
    return res


def check_cert(line, F):
    fmt = line["format"]
    if fmt == "flat-v1":
        return check_flat(line["body"], F, line["closure"])
    if fmt == "wdag-v1":
        r = check_wdag(line["body"], F)
        r["counts_for_W4"] = bool(r["verified"])
        # an M_4 wdag must be a single node with no prods
        if line["closure"] == "M_4":
            nd = line["body"].get("nodes", [])
            if r["verified"] and not (len(nd) == 1 and not nd[0]["prods"]):
                r.update(verified=False, reason="M_4 wdag with products or several nodes")
        return r
    return {"format": fmt, "verified": False, "reason": "unknown format"}


# ---------------------------------------------------------------------------
# draw rules (V3)
# ---------------------------------------------------------------------------
def union_support(B):
    E0 = s3_rows(0, B)
    U = list(E0)
    for j in range(17):
        Ej = s3_rows(tp(j), B)
        for k in range(NE):
            U[k] |= Ej[k] ^ E0[k]
    return U


def conv17():
    rows = [0] * NE
    for a in range(9):
        for b in range(9):
            rows[a + b] |= 1 << COLIDX[(1 << a) | (1 << (9 + b))]
    return rows


QCOLS = (((1 << 172) - 1) >> 19) << 19


def replay_arm(arm, seed, slots, B, U, sl, qparts, s3full, lqparts):
    """-> list of attempt records, list of kept systems."""
    g = np.random.Generator(np.random.PCG64(seed))
    const_pos = [(k, c) for (k, c) in sl if c == 0]
    Upos = []
    for k in range(NE):
        for c in range(172):
            if (U[k] >> c) & 1:
                Upos.append(k * 172 + c)
    Upos = np.array(Upos, dtype=np.int64)
    kept_hashes = set()
    attempts, kept = [], []
    for slot in range(len(slots)):
        need = {"unsat": True, "sat": True}
        for a in range(256):
            info = {}
            rej = None
            if arm in ("N-CONV", "N-CONV17"):
                bits = g.integers(0, 2, size=len(sl))
                base = qparts[slot] if arm == "N-CONV" else CONV17
                rows = list(base)
                for (k, c), bt in zip(sl, bits.tolist()):
                    if bt:
                        rows[k] |= 1 << c
                if arm == "N-CONV" and rows == s3full[slot]:
                    rej = "identity"
            elif arm == "N-CONVL":
                bits = g.integers(0, 2, size=len(const_pos))
                rows = list(lqparts[slot])
                bprime = 0
                for (k, c), bt in zip(const_pos, bits.tolist()):
                    if bt:
                        rows[k] |= 1
                        bprime |= 1 << k
                info["bprime"] = bprime
                own = [(B >> k) & 1 for (k, c) in const_pos]
                if bits.tolist() == own:
                    rej = "identity"
                elif bprime == 0:
                    rej = "bprime_zero"
            elif arm == "N-ELL144":
                M = np.zeros(17 * 172, dtype=np.int64)
                M[Upos] = g.integers(0, 2, size=Upos.size)
                cc = int(g.integers(0, 2))
                info["c"] = cc
                M = M.reshape(17, 172)
                rows = []
                for k in range(16):
                    rr = 0
                    for c in np.flatnonzero(M[k]).tolist():
                        rr |= 1 << c
                    rows.append(rr)
                rows.append((1 << COLIDX[1]) | (1 << COLIDX[1 << 9]) | cc)
            else:
                raise ValueError(arm)
            Eh = to_hex(rows)
            h = hsha(Eh)
            if rej is None and h in kept_hashes:
                rej = "duplicate"
            rec = {"slot": slot, "attempt": a, "E_sha256": h}
            rec.update(info)
            if rej:
                rec.update(s=None, outcome="rejected:" + rej)
                attempts.append(rec)
                continue
            sols = solutions(rows)
            s = len(sols)
            rec["s"] = s
            if s == 0 and need["unsat"]:
                need["unsat"] = False
                rec["outcome"] = "kept_unsat"
                kept_hashes.add(h)
                kept.append({"slot": slot, "role": "unsat", "attempt": a, "E_sha256": h,
                             "rows": rows, "s": 0, "solutions": []})
            elif s >= 1 and need["sat"]:
                need["sat"] = False
                rec["outcome"] = "kept_sat"
                kept_hashes.add(h)
                kept.append({"slot": slot, "role": "sat", "attempt": a, "E_sha256": h,
                             "rows": rows, "s": s, "solutions": sols})
            else:
                rec["outcome"] = "discarded"
            attempts.append(rec)
            if not need["unsat"] and not need["sat"]:
                break
    return attempts, kept


CONV17 = conv17()
# Seeds transcribed from the specification (instance_sets.fresh_arms), not read
# from any executor-written file.
SEEDS = {"N-CONV": 2026092450101, "N-CONVL": 2026092450102,
         "N-CONV17": 2026092450103, "N-ELL144": 2026092450104}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def rjl(p):
    with gzip.open(p, "rt") as f:
        return [json.loads(l) for l in f if l.strip()]


def wj(p, obj):
    with open(p, "w") as f:
        json.dump(obj, f, indent=1)
        f.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--curve", required=True)
    ap.add_argument("--archived", required=True)
    ap.add_argument("--nell", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    import os
    dev_slots = int(os.environ.get("NCONV_DEV_SLOTS", "0") or 0)
    dev_off = int(os.environ.get("NCONV_DEV_SEED_OFFSET", "0") or 0)
    if (dev_slots or dev_off) and "/experiments/" in str(Path(args.out).resolve()):
        raise SystemExit("development overrides NCONV_DEV_* are set: refusing to write under experiments/")
    t0 = time.time()
    run = Path(args.run)
    out = Path(args.out)
    started = now()
    print(f"[verifier] start {started}", flush=True)
    for mod in list(sys.modules):
        if mod.startswith("crypto_autoresearcher"):
            raise SystemExit("verifier independence violated: crypto_autoresearcher imported")

    curve = json.load(open(args.curve))
    B = int(curve["B"])
    arch = json.load(open(args.archived))
    nell = json.load(open(args.nell))

    # field self-check
    fchk = {"t_order_2^17-1": True,
            "mul_inverse_ok": all(fmul(a, finv(a)) == 1 for a in (1, 2, 3, 12345, 131071)),
            "trace_values_binary": all(ftr(a) in (0, 1) for a in range(1, 2000))}

    # ---- V1: rebuild every system -------------------------------------------
    U = union_support(B)
    sl = [(k, c) for k in range(NE) for c in range(19) if (U[k] >> c) & 1]
    slots_xr = []
    set_order = [("U62", "S3-U62"), ("S62", "S3-S62"), ("C20", "S3-C20")]
    for sname, _ in set_order:
        for r in arch["sets"][sname]:
            slots_xr.append((sname, r["idx"], r["archived"]["x_R"]))
    s3full = [s3_rows(x, B) for (_, _, x) in slots_xr]
    qparts = [[r & QCOLS for r in rows] for rows in s3full]
    lqparts = [[r & ~1 for r in rows] for rows in s3full]  # quad + linear, constant cleared
    xr_ok = len(slots_xr) == 144

    own = {}  # key -> dict(rows, arm, role, s_expected)
    s3_cross = {"checked": 0, "mismatch": []}
    for sname, arm in [("U62", "S3-U62"), ("C20", "S3-C20"), ("S62", "S3-S62"),
                       ("N-AFF62", "NULL-AFF62"), ("N-F262", "NULL-F262")]:
        for r in arch["sets"][sname]:
            rows = [int(h, 16) for h in r["E_hex"]]
            if arm.startswith("S3-"):
                s3_cross["checked"] += 1
                if s3_rows(r["archived"]["x_R"], B) != rows:
                    s3_cross["mismatch"].append(r["key"])
            own[r["key"]] = {"rows": rows, "arm": arm,
                             "role": "unsat" if r["archived"]["s"] == 0 else "sat",
                             "s_archived": r["archived"]["s"]}
    for r in nell["instances"]:
        rows = [int(h, 16) for h in r["E_hex"]]
        own["NELL-A20:" + r["label"]] = {"rows": rows, "arm": "NELL-A20", "role": "unsat",
                                         "s_archived": 0}

    # ---- V3: replay draw streams ------------------------------------------------
    draw_rep = {"arms": {}}
    for arm in ["N-CONV", "N-CONVL", "N-CONV17", "N-ELL144"]:
        ta = time.time()
        seed = SEEDS[arm] + dev_off
        nsl = dev_slots or 144
        attempts, kept = replay_arm(arm, seed, slots_xr[:nsl], B, U, sl, qparts, s3full, lqparts)
        logged = rjl(run / f"draws-{arm}.jsonl.gz")
        fields = ["slot", "attempt", "E_sha256", "s", "outcome"]
        if arm == "N-CONVL":
            fields.append("bprime")
        if arm == "N-ELL144":
            fields.append("c")
        mism = []
        if len(logged) != len(attempts):
            mism.append(f"attempt count {len(logged)} logged vs {len(attempts)} replayed")
        for i, (a, b) in enumerate(zip(logged, attempts)):
            for f in fields:
                if a.get(f) != b.get(f):
                    mism.append(f"line {i} field {f}: logged {a.get(f)} replayed {b.get(f)}")
                    break
            if len(mism) > 20:
                break
        for kp in kept:
            key = f"{arm}:{kp['slot']}:{kp['role']}"
            own[key] = {"rows": kp["rows"], "arm": arm, "role": kp["role"], "s_replay": kp["s"],
                        "attempt": kp["attempt"], "E_sha256": kp["E_sha256"],
                        "solutions": kp["solutions"]}
        exhausted = []
        for slot in range(nsl):
            for role in ("unsat", "sat"):
                if f"{arm}:{slot}:{role}" not in own:
                    exhausted.append(f"{slot}:{role}")
        draw_rep["arms"][arm] = {"seed": seed, "attempts_replayed": len(attempts),
                                 "attempts_logged": len(logged), "kept_replayed": len(kept),
                                 "exhausted": exhausted, "mismatches": mism,
                                 "pass": not mism, "seconds": round(time.time() - ta, 2)}
        print(f"[verifier] V3 {arm}: {len(attempts)} attempts, {len(kept)} kept, "
              f"{len(mism)} mismatches ({time.time() - ta:.1f}s)", flush=True)

    # ---- compare with instances.jsonl.gz (V1, V3 kept systems) --------------------
    inst = rjl(run / "instances.jsonl.gz")
    cons = {"s3_archived_vs_own_construction": s3_cross, "field_selfcheck": fchk,
            "union_support_sizes": [bin(u).count("1") for u in U], "S_L_size": len(sl),
            "xr144_size_144": xr_ok, "xr_mismatch_vs_run": [],
            "systems_checked": 0, "E_mismatch": [], "missing_in_own": [], "missing_in_run": [],
            "kept_attempt_mismatch": [], "per_arm": {}}
    run_keys = set()
    for r in inst:
        key = r["key"]
        run_keys.add(key)
        cons["systems_checked"] += 1
        o = own.get(key)
        pa = cons["per_arm"].setdefault(r["arm"], {"n": 0, "E_equal": 0})
        pa["n"] += 1
        if o is None:
            cons["missing_in_own"].append(key)
            continue
        if to_hex(o["rows"]) != r["E_hex"] or hsha(to_hex(o["rows"])) != r["E_sha256"]:
            cons["E_mismatch"].append(key)
        else:
            pa["E_equal"] += 1
        if r["arm"] in ("N-CONV", "N-CONVL"):
            sname, idx, xr = slots_xr[r["slot"]]
            if (r.get("source_set"), r.get("idx"), r.get("x_R")) != (sname, idx, xr):
                cons["xr_mismatch_vs_run"].append(key)
        if "attempt" in o and (o["attempt"] != r.get("attempt") or o["E_sha256"] != r["E_sha256"]):
            cons["kept_attempt_mismatch"].append(key)
    for k in own:
        if k not in run_keys:
            cons["missing_in_run"].append(k)
    cons["pass_V1"] = (not cons["E_mismatch"] and not cons["missing_in_own"]
                       and not cons["missing_in_run"] and not s3_cross["mismatch"]
                       and xr_ok and not cons["xr_mismatch_vs_run"])
    draw_rep["kept_attempt_mismatch"] = cons["kept_attempt_mismatch"]
    draw_rep["pass"] = all(v["pass"] for v in draw_rep["arms"].values()) and \
        not cons["kept_attempt_mismatch"] and not cons["missing_in_run"]

    # ---- V2: s and solution lists ---------------------------------------------------
    v2 = {"checked": 0, "s_mismatch": [], "solution_list_mismatch": [], "archived_s_mismatch": []}
    tv = time.time()
    for r in inst:
        o = own.get(r["key"])
        if o is None:
            continue
        sols = o.get("solutions")
        if sols is None:
            sols = solutions(o["rows"])
        s = len(sols)
        v2["checked"] += 1
        if s != r["s"]:
            v2["s_mismatch"].append(r["key"])
        if "s_archived" in o and s != o["s_archived"]:
            v2["archived_s_mismatch"].append(r["key"])
        if r["role"] == "sat":
            if sorted(r.get("solutions") or []) != sols:
                v2["solution_list_mismatch"].append(r["key"])
    v2["pass"] = not (v2["s_mismatch"] or v2["solution_list_mismatch"] or v2["archived_s_mismatch"])
    v2["seconds"] = round(time.time() - tv, 2)
    cons["V2"] = v2
    print(f"[verifier] V2: {v2['checked']} systems, pass={v2['pass']}", flush=True)

    Fown = {k: rows_masks(o["rows"]) for k, o in own.items()}

    # ---- V4: certificates -----------------------------------------------------------
    tc = time.time()
    certs = rjl(run / "certificates.jsonl.gz")
    cv = {"certificates": [], "summary": {}}
    ok_ids = set()
    for i, line in enumerate(certs):
        F = Fown.get(line["key"])
        if F is None:
            res = {"format": line["format"], "verified": False, "reason": "system not rebuilt"}
        else:
            res = check_cert(line, F)
        res.update(cid=line.get("cid", i), key=line["key"], arm=line.get("arm"),
                   closure=line["closure"])
        cv["certificates"].append(res)
        if res["verified"]:
            ok_ids.add(res["cid"])
        sk = f"{line['closure']}|{line.get('arm')}|{line['format']}"
        sm = cv["summary"].setdefault(sk, {"submitted": 0, "verified": 0, "failed": 0})
        sm["submitted"] += 1
        sm["verified" if res["verified"] else "failed"] += 1
    cv["n_submitted"] = len(certs)
    cv["n_verified"] = sum(1 for c in cv["certificates"] if c["verified"])
    cv["n_failed"] = cv["n_submitted"] - cv["n_verified"]
    cv["seconds"] = round(time.time() - tc, 2)
    print(f"[verifier] V4: {cv['n_submitted']} certificates, {cv['n_verified']} verified "
          f"({cv['seconds']}s)", flush=True)

    # ---- V5: negative controls ---------------------------------------------------------
    ncp = run / "negative-controls-certificates.jsonl.gz"
    nc = {"controls": [], "accepted": [], "source_not_verified": []}
    if ncp.exists():
        for line in rjl(ncp):
            F = Fown.get(line["key"])
            res = check_cert(line, F) if F is not None else {"verified": False,
                                                            "reason": "system not rebuilt"}
            ent = {"nc_id": line["nc_id"], "kind": line["kind"], "type": line["type"],
                   "key": line["key"], "source_cid": line["source_cid"],
                   "rejected": not res["verified"], "reason": res.get("reason")}
            nc["controls"].append(ent)
            if res["verified"]:
                nc["accepted"].append(line["nc_id"])
            if line["source_cid"] not in ok_ids:
                nc["source_not_verified"].append(line["nc_id"])
    nc["n"] = len(nc["controls"])
    nc["n_rejected"] = sum(1 for c in nc["controls"] if c["rejected"])
    nc["pass"] = nc["n"] > 0 and not nc["accepted"] and not nc["source_not_verified"]

    meta = {"verifier": "experiments/EXP-CERTBIN-ddfe75/verifier/verify_nconv.py",
            "argv": sys.argv, "started": started, "finished": now(),
            "seconds": round(time.time() - t0, 2),
            "dev_overrides": {"NCONV_DEV_SLOTS": dev_slots, "NCONV_DEV_SEED_OFFSET": dev_off},
            "imports_crypto_autoresearcher": any(m.startswith("crypto_autoresearcher") for m in sys.modules),
            "numpy": np.__version__, "python": sys.version.split()[0]}
    cv["meta"] = meta
    cons["meta"] = meta
    draw_rep["meta"] = meta
    nc["meta"] = meta
    wj(out / "certificate-verification.json", cv)
    wj(out / "construction-verification.json", cons)
    wj(out / "draw-replay-verification.json", draw_rep)
    wj(out / "negative-controls-verification.json", nc)
    print(f"[verifier] done: V1 {cons['pass_V1']} V2 {v2['pass']} V3 {draw_rep['pass']} "
          f"certs {cv['n_verified']}/{cv['n_submitted']} NC rejected {nc['n_rejected']}/{nc['n']} "
          f"({meta['seconds']}s)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
