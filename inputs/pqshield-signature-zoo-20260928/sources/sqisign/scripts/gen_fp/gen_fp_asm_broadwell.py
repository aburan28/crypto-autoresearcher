#!/usr/bin/env python3
"""
Generator of x64 (Intel Broadwell, MULX/ADCX/ADOX) field arithmetic for
Montgomery-friendly primes of the form p = c * 2^t - 1.

It emits fp_add, fp_sub, fp_mul, fp_sqr, fp2_mul_c0, fp2_mul_c1,
fp2_sq_c0 and fp2_sq_c1, mirroring the hand-written implementations in
src/gf/broadwell/lvl{1,3,5}/fp_asm.S.

Assumptions (checked below):
  * t >= 64*(N-1), i.e. all limbs of p below the top one are 0xFFFF...FF,
    and p+1 = c*2^t has a single non-zero (top) limb.  This is what makes
    the Montgomery reduction a single 64x64 multiply per iteration.
  * The prime has at least 4 spare bits in the top limb, so that modular
    corrections / carry propagations can be delayed (lazy reduction with
    values kept < 2p).

Usage:
    python gen_fp_asm_broadwell.py --c 3 --t 324 -o fp_asm.S
    python gen_fp_asm_broadwell.py --c 3 --t 632 --spill-pointers -o fp_asm.S
    python gen_fp_asm_broadwell.py --c 17 --t 664 --spill-pointers-max -o fp_asm.S

Notes: (08.03.2026) supports primes with up to 11 limbs (704 bits max.):
  * up to 8 limbs, all pointers stay in registers;
  * 9-10 limbs need --spill-pointers (rdi parked in the frame, rcx replaced
    by a buffer);
  * 11 limbs need --spill-pointers-max (rsi also parked, a read from the frame).
"""

import argparse
import os
import sys

POOL = ["r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", "rax"]
EXTRA = ["rbx", "rbp"]
CALLEE_SAVED = ("rbx", "rbp", "r12", "r13", "r14", "r15")

# Register budget for the interleaved Montgomery loop:
#   rsp : stack;  rdx : implicit mulx operand;  rdi/rsi/rcx : dst/a/b pointers
# leaving rax, rbx, rbp, r8-r15 (11 registers) for N+1 accumulators + 2 temps.
MAX_LIMBS_REGS = 8            # N+3 <= 11
MAX_LIMBS_SPILL = 10          # rdi saved to the frame, rcx replaced by a buffer
MAX_LIMBS_SPILL_MAX = 11      # rsi also parked; a is read from the frame


# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------
class Params:
    def __init__(self, c, t, spill_pointers=False, spill_max=False):
        self.c = c
        self.t = t
        self.p = c * (1 << t) - 1
        self.bits = self.p.bit_length()
        self.N = (self.bits + 63) // 64
        self.W = 64 * self.N
        self.bytes = (self.bits + 7) // 8
        self.spill_max = spill_max
        self.spill = spill_pointers or spill_max

        # Shift that isolates the spare (headroom) bits of the top limb;
        # drives the delayed modular corrections.
        self.shift = self.bits - 64 * (self.N - 1)
        self.spare = 64 - self.shift

        # p = 2^t - 1 : all limbs below the top are 0xFFFF...FF and the top
        # limb is 2^shift - 1, so the modular corrections collapse to a
        # fold-and-mask (single pass instead of two conditional passes).
        self.mersenne = (c == 1)
        # Montgomery outputs are bounded by numerator/2^(64N) + p; when that
        # exceeds 2^bits (Mersenne: the gap p to 2^bits is 1) the kernels need
        # one final masked subtraction of p.  8*2^(2*bits) covers fp2_sq_c0's
        # (a0+a1)*(a0-a1+2p) worst case.
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

        limit = (MAX_LIMBS_SPILL_MAX if spill_max else
                 MAX_LIMBS_SPILL if spill_pointers else MAX_LIMBS_REGS)
        if self.N > limit:
            if not self.spill and self.N <= MAX_LIMBS_SPILL:
                raise ValueError(
                    "p is %d bits (%d limbs): the interleaved loop needs "
                    "N+3 = %d registers but only 11 are free. Re-run with "
                    "--spill-pointers to park rdi/rcx in the stack frame."
                    % (self.bits, self.N, self.N + 3))
            if self.N <= MAX_LIMBS_SPILL_MAX:
                raise ValueError(
                    "p is %d bits (%d limbs): re-run with --spill-pointers-max "
                    "to park rsi as well and read a from the stack frame."
                    % (self.bits, self.N))
            raise ValueError(
                "p is %d bits (%d limbs), above the %d-limb (%d-bit) ceiling "
                "of this register-resident generator. A field this large needs "
                "a blocked schedule with the accumulator in a stack frame, "
                "which is not implemented here."
                % (self.bits, self.N, MAX_LIMBS_SPILL_MAX,
                   64 * MAX_LIMBS_SPILL_MAX))

        # p + 1 = c * 2^t : only the top limb is non-zero.
        self.p_plus_1 = [0] * self.N
        self.p_plus_1[self.N - 1] = (c << (t - 64 * (self.N - 1))) & (2**64 - 1)

        # N+1 accumulators, 2 temporaries.  rdi/rcx precede rbx/rbp so that
        # N<=8 reproduces the reference allocation exactly.
        self.pool = (POOL + (["rdi", "rcx"] if self.spill else [])
                     + (["rsi"] if spill_max else []) + EXTRA)
        if len(self.pool) < self.N + 3:
            raise ValueError("internal: register pool too small for N=%d" % self.N)
        self.acc = self.pool[: self.N + 1]
        self.T0, self.T1 = self.pool[self.N + 1: self.N + 3]
        self.used = self.acc + [self.T0, self.T1]
        # In spill mode the 2p-b1 (fp2_mul_c0) and a0-a1+2p (fp2_sq_c0) blocks
        # use rbp in place of rax, since rax is their subtrahend temporary.
        if spill_pointers and "rbp" not in self.used:
            self.used = self.used + ["rbp"]
        self.saved = [r for r in CALLEE_SAVED if r in self.used]

    def off(self, base, i):
        return base if i == 0 else "%s+%d" % (base, 8 * i)

    def mem(self, base, i):
        return "[%s]" % self.off(base, i)

    def frame(self, nwords):
        size = 8 * nwords + (8 if self.spill else 0)
        return (size + 15) & ~15 if size else 0

    def rdi_slot(self, nwords):
        return 8 * nwords

    def buf(self, i):
        return self.mem("rsp", i)


