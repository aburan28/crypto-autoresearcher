/* collide.c -- TASK-20260802-4500d4 independent counting engine.
 *
 * Written from scratch for this task. BATCH-002's cnt.c was READ to learn what
 * object is measured (byte order, coset layout, projection index convention,
 * C1 round convention) and to fix the same object; no line of it was copied,
 * and it is neither compiled nor executed by this task.
 *
 * DELIBERATE DESIGN DIFFERENCES from cnt.c, so that a shared bug is less
 * likely:
 *   - Parallelism: cnt.c partitions the VALUE space and makes EVERY thread scan
 *     the whole 2^32 input, incrementing only its own value slice of a SHARED
 *     array. Here each thread owns a whole value WINDOW with a PRIVATE counter
 *     array; threads never touch each other's memory. Windows are handed out
 *     from an atomic work queue.
 *   - Input enumeration: cnt.c walks a single 32-bit counter and masks bytes out
 *     of it. Here the coset is walked as four explicit nested loops over the
 *     four free diagonal bytes, with the first-round T-table lookups of the
 *     three outer bytes hoisted out of the inner loop. That is a different
 *     traversal order and a different arithmetic path to the same 2^32 inputs.
 *   - Counters are uint16 with two independent overflow detectors (per-window
 *     conservation of increments, and max_occ < 65535).
 *
 * Object (same as cnt.c): full 2^32 coset of D_0 = state bytes {0,5,10,15},
 * r-round AES-shaped SPN, C1 convention (final round has no mixing layer),
 * configurable GF(2^8) mixing matrix M with M[row][col] row-major from hex,
 * projection pi_{j0}(c) = bytes at ID_{j0} = {4*((j0-t) mod 4)+t : t=0..3} with
 * byte t at bit 8t. Reports occupancy histogram, N, n = sum_v C(m_v,2), and the
 * cross-check n_alt = (sum_v m_v^2 - N)/2.
 *
 * No RNG inside; every parameter comes from the command line.
 *
 * usage: collide <r> <j0> <key32hex> <base32hex> <matrix32hex> <winbits> <threads>
 *        collide block <r> <key32hex> <matrix32hex> <pt32hex>
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <sys/mman.h>
#include <time.h>

static const uint8_t SB[256] = {
0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16};

/* GF(2^8) multiply, modulus 0x11b, written as a shift-and-add loop. */
static uint8_t gf(uint8_t a, uint8_t b)
{
    uint8_t p = 0;
    while (b) {
        if (b & 1) p ^= a;
        b >>= 1;
        uint8_t carry = a & 0x80;
        a = (uint8_t)(a << 1);
        if (carry) a ^= 0x1b;
    }
    return p;
}

static int R, J0, NTHREADS, WINBITS;
static uint32_t RK[11][4];       /* round keys, column words */
static uint32_t BASECOL[4];      /* fixed 12 bytes of the coset, column words */
static uint32_t TT[4][256];      /* TT[j][x] = column M[:,j] * SB[x], packed */
static uint64_t ENTRIES;         /* counters per window = 2^(32-WINBITS) */
static uint32_t IDXMASK;
static int NWIN;

#define HB 65536
static uint64_t GH[HB];          /* global occupancy histogram */
static uint64_t GN;              /* total increments */
static int INTEGRITY_FAIL;       /* set if any window fails conservation */
static pthread_mutex_t MERGE = PTHREAD_MUTEX_INITIALIZER;
static int NEXTWIN;

static void hexbytes(const char *h, uint8_t *o, int n)
{
    for (int i = 0; i < n; i++) {
        unsigned v = 0;
        if (sscanf(h + 2 * i, "%2x", &v) != 1) { fprintf(stderr, "bad hex\n"); exit(2); }
        o[i] = (uint8_t)v;
    }
}

/* AES-128 key schedule; expanded into column words per round. */
static void schedule(const uint8_t *key)
{
    uint8_t w[176];
    memcpy(w, key, 16);
    uint8_t rc = 1;
    for (int i = 4; i < 44; i++) {
        uint8_t t[4] = { w[4*i-4], w[4*i-3], w[4*i-2], w[4*i-1] };
        if (i % 4 == 0) {
            uint8_t s = t[0];
            t[0] = (uint8_t)(SB[t[1]] ^ rc);
            t[1] = SB[t[2]];
            t[2] = SB[t[3]];
            t[3] = SB[s];
            rc = gf(rc, 2);
        }
        for (int j = 0; j < 4; j++) w[4*i+j] = w[4*(i-4)+j] ^ t[j];
    }
    for (int r = 0; r <= 10; r++)
        for (int c = 0; c < 4; c++)
            RK[r][c] = (uint32_t)w[16*r+4*c]
                     | ((uint32_t)w[16*r+4*c+1] << 8)
                     | ((uint32_t)w[16*r+4*c+2] << 16)
                     | ((uint32_t)w[16*r+4*c+3] << 24);
}

