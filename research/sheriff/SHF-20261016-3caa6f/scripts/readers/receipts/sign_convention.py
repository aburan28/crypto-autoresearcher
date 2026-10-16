import sys, json, hashlib, importlib.util
spec = importlib.util.spec_from_file_location("kv", sys.argv[1])
# reuse arithmetic by exec of the function defs only
src = open(sys.argv[1]).read().split("# Koblitz order")[0]
sys.argv = [sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]]
g = {"__name__": "x"}
exec(src, g)
targets = g["targets"]; M=g["M"]; A=g["A"]; H=g["H"]
fsq, finv, fmul, trace, halftrace, mul = g["fsq"], g["finv"], g["fmul"], g["trace"], g["halftrace"], g["mul"]
res = {}
for p in targets["points"]:
    Q = tuple(int(v) for v in p["point"]); seed = p["seed"]; c0 = 0
    while True:
        dig = hashlib.sha256(("%s|%s|%d|%d" % (targets["domain"], targets["role"], seed, c0)).encode()).digest()
        x = int.from_bytes(dig[0:8], "little") % (1 << M)
        c = x ^ A ^ fsq(finv(x))
        if x and trace(c) == 0: break
        c0 += 1
    z = halftrace(c); bit = dig[8] & 1
    cands = {"z_bit0_eq": z if (z & 1) == bit else z ^ 1, "z_bit0_ne": z if (z & 1) != bit else z ^ 1,
             "y_bit0_eq": None, "halftrace_flip_if_bit": z ^ bit}
    y0, y1 = fmul(x, z), fmul(x, z ^ 1)
    cands_y = {k: fmul(x, v) for k, v in cands.items() if v is not None}
    cands_y["y_bit0_eq"] = y0 if (y0 & 1) == bit else y1
    cands_y["y_bit0_ne"] = y0 if (y0 & 1) != bit else y1
    for k, y in cands_y.items():
        res.setdefault(k, 0)
        res[k] += mul(H, (x, y)) == Q
print(res, "of", len(targets["points"]))
