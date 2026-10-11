/*
 * AArch64 Keccak-p[1600] x1 implementation.
 *
 * Two compilation paths selected at compile time:
 *
 *   __ARM_FEATURE_SHA3 defined (e.g. -march=armv8-a+sha3):
 *     SHA3-accelerated path.
 *     - theta: scalar column parities + RAX1 for D[x] computation (2 NEON ops for D[0..3])
 *     - rho+theta+pi: fully scalar (all 25 rotation constants are distinct)
 *     - chi: BCAX for rows pairwise (y=0,1) and (y=2,3), scalar for y=4
 *     - State remains scalar uint64_t[25] (standard 200-byte linear SnP format)
 *
 *   __ARM_FEATURE_SHA3 not defined:
 *     Delegates entirely to opt64/KeccakP-1600-opt64.c (generic 64-bit C).
 *     The compiler may still auto-generate BIC/EOR from the ~B & C patterns.
 *
 * Both paths use the standard SnP state: 200 bytes, 8-byte aligned, no lane
 * complementing, little-endian lanes.  The SnP interface is identical to opt64.
 */

#include <stdint.h>
#include <string.h>
#include <stddef.h>
#include "brg_endian.h"
#include "KeccakP-1600-opt64-config.h"
#include "SnP-Relaned.h"

#ifdef __ARM_FEATURE_SHA3

#include <arm_neon.h>

/* ----------------------------------------------------------------
 * Round constants
 * ---------------------------------------------------------------- */
static const uint64_t KeccakRC[24] = {
    0x0000000000000001ULL, 0x0000000000008082ULL,
    0x800000000000808aULL, 0x8000000080008000ULL,
    0x000000000000808bULL, 0x0000000080000001ULL,
    0x8000000080008081ULL, 0x8000000000008009ULL,
    0x000000000000008aULL, 0x0000000000000088ULL,
    0x0000000080008009ULL, 0x000000008000000aULL,
    0x000000008000808bULL, 0x800000000000008bULL,
    0x8000000000008089ULL, 0x8000000000008003ULL,
    0x8000000000008002ULL, 0x8000000000000080ULL,
    0x000000000000800aULL, 0x800000008000000aULL,
    0x8000000080008081ULL, 0x8000000000008080ULL,
    0x0000000080000001ULL, 0x8000000080008008ULL,
};

/* ----------------------------------------------------------------
 * One Keccak round with SHA3 intrinsics
 *
 * theta:   scalar column parities; RAX1 for D[0..3] (2 NEON ops), scalar for D[4]
 * rho+pi: fully scalar (rotation constants are all distinct; XAR would need the same
 *      imm for both NEON lanes, which never occurs here)
 * chi:   BCAX on row pairs (y=0,1) and (y=2,3) -> 5 BCAX each; scalar for y=4
 * iota:   scalar XOR
 * ---------------------------------------------------------------- */
#define ROL64(a, n) (((uint64_t)(a) << (n)) | ((uint64_t)(a) >> (64 - (n))))

