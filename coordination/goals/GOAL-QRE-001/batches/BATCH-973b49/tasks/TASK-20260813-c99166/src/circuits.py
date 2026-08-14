"""Reversible-circuit library for TASK-20260813-c99166 (GOAL-QRE-001).

ONE circuit description, TWO consumers.  Every circuit below is emitted by a
single builder into an abstract machine.  The machine is either

  * a TALLY  (Machine(run=False)) -- counts X / CNOT / CCX and tracks qubit
    allocation, executing nothing; or
  * a RUNNER (Machine(run=True))  -- executes the identical gate stream on a
    classical bit vector and refuses to free an ancilla that is not |0>.

The builder cannot tell the two apart: the circuit that is counted IS the
circuit that is simulated.  See PREREGISTRATION.md clauses 1, 3, 4, 8, 9.

Gate set: X, CNOT, CCX only (PREREGISTRATION clause 1).
No constant in this file is taken from any publication; every sub-circuit is
constructed here and its correctness is established by simulation.
"""


class DirtyAncilla(Exception):
    """Raised when a register is released without being returned to |0>."""


class Machine:
    def __init__(self, run=False):
        self.run = run
        self.bits = []
        self.free_pool = []
        self.live = 0
        self.peak = 0
        self.io = 0
        self.counts = {"x": 0, "cnot": 0, "ccx": 0}
        self._rec = []

    # ---------------- qubit management ----------------
    def alloc(self, n=1, io=False):
        qs = []
        for _ in range(n):
            if self.free_pool:
                q = self.free_pool.pop()
            else:
                q = len(self.bits)
                self.bits.append(0)
            qs.append(q)
        self.live += n
        if io:
            self.io += n
        if self.live > self.peak:
            self.peak = self.live
        return qs

    def free(self, qs):
        for q in qs:
            if self.run and self.bits[q] != 0:
                raise DirtyAncilla("qubit %d released in state 1" % q)
            self.free_pool.append(q)
        self.live -= len(qs)

    # ---------------- state preparation / readout (NOT circuit gates) -------
    def prepare(self, reg, value):
        for j, q in enumerate(reg):
            self.bits[q] = (value >> j) & 1

    def read(self, reg):
        v = 0
        for j, q in enumerate(reg):
            v |= self.bits[q] << j
        return v

    # ---------------- gates ----------------
    def _emit(self, op):
        if self._rec:
            self._rec[-1].append(op)
            return
        k = op[0]
        self.counts[k] += 1
        if self.run:
            b = self.bits
            if k == "x":
                b[op[1]] ^= 1
            elif k == "cnot":
                b[op[2]] ^= b[op[1]]
            else:
                b[op[3]] ^= b[op[1]] & b[op[2]]

    def x(self, a):
        self._emit(("x", a))

    def cnot(self, a, b):
        assert a != b
        self._emit(("cnot", a, b))

    def ccx(self, a, b, c):
        assert a != b and a != c and b != c
        self._emit(("ccx", a, b, c))

    def swap(self, a, b):
        self.cnot(a, b)
        self.cnot(b, a)
        self.cnot(a, b)

    # ---------------- capture / replay / inverse ----------------
    # Gate ops are buffered; qubit alloc/free happen for real during capture,
    # so ancilla reuse and the peak-qubit figure are unaffected by capturing.
    # Every gate in the set is an involution, so the inverse of a circuit is
    # its gate list reversed.
    def capture(self, fn, *args, **kw):
        self._rec.append([])
        try:
            ret = fn(self, *args, **kw)
        finally:
            ops = self._rec.pop()
        return ops, ret

    def replay(self, ops, invert=False):
        for op in (reversed(ops) if invert else ops):
            self._emit(op)

    def inverse(self, fn, *args, **kw):
        ops, _ = self.capture(fn, *args, **kw)
        self.replay(ops, invert=True)


# =====================================================================
# integer arithmetic mod 2^n
# =====================================================================

def add(m, a, b, cout=None):
    """b <- b + a  (mod 2^n); if cout is given it is XORed with the carry-out.
    Register a is preserved.  1 clean ancilla, 2n Toffoli."""
    n = len(a)
    assert len(b) == n
    (c0,) = m.alloc(1)
    prev = c0
    for i in range(n):
        # MAJ(prev, b[i], a[i]) : a[i] becomes carry_{i+1}
        m.cnot(a[i], b[i])
        m.cnot(a[i], prev)
        m.ccx(prev, b[i], a[i])
        prev = a[i]
    if cout is not None:
        m.cnot(a[n - 1], cout)
    for i in reversed(range(n)):
        prev = c0 if i == 0 else a[i - 1]
        # UMA(prev, b[i], a[i])
        m.ccx(prev, b[i], a[i])
        m.cnot(a[i], prev)
        m.cnot(prev, b[i])
    m.free([c0])


def sub(m, a, b, cout=None):
    """b <- b - a (mod 2^n)."""
    m.inverse(add, a, b, cout)


