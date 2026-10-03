set(SOURCE_FILES_GF_SPECIFIC ${SAT64_DIR}/lvlx/fp_generic.c)
set(FP_ASM ${CMAKE_CURRENT_SOURCE_DIR}/fp_asm.S)

include(${SAT64_DIR}/lvlx.cmake)

target_compile_definitions(${LIB_GF_${SVARIANT_UPPER}} PUBLIC SQISIGN_FP2_FUSED_ASM)