static void keccak_round_sha3(uint64_t A[25], uint64_t rc)
{
    /* ---- theta: column parities ---- */
    uint64_t c0 = A[0]  ^ A[5]  ^ A[10] ^ A[15] ^ A[20];
    uint64_t c1 = A[1]  ^ A[6]  ^ A[11] ^ A[16] ^ A[21];
    uint64_t c2 = A[2]  ^ A[7]  ^ A[12] ^ A[17] ^ A[22];
    uint64_t c3 = A[3]  ^ A[8]  ^ A[13] ^ A[18] ^ A[23];
    uint64_t c4 = A[4]  ^ A[9]  ^ A[14] ^ A[19] ^ A[24];

    /* D[x] = C[x-1] ^ ROL(C[x+1], 1) via RAX1:
     *   vrax1q_u64(a, b) = { a[0] ^ ROL(b[0], 1), a[1] ^ ROL(b[1], 1) }
     *   {D[0], D[2]} = rax1({C[4], C[1]}, {C[1], C[3]})
     *   {D[1], D[3]} = rax1({C[0], C[2]}, {C[2], C[4]})
     */
    uint64x2_t vD02 = vrax1q_u64((uint64x2_t){c4, c1}, (uint64x2_t){c1, c3});
    uint64x2_t vD13 = vrax1q_u64((uint64x2_t){c0, c2}, (uint64x2_t){c2, c4});
    uint64_t d0 = vgetq_lane_u64(vD02, 0);
    uint64_t d1 = vgetq_lane_u64(vD13, 0);
    uint64_t d2 = vgetq_lane_u64(vD02, 1);
    uint64_t d3 = vgetq_lane_u64(vD13, 1);
    uint64_t d4 = c3 ^ ROL64(c0, 1);

    /* ---- theta + rho + pi combined into B (pi-permuted output positions) ----
     *
     * For each lane at old index i (x=i%5, y=i/5):
     *   B[new_idx] = ROL(A[i] ^ D[x], rho_offset)
     *
     * Mapping old->new and rotation offsets (computed from Keccak spec):
     *   0->0(0)   1->10(1)   2->20(62)  3->5(28)   4->15(27)
     *   5->16(36) 6->1(44)   7->11(6)   8->21(55)  9->6(20)
     *   10->7(3)  11->17(10) 12->2(43)  13->12(25) 14->22(39)
     *   15->23(41)16->8(45)  17->18(15) 18->3(21)  19->13(8)
     *   20->14(18)21->24(2)  22->9(61)  23->19(56) 24->4(14)
     */
    uint64_t B[25];
    B[0]  =          A[0]  ^ d0;
    B[10] = ROL64(   A[1]  ^ d1,  1);
    B[20] = ROL64(   A[2]  ^ d2, 62);
    B[5]  = ROL64(   A[3]  ^ d3, 28);
    B[15] = ROL64(   A[4]  ^ d4, 27);
    B[16] = ROL64(   A[5]  ^ d0, 36);
    B[1]  = ROL64(   A[6]  ^ d1, 44);
    B[11] = ROL64(   A[7]  ^ d2,  6);
    B[21] = ROL64(   A[8]  ^ d3, 55);
    B[6]  = ROL64(   A[9]  ^ d4, 20);
    B[7]  = ROL64(   A[10] ^ d0,  3);
    B[17] = ROL64(   A[11] ^ d1, 10);
    B[2]  = ROL64(   A[12] ^ d2, 43);
    B[12] = ROL64(   A[13] ^ d3, 25);
    B[22] = ROL64(   A[14] ^ d4, 39);
    B[23] = ROL64(   A[15] ^ d0, 41);
    B[8]  = ROL64(   A[16] ^ d1, 45);
    B[18] = ROL64(   A[17] ^ d2, 15);
    B[3]  = ROL64(   A[18] ^ d3, 21);
    B[13] = ROL64(   A[19] ^ d4,  8);
    B[14] = ROL64(   A[20] ^ d0, 18);
    B[24] = ROL64(   A[21] ^ d1,  2);
    B[9]  = ROL64(   A[22] ^ d2, 61);
    B[19] = ROL64(   A[23] ^ d3, 56);
    B[4]  = ROL64(   A[24] ^ d4, 14);

    /* ---- chi: A[x,y] = B[x,y] ^ (~B[x+1,y] & B[x+2,y])
     *            = bcax(B[x,y], B[x+2,y], B[x+1,y])
     *
     * Pack two adjacent rows into NEON lanes: lane-0 = row y, lane-1 = row y+1.
     * Each BCAX then computes two chi outputs (one per row) simultaneously.
     */
    for (int y = 0; y < 4; y += 2) {
        int b = y * 5;
        uint64x2_t vB0 = (uint64x2_t){ B[b+0], B[b+5] };
        uint64x2_t vB1 = (uint64x2_t){ B[b+1], B[b+6] };
        uint64x2_t vB2 = (uint64x2_t){ B[b+2], B[b+7] };
        uint64x2_t vB3 = (uint64x2_t){ B[b+3], B[b+8] };
        uint64x2_t vB4 = (uint64x2_t){ B[b+4], B[b+9] };
        uint64x2_t vA0 = vbcaxq_u64(vB0, vB2, vB1);
        uint64x2_t vA1 = vbcaxq_u64(vB1, vB3, vB2);
        uint64x2_t vA2 = vbcaxq_u64(vB2, vB4, vB3);
        uint64x2_t vA3 = vbcaxq_u64(vB3, vB0, vB4);
        uint64x2_t vA4 = vbcaxq_u64(vB4, vB1, vB0);
        A[b+0] = vgetq_lane_u64(vA0, 0);  A[b+5] = vgetq_lane_u64(vA0, 1);
        A[b+1] = vgetq_lane_u64(vA1, 0);  A[b+6] = vgetq_lane_u64(vA1, 1);
        A[b+2] = vgetq_lane_u64(vA2, 0);  A[b+7] = vgetq_lane_u64(vA2, 1);
        A[b+3] = vgetq_lane_u64(vA3, 0);  A[b+8] = vgetq_lane_u64(vA3, 1);
        A[b+4] = vgetq_lane_u64(vA4, 0);  A[b+9] = vgetq_lane_u64(vA4, 1);
    }
    /* y=4 (indices 20-24): scalar */
    A[20] = B[20] ^ (~B[21] & B[22]);
    A[21] = B[21] ^ (~B[22] & B[23]);
    A[22] = B[22] ^ (~B[23] & B[24]);
    A[23] = B[23] ^ (~B[24] & B[20]);
    A[24] = B[24] ^ (~B[20] & B[21]);

    /* ---- iota ---- */
    A[0] ^= rc;
}

