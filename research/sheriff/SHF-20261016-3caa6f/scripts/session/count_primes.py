"""B8 check for crypto:papers/structural-completeness/structural_completeness.tex:404
("all 621 primes p = 1 (mod 6) with p <= 5000"): count them."""
N = 5000
sieve = bytearray([1]) * (N + 1)
sieve[0:2] = b"\x00\x00"
for i in range(2, int(N ** 0.5) + 1):
    if sieve[i]:
        sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
primes = [p for p in range(N + 1) if sieve[p]]
print(f"primes <= {N}: {len(primes)}; p = 1 mod 6: {sum(p % 6 == 1 for p in primes)}")
