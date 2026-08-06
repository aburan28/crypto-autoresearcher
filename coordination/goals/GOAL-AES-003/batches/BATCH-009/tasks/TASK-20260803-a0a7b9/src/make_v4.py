#!/usr/bin/env python3
"""Build yoyo_sbox_v4.c from yoyo_sbox_v3.c by PURE INSERTION.

Every edit below is an `ins(anchor, added_text)` that inserts text immediately
after an exact, unique anchor string taken verbatim from v3.  No v3 character is
ever deleted or altered.  The script asserts that each anchor occurs exactly
once and that the v3 text is a subsequence-preserving prefix-wise superset (we
verify by checking that removing all added blocks reproduces v3 byte for byte).

TASK-20260803-a0a7b9, BATCH-009.  Additions are marked  /* B9 ADDITION */.
"""
import sys, hashlib

SRC = "yoyo_sbox_v3.c.readonly_copy"
DST = "yoyo_sbox_v4.c"

v3 = open(SRC).read()
text = v3
added = []


def ins(anchor, block):
    global text
    assert text.count(anchor) == 1, ("anchor not unique: %r" % anchor[:60])
    i = text.index(anchor) + len(anchor)
    text = text[:i] + block + text[i:]
    added.append(block)


# ---------------------------------------------------------------- 1. header
ins("""#include <math.h>   /* RC-10 ADDITION (v3 only): pow() for the exact prefix nulls */
""",
"""
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
""")

# ---------------------------------------------------------------- 2. globals
ins("""/* ---------- the S-box (parameter) and its inverse ---------- */
static uint8_t SBOX[256], ISBOX[256];
""",
"""
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
""")

# ---------------------------------------------------------------- 3. job struct
ins("""    uint64_t wgek[4];
""",
"""    /* ---- B9 ADDITIONS (v4 only) ---- */
    int tid;                    /* thread index, for RC-11 pairing            */
    int idealperm;              /* 1 = ideal-permutation cipher model         */
    uint64_t seed_cipher;       /* second splitmix64 stream, ideal model only */
    uint64_t stream_gap;        /* min steps between the two streams          */
    uint64_t pdigest;           /* order-sensitive digest of the (p0,p1) stream*/
    uint64_t ideal_redraws;     /* injectivity rejections actually taken      */
    uint64_t *hits;             /* trial indices of non-trivial W>=1 hits     */
    uint64_t nhits, hitcap, hit_overflow;
""")

# ---------------------------------------------------------------- 4. worker locals
ins("""    uint8_t p0[16],p1[16],c0[16],c1[16],q0[16],q1[16],d[16];
""",
"""    /* B9 ADDITIONS (v4 only) */
    uint64_t stc = J->seed_cipher;          /* ciphertext stream, ideal only  */
    uint8_t c0o[16], c1o[16];               /* pre-swap ciphertexts, ideal only*/
    uint64_t pdig = 1469598103934665603ULL; /* FNV-1a 64 offset basis          */
""")

# ------------------------------------------------- 5. digest + ideal encryption
ins("""                if(!nz) ok=0;
            }
        }
""",
"""        /* B9 ADDITION (v4 only): order-sensitive digest of the FULL (p0,p1)
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
""")

ins("""        enc_r(p0,c0,s,r);
        enc_r(p1,c1,s,r);
""",
"""        }   /* B9 ADDITION (v4 only): closes the else of the ideal branch */
        /* B9 ADDITION (v4 only): keep the PRE-swap ciphertexts so the lazy
         * decryption can honour the two pairs already sampled. */
        if(J->idealperm){ memcpy(c0o,c0,16); memcpy(c1o,c1,16); }
""")

# ------------------------------------------------- 6. ideal decryption
ins("""                c0[i]=y; c1[i]=x;
            }
""",
"""        /* B9 ADDITION (v4 only): ideal-permutation inverse queries, exactly
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
""")

ins("""        dec_r(c0,q0,s,r);
        dec_r(c1,q1,s,r);
""",
"""        }   /* B9 ADDITION (v4 only): closes the else of the ideal branch */
""")

# ------------------------------------------------- 7. hit logging
ins("""        if(W>=1) J->wge1++;
""",
"""        /* B9 ADDITION (v4 only): RC-11 trial-index log.  Records only the
         * index; touches no counter used by any v3 field. */
        if(W>=1){
            if(J->nhits < J->hitcap) J->hits[J->nhits++] = t;
            else J->hit_overflow++;
        }
""")

# ------------------------------------------------- 8. publish digest/gap
ins("""            for(int k=1;k<=kmax;k++) J->wgek[k-1]++;
        }
    }
""",
"""    /* B9 ADDITION (v4 only): publish the stream digest computed above. */
    J->pdigest = pdig;
""")

