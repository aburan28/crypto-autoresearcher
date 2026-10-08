#!/usr/bin/env python3
"""
Generator of the C binding for an asm (Broadwell/arm64) parameter set with
prime p = c * 2^t - 1.

The field arithmetic itself is not generated: the four hot kernels come from
gen_fp_asm_broadwell.py or gen_fp_asm_arm64.py and everything else from the
shared, prime-agnostic src/gf/sat64/lvlx/fp_generic.c. This script emits the
thin per-level layer that binds the two into the tree's fp API:

  src/gf/sat64/<name>/fp.c                          p and p2 for the asm
  src/gf/sat64/<name>/include/fp.h                  fp_t + API (via fp_generic.h)
  src/gf/sat64/<name>/include/fp2.h                 the four merged asm kernels
  src/gf/sat64/<name>/include/fp_generic_params.h   constants for fp_generic.c
  src/gf/sat64/<name>/test/CMakeLists.txt
  src/gf/broadwell/<name>/CMakeLists.txt
  src/gf/arm64/<name>/CMakeLists.txt

Usage:
    python gen_fp_c.py --name p248_5 --c 5 --t 248
    python gen_fp_c.py --name p248_5 --prime '5*2^248-1' --gf-root src/gf
"""

import argparse
import os
import re
import sys


class Params:
    def __init__(self, c, t):
        self.c = c
        self.t = t
        self.p = c * (1 << t) - 1
        self.bits = self.p.bit_length()
        self.N = (self.bits + 63) // 64
        self.shift = self.bits - 64 * (self.N - 1)
        self.spare = 64 - self.shift

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
        if c % 2 == 0 or c >= 1 << 31:
            raise ValueError("fp_generic needs odd c < 2^31 (got %d)" % c)

        R = (1 << (64 * self.N)) % self.p
        self.one = R % self.p
        self.R2 = (R * R) % self.p
        self.two_inv = (pow(2, -1, self.p) * R) % self.p
        self.three_inv = (pow(3, -1, self.p) * R) % self.p


def limbs(v, n, per_line=4, indent=" " * 4):
    ls = ["0x%016x" % ((v >> (64 * i)) & (2**64 - 1)) for i in range(n)]
    out = []
    for i in range(0, n, per_line):
        out.append(indent + ", ".join(ls[i:i + per_line]) + ",")
    return "\n".join(out).rstrip(",")


def init_list(v, n):
    return ", ".join("0x%016xULL" % ((v >> (64 * i)) & (2**64 - 1)) for i in range(n))


def gen_params_h(P, name):
    return f"""// {name}: p = {P.c} * 2^{P.t} - 1 ({P.bits} bits, {P.N} limbs)
#ifndef FP_GENERIC_PARAMS_H
#define FP_GENERIC_PARAMS_H

#define FPG_N {P.N}
#define FPG_BITS {P.bits}
#define FPG_C {P.c}ULL
#define FPG_T {P.t}

#define FPG_P_INIT {{ {init_list(P.p, P.N)} }}
#define FPG_ONE_INIT {{ {init_list(P.one, P.N)} }}
#define FPG_R2_INIT {{ {init_list(P.R2, P.N)} }}
#define FPG_TWO_INV_INIT {{ {init_list(P.two_inv, P.N)} }}
#define FPG_THREE_INV_INIT {{ {init_list(P.three_inv, P.N)} }}

#endif
"""


def gen_fp_h(P, name):
    guard = "FP_%s_H" % name.upper()
    return f"""#ifndef {guard}
#define {guard}

#include <sqisign_namespace.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <tutil.h>
#include <fp_constants.h>
#include <fp_generic.h>

_Static_assert(NWORDS_FIELD == FPG_N, "fp_constants.h disagrees with fp_generic_params.h");

// Type for elements of GF(p)
#define fp_t fpg_t

// Constants in Montgomery form, provided by fp_generic.c
#undef ZERO
#undef ONE
#define ZERO fpg_ZERO
#define ONE fpg_ONE

#endif
"""


def gen_fp2_h(P, name):
    guard = "FP2_%s_H" % name.upper()
    return f"""#ifndef {guard}
#define {guard}

#define NO_FP2X_MUL
#define NO_FP2X_SQR

#include <string.h>
#include <fp2x.h>

#ifdef SQISIGN_FP2_FUSED_ASM
/* The arm64 assembly computes both components in one call (fp2_mul via
 * Karatsuba, fp2_sqr sharing one frame and one load of the input). */
extern void fp2_mul(fp2_t *x, const fp2_t *y, const fp2_t *z);
extern void fp2_sqr(fp2_t *x, const fp2_t *y);
#else
extern void fp2_sq_c0(fp2_t *out, const fp2_t *in);
extern void fp2_sq_c1(fp_t *out, const fp2_t *in);

extern void fp2_mul_c0(fp_t *out, const fp2_t *in0, const fp2_t *in1);
extern void fp2_mul_c1(fp_t *out, const fp2_t *in0, const fp2_t *in1);

static inline void
fp2_mul(fp2_t *x, const fp2_t *y, const fp2_t *z)
{{
    fp_t t;

    fp2_mul_c0(&t, y, z);     // c0 = a0*b0 - a1*b1
    fp2_mul_c1(&x->im, y, z); // c1 = a0*b1 + a1*b0
    memcpy(&x->re, &t, sizeof(fp_t));
}}

static inline void
fp2_sqr(fp2_t *x, const fp2_t *y)
{{
    fp2_t t;

    fp2_sq_c0(&t, y);     // c0 = (a0+a1)(a0-a1)
    fp2_sq_c1(&x->im, y); // c1 = 2a0*a1
    memcpy(&x->re, &t.re, sizeof(fp_t));
}}
#endif

#endif
"""


