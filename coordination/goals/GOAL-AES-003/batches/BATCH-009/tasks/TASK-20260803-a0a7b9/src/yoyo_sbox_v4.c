/* TASK-20260803-367b1b -- yoyo probe with a PARAMETERIZED S-box.
 *
 * WHY THIS IS A REWRITE, NOT A REUSE: the BATCH-002 probe
 * (BATCH-002/tasks/TASK-20260802-e4fa63/probe.c) implements AES with the
 * AES-NI instructions _mm_aesenc_si128 / _mm_aesdec_si128, which hardwire the
 * AES S-box in silicon. The S-box cannot be substituted there. This file
 * reimplements the SAME measured object in software with a T-table AES whose
 * S-box is a run-time parameter, and reproduces BATCH-002's conventions
 * verbatim:
 *
 *   E_K^r = ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0
 *   round keys = first r+1 of the UNTRUNCATED FIPS-197 AES-128 expansion,
 *                computed with the SAME (possibly random) S-box.
 *   plaintext words  PW[j] = {4*((j+row)%4)+row}   -> PW[0]={0,5,10,15}
 *      (FORWARD ShiftRows diagonals)
 *   ciphertext words CW[j] = {4*((j-row)%4)+row}   -> CW[0]={0,13,10,7}
 *      (INVERSE ShiftRows diagonals)
 *
 * Yoyo trial (identical to BATCH-002 worker()):
 *   draw p0; p1 = p0 with every byte of every word in `amask` re-randomised
 *     (reject a draw that leaves any active word unchanged);
 *   c0 = E^r(p0), c1 = E^r(p1);
 *   swap the ciphertext words in `smask` between c0 and c1 (a swap where all
 *     swapped bytes already agree is TRIVIAL and is excluded);
 *   q0 = D^r(c0'), q1 = D^r(c1'); d = q0 ^ q1;
 *   W = number of plaintext words j with d zero on all of PW[j]; count W>=1.
 *
 * Analytic null: P(W>=1) ~ 4 * 2^-32, so NULL = trials * 2^-30.
 *
 * Pure measurement. certificate.kind: none.
 * build: gcc -O2 -pthread -o yoyo_sbox src/yoyo_sbox.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <pthread.h>
#include <math.h>   /* RC-10 ADDITION (v3 only): pow() for the exact prefix nulls */

/* ================= B9 ADDITION (v4 only) =====================================
 * TASK-20260803-a0a7b9 adds exactly two capabilities to v3 and removes none:
 *
 *  (A) SECTION 3 NULL OBJECT.  sbox spec "ideal" replaces THE CIPHER ITSELF
 *      with a uniformly random bijection on 128 bits, realised as an exactly
 *      LAZILY SAMPLED ideal permutation.  The probe makes only four oracle
 *      queries per trial -- E(p0), E(p1), D(c0'), D(c1') -- so the permutation
 *      is sampled one trial at a time, keeping that trial's two forward pairs:
 *
 *        E(p0)=c0  <- uniform 128 bits
 *        E(p1)=c1  <- uniform 128 bits, redrawn if == c0        (injectivity)
 *        D(c0') = p0 if c0'==c0 ; p1 if c0'==c1 ; else fresh q0 not in {p0,p1}
 *        D(c1') = p1 if c1'==c1 ; p0 if c1'==c0 ; else fresh q1 not in
 *                 {p0,p1,q0}
 *
 *      Within a trial this is the EXACT uniform law over bijections given the
 *      queries made.  Cross-trial consistency is not maintained; at <= 2^34
 *      trials that is <= 2^36 queries in a 2^128 domain, so the chance any two
 *      trials' queries would have forced a shared answer is <= 2^-56.  Stated
 *      as a bound, not a measurement.
 *
 *      The ciphertext randomness comes from a SECOND splitmix64 stream so the
 *      p0/p1 draw code and its rejection loop are untouched and the plaintext
 *      sequence is IDENTICAL to a real-cipher arm at the same seed/armid/thr.
 *      Because every splitmix64 state lies on one orbit under s += GAMMA, the
 *      second stream is a SHIFT of the first by k = (sC-sP)*GAMMA^-1 mod 2^64
 *      steps; v4 computes k per thread and prints min(k, 2^64-k) so overlap
 *      can be excluded rather than assumed.
 *
 *  (B) RC-11 TRIAL-INDEX LOGGING.  The (thread, trial index) of every
 *      non-trivial W>=1 hit is recorded and printed, so matched arms that
 *      consume the same plaintext stream can be analysed PAIRED.  Plus an
 *      order-sensitive 64-bit digest of the whole (p0,p1) stream, which PROVES
 *      two arms saw the same inputs instead of asserting it.
 *
 * Both are inert unless requested: with spec "aes"/"rand:<seed>" the cipher
 * path is the v3 path unchanged, and the new counters only read state.
 * ========================================================================== */