#undef ROL64

/* Apply nrounds starting from round index start_round. */
static void keccak_permute_sha3(uint64_t A[25], unsigned int start_round,
                                 unsigned int nrounds)
{
    for (unsigned int i = start_round; i < start_round + nrounds; i++)
        keccak_round_sha3(A, KeccakRC[i]);
}

/* ----------------------------------------------------------------
 * Public SnP permutation interface
 * ---------------------------------------------------------------- */
void KeccakP1600_Permute_24rounds(void *state)
{
    keccak_permute_sha3((uint64_t *)state, 0, 24);
}

void KeccakP1600_Permute_12rounds(void *state)
{
    keccak_permute_sha3((uint64_t *)state, 12, 12);
}

void KeccakP1600_Permute_Nrounds(void *state, unsigned int nrounds)
{
    keccak_permute_sha3((uint64_t *)state, 24 - nrounds, nrounds);
}

/* ----------------------------------------------------------------
 * Fast absorb loops (call our permutation, keep state in a local copy
 * to avoid pointer-aliasing overhead across loop iterations)
 * ---------------------------------------------------------------- */
size_t KeccakF1600_FastLoop_Absorb(void *state, unsigned int laneCount,
                                    const unsigned char *data, size_t dataByteLen)
{
    size_t initialLen = dataByteLen;
    uint64_t localState[25];

    memcpy(localState, state, 200);
    while (dataByteLen >= laneCount * 8) {
        for (unsigned int i = 0; i < laneCount; i++) {
            uint64_t lane;
            memcpy(&lane, data + i * 8, 8);
            localState[i] ^= lane;
        }
        keccak_permute_sha3(localState, 0, 24);
        data        += laneCount * 8;
        dataByteLen -= laneCount * 8;
    }
    memcpy(state, localState, 200);
    return initialLen - dataByteLen;
}

size_t KeccakP1600_12rounds_FastLoop_Absorb(void *state, unsigned int laneCount,
                                             const unsigned char *data, size_t dataByteLen)
{
    size_t initialLen = dataByteLen;
    uint64_t localState[25];

    memcpy(localState, state, 200);
    while (dataByteLen >= laneCount * 8) {
        for (unsigned int i = 0; i < laneCount; i++) {
            uint64_t lane;
            memcpy(&lane, data + i * 8, 8);
            localState[i] ^= lane;
        }
        keccak_permute_sha3(localState, 12, 12);
        data        += laneCount * 8;
        dataByteLen -= laneCount * 8;
    }
    memcpy(state, localState, 200);
    return initialLen - dataByteLen;
}

