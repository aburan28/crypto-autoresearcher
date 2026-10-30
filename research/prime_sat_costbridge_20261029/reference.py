"""Certified two-summand reference, conditional on the input p being prime.

No primality proof, scalar recovery, benchmark, or constant-time claim.  The
checker is a separate implementation and does not import this module.
"""
import argparse
import hashlib
import json


def _integer(value, name):
    if type(value) is not int:
        raise ValueError(name + " must be an integer (not bool)")
    return value


def _canonical(value, p, name):
    value = _integer(value, name)
    if not 0 <= value < p:
        raise ValueError(name + " must be canonical modulo p")
    return value


class _Domain:
    def __init__(self, spec, p):
        self.p = p
        if type(spec) is list:
            self.values = tuple(_canonical(x, p, "domain coordinate") for x in spec)
            self.index = set(self.values)
            if len(self.index) != len(self.values):
                raise ValueError("duplicate explicit domain coordinate")
            self.size = len(self.values)
        elif type(spec) is dict and set(spec) == {"kind", "offset", "size"}:
            if spec["kind"] != "interval":
                raise ValueError("unsupported domain kind")
            self.offset = _canonical(spec["offset"], p, "interval offset")
            self.size = _integer(spec["size"], "interval size")
            if not 0 <= self.size <= p:
                raise ValueError("interval size outside [0,p]")
            self.values = None
        else:
            raise ValueError("domain must be a list or modular interval")

    def __iter__(self):
        if self.values is not None:
            yield from self.values
        else:
            for i in range(self.size):
                yield (self.offset + i) % self.p

    def contains(self, x):
        if self.values is not None:
            return x in self.index
        return (x - self.offset) % self.p < self.size


def _parse(instance):
    if type(instance) is not dict:
        raise ValueError("instance must be an object")
    required = {"p", "a", "b", "target", "D1", "D2"}
    if not required <= set(instance) or set(instance) - required - {"nonresidue"}:
        raise ValueError("wrong instance fields")
    p = _integer(instance["p"], "p")
    if p <= 3 or p % 2 == 0:
        raise ValueError("p must be a prime greater than 3; primality is assumed")
    a = _integer(instance["a"], "a") % p
    b = _integer(instance["b"], "b") % p
    if (4 * a**3 + 27 * b**2) % p == 0:
        raise ValueError("singular curve")
    R = instance["target"]
    if type(R) is not list or len(R) != 2:
        raise ValueError("target must be [r,t]")
    r, t = (_canonical(v, p, "target coordinate") for v in R)
    if t == 0 or (t*t - r**3 - a*r - b) % p:
        raise ValueError("target must be on curve with t != 0")
    if "nonresidue" in instance:
        _canonical(instance["nonresidue"], p, "nonresidue")
    return p, a, b, (r, t), _Domain(instance["D1"], p), _Domain(instance["D2"], p)


def _nonsquare(p, supplied):
    if supplied is not None:
        z = _canonical(supplied, p, "nonresidue")
        if pow(z, (p - 1)//2, p) != p - 1:
            raise ValueError("supplied nonresidue fails Euler certification")
        return z, "supplied", 1
    if p % 4 == 3:
        z = p - 1
        if pow(z, (p - 1)//2, p) != p - 1:
            raise ValueError("prime premise failed during nonsquare setup")
        return z, "minus_one", 1
    probes = 0
    for z in range(2, p):
        probes += 1
        if pow(z, (p - 1)//2, p) == p - 1:
            return z, "deterministic_scan", probes
    raise ValueError("prime premise failed: no Euler-certified nonsquare")


def _sqrt_square(a, p, z):
    """Tonelli-Shanks for a known nonzero square and a verified nonsquare z."""
    if p % 4 == 3:
        root = pow(a, (p + 1)//4, p)
    else:
        odd, exponent = p - 1, 0
        while odd % 2 == 0:
            odd //= 2
            exponent += 1
        c = pow(z, odd, p)
        root = pow(a, (odd + 1)//2, p)
        residue = pow(a, odd, p)
        m = exponent
        while residue != 1:
            power, i = residue, 0
            while power != 1 and i < m:
                power = power * power % p
                i += 1
            if i == m:
                raise ValueError("square-root invariant failed")
            factor = pow(c, 1 << (m - i - 1), p)
            root = root * factor % p
            c = factor * factor % p
            residue = residue * c % p
            m = i
    if root * root % p != a:
        raise ValueError("square-root verification failed")
    return root


def _add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x, y = P
    u, v = Q
    if x == u:
        if (y + v) % p == 0:
            return None
        slope = (3*x*x + a) * pow(2*y, -1, p) % p
    else:
        slope = (v - y) * pow(u - x, -1, p) % p
    rx = (slope*slope - x - u) % p
    return rx, (slope*(x - rx) - y) % p


def solve(instance, mode="all"):
    """Return all projected models with coverage certificates, or one witness.

    A successful result is conditional on p prime.  First mode always has
    complete=False, even when it exhausts D1 without finding a witness.
    """
    if mode not in ("all", "first"):
        raise ValueError("mode must be all or first")
    p, a, b, R, d1, d2 = _parse(instance)
    z, method, probes = _nonsquare(p, instance.get("nonresidue"))
    records, found = [], {}
    stop = False
    for x in d1:
        value = (x**3 + a*x + b) % p
        if value == 0:
            roots = [0]
            record = {"x": x, "kind": "zero", "roots": roots}
        else:
            symbol = pow(value, (p - 1)//2, p)
            if symbol == 1:
                y = _sqrt_square(value, p, z)
                roots = sorted({y, (-y) % p})
                record = {"x": x, "kind": "square", "roots": roots}
            elif symbol == p - 1:
                roots = []
                w = _sqrt_square(z * value % p, p, z)
                record = {"x": x, "kind": "nonsquare", "twisted_root": w}
            else:
                raise ValueError("prime premise failed during Euler test")
        records.append(record)
        for y in roots:
            Q = _add(R, (x, (-y) % p), a, p)
            if Q is not None and d2.contains(Q[0]):
                pair = (x, Q[0])
                found.setdefault(pair, {"P": [x, y], "Q": list(Q)})
                if mode == "first":
                    stop = True
                    break
        if stop:
            break
    pairs = sorted(found)
    digest = hashlib.sha256(json.dumps(instance, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schema": "prime-complement-reference/v1", "mode": mode,
        "input_sha256": digest, "complete": mode == "all",
        "prime_assumed": True, "primality_verified": False,
        "setup": {"nonresidue": z, "method": method, "euler_probes": probes},
        "lift_records": records, "projected_pairs": [list(v) for v in pairs],
        "witnesses": [found[v] for v in pairs],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=("all", "first"), default="all")
    args = parser.parse_args()
    with open(args.input) as f:
        result = solve(json.load(f), args.mode)
    with open(args.output, "x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
