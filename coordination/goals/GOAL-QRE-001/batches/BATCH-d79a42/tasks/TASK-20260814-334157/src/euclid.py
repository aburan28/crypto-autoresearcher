"""Reversible binary extended-Euclidean (Kaliski-style) modular inverter for
TASK-20260814-334157 (GOAL-QRE-001, BATCH-d79a42, lane A).

CONVENTION.  Inherited unchanged from BATCH-973b49 / TASK-20260813-c99166 and
restated clause-by-clause in this batch's frozen PREREGISTRATION.md section 1.
Gate set {X, CNOT, CCX}; T = 7 * Toffoli; all ancillas clean on allocation and
returned to |0>; uncomputation by exact circuit inverse; no measurement, no
feedforward, no borrowed ancilla.  This module IMPORTS BATCH-973b49's builder
(src/circuits.py) and adds a new inverter sub-circuit alongside the Fermat one;
it does not modify, re-implement or re-tune any inherited sub-circuit.  The
Machine, the adder, mod_add, mod_dbl, modmul_acc and point_add used here are
BATCH-973b49's own objects, so a count taken here is taken with the same
instrument that produced EV-QRE-45dfe1.

DERIVATION (nothing below is cited; every step is established in this file and
checked by classical simulation in run_validation_e.py).

Classical iteration, on state (u, v, r, s) with u, v exact non-negative
integers and r, s reduced modulo the odd prime p:

    if   u even                 : u <- u/2      ; s <- 2s mod p
    elif v even                 : v <- v/2      ; r <- 2r mod p
    elif u > v                  : u <- (u-v)/2  ; r <- (r+s) mod p ; s <- 2s mod p
    else                        : v <- (v-u)/2  ; s <- (s+r) mod p ; r <- 2r mod p

started from (u, v, r, s) = (p, x, 0, s0).

(D1) INVARIANT.  With s0 = 1 one checks branch by branch that
        r*x = -u * 2^k  (mod p)   and   s*x = v * 2^k  (mod p)
     after k iterations.  Base case k = 0: r*x = 0 = -p = -u*2^0, s*x = x = v.
     Branch 1: r, u/2 * 2^{k+1} = u*2^k unchanged; s'x = 2sx = 2v2^k = v2^{k+1}.
     Branch 2: r'x = 2rx = -u2^{k+1}; s unchanged and v/2 * 2^{k+1} = v2^k.
     Branch 3: r'x = rx + sx = (-u + v)2^k = -((u-v)/2) 2^{k+1};  s'x = v2^{k+1}.
     Branch 4: r'x = 2rx = -u2^{k+1};  s'x = sx + rx = (v-u)2^k = v' 2^{k+1}.

(D2) TERMINATION AND A FIXED STEP COUNT.  Let Phi = bitlength(u) + bitlength(v).
     Every branch replaces one of u, v by a strictly smaller non-negative
     integer of strictly smaller bitlength (u/2, v/2, (u-v)/2 < u, (v-u)/2 < v),
     so Phi drops by at least 1 per iteration.  Initially Phi <= n + n = 2n and
     the terminal state (u, v) = (1, 0) has Phi = 1, so the algorithm reaches
     v = 0 in at most 2n - 1 iterations.  The circuit therefore runs a FIXED
     K = 2n iterations for every input, which is what PREREGISTRATION clause 1.4
     requires (a worst-case-bounded fixed step count, the analogue of Fermat's
     fixed-length square-and-multiply chain).  The worst case 2n - 1 is
     additionally confirmed exhaustively for n = 3..16 in run_validation_e.py.

(D3) THE POST-TERMINAL STEPS ARE NOT WASTED, AND THEY REMOVE THE ITERATION
     COUNT FROM THE ANSWER.  Once v = 0 the state has u = gcd(p, x) = 1, which
     is odd, so every further iteration takes branch 2: v <- 0, r <- 2r.  Hence
     after the full fixed K iterations r*x = -2^K (mod p) with K = 2n a CLASSICAL
     CONSTANT -- the data-dependent iteration count k has cancelled.  No counter
     register and no v != 0 flag is needed anywhere in the circuit.

(D4) PHASE 2 IS FREE.  The (r, s) updates are linear in (r, s) and the branch
     decisions depend on (u, v) only, so (r_K, s_K) = M(p, x) . (r_0, s_0) for an
     integer matrix M depending only on (p, x).  With r_0 = 0 the final r is
     linear in s_0, so initialising
         s_0 = -2^{-K} mod p        (a classical constant, K = 2n)
     gives r_K = x^{-1} mod p directly.  The Montgomery-factor correction phase
     of the classical two-phase algorithm therefore costs zero gates here: it is
     absorbed into which classical constant the s register is initialised to by
     X gates.

(D5) GARBAGE AND CLEANLINESS.  Each iteration keeps eight one-bit control
     records (e, g1, b2, c, g3, g4, hu, hv).  They are NOT uncomputed inside the
     loop -- after an iteration u and v have moved, so they are no longer a
     function of the live state.  They are cleared by running the exact inverse
     of the whole phase-1 circuit after the answer has been copied out, exactly
     as BATCH-973b49's Fermat mod_inv clears its chain registers.  Total
     persistent garbage is 8K = 16n bits, i.e. LINEAR in n, against the Fermat
     chain's (b + w - 2) registers of n qubits each.  Every wider scratch
     register (comparison temporary, controlled-copy registers, adder carries)
     is released inside the iteration and reused by the next one.
"""

