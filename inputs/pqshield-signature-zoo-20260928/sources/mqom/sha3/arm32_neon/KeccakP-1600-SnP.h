/*
The eXtended Keccak Code Package (XKCP)
https://github.com/XKCP/XKCP

The Keccak-p permutations, designed by Guido Bertoni, Joan Daemen, Michael Peeters and Gilles Van Assche.

Implementation by Ronny Van Keer (ARMv7A+NEON).

For more information, feedback or questions, please refer to the Keccak Team website:
https://keccak.team/

To the extent possible under law, the implementer has waived all copyright
and related or neighboring rights to the source code in this file.
http://creativecommons.org/publicdomain/zero/1.0/

---

Adapted for the MQOM3 project: void* state API to match existing sponge infrastructure.
stateAlignment = 8: used as stride for the times4 serial fallback (round_up(200,8)=200).
All alignment hints (:64, :128) have been removed from the assembly so the permutation
works at any 4-byte-aligned address; on ARM Linux (SCTLR.A=0) VLD1/VST1 without hints
impose no hardware alignment fault (ARM ARM sec.A3.2.1).
*/

#ifndef _KeccakP_1600_SnP_h_
#define _KeccakP_1600_SnP_h_

#include "brg_endian.h"

#include <stddef.h>

#define KeccakP1600_implementation      "ARMv7A+NEON optimized assembler implementation"
#define KeccakP1600_stateSizeInBytes    200
#define KeccakP1600_stateAlignment      8
/* Note: KeccakF1600_FastLoop_Absorb is present in the assembly source but
 * disabled with .if 0  - do NOT define KeccakF1600_FastLoop_supported here. */

#define KeccakP1600_StaticInitialize()

void KeccakP1600_Initialize(void *state);
#if (PLATFORM_BYTE_ORDER == IS_LITTLE_ENDIAN)
#define KeccakP1600_AddByte(state, byte, offset) \
    ((unsigned char *)(state))[(offset)] ^= (byte)
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

#endif