def hexq(v):
    return "0x%016X" % v


# --------------------------------------------------------------------------
# Prologue / epilogue / frame helpers
# --------------------------------------------------------------------------
def prologue(regs, ind="    "):
    return "".join("%spush   %s\n" % (ind, r) for r in regs)


def epilogue(regs, ind="    "):
    return "".join("%spop    %s\n" % (ind, r) for r in reversed(regs))


def frame_open(P, nwords, ind="    "):
    f = P.frame(nwords)
    if not f:
        return ""
    s = "%ssub    rsp, %d\n" % (ind, f)
    if P.spill:
        s += "%smov    [rsp+%d], rdi          // park the dst pointer\n" % (
            ind, P.rdi_slot(nwords))
    return s


def frame_close(P, nwords, ind="    "):
    f = P.frame(nwords)
    return "%sadd    rsp, %d\n" % (ind, f) if f else ""


def dst_pointer(P, nwords, dead="rsi", ind="    "):
    """In spill mode rdi may hold a result limb, so reload into a dead reg.

    Below 11 limbs rsi (the `a` pointer) is dead by then; at 11 limbs rsi is an
    accumulator and the caller passes st[N], which is dead after the rotation.
    """
    if not P.spill:
        return "", "rdi"
    return ("%smov    %s, [rsp+%d]           // reload the dst pointer\n"
            % (ind, dead, P.rdi_slot(nwords))), dead


def copy_words(P, src, src_index, dst_index, n, ind="    "):
    s = []
    for i in range(n):
        s.append("%smov    rax, %s\n" % (ind, P.mem(src, src_index + i)))
        s.append("%smov    %s, rax\n" % (ind, P.buf(dst_index + i)))
    return "".join(s)


# --------------------------------------------------------------------------
# Header and macros
# --------------------------------------------------------------------------
def gen_header(P):
    quads = ", ".join(hexq(v) for v in P.p_plus_1)
    return f"""#include <sqisign_namespace.h>
.intel_syntax noprefix

.set pbytes,{P.bytes}
.set plimbs,{P.N}

#ifdef __APPLE__
.section __TEXT,__const
#else
.section .rodata
#endif
// p + 1 = {P.c} * 2^{P.t}
p_plus_1: .quad {quads}

#if defined(__linux__) && defined(__ELF__)
.section .note.GNU-stack,"",@progbits
#endif

#include <asm_preamble.h>

.text
.p2align 4,,15
"""


