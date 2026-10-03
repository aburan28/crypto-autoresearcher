#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <openssl/crypto.h>
#include <openssl/evp.h>
#include "prim.h"
#if defined(PRIM_AES_BACKEND_X86AESNI)
#include "x86aesni.h"
#endif // PRIM_AES_BACKEND_X86AESNI

#if PRIM_NO_EVP_DIGEST_SQUEEZE
static void shake256_clear_cache(shake256 *ctx)
{
    if (ctx->cache != NULL) {
        OPENSSL_cleanse(ctx->cache, ctx->cache_size);
        free(ctx->cache);
        ctx->cache = NULL;
    }
    ctx->offset = 0;
    ctx->cache_size = 0;
}
#endif // PRIM_NO_EVP_DIGEST_SQUEEZE

void shake256_init(shake256 *ctx)
{
    ctx->md_ctx = EVP_MD_CTX_new();
    if (ctx->md_ctx == NULL) abort();
#if PRIM_NO_EVP_DIGEST_SQUEEZE
    ctx->offset = 0;
    ctx->cache_size = 0;
    ctx->cache = NULL;
#endif // PRIM_NO_EVP_DIGEST_SQUEEZE
    shake256_reset(ctx);
}

void shake256_reset(shake256 *ctx)
{
#if PRIM_NO_EVP_DIGEST_SQUEEZE
    shake256_clear_cache(ctx);
#endif // PRIM_NO_EVP_DIGEST_SQUEEZE
    if (EVP_DigestInit_ex2(ctx->md_ctx, EVP_shake256(), NULL) != 1) abort();
}

void shake256_update(shake256 *ctx, const uint8_t *data, size_t size)
{
    if (EVP_DigestUpdate(ctx->md_ctx, data, size) != 1) abort();
#if PRIM_NO_EVP_DIGEST_SQUEEZE
    shake256_clear_cache(ctx);
#endif // PRIM_NO_EVP_DIGEST_SQUEEZE
}

void shake256_digestfinal(shake256 *ctx, uint8_t *dst, size_t size)
{
    if (EVP_DigestFinalXOF(ctx->md_ctx, dst, size) != 1) abort();
}

void shake256_squeeze(shake256 *ctx, uint8_t *dst, size_t size)
{
#if !PRIM_NO_EVP_DIGEST_SQUEEZE
    if (EVP_DigestSqueeze(ctx->md_ctx, dst, size) != 1) abort();
#else
    if (size > SIZE_MAX - ctx->offset) abort();
    size_t total = ctx->offset + size;
    if (total > ctx->cache_size) {
        size_t new_size = ctx->cache_size ? ctx->cache_size : 1088;
        while (new_size < total) {
            if (new_size > SIZE_MAX / 2) {
                new_size = total;
                break;
            }
            new_size <<= 1;
        }
        EVP_MD_CTX *tmp = EVP_MD_CTX_new();
        if (tmp == NULL) abort();
        if (EVP_MD_CTX_copy_ex(tmp, ctx->md_ctx) != 1) {
            EVP_MD_CTX_free(tmp);
            abort();
        }
        uint8_t *new_cache = malloc(new_size);
        if (new_cache == NULL) {
            EVP_MD_CTX_free(tmp);
            abort();
        }
        if (EVP_DigestFinalXOF(tmp, new_cache, new_size) != 1) {
            OPENSSL_cleanse(new_cache, new_size);
            free(new_cache);
            EVP_MD_CTX_free(tmp);
            abort();
        }
        EVP_MD_CTX_free(tmp);
        if (ctx->cache != NULL) {
            OPENSSL_cleanse(ctx->cache, ctx->cache_size);
            free(ctx->cache);
        }
        ctx->cache = new_cache;
        ctx->cache_size = new_size;
    }
    memcpy(dst, &ctx->cache[ctx->offset], size);
    ctx->offset = total;
#endif // PRIM_NO_EVP_DIGEST_SQUEEZE
}

