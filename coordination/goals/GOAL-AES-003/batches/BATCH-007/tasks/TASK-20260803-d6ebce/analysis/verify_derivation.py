#!/usr/bin/env python3
"""TASK-20260803-d6ebce -- INDEPENDENT ANALYSIS CODE (not the frozen instrument).

Purpose: check that the derivation in PREREGISTRATION.md actually FOLLOWS, step
by step, rather than merely that its final prediction matches. This is a
byte-oriented reimplementation of the same cipher convention (the frozen
instrument is T-table based), written for this task.

It checks, on random keys / S-boxes / plaintexts:

  KAT   FIPS-197 C.1 known-answer test of THIS implementation.
  L4    exchange invariance of the pair difference at the swap point.
  STEP1 swapping ciphertext word j == swapping diagonal PW[j] of z_{r-2},
        verified as full-state equality, for r = 2,3,4,5.
  STEP4 Delta(z_{r-2}') == Delta(z_{r-2}) holds; and the r=5 break is located
        by testing whether Delta(y_2') == Delta(y_2), which the derivation says
        holds at r=4 and fails at r=5.
  PROP1 W = 4-|A| and preserved(j) <=> j not in A, at r = 1,2,3,4; and the same
        test at r=5 to show it fails there.

Nothing here is used as a headline measurement; the headline numbers come from
the frozen instrument. This is a check on the ARGUMENT.
"""
import random
import sys

# ---------------- GF(2^8) ----------------
def xt(a):
    a <<= 1
    return (a ^ 0x1b) & 0xff if a & 0x100 else a

def gmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = xt(a)
        b >>= 1
    return r

def aes_sbox():
    inv = [0] * 256
    for a in range(1, 256):
        for b in range(1, 256):
            if gmul(a, b) == 1:
                inv[a] = b
                break
    s = []
    for i in range(256):
        x, y = inv[i], 0
        for bit in range(8):
            v = ((x >> bit) & 1) ^ ((x >> ((bit + 4) & 7)) & 1) ^ \
                ((x >> ((bit + 5) & 7)) & 1) ^ ((x >> ((bit + 6) & 7)) & 1) ^ \
                ((x >> ((bit + 7) & 7)) & 1) ^ ((0x63 >> bit) & 1)
            y |= v << bit
        s.append(y)
    return s

def rand_sbox(rng):
    s = list(range(256))
    rng.shuffle(s)
    return s

def inv_sbox(s):
    t = [0] * 256
    for i, v in enumerate(s):
        t[v] = i
    return t

# ---------------- state layout: index = 4*col + row ----------------
def SB(st, s):
    return [s[b] for b in st]

def SR(st):
    o = [0] * 16
    for c in range(4):
        for row in range(4):
            o[4 * ((c - row) % 4) + row] = st[4 * c + row]
    return o

def ISR(st):
    o = [0] * 16
    for c in range(4):
        for row in range(4):
            o[4 * ((c + row) % 4) + row] = st[4 * c + row]
    return o

def MC(st):
    o = [0] * 16
    for c in range(4):
        a = st[4 * c:4 * c + 4]
        o[4 * c + 0] = gmul(a[0], 2) ^ gmul(a[1], 3) ^ a[2] ^ a[3]
        o[4 * c + 1] = a[0] ^ gmul(a[1], 2) ^ gmul(a[2], 3) ^ a[3]
        o[4 * c + 2] = a[0] ^ a[1] ^ gmul(a[2], 2) ^ gmul(a[3], 3)
        o[4 * c + 3] = gmul(a[0], 3) ^ a[1] ^ a[2] ^ gmul(a[3], 2)
    return o