def gen_macros(P):
    N = P.N
    Z = ["Z%d" % i for i in range(N + 1)]
    out = [f"""
///////////////////////////////////////////////////////////////// MACROS
// z = a x bi + z
// Inputs: base memory pointer M1 (a), bi pre-stored in rdx,
//         accumulator z in [{Z[0]}:{Z[N]}]
// Output: [{Z[0]}:{Z[N]}]
// Temps:  regs T0:T1, carry-scratch C
/////////////////////////////////////////////////////////////////
.macro MULADD64x{P.W} M1, {", ".join(Z)}, T0, T1, C
    xor    \\C, \\C
    mulx   \\T0, \\T1, \\M1     // A0*B0
    adox   \\{Z[0]}, \\T1
    adox   \\{Z[1]}, \\T0"""]
    for i in range(1, N):
        out.append(f"""    mulx   \\T0, \\T1, {8*i}\\M1    // A0*B{i}
    adcx   \\{Z[i]}, \\T1
    adox   \\{Z[i+1]}, \\T0""")
    out.append(f"""    adc    \\{Z[N]}, 0
.endm

// z = (z0 x (p+1))/2^64 folded into the accumulator.
// p+1 = c*2^t has a single non-zero limb, so this is one 64x64 multiply.
.macro MULADD64x64 M1, {", ".join(Z[:N])}, T0, T1
    xor    \\T0, \\T0
    mulx   \\T0, \\T1, \\M1
    adox   \\{Z[N-2]}, \\T1
    adox   \\{Z[N-1]}, \\T0
.endm
""")
    return "\n".join(out)


# --------------------------------------------------------------------------
# fp_add / fp_sub
# --------------------------------------------------------------------------
def _addsub_regs(P):
    """rdi/rsi/rdx are the only live pointers here, so rcx/rbx/rbp are free;
    rax and rdx are reserved for the correction mask."""
    cand = [r for r in POOL if r != "rax"] + EXTRA + ["rcx"]
    if len(cand) < P.N:
        raise ValueError("fp_add/fp_sub need %d scratch registers, have %d"
                         % (P.N, len(cand)))
    return cand[: P.N]


def _correction_sub(P, regs, ind="  "):
    s = ["%smov    rax, %s\n" % (ind, regs[-1]),
         "%sshr    rax, %d\n" % (ind, P.shift),
         "%sneg    rax\n" % ind,
         "%smov    rdx, [rip+p+%d]\n" % (ind, 8 * (P.N - 1)),
         "%sand    rdx, rax\n" % ind,
         "%ssub    %s, rax\n" % (ind, regs[0])]
    for r in regs[1:-1]:
        s.append("%ssbb    %s, rax\n" % (ind, r))
    s.append("%ssbb    %s, rdx\n" % (ind, regs[-1]))
    return "".join(s)


def _correction_add(P, regs, mask_setup, ind="  "):
    s = [mask_setup,
         "%smov    rdx, [rip+p+%d]\n" % (ind, 8 * (P.N - 1)),
         "%sand    rdx, rax\n" % ind,
         "%sadd    %s, rax\n" % (ind, regs[0])]
    for r in regs[1:-1]:
        s.append("%sadc    %s, rax\n" % (ind, r))
    s.append("%sadc    %s, rdx\n" % (ind, regs[-1]))
    return "".join(s)

def _mersenne_mask(P, regs, ind="  "):
    """Reduce the top limb mod 2^shift; the overflow was already folded in."""
    return ("%smov    rax, [rip+p+%d]\n" % (ind, 8 * (P.N - 1)) +
            "%sand    %s, rax\n" % (ind, regs[-1]))


def _mersenne_add(P, regs, ind="  "):
    """p = 2^t-1: fold the bits above the top limb back into limb 0."""
    s = ["%smov    rax, %s\n" % (ind, regs[-1]),
         "%sshr    rax, %d\n" % (ind, P.shift),
         "%sadd    %s, rax\n" % (ind, regs[0])]
    for r in regs[1:]:
        s.append("%sadc    %s, 0\n" % (ind, r))
    return "".join(s) + _mersenne_mask(P, regs, ind)


def _mersenne_sub(P, regs, ind="  "):
    """p = 2^t-1: rax is the 0/-1 borrow mask; adding it adds 2^(64N)-1."""
    s = ["%sadd    %s, rax\n" % (ind, regs[0])]
    for r in regs[1:]:
        s.append("%sadc    %s, rax\n" % (ind, r))
    return "".join(s) + _mersenne_mask(P, regs, ind)

def gen_fp_add(P):
    regs = _addsub_regs(P)
    saved = [r for r in CALLEE_SAVED if r in regs]
    s = ["\n.global fp_add\nfp_add:\n", prologue(saved, "  "), "  xor    rax, rax\n"]
    for i, r in enumerate(regs):
        s.append("  mov    %s, %s\n" % (r, P.mem("rsi", i)))
    s.append("  add    %s, %s\n" % (regs[0], P.mem("rdx", 0)))
    for i, r in enumerate(regs[1:], 1):
        s.append("  adc    %s, %s\n" % (r, P.mem("rdx", i)))
    if P.mersenne:
        s.append("\n" + _mersenne_add(P, regs))
    else:
        # Inputs are < 2p, so at most two conditional subtractions are needed.
        s.append("\n" + _correction_sub(P, regs))
        s.append("\n" + _correction_sub(P, regs))
    s.append("\n")
    for i, r in enumerate(regs):
        s.append("  mov    %s, %s\n" % (P.mem("rdi", i), r))
    s.append(epilogue(saved, "  "))
    s.append("  ret\n")
    return "".join(s)


