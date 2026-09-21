# Second implementation selection (EXP-MLKEM-004)

## Preference order
1. BoringSSL ML-KEM assembly or fixed-bound compare
2. PQClean ML-KEM avx2 or aarch64 assembly comparison
3. Another pinned public implementation meeting the mechanism criterion

Explicitly insufficient as load-bearing second implementation: length-parameterized portable/intrinsic verify (liboqs 0.12.0 style).

## Attempts
- **BoringSSL**: `rejected_mechanism_mismatch` — ML-KEM decap uses length-parameterized CRYPTO_memcmp; not fixed-bound hand-written vector/SIMD comparison tails.
  - evidence: `/tmp/exp-mlkem-004/pre-run/boringssl_mechanism_evidence.txt`
  - commit: `22a0079b189c391b95689813a41982ce11876f0a`
- **PQClean**: `rejected_mechanism_mismatch` — ml-kem-1024/avx2/verify.c uses len/32 intrinsic loop + scalar remainder (liboqs-style; explicitly insufficient). aarch64/verify.c is a runtime-length scalar loop; backend assembly is NTT/poly, not comparison.
  - evidence: `/tmp/exp-mlkem-004/pre-run/pqclean_mechanism_evidence.txt`
  - commit: `202a8f96315f9ed219387a50f7e40d04af037ea8`
- **mlkem-native**: `rejected_mechanism_mismatch` — mlk_ct_memcmp is length-parameterized portable verify.
  - evidence: `/tmp/exp-mlkem-004/pre-run/other_second_impl_attempts.txt`
  - commit: `n/a`
- **aws-lc**: `rejected_mechanism_mismatch` — ML-KEM path uses mlkem-native length-parameterized compare.
  - evidence: `/tmp/exp-mlkem-004/pre-run/other_second_impl_attempts.txt`
  - commit: `n/a`

## Outcome

`second_impl_unavailable` — preference order exhausted without a buildable mechanism-matched second implementation whose ciphertext comparison uses fixed-bound hand-written vector/SIMD tails.

WolfSSL-only lines may still be reported; isolation across implementations is not claimed.

## Evidence: boringssl_mechanism_evidence.txt

```
BoringSSL ML-KEM comparison mechanism inspection
repo=/tmp/exp-mlkem-004/second-impl/boringssl
commit=22a0079b189c391b95689813a41982ce11876f0a

/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:371:// constant_time_eq_w returns 0xff..f if a == b and 0 otherwise.
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:372:inline crypto_word_t constant_time_eq_w(crypto_word_t a, crypto_word_t b) {
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:376:// constant_time_eq_8 acts like `constant_time_eq_w` but returns an 8-bit
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:378:inline uint8_t constant_time_eq_8(crypto_word_t a, crypto_word_t b) {
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:379:  return (uint8_t)(constant_time_eq_w(a, b));
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:382:// constant_time_eq_int acts like `constant_time_eq_w` but works on int
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:384:inline crypto_word_t constant_time_eq_int(int a, int b) {
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:385:  return constant_time_eq_w((crypto_word_t)(a), (crypto_word_t)(b));
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:388:// constant_time_eq_int_8 acts like `constant_time_eq_int` but returns an 8-bit
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:390:inline uint8_t constant_time_eq_int_8(int a, int b) {
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:391:  return constant_time_eq_8((crypto_word_t)(a), (crypto_word_t)(b));
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/internal.h:845:// Note `OPENSSL_memcmp` is a different function from `CRYPTO_memcmp`.
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/bytestring/cbs.cc:79:  return CRYPTO_memcmp(cbs->data, data, len) == 0;
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/fipsmodule/aes/key_wrap.cc.inc:121:  if (CRYPTO_memcmp(calculated_iv, iv, 8) != 0) {
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/fipsmodule/aes/key_wrap.cc.inc:193:  crypto_word_t ok = constant_time_eq_int(
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/fipsmodule/aes/key_wrap.cc.inc:194:      CRYPTO_memcmp(iv, kPaddingConstant, sizeof(kPaddingConstant)), 0);
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/fipsmodule/aes/key_wrap.cc.inc:198:  ok &= constant_time_eq_w((claimed_len - 1) >> 3, (in_len - 9) >> 3);
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/mem.cc:322:int CRYPTO_memcmp(const void *in_a, const void *in_b, size_t len) {
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/cipher/e_aesctrhmac.cc:246:  if (CRYPTO_memcmp(hmac_result, in_tag.data(), ctx->tag_len) != 0) {
/tmp/exp-mlkem-004/second-impl/boringssl/crypto/hpke/hpke.cc:395:  if (CRYPTO_memcmp(kAllZeros, priv, sizeof(kAllZeros)) == 0) {

VERDICT: length-parameterized CRYPTO_memcmp — REJECT as load-bearing second impl.

```

## Evidence: pqclean_mechanism_evidence.txt

```
PQClean ml-kem-1024 aarch64 verify
file=crypto_kem/ml-kem-1024/aarch64/verify.c
commit=202a8f96315f9ed219387a50f7e40d04af037ea8
bound_type=runtime_length_scalar_loop
assembly_in_backend=NTT/poly only; verify.c is length-parameterized scalar
VERDICT: REJECT — not fixed-bound hand-written vector/SIMD comparison tail.

PQClean ml-kem-1024 avx2 verify
file=crypto_kem/ml-kem-1024/avx2/verify.c
pattern=for (i = 0; i < len / 32; i++) + scalar remainder
VERDICT: REJECT — same length-parameterized intrinsic class as liboqs 0.12.0 (explicitly insufficient).

```

## Evidence: other_second_impl_attempts.txt

```
mlkem-native mlk_ct_memcmp
file=mlkem/src/verify.h
commit=2cf613b6857ccec80b372814a0f387c8facbfea6
pattern=for (i = 0; i < len; i++)
VERDICT: REJECT — length-parameterized portable verify.

aws-lc ml_kem
commit=0f7c326e4fb07488a492550bd92d881b2d528272
uses mlkem-native ct_memcmp path
VERDICT: REJECT — not fixed-bound handwritten vector tails.

```