# ------------------------------------------------- 9. load_sbox: "ideal" spec
ins("""    if(!strcmp(spec,"aes")){ build_aes_sbox(); return 1; }
""",
"""    /* B9 ADDITION (v4 only): the section 3 null object.  The AES tables are
     * still built so that verify_bijective_and_invert() and build_tables()
     * behave exactly as in v3, but NOTHING in the worker's ideal path reads
     * them: no S-box, no MixColumns, no key schedule, no round count. */
    if(!strcmp(spec,"ideal")){ IDEALPERM = 1; build_aes_sbox(); return 1; }
""")

# ------------------------------------------------- 10. arm setup
ins("""        jobs[t].rounds=rounds; jobs[t].amask=amask; jobs[t].smask=smask; jobs[t].s=&s;
""",
"""        /* ---- B9 ADDITIONS (v4 only) ---- */
        jobs[t].tid = t;
        jobs[t].idealperm = IDEALPERM;
        jobs[t].seed_cipher = jobs[t].seed_thread ^ B9_CIPHER_STREAM_OFFSET;
        jobs[t].stream_gap = b9_stream_gap(jobs[t].seed_thread, jobs[t].seed_cipher);
        jobs[t].hitcap = 4096;
        jobs[t].hits = calloc(jobs[t].hitcap, sizeof(uint64_t));
        if(!jobs[t].hits){ fprintf(stderr,"hit buffer alloc failed\\n"); return 5; }
""")

# ------------------------------------------------- 11. output block
# Inserted BEFORE the comma-less final v3 field so that v3's own output lines
# are byte-identical and still terminate the object correctly.
ins("""           (double)(N-trivial)*(1.0-pow(1.0-1.0/4294967296.0,4.0)));
""",
"""    /* ================= B9 ADDITIONS (v4 only): new output fields ========== */
    {   uint64_t gapmin = ~0ULL, redraw = 0, ovf = 0, nh = 0;
        for(int t=0;t<nthr;t++){
            if(jobs[t].stream_gap < gapmin) gapmin = jobs[t].stream_gap;
            redraw += jobs[t].ideal_redraws;
            ovf    += jobs[t].hit_overflow;
            nh     += jobs[t].nhits;
        }
        printf("  \\"cipher_model\\": \\"%s\\",\\n",
               IDEALPERM ? "ideal_permutation_lazy_128bit" : "spn_ttable_aes_structure");
        printf("  \\"ideal_permutation\\": %s,\\n", IDEALPERM ? "true" : "false");
        /* order-sensitive FNV-1a-style digest of every (p0,p1) pair, per thread */
        printf("  \\"plaintext_stream_digest\\": [");
        for(int t=0;t<nthr;t++)
            printf("\\"%016llx\\"%s",(unsigned long long)jobs[t].pdigest, t<nthr-1?",":"");
        printf("],\\n");
        printf("  \\"cipher_stream_seeds\\": [");
        for(int t=0;t<nthr;t++)
            printf("%llu%s",(unsigned long long)jobs[t].seed_cipher, t<nthr-1?",":"");
        printf("],\\n");
        printf("  \\"stream_gap_min_steps\\": %llu,\\n",(unsigned long long)gapmin);
        printf("  \\"stream_gap_min_log2\\": %.3f,\\n", gapmin? log2((double)gapmin) : -1.0);
        printf("  \\"ideal_injectivity_redraws\\": %llu,\\n",(unsigned long long)redraw);
        printf("  \\"hit_log_overflow\\": %llu,\\n",(unsigned long long)ovf);
        printf("  \\"hit_trials_logged\\": %llu,\\n",(unsigned long long)nh);
        /* RC-11: (thread, trial index) of every non-trivial W>=1 hit. */
        printf("  \\"hit_trials\\": [");
        {   int first=1;
            for(int t=0;t<nthr;t++)
                for(uint64_t i=0;i<jobs[t].nhits;i++){
                    printf("%s[%d,%llu]", first?"":",", t,
                           (unsigned long long)jobs[t].hits[i]);
                    first=0;
                }
        }
        printf("],\\n");
        printf("  \\"instrument_v4\\": \\"yoyo_sbox_v4\\",\\n");
    }
""")

# ------------------------------------------------- 12. note on the hit buffers
ins("""    free(jobs); free(th);
""",
"""    /* B9 ADDITION (v4 only): jobs[t].hits is deliberately NOT freed here.  It
     * would be a use-after-free to reach through jobs[] after free(jobs), and
     * the process exits on the next line, so the OS reclaims it.  Recorded so a
     * reader does not mistake it for an oversight. */
""")

# ---- verification: removing every added block must reproduce v3 byte for byte
check = text
for blk in added:
    assert check.count(blk) >= 1, "added block vanished"
    check = check.replace(blk, "", 1)
assert check == v3, "v4 is NOT an additions-only superset of v3"

open(DST, "w").write(text)
print("v3 sha256:", hashlib.sha256(v3.encode()).hexdigest())
print("v4 sha256:", hashlib.sha256(text.encode()).hexdigest())
print("v3 bytes:", len(v3), " v4 bytes:", len(text), " added:", len(text) - len(v3))
print("ADDITIONS-ONLY VERIFIED: deleting the %d inserted blocks reproduces v3 exactly."
      % len(added))
