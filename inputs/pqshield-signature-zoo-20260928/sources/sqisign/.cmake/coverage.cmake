# SPDX-License-Identifier: Apache-2.0
#
# Convenience targets for code coverage:
#
#   cmake --build <builddir> --target coverage        measure this host's configurations
#   cmake --build <builddir> --target coverage-open   as above, then open the report
#
# (or simply `make coverage` / `make coverage-open` from inside the build directory).
#
# These targets do not measure *this* build directory. Coverage needs CMAKE_BUILD_TYPE=COVERAGE, and configuring one
# here would force every developer's build to -O0; scripts/coverage.sh builds its own build-coverage-<type>/ trees
# instead, one per SQISIGN_BUILD_TYPE. For the same reason the targets do not depend on `all`.
#
# gcovr is deliberately not looked up here, matching cppcheck.cmake and clang-tidy.cmake: the script does the lookup
# and version check when the target runs, so an unrelated `cmake ..` still works on a machine without it.
#
# Deliberately not done here:
#   * add_test() - this is a measurement, not a test, and should not gate ctest.

add_custom_target(coverage
    COMMAND ${PROJECT_SOURCE_DIR}/scripts/coverage.sh
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMENT "Measuring code coverage"
    USES_TERMINAL
    VERBATIM
)

add_custom_target(coverage-open
    COMMAND ${PROJECT_SOURCE_DIR}/scripts/coverage.sh --open
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMENT "Measuring code coverage, then opening the report"
    USES_TERMINAL
    VERBATIM
)
