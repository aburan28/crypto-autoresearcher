# PREREGISTRATION — Identity/affine S-box arm (BATCH-b41ba9, TASK-20260806-47f217)

Written BEFORE any arm cipher call of this task. Frozen at task start
(2026-08-07T00:01Z). The algebraic prediction below was computed in code
(`algebra_rank.py`, run 2026-08-07T00:01Z) BEFORE this text; the first
`probe_sbox` cipher call of the arm happens after this text.

## Task

TASK-20260806-47f217, batch BATCH-b41ba9, goal GOAL-AES-003. Executor role.

## Question (the Red Team's cheapest next discriminator)

BATCH-713991 (closed, DEC-20260804-73977c) established that the r=5 yoyo
excess is NOT attributable to the AES S-box table's values: AES W=59, random
bijective sbox seeds 424242201/424242202 W=58/51, all vs null expectation
4.0 at N=2^32, controls pass. The untested class boundary is
identity/affine: with SBOX[i]=i the cipher is **affine over GF(2)**, so the
expected W>=1 count is COMPUTABLE IN ADVANCE from the 32x32 GF(2) word-map
structure. This arm decides whether ANY nonlinearity is required for the
excess.

## Instrument (frozen)

`probe_sbox.c` — byte-identical copy of BATCH-713991's
`TASK-20260804-f5e58b/probe_sbox.c` with ONE substantive edit (the identity
S-box table construction) plus the mandated plumbing (pinidentity mode,
`identity` arm selector, usage string) and a provenance header comment.
Round geometry, MixColumns, ShiftRows, RNG (splitmix64), key schedule, trial
logic, worker threads, statistics: IDENTICAL to the source.

- Geometry: PW[j]={4*((j+row)%4)+row}, CW[j]={4*((j-row)%4)+row}.
- Trial: p0 uniform; p1=p0 with bytes of words in amask re-randomised (zero
  word-diff rejected); c0=enc_r(p0), c1=enc_r(p1); swap ciphertext bytes of
  words in smask between c0,c1 (trivial swap detected and excluded);
  q0=dec_r(c0), q1=dec_r(c1); d=q0^q1; Z=#zero-diff bytes; W=#words (over
  PW, all 4) with all-zero diff bytes.
- Null (random-permutation model, BATCH-002 sec.3): per-trial P(W>=1) =
  4*2^-32 = 2^-30; expected count 4.0 at N=2^32; excess = W_ge1 /
  (nontrivial_trials * 2^-30).

## The exact source diff (one hive edit)

`diff` of the source (`BATCH-713991/tasks/TASK-20260804-f5e58b/probe_sbox.c`)
against this task's `probe_sbox.c` (121 lines; the substantive hunk is the
identity table construction; the other hunks are the mandated plumbing and
the provenance header):

