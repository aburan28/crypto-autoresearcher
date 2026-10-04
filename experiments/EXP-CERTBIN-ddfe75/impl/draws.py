"""Fresh-arm draw rules and the keep rule (specification instance_sets.fresh_arms,
generator_rule, keep_rule). One numpy PCG64 generator per arm, consumed in
slot order and attempt order; nothing else touches it.
"""
from __future__ import annotations

import numpy as np

import construct
import satcount
from common import MAX_ATTEMPTS, NCOL, NEQ, e_sha256, rows_to_hex


class ArmContext:
    def __init__(self, B, U, xr144):
        self.B = B
        self.U = U
        self.SL = construct.s_l_positions(U)
        self.const_pos = [(k, c) for (k, c) in self.SL if c == 0]
        self.xr144 = xr144
        self.s3 = [construct.e_s3(x, B) for (_, _, x) in xr144]
        self.qp = [construct.qpart(x) for (_, _, x) in xr144]
        ql = []
        for x in [x for (_, _, x) in xr144]:
            q, l_ = construct.qpart(x), construct.lpart(x)
            ql.append([a | b for a, b in zip(q, l_)])
        self.qlp = ql
        self.conv17 = construct.conv17_rows()
        upos = []
        for k in range(NEQ):
            for c in range(NCOL):
                if (U[k] >> c) & 1:
                    upos.append(k * NCOL + c)
        self.Upos = np.array(upos, dtype=np.int64)  # == flatnonzero(U) row-major
        self.B_bits_at_const = [(B >> k) & 1 for (k, _) in self.const_pos]


def _place(base, positions, bits):
    rows = list(base)
    for (k, c), b in zip(positions, bits):
        if b:
            rows[k] |= 1 << c
    return rows


def draw_once(arm, g, ctx, slot):
    """One attempt: -> (rows, info dict, rejection reason or None)."""
    info = {}
    if arm == "N-CONV":
        bits = g.integers(0, 2, size=len(ctx.SL)).tolist()
        rows = _place(ctx.qp[slot], ctx.SL, bits)
        rej = "identity" if rows == ctx.s3[slot] else None
    elif arm == "N-CONV17":
        bits = g.integers(0, 2, size=len(ctx.SL)).tolist()
        rows = _place(ctx.conv17, ctx.SL, bits)
        rej = None
    elif arm == "N-CONVL":
        bits = g.integers(0, 2, size=len(ctx.const_pos)).tolist()
        rows = _place(ctx.qlp[slot], ctx.const_pos, bits)
        bprime = 0
        for (k, _), b in zip(ctx.const_pos, bits):
            if b:
                bprime |= 1 << k
        info["bprime"] = bprime
        if bits == ctx.B_bits_at_const:
            rej = "identity"
        elif bprime == 0:
            rej = "bprime_zero"
        else:
            rej = None
    elif arm == "N-ELL144":
        M = np.zeros(NEQ * NCOL, dtype=np.uint8)
        M[ctx.Upos] = g.integers(0, 2, size=ctx.Upos.size)
        c = int(g.integers(0, 2))
        info["c"] = c
        M = M.reshape(NEQ, NCOL)
        rows = []
        for k in range(NEQ - 1):
            r = 0
            for j in np.flatnonzero(M[k]).tolist():
                r |= 1 << j
            rows.append(r)
        rows.append((1 << 1) | (1 << 10) | c)  # v_0 + v_9 + c (columns 1, 10, 0)
        rej = None
    else:
        raise ValueError(arm)
    return rows, info, rej


def run_arm(arm, seed, ctx, log_cb=None):
    """-> (attempt records, kept systems, exhausted list)."""
    g = np.random.Generator(np.random.PCG64(seed))
    kept_hashes = set()
    attempts, kept, exhausted = [], [], []
    from common import DEV_SLOTS
    nslots = DEV_SLOTS or len(ctx.xr144)
    for slot in range(nslots):
        need_u = need_s = True
        for a in range(MAX_ATTEMPTS):
            rows, info, rej = draw_once(arm, g, ctx, slot)
            Eh = rows_to_hex(rows)
            h = e_sha256(Eh)
            if rej is None and h in kept_hashes:
                rej = "duplicate"
            rec = {"slot": slot, "attempt": a, "E_sha256": h}
            rec.update(info)
            if rej:
                rec.update(s=None, outcome="rejected:" + rej)
                attempts.append(rec)
                continue
            s, sols = satcount.count_solutions(rows)
            rec["s"] = s
            if s == 0 and need_u:
                need_u = False
                rec["outcome"] = "kept_unsat"
                kept_hashes.add(h)
                kept.append(dict(slot=slot, role="unsat", attempt=a, rows=rows, E_hex=Eh,
                                 E_sha256=h, s=0, solutions=[], info=info))
            elif s >= 1 and need_s:
                need_s = False
                rec["outcome"] = "kept_sat"
                kept_hashes.add(h)
                kept.append(dict(slot=slot, role="sat", attempt=a, rows=rows, E_hex=Eh,
                                 E_sha256=h, s=s, solutions=sols, info=info))
            else:
                rec["outcome"] = "discarded"
            attempts.append(rec)
            if not need_u and not need_s:
                break
        if need_u:
            exhausted.append({"slot": slot, "role": "unsat"})
        if need_s:
            exhausted.append({"slot": slot, "role": "sat"})
        if log_cb and slot % 36 == 35:
            log_cb(f"{arm}: slot {slot + 1}/144, attempts so far {len(attempts)}")
    return attempts, kept, exhausted