def gen_fp_sub(P):
    regs = _addsub_regs(P)
    saved = [r for r in CALLEE_SAVED if r in regs]
    s = ["\n.global fp_sub\nfp_sub:\n", prologue(saved, "  "), "  xor    rax, rax\n"]
    for i, r in enumerate(regs):
        s.append("  mov    %s, %s\n" % (r, P.mem("rsi", i)))
    s.append("  sub    %s, %s\n" % (regs[0], P.mem("rdx", 0)))
    for i, r in enumerate(regs[1:], 1):
        s.append("  sbb    %s, %s\n" % (r, P.mem("rdx", i)))
    s.append("  sbb    rax, 0\n")
    if P.mersenne:
        s.append("\n" + _mersenne_sub(P, regs))
    else:
        # First correction: mask = borrow.  Second: mask = sign of the top limb.
        s.append("\n" + _correction_add(P, regs, ""))
        mask = "  mov    rax, %s\n  sar    rax, %d\n" % (regs[-1], P.shift)
        s.append("\n" + _correction_add(P, regs, mask))
    s.append("\n")
    for i, r in enumerate(regs):
        s.append("  mov    %s, %s\n" % (P.mem("rdi", i), r))
    s.append(epilogue(saved, "  "))
    s.append("  ret\n")
    return "".join(s)


# --------------------------------------------------------------------------
# Interleaved Montgomery building blocks
# --------------------------------------------------------------------------
def first_column(P, state, bi, srcbase, ind="    "):
    """[state] <- a x b_i  (fresh accumulator, no addition)."""
    N, acc = P.N, state
    s = ["%smov    rdx, %s\n" % (ind, bi),
         "%smulx   %s, %s, %s\n" % (ind, acc[1], acc[0], P.mem(srcbase, 0)),
         "%sxor    %s, %s              // clears CF and OF\n"
         % (ind, acc[N], acc[N])]
    for i in range(1, N):
        s.append("%smulx   %s, %s, %s\n"
                 % (ind, acc[i + 1], P.T1, P.mem(srcbase, i)))
        s.append("%sadcx   %s, %s\n" % (ind, acc[i], P.T1))
    s.append("%sadc    %s, 0\n" % (ind, acc[N]))
    return "".join(s)


def muladd(P, state, mem, C, ind="    "):
    return "%sMULADD64x%d %s, %s, %s, %s, %s\n" % (
        ind, P.W, mem, ", ".join(state), P.T0, P.T1, C)


def reduce_step(P, state, ind="    "):
    s = "%smov    rdx, %s                 // rdx <- z0\n" % (ind, state[0])
    s += "%sMULADD64x64 [rip+p_plus_1+%d], %s, %s, %s\n" % (
        ind, 8 * (P.N - 1), ", ".join(state[1:]), P.T0, P.T1)
    return s, state[1:] + state[:1]


def store_result(P, state, dst, ind="    "):
    return "".join("%smov    %s, %s\n" % (ind, P.mem(dst, i), state[i])
                   for i in range(P.N))


def rotate(P, state):
    return state[P.N:] + state[: P.N]


def _domain_fold(P, st, ind="    "):
    """One masked subtraction of p brings the result into [0, 2^bits)."""
    s = ["%smov    %s, %s\n" % (ind, P.T1, st[P.N - 1]),
         "%sshr    %s, %d\n" % (ind, P.T1, P.shift),
         "%sneg    %s\n" % (ind, P.T1),
         "%smov    %s, [rip+p+%d]\n" % (ind, P.T0, 8 * (P.N - 1)),
         "%sand    %s, %s\n" % (ind, P.T0, P.T1),
         "%ssub    %s, %s\n" % (ind, st[0], P.T1)]
    for r in st[1:P.N - 1]:
        s.append("%ssbb    %s, %s\n" % (ind, r, P.T1))
    s.append("%ssbb    %s, %s\n" % (ind, st[P.N - 1], P.T0))
    return "".join(s)


def gen_fpmul_macro(P):
    N = P.N
    Z = ["Z%d" % i for i in range(N + 1)]
    st = ["\\" + z for z in Z]
    body = [f"""
///////////////////////////////////////////////////////////////// MACRO
// z = a x b (mod p)
// Inputs: base memory pointers M0 (a), M1 (b)
//         accumulator z in [{Z[0]}:{Z[N]}], pre-loaded with a0 x b
// Output: [{Z[0]}:{Z[N]}] (rotated by N positions)
// Temps:  regs T0:T1
/////////////////////////////////////////////////////////////////
.macro FPMUL{P.W}x{P.W} M0, M1, {", ".join(Z)}, T0, T1"""]

    def red(state):
        s = "    mov    rdx, %s                 // rdx <- z0\n" % state[0]
        s += "    MULADD64x64 [rip+p_plus_1+%d], %s, \\T0, \\T1\n" % (
            8 * (N - 1), ", ".join(state[1:]))
        return s, state[1:] + state[:1]

    code, st = red(st)
    body.append(code)
    for i in range(1, N):
        body.append("    // z = a%02d x b + z" % i)
        body.append("    mov    rdx, %d\\M0" % (8 * i))
        body.append("    MULADD64x%d \\M1, %s, \\T0, \\T1, %s"
                    % (P.W, ", ".join(st), st[N]))
        code, st = red(st)
        body.append(code.rstrip("\n"))
    body.append(".endm\n")
    return "\n".join(body)


