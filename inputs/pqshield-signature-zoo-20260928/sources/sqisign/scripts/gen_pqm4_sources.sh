#!/bin/bash

# This script should be run in the root folder of the repository, and creates pqm4 files
# in "src/pqm4/sqisign_<variant>/<impl>" for each selected parameter set, covering the full
# scheme (keygen, sign and verify).
#
# Usage: scripts/gen_pqm4_sources.sh [ref|m4f|all]
#
#   ref (default)  portable reference arithmetic (modarith, src/gf/ref)
#   m4f            optimized Cortex-M4 arithmetic (m4-modarith, src/gf/armv7e-m)
#   all            both implementations
#
# pqm4's test and benchmark tooling automatically builds and runs every implementation directory of
# a scheme, so generating with "all" yields a direct ref-vs-m4f comparison on the target.

# Abort on the first failing command: a source file that has been moved or renamed must not silently produce an
# incomplete pqm4 tree.
set -eu

MODE=${1:-ref}
case "${MODE}" in
    ref) IMPLS="ref" ;;
    m4f) IMPLS="m4f" ;;
    all) IMPLS="ref m4f" ;;
    *) echo "usage: $0 [ref|m4f|all]"; exit 1 ;;
esac

for LVL in p324_3 p500_27 p664_17
do
    PQCGENKAT_SIGN_PQM4_BINARY=build/apps/PQCgenKAT_sign_pqm4_${LVL}

    if [ ! -f ${PQCGENKAT_SIGN_PQM4_BINARY} ]; then
        echo ${PQCGENKAT_SIGN_PQM4_BINARY} not found. Build it before running this script, or change the build folder in the script. Aborting.
        exit 1
    fi

    for IMPL in ${IMPLS}
    do
        DST_PATH=src/pqm4/sqisign_${LVL}/${IMPL}

        if [ -d ${DST_PATH} ]; then
            echo Destination folder ${DST_PATH} already exists. Delete it before running this script. Aborting.
            exit 1
        fi

        mkdir -p ${DST_PATH}

        # Run API generation script
        ${PQCGENKAT_SIGN_PQM4_BINARY} ${DST_PATH}

        # The implementations share everything but the GF(p) arithmetic: m4f swaps the per-prime
        # field file and selects the saturated 32-bit limb layout via SQISIGN_GF_IMPL_SAT32.
        if [ "${IMPL}" = "ref" ]; then
            GF_IMPL_FLAG="-DSQISIGN_GF_IMPL_REF"
        else
            GF_IMPL_FLAG="-DSQISIGN_GF_IMPL_SAT32"
        fi

        CPPFLAGS="-DRADIX_32 -DSQISIGN_BUILD_TYPE_REF ${GF_IMPL_FLAG} -DSQISIGN_VARIANT=${LVL} -DTARGET_ARM -DNDEBUG -DDISABLE_NAMESPACING -DSQISIGN_SINGLE_THREADED -DENABLE_SIGN -Dshake256_inc_ctx_reset=shake256_inc_init"
        PQM4_NAME="crypto_sign_sqisign_${LVL}_${IMPL}"

        echo "elf/${PQM4_NAME}_%.elf: CPPFLAGS+=${CPPFLAGS}" > ${DST_PATH}/config.mk
        echo "obj/lib${PQM4_NAME}.a: CPPFLAGS+=${CPPFLAGS}" >> ${DST_PATH}/config.mk

        cp include/{ct_testing,mem,sig,sqisign_namespace}.h ${DST_PATH}/

        cp src/sqisign.c ${DST_PATH}/

        cp src/common/generic/include/{prng,tools,tutil}.h ${DST_PATH}/
        cp src/common/generic/{mem,prng}.c ${DST_PATH}/

        cp src/ec/ref/lvlx/{basis,biextension,ec,isog,normalize}.c ${DST_PATH}/
        cp src/ec/ref/include/{biextension,ec,isog}.h ${DST_PATH}/

        cp src/gf/ref/lvlx/{fp,fp2}.c ${DST_PATH}/
        cp src/gf/ref/include/{fp,fp2}.h ${DST_PATH}/

        cp src/hd/ref/lvlx/{{hd,gluing,splitting,theta_isogenies,theta_structure}.c,{gluing,splitting,theta_structure}.h} ${DST_PATH}/
        cp src/hd/ref/include/hd.h ${DST_PATH}/

        cp src/id2iso/ref/lvlx/{dim2id2iso,id2iso}.c ${DST_PATH}/
        cp src/id2iso/ref/include/id2iso.h ${DST_PATH}/

        cp src/mp/ref/lvlx/{modqx,mp}.c ${DST_PATH}/
        cp src/mp/ref/include/{modqx,mp,mp_carry,mp_ct,mp_internal,primality_test}.h ${DST_PATH}/

        cp src/precomp/ref/${LVL}/include/{e0_basis,ec_params,encoded_sizes,endomorphism_action,fp_constants,quaternion_constants,quaternion_data,torsion_constants}.h ${DST_PATH}/
        cp src/precomp/ref/${LVL}/{e0_basis,ec_params,endomorphism_action,quaternion_data,torsion_constants}.c ${DST_PATH}/

        cp src/quaternion/ref/lvlx/{algebra,dim2,dim4,finit,ideal,integers,lattice,lll_applications,protocol,qlapoty,stdorder}.c ${DST_PATH}/
        cp src/quaternion/ref/lvlx/lll/{{gaussian_xgcd,lehmer_xgcd,lll_dim4,lll_lg2}.c,{lll_config,lll_lg2}.h} ${DST_PATH}/
        cp src/quaternion/ref/lvlx/internal_quaternion_headers/{internal,lll}.h ${DST_PATH}/
        cp src/quaternion/ref/include/quaternion.h ${DST_PATH}/

        cp src/signature/ref/lvlx/{encode_secret,keygen,sign}.c ${DST_PATH}/
        cp src/signature/ref/include/signature.h ${DST_PATH}/

        cp src/verification/ref/lvlx/{common,encode_public,verify}.c ${DST_PATH}/
        cp src/verification/ref/include/verification.h ${DST_PATH}/

        if [ "${IMPL}" = "ref" ]; then
            cp src/gf/ref/${LVL}/{fp_${LVL}.c,fp_${LVL}_32.inc} ${DST_PATH}/
        else
            cp src/gf/armv7e-m/${LVL}/{code_${LVL}_mont.c,fp_${LVL}_armv7em.c} ${DST_PATH}/
        fi
    done
done
