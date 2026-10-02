/*
The Keccak-p permutations, designed by Guido Bertoni, Joan Daemen, Michael Peeters and Gilles Van Assche.

Implementation by the XKCP contributors, hereby denoted as "the implementer".

For more information, feedback or questions, please refer to the Keccak Team website:
https://keccak.team/

Keccak-p[1600]x4 for AArch64. Byte/lane management is generated from the generic
PlSnP-Fallback.inc template (serial fallback on the single-state SnP backend);
the 24-round permutation and absorb fast-loop use the verified Becker-Kannwischer
scalar+NEON hybrid core from mlkem-native (v8a, or v84a when SHA3 is available).

To the extent possible under law, the implementer has waived all copyright
and related or neighboring rights to the source code in this file.
http://creativecommons.org/publicdomain/zero/1.0/
*/

#include <stdint.h>
#include "KeccakP-1600-SnP.h"
/* KeccakP-1600-times4-SnP.h is intentionally NOT included here: PlSnP-Fallback.inc
 * defines all functions with (void*), which would conflict with the (const void*)
 * declarations in the SnP header for Extract functions. The SnP header is included
 * only by outer code (KeccakSpongetimes4.c) which does not pull in PlSnP-Fallback.inc. */

/* Generate the serial-fallback byte/lane helpers and the 12/6/4-round PermuteAll.
   The 24-round PermuteAll is redirected to a private name so we can provide the
   accelerated version below. */
#define prefix                          KeccakP1600times4
#define PlSnP_baseParallelism           1
#define PlSnP_targetParallelism         4
#define SnP_laneLengthInBytes           8
#define SnP                             KeccakP1600
#define SnP_Permute                     KeccakP1600_Permute_24rounds
#define SnP_Permute_12rounds            KeccakP1600_Permute_12rounds
#define SnP_Permute_Nrounds             KeccakP1600_Permute_Nrounds
#define PlSnP_PermuteAll                KeccakP1600times4_PermuteAll_24rounds_serial
#define PlSnP_PermuteAll_12rounds       KeccakP1600times4_PermuteAll_12rounds
#define PlSnP_PermuteAll_6rounds        KeccakP1600times4_PermuteAll_6rounds
#define PlSnP_PermuteAll_4rounds        KeccakP1600times4_PermuteAll_4rounds

#include "PlSnP-Fallback.inc"

/* SnP_laneLengthInBytes (8) is defined above and left defined by the template;
   reused below by the absorb fast loops. */

/* Keccak-f[1600] round constants, standard order. */
static const uint64_t KeccakP1600times4_RC[24] = {
    0x0000000000000001ULL, 0x0000000000008082ULL, 0x800000000000808aULL,
    0x8000000080008000ULL, 0x000000000000808bULL, 0x0000000080000001ULL,
    0x8000000080008081ULL, 0x8000000000008009ULL, 0x000000000000008aULL,
    0x0000000000000088ULL, 0x0000000080008009ULL, 0x000000008000000aULL,
    0x000000008000808bULL, 0x800000000000008bULL, 0x8000000000008089ULL,
    0x8000000000008003ULL, 0x8000000000008002ULL, 0x8000000000000080ULL,
    0x000000000000800aULL, 0x800000008000000aULL, 0x8000000080008081ULL,
    0x8000000000008080ULL, 0x0000000080000001ULL, 0x8000000080008008ULL
};

#if defined(__ARM_FEATURE_SHA3)
extern void KeccakP1600times4_v84a_permute24(uint64_t state[100], const uint64_t rc[24]);
#define KeccakP1600times4_permute24 KeccakP1600times4_v84a_permute24
#else
extern void KeccakP1600times4_v8a_permute24(uint64_t state[100], const uint64_t rc[24]);
#define KeccakP1600times4_permute24 KeccakP1600times4_v8a_permute24
#endif

/* MQOM3 adaptation: void* API (states is uint64_t[100] = 4 sequential states of 25 lanes each) */
void KeccakP1600times4_PermuteAll_24rounds(void *states)
{
    KeccakP1600times4_permute24((uint64_t *)states, KeccakP1600times4_RC);
}

size_t KeccakF1600times4_FastLoop_Absorb(void *states, unsigned int laneCount, unsigned int laneOffsetParallel, unsigned int laneOffsetSerial, const unsigned char *data, size_t dataByteLen)
{
    const unsigned char *dataStart = data;

    while (dataByteLen >= (laneOffsetParallel*3 + laneCount)*SnP_laneLengthInBytes) {
        KeccakP1600times4_AddLanesAll(states, data, laneCount, laneOffsetParallel);
        KeccakP1600times4_PermuteAll_24rounds(states);
        data += laneOffsetSerial*SnP_laneLengthInBytes;
        dataByteLen -= laneOffsetSerial*SnP_laneLengthInBytes;
    }
    return data - dataStart;
}

size_t KeccakP1600times4_12rounds_FastLoop_Absorb(void *states, unsigned int laneCount, unsigned int laneOffsetParallel, unsigned int laneOffsetSerial, const unsigned char *data, size_t dataByteLen)
{
    const unsigned char *dataStart = data;

    while (dataByteLen >= (laneOffsetParallel*3 + laneCount)*SnP_laneLengthInBytes) {
        KeccakP1600times4_AddLanesAll(states, data, laneCount, laneOffsetParallel);
        KeccakP1600times4_PermuteAll_12rounds(states);
        data += laneOffsetSerial*SnP_laneLengthInBytes;
        dataByteLen -= laneOffsetSerial*SnP_laneLengthInBytes;
    }
    return data - dataStart;
}