def fpmul_call(P, M0, M1, state, ind="    "):
    return "%sFPMUL%dx%d %s, %s, %s, %s, %s\n" % (
        ind, P.W, P.W, M0, M1, ", ".join(state), P.T0, P.T1)


def _scratch_regs(P, n, live=("rdi", "rcx", "rsi"), avoid=()):
    """n registers that are free at this point in the routine.

    ``live`` names the pointers still in use there: rdi is free once parked,
    rcx is untouched by the fp2_sq_* routines, and rsi is free once a has been
    copied to the frame.  ``avoid`` names registers reserved as an explicit
    temporary; when rax is reserved, rbp takes its slot.
    """
    cand = [r for r in P.pool if r not in live and r not in avoid]
    if avoid and "rbp" in cand and "rbx" in cand:
        cand.remove("rbp")
        cand.insert(cand.index("rbx"), "rbp")
    if len(cand) < n:
        raise ValueError("not enough scratch registers (%d < %d)" % (len(cand), n))
    return cand[:n]


# --------------------------------------------------------------------------
# fp_mul / fp_sqr
# --------------------------------------------------------------------------
def gen_fp_mul(P):
    N = P.N
    st = list(P.acc)
    nw = (2 * N if P.spill_max else N) if P.spill else 0
    s = ["""
//***********************************************************************
//  Field multiplication in GF(p)
//  Operation: c = a x b mod p
//  Inputs: a stored in [rsi], b stored in [rdx]
//  Output: c stored in [rdi]
//***********************************************************************
.global fp_mul
fp_mul:
"""]
    s.append(prologue(P.saved))
    s.append("    mov    rcx, rdx\n")
    s.append(frame_open(P, nw))
    if P.spill:
        s.append("    // free rcx: copy b into the scratch frame\n")
        s.append(copy_words(P, "rcx", 0, 0, N))
    if P.spill_max:
        s.append("    // free rsi: copy a into the scratch frame\n")
        s.append(copy_words(P, "rsi", 0, N, N))
    M0 = "[rsp]" if P.spill else "[rcx]"
    abase = ("rsp+%d" % (8 * N)) if P.spill_max else "rsi"
    s.append("\n    // [%s:%s] <- z = a x b0\n" % (st[0], st[-1]))
    s.append(first_column(P, st, M0, abase))
    s.append("\n")
    s.append(fpmul_call(P, M0, "[%s]" % abase, st))
    st = rotate(P, st)
    s.append("\n")
    ptr_code, dst = dst_pointer(P, nw, st[N] if P.spill_max else "rsi")
    s.append(ptr_code)
    if P.needs_fold:
        s.append(_domain_fold(P, st))
    s.append(store_result(P, st, dst))
    s.append(frame_close(P, nw))
    s.append(epilogue(P.saved))
    s.append("    ret\n")
    return "".join(s)


def gen_fp_sqr(P):
    return """
//***********************************************************************
//  Field squaring in GF(p)
//  Operation: c = a^2 mod p
//  Input: a stored in [rsi]
//  Output: c stored in [rdi]
//***********************************************************************
.global fp_sqr
fp_sqr:
    mov    rdx, rsi
    jmp    fp_mul
"""


# --------------------------------------------------------------------------
# fp2_mul_c0 / fp2_mul_c1
# --------------------------------------------------------------------------
def gen_2p_minus(P, dst_base, dst_index, src, src_index, regs, ind="\t"):
    """[dst + 8*dst_index ..] <- 2p - [src + 8*src_index ..].

    src_index selects which half of an fp2_t operand is read: 0 for the
    real part (b0), N for the imaginary part (b1).
    """
    N = P.N
    s = ["%smov    %s, [rip+p2]\n" % (ind, regs[0]),
         "%smov    %s, [rip+p2+8]\n" % (ind, regs[1])]
    for r in regs[2:-1]:
        s.append("%smov    %s, %s\n" % (ind, r, regs[1]))
    s.append("%smov    %s, [rip+p2+%d]\n" % (ind, regs[-1], 8 * (N - 1)))
    for i in range(0, N, 2):
        s.append("%smov    rax, %s\n" % (ind, P.mem(src, src_index + i)))
        if i + 1 < N:
            s.append("%smov    rdx, %s\n" % (ind, P.mem(src, src_index + i + 1)))
        s.append("%s%s    %s, rax\n" % (ind, "sub" if i == 0 else "sbb", regs[i]))
        if i + 1 < N:
            s.append("%ssbb    %s, rdx\n" % (ind, regs[i + 1]))
    for i in range(N):
        s.append("%smov    %s, %s\n"
                 % (ind, P.mem(dst_base, dst_index + i), regs[i]))
    return "".join(s)


