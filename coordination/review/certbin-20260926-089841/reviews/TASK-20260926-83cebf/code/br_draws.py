"""Stream replay of the fresh arms, from EXP-CERTBIN-ddfe75
instance_sets.fresh_arms, generator_rule and keep_rule, literally.

One numpy.random.Generator(numpy.random.PCG64(seed)) per arm, consumed in slot
order and attempt order; no other call touches it.
"""
import hashlib
import numpy as np

import br_system as S
from br_sat import count_s

ARM_SEEDS = {"N-CONV": 2026092450101, "N-CONVL": 2026092450102,
             "N-CONV17": 2026092450103, "N-ELL144": 2026092450104}
MAX_ATTEMPT = 255


def e_key(E):
    """Content key for duplicate detection (equality of the 17 x 172 matrix)."""
    return hashlib.sha256(np.ascontiguousarray(E, dtype=np.uint8).tobytes()).hexdigest()


class ArmReplay:
    def __init__(self, arm, B, U, SL, slot_xr):
        self.arm = arm
        self.B = B
        self.U = U
        self.SL = SL
        self.slot_xr = slot_xr          # list of x_R by slot (used by N-CONV, N-CONVL)
        self.g = np.random.Generator(np.random.PCG64(ARM_SEEDS[arm]))
        self.kept_keys = {}             # key -> (slot, role)
        self.const_pos = [(k, c) for (k, c) in SL if c == 0]
        self.Upos = np.flatnonzero(U.reshape(-1))     # row-major
        self.Q17 = S.conv17_quadratic()

    # one draw = exactly the calls of the arm's draw rule
    def draw(self, slot):
        arm = self.arm
        g = self.g
        extra = {}
        if arm == "N-CONV":
            xR = self.slot_xr[slot]
            ES3 = S.E_S3(xR, self.B)
            bits = g.integers(0, 2, size=len(self.SL))
            E = np.zeros_like(ES3)
            E[:, S.QUAD_COLS] = ES3[:, S.QUAD_COLS]
            for (k, c), b in zip(self.SL, bits):
                E[k, c] = b
            reject = "identity" if np.array_equal(E, ES3) else None
        elif arm == "N-CONVL":
            xR = self.slot_xr[slot]
            ES3 = S.E_S3(xR, self.B)
            bits = g.integers(0, 2, size=len(self.const_pos))
            E = ES3.copy()
            E[:, 0] = 0
            for (k, c), b in zip(self.const_pos, bits):
                E[k, 0] = b
            own = [(self.B >> k) & 1 for (k, c) in self.const_pos]
            bprime = 0
            for (k, c), b in zip(self.const_pos, bits):
                if b:
                    bprime |= 1 << k
            extra["b_prime"] = bprime
            extra["drawn_bits"] = [int(b) for b in bits]
            if [int(b) for b in bits] == own:
                reject = "identity"
            elif not any(bits):
                reject = "b_prime_zero"
            else:
                reject = None
        elif arm == "N-CONV17":
            bits = g.integers(0, 2, size=len(self.SL))
            E = np.zeros((S.NEQ, S.NCOL_E), dtype=np.uint8)
            E[:, S.QUAD_COLS] = self.Q17[:, S.QUAD_COLS]
            for (k, c), b in zip(self.SL, bits):
                E[k, c] = b
            reject = None
        elif arm == "N-ELL144":
            M = np.zeros(S.NEQ * S.NCOL_E, dtype=np.uint8)
            M[self.Upos] = g.integers(0, 2, size=self.Upos.size)
            c = int(g.integers(0, 2))
            M = M.reshape(S.NEQ, S.NCOL_E)
            M[16, :] = 0
            M[16, S.E_COL[1 << 0]] = 1
            M[16, S.E_COL[1 << 9]] = 1
            M[16, 0] = c
            E = M
            extra["c"] = c
            reject = None
        else:
            raise ValueError(arm)
        return E.astype(np.uint8), reject, extra

    def run_slot(self, slot):
        attempts = []
        roles = {"unsat": None, "sat": None}
        for a in range(MAX_ATTEMPT + 1):
            E, reject, extra = self.draw(slot)
            key = e_key(E)
            if reject is None and key in self.kept_keys:
                reject = "duplicate"
            s, sols = count_s(E, want_solutions=True)
            rec = {"arm": self.arm, "slot": slot, "attempt": a,
                   "row_hex": S.row_hex(E), "s": s}
            rec.update(extra)
            if reject is not None:
                rec["outcome"] = "rejected"
                rec["reject_reason"] = reject
            elif s == 0:
                if roles["unsat"] is None:
                    roles["unsat"] = {"attempt": a, "E": E, "s": s, "key": key}
                    self.kept_keys[key] = (slot, "unsat")
                    rec["outcome"] = "kept_unsat"
                else:
                    rec["outcome"] = "discarded"
            else:
                if roles["sat"] is None:
                    roles["sat"] = {"attempt": a, "E": E, "s": s, "key": key, "solutions": sols}
                    self.kept_keys[key] = (slot, "sat")
                    rec["outcome"] = "kept_sat"
                else:
                    rec["outcome"] = "discarded"
            attempts.append(rec)
            if roles["unsat"] is not None and roles["sat"] is not None:
                break
        exhausted = [r for r in ("unsat", "sat") if roles[r] is None]
        return attempts, roles, exhausted
