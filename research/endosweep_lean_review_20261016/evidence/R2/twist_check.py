"""R2: in F_{q^4}, q = 2^m, does s^2 + s = a + u (a in F_2, u^2+u+1=0) give s + s^q = u (gls.py's psi) or u + 1 (-psi)?"""
def mk(n):
    # find an irreducible polynomial of degree n (brute force, Rabin-free: check no roots-in-subfields via x^(2^n) = x and gcd-free test by order)
    def mulp(a, b, poly):
        r = 0
        while b:
            if b & 1: r ^= a
            b >>= 1; a <<= 1
            if a >> n & 1: a ^= poly
        return r
    def is_irred(poly):
        # x^(2^n) == x mod poly and x^(2^(n/p)) != x for each prime p | n
        def frob_k(k):
            x = 2
            for _ in range(k): x = mulp(x, x, poly)
            return x
        if frob_k(n) != 2: return False
        ps = [p for p in range(2, n + 1) if n % p == 0 and all(p % d for d in range(2, p))]
        return all(frob_k(n // p) != 2 for p in ps)
    for poly in range((1 << n) + 1, 1 << (n + 1), 2):
        if is_irred(poly): return poly, (lambda a, b: mulp(a, b, poly))
for m in (1, 3, 5):
    n = 4 * m
    poly, mul = mk(n)
    def pw(x, e):
        r = 1
        while e:
            if e & 1: r = mul(r, x)
            x = mul(x, x); e >>= 1
        return r
    us = [x for x in range(1 << n) if mul(x, x) ^ x ^ 1 == 0] if n <= 12 else None
    if us is None:   # u = g^((2^n-1)/3) for any g with that power != 1
        g = 2
        while pw(g, ((1 << n) - 1) // 3) == 1: g += 1
        u0 = pw(g, ((1 << n) - 1) // 3); us = [u0, u0 ^ 1]
    u = us[0]
    q = 1 << m
    for a in (0, 1):
        c = a ^ u
        # s with s^2 + s = c: s = sum of c^(2^(2i))... use brute force for small n, else linear solve via trace trick
        if n <= 12:
            s = next(x for x in range(1 << n) if mul(x, x) ^ x == c)
        else:
            # half-trace style: n even, so solve by brute over a random subset is slow; use linear algebra over F_2
            rows = []
            for i in range(n):
                e = 1 << i; rows.append((mul(e, e) ^ e, e))
            # Gaussian elimination: find combination of rows' images equal to c
            basis = {}
            for img, pre in rows:
                while img:
                    hb = img.bit_length() - 1
                    if hb in basis: bi, bp = basis[hb]; img ^= bi; pre ^= bp
                    else: basis[hb] = (img, pre); break
            img, s = c, 0
            while img:
                hb = img.bit_length() - 1
                bi, bp = basis[hb]; img ^= bi; s ^= bp
        assert mul(s, s) ^ s == c
        t = s ^ pw(s, q)
        print(f"m={m} (m mod 4 = {m % 4}), a={a}: s + s^q == u ? {t == u};  == u+1 ? {t == u ^ 1}")
