# SPDX-License-Identifier: Apache-2.0
#
# Convenience targets for clang-format:
#
#   cmake --build <builddir> --target format         reformat the tree in place
#   cmake --build <builddir> --target check-format   report violations, change nothing
#
# (or simply `make format` / `make check-format` from inside the build directory).
#
# clang-format is deliberately NOT looked up here, and in particular there is no find_program: the binary these targets
# use is the one pre-commit downloaded for the pinned version, which lives in pre-commit's cache rather than on PATH.
# Locating anything at configure time would either make an unrelated `cmake ..` fail on a machine without it, or bake a
# stale path into the build directory. scripts/format.sh does the lookup when the target actually runs, and prints
# installation instructions on failure. See FORMATTING.md.

add_custom_target(format
    COMMAND ${PROJECT_SOURCE_DIR}/scripts/format.sh
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMENT "Formatting C sources with clang-format"
    USES_TERMINAL
    VERBATIM
)

add_custom_target(check-format
    COMMAND ${PROJECT_SOURCE_DIR}/scripts/format.sh --check
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMENT "Checking C source formatting with clang-format"
    USES_TERMINAL
    VERBATIM
)
