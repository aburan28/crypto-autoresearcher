# Second implementation selection (EXP-MLKEM-005)

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
- **BoringSSL** [strict_fixed_bound]: `rejected_mechanism_mismatch` — length-parameterized CRYPTO_memcmp; not fixed-bound hand-written tails. Re-checked at run start (EV-MLKEM-007).
  - evidence: `/tmp/exp-mlkem-005/pre-run/boringssl_mechanism_evidence.txt`
  - commit: `22a0079b189c391b95689813a41982ce11876f0a`
- **PQClean_avx2_verify** [strict_fixed_bound]: `rejected_mechanism_mismatch` — len/32 intrinsic loop + scalar remainder.
  - evidence: `/tmp/exp-mlkem-005/pre-run/pqclean_mechanism_evidence.txt`
  - commit: `202a8f96315f9ed219387a50f7e40d04af037ea8`
- **PQClean_aarch64_verify** [strict_fixed_bound]: `rejected_mechanism_mismatch` — runtime-length scalar loop.
  - evidence: `/tmp/exp-mlkem-005/pre-run/pqclean_mechanism_evidence.txt`
  - commit: `202a8f96315f9ed219387a50f7e40d04af037ea8`
- **mlkem-native** [strict_fixed_bound]: `rejected_mechanism_mismatch` — length-parameterized portable verify.
  - evidence: `/tmp/exp-mlkem-005/pre-run/other_second_impl_attempts.txt`
- **aws-lc** [strict_fixed_bound]: `rejected_mechanism_mismatch` — uses mlkem-native compare path.
  - evidence: `/tmp/exp-mlkem-005/pre-run/other_second_impl_attempts.txt`
- **PQClean_ml-kem-1024_avx2_verify** [widened_optimized_compare]: `selected` — W1 default widened peer; probe rebuilt after initial link failure (missing scheme-local symbol aliases / common objects). 
  - evidence: `/tmp/exp-mlkem-005/pre-run/pqclean_mechanism_evidence.txt`
  - commit: `202a8f96315f9ed219387a50f7e40d04af037ea8`
  - probe: `/tmp/exp-mlkem-005/harness/pqclean-probe`
  - backend: `avx2`

## Outcome

Pinned **PQClean** under `criterion_used=widened_optimized_compare` at commit `202a8f96315f9ed219387a50f7e40d04af037ea8`, backend `avx2`,
path `crypto_kem/ml-kem-1024/avx2/verify.c`.

Mechanism class: `optimized_compare_neighborhood`.

Claim boundary: a null under widened_optimized_compare does not license isolation under strict
fixed-bound-tail of H-MLKEM-004.

## Infrastructure note

First RUN-MLKEM-017 attempt recorded `build_failed_or_wrong_backend` because `pqclean-probe`
failed to link. Probe repair completed before re-execution of RUN-MLKEM-018/019/020. Failed
attempt packages archived under `analysis/failed_attempts/`.

## Evidence: boringssl_mechanism_evidence.txt

```
BoringSSL ML-KEM comparison mechanism inspection
repo=/tmp/exp-mlkem-005/second-impl/boringssl
commit=22a0079b189c391b95689813a41982ce11876f0a


VERDICT_STRICT: length-parameterized CRYPTO_memcmp — REJECT under strict_fixed_bound. Eligible only under widened_optimized_compare if selected as W2/W3, not as silent fixed-bound stand-in.

```

## Evidence: pqclean_mechanism_evidence.txt

```
# PQClean mechanism evidence
scheme_dir=/tmp/exp-mlkem-005/second-impl/PQClean/crypto_kem/ml-kem-1024/avx2
backend=avx2
commit=202a8f96315f9ed219387a50f7e40d04af037ea8
verify_file=/tmp/exp-mlkem-005/second-impl/PQClean/crypto_kem/ml-kem-1024/avx2/verify.c
--- head of verify ---
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

    bvec = _mm256_set1_epi64x(-(uint64_t)b);
    for (i = 0; i < len / 32; i++) {
        rvec = _mm256_loadu_si256((__m256i *)&r[32 * i]);
        xvec = _mm256_loadu_si256((__m256i *)&x[32 * i]);
        rvec = _mm256_blendv_epi8(rvec, xvec, bvec);
        _mm256_storeu_si256((__m256i *)&r[32 * i], rvec);
    }

    r += 32 * i;
    x += 32 * i;
    len -= 32 * i;
    for (i = 0; i < len; i++) {
        r[i] ^= -b & (x[i] ^ r[i]);
    }
}
--- bound / vector markers ---
48:*              assumes two's complement representation of negative integers.

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
