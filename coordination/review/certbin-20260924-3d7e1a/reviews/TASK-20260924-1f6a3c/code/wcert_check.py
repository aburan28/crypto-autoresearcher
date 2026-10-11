"""Independent checker for "certbin.wcert.v1" W-certificates (card BR-5).

Imports NOTHING from the closure engine (gf2n, boolsys, gf2lin, closure). It has
its own F_{2^17} arithmetic, builds f_0..f_16 from a HAND-EXPANDED formula of
S_3 (not the generic polynomial product used by the engine), and does its own
Boolean-ring arithmetic on sets of monomial masks.

Hand expansion (v Boolean, so x_1^2 = sum_i v_i t^{2i} and x_2^2 = sum_j v_{9+j} t^{2j}):
  S_3 = x1^2 x2^2 + x1^2 x3^2 + x2^2 x3^2 + x1 x2 x3 + B
  constant        : B
  v_i      (i<9)  : t^{2i} * x3^2
  v_{9+j}  (j<9)  : t^{2j} * x3^2
  v_i v_{9+j}     : t^{2i+2j} + t^{i+j} * x3
Equation k is the set of monomials whose coefficient has t^k.

Element semantics: g_id = sum_{(mu,k) in rows} mu*f_k + sum_{(j,p) in products} v_j*g_p.
Valid iff: every mu has degree <= 2 (and D == 4); every parent p is an EARLIER
element; every parent used has degree <= 3; every g_id has degree <= 4; and
g_{output_id} is exactly the constant 1.
"""
import gzip
import json
import sys

_MOD = 0b100000000000001001  # t^17 + t^3 + 1
_NV = 18


def _fmul(a, b):
    r = 0
    for i in range(17):
        if (b >> i) & 1:
            r ^= a << i
    for d in range(32, 16, -1):
        if (r >> d) & 1:
            r ^= _MOD << (d - 17)
    return r


def _tpow(e):
    """t^e reduced mod f."""
    r = 1
    for _ in range(e):
        r <<= 1
        if r >> 17:
            r ^= _MOD
    return r


def equations_curve(xR, B):
    x3sq = _fmul(xR, xR)
    coef = {0: B}
    for i in range(9):
        c = _fmul(_tpow(2 * i), x3sq)
        coef[1 << i] = coef.get(1 << i, 0) ^ c
        coef[1 << (9 + i)] = coef.get(1 << (9 + i), 0) ^ c
    for i in range(9):
        for j in range(9):
            c = _tpow(2 * i + 2 * j) ^ _fmul(_tpow(i + j), xR)
            m = (1 << i) | (1 << (9 + j))
            coef[m] = coef.get(m, 0) ^ c
    eqs = [set() for _ in range(17)]
    for m, c in coef.items():
        for k in range(17):
            if (c >> k) & 1:
                eqs[k].add(m)
    return [frozenset(e) for e in eqs]


def equations_explicit(eq_lists):
    eqs = []
    for eq in eq_lists:
        s = set()
        for mon in eq:
            m = 0
            for i in mon:
                m |= 1 << i
            s ^= {m}
        eqs.append(frozenset(s))
    return eqs


def _deg(poly):
    return max((bin(m).count("1") for m in poly), default=-1)


def check(cert, eqs):
    """Return (accepted: bool, reason: str, stats: dict)."""
    stats = {"n_elements": 0, "n_row_refs": 0, "n_product_refs": 0,
             "max_deg_mu": -1, "max_deg_element": -1, "max_deg_parent": -1}
    try:
        if cert.get("D") != 4:
            return False, "D is not 4", stats
        elements = cert["elements"]
        out_id = cert["output_id"]
        polys = {}
        rowcache = {}
        for el in elements:
            eid = el["id"]
            if eid in polys:
                return False, "duplicate id %r" % (eid,), stats
            g = set()
            for mu, k in el["rows"]:
                if not isinstance(k, int) or not (0 <= k < 17):
                    return False, "bad k %r" % (k,), stats
                if list(mu) != sorted(set(mu)) or any((not isinstance(i, int)) or i < 0 or i >= _NV for i in mu):
                    return False, "bad mu %r" % (mu,), stats
                if len(mu) > 2:
                    return False, "mu of degree %d > 2 (not an M_4 row)" % len(mu), stats
                stats["max_deg_mu"] = max(stats["max_deg_mu"], len(mu))
                key = (tuple(mu), k)
                rp = rowcache.get(key)
                if rp is None:
                    mm = 0
                    for i in mu:
                        mm |= 1 << i
                    acc = set()
                    for m in eqs[k]:
                        acc ^= {m | mm}
                    rp = frozenset(acc)
                    rowcache[key] = rp
                g ^= rp
                stats["n_row_refs"] += 1
            for j, p in el["products"]:
                if not isinstance(j, int) or not (0 <= j < _NV):
                    return False, "bad j %r" % (j,), stats
                if p not in polys:
                    return False, "parent %r is not an EARLIER element of %r" % (p, eid), stats
                gp = polys[p]
                dp = _deg(gp)
                if dp > 3:
                    return False, "parent %r has degree %d > 3" % (p, dp), stats
                stats["max_deg_parent"] = max(stats["max_deg_parent"], dp)
                bj = 1 << j
                prod = set()
                for m in gp:
                    prod ^= {m | bj}
                g ^= prod
                stats["n_product_refs"] += 1
            dg = _deg(g)
            if dg > 4:
                return False, "element %r has degree %d > 4" % (eid, dg), stats
            stats["max_deg_element"] = max(stats["max_deg_element"], dg)
            polys[eid] = frozenset(g)
            stats["n_elements"] += 1
        if out_id not in polys:
            return False, "output_id not defined", stats
        if polys[out_id] != frozenset({0}):
            return False, "output element is not exactly the constant 1", stats
        return True, "ok", stats
    except Exception as exc:  # malformed record
        return False, "malformed: %r" % (exc,), stats


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--certs", required=True)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    inp = json.load(open(a.inputs))
    B = inp["curve"]["B"]
    by_label = {i["label"]: i for i in inp["instances"]}
    results = {}
    with gzip.open(a.certs, "rt") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("schema") != "certbin.wcert.v1":
                results[rec.get("label")] = {"accepted": False, "reason": "schema"}
                continue
            inst = by_label[rec["label"]]
            eqs = (equations_curve(inst["x_R"], B) if inst["kind"] == "curve"
                   else equations_explicit(inst["equations"]))
            ok, reason, stats = check(rec, eqs)
            results[rec["label"]] = {"accepted": ok, "reason": reason, **stats}
    json.dump(results, open(a.out, "w"), indent=1, sort_keys=True)
    n_ok = sum(1 for r in results.values() if r["accepted"])
    print("checked %d certificates, accepted %d" % (len(results), n_ok))


if __name__ == "__main__":
    main(sys.argv[1:])