```
1,2c1,2
< /* TASK-20260804-f5e58b -- RANK 3 S-box probe (probe_sbox.c)
<  * GOAL-AES-003, batch BATCH-713991. Executor role.
---
> /* TASK-20260806-47f217 -- IDENTITY/affine S-box probe (probe_sbox.c)
>  * GOAL-AES-003, batch BATCH-b41ba9. Executor role.
4,19c4,12
<  * Fully software AES-shaped SPN with a REPLACEABLE global SBOX[]. Port of
<  * BATCH-002's probe.c (TASK-20260802-e4fa63) from AES-NI intrinsics
<  * (_mm_aesenc/_mm_aesdec/_mm_aesimc) to byte-table software, so the S-box
<  * can be swapped between
<  *   (a) the AES S-box: computed at runtime from GF(2^8) inverse + FIPS-197
<  *       affine map -- exactly build_sbox() of probe.c -- and
<  *   (b) uniform random bijective permutations over 0..255, drawn with
<  *       splitmix64 (sm64, same function as probe.c) from RECORDED seeds,
<  *       verified bijective (inverse maps back) before use.
<  *
<  * The trial geometry, RNG, key schedule, worker loop and statistics are
<  * ported line-for-line from probe.c. The ONLY semantic changes are:
<  *   - enc_r/dec_r: software byte rounds instead of AES-NI intrinsics;
<  *   - sched: plain round-key array (no aesimc folding; the software
<  *     decryption applies InvMixColumns directly);
<  *   - global SBOX/INV_SBOX plus S-box selection and recording.
---
>  * Copy of TASK-20260804-f5e58b's probe_sbox.c (BATCH-713991) with ONE
>  * substantive edit: the arm's S-box table is the identity map SBOX[i]=i
>  * (set_identity_sbox), making the cipher affine over GF(2) so the r=5 yoyo
>  * W-count is algebraically computable in advance. Round geometry,
>  * MixColumns, ShiftRows, RNG, trial logic, worker threads are identical to
>  * the source. The AES construction path (build_sbox/set_aes_sbox) and the
>  * random path (set_random_sbox) are intact and reachable; `pin` still
>  * FIPS-197-pins the AES path, `pinsbox` the random paths, and the new
>  * `pinidentity` pins identity-table bijectivity + r=1..10 roundtrips.
132a126,139
> }
>
> /* ---------- identity S-box (TASK-20260806-47f217 hive edit) ----------
>  * The ONE substantive edit of this task: the S-box table construction used
>  * by the arm is the identity map SBOX[i]=i for i in 0..255, which makes the
>  * whole cipher affine over GF(2). The affine/inverse construction path of
>  * build_sbox() is left intact and unused by the arm; it stays reachable via
>  * set_aes_sbox() so the `pin` mode keeps FIPS-197-pinning the genuine AES
>  * path. set_random_sbox() is likewise intact and reachable (pinsbox, arm
>  * with a numeric seed). */
> static void set_identity_sbox(void){
>     for(int i=0;i<256;i++) SBOX[i]=(uint8_t)i;
>     build_inv_sbox();
>     snprintf(SBOX_LABEL,sizeof(SBOX_LABEL),"identity");
448a456,503
> /* ---------- pin for the identity S-box: bijectivity (trivial) + r=1..10
>  * roundtrips dec(enc(x,key,r))==x on 512 random (key,plaintext) vectors.
>  * The FIPS-197 KAT does not apply to the identity table (it pins the AES
>  * table's values); what the identity arm needs pinned is that the identity
>  * table roundtrips exactly like any other bijective table. */
> static int pinidentity(uint64_t seed){
>     set_identity_sbox();
>     int bijective = build_inv_sbox();
>     const uint8_t kat_key[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
>     const uint8_t kat_pt[16]={0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77,
>                               0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
>     sched s; sched_init(kat_key,&s);
>     uint8_t y[16];
>     printf("{\n  \"mode\": \"pinidentity\",\n  \"sbox\": \"%s\",\n", SBOX_LABEL);
>     printf("  \"sbox_bijective\": %s,\n", bijective?"true":"false");
>     printf("  \"sbox_table_hex\": \"");
>     print_sbox_hex();
>     printf("\",\n  \"inv_sbox_table_hex\": \"");
>     print_inv_sbox_hex();
>     printf("\",\n  \"sbox_first8\": [");
>     for(int i=0;i<8;i++) printf("%d%s",SBOX[i], i<7?",":"");
>     printf("],\n");
>     /* roundtrips dec(enc(x,key,r))==x for r=1..10, 512 random vectors */
>     uint64_t st=seed; int nvec=512, fails=0; uint64_t first_fail_r=0;
>     for(int v=0;v<nvec;v++){
>         uint8_t k[16], pt[16];
>         for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(k+i,&z,8); }
>         for(int i=0;i<16;i+=8){ uint64_t z=sm64(&st); memcpy(pt+i,&z,8); }
>         sched sv; sched_init(k,&sv);
>         for(int r=1;r<=10;r++){
>             uint8_t a[16], c[16], e[16];
>             memcpy(a,pt,16);
>             enc_r(c,a,&sv,r);
>             dec_r(e,c,&sv,r);
>             if(memcmp(e,pt,16)!=0){ fails++; if(!first_fail_r) first_fail_r=r; }
>         }
>     }
>     printf("  \"roundtrip_vectors\": %d,\n", nvec);
>     printf("  \"roundtrip_rounds_each\": \"1..10\",\n");
>     printf("  \"roundtrip_checks\": %d,\n", nvec*10);
>     printf("  \"roundtrip_failures\": %d,\n", fails);
>     printf("  \"roundtrip_first_failure_round\": %llu,\n",(unsigned long long)first_fail_r);
>     printf("  \"pin_seed\": %llu,\n",(unsigned long long)seed);
>     printf("  \"pin_pass\": %s\n", (bijective && fails==0)?"true":"false");
>     printf("}\n");
>     return (bijective && fails==0)?0:1;
> }
>
463c518
<     if(argc<2){ fprintf(stderr,"usage: probe_sbox pin <seed> | probe_sbox pinsbox <seed> | probe_sbox geom | probe_sbox arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads> [aes|sboxseed]\n"); return 2; }
---
>     if(argc<2){ fprintf(stderr,"usage: probe_sbox pin <seed> | probe_sbox pinsbox <seed> | probe_sbox pinidentity <seed> | probe_sbox geom | probe_sbox arm <name> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads> [aes|identity|sboxseed]\n"); return 2; }
472a528,531
>     if(!strcmp(argv[1],"pinidentity")){
>         uint64_t seed=strtoull(argv[2],NULL,10);
>         return pinidentity(seed);
>     }
481,482c540,542
<     /* S-box selection: argv[10] = "aes" (default) or a seed for a random
<      * bijective draw. Also verifies bijectivity of the selected table. */
---
>     /* S-box selection: argv[10] = "aes" (default), "identity", or a seed
>      * for a random bijective draw. Also verifies bijectivity of the
>      * selected table. */
484c544
<     if(argc>=11 && strcmp(argv[10],"aes")!=0){
---
>     if(argc>=11 && strcmp(argv[10],"aes")!=0 && strcmp(argv[10],"identity")!=0){
486a547,549
>     } else if(argc>=11 && strcmp(argv[10],"identity")==0){
>         set_identity_sbox();
>         sbox_ok = 1;
```