/* One full-mixing round on the four column words. */
static inline void round_mix(uint32_t *c, int r)
{
    uint32_t d0, d1, d2, d3;
    d0 = TT[0][ c[0]        & 0xff] ^ TT[1][(c[1] >>  8) & 0xff]
       ^ TT[2][(c[2] >> 16) & 0xff] ^ TT[3][(c[3] >> 24) & 0xff];
    d1 = TT[0][ c[1]        & 0xff] ^ TT[1][(c[2] >>  8) & 0xff]
       ^ TT[2][(c[3] >> 16) & 0xff] ^ TT[3][(c[0] >> 24) & 0xff];
    d2 = TT[0][ c[2]        & 0xff] ^ TT[1][(c[3] >>  8) & 0xff]
       ^ TT[2][(c[0] >> 16) & 0xff] ^ TT[3][(c[1] >> 24) & 0xff];
    d3 = TT[0][ c[3]        & 0xff] ^ TT[1][(c[0] >>  8) & 0xff]
       ^ TT[2][(c[1] >> 16) & 0xff] ^ TT[3][(c[2] >> 24) & 0xff];
    c[0] = d0 ^ RK[r][0]; c[1] = d1 ^ RK[r][1];
    c[2] = d2 ^ RK[r][2]; c[3] = d3 ^ RK[r][3];
}

/* Final round: SubBytes + ShiftRows + AddRoundKey, no mixing (C1). */
static inline void round_last(uint32_t *c)
{
    uint32_t d0, d1, d2, d3;
    d0 = (uint32_t)SB[ c[0]        & 0xff]
       | ((uint32_t)SB[(c[1] >>  8) & 0xff] <<  8)
       | ((uint32_t)SB[(c[2] >> 16) & 0xff] << 16)
       | ((uint32_t)SB[(c[3] >> 24) & 0xff] << 24);
    d1 = (uint32_t)SB[ c[1]        & 0xff]
       | ((uint32_t)SB[(c[2] >>  8) & 0xff] <<  8)
       | ((uint32_t)SB[(c[3] >> 16) & 0xff] << 16)
       | ((uint32_t)SB[(c[0] >> 24) & 0xff] << 24);
    d2 = (uint32_t)SB[ c[2]        & 0xff]
       | ((uint32_t)SB[(c[3] >>  8) & 0xff] <<  8)
       | ((uint32_t)SB[(c[0] >> 16) & 0xff] << 16)
       | ((uint32_t)SB[(c[1] >> 24) & 0xff] << 24);
    d3 = (uint32_t)SB[ c[3]        & 0xff]
       | ((uint32_t)SB[(c[0] >>  8) & 0xff] <<  8)
       | ((uint32_t)SB[(c[1] >> 16) & 0xff] << 16)
       | ((uint32_t)SB[(c[2] >> 24) & 0xff] << 24);
    c[0] = d0 ^ RK[R][0]; c[1] = d1 ^ RK[R][1];
    c[2] = d2 ^ RK[R][2]; c[3] = d3 ^ RK[R][3];
}

static inline uint32_t project(const uint32_t *c)
{
    return ( c[ J0      & 3] & 0x000000ffu)
         | ( c[(J0 - 1) & 3] & 0x0000ff00u)
         | ( c[(J0 - 2) & 3] & 0x00ff0000u)
         | ( c[(J0 - 3) & 3] & 0xff000000u);
}

static void encrypt_block(uint32_t *c)
{
    for (int i = 0; i < 4; i++) c[i] ^= RK[0][i];
    for (int r = 1; r < R; r++) round_mix(c, r);
    round_last(c);
}

