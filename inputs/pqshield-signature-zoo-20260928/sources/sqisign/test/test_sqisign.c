// SPDX-License-Identifier: Apache-2.0

#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <rng.h>
#include <sig.h>
#include <api.h>
#include <bench_test_arguments.h>
#ifdef TARGET_BIG_ENDIAN
#include <tutil.h>
#endif

static void
print_hex(const unsigned char *hex, int len)
{
    for (int i = 0; i < len; ++i) {
        printf("%02x", hex[i]);
    }
    printf("\n");
}

// Tests that crypto_sign_verify() and crypto_sign_open() reject a wrong signature length, and that they do so before
// reading the signature buffer at all.
//
// Two details ensure that these tests notice if those length checks ever go missing:
//
//  - Every buffer is allocated to exactly the length that is then passed to the function, so a sanitizer flags any read
//    past that length. Writing the tests with one full-size buffer, called with a smaller length, would read from a
//    memory region that is still validly allocated, where nothing would complain.
//
//  - sig is a valid signature over msg. Were it corrupted, every call below would return -1 simply because the
//    signature does not verify, and the length checks could be deleted without a single test failing.
static int
test_invalid_lengths(const unsigned char *sig,
                     const unsigned char *msg,
                     unsigned long long in_msglen,
                     const unsigned char *pk)
{
    // Suffix lengths tried on the oversized cases
    static const unsigned long long suffixes[] = { 1, 16 };

    int res = 0;
    unsigned long long mlen;
    unsigned char *sm = NULL;
    unsigned char *sig_trunc = NULL;
    unsigned char *msg_out = NULL;

    printf("Testing length validation of Open, Verify: %s\n", CRYPTO_ALGNAME);

    // A valid signed message: a detached signature over msg, with msg appended, is exactly what crypto_sign() produces.
    sm = malloc(CRYPTO_BYTES + in_msglen);
    if (!sm) {
        return -1;
    }
    memcpy(sm, sig, CRYPTO_BYTES);
    memcpy(sm + CRYPTO_BYTES, msg, in_msglen);

    // Establish that the inputs are valid, so that every rejection below is attributable to the length alone.
    if (crypto_sign_verify(sig, CRYPTO_BYTES, msg, in_msglen, pk) != 0) {
        printf("crypto_sign_verify rejected a valid signature\n");
        res = -1;
        goto err;
    }

    for (unsigned long long len = 0; len < (unsigned long long)CRYPTO_BYTES; len++) {
        // Undersized detached signature: must be rejected before sig is read.
        sig_trunc = malloc(len ? len : 1);
        if (!sig_trunc) {
            res = -1;
            goto err;
        }
        memcpy(sig_trunc, sig, len);

        if (crypto_sign_verify(sig_trunc, len, msg, in_msglen, pk) != -1) {
            printf("crypto_sign_verify accepted an undersized signature, siglen=%llu\n", len);
            res = -1;
            goto err;
        }

        // Undersized signed message: must be rejected before sm is read, and must clear mlen.
        msg_out = malloc(len ? len : 1);
        if (!msg_out) {
            res = -1;
            goto err;
        }
        memcpy(sig_trunc, sm, len);
        mlen = in_msglen ? in_msglen : 1; // deliberately non-zero

        if (crypto_sign_open(msg_out, &mlen, sig_trunc, len, pk) != -1 || mlen != 0) {
            printf("crypto_sign_open accepted an undersized signed message, smlen=%llu\n", len);
            res = -1;
            goto err;
        }

        free(sig_trunc);
        sig_trunc = NULL;
        free(msg_out);
        msg_out = NULL;
    }

    // Oversized detached signature: signatures are of fixed size, so a valid one followed by appended bytes must be
    // rejected rather than accepted with the suffix ignored. Both a random and an all-zero suffix are tried, the latter
    // being the most benign-looking choice available to a caller.
    for (size_t i = 0; i < sizeof(suffixes) / sizeof(suffixes[0]); i++) {
        unsigned long long extra = suffixes[i];
        unsigned long long len = (unsigned long long)CRYPTO_BYTES + extra;

        sig_trunc = malloc(len);
        if (!sig_trunc) {
            res = -1;
            goto err;
        }
        memcpy(sig_trunc, sig, CRYPTO_BYTES);
        randombytes(sig_trunc + CRYPTO_BYTES, extra);

        if (crypto_sign_verify(sig_trunc, len, msg, in_msglen, pk) != -1) {
            printf("crypto_sign_verify accepted a signature with a random suffix, siglen=%llu\n", len);
            res = -1;
            goto err;
        }

        memset(sig_trunc + CRYPTO_BYTES, 0, extra);
        if (crypto_sign_verify(sig_trunc, len, msg, in_msglen, pk) != -1) {
            printf("crypto_sign_verify accepted a signature with a zero suffix, siglen=%llu\n", len);
            res = -1;
            goto err;
        }

        free(sig_trunc);
        sig_trunc = NULL;
    }

    // The exact boundary: smlen == CRYPTO_BYTES claims a zero-length message, which is a well-formed request but not
    // the message that was signed. Only meaningful when the signed message was not itself empty.
    if (in_msglen > 0) {
        sig_trunc = malloc(CRYPTO_BYTES);
        msg_out = malloc(1);
        if (!sig_trunc || !msg_out) {
            res = -1;
            goto err;
        }
        memcpy(sig_trunc, sm, CRYPTO_BYTES);
        mlen = in_msglen;

        if (crypto_sign_open(msg_out, &mlen, sig_trunc, CRYPTO_BYTES, pk) != -1 || mlen != 0) {
            printf("crypto_sign_open accepted an empty-message claim, smlen=%d\n", CRYPTO_BYTES);
            res = -1;
            goto err;
        }

        free(sig_trunc);
        sig_trunc = NULL;
        free(msg_out);
        msg_out = NULL;
    }

    // Appending bytes to a signed message is not an encoding ambiguity: the suffix is part of the message, so this must
    // fail as a signature over a different message. msg_out is sized exactly to smlen - CRYPTO_BYTES, which the failure
    // path zeroes.
    for (size_t i = 0; i < sizeof(suffixes) / sizeof(suffixes[0]); i++) {
        unsigned long long extra = suffixes[i];
        unsigned long long len = (unsigned long long)CRYPTO_BYTES + in_msglen + extra;

        sig_trunc = malloc(len);
        msg_out = malloc(len - CRYPTO_BYTES);
        if (!sig_trunc || !msg_out) {
            res = -1;
            goto err;
        }
        memcpy(sig_trunc, sm, CRYPTO_BYTES + in_msglen);
        randombytes(sig_trunc + CRYPTO_BYTES + in_msglen, extra);
        mlen = 0;

        if (crypto_sign_open(msg_out, &mlen, sig_trunc, len, pk) != -1 || mlen != 0) {
            printf("crypto_sign_open accepted a signed message with a suffix, smlen=%llu\n", len);
            res = -1;
            goto err;
        }

        free(sig_trunc);
        sig_trunc = NULL;
        free(msg_out);
        msg_out = NULL;
    }

err:
    free(sm);
    free(sig_trunc);
    free(msg_out);
    return res;
}

