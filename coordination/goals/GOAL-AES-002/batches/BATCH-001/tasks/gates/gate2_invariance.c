/* ==========================================================================
 * GATE 2 / CAND-FR-2 -- projected key-difference invariance used as an OFFLINE
 * sieve.  Measures q_r(delta,pi) = Pr_K[ pi(E_K^(r)(P)) = pi(E_{K+delta}^(r)(P)) ]
 * for r = 1..Nr, with matched and sibling nulls, a sensitivity anchor and a
 * vacuity check.
 *
 * NO RELATED-KEY ORACLE IS QUERIED.  Both encryptions are computed offline by
 * this program, so the mechanism stays single-key-legitimate.
 *
 * THIS IS NOT AN ATTACK, NOT A DISTINGUISHER, NOT A KEY RECOVERY.  It asserts
 * NOTHING about AES security at any round count.  The only reference used
 * anywhere is exhaustive key search, which is definitional.
 *
 * A single software code path is used for every matrix so that the real cipher
 * and both nulls are measured by the SAME instrument (the S-box is swappable,
 * which AES-NI cannot do).  gcc -O3 -maes is available and was verified, but
 * using it for the real cipher and software for the null would make the two
 * incomparable.
 *
 * inference stanza (artifact-provenance gate):
 *   requested_policy: executor-implementation
 *   resolved_model:   claude-opus-5 (Claude Code subagent, model: inherit)
 *   fallback_used:    true   (GPT-5.6 policy aliases unresolvable in this harness)
 *   model_verified:   false  (no adapter doctor --probe run)
 * ========================================================================== */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* ---------------- deterministic PRNG: splitmix64 -------------------------- */
