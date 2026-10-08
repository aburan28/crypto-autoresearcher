#!/usr/bin/env python3
"""
Generator of AArch64 field arithmetic for Montgomery-friendly primes of the
form p = c * 2^t - 1.

It emits fp_add, fp_sub, fp_mul, fp_sqr, fp2_mul and fp2_sqr, mirroring
gen_fp_asm_broadwell.py and the hand-written AArch64 implementations it
replaces (src/gf/arm64/lvl{1,5}/fp_asm.S on the pre-bhe branches), except
that the GF(p^2) routines are single fused calls computing both output
components: fp2_mul with 3 Montgomery multiplications (Karatsuba) instead
of the 4 that separate c0/c1 entry points cost, fp2_sqr with the same 2 as
before but sharing one frame and one load of the input.

Assumptions (checked below, same as the Broadwell generator):
  * t >= 64*(N-1), i.e. all limbs of p below the top one are 0xFFFF...FF,
    and p+1 = c*2^t has a single non-zero (top) limb.  This is what makes
    the Montgomery reduction a single 64x64 multiply per iteration.
  * The prime has at least 4 spare bits in the top limb, so that modular
    corrections / carry propagations can be delayed (lazy reduction with
    values kept < 2p).

Usage:
    python gen_fp_asm_arm64.py --c 27 --t 500 -o fp_asm.S
    python gen_fp_asm_arm64.py --prime '17*2^664-1' -o fp_asm.S

Unlike the Broadwell generator there are no spill flags: AArch64 has no
pointer scarcity, so the strategy follows from the limb count alone.  The
multiplicand is register-resident everywhere.  Each of fp2_mul's three
Montgomery multiplications keeps one operand resident and streams the
other (scalar) from memory, so it fits the same 2N+3 registers as fp_mul;
12+ limbs would need a streamed multiplicand, which is not implemented.
"""

import argparse
import os
import sys

# x0/x2 stay pointers where live, x18 is platform-reserved, x29 is untouched.
# x30 (saved) and x1 (dead once the operands are loaded) close the pool.
POOL = (["x%d" % i for i in range(3, 18)]
        + ["x%d" % i for i in range(19, 29)] + ["x30", "x1"])
CALLEE_SAVED = tuple("x%d" % i for i in range(19, 29)) + ("x30",)

MAX_LIMBS = 11


# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------
class Params:
    def __init__(self, c, t):
        self.c = c
        self.t = t
        self.p = c * (1 << t) - 1
        self.bits = self.p.bit_length()
        self.N = (self.bits + 63) // 64
        self.W = 64 * self.N
        self.bytes = (self.bits + 7) // 8

        # Shift that isolates the spare (headroom) bits of the top limb;
        # drives the delayed modular corrections.
        self.shift = self.bits - 64 * (self.N - 1)
        self.spare = 64 - self.shift

        # p = 2^t - 1 : the modular corrections collapse to a fold-and-mask.
        self.mersenne = (c == 1)
        # Montgomery outputs are bounded by numerator/2^(64N) + p; when that
        # exceeds 2^bits the kernels need one final masked subtraction of p.
        # 8*2^(2*bits) covers fp2_sqr's (a0+a1)*(a0-a1+2p) worst case.
        self.needs_fold = ((8 << (2 * self.bits)) >> (64 * self.N)) + self.p >= (1 << self.bits)

        if self.N < 3:
            raise ValueError("primes below 3 limbs are not supported")
        if t < 64 * (self.N - 1):
            raise ValueError("p+1 = c*2^t must have a single non-zero limb "
                             "(need t >= 64*(N-1))")
        # 4 = threshold at which outputs stay inside [0, 2^bits); see test/.
        if self.spare < 4:
            raise ValueError("prime needs at least 4 spare bits in the top limb "
                             "(got %d): outputs would leave the [0,2^%d) domain "
                             "the add/sub corrections rely on"
                             % (self.spare, self.bits))
        if self.N > MAX_LIMBS:
            raise ValueError(
                "p is %d bits (%d limbs), above the %d-limb ceiling of the "
                "register-resident fp_mul (2N+3 registers). A field this "
                "large needs a streamed multiplicand, which is not "
                "implemented here." % (self.bits, self.N, MAX_LIMBS))

        # The single non-zero limb of p+1, and the top limbs of p and 2p.
        self.pp1_top = c << (t - 64 * (self.N - 1))
        self.p_top = self.pp1_top - 1
        self.p2_top = 2 * self.pp1_top - 1

        n = self.N
        # fp_mul / fp2_mul / fp2_sq_*: multiplicand A, accumulator Z, scalar
        # BI, temp T0.  The reduction borrows BI as its second temp (dead
        # there).  fp2_mul reuses the same 2N+3 shape: each of its three
        # Montgomery multiplications streams the scalar operand from memory.
        self.A = POOL[:n]
        self.Z = POOL[n:2 * n + 1]
        self.BI = POOL[2 * n + 1]
        self.T0 = POOL[2 * n + 2]

        # Fused-Karatsuba fp2_mul bound bookkeeping (exact integers).
        # montmul(x, y) < x*y/2^(64N) + p (Montgomery envelope): with domain
        # inputs (< 2^bits) that is E01; with raw Karatsuba sums s = a0+a1,
        # r = b0+b1 (< 2^(bits+1)) it is E2.  s*r < 4*2^(2*bits) stays well
        # inside the 8*2^(2*bits) numerator envelope the kernels are proven
        # for (see needs_fold above).
        R = 1 << (64 * n)
        E01 = ((1 << (2 * self.bits)) >> (64 * n)) + self.p + 1
        E2 = ((4 << (2 * self.bits)) >> (64 * n)) + self.p + 1
        if E01 > 2 * self.p:
            # impossible with spare >= 4 (E01 <= 2^(bits-4) + p + 1 < 2p)
            raise ValueError("fp2_mul: montmul excess reaches 2p; "
                             "2p - P would not stay positive")

        def _passes(bound):
            """Masked passes (subtract p when v >= 2^bits) to reach [0, 2^bits)."""
            k = 0
            while bound > (1 << self.bits):
                bound = max(1 << self.bits, bound - self.p)
                k += 1
            return k

        # e = P2 + (2p - P0); c0 = u - P1 <= u = P0 + 2p; c1 = w - P1 <= w =
        # e' + 2p with e' < 2^bits after the ke passes.
        self.ke = _passes(E2 + 2 * self.p)
        self.k0 = _passes(E01 + 2 * self.p)
        self.k1 = _passes((1 << self.bits) + 2 * self.p)
        for B in (E2 + 2 * self.p, E01 + 2 * self.p):
            if B >= R:
                # impossible with spare >= 4 (B < 2^(bits+2) <= 2^(64N))
                raise ValueError("fp2_mul: intermediate exceeds N limbs")
        assert max(self.ke, self.k0, self.k1) <= 4

    def mem(self, base, i):
        return _adr(base, i)