def gen_fp2_mul(P, imaginary):
    """imaginary=False: c = a0*b0 - a1*b1 ; True: c = a0*b1 + a1*b0."""
    N, B = P.N, 8 * P.N
    st = list(P.acc)
    name = "fp2_mul_c1" if imaginary else "fp2_mul_c0"
    op = "a0 x b1 + a1 x b0" if imaginary else "a0 x b0 - a1 x b1"
    nw = (4 * N if P.spill_max else 2 * N) if P.spill else 0
    ab = 2 * N                      # frame index of a0 in --spill-pointers-max
    s = [f"""
//***********************************************************************
//  Multiplication in GF(p^2), {"complex" if imaginary else "non-complex"} part
//  Operation: c [rdi] = {op}
//  Inputs: a = [a1, a0] stored in [rsi]
//          b = [b1, b0] stored in [rdx]
//  Output: c stored in [rdi]
//***********************************************************************
.global {name}
{name}:
"""]
    s.append(prologue(P.saved))
    s.append("    mov    rcx, rdx\n")
    s.append(frame_open(P, nw))

    if imaginary:
        if P.spill:
            s.append("    // free rcx: copy b0 and b1 into the scratch frame\n")
            s.append(copy_words(P, "rcx", 0, 0, 2 * N))
            w0 = lambda i: P.buf(N + i)     # b1 words (paired with a0)
            w1 = lambda i: P.buf(i)         # b0 words (paired with a1)
        else:
            w0 = lambda i: P.mem("rcx", N + i)
            w1 = lambda i: P.mem("rcx", i)
        if P.spill_max:
            s.append("    // free rsi: copy a0 and a1 into the scratch frame\n")
            s.append(copy_words(P, "rsi", 0, ab, 2 * N))
    else:
        # c0 negates b1 lazily: 2p - b1 is kept in the scratch area.
        scr = "rsp" if P.spill else "rdi"
        if P.spill:
            s.append("    // free rcx: copy b0 into the scratch frame\n")
            s.append(copy_words(P, "rcx", 0, 0, N))
        if P.spill_max:
            s.append("    // free rsi: copy a0 and a1 into the scratch frame\n")
            s.append(copy_words(P, "rsi", 0, ab, 2 * N))
        # rax is the subtrahend temporary in gen_2p_minus, so the p2 limbs
        # must be allocated elsewhere (rbp instead of rax).
        live = ("rcx",) if P.spill_max else ("rdi", "rcx", "rsi")
        s.append("\t// [%s] <- 2p - b1\n" % scr)
        s.append(gen_2p_minus(P, scr, N if P.spill else 0, "rcx", N,
                              _scratch_regs(P, N, live=live, avoid=("rax",)),
                              "\t"))
        s.append("\n")
        if P.spill:
            w0 = lambda i: P.buf(i)         # b0 words    (paired with a0)
            w1 = lambda i: P.buf(N + i)     # 2p-b1 words (paired with a1)
        else:
            w0 = lambda i: P.mem("rcx", i)
            w1 = lambda i: P.mem("rdi", i)

    a0_base = ("rsp+%d" % (8 * ab)) if P.spill_max else "rsi"
    A0 = "[%s]" % a0_base
    A1 = ("[rsp+%d]" % (8 * (ab + N))) if P.spill_max else "[rsi+%d]" % B
    s.append("\n    // [%s:%s] <- z = a x b_0\n" % (st[0], st[-1]))
    s.append(first_column(P, st, w0(0), a0_base))
    s.append("\n")
    s.append("    mov    rdx, %s\n" % w1(0))
    s.append(muladd(P, st, A1, P.T0))
    code, st = reduce_step(P, st)
    s.append(code + "\n")

    for i in range(1, N):
        s.append("    // z = a0 x b0_%d %s a1 x b1_%d + z\n"
                 % (i, "+" if imaginary else "-", i))
        s.append("    mov    rdx, %s\n" % w0(i))
        s.append(muladd(P, st, A0, st[N]))
        s.append("    mov    rdx, %s\n" % w1(i))
        s.append(muladd(P, st, A1, P.T0))
        code, st = reduce_step(P, st)
        s.append(code + "\n")

    ptr_code, dst = dst_pointer(P, nw, st[N] if P.spill_max else "rsi")
    s.append(ptr_code)
    if P.needs_fold:
        s.append(_domain_fold(P, st))
    s.append(store_result(P, st, dst))
    s.append(frame_close(P, nw))
    s.append(epilogue(P.saved))
    s.append("    ret\n")
    return "".join(s)


