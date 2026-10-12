set(SOURCE_FILES_QUATERNION_GENERIC_REF
    ${LVLX_DIR}/algebra.c
    ${LVLX_DIR}/dim4.c
    ${LVLX_DIR}/dim2.c
    ${LVLX_DIR}/integers.c
    ${LVLX_DIR}/lattice.c
    ${LVLX_DIR}/finit.c
    ${LVLX_DIR}/printer.c
    ${LVLX_DIR}/lll_applications.c
    ${LVLX_DIR}/lll/lll_lg2.c
    ${LVLX_DIR}/lll/lll_dim4.c
    ${LVLX_DIR}/lll/lehmer_xgcd.c
    ${LVLX_DIR}/lll/gaussian_xgcd.c
    ${LVLX_DIR}/stdorder.c
    ${LVLX_DIR}/qlapoty.c
    ${LVLX_DIR}/ideal.c
    ${LVLX_DIR}/protocol.c
    ${LVLX_DIR}/test/random_input_generation.c
)

add_library(${LIB_QUATERNION_${SVARIANT_UPPER}} STATIC ${SOURCE_FILES_QUATERNION_GENERIC_REF})
target_link_libraries(${LIB_QUATERNION_${SVARIANT_UPPER}}  ${LIB_MP_${SVARIANT_UPPER}} m)
target_include_directories(${LIB_QUATERNION_${SVARIANT_UPPER}} PRIVATE common ${INC_MP} ${INC_PUBLIC} ${INC_COMMON} ${INC_QUATERNION} ${INC_PRECOMP_${SVARIANT_UPPER}} ${LVLX_DIR}/internal_quaternion_headers)
target_compile_options(${LIB_QUATERNION_${SVARIANT_UPPER}} PRIVATE ${C_OPT_FLAGS})
target_compile_definitions(${LIB_QUATERNION_${SVARIANT_UPPER}} PUBLIC SQISIGN_VARIANT=${SVARIANT_LOWER})

add_subdirectory(test)

