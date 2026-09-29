/*
 * anchor.c -- TASK-20260804-8965ec cross-instrument anchor helper.
 *
 * INFERENCE BLOCK: policy executor-implementation, requested_policy
 * executor-implementation, resolved_model claude-sonnet-5, fallback_used
 * false, model_verified false (no adapter probe available in this harness),
 * standing_basis 0137a051eb5828789eb267fa83c8278086578d4c.
 *
 * Purpose: an INDEPENDENT (third) AES-128 implementation -- written from the
 * FIPS-197 specification, not derived from count5.c or cnt.c -- used only to:
 *   (1) verify itself against the FIPS-197 Appendix C.1 known-answer test
 *       (full 10-round AES-128, standard MixColumns);
 *   (2) expand a raw 16-byte key into the 176-byte round-key blob that
 *       count5.c requires on argv (count5.c takes an already-expanded
 *       schedule, it does not run key expansion itself);
 *   (3) independently encrypt one 16-byte plaintext block for r rounds under
 *       the campaign's C1 convention (final round has no MixColumns), for
 *       cross-checking cnt.c's own "block" pin mode and count5.c's per-block
 *       output, all with the STANDARD AES mixing matrix (AES_MC), which is
 *       the only matrix count5.c can run (it is AES-NI-hardware-only and
 *       cannot vary the mixing layer).
 *
 * This file duplicates no code from count5.c or cnt.c; the S-box table is
 * the public FIPS-197 constant and the algorithm is the public specification.
 *
 * usage:
 *   anchor kat                       -- FIPS-197 C.1 KAT self-check
 *   anchor keysched <key32hex>       -- print 176-byte round-key hex for count5.c
 *   anchor block <key32hex> <r> <pt32hex>   -- C1-convention r-round single-block encrypt
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static const uint8_t SBOX[256] = {
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

static uint8_t gmul(uint8_t a, uint8_t b){
  uint8_t p=0;
  for(int i=0;i<8;i++){
    if(b&1) p^=a;
    uint8_t hi=a&0x80; a=(uint8_t)(a<<1); if(hi) a^=0x1b;
    b>>=1;
  }
  return p;
}

static void hex2b(const char*h,uint8_t*o,int n){for(int i=0;i<n;i++){unsigned v;sscanf(h+2*i,"%2x",&v);o[i]=(uint8_t)v;}}
static void b2hex(const uint8_t*b,int n,char*o){for(int i=0;i<n;i++) sprintf(o+2*i,"%02x",b[i]); o[2*n]=0;}

/* Standard FIPS-197 key expansion for AES-128: rk is 176 bytes, 11 round keys. */
static void keyexpand(const uint8_t *key, uint8_t *rk){
  memcpy(rk,key,16);
  uint8_t rcon=1;
  for(int i=16;i<176;i+=4){
    uint8_t t[4]={rk[i-4],rk[i-3],rk[i-2],rk[i-1]};
    if(i%16==0){
      uint8_t tmp=t[0];
      t[0]=(uint8_t)(SBOX[t[1]]^rcon); t[1]=SBOX[t[2]]; t[2]=SBOX[t[3]]; t[3]=SBOX[tmp];
      rcon=gmul(rcon,2);
    }
    for(int j=0;j<4;j++) rk[i+j]=(uint8_t)(rk[i-16+j]^t[j]);
  }
}

/* State is column-major bytes s[0..15], s[4*c+r] = row r, col c (FIPS-197 layout). */
static void add_round_key(uint8_t *s, const uint8_t *rk){ for(int i=0;i<16;i++) s[i]^=rk[i]; }
static void sub_bytes(uint8_t *s){ for(int i=0;i<16;i++) s[i]=SBOX[s[i]]; }
static void shift_rows(uint8_t *s){
  uint8_t t[16]; memcpy(t,s,16);
  for(int c=0;c<4;c++) for(int r=0;r<4;r++) s[4*c+r]=t[4*((c+r)%4)+r];
}
/* Standard AES MixColumns (matrix rows [2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]) */
static void mix_columns(uint8_t *s){
  for(int c=0;c<4;c++){
    uint8_t a0=s[4*c+0],a1=s[4*c+1],a2=s[4*c+2],a3=s[4*c+3];
    s[4*c+0]=(uint8_t)(gmul(a0,2)^gmul(a1,3)^a2^a3);
    s[4*c+1]=(uint8_t)(a0^gmul(a1,2)^gmul(a2,3)^a3);
    s[4*c+2]=(uint8_t)(a0^a1^gmul(a2,2)^gmul(a3,3));
    s[4*c+3]=(uint8_t)(gmul(a0,3)^a1^a2^gmul(a3,2));
  }
}

