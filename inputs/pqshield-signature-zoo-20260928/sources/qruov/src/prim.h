#ifndef PRIM_H
#define PRIM_H

#include <stddef.h>
#include <stdint.h>
#include <openssl/evp.h>

// OpenSSL < 3.3 does not provide EVP_DigestSqueeze().
// For testing, defining PRIM_FORCE_NO_EVP_DIGEST_SQUEEZE forces
// the fallback path even when the API exists.
#if defined(PRIM_FORCE_NO_EVP_DIGEST_SQUEEZE)
#define PRIM_NO_EVP_DIGEST_SQUEEZE 1
#else
#define PRIM_NO_EVP_DIGEST_SQUEEZE (!OPENSSL_VERSION_PREREQ(3, 3))
#endif // PRIM_FORCE_NO_EVP_DIGEST_SQUEEZE

typedef struct shake256 {
    EVP_MD_CTX *md_ctx;
#if PRIM_NO_EVP_DIGEST_SQUEEZE
    size_t offset;
    size_t cache_size;
    uint8_t *cache;
#endif // PRIM_NO_EVP_DIGEST_SQUEEZE
} shake256;

typedef struct shake128 {
    EVP_MD_CTX *md_ctx;
} shake128;

typedef struct aes128 {
#if defined(PRIM_AES_BACKEND_X86AESNI)
    // AES-128 round keys (11 x 16 bytes), 16-byte aligned for AES-NI loads.
    uint8_t round_keys[11 * 16] __attribute__((aligned(16)));
#else
    EVP_CIPHER_CTX *cipher_ctx;
#endif // PRIM_AES_BACKEND_X86AESNI
} aes128;

// Requires:
//   - message := update* -> digestfinal | update* -> squeeze*
//   - call order: init -> message -> (reset -> message)* -> free
void shake256_init(shake256 *ctx);
void shake256_reset(shake256 *ctx);
void shake256_update(shake256 *ctx, const uint8_t *data, size_t size);
void shake256_digestfinal(shake256 *ctx, uint8_t *dst, size_t size);
void shake256_squeeze(shake256 *ctx, uint8_t *dst, size_t size);
void shake256_free(shake256 *ctx);

// Requires: call order is init -> update* -> digestfinal -> free
void shake128_init(shake128 *ctx);
void shake128_update(shake128 *ctx, const uint8_t *data, size_t size);
void shake128_digestfinal(shake128 *ctx, uint8_t *dst, size_t size);
void shake128_free(shake128 *ctx);

// Requires: call order is init -> stream* -> free
void aes128ctr_init(aes128 *ctx, const uint8_t key[16]);
void aes128ctr_stream(aes128 *ctx, const uint8_t iv[8], uint8_t *dst, size_t size);
void aes128ctr_free(aes128 *ctx);

#endif // PRIM_H
