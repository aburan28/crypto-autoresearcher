#!/usr/bin/env python3
# cal_crosscheck.py -- part of TASK-20260901-f5d3a4 RUN 4 (calibration).
# Exact Python replication of ONE affarm046 arm thread stream (1 thread,
# arm_id 1) using the campaign formulas: splitmix64 RNG, key derivation
# kst = seed ^ 0xA5A5..., per-thread seed seed ^ armid*0x1234567891 ^
# (t+1)*0x9E3779B97F4A7C15, verbatim worker semantics. Compares counters
# against the C receipt. Used to tie the fresh C worker to the validated
# Python trial semantics (gate0/bridge) before the frozen 2^30 arm.
import json, sys

MASK64 = (1 << 64) - 1

def sm64(state):
    state[0] = (state[0] + 0x9E3779B97F4A7C15) & MASK64
    z = state[0]
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
    return z ^ (z >> 31)

def xt(a): return ((a << 1) ^ ((a >> 7) * 0x1b)) & 0xFF
XT2 = [xt(i) for i in range(256)]
XT4 = [xt(XT2[i]) for i in range(256)]
XT8 = [xt(XT4[i]) for i in range(256)]

def sub_shift(s):
    return [s[4 * ((c + r) & 3) + r] for c in range(4) for r in range(4)]

def inv_sub_shift(s):
    return [s[4 * ((c - r + 4) & 3) + r] for c in range(4) for r in range(4)]

def mix_columns(s):
    out = list(s)
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        t = a0 ^ a1 ^ a2 ^ a3
        out[4*c]   = a0 ^ t ^ XT2[a0 ^ a1]
        out[4*c+1] = a1 ^ t ^ XT2[a1 ^ a2]
        out[4*c+2] = a2 ^ t ^ XT2[a2 ^ a3]
        out[4*c+3] = a3 ^ t ^ XT2[a3 ^ a0]
    return out

def inv_mix_columns(s):
    out = list(s)
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        w = [XT8[x] for x in (a0, a1, a2, a3)]
        v = [XT4[x] for x in (a0, a1, a2, a3)]
        u = [XT2[x] for x in (a0, a1, a2, a3)]
        out[4*c]   = w[0]^v[0]^u[0] ^ w[1]^u[1]^a1 ^ w[2]^v[2]^a2 ^ w[3]^a3
        out[4*c+1] = w[0]^a0 ^ w[1]^v[1]^u[1] ^ w[2]^u[2]^a2 ^ w[3]^v[3]^a3
        out[4*c+2] = w[0]^v[0]^a0 ^ w[1]^a1 ^ w[2]^v[2]^u[2] ^ w[3]^u[3]^a3
        out[4*c+3] = w[0]^u[0]^a0 ^ w[1]^v[1]^a1 ^ w[2]^a2 ^ w[3]^v[3]^u[3]
    return out

def key_expand_identity(key):
    rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]
    rk = [list(key)]
    for i in range(1, 11):
        t = list(rk[i-1][12:16])
        tmp = t[0]; t[0] = t[1]; t[1] = t[2]; t[2] = t[3]; t[3] = tmp
        t[0] ^= rcon[i-1]
        row = list(rk[i-1])
        for w in range(4):
            for b in range(4):
                row[4*w+b] = rk[i-1][4*w+b] ^ (t[b] if w == 0 else row[4*(w-1)+b])
        rk.append(row)
    return rk

def enc_rk(pt, rk, rounds):
    st = [pt[i] ^ rk[0][i] for i in range(16)]
    for i in range(1, rounds):
        st = mix_columns(sub_shift(st))
        st = [st[k] ^ rk[i][k] for k in range(16)]
    st = sub_shift(st)
    return [st[k] ^ rk[rounds][k] for k in range(16)]

def dec_rk(ct, rk, rounds):
    st = [ct[i] ^ rk[rounds][i] for i in range(16)]
    st = inv_sub_shift(st)
    for i in range(rounds - 1, 0, -1):
        st = [st[k] ^ rk[i][k] for k in range(16)]
        st = inv_sub_shift(inv_mix_columns(st))
    return [st[k] ^ rk[0][k] for k in range(16)]

PW = [[4 * ((j + row) % 4) + row for row in range(4)] for j in range(4)]
CW = [[4 * ((j - row) % 4) + row for row in range(4)] for j in range(4)]

def replicate(seed, armid, rounds, amask, smask, ntrials):
    kst = [seed ^ 0xA5A5A5A5A5A5A5A5]
    key = []
    for _ in range(2):
        z = sm64(kst)
        key += [(z >> (8 * i)) & 0xFF for i in range(8)]
    rk = key_expand_identity(key)
    init_seed = (seed ^ ((armid * 0x1234567891) & MASK64) ^ 0x9E3779B97F4A7C15) & MASK64
    st = [init_seed]
    zhist = [0]*17; whist = [0]*5; wword = [0]*4
    trivial = 0; wge1 = 0
    for _ in range(ntrials):
        a = sm64(st); b = sm64(st)
        p0 = [(a >> (8*i)) & 0xFF for i in range(8)] + [(b >> (8*i)) & 0xFF for i in range(8)]
        p1 = list(p0)
        while True:
            ok = True
            for j in range(4):
                if amask & (1 << j):
                    rnd = sm64(st); nz = False
                    for row in range(4):
                        nb = (rnd >> (8 * row)) & 0xFF
                        p1[PW[j][row]] = nb
                        if nb != p0[PW[j][row]]: nz = True
                    if not nz: ok = False
            if ok: break
        c0 = enc_rk(p0, rk, rounds); c1 = enc_rk(p1, rk, rounds)
        triv = True
        for j in range(4):
            if smask & (1 << j):
                for row in range(4):
                    i = CW[j][row]
                    x, y = c0[i], c1[i]
                    if x != y: triv = False
                    c0[i], c1[i] = y, x
        q0 = dec_rk(c0, rk, rounds); q1 = dec_rk(c1, rk, rounds)
        Z = sum(1 for i in range(16) if q0[i] == q1[i])
        W = 0
        for j in range(4):
            z = all(q0[PW[j][row]] == q1[PW[j][row]] for row in range(4))
            if z:
                W += 1
                if not triv: wword[j] += 1
        if triv:
            trivial += 1
            continue
        zhist[Z] += 1; whist[W] += 1
        if W >= 1: wge1 += 1
    return {"key_hex": "".join("%02x" % k for k in key),
            "thread_seed_initial": init_seed,
            "trivial_swaps_excluded": trivial,
            "nontrivial_trials": ntrials - trivial,
            "W_ge1_nontrivial": wge1,
            "W_ge1_by_word": wword,
            "whist": whist, "zhist": zhist}

if __name__ == "__main__":
    seed = int(sys.argv[1]); armid = int(sys.argv[2]); rounds = int(sys.argv[3])
    amask = int(sys.argv[4]); smask = int(sys.argv[5]); ntrials = int(sys.argv[6])
    print(json.dumps(replicate(seed, armid, rounds, amask, smask, ntrials), indent=1))
