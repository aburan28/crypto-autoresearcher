/*
The eXtended Keccak Code Package (XKCP)
https://github.com/XKCP/XKCP

The Keccak-p permutations, designed by Guido Bertoni, Joan Daemen, Michael Peeters and Gilles Van Assche.

Implementation by Gilles Van Assche and Ronny Van Keer, hereby denoted as "the implementer".

For more information, feedback or questions, please refer to the Keccak Team website:
https://keccak.team/

To the extent possible under law, the implementer has waived all copyright
and related or neighboring rights to the source code in this file.
http://creativecommons.org/publicdomain/zero/1.0/

---

Please refer to SnP-documentation.h for more details.
*/

#ifndef _KeccakP_1600_SnP_h_
#define _KeccakP_1600_SnP_h_

#include <stddef.h>
#include <stdint.h>
#include "brg_endian.h"
#include "load-store.h"
#include "KeccakP-1600-opt64-config.h"

/* Map old config names to the plain64_ names expected by opt64.c */
#ifdef KeccakP1600_fullUnrolling
#define KeccakP1600_plain64_fullUnrolling
#endif
#ifndef KeccakP1600_plain64_implementation_config
#define KeccakP1600_plain64_implementation_config KeccakP1600_implementation_config
#endif

/* ---------------------------------------------------------------- */
/* State type used by the plain-64 implementation                   */
/* ---------------------------------------------------------------- */

typedef struct {
    uint64_t A[25];
} KeccakP1600_plain64_state;

/* ---------------------------------------------------------------- */
/* Declarations of the plain-64 functions defined in opt64.c        */
/* ---------------------------------------------------------------- */

#define KeccakP1600_plain64_StaticInitialize()
void KeccakP1600_plain64_Initialize(KeccakP1600_plain64_state *state);
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
#define KeccakP1600_plain64_AddByte(state, byte, offset) \
    ((unsigned char *)(state))[(offset)] ^= (byte)
#else
void KeccakP1600_plain64_AddByte(KeccakP1600_plain64_state *state, unsigned char data, unsigned int offset);
#endif
void KeccakP1600_plain64_AddBytes(KeccakP1600_plain64_state *state, const unsigned char *data, unsigned int offset, unsigned int length);
void KeccakP1600_plain64_OverwriteBytes(KeccakP1600_plain64_state *state, const unsigned char *data, unsigned int offset, unsigned int length);
void KeccakP1600_plain64_OverwriteWithZeroes(KeccakP1600_plain64_state *state, unsigned int byteCount);
void KeccakP1600_plain64_Permute_Nrounds(KeccakP1600_plain64_state *state, unsigned int nrounds);
void KeccakP1600_plain64_Permute_12rounds(KeccakP1600_plain64_state *state);
void KeccakP1600_plain64_Permute_24rounds(KeccakP1600_plain64_state *state);
void KeccakP1600_plain64_ExtractBytes(const KeccakP1600_plain64_state *state, unsigned char *data, unsigned int offset, unsigned int length);
void KeccakP1600_plain64_ExtractAndAddBytes(const KeccakP1600_plain64_state *state, const unsigned char *input, unsigned char *output, unsigned int offset, unsigned int length);
size_t KeccakF1600_plain64_FastLoop_Absorb(KeccakP1600_plain64_state *state, unsigned int laneCount, const unsigned char *data, size_t dataByteLen);
size_t KeccakP1600_12rounds_plain64_FastLoop_Absorb(KeccakP1600_plain64_state *state, unsigned int laneCount, const unsigned char *data, size_t dataByteLen);

/* ---------------------------------------------------------------- */
/* SnP interface: maps generic names to the plain-64 implementation */
/* KeccakSponge.c and related callers use void* state; we cast here */
/* so the upstream typed-pointer functions are called correctly.     */
/* ---------------------------------------------------------------- */

#define KeccakP1600_implementation      "generic 64-bit optimized implementation (" KeccakP1600_implementation_config ")"
#define KeccakP1600_stateSizeInBytes    200
#define KeccakP1600_stateAlignment      8

/*
 * FastLoop_Absorb is now safe on all endiannesses and alignments:
 * addInput uses loadInputLane which does memcpy (alignment-safe) on
 * little-endian and byte-by-byte construction on big-endian.
 */
#define KeccakF1600_FastLoop_supported
#define KeccakP1600_12rounds_FastLoop_supported

#define KeccakP1600_StaticInitialize()
#define KeccakP1600_Initialize(state) \
    KeccakP1600_plain64_Initialize((KeccakP1600_plain64_state *)(state))
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
#define KeccakP1600_AddByte(state, byte, offset) \
    ((unsigned char *)(state))[(offset)] ^= (byte)
#else
#define KeccakP1600_AddByte(state, byte, offset) \
    KeccakP1600_plain64_AddByte((KeccakP1600_plain64_state *)(state), (byte), (offset))
#endif
#define KeccakP1600_AddBytes(state, data, offset, length) \
    KeccakP1600_plain64_AddBytes((KeccakP1600_plain64_state *)(state), (data), (offset), (length))
#define KeccakP1600_OverwriteBytes(state, data, offset, length) \
    KeccakP1600_plain64_OverwriteBytes((KeccakP1600_plain64_state *)(state), (data), (offset), (length))
#define KeccakP1600_OverwriteWithZeroes(state, byteCount) \
    KeccakP1600_plain64_OverwriteWithZeroes((KeccakP1600_plain64_state *)(state), (byteCount))
#define KeccakP1600_Permute_Nrounds(state, nrounds) \
    KeccakP1600_plain64_Permute_Nrounds((KeccakP1600_plain64_state *)(state), (nrounds))
#define KeccakP1600_Permute_12rounds(state) \
    KeccakP1600_plain64_Permute_12rounds((KeccakP1600_plain64_state *)(state))
#define KeccakP1600_Permute_24rounds(state) \
    KeccakP1600_plain64_Permute_24rounds((KeccakP1600_plain64_state *)(state))
#define KeccakP1600_ExtractBytes(state, data, offset, length) \
    KeccakP1600_plain64_ExtractBytes((const KeccakP1600_plain64_state *)(state), (data), (offset), (length))
#define KeccakP1600_ExtractAndAddBytes(state, input, output, offset, length) \
    KeccakP1600_plain64_ExtractAndAddBytes((const KeccakP1600_plain64_state *)(state), (input), (output), (offset), (length))
#ifndef KeccakP1600_no_FastLoop
#define KeccakF1600_FastLoop_Absorb(state, laneCount, data, dataByteLen) \
    KeccakF1600_plain64_FastLoop_Absorb((KeccakP1600_plain64_state *)(state), (laneCount), (data), (dataByteLen))
#define KeccakP1600_12rounds_FastLoop_Absorb(state, laneCount, data, dataByteLen) \
    KeccakP1600_12rounds_plain64_FastLoop_Absorb((KeccakP1600_plain64_state *)(state), (laneCount), (data), (dataByteLen))
#endif

#endif
