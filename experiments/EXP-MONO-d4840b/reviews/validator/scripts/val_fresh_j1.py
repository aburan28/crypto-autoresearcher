"""
Validator J1 -- fresh, independent script (not reusing any prior file in scratchpad).
Build a chi table from scratch and confirm:
  (1) chi(-x) = chi(-1) * chi(x) for all nonzero x, at p=101 and p=103
  (2) chi(-1) = +1 when p == 1 mod 4 (p=101), chi(-1) = -1 when p == 3 mod 4 (p=103)
"""

def build_chi_table(p):
    # chi(x) = x^((p-1)/2) mod p, mapped to {-1, 0, 1}
    chi = [0] * p
    e = (p - 1) // 2
    for x in range(p):
        if x == 0:
            chi[x] = 0
            continue
        v = pow(x, e, p)
        if v == 1:
            chi[x] = 1
        elif v == p - 1:
            chi[x] = -1
        else:
            raise ValueError(f"unexpected residue {v} for x={x}, p={p} (not prime? Euler failed)")
    return chi

for p in (101, 103):
    assert all(p % d != 0 for d in range(2, int(p**0.5) + 1)), f"{p} not prime"
    chi = build_chi_table(p)
    print(f"--- p={p}, p mod 4 = {p % 4} ---")
    print(f"chi(-1) = chi[{(-1) % p}] = {chi[(-1) % p]}")
    expected_neg1 = 1 if p % 4 == 1 else -1
    assert chi[(-1) % p] == expected_neg1, f"chi(-1) mismatch at p={p}"
    # confirm chi(-x) = chi(-1)*chi(x) for ALL nonzero x
    mismatches = []
    for x in range(1, p):
        lhs = chi[(-x) % p]
        rhs = chi[-1 % p] * chi[x]
        if lhs != rhs:
            mismatches.append((x, lhs, rhs))
    print(f"checked chi(-x)==chi(-1)*chi(x) for all {p-1} nonzero x: "
          f"{'ALL MATCH' if not mismatches else f'{len(mismatches)} MISMATCHES'}")
    if mismatches:
        print("  sample mismatches:", mismatches[:5])
    # also brute-force cross-check chi via direct QR test (is x a square mod p by scanning squares)
    squares = set((y * y) % p for y in range(1, p))
    qr_mismatches = []
    for x in range(1, p):
        is_qr = x in squares
        expected = 1 if is_qr else -1
        if chi[x] != expected:
            qr_mismatches.append((x, chi[x], expected))
    print(f"cross-check chi against brute-force QR-by-squares test: "
          f"{'ALL MATCH' if not qr_mismatches else f'{len(qr_mismatches)} MISMATCHES'}")
