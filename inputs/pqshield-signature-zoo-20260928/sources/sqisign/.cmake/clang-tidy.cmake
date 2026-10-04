# SPDX-License-Identifier: Apache-2.0
#
# Convenience targets for clang-tidy static analysis:
#
#   cmake --build <builddir> --target clang-tidy       analyze this host's configurations
#   cmake --build <builddir> --target clang-tidy-fix   as above, applying the fixes it can make automatically
#
# (or simply `make clang-tidy` / `make clang-tidy-fix` from inside the build directory).
#
# clang-tidy is deliberately NOT looked up here. Locating it at configure time would either make an unrelated `cmake ..`
# fail on a machine without it, or bake a stale path into the build directory. scripts/clang-tidy.sh does the lookup
# when the target actually runs, picks the newest binary meeting the version floor, and prints installation instructions
# on failure.
#
# Note that these targets do not analyze *this* build directory: clang-tidy needs one compile database per
# SQISIGN_BUILD_TYPE, and the script configures its own build-clang-tidy-<type>/ directories for that purpose. So the
# analysis is the same no matter which build directory you invoke it from.
#
# The check list is in .clang-tidy at the repository root, not here and not in the script, so that clangd shows the same
# findings in an editor.
#
# Deliberately not done here:
#   * CMAKE_C_CLANG_TIDY - that runs clang-tidy per translation unit on every compile, which ignores this project's
#                          per-configuration setup, defeats ccache and slows ordinary builds down a great deal.
#   * add_test() - this is not a test and should not gate ctest.

add_custom_target(clang-tidy
    COMMAND ${PROJECT_SOURCE_DIR}/scripts/clang-tidy.sh
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMENT "Running clang-tidy static analysis"
    USES_TERMINAL
    VERBATIM
)

add_custom_target(clang-tidy-fix
    COMMAND ${PROJECT_SOURCE_DIR}/scripts/clang-tidy.sh --fix
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMENT "Running clang-tidy static analysis, applying automatic fixes"
    USES_TERMINAL
    VERBATIM
)