void shake256_free(shake256 *ctx)
{
#if PRIM_NO_EVP_DIGEST_SQUEEZE
    shake256_clear_cache(ctx);
#endif // PRIM_NO_EVP_DIGEST_SQUEEZE
    EVP_MD_CTX_free(ctx->md_ctx);
    ctx->md_ctx = NULL;
}

void shake128_init(shake128 *ctx)
{
    ctx->md_ctx = EVP_MD_CTX_new();
    if (ctx->md_ctx == NULL) abort();
    if (EVP_DigestInit_ex2(ctx->md_ctx, EVP_shake128(), NULL) != 1) abort();
}

void shake128_update(shake128 *ctx, const uint8_t *data, size_t size)
{
    if (EVP_DigestUpdate(ctx->md_ctx, data, size) != 1) abort();
}

void shake128_digestfinal(shake128 *ctx, uint8_t *dst, size_t size)
{
    if (EVP_DigestFinalXOF(ctx->md_ctx, dst, size) != 1) abort();
}

void shake128_free(shake128 *ctx)
{
    EVP_MD_CTX_free(ctx->md_ctx);
    ctx->md_ctx = NULL;
}

#if defined(PRIM_AES_BACKEND_X86AESNI)
void aes128ctr_init(aes128 *ctx, const uint8_t key[16])
{
    AES128_Key_Expansion(ctx->round_keys, key);
}

void aes128ctr_stream(aes128 *ctx, const uint8_t iv[8], uint8_t *dst, size_t size)
{
    const size_t blocks = size / 16u;
    const size_t tail = size % 16u;
    uint8_t nonce[16] = {0};
    memcpy(nonce, iv, 8);

    if (blocks != 0) {
        if (blocks > ULONG_MAX) abort();
        AES128_CTR_Stream(dst, (unsigned long)blocks, ctx->round_keys, nonce, 0);
    }
    if (tail != 0) {
        uint8_t tail_block[16];
        if (blocks > UINT32_MAX) abort();
        AES128_CTR_Stream(tail_block, 1, ctx->round_keys, nonce, (uint32_t)blocks);
        memcpy(dst + (blocks * 16u), tail_block, tail);
    }
}

void aes128ctr_free(aes128 *ctx)
{
    OPENSSL_cleanse(ctx->round_keys, sizeof(ctx->round_keys));
}
#else
void aes128ctr_init(aes128 *ctx, const uint8_t key[16])
{
    ctx->cipher_ctx = EVP_CIPHER_CTX_new();
    if (ctx->cipher_ctx == NULL) abort();
    if (EVP_EncryptInit_ex2(ctx->cipher_ctx, EVP_aes_128_ctr(), key, NULL, NULL) != 1) abort();
}

void aes128ctr_stream(aes128 *ctx, const uint8_t iv[8], uint8_t *dst, size_t size)
{
    uint8_t ctr_iv[16] = {0};
    uint8_t *out = dst;
    size_t remaining = size;

    memcpy(ctr_iv, iv, 8);
    if (EVP_EncryptInit_ex2(ctx->cipher_ctx, NULL, NULL, ctr_iv, NULL) != 1) abort();

    if (size == 0) return;
    memset(dst, 0, size);
    while (remaining != 0) {
        const size_t chunk = remaining > (size_t)INT_MAX ? (size_t)INT_MAX : remaining;
        const int in_size = (int)chunk;
        int out_size = 0;
        if (EVP_EncryptUpdate(ctx->cipher_ctx, out, &out_size, out, in_size) != 1) abort();
        if (out_size != in_size) abort();
        out += chunk;
        remaining -= chunk;
    }
}

void aes128ctr_free(aes128 *ctx)
{
    EVP_CIPHER_CTX_free(ctx->cipher_ctx);
    ctx->cipher_ctx = NULL;
}
#endif // PRIM_AES_BACKEND_X86AESNI