(Note: the diff above is the verbatim `diff` output; the `>`-prefixed lines
are the new file. The one substantive edit is the identity table
construction `set_identity_sbox()`; the remaining hunks are the mandated
plumbing — `pinidentity` mode, `identity` arm selector, usage string — and
the provenance header comment. No line of round geometry, MixColumns,
ShiftRows, RNG, key schedule, trial logic, worker thread or statistics code
was changed.)

## Frozen arm spec (ONE arm)

| Field | Value |
|-------|-------|
| arm name | ID5 |
| rounds | 5 |
| amask | 1 (word 0) |
| smask | 1 (word 0) |
| N | 2^32 (log2N=32) |
| threads | 8 |
| arm_id | 301 |
| sbox | identity (SBOX[i]=i) |
| master seed | **189001301** (executed; see seed note) |

**Seed note (recorded discrepancy, not silently resolved).** The task text's
frozen-arm-spec bullet names "fresh master seed = 424242301", while the
mandated run command is `./probe_sbox arm ID5 5 1 1 32 189001301 301 8
identity`. Both seeds are fresh (unused in the campaign before). The
executed command is the mandated one, verbatim, so the executed master seed
is **189001301**; the JSON receipt records it. The algebraic expectation E
is a function of the cipher's GF(2) matrix structure only — it does not
depend on the RNG seed — so this discrepancy cannot affect the prediction or
the classification. Both values are recorded here and in results.json.

## Algebraic prediction (frozen, computed in code BEFORE this text)

With SBOX = identity every component (SubBytes, ShiftRows, MixColumns,
AddRoundKey) is affine over GF(2), so E_K(x) = M·x + b and D_K(y) =
M^{-1}·y + b'. The trial's swap of ciphertext bytes at CW[0] preserves the
ciphertext XOR difference (swapping bytes between two vectors leaves their
pairwise XOR unchanged), so:

  q0 ^ q1 = M^{-1}·(c0' ^ c1') = M^{-1}·M·(p0 ^ p1) = p0 ^ p1.

The word-j map A_j : (p0^p1)|PW[0] -> (q0^q1)|PW[j] is therefore
P_j·(D·M)·P_0^T. `algebra_rank.py` built the exact 128x128 GF(2) matrices M
(enc, zeroed constants) and D (dec, zeroed constants) from the cipher's
byte-level structure (ported line-for-line from probe_sbox.c), verified
D·M = M·D = I numerically, and computed the four 32x32 word maps and their
ranks:

