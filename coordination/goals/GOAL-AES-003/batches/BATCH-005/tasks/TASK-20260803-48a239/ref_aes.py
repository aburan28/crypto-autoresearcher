#!/usr/bin/env python3
"""TASK-20260803-367b1b segment 2 -- INDEPENDENT reference implementation.

Written from the FIPS-197 description in plain Python, byte by byte: no
T-tables, no equivalent-inverse-cipher, no shared code path and no shared
constants with src/yoyo_sbox.c. Its only job is to be an ABSOLUTE per-round
anchor for the random-S-box arms, which the C probe's own pin cannot supply:
that pin applies the FIPS-197 C.1 known-answer vector at r=10 and only for the
real AES S-box, and its 5120 round-trips are invariant under any conjugation
that enc_r and dec_r happen to share.

This file computes enc_r for r = 1..10 for a given S-box and compares against
the C binary's `vec` dump. A conjugation error inside the C probe cannot
survive this comparison, because this implementation shares none of it.

Round convention being checked (the same one the probe measures):
  E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0
State layout: byte index 4*col + row (column-major), as in the probe.
"""
import json
import subprocess
import sys
import os

D = os.path.dirname(os.path.abspath(__file__))


def xtime(a):
    a <<= 1
    if a & 0x100:
        a ^= 0x11B
    return a & 0xFF


def gmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = xtime(a)
        b >>= 1
    return r


def aes_sbox():
    """AES S-box from scratch: multiplicative inverse in GF(2^8) then the
    FIPS-197 affine map. Computed by brute-force inversion, independently of
    the C probe."""
    inv = [0] * 256
    for a in range(1, 256):
        for b in range(1, 256):
            if gmul(a, b) == 1:
                inv[a] = b
                break
    s = []
    for i in range(256):
        x = inv[i]
        y = 0
        for bit in range(8):
            v = ((x >> bit) & 1) ^ ((x >> ((bit + 4) % 8)) & 1) ^ ((x >> ((bit + 5) % 8)) & 1) \
                ^ ((x >> ((bit + 6) % 8)) & 1) ^ ((x >> ((bit + 7) % 8)) & 1) ^ ((0x63 >> bit) & 1)
            y |= v << bit
        s.append(y)
    return s


def splitmix64(state):
    """Only used to REDRAW the random S-boxes independently of the C code path,
    so that the drawn table itself is checked too."""
    while True:
        state = (state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        yield z ^ (z >> 31)


def random_sbox(seed):
    g = splitmix64(seed)
    s = list(range(256))
    for i in range(255, 0, -1):
        m = i + 1
        lim = (1 << 64) - ((1 << 64) % m)
        while True:
            r = next(g)
            if r < lim:
                break
        j = r % m
        s[i], s[j] = s[j], s[i]
    return s


def key_expand(key, sbox):
    rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
    rk = [list(key)]
    for i in range(1, 11):
        prev = rk[i - 1]
        t = list(prev[12:16])
        t = [sbox[t[1]], sbox[t[2]], sbox[t[3]], sbox[t[0]]]
        t[0] ^= rcon[i - 1]
        cur = [0] * 16
        for w in range(4):
            for b in range(4):
                cur[4 * w + b] = prev[4 * w + b] ^ (t[b] if w == 0 else cur[4 * (w - 1) + b])
        rk.append(cur)
    return rk


def sub_bytes(st, sbox):
    return [sbox[b] for b in st]


def shift_rows(st):
    """row `row` shifts LEFT by `row`: out[4*c+row] = in[4*((c+row)%4)+row]"""
    return [st[4 * ((c + row) % 4) + row] for c in range(4) for row in range(4)]


def mix_columns(st):
    out = [0] * 16
    for c in range(4):
        a = st[4 * c:4 * c + 4]
        out[4 * c + 0] = gmul(a[0], 2) ^ gmul(a[1], 3) ^ a[2] ^ a[3]
        out[4 * c + 1] = a[0] ^ gmul(a[1], 2) ^ gmul(a[2], 3) ^ a[3]
        out[4 * c + 2] = a[0] ^ a[1] ^ gmul(a[2], 2) ^ gmul(a[3], 3)
        out[4 * c + 3] = gmul(a[0], 3) ^ a[1] ^ a[2] ^ gmul(a[3], 2)
    return out


def enc_r(pt, key, sbox, r):
    rk = key_expand(key, sbox)
    st = [pt[i] ^ rk[0][i] for i in range(16)]
    for i in range(1, r):
        st = sub_bytes(st, sbox)
        st = shift_rows(st)
        st = mix_columns(st)
        st = [st[k] ^ rk[i][k] for k in range(16)]
    st = sub_bytes(st, sbox)
    st = shift_rows(st)
    st = [st[k] ^ rk[r][k] for k in range(16)]
    return st


def main():
    results = {
        "what_this_anchors": (
            "an INDEPENDENT plain-Python FIPS-197 implementation (byte-wise SubBytes/ShiftRows/"
            "MixColumns, no T-tables, no equivalent-inverse-cipher, no shared code or constants with "
            "the C probe) checked against the C probe's enc_r output for EVERY round count r=1..10, "
            "under the real AES S-box and under both random S-boxes. This is an absolute per-round "
            "anchor and is NOT invariant under a conjugation shared by enc_r and dec_r."),
        "binary_used_for_the_dump": "yoyo_sbox_v2 (src/yoyo_sbox.c plus a read-only `vec` dump mode; "
                                    "diff in src/yoyo_sbox_v2.diff), tied to the measuring binary by "
                                    "an identical-output arm comparison recorded separately",
        "arms": {},
    }
    # independent AES S-box check against FIPS-197's published first row
    sb_aes = aes_sbox()
    results["aes_sbox_rebuilt_independently_first16"] = sb_aes[:16]
    results["aes_sbox_matches_fips197_published_first_row"] = sb_aes[:16] == [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
        0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76]

    specs = [("aes", sb_aes),
             ("rand:20260803001", random_sbox(20260803001)),
             ("rand:20260803002", random_sbox(20260803002))]
    allok = True
    for spec, sbox in specs:
        out = subprocess.run([os.path.join(D, "yoyo_sbox_v2"), "vec", spec],
                             capture_output=True, text=True)
        d = json.loads(out.stdout)
        key = list(bytes.fromhex(d["key"]))
        pt = list(bytes.fromhex(d["pt"]))
        per_round = {}
        ok = True
        for r in range(1, 11):
            mine = bytes(enc_r(pt, key, sbox, r)).hex()
            theirs = d["enc_by_round"][str(r)]
            per_round[str(r)] = {"c_probe": theirs, "python_reference": mine, "match": mine == theirs}
            ok = ok and mine == theirs
        # also re-derive the random tables independently and compare
        tblmatch = None
        if spec.startswith("rand:"):
            f = os.path.join(D, "runs", "sbox_" + spec.replace(":", "_") + ".json")
            tblmatch = json.load(open(f))["sbox"] == sbox
        results["arms"][spec] = {
            "key": d["key"], "pt": d["pt"],
            "rounds_checked": "1..10",
            "all_rounds_match": ok,
            "sbox_table_independently_redrawn_and_matches": tblmatch,
            "per_round": per_round,
        }
        allok = allok and ok and (tblmatch is not False)
    results["ANCHOR_PASS"] = allok
    with open(os.path.join(D, "runs", "independent_reference_check.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("ANCHOR_PASS =", allok)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