import os
import sys

_B1 = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))),
    "BATCH-973b49", "tasks", "TASK-20260813-c99166", "src")
if _B1 not in sys.path:
    sys.path.insert(0, _B1)

import circuits as C                                                  # noqa: E402
from circuits import Machine, add, sub, mod_add                       # noqa: E402,F401

# ---------------------------------------------------------------------------
# controlled primitives.  Each is built ONLY from X / CNOT / CCX and from the
# inherited adder; none of them modifies an inherited sub-circuit.
# ---------------------------------------------------------------------------


def ctrl_copy(m, ctrl, src, dst):
    """dst ^= src, controlled on ctrl.  len(src) Toffoli."""
    for a, b in zip(src, dst):
        m.ccx(ctrl, a, b)


def ctrl_sub_reg(m, ctrl, A, B):
    """B <- B - A if ctrl else B  (mod 2^len(B)).  A preserved.
    Cost: 2*len(A) (controlled copy in and out) + 2*len(A) (the inherited
    ripple subtractor) = 4*len(A) Toffoli."""
    k = len(A)
    Cr = m.alloc(k)
    ctrl_copy(m, ctrl, A, Cr)
    sub(m, Cr, B)
    ctrl_copy(m, ctrl, A, Cr)
    m.free(Cr)


def ctrl_rot_right(m, ctrl, R):
    """R <- R >>> 1 (cyclic, toward the least significant end) if ctrl.
    len(R)-1 controlled swaps = len(R)-1 Toffoli.  When the low bit of R is 0
    and its top bit is 0 this is exactly R <- R/2."""
    k = len(R)
    for i in range(k - 1):
        a, b = R[i], R[i + 1]
        m.cnot(b, a)
        m.ccx(ctrl, a, b)
        m.cnot(b, a)


def ctrl_mod_add(m, ctrl, A, B, M):
    """B <- (B + A) mod M if ctrl else B.  Requires 0 <= A, B < M.
    Cost: 2n (controlled copy in/out) + the inherited mod_add's 10(n+1)."""
    n = len(A)
    Cr = m.alloc(n)
    ctrl_copy(m, ctrl, A, Cr)
    C.mod_add(m, Cr, B, M)
    ctrl_copy(m, ctrl, A, Cr)
    m.free(Cr)