def gen_fp2_mul_c0(P):
    return gen_fp2_mul(P, False)


def gen_fp2_mul_c1(P):
    return gen_fp2_mul(P, True)


# --------------------------------------------------------------------------
# fp2_sq_c0 / fp2_sq_c1
# --------------------------------------------------------------------------
def gen_fp2_sq_c0(P):
    N, B = P.N, 8 * P.N
    # rax carries the p2 limbs in the a0-a1+2p block, so it must not also hold
    # an a0 limb.  rdi is already parked and rcx is unused here, so both are
    # available as scratch at 11 limbs.
    regs = _scratch_regs(P, N, live=("rsi",) if P.spill_max else
                         ("rdi", "rcx", "rsi"), avoid=("rax",))
    st = list(P.acc)
    nw = 2 * N if P.spill else 0
    scr = "rsp" if P.spill else "rdi"
    s = ["""
//***********************************************************************
//  Squaring in GF(p^2), non-complex part
//  Operation: c [rdi] = (a0+a1) x (a0-a1)
//  Inputs: a = [a1, a0] stored in [rsi]
//  Output: c stored in [rdi]
//***********************************************************************
.global fp2_sq_c0
fp2_sq_c0:
"""]
    s.append(prologue(P.saved))
    s.append(frame_open(P, nw))

    s.append("\n\t// [%s] <- a0 + a1 (no reduction, kept lazy)\n" % scr)
    for i, r in enumerate(regs):
        s.append("\tmov    %s, %s\n" % (r, P.mem("rsi", i)))
    s.append("\tadd    %s, %s\n" % (regs[0], P.mem("rsi", N)))
    for i, r in enumerate(regs[1:], 1):
        s.append("\tadc    %s, %s\n" % (r, P.mem("rsi", N + i)))
    for i, r in enumerate(regs):
        s.append("\tmov    %s, %s\n" % (P.mem(scr, i), r))

    s.append("\n\t// [%s+%d] <- a0 - a1 + 2p\n" % (scr, B))
    for i, r in enumerate(regs):
        s.append("\tmov    %s, %s\n" % (r, P.mem("rsi", i)))
    s.append("\tsub    %s, %s\n" % (regs[0], P.mem("rsi", N)))
    for i, r in enumerate(regs[1:], 1):
        s.append("\tsbb    %s, %s\n" % (r, P.mem("rsi", N + i)))
    s.append("\tmov    rax, [rip+p2]\n")
    s.append("\tadd    %s, rax\n" % regs[0])
    s.append("\tmov    rax, [rip+p2+8]\n")
    for r in regs[1:-1]:
        s.append("\tadc    %s, rax\n" % r)
    s.append("\tadc    %s, [rip+p2+%d]\n" % (regs[-1], 8 * (N - 1)))
    for i, r in enumerate(regs):
        s.append("\tmov    %s, %s\n" % (P.mem(scr, N + i), r))

    s.append("\n    // [%s:%s] <- z = (a0+a1)_0 x (a0-a1+2p)\n" % (st[0], st[-1]))
    sum_base, diff_base = scr, "%s+%d" % (scr, B)
    s.append(first_column(P, st, "[%s]" % sum_base, diff_base))
    s.append("\n")
    s.append(fpmul_call(P, "[%s]" % sum_base, "[%s]" % diff_base, st))
    st = rotate(P, st)
    s.append("\n")
    ptr_code, dst = dst_pointer(P, nw, st[N] if P.spill_max else "rsi")
    s.append(ptr_code)
    if P.needs_fold:
        s.append(_domain_fold(P, st))
    s.append(store_result(P, st, dst))
    s.append(frame_close(P, nw))
    s.append(epilogue(P.saved))
    s.append("    ret\n")
    return "".join(s)


