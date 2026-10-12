"""Locked higher-order scores; dimensionless except MI/entropy (bits) and runs.

These are coordinate/sequence statistics, not group rank or ECDLP cost.
Integer binning and residue/bit extraction are exact. Floating normalization
is used only for ordinal patterns and spectral calculations.
"""
import numpy as np

WALK_METRICS = ['mi_lag1', 'mi_lag4', 'triple64', 'triple96', 'motif64',
                'longrun64', 'spectral64', 'hankel64_deficit', 'perm_gap', 'lowx_pairs']
FIELD_METRICS = ['xy_mi', 'x_tail64', 'xy_tail64', 'x_mod64_dispersion']


def mutual_information(left, right, bins=8):
    counts = np.bincount(bins*left+right, minlength=bins*bins).reshape(bins, bins)
    joint = counts / len(left)
    product = joint.sum(1)[:, None] * joint.sum(0)[None, :]
    keep = joint > 0
    return float(np.sum(joint[keep]*np.log2(joint[keep]/product[keep])))


def longest_run(bits):
    changes = np.flatnonzero(bits[1:] != bits[:-1]) + 1
    return int(np.diff(np.r_[0, changes, len(bits)]).max())


def gf2_hankel_rank(bits, size=32):
    # Packed integer Gaussian elimination over GF(2), no floating rank.
    basis = {}
    for i in range(size):
        row = sum(int(bits[i+j]) << j for j in range(size))
        while row:
            pivot = row.bit_length()-1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def encode(coords, p):
    width = (p.bit_length()+7)//8
    return b''.join(x.to_bytes(width, 'big')+y.to_bytes(width, 'big') for x, y in coords)


def decode(raw, p):
    width = (p.bit_length()+7)//8
    if len(raw) % (2*width):
        raise ValueError('Truncated point encoding')
    return [(int.from_bytes(raw[i:i+width], 'big'), int.from_bytes(raw[i+width:i+2*width], 'big'))
            for i in range(0, len(raw), 2*width)]


def transport(raw, p):
    return encode([(4*x % p, 8*y % p) for x, y in decode(raw, p)], p)


def features(raw, p):
    width = (p.bit_length()+7)//8
    encoded = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 2, width)
    n = len(encoded)
    if n < 64:
        raise ValueError('At least 64 points needed for higher-order scores')
    weights = np.exp2(-8.0*np.arange(1, width+1))
    normalized = (encoded.astype(np.float64) @ weights) / (p / 2**(8*width))
    # Eight bins, exact correction near boundaries; tails use 64 bins.
    scaled = normalized*64
    bins64 = np.floor(scaled).astype(np.int64)
    near = np.argwhere(np.abs(scaled-np.rint(scaled)) < 1e-11)
    for i, axis in near:
        bins64[i, axis] = 64*int.from_bytes(encoded[i, axis].tobytes(), 'big')//p
    if np.any(bins64 < 0) or np.any(bins64 >= 64):
        raise ValueError('Point coordinates outside the field')
    xb, yb = bins64[:, 0]//8, bins64[:, 1]//8
    result = {'mi_lag1': mutual_information(xb[:-1], xb[1:]),
              'mi_lag4': mutual_information(xb[:-4], xb[4:]),
              'xy_mi': mutual_information(xb, yb)}
    xlow, ylow = bins64[:, 0] == 0, bins64[:, 1] == 0
    result.update(x_tail64=float(xlow.mean()), xy_tail64=float((xlow & ylow).mean()),
                  lowx_pairs=float((xlow[:-1] & xlow[1:]).mean()))
    for bit in (64, 96):
        values = ((encoded[:, 0, width-1-bit//8] >> (bit % 8)) & 1).astype(np.int8)
        signed = values*2-1
        result[f'triple{bit}'] = float(abs(np.mean(signed[:-2]*signed[1:-1]*signed[2:])))
        if bit == 64:
            motifs = values[:-3]*8+values[1:-2]*4+values[2:-1]*2+values[3:]
            counts = np.bincount(motifs, minlength=16)
            result['motif64'] = float(np.sum((counts-(n-3)/16)**2/((n-3)/16))/15)
            result['longrun64'] = longest_run(values)
            spectrum = np.abs(np.fft.rfft(signed-signed.mean()))[1:]**2
            result['spectral64'] = float(spectrum.max()/spectrum.mean()) if spectrum.mean() else float(n)
            result['hankel64_deficit'] = 32-gf2_hankel_rank(values)
    windows = np.lib.stride_tricks.sliding_window_view(normalized[:, 0], 3)
    order = np.argsort(windows, axis=1, kind='stable')
    # Handle extraordinarily close floating ties with exact x values.
    ties = np.flatnonzero(np.any(np.diff(np.sort(windows, axis=1), axis=1) == 0, axis=1))
    for i in ties:
        exact = [int.from_bytes(encoded[i+j, 0].tobytes(), 'big') for j in range(3)]
        order[i] = sorted(range(3), key=lambda j: (exact[j], j))
    codes = 9*order[:, 0]+3*order[:, 1]+order[:, 2]
    counts = np.bincount(codes, minlength=27)
    probabilities = counts[counts > 0]/(n-2)
    result['perm_gap'] = float(max(0, np.log2(6)+np.sum(probabilities*np.log2(probabilities))))
    residues = encoded[:, 0, -1] & 63
    counts = np.bincount(residues, minlength=64)
    result['x_mod64_dispersion'] = float(np.sum((counts-n/64)**2/(n/64))/63)
    return result