/* ----------------------------------------------------------------
 * SnP memory functions  - identical to opt64 (same state layout).
 * ---------------------------------------------------------------- */
void KeccakP1600_Initialize(void *state)
{
    memset(state, 0, 200);
}

void KeccakP1600_AddBytesInLane(void *state, unsigned int lanePosition,
                                 const unsigned char *data, unsigned int offset,
                                 unsigned int length)
{
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
    uint64_t lane;
    if (length == 0) return;
    if (length == 1) {
        lane = data[0];
    } else {
        lane = 0;
        memcpy(&lane, data, length);
    }
    lane <<= offset * 8;
#else
    uint64_t lane = 0;
    for (unsigned int i = 0; i < length; i++)
        lane |= ((uint64_t)data[i]) << ((i + offset) * 8);
#endif
    ((uint64_t *)state)[lanePosition] ^= lane;
}

void KeccakP1600_AddLanes(void *state, const unsigned char *data, unsigned int laneCount)
{
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
    unsigned int i = 0;
#ifdef NO_MISALIGNED_ACCESSES
    if (((uintptr_t)state & 7) || ((uintptr_t)data & 7)) {
        for (i = 0; i < laneCount * 8; i++)
            ((unsigned char *)state)[i] ^= data[i];
        return;
    }
#endif
    for (; i + 4 <= laneCount; i += 4) {
        ((uint64_t *)state)[i+0] ^= ((const uint64_t *)data)[i+0];
        ((uint64_t *)state)[i+1] ^= ((const uint64_t *)data)[i+1];
        ((uint64_t *)state)[i+2] ^= ((const uint64_t *)data)[i+2];
        ((uint64_t *)state)[i+3] ^= ((const uint64_t *)data)[i+3];
    }
    for (; i < laneCount; i++)
        ((uint64_t *)state)[i] ^= ((const uint64_t *)data)[i];
#else
    for (unsigned int i = 0; i < laneCount; i++) {
        const unsigned char *p = data + i * 8;
        uint64_t lane = (uint64_t)p[0] | ((uint64_t)p[1] << 8) | ((uint64_t)p[2] << 16)
                      | ((uint64_t)p[3] << 24) | ((uint64_t)p[4] << 32)
                      | ((uint64_t)p[5] << 40) | ((uint64_t)p[6] << 48)
                      | ((uint64_t)p[7] << 56);
        ((uint64_t *)state)[i] ^= lane;
    }
#endif
}

#if (PLATFORM_BYTE_ORDER != IS_LITTLE_ENDIAN)
void KeccakP1600_AddByte(void *state, unsigned char byte, unsigned int offset)
{
    uint64_t lane = (uint64_t)byte << ((offset % 8) * 8);
    ((uint64_t *)state)[offset / 8] ^= lane;
}
#endif

void KeccakP1600_AddBytes(void *state, const unsigned char *data,
                           unsigned int offset, unsigned int length)
{
    SnP_AddBytes(state, data, offset, length,
                 KeccakP1600_AddLanes, KeccakP1600_AddBytesInLane, 8);
}

void KeccakP1600_OverwriteBytesInLane(void *state, unsigned int lanePosition,
                                       const unsigned char *data, unsigned int offset,
                                       unsigned int length)
{
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
    memcpy((unsigned char *)state + lanePosition * 8 + offset, data, length);
#else
    uint64_t lane = ((uint64_t *)state)[lanePosition];
    for (unsigned int i = 0; i < length; i++) {
        lane &= ~((uint64_t)0xFF << ((offset + i) * 8));
        lane |= (uint64_t)data[i] << ((offset + i) * 8);
    }
    ((uint64_t *)state)[lanePosition] = lane;
#endif
}

void KeccakP1600_OverwriteLanes(void *state, const unsigned char *data,
                                 unsigned int laneCount)
{
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
    memcpy(state, data, laneCount * 8);
#else
    for (unsigned int i = 0; i < laneCount; i++) {
        const unsigned char *p = data + i * 8;
        ((uint64_t *)state)[i] = (uint64_t)p[0] | ((uint64_t)p[1] << 8)
            | ((uint64_t)p[2] << 16) | ((uint64_t)p[3] << 24)
            | ((uint64_t)p[4] << 32) | ((uint64_t)p[5] << 40)
            | ((uint64_t)p[6] << 48) | ((uint64_t)p[7] << 56);
    }
#endif
}

