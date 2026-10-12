/* Public, deterministic point-distribution sampler. No target logs or keys. */
#include <openssl/ec.h>
#include <openssl/bn.h>
#include <openssl/sha.h>
#include <openssl/obj_mac.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static BIGNUM *decimal(const char *s) {
    BIGNUM *v = NULL;
    if (!BN_dec2bn(&v, s)) return NULL;
    return v;
}

/* Seed is 32 public bytes, domain is a counter in big-endian encoding.
   Rejection, not reduction, gives an unbiased integer in [0, limit). */
static int draw(BIGNUM *v, const BIGNUM *limit, const unsigned char *seed,
                uint64_t *counter) {
    unsigned char message[40], hash[32];
    int bits = BN_num_bits(limit), bytes = (bits + 7) / 8;
    if (bytes > 32) return 0;
    memcpy(message, seed, 32);
    do {
        uint64_t c = (*counter)++;
        for (int j = 0; j < 8; j++) message[39-j] = (unsigned char)(c >> (8*j));
        SHA256(message, sizeof(message), hash);
        hash[0] &= (unsigned char)(0xff >> (8*bytes-bits));
        if (!BN_bin2bn(hash, bytes, v)) return 0;
    } while (BN_cmp(v, limit) >= 0);
    return 1;
}

/* mode 0: independent uniform nonzero k times H.
   mode 1: uniform nonzero k times H, followed by consecutive additions of H.
   mode 2: independent uniform affine points by exact weighted x rejection.
   Output: count pairs of fixed-width big-endian x,y; infinity is an error. */
int sample(const char *ps, const char *as, const char *bs, const char *ns,
           const char *gxs, const char *gys, const unsigned char *seed,
           int mode, uint64_t count, unsigned char *output, uint64_t *used) {
    int ok = 0, bytes = 0;
    BN_CTX *ctx = BN_CTX_new();
    BIGNUM *p=decimal(ps), *a=decimal(as), *b=decimal(bs), *n=decimal(ns);
    BIGNUM *gx=decimal(gxs), *gy=decimal(gys);
    BIGNUM *k=BN_new(), *x=BN_new(), *y=BN_new(), *rhs=BN_new(), *tmp=BN_new();
    EC_GROUP *group=NULL; EC_POINT *h=NULL, *q=NULL;
    uint64_t counter=0;
    if (!ctx || !p || !a || !b || !n || !gx || !gy || !k || !x || !y || !rhs || !tmp) goto done;
    bytes = (BN_num_bits(p)+7)/8;
    group=EC_GROUP_new_curve_GFp(p,a,b,ctx);
    if (!group) goto done;
    h=EC_POINT_new(group); q=EC_POINT_new(group);
    if (!h || !q) goto done;
    if (mode != 2) {
        if (!EC_POINT_set_affine_coordinates(group,h,gx,gy,ctx)) goto done;
        if (EC_POINT_is_on_curve(group,h,ctx) != 1) goto done;
        if (!EC_POINT_mul(group,q,NULL,h,n,ctx) || EC_POINT_is_at_infinity(group,q)!=1) goto done;
        if (!EC_GROUP_set_generator(group,h,n,BN_value_one())) goto done;
    }
    for (uint64_t i=0; i<count; i++) {
        if (mode == 2) {
            for (;;) {
                if (!draw(x,p,seed,&counter)) goto done;
                if (!BN_mod_sqr(rhs,x,p,ctx) || !BN_mod_mul(rhs,rhs,x,p,ctx) ||
                    !BN_mod_mul(tmp,a,x,p,ctx) || !BN_mod_add(rhs,rhs,tmp,p,ctx) ||
                    !BN_mod_add(rhs,rhs,b,p,ctx)) goto done;
                unsigned char message[40],hash[32];
                memcpy(message,seed,32);
                uint64_t c=counter++;
                for (int j=0;j<8;j++) message[39-j]=(unsigned char)(c>>(8*j));
                SHA256(message,40,hash);
                int sign=hash[0]&1;
                if (BN_is_zero(rhs)) {
                    if (sign) continue; /* multiplicity one, accept with 1/2 */
                    BN_zero(y); break;
                }
                if (!BN_mod_sqrt(y,rhs,p,ctx)) continue;
                if (BN_is_odd(y)!=sign && !BN_sub(y,p,y)) goto done;
                break;
            }
        } else {
            if (mode == 0 || i == 0) {
                do { if (!draw(k,n,seed,&counter)) goto done; } while (BN_is_zero(k));
                if (!EC_POINT_mul(group,q,k,NULL,NULL,ctx)) goto done;
            } else if (!EC_POINT_add(group,q,q,h,ctx)) goto done;
            if (EC_POINT_is_at_infinity(group,q)) goto done;
            if (!EC_POINT_get_affine_coordinates(group,q,x,y,ctx)) goto done;
        }
        if (BN_bn2binpad(x,output+i*2*bytes,bytes)!=bytes ||
            BN_bn2binpad(y,output+(i*2+1)*bytes,bytes)!=bytes) goto done;
    }
    *used=counter; ok=1;
done:
    EC_POINT_free(h); EC_POINT_free(q); EC_GROUP_free(group);
    BN_free(p); BN_free(a); BN_free(b); BN_free(n); BN_free(gx); BN_free(gy);
    BN_free(k); BN_free(x); BN_free(y); BN_free(rhs); BN_free(tmp); BN_CTX_free(ctx);
    return ok;
}