static int
test_sqisign(unsigned long long in_msglen)
{
    unsigned char *pk = calloc(CRYPTO_PUBLICKEYBYTES, 1);
    unsigned char *sk = calloc(CRYPTO_SECRETKEYBYTES, 1);
    unsigned char *sig = calloc(CRYPTO_BYTES + in_msglen, 1);

    unsigned char *msg = malloc(in_msglen);
    unsigned char *msg_open = malloc(in_msglen);

    unsigned long long msglen = in_msglen;

    randombytes(msg, in_msglen);
    randombytes(msg_open, in_msglen);

    printf("Testing Keygen, Sign, Open: %s\n", CRYPTO_ALGNAME);

    int res = crypto_sign_keypair(pk, sk);
    if (res != 0) {
        res = -1;
        goto err;
    }

    unsigned long long smlen = CRYPTO_BYTES + in_msglen;

    res = crypto_sign(sig, &smlen, msg, in_msglen, sk);
    if (res != 0) {
        res = -1;
        goto err;
    }

    printf("pk: ");
    print_hex(pk, CRYPTO_PUBLICKEYBYTES);
    printf("sk: ");
    print_hex(sk, CRYPTO_SECRETKEYBYTES);
    printf("sm: ");
    print_hex(sig, smlen);

    res = crypto_sign_open(msg_open, &msglen, sig, smlen, pk);
    if (res != 0 || msglen != in_msglen || memcmp(msg_open, msg, msglen) != 0) {
        res = -1;
        goto err;
    }

    randombytes(msg_open, in_msglen);

    sig[0] = ~sig[0];
    res = crypto_sign_open(msg_open, &msglen, sig, smlen, pk);
    if (res != -1) {
        res = -1;
        goto err;
    }

    // Test with `sm` and `m` as the same buffer
    msglen = in_msglen;
    randombytes(msg, in_msglen);
    memcpy(sig, msg, msglen);

    res = crypto_sign(sig, &smlen, sig, in_msglen, sk);
    if (res != 0) {
        res = -1;
        goto err;
    }

    randombytes(msg_open, in_msglen);

    res = crypto_sign_open(msg_open, &msglen, sig, smlen, pk);
    if (res != 0 || msglen != in_msglen || memcmp(msg_open, msg, msglen) != 0) {
        res = -1;
        goto err;
    }

    // Test detached signature API
    randombytes(msg, in_msglen);

    unsigned long long siglen = CRYPTO_BYTES;
    res = crypto_sign_signature(sig, &siglen, msg, in_msglen, sk);
    if (res != 0 || siglen != CRYPTO_BYTES) {
        res = -1;
        goto err;
    }

    res = crypto_sign_verify(sig, siglen, msg, in_msglen, pk);
    if (res != 0) {
        res = -1;
        goto err;
    }

    sig[0] = ~sig[0];
    res = crypto_sign_verify(sig, siglen, msg, in_msglen, pk);
    if (res != -1) {
        res = -1;
        goto err;
    }

    // Test invalid signature lengths. First, restore the valid signature.
    sig[0] = ~sig[0];
    res = test_invalid_lengths(sig, msg, in_msglen, pk);
    if (res != 0) {
        res = -1;
        goto err;
    }

err:
    free(pk);
    free(sk);
    free(sig);
    free(msg);
    free(msg_open);
    return res;
}

