import json, hashlib, sys
d = sys.argv[1]
def isprime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True
bad = 0; n = 0; plist = {}
for r in ("01", "02", "03"):
    for l in open(f"{d}/runs/RUN-ECDLP-f49f75-{r}/raw-result.jsonl"):
        x = json.loads(l); n += 1
        m, L = x["m"], x["L"]
        s = int(hashlib.sha256(f"EXP-ECDLP-f49f75/v1|{m}|{L}|{x['inst']}".encode()).hexdigest()[:12], 16)
        q = 2 ** (m * L) + 1
        while not (isprime(q) and q % 4 == 3 and (q + 1) % 2 ** L == 0): q += 1
        ok = (s == x["seed"] and q == x["p"] and x["p"].bit_length() == x["p_bits"] and x["timeout"] == 600
              and x["kind"] == ("planted" if x["inst"] < 4 else "random") and x["solvers"] == ["std", "slimgb"])
        bad += not ok
        plist[(m, L)] = x["p"]
print("rows", n, "param mismatches", bad)
print({f"m{m}L{L}": f"{p} ({p.bit_length()}b)" for (m, L), p in sorted(plist.items())})
