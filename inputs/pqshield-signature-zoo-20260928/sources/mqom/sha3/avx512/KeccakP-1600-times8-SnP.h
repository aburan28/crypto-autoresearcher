/*
Local wrapper for KeccakP-1600-times8 AVX-512, compatible with the PlSnP sponge
layer.  The XKCP AVX-512 functions take typed KeccakP1600times8_SIMD512_states *,
while the generic sponge layer stores state as unsigned char[].  The macros below
add the necessary casts so KeccakSpongetimes8.inc can be used unchanged.
*/

#ifndef _KeccakP_1600_times8_SnP_h_
#define _KeccakP_1600_times8_SnP_h_

#include "SIMD512-8-config.h"
#include "KeccakP-1600-times8-AVX512.h"

typedef KeccakP1600times8_SIMD512_states KeccakP1600times8_states;

#define KeccakP1600times8_implementation    "AVX-512 implementation (" KeccakP1600times8_implementation_config ")"
#define KeccakP1600times8_statesSizeInBytes  1600
#define KeccakP1600times8_statesAlignment    64

#define KeccakP1600times8_StaticInitialize()
#define KeccakP1600times8_InitializeAll(states) \
    KeccakP1600times8_AVX512_InitializeAll((KeccakP1600times8_SIMD512_states *)(states))
/* AddByte is already a byte-level macro in AVX512.h; pass-through is safe */
#define KeccakP1600times8_AddByte(states, instanceIndex, byte, offset) \
    KeccakP1600times8_AVX512_AddByte(states, instanceIndex, byte, offset)
#define KeccakP1600times8_AddBytes(states, instanceIndex, data, offset, length) \
    KeccakP1600times8_AVX512_AddBytes((KeccakP1600times8_SIMD512_states *)(states), instanceIndex, data, offset, length)
#define KeccakP1600times8_ExtractBytes(states, instanceIndex, data, offset, length) \
    KeccakP1600times8_AVX512_ExtractBytes((KeccakP1600times8_SIMD512_states *)(states), instanceIndex, data, offset, length)
#define KeccakP1600times8_PermuteAll_24rounds(states) \
    KeccakP1600times8_AVX512_PermuteAll_24rounds((KeccakP1600times8_SIMD512_states *)(states))

#endif /* _KeccakP_1600_times8_SnP_h_ */
