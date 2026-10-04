# SPDX-License-Identifier: Apache-2.0

# AddressSanitizer
set(CMAKE_C_FLAGS_ASAN
    "-fsanitize=address -fno-optimize-sibling-calls -fsanitize-address-use-after-scope -fno-omit-frame-pointer -g -O1"
    CACHE STRING "Flags used by the C compiler during AddressSanitizer builds."
    FORCE)

# LeakSanitizer
set(CMAKE_C_FLAGS_LSAN
    "-fsanitize=leak -fno-omit-frame-pointer -g -O1"
    CACHE STRING "Flags used by the C compiler during LeakSanitizer builds."
    FORCE)

# MemorySanitizer
set(CMAKE_C_FLAGS_MSAN
    "-fsanitize=memory -fno-optimize-sibling-calls -fsanitize-memory-track-origins=2 -fno-omit-frame-pointer -g -O1"
    CACHE STRING "Flags used by the C compiler during MemorySanitizer builds."
    FORCE)

# UndefinedBehaviour
set(CMAKE_C_FLAGS_UBSAN
    "-fsanitize=undefined"
    CACHE STRING "Flags used by the C compiler during UndefinedBehaviourSanitizer builds."
    FORCE)

# Required to work around a clang bug: https://reviews.llvm.org/D49828
if (CMAKE_C_COMPILER_ID MATCHES "Clang" AND
    (${CMAKE_SYSTEM_PROCESSOR} MATCHES "aarch64" OR ${CMAKE_SYSTEM_PROCESSOR} MATCHES "arm64"))
    foreach(LINKER_KIND EXE SHARED MODULE)
        set(CMAKE_${LINKER_KIND}_LINKER_FLAGS_UBSAN
            "--rtlib=compiler-rt"
            CACHE STRING "Flags used by the linker during UndefinedBehaviourSanitizer builds."
            FORCE)
    endforeach()
endif()

# Coverage. -O0 -g comes after the -O2 that .cmake/flags.cmake appends to CMAKE_C_FLAGS, so it wins; without it gcov
# attributes lines to wherever the optimizer moved them. LTO is disabled for this build type in flags.cmake, for the
# same reason.
set(CMAKE_C_FLAGS_COVERAGE
    "--coverage -O0 -g"
    CACHE STRING "Flags used by the C compiler during Coverage builds."
    FORCE)

set(CMAKE_EXE_LINKER_FLAGS_COVERAGE
    "--coverage"
    CACHE STRING "Flags used by the linker during Coverage builds."
    FORCE)

set(CMAKE_SHARED_LINKER_FLAGS_COVERAGE
    "--coverage"
    CACHE STRING "Flags used by the linker for shared libraries during Coverage builds."
    FORCE)

set(CMAKE_C_FLAGS_PERF
    "-ggdb"
    CACHE STRING "Flags used for profiling with perf or pprof."
    FORCE)

set(CMAKE_C_FLAGS_GPROF
    "-g -pg"
    CACHE STRING "Flags used for profiling with gprof."
    FORCE)
