# Lattice-vector blinding for GLV (C5) against naive blinding

e = 64 bits of blinding, 10000 random scalars per case. **Measured** bit lengths (the doubling count of an interleaved multi-scalar multiplication is the largest coefficient bit length). no leakage model: cost and the distribution of the computed coefficients only.

## Cost

| case | d | n bits | unblinded D (mean/max) | C5 D (mean/max) | naive D (mean/max) | C5 extra bits (mean/max/provable) | e/d | k + r n bits | ratio C5 (pred. d) | ratio naive (pred.) | classical erased |
|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| GOST CryptoPro-B (chain 4+omega, degree 5*5*7) | 2 | 256 | 126.332 / 127 | 158.344 / 159 | 190.326 / 191 | 32.012 / 32 / 31 | 32 | 318.017 | 2.008 (2) | 1.671 (1.667) | 10000/10000 |
| secp256k1 (zeta_3) | 2 | 256 | 126.779 / 128 | 158.785 / 160 | 190.775 / 192 | 32.006 / 32 / 32 | 32 | 318.989 | 2.009 (2) | 1.672 (1.667) | 10000/10000 |
| Tom-521 (chain 47+omega, degree 9317) | 2 | 521 | 259.343 / 260 | 291.336 / 292 | 323.331 / 324 | 31.993 / 32 / 31 | 32 | 584.016 | 2.005 (2) | 1.806 (1.803) | 10000/10000 |
| FourQ (4-D: 1, phi, psi, phi psi) | 4 | 246 | 60.709 / 62 | 76.722 / 78 | 124.727 / 126 | 16.013 / 16 / 15 | 16 | 308.498 | 4.021 (4) | 2.473 (2.47) | 10000/10000 |

Every blinded vector reconstructs k mod n: GOST CryptoPro-B (chain 4+omega, degree 5*5*7): True; secp256k1 (zeta_3): True; Tom-521 (chain 47+omega, degree 9317): True; FourQ (4-D: 1, phi, psi, phi psi): True

On points: GOST CryptoPro-B (chain 4+omega, degree 5*5*7): {'points': 2, 'samples': 6, 'ok': True}; secp256k1 (zeta_3): {'points': 1, 'samples': 6, 'ok': True}; FourQ (4-D: 1, phi, psi, phi psi): {'points': 1, 'samples': 6, 'ok': True}

## Min-entropy of the top bits (given k)

| case | lambda_1^inf bits | window bits >= s0: H_inf | blinding window B_j | top bits/coeff | N(B) | bound e - log2 N(B) | exact at e = 16 (min over k) | deficit | killed (< e - 4) |
|:--|--:|--:|:--|:--|--:|--:|--:|--:|:--|
| GOST CryptoPro-B (chain 4+omega, degree 5*5*7) | 128 | 64 (exact) | [127, 127] | [33, 33] | 1 | 64.0 | 16.0 / 16 | 0.0 | False |
| secp256k1 (zeta_3) | 128 | 64 (exact) | [128, 128] | [33, 33] | 3 | 62.415 | 15.0 / 16 | 1.0 | False |
| Tom-521 (chain 47+omega, degree 9317) | 261 | 64 (exact) | [260, 260] | [33, 33] | 1 | 64.0 | 16.0 / 16 | 0.0 | False |
| FourQ (4-D: 1, phi, psi, phi psi) | 61 | 64 (exact) | [62, 61, 61, 62] | [17, 17, 17, 17] | 19 | 59.752 | 14.0 / 16 | 2.0 | False |

## Per-coefficient top bits (sample of 10^4, plug-in min-entropy)

loop_bits = the provable bound (a constant-time loop length); H_inf of (sign, top T bits of |x| below it).

