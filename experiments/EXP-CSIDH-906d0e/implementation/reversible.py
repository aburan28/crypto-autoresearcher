#!/usr/bin/env python3
"""Reversible NCT circuit substrate for EXP-CSIDH-906d0e.

A circuit is a straight-line sequence of NOT, CNOT and Toffoli gates over
classically simulated bits, applied directly to a bytearray state as the
builder runs. The gate sequence is data-independent (every conditional is
a controlled gate, never a skipped gate), so a builder produces the same
allocation width and gate counts for every input pair.

Frozen allocation discipline (experiments/EXP-CSIDH-906d0e/specification.yaml,
inputs.ancilla_definition): every temporary is a fresh zero-initialized bit;
no scratch bit is ever reused in time; garbage is never uncomputed and
counts toward the width. Input registers are never written. The width is
the number of allocated bits minus the 96 input and 48 output bits.
"""
from __future__ import annotations

WIDTH = 16
MASK = (1 << WIDTH) - 1


class Circuit:
    """Gate-level NCT circuit with a direct classical simulation."""

    def __init__(self) -> None:
        self.nbits = 0
        self._buf = bytearray(1 << 16)
        self.counts = {"X": 0, "CNOT": 0, "CCNOT": 0}
        self.input_bits: list[int] = []
        self.output_bits: list[int] = []

    # -- allocation ------------------------------------------------------
    def _alloc(self) -> int:
        bit = self.nbits
        self.nbits += 1
        if (bit >> 3) >= len(self._buf):
            self._buf.extend(bytes(len(self._buf)))
        return bit

    def reg(self, value: int = 0, n: int = WIDTH) -> list[int]:
        """Fresh zero-initialized register, optionally loaded with a value."""
        bits = [self._alloc() for _ in range(n)]
        if value:
            v = value & ((1 << n) - 1)
            for i, b in enumerate(bits):
                if (v >> i) & 1:
                    self.x(b)
        return bits

    def input_reg(self, value: int) -> list[int]:
        """Input register: initial value set directly, never written by gates."""
        bits = [self._alloc() for _ in range(WIDTH)]
        v = value & MASK
        for i, b in enumerate(bits):
            if (v >> i) & 1:
                self._buf[b >> 3] |= 1 << (b & 7)
        self.input_bits.extend(bits)
        return bits

    def output_reg(self) -> list[int]:
        bits = [self._alloc() for _ in range(WIDTH)]
        self.output_bits.extend(bits)
        return bits

    # -- primitive gates ---------------------------------------------------
    def _get(self, b: int) -> int:
        return (self._buf[b >> 3] >> (b & 7)) & 1

    def _flip(self, b: int) -> None:
        self._buf[b >> 3] ^= 1 << (b & 7)

    def x(self, t: int) -> None:
        self._flip(t)
        self.counts["X"] += 1

    def cnot(self, c: int, t: int) -> None:
        if self._get(c):
            self._flip(t)
        self.counts["CNOT"] += 1

    def tof(self, c1: int, c2: int, t: int) -> None:
        if self._get(c1) and self._get(c2):
            self._flip(t)
        self.counts["CCNOT"] += 1

    # -- register helpers ----------------------------------------------------
    def val(self, bits: list[int]) -> int:
        v = 0
        for i, b in enumerate(bits):
            v |= self._get(b) << i
        return v

    def signed(self, bits: list[int]) -> int:
        v = self.val(bits)
        return v - (1 << WIDTH) if v >> (WIDTH - 1) else v

    def copy(self, bits: list[int]) -> list[int]:
        out = [self._alloc() for _ in bits]
        for s, t in zip(bits, out):
            self.cnot(s, t)
        return out

    def width(self) -> int:
        return self.nbits - len(self.input_bits) - len(self.output_bits)

    def inputs_unchanged(self, initial: list[int]) -> bool:
        return all(self._get(b) == v for b, v in zip(self.input_bits, initial))

    def initial_input_snapshot(self) -> list[int]:
        return [self._get(b) for b in self.input_bits]

    # -- arithmetic; every output is a fresh register ---------------------------
    def add(self, a: list[int], b: list[int]) -> list[int]:
        out = [self._alloc() for _ in a]
        carry: int | None = None
        for i in range(len(a)):
            self.cnot(a[i], out[i])
            self.cnot(b[i], out[i])
            if carry is not None:
                self.cnot(carry, out[i])
                c = self._alloc()
                self.tof(a[i], carry, c)
                self.tof(b[i], carry, c)
            else:
                c = self._alloc()
            self.tof(a[i], b[i], c)
            carry = c
        return out

    def neg(self, a: list[int]) -> list[int]:
        one = self.reg(1)
        flipped = [self._alloc() for _ in a]
        for s, t in zip(a, flipped):
            self.x(t)
            self.cnot(s, t)
        return self.add(flipped, one)

    def sub(self, a: list[int], b: list[int]) -> list[int]:
        return self.add(a, self.neg(b))

    def mul(self, a: list[int], b: list[int]) -> list[int]:
        out = [self._alloc() for _ in a]
        for i in range(len(b)):
            t = [self._alloc() for _ in a]
            for j in range(i, len(a)):
                self.cnot(a[j - i], t[j])
            s = [self._alloc() for _ in a]
            for j in range(len(a)):
                self.tof(t[j], b[i], s[j])
            carry: int | None = None
            for j in range(len(a)):
                c = self._alloc()
                self.tof(s[j], out[j], c)
                if carry is not None:
                    self.tof(s[j], carry, c)
                    self.tof(out[j], carry, c)
                self.cnot(s[j], out[j])
                if carry is not None:
                    self.cnot(carry, out[j])
                carry = c
        return out

    def asr1(self, a: list[int]) -> list[int]:
        """Arithmetic shift right by one; exact halving of even values."""
        out = [self._alloc() for _ in a]
        for i in range(len(a) - 1):
            self.cnot(a[i + 1], out[i])
        self.cnot(a[-1], out[-1])
        return out

    def cmpu_lt(self, a: list[int], b: list[int]) -> int:
        """Unsigned a < b into a fresh bit (lt/eq ripple from the top)."""
        lt = self._alloc()   # a < b in the bits above the scan point
        eq = self._alloc()   # a == b in the bits above the scan point
        self.x(eq)
        for i in range(len(a) - 1, -1, -1):
            na = self._alloc()
            self.x(na)
            self.cnot(a[i], na)          # not a_i
            al = self._alloc()
            self.tof(na, b[i], al)       # a_i < b_i
            d = self._alloc()
            self.cnot(a[i], d)
            self.cnot(b[i], d)           # a_i xor b_i
            nd = self._alloc()
            self.x(nd)
            self.cnot(d, nd)            # a_i == b_i
            nxt_lt = self._alloc()
            self.cnot(lt, nxt_lt)
            self.tof(eq, al, nxt_lt)     # lt or (eq and a_i<b_i); disjoint
            nxt_eq = self._alloc()
            self.tof(eq, nd, nxt_eq)     # eq and a_i==b_i
            lt, eq = nxt_lt, nxt_eq
        return lt

    def cmps_lt(self, a: list[int], b: list[int]) -> int:
        """Signed a < b into a fresh bit."""
        d = self.sub(a, b)
        out = self._alloc()
        self.cnot(d[-1], out)
        return out

    def eq_reg(self, a: list[int], value: int) -> int:
        """Fresh bit: register equals the 16-bit pattern of value."""
        acc = self._alloc()
        self.x(acc)
        for i in range(len(a)):
            want = (value >> i) & 1
            term = self._alloc()
            if want:
                self.cnot(a[i], term)
            else:
                self.x(term)
                self.cnot(a[i], term)
            nxt = self._alloc()
            self.tof(acc, term, nxt)  # acc = acc AND term
            acc = nxt
        return acc

    def is_neg(self, a: list[int]) -> int:
        b = self._alloc()
        self.cnot(a[-1], b)
        return b

    def csel(self, cond: int, x: list[int], y: list[int]) -> list[int]:
        """Fresh register: x if cond else y."""
        out = [self._alloc() for _ in x]
        for i in range(len(x)):
            d = self._alloc()
            self.cnot(x[i], d)
            self.cnot(y[i], d)
            self.cnot(y[i], out[i])
            self.tof(cond, d, out[i])
        return out

    def abs(self, a: list[int]) -> list[int]:
        neg = self.is_neg(a)
        return self.csel(neg, self.neg(a), a)

    def csel_bit(self, cond: int, x: int, y: int) -> int:
        out = self._alloc()
        d = self._alloc()
        self.cnot(x, d)
        self.cnot(y, d)
        self.cnot(y, out)
        self.tof(cond, d, out)
        return out

    # -- division ---------------------------------------------------------
    def divmod_pos(self, n: list[int], d: list[int]) -> tuple[list[int], list[int]]:
        """Unsigned restoring division; 0 <= n, 0 < d < 2^16.

        Guarded: if d reads as zero the pair (q, r) = (0, n) is returned so
        fixed-length Euclid loops stay no-ops after convergence.
        """
        dzero = self.eq_reg(d, 0)
        zero = self.reg(0)
        q = self.reg(0)
        r = self.reg(0)
        for j in range(len(n) - 1, -1, -1):
            t = [self._alloc() for _ in n]
            for k in range(1, len(n)):
                self.cnot(r[k - 1], t[k])
            self.cnot(n[j], t[0])
            geq = self._alloc()
            self.x(geq)
            lt = self.cmpu_lt(t, d)
            self.cnot(lt, geq)
            diff = self.sub(t, d)
            picked = self.csel(geq, diff, t)
            r = self.csel(dzero, r, picked)
            self.cnot(geq, q[j])
        q = self.csel(dzero, zero, q)
        r = self.csel(dzero, n, r)
        return q, r

    def fdivmod(self, n: list[int], d: list[int]) -> tuple[list[int], list[int]]:
        """Floor division and remainder, d > 0, n signed."""
        neg = self.is_neg(n)
        nn = self.csel(neg, self.neg(n), n)
        q, r = self.divmod_pos(nn, d)
        zero = self.reg(0)
        one = self.reg(1)
        rpos = self._alloc()
        self.x(rpos)
        self.cnot(self.eq_reg(r, 0), rpos)
        bump = self.csel(rpos, one, zero)
        qn = self.sub(self.neg(q), bump)
        d_minus_r = self.sub(d, r)
        rneg = self.csel(rpos, d_minus_r, zero)
        q = self.csel(neg, qn, q)
        r = self.csel(neg, rneg, r)
        return q, r

    # -- fixed-length Euclid --------------------------------------------------
    def gcd(self, a: list[int], b: list[int]) -> list[int]:
        """gcd of unsigned magnitudes, 24 fixed Euclid steps, guarded."""
        u = self.copy(a)
        v = self.copy(b)
        for _ in range(24):
            vzero = self.eq_reg(v, 0)
            q, r = self.divmod_pos(u, v)
            u2 = self.csel(vzero, u, v)
            v2 = self.csel(vzero, v, r)
            u, v = u2, v2
        return u

    def ext_gcd(self, a: list[int], b: list[int]) -> tuple[list[int], list[int], list[int]]:
        """Division-based extended Euclid on unsigned magnitudes, 24 steps.

        Returns (g, s, t) with s*|a| + t*|b| = g maintained on the classical
        mirror; callers adjust coefficient signs for negative originals.
        """
        zero = self.reg(0)
        one = self.reg(1)
        u = self.copy(a)
        v = self.copy(b)
        s0, s1 = self.copy(one), self.copy(zero)
        t0, t1 = self.copy(zero), self.copy(one)
        for _ in range(24):
            vzero = self.eq_reg(v, 0)
            q, r = self.divmod_pos(u, v)
            qs = self.sub(s0, self.mul(q, s1))
            qt = self.sub(t0, self.mul(q, t1))
            u2 = self.csel(vzero, u, v)
            v2 = self.csel(vzero, v, r)
            s02 = self.csel(vzero, s0, s1)
            s12 = self.csel(vzero, s1, qs)
            t02 = self.csel(vzero, t0, t1)
            t12 = self.csel(vzero, t1, qt)
            u, v, s0, s1, t0, t1 = u2, v2, s02, s12, t02, t12
        return u, s0, t0
