/*
 * AArch64 Keccak-p[1600] SnP header.
 * Selects implementation string based on available extensions.
 * State format: 200 bytes, 8-byte aligned, little-endian lanes (identical to opt64).
 */

#ifndef _KeccakP_1600_SnP_h_
#define _KeccakP_1600_SnP_h_

#include "brg_endian.h"
#include "KeccakP-1600-opt64-config.h"

#ifdef __ARM_FEATURE_SHA3
#  define KeccakP1600_implementation \
        "AArch64 with ARMv8.2+SHA3 extensions (RAX1/BCAX)"
#else
#  define KeccakP1600_implementation \
        "AArch64 plain C (opt64 fallback, " KeccakP1600_implementation_config ")"
#endif

#define KeccakP1600_stateSizeInBytes    200
#define KeccakP1600_stateAlignment      8
#define KeccakF1600_FastLoop_supported
#define KeccakP1600_12rounds_FastLoop_supported

#include <stddef.h>

#define KeccakP1600_StaticInitialize()
void KeccakP1600_Initialize(void *state);
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
#define KeccakP1600_AddByte(state, byte, offset) \
    ((unsigned char*)(state))[(offset)] ^= (byte)
#else
void KeccakP1600_AddByte(void *state, unsigned char data, unsigned int offset);
#endif
void KeccakP1600_AddBytes(void *state, const unsigned char *data, unsigned int offset, unsigned int length);
void KeccakP1600_OverwriteBytes(void *state, const unsigned char *data, unsigned int offset, unsigned int length);
void KeccakP1600_OverwriteWithZeroes(void *state, unsigned int byteCount);
void KeccakP1600_Permute_Nrounds(void *state, unsigned int nrounds);
void KeccakP1600_Permute_12rounds(void *state);
void KeccakP1600_Permute_24rounds(void *state);
void KeccakP1600_ExtractBytes(const void *state, unsigned char *data, unsigned int offset, unsigned int length);
void KeccakP1600_ExtractAndAddBytes(const void *state, const unsigned char *input, unsigned char *output, unsigned int offset, unsigned int length);
size_t KeccakF1600_FastLoop_Absorb(void *state, unsigned int laneCount, const unsigned char *data, size_t dataByteLen);
size_t KeccakP1600_12rounds_FastLoop_Absorb(void *state, unsigned int laneCount, const unsigned char *data, size_t dataByteLen);

#endif /* _KeccakP_1600_SnP_h_ */