static inline uint64_t sm64(uint64_t *s){
    uint64_t z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

/* ---------------- AES tables ---------------------------------------------- */
static const uint8_t SBOX_REAL[256] = {
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
static const uint8_t RCON[15]={0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36,0x6c,0xd8,0xab,0x4d};

static uint8_t SBOX[256];                 /* active S-box (real or random)     */
static inline uint8_t xt(uint8_t a){ return (uint8_t)((a<<1) ^ ((a>>7)*0x1b)); }

/* matrices ---------------------------------------------------------------- */
#define M_AES128   0   /* real cipher, real key schedule                      */
#define M_NULLA    1   /* NULL-A: independent uniformly random round keys      */
#define M_NULLB    2   /* NULL-B: seeded random S-box, real key schedule (SIB) */
#define M_AES256   3   /* real cipher, 256-bit key (E1/E2 discriminator)       */
#define M_RANDPERM 4   /* random S-box AND random round keys (vacuity control) */

static void keyexp(const uint8_t *key, int klen, int Nr, int mode, uint8_t rk[15][16]){
    if(mode==M_NULLA || mode==M_RANDPERM){
        /* round keys = a deterministic PRF of the master key, so K and K+delta
         * give unrelated round keys: negates key-schedule structure entirely. */
        uint64_t s = 0xcbf29ce484222325ULL;
        for(int i=0;i<klen;i++){ s ^= key[i]; s *= 0x100000001b3ULL; }
        for(int r=0;r<=Nr;r++) for(int j=0;j<16;j+=8){
            uint64_t v = sm64(&s); memcpy(&rk[r][j], &v, 8);
        }
        return;
    }
    int Nk = klen/4, Nb=4, tot = Nb*(Nr+1);
    uint8_t w[60][4];
    for(int i=0;i<Nk;i++) memcpy(w[i], key+4*i, 4);
    for(int i=Nk;i<tot;i++){
        uint8_t t[4]; memcpy(t, w[i-1], 4);
        if(i % Nk == 0){
            uint8_t tmp=t[0]; t[0]=SBOX[t[1]]; t[1]=SBOX[t[2]]; t[2]=SBOX[t[3]]; t[3]=SBOX[tmp];
            t[0] ^= RCON[i/Nk];
        } else if(Nk>6 && (i % Nk)==4){
            for(int j=0;j<4;j++) t[j]=SBOX[t[j]];
        }
        for(int j=0;j<4;j++) w[i][j] = w[i-Nk][j] ^ t[j];
    }
    for(int r=0;r<=Nr;r++) for(int c=0;c<4;c++) memcpy(&rk[r][4*c], w[4*r+c], 4);
}

/* one encryption producing, for every r=1..Nr, BOTH reduced-round conventions:
 *   out_mc[r]  : r rounds, round r INCLUDES MixColumns
 *   out_nomc[r]: r rounds, round r OMITS MixColumns (the FIPS-197 final-round shape)
 */
static void enc_all(const uint8_t *pt, uint8_t rk[15][16], int Nr,
                    uint8_t out_mc[15][16], uint8_t out_nomc[15][16]){
    uint8_t s[16], t[16];
    for(int i=0;i<16;i++) s[i]=pt[i]^rk[0][i];
    for(int r=1;r<=Nr;r++){
        /* SubBytes + ShiftRows */
        for(int c=0;c<4;c++) for(int rw=0;rw<4;rw++)
            t[4*c+rw] = SBOX[ s[4*((c+rw)&3)+rw] ];
        /* no-MixColumns convention for this r */
        for(int i=0;i<16;i++) out_nomc[r][i] = t[i]^rk[r][i];
        /* MixColumns convention for this r */
        for(int c=0;c<4;c++){
            uint8_t a0=t[4*c],a1=t[4*c+1],a2=t[4*c+2],a3=t[4*c+3];
            uint8_t x=a0^a1^a2^a3;
            s[4*c+0]=a0^x^xt(a0^a1);
            s[4*c+1]=a1^x^xt(a1^a2);
            s[4*c+2]=a2^x^xt(a2^a3);
            s[4*c+3]=a3^x^xt(a3^a0);
        }
        for(int i=0;i<16;i++){ s[i]^=rk[r][i]; out_mc[r][i]=s[i]; }
    }
}

/* --------------------------------------------------------------------------
 * configuration
 * -------------------------------------------------------------------------- */
#define MAXD 20
typedef struct { int mode, klen, Nr, ndelta; uint8_t delta[MAXD][32]; char name[24]; char dname[MAXD][32]; } cfg_t;

static uint8_t PT[16] = {0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,
                         0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};

int main(int argc, char **argv){
    uint64_t N      = (argc>1)? strtoull(argv[1],0,10) : (1ULL<<21);
    uint64_t shard  = (argc>2)? strtoull(argv[2],0,10) : 0;
    uint64_t nshard = (argc>3)? strtoull(argv[3],0,10) : 1;
    uint64_t SEED   = (argc>4)? strtoull(argv[4],0,10) : 20260801002ULL;
    int      keygen = (argc>5)? atoi(argv[5]) : 0;  /* 0 splitmix64, 1 AES-CTR */

    /* KAT mode: emit full-round ciphertexts for external FIPS-197 pinning
     * against pycryptodome.  The instrument is not used until this passes. */
    if(argc>6 && argv[6][0]=='k'){
        uint8_t k16[16], k32[32], rk[15][16], om[15][16], on[15][16];
        for(int i=0;i<16;i++) k16[i]=(uint8_t)i;
        for(int i=0;i<32;i++) k32[i]=(uint8_t)i;
        memcpy(SBOX,SBOX_REAL,256);
        keyexp(k16,16,10,M_AES128,rk); enc_all(PT,rk,10,om,on);
        printf("AES128 "); for(int i=0;i<16;i++) printf("%02x",on[10][i]); printf("\n");
        keyexp(k32,32,14,M_AES256,rk); enc_all(PT,rk,14,om,on);
        printf("AES256 "); for(int i=0;i<16;i++) printf("%02x",on[14][i]); printf("\n");
        return 0;
    }

    cfg_t cfgs[5]; int ncfg=0;
    for(int m=0;m<5;m++){
        cfg_t *c=&cfgs[ncfg];
        memset(c,0,sizeof(*c));
        c->mode=m;
        c->klen = (m==M_AES256)?32:16;
        c->Nr   = (m==M_AES256)?14:10;
        strcpy(c->name, m==M_AES128?"AES128":m==M_NULLA?"NULL_A_randrk":
                        m==M_NULLB?"NULL_B_randsbox":m==M_AES256?"AES256":"RANDPERM");
        int d=0;
        /* delta 0 : the VACUITY CHECK, delta = 0, must read q = 1 exactly */
        memset(c->delta[d],0,32); strcpy(c->dname[d],"zero_vacuity"); d++;
        if(c->klen==16){
            for(int p=0;p<16;p++){ memset(c->delta[d],0,32); c->delta[d][p]=0x01;
                snprintf(c->dname[d],32,"single_byte_%d",p); d++; }
            memset(c->delta[d],0,32); c->delta[d][0]=0x01; c->delta[d][1]=0x01;
            c->delta[d][2]=0x01; c->delta[d][3]=0x01; strcpy(c->dname[d],"W0_full_word"); d++;
            memset(c->delta[d],0,32); c->delta[d][0]=0x80; c->delta[d][3]=0x80;
            strcpy(c->dname[d],"W0_two_byte"); d++;
            memset(c->delta[d],0,32); c->delta[d][12]=0x01; c->delta[d][13]=0x01;
            c->delta[d][14]=0x01; c->delta[d][15]=0x01; strcpy(c->dname[d],"W3_full_word"); d++;
        } else {
            for(int p=0;p<32;p+=4){ memset(c->delta[d],0,32); c->delta[d][p]=0x01;
                snprintf(c->dname[d],32,"single_byte_%d",p); d++; }
            memset(c->delta[d],0,32); c->delta[d][0]=0x01; c->delta[d][1]=0x01;
            c->delta[d][2]=0x01; c->delta[d][3]=0x01; strcpy(c->dname[d],"W0_full_word"); d++;
        }
        c->ndelta=d; ncfg++;
    }

    /* counters: [cfg][delta][conv][r][bit] and byte counters */
    static uint64_t bitc[5][MAXD][2][15][128];
    static uint64_t bytec[5][MAXD][2][15][16];
    memset(bitc,0,sizeof(bitc)); memset(bytec,0,sizeof(bytec));

    uint8_t rk1[15][16], rk2[15][16];
    uint8_t o1mc[15][16], o1no[15][16], o2mc[15][16], o2no[15][16];
    uint8_t key[32], key2[32];

    /* AES-CTR key generator uses the real cipher under an independent seed key */
    uint8_t ctrkey[16]; uint8_t ctrrk[15][16];
    { uint64_t s=SEED^0xA5A5A5A5A5A5A5A5ULL;
      for(int i=0;i<16;i+=8){uint64_t v=sm64(&s); memcpy(ctrkey+i,&v,8);} }
    memcpy(SBOX,SBOX_REAL,256);
    keyexp(ctrkey,16,10,M_AES128,ctrrk);

    for(int ci=0; ci<ncfg; ci++){
        cfg_t *c=&cfgs[ci];
        /* install the S-box for this matrix */
        if(c->mode==M_NULLB || c->mode==M_RANDPERM){
            uint64_t s = 0x5EED0B0B0B0B0001ULL;      /* recorded fixed seed */
            for(int i=0;i<256;i++) SBOX[i]=(uint8_t)i;
            for(int i=255;i>0;i--){ int j=(int)(sm64(&s)%(uint64_t)(i+1));
                uint8_t t=SBOX[i]; SBOX[i]=SBOX[j]; SBOX[j]=t; }
        } else memcpy(SBOX,SBOX_REAL,256);

        for(uint64_t n=shard; n<N; n+=nshard){
            /* draw K deterministically from the key index */
            if(keygen==0){
                uint64_t s = SEED ^ (n*0x9E3779B97F4A7C15ULL) ^ ((uint64_t)ci<<40);
                for(int i=0;i<c->klen;i+=8){ uint64_t v=sm64(&s); memcpy(key+i,&v,8); }
            } else {
                uint8_t ctr[16], om[15][16], on[15][16];
                memset(ctr,0,16); memcpy(ctr,&n,8); ctr[8]=(uint8_t)ci;
                uint8_t sv[256]; memcpy(sv,SBOX,256); memcpy(SBOX,SBOX_REAL,256);
                enc_all(ctr,ctrrk,10,om,on); memcpy(key,on[10],16);
                if(c->klen==32){ ctr[9]=1; enc_all(ctr,ctrrk,10,om,on); memcpy(key+16,on[10],16); }
                memcpy(SBOX,sv,256);
            }
            keyexp(key,c->klen,c->Nr,c->mode,rk1);
            enc_all(PT,rk1,c->Nr,o1mc,o1no);
            for(int di=0; di<c->ndelta; di++){
                for(int i=0;i<c->klen;i++) key2[i]=key[i]^c->delta[di][i];
                keyexp(key2,c->klen,c->Nr,c->mode,rk2);
                enc_all(PT,rk2,c->Nr,o2mc,o2no);
                for(int r=1;r<=c->Nr;r++){
                    for(int conv=0; conv<2; conv++){
                        const uint8_t *a = conv? o1no[r] : o1mc[r];
                        const uint8_t *b = conv? o2no[r] : o2mc[r];
                        for(int j=0;j<16;j++){
                            uint8_t dxor = a[j]^b[j];
                            if(dxor==0) bytec[ci][di][conv][r][j]++;
                            for(int bt=0;bt<8;bt++)
                                if(((dxor>>bt)&1)==0) bitc[ci][di][conv][r][8*j+bt]++;
                        }
                    }
                }
            }
        }
    }

    /* emit raw counters */
    uint64_t nlocal = 0; for(uint64_t n=shard;n<N;n+=nshard) nlocal++;
    printf("{\"N_total\":%llu,\"N_this_shard\":%llu,\"shard\":%llu,\"nshards\":%llu,"
           "\"seed\":%llu,\"keygen\":%d,\"records\":[\n",
           (unsigned long long)N,(unsigned long long)nlocal,(unsigned long long)shard,
           (unsigned long long)nshard,(unsigned long long)SEED,keygen);
    int first=1;
    for(int ci=0;ci<ncfg;ci++) for(int di=0;di<cfgs[ci].ndelta;di++)
      for(int conv=0;conv<2;conv++) for(int r=1;r<=cfgs[ci].Nr;r++){
        if(!first) printf(",\n"); first=0;
        printf("{\"matrix\":\"%s\",\"delta\":\"%s\",\"conv\":\"%s\",\"r\":%d,\"bit0\":[",
               cfgs[ci].name, cfgs[ci].dname[di], conv?"no_final_mixcolumns":"with_mixcolumns", r);
        for(int i=0;i<128;i++) printf("%s%llu", i?",":"", (unsigned long long)bitc[ci][di][conv][r][i]);
        printf("],\"byte0\":[");
        for(int i=0;i<16;i++) printf("%s%llu", i?",":"", (unsigned long long)bytec[ci][di][conv][r][i]);
        printf("]}");
      }
    printf("\n]}\n");
    return 0;
}