void KeccakP1600_OverwriteBytes(void *state, const unsigned char *data,
                                 unsigned int offset, unsigned int length)
{
    SnP_OverwriteBytes(state, data, offset, length,
                       KeccakP1600_OverwriteLanes, KeccakP1600_OverwriteBytesInLane, 8);
}

void KeccakP1600_OverwriteWithZeroes(void *state, unsigned int byteCount)
{
    memset(state, 0, byteCount);
}

void KeccakP1600_ExtractBytesInLane(const void *state, unsigned int lanePosition,
                                     unsigned char *data, unsigned int offset,
                                     unsigned int length)
{
    uint64_t lane = ((const uint64_t *)state)[lanePosition];
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
    memcpy(data, (const uint8_t *)&lane + offset, length);
#else
    lane >>= offset * 8;
    for (unsigned int i = 0; i < length; i++) {
        data[i] = lane & 0xFF;
        lane >>= 8;
    }
#endif
}

void KeccakP1600_ExtractLanes(const void *state, unsigned char *data,
                               unsigned int laneCount)
{
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
    memcpy(data, state, laneCount * 8);
#else
    for (unsigned int i = 0; i < laneCount; i++) {
        uint64_t lane = ((const uint64_t *)state)[i];
        unsigned char *p = data + i * 8;
        for (int j = 0; j < 8; j++) { p[j] = lane & 0xFF; lane >>= 8; }
    }
#endif
}

void KeccakP1600_ExtractBytes(const void *state, unsigned char *data,
                               unsigned int offset, unsigned int length)
{
    SnP_ExtractBytes(state, data, offset, length,
                     KeccakP1600_ExtractLanes, KeccakP1600_ExtractBytesInLane, 8);
}

void KeccakP1600_ExtractAndAddBytesInLane(const void *state, unsigned int lanePosition,
                                           const unsigned char *input, unsigned char *output,
                                           unsigned int offset, unsigned int length)
{
    uint64_t lane = ((const uint64_t *)state)[lanePosition];
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
    for (unsigned int i = 0; i < length; i++)
        output[i] = input[i] ^ ((const uint8_t *)&lane)[offset + i];
#else
    lane >>= offset * 8;
    for (unsigned int i = 0; i < length; i++) {
        output[i] = input[i] ^ (lane & 0xFF);
        lane >>= 8;
    }
#endif
}

void KeccakP1600_ExtractAndAddLanes(const void *state, const unsigned char *input,
                                     unsigned char *output, unsigned int laneCount)
{
    const uint64_t *stateAsLanes = (const uint64_t *)state;  /* state is always 8-byte aligned */
    for (unsigned int i = 0; i < laneCount; i++) {
        uint64_t lane_in, lane_out;
        memcpy(&lane_in, input + i * 8, 8);
        lane_out = stateAsLanes[i] ^ lane_in;
        memcpy(output + i * 8, &lane_out, 8);
    }
}

void KeccakP1600_ExtractAndAddBytes(const void *state, const unsigned char *input,
                                     unsigned char *output, unsigned int offset,
                                     unsigned int length)
{
    SnP_ExtractAndAddBytes(state, input, output, offset, length,
                           KeccakP1600_ExtractAndAddLanes,
                           KeccakP1600_ExtractAndAddBytesInLane, 8);
}

#else /* __ARM_FEATURE_SHA3 not defined */

/* Plain C fallback: opt64 provides all functions except FastLoop_Absorb.
 * We skip opt64's FastLoop and provide our own alignment-safe versions below
 * (opt64 casts data directly to uint64_t*, which UBSan flags on strict-alignment
 * platforms when the caller provides an unaligned pointer). */
#define KeccakP1600_no_FastLoop
#include "opt64/KeccakP-1600-opt64.c"
#undef KeccakP1600_no_FastLoop

