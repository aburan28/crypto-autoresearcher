# SPDX-License-Identifier: Apache-2.0

FOREACH(SVARIANT ${SVARIANT_S})

    string(TOLOWER ${SVARIANT} SVARIANT_LOWER)
    string(TOUPPER ${SVARIANT} SVARIANT_UPPER)

    add_executable(sqisign_test_kat_${SVARIANT} test_kat.c)
    target_link_libraries(sqisign_test_kat_${SVARIANT} sqisign_${SVARIANT_LOWER}_test)
    target_include_directories(sqisign_test_kat_${SVARIANT} PRIVATE ${PROJECT_SOURCE_DIR}/src/nistapi/${SVARIANT_LOWER} ${INC_PUBLIC} ${INC_INTBIG} ${INC_PRECOMP_${SVARIANT_UPPER}} ${INC_QUATERNION} ${INC_KLPT} ${INC_GF_${SVARIANT_UPPER}} ${INC_EC} ${INC_COMMON} ${INC_ID2ISO} ${INC_PROTOCOLS})
    add_test(sqisign_${SVARIANT}_KAT sqisign_test_kat_${SVARIANT})

    if (ENABLE_SIGN)

        add_executable(sqisign_test_scheme_${SVARIANT} test_sqisign.c)
        target_link_libraries(sqisign_test_scheme_${SVARIANT} sqisign_${SVARIANT_LOWER}_test_nistapi)
        target_include_directories(sqisign_test_scheme_${SVARIANT} PUBLIC ${PROJECT_SOURCE_DIR}/src/common ${INC_PUBLIC} ${PROJECT_SOURCE_DIR}/src/nistapi/${SVARIANT_LOWER})
        add_test(sqisign_${SVARIANT}_SELFTEST sqisign_test_scheme_${SVARIANT})

        if (ENABLE_CT_TESTING)
            # Constant-time testing harness (keypair + sign, no verification), run under valgrind by the daily CT
            # job in .github/workflows/ct-test.yml. The canonical invocation is documented in README
            # ('Constant-time tests'); deviating from it (in particular the build type and --num-callers) breaks
            # suppression matching and yields false positives, which is why the ctest registration below spells the
            # whole command out rather than just naming the executable.
            add_executable(sqisign_test_ct_${SVARIANT} test_ct.c)
            target_link_libraries(sqisign_test_ct_${SVARIANT} sqisign_${SVARIANT_LOWER}_test_nistapi)
            target_include_directories(sqisign_test_ct_${SVARIANT} PUBLIC ${PROJECT_SOURCE_DIR}/src/common ${INC_PUBLIC} ${PROJECT_SOURCE_DIR}/src/nistapi/${SVARIANT_LOWER})

            # Labelled "ct" so a plain `ctest` is unchanged and `ctest -L ct` runs the constant-time suite.
            if (VALGRIND_EXECUTABLE)
                add_test(NAME sqisign_${SVARIANT}_CT
                         COMMAND ${VALGRIND_EXECUTABLE} --error-exitcode=1 --max-stackframe=4116160
                                 --num-callers=25 -s
                                 --suppressions=${PROJECT_SOURCE_DIR}/test/ct-quaternion.supp
                                 $<TARGET_FILE:sqisign_test_ct_${SVARIANT}>)
                set_tests_properties(sqisign_${SVARIANT}_CT PROPERTIES LABELS ct)
            endif()
        endif()

    endif()

ENDFOREACH()
