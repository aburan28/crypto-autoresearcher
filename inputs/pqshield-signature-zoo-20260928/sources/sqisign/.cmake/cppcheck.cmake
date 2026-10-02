# SPDX-License-Identifier: Apache-2.0
#
# Convenience targets for cppcheck static analysis:
#
#   cmake --build <builddir> --target cppcheck         analyze this host's configurations
#   cmake --build <builddir> --target cppcheck-audit   as above, plus report stale suppressions
#
# (or simply `make cppcheck` / `make cppcheck-audit` from inside the build directory).
#
# cppcheck is deliberately NOT looked up here. Locating it at configure time would either make an unrelated `cmake ..`
# fail on a machine without it, or bake a stale path into the build directory. scripts/cppcheck.sh does the lookup when
# the target actually runs, checks the version, and prints installation instructions on failure.
#
# Note that these targets do not analyze *this* build directory: cppcheck needs one compile database per
# SQISIGN_BUILD_TYPE, and the script configures its own build-cppcheck-<type>/ directories for that purpose. So the
# analysis is the same no matter which build directory you invoke it from.
#
# Deliberately not done here:
#   * CMAKE_C_CPPCHECK - that runs cppcheck per translation unit on every compile, which ignores this project's flag set
#                        and slows ordinary builds down.
#   * add_test() - this is not a test and should not gate ctest.

add_custom_target(cppcheck
    COMMAND ${PROJECT_SOURCE_DIR}/scripts/cppcheck.sh
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMENT "Running cppcheck static analysis"
    USES_TERMINAL
    VERBATIM
)

add_custom_target(cppcheck-audit
    COMMAND ${PROJECT_SOURCE_DIR}/scripts/cppcheck.sh --audit
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMENT "Running cppcheck static analysis, reporting unmatched suppressions"
    USES_TERMINAL
    VERBATIM
)
