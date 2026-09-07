import functools

@functools.lru_cache(maxsize=None)
def a_recursive(n: int) -> int:
    """Standard recursive definition retrieved via web search:
    a(0)=1; a(n)=a(n//2) if n even; a(n) = (-1)**((n-1)//2) * a((n-1)//2) if n odd."""
    if n == 0:
        return 1
    if n % 2 == 0:
        return a_recursive(n // 2)
    m = (n - 1) // 2
    return ((-1) ** m) * a_recursive(m)

def u_block_count(x: int) -> int:
    if x < 2:
        return 0
    bits = bin(x)[2:]
    return sum(1 for i in range(len(bits) - 1) if bits[i] == '1' and bits[i + 1] == '1')

def sign_from_u(x: int) -> int:
    return 1 if u_block_count(x) % 2 == 0 else -1

# retrieved OEIS A020985 initial terms (n=0..15), via WebSearch of a mirror
retrieved_A020985 = [1, 1, 1, -1, 1, 1, -1, 1, 1, 1, 1, -1, -1, -1, 1, -1]

vals_recursive = [a_recursive(n) for n in range(16)]
vals_from_u = [sign_from_u(n) for n in range(16)]

print("retrieved A020985 (n=0..15):     ", retrieved_A020985)
print("standard recursive a(n) (n=0..15):", vals_recursive)
print("block-count-derived sign(n=0..15):", vals_from_u)
print("recursive == retrieved OEIS:", vals_recursive == retrieved_A020985)
print("block-count == retrieved OEIS:", vals_from_u == retrieved_A020985)

# Cross-check recursive def vs block-count def over a much larger range
N = 2_000_000
mism = 0
for x in range(N):
    if a_recursive(x) != sign_from_u(x):
        mism += 1
        if mism <= 5:
            print("cross-def mismatch at", x, a_recursive(x), sign_from_u(x))
print(f"recursive-vs-blockcount mismatches over [0,{N}) = {mism}")

# Now also check estimator.py's ACTUAL broken recursion against this correct one
def broken_recursion_scalar(x: int) -> int:
    if x < 2:
        return 1
    sign = 1
    while x >= 2:
        if x & 1:
            sign = -sign
        x >>= 1
    return sign

mism_broken_vs_correct = sum(1 for x in range(200000) if broken_recursion_scalar(x) != a_recursive(x))
print(f"BROKEN estimator.py recursion vs CORRECT standard recursion mismatches over [0,200000) = {mism_broken_vs_correct} (out of 200000)")
