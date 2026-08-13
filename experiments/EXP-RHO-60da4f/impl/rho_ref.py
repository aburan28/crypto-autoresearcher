#!/usr/bin/env python3
"""
EXP-RHO-60da4f reference implementation "B" (Python), independently coded
from impl/rho.c for control C4 (two-implementation agreement on a frozen
seed at the smallest size). Mirrors the SAME algorithm (affine-native walk,
same splitmix64 PRNG, same hash-based branch selection, same canonicalization
and escape-rule definitions) but is a separate, independently written
codebase, per the spec's C4 requirement.

Also used standalone to validate the raw fruitless-2-cycle rate against the
1/(2r) prediction on the smallest curve, since it is fast enough in pure
Python at that size.
"""
import sys, json, argparse

MASK64 = (1 << 64) - 1

def splitmix64_stream(state):
    while True:
        state = (state + 0x9E3779B97f4A7C15) & MASK64
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        z = z ^ (z >> 31)
        yield z, state

class Field:
    def __init__(self, p):
        self.p = p
        self.mul = 0
        self.sqr = 0
        self.inv = 0
        self.counting = False
    def madd(self, a, b): return (a + b) % self.p
    def msub(self, a, b): return (a - b) % self.p
    def mmul(self, a, b):
        if self.counting: self.mul += 1
        return (a * b) % self.p
    def msqr(self, a):
        if self.counting: self.sqr += 1
        return (a * a) % self.p
    def minv(self, a):
        if self.counting: self.inv += 1
        return pow(a, -1, self.p)

class Curve:
    def __init__(self, p, a, b):
        self.F = Field(p)
        self.a = a; self.b = b
    def add(self, P, Q):
        F = self.F
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % F.p == 0:
                return None
            xx = F.msqr(x1)
            num = F.madd(F.madd(xx, xx), xx); num = F.madd(num, self.a)
            den = F.madd(y1, y1)
            lam = F.mmul(num, F.minv(den))
        else:
            num = F.msub(y2, y1)
            den = F.msub(x2, x1)
            lam = F.mmul(num, F.minv(den))
        x3 = F.msub(F.msub(F.msqr(lam), x1), x2)
        y3 = F.msub(F.mmul(lam, F.msub(x1, x3)), y1)
        return (x3, y3)
    def scalar_mult(self, P, k):
        R = None; Q = P
        while k:
            if k & 1: R = self.add(R, Q)
            Q = self.add(Q, Q)
            k >>= 1
        return R
    def canon(self, P):
        x, y = P
        if y <= (self.F.p - 1) // 2:
            return (x, y)
        return (x, self.F.p - y)

def hash_branch(x, key, rcount):
    z = (x ^ key) & MASK64
    z = ((z ^ (z >> 33)) * 0xff51afd7ed558ccd) & MASK64
    z = ((z ^ (z >> 33)) * 0xc4ceb9fe1a85ec53) & MASK64
    z = z ^ (z >> 33)
    return z % rcount

def hash_branch2(x, key, rcount):
    z = (x ^ key ^ 0xABCDEF1234567890) & MASK64
    z = ((z ^ (z >> 31)) * 0x9E3779B97F4A7C15) & MASK64
    z = ((z ^ (z >> 29)) * 0xBF58476D1CE4E5B9) & MASK64
    z = z ^ (z >> 32)
    return z % rcount