int
main(int argc, char *argv[])
{
    uint32_t seed[12] = { 0 };
    int help = 0;
    int seed_set = 0;
    int msglen_set = 0;
    int res = 0;
    unsigned long long msglen = 32;

    for (int i = 1; i < argc; i++) {
        unsigned int _msglen;

        if (!help && strcmp(argv[i], "--help") == 0) {
            help = 1;
            continue;
        }

        if (!seed_set && !parse_seed(argv[i], seed)) {
            seed_set = 1;
            continue;
        }

        if (!msglen_set && sscanf(argv[i], "--msglen=%u", &_msglen) == 1) {
            msglen = (unsigned long long)_msglen;
            msglen_set = 1;
        }
    }

    if (help) {
        printf("Usage: %s [--seed=<seed>]\n", argv[0]);
        printf("Where <seed> is the random seed to be used; if not present, a random seed is "
               "generated\n");
        return 1;
    }

    if (!seed_set) {
        randombytes_select((unsigned char *)seed, sizeof(seed));
    }

    print_seed(seed);

#if defined(TARGET_BIG_ENDIAN)
    for (int i = 0; i < 12; i++) {
        seed[i] = BSWAP32(seed[i]);
    }
#endif

    randombytes_init((unsigned char *)seed, NULL, 256);

    res = test_sqisign(msglen);

    if (res != 0) {
        printf("test failed for %s\n", CRYPTO_ALGNAME);
    }
    return res;
}
