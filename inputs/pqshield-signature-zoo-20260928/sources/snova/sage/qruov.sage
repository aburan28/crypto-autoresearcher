# SPDX-License-Identifier: CC0-1.0
#
# QR-UOV implementation in SageMath
#
# 2025, Jan Adriaan Leegwater

import hashlib
import traceback

try:
    import nistrng
except:
    print('Error importing nistrng')
    print('Try: export PYTHONPATH=`pwd`')
    quit()

################################################################

# QR-UOV params
# qruov1q127L3v156m54refa

q = 127
v = 156
m = 54
l = 3

# Parameter to relate asymmetric pubmat to a symmetric pubmat
# Needed to recreate the official KATs
mult_fact = 2

# Parameter sets for testing

if False:
    q = 127
    v = 51
    m = 18
    l = 3
    mult_fact = 1
elif False:
    q = 31
    v = 60
    m = 20
    l = 2
    mult_fact = 1
elif False:
    q = 16
    v = 60
    m = 20
    l = 2
    # Must set mult_fact = 1 when the field order is even
    mult_fact = 1


# Create extension Galois Field with defined polynomial

GF_base = GF(q)
GF_base_poly = GF_base['x']
x = GF_base_poly.gen()

if q == 127 and l == 3:
    GF_q = GF_base_poly.extension(x**3 - x - 1, names='z')
elif q == 16 and l == 2:
    y = GF_base.gen()
    GF_q = GF_base_poly.extension(x**2 - y * x - 1, names='z')
else:
    GF_q = GF(q**l)

z = GF_q.gen()


# Derived

L = l
V = v // L
M = m // L

m1 = m
n = v + m
N = n // L

npub = m * (M * (M + 1)) // 2

# Constants from QR-UOV specification

n1 = L * V * (V + 1) // 2
n2 = L * V * M
n3 = L * V
n4 = L * M

QRUOV_tau1 = 4267  # n1 = L*V*(V+1)/2 : 4134
QRUOV_tau2 = 2916  # n2 = L*V*M : 2808
QRUOV_tau3 = 192  # n3 = L*V = v : 156
QRUOV_tau4 = 82  # n4 = L*M = m : 54

# Pack and unpack

PACK_GF = 8
PACK_BYTES = 7


def BYTES_GF(x):
    return (PACK_BYTES * (x) + PACK_GF - 1) // PACK_GF


################################################################