def IMC(st):
    o = [0] * 16
    for c in range(4):
        a = st[4 * c:4 * c + 4]
        o[4 * c + 0] = gmul(a[0], 14) ^ gmul(a[1], 11) ^ gmul(a[2], 13) ^ gmul(a[3], 9)
        o[4 * c + 1] = gmul(a[0], 9) ^ gmul(a[1], 14) ^ gmul(a[2], 11) ^ gmul(a[3], 13)
        o[4 * c + 2] = gmul(a[0], 13) ^ gmul(a[1], 9) ^ gmul(a[2], 14) ^ gmul(a[3], 11)
        o[4 * c + 3] = gmul(a[0], 11) ^ gmul(a[1], 13) ^ gmul(a[2], 9) ^ gmul(a[3], 14)
    return o

def ARK(st, k):
    return [a ^ b for a, b in zip(st, k)]

RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]

def key_expand(key, s):
    rk = [list(key)]
    for i in range(1, 11):
        t = rk[i - 1][12:16]
        t = [s[t[1]], s[t[2]], s[t[3]], s[t[0]]]
        t[0] ^= RCON[i - 1]
        nk = [0] * 16
        for w in range(4):
            for b in range(4):
                nk[4 * w + b] = rk[i - 1][4 * w + b] ^ (t[b] if w == 0 else nk[4 * (w - 1) + b])
        rk.append(nk)
    return rk

PW = [[4 * ((j + row) % 4) + row for row in range(4)] for j in range(4)]
CW = [[4 * ((j - row) % 4) + row for row in range(4)] for j in range(4)]

def enc_trace(p, rk, s, r):
    """Return (ciphertext, trace) where trace['z'][i] is the state AFTER the MC
    of round i (i = 1..r-1), matching the derivation's z_i."""
    tr = {'z': {}, 'y': {}}
    a = ARK(p, rk[0])
    for i in range(1, r):
        y = SR(SB(a, s))
        tr['y'][i] = y
        z = MC(y)
        tr['z'][i] = z
        a = ARK(z, rk[i])
    y = SR(SB(a, s))
    tr['y'][r] = y
    return ARK(y, rk[r]), tr

def dec(c, rk, s, r):
    isb = inv_sbox(s)
    a = ARK(c, rk[r])
    a = [isb[b] for b in ISR(a)]
    for i in range(r - 1, 0, -1):
        a = ARK(a, rk[i])
        a = IMC(a)
        a = [isb[b] for b in ISR(a)]
    return ARK(a, rk[0])

def xor(a, b):
    return [x ^ y for x, y in zip(a, b)]

def swap_positions(a, b, pos):
    a, b = list(a), list(b)
    for i in pos:
        a[i], b[i] = b[i], a[i]
    return a, b

def cw_positions(smask):
    return [i for j in range(4) for i in CW[j] if smask >> j & 1]

def pw_positions(mask):
    return [i for j in range(4) for i in PW[j] if mask >> j & 1]