def add_const(m, c, b):
    """b <- b + c (mod 2^n), c classical.  Constant loaded with X gates."""
    n = len(b)
    c &= (1 << n) - 1
    reg = m.alloc(n)
    for j in range(n):
        if (c >> j) & 1:
            m.x(reg[j])
    add(m, reg, b)
    for j in range(n):
        if (c >> j) & 1:
            m.x(reg[j])
    m.free(reg)


def sub_const(m, c, b):
    m.inverse(add_const, c, b)


# =====================================================================
# arithmetic mod a classical odd modulus M
# =====================================================================

def mod_add(m, A, B, M):
    """B <- (A + B) mod M.  Requires 0 <= A < M, 0 <= B < M, M odd, M < 2^n.
    A preserved.  Five general-adder passes (PREREGISTRATION clause 7)."""
    n = len(A)
    assert len(B) == n
    (zA,) = m.alloc(1)
    (z,) = m.alloc(1)
    Ax = A + [zA]
    Bx = B + [z]
    add(m, Ax, Bx)              # B = A+B, no overflow of n+1 bits
    sub_const(m, M, Bx)         # B = A+B-M ; z = 1 iff A+B < M
    (t,) = m.alloc(1)
    m.cnot(z, t)
    C = m.alloc(n + 1)          # conditional add of M back
    for j in range(n + 1):
        if (M >> j) & 1:
            m.cnot(t, C[j])
    add(m, C, Bx)
    for j in range(n + 1):
        if (M >> j) & 1:
            m.cnot(t, C[j])
    m.free(C)
    # uncompute t:  t = 1  <=>  no reduction happened  <=>  result >= A
    sub(m, Ax, Bx)
    m.x(z)
    m.cnot(z, t)
    m.x(z)
    add(m, Ax, Bx)
    m.free([t])
    m.free([z])
    m.free([zA])


def mod_sub(m, A, B, M):
    """B <- (B - A) mod M."""
    m.inverse(mod_add, A, B, M)


def mod_add_const(m, c, B, M):
    """B <- (B + c) mod M, c classical with 0 <= c < M."""
    n = len(B)
    reg = m.alloc(n)
    for j in range(n):
        if (c >> j) & 1:
            m.x(reg[j])
    mod_add(m, reg, B, M)
    for j in range(n):
        if (c >> j) & 1:
            m.x(reg[j])
    m.free(reg)


def mod_sub_const(m, c, B, M):
    m.inverse(mod_add_const, c, B, M)


def mod_neg(m, B, M):
    """B <- (M - B) mod 2^n.  Correct as negation mod M for 0 < B < M."""
    n = len(B)
    for q in B:
        m.x(q)
    add_const(m, (M + 1) % (1 << n), B)


def mod_dbl(m, B, M):
    """B <- 2B mod M.  Requires 0 <= B < M, M odd."""
    n = len(B)
    (z,) = m.alloc(1)
    R = B + [z]
    for i in range(n, 0, -1):       # cyclic left rotation == multiply by 2
        m.swap(R[i], R[i - 1])
    sub_const(m, M, R)              # R = 2B - M ; z = 1 iff 2B < M
    (t,) = m.alloc(1)
    m.cnot(z, t)
    C = m.alloc(n + 1)
    for j in range(n + 1):
        if (M >> j) & 1:
            m.cnot(t, C[j])
    add(m, C, R)
    for j in range(n + 1):
        if (M >> j) & 1:
            m.cnot(t, C[j])
    m.free(C)
    # t = 1  <=>  no reduction  <=>  result = 2B is even (M odd)
    m.x(B[0])
    m.cnot(B[0], t)
    m.x(B[0])
    m.free([t])
    m.free([z])


def mod_hlv(m, B, M):
    m.inverse(mod_dbl, B, M)


def modmul_acc(m, X, Y, Z, M, sign=1):
    """Z <- (Z + sign * X*Y) mod M.  X, Y preserved; X may alias Y (squaring).
    Z must be a distinct register.  Requires all values < M."""
    n = len(X)
    assert len(Y) == n and len(Z) == n
    R = m.alloc(n)
    for j in range(n):
        m.cnot(Y[j], R[j])          # R = Y
    for i in range(n):
        C = m.alloc(n)
        for j in range(n):
            m.ccx(X[i], R[j], C[j])
        if sign > 0:
            mod_add(m, C, Z, M)
        else:
            mod_sub(m, C, Z, M)
        for j in range(n):
            m.ccx(X[i], R[j], C[j])
        m.free(C)
        if i < n - 1:
            mod_dbl(m, R, M)
    for _ in range(n - 1):
        mod_hlv(m, R, M)
    for j in range(n):
        m.cnot(Y[j], R[j])
    m.free(R)


# =====================================================================
# modular inversion by Fermat's little theorem  (PREREGISTRATION clause 7)
# =====================================================================

def _fermat_chain(m, X, p, regs):
    """Left-to-right square-and-multiply for X^(p-2) mod p.
    Allocates one clean n-qubit register per chain step and keeps them all
    (appended to `regs`); returns the register holding the result."""
    n = len(X)
    e = p - 2
    bits = bin(e)[2:]
    cur = X
    for ch in bits[1:]:
        sq = m.alloc(n)
        regs.append(sq)
        modmul_acc(m, cur, cur, sq, p, 1)
        cur = sq
        if ch == "1":
            mu = m.alloc(n)
            regs.append(mu)
            modmul_acc(m, cur, X, mu, p, 1)
            cur = mu
    return cur