/* Scan the whole coset once, counting only values in window `win`. */
static void scan_window(int win, uint16_t *cnt, uint64_t *inwin_out)
{
    uint64_t inwin = 0;
    const uint32_t k0 = RK[0][0], k1 = RK[0][1], k2 = RK[0][2], k3 = RK[0][3];
    /* free diagonal bytes: state byte 0 (col0 row0), 5 (col1 row1),
       10 (col2 row2), 15 (col3 row3) */
    const uint32_t b0 = (BASECOL[0] & ~0x000000ffu) ^ k0;
    const uint32_t b1 = (BASECOL[1] & ~0x0000ff00u) ^ k1;
    const uint32_t b2 = (BASECOL[2] & ~0x00ff0000u) ^ k2;
    const uint32_t b3 = (BASECOL[3] & ~0xff000000u) ^ k3;

    for (unsigned x3 = 0; x3 < 256; x3++) {
        uint32_t c3v = b3 ^ ((uint32_t)x3 << 24);
        /* first mixing round, contributions of the three outer free bytes and
           of the fixed bytes, hoisted out of the inner loop */
        for (unsigned x2 = 0; x2 < 256; x2++) {
            uint32_t c2v = b2 ^ ((uint32_t)x2 << 16);
            for (unsigned x1 = 0; x1 < 256; x1++) {
                uint32_t c1v = b1 ^ ((uint32_t)x1 << 8);
                /* precompute the parts of round 1 that do not depend on x0 */
                uint32_t p0 = TT[1][(c1v >>  8) & 0xff] ^ TT[2][(c2v >> 16) & 0xff]
                            ^ TT[3][(c3v >> 24) & 0xff] ^ RK[1][0];
                uint32_t q1 = TT[0][ c1v        & 0xff] ^ TT[1][(c2v >>  8) & 0xff]
                            ^ TT[2][(c3v >> 16) & 0xff] ^ RK[1][1];
                uint32_t q2 = TT[0][ c2v        & 0xff] ^ TT[1][(c3v >>  8) & 0xff]
                            ^ TT[3][(c1v >> 24) & 0xff] ^ RK[1][2];
                uint32_t q3 = TT[0][ c3v        & 0xff] ^ TT[2][(c1v >> 16) & 0xff]
                            ^ TT[3][(c2v >> 24) & 0xff] ^ RK[1][3];
                for (unsigned x0 = 0; x0 < 256; x0++) {
                    uint32_t c0v = b0 ^ (uint32_t)x0;
                    uint32_t c[4];
                    if (R > 1) {
                        c[0] = p0 ^ TT[0][ c0v        & 0xff];
                        c[1] = q1 ^ TT[3][(c0v >> 24) & 0xff];
                        c[2] = q2 ^ TT[2][(c0v >> 16) & 0xff];
                        c[3] = q3 ^ TT[1][(c0v >>  8) & 0xff];
                        for (int r = 2; r < R; r++) round_mix(c, r);
                        round_last(c);
                    } else {
                        c[0] = c0v; c[1] = c1v; c[2] = c2v; c[3] = c3v;
                        round_last(c);
                    }
                    uint32_t v = project(c);
                    if (WINBITS == 0 || (uint32_t)(v >> (32 - WINBITS)) == (uint32_t)win) {
                        cnt[v & IDXMASK]++;
                        inwin++;
                    }
                }
            }
        }
    }
    *inwin_out = inwin;
}

static void *worker(void *unused)
{
    (void)unused;
    size_t bytes = (size_t)ENTRIES * sizeof(uint16_t);
    for (;;) {
        int win;
        pthread_mutex_lock(&MERGE);
        win = NEXTWIN < NWIN ? NEXTWIN++ : -1;
        pthread_mutex_unlock(&MERGE);
        if (win < 0) break;

        uint16_t *cnt = mmap(NULL, bytes, PROT_READ | PROT_WRITE,
                             MAP_PRIVATE | MAP_ANONYMOUS | MAP_NORESERVE, -1, 0);
        if (cnt == MAP_FAILED) { perror("mmap"); exit(3); }
        madvise(cnt, bytes, MADV_HUGEPAGE);

        uint64_t inwin = 0;
        scan_window(win, cnt, &inwin);

        uint64_t *h = calloc(HB, sizeof(uint64_t));
        if (!h) { perror("calloc"); exit(3); }
        for (uint64_t i = 0; i < ENTRIES; i++) h[cnt[i]]++;
        munmap(cnt, bytes);

        uint64_t wsum = 0;
        for (uint64_t b = 0; b < HB; b++) wsum += h[b] * b;

        pthread_mutex_lock(&MERGE);
        if (wsum != inwin) INTEGRITY_FAIL = 1;   /* wrap or lost update */
        for (uint64_t b = 0; b < HB; b++) GH[b] += h[b];
        GN += inwin;
        pthread_mutex_unlock(&MERGE);
        free(h);
    }
    return NULL;
}

