set(SOURCE_FILES_QUATERNION_GENERIC_REF
    ${LVLX_DIR}/test/helpers.c
    ${LVLX_DIR}/test/algebra.c
    ${LVLX_DIR}/test/dim4.c
    ${LVLX_DIR}/test/dim2.c
    ${LVLX_DIR}/test/integers.c
    ${LVLX_DIR}/test/lattice.c
    ${LVLX_DIR}/test/finit.c
    ${LVLX_DIR}/test/stdorder.c
    ${LVLX_DIR}/test/qlapoty.c
    ${LVLX_DIR}/test/ideal.c
    ${LVLX_DIR}/test/protocol.c
)

set(SOURCE_FILES_QUATERNION_GENERIC_REF_TESTS
    ${SOURCE_FILES_QUATERNION_GENERIC_REF}
    ${LVLX_DIR}/lll/test/dim2_reference.c
    ${LVLX_DIR}/lll/test/rationals.c
    ${LVLX_DIR}/lll/test/lll_verification.c
    ${LVLX_DIR}/lll/test/lll_tests.c
    ${LVLX_DIR}/lll/test/dim2_tests.c
)
add_executable(sqisign_test_quaternion_${SVARIANT_LOWER} ${SOURCE_FILES_QUATERNION_GENERIC_REF_TESTS} ${LVLX_DIR}/test/test_quaternions.c)
target_link_libraries(sqisign_test_quaternion_${SVARIANT_LOWER} ${LIB_QUATERNION_${SVARIANT_UPPER}} ${LIB_PRECOMP_${SVARIANT_UPPER}} ${LIB_MP_${SVARIANT_UPPER}} sqisign_common_test)
target_include_directories(sqisign_test_quaternion_${SVARIANT_LOWER} PRIVATE ${LVLX_DIR}/internal_quaternion_headers ${INC_COMMON} ${INC_QUATERNION} ${INC_MP} ${INC_PRECOMP_${SVARIANT_UPPER}} ${INC_PUBLIC})

# Benchmarks for the constant-time reduction entry points.
add_executable(sqisign_bm_quaternion_ct_${SVARIANT_LOWER} ${LVLX_DIR}/lll/lll_ct_benchmarks.c)
target_link_libraries(sqisign_bm_quaternion_ct_${SVARIANT_LOWER} ${LIB_QUATERNION_${SVARIANT_UPPER}} ${LIB_PRECOMP_${SVARIANT_UPPER}} ${LIB_MP_${SVARIANT_UPPER}} sqisign_common_test)
target_include_directories(sqisign_bm_quaternion_ct_${SVARIANT_LOWER} PRIVATE ${LVLX_DIR}/internal_quaternion_headers ${INC_COMMON} ${INC_QUATERNION} ${INC_MP} ${INC_PRECOMP_${SVARIANT_UPPER}} ${INC_PUBLIC})
set(BM_BINS ${BM_BINS} sqisign_bm_quaternion_ct_${SVARIANT_LOWER} CACHE INTERNAL "List of benchmark executables")

# ctgrind harness for the CT reduction entry points. Deliberately SEPARATE from test/test_ct.c:
if (ENABLE_CT_TESTING)
    add_executable(sqisign_test_ct_lattice_${SVARIANT_LOWER} ${LVLX_DIR}/lll/lll_ct_ctgrind.c)
    target_link_libraries(sqisign_test_ct_lattice_${SVARIANT_LOWER} ${LIB_QUATERNION_${SVARIANT_UPPER}} ${LIB_PRECOMP_${SVARIANT_UPPER}} ${LIB_MP_${SVARIANT_UPPER}} sqisign_common_test)
    target_include_directories(sqisign_test_ct_lattice_${SVARIANT_LOWER} PRIVATE ${LVLX_DIR}/internal_quaternion_headers ${INC_COMMON} ${INC_QUATERNION} ${INC_MP} ${INC_PRECOMP_${SVARIANT_UPPER}} ${INC_PUBLIC})

    if (VALGRIND_EXECUTABLE)
        add_test(NAME sqisign_${SVARIANT_LOWER}_CT_LATTICE
                 COMMAND ${VALGRIND_EXECUTABLE} --error-exitcode=1 --max-stackframe=4116160
                         --num-callers=25 -s
                         --suppressions=${PROJECT_SOURCE_DIR}/test/ct-lattice-known.supp
                         $<TARGET_FILE:sqisign_test_ct_lattice_${SVARIANT_LOWER}>)
        set_tests_properties(sqisign_${SVARIANT_LOWER}_CT_LATTICE PROPERTIES LABELS ct)
    endif()
endif()


set(SOURCE_FILES_QUATERNION_RI_BENCH
    ${LVLX_DIR}/test/represent_integer_benchmarks.c
)
add_executable(sqisign_benchmark_represent_integer_${SVARIANT_LOWER} ${SOURCE_FILES_QUATERNION_RI_BENCH})
target_link_libraries(sqisign_benchmark_represent_integer_${SVARIANT_LOWER} ${LIB_QUATERNION_${SVARIANT_UPPER}} ${LIB_PRECOMP_${SVARIANT_UPPER}} ${LIB_MP_${SVARIANT_UPPER}} sqisign_common_test)
target_include_directories(sqisign_benchmark_represent_integer_${SVARIANT_LOWER} PRIVATE ${LVLX_DIR}/internal_quaternion_headers  ${INC_PUBLIC} ${INC_QUATERNION} ${INC_MP} ${INC_COMMON} ${INC_PRECOMP_${SVARIANT_UPPER}} ./include/ )
set(BM_BINS ${BM_BINS} sqisign_benchmark_represent_integer_${SVARIANT_LOWER} CACHE INTERNAL "List of benchmark executables")

set(SOURCE_FILES_QUATERNION_QN_BENCH
    ${LVLX_DIR}/test/qlapoty_normeq_benchmarks.c
)
add_executable(sqisign_benchmark_qlapoty_normeq_${SVARIANT_LOWER} ${SOURCE_FILES_QUATERNION_QN_BENCH})
target_link_libraries(sqisign_benchmark_qlapoty_normeq_${SVARIANT_LOWER} ${LIB_QUATERNION_${SVARIANT_UPPER}} ${LIB_PRECOMP_${SVARIANT_UPPER}} ${LIB_MP_${SVARIANT_UPPER}} sqisign_common_test)
target_include_directories(sqisign_benchmark_qlapoty_normeq_${SVARIANT_LOWER} PRIVATE ${LVLX_DIR}/internal_quaternion_headers ${INC_PUBLIC} ${INC_QUATERNION} ${INC_MP} ${INC_COMMON} ${INC_PRECOMP_${SVARIANT_UPPER}} ./include/ )
set(BM_BINS ${BM_BINS} sqisign_benchmark_qlapoty_normeq_${SVARIANT_LOWER} CACHE INTERNAL "List of benchmark executables")


add_test(sqisign_test_quaternion_${SVARIANT_LOWER} sqisign_test_quaternion_${SVARIANT_LOWER})

set_tests_properties(sqisign_test_quaternion_${SVARIANT_LOWER} PROPERTIES TIMEOUT 3600)
