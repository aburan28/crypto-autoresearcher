# SPDX-License-Identifier: MIT
#
# TSUOV implementation in SageMath
#
# Copyright (c) 2025 SNOVA TEAM

import hashlib
import traceback

################################################################

# TSUOV parameters

if True:
    # TSUOV

    q = 31
    v = 60
    o = 4
    l = 1
    l_qr = 2
    r = 11

    m1 = 61
    m2 = o * l * r
    RANDOM_E = True
    SNOVA = False

elif True:
    # SNOVA_24_5_23_4

    v = 24
    o = 5
    q = 23
    l = 4
    l_qr = 1

    r = l
    m1 = o
    m2 = o * l * r
    RANDOM_E = False
    SNOVA = True

elif True:
    # RectSNOVA candidate

    v = 37
    o = 6
    q = 19
    l = 2
    l_qr = 1
    r = 6
    m1 = 17
    m2 = o * l * r
    RANDOM_E = False
    SNOVA = False

elif False:
    # QR-UOV qruov1q127L3v156m54refa params, KATs differ

    q = 127
    v = 52
    o = 18
    l = 1
    l_qr = 3
    r = l

    m1 = o * l_qr
    m2 = o * l * r
    RANDOM_E = True
    SNOVA = False

else:
    # SNOVA / TSUOV hybrid

    q = 19
    v = 30
    o = 4
    l = 2
    l_qr = 2
    r = 5

    m1 = o * l_qr * r
    m2 = o * l * r
    RANDOM_E = True
    SNOVA = False


################################################################

n_alpha = r * r + r
n = v + o

ASYMMETRIC_PUBMAT = q == 16
SIGN_DIGEST = l == r and q == 16

# Set GF

GF_q = GF(q, 'x')
x = GF_q.gen()


if q == 31 and l_qr == 2:
    GF_q_poly = GF_q['y']
    y = GF_q_poly.gen()
    GF_ext = GF_q_poly.extension(y**2 - 3 * y - 1, names='z')
else:
    GF_ext = GF(q**l_qr, 'z')
z = GF_ext.gen()


if q == 16:
    def from_int(x): return GF_q.from_integer(x)
    def to_int(x): return x.to_integer()
else:
    def from_int(x): return x
    def to_int(x): return int(x)


# Set constants

if q == 16:
    PACK_GF = 2
    PACK_BYTES = 1

elif q == 19:
    Q_A = 1
    Q_B = 3
    Q_C = 15
    PACK_GF = 15
    PACK_BYTES = 8

elif q == 23:
    Q_A = 1
    Q_B = 11
    Q_C = 22
    PACK_GF = 7
    PACK_BYTES = 4

elif q == 31:
    Q_A = 2
    Q_B = 5
    Q_C = 8
    PACK_GF = 8
    PACK_BYTES = 5

elif q == 127:
    Q_A = 1
    Q_B = 11
    Q_C = 22
    PACK_GF = 8
    PACK_BYTES = 7


if SNOVA:
    try:
        from nistrng import rng
    except:
        print('Error importing nistrng')
        print('Try: export PYTHONPATH=`pwd`')
        quit()
else:
    class rng:
        def __init__(self, seed):
            self.xof = hashlib.shake_256(seed)

        def random_bytes(self, num):
            return self.xof.digest(num)

# Derived constants


def BYTES_GF(x):
    return (PACK_BYTES * (x) + PACK_GF - 1) // PACK_GF


GF16_HASH = m2 * l_qr

if ASYMMETRIC_PUBMAT:
    NUM_GEN_PUB_GF = m1 * (v * v + 2 * v * o) * l**2 + o * n_alpha * (r * (r + l) + 2 * l)
    NUMGF_PK = m1 * o * l * (o * l)