int main(int argc, char **argv)
{
    if (argc >= 2 && strcmp(argv[1], "block") == 0) {
        if (argc < 6) { fprintf(stderr, "usage: collide block r keyhex matrixhex pthex\n"); return 2; }
        uint8_t key[16], mm[16], pt[16];
        R = atoi(argv[2]);
        hexbytes(argv[3], key, 16); hexbytes(argv[4], mm, 16); hexbytes(argv[5], pt, 16);
        for (int j = 0; j < 4; j++)
            for (int x = 0; x < 256; x++) {
                uint32_t w = 0;
                for (int i = 0; i < 4; i++) w |= (uint32_t)gf(mm[4*i+j], SB[x]) << (8*i);
                TT[j][x] = w;
            }
        schedule(key);
        uint32_t c[4];
        for (int i = 0; i < 4; i++)
            c[i] = (uint32_t)pt[4*i] | ((uint32_t)pt[4*i+1] << 8)
                 | ((uint32_t)pt[4*i+2] << 16) | ((uint32_t)pt[4*i+3] << 24);
        encrypt_block(c);
        printf("{\"ct\":\"");
        for (int i = 0; i < 4; i++)
            for (int b = 0; b < 4; b++) printf("%02x", (unsigned)((c[i] >> (8*b)) & 0xff));
        printf("\"}\n");
        return 0;
    }

    if (argc < 8) {
        fprintf(stderr, "usage: collide r j0 keyhex basehex matrixhex winbits threads\n");
        return 2;
    }
    R = atoi(argv[1]); J0 = atoi(argv[2]);
    uint8_t key[16], base[16], mm[16];
    hexbytes(argv[3], key, 16); hexbytes(argv[4], base, 16); hexbytes(argv[5], mm, 16);
    WINBITS = atoi(argv[6]); NTHREADS = atoi(argv[7]);
    if (R < 1 || R > 10 || J0 < 0 || J0 > 3 || WINBITS < 0 || WINBITS > 8
        || NTHREADS < 1 || NTHREADS > 8) { fprintf(stderr, "bad args\n"); return 2; }

    schedule(key);
    for (int c = 0; c < 4; c++)
        BASECOL[c] = (uint32_t)base[4*c] | ((uint32_t)base[4*c+1] << 8)
                   | ((uint32_t)base[4*c+2] << 16) | ((uint32_t)base[4*c+3] << 24);
    for (int j = 0; j < 4; j++)
        for (int x = 0; x < 256; x++) {
            uint32_t w = 0;
            for (int i = 0; i < 4; i++) w |= (uint32_t)gf(mm[4*i+j], SB[x]) << (8*i);
            TT[j][x] = w;
        }

    NWIN = 1 << WINBITS;
    ENTRIES = 1ull << (32 - WINBITS);
    IDXMASK = (uint32_t)(ENTRIES - 1);
    NEXTWIN = 0;

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    pthread_t th[8];
    for (int i = 0; i < NTHREADS; i++) pthread_create(&th[i], NULL, worker, NULL);
    for (int i = 0; i < NTHREADS; i++) pthread_join(th[i], NULL);
    clock_gettime(CLOCK_MONOTONIC, &t1);

    unsigned __int128 npair = 0, sq = 0;
    uint64_t maxocc = 0;
    for (uint64_t b = 0; b < HB; b++) {
        if (!GH[b]) continue;
        npair += (unsigned __int128)GH[b] * ((uint64_t)b * (b - 1) / 2);
        sq    += (unsigned __int128)GH[b] * ((uint64_t)b * b);
        maxocc = b;
    }
    unsigned __int128 alt = (sq - (unsigned __int128)GN) / 2;
    double secs = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);

    printf("{\"engine\":\"collide.c/TASK-20260802-4500d4\",\"r\":%d,\"j0\":%d,"
           "\"counter_bits\":16,\"winbits\":%d,\"threads\":%d,",
           R, J0, WINBITS, NTHREADS);
    printf("\"key\":\"%s\",\"base\":\"%s\",\"matrix\":\"%s\",", argv[3], argv[4], argv[5]);
    printf("\"N\":%llu,\"N_ok\":%s,", (unsigned long long)GN,
           GN == (1ull << 32) ? "true" : "false");
    printf("\"n\":%llu,\"n_alt\":%llu,\"n_agree\":%s,",
           (unsigned long long)npair, (unsigned long long)alt,
           npair == alt ? "true" : "false");
    printf("\"n_mod8\":%llu,\"n_mod16\":%llu,\"max_occ\":%llu,",
           (unsigned long long)(npair % 8), (unsigned long long)(npair % 16),
           (unsigned long long)maxocc);
    printf("\"conservation_ok\":%s,\"max_occ_below_ceiling\":%s,"
           "\"counter_integrity_ok\":%s,",
           INTEGRITY_FAIL ? "false" : "true",
           maxocc < 65535 ? "true" : "false",
           (!INTEGRITY_FAIL && maxocc < 65535) ? "true" : "false");
    printf("\"occ_hist\":{");
    int first = 1;
    for (uint64_t b = 0; b < HB; b++)
        if (GH[b]) { printf("%s\"%llu\":%llu", first ? "" : ",",
                            (unsigned long long)b, (unsigned long long)GH[b]); first = 0; }
    printf("},\"seconds\":%.2f}\n", secs);
    return 0;
}
