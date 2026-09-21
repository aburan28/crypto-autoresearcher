/* CPython 3.12-compatible MT19937 + affine EC walk for EXP-ECDLP-420e73 Stage 14.
 *
 * randrange(16) is _randbelow(16): getrandbits(5) until < 16.
 * getrandbits(5) is genrand_int32() >> 27.
 * MT state is copied from Python random.Random.getstate() so seeding stays
 * on the protocol RNG. Affine addition matches stage11_h3_rerandom_16777213.py.
 *
 * out: [status, steps, landing_x_or_-1, first_j, first_j_used_as_step]
 * status: 0 hit, 1 capped, 2 identity, 3 identity_at_start
 */
#include <stdint.h>
#include <string.h>

#define N 624
#define M 397
#define MATRIX_A 0x9908b0dfUL
#define UPPER_MASK 0x80000000UL
#define LOWER_MASK 0x7fffffffUL

typedef struct {
    uint32_t mt[N];
    int index;
} MT;

static uint32_t genrand_int32(MT *self) {
    uint32_t y;
    static const uint32_t mag01[2] = {0x0UL, MATRIX_A};
    uint32_t *mt = self->mt;
    int kk;
    if (self->index >= N) {
        for (kk = 0; kk < N - M; kk++) {
            y = (mt[kk] & UPPER_MASK) | (mt[kk + 1] & LOWER_MASK);
            mt[kk] = mt[kk + M] ^ (y >> 1) ^ mag01[y & 1UL];
        }
        for (; kk < N - 1; kk++) {
            y = (mt[kk] & UPPER_MASK) | (mt[kk + 1] & LOWER_MASK);
            mt[kk] = mt[kk + (M - N)] ^ (y >> 1) ^ mag01[y & 1UL];
        }
        y = (mt[N - 1] & UPPER_MASK) | (mt[0] & LOWER_MASK);
        mt[N - 1] = mt[M - 1] ^ (y >> 1) ^ mag01[y & 1UL];
        self->index = 0;
    }
    y = mt[self->index++];
    y ^= (y >> 11);
    y ^= (y << 7) & 0x9d2c5680UL;
    y ^= (y << 15) & 0xefc60000UL;
    y ^= (y >> 18);
    return y;
}

static uint32_t getrandbits5(MT *self) {
    return genrand_int32(self) >> 27;
}

static int randrange16(MT *self) {
    uint32_t r = getrandbits5(self);
    while (r >= 16u) {
        r = getrandbits5(self);
    }
    return (int)r;
}

static int64_t modinv(int64_t a, int64_t p) {
    int64_t t = 0, newt = 1;
    int64_t r = p, newr = a % p;
    if (newr < 0) {
        newr += p;
    }
    while (newr != 0) {
        int64_t q = r / newr;
        int64_t tmp = newt;
        newt = t - q * newt;
        t = tmp;
        tmp = newr;
        newr = r - q * newr;
        r = tmp;
    }
    if (r > 1) {
        return -1;
    }
    if (t < 0) {
        t += p;
    }
    return t;
}

static inline int in_v(const uint32_t *bits, int64_t x) {
    return (int)((bits[(uint32_t)x >> 5] >> ((uint32_t)x & 31u)) & 1u);
}

/* Return 1 if the sum is the identity, 0 otherwise. */
static int add_aff(int64_t p, int64_t a,
                   int64_t x1, int64_t y1, int inf1,
                   int64_t x2, int64_t y2,
                   int64_t *x3, int64_t *y3) {
    if (inf1) {
        *x3 = x2;
        *y3 = y2;
        return 0;
    }
    int64_t lam;
    if (x1 == x2) {
        int64_t ys = (y1 + y2) % p;
        if (ys < 0) {
            ys += p;
        }
        if (ys == 0) {
            return 1;
        }
        if (y1 == 0) {
            return 1;
        }
        int64_t den = modinv((2 * y1) % p, p);
        int64_t xx = x1 % p;
        if (xx < 0) {
            xx += p;
        }
        int64_t num = ((3 * xx) % p * xx + a) % p;
        if (num < 0) {
            num += p;
        }
        lam = (num * den) % p;
        if (lam < 0) {
            lam += p;
        }
    } else {
        int64_t dx = (x2 - x1) % p;
        if (dx < 0) {
            dx += p;
        }
        int64_t den = modinv(dx, p);
        int64_t dy = (y2 - y1) % p;
        if (dy < 0) {
            dy += p;
        }
        lam = (dy * den) % p;
        if (lam < 0) {
            lam += p;
        }
    }
    int64_t xx = (lam * lam - x1 - x2) % p;
    if (xx < 0) {
        xx += p;
    }
    int64_t yy = (lam * (x1 - xx) - y1) % p;
    if (yy < 0) {
        yy += p;
    }
    *x3 = xx;
    *y3 = yy;
    return 0;
}

void stage14_walk(
    uint32_t *mt, int index,
    int64_t p, int64_t curve_a,
    int64_t *add_x, int64_t *add_y,
    int64_t sx, int64_t sy, int start_inf,
    uint32_t *vbits,
    int64_t cap,
    int64_t *out
) {
    MT rng;
    memcpy(rng.mt, mt, sizeof(rng.mt));
    rng.index = index;
    int first_j = randrange16(&rng);
    out[3] = first_j;
    if (start_inf) {
        out[0] = 3;
        out[1] = 0;
        out[2] = -1;
        out[4] = 0;
        return;
    }
    int64_t rx = sx, ry = sy;
    if (in_v(vbits, rx)) {
        out[0] = 0;
        out[1] = 0;
        out[2] = rx;
        out[4] = 0;
        return;
    }
    int64_t nx, ny;
    int j = first_j;
    if (add_aff(p, curve_a, rx, ry, 0, add_x[j], add_y[j], &nx, &ny)) {
        out[0] = 2;
        out[1] = 1;
        out[2] = -1;
        out[4] = 1;
        return;
    }
    rx = nx;
    ry = ny;
    if (in_v(vbits, rx)) {
        out[0] = 0;
        out[1] = 1;
        out[2] = rx;
        out[4] = 1;
        return;
    }
    for (int64_t step = 2; step <= cap; step++) {
        j = randrange16(&rng);
        if (add_aff(p, curve_a, rx, ry, 0, add_x[j], add_y[j], &nx, &ny)) {
            out[0] = 2;
            out[1] = step;
            out[2] = -1;
            out[4] = 1;
            return;
        }
        rx = nx;
        ry = ny;
        if (in_v(vbits, rx)) {
            out[0] = 0;
            out[1] = step;
            out[2] = rx;
            out[4] = 1;
            return;
        }
    }
    out[0] = 1;
    out[1] = cap;
    out[2] = rx;
    out[4] = 1;
}