/* Full standard AES-128 encrypt (10 rounds), FIPS-197 layout, for the KAT only. */
static void aes128_encrypt_full(const uint8_t *rk, const uint8_t *pt, uint8_t *ct){
  uint8_t s[16]; memcpy(s,pt,16);
  add_round_key(s,rk+0);
  for(int r=1;r<10;r++){ sub_bytes(s); shift_rows(s); mix_columns(s); add_round_key(s,rk+16*r); }
  sub_bytes(s); shift_rows(s); add_round_key(s,rk+16*10);
  memcpy(ct,s,16);
}

/* r-round encrypt under the campaign's C1 convention: final round has NO
 * MixColumns, matching both count5.c's encr() and cnt.c's enc_soft()/AES-NI
 * hardware path (_mm_aesenclast_si128 omits MixColumns on the last round). */
static void aes_r_round_c1(const uint8_t *rk, int r, const uint8_t *pt, uint8_t *ct){
  uint8_t s[16]; memcpy(s,pt,16);
  add_round_key(s,rk+0);
  for(int i=1;i<r;i++){ sub_bytes(s); shift_rows(s); mix_columns(s); add_round_key(s,rk+16*i); }
  sub_bytes(s); shift_rows(s); add_round_key(s,rk+16*r);
  memcpy(ct,s,16);
}

int main(int argc,char**argv){
  if(argc<2){ fprintf(stderr,"usage: anchor kat | keysched <key32hex> | block <key32hex> <r> <pt32hex>\n"); return 2; }

  if(strcmp(argv[1],"kat")==0){
    /* FIPS-197 Appendix C.1: AES-128 */
    uint8_t key[16],pt[16],ct[16],rk[176];
    hex2b("000102030405060708090a0b0c0d0e0f",key,16);
    hex2b("00112233445566778899aabbccddeeff",pt,16);
    keyexpand(key,rk);
    aes128_encrypt_full(rk,pt,ct);
    char cthex[33]; b2hex(ct,16,cthex);
    const char *expect="69c4e0d86a7b0430d8cdb78070b4c55a";
    int ok = (strcmp(cthex,expect)==0);
    printf("{\"kat\":\"FIPS-197-C1\",\"key\":\"000102030405060708090a0b0c0d0e0f\",");
    printf("\"pt\":\"00112233445566778899aabbccddeeff\",\"expected_ct\":\"%s\",",expect);
    printf("\"got_ct\":\"%s\",\"pass\":%s}\n",cthex,ok?"true":"false");
    return ok?0:1;
  }

  if(strcmp(argv[1],"keysched")==0){
    if(argc<3){ fprintf(stderr,"need key32hex\n"); return 2; }
    uint8_t key[16],rk[176]; hex2b(argv[2],key,16); keyexpand(key,rk);
    char h[353]; b2hex(rk,176,h);
    printf("%s\n",h);
    return 0;
  }

  if(strcmp(argv[1],"block")==0){
    if(argc<5){ fprintf(stderr,"need key32hex r pt32hex\n"); return 2; }
    uint8_t key[16],pt[16],ct[16],rk[176];
    hex2b(argv[2],key,16); int r=atoi(argv[3]); hex2b(argv[4],pt,16);
    keyexpand(key,rk);
    aes_r_round_c1(rk,r,pt,ct);
    char cthex[33]; b2hex(ct,16,cthex);
    char rkhex[353]; b2hex(rk,176,rkhex);
    printf("{\"engine\":\"anchor_reference\",\"r\":%d,\"key\":\"%s\",\"pt\":\"%s\",\"ct\":\"%s\",\"rk\":\"%s\"}\n",
      r,argv[2],argv[4],cthex,rkhex);
    return 0;
  }

  fprintf(stderr,"unknown mode %s\n",argv[1]);
  return 2;
}
