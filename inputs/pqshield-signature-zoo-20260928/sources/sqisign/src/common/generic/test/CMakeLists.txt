add_executable(sqisign_test_shake256 test_shake256.c)
target_link_libraries(sqisign_test_shake256 sqisign_common_test)
target_include_directories(sqisign_test_shake256 PRIVATE ${INC_COMMON} ${INC_PUBLIC})
add_test(sqisign_test_shake256 sqisign_test_shake256)

add_executable(sqisign_test_prng test_prng.c)
target_link_libraries(sqisign_test_prng sqisign_common_test)
target_include_directories(sqisign_test_prng PRIVATE ${INC_COMMON} ${INC_PUBLIC})
add_test(sqisign_test_prng sqisign_test_prng)

add_executable(sqisign_test_ctrdrbg_kat test_ctrdrbg_kat.c)
target_link_libraries(sqisign_test_ctrdrbg_kat sqisign_common_test)
target_include_directories(sqisign_test_ctrdrbg_kat PRIVATE ${INC_COMMON} ${INC_PUBLIC})
add_test(sqisign_test_ctrdrbg_kat sqisign_test_ctrdrbg_kat)

add_executable(sqisign_test_ctrdrbg_threads test_ctrdrbg_threads.c)
target_link_libraries(sqisign_test_ctrdrbg_threads sqisign_common_test pthread)
target_include_directories(sqisign_test_ctrdrbg_threads PRIVATE ${INC_COMMON} ${INC_PUBLIC})
add_test(sqisign_test_ctrdrbg_threads sqisign_test_ctrdrbg_threads)

# This one #includes ../prng.c to install a chosen root seed, so it must compile its dependencies itself rather than
# link sqisign_common_test, which would define prng.o a second time. randombytes_system.c is here only to resolve the
# randombytes() reference in prng_seed(), which this test never calls.
add_executable(sqisign_test_prng_kat
    test_prng_kat.c
    ../fips202.c
    ../mem.c
    ../randombytes_system.c
)
target_include_directories(sqisign_test_prng_kat PRIVATE ../include ${INC_COMMON} ${INC_PUBLIC})
target_compile_definitions(sqisign_test_prng_kat PRIVATE RANDOMBYTES_SYSTEM)
add_test(sqisign_test_prng_kat sqisign_test_prng_kat)
