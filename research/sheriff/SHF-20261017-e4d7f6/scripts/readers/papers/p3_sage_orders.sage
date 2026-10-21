# Independent #E table for y^2 = x^3 + b over F_p, 5 <= p < 500 (PARI via Sage).
import json, sys
out = {}
for p in prime_range(5, 500):
    F = GF(p)
    out[str(p)] = {str(b): int(EllipticCurve(F, [0, b]).order()) for b in range(1, p)}
json.dump(out, open(sys.argv[1], "w"))
print("curves:", sum(len(v) for v in out.values()))
