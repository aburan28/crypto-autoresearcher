import sys; sys.path.insert(0, "/tmp/claude-0/validator2/work")
from solparse import *
for name in ("t1", "t7"):
    d = parse_sol(open(f"/tmp/claude-0/validator2/evaltest/{name}.sol").read())
    p, nv, deg, vars_, lin, rest = d[1][0], d[1][1], d[1][2], d[1][3], d[1][4], d[1][5]
    w = rest[1][0][1]; den = rest[1][1]; params = rest[1][2]
    ts = poly_roots_fp(w, p)
    print(name, "vars", vars_, "lin", lin, "deg", deg, "w", w, "den", den, "roots T", ts)
    # derivative of w
    wd = [i * c % p for i, c in enumerate(w)][1:]
    for t in ts:
        vals = [sum(c * pow(t, i, p) for i, c in enumerate(pp[0][1])) % p for pp in params]
        wdt = sum(c * pow(t, i, p) for i, c in enumerate(wd)) % p
        print("  t", t, "raw", vals, "-v/w'", [(-v * pow(wdt, -1, p)) % p for v in vals], "v/w'", [(v * pow(wdt, -1, p)) % p for v in vals])