def ctrl_mod_dbl(m, ctrl, B, M):
    """B <- 2B mod M if ctrl else B.  Requires 0 <= B < M, M odd.

    Derived as the controlled analogue of the inherited mod_dbl: the rotation
    becomes a controlled rotation, the constant subtraction becomes a
    subtraction of (ctrl ? M : 0) -- the classical constant is loaded into a
    clean register by CNOTs from ctrl, which costs no Toffoli -- and the
    reduction flag is uncomputed with one extra Toffoli because when ctrl = 0
    the register is unchanged and the parity test that clears the flag in the
    uncontrolled circuit no longer applies.
    Cost: (n) rotation + 2(n+1) constant subtraction + 2(n+1) conditional
    re-add + 1 = 5n + 5 Toffoli."""
    n = len(B)
    (z,) = m.alloc(1)
    R = B + [z]
    ctrl_rot_left(m, ctrl, R)
    # subtract (ctrl ? M : 0)
    Cm = m.alloc(n + 1)
    for j in range(n + 1):
        if (M >> j) & 1:
            m.cnot(ctrl, Cm[j])
    sub(m, Cm, R)
    for j in range(n + 1):
        if (M >> j) & 1:
            m.cnot(ctrl, Cm[j])
    m.free(Cm)
    # z = 1  <=>  ctrl and 2B < M  <=>  a re-add is needed
    (t,) = m.alloc(1)
    m.cnot(z, t)
    Ca = m.alloc(n + 1)
    for j in range(n + 1):
        if (M >> j) & 1:
            m.cnot(t, Ca[j])
    add(m, Ca, R)
    for j in range(n + 1):
        if (M >> j) & 1:
            m.cnot(t, Ca[j])
    m.free(Ca)
    # uncompute t: t = 1 <=> ctrl and the result is even
    m.x(B[0])
    m.ccx(ctrl, B[0], t)
    m.x(B[0])
    m.free([t])
    m.free([z])


def ctrl_rot_left(m, ctrl, R):
    """R <- R <<< 1 (cyclic, toward the most significant end) if ctrl."""
    k = len(R)
    for i in range(k - 1, 0, -1):
        a, b = R[i], R[i - 1]
        m.cnot(b, a)
        m.ccx(ctrl, a, b)
        m.cnot(b, a)


# ---------------------------------------------------------------------------
# phase 1 of the inverter
# ---------------------------------------------------------------------------