def rej_samp(data, n1, baseval=False):
    # QR-UOV compliant rejection sampling
    aux_idx = n1
    res = []
    idx = 0
    while len(res) < n1:
        if q == 16:
            res.append(data[idx] % 16)
            res.append(data[idx] // 16)
        else:
            v = data[idx] & q
            if v != q:
                res.append(v)
            else:
                while data[aux_idx] & q == q:
                    aux_idx += 1
                res.append(data[aux_idx] & q)
                aux_idx += 1
        idx += 1

    if baseval:
        return res

    # Convert to GF_q elements
    gfres = vector(GF_q, n1 // L)
    for ni in range(n1 // L):
        for nk in range(L):
            gfres[ni] += z**nk * res[ni * L + nk]
    return gfres


def compress_gf(data):
    # Convert elements of GF_base to bytes
    if q == 16:
        return bytes([d[0].to_integer() for d in data])
    res = []
    idx = 0
    while idx < len(data):
        sum = 0
        for i in range(min(PACK_GF, len(data) - idx)):
            sum += int(data[idx + i]) * int((q + 1)**i)
        idx += PACK_GF
        for i in range(PACK_BYTES):
            res.append(int(sum) % 256)
            sum = sum // 256
    return bytes(res[:BYTES_GF(len(data))])


def expand_gf(data, num):
    # Convert bytes to elements of GF_q
    if q == 16:
        res = [GF_base.from_integer(d) for d in data]
    else:
        res = []
        idx = 0
        while idx < len(data):
            sum = 0
            for i in range(min(PACK_BYTES, len(data) - idx)):
                sum += int(data[idx + i]) * int(256**i)
            idx += PACK_BYTES
            for i in range(PACK_GF):
                res.append(int(sum) & q)
                sum = sum // (q + 1)

    # Convert to GF_q elements
    gfres = vector(GF_q, num)
    for ni in range(num):
        for nk in range(L):
            gfres[ni] += z**nk * res[ni * L + nk]

    return gfres


def expand_T12(sk_seed):
    skx_bytes = nistrng.aesctr(sk_seed, QRUOV_tau2)
    r2 = rej_samp(skx_bytes, n2)

    T12 = matrix(GF_q, V, M)
    idx = 0
    for ni in range(V):
        for nj in range(M):
            T12[ni, nj] = -r2[idx]
            idx += 1

    return T12


def expand_public(pk_seed):
    P11m = []
    P12m = []
    P21m = []
    for mi in range(m):
        pkx_bytes = nistrng.aesctr(pk_seed, QRUOV_tau1, iv=2 * mi)
        r1 = rej_samp(pkx_bytes, n1)

        P11 = matrix(GF_q, V, V)
        idx = 0
        for ni in range(V):
            P11[ni, ni] = r1[idx]
            idx += 1
            for nj in range(ni + 1, V):
                P11[ni, nj] = mult_fact * r1[idx]
                idx += 1

        pkx_bytes = nistrng.aesctr(pk_seed, QRUOV_tau2, iv=2 * mi + 1)
        r2 = rej_samp(pkx_bytes, n2)

        P12 = matrix(GF_q, V, M)
        P21 = matrix(GF_q, M, V)
        idx = 0
        for ni in range(V):
            for nj in range(M):
                P21[nj, ni] = mult_fact * r2[idx]
                idx += 1

        P11m.append(P11)
        P12m.append(P12)
        P21m.append(P21)

    return P11m, P12m, P21m


def compress_p22(pub22):
    # Pack the generated public key as bytes
    pk = bytearray()
    res = []
    for mi in range(m):
        for ni in range(M):
            res += pub22[mi][ni, ni].list()
            for nj in range(ni + 1, M):
                res += ((pub22[mi][ni, nj] + pub22[mi][nj, ni]) / mult_fact).list()
    pk += compress_gf(res)
    return pk


def expand_p22(p22bytes):
    # Expand public key
    data = expand_gf(p22bytes, npub)
    P22 = []
    idx = 0
    for mi in range(m):
        pub22 = matrix(GF_q, M, M)
        for ni in range(M):
            pub22[ni, ni] = data[idx]
            idx += 1
            for nj in range(ni + 1, M):
                pub22[ni, nj] = mult_fact * data[idx]
                idx += 1
        P22.append(pub22)
    return P22


def hash_combined(msg, pk_seed, salt):
    # Get message hash in $\mathbb{F}_{q}$
    mu = hashlib.shake_256(pk_seed + msg).digest(64)
    dgst = hashlib.shake_256(mu + salt).digest(QRUOV_tau4)
    msg_hash = rej_samp(dgst, m, baseval=True)

    return msg_hash


################################################################

def QR_proj(x):
    return x[0]

# API functions


def genkeys(seed):
    # Generate Public key
    sk_seed = seed[:16]
    T12 = expand_T12(sk_seed)

    pk_seed = seed[16:]
    P11, P12, P21 = expand_public(pk_seed)

    P22 = [-(T12.transpose() * (P11[mi] * T12 + P12[mi]) + P21[mi] * T12) for mi in range(m1)]

    return seed, pk_seed + compress_p22(P22)


def sign(sk, msg, seeds):
    '''
    Sign message

    In an alternative but equivalent formulation of QR-UOV, the verify compares a hash
    to a projected MQ value, projected from GF_q to GF_base by QR_proj

    To sign, a signature in GF_q is to be found. This signature in GF_q can be written in
    components of GF_base in terms of its coefficients s_{i,k}
    $signature_i = sum_{k=0}^{l-1} s_{i,k} z^k$

    The coefficients of the A matrix that solves $y = A cdot x$
    for some vinegar $v$ are then given by $QR_proj(F_{21} cdot v z^k)$
    The entries of y, A and x are in GF_base. After solving, $x$ has the coefficients s_{i,k}.
    '''
    sk_seed = sk[:16]
    pk_seed = sk[16:]
    seed_y, seed_r = seeds

    P11, P12, P21 = expand_public(pk_seed)

    # Expand private key
    T12 = expand_T12(sk_seed)
    F12 = []
    F21 = []
    for mi in range(m1):
        F12.append(P11[mi] * T12 + P12[mi])
        F21.append(T12.transpose() * P11[mi] + P21[mi])

    # Sample vinegar vector
    vinegar_bytes = nistrng.aesctr(seed_y, QRUOV_tau3)
    vinegar = vector(GF_q, rej_samp(vinegar_bytes, v))

    # Establish F_vv, evaluate central map for vinegar
    F_vv = [QR_proj(vinegar * P11[mi] * vinegar) for mi in range(m1)]

    # Establish A matrix
    A = matrix(GF_q, m, m)
    for mi in range(m1):
        vinegar_F21 = F21[mi] * vinegar + vinegar * F12[mi]
        # *QR-UOV: project from GF_q to GF_base
        for ni in range(M):
            for nk in range(L):
                val = vinegar_F21[ni] * z**nk
                A[mi, ni * L + nk] = QR_proj(val)

    num_sign = 0
    while True:
        # QR-UOV uses the salt for rejection sampling of the solution
        num_sign += 1
        if num_sign > 255:
            raise Exception('Signing failed')
        salt = nistrng.aesctr(seed_r, 16 * num_sign)[-16:]

        # Get message hash and combine with F_vv
        msg_hash = hash_combined(msg, pk_seed, salt)
        b_vec = vector(GF_q, [msg_hash[mi] - F_vv[mi] for mi in range(m1)])

        try:
            solution = A.solve_right(b_vec)
            break
        except ValueError:
            print('no solution', num_sign)
            pass

    # Create signature
    oil = vector(GF_q, M)
    for ni in range(M):
        for nk in range(L):
            # QR-UOV: inverse of *QR-UOV: project from GF_q to GF_base
            oil[ni] += z**nk * solution[ni * L + nk]
    vinegar += T12 * oil

    # Output
    res = []
    for i in range(V):
        res += vinegar[i].list()
    for i in range(M):
        res += oil[i].list()

    return salt + compress_gf(res)


def verify(pk, sig_bytes, msg):
    # Verify signature of message

    # Get expected hash
    pk_seed = pk[:16]
    salt = sig_bytes[:16]
    msg_hash = hash_combined(msg, pk_seed, salt)

    # Decode sig
    sig = expand_gf(sig_bytes[16:], N)

    # Expand pubkey
    P11, P12, P21 = expand_public(pk_seed)
    P22 = expand_p22(pk[16:])
    P = [matrix.block([[P11[mi], P12[mi]], [P21[mi], P22[mi]]]) for mi in range(m1)]

    # Evaluate central map
    p_sig = [sig * P[mi] * sig for mi in range(m1)]

    # QR-UOV: Project from GF_q to GF_base
    sig_hash = [QR_proj(p_sig[mi]) for mi in range(m)]

    # Check against expected hash
    if msg_hash != sig_hash:
        raise Exception('Verify failed')


################################################################

# Generate KATs
entropy_input = bytearray(48)
for i in range(48):
    entropy_input[i] = i
drbg = nistrng.rng(entropy_input)

print('# QR-UOV', q, l, v, m, 'AES')
print()

for count in range(1):
    seed = drbg.random_bytes(48)
    srbdg = nistrng.rng(seed)

    keygen_seed = srbdg.random_bytes(16)
    keygen_seed = keygen_seed + srbdg.random_bytes(16)
    seed_y = srbdg.random_bytes(16)
    seed_r = srbdg.random_bytes(16)
    salt = seed_y, seed_r,

    mlen = 33 * (count + 1)
    msg = drbg.random_bytes(mlen)

    try:
        # Keygen
        sk, pk = genkeys(keygen_seed)

        print('count =', count)
        print('seed =', seed.hex().upper())
        print('mlen =', mlen)
        print('msg =', msg.hex().upper())
        print('pk =', pk.hex().upper())
        print('sk =', sk.hex().upper())

        # Sign
        sig = sign(sk, msg, salt)
        sm = sig + msg

        print('smlen =', len(sm))
        print('sm =', sm.hex().upper())
        print()

        # Verify
        verify(pk, sig, msg)

    except Exception as exc:
        traceback.print_exc()
        quit()