def gen_fp2_sq_c1(P):
    N, B = P.N, 8 * P.N
    st = list(P.acc)
    nw = 2 * N if P.spill_max else N     # 2a0 always lives on the stack
    s = ["""
//***********************************************************************
//  Squaring in GF(p^2), complex part
//  Operation: c [rdi] = 2a0 x a1
//  Inputs: a = [a1, a0] stored in [rsi]
//  Output: c stored in [rdi]
//***********************************************************************
.global fp2_sq_c1
fp2_sq_c1:
"""]
    s.append(prologue(P.saved))
    if P.spill_max:
        # park rdi and free rsi first: both are scratch for the 2a0 block.
        s.append(frame_open(P, nw, "\t"))
        s.append("\t// free rsi: copy a1 into the scratch frame\n")
        s.append(copy_words(P, "rsi", N, N, N, "\t"))
    regs = _scratch_regs(P, N, live=("rsi",) if P.spill_max else
                         ("rdi", "rcx", "rsi"))
    s.append("\n\t// 2a0 (no reduction, kept lazy)\n")
    for i, r in enumerate(regs):
        s.append("\tmov    %s, %s\n" % (r, P.mem("rsi", i)))
    s.append("\tadd    %s, %s\n" % (regs[0], regs[0]))
    for r in regs[1:]:
        s.append("\tadc    %s, %s\n" % (r, r))
    if not P.spill_max:
        s.append(frame_open(P, nw, "\t"))
    for i, r in enumerate(regs):
        s.append("\tmov    %s, %s\n" % (P.buf(i), r))

    a1 = ("rsp+%d" % (8 * N)) if P.spill_max else "rsi+%d" % B
    s.append("\n    // [%s:%s] <- z = (2a0)_0 x a1\n" % (st[0], st[-1]))
    s.append(first_column(P, st, "[rsp]", a1))
    s.append("\n")
    s.append(fpmul_call(P, "[rsp]", "[%s]" % a1, st))
    st = rotate(P, st)
    s.append("\n")
    ptr_code, dst = dst_pointer(P, nw, st[N] if P.spill_max else "rsi")
    s.append(ptr_code)
    if P.needs_fold:
        s.append(_domain_fold(P, st))
    s.append(store_result(P, st, dst))
    s.append(frame_close(P, nw))
    s.append(epilogue(P.saved))
    s.append("    ret\n")
    return "".join(s)


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
def generate(c, t, spill_pointers=False, spill_max=False):
    P = Params(c, t, spill_pointers=spill_pointers, spill_max=spill_max)
    parts = [
        "// Auto-generated by gen_fp_asm_broadwell.py -- do not edit.\n"
        "// p = %d * 2^%d - 1  (%d bits, %d limbs, %d spare bits)%s\n"
        % (P.c, P.t, P.bits, P.N, P.spare,
           ("\n// Pointer spilling enabled (rdi%s parked in the stack frame)."
            % (" and rsi" if P.spill_max else "")) if P.spill else ""),
        gen_header(P),
        gen_fp_add(P),
        gen_fp_sub(P),
        gen_macros(P),
        gen_fp2_mul_c0(P),
        gen_fp2_mul_c1(P),
        gen_fpmul_macro(P),
        gen_fp2_sq_c0(P),
        gen_fp2_sq_c1(P),
        gen_fp_mul(P),
        gen_fp_sqr(P),
    ]
    return P, "\n".join(parts)



# The committed primes under scripts/Broadwell/; the spill mode follows
# from the limb count (<=8 none, 9-10 --spill-pointers, 11 --spill-pointers-max).
COMMITTED = [(5, 248), (3, 306), (3, 458), (27, 500), (1, 607),
             (17, 664), (19, 665)]


def self_test():
    """Regression check: regeneration, parse_prime, and the input guard."""
    here = os.path.dirname(os.path.abspath(__file__))
    fails = []

    for c, t in COMMITTED:
        ref = os.path.join(here, "..", "Broadwell", "p%d.%d" % (t, c), "fp_asm.S")
        if not os.path.exists(ref):
            print("  SKIP  p%d.%d (no committed reference)" % (t, c)); continue
        n = ((c * (1 << t) - 1).bit_length() + 63) // 64
        _, got = generate(c, t, spill_pointers=(8 < n <= 10), spill_max=(n == 11))
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

    for c, t, spill, accept in [(5, 248, False, True), (27, 500, False, True),
                                (3, 306, False, True), (1, 607, True, True),
                                (3, 250, False, True), (3, 251, False, False),
                                (3, 252, False, False), (65, 376, False, False)]:
        try:
            Params(c, t, spill_pointers=spill); got = True
        except ValueError:
            got = False
        ok = got == accept
        print("  %-6s guard c=%d t=%d -> %s" % ("ok" if ok else "FAIL", c, t,
                                                "accept" if got else "reject"))
        if not ok:
            fails.append("guard c=%d t=%d" % (c, t))

    print("\nself-test: %s" % ("PASS" if not fails else "FAIL (%s)" % ", ".join(fails)))
    print("semantic tests (x86-64 only): see scripts/Broadwell/test/run.sh")
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
    ap.add_argument("--spill-pointers", action="store_true",
                    help="park rdi/rcx in the stack frame to free two more "
                         "accumulators (needed for 9- and 10-limb primes)")
    ap.add_argument("--spill-pointers-max", action="store_true",
                    help="also park rsi and read a from the stack frame "
                         "(needed for 11-limb primes)")
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

    P, text = generate(c, t, spill_pointers=args.spill_pointers,
                       spill_max=args.spill_pointers_max)
    with open(args.output, "w", newline="\n") as f:
        f.write(text)
    print("Wrote %s: p = %d*2^%d-1, %d bits, %d limbs, %d spare bits%s"
          % (args.output, c, t, P.bits, P.N, P.spare,
             " (pointer spilling)" if P.spill else ""))


if __name__ == "__main__":
    main()