def _euclid_phase1(m, X, p, keep, branch_order_swapped=False):
    """Run K = 2n fixed iterations of the derived binary-EEA recurrence.

    X is the n-bit input register (preserved).  Every register allocated here
    is appended to `keep` and stays live; the caller clears them by replaying
    the inverse of this block.  Returns the register holding r_K = x^-1 mod p.

    `branch_order_swapped` is the PRE-REGISTERED NEGATIVE CONTROL (section 5 of
    PREREGISTRATION.md): it exchanges which of the two mutually exclusive
    update rules is applied when the comparison bit is 0 versus 1, i.e. it
    swaps the u > v branch with the u <= v branch.  It is False in every
    counted or reported circuit.
    """
    n = len(X)
    K = 2 * n
    s0 = (-pow(pow(2, K, p), -1, p)) % p

    U = m.alloc(n + 1); keep.append(U)      # u, exact, top bit always 0
    V = m.alloc(n + 1); keep.append(V)      # v, exact, top bit always 0
    R = m.alloc(n);     keep.append(R)      # r mod p
    S = m.alloc(n);     keep.append(S)      # s mod p

    for j in range(n):                      # u <- p  (classical constant)
        if (p >> j) & 1:
            m.x(U[j])
    for j in range(n):                      # v <- x  (quantum input, copied)
        m.cnot(X[j], V[j])
    for j in range(n):                      # s <- s0 (classical constant)
        if (s0 >> j) & 1:
            m.x(S[j])

    for _ in range(K):
        e = m.alloc(1);  keep.append(e)     # u even
        g1 = m.alloc(1); keep.append(g1)    # u odd and v odd
        b2 = m.alloc(1); keep.append(b2)    # u odd and v even        (branch 2)
        c = m.alloc(1);  keep.append(c)     # u > v
        g3 = m.alloc(1); keep.append(g3)    # branch 3
        g4 = m.alloc(1); keep.append(g4)    # branch 4
        hu = m.alloc(1); keep.append(hu)    # u is halved  (branch 1 or 3)
        hv = m.alloc(1); keep.append(hv)    # v is halved  (branch 2 or 4)
        e, g1, b2, c, g3, g4, hu, hv = (e[0], g1[0], b2[0], c[0],
                                        g3[0], g4[0], hu[0], hv[0])

        m.x(U[0]); m.cnot(U[0], e); m.x(U[0])           # e = not u0
        m.ccx(U[0], V[0], g1)                           # g1 = u0 and v0
        m.cnot(U[0], b2); m.cnot(g1, b2)                # b2 = u0 and not v0

        # c = (u > v), by the sign bit of v - u on n+1 bits
        Tm = m.alloc(n + 1)
        for j in range(n + 1):
            m.cnot(V[j], Tm[j])
        sub(m, U, Tm)
        m.cnot(Tm[n], c)
        add(m, U, Tm)
        for j in range(n + 1):
            m.cnot(V[j], Tm[j])
        m.free(Tm)

        m.ccx(g1, c, g3)                                # g3 = both odd, u > v
        m.cnot(g1, g4); m.cnot(g3, g4)                  # g4 = both odd, u <= v

        lo, hi = (g4, g3) if branch_order_swapped else (g3, g4)

        ctrl_sub_reg(m, lo, V, U)                       # branch 3: u <- u - v
        ctrl_sub_reg(m, hi, U, V)                       # branch 4: v <- v - u

        m.cnot(e, hu); m.cnot(lo, hu)                   # hu = branch 1 or 3
        m.cnot(b2, hv); m.cnot(hi, hv)                  # hv = branch 2 or 4

        ctrl_mod_add(m, lo, S, R, p)                    # branch 3: r <- r + s
        ctrl_mod_add(m, hi, R, S, p)                    # branch 4: s <- s + r

        ctrl_rot_right(m, hu, U)                        # u <- u / 2
        ctrl_rot_right(m, hv, V)                        # v <- v / 2
        ctrl_mod_dbl(m, hu, S, p)                       # s <- 2s
        ctrl_mod_dbl(m, hv, R, p)                       # r <- 2r

    return R


def mod_inv_euclid(m, X, T, p, branch_order_swapped=False):
    """T <- x^-1 mod p for 1 <= x < p.  X preserved, T starts at |0>, every
    scratch register returned to |0> and released.

    Same signature and same contract as BATCH-973b49's Fermat mod_inv, so it
    can be substituted inside the inherited point_add without touching it.
    Structure is also the same: build phase 1, copy the result out with CNOTs,
    replay phase 1 inverted."""
    keep = []
    ops, res = m.capture(_euclid_phase1, X, p, keep, branch_order_swapped)
    m.replay(ops)
    for j in range(len(T)):
        m.cnot(res[j], T[j])
    m.replay(ops, invert=True)
    for r in reversed(keep):
        m.free(r)


# ---------------------------------------------------------------------------
# point addition with the new inverter substituted in
# ---------------------------------------------------------------------------

def point_add_euclid(m, X, Y, p, x2, y2, branch_order_swapped=False):
    """BATCH-973b49's point_add, byte for byte, with ONLY the modular inverter
    substituted.  point_add resolves `mod_inv` from its own module globals at
    call time, so rebinding that name runs the inherited source unmodified
    with the new inverter in the inversion slot.  Nothing else in the
    point-addition structure (coordinate subtractions, slope multiplication,
    uncomputation of lambda) is touched."""
    saved = C.mod_inv

    def _inv(mm, XX, TT, pp):
        return mod_inv_euclid(mm, XX, TT, pp, branch_order_swapped)

    C.mod_inv = _inv
    try:
        C.point_add(m, X, Y, p, x2, y2)
    finally:
        C.mod_inv = saved