def run_walk(curve, G, N, seed, r, dp_bits, rule, k_param, step_budget, trace=None):
    F = curve.F
    # start point (setup, untimed)
    F.counting = False
    state = (seed * 2654435761 + 0x1234) & MASK64
    gen = splitmix64_stream(state)
    z, state = next(gen)
    k0 = 1 + z % (N - 1)
    start = curve.scalar_mult(G, k0)
    cur = curve.canon(start)

    # branch table (setup, untimed)
    state2 = (0xB4A17C1 ^ seed) & MASK64
    gen2 = splitmix64_stream(state2)
    branch = []
    for i in range(r):
        z2, state2 = next(gen2)
        e = 1 + z2 % (N - 1)
        Ri = curve.scalar_mult(G, e)
        branch.append(curve.canon(Ri))
    hash_key = (seed * 0x9E3779B97F4A7C15 + r * 31 + dp_bits * 7) & MASK64

    F.counting = True
    dp_mask = (1 << dp_bits) - 1 if dp_bits < 64 else MASK64
    seen_dp = set()
    hist_2back = None; hist_1back = None
    escape_triggers = 0
    raw_would_trigger = 0
    dp_count = 0
    fruitless_run = 0; fruitless_max = 0
    absorbed = False

    for t in range(step_budget):
        do_check = False
        if rule == "none": do_check = False
        elif rule == "det": do_check = True
        elif rule == "reselect": do_check = True
        elif rule == "periodic": do_check = (k_param > 0 and (t % k_param) == 0)
        elif rule == "lookahead": do_check = False

        escaped = False
        if rule == "lookahead":
            bidx = hash_branch(cur[0], hash_key, r)
            trial = curve.add(cur, branch[bidx])
            if trial is not None and trial[0] == cur[0]:
                bidx2 = hash_branch2(cur[0], hash_key, r)
                step_a = curve.add(cur, branch[bidx2])
                ca = curve.canon(step_a)
                bidx3 = hash_branch(ca[0], hash_key, r)
                step_b = curve.add(ca, branch[bidx3])
                cur = curve.canon(step_b)
                escape_triggers += 1
                escaped = True
            else:
                cur = curve.canon(trial)
            new_x = cur[0]
        else:
            bidx = hash_branch(cur[0], hash_key, r)
            cand = curve.add(cur, branch[bidx])
            cand_c = curve.canon(cand)
            would_2cycle = (hist_2back is not None and cand_c[0] == hist_2back)
            if would_2cycle: raw_would_trigger += 1
            if do_check and would_2cycle:
                bidx_alt = hash_branch2(cur[0], hash_key, r)
                res_pt = curve.add(cur, branch[bidx_alt])
                cur = curve.canon(res_pt)
                escape_triggers += 1
                escaped = True
            else:
                cur = cand_c
            new_x = cur[0]

        if escaped:
            fruitless_run += 1
            fruitless_max = max(fruitless_max, fruitless_run)
            absorbed = True
        else:
            fruitless_run = 0

        hist_2back = hist_1back; hist_1back = new_x

        if trace is not None and t < trace:
            print(f"t={t} x={cur[0]} y={cur[1]}", file=sys.stderr)

        if (cur[0] & dp_mask) == 0:
            dp_count += 1
            if cur[0] in seen_dp:
                return dict(steps=t+1, mul=F.mul, sqr=F.sqr, inv=F.inv,
                            escape_triggers=escape_triggers, dp_count=dp_count,
                            censored=0, collided=1,
                            longest_fruitless_run=fruitless_max,
                            absorbed_2cycle_detected=int(absorbed),
                            step_budget=step_budget,
                            raw_fruitless_would_trigger=raw_would_trigger)
            seen_dp.add(cur[0])

    return dict(steps=step_budget, mul=F.mul, sqr=F.sqr, inv=F.inv,
                escape_triggers=escape_triggers, dp_count=dp_count,
                censored=1, collided=0,
                longest_fruitless_run=fruitless_max,
                absorbed_2cycle_detected=int(absorbed),
                step_budget=step_budget,
                raw_fruitless_would_trigger=raw_would_trigger)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, required=True)
    ap.add_argument("--a", type=int, required=True)
    ap.add_argument("--b", type=int, required=True)
    ap.add_argument("--N", type=int, required=True)
    ap.add_argument("--gx", type=int, required=True)
    ap.add_argument("--gy", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--r", type=int, default=8)
    ap.add_argument("--dpbits", type=int, default=12)
    ap.add_argument("--escape", default="det")
    ap.add_argument("--k", type=int, default=0)
    ap.add_argument("--budget-mult", type=float, default=64.0)
    ap.add_argument("--trace", type=int, default=None)
    args = ap.parse_args()

    curve = Curve(args.p, args.a, args.b)
    G = (args.gx, args.gy)
    n2 = args.N / 2.0
    step_budget = max(1000, int(args.budget_mult * (n2 ** 0.5)))
    res = run_walk(curve, G, args.N, args.seed, args.r, args.dpbits, args.escape,
                    args.k, step_budget, trace=args.trace)
    print(json.dumps(res))

if __name__ == "__main__":
    main()
