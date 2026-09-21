"""Toy elliptic-curve group arithmetic and point encodings for EXP-REPL-1d1287."""
import hashlib
import json

def mod_inv(a, p):
    return pow(int(a) % p, p - 2, p)

def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * mod_inv(2 * y1, p) % p
    else:
        lam = (y2 - y1) * mod_inv((x2 - x1) % p, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(k, P, a, p):
    R = None
    Q = P
    k = int(k)
    while k > 0:
        if k & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_add(Q, Q, a, p)
        k >>= 1
    return R

class Curve:
    def __init__(self, name, p, a, b, N, G):
        self.name, self.p, self.a, self.b, self.N, self.G = name, p, a, b, N, tuple(G)
        self.bits_p = p.bit_length()
        # pad coordinate width to a multiple of 4 bits (hex limbs)
        self.limb_bits = 4
        self.n_limbs_coord = -(-self.bits_p // self.limb_bits)  # ceil
        self.coord_width_bits = self.n_limbs_coord * self.limb_bits

    def scalar_mul(self, k):
        return ec_mul(k % self.N, self.G, self.a, self.p)

def load_curves(path="/tmp/wt-run-exp/experiments/EXP-REPL-1d1287/curves.json"):
    with open(path) as f:
        d = json.load(f)
    out = {}
    for name, c in d["curves"].items():
        out[name] = Curve(name, c["p"], c["a"], c["b"], c["subgroup_order"], c["generator"])
    return out

def int_to_limbs(x, n_limbs, limb_bits=4):
    mask = (1 << limb_bits) - 1
    return [(x >> (limb_bits * i)) & mask for i in range(n_limbs - 1, -1, -1)]

# ---- presentations ----

def encode_affine_xy(curve, k):
    x, y = curve.scalar_mul(k)
    return int_to_limbs(x, curve.n_limbs_coord) + int_to_limbs(y, curve.n_limbs_coord)

def encode_x_only(curve, k):
    x, y = curve.scalar_mul(k)
    return int_to_limbs(x, curve.n_limbs_coord)

def encode_projective(curve, k, rng):
    x, y = curve.scalar_mul(k)
    p = curve.p
    z = rng.randrange(1, p)
    z2 = (z * z) % p
    z3 = (z2 * z) % p
    X = (x * z2) % p
    Y = (y * z3) % p
    Z = z
    return int_to_limbs(X, curve.n_limbs_coord) + int_to_limbs(Y, curve.n_limbs_coord) + int_to_limbs(Z, curve.n_limbs_coord)

def encode_planted_leaky(curve, k):
    # affine_xy_limbs but the last hex limb of the x-encoding is overwritten
    # with the top 4 bits of k (which determine the MSB target directly).
    # This is C3: a deliberately, trivially learnable channel.
    x, y = curve.scalar_mul(k)
    xl = int_to_limbs(x, curve.n_limbs_coord)
    top4 = (k >> max(curve.N.bit_length() - 5, 0)) & 0xF
    xl = xl[:-1] + [top4]
    yl = int_to_limbs(y, curve.n_limbs_coord)
    return xl + yl

PRF_KEY = b"EXP-REPL-1d1287-scramble-prf-key-v1"

def encode_scrambled(curve, k, n_limbs_out):
    # PRF-driven bijection-like map from k to a bit-string of the same
    # length (in limbs) as affine_xy_limbs. The group is untouched (k still
    # indexes the same set of logarithms); the coordinate/algebraic
    # structure is destroyed -- output limbs are pseudorandom function of k
    # via HMAC-style hashing, unrelated to the curve's group law.
    needed_bytes = (n_limbs_out * 4 + 7) // 8 + 1
    out = b""
    counter = 0
    while len(out) < needed_bytes:
        h = hashlib.sha256(PRF_KEY + curve.name.encode() + k.to_bytes(8, "big") + counter.to_bytes(4, "big"))
        out += h.digest()
        counter += 1
    val = int.from_bytes(out, "big")
    return int_to_limbs(val, n_limbs_out)

def encode_shuffled_label_input(curve, k):
    # C2 uses the real affine encoding as input; only the label is shuffled
    # (done at dataset-assembly time, not here).
    return encode_affine_xy(curve, k)

PRESENTATIONS = ["affine_xy_limbs", "x_only_limbs", "projective_jacobian_limbs", "scrambled_labels"]

def msb_target(curve, k):
    return 1 if k < (curve.N // 2) else 0
