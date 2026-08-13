#!/usr/bin/env python3
"""verify_sbox.py — independent Python cross-check of the three S-box tables
used by probe_sbox.c (TASK-20260804-f5e58b RANK 3).

Checks:
  1. AES S-box: recomputed from GF(2^8) inverse + FIPS-197 affine map,
     compared byte-for-byte with the C build_sbox() table (pin_aes.json)
     and with the canonical FIPS-197 first 16 bytes
     637c777bf26b6fc53001672bfed7ab76 (BATCH-003 ref.json sbox_sha_check).
  2. Random S-box #1 (seed 424242201) and #2 (seed 424242202): recomputed
     with an independent Python splitmix64 + Fisher-Yates, compared
     byte-for-byte with the C pinsbox outputs.
  3. Bijectivity of all three tables (inverse maps back, both directions).
  4. sha256 of each table recorded for RESULTS.json.
"""
import hashlib, json

def sm64_stateful(state):
    state[0] = (state[0] + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = state[0]
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return z ^ (z >> 31)

def fisher_yates(seed):
    p = list(range(256))
    state = [seed]
    for i in range(255, 0, -1):
        r = sm64_stateful(state)
        j = r % (i + 1)
        p[i], p[j] = p[j], p[i]
    return p

def gf_mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
        b >>= 1
    return r

def aes_sbox():
    inv = [0]*256
    for a in range(1, 256):
        for b in range(1, 256):
            if gf_mul(a, b) == 1:
                inv[a] = b
                break
    sbox = [0]*256
    for i in range(256):
        x = inv[i]
        y = 0
        for bit in range(8):
            v = ((x >> bit) & 1) ^ ((x >> ((bit+4) & 7)) & 1) ^ ((x >> ((bit+5) & 7)) & 1) \
                ^ ((x >> ((bit+6) & 7)) & 1) ^ ((x >> ((bit+7) & 7)) & 1) ^ ((0x63 >> bit) & 1)
            y |= v << bit
        sbox[i] = y
    return sbox

def hex_to_table(h):
    return [int(h[i:i+2], 16) for i in range(0, len(h), 2)]

def check_bijective(t):
    inv = [0]*256
    for i, v in enumerate(t):
        inv[v] = i
    for i in range(256):
        if inv[t[i]] != i or t[inv[i]] != i:
            return False
    return True

def main():
    aes_c = hex_to_table(json.load(open('pin_aes.json'))['sbox_table_hex'])
    s1_c = hex_to_table(json.load(open('pinsbox1.json'))['sbox_table_hex'])
    s2_c = hex_to_table(json.load(open('pinsbox2.json'))['sbox_table_hex'])

    aes_py = aes_sbox()
    s1_py = fisher_yates(424242201)
    s2_py = fisher_yates(424242202)

    canonical_prefix = '637c777bf26b6fc53001672bfed7ab76'
    results = {}
    results['aes_table_matches_python_recompute'] = aes_c == aes_py
    results['aes_table_first16_matches_fips197'] = ''.join('%02x' % b for b in aes_c[:16]) == canonical_prefix
    results['sbox1_matches_python_recompute'] = s1_c == s1_py
    results['sbox2_matches_python_recompute'] = s2_c == s2_py
    results['aes_bijective'] = check_bijective(aes_c)
    results['sbox1_bijective'] = check_bijective(s1_c)
    results['sbox2_bijective'] = check_bijective(s2_c)
    results['aes_sha256'] = hashlib.sha256(bytes(aes_c)).hexdigest()
    results['sbox1_sha256'] = hashlib.sha256(bytes(s1_c)).hexdigest()
    results['sbox2_sha256'] = hashlib.sha256(bytes(s2_c)).hexdigest()
    results['sbox1_seed'] = 424242201
    results['sbox2_seed'] = 424242202
    results['all_pass'] = all([
        results['aes_table_matches_python_recompute'],
        results['aes_table_first16_matches_fips197'],
        results['sbox1_matches_python_recompute'],
        results['sbox2_matches_python_recompute'],
        results['aes_bijective'], results['sbox1_bijective'], results['sbox2_bijective'],
    ])
    for k, v in results.items():
        print(f'{k}: {v}')
    json.dump(results, open('sbox_verify.json', 'w'), indent=1)
    return 0 if results['all_pass'] else 1

if __name__ == '__main__':
    import sys
    sys.exit(main())