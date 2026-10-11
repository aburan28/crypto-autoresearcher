"""Independent checker for wdag-v1 certificates (EXP-CERTBIN-ddfe75
object.certificate_format), written from the text alone.

A certificate {"D": 4, "nv": 18, "nodes": [...], "output": o} defines
  poly(i) = sum_{(mu,k) in rows} mu*f_k + sum_{(j,c) in prods} v_j * poly(c)  in B.
VALID iff
  (a) every child id c is less than i (topological order);
  (b) every |mu| <= D - 2 and every k is in 0..16;
  (c) every child c used in prods has deg poly(c) <= D - 1;
  (d) every node has deg poly(i) <= D;
  (e) poly(output) == 1.

This module shares NO arithmetic with the elimination engine: polynomials are
Python sets of monomial bitmasks, multiplication is bitwise OR of masks with
XOR (symmetric difference) accumulation, and f_k is read from the system's
own monomial lists.
"""


def _toggle_all(s, items):
    """XOR-accumulate items into the set s, respecting multiplicity (a
    monomial produced twice cancels)."""
    for x in items:
        if x in s:
            s.remove(x)
        else:
            s.add(x)


def _deg(poly):
    return max((bin(m).count("1") for m in poly), default=-1)   # deg 0 = -1


class Checker:
    def __init__(self, equations, D=4, nv=18, neq=17):
        """equations: list of neq lists of monomials (index lists)."""
        self.D, self.nv, self.neq = D, nv, neq
        self.f = []
        for eq in equations:
            s = set()
            ms = []
            for mono in eq:
                m = 0
                for i in mono:
                    m |= 1 << int(i)
                ms.append(m)
            _toggle_all(s, ms)
            self.f.append(frozenset(s))
        self._cache = {}

    def _row(self, mumask, k):
        key = (mumask, k)
        r = self._cache.get(key)
        if r is None:
            s = set()
            _toggle_all(s, (m | mumask for m in self.f[k]))
            r = frozenset(s)
            self._cache[key] = r
        return r

    def check(self, cert):
        """Returns dict: valid, failures (list of 'a'..'e' / 'format' with
        details), node_count, row_count, max_mu, max_child_degree, and the
        degree of every node."""
        fails = []

        def fail(rule, msg):
            fails.append({"rule": rule, "detail": msg})

        D, nv, neq = self.D, self.nv, self.neq
        if cert.get("D") != D or cert.get("nv") != nv:
            fail("format", "D/nv header mismatch: %r/%r" % (cert.get("D"), cert.get("nv")))
        nodes = cert.get("nodes")
        if not isinstance(nodes, list) or not nodes:
            fail("format", "no nodes")
            return self._result(fails, {}, cert)
        byid = {}
        for pos, nd in enumerate(nodes):
            nid = nd.get("id")
            if not isinstance(nid, int) or nid in byid:
                fail("format", "bad or duplicate node id at position %d" % pos)
                continue
            byid[nid] = nd
        out = cert.get("output")
        if out not in byid:
            fail("format", "output id %r is not a node" % (out,))
        # rule (a) and (b), and structure
        max_mu = 0
        nrows = 0
        for nid, nd in byid.items():
            for pr in nd.get("prods", []):
                j, c = pr
                if not (isinstance(j, int) and 0 <= j < nv):
                    fail("format", "node %d: variable index %r out of range" % (nid, j))
                if c not in byid:
                    fail("a", "node %d: child %r does not exist" % (nid, c))
                elif not c < nid:
                    fail("a", "node %d: child %d is not less than %d" % (nid, c, nid))
            for rw in nd.get("rows", []):
                mu, k = rw
                nrows += 1
                max_mu = max(max_mu, len(mu))
                if len(mu) > D - 2:
                    fail("b", "node %d: |mu| = %d > %d" % (nid, len(mu), D - 2))
                if not (isinstance(k, int) and 0 <= k < neq):
                    fail("b", "node %d: k = %r not in 0..%d" % (nid, k, neq - 1))
                if list(mu) != sorted(set(mu)) or any(not (0 <= i < nv) for i in mu):
                    fail("format", "node %d: mu %r not a sorted index list" % (nid, mu))
        # polynomials (memoized recursion; a cycle is a rule (a) failure)
        polys = {}
        state = {}

        def poly(nid):
            if nid in polys:
                return polys[nid]
            if state.get(nid) == "open":
                raise RecursionError("cycle at node %d" % nid)
            state[nid] = "open"
            nd = byid[nid]
            s = set()
            for mu, k in nd.get("rows", []):
                if not (isinstance(k, int) and 0 <= k < neq):
                    continue                     # already a rule (b) failure
                mm = 0
                for i in mu:
                    mm |= 1 << int(i)
                s ^= self._row(mm, k)
            for j, c in nd.get("prods", []):
                if c not in byid:
                    continue
                pc = poly(c)
                bit = 1 << int(j)
                t = set()
                _toggle_all(t, (m | bit for m in pc))
                s ^= t
            polys[nid] = frozenset(s)
            state[nid] = "done"
            return polys[nid]

        degs = {}
        try:
            for nid in sorted(byid):
                degs[nid] = _deg(poly(nid))
        except RecursionError as e:
            fail("a", "cyclic references: %s" % e)
            return self._result(fails, degs, cert, nrows, max_mu)
        max_child_deg = -1
        for nid, nd in byid.items():
            for j, c in nd.get("prods", []):
                if c in degs:
                    max_child_deg = max(max_child_deg, degs[c])
                    if degs[c] > D - 1:
                        fail("c", "node %d: child %d has degree %d > %d" % (nid, c, degs[c], D - 1))
            if degs[nid] > D:
                fail("d", "node %d has degree %d > %d" % (nid, degs[nid], D))
        if out in byid:
            if polys[out] != frozenset({0}):
                fail("e", "poly(output) != 1 (it has %d monomials, degree %d)" % (len(polys[out]), degs[out]))
        return self._result(fails, degs, cert, nrows, max_mu, max_child_deg)

    @staticmethod
    def _result(fails, degs, cert, nrows=0, max_mu=0, max_child_deg=-1):
        return {
            "valid": not fails,
            "failures": fails,
            "failed_rules": sorted(set(f["rule"] for f in fails)),
            "node_count": len(cert.get("nodes") or []),
            "row_count": nrows,
            "max_mu": max_mu,
            "max_child_degree": max_child_deg,
        }
