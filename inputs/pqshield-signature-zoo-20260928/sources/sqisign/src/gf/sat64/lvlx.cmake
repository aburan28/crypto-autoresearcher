set(INC_GF ${SAT64_DIR}/include CACHE INTERNAL "INC")
set(INC_GF_${SVARIANT_UPPER} ${SAT64_DIR}/${SVARIANT_LOWER}/include CACHE INTERNAL "INC")

set(SOURCE_FILES_GF_${SVARIANT_UPPER}_SAT64
    ${SOURCE_FILES_GF_SPECIFIC}
    ${FP_ASM}
    ${SAT64_DIR}/${SVARIANT_LOWER}/fp.c
    ${SAT64_DIR}/lvlx/fp2.c
)

add_library(${LIB_GF_${SVARIANT_UPPER}} STATIC ${SOURCE_FILES_GF_${SVARIANT_UPPER}_SAT64})
# same as gf/ref: mp.h reaches precomp's encoded_sizes.h
target_link_libraries(${LIB_GF_${SVARIANT_UPPER}} ${LIB_MP_${SVARIANT_UPPER}})
target_include_directories(${LIB_GF_${SVARIANT_UPPER}} PRIVATE ${INC_COMMON} ${INC_MP} ${PROJECT_SOURCE_DIR}/src/precomp/ref/${SVARIANT_LOWER}/include ${INC_GF} ${INC_GF_${SVARIANT_UPPER}} ${INC_PUBLIC})
target_compile_options(${LIB_GF_${SVARIANT_UPPER}} PRIVATE ${C_OPT_FLAGS})
target_compile_definitions(${LIB_GF_${SVARIANT_UPPER}} PUBLIC SQISIGN_VARIANT=${SVARIANT_LOWER})

# Explicit binary dir is mandatory: the test source is outside this arch dir
# (it lives in the shared sat64 tree), so CMake can't auto-derive one.
add_subdirectory(${SAT64_DIR}/${SVARIANT_LOWER}/test ${CMAKE_CURRENT_BINARY_DIR}/test)