| case | scheme | j | loop bits | P(bitlen = loop) | P(top bit set) | H top1+s | H top2+s | H top4+s | H top4+s at empirical max |
|:--|:--|--:|--:|--:|--:|--:|--:|--:|--:|
| GOST CryptoPro-B (chain 4+omega, degree 5*5*7) | c5 | 0 | 159 | 0.3378 | 0.3378 | 1.587 | 2.554 | 4.468 | 4.468 |
| GOST CryptoPro-B (chain 4+omega, degree 5*5*7) | c5 | 1 | 159 | 0.2475 | 0.2475 | 1.399 | 2.378 | 4.299 | 4.299 |
| GOST CryptoPro-B (chain 4+omega, degree 5*5*7) | naive | 0 | 191 | 0.3338 | 0.3338 | 1.567 | 2.563 | 4.493 | 4.493 |
| GOST CryptoPro-B (chain 4+omega, degree 5*5*7) | naive | 1 | 191 | 0.2444 | 0.2444 | 1.397 | 2.381 | 4.322 | 4.322 |
| GOST CryptoPro-B (chain 4+omega, degree 5*5*7) | classical k + r n (no GLV) | 0 | 319 | 0.4975 | 0.4975 | 0.993 | 1.966 | 3.88 |  |
| secp256k1 (zeta_3) | c5 | 0 | 160 | 0.095 | 0.095 | 1.126 | 2.1 | 4.023 | 4.023 |
| secp256k1 (zeta_3) | c5 | 1 | 160 | 0.01 | 0.01 | 1.0 | 1.82 | 3.749 | 3.749 |
| secp256k1 (zeta_3) | naive | 0 | 192 | 0.0884 | 0.0884 | 1.109 | 2.1 | 4.007 | 4.007 |
| secp256k1 (zeta_3) | naive | 1 | 192 | 0.0102 | 0.0102 | 1.011 | 1.844 | 3.786 | 3.786 |
| secp256k1 (zeta_3) | classical k + r n (no GLV) | 0 | 320 | 0.4995 | 0.4995 | 0.999 | 1.957 | 3.9 |  |
| Tom-521 (chain 47+omega, degree 9317) | c5 | 0 | 292 | 0.1927 | 0.1927 | 1.291 | 2.287 | 4.219 | 4.219 |
| Tom-521 (chain 47+omega, degree 9317) | c5 | 1 | 292 | 0.3863 | 0.3863 | 1.704 | 2.664 | 4.594 | 4.594 |
| Tom-521 (chain 47+omega, degree 9317) | naive | 0 | 324 | 0.1822 | 0.1822 | 1.285 | 2.281 | 4.224 | 4.224 |
| Tom-521 (chain 47+omega, degree 9317) | naive | 1 | 324 | 0.3941 | 0.3941 | 1.709 | 2.671 | 4.573 | 4.573 |
| Tom-521 (chain 47+omega, degree 9317) | classical k + r n (no GLV) | 0 | 585 | 0.4965 | 0.4965 | 0.99 | 1.989 | 3.95 |  |
| FourQ (4-D: 1, phi, psi, phi psi) | c5 | 0 | 78 | 0.0151 | 0.0151 | 1.011 | 1.415 | 3.242 | 3.242 |
| FourQ (4-D: 1, phi, psi, phi psi) | c5 | 1 | 77 | 0.1285 | 0.1285 | 1.192 | 1.953 | 3.889 | 3.889 |
| FourQ (4-D: 1, phi, psi, phi psi) | c5 | 2 | 77 | 0.3069 | 0.3069 | 1.489 | 2.484 | 4.417 | 4.417 |
| FourQ (4-D: 1, phi, psi, phi psi) | c5 | 3 | 78 | 0.0219 | 0.0219 | 1.01 | 1.532 | 3.326 | 3.326 |
| FourQ (4-D: 1, phi, psi, phi psi) | naive | 0 | 126 | 0.014 | 0.014 | 1.014 | 1.438 | 3.222 | 3.222 |
| FourQ (4-D: 1, phi, psi, phi psi) | naive | 1 | 125 | 0.1296 | 0.1296 | 1.198 | 1.929 | 3.786 | 3.786 |
| FourQ (4-D: 1, phi, psi, phi psi) | naive | 2 | 125 | 0.3158 | 0.3158 | 1.518 | 2.506 | 4.43 | 4.43 |
| FourQ (4-D: 1, phi, psi, phi psi) | naive | 3 | 126 | 0.0222 | 0.0222 | 1.019 | 1.573 | 3.329 | 3.329 |
| FourQ (4-D: 1, phi, psi, phi psi) | classical k + r n (no GLV) | 0 | 310 | 0.2343 | 0.2343 | 0.385 | 1.361 | 3.32 |  |

## Extra bits against e (2000 scalars each)

| case | e | e/d | extra mean | extra max |
|:--|--:|--:|--:|--:|
| secp256k1 (zeta_3) | 16 | 8 | 8.023 | 8 |
| secp256k1 (zeta_3) | 32 | 16 | 15.968 | 16 |
| secp256k1 (zeta_3) | 64 | 32 | 32.002 | 32 |
| secp256k1 (zeta_3) | 128 | 64 | 64.007 | 64 |
| FourQ (4-D: 1, phi, psi, phi psi) | 16 | 4 | 4.001 | 4 |
| FourQ (4-D: 1, phi, psi, phi psi) | 32 | 8 | 7.989 | 8 |
| FourQ (4-D: 1, phi, psi, phi psi) | 64 | 16 | 16.023 | 16 |
| FourQ (4-D: 1, phi, psi, phi psi) | 128 | 32 | 32.002 | 32 |
