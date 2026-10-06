# QR-UOV Round 3 Reference Implementation

## Security Notice

This is a reference implementation and is not hardened against side-channel attacks. In particular, signing is not constant-time and must not be assumed to resist timing attacks.

## Implementations

- `ref`: straightforward reference C implementation
- `opt`: optimized C implementation (no SIMD intrinsics required)
- `avx2`: AVX2/BMI2-optimized implementation for x86-64 CPUs supporting AVX2

## Requirements

- GNU `make`. On macOS or BSD, install GNU `make` and use `gmake`.
- OpenSSL `libcrypto` `3.0+`. OpenSSL `3.3+` is recommended for `EVP_DigestSqueeze`.

## Usage

Run `make help` for targets and build options. On macOS or BSD, use `gmake help`.

## Round 3 Changes

### Specification

- Adds q127/L10 parameter sets: Level I `(q,v,m,L)=(127,540,60,10)`, Level III `(127,820,90,10)`, and Level V `(127,1040,110,10)`.
- Public-seed expansion uses AES-128-CTR or SHAKE128 from the 128-bit public seed `seed_pk`.
- Secret-key seed expansion uses SHAKE256 from the 256-bit secret seed `seed_sk`.
- `seed_pk` is derived as `SHAKE256(seed_sk || 0x0001)`, and the serialized secret key contains only `seed_sk`.
- Signing fails if the rank of the oil linear system `L` is less than `m - delta`, with `delta = 2` for `q = 127`, `delta = 3` for `q = 31`, and `delta = 4` for `q = 7`.

### Implementation

- The `opt` and `avx2` implementations introduce new optimizations: evaluation-interpolation for key generation, and precomputing signature-dependent terms for verification.
- The `avx2` implementation substantially improves performance over the Round 2 reference implementation.

## Reference

- Amagasa, H., Ueno, R., & Homma, N. (2026). AVX2 Implementation of QR-UOV for Modern x86 Processors. IACR Transactions on Cryptographic Hardware and Embedded Systems, 2026(2), 325-346. https://doi.org/10.46586/tches.v2026.i2.325-346
