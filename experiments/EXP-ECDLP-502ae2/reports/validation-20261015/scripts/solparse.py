"""Independent parsers (no eval of producer code): msolve GB text, msolve -P 1 parametrization, input polys."""
import ast, re
def parse_poly(s):
    """'c*x^a*y^b+...' (signs +/-; implicit coeff 1) -> list of (coeff, {var: exp})."""
    s = s.replace(" ", "").replace("\n", "")
    terms, i, out = re.findall(r"[+-]?[^+-]+", s), 0, []
    for t in terms:
        sign = -1 if t.startswith("-") else 1
        t = t.lstrip("+-")
        c, mono = 1, {}
        for f in t.split("*"):
            if re.fullmatch(r"\d+", f):
                c *= int(f)
            else:
                v, _, e = f.partition("^")
                mono[v] = mono.get(v, 0) + (int(e) if e else 1)
        out.append((sign * c, mono))
    return out
def n_const_terms(s):
    return sum(1 for c, mono in parse_poly(s) if not mono)
def eval_poly(terms, pt, p):
    acc = 0
    for c, mono in terms:
        v = c
        for x, e in mono.items():
            v = v * pow(pt[x], e, p) % p
        acc = (acc + v) % p
    return acc
def gb_polys(text):
    lines = [l for l in text.splitlines() if not l.startswith("#")]
    body = "".join(lines).strip()
    assert body.startswith("[") and body.endswith("]:"), body[:80]
    inner = body[1:-2]
    return [x for x in inner.split(",") if x]
def parse_sol(text):
    body = text.strip()
    assert body.endswith(":")
    return ast.literal_eval(body[:-1])
def poly_roots_fp(coeffs, p):
    """roots in F_p of sum coeffs[i] T^i by gcd with T^p - T (small p ok via brute force if p small)."""
    # use polynomial arithmetic: gcd(f, T^p - T)
    def trim(a):
        while a and a[-1] % p == 0: a.pop()
        return a
    def mulmod(a, b, f):
        r = [0] * (len(a) + len(b) - 1) if a and b else []
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    r[i + j] = (r[i + j] + x * y) % p
        return polymod(r, f)
    def polymod(a, f):
        a = trim(list(a)); f = trim(list(f)); inv = pow(f[-1], -1, p)
        while len(a) >= len(f):
            q = a[-1] * inv % p; d = len(a) - len(f)
            for i, y in enumerate(f):
                a[d + i] = (a[d + i] - q * y) % p
            a = trim(a)
        return a
    def gcd(a, b):
        a, b = trim(list(a)), trim(list(b))
        while b:
            a, b = b, polymod(a, b)
        return a
    f = trim([c % p for c in coeffs])
    # T^p mod f by square and multiply
    r, base, e = [1], [0, 1], p
    while e:
        if e & 1: r = mulmod(r, base, f)
        base = mulmod(base, base, f); e >>= 1
    r = r + [0] * max(0, 2 - len(r)); r[1] = (r[1] - 1) % p
    g = gcd(f, trim(r))
    return [t for t in range(p) if not sum(c * pow(t, i, p) for i, c in enumerate(g)) % p] if len(g) > 1 and p < 5_000_000 else []