def gen_fp_c_file(P, name):
    return f"""// {name}: p = {P.c} * 2^{P.t} - 1 ({P.bits} bits, {P.N} limbs, {P.spare} spare bits)
#include <fp.h>

const digit_t p[NWORDS_FIELD] = {{
{limbs(P.p, P.N)}
}};
const digit_t p2[NWORDS_FIELD] = {{
{limbs(2 * P.p, P.N)}
}};
"""


BROADWELL_CMAKE = """set(SOURCE_FILES_GF_SPECIFIC ${SAT64_DIR}/lvlx/fp_generic.c)
set(FP_ASM ${CMAKE_CURRENT_SOURCE_DIR}/fp_asm.S)

include(${SAT64_DIR}/lvlx.cmake)
"""

# The arm64 leaf additionally selects the fused fp2 entry points its
# assembly exports (Broadwell keeps the c0/c1 pairs).
ARM64_CMAKE = BROADWELL_CMAKE + """
target_compile_definitions(${LIB_GF_${SVARIANT_UPPER}} PUBLIC SQISIGN_FP2_FUSED_ASM)
"""

TEST_CMAKE = "include(../../lvlx_test.cmake)\n"


def check_asm_stamp(path, c, t, gen="gen_fp_asm_broadwell.py"):
    """Refuse to emit a binding that disagrees with an existing fp_asm.S."""
    if not os.path.exists(path):
        print("note: %s not found; generate it with %s --c %d --t %d"
              % (path, gen, c, t))
        return
    with open(path) as f:
        head = f.read(4096)
    m = re.search(r"^// p = (\d+) \* 2\^(\d+) - 1", head, re.M)
    if m and (int(m.group(1)), int(m.group(2))) != (c, t):
        raise SystemExit("error: %s was generated for p = %s*2^%s-1, not "
                         "p = %d*2^%d-1" % (path, m.group(1), m.group(2), c, t))


def parse_prime(text):
    """Accept 'c*2^t-1', or a raw (hex/dec) prime, and return (c, t)."""
    text = text.replace(" ", "").replace("**", "^")
    if "^" in text:
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
    ap.add_argument("--name", required=True,
                    help="variant name, e.g. p248_5 (letters/digits/underscore)")
    ap.add_argument("--c", type=int, help="cofactor c in p = c*2^t - 1")
    ap.add_argument("--t", type=int, help="exponent t in p = c*2^t - 1")
    ap.add_argument("--prime", help="prime as 'c*2^t-1' or as a decimal/hex value")
    ap.add_argument("--gf-root", default=None,
                    help="src/gf directory (default: relative to this script)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    args = ap.parse_args()

    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", args.name):
        ap.error("invalid name %r: must be a C-identifier-safe token "
                 "(it ends up in SQISIGN_VARIANT and in symbol names)" % args.name)

    if args.prime:
        c, t = parse_prime(args.prime)
    elif args.c is not None and args.t is not None:
        c, t = args.c, args.t
    else:
        ap.error("provide --prime or both --c and --t")

    P = Params(c, t)
    gf = args.gf_root or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", "..", "src", "gf")
    gf = os.path.normpath(gf)
    sat = os.path.join(gf, "sat64", args.name)
    bw = os.path.join(gf, "broadwell", args.name)
    a64 = os.path.join(gf, "arm64", args.name)

    files = {
        os.path.join(sat, "fp.c"): gen_fp_c_file(P, args.name),
        os.path.join(sat, "include", "fp.h"): gen_fp_h(P, args.name),
        os.path.join(sat, "include", "fp2.h"): gen_fp2_h(P, args.name),
        os.path.join(sat, "include", "fp_generic_params.h"): gen_params_h(P, args.name),
        os.path.join(sat, "test", "CMakeLists.txt"): TEST_CMAKE,
        os.path.join(bw, "CMakeLists.txt"): BROADWELL_CMAKE,
        os.path.join(a64, "CMakeLists.txt"): ARM64_CMAKE,
    }
    check_asm_stamp(os.path.join(bw, "fp_asm.S"), c, t)
    check_asm_stamp(os.path.join(a64, "fp_asm.S"), c, t, gen="gen_fp_asm_arm64.py")
    for path, text in files.items():
        if os.path.exists(path) and not args.force:
            print("skip  %s (exists; use --force)" % path)
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="\n") as f:
            f.write(text)
        print("write %s" % path)

    print("done: p = %d*2^%d-1, %d bits, %d limbs, %d spare bits"
          % (c, t, P.bits, P.N, P.spare))


if __name__ == "__main__":
    main()
