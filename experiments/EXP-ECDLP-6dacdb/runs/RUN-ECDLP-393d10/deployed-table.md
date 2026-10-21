| curve | special | l bits | k_actual | rho log2 | k* GNFS | k* exTNFS | k* SNFS/STNFS | order check |
|---|---|---|---|---|---|---|---|---|
| Curve25519 | True | 253 | > 1000000 | 125.8 | 9 | 11 | 16 | True |
| P-256 | True | 256 | > 1000000 | 127.8 | 9 | 12 | 17 | True |
| secp256k1 | True | 256 | > 1000000 | 127.8 | 9 | 12 | 17 | True |
| P-521 | True | 521 | > 1000000 | 260.3 | 27 | 34 | 48 | True |
| Ed448 | True | 446 | > 1000000 | 222.8 | 21 | 27 | 37 | None |
| brainpoolP256r1 | False | 256 | > 1000000 | 127.5 | 9 | 12 | 17 | True |

Constants are recalled and the o(1) is dropped: k* is optimistic for the attacker. k_actual is an exact lower bound from direct exponentiation.