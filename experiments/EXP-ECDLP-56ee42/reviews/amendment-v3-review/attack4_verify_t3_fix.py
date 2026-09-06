import numpy as np

def rudin_shapiro_u_ref(x: int) -> int:
    if x < 2:
        return 0
    bits = bin(x)[2:]
    return sum(1 for i in range(len(bits) - 1) if bits[i] == '1' and bits[i+1] == '1')

def u_via_popcount_identity(x: int) -> int:
    return bin(x & (x >> 1)).count('1')

# --- Check 1: scalar identity u(x) = popcount(x & (x>>1)) over a wide range ---
N = 5_000_000
mismatches = 0
for x in range(N):
    a = rudin_shapiro_u_ref(x)
    b = u_via_popcount_identity(x)
    if a != b:
        mismatches += 1
        if mismatches <= 5:
            print("MISMATCH", x, a, b)
print(f"Check 1: scalar identity mismatches over [0,{N}) = {mismatches}")

# --- Check 1b: edge cases / larger/random 64-bit-ish values (beyond the
# experiment's actual domain, to check the identity's generality) ---
import random
random.seed(12345)
mism2 = 0
for _ in range(200000):
    x = random.randint(0, 2**40)
    if rudin_shapiro_u_ref(x) != u_via_popcount_identity(x):
        mism2 += 1
print(f"Check 1b: identity mismatches over 200000 random x in [0,2^40) = {mism2}")

# --- Check 2: vectorized SWAR popcount_mod4-style reduction, mod2 variant ---
def popcount_mod4_array(xs: np.ndarray) -> np.ndarray:
    """Exact copy of estimator.py's popcount_mod4_array."""
    x = xs.astype(np.uint64)
    c = x - ((x >> 1) & 0x5555555555555555)
    c = (c & 0x3333333333333333) + ((c >> 2) & 0x3333333333333333)
    c = (c + (c >> 4)) & 0x0F0F0F0F0F0F0F0F
    pc = ((c * 0x0101010101010101) >> 56).astype(np.uint8)
    return (pc % 4).astype(np.int8)

def popcount_exact_array(xs: np.ndarray) -> np.ndarray:
    """Same SWAR chain but returns the EXACT popcount (0..64), not mod-reduced,
    to confirm the reduction chain itself is a genuine full popcount (i.e. that
    taking mod 2 at the end instead of mod 4 is a valid substitution, not a
    different algorithm)."""
    x = xs.astype(np.uint64)
    c = x - ((x >> 1) & 0x5555555555555555)
    c = (c & 0x3333333333333333) + ((c >> 2) & 0x3333333333333333)
    c = (c + (c >> 4)) & 0x0F0F0F0F0F0F0F0F
    pc = ((c * 0x0101010101010101) >> 56).astype(np.uint64)
    return pc

def rudin_shapiro_sign_true_array_proposed(xs: np.ndarray) -> np.ndarray:
    """The amendment's proposed vectorized fix: y = x & (x>>1); run the SAME
    SWAR popcount reduction popcount_mod4_array uses on y; take mod 2 instead
    of mod 4."""
    x = xs.astype(np.uint64)
    y = x & (x >> 1)
    c = y - ((y >> 1) & 0x5555555555555555)
    c = (c & 0x3333333333333333) + ((c >> 2) & 0x3333333333333333)
    c = (c + (c >> 4)) & 0x0F0F0F0F0F0F0F0F
    pc = ((c * 0x0101010101010101) >> 56).astype(np.uint8)
    bit = (pc % 2).astype(np.int64)
    return (1 - 2 * bit).astype(np.int8)

def rudin_shapiro_sign_true_scalar(x: int) -> int:
    return 1 if (x & (x >> 1)).bit_count() % 2 == 0 else -1

# Check that popcount_exact_array actually matches Python's bit_count for a
# range including values with many bits set (confirms the SWAR chain is a
# genuine full popcount, so mod-4 -> mod-2 is a valid endpoint substitution).
xs_test = np.arange(0, 2_000_000, dtype=np.uint64)
exact = popcount_exact_array(xs_test)
ref_exact = np.array([int(x).bit_count() for x in xs_test.tolist()[:200000]])
match_exact = np.array_equal(exact[:200000], ref_exact)
print(f"Check 2a: SWAR chain reproduces EXACT popcount over 200000 samples: {match_exact}")

# also test some large values (up to 2^63-ish) to check the SWAR chain doesn't
# depend on value being 'small' -- test random 63-bit values
rand63 = np.array([random.randint(0, 2**63 - 1) for _ in range(50000)], dtype=np.uint64)
exact_rand = popcount_exact_array(rand63)
ref_rand = np.array([int(x).bit_count() for x in rand63.tolist()])
match_rand63 = np.array_equal(exact_rand, ref_rand)
print(f"Check 2b: SWAR chain reproduces EXACT popcount for 50000 random 63-bit values: {match_rand63}")

# Now the actual proposed T3 vectorized function vs scalar and vs reference,
# over the full range the experiment cares about (up to 2^20 as required, and
# further up to 2,000,000 as this session's other spot check claimed).
xs = np.arange(0, 2_000_000, dtype=np.uint64)
arr_out = rudin_shapiro_sign_true_array_proposed(xs)
mism3 = 0
for x in range(0, 2_000_000, 1):
    pass  # will vectorize the reference check below instead of a slow python loop

ref_sign = np.array([rudin_shapiro_sign_true_scalar(int(x)) for x in xs[:300000].tolist()])
mism3 = int(np.sum(arr_out[:300000] != ref_sign))
print(f"Check 3: vectorized rudin_shapiro_sign_true_array vs scalar over 300000 samples mismatches = {mism3}")

# vs the reference u(x) mod 2 sign directly (ground truth from block-count def)
ref_from_u = np.array([1 if rudin_shapiro_u_ref(int(x)) % 2 == 0 else -1 for x in xs[:300000].tolist()])
mism4 = int(np.sum(arr_out[:300000] != ref_from_u))
print(f"Check 4: vectorized array vs literal block-count u(x) reference over 300000 samples mismatches = {mism4}")

# Check array-vs-scalar consistency over x in [0, 2^20) as V3-RA-3 (c) requires
xs220 = np.arange(0, 2**20, dtype=np.uint64)
arr220 = rudin_shapiro_sign_true_array_proposed(xs220)
scalar220 = np.array([rudin_shapiro_sign_true_scalar(int(x)) for x in xs220.tolist()])
mism5 = int(np.sum(arr220 != scalar220))
print(f"Check 5 (V3-RA-3c style, x in [0,2^20)): array-vs-scalar mismatches = {mism5}")

# Check OEIS A020985 for x=0..15 (values of the LITERAL Rudin-Shapiro
# sequence r(n) = (-1)^{number of (possibly overlapping) occurrences of 11 in
# binary expansion of n}); OEIS A020985 lists 1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,1,-1,-1 for n=0..15
oeis_a020985 = [1,1,1,-1,1,1,-1,1,1,1,1,-1,-1,1,-1,-1]
computed016 = [rudin_shapiro_sign_true_scalar(x) for x in range(16)]
print("OEIS A020985 (n=0..15):      ", oeis_a020985)
print("rudin_shapiro_sign_true(0..15):", computed016)
print("Check 6: OEIS match:", oeis_a020985 == computed016)
