"""J1(f) C-1 T1 at scale: for every j0 prime selected or skipped (R14 rows' j0_generation
logs), count the points of all six twists y^2 = x^3 + g^i (i = 0..5, g a primitive root)
exhaustively with a quadratic-residue table (numpy, chunked; no BSGS; own code, no engine
import). Checks each recorded skip reason, each selected curve's N (= #E(y^2 = x^3 + b)),
N prime, N != p, N > 4*isqrt(p)+4, p = 1 mod 3, bit length, and five distinct primes per rung."""
import gzip, json, math, os, sys
import numpy as np
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
CH = 1 << 20


def is_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):  # deterministic below 3.3e24
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def factor(n):
    f, d = set(), 2
    while d * d <= n:
        while n % d == 0:
            f.add(d)
            n //= d
        d += 1
    if n > 1:
        f.add(n)
    return f


def prim_root(p):
    qs = factor(p - 1)
    g = 2
    while any(pow(g, (p - 1) // q, p) == 1 for q in qs):
        g += 1
    return g


def twist_orders(p, extra_b=()):
    """[#E(y^2 = x^3 + g^i) for i = 0..5] and {b: #E(y^2 = x^3 + b)} for extra b."""
    g = prim_root(p)
    bs = [pow(g, i, p) for i in range(6)] + list(extra_b)
    issq = np.zeros(p, dtype=bool)
    for s in range(0, p, CH):
        x = np.arange(s, min(p, s + CH), dtype=np.int64)
        issq[(x * x) % p] = True
    issq[0] = False  # chi(0) = 0 handled separately
    sums = [0] * len(bs)
    for s in range(0, p, CH):
        x = np.arange(s, min(p, s + CH), dtype=np.int64)
        x3 = ((x * x) % p) * x % p
        for i, b in enumerate(bs):
            v = (x3 + b) % p
            nz = v != 0
            sq = issq[v]
            sums[i] += int(np.count_nonzero(sq)) - int(np.count_nonzero(nz & ~sq))
    orders = [p + 1 + s for s in sums]
    return g, orders[:6], dict(zip(extra_b, orders[6:]))


def accepted(m, p):
    return m != p and m > 4 * math.isqrt(p) + 4 and is_prime(m)


def main():
    p14 = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-j0/rows.jsonl.gz")
    rows = [json.loads(l) for l in gzip.open(rl.opened(p14, "J1(f) C-1: R14 canonical rows (j0_generation logs, p, b, N)"), "rt")]
    cells = {}
    for r in rows:
        k = (r["bits"], r["curve"])
        cells.setdefault(k, {"p": r["p"], "a": r["a"], "b": r["b"], "N": r["N"], "gen": r.get("j0_generation")})
        c = cells[k]
        if (c["p"], c["a"], c["b"], c["N"]) != (r["p"], r["a"], r["b"], r["N"]) or c["gen"] != r.get("j0_generation"):
            c["inconsistent_rows"] = True
    out = {"cells": {}, "problems": [], "primes_counted": 0}
    cache = {}
    for (bits, c), d in sorted(cells.items()):
        gen = d["gen"] or []
        skipped = [e for e in gen if "reason" in e]
        final = [e for e in gen if "prime_draws" in e]
        ent = {"p": d["p"], "b": d["b"], "N": d["N"], "skipped": skipped, "final": final}
        prob = []
        if d.get("inconsistent_rows"):
            prob.append("rows of the job disagree on curve or log")
        if not final or final[-1].get("p") != d["p"] or final[-1].get("b") != d["b"]:
            prob.append("generation log final entry != row curve")
        p = d["p"]
        if p % 3 != 1 or p.bit_length() != bits or d["a"] != 0:
            prob.append("p mod 3, bit length or a")
        if p not in cache:
            cache[p] = twist_orders(p, extra_b=(d["b"],))
            out["primes_counted"] += 1
        g, orders, extra = cache[p]
        ent["twist_orders"] = orders
        ent["selected_curve_order_exhaustive"] = extra.get(d["b"]) if d["b"] in extra else twist_orders(p, (d["b"],))[2][d["b"]]
        if ent["selected_curve_order_exhaustive"] != d["N"]:
            prob.append("exhaustive #E(x^3 + b) != recorded N")
        if not accepted(d["N"], p):
            prob.append("recorded N fails acceptance (prime, != p, > 4 isqrt(p) + 4)")
        if d["N"] not in orders:
            prob.append("N not among the six twist orders")
        for e in skipped:
            q = e["p"]
            if e["reason"] == "no_prime_order_twist":
                if q not in cache:
                    cache[q] = twist_orders(q)
                    out["primes_counted"] += 1
                qo = cache[q][1]
                e_check = {"p": q, "twist_orders": qo, "any_accepted": any(accepted(m, q) for m in qo)}
                if e_check["any_accepted"]:
                    prob.append(f"skip reason no_prime_order_twist contradicted at p={q}")
                if q % 3 != 1 or q.bit_length() != bits:
                    prob.append(f"skipped p={q}: mod 3 or bit length")
                ent.setdefault("skip_checks", []).append(e_check)
            elif e["reason"] == "duplicate_prime":
                lower = [cells[(bits, cc)]["p"] for cc in range(c) if (bits, cc) in cells]
                ok = q in lower
                ent.setdefault("skip_checks", []).append({"p": q, "duplicate_of_lower_index_selected": ok})
                if not ok:
                    prob.append(f"duplicate_prime p={q} not selected by a lower-index curve")
            else:
                prob.append(f"unknown skip reason {e['reason']}")
        ent["problems"] = prob
        out["cells"][f"{bits}|{c}"] = ent
        if prob:
            out["problems"].append([bits, c, prob])
    byb = {}
    for (bits, c), d in cells.items():
        byb.setdefault(bits, []).append(d["p"])
    out["distinct_primes_per_rung"] = {b: len(set(v)) == len(v) == 5 for b, v in sorted(byb.items())}
    out["skipped_total"] = sum(len([e for e in (d["gen"] or []) if "reason" in e]) for d in cells.values())
    with open(os.path.join(W, "checks", "out", "j1f-c1-twists.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print("cells", len(cells), "primes counted", out["primes_counted"], "skipped total", out["skipped_total"],
          "distinct per rung", out["distinct_primes_per_rung"], "problems", out["problems"])


if __name__ == "__main__":
    main()
