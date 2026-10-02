add_executable(sqisign_test_mp_${SVARIANT_LOWER} ${LVLX_DIR}/test/test_mp.c ${LVLX_DIR}/test/mp_test_utils.c)
target_link_libraries(sqisign_test_mp_${SVARIANT_LOWER} ${LIB_MP_${SVARIANT_UPPER}} sqisign_common_test)
target_include_directories(sqisign_test_mp_${SVARIANT_LOWER} PRIVATE ${INC_MP} ${INC_COMMON} ${INC_PUBLIC} ${PROJECT_SOURCE_DIR}/src/precomp/ref/${SVARIANT_LOWER}/include)
add_test(sqisign_test_mp_${SVARIANT_LOWER} sqisign_test_mp_${SVARIANT_LOWER})

add_executable(sqisign_bench_mp_${SVARIANT_LOWER} ${LVLX_DIR}/test/bench_mp.c ${LVLX_DIR}/test/mp_test_utils.c)
target_link_libraries(sqisign_bench_mp_${SVARIANT_LOWER} ${LIB_MP_${SVARIANT_UPPER}} sqisign_common_test)
target_include_directories(sqisign_bench_mp_${SVARIANT_LOWER} PRIVATE ${INC_MP} ${INC_COMMON} ${INC_PUBLIC} ${PROJECT_SOURCE_DIR}/src/precomp/ref/${SVARIANT_LOWER}/include)
target_compile_definitions(sqisign_bench_mp_${SVARIANT_LOWER} PRIVATE SQISIGN_VARIANT=${SVARIANT_LOWER})

set(BM_BINS ${BM_BINS} sqisign_bench_mp_${SVARIANT_LOWER} CACHE INTERNAL "List of benchmark executables")
