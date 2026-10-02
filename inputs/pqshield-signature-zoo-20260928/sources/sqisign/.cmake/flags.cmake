# SPDX-License-Identifier: Apache-2.0

if (CMAKE_SYSTEM_NAME STREQUAL "WindowsStore")
	set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -nostdlib")
endif()

if (SOURCE_PATH)
	set(SOURCE_FINAL_PATH ${SOURCE_PATH})
else()
	set(SOURCE_FINAL_PATH ${PROJECT_BINARY_DIR}/src)
endif()


include(GNUInstallDirs)
include(CheckSymbolExists)
include(CMakePushCheckState)

set(STRICT_OPTIONS_CPP )
set(STRICT_OPTIONS_C )
set(STRICT_OPTIONS_CXX )
if(MSVC)
	if(ENABLE_STRICT)
		set(STRICT_OPTIONS_CPP "${STRICT_OPTIONS_CPP} /WX /Zc:__cplusplus")
	endif()
else()
	set(STRICT_OPTIONS_CXX "${STRICT_OPTIONS_CXX} -std=c++14 -O2")
	set(STRICT_OPTIONS_CPP "${STRICT_OPTIONS_CPP} -Wall -Wuninitialized -Wno-deprecated-declarations -Wno-missing-field-initializers -Wno-unused-function -Wno-missing-braces")
	if (CMAKE_BUILD_TYPE STREQUAL "Debug")
		set(STRICT_OPTIONS_C "${STRICT_OPTIONS_C} -Og -g")
	else()
		set(STRICT_OPTIONS_C "${STRICT_OPTIONS_C} -O2")
		string(REPLACE "-O3" "-O2" CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE}")
	endif()
	set(STRICT_OPTIONS_C "${STRICT_OPTIONS_C} -std=c11 -Wno-error=strict-prototypes -fvisibility=hidden -funroll-loops -Wno-error=implicit-function-declaration -Wno-error=attributes")
	if(CMAKE_C_COMPILER_ID MATCHES "Clang")
		set(STRICT_OPTIONS_CPP "${STRICT_OPTIONS_CPP} -Wno-error=unknown-warning-option -Qunused-arguments -Wno-tautological-compare")
		set(STRICT_OPTIONS_CPP "${STRICT_OPTIONS_CPP} -Wno-pass-failed")
	endif()
	if(ENABLE_STRICT)
		set(STRICT_OPTIONS_C "${STRICT_OPTIONS_C} ${STRICT_OPTIONS_CPP} -Werror -Wextra -fno-strict-aliasing")
	endif()
	if(ENABLE_PEDANTIC)
		# pedantic (ISO-C) mode, no unused functions, shadow and strict prototypes
		string(REPLACE "-Wno-unused-function" "" STRICT_OPTIONS_C "${STRICT_OPTIONS_C}")
		set(STRICT_OPTIONS_C "${STRICT_OPTIONS_C} -Wpedantic -Wshadow -Wstrict-prototypes")
		add_compile_definitions(C_PEDANTIC_MODE)
	endif()
endif()

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${STRICT_OPTIONS_C}")

if (NOT CMAKE_BUILD_TYPE STREQUAL "Debug" AND NOT CMAKE_BUILD_TYPE STREQUAL "COVERAGE" AND NOT ENABLE_CT_TESTING)
	# enable link-time optimization (LTO)
	# Not for CT-testing builds: the valgrind suppressions in test/ct-quaternion.supp are anchored on function names,
	# and LTO breaks that twice over - it inlines across module boundaries (quaternion code ends up attributed to
	# id2iso/hd frames), and valgrind versions <= 3.24 cannot resolve the names of LTO-inlined frames at all
	# (reported as UnknownInlinedFun), so the suppressions silently stop matching. CT test binaries have no
	# performance requirements.
	include(CheckIPOSupported)
	check_ipo_supported(RESULT result)
	if(result)
		set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
	endif()
endif()
