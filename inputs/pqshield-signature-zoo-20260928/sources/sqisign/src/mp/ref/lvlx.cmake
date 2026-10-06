set(SOURCE_FILES_MP_${SVARIANT_UPPER}_REF
    ${LVLX_DIR}/mp.c
    ${LVLX_DIR}/modqx.c
)

add_library(${LIB_MP_${SVARIANT_UPPER}} STATIC ${SOURCE_FILES_MP_${SVARIANT_UPPER}_REF})
target_include_directories(${LIB_MP_${SVARIANT_UPPER}} PRIVATE ${INC_PUBLIC} ${INC_COMMON} ${INC_MP} ${PROJECT_SOURCE_DIR}/src/precomp/ref/${SVARIANT_LOWER}/include)
target_compile_options(${LIB_MP_${SVARIANT_UPPER}} PRIVATE ${C_OPT_FLAGS})
target_compile_definitions(${LIB_MP_${SVARIANT_UPPER}} PUBLIC SQISIGN_VARIANT=${SVARIANT_LOWER})

add_subdirectory(test)