| word j | 32x32 map A_j | rank | nullity | P(word j zero) = 2^-rank |
|--------|---------------|------|---------|---------------------------|
| 0 | identity (P_0·P_0^T) | **32** | 0 | 2^-32 ≈ 2.33e-10 |
| 1 | zero map | **0** | 32 | 1 |
| 2 | zero map | **0** | 32 | 1 |
| 3 | zero map | **0** | 32 | 1 |

Frozen expectation (per the 2^-rank formula, E[W] = Σ_j 2^-rank_j):

- **E[W] per trial = 3.000000000233** (3 + 2^-32).
- **E[W_ge1] per trial = 1.0 EXACTLY**: the worker rejects an all-equal
  word-0 re-randomisation, so the word-0 diff is conditioned NONZERO and the
  identity word-0 map never outputs zero; words 1..3 are deterministic zeros.
- **E[W_ge1 count] at N=2^32 = nontrivial_trials ≈ 4,294,967,295** (2^32
  minus ~1 expected trivial swap; the trivial-swap map word-0-diff ->
  (M·diff)|CW[0] has rank 32, so E[trivial] = 2^32·2^-32 = 1.0).
- **excess_E = W_ge1/(nontrivial·2^-30) = 2^30 = 1,073,741,824**.
- Predicted histograms: whist = [0, 0, 0, nontrivial, 0]; zhist[12] ≈
  nontrivial (words 1-3 fully equal; word 0 contributes 0-3 equal bytes).

The byte-level claim q0^q1 = p0^p1 and W=3 was additionally confirmed
empirically in the same script on 2000 random trials of the full affine
cipher with a real key (2000/2000 qdiff==pdiff, 2000/2000 W=3,
whist=[0,0,0,2000,0]).

## Classification rule (pre-committed, per DEC-20260804-73977c D-5 and the Red Team)

- **NO-NONLINEARITY-REQUIRED**: measured W_ge1 count inside the observed
  [40,70] band, OR (as computed here) at the algebraic prediction E ≈ 2^32 —
  i.e., the excess persists (indeed maximally) with a fully affine cipher, so
  no S-box nonlinearity is required for the yoyo excess.
- **NONLINEARITY-REQUIRED**: measured count within the Poisson CI of the
  null expectation ~4 (i.e. the excess vanishes without nonlinearity),
  narrowing the claim to "independence among nonlinear bijections".

The Red Team's two-band rule anticipated E ≈ 4; the computed E ≈ 2^32 lies
outside both forecast bands, so the pre-committed reading is: a count at
E ≈ 2^32 (W=3 per trial) is the extreme "no nonlinearity required" outcome;
a count ≈ 4 is "nonlinearity required". The measured count is compared to E
and the classification is stated plainly.

## Pins (frozen, all REQUIRED before the arm)

1. `pin <seed>` — FIPS-197 C.1 KAT at r=10 and r=5 anchor, roundtrips: the
   AES path is preserved (build_sbox/set_aes_sbox untouched), so this must
   still PASS. The FIPS-197 KAT does not apply to the identity table (it
   pins the AES table's values); that is recorded, not a failure.
2. `pinsbox <seed>` — random path preserved: bijectivity + roundtrips must
   still PASS.
3. `pinidentity <seed>` — NEW: identity table bijectivity (trivial true) and
   dec(enc(x,key,r))==x for r=1..10 on 512 random vectors, zero failures.
4. Calibration arm (recorded as calibration, NOT an arm): N=2^20 identity
   run must show whist=[0,0,0,N,0] and W_ge1=nontrivial, confirming the
   algebraic prediction at small scale before the frozen arm.

## Tier / scope / prohibitions

TOY TIER. No statement about full-round or deployed AES (RQ-AES-003 R3); no
promotion or dismissal of any hypothesis (executor role). Edit NO prior-batch
artifact and nothing outside this task's write_scope (in particular nothing
under BATCH-713991). No git. Structured artifacts must parse (JSON validated
with python3 json.load).

## Inference block

policy: executor-implementation; requested_policy: executor-implementation;
resolved_model: deepseek-v4-flash-free (ACTUAL model serving this session,
self-reported from session context; no adapter probe run);
fallback_used: false; model_verified: false; standing_basis: source
TASK-20260804-f5e58b (BATCH-713991).

## Budget

2700 s wall clock, 8 GB, max 2 runs (1 arm + calibration). HALT at
binding_stop; partial results reported as measured, never as nulls.