/* ---------- splitmix64 ---------- */
static inline uint64_t sm64(uint64_t *s){
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* ---------- GF(2^8) ---------- */
static uint8_t xt(uint8_t a){ return (uint8_t)((a<<1) ^ ((a>>7)*0x1b)); }
static uint8_t gmul(uint8_t a, uint8_t b){
    uint8_t r=0; while(b){ if(b&1) r^=a; a=xt(a); b>>=1; } return r;
}

/* ---------- the S-box (parameter) and its inverse ---------- */
static uint8_t SBOX[256], ISBOX[256];

/* B9 ADDITION (v4 only): cipher-model selector.  0 = the v3 SPN (unchanged);
 * 1 = the lazily sampled ideal permutation.  Set only by spec "ideal". */
static int IDEALPERM = 0;
#define SM64_GAMMA 0x9E3779B97F4A7C15ULL
/* B9 ADDITION: offset of the ciphertext stream from the plaintext stream. */
#define B9_CIPHER_STREAM_OFFSET 0xD1B54A32D192ED03ULL
/* B9 ADDITION: modular inverse of GAMMA mod 2^64 by Newton iteration. */
static uint64_t b9_gamma_inv(void){
    uint64_t x = SM64_GAMMA;              /* x = a^-1 mod 2^3 is a itself here */
    for(int i=0;i<6;i++) x *= 2ULL - SM64_GAMMA*x;
    return x;
}
/* B9 ADDITION: how many sm64 steps separate two stream states, minimised over
 * the two directions round the 2^64 cycle. */
static uint64_t b9_stream_gap(uint64_t sP, uint64_t sC){
    uint64_t k = (sC - sP) * b9_gamma_inv();
    uint64_t back = 0ULL - k;             /* 2^64 - k */
    return (k < back) ? k : back;
}

static void build_aes_sbox(void){
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

/* Uniform random permutation of 0..255 by Fisher-Yates with splitmix64.
 * For i = 255 down to 1: j = uniform in [0,i] by REJECTION SAMPLING on a
 * 64-bit draw (no modulo bias); swap S[i],S[j]. */
static void build_random_sbox(uint64_t seed){
    uint64_t st=seed;
    for(int i=0;i<256;i++) SBOX[i]=(uint8_t)i;
    for(int i=255;i>=1;i--){
        uint64_t m=(uint64_t)i+1ULL;
        uint64_t lim = UINT64_MAX - (UINT64_MAX % m);   /* largest multiple of m */
        uint64_t r;
        do { r = sm64(&st); } while (r >= lim);
        uint64_t j = r % m;
        uint8_t t=SBOX[i]; SBOX[i]=SBOX[j]; SBOX[j]=t;
    }
}

/* returns 1 if SBOX is a bijection; fills ISBOX */
static int verify_bijective_and_invert(void){
    int seen[256]; memset(seen,0,sizeof seen);
    for(int i=0;i<256;i++){ if(seen[SBOX[i]]) return 0; seen[SBOX[i]]=1; ISBOX[SBOX[i]]=(uint8_t)i; }
    for(int i=0;i<256;i++) if(!seen[i]) return 0;
    for(int i=0;i<256;i++) if(ISBOX[SBOX[i]]!=(uint8_t)i) return 0;
    for(int i=0;i<256;i++) if(SBOX[ISBOX[i]]!=(uint8_t)i) return 0;
    return 1;
}

/* ---------- T-tables (rebuilt for whatever S-box is loaded) ---------- */
static uint32_t T0[256],T1[256],T2[256],T3[256];   /* SB+SR+MC */
static uint32_t U0[256],U1[256],U2[256],U3[256];   /* ISB+ISR+IMC (equiv. inverse) */
static inline uint32_t w4(uint8_t b0,uint8_t b1,uint8_t b2,uint8_t b3){
    return (uint32_t)b0 | ((uint32_t)b1<<8) | ((uint32_t)b2<<16) | ((uint32_t)b3<<24);
}
static void build_tables(void){
    for(int x=0;x<256;x++){
        uint8_t y=SBOX[x];
        T0[x]=w4(gmul(y,2),y,y,gmul(y,3));
        T1[x]=w4(gmul(y,3),gmul(y,2),y,y);
        T2[x]=w4(y,gmul(y,3),gmul(y,2),y);
        T3[x]=w4(y,y,gmul(y,3),gmul(y,2));
        uint8_t z=ISBOX[x];
        U0[x]=w4(gmul(z,0x0e),gmul(z,0x09),gmul(z,0x0d),gmul(z,0x0b));
        U1[x]=w4(gmul(z,0x0b),gmul(z,0x0e),gmul(z,0x09),gmul(z,0x0d));
        U2[x]=w4(gmul(z,0x0d),gmul(z,0x0b),gmul(z,0x0e),gmul(z,0x09));
        U3[x]=w4(gmul(z,0x09),gmul(z,0x0d),gmul(z,0x0b),gmul(z,0x0e));
    }
}

/* ---------- key expansion (FIPS-197, using the loaded S-box) ---------- */
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

typedef struct { uint32_t ek[11][4]; uint32_t dk[11][4]; } sched;

static void sched_init(const uint8_t key[16], sched *s){
    uint8_t rk[11][16]; key_expand(key, rk);
    for(int i=0;i<=10;i++) for(int c=0;c<4;c++)
        s->ek[i][c]=w4(rk[i][4*c+0],rk[i][4*c+1],rk[i][4*c+2],rk[i][4*c+3]);
    /* dk[i] = InvMixColumns(ek[i]) for the equivalent inverse cipher */
    for(int i=0;i<=10;i++) for(int c=0;c<4;c++){
        uint8_t a0=rk[i][4*c+0],a1=rk[i][4*c+1],a2=rk[i][4*c+2],a3=rk[i][4*c+3];
        s->dk[i][c]=w4(
          gmul(a0,0x0e)^gmul(a1,0x0b)^gmul(a2,0x0d)^gmul(a3,0x09),
          gmul(a0,0x09)^gmul(a1,0x0e)^gmul(a2,0x0b)^gmul(a3,0x0d),
          gmul(a0,0x0d)^gmul(a1,0x09)^gmul(a2,0x0e)^gmul(a3,0x0b),
          gmul(a0,0x0b)^gmul(a1,0x0d)^gmul(a2,0x09)^gmul(a3,0x0e));
    }
}

#define B(w,i) ((uint8_t)((w)>>(8*(i))))

/* r-round encryption: ARK_r . SR . SB . [ARK_i . MC . SR . SB]_{i=r-1..1} . ARK_0 */
static void enc_r(const uint8_t in[16], uint8_t out[16], const sched *s, int r){
    uint32_t a[4],b[4];
    for(int c=0;c<4;c++) a[c]=w4(in[4*c],in[4*c+1],in[4*c+2],in[4*c+3]) ^ s->ek[0][c];
    for(int i=1;i<r;i++){
        for(int c=0;c<4;c++)
            b[c] = T0[B(a[c],0)] ^ T1[B(a[(c+1)&3],1)] ^ T2[B(a[(c+2)&3],2)] ^ T3[B(a[(c+3)&3],3)] ^ s->ek[i][c];
        memcpy(a,b,sizeof a);
    }
    for(int c=0;c<4;c++){
        uint32_t v = w4(SBOX[B(a[c],0)],SBOX[B(a[(c+1)&3],1)],SBOX[B(a[(c+2)&3],2)],SBOX[B(a[(c+3)&3],3)]) ^ s->ek[r][c];
        out[4*c+0]=B(v,0); out[4*c+1]=B(v,1); out[4*c+2]=B(v,2); out[4*c+3]=B(v,3);
    }
}

/* exact inverse of enc_r */
static void dec_r(const uint8_t in[16], uint8_t out[16], const sched *s, int r){
    uint32_t a[4],b[4];
    for(int c=0;c<4;c++) a[c]=w4(in[4*c],in[4*c+1],in[4*c+2],in[4*c+3]) ^ s->ek[r][c];
    for(int i=r-1;i>=1;i--){
        for(int c=0;c<4;c++)
            b[c] = U0[B(a[c],0)] ^ U1[B(a[(c+3)&3],1)] ^ U2[B(a[(c+2)&3],2)] ^ U3[B(a[(c+1)&3],3)] ^ s->dk[i][c];
        memcpy(a,b,sizeof a);
    }
    for(int c=0;c<4;c++){
        uint32_t v = w4(ISBOX[B(a[c],0)],ISBOX[B(a[(c+3)&3],1)],ISBOX[B(a[(c+2)&3],2)],ISBOX[B(a[(c+1)&3],3)]) ^ s->ek[0][c];
        out[4*c+0]=B(v,0); out[4*c+1]=B(v,1); out[4*c+2]=B(v,2); out[4*c+3]=B(v,3);
    }
}

/* ---------- geometry ---------- */
static int PW[4][4], CW[4][4];
static void build_geom(void){
    for(int j=0;j<4;j++) for(int row=0;row<4;row++){
        PW[j][row] = 4*(((j+row)%4+4)%4)+row;   /* FORWARD ShiftRows diagonals  */
        CW[j][row] = 4*(((j-row)%4+4)%4)+row;   /* INVERSE ShiftRows diagonals  */
    }
}

/* ---------- worker ---------- */
typedef struct {
    uint64_t ntrials, seed_thread;
    int rounds, amask, smask;
    const sched *s;
    uint64_t whist[5], trivial, wword[4], wge1;
    /* RC-10 ADDITION (v3 only): trials in which d is zero on the FIRST k bytes
     * of PW[j] for at least one j, k = 1..4. wgek[3] (k=4) is by construction
     * the same event as W>=1 and MUST equal wge1. Nothing else changes. */
    uint64_t wgek[4];
    /* ---- B9 ADDITIONS (v4 only) ---- */
    int tid;                    /* thread index, for RC-11 pairing            */
    int idealperm;              /* 1 = ideal-permutation cipher model         */
    uint64_t seed_cipher;       /* second splitmix64 stream, ideal model only */
    uint64_t stream_gap;        /* min steps between the two streams          */
    uint64_t pdigest;           /* order-sensitive digest of the (p0,p1) stream*/
    uint64_t ideal_redraws;     /* injectivity rejections actually taken      */
    uint64_t *hits;             /* trial indices of non-trivial W>=1 hits     */
    uint64_t nhits, hitcap, hit_overflow;
} job;

static void *worker(void *arg){
    job *J=(job*)arg;
    uint64_t st=J->seed_thread;
    const sched *s=J->s;
    int r=J->rounds;
    uint8_t p0[16],p1[16],c0[16],c1[16],q0[16],q1[16],d[16];
    /* B9 ADDITIONS (v4 only) */
    uint64_t stc = J->seed_cipher;          /* ciphertext stream, ideal only  */
    uint8_t c0o[16], c1o[16];               /* pre-swap ciphertexts, ideal only*/
    uint64_t pdig = 1469598103934665603ULL; /* FNV-1a 64 offset basis          */
    for(uint64_t t=0;t<J->ntrials;t++){
        uint64_t a=sm64(&st), b=sm64(&st);
        memcpy(p0,&a,8); memcpy(p0+8,&b,8);
        memcpy(p1,p0,16);
        int ok=0;
        while(!ok){
            ok=1;
            for(int j=0;j<4;j++) if(J->amask & (1<<j)){
                uint64_t rnd=sm64(&st); int nz=0;
                for(int row=0;row<4;row++){
                    uint8_t nb=(uint8_t)(rnd>>(8*row));
                    p1[PW[j][row]]=nb;
                    if(nb != p0[PW[j][row]]) nz=1;
                }
                if(!nz) ok=0;
            }
        }
        /* B9 ADDITION (v4 only): order-sensitive digest of the FULL (p0,p1)
         * stream, accumulated AFTER the rejection loop has settled p1.  Reads
         * p0/p1 only; draws no randomness; identical in every cipher model, so
         * two arms printing the same digest saw the same inputs. */
        {   uint64_t w;
            for(int i=0;i<16;i+=8){ memcpy(&w,p0+i,8); pdig = (pdig ^ w) * 1099511628211ULL; }
            for(int i=0;i<16;i+=8){ memcpy(&w,p1+i,8); pdig = (pdig ^ w) * 1099511628211ULL; }
        }
        /* B9 ADDITION (v4 only): ideal-permutation forward queries.  When
         * J->idealperm is 0 this block is skipped entirely and the two v3
         * enc_r() calls below run unchanged. */
        if(J->idealperm){
            uint64_t z;
            z=sm64(&stc); memcpy(c0,&z,8); z=sm64(&stc); memcpy(c0+8,&z,8);
            do {
                z=sm64(&stc); memcpy(c1,&z,8); z=sm64(&stc); memcpy(c1+8,&z,8);
                if(memcmp(c1,c0,16)==0) J->ideal_redraws++; else break;
            } while(1);
        } else {
        enc_r(p0,c0,s,r);
        enc_r(p1,c1,s,r);
        }   /* B9 ADDITION (v4 only): closes the else of the ideal branch */
        /* B9 ADDITION (v4 only): keep the PRE-swap ciphertexts so the lazy
         * decryption can honour the two pairs already sampled. */
        if(J->idealperm){ memcpy(c0o,c0,16); memcpy(c1o,c1,16); }
        int trivial=1;
        for(int j=0;j<4;j++) if(J->smask & (1<<j))
            for(int row=0;row<4;row++){
                int i=CW[j][row];
                uint8_t x=c0[i], y=c1[i];
                if(x!=y) trivial=0;
                c0[i]=y; c1[i]=x;
            }
        /* B9 ADDITION (v4 only): ideal-permutation inverse queries, exactly
         * consistent with the two forward pairs sampled above.  c0'!=c1'
         * whenever the swap is non-trivial, so q0!=q1 is a real constraint and
         * is enforced. */
        if(J->idealperm){
            uint64_t z;
            if(memcmp(c0,c0o,16)==0)      memcpy(q0,p0,16);
            else if(memcmp(c0,c1o,16)==0) memcpy(q0,p1,16);
            else do {
                z=sm64(&stc); memcpy(q0,&z,8); z=sm64(&stc); memcpy(q0+8,&z,8);
                if(memcmp(q0,p0,16)==0||memcmp(q0,p1,16)==0) J->ideal_redraws++;
                else break;
            } while(1);
            if(memcmp(c1,c1o,16)==0)      memcpy(q1,p1,16);
            else if(memcmp(c1,c0o,16)==0) memcpy(q1,p0,16);
            else do {
                z=sm64(&stc); memcpy(q1,&z,8); z=sm64(&stc); memcpy(q1+8,&z,8);
                if(memcmp(q1,p0,16)==0||memcmp(q1,p1,16)==0||memcmp(q1,q0,16)==0)
                    J->ideal_redraws++;
                else break;
            } while(1);
        } else {
        dec_r(c0,q0,s,r);
        dec_r(c1,q1,s,r);
        }   /* B9 ADDITION (v4 only): closes the else of the ideal branch */
        for(int i=0;i<16;i++) d[i]=q0[i]^q1[i];
        int W=0;
        for(int j=0;j<4;j++){
            int z=1; for(int row=0;row<4;row++) if(d[PW[j][row]]) { z=0; break; }
            if(z){ W++; if(!trivial) J->wword[j]++; }
        }
        if(trivial){ J->trivial++; continue; }
        J->whist[W]++;
        if(W>=1) J->wge1++;
        /* B9 ADDITION (v4 only): RC-11 trial-index log.  Records only the
         * index; touches no counter used by any v3 field. */
        if(W>=1){
            if(J->nhits < J->hitcap) J->hits[J->nhits++] = t;
            else J->hit_overflow++;
        }
        /* RC-10 ADDITION (v3 only): longest zero PREFIX of d over PW[j], any j.
         * Reads only d and PW; draws no randomness; touches no other counter. */
        {   int kmax=0;
            for(int j=0;j<4;j++){
                int p=0; while(p<4 && d[PW[j][p]]==0) p++;
                if(p>kmax) kmax=p;
            }
            for(int k=1;k<=kmax;k++) J->wgek[k-1]++;
        }
    }
    /* B9 ADDITION (v4 only): publish the stream digest computed above. */
    J->pdigest = pdig;
    return NULL;
}

/* ---------- pin ---------- */
static int pin(uint64_t seed, int aes_sbox){
    int kat_enc_ok=-1, kat_dec_ok=-1;
    char ctbuf[33]; ctbuf[0]=0;
    if(aes_sbox){
        const uint8_t kk[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
        const uint8_t pt[16]={0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,
                              0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
        const uint8_t ct[16]={0x69,0xc4,0xe0,0xd8,0x6a,0x7b,0x04,0x30,
                              0xd8,0xcd,0xb7,0x80,0x70,0xb4,0xc5,0x5a};
        sched s; sched_init(kk,&s);
        uint8_t y[16],x[16];
        enc_r(pt,y,&s,10); kat_enc_ok=(memcmp(y,ct,16)==0);
        for(int i=0;i<16;i++) sprintf(ctbuf+2*i,"%02x",y[i]);
        dec_r(ct,x,&s,10); kat_dec_ok=(memcmp(x,pt,16)==0);
    }
    uint64_t st=seed; int nvec=512, fails=0; int first_fail_r=0;
    for(int v=0;v<nvec;v++){
        uint8_t k[16], pt[16];
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(k+i,&z,8); }
        for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(pt+i,&z,8); }
        sched sv; sched_init(k,&sv);
        for(int r=1;r<=10;r++){
            uint8_t c[16],e[16];
            enc_r(pt,c,&sv,r); dec_r(c,e,&sv,r);
            if(memcmp(e,pt,16)!=0){ fails++; if(!first_fail_r) first_fail_r=r; }
        }
    }
    printf("  \"fips197_c1_kat_applicable\": %s,\n", aes_sbox?"true":"false");
    if(aes_sbox){
        printf("  \"fips197_c1_kat_encrypt_match\": %s,\n", kat_enc_ok?"true":"false");
        printf("  \"fips197_c1_kat_decrypt_match\": %s,\n", kat_dec_ok?"true":"false");
        printf("  \"fips197_c1_kat_ciphertext_computed\": \"%s\",\n", ctbuf);
    }
    printf("  \"roundtrip_vectors\": %d,\n", nvec);
    printf("  \"roundtrip_checks\": %d,\n", nvec*10);
    printf("  \"roundtrip_failures\": %d,\n", fails);
    printf("  \"roundtrip_first_failure_round\": %d,\n", first_fail_r);
    printf("  \"pin_seed\": %llu,\n",(unsigned long long)seed);
    int pass = (fails==0) && (!aes_sbox || (kat_enc_ok==1 && kat_dec_ok==1));
    printf("  \"pin_pass\": %s\n", pass?"true":"false");
    return pass?0:1;
}

static void print_sbox(void){
    printf("  \"sbox\": [");
    for(int i=0;i<256;i++) printf("%d%s",SBOX[i], i<255?",":"");
    printf("],\n");
    printf("  \"sbox_first8\": [");
    for(int i=0;i<8;i++) printf("%d%s",SBOX[i], i<7?",":"");
    printf("],\n");
}

/* load the S-box named by argv: "aes" or "rand:<seed>" */
static int load_sbox(const char *spec, uint64_t *out_seed){
    *out_seed=0;
    if(!strcmp(spec,"aes")){ build_aes_sbox(); return 1; }
    /* B9 ADDITION (v4 only): the section 3 null object.  The AES tables are
     * still built so that verify_bijective_and_invert() and build_tables()
     * behave exactly as in v3, but NOTHING in the worker's ideal path reads
     * them: no S-box, no MixColumns, no key schedule, no round count. */
    if(!strcmp(spec,"ideal")){ IDEALPERM = 1; build_aes_sbox(); return 1; }
    if(!strncmp(spec,"rand:",5)){ *out_seed=strtoull(spec+5,NULL,10); build_random_sbox(*out_seed); return 0; }
    fprintf(stderr,"bad sbox spec '%s' (want aes | rand:<seed>)\n",spec); exit(2);
}

int main(int argc, char **argv){
    build_geom();
    if(argc<2){
        fprintf(stderr,"usage: yoyo_sbox geom\n"
                       "       yoyo_sbox pin  <sboxspec> <seed>\n"
                       "       yoyo_sbox sbox <sboxspec>\n"
                       "       yoyo_sbox arm  <name> <sboxspec> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads>\n");
        return 2;
    }
    if(!strcmp(argv[1],"geom")){
        printf("{\n  \"PW_forward_shiftrows_diagonals\": [");
        for(int j=0;j<4;j++){ printf("[%d,%d,%d,%d]%s",PW[j][0],PW[j][1],PW[j][2],PW[j][3], j<3?",":""); }
        printf("],\n  \"CW_inverse_shiftrows_diagonals\": [");
        for(int j=0;j<4;j++){ printf("[%d,%d,%d,%d]%s",CW[j][0],CW[j][1],CW[j][2],CW[j][3], j<3?",":""); }
        printf("]\n}\n");
        return 0;
    }
    if(!strcmp(argv[1],"vec")){
        /* SEGMENT 2 ANCHOR MODE (added in yoyo_sbox_v2.c only): dump enc_r for
           r=1..10 on a fixed key/plaintext so an independent implementation can
           check EVERY round count, not just r=10. */
        uint64_t ss; load_sbox(argv[2],&ss);
        if(!verify_bijective_and_invert()){ printf("{\"bijective\":false}\n"); return 1; }
        build_tables();
        uint8_t k[16],pt[16];
        for(int i=0;i<16;i++){ k[i]=(uint8_t)(0x10+i); pt[i]=(uint8_t)(0xa0+i); }
        printf("{\n  \"sbox_spec\": \"%s\",\n  \"key\": \"",argv[2]);
        for(int i=0;i<16;i++) printf("%02x",k[i]);
        printf("\",\n  \"pt\": \"");
        for(int i=0;i<16;i++) printf("%02x",pt[i]);
        printf("\",\n  \"enc_by_round\": {");
        sched s2; sched_init(k,&s2);
        for(int r=1;r<=10;r++){
            uint8_t c[16]; enc_r(pt,c,&s2,r);
            printf("%s\n    \"%d\": \"",r>1?",":"",r);
            for(int i=0;i<16;i++) printf("%02x",c[i]);
            printf("\"");
        }
        printf("\n  }\n}\n");
        return 0;
    }
    if(!strcmp(argv[1],"pin")){
        uint64_t ss; int is_aes=load_sbox(argv[2],&ss);
        int bij=verify_bijective_and_invert(); build_tables();
        printf("{\n  \"mode\": \"pin\",\n  \"sbox_spec\": \"%s\",\n  \"sbox_bijective\": %s,\n",
               argv[2], bij?"true":"false");
        if(!bij){ printf("  \"pin_pass\": false\n}\n"); return 1; }
        print_sbox();
        int rc=pin(strtoull(argv[3],NULL,10), is_aes);
        printf("}\n");
        return rc;
    }
    if(!strcmp(argv[1],"sbox")){
        uint64_t ss; load_sbox(argv[2],&ss);
        int bij=verify_bijective_and_invert();
        printf("{\n  \"sbox_spec\": \"%s\",\n  \"sbox_seed\": %llu,\n  \"sbox_bijective\": %s,\n",
               argv[2],(unsigned long long)ss, bij?"true":"false");
        print_sbox();
        printf("  \"draw\": \"Fisher-Yates over 0..255 with splitmix64, rejection sampling (no modulo bias)\"\n}\n");
        return bij?0:1;
    }
    if(strcmp(argv[1],"arm")) { fprintf(stderr,"bad mode\n"); return 2; }
    if(argc<11){ fprintf(stderr,"arm needs 9 args\n"); return 2; }
    const char *name=argv[2];
    const char *spec=argv[3];
    uint64_t sbox_seed; load_sbox(spec,&sbox_seed);
    if(!verify_bijective_and_invert()){ fprintf(stderr,"S-BOX NOT BIJECTIVE -- refusing to measure\n"); return 4; }
    build_tables();
    int rounds=atoi(argv[4]), amask=atoi(argv[5]), smask=atoi(argv[6]);
    int log2N=atoi(argv[7]);
    uint64_t seed=strtoull(argv[8],NULL,10);
    int armid=atoi(argv[9]); int nthr=atoi(argv[10]);
    if(smask==0 || smask==15){ fprintf(stderr,"degenerate smask forbidden\n"); return 3; }
    if(amask==0){ fprintf(stderr,"empty amask forbidden\n"); return 3; }

    uint64_t kst = seed ^ 0xA5A5A5A5A5A5A5A5ULL;
    uint8_t key[16];
    for(int i=0;i<16;i+=8){ uint64_t z=sm64(&kst); memcpy(key+i,&z,8); }
    sched s; sched_init(key,&s);

    uint64_t N = 1ULL<<log2N;
    job *jobs=calloc(nthr,sizeof(job));
    pthread_t *th=calloc(nthr,sizeof(pthread_t));
    uint64_t per=N/nthr;
    for(int t=0;t<nthr;t++){
        jobs[t].ntrials = per + (t==0 ? N - per*nthr : 0);
        jobs[t].seed_thread = seed ^ ((uint64_t)armid*0x1234567891ULL)
                            ^ ((uint64_t)(t+1)*0x9E3779B97F4A7C15ULL);
        jobs[t].rounds=rounds; jobs[t].amask=amask; jobs[t].smask=smask; jobs[t].s=&s;
        /* ---- B9 ADDITIONS (v4 only) ---- */
        jobs[t].tid = t;
        jobs[t].idealperm = IDEALPERM;
        jobs[t].seed_cipher = jobs[t].seed_thread ^ B9_CIPHER_STREAM_OFFSET;
        jobs[t].stream_gap = b9_stream_gap(jobs[t].seed_thread, jobs[t].seed_cipher);
        jobs[t].hitcap = 4096;
        jobs[t].hits = calloc(jobs[t].hitcap, sizeof(uint64_t));
        if(!jobs[t].hits){ fprintf(stderr,"hit buffer alloc failed\n"); return 5; }
    }
    for(int t=0;t<nthr;t++) pthread_create(&th[t],NULL,worker,&jobs[t]);
    for(int t=0;t<nthr;t++) pthread_join(th[t],NULL);

    uint64_t wh[5]={0}, wword[4]={0}, trivial=0, wge1=0;
    uint64_t wgek[4]={0};   /* RC-10 ADDITION (v3 only) */
    for(int t=0;t<nthr;t++){
        for(int i=0;i<5;i++)  wh[i]+=jobs[t].whist[i];
        for(int i=0;i<4;i++)  wword[i]+=jobs[t].wword[i];
        for(int i=0;i<4;i++)  wgek[i]+=jobs[t].wgek[i];   /* RC-10 ADDITION */
        trivial+=jobs[t].trivial; wge1+=jobs[t].wge1;
    }
    printf("{\n  \"arm\": \"%s\",\n  \"sbox_spec\": \"%s\",\n  \"sbox_seed\": %llu,\n  \"sbox_bijective\": true,\n",
           name,spec,(unsigned long long)sbox_seed);
    printf("  \"sbox_first8\": [");
    for(int i=0;i<8;i++) printf("%d%s",SBOX[i], i<7?",":"");
    printf("],\n");
    printf("  \"rounds\": %d,\n  \"amask\": %d,\n  \"smask\": %d,\n",rounds,amask,smask);
    printf("  \"trials\": %llu,\n  \"log2N\": %d,\n  \"seed\": %llu,\n  \"arm_id\": %d,\n  \"threads\": %d,\n",
           (unsigned long long)N, log2N, (unsigned long long)seed, armid, nthr);
    printf("  \"key_hex\": \""); for(int i=0;i<16;i++) printf("%02x",key[i]); printf("\",\n");
    printf("  \"thread_seeds\": [");
    for(int t=0;t<nthr;t++) printf("%llu%s",(unsigned long long)jobs[t].seed_thread, t<nthr-1?",":"");
    printf("],\n");
    printf("  \"trivial_swaps_excluded\": %llu,\n",(unsigned long long)trivial);
    printf("  \"nontrivial_trials\": %llu,\n",(unsigned long long)(N-trivial));
    printf("  \"W_ge1_nontrivial\": %llu,\n",(unsigned long long)wge1);
    printf("  \"W_ge1_by_word\": [%llu,%llu,%llu,%llu],\n",
           (unsigned long long)wword[0],(unsigned long long)wword[1],
           (unsigned long long)wword[2],(unsigned long long)wword[3]);
    printf("  \"whist\": [");
    for(int i=0;i<5;i++) printf("%llu%s",(unsigned long long)wh[i], i<4?",":"");
    printf("],\n");
    printf("  \"null_expectation_analytic\": %.10f,\n", (double)(N-trivial)*4.0/4294967296.0);
    /* RC-10 ADDITION (v3 only): the k-byte-prefix counters. Index i is k=i+1.
       W_ge1_prefix_k[3] is the same event as W_ge1_nontrivial by construction. */
    printf("  \"W_ge1_prefix_k\": [%llu,%llu,%llu,%llu],\n",
           (unsigned long long)wgek[0],(unsigned long long)wgek[1],
           (unsigned long long)wgek[2],(unsigned long long)wgek[3]);
    printf("  \"prefix_k4_equals_W_ge1\": %s,\n", (wgek[3]==wge1)?"true":"false");
    printf("  \"null_expectation_prefix_k_exact\": [%.10f,%.10f,%.10f,%.10f],\n",
           (double)(N-trivial)*(1.0-pow(1.0-1.0/256.0,4.0)),
           (double)(N-trivial)*(1.0-pow(1.0-1.0/65536.0,4.0)),
           (double)(N-trivial)*(1.0-pow(1.0-1.0/16777216.0,4.0)),
           (double)(N-trivial)*(1.0-pow(1.0-1.0/4294967296.0,4.0)));
    /* ================= B9 ADDITIONS (v4 only): new output fields ========== */
    {   uint64_t gapmin = ~0ULL, redraw = 0, ovf = 0, nh = 0;
        for(int t=0;t<nthr;t++){
            if(jobs[t].stream_gap < gapmin) gapmin = jobs[t].stream_gap;
            redraw += jobs[t].ideal_redraws;
            ovf    += jobs[t].hit_overflow;
            nh     += jobs[t].nhits;
        }
        printf("  \"cipher_model\": \"%s\",\n",
               IDEALPERM ? "ideal_permutation_lazy_128bit" : "spn_ttable_aes_structure");
        printf("  \"ideal_permutation\": %s,\n", IDEALPERM ? "true" : "false");
        /* order-sensitive FNV-1a-style digest of every (p0,p1) pair, per thread */
        printf("  \"plaintext_stream_digest\": [");
        for(int t=0;t<nthr;t++)
            printf("\"%016llx\"%s",(unsigned long long)jobs[t].pdigest, t<nthr-1?",":"");
        printf("],\n");
        printf("  \"cipher_stream_seeds\": [");
        for(int t=0;t<nthr;t++)
            printf("%llu%s",(unsigned long long)jobs[t].seed_cipher, t<nthr-1?",":"");
        printf("],\n");
        printf("  \"stream_gap_min_steps\": %llu,\n",(unsigned long long)gapmin);
        printf("  \"stream_gap_min_log2\": %.3f,\n", gapmin? log2((double)gapmin) : -1.0);
        printf("  \"ideal_injectivity_redraws\": %llu,\n",(unsigned long long)redraw);
        printf("  \"hit_log_overflow\": %llu,\n",(unsigned long long)ovf);
        printf("  \"hit_trials_logged\": %llu,\n",(unsigned long long)nh);
        /* RC-11: (thread, trial index) of every non-trivial W>=1 hit. */
        printf("  \"hit_trials\": [");
        {   int first=1;
            for(int t=0;t<nthr;t++)
                for(uint64_t i=0;i<jobs[t].nhits;i++){
                    printf("%s[%d,%llu]", first?"":",", t,
                           (unsigned long long)jobs[t].hits[i]);
                    first=0;
                }
        }
        printf("],\n");
        printf("  \"instrument_v4\": \"yoyo_sbox_v4\",\n");
    }
    printf("  \"instrument\": \"yoyo_sbox_v3\"\n");
    printf("}\n");
    free(jobs); free(th);
    /* B9 ADDITION (v4 only): jobs[t].hits is deliberately NOT freed here.  It
     * would be a use-after-free to reach through jobs[] after free(jobs), and
     * the process exits on the next line, so the OS reclaims it.  Recorded so a
     * reader does not mistake it for an oversight. */
    return 0;
}
