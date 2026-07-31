# Second implementation selection (EXP-MLKEM-009)

## Strict preference order (re-checked at run start)
1. BoringSSL ML-KEM assembly or fixed-bound compare
2. PQClean ML-KEM with fixed-bound hand-written assembly comparison tails
3. Another pinned public fixed-bound target

**strict_fixed_bound_disposition:** `empty_preferred_public_neighborhood`

## Widened order (activated when strict neighborhood empty)
W1. PQClean ml-kem-1024 avx2 verify (optimized_compare_neighborhood)
W2. liboqs 0.12.x ML-KEM verify as optimized-compare peer
W3. Another pinned public optimized CT-compare

**criterion_used:** `widened_optimized_compare`

## Attempts
- **BoringSSL** [strict_fixed_bound]: `rejected_mechanism_mismatch` — ML-KEM decap uses length-parameterized CRYPTO_memcmp; not fixed-bound hand-written vector/SIMD comparison tails. Re-checked at run start; EV-MLKEM-007 / design-time preflight confirmed.
  - evidence: `/tmp/exp-mlkem-007/pre-run/boringssl_mechanism_evidence.txt`
  - commit: `ed1271af005c1def37a100d5924f1c8c8ae7062c`
- **PQClean_avx2_verify** [strict_fixed_bound]: `rejected_mechanism_mismatch` — ml-kem-1024/avx2/verify.c uses len/32 intrinsic loop + scalar remainder; not fixed-bound hand-written comparison tails under strict criterion.
  - evidence: `/tmp/exp-mlkem-007/pre-run/pqclean_mechanism_evidence.txt`
  - commit: `10738d92323117d84bb6202c85722ddfd96dc1d4`
- **PQClean_aarch64_verify** [strict_fixed_bound]: `rejected_mechanism_mismatch` — aarch64/verify.c is a runtime-length scalar loop; backend assembly is NTT/poly, not fixed-bound comparison.
  - evidence: `/tmp/exp-mlkem-007/pre-run/pqclean_mechanism_evidence.txt`
  - commit: `10738d92323117d84bb6202c85722ddfd96dc1d4`
- **mlkem-native** [strict_fixed_bound]: `rejected_mechanism_mismatch` — mlk_ct_memcmp is length-parameterized portable verify.
  - evidence: `/tmp/exp-mlkem-007/pre-run/other_second_impl_attempts.txt`
  - commit: `n/a`
- **aws-lc** [strict_fixed_bound]: `rejected_mechanism_mismatch` — ML-KEM path uses mlkem-native length-parameterized compare.
  - evidence: `/tmp/exp-mlkem-007/pre-run/other_second_impl_attempts.txt`
  - commit: `n/a`
- **PQClean_ml-kem-1024_avx2_verify** [widened_optimized_compare]: `selected` — Default widened peer W1: previously rejected only for strict fixed-bound mismatch; under widened criterion it is an evidenced optimized-compare peer.
  - evidence: `/tmp/exp-mlkem-007/pre-run/pqclean_mechanism_evidence.txt`
  - commit: `10738d92323117d84bb6202c85722ddfd96dc1d4`

## Outcome

Pinned **PQClean** under `criterion_used=widened_optimized_compare` at commit `10738d92323117d84bb6202c85722ddfd96dc1d4`, backend `avx2`.

Mechanism class: `optimized_compare_neighborhood`.

Claim boundary: optional widened peer is laboratory continuity only. GOAL criterion-2 disposition remains `second_impl_unavailable` when strict fixed-bound order is empty. Do not paraphrase as H-MLKEM-004 support or GOAL-MLKEM-002 completion criterion 2.

## Evidence: boringssl_mechanism_evidence.txt

```
BoringSSL ML-KEM comparison mechanism inspection
repo=/tmp/exp-mlkem-007/second-impl/boringssl
commit=ed1271af005c1def37a100d5924f1c8c8ae7062c


VERDICT_STRICT: length-parameterized CRYPTO_memcmp — REJECT under strict_fixed_bound.

```

## Evidence: pqclean_mechanism_evidence.txt

```
# PQClean mechanism evidence (widened laboratory continuity only)
scheme_dir=/tmp/exp-mlkem-007/second-impl/PQClean/crypto_kem/ml-kem-1024/avx2
backend=avx2
commit=10738d92323117d84bb6202c85722ddfd96dc1d4
verify_file=/tmp/exp-mlkem-007/second-impl/PQClean/crypto_kem/ml-kem-1024/avx2/verify.c
VERDICT_STRICT: optimized length-parameterized SIMD verify — REJECT under strict_fixed_bound.
#include "compat.h"
#include "verify.h"
#include <immintrin.h>
#include <stdint.h>
#include <stdlib.h>

/*************************************************
* Name:        PQCLEAN_MLKEM1024_AVX2_verify
*
* Description: Compare two arrays for equality in constant time.
*
* Arguments:   const uint8_t *a: pointer to first byte array
*              const uint8_t *b: pointer to second byte array
*              size_t len: length of the byte arrays
*
* Returns 0 if the byte arrays are equal, 1 otherwise
**************************************************/
int PQCLEAN_MLKEM1024_AVX2_verify(const uint8_t *a, const uint8_t *b, size_t len) {
    size_t i;
    uint64_t r;
    __m256i f, g, h;

    h = _mm256_setzero_si256();
    for (i = 0; i < len / 32; i++) {
        f = _mm256_loadu_si256((__m256i *)&a[32 * i]);
        g = _mm256_loadu_si256((__m256i *)&b[32 * i]);
        f = _mm256_xor_si256(f, g);
        h = _mm256_or_si256(h, f);
    }
    r = 1 - _mm256_testz_si256(h, h);

    a += 32 * i;
    b += 32 * i;
    len -= 32 * i;
    for (i = 0; i < len; i++) {
        r |= a[i] ^ b[i];
    }

    r = (-r) >> 63;
    return r;
}

/*************************************************
* Name:        PQCLEAN_MLKEM1024_AVX2_cmov
*
* Description: Copy len bytes from x to r if b is 1;
*              don't modify x if b is 0. Requires b to be in {0,1};
*              assumes two's complement representation of negative integers.
*              Runs in constant time.
*
* Arguments:   uint8_t *r: pointer to output byte array
*              const uint8_t *x: pointer to input byte array
*              size_t len: Amount of bytes to be copied
*              uint8_t b: Condition bit; has to be in {0,1}
**************************************************/
void PQCLEAN_MLKEM1024_AVX2_cmov(uint8_t *restrict r, const uint8_t *x, size_t len, uint8_t b) {
    size_t i;
    __m256i xvec, rvec, bvec;

    PQCLEAN_PREVENT_BRANCH_HACK(b);

```

## Evidence: other_second_impl_attempts.txt

```
mlkem-native mlk_ct_memcmp
pattern=for (i = 0; i < len; i++)
VERDICT: REJECT under strict_fixed_bound — length-parameterized portable verify.

aws-lc ml_kem
uses mlkem-native ct_memcmp path
VERDICT: REJECT under strict_fixed_bound — not fixed-bound handwritten vector tails.

```