/* opt64.c exports KeccakP1600_plain64_* symbols and its SnP header defines the
 * KeccakP1600_* names as macros. aarch64/KeccakP-1600-SnP.h (included by KeccakSponge.c
 * and times4.c) declares KeccakP1600_* as real functions, so we undef the macros and
 * provide thin wrappers to satisfy the linker for the no-SHA3 fallback path. */
#undef KeccakP1600_Initialize
#undef KeccakP1600_AddBytes
#undef KeccakP1600_OverwriteBytes
#undef KeccakP1600_OverwriteWithZeroes
#undef KeccakP1600_Permute_Nrounds
#undef KeccakP1600_Permute_12rounds
#undef KeccakP1600_Permute_24rounds
#undef KeccakP1600_ExtractBytes
#undef KeccakP1600_ExtractAndAddBytes
void KeccakP1600_Initialize(void *state) {
    KeccakP1600_plain64_Initialize((KeccakP1600_plain64_state *)state);
}
void KeccakP1600_AddBytes(void *state, const unsigned char *data, unsigned int offset, unsigned int length) {
    KeccakP1600_plain64_AddBytes((KeccakP1600_plain64_state *)state, data, offset, length);
}
void KeccakP1600_OverwriteBytes(void *state, const unsigned char *data, unsigned int offset, unsigned int length) {
    KeccakP1600_plain64_OverwriteBytes((KeccakP1600_plain64_state *)state, data, offset, length);
}
void KeccakP1600_OverwriteWithZeroes(void *state, unsigned int byteCount) {
    KeccakP1600_plain64_OverwriteWithZeroes((KeccakP1600_plain64_state *)state, byteCount);
}
void KeccakP1600_Permute_Nrounds(void *state, unsigned int nrounds) {
    KeccakP1600_plain64_Permute_Nrounds((KeccakP1600_plain64_state *)state, nrounds);
}
void KeccakP1600_Permute_12rounds(void *state) {
    KeccakP1600_plain64_Permute_12rounds((KeccakP1600_plain64_state *)state);
}
void KeccakP1600_Permute_24rounds(void *state) {
    KeccakP1600_plain64_Permute_24rounds((KeccakP1600_plain64_state *)state);
}
void KeccakP1600_ExtractBytes(const void *state, unsigned char *data, unsigned int offset, unsigned int length) {
    KeccakP1600_plain64_ExtractBytes((const KeccakP1600_plain64_state *)state, data, offset, length);
}
void KeccakP1600_ExtractAndAddBytes(const void *state, const unsigned char *input, unsigned char *output, unsigned int offset, unsigned int length) {
    KeccakP1600_plain64_ExtractAndAddBytes((const KeccakP1600_plain64_state *)state, input, output, offset, length);
}

size_t KeccakF1600_FastLoop_Absorb(void *state, unsigned int laneCount,
                                    const unsigned char *data, size_t dataByteLen)
{
    size_t initialLen = dataByteLen;
    uint64_t localState[25];

    memcpy(localState, state, 200);
    while (dataByteLen >= laneCount * 8) {
        for (unsigned int i = 0; i < laneCount; i++) {
            uint64_t lane;
            memcpy(&lane, data + i * 8, 8);
            localState[i] ^= lane;
        }
        KeccakP1600_Permute_24rounds(localState);
        data        += laneCount * 8;
        dataByteLen -= laneCount * 8;
    }
    memcpy(state, localState, 200);
    return initialLen - dataByteLen;
}

size_t KeccakP1600_12rounds_FastLoop_Absorb(void *state, unsigned int laneCount,
                                             const unsigned char *data, size_t dataByteLen)
{
    size_t initialLen = dataByteLen;
    uint64_t localState[25];

    memcpy(localState, state, 200);
    while (dataByteLen >= laneCount * 8) {
        for (unsigned int i = 0; i < laneCount; i++) {
            uint64_t lane;
            memcpy(&lane, data + i * 8, 8);
            localState[i] ^= lane;
        }
        KeccakP1600_Permute_12rounds(localState);
        data        += laneCount * 8;
        dataByteLen -= laneCount * 8;
    }
    memcpy(state, localState, 200);
    return initialLen - dataByteLen;
}

#endif /* __ARM_FEATURE_SHA3 */
