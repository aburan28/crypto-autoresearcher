"""B8/B4 check for crypto:papers/lll-degeneracy-note failure mode A: which
256-bit group orders overflow f64 at n^4 (the Gram-Schmidt norm scale the
repo's own note blames)? Exact rational comparison, no floating point."""
from fractions import Fraction
import sys

ORDERS = {  # standard group orders (SEC 2, FIPS 186-4, RFC 5639)
    "secp256k1": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
    "P-256": 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
    "brainpoolP256r1": 0xA9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7,
}
for name, n in ORDERS.items():
    print(f"{name:16} n^4 > f64::MAX: {Fraction(n) ** 4 > Fraction(sys.float_info.max)}")