def make_pair(rng, amask):
    p0 = [rng.randrange(256) for _ in range(16)]
    while True:
        p1 = list(p0)
        ok = True
        for j in range(4):
            if amask >> j & 1:
                nz = False
                for i in PW[j]:
                    nb = rng.randrange(256)
                    p1[i] = nb
                    if nb != p0[i]:
                        nz = True
                if not nz:
                    ok = False
        if ok:
            return p0, p1

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20260803
    rng = random.Random(seed)
    S_AES = aes_sbox()
    out = {}

    # ---- KAT of THIS implementation ----
    k = list(range(16))
    pt = [0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
          0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff]
    exp = bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")
    rk = key_expand(k, S_AES)
    ct, _ = enc_trace(pt, rk, S_AES, 10)
    out['kat_fips197_c1_encrypt'] = (bytes(ct) == exp)
    out['kat_fips197_c1_ciphertext'] = bytes(ct).hex()
    out['kat_fips197_c1_decrypt'] = (dec(list(exp), rk, S_AES, 10) == pt)
    out['kat_roundtrip_r1_to_r6'] = all(
        dec(enc_trace(pt, rk, S_AES, r)[0], rk, S_AES, r) == pt for r in range(1, 7))

    # ---- per-round checks ----
    per_round = {}
    NTRIAL = 60
    for r in range(1, 6):
        rec = {'trials': NTRIAL, 'step1_pushback_ok': 0, 'step1_applicable': 0,
               'L4_diff_invariant_ok': 0,
               'delta_y2_preserved_ok': 0, 'delta_y2_applicable': 0,
               'prop1_ok': 0, 'prop1_violations': [], 'W_values': {}}
        for _ in range(NTRIAL):
            sbx = S_AES if rng.random() < 0.5 else rand_sbox(rng)
            key = [rng.randrange(256) for _ in range(16)]
            rk = key_expand(key, sbx)
            amask = rng.choice([1, 2, 4, 8, 3, 5, 6, 9, 10, 12, 7, 11, 13, 14, 15])
            smask = rng.choice(list(range(1, 15)))
            A = [j for j in range(4) if amask >> j & 1]
            p0, p1 = make_pair(rng, amask)
            c0, tr0 = enc_trace(p0, rk, sbx, r)
            c1, tr1 = enc_trace(p1, rk, sbx, r)
            sp = cw_positions(smask)
            trivial = all(c0[i] == c1[i] for i in sp)
            c0s, c1s = swap_positions(c0, c1, sp)

            # L4: difference invariant at the swap point
            if xor(c0s, c1s) == xor(c0, c1):
                rec['L4_diff_invariant_ok'] += 1

            # STEP1: ciphertext-word swap == diagonal swap of z_{r-2}
            if r >= 3:
                rec['step1_applicable'] += 1
                z0, z1 = tr0['z'][r - 2], tr1['z'][r - 2]
                za, zb = swap_positions(z0, z1, pw_positions(smask))
                # re-encrypt from z_{r-2} forward and compare to the swapped ct
                def fwd(z):
                    a = ARK(z, rk[r - 2])
                    for i in range(r - 1, r):
                        pass
                    for i in range(r - 2 + 1, r):
                        y = SR(SB(a, sbx))
                        a = ARK(MC(y), rk[i])
                    return ARK(SR(SB(a, sbx)), rk[r])
                if fwd(za) == c0s and fwd(zb) == c1s:
                    rec['step1_pushback_ok'] += 1
            elif r == 2:
                rec['step1_applicable'] += 1
                # swap point is the plaintext diagonal itself
                pa, pb = swap_positions(p0, p1, pw_positions(smask))
                if enc_trace(pa, rk, sbx, r)[0] == c0s and \
                   enc_trace(pb, rk, sbx, r)[0] == c1s:
                    rec['step1_pushback_ok'] += 1

            q0 = dec(c0s, rk, sbx, r)
            q1 = dec(c1s, rk, sbx, r)

            # STEP4 probe: does Delta(y_2) survive the swap?  Derivation says
            # yes at r<=4 (only linear MC^-1 crossed) and no at r=5.
            if r >= 2:
                rec['delta_y2_applicable'] += 1
                _, tq0 = enc_trace(q0, rk, sbx, r)
                _, tq1 = enc_trace(q1, rk, sbx, r)
                if xor(tq0['y'][2], tq1['y'][2]) == xor(tr0['y'][2], tr1['y'][2]):
                    rec['delta_y2_preserved_ok'] += 1

            if trivial:
                continue
            d = xor(q0, q1)
            W = sum(1 for j in range(4) if all(d[i] == 0 for i in PW[j]))
            pres = [j for j in range(4) if all(d[i] == 0 for i in PW[j])]
            rec['W_values'][str(W)] = rec['W_values'].get(str(W), 0) + 1
            if pres == [j for j in range(4) if j not in A]:
                rec['prop1_ok'] += 1
            elif len(rec['prop1_violations']) < 3:
                rec['prop1_violations'].append(
                    {'r': r, 'amask': amask, 'smask': smask,
                     'preserved': pres, 'expected': [j for j in range(4) if j not in A]})
        per_round[str(r)] = rec
    out['per_round'] = per_round
    import json
    print(json.dumps(out, indent=1))

if __name__ == '__main__':
    main()
