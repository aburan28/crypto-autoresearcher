/* TASK-20260803-48a239 -- RC-7 half 1.
 *
 * Dumps enc_r for r = 1..10 on the SAME fixed key/plaintext that
 * yoyo_sbox_v2's `vec` mode uses (key = 0x10..0x1f, pt = 0xa0..0xaf), using
 * the AES-NI code path COPIED VERBATIM from BATCH-002
 * (BATCH-002/tasks/TASK-20260802-e4fa63/probe.c lines 30-83): the same
 * build_sbox, key_expand, sched_init, enc_r. The S-box here is fixed in
 * silicon by _mm_aesenc_si128; that is the whole point of the comparison.
 *
 * Purpose: settle the red team's RC-7 half 1 -- one 16-byte enc_5 vector
 * compared between the software T-table probe and BATCH-002's AES-NI probe,
 * so that the "13.5x reproduction of BATCH-002" claim rests on the two probes
 * computing the same function rather than on two similar-looking numbers.
 *
 * Pure verification. certificate.kind: none.
 * build: gcc -O2 -maes -msse4.1 -o rc7_aesni_vec rc7_aesni_vec.c
 */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <wmmintrin.h>
#include <emmintrin.h>

static uint8_t SBOX[256];
static uint8_t xt(uint8_t a){ return (uint8_t)((a<<1) ^ ((a>>7)*0x1b)); }
static uint8_t gmul(uint8_t a, uint8_t b){
    uint8_t r=0; while(b){ if(b&1) r^=a; a=xt(a); b>>=1; } return r;
}
static void build_sbox(void){
    uint8_t inv[256]; inv[0]=0;
    for(int a=1;a<256;a++) for(int b=1;b<256;b++) if(gmul((uint8_t)a,(uint8_t)b)==1){ inv[a]=(uint8_t)b; break; }
    for(int i=0;i<256;i++){
        uint8_t x=inv[i], y=0;
        for(int bit=0;bit<8;bit++){
            uint8_t v = ((x>>bit)&1) ^ ((x>>((bit+4)&7))&1) ^ ((x>>((bit+5)&7))&1)
                      ^ ((x>>((bit+6)&7))&1) ^ ((x>>((bit+7)&7))&1) ^ ((0x63>>bit)&1);
            y |= (uint8_t)(v<<bit);
        }
        SBOX[i]=y;
    }
}
static void key_expand(const uint8_t key[16], uint8_t rk[11][16]){
    static const uint8_t rcon[10]={0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36};
    memcpy(rk[0], key, 16);
    for(int i=1;i<=10;i++){
        uint8_t t[4];
        memcpy(t, rk[i-1]+12, 4);
        uint8_t tmp=t[0]; t[0]=SBOX[t[1]]; t[1]=SBOX[t[2]]; t[2]=SBOX[t[3]]; t[3]=SBOX[tmp];
        t[0]^=rcon[i-1];
        for(int w=0;w<4;w++)
            for(int b=0;b<4;b++)
                rk[i][4*w+b] = rk[i-1][4*w+b] ^ (w==0 ? t[b] : rk[i][4*(w-1)+b]);
    }
}
typedef struct { __m128i ek[11]; __m128i dk[11]; } sched;
static void sched_init(const uint8_t key[16], sched *s){
    uint8_t rk[11][16]; key_expand(key, rk);
    for(int i=0;i<=10;i++) s->ek[i]=_mm_loadu_si128((const __m128i*)rk[i]);
    s->dk[0]=s->ek[0]; s->dk[10]=s->ek[10];
    for(int i=1;i<10;i++) s->dk[i]=_mm_aesimc_si128(s->ek[i]);
}
static inline __m128i enc_r(__m128i x, const sched *s, int r){
    x=_mm_xor_si128(x, s->ek[0]);
    for(int i=1;i<r;i++) x=_mm_aesenc_si128(x, s->ek[i]);
    return _mm_aesenclast_si128(x, s->ek[r]);
}
static inline __m128i dec_r(__m128i x, const sched *s, int r){
    x=_mm_xor_si128(x, s->ek[r]);
    for(int i=r-1;i>=1;i--) x=_mm_aesdec_si128(x, s->dk[i]);
    return _mm_aesdeclast_si128(x, s->ek[0]);
}

int main(void){
    build_sbox();
    uint8_t k[16], pt[16], buf[16];
    for(int i=0;i<16;i++){ k[i]=(uint8_t)(0x10+i); pt[i]=(uint8_t)(0xa0+i); }
    sched s; sched_init(k,&s);
    printf("{\n  \"probe\": \"AES-NI (_mm_aesenc_si128), code path copied verbatim from BATCH-002 probe.c\",\n");
    printf("  \"key\": \""); for(int i=0;i<16;i++) printf("%02x",k[i]);
    printf("\",\n  \"pt\": \""); for(int i=0;i<16;i++) printf("%02x",pt[i]);
    printf("\",\n  \"enc_by_round\": {");
    int rtfail=0;
    for(int r=1;r<=10;r++){
        __m128i x=_mm_loadu_si128((const __m128i*)pt);
        __m128i c=enc_r(x,&s,r);
        _mm_storeu_si128((__m128i*)buf,c);
        printf("%s\n    \"%d\": \"",r>1?",":"",r);
        for(int i=0;i<16;i++) printf("%02x",buf[i]);
        printf("\"");
        __m128i back=dec_r(c,&s,r);
        uint8_t bb[16]; _mm_storeu_si128((__m128i*)bb,back);
        if(memcmp(bb,pt,16)!=0) rtfail++;
    }
    printf("\n  },\n  \"roundtrip_failures_r1_to_r10\": %d\n}\n", rtfail);
    return 0;
}
