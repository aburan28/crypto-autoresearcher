"""ref4.py -- INDEPENDENT implementation of MINI-AES-64.

Written from the specification, not from sq4.c: row-major matrix state,
log/antilog tables for GF(2^4) multiplication, list-of-lists round function.
It shares no code, no table and no data file with the attack.

Spec it implements:
  GF(2^4) modulo x^4+x+1 (0x13)
  state: 4x4 matrix of 4-bit cells; the 16-hex-character serialisation
         h[i] is cell (row = i mod 4, col = i div 4)   [column-major string]
  SubCells:   x -> A(x^{-1}),  A(b)_i = b_i ^ b_{i+1} ^ b_{i+2} ^ c_i (mod 4),
              c = 0x6, inverse of 0 taken as 0
  ShiftRows:  row r rotated LEFT by r
  MixColumns: circulant matrix with first row (02,03,01,01) over GF(2^4)
  KeySchedule: 4 words of 4 cells; w[i] = w[i-4] ^ f(w[i-1]);
              for i % 4 == 0, f = RotWord then SubCells then xor Rcon(i/4)
              into cell 0, Rcon(j) = x^(j-1) in GF(2^4)
  Encryption of R rounds: ARK(K0); rounds 1..R = SubCells, ShiftRows,
              MixColumns (omitted in round R), ARK(Kr)
"""

# --- GF(2^4) via log/antilog on the generator x=2 -------------------------
_ALOG = [0] * 30
_LOG = [None] * 16
_v = 1
for _i in range(15):
    _ALOG[_i] = _v
    _LOG[_v] = _i
    _v <<= 1
    if _v & 0x10:
        _v ^= 0x13
for _i in range(15, 30):
    _ALOG[_i] = _ALOG[_i - 15]


def gmul(a, b):
    if a == 0 or b == 0:
        return 0
    return _ALOG[_LOG[a] + _LOG[b]]


def ginv(a):
    if a == 0:
        return 0
    return _ALOG[(15 - _LOG[a]) % 15]


def _aff(b):
    out = 0
    for i in range(4):
        bit = ((b >> i) & 1) ^ ((b >> ((i + 1) % 4)) & 1) ^ ((b >> ((i + 2) % 4)) & 1) ^ ((0x6 >> i) & 1)
        out |= bit << i
    return out


SBOX = [_aff(ginv(x)) for x in range(16)]
MIXROW = [2, 3, 1, 1]


def rcon(j):
    return _ALOG[(j - 1) % 15]


def str2mat(h):
    assert len(h) == 16
    cells = [int(ch, 16) for ch in h]
    return [[cells[4 * c + r] for c in range(4)] for r in range(4)]


def mat2str(m):
    return "".join("%x" % m[r][c] for c in range(4) for r in range(4))


def key_schedule(keystr, nrounds):
    cells = [int(ch, 16) for ch in keystr]
    w = [cells[4 * i:4 * i + 4] for i in range(4)]
    for i in range(4, 4 * (nrounds + 1)):
        t = list(w[i - 1])
        if i % 4 == 0:
            t = t[1:] + t[:1]
            t = [SBOX[x] for x in t]
            t[0] ^= rcon(i // 4)
        w.append([w[i - 4][j] ^ t[j] for j in range(4)])
    keys = []
    for r in range(nrounds + 1):
        flat = []
        for i in range(4):
            flat.extend(w[4 * r + i])
        keys.append([[flat[4 * c + r2] for c in range(4)] for r2 in range(4)])
    return keys


def encrypt(ptstr, keystr, nrounds):
    st = str2mat(ptstr)
    ks = key_schedule(keystr, nrounds)
    st = [[st[r][c] ^ ks[0][r][c] for c in range(4)] for r in range(4)]
    for rnd in range(1, nrounds + 1):
        st = [[SBOX[st[r][c]] for c in range(4)] for r in range(4)]
        st = [[st[r][(c + r) % 4] for c in range(4)] for r in range(4)]
        if rnd != nrounds:
            new = [[0] * 4 for _ in range(4)]
            for c in range(4):
                col = [st[r][c] for r in range(4)]
                for r in range(4):
                    acc = 0
                    for k in range(4):
                        acc ^= gmul(MIXROW[(k - r) % 4], col[k])
                    new[r][c] = acc
            st = new
        st = [[st[r][c] ^ ks[rnd][r][c] for c in range(4)] for r in range(4)]
    return mat2str(st)


if __name__ == "__main__":
    import sys
    print(encrypt(sys.argv[1], sys.argv[2], int(sys.argv[3])))