def hexq(v):
    return "0x%016X" % v


def saved_regs(used):
    return [r for r in CALLEE_SAVED if r in used]


def reg_range(regs):
    """Compact display: [x14,x15,x16,x17,x19] -> 'x14..x17,x19'."""
    nums = [int(r[1:]) for r in regs]
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j == i:
            parts.append("x%d" % nums[i])
        elif j == i + 1:
            parts.extend(["x%d" % nums[i], "x%d" % nums[j]])
        else:
            parts.append("x%d..x%d" % (nums[i], nums[j]))
        i = j + 1
    return ",".join(parts)


# --------------------------------------------------------------------------
# Instruction formatting
# --------------------------------------------------------------------------
def ins(mn, args, ind="    "):
    return "%s%-5s %s\n" % (ind, mn, args)


def tail(line, comment):
    """Append an aligned // comment to a formatted instruction line."""
    text = line.rstrip("\n")
    pad = max(37, len(text) + 1)
    return "%s// %s\n" % (text.ljust(pad), comment)


def mov_imm(reg, v, ind="    ", comment=""):
    """Materialise a 64-bit constant with the shortest movz/movn/movk run."""
    v &= (1 << 64) - 1
    ch = [(v >> (16 * i)) & 0xFFFF for i in range(4)]
    nz = [i for i in range(4) if ch[i]]
    nf = [i for i in range(4) if ch[i] != 0xFFFF]
    lsl = lambda i: "" if i == 0 else ", lsl #%d" % (16 * i)
    out = []
    if not nz:
        out.append(ins("mov", "%s, xzr" % reg, ind))
    elif v > (1 << 64) - 0x10001:
        out.append(ins("mov", "%s, #-%d" % (reg, (1 << 64) - v), ind))
    elif len(nf) < len(nz):
        # the immediate is complemented: spell the value out in the comment
        if comment:
            comment += " = %s" % hexq(v)
        i = nf[0]
        out.append(ins("movn", "%s, #0x%04x%s" % (reg, ~ch[i] & 0xFFFF, lsl(i)), ind))
        for i in nf[1:]:
            out.append(ins("movk", "%s, #0x%04x%s" % (reg, ch[i], lsl(i)), ind))
    else:
        i = nz[0]
        out.append(ins("movz", "%s, #0x%04x%s" % (reg, ch[i], lsl(i)), ind))
        for i in nz[1:]:
            out.append(ins("movk", "%s, #0x%04x%s" % (reg, ch[i], lsl(i)), ind))
    if comment:
        out[-1] = tail(out[-1], comment)
    return "".join(out)


def _adr(base, i):
    return "[%s]" % base if i == 0 else "[%s, #%d]" % (base, 8 * i)


def ld_vec(regs, base, index=0, ind="    "):
    """ldp/ldr the given registers from base + 8*index."""
    s, i = [], 0
    while i < len(regs):
        if i + 1 < len(regs):
            s.append(ins("ldp", "%s, %s, %s" % (regs[i], regs[i + 1],
                                                _adr(base, index + i)), ind))
            i += 2
        else:
            s.append(ins("ldr", "%s, %s" % (regs[i], _adr(base, index + i)), ind))
            i += 1
    return "".join(s)


def st_vec(regs, base, index=0, ind="    "):
    s, i = [], 0
    while i < len(regs):
        if i + 1 < len(regs):
            s.append(ins("stp", "%s, %s, %s" % (regs[i], regs[i + 1],
                                                _adr(base, index + i)), ind))
            i += 2
        else:
            s.append(ins("str", "%s, %s" % (regs[i], _adr(base, index + i)), ind))
            i += 1
    return "".join(s)


# --------------------------------------------------------------------------
# Prologue / epilogue
# --------------------------------------------------------------------------
def _save_pairs(saved):
    pairs = [(saved[k], saved[k + 1]) for k in range(0, len(saved) - 1, 2)]
    odd = saved[-1] if len(saved) % 2 else None
    return pairs, odd