def mod_inv(m, X, T, p):
    """T <- X^(p-2) mod p (= X^-1 for X != 0).  X preserved, T starts at |0>,
    all scratch returned to |0> and released."""
    regs = []
    ops, res = m.capture(_fermat_chain, X, p, regs)
    m.replay(ops)                       # compute the chain
    for j in range(len(T)):
        m.cnot(res[j], T[j])            # copy the result out
    m.replay(ops, invert=True)          # uncompute the chain
    for r in reversed(regs):
        m.free(r)


# =====================================================================
# (a) modular exponentiation, RSA shape   (PREREGISTRATION clause 5)
# =====================================================================

def ctrl_modmul(m, c, Z, k, N):
    """Z <- k*Z mod N  if c = 1, else Z unchanged.  gcd(k,N) = 1, Z < N."""
    n = len(Z)
    W = m.alloc(n)
    kinv = pow(k, -1, N)
    for i in range(n):
        (q,) = m.alloc(1)
        m.ccx(c, Z[i], q)
        const = (k << i) % N
        A = m.alloc(n)
        for j in range(n):
            if (const >> j) & 1:
                m.cnot(q, A[j])
        mod_add(m, A, W, N)
        for j in range(n):
            if (const >> j) & 1:
                m.cnot(q, A[j])
        m.free(A)
        m.ccx(c, Z[i], q)
        m.free([q])
    for i in range(n):                  # controlled swap Z <-> W
        m.cnot(W[i], Z[i])
        m.ccx(c, Z[i], W[i])
        m.cnot(W[i], Z[i])
    for i in range(n):                  # uncompute W with k^-1
        (q,) = m.alloc(1)
        m.ccx(c, Z[i], q)
        const = (kinv << i) % N
        A = m.alloc(n)
        for j in range(n):
            if (const >> j) & 1:
                m.cnot(q, A[j])
        mod_sub(m, A, W, N)
        for j in range(n):
            if (const >> j) & 1:
                m.cnot(q, A[j])
        m.free(A)
        m.ccx(c, Z[i], q)
        m.free([q])
    m.free(W)


def modexp(m, E, Z, a, N):
    """Z <- a^E * Z mod N, for a 2n-bit exponent register E (unchanged) and an
    n-bit target Z prepared as 1.  2n controlled modular multiplications."""
    n = len(Z)
    assert len(E) == 2 * n
    for j in range(2 * n):
        k = pow(a, 1 << j, N)
        ctrl_modmul(m, E[j], Z, k, N)


# =====================================================================
# (b) elliptic-curve point addition, 256-bit prime-field shape
#     (PREREGISTRATION clause 6)
# =====================================================================

def point_add(m, X, Y, p, x2, y2):
    """(x1,y1) -> (x1,y1) + (x2,y2) in place, (x2,y2) a classical affine point
    of a short Weierstrass curve over F_p.  Valid for x1 != x2 and x3 != x2.
    All ancillas returned to |0>.

    Identities used (derived, see derive_identities.py):
        u  = x1 - x2,  v = y1 - y2,  lam = v/u
        x3 - x2 = lam^2 - u - 3*x2
        y3 + y2 = -lam*(x3 - x2)
    """
    n = len(X)
    mod_sub_const(m, x2 % p, X, p)          # X = u
    mod_sub_const(m, y2 % p, Y, p)          # Y = v
    # NOTE: every register that must stay live across a captured block is
    # allocated BEFORE the capture.  A captured block returns its scratch to
    # the free pool, so a later long-lived allocation would alias the qubits
    # the replayed block writes to.  (This was caught by simulation.)
    L = m.alloc(n)
    T = m.alloc(n)
    ops1, _ = m.capture(mod_inv, X, T, p)
    m.replay(ops1)                          # T = u^-1
    modmul_acc(m, Y, T, L, p, 1)            # L = lam
    modmul_acc(m, L, X, Y, p, -1)           # Y = v - lam*u = 0
    m.replay(ops1, invert=True)             # T = 0
    m.free(T)
    mod_neg(m, X, p)                        # X = -u
    modmul_acc(m, L, L, X, p, 1)            # X = lam^2 - u
    mod_sub_const(m, (3 * x2) % p, X, p)    # X = x3 - x2
    modmul_acc(m, L, X, Y, p, -1)           # Y = -lam*(x3-x2) = y3 + y2
    T2 = m.alloc(n)
    ops2, _ = m.capture(mod_inv, X, T2, p)
    m.replay(ops2)                          # T2 = (x3-x2)^-1
    modmul_acc(m, Y, T2, L, p, 1)           # L = lam + (y3+y2)/(x3-x2) = 0
    m.replay(ops2, invert=True)             # T2 = 0
    m.free(T2)
    m.free(L)
    mod_add_const(m, x2 % p, X, p)          # X = x3
    mod_sub_const(m, y2 % p, Y, p)          # Y = y3
