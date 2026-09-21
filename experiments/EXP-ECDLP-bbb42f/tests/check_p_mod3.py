import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.sampler import field_prime_for_bits

for bits in (20, 24, 28):
    p = field_prime_for_bits(bits)
    print(f"bits={bits} p={p} p mod 3={p % 3}")