def frame_open(saved, bufbytes=0, buffer_name="", ind="    "):
    """Pre-index stp frame, or sub-sp frame when a scratch buffer is needed."""
    pairs, odd = _save_pairs(saved)
    save_bytes = 16 * ((len(saved) + 1) // 2)
    s = []
    if bufbytes:
        buf = (bufbytes + 15) & ~15
        line = ins("sub", "sp, sp, #%d" % (buf + save_bytes), ind)
        if saved:
            line = tail(line, "%d for %s buffer + %d for callee saves"
                        % (buf, buffer_name, save_bytes))
        else:
            line = tail(line, "scratch for %s" % buffer_name)
        s.append(line)
        for i, (r0, r1) in enumerate(pairs):
            s.append(ins("stp", "%s, %s, [sp, #%d]" % (r0, r1, buf + 16 * i), ind))
        if odd:
            s.append(ins("str", "%s, [sp, #%d]" % (odd, buf + 16 * len(pairs)), ind))
    elif len(saved) == 1:
        s.append(ins("str", "%s, [sp, #-16]!" % saved[0], ind))
    elif saved:
        s.append(ins("stp", "%s, %s, [sp, #-%d]!"
                     % (pairs[0][0], pairs[0][1], save_bytes), ind))
        for i, (r0, r1) in enumerate(pairs[1:], 1):
            s.append(ins("stp", "%s, %s, [sp, #%d]" % (r0, r1, 16 * i), ind))
        if odd:
            s.append(ins("str", "%s, [sp, #%d]" % (odd, 16 * len(pairs)), ind))
    return "".join(s)


def frame_close(saved, bufbytes=0, ind="    "):
    pairs, odd = _save_pairs(saved)
    save_bytes = 16 * ((len(saved) + 1) // 2)
    s = []
    if bufbytes:
        buf = (bufbytes + 15) & ~15
        if odd:
            s.append(ins("ldr", "%s, [sp, #%d]" % (odd, buf + 16 * len(pairs)), ind))
        for i in range(len(pairs) - 1, -1, -1):
            s.append(ins("ldp", "%s, %s, [sp, #%d]"
                         % (pairs[i][0], pairs[i][1], buf + 16 * i), ind))
        s.append(ins("add", "sp, sp, #%d" % (buf + save_bytes), ind))
    elif len(saved) == 1:
        s.append(ins("ldr", "%s, [sp], #16" % saved[0], ind))
    elif saved:
        if odd:
            s.append(ins("ldr", "%s, [sp, #%d]" % (odd, 16 * len(pairs)), ind))
        for i in range(len(pairs) - 1, 0, -1):
            s.append(ins("ldp", "%s, %s, [sp, #%d]"
                         % (pairs[i][0], pairs[i][1], 16 * i), ind))
        s.append(ins("ldp", "%s, %s, [sp], #%d"
                     % (pairs[0][0], pairs[0][1], save_bytes), ind))
    return "".join(s)


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
def gen_header(P):
    strategy = (
        "// The multiplicand is register-resident throughout (Broadwell streams it\n"
        "// from memory).  fp2_mul computes both output components in one call with\n"
        "// 3 Montgomery multiplications (Karatsuba): P0 = a0 x b0, P1 = a1 x b1,\n"
        "// P2 = (a0+a1) x (b0+b1); c0 = P0 - P1, c1 = P2 - P0 - P1, with all\n"
        "// combinations kept positive by adding 2p and brought back into the\n"
        "// [0, 2^bits) domain by masked subtractions of p.")
    return f"""// Auto-generated by gen_fp_asm_arm64.py -- do not edit.
// p = {P.c} * 2^{P.t} - 1  ({P.bits} bits, {P.N} limbs, {P.spare} spare bits)
//
// AArch64 assembly for GF(p) / GF(p^2) arithmetic.
//
// Port of the Broadwell schedule (see gen_fp_asm_broadwell.py).  64x64->128
// products use MUL (low) + UMULH (high); AArch64 has a single carry flag, so
// each per-limb multiply-accumulate is two flag-resetting ADDS/ADCS chains
// (all low halves, then all high halves one limb up) with a single scratch
// temp, which an out-of-order core renames per product.  Montgomery
// reduction uses mu = -p^-1 mod 2^64 = 1 and the single non-zero limb of
// p+1 = c*2^t (PP1_TOP = {hexq(P.pp1_top)}, rematerialised by MOVZ), so
// each step is one 64x64 multiply into the top two accumulator limbs; limb
// 0 is dropped by operand rotation.  All constants are materialised inline:
// no .rodata, no p/p2 loads.  x18 (platform register) is never used.
//
{strategy}
//
// Calling convention (AAPCS64): x0 = out, x1 = a/in0, x2 = b/in1.

#include <sqisign_namespace.h>

#if defined(__linux__) && defined(__ELF__)
.section .note.GNU-stack,"",@progbits
#endif

#include <asm_preamble.h>

.text
.p2align 4
"""


# --------------------------------------------------------------------------
# fp_add / fp_sub
# --------------------------------------------------------------------------
def _addsub_regs(P):
    """a resident + 2 rolling temps for b + the p[N-1] constant."""
    return POOL[:P.N], POOL[P.N], POOL[P.N + 1], POOL[P.N + 2]


def _rolling_chain(P, a, t0, t1, base, index, first, mid, last, ind="    "):
    """a op= [base + 8*index ..], the second operand ldp'd pairwise."""
    s, n = [], P.N
    for i in range(0, n - 1, 2):
        s.append(ld_vec([t0, t1], base, index + i, ind))
        s.append(ins(first if i == 0 else mid, "%s, %s, %s" % (a[i], a[i], t0), ind))
        op = last if i + 1 == n - 1 else mid
        s.append(ins(op, "%s, %s, %s" % (a[i + 1], a[i + 1], t1), ind))
    if n % 2:
        s.append(ld_vec([t0], base, index + n - 1, ind))
        s.append(ins(last, "%s, %s, %s" % (a[n - 1], a[n - 1], t0), ind))
    return "".join(s)


def _sub_p_masked(P, a, m, mp, pt, ind="    "):
    """a -= p & mask: the all-ones mask m doubles as p's low limbs."""
    s = [ins("and", "%s, %s, %s" % (mp, pt, m), ind),
         ins("subs", "%s, %s, %s" % (a[0], a[0], m), ind)]
    for r in a[1:-1]:
        s.append(ins("sbcs", "%s, %s, %s" % (r, r, m), ind))
    s.append(ins("sbc", "%s, %s, %s" % (a[-1], a[-1], mp), ind))
    return "".join(s)


def _add_p_masked(P, a, m, mp, pt, ind="    "):
    s = [ins("and", "%s, %s, %s" % (mp, pt, m), ind),
         ins("adds", "%s, %s, %s" % (a[0], a[0], m), ind)]
    for r in a[1:-1]:
        s.append(ins("adcs", "%s, %s, %s" % (r, r, m), ind))
    s.append(ins("adc", "%s, %s, %s" % (a[-1], a[-1], mp), ind))
    return "".join(s)


def gen_fp_add(P):
    a, t0, t1, pt = _addsub_regs(P)
    s = ["\n.global fp_add\n.p2align 6\nfp_add:\n"]
    s.append(ld_vec(a, "x1"))
    s.append(_rolling_chain(P, a, t0, t1, "x2", 0, "adds", "adcs", "adc"))
    s.append(mov_imm(pt, P.p_top, comment="p[%d]" % (P.N - 1)))
    if P.mersenne:
        # p = 2^t - 1: fold the spare bits of the top limb into limb 0.
        s.append(ins("lsr", "%s, %s, #%d" % (t0, a[-1], P.shift)))
        s.append(ins("adds", "%s, %s, %s" % (a[0], a[0], t0)))
        for r in a[1:-1]:
            s.append(ins("adcs", "%s, %s, xzr" % (r, r)))
        s.append(ins("adc", "%s, %s, xzr" % (a[-1], a[-1])))
        s.append(ins("and", "%s, %s, %s" % (a[-1], a[-1], pt)))
    else:
        # Inputs are < 2p, so at most two conditional subtractions are needed.
        for p in (1, 2):
            s.append("    // pass %d\n" % p)
            s.append(ins("lsr", "%s, %s, #%d" % (t0, a[-1], P.shift)))
            s.append(ins("neg", "%s, %s" % (t0, t0)))
            s.append(_sub_p_masked(P, a, t0, t1, pt))
    s.append(st_vec(a, "x0"))
    s.append("    ret\n")
    return "".join(s)


def gen_fp_sub(P):
    a, t0, t1, pt = _addsub_regs(P)
    s = ["\n.global fp_sub\n.p2align 6\nfp_sub:\n"]
    s.append(ld_vec(a, "x1"))
    s.append(_rolling_chain(P, a, t0, t1, "x2", 0, "subs", "sbcs", "sbcs"))
    s.append(tail(ins("sbc", "%s, xzr, xzr" % t0), "mask = -borrow"))
    s.append(mov_imm(pt, P.p_top, comment="p[%d]" % (P.N - 1)))
    if P.mersenne:
        # p = 2^t - 1: the mask adds 2^(64N)-1; then reduce the top limb.
        s.append(ins("adds", "%s, %s, %s" % (a[0], a[0], t0)))
        for r in a[1:-1]:
            s.append(ins("adcs", "%s, %s, %s" % (r, r, t0)))
        s.append(ins("adc", "%s, %s, %s" % (a[-1], a[-1], t0)))
        s.append(ins("and", "%s, %s, %s" % (a[-1], a[-1], pt)))
    else:
        # First correction: mask = borrow.  Second: mask = sign of the top limb.
        s.append(_add_p_masked(P, a, t0, t1, pt))
        s.append("    // pass 2 (sign mask)\n")
        s.append(ins("asr", "%s, %s, #%d" % (t0, a[-1], P.shift)))
        s.append(_add_p_masked(P, a, t0, t1, pt))
    s.append(st_vec(a, "x0"))
    s.append("    ret\n")
    return "".join(s)


# --------------------------------------------------------------------------
# Macros
# --------------------------------------------------------------------------
def _arglist(*groups):
    return ", ".join(",".join(g) for g in groups)


def gen_macros(P):
    N, W = P.N, P.W
    Z = ["Z%d" % i for i in range(N + 1)]
    A = ["A%d" % i for i in range(N)]
    bz = ["\\" + z for z in Z]
    ba = ["\\" + a for a in A]

    out = [f"""
///////////////////////////////////////////////////////////////// MACROS
// z = a x bi   (initial product, no input accumulator)
// Inputs: a in registers [{A[0]}:{A[N-1]}],
//         bi in register BI
// Output: [{Z[0]}:{Z[N]}]
// Temps:  reg T0
// Notes:  the {N} low halves land directly in [{Z[0]}:{Z[N-1]}], then the
//         high halves are summed one limb up in a single ADDS/ADCS
//         chain.  One temp suffices: MUL/UMULH leave the flags
//         untouched, and the renamer gives each product a fresh
//         physical T0, so they still issue in parallel.
/////////////////////////////////////////////////////////////////
.macro MUL64x{W} {_arglist(Z, A, ["BI"], ["T0"])}
"""]
    for i in range(N):
        out.append(ins("mul", "%s, %s, \\BI" % (bz[i], ba[i])))
    for i in range(N - 1):
        out.append(ins("umulh", "\\T0, %s, \\BI" % ba[i]))
        out.append(ins("adds" if i == 0 else "adcs",
                       "%s, %s, \\T0" % (bz[i + 1], bz[i + 1])))
    out.append(ins("umulh", "%s, %s, \\BI" % (bz[N], ba[N - 1])))
    out.append(ins("adc", "%s, %s, xzr" % (bz[N], bz[N])))
    out.append(f""".endm

/////////////////////////////////////////////////////////////////
// z = a x bi + z
// Inputs: a in registers [{A[0]}:{A[N-1]}],
//         bi in register BI,
//         accumulator z in [{Z[0]}:{Z[N]}]
// Output: [{Z[0]}:{Z[N]}]
// Temps:  reg T0
// Notes:  same single-temp two-chain schedule as MUL64x{W}.
/////////////////////////////////////////////////////////////////
.macro MULADD64x{W} {_arglist(Z, A, ["BI"], ["T0"])}
""")
    for i in range(N):
        out.append(ins("mul", "\\T0, %s, \\BI" % ba[i]))
        out.append(ins("adds" if i == 0 else "adcs",
                       "%s, %s, \\T0" % (bz[i], bz[i])))
    out.append(ins("adc", "%s, %s, xzr" % (bz[N], bz[N])))
    for i in range(N):
        out.append(ins("umulh", "\\T0, %s, \\BI" % ba[i]))
        out.append(ins("adds" if i == 0 else ("adc" if i == N - 1 else "adcs"),
                       "%s, %s, \\T0" % (bz[i + 1], bz[i + 1])))
    out.append(""".endm

// Montgomery word-reduction step: m = Z0; add m x PP1_TOP into the top two
// limbs (mu = 1).  PP1_TOP is rematerialised in T0; callers pass the scalar
// register as T1 (dead during the reduction, reloaded for the next column).
.macro MULADD64x64 %s, T0,T1
""" % _arglist(Z))
    out.append(mov_imm("\\T0", P.pp1_top))
    out.append(ins("mul", "\\T1, %s, \\T0" % bz[0]))
    out.append(ins("umulh", "\\T0, %s, \\T0" % bz[0]))
    out.append(ins("adds", "%s, %s, \\T1" % (bz[N - 1], bz[N - 1])))
    out.append(ins("adc", "%s, %s, \\T0" % (bz[N], bz[N])))
    out.append(".endm\n")
    return "".join(out)


# --------------------------------------------------------------------------
# Montgomery building blocks (function bodies, real registers)
# --------------------------------------------------------------------------
def _window(names, order):
    """main's '[x10:x17, x9]' accumulator-window display."""
    idx = {r: i for i, r in enumerate(order)}
    segs, i = [], 0
    while i < len(names):
        j = i
        while j + 1 < len(names) and idx[names[j + 1]] == idx[names[j]] + 1:
            j += 1
        segs.append(names[i] if i == j else "%s:%s" % (names[i], names[j]))
        i = j + 1
    return "[%s]" % ", ".join(segs)


def acc_window(state, order):
    return _window(state, order)


def mul_call(P, st, A, bi, t0, first, ind="    "):
    name = ("MUL64x%d" if first else "MULADD64x%d") % P.W
    return "%s%s  %s\n" % (ind, name, _arglist(st, A, [bi], [t0]))


def _domain_fold(P, st, t0, t1, ind="    "):
    """One masked subtraction of p brings the result into [0, 2^bits)."""
    s = [ins("lsr", "%s, %s, #%d" % (t0, st[P.N - 1], P.shift), ind),
         ins("neg", "%s, %s" % (t0, t0), ind),
         mov_imm(t1, P.p_top, ind, comment="p[%d]" % (P.N - 1)),
         ins("and", "%s, %s, %s" % (t1, t1, t0), ind),
         ins("subs", "%s, %s, %s" % (st[0], st[0], t0), ind)]
    for r in st[1:P.N - 1]:
        s.append(ins("sbcs", "%s, %s, %s" % (r, r, t0), ind))
    s.append(ins("sbc", "%s, %s, %s" % (st[P.N - 1], st[P.N - 1], t1), ind))
    return "".join(s)


def finish(P, st, t0, t1, index=0):
    s = []
    if P.needs_fold:
        s.append(_domain_fold(P, st, t0, t1))
    s.append(st_vec(st[:P.N], "x0", index))
    return "".join(s)


def gen_fpmul_macro(P):
    N, W = P.N, P.W
    Z = ["Z%d" % i for i in range(N + 1)]
    A = ["A%d" % i for i in range(N)]
    st = list(Z)
    out = [f"""
///////////////////////////////////////////////////////////////// MACRO
// z = a x b (mod p)
// Inputs: scalar source pointer M0 (b; b[0] is already folded into z by
//         the caller's initial product), a in registers [{A[0]}:{A[N-1]}],
//         accumulator z in [{Z[0]}:{Z[N]}] pre-loaded with a x b[0].
// Output: [{Z[0]}:{Z[N]}] (rotated by {N} positions)
// Temps:  BI (scalar; doubles as the reduction's 2nd temp), reg T0
/////////////////////////////////////////////////////////////////
.macro FPMUL{W}x{W} M0, {_arglist(A, Z, ["BI"], ["T0"])}
"""]

    def red(state):
        s = "    // %s <- z = (z0 x p_plus_1 + z)/2^64\n" % _window(state[1:], Z)
        s += "    MULADD64x64 %s, \\T0, \\BI\n" % _arglist(["\\" + z for z in state])
        return s, state[1:] + state[:1]

    code, st = red(st)
    out.append(code)
    for i in range(1, N):
        out.append("\n    // %s <- z = a x b%d + z\n" % (_window(st, Z), i))
        out.append(ins("mov", "\\%s, xzr" % st[N]))
        out.append(ins("ldr", "\\BI, [\\M0, #%d]" % (8 * i)))
        out.append("    MULADD64x%d  %s\n"
                   % (W, _arglist(["\\" + z for z in st], ["\\" + a for a in A],
                                  ["\\BI"], ["\\T0"])))
        code, st = red(st)
        out.append(code)
    out.append(".endm\n")
    return "".join(out)


def fpmul_call(P, M0, A, st, bi, t0, ind="    "):
    return "%sFPMUL%dx%d  %s, %s\n" % (ind, P.W, P.W, M0,
                                       _arglist(A, st, [bi], [t0]))


# --------------------------------------------------------------------------
# fp_mul / fp_sqr
# --------------------------------------------------------------------------
def gen_fp_mul(P):
    N = P.N
    A, st, bi, t0 = P.A, list(P.Z), P.BI, P.T0
    saved = saved_regs(A + st + [bi, t0])
    s = [f"""
//***********************************************************************
//  Field multiplication in GF(p)
//  Operation: c = a x b mod p
//  Inputs: a stored in [x1], b stored in [x2]
//  Output: c stored in [x0]
//  Register allocation: a (resident) = {reg_range(A)};
//                       acc z0..z{N} = {reg_range(st)},
//                       scalar bi = {bi}, MULADD temp {t0};
//                       the reduction borrows bi (dead there).
//***********************************************************************
.global fp_mul
.p2align 6
fp_mul:
"""]
    s.append(frame_open(saved))
    s.append(ld_vec(A, "x1"))
    s.append("\n    // %s <- z = a x b0\n" % _window(st, P.Z))
    s.append(ins("ldr", "%s, [x2]" % bi))
    s.append(mul_call(P, st, A, bi, t0, first=True))
    s.append(fpmul_call(P, "x2", A, st, bi, t0))
    st = st[N:] + st[:N]
    s.append("\n")
    s.append(finish(P, st, t0, bi))
    s.append(frame_close(saved))
    s.append("    ret\n")
    return "".join(s)


def gen_fp_sqr(P):
    return """
.global fp_sqr
.p2align 6
fp_sqr:
    mov   x2, x1
    b     fp_mul
"""


# --------------------------------------------------------------------------
# fp2_mul (fused, Karatsuba)
# --------------------------------------------------------------------------
def _add_2p(P, dst, src, t, ind="    "):
    """dst = src + 2p; the 2p limbs {-2, -1, ..., p2_top} roll through t
    (MOVs between the flag ops leave the carry untouched)."""
    s = [mov_imm(t, (1 << 64) - 2, ind),
         ins("adds", "%s, %s, %s" % (dst[0], src[0], t), ind),
         mov_imm(t, (1 << 64) - 1, ind)]
    for d, a in zip(dst[1:-1], src[1:-1]):
        s.append(ins("adcs", "%s, %s, %s" % (d, a, t), ind))
    s.append(mov_imm(t, P.p2_top, ind, comment="2p[%d]" % (P.N - 1)))
    s.append(ins("adc", "%s, %s, %s" % (dst[-1], src[-1], t), ind))
    return "".join(s)


def _rsb_2p(P, a, t, ind="    "):
    """a = 2p - a, in place."""
    s = [mov_imm(t, (1 << 64) - 2, ind),
         ins("subs", "%s, %s, %s" % (a[0], t, a[0]), ind),
         mov_imm(t, (1 << 64) - 1, ind)]
    for r in a[1:-1]:
        s.append(ins("sbcs", "%s, %s, %s" % (r, t, r), ind))
    s.append(mov_imm(t, P.p2_top, ind, comment="2p[%d]" % (P.N - 1)))
    s.append(ins("sbc", "%s, %s, %s" % (a[-1], t, a[-1]), ind))
    return "".join(s)


def _sub_mem_reg(P, dst, z, base, index, t0, t1, ind="    "):
    """dst = [base + 8*index ..] - z (memory minus registers; dst may be z)."""
    s, n = [], P.N
    for i in range(0, n - 1, 2):
        s.append(ld_vec([t0, t1], base, index + i, ind))
        s.append(ins("subs" if i == 0 else "sbcs",
                     "%s, %s, %s" % (dst[i], t0, z[i]), ind))
        op = "sbc" if i + 1 == n - 1 else "sbcs"
        s.append(ins(op, "%s, %s, %s" % (dst[i + 1], t1, z[i + 1]), ind))
    if n % 2:
        s.append(ld_vec([t0], base, index + n - 1, ind))
        s.append(ins("sbc", "%s, %s, %s" % (dst[n - 1], t0, z[n - 1]), ind))
    return "".join(s)


def _mask_passes(P, a, k, m, mp, pt, what, ind="    "):
    """k masked passes: a -= p whenever a >= 2^bits.  Unlike the add/sub
    corrections the top field can exceed 1 here, so the mask is
    -(field != 0) (neg + asr) rather than a plain neg.  pt holds p's top
    limb throughout."""
    s = []
    for i in range(k):
        s.append("%s// %s pass %d/%d\n" % (ind, what, i + 1, k))
        s.append(ins("lsr", "%s, %s, #%d" % (m, a[-1], P.shift), ind))
        s.append(ins("neg", "%s, %s" % (m, m), ind))
        s.append(ins("asr", "%s, %s, #63" % (m, m), ind))
        s.append(_sub_p_masked(P, a, m, mp, pt, ind))
    return "".join(s)


def gen_fp2_mul(P):
    """One call computes both components of c = a x b in GF(p^2) with three
    Montgomery multiplications (Karatsuba):
        P0 = mont(a0, b0), P1 = mont(a1, b1), P2 = mont(a0+a1, b0+b1)
        c0 = P0 - P1, c1 = P2 - P0 - P1
    The subtractions are kept positive by adding 2p and folded back into
    [0, 2^bits) by masked subtractions of p; the exact bounds live in
    Params (ke/k0/k1)."""
    N = P.N
    A, st, bi, t0 = P.A, list(P.Z), P.BI, P.T0
    saved = saved_regs(A + st + [bi, t0])
    s = [f"""
//***********************************************************************
//  Multiplication in GF(p^2), both components (Karatsuba, 3 montmuls)
//  Operation: c0 = a0 x b0 - a1 x b1 ; c1 = a0 x b1 + a1 x b0
//    as P0 = a0 x b0, P1 = a1 x b1, P2 = (a0+a1) x (b0+b1)  (all raw,
//    i.e. without the final masked subtraction of p), then
//    c0 = (P0 + 2p) - P1 and c1 = (fold(P2 + 2p - P0) + 2p) - P1,
//    each folded into [0, 2^{P.bits}) by masked subtractions of p
//    ({P.ke}/{P.k0}/{P.k1} passes for e/c0/c1).  The additive Karatsuba sums
//    s = a0+a1, r = b0+b1 are < 2^{P.bits + 1}, so s x r stays inside the
//    8 x 2^{2 * P.bits} numerator envelope the montmul kernels allow.
//  Inputs: a = [a1, a0] stored in [x1]
//          b = [b1, b0] stored in [x2]
//  Output: c = [c1, c0] stored in [x0]  (written only at the end: c may
//          alias a or b)
//  Register allocation: multiplicand (r/b0/b1 in turn) = {reg_range(A)};
//                       acc z0..z{N} = {reg_range(st)},
//                       scalar bi = {bi}, MULADD temp {t0};
//                       scalars (s/a0/a1) streamed from [sp]/[x1].
//  Stack: [sp+0 .. {8 * N}) holds s, then P2, then w = fold(P2+2p-P0) + 2p;
//         [sp+{8 * N} .. {16 * N}) holds u = P0 + 2p.
//***********************************************************************
.global fp2_mul
.p2align 6
fp2_mul:
"""]
    s.append(frame_open(saved, 16 * N, "s/P2/w + u"))

    s.append("\n    // s = a0 + a1 (raw, < 2^%d) -> [sp]\n" % (P.bits + 1))
    s.append(ld_vec(st[:N], "x1"))
    s.append(_rolling_chain(P, st[:N], bi, t0, "x1", N, "adds", "adcs", "adc"))
    s.append(st_vec(st[:N], "sp"))

    s.append("    // r = b0 + b1 (raw) -> %s, resident multiplicand of P2\n"
             % reg_range(A))
    s.append(ld_vec(A, "x2"))
    s.append(_rolling_chain(P, A, bi, t0, "x2", N, "adds", "adcs", "adc"))

    s.append("\n    // %s <- z = r x s0\n" % _window(st, P.Z))
    s.append(ins("ldr", "%s, [sp]" % bi))
    s.append(mul_call(P, st, A, bi, t0, first=True))
    s.append(fpmul_call(P, "sp", A, st, bi, t0))
    st = st[N:] + st[:N]
    s.append("    // P2 (raw) -> [sp], overwriting s (fully consumed)\n")
    s.append(st_vec(st[:N], "sp"))

    s.append("\n    // %s <- z = b0 x a0_0\n" % _window(st, P.Z))
    s.append(ld_vec(A, "x2"))
    s.append(ins("ldr", "%s, [x1]" % bi))
    s.append(mul_call(P, st, A, bi, t0, first=True))
    s.append(fpmul_call(P, "x1", A, st, bi, t0))
    st = st[N:] + st[:N]

    s.append("\n    // u = P0 + 2p -> [sp+%d]  (b0 is dead, reuse %s)\n"
             % (8 * N, reg_range(A)))
    s.append(_add_2p(P, A, st[:N], t0))
    s.append(st_vec(A, "sp", N))

    s.append("    // e = P2 + (2p - P0), then fold e into [0, 2^%d)\n" % P.bits)
    s.append(_rsb_2p(P, st[:N], t0))
    s.append(_rolling_chain(P, st[:N], bi, t0, "sp", 0, "adds", "adcs", "adc"))
    s.append(mov_imm(A[0], P.p_top, comment="p[%d]" % (N - 1)))
    s.append(_mask_passes(P, st[:N], P.ke, bi, t0, A[0], "e"))
    s.append("    // w = e + 2p -> [sp], overwriting P2 (fully consumed)\n")
    s.append(_add_2p(P, st[:N], st[:N], t0))
    s.append(st_vec(st[:N], "sp"))

    s.append("\n    // %s <- z = b1 x a1_0\n" % _window(st, P.Z))
    s.append(ld_vec(A, "x2", N))
    s.append(tail(ins("add", "x1, x1, #%d" % (8 * N)), "a1; x1 is dead after P1"))
    s.append(ins("ldr", "%s, [x1]" % bi))
    s.append(mul_call(P, st, A, bi, t0, first=True))
    s.append(fpmul_call(P, "x1", A, st, bi, t0))
    st = st[N:] + st[:N]

    s.append("\n    // c0 = u - P1 -> %s ; c1 = w - P1 -> %s (in place)\n"
             % (reg_range(A), reg_range(st[:N])))
    s.append(_sub_mem_reg(P, A, st[:N], "sp", N, bi, t0))
    s.append(_sub_mem_reg(P, st[:N], st[:N], "sp", 0, bi, t0))
    s.append(mov_imm(st[N], P.p_top, comment="p[%d]" % (N - 1)))
    s.append(_mask_passes(P, A, P.k0, bi, t0, st[N], "c0"))
    s.append(_mask_passes(P, st[:N], P.k1, bi, t0, st[N], "c1"))

    s.append("\n")
    s.append(st_vec(A, "x0"))
    s.append(st_vec(st[:N], "x0", N))
    s.append(frame_close(saved, 16 * N))
    s.append("    ret\n")
    return "".join(s)


# --------------------------------------------------------------------------
# fp2_sqr (fused)
# --------------------------------------------------------------------------
def gen_fp2_sqr(P):
    """One call computes both components of c = a^2 in GF(p^2):
        c0 = mont(a0+a1, a0-a1+2p), c1 = mont(a1, 2*a0)
    Same two Montgomery multiplications as the previous fp2_sq_c0/c1 pair,
    but sharing one frame and one load of a.  c0 is stored before a1 is
    reloaded for c1, which is safe under exact aliasing (c == a): the c0
    store only touches a0's slot."""
    N = P.N
    A, st, bi, t0 = P.A, list(P.Z), P.BI, P.T0
    saved = saved_regs(A + st + [bi, t0])
    s = [f"""
//***********************************************************************
//  Squaring in GF(p^2), both components
//  Operation: c0 = (a0+a1) x (a0-a1) ; c1 = 2 a0 x a1
//  Inputs: a = [a1, a0] stored in [x1]
//  Output: c = [c1, c0] stored in [x0]  (c may alias a)
//  Register allocation: multiplicand (d = a0-a1+2p, then a1) = {reg_range(A)};
//                       acc z0..z{N} = {reg_range(st)},
//                       scalar bi = {bi}, MULADD temp {t0};
//                       scalars streamed from [sp].
//  Stack: [sp+0 .. {8 * N}) holds s = a0+a1 (raw);
//         [sp+{8 * N} .. {16 * N}) holds t = 2*a0 (raw; self-add, EXTR is slow).
//***********************************************************************
.global fp2_sqr
.p2align 6
fp2_sqr:
"""]
    s.append(frame_open(saved, 16 * N, "s + t"))
    s.append("\n    // t = 2*a0 (raw) -> [sp+%d] ; a0 stays in %s\n"
             % (8 * N, reg_range(A)))
    s.append(ld_vec(A, "x1"))
    s.append(ins("adds", "%s, %s, %s" % (st[0], A[0], A[0])))
    for z, a in zip(st[1:N - 1], A[1:-1]):
        s.append(ins("adcs", "%s, %s, %s" % (z, a, a)))
    s.append(ins("adc", "%s, %s, %s" % (st[N - 1], A[-1], A[-1])))
    s.append(st_vec(st[:N], "sp", N))

    s.append("    // s = a0 + a1 (raw) -> [sp]\n")
    s.append(ld_vec(st[:N], "x1", N))
    s.append(ins("adds", "%s, %s, %s" % (st[0], st[0], A[0])))
    for z, a in zip(st[1:N - 1], A[1:-1]):
        s.append(ins("adcs", "%s, %s, %s" % (z, a, z)))
    s.append(ins("adc", "%s, %s, %s" % (st[N - 1], st[N - 1], A[-1])))
    s.append(st_vec(st[:N], "sp"))

    s.append("    // d = a0 - a1 + 2p (raw) -> %s ; p2 = 2p = {-2,-1,...,%s}\n"
             % (reg_range(A), hexq(P.p2_top)))
    s.append(_rolling_chain(P, A, st[0], st[1], "x1", N, "subs", "sbcs", "sbcs"))
    s.append(mov_imm(st[0], (1 << 64) - 2))
    s.append(ins("adds", "%s, %s, %s" % (A[0], A[0], st[0])))
    s.append(mov_imm(st[0], (1 << 64) - 1))
    for r in A[1:-1]:
        s.append(ins("adcs", "%s, %s, %s" % (r, r, st[0])))
    s.append(mov_imm(st[0], P.p2_top, comment="2p[%d]" % (N - 1)))
    s.append(ins("adc", "%s, %s, %s" % (A[-1], A[-1], st[0])))

    s.append("\n    // %s <- z = d x s0\n" % _window(st, P.Z))
    s.append(ins("ldr", "%s, [sp]" % bi))
    s.append(mul_call(P, st, A, bi, t0, first=True))
    s.append(fpmul_call(P, "sp", A, st, bi, t0))
    st = st[N:] + st[:N]
    s.append("\n    // c0 -> [x0] (a0's slot; a1 is still intact if c == a)\n")
    s.append(finish(P, st, t0, bi))

    s.append("\n    // %s <- z = a1 x t0\n" % _window(st, P.Z))
    s.append(ld_vec(A, "x1", N))
    s.append(tail(ins("add", "x1, sp, #%d" % (8 * N)),
                  "x1 is dead after the a1 load: reuse it as the t pointer"))
    s.append(ins("ldr", "%s, [x1]" % bi))
    s.append(mul_call(P, st, A, bi, t0, first=True))
    s.append(fpmul_call(P, "x1", A, st, bi, t0))
    st = st[N:] + st[:N]
    s.append("\n")
    s.append(finish(P, st, t0, bi, N))
    s.append(frame_close(saved, 16 * N))
    s.append("    ret\n")
    return "".join(s)


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def generate(c, t):
    P = Params(c, t)
    parts = [
        gen_header(P),
        gen_fp_add(P),
        gen_fp_sub(P),
        gen_macros(P),
        gen_fpmul_macro(P),
        gen_fp2_mul(P),
        gen_fp2_sqr(P),
        gen_fp_mul(P),
        gen_fp_sqr(P),
    ]
    return P, "".join(parts)


# The committed reference outputs under scripts/arm64/, mirroring the
# Broadwell generator's set: 4-11 limbs, Mersenne, fold, both fp2 tiers.
COMMITTED = [(5, 248), (3, 306), (3, 458), (27, 500), (1, 607),
             (17, 664), (19, 665)]


def self_test():
    """Regression check: regeneration, parse_prime, and the input guard."""
    here = os.path.dirname(os.path.abspath(__file__))
    fails = []

    for c, t in COMMITTED:
        ref = os.path.join(here, "..", "arm64", "p%d.%d" % (t, c), "fp_asm.S")
        if not os.path.exists(ref):
            print("  SKIP  p%d.%d (no committed reference)" % (t, c)); continue
        _, got = generate(c, t)
        want = open(ref, newline="").read()
        ok = got == want
        print("  %-6s regenerate p%d.%d/fp_asm.S" % ("ok" if ok else "FAIL", t, c))
        if not ok:
            fails.append("regeneration p%d.%d" % (t, c))

    for spec, want in [("5*2^248-1", (5, 248)), ("3*2^631-1", (3, 631)),
                       ("3*2^311-1", (3, 311)), ("11*2^61-1", (11, 61)),
                       ("2**607-1", (1, 607)), ("27*2^500-1", (27, 500))]:
        got = parse_prime(spec)
        ok = got == want
        print("  %-6s parse_prime(%s) -> %s" % ("ok" if ok else "FAIL", spec, got))
        if not ok:
            fails.append("parse_prime %s" % spec)

    for c, t, accept in [(5, 248, True), (27, 500, True), (3, 306, True),
                         (1, 607, True), (17, 664, True), (3, 250, True),
                         (3, 251, False), (3, 252, False), (65, 376, False),
                         (3, 762, False)]:
        try:
            Params(c, t); got = True
        except ValueError:
            got = False
        ok = got == accept
        print("  %-6s guard c=%d t=%d -> %s" % ("ok" if ok else "FAIL", c, t,
                                                "accept" if got else "reject"))
        if not ok:
            fails.append("guard c=%d t=%d" % (c, t))

    print("\nself-test: %s" % ("PASS" if not fails else "FAIL (%s)" % ", ".join(fails)))
    print("semantic tests (native arm64): see scripts/arm64/test/run.sh")
    return 1 if fails else 0


def parse_prime(text):
    """Accept 'c*2^t-1', or a raw (hex/dec) prime, and return (c, t)."""
    text = text.replace(" ", "").replace("**", "^")
    if "^" in text:
        if text.startswith("2^"):
            left, rest = "1", text[2:]   # Mersenne: 2^t-1
        else:
            left, rest = text.split("*2^")
        if rest.endswith("-1"):
            rest = rest[:-2]          # strip the SUFFIX, not the characters
        c, t = int(left, 0), int(rest)
        if t <= 0 or c <= 0:
            raise ValueError("bad prime spec %r" % text)
        return c, t
    p = int(text, 0)
    n = p + 1
    t = (n & -n).bit_length() - 1
    c = n >> t
    if c * (1 << t) - 1 != p:
        raise ValueError("p is not of the form c*2^t-1")
    return c, t


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--c", type=int, help="cofactor c in p = c*2^t - 1")
    ap.add_argument("--t", type=int, help="exponent t in p = c*2^t - 1")
    ap.add_argument("--prime", help="prime as 'c*2^t-1' or as a decimal/hex value")
    ap.add_argument("-o", "--output", default="fp_asm.S")
    ap.add_argument("--self-test", action="store_true",
                    help="run the regression checks and exit")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    if args.prime:
        c, t = parse_prime(args.prime)
    elif args.c is not None and args.t is not None:
        c, t = args.c, args.t
    else:
        ap.error("provide --prime or both --c and --t")

    P, text = generate(c, t)
    with open(args.output, "w", newline="\n") as f:
        f.write(text)
    print("Wrote %s: p = %d*2^%d-1, %d bits, %d limbs, %d spare bits"
          % (args.output, c, t, P.bits, P.N, P.spare))


if __name__ == "__main__":
    main()