else:
    NUM_GEN_PUB_GF = m1 * (v * (v + 1) // 2 + v * o) * l**2 + o * n_alpha * (r * (r + l) + 2 * l)
    NUMGF_PK = m1 * o * l * (o * l + 1) // 2

if q == 16:
    NUM_GEN_PUB_BYTES = NUM_GEN_PUB_GF // 2 * l_qr
else:
    NUM_GEN_PUB_BYTES = NUM_GEN_PUB_GF * l_qr


# Create the S matrix

if q == 16:
    S = matrix(GF_q, l, l, lambda i, j: from_int(abs(8 - (i + j))))
    if l == 5:
        S[4, 4] = from_int(9)
else:
    S = matrix(GF_q, l, l)
    for i in range(l):
        for j in range(i, l):
            S[i, j] = (Q_A + i + j) & Q_B
            S[j, i] = S[i, j]
    S[l - 1, l - 1] = Q_C


S_times_o = matrix.block_diagonal([S for _ in range(o)])
S_times_v = matrix.block_diagonal([S for _ in range(v)])
S_times_n = matrix.block_diagonal([S for _ in range(n)])


# Utils

def expand_gf(data, num, ext=False):
    # Convert bytes to elements of $\mathbb{F}_{q}$
    res = []
    idx = 0
    while idx < len(data):
        bsum = 0
        for i in range(min(PACK_BYTES, len(data) - idx)):
            bsum += int(data[idx + i]) * int(256**i)
        idx += PACK_BYTES
        if q == 16:
            res.append(from_int(int(bsum) % 16))
            res.append(from_int(int(bsum / 16) % 16))
            bsum = bsum // 256
        else:
            for i in range(PACK_GF):
                res.append(from_int(int(bsum) % q))
                bsum = bsum // q
    if ext and l_qr > 1:
        resx = []
        for i1 in range(num // l_qr):
            resx.append(sum([z**j1 * res[i1 * l_qr + j1] for j1 in range(l_qr)]))
        res = resx
    return res[:num]


def compress_gf(data, num, ext=False):
    # Convert elements of $\mathbb{F}_{q}$ to bytes
    if ext and l_qr > 1:
        # Coerce to GF_ext, forces unresolved calculations
        xdata = vector(GF_ext, data)
        d1 = []
        for i1 in range(num // l_qr):
            d1 += xdata[i1].list()
        data = d1
    res = []
    idx = 0
    while idx < len(data):
        sum = 0
        for i in range(min(PACK_GF, len(data) - idx)):
            sum += to_int(data[idx + i]) * int(q**i)
        idx += PACK_GF
        for i in range(PACK_BYTES):
            res.append(int(sum) % 256)
            sum = sum // 256
    return bytes(res[:BYTES_GF(num)])


def hash_combined(msg, pk_seed, salt):
    # Get message hash in $\mathbb{F}_{q}$
    state = hashlib.shake_256()
    if SIGN_DIGEST:
        state.update(pk_seed)
        dgst = hashlib.shake_256(msg).digest(64)
        state.update(dgst)
    else:
        state.update(pk_seed)
        state.update(msg)
    state.update(salt)
    res = state.digest(BYTES_GF(GF16_HASH))

    if l_qr > 1:
        res_gf = expand_gf(res, GF16_HASH, ext=False)
        msg_hash = res_gf[:m2 * l_qr]
    else:
        res_gf = expand_gf(res, GF16_HASH)
        # Necessary to be compliant to KATs from C-Reference
        msg_hash = [res_gf[mi * l * r + j1 * l + i1] for mi in range(o) for i1 in range(l) for j1 in range(r)]

    return msg_hash, res


# XOF

def snova_xof(seed):
    # $\texttt{SNOVA{\_}SHAKE}$ public key expansion
    blocks = (NUM_GEN_PUB_BYTES + 167) // 168
    res = bytearray()
    for i in range(blocks):
        blockseed = bytearray(seed)
        for j in range(8):
            blockseed.append((i >> (8 * j)) % 256)
        res += hashlib.shake_128(blockseed).digest(168)
    return bytes(res[:NUM_GEN_PUB_BYTES])


# Expand secret

def expand_T12(sk_data):
    # Generate the secret map $T_{12}$

    def gen_a_FqS(coefs):
        # Generate elements of $\mathbb{F}_{q}[S]$
        if SNOVA and coefs[l * l_qr - 1] == 0:
            coefs[l * l_qr - 1] = q - (coefs[0] if coefs[0] != 0 else 1)
        F = matrix(GF_ext, l, l)
        for i1 in range(l):
            F += S**i1 * sum([z**j1 * from_int(coefs[i1 * l_qr + j1]) for j1 in range(l_qr)])
        return F

    coef = []
    idx = 0
    i = 0
    while i < o * v * l * l_qr:
        b = sk_data[idx]
        if q == 16:
            coef.append(b % 16)
            coef.append(b // 16)
            i += 2
        else:
            if b < (256 // q) * q:
                coef.append(b % q)
                i += 1
        idx += 1
    T12 = [gen_a_FqS(coef[l * l_qr * i:]) for i in range(o * v)]

    # Convert to a single matrix
    T12m = matrix(GF_ext, v * l, o * l)
    for ni in range(v):
        for nj in range(o):
            for i1 in range(l):
                for j1 in range(l):
                    T12m[ni * l + i1, nj * l + j1] = T12[ni * o + nj][i1, j1]
    return T12m


# Expand public

def convert_bytes_to_GF(data):
    # Expand public XOF data
    if q == 16:
        res = []
        for item in data:
            res.append(from_int(item % 16))
            res.append(from_int(item // 16))
        return res
    else:
        return [item % q for item in data]


def fixed_abq():
    NUM_ABQ = o * n_alpha * (r * (r + l) + 2 * l)
    abqdata = hashlib.shake_256(b'SNOVA_ABQ').digest(NUM_ABQ)
    return convert_bytes_to_GF(abqdata)


def expand_public_sym(seed):
    # Generate the random part of public key for odd $q$
    bindata = snova_xof(seed)
    data = convert_bytes_to_GF(bindata)
    if l_qr > 1:
        data = [sum([z**j1 * data[i1 * l_qr + j1] for j1 in range(l_qr)]) for i1 in range(len(data) // l_qr)]

    idx = 0
    Pm11 = []
    Pm12 = []
    Pm21 = []
    for _ in range(m1):
        p11 = matrix(GF_ext, v * l, v * l)
        p12 = matrix(GF_ext, v * l, o * l)
        p21 = matrix(GF_ext, o * l, v * l)
        for ni in range(v):
            for i1 in range(l):
                for j1 in range(i1, l):
                    p11[ni * l + i1, ni * l + j1] = data[idx]
                    p11[ni * l + j1, ni * l + i1] = data[idx]
                    idx += 1
            for nj in range(ni + 1, v):
                for i1 in range(l):
                    for j1 in range(l):
                        p11[ni * l + i1, nj * l + j1] = data[idx]
                        p11[nj * l + j1, ni * l + i1] = data[idx]
                        idx += 1
            for nj in range(o):
                for i1 in range(l):
                    for j1 in range(l):
                        p12[ni * l + i1, nj * l + j1] = data[idx]
                        p21[nj * l + j1, ni * l + i1] = data[idx]
                        idx += 1
        Pm11.append(p11)
        Pm12.append(p12)
        Pm21.append(p21)
    return Pm11, Pm12, Pm21, fixed_abq() if l < 4 else data[idx:]


def expand_public_asym(seed):
    # Generate the random part of public key for $q=16$
    bindata = snova_xof(seed)
    data = convert_bytes_to_GF(bindata)
    if l_qr > 1:
        data = [sum([z**j1 * data[i1 * l_qr + j1] for j1 in range(l_qr)]) for i1 in range(len(data) // l_qr)]

    idx = 0
    Pm11 = []
    for _ in range(m1):
        p11 = matrix(GF_ext, v * l, v * l)
        for ni in range(v):
            for nj in range(v):
                for i1 in range(l):
                    for j1 in range(l):
                        p11[ni * l + i1, nj * l + j1] = data[idx]
                        idx += 1
        Pm11.append(p11)
    Pm12 = []
    for _ in range(m1):
        p12 = matrix(GF_ext, v * l, o * l)
        for ni in range(v):
            for nj in range(o):
                for i1 in range(l):
                    for j1 in range(l):
                        p12[ni * l + i1, nj * l + j1] = data[idx]
                        idx += 1
        Pm12.append(p12)
    Pm21 = []
    for _ in range(m1):
        p21 = matrix(GF_ext, o * l, v * l)
        for ni in range(o):
            for nj in range(v):
                for i1 in range(l):
                    for j1 in range(l):
                        p21[ni * l + i1, nj * l + j1] = data[idx]
                        idx += 1
        Pm21.append(p21)
    return Pm11, Pm12, Pm21, fixed_abq() if l < 4 else data[idx:]


def expand_public(seed):
    if ASYMMETRIC_PUBMAT:
        return expand_public_asym(seed)
    else:
        return expand_public_sym(seed)


def compress_p22(pub22):
    # Pack the generated public key as bytes
    pk = bytearray()
    res = []
    for mi in range(m1):
        for ni in range(o):
            if ASYMMETRIC_PUBMAT:
                for nj in range(o):
                    for i1 in range(l):
                        for j1 in range(l):
                            res.append(pub22[mi][ni * l + i1, nj * l + j1])
            else:
                for i1 in range(l):
                    for j1 in range(i1, l):
                        res.append(pub22[mi][ni * l + i1, ni * l + j1])
                    for nj in range(ni + 1, o):
                        for j1 in range(l):
                            res.append(pub22[mi][ni * l + i1, nj * l + j1])
    pk += compress_gf(res, NUMGF_PK * l_qr, ext=True)
    return pk


def expand_p22(p22bytes):
    # Expand public key
    data = expand_gf(p22bytes, NUMGF_PK * l_qr, ext=True)
    idx = 0
    P22 = []
    for _ in range(m1):
        pub22 = matrix(GF_ext, o * l, o * l)
        for ni in range(o):
            if ASYMMETRIC_PUBMAT:
                for nj in range(o):
                    for i1 in range(l):
                        for j1 in range(l):
                            pub22[ni * l + i1, nj * l + j1] = data[idx]
                            idx += 1
            else:
                for i1 in range(l):
                    for j1 in range(i1, l):
                        pub22[ni * l + i1, ni * l + j1] = data[idx]
                        pub22[ni * l + j1, ni * l + i1] = data[idx]
                        idx += 1
                    for nj in range(ni + 1, o):
                        for j1 in range(l):
                            pub22[ni * l + i1, nj * l + j1] = data[idx]
                            pub22[nj * l + j1, ni * l + i1] = data[idx]
                            idx += 1
        P22.append(pub22)
    return P22


def decode_sig(sig_bytes):
    # Decode sig
    # salt = sig_bytes[-16:]
    gfsig = expand_gf(sig_bytes[:-16], n * l * r * l_qr, ext=True)
    if len(gfsig) < n * l * r:
        raise Exception('Verify failed.')
    sig = matrix(GF_ext, n * l, r, lambda i, j: gfsig[i * r + j])

    return sig, salt


# Generate E matrix

def gen_E(abqdata):
    if RANDOM_E:
        NUM_E = m1 * m2 * r**2 * l**2 * l_qr
        e_bytes = hashlib.shake_256(b'SNOVA_E').digest(NUM_E)
        e_data = convert_bytes_to_GF(e_bytes)
        emat = [[[matrix(GF_q, m2 * l_qr, r**2, lambda i, j: e_data[(((a * l + b) * m1 + mi) * m2 * l_qr + i) * r**2 + j])
                 for a in range(l)] for b in range(l)] for mi in range(m1)]
        return emat

    def create_AB(data, r1, r2):
        # Generate invertible matrices
        M = matrix(GF_q, r1, r2, lambda i, j: data[i * r2 + j])
        if l == r1 and l == r2:
            f1 = 1
            while M.det() == 0 and f1 < q:
                M += from_int(f1) * S
                f1 += 1
            if f1 == q:
                raise Exception('f1 == q')
        return M

    def nonzero_q(data):
        fq = [to_int(data[i]) for i in range(l)]
        if fq[l - 1] == 0:
            fq[l - 1] = q - (fq[0] if fq[0] != 0 else 1)
        return [from_int(fq[i]) for i in range(l)]

    A = [create_AB(abqdata[i * r**2:], r, r) for i in range(o * n_alpha)]
    B = [create_AB(abqdata[o * n_alpha * r**2 + i * l * r:], r, l) for i in range(o * n_alpha)]
    q1 = [nonzero_q(abqdata[o * n_alpha * r * (r + l) + i * l:]) for i in range(o * n_alpha)]
    q2 = [nonzero_q(abqdata[o * n_alpha * r * (r + l) + o * n_alpha * l + i * l:]) for i in range(o * n_alpha)]

    emat = [[[matrix(GF_ext, m2, r**2) for a in range(l)] for b in range(l)] for mi in range(m1)]
    for mi in range(o):
        for alpha in range(n_alpha):
            mia = mi * n_alpha + alpha
            mi_prime = (mi + alpha) % m1
            for a in range(l):
                for b in range(l):
                    for i1 in range(l):
                        for i2 in range(r):
                            for j1 in range(r):
                                for j2 in range(r):
                                    emat[mi_prime][a][b][mi * l * r + i1 * r + i2, j1 * r + j2] += \
                                        A[mia][i2, j1] * q1[mia][a] * q2[mia][b] * B[mia][j2, i1]
    return emat

################################################################


def QR_proj(x):
    if l_qr > 1:
        return x[0]
    else:
        return x

# API functions


def genkeys(seed):
    # Generate Public key
    sk = seed
    sk_seed = sk[16:]
    pk_seed = sk[:16]
    t12data = hashlib.shake_256(sk_seed).digest(2 * o * v * l * l_qr)  # Overdimensioned

    T12 = expand_T12(t12data)
    P11, P12, P21, _ = expand_public(pk_seed)

    P22 = [-(T12.transpose() * (P11[mi] * T12 + P12[mi]) + P21[mi] * T12) for mi in range(m1)]

    return sk, pk_seed + compress_p22(P22)


# Sign message

def sign(sk, msg, salt):
    '''
    Sign message

    In an alternative but equivalent formulation of QR-UOV, the verify compares a hash
    to a projected MQ value, projected from GF_ext to GF_q by QR_proj

    To sign, a signature in GF_ext is to be found. This signature in GF_ext can be written in
    components of GF_q in terms of its coefficients s_{i,k}
    $signature_i = sum_{k=0}^{l-1} s_{i,k} z^k$

    The coefficients of the A matrix that solves $y = A cdot x$
    for some vinegar $v$ are then given by $QR_proj(F_{21} cdot v z^k)$
    The entries of y, A and x are in GF_q. After solving, $x$ has the coefficients s_{i,k}.
    '''

    sk_seed = sk[16:]
    pk_seed = sk[:16]
    t12data = hashlib.shake_256(sk_seed).digest(2 * o * v * l * l_qr)  # Overdimensioned
    m_g = m2 * l_qr

    T12 = expand_T12(t12data)

    P11, P12, P21, abqdata = expand_public(pk_seed)
    emat = gen_E(abqdata)

    # Expand private key
    F12 = []
    F21 = []
    for mi in range(m1):
        F12.append(P11[mi] * T12 + P12[mi])
        F21.append(T12.transpose() * P11[mi] + P21[mi])

    num_sign = 0
    while True:
        num_sign += 1
        if num_sign == 255:
            raise Exception('signing failed')

        # Assign values to vinegar variables
        # Vinegar from sk and salt

        salt_byte = salt
        msg_hash, msg_bytes = hash_combined(msg, pk_seed, salt_byte)
        v_state = hashlib.shake_256()
        v_state.update(sk_seed)
        if SIGN_DIGEST:
            dgst = hashlib.shake_256(msg).digest(64)
            v_state.update(dgst)
            v_state.update(salt)
        else:
            v_state.update(msg_bytes)
        v_state.update(num_sign.to_bytes(1))
        vinegar_byte = v_state.digest(BYTES_GF(v * l * r))
        vinegar_gf = expand_gf(vinegar_byte, v * l * r)
        vinegar = matrix(GF_ext, v * l, r, lambda i, j: vinegar_gf[i * r + j])
        rvec = vector(GF_ext, m2 * l_qr)

        # Compute the vinegar part of the central map
        p_vin = [[[vinegar.transpose() * S_times_v**b * P11[mi] * S_times_v**a * vinegar
                   for a in range(l)] for b in range(l)] for mi in range(m1)]

        # Apply emulsifier
        res = vector(GF_ext, m_g)
        for mi in range(m1):
            for a in range(l):
                for b in range(l):
                    vin_vec = vector([p_vin[mi][a][b][i1, j1] for i1 in range(r) for j1 in range(r)])
                    res += emat[mi][a][b] * vin_vec
        F_vv = list(res)

        # Get msg vinegar part
        msg_vv = vector([msg_hash[idx] - QR_proj(F_vv[idx]) for idx in range(m_g)])

        # Compute the coefficient matrix of the oil variable
        # compute the coefficients of Xo and put into gauss matrix
        F21_ab = [[[S_times_o**b * F21[mi] * S_times_v**a * vinegar
                    for a in range(l)] for b in range(l)] for mi in range(m1)]
        F12_ab = [[[vinegar.transpose() * S_times_v**b * F12[mi] * S_times_o**a
                    for a in range(l)] for b in range(l)] for mi in range(m1)]

        A = matrix(GF_ext, m_g, m2 * l_qr)
        for ti1 in range(m_g):
            for tj1 in range(o * l):
                for tj2 in range(r):
                    for mi_prime in range(m1):
                        for a in range(l):
                            for b in range(l):
                                for k1 in range(r):
                                    val = \
                                        emat[mi_prime][a][b][ti1, tj2 * r + k1] \
                                        * F21_ab[mi_prime][a][b][tj1, k1] \
                                        + emat[mi_prime][a][b][ti1, k1 * r + tj2] \
                                        * F12_ab[mi_prime][a][b][k1, tj1]
                                    for nk in range(l_qr):
                                        A[ti1, (tj2 * o * l + tj1) * l_qr + nk] += QR_proj(val * z**nk)

        try:
            solution = A.solve_right(msg_vv - A * rvec) + rvec
        except ValueError:
            # print('no solution', num_sign, file=sys.stderr)
            continue

        if l_qr > 1:
            solution = [sum([solution[(tj2 * o * l + tj1) * l_qr + nk] * z**nk for nk in range(l_qr)])
                        for tj1 in range(o * l) for tj2 in range(r)]
        else:
            solution = [solution[tj2 * o * l + tj1] for tj1 in range(o * l) for tj2 in range(r)]

        sol_mat = matrix(GF_ext, o * l, r, lambda i, j: solution[i * r + j])
        vinegar += T12 * sol_mat
        sig_gf = [vinegar[mi * l + i1, j1] for mi in range(v) for i1 in range(l) for j1 in range(r)]
        sig_gf += solution

        # Check for symmetric signature
        ok = True
        if l > 1 and l == r and not ASYMMETRIC_PUBMAT:
            for idx in range(n):
                is_sym = True
                for i1 in range(l):
                    for j1 in range(i1 + 1, l):
                        if sig_gf[idx * l * r + i1 * r + j1] != sig_gf[idx * l * r + j1 * r + i1]:
                            is_sym = False
                if is_sym:
                    ok = False
        if ok:
            break

    return compress_gf(sig_gf, n * l * r * l_qr, ext=True) + salt_byte


# Verify signature of message

def verify(pk, sig_bytes, msg):
    # Verify signature of message

    # Decode sig
    sig, salt = decode_sig(sig_bytes)

    # Check for symmetric signature
    if l > 1 and l == r and not ASYMMETRIC_PUBMAT:
        for idx in range(n):
            is_sym = True
            for i1 in range(l):
                for j1 in range(i1 + 1, l):
                    if sig[idx * l + i1, j1] != sig[idx * l + j1, i1]:
                        is_sym = False
            if is_sym:
                raise Exception('Verify failed!')

    # Expand pubkey
    pk_seed = pk[:16]
    P11, P12, P21, abqdata = expand_public(pk_seed)
    P22 = expand_p22(pk[16:])
    P = [matrix.block([[P11[mi], P12[mi]], [P21[mi], P22[mi]]]) for mi in range(m1)]

    # Whip-up signature
    p_sig = [[[sig.transpose() * S_times_n**b * P[mi] * S_times_n**a * sig
               for a in range(l)] for b in range(l)] for mi in range(m1)]

    # Apply emulsifier
    emat = gen_E(abqdata)

    res = vector(GF_ext, emat[0][0][0].nrows())
    for mi in range(m1):
        for a in range(l):
            for b in range(l):
                sig_vec = vector([p_sig[mi][a][b][i1, j1] for i1 in range(r) for j1 in range(r)])
                res += emat[mi][a][b] * sig_vec
    sig_hash = [QR_proj(val) for val in res]

    # Check against expected hash
    msg_hash, _ = hash_combined(msg, pk_seed, salt)

    if msg_hash != sig_hash:
        raise Exception('Verify failed')


################################################################


# Generate KATs
entropy_input = bytearray(48)
for i in range(48):
    entropy_input[i] = i
drbg = rng(entropy_input)
srbdg = rng(entropy_input)

print('# TSUOV', v, o, q, l, l_qr, ' / ', r, m1, m2 * l_qr)
print()

for count in range(1):
    seed = drbg.random_bytes(48)
    srbdg = rng(seed)

    keygen_seed = srbdg.random_bytes(48)
    salt = srbdg.random_bytes(16)

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